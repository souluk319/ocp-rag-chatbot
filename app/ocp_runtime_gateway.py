from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse

from app.runtime_config import RuntimeConfig, load_runtime_config
from app.runtime_gateway_support import (
    answer_requires_prefix,
    build_answer_prefix,
    build_citation_appendix,
    build_done_payload,
    build_policy_overlay,
    commit_runtime_grounding,
    load_session_manager,
    prepare_runtime_turn,
    shape_answer,
)
from app.runtime_source_index import load_active_source_catalog, reset_active_source_catalog


SESSION_COOKIE_NAME = "ocp_runtime_session"
KNOWN_UPSTREAM_CONVERSATIONS: set[str] = set()

app = FastAPI(title="OCP Runtime Gateway")


@lru_cache(maxsize=1)
def get_runtime_config() -> RuntimeConfig:
    return load_runtime_config()


def require_gateway_config() -> RuntimeConfig:
    config = get_runtime_config()
    missing = config.missing_gateway_keys()
    if missing:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Runtime gateway configuration is incomplete.",
                "missing_required_keys": missing,
            },
        )
    return config


def conversation_exists(config: RuntimeConfig, headers: dict[str, str], conversation_id: str) -> bool:
    if not conversation_id:
        return False
    if conversation_id in KNOWN_UPSTREAM_CONVERSATIONS:
        return True

    url = f"{config.opendocuments_base_url.rstrip('/')}/api/v1/conversations/{conversation_id}/messages"
    try:
        response = requests.get(url, headers=headers, timeout=config.request_timeout_seconds)
    except requests.RequestException:
        return False

    if response.status_code == 200:
        KNOWN_UPSTREAM_CONVERSATIONS.add(conversation_id)
        return True
    return False


def create_upstream_conversation(config: RuntimeConfig, headers: dict[str, str], *, title: str = "") -> str:
    url = f"{config.opendocuments_base_url.rstrip('/')}/api/v1/conversations"
    payload = {"title": title} if title else {}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=config.request_timeout_seconds)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"OpenDocuments conversation bootstrap failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="OpenDocuments conversation bootstrap returned invalid JSON.") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail={"message": "OpenDocuments conversation bootstrap failed.", "upstream": payload})

    conversation_id = str(payload.get("id", "")).strip()
    if not conversation_id:
        raise HTTPException(status_code=502, detail="OpenDocuments conversation bootstrap did not return an id.")

    KNOWN_UPSTREAM_CONVERSATIONS.add(conversation_id)
    return conversation_id


def ensure_session_id(
    request: Request,
    config: RuntimeConfig,
    headers: dict[str, str],
    *,
    explicit_conversation_id: str | None,
    query: str,
) -> str:
    explicit = (explicit_conversation_id or "").strip()
    if explicit:
        if conversation_exists(config, headers, explicit):
            return explicit
        title = query.strip()[:80]
        return create_upstream_conversation(config, headers, title=title)

    cookie_value = (request.cookies.get(SESSION_COOKIE_NAME, "") or "").strip()
    if cookie_value and conversation_exists(config, headers, cookie_value):
        return cookie_value

    title = query.strip()[:80]
    return create_upstream_conversation(config, headers, title=title)


def upstream_headers(request: Request, config: RuntimeConfig) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    auth = request.headers.get("authorization", "").strip()
    if auth and config.forward_client_auth:
        headers["Authorization"] = auth
    return headers


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_id,
        max_age=60 * 60 * 12,
        httponly=True,
        samesite="lax",
    )


def resolve_viewer_html(request_path: str) -> Path:
    document = load_active_source_catalog().resolve_viewer_document(request_path)
    html_path = str(document.get("html_path", "")).strip()
    if not html_path:
        raise HTTPException(status_code=404, detail="Viewer document not found.")

    candidate = Path(html_path)
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Viewer HTML is missing on disk.")
    return candidate


