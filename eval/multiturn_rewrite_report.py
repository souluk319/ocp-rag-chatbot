from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.multiturn_memory import SessionMemoryManager


def load_scenarios(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def contains_all_terms(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def contains_any_forbidden(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def evaluate_scenario(manager: SessionMemoryManager, scenario: dict) -> dict:
    session_id = scenario["scenario_id"]
    turn_reports = []
    all_turns_pass = True

    for turn in scenario["turns"]:
        result = manager.process_turn(
            session_id=session_id,
            turn_index=turn["turn_index"],
            question_ko=turn["question_ko"],
            reference_doc_path=turn.get("expected_document_path", ""),
            reference_source_dir=turn.get("expected_source_dir", ""),
        )
        actual_turn = result["turn"]
        rewritten_query = actual_turn["rewritten_query"]
        checks = {
            "classification_match": actual_turn["classification"] == turn["expected_classification"],
            "source_dir_match": actual_turn["source_dir"] == turn["expected_source_dir"],
            "topic_match": actual_turn["active_topic"] == turn["expected_topic"],
            "version_match": actual_turn["active_version"] == turn["expected_version"],
            "rewrite_terms_match": contains_all_terms(rewritten_query, turn["required_rewrite_terms"]),
            "forbidden_terms_absent": not contains_any_forbidden(
                rewritten_query,
                turn.get("forbidden_rewrite_terms", []),
            ),
        }
        checks["turn_pass"] = all(checks.values())
        all_turns_pass = all_turns_pass and checks["turn_pass"]

        turn_reports.append(
            {
                "turn_index": turn["turn_index"],
                "question_ko": turn["question_ko"],
                "expected_classification": turn["expected_classification"],
                "expected_source_dir": turn["expected_source_dir"],
                "expected_topic": turn["expected_topic"],
                "expected_version": turn["expected_version"],
                "rewritten_query": rewritten_query,
                "checks": checks,
                "issues": actual_turn["issues"],
                "state_after": result["state_after"],
            }
        )

    return {
        "scenario_id": scenario["scenario_id"],
        "title": scenario["title"],
        "turn_count": len(scenario["turns"]),
        "all_turns_pass": all_turns_pass,
        "turns": turn_reports,
    }


def build_summary(reports: list[dict]) -> dict:
    all_turns = [turn for scenario in reports for turn in scenario["turns"]]
    scenario_count = len(reports)
    turn_count = len(all_turns)
    fully_passing_scenarios = sum(1 for scenario in reports if scenario["all_turns_pass"])

    def ratio(key: str) -> float:
        if turn_count == 0:
            return 0.0
        return round(
            sum(1 for turn in all_turns if turn["checks"][key]) / turn_count,
            4,
        )

    return {
        "scenario_count": scenario_count,
        "turn_count": turn_count,
        "rewrite_term_pass_rate": ratio("rewrite_terms_match"),
        "source_dir_pass_rate": ratio("source_dir_match"),
        "version_pass_rate": ratio("version_match"),
        "classification_pass_rate": ratio("classification_match"),
        "topic_pass_rate": ratio("topic_match"),
        "fully_passing_scenarios": fully_passing_scenarios,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Stage 7 multi-turn rewrite scenarios.")
    parser.add_argument("--scenarios", required=True, help="Path to the multi-turn scenario JSON file.")
    parser.add_argument("--output", help="Optional path to write the JSON report.")
    args = parser.parse_args()

    payload = load_scenarios(Path(args.scenarios))
    manager = SessionMemoryManager()
    reports = [evaluate_scenario(manager, scenario) for scenario in payload.get("scenarios", [])]
    report = {
        "summary": build_summary(reports),
        "scenarios": reports,
    }

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
