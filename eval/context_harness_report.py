from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


REQUIRED_FIELDS = {
    "trace_version",
    "run_id",
    "scenario_id",
    "turn_id",
    "turn_index",
    "turn_type",
    "user_query",
    "rewritten_query",
    "expected_support_chunk_ids",
    "retrieval_candidates",
    "reranked_candidates",
    "assembled_context",
    "citations",
    "token_budget",
    "truncation",
    "version_context",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize Stage 4.5 context-retention traces and classify where expected evidence was lost."
    )
    parser.add_argument("input", type=Path, help="Path to a JSONL trace file or a JSON array file.")
    return parser.parse_args()


def load_records(path: Path) -> list[dict]:
    if path.suffix.lower() == ".jsonl":
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return payload["records"]
    raise ValueError("Unsupported trace file shape. Use JSONL, JSON array, or an object with a 'records' list.")


def candidate_ids(items: Iterable[object]) -> list[str]:
    values: list[str] = []
    for item in items:
        if isinstance(item, str):
            values.append(item)
            continue
        if isinstance(item, dict):
            chunk_id = item.get("chunk_id") or item.get("id")
            if chunk_id:
                values.append(str(chunk_id))
    return values


def missing_fields(record: dict) -> list[str]:
    return sorted(field for field in REQUIRED_FIELDS if field not in record)


def summarize_record(record: dict) -> dict:
    expected = set(candidate_ids(record.get("expected_support_chunk_ids", [])))
    retrieved = set(candidate_ids(record.get("retrieval_candidates", [])))
    reranked = set(candidate_ids(record.get("reranked_candidates", [])))
    assembled = set(candidate_ids(record.get("assembled_context", [])))
    cited = set(candidate_ids(record.get("citations", [])))

    retrieval_miss = bool(expected and not expected.issubset(retrieved))
    rerank_loss = bool(expected and expected.issubset(retrieved) and not expected.issubset(reranked))
    assembly_loss = bool(expected and expected.issubset(reranked) and not expected.issubset(assembled))
    citation_loss = bool(expected and expected.issubset(assembled) and not expected.issubset(cited))

    truncation = record.get("truncation", {}) or {}
    version_context = record.get("version_context", {}) or {}
    version_before = str(version_context.get("before", "")).strip()
    version_after = str(version_context.get("after", "")).strip()
    change_reason = str(version_context.get("change_reason", "")).strip()
    version_drift = bool(version_before and version_after and version_before != version_after and change_reason != "explicit_user_change")

    is_follow_up = record.get("turn_type") == "follow_up"
    rewritten_query = str(record.get("rewritten_query", "")).strip()
    user_query = str(record.get("user_query", "")).strip()
    follow_up_rewrite_missing = bool(is_follow_up and (not rewritten_query or rewritten_query == user_query))

    findings = []
    if retrieval_miss:
        findings.append("retrieval_miss")
    if rerank_loss:
        findings.append("rerank_loss")
    if assembly_loss:
        findings.append("assembly_loss")
    if citation_loss:
        findings.append("citation_loss")
    if truncation.get("applied"):
        findings.append("truncation_applied")
    if version_drift:
        findings.append("version_drift")
    if follow_up_rewrite_missing:
        findings.append("follow_up_rewrite_missing")

    return {
        "turn_id": record.get("turn_id"),
        "scenario_id": record.get("scenario_id"),
        "turn_index": record.get("turn_index"),
        "findings": findings,
        "retrieved_count": len(retrieved),
        "reranked_count": len(reranked),
        "assembled_count": len(assembled),
        "cited_count": len(cited),
    }


def summarize_records(records: list[dict]) -> dict:
    invalid_records = []
    per_turn = []
    totals = {
        "record_count": len(records),
        "follow_up_turns": 0,
        "turns_with_rewrite": 0,
        "retrieval_miss": 0,
        "rerank_loss": 0,
        "assembly_loss": 0,
        "citation_loss": 0,
        "truncation_applied": 0,
        "version_drift": 0,
        "follow_up_rewrite_missing": 0,
    }

    for index, record in enumerate(records):
        missing = missing_fields(record)
        if missing:
            invalid_records.append({"index": index, "turn_id": record.get("turn_id"), "missing_fields": missing})
            continue

        summary = summarize_record(record)
        per_turn.append(summary)

        if record.get("turn_type") == "follow_up":
            totals["follow_up_turns"] += 1
        if str(record.get("rewritten_query", "")).strip():
            totals["turns_with_rewrite"] += 1

        for finding in summary["findings"]:
            if finding in totals:
                totals[finding] += 1

    return {
        "summary": totals,
        "invalid_records": invalid_records,
        "per_turn": per_turn,
    }


def main() -> None:
    args = parse_args()
    records = load_records(args.input)
    report = summarize_records(records)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
