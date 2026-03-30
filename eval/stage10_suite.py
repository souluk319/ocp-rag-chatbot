from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.context_harness_report import load_records as load_trace_records
from eval.context_harness_report import summarize_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate Stage 10 evaluation and red-team evidence into a release-gate decision.")
    parser.add_argument("--policy-report", type=Path, required=True)
    parser.add_argument("--multiturn-report", type=Path, required=True)
    parser.add_argument("--context-traces", type=Path, required=True)
    parser.add_argument("--red-team-report", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_gates(policy_report: dict, multiturn_report: dict, context_report: dict, red_team_report: dict) -> dict:
    policy_summary = policy_report.get("summary", {})
    multiturn_summary = multiturn_report.get("summary", {})
    context_summary = context_report.get("summary", {})
    red_team_summary = red_team_report.get("summary", {})
    by_query_class = policy_report.get("by_query_class", {})
    follow_up_class = by_query_class.get("follow_up_rewrite", {})

    gates = {
        "retrieval_first_slice_gate": (
            policy_summary.get("source_dir_hit@5", 0.0) >= 0.85
            and policy_summary.get("supporting_doc_hit@10", 0.0) >= 0.75
            and policy_summary.get("citation_correctness", 0.0) >= 0.90
            and policy_summary.get("rerank_lift@5", -1.0) >= 0.0
        ),
        "multiturn_gate": (
            multiturn_summary.get("scenario_count", 0) > 0
            and multiturn_summary.get("fully_passing_scenarios", 0) == multiturn_summary.get("scenario_count", 0)
            and multiturn_summary.get("classification_pass_rate", 0.0) == 1.0
            and multiturn_summary.get("version_pass_rate", 0.0) == 1.0
        ),
        "context_traceability_gate": (
            context_report.get("invalid_records", []) == []
            and (
                context_summary.get("retrieval_miss", 0) > 0
                or context_summary.get("rerank_loss", 0) > 0
                or context_summary.get("assembly_loss", 0) > 0
                or context_summary.get("citation_loss", 0) > 0
                or context_summary.get("follow_up_rewrite_missing", 0) > 0
            )
        ),
        "red_team_gate": (
            red_team_summary.get("case_count", 0) > 0
            and red_team_summary.get("passed_count", 0) == red_team_summary.get("case_count", 0)
        ),
        "follow_up_retrieval_gate": (
            follow_up_class.get("supporting_doc_hit@10", 0.0) >= 1.0
            and follow_up_class.get("citation_correctness", 0.0) >= 1.0
        ),
    }
    return gates


def known_blockers(policy_report: dict, gates: dict[str, bool]) -> list[str]:
    blockers: list[str] = []
    if not gates["follow_up_retrieval_gate"]:
        blockers.append(
            "RB-011 follow-up rewrite query still misses the expected supporting document, so widening scope would hide a known grounded follow-up weakness."
        )
    if not gates["retrieval_first_slice_gate"]:
        blockers.append("The first-slice retrieval gate is not fully satisfied.")
    if not gates["red_team_gate"]:
        blockers.append("One or more Stage 10 red-team checks failed.")
    return blockers


def main() -> None:
    args = parse_args()
    policy_report = load_json(args.policy_report)
    multiturn_report = load_json(args.multiturn_report)
    context_records = load_trace_records(args.context_traces)
    context_report = summarize_records(context_records)
    red_team_report = load_json(args.red_team_report)

    gates = evaluate_gates(policy_report, multiturn_report, context_report, red_team_report)
    blockers = known_blockers(policy_report, gates)
    overall_decision = "go" if all(gates.values()) else "no-go"

    report = {
        "policy_summary_basis": policy_report.get("summary_basis", "policy_prepared_candidates"),
        "policy_summary_note": policy_report.get("summary_note", ""),
        "raw_retrieval_summary": policy_report.get("raw_retrieval_summary", {}),
        "policy_summary": policy_report.get("summary", {}),
        "multiturn_summary": multiturn_report.get("summary", {}),
        "context_summary": context_report.get("summary", {}),
        "red_team_summary": red_team_report.get("summary", {}),
        "gates": gates,
        "known_blockers": blockers,
        "overall_decision": overall_decision,
    }

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
