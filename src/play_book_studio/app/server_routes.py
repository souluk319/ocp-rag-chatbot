# HTTP source/customer-pack 엔드포인트 로직을 server.py 밖으로 분리한다.
from __future__ import annotations

import json
import re
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urljoin, urlparse, urlunparse

from play_book_studio.app.data_control_room import build_data_control_room_payload
from play_book_studio.app.customer_pack_read_boundary import (
    blocked_customer_pack_draft_ids_from_payload,
    customer_pack_draft_id_from_viewer_path,
    load_customer_pack_read_boundary,
    sanitize_customer_pack_book_payload,
    sanitize_customer_pack_draft_payload,
    sanitize_customer_pack_mutation_payload,
    sanitize_customer_pack_source_meta_payload,
    sanitize_debug_chat_log_entry,
)
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
from play_book_studio.app.intake_api import (
    build_customer_pack_plan as _build_customer_pack_plan,
    build_customer_pack_support_matrix as _build_customer_pack_support_matrix,
    capture_customer_pack_draft as _capture_customer_pack_draft,
    create_customer_pack_draft as _create_customer_pack_draft,
    delete_customer_pack_draft as _delete_customer_pack_draft,
    ingest_customer_pack as _ingest_customer_pack,
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
    _entity_hubs,
    _figure_asset_by_name,
    _figure_section_match,
    internal_active_runtime_markdown_viewer_html as _internal_active_runtime_markdown_viewer_html,
    internal_buyer_packet_viewer_html as _internal_buyer_packet_viewer_html,
    internal_entity_hub_viewer_html as _internal_entity_hub_viewer_html,
    internal_figure_viewer_html as _internal_figure_viewer_html,
    internal_viewer_html as _internal_viewer_html,
    parse_active_runtime_markdown_viewer_path,
    parse_entity_hub_viewer_path,
    parse_figure_viewer_path,
)
from play_book_studio.app.source_books_customer_pack import (
    internal_customer_pack_viewer_html as _internal_customer_pack_viewer_html,
    list_customer_pack_drafts as _list_customer_pack_drafts,
    load_customer_pack_book as _load_customer_pack_book,
)
from play_book_studio.app.viewers import _parse_viewer_path
from play_book_studio.app.viewer_paths import _viewer_path_to_local_html


_BODY_RE = re.compile(r"<body(?P<attrs>[^>]*)>(?P<body>.*)</body>", re.IGNORECASE | re.DOTALL)
_STYLE_RE = re.compile(r"<style[^>]*>(?P<css>.*?)</style>", re.IGNORECASE | re.DOTALL)
_SCRIPT_RE = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_BODY_CLASS_RE = re.compile(r'class=(["\'])(?P<value>.*?)\1', re.IGNORECASE | re.DOTALL)
_RESOURCE_ATTR_RE = re.compile(r'(?P<attr>\b(?:src|href))=(?P<quote>["\'])(?P<value>.*?)(?P=quote)', re.IGNORECASE | re.DOTALL)
_DOCS_DIRECTORY_VIEWER_PATH_RE = re.compile(r"^/docs/ocp/[^/]+/[^/]+/[^/]+$")
_ACTIVE_RUNTIME_DIRECTORY_VIEWER_PATH_RE = re.compile(r"^/playbooks/wiki-runtime/active/[^/]+$")
_ENTITY_DIRECTORY_VIEWER_PATH_RE = re.compile(r"^/wiki/entities/[^/]+$")
_FIGURE_DIRECTORY_VIEWER_PATH_RE = re.compile(r"^/wiki/figures/[^/]+/[^/]+$")


def _send_customer_pack_read_blocked(handler: Any) -> None:
    handler._send_json(
        {"error": "요청한 customer pack runtime을 찾을 수 없습니다."},
        HTTPStatus.NOT_FOUND,
    )


def _customer_pack_read_allowed(root_dir: Path, draft_id: str) -> bool:
    summary = load_customer_pack_read_boundary(root_dir, draft_id)
    return bool(summary.get("read_allowed", False))


def _scope_viewer_style(style_text: str) -> str:
    return (
        str(style_text or "")
        .replace(":root", ".viewer-root")
        .replace("body.is-embedded", ".viewer-root.is-embedded")
        .replace("body", ".viewer-root")
    )


