"""translation_draft manifest를 실제 한국어 draft 산출물로 변환한다."""

from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.canonical import project_playbook_document, write_playbook_documents
from play_book_studio.config.settings import Settings

from .chunking import chunk_sections
from .collector import collect_entry, entry_with_collected_metadata, raw_html_path
from .data_quality import build_playbook_reader_grade_audit_for_dirs
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


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _rows_by_slug(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        slug = str(row.get("book_slug", "")).strip()
        if not slug:
            continue
        grouped.setdefault(slug, []).append(row)
    return grouped


def _playbooks_by_slug(path: Path) -> dict[str, dict[str, object]]:
    return {
        str(row.get("book_slug", "")).strip(): row
        for row in _read_jsonl(path)
        if str(row.get("book_slug", "")).strip()
    }


def _materialize_outputs(
    settings: Settings,
    *,
    normalized_by_slug: dict[str, list[dict[str, object]]],
    chunks_by_slug: dict[str, list[dict[str, object]]],
    playbooks_by_slug: dict[str, dict[str, object]],
) -> None:
    normalized_rows = [
        row
        for slug in sorted(normalized_by_slug)
        for row in normalized_by_slug[slug]
    ]
    chunk_rows = [
        row
        for slug in sorted(chunks_by_slug)
        for row in chunks_by_slug[slug]
    ]
    playbook_rows = [playbooks_by_slug[slug] for slug in sorted(playbooks_by_slug)]
    _write_jsonl(_normalized_docs_path(settings), normalized_rows)
    _write_jsonl(_chunks_path(settings), chunk_rows)
    _write_jsonl(_playbook_documents_path(settings), playbook_rows)
    books_dir = _playbook_books_dir(settings)
    books_dir.mkdir(parents=True, exist_ok=True)
    expected_filenames = {f"{slug}.json" for slug in playbooks_by_slug}
    for slug, payload in playbooks_by_slug.items():
        (books_dir / f"{slug}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    for stale_path in books_dir.glob("*.json"):
        if stale_path.name not in expected_filenames:
            stale_path.unlink()


def generate_translation_drafts(
    settings: Settings,
    *,
    slugs: list[str] | None = None,
    force_collect: bool = False,
    force_regenerate: bool = False,
) -> dict[str, object]:
    entries = read_manifest(settings.translation_draft_manifest_path)
    selected = [
        entry for entry in entries
        if not slugs or entry.book_slug in set(slugs)
    ]
    normalized_by_slug = (
        {}
        if force_regenerate
        else _rows_by_slug(_read_jsonl(_normalized_docs_path(settings)))
    )
    chunks_by_slug = (
        {}
        if force_regenerate
        else _rows_by_slug(_read_jsonl(_chunks_path(settings)))
    )
    playbooks_by_slug = (
        {}
        if force_regenerate
        else _playbooks_by_slug(_playbook_documents_path(settings))
    )
    books: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    reused_books: list[str] = []

    for entry in selected:
        if (
            not force_regenerate
            and entry.book_slug in normalized_by_slug
            and entry.book_slug in chunks_by_slug
            and entry.book_slug in playbooks_by_slug
        ):
            playbook_row = playbooks_by_slug[entry.book_slug]
            books.append(
                {
                    "book_slug": entry.book_slug,
                    "section_count": len(normalized_by_slug[entry.book_slug]),
                    "chunk_count": len(chunks_by_slug[entry.book_slug]),
                    "title": str(playbook_row.get("title") or entry.title),
                    "translation_status": str(
                        playbook_row.get("translation_status") or entry.content_status
                    ),
                    "resume_state": "reused",
                }
            )
            reused_books.append(entry.book_slug)
            continue
        try:
            collect_entry(entry, settings, force=force_collect)
            html = raw_html_path(settings, entry.book_slug).read_text(encoding="utf-8")
            runtime_entry = entry_with_collected_metadata(settings, entry)
            document = extract_document_ast(html, runtime_entry, settings=settings)
            sections = project_normalized_sections(document)
            chunks = chunk_sections(sections, settings)
            playbook_document = project_playbook_document(document)

            normalized_by_slug[entry.book_slug] = [section.to_dict() for section in sections]
            chunks_by_slug[entry.book_slug] = [chunk.to_dict() for chunk in chunks]
            playbooks_by_slug[entry.book_slug] = playbook_document.to_dict()
            _materialize_outputs(
                settings,
                normalized_by_slug=normalized_by_slug,
                chunks_by_slug=chunks_by_slug,
                playbooks_by_slug=playbooks_by_slug,
            )
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
                    "resume_state": "generated",
                }
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"book_slug": entry.book_slug, "error": str(exc)})

    manualbook_audit = build_playbook_reader_grade_audit_for_dirs(
        (_playbook_books_dir(settings),)
    )
    normalized_rows = [
        row for slug in sorted(normalized_by_slug) for row in normalized_by_slug[slug]
    ]
    chunk_rows = [
        row for slug in sorted(chunks_by_slug) for row in chunks_by_slug[slug]
    ]

    return {
        "summary": {
            "requested_count": len(selected),
            "generated_count": len(books),
            "reused_count": len(reused_books),
            "error_count": len(errors),
            "section_count": len(normalized_rows),
            "chunk_count": len(chunk_rows),
            "draft_manualbook_failing_book_count": int(
                manualbook_audit.get("failing_book_count", 0)
            ),
        },
        "books": books,
        "errors": errors,
        "draft_manualbook_audit": manualbook_audit,
        "output_targets": {
            "normalized_docs_path": str(_normalized_docs_path(settings)),
            "chunks_path": str(_chunks_path(settings)),
            "playbook_documents_path": str(_playbook_documents_path(settings)),
            "playbook_books_dir": str(_playbook_books_dir(settings)),
        },
    }
