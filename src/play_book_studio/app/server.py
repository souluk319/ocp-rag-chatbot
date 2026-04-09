"""Play Book Studio의 HTTP 런타임 진입점."""
from __future__ import annotations

import json
import mimetypes
import threading
import uuid
import webbrowser
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
    handle_debug_chat_log as _handle_debug_chat_log_request,
    handle_debug_session as _handle_debug_session_request,
    handle_doc_to_book_book as _handle_doc_to_book_book_request,
    handle_doc_to_book_capture as _handle_doc_to_book_capture_request,
    handle_doc_to_book_captured as _handle_doc_to_book_captured_request,
    handle_doc_to_book_draft_create as _handle_doc_to_book_draft_create_request,
    handle_doc_to_book_drafts as _handle_doc_to_book_drafts_request,
    handle_doc_to_book_normalize as _handle_doc_to_book_normalize_request,
    handle_doc_to_book_plan as _handle_doc_to_book_plan_request,
    handle_doc_to_book_upload_draft as _handle_doc_to_book_upload_draft_request,
    handle_source_meta as _handle_source_meta_request,
)
from play_book_studio.app.chat_debug import (
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
    internal_doc_to_book_viewer_html as _internal_doc_to_book_viewer_html,
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
DEFAULT_RUNTIME_TOP_K = 8
DEFAULT_RUNTIME_CANDIDATE_K = 20
DEFAULT_RUNTIME_MAX_CONTEXT_CHUNKS = 6
def _build_chat_payload(
    *,
    root_dir: Path,
    answerer: ChatAnswerer | None = None,
    session: ChatSession,
    result: AnswerResult,
) -> dict[str, Any]:
    # UI 응답과 재현성 로그에 쓰는 chat payload serialization helper.
    payload = {
        "session_id": session.session_id,
        "mode": session.mode,
        "answer": result.answer,
        "rewritten_query": result.rewritten_query,
        "response_kind": result.response_kind,
        "warnings": list(result.warnings),
        "cited_indices": list(result.cited_indices),
        "citations": [
            _serialize_citation(root_dir, citation)
            for citation in result.citations
        ],
        "suggested_queries": _suggest_follow_up_questions(session=session, result=result),
        "context": session.context.to_dict(),
        "history_size": len(session.history),
        "retrieval_trace": dict(result.retrieval_trace),
        "pipeline_trace": dict(result.pipeline_trace),
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
    # REST endpoint를 answerer, session store, viewer, doc-to-book helper에
    # 실제로 연결하는 구간이다.
    answerer_lock = threading.Lock()
    current_llm_signature = _llm_runtime_signature(answerer.settings)

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

            if request_path in {"/", "/index.html"}:
                self._send_html(INDEX_HTML_PATH.read_text(encoding="utf-8"))
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
            if request_path == "/api/health":
                self._send_json(_build_health_payload(current_answerer()))
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
            if request_path == "/api/doc-to-book/drafts":
                self._handle_doc_to_book_drafts(parsed_request.query)
                return
            if request_path == "/api/doc-to-book/book":
                self._handle_doc_to_book_book(parsed_request.query)
                return
            if request_path == "/api/doc-to-book/captured":
                self._handle_doc_to_book_captured(parsed_request.query)
                return
            internal_doc_to_book_viewer = _internal_doc_to_book_viewer_html(root_dir, self.path)
            if internal_doc_to_book_viewer is not None:
                self._send_html(internal_doc_to_book_viewer)
                return
            internal_viewer = _internal_viewer_html(root_dir, self.path)
            if internal_viewer is not None:
                self._send_html(internal_viewer)
                return
            local_html = _viewer_path_to_local_html(root_dir, self.path)
            if local_html is not None:
                self._send_html(local_html.read_text(encoding="utf-8"))
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
            if self.path == "/api/doc-to-book/plan":
                self._handle_doc_to_book_plan(payload)
                return
            if self.path == "/api/doc-to-book/drafts":
                self._handle_doc_to_book_draft_create(payload)
                return
            if self.path == "/api/doc-to-book/upload-draft":
                self._handle_doc_to_book_upload_draft(payload)
                return
            if self.path == "/api/doc-to-book/capture":
                self._handle_doc_to_book_capture(payload)
                return
            if self.path == "/api/doc-to-book/normalize":
                self._handle_doc_to_book_normalize(payload)
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

        def _handle_doc_to_book_plan(self, payload: dict[str, Any]) -> None:
            _handle_doc_to_book_plan_request(self, payload)

        def _handle_doc_to_book_drafts(self, query: str) -> None:
            _handle_doc_to_book_drafts_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_doc_to_book_captured(self, query: str) -> None:
            _handle_doc_to_book_captured_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_doc_to_book_book(self, query: str) -> None:
            _handle_doc_to_book_book_request(
                self,
                query,
                root_dir=root_dir,
            )

        def _handle_doc_to_book_draft_create(self, payload: dict[str, Any]) -> None:
            _handle_doc_to_book_draft_create_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_doc_to_book_upload_draft(self, payload: dict[str, Any]) -> None:
            _handle_doc_to_book_upload_draft_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_doc_to_book_capture(self, payload: dict[str, Any]) -> None:
            _handle_doc_to_book_capture_request(
                self,
                payload,
                root_dir=root_dir,
            )

        def _handle_doc_to_book_normalize(self, payload: dict[str, Any]) -> None:
            _handle_doc_to_book_normalize_request(
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
    store = SessionStore()
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
