from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.english_residue_taxonomy import (  # noqa: E402
    KEEP_TERMS_CODE_PATHS,
    MIXED_LINE,
    TRANSLATE_TARGET_PROSE,
    classify_english_residue_line,
)
from play_book_studio.execution_guard import run_guarded_script  # noqa: E402

RUNTIME_DIR = ROOT / "data" / "wiki_runtime_books" / "full_rebuild"
CANDIDATE_DIR = ROOT / "data" / "gold_candidate_books" / "full_rebuild"
REPORT_PATH = ROOT / "reports" / "build_logs" / "ocp420_english_residue_taxonomy_report.json"
QUALIFICATION_REPORT_PATH = ROOT / "reports" / "build_logs" / "ocp420_redhat_expression_qualification_report.json"

_CATEGORY_ORDER = (
    TRANSLATE_TARGET_PROSE,
    KEEP_TERMS_CODE_PATHS,
    MIXED_LINE,
)
_CATEGORY_DESCRIPTIONS = {
    TRANSLATE_TARGET_PROSE: (
        "Reader-facing English prose or headings that should be translated and count as qualification-failing residue."
    ),
    KEEP_TERMS_CODE_PATHS: (
        "Product terms, CLI commands, code, paths, URLs, source tags, and markup traces that must be preserved and do not fail qualification."
    ),
    MIXED_LINE: (
        "Korean-English mixed lines or prose-plus-code lines that need review and are tracked separately from automatic qualification failure."
    ),
}


def _sample_payload(slug: str, line_no: int, line: str, result: Any) -> dict[str, Any]:
    return {
        "slug": slug,
        "line_no": line_no,
        "line": line,
        "general_word_count": result.general_word_count,
        "protected_token_count": result.protected_token_count,
        "has_hangul": result.has_hangul,
        "codeish": result.codeish,
    }


