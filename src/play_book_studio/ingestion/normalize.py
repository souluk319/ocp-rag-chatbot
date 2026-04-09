"""노이즈가 많은 게시 HTML을 canonical section으로 바꾼다.

검색 품질 문제의 근원은 여기서 시작되는 경우가 많다. 섹션 경계가 잘못되거나,
노이즈가 남거나, anchor가 사라지면 뒤 단계 전체로 전파된다.
"""

from __future__ import annotations

import json
import re
from typing import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag

from play_book_studio.canonical import (
    CanonicalDocumentAst,
    build_web_document_ast,
    project_corpus_sections,
    translate_document_ast,
    validate_document_ast,
)
from play_book_studio.ingestion.models import CONTENT_STATUS_TRANSLATED_KO_DRAFT

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
    "rh-badge",
    "rh-back-to-top",
)

HEADING_RE = re.compile(r"<<<HEADING\s+(.*?)\s+>>>")
COPY_SUFFIX_RE = re.compile(r"\s*링크 복사\s*링크가 클립보드에 복사되었습니다!\s*")
VERSION_ONLY_RE = re.compile(r"^OpenShift Container Platform\s*4\.\d+\s*$")
CODE_LANGUAGE_RE = re.compile(r"language-([a-zA-Z0-9_+-]+)")
LEADING_NOISE_RE = (
    re.compile(r"^Red Hat OpenShift Documentation Team$"),
    re.compile(r"^Red Hat OpenShift Documentation Team(?:\s+법적 공지\s+초록)?\s*", re.IGNORECASE),
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
    return "\n".join(lines).strip("\n")


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


def _normalize_marker_attr(value: str) -> str:
    return " ".join((value or "").replace('"', "'").split()).strip()


def _marker_attrs(**values: object) -> str:
    parts: list[str] = []
    for key, value in values.items():
        if value is None:
            continue
        normalized = _normalize_marker_attr(str(value))
        if not normalized:
            continue
        parts.append(f'{key}="{normalized}"')
    return (" " + " ".join(parts)) if parts else ""


def _extract_code_language(tag: Tag, default: str = "shell") -> str:
    candidates = [tag]
    parent = tag.parent
    if isinstance(parent, Tag):
        candidates.append(parent)
    for candidate in candidates:
        class_names = candidate.get("class") or []
        for class_name in class_names:
            match = CODE_LANGUAGE_RE.search(str(class_name))
            if match:
                return match.group(1).strip().lower()
    return default


def _code_marker(
    code_text: str,
    *,
    language: str = "shell",
    wrap_hint: bool = False,
    overflow_hint: str = "toggle",
    caption: str = "",
) -> str:
    attrs = _marker_attrs(
        language=language,
        wrap_hint=str(wrap_hint).lower(),
        overflow_hint=overflow_hint,
        caption=caption,
    )
    return f"\n\n[CODE{attrs}]\n{code_text}\n[/CODE]\n\n"


def _table_marker(table_text: str, *, caption: str = "") -> str:
    attrs = _marker_attrs(caption=caption)
    return f"\n\n[TABLE{attrs}]\n{table_text}\n[/TABLE]\n\n"


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
    pattern = re.compile(
        r"(\[CODE(?:\s+[^\]]+)?\].*?\[/CODE\]|\[TABLE(?:\s+[^\]]+)?\].*?\[/TABLE\])",
        re.DOTALL,
    )
    parts = pattern.split(text)
    normalized: list[str] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("[CODE") or part.startswith("[TABLE"):
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
        stripped = current
        changed = False
        for pattern in LEADING_NOISE_RE:
            if pattern.match(stripped):
                replaced = pattern.sub("", stripped, count=1).strip()
                changed = True
                if replaced:
                    lines[0] = replaced
                else:
                    lines.pop(0)
                break
        if changed:
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


def extract_document_ast(
    html: str,
    entry: SourceManifestEntry,
    *,
    settings=None,
) -> CanonicalDocumentAst:
    """게시 HTML을 공통 canonical AST로 바꾼다.

    현재는 기존 normalize 경계를 유지하면서 AST를 중간 원천 구조로 끼워 넣는 단계다.
    retrieval은 아직 `NormalizedSection`을 보지만, 그 데이터도 이제 AST projection에서 나온다.
    """

    # Red Hat 게시 문서를 일관된 section 흐름으로 정규화하되, citation과 viewer에
    # 필요한 anchor, code/table block은 최대한 안정적으로 보존한다.
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("main#main-content article") or soup.select_one("article")
    if article is None:
        raise ValueError(f"Could not find article body for {entry.book_slug}")

    for selector in REMOVE_SELECTORS:
        for node in article.select(selector):
            node.decompose()

    for tag in article.find_all("rh-code-block"):
        code_segments = [
            _normalize_code(pre.get_text("", strip=False))
            for pre in tag.find_all("pre")
            if _normalize_code(pre.get_text("", strip=False))
        ]
        code_text = "\n".join(segment for segment in code_segments if segment).strip()
        if not code_text:
            tag.decompose()
            continue
        actions = {
            item.strip().lower()
            for item in str(tag.get("actions") or "").split()
            if item.strip()
        }
        overflow_hint = "toggle"
        if str(tag.get("full-height") or "").strip().lower() in {"false", "0", "off"}:
            overflow_hint = "inline"
        tag.replace_with(
            NavigableString(
                _code_marker(
                    code_text,
                    language=str(tag.get("language") or "shell").strip().lower() or "shell",
                    wrap_hint="wrap" in actions,
                    overflow_hint=overflow_hint,
                )
            )
        )

    for tag in article.find_all("pre"):
        code_text = _normalize_code(tag.get_text("", strip=False))
        if not code_text:
            tag.decompose()
            continue
        tag.replace_with(
            NavigableString(
                _code_marker(
                    code_text,
                    language=_extract_code_language(tag),
                    wrap_hint=False,
                    overflow_hint="toggle",
                )
            )
        )

    for tag in article.find_all("code"):
        inline_code = " ".join(tag.get_text(" ", strip=True).split())
        if inline_code:
            tag.replace_with(NavigableString(f"`{inline_code}`"))

    for tag in article.find_all("table"):
        table_text = _table_to_text(tag)
        if not table_text:
            tag.decompose()
            continue
        caption = ""
        caption_tag = tag.find("caption")
        if isinstance(caption_tag, Tag):
            caption = caption_tag.get_text(" ", strip=True)
        tag.replace_with(NavigableString(_table_marker(table_text, caption=caption)))

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
    document = build_web_document_ast(
        entry=entry,
        book_title=book_title,
        parsed_sections=parsed_sections,
    )
    if settings is not None and entry.content_status == CONTENT_STATUS_TRANSLATED_KO_DRAFT:
        document = translate_document_ast(document, settings)
    issues = validate_document_ast(document)
    if issues:
        valid_sections = {section.section_id for section in document.sections}
        filtered = [issue for issue in issues if issue.code not in {"empty_blocks"} or issue.section_id not in valid_sections]
        if filtered:
            joined = ", ".join(issue.code for issue in filtered[:5])
            raise ValueError(f"Invalid canonical AST for {entry.book_slug}: {joined}")
    return document


def extract_sections(html: str, entry: SourceManifestEntry) -> list[NormalizedSection]:
    document = extract_document_ast(html, entry)
    return project_normalized_sections(document)


def project_normalized_sections(document: CanonicalDocumentAst) -> list[NormalizedSection]:
    sections: list[NormalizedSection] = []
    for row in project_corpus_sections(document):
        text = _trim_leading_noise_lines(row.text.strip())
        if not text:
            continue
        if _is_noise_heading(row.heading):
            continue
        sections.append(
            NormalizedSection(
                book_slug=row.book_slug,
                book_title=row.book_title,
                heading=row.heading,
                section_level=row.section_level,
                section_path=list(row.section_path),
                anchor=row.anchor,
                source_url=row.source_url,
                viewer_path=row.viewer_path,
                text=text,
                section_id=row.section_id,
                semantic_role=row.semantic_role,
                block_kinds=row.block_kinds,
                source_language=row.source_language,
                display_language=row.display_language,
                translation_status=row.translation_status,
                translation_stage=row.translation_stage,
                translation_source_language=row.translation_source_language,
                translation_source_url=row.translation_source_url,
                translation_source_fingerprint=row.translation_source_fingerprint,
            )
        )

    return sections


def iter_normalized_dicts(sections: Iterable[NormalizedSection]) -> list[dict[str, object]]:
    return [section.to_dict() for section in sections]
