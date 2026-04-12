"""playbook viewer / customer-pack helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from play_book_studio.config.settings import load_settings
from play_book_studio.intake import CustomerPackDraftStore
from play_book_studio.intake.service import evaluate_canonical_book_quality

from .presenters import _default_customer_pack_summary
from .viewers import (
    _build_study_section_cards,
    _parse_viewer_path,
    _render_study_viewer_html,
)


def _playbook_book_path(root_dir: Path, book_slug: str) -> Path:
    settings = load_settings(root_dir)
    return settings.playbook_books_dir / f"{book_slug}.json"


def _playbook_book_candidates(root_dir: Path, book_slug: str) -> tuple[Path, ...]:
    settings = load_settings(root_dir)
    return tuple(directory / f"{book_slug}.json" for directory in settings.playbook_book_dirs)


def _load_playbook_book(root_dir: Path, book_slug: str) -> dict[str, Any] | None:
    for path in _playbook_book_candidates(root_dir, book_slug):
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def _playbook_viewer_chrome(playbook_book: dict[str, Any]) -> tuple[str, str]:
    source_metadata = (
        playbook_book.get("source_metadata")
        if isinstance(playbook_book.get("source_metadata"), dict)
        else {}
    )
    source_type = str(source_metadata.get("source_type") or "").strip()
    if source_type == "topic_playbook":
        summary = str(playbook_book.get("topic_summary") or "").strip()
        if not summary:
            parent_title = str(source_metadata.get("derived_from_title") or "").strip()
            if parent_title:
                summary = f"{parent_title}에서 실행 절차만 추린 토픽 플레이북입니다."
            else:
                summary = "실행 절차 중심으로 다시 엮은 토픽 플레이북입니다."
        return "Topic Playbook", summary
    return "Manual Book", "정리된 AST 기준의 유저용 매뉴얼북을 보여줍니다."


def internal_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None

    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    book_slug, target_anchor = parsed
    playbook_book = _load_playbook_book(root_dir, book_slug)
    if playbook_book is None:
        return None
    sections = [dict(section) for section in (playbook_book.get("sections") or []) if isinstance(section, dict)]
    if not sections:
        return None
    book_title = str(playbook_book.get("title") or book_slug)
    source_url = str(playbook_book.get("source_uri") or "")
    eyebrow, summary = _playbook_viewer_chrome(playbook_book)

    cards = _build_study_section_cards(sections, target_anchor=target_anchor, embedded=embedded)
    return _render_study_viewer_html(
        title=book_title,
        source_url=source_url,
        cards=cards,
        section_count=len(sections),
        eyebrow=eyebrow,
        summary=summary,
        embedded=embedded,
    )


def parse_customer_pack_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    parsed = urlparse((viewer_path or "").strip())
    request_path = parsed.path.strip()
    prefix = "/playbooks/customer-packs/"
    if not request_path.startswith(prefix):
        return None
    remainder = request_path[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) == 2 and parts[1] == "index.html":
        return parts[0], parsed.fragment.strip()
    if len(parts) == 4 and parts[1] == "assets" and parts[3] == "index.html":
        return f"{parts[0]}::{parts[2]}", parsed.fragment.strip()
    return None


def load_customer_pack_book(root_dir: Path, draft_id: str) -> dict[str, Any] | None:
    resolved_draft_id = draft_id
    asset_slug = ""
    if "::" in draft_id:
        resolved_draft_id, asset_slug = draft_id.split("::", 1)
    record = CustomerPackDraftStore(root_dir).get(draft_id)
    if record is None and resolved_draft_id != draft_id:
        record = CustomerPackDraftStore(root_dir).get(resolved_draft_id)
    if record is None or not record.canonical_book_path.strip():
        return None
    canonical_path = (
        load_settings(root_dir).customer_pack_books_dir / f"{asset_slug}.json"
        if asset_slug
        else Path(record.canonical_book_path)
    )
    if not canonical_path.exists():
        return None
    payload = json.loads(canonical_path.read_text(encoding="utf-8"))
    payload["draft_id"] = record.draft_id
    payload["target_viewer_path"] = (
        f"/playbooks/customer-packs/{record.draft_id}/assets/{asset_slug}/index.html"
        if asset_slug
        else f"/playbooks/customer-packs/{record.draft_id}/index.html"
    )
    payload["target_anchor"] = payload.get("target_anchor") or ""
    payload["source_origin_url"] = f"/api/customer-packs/captured?draft_id={record.draft_id}"
    payload.setdefault("source_collection", record.plan.source_collection)
    payload.setdefault("pack_id", record.plan.pack_id)
    payload.setdefault("pack_label", record.plan.pack_label)
    payload.setdefault("inferred_product", record.plan.inferred_product)
    payload.setdefault("inferred_version", record.plan.inferred_version)
    payload.update(evaluate_canonical_book_quality(payload))
    return payload


def internal_customer_pack_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = parse_customer_pack_viewer_path(viewer_path)
    if parsed is None:
        return None

    request = urlparse((viewer_path or "").strip())
    embedded = "embed=1" in request.query
    draft_id, target_anchor = parsed
    canonical_book = load_customer_pack_book(root_dir, draft_id)
    if canonical_book is None:
        return None

    sections = list(canonical_book.get("sections") or [])
    if not sections:
        return None
    cards = _build_study_section_cards(sections, target_anchor=target_anchor, embedded=embedded)
    family_label = str(canonical_book.get("family_label") or "").strip()
    family_summary = str(canonical_book.get("family_summary") or "").strip()
    derived_asset_count = int(canonical_book.get("derived_asset_count") or 0)
    if family_label:
        base_summary = family_summary or _default_customer_pack_summary(canonical_book)
    else:
        base_summary = _default_customer_pack_summary(canonical_book)
        if derived_asset_count > 0:
            base_summary = (
                f"{base_summary} 이 초안에서 {derived_asset_count}개의 파생 플레이북 자산이 추가로 생성되었습니다."
            )
    quality_summary = str(canonical_book.get("quality_summary") or "").strip()
    summary = f"{base_summary} {quality_summary}".strip() if quality_summary else base_summary
    if str(canonical_book.get("quality_status") or "ready") != "ready":
        summary = f"{summary} 이 자산은 아직 review needed 상태입니다."
    return _render_study_viewer_html(
        title=str(canonical_book.get("title") or draft_id),
        source_url=str(canonical_book.get("source_origin_url") or canonical_book.get("source_uri") or ""),
        cards=cards,
        section_count=len(sections),
        eyebrow=family_label or "Customer Playbook Draft",
        summary=summary,
        embedded=embedded,
    )


def list_customer_pack_drafts(root_dir: Path) -> dict[str, Any]:
    drafts: list[dict[str, Any]] = []
    store = CustomerPackDraftStore(root_dir)
    for record in store.list():
        summary = record.to_summary()
        if record.canonical_book_path.strip():
            payload = load_customer_pack_book(root_dir, record.draft_id)
            if payload is not None:
                summary["quality_status"] = payload.get("quality_status")
                summary["quality_score"] = payload.get("quality_score")
                summary["quality_summary"] = payload.get("quality_summary")
                summary["quality_flags"] = payload.get("quality_flags")
                summary["playable_asset_count"] = payload.get("playable_asset_count", 1)
                summary["derived_asset_count"] = payload.get("derived_asset_count", 0)
                summary["derived_assets"] = payload.get("derived_assets", [])
        drafts.append(summary)
    return {"drafts": drafts}


__all__ = [
    "internal_customer_pack_viewer_html",
    "internal_viewer_html",
    "list_customer_pack_drafts",
    "load_customer_pack_book",
    "parse_customer_pack_viewer_path",
]

