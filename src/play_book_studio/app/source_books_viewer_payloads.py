"""Viewer payload builders split out of source_books.py."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from play_book_studio.config.settings import load_settings

from .presenters import _manifest_entry_for_book
from .source_books_customer_pack import internal_customer_pack_viewer_html
from .source_books_viewer_resolver import (
    _load_buyer_packet_entry,
    _load_normalized_book_sections,
    _load_playbook_book,
    parse_active_runtime_markdown_viewer_path,
    parse_buyer_packet_viewer_path,
    parse_entity_hub_viewer_path,
    parse_figure_viewer_path,
)
from .source_books_wiki_relations import (
    _active_runtime_markdown_path,
    _build_backlinks,
    _build_entity_backlinks,
    _candidate_relations,
    _entity_hub_sections,
    _entity_hubs,
    _entity_related_sections,
    _figure_asset_by_name,
    _figure_asset_filename,
    _figure_assets,
    _figure_entity_index,
    _figure_section_match,
    _figure_viewer_href,
    _figure_viewer_sections,
    _preferred_book_href,
    _rewrite_book_href,
    _wiki_relation_items,
)
from .viewer_page import _render_page_overlay_toolbar
from .viewers import (
    _build_section_metrics,
    _build_section_outline,
    _build_study_section_cards,
    _parse_viewer_path,
    _render_study_viewer_html,
)
from .wiki_user_overlay import build_wiki_overlay_signal_payload


def _build_entity_hub_supplementary_blocks(root_dir: Path, entity_slug: str) -> list[str]:
    entity = _entity_hubs().get(entity_slug)
    if entity is None:
        return []
    related_books = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in entity.get("related_books", [])
        if isinstance(item, dict)
    )
    next_path_links = "".join(
        """
        <div class="wiki-path">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in entity.get("next_reading_path", [])
        if isinstance(item, dict)
    )
    backlinks = _build_entity_backlinks(root_dir, entity_slug)
    figure_index = _figure_entity_index()
    related_figures = figure_index.get("by_entity", {}).get(entity_slug, []) if isinstance(figure_index.get("by_entity"), dict) else []
    related_sections = _entity_related_sections(entity_slug)
    backlink_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(str(item.get("href") or ""), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in backlinks
    )
    figure_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(str(item.get("viewer_path") or item.get("asset_url") or ""), quote=True),
            label=html.escape(str(item.get("caption") or "Figure")),
            summary=html.escape(
                "{book} · {section}".format(
                    book=str(item.get("book_title") or item.get("book_slug") or "").strip() or "related book",
                    section=str(item.get("section_hint") or "unmatched").strip() or "unmatched",
                )
            ),
        ).strip()
        for item in related_figures[:6]
        if isinstance(item, dict)
    )
    section_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in related_sections[:6]
        if isinstance(item, dict)
    )
    return [
        """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Entity Hub</div>
          <a href="/wiki/entities/{entity_slug}/index.html">{title}</a>
          <p>{summary}</p>
        </section>
        <section class="wiki-grid wiki-grid-primary">
          <article class="wiki-card wiki-card-primary">
            <h3>Recommended Path</h3>
            {next_path_links}
          </article>
          <article class="wiki-card wiki-card-primary">
            <h3>Connections</h3>
            <div class="wiki-card-stack">
              <div>
                <h4>Books</h4>
                {related_books}
              </div>
              <div>
                <h4>Referenced By</h4>
                {backlink_links}
              </div>
            </div>
          </article>
        </section>
        <details class="wiki-details">
          <summary>More</summary>
          <section class="wiki-grid wiki-grid-secondary">
            <article class="wiki-card">
              <h3>Related Figures</h3>
              {figure_links}
            </article>
            <article class="wiki-card">
              <h3>Related Sections</h3>
              {section_links}
            </article>
          </section>
        </details>
        """.format(
            entity_slug=html.escape(entity_slug, quote=True),
            title=html.escape(str(entity.get("title") or entity_slug)),
            summary=html.escape(str(entity.get("summary") or "")),
            related_books=related_books or '<div class="wiki-empty">연결된 북이 아직 없습니다.</div>',
            next_path_links=next_path_links or '<div class="wiki-empty">연결된 경로가 아직 없습니다.</div>',
            backlink_links=backlink_links or '<div class="wiki-empty">이 엔터티를 참조하는 문서가 아직 없습니다.</div>',
            figure_links=figure_links or '<div class="wiki-empty">연결된 figure 자산이 아직 없습니다.</div>',
            section_links=section_links or '<div class="wiki-empty">연결된 절차 섹션이 아직 없습니다.</div>',
        ).strip()
    ]


