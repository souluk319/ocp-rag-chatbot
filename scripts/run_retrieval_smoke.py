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
from ocp_rag.retrieval.models import SessionContext
from ocp_rag.retrieval.retriever import Part2Retriever


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the retrieval smoke benchmark")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "part2_smoke_queries.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--skip-vector", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT, create_dirs=True)
    retriever = Part2Retriever.from_settings(settings, enable_vector=not args.skip_vector)
    cases = read_jsonl(args.cases)
    details: list[dict] = []
    hits = 0

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
        expected_books = list(case.get("expected_book_slugs", []))
        matched = any(book_slug in top_books for book_slug in expected_books)
        hits += int(matched)
        details.append(
            {
                "query": case["query"],
                "expected_book_slugs": expected_books,
                "matched": matched,
                "top_book_slugs": top_books,
                "warnings": result.trace.get("warnings", []),
            }
        )

    report = {
        "case_count": len(cases),
        "top_k": args.top_k,
        "candidate_k": args.candidate_k,
        "hit_at_k": round(hits / max(len(cases), 1), 4),
        "details": details,
    }
    output_path = settings.retrieval_smoke_report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote smoke report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
