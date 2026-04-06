from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest.settings import load_settings
from ocp_rag.retrieval.models import SessionContext
from ocp_rag.answering import Part3Answerer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Part 3 answer pipeline")
    parser.add_argument("--query", required=True)
    parser.add_argument("--mode", choices=("ops", "learn"), default="ops")
    parser.add_argument("--context-json")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--max-context-chunks", type=int, default=6)
    parser.add_argument("--skip-log", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    answerer = Part3Answerer.from_settings(settings)
    context = SessionContext.from_dict(
        json.loads(args.context_json) if args.context_json else None
    )
    result = answerer.answer(
        args.query,
        mode=args.mode,
        context=context,
        top_k=args.top_k,
        candidate_k=args.candidate_k,
        max_context_chunks=args.max_context_chunks,
    )
    if not args.skip_log:
        answerer.append_log(result)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
