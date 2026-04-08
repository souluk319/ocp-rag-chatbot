# 최소 검색 품질 게이트를 확인하는 sanity 케이스 실행 스크립트.
# 큰 변경 뒤에 전체 benchmark 전에 빠르게 이상 유무를 보는 용도다.
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
from play_book_studio.retrieval.retriever import Part2Retriever
from play_book_studio.evals.sanity import evaluate_case, read_jsonl, summarize_results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the retrieval sanity gate")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "retrieval_sanity_cases.jsonl",
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

    details = [
        evaluate_case(
            retriever,
            case,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            use_vector=not args.skip_vector,
        )
        for case in cases
    ]
    report = {
        "cases_file": str(args.cases),
        "top_k": args.top_k,
        "candidate_k": args.candidate_k,
        **summarize_results(details),
    }

    output_path = settings.retrieval_sanity_report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote sanity report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
