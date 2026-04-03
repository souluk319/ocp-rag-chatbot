from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import load_settings
from ocp_rag_part3 import Part3Answerer
from ocp_rag_part3.ragas_eval import evaluate_with_ragas, read_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Part 3 RAGAS golden-set evaluation")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "part3_ragas_golden_cases.jsonl",
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

    try:
        report = {
            "cases_file": str(args.cases),
            "top_k": args.top_k,
            "candidate_k": args.candidate_k,
            "max_context_chunks": args.max_context_chunks,
            **evaluate_with_ragas(
                cases=cases,
                answerer=answerer,
                settings=settings,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
                max_context_chunks=args.max_context_chunks,
            ),
        }
    except ValueError as exc:
        print(f"ragas eval configuration error: {exc}", file=sys.stderr)
        return 2

    output_path = settings.part3_ragas_report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote ragas eval report: {output_path}")
    print(json.dumps(report["ragas_overall"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
