from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.overrides import (
    deduplicate_override_sections,
    read_override_sections,
    write_override_sections,
)
from ocp_rag_part1.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deduplicate translation override JSONL files by (book_slug, anchor)."
    )
    parser.add_argument(
        "--books",
        nargs="*",
        default=[],
        help="Optional subset of book slugs to clean. Default: all override files.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    target_paths = sorted(settings.translation_overrides_dir.glob("*.jsonl"))
    if args.books:
        wanted = set(args.books)
        target_paths = [path for path in target_paths if path.stem in wanted]

    summary: list[dict[str, object]] = []
    for path in target_paths:
        original = read_override_sections(path)
        deduped, duplicate_count = deduplicate_override_sections(original)
        write_override_sections(path, deduped)
        row = {
            "book_slug": path.stem,
            "original_count": len(original),
            "deduped_count": len(deduped),
            "duplicate_count_removed": duplicate_count,
            "path": str(path),
        }
        summary.append(row)
        print(
            f"{path.stem}: original={len(original)} deduped={len(deduped)} "
            f"removed={duplicate_count}"
        )

    report_path = settings.translation_overrides_dir / "_dedupe_report.json"
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote dedupe report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