def _normalized_book_summary(sections: list[dict[str, Any]]) -> str:
    for section in sections:
        text = str(section.get("text") or "").replace("\r\n", "\n").replace("\r", "\n").strip()
        if not text:
            continue
        paragraph = re.sub(r"\s+", " ", text.split("\n\n", 1)[0]).strip()
        if len(paragraph) > 200:
            return paragraph[:197].rstrip() + "..."
        return paragraph
    return ""


def _playbook_viewer_chrome(playbook_book: dict[str, Any]) -> tuple[str, str]:
    source_metadata = (
        playbook_book.get("source_metadata")
        if isinstance(playbook_book.get("source_metadata"), dict)
        else {}
    )
    source_type = str(source_metadata.get("source_type") or "").strip()
    summary = str(playbook_book.get("topic_summary") or "").strip()
    parent_title = str(source_metadata.get("derived_from_title") or "").strip()
    if source_type == "topic_playbook":
        if not summary:
            summary = (
                f"{parent_title}에서 실행 절차만 추린 토픽 플레이북입니다."
                if parent_title
                else "실행 절차 중심으로 다시 엮은 토픽 플레이북입니다."
            )
        return "Topic Playbook", summary
    if source_type == "operation_playbook":
        if not summary:
            summary = (
                f"{parent_title}에서 운영 절차와 검증만 추린 운영 플레이북입니다."
                if parent_title
                else "운영 절차와 검증 중심으로 다시 엮은 운영 플레이북입니다."
            )
        return "Operation Playbook", summary
    if source_type == "troubleshooting_playbook":
        if not summary:
            summary = (
                f"{parent_title}에서 장애 대응 경로만 추린 트러블슈팅 플레이북입니다."
                if parent_title
                else "장애 대응 경로 중심으로 다시 엮은 트러블슈팅 플레이북입니다."
            )
        return "Troubleshooting Playbook", summary
    if source_type == "policy_overlay_book":
        if not summary:
            summary = (
                f"{parent_title}에서 제한, 요구 사항, 검증 기준만 다시 묶은 정책 오버레이입니다."
                if parent_title
                else "제한, 요구 사항, 검증 기준만 다시 묶은 정책 오버레이입니다."
            )
        return "Policy Overlay", summary
    if source_type == "synthesized_playbook":
        if not summary:
            summary = (
                f"{parent_title}에서 핵심 설명, 절차, 검증만 압축한 합성 플레이북입니다."
                if parent_title
                else "핵심 설명, 절차, 검증을 압축한 합성 플레이북입니다."
            )
        return "Synthesized Playbook", summary
    return "Manual Book", "정리된 AST 기준의 유저용 매뉴얼북을 보여줍니다."


def _parse_markdown_heading(line: str) -> tuple[int, str] | None:
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    level = len(stripped) - len(stripped.lstrip("#"))
    if level < 1 or level > 6:
        return None
    title = stripped[level:].strip()
    if not title:
        return None
    return level, title


def _anchorify_heading(text: str) -> str:
    normalized = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    normalized = re.sub(r"[\s_]+", "-", normalized)
    return normalized or "section"


