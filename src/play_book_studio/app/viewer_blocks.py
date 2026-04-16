# 플레이북 문서의 section body를 HTML 블록으로 렌더링한다.
import html
import json
import re
from typing import Any

from play_book_studio.canonical.command_split import split_inline_commands

NORMALIZED_BLOCK_RE = re.compile(
    r"(\[CODE(?:\s+[^\]]+)?\].*?\[/CODE\]|\[TABLE(?:\s+[^\]]+)?\].*?\[/TABLE\]|\[FIGURE(?:\s+[^\]]+)?\].*?\[/FIGURE\])",
    re.DOTALL,
)
FENCED_CODE_BLOCK_RE = re.compile(
    r"```(?P<language>[A-Za-z0-9_+\-]*)[ \t]*\n(?P<body>.*?\n?)```",
    re.DOTALL,
)
MARKDOWN_IMAGE_BLOCK_RE = re.compile(
    r"(?m)^(?:>\s*)?!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+\"(?P<title>[^\"]+)\")?\)\s*$"
)
MARKDOWN_TABLE_BLOCK_RE = re.compile(
    r"(?ms)(^|\n{2,})(?P<body>\|.*?\|\s*\n\|\s*[-:| ]+\|\s*(?:\n\|.*?\|\s*)+)(?=\n{2,}|\Z)"
)
WIKI_ASSET_URL_RE = re.compile(r"^/playbooks/wiki-assets/[^/]+/(?P<slug>[^/]+)/(?P<asset_name>[^/]+)$")
MARKER_ATTR_RE = re.compile(r'([a-z_]+)="((?:[^"\\]|\\.)*)"')
CODE_BLOCK_RE = re.compile(r"^\[CODE(?P<attrs>[^\]]*)\]\s*(?P<body>.*?)\s*\[/CODE\]$", re.DOTALL)
TABLE_BLOCK_RE = re.compile(r"^\[TABLE(?P<attrs>[^\]]*)\]\s*(?P<body>.*?)\s*\[/TABLE\]$", re.DOTALL)
FIGURE_BLOCK_RE = re.compile(r"^\[FIGURE(?P<attrs>[^\]]*)\]\s*(?P<body>.*?)\s*\[/FIGURE\]$", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
ORDERED_LIST_ITEM_RE = re.compile(r"^(?P<index>\d+)\.\s+(?P<body>.+)$", re.DOTALL)
SOURCE_VIEW_LEADING_NOISE_RE = re.compile(
    r"^\s*Red Hat OpenShift Documentation Team(?:\s+법적 공지)?(?:\s+초록)?\s*",
)
SOURCE_VIEW_TOC_RE = re.compile(r"^\s*목차\s*(?:\n\n|\n)?")
ASCII_GRID_BORDER_RE = re.compile(r"^\s*[+\-=:]{3,}\s*$")
ASCII_GRID_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
MARKDOWN_TABLE_DIVIDER_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
LOW_SIGNAL_SHELL_RE = re.compile(
    r"^(?:\.\.\.|(?:\$|#)?\s*(?:oc|kubectl))\s*$",
    re.IGNORECASE,
)
READER_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|(?<=다\.)\s+|(?<=니다\.)\s+")
READER_BREAKWORD_RE = re.compile(
    r"\s+(?=(?:Procedure|Prerequisites|Warning|Caution|Note|주의|참고|사전 요구 사항|프로세스|다음 절차|다음 명령))"
)


def _clean_source_view_text(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = SOURCE_VIEW_LEADING_NOISE_RE.sub("", cleaned, count=1).lstrip()
    cleaned = SOURCE_VIEW_TOC_RE.sub("", cleaned, count=1).lstrip()
    return cleaned


def _normalize_markdown_fenced_code_blocks(text: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        language = (match.group("language") or "").strip() or "shell"
        body = (match.group("body") or "").strip("\n")
        return f'[CODE language="{language}" wrap_hint="false"]\n{body}\n[/CODE]'

    return FENCED_CODE_BLOCK_RE.sub(_replace, text)


def _normalize_markdown_image_blocks(text: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        alt = (match.group("alt") or "").strip()
        src = (match.group("src") or "").strip()
        title = (match.group("title") or "").strip()
        caption = title or alt
        attrs = ' src="{src}" alt="{alt}"'.format(
            src=html.escape(src, quote=True),
            alt=html.escape(alt or caption, quote=True),
        )
        body = html.escape(caption)
        return f'[FIGURE{attrs}]\n{body}\n[/FIGURE]'

    return MARKDOWN_IMAGE_BLOCK_RE.sub(_replace, text)


def _normalize_markdown_table_blocks(text: str) -> str:
    lines = str(text or "").splitlines()
    if not lines:
        return str(text or "")

    normalized: list[str] = []
    index = 0
    total = len(lines)
    while index < total:
        current = lines[index]
        next_line = lines[index + 1] if index + 1 < total else ""
        if "|" in current and MARKDOWN_TABLE_DIVIDER_RE.match(next_line):
            block = [current, next_line]
            index += 2
            while index < total:
                candidate = lines[index]
                if candidate.strip() and "|" in candidate:
                    block.append(candidate)
                    index += 1
                    continue
                break
            normalized.append("[TABLE]")
            normalized.extend(block)
            normalized.append("[/TABLE]")
            continue
        normalized.append(current)
        index += 1

    trailing_newline = "\n" if str(text or "").endswith("\n") else ""
    return "\n".join(normalized) + trailing_newline


def _render_inline_html(text: str) -> str:
    fragments: list[str] = []
    last_index = 0
    for match in INLINE_CODE_RE.finditer(text):
        if match.start() > last_index:
            fragments.append(html.escape(text[last_index:match.start()]))
        fragments.append(f"<code>{html.escape(match.group(1))}</code>")
        last_index = match.end()
    if last_index < len(text):
        fragments.append(html.escape(text[last_index:]))
    return "".join(fragments)


def _render_text_with_command_boxes(text: str, *, step_mode: bool = False) -> str:
    split = split_inline_commands(text)
    if split is None:
        escaped = _render_inline_html(text)
        if step_mode:
            return f'<div class="step-text">{escaped}</div>'
        return f"<p>{escaped}</p>"

    fragments: list[str] = []
    if split.narrative_text:
        narrative_html = _render_inline_html(split.narrative_text)
        if step_mode:
            fragments.append(f'<div class="step-text">{narrative_html}</div>')
        else:
            fragments.append(f"<p>{narrative_html}</p>")
    for index, command in enumerate(split.commands):
        fragments.append(
            _render_code_block_html(
                command,
                language="shell",
                copy_text=command,
                wrap_hint=True,
                overflow_hint="toggle",
                caption=split.caption_text if index == 0 and not split.narrative_text else "",
                preserve_layout=_looks_like_ascii_grid(command),
            )
        )
    return "".join(fragments)


def _parse_marker_attrs(text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, value in MARKER_ATTR_RE.findall(text or ""):
        attrs[key.strip().lower()] = value.strip()
    return attrs


def _parse_bool_attr(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _looks_like_subheading(text: str) -> bool:
    stripped = text.strip()
    if not stripped or len(stripped) > 36:
        return False
    if re.search(r"(?:니다|합니다|하십시오|하세요|[\.\?\!])", stripped):
        return False
    return True


def _looks_like_ascii_grid(text: str) -> bool:
    lines = [line.rstrip() for line in (text or "").splitlines() if line.strip()]
    if len(lines) < 3:
        return False
    border_rows = sum(1 for line in lines if ASCII_GRID_BORDER_RE.match(line))
    cell_rows = sum(1 for line in lines if ASCII_GRID_ROW_RE.match(line))
    return border_rows >= 2 and cell_rows >= 1


def _split_table_row(row: str) -> list[str]:
    stripped = str(row or "").strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _looks_like_markdown_table_block(text: str) -> bool:
    lines = [line.rstrip() for line in str(text or "").splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    if "|" not in lines[0]:
        return False
    if not MARKDOWN_TABLE_DIVIDER_RE.match(lines[1]):
        return False
    body_lines = lines[2:]
    return bool(body_lines) and all("|" in line for line in body_lines)


def _split_reader_display_paragraphs(text: str) -> list[str]:
    def _hard_wrap(value: str, *, limit: int = 160) -> list[str]:
        words = [word for word in str(value or "").split() if word]
        if not words:
            return []
        wrapped: list[str] = []
        bucket: list[str] = []
        bucket_len = 0
        for word in words:
            projected = bucket_len + len(word) + (1 if bucket else 0)
            if bucket and projected > limit:
                wrapped.append(" ".join(bucket).strip())
                bucket = [word]
                bucket_len = len(word)
                continue
            bucket.append(word)
            bucket_len = projected
        if bucket:
            wrapped.append(" ".join(bucket).strip())
        return wrapped

    cleaned = " ".join(str(text or "").split()).strip()
    if not cleaned:
        return []
    if READER_BREAKWORD_RE.search(cleaned):
        segmented: list[str] = []
        for piece in READER_BREAKWORD_RE.split(cleaned):
            piece = piece.strip()
            if not piece:
                continue
            if len(piece) > 260:
                segmented.extend(_hard_wrap(piece))
            else:
                segmented.append(piece)
        if len(segmented) > 1:
            return segmented
    if len(cleaned) <= 320:
        return [cleaned]
    sentences = [
        sentence.strip()
        for sentence in READER_SENTENCE_SPLIT_RE.split(cleaned)
        if sentence.strip()
    ]
    if len(sentences) <= 1:
        return _hard_wrap(cleaned) or [cleaned]
    chunks: list[str] = []
    bucket: list[str] = []
    bucket_len = 0
    for sentence in sentences:
        projected = bucket_len + len(sentence) + (1 if bucket else 0)
        if bucket and (projected > 260 or len(bucket) >= 2):
            chunks.append(" ".join(bucket).strip())
            bucket = [sentence]
            bucket_len = len(sentence)
            continue
        bucket.append(sentence)
        bucket_len = projected
    if bucket:
        chunks.append(" ".join(bucket).strip())
    normalized_chunks: list[str] = []
    for chunk in chunks or [cleaned]:
        if len(chunk) > 320:
            normalized_chunks.extend(_hard_wrap(chunk))
        else:
            normalized_chunks.append(chunk)
    return normalized_chunks or [cleaned]


def _is_low_signal_ordered_item_body(text: str) -> bool:
    normalized = " ".join(str(text or "").split()).strip()
    if not normalized:
        return True
    return re.fullmatch(r"\d+(?:[./:-]\d+)*", normalized) is not None


def _looks_like_structured_code_paragraph(text: str) -> bool:
    normalized = " ".join(str(text or "").split()).strip()
    if len(normalized) < 120:
        return False
    colon_count = normalized.count(":")
    quote_count = normalized.count('"')
    if normalized.startswith("{"):
        return colon_count >= 4 and quote_count >= 8
    if normalized.startswith('"'):
        return colon_count >= 4 and quote_count >= 6
    return False


def _should_suppress_low_signal_code_block(code_text: str, *, language: str = "shell") -> bool:
    normalized = (code_text or "").strip()
    if not normalized:
        return True
    normalized_language = (language or "shell").strip().lower()
    if normalized_language not in {"shell", "shell-session", "bash", "sh", "console", "text"}:
        return False
    return LOW_SIGNAL_SHELL_RE.fullmatch(normalized) is not None


def _render_code_block_html(
    code_text: str,
    *,
    language: str = "shell",
    copy_text: str = "",
    wrap_hint: bool = False,
    overflow_hint: str = "toggle",
    caption: str = "",
    preserve_layout: bool = False,
) -> str:
    if _should_suppress_low_signal_code_block(code_text, language=language):
        return ""
    copy_payload = html.escape(json.dumps(copy_text or code_text), quote=True)
    classes = ["code-block"]
    if preserve_layout:
        classes.append("preserve-layout")
        wrap_hint = False
    if wrap_hint:
        classes.append("is-wrapped")
    caption_html = (
        '<div class="code-caption">{}</div>'.format(html.escape(caption))
        if caption.strip()
        else ""
    )
    _ = overflow_hint
    return """
    <section class="{classes}">
      {caption_html}
      <div class="code-header">
        <span class="code-label">{language}</span>
        <div class="code-actions">
          <button type="button" class="copy-button icon-button" data-copy="{copy_payload}" data-label-default="복사" onclick="copyViewerCode(this)" title="복사" aria-label="복사">
            <span aria-hidden="true">⧉</span>
          </button>
          <button type="button" class="copy-button icon-button" data-label-default="줄바꿈" data-label-active="줄바꿈 해제" aria-pressed="{wrap_pressed}" onclick="toggleViewerCodeWrap(this)" title="{wrap_title}" aria-label="{wrap_title}">
            <span aria-hidden="true">↵</span>
          </button>
        </div>
      </div>
      <pre><code>{code}</code></pre>
    </section>
    """.format(
        classes=" ".join(classes),
        caption_html=caption_html,
        language=html.escape(language),
        copy_payload=copy_payload,
        wrap_pressed="true" if wrap_hint else "false",
        wrap_title="줄바꿈 해제" if wrap_hint else "줄바꿈",
        code=html.escape(code_text),
    ).strip()


def _render_table_block_html(table_text: str, *, caption: str = "") -> str:
    raw_lines = [row for row in table_text.splitlines() if row.strip()]
    rows = [_split_table_row(row) for row in raw_lines]
    if not rows:
        return ""
    headers = rows[0]
    body = rows[1:]
    if len(raw_lines) >= 2 and MARKDOWN_TABLE_DIVIDER_RE.match(raw_lines[1]):
        body = rows[2:]
    if not body:
        body = [headers]
        headers = []
    header_html = ""
    if headers:
        header_cells = "".join(f"<th>{html.escape(cell)}</th>" for cell in headers)
        header_html = f"<thead><tr>{header_cells}</tr></thead>"
    body_rows: list[str] = []
    for row in body:
        cells = "".join(f"<td>{html.escape(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    caption_html = (
        '<div class="table-caption">{}</div>'.format(html.escape(caption))
        if caption.strip()
        else ""
    )
    return """
    <div class="table-wrap">
      {caption_html}
      <table>
        {header_html}
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
    """.format(caption_html=caption_html, header_html=header_html, rows="".join(body_rows)).strip()


def _render_figure_block_html(src: str, *, caption: str = "", alt: str = "", kind: str = "", diagram_type: str = "") -> str:
    safe_src = html.escape(src, quote=True)
    safe_alt = html.escape(alt or caption or "figure", quote=True)
    caption_html = f"<figcaption>{html.escape(caption)}</figcaption>" if caption.strip() else ""
    normalized_kind = (kind or "").strip().lower()
    normalized_diagram_type = (diagram_type or "").strip().lower()
    class_names = ["figure-block"]
    if normalized_kind == "diagram" or src.strip().lower().endswith(".svg"):
        class_names.append("diagram-block")
    eyebrow_html = ""
    if normalized_kind == "diagram":
        label = "Diagram" if not normalized_diagram_type else f"Diagram · {normalized_diagram_type.replace('_', ' ')}"
        eyebrow_html = f'<div class="figure-eyebrow">{html.escape(label)}</div>'
    href = src
    external_attrs = ' target="_blank" rel="noreferrer"'
    match = WIKI_ASSET_URL_RE.fullmatch(src.strip())
    if match is not None:
        href = "/wiki/figures/{slug}/{asset_name}/index.html".format(
            slug=match.group("slug"),
            asset_name=match.group("asset_name"),
        )
        external_attrs = ""
    else:
        pass
    return """
    <figure class="{class_names}">
      {eyebrow_html}
      <a class="figure-link" href="{href}"{external_attrs}>
        <img src="{src}" alt="{alt}" loading="lazy" />
      </a>
      {caption_html}
    </figure>
    """.format(
        class_names=" ".join(class_names),
        eyebrow_html=eyebrow_html,
        href=html.escape(href, quote=True),
        external_attrs=external_attrs,
        src=safe_src,
        alt=safe_alt,
        caption_html=caption_html,
    ).strip()


def _render_playbook_block_html(block: dict[str, Any]) -> str:
    kind = str(block.get("kind") or "").strip()
    if kind == "paragraph":
        return _render_text_with_command_boxes(str(block.get("text") or "").strip())
    if kind == "prerequisite":
        items = [str(item).strip() for item in (block.get("items") or []) if str(item).strip()]
        if not items:
            return ""
        return """
        <section class="note-card note-note">
          <div class="note-title">사전 요구 사항</div>
          <ul class="list-block">{items}</ul>
        </section>
        """.format(
            items="".join(f"<li>{html.escape(item)}</li>" for item in items)
        ).strip()
    if kind == "procedure":
        steps = list(block.get("steps") or [])
        items: list[str] = []
        for step in steps:
            text = str(step.get("text") or "").strip()
            if not text:
                continue
            substeps = [str(item).strip() for item in (step.get("substeps") or []) if str(item).strip()]
            substep_html = ""
            if substeps:
                substep_html = '<ul class="substep-list">{}</ul>'.format(
                    "".join(f"<li>{html.escape(item)}</li>" for item in substeps)
                )
            items.append(
                "<li>{}{}</li>".format(
                    _render_text_with_command_boxes(text, step_mode=True),
                    substep_html,
                )
            )
        if not items:
            return ""
        return '<ol class="procedure-list">{}</ol>'.format("".join(items))
    if kind == "code":
        code_text = str(block.get("code") or "").strip()
        return _render_code_block_html(
            code_text,
            language=str(block.get("language") or "shell").strip() or "shell",
            copy_text=str(block.get("copy_text") or "").strip(),
            wrap_hint=bool(block.get("wrap_hint", True)),
            overflow_hint=str(block.get("overflow_hint") or "toggle").strip() or "toggle",
            caption=str(block.get("caption") or "").strip(),
            preserve_layout=_looks_like_ascii_grid(code_text),
        )
    if kind == "note":
        variant = str(block.get("variant") or "note").strip().lower()
        title = str(block.get("title") or "").strip()
        note_title = title or {
            "warning": "주의",
            "caution": "주의",
            "important": "중요",
            "tip": "팁",
        }.get(variant, "참고")
        return """
        <section class="note-card note-{variant}">
          <div class="note-title">{title}</div>
          <p>{text}</p>
        </section>
        """.format(
            variant=html.escape(variant, quote=True),
            title=html.escape(note_title),
            text=_render_inline_html(str(block.get("text") or "").strip()),
        ).strip()
    if kind == "table":
        headers = [str(item).strip() for item in (block.get("headers") or [])]
        rows = [tuple(str(cell).strip() for cell in row) for row in (block.get("rows") or [])]
        lines: list[str] = []
        if headers:
            lines.append(" | ".join(headers))
        lines.extend(" | ".join(row) for row in rows)
        return _render_table_block_html("\n".join(lines), caption=str(block.get("caption") or "").strip())
    return ""


def _render_normalized_section_html(text: str) -> str:
    blocks: list[str] = []
    normalized = _clean_source_view_text(text)
    normalized = _normalize_markdown_fenced_code_blocks(normalized)
    normalized = _normalize_markdown_image_blocks(normalized)
    normalized = _normalize_markdown_table_blocks(normalized)
    paragraph_queue: list[str] = []

    def flush_paragraph_queue() -> None:
        nonlocal paragraph_queue
        if not paragraph_queue:
            return
        index = 0
        while index < len(paragraph_queue):
            current = paragraph_queue[index]
            ordered_match = ORDERED_LIST_ITEM_RE.match(current)
            if not ordered_match:
                if _looks_like_subheading(current):
                    blocks.append(f"<h3>{html.escape(current)}</h3>")
                elif _looks_like_structured_code_paragraph(current):
                    blocks.append(
                        _render_code_block_html(
                            current,
                            language="json",
                            copy_text=current,
                            wrap_hint=False,
                            overflow_hint="toggle",
                        )
                    )
                else:
                    for paragraph in _split_reader_display_paragraphs(current):
                        blocks.append(f"<p>{_render_inline_html(paragraph)}</p>")
                index += 1
                continue

            start = int(ordered_match.group("index"))
            items: list[str] = []
            while index < len(paragraph_queue):
                item_match = ORDERED_LIST_ITEM_RE.match(paragraph_queue[index])
                if not item_match:
                    break
                item_body = item_match.group("body").strip()
                index += 1
                if _is_low_signal_ordered_item_body(item_body):
                    continue
                item_body_parts = [_render_inline_html(item_body)]
                while index < len(paragraph_queue):
                    continuation = paragraph_queue[index]
                    if ORDERED_LIST_ITEM_RE.match(continuation) or _looks_like_subheading(continuation):
                        break
                    for paragraph in _split_reader_display_paragraphs(continuation):
                        item_body_parts.append(
                            "<p>{}</p>".format(_render_inline_html(paragraph))
                        )
                    index += 1
                items.append("<li>{}</li>".format("".join(item_body_parts)))
            if items:
                blocks.append(
                    '<ol class="normalized-ordered-list" start="{}">{}</ol>'.format(
                        start,
                        "".join(items),
                    )
                )
        paragraph_queue = []

    for part in NORMALIZED_BLOCK_RE.split(normalized):
        if not part:
            continue
        stripped = part.strip()
        if not stripped:
            continue
        code_match = CODE_BLOCK_RE.match(stripped)
        if code_match:
            flush_paragraph_queue()
            attrs = _parse_marker_attrs(code_match.group("attrs"))
            code_text = code_match.group("body").strip("\n")
            blocks.append(
                _render_code_block_html(
                    code_text,
                    language=str(attrs.get("language") or "shell").strip() or "shell",
                    copy_text=code_text,
                    wrap_hint=_parse_bool_attr(attrs.get("wrap_hint"), False),
                    overflow_hint=str(attrs.get("overflow_hint") or "toggle").strip() or "toggle",
                    caption=str(attrs.get("caption") or "").strip(),
                    preserve_layout=_looks_like_ascii_grid(code_text),
                )
            )
            continue
        table_match = TABLE_BLOCK_RE.match(stripped)
        if table_match:
            flush_paragraph_queue()
            attrs = _parse_marker_attrs(table_match.group("attrs"))
            table_text = table_match.group("body").strip("\n")
            blocks.append(
                _render_table_block_html(
                    table_text,
                    caption=str(attrs.get("caption") or "").strip(),
                )
            )
            continue
        figure_match = FIGURE_BLOCK_RE.match(stripped)
        if figure_match:
            flush_paragraph_queue()
            attrs = _parse_marker_attrs(figure_match.group("attrs"))
            blocks.append(
                _render_figure_block_html(
                    str(attrs.get("src") or "").strip(),
                    caption=html.unescape(figure_match.group("body").strip()),
                    alt=str(attrs.get("alt") or "").strip(),
                    kind=str(attrs.get("kind") or "").strip(),
                    diagram_type=str(attrs.get("diagram_type") or "").strip(),
                )
            )
            continue
        for paragraph in re.split(r"\n\s*\n+", stripped):
            if _looks_like_markdown_table_block(paragraph):
                flush_paragraph_queue()
                blocks.append(_render_table_block_html(paragraph))
                continue
            cleaned = re.sub(r"\s*\n\s*", " ", paragraph).strip()
            if not cleaned:
                continue
            paragraph_queue.append(cleaned)
    flush_paragraph_queue()
    return "\n".join(blocks)
