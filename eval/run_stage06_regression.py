from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_command(args: list[str]) -> None:
    subprocess.run(args, check=True, cwd=REPO_ROOT)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Stage 6 widened-corpus regression and summarize raw-vs-policy retrieval separately."
    )
    parser.add_argument(
        "--policy-report",
        type=Path,
        default=Path("data/manifests/generated/stage05-policy-report.json"),
    )
    parser.add_argument(
        "--multiturn-scenarios",
        type=Path,
        default=Path("eval/benchmarks/p0_multiturn_scenarios.json"),
    )
    parser.add_argument(
        "--red-team-cases",
        type=Path,
        default=Path("eval/benchmarks/p0_red_team_cases.jsonl"),
    )
    parser.add_argument(
        "--context-traces",
        type=Path,
        default=Path("eval/fixtures/context_harness_sample.jsonl"),
    )
    parser.add_argument(
        "--multiturn-output",
        type=Path,
        default=Path("data/manifests/generated/stage06-multiturn-report.json"),
    )
    parser.add_argument(
        "--red-team-output",
        type=Path,
        default=Path("data/manifests/generated/stage06-red-team-report.json"),
    )
    parser.add_argument(
        "--suite-output",
        type=Path,
        default=Path("data/manifests/generated/stage06-suite-report.json"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("data/manifests/generated/stage06-regression-summary.json"),
    )
    parser.add_argument(
        "--runtime-report",
        type=Path,
        default=Path("data/manifests/generated/stage08-live-runtime-report.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    args.multiturn_output.parent.mkdir(parents=True, exist_ok=True)
    args.red_team_output.parent.mkdir(parents=True, exist_ok=True)
    args.suite_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)

    run_command(
        [
            PYTHON,
            "eval/multiturn_rewrite_report.py",
            "--scenarios",
            str(args.multiturn_scenarios),
            "--output",
            str(args.multiturn_output),
        ]
    )
    run_command(
        [
            PYTHON,
            "eval/stage10_red_team_report.py",
            "--cases",
            str(args.red_team_cases),
            "--output",
            str(args.red_team_output),
        ]
    )
    run_command(
        [
            PYTHON,
            "eval/stage10_suite.py",
            "--policy-report",
            str(args.policy_report),
            "--multiturn-report",
            str(args.multiturn_output),
            "--context-traces",
            str(args.context_traces),
            "--red-team-report",
            str(args.red_team_output),
            "--output",
            str(args.suite_output),
        ]
    )

    policy_report = load_json(args.policy_report)
    multiturn_report = load_json(args.multiturn_output)
    red_team_report = load_json(args.red_team_output)
    suite_report = load_json(args.suite_output)
    runtime_report = load_json(args.runtime_report)

    raw_summary = policy_report.get("raw_retrieval_summary", {})
    policy_summary = policy_report.get("summary", {})

    def retrieval_gate(summary: dict) -> bool:
        return (
            summary.get("source_dir_hit@5", 0.0) >= 0.85
            and summary.get("supporting_doc_hit@10", 0.0) >= 0.75
            and summary.get("citation_correctness", 0.0) >= 0.90
        )

    raw_gate = retrieval_gate(raw_summary)
    policy_gate = retrieval_gate(policy_summary)

    def metric_delta(key: str) -> float:
        return round(float(policy_summary.get(key, 0.0)) - float(raw_summary.get(key, 0.0)), 4)

    all_gates = {
        "raw_retrieval_gate": raw_gate,
        "policy_retrieval_gate": policy_gate,
        "policy_suite_gate": suite_report.get("overall_decision", "") == "go",
        "multiturn_gate": bool(multiturn_report.get("summary", {}).get("fully_passing_scenarios", 0))
        and multiturn_report.get("summary", {}).get("fully_passing_scenarios", 0)
        == multiturn_report.get("summary", {}).get("scenario_count", 0),
        "red_team_gate": bool(red_team_report.get("summary", {}).get("passed_count", 0))
        and red_team_report.get("summary", {}).get("passed_count", 0)
        == red_team_report.get("summary", {}).get("case_count", 0),
        "runtime_gate": bool(runtime_report.get("overall_pass")),
    }

    if raw_gate and policy_gate and all_gates["policy_suite_gate"] and all_gates["multiturn_gate"] and all_gates["red_team_gate"] and all_gates["runtime_gate"]:
        overall_decision = "go"
        verdict_reason = "Raw and policy-prepared retrieval both meet the widened-corpus regression bar, and the companion runtime/multiturn/red-team checks pass."
    elif policy_gate and all_gates["policy_suite_gate"] and all_gates["multiturn_gate"] and all_gates["red_team_gate"] and all_gates["runtime_gate"]:
        overall_decision = "policy-go/raw-gap-present"
        verdict_reason = "Policy-prepared retrieval is acceptable, but the raw widened-corpus baseline still underperforms, so the regression is not fully clean."
    else:
        overall_decision = "no-go"
        verdict_reason = "One or more widened-corpus regression gates failed."

    summary = {
        "stage": 6,
        "policy_report_path": str((REPO_ROOT / args.policy_report).resolve()),
        "multiturn_output_path": str((REPO_ROOT / args.multiturn_output).resolve()),
        "red_team_output_path": str((REPO_ROOT / args.red_team_output).resolve()),
        "suite_output_path": str((REPO_ROOT / args.suite_output).resolve()),
        "runtime_report_path": str((REPO_ROOT / args.runtime_report).resolve()),
        "raw_retrieval_summary": raw_summary,
        "policy_retrieval_summary": policy_summary,
        "raw_vs_policy_delta": {
            "source_dir_hit@5": metric_delta("source_dir_hit@5"),
            "supporting_doc_hit@10": metric_delta("supporting_doc_hit@10"),
            "citation_correctness": metric_delta("citation_correctness"),
            "rerank_lift@5": float(policy_summary.get("rerank_lift@5", 0.0)),
        },
        "multiturn_summary": multiturn_report.get("summary", {}),
        "red_team_summary": red_team_report.get("summary", {}),
        "runtime_summary": {
            "overall_pass": runtime_report.get("overall_pass"),
            "checks": runtime_report.get("checks", {}),
            "bridge_health": runtime_report.get("bridge_health", {}),
        },
        "stage6_gates": all_gates,
        "gates": suite_report.get("gates", {}),
        "raw_gate": raw_gate,
        "policy_gate": policy_gate,
        "policy_suite_decision": suite_report.get("overall_decision", ""),
        "known_blockers": suite_report.get("known_blockers", []),
        "overall_decision": overall_decision,
        "verdict_reason": verdict_reason,
        "pass": overall_decision == "go",
    }

    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
