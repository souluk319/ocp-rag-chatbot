from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_paths(paths: list[str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for raw in paths:
        path = REPO_ROOT / raw
        results.append(
            {
                "path": raw,
                "exists": path.exists(),
                "is_dir": path.is_dir(),
                "is_file": path.is_file(),
            }
        )
    return results


def main() -> None:
    core_paths = [
        "README.md",
        "docs/v2/repository-map.md",
        "app/ocp_runtime_gateway.py",
        "app/opendocuments_openai_bridge.py",
        "app/ocp_policy.py",
        "app/multiturn_memory.py",
        "ingest/normalize_openshift_docs.py",
        "configs/source-profiles.yaml",
        "configs/active-source-profile.yaml",
        "deployment/start_runtime_stack.py",
        "deployment/run_live_runtime_smoke.py",
        "eval/run_stage05_regression.py",
        "eval/run_stage06_regression.py",
    ]
    support_paths = [
        "docs/v2/project-plan-summary.md",
        "docs/v2/ten-stage-verification-plan.md",
        "docs/v2/stage08-live-runtime-quality-report.md",
        "docs/v2/stage07-refresh-activate-rollback-report.md",
        "docs/v2/stage06-multiturn-redteam-regression-report.md",
        "docs/v2/stage05-stage9-regression-report.md",
        "deployment/operator-runbook-stage14.md",
        "data/manifests/generated/stage08-live-runtime-report.json",
    ]
    directory_paths = [
        "app",
        "configs",
        "ingest",
        "deployment",
        "eval",
        "docs/v2",
        "data",
        "indexes",
        "workspace",
    ]

    root_entries = sorted(path.name for path in REPO_ROOT.iterdir())
    root_python_files = sorted(path.name for path in REPO_ROOT.glob("*.py"))
    ignored_runtime_files = [".env", "docs/internal", "data/manifests/generated"]

    report = {
        "stage": 9,
        "core_paths": check_paths(core_paths),
        "support_paths": check_paths(support_paths),
        "directories": check_paths(directory_paths),
        "root_entries": root_entries,
        "root_python_files": root_python_files,
        "ignored_runtime_files": ignored_runtime_files,
    }

    report["missing_core_paths"] = [item["path"] for item in report["core_paths"] if not item["exists"]]
    report["missing_support_paths"] = [item["path"] for item in report["support_paths"] if not item["exists"]]
    report["missing_directories"] = [item["path"] for item in report["directories"] if not item["exists"]]
    report["root_python_files_present"] = bool(root_python_files)
    report["pass"] = not (
        report["missing_core_paths"]
        or report["missing_support_paths"]
        or report["missing_directories"]
        or report["root_python_files_present"]
    )

    output_path = REPO_ROOT / "data" / "manifests" / "generated" / "stage09-repository-map-check.json"
    write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
