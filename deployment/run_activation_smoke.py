from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config
from deployment.run_live_runtime_smoke import start_process, wait_for_json
from deployment.stage11_activation_utils import load_index_manifest, load_jsonl, resolve_index_dir
from deployment.stage11_bundle_utils import load_json, repo_relative, repo_root, utc_now, write_json


def auto_detect_opendocuments_root() -> Path:
    candidate = repo_root().parent / "ocp-rag-v2" / "OpenDocuments"
    return candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stage 11 activation smoke against the real OpenDocuments runtime.")
    parser.add_argument("--index", required=True)
    parser.add_argument("--index-root", type=Path, default=repo_root() / "indexes")
    parser.add_argument("--smoke-set", type=Path, default=repo_root() / "deployment" / "activation-smoke-case-ids.json")
    parser.add_argument(
        "--benchmark-cases",
        type=Path,
        default=repo_root() / "eval" / "benchmarks" / "p0_retrieval_benchmark_cases.jsonl",
    )
    parser.add_argument(
        "--opendocuments-root",
        type=Path,
        default=auto_detect_opendocuments_root(),
    )
    parser.add_argument("--bridge-port", type=int, default=18111)
    parser.add_argument("--startup-timeout-seconds", type=float, default=90.0)
    parser.add_argument("--reuse-existing-data-dir", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _normalize_document_path(document_path: str, source_id: str) -> str:
    normalized = str(document_path or "").replace("\\", "/").strip()
    prefix = f"{source_id}/"
    if normalized.startswith(prefix):
        return normalized[len(prefix) :]
    return normalized


def _normalize_source_dir(document_path: str, source_dir: str, source_id: str) -> str:
    normalized_path = _normalize_document_path(document_path, source_id)
    if "/" in normalized_path:
        return normalized_path.split("/", 1)[0]
    normalized_dir = str(source_dir or "").strip()
    if normalized_dir == source_id:
        return normalized_path
    return normalized_dir


def prepare_smoke_cases(*, smoke_set_path: Path, benchmark_cases_path: Path, output_path: Path) -> list[dict[str, Any]]:
    case_ids = load_json(smoke_set_path).get("case_ids", [])
    available_cases = {case["id"]: case for case in load_jsonl(benchmark_cases_path)}
    selected_cases: list[dict[str, Any]] = []
    for case_id in case_ids:
        case = available_cases.get(case_id)
        if case is None:
            raise SystemExit(f"Smoke case id is missing from benchmark set: {case_id}")
        selected_cases.append(case)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(case, ensure_ascii=False) for case in selected_cases]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return selected_cases


def execute_runtime_smoke(
    *,
    smoke_workspace: Path,
    smoke_data_dir: Path,
    index_dir: Path,
    index_manifest: dict[str, Any],
    opendocuments_root: Path,
    smoke_cases_path: Path,
    smoke_results_path: Path,
    sample_out_path: Path,
    failures_out_path: Path,
    reuse_existing_data_dir: bool,
) -> None:
    if not opendocuments_root.exists():
        raise SystemExit(f"OpenDocuments root does not exist: {opendocuments_root}")

    stage6_runner = repo_root() / "eval" / "run_opendocuments_stage6.mjs"
    if not stage6_runner.exists():
        raise SystemExit(f"Missing Stage 6 runner: {stage6_runner}")

    staging_path = repo_root() / str(index_manifest.get("staging_path", "")).replace("/", "\\")
    staged_manifest_path = repo_root() / str(index_manifest.get("staged_manifest_path", "")).replace("/", "\\")
    if not staged_manifest_path.exists():
        raise SystemExit(f"Staged manifest is missing: {staged_manifest_path}")

    smoke_workspace.mkdir(parents=True, exist_ok=True)
    smoke_results_path.parent.mkdir(parents=True, exist_ok=True)
    sample_out_path.parent.mkdir(parents=True, exist_ok=True)
    failures_out_path.parent.mkdir(parents=True, exist_ok=True)

    first_case = load_jsonl(smoke_cases_path)[0]
    sample_query = str(first_case.get("question_ko", "")).strip()

    command = [
        shutil.which("npx.cmd") or shutil.which("npx") or "npx",
        "-p",
        "node@20",
        "node",
        str(stage6_runner),
        "--workspace",
        str(smoke_workspace),
        "--cases",
        str(smoke_cases_path),
        "--output",
        str(smoke_results_path),
        "--opendocuments-root",
        str(opendocuments_root),
        "--html-root",
        str(staging_path / "views"),
        "--manifest",
        str(staged_manifest_path),
        "--data-dir",
        str(smoke_data_dir),
        "--failures-out",
        str(failures_out_path),
        "--sample-query",
        sample_query,
        "--sample-out",
        str(sample_out_path),
        "--retrieval-only",
    ]
    if reuse_existing_data_dir and smoke_data_dir.exists():
        command.append("--skip-ingest")
    else:
        command.append("--reset-data-dir")
    env = os.environ.copy()
    subprocess.run(command, cwd=repo_root(), env=env, check=True)


