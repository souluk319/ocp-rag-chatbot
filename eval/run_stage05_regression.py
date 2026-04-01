from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config
from deployment.run_live_runtime_smoke import start_process, wait_for_json


def repo_root() -> Path:
    return REPO_ROOT


def auto_detect_opendocuments_root() -> Path:
    return repo_root().parent / "ocp-rag-v2" / "OpenDocuments"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run widened corpus Stage 5 retrieval/citation regression.")
    parser.add_argument(
        "--cases",
        type=Path,
        default=repo_root() / "eval" / "benchmarks" / "p0_retrieval_benchmark_cases.jsonl",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root() / "data" / "staging" / "s15c" / "manifests" / "staged-manifest.json",
    )
    parser.add_argument(
        "--html-root",
        type=Path,
        default=repo_root() / "data" / "staging" / "s15c" / "views",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=repo_root() / "indexes" / "s15c-core" / ".stage05-workspace",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=repo_root() / "indexes" / "s15c-core" / ".activation-smoke-data",
    )
    parser.add_argument(
        "--results-out",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "stage05-raw-results.jsonl",
    )
    parser.add_argument(
        "--policy-results-out",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "stage05-policy-results.jsonl",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "stage05-policy-report.json",
    )
    parser.add_argument(
        "--sample-out",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "stage05-sample-query.json",
    )
    parser.add_argument(
        "--failures-out",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "stage05-ingest-failures.json",
    )
    parser.add_argument(
        "--combined-out",
        type=Path,
        default=repo_root() / "data" / "manifests" / "generated" / "stage05-regression-summary.json",
    )
    parser.add_argument(
        "--opendocuments-root",
        type=Path,
        default=auto_detect_opendocuments_root(),
    )
    parser.add_argument("--bridge-port", type=int, default=18112)
    parser.add_argument("--startup-timeout-seconds", type=float, default=90.0)
    parser.add_argument(
        "--reuse-existing-data-dir",
        action="store_true",
        help="Reuse an existing OpenDocuments data dir instead of rebuilding it from scratch.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_stage6_benchmark(args: argparse.Namespace) -> None:
    runtime_config = load_runtime_config()
    missing = runtime_config.missing_required_keys()
    if missing:
        raise SystemExit(f"Runtime config is incomplete for Stage 5 regression: {missing}")

    stage6_runner = repo_root() / "eval" / "run_opendocuments_stage6.mjs"
    if not stage6_runner.exists():
        raise SystemExit(f"Missing Stage 6 runner: {stage6_runner}")
    if not args.opendocuments_root.exists():
        raise SystemExit(f"OpenDocuments root does not exist: {args.opendocuments_root}")

    if args.workspace.exists():
        shutil.rmtree(args.workspace, ignore_errors=True)
    if args.data_dir.exists() and not args.reuse_existing_data_dir:
        shutil.rmtree(args.data_dir, ignore_errors=True)

    bridge_base_url = f"http://127.0.0.1:{args.bridge_port}"
    bridge_log_path = repo_root() / "data" / "manifests" / "generated" / "stage05-bridge.log"
    bridge_env = os.environ.copy()
    bridge_env["PYTHONIOENCODING"] = "utf-8"
    bridge_env["OD_EMBEDDING_DIMENSIONS"] = str(runtime_config.embedding_dimensions)
    bridge = start_process(
        name="stage05-bridge",
        command=[
            sys.executable,
            "-m",
            "uvicorn",
            "app.opendocuments_openai_bridge:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.bridge_port),
        ],
        cwd=repo_root(),
        env=bridge_env,
        log_path=bridge_log_path,
    )

    previous_env = {
        key: os.environ.get(key)
        for key in (
            "OPENAI_BASE_URL",
            "OPENAI_API_KEY",
            "OD_CHAT_MODEL",
            "OD_EMBEDDING_MODEL",
            "OD_EMBEDDING_DIMENSIONS",
            "OD_ALLOW_LOCAL_CHAT_FALLBACK",
        )
    }
    try:
        wait_for_json(
            f"{bridge_base_url}/health",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ok") is True,
        )
        wait_for_json(
            f"{bridge_base_url}/ready",
            timeout_seconds=args.startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ready") is True,
        )

        os.environ["OPENAI_BASE_URL"] = f"{bridge_base_url}/v1"
        os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "stage05-local")
        os.environ["OD_CHAT_MODEL"] = runtime_config.chat_model
        os.environ["OD_EMBEDDING_MODEL"] = runtime_config.embedding_model
        os.environ["OD_EMBEDDING_DIMENSIONS"] = str(runtime_config.embedding_dimensions)
        os.environ["OD_ALLOW_LOCAL_CHAT_FALLBACK"] = "0"

        lines = [line for line in args.cases.read_text(encoding="utf-8").splitlines() if line.strip()]
        first_question = json.loads(lines[0]).get("question_ko", "")

        command = [
            shutil.which("npx.cmd") or shutil.which("npx") or "npx",
            "-p",
            "node@20",
            "node",
            str(stage6_runner),
            "--workspace",
            str(args.workspace),
            "--cases",
            str(args.cases),
            "--output",
            str(args.results_out),
            "--opendocuments-root",
            str(args.opendocuments_root),
            "--html-root",
            str(args.html_root),
            "--manifest",
            str(args.manifest),
            "--data-dir",
            str(args.data_dir),
            "--failures-out",
            str(args.failures_out),
            "--sample-query",
            first_question,
            "--sample-out",
            str(args.sample_out),
            "--retrieval-only",
        ]
        if args.reuse_existing_data_dir:
            command.append("--skip-ingest")
        else:
            command.append("--reset-data-dir")
        subprocess.run(command, cwd=repo_root(), env=os.environ.copy(), check=True)
    finally:
        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        bridge.terminate()


