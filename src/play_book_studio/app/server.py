"""Play Book Studio의 HTTP 런타임 진입점."""
from __future__ import annotations

import json
import mimetypes
import threading
import time
import uuid
import webbrowser
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from play_book_studio.answering.answerer import ChatAnswerer
from play_book_studio.answering.models import AnswerResult
from play_book_studio.app.server_chat import (
    handle_chat as _handle_chat_request,
    handle_chat_stream as _handle_chat_stream_request,
)
from play_book_studio.app.server_routes import (
    handle_data_control_room as _handle_data_control_room_request,
    handle_debug_chat_log as _handle_debug_chat_log_request,
    handle_debug_session as _handle_debug_session_request,
    handle_customer_pack_book as _handle_customer_pack_book_request,
    handle_buyer_packet as _handle_buyer_packet_request,
    handle_customer_pack_capture as _handle_customer_pack_capture_request,
    handle_customer_pack_captured as _handle_customer_pack_captured_request,
    handle_customer_pack_draft_create as _handle_customer_pack_draft_create_request,
    handle_customer_pack_drafts as _handle_customer_pack_drafts_request,
    handle_customer_pack_ingest as _handle_customer_pack_ingest_request,
    handle_customer_pack_delete_draft as _handle_customer_pack_delete_draft_request,
    handle_sessions_list as _handle_sessions_list_request,
    handle_session_load as _handle_session_load_request,
    handle_session_delete as _handle_session_delete_request,
    handle_sessions_delete_all as _handle_sessions_delete_all_request,
    handle_customer_pack_normalize as _handle_customer_pack_normalize_request,
    handle_customer_pack_plan as _handle_customer_pack_plan_request,
    handle_customer_pack_support_matrix as _handle_customer_pack_support_matrix_request,
    handle_customer_pack_upload_draft as _handle_customer_pack_upload_draft_request,
    handle_repository_favorites as _handle_repository_favorites_request,
    handle_repository_favorites_remove as _handle_repository_favorites_remove_request,
    handle_repository_favorites_save as _handle_repository_favorites_save_request,
    handle_repository_search as _handle_repository_search_request,
    handle_repository_unanswered as _handle_repository_unanswered_request,
    handle_runtime_figures as _handle_runtime_figures_request,
    handle_source_meta as _handle_source_meta_request,
    handle_wiki_overlay_signals as _handle_wiki_overlay_signals_request,
    handle_wiki_user_overlay_remove as _handle_wiki_user_overlay_remove_request,
    handle_wiki_user_overlay_save as _handle_wiki_user_overlay_save_request,
    handle_wiki_user_overlays as _handle_wiki_user_overlays_request,
)
from play_book_studio.app.chat_debug import (
    append_unanswered_question_log as _append_unanswered_question_log,
    append_chat_turn_log as _append_chat_turn_log,
    build_session_debug_payload as _build_session_debug_payload,
    build_turn_diagnosis as _build_turn_diagnosis,
    build_turn_stages as _build_turn_stages,
    write_recent_chat_session_snapshot as _write_recent_chat_session_snapshot,
)
from play_book_studio.app.presenters import (
    _build_health_payload,
    _llm_runtime_signature,
    _refresh_answerer_llm_settings,
    _serialize_citation,
)
from play_book_studio.app.source_books import (
    build_chat_navigation_links as _build_chat_navigation_links,
    internal_buyer_packet_viewer_html as _internal_buyer_packet_viewer_html,
    build_chat_section_links as _build_chat_section_links,
    internal_customer_pack_viewer_html as _internal_customer_pack_viewer_html,
    internal_entity_hub_viewer_html as _internal_entity_hub_viewer_html,
    internal_figure_viewer_html as _internal_figure_viewer_html,
    internal_gold_candidate_markdown_viewer_html as _internal_gold_candidate_markdown_viewer_html,
    internal_viewer_html as _internal_viewer_html,
)
from play_book_studio.app.session_flow import (
    context_with_request_overrides as _context_with_request_overrides,
    derive_next_context as _derive_next_context,
    suggest_follow_up_questions as _suggest_follow_up_questions,
)
from play_book_studio.app.sessions import ChatSession, SessionStore
from play_book_studio.app.viewers import _viewer_path_to_local_html


STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML_PATH = STATIC_DIR / "index.html"
WORKSPACE_HTML_PATH = STATIC_DIR / "workspace.html"
DATA_SITUATION_ROOM_HTML_PATH = STATIC_DIR / "data-situation-room.html"
DEFAULT_RUNTIME_TOP_K = 8
DEFAULT_RUNTIME_CANDIDATE_K = 20
DEFAULT_RUNTIME_MAX_CONTEXT_CHUNKS = 6
BLOCKED_LEGACY_VIEWER_PREFIXES = (
    "/playbooks/gold-candidates/",
    "/playbooks/wiki-runtime/wave1/",
)
DATA_CONTROL_ROOM_CACHE_TTL_SECONDS = 30.0
VIEWER_HTML_CACHE_TTL_SECONDS = 45.0


class _TimedValueCache:
    def __init__(self, ttl_seconds: float) -> None:
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._items: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        now = time.monotonic()
        with self._lock:
            cached = self._items.get(key)
            if cached is None:
                return None
            created_at, value = cached
            if now - created_at > self.ttl_seconds:
                self._items.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any) -> Any:
        with self._lock:
            self._items[key] = (time.monotonic(), value)
        return value


def _build_chat_payload(
    *,
    root_dir: Path,
    answerer: ChatAnswerer | None = None,
    session: ChatSession,
    result: AnswerResult,
) -> dict[str, Any]:
    # UI 응답과 재현성 로그에 쓰는 chat payload serialization helper.
    serialized_citations = [
        _serialize_citation(root_dir, citation)
        for citation in result.citations
    ]
    payload = {
        "session_id": session.session_id,
        "mode": session.mode,
        "answer": result.answer,
        "rewritten_query": result.rewritten_query,
        "response_kind": result.response_kind,
        "warnings": list(result.warnings),
        "cited_indices": list(result.cited_indices),
        "citations": serialized_citations,
        "related_links": _build_chat_navigation_links(
            root_dir,
            serialized_citations,
            user_id=session.context.user_id,
        ),
        "related_sections": _build_chat_section_links(
            root_dir,
            serialized_citations,
            user_id=session.context.user_id,
        ),
        "suggested_queries": _suggest_follow_up_questions(session=session, result=result),
        "context": session.context.to_dict(),
        "history_size": len(session.history),
        "retrieval_trace": dict(result.retrieval_trace),
        "pipeline_trace": dict(result.pipeline_trace),
    }
    if result.response_kind == "no_answer":
        payload["acquisition"] = {
            "kind": "repository_search",
            "title": "현재 Playbook Library에 해당 자료가 없습니다.",
            "body": "자료 추가를 원하시면 체크 후 확인을 눌러주세요.",
            "checkbox_label": "Repository에서 우선순위로 필요한 데이터 찾기",
            "confirm_label": "확인",
            "repository_query": (result.rewritten_query or result.query or "").strip(),
        }
    if answerer is not None:
        payload["runtime"] = _build_health_payload(answerer)["runtime"]
    return payload


