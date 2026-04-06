from __future__ import annotations

import json
import re
from typing import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag

from .models import NormalizedSection, SourceManifestEntry


REMOVE_SELECTORS = (
    "script",
    "style",
    "nav",
    "header",
    "footer",
    "noscript",
    "button",
    "svg",
    "rh-back-to-top",
)

HEADING_RE = re.compile(r"<<<HEADING\s+(.*?)\s+>>>")
COPY_SUFFIX_RE = re.compile(r"\s*링크 복사\s*링크가 클립보드에 복사되었습니다!\s*")
VERSION_ONLY_RE = re.compile(r"^OpenShift Container Platform\s*4\.\d+\s*$")
LEADING_NOISE_RE = (
    re.compile(r"^Red Hat OpenShift Documentation Team$"),
    re.compile(r"^법적 공지$"),
    re.compile(r"^초록$"),
    re.compile(r"^Legal Notice$", re.IGNORECASE),
    re.compile(r"^Abstract$", re.IGNORECASE),
)
NOISE_HEADING_RE = (
    re.compile(r"^Legal Notice$", re.IGNORECASE),
    re.compile(r"^이 콘텐츠는 선택한 언어로 제공되지 않습니다\.?$"),
    re.compile(r"^This content is not available in (the )?selected language\.?$", re.IGNORECASE),
)


def _clean_heading_text(text: str) -> str:
    cleaned = COPY_SUFFIX_RE.sub("", text or "")
    return " ".join(cleaned.split()).strip()


