from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

from .models import NormalizedSection, SourceManifestEntry
from .normalize import extract_sections_from_html_fragment


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z가-힣]+", "-", (value or "").strip().lower())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "document"


def _normalize_code_block(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip()


def _build_local_entry(path: Path, *, book_slug: str | None = None, title: str | None = None) -> SourceManifestEntry:
    resolved = path.resolve()
    slug = _slugify(book_slug or resolved.stem)
    display_title = (title or resolved.stem).strip() or slug
    return SourceManifestEntry(
        book_slug=slug,
        title=display_title,
        vendor_title=display_title,
        source_url=resolved.as_uri(),
        viewer_path=f"/docs/local/{slug}/index.html",
        high_value=True,
        citation_eligible=True,
        approval_status="user_uploaded",
        approval_notes="local document ingest",
        viewer_strategy="normalized_local_doc",
    )


def _split_markdown_sections(text: str) -> list[tuple[str, str, int, list[str], str]]:
    sections: list[tuple[str, str, int, list[str], str]] = []
    path_by_level: dict[int, str] = {}
    current_heading = "Overview"
    current_anchor = "overview"
    current_level = 1
    current_lines: list[str] = []
    in_code = False

    def flush() -> None:
        nonlocal current_lines
        body = "\n".join(current_lines).strip()
        if body:
            section_path = [value for key, value in sorted(path_by_level.items()) if key >= 1]
            sections.append((current_heading, current_anchor, current_level, section_path or [current_heading], body))
        current_lines = []

    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            current_lines.append(line)
            continue
        if not in_code:
            match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if match:
                flush()
                current_level = len(match.group(1))
                current_heading = match.group(2).strip() or "Section"
                current_anchor = _slugify(current_heading)
                path_by_level[current_level] = current_heading
                for key in list(path_by_level):
                    if key > current_level:
                        del path_by_level[key]
                continue
        current_lines.append(line)
    flush()
    if not sections:
        body = text.strip()
        if body:
            sections.append(("Overview", "overview", 1, ["Overview"], body))
    return sections


def _markdown_sections_to_records(text: str, entry: SourceManifestEntry) -> list[NormalizedSection]:
    sections: list[NormalizedSection] = []
    for heading, anchor, level, section_path, body in _split_markdown_sections(text):
        blocks: list[str] = []
        in_code = False
        code_lines: list[str] = []
        prose_lines: list[str] = []
        for raw_line in body.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith("```"):
                if in_code:
                    code = _normalize_code_block("\n".join(code_lines))
                    if code:
                        blocks.append(f"[CODE]\n{code}\n[/CODE]")
                    code_lines = []
                    in_code = False
                else:
                    if prose_lines:
                        prose = "\n".join(prose_lines).strip()
                        if prose:
                            blocks.append(prose)
                        prose_lines = []
                    in_code = True
                continue
            if in_code:
                code_lines.append(raw_line)
            else:
                prose_lines.append(raw_line)
        if code_lines:
            code = _normalize_code_block("\n".join(code_lines))
            if code:
                blocks.append(f"[CODE]\n{code}\n[/CODE]")
        if prose_lines:
            prose = "\n".join(prose_lines).strip()
            if prose:
                blocks.append(prose)
        normalized_text = "\n\n".join(block for block in blocks if block).strip()
        if not normalized_text:
            continue
        sections.append(
            NormalizedSection(
                book_slug=entry.book_slug,
                book_title=entry.title,
                heading=heading,
                section_level=level,
                section_path=section_path,
                anchor=anchor,
                source_url=entry.source_url,
                viewer_path=f"{entry.viewer_path}#{anchor}",
                text=normalized_text,
            )
        )
    return sections


def _pdf_sections_to_records(path: Path, entry: SourceManifestEntry) -> list[NormalizedSection]:
    reader = PdfReader(str(path))
    sections: list[NormalizedSection] = []
    for index, page in enumerate(reader.pages, start=1):
        body = (page.extract_text() or "").strip()
        if not body:
            continue
        anchor = f"page-{index}"
        sections.append(
            NormalizedSection(
                book_slug=entry.book_slug,
                book_title=entry.title,
                heading=f"Page {index}",
                section_level=1,
                section_path=[f"Page {index}"],
                anchor=anchor,
                source_url=entry.source_url,
                viewer_path=f"{entry.viewer_path}#{anchor}",
                text=body,
            )
        )
    if sections:
        return sections

    raise ValueError(f"PDF 텍스트를 추출하지 못했습니다: {path.name}")


def extract_sections_from_local_path(
    path: str | Path,
    *,
    book_slug: str | None = None,
    title: str | None = None,
) -> tuple[SourceManifestEntry, list[NormalizedSection]]:
    source_path = Path(path)
    entry = _build_local_entry(source_path, book_slug=book_slug, title=title)
    suffix = source_path.suffix.lower()
    if suffix in {".html", ".htm"}:
        text = source_path.read_text(encoding="utf-8")
        sections = extract_sections_from_html_fragment(text, entry)
    elif suffix in {".md", ".markdown", ".txt"}:
        text = source_path.read_text(encoding="utf-8")
        sections = _markdown_sections_to_records(text, entry)
    elif suffix == ".pdf":
        sections = _pdf_sections_to_records(source_path, entry)
    else:
        raise ValueError(f"unsupported local document type: {suffix or source_path.name}")
    return entry, sections
