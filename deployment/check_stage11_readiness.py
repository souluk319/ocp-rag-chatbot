from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config


def repo_root() -> Path:
    return REPO_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository-side readiness before activating Stage 11.")
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
    parser.add_argument(
        "--smoke-cases",
        type=Path,
        default=repo_root() / "deployment" / "activation-smoke-case-ids.json",
    )
    parser.add_argument(
        "--benchmark-cases",
        type=Path,
        default=repo_root() / "eval" / "benchmarks" / "p0_retrieval_benchmark_cases.jsonl",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        ids.add(str(json.loads(line).get("id", "")))
    return ids


def append_check(
    checks: list[dict[str, Any]],
    *,
    name: str,
    ok: bool,
    blocking: bool,
    detail: str,
) -> None:
    checks.append(
        {
            "name": name,
            "ok": ok,
            "blocking": blocking,
            "detail": detail,
        }
    )


def main() -> int:
    args = parse_args()
    checks: list[dict[str, Any]] = []

    if not args.manifest.exists():
        append_check(
            checks,
            name="normalized_manifest",
            ok=False,
            blocking=True,
            detail=f"missing {args.manifest}",
        )
        append_check(
            checks,
            name="viewer_urls",
            ok=False,
            blocking=True,
            detail="manifest unavailable",
        )
    else:
        manifest = load_json(args.manifest)
        documents = manifest.get("documents", manifest)
        append_check(
            checks,
            name="normalized_manifest",
            ok=bool(documents),
            blocking=True,
            detail=f"document_count={len(documents)}",
        )
        missing_viewers = [
            document.get("document_id", "")
            for document in documents
            if not document.get("viewer_url")
        ]
        append_check(
            checks,
            name="viewer_urls",
            ok=not missing_viewers,
            blocking=True,
            detail=f"missing_viewer_count={len(missing_viewers)}",
        )

    if not args.suite_report.exists():
        append_check(
            checks,
            name="stage10_gate",
            ok=False,
            blocking=True,
            detail=f"missing {args.suite_report}",
        )
    else:
        suite_report = load_json(args.suite_report)
        overall = str(suite_report.get("overall_decision", "")).strip().lower()
        append_check(
            checks,
            name="stage10_gate",
            ok=overall == "go",
            blocking=True,
            detail=f"overall_decision={overall or 'missing'}",
        )

    normalized_root = repo_root() / "data" / "normalized" / "openshift-docs-p0"
    append_check(
        checks,
        name="normalized_corpus_root",
        ok=normalized_root.exists(),
        blocking=True,
        detail=str(normalized_root.relative_to(repo_root())),
    )

    views_root = repo_root() / "data" / "views" / "openshift-docs-p0"
    append_check(
        checks,
        name="html_view_root",
        ok=views_root.exists(),
        blocking=True,
        detail=str(views_root.relative_to(repo_root())),
    )

    runtime_config = load_runtime_config()
    missing_runtime_keys = runtime_config.missing_required_keys()
    append_check(
        checks,
        name="runtime_contract",
        ok=not missing_runtime_keys,
        blocking=True,
        detail=(
            "runtime_mode="
            f"{runtime_config.runtime_mode()}, missing={','.join(missing_runtime_keys) or 'none'}"
        ),
    )

    for path_name in ("outbound", "inbound", "approved", "archive"):
        package_dir = repo_root() / "data" / "packages" / path_name
        append_check(
            checks,
            name=f"package_dir_{path_name}",
            ok=package_dir.exists(),
            blocking=True,
            detail=str(package_dir.relative_to(repo_root())),
        )

    staging_dir = repo_root() / "data" / "staging"
    append_check(
        checks,
        name="staging_dir",
        ok=staging_dir.exists(),
        blocking=True,
        detail=str(staging_dir.relative_to(repo_root())),
    )

    if not args.smoke_cases.exists():
        append_check(
            checks,
            name="activation_smoke_cases",
            ok=False,
            blocking=True,
            detail=f"missing {args.smoke_cases}",
        )
    elif not args.benchmark_cases.exists():
        append_check(
            checks,
            name="activation_smoke_cases",
            ok=False,
            blocking=True,
            detail=f"missing {args.benchmark_cases}",
        )
    else:
        smoke_payload = load_json(args.smoke_cases)
        case_ids = [str(item) for item in smoke_payload.get("case_ids", []) if str(item).strip()]
        benchmark_ids = load_jsonl_ids(args.benchmark_cases)
        missing_case_ids = [case_id for case_id in case_ids if case_id not in benchmark_ids]
        append_check(
            checks,
            name="activation_smoke_cases",
            ok=bool(case_ids) and not missing_case_ids,
            blocking=True,
            detail=(
                f"case_count={len(case_ids)}, "
                f"missing_ids={','.join(missing_case_ids) if missing_case_ids else 'none'}"
            ),
        )

    if not args.baseline.exists():
        append_check(
            checks,
            name="approved_baseline_record",
            ok=False,
            blocking=True,
            detail=f"missing {args.baseline}",
        )
    else:
        baseline = load_json(args.baseline)
        manifest_id = str(baseline.get("manifest_id", "")).strip()
        approved_at = baseline.get("approved_at")
        detail = f"manifest_id={manifest_id or 'missing'}, approved_at={approved_at}"
        append_check(
            checks,
            name="approved_baseline_record",
            ok=bool(manifest_id),
            blocking=True,
            detail=detail,
        )
        append_check(
            checks,
            name="approved_baseline_initialized",
            ok=manifest_id not in {"", "baseline-uninitialized"} and approved_at is not None,
            blocking=False,
            detail=detail,
        )

    if not args.index_pointer.exists():
        append_check(
            checks,
            name="index_pointer_file",
            ok=False,
            blocking=True,
            detail=f"missing {args.index_pointer}",
        )
    else:
        current_pointer = args.index_pointer.read_text(encoding="utf-8").strip()
        append_check(
            checks,
            name="index_pointer_file",
            ok=bool(current_pointer),
            blocking=True,
            detail=f"current_pointer={current_pointer or 'blank'}",
        )
        append_check(
            checks,
            name="index_pointer_initialized",
            ok=current_pointer not in {"", "uninitialized"},
            blocking=False,
            detail=f"current_pointer={current_pointer or 'blank'}",
        )

    previous_pointer = repo_root() / "indexes" / "previous.txt"
    append_check(
        checks,
        name="previous_index_pointer",
        ok=previous_pointer.exists(),
        blocking=True,
        detail=str(previous_pointer.relative_to(repo_root())),
    )

    for relative_dir in ("indexes/archive", "indexes/failed"):
        target_dir = repo_root() / relative_dir
        append_check(
            checks,
            name=f"dir_{target_dir.name}",
            ok=target_dir.exists(),
            blocking=True,
            detail=relative_dir,
        )

    for relative_path in (
        "deployment/airgap-flow.md",
        "deployment/bundle-schema.yaml",
        "deployment/approval-record-schema.yaml",
        "deployment/bundle-layout-contract.md",
        "deployment/manifest-lineage-contract.md",
        "deployment/index-activation-contract.md",
        "deployment/operator-runbook-stage11.md",
        "deployment/stage11-readiness.md",
    ):
        artifact = repo_root() / relative_path
        append_check(
            checks,
            name=f"artifact_{artifact.stem}",
            ok=artifact.exists(),
            blocking=True,
            detail=relative_path,
        )

    blocking_failures = [check for check in checks if check["blocking"] and not check["ok"]]
    warnings = [check for check in checks if not check["blocking"] and not check["ok"]]

    report = {
        "ready_for_stage11": not blocking_failures,
        "blocking_failure_count": len(blocking_failures),
        "warning_count": len(warnings),
        "blocking_failures": blocking_failures,
        "warnings": warnings,
        "checks": checks,
    }

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 1 if blocking_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
