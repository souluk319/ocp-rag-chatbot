from __future__ import annotations

import json
import re
import threading
import uuid
import webbrowser
from urllib.parse import urlparse
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ocp_rag_part1.language_policy import describe_language_policy, load_language_policy_map
from ocp_rag_part1.settings import load_settings
from ocp_rag_part2.models import SessionContext
from ocp_rag_part2.query import is_generic_intro_query
from ocp_rag_part3 import Part3Answerer
from ocp_rag_part3.models import AnswerResult, Citation


STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML_PATH = STATIC_DIR / "index.html"
OPENSHIFT_ENTITY_RE = re.compile(r"(오픈시프트|openshift)", re.IGNORECASE)
MCO_ENTITY_RE = re.compile(r"machine config operator", re.IGNORECASE)
ETCD_ENTITY_RE = re.compile(r"\betcd\b", re.IGNORECASE)
OPERATOR_ENTITY_RE = re.compile(r"\boperator\b", re.IGNORECASE)


@dataclass(slots=True)
class Turn:
    query: str
    mode: str
    answer: str


@dataclass(slots=True)
class ChatSession:
    session_id: str
    mode: str = "ops"
    context: SessionContext = field(
        default_factory=lambda: SessionContext(mode="ops", ocp_version="4.20")
    )
    history: list[Turn] = field(default_factory=list)

    @property
    def last_query(self) -> str:
        if not self.history:
            return ""
        return self.history[-1].query


class SessionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, ChatSession] = {}

    def get(self, session_id: str) -> ChatSession:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = ChatSession(session_id=session_id)
                self._sessions[session_id] = session
            return session

    def reset(self, session_id: str) -> ChatSession:
        with self._lock:
            session = ChatSession(session_id=session_id)
            self._sessions[session_id] = session
            return session

    def update(self, session: ChatSession) -> None:
        with self._lock:
            self._sessions[session.session_id] = session


def _citation_href(citation: Citation) -> str:
    viewer_path = (citation.viewer_path or "").strip()
    if viewer_path:
        return viewer_path
    if citation.anchor:
        return f"{citation.source_url}#{citation.anchor}"
    return citation.source_url


def _viewer_path_to_local_html(root_dir: Path, viewer_path: str) -> Path | None:
    parsed = urlparse((viewer_path or "").strip())
    request_path = parsed.path.strip()
    prefix = "/docs/ocp/4.20/ko/"
    if not request_path.startswith(prefix):
        return None

    remainder = request_path[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) < 2:
        return None

    book_slug = parts[0]
    settings = load_settings(root_dir)
    candidate = settings.viewer_docs_dir / book_slug / "index.html"
    if not candidate.exists():
        return None
    return candidate


