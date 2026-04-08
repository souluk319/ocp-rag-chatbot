from __future__ import annotations

# captured source에서 canonical study asset을 조립하는 web/pdf 빌더 모음.

from collections.abc import Callable
from pathlib import Path

from play_book_studio.ingestion.models import SourceManifestEntry
from play_book_studio.ingestion.normalize import extract_sections

from ..models import DocToBookDraftRecord
from ..planner import DocToBookPlanner
from .pdf import (
    extract_pdf_markdown_with_docling,
    extract_pdf_outline,
    extract_pdf_pages,
)
from .pdf_rows import (
    _build_pdf_rows,
    _build_pdf_rows_from_docling_markdown,
    _docling_korean_quality_ok,
)


def build_canonical_book(
    record: DocToBookDraftRecord,
    *,
    extract_pdf_markdown_with_docling_fn: Callable[[Path], str] = extract_pdf_markdown_with_docling,
    extract_pdf_outline_fn: Callable[[Path], list] = extract_pdf_outline,
    extract_pdf_pages_fn: Callable[[Path], list[str]] = extract_pdf_pages,
):
    if record.request.source_type == "pdf":
        return _build_pdf_canonical_book(
            record,
            extract_pdf_markdown_with_docling_fn=extract_pdf_markdown_with_docling_fn,
            extract_pdf_outline_fn=extract_pdf_outline_fn,
            extract_pdf_pages_fn=extract_pdf_pages_fn,
        )
    if record.request.source_type == "web":
        return _build_web_canonical_book(record)
    raise ValueError("지원하지 않는 source_type입니다.")


def _build_web_canonical_book(record: DocToBookDraftRecord):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")

    html = capture_path.read_text(encoding="utf-8")
    manifest_entry = SourceManifestEntry(
        book_slug=record.plan.book_slug,
        title=record.plan.title,
        source_url=record.request.uri,
        viewer_path=f"/docs/intake/{record.draft_id}/index.html",
        high_value=False,
        viewer_strategy="internal_text",
        body_language_guess=record.request.language_hint,
        approval_status="derived",
    )
    sections = extract_sections(html, manifest_entry)
    if not sections:
        raise ValueError("capture한 문서에서 canonical section을 만들지 못했습니다.")
    rows = [section.to_dict() for section in sections]
    return DocToBookPlanner().build_canonical_book(rows, request=record.request)


def _build_pdf_canonical_book(
    record: DocToBookDraftRecord,
    *,
    extract_pdf_markdown_with_docling_fn: Callable[[Path], str],
    extract_pdf_outline_fn: Callable[[Path], list],
    extract_pdf_pages_fn: Callable[[Path], list[str]],
):
    capture_path = Path(record.capture_artifact_path)
    if not capture_path.exists():
        raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
    try:
        markdown = extract_pdf_markdown_with_docling_fn(capture_path)
        markdown_rows = _build_pdf_rows_from_docling_markdown(markdown, record)
        # Quality gate: docling sometimes merges Korean characters without spaces
        # (e.g. "컨트롤플레인정보"). Detect and fall back to pypdf in that case.
        if markdown_rows and _docling_korean_quality_ok(markdown_rows):
            return DocToBookPlanner().build_canonical_book(markdown_rows, request=record.request)
    except Exception:
        pass
    pages = extract_pdf_pages_fn(capture_path)
    outline = extract_pdf_outline_fn(capture_path)
    rows = _build_pdf_rows(pages, record, outline=outline)
    if not rows:
        raise ValueError("PDF에서 canonical section을 만들지 못했습니다.")
    return DocToBookPlanner().build_canonical_book(rows, request=record.request)
