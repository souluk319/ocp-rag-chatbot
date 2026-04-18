from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import request

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT = ROOT / "reports" / "build_logs" / "ocp420_materialization_summary.json"
DEFAULT_API_BASE = "http://127.0.0.1:8765"

SOURCE_MANIFEST_UPDATE_REPORT = ROOT / "artifacts" / "corpus" / "source_manifest_update_report.json"
SOURCE_APPROVAL_REPORT = ROOT / "artifacts" / "corpus" / "source_approval_report.json"
CORPUS_GAP_REPORT = ROOT / "artifacts" / "corpus" / "corpus_gap_report.json"
TRANSLATION_LANE_REPORT = ROOT / "artifacts" / "corpus" / "translation_lane_report.json"
ACTIVE_RUNTIME_VIEWER_REPORT = ROOT / "reports" / "build_logs" / "active_runtime_viewer_serving_report.json"
APPROVED_MANIFEST = ROOT / "manifests" / "ocp_ko_4_20_approved_ko.json"
MORNING_GATE_LATEST = ROOT / "reports" / "build_logs" / "foundry_runs" / "profiles" / "morning_gate" / "latest.json"
VALIDATION_GATE_LATEST = ROOT / "reports" / "build_logs" / "foundry_runs" / "validation_gate" / "latest.json"
RUNTIME_SMOKE_LATEST = ROOT / "reports" / "build_logs" / "foundry_runs" / "runtime_smoke" / "latest.json"

