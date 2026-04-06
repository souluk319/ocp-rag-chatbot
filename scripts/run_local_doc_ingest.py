from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest.pipeline import run_local_document_pipeline
from ocp_rag.shared.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build normalized local-doc artifacts")
    parser.add_argument("inputs", nargs="+", help="Local .html/.md/.txt files to normalize")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory. Defaults to ARTIFACTS_DIR/ingest/local_document_preview",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT, create_dirs=True)
    report = run_local_document_pipeline(
        settings,
        inputs=[Path(item) for item in args.inputs],
        output_dir=args.output_dir,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
