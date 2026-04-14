from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.reader_grade_pipeline import ensure_translation_manifest
from play_book_studio.ingestion.translation_draft_generation import generate_translation_drafts


HEADING_NUMBER_PREFIX_RE = re.compile(
    r"^\s*(?:chapter\s+\d+\.?\s*|\d+\s*장\.?\s*|(?:\d+|[A-Za-z])(?:\.\d+)*\.?\s+)",
    re.IGNORECASE,
)
LABEL_ONLY_RE = re.compile(r"^(중요|참고|팁|주의|경고|선행 조건|사전 요구 사항|사전 조건|절차|예상 출력)$")
LEGAL_NOTICE_RE = re.compile(r"red hat open(sh|s)ift .*법적 고지 요약", re.IGNORECASE)
GENERIC_DOC_INTRO_RE = re.compile(r"^이 문서에서는 .+ 설명합니다\.?$")
PAST_TENSE_PREFACE_RE = re.compile(r"(.+?)(검토했습니다|읽으셨습니다|구성했습니다)\.?$")
ASCII_HEAVY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ,:/()_-]{16,}$")

KEYWORDS = {
    "overview": ["개요", "소개", "overview", "introduction"],
    "prereq": ["사전", "준비", "요구", "필수", "requirements", "before you begin", "prereq"],
    "procedure": ["설치", "구성", "생성", "설정", "배포", "백업", "복원", "절차", "install", "configure", "create", "setup", "backup", "restore"],
    "verify": ["검증", "확인", "verify", "validation", "check", "상태"],
    "failure": ["문제", "오류", "장애", "문제 해결", "우회", "failure", "troubleshooting", "known issue", "warning"],
    "architecture": ["구성", "아키텍처", "구조", "topology", "architecture", "component"],
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate 10 pipeline trial markdown outputs for reader-grade books.")
    parser.add_argument("output_root", nargs="?", default="tests/reader_grade_pipeline_trials")
    parser.add_argument("--slug", dest="slugs", action="append", required=True)
    return parser


def _clean_heading(text: str) -> str:
    raw = " ".join(str(text or "").split()).strip()
    cleaned = HEADING_NUMBER_PREFIX_RE.sub("", raw).strip()
    return cleaned or raw


def _block_text(block: dict[str, object]) -> str:
    kind = str(block.get("kind") or "").strip()
    if kind == "paragraph":
        return str(block.get("text") or "").strip()
    if kind == "code":
        code = str(block.get("code") or "").rstrip()
        if not code:
            return ""
        language = str(block.get("language") or "text").strip() or "text"
        return f"```{language}\n{code}\n```"
    if kind == "note":
        title = str(block.get("title") or "참고").strip() or "참고"
        text = str(block.get("text") or "").strip()
        return f"> **{title}**\n> {text}" if text else ""
    if kind == "prerequisite":
        items = [str(item).strip() for item in (block.get("items") or []) if str(item).strip()]
        return "\n".join(f"- {item}" for item in items)
    if kind == "procedure":
        lines: list[str] = []
        for index, step in enumerate(block.get("steps") or [], start=1):
            text = str(step.get("text") or "").strip()
            if text:
                lines.append(f"{index}. {text}")
            for substep in (step.get("substeps") or []):
                normalized = str(substep).strip()
                if normalized:
                    lines.append(f"   - {normalized}")
        return "\n".join(lines)
    if kind == "table":
        headers = [str(item).strip() for item in (block.get("headers") or [])]
        rows = [[str(cell).strip() for cell in row] for row in (block.get("rows") or [])]
        lines: list[str] = []
        if headers:
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)
    return ""


def _section_body(section: dict[str, object], *, max_blocks: int = 12) -> str:
    blocks = [dict(block) for block in (section.get("blocks") or []) if isinstance(block, dict)]
    rendered: list[str] = []
    pending_label = ""
    for block in blocks[:max_blocks]:
        text = _block_text(block)
        if not text:
            continue
        if str(block.get("kind") or "") == "paragraph" and LABEL_ONLY_RE.match(text):
            pending_label = text
            continue
        if pending_label and str(block.get("kind") or "") == "paragraph":
            rendered.append(f"> **{pending_label}**\n> {text}")
            pending_label = ""
            continue
        if pending_label:
            rendered.append(f"### {pending_label}")
            pending_label = ""
        rendered.append(text)
    return "\n\n".join(item for item in rendered if item).strip()


