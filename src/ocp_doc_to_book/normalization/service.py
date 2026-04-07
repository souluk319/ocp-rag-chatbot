from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from ocp_rag_part1.models import SourceManifestEntry
from ocp_rag_part1.normalize import extract_sections
from ocp_rag_part1.settings import load_settings

from ..books.store import DocToBookDraftStore
from ..models import DocToBookDraftRecord
from ..service import DocToBookPlanner
from .pdf import (
    PdfOutlineEntry,
    extract_pdf_markdown_with_docling,
    extract_pdf_outline,
    extract_pdf_pages,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DocToBookNormalizeService:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.settings = load_settings(self.root_dir)
        self.store = DocToBookDraftStore(self.root_dir)

    def normalize(self, *, draft_id: str) -> DocToBookDraftRecord:
        record = self.store.get(draft_id.strip())
        if record is None:
            raise ValueError("doc-to-book draft를 찾을 수 없습니다.")
        if not record.capture_artifact_path.strip():
            raise ValueError("먼저 capture를 실행해서 source artifact를 확보해야 합니다.")

        try:
            canonical_book = self._build_canonical_book(record)
            book_path = self.settings.doc_to_book_books_dir / f"{record.draft_id}.json"
            book_path.write_text(
                json.dumps(canonical_book.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            record.status = "normalized"
            record.canonical_book_path = str(book_path)
            record.normalized_section_count = len(canonical_book.sections)
            record.normalize_error = ""
        except Exception as exc:  # noqa: BLE001
            record.status = "normalize_failed"
            record.normalize_error = str(exc)
            record.updated_at = _utc_now()
            self.store.save(record)
            raise

        record.updated_at = _utc_now()
        self.store.save(record)
        return record

    def _build_canonical_book(self, record: DocToBookDraftRecord):
        if record.request.source_type == "pdf":
            return self._build_pdf_canonical_book(record)
        if record.request.source_type != "web":
            raise ValueError("지원하지 않는 source_type입니다.")

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

    def _build_pdf_canonical_book(self, record: DocToBookDraftRecord):
        capture_path = Path(record.capture_artifact_path)
        if not capture_path.exists():
            raise FileNotFoundError(f"captured artifact를 찾을 수 없습니다: {capture_path}")
        try:
            markdown = extract_pdf_markdown_with_docling(capture_path)
            markdown_rows = _build_pdf_rows_from_docling_markdown(markdown, record)
            if markdown_rows:
                return DocToBookPlanner().build_canonical_book(markdown_rows, request=record.request)
        except Exception:
            pass
        pages = extract_pdf_pages(capture_path)
        outline = extract_pdf_outline(capture_path)
        rows = _build_pdf_rows(pages, record, outline=outline)
        if not rows:
            raise ValueError("PDF에서 canonical section을 만들지 못했습니다.")
        return DocToBookPlanner().build_canonical_book(rows, request=record.request)


HEADING_PREFIX_RE = re.compile(r"^(?:#{1,6}\s+|\d+(?:\.\d+)*[\.\)]?\s+)")
HEADING_PUNCTUATION_RE = re.compile(r"[\.!\?]|니다$|합니다$|하십시오$|하세요$")
WHITESPACE_RE = re.compile(r"\s+")
PAGE_MARKER_RE = re.compile(r"^(?:page|페이지)\s+\d+$", re.IGNORECASE)
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
ANCHOR_SANITIZE_RE = re.compile(r"[^a-z0-9가-힣]+")
PDF_STRUCTURE_BREAK_RE = re.compile(
    r"(?=(?:\d+\s*장\s*\.|\d+\.\d+(?:\.\d+)*\.|(?:표|그림)\s*\d+\.\d+\.|(?:중요|주의|참고|팁)\b))"
)
PDF_STRUCTURAL_MARKER_RE = re.compile(
    r"(?:\d+\s*장\s*\.|\d+\.\d+(?:\.\d+)*\.|(?:표|그림)\s*\d+\.\d+\.|(?:중요|주의|참고|팁)\b)"
)
PDF_FRONT_MATTER_TITLE_RE = re.compile(
    r"OpenShift Container Platform\s+\d+\.\d+.*?(?:Last Updated:\s*\d{4}-\d{2}-\d{2})?",
    re.IGNORECASE,
)
PDF_TOC_DOT_LEADER_RE = re.compile(r"(?:\.\s*){12,}")
PDF_TRAILING_PAGE_NUMBER_RE = re.compile(r"\s+\d+\s*$")
PDF_TRAILING_CHAPTER_FOOTER_RE = re.compile(
    r"(?:\d+\s*장(?:\s*장)?\s*\.\s*[가-힣A-Za-z0-9\s().:/_-]{8,}?\s+\d+)\s*$"
)
PDF_SKIP_PAGE_RE = re.compile(
    r"^(?:OpenShift Container Platform\s+\d+\.\d+.*|Last Updated:\s*\d{4}-\d{2}-\d{2}|Table of Contents.*|Legal Notice.*)?$",
    re.IGNORECASE,
)
DOCLING_SKIP_HEADINGS = {"legal notice", "table of contents"}
DOCLING_INLINE_HEADINGS = {
    "abstract",
    "사전 요구 사항",
    "프로세스",
    "추가 리소스",
    "중요",
    "참고",
    "작은 정보",
    "출력 예",
    "사용 예",
    "출력",
    "예",
    "spec:",
}
DOCLING_INLINE_HEADINGS_LOWER = {item.lower() for item in DOCLING_INLINE_HEADINGS}


def _build_pdf_rows(
    pages: list[str],
    record: DocToBookDraftRecord,
    *,
    outline: list[PdfOutlineEntry] | None = None,
) -> list[dict[str, object]]:
    if outline:
        outline_rows = _build_pdf_rows_from_outline(pages, outline, record)
        if outline_rows:
            _validate_pdf_rows(outline_rows, page_count=len(pages))
            return outline_rows

    rows: list[dict[str, object]] = []
    book_slug = record.plan.book_slug
    viewer_base = f"/docs/intake/{record.draft_id}/index.html"
    source_url = record.request.uri
    book_title = record.plan.title
    ordinal = 1

    for page_number, page_text in enumerate(pages, start=1):
        page_sections = _segment_pdf_page(page_text)
        if not page_sections:
            continue
        for section_index, (heading, body) in enumerate(page_sections, start=1):
            anchor_seed = heading if heading and not heading.startswith("Page ") else f"page-{page_number}-{section_index}"
            anchor = _pdf_anchor(anchor_seed, ordinal)
            section_path = [f"Page {page_number}"]
            if heading:
                section_path.append(heading)
            rows.append(
                {
                    "book_slug": book_slug,
                    "book_title": book_title,
                    "heading": heading or f"Page {page_number}",
                    "section_level": _infer_pdf_section_level(heading),
                    "section_path": section_path,
                    "anchor": anchor,
                    "source_url": source_url,
                    "viewer_path": f"{viewer_base}#{anchor}",
                    "text": body.strip(),
                }
            )
            ordinal += 1
    _validate_pdf_rows(rows, page_count=len(pages))
    return rows


def _build_pdf_rows_from_docling_markdown(
    markdown: str,
    record: DocToBookDraftRecord,
) -> list[dict[str, object]]:
    sections = _segment_docling_markdown(markdown)
    if not sections:
        return []

    rows: list[dict[str, object]] = []
    stack: list[str] = []
    book_slug = record.plan.book_slug
    viewer_base = f"/docs/intake/{record.draft_id}/index.html"
    source_url = record.request.uri
    book_title = record.plan.title

    for ordinal, (level, heading, body) in enumerate(sections, start=1):
        stack = stack[: level - 1]
        stack.append(heading)
        anchor = _pdf_anchor(heading, ordinal)
        rows.append(
            {
                "book_slug": book_slug,
                "book_title": book_title,
                "heading": heading,
                "section_level": level,
                "section_path": list(stack),
                "anchor": anchor,
                "source_url": source_url,
                "viewer_path": f"{viewer_base}#{anchor}",
                "text": body,
            }
        )

    _validate_pdf_rows(rows, page_count=max(len(rows), 1))
    return rows


def _build_pdf_rows_from_outline(
    pages: list[str],
    outline: list[PdfOutlineEntry],
    record: DocToBookDraftRecord,
) -> list[dict[str, object]]:
    if not pages or not outline:
        return []

    prepared_pages = [_prepare_pdf_page_text(page) for page in pages]
    matched_positions: list[tuple[int, int, int]] = []
    cursor_page = 0
    cursor_offset = 0
    for entry in outline:
        matched = _find_pdf_outline_position(
            prepared_pages,
            entry.title,
            start_page=cursor_page,
            start_offset=cursor_offset,
        )
        if matched is None:
            matched = (cursor_page, cursor_offset, cursor_offset)
        matched_positions.append(matched)
        cursor_page, _, cursor_offset = matched

    rows: list[dict[str, object]] = []
    stack: list[str] = []
    book_slug = record.plan.book_slug
    viewer_base = f"/docs/intake/{record.draft_id}/index.html"
    source_url = record.request.uri
    book_title = record.plan.title

    for ordinal, entry in enumerate(outline, start=1):
        start_page, start_offset, _ = matched_positions[ordinal - 1]
        if ordinal < len(matched_positions):
            end_page, end_offset, _ = matched_positions[ordinal]
        else:
            end_page, end_offset = len(prepared_pages) - 1, len(prepared_pages[-1]) if prepared_pages else 0
        body = _extract_outline_section_body(
            prepared_pages,
            start_page=start_page,
            start_offset=start_offset,
            end_page=end_page,
            end_offset=end_offset,
            current_title=entry.title,
        )
        if not body:
            continue
        level = max(entry.level, 1)
        stack = stack[: level - 1]
        stack.append(entry.title)
        anchor = _pdf_anchor(entry.title, ordinal)
        rows.append(
            {
                "book_slug": book_slug,
                "book_title": book_title,
                "heading": entry.title,
                "section_level": level,
                "section_path": list(stack),
                "anchor": anchor,
                "source_url": source_url,
                "viewer_path": f"{viewer_base}#{anchor}",
                "text": body,
            }
        )

    return rows


def _segment_pdf_page(page_text: str) -> list[tuple[str, str]]:
    prepared = _prepare_pdf_page_text(page_text)
    if not prepared:
        return []
    lines = [line.strip() for line in prepared.splitlines()]
    sections: list[tuple[str, str]] = []
    current_heading = ""
    current_body: list[str] = []

    def flush() -> None:
        nonlocal current_heading, current_body
        body = "\n\n".join(part for part in current_body if part.strip()).strip()
        if current_heading or body:
            heading = current_heading or "Page Summary"
            sections.append((heading, body or heading))
        current_heading = ""
        current_body = []

    for raw_line in lines:
        line = WHITESPACE_RE.sub(" ", raw_line).strip()
        if not line:
            if current_body and current_body[-1]:
                current_body.append("")
            continue
        if PAGE_MARKER_RE.match(line):
            continue
        if _looks_like_pdf_heading(line):
            flush()
            current_heading = _normalize_pdf_heading(line)
            continue
        current_body.append(line)

    flush()
    return [(heading, body) for heading, body in sections if body.strip()]


def _segment_docling_markdown(markdown: str) -> list[tuple[int, str, str]]:
    lines = str(markdown or "").splitlines()
    sections: list[tuple[int, str, str]] = []
    current_heading = ""
    current_level = 0
    body_lines: list[str] = []
    parent_level = 0

    def flush() -> None:
        nonlocal current_heading, current_level, body_lines, parent_level
        heading = current_heading.strip()
        body = _clean_docling_section_body("\n".join(body_lines), heading=heading)
        if heading and body and not _skip_docling_heading(heading):
            sections.append((current_level or 1, heading, body))
            parent_level = current_level or 1
        current_heading = ""
        current_level = 0
        body_lines = []

    for raw_line in lines:
        stripped = raw_line.strip()
        match = MARKDOWN_HEADING_RE.match(stripped)
        if match:
            heading = match.group(2).strip()
            if current_heading and _should_inline_docling_heading(heading):
                if body_lines and body_lines[-1].strip():
                    body_lines.append("")
                body_lines.append(f"### {heading}")
                continue
            flush()
            raw_level = len(match.group(1))
            current_level = _docling_section_level(
                heading,
                raw_level=raw_level,
                parent_level=parent_level,
            )
            current_heading = heading
            continue
        body_lines.append(raw_line.rstrip())

    flush()
    return sections


def _pdf_search_key(text: str) -> str:
    lowered = str(text or "").lower()
    lowered = re.sub(r"\s+", "", lowered)
    lowered = re.sub(r"[^0-9a-z가-힣]+", "", lowered)
    return lowered


def _pdf_title_pattern(title: str) -> re.Pattern[str] | None:
    tokens = [
        re.escape(token)
        for token in re.findall(r"\d+|[A-Za-z]+|[가-힣]+", title)
        if token
    ]
    if not tokens:
        return None
    return re.compile(r"[\s().:/_-]*".join(tokens), re.IGNORECASE)


def _find_pdf_outline_position(
    pages: list[str],
    title: str,
    *,
    start_page: int,
    start_offset: int,
) -> tuple[int, int, int] | None:
    pattern = _pdf_title_pattern(title)
    if pattern is None:
        return None

    for index in range(start_page, len(pages)):
        haystack = pages[index]
        if not haystack.strip():
            continue
        offset = start_offset if index == start_page else 0
        match = pattern.search(haystack, pos=offset)
        if match:
            return index, match.start(), match.end()

    for index in range(0, start_page):
        haystack = pages[index]
        if not haystack.strip():
            continue
        match = pattern.search(haystack)
        if match:
            return index, match.start(), match.end()
    return None


def _extract_outline_section_body(
    pages: list[str],
    *,
    start_page: int,
    start_offset: int,
    end_page: int,
    end_offset: int,
    current_title: str,
) -> str:
    start_page = max(start_page, 0)
    end_page = min(max(end_page, start_page), len(pages) - 1)
    if start_page >= len(pages) or end_page < start_page:
        return ""

    current_pattern = _pdf_title_pattern(current_title)
    segment_pages: list[str] = []
    consumed_prefix = 0
    for index in range(start_page, end_page + 1):
        page_text = pages[index]
        if not page_text.strip():
            continue
        if index == start_page:
            if current_pattern:
                match = current_pattern.search(page_text, pos=start_offset)
                if match:
                    consumed_prefix = match.end()
                    page_text = page_text[match.end() :]
                else:
                    consumed_prefix = start_offset
                    page_text = page_text[start_offset:]
            else:
                consumed_prefix = start_offset
                page_text = page_text[start_offset:]
        if index == end_page:
            adjusted_limit = end_offset - consumed_prefix if end_page == start_page else end_offset
            limit = min(max(adjusted_limit, 0), len(page_text))
            page_text = page_text[:limit]
        segment_pages.append(page_text.strip())

    text = "\n\n".join(page for page in segment_pages if page.strip())
    text = _clean_outline_section_body(text, heading=current_title)
    return text.strip()


def _clean_outline_section_body(text: str, *, heading: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    cleaned = PDF_TRAILING_CHAPTER_FOOTER_RE.sub("", cleaned).strip()
    cleaned = re.sub(r"(?i)^openShift container platform\s+\d+\.\d+\s+", "", cleaned)
    heading_pattern = _pdf_title_pattern(heading)
    if heading_pattern:
        cleaned = heading_pattern.sub("", cleaned, count=1).strip()
    cleaned = re.sub(r"\bPage Summary\b", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _skip_docling_heading(heading: str) -> bool:
    normalized = heading.strip().lower()
    if normalized in DOCLING_SKIP_HEADINGS:
        return True
    if normalized.startswith("openshift container platform "):
        return True
    return False


def _should_inline_docling_heading(heading: str) -> bool:
    normalized = heading.strip().lower()
    return normalized in DOCLING_INLINE_HEADINGS_LOWER


def _docling_section_level(heading: str, *, raw_level: int, parent_level: int) -> int:
    normalized = heading.strip()
    chapter_match = re.match(r"^\d+\s*장\b", normalized)
    if chapter_match:
        return 1
    section_match = re.match(r"^(\d+(?:\.\d+)+)", normalized)
    if section_match:
        return section_match.group(1).count(".") + 1
    if re.match(r"^(?:표|그림)\s*\d+\.\d+", normalized):
        return max(parent_level + 1, 2)
    return max(parent_level + 1, max(raw_level - 1, 1))


def _clean_docling_section_body(text: str, *, heading: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    kept_lines: list[str] = []
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if not line:
            kept_lines.append("")
            continue
        if line == "<!-- image -->":
            continue
        if line in {"OpenShift Container Platform 시작하기"}:
            continue
        if re.fullmatch(r"OpenShift Container Platform \d+\.\d+", line):
            continue
        if line == ".":
            continue
        if lower.startswith("copyright ©"):
            continue
        if _is_docling_dot_leader_line(line):
            continue
        if _is_docling_table_separator_line(line):
            continue
        kept_lines.append(raw_line)

    cleaned = "\n".join(kept_lines).strip()
    cleaned = _strip_leading_heading_line(cleaned, heading)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _strip_leading_heading_line(text: str, heading: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned or not heading.strip():
        return cleaned
    lines = cleaned.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return ""
    first = lines[0].strip()
    if first == heading.strip():
        return "\n".join(lines[1:]).strip()
    first_key = _pdf_search_key(first)
    heading_key = _pdf_search_key(heading)
    if first_key and heading_key and first_key == heading_key:
        return "\n".join(lines[1:]).strip()
    return cleaned


def _is_docling_dot_leader_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    dot_count = stripped.count(".")
    if dot_count < 12:
        return False
    other = re.sub(r"[.\s|]", "", stripped)
    return other == ""


def _is_docling_table_separator_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False
    inner = stripped.strip("|").replace("-", "").replace(":", "").replace(" ", "")
    return inner == ""


def _looks_like_pdf_heading(line: str) -> bool:
    candidate = line.strip()
    if not candidate or len(candidate) > 96:
        return False
    if PDF_STRUCTURAL_MARKER_RE.match(candidate) or HEADING_PREFIX_RE.match(candidate):
        return True
    if HEADING_PUNCTUATION_RE.search(candidate):
        return False
    words = candidate.split()
    if 2 <= len(words) <= 8 and candidate == candidate.title():
        return True
    if len(words) == 1:
        return len(candidate) >= 8 and not re.search(r"[,:;]", candidate)
    return 8 <= len(candidate) <= 42 and not re.search(r"[,:;]", candidate)


def _normalize_pdf_heading(line: str) -> str:
    stripped = line.strip()
    return re.sub(r"^#{1,6}\s*", "", stripped)


def _infer_pdf_section_level(heading: str) -> int:
    normalized = heading.strip()
    match = re.match(r"^(\d+(?:\.\d+)*)", normalized)
    if match:
        return match.group(1).count(".") + 1
    return 1


def _pdf_anchor(seed: str, ordinal: int) -> str:
    normalized = ANCHOR_SANITIZE_RE.sub("-", seed.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or f"pdf-section-{ordinal}"


def _validate_pdf_rows(rows: list[dict[str, object]], *, page_count: int) -> None:
    if not rows:
        return
    short_rows = 0
    for row in rows:
        text = str(row.get("text") or "").strip()
        if len(text) <= 18:
            short_rows += 1
    if len(rows) > max(400, page_count * 12) and short_rows / max(len(rows), 1) >= 0.55:
        raise ValueError(
            "PDF section normalization 품질이 낮습니다. "
            "줄 단위 텍스트가 과도하게 쪼개져 study view로 쓰기 어렵습니다. "
            "더 나은 PDF 추출기나 OCR 전처리가 필요합니다."
        )


def _prepare_pdf_page_text(page_text: str) -> str:
    normalized = (page_text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return ""
    if _should_skip_pdf_page(normalized):
        return ""
    normalized = re.sub(r"\n\s*\n+", "\u2029", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" ?\n ?", " ", normalized)
    normalized = normalized.replace("\u2029", "\n\n")
    normalized = PDF_TOC_DOT_LEADER_RE.sub(" ", normalized)
    normalized = PDF_TRAILING_PAGE_NUMBER_RE.sub("", normalized).strip()
    normalized = PDF_TRAILING_CHAPTER_FOOTER_RE.sub("", normalized).strip()

    marker_match = PDF_STRUCTURAL_MARKER_RE.search(normalized)
    if marker_match and marker_match.start() > 0:
        prefix = normalized[:marker_match.start()].strip()
        if prefix and PDF_FRONT_MATTER_TITLE_RE.search(prefix):
            normalized = normalized[marker_match.start() :].strip()

    if (
        normalized.lower().startswith("table of contents")
        or normalized.startswith("목차")
    ) and len(PDF_STRUCTURAL_MARKER_RE.findall(normalized)) >= 6:
        return ""

    if not PDF_STRUCTURAL_MARKER_RE.search(normalized):
        if PDF_SKIP_PAGE_RE.match(normalized):
            return ""
        if PDF_FRONT_MATTER_TITLE_RE.search(normalized) and len(normalized) < 260:
            return ""

    normalized = PDF_STRUCTURE_BREAK_RE.sub("\n\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return normalized


def _should_skip_pdf_page(normalized: str) -> bool:
    compact = re.sub(r"\s+", " ", normalized).strip()
    lowered = compact.lower()
    if not compact:
        return True
    if PDF_STRUCTURAL_MARKER_RE.search(compact):
        return False
    if lowered.startswith("legal notice") or "copyright ©" in lowered:
        return True
    if compact.startswith("목차") or lowered.startswith("table of contents"):
        return True
    if compact.count(".") >= 200 and ("table of contents" in lowered or compact.count("1.") >= 2):
        return True
    if PDF_SKIP_PAGE_RE.match(compact) and len(compact) < 260:
        return True
    return False