def _markdown_sections(markdown_text: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    path_stack: list[str] = []
    for raw_line in markdown_text.splitlines():
        heading = _parse_markdown_heading(raw_line)
        if heading is not None:
            level, title = heading
            while len(path_stack) >= level:
                path_stack.pop()
            path_stack.append(title)
            current = {
                "anchor": _anchorify_heading(title),
                "heading": title,
                "section_path": list(path_stack),
                "text": "",
                "blocks": [],
            }
            sections.append(current)
            continue
        if current is None:
            continue
        current["text"] = f"{current['text']}\n{raw_line}".strip()
    return [section for section in sections if str(section.get("text") or "").strip() or str(section.get("heading") or "").strip()]


def _markdown_summary(sections: list[dict[str, Any]]) -> str:
    for section in sections:
        raw_text = str(section.get("text") or "").strip()
        if not raw_text:
            continue
        paragraph = raw_text.split("\n\n", 1)[0].strip()
        paragraph = re.sub(r"\s+", " ", paragraph)
        if len(paragraph) > 180:
            paragraph = paragraph[:177].rstrip() + "..."
        if paragraph:
            return paragraph
    return ""


def _trim_leading_title_section(sections: list[dict[str, Any]], *, title: str) -> list[dict[str, Any]]:
    if not sections:
        return sections
    first = sections[0]
    first_heading = str(first.get("heading") or "").strip()
    if first_heading != str(title or "").strip():
        return sections
    section_path = [str(item).strip() for item in (first.get("section_path") or []) if str(item).strip()]
    if len(section_path) != 1:
        return sections
    remaining = sections[1:]
    if not remaining:
        return sections
    carry_text = str(first.get("text") or "").strip()
    if not carry_text:
        return remaining
    merged_first = dict(remaining[0])
    next_text = str(merged_first.get("text") or "").strip()
    merged_first["text"] = f"{carry_text}\n\n{next_text}".strip() if next_text else carry_text
    return [merged_first, *remaining[1:]]


def _build_wiki_supplementary_blocks(root_dir: Path, slug: str) -> list[str]:
    relation = _candidate_relations().get(slug, {})
    manifest_entry = _manifest_entry_for_book(root_dir, slug)
    title = str(manifest_entry.get("title") or slug.replace("_", " ").title())
    summary = str(manifest_entry.get("summary") or "").strip()
    parent_block = ""
    if summary:
        parent_block = """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Validated Runtime</div>
          <a href="{href}">{label}</a>
          <p>{summary}</p>
        </section>
        """.format(
            href=html.escape(_preferred_book_href(root_dir, slug), quote=True),
            label=html.escape(title),
            summary=html.escape(summary),
        ).strip()
    entity_links = "".join(
        f'<a href="{html.escape(str(item.get("href") or ""), quote=True)}">{html.escape(str(item.get("label") or ""))}</a>'
        for item in _wiki_relation_items(relation, "entities")
    )
    related_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "related_docs")
    )
    next_path_links = "".join(
        """
        <div class="wiki-path">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "next_reading_path")
    )
    backlinks = _build_backlinks(root_dir, slug)
    backlink_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(str(item.get("href") or ""), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in backlinks
    )
    sibling_blocks = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "sibling_docs")
    )
    figure_blocks = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(str(item.get("viewer_path") or item.get("asset_url") or ""), quote=True),
            label=html.escape(str(item.get("caption") or "Figure")),
            summary=html.escape(str(item.get("section_hint") or "related figure")),
        ).strip()
        for item in _wiki_relation_items(relation, "related_figures")
    )
    section_blocks = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "related_sections")
    )
    return [
        """
        <section class="wiki-grid">
          <article class="wiki-card">
            <h3>Entities</h3>
            <div class="wiki-entity-list">{entity_links}</div>
          </article>
          <article class="wiki-card">
            <h3>Related Documents</h3>
            {related_links}
          </article>
          <article class="wiki-card">
            <h3>Recommended Path</h3>
            {next_path_links}
          </article>
        </section>
        <details class="wiki-details">
          <summary>More</summary>
          <section class="wiki-grid wiki-grid-secondary">
            <article class="wiki-card">
              <h3>Backlinks</h3>
              {backlink_links}
            </article>
            <article class="wiki-card">
              <h3>Sibling Documents</h3>
              {sibling_blocks}
            </article>
            <article class="wiki-card">
              <h3>Figures</h3>
              {figure_blocks}
            </article>
            <article class="wiki-card">
              <h3>Sections</h3>
              {section_blocks}
            </article>
          </section>
        </details>
        """.format(
            entity_links=entity_links or '<div class="wiki-empty">핵심 엔터티 연결이 아직 없습니다.</div>',
            related_links=related_links or '<div class="wiki-empty">연결된 문서가 아직 없습니다.</div>',
            next_path_links=next_path_links or '<div class="wiki-empty">연결된 경로가 아직 없습니다.</div>',
            backlink_links=backlink_links or '<div class="wiki-empty">아직 연결된 역방향 문서가 없습니다.</div>',
            sibling_blocks=sibling_blocks or '<div class="wiki-empty">같은 작업군 문서는 아직 준비 중입니다.</div>',
            figure_blocks=figure_blocks or '<div class="wiki-empty">연결된 figure 자산이 아직 없습니다.</div>',
            section_blocks=section_blocks or '<div class="wiki-empty">연결된 절차 섹션이 아직 없습니다.</div>',
        ).strip()
    ]


def _build_buyer_packet_supplementary_blocks(bundle: dict[str, Any], packet: dict[str, Any]) -> list[str]:
    stage = str(bundle.get("current_stage") or "").strip()
    commercial_truth = str(bundle.get("commercial_truth") or "").strip()
    purpose = str(packet.get("purpose") or "").strip()
    related_packets = [
        item for item in (bundle.get("packets") or [])
        if isinstance(item, dict) and str(item.get("id") or "").strip() != str(packet.get("id") or "").strip()
    ]
    related_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(f"/buyer-packets/{str(item.get('id') or '').strip()}", quote=True),
            label=html.escape(str(item.get("title") or "")),
            summary=html.escape(str(item.get("purpose") or "")),
        ).strip()
        for item in related_packets[:4]
    )
    pills = "".join(
        f'<span class="meta-pill">{html.escape(bit)}</span>'
        for bit in [
            "Release Packet",
            stage if stage else "",
            "ready" if str(packet.get("status") or "") == "ok" else str(packet.get("status") or ""),
        ]
        if bit
    )
    return [
        """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Release Packet</div>
          <div class="viewer-truth-topline">
            <span class="viewer-truth-badge">Release Packet</span>
            <a class="viewer-truth-link" href="/playbook-library">Playbook Library</a>
          </div>
          <div class="viewer-truth-title">{title}</div>
          <p>{summary}</p>
          <div class="wiki-entity-list">{pills}</div>
        </section>
        <section class="wiki-grid">
          <article class="wiki-card">
            <h3>Commercial Truth</h3>
            <div class="wiki-links">
              <a href="/playbook-library">Current Stage</a>
              <span>{commercial_truth}</span>
            </div>
          </article>
          <article class="wiki-card">
            <h3>Related Packets</h3>
            {related_links}
          </article>
        </section>
        """.format(
            title=html.escape(str(packet.get("title") or "")),
            summary=html.escape(purpose or "현재 판매/데모/릴리스 기준선을 고정하는 packet."),
            pills=pills or '<span class="meta-pill">Release Packet</span>',
            commercial_truth=html.escape(commercial_truth or "current commercial truth unavailable"),
            related_links=related_links or '<div class="wiki-empty">연결된 release packet 이 아직 없습니다.</div>',
        ).strip()
    ]


def _build_figure_supplementary_blocks(root_dir: Path, slug: str, asset_name: str, asset: dict[str, Any]) -> list[str]:
    relation = _candidate_relations().get(slug, {})
    section_match = _figure_section_match(slug, asset_name)
    parent_title = slug.replace("_", " ").title()
    parent_summary = "이 figure 가 포함된 부모 북으로 돌아간다."
    related_entities = [
        item for item in (asset.get("related_entities") or [])
        if isinstance(item, dict) and str(item.get("href") or "").strip()
    ]
    related_entity_links = "".join(
        f'<a href="{html.escape(str(item.get("href") or ""), quote=True)}">{html.escape(str(item.get("label") or ""))}</a>'
        for item in related_entities
    )
    related_books = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "related_docs")
    )
    next_path_links = "".join(
        """
        <div class="wiki-path">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_rewrite_book_href(root_dir, str(item.get("href") or "")), quote=True),
            label=html.escape(str(item.get("label") or "")),
            summary=html.escape(str(item.get("summary") or "")),
        ).strip()
        for item in _wiki_relation_items(relation, "next_reading_path")
    )
    sibling_figures = [
        item for item in _figure_assets().get(slug, [])
        if isinstance(item, dict) and _figure_asset_filename(item) != asset_name
    ]
    sibling_figure_links = "".join(
        """
        <div class="wiki-links">
          <a href="{href}">{label}</a>
          <span>{summary}</span>
        </div>
        """.format(
            href=html.escape(_figure_viewer_href(slug, item), quote=True),
            label=html.escape(str(item.get("caption") or _figure_asset_filename(item) or "Figure")),
            summary=html.escape(str(item.get("section_hint") or "같은 문서의 다른 figure 자산")),
        ).strip()
        for item in sibling_figures[:6]
    )
    related_section_block = ""
    if isinstance(section_match, dict) and str(section_match.get("section_href") or "").strip():
        related_section_block = """
        <article class="wiki-card">
          <h3>Related Section</h3>
          <div class="wiki-links">
            <a href="{href}">{label}</a>
            <span>{summary}</span>
          </div>
        </article>
        """.format(
            href=html.escape(str(section_match.get("section_href") or ""), quote=True),
            label=html.escape(str(section_match.get("section_heading") or "Related Section")),
            summary=html.escape(str(section_match.get("section_path") or str(section_match.get("section_hint") or ""))),
        ).strip()
    return [
        """
        <section class="wiki-parent-card">
          <div class="wiki-parent-eyebrow">Parent Book</div>
          <a href="{href}">{label}</a>
          <p>{summary}</p>
        </section>
        <section class="wiki-grid">
          <article class="wiki-card">
            <h3>Entities</h3>
            <div class="wiki-entity-list">{entity_links}</div>
          </article>
          <article class="wiki-card">
            <h3>Documents</h3>
            {related_books}
          </article>
          <article class="wiki-card">
            <h3>Recommended Path</h3>
            {next_path_links}
          </article>
        </section>
        <section class="wiki-grid wiki-grid-secondary">
          {related_section_block}
          <article class="wiki-card">
            <h3>Figures</h3>
            {sibling_figure_links}
          </article>
        </section>
        """.format(
            href=html.escape(_preferred_book_href(root_dir, slug), quote=True),
            label=html.escape(parent_title),
            summary=html.escape(parent_summary),
            entity_links=related_entity_links or '<div class="wiki-empty">연결된 엔터티가 아직 없습니다.</div>',
            related_books=related_books or '<div class="wiki-empty">연관 문서가 아직 없습니다.</div>',
            next_path_links=next_path_links or '<div class="wiki-empty">연결된 경로가 아직 없습니다.</div>',
            related_section_block=related_section_block or '<article class="wiki-card"><h3>Section Match</h3><div class="wiki-empty">정확한 섹션 매칭이 아직 없습니다.</div></article>',
            sibling_figure_links=sibling_figure_links or '<div class="wiki-empty">같은 문서의 다른 figure 자산이 없습니다.</div>',
        ).strip()
    ]


