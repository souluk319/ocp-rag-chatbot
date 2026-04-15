from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.source_books import internal_customer_pack_viewer_html


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    viewer_path = "/playbooks/customer-packs/synthetic-customer-pack/index.html"
    source_books = (root / "src" / "play_book_studio" / "app" / "source_books.py").read_text(encoding="utf-8")
    viewer_page = (root / "src" / "play_book_studio" / "app" / "viewer_page.py").read_text(encoding="utf-8")

    report = {
        "status": "ok",
        "source_uses_viewer_truth_topline": "viewer-truth-topline" in source_books,
        "source_uses_viewer_truth_title": "viewer-truth-title" in source_books,
        "viewer_has_viewer_truth_badge_css": ".viewer-truth-badge" in viewer_page,
        "viewer_has_viewer_truth_title_css": ".viewer-truth-title" in viewer_page,
        "viewer_meta_pill_unified": ".wiki-entity-list a,\n          .meta-pill" in viewer_page,
        "viewer_html_function_exists": callable(internal_customer_pack_viewer_html),
    }
    if not all(report.values()):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    out = root / "reports" / "build_logs" / "customer_pack_truth_visual_system_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
