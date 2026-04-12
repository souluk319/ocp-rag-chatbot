# HTTP source/customer-pack 엔드포인트 로직을 server.py 밖으로 분리한다.
from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from play_book_studio.app.data_control_room import build_data_control_room_payload
from play_book_studio.config.settings import load_settings
from play_book_studio.app.intake_api import (
    build_customer_pack_plan as _build_customer_pack_plan,
    build_customer_pack_support_matrix as _build_customer_pack_support_matrix,
    capture_customer_pack_draft as _capture_customer_pack_draft,
    create_customer_pack_draft as _create_customer_pack_draft,
    load_customer_pack_capture as _load_customer_pack_capture,
    load_customer_pack_draft as _load_customer_pack_draft,
    normalize_customer_pack_draft as _normalize_customer_pack_draft,
    upload_customer_pack_draft as _upload_customer_pack_draft,
)
from play_book_studio.app.presenters import (
    _core_pack_payload,
    _customer_pack_meta_for_viewer_path,
    _humanize_book_slug,
    _manifest_entry_for_book,
    _resolve_normalized_row_for_viewer_path,
)
from play_book_studio.app.source_books import (
    load_customer_pack_book as _load_customer_pack_book,
    list_customer_pack_drafts as _list_customer_pack_drafts,
)
from play_book_studio.app.viewers import _parse_viewer_path


def handle_source_meta(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    viewer_path = str((params.get("viewer_path") or [""])[0]).strip()
    if not viewer_path:
        handler._send_json({"error": "viewer_path가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return

    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        payload = _customer_pack_meta_for_viewer_path(root_dir, viewer_path)
        if payload is None:
            handler._send_json(
                {"error": "지원하지 않는 viewer_path입니다."},
                HTTPStatus.BAD_REQUEST,
            )
            return
        handler._send_json(payload)
        return

    book_slug, anchor = parsed
    row, matched_exact = _resolve_normalized_row_for_viewer_path(root_dir, viewer_path)
    manifest_entry = _manifest_entry_for_book(root_dir, book_slug)
    book_title = (
        str((row or {}).get("book_title") or "")
        or str(manifest_entry.get("title") or "")
        or _humanize_book_slug(book_slug)
    )
    section_path = [
        str(item)
        for item in ((row or {}).get("section_path") or [])
        if str(item).strip()
    ]
    settings = load_settings(root_dir)
    handler._send_json(
        {
            "book_slug": book_slug,
            "book_title": book_title,
            "anchor": anchor,
            "section": str((row or {}).get("heading") or ""),
            "section_path": section_path,
            "section_path_label": " > ".join(section_path)
            if section_path
            else str((row or {}).get("heading") or ""),
            "source_url": str((row or {}).get("source_url") or manifest_entry.get("source_url") or ""),
            "viewer_path": viewer_path,
            "section_match_exact": matched_exact,
            **_core_pack_payload(version=settings.ocp_version, language=settings.docs_language),
        }
    )


def handle_debug_session(handler: Any, query: str, *, store: Any, build_session_debug_payload: Any) -> None:
    params = parse_qs(query, keep_blank_values=False)
    session_id = str((params.get("session_id") or [""])[0]).strip()
    session = store.peek(session_id) if session_id else store.latest()
    if session is None:
        handler._send_json({"error": "조회할 세션이 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json(build_session_debug_payload(session))


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
        handler._send_json({"entries": [], "count": 0, "path": str(log_path)})
        return

    lines = log_path.read_text(encoding="utf-8").splitlines()
    entries = [json.loads(line) for line in lines[-limit:] if line.strip()]
    handler._send_json({"entries": entries, "count": len(entries), "path": str(log_path)})


def handle_data_control_room(handler: Any, query: str, *, root_dir: Path) -> None:
    del query
    handler._send_json(build_data_control_room_payload(root_dir))


def handle_customer_pack_plan(handler: Any, payload: dict[str, Any]) -> None:
    try:
        plan = _build_customer_pack_plan(payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(plan)


def handle_customer_pack_support_matrix(handler: Any, query: str, *, root_dir: Path) -> None:
    del query, root_dir
    handler._send_json(_build_customer_pack_support_matrix())


def handle_customer_pack_drafts(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    draft_id = str((params.get("draft_id") or [""])[0]).strip()
    if not draft_id:
        handler._send_json(_list_customer_pack_drafts(root_dir))
        return

    draft = _load_customer_pack_draft(root_dir, draft_id)
    if draft is None:
        handler._send_json({"error": "업로드 플레이북 초안을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json(draft)


def handle_customer_pack_captured(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    draft_id = str((params.get("draft_id") or [""])[0]).strip()
    if not draft_id:
        handler._send_json({"error": "draft_id가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return

    capture = _load_customer_pack_capture(root_dir, draft_id)
    if capture is None:
        handler._send_json({"error": "captured artifact를 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
        return

    body, content_type = capture
    handler._send_bytes(body, content_type=content_type)


def handle_customer_pack_book(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    draft_id = str((params.get("draft_id") or [""])[0]).strip()
    if not draft_id:
        handler._send_json({"error": "draft_id가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return

    payload = _load_customer_pack_book(root_dir, draft_id)
    if payload is None:
        handler._send_json(
            {"error": "정규화된 플레이북 북을 찾을 수 없습니다."},
            HTTPStatus.NOT_FOUND,
        )
        return
    handler._send_json(payload)


def handle_customer_pack_draft_create(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        draft = _create_customer_pack_draft(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(draft, HTTPStatus.CREATED)


def handle_customer_pack_upload_draft(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        draft = _upload_customer_pack_draft(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    except Exception as exc:  # noqa: BLE001
        handler._send_json(
            {"error": f"파일 업로드 중 오류가 발생했습니다: {exc}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return
    handler._send_json(draft, HTTPStatus.CREATED)


def handle_customer_pack_capture(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        draft = _capture_customer_pack_draft(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    except FileNotFoundError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
        return
    except Exception as exc:  # noqa: BLE001
        handler._send_json(
            {"error": f"capture 중 오류가 발생했습니다: {exc}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return
    handler._send_json(draft, HTTPStatus.CREATED)


def handle_customer_pack_normalize(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        draft = _normalize_customer_pack_draft(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    except FileNotFoundError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
        return
    except Exception as exc:  # noqa: BLE001
        handler._send_json(
            {"error": f"normalize 중 오류가 발생했습니다: {exc}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return
    handler._send_json(draft, HTTPStatus.CREATED)
