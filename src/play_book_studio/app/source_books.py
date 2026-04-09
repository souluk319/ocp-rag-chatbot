"""source viewer / canonical source book / intake book helper."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from play_book_studio.config.settings import load_settings
from play_book_studio.intake import DocSourceRequest, DocToBookDraftStore, DocToBookPlanner
from play_book_studio.intake.service import evaluate_canonical_book_quality

from .presenters import (
    _core_pack_payload,
    _default_doc_to_book_summary,
    _load_normalized_sections,
    _manifest_entry_for_book,
)
from .viewers import (
    _build_study_section_cards,
    _parse_viewer_path,
    _render_study_viewer_html,
)


def _playbook_book_path(root_dir: Path, book_slug: str) -> Path:
    settings = load_settings(root_dir)
    return settings.playbook_books_dir / f"{book_slug}.json"


def _load_playbook_book(root_dir: Path, book_slug: str) -> dict[str, Any] | None:
    path = _playbook_book_path(root_dir, book_slug)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=8)
def internal_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None

    book_slug, target_anchor = parsed
    playbook_book = _load_playbook_book(root_dir, book_slug)
    if playbook_book is not None:
        sections = [dict(section) for section in (playbook_book.get("sections") or []) if isinstance(section, dict)]
        if not sections:
            return None
        book_title = str(playbook_book.get("title") or book_slug)
        source_url = str(playbook_book.get("source_uri") or "")
        summary = "정리된 AST 기준으로 관련 구간을 보여줍니다."
    else:
        settings = load_settings(root_dir)
        normalized_docs_path = settings.normalized_docs_path
        if not normalized_docs_path.exists():
            return None

        sections_by_book = _load_normalized_sections(
            str(normalized_docs_path),
            normalized_docs_path.stat().st_mtime_ns,
        )
        sections = sections_by_book.get(book_slug) or []
        if not sections:
            return None

        first_row = sections[0]
        book_title = str(first_row.get("book_title") or book_slug)
        source_url = str(first_row.get("source_url") or "")
        summary = "정리된 본문 기준으로 관련 구간을 보여줍니다."

    cards = _build_study_section_cards(sections, target_anchor=target_anchor)
    return _render_study_viewer_html(
        title=book_title,
        source_url=source_url,
        cards=cards,
        section_count=len(sections),
        eyebrow="Reference Viewer",
        summary=summary,
    )


def parse_doc_to_book_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    parsed = urlparse((viewer_path or "").strip())
    request_path = parsed.path.strip()
    prefix = "/docs/intake/"
    if not request_path.startswith(prefix):
        return None
    remainder = request_path[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) != 2 or parts[1] != "index.html":
        return None
    return parts[0], parsed.fragment.strip()


def load_doc_to_book_book(root_dir: Path, draft_id: str) -> dict[str, Any] | None:
    record = DocToBookDraftStore(root_dir).get(draft_id)
    if record is None or not record.canonical_book_path.strip():
        return None
    canonical_path = Path(record.canonical_book_path)
    if not canonical_path.exists():
        return None
    payload = json.loads(canonical_path.read_text(encoding="utf-8"))
    payload["draft_id"] = record.draft_id
    payload["target_viewer_path"] = f"/docs/intake/{record.draft_id}/index.html"
    payload["target_anchor"] = payload.get("target_anchor") or ""
    payload["source_origin_url"] = f"/api/doc-to-book/captured?draft_id={record.draft_id}"
    payload.setdefault("source_collection", record.plan.source_collection)
    payload.setdefault("pack_id", record.plan.pack_id)
    payload.setdefault("pack_label", record.plan.pack_label)
    payload.setdefault("inferred_product", record.plan.inferred_product)
    payload.setdefault("inferred_version", record.plan.inferred_version)
    payload.update(evaluate_canonical_book_quality(payload))
    return payload


def internal_doc_to_book_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_doc_to_book_viewer_path(viewer_path)
    if parsed is None:
        return None

    draft_id, target_anchor = parsed
    canonical_book = load_doc_to_book_book(root_dir, draft_id)
    if canonical_book is None:
        return None

    sections = list(canonical_book.get("sections") or [])
    if not sections:
        return None
    cards = _build_study_section_cards(sections, target_anchor=target_anchor)
    base_summary = _default_doc_to_book_summary(canonical_book)
    quality_summary = str(canonical_book.get("quality_summary") or "").strip()
    summary = f"{base_summary} {quality_summary}".strip() if quality_summary else base_summary
    if str(canonical_book.get("quality_status") or "ready") != "ready":
        summary = f"{summary} 이 자산은 아직 review needed 상태입니다."
    return _render_study_viewer_html(
        title=str(canonical_book.get("title") or draft_id),
        source_url=str(canonical_book.get("source_origin_url") or canonical_book.get("source_uri") or ""),
        cards=cards,
        section_count=len(sections),
        eyebrow="Doc-to-Book Study Viewer",
        summary=summary,
    )


def canonical_source_book(root_dir: Path, viewer_path: str) -> dict[str, Any] | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None

    book_slug, target_anchor = parsed
    playbook_book = _load_playbook_book(root_dir, book_slug)
    if playbook_book is not None:
        settings = load_settings(root_dir)
        playbook_book["target_anchor"] = target_anchor
        playbook_book.update(_core_pack_payload(version=settings.ocp_version, language=settings.docs_language))
        return playbook_book

    settings = load_settings(root_dir)
    normalized_docs_path = settings.normalized_docs_path
    if not normalized_docs_path.exists():
        return None

    sections_by_book = _load_normalized_sections(
        str(normalized_docs_path),
        normalized_docs_path.stat().st_mtime_ns,
    )
    rows = sections_by_book.get(book_slug) or []
    if not rows:
        return None

    first_row = rows[0]
    manifest_entry = _manifest_entry_for_book(root_dir, book_slug)
    request = DocSourceRequest(
        source_type="web",
        uri=str(first_row.get("source_url") or manifest_entry.get("source_url") or ""),
        title=str(first_row.get("book_title") or manifest_entry.get("title") or book_slug),
        language_hint="ko",
    )
    canonical_book = DocToBookPlanner().build_canonical_book(rows, request=request)
    payload = canonical_book.to_dict()
    payload["target_anchor"] = target_anchor
    payload.update(_core_pack_payload(version=settings.ocp_version, language=settings.docs_language))
    return payload


def list_doc_to_book_drafts(root_dir: Path) -> dict[str, Any]:
    drafts: list[dict[str, Any]] = []
    store = DocToBookDraftStore(root_dir)
    for record in store.list():
        summary = record.to_summary()
        if record.canonical_book_path.strip():
            payload = load_doc_to_book_book(root_dir, record.draft_id)
            if payload is not None:
                summary["quality_status"] = payload.get("quality_status")
                summary["quality_score"] = payload.get("quality_score")
                summary["quality_summary"] = payload.get("quality_summary")
                summary["quality_flags"] = payload.get("quality_flags")
        drafts.append(summary)
    return {"drafts": drafts}


__all__ = [
    "canonical_source_book",
    "internal_doc_to_book_viewer_html",
    "internal_viewer_html",
    "list_doc_to_book_drafts",
    "load_doc_to_book_book",
    "parse_doc_to_book_viewer_path",
]
