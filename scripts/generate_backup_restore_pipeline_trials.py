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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate 10 backup_and_restore pipeline trial markdown outputs.",
    )
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


def _find_section(sections: list[dict[str, object]], target_heading: str) -> dict[str, object]:
    for section in sections:
        if _clean_heading(str(section.get("heading") or "")) == target_heading:
            return section
    return {}


def _load_base_texts() -> dict[str, str]:
    settings = load_settings(ROOT)
    ensure_translation_manifest(settings, ["backup_and_restore"])
    generate_translation_drafts(settings, slugs=["backup_and_restore"], force_regenerate=True)
    playbook_path = settings.silver_ko_dir / "translation_drafts" / "playbooks" / "backup_and_restore.json"
    payload = json.loads(playbook_path.read_text(encoding="utf-8"))
    sections = [dict(section) for section in (payload.get("sections") or []) if isinstance(section, dict)]
    selected = {
        "overview": _find_section(sections, "컨트롤 플레인 백업 및 복원 작업"),
        "backup_overview": _find_section(sections, "etcd 백업"),
        "backup_steps": _find_section(sections, "etcd 데이터 백업"),
        "dr_overview": _find_section(sections, "재해 복구 개요"),
        "restore_overview": _find_section(sections, "이전 클러스터 상태로 복원하기"),
        "restore_multi": _find_section(sections, "여러 노드를 위한 이전 클러스터 상태로 복원"),
        "manual_restore": _find_section(sections, "etcd 백업에서 수동으로 클러스터 복원"),
        "failure_signals": _find_section(sections, "지속 가능한 저장 상태 복원에 대한 문제 및 우회 방법"),
    }
    return {
        "overview": _section_body(selected["overview"], max_blocks=4),
        "backup_overview": _section_body(selected["backup_overview"], max_blocks=6),
        "backup_steps": _section_body(selected["backup_steps"], max_blocks=18),
        "dr_overview": _section_body(selected["dr_overview"], max_blocks=6),
        "restore_overview": _section_body(selected["restore_overview"], max_blocks=10),
        "restore_multi": _section_body(selected["restore_multi"], max_blocks=12),
        "manual_restore": _section_body(selected["manual_restore"], max_blocks=28),
        "failure_signals": _section_body(selected["failure_signals"], max_blocks=10),
        "verify": "- 백업 파일 두 개가 모두 있어야 한다.\n- 복구 후 cluster health 와 etcd 상태를 확인한다.",
    }


def _trial_specs(base: dict[str, str]) -> list[tuple[str, str, str]]:
    return [
        ("01_en_slim_then_ko", "EN slim book -> KO translation", f"""# Backup and Restore

## Overview

이 문서는 OpenShift control plane 작업 전에 필요한 etcd 백업 절차와, 백업본에서 클러스터를 수동으로 복구하는 핵심 절차를 정리한다.

{base['overview']}

## Before You Begin

{base['backup_overview']}

## Back Up etcd Data

{base['backup_steps']}

## Restore Cluster State

{base['restore_overview']}

## Manual Restore from etcd Backup

{base['manual_restore']}

## Failure Signals

{base['failure_signals']}
"""),
        ("02_markdown_template_fill", "Normalized markdown -> runbook template", f"""# Backup and Restore

## When To Use

- 클러스터 종료, 재시작, 휴면, 제어 플레인 유지보수 전
- etcd 백업 기준을 다시 확인해야 할 때
- 백업본에서 클러스터를 수동 복구해야 할 때

## Overview

{base['overview']}

## Procedure

{base['backup_steps']}

## Restore

{base['manual_restore']}
"""),
        ("03_section_cluster_slim", "Section clustering -> slim book", f"""# Backup and Restore

## Core Path

- etcd 백업
- 클러스터 상태 복원
- 수동 복구
- 실패 신호 확인

## etcd Backup

{base['backup_steps']}

## Cluster Recovery

{base['manual_restore']}
"""),
        ("04_procedure_code_verify", "Procedure/code/verify first", f"""# Backup and Restore

## Backup

{base['backup_steps']}

## Verify

{base['verify']}

## Restore

{base['manual_restore']}
"""),
        ("05_heading_cleanup_noise_drop", "Heading cleanup + noise drop", f"""# Backup and Restore

## Overview

{base['backup_overview']}

## Backup

{base['backup_steps']}

## Disaster Recovery

{base['dr_overview']}

## Restore

{base['restore_overview']}
"""),
        ("06_full_manual_reshape", "Full-manual summary reshape", f"""# Backup and Restore

## Context

{base['overview']}

## Backup Path

{base['backup_overview']}

{base['backup_steps']}

## Restore Path

{base['restore_overview']}

{base['manual_restore']}
"""),
        ("07_toc_aware_book", "TOC-aware book", f"""# Backup and Restore

## 목차

- Overview
- Backup
- Restore
- Verify
- Failure Signals

## Overview

{base['dr_overview']}

## Backup

{base['backup_steps']}

## Restore

{base['manual_restore']}

## Verify

{base['verify']}
"""),
        ("08_operator_first", "Operator-first shaping", f"""# Backup and Restore

## Start Here

운영자는 이 문서에서 두 가지만 먼저 확인한다.

- 지금 백업을 어떻게 남기는가
- 백업본에서 어떻게 복구하는가

## Backup

{base['backup_overview']}

{base['backup_steps']}

## Restore

{base['manual_restore']}
"""),
        ("09_failure_first_recovery", "Failure-first recovery book", f"""# Backup and Restore

## Failure Signals

{base['failure_signals']}

## Recovery Context

{base['restore_overview']}

## Manual Restore

{base['manual_restore']}
"""),
        ("10_verify_first_ops", "Verify-first ops book", f"""# Backup and Restore

## Success Criteria

{base['verify']}

## Backup

{base['backup_steps']}

## Restore

{base['manual_restore']}

## Multi-Node Restore Notes

{base['restore_multi']}
"""),
    ]