def _normalize_code(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").expandtabs(4)
    lines = [line.rstrip() for line in normalized.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip()


def _table_to_text(table: Tag) -> str:
    rows: list[str] = []
    for row in table.find_all("tr"):
        cells = [
            " ".join(cell.get_text(" ", strip=True).split())
            for cell in row.find_all(["th", "td"])
        ]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows).strip()


def _normalize_non_code_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    paragraphs: list[str] = []
    for chunk in re.split(r"\n\s*\n+", text):
        cleaned = re.sub(r"\s*\n\s*", " ", chunk).strip()
        cleaned = re.sub(r"\s+([,.:;!?%)\]])", r"\1", cleaned)
        cleaned = re.sub(r"([(\[])\s+", r"\1", cleaned)
        if cleaned:
            paragraphs.append(cleaned)
    return "\n\n".join(paragraphs).strip()


def _normalize_text_preserving_blocks(text: str) -> str:
    pattern = re.compile(r"(\[CODE\].*?\[/CODE\]|\[TABLE\].*?\[/TABLE\])", re.DOTALL)
    parts = pattern.split(text)
    normalized: list[str] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("[CODE]") or part.startswith("[TABLE]"):
            normalized.append(part.strip())
        else:
            cleaned = _normalize_non_code_whitespace(part)
            if cleaned:
                normalized.append(cleaned)
    return "\n\n".join(normalized).strip()


def _trim_leading_noise_lines(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    while lines:
        current = lines[0]
        if not current:
            lines.pop(0)
            continue
        if any(pattern.match(current) for pattern in LEADING_NOISE_RE):
            lines.pop(0)
            continue
        break
    return "\n".join(lines).strip()


def _should_keep_preamble(text: str) -> bool:
    if not text:
        return False
    if VERSION_ONLY_RE.match(text):
        return False
    word_count = len(re.findall(r"\S+", text))
    if word_count <= 4 and "OpenShift Container Platform" in text:
        return False
    return True


def _is_noise_heading(text: str) -> bool:
    cleaned = " ".join((text or "").split()).strip()
    return any(pattern.match(cleaned) for pattern in NOISE_HEADING_RE)


def _parse_marked_text(marked_text: str) -> tuple[str, list[dict[str, object]]]:
    sections: list[dict[str, object]] = []
    path_by_level: dict[int, str] = {}
    book_title = ""
    current: dict[str, object] | None = None
    current_chunks: list[str] = []
    preamble_chunks: list[str] = []
    last_pos = 0

    def flush_current() -> None:
        nonlocal current, current_chunks
        if current is None:
            return
        text = _normalize_text_preserving_blocks("\n".join(current_chunks))
        if text:
            current["text"] = text
            sections.append(current.copy())
        current = None
        current_chunks = []

    for match in HEADING_RE.finditer(marked_text):
        body = marked_text[last_pos:match.start()]
        if body.strip():
            if current is None:
                preamble_chunks.append(body)
            else:
                current_chunks.append(body)

        heading = json.loads(match.group(1))
        level = int(heading["level"])
        title = _clean_heading_text(str(heading["title"]))
        anchor = str(heading.get("anchor") or "").strip()

        if level == 1:
            book_title = title or book_title
            path_by_level = {1: book_title}
        else:
            flush_current()
            path_by_level[level] = title
            for deeper_level in list(path_by_level):
                if deeper_level > level:
                    del path_by_level[deeper_level]
            current = {
                "heading": title,
                "anchor": anchor or f"{title.lower().replace(' ', '-')}",
                "section_level": level,
                "section_path": [value for key, value in sorted(path_by_level.items()) if key >= 2],
            }
        last_pos = match.end()

    tail = marked_text[last_pos:]
    if tail.strip():
        if current is None:
            preamble_chunks.append(tail)
        else:
            current_chunks.append(tail)
    flush_current()

    preamble_text = _normalize_text_preserving_blocks("\n".join(preamble_chunks))
    if _should_keep_preamble(preamble_text):
        sections.insert(
            0,
            {
                "heading": book_title or "Overview",
                "anchor": "overview",
                "section_level": 1,
                "section_path": [book_title or "Overview"],
                "text": preamble_text,
            },
        )

    return book_title or "Untitled", sections


def extract_sections(html: str, entry: SourceManifestEntry) -> list[NormalizedSection]:
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("main#main-content article") or soup.select_one("article")
    if article is None:
        raise ValueError(f"Could not find article body for {entry.book_slug}")

    for selector in REMOVE_SELECTORS:
        for node in article.select(selector):
            node.decompose()

    for tag in article.find_all("pre"):
        code_text = _normalize_code(tag.get_text("", strip=False))
        tag.replace_with(NavigableString(f"\n\n[CODE]\n{code_text}\n[/CODE]\n\n"))

    for tag in article.find_all("code"):
        inline_code = " ".join(tag.get_text(" ", strip=True).split())
        if inline_code:
            tag.replace_with(NavigableString(f"`{inline_code}`"))

    for tag in article.find_all("table"):
        table_text = _table_to_text(tag)
        tag.replace_with(NavigableString(f"\n\n[TABLE]\n{table_text}\n[/TABLE]\n\n"))

    for heading in article.find_all(re.compile(r"^h[1-6]$")):
        level = int(heading.name[1:])
        marker = json.dumps(
            {
                "level": level,
                "anchor": heading.get("id", ""),
                "title": _clean_heading_text(heading.get_text(" ", strip=True)),
            },
            ensure_ascii=False,
        )
        heading.replace_with(NavigableString(f"\n\n<<<HEADING {marker} >>>\n\n"))

    marked_text = article.get_text("\n")
    book_title, parsed_sections = _parse_marked_text(marked_text)
    sections: list[NormalizedSection] = []

    for section in parsed_sections:
        text = _trim_leading_noise_lines(str(section["text"]).strip())
        if not text:
            continue
        if _is_noise_heading(str(section["heading"])):
            continue
        anchor = str(section["anchor"])
        viewer_path = f"{entry.viewer_path}#{anchor}"
        sections.append(
            NormalizedSection(
                book_slug=entry.book_slug,
                book_title=book_title,
                heading=str(section["heading"]),
                section_level=int(section["section_level"]),
                section_path=list(section["section_path"]),
                anchor=anchor,
                source_url=entry.source_url,
                viewer_path=viewer_path,
                text=text,
            )
        )

    return sections


def iter_normalized_dicts(sections: Iterable[NormalizedSection]) -> list[dict[str, object]]:
    return [section.to_dict() for section in sections]
