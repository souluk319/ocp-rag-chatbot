from __future__ import annotations

import json
from pathlib import Path

from .chunking import chunk_sections
from .collector import collect_entry, raw_html_path
from .embedding import EmbeddingClient
from .manifest import fetch_docs_index, parse_manifest_entries, read_manifest, write_manifest
from .models import ChunkRecord, NormalizedSection, PipelineLog, SourceManifestEntry
from .normalize import extract_sections
from .qdrant_store import ensure_collection, upsert_chunks
from ocp_rag.shared.settings import HIGH_VALUE_SLUGS, Settings


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _save_log(settings: Settings, log: PipelineLog) -> None:
    settings.preprocessing_log_path.write_text(
        json.dumps(log.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _progress(message: str) -> None:
    print(message, flush=True)


def ensure_manifest(settings: Settings, refresh: bool = False) -> list[SourceManifestEntry]:
    if refresh or not settings.source_manifest_path.exists():
        index_html = fetch_docs_index(settings)
        entries = parse_manifest_entries(index_html, settings)
        write_manifest(settings.source_manifest_path, entries)
        return entries
    return read_manifest(settings.source_manifest_path)


def _select_entries(
    entries: list[SourceManifestEntry], subset: str, limit: int | None
) -> list[SourceManifestEntry]:
    if subset == "high-value":
        selected = [entry for entry in entries if entry.book_slug in HIGH_VALUE_SLUGS]
    else:
        selected = list(entries)
    return selected[:limit] if limit is not None else selected


def run_part1(
    settings: Settings,
    *,
    refresh_manifest: bool = False,
    collect_subset: str = "all",
    process_subset: str = "high-value",
    collect_limit: int | None = None,
    process_limit: int | None = None,
    force_collect: bool = False,
    skip_embeddings: bool = False,
    skip_qdrant: bool = False,
) -> PipelineLog:
    log = PipelineLog()
    log.stage = "manifest"
    entries = ensure_manifest(settings, refresh=refresh_manifest)
    log.manifest_count = len(entries)
    _progress(f"[manifest] entries={len(entries)}")
    _save_log(settings, log)

    collect_entries = _select_entries(entries, collect_subset, collect_limit)
    _progress(f"[collect] target_books={len(collect_entries)} subset={collect_subset}")
    log.stage = "collect"
    for index, entry in enumerate(collect_entries, start=1):
        try:
            collect_entry(entry, settings, force=force_collect)
            log.collected_count += 1
            log.collected_sources.append(entry.book_slug)
            log.upsert_book_stat(entry.book_slug, collected=True, source_url=entry.source_url)
            _progress(f"[collect {index}/{len(collect_entries)}] {entry.book_slug}")
            _save_log(settings, log)
        except Exception as exc:  # noqa: BLE001
            log.add_error("collect", entry.book_slug, str(exc))
            _save_log(settings, log)

    process_entries = _select_entries(entries, process_subset, process_limit)
    all_sections: list[NormalizedSection] = []
    _progress(f"[normalize] target_books={len(process_entries)} subset={process_subset}")
    log.stage = "normalize"
    for index, entry in enumerate(process_entries, start=1):
        try:
            html_path = raw_html_path(settings, entry.book_slug)
            if not html_path.exists():
                collect_entry(entry, settings, force=False)
                log.collected_count += 1
                log.collected_sources.append(entry.book_slug)
            html = html_path.read_text(encoding="utf-8")
            sections = extract_sections(html, entry)
            all_sections.extend(sections)
            log.processed_sources.append(entry.book_slug)
            log.upsert_book_stat(
                entry.book_slug,
                processed=True,
                section_count=len(sections),
                title=entry.title,
                high_value=entry.high_value,
            )
            _progress(
                f"[normalize {index}/{len(process_entries)}] "
                f"{entry.book_slug} sections={len(sections)}"
            )
            _save_log(settings, log)
        except Exception as exc:  # noqa: BLE001
            log.add_error("normalize", entry.book_slug, str(exc))
            _save_log(settings, log)

    log.stage = "write_normalized"
    log.normalized_count = len(all_sections)
    _progress(f"[normalize] total_sections={len(all_sections)}")
    _write_jsonl(settings.normalized_docs_path, [section.to_dict() for section in all_sections])
    _save_log(settings, log)

    log.stage = "chunk"
    chunks: list[ChunkRecord] = chunk_sections(all_sections, settings)
    log.chunk_count = len(chunks)
    chunk_counts: dict[str, int] = {}
    for chunk in chunks:
        chunk_counts[chunk.book_slug] = chunk_counts.get(chunk.book_slug, 0) + 1
    for book_slug, count in chunk_counts.items():
        log.upsert_book_stat(book_slug, chunk_count=count)
    _progress(f"[chunk] total_chunks={len(chunks)}")
    _write_jsonl(settings.chunks_path, [chunk.to_dict() for chunk in chunks])
    _write_jsonl(
        settings.bm25_corpus_path,
        [
            {
                "chunk_id": chunk.chunk_id,
                "book_slug": chunk.book_slug,
                "chapter": chunk.chapter,
                "section": chunk.section,
                "anchor": chunk.anchor,
                "source_url": chunk.source_url,
                "viewer_path": chunk.viewer_path,
                "text": chunk.text,
            }
            for chunk in chunks
        ],
    )
    _save_log(settings, log)

    if chunks and not skip_embeddings:
        try:
            log.stage = "embed"
            client = EmbeddingClient(settings)
            vectors = client.embed_texts(
                (chunk.text for chunk in chunks),
                progress_callback=lambda done, total: (
                    _progress(f"[embed {done}/{total}]"),
                    _save_log(settings, log),
                ),
            )
            log.embedded_count = len(vectors)
            _progress(f"[embed] total_vectors={len(vectors)}")
            _save_log(settings, log)
            if not skip_qdrant:
                log.stage = "qdrant"
                ensure_collection(settings)
                log.qdrant_upserted_count = upsert_chunks(
                    settings,
                    chunks,
                    vectors,
                    progress_callback=lambda done, total: (
                        _progress(f"[qdrant {done}/{total}]"),
                        _save_log(settings, log),
                    ),
                )
                _progress(f"[qdrant] upserted={log.qdrant_upserted_count}")
        except Exception as exc:  # noqa: BLE001
            log.add_error("embed_or_qdrant", "pipeline", str(exc))
            _save_log(settings, log)

    log.stage = "done"
    _save_log(settings, log)
    return log
