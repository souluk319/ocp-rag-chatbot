from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path

from .language_policy import describe_language_policy, load_language_policy_map
from .models import NormalizedSection
from .section_keys import assign_section_keys
from .settings import Settings


BLOCK_RE = re.compile(r"(\[CODE\].*?\[/CODE\]|\[TABLE\].*?\[/TABLE\])", re.DOTALL)
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
SPACE_RE = re.compile(r"\s+")


def _escape(value: str) -> str:
    return html.escape(value or "", quote=True)


def _normalize_inline_text(text: str) -> str:
    return SPACE_RE.sub(" ", (text or "").strip())


def _contains_hangul(text: str) -> bool:
    return bool(HANGUL_RE.search(text or ""))


def _render_table(block_text: str) -> str:
    lines = [line.strip() for line in block_text.splitlines() if line.strip()]
    if not lines:
        return ""
    rows: list[str] = []
    for line in lines:
        cells = [_escape(cell.strip()) for cell in line.split("|")]
        if not any(cells):
            continue
        row_html = "".join(f"<td>{cell}</td>" for cell in cells)
        rows.append(f"<tr>{row_html}</tr>")
    if not rows:
        return ""
    return "<div class=\"table-wrap\"><table>" + "".join(rows) + "</table></div>"


def _render_text_blocks(text: str) -> str:
    parts = BLOCK_RE.split(text or "")
    html_parts: list[str] = []

    for part in parts:
        if not part:
            continue
        stripped = part.strip()
        if not stripped:
            continue
        if stripped.startswith("[CODE]") and stripped.endswith("[/CODE]"):
            code = stripped[len("[CODE]") : -len("[/CODE]")].strip("\n")
            html_parts.append(f"<pre><code>{_escape(code)}</code></pre>")
            continue
        if stripped.startswith("[TABLE]") and stripped.endswith("[/TABLE]"):
            table_text = stripped[len("[TABLE]") : -len("[/TABLE]")].strip("\n")
            rendered = _render_table(table_text)
            if rendered:
                html_parts.append(rendered)
            continue

        paragraphs = [item.strip() for item in re.split(r"\n\s*\n", stripped) if item.strip()]
        for paragraph in paragraphs:
            rendered = "<br>".join(_escape(line.strip()) for line in paragraph.splitlines() if line.strip())
            if rendered:
                html_parts.append(f"<p>{rendered}</p>")

    return "\n".join(html_parts)


def _book_language_label(sections: list[NormalizedSection]) -> tuple[str, str]:
    if not sections:
        return "unknown", "본문이 비어 있습니다."
    hangul_sections = sum(int(_contains_hangul(section.text)) for section in sections)
    ratio = hangul_sections / max(len(sections), 1)
    if ratio >= 0.8:
        return "ko", "한국어 본문 중심 문서"
    if ratio >= 0.3:
        return "mixed", "한국어와 영어가 혼합된 문서"
    return "en", "영문 원문 비중이 높은 문서"


