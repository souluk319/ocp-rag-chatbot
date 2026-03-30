from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from deployment.stage11_bundle_utils import current_manifest_documents, load_json, repo_relative, write_json


def repo_root() -> Path:
    return REPO_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize the approved baseline record for Stage 11 from the validated manifest and Stage 10 suite."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "generated" / "openshift-docs-p0.json",
    )
    parser.add_argument(
        "--suite-report",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "generated" / "stage10-suite-report.json",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "approved-baseline.json",
    )
    parser.add_argument(
        "--index-pointer",
        type=Path,
        default=REPO_ROOT / "indexes" / "current.txt",
    )
    parser.add_argument("--active-index-id", default="")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def is_placeholder_baseline(payload: dict) -> bool:
    return str(payload.get("manifest_id", "")).strip() in {"", "baseline-uninitialized"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    args = parse_args()
    manifest = load_json(args.manifest)
    manifest_documents = current_manifest_documents(manifest)
    suite_report = load_json(args.suite_report)
    existing = load_json(args.baseline) if args.baseline.exists() else {}

    if suite_report.get("overall_decision") != "go" and not args.force:
        raise SystemExit("Stage 10 suite is not in `go` state. Use --force only if you intentionally want to bypass this.")

    if existing and not is_placeholder_baseline(existing) and not args.force:
        raise SystemExit("Approved baseline is already initialized. Use --force to overwrite it.")

    active_index_id = args.active_index_id.strip()
    baseline_payload = {
        "baseline_id": f"approved-{manifest.get('manifest_id', 'unknown')}",
        "manifest_id": manifest.get("manifest_id", ""),
        "normalized_manifest_path": repo_relative(args.manifest),
        "source_id": manifest.get("source_id", ""),
        "approved_at": utc_now(),
        "stage10_overall_decision": suite_report.get("overall_decision", ""),
        "stage10_suite_report": repo_relative(args.suite_report),
        "document_count": manifest.get("document_count", 0),
        "top_level_counts": manifest.get("top_level_counts", {}),
        "category_counts": manifest.get("category_counts", {}),
        "activation_smoke_set": repo_relative(repo_root() / "deployment" / "activation-smoke-case-ids.json"),
        "active_index_id": active_index_id or None,
        "notes": [],
        "documents": manifest_documents,
    }
    if not active_index_id:
        baseline_payload["notes"].append(
            "Seed indexes/current.txt with a real validated local index id before starting Stage 11 activation work."
        )
    write_json(args.baseline, baseline_payload)

    if active_index_id:
        args.index_pointer.parent.mkdir(parents=True, exist_ok=True)
        args.index_pointer.write_text(active_index_id + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "baseline_path": str(args.baseline),
                "manifest_id": baseline_payload["manifest_id"],
                "stage10_overall_decision": baseline_payload["stage10_overall_decision"],
                "active_index_id": baseline_payload["active_index_id"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
