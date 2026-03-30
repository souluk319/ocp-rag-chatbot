from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.stage11_bundle_utils import repo_relative, repo_root, write_json
from deployment.validate_bundle import validate_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and expand a Stage 11 bundle into the staging area.")
    parser.add_argument("bundle", type=Path)
    parser.add_argument(
        "--staging-root",
        type=Path,
        default=repo_root() / "data" / "staging",
    )
    parser.add_argument("--allow-unapproved", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_root = args.bundle.resolve()
    report = validate_bundle(bundle_root, require_approved=not args.allow_unapproved)
    if not report["valid"]:
        raise SystemExit("Bundle validation failed. Refusing to stage.")

    approval_payload = json.loads((bundle_root / "approval.json").read_text(encoding="utf-8"))
    bundle_id = report["bundle_id"]
    staging_path = args.staging_root / bundle_id
    if staging_path.exists():
        if not args.force:
            raise SystemExit(f"Staging path already exists: {staging_path}")
        shutil.rmtree(staging_path)

    staging_path.mkdir(parents=True, exist_ok=True)
    for name in ("documents", "views", "manifests", "reports"):
        source = bundle_root / name
        if source.exists():
            shutil.copytree(source, staging_path / name)
    shutil.copy2(bundle_root / "manifest.json", staging_path / "manifests" / "bundle-manifest.json")
    shutil.copy2(bundle_root / "approval.json", staging_path / "manifests" / "approval.json")
    shutil.copy2(bundle_root / "checksums.sha256", staging_path / "reports" / "checksums.sha256")

    staging_report = {
        "bundle_id": bundle_id,
        "bundle_path": repo_relative(bundle_root),
        "staging_path": repo_relative(staging_path),
        "approval_status": approval_payload.get("status"),
        "approved_for_import": approval_payload.get("approved_for_import"),
        "file_count": report.get("file_count", 0),
        "summary": report.get("summary", {}),
    }
    write_json(staging_path / "reports" / "staging-report.json", staging_report)
    if args.output:
        write_json(args.output, staging_report)
    print(json.dumps(staging_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
