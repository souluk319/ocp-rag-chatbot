"""source bundle readiness를 번역/수동검토 산출물 큐로 승격한다."""

from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.config.settings import Settings

from .manifest import read_manifest, runtime_catalog_entries, write_manifest
from .models import CONTENT_STATUS_TRANSLATED_KO_DRAFT, SourceManifestEntry
from .source_bundle_quality import build_source_bundle_quality_report


def _entry_identity(entry: SourceManifestEntry) -> tuple[str, str, str, str]:
    return (
        entry.ocp_version,
        entry.docs_language,
        entry.source_kind,
        entry.book_slug,
    )


def _safe_read_manifest(path: Path) -> list[SourceManifestEntry]:
    if not path.exists():
        return []
    return read_manifest(path)


def _bundle_root(settings: Settings, slug: str) -> Path:
    return settings.bronze_dir / "source_bundles" / slug


def _bundle_dossier(settings: Settings, slug: str) -> dict[str, object]:
    path = _bundle_root(settings, slug) / "dossier.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _build_translation_entry(
    entry: SourceManifestEntry,
    *,
    readiness_row: dict[str, object],
    dossier: dict[str, object],
) -> SourceManifestEntry:
    payload = entry.to_dict()
    official_docs = dict(dossier.get("official_docs", {}))
    official_en = dict(official_docs.get("en", {}))
    source_url = str(official_en.get("url") or entry.translation_source_url or entry.resolved_source_url or entry.source_url)
    source_language = (
        entry.translation_source_language
        or entry.resolved_language
        or ("en" if bool(readiness_row.get("ko_fallback_banner", False)) else entry.docs_language)
        or "en"
    ).strip() or "en"
    if source_language == "ko":
        source_language = "en"
    payload.update(
        {
            "content_status": CONTENT_STATUS_TRANSLATED_KO_DRAFT,
            "citation_eligible": False,
            "citation_block_reason": "translated Korean draft requires review before citation",
            "approval_status": "needs_review",
            "approval_notes": "synthesis lane promoted from translation_ready bronze bundle",
            "resolved_language": source_language,
            "source_lane": "official_en_fallback" if bool(readiness_row.get("ko_fallback_banner", False)) else (entry.source_lane or "official_ko"),
            "translation_source_language": source_language,
            "translation_target_language": "ko",
            "translation_source_url": source_url,
            "translation_source_fingerprint": entry.translation_source_fingerprint or entry.source_fingerprint,
            "translation_stage": CONTENT_STATUS_TRANSLATED_KO_DRAFT,
        }
    )
    return SourceManifestEntry(**payload)


def build_synthesis_lane(settings: Settings) -> dict[str, object]:
    quality_report = build_source_bundle_quality_report(settings)
    runtime_catalog = runtime_catalog_entries(read_manifest(settings.source_catalog_path), settings)
    runtime_catalog_by_slug = {entry.book_slug: entry for entry in runtime_catalog}
    approved_entries = _safe_read_manifest(settings.source_manifest_path)
    existing_translation_entries = _safe_read_manifest(settings.translation_draft_manifest_path)
    translation_overlay = {_entry_identity(entry): entry for entry in existing_translation_entries}

    translation_ready_rows = [
        row for row in quality_report["bundles"] if row["readiness"] == "translation_ready"
    ]
    manual_review_rows = [
        row for row in quality_report["bundles"] if row["readiness"] == "manual_review_ready"
    ]

    translation_entries: list[SourceManifestEntry] = []
    translation_rows: list[dict[str, object]] = []
    for row in translation_ready_rows:
        slug = str(row["book_slug"])
        runtime_entry = runtime_catalog_by_slug.get(slug)
        if runtime_entry is None:
            continue
        base_entry = translation_overlay.get(_entry_identity(runtime_entry), runtime_entry)
        dossier = _bundle_dossier(settings, slug)
        translated_entry = _build_translation_entry(base_entry, readiness_row=row, dossier=dossier)
        translation_entries.append(translated_entry)
        translation_rows.append(
            {
                **row,
                "bundle_root": str(_bundle_root(settings, slug)),
                "translation_source_url": translated_entry.translation_source_url,
                "translation_source_language": translated_entry.translation_source_language,
            }
        )

    approved_by_key = {_entry_identity(entry): entry for entry in approved_entries}
    for entry in translation_entries:
        approved_by_key[_entry_identity(entry)] = entry
    corpus_working_entries = sorted(approved_by_key.values(), key=_entry_identity)

    manual_review_queue = [
        {
            **row,
            "bundle_root": str(_bundle_root(settings, str(row["book_slug"]))),
        }
        for row in manual_review_rows
    ]

    return {
        "summary": {
            "approved_runtime_count": len(approved_entries),
            "translation_ready_count": len(translation_entries),
            "manual_review_ready_count": len(manual_review_queue),
            "corpus_working_count": len(corpus_working_entries),
        },
        "translation_ready": translation_rows,
        "manual_review_ready": manual_review_queue,
        "output_targets": {
            "translation_draft_manifest_path": str(settings.translation_draft_manifest_path),
            "corpus_working_manifest_path": str(settings.corpus_working_manifest_path),
        },
        "translation_entries": translation_entries,
        "corpus_working_entries": corpus_working_entries,
    }


def write_synthesis_lane_outputs(
    settings: Settings,
    *,
    report_path: Path,
) -> dict[str, object]:
    report = build_synthesis_lane(settings)
    translation_entries = list(report.pop("translation_entries"))
    corpus_working_entries = list(report.pop("corpus_working_entries"))
    write_manifest(settings.translation_draft_manifest_path, translation_entries)
    write_manifest(settings.corpus_working_manifest_path, corpus_working_entries)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
