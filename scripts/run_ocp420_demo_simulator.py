from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib import request

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_MANIFEST = ROOT / "manifests" / "ocp420_demo_simulator_scenarios.jsonl"
DEFAULT_OUTPUT = ROOT / "reports" / "demo_simulator" / "ocp420_demo_simulator_eval.json"
DEFAULT_API_BASE = "http://127.0.0.1:8765"
SECTION_PREFIX_RE = re.compile(r"^\s*[0-9]+(?:\.[0-9]+)*\.?\s*")
GUIDE_SIGNAL_RE = re.compile(r"(먼저|우선|확인|다음|주의|핵심|실무)")
BLOCKING_WARNING_RE = re.compile(
    r"(no inline citation|insufficient .* grounding|missing corpus coverage)",
    re.IGNORECASE,
)
LEGACY_BOOK_FAMILY_PREFIXES: dict[str, tuple[str, ...]] = {
    "architecture": ("architecture__",),
    "authentication_and_authorization": ("authentication__",),
    "backup_and_restore": ("backup_and_restore__",),
    "cli_tools": ("cli_reference__",),
    "etcd": ("etcd__",),
    "images": ("openshift_images__", "disconnected__installing_mirroring_installation_images"),
    "machine_config_operations": ("machine_configuration__",),
    "machine_config_rollout_operations": ("machine_configuration__",),
    "machine_configuration": ("machine_configuration__",),
    "operators": ("operators__",),
    "overview": ("welcome__",),
    "postinstallation_configuration": (
        "post_installation_configuration__",
        "installing__installing_bare_metal__bare_metal_postinstallation_configuration",
    ),
    "route_and_ingress": ("networking__ingress_load_balancing__",),
}


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


