from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from play_book_studio.config.settings import load_settings

from .wiki_relations import load_wiki_relation_assets
from .wiki_user_overlay_targets import (
    _book_title_lookup,
    _candidate_links_from_book,
    _candidate_links_from_entity,
    _candidate_links_from_figure,
    _candidate_links_from_section,
    _normalize_overlay_target,
    _resolve_overlay_target_for_item,
    resolve_overlay_target,
)

VALID_OVERLAY_KINDS = {"favorite", "check", "note", "recent_position"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _overlay_dir(root_dir: Path) -> Path:
    path = load_settings(root_dir).runtime_dir / "wiki_overlays"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _overlay_document_path(root_dir: Path) -> Path:
    return _overlay_dir(root_dir) / "overlays.json"


def _load_overlay_document(root_dir: Path) -> dict[str, Any]:
    path = _overlay_document_path(root_dir)
    if not path.exists():
        return {"version": 1, "updated_at": "", "items": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "updated_at": "", "items": []}
    items = payload.get("items")
    if not isinstance(items, list):
        items = []
    return {
        "version": 1,
        "updated_at": str(payload.get("updated_at") or ""),
        "items": [dict(item) for item in items if isinstance(item, dict)],
    }


def _overlay_timestamp(value: str) -> str:
    normalized = str(value or "").strip()
    return normalized or "1970-01-01T00:00:00Z"


def _overlay_signal_weight(kind: str) -> int:
    return {"favorite": 4, "check": 3, "note": 2, "recent_position": 1}.get(str(kind or "").strip(), 0)


def _save_overlay_document(root_dir: Path, payload: dict[str, Any]) -> None:
    _overlay_document_path(root_dir).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _upsert_policy(kind: str) -> bool:
    return kind in {"favorite", "check", "recent_position"}


def list_wiki_user_overlays(root_dir: Path, *, user_id: str) -> dict[str, Any]:
    normalized_user_id = str(user_id or "").strip()
    if not normalized_user_id:
        raise ValueError("user_id가 필요합니다.")
    document = _load_overlay_document(root_dir)
    items: list[dict[str, Any]] = []
    for item in document.get("items", []):
        if str(item.get("user_id") or "").strip() != normalized_user_id:
            continue
        enriched = dict(item)
        enriched["resolved_target"] = _resolve_overlay_target_for_item(root_dir, item)
        items.append(enriched)
    items.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
    return {"count": len(items), "updated_at": document.get("updated_at") or "", "items": items}


def _top_signal_items(root_dir: Path) -> list[dict[str, Any]]:
    document = _load_overlay_document(root_dir)
    title_lookup = _book_title_lookup(root_dir)
    grouped: dict[str, dict[str, Any]] = {}
    for item in document.get("items", []):
        if not isinstance(item, dict):
            continue
        target_ref = str(item.get("target_ref") or "").strip()
        target_kind = str(item.get("target_kind") or "").strip()
        if not target_ref or not target_kind:
            continue
        resolved = _resolve_overlay_target_for_item(root_dir, item)
        bucket = grouped.setdefault(
            target_ref,
            {
                "target_ref": target_ref,
                "target_kind": target_kind,
                "book_slug": str(item.get("book_slug") or resolved.get("book_slug") or "").strip(),
                "title": str(resolved.get("title") or item.get("title") or title_lookup.get(str(item.get("book_slug") or "").strip()) or target_ref).strip(),
                "viewer_path": str(resolved.get("viewer_path") or item.get("viewer_path") or "").strip(),
                "summary": str(resolved.get("summary") or item.get("summary") or "").strip(),
                "kind_breakdown": Counter(),
                "count": 0,
                "user_ids": set(),
                "last_touched_at": "",
                "weight_score": 0,
            },
        )
        kind = str(item.get("kind") or "").strip()
        bucket["kind_breakdown"][kind] += 1
        bucket["count"] += 1
        bucket["weight_score"] += _overlay_signal_weight(kind)
        bucket["user_ids"].add(str(item.get("user_id") or "").strip())
        updated_at = _overlay_timestamp(str(item.get("updated_at") or ""))
        if updated_at > str(bucket.get("last_touched_at") or ""):
            bucket["last_touched_at"] = updated_at
    ranked: list[dict[str, Any]] = []
    for item in grouped.values():
        breakdown = item["kind_breakdown"]
        primary_kind = ""
        primary_count = 0
        if breakdown:
            primary_kind, primary_count = max(
                breakdown.items(),
                key=lambda pair: (_overlay_signal_weight(pair[0]), pair[1], pair[0]),
            )
        ranked.append(
            {
                "target_ref": item["target_ref"],
                "target_kind": item["target_kind"],
                "book_slug": item["book_slug"],
                "title": item["title"],
                "viewer_path": item["viewer_path"],
                "summary": item["summary"],
                "count": int(item["count"]),
                "user_count": len(item["user_ids"]),
                "last_touched_at": str(item["last_touched_at"] or ""),
                "weight_score": int(item["weight_score"]),
                "kind_breakdown": dict(sorted(breakdown.items())),
                "primary_kind": primary_kind,
                "primary_kind_count": primary_count,
            }
        )
    ranked.sort(
        key=lambda entry: (
            int(entry.get("weight_score") or 0),
            int(entry.get("count") or 0),
            str(entry.get("last_touched_at") or ""),
            str(entry.get("title") or ""),
        ),
        reverse=True,
    )
    return ranked


def _build_personalized_next_plays(root_dir: Path, user_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dedupe: set[str] = set()
    plays: list[dict[str, Any]] = []
    for item in user_items:
        target_kind = str(item.get("target_kind") or "").strip()
        target_ref = str(item.get("target_ref") or "").strip()
        kind = str(item.get("kind") or "").strip()
        reason_prefix = {
            "favorite": "즐겨찾기 기반",
            "check": "체크 완료 후 다음 경로",
            "note": "개인 메모 기반",
            "recent_position": "최근 위치 기반",
        }.get(kind, "overlay 기반")
        candidates: list[dict[str, Any]] = []
        if target_kind == "book" and target_ref.startswith("book:"):
            candidates = _candidate_links_from_book(root_dir, target_ref.split(":", 1)[1].strip())
        elif target_kind == "entity_hub" and target_ref.startswith("entity:"):
            candidates = _candidate_links_from_entity(root_dir, target_ref.split(":", 1)[1].strip())
        elif target_kind == "section" and target_ref.startswith("section:"):
            remainder = target_ref.split(":", 1)[1]
            if "#" in remainder:
                book_slug, anchor = remainder.split("#", 1)
                candidates = _candidate_links_from_section(root_dir, book_slug.strip(), anchor.strip())
        elif target_kind == "figure" and target_ref.startswith("figure:"):
            remainder = target_ref.split(":", 1)[1]
            if ":" in remainder:
                book_slug, asset_name = remainder.split(":", 1)
                candidates = _candidate_links_from_figure(root_dir, book_slug.strip(), asset_name.strip())
        for candidate in candidates:
            href = str(candidate.get("href") or "").strip()
            if not href or href in dedupe:
                continue
            dedupe.add(href)
            plays.append(
                {
                    "label": str(candidate.get("label") or "").strip(),
                    "href": href,
                    "kind": str(candidate.get("kind") or "book").strip(),
                    "summary": str(candidate.get("summary") or "").strip(),
                    "reason": reason_prefix,
                    "source_target_ref": target_ref,
                    "source_overlay_kind": kind,
                }
            )
            if len(plays) >= 8:
                return plays
    return plays


def build_wiki_overlay_signal_payload(root_dir: Path, *, user_id: str | None = None) -> dict[str, Any]:
    document = _load_overlay_document(root_dir)
    items = [dict(item) for item in document.get("items", []) if isinstance(item, dict)]
    kind_counter = Counter(str(item.get("kind") or "").strip() for item in items)
    target_count = len({str(item.get("target_ref") or "").strip() for item in items if str(item.get("target_ref") or "").strip()})
    user_count = len({str(item.get("user_id") or "").strip() for item in items if str(item.get("user_id") or "").strip()})
    payload: dict[str, Any] = {
        "updated_at": str(document.get("updated_at") or ""),
        "summary": {
            "total_overlay_count": len(items),
            "favorite_count": int(kind_counter.get("favorite", 0)),
            "check_count": int(kind_counter.get("check", 0)),
            "note_count": int(kind_counter.get("note", 0)),
            "recent_position_count": int(kind_counter.get("recent_position", 0)),
            "target_count": target_count,
            "user_count": user_count,
        },
        "top_targets": _top_signal_items(root_dir)[:12],
    }
    normalized_user_id = str(user_id or "").strip()
    if normalized_user_id:
        user_items = [dict(item) for item in items if str(item.get("user_id") or "").strip() == normalized_user_id]
        user_items.sort(key=lambda item: _overlay_timestamp(str(item.get("updated_at") or "")), reverse=True)
        recent_targets: list[dict[str, Any]] = []
        for item in user_items:
            resolved = _resolve_overlay_target_for_item(root_dir, item)
            recent_targets.append(
                {
                    "overlay_id": str(item.get("overlay_id") or ""),
                    "kind": str(item.get("kind") or ""),
                    "target_ref": str(item.get("target_ref") or ""),
                    "target_kind": str(item.get("target_kind") or ""),
                    "label": str(resolved.get("title") or item.get("title") or item.get("target_ref") or "").strip(),
                    "href": str(resolved.get("viewer_path") or item.get("viewer_path") or "").strip(),
                    "summary": str(resolved.get("summary") or item.get("summary") or "").strip(),
                    "updated_at": str(item.get("updated_at") or ""),
                }
            )
        payload["user_focus"] = {
            "user_id": normalized_user_id,
            "overlay_count": len(user_items),
            "favorite_count": sum(1 for item in user_items if str(item.get("kind") or "") == "favorite"),
            "check_count": sum(1 for item in user_items if str(item.get("kind") or "") == "check"),
            "note_count": sum(1 for item in user_items if str(item.get("kind") or "") == "note"),
            "recent_position_count": sum(1 for item in user_items if str(item.get("kind") or "") == "recent_position"),
            "recent_targets": recent_targets[:6],
            "recommended_next_plays": _build_personalized_next_plays(root_dir, user_items),
        }
    return payload


def save_wiki_user_overlay(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    kind = str(payload.get("kind") or "").strip()
    if kind not in VALID_OVERLAY_KINDS:
        raise ValueError("kind는 favorite, check, note, recent_position 중 하나여야 합니다.")
    user_id = str(payload.get("user_id") or "").strip()
    if not user_id:
        raise ValueError("user_id가 필요합니다.")
    target_kind, target_ref, book_slug = _normalize_overlay_target(payload)
    document = _load_overlay_document(root_dir)
    items = [dict(item) for item in document.get("items", []) if isinstance(item, dict)]
    overlay_id = str(payload.get("overlay_id") or "").strip()
    now = _now_iso()
    record = {
        "overlay_id": overlay_id or f"ovl-{uuid4().hex[:12]}",
        "user_id": user_id,
        "kind": kind,
        "target_kind": target_kind,
        "target_ref": target_ref,
        "book_slug": book_slug,
        "payload": dict(payload.get("payload") or {}),
        "created_at": now,
        "updated_at": now,
    }
    if kind == "check":
        record["status"] = str(payload.get("status") or "checked").strip() or "checked"
        record["checked_at"] = now if record["status"] == "checked" else ""
    if kind == "note":
        record["body"] = str(payload.get("body") or "").strip()
        record["pinned"] = bool(payload.get("pinned", False))
    if kind == "favorite":
        record["title"] = str(payload.get("title") or "").strip()
        record["summary"] = str(payload.get("summary") or "").strip()
    resolved = _resolve_overlay_target_for_item(root_dir, record)
    record["viewer_path"] = str(payload.get("viewer_path") or record.get("viewer_path") or resolved.get("viewer_path") or "").strip()
    replaced = False
    new_items: list[dict[str, Any]] = []
    for item in items:
        if _upsert_policy(kind):
            if str(item.get("user_id") or "").strip() == user_id and str(item.get("kind") or "").strip() == kind and str(item.get("target_ref") or "").strip() == target_ref:
                record["overlay_id"] = str(item.get("overlay_id") or record["overlay_id"])
                record["created_at"] = str(item.get("created_at") or record["created_at"])
                new_items.append(record)
                replaced = True
                continue
        elif overlay_id and str(item.get("overlay_id") or "").strip() == overlay_id:
            record["created_at"] = str(item.get("created_at") or record["created_at"])
            new_items.append(record)
            replaced = True
            continue
        new_items.append(item)
    if not replaced:
        new_items.append(record)
    document["items"] = new_items
    document["updated_at"] = now
    _save_overlay_document(root_dir, document)
    return {"saved": True, "record": {**record, "resolved_target": _resolve_overlay_target_for_item(root_dir, record)}, "count": len(new_items), "updated_at": document["updated_at"]}


def remove_wiki_user_overlay(root_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = str(payload.get("user_id") or "").strip()
    overlay_id = str(payload.get("overlay_id") or "").strip()
    kind = str(payload.get("kind") or "").strip()
    target_ref = str(payload.get("target_ref") or "").strip()
    if not user_id:
        raise ValueError("user_id가 필요합니다.")
    if not overlay_id and not (kind and target_ref):
        raise ValueError("overlay_id 또는 kind+target_ref가 필요합니다.")
    document = _load_overlay_document(root_dir)
    remaining: list[dict[str, Any]] = []
    removed = 0
    for item in document.get("items", []):
        item_user_id = str(item.get("user_id") or "").strip()
        if item_user_id != user_id:
            remaining.append(dict(item))
            continue
        if overlay_id and str(item.get("overlay_id") or "").strip() == overlay_id:
            removed += 1
            continue
        if kind and target_ref and str(item.get("kind") or "").strip() == kind and str(item.get("target_ref") or "").strip() == target_ref:
            removed += 1
            continue
        remaining.append(dict(item))
    document["items"] = remaining
    document["updated_at"] = _now_iso()
    _save_overlay_document(root_dir, document)
    return {"removed": removed, "count": len(remaining), "updated_at": document["updated_at"]}


__all__ = [
    "build_wiki_overlay_signal_payload",
    "list_wiki_user_overlays",
    "remove_wiki_user_overlay",
    "resolve_overlay_target",
    "save_wiki_user_overlay",
]
