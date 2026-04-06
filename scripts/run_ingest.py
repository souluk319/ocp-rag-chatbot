from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest.pipeline import run_ingest_pipeline
from ocp_rag.shared.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ingest pipeline")
    parser.add_argument("--refresh-manifest", action="store_true")
    parser.add_argument("--collect-subset", choices=("all", "high-value"), default="all")
    parser.add_argument("--process-subset", choices=("all", "high-value"), default="high-value")
    parser.add_argument("--collect-limit", type=int)
    parser.add_argument("--process-limit", type=int)
    parser.add_argument("--force-collect", action="store_true")
    parser.add_argument("--skip-embeddings", action="store_true")
    parser.add_argument("--skip-qdrant", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT, create_dirs=True)
    log = run_ingest_pipeline(
        settings,
        refresh_manifest=args.refresh_manifest,
        collect_subset=args.collect_subset,
        process_subset=args.process_subset,
        collect_limit=args.collect_limit,
        process_limit=args.process_limit,
        force_collect=args.force_collect,
        skip_embeddings=args.skip_embeddings,
        skip_qdrant=args.skip_qdrant,
    )
    print(f"manifest_count={log.manifest_count}")
    print(f"collected_count={log.collected_count}")
    print(f"normalized_count={log.normalized_count}")
    print(f"chunk_count={log.chunk_count}")
    print(f"embedded_count={log.embedded_count}")
    print(f"qdrant_upserted_count={log.qdrant_upserted_count}")
    print(f"errors={len(log.errors)}")
    if log.errors:
        for error in log.errors:
            print(f"[{error['stage']}] {error['source']}: {error['message']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