def _canonicalize_viewer_path(viewer_path: str) -> str:
    raw = str(viewer_path or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    path = parsed.path.strip()
    if not path:
        return raw

    normalized_path = path if path == "/" else path.rstrip("/")
    if (
        normalized_path
        and not normalized_path.endswith("/index.html")
        and (
            _DOCS_DIRECTORY_VIEWER_PATH_RE.fullmatch(normalized_path)
            or _ACTIVE_RUNTIME_DIRECTORY_VIEWER_PATH_RE.fullmatch(normalized_path)
            or _ENTITY_DIRECTORY_VIEWER_PATH_RE.fullmatch(normalized_path)
            or _FIGURE_DIRECTORY_VIEWER_PATH_RE.fullmatch(normalized_path)
        )
    ):
        normalized_path = f"{normalized_path}/index.html"

    if normalized_path == path:
        return raw
    return urlunparse(parsed._replace(path=normalized_path))


def _viewer_html_for_path(root_dir: Path, viewer_path: str) -> str | None:
    viewer_path = _canonicalize_viewer_path(viewer_path)
    internal_html = (
      _internal_buyer_packet_viewer_html(root_dir, viewer_path)
      or _internal_customer_pack_viewer_html(root_dir, viewer_path)
      or _internal_active_runtime_markdown_viewer_html(root_dir, viewer_path)
      or _internal_entity_hub_viewer_html(root_dir, viewer_path)
      or _internal_figure_viewer_html(root_dir, viewer_path)
      or _internal_viewer_html(root_dir, viewer_path)
    )
    if internal_html is not None:
      return internal_html
    local_html = _viewer_path_to_local_html(root_dir, viewer_path)
    if local_html is not None:
      return local_html.read_text(encoding="utf-8")
    return None


def _normalize_viewer_resource_urls(html_text: str, viewer_path: str) -> str:
    base = f"http://runtime.local{viewer_path}"

    def _replace(match: re.Match[str]) -> str:
        value = str(match.group("value") or "").strip()
        if not value or value.startswith("#") or re.match(r"^(?:data:|blob:|mailto:|tel:|javascript:)", value, re.IGNORECASE):
            return match.group(0)
        absolute = urljoin(base, value)
        normalized = absolute.replace("http://runtime.local", "", 1)
        return f'{match.group("attr")}={match.group("quote")}{normalized}{match.group("quote")}'

    return _RESOURCE_ATTR_RE.sub(_replace, html_text)


def _build_viewer_document_payload(html_text: str, viewer_path: str) -> dict[str, Any]:
    body_match = _BODY_RE.search(html_text)
    body_attrs = body_match.group("attrs") if body_match else ""
    body_html = body_match.group("body") if body_match else html_text
    class_match = _BODY_CLASS_RE.search(body_attrs)
    body_class_name = str(class_match.group("value") if class_match else "").strip()
    inline_styles = [
        _scope_viewer_style(match.group("css"))
        for match in _STYLE_RE.finditer(html_text)
        if str(match.group("css") or "").strip()
    ]
    normalized_body_html = _normalize_viewer_resource_urls(_SCRIPT_RE.sub("", body_html), viewer_path)
    return {
        "viewer_path": viewer_path,
        "body_class_name": body_class_name,
        "inline_styles": inline_styles,
        "html": normalized_body_html,
        "interaction_policy": {
            "code_copy": True,
            "code_wrap_toggle": True,
            "recent_position_tracking": True,
            "anchor_navigation": True,
        },
    }


def _official_runtime_source_meta(
    *,
    root_dir: Path,
    viewer_path: str,
    resolved_viewer_path: str,
    book_slug: str,
    anchor: str,
) -> dict[str, Any]:
    row, matched_exact = _resolve_normalized_row_for_viewer_path(root_dir, resolved_viewer_path)
    manifest_entry = _manifest_entry_for_book(root_dir, book_slug)
    settings = load_settings(root_dir)
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
    pack_label = str(manifest_entry.get("pack_label") or settings.active_pack.pack_label or "").strip()
    runtime_truth_label = f"{pack_label} Runtime" if pack_label else "Validated Pack Runtime"
    return {
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
        "source_lane": str(manifest_entry.get("source_lane") or "approved_wiki_runtime"),
        "approval_state": str(manifest_entry.get("approval_state") or "approved"),
        "publication_state": str(manifest_entry.get("publication_state") or "active"),
        "parser_backend": str(manifest_entry.get("parser_backend") or ""),
        "boundary_truth": "official_validated_runtime",
        "runtime_truth_label": runtime_truth_label,
        "boundary_badge": "Validated Runtime",
        **_core_pack_payload(version=settings.ocp_version, language=settings.docs_language),
    }


def _viewer_source_meta(root_dir: Path, viewer_path: str) -> dict[str, Any] | None:
    viewer_path = _canonicalize_viewer_path(viewer_path)
    customer_pack_meta = _customer_pack_meta_for_viewer_path(root_dir, viewer_path)
    if customer_pack_meta is not None:
        return customer_pack_meta

    parsed = _parse_viewer_path(viewer_path)
    if parsed is not None:
        book_slug, anchor = parsed
        return _official_runtime_source_meta(
            root_dir=root_dir,
            viewer_path=viewer_path,
            resolved_viewer_path=viewer_path,
            book_slug=book_slug,
            anchor=anchor,
        )

    active_book_slug = parse_active_runtime_markdown_viewer_path(viewer_path)
    if active_book_slug:
        anchor = viewer_path.split("#", 1)[1].strip() if "#" in viewer_path else ""
        settings = load_settings(root_dir)
        docs_viewer_path = f"/docs/ocp/{settings.ocp_version}/{settings.docs_language}/{active_book_slug}/index.html"
        if anchor:
            docs_viewer_path = f"{docs_viewer_path}#{anchor}"
        return _official_runtime_source_meta(
            root_dir=root_dir,
            viewer_path=viewer_path,
            resolved_viewer_path=docs_viewer_path,
            book_slug=active_book_slug,
            anchor=anchor,
        )

    entity_slug = parse_entity_hub_viewer_path(viewer_path)
    if entity_slug:
        entity = _entity_hubs().get(entity_slug)
        if entity is None:
            return None
        title = str(entity.get("title") or entity_slug).strip() or entity_slug
        return {
            "book_slug": entity_slug,
            "book_title": title,
            "anchor": "",
            "section": title,
            "section_path": [title],
            "section_path_label": title,
            "source_url": "",
            "viewer_path": viewer_path,
            "section_match_exact": True,
            "source_lane": "approved_wiki_runtime",
            "approval_state": "approved",
            "publication_state": "active",
            "parser_backend": "",
            "boundary_truth": "official_validated_runtime",
            "runtime_truth_label": "Validated Runtime Entity Hub",
            "boundary_badge": "Validated Runtime",
            **_core_pack_payload(),
        }

    figure_parsed = parse_figure_viewer_path(viewer_path)
    if figure_parsed is not None:
        slug, asset_name = figure_parsed
        asset = _figure_asset_by_name(slug, asset_name)
        if asset is None:
            return None
        caption = str(asset.get("caption") or asset.get("alt") or asset_name).strip() or asset_name
        section_match = _figure_section_match(slug, asset_name) or {}
        section_path = [
            str(section_match.get("section_heading") or "").strip(),
            caption,
        ]
        section_path = [item for item in section_path if item]
        return {
            "book_slug": slug,
            "book_title": caption,
            "anchor": asset_name,
            "section": caption,
            "section_path": section_path,
            "section_path_label": " > ".join(section_path) if section_path else caption,
            "source_url": str(asset.get("asset_url") or "").strip(),
            "viewer_path": viewer_path,
            "section_match_exact": True,
            "source_lane": "approved_wiki_runtime",
            "approval_state": "approved",
            "publication_state": "active",
            "parser_backend": "",
            "boundary_truth": "official_validated_runtime",
            "runtime_truth_label": "Validated Runtime Figure",
            "boundary_badge": "Validated Runtime",
            **_core_pack_payload(),
        }

    return None


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


def handle_source_meta(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    viewer_path = str((params.get("viewer_path") or [""])[0]).strip()
    if not viewer_path:
        handler._send_json({"error": "viewer_path가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return
    customer_pack_draft_id = customer_pack_draft_id_from_viewer_path(viewer_path)
    if customer_pack_draft_id and not _customer_pack_read_allowed(root_dir, customer_pack_draft_id):
        _send_customer_pack_read_blocked(handler)
        return

    payload = _viewer_source_meta(root_dir, viewer_path)
    if payload is None:
        handler._send_json(
            {"error": "지원하지 않는 viewer_path입니다."},
            HTTPStatus.BAD_REQUEST,
        )
        return
    if customer_pack_draft_id:
        payload = sanitize_customer_pack_source_meta_payload(payload)
    handler._send_json(payload)


def handle_viewer_document(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    viewer_path = str((params.get("viewer_path") or [""])[0]).strip()
    if not viewer_path:
        handler._send_json({"error": "viewer_path가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return
    viewer_path = _canonicalize_viewer_path(viewer_path)
    customer_pack_draft_id = customer_pack_draft_id_from_viewer_path(viewer_path)
    if customer_pack_draft_id and not _customer_pack_read_allowed(root_dir, customer_pack_draft_id):
        _send_customer_pack_read_blocked(handler)
        return
    html_text = _viewer_html_for_path(root_dir, viewer_path)
    if html_text is None:
        handler._send_json({"error": "viewer document를 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json(_build_viewer_document_payload(html_text, viewer_path))


def handle_runtime_figures(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    book_slug = str((params.get("book_slug") or [""])[0]).strip()
    limit_raw = str((params.get("limit") or ["3"])[0]).strip()
    if not book_slug:
      handler._send_json({"error": "book_slug가 필요합니다."}, HTTPStatus.BAD_REQUEST)
      return
    try:
      limit = max(1, min(12, int(limit_raw or "3")))
    except ValueError:
      limit = 3
    asset_path = root_dir / "data" / "wiki_relations" / "figure_assets.json"
    if not asset_path.exists():
      handler._send_json({"count": 0, "items": []})
      return
    payload = json.loads(asset_path.read_text(encoding="utf-8"))
    entries = payload.get("entries") if isinstance(payload.get("entries"), dict) else {}
    items = entries.get(book_slug) if isinstance(entries, dict) else []
    if not isinstance(items, list):
      items = []
    normalized: list[dict[str, Any]] = []
    for item in items[:limit]:
      if not isinstance(item, dict):
        continue
      normalized.append(
        {
          "caption": str(item.get("caption") or item.get("alt") or "Figure"),
          "viewer_path": str(item.get("viewer_path") or "").strip(),
          "asset_url": str(item.get("asset_url") or "").strip(),
          "asset_kind": str(item.get("asset_kind") or "figure"),
          "diagram_type": str(item.get("diagram_type") or "").strip(),
          "section_hint": str(item.get("section_hint") or "").strip(),
        }
      )
    handler._send_json({"count": len(normalized), "items": normalized, "book_slug": book_slug})


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
        payload = _list_customer_pack_drafts(root_dir)
        allowed_drafts = [
            sanitize_customer_pack_draft_payload(draft)
            for draft in (payload.get("drafts") or [])
            if isinstance(draft, dict)
            and _customer_pack_read_allowed(root_dir, str(draft.get("draft_id") or ""))
        ]
        handler._send_json({"drafts": allowed_drafts, "count": len(allowed_drafts)})
        return
    if not _customer_pack_read_allowed(root_dir, draft_id):
        _send_customer_pack_read_blocked(handler)
        return

    draft = _load_customer_pack_draft(root_dir, draft_id)
    if draft is None:
        handler._send_json({"error": "업로드 플레이북 초안을 찾을 수 없습니다."}, HTTPStatus.NOT_FOUND)
        return
    handler._send_json(sanitize_customer_pack_draft_payload(draft))


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


def handle_customer_pack_captured(handler: Any, query: str, *, root_dir: Path) -> None:
    params = parse_qs(query, keep_blank_values=False)
    draft_id = str((params.get("draft_id") or [""])[0]).strip()
    if not draft_id:
        handler._send_json({"error": "draft_id가 필요합니다."}, HTTPStatus.BAD_REQUEST)
        return
    if not _customer_pack_read_allowed(root_dir, draft_id):
        _send_customer_pack_read_blocked(handler)
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
    if not _customer_pack_read_allowed(root_dir, draft_id):
        _send_customer_pack_read_blocked(handler)
        return

    payload = _load_customer_pack_book(root_dir, draft_id)
    if payload is None:
        handler._send_json(
            {"error": "정규화된 플레이북 북을 찾을 수 없습니다."},
            HTTPStatus.NOT_FOUND,
        )
        return
    handler._send_json(sanitize_customer_pack_book_payload(payload))


def handle_customer_pack_draft_create(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        draft = _create_customer_pack_draft(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler._send_json(sanitize_customer_pack_mutation_payload(draft), HTTPStatus.CREATED)


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
    handler._send_json(sanitize_customer_pack_mutation_payload(draft), HTTPStatus.CREATED)


def handle_customer_pack_ingest(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    try:
        draft = _ingest_customer_pack(root_dir, payload)
    except ValueError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    except FileNotFoundError as exc:
        handler._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
        return
    except Exception as exc:  # noqa: BLE001
        handler._send_json(
            {"error": f"ingest 중 오류가 발생했습니다: {exc}"},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        return
    handler._send_json(sanitize_customer_pack_mutation_payload(draft), HTTPStatus.CREATED)


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
    handler._send_json(sanitize_customer_pack_mutation_payload(draft), HTTPStatus.CREATED)


def handle_customer_pack_delete_draft(handler: Any, payload: dict[str, Any], *, root_dir: Path) -> None:
    draft_id = str(payload.get("draft_id") or "").strip()
    if not draft_id:
        handler._send_json({"error": "draft_id is required"}, HTTPStatus.BAD_REQUEST)
        return
    success = _delete_customer_pack_draft(root_dir, draft_id)
    if success:
        handler._send_json({"success": True, "draft_id": draft_id})
    else:
        handler._send_json({"error": "Draft not found"}, HTTPStatus.NOT_FOUND)


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
    handler._send_json(sanitize_customer_pack_mutation_payload(draft), HTTPStatus.CREATED)
