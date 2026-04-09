# source catalog를 승인 가능한 runtime manifest와 approval 리포트로 바꾸는 helper다.
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .audit_rules import (
    CONTENT_STATUS_SORT_ORDER,
    LANGUAGE_FALLBACK_RE,
    body_language_guess,
    classify_content_status,
    hangul_ratio,
    is_english_like_title,
    resolve_final_content_status,
)
from .corpus_policy import (
    LANE_MANUAL_REVIEW_FIRST,
    LANE_TRANSLATION_FIRST,
    classify_gap_lane,
)
from .manifest import read_manifest, runtime_catalog_entries, write_manifest
from .models import (
    CITATION_ELIGIBLE_STATUSES,
    CONTENT_STATUS_APPROVED_KO,
    CONTENT_STATUS_BLOCKED,
    CONTENT_STATUS_EN_ONLY,
    CONTENT_STATUS_MIXED,
    CONTENT_STATUS_TRANSLATED_KO_DRAFT,
    SourceManifestEntry,
)
from .translation_lane import (
    TRANSLATION_STAGE_APPROVED,
    build_translation_metadata,
)
from .validation import read_jsonl


def build_source_approval_report(settings) -> dict[str, object]:
    manifest = _runtime_manifest_with_translation_overlay(settings)
    normalized_docs = read_jsonl(settings.normalized_docs_path)
    chunks = read_jsonl(settings.chunks_path)

    sections_by_book: dict[str, list[dict]] = {}
    for row in normalized_docs:
        sections_by_book.setdefault(str(row["book_slug"]), []).append(row)

    chunks_by_book: dict[str, list[dict]] = {}
    for row in chunks:
        chunks_by_book.setdefault(str(row["book_slug"]), []).append(row)

    per_book: list[dict[str, object]] = []
    counts: Counter[str] = Counter()

    for entry in manifest:
        section_rows = sections_by_book.get(entry.book_slug, [])
        chunk_rows = chunks_by_book.get(entry.book_slug, [])
        html_path = settings.raw_html_dir / f"{entry.book_slug}.html"
        raw_html = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
        fallback_detected = bool(LANGUAGE_FALLBACK_RE.search(raw_html))
        hangul_section_ratio = hangul_ratio([str(row.get("text", "")) for row in section_rows])
        hangul_chunk_ratio = hangul_ratio([str(row.get("text", "")) for row in chunk_rows])
        title_english_like = is_english_like_title(entry.title)
        auto_status, auto_reason = classify_content_status(
            section_count=len(section_rows),
            chunk_count=len(chunk_rows),
            hangul_section_ratio=hangul_section_ratio,
            hangul_chunk_ratio=hangul_chunk_ratio,
            title_english_like=title_english_like,
            fallback_detected=fallback_detected,
        )
        content_status, citation_eligible, citation_block_reason, approval_status = (
            resolve_final_content_status(
                entry,
                auto_status=auto_status,
                auto_reason=auto_reason,
            )
        )
        body_language = body_language_guess(
            hangul_chunk_ratio=hangul_chunk_ratio,
            fallback_detected=fallback_detected,
        )
        viewer_strategy = "internal_text"
        gap_lane, gap_priority, gap_action = classify_gap_lane(
            book_slug=entry.book_slug,
            high_value=entry.high_value,
            content_status=content_status,
            fallback_detected=fallback_detected,
        )
        translation_lane = build_translation_metadata(
            entry,
            content_status=content_status,
            citation_eligible=citation_eligible,
            corpus_dir=getattr(settings, "corpus_dir", None),
        )

        record = {
            "product_slug": entry.product_slug,
            "ocp_version": entry.ocp_version,
            "docs_language": entry.docs_language,
            "source_kind": entry.source_kind,
            "book_slug": entry.book_slug,
            "title": entry.title,
            "vendor_title": entry.vendor_title or entry.title,
            "high_value": entry.high_value,
            "section_count": len(section_rows),
            "chunk_count": len(chunk_rows),
            "hangul_section_ratio": hangul_section_ratio,
            "hangul_chunk_ratio": hangul_chunk_ratio,
            "title_english_like": title_english_like,
            "fallback_detected": fallback_detected,
            "body_language_guess": body_language,
            "content_status": content_status,
            "citation_eligible": citation_eligible,
            "citation_block_reason": citation_block_reason,
            "viewer_strategy": viewer_strategy,
            "approval_status": approval_status,
            "approval_notes": entry.approval_notes,
            "source_fingerprint": entry.source_fingerprint,
            "index_url": entry.index_url,
            "source_url": entry.source_url,
            "resolved_source_url": entry.resolved_source_url,
            "resolved_language": entry.resolved_language,
            "source_state": entry.source_state,
            "source_state_reason": entry.source_state_reason,
            "catalog_source_label": entry.catalog_source_label,
            "viewer_path": entry.viewer_path,
            "gap_lane": gap_lane,
            "gap_priority": gap_priority,
            "gap_action": gap_action,
            "translation_lane": translation_lane,
        }
        counts[content_status] += 1
        per_book.append(record)

    per_book.sort(
        key=lambda item: (
            CONTENT_STATUS_SORT_ORDER.get(str(item["content_status"]), 9),
            -int(bool(item["high_value"])),
            str(item["book_slug"]),
        )
    )

    high_value_issues = [
        item for item in per_book if item["high_value"] and item["content_status"] != CONTENT_STATUS_APPROVED_KO
    ]
    gap_lane_counts = Counter(str(item["gap_lane"]) for item in high_value_issues)

    return {
        "summary": {
            "book_count": len(per_book),
            "approved_ko_count": counts[CONTENT_STATUS_APPROVED_KO],
            "translated_ko_draft_count": counts[CONTENT_STATUS_TRANSLATED_KO_DRAFT],
            "mixed_count": counts[CONTENT_STATUS_MIXED],
            "en_only_count": counts[CONTENT_STATUS_EN_ONLY],
            "blocked_count": counts[CONTENT_STATUS_BLOCKED],
            "high_value_issue_count": len(high_value_issues),
        },
        "policy": {
            "product_scope": "ocp_playbook_studio",
            "primary_source": "docs.redhat.com published Korean html-single",
            "change_feed_candidate": "github.com/openshift/openshift-docs",
            "citation_default_statuses": list(CITATION_ELIGIBLE_STATUSES),
            "translation_lane_statuses": [CONTENT_STATUS_TRANSLATED_KO_DRAFT],
        },
        "gap_summary": {
            "translation_first_count": gap_lane_counts[LANE_TRANSLATION_FIRST],
            "manual_review_first_count": gap_lane_counts[LANE_MANUAL_REVIEW_FIRST],
            "other_gap_count": len(high_value_issues)
            - gap_lane_counts[LANE_TRANSLATION_FIRST]
            - gap_lane_counts[LANE_MANUAL_REVIEW_FIRST],
        },
        "high_value_issues": high_value_issues,
        "books": per_book,
    }


