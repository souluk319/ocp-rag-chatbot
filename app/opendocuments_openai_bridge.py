from __future__ import annotations

import os
import time
from functools import lru_cache
from typing import Any
import json
import re

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from sentence_transformers import SentenceTransformer


COMPANY_BASE_URL = os.getenv("OD_COMPANY_BASE_URL", "http://cllm.cywell.co.kr/v1").rstrip("/")
CHAT_MODEL = os.getenv("OD_CHAT_MODEL", "Qwen/Qwen3.5-9B")
EMBEDDING_MODEL = os.getenv("OD_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
REQUEST_TIMEOUT = float(os.getenv("OD_BRIDGE_TIMEOUT_SECONDS", "120"))
COMPANY_BEARER_TOKEN = os.getenv("OD_COMPANY_BEARER_TOKEN", "").strip()
ALLOW_LOCAL_CHAT_FALLBACK = os.getenv("OD_ALLOW_LOCAL_CHAT_FALLBACK", "1").strip().lower() not in {"0", "false", "no"}

app = FastAPI(title="OpenDocuments Stage6 OpenAI Bridge")


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def proxy_headers(request: Request) -> dict[str, str]:
    headers = {}
    auth = request.headers.get("authorization", "").strip()
    if COMPANY_BEARER_TOKEN:
        token = COMPANY_BEARER_TOKEN
        headers["Authorization"] = token if token.lower().startswith("bearer ") else f"Bearer {token}"
    elif auth:
        headers["Authorization"] = auth
    return headers


def proxy_response_json(method: str, path: str, *, headers: dict[str, str] | None = None, json_body: Any = None) -> Response:
    url = f"{COMPANY_BASE_URL}{path}"
    response = requests.request(method, url, headers=headers, json=json_body, timeout=REQUEST_TIMEOUT)
    return JSONResponse(status_code=response.status_code, content=response.json())


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


def make_fallback_completion(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = extract_prompt_text(payload)
    content = build_local_fallback_answer(prompt)
    token_estimate = max(1, len(content.split()))
    return {
        "id": f"stage6-fallback-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": payload.get("model", CHAT_MODEL),
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


def stream_fallback_completion(payload: dict[str, Any]):
    completion = make_fallback_completion(payload)
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
    return {
        "ok": True,
        "company_base_url": COMPANY_BASE_URL,
        "chat_model": CHAT_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "company_token_configured": bool(COMPANY_BEARER_TOKEN),
        "local_chat_fallback": ALLOW_LOCAL_CHAT_FALLBACK,
    }


@app.get("/v1/models")
def list_models(request: Request) -> Response:
    response = proxy_response_json("GET", "/models", headers=proxy_headers(request))
    if response.status_code in {401, 403} and ALLOW_LOCAL_CHAT_FALLBACK:
        return JSONResponse(
            {
                "object": "list",
                "data": [
                    {
                        "id": CHAT_MODEL,
                        "object": "model",
                        "owned_by": "stage6-local-fallback",
                    }
                ],
            }
        )
    return response


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> Response:
    payload = await request.json()
    url = f"{COMPANY_BASE_URL}/chat/completions"
    headers = proxy_headers(request)
    headers["Content-Type"] = "application/json"

    try:
        if payload.get("stream"):
            upstream = requests.post(url, headers=headers, json=payload, stream=True, timeout=REQUEST_TIMEOUT)
            if upstream.status_code >= 400:
                try:
                    detail = upstream.json()
                except Exception:
                    detail = {"error": upstream.text}
                if upstream.status_code in {401, 403} and ALLOW_LOCAL_CHAT_FALLBACK:
                    upstream.close()
                    return StreamingResponse(stream_fallback_completion(payload), media_type="text/event-stream")
                return JSONResponse(status_code=upstream.status_code, content=detail)

            def event_stream():
                try:
                    for chunk in upstream.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                finally:
                    upstream.close()

            media_type = upstream.headers.get("content-type", "text/event-stream")
            return StreamingResponse(event_stream(), media_type=media_type)

        response = proxy_response_json("POST", "/chat/completions", headers=headers, json_body=payload)
        if response.status_code in {401, 403} and ALLOW_LOCAL_CHAT_FALLBACK:
            return JSONResponse(make_fallback_completion(payload))
        return response
    except requests.RequestException as exc:
        if ALLOW_LOCAL_CHAT_FALLBACK:
            if payload.get("stream"):
                return StreamingResponse(stream_fallback_completion(payload), media_type="text/event-stream")
            return JSONResponse(make_fallback_completion(payload))
        raise HTTPException(status_code=502, detail=f"Company LLM proxy failed: {exc}") from exc


@app.post("/v1/embeddings")
async def embeddings(request: Request) -> Response:
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
    dense_vectors = model.encode(texts, normalize_embeddings=False).tolist()

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
            "model": payload.get("model", EMBEDDING_MODEL),
            "usage": {
                "prompt_tokens": token_estimate,
                "total_tokens": token_estimate,
            },
        }
    )
