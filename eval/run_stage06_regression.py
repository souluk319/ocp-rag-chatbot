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
        description="Run Stage 6 multiturn and red-team regression against the Stage 5 widened corpus gate."
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

    summary = {
        "stage": 6,
        "policy_report_path": str((REPO_ROOT / args.policy_report).resolve()),
        "multiturn_output_path": str((REPO_ROOT / args.multiturn_output).resolve()),
        "red_team_output_path": str((REPO_ROOT / args.red_team_output).resolve()),
        "suite_output_path": str((REPO_ROOT / args.suite_output).resolve()),
        "policy_summary": policy_report.get("summary", {}),
        "multiturn_summary": multiturn_report.get("summary", {}),
        "red_team_summary": red_team_report.get("summary", {}),
        "gates": suite_report.get("gates", {}),
        "overall_decision": suite_report.get("overall_decision", ""),
        "known_blockers": suite_report.get("known_blockers", []),
        "pass": suite_report.get("overall_decision", "") == "go",
    }

    args.summary_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