def _entry_identity(entry: SourceManifestEntry) -> tuple[str, str, str, str]:
    return (
        entry.ocp_version,
        entry.docs_language,
        entry.source_kind,
        entry.book_slug,
    )


def _runtime_manifest_with_translation_overlay(settings) -> list[SourceManifestEntry]:
    manifest = runtime_catalog_entries(read_manifest(settings.source_catalog_path), settings)
    translation_manifest_path = getattr(settings, "translation_draft_manifest_path", None)
    if translation_manifest_path is None or not Path(translation_manifest_path).exists():
        return manifest

    overlays = read_manifest(Path(translation_manifest_path))
    overlay_map = {_entry_identity(entry): entry for entry in overlays}
    merged: list[SourceManifestEntry] = []
    seen = set()
    for entry in manifest:
        key = _entry_identity(entry)
        merged.append(overlay_map.get(key, entry))
        seen.add(key)
    for entry in overlays:
        key = _entry_identity(entry)
        if key not in seen:
            merged.append(entry)
    return merged


def build_translation_lane_report(settings) -> dict[str, object]:
    approval_report = build_source_approval_report(settings)
    books = list(approval_report["books"])
    stage_counts: Counter[str] = Counter(
        str(item.get("translation_lane", {}).get("stage", "unknown")) for item in books
    )
    active_queue = [
        item
        for item in books
        if str(item.get("translation_lane", {}).get("stage", "")) != TRANSLATION_STAGE_APPROVED
    ]
    return {
        "summary": {
            "book_count": len(books),
            "approved_ko_count": stage_counts[TRANSLATION_STAGE_APPROVED],
            "translated_ko_draft_count": stage_counts[CONTENT_STATUS_TRANSLATED_KO_DRAFT],
            "translation_required_count": stage_counts[CONTENT_STATUS_EN_ONLY],
            "mixed_review_count": stage_counts["mixed_review"],
            "blocked_count": stage_counts[CONTENT_STATUS_BLOCKED],
            "active_queue_count": len(active_queue),
        },
        "policy": {
            "lane_flow": [
                CONTENT_STATUS_EN_ONLY,
                CONTENT_STATUS_TRANSLATED_KO_DRAFT,
                CONTENT_STATUS_APPROVED_KO,
            ],
            "runtime_gate_statuses": list(CITATION_ELIGIBLE_STATUSES),
            "translation_default_target_language": getattr(settings, "docs_language", "ko"),
        },
        "active_queue": active_queue,
        "books": books,
    }