def internal_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None

    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    book_slug, target_anchor = parsed
    playbook_book = _load_playbook_book(root_dir, book_slug)
    manifest_entry = _manifest_entry_for_book(root_dir, book_slug)
    if playbook_book is None:
        sections = _load_normalized_book_sections(root_dir, book_slug)
        source_url = (
            str(manifest_entry.get("source_url") or "").strip()
            or _preferred_book_href(root_dir, book_slug)
        )
        if not sections:
            markdown_path = _active_runtime_markdown_path(root_dir, book_slug)
            if markdown_path is None or not markdown_path.exists() or not markdown_path.is_file():
                return None
            sections = _markdown_sections(markdown_path.read_text(encoding="utf-8"))
            if not sections:
                return None
            book_title = (
                str(manifest_entry.get("title") or "").strip()
                or str(sections[0].get("heading") or "").strip()
                or book_slug.replace("_", " ").title()
            )
            content_sections = _trim_leading_title_section(sections, title=book_title)
            if not content_sections:
                content_sections = sections
        else:
            book_title = (
                str(manifest_entry.get("title") or "").strip()
                or str(sections[0].get("book_title") or "").strip()
                or book_slug.replace("_", " ").title()
            )
            content_sections = sections
        eyebrow = "Validated Runtime"
        summary = _normalized_book_summary(content_sections)
    else:
        sections = [dict(section) for section in (playbook_book.get("sections") or []) if isinstance(section, dict)]
        if not sections:
            return None
        book_title = str(playbook_book.get("title") or book_slug)
        source_url = str(playbook_book.get("source_uri") or "")
        eyebrow, summary = _playbook_viewer_chrome(playbook_book)
        content_sections = sections

    cards = _build_study_section_cards(content_sections, book_slug=book_slug, target_anchor=target_anchor, embedded=embedded)
    settings = load_settings(root_dir)
    return _render_study_viewer_html(
        title=book_title,
        source_url=source_url,
        cards=cards,
        section_count=len(content_sections),
        eyebrow=eyebrow,
        summary=summary,
        embedded=embedded,
        section_outline=_build_section_outline(content_sections),
        section_metrics=_build_section_metrics(content_sections),
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="book",
            target_ref=f"book:{book_slug}",
            title=book_title,
            book_slug=book_slug,
            viewer_path=f"/docs/ocp/{settings.ocp_version}/{settings.docs_language}/{book_slug}/index.html",
        ),
    )


