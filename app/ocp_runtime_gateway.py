from __future__ import annotations

import json
import re
import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse

from app.runtime_config import RuntimeConfig, load_runtime_config
from app.runtime_gateway_support import (
    answer_requires_prefix,
    answer_needs_source_backed_rescue,
    build_answer_prefix,
    build_citation_appendix,
    build_direct_rag_runtime_payload,
    build_done_payload,
    build_manifest_backed_definition_answer,
    build_manifest_backed_reference_answer,
    build_pipeline_trace,
    build_policy_overlay,
    build_source_backed_runtime_answer,
    commit_runtime_grounding,
    load_session_manager,
    pick_manifest_backed_definition_sources,
    pick_manifest_backed_reference_sources,
    prepare_runtime_turn,
    shape_answer,
    should_use_local_runtime_rescue,
)
from app.runtime_cache import TtlLruCache
from app.runtime_source_index import (
    load_active_source_catalog,
    reset_active_source_catalog,
)


SESSION_COOKIE_NAME = "ocp_runtime_session"
KNOWN_UPSTREAM_CONVERSATIONS: set[str] = set()

app = FastAPI(title="OCP Runtime Gateway")
STATIC_DIR = Path(__file__).resolve().parent / "static"


@lru_cache(maxsize=1)
def get_runtime_config() -> RuntimeConfig:
    return load_runtime_config()


@lru_cache(maxsize=1)
def load_query_cache() -> TtlLruCache[dict[str, Any]]:
    config = load_runtime_config()
    return TtlLruCache(
        max_items=config.query_cache_max_items,
        ttl_seconds=config.query_cache_ttl_seconds,
    )


def reset_query_cache() -> None:
    load_query_cache().clear()


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


def conversation_exists(
    config: RuntimeConfig, headers: dict[str, str], conversation_id: str
) -> bool:
    if not conversation_id:
        return False
    if conversation_id in KNOWN_UPSTREAM_CONVERSATIONS:
        return True

    url = f"{config.opendocuments_base_url.rstrip('/')}/api/v1/conversations/{conversation_id}/messages"
    try:
        response = requests.get(
            url, headers=headers, timeout=config.request_timeout_seconds
        )
    except requests.RequestException:
        return False

    if response.status_code == 200:
        KNOWN_UPSTREAM_CONVERSATIONS.add(conversation_id)
        return True
    return False


def create_upstream_conversation(
    config: RuntimeConfig, headers: dict[str, str], *, title: str = ""
) -> str:
    url = f"{config.opendocuments_base_url.rstrip('/')}/api/v1/conversations"
    payload = {"title": title} if title else {}
    try:
        response = requests.post(
            url, headers=headers, json=payload, timeout=config.request_timeout_seconds
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"OpenDocuments conversation bootstrap failed: {exc}",
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="OpenDocuments conversation bootstrap returned invalid JSON.",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "OpenDocuments conversation bootstrap failed.",
                "upstream": payload,
            },
        )

    conversation_id = str(payload.get("id", "")).strip()
    if not conversation_id:
        raise HTTPException(
            status_code=502,
            detail="OpenDocuments conversation bootstrap did not return an id.",
        )

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
    for raw_line in response.iter_lines(decode_unicode=False):
        if raw_line is None:
            continue
        if isinstance(raw_line, bytes):
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r")
        else:
            line = str(raw_line).rstrip("\r")
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


def looks_like_definition_query(query: str) -> bool:
    normalized = re.sub(r"\s+", " ", (query or "")).strip().lower()
    if not normalized:
        return False
    product_terms = ("ocp", "openshift", "open shift", "오픈시프트")
    definition_cues = (
        "뭐야",
        "무엇",
        "정의",
        "소개",
        "개요",
        "란",
        "what is",
        "overview",
        "introduction",
    )
    return any(term in normalized for term in product_terms) and (
        any(cue in normalized for cue in definition_cues)
        or normalized in {"ocp", "openshift", "오픈시프트"}
    )


