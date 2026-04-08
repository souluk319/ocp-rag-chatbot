# 내부 /docs viewer HTML과 viewer_path 파싱 규칙을 만드는 파일.
import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from play_book_studio.config.settings import load_settings

NORMALIZED_BLOCK_RE = re.compile(r"(\[CODE\].*?\[/CODE\]|\[TABLE\].*?\[/TABLE\])", re.DOTALL)
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


def _looks_like_subheading(text: str) -> bool:
    stripped = text.strip()
    if not stripped or len(stripped) > 36:
        return False
    if re.search(r"(?:니다|합니다|하십시오|하세요|[\.\?\!])", stripped):
        return False
    return True


def _render_code_block_html(code_text: str, *, language: str = "shell") -> str:
    copy_payload = html.escape(json.dumps(code_text), quote=True)
    return """
    <section class="code-block">
      <div class="code-header">
        <span class="code-label">{language}</span>
        <button type="button" class="copy-button" data-copy="{copy_payload}" onclick="copyViewerCode(this)">복사</button>
      </div>
      <pre><code>{code}</code></pre>
    </section>
    """.format(
        language=html.escape(language),
        copy_payload=copy_payload,
        code=html.escape(code_text),
    ).strip()


def _render_table_block_html(table_text: str) -> str:
    rows = [
        [cell.strip() for cell in row.split(" | ")]
        for row in table_text.splitlines()
        if row.strip()
    ]
    if not rows:
        return ""

    body_rows: list[str] = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return """
    <div class="table-wrap">
      <table>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
    """.format(rows="".join(body_rows)).strip()


def _render_normalized_section_html(text: str) -> str:
    blocks: list[str] = []
    normalized = _clean_source_view_text(text)
    for part in NORMALIZED_BLOCK_RE.split(normalized):
        if not part:
            continue
        stripped = part.strip()
        if not stripped:
            continue
        if stripped.startswith("[CODE]") and stripped.endswith("[/CODE]"):
            code_text = stripped[len("[CODE]") : -len("[/CODE]")].strip("\n")
            blocks.append(_render_code_block_html(code_text))
            continue
        if stripped.startswith("[TABLE]") and stripped.endswith("[/TABLE]"):
            table_text = stripped[len("[TABLE]") : -len("[/TABLE]")].strip("\n")
            blocks.append(_render_table_block_html(table_text))
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
        section_path = [str(item) for item in (row.get("section_path") or []) if str(item).strip()]
        breadcrumb = " > ".join(section_path) if section_path else heading
        section_text = _clean_source_view_text(str(row.get("text") or ""))
        is_target = bool(target_anchor) and anchor == target_anchor
        cards.append(
            """
            <section id="{anchor}" class="section-card{target_class}">
              <div class="section-meta">{breadcrumb}</div>
              <h2>{heading}</h2>
              <div class="section-body">{text}</div>
            </section>
            """.format(
                anchor=html.escape(anchor, quote=True),
                target_class=" is-target" if is_target else "",
                breadcrumb=html.escape(breadcrumb),
                heading=html.escape(heading),
                text=_render_normalized_section_html(section_text),
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
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(75, 48, 26, 0.06);
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
          }}
          .actions {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 18px;
          }}
          .actions a {{
            text-decoration: none;
            color: var(--accent);
            font-weight: 700;
          }}
          .section-list {{
            display: grid;
            gap: 16px;
            margin-top: 20px;
          }}
          .section-card {{
            background: rgba(255, 253, 248, 0.94);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 18px;
            scroll-margin-top: 20px;
          }}
          .section-card.is-target {{
            border-color: var(--accent);
            background: var(--accent-soft);
          }}
          .section-card h2 {{
            margin: 6px 0 10px;
            font-size: 1.15rem;
            line-height: 1.4;
          }}
          .section-body {{
            display: grid;
            gap: 14px;
          }}
          .section-body p,
          .section-body h3 {{
            margin: 0;
          }}
          .section-body h3 {{
            font-size: 1rem;
            color: var(--accent);
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
            border: 1px solid rgba(31, 28, 24, 0.08);
            border-radius: 16px;
            overflow: hidden;
            background: #fcfbf8;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
          }}
          .code-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 10px 12px;
            background: #f3ece2;
            border-bottom: 1px solid rgba(31, 28, 24, 0.08);
          }}
          .code-label {{
            color: #7e6c58;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }}
          .copy-button {{
            border: 1px solid rgba(31, 28, 24, 0.08);
            border-radius: 10px;
            padding: 7px 11px;
            background: rgba(255, 255, 255, 0.85);
            color: var(--ink);
            font: inherit;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
          }}
          .copy-button.is-copied {{
            background: rgba(138, 45, 28, 0.12);
            color: var(--accent);
          }}
          .code-block pre {{
            margin: 0;
            padding: 16px 18px 18px;
            overflow-x: auto;
            white-space: pre;
            background: #fffdfa;
            color: #2e261f;
            font-family: "SF Mono", "Menlo", monospace;
            font-size: 0.92rem;
            line-height: 1.65;
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
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.88);
          }}
          table {{
            width: 100%;
            border-collapse: collapse;
          }}
          td {{
            padding: 10px 12px;
            border-bottom: 1px solid rgba(216, 204, 184, 0.7);
            text-align: left;
            vertical-align: top;
            font-size: 0.94rem;
            line-height: 1.5;
          }}
          tr:last-child td {{
            border-bottom: 0;
          }}
          .section-meta {{
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.5;
          }}
        </style>
        <script>
          async function copyViewerCode(button) {{
            try {{
              const text = JSON.parse(button.dataset.copy || '""');
              if (navigator.clipboard && navigator.clipboard.writeText) {{
                await navigator.clipboard.writeText(text);
              }}
              const original = button.textContent;
              button.textContent = "복사됨";
              button.classList.add("is-copied");
              window.setTimeout(() => {{
                button.textContent = original;
                button.classList.remove("is-copied");
              }}, 1400);
            }} catch (error) {{
              button.textContent = "실패";
              window.setTimeout(() => {{
                button.textContent = "복사";
              }}, 1400);
            }}
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
