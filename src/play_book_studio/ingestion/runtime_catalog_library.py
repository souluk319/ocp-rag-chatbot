from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Any

from play_book_studio.canonical import project_playbook_document
from play_book_studio.config.settings import Settings

from .chunking import chunk_sections
from .collector import collect_entry, entry_with_collected_metadata, raw_html_path
from .graph_sidecar import write_graph_sidecar
from .manifest import read_manifest, runtime_catalog_entries
from .models import ChunkRecord, SourceManifestEntry
from .normalize import extract_document_ast, project_normalized_sections
from .pipeline import _entry_with_inferred_runtime_status
from .topic_playbooks import DERIVED_PLAYBOOK_SOURCE_TYPES, materialize_derived_playbooks
from .validation import read_jsonl


OFFICIAL_SOURCE_TYPE = "official_doc"


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [dict(row) for row in read_jsonl(path)]


def _write_jsonl_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _playbook_source_type(row: dict[str, Any]) -> str:
    source_metadata = row.get("source_metadata") if isinstance(row.get("source_metadata"), dict) else {}
    return str(source_metadata.get("source_type") or "").strip()


def _retain_non_official_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in rows
        if str(row.get("source_type") or "").strip() != OFFICIAL_SOURCE_TYPE
    ]


def _retain_non_official_non_derived_playbook_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in rows
        if _playbook_source_type(row) not in ({OFFICIAL_SOURCE_TYPE} | DERIVED_PLAYBOOK_SOURCE_TYPES)
    ]


def _cleanup_stale_official_book_files(books_dir: Path, *, expected_slugs: set[str]) -> None:
    if not books_dir.exists():
        return
    for path in books_dir.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if _playbook_source_type(payload) != OFFICIAL_SOURCE_TYPE:
            continue
        if path.stem not in expected_slugs:
            path.unlink()


