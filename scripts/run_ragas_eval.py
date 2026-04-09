# `play_book.cmd ragas`와 같은 실행 경로를 쓰는 호환 스크립트다.
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.cli import _run_ragas


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
    return _run_ragas(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