def build_runtime_smoke_report(
    *,
    index_dir: Path,
    index_manifest: dict[str, Any],
    smoke_cases_path: Path,
    smoke_results_path: Path,
    sample_out_path: Path,
    failures_out_path: Path,
) -> dict[str, Any]:
    smoke_cases = load_jsonl(smoke_cases_path)
    smoke_results = {record["benchmark_case_id"]: record for record in load_jsonl(smoke_results_path)}
    failures = load_json(failures_out_path) if failures_out_path.exists() else []
    source_id = str(index_manifest.get("source_id", "")).strip()

    case_reports: list[dict[str, Any]] = []
    grounded_pass = True
    click_through_pass = True
    citation_presence_pass = True
    source_dir_pass = True
    supporting_doc_pass = True

    for case in smoke_cases:
        result = smoke_results.get(case["id"])
        if result is None:
            case_reports.append(
                {
                    "case_id": case["id"],
                    "passed": False,
                    "error": "Missing smoke result record.",
                }
            )
            grounded_pass = False
            click_through_pass = False
            citation_presence_pass = False
            source_dir_pass = False
            supporting_doc_pass = False
            continue

        expected_source_dirs = set(case.get("expected_source_dirs", []))
        expected_document_paths = set(case.get("expected_document_paths", []))
        normalized_candidates = []
        for candidate in result.get("reranked_candidates", []):
            normalized_path = _normalize_document_path(candidate.get("document_path", ""), source_id)
            normalized_candidates.append(
                {
                    "rank": candidate.get("rank"),
                    "source_dir": _normalize_source_dir(candidate.get("document_path", ""), candidate.get("source_dir", ""), source_id),
                    "document_path": normalized_path,
                    "viewer_url": candidate.get("viewer_url", ""),
                }
            )
        normalized_citations = []
        for citation in result.get("citations", []):
            normalized_path = _normalize_document_path(citation.get("document_path", ""), source_id)
            normalized_citations.append(
                {
                    "document_path": normalized_path,
                    "viewer_url": citation.get("viewer_url", ""),
                    "section_title": citation.get("section_title", ""),
                }
            )

        top5 = normalized_candidates[:5]
        top10 = normalized_candidates[:10]
        source_dir_hit_top5 = any(candidate["source_dir"] in expected_source_dirs for candidate in top5)
        supporting_doc_hit_top10 = any(candidate["document_path"] in expected_document_paths for candidate in top10)
        citation_presence = bool(normalized_citations)
        citation_expected_hit = any(citation["document_path"] in expected_document_paths for citation in normalized_citations)
        click_through_ok = bool(result.get("click_through_ok", False)) and all(
            Path(str(citation.get("viewer_url", ""))).exists() for citation in normalized_citations
        )
        grounded_answer = bool(result.get("grounded_answer", False))

        case_runtime_pass = all(
            (
                grounded_answer,
                click_through_ok,
                citation_presence,
            )
        )
        case_retrieval_alignment_pass = all(
            (
                source_dir_hit_top5,
                supporting_doc_hit_top10,
                citation_expected_hit,
            )
        )

        grounded_pass = grounded_pass and grounded_answer
        click_through_pass = click_through_pass and click_through_ok
        citation_presence_pass = citation_presence_pass and citation_presence
        source_dir_pass = source_dir_pass and source_dir_hit_top5
        supporting_doc_pass = supporting_doc_pass and supporting_doc_hit_top10

        case_reports.append(
            {
                "case_id": case["id"],
                "question_ko": case.get("question_ko", ""),
                "expected_source_dirs": sorted(expected_source_dirs),
                "expected_document_paths": sorted(expected_document_paths),
                "grounded_answer": grounded_answer,
                "click_through_ok": click_through_ok,
                "citation_presence": citation_presence,
                "source_dir_hit_top5": source_dir_hit_top5,
                "supporting_doc_hit_top10": supporting_doc_hit_top10,
                "citation_expected_hit": citation_expected_hit,
                "top_candidates": top5,
                "citations": normalized_citations,
                "runtime_pass": case_runtime_pass,
                "retrieval_alignment_pass": case_retrieval_alignment_pass,
                "passed": case_runtime_pass,
            }
        )

    observed_case_count = len(smoke_results)
    smoke_case_count = len(smoke_cases)
    complete_case_set = observed_case_count == smoke_case_count
    failures_empty = isinstance(failures, list) and not failures
    runtime_smoke_pass = all(
        (
            complete_case_set,
            grounded_pass,
            click_through_pass,
            citation_presence_pass,
            failures_empty,
        )
    )
    retrieval_alignment_pass = source_dir_pass and supporting_doc_pass

    return {
        "bundle_id": index_manifest.get("bundle_id", index_dir.name),
        "index_id": index_manifest.get("index_id", index_dir.name),
        "staging_path": index_manifest.get("staging_path", ""),
        "workspace_path": repo_relative(repo_root() / "workspace" / "stage11" / index_dir.name),
        "index_path": repo_relative(index_dir),
        "staged_manifest_path": index_manifest.get("staged_manifest_path", ""),
        "smoke_cases_path": repo_relative(smoke_cases_path),
        "smoke_results_path": repo_relative(smoke_results_path),
        "sample_out_path": repo_relative(sample_out_path),
        "failures_out_path": repo_relative(failures_out_path),
        "smoke_case_count": smoke_case_count,
        "observed_case_count": observed_case_count,
        "complete_case_set": complete_case_set,
        "grounded_pass": grounded_pass,
        "click_through_pass": click_through_pass,
        "citation_presence_pass": citation_presence_pass,
        "source_dir_pass": source_dir_pass,
        "supporting_doc_pass": supporting_doc_pass,
        "ingest_failures_empty": failures_empty,
        "runtime_smoke_pass": runtime_smoke_pass,
        "retrieval_alignment_pass": retrieval_alignment_pass,
        "failed_case_ids": [case["case_id"] for case in case_reports if not case.get("runtime_pass")],
        "retrieval_alignment_failed_case_ids": [
            case["case_id"] for case in case_reports if not case.get("retrieval_alignment_pass")
        ],
        "overall_pass": runtime_smoke_pass,
        "generated_at": utc_now(),
        "cases": case_reports,
    }