def _ordered_unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = str(item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _family_prefixes_for_expected_slug(expected_slug: str) -> tuple[str, ...]:
    slug = str(expected_slug or "").strip()
    if not slug:
        return ()
    prefixes = list(LEGACY_BOOK_FAMILY_PREFIXES.get(slug, ()))
    prefixes.append(f"{slug}__")
    return tuple(_ordered_unique(prefixes))


def _match_expected_key(
    actual_book_slug: str,
    *,
    expected_book_slugs: list[str],
    expected_book_families: list[str],
) -> str:
    actual = str(actual_book_slug or "").strip()
    if not actual:
        return ""
    for expected_slug in expected_book_slugs:
        if actual == expected_slug:
            return expected_slug
    for expected_slug in expected_book_slugs:
        for prefix in _family_prefixes_for_expected_slug(expected_slug):
            if actual.startswith(prefix):
                return expected_slug
    for family_prefix in expected_book_families:
        family = str(family_prefix or "").strip()
        if family and actual.startswith(family):
            return family
    return actual


def _normalize_book_list(
    book_slugs: Iterable[str],
    *,
    expected_book_slugs: list[str],
    expected_book_families: list[str],
) -> list[str]:
    return _ordered_unique(
        _match_expected_key(
            str(book_slug),
            expected_book_slugs=expected_book_slugs,
            expected_book_families=expected_book_families,
        )
        for book_slug in book_slugs
    )


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
                for row in bucket.get("top_hits") or []:
                    if isinstance(row, dict):
                        books.append(str(row.get("book_slug") or ""))

    return _ordered_unique(books)


def _has_inline_citation(payload: dict[str, Any]) -> bool:
    cited_indices = payload.get("cited_indices") or []
    if isinstance(cited_indices, list) and cited_indices:
        return True
    answer = str(payload.get("answer") or "")
    return "[1]" in answer or "[2]" in answer or "[3]" in answer


def _guide_tone_pass(*, query: str, answer: str, mode: str) -> bool:
    normalized_query = str(query or "").strip().lower()
    normalized_answer = re.sub(r"\s+", " ", str(answer or "").strip())
    if not normalized_answer.startswith("답변:"):
        return False
    if any(token in normalized_answer for token in ("차이", "전역", "범위", "프로젝트")):
        return True
    if mode == "ops" or any(token in normalized_query for token in ("방법", "명령", "절차", "확인")):
        return bool("```" in normalized_answer or GUIDE_SIGNAL_RE.search(normalized_answer))
    return bool(
        GUIDE_SIGNAL_RE.search(normalized_answer)
        or any(token in normalized_answer for token in ("역할", "의미", "사용", "실제", "이유", "운영", "구성", "중요"))
    )


def _hallucination_guard_pass(
    *,
    payload: dict[str, Any],
    expected_match_keys: list[str],
    cited_books: list[str],
    retrieved_books: list[str],
) -> bool:
    warnings = [str(item or "") for item in payload.get("warnings") or []]
    if str(payload.get("response_kind") or "") != "rag":
        return False
    if any(BLOCKING_WARNING_RE.search(warning) for warning in warnings):
        return False
    if not _has_inline_citation(payload):
        return False
    if expected_match_keys and not any(book in expected_match_keys for book in cited_books):
        return False
    if expected_match_keys and not any(book in expected_match_keys for book in retrieved_books):
        return False
    return True


def _stream_chat(api_base: str, payload: dict[str, Any], *, timeout: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{api_base.rstrip('/')}/api/chat/stream",
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as resp:
        events: list[dict[str, Any]] = []
        result_payload: dict[str, Any] | None = None
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
                if event.get("type") == "error":
                    raise RuntimeError(str(event.get("error") or "stream error"))
                if event.get("type") == "result" and isinstance(event.get("payload"), dict):
                    result_payload = dict(event["payload"])
        if result_payload is None:
            raise RuntimeError("stream completed without result payload")
    return result_payload, events


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
        turns = scenario.get("turns") or []
        session_id = f"{scenario['id']}-{uuid.uuid4().hex[:8]}"
        scenario_turns: list[dict[str, Any]] = []

        for turn in turns:
            payload, events = _stream_chat(
                api_base,
                {
                    "session_id": session_id,
                    "query": str(turn["query"]),
                },
                timeout=timeout,
            )
            expected_books = _ordered_unique(turn.get("expected_book_slugs", []))
            expected_families = _ordered_unique(turn.get("expected_book_families", []))
            expected_match_keys = _ordered_unique(expected_books + expected_families)
            raw_cited_books = _ordered_unique(
                [str(item.get("book_slug") or "") for item in payload.get("citations", []) if isinstance(item, dict)]
            )
            cited_books = _normalize_book_list(
                raw_cited_books,
                expected_book_slugs=expected_books,
                expected_book_families=expected_families,
            )
            raw_retrieved_books = _retrieved_books(payload)
            retrieved_books = _normalize_book_list(
                raw_retrieved_books,
                expected_book_slugs=expected_books,
                expected_book_families=expected_families,
            )
            response_kind = str(payload.get("response_kind") or "")
            current_topic = str((payload.get("context") or {}).get("current_topic") or "")
            stream_trace_count = sum(1 for event in events if str(event.get("type") or "") == "trace")
            stream_result_count = sum(1 for event in events if str(event.get("type") or "") == "result")
            streaming_pass = stream_trace_count > 0 and stream_result_count == 1
            topic_pass = _topic_matches(current_topic, str(turn.get("expected_topic") or ""))
            citation_required = bool(turn.get("citation_required", False))
            citation_pass = (not citation_required) or any(book in expected_match_keys for book in cited_books)
            retrieval_pass = any(book in expected_match_keys for book in retrieved_books)
            context_required = bool(turn.get("previous_turn_context_required", False))
            history_size = int(payload.get("history_size") or 0)
            history_pass = history_size >= int(turn.get("turn") or 0)
            context_pass = (not context_required) or (topic_pass and history_pass)
            guide_tone_pass = _guide_tone_pass(
                query=str(turn.get("query") or ""),
                answer=str(payload.get("answer") or ""),
                mode=str(scenario.get("mode") or turn.get("mode") or "ops"),
            )
            hallucination_guard_pass = _hallucination_guard_pass(
                payload=payload,
                expected_match_keys=expected_match_keys,
                cited_books=cited_books,
                retrieved_books=retrieved_books,
            )
            turn_pass = all(
                (
                    streaming_pass,
                    topic_pass,
                    citation_pass,
                    retrieval_pass,
                    context_pass,
                    history_pass,
                    guide_tone_pass,
                    hallucination_guard_pass,
                )
            )

            result = {
                "scenario_id": scenario["id"],
                "scenario_title": scenario["title"],
                "turn": int(turn["turn"]),
                "query": str(turn["query"]),
                "mode": str(scenario.get("mode") or turn.get("mode") or "ops"),
                "expected_topic": str(turn.get("expected_topic") or ""),
                "response_kind": response_kind,
                "history_size": history_size,
                "current_topic": current_topic,
                "stream_trace_count": stream_trace_count,
                "stream_result_count": stream_result_count,
                "streaming_pass": streaming_pass,
                "topic_pass": topic_pass,
                "citation_pass": citation_pass,
                "retrieval_pass": retrieval_pass,
                "context_pass": context_pass,
                "history_pass": history_pass,
                "guide_tone_pass": guide_tone_pass,
                "hallucination_guard_pass": hallucination_guard_pass,
                "pass": turn_pass,
                "warnings": list(payload.get("warnings") or []),
                "cited_books": cited_books,
                "retrieved_books": retrieved_books[:10],
                "answer_preview": str(payload.get("answer") or "")[:320],
            }
            turn_results.append(result)
            scenario_turns.append(result)

        scenario_pass = len(scenario_turns) >= 5 and all(item["pass"] for item in scenario_turns)
        scenario_results.append(
            {
                "scenario_id": scenario["id"],
                "title": scenario["title"],
                "mode": str(scenario.get("mode") or "ops"),
                "track": str(scenario.get("track") or ""),
                "turn_count": len(scenario_turns),
                "meets_min_turn_requirement": len(scenario_turns) >= 5,
                "passed_turn_count": sum(int(item["pass"]) for item in scenario_turns),
                "completion_pass": scenario_pass,
                "failed_turns": [
                    {
                        "turn": item["turn"],
                        "query": item["query"],
                        "streaming_pass": item["streaming_pass"],
                        "topic_pass": item["topic_pass"],
                        "citation_pass": item["citation_pass"],
                        "retrieval_pass": item["retrieval_pass"],
                        "context_pass": item["context_pass"],
                        "guide_tone_pass": item["guide_tone_pass"],
                        "hallucination_guard_pass": item["hallucination_guard_pass"],
                    }
                    for item in scenario_turns
                    if not item["pass"]
                ],
            }
        )

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest_path": str(manifest_path),
        "api_base": api_base,
        "scenario_count": len(scenario_results),
        "turn_count": len(turn_results),
        "scenario_completion_count": sum(int(item["completion_pass"]) for item in scenario_results),
        "scenario_completion_rate": round(
            sum(int(item["completion_pass"]) for item in scenario_results) / max(len(scenario_results), 1),
            4,
        ),
        "turn_pass_count": sum(int(item["pass"]) for item in turn_results),
        "turn_pass_rate": round(
            sum(int(item["pass"]) for item in turn_results) / max(len(turn_results), 1),
            4,
        ),
        "streaming_turn_pass_rate": round(
            sum(int(item["streaming_pass"]) for item in turn_results) / max(len(turn_results), 1),
            4,
        ),
        "guide_tone_pass_rate": round(
            sum(int(item["guide_tone_pass"]) for item in turn_results) / max(len(turn_results), 1),
            4,
        ),
        "hallucination_guard_pass_rate": round(
            sum(int(item["hallucination_guard_pass"]) for item in turn_results) / max(len(turn_results), 1),
            4,
        ),
        "history_pass_rate": round(
            sum(int(item["history_pass"]) for item in turn_results) / max(len(turn_results), 1),
            4,
        ),
        "track_counts": dict(sorted(Counter(str(item.get("track") or "") for item in scenario_results).items())),
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
    parser = argparse.ArgumentParser(description="Run the OCP 4.20 demo simulator harness.")
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
