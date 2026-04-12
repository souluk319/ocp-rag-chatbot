# `play_book.cmd eval`과 같은 실행 경로를 쓰는 호환 스크립트다.
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.cli import _add_runtime_args, _run_eval


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the answer evaluation")
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "manifests" / "answer_eval_cases.jsonl",
    )
    _add_runtime_args(parser)
    return parser


def main() -> int:
    return _run_eval(build_parser().parse_args())


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