def _section_score(section: dict[str, object], key: str) -> tuple[int, int]:
    heading = _clean_heading(str(section.get("heading") or ""))
    heading_hits = sum(1 for token in KEYWORDS[key] if token in heading.casefold())
    body = _section_body(section, max_blocks=10)
    body_hits = sum(1 for token in KEYWORDS[key] if token in body.casefold())
    block_bonus = 0
    for block in (section.get("blocks") or []):
        if not isinstance(block, dict):
            continue
        kind = str(block.get("kind") or "").strip()
        if key == "procedure" and kind in {"procedure", "code"}:
            block_bonus += 2
        if key == "verify" and kind in {"note", "procedure"}:
            block_bonus += 1
    score = heading_hits * 4 + body_hits + block_bonus
    return score, len(body)


def _normalize_dedupe_key(text: str) -> str:
    return " ".join(text.split()).strip().casefold()


def _sanitize_paragraph(text: str) -> str:
    normalized = " ".join(str(text or "").split()).strip()
    if not normalized:
        return ""
    if LEGAL_NOTICE_RE.search(normalized):
        return ""
    if ASCII_HEAVY_RE.match(normalized) and not any("\uac00" <= ch <= "\ud7a3" for ch in normalized):
        return ""
    if GENERIC_DOC_INTRO_RE.match(normalized):
        return ""
    preface_match = PAST_TENSE_PREFACE_RE.match(normalized)
    if preface_match:
        stem = preface_match.group(1).strip()
        if stem:
            return f"- {stem} 확인한다."
    if normalized.startswith("이 문서에서는 ") and "설명합니다" in normalized:
        return ""
    return normalized


def _sanitize_section_text(text: str, *, max_paragraphs: int | None = None, bulletize: bool = False) -> str:
    pieces = [piece.strip() for piece in str(text or "").split("\n\n")]
    kept: list[str] = []
    seen: set[str] = set()
    for piece in pieces:
        cleaned = _sanitize_paragraph(piece)
        if not cleaned:
            continue
        key = _normalize_dedupe_key(cleaned)
        if key in seen:
            continue
        seen.add(key)
        if bulletize and not cleaned.startswith(("-", ">", "```", "###")):
            cleaned = f"- {cleaned}"
        kept.append(cleaned)
        if max_paragraphs is not None and len(kept) >= max_paragraphs:
            break
    return "\n\n".join(kept).strip()


def _has_keyword(text: str, key: str) -> bool:
    normalized = text.casefold()
    return any(token in normalized for token in KEYWORDS[key])


