from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from shutil import which


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the enterprise-4.20 Golden Set benchmark and score it.")
    parser.add_argument("--skip-runner", action="store_true")
    parser.add_argument("--workspace", type=Path, default=REPO_ROOT / "indexes" / "golden-set-4.20")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "indexes" / "golden-set-4.20" / ".data")
    parser.add_argument("--results-out", type=Path, default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_results.jsonl")
    parser.add_argument("--report-out", type=Path, default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_report.json")
    parser.add_argument("--failures-out", type=Path, default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_failures.json")
    parser.add_argument("--sample-out", type=Path, default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_sample.json")
    parser.add_argument("--profile", default="precise")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--force-ingest", action="store_true")
    parser.add_argument("--reset-data-dir", action="store_true")
    return parser.parse_args()


def run_command(command: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, check=True, cwd=REPO_ROOT, env=env)


def resolve_node_launcher() -> str:
    if os.name == "nt":
        return which("npx.cmd") or "npx.cmd"
    return which("npx") or "npx"


def main() -> None:
    args = parse_args()
    runtime = load_runtime_config()

    cases_path = REPO_ROOT / "eval" / "benchmarks" / "golden_set_100_cases.jsonl"
    rubric_path = REPO_ROOT / "eval" / "benchmarks" / "golden_set_100_rubric.json"
    manifest_path = REPO_ROOT / "data" / "manifests" / "generated" / "openshift-docs-4.20-balanced.json"
    html_root = REPO_ROOT / "data" / "views" / "openshift-docs-4.20-balanced"
    open_documents_root = REPO_ROOT.parent / "ocp-rag-v2" / "OpenDocuments"

    run_command([sys.executable, str(REPO_ROOT / "eval" / "build_golden_set_assets.py")])

    if not args.skip_runner:
        env = os.environ.copy()
        env["OPENAI_BASE_URL"] = env.get("OPENAI_BASE_URL", "http://127.0.0.1:18101/v1")
        env["OPENAI_API_KEY"] = env.get("OPENAI_API_KEY", "golden-set-local")
        env["OD_CHAT_MODEL"] = runtime.chat_model
        env["OD_EMBEDDING_MODEL"] = runtime.embedding_model
        env["OD_EMBEDDING_DIMENSIONS"] = str(runtime.embedding_dimensions)
        env["OPENDOCUMENTS_CHAT_TIMEOUT_MS"] = env.get("OPENDOCUMENTS_CHAT_TIMEOUT_MS", "300000")
        env["OPENDOCUMENTS_EMBED_TIMEOUT_MS"] = env.get("OPENDOCUMENTS_EMBED_TIMEOUT_MS", "180000")
        env["OPENDOCUMENTS_EMBED_BATCH_SIZE"] = env.get("OPENDOCUMENTS_EMBED_BATCH_SIZE", "8")

        command = [
            resolve_node_launcher(),
            "-p",
            "node@20",
            "node",
            str(REPO_ROOT / "eval" / "run_opendocuments_stage6.mjs"),
            "--workspace",
            str(args.workspace),
            "--cases",
            str(cases_path),
            "--output",
            str(args.results_out),
            "--opendocuments-root",
            str(open_documents_root),
            "--html-root",
            str(html_root),
            "--manifest",
            str(manifest_path),
            "--data-dir",
            str(args.data_dir),
            "--failures-out",
            str(args.failures_out),
            "--sample-query",
            "설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?",
            "--sample-out",
            str(args.sample_out),
            "--profile",
            args.profile,
            "--top",
            str(args.top_k),
        ]
        if args.force_ingest:
            command.append("--force-ingest")
        if args.reset_data_dir:
            command.append("--reset-data-dir")

        run_command(command, env=env)

    run_command(
        [
            sys.executable,
            str(REPO_ROOT / "eval" / "score_golden_set_4_20.py"),
            "--cases",
            str(cases_path),
            "--rubric",
            str(rubric_path),
            "--results",
            str(args.results_out),
            "--output",
            str(args.report_out),
        ]
    )


if __name__ == "__main__":
    main()
