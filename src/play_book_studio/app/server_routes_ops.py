from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from play_book_studio.app.customer_pack_read_boundary import (
    blocked_customer_pack_draft_ids_from_payload,
    sanitize_debug_chat_log_entry,
)
from play_book_studio.app.data_control_room import build_data_control_room_payload
from play_book_studio.app.repository_registry import (
    list_repository_favorites as _list_repository_favorites,
    remove_repository_favorite as _remove_repository_favorite,
    save_repository_favorites as _save_repository_favorites,
    search_github_repositories as _search_github_repositories,
)
from play_book_studio.app.wiki_user_overlay import (
    build_wiki_overlay_signal_payload as _build_wiki_overlay_signal_payload,
    list_wiki_user_overlays as _list_wiki_user_overlays,
    remove_wiki_user_overlay as _remove_wiki_user_overlay,
    save_wiki_user_overlay as _save_wiki_user_overlay,
)
from play_book_studio.config.settings import load_settings


def _list_unanswered_questions(root_dir: Path, *, limit: int = 20) -> dict[str, Any]:
    settings = load_settings(root_dir)
    target = settings.unanswered_questions_path
    if not target.exists():
        return {"count": 0, "items": []}
    rows: list[dict[str, Any]] = []
    seen_queries: set[str] = set()
    for line in reversed(target.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(payload.get("record_kind") or "") != "unanswered_question":
            continue
        query = str(payload.get("query") or "").strip()
        if not query or query in seen_queries:
            continue
        seen_queries.add(query)
        rows.append(
            {
                "query": query,
                "rewritten_query": str(payload.get("rewritten_query") or "").strip(),
                "timestamp": str(payload.get("timestamp") or "").strip(),
                "response_kind": str(payload.get("response_kind") or "").strip(),
                "warnings": [str(item) for item in (payload.get("warnings") or []) if str(item).strip()],
            }
        )
        if len(rows) >= max(1, limit):
            break
    return {"count": len(rows), "items": rows}


def handle_sessions_list(handler: Any, query: str, *, store: Any) -> None:
    params = parse_qs(query, keep_blank_values=False)
    limit_raw = str((params.get("limit") or ["50"])[0]).strip()
    try:
        limit = max(1, min(200, int(limit_raw)))
    except ValueError:
        limit = 50
    summaries = store.list_summaries(limit=limit)
    handler._send_json({"sessions": summaries, "count": len(summaries)})


def handle_session_load(handler: Any, query: str, *, store: Any) -> None:
    params = parse_qs(query, keep_blank_values=False)
    session_id = str((params.get("session_id") or [""])[0]).strip()
    if not session_id:
        handler._send_json({"error": "session_id is required"}, HTTPStatus.BAD_REQUEST)
        return
    session = store.peek(session_id)
    if session is None:
        handler._send_json({"error": "Session not found"}, HTTPStatus.NOT_FOUND)
        return
    from play_book_studio.app.sessions import serialize_session_snapshot

    payload = serialize_session_snapshot(session)
    blocked = blocked_customer_pack_draft_ids_from_payload(Path(store._root_dir or "."), payload)
    if blocked:
        handler._send_json({"error": "Session not found"}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json(payload)


def handle_session_delete(handler: Any, payload: dict[str, Any], *, store: Any) -> None:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id:
        handler._send_json({"error": "session_id is required"}, HTTPStatus.BAD_REQUEST)
        return
    deleted = bool(store.delete(session_id))
    if not deleted:
        handler._send_json({"error": "Session not found"}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json({"success": True, "session_id": session_id})


def handle_sessions_delete_all(handler: Any, payload: dict[str, Any], *, store: Any) -> None:
    del payload
    deleted_count = int(store.delete_all())
    handler._send_json({"success": True, "deleted_count": deleted_count})


def handle_debug_session(handler: Any, query: str, *, store: Any, build_session_debug_payload: Any) -> None:
    params = parse_qs(query, keep_blank_values=False)
    session_id = str((params.get("session_id") or [""])[0]).strip()
    session = store.peek(session_id) if session_id else store.latest()
    if session is None:
        handler._send_json({"error": "조회할 세션이 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    payload = build_session_debug_payload(session)
    blocked = blocked_customer_pack_draft_ids_from_payload(Path(store._root_dir or "."), payload)
    if blocked:
        handler._send_json({"error": "조회할 세션이 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json(payload)


def handle_debug_chat_log(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    limit_raw = str((params.get("limit") or ["20"])[0]).strip()
    try:
        limit = max(1, min(200, int(limit_raw or "20")))
    except ValueError:
        handler._send_json({"error": "limit는 정수여야 합니다."}, HTTPStatus.BAD_REQUEST)
        return
    log_path = load_settings(root_dir).chat_log_path
    if not log_path.exists():
        handler._send_json({"entries": [], "count": 0})
        return
    lines = log_path.read_text(encoding="utf-8").splitlines()
    entries = [json.loads(line) for line in lines[-limit:] if line.strip()]
    sanitized_entries = [
        sanitize_debug_chat_log_entry(entry)
        for entry in entries
        if not blocked_customer_pack_draft_ids_from_payload(root_dir, entry)
    ]
    handler._send_json({"entries": sanitized_entries, "count": len(sanitized_entries)})


def handle_data_control_room(handler: Any, query: str, *, root_dir: Path) -> dict[str, Any]:
    del query
    payload = build_data_control_room_payload(root_dir)
    handler._send_json(payload)
    return payload


def handle_buyer_packet(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    packet_id = str((params.get("packet_id") or [""])[0]).strip()
    if not packet_id:
        handler._send_json({"error": "packet_id가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return
    bundle_path = root_dir / "reports" / "build_logs" / "buyer_packet_bundle_index.json"
    if not bundle_path.exists():
        handler._send_json({"error": "buyer packet bundle이 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    packets = bundle.get("packets") if isinstance(bundle.get("packets"), list) else []
    match = next(
        (
            entry for entry in packets
            if isinstance(entry, dict) and str(entry.get("id") or "").strip() == packet_id
        ),
        None,
    )
    if not isinstance(match, dict):
        handler._send_json({"error": "buyer packet을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    markdown_path = root_dir / str(match.get("markdown_path") or "")
    json_path = root_dir / str(match.get("json_path") or "")
    if not markdown_path.exists():
        handler._send_json({"error": "buyer packet markdown을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json(
        {
            "packet_id": packet_id,
            "title": str(match.get("title") or packet_id),
            "purpose": str(match.get("purpose") or ""),
            "status": str(match.get("status") or ""),
            "markdown_path": str(markdown_path.resolve()),
            "json_path": str(json_path.resolve()) if json_path.exists() else "",
            "body": markdown_path.read_text(encoding="utf-8"),
        }
    )


def handle_repository_search(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    search_query = str((params.get("query") or [""])[0]).strip()
    limit_raw = str((params.get("limit") or ["12"])[0]).strip()
    try:
        limit = int(limit_raw or "12")
    except ValueError:
        handler._send_json({"error": "limit는 정수여야 합니다."}, HTTPStatus.BAD_REQUEST)
        return
    try:
        payload = _search_github_repositories(root_dir, query=search_query, limit=limit)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    except Exception as exc:  # noqa: BLE001
        handler._send_json(
            {"error": f"repository search 중 오류가 발생했습니다: {exc}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return
    handler._send_json(payload)


def handle_repository_unanswered(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    limit_raw = str((params.get("limit") or ["20"])[0]).strip()
    try:
        limit = int(limit_raw or "20")
    except ValueError:
        handler._send_json({"error": "limit는 정수여야 합니다."}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(_list_unanswered_questions(root_dir, limit=limit))


def handle_repository_favorites(handler: Any, query: str, *, root_dir: Path) -> None:
    del query
    handler._send_json(_list_repository_favorites(root_dir))


def handle_repository_favorites_save(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        saved = _save_repository_favorites(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(saved, HTTPStatus.CREATED)


def handle_repository_favorites_remove(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        saved = _remove_repository_favorite(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(saved)


def handle_wiki_user_overlays(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    user_id = str((params.get("user_id") or [""])[0]).strip()
    if not user_id:
        handler._send_json({"error": "user_id가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return
    try:
        payload = _list_wiki_user_overlays(root_dir, user_id=user_id)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(payload)


def handle_wiki_overlay_signals(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    user_id = str((params.get("user_id") or [""])[0]).strip()
    handler._send_json(_build_wiki_overlay_signal_payload(root_dir, user_id=user_id or None))


def handle_wiki_user_overlay_save(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        saved = _save_wiki_user_overlay(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(saved, HTTPStatus.CREATED)


def handle_wiki_user_overlay_remove(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        saved = _remove_wiki_user_overlay(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(saved)


__all__ = [
    "handle_buyer_packet",
    "handle_data_control_room",
    "handle_debug_chat_log",
    "handle_debug_session",
    "handle_repository_favorites",
    "handle_repository_favorites_remove",
    "handle_repository_favorites_save",
    "handle_repository_search",
    "handle_repository_unanswered",
    "handle_session_delete",
    "handle_session_load",
    "handle_sessions_delete_all",
    "handle_sessions_list",
    "handle_wiki_overlay_signals",
    "handle_wiki_user_overlay_remove",
    "handle_wiki_user_overlay_save",
    "handle_wiki_user_overlays",
]