def render_book_viewer(
    book_slug: str,
    sections: list[NormalizedSection],
    *,
    policy: dict[str, object] | None = None,
) -> str:
    if not sections:
        raise ValueError(f"No sections available for {book_slug}")

    book_title = sections[0].book_title
    source_url = sections[0].source_url
    language_code, fallback_label = _book_language_label(sections)
    policy_display = describe_language_policy(policy) if policy else None
    language_label = policy_display["badge"] if policy_display else fallback_label
    language_note = policy_display["note"] if policy_display else fallback_label
    badge_tone = policy_display["tone"] if policy_display else (
        "warn" if language_code != "ko" else "normal"
    )

    toc_items: list[str] = []
    body_parts: list[str] = []

    for section in sections:
        heading_level = min(max(section.section_level + 1, 2), 6)
        heading = _escape(section.heading)
        anchor = _escape(section.section_key or section.anchor)
        path_text = " > ".join(section.section_path)
        toc_label = _escape(path_text or section.heading)
        toc_items.append(f"<li><a href=\"#{anchor}\">{toc_label}</a></li>")

        if path_text and path_text != section.heading:
            path_html = f"<div class=\"section-path\">{_escape(path_text)}</div>"
        else:
            path_html = ""

        body_parts.append(
            "\n".join(
                [
                    f"<section id=\"{anchor}\" class=\"doc-section\">",
                    path_html,
                    f"<h{heading_level}>{heading}</h{heading_level}>",
                    _render_text_blocks(section.text),
                    "</section>",
                ]
            )
        )

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_escape(book_title)}</title>
  <style>
    :root {{
      --bg: #f6f4ef;
      --panel: #fffdf8;
      --line: rgba(34, 39, 46, 0.12);
      --ink: #20252b;
      --muted: #5c6773;
      --accent: #0f766e;
      --warn: #b45309;
      --shadow: 0 18px 40px rgba(29, 25, 19, 0.08);
      --radius: 20px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI Variable", "Malgun Gothic", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15,118,110,0.12), transparent 28%),
        linear-gradient(180deg, #fbfaf7 0%, #f1ede4 100%);
      line-height: 1.72;
    }}
    .shell {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 28px 20px 40px;
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      gap: 20px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    aside {{
      padding: 18px;
      position: sticky;
      top: 18px;
      height: fit-content;
    }}
    main {{
      padding: 28px;
    }}
    h1 {{
      margin: 0 0 10px;
      line-height: 1.15;
      font-size: clamp(30px, 3vw, 42px);
    }}
    h2, h3, h4, h5, h6 {{
      line-height: 1.3;
      margin: 28px 0 10px;
      scroll-margin-top: 20px;
    }}
    .meta {{
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 18px;
    }}
    .badge {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      border: 1px solid var(--line);
      background: rgba(15,118,110,0.08);
      color: var(--accent);
    }}
    .badge.warn {{
      background: rgba(180,83,9,0.1);
      color: var(--warn);
    }}
    .source-link {{
      display: inline-block;
      margin-top: 12px;
      color: var(--accent);
      text-decoration: none;
      font-weight: 700;
    }}
    .source-link:hover {{
      text-decoration: underline;
    }}
    .toc-title {{
      margin: 0 0 12px;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .toc {{
      margin: 0;
      padding-left: 18px;
      font-size: 14px;
    }}
    .toc li + li {{
      margin-top: 8px;
    }}
    .toc a {{
      color: var(--ink);
      text-decoration: none;
    }}
    .toc a:hover {{
      color: var(--accent);
    }}
    .section-path {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 6px;
    }}
    .doc-section + .doc-section {{
      border-top: 1px solid var(--line);
      padding-top: 24px;
      margin-top: 24px;
    }}
    p {{
      margin: 10px 0;
    }}
    pre {{
      background: #1f2937;
      color: #f8fafc;
      padding: 16px;
      border-radius: 14px;
      overflow-x: auto;
      font-size: 13px;
      line-height: 1.6;
    }}
    code {{
      font-family: Consolas, "Cascadia Code", monospace;
    }}
    .table-wrap {{
      overflow-x: auto;
      margin: 12px 0;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      min-width: 420px;
      background: white;
    }}
    td {{
      border: 1px solid var(--line);
      padding: 10px 12px;
      vertical-align: top;
      font-size: 14px;
    }}
    @media (max-width: 980px) {{
      .shell {{
        grid-template-columns: 1fr;
      }}
      aside {{
        position: static;
      }}
      main {{
        padding: 22px;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="card">
      <div class="toc-title">Book</div>
      <strong>{_escape(book_slug)}</strong>
      <p class="meta">{_escape(language_note)}</p>
      <div class="toc-title">Sections</div>
      <ol class="toc">
        {''.join(toc_items)}
      </ol>
    </aside>
    <main class="card">
      <span class="badge{' warn' if badge_tone != 'normal' else ''}">{_escape(language_label)}</span>
      <h1>{_escape(book_title)}</h1>
      <div class="meta">{_escape(language_note)} 내부 문서 뷰어용 정제본이며, citation 클릭 시 이 페이지가 열리도록 설계합니다.</div>
      <a class="source-link" href="{_escape(source_url)}" target="_blank" rel="noreferrer">원본 출처 보기</a>
      {''.join(body_parts)}
    </main>
  </div>
</body>
</html>
"""


def write_viewer_docs(sections: list[NormalizedSection], settings: Settings) -> int:
    grouped: dict[str, list[NormalizedSection]] = defaultdict(list)
    policy_map = load_language_policy_map(settings)
    for section in sections:
        grouped[section.book_slug].append(section)

    written = 0
    for book_slug, book_sections in grouped.items():
        target_dir = settings.viewer_docs_dir / book_slug
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / "index.html"
        target_path.write_text(
            render_book_viewer(
                book_slug,
                book_sections,
                policy=policy_map.get(book_slug),
            ),
            encoding="utf-8",
        )
        written += 1
    return written


def read_normalized_sections(path: Path) -> list[NormalizedSection]:
    rows: list[NormalizedSection] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            rows.append(NormalizedSection(**payload))
    return assign_section_keys(rows)
