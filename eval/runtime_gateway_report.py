from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.multiturn_memory import SessionMemoryManager
from app.runtime_gateway_support import build_policy_overlay, commit_runtime_grounding, prepare_runtime_turn
from app.runtime_source_index import load_active_source_catalog, reset_active_source_catalog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fixture-based checks for the live runtime gateway overlay.")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    manager = SessionMemoryManager()
    reset_active_source_catalog()
    load_active_source_catalog()

    results: list[dict] = []
    for case in cases:
        plan = prepare_runtime_turn(
            question_ko=case["question_ko"],
            conversation_id=case["conversation_id"],
            mode=case.get("mode", "operations"),
            memory_manager=manager,
        )
        overlay = build_policy_overlay(
            question_ko=case["question_ko"],
            mode=case.get("mode", "operations"),
            sources=case.get("upstream_sources", []),
            memory_before=plan.memory_before,
        )
        state_after = commit_runtime_grounding(
            conversation_id=case["conversation_id"],
            sources=overlay["policy_sources"],
            memory_manager=manager,
        )
        top_source = overlay["policy_sources"][0] if overlay["policy_sources"] else {}
        results.append(
            {
                "id": case["id"],
                "conversation_id": plan.conversation_id,
                "rewritten_query": plan.rewritten_query,
                "top_document_path": top_source.get("document_path", ""),
                "top_viewer_url": top_source.get("viewer_url", ""),
                "policy_signals": overlay["policy_signals"],
                "state_after": state_after,
            }
        )

    report = {
        "case_count": len(results),
        "results": results,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