def run_activation_smoke(
    *,
    index_dir: Path,
    index_manifest: dict[str, Any],
    smoke_set_path: Path,
    benchmark_cases_path: Path,
    opendocuments_root: Path,
    bridge_port: int = 18111,
    startup_timeout_seconds: float = 90.0,
    reuse_existing_data_dir: bool = False,
    output_path: Path | None = None,
) -> dict[str, Any]:
    staging_path = repo_root() / str(index_manifest.get("staging_path", "")).replace("/", "\\")
    if not staging_path.exists():
        raise SystemExit(f"Staging path does not exist: {staging_path}")

    smoke_cases_path = staging_path / "reports" / "activation-smoke-cases.jsonl"
    smoke_results_path = index_dir / "smoke-results.jsonl"
    sample_out_path = index_dir / "sample-query.json"
    failures_out_path = index_dir / "ingest-failures.json"
    smoke_workspace = index_dir / ".activation-smoke-workspace"
    smoke_data_dir = index_dir / ".activation-smoke-data"
    bridge_base_url = f"http://127.0.0.1:{bridge_port}"
    runtime_config = load_runtime_config()
    missing = runtime_config.missing_required_keys()
    if missing:
        raise SystemExit(f"Runtime config is incomplete for activation smoke: {missing}")

    prepare_smoke_cases(
        smoke_set_path=smoke_set_path,
        benchmark_cases_path=benchmark_cases_path,
        output_path=smoke_cases_path,
    )
    if smoke_workspace.exists():
        shutil.rmtree(smoke_workspace, ignore_errors=True)
    if smoke_data_dir.exists() and not reuse_existing_data_dir:
        shutil.rmtree(smoke_data_dir, ignore_errors=True)
    bridge_log_path = index_dir / "reports" / "activation-smoke-bridge.log"
    bridge_env = os.environ.copy()
    bridge_env["PYTHONIOENCODING"] = "utf-8"
    bridge_env["OD_EMBEDDING_DIMENSIONS"] = str(runtime_config.embedding_dimensions)
    # Activation smoke prioritizes retrieval/citation validation, so allow
    # the explicit local chat fallback when company chat auth is unavailable.
    bridge_env["OD_ALLOW_LOCAL_CHAT_FALLBACK"] = "1"
    bridge = start_process(
        name="activation-smoke-bridge",
        command=[
            sys.executable,
            "-m",
            "uvicorn",
            "app.opendocuments_openai_bridge:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(bridge_port),
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
        )
    }
    try:
        wait_for_json(
            f"{bridge_base_url}/health",
            timeout_seconds=startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ok") is True,
        )
        wait_for_json(
            f"{bridge_base_url}/ready",
            timeout_seconds=startup_timeout_seconds,
            predicate=lambda payload: isinstance(payload, dict) and payload.get("ready") is True,
        )
        os.environ["OPENAI_BASE_URL"] = f"{bridge_base_url}/v1"
        os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "stage11-local")
        os.environ["OD_CHAT_MODEL"] = runtime_config.chat_model
        os.environ["OD_EMBEDDING_MODEL"] = runtime_config.embedding_model
        os.environ["OD_EMBEDDING_DIMENSIONS"] = str(runtime_config.embedding_dimensions)
        execute_runtime_smoke(
            smoke_workspace=smoke_workspace,
            smoke_data_dir=smoke_data_dir,
            index_dir=index_dir,
            index_manifest=index_manifest,
            opendocuments_root=opendocuments_root,
            smoke_cases_path=smoke_cases_path,
            smoke_results_path=smoke_results_path,
            sample_out_path=sample_out_path,
            failures_out_path=failures_out_path,
            reuse_existing_data_dir=reuse_existing_data_dir,
        )
    finally:
        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        bridge.terminate()
    final_output_path = output_path or (index_dir / "reports" / "activation-smoke-report.json")
    report = build_runtime_smoke_report(
        index_dir=index_dir,
        index_manifest=index_manifest,
        smoke_cases_path=smoke_cases_path,
        smoke_results_path=smoke_results_path,
        sample_out_path=sample_out_path,
        failures_out_path=failures_out_path,
    )
    write_json(final_output_path, report)
    write_json(index_dir / "reports" / "activation-smoke-report.json", report)
    return report


def main() -> int:
    args = parse_args()
    index_dir, index_manifest = load_index_manifest(args.index, index_root=args.index_root)
    report = run_activation_smoke(
        index_dir=index_dir,
        index_manifest=index_manifest,
        smoke_set_path=args.smoke_set,
        benchmark_cases_path=args.benchmark_cases,
        opendocuments_root=args.opendocuments_root.resolve(),
        bridge_port=args.bridge_port,
        startup_timeout_seconds=args.startup_timeout_seconds,
        reuse_existing_data_dir=args.reuse_existing_data_dir,
        output_path=args.output or (index_dir / "reports" / "activation-smoke-report.json"),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
