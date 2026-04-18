from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import request

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_MANIFEST = ROOT / "manifests" / "ocp420_multiturn_live_scenarios.jsonl"
DEFAULT_OUTPUT = ROOT / "reports" / "multiturn" / "ocp420_multiturn_live_eval.json"
DEFAULT_API_BASE = "http://127.0.0.1:8765"
SECTION_PREFIX_RE = re.compile(r"^\s*[0-9]+(?:\.[0-9]+)*\.?\s*")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _normalize_topic(value: str) -> str:
    stripped = SECTION_PREFIX_RE.sub("", (value or "").strip())
    return re.sub(r"\s+", " ", stripped).strip().lower()


def _topic_matches(actual: str, expected: str) -> bool:
    normalized_actual = _normalize_topic(actual)
    normalized_expected = _normalize_topic(expected)
    if not normalized_actual or not normalized_expected:
        return False
    return (
        normalized_actual == normalized_expected
        or normalized_expected in normalized_actual
        or normalized_actual in normalized_expected
    )


def _post_json(api_base: str, path: str, payload: dict[str, Any], *, timeout: int) -> dict[str, Any]:
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{api_base.rstrip('/')}{path}",
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = str(item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _retrieved_books(payload: dict[str, Any]) -> list[str]:
    books: list[str] = []
    for citation in payload.get("citations", []):
        if isinstance(citation, dict):
            books.append(str(citation.get("book_slug") or ""))

    retrieval_trace = payload.get("retrieval_trace") or {}
    for key in ("bm25", "vector", "hybrid"):
        rows = retrieval_trace.get(key) or []
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    books.append(str(row.get("book_slug") or ""))

    metrics = retrieval_trace.get("metrics") or {}
    if isinstance(metrics, dict):
        for key in ("bm25", "vector", "hybrid", "reranked"):
            bucket = metrics.get(key) or {}
            if isinstance(bucket, dict):
                top_hits = bucket.get("top_hits") or []
                if isinstance(top_hits, list):
                    for row in top_hits:
                        if isinstance(row, dict):
                            books.append(str(row.get("book_slug") or ""))

    return _ordered_unique(books)


def _has_inline_citation(payload: dict[str, Any]) -> bool:
    cited_indices = payload.get("cited_indices") or []
    if isinstance(cited_indices, list) and cited_indices:
        return True
    answer = str(payload.get("answer") or "")
    return "[1]" in answer or "[2]" in answer or "[3]" in answer


def _classify_failure(
    *,
    response_kind: str,
    topic_pass: bool,
    context_pass: bool,
    corpus_target_pass: bool,
    citation_pass: bool,
    format_pass: bool,
) -> str:
    if response_kind == "no_answer":
        return "corpus 부재"
    if not corpus_target_pass or not citation_pass:
        return "retrieval 실패"
    if not context_pass or not topic_pass:
        return "context 유지 실패"
    return "answer formatting 문제"


def run_eval(
    *,
    manifest_path: Path,
    output_path: Path,
    api_base: str,
    timeout: int,
) -> dict[str, Any]:
    scenarios = _load_jsonl(manifest_path)
    turn_results: list[dict[str, Any]] = []
    scenario_results: list[dict[str, Any]] = []

    for scenario in scenarios:
        session_id = f"{scenario['id']}-{uuid.uuid4().hex[:8]}"
        scenario_turns: list[dict[str, Any]] = []
        for turn in scenario["turns"]:
            payload = _post_json(
                api_base,
                "/api/chat",
                {"session_id": session_id, "query": str(turn["query"])},
                timeout=timeout,
            )
            expected_books = [str(item) for item in turn.get("expected_book_slugs", [])]
            cited_books = _ordered_unique(
                [str(item.get("book_slug") or "") for item in payload.get("citations", []) if isinstance(item, dict)]
            )
            retrieved_books = _retrieved_books(payload)
            response_kind = str(payload.get("response_kind") or "")
            current_topic = str((payload.get("context") or {}).get("current_topic") or "")
            topic_pass = _topic_matches(current_topic, str(turn.get("expected_topic") or ""))
            citation_required = bool(turn.get("citation_required", False))
            citation_pass = (not citation_required) or any(book in expected_books for book in cited_books)
            corpus_target_pass = any(book in expected_books for book in retrieved_books)
            previous_context_required = bool(turn.get("previous_turn_context_required", False))
            context_pass = (not previous_context_required) or topic_pass
            format_pass = response_kind == "rag" and _has_inline_citation(payload)
            turn_pass = all(
                [
                    topic_pass,
                    context_pass,
                    corpus_target_pass,
                    format_pass,
                    citation_pass,
                ]
            )
            failure_bucket = ""
            if not turn_pass:
                failure_bucket = _classify_failure(
                    response_kind=response_kind,
                    topic_pass=topic_pass,
                    context_pass=context_pass,
                    corpus_target_pass=corpus_target_pass,
                    citation_pass=citation_pass,
                    format_pass=format_pass,
                )
            result = {
                "scenario_id": scenario["id"],
                "scenario_title": scenario["title"],
                "scenario_track": scenario["track"],
                "scenario_goal_type": scenario["goal_type"],
                "turn": int(turn["turn"]),
                "query": str(turn["query"]),
                "expected_topic": str(turn["expected_topic"]),
                "expected_book_slug": str(turn.get("expected_book_slug") or ""),
                "expected_book_slugs": expected_books,
                "corpus_target": str(turn.get("corpus_target") or ""),
                "citation_required": citation_required,
                "previous_turn_context_required": previous_context_required,
                "response_kind": response_kind,
                "history_size": int(payload.get("history_size") or 0),
                "current_topic": current_topic,
                "topic_pass": topic_pass,
                "context_pass": context_pass,
                "corpus_target_pass": corpus_target_pass,
                "citation_pass": citation_pass,
                "format_pass": format_pass,
                "pass": turn_pass,
                "failure_bucket": failure_bucket,
                "warnings": list(payload.get("warnings") or []),
                "cited_books": cited_books,
                "retrieved_books": retrieved_books[:10],
                "answer_preview": str(payload.get("answer") or "")[:320],
            }
            turn_results.append(result)
            scenario_turns.append(result)

        scenario_pass = all(item["pass"] for item in scenario_turns)
        scenario_results.append(
            {
                "scenario_id": scenario["id"],
                "title": scenario["title"],
                "track": scenario["track"],
                "goal_type": scenario["goal_type"],
                "turn_count": len(scenario_turns),
                "passed_turn_count": sum(int(item["pass"]) for item in scenario_turns),
                "completion_pass": scenario_pass,
                "failed_turns": [
                    {
                        "turn": item["turn"],
                        "query": item["query"],
                        "failure_bucket": item["failure_bucket"],
                        "response_kind": item["response_kind"],
                    }
                    for item in scenario_turns
                    if not item["pass"]
                ],
            }
        )

    failure_counts = Counter(item["failure_bucket"] for item in turn_results if item["failure_bucket"])
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_path": str(manifest_path),
        "api_base": api_base,
        "scenario_count": len(scenario_results),
        "turn_count": len(turn_results),
        "turn_pass_count": sum(int(item["pass"]) for item in turn_results),
        "turn_pass_rate": round(
            sum(int(item["pass"]) for item in turn_results) / max(len(turn_results), 1),
            4,
        ),
        "scenario_completion_count": sum(int(item["completion_pass"]) for item in scenario_results),
        "scenario_completion_rate": round(
            sum(int(item["completion_pass"]) for item in scenario_results) / max(len(scenario_results), 1),
            4,
        ),
        "failure_bucket_counts": dict(sorted(failure_counts.items())),
        "track_counts": dict(sorted(Counter(item["track"] for item in scenarios).items())),
        "goal_type_counts": dict(sorted(Counter(item["goal_type"] for item in scenarios).items())),
    }
    report = {
        "summary": summary,
        "scenarios": scenario_results,
        "turns": turn_results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the nightly OCP 4.20 live multiturn eval.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    report = run_eval(
        manifest_path=args.manifest,
        output_path=args.output,
        api_base=args.api_base,
        timeout=args.timeout,
    )
    json.dump(report["summary"], sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
