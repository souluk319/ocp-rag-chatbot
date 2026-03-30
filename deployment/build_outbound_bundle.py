from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.stage11_bundle_utils import (
    diff_documents,
    extract_source_manifest_version,
    load_baseline_documents,
    load_manifest_documents,
    repo_relative,
    repo_root,
    utc_now,
    write_checksum_manifest,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an outbound Stage 11 air-gap bundle.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "openshift-docs-p0.json",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=repo_root() / "data" / "manifests" / "approved-baseline.json",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=repo_root() / "configs" / "source-manifest.yaml",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=repo_root() / "data" / "packages" / "outbound",
    )
    parser.add_argument("--bundle-id", default="")
    parser.add_argument("--mode", choices=("delta", "seed"), default="delta")
    parser.add_argument("--reviewer", default="pending-review")
    parser.add_argument("--approval-status", choices=("pending", "approved", "rejected"), default="pending")
    parser.add_argument("--reviewed-at", default="")
    parser.add_argument("--source-scope-verified", action="store_true")
    parser.add_argument("--removal-impact-checked", action="store_true")
    parser.add_argument("--checksum-verified", action="store_true")
    parser.add_argument("--approved-for-import", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def build_bundle_id(*, source_id: str, mode: str) -> str:
    timestamp = utc_now().replace(":", "").replace("-", "")
    return f"{source_id}-{mode}-{timestamp}"


def emitted_record(change: dict[str, Any]) -> dict[str, Any]:
    record = change["current"] or change["previous"]
    assert record is not None
    return {
        "document_id": change["document_id"],
        "title": record.get("title", ""),
        "relative_path": record.get("normalized_relative_path", ""),
        "checksum": record.get("checksum", ""),
        "action": change["action"],
        "source_id": record.get("source_id", ""),
        "category": record.get("category", ""),
        "version": record.get("version", ""),
        "view_relative_path": record.get("view_relative_path", ""),
        "view_checksum": record.get("html_checksum", ""),
        "viewer_url": record.get("viewer_url", ""),
        "source_url": record.get("source_url", ""),
        "top_level_dir": record.get("top_level_dir", ""),
        "changed_fields": change.get("changed_fields", []),
    }


def copy_payload(bundle_root: Path, record: dict[str, Any], manifest: dict[str, Any]) -> None:
    document_lookup = {item["document_id"]: item for item in manifest.get("documents", [])}
    source = document_lookup[record["document_id"]]
    normalized_dst = bundle_root / record["relative_path"]
    normalized_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(source["normalized_path"]), normalized_dst)

    view_relative_path = record.get("view_relative_path", "")
    if view_relative_path:
        html_dst = bundle_root / view_relative_path
        html_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(source["html_path"]), html_dst)


def main() -> int:
    args = parse_args()
    manifest, _, current_index = load_manifest_documents(args.manifest)
    baseline, baseline_documents, baseline_index = load_baseline_documents(args.baseline)

    if args.mode == "delta" and not baseline_documents:
        raise SystemExit("Approved baseline does not contain document snapshots; refresh it before delta bundle generation.")

    source_manifest_version = extract_source_manifest_version(args.source_manifest)
    bundle_id = args.bundle_id.strip() or build_bundle_id(source_id=manifest.get("source_id", "bundle"), mode=args.mode)
    bundle_root = args.output_root / bundle_id
    if bundle_root.exists():
        if not args.force:
            raise SystemExit(f"Bundle path already exists: {bundle_root}")
        shutil.rmtree(bundle_root)

    bundle_root.mkdir(parents=True, exist_ok=True)
    for relative_dir in ("documents", "views", "manifests", "reports"):
        (bundle_root / relative_dir).mkdir(parents=True, exist_ok=True)

    changes = diff_documents(current_index, baseline_index, mode=args.mode)
    emitted_files: list[dict[str, Any]] = []
    for change in changes:
        record = emitted_record(change)
        if change["action"] in {"added", "changed"}:
            copy_payload(bundle_root, record, manifest)
        emitted_files.append(record)

    reviewed_at = args.reviewed_at.strip() or utc_now()
    approval_payload = {
        "bundle_id": bundle_id,
        "status": args.approval_status,
        "reviewer": args.reviewer,
        "reviewed_at": reviewed_at,
        "source_scope_verified": bool(args.source_scope_verified or args.approval_status == "approved"),
        "removal_impact_checked": bool(args.removal_impact_checked or args.approval_status == "approved"),
        "checksum_verified": bool(args.checksum_verified or args.approval_status == "approved"),
        "approved_for_import": bool(args.approved_for_import or args.approval_status == "approved"),
        "notes": [],
    }
    if args.mode == "seed":
        approval_payload["notes"].append("Seed bundle: packages the full approved corpus for first-cycle import testing.")

    manifest_payload = {
        "bundle_id": bundle_id,
        "created_at": utc_now(),
        "source_manifest_version": source_manifest_version,
        "normalized_manifest_id": manifest.get("manifest_id", ""),
        "baseline_manifest_id": baseline.get("manifest_id", ""),
        "source_profile": manifest.get("source_profile", {}),
        "source_lineage": manifest.get("source_lineage", {}),
        "target_release": manifest.get("target_release", {}),
        "approval": {
            "status": approval_payload["status"],
            "reviewer": approval_payload["reviewer"],
            "reviewed_at": approval_payload["reviewed_at"],
        },
        "files": emitted_files,
        "summary": {
            "added": sum(1 for record in emitted_files if record["action"] == "added"),
            "changed": sum(1 for record in emitted_files if record["action"] == "changed"),
            "removed": sum(1 for record in emitted_files if record["action"] == "removed"),
        },
        "source_id": manifest.get("source_id", ""),
        "mode": args.mode,
        "payload_counts": {
            "documents": sum(1 for record in emitted_files if record["action"] in {"added", "changed"}),
            "views": sum(
                1 for record in emitted_files if record["action"] in {"added", "changed"} and record.get("view_relative_path")
            ),
        },
    }
    diff_summary = {
        "bundle_id": bundle_id,
        "mode": args.mode,
        "normalized_manifest_id": manifest.get("manifest_id", ""),
        "baseline_manifest_id": baseline.get("manifest_id", ""),
        "source_profile": manifest.get("source_profile", {}),
        "source_lineage": manifest.get("source_lineage", {}),
        "target_release": manifest.get("target_release", {}),
        "summary": manifest_payload["summary"],
        "documents": emitted_files,
    }

    shutil.copy2(args.source_manifest, bundle_root / "manifests" / "source-manifest.yaml")
    for optional_config_name in ("source-profiles.yaml", "active-source-profile.yaml"):
        optional_path = args.source_manifest.parent / optional_config_name
        if optional_path.exists():
            shutil.copy2(optional_path, bundle_root / "manifests" / optional_config_name)
    shutil.copy2(args.manifest, bundle_root / "manifests" / "normalized-manifest.json")
    shutil.copy2(args.baseline, bundle_root / "manifests" / "previous-approved-baseline.json")
    write_json(bundle_root / "manifest.json", manifest_payload)
    write_json(bundle_root / "approval.json", approval_payload)
    write_json(bundle_root / "reports" / "diff-summary.json", diff_summary)
    write_checksum_manifest(bundle_root)

    print(
        json.dumps(
            {
                "bundle_id": bundle_id,
                "bundle_path": repo_relative(bundle_root),
                "mode": args.mode,
                "summary": manifest_payload["summary"],
                "approval_status": approval_payload["status"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
