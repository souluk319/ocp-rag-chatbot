from __future__ import annotations

import time
from functools import lru_cache
from threading import Lock
from typing import Any
import json
import re

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from sentence_transformers import SentenceTransformer

from app.runtime_config import RuntimeConfig, load_runtime_config

app = FastAPI(title="OpenDocuments Stage8 OpenAI Bridge")

_TELEMETRY_LOCK = Lock()
_BRIDGE_TELEMETRY: dict[str, Any] = {
    "started_at": time.time(),
    "models_requests": 0,
    "embedding_requests": 0,
    "chat_requests": 0,
    "streaming_chat_requests": 0,
    "upstream_chat_success_count": 0,
    "upstream_chat_error_count": 0,
    "fallback_chat_count": 0,
    "last_models_status": None,
    "last_chat_status": None,
    "last_chat_target_path": None,
    "last_embedding_dimensions": None,
    "last_embedding_model": None,
}


def record_telemetry(**updates: Any) -> None:
    with _TELEMETRY_LOCK:
        _BRIDGE_TELEMETRY.update(updates)


def bump_telemetry(counter_name: str, *, amount: int = 1, **updates: Any) -> None:
    with _TELEMETRY_LOCK:
        _BRIDGE_TELEMETRY[counter_name] = int(_BRIDGE_TELEMETRY.get(counter_name, 0)) + amount
        _BRIDGE_TELEMETRY.update(updates)


def telemetry_snapshot() -> dict[str, Any]:
    with _TELEMETRY_LOCK:
        return dict(_BRIDGE_TELEMETRY)


@lru_cache(maxsize=1)
def get_runtime_config() -> RuntimeConfig:
    return load_runtime_config()


def require_runtime_config() -> RuntimeConfig:
    config = get_runtime_config()
    missing = config.missing_required_keys()
    if missing:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Runtime configuration is incomplete for the approved company path.",
                "missing_required_keys": missing,
            },
        )
    return config


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    config = require_runtime_config()
    return SentenceTransformer(config.embedding_model)


def proxy_headers(request: Request, config: RuntimeConfig) -> dict[str, str]:
    headers = {}
    auth = request.headers.get("authorization", "").strip()
    if config.company_bearer_token:
        token = config.company_bearer_token
        headers["Authorization"] = token if token.lower().startswith("bearer ") else f"Bearer {token}"
    elif config.forward_client_auth and auth:
        headers["Authorization"] = auth
    return headers


def proxy_response(method: str, path: str, config: RuntimeConfig, *, headers: dict[str, str] | None = None, json_body: Any = None) -> Response:
    url = f"{config.company_base_url.rstrip('/')}{path}"
    response = requests.request(method, url, headers=headers, json=json_body, timeout=config.request_timeout_seconds)
    content_type = response.headers.get("content-type", "application/json")
    if "application/json" in content_type.lower():
        try:
            return JSONResponse(status_code=response.status_code, content=response.json())
        except ValueError:
            pass
    return Response(status_code=response.status_code, content=response.content, media_type=content_type)


def extract_prompt_text(payload: dict[str, Any]) -> str:
    messages = payload.get("messages")
    if not isinstance(messages, list):
        return ""

    for message in reversed(messages):
        if not isinstance(message, dict):
            continue
        if message.get("role") != "user":
            continue
        content = message.get("content", "")
        if isinstance(content, str):
            return content
    return ""


def clean_excerpt(text: str, *, limit: int = 220) -> str:
    stripped = re.sub(r"\s+", " ", text.replace("\r", " ").replace("\n", " ")).strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3].rstrip() + "..."


def adjust_embedding_dimensions(vector: list[float], *, target_dimensions: int) -> list[float]:
    if target_dimensions <= 0:
        return vector
    current_dimensions = len(vector)
    if current_dimensions == target_dimensions:
        return vector
    if current_dimensions > target_dimensions:
        return vector[:target_dimensions]
    return vector + [0.0] * (target_dimensions - current_dimensions)


