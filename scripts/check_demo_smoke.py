"""Live smoke checks for demo readiness.

This script targets a running API server and verifies:
- multi-turn session continuity
- query rewrite behavior on follow-up questions
- streaming event delivery
- basic answer/source generation for ops and learn modes
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any

import httpx


DEFAULT_ENDPOINT = "http://127.0.0.1:8000"


OPS_TURNS = [
    "새로 배포한 앱의 파드 상태가 Pending이야",
    "어디부터 봐야 해?",
    "그다음엔 노드 쪽에서 뭐 봐야 해?",
    "그럼 drain이랑 cordon이랑 차이는 뭐야?",
    "마지막으로 현장에서 바로 확인할 명령만 짧게 정리해줘",
]

LEARN_QUERY = "OpenShift Route와 Ingress 차이가 뭐야?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the OCP RAG demo")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Base URL of the running API server")
    parser.add_argument(
        "--transport",
        choices=("api", "stream", "both"),
        default="both",
        help="Which response transport to exercise for the ops flow",
    )
    parser.add_argument("--timeout", type=float, default=180.0, help="Per request timeout in seconds")
    return parser.parse_args()


def post_json(client: httpx.Client, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    resp = client.post(f"{endpoint}/api/chat", json=payload)
    resp.raise_for_status()
    return resp.json()


def post_stream(client: httpx.Client, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    collected: dict[str, Any] = {
        "answer": "",
        "sources": [],
        "rewritten_query": "",
        "session_id": None,
        "cached": False,
    }
    current_event: str | None = None
    data_lines: list[str] = []

    def flush_event() -> None:
        nonlocal current_event, data_lines, collected
        if not current_event or not data_lines:
            current_event = None
            data_lines = []
            return

        raw = "\n".join(data_lines)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw

        if current_event == "rewrite":
            collected["rewritten_query"] = parsed if isinstance(parsed, str) else str(parsed)
        elif current_event == "sources" and isinstance(parsed, list):
            collected["sources"] = parsed
        elif current_event == "token":
            collected["answer"] += parsed if isinstance(parsed, str) else str(parsed)
        elif current_event == "cached":
            collected["answer"] = parsed if isinstance(parsed, str) else str(parsed)
            collected["cached"] = True
        elif current_event == "done" and isinstance(parsed, dict):
            collected["session_id"] = parsed.get("session_id", collected["session_id"])
            collected["cached"] = bool(parsed.get("cached", collected["cached"]))
        data_lines = []
        current_event = None

    with client.stream("POST", f"{endpoint}/api/chat/stream", json=payload) as resp:
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


def check_ops_flow(client: httpx.Client, endpoint: str, transport: str, failures: list[str]) -> None:
    session_id = None
    for idx, query in enumerate(OPS_TURNS, 1):
        payload = {"query": query, "mode": "ops", "stream": transport == "stream"}
        if session_id:
            payload["session_id"] = session_id

        if transport == "stream":
            result = post_stream(client, endpoint, payload)
        else:
            result = post_json(client, endpoint, payload)

        session_id = result.get("session_id", session_id)
        answer = result.get("answer", "")
        sources = result.get("sources", []) or []
        rewritten = result.get("rewritten_query", "")

        if not session_id:
            failures.append(f"ops.turn{idx}: missing session_id")
        if not answer.strip():
            failures.append(f"ops.turn{idx}: empty answer")
        if not sources:
            failures.append(f"ops.turn{idx}: empty sources")

        if idx == 2 and rewritten == query:
            failures.append("ops.turn2: follow-up rewrite did not change the query")
        if idx == 2 and not any(token in rewritten for token in ("Pending", "파드", "진단")):
            failures.append("ops.turn2: rewrite does not reflect the pending-diagnosis context")
        if idx == 5 and not any(token in rewritten for token in ("Pending", "파드", "명령")):
            failures.append("ops.turn5: rewrite does not reflect the pending-diagnosis context")


def check_learn_flow(client: httpx.Client, endpoint: str, failures: list[str]) -> None:
    result = post_json(client, endpoint, {"query": LEARN_QUERY, "mode": "learn", "stream": False})
    answer = result.get("answer", "")
    sources = result.get("sources", []) or []
    if not answer.strip():
        failures.append("learn.flow: empty answer")
    if not sources:
        failures.append("learn.flow: empty sources")
    if not any(token in answer for token in ("Route", "Ingress", "라우트", "인그레스")):
        failures.append("learn.flow: answer does not mention Route/Ingress")


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    try:
        with httpx.Client(timeout=args.timeout) as client:
            stats = client.get(f"{args.endpoint}/api/stats")
            stats.raise_for_status()
            if not stats.json().get("locked_model") == "Qwen/Qwen3.5-9B":
                failures.append("stats.locked_model: unexpected model")

            if args.transport in ("api", "both"):
                check_ops_flow(client, args.endpoint, "api", failures)
            if args.transport in ("stream", "both"):
                check_ops_flow(client, args.endpoint, "stream", failures)

            check_learn_flow(client, args.endpoint, failures)
    except httpx.HTTPError as exc:
        print(f"Smoke test failed to reach the server: {exc}")
        return 1

    if failures:
        print("Demo smoke test failed.")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Demo smoke test passed.")
    print(f"- endpoint: {args.endpoint}")
    print(f"- transport: {args.transport}")
    print("- ops flow: 5-turn session continuity verified")
    print("- learn flow: Route vs Ingress verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
