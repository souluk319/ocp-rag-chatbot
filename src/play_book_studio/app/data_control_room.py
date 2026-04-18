"""데이터상황실 전용 집계 payload."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from play_book_studio.app.data_control_room_buckets import (
    _build_approved_wiki_runtime_book_bucket,
    _build_product_gate_bucket,
    _build_buyer_packet_bundle_bucket,
    _build_gold_candidate_book_bucket,
    _build_navigation_backlog_bucket,
    _build_product_rehearsal_summary,
    _build_release_candidate_freeze_summary,
    _build_wiki_usage_signal_bucket,
    _iso_now,
    _safe_int,
    _safe_read_json,
    _safe_read_yaml,
)
from play_book_studio.config.settings import load_settings
from play_book_studio.intake import CustomerPackDraftStore
from play_book_studio.ingestion.topic_playbooks import (
    DERIVED_PLAYBOOK_SOURCE_TYPES,
    OPERATION_PLAYBOOK_SOURCE_TYPE,
    TOPIC_PLAYBOOK_SOURCE_TYPE,
    TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE,
)

POLICY_OVERLAY_BOOK_SOURCE_TYPE = "policy_overlay_book"
SYNTHESIZED_PLAYBOOK_SOURCE_TYPE = "synthesized_playbook"
DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPES = (
    TOPIC_PLAYBOOK_SOURCE_TYPE,
    OPERATION_PLAYBOOK_SOURCE_TYPE,
    TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE,
    POLICY_OVERLAY_BOOK_SOURCE_TYPE,
    SYNTHESIZED_PLAYBOOK_SOURCE_TYPE,
)
DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPE_SET = frozenset(
    set(DERIVED_PLAYBOOK_SOURCE_TYPES)
    | {
        POLICY_OVERLAY_BOOK_SOURCE_TYPE,
        SYNTHESIZED_PLAYBOOK_SOURCE_TYPE,
    }
)
PLAYBOOK_LIBRARY_FAMILY_LABELS = {
    TOPIC_PLAYBOOK_SOURCE_TYPE: "토픽 플레이북",
    OPERATION_PLAYBOOK_SOURCE_TYPE: "운용 플레이북",
    TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE: "트러블슈팅 플레이북",
    POLICY_OVERLAY_BOOK_SOURCE_TYPE: "정책 오버레이",
    SYNTHESIZED_PLAYBOOK_SOURCE_TYPE: "종합 플레이북",
}
def _safe_read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists() or not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _path_snapshot(path: Path) -> dict[str, Any]:
    exists = path.exists()
    payload: dict[str, Any] = {
        "path": str(path),
        "exists": exists,
    }
    if exists:
        try:
            stat = path.stat()
            payload["mtime"] = datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds")
            if path.is_file():
                payload["size_bytes"] = stat.st_size
        except OSError:
            return payload
    return payload


def _path_snapshot_for_optional(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"path": "", "exists": False}
    return _path_snapshot(path)


def _job_payload(report: dict[str, Any], job_id: str) -> dict[str, Any]:
    for job in report.get("job_results", []):
        if not isinstance(job, dict):
            continue
        if str(job.get("job_id") or "") != job_id:
            continue
        payload = job.get("payload")
        return payload if isinstance(payload, dict) else {}
    return {}


def _job_report_path(report: dict[str, Any], job_id: str) -> str:
    for job in report.get("job_results", []):
        if not isinstance(job, dict):
            continue
        if str(job.get("job_id") or "") != job_id:
            continue
        return str(job.get("audit_report_path") or "")
    return ""


def _resolve_report_path(candidate: str) -> Path | None:
    value = str(candidate or "").strip()
    if not value:
        return None
    path = Path(value)
    return path if path.exists() else None
def _report_count(report: dict[str, Any], *, summary_key: str, rows_key: str) -> int:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if isinstance(summary, dict) and summary_key in summary:
        return _safe_int(summary.get(summary_key))
    rows = report.get(rows_key)
    if isinstance(rows, list):
        return len(rows)
    return 0


def _select_report_candidate(
    *paths: Path | None,
    summary_key: str,
    rows_key: str,
    expected_count: int = 0,
) -> tuple[Path | None, dict[str, Any]]:
    candidates: list[tuple[tuple[int, int, int, float], Path, dict[str, Any]]] = []
    seen: set[Path] = set()
    for candidate_path in paths:
        if candidate_path is None:
            continue
        resolved = candidate_path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        payload = _safe_read_json(resolved)
        if not payload:
            continue
        primary_count = _report_count(payload, summary_key=summary_key, rows_key=rows_key)
        book_count = _report_count(payload, summary_key="book_count", rows_key="books")
        try:
            mtime = resolved.stat().st_mtime
        except OSError:
            mtime = 0.0
        score = (
            1 if expected_count > 0 and primary_count == expected_count else 0,
            1 if primary_count > 0 else 0,
            book_count,
            mtime,
        )
        candidates.append((score, resolved, payload))

    if not candidates:
        return None, {}

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, best_path, best_payload = candidates[0]
    return best_path, best_payload


def _grade_label(book: dict[str, Any]) -> str:
    content_status = str(book.get("content_status") or "").strip()
    approval_status = str(book.get("approval_status") or "").strip()
    if content_status == "approved_ko" and approval_status == "approved":
        return "Gold"
    if content_status == "translated_ko_draft":
        return "Silver Draft"
    if content_status == "mixed":
        return "Mixed Review"
    if content_status == "en_only":
        return "English Only"
    if content_status == "blocked":
        return "Blocked"
    if content_status:
        return content_status
    if approval_status:
        return approval_status
    return "Unknown"


def _is_gold_book(book: dict[str, Any]) -> bool:
    content_status = str(book.get("content_status") or "").strip()
    approval_status = str(book.get("approval_status") or book.get("review_status") or "").strip()
    return content_status == "approved_ko" and approval_status == "approved"


def _candidate_file_rows(*paths: Path) -> tuple[Path | None, list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    selected_path: Path | None = None
    selected_rows: list[dict[str, Any]] = []
    for path in paths:
        if any(item.get("path") == str(path) for item in candidates):
            continue
        rows = _safe_read_jsonl(path)
        candidates.append(
            {
                **_path_snapshot(path),
                "row_count": len(rows),
            }
        )
        if selected_path is None and rows:
            selected_path = path
            selected_rows = rows
    if selected_path is None and candidates:
        selected_path = Path(candidates[0]["path"])
    return selected_path, selected_rows, candidates


def _candidate_playbook_dirs(*paths: Path, expected_count: int) -> tuple[Path | None, list[Path], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    selected_dir: Path | None = None
    selected_files: list[Path] = []
    for path in paths:
        if any(item.get("path") == str(path) for item in candidates):
            continue
        files = sorted(path.glob("*.json")) if path.exists() and path.is_dir() else []
        candidate_payload = {
            **_path_snapshot(path),
            "file_count": len(files),
        }
        candidates.append(candidate_payload)
        if selected_dir is None and files and len(files) == expected_count:
            selected_dir = path
            selected_files = files
    if selected_dir is None:
        best = None
        best_files: list[Path] = []
        for candidate in candidates:
            path = Path(str(candidate["path"]))
            files = sorted(path.glob("*.json")) if path.exists() and path.is_dir() else []
            if len(files) > len(best_files):
                best = path
                best_files = files
        selected_dir = best
        selected_files = best_files
    return selected_dir, selected_files, candidates


def _summarize_eval(report: dict[str, Any], *, overall_key: str = "overall") -> dict[str, Any]:
    overall = report.get(overall_key) if isinstance(report.get(overall_key), dict) else {}
    payload: dict[str, Any] = {"exists": bool(report)}
    for key in (
        "case_count",
        "book_hit_at_1",
        "book_hit_at_3",
        "book_hit_at_5",
        "pass_rate",
        "avg_citation_precision",
        "answer_present_rate",
        "faithfulness",
        "answer_relevancy",
    ):
        value = overall.get(key)
        if value is not None:
            payload[key] = value
    return payload


def _book_index(books: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(book.get("book_slug") or "").strip(): book
        for book in books
        if isinstance(book, dict) and str(book.get("book_slug") or "").strip()
    }


def _build_high_value_focus(
    source_bundle_quality: dict[str, Any],
    *,
    known_books: dict[str, dict[str, Any]],
    manifest_by_slug: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    bundles = source_bundle_quality.get("bundles") if isinstance(source_bundle_quality.get("bundles"), list) else []
    items: list[dict[str, Any]] = []
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        slug = str(bundle.get("book_slug") or "").strip()
        known = known_books.get(slug, {})
        manifest = manifest_by_slug.get(slug, {})
        items.append(
            {
                "book_slug": slug,
                "title": str(bundle.get("title") or known.get("title") or manifest.get("title") or slug),
                "grade": _grade_label(known) if known else _grade_label(manifest) if manifest else "Unknown",
                "content_status": str(bundle.get("content_status") or known.get("content_status") or manifest.get("content_status") or ""),
                "gap_lane": str(bundle.get("gap_lane") or known.get("gap_lane") or manifest.get("gap_lane") or ""),
                "promotion_strategy": str(bundle.get("promotion_strategy") or ""),
                "readiness": str(bundle.get("readiness") or ""),
                "ko_fallback_banner": bool(bundle.get("ko_fallback_banner") or False),
                "manifest_approved": bool(bundle.get("manifest_approved") or False),
                "has_en_html": bool(bundle.get("has_en_html") or False),
                "repo_artifact_count": int(bundle.get("repo_artifact_count") or 0),
                "exact_issue_pr_count": int(bundle.get("exact_issue_pr_count") or 0),
                "related_issue_pr_count": int(bundle.get("related_issue_pr_count") or 0),
                "recommended_action": str(bundle.get("recommended_action") or ""),
            }
        )

    if not items:
        for book in known_books.values():
            if not bool(book.get("high_value")):
                continue
            items.append(
                {
                    "book_slug": str(book.get("book_slug") or ""),
                    "title": str(book.get("title") or ""),
                    "grade": str(book.get("grade") or "Unknown"),
                    "content_status": str(book.get("content_status") or ""),
                    "gap_lane": str(book.get("gap_lane") or ""),
                    "promotion_strategy": "",
                    "readiness": str(book.get("grade") or ""),
                    "ko_fallback_banner": bool(book.get("fallback_detected") or False),
                    "manifest_approved": str(book.get("approval_status") or "") == "approved",
                    "has_en_html": bool(book.get("source_url") or ""),
                    "repo_artifact_count": int(book.get("chunk_count") or 0),
                    "exact_issue_pr_count": 0,
                    "related_issue_pr_count": 0,
                    "recommended_action": str(book.get("gap_action") or ""),
                }
            )

    return {
        "count": len(items),
        "books": sorted(items, key=lambda item: (str(item.get("readiness") or ""), str(item.get("book_slug") or ""))),
        "ready_count": sum(1 for item in items if str(item.get("readiness") or "") == "already_promoted"),
        "manifest_approved_count": sum(1 for item in items if bool(item.get("manifest_approved"))),
    }


def _build_source_of_truth_drift(
    *,
    gate_report: dict[str, Any],
    source_approval_report: dict[str, Any],
    translation_lane_report: dict[str, Any],
    manifest_path: Path,
    selected_chunks_path: Path | None,
    chunk_candidates: list[dict[str, Any]],
    selected_playbook_dir: Path | None,
    playbook_candidates: list[dict[str, Any]],
    source_approval_report_path: Path | None,
    translation_lane_path: Path | None,
) -> dict[str, Any]:
    gate_verdict = gate_report.get("verdict") if isinstance(gate_report.get("verdict"), dict) else {}
    gate_summary = gate_verdict.get("summary") if isinstance(gate_verdict.get("summary"), dict) else {}
    source_summary = source_approval_report.get("summary") if isinstance(source_approval_report.get("summary"), dict) else {}
    translation_summary = translation_lane_report.get("summary") if isinstance(translation_lane_report.get("summary"), dict) else {}

    chunk_existing = [candidate for candidate in chunk_candidates if bool(candidate.get("exists"))]
    playbook_existing = [candidate for candidate in playbook_candidates if bool(candidate.get("exists"))]
    chunk_drift = len(chunk_existing) > 1
    playbook_drift = len(playbook_existing) > 1
    manifest_drift = not manifest_path.exists()

    mismatches: list[str] = []
    if int(gate_summary.get("approved_runtime_count") or 0) != int(source_summary.get("approved_ko_count") or 0):
        mismatches.append("gate_approved_runtime_count_vs_source_approval_approved_ko_count")
    if int(translation_summary.get("active_queue_count") or 0) != len(translation_lane_report.get("active_queue") or []):
        mismatches.append("translation_lane_active_queue_count_vs_payload")

    return {
        "canonical_grade_source": {
            "name": "source_approval_report",
            "path": str(source_approval_report_path or ""),
            "exists": bool(source_approval_report_path and source_approval_report_path.exists()),
            "rule": "Source approval report is the grade authority for approved_ko / translated_ko_draft / blocked classification.",
            "derived_views": [
                "known_books",
                "gold_books",
                "summary.gate.approved_runtime_count",
            ],
            "summary": source_summary,
        },
        "storage_drift": {
            "manifest": {
                "path": str(manifest_path),
                "exists": manifest_path.exists(),
                "selected": str(manifest_path),
            },
            "chunks": {
                "selected_path": str(selected_chunks_path or ""),
                "candidates": chunk_existing,
                "drift_detected": chunk_drift,
            },
            "playbooks": {
                "selected_dir": str(selected_playbook_dir or ""),
                "candidates": playbook_existing,
                "drift_detected": playbook_drift,
            },
            "report_paths": {
                "source_approval_report": str(source_approval_report_path or ""),
                "translation_lane_report": str(translation_lane_path or ""),
            },
            "drift_detected": manifest_drift or chunk_drift or playbook_drift or bool(mismatches),
        },
        "status_alignment": {
            "gate_status": str(gate_verdict.get("status") or "unknown"),
            "approved_runtime_count": int(gate_summary.get("approved_runtime_count") or 0),
            "approved_ko_count": int(source_summary.get("approved_ko_count") or 0),
            "active_queue_count": int(translation_summary.get("active_queue_count") or 0),
            "mismatches": mismatches,
        },
    }


def _build_known_books_section(
    source_books: list[dict[str, Any]],
    *,
    manifest_by_slug: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    known_books = [_simplify_book(book) for book in source_books if isinstance(book, dict)]
    for book in known_books:
        slug = str(book.get("book_slug") or "").strip()
        manifest = manifest_by_slug.get(slug, {})
        if not book.get("source_url"):
            book["source_url"] = str(manifest.get("source_url") or manifest.get("resolved_source_url") or "")
        if not book.get("viewer_path"):
            book["viewer_path"] = str(manifest.get("viewer_path") or "")
    return known_books


def _simplify_book(book: dict[str, Any]) -> dict[str, Any]:
    translation_lane = book.get("translation_lane") if isinstance(book.get("translation_lane"), dict) else {}
    reader_grade = book.get("manualbook_reader_grade") if isinstance(book.get("manualbook_reader_grade"), dict) else {}
    return {
        "book_slug": str(book.get("book_slug") or ""),
        "title": str(book.get("title") or book.get("vendor_title") or ""),
        "grade": _grade_label(book),
        "content_status": str(book.get("content_status") or ""),
        "approval_status": str(book.get("approval_status") or ""),
        "review_status": str(book.get("review_status") or ""),
        "source_type": str(book.get("source_type") or ""),
        "source_lane": str(book.get("source_lane") or ""),
        "high_value": bool(book.get("high_value")),
        "fallback_detected": bool(book.get("fallback_detected")),
        "chunk_count": int(book.get("chunk_count") or 0),
        "section_count": int(book.get("section_count") or 0),
        "viewer_path": str(book.get("viewer_path") or ""),
        "source_url": str(book.get("source_url") or ""),
        "updated_at": str(book.get("updated_at") or ""),
        "manualbook_reader_grade_failed": bool(book.get("manualbook_reader_grade_failed")),
        "manualbook_reader_grade": reader_grade,
        "runtime_eligible": bool(translation_lane.get("runtime_eligible")),
        "citation_eligible": bool(book.get("citation_eligible")),
        "gap_lane": str(book.get("gap_lane") or ""),
        "gap_action": str(book.get("gap_action") or ""),
        "approval_state": str(book.get("approval_state") or ""),
        "publication_state": str(book.get("publication_state") or ""),
        "parser_backend": str(book.get("parser_backend") or ""),
        "boundary_truth": str(book.get("boundary_truth") or ""),
        "runtime_truth_label": str(book.get("runtime_truth_label") or ""),
        "boundary_badge": str(book.get("boundary_badge") or ""),
    }


def _customer_pack_draft_id_from_book(book: dict[str, Any]) -> str:
    viewer_path = str(book.get("viewer_path") or "").strip()
    prefix = "/playbooks/customer-packs/"
    if viewer_path.startswith(prefix):
        remainder = viewer_path[len(prefix) :]
        parts = [part for part in remainder.split("/") if part]
        if parts:
            return str(parts[0]).strip()
    slug = str(book.get("book_slug") or "").strip()
    if "--" in slug:
        return slug.split("--", 1)[0].strip()
    return ""


def _apply_customer_pack_runtime_truth(
    books: list[dict[str, Any]],
    *,
    draft_records_by_id: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for book in books:
        entry = dict(book)
        draft_id = _customer_pack_draft_id_from_book(entry)
        record = draft_records_by_id.get(draft_id) if draft_id else None
        if record is not None:
            entry["source_lane"] = str(entry.get("source_lane") or getattr(record, "source_lane", "") or "customer_source_first_pack")
            entry["approval_state"] = str(entry.get("approval_state") or getattr(record, "approval_state", "") or "unreviewed")
            entry["publication_state"] = str(entry.get("publication_state") or getattr(record, "publication_state", "") or "draft")
            entry["parser_backend"] = str(entry.get("parser_backend") or getattr(record, "parser_backend", "") or "customer_pack_normalize_service")
            entry["boundary_truth"] = str(entry.get("boundary_truth") or "private_customer_pack_runtime")
            entry["runtime_truth_label"] = str(entry.get("runtime_truth_label") or "Customer Source-First Pack")
            entry["boundary_badge"] = str(entry.get("boundary_badge") or "Private Pack Runtime")
        items.append(entry)
    return items


def _aggregate_corpus_books(
    rows: list[dict[str, Any]],
    *,
    manifest_by_slug: dict[str, dict[str, Any]],
    known_books: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        slug = str(row.get("book_slug") or "").strip()
        if not slug:
            continue
        title = (
            str(row.get("book_title") or "")
            or str(known_books.get(slug, {}).get("title") or "")
            or str(manifest_by_slug.get(slug, {}).get("title") or "")
            or slug
        )
        bucket = grouped.setdefault(
            slug,
            {
                "book_slug": slug,
                "title": title,
                "grade": _grade_label(known_books.get(slug, {})) if slug in known_books else "Gold" if slug in manifest_by_slug else "Unknown",
                "chunk_count": 0,
                "token_total": 0,
                "command_chunk_count": 0,
                "error_chunk_count": 0,
                "anchors": set(),
                "chunk_types": Counter(),
                "source_type": str(row.get("source_type") or manifest_by_slug.get(slug, {}).get("source_type") or ""),
                "source_lane": str(row.get("source_lane") or manifest_by_slug.get(slug, {}).get("source_lane") or ""),
                "review_status": str(row.get("review_status") or manifest_by_slug.get(slug, {}).get("review_status") or ""),
                "updated_at": str(row.get("updated_at") or manifest_by_slug.get(slug, {}).get("updated_at") or ""),
                "viewer_path": str(row.get("viewer_path") or manifest_by_slug.get(slug, {}).get("viewer_path") or ""),
                "source_url": str(row.get("source_url") or known_books.get(slug, {}).get("source_url") or manifest_by_slug.get(slug, {}).get("source_url") or ""),
                "materialized": True,
            },
        )
        bucket["chunk_count"] += 1
        bucket["token_total"] += int(row.get("token_count") or 0)
        if row.get("cli_commands"):
            bucket["command_chunk_count"] += 1
        if row.get("error_strings"):
            bucket["error_chunk_count"] += 1
        anchor_id = str(row.get("anchor_id") or row.get("anchor") or "").strip()
        if anchor_id:
            bucket["anchors"].add(anchor_id)
        chunk_type = str(row.get("chunk_type") or "unknown").strip() or "unknown"
        bucket["chunk_types"][chunk_type] += 1

    for slug, entry in manifest_by_slug.items():
        grouped.setdefault(
            slug,
            {
                "book_slug": slug,
                "title": str(entry.get("title") or slug),
                "grade": _grade_label(known_books.get(slug, {})) if slug in known_books else "Gold",
                "chunk_count": 0,
                "token_total": 0,
                "command_chunk_count": 0,
                "error_chunk_count": 0,
                "anchors": set(),
                "chunk_types": Counter(),
                "source_type": str(entry.get("source_type") or ""),
                "source_lane": str(entry.get("source_lane") or ""),
                "review_status": str(entry.get("review_status") or ""),
                "updated_at": str(entry.get("updated_at") or ""),
                "viewer_path": str(entry.get("viewer_path") or ""),
                "source_url": str(known_books.get(slug, {}).get("source_url") or entry.get("source_url") or ""),
                "materialized": False,
            },
        )

    items: list[dict[str, Any]] = []
    for entry in grouped.values():
        chunk_types = entry.pop("chunk_types")
        anchors = entry.pop("anchors")
        items.append(
            {
                **entry,
                "anchor_count": len(anchors),
                "chunk_type_breakdown": dict(sorted(chunk_types.items())),
            }
        )
    return sorted(items, key=lambda item: (-int(item["chunk_count"]), str(item["book_slug"])))


def _aggregate_playbooks(
    files: list[Path],
    *,
    manifest_by_slug: dict[str, dict[str, Any]],
    known_books: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for path in files:
        payload = _safe_read_json(path)
        slug = str(payload.get("asset_slug") or payload.get("book_slug") or path.stem).strip()
        if not slug:
            continue
        sections = payload.get("sections")
        if not isinstance(sections, list):
            sections = []
        section_roles = Counter()
        block_kinds = Counter()
        for section in sections:
            if not isinstance(section, dict):
                continue
            role = str(section.get("semantic_role") or "unknown").strip() or "unknown"
            section_roles[role] += 1
            for block in section.get("blocks") or []:
                if not isinstance(block, dict):
                    continue
                block_kind = str(block.get("kind") or "unknown").strip() or "unknown"
                block_kinds[block_kind] += 1
        source_metadata = payload.get("source_metadata") if isinstance(payload.get("source_metadata"), dict) else {}
        playbook_family = str(payload.get("playbook_family") or "").strip()
        source_type = str(
            (
                playbook_family
                if playbook_family in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPE_SET
                else (
                    source_metadata.get("source_type")
                    or payload.get("source_type")
                    or ""
                )
            )
            or ""
        )
        known = known_books.get(slug, {})
        manifest = manifest_by_slug.get(slug, {})
        grouped[slug] = {
            "book_slug": slug,
            "title": str(payload.get("title") or payload.get("book_title") or slug),
            "grade": _grade_label(known) if known else "Gold" if manifest else "Unknown",
            "translation_status": str(payload.get("translation_status") or known.get("content_status") or ""),
            "review_status": str(payload.get("review_status") or known.get("review_status") or ""),
            "source_type": source_type or str(known.get("source_type") or manifest.get("source_type") or ""),
            "source_lane": str(source_metadata.get("source_lane") or known.get("source_lane") or manifest.get("source_lane") or ""),
            "source_collection": str(payload.get("source_collection") or source_metadata.get("source_collection") or ""),
            "section_count": len(sections),
            "anchor_count": len(payload.get("anchor_map") or {}),
            "code_block_count": int(block_kinds.get("code", 0)),
            "procedure_block_count": int(block_kinds.get("procedure", 0)),
            "paragraph_block_count": int(block_kinds.get("paragraph", 0)),
            "semantic_role_breakdown": dict(sorted(section_roles.items())),
            "block_kind_breakdown": dict(sorted(block_kinds.items())),
            "legal_notice_url": str(payload.get("legal_notice_url") or source_metadata.get("legal_notice_url") or ""),
            "viewer_path": str(
                payload.get("target_viewer_path")
                or payload.get("viewer_path")
                or manifest.get("viewer_path")
                or known.get("viewer_path")
                or ""
            ),
            "source_url": str(
                payload.get("source_origin_url")
                or payload.get("source_uri")
                or payload.get("source_url")
                or ""
            ),
            "updated_at": str(source_metadata.get("updated_at") or known.get("updated_at") or manifest.get("updated_at") or ""),
            "materialized": True,
        }

    for slug, entry in manifest_by_slug.items():
        grouped.setdefault(
            slug,
            {
                "book_slug": slug,
                "title": str(entry.get("title") or slug),
                "grade": _grade_label(known_books.get(slug, {})) if slug in known_books else "Gold",
                "translation_status": str(entry.get("content_status") or ""),
                "review_status": str(entry.get("review_status") or ""),
                "source_type": str(entry.get("source_type") or ""),
                "source_lane": str(entry.get("source_lane") or ""),
                "section_count": 0,
                "anchor_count": 0,
                "code_block_count": 0,
                "procedure_block_count": 0,
                "paragraph_block_count": 0,
                "semantic_role_breakdown": {},
                "block_kind_breakdown": {},
                "legal_notice_url": str(entry.get("legal_notice_url") or ""),
                "viewer_path": str(entry.get("viewer_path") or ""),
                "source_url": str(known_books.get(slug, {}).get("source_url") or entry.get("source_url") or ""),
                "updated_at": str(entry.get("updated_at") or ""),
                "materialized": False,
            },
        )

    return sorted(grouped.values(), key=lambda item: (-int(item["section_count"]), str(item["book_slug"])))


def _derived_family_status(
    family: str,
    books: list[dict[str, Any]],
) -> dict[str, Any]:
    slugs = sorted(
        str(book.get("book_slug") or "").strip()
        for book in books
        if str(book.get("book_slug") or "").strip()
    )
    return {
        "family": family,
        "count": len(books),
        "slugs": slugs,
        "status": "materialized" if books else "not_emitted",
        "books": books,
    }


def _library_breakdown(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"key": key, "count": count}
        for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _build_manual_book_library(
    core_manualbooks: list[dict[str, Any]],
    extra_manualbooks: list[dict[str, Any]],
) -> dict[str, Any]:
    books: list[dict[str, Any]] = []
    source_type_counter: Counter[str] = Counter()
    for group_key, group_label, group_books in (
        ("runtime_core", "런타임 팩", core_manualbooks),
        ("extra", "확장 북", extra_manualbooks),
    ):
        for book in group_books:
            item = dict(book)
            item["library_group"] = group_key
            item["library_group_label"] = group_label
            books.append(item)
            source_type_counter[str(item.get("source_type") or "unknown").strip() or "unknown"] += 1
    return {
        "total_count": len(books),
        "core_count": len(core_manualbooks),
        "extra_count": len(extra_manualbooks),
        "books": books,
        "group_breakdown": [
            {"key": "runtime_core", "label": "런타임 팩", "count": len(core_manualbooks)},
            {"key": "extra", "label": "확장 북", "count": len(extra_manualbooks)},
        ],
        "source_type_breakdown": _library_breakdown(source_type_counter),
    }


def _build_playbook_library(
    derived_playbook_family_statuses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    families: list[dict[str, Any]] = []
    books: list[dict[str, Any]] = []
    for family in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPES:
        status = derived_playbook_family_statuses.get(family, {})
        family_books = []
        for book in status.get("books") or []:
            if not isinstance(book, dict):
                continue
            item = dict(book)
            item["family"] = family
            item["family_label"] = PLAYBOOK_LIBRARY_FAMILY_LABELS.get(family, family)
            family_books.append(item)
        families.append(
            {
                "family": family,
                "family_label": PLAYBOOK_LIBRARY_FAMILY_LABELS.get(family, family),
                "count": len(family_books),
                "status": str(status.get("status") or "not_emitted"),
                "books": family_books,
            }
        )
        books.extend(family_books)
    return {
        "total_count": len(books),
        "family_count": sum(1 for family in families if int(family.get("count") or 0) > 0),
        "families": families,
        "books": books,
    }
def _apply_viewer_path_fallback(books: list[dict[str, Any]], *, root: Path) -> list[dict[str, Any]]:
    settings = load_settings(root)
    playbook_dir = settings.playbook_books_dir.resolve()
    for book in books:
        if str(book.get("viewer_path") or "").strip():
            continue
        slug = str(book.get("book_slug") or "").strip()
        if not slug:
            continue
        if (playbook_dir / f"{slug}.json").exists():
            book["viewer_path"] = settings.viewer_path_template.format(slug=slug)
    return books


def build_data_control_room_payload(root_dir: str | Path) -> dict[str, Any]:
    root = Path(root_dir).resolve()
    settings = load_settings(root)

    gate_path = root / "reports" / "build_logs" / "foundry_runs" / "profiles" / "morning_gate" / "latest.json"
    gate_report = _safe_read_json(gate_path)
    verdict = gate_report.get("verdict") if isinstance(gate_report.get("verdict"), dict) else {}
    verdict_summary = verdict.get("summary") if isinstance(verdict.get("summary"), dict) else {}

    manifest = _safe_read_json(settings.source_manifest_path)
    manifest_entries = manifest.get("entries") if isinstance(manifest.get("entries"), list) else []
    manifest_by_slug = {
        str(entry.get("book_slug") or "").strip(): entry
        for entry in manifest_entries
        if isinstance(entry, dict) and str(entry.get("book_slug") or "").strip()
    }
    manifest_slugs = set(manifest_by_slug)
    expected_approved_runtime_count = len(manifest_by_slug)

    source_approval_payload = _job_payload(gate_report, "source_approval")
    gate_source_approval_report_path = _resolve_report_path(
        str(
            ((source_approval_payload.get("output_targets") or {}).get("approval_report_path"))
            or _job_report_path(gate_report, "source_approval")
        )
    )
    source_approval_report_path, source_approval_report = _select_report_candidate(
        gate_source_approval_report_path,
        settings.source_approval_report_path,
        summary_key="approved_ko_count",
        rows_key="books",
        expected_count=expected_approved_runtime_count,
    )

    source_summary = (
        source_approval_report.get("summary")
        if isinstance(source_approval_report.get("summary"), dict)
        else {}
    )
    source_book_count = _safe_int(source_summary.get("book_count") or len(source_approval_report.get("books") or []))
    selected_approved_runtime_count = _safe_int(
        source_summary.get("approved_ko_count")
        or verdict_summary.get("approved_runtime_count")
        or expected_approved_runtime_count
    )

    gate_translation_lane_path = _resolve_report_path(
        str(
            ((source_approval_payload.get("output_targets") or {}).get("translation_lane_report_path"))
            or _job_report_path(gate_report, "synthesis_lane")
        )
    )
    translation_lane_path, translation_lane_report = _select_report_candidate(
        gate_translation_lane_path,
        settings.translation_lane_report_path,
        summary_key="active_queue_count",
        rows_key="active_queue",
        expected_count=max(source_book_count - selected_approved_runtime_count, 0),
    )
    source_bundle_quality_payload = _job_payload(gate_report, "source_bundle_quality")

    retrieval_report = _safe_read_json(settings.retrieval_eval_report_path)
    answer_report = _safe_read_json(settings.answer_eval_report_path)
    ragas_report = _safe_read_json(settings.ragas_eval_report_path)
    runtime_report = _safe_read_json(settings.runtime_report_path)
    runtime_smoke_payload = _job_payload(gate_report, "runtime_smoke")

    source_books = source_approval_report.get("books") if isinstance(source_approval_report.get("books"), list) else []
    known_books = {
        str(book.get("book_slug") or "").strip(): book
        for book in source_books
        if isinstance(book, dict) and str(book.get("book_slug") or "").strip()
    }
    active_queue = translation_lane_report.get("active_queue") if isinstance(translation_lane_report.get("active_queue"), list) else []
    known_book_rows = _build_known_books_section(source_books, manifest_by_slug=manifest_by_slug)
    active_queue_rows = [_simplify_book(book) for book in active_queue if isinstance(book, dict)]
    high_value_focus = _build_high_value_focus(
        source_bundle_quality_payload,
        known_books=known_books,
        manifest_by_slug=manifest_by_slug,
    )

    selected_chunks_path, chunk_rows, chunk_candidates = _candidate_file_rows(
        settings.chunks_path,
        settings.chunks_path,
    )
    selected_playbook_dir, playbook_files, playbook_candidates = _candidate_playbook_dirs(
        *settings.playbook_book_dirs,
        expected_count=len(manifest_by_slug),
    )
    customer_pack_files = sorted(settings.customer_pack_books_dir.glob("*.json"))
    customer_pack_draft_records = {
        record.draft_id: record
        for record in CustomerPackDraftStore(root).list()
        if str(record.draft_id or "").strip()
    }
    all_playbook_files: list[Path] = []
    seen_playbook_paths: set[str] = set()
    for path in [*playbook_files, *customer_pack_files]:
        normalized_path = str(path)
        if normalized_path in seen_playbook_paths:
            continue
        seen_playbook_paths.add(normalized_path)
        all_playbook_files.append(path)

    corpus_books = _aggregate_corpus_books(
        chunk_rows,
        manifest_by_slug=manifest_by_slug,
        known_books=known_books,
    )
    manualbooks = _aggregate_playbooks(
        all_playbook_files,
        manifest_by_slug=manifest_by_slug,
        known_books=known_books,
    )
    manualbooks = _apply_customer_pack_runtime_truth(
        manualbooks,
        draft_records_by_id=customer_pack_draft_records,
    )
    derived_playbook_family_statuses = {
        family: _derived_family_status(
            family,
            [
                book
                for book in manualbooks
                if str(book.get("source_type") or "").strip() == family
            ],
        )
        for family in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPES
    }
    derived_playbooks = [
        book
        for family in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPES
        for book in derived_playbook_family_statuses[family]["books"]
    ]
    core_corpus_books = [
        book
        for book in corpus_books
        if str(book.get("book_slug") or "").strip() in manifest_slugs
    ]
    extra_corpus_books = [
        book
        for book in corpus_books
        if str(book.get("book_slug") or "").strip() not in manifest_slugs
    ]
    topic_playbooks = _apply_viewer_path_fallback(
        list(derived_playbook_family_statuses[TOPIC_PLAYBOOK_SOURCE_TYPE]["books"]),
        root=root,
    )
    operation_playbooks = _apply_viewer_path_fallback(
        list(
        derived_playbook_family_statuses[OPERATION_PLAYBOOK_SOURCE_TYPE]["books"]
        ),
        root=root,
    )
    troubleshooting_playbooks = _apply_viewer_path_fallback(
        list(
        derived_playbook_family_statuses[TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE]["books"]
        ),
        root=root,
    )
    policy_overlay_books = _apply_viewer_path_fallback(
        list(
        derived_playbook_family_statuses[POLICY_OVERLAY_BOOK_SOURCE_TYPE]["books"]
        ),
        root=root,
    )
    synthesized_playbooks = _apply_viewer_path_fallback(
        list(
        derived_playbook_family_statuses[SYNTHESIZED_PLAYBOOK_SOURCE_TYPE]["books"]
        ),
        root=root,
    )
    core_manualbooks = [
        book
        for book in manualbooks
        if str(book.get("source_type") or "").strip() not in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPE_SET
        and str(book.get("book_slug") or "").strip() in manifest_slugs
    ]
    extra_manualbooks = [
        book
        for book in manualbooks
        if str(book.get("source_type") or "").strip() not in DATA_CONTROL_ROOM_DERIVED_PLAYBOOK_SOURCE_TYPE_SET
        and str(book.get("book_slug") or "").strip() not in manifest_slugs
    ]
    user_library_books = _apply_viewer_path_fallback(
        [
            book
            for book in extra_manualbooks
            if str(book.get("boundary_truth") or "").strip() == "private_customer_pack_runtime"
            or str(book.get("source_lane") or "").strip() == "customer_source_first_pack"
        ],
        root=root,
    )
    customer_pack_runtime_books = _apply_viewer_path_fallback(
        [
            book
            for book in manualbooks
            if str(book.get("boundary_truth") or "").strip() == "private_customer_pack_runtime"
            or str(book.get("source_lane") or "").strip() == "customer_source_first_pack"
        ],
        root=root,
    )

    grade_breakdown_counter = Counter(_grade_label(book) for book in source_books)
    gold_books = [
        _simplify_book(book)
        for slug in manifest_by_slug
        for book in [known_books.get(slug)]
        if isinstance(book, dict) and _is_gold_book(book)
    ]
    materialized_corpus_slugs = {
        str(row.get("book_slug") or "").strip()
        for row in chunk_rows
        if str(row.get("book_slug") or "").strip()
    }
    materialized_core_corpus_slugs = materialized_corpus_slugs & manifest_slugs
    extra_materialized_corpus_slugs = materialized_corpus_slugs - manifest_slugs
    materialized_topic_playbook_slugs = set(derived_playbook_family_statuses[TOPIC_PLAYBOOK_SOURCE_TYPE]["slugs"])
    materialized_operation_playbook_slugs = set(
        derived_playbook_family_statuses[OPERATION_PLAYBOOK_SOURCE_TYPE]["slugs"]
    )
    materialized_troubleshooting_playbook_slugs = set(
        derived_playbook_family_statuses[TROUBLESHOOTING_PLAYBOOK_SOURCE_TYPE]["slugs"]
    )
    materialized_policy_overlay_book_slugs = set(
        derived_playbook_family_statuses[POLICY_OVERLAY_BOOK_SOURCE_TYPE]["slugs"]
    )
    materialized_synthesized_playbook_slugs = set(
        derived_playbook_family_statuses[SYNTHESIZED_PLAYBOOK_SOURCE_TYPE]["slugs"]
    )
    materialized_derived_playbook_slugs = (
        materialized_topic_playbook_slugs
        | materialized_operation_playbook_slugs
        | materialized_troubleshooting_playbook_slugs
        | materialized_policy_overlay_book_slugs
        | materialized_synthesized_playbook_slugs
    )
    materialized_manualbook_slugs = {
        path.stem
        for path in all_playbook_files
        if path.stem not in materialized_derived_playbook_slugs
    }
    materialized_core_manualbook_slugs = materialized_manualbook_slugs & manifest_slugs
    extra_materialized_manualbook_slugs = materialized_manualbook_slugs - manifest_slugs
    buyer_scope = (
        source_bundle_quality_payload.get("buyer_scope")
        if isinstance(source_bundle_quality_payload.get("buyer_scope"), dict)
        else {}
    )
    raw_manual_count = int(buyer_scope.get("raw_manual_count") or len(manifest_by_slug))
    playable_asset_count = (
        len(core_manualbooks)
        + len(extra_manualbooks)
        + len(derived_playbooks)
    )
    playable_asset_multiplication = {
        "raw_manual_count": raw_manual_count,
        "playable_asset_count": playable_asset_count,
        "delta_vs_raw_manual_count": playable_asset_count - raw_manual_count,
        "ratio_vs_raw_manual_count": (
            round(playable_asset_count / raw_manual_count, 4)
            if raw_manual_count > 0
            else 0.0
        ),
    }
    manual_book_library = _build_manual_book_library(core_manualbooks, extra_manualbooks)
    playbook_library = _build_playbook_library(derived_playbook_family_statuses)
    gold_candidate_books = _build_gold_candidate_book_bucket(root)
    approved_wiki_runtime_books = _build_approved_wiki_runtime_book_bucket(
        root,
        translation_lane_report=translation_lane_report,
    )
    navigation_backlog = _build_navigation_backlog_bucket(root)
    wiki_usage_signals = _build_wiki_usage_signal_bucket(root)
    product_gate = _build_product_gate_bucket(root)
    product_rehearsal = _build_product_rehearsal_summary(root)
    buyer_packet_bundle = _build_buyer_packet_bundle_bucket(root)
    release_candidate_freeze = _build_release_candidate_freeze_summary(root)

    chunk_candidate_counts = {
        candidate["row_count"]
        for candidate in chunk_candidates
        if candidate.get("exists")
    }
    playbook_candidate_counts = {
        candidate["file_count"]
        for candidate in playbook_candidates
        if candidate.get("exists")
    }
    canonical_grade_source = {
        "name": "source_approval_report",
        "path": str(source_approval_report_path or ""),
        "exists": bool(source_approval_report_path and source_approval_report_path.exists()),
        "rule": "Source approval report is the canonical grade source for approved_ko / translated_ko_draft / blocked classification.",
        "summary": source_approval_report.get("summary") if isinstance(source_approval_report.get("summary"), dict) else {},
    }
    source_of_truth_drift = _build_source_of_truth_drift(
        gate_report=gate_report,
        source_approval_report=source_approval_report,
        translation_lane_report=translation_lane_report,
        manifest_path=settings.source_manifest_path,
        selected_chunks_path=selected_chunks_path,
        chunk_candidates=chunk_candidates,
        selected_playbook_dir=selected_playbook_dir,
        playbook_candidates=playbook_candidates,
        source_approval_report_path=source_approval_report_path,
        translation_lane_path=translation_lane_path,
    )

    answer_overall = answer_report.get("overall") if isinstance(answer_report.get("overall"), dict) else {}
    ragas_overall = ragas_report.get("overall") if isinstance(ragas_report.get("overall"), dict) else {}
    runtime_app = runtime_report.get("app") if isinstance(runtime_report.get("app"), dict) else {}
    runtime_runtime = runtime_report.get("runtime") if isinstance(runtime_report.get("runtime"), dict) else {}
    runtime_probes = runtime_report.get("probes") if isinstance(runtime_report.get("probes"), dict) else {}

    report_paths = {
        "gate": str(gate_path),
        "source_approval": str(source_approval_report_path or ""),
        "translation_lane": str(translation_lane_path or ""),
        "retrieval_eval": str(settings.retrieval_eval_report_path),
        "answer_eval": str(settings.answer_eval_report_path),
        "ragas_eval": str(settings.ragas_eval_report_path),
        "runtime": str(settings.runtime_report_path),
    }

    report_snapshots = {
        "morning_gate": _path_snapshot(gate_path),
        "source_approval": _path_snapshot_for_optional(source_approval_report_path),
        "translation_lane": _path_snapshot_for_optional(translation_lane_path),
        "retrieval_eval": _path_snapshot(settings.retrieval_eval_report_path),
        "answer_eval": _path_snapshot(settings.answer_eval_report_path),
        "ragas_eval": _path_snapshot(settings.ragas_eval_report_path),
        "runtime_report": _path_snapshot(settings.runtime_report_path),
    }

    return {
        "generated_at": _iso_now(),
        "active_pack": {
            "app_id": settings.app_id,
            "app_label": settings.app_label,
            "pack_id": settings.active_pack_id,
            "pack_label": settings.active_pack_label,
            "ocp_version": settings.ocp_version,
            "docs_language": settings.docs_language,
            "viewer_path_prefix": settings.viewer_path_prefix,
        },
        "summary": {
            "gate_status": str(verdict.get("status") or "unknown"),
            "release_blocking": bool(verdict.get("release_blocking")),
            "approved_runtime_count": selected_approved_runtime_count,
            "known_book_count": int(source_approval_report.get("summary", {}).get("book_count") or len(source_books)),
            "gold_book_count": len(gold_books),
            "known_books_count": len(known_book_rows),
            "queue_count": len(active_queue_rows),
            "active_queue_count": len(active_queue_rows),
            "high_value_focus_count": int(high_value_focus.get("count") or 0),
            "blocked_count": int(source_approval_report.get("summary", {}).get("blocked_count") or 0),
            "raw_manual_count": raw_manual_count,
            "chunk_count": len(chunk_rows),
            "corpus_book_count": len(materialized_core_corpus_slugs),
            "core_corpus_book_count": len(materialized_core_corpus_slugs),
            "manualbook_count": len(materialized_core_manualbook_slugs),
            "core_manualbook_count": len(materialized_core_manualbook_slugs),
            "customer_pack_runtime_book_count": len(customer_pack_runtime_books),
            "user_library_book_count": len(user_library_books),
            "gold_candidate_book_count": len(gold_candidate_books.get("books") or []),
            "approved_wiki_runtime_book_count": len(approved_wiki_runtime_books.get("books") or []),
            "wiki_navigation_backlog_count": len(navigation_backlog.get("books") or []),
            "wiki_usage_signal_count": len(wiki_usage_signals.get("books") or []),
            "product_gate_count": len(product_gate.get("books") or []),
            "buyer_packet_bundle_count": len(buyer_packet_bundle.get("books") or []),
            "release_candidate_freeze_ready": bool(release_candidate_freeze.get("exists")),
            "product_gate_pass_rate": product_rehearsal.get("critical_scenario_pass_rate"),
            "topic_playbook_count": len(topic_playbooks),
            "operation_playbook_count": len(operation_playbooks),
            "troubleshooting_playbook_count": len(troubleshooting_playbooks),
            "policy_overlay_book_count": len(policy_overlay_books),
            "synthesized_playbook_count": len(synthesized_playbooks),
            "derived_playbook_count": len(derived_playbooks),
            "playable_asset_count": playable_asset_count,
            "extra_corpus_book_count": len(extra_materialized_corpus_slugs),
            "extra_manualbook_count": len(extra_materialized_manualbook_slugs),
            "retrieval_hit_at_1": retrieval_report.get("overall", {}).get("book_hit_at_1"),
            "answer_pass_rate": answer_overall.get("pass_rate"),
            "citation_precision": answer_overall.get("avg_citation_precision"),
            "ragas_faithfulness": ragas_overall.get("faithfulness"),
            "canonical_grade_source": canonical_grade_source["name"],
        },
        "gate": {
            "path": str(gate_path),
            "run_at": str(gate_report.get("run_at") or ""),
            "status": str(verdict.get("status") or "unknown"),
            "release_blocking": bool(verdict.get("release_blocking")),
            "reasons": list(verdict.get("reasons") or []),
            "summary": {
                "approved_runtime_count": int(verdict_summary.get("approved_runtime_count") or len(manifest_by_slug)),
                "translation_ready_count": int(verdict_summary.get("translation_ready_count") or 0),
                "manual_review_ready_count": int(verdict_summary.get("manual_review_ready_count") or 0),
                "high_value_issue_count": int(verdict_summary.get("high_value_issue_count") or 0),
                "source_expansion_needed_count": int(verdict_summary.get("source_expansion_needed_count") or 0),
                "failed_validation_checks": list(verdict_summary.get("failed_validation_checks") or []),
                "failed_data_quality_checks": list(verdict_summary.get("failed_data_quality_checks") or []),
            },
        },
        "grading": {
            "summary": source_approval_report.get("summary") if isinstance(source_approval_report.get("summary"), dict) else {},
            "grade_breakdown": [
                {"grade": grade, "count": count}
                for grade, count in sorted(grade_breakdown_counter.items(), key=lambda item: (-item[1], item[0]))
            ],
            "gold_books": gold_books,
            "queue_books": active_queue_rows,
        },
        "evaluations": {
            "retrieval": {
                **_summarize_eval(retrieval_report),
                "path": str(settings.retrieval_eval_report_path),
            },
            "answer": {
                **_summarize_eval(answer_report),
                "path": str(settings.answer_eval_report_path),
            },
            "ragas": {
                **_summarize_eval(ragas_report),
                "path": str(settings.ragas_eval_report_path),
            },
            "runtime": {
                "path": str(settings.runtime_report_path),
                "app": runtime_app,
                "runtime": runtime_runtime,
                "probes": runtime_probes,
                "latest_smoke": runtime_smoke_payload,
            },
        },
        "source_of_truth": {
            "artifacts_dir": str(settings.artifacts_dir),
            "manifest": _path_snapshot(settings.source_manifest_path),
            "chunks": {
                "selected_path": str(selected_chunks_path) if selected_chunks_path else "",
                "candidates": chunk_candidates,
                "drift_detected": len(chunk_candidate_counts) > 1,
            },
            "playbooks": {
                "selected_dir": str(selected_playbook_dir) if selected_playbook_dir else "",
                "candidates": playbook_candidates,
                "drift_detected": len(playbook_candidate_counts) > 1,
            },
        },
        "canonical_grade_source": canonical_grade_source,
        "source_of_truth_drift": source_of_truth_drift,
        "corpus": {
            "selected_path": str(selected_chunks_path) if selected_chunks_path else "",
            "books": core_corpus_books,
        },
        "manualbooks": {
            "selected_dir": str(selected_playbook_dir) if selected_playbook_dir else "",
            "books": core_manualbooks,
        },
        "customer_pack_runtime_books": {
            "selected_dir": str(settings.customer_pack_books_dir.resolve()),
            "books": customer_pack_runtime_books,
        },
        "user_library_books": {
            "selected_dir": str(settings.customer_pack_books_dir.resolve()),
            "books": user_library_books,
        },
        "gold_candidate_books": gold_candidate_books,
        "approved_wiki_runtime_books": approved_wiki_runtime_books,
        "wiki_navigation_backlog": navigation_backlog,
        "wiki_usage_signals": wiki_usage_signals,
        "product_gate": product_gate,
        "buyer_packet_bundle": buyer_packet_bundle,
        "release_candidate_freeze": release_candidate_freeze,
        "product_rehearsal": product_rehearsal,
        "manual_book_library": manual_book_library,
        "topic_playbooks": {
            "selected_dir": str(selected_playbook_dir) if selected_playbook_dir else "",
            "books": topic_playbooks,
        },
        "operation_playbooks": {
            "selected_dir": str(selected_playbook_dir) if selected_playbook_dir else "",
            "books": operation_playbooks,
        },
        "troubleshooting_playbooks": {
            "selected_dir": str(selected_playbook_dir) if selected_playbook_dir else "",
            "books": troubleshooting_playbooks,
        },
        "policy_overlay_books": {
            "selected_dir": str(selected_playbook_dir) if selected_playbook_dir else "",
            "books": policy_overlay_books,
        },
        "synthesized_playbooks": {
            "selected_dir": str(selected_playbook_dir) if selected_playbook_dir else "",
            "books": synthesized_playbooks,
        },
        "derived_playbook_families": derived_playbook_family_statuses,
        "playbook_library": playbook_library,
        "materialization": {
            "manifest_book_count": len(manifest_by_slug),
            "gold_book_count": len(gold_books),
            "corpus_book_count": len(core_corpus_books),
            "core_corpus_book_count": len(core_corpus_books),
            "manualbook_book_count": len(core_manualbooks),
            "core_manualbook_book_count": len(core_manualbooks),
            "customer_pack_runtime_book_count": len(customer_pack_runtime_books),
            "user_library_book_count": len(user_library_books),
            "topic_playbook_book_count": len(topic_playbooks),
            "operation_playbook_book_count": len(operation_playbooks),
            "troubleshooting_playbook_book_count": len(troubleshooting_playbooks),
            "policy_overlay_book_book_count": len(policy_overlay_books),
            "synthesized_playbook_book_count": len(synthesized_playbooks),
            "derived_playbook_book_count": len(derived_playbooks),
            "playable_asset_count": playable_asset_count,
            "playable_asset_multiplication": playable_asset_multiplication,
            "extra_corpus_book_count": len(extra_corpus_books),
            "extra_manualbook_book_count": len(extra_manualbooks),
            "materialized_corpus_book_count": len(materialized_core_corpus_slugs),
            "materialized_manualbook_book_count": len(materialized_core_manualbook_slugs),
            "materialized_topic_playbook_count": len(materialized_topic_playbook_slugs),
            "materialized_operation_playbook_count": len(materialized_operation_playbook_slugs),
            "materialized_troubleshooting_playbook_count": len(materialized_troubleshooting_playbook_slugs),
            "materialized_policy_overlay_book_count": len(materialized_policy_overlay_book_slugs),
            "materialized_synthesized_playbook_count": len(materialized_synthesized_playbook_slugs),
            "materialized_derived_playbook_count": len(materialized_derived_playbook_slugs),
            "extra_corpus_books": sorted(extra_materialized_corpus_slugs),
            "extra_manualbook_books": sorted(extra_materialized_manualbook_slugs),
            "missing_corpus_books": sorted(manifest_slugs - materialized_core_corpus_slugs),
            "missing_manualbook_books": sorted(manifest_slugs - materialized_core_manualbook_slugs),
            "logical_counts_match": (
                len(manifest_by_slug) == len(core_corpus_books) == len(core_manualbooks)
            ),
            "counts_match": (
                len(manifest_by_slug)
                == len(gold_books)
                == len(materialized_core_corpus_slugs)
                == len(materialized_core_manualbook_slugs)
            ),
        },
        "known_books": known_book_rows,
        "active_queue": active_queue_rows,
        "high_value_focus": high_value_focus,
        "report_paths": report_paths,
        "gold_books": gold_books,
        "corpus_book_status": core_corpus_books,
        "extra_corpus_book_status": extra_corpus_books,
        "manualbook_status": core_manualbooks,
        "extra_manualbook_status": extra_manualbooks,
        "topic_playbook_status": topic_playbooks,
        "operation_playbook_status": operation_playbooks,
        "troubleshooting_playbook_status": troubleshooting_playbooks,
        "policy_overlay_book_status": policy_overlay_books,
        "synthesized_playbook_status": synthesized_playbooks,
        "recent_report_paths": report_snapshots,
        "reports": {
            "gate": {
                "status": str(verdict.get("status") or "unknown"),
                "summary": verdict_summary,
            },
            "source_approval": {
                "path": str(source_approval_report_path or ""),
                "summary": source_approval_report.get("summary") if isinstance(source_approval_report.get("summary"), dict) else {},
            },
            "translation_lane": {
                "path": str(translation_lane_path or ""),
                "summary": translation_lane_report.get("summary") if isinstance(translation_lane_report.get("summary"), dict) else {},
            },
            "retrieval": _summarize_eval(retrieval_report),
            "answer": _summarize_eval(answer_report),
            "ragas": _summarize_eval(ragas_report),
            "runtime": runtime_smoke_payload,
        },
    }
