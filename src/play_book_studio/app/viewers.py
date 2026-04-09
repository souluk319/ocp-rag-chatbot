# 내부 /docs viewer HTML과 viewer_path 파싱 규칙을 만드는 파일.
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from play_book_studio.config.settings import load_settings

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
VIEWER_PATH_RE = re.compile(r"^/docs/ocp/[^/]+/[^/]+/([^/]+)/index\.html$")


def _viewer_path_to_local_html(root_dir: Path, viewer_path: str) -> Path | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None
    book_slug, _ = parsed
    settings = load_settings(root_dir)
    candidate = settings.raw_html_dir / f"{book_slug}.html"
    if not candidate.exists():
        return None
    return candidate


def _parse_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    parsed = urlparse((viewer_path or "").strip())
    path_part = parsed.path.strip()
    match = VIEWER_PATH_RE.fullmatch(path_part)
    if match is None:
        return None
    return match.group(1), parsed.fragment.strip()


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


def _render_code_block_html(
    code_text: str,
    *,
    language: str = "shell",
    copy_text: str = "",
    wrap_hint: bool = False,
    overflow_hint: str = "toggle",
    caption: str = "",
) -> str:
    copy_payload = html.escape(json.dumps(copy_text or code_text), quote=True)
    classes = ["code-block"]
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
        return _render_code_block_html(
            str(block.get("code") or "").strip(),
            language=str(block.get("language") or "shell").strip() or "shell",
            copy_text=str(block.get("copy_text") or "").strip(),
            wrap_hint=bool(block.get("wrap_hint", True)),
            overflow_hint=str(block.get("overflow_hint") or "toggle").strip() or "toggle",
            caption=str(block.get("caption") or "").strip(),
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
            )
            )
            continue
        table_match = TABLE_BLOCK_RE.match(stripped)
        if table_match:
            attrs = _parse_marker_attrs(table_match.group("attrs"))
            table_text = table_match.group("body").strip("\n")
            blocks.append(_render_table_block_html(table_text, caption=str(attrs.get("caption") or "").strip()))
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


def _build_study_section_cards(
    sections: list[dict[str, Any]],
    *,
    target_anchor: str = "",
) -> list[str]:
    cards: list[str] = []
    for row in sections:
        anchor = str(row.get("anchor") or "")
        heading = str(row.get("heading") or "")
        section_path = [
            str(item)
            for item in (row.get("section_path") or row.get("path") or [])
            if str(item).strip()
        ]
        breadcrumb = " > ".join(section_path) if section_path else heading
        section_text = _clean_source_view_text(str(row.get("text") or ""))
        is_target = bool(target_anchor) and anchor == target_anchor
        blocks = [dict(block) for block in (row.get("blocks") or []) if isinstance(block, dict)]
        rendered_body = (
            "\n".join(
                fragment for fragment in (_render_playbook_block_html(block) for block in blocks) if fragment
            )
            if blocks
            else _render_normalized_section_html(section_text)
        )
        cards.append(
            """
            <section id="{anchor}" class="section-card{target_class}">
              <div class="section-header">
                <div class="section-meta">{breadcrumb}</div>
                <h2>{heading}</h2>
              </div>
              <div class="section-body">{text}</div>
            </section>
            """.format(
                anchor=html.escape(anchor, quote=True),
                target_class=" is-target" if is_target else "",
                breadcrumb=html.escape(breadcrumb),
                heading=html.escape(heading),
                text=rendered_body,
            ).strip()
        )
    return cards


