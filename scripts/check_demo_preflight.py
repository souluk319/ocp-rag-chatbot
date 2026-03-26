"""Live preflight checks for demo readiness.

This script targets a running API server and verifies the contract that is
most likely to break during a live demo:
- locked submission model
- non-empty index and cache stats
- direct /api/chat response contract
- cache hit on a repeated query
- SSE streaming event delivery
- multi-turn session history growth
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api import app


LOCKED_MODEL = "Qwen/Qwen3.5-9B"
BASE_QUERY = "OpenShift에서 Pod가 Pending일 때 먼저 확인할 항목은 무엇인가요?"
FOLLOW_UP_QUERY = "다음엔?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live preflight checks against the OCP RAG API")
    parser.add_argument(
        "--endpoint",
        default=None,
        help="Base URL of the running API server. Omit this to run against the in-process app.",
    )
    parser.add_argument("--timeout", type=float, default=180.0, help="Per-request timeout in seconds")
    return parser.parse_args()


def require(failures: list[str], name: str, condition: Any, detail: str | None = None) -> None:
    if not condition:
        failures.append(name if detail is None else f"{name}: {detail}")


def _api_url(endpoint: str | None, path: str) -> str:
    return path if endpoint is None else f"{endpoint}{path}"


def _post_chat(client: Any, endpoint: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    resp = client.post(_api_url(endpoint, "/api/chat"), json=payload)
    resp.raise_for_status()
    return resp.json()


def _post_stream(client: Any, endpoint: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    collected: dict[str, Any] = {
        "answer": "",
        "sources": [],
        "rewritten_query": "",
        "session_id": None,
        "cached": False,
        "events": [],
        "token_count": 0,
    }
    current_event: str | None = None
    data_lines: list[str] = []

    def flush_event() -> None:
        nonlocal current_event, data_lines
        if not current_event:
            data_lines = []
            return

        raw = "\n".join(data_lines).strip()
        parsed: Any = raw
        if raw:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = raw

        collected["events"].append(current_event)
        if current_event == "rewrite":
            collected["rewritten_query"] = parsed if isinstance(parsed, str) else str(parsed)
        elif current_event == "sources" and isinstance(parsed, list):
            collected["sources"] = parsed
        elif current_event == "token":
            collected["answer"] += parsed if isinstance(parsed, str) else str(parsed)
            collected["token_count"] += 1
        elif current_event == "cached":
            collected["answer"] = parsed if isinstance(parsed, str) else str(parsed)
            collected["cached"] = True
        elif current_event == "done" and isinstance(parsed, dict):
            collected["session_id"] = parsed.get("session_id", collected["session_id"])
            collected["cached"] = bool(parsed.get("cached", collected["cached"]))

        current_event = None
        data_lines = []

    with client.stream("POST", _api_url(endpoint, "/api/chat/stream"), json=payload) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line is None:
                continue
            if line.startswith("event:"):
                flush_event()
                current_event = line[len("event:"):].strip()
                continue
            if line.startswith("data:"):
                data_lines.append(line[len("data:"):].lstrip())
                continue
            if line == "":
                flush_event()
        flush_event()

    return collected


def check_stats(client: Any, endpoint: str | None, failures: list[str]) -> None:
    resp = client.get(_api_url(endpoint, "/api/stats"))
    require(failures, "stats.status_code", resp.status_code == 200, f"got {resp.status_code}")
    if resp.status_code != 200:
        return

    stats = resp.json()
    require(failures, "stats.submission_mode", bool(stats.get("submission_mode")), "submission mode is off")
    require(
        failures,
        "stats.endpoint_switching",
        not bool(stats.get("endpoint_switching")),
        "endpoint switching should be disabled",
    )
    require(failures, "stats.locked_model", stats.get("locked_model") == LOCKED_MODEL, f"got {stats.get('locked_model')!r}")

    index_stats = stats.get("index", {}) or {}
    require(
        failures,
        "stats.index.total_vectors",
        int(index_stats.get("total_vectors", 0)) > 0,
        f"got {index_stats.get('total_vectors', 0)!r}",
    )
    require(
        failures,
        "stats.index.is_built",
        bool(index_stats.get("is_built")),
        "index is not marked as built",
    )
    require(
        failures,
        "stats.semantic_cache.max_size",
        int((stats.get("semantic_cache", {}) or {}).get("max_size", 0)) > 0,
        "semantic cache is not configured",
    )


def check_json_turn(client: Any, endpoint: str | None, failures: list[str]) -> tuple[str, str]:
    payload = {"query": BASE_QUERY, "mode": "ops", "stream": False}
    first = _post_chat(client, endpoint, payload)

    session_id = first.get("session_id")
    answer = first.get("answer", "")
    sources = first.get("sources", []) or []

    require(failures, "chat.first.session_id", bool(session_id), "missing session id")
    require(failures, "chat.first.answer", bool(str(answer).strip()), "empty answer")
    require(failures, "chat.first.sources", bool(sources), "empty sources")
    require(failures, "chat.first.cached", first.get("cached") is False, f"got {first.get('cached')!r}")
    require(
        failures,
        "chat.first.rewritten_query",
        bool(str(first.get("rewritten_query", "")).strip()),
        "empty rewritten query",
    )

    for idx, source in enumerate(sources[:3], 1):
        require(failures, f"chat.first.source[{idx}].chunk_id", bool(source.get("chunk_id")), "missing chunk_id")
        require(failures, f"chat.first.source[{idx}].source", bool(source.get("source")), "missing source name")

    second = _post_chat(
        client,
        endpoint,
        {
            "query": BASE_QUERY,
            "session_id": session_id,
            "mode": "ops",
            "stream": False,
        },
    )

    require(failures, "chat.cache.cached", second.get("cached") is True, f"got {second.get('cached')!r}")
    require(failures, "chat.cache.session_id", second.get("session_id") == session_id, "session id changed")
    require(failures, "chat.cache.answer", second.get("answer") == answer, "cached answer changed")

    return session_id, answer


def check_stream_turn(client: Any, endpoint: str | None, session_id: str, failures: list[str]) -> None:
    payload = {
        "query": FOLLOW_UP_QUERY,
        "session_id": session_id,
        "mode": "ops",
        "stream": True,
    }
    result = _post_stream(client, endpoint, payload)

    require(failures, "stream.session_id", result.get("session_id") == session_id, "session id changed")
    require(failures, "stream.answer", bool(str(result.get("answer", "")).strip()), "empty streamed answer")
    require(failures, "stream.sources", bool(result.get("sources")), "empty streamed sources")
    require(failures, "stream.token_count", int(result.get("token_count", 0)) > 0, "no token events received")
    require(
        failures,
        "stream.rewrite_changed",
        str(result.get("rewritten_query", "")).strip() != FOLLOW_UP_QUERY,
        "follow-up query was not rewritten",
    )
    require(failures, "stream.cached", result.get("cached") is False, f"got {result.get('cached')!r}")
    require(failures, "stream.trace_event", "trace" in result.get("events", []), "trace event missing")
    require(failures, "stream.rewrite_event", "rewrite" in result.get("events", []), "rewrite event missing")
    require(failures, "stream.sources_event", "sources" in result.get("events", []), "sources event missing")
    require(failures, "stream.done_event", "done" in result.get("events", []), "done event missing")

    stats_resp = client.get(_api_url(endpoint, "/api/stats"))
    require(failures, "stats.after_stream.status_code", stats_resp.status_code == 200, f"got {stats_resp.status_code}")
    if stats_resp.status_code != 200:
        return

    stats = stats_resp.json()
    require(
        failures,
        "stats.after_stream.active_sessions",
        int(stats.get("active_sessions", 0)) >= 1,
        f"got {stats.get('active_sessions', 0)!r}",
    )
    require(
        failures,
        "stats.after_stream.cache_hits",
        int((stats.get("semantic_cache", {}) or {}).get("total_hits", 0)) >= 1,
        f"got {(stats.get('semantic_cache', {}) or {}).get('total_hits', 0)!r}",
    )


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    if args.endpoint:
        endpoint = args.endpoint.rstrip("/")
        try:
            with httpx.Client(timeout=args.timeout) as client:
                check_stats(client, endpoint, failures)
                session_id, _ = check_json_turn(client, endpoint, failures)
                check_stream_turn(client, endpoint, session_id, failures)
        except httpx.HTTPError as exc:
            print(f"Preflight check could not reach the server: {exc}")
            return 1
    else:
        try:
            with TestClient(app) as client:
                check_stats(client, None, failures)
                session_id, _ = check_json_turn(client, None, failures)
                check_stream_turn(client, None, session_id, failures)
        except Exception as exc:
            print(f"In-process preflight check failed to start or run: {exc}")
            return 1

    if failures:
        print("Demo preflight check failed.")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Demo preflight check passed.")
    print(f"- mode: {'remote' if args.endpoint else 'in-process'}")
    if args.endpoint:
        print(f"- endpoint: {endpoint}")
    print(f"- locked model: {LOCKED_MODEL}")
    print("- cache hit: verified")
    print("- SSE stream: verified")
    print("- session history: verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
