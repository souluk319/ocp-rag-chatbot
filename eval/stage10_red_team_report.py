from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.multiturn_memory import SessionMemoryManager
from app.ocp_policy import load_policy_engine
from eval.retrieval_benchmark_report import load_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stage 10 red-team checks against the Stage 9 policy baseline.")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def evaluate_policy_case(case: dict[str, Any]) -> dict[str, Any]:
    engine = load_policy_engine()
    reranked, signals = engine.rerank_candidates(
        case["question_ko"],
        case.get("candidates", []),
        mode=case.get("mode", "operations"),
        memory_state=case.get("memory_state", {}),
    )
    contract = engine.build_answer_contract(
        case["question_ko"],
        reranked,
        mode=case.get("mode", "operations"),
        grounded=bool(reranked),
        memory_state=case.get("memory_state", {}),
    )
    expected = case.get("expected", {})
    instructions = " ".join(contract.get("instructions", []))
    top_candidate = reranked[0] if reranked else {}
    checks: dict[str, bool] = {}

    if "grounded" in expected:
        checks["grounded_match"] = bool(contract.get("grounded")) == bool(expected["grounded"])
    if expected.get("ungrounded_response"):
        checks["ungrounded_response_present"] = engine.answering.get("ungrounded_response_ko", "") in instructions
    if "top_document_path" in expected:
        checks["top_document_match"] = top_candidate.get("document_path", "") == expected["top_document_path"]
    if "top_product" in expected:
        checks["top_product_match"] = top_candidate.get("product", "") == expected["top_product"]
    if "version_hint" in expected:
        checks["version_hint_match"] = contract.get("signals", {}).get("version_hint", "") == expected["version_hint"]
    if expected.get("risk_notice"):
        checks["risk_notice_present"] = "주의 문구" in instructions or "위험" in instructions
    if expected.get("citations_required"):
        checks["citations_required"] = any("출처" in item or "citation" in item.lower() for item in contract.get("instructions", []))
    if expected.get("version_uncertainty_notice"):
        checks["version_uncertainty_notice"] = "버전이 명시되지 않으면" in instructions

    return {
        "id": case["id"],
        "case_type": "policy",
        "title": case["title"],
        "group": case["group"],
        "checks": checks,
        "passed": all(checks.values()) if checks else True,
        "top_candidate": {
            "document_path": top_candidate.get("document_path", ""),
            "product": top_candidate.get("product", ""),
            "version": top_candidate.get("version", ""),
        },
        "signals": signals.to_dict(),
        "answer_contract": contract,
    }


def evaluate_memory_case(case: dict[str, Any]) -> dict[str, Any]:
    manager = SessionMemoryManager()
    final_turn: dict[str, Any] | None = None
    state_after: dict[str, Any] | None = None

    for turn in case.get("turns", []):
        result = manager.process_turn(
            session_id=case["session_id"],
            turn_index=turn["turn_index"],
            question_ko=turn["question_ko"],
            reference_doc_path=turn.get("reference_doc_path", ""),
            reference_source_dir=turn.get("reference_source_dir", ""),
        )
        final_turn = result["turn"]
        state_after = result["state_after"]

    expected = case.get("expected", {})
    final_turn = final_turn or {}
    checks = {
        "classification_match": final_turn.get("classification", "") == expected.get("final_classification", ""),
        "source_dir_match": final_turn.get("source_dir", "") == expected.get("final_source_dir", ""),
        "topic_match": final_turn.get("active_topic", "") == expected.get("final_topic", ""),
        "version_match": final_turn.get("active_version", "") == expected.get("final_version", ""),
    }

    return {
        "id": case["id"],
        "case_type": "memory",
        "title": case["title"],
        "group": case["group"],
        "checks": checks,
        "passed": all(checks.values()),
        "final_turn": final_turn,
        "state_after": state_after or {},
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    group_counts: dict[str, int] = {}
    group_pass_counts: dict[str, int] = {}
    for result in results:
        group = result["group"]
        group_counts[group] = group_counts.get(group, 0) + 1
        if result["passed"]:
            group_pass_counts[group] = group_pass_counts.get(group, 0) + 1

    return {
        "case_count": len(results),
        "passed_count": sum(1 for result in results if result["passed"]),
        "failed_case_ids": [result["id"] for result in results if not result["passed"]],
        "group_pass_rates": {
            group: round(group_pass_counts.get(group, 0) / count, 4)
            for group, count in sorted(group_counts.items())
        },
    }


def main() -> None:
    args = parse_args()
    cases = load_records(args.cases)
    results: list[dict[str, Any]] = []

    for case in cases:
        if case["case_type"] == "policy":
            results.append(evaluate_policy_case(case))
        elif case["case_type"] == "memory":
            results.append(evaluate_memory_case(case))
        else:
            raise ValueError(f"Unsupported case_type: {case['case_type']}")

    report = {
        "summary": summarize(results),
        "results": results,
    }

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
