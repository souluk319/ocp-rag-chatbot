# section 카드와 문서 viewer 전체 HTML을 조립한다.
import html
import re
from typing import Any

from play_book_studio.app.viewer_blocks import (
    _clean_source_view_text,
    _render_normalized_section_html,
    _render_playbook_block_html,
)

HEADING_NUMBER_PREFIX_RE = re.compile(
    r"^\s*(?:chapter\s+\d+\.?\s*|\d+\s*장\.?\s*|(?:\d+|[A-Za-z])(?:\.\d+)*\.?\s+)",
    re.IGNORECASE,
)


def _display_heading(text: str) -> str:
    raw = " ".join(str(text or "").split()).strip()
    if not raw:
        return ""
    cleaned = HEADING_NUMBER_PREFIX_RE.sub("", raw).strip()
    return cleaned or raw


def _render_page_overlay_toolbar(
    *,
    target_kind: str,
    target_ref: str,
    title: str,
    book_slug: str = "",
    anchor: str = "",
    asset_name: str = "",
    entity_slug: str = "",
    viewer_path: str = "",
) -> str:
    return """
    <div class="overlay-page-target" hidden data-page-root="true" data-target-kind="{target_kind}" data-target-ref="{target_ref}" data-target-title="{title}" data-book-slug="{book_slug}" data-anchor="{anchor}" data-asset-name="{asset_name}" data-entity-slug="{entity_slug}" data-viewer-path="{viewer_path}"></div>
    """.format(
        target_kind=html.escape(target_kind, quote=True),
        target_ref=html.escape(target_ref, quote=True),
        title=html.escape(title, quote=True),
        book_slug=html.escape(book_slug, quote=True),
        anchor=html.escape(anchor, quote=True),
        asset_name=html.escape(asset_name, quote=True),
        entity_slug=html.escape(entity_slug, quote=True),
        viewer_path=html.escape(viewer_path, quote=True),
    ).strip()