def build_corpus_gap_report(settings) -> dict[str, object]:
    approval_report = build_source_approval_report(settings)
    high_value_issues = list(approval_report["high_value_issues"])
    ordered_issues = sorted(
        high_value_issues,
        key=lambda item: (
            int(item["gap_priority"]),
            str(item["book_slug"]),
        ),
    )

    translation_first = [item for item in ordered_issues if item["gap_lane"] == LANE_TRANSLATION_FIRST]
    manual_review_first = [item for item in ordered_issues if item["gap_lane"] == LANE_MANUAL_REVIEW_FIRST]
    remaining = [
        item
        for item in ordered_issues
        if item["gap_lane"] not in {LANE_TRANSLATION_FIRST, LANE_MANUAL_REVIEW_FIRST}
    ]

    return {
        "summary": {
            "high_value_issue_count": len(ordered_issues),
            "translation_first_count": len(translation_first),
            "manual_review_first_count": len(manual_review_first),
            "remaining_gap_count": len(remaining),
        },
        "translation_first": translation_first,
        "manual_review_first": manual_review_first,
        "remaining_gaps": remaining,
    }


def build_approved_manifest(
    settings,
    *,
    allowed_statuses: tuple[str, ...] = (CONTENT_STATUS_APPROVED_KO,),
) -> list[SourceManifestEntry]:
    approval_report = build_source_approval_report(settings)
    books = approval_report["books"]
    entries: list[SourceManifestEntry] = []

    for item in books:
        if item["content_status"] not in allowed_statuses:
            continue
        entries.append(
            SourceManifestEntry(
                product_slug=str(item.get("product_slug", "openshift_container_platform")),
                ocp_version=str(item.get("ocp_version", getattr(settings, "ocp_version", "4.20"))),
                docs_language=str(item.get("docs_language", getattr(settings, "docs_language", "ko"))),
                source_kind=str(item.get("source_kind", "html-single")),
                book_slug=str(item["book_slug"]),
                title=str(item["title"]),
                index_url=str(item.get("index_url", "")),
                source_url=str(item["source_url"]),
                resolved_source_url=str(item.get("resolved_source_url", item["source_url"])),
                resolved_language=str(item.get("resolved_language", item.get("docs_language", getattr(settings, "docs_language", "ko")))),
                source_state=str(item.get("source_state", "published_native")),
                source_state_reason=str(item.get("source_state_reason", "")),
                catalog_source_label=str(item.get("catalog_source_label", "docs.redhat.com published OCP html-single catalog")),
                viewer_path=str(item["viewer_path"]),
                high_value=bool(item["high_value"]),
                vendor_title=str(item["vendor_title"]),
                content_status=str(item["content_status"]),
                citation_eligible=bool(item["citation_eligible"]),
                citation_block_reason=str(item["citation_block_reason"]),
                viewer_strategy=str(item["viewer_strategy"]),
                body_language_guess=str(item["body_language_guess"]),
                hangul_section_ratio=float(item["hangul_section_ratio"]),
                hangul_chunk_ratio=float(item["hangul_chunk_ratio"]),
                fallback_detected=bool(item["fallback_detected"]),
                source_fingerprint=str(item["source_fingerprint"]),
                approval_status=str(item["approval_status"]),
                approval_notes=str(item["approval_notes"]),
            )
        )
    return entries


def write_approved_manifest(
    path: Path,
    entries: list[SourceManifestEntry],
) -> None:
    write_manifest(path, entries)
