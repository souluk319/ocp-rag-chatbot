from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DEFAULT_REPORT_PATH = ROOT / "reports" / "build_logs" / "translation_draft_generation_report.json"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.translation_draft_generation import generate_translation_drafts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate actual Korean draft artifacts from translated draft manifest.",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        default=[],
        help="Optional slug filter. Repeatable.",
    )
    parser.add_argument(
        "--force-collect",
        action="store_true",
        help="Re-fetch source HTML even if cached.",
    )
    parser.add_argument(
        "--force-regenerate",
        action="store_true",
        help="Ignore existing draft outputs and regenerate selected books from scratch.",
    )
    parser.add_argument(
        "--manifest-path",
        help="Optional manifest path to read instead of the default translation draft manifest.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    report = generate_translation_drafts(
        settings,
        slugs=[slug.strip() for slug in args.slugs if slug.strip()] or None,
        force_collect=args.force_collect,
        force_regenerate=args.force_regenerate,
        manifest_path=(Path(args.manifest_path).expanduser().resolve() if args.manifest_path else None),
    )
    report_path = DEFAULT_REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