def _unique_entities(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = (value or "").strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        ordered.append(normalized)
    return ordered


def _extract_open_entities(query: str, result: AnswerResult) -> list[str]:
    entities: list[str] = []
    normalized_query = query or ""

    if OPENSHIFT_ENTITY_RE.search(normalized_query):
        entities.append("OpenShift Container Platform")
    if MCO_ENTITY_RE.search(normalized_query):
        entities.append("Machine Config Operator")
    if ETCD_ENTITY_RE.search(normalized_query):
        entities.append("etcd")
    if OPERATOR_ENTITY_RE.search(normalized_query) and "Machine Config Operator" not in entities:
        entities.append("Operator")

    if entities:
        return _unique_entities(entities)

    for citation in result.citations:
        if citation.book_slug in {"architecture", "overview"} and is_generic_intro_query(query):
            entities.append("OpenShift Container Platform")
        elif citation.book_slug == "machine_configuration":
            entities.append("Machine Config Operator")
        elif citation.book_slug == "etcd" or ETCD_ENTITY_RE.search(citation.section):
            entities.append("etcd")
        elif citation.book_slug == "operators":
            entities.append("Operator")

    return _unique_entities(entities)


def _derive_next_context(
    previous: SessionContext | None,
    *,
    query: str,
    mode: str,
    result: AnswerResult,
) -> SessionContext:
    next_context = SessionContext.from_dict(previous.to_dict() if previous else None)
    next_context.mode = mode
    next_context.ocp_version = next_context.ocp_version or "4.20"
    extracted_entities = _extract_open_entities(query, result)
    if extracted_entities:
        next_context.open_entities = extracted_entities
        if is_generic_intro_query(query):
            next_context.user_goal = "개념 설명"

    if result.citations:
        primary = result.citations[0]
        next_context.current_topic = primary.section or next_context.current_topic
        next_context.unresolved_question = None
    else:
        next_context.unresolved_question = query
    return next_context


def _citation_payload(
    citation: Citation,
    language_policy_map: dict[str, dict[str, object]],
) -> dict[str, Any]:
    payload = {
        **citation.to_dict(),
        "href": _citation_href(citation),
    }
    policy = language_policy_map.get(citation.book_slug)
    if policy:
        payload["language_policy"] = {
            **{
                "language_status": str(policy.get("language_status", "")),
                "recommended_action": str(policy.get("recommended_action", "")),
                "translation_priority": str(policy.get("translation_priority", "")),
            },
            **describe_language_policy(policy),
        }
    return payload


def _build_chat_payload(
    *,
    session: ChatSession,
    result: AnswerResult,
    language_policy_map: dict[str, dict[str, object]],
) -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "mode": session.mode,
        "answer": result.answer,
        "rewritten_query": result.rewritten_query,
        "warnings": list(result.warnings),
        "cited_indices": list(result.cited_indices),
        "confidence": result.confidence.to_dict() if result.confidence else None,
        "citations": [
            _citation_payload(citation, language_policy_map)
            for citation in result.citations
        ],
        "context": session.context.to_dict(),
        "history_size": len(session.history),
    }


def _build_handler(
    *,
    answerer: Part3Answerer,
    store: SessionStore,
    root_dir: Path,
) -> type[BaseHTTPRequestHandler]:
    settings = load_settings(root_dir)
    language_policy_map = load_language_policy_map(settings)

    class ChatHandler(BaseHTTPRequestHandler):
        server_version = "OCPRAGPart4/0.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return None

        def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path in {"/", "/index.html"}:
                self._send_html(INDEX_HTML_PATH.read_text(encoding="utf-8"))
                return
            if self.path == "/api/health":
                self._send_json({"ok": True})
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
            if self.path == "/api/reset":
                self._handle_reset(payload)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _handle_chat(self, payload: dict[str, Any]) -> None:
            session_id = str(payload.get("session_id") or uuid.uuid4().hex)
            session = store.get(session_id)
            mode = str(payload.get("mode") or session.mode or "ops")
            regenerate = bool(payload.get("regenerate", False))
            query = str(payload.get("query") or "").strip()
            if regenerate and not query:
                query = session.last_query

            if not query:
                self._send_json({"error": "질문을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
                return

            try:
                result = answerer.answer(
                    query,
                    mode=mode,
                    context=session.context,
                    top_k=5,
                    candidate_k=20,
                    max_context_chunks=6,
                )
                answerer.append_log(result)
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    {"error": f"답변 생성 중 오류가 발생했습니다: {exc}"},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
                return

            session.mode = mode
            session.context = _derive_next_context(
                session.context,
                query=query,
                mode=mode,
                result=result,
            )
            session.history.append(Turn(query=query, mode=mode, answer=result.answer))
            session.history = session.history[-20:]
            store.update(session)
            self._send_json(
                _build_chat_payload(
                    session=session,
                    result=result,
                    language_policy_map=language_policy_map,
                )
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
    "_citation_href",
    "_citation_payload",
    "_viewer_path_to_local_html",
    "_derive_next_context",
    "serve",
]
