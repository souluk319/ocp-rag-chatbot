"""translation_draft manifest를 실제 한국어 draft 산출물로 변환한다."""

from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.canonical import project_playbook_document, write_playbook_documents
from play_book_studio.config.settings import Settings

from .chunking import chunk_sections
from .collector import collect_entry, raw_html_path
from .manifest import read_manifest
from .normalize import extract_document_ast, project_normalized_sections


def _draft_root(settings: Settings) -> Path:
    return settings.silver_ko_dir / "translation_drafts"


def _normalized_docs_path(settings: Settings) -> Path:
    return _draft_root(settings) / "normalized_docs.jsonl"


def _chunks_path(settings: Settings) -> Path:
    return _draft_root(settings) / "chunks.jsonl"


def _playbook_documents_path(settings: Settings) -> Path:
    return _draft_root(settings) / "playbook_documents.jsonl"


def _playbook_books_dir(settings: Settings) -> Path:
    return _draft_root(settings) / "playbooks"


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate_translation_drafts(
    settings: Settings,
    *,
    slugs: list[str] | None = None,
    force_collect: bool = False,
) -> dict[str, object]:
    entries = read_manifest(settings.translation_draft_manifest_path)
    selected = [
        entry for entry in entries
        if not slugs or entry.book_slug in set(slugs)
    ]
    normalized_rows: list[dict[str, object]] = []
    chunk_rows: list[dict[str, object]] = []
    playbook_documents = []
    books: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []

    for entry in selected:
        try:
            collect_entry(entry, settings, force=force_collect)
            html = raw_html_path(settings, entry.book_slug).read_text(encoding="utf-8")
            document = extract_document_ast(html, entry, settings=settings)
            sections = project_normalized_sections(document)
            chunks = chunk_sections(sections, settings)
            playbook_document = project_playbook_document(document)

            normalized_rows.extend(section.to_dict() for section in sections)
            chunk_rows.extend(chunk.to_dict() for chunk in chunks)
            playbook_documents.append(playbook_document)
            books.append(
                {
                    "book_slug": entry.book_slug,
                    "section_count": len(sections),
                    "chunk_count": len(chunks),
                    "title": getattr(document, "title", playbook_document.title),
                    "translation_status": getattr(
                        document,
                        "translation_status",
                        playbook_document.translation_status,
                    ),
                }
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"book_slug": entry.book_slug, "error": str(exc)})

    _write_jsonl(_normalized_docs_path(settings), normalized_rows)
    _write_jsonl(_chunks_path(settings), chunk_rows)
    write_playbook_documents(
        _playbook_documents_path(settings),
        _playbook_books_dir(settings),
        playbook_documents,
    )

    return {
        "summary": {
            "requested_count": len(selected),
            "generated_count": len(books),
            "error_count": len(errors),
            "section_count": len(normalized_rows),
            "chunk_count": len(chunk_rows),
        },
        "books": books,
        "errors": errors,
        "output_targets": {
            "normalized_docs_path": str(_normalized_docs_path(settings)),
            "chunks_path": str(_chunks_path(settings)),
            "playbook_documents_path": str(_playbook_documents_path(settings)),
            "playbook_books_dir": str(_playbook_books_dir(settings)),
        },
    }