def _trial_docs() -> dict[str, dict[str, object]]:
    common_input = [
        "Red Hat OCP html-single raw HTML",
        "canonical AST extraction",
        "silver_ko translated draft playbook",
    ]
    common_stack = [
        "raw HTML collector cache",
        "canonical AST / normalized sections",
        "LLM translation draft",
        "Markdown final output",
    ]
    return {
        "01_en_slim_then_ko": {
            "goal": "영문에서 slim book 구조를 먼저 잠그고, 그 구조를 한국어로 유지하는 기준선",
            "pipeline": [
                "raw HTML 수집",
                "영문 AST 구조화",
                "핵심 절차만 slim book 으로 재배열",
                "한국어 번역 draft 반영",
                "Markdown 최종본 출력",
            ],
            "stack": common_stack + ["runbook section shaping", "KO final wording pass"],
            "notes": [
                "가장 정석적인 비교 기준",
                "현재 shadow reference 에 가장 가까워야 하는 trial",
            ],
        },
        "02_markdown_template_fill": {
            "goal": "normalized markdown 재료를 템플릿에 강제로 끼워 넣는 방식 검증",
            "pipeline": [
                "translated draft section 추출",
                "Markdown 템플릿 슬롯 채움",
                "Procedure / Restore / When To Use 순서 고정",
            ],
            "stack": common_input + ["Markdown template fill", "section slot mapping"],
            "notes": [
                "템플릿 강제력이 높음",
                "과도한 정보 손실 가능성 확인용",
            ],
        },
        "03_section_cluster_slim": {
            "goal": "비슷한 section 을 묶어 core path 만 남기는 방식 검증",
            "pipeline": [
                "translated draft section 스캔",
                "backup / restore / failure cluster 추출",
                "core path 만 slim book 으로 출력",
            ],
            "stack": common_input + ["section clustering heuristic", "slim TOC"],
            "notes": [
                "정보 밀도를 가장 많이 줄이는 방식",
                "first reading path 가 잘 드러나는지 확인",
            ],
        },
        "04_procedure_code_verify": {
            "goal": "절차, 코드, 검증을 최우선으로 두는 runbook형",
            "pipeline": [
                "procedure block 우선 추출",
                "code block 보존",
                "verify 축을 상단으로 배치",
            ],
            "stack": common_input + ["procedure-first shaping", "code block preservation"],
            "notes": [
                "운영 실무용에 가까움",
                "서술보다 실행성이 중요할 때 유리",
            ],
        },
        "05_heading_cleanup_noise_drop": {
            "goal": "번호와 broad heading 잡음을 강하게 걷어내는 방식 검증",
            "pipeline": [
                "heading number 제거",
                "잡음 section 제외",
                "남은 핵심 section 을 재배열",
            ],
            "stack": common_input + ["heading cleanup", "noise drop", "section pruning"],
            "notes": [
                "가독성 문제를 직접 겨냥",
                "원문 정보 유실 가능성도 같이 봐야 함",
            ],
        },
        "06_full_manual_reshape": {
            "goal": "정보는 넓게 남기되 reader surface 만 재배열하는 방식 검증",
            "pipeline": [
                "full manual 중 핵심 설명 유지",
                "backup path / restore path 로 재배치",
                "Markdown 최종본 출력",
            ],
            "stack": common_input + ["wide-context reshape", "guided manual ordering"],
            "notes": [
                "요약보다 문맥 유지에 강함",
                "길어질 위험이 있음",
            ],
        },
        "07_toc_aware_book": {
            "goal": "목차형 독해를 먼저 세우는 방식 검증",
            "pipeline": [
                "핵심 축을 TOC로 먼저 제시",
                "본문을 TOC 순서대로 재배열",
                "verify/failure 를 명시적 섹션으로 분리",
            ],
            "stack": common_input + ["TOC-aware structure", "manual book navigation mindset"],
            "notes": [
                "나중에 좌측 목차 viewer 와 잘 맞는지 보기 좋음",
            ],
        },
        "08_operator_first": {
            "goal": "운영자가 가장 먼저 보는 관점으로만 재배열",
            "pipeline": [
                "운영자 질문 기준으로 섹션 선택",
                "backup -> restore 순서만 남김",
                "배경 설명 최소화",
            ],
            "stack": common_input + ["role-based shaping", "operator-first summarization"],
            "notes": [
                "구매자 데모보다 운영자 실사용에 가까움",
            ],
        },
        "09_failure_first_recovery": {
            "goal": "장애 조짐과 복구를 먼저 보여주는 recovery book 검증",
            "pipeline": [
                "failure signal section 우선",
                "recovery context 연결",
                "manual restore 절차 배치",
            ],
            "stack": common_input + ["failure-first structuring", "recovery playbook ordering"],
            "notes": [
                "트러블슈팅형 파생 북에 적합한지 확인용",
            ],
        },
        "10_verify_first_ops": {
            "goal": "성공 조건과 검증 포인트를 먼저 두는 방식 검증",
            "pipeline": [
                "success criteria 정리",
                "backup/restore 본문 연결",
                "verify-first 운영 문서로 출력",
            ],
            "stack": common_input + ["verify-first structure", "ops acceptance criteria"],
            "notes": [
                "운영 검증 관점이 강함",
                "실행 후 무엇을 확인하는지 빨리 보이게 함",
            ],
        },
    }


