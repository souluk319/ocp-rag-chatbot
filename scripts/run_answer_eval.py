# answer eval manifest를 읽어 기본 답변 품질 회귀를 점검하는 스크립트.
# play_book.cmd eval의 내부 동작을 직접 확인하거나 케이스 파일을 바꿔 돌릴 때 쓴다.
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
from play_book_studio.answering.answerer import Part3Answerer
from play_book_studio.evals.answer_eval import evaluate_case, summarize_case_results


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the answer evaluation")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "answer_eval_cases.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--max-context-chunks", type=int, default=6)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    answerer = Part3Answerer.from_settings(settings)
    cases = read_jsonl(args.cases)

    details: list[dict] = []
    for case in cases:
        details.append(
            evaluate_case(
                answerer,
                case,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
                max_context_chunks=args.max_context_chunks,
            )
        )

    report = {
        "cases_file": str(args.cases),
        "top_k": args.top_k,
        "candidate_k": args.candidate_k,
        "max_context_chunks": args.max_context_chunks,
        **summarize_case_results(details),
        "details": details,
    }

    output_path = settings.answer_eval_report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote answer eval report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