def build_local_fallback_answer(prompt: str) -> str:
    question_match = re.search(r"## Question\s+(.*?)\s+## Instructions", prompt, re.DOTALL)
    question = question_match.group(1).strip() if question_match else "질문을 확인할 수 없습니다."
    context_match = re.search(r"## Context\s+(.*?)\s+## Question", prompt, re.DOTALL)
    context_block = context_match.group(1).strip() if context_match else prompt

    source_matches = re.findall(
        r"\[Source: ([^\]]+)\]\s*(.*?)(?=\n\n\[Source: |\n## Question|\Z)",
        context_block,
        re.DOTALL,
    )

    lines = [
        "회사 LLM 인증 토큰이 아직 연결되지 않아 Stage 6 로컬 fallback 생성기를 사용했습니다.",
        f"질문: {question}",
        "",
        "가장 관련된 근거 문서는 아래와 같습니다.",
    ]

    for index, (source_label, source_body) in enumerate(source_matches[:3], start=1):
        lines.append(f"{index}. [Source: {source_label}]")
        lines.append(f"   {clean_excerpt(source_body)}")

    if not source_matches:
        lines.append("1. 관련 문맥을 찾지 못했습니다. source retrieval 결과를 먼저 확인해 주세요.")

    lines.extend(
        [
            "",
            "정확한 절차와 예외사항은 위 출처 문서를 직접 열어 원문 기준으로 확인해 주세요.",
        ]
    )
    return "\n".join(lines)


def make_fallback_completion(payload: dict[str, Any], config: RuntimeConfig) -> dict[str, Any]:
    prompt = extract_prompt_text(payload)
    content = build_local_fallback_answer(prompt)
    token_estimate = max(1, len(content.split()))
    return {
        "id": f"stage6-fallback-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": payload.get("model", config.chat_model),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": token_estimate,
            "completion_tokens": token_estimate,
            "total_tokens": token_estimate * 2,
        },
    }


def stream_fallback_completion(payload: dict[str, Any], config: RuntimeConfig):
    completion = make_fallback_completion(payload, config)
    content = completion["choices"][0]["message"]["content"]
    model = completion["model"]
    chunks = [content[i : i + 120] for i in range(0, len(content), 120)] or [""]

    for index, part in enumerate(chunks):
        chunk_payload = {
            "id": completion["id"],
            "object": "chat.completion.chunk",
            "created": completion["created"],
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": part},
                    "finish_reason": None,
                }
            ],
        }
        if index == len(chunks) - 1:
            chunk_payload["choices"][0]["finish_reason"] = "stop"
        yield f"data: {json.dumps(chunk_payload, ensure_ascii=False)}\n\n"

    yield "data: [DONE]\n\n"


@app.get("/health")
def health() -> dict[str, Any]:
    config = get_runtime_config()
    return {
        "ok": not config.missing_required_keys(),
        **config.to_health_dict(),
    }


@app.get("/evidence")
def evidence() -> dict[str, Any]:
    config = get_runtime_config()
    return {
        "ok": not config.missing_required_keys(),
        "runtime_mode": config.runtime_mode(),
        "embedding_model": config.embedding_model,
        "embedding_dimensions": config.embedding_dimensions,
        "telemetry": telemetry_snapshot(),
    }


@app.get("/ready")
def ready() -> dict[str, Any]:
    config = require_runtime_config()
    model = get_embedder()
    probe_vector = model.encode(["probe"], normalize_embeddings=False).tolist()[0]
    adjusted = adjust_embedding_dimensions(probe_vector, target_dimensions=config.embedding_dimensions)
    return {
        "ok": True,
        "ready": True,
        "embedding_model": config.embedding_model,
        "embedding_dimensions": len(adjusted),
    }


