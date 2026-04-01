from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.run_activation_smoke import run_activation_smoke
from deployment.stage11_activation_utils import (
    archive_index_snapshot,
    load_index_manifest,
    read_pointer,
    resolve_index_dir,
    update_index_manifest_state,
    write_pointer,
)
from deployment.stage11_bundle_utils import repo_relative, repo_root, utc_now, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roll back to the previously active Stage 11 index.")
    parser.add_argument("--index-root", type=Path, default=repo_root() / "indexes")
    parser.add_argument("--current-pointer", type=Path, default=repo_root() / "indexes" / "current.txt")
    parser.add_argument("--previous-pointer", type=Path, default=repo_root() / "indexes" / "previous.txt")
    parser.add_argument("--archive-root", type=Path, default=repo_root() / "indexes" / "archive")
    parser.add_argument("--smoke-set", type=Path, default=repo_root() / "deployment" / "activation-smoke-case-ids.json")
    parser.add_argument(
        "--benchmark-cases",
        type=Path,
        default=repo_root() / "eval" / "benchmarks" / "p0_retrieval_benchmark_cases.jsonl",
    )
    parser.add_argument(
        "--operator",
        default="local-operator",
    )
    parser.add_argument("--reuse-existing-data-dir", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current_before = read_pointer(args.current_pointer, default="uninitialized")
    previous_before = read_pointer(args.previous_pointer, default="none")
    if previous_before in {"", "none", "uninitialized"}:
        raise SystemExit("Rollback target is not available in indexes/previous.txt.")

    restore_dir, restore_manifest = load_index_manifest(previous_before, index_root=args.index_root)
    restore_index_id = str(restore_manifest.get("index_id", restore_dir.name))

    archive_path = None
    if current_before not in {"", "none", "uninitialized"}:
        current_index_dir = resolve_index_dir(current_before, index_root=args.index_root)
        if current_index_dir.exists():
            archive_path = archive_index_snapshot(
                current_index_dir,
                archive_root=args.archive_root,
                reason="rollback",
                related_index_id=restore_index_id,
                operator=args.operator,
            )
            update_index_manifest_state(
                current_index_dir,
                state="previous",
                state_note=f"Rolled back from current to {restore_index_id}.",
            )

    current_after = restore_index_id
    previous_after = current_before if current_before not in {"", "uninitialized"} else "none"
    write_pointer(args.current_pointer, current_after)
    write_pointer(args.previous_pointer, previous_after)

    restored_at = utc_now()
    update_index_manifest_state(
        restore_dir,
        state="active",
        state_note="Restored as the current index through rollback.",
        extra_updates={
            "last_rollback_restored_at": restored_at,
            "last_rollback_operator": args.operator,
        },
    )

    smoke_report = run_activation_smoke(
        index_dir=restore_dir,
        index_manifest=restore_manifest,
        smoke_set_path=args.smoke_set,
        benchmark_cases_path=args.benchmark_cases,
        opendocuments_root=repo_root().parent / "ocp-rag-v2" / "OpenDocuments",
        reuse_existing_data_dir=args.reuse_existing_data_dir,
        output_path=restore_dir / "reports" / "post-rollback-smoke-report.json",
    )
    smoke_report["smoke_reason"] = "post-rollback verification"
    smoke_report_path = restore_dir / "reports" / "post-rollback-smoke-report.json"
    write_json(smoke_report_path, smoke_report)

    rollback_report = {
        "rolled_back_at": restored_at,
        "operator": args.operator,
        "restored_index_id": restore_index_id,
        "current_before": current_before,
        "previous_before": previous_before,
        "current_after": current_after,
        "previous_after": previous_after,
        "archive_path": repo_relative(archive_path) if archive_path else None,
        "smoke_report_path": repo_relative(smoke_report_path),
        "smoke_passed": bool(smoke_report.get("overall_passed", smoke_report.get("overall_pass", False))),
    }

    write_json(restore_dir / "reports" / "rollback-report.json", rollback_report)
    if args.output:
        write_json(args.output, rollback_report)

    print(json.dumps(rollback_report, ensure_ascii=False, indent=2))
    return 0 if rollback_report["smoke_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
