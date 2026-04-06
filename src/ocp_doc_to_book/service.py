from __future__ import annotations

import re
from pathlib import PurePosixPath
from urllib.parse import urlparse

from .ingestion import resolve_pdf_capture, resolve_web_capture_url
from .models import CanonicalBook, CanonicalBookDraft, CanonicalSection, DocSourceRequest


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9가-힣]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "untitled-book"


def _infer_title(request: DocSourceRequest) -> str:
    if request.title.strip():
        return request.title.strip()

    if request.source_type == "pdf":
        path = PurePosixPath(request.uri.replace("\\", "/"))
        return path.stem or "PDF source"

    parsed = urlparse(request.uri)
    if parsed.path.strip("/"):
        return PurePosixPath(parsed.path).name or parsed.netloc or "Web source"
    return parsed.netloc or "Web source"


def _detect_block_kinds(text: str) -> tuple[str, ...]:
    kinds: list[str] = []
    normalized = text or ""
    if normalized.strip():
        kinds.append("paragraph")
    if "[CODE]" in normalized and "[/CODE]" in normalized:
        kinds.append("code")
    if "[TABLE]" in normalized and "[/TABLE]" in normalized:
        kinds.append("table")
    return tuple(kinds)


def _section_path_label(section_path: tuple[str, ...], heading: str) -> str:
    if section_path:
        return " > ".join(part for part in section_path if part)
    return heading


def _section_key(book_slug: str, anchor: str, ordinal: int) -> str:
    if anchor.strip():
        return f"{book_slug}:{anchor.strip()}"
    return f"{book_slug}:section-{ordinal}"


class DocToBookPlanner:
    def plan(self, request: DocSourceRequest) -> CanonicalBookDraft:
        title = _infer_title(request)
        slug = _slugify(title)

        if request.source_type == "web":
            acquisition_uri, capture_strategy = resolve_web_capture_url(request.uri)
            acquisition_step = "Resolve the source URL and prefer an html-single snapshot before parsing."
            notes = (
                "Web sources should preserve original chapter/page mapping where possible.",
                "The normalized book view should stay separate from downstream retrieval chunks.",
            )
        else:
            acquisition_uri, capture_strategy = resolve_pdf_capture(request.uri)
            acquisition_step = "Extract text and structural markers from PDF pages before section normalization."
            notes = (
                "PDF sources need a lightweight structure recovery pass before chunk derivation.",
                "Page numbers can remain as auxiliary metadata until section anchors become reliable.",
            )

        return CanonicalBookDraft(
            book_slug=slug,
            title=title,
            source_type=request.source_type,
            source_uri=request.uri,
            acquisition_uri=acquisition_uri,
            capture_strategy=capture_strategy,
            acquisition_step=acquisition_step,
            normalization_step="Build canonical sections that preserve headings, anchors, code blocks, and tables.",
            derivation_step="Derive a source-view document first, then retrieval chunks and embeddings as downstream artifacts.",
            notes=notes,
        )

    def build_canonical_book(
        self,
        rows: list[dict[str, object]],
        *,
        request: DocSourceRequest | None = None,
    ) -> CanonicalBook:
        if not rows:
            raise ValueError("rows must not be empty")

        first = rows[0]
        request = request or DocSourceRequest(
            source_type="web",
            uri=str(first.get("source_url") or ""),
            title=str(first.get("book_title") or first.get("book_slug") or ""),
            language_hint="ko",
        )
        draft = self.plan(request)
        book_slug = str(first.get("book_slug") or draft.book_slug)
        title = str(first.get("book_title") or draft.title)
        source_uri = str(first.get("source_url") or request.uri)

        sections: list[CanonicalSection] = []
        for ordinal, row in enumerate(rows, start=1):
            heading = str(row.get("heading") or "").strip() or f"Section {ordinal}"
            anchor = str(row.get("anchor") or "").strip()
            section_path = tuple(
                str(item).strip()
                for item in (row.get("section_path") or [])
                if str(item).strip()
            )
            section_text = str(row.get("text") or "").strip()
            sections.append(
                CanonicalSection(
                    ordinal=ordinal,
                    section_key=_section_key(book_slug, anchor, ordinal),
                    heading=heading,
                    section_level=int(row.get("section_level") or 0),
                    section_path=section_path,
                    section_path_label=_section_path_label(section_path, heading),
                    anchor=anchor,
                    viewer_path=str(row.get("viewer_path") or "").strip(),
                    source_url=str(row.get("source_url") or source_uri).strip(),
                    text=section_text,
                    block_kinds=_detect_block_kinds(section_text),
                )
            )

        return CanonicalBook(
            canonical_model=draft.canonical_model,
            book_slug=book_slug,
            title=title,
            source_type=request.source_type,
            source_uri=source_uri,
            language_hint=request.language_hint,
            source_view_strategy="normalized_sections_v1",
            retrieval_derivation=draft.retrieval_derivation,
            sections=tuple(sections),
            notes=draft.notes,
        )
