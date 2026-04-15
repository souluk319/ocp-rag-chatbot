from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.server_chat import _summarize_citation_truth


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    workspace_page = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
    summary = _summarize_citation_truth(
        {
            "citations": [
                {
                    "source_lane": "approved_wiki_runtime",
                    "boundary_truth": "official_validated_runtime",
                    "runtime_truth_label": "OpenShift 4.20 Runtime",
                    "boundary_badge": "Validated Runtime",
                    "publication_state": "published",
                    "approval_state": "approved",
                },
                {
                    "source_lane": "customer_source_first_pack",
                    "boundary_truth": "private_customer_pack_runtime",
                    "runtime_truth_label": "Customer Source-First Pack",
                    "boundary_badge": "Private Runtime",
                    "publication_state": "draft",
                    "approval_state": "unreviewed",
                },
            ]
        }
    )
    report = {
        "status": "ok",
        "mixed_boundary_truth": str(summary.get("boundary_truth") or ""),
        "mixed_boundary_badge": str(summary.get("boundary_badge") or ""),
        "mixed_runtime_truth_label": str(summary.get("runtime_truth_label") or ""),
        "mixed_source_lane": str(summary.get("source_lane") or ""),
        "frontend_mentions_mixed_runtime": "Mixed Runtime" in workspace_page,
        "frontend_mentions_runtime_copy_logic": "runtimeTruthLabel || 'Official + Private Runtime'" in workspace_page,
    }
    if not (
        report["mixed_boundary_truth"] == "mixed_runtime_bridge"
        and report["mixed_boundary_badge"] == "Mixed Runtime"
        and report["mixed_runtime_truth_label"] == "OpenShift 4.20 Runtime + Customer Source-First Pack"
        and report["mixed_source_lane"] == "mixed_runtime_bridge"
        and report["frontend_mentions_mixed_runtime"]
        and report["frontend_mentions_runtime_copy_logic"]
    ):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    report_path = root / "reports" / "build_logs" / "mixed_runtime_truth_surface_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