def build_local_definition_payload(
    *,
    query: str,
    session_id: str,
    mode: str,
    rewritten_query: str,
    turn_trace: dict[str, Any],
) -> dict[str, Any] | None:
    overlay = build_policy_overlay(
        question_ko=query,
        mode=mode,
        sources=[],
        memory_before=turn_trace.get("state_before", {}),
    )
    policy_sources = pick_manifest_backed_definition_sources()
    if not policy_sources:
        return None

    commit_runtime_grounding(
        conversation_id=session_id,
        sources=policy_sources,
        memory_manager=load_session_manager(),
    )
    answer = shape_answer(
        build_manifest_backed_definition_answer(query, policy_sources),
        overlay["answer_contract"],
        policy_sources,
    )
    pipeline_trace = build_pipeline_trace(
        query=query,
        mode=mode,
        route="manifest_definition",
        rewritten_query=rewritten_query,
        turn_trace=turn_trace,
        raw_sources=[],
        policy_sources=policy_sources,
        policy_signals=overlay["policy_signals"],
        local_rescue_topic="definition",
        upstream_used=False,
        answer_contract=overlay["answer_contract"],
    )
    return {
        "queryId": f"local-definition-{session_id}",
        "answer": answer,
        "sources": policy_sources,
        "source_count": len(policy_sources),
        "confidence": {
            "score": 0.72,
            "level": "medium",
            "reason": "manifest-backed definition response",
        },
        "route": "manifest_definition",
        "profile": "precise",
        "conversationId": session_id,
        "mode": mode,
        "rewrittenQuery": rewritten_query,
        "policySignals": overlay["policy_signals"],
        "turnTrace": turn_trace,
        "pipelineTrace": pipeline_trace,
    }


def build_local_reference_payload(
    *,
    query: str,
    session_id: str,
    mode: str,
    rewritten_query: str,
    turn_trace: dict[str, Any],
) -> dict[str, Any] | None:
    overlay = build_policy_overlay(
        question_ko=query,
        mode=mode,
        sources=[],
        memory_before=turn_trace.get("state_before", {}),
    )
    policy_sources = pick_manifest_backed_reference_sources(query)
    if not policy_sources:
        return None

    commit_runtime_grounding(
        conversation_id=session_id,
        sources=policy_sources,
        memory_manager=load_session_manager(),
    )
    answer = shape_answer(
        build_manifest_backed_reference_answer(query, policy_sources),
        overlay["answer_contract"],
        policy_sources,
    )
    pipeline_trace = build_pipeline_trace(
        query=query,
        mode=mode,
        route="manifest_runtime_rescue",
        rewritten_query=rewritten_query,
        turn_trace=turn_trace,
        raw_sources=[],
        policy_sources=policy_sources,
        policy_signals=overlay["policy_signals"],
        local_rescue_topic="reference",
        upstream_used=False,
        answer_contract=overlay["answer_contract"],
    )
    return {
        "queryId": f"local-reference-{session_id}",
        "answer": answer,
        "sources": policy_sources,
        "source_count": len(policy_sources),
        "confidence": {
            "score": 0.68,
            "level": "medium",
            "reason": "manifest-backed runtime rescue",
        },
        "route": "manifest_runtime_rescue",
        "profile": "precise",
        "conversationId": session_id,
        "mode": mode,
        "rewrittenQuery": rewritten_query,
        "policySignals": overlay["policy_signals"],
        "turnTrace": turn_trace,
        "pipelineTrace": pipeline_trace,
        "runtimeRescue": True,
    }


