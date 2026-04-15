from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.source_books import build_chat_navigation_links


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    citations = [
        {
            "book_slug": "backup_and_restore",
            "section": "Overview",
            "excerpt": "etcd backup and restore",
            "href": "/playbooks/wiki-runtime/active/backup_and_restore/index.html#overview",
        }
    ]
    links = build_chat_navigation_links(root, citations)
    validated = next(
        (item for item in links if str(item.get("boundary_truth") or "") == "official_validated_runtime"),
        {},
    )
    entity = next((item for item in links if str(item.get("kind") or "") == "entity"), {})
    workspace_page = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
    report = {
        "status": "ok",
        "validated_link_found": bool(validated),
        "validated_boundary_badge": str(validated.get("boundary_badge") or ""),
        "validated_runtime_truth_label": str(validated.get("runtime_truth_label") or ""),
        "validated_source_lane": str(validated.get("source_lane") or ""),
        "entity_link_has_no_boundary_truth": not bool(entity.get("boundary_truth")),
        "frontend_mentions_candidate_runtime": "Candidate Runtime" in workspace_page,
        "frontend_uses_truth_surface_for_related_links": "truthSurfaceCopy(link).label" in workspace_page,
    }
    if not (
        report["validated_link_found"]
        and report["validated_boundary_badge"] == "Validated Runtime"
        and report["validated_runtime_truth_label"].endswith("Runtime")
        and report["validated_source_lane"] == "approved_wiki_runtime"
        and report["entity_link_has_no_boundary_truth"]
        and report["frontend_mentions_candidate_runtime"]
        and report["frontend_uses_truth_surface_for_related_links"]
    ):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    report_path = root / "reports" / "build_logs" / "chat_truth_taxonomy_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
