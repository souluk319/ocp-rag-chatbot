"""Fast contract checks for submission-safe behavior.

This script does not require the external LLM endpoint. It verifies that the
app stays locked to the grading model and that endpoint switching remains
disabled in submission mode.
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api import app


LOCKED_MODEL = "Qwen/Qwen3.5-9B"


def expect(name: str, actual, expected, failures: list[str]) -> None:
    if actual != expected:
        failures.append(f"{name}: expected {expected!r}, got {actual!r}")


def expect_true(name: str, value, failures: list[str]) -> None:
    if not value:
        failures.append(f"{name}: expected truthy value, got {value!r}")


def expect_false(name: str, value, failures: list[str]) -> None:
    if value:
        failures.append(f"{name}: expected falsy value, got {value!r}")


def main() -> int:
    failures: list[str] = []

    with TestClient(app) as client:
        stats_resp = client.get("/api/stats")
        endpoints_resp = client.get("/api/llm/endpoints")
        health_resp = client.get("/api/llm/health")
        switch_resp = client.post("/api/llm/endpoint", json={"key": "macmini"})
        sessions_resp = client.get("/api/sessions")
        history_resp = client.get("/api/session/demo/history")
        cache_clear_resp = client.post("/api/cache/clear")

    expect("stats.status_code", stats_resp.status_code, 200, failures)
    expect("endpoints.status_code", endpoints_resp.status_code, 200, failures)
    expect("health.status_code", health_resp.status_code, 200, failures)
    expect("switch.status_code", switch_resp.status_code, 403, failures)
    expect("sessions.status_code", sessions_resp.status_code, 403, failures)
    expect("history.status_code", history_resp.status_code, 403, failures)
    expect("cache_clear.status_code", cache_clear_resp.status_code, 403, failures)

    stats = stats_resp.json()
    endpoints = endpoints_resp.json()
    health = health_resp.json()

    expect_true("stats.submission_mode", stats.get("submission_mode"), failures)
    expect_false("stats.endpoint_switching", stats.get("endpoint_switching"), failures)
    expect("stats.locked_model", stats.get("locked_model"), LOCKED_MODEL, failures)

    expect_true("endpoints.submission_mode", endpoints.get("submission_mode"), failures)
    expect_false("endpoints.allow_endpoint_switch", endpoints.get("allow_endpoint_switch"), failures)
    expect_false("endpoints.show_endpoint_selector", endpoints.get("show_endpoint_selector"), failures)
    expect("endpoints.locked_model", endpoints.get("locked_model"), LOCKED_MODEL, failures)
    expect("endpoints.count", len(endpoints.get("endpoints", [])), 1, failures)

    visible = endpoints.get("endpoints", [{}])[0]
    expect("visible.model", visible.get("model"), LOCKED_MODEL, failures)
    expect_true("visible.active", visible.get("active"), failures)

    expect("health.model", health.get("model"), LOCKED_MODEL, failures)
    expect_true("health.submission_mode", health.get("submission_mode"), failures)
    expect_false("health.endpoint_switching", health.get("endpoint_switching"), failures)

    detail = switch_resp.json().get("detail", "")
    if "disabled" not in str(detail).lower():
        failures.append(f"switch.detail: expected a disabled message, got {detail!r}")

    if failures:
        print("Submission contract check failed.")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Submission contract check passed.")
    print(f"- locked model: {LOCKED_MODEL}")
    print("- endpoint switching: disabled")
    print("- visible endpoints: 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
