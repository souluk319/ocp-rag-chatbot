from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "build_logs" / "pipeline_quality_outlier_report.json"
DEFAULT_CHECKLIST_OUTPUT = ROOT / "reports" / "build_logs" / "demo_quality_checklist.json"
ACTIVE_MANIFEST = ROOT / "data" / "wiki_runtime_books" / "active_manifest.json"
SOURCE_APPROVAL_REPORT = ROOT / "artifacts" / "corpus" / "source_approval_report.json"
PLAYBOOK_DIR = ROOT / "data" / "gold_manualbook_ko" / "playbooks"
RAW_HTML_DIR = ROOT / "data" / "bronze" / "raw_html"

_RAW_HEADING_RE = re.compile(r"<h[234]\b", re.IGNORECASE)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0


def _section_count(path: Path) -> int:
    if not path.exists():
        return 0
    payload = _read_json(path)
    return len(payload.get("sections") or [])


def _raw_heading_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(_RAW_HEADING_RE.findall(path.read_text(encoding="utf-8")))


def _percentile_floor(values: list[int], percentile: float) -> int:
    ordered = sorted(int(value) for value in values if int(value) >= 0)
    if not ordered:
        return 0
    index = max(math.ceil(len(ordered) * percentile) - 1, 0)
    return ordered[index]


def _book_report_map() -> dict[str, dict[str, Any]]:
    payload = _read_json(SOURCE_APPROVAL_REPORT)
    books = payload.get("books") or []
    return {
        str(book.get("book_slug") or "").strip(): dict(book)
        for book in books
        if str(book.get("book_slug") or "").strip()
    }


def _classify_outlier(
    *,
    book_report: dict[str, Any],
    runtime_excerpt: str,
    section_count: int,
    split_ratio: float,
) -> tuple[str, str]:
    source_state_reason = str(book_report.get("source_state_reason") or "").strip()
    title_english_like = bool(book_report.get("title_english_like") or False)
    reader_grade_failed = bool(book_report.get("manualbook_reader_grade_failed") or False)
    runtime_lower = runtime_excerpt.lower()
    if (
        "separate documentation set" in runtime_lower
        or "separate documentation" in runtime_lower
        or ("manual_synthesis" in source_state_reason and section_count <= 2)
    ) and section_count <= 8:
        return (
            "source collection problem",
            "runtime book is effectively a redirect/landing summary rather than a full collected source",
        )
    if split_ratio < 0.50:
        return (
            "section split problem",
            "raw heading density is materially higher than playbook section density",
        )
    if title_english_like or reader_grade_failed:
        return (
            "reader-grade quality problem",
            "reader-facing title/headings remain mixed-language or weakly normalized",
        )
    return (
        "normalize problem",
        "runtime structure is thinner than expected but source collection evidence is inconclusive",
    )


