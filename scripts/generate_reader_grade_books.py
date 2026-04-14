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
from play_book_studio.ingestion.reader_grade_pipeline import build_reader_grade_books


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate reader-grade markdown books from translated OCP drafts.",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        default=[],
        help="Supported: backup_and_restore, installing_on_any_platform",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    slugs = [slug.strip() for slug in args.slugs if slug.strip()] or [
        "backup_and_restore",
        "installing_on_any_platform",
    ]
    settings = load_settings(ROOT)
    outputs = build_reader_grade_books(settings, slugs=slugs, force_regenerate=True)
    payload = {
        "count": len(outputs),
        "books": [
            {
                "slug": item.slug,
                "title": item.title,
                "output_path": str(item.output_path),
                "used_section_count": item.section_count,
            }
            for item in outputs
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
