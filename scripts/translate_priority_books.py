from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.language_policy import load_language_policy_map
from ocp_rag_part1.overrides import (
    deduplicate_override_sections,
    read_override_sections,
    write_override_sections,
)
from ocp_rag_part1.settings import load_settings
from ocp_rag_part1.translation import SectionTranslator, read_sections, translate_section


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Translate English-first high-value books into Korean section overrides."
    )
    parser.add_argument(
        "--books",
        nargs="*",
        default=[],
        help="Specific book slugs to translate. Default: translate_priority books from language policy.",
    )
    parser.add_argument(
        "--limit-sections",
        type=int,
        default=0,
        help="Translate only the first N sections per selected book for smoke validation.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing translated override files.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Retry count per section when translation fails.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    policy_map = load_language_policy_map(settings)
    target_books = args.books or [
        slug
        for slug, policy in policy_map.items()
        if str(policy.get("recommended_action")) == "translate_priority"
    ]
    target_books = list(dict.fromkeys(target_books))
    if not target_books:
        raise SystemExit("No translation target books found.")

    all_sections = read_sections(settings)
    grouped: dict[str, list] = {}
    for section in all_sections:
        if section.book_slug in target_books:
            grouped.setdefault(section.book_slug, []).append(section)

    translator = SectionTranslator(settings)
    report_rows: list[dict[str, object]] = []
    translated_total = 0

    for slug in target_books:
        sections = grouped.get(slug, [])
        if args.limit_sections > 0:
            sections = sections[: args.limit_sections]
        output_path = settings.translation_overrides_dir / f"{slug}.jsonl"
        if args.overwrite and output_path.exists():
            output_path.unlink()

        existing_sections = read_override_sections(output_path)
        deduped_existing, duplicate_count = deduplicate_override_sections(existing_sections)
        if duplicate_count > 0:
            write_override_sections(output_path, deduped_existing)
            print(
                f"deduplicated {slug}: removed_duplicates={duplicate_count} "
                f"kept={len(deduped_existing)}"
            )

        valid_keys = {section.section_key or section.anchor for section in sections}
        filtered_existing = [
            section
            for section in deduped_existing
            if (section.section_key or section.anchor) in valid_keys
        ]
        stale_count = len(deduped_existing) - len(filtered_existing)
        if stale_count > 0:
            write_override_sections(output_path, filtered_existing)
            print(
                f"pruned stale overrides for {slug}: removed_stale={stale_count} "
                f"kept={len(filtered_existing)}"
            )

        existing_keys = {section.section_key or section.anchor for section in filtered_existing}
        pending_sections = [
            section
            for section in sections
            if (section.section_key or section.anchor) not in existing_keys
        ]
        translated_count = len(filtered_existing)

        with output_path.open("a", encoding="utf-8") as handle:
            for section in pending_sections:
                translated = None
                for attempt in range(1, max(args.max_retries, 1) + 1):
                    try:
                        translated = translate_section(translator, section)
                        handle.write(json.dumps(translated.to_dict(), ensure_ascii=False) + "\n")
                        handle.flush()
                        translated_count += 1
                        translated_total += 1
                        break
                    except Exception as exc:  # noqa: BLE001
                        if attempt >= args.max_retries:
                            raise
                        time.sleep(attempt)
                if translated is None:
                    raise RuntimeError(f"translation did not produce output for {slug}:{section.anchor}")

        report_rows.append(
            {
                "book_slug": slug,
                "section_count": len(sections),
                "output_section_count": translated_count,
                "duplicate_count_removed": duplicate_count,
                "stale_count_removed": stale_count,
                "status": "translated" if translated_count == len(sections) else "partial",
                "output_path": str(output_path),
            }
        )
        print(f"translated {slug}: sections={translated_count}/{len(sections)} -> {output_path}")

    status_counts = Counter(str(row["status"]) for row in report_rows)
    payload = {
        "book_count": len(target_books),
        "translated_section_count": translated_total,
        "status_counts": dict(status_counts),
        "books": report_rows,
    }
    settings.translation_report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote translation report: {settings.translation_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
