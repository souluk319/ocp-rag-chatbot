from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.shared.settings import load_settings
from ocp_rag.shared.io import read_jsonl
from ocp_rag.retrieval.models import SessionContext
from ocp_rag.retrieval.retriever import Part2Retriever


def _hit_at(top_books: list[str], expected_books: set[str], k: int) -> bool:
    return any(book_slug in expected_books for book_slug in top_books[:k])


def _metric_summary(details: list[dict]) -> dict[str, float]:
    total = max(len(details), 1)
    return {
        "case_count": len(details),
        "book_hit_at_1": round(sum(int(item["book_hit_at_1"]) for item in details) / total, 4),
        "book_hit_at_3": round(sum(int(item["book_hit_at_3"]) for item in details) / total, 4),
        "book_hit_at_5": round(sum(int(item["book_hit_at_5"]) for item in details) / total, 4),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Part 2 retrieval evaluation benchmark")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "part2_retrieval_eval_cases.jsonl",
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

    details: list[dict] = []
    by_category: dict[str, list[dict]] = defaultdict(list)

    for case in cases:
        context = SessionContext.from_dict(case.get("context"))
        result = retriever.retrieve(
            str(case["query"]),
            context=context,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            use_vector=not args.skip_vector,
        )
        top_books = [hit.book_slug for hit in result.hits]
        expected_books = set(case.get("expected_book_slugs", []))
        detail = {
            "id": case["id"],
            "category": case["category"],
            "query": case["query"],
            "expected_book_slugs": sorted(expected_books),
            "rewritten_query": result.rewritten_query,
            "top_book_slugs": top_books,
            "book_hit_at_1": _hit_at(top_books, expected_books, 1),
            "book_hit_at_3": _hit_at(top_books, expected_books, 3),
            "book_hit_at_5": _hit_at(top_books, expected_books, 5),
            "warnings": result.trace.get("warnings", []),
        }
        details.append(detail)
        by_category[case["category"]].append(detail)

    report = {
        "case_count": len(cases),
        "top_k": args.top_k,
        "candidate_k": args.candidate_k,
        "overall": _metric_summary(details),
        "by_category": {
            category: _metric_summary(category_details)
            for category, category_details in sorted(by_category.items())
        },
        "misses_at_5": [item for item in details if not item["book_hit_at_5"]],
        "details": details,
    }

    output_path = settings.part2_dir / "retrieval_eval_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote eval report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