def internal_active_runtime_markdown_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    slug = parse_active_runtime_markdown_viewer_path(viewer_path)
    if not slug:
        return None
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    markdown_path = _active_runtime_markdown_path(root_dir, slug)
    if markdown_path is None:
        return None
    if not markdown_path.exists() or not markdown_path.is_file():
        return None
    sections = _markdown_sections(markdown_path.read_text(encoding="utf-8"))
    if not sections:
        return None
    title = sections[0].get("heading") or slug.replace("_", " ").title()
    content_sections = _trim_leading_title_section(sections, title=str(title))
    summary = _markdown_summary(content_sections)
    cards = _build_study_section_cards(content_sections, book_slug=slug, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=str(title),
        source_url="",
        cards=cards,
        supplementary_blocks=_build_wiki_supplementary_blocks(root_dir, slug),
        section_count=len(content_sections),
        eyebrow="Approved Wiki Runtime Book",
        summary=summary,
        embedded=embedded,
        section_outline=_build_section_outline(content_sections),
        section_metrics=_build_section_metrics(content_sections),
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="book",
            target_ref=f"book:{slug}",
            title=str(title),
            book_slug=slug,
            viewer_path=_preferred_book_href(root_dir, slug),
        ),
    )


def internal_entity_hub_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_entity_hub_viewer_path(viewer_path)
    if parsed is None:
        return None
    entity = _entity_hubs().get(parsed)
    if entity is None:
        return None
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    sections = _entity_hub_sections(parsed)
    cards = _build_study_section_cards(sections, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=str(entity.get("title") or parsed),
        source_url="",
        cards=cards,
        supplementary_blocks=_build_entity_hub_supplementary_blocks(root_dir, parsed),
        section_count=len(sections),
        eyebrow=str(entity.get("eyebrow") or "Entity Hub"),
        summary=str(entity.get("summary") or ""),
        embedded=embedded,
        section_outline=_build_section_outline(sections),
        section_metrics=_build_section_metrics(sections),
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="entity_hub",
            target_ref=f"entity:{parsed}",
            title=str(entity.get("title") or parsed),
            entity_slug=parsed,
            viewer_path=f"/wiki/entities/{parsed}/index.html",
        ),
    )