def build_reports(
    *,
    output_path: Path = DEFAULT_OUTPUT,
    checklist_output_path: Path = DEFAULT_CHECKLIST_OUTPUT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    active_manifest = _read_json(ACTIVE_MANIFEST)
    active_entries = [dict(entry) for entry in (active_manifest.get("entries") or []) if isinstance(entry, dict)]
    book_reports = _book_report_map()
    section_counts = [
        _section_count(PLAYBOOK_DIR / f"{str(entry.get('slug') or '').strip()}.json")
        for entry in active_entries
        if str(entry.get("slug") or "").strip()
    ]
    low_section_threshold = _percentile_floor(section_counts, 0.10)
    outliers: list[dict[str, Any]] = []
    for entry in active_entries:
        slug = str(entry.get("slug") or "").strip()
        if not slug:
            continue
        title = str(entry.get("title") or slug).strip() or slug
        playbook_path = PLAYBOOK_DIR / f"{slug}.json"
        runtime_path = Path(str(entry.get("runtime_path") or "").strip())
        raw_html_path = RAW_HTML_DIR / f"{slug}.html"
        raw_meta_path = RAW_HTML_DIR / f"{slug}.meta.json"
        section_count = _section_count(playbook_path)
        raw_heading_count = _raw_heading_count(raw_html_path)
        split_ratio = round(section_count / raw_heading_count, 2) if raw_heading_count else 0.0
        runtime_line_count = _line_count(runtime_path)
        book_report = dict(book_reports.get(slug) or {})
        runtime_excerpt = runtime_path.read_text(encoding="utf-8")[:2000] if runtime_path.exists() else ""
        is_low_section = section_count <= low_section_threshold
        weak_structure = raw_heading_count > 0 and split_ratio < 0.50
        if not (is_low_section or weak_structure):
            continue
        classification, note = _classify_outlier(
            book_report=book_report,
            runtime_excerpt=runtime_excerpt,
            section_count=section_count,
            split_ratio=split_ratio,
        )
        outliers.append(
            {
                "book_slug": slug,
                "title": title,
                "classification": classification,
                "counts": {
                    "section_count": section_count,
                    "chunk_count": int(book_report.get("chunk_count") or 0),
                    "raw_heading_count": raw_heading_count,
                    "split_ratio": split_ratio,
                    "runtime_line_count": runtime_line_count,
                    "active_low_section_threshold": low_section_threshold,
                },
                "evidence_paths": [
                    str(playbook_path),
                    str(runtime_path),
                    str(raw_meta_path if raw_meta_path.exists() else raw_html_path),
                ],
                "source_state_reason": str(book_report.get("source_state_reason") or "").strip(),
                "note": note,
            }
        )
    outliers.sort(
        key=lambda item: (
            int(item["counts"]["section_count"]),
            float(item["counts"]["split_ratio"]),
            str(item["book_slug"]),
        )
    )
    report = {
        "generated_at_utc": _utc_now(),
        "runtime_book_count": len(active_entries),
        "thresholds": {
            "low_section_threshold": low_section_threshold,
            "low_section_percentile": "p10",
            "weak_structure_split_ratio_threshold": 0.50,
        },
        "outlier_count": len(outliers),
        "classification_counts": dict(Counter(str(item["classification"]) for item in outliers)),
        "outliers": outliers,
    }
    blockers = [
        {
            "id": "monitoring_source_scope",
            "summary": "monitoring runtime book is still a shallow landing-page synthesis with only 2 sections",
            "book_slug": "monitoring",
        },
        {
            "id": "logging_source_scope",
            "summary": "logging runtime book is still a shallow landing-page synthesis with only 2 sections",
            "book_slug": "logging",
        },
    ][:3]
    warnings = [
        {
            "id": "observability_overview_split",
            "summary": "observability_overview remains structurally thin versus raw heading density",
            "book_slug": "observability_overview",
        },
        {
            "id": "customer_pack_post_response_sanitize_gap",
            "summary": "browser-facing upload/capture/normalize/ingest POST responses still carry raw draft payloads",
        },
        {
            "id": "workspace_trace_raw_dump",
            "summary": "Workspace forensic trace still exposes raw retrieval/pipeline payload dumps for browser users",
        },
    ][:5]
    later = [
        {
            "id": "asset_ownership_boundary",
            "summary": "customer-pack asset ownership proof for draft_id::asset_slug paths is still not enforced",
        },
        {
            "id": "blocked_catalog_backfill",
            "summary": "the broader blocked 84-book catalog remains outside this packet scope",
        },
    ]
    checklist = {
        "generated_at_utc": _utc_now(),
        "blocker": blockers,
        "warning": warnings,
        "later": later,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checklist_output_path.write_text(json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report, checklist


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build pipeline quality outlier and demo checklist reports.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to write the outlier report JSON.",
    )
    parser.add_argument(
        "--checklist-output",
        type=Path,
        default=DEFAULT_CHECKLIST_OUTPUT,
        help="Path to write the demo quality checklist JSON.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build_reports(
        output_path=args.output,
        checklist_output_path=args.checklist_output,
    )
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
