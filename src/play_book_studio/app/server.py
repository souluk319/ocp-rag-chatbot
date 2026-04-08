"""Play Book Studio의 HTTP 런타임.

채팅 요청 하나가 어떻게 처리되는지 보려면 `cli.py` 다음으로 이 파일을 보면 된다:
request parsing -> session/context update -> answer generation -> UI payload
"""

from __future__ import annotations

import html
import json
import mimetypes
import re
import threading
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from play_book_studio.config.settings import Settings, load_settings
from play_book_studio.config.validation import read_jsonl
from play_book_studio.retrieval.models import SessionContext
from play_book_studio.answering.answerer import Part3Answerer
from play_book_studio.answering.models import AnswerResult
from play_book_studio.app.chat_debug import (
    append_chat_turn_log as _append_chat_turn_log,
    build_session_debug_payload as _build_session_debug_payload,
    build_turn_diagnosis as _build_turn_diagnosis,
    build_turn_stages as _build_turn_stages,
    write_recent_chat_session_snapshot as _write_recent_chat_session_snapshot,
)
from play_book_studio.app.intake_api import (
    build_doc_to_book_plan as _build_doc_to_book_plan,
    capture_doc_to_book_draft as _capture_doc_to_book_draft,
    create_doc_to_book_draft as _create_doc_to_book_draft,
    load_doc_to_book_capture as _load_doc_to_book_capture,
    load_doc_to_book_draft as _load_doc_to_book_draft,
    normalize_doc_to_book_draft as _normalize_doc_to_book_draft,
    upload_doc_to_book_draft as _upload_doc_to_book_draft,
)
from play_book_studio.app.presenters import (
    _build_health_payload,
    _citation_href,
    _core_pack_payload,
    _doc_to_book_book_for_viewer_path,
    _doc_to_book_meta_for_viewer_path,
    _humanize_book_slug,
    _llm_runtime_signature,
    _manifest_entry_for_book,
    _refresh_answerer_llm_settings,
    _resolve_normalized_row_for_viewer_path,
    _serialize_citation,
)
from play_book_studio.app.source_books import (
    canonical_source_book as _canonical_source_book,
    internal_doc_to_book_viewer_html as _internal_doc_to_book_viewer_html,
    internal_viewer_html as _internal_viewer_html,
    list_doc_to_book_drafts as _list_doc_to_book_drafts,
    load_doc_to_book_book as _load_doc_to_book_book,
)
from play_book_studio.app.session_flow import (
    context_with_request_overrides as _context_with_request_overrides,
    derive_next_context as _derive_next_context,
    suggest_follow_up_questions as _suggest_follow_up_questions,
)
from play_book_studio.app.sessions import (
    RUNTIME_CHAT_MODE,
    ChatSession,
    SessionStore,
    Turn,
)
from play_book_studio.app.viewers import (
    _parse_viewer_path,
    _render_normalized_section_html,
    _viewer_path_to_local_html,
)


STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML_PATH = STATIC_DIR / "index.html"
DEFAULT_RUNTIME_TOP_K = 8
DEFAULT_RUNTIME_CANDIDATE_K = 20
DEFAULT_RUNTIME_MAX_CONTEXT_CHUNKS = 6




