def main() -> int:
    build_parser().parse_args()
    base = _load_base_texts()
    target_root = ROOT / "tests" / "reader_grade_pipeline_trials" / "backup_and_restore"
    target_root.mkdir(parents=True, exist_ok=True)
    index_lines = ["# Backup and Restore Pipeline Trials", ""]
    docs = _trial_docs()
    for name, pipeline_name, body in _trial_specs(base):
        trial_dir = target_root / name
        trial_dir.mkdir(parents=True, exist_ok=True)
        detail = docs[name]
        pipeline_lines = "\n".join(f"- {item}" for item in detail["pipeline"])
        stack_lines = "\n".join(f"- {item}" for item in detail["stack"])
        note_lines = "\n".join(f"- {item}" for item in detail["notes"])
        (trial_dir / "pipeline.md").write_text(
            (
                f"# {name}\n\n"
                f"## Pipeline Name\n\n"
                f"`{pipeline_name}`\n\n"
                f"## Goal\n\n"
                f"{detail['goal']}\n\n"
                f"## Source\n\n"
                f"- `backup_and_restore`\n"
                f"- translated draft input from `data/silver_ko/translation_drafts/playbooks/backup_and_restore.json`\n\n"
                f"## Pipeline Steps\n\n"
                f"{pipeline_lines}\n\n"
                f"## Tech Stack\n\n"
                f"{stack_lines}\n\n"
                f"## Notes\n\n"
                f"{note_lines}\n"
            ),
            encoding="utf-8",
        )
        (trial_dir / "output.md").write_text(body.strip() + "\n", encoding="utf-8")
        (trial_dir / "meta.json").write_text(
            json.dumps(
                {
                    "trial": name,
                    "pipeline": pipeline_name,
                    "source_slug": "backup_and_restore",
                    "output": "output.md",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        index_lines.append(f"- `{name}`: `{pipeline_name}`")
    (target_root / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(json.dumps({"trial_count": 10, "root": str(target_root)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
