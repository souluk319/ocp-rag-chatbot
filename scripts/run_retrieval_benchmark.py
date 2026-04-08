# retrieval benchmark 케이스를 돌려 검색 전략 변경 전후를 비교하는 스크립트.
# shaping이나 reranker 실험 결과를 수치로 남길 때 쓴다.
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.evals.retrieval_eval import summarize_case_results
from play_book_studio.retrieval.models import SessionContext
from play_book_studio.retrieval.retriever import Part2Retriever


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the retrieval benchmark")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "retrieval_benchmark_cases.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--skip-vector", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    retriever = Part2Retriever.from_settings(settings, enable_vector=not args.skip_vector)
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

    output_path = settings.benchmark_report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote benchmark report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