def _build_handler(
    *,
    answerer: ChatAnswerer,
    store: SessionStore,
    root_dir: Path,
) -> type[BaseHTTPRequestHandler]:
    # REST endpoint를 answerer, session store, viewer, customer-pack helper에
    # 실제로 연결하는 구간이다.
    answerer_lock = threading.Lock()
    current_llm_signature = _llm_runtime_signature(answerer.settings)
    data_control_room_cache = _TimedValueCache(DATA_CONTROL_ROOM_CACHE_TTL_SECONDS)
    viewer_html_cache = _TimedValueCache(VIEWER_HTML_CACHE_TTL_SECONDS)

    def current_answerer() -> ChatAnswerer:
        nonlocal answerer, current_llm_signature
        with answerer_lock:
            answerer, current_llm_signature = _refresh_answerer_llm_settings(
                answerer,
                root_dir=root_dir,
                current_signature=current_llm_signature,
            )
            return answerer

    class ChatHandler(BaseHTTPRequestHandler):
        server_version = "PlayBookStudio/0.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return None

        def _debug_timing(self, label: str, started_at: float) -> None:
            elapsed = time.monotonic() - started_at
            print(f"[timing] {label} {elapsed:.3f}s", file=sys.stderr, flush=True)

        def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def _send_bytes(
            self,
            body: bytes,
            *,
            content_type: str,
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def _start_ndjson_stream(self) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

        def _stream_event(self, payload: dict[str, Any]) -> None:
            try:
                body = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
                self.wfile.write(body)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return

        def do_GET(self) -> None:  # noqa: N802
            parsed_request = urlparse(self.path)
            request_path = parsed_request.path
            started_at = time.monotonic()

            if any(request_path.startswith(prefix) for prefix in BLOCKED_LEGACY_VIEWER_PREFIXES):
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                return

            if request_path in {"/", "/index.html"}:
                self._send_html(INDEX_HTML_PATH.read_text(encoding="utf-8"))
                return
            if request_path in {"/studio", "/studio.html"}:
                self._send_html(WORKSPACE_HTML_PATH.read_text(encoding="utf-8"))
                return
            if request_path in {"/data-situation-room", "/data-situation-room.html"}:
                self._send_html(DATA_SITUATION_ROOM_HTML_PATH.read_text(encoding="utf-8"))
                return
            if request_path.startswith("/assets/"):
                relative = request_path.removeprefix("/assets/").strip("/")
                asset_path = (STATIC_DIR / "assets" / relative).resolve()
                assets_root = (STATIC_DIR / "assets").resolve()
                if assets_root in asset_path.parents and asset_path.is_file():
                    content_type = mimetypes.guess_type(str(asset_path))[0] or "application/octet-stream"
                    self._send_bytes(asset_path.read_bytes(), content_type=content_type)
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            if request_path.startswith("/playbooks/wiki-assets/"):
                relative = request_path.removeprefix("/playbooks/wiki-assets/").strip("/")
                asset_path = (root_dir / "data" / "wiki_assets" / relative).resolve()
                assets_root = (root_dir / "data" / "wiki_assets").resolve()
                if asset_path.is_file() and (asset_path == assets_root or assets_root in asset_path.parents):
                    content_type = mimetypes.guess_type(str(asset_path))[0] or "application/octet-stream"
                    self._send_bytes(asset_path.read_bytes(), content_type=content_type)
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            if request_path == "/api/health":
                self._send_json(_build_health_payload(current_answerer()))
                return
            if request_path == "/api/data-control-room":
                started_at = time.monotonic()
                self._handle_data_control_room(parsed_request.query)
                self._debug_timing("data-control-room", started_at)
                return
            if request_path == "/api/buyer-packet":
                self._handle_buyer_packet(parsed_request.query)
                return
            if request_path == "/api/customer-packs/support-matrix":
                self._handle_customer_pack_support_matrix(parsed_request.query)
                return
            if request_path == "/api/sessions":
                self._handle_sessions_list(parsed_request.query)
                return
            if request_path == "/api/sessions/load":
                self._handle_session_load(parsed_request.query)
                return
            if request_path == "/api/debug/session":
                self._handle_debug_session(parsed_request.query)
                return
            if request_path == "/api/debug/chat-log":
                self._handle_debug_chat_log(parsed_request.query)
                return
            if request_path == "/api/source-meta":
                self._handle_source_meta(parsed_request.query)
                return
            if request_path == "/api/runtime-figures":
                self._handle_runtime_figures(parsed_request.query)
                return
            if request_path == "/api/repositories/search":
                self._handle_repository_search(parsed_request.query)
                return
            if request_path == "/api/repositories/unanswered":
                self._handle_repository_unanswered(parsed_request.query)
                return
            if request_path == "/api/repositories/favorites":
                self._handle_repository_favorites(parsed_request.query)
                return
            if request_path == "/api/wiki-overlays":
                self._handle_wiki_user_overlays(parsed_request.query)
                return
            if request_path == "/api/wiki-overlay-signals":
                self._handle_wiki_overlay_signals(parsed_request.query)
                return
            if request_path == "/api/customer-packs/drafts":
                self._handle_customer_pack_drafts(parsed_request.query)
                return
            if request_path == "/api/customer-packs/book":
                self._handle_customer_pack_book(parsed_request.query)
                return
            if request_path == "/api/customer-packs/captured":
                self._handle_customer_pack_captured(parsed_request.query)
                return
            viewer_cache_key = self.path
            cached_viewer_html = viewer_html_cache.get(viewer_cache_key)
            if isinstance(cached_viewer_html, str):
                self._send_html(cached_viewer_html)
                return

            local_html = _viewer_path_to_local_html(root_dir, self.path)
            if local_html is not None:
                self._send_html(viewer_html_cache.set(viewer_cache_key, local_html.read_text(encoding="utf-8")))
                self._debug_timing(f"viewer:{request_path}", started_at)
                return

            internal_buyer_packet_viewer = _internal_buyer_packet_viewer_html(root_dir, self.path)
            if internal_buyer_packet_viewer is not None:
                self._send_html(viewer_html_cache.set(viewer_cache_key, internal_buyer_packet_viewer))
                return
            internal_customer_pack_viewer = _internal_customer_pack_viewer_html(root_dir, self.path)
            if internal_customer_pack_viewer is not None:
                self._send_html(viewer_html_cache.set(viewer_cache_key, internal_customer_pack_viewer))
                return
            internal_gold_candidate_markdown_viewer = _internal_gold_candidate_markdown_viewer_html(root_dir, self.path)
            if internal_gold_candidate_markdown_viewer is not None:
                self._send_html(viewer_html_cache.set(viewer_cache_key, internal_gold_candidate_markdown_viewer))
                self._debug_timing(f"viewer:{request_path}", started_at)
                return
            internal_entity_hub_viewer = _internal_entity_hub_viewer_html(root_dir, self.path)
            if internal_entity_hub_viewer is not None:
                self._send_html(viewer_html_cache.set(viewer_cache_key, internal_entity_hub_viewer))
                return
            internal_figure_viewer = _internal_figure_viewer_html(root_dir, self.path)
            if internal_figure_viewer is not None:
                self._send_html(viewer_html_cache.set(viewer_cache_key, internal_figure_viewer))
                return
            internal_viewer = _internal_viewer_html(root_dir, self.path)
            if internal_viewer is not None:
                self._send_html(viewer_html_cache.set(viewer_cache_key, internal_viewer))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self) -> None:  # noqa: N802
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            try:
                payload = json.loads(raw_body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_json({"error": "잘못된 JSON 요청입니다."}, HTTPStatus.BAD_REQUEST)
                return

            if self.path == "/api/chat":
                self._handle_chat(payload)
                return
            if self.path == "/api/chat/stream":
                self._handle_chat_stream(payload)
                return
            if self.path == "/api/sessions/delete":
                self._handle_session_delete(payload)
                return
            if self.path == "/api/sessions/delete-all":
                self._handle_sessions_delete_all(payload)
                return
            if self.path == "/api/customer-packs/plan":
                self._handle_customer_pack_plan(payload)
                return
            if self.path == "/api/customer-packs/drafts":
                self._handle_customer_pack_draft_create(payload)
                return
            if self.path == "/api/customer-packs/upload-draft":
                self._handle_customer_pack_upload_draft(payload)
                return
            if self.path == "/api/customer-packs/ingest":
                self._handle_customer_pack_ingest(payload)
                return
            if self.path == "/api/customer-packs/capture":
                self._handle_customer_pack_capture(payload)
                return
            if self.path == "/api/customer-packs/normalize":
                self._handle_customer_pack_normalize(payload)
                return
            if self.path == "/api/customer-packs/delete-draft":
                self._handle_customer_pack_delete_draft(payload)
                return
            if self.path == "/api/repositories/favorites":
                self._handle_repository_favorites_save(payload)
                return
            if self.path == "/api/repositories/favorites/remove":
                self._handle_repository_favorites_remove(payload)
                return
            if self.path == "/api/wiki-overlays":
                self._handle_wiki_user_overlay_save(payload)
                return
            if self.path == "/api/wiki-overlays/remove":
                self._handle_wiki_user_overlay_remove(payload)
                return
            if self.path == "/api/reset":
                self._handle_reset(payload)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _handle_source_meta(self, query: str) -> None:
            _handle_source_meta_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_repository_search(self, query: str) -> None:
            _handle_repository_search_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_runtime_figures(self, query: str) -> None:
            _handle_runtime_figures_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_repository_favorites(self, query: str) -> None:
            _handle_repository_favorites_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_repository_unanswered(self, query: str) -> None:
            _handle_repository_unanswered_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_wiki_user_overlays(self, query: str) -> None:
            _handle_wiki_user_overlays_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_wiki_overlay_signals(self, query: str) -> None:
            _handle_wiki_overlay_signals_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_data_control_room(self, query: str) -> None:
            del query
            cached_payload = data_control_room_cache.get("payload")
            if isinstance(cached_payload, dict):
                self._send_json(cached_payload)
                return
            payload = _handle_data_control_room_request(
                self,
                "",
                root_dir=root_dir,
            )
            if payload is not None:
                data_control_room_cache.set("payload", payload)

        def _handle_buyer_packet(self, query: str) -> None:
            _handle_buyer_packet_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_sessions_list(self, query: str) -> None:
            _handle_sessions_list_request(self, query, store=store)

        def _handle_session_load(self, query: str) -> None:
            _handle_session_load_request(self, query, store=store)

        def _handle_session_delete(self, payload: dict[str, Any]) -> None:
            _handle_session_delete_request(self, payload, store=store)

        def _handle_sessions_delete_all(self, payload: dict[str, Any]) -> None:
            _handle_sessions_delete_all_request(self, payload, store=store)

        def _handle_debug_session(self, query: str) -> None:
            _handle_debug_session_request(
                self,
                query,
                store=store,
                build_session_debug_payload=_build_session_debug_payload,
            )

        def _handle_debug_chat_log(self, query: str) -> None:
            _handle_debug_chat_log_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_customer_pack_plan(self, payload: dict[str, Any]) -> None:
            _handle_customer_pack_plan_request(self, payload)

        def _handle_customer_pack_support_matrix(self, query: str) -> None:
            _handle_customer_pack_support_matrix_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_customer_pack_drafts(self, query: str) -> None:
            _handle_customer_pack_drafts_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_customer_pack_captured(self, query: str) -> None:
            _handle_customer_pack_captured_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_customer_pack_book(self, query: str) -> None:
            _handle_customer_pack_book_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_customer_pack_draft_create(self, payload: dict[str, Any]) -> None:
            _handle_customer_pack_draft_create_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_customer_pack_upload_draft(self, payload: dict[str, Any]) -> None:
            _handle_customer_pack_upload_draft_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_customer_pack_ingest(self, payload: dict[str, Any]) -> None:
            _handle_customer_pack_ingest_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_customer_pack_capture(self, payload: dict[str, Any]) -> None:
            _handle_customer_pack_capture_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_customer_pack_normalize(self, payload: dict[str, Any]) -> None:
            _handle_customer_pack_normalize_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_customer_pack_delete_draft(self, payload: dict[str, Any]) -> None:
            _handle_customer_pack_delete_draft_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_repository_favorites_save(self, payload: dict[str, Any]) -> None:
            _handle_repository_favorites_save_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_repository_favorites_remove(self, payload: dict[str, Any]) -> None:
            _handle_repository_favorites_remove_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_wiki_user_overlay_save(self, payload: dict[str, Any]) -> None:
            _handle_wiki_user_overlay_save_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_wiki_user_overlay_remove(self, payload: dict[str, Any]) -> None:
            _handle_wiki_user_overlay_remove_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_chat(self, payload: dict[str, Any]) -> None:
            _handle_chat_request(
                self,
                payload,
                current_answerer=current_answerer,
                store=store,
                root_dir=root_dir,
                build_chat_payload=_build_chat_payload,
                context_with_request_overrides=_context_with_request_overrides,
                derive_next_context=_derive_next_context,
                append_chat_turn_log=_append_chat_turn_log,
                append_unanswered_question_log=_append_unanswered_question_log,
                write_recent_chat_session_snapshot=_write_recent_chat_session_snapshot,
                build_turn_stages=_build_turn_stages,
                build_turn_diagnosis=_build_turn_diagnosis,
            )

        def _handle_chat_stream(self, payload: dict[str, Any]) -> None:
            _handle_chat_stream_request(
                self,
                payload,
                current_answerer=current_answerer,
                store=store,
                root_dir=root_dir,
                build_chat_payload=_build_chat_payload,
                context_with_request_overrides=_context_with_request_overrides,
                derive_next_context=_derive_next_context,
                append_chat_turn_log=_append_chat_turn_log,
                append_unanswered_question_log=_append_unanswered_question_log,
                write_recent_chat_session_snapshot=_write_recent_chat_session_snapshot,
                build_turn_stages=_build_turn_stages,
                build_turn_diagnosis=_build_turn_diagnosis,
            )

        def _handle_reset(self, payload: dict[str, Any]) -> None:
            session_id = str(payload.get("session_id") or uuid.uuid4().hex)
            session = store.reset(session_id)
            self._send_json(
                {
                    "session_id": session.session_id,
                    "mode": session.mode,
                    "context": session.context.to_dict(),
                }
            )

    return ChatHandler


def serve(
    *,
    answerer: ChatAnswerer,
    root_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    # `play_book.cmd ui`가 호출하는 공개 진입점이다.
    store = SessionStore(root_dir)
    handler = _build_handler(answerer=answerer, store=store, root_dir=root_dir)
    server = ThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{port}"
    print(f"Play Book Studio UI running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


__all__ = [
    "ChatSession",
    "SessionStore",
    "serve",
]