RETRIEVAL_PROBES = [
    {
        "query": "OpenShift 아키텍처를 처음 설명해줘",
        "expected_book_slugs": ["architecture", "overview"],
        "expected_topic": "OpenShift 아키텍처",
    },
    {
        "query": "특정 namespace에 admin 권한 주는 법 알려줘",
        "expected_book_slugs": ["authentication_and_authorization"],
        "expected_topic": "RBAC",
    },
    {
        "query": "etcd 백업은 어떻게 하나?",
        "expected_book_slugs": ["postinstallation_configuration", "etcd"],
        "expected_topic": "etcd 백업/복원",
    },
    {
        "query": "Deployment의 복제본 개수를 늘리는 방법을 알려줘",
        "expected_book_slugs": ["cli_tools"],
        "expected_topic": "Deployment 스케일링",
    },
    {
        "query": "Machine Config Operator가 뭐야?",
        "expected_book_slugs": ["machine_configuration", "operators"],
        "expected_topic": "Machine Config Operator",
    },
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _job_payload(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    if "payload" in payload and isinstance(payload["payload"], dict):
        return dict(payload["payload"])
    return payload


def _get_json(api_base: str, path: str, *, timeout: int) -> dict[str, Any]:
    req = request.Request(f"{api_base.rstrip('/')}{path}", method="GET")
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


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


def _failure_type_counts(books: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for book in books:
        if str(book.get("approval_status") or "") == "approved" and str(book.get("content_status") or "") == "approved_ko":
            continue
        translation_lane = book.get("translation_lane") or {}
        citation_block_reason = str(book.get("citation_block_reason") or "").strip()
        corpus_output_mode = str(translation_lane.get("corpus_output_mode") or "").strip()
        if corpus_output_mode == "translation_required" or str(book.get("gap_lane") or "") == "translation_first":
            key = "translation_required:selected_language_fallback"
        elif citation_block_reason == "missing normalized sections or chunks":
            key = "blocked:missing_normalized_sections_or_chunks"
        elif citation_block_reason:
            key = f"blocked:{citation_block_reason}"
        else:
            key = f"blocked:{str(book.get('content_status') or 'unknown')}"
        counter[key] += 1
    return dict(sorted(counter.items()))


def _build_retrieval_probes(api_base: str, *, timeout: int) -> dict[str, Any]:
    probes: list[dict[str, Any]] = []
    pass_count = 0
    for index, spec in enumerate(RETRIEVAL_PROBES, start=1):
        payload = _post_json(
            api_base,
            "/api/chat",
            {"session_id": f"ocp420-summary-{index}", "query": spec["query"]},
            timeout=timeout,
        )
        citations = _ordered_unique(
            [str(item.get("book_slug") or "") for item in payload.get("citations", []) if isinstance(item, dict)]
        )
        probe_pass = str(payload.get("response_kind") or "") == "rag" and any(
            book in spec["expected_book_slugs"] for book in citations
        )
        pass_count += int(probe_pass)
        probes.append(
            {
                "query": spec["query"],
                "expected_topic": spec["expected_topic"],
                "expected_book_slugs": spec["expected_book_slugs"],
                "response_kind": payload.get("response_kind"),
                "current_topic": (payload.get("context") or {}).get("current_topic"),
                "cited_books": citations,
                "pass": probe_pass,
            }
        )
    return {
        "probe_count": len(probes),
        "pass_count": pass_count,
        "pass_rate": round(pass_count / max(len(probes), 1), 4),
        "retrieval_reflected": pass_count == len(probes),
        "probes": probes,
    }


def build_summary(*, output_path: Path, api_base: str, timeout: int) -> dict[str, Any]:
    source_manifest_report = _read_json(SOURCE_MANIFEST_UPDATE_REPORT)
    source_approval_report = _read_json(SOURCE_APPROVAL_REPORT)
    corpus_gap_report = _read_json(CORPUS_GAP_REPORT)
    translation_lane_report = _read_json(TRANSLATION_LANE_REPORT)
    active_runtime_viewer_report = _read_json(ACTIVE_RUNTIME_VIEWER_REPORT)
    approved_manifest = _read_json(APPROVED_MANIFEST)
    morning_gate_latest = _read_json(MORNING_GATE_LATEST)
    validation_gate_latest = _job_payload(VALIDATION_GATE_LATEST)
    runtime_smoke_latest = _job_payload(RUNTIME_SMOKE_LATEST)
    health_payload = _get_json(api_base, "/api/health", timeout=timeout)
    data_control_room_payload = _get_json(api_base, "/api/data-control-room", timeout=timeout)
    data_control_room_summary = data_control_room_payload.get("summary") or {}
    retrieval_probes = _build_retrieval_probes(api_base, timeout=timeout)

    high_value_issues = [
        {
            "book_slug": issue.get("book_slug"),
            "source_lane": issue.get("source_lane"),
            "content_status": issue.get("content_status"),
            "citation_block_reason": issue.get("citation_block_reason"),
        }
        for issue in source_approval_report.get("high_value_issues", [])[:5]
    ]

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_base": api_base,
        "source_inventory": {
            "input_doc_count": int(source_manifest_report.get("summary", {}).get("current_count", 0)),
            "source_catalog_entries": int(source_approval_report.get("summary", {}).get("book_count", 0)),
            "high_value_entry_count": int(len(source_approval_report.get("high_value_issues", []))),
        },
        "corpus_materialization": {
            "success_doc_count": int(source_approval_report.get("summary", {}).get("approved_ko_count", 0)),
            "failure_doc_count": int(source_approval_report.get("summary", {}).get("blocked_count", 0))
            + int(source_approval_report.get("summary", {}).get("translated_ko_draft_count", 0))
            + int(source_approval_report.get("summary", {}).get("en_only_count", 0)),
            "approved_manifest_count": int(approved_manifest.get("entry_count") or approved_manifest.get("count") or 0),
            "chunk_count": int(data_control_room_summary.get("chunk_count", 0)),
            "failure_types": _failure_type_counts(source_approval_report.get("books", [])),
            "high_value_translation_gaps": high_value_issues,
            "corpus_gap_summary": corpus_gap_report.get("summary", {}),
            "translation_lane_summary": translation_lane_report.get("summary", {}),
        },
        "library_materialization": {
            "library_visible_count": int(active_runtime_viewer_report.get("docs_materialized_count", 0)),
            "active_library_visible_count": int(active_runtime_viewer_report.get("active_runtime_materialized_count", 0)),
            "runtime_eligible_count": int(active_runtime_viewer_report.get("runtime_eligible_count", 0)),
            "active_manifest_count": int(active_runtime_viewer_report.get("active_manifest_count", 0)),
            "approved_runtime_count": int(data_control_room_summary.get("approved_runtime_count", 0)),
            "approved_wiki_runtime_book_count": int(data_control_room_summary.get("approved_wiki_runtime_book_count", 0)),
        },
        "runtime_live_state": {
            "health_ok": bool(health_payload.get("ok", False)),
            "active_pack": health_payload.get("runtime", {}).get("active_pack_id")
            or health_payload.get("runtime", {}).get("active_pack_label"),
            "docs_language": health_payload.get("runtime", {}).get("docs_language"),
            "corpus_book_count": int(data_control_room_summary.get("corpus_book_count", 0)),
            "manualbook_count": int(data_control_room_summary.get("manualbook_count", 0)),
            "known_book_count": int(data_control_room_summary.get("known_book_count", 0)),
            "gate_status": data_control_room_summary.get("gate_status"),
            "release_blocking": data_control_room_summary.get("release_blocking"),
        },
        "release_gate": {
            "status": morning_gate_latest.get("verdict", {}).get("status"),
            "release_blocking": morning_gate_latest.get("verdict", {}).get("release_blocking"),
            "reasons": list(morning_gate_latest.get("verdict", {}).get("reasons", [])),
            "approved_runtime_count": int(
                morning_gate_latest.get("verdict", {}).get("summary", {}).get("approved_runtime_count", 0)
            ),
            "translation_ready_count": int(
                morning_gate_latest.get("verdict", {}).get("summary", {}).get("translation_ready_count", 0)
            ),
            "manual_review_ready_count": int(
                morning_gate_latest.get("verdict", {}).get("summary", {}).get("manual_review_ready_count", 0)
            ),
            "high_value_issue_count": int(
                morning_gate_latest.get("verdict", {}).get("summary", {}).get("high_value_issue_count", 0)
            ),
            "current_run_at": morning_gate_latest.get("run_at"),
        },
        "validation_snapshot": {
            "artifact_expectation_mode": validation_gate_latest.get("artifact_expectation_mode"),
            "expected_book_count": validation_gate_latest.get("expected_book_count"),
            "expected_source_book_count": validation_gate_latest.get("expected_source_book_count"),
            "expected_derived_book_count": validation_gate_latest.get("expected_derived_book_count"),
            "chunk_book_count": validation_gate_latest.get("chunk_book_count"),
            "chunk_count": validation_gate_latest.get("chunk_count"),
            "qdrant_count": validation_gate_latest.get("qdrant_count"),
            "failed_checks": [
                name for name, value in dict(validation_gate_latest.get("checks", {})).items() if value is False
            ],
        },
        "runtime_smoke_snapshot": {
            "health_status": runtime_smoke_latest.get("probes", {}).get("local_ui", {}).get("health_status"),
            "qdrant_collection_present": runtime_smoke_latest.get("probes", {}).get("qdrant", {}).get("collection_present"),
            "graph_compact_ready": runtime_smoke_latest.get("runtime", {}).get("graph_compact_artifact", {}).get("ready"),
        },
        "retrieval_live_probes": retrieval_probes,
        "evidence_files": [
            str(SOURCE_MANIFEST_UPDATE_REPORT),
            str(SOURCE_APPROVAL_REPORT),
            str(CORPUS_GAP_REPORT),
            str(TRANSLATION_LANE_REPORT),
            str(ACTIVE_RUNTIME_VIEWER_REPORT),
            str(APPROVED_MANIFEST),
            str(MORNING_GATE_LATEST),
            str(VALIDATION_GATE_LATEST),
            str(RUNTIME_SMOKE_LATEST),
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the nightly OCP 4.20 materialization summary.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    summary = build_summary(
        output_path=args.output,
        api_base=args.api_base,
        timeout=args.timeout,
    )
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
