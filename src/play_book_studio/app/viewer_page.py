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
          :root {{
            color-scheme: light;
            --bg: #f3f5f7;
            --panel: #ffffff;
            --panel-soft: #f7f8fa;
            --line: rgba(17, 20, 24, 0.1);
            --line-strong: rgba(17, 20, 24, 0.16);
            --ink: #111418;
            --muted: #5f6872;
            --accent: #c62828;
            --accent-soft: rgba(238, 0, 0, 0.06);
          }}
          * {{
            box-sizing: border-box;
          }}
          body {{
            margin: 0;
            background:
              radial-gradient(circle at top right, rgba(238, 0, 0, 0.06), transparent 24rem),
              linear-gradient(180deg, #f7f8fa 0%, var(--bg) 100%);
            color: var(--ink);
            font-family: "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
          }}
          main {{
            width: min(1480px, calc(100vw - 32px));
            max-width: none;
            margin: 0 auto;
            padding: 28px 0 44px;
          }}
          body.is-embedded {{
            background: linear-gradient(180deg, #f8f9fb 0%, #f1f3f5 100%);
          }}
          body.is-embedded main {{
            width: 100%;
            margin: 0;
            padding: 16px 18px 24px;
            min-height: 100%;
          }}
          .study-document-embedded {{
            min-height: 100%;
            padding: 0;
            border: 0;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
          }}
          .hero {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 36px 38px;
            box-shadow:
              0 20px 50px rgba(17, 20, 24, 0.08),
              inset 0 1px 0 rgba(255, 255, 255, 0.8);
          }}
          .hero-grid {{
            display: grid;
            grid-template-columns: minmax(0, 1.8fr) minmax(240px, 0.9fr);
            gap: 24px;
            align-items: end;
          }}
          .hero-main {{
            display: grid;
            gap: 14px;
          }}
          .eyebrow {{
            color: var(--accent);
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }}
          h1 {{
            margin: 0;
            font-family: "Fraunces", "Iowan Old Style", "Noto Serif KR", serif;
            font-size: clamp(2.6rem, 5vw, 4.4rem);
            line-height: 0.98;
            letter-spacing: -0.05em;
            max-width: 10ch;
          }}
          .summary {{
            margin: 0;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.78;
            max-width: 66ch;
          }}
          .actions {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
          }}
          .hero-actions {{
            justify-content: flex-end;
          }}
          .hero-meta {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: flex-end;
          }}
          .hero-outline {{
            display: grid;
            gap: 10px;
            margin-top: 6px;
          }}
          .hero-outline-label {{
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
          }}
          .hero-outline-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
          }}
          .hero-jump-link {{
            display: inline-flex;
            align-items: center;
            min-height: 38px;
            padding: 0 14px;
            border-radius: 999px;
            border: 1px solid rgba(17, 20, 24, 0.08);
            background: rgba(17, 20, 24, 0.025);
            color: var(--ink);
            font-size: 0.88rem;
            font-weight: 700;
            line-height: 1.2;
            text-decoration: none;
          }}
          .hero-jump-link:hover {{
            color: var(--accent);
            border-color: rgba(198, 40, 40, 0.18);
            background: rgba(198, 40, 40, 0.05);
          }}
          .meta-pill,
          .actions a {{
            display: inline-flex;
            align-items: center;
            min-height: 38px;
            padding: 0 14px;
            border: 1px solid rgba(17, 20, 24, 0.08);
            border-radius: 999px;
            background: rgba(17, 20, 24, 0.025);
            color: var(--muted);
            font-size: 0.88rem;
            font-weight: 700;
            text-decoration: none;
          }}
          .meta-pill-accent {{
            color: var(--accent);
            border-color: rgba(198, 40, 40, 0.16);
            background: rgba(198, 40, 40, 0.06);
          }}
          .section-list {{
            display: grid;
            gap: 28px;
          }}
          .reader-layout {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(280px, 360px);
            gap: 24px;
            align-items: start;
            margin-top: 24px;
          }}
          .reader-main {{
            min-width: 0;
          }}
          .reader-sidebar {{
            position: sticky;
            top: 18px;
            display: grid;
            gap: 18px;
          }}
          .wiki-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin: 0;
          }}
          .wiki-grid-primary {{
            align-items: start;
          }}
          .wiki-grid-secondary {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin-top: 0;
          }}
          .wiki-parent-card {{
            display: grid;
            gap: 10px;
            background: linear-gradient(180deg, rgba(198, 40, 40, 0.06), rgba(198, 40, 40, 0.02));
            border: 1px solid rgba(198, 40, 40, 0.12);
            border-radius: 22px;
            padding: 18px 20px;
          }}
          .wiki-parent-eyebrow {{
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }}
          .viewer-truth-topline {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            flex-wrap: wrap;
          }}
          .viewer-truth-badge {{
            display: inline-flex;
            align-items: center;
            min-height: 24px;
            padding: 0 10px;
            border-radius: 999px;
            border: 1px solid rgba(198, 40, 40, 0.16);
            background: rgba(198, 40, 40, 0.08);
            color: var(--accent);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
          }}
          .viewer-truth-link {{
            display: inline-flex;
            align-items: center;
            min-height: 24px;
            color: var(--muted);
            text-decoration: none;
            font-size: 0.82rem;
            font-weight: 700;
          }}
          .viewer-truth-title {{
            color: var(--ink);
            font-size: 1.02rem;
            font-weight: 800;
            line-height: 1.4;
          }}
          .wiki-parent-card a {{
            color: var(--ink);
            text-decoration: none;
            font-weight: 800;
            font-size: 1.02rem;
            line-height: 1.4;
          }}
          .wiki-parent-card p {{
            margin: 0;
            color: var(--muted);
            line-height: 1.55;
          }}
          .wiki-card {{
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 16px 18px;
            box-shadow: 0 10px 24px rgba(17, 20, 24, 0.05);
          }}
          .wiki-card h3 {{
            margin: 0 0 10px;
            font-size: 0.9rem;
            line-height: 1.4;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.04em;
          }}
          .wiki-card h4 {{
            margin: 0 0 10px;
            font-size: 0.82rem;
            line-height: 1.4;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
          }}
          .wiki-card-primary {{
            padding: 18px 20px;
          }}
          .wiki-card-intro {{
            margin: 0 0 12px;
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.6;
          }}
          .wiki-card-stack {{
            display: grid;
            gap: 16px;
          }}
          .wiki-links,
          .wiki-path {{
            display: grid;
            gap: 10px;
          }}
          .wiki-details {{
            margin-top: 8px;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.78);
            overflow: hidden;
          }}
          .wiki-details summary {{
            list-style: none;
            cursor: pointer;
            padding: 14px 18px;
            font-size: 0.88rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            color: var(--muted);
            background: rgba(17, 20, 24, 0.025);
          }}
          .wiki-details summary::-webkit-details-marker {{
            display: none;
          }}
          .wiki-details[open] summary {{
            border-bottom: 1px solid var(--line);
            color: var(--ink);
          }}
          .wiki-details > .wiki-grid {{
            padding: 14px 14px 12px;
            margin: 0;
          }}
          .wiki-links a,
          .wiki-path a {{
            color: var(--ink);
            text-decoration: none;
            font-weight: 700;
            line-height: 1.5;
          }}
          .wiki-links a:hover,
          .wiki-path a:hover {{
            color: var(--accent);
          }}
          .wiki-links span,
          .wiki-path span {{
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.55;
          }}
          .wiki-empty {{
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.55;
          }}
          .wiki-entity-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
          }}
          .wiki-entity-list a,
          .meta-pill {{
            display: inline-flex;
            align-items: center;
            min-height: 34px;
            padding: 0 12px;
            border-radius: 999px;
            border: 1px solid var(--line);
            background: rgba(17, 20, 24, 0.025);
            color: var(--ink);
            text-decoration: none;
            font-size: 0.86rem;
            font-weight: 700;
          }}
          .wiki-entity-list a:hover {{
            color: var(--accent);
            border-color: rgba(198, 40, 40, 0.2);
            background: rgba(198, 40, 40, 0.05);
          }}
          .figure-block {{
            display: grid;
            gap: 10px;
            margin: 18px 0;
            padding: 14px;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(17, 20, 24, 0.02);
          }}
          .diagram-block {{
            border-color: rgba(198, 40, 40, 0.18);
            background: linear-gradient(180deg, rgba(198, 40, 40, 0.05), rgba(198, 40, 40, 0.015));
          }}
          .figure-eyebrow {{
            color: var(--accent);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }}
          .figure-link {{
            display: block;
            width: fit-content;
            max-width: min(100%, 760px);
            margin: 0 auto;
            text-decoration: none;
          }}
          .figure-block img {{
            display: block;
            width: auto;
            height: auto;
            max-width: 100%;
            max-height: min(68vh, 760px);
            margin: 0 auto;
            border-radius: 12px;
            border: 1px solid rgba(17, 20, 24, 0.08);
            background: #fff;
            object-fit: contain;
          }}
          .diagram-block .figure-link {{
            max-width: min(100%, 920px);
          }}
          .figure-block figcaption {{
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.55;
            max-width: min(100%, 760px);
            margin: 0 auto;
          }}
          .diagram-block figcaption {{
            max-width: min(100%, 920px);
          }}
          body.is-embedded .section-list {{
            margin-top: 14px;
            gap: 0;
          }}
          body.is-embedded .wiki-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin: 8px 0 18px;
          }}
          body.is-embedded .wiki-parent-card {{
            margin: 8px 0 14px;
            padding: 14px 16px;
            border-radius: 16px;
          }}
          body.is-embedded .wiki-card {{
            border-radius: 16px;
            padding: 14px 16px;
          }}
          body.is-embedded .wiki-details {{
            margin: 6px 0 16px;
            border-radius: 16px;
          }}
          body.is-embedded .wiki-details summary {{
            padding: 12px 16px;
          }}
          @media (max-width: 1100px) {{
            .hero-grid,
            .reader-layout {{
              grid-template-columns: 1fr;
            }}
            .hero-actions,
            .hero-meta {{
              justify-content: flex-start;
              align-items: flex-start;
            }}
            .hero-outline-links {{
              gap: 8px;
            }}
            .reader-sidebar {{
              position: static;
            }}
            .wiki-grid,
            body.is-embedded .wiki-grid {{
              grid-template-columns: 1fr;
            }}
            .wiki-grid-secondary {{
              grid-template-columns: 1fr;
            }}
          }}
          .embedded-origin-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0 0 14px;
          }}
          .embedded-origin-link {{
            display: inline-flex;
            align-items: center;
            min-height: 34px;
            padding: 0 12px;
            border-radius: 999px;
            border: 1px solid rgba(17, 20, 24, 0.08);
            background: rgba(255, 255, 255, 0.88);
            color: #4b5560;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            text-decoration: none;
          }}
          .embedded-origin-link:hover {{
            color: var(--ink);
            border-color: rgba(17, 20, 24, 0.14);
            background: rgba(255, 255, 255, 0.96);
          }}
          body.is-embedded .embedded-section {{
            padding: 0 0 28px;
            scroll-margin-top: 20px;
          }}
          body.is-embedded .embedded-section + .embedded-section {{
            margin-top: 28px;
            padding-top: 28px;
            border-top: 1px solid var(--line);
          }}
          body.is-embedded .embedded-section.is-target {{
            background: linear-gradient(180deg, rgba(238, 0, 0, 0.028), rgba(255, 255, 255, 0.96));
            border-radius: 16px;
            padding: 16px 18px 22px;
            box-shadow: inset 0 0 0 1px rgba(238, 0, 0, 0.1);
          }}
          body.is-embedded .section-card {{
            background: transparent;
            border: 0;
            border-radius: 0;
            padding: 0 0 28px;
            box-shadow: none;
          }}
          body.is-embedded .section-card + .section-card {{
            margin-top: 28px;
            padding-top: 28px;
            border-top: 1px solid var(--line);
          }}
          body.is-embedded .section-card.is-target {{
            background: transparent;
            border-color: transparent;
            box-shadow: none;
          }}
          body.is-embedded .section-header {{
            padding-bottom: 12px;
            margin-bottom: 14px;
          }}
          body.is-embedded .section-header h2 {{
            font-size: clamp(1.4rem, 2.6vw, 2rem);
            line-height: 1.32;
            letter-spacing: -0.03em;
          }}
          body.is-embedded .section-meta {{
            font-size: 0.82rem;
            letter-spacing: -0.01em;
          }}
          body.is-embedded .section-body {{
            gap: 18px;
          }}
          body.is-embedded .section-body p {{
            font-size: 1rem;
            line-height: 1.82;
            color: var(--ink);
          }}
          .section-card {{
            background: transparent;
            border: 0;
            border-radius: 0;
            padding: 0 0 10px;
            scroll-margin-top: 20px;
            box-shadow: none;
          }}
          .section-card + .section-card {{
            padding-top: 28px;
            border-top: 1px solid rgba(17, 20, 24, 0.08);
          }}
          .section-card.is-target {{
            border-top-color: rgba(198, 40, 40, 0.22);
            background: linear-gradient(180deg, rgba(198, 40, 40, 0.03), transparent 60%);
            border-radius: 18px;
            padding: 18px 20px 22px;
            box-shadow: inset 0 0 0 1px rgba(198, 40, 40, 0.08);
          }}
          .section-header {{
            display: grid;
            gap: 10px;
            padding-bottom: 14px;
            margin-bottom: 18px;
            border-bottom: 1px solid rgba(17, 20, 24, 0.08);
          }}
          .section-card h2 {{
            margin: 0;
            font-family: "Fraunces", "Iowan Old Style", "Noto Serif KR", serif;
            font-size: clamp(1.7rem, 2.3vw, 2.4rem);
            line-height: 1.16;
            letter-spacing: -0.04em;
          }}
          .section-card.section-level-2 h2 {{
            font-size: clamp(1.45rem, 2vw, 2rem);
          }}
          .section-card.section-level-3 h2,
          .section-card.section-level-4 h2,
          .section-card.section-level-5 h2,
          .section-card.section-level-6 h2 {{
            font-size: clamp(1.2rem, 1.6vw, 1.6rem);
            letter-spacing: -0.02em;
          }}
          .section-body {{
            display: grid;
            gap: 18px;
          }}
          .section-body p,
          .section-body h3 {{
            margin: 0;
          }}
          .section-body h3 {{
            padding-top: 10px;
            font-size: 1.12rem;
            color: var(--ink);
            letter-spacing: -0.01em;
          }}
          .section-body p,
          .section-body li,
          .section-body td {{
            font-size: 1rem;
            line-height: 1.82;
            color: #36404a;
          }}
          .section-body a {{
            color: #9a3412;
            text-decoration: none;
            border-bottom: 1px solid rgba(154, 52, 18, 0.18);
          }}
          .section-body a:hover {{
            color: #7c2d12;
            border-bottom-color: rgba(124, 45, 18, 0.32);
          }}
          .section-body code {{
            display: inline;
            padding: 0.08rem 0.32rem;
            border-radius: 6px;
            border: 1px solid rgba(238, 0, 0, 0.14);
            background: rgba(238, 0, 0, 0.05);
            color: #a32719;
            font-family: "SF Mono", "Menlo", monospace;
            font-size: 0.92em;
          }}
          .code-block {{
            border: 1px solid var(--line);
            border-radius: 20px;
            overflow: hidden;
            background: linear-gradient(180deg, #ffffff 0%, #f7f8fa 100%);
            box-shadow:
              inset 0 1px 0 rgba(255, 255, 255, 0.75),
              0 8px 24px rgba(17, 20, 24, 0.05);
          }}
          .code-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 12px 14px;
            background: linear-gradient(180deg, #f8f9fb 0%, #f1f3f5 100%);
            border-top: 1px solid rgba(255, 255, 255, 0.8);
            border-bottom: 1px solid var(--line);
          }}
          .code-label {{
            color: #66707a;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }}
          .code-caption,
          .table-caption {{
            padding: 14px 16px 0;
            color: var(--muted);
            font-size: 0.8rem;
            font-weight: 700;
            line-height: 1.5;
            letter-spacing: 0.02em;
          }}
          .copy-button {{
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 7px 11px;
            background: rgba(255, 255, 255, 0.95);
            color: var(--ink);
            font: inherit;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
          }}
          .icon-button {{
            width: 34px;
            min-width: 34px;
            height: 34px;
            padding: 0;
            display: inline-grid;
            place-items: center;
            font-size: 0.95rem;
            line-height: 1;
          }}
          .code-actions {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
          }}
          .copy-button.is-copied {{
            background: rgba(238, 0, 0, 0.1);
            color: var(--accent);
          }}
          .code-block.is-wrapped pre,
          .code-block.is-wrapped code {{
            white-space: pre-wrap;
            word-break: break-word;
          }}
          .code-block pre {{
            margin: 0;
            padding: 18px 20px 20px;
            overflow-x: auto;
            white-space: pre;
            background: #fbfcfd;
            color: #232a31;
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
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.96);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
          }}
          table {{
            width: 100%;
            border-collapse: collapse;
          }}
          th,
          td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--line);
            text-align: left;
            vertical-align: top;
            font-size: 0.94rem;
            line-height: 1.5;
          }}
          th {{
            background: #f6f7f9;
            color: #55606b;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            text-transform: uppercase;
          }}
          tbody tr:nth-child(even) {{
            background: rgba(17, 20, 24, 0.02);
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
          .normalized-ordered-list,
          .procedure-list,
          .substep-list {{
            margin: 0;
            padding-left: 1.2rem;
          }}
          .normalized-ordered-list {{
            display: grid;
            gap: 10px;
            margin: 8px 0 14px;
          }}
          .normalized-ordered-list > li {{
            line-height: 1.82;
          }}
          .normalized-ordered-list > li > p {{
            margin: 8px 0 0;
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
            border: 1px solid var(--line);
            border-radius: 16px;
            background: #fbfcfd;
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
            background: rgba(238, 0, 0, 0.09);
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
            border: 1px solid var(--line-strong);
            border-left: 5px solid rgba(198, 40, 40, 0.45);
            border-radius: 16px;
            padding: 16px 18px;
            background: linear-gradient(180deg, rgba(238, 0, 0, 0.025) 0%, rgba(238, 0, 0, 0.05) 100%);
          }}
          .note-card.note-warning,
          .note-card.note-caution {{
            background: rgba(245, 158, 11, 0.08);
            border-color: rgba(245, 158, 11, 0.18);
            border-left-color: rgba(217, 119, 6, 0.5);
          }}
          .note-card.note-important {{
            background: rgba(198, 40, 40, 0.08);
            border-color: rgba(198, 40, 40, 0.18);
            border-left-color: rgba(198, 40, 40, 0.5);
          }}
          .note-card.note-tip {{
            background: rgba(22, 163, 74, 0.08);
            border-color: rgba(22, 163, 74, 0.18);
            border-left-color: rgba(22, 163, 74, 0.5);
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
