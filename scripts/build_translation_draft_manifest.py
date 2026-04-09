# 영문 fallback 고가치 문서를 translated_ko_draft manifest로 올린다.
# 이제 영어 원본을 제외하지 않고, 코퍼스/플레이북 draft 생산 대상에 넣는 진입점이다.
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.approval_report import build_source_approval_report
from play_book_studio.ingestion.manifest import read_manifest, runtime_catalog_entries, write_manifest
from play_book_studio.ingestion.models import CONTENT_STATUS_TRANSLATED_KO_DRAFT, SourceManifestEntry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build translated Korean draft manifest for high-value fallback docs.",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        default=[],
        help="Specific book slug to include. Repeatable. Defaults to translation_first high-value queue.",
    )
    parser.add_argument(
        "--output-manifest-path",
        help="Optional output path. Defaults to the active pack translated draft manifest path.",
    )
    return parser


def _select_target_slugs(settings, explicit_slugs: list[str]) -> list[str]:
    if explicit_slugs:
        return sorted({slug.strip() for slug in explicit_slugs if slug.strip()})
    report = build_source_approval_report(settings)
    selected = [
        str(item["book_slug"])
        for item in report["books"]
        if item.get("high_value")
        and item.get("gap_lane") == "translation_first"
        and str(item.get("content_status")) in {"en_only", "mixed"}
    ]
    if selected:
        return selected
    translated_manifest_path = settings.translation_draft_manifest_path
    if translated_manifest_path.exists():
        return [entry.book_slug for entry in read_manifest(translated_manifest_path)]
    return []


def _build_draft_entry(entry: SourceManifestEntry) -> SourceManifestEntry:
    source_language = (entry.translation_source_language or entry.resolved_language or entry.docs_language or "ko").strip() or "ko"
    payload = entry.to_dict()
    payload.update(
        {
            "content_status": CONTENT_STATUS_TRANSLATED_KO_DRAFT,
            "citation_eligible": False,
            "citation_block_reason": "translated Korean draft requires review before citation",
            "approval_status": "needs_review",
            "approval_notes": "machine translation draft scheduled for corpus/playbook generation",
            "resolved_language": source_language,
            "translation_source_language": source_language,
            "translation_target_language": "ko",
            "translation_source_url": entry.resolved_source_url or entry.source_url,
            "translation_source_fingerprint": entry.source_fingerprint,
            "translation_stage": CONTENT_STATUS_TRANSLATED_KO_DRAFT,
        }
    )
    return SourceManifestEntry(**payload)


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    approval_report = build_source_approval_report(settings)
    target_slugs = _select_target_slugs(settings, args.slugs)
    catalog_entries = runtime_catalog_entries(read_manifest(settings.source_catalog_path), settings)
    catalog_by_slug = {entry.book_slug: entry for entry in catalog_entries}
    books_by_slug = {str(item["book_slug"]): item for item in approval_report["books"]}

    missing = [slug for slug in target_slugs if slug not in catalog_by_slug]
    if missing:
        raise SystemExit(f"missing source catalog entries for slugs: {', '.join(sorted(missing))}")

    entries: list[SourceManifestEntry] = []
    for slug in target_slugs:
        entry = catalog_by_slug[slug]
        book = books_by_slug.get(slug, {})
        seeded = SourceManifestEntry(
            **{
                **entry.to_dict(),
                "resolved_source_url": str(book.get("resolved_source_url") or entry.resolved_source_url or entry.source_url),
                "fallback_detected": bool(book.get("fallback_detected", entry.fallback_detected)),
                "body_language_guess": str(book.get("body_language_guess") or entry.body_language_guess),
                "translation_source_language": (
                    "en"
                    if str(book.get("body_language_guess") or entry.body_language_guess) in {"en_only", "mixed"}
                    else str(
                        book.get("translation_lane", {}).get("source_language")
                        or book.get("resolved_language")
                        or entry.resolved_language
                        or entry.docs_language
                    )
                ),
            }
        )
        entries.append(_build_draft_entry(seeded))

    output_path = (
        Path(args.output_manifest_path).expanduser()
        if args.output_manifest_path
        else settings.translation_draft_manifest_path
    )
    if not output_path.is_absolute():
        output_path = (ROOT / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_manifest(output_path, entries)

    print(f"wrote translated draft manifest ({len(entries)} books): {output_path}")
    if entries:
        print("slugs=" + ", ".join(entry.book_slug for entry in entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
