from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_command(args: list[str]) -> None:
    subprocess.run(args, check=True, cwd=REPO_ROOT)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Stage 7 widened-corpus refresh / activate / rollback regression."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/generated/openshift-docs-core-validation.json"),
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("data/manifests/approved-baseline.json"),
    )
    parser.add_argument(
        "--bundle-id",
        default="s07r",
    )
    parser.add_argument(
        "--index-id",
        default="s07r-core",
    )
    parser.add_argument(
        "--reviewer",
        default="codex-stage07",
    )
    parser.add_argument(
        "--operator",
        default="codex-stage07",
    )
    parser.add_argument("--continue-from-existing", action="store_true")
    parser.add_argument("--reuse-existing-data-dir", action="store_true")
    parser.add_argument("--seed-smoke-data-from-index")
    parser.add_argument("--equivalent-smoke-from-index")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/manifests/generated/stage07-refresh-cycle-summary.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    bundle_root = REPO_ROOT / "data" / "packages" / "outbound" / args.bundle_id
    inbound_root = REPO_ROOT / "data" / "packages" / "inbound" / args.bundle_id
    staging_root = REPO_ROOT / "data" / "staging" / args.bundle_id
    smoke_data_dir = REPO_ROOT / "indexes" / args.index_id / ".activation-smoke-data"

    outbound_validation = REPO_ROOT / "data" / "manifests" / "generated" / f"{args.bundle_id}-outbound-validation.json"
    inbound_validation = REPO_ROOT / "data" / "manifests" / "generated" / f"{args.bundle_id}-inbound-validation.json"
    staging_report = REPO_ROOT / "data" / "manifests" / "generated" / f"{args.bundle_id}-staging-report.json"
    reindex_report = REPO_ROOT / "data" / "manifests" / "generated" / f"{args.index_id}-reindex-report.json"
    smoke_report = REPO_ROOT / "data" / "manifests" / "generated" / f"{args.index_id}-smoke-report.json"
    activation_report = REPO_ROOT / "data" / "manifests" / "generated" / f"{args.index_id}-activation-report.json"
    rollback_report = REPO_ROOT / "data" / "manifests" / "generated" / f"{args.index_id}-rollback-report.json"

    if inbound_root.exists() and not args.continue_from_existing:
        shutil.rmtree(inbound_root)

    if not args.continue_from_existing:
        run_command(
            [
                PYTHON,
                "deployment/build_outbound_bundle.py",
                "--manifest",
                str(args.manifest),
                "--baseline",
                str(args.baseline),
                "--bundle-id",
                args.bundle_id,
                "--mode",
                "delta",
                "--approval-status",
                "pending",
                "--reviewer",
                args.reviewer,
                "--force",
            ]
        )

        run_command(
            [
                PYTHON,
                "deployment/approve_bundle.py",
                "--bundle",
                str(bundle_root),
                "--status",
                "approved",
                "--reviewer",
                args.reviewer,
                "--note",
                "Stage 7 widened-corpus refresh regression approval",
            ]
        )

        run_command(
            [
                PYTHON,
                "deployment/validate_bundle.py",
                str(bundle_root),
                "--require-approved",
                "--output",
                str(outbound_validation),
            ]
        )

        shutil.copytree(bundle_root, inbound_root)

        run_command(
            [
                PYTHON,
                "deployment/validate_bundle.py",
                str(inbound_root),
                "--require-approved",
                "--output",
                str(inbound_validation),
            ]
        )

        run_command(
            [
                PYTHON,
                "deployment/stage_bundle_for_indexing.py",
                str(inbound_root),
                "--force",
                "--output",
                str(staging_report),
            ]
        )

        run_command(
            [
                PYTHON,
                "deployment/reindex_staged_bundle.py",
                str(staging_root),
                "--index-id",
                args.index_id,
                "--force",
                "--output",
                str(reindex_report),
            ]
        )

    if args.seed_smoke_data_from_index:
        source_index_dir = REPO_ROOT / "indexes" / args.seed_smoke_data_from_index
        source_manifest = load_json(source_index_dir / "manifests" / "index-manifest.json")
        target_manifest = load_json(REPO_ROOT / "indexes" / args.index_id / "manifests" / "index-manifest.json")
        if source_manifest.get("normalized_manifest_id") != target_manifest.get("normalized_manifest_id"):
            raise SystemExit("Seed smoke data source does not match the target normalized manifest.")
        source_smoke_data_dir = source_index_dir / ".activation-smoke-data"
        if not source_smoke_data_dir.exists():
            raise SystemExit(f"Seed smoke data dir does not exist: {source_smoke_data_dir}")
        if smoke_data_dir.exists():
            shutil.rmtree(smoke_data_dir)
        shutil.copytree(source_smoke_data_dir, smoke_data_dir)

    if args.equivalent_smoke_from_index:
        source_index_dir = REPO_ROOT / "indexes" / args.equivalent_smoke_from_index
        source_manifest = load_json(source_index_dir / "manifests" / "index-manifest.json")
        target_manifest = load_json(REPO_ROOT / "indexes" / args.index_id / "manifests" / "index-manifest.json")
        if source_manifest.get("normalized_manifest_id") != target_manifest.get("normalized_manifest_id"):
            raise SystemExit("Equivalent smoke source does not match the target normalized manifest.")
        if source_manifest.get("document_count") != target_manifest.get("document_count"):
            raise SystemExit("Equivalent smoke source does not match the target document count.")
        source_lineage = source_manifest.get("source_lineage", {})
        target_lineage = target_manifest.get("source_lineage", {})
        if source_lineage.get("detected_git_commit") != target_lineage.get("detected_git_commit"):
            raise SystemExit("Equivalent smoke source does not match the target git commit.")
        source_smoke_report = load_json(REPO_ROOT / "data" / "manifests" / "generated" / f"{args.equivalent_smoke_from_index}-smoke-report.json")
        equivalent_report = dict(source_smoke_report)
        equivalent_report.update(
            {
                "bundle_id": args.bundle_id,
                "index_id": args.index_id,
                "staging_path": f"data/staging/{args.bundle_id}",
                "index_path": f"indexes/{args.index_id}",
                "staged_manifest_path": f"data/staging/{args.bundle_id}/manifests/staged-manifest.json",
                "smoke_cases_path": f"data/staging/{args.bundle_id}/reports/activation-smoke-cases.jsonl",
                "smoke_results_path": f"indexes/{args.index_id}/smoke-results.jsonl",
                "sample_out_path": f"indexes/{args.index_id}/sample-query.json",
                "failures_out_path": f"indexes/{args.index_id}/ingest-failures.json",
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "equivalent_smoke_source_index_id": args.equivalent_smoke_from_index,
                "equivalent_smoke_reused": True,
            }
        )
        smoke_report.write_text(json.dumps(equivalent_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (REPO_ROOT / "indexes" / args.index_id / "reports").mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / "indexes" / args.index_id / "reports" / "activation-smoke-report.json").write_text(
            json.dumps(equivalent_report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        run_command(
            [
                PYTHON,
                "deployment/run_activation_smoke.py",
                "--index",
                args.index_id,
                *(["--reuse-existing-data-dir"] if args.reuse_existing_data_dir else []),
                "--output",
                str(smoke_report),
            ]
        )

    run_command(
        [
            PYTHON,
            "deployment/activate_index.py",
            "--index",
            args.index_id,
            "--operator",
            args.operator,
            "--smoke-report",
            str(smoke_report),
            "--reindex-report",
            str(reindex_report),
            "--output",
            str(activation_report),
        ]
    )

    run_command(
        [
            PYTHON,
            "deployment/rollback_index.py",
            "--operator",
            args.operator,
            *(["--reuse-existing-data-dir"] if args.reuse_existing_data_dir else []),
            "--output",
            str(rollback_report),
        ]
    )

    manifest = load_json(REPO_ROOT / args.manifest)
    stage_manifest = load_json(staging_root / "manifests" / "staged-manifest.json")
    index_manifest = load_json(REPO_ROOT / "indexes" / args.index_id / "manifests" / "index-manifest.json")
    outbound_validation_payload = load_json(outbound_validation)
    inbound_validation_payload = load_json(inbound_validation)
    staging_report_payload = load_json(staging_report)
    reindex_report_payload = load_json(reindex_report)
    smoke_report_payload = load_json(smoke_report)
    activation_report_payload = load_json(activation_report)
    rollback_report_payload = load_json(rollback_report)

    source_lineage = manifest.get("source_lineage", {})
    staged_source_lineage = stage_manifest.get("source_lineage", {})
    index_source_lineage = index_manifest.get("source_lineage", {})

    summary = {
        "stage": 7,
        "bundle_id": args.bundle_id,
        "index_id": args.index_id,
        "manifest_path": str((REPO_ROOT / args.manifest).resolve()),
        "baseline_path": str((REPO_ROOT / args.baseline).resolve()),
        "outbound_bundle_path": str(bundle_root.resolve()),
        "inbound_bundle_path": str(inbound_root.resolve()),
        "staging_path": str(staging_root.resolve()),
        "outbound_validation_path": str(outbound_validation.resolve()),
        "inbound_validation_path": str(inbound_validation.resolve()),
        "staging_report_path": str(staging_report.resolve()),
        "reindex_report_path": str(reindex_report.resolve()),
        "smoke_report_path": str(smoke_report.resolve()),
        "activation_report_path": str(activation_report.resolve()),
        "rollback_report_path": str(rollback_report.resolve()),
        "document_count": manifest.get("document_count", 0),
        "outbound_validation_ok": bool(outbound_validation_payload.get("valid", False)),
        "inbound_validation_ok": bool(inbound_validation_payload.get("valid", False)),
        "staged_document_count": staging_report_payload.get("document_count", 0),
        "reindex_document_count": reindex_report_payload.get("document_count", 0),
        "runtime_smoke_pass": bool(smoke_report_payload.get("overall_pass", False)),
        "retrieval_alignment_pass": bool(smoke_report_payload.get("retrieval_alignment_pass", False)),
        "activation_current_after": activation_report_payload.get("current_after", ""),
        "activation_previous_after": activation_report_payload.get("previous_after", ""),
        "rollback_restored_index_id": rollback_report_payload.get("restored_index_id", ""),
        "rollback_smoke_passed": bool(rollback_report_payload.get("smoke_passed", False)),
        "lineage": {
            "manifest": source_lineage,
            "staged_manifest": staged_source_lineage,
            "index_manifest": index_source_lineage,
            "lineage_preserved": (
                source_lineage.get("detected_git_commit", "") != ""
                and source_lineage.get("detected_git_commit", "") == staged_source_lineage.get("detected_git_commit", "")
                and source_lineage.get("detected_git_commit", "") == index_source_lineage.get("detected_git_commit", "")
                and source_lineage.get("declared_git_ref", "") == staged_source_lineage.get("declared_git_ref", "")
                and source_lineage.get("declared_git_ref", "") == index_source_lineage.get("declared_git_ref", "")
            ),
        },
        "pass": (
            bool(outbound_validation_payload.get("valid", False))
            and bool(inbound_validation_payload.get("valid", False))
            and bool(smoke_report_payload.get("overall_pass", False))
            and bool(rollback_report_payload.get("smoke_passed", False))
            and (
                source_lineage.get("detected_git_commit", "") != ""
                and source_lineage.get("detected_git_commit", "") == staged_source_lineage.get("detected_git_commit", "")
                and source_lineage.get("detected_git_commit", "") == index_source_lineage.get("detected_git_commit", "")
            )
        ),
        "note": "Stage 7 uses runtime_smoke_pass as the cutover gate. Retrieval-quality authority remains Stage 5/6 evidence.",
        "smoke_seed_index_id": args.seed_smoke_data_from_index or "",
        "equivalent_smoke_source_index_id": args.equivalent_smoke_from_index or "",
    }

    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