def _scan_runtime_markdown() -> dict[str, Any]:
    totals: Counter[str] = Counter()
    file_counts: dict[str, Counter[str]] = {}
    global_samples: dict[str, list[dict[str, Any]]] = {kind: [] for kind in _CATEGORY_ORDER}
    file_samples: dict[str, dict[str, list[dict[str, Any]]]] = {}

    for markdown_path in sorted(RUNTIME_DIR.glob("*.md")):
        slug = markdown_path.stem
        counter: Counter[str] = Counter()
        local_samples = {kind: [] for kind in _CATEGORY_ORDER}
        for line_no, raw_line in enumerate(markdown_path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            result = classify_english_residue_line(line)
            if not result.kind:
                continue
            counter[result.kind] += 1
            totals[result.kind] += 1
            payload = _sample_payload(slug, line_no, line, result)
            if len(local_samples[result.kind]) < 5:
                local_samples[result.kind].append(payload)
            if len(global_samples[result.kind]) < 10:
                global_samples[result.kind].append(payload)
        file_counts[slug] = counter
        file_samples[slug] = local_samples

    return {
        "totals": {kind: int(totals.get(kind, 0)) for kind in _CATEGORY_ORDER},
        "files": file_counts,
        "samples": global_samples,
        "file_samples": file_samples,
    }


def _top_files(file_counts: dict[str, Counter[str]], kind: str, limit: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(
        (
            {"file": f"{slug}.md", "count": int(counter.get(kind, 0))}
            for slug, counter in file_counts.items()
            if int(counter.get(kind, 0)) > 0
        ),
        key=lambda item: (-int(item["count"]), str(item["file"])),
    )
    return ranked[:limit]


def _compare_candidate_runtime() -> tuple[bool, list[dict[str, str]]]:
    mismatches: list[dict[str, str]] = []
    names = {path.name for path in RUNTIME_DIR.glob("*.md")}
    names.update(path.name for path in CANDIDATE_DIR.glob("*.md"))
    for name in sorted(names):
        runtime_path = RUNTIME_DIR / name
        candidate_path = CANDIDATE_DIR / name
        if not runtime_path.exists():
            mismatches.append({"file": name, "reason": "runtime_missing"})
            continue
        if not candidate_path.exists():
            mismatches.append({"file": name, "reason": "candidate_missing"})
            continue
        runtime_text = runtime_path.read_text(encoding="utf-8")
        candidate_text = candidate_path.read_text(encoding="utf-8")
        if runtime_text != candidate_text:
            mismatches.append({"file": name, "reason": "content_mismatch"})
    return (len(mismatches) == 0), mismatches


def _build_taxonomy_report() -> dict[str, Any]:
    scan = _scan_runtime_markdown()
    candidate_runtime_identical, candidate_runtime_mismatches = _compare_candidate_runtime()
    translate_top_files = _top_files(scan["files"], TRANSLATE_TARGET_PROSE)
    mixed_top_files = _top_files(scan["files"], MIXED_LINE)
    keep_top_files = _top_files(scan["files"], KEEP_TERMS_CODE_PATHS)
    files_with_translation_target = sum(
        1 for counter in scan["files"].values() if int(counter.get(TRANSLATE_TARGET_PROSE, 0)) > 0
    )
    files_with_mixed_lines = sum(1 for counter in scan["files"].values() if int(counter.get(MIXED_LINE, 0)) > 0)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_dir": str(RUNTIME_DIR),
        "candidate_dir": str(CANDIDATE_DIR),
        "taxonomy": [
            {"kind": kind, "description": _CATEGORY_DESCRIPTIONS[kind]}
            for kind in _CATEGORY_ORDER
        ],
        "totals": scan["totals"],
        "files_with_translate_target_prose": files_with_translation_target,
        "files_with_mixed_lines": files_with_mixed_lines,
        "top_translate_target_files": translate_top_files,
        "top_keep_terms_code_paths_files": keep_top_files,
        "top_mixed_files": mixed_top_files,
        "sample_translate_target_prose": scan["samples"][TRANSLATE_TARGET_PROSE],
        "sample_keep_terms_code_paths": scan["samples"][KEEP_TERMS_CODE_PATHS],
        "sample_mixed_lines": scan["samples"][MIXED_LINE],
        "candidate_runtime_identical": candidate_runtime_identical,
        "candidate_runtime_mismatches": candidate_runtime_mismatches,
    }


def _update_qualification_report(taxonomy_report: dict[str, Any]) -> None:
    if not QUALIFICATION_REPORT_PATH.exists():
        return
    payload = json.loads(QUALIFICATION_REPORT_PATH.read_text(encoding="utf-8"))
    criteria = payload.get("acceptance_criteria")
    if not isinstance(criteria, dict):
        return
    target = criteria.get("AC-EXP-3-korean_completeness")
    if not isinstance(target, dict):
        return

    translate_count = int(taxonomy_report["totals"][TRANSLATE_TARGET_PROSE])
    keep_count = int(taxonomy_report["totals"][KEEP_TERMS_CODE_PATHS])
    mixed_count = int(taxonomy_report["totals"][MIXED_LINE])

    target["status"] = "pass" if translate_count == 0 else "fail"
    target["measurement"] = "runtime markdown english residue taxonomy scan + candidate/runtime equality check"
    target["evidence"] = {
        "translate_target_prose_lines": translate_count,
        "keep_terms_code_paths_lines": keep_count,
        "mixed_lines": mixed_count,
        "files_with_translate_target_prose": int(taxonomy_report["files_with_translate_target_prose"]),
        "files_with_mixed_lines": int(taxonomy_report["files_with_mixed_lines"]),
        "top_translate_target_files": taxonomy_report["top_translate_target_files"],
        "top_keep_terms_code_paths_files": taxonomy_report["top_keep_terms_code_paths_files"],
        "top_mixed_files": taxonomy_report["top_mixed_files"],
        "sample_translate_target_prose": taxonomy_report["sample_translate_target_prose"],
        "sample_keep_terms_code_paths": taxonomy_report["sample_keep_terms_code_paths"],
        "sample_mixed_lines": taxonomy_report["sample_mixed_lines"],
        "candidate_runtime_identical": bool(taxonomy_report["candidate_runtime_identical"]),
        "candidate_runtime_mismatches": taxonomy_report["candidate_runtime_mismatches"],
        "taxonomy_report_path": str(REPORT_PATH),
    }
    target["current_gap"] = (
        "qualification failure is driven only by untranslated reader-facing English prose/headings; "
        "product terms, CLI/code/paths are excluded from failure count and mixed lines remain review backlog"
        if translate_count > 0
        else "no qualification-failing untranslated reader-facing English prose/headings remain"
    )
    QUALIFICATION_REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    report = _build_taxonomy_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _update_qualification_report(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
