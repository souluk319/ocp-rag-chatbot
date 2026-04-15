from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tsx = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
    css = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.css").read_text(encoding="utf-8")
    source_books = (root / "src" / "play_book_studio" / "app" / "source_books.py").read_text(encoding="utf-8")

    report = {
        "status": "ok",
        "truth_badge_block_supports_show_meta": "showMeta = true" in tsx,
        "assistant_truth_row_is_compact": "badgeClassName=\"assistant-truth-chip\"" in tsx and "showMeta={false}" in tsx,
        "session_truth_row_is_compact": "badgeClassName=\"session-truth-chip\"" in tsx and tsx.count("showMeta={false}") >= 2,
        "related_links_use_summary_not_truth_meta": "const meta = link.summary ? [link.summary] : [];" in tsx,
        "duplicate_empty_citation_badge_rule_removed": ".citation-tag-badge {\n}" not in css,
        "customer_pack_viewer_drops_runtime_title_duplication": 'evidence_badges = [\n        f"approval: {approval_state}",\n        f"publication: {publication_state}",' in source_books,
        "customer_pack_viewer_uses_compact_copy": "customer source-first private runtime 문서다. 아래 evidence 로 현재 상태만 확인하면 된다." in source_books,
    }
    if not all(report.values()):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    out = root / "reports" / "build_logs" / "truth_surface_trim_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