def _build_chat_payload(
    *,
    root_dir: Path,
    answerer: Part3Answerer | None = None,
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
    answerer: Part3Answerer,
    store: SessionStore,
    root_dir: Path,
) -> type[BaseHTTPRequestHandler]:
    # REST endpoint를 answerer, session store, viewer, doc-to-book helper에
    # 실제로 연결하는 구간이다.
    answerer_lock = threading.Lock()
    current_llm_signature = _llm_runtime_signature(answerer.settings)

    def current_answerer() -> Part3Answerer:
        nonlocal answerer, current_llm_signature
        with answerer_lock:
            answerer, current_llm_signature = _refresh_answerer_llm_settings(
                answerer,
                root_dir=root_dir,
                current_signature=current_llm_signature,
            )
            return answerer

    class ChatHandler(BaseHTTPRequestHandler):
        server_version = "OCPRAGPart4/0.1"

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
            if request_path == "/api/source-book":
                self._handle_source_book(parsed_request.query)
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
            params = parse_qs(query, keep_blank_values=False)
            viewer_path = str((params.get("viewer_path") or [""])[0]).strip()
            if not viewer_path:
                self._send_json(
                    {"error": "viewer_path가 필요합니다."},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            parsed = _parse_viewer_path(viewer_path)
            if parsed is None:
                payload = _doc_to_book_meta_for_viewer_path(root_dir, viewer_path)
                if payload is None:
                    self._send_json(
                        {"error": "지원하지 않는 viewer_path입니다."},
                        HTTPStatus.BAD_REQUEST,
                    )
                    return
                self._send_json(payload)
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
            self._send_json(
                {
                    "book_slug": book_slug,
                    "book_title": book_title,
                    "anchor": anchor,
                    "section": str((row or {}).get("heading") or ""),
                    "section_path": section_path,
                    "section_path_label": (
                        " > ".join(section_path)
                        if section_path
                        else str((row or {}).get("heading") or "")
                    ),
                    "source_url": str((row or {}).get("source_url") or manifest_entry.get("source_url") or ""),
                    "viewer_path": viewer_path,
                    "section_match_exact": matched_exact,
                    **_core_pack_payload(version=settings.ocp_version, language=settings.docs_language),
                }
            )

        def _handle_debug_session(self, query: str) -> None:
            params = parse_qs(query, keep_blank_values=False)
            session_id = str((params.get("session_id") or [""])[0]).strip()
            session = store.peek(session_id) if session_id else store.latest()
            if session is None:
                self._send_json(
                    {"error": "조회할 세션이 없습니다."},
                    HTTPStatus.NOT_FOUND,
                )
                return
            self._send_json(_build_session_debug_payload(session))

        def _handle_debug_chat_log(self, query: str) -> None:
            params = parse_qs(query, keep_blank_values=False)
            limit_raw = str((params.get("limit") or ["20"])[0]).strip()
            try:
                limit = max(1, min(200, int(limit_raw or "20")))
            except ValueError:
                self._send_json({"error": "limit는 정수여야 합니다."}, HTTPStatus.BAD_REQUEST)
                return

            log_path = load_settings(root_dir).chat_log_path
            if not log_path.exists():
                self._send_json({"entries": [], "count": 0, "path": str(log_path)})
                return

            lines = log_path.read_text(encoding="utf-8").splitlines()
            entries = [json.loads(line) for line in lines[-limit:] if line.strip()]
            self._send_json(
                {
                    "entries": entries,
                    "count": len(entries),
                    "path": str(log_path),
                }
            )

        def _handle_source_book(self, query: str) -> None:
            params = parse_qs(query, keep_blank_values=False)
            viewer_path = str((params.get("viewer_path") or [""])[0]).strip()
            if not viewer_path:
                self._send_json(
                    {"error": "viewer_path가 필요합니다."},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            canonical_book = _canonical_source_book(root_dir, viewer_path)
            if canonical_book is None:
                canonical_book = _doc_to_book_book_for_viewer_path(root_dir, viewer_path)
            if canonical_book is None:
                self._send_json(
                    {"error": "canonical source book을 만들 수 없습니다."},
                    HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(canonical_book)

        def _handle_doc_to_book_plan(self, payload: dict[str, Any]) -> None:
            try:
                plan = _build_doc_to_book_plan(payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return

            self._send_json(plan)

        def _handle_doc_to_book_drafts(self, query: str) -> None:
            params = parse_qs(query, keep_blank_values=False)
            draft_id = str((params.get("draft_id") or [""])[0]).strip()
            if not draft_id:
                self._send_json(_list_doc_to_book_drafts(root_dir))
                return

            draft = _load_doc_to_book_draft(root_dir, draft_id)
            if draft is None:
                self._send_json(
                    {"error": "doc-to-book draft를 찾을 수 없습니다."},
                    HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(draft)

        def _handle_doc_to_book_captured(self, query: str) -> None:
            params = parse_qs(query, keep_blank_values=False)
            draft_id = str((params.get("draft_id") or [""])[0]).strip()
            if not draft_id:
                self._send_json(
                    {"error": "draft_id가 필요합니다."},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            capture = _load_doc_to_book_capture(root_dir, draft_id)
            if capture is None:
                self._send_json(
                    {"error": "captured artifact를 찾을 수 없습니다."},
                    HTTPStatus.NOT_FOUND,
                )
                return

            body, content_type = capture
            self._send_bytes(body, content_type=content_type)

        def _handle_doc_to_book_book(self, query: str) -> None:
            params = parse_qs(query, keep_blank_values=False)
            draft_id = str((params.get("draft_id") or [""])[0]).strip()
            if not draft_id:
                self._send_json(
                    {"error": "draft_id가 필요합니다."},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            payload = _load_doc_to_book_book(root_dir, draft_id)
            if payload is None:
                self._send_json(
                    {"error": "canonical doc-to-book book을 찾을 수 없습니다."},
                    HTTPStatus.NOT_FOUND,
                )
                return

            self._send_json(payload)

        def _handle_doc_to_book_draft_create(self, payload: dict[str, Any]) -> None:
            try:
                draft = _create_doc_to_book_draft(root_dir, payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return

            self._send_json(draft, HTTPStatus.CREATED)

        def _handle_doc_to_book_upload_draft(self, payload: dict[str, Any]) -> None:
            try:
                draft = _upload_doc_to_book_draft(root_dir, payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    {"error": f"파일 업로드 중 오류가 발생했습니다: {exc}"},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
                return

            self._send_json(draft, HTTPStatus.CREATED)

        def _handle_doc_to_book_capture(self, payload: dict[str, Any]) -> None:
            try:
                draft = _capture_doc_to_book_draft(root_dir, payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            except FileNotFoundError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
                return
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    {"error": f"capture 중 오류가 발생했습니다: {exc}"},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
                return

            self._send_json(draft, HTTPStatus.CREATED)

        def _handle_doc_to_book_normalize(self, payload: dict[str, Any]) -> None:
            try:
                draft = _normalize_doc_to_book_draft(root_dir, payload)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            except FileNotFoundError as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
                return
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    {"error": f"normalize 중 오류가 발생했습니다: {exc}"},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
                return

            self._send_json(draft, HTTPStatus.CREATED)

        def _handle_chat(self, payload: dict[str, Any]) -> None:
            active_answerer = current_answerer()
            session_id = str(payload.get("session_id") or uuid.uuid4().hex)
            session = store.get(session_id)
            mode = RUNTIME_CHAT_MODE
            regenerate = bool(payload.get("regenerate", False))
            query = str(payload.get("query") or "").strip()
            request_context = _context_with_request_overrides(
                session.context,
                payload=payload,
                mode=mode,
                default_ocp_version=answerer.settings.ocp_version,
            )
            context_before = SessionContext.from_dict(request_context.to_dict())
            if regenerate and not query:
                query = session.last_query

            if not query:
                self._send_json({"error": "질문을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
                return

            try:
                result = active_answerer.answer(
                    query,
                    mode=mode,
                    context=request_context,
                    top_k=DEFAULT_RUNTIME_TOP_K,
                    candidate_k=DEFAULT_RUNTIME_CANDIDATE_K,
                    max_context_chunks=DEFAULT_RUNTIME_MAX_CONTEXT_CHUNKS,
                )
                active_answerer.append_log(result)
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    {"error": f"답변 생성 중 오류가 발생했습니다: {exc}"},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
                return

            session.mode = RUNTIME_CHAT_MODE
            session.context = _derive_next_context(
                request_context,
                query=query,
                mode=mode,
                result=result,
                default_ocp_version=answerer.settings.ocp_version,
            )
            session.history.append(
                Turn(
                    query=query,
                    mode=mode,
                    answer=result.answer,
                    rewritten_query=result.rewritten_query,
                    response_kind=result.response_kind,
                    warnings=list(result.warnings),
                    stages=_build_turn_stages(result),
                    diagnosis=_build_turn_diagnosis(result),
                )
            )
            session.history = session.history[-20:]
            store.update(session)
            _append_chat_turn_log(
                root_dir,
                answerer=active_answerer,
                session=session,
                query=query,
                result=result,
                context_before=context_before,
                context_after=session.context,
            )
            _write_recent_chat_session_snapshot(
                root_dir,
                session=session,
            )
            self._send_json(
                _build_chat_payload(
                    root_dir=root_dir,
                    answerer=active_answerer,
                    session=session,
                    result=result,
                )
            )

        def _handle_chat_stream(self, payload: dict[str, Any]) -> None:
            active_answerer = current_answerer()
            session_id = str(payload.get("session_id") or uuid.uuid4().hex)
            session = store.get(session_id)
            mode = RUNTIME_CHAT_MODE
            regenerate = bool(payload.get("regenerate", False))
            query = str(payload.get("query") or "").strip()
            request_context = _context_with_request_overrides(
                session.context,
                payload=payload,
                mode=mode,
                default_ocp_version=answerer.settings.ocp_version,
            )
            context_before = SessionContext.from_dict(request_context.to_dict())
            if regenerate and not query:
                query = session.last_query

            if not query:
                self._send_json({"error": "질문을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
                return

            self._start_ndjson_stream()
            self._stream_event(
                {
                    "type": "trace",
                    "step": "request_received",
                    "label": "질문 접수 완료",
                    "status": "done",
                    "detail": query[:180],
                }
            )

            def emit_trace(event: dict[str, Any]) -> None:
                self._stream_event(event)

            try:
                result = active_answerer.answer(
                    query,
                    mode=mode,
                    context=request_context,
                    top_k=DEFAULT_RUNTIME_TOP_K,
                    candidate_k=DEFAULT_RUNTIME_CANDIDATE_K,
                    max_context_chunks=DEFAULT_RUNTIME_MAX_CONTEXT_CHUNKS,
                    trace_callback=emit_trace,
                )
                active_answerer.append_log(result)
            except Exception as exc:  # noqa: BLE001
                self._stream_event(
                    {
                        "type": "error",
                        "error": f"답변 생성 중 오류가 발생했습니다: {exc}",
                    }
                )
                return

            session.mode = RUNTIME_CHAT_MODE
            session.context = _derive_next_context(
                request_context,
                query=query,
                mode=mode,
                result=result,
                default_ocp_version=answerer.settings.ocp_version,
            )
            session.history.append(
                Turn(
                    query=query,
                    mode=mode,
                    answer=result.answer,
                    rewritten_query=result.rewritten_query,
                    response_kind=result.response_kind,
                    warnings=list(result.warnings),
                    stages=_build_turn_stages(result),
                    diagnosis=_build_turn_diagnosis(result),
                )
            )
            session.history = session.history[-20:]
            store.update(session)
            _append_chat_turn_log(
                root_dir,
                answerer=active_answerer,
                session=session,
                query=query,
                result=result,
                context_before=context_before,
                context_after=session.context,
            )
            _write_recent_chat_session_snapshot(
                root_dir,
                session=session,
            )
            self._stream_event(
                {
                    "type": "result",
                    "payload": _build_chat_payload(
                        root_dir=root_dir,
                        answerer=active_answerer,
                        session=session,
                        result=result,
                    ),
                }
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
    answerer: Part3Answerer,
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
    print(f"Part 4 QA UI running at {url}")
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
    "_build_doc_to_book_plan",
    "_capture_doc_to_book_draft",
    "_create_doc_to_book_draft",
    "_load_doc_to_book_book",
    "_load_doc_to_book_capture",
    "_load_doc_to_book_draft",
    "_list_doc_to_book_drafts",
    "_normalize_doc_to_book_draft",
    "_canonical_source_book",
    "_citation_href",
    "_serialize_citation",
    "_internal_viewer_html",
    "_viewer_path_to_local_html",
    "_derive_next_context",
    "serve",
]
