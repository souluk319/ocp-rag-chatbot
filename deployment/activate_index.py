from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.stage11_activation_utils import (
    archive_index_snapshot,
    load_index_manifest,
    read_pointer,
    resolve_index_dir,
    update_index_manifest_state,
    write_pointer,
)
from deployment.stage11_bundle_utils import load_json, repo_relative, repo_root, utc_now, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Activate a Stage 11 index after reindex and smoke validation.")
    parser.add_argument("--index", required=True)
    parser.add_argument("--index-root", type=Path, default=repo_root() / "indexes")
    parser.add_argument("--current-pointer", type=Path, default=repo_root() / "indexes" / "current.txt")
    parser.add_argument("--previous-pointer", type=Path, default=repo_root() / "indexes" / "previous.txt")
    parser.add_argument("--archive-root", type=Path, default=repo_root() / "indexes" / "archive")
    parser.add_argument("--smoke-report", type=Path)
    parser.add_argument("--reindex-report", type=Path)
    parser.add_argument("--operator", default="local-operator")
    parser.add_argument("--bootstrap-current", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index_dir, index_manifest = load_index_manifest(args.index, index_root=args.index_root)
    index_id = str(index_manifest.get("index_id", index_dir.name))

    smoke_report_path = args.smoke_report or (index_dir / "reports" / "activation-smoke-report.json")
    reindex_report_path = args.reindex_report or (index_dir / "reports" / "reindex-report.json")
    if not smoke_report_path.exists():
        raise SystemExit(f"Smoke report is missing: {smoke_report_path}")
    if not reindex_report_path.exists():
        raise SystemExit(f"Reindex report is missing: {reindex_report_path}")

    smoke_report = load_json(smoke_report_path)
    reindex_report = load_json(reindex_report_path)
    smoke_index_id = str(smoke_report.get("index_id") or smoke_report.get("bundle_id") or "").strip()
    if smoke_index_id != index_id:
        raise SystemExit("Smoke report does not belong to the target index.")
    if reindex_report.get("index_id") != index_id:
        raise SystemExit("Reindex report does not belong to the target index.")
    smoke_passed = smoke_report.get("overall_passed")
    if smoke_passed is None:
        smoke_passed = smoke_report.get("overall_pass")
    if not smoke_passed:
        raise SystemExit("Smoke report did not pass; refusing to activate.")
    if not reindex_report.get("valid_for_activation"):
        raise SystemExit("Reindex report is not activation-safe.")

    current_before = read_pointer(args.current_pointer, default="uninitialized")
    previous_before = read_pointer(args.previous_pointer, default="none")
    bootstrap_mode = current_before == "uninitialized"
    if bootstrap_mode and not args.bootstrap_current:
        raise SystemExit("Current pointer is uninitialized. Use --bootstrap-current for the first activation.")

    archive_path = None
    if current_before not in {"", "none", "uninitialized", index_id}:
        current_index_dir = resolve_index_dir(current_before, index_root=args.index_root)
        if current_index_dir.exists():
            archive_path = archive_index_snapshot(
                current_index_dir,
                archive_root=args.archive_root,
                reason="activation",
                related_index_id=index_id,
                operator=args.operator,
            )
            update_index_manifest_state(
                current_index_dir,
                state="previous",
                state_note=f"Superseded by activation of {index_id}.",
            )

    previous_after = "none" if bootstrap_mode else current_before
    write_pointer(args.previous_pointer, previous_after)
    write_pointer(args.current_pointer, index_id)

    activated_at = utc_now()
    update_index_manifest_state(
        index_dir,
        state="active",
        state_note="Activated as the current Stage 11 index.",
        extra_updates={
            "last_activated_at": activated_at,
            "last_activation_operator": args.operator,
        },
    )

    activation_report = {
        "index_id": index_id,
        "activated_at": activated_at,
        "activation_mode": "bootstrap" if bootstrap_mode else "switch",
        "operator": args.operator,
        "current_before": current_before,
        "previous_before": previous_before,
        "current_after": index_id,
        "previous_after": previous_after,
        "smoke_report_path": repo_relative(smoke_report_path),
        "reindex_report_path": repo_relative(reindex_report_path),
        "archive_path": repo_relative(archive_path) if archive_path else None,
        "activation_succeeded": True,
    }

    write_json(index_dir / "reports" / "activation-report.json", activation_report)
    if args.output:
        write_json(args.output, activation_report)

    print(json.dumps(activation_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
