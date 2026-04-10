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
        "--report-path",
        default="reports/build_logs/translation_draft_generation_report.json",
        help="Where to write the generation report JSON.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    report = generate_translation_drafts(
        settings,
        slugs=[slug.strip() for slug in args.slugs if slug.strip()] or None,
        force_collect=args.force_collect,
    )
    report_path = Path(args.report_path).expanduser()
    if not report_path.is_absolute():
        report_path = (ROOT / report_path).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
