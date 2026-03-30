from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root().resolve()))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize the approved baseline record for Stage 11 from the validated manifest and Stage 10 suite."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "openshift-docs-p0.json",
    )
    parser.add_argument(
        "--suite-report",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "stage10-suite-report.json",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=repo_root() / "data" / "manifests" / "approved-baseline.json",
    )
    parser.add_argument(
        "--index-pointer",
        type=Path,
        default=repo_root() / "indexes" / "current.txt",
    )
    parser.add_argument("--active-index-id", default="")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_placeholder_baseline(payload: dict) -> bool:
    return str(payload.get("manifest_id", "")).strip() in {"", "baseline-uninitialized"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    args = parse_args()
    manifest = load_json(args.manifest)
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
    }
    if not active_index_id:
        baseline_payload["notes"].append(
            "Seed indexes/current.txt with a real validated local index id before starting Stage 11 activation work."
        )

    args.baseline.parent.mkdir(parents=True, exist_ok=True)
    args.baseline.write_text(json.dumps(baseline_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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