def run_stage9_report(args: argparse.Namespace) -> None:
    command = [
        sys.executable,
        str(repo_root() / "eval" / "stage9_policy_report.py"),
        "--cases",
        str(args.cases),
        "--results",
        str(args.results_out),
        "--manifest",
        str(args.manifest),
        "--output-results",
        str(args.policy_results_out),
        "--output-report",
        str(args.report_out),
    ]
    subprocess.run(command, cwd=repo_root(), check=True)


def build_combined_report(args: argparse.Namespace) -> dict[str, object]:
    report = json.loads(args.report_out.read_text(encoding="utf-8"))
    failures = json.loads(args.failures_out.read_text(encoding="utf-8")) if args.failures_out.exists() else []
    return {
        "stage": 5,
        "cases_path": str(args.cases),
        "manifest_path": str(args.manifest),
        "results_path": str(args.results_out),
        "policy_results_path": str(args.policy_results_out),
        "policy_report_path": str(args.report_out),
        "failures_path": str(args.failures_out),
        "workspace_path": str(args.workspace),
        "data_dir": str(args.data_dir),
        "sample_out_path": str(args.sample_out),
        "raw_summary": report.get("raw_retrieval_summary", {}),
        "policy_summary": report.get("summary", {}),
        "by_query_class": report.get("by_query_class", {}),
        "failure_count": len(failures) if isinstance(failures, list) else None,
        "pass": (
            report.get("summary", {}).get("source_dir_hit@5", 0.0) >= 0.85
            and report.get("summary", {}).get("supporting_doc_hit@10", 0.0) >= 0.75
            and report.get("summary", {}).get("citation_correctness", 0.0) >= 0.90
        ),
    }


def main() -> int:
    args = parse_args()
    run_stage6_benchmark(args)
    run_stage9_report(args)
    combined = build_combined_report(args)
    write_json(args.combined_out, combined)
    print(json.dumps(combined, ensure_ascii=False, indent=2))
    return 0 if combined["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