def _render_study_viewer_html(
    *,
    title: str,
    source_url: str,
    cards: list[str],
    section_count: int,
    eyebrow: str,
    summary: str,
) -> str:
    return """
    <!DOCTYPE html>
    <html lang="ko">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{title} - OCP 출처 뷰어</title>
        <style>
          :root {{
            color-scheme: light;
            --bg: #f5f1e8;
            --panel: #fffdf8;
            --line: #d8ccb8;
            --ink: #1f1c18;
            --muted: #675f54;
            --accent: #8a2d1c;
            --accent-soft: #f7e1da;
          }}
          * {{
            box-sizing: border-box;
          }}
          body {{
            margin: 0;
            background:
              radial-gradient(circle at top right, rgba(214, 123, 92, 0.16), transparent 24rem),
              linear-gradient(180deg, #f7f0e6 0%, var(--bg) 100%);
            color: var(--ink);
            font-family: "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
          }}
          main {{
            width: min(1480px, calc(100vw - 32px));
            max-width: none;
            margin: 0 auto;
            padding: 28px 0 44px;
          }}
          .hero {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 28px 30px;
            box-shadow:
              0 20px 50px rgba(75, 48, 26, 0.08),
              inset 0 1px 0 rgba(255, 255, 255, 0.8);
          }}
          .eyebrow {{
            color: var(--accent);
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }}
          h1 {{
            margin: 10px 0 8px;
            font-size: clamp(1.8rem, 3vw, 2.7rem);
            line-height: 1.15;
          }}
          .summary {{
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
            max-width: 72ch;
          }}
          .actions {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 18px;
            align-items: center;
          }}
          .meta-pill,
          .actions a {{
            display: inline-flex;
            align-items: center;
            min-height: 38px;
            padding: 0 14px;
            border: 1px solid rgba(138, 45, 28, 0.16);
            border-radius: 999px;
            background: rgba(255, 249, 243, 0.9);
            color: var(--accent);
            font-size: 0.88rem;
            font-weight: 700;
            text-decoration: none;
          }}
          .section-list {{
            display: grid;
            gap: 18px;
            margin-top: 24px;
          }}
          .section-card {{
            background: rgba(255, 253, 248, 0.94);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 20px 22px 22px;
            scroll-margin-top: 20px;
            box-shadow: 0 12px 30px rgba(75, 48, 26, 0.05);
          }}
          .section-card.is-target {{
            border-color: var(--accent);
            background: var(--accent-soft);
            box-shadow: 0 18px 34px rgba(138, 45, 28, 0.12);
          }}
          .section-header {{
            display: grid;
            gap: 8px;
            padding-bottom: 14px;
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(216, 204, 184, 0.75);
          }}
          .section-card h2 {{
            margin: 0;
            font-size: 1.2rem;
            line-height: 1.45;
            letter-spacing: -0.01em;
          }}
          .section-body {{
            display: grid;
            gap: 16px;
          }}
          .section-body p,
          .section-body h3 {{
            margin: 0;
          }}
          .section-body h3 {{
            padding-top: 6px;
            font-size: 1rem;
            color: var(--accent);
            letter-spacing: -0.01em;
          }}
          .section-body code {{
            display: inline;
            padding: 0.08rem 0.32rem;
            border-radius: 6px;
            border: 1px solid rgba(138, 45, 28, 0.12);
            background: rgba(138, 45, 28, 0.05);
            color: #7c2f21;
            font-family: "SF Mono", "Menlo", monospace;
            font-size: 0.92em;
          }}
          .code-block {{
            border: 1px solid rgba(31, 28, 24, 0.1);
            border-radius: 18px;
            overflow: hidden;
            background: linear-gradient(180deg, #fffdf9 0%, #fbf6ef 100%);
            box-shadow:
              inset 0 1px 0 rgba(255, 255, 255, 0.75),
              0 8px 24px rgba(45, 31, 22, 0.05);
          }}
          .code-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 12px 14px;
            background: linear-gradient(180deg, #f5eee3 0%, #efe4d6 100%);
            border-top: 1px solid rgba(255, 255, 255, 0.8);
            border-bottom: 1px solid rgba(31, 28, 24, 0.08);
          }}
          .code-label {{
            color: #7e6c58;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }}
          .code-caption,
          .table-caption {{
            padding: 14px 16px 0;
            color: #544b42;
            font-size: 0.8rem;
            font-weight: 700;
            line-height: 1.5;
            letter-spacing: 0.02em;
          }}
          .copy-button {{
            border: 1px solid rgba(31, 28, 24, 0.08);
            border-radius: 999px;
            padding: 7px 11px;
            background: rgba(255, 255, 255, 0.85);
            color: var(--ink);
            font: inherit;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
          }}
          .code-actions {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
          }}
          .copy-button.is-copied {{
            background: rgba(138, 45, 28, 0.12);
            color: var(--accent);
          }}
          .code-block.is-wrapped pre,
          .code-block.is-wrapped code {{
            white-space: pre-wrap;
            word-break: break-word;
          }}
          .code-block.is-expanded {{
            margin-inline: -10px;
          }}
          .code-block.is-expanded pre {{
            overflow-x: visible;
          }}
          .code-block pre {{
            margin: 0;
            padding: 18px 20px 20px;
            overflow-x: auto;
            white-space: pre;
            background: rgba(255, 253, 250, 0.92);
            color: #2f261e;
            font-family: "SF Mono", "Menlo", monospace;
            font-size: 0.92rem;
            line-height: 1.7;
          }}
          .code-block code {{
            display: block;
            padding: 0;
            border: 0;
            border-radius: 0;
            background: transparent;
            color: inherit;
            font: inherit;
            white-space: inherit;
          }}
          .table-wrap {{
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
          }}
          table {{
            width: 100%;
            border-collapse: collapse;
          }}
          th,
          td {{
            padding: 12px 14px;
            border-bottom: 1px solid rgba(216, 204, 184, 0.7);
            text-align: left;
            vertical-align: top;
            font-size: 0.94rem;
            line-height: 1.5;
          }}
          th {{
            background: #f7efe4;
            color: #5f4632;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            text-transform: uppercase;
          }}
          tbody tr:nth-child(even) {{
            background: rgba(248, 241, 231, 0.42);
          }}
          tr:last-child td {{
            border-bottom: 0;
          }}
          .section-meta {{
            color: var(--muted);
            font-size: 0.86rem;
            font-weight: 700;
            line-height: 1.5;
          }}
          .list-block,
          .procedure-list,
          .substep-list {{
            margin: 0;
            padding-left: 1.2rem;
          }}
          .procedure-list {{
            display: grid;
            gap: 12px;
            counter-reset: playbook-step;
            list-style: none;
            padding-left: 0;
          }}
          .procedure-list > li {{
            position: relative;
            display: grid;
            gap: 8px;
            padding: 14px 16px 14px 58px;
            border: 1px solid rgba(216, 204, 184, 0.8);
            border-radius: 16px;
            background: rgba(255, 252, 246, 0.96);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
          }}
          .procedure-list > li::before {{
            counter-increment: playbook-step;
            content: counter(playbook-step);
            position: absolute;
            left: 16px;
            top: 14px;
            width: 28px;
            height: 28px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            background: rgba(138, 45, 28, 0.12);
            color: var(--accent);
            font-size: 0.82rem;
            font-weight: 800;
          }}
          .step-text {{
            font-weight: 600;
          }}
          .substep-list {{
            margin-top: 2px;
            color: var(--muted);
          }}
          .note-card {{
            border: 1px solid rgba(138, 45, 28, 0.12);
            border-left: 5px solid rgba(138, 45, 28, 0.45);
            border-radius: 16px;
            padding: 16px 18px;
            background: linear-gradient(180deg, rgba(138, 45, 28, 0.04) 0%, rgba(138, 45, 28, 0.07) 100%);
          }}
          .note-card.note-warning,
          .note-card.note-caution {{
            background: #fff4e5;
            border-color: #f0c36d;
            border-left-color: #c98c2f;
          }}
          .note-card.note-important {{
            background: #fdeceb;
            border-color: #e7a49c;
            border-left-color: #c95f50;
          }}
          .note-card.note-tip {{
            background: #edf7f1;
            border-color: #9fd0b1;
            border-left-color: #4d946a;
          }}
          .note-title {{
            margin-bottom: 8px;
            color: var(--accent);
            font-size: 0.92rem;
            font-weight: 800;
          }}
        </style>
        <script>
          async function copyViewerCode(button) {{
            try {{
              const text = JSON.parse(button.dataset.copy || '""');
              const label = button.dataset.labelDefault || "복사";
              if (navigator.clipboard && navigator.clipboard.writeText) {{
                await navigator.clipboard.writeText(text);
              }}
              button.textContent = "복사됨";
              button.classList.add("is-copied");
              window.setTimeout(() => {{
                button.textContent = label;
                button.classList.remove("is-copied");
              }}, 1400);
            }} catch (error) {{
              button.textContent = "실패";
              window.setTimeout(() => {{
                button.textContent = button.dataset.labelDefault || "복사";
              }}, 1400);
            }}
          }}
          function toggleViewerCodeWrap(button) {{
            const block = button.closest(".code-block");
            if (!block) return;
            block.classList.toggle("is-wrapped");
            const wrapped = block.classList.contains("is-wrapped");
            button.setAttribute("aria-pressed", wrapped ? "true" : "false");
            button.textContent = wrapped
              ? (button.dataset.labelActive || "줄바꿈 해제")
              : (button.dataset.labelDefault || "줄바꿈");
          }}
          function toggleViewerCodeOverflow(button) {{
            const block = button.closest(".code-block");
            if (!block) return;
            block.classList.toggle("is-expanded");
            const expanded = block.classList.contains("is-expanded");
            button.setAttribute("aria-pressed", expanded ? "true" : "false");
            button.textContent = expanded
              ? (button.dataset.labelActive || "기본 폭")
              : (button.dataset.labelDefault || "넓게 보기");
          }}
        </script>
      </head>
      <body>
        <main>
          <section class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="summary">{summary}</p>
            <div class="actions">
              <span>섹션 수: {section_count}</span>
              <a href="{source_url}" target="_blank" rel="noreferrer">원문 열기</a>
            </div>
          </section>
          <div class="section-list">
            {cards}
          </div>
        </main>
      </body>
    </html>
    """.format(
        title=html.escape(title),
        eyebrow=html.escape(eyebrow),
        summary=html.escape(summary),
        section_count=section_count,
        source_url=html.escape(source_url, quote=True),
        cards="\n".join(cards),
    ).strip()
