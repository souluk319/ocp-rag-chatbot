"""Replay evaluation fixtures against the live OCP RAG API and emit a report.

Usage:
  py -3 scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --output data/eval/report.json
  py -3 scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --transport stream --format both
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import httpx


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURE = ROOT / "scripts" / "eval-fixture.seed.json"
DEFAULT_OUTPUT_JSON = ROOT / "data" / "eval_report.json"
DEFAULT_OUTPUT_MD = ROOT / "data" / "eval_report.md"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def contains_any(text: str, candidates: Iterable[str]) -> bool:
    haystack = text.casefold()
    return any(candidate and candidate.casefold() in haystack for candidate in candidates)


def contains_all(text: str, candidates: Iterable[str]) -> bool:
    haystack = text.casefold()
    return all(candidate and candidate.casefold() in haystack for candidate in candidates)


def has_step_list(answer: str) -> bool:
    return bool(re.search(r"(?m)^\s*(?:\d+[\).\:]|[-*])\s+\S", answer))


def has_command_example(answer: str) -> bool:
    return bool(re.search(r"(?is)\b(?:oc|kubectl)\s+[a-z0-9][^\n`]*", answer))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay OCP RAG evaluation fixtures against the API")
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE), help="Path to the fixture JSON file")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000", help="Base API URL")
    parser.add_argument(
        "--transport",
        choices=("api", "stream"),
        default="api",
        help="Use the JSON response endpoint or the SSE streaming endpoint",
    )
    parser.add_argument(
        "--format",
        choices=("json", "md", "both"),
        default="both",
        help="Output format for the report",
    )
    parser.add_argument("--output", default=None, help="Output path. For --format both, JSON is written to this path and MD uses the same stem.")
    parser.add_argument("--timeout", type=float, default=180.0, help="Per request timeout in seconds")
    parser.add_argument("--limit", type=int, default=None, help="Only evaluate the first N fixtures")
    parser.add_argument("--dry-run", action="store_true", help="Print fixture ids and queries without calling the API")
    return parser.parse_args()


def load_fixtures(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_session_turns(conversation: list[dict[str, str]]) -> list[str]:
    return [turn["content"] for turn in conversation if turn.get("role") == "user"]


def api_mode_from_fixture(mode_hint: str) -> str:
    return "learn" if mode_hint == "education" else "ops"


@dataclass
class TurnResult:
    fixture_id: str
    mode_hint: str
    query_class: str
    language: str
    replayed_user_turns: int
    session_id: str | None
    original_query: str
    rewritten_query: str
    answer: str
    sources: list[dict[str, Any]]
    transport: str
    duration_ms: int
    checks: dict[str, Any]
    passed: bool


def evaluate_checks(fixture: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expected = fixture["expected"]
    answer = result.get("answer", "")
    rewritten = result.get("rewritten_query", "")
    sources = result.get("sources", []) or []
    top_sources = [s.get("source", "") for s in sources[:3] if s.get("source")]
    source_names = [s.get("source", "") for s in sources if s.get("source")]
    source_set = {s for s in source_names if s}

    rewrite_expected = expected.get("rewrite", {})
    rewrite_checks: dict[str, Any] = {"passed": True, "details": []}
    if "should_change" in rewrite_expected:
        changed = normalize_text(rewritten) != normalize_text(result.get("original_query", ""))
        ok = changed == bool(rewrite_expected["should_change"])
        rewrite_checks["passed"] &= ok
        rewrite_checks["details"].append({"check": "should_change", "passed": ok, "expected": rewrite_expected["should_change"], "actual": changed})
    if "must_equal" in rewrite_expected:
        ok = normalize_text(rewritten) == normalize_text(rewrite_expected["must_equal"])
        rewrite_checks["passed"] &= ok
        rewrite_checks["details"].append({"check": "must_equal", "passed": ok, "expected": rewrite_expected["must_equal"], "actual": rewritten})
    if "must_include_any" in rewrite_expected:
        ok = contains_any(rewritten, rewrite_expected["must_include_any"])
        rewrite_checks["passed"] &= ok
        rewrite_checks["details"].append({"check": "must_include_any", "passed": ok, "expected": rewrite_expected["must_include_any"]})
    if "must_not_include_any" in rewrite_expected:
        ok = not contains_any(rewritten, rewrite_expected["must_not_include_any"])
        rewrite_checks["passed"] &= ok
        rewrite_checks["details"].append({"check": "must_not_include_any", "passed": ok, "expected": rewrite_expected["must_not_include_any"]})

    retrieval_expected = expected["retrieval"]
    retrieval_checks: dict[str, Any] = {"passed": True, "details": []}
    if "source_any" in retrieval_expected:
        ok = any(source in source_set for source in retrieval_expected["source_any"])
        retrieval_checks["passed"] &= ok
        retrieval_checks["details"].append({"check": "source_any", "passed": ok, "expected": retrieval_expected["source_any"], "top_sources": top_sources})
    if "source_prefer_top3" in retrieval_expected:
        ok = any(source in top_sources for source in retrieval_expected["source_prefer_top3"])
        retrieval_checks["passed"] &= ok
        retrieval_checks["details"].append({"check": "source_prefer_top3", "passed": ok, "expected": retrieval_expected["source_prefer_top3"], "top_sources": top_sources})
    if "source_exclude_top3" in retrieval_expected:
        ok = not any(source in top_sources for source in retrieval_expected["source_exclude_top3"])
        retrieval_checks["passed"] &= ok
        retrieval_checks["details"].append({"check": "source_exclude_top3", "passed": ok, "expected": retrieval_expected["source_exclude_top3"], "top_sources": top_sources})
    if "min_distinct_sources" in retrieval_expected:
        ok = len(source_set) >= int(retrieval_expected["min_distinct_sources"])
        retrieval_checks["passed"] &= ok
        retrieval_checks["details"].append({"check": "min_distinct_sources", "passed": ok, "expected": retrieval_expected["min_distinct_sources"], "actual": len(source_set)})

    answer_expected = expected["answer"]
    answer_checks: dict[str, Any] = {"passed": True, "details": []}
    ok = contains_any(answer, answer_expected.get("must_include_any", []))
    answer_checks["passed"] &= ok
    answer_checks["details"].append({"check": "must_include_any", "passed": ok, "expected": answer_expected.get("must_include_any", [])})

    if answer_expected.get("should_include_any"):
        ok = contains_any(answer, answer_expected["should_include_any"])
        answer_checks["passed"] &= ok
        answer_checks["details"].append({"check": "should_include_any", "passed": ok, "expected": answer_expected["should_include_any"]})

    if answer_expected.get("must_not_include_any"):
        ok = not contains_any(answer, answer_expected["must_not_include_any"])
        answer_checks["passed"] &= ok
        answer_checks["details"].append({"check": "must_not_include_any", "passed": ok, "expected": answer_expected["must_not_include_any"]})

    if answer_expected.get("citation_required"):
        ok = len(sources) > 0
        answer_checks["passed"] &= ok
        answer_checks["details"].append({"check": "citation_required", "passed": ok, "actual_source_count": len(sources)})

    if answer_expected.get("requires_step_list"):
        ok = has_step_list(answer)
        answer_checks["passed"] &= ok
        answer_checks["details"].append({"check": "requires_step_list", "passed": ok})

    if answer_expected.get("requires_command_example"):
        ok = has_command_example(answer)
        answer_checks["passed"] &= ok
        answer_checks["details"].append({"check": "requires_command_example", "passed": ok})

    overall = bool(rewrite_checks["passed"] and retrieval_checks["passed"] and answer_checks["passed"])
    return {
        "rewrite": rewrite_checks,
        "retrieval": retrieval_checks,
        "answer": answer_checks,
        "overall": overall,
    }


def replay_fixture(client: httpx.Client, base_url: str, transport: str, fixture: dict[str, Any]) -> TurnResult:
    conversation = fixture["conversation"]
    user_turns = build_session_turns(conversation)
    session_id: str | None = None
    last_response: dict[str, Any] | None = None
    original_query = user_turns[-1]

    def post_json(payload: dict[str, Any]) -> dict[str, Any]:
        resp = client.post(f"{base_url}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()

    def post_stream(payload: dict[str, Any]) -> dict[str, Any]:
        with client.stream("POST", f"{base_url}/api/chat/stream", json=payload) as resp:
            resp.raise_for_status()
            collected: dict[str, Any] = {"answer": "", "sources": [], "rewritten_query": "", "cached": False}
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
                elif current_event == "sources":
                    collected["sources"] = parsed if isinstance(parsed, list) else collected["sources"]
                elif current_event == "token":
                    collected["answer"] += parsed if isinstance(parsed, str) else str(parsed)
                elif current_event == "cached":
                    collected["answer"] = parsed if isinstance(parsed, str) else str(parsed)
                    collected["cached"] = True
                elif current_event == "done":
                    if isinstance(parsed, dict) and "session_id" in parsed:
                        collected["session_id"] = parsed["session_id"]
                    collected["cached"] = bool(parsed.get("cached", False)) if isinstance(parsed, dict) else collected["cached"]
                current_event = None
                data_lines = []

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

    for index, user_query in enumerate(user_turns, 1):
        payload = {
            "query": user_query,
            "session_id": session_id,
            "mode": api_mode_from_fixture(fixture["mode_hint"]),
            "top_k": 5,
            "stream": transport == "stream",
        }
        response = post_stream(payload) if transport == "stream" else post_json(payload)
        session_id = response.get("session_id", session_id)
        if index == len(user_turns):
            last_response = {
                "original_query": user_query,
                **response,
            }

    if last_response is None:
        raise RuntimeError(f"Fixture {fixture['id']} did not contain a user turn")

    checks = evaluate_checks(fixture, last_response)
    return TurnResult(
        fixture_id=fixture["id"],
        mode_hint=fixture["mode_hint"],
        query_class=fixture["query_class"],
        language=fixture["language"],
        replayed_user_turns=len(user_turns),
        session_id=session_id,
        original_query=last_response["original_query"],
        rewritten_query=last_response.get("rewritten_query", ""),
        answer=last_response.get("answer", ""),
        sources=last_response.get("sources", []),
        transport=transport,
        duration_ms=0,
        checks=checks,
        passed=bool(checks["overall"]),
    )


def run(fixtures: list[dict[str, Any]], endpoint: str, transport: str, timeout: float, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "endpoint": endpoint,
            "transport": transport,
            "dry_run": True,
            "summary": {
                "fixtures_total": len(fixtures),
            },
            "fixtures": [
                {
                    "id": fixture["id"],
                    "mode_hint": fixture["mode_hint"],
                    "query_class": fixture["query_class"],
                    "conversation_turns": len(fixture["conversation"]),
                }
                for fixture in fixtures
            ],
        }

    client = httpx.Client(timeout=timeout)
    start = time.time()
    results: list[dict[str, Any]] = []
    try:
        try:
            client.post(f"{endpoint}/api/cache/clear")
        except Exception:
            pass
        for fixture in fixtures:
            fixture_start = time.time()
            result = replay_fixture(client, endpoint, transport, fixture)
            payload = asdict(result)
            payload["duration_ms"] = int((time.time() - fixture_start) * 1000)
            results.append(payload)
    finally:
        client.close()

    total_ms = int((time.time() - start) * 1000)
    passed = [r for r in results if r["passed"]]
    failed = [r for r in results if not r["passed"]]

    def avg_score(key: str) -> float:
        scores = [1.0 if r["checks"][key]["passed"] else 0.0 for r in results]
        return round(sum(scores) / len(scores) * 100, 1) if scores else 0.0

    summary = {
        "fixtures_total": len(results),
        "fixtures_passed": len(passed),
        "fixtures_failed": len(failed),
        "pass_rate": round(len(passed) / len(results) * 100, 1) if results else 0.0,
        "rewrite_pass_rate": avg_score("rewrite"),
        "retrieval_pass_rate": avg_score("retrieval"),
        "answer_pass_rate": avg_score("answer"),
        "total_runtime_ms": total_ms,
        "endpoint": endpoint,
        "transport": transport,
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "transport": transport,
        "dry_run": False,
        "summary": summary,
        "fixtures": results,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# OCP RAG Evaluation Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Endpoint: `{report['endpoint']}`",
        f"- Transport: `{report['transport']}`",
        f"- Fixtures: `{summary['fixtures_passed']}/{summary['fixtures_total']}` passed",
        f"- Pass rate: `{summary['pass_rate']}%`",
        f"- Rewrite pass rate: `{summary['rewrite_pass_rate']}%`",
        f"- Retrieval pass rate: `{summary['retrieval_pass_rate']}%`",
        f"- Answer pass rate: `{summary['answer_pass_rate']}%`",
        f"- Total runtime: `{summary['total_runtime_ms']}ms`",
        "",
        "## Fixture Results",
        "",
        "| ID | Mode | Class | Pass | Time | Top sources |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for fixture in report["fixtures"]:
        top_sources = ", ".join([s.get("source", "") for s in fixture.get("sources", [])[:3] if s.get("source")]) or "-"
        lines.append(
            f"| `{fixture['fixture_id']}` | `{fixture['mode_hint']}` | `{fixture['query_class']}` | "
            f"{'PASS' if fixture['passed'] else 'FAIL'} | `{fixture['duration_ms']}ms` | {top_sources} |"
        )

    failed = [fixture for fixture in report["fixtures"] if not fixture["passed"]]
    if failed:
        lines.extend(["", "## Failures", ""])
        for fixture in failed:
            lines.append(f"### `{fixture['fixture_id']}`")
            lines.append(f"- Original query: `{fixture['original_query']}`")
            lines.append(f"- Rewritten query: `{fixture['rewritten_query']}`")
            lines.append(f"- Session id: `{fixture['session_id']}`")
            for section in ("rewrite", "retrieval", "answer"):
                checks = fixture["checks"][section]["details"]
                for check in checks:
                    if not check["passed"]:
                        lines.append(f"- `{section}.{check['check']}` failed")
                        lines.append(f"  - Expected: `{check.get('expected')}`")
                        if "actual" in check:
                            lines.append(f"  - Actual: `{check.get('actual')}`")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: dict[str, Any], output: str | None, output_format: str) -> None:
    if output_format in ("json", "both"):
        json_path = Path(output) if output else DEFAULT_OUTPUT_JSON
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"JSON report written to {json_path}")

    if output_format in ("md", "both"):
        md_path = Path(output).with_suffix(".md") if output else DEFAULT_OUTPUT_MD
        md_path.parent.mkdir(parents=True, exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(render_markdown(report))
        print(f"Markdown report written to {md_path}")


def main() -> int:
    args = parse_args()
    endpoint = args.endpoint.rstrip("/")
    fixtures = load_fixtures(args.fixture)
    if args.limit is not None:
        fixtures = fixtures[: args.limit]

    if args.dry_run:
        report = run(fixtures, endpoint, args.transport, args.timeout, dry_run=True)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    report = run(fixtures, endpoint, args.transport, args.timeout, dry_run=False)
    write_outputs(report, args.output, args.format)

    summary = report["summary"]
    print(
        f"Passed {summary['fixtures_passed']}/{summary['fixtures_total']} fixtures "
        f"({summary['pass_rate']}%), transport={summary['transport']}, endpoint={summary['endpoint']}"
    )
    return 0 if summary["fixtures_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
