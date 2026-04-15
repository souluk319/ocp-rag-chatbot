from __future__ import annotations

import json
import tempfile
from pathlib import Path

from play_book_studio.app.intake_api import create_customer_pack_draft, delete_customer_pack_draft
from play_book_studio.intake.books.store import CustomerPackDraftStore
from play_book_studio.intake.normalization.service import CustomerPackNormalizeService
from play_book_studio.intake.capture.service import CustomerPackCaptureService


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    temp_path = Path(tempfile.gettempdir()) / "customer-pack-evidence-smoke.md"
    temp_path.write_text(
        "# Customer Pack Evidence Smoke\n\n## Procedure\n\nRun this command.\n\n```bash\noc get nodes\n```\n",
        encoding="utf-8",
    )

    draft = create_customer_pack_draft(
        REPO_ROOT,
        {
            "source_type": "md",
            "uri": str(temp_path),
            "title": "Customer Pack Evidence Smoke",
            "language_hint": "ko",
        },
    )
    draft_id = str(draft["draft_id"])
    report: dict[str, object]
    try:
        captured = CustomerPackCaptureService(REPO_ROOT).capture(draft_id=draft_id).to_dict()
        normalized = CustomerPackNormalizeService(REPO_ROOT).normalize(draft_id=draft_id).to_dict()
        stored = CustomerPackDraftStore(REPO_ROOT).get(draft_id)
        canonical_path = Path(str(normalized.get("canonical_book_path") or ""))
        canonical_payload = json.loads(canonical_path.read_text(encoding="utf-8"))
        evidence = dict(canonical_payload.get("customer_pack_evidence") or {})

        report = {
            "status": "ok",
            "draft_id": draft_id,
            "captured_status": captured.get("status"),
            "normalized_status": normalized.get("status"),
            "source_lane": stored.source_lane if stored else "",
            "source_fingerprint_present": bool(stored and stored.source_fingerprint),
            "parser_route": stored.parser_route if stored else "",
            "parser_backend": stored.parser_backend if stored else "",
            "pack_id": stored.plan.pack_id if stored else "",
            "publication_state": stored.publication_state if stored else "",
            "approval_state": stored.approval_state if stored else "",
            "evidence_present": bool(evidence),
            "evidence_source_lane": evidence.get("source_lane"),
            "evidence_pack_id": evidence.get("pack_id"),
            "evidence_pack_version": evidence.get("pack_version"),
            "evidence_parser_route": evidence.get("parser_route"),
            "evidence_publication_state": evidence.get("publication_state"),
            "canonical_book_exists": canonical_path.exists(),
        }
        required_truth = all(
            [
                report["captured_status"] == "captured",
                report["normalized_status"] == "normalized",
                report["source_lane"] == "customer_source_first_pack",
                report["source_fingerprint_present"] is True,
                bool(report["parser_route"]),
                report["evidence_present"] is True,
                report["evidence_source_lane"] == "customer_source_first_pack",
                bool(report["evidence_pack_id"]),
                bool(report["evidence_pack_version"]),
                bool(report["evidence_parser_route"]),
                report["canonical_book_exists"] is True,
            ]
        )
        report["status"] = "ok" if required_truth else "fail"
    finally:
        delete_customer_pack_draft(REPO_ROOT, draft_id)
        temp_path.unlink(missing_ok=True)

    out_dir = REPO_ROOT / "reports" / "build_logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "customer_pack_evidence_report.json"
    md_path = out_dir / "customer_pack_evidence_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_lines = ["# Customer Pack Evidence Report", ""]
    for key, value in report.items():
        md_lines.append(f"- {key}: `{value}`")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
