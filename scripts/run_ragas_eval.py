# RAGAS judge 기반 평가를 돌려 faithfulness/relevancy 계열 지표를 기록하는 스크립트.
# answer eval과 별도로 정합성·관련성 경향을 비교할 때 쓴다.
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_effective_env, load_settings
from play_book_studio.answering.answerer import Part3Answerer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the RAGAS evaluation")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "ragas_eval_cases.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--max-context-chunks", type=int, default=6)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument(
        "--judge-model",
        default=None,
        help="OpenAI judge model override. Defaults to OPENAI_JUDGE_MODEL or gpt-5.2.",
    )
    parser.add_argument(
        "--embedding-model",
        default=None,
        help="OpenAI embedding model override. Defaults to OPENAI_EMBEDDING_MODEL or text-embedding-3-small.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only build the normalized RAGAS dataset rows and skip judge execution.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        from play_book_studio.evals.ragas_eval import (
            build_ragas_case_row,
            evaluate_cases_with_ragas,
            generate_answers_for_cases,
            load_openai_judge_config_from_env,
            read_jsonl,
        )
    except ModuleNotFoundError as exc:
        missing = exc.name or "optional dependency"
        print(
            f"ragas dependencies are not installed: missing {missing}\n"
            "hint: install the eval extras with `pip install -e \".[eval]\"`",
            file=sys.stderr,
        )
        return 1

    effective_env = load_effective_env(ROOT)
    settings = load_settings(ROOT)
    answerer = Part3Answerer.from_settings(settings)
    cases = read_jsonl(args.cases)

    if args.dry_run:
        generated_results = generate_answers_for_cases(
            answerer,
            cases,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            max_context_chunks=args.max_context_chunks,
        )
        rows: list[dict] = []
        for case, generated_result in zip(cases, generated_results, strict=True):
            row, metadata = build_ragas_case_row(case, generated_result=generated_result)
            rows.append({**metadata, **row})
        output_path = settings.ragas_dataset_preview_path
        output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote ragas dataset preview: {output_path}")
        print(json.dumps({"case_count": len(rows), "preview_path": str(output_path)}, ensure_ascii=False, indent=2))
        return 0

    try:
        judge_config = load_openai_judge_config_from_env(effective_env)
    except ValueError as exc:
        print(f"ragas judge configuration error: {exc}")
        print("hint: add OPENAI_API_KEY to .env or run with --dry-run first")
        return 1

    judge_config.judge_model = args.judge_model or judge_config.judge_model
    judge_config.embedding_model = args.embedding_model or judge_config.embedding_model

    report = evaluate_cases_with_ragas(
        answerer,
        cases,
        judge_config=judge_config,
        top_k=args.top_k,
        candidate_k=args.candidate_k,
        max_context_chunks=args.max_context_chunks,
        batch_size=args.batch_size,
    )

    output_path = settings.ragas_eval_report_path
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote ragas eval report: {output_path}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