@app.get("/v1/models")
def list_models(request: Request) -> Response:
    config = require_runtime_config()
    bump_telemetry("models_requests")
    response = proxy_response("GET", "/models", config, headers=proxy_headers(request, config))
    record_telemetry(last_models_status=response.status_code)
    if response.status_code in {401, 403} and config.allow_local_chat_fallback:
        return JSONResponse(
            {
                "object": "list",
                "data": [
                    {
                        "id": config.chat_model,
                        "object": "model",
                        "owned_by": "stage8-explicit-local-fallback",
                    }
                ],
            }
        )
    return response


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> Response:
    config = require_runtime_config()
    payload = await request.json()
    url = f"{config.company_base_url.rstrip('/')}/chat/completions"
    headers = proxy_headers(request, config)
    headers["Content-Type"] = "application/json"
    is_stream = bool(payload.get("stream"))
    bump_telemetry(
        "chat_requests",
        streaming_chat_requests=telemetry_snapshot().get("streaming_chat_requests", 0) + (1 if is_stream else 0),
        last_chat_target_path="/chat/completions",
    )

    try:
        if is_stream:
            upstream = requests.post(url, headers=headers, json=payload, stream=True, timeout=config.request_timeout_seconds)
            record_telemetry(last_chat_status=upstream.status_code)
            if upstream.status_code >= 400:
                try:
                    detail = upstream.json()
                except Exception:
                    detail = {"error": upstream.text}
                bump_telemetry("upstream_chat_error_count")
                if upstream.status_code in {401, 403} and config.allow_local_chat_fallback:
                    upstream.close()
                    bump_telemetry("fallback_chat_count")
                    return StreamingResponse(stream_fallback_completion(payload, config), media_type="text/event-stream")
                return JSONResponse(status_code=upstream.status_code, content=detail)
            bump_telemetry("upstream_chat_success_count")

            def event_stream():
                try:
                    for chunk in upstream.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                finally:
                    upstream.close()

            media_type = upstream.headers.get("content-type", "text/event-stream")
            return StreamingResponse(event_stream(), media_type=media_type)

        response = proxy_response("POST", "/chat/completions", config, headers=headers, json_body=payload)
        record_telemetry(last_chat_status=response.status_code)
        if response.status_code in {401, 403} and config.allow_local_chat_fallback:
            bump_telemetry("fallback_chat_count")
            return JSONResponse(make_fallback_completion(payload, config))
        if response.status_code >= 400:
            bump_telemetry("upstream_chat_error_count")
        else:
            bump_telemetry("upstream_chat_success_count")
        return response
    except requests.RequestException as exc:
        if config.allow_local_chat_fallback:
            bump_telemetry("fallback_chat_count")
            if is_stream:
                return StreamingResponse(stream_fallback_completion(payload, config), media_type="text/event-stream")
            return JSONResponse(make_fallback_completion(payload, config))
        raise HTTPException(status_code=502, detail=f"Company LLM proxy failed: {exc}") from exc


@app.post("/v1/embeddings")
async def embeddings(request: Request) -> Response:
    config = require_runtime_config()
    try:
        payload = await request.json()
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc

    raw_input = payload.get("input")
    if raw_input is None:
        raise HTTPException(status_code=400, detail="'input' is required")

    if isinstance(raw_input, str):
        texts = [raw_input]
    elif isinstance(raw_input, list) and all(isinstance(item, str) for item in raw_input):
        texts = raw_input
    else:
        raise HTTPException(status_code=400, detail="'input' must be a string or a list of strings")

    model = get_embedder()
    raw_dense_vectors = model.encode(texts, normalize_embeddings=False).tolist()
    dense_vectors = [
        adjust_embedding_dimensions(vector, target_dimensions=config.embedding_dimensions)
        for vector in raw_dense_vectors
    ]
    bump_telemetry(
        "embedding_requests",
        last_embedding_dimensions=len(dense_vectors[0]) if dense_vectors else 0,
        last_embedding_model=config.embedding_model,
    )

    data = [
        {
            "object": "embedding",
            "index": index,
            "embedding": vector,
        }
        for index, vector in enumerate(dense_vectors)
    ]

    token_estimate = sum(max(1, len(text.split())) for text in texts)

    return JSONResponse(
        {
            "object": "list",
            "data": data,
            "model": payload.get("model", config.embedding_model),
            "usage": {
                "prompt_tokens": token_estimate,
                "total_tokens": token_estimate,
            },
        }
    )