def _write_official_playbook_payloads(
    books_dir: Path,
    payloads: list[dict[str, Any]],
) -> None:
    books_dir.mkdir(parents=True, exist_ok=True)
    for payload in payloads:
        slug = str(payload.get("book_slug") or "").strip()
        if not slug:
            continue
        (books_dir / f"{slug}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _bm25_row(chunk_row: dict[str, Any]) -> dict[str, Any]:
    chunk_type = str(chunk_row.get("chunk_type", "reference"))
    return {
        "chunk_id": chunk_row["chunk_id"],
        "book_slug": chunk_row["book_slug"],
        "chapter": chunk_row["chapter"],
        "section": chunk_row["section"],
        "anchor": chunk_row["anchor"],
        "source_url": chunk_row["source_url"],
        "viewer_path": chunk_row["viewer_path"],
        "text": chunk_row["text"],
        "section_path": list(chunk_row.get("section_path", [])),
        "chunk_type": chunk_type,
        "source_id": chunk_row["source_id"],
        "source_lane": chunk_row["source_lane"],
        "source_type": chunk_row["source_type"],
        "source_collection": chunk_row["source_collection"],
        "product": chunk_row["product"],
        "version": chunk_row["version"],
        "locale": chunk_row["locale"],
        "translation_status": chunk_row["translation_status"],
        "review_status": chunk_row["review_status"],
        "trust_score": chunk_row["trust_score"],
        "semantic_role": (
            "procedure"
            if chunk_type in {"procedure", "command"}
            else ("concept" if chunk_type == "concept" else "reference")
        ),
        "cli_commands": list(chunk_row.get("cli_commands", [])),
        "error_strings": list(chunk_row.get("error_strings", [])),
        "k8s_objects": list(chunk_row.get("k8s_objects", [])),
        "operator_names": list(chunk_row.get("operator_names", [])),
        "verification_hints": list(chunk_row.get("verification_hints", [])),
    }


def _chunk_records(rows: list[dict[str, Any]]) -> list[ChunkRecord]:
    allowed = {field.name for field in fields(ChunkRecord)}
    records: list[ChunkRecord] = []
    for row in rows:
        payload = {key: value for key, value in row.items() if key in allowed}
        payload["section_path"] = tuple(payload.get("section_path", []))
        payload["cli_commands"] = tuple(payload.get("cli_commands", []))
        payload["error_strings"] = tuple(payload.get("error_strings", []))
        payload["k8s_objects"] = tuple(payload.get("k8s_objects", []))
        payload["operator_names"] = tuple(payload.get("operator_names", []))
        payload["verification_hints"] = tuple(payload.get("verification_hints", []))
        records.append(ChunkRecord(**payload))
    return records


def _runtime_catalog_entries(settings: Settings) -> list[SourceManifestEntry]:
    return runtime_catalog_entries(read_manifest(settings.source_catalog_path), settings)


def materialize_runtime_catalog_library(
    settings: Settings,
    *,
    force_collect: bool = False,
) -> dict[str, Any]:
    entries = _runtime_catalog_entries(settings)

    all_sections = []
    playbook_payloads: list[dict[str, Any]] = []
    processed_slugs: list[str] = []
    collected_slugs: list[str] = []
    errors: list[dict[str, str]] = []
    content_status_counts: dict[str, int] = {}

    for entry in entries:
        try:
            html_path = raw_html_path(settings, entry.book_slug)
            if force_collect or not html_path.exists():
                collect_entry(entry, settings, force=force_collect)
                collected_slugs.append(entry.book_slug)
            runtime_entry = entry_with_collected_metadata(settings, entry)
            html = raw_html_path(settings, entry.book_slug).read_text(encoding="utf-8")
            document = extract_document_ast(html, runtime_entry, settings=settings)
            sections = project_normalized_sections(document)
            inferred_entry = _entry_with_inferred_runtime_status(
                runtime_entry,
                html=html,
                sections=sections,
            )
            if inferred_entry.to_dict() != runtime_entry.to_dict():
                document = extract_document_ast(html, inferred_entry, settings=settings)
                sections = project_normalized_sections(document)
            all_sections.extend(sections)
            playbook_payloads.append(project_playbook_document(document).to_dict())
            processed_slugs.append(entry.book_slug)
            status = str(inferred_entry.content_status or "unknown")
            content_status_counts[status] = content_status_counts.get(status, 0) + 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"book_slug": entry.book_slug, "message": str(exc)})

    official_normalized_rows = [section.to_dict() for section in all_sections]
    official_chunk_rows = [chunk.to_dict() for chunk in chunk_sections(all_sections, settings)]

    retained_normalized_rows = _retain_non_official_rows(_read_jsonl_rows(settings.normalized_docs_path))
    retained_chunk_rows = _retain_non_official_rows(_read_jsonl_rows(settings.chunks_path))
    retained_playbook_rows = _retain_non_official_non_derived_playbook_rows(
        _read_jsonl_rows(settings.playbook_documents_path)
    )

    merged_normalized_rows = retained_normalized_rows + official_normalized_rows
    merged_chunk_rows = retained_chunk_rows + official_chunk_rows
    merged_playbook_rows = retained_playbook_rows + sorted(
        playbook_payloads,
        key=lambda row: str(row.get("book_slug") or ""),
    )

    _write_jsonl_rows(settings.normalized_docs_path, merged_normalized_rows)
    _write_jsonl_rows(settings.chunks_path, merged_chunk_rows)
    _write_jsonl_rows(settings.bm25_corpus_path, [_bm25_row(row) for row in merged_chunk_rows])
    _write_jsonl_rows(settings.playbook_documents_path, merged_playbook_rows)

    official_slugs = {
        str(payload.get("book_slug") or "").strip()
        for payload in playbook_payloads
        if str(payload.get("book_slug") or "").strip()
    }
    _cleanup_stale_official_book_files(settings.playbook_books_dir, expected_slugs=official_slugs)
    _write_official_playbook_payloads(settings.playbook_books_dir, playbook_payloads)

    derived_summary = materialize_derived_playbooks(settings)
    graph_payload = write_graph_sidecar(
        settings,
        chunks=_chunk_records(merged_chunk_rows),
        playbook_documents=_read_jsonl_rows(settings.playbook_documents_path),
    )

    return {
        "runtime_catalog_count": len(entries),
        "processed_count": len(processed_slugs),
        "collected_count": len(collected_slugs),
        "official_playbook_count": len(playbook_payloads),
        "official_section_count": len(official_normalized_rows),
        "official_chunk_count": len(official_chunk_rows),
        "content_status_counts": dict(sorted(content_status_counts.items())),
        "derived_summary": derived_summary,
        "graph_book_count": int(graph_payload.get("book_count", 0) or 0),
        "graph_relation_count": int(graph_payload.get("relation_count", 0) or 0),
        "errors": errors,
    }