def _build_study_section_cards(
    sections: list[dict[str, Any]],
    *,
    book_slug: str = "",
    target_anchor: str = "",
    embedded: bool = False,
) -> list[str]:
    cards: list[str] = []
    for row in sections:
        anchor = str(row.get("anchor") or "")
        heading = str(row.get("heading") or "")
        display_heading = _display_heading(heading)
        section_path = [
            _display_heading(str(item))
            for item in (row.get("section_path") or row.get("path") or [])
            if str(item).strip()
        ]
        level = max(1, int(row.get("level") or row.get("section_level") or len(section_path) or 1))
        breadcrumb = " > ".join(item for item in section_path if item) if section_path else display_heading
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
        if embedded:
            cards.append(
                """
                <section id="{anchor}" class="embedded-section{target_class}">
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
                    heading=html.escape(display_heading),
                    text=rendered_body,
                ).strip()
            )
            continue
        cards.append(
            """
            <section id="{anchor}" class="section-card section-level-{level}{target_class}" data-semantic-role="{semantic_role}" data-section-level="{level}">
              <div class="section-header">
                <div class="section-meta">{breadcrumb}</div>
                <h2>{heading}</h2>
              </div>
              <div class="section-body">{text}</div>
            </section>
            """.format(
                anchor=html.escape(anchor, quote=True),
                level=level,
                target_class=" is-target" if is_target else "",
                semantic_role=html.escape(str(row.get("semantic_role") or "").strip(), quote=True),
                breadcrumb=html.escape(breadcrumb),
                heading=html.escape(display_heading),
                text=rendered_body,
            ).strip()
        )
    return cards


def _build_section_outline(sections: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, str]]:
    outline: list[dict[str, str]] = []
    for row in sections:
        anchor = str(row.get("anchor") or "").strip()
        heading = _display_heading(str(row.get("heading") or ""))
        if not anchor or not heading:
            continue
        path = [
            _display_heading(str(item))
            for item in (row.get("section_path") or row.get("path") or [])
            if str(item).strip()
        ]
        outline.append(
            {
                "anchor": anchor,
                "heading": heading,
                "path": " > ".join(item for item in path if item) or heading,
            }
        )
        if len(outline) >= limit:
            break
    return outline


def _build_section_metrics(sections: list[dict[str, Any]]) -> list[str]:
    semantic_counts: dict[str, int] = {}
    figure_count = 0
    code_count = 0
    table_count = 0
    for row in sections:
        semantic_role = str(row.get("semantic_role") or "").strip().lower()
        if semantic_role:
            semantic_counts[semantic_role] = semantic_counts.get(semantic_role, 0) + 1
        for block in row.get("blocks") or []:
            if not isinstance(block, dict):
                continue
            kind = str(block.get("kind") or "").strip().lower()
            if kind == "figure":
                figure_count += 1
            elif kind == "code":
                code_count += 1
            elif kind == "table":
                table_count += 1
    metrics = [f"섹션 {len(sections)}"]
    if semantic_counts.get("procedure"):
        metrics.append(f"절차 {semantic_counts['procedure']}")
    if semantic_counts.get("reference"):
        metrics.append(f"참조 {semantic_counts['reference']}")
    if figure_count:
        metrics.append(f"figure {figure_count}")
    if table_count:
        metrics.append(f"table {table_count}")
    if code_count:
        metrics.append(f"code {code_count}")
    return metrics[:5]


def _render_study_viewer_html(
    *,
    title: str,
    source_url: str,
    cards: list[str],
    supplementary_blocks: list[str] | None = None,
    section_count: int,
    eyebrow: str,
    summary: str,
    embedded: bool = False,
    page_overlay_toolbar: str = "",
    section_outline: list[dict[str, str]] | None = None,
    section_metrics: list[str] | None = None,
) -> str:
    hero_block = ""
    embedded_meta_block = ""
    document_class = "study-document"
    hero_meta_block = ""
    hero_outline_block = ""
    hero_metric_pills = "".join(
        '<span class="meta-pill">{}</span>'.format(html.escape(metric))
        for metric in (section_metrics or [])
        if str(metric).strip()
    )
    if section_outline and not embedded:
        hero_outline_links = "".join(
            """
            <a class="hero-jump-link" href="#{anchor}" title="{path}">{heading}</a>
            """.format(
                anchor=html.escape(str(item.get("anchor") or ""), quote=True),
                path=html.escape(str(item.get("path") or "")),
                heading=html.escape(str(item.get("heading") or "")),
            ).strip()
            for item in section_outline
            if str(item.get("anchor") or "").strip() and str(item.get("heading") or "").strip()
        )
        if hero_outline_links:
            hero_outline_block = """
              <div class="hero-outline">
                <div class="hero-outline-label">Quick Navigation</div>
                <div class="hero-outline-links">{hero_outline_links}</div>
              </div>
            """.format(hero_outline_links=hero_outline_links)
    if not embedded:
        hero_meta_block = """
            <div class="hero-meta">
              {hero_metric_pills}
              <span class="meta-pill meta-pill-accent">{eyebrow}</span>
              {source_link}
            </div>
        """
        hero_block = """
          <section class="hero">
            <div class="hero-grid">
              <div class="hero-main">
                <div class="eyebrow">{eyebrow}</div>
                <h1>{title}</h1>
                <p class="summary">{summary}</p>
                {hero_outline_block}
                {page_overlay_toolbar}
              </div>
              <div class="actions hero-actions">
                {hero_meta_block}
              </div>
            </div>
          </section>
        """
    else:
        document_class = "study-document study-document-embedded"
        if source_url:
            embedded_meta_block = """
              <div class="embedded-origin-row">
                <a class="embedded-origin-link" href="{source_url}" target="_blank" rel="noreferrer">공식 매뉴얼 원문</a>
              </div>
            """
        if page_overlay_toolbar:
            embedded_meta_block = (embedded_meta_block + page_overlay_toolbar) if embedded_meta_block else page_overlay_toolbar
    extra_blocks = "\n".join(supplementary_blocks or [])
    reader_sidebar = ""
    if extra_blocks and not embedded:
        reader_sidebar = '<aside class="reader-sidebar">{}</aside>'.format(extra_blocks)
        extra_blocks = ""
    return """
    <!DOCTYPE html>
    <html lang="ko">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{title} - OCP 출처 뷰어</title>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
          
          :root {{
            color-scheme: light;
            --bg: #ffffff;
            --panel: #ffffff;
            --panel-soft: #f9fafb;
            --line: #e2e8f0;
            --line-strong: #cbd5e1;
            --ink: #0f172a;
            --ink-soft: #334155;
            --muted: #64748b;
            --accent: #2563eb;
            --accent-soft: #eff6ff;
            --border-radius: 12px;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
          }}
          * {{
            box-sizing: border-box;
          }}
          body {{
            margin: 0;
            background: var(--bg);
            color: var(--ink);
            font-family: 'Inter', 'Noto Sans KR', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }}
          body.is-embedded {{
            background: #ffffff;
            margin: 0;
            padding: 0;
          }}
          html, body {{
            max-width: 100%;
          }}
          main {{
            width: min(1000px, calc(100vw - 48px));
            max-width: 100%;
            min-width: 0;
            margin: 0 auto;
            padding: 40px 0 80px;
          }}
          body.is-embedded main {{
            width: 100%;
            margin: 0;
            padding: 32px 48px;
            min-height: 100%;
            min-width: 0;
          }}
          .study-document-embedded {{
            min-height: 100%;
            padding: 0;
            border: 0;
            background: transparent;
            box-shadow: none;
            min-width: 0;
          }}
          
          /* Hero Section */
          .hero {{
            margin: 0 0 50px;
            padding: 0 0 40px;
            border-bottom: 1px solid var(--line);
          }}
          body.is-embedded .hero {{
            margin: 0 0 32px;
            padding: 0;
            border-bottom: 0;
          }}
          .hero-grid {{
            display: grid;
            grid-template-columns: minmax(0, 1fr);
            gap: 20px;
            min-width: 0;
          }}
          .hero-main {{
            display: grid;
            gap: 16px;
            max-width: 100%;
            min-width: 0;
          }}
          .eyebrow {{
            color: var(--accent);
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }}
          h1 {{
            margin: 0;
            font-size: clamp(2.2rem, 4.5vw, 3.2rem);
            line-height: 1.15;
            letter-spacing: -0.02em;
            font-weight: 800;
            color: var(--ink);
            max-width: 100%;
            overflow-wrap: anywhere;
            word-break: keep-all;
          }}
          body.is-embedded h1 {{
            font-size: clamp(1.8rem, 3.8vw, 2.6rem);
            margin-bottom: 8px;
          }}
          .summary {{
            margin: 0;
            color: var(--ink-soft);
            font-size: 1.125rem;
            line-height: 1.7;
            max-width: 100%;
            overflow-wrap: break-word;
            word-break: keep-all;
          }}
          
          /* Hero Outline (Quick Navigation) */
          .hero-outline {{
            margin-top: 12px;
            padding: 16px;
            background: var(--panel-soft);
            border-radius: var(--border-radius);
            border: 1px solid var(--line);
          }}
          .hero-outline-label {{
            font-size: 0.8125rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted);
            margin-bottom: 12px;
          }}
          .hero-outline-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
          }}
          .hero-jump-link {{
            color: var(--accent);
            text-decoration: underline;
            text-decoration-color: transparent;
            font-size: 0.9375rem;
            line-height: 1.4;
            transition: text-decoration-color 0.2s ease;
          }}
          .hero-jump-link:hover {{
            text-decoration-color: var(--accent);
          }}
          
          .hero-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            margin-top: 12px;
            max-width: 100%;
            min-width: 0;
          }}
          .meta-pill, .hero-meta a {{
            display: inline-flex;
            align-items: center;
            min-height: 32px;
            padding: 0 16px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: var(--panel-soft);
            color: var(--ink-soft);
            font-size: 0.875rem;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
            max-width: 100%;
            min-width: 0;
          }}
          .meta-pill:hover, .hero-meta a:hover {{
            background: #f1f5f9;
            border-color: var(--line-strong);
            color: var(--ink);
          }}
          .meta-pill-accent {{
            color: var(--accent);
            border-color: #bfdbfe;
            background: var(--accent-soft);
          }}
          
          /* Layout */
          .reader-layout {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(260px, 300px);
            justify-content: space-between;
            gap: 80px;
            align-items: start;
          }}
          .reader-main {{
            min-width: 0;
          }}
          .reader-sidebar {{
            position: sticky;
            top: 40px;
            display: grid;
            gap: 32px;
          }}
          
          /* Auto-hide sidebar if embedded */
          body.is-embedded .reader-sidebar {{
            display: none !important;
          }}
          body.is-embedded .reader-layout {{
            grid-template-columns: 1fr;
            max-width: 900px;
            margin: 0 auto;
          }}
          
          /* Quick Navigation */
          .reader-outline-card {{
            display: grid;
            gap: 16px;
            padding: 24px;
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            background: var(--panel);
            box-shadow: var(--shadow-sm);
          }}
          .reader-outline-label {{
            color: var(--ink);
            font-size: 0.875rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }}
          .reader-outline-links {{
            display: grid;
            gap: 10px;
            max-width: 100%;
            min-width: 0;
          }}
          .reader-outline-link {{
            display: block;
            color: var(--muted);
            text-decoration: none;
            font-size: 0.9375rem;
            line-height: 1.5;
            padding-left: 14px;
            border-left: 2px solid var(--line);
            transition: all 0.2s ease;
          }}
          .reader-outline-link:hover {{
            color: var(--accent);
            border-left-color: var(--accent);
          }}
          .hero-outline {{
            display: grid;
            gap: 12px;
            max-width: 100%;
            min-width: 0;
          }}
          .hero-outline-label {{
            color: var(--ink);
            font-size: 1rem;
            font-weight: 600;
          }}
          .hero-outline-links {{
            display: grid;
            gap: 10px;
          }}
          .hero-jump-link {{
            display: block;
            max-width: 100%;
            min-width: 0;
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
            line-height: 1.5;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
          .hero-jump-link:hover {{
            text-decoration: underline;
            text-underline-offset: 0.16em;
          }}
          
          /* Sections */
          .section-list {{
            display: grid;
            gap: 80px;
            min-width: 0;
          }}
          .section-card {{
            scroll-margin-top: 40px;
            border: 0;
            background: transparent;
            box-shadow: none;
            min-width: 0;
            max-width: 100%;
          }}
          body.is-embedded .section-list {{
            gap: 40px;
          }}
          body.is-embedded .section-card + .section-card {{
            padding-top: 40px;
            border-top: 1px solid var(--line);
          }}
          .section-card.is-target {{
            padding: 40px;
            margin: -40px;
            border-radius: calc(var(--border-radius) + 12px);
            background: var(--accent-soft);
            border: 1px solid #bfdbfe;
          }}
          body.is-embedded .section-card.is-target {{
            margin: 0;
            padding: 32px 40px;
            border-left: 4px solid var(--accent);
            border-radius: 0 16px 16px 0;
            border-top: 0;
            border-bottom: 0;
            border-right: 0;
            background: linear-gradient(90deg, #eff6ff 0%, #ffffff 100%);
            box-shadow: none;
          }}
          
          .section-header {{
            margin-bottom: 32px;
            min-width: 0;
          }}
          .section-meta {{
            color: var(--accent);
            font-size: 0.9375rem;
            font-weight: 600;
            margin-bottom: 12px;
            display: block;
          }}
          .section-card h2 {{
            margin: 0;
            font-size: clamp(1.75rem, 3.5vw, 2.25rem);
            font-weight: 700;
            color: var(--ink);
            line-height: 1.3;
            letter-spacing: -0.01em;
            max-width: 100%;
            overflow-wrap: anywhere;
            word-break: keep-all;
          }}
          
          /* Body Text */
          .section-body {{
            display: block;
            color: var(--ink-soft);
            min-width: 0;
            max-width: 100%;
          }}
          .section-body p {{
            font-size: 1rem;
            line-height: 1.625;
            color: var(--ink-soft);
            margin: 0 0 1.25em 0;
            word-break: keep-all;
            overflow-wrap: break-word;
          }}
          .section-body p:last-child {{
            margin-bottom: 0;
          }}
          .section-body li, .section-body td {{
            font-size: 1rem;
            line-height: 1.625;
            color: var(--ink-soft);
            overflow-wrap: break-word;
            word-break: keep-all;
          }}
          .section-body h3 {{
            margin: 2.5em 0 1em;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--ink);
            letter-spacing: -0.01em;
            line-height: 1.4;
            max-width: 100%;
            overflow-wrap: anywhere;
          }}
          .section-body a {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
            border-bottom: 1px solid transparent;
            transition: border-bottom-color 0.2s ease;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
          .section-body a:hover {{
            border-bottom-color: var(--accent);
          }}
          
          /* Lists */
          .section-body ul, .section-body ol, .procedure-list {{
            padding-left: 20px;
            margin: 0 0 1.25em 0;
          }}
          .section-body li {{
            margin-bottom: 0.5em;
          }}
          .section-body li > p {{
            margin-bottom: 0.5em;
          }}
          
          /* Code blocks */
          .section-body code {{
            display: inline;
            padding: 0.125rem 0.375rem;
            border-radius: 6px;
            background: #f1f5f9;
            border: 1px solid var(--line);
            color: #db2777;
            font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
            white-space: break-spaces;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
          .code-block {{
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            overflow: hidden;
            background: #0f172a;
            box-shadow: var(--shadow-sm);
            margin: 16px 0;
            min-width: 0;
            max-width: 100%;
          }}
          .code-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 20px;
            border-bottom: 1px solid #1e293b;
            background: #0f172a;
          }}
          .code-label {{
            color: #94a3b8;
            font-size: 0.8125rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }}
          .code-actions {{
            display: flex;
            gap: 12px;
          }}
          .icon-button {{
            width: 32px;
            height: 32px;
            padding: 0;
            border: 0;
            border-radius: 6px;
            background: transparent;
            color: #94a3b8;
            cursor: pointer;
            display: grid;
            place-items: center;
            transition: all 0.2s ease;
          }}
          .icon-button:hover {{
            background: #1e293b;
            color: #f8fafc;
          }}
          .code-block pre {{
            margin: 0;
            padding: 24px;
            overflow-x: auto;
            color: #f8fafc;
            font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
            font-size: 0.875rem;
            line-height: 1.7;
            max-width: 100%;
            min-width: 0;
          }}
          .code-block code {{
            background: transparent;
            border: 0;
            padding: 0;
            color: inherit;
            white-space: inherit;
            overflow-wrap: normal;
            word-break: normal;
          }}
          
          /* Notes */
          .note-card {{
            padding: 24px 32px;
            margin: 16px 0;
            border-radius: var(--border-radius);
            background: var(--panel-soft);
            border-left: 4px solid var(--muted);
          }}
          .note-title {{
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 12px;
            font-size: 1rem;
          }}
          .note-warning, .note-caution {{ border-left-color: #f59e0b; background: #fffbeb; }}
          .note-warning .note-title, .note-caution .note-title {{ color: #b45309; }}
          .note-note {{ border-left-color: #3b82f6; background: #eff6ff; }}
          .note-note .note-title {{ color: #1d4ed8; }}
          .note-important {{ border-left-color: #8b5cf6; background: #f5f3ff; }}
          .note-important .note-title {{ color: #5b21b6; }}
          .note-tip {{ border-left-color: #10b981; background: #ecfdf5; }}
          .note-tip .note-title {{ color: #047857; }}
          
          /* Tables */
          .table-wrap {{
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-sm);
            margin: 24px 0;
            max-width: 100%;
          }}
          table {{
            width: 100%;
            max-width: 100%;
            border-collapse: collapse;
            background: var(--panel);
          }}
          th, td {{
            padding: 16px 24px;
            text-align: left;
            border-bottom: 1px solid var(--line);
            overflow-wrap: break-word;
            word-break: keep-all;
          }}
          th {{
            background: var(--panel-soft);
            font-weight: 600;
            font-size: 0.9375rem;
            color: var(--ink);
          }}
          tr:last-child td {{ border-bottom: 0; }}
          
          /* Figures */
          .figure-block {{
            margin: 40px 0;
            padding: 32px;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            text-align: center;
            max-width: 100%;
          }}
          .figure-block img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
            margin: 0 auto;
          }}
          .figure-block figcaption {{
            margin-top: 20px;
            font-size: 0.9375rem;
            color: var(--muted);
          }}
          
          /* Embedded Source Overrides */
          .embedded-origin-row {{
            margin-bottom: 32px;
          }}
          .embedded-origin-link {{
            display: inline-flex;
            align-items: center;
            height: 36px;
            padding: 0 20px;
            border-radius: 999px;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            color: var(--ink-soft);
            text-decoration: none;
            font-size: 0.9375rem;
            font-weight: 500;
            transition: all 0.2s ease;
          }}
          .embedded-origin-link:hover {{
            background: var(--line);
            color: var(--ink);
          }}
          
          @media (max-width: 1100px) {{
            .reader-layout {{
              grid-template-columns: 1fr;
              padding: 0 24px;
            }}
            .reader-sidebar {{
              display: none;
            }}
          }}
          .wiki-parent-card, .wiki-card {{
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            padding: 24px;
            background: var(--panel);
            box-shadow: var(--shadow-sm);
            margin: 16px 0;
          }}
          .wiki-parent-card p, .wiki-card p {{
            color: var(--ink-soft);
            line-height: 1.7;
          }}
          .wiki-parent-card a, .wiki-card a {{
            color: var(--ink);
            font-weight: 600;
            text-decoration: none;
          }}
          .wiki-parent-eyebrow {{
            color: var(--accent);
            font-size: 0.8125rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 8px;
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
          const OVERLAY_USER_KEY = "playbook_studio_overlay_user";
          function overlayUserId() {{
            return window.localStorage.getItem(OVERLAY_USER_KEY) || "viewer-user";
          }}
          async function overlayFetch(path, init) {{
            const response = await fetch(path, {{
              headers: {{ "Content-Type": "application/json; charset=utf-8" }},
              ...init,
            }});
            if (!response.ok) {{
              throw new Error("overlay request failed");
            }}
            return response.json();
          }}
          function toolbarPayload(toolbar) {{
            return {{
              user_id: overlayUserId(),
              target_kind: toolbar.dataset.targetKind || "",
              target_ref: toolbar.dataset.targetRef || "",
              book_slug: toolbar.dataset.bookSlug || "",
              anchor: toolbar.dataset.anchor || "",
              asset_name: toolbar.dataset.assetName || "",
              entity_slug: toolbar.dataset.entitySlug || "",
              viewer_path: toolbar.dataset.viewerPath || window.location.pathname + window.location.hash,
            }};
          }}
          async function markRecentPosition() {{
            const target = document.querySelector(".overlay-page-target[data-page-root='true']");
            if (!target) return;
            const payload = toolbarPayload(target);
            await overlayFetch('/api/wiki-overlays', {{
              method: 'POST',
              body: JSON.stringify({{ ...payload, kind: "recent_position" }}),
            }});
          }}
          document.addEventListener("DOMContentLoaded", async () => {{
            try {{
              await markRecentPosition();
            }} catch (error) {{
              console.error(error);
            }}
          }});
        </script>
      </head>
      <body class="{body_class}">
        <main>
          {hero_block}
          <section class="reader-layout">
            <div class="reader-main">
              <article class="{document_class}">
                {embedded_meta_block}
                {extra_blocks}
                <div class="section-list">
                  {cards}
                </div>
              </article>
            </div>
            {reader_sidebar}
          </section>
        </main>
      
        <script>
          if (window.self !== window.top) {{
            document.body.classList.add("is-embedded");
          }}
        </script>

      </body>
    </html>
    """.format(
        title=html.escape(title),
        eyebrow=html.escape(eyebrow),
        summary=html.escape(summary),
        section_count=section_count,
        source_url=html.escape(source_url, quote=True),
        body_class="is-embedded" if embedded else "",
        document_class=document_class,
        extra_blocks=extra_blocks,
        reader_sidebar=reader_sidebar,
        embedded_meta_block=embedded_meta_block.format(
            source_url=html.escape(source_url, quote=True),
        ) if embedded_meta_block else "",
        page_overlay_toolbar=page_overlay_toolbar,
        hero_metric_pills=hero_metric_pills,
        hero_outline_block=hero_outline_block,
        hero_meta_block=hero_meta_block.format(
            eyebrow=html.escape(eyebrow),
            hero_metric_pills=hero_metric_pills,
            source_link=(
                '<a href="{href}" target="_blank" rel="noreferrer">원문 열기</a>'.format(
                    href=html.escape(source_url, quote=True),
                )
                if source_url
                else ""
            ),
        ) if hero_meta_block else "",
        hero_block=hero_block.format(
            title=html.escape(title),
            eyebrow=html.escape(eyebrow),
            summary=html.escape(summary),
            source_url=html.escape(source_url, quote=True),
            page_overlay_toolbar=page_overlay_toolbar,
            hero_outline_block=hero_outline_block,
            hero_meta_block=hero_meta_block.format(
                eyebrow=html.escape(eyebrow),
                hero_metric_pills=hero_metric_pills,
                source_link=(
                    '<a href="{href}" target="_blank" rel="noreferrer">원문 열기</a>'.format(
                        href=html.escape(source_url, quote=True),
                    )
                    if source_url
                    else ""
                ),
            ) if hero_meta_block else "",
        ) if hero_block else "",
        cards="\n".join(cards),
    ).strip()
