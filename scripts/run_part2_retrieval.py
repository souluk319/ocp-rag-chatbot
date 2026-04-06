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
from ocp_rag.retrieval.retriever import Part2Retriever


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Part 2 retrieval pipeline")
    parser.add_argument("query", nargs="+")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--context-file", type=Path)
    parser.add_argument("--skip-bm25", action="store_true")
    parser.add_argument("--skip-vector", action="store_true")
    parser.add_argument("--log-path", type=Path)
    return parser


def load_context(path: Path | None) -> SessionContext:
    if path is None:
        return SessionContext()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SessionContext.from_dict(payload)


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    retriever = Part2Retriever.from_settings(settings, enable_vector=not args.skip_vector)
    context = load_context(args.context_file)
    result = retriever.retrieve(
        " ".join(args.query),
        context=context,
        top_k=args.top_k,
        candidate_k=args.candidate_k,
        use_bm25=not args.skip_bm25,
        use_vector=not args.skip_vector,
    )
    log_path = retriever.append_log(result, args.log_path)
    print(f"log_path={log_path}")
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
