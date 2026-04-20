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
from play_book_studio.ingestion.source_first import (
    derive_official_docs_legal_notice_url,
    derive_official_docs_license_or_terms,
    derive_source_repo_updated_at,
    resolve_repo_binding,
    source_mirror_root,
)


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
        "--all-runtime-catalog",
        action="store_true",
        help="Include every active runtime source-catalog slug instead of the high-value translation queue only.",
    )
    parser.add_argument(
        "--output-path",
        help=(
            "Optional manifest output path. "
            "When omitted, --all-runtime-catalog writes to a dedicated all-runtime queue path."
        ),
    )
    return parser


def _select_target_slugs(
    settings,
    explicit_slugs: list[str],
    *,
    all_runtime_catalog: bool = False,
) -> list[str]:
    if explicit_slugs:
        return sorted({slug.strip() for slug in explicit_slugs if slug.strip()})
    if all_runtime_catalog:
        return sorted(
            {
                entry.book_slug
                for entry in runtime_catalog_entries(read_manifest(settings.source_catalog_path), settings)
            }
        )
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
    source_repo_capable = bool(
        str(entry.primary_input_kind or "").strip() == "source_repo"
        or str(entry.source_kind or "").strip() == "source-first"
        or (
            str(entry.source_repo or "").strip()
            and (
                str(entry.source_relative_path or "").strip()
                or any(str(path).strip() for path in entry.source_relative_paths)
            )
        )
    )
    payload.update(
        {
            "source_kind": "source-first" if source_repo_capable else "html-single",
            "content_status": CONTENT_STATUS_TRANSLATED_KO_DRAFT,
            "citation_eligible": False,
            "citation_block_reason": "translated Korean draft requires review before citation",
            "approval_status": "needs_review",
            "approval_notes": "machine translation draft scheduled for corpus/playbook generation",
            "resolved_language": source_language,
            "primary_input_kind": "source_repo" if source_repo_capable else "html_single",
            "fallback_input_kind": "",
            "source_lane": "official_source_first" if source_repo_capable else str(entry.source_lane or ""),
            "translation_source_language": source_language,
            "translation_target_language": "ko",
            "translation_source_url": entry.resolved_source_url or entry.source_url,
            "translation_source_fingerprint": entry.source_fingerprint,
            "translation_stage": CONTENT_STATUS_TRANSLATED_KO_DRAFT,
        }
    )
    return SourceManifestEntry(**payload)


def _default_output_path(settings, *, all_runtime_catalog: bool) -> Path:
    output_path = settings.translation_draft_manifest_path
    if not all_runtime_catalog:
        return output_path
    return output_path.with_name(f"{output_path.stem}_all_runtime{output_path.suffix}")


def main() -> int:
    args = build_parser().parse_args()
    settings = load_settings(ROOT)
    approval_report = build_source_approval_report(settings)
    target_slugs = _select_target_slugs(
        settings,
        args.slugs,
        all_runtime_catalog=args.all_runtime_catalog,
    )
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
        binding = resolve_repo_binding(settings.root_dir, slug)
        source_relative_paths = tuple(binding.source_relative_paths) if binding is not None else tuple(
            str(path).strip() for path in entry.source_relative_paths if str(path).strip()
        )
        mirror_root = Path(entry.source_mirror_root or source_mirror_root(settings.root_dir))
        seeded_entry = SourceManifestEntry(
            **{
                **entry.to_dict(),
                "source_binding_kind": str(entry.source_binding_kind or (binding.binding_kind if binding is not None else "")),
                "source_relative_path": str(entry.source_relative_path or (binding.root_relative_path if binding is not None else "")),
                "source_relative_paths": list(source_relative_paths),
                "source_mirror_root": str(mirror_root),
            }
        )
        legal_notice_url = str(
            book.get("legal_notice_url")
            or seeded_entry.legal_notice_url
            or derive_official_docs_legal_notice_url(seeded_entry)
        )
        license_or_terms = str(
            book.get("license_or_terms")
            or seeded_entry.license_or_terms
            or derive_official_docs_license_or_terms(seeded_entry, legal_notice_url=legal_notice_url)
        )
        updated_at = str(
            book.get("updated_at")
            or seeded_entry.updated_at
            or derive_source_repo_updated_at(
                settings.root_dir,
                source_relative_paths=source_relative_paths,
                mirror_root=mirror_root,
            )
        )
        seeded = SourceManifestEntry(
            **{
                **seeded_entry.to_dict(),
                "resolved_source_url": str(book.get("resolved_source_url") or seeded_entry.resolved_source_url or seeded_entry.source_url),
                "fallback_detected": bool(book.get("fallback_detected", seeded_entry.fallback_detected)),
                "body_language_guess": str(book.get("body_language_guess") or seeded_entry.body_language_guess),
                "legal_notice_url": legal_notice_url,
                "license_or_terms": license_or_terms,
                "updated_at": updated_at,
                "translation_source_language": (
                    "en"
                    if str(book.get("body_language_guess") or seeded_entry.body_language_guess) in {"en_only", "mixed"}
                    else str(
                        book.get("translation_lane", {}).get("source_language")
                        or book.get("resolved_language")
                        or seeded_entry.resolved_language
                        or seeded_entry.docs_language
                    )
                ),
            }
        )
        entries.append(_build_draft_entry(seeded))

    output_path = (
        Path(args.output_path).expanduser().resolve()
        if args.output_path
        else _default_output_path(settings, all_runtime_catalog=args.all_runtime_catalog)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_manifest(output_path, entries)

    print(f"wrote translated draft manifest ({len(entries)} books): {output_path}")
    if entries:
        print("slugs=" + ", ".join(entry.book_slug for entry in entries))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
