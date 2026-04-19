"""data_control_room library aggregation functions."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.topic_playbooks import (
    DERIVED_PLAYBOOK_SOURCE_TYPES,
    OPERATION_PLAYBOOK_SOURCE_TYPE,
    TOPIC_PLAYBOOK_SOURCE_TYPE,
    TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE,
)

POLICY_OVERLAY_BOOK_SOURCE_TYPE = "policy_overlay_book"
SYNTHESIZED_PLAYBOOK_SOURCE_TYPE = "synthesized_playbook"
DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPES = (
    TOPIC_PLAYBOOK_SOURCE_TYPE,
    OPERATION_PLAYBOOK_SOURCE_TYPE,
    TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE,
    POLICY_OVERLAY_BOOK_SOURCE_TYPE,
    SYNTHESIZED_PLAYBOOK_SOURCE_TYPE,
)
DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPE_SET = frozenset(
    set(DERIVED_PLAYBOOK_SOURCE_TYPES) | {POLICY_OVERLAY_BOOK_SOURCE_TYPE, SYNTHESIZED_PLAYBOOK_SOURCE_TYPE}
)
PLAYBOOK_LIBRARY_FAMILY_LABELS = {
    TOPIC_PLAYBOOK_SOURCE_TYPE: "토픽 플레이북",
    OPERATION_PLAYBOOK_SOURCE_TYPE: "운용 플레이북",
    TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE: "트러블슈팅 플레이북",
    POLICY_OVERLAY_BOOK_SOURCE_TYPE: "정책 오버레이",
    SYNTHESIZED_PLAYBOOK_SOURCE_TYPE: "종합 플레이북",
}


def _customer_pack_draft_id_from_book(book: dict[str, Any]) -> str:
    viewer_path = str(book.get("viewer_path") or "").strip()
    prefix = "/playbooks/customer-packs/"
    if viewer_path.startswith(prefix):
        remainder = viewer_path[len(prefix) :]
        parts = [part for part in remainder.split("/") if part]
        if parts:
            return str(parts[0]).strip()
    slug = str(book.get("book_slug") or "").strip()
    return slug.split("--", 1)[0].strip() if "--" in slug else ""


def _apply_customer_pack_runtime_truth(
    books: list[dict[str, Any]],
    *,
    draft_records_by_id: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for book in books:
        entry = dict(book)
        draft_id = _customer_pack_draft_id_from_book(entry)
        record = draft_records_by_id.get(draft_id) if draft_id else None
        if record is not None:
            entry["source_lane"] = str(entry.get("source_lane") or getattr(record, "source_lane", "") or "customer_source_first_pack")
            entry["approval_state"] = str(entry.get("approval_state") or getattr(record, "approval_state", "") or "unreviewed")
            entry["publication_state"] = str(entry.get("publication_state") or getattr(record, "publication_state", "") or "draft")
            entry["parser_backend"] = str(entry.get("parser_backend") or getattr(record, "parser_backend", "") or "customer_pack_normalize_service")
            entry["boundary_truth"] = str(entry.get("boundary_truth") or "private_customer_pack_runtime")
            entry["runtime_truth_label"] = str(entry.get("runtime_truth_label") or "Customer Source-First Pack")
            entry["boundary_badge"] = str(entry.get("boundary_badge") or "Private Pack Runtime")
        items.append(entry)
    return items


def _aggregate_corpus_books(
    rows: list[dict[str, Any]],
    *,
    manifest_by_slug: dict[str, dict[str, Any]],
    known_books: dict[str, dict[str, Any]],
    grade_label: Any,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        slug = str(row.get("book_slug") or "").strip()
        if not slug:
            continue
        title = str(row.get("book_title") or "") or str(known_books.get(slug, {}).get("title") or "") or str(manifest_by_slug.get(slug, {}).get("title") or "") or slug
        bucket = grouped.setdefault(
            slug,
            {
                "book_slug": slug,
                "title": title,
                "grade": grade_label(known_books.get(slug, {})) if slug in known_books else "Gold" if slug in manifest_by_slug else "Bronze",
                "chunk_count": 0,
                "token_total": 0,
                "command_chunk_count": 0,
                "error_chunk_count": 0,
                "anchors": set(),
                "chunk_types": Counter(),
                "source_type": str(row.get("source_type") or manifest_by_slug.get(slug, {}).get("source_type") or ""),
                "source_lane": str(row.get("source_lane") or manifest_by_slug.get(slug, {}).get("source_lane") or ""),
                "review_status": str(row.get("review_status") or manifest_by_slug.get(slug, {}).get("review_status") or ""),
                "updated_at": str(row.get("updated_at") or manifest_by_slug.get(slug, {}).get("updated_at") or ""),
                "viewer_path": str(row.get("viewer_path") or manifest_by_slug.get(slug, {}).get("viewer_path") or ""),
                "source_url": str(row.get("source_url") or known_books.get(slug, {}).get("source_url") or manifest_by_slug.get(slug, {}).get("source_url") or ""),
                "materialized": True,
            },
        )
        bucket["chunk_count"] += 1
        bucket["token_total"] += int(row.get("token_count") or 0)
        if row.get("cli_commands"):
            bucket["command_chunk_count"] += 1
        if row.get("error_strings"):
            bucket["error_chunk_count"] += 1
        anchor_id = str(row.get("anchor_id") or row.get("anchor") or "").strip()
        if anchor_id:
            bucket["anchors"].add(anchor_id)
        bucket["chunk_types"][str(row.get("chunk_type") or "unknown").strip() or "unknown"] += 1
    for slug, entry in manifest_by_slug.items():
        grouped.setdefault(
            slug,
            {
                "book_slug": slug,
                "title": str(entry.get("title") or slug),
                "grade": grade_label(known_books.get(slug, {})) if slug in known_books else "Gold",
                "chunk_count": 0,
                "token_total": 0,
                "command_chunk_count": 0,
                "error_chunk_count": 0,
                "anchors": set(),
                "chunk_types": Counter(),
                "source_type": str(entry.get("source_type") or ""),
                "source_lane": str(entry.get("source_lane") or ""),
                "review_status": str(entry.get("review_status") or ""),
                "updated_at": str(entry.get("updated_at") or ""),
                "viewer_path": str(entry.get("viewer_path") or ""),
                "source_url": str(known_books.get(slug, {}).get("source_url") or entry.get("source_url") or ""),
                "materialized": False,
            },
        )
    items: list[dict[str, Any]] = []
    for entry in grouped.values():
        chunk_types = entry.pop("chunk_types")
        anchors = entry.pop("anchors")
        items.append({**entry, "anchor_count": len(anchors), "chunk_type_breakdown": dict(sorted(chunk_types.items()))})
    return sorted(items, key=lambda item: (-int(item["chunk_count"]), str(item["book_slug"])))


def _aggregate_playbooks(
    files: list[Path],
    *,
    manifest_by_slug: dict[str, dict[str, Any]],
    known_books: dict[str, dict[str, Any]],
    grade_label: Any,
    safe_read_json: Any,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for path in files:
        payload = safe_read_json(path)
        slug = str(payload.get("asset_slug") or payload.get("book_slug") or path.stem).strip()
        if not slug:
            continue
        sections = payload.get("sections")
        if not isinstance(sections, list):
            sections = []
        section_roles = Counter()
        block_kinds = Counter()
        for section in sections:
            if not isinstance(section, dict):
                continue
            section_roles[str(section.get("semantic_role") or "unknown").strip() or "unknown"] += 1
            for block in section.get("blocks") or []:
                if isinstance(block, dict):
                    block_kinds[str(block.get("kind") or "unknown").strip() or "unknown"] += 1
        source_metadata = payload.get("source_metadata") if isinstance(payload.get("source_metadata"), dict) else {}
        playbook_family = str(payload.get("playbook_family") or "").strip()
        source_type = str((playbook_family if playbook_family in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPE_SET else (source_metadata.get("source_type") or payload.get("source_type") or "")) or "")
        known = known_books.get(slug, {})
        manifest = manifest_by_slug.get(slug, {})
        grouped[slug] = {
            "book_slug": slug,
            "title": str(payload.get("title") or payload.get("book_title") or slug),
            "grade": grade_label(known) if known else "Gold" if manifest else "Bronze",
            "translation_status": str(payload.get("translation_status") or known.get("content_status") or ""),
            "review_status": str(payload.get("review_status") or known.get("review_status") or ""),
            "source_type": source_type or str(known.get("source_type") or manifest.get("source_type") or ""),
            "source_lane": str(source_metadata.get("source_lane") or known.get("source_lane") or manifest.get("source_lane") or ""),
            "source_collection": str(payload.get("source_collection") or source_metadata.get("source_collection") or ""),
            "section_count": len(sections),
            "anchor_count": len(payload.get("anchor_map") or {}),
            "code_block_count": int(block_kinds.get("code", 0)),
            "procedure_block_count": int(block_kinds.get("procedure", 0)),
            "paragraph_block_count": int(block_kinds.get("paragraph", 0)),
            "semantic_role_breakdown": dict(sorted(section_roles.items())),
            "block_kind_breakdown": dict(sorted(block_kinds.items())),
            "legal_notice_url": str(payload.get("legal_notice_url") or source_metadata.get("legal_notice_url") or ""),
            "viewer_path": str(payload.get("target_viewer_path") or payload.get("viewer_path") or manifest.get("viewer_path") or known.get("viewer_path") or ""),
            "source_url": str(payload.get("source_origin_url") or payload.get("source_uri") or payload.get("source_url") or ""),
            "updated_at": str(source_metadata.get("updated_at") or known.get("updated_at") or manifest.get("updated_at") or ""),
            "materialized": True,
        }
    for slug, entry in manifest_by_slug.items():
        grouped.setdefault(
            slug,
            {
                "book_slug": slug,
                "title": str(entry.get("title") or slug),
                "grade": grade_label(known_books.get(slug, {})) if slug in known_books else "Gold",
                "translation_status": str(entry.get("content_status") or ""),
                "review_status": str(entry.get("review_status") or ""),
                "source_type": str(entry.get("source_type") or ""),
                "source_lane": str(entry.get("source_lane") or ""),
                "section_count": 0,
                "anchor_count": 0,
                "code_block_count": 0,
                "procedure_block_count": 0,
                "paragraph_block_count": 0,
                "semantic_role_breakdown": {},
                "block_kind_breakdown": {},
                "legal_notice_url": str(entry.get("legal_notice_url") or ""),
                "viewer_path": str(entry.get("viewer_path") or ""),
                "source_url": str(known_books.get(slug, {}).get("source_url") or entry.get("source_url") or ""),
                "updated_at": str(entry.get("updated_at") or ""),
                "materialized": False,
            },
        )
    return sorted(grouped.values(), key=lambda item: (-int(item["section_count"]), str(item["book_slug"])))


def _derived_family_status(family: str, books: list[dict[str, Any]]) -> dict[str, Any]:
    slugs = sorted(str(book.get("book_slug") or "").strip() for book in books if str(book.get("book_slug") or "").strip())
    return {"family": family, "count": len(books), "slugs": slugs, "status": "materialized" if books else "not_emitted", "books": books}


def _library_breakdown(counter: Counter[str]) -> list[dict[str, Any]]:
    return [{"key": key, "count": count} for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))]


def _build_manual_book_library(core_manualbooks: list[dict[str, Any]], extra_manualbooks: list[dict[str, Any]]) -> dict[str, Any]:
    books: list[dict[str, Any]] = []
    source_type_counter: Counter[str] = Counter()
    for group_key, group_label, group_books in (("runtime_core", "런타임 팩", core_manualbooks), ("extra", "확장 북", extra_manualbooks)):
        for book in group_books:
            item = dict(book)
            item["library_group"] = group_key
            item["library_group_label"] = group_label
            books.append(item)
            source_type_counter[str(item.get("source_type") or "unknown").strip() or "unknown"] += 1
    return {
        "total_count": len(books),
        "core_count": len(core_manualbooks),
        "extra_count": len(extra_manualbooks),
        "books": books,
        "group_breakdown": [
            {"key": "runtime_core", "label": "런타임 팩", "count": len(core_manualbooks)},
            {"key": "extra", "label": "확장 북", "count": len(extra_manualbooks)},
        ],
        "source_type_breakdown": _library_breakdown(source_type_counter),
    }


def _build_playbook_library(derived_playbook_family_statuses: dict[str, dict[str, Any]]) -> dict[str, Any]:
    families: list[dict[str, Any]] = []
    books: list[dict[str, Any]] = []
    for family in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPES:
        status = derived_playbook_family_statuses.get(family, {})
        family_books: list[dict[str, Any]] = []
        for book in status.get("books") or []:
            if isinstance(book, dict):
                item = dict(book)
                item["family"] = family
                item["family_label"] = PLAYBOOK_LIBRARY_FAMILY_LABELS.get(family, family)
                family_books.append(item)
        families.append(
            {
                "family": family,
                "family_label": PLAYBOOK_LIBRARY_FAMILY_LABELS.get(family, family),
                "count": len(family_books),
                "status": str(status.get("status") or "not_emitted"),
                "books": family_books,
            }
        )
        books.extend(family_books)
    return {"total_count": len(books), "family_count": sum(1 for family in families if int(family.get("count") or 0) > 0), "families": families, "books": books}


def _apply_viewer_path_fallback(books: list[dict[str, Any]], *, root: Path) -> list[dict[str, Any]]:
    settings = load_settings(root)
    playbook_dir = settings.playbook_books_dir.resolve()
    for book in books:
        if str(book.get("viewer_path") or "").strip():
            continue
        slug = str(book.get("book_slug") or "").strip()
        if slug and (playbook_dir / f"{slug}.json").exists():
            book["viewer_path"] = settings.viewer_path_template.format(slug=slug)
    return books


__all__ = [
    "DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPES",
    "DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPE_SET",
    "OPERATION_PLAYBOOK_SOURCE_TYPE",
    "PLAYBOOK_LIBRARY_FAMILY_LABELS",
    "POLICY_OVERLAY_BOOK_SOURCE_TYPE",
    "SYNTHESIZED_PLAYBOOK_SOURCE_TYPE",
    "TOPIC_PLAYBOOK_SOURCE_TYPE",
    "TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE",
    "_aggregate_corpus_books",
    "_aggregate_playbooks",
    "_apply_customer_pack_runtime_truth",
    "_apply_viewer_path_fallback",
    "_build_manual_book_library",
    "_build_playbook_library",
    "_derived_family_status",
]