def serialize_sse(event: str, payload: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def health_payload(config: RuntimeConfig) -> dict[str, Any]:
    payload = config.to_health_dict()
    try:
        catalog = load_active_source_catalog()
        payload["active_index_id"] = catalog.index_id
        payload["active_manifest_path"] = str(catalog.manifest_path)
        payload["active_document_count"] = len(catalog.documents)
        payload["query_cache"] = load_query_cache().stats()
    except Exception as exc:  # pragma: no cover - health guard
        payload["active_index_error"] = str(exc)
    return payload


def local_query_cache_key(
    *,
    route_name: str,
    query: str,
    mode: str,
    rewritten_query: str,
    memory_before: dict[str, Any],
) -> str:
    catalog = load_active_source_catalog()
    normalized = {
        "route": route_name,
        "query": query.strip(),
        "mode": mode.strip(),
        "rewritten_query": rewritten_query.strip(),
        "active_index_id": catalog.index_id,
        "memory": {
            "active_topic": str(memory_before.get("active_topic", "")).strip(),
            "source_dir": str(memory_before.get("source_dir", "")).strip(),
            "active_category": str(memory_before.get("active_category", "")).strip(),
            "active_version": str(memory_before.get("active_version", "")).strip(),
            "reference_doc_path": str(
                memory_before.get("reference_doc_path", "")
            ).strip(),
        },
    }
    encoded = json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def restore_cached_local_payload(
    *,
    cached_core: dict[str, Any],
    session_id: str,
    query: str,
    mode: str,
    rewritten_query: str,
    turn_trace: dict[str, Any],
) -> dict[str, Any]:
    route_name = (
        str(cached_core.get("route", "manifest_runtime_rescue")).strip()
        or "manifest_runtime_rescue"
    )
    local_rescue_topic = (
        "definition" if route_name == "manifest_definition" else "reference"
    )
    payload = dict(cached_core)
    payload["queryId"] = f"cached-{route_name}-{session_id}"
    payload["conversationId"] = session_id
    payload["mode"] = mode
    payload["rewrittenQuery"] = rewritten_query
    payload["turnTrace"] = turn_trace
    payload["pipelineTrace"] = build_pipeline_trace(
        query=query,
        mode=mode,
        route=route_name,
        rewritten_query=rewritten_query,
        turn_trace=turn_trace,
        raw_sources=[],
        policy_sources=payload.get("sources", []),
        policy_signals=payload.get("policySignals", {}),
        local_rescue_topic=local_rescue_topic,
        upstream_used=False,
        answer_contract={},
    )
    return payload


def load_cached_local_payload(
    *,
    route_name: str,
    query: str,
    session_id: str,
    mode: str,
    rewritten_query: str,
    turn_trace: dict[str, Any],
    memory_before: dict[str, Any],
) -> dict[str, Any] | None:
    cache_key = local_query_cache_key(
        route_name=route_name,
        query=query,
        mode=mode,
        rewritten_query=rewritten_query,
        memory_before=memory_before,
    )
    cached_core = load_query_cache().get(cache_key)
    if cached_core is None:
        return None
    return restore_cached_local_payload(
        cached_core=cached_core,
        session_id=session_id,
        query=query,
        mode=mode,
        rewritten_query=rewritten_query,
        turn_trace=turn_trace,
    )


def store_cached_local_payload(
    *,
    payload: dict[str, Any],
    route_name: str,
    query: str,
    mode: str,
    rewritten_query: str,
    memory_before: dict[str, Any],
) -> None:
    cache_key = local_query_cache_key(
        route_name=route_name,
        query=query,
        mode=mode,
        rewritten_query=rewritten_query,
        memory_before=memory_before,
    )
    cacheable_core = {
        "answer": payload.get("answer", ""),
        "sources": payload.get("sources", []),
        "source_count": payload.get("source_count", 0),
        "confidence": payload.get("confidence", {}),
        "route": payload.get("route", route_name),
        "profile": payload.get("profile", "precise"),
        "policySignals": payload.get("policySignals", {}),
        "runtimeRescue": payload.get("runtimeRescue", False),
    }
    load_query_cache().set(cache_key, cacheable_core)


def commit_cached_local_payload_grounding(
    *,
    conversation_id: str,
    cached_payload: dict[str, Any],
    memory_manager=None,
) -> dict[str, Any]:
    return commit_runtime_grounding(
        conversation_id=conversation_id,
        sources=cached_payload.get("sources", []),
        memory_manager=memory_manager or load_session_manager(),
    )


@app.get("/health")
def health() -> dict[str, Any]:
    config = get_runtime_config()
    return {
        "ok": not config.missing_gateway_keys(),
        **health_payload(config),
    }


@app.get("/")
def chat_home() -> Response:
    page = STATIC_DIR / "runtime_chat.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="Runtime chat page is missing.")
    return FileResponse(page, media_type="text/html")


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
        raise HTTPException(
            status_code=400, detail=f"Invalid JSON body: {exc}"
        ) from exc

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
    mode = (
        str(body.get("mode") or config.default_chat_mode or "operations").strip()
        or "operations"
    )
    plan = prepare_runtime_turn(
        question_ko=query,
        conversation_id=session_id,
        mode=mode,
        memory_manager=load_session_manager(),
    )
    definition_query = looks_like_definition_query(query)
    definition_follow_up = (
        str(plan.turn_trace.get("turn", {}).get("active_topic", "")).strip()
        == "definition"
        and str(plan.turn_trace.get("turn", {}).get("classification", "")).strip()
        == "follow_up"
    )
    if definition_query or definition_follow_up:
        local_definition_payload = build_local_definition_payload(
            query=query,
            session_id=session_id,
            mode=mode,
            rewritten_query=plan.rewritten_query,
            turn_trace=plan.turn_trace,
        )
        if local_definition_payload:
            response = JSONResponse(local_definition_payload)
            set_session_cookie(response, session_id)
            return response
    direct_payload = build_direct_rag_runtime_payload(
        question_ko=query,
        conversation_id=session_id,
        mode=mode,
        rewritten_query=plan.rewritten_query,
        turn_trace=plan.turn_trace,
        memory_before=plan.memory_before,
    )
    if direct_payload:
        response = JSONResponse(direct_payload)
        set_session_cookie(response, session_id)
        return response
    if should_use_local_runtime_rescue(query):
        cached_local_payload = load_cached_local_payload(
            route_name="manifest_runtime_rescue",
            query=query,
            session_id=session_id,
            mode=mode,
            rewritten_query=plan.rewritten_query,
            turn_trace=plan.turn_trace,
            memory_before=plan.memory_before,
        )
        if cached_local_payload:
            commit_cached_local_payload_grounding(
                conversation_id=session_id,
                cached_payload=cached_local_payload,
                memory_manager=load_session_manager(),
            )
            response = JSONResponse(cached_local_payload)
            set_session_cookie(response, session_id)
            return response
        local_payload = build_local_reference_payload(
            query=query,
            session_id=session_id,
            mode=mode,
            rewritten_query=plan.rewritten_query,
            turn_trace=plan.turn_trace,
        )
        if local_payload:
            store_cached_local_payload(
                payload=local_payload,
                route_name="manifest_runtime_rescue",
                query=query,
                mode=mode,
                rewritten_query=plan.rewritten_query,
                memory_before=plan.memory_before,
            )
            response = JSONResponse(local_payload)
            set_session_cookie(response, session_id)
            return response

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
        raise HTTPException(
            status_code=502, detail=f"OpenDocuments upstream failed: {exc}"
        ) from exc

    try:
        payload = upstream.json()
    except ValueError:
        return Response(
            status_code=upstream.status_code,
            content=upstream.content,
            media_type=upstream.headers.get("content-type"),
        )

    if upstream.status_code >= 400:
        return JSONResponse(status_code=upstream.status_code, content=payload)

    raw_sources = payload.get("sources", [])
    overlay = build_policy_overlay(
        question_ko=query,
        mode=mode,
        sources=raw_sources,
        memory_before=plan.memory_before,
    )
    policy_sources = overlay["policy_sources"]
    if definition_query and not policy_sources:
        policy_sources = pick_manifest_backed_definition_sources()
    matched_rules = set(overlay["policy_signals"].get("matched_rules", []))
    commit_runtime_grounding(
        conversation_id=session_id,
        sources=policy_sources,
        memory_manager=load_session_manager(),
    )

    if (
        not payload.get("sources")
        and policy_sources
        and (definition_query or "definition_intro" in matched_rules)
    ):
        base_answer = build_manifest_backed_definition_answer(query, policy_sources)
    else:
        base_answer = str(payload.get("answer", ""))
        if answer_needs_source_backed_rescue(base_answer, policy_sources):
            base_answer = build_source_backed_runtime_answer(query, policy_sources)

    payload["answer"] = shape_answer(
        base_answer, overlay["answer_contract"], policy_sources
    )
    payload["sources"] = policy_sources
    payload["source_count"] = len(policy_sources)
    payload["conversationId"] = session_id
    payload["mode"] = mode
    payload["rewrittenQuery"] = plan.rewritten_query
    payload["policySignals"] = overlay["policy_signals"]
    payload["turnTrace"] = plan.turn_trace
    payload["route"] = "opendocuments_policy_path"
    payload["pipelineTrace"] = build_pipeline_trace(
        query=query,
        mode=mode,
        route=payload["route"],
        rewritten_query=plan.rewritten_query,
        turn_trace=plan.turn_trace,
        raw_sources=raw_sources if isinstance(raw_sources, list) else [],
        policy_sources=policy_sources,
        policy_signals=overlay["policy_signals"],
        upstream_used=True,
        answer_contract=overlay["answer_contract"],
    )

    response = JSONResponse(payload)
    set_session_cookie(response, session_id)
    return response


@app.post("/api/v1/chat/stream")
async def stream_chat(request: Request) -> Response:
    config = require_gateway_config()
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid JSON body: {exc}"
        ) from exc

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
    mode = (
        str(body.get("mode") or config.default_chat_mode or "operations").strip()
        or "operations"
    )
    plan = prepare_runtime_turn(
        question_ko=query,
        conversation_id=session_id,
        mode=mode,
        memory_manager=load_session_manager(),
    )
    definition_query = looks_like_definition_query(query)
    definition_follow_up = (
        str(plan.turn_trace.get("turn", {}).get("active_topic", "")).strip()
        == "definition"
        and str(plan.turn_trace.get("turn", {}).get("classification", "")).strip()
        == "follow_up"
    )
    if definition_query or definition_follow_up:
        local_definition_payload = build_local_definition_payload(
            query=query,
            session_id=session_id,
            mode=mode,
            rewritten_query=plan.rewritten_query,
            turn_trace=plan.turn_trace,
        )
        if local_definition_payload:

            async def local_definition_stream() -> Iterator[str]:
                yield serialize_sse(
                    "trace", local_definition_payload.get("pipelineTrace", [])
                )
                yield serialize_sse("sources", local_definition_payload["sources"])
                yield serialize_sse("chunk", local_definition_payload["answer"])
                yield serialize_sse(
                    "done",
                    build_done_payload(
                        {
                            "route": local_definition_payload.get(
                                "route", "manifest_definition"
                            ),
                            "pipelineTrace": local_definition_payload.get(
                                "pipelineTrace", []
                            ),
                        },
                        conversation_id=session_id,
                        mode=mode,
                        rewritten_query=plan.rewritten_query,
                    ),
                )

            response = StreamingResponse(
                local_definition_stream(),
                media_type="text/event-stream",
                headers={
                    "Content-Type": "text/event-stream; charset=utf-8",
                    "Cache-Control": "no-cache",
                },
            )
            set_session_cookie(response, session_id)
            return response
    direct_payload = build_direct_rag_runtime_payload(
        question_ko=query,
        conversation_id=session_id,
        mode=mode,
        rewritten_query=plan.rewritten_query,
        turn_trace=plan.turn_trace,
        memory_before=plan.memory_before,
    )
    if direct_payload:

        async def direct_stream() -> Iterator[str]:
            yield serialize_sse("trace", direct_payload.get("pipelineTrace", []))
            yield serialize_sse("sources", direct_payload["sources"])
            yield serialize_sse("chunk", direct_payload["answer"])
            yield serialize_sse(
                "done",
                build_done_payload(
                    {
                        "route": direct_payload.get("route", "direct_rag_policy_path"),
                        "pipelineTrace": direct_payload.get("pipelineTrace", []),
                    },
                    conversation_id=session_id,
                    mode=mode,
                    rewritten_query=plan.rewritten_query,
                ),
            )

        response = StreamingResponse(
            direct_stream(),
            media_type="text/event-stream",
            headers={
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache",
            },
        )
        set_session_cookie(response, session_id)
        return response
    cached_local_payload = load_cached_local_payload(
        route_name="manifest_runtime_rescue",
        query=query,
        session_id=session_id,
        mode=mode,
        rewritten_query=plan.rewritten_query,
        turn_trace=plan.turn_trace,
        memory_before=plan.memory_before,
    )
    if should_use_local_runtime_rescue(query) and cached_local_payload:
        commit_cached_local_payload_grounding(
            conversation_id=session_id,
            cached_payload=cached_local_payload,
            memory_manager=load_session_manager(),
        )

        async def cached_local_reference_stream() -> Iterator[str]:
            yield serialize_sse("trace", cached_local_payload.get("pipelineTrace", []))
            yield serialize_sse("sources", cached_local_payload["sources"])
            yield serialize_sse("chunk", cached_local_payload["answer"])
            yield serialize_sse(
                "done",
                build_done_payload(
                    {
                        "route": cached_local_payload.get(
                            "route", "manifest_runtime_rescue"
                        ),
                        "pipelineTrace": cached_local_payload.get("pipelineTrace", []),
                    },
                    conversation_id=session_id,
                    mode=mode,
                    rewritten_query=plan.rewritten_query,
                ),
            )

        response = StreamingResponse(
            cached_local_reference_stream(),
            media_type="text/event-stream",
            headers={
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache",
            },
        )
        set_session_cookie(response, session_id)
        return response
    if should_use_local_runtime_rescue(query):
        local_payload = build_local_reference_payload(
            query=query,
            session_id=session_id,
            mode=mode,
            rewritten_query=plan.rewritten_query,
            turn_trace=plan.turn_trace,
        )
        if local_payload:
            store_cached_local_payload(
                payload=local_payload,
                route_name="manifest_runtime_rescue",
                query=query,
                mode=mode,
                rewritten_query=plan.rewritten_query,
                memory_before=plan.memory_before,
            )

            async def local_reference_stream() -> Iterator[str]:
                yield serialize_sse("trace", local_payload.get("pipelineTrace", []))
                yield serialize_sse("sources", local_payload["sources"])
                yield serialize_sse("chunk", local_payload["answer"])
                yield serialize_sse(
                    "done",
                    build_done_payload(
                        {
                            "route": local_payload.get(
                                "route", "manifest_runtime_rescue"
                            ),
                            "pipelineTrace": local_payload.get("pipelineTrace", []),
                        },
                        conversation_id=session_id,
                        mode=mode,
                        rewritten_query=plan.rewritten_query,
                    ),
                )

            response = StreamingResponse(
                local_reference_stream(),
                media_type="text/event-stream",
                headers={
                    "Content-Type": "text/event-stream; charset=utf-8",
                    "Cache-Control": "no-cache",
                },
            )
            set_session_cookie(response, session_id)
            return response

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
        raise HTTPException(
            status_code=502, detail=f"OpenDocuments upstream failed: {exc}"
        ) from exc

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
        raw_sources: list[dict[str, Any]] = []
        policy_sources: list[dict[str, Any]] = []
        policy_signals: dict[str, Any] = {}
        answer_contract: dict[str, Any] | None = None
        prefix_emitted = False
        done_payload: dict[str, Any] = {}
        local_definition_override = False
        local_source_override = False
        route_name = "opendocuments_policy_path"
        local_rescue_topic = ""

        try:
            yield serialize_sse(
                "trace",
                build_pipeline_trace(
                    query=query,
                    mode=mode,
                    route=route_name,
                    rewritten_query=plan.rewritten_query,
                    turn_trace=plan.turn_trace,
                    raw_sources=raw_sources,
                    policy_sources=policy_sources,
                    policy_signals=policy_signals,
                    local_rescue_topic=local_rescue_topic,
                    upstream_used=False,
                    answer_contract=answer_contract or {},
                ),
            )
            for event_type, payload in iter_sse_events(upstream):
                if event_type == "sources":
                    raw_sources = payload if isinstance(payload, list) else []
                    overlay = build_policy_overlay(
                        question_ko=query,
                        mode=mode,
                        sources=raw_sources,
                        memory_before=plan.memory_before,
                    )
                    definition_query = looks_like_definition_query(query)
                    policy_sources = overlay["policy_sources"]
                    policy_signals = overlay["policy_signals"]
                    if definition_query and not policy_sources:
                        policy_sources = pick_manifest_backed_definition_sources()
                    answer_contract = overlay["answer_contract"]
                    yield serialize_sse("sources", policy_sources)
                    matched_rules = set(
                        overlay["policy_signals"].get("matched_rules", [])
                    )
                    if (
                        (not raw_sources)
                        and policy_sources
                        and (definition_query or "definition_intro" in matched_rules)
                    ):
                        local_definition_override = True
                        route_name = "manifest_definition"
                        local_rescue_topic = "definition"
                        yield serialize_sse(
                            "trace",
                            build_pipeline_trace(
                                query=query,
                                mode=mode,
                                route=route_name,
                                rewritten_query=plan.rewritten_query,
                                turn_trace=plan.turn_trace,
                                raw_sources=raw_sources,
                                policy_sources=policy_sources,
                                policy_signals=policy_signals,
                                local_rescue_topic=local_rescue_topic,
                                upstream_used=True,
                                answer_contract=overlay["answer_contract"],
                            ),
                        )
                        local_answer = build_manifest_backed_definition_answer(
                            query, policy_sources
                        )
                        if answer_contract and not prefix_emitted:
                            if answer_requires_prefix(full_answer, answer_contract):
                                prefix = build_answer_prefix(answer_contract)
                                if prefix:
                                    full_answer += prefix
                                    yield serialize_sse("chunk", prefix)
                            prefix_emitted = True
                        full_answer += local_answer
                        yield serialize_sse("chunk", local_answer)
                    if not local_definition_override:
                        yield serialize_sse(
                            "trace",
                            build_pipeline_trace(
                                query=query,
                                mode=mode,
                                route=route_name,
                                rewritten_query=plan.rewritten_query,
                                turn_trace=plan.turn_trace,
                                raw_sources=raw_sources,
                                policy_sources=policy_sources,
                                policy_signals=policy_signals,
                                local_rescue_topic=local_rescue_topic,
                                upstream_used=True,
                                answer_contract=overlay["answer_contract"],
                            ),
                        )
                    continue

                if event_type == "chunk":
                    if local_definition_override or local_source_override:
                        continue
                    text = str(payload)
                    if policy_sources and answer_needs_source_backed_rescue(
                        full_answer + text, policy_sources
                    ):
                        local_source_override = True
                        route_name = "source_backed_runtime_rescue"
                        local_rescue_topic = "reference"
                        yield serialize_sse(
                            "trace",
                            build_pipeline_trace(
                                query=query,
                                mode=mode,
                                route=route_name,
                                rewritten_query=plan.rewritten_query,
                                turn_trace=plan.turn_trace,
                                raw_sources=raw_sources,
                                policy_sources=policy_sources,
                                policy_signals=policy_signals,
                                local_rescue_topic=local_rescue_topic,
                                upstream_used=True,
                                answer_contract=answer_contract or {},
                            ),
                        )
                        local_answer = build_source_backed_runtime_answer(
                            query, policy_sources
                        )
                        if answer_contract and not prefix_emitted:
                            if answer_requires_prefix(full_answer, answer_contract):
                                prefix = build_answer_prefix(answer_contract)
                                if prefix:
                                    full_answer += prefix
                                    yield serialize_sse("chunk", prefix)
                            prefix_emitted = True
                        full_answer += local_answer
                        yield serialize_sse("chunk", local_answer)
                        continue
                    if answer_contract and not prefix_emitted:
                        if answer_requires_prefix(full_answer, answer_contract):
                            prefix = build_answer_prefix(answer_contract)
                            if prefix:
                                full_answer += prefix
                                yield serialize_sse("chunk", prefix)
                        prefix_emitted = True
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

            final_trace = build_pipeline_trace(
                query=query,
                mode=mode,
                route=route_name,
                rewritten_query=plan.rewritten_query,
                turn_trace=plan.turn_trace,
                raw_sources=raw_sources,
                policy_sources=policy_sources,
                policy_signals=policy_signals,
                local_rescue_topic=local_rescue_topic,
                upstream_used=True,
                answer_contract=answer_contract or {},
            )
            yield serialize_sse("trace", final_trace)
            yield serialize_sse(
                "done",
                build_done_payload(
                    {
                        **done_payload,
                        "route": route_name,
                        "pipelineTrace": final_trace,
                    },
                    conversation_id=session_id,
                    mode=mode,
                    rewritten_query=plan.rewritten_query,
                ),
            )
        finally:
            upstream.close()

    response = StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache",
        },
    )
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
        raise HTTPException(
            status_code=502, detail=f"OpenDocuments upstream failed: {exc}"
        ) from exc

    content_type = upstream.headers.get("content-type", "application/json")
    if "application/json" in content_type.lower():
        try:
            return JSONResponse(
                status_code=upstream.status_code, content=upstream.json()
            )
        except ValueError:
            pass
    return Response(
        status_code=upstream.status_code,
        content=upstream.content,
        media_type=content_type,
    )
