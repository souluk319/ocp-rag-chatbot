from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.stage11_bundle_utils import load_json, utc_now, write_checksum_manifest, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply an approval decision to a Stage 11 bundle and refresh checksums.")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--status", choices=("pending", "approved", "rejected"), default="approved")
    parser.add_argument("--reviewer", default="local-reviewer")
    parser.add_argument("--reviewed-at", default="")
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--smoke-query-report", default="")
    parser.add_argument("--removal-impact-summary", dest="removal_impact_summary", default="")
    parser.add_argument("--evidence-link", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_root = args.bundle.resolve()
    manifest_path = bundle_root / "manifest.json"
    approval_path = bundle_root / "approval.json"
    if not manifest_path.exists() or not approval_path.exists():
        raise SystemExit(f"Bundle manifest or approval record is missing under {bundle_root}")

    manifest = load_json(manifest_path)
    previous = load_json(approval_path)
    approved = args.status == "approved"
    approval = {
        "bundle_id": manifest.get("bundle_id", bundle_root.name),
        "status": args.status,
        "reviewer": args.reviewer,
        "reviewed_at": args.reviewed_at or utc_now(),
        "source_scope_verified": approved,
        "removal_impact_checked": approved,
        "checksum_verified": approved,
        "approved_for_import": approved,
    }
    if args.note:
        approval["notes"] = args.note
    elif previous.get("notes"):
        approval["notes"] = previous["notes"]
    if args.smoke_query_report:
        approval["smoke_query_report"] = args.smoke_query_report
    elif previous.get("smoke_query_report"):
        approval["smoke_query_report"] = previous["smoke_query_report"]
    if args.removal_impact_summary:
        approval["removal_impact_summary"] = args.removal_impact_summary
    elif previous.get("removal_impact_summary"):
        approval["removal_impact_summary"] = previous["removal_impact_summary"]
    if args.evidence_link:
        approval["evidence_links"] = args.evidence_link
    elif previous.get("evidence_links"):
        approval["evidence_links"] = previous["evidence_links"]

    manifest["approval"] = {
        "status": approval["status"],
        "reviewer": approval["reviewer"],
        "reviewed_at": approval["reviewed_at"],
    }
    write_json(approval_path, approval)
    write_json(manifest_path, manifest)
    write_checksum_manifest(bundle_root)

    print(
        json.dumps(
            {
                "bundle_id": approval["bundle_id"],
                "status": approval["status"],
                "reviewer": approval["reviewer"],
                "bundle_path": str(bundle_root),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
