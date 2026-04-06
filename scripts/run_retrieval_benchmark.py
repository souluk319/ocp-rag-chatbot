from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.shared.io import read_jsonl
from ocp_rag.shared.settings import load_settings
from ocp_rag.evals.retrieval import summarize_case_results
from ocp_rag.retrieval.models import SessionContext
from ocp_rag.retrieval.retriever import Retriever


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the retrieval benchmark")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "part2_retrieval_benchmark.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--skip-vector", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT, create_dirs=True)
    retriever = Retriever.from_settings(settings, enable_vector=not args.skip_vector)
    cases = read_jsonl(args.cases)

    case_results: list[dict] = []
    for case in cases:
        context = SessionContext.from_dict(case.get("context"))
        result = retriever.retrieve(
            str(case["query"]),
            context=context,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            use_vector=not args.skip_vector,
        )
        case_results.append(
            {
                "id": case.get("id"),
                "mode": case.get("mode", "ops"),
                "query_type": case.get("query_type", "ops"),
                "query": case["query"],
                "rewritten_query": result.rewritten_query,
                "expected_book_slugs": list(case.get("expected_book_slugs", [])),
                "top_book_slugs": [hit.book_slug for hit in result.hits],
                "warnings": result.trace.get("warnings", []),
            }
        )

    summary = summarize_case_results(case_results)
    report = {
        "cases_file": str(args.cases),
        "top_k": args.top_k,
        "candidate_k": args.candidate_k,
        **summary,
        "details": case_results,
    }

    output_path = settings.retrieval_benchmark_report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote benchmark report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