def internal_figure_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_figure_viewer_path(viewer_path)
    if parsed is None:
        return None
    slug, asset_name = parsed
    asset = _figure_asset_by_name(slug, asset_name)
    if asset is None:
        return None
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    title = str(asset.get("caption") or asset.get("alt") or asset_name).strip() or asset_name
    sections = _figure_viewer_sections(slug, asset_name, asset)
    cards = _build_study_section_cards(sections, book_slug=slug, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=title,
        source_url=str(asset.get("asset_url") or "").strip(),
        cards=cards,
        supplementary_blocks=_build_figure_supplementary_blocks(root_dir, slug, asset_name, asset),
        section_count=len(sections),
        eyebrow="Figure Asset",
        summary=f"{slug.replace('_', ' ').title()} 문서에서 추출한 figure 자산이다.",
        embedded=embedded,
        section_outline=_build_section_outline(sections),
        section_metrics=_build_section_metrics(sections),
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="figure",
            target_ref=f"figure:{slug}:{asset_name}",
            title=title,
            book_slug=slug,
            asset_name=asset_name,
            viewer_path=f"/wiki/figures/{slug}/{asset_name}/index.html",
        ),
    )


def internal_buyer_packet_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    packet_id = parse_buyer_packet_viewer_path(viewer_path)
    if packet_id is None:
        return None
    loaded = _load_buyer_packet_entry(root_dir, packet_id)
    if loaded is None:
        return None
    bundle, packet = loaded
    markdown_path = root_dir / str(packet.get("markdown_path") or "")
    if not markdown_path.exists() or not markdown_path.is_file():
        return None
    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    sections = _markdown_sections(markdown_path.read_text(encoding="utf-8"))
    if not sections:
        return None
    title = str(packet.get("title") or packet_id)
    content_sections = _trim_leading_title_section(sections, title=title)
    summary = str(packet.get("purpose") or "").strip() or _markdown_summary(content_sections)
    cards = _build_study_section_cards(content_sections, target_anchor=request.fragment.strip(), embedded=embedded)
    return _render_study_viewer_html(
        title=title,
        source_url=f"/api/buyer-packet?packet_id={packet_id}",
        cards=cards,
        supplementary_blocks=_build_buyer_packet_supplementary_blocks(bundle, packet),
        section_count=len(content_sections),
        eyebrow="Buyer Packet",
        summary=summary,
        embedded=embedded,
        section_outline=_build_section_outline(content_sections),
        section_metrics=_build_section_metrics(content_sections),
        page_overlay_toolbar=_render_page_overlay_toolbar(
            target_kind="buyer_packet",
            target_ref=f"buyer_packet:{packet_id}",
            title=title,
            viewer_path=f"/buyer-packets/{packet_id}",
        ),
    )


__all__ = [
    "internal_active_runtime_markdown_viewer_html",
    "internal_buyer_packet_viewer_html",
    "internal_customer_pack_viewer_html",
    "internal_entity_hub_viewer_html",
    "internal_figure_viewer_html",
    "internal_viewer_html",
]
