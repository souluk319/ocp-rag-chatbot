from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.stage11_bundle_utils import load_json, repo_relative, sha256_file, write_json

BUNDLE_REQUIRED = ("bundle_id", "created_at", "source_manifest_version", "baseline_manifest_id", "approval", "files", "summary")
APPROVAL_REQUIRED = (
    "bundle_id",
    "status",
    "reviewer",
    "reviewed_at",
    "source_scope_verified",
    "removal_impact_checked",
    "checksum_verified",
    "approved_for_import",
)
APPROVAL_STATUS_ALLOWED = {"pending", "approved", "rejected"}
FILE_REQUIRED = ("document_id", "relative_path", "checksum", "action", "source_id", "category", "version")
ACTION_ALLOWED = {"added", "changed", "removed"}
SUMMARY_REQUIRED = ("added", "changed", "removed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Stage 11 outbound or inbound bundle.")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--require-approved", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def validate_required(payload: dict[str, Any], required: tuple[str, ...], label: str, errors: list[str]) -> None:
    missing = [field for field in required if field not in payload]
    if missing:
        errors.append(f"{label}: missing required fields: {', '.join(missing)}")


def parse_checksum_file(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        checksum, relative_path = line.split("  ", 1)
        checksums[relative_path] = checksum
    return checksums


def validate_bundle(bundle_root: Path, *, require_approved: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    required_paths = (
        bundle_root / "manifest.json",
        bundle_root / "approval.json",
        bundle_root / "checksums.sha256",
        bundle_root / "manifests" / "source-manifest.yaml",
        bundle_root / "manifests" / "normalized-manifest.json",
        bundle_root / "manifests" / "previous-approved-baseline.json",
        bundle_root / "reports" / "diff-summary.json",
        bundle_root / "documents",
        bundle_root / "views",
    )
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing required path: {repo_relative(path)}")

    manifest = load_json(bundle_root / "manifest.json") if (bundle_root / "manifest.json").exists() else {}
    approval = load_json(bundle_root / "approval.json") if (bundle_root / "approval.json").exists() else {}

    validate_required(manifest, BUNDLE_REQUIRED, "manifest.json", errors)
    validate_required(approval, APPROVAL_REQUIRED, "approval.json", errors)
    if approval.get("status") and approval.get("status") not in APPROVAL_STATUS_ALLOWED:
        errors.append(f"approval.json: unsupported status {approval['status']}")
    if require_approved and (
        approval.get("status") != "approved"
        or not approval.get("approved_for_import")
        or not approval.get("source_scope_verified")
        or not approval.get("removal_impact_checked")
        or not approval.get("checksum_verified")
    ):
        errors.append("bundle is not fully approved for import")

    if manifest.get("bundle_id") and bundle_root.name != manifest.get("bundle_id"):
        errors.append(f"bundle_id mismatch: directory={bundle_root.name}, manifest={manifest.get('bundle_id')}")
    if approval.get("bundle_id") and manifest.get("bundle_id") and approval.get("bundle_id") != manifest.get("bundle_id"):
        errors.append("approval.json bundle_id does not match manifest.json bundle_id")

    if isinstance(manifest.get("summary"), dict):
        validate_required(manifest["summary"], SUMMARY_REQUIRED, "manifest.summary", errors)
    if isinstance(manifest.get("approval"), dict):
        validate_required(manifest["approval"], ("status", "reviewer", "reviewed_at"), "manifest.approval", errors)
        if manifest["approval"].get("status") != approval.get("status"):
            errors.append("manifest.approval.status does not match approval.json status")

    files = manifest.get("files", []) if isinstance(manifest.get("files"), list) else []
    action_counts = {"added": 0, "changed": 0, "removed": 0}
    for entry in files:
        validate_required(entry, FILE_REQUIRED, f"manifest.files[{entry.get('document_id', '?')}]", errors)
        action = entry.get("action")
        if action not in ACTION_ALLOWED:
            errors.append(f"unsupported file action: {action}")
            continue
        action_counts[action] += 1

        payload_path = bundle_root / str(entry.get("relative_path", ""))
        view_relative_path = str(entry.get("view_relative_path", "")).strip()
        view_path = bundle_root / view_relative_path if view_relative_path else None

        if action == "removed":
            if payload_path.exists():
                errors.append(f"removed record still ships payload: {entry.get('relative_path')}")
            if view_path and view_path.exists():
                errors.append(f"removed record still ships view payload: {view_relative_path}")
            continue

        if not payload_path.exists():
            errors.append(f"missing payload for {entry.get('document_id')}: {entry.get('relative_path')}")
        elif sha256_file(payload_path) != entry.get("checksum"):
            errors.append(f"checksum mismatch for {entry.get('relative_path')}")

        if view_relative_path:
            if not view_path or not view_path.exists():
                errors.append(f"missing view payload for {entry.get('document_id')}: {view_relative_path}")
            elif entry.get("view_checksum") and sha256_file(view_path) != entry.get("view_checksum"):
                errors.append(f"view checksum mismatch for {view_relative_path}")
        else:
            warnings.append(f"no view_relative_path for {entry.get('document_id')}")

    manifest_summary = manifest.get("summary", {})
    for action, count in action_counts.items():
        if manifest_summary.get(action) != count:
            errors.append(f"summary.{action}={manifest_summary.get(action)} but counted {count}")

    checksum_file = bundle_root / "checksums.sha256"
    if checksum_file.exists():
        checksum_entries = parse_checksum_file(checksum_file)
        actual_files = {
            path.relative_to(bundle_root).as_posix(): sha256_file(path)
            for path in bundle_root.rglob("*")
            if path.is_file() and path.name != "checksums.sha256"
        }
        missing_checksum_entries = sorted(set(actual_files) - set(checksum_entries))
        unexpected_checksum_entries = sorted(set(checksum_entries) - set(actual_files))
        for relative_path in missing_checksum_entries:
            errors.append(f"checksums.sha256 missing entry: {relative_path}")
        for relative_path in unexpected_checksum_entries:
            errors.append(f"checksums.sha256 references missing file: {relative_path}")
        for relative_path, expected_checksum in actual_files.items():
            if checksum_entries.get(relative_path) != expected_checksum:
                errors.append(f"checksum manifest mismatch: {relative_path}")

    return {
        "bundle_id": manifest.get("bundle_id", bundle_root.name),
        "bundle_path": repo_relative(bundle_root),
        "valid": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "summary": manifest_summary,
        "file_count": len(files),
    }


def main() -> int:
    args = parse_args()
    report = validate_bundle(args.bundle.resolve(), require_approved=args.require_approved)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        write_json(args.output, report)
    print(rendered)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