def _pick_sections(sections: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    selected: dict[str, dict[str, object]] = {}
    for key in ("overview", "prereq", "procedure", "verify", "failure", "architecture"):
        ranked = sorted(sections, key=lambda section: _section_score(section, key), reverse=True)
        for section in ranked:
            score, _ = _section_score(section, key)
            if score > 0:
                selected[key] = section
                break
    fallback_iter = iter(sections)
    for key in ("overview", "prereq", "procedure", "verify", "failure", "architecture"):
        if key not in selected:
            selected[key] = next(fallback_iter, {})
    return selected


def _load_playbook(slug: str) -> tuple[str, dict[str, str], str]:
    settings = load_settings(ROOT)
    gold_playbook_path = settings.gold_manualbook_ko_dir / "playbooks" / f"{slug}.json"
    if gold_playbook_path.exists():
        gold_payload = json.loads(gold_playbook_path.read_text(encoding="utf-8"))
        if str(gold_payload.get("translation_status") or "").strip() == "approved_ko":
            payload = gold_payload
            source_path = str(gold_playbook_path.relative_to(ROOT))
        else:
            ensure_translation_manifest(settings, [slug])
            generate_translation_drafts(settings, slugs=[slug], force_regenerate=True)
            playbook_path = settings.silver_ko_dir / "translation_drafts" / "playbooks" / f"{slug}.json"
            payload = json.loads(playbook_path.read_text(encoding="utf-8"))
            source_path = str(playbook_path.relative_to(ROOT))
    else:
        ensure_translation_manifest(settings, [slug])
        generate_translation_drafts(settings, slugs=[slug], force_regenerate=True)
        playbook_path = settings.silver_ko_dir / "translation_drafts" / "playbooks" / f"{slug}.json"
        payload = json.loads(playbook_path.read_text(encoding="utf-8"))
        source_path = str(playbook_path.relative_to(ROOT))
    title = str(payload.get("title") or slug.replace("_", " "))
    sections = [dict(section) for section in (payload.get("sections") or []) if isinstance(section, dict)]
    sections = [section for section in sections if _section_body(section, max_blocks=8)]
    selected = _pick_sections(sections)
    picked = {
        "overview": _sanitize_section_text(_section_body(selected["overview"], max_blocks=5), max_paragraphs=2),
        "prereq": _sanitize_section_text(_section_body(selected["prereq"], max_blocks=6), max_paragraphs=4, bulletize=True),
        "procedure": _sanitize_section_text(_section_body(selected["procedure"], max_blocks=18)),
        "verify": _sanitize_section_text(_section_body(selected["verify"], max_blocks=8), max_paragraphs=4),
        "failure": _sanitize_section_text(_section_body(selected["failure"], max_blocks=8), max_paragraphs=4),
        "architecture": _sanitize_section_text(_section_body(selected["architecture"], max_blocks=8), max_paragraphs=2),
    }
    if not picked["verify"]:
        picked["verify"] = "- 주요 작업 후 상태, 리소스, 예상 결과를 다시 확인한다."
    if not picked["failure"]:
        picked["failure"] = "- 실패 신호와 우회 경로는 운영 기준에 맞게 별도 확인이 필요하다."
    # Drop repeated paragraphs across sections after per-section cleanup.
    used: set[str] = set()
    for key in ("overview", "prereq", "architecture", "procedure", "verify", "failure"):
        paragraphs: list[str] = []
        for piece in [part.strip() for part in picked[key].split("\n\n") if part.strip()]:
            dedupe_key = _normalize_dedupe_key(piece)
            if dedupe_key in used:
                continue
            used.add(dedupe_key)
            paragraphs.append(piece)
        picked[key] = "\n\n".join(paragraphs).strip()
    return title, picked, source_path


def _trial_specs(title: str, base: dict[str, str]) -> list[tuple[str, str, str]]:
    return [
        ("01_en_slim_then_ko", "EN slim book -> KO translation", f"""# {title}

## Overview

{base['overview']}

## Before You Begin

{base['prereq']}

## Procedure

{base['procedure']}

## Verify

{base['verify']}
"""),
        ("02_markdown_template_fill", "Normalized markdown -> runbook template", f"""# {title}

## When To Use

{base['overview']}

## Prerequisites

{base['prereq']}

## Procedure

{base['procedure']}
"""),
        ("03_section_cluster_slim", "Section clustering -> slim book", f"""# {title}

## Core Path

- 핵심 개요
- 필수 준비
- 절차
- 검증

## Core Overview

{base['overview']}

## Core Procedure

{base['procedure']}
"""),
        ("04_procedure_code_verify", "Procedure/code/verify first", f"""# {title}

## Procedure

{base['procedure']}

## Verify

{base['verify']}

## Failure Signals

{base['failure']}
"""),
        ("05_heading_cleanup_noise_drop", "Heading cleanup + noise drop", f"""# {title}

## Overview

{base['overview']}

## Architecture

{base['architecture']}

## Procedure

{base['procedure']}
"""),
        ("06_full_manual_reshape", "Full-manual summary reshape", f"""# {title}

## Context

{base['overview']}

## Planning Notes

{base['prereq']}

## Execution Path

{base['procedure']}

## Verification

{base['verify']}
"""),
        ("07_toc_aware_book", "TOC-aware book", f"""# {title}

## 목차

- Overview
- Before You Begin
- Procedure
- Verify
- Failure Signals

## Overview

{base['overview']}

## Before You Begin

{base['prereq']}

## Procedure

{base['procedure']}

## Verify

{base['verify']}

## Failure Signals

{base['failure']}
"""),
        ("08_operator_first", "Operator-first shaping", f"""# {title}

## First Reading Path

1. 현재 작업 목적을 확인한다.
2. 선행 조건을 확인한다.
3. 절차를 실행한다.
4. 결과를 검증한다.

## Purpose

{base['overview']}

## Readiness Check

{base['prereq']}

## Operator Procedure

{base['procedure']}
"""),
        ("09_failure_first_recovery", "Failure-first recovery book", f"""# {title}

## Failure Signals

{base['failure']}

## Recovery Path

{base['procedure']}

## Verify

{base['verify']}
"""),
        ("10_verify_first_ops", "Verify-first ops book", f"""# {title}

## Success Criteria

{base['verify']}

## Procedure

{base['procedure']}

## Known Failure Signals

{base['failure']}
"""),
    ]


def _trial_docs(label: str, description: str, slug: str, title: str, source_path: str) -> str:
    stack = {
        "01_en_slim_then_ko": ["Raw HTML", "canonical normalize", "translation draft", "slim-book shaping", "Markdown final"],
        "02_markdown_template_fill": ["Raw HTML", "normalized markdown projection", "runbook template fill", "Markdown final"],
        "03_section_cluster_slim": ["Raw HTML", "translated sections", "section clustering", "slim book assembly"],
        "04_procedure_code_verify": ["Raw HTML", "block extraction", "procedure/code/verify layout", "Markdown final"],
        "05_heading_cleanup_noise_drop": ["Raw HTML", "heading cleanup", "noise drop", "guided manual assembly"],
        "06_full_manual_reshape": ["Raw HTML", "translated draft", "summary reshape", "Markdown final"],
        "07_toc_aware_book": ["Raw HTML", "section tree", "toc-aware composition", "Markdown final"],
        "08_operator_first": ["Raw HTML", "operator-first routing", "procedure prioritization", "Markdown final"],
        "09_failure_first_recovery": ["Raw HTML", "failure signal extraction", "recovery shaping", "Markdown final"],
        "10_verify_first_ops": ["Raw HTML", "verification extraction", "ops shaping", "Markdown final"],
    }[label]
    lines = [
        f"# {label} — {description}",
        "",
        "## Goal",
        "",
        f"`{slug}` 문서를 다른 shaping 순서로 재구성해서 reader-grade book 후보를 만든다.",
        "",
        "## Source",
        "",
        f"- slug: `{slug}`",
        f"- title: `{title}`",
        f"- input: `{source_path}`",
        "",
        "## Pipeline Steps",
        "",
    ]
    for index, step in enumerate(stack, start=1):
        lines.append(f"{index}. {step}")
    lines.extend(
        [
            "",
            "## Tech Stack",
            "",
            "- Python (`.venv\\Scripts\\python.exe`)",
            "- `translation_draft_generation.generate_translation_drafts`",
            "- `reader_grade_pipeline.ensure_translation_manifest`",
            "- markdown post-processing",
            "",
            "## Notes",
            "",
            "- 이 폴더의 `output.md` 가 사용자 비교 대상이다.",
            "- `meta.json` 은 trial 메타데이터만 남긴다.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _write_trials(root: Path, slug: str, title: str, trials: list[tuple[str, str, str]], source_path: str) -> None:
    target_root = root / slug
    target_root.mkdir(parents=True, exist_ok=True)
    index_lines = [f"# {title} Pipeline Trials", ""]
    for label, description, content in trials:
        folder = target_root / label
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "output.md").write_text(content.strip() + "\n", encoding="utf-8")
        (folder / "pipeline.md").write_text(_trial_docs(label, description, slug, title, source_path), encoding="utf-8")
        (folder / "meta.json").write_text(
            json.dumps({"source_slug": slug, "title": title, "label": label, "description": description, "input_path": source_path}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        index_lines.append(f"- [{label}]({label}/output.md) — {description}")
    (target_root / "README.md").write_text("\n".join(index_lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    output_root = ROOT / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    created: list[dict[str, object]] = []
    for slug in args.slugs:
        title, base, source_path = _load_playbook(slug)
        trials = _trial_specs(title, base)
        _write_trials(output_root, slug, title, trials, source_path)
        created.append({"slug": slug, "title": title, "trial_count": len(trials), "input_path": source_path})
    print(json.dumps({"root": str(output_root), "created": created}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