def iter_sse_events(response: requests.Response) -> Iterator[tuple[str, Any]]:
    def decode_payload(event_name: str, payload_text: str) -> Any:
        try:
            return json.loads(payload_text)
        except json.JSONDecodeError:
            normalized = payload_text.replace("\n", "\\n")
            try:
                return json.loads(normalized)
            except json.JSONDecodeError:
                if event_name == "chunk":
                    return payload_text.strip('"')
                return payload_text

    event_type = ""
    data_lines: list[str] = []
    for raw_line in response.iter_lines(decode_unicode=True):
        if raw_line is None:
            continue
        line = raw_line.rstrip("\r")
        if not line:
            if data_lines:
                payload = "\n".join(data_lines)
                current_event = event_type or "message"
                yield current_event, decode_payload(current_event, payload)
            event_type = ""
            data_lines = []
            continue

        if line.startswith("event:"):
            event_type = line.split(":", 1)[1].strip()
            continue

        if line.startswith("data:"):
            data_lines.append(line.split(":", 1)[1].strip())

    if data_lines:
        payload = "\n".join(data_lines)
        current_event = event_type or "message"
        yield current_event, decode_payload(current_event, payload)


def serialize_sse(event: str, payload: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def health_payload(config: RuntimeConfig) -> dict[str, Any]:
    payload = config.to_health_dict()
    try:
        catalog = load_active_source_catalog()
        payload["active_index_id"] = catalog.index_id
        payload["active_manifest_path"] = str(catalog.manifest_path)
        payload["active_document_count"] = len(catalog.documents)
    except Exception as exc:  # pragma: no cover - health guard
        payload["active_index_error"] = str(exc)
    return payload


@app.get("/health")
def health() -> dict[str, Any]:
    config = get_runtime_config()
    return {
        "ok": not config.missing_gateway_keys(),
        **health_payload(config),
    }


@app.get("/viewer/{source_id}/{document_path:path}")
def viewer_document(source_id: str, document_path: str) -> Response:
    request_path = f"/viewer/{source_id}/{document_path}"
    html_path = resolve_viewer_html(request_path)
    return FileResponse(html_path, media_type="text/html")


@app.post("/api/v1/chat")
async def chat(request: Request) -> Response:
    config = require_gateway_config()
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc

    query = str(body.get("query", "")).strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    reset_active_source_catalog()
    headers = upstream_headers(request, config)
    session_id = ensure_session_id(
        request,
        config,
        headers,
        explicit_conversation_id=body.get("conversationId"),
        query=query,
    )
    mode = str(body.get("mode") or config.default_chat_mode or "operations").strip() or "operations"
    plan = prepare_runtime_turn(
        question_ko=query,
        conversation_id=session_id,
        mode=mode,
        memory_manager=load_session_manager(),
    )

    upstream_body = {
        "query": plan.rewritten_query,
        "profile": body.get("profile"),
        "conversationId": session_id,
    }
    upstream_url = f"{config.opendocuments_base_url.rstrip('/')}/api/v1/chat"

    try:
        upstream = requests.post(
            upstream_url,
            headers=headers,
            json=upstream_body,
            timeout=config.request_timeout_seconds,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"OpenDocuments upstream failed: {exc}") from exc

    try:
        payload = upstream.json()
    except ValueError:
        return Response(status_code=upstream.status_code, content=upstream.content, media_type=upstream.headers.get("content-type"))

    if upstream.status_code >= 400:
        return JSONResponse(status_code=upstream.status_code, content=payload)

    overlay = build_policy_overlay(
        question_ko=query,
        mode=mode,
        sources=payload.get("sources", []),
        memory_before=plan.memory_before,
    )
    policy_sources = overlay["policy_sources"]
    commit_runtime_grounding(
        conversation_id=session_id,
        sources=policy_sources,
        memory_manager=load_session_manager(),
    )

    payload["answer"] = shape_answer(str(payload.get("answer", "")), overlay["answer_contract"], policy_sources)
    payload["sources"] = policy_sources
    payload["conversationId"] = session_id
    payload["mode"] = mode
    payload["rewrittenQuery"] = plan.rewritten_query
    payload["policySignals"] = overlay["policy_signals"]
    payload["turnTrace"] = plan.turn_trace

    response = JSONResponse(payload)
    set_session_cookie(response, session_id)
    return response


@app.post("/api/v1/chat/stream")
async def stream_chat(request: Request) -> Response:
    config = require_gateway_config()
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc

    query = str(body.get("query", "")).strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    reset_active_source_catalog()
    headers = upstream_headers(request, config)
    session_id = ensure_session_id(
        request,
        config,
        headers,
        explicit_conversation_id=body.get("conversationId"),
        query=query,
    )
    mode = str(body.get("mode") or config.default_chat_mode or "operations").strip() or "operations"
    plan = prepare_runtime_turn(
        question_ko=query,
        conversation_id=session_id,
        mode=mode,
        memory_manager=load_session_manager(),
    )

    upstream_body = {
        "query": plan.rewritten_query,
        "profile": body.get("profile"),
        "conversationId": session_id,
    }
    upstream_url = f"{config.opendocuments_base_url.rstrip('/')}/api/v1/chat/stream"

    try:
        upstream = requests.post(
            upstream_url,
            headers=headers,
            json=upstream_body,
            timeout=config.request_timeout_seconds,
            stream=True,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"OpenDocuments upstream failed: {exc}") from exc

    if upstream.status_code >= 400:
        try:
            detail = upstream.json()
        except Exception:
            detail = {"error": upstream.text}
        finally:
            upstream.close()
        return JSONResponse(status_code=upstream.status_code, content=detail)

    def event_stream() -> Iterator[str]:
        full_answer = ""
        policy_sources: list[dict[str, Any]] = []
        answer_contract: dict[str, Any] | None = None
        prefix_emitted = False
        done_payload: dict[str, Any] = {}

        try:
            for event_type, payload in iter_sse_events(upstream):
                if event_type == "sources":
                    overlay = build_policy_overlay(
                        question_ko=query,
                        mode=mode,
                        sources=payload if isinstance(payload, list) else [],
                        memory_before=plan.memory_before,
                    )
                    policy_sources = overlay["policy_sources"]
                    answer_contract = overlay["answer_contract"]
                    yield serialize_sse("sources", policy_sources)
                    continue

                if event_type == "chunk":
                    if answer_contract and not prefix_emitted:
                        if answer_requires_prefix(full_answer, answer_contract):
                            prefix = build_answer_prefix(answer_contract)
                            if prefix:
                                full_answer += prefix
                                yield serialize_sse("chunk", prefix)
                        prefix_emitted = True
                    text = str(payload)
                    full_answer += text
                    yield serialize_sse("chunk", text)
                    continue

                if event_type == "done":
                    done_payload = payload if isinstance(payload, dict) else {}
                    continue

                yield serialize_sse(event_type, payload)

            if policy_sources and "[Source:" not in full_answer:
                appendix = "\n\n" + build_citation_appendix(policy_sources)
                full_answer += appendix
                yield serialize_sse("chunk", appendix)

            if policy_sources:
                commit_runtime_grounding(
                    conversation_id=session_id,
                    sources=policy_sources,
                    memory_manager=load_session_manager(),
                )

            yield serialize_sse(
                "done",
                build_done_payload(done_payload, conversation_id=session_id, mode=mode, rewritten_query=plan.rewritten_query),
            )
        finally:
            upstream.close()

    response = StreamingResponse(event_stream(), media_type="text/event-stream")
    set_session_cookie(response, session_id)
    return response


@app.post("/api/v1/chat/feedback")
async def chat_feedback(request: Request) -> Response:
    config = require_gateway_config()
    body = await request.body()
    upstream_url = f"{config.opendocuments_base_url.rstrip('/')}/api/v1/chat/feedback"

    try:
        upstream = requests.post(
            upstream_url,
            headers=upstream_headers(request, config),
            data=body,
            timeout=config.request_timeout_seconds,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"OpenDocuments upstream failed: {exc}") from exc

    content_type = upstream.headers.get("content-type", "application/json")
    if "application/json" in content_type.lower():
        try:
            return JSONResponse(status_code=upstream.status_code, content=upstream.json())
        except ValueError:
            pass
    return Response(status_code=upstream.status_code, content=upstream.content, media_type=content_type)
