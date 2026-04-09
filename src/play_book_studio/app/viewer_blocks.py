# 플레이북 문서의 section body를 HTML 블록으로 렌더링한다.
import html
import json
import re
from typing import Any

NORMALIZED_BLOCK_RE = re.compile(
    r"(\[CODE(?:\s+[^\]]+)?\].*?\[/CODE\]|\[TABLE(?:\s+[^\]]+)?\].*?\[/TABLE\])",
    re.DOTALL,
)
MARKER_ATTR_RE = re.compile(r'([a-z_]+)="((?:[^"\\]|\\.)*)"')
CODE_BLOCK_RE = re.compile(r"^\[CODE(?P<attrs>[^\]]*)\]\s*(?P<body>.*?)\s*\[/CODE\]$", re.DOTALL)
TABLE_BLOCK_RE = re.compile(r"^\[TABLE(?P<attrs>[^\]]*)\]\s*(?P<body>.*?)\s*\[/TABLE\]$", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
SOURCE_VIEW_LEADING_NOISE_RE = re.compile(
    r"^\s*Red Hat OpenShift Documentation Team(?:\s+법적 공지)?(?:\s+초록)?\s*",
)
SOURCE_VIEW_TOC_RE = re.compile(r"^\s*목차\s*(?:\n\n|\n)?")
ASCII_GRID_BORDER_RE = re.compile(r"^\s*[+\-=:]{3,}\s*$")
ASCII_GRID_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")


def _clean_source_view_text(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = SOURCE_VIEW_LEADING_NOISE_RE.sub("", cleaned, count=1).lstrip()
    cleaned = SOURCE_VIEW_TOC_RE.sub("", cleaned, count=1).lstrip()
    return cleaned


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
    overflow_button = ""
    if overflow_hint != "inline":
        overflow_button = (
            '<button type="button" class="copy-button" data-label-default="넓게 보기" '
            'data-label-active="기본 폭" aria-pressed="false" '
            'onclick="toggleViewerCodeOverflow(this)">넓게 보기</button>'
        )
    return """
    <section class="{classes}">
      {caption_html}
      <div class="code-header">
        <span class="code-label">{language}</span>
        <div class="code-actions">
          <button type="button" class="copy-button" data-copy="{copy_payload}" data-label-default="복사" onclick="copyViewerCode(this)">복사</button>
          <button type="button" class="copy-button" data-label-default="줄바꿈" data-label-active="줄바꿈 해제" aria-pressed="{wrap_pressed}" onclick="toggleViewerCodeWrap(this)">{wrap_label}</button>
          {overflow_button}
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
        wrap_label="줄바꿈 해제" if wrap_hint else "줄바꿈",
        overflow_button=overflow_button,
        code=html.escape(code_text),
    ).strip()


def _render_table_block_html(table_text: str, *, caption: str = "") -> str:
    rows = [
        [cell.strip() for cell in row.split("|")]
        for row in table_text.splitlines()
        if row.strip()
    ]
    if not rows:
        return ""
    headers = rows[0]
    body = rows[1:]
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


def _render_playbook_block_html(block: dict[str, Any]) -> str:
    kind = str(block.get("kind") or "").strip()
    if kind == "paragraph":
        return f"<p>{_render_inline_html(str(block.get('text') or '').strip())}</p>"
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
                '<li><div class="step-text">{}</div>{}</li>'.format(
                    _render_inline_html(text),
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
    for part in NORMALIZED_BLOCK_RE.split(normalized):
        if not part:
            continue
        stripped = part.strip()
        if not stripped:
            continue
        code_match = CODE_BLOCK_RE.match(stripped)
        if code_match:
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
            attrs = _parse_marker_attrs(table_match.group("attrs"))
            table_text = table_match.group("body").strip("\n")
            blocks.append(
                _render_table_block_html(
                    table_text,
                    caption=str(attrs.get("caption") or "").strip(),
                )
            )
            continue
        for paragraph in re.split(r"\n\s*\n+", stripped):
            cleaned = re.sub(r"\s*\n\s*", " ", paragraph).strip()
            if not cleaned:
                continue
            if _looks_like_subheading(cleaned):
                blocks.append(f"<h3>{html.escape(cleaned)}</h3>")
            else:
                blocks.append(f"<p>{_render_inline_html(cleaned)}</p>")
    return "\n".join(blocks)
