"""bucket builders for the data control room payload."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from play_book_studio.config.settings import load_settings
from play_book_studio.runtime_catalog_registry import official_runtime_books

from .wiki_user_overlay import build_wiki_overlay_signal_payload


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _safe_read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists() or not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_read_yaml(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists() or not path.is_file():
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: Any) -> float | None:
    try:
        if value in ("", None):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _markdown_heading_count(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        normalized = line.strip()
        if normalized.startswith("## "):
            count += 1
    return count


def _markdown_code_block_count(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    fence_count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("```"))
    return fence_count // 2


def _build_gold_candidate_book_bucket(root: Path) -> dict[str, Any]:
    manifest_path = root / "data" / "gold_candidate_books" / "full_rebuild_manifest.json"
    return {
        "selected_dir": "",
        "books": [],
        "manifest_path": str(manifest_path.resolve()),
        "surface_policy": "hidden_from_latest_only_surface",
    }


def _translation_runtime_blocked_slugs(translation_lane_report: dict[str, Any]) -> set[str]:
    active_queue = (
        translation_lane_report.get("active_queue")
        if isinstance(translation_lane_report.get("active_queue"), list)
        else []
    )
    blocked: set[str] = set()
    for row in active_queue:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("book_slug") or "").strip()
        lane = row.get("translation_lane") if isinstance(row.get("translation_lane"), dict) else {}
        if not slug:
            continue
        if lane and not bool(lane.get("runtime_eligible")):
            blocked.add(slug)
    return blocked


def _build_approved_wiki_runtime_book_bucket(root: Path, *, translation_lane_report: dict[str, Any]) -> dict[str, Any]:
    manifest_path = root / "data" / "wiki_runtime_books" / "active_manifest.json"
    blocked_slugs = _translation_runtime_blocked_slugs(translation_lane_report)
    books: list[dict[str, Any]] = []
    runtime_paths: list[Path] = []
    hidden_books: list[dict[str, Any]] = []
    for entry in official_runtime_books(root):
        slug = str(entry.get("book_slug") or "").strip()
        if not slug:
            continue
        runtime_path_value = str(entry.get("runtime_path") or "").strip()
        runtime_path = Path(runtime_path_value).resolve() if runtime_path_value else None
        if slug in blocked_slugs:
            hidden_books.append(
                {
                    "book_slug": slug,
                    "title": str(entry.get("title") or slug),
                    "hidden_reason": "translated_ko_draft_runtime_ineligible",
                }
            )
            continue
        section_count = int(entry.get("section_count") or 0)
        code_block_count = int(entry.get("code_block_count") or 0)
        if runtime_path is not None and runtime_path.exists() and runtime_path.is_file():
            runtime_paths.append(runtime_path)
            section_count = max(section_count, _markdown_heading_count(runtime_path))
            code_block_count = max(code_block_count, _markdown_code_block_count(runtime_path))
        books.append(
            {
                "book_slug": slug,
                "title": str(entry.get("title") or slug),
                "grade": "Approved Wiki Runtime",
                "review_status": "approved_wiki_runtime",
                "source_type": str(entry.get("source_type") or "reader_grade_md"),
                "source_lane": str(entry.get("source_lane") or "approved_wiki_runtime"),
                "section_count": section_count,
                "code_block_count": code_block_count,
                "viewer_path": str(entry.get("viewer_path") or entry.get("docs_viewer_path") or ""),
                "source_url": str(entry.get("source_url") or entry.get("source_candidate_path") or ""),
                "updated_at": str(entry.get("updated_at") or ""),
            }
        )
    if runtime_paths:
        parents = {str(path.parent) for path in runtime_paths}
        selected_dir = sorted(parents)[0] if len(parents) == 1 else str((root / "data" / "wiki_runtime_books").resolve())
    else:
        selected_dir = str((root / "data" / "wiki_runtime_books").resolve())
    return {
        "selected_dir": selected_dir,
        "books": books,
        "manifest_path": str(manifest_path.resolve()),
        "hidden_books": hidden_books,
        "hidden_count": len(hidden_books),
    }


def _build_navigation_backlog_bucket(root: Path) -> dict[str, Any]:
    asset_path = root / "data" / "wiki_relations" / "navigation_backlog.json"
    asset = _safe_read_json(asset_path)
    entries = asset.get("entries") if isinstance(asset.get("entries"), list) else []
    books: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        signal_id = str(entry.get("signal_id") or "").strip()
        label = str(entry.get("label") or signal_id or "Backlog Signal").strip()
        signal_type = str(entry.get("signal_type") or "unknown").strip()
        href = str(entry.get("href") or "").strip()
        books.append(
            {
                "book_slug": signal_id or label.lower().replace(" ", "-"),
                "title": label,
                "grade": "Navigation Backlog",
                "review_status": signal_type,
                "source_type": "chat_navigation_signal",
                "source_lane": "wiki_navigation_backlog",
                "section_count": _safe_int(entry.get("count")),
                "code_block_count": 0,
                "viewer_path": href,
                "source_url": str(asset_path.resolve()),
                "updated_at": str(asset.get("generated_at") or ""),
            }
        )
    return {
        "selected_dir": str((root / "data" / "wiki_relations").resolve()),
        "books": books,
        "manifest_path": str(asset_path.resolve()),
    }


def _build_wiki_usage_signal_bucket(root: Path) -> dict[str, Any]:
    payload = build_wiki_overlay_signal_payload(root)
    top_targets = payload.get("top_targets") if isinstance(payload.get("top_targets"), list) else []
    books: list[dict[str, Any]] = []
    for index, entry in enumerate(top_targets):
        if not isinstance(entry, dict):
            continue
        target_ref = str(entry.get("target_ref") or "").strip()
        title = str(entry.get("title") or target_ref or f"signal-{index + 1}").strip()
        kind = str(entry.get("primary_kind") or entry.get("target_kind") or "signal").strip()
        books.append(
            {
                "book_slug": target_ref.replace(":", "-").replace("#", "-") or f"signal-{index + 1}",
                "title": title,
                "grade": "Wiki Usage Signal",
                "review_status": f"{kind} · {int(entry.get('count') or 0)}",
                "source_type": "wiki_user_overlay_signal",
                "source_lane": "wiki_usage_signals",
                "section_count": int(entry.get("count") or 0),
                "code_block_count": int(entry.get("user_count") or 0),
                "viewer_path": str(entry.get("viewer_path") or ""),
                "source_url": "",
                "updated_at": str(entry.get("last_touched_at") or payload.get("updated_at") or ""),
            }
        )
    runtime_dir = load_settings(root).runtime_dir / "wiki_overlays"
    return {
        "selected_dir": str(runtime_dir.resolve()),
        "books": books,
        "manifest_path": str((runtime_dir / "overlays.json").resolve()),
        "summary": payload.get("summary") if isinstance(payload.get("summary"), dict) else {},
    }


def _build_product_gate_bucket(root: Path) -> dict[str, Any]:
    scorecard_path = root / "PRODUCT_GATE_SCORECARD.yaml"
    scorecard = _safe_read_yaml(scorecard_path)
    promotion_gate = (
        scorecard.get("promotion_gate", {}).get("full_sale_requires", [])
        if isinstance(scorecard.get("promotion_gate"), dict)
        else []
    )
    release_blockers = scorecard.get("release_blockers", [])
    scenario_set = scorecard.get("scenario_set", [])

    books = [
        {
            "book_slug": "product_gate__promotion",
            "title": "Full-Sale Promotion Gate",
            "grade": "Gate",
            "review_status": "locked",
            "source_type": "scorecard_gate",
            "source_lane": "product_gate",
            "section_count": len(promotion_gate),
            "code_block_count": 0,
            "viewer_path": "",
            "source_url": str(scorecard_path.resolve()),
            "updated_at": _iso_now(),
            "boundary_badge": "Promotion Gate",
            "runtime_truth_label": f"{len(promotion_gate)} release requirements",
            "approval_state": "full_sale",
            "publication_state": "criteria",
        },
        {
            "book_slug": "product_gate__blockers",
            "title": "Release Blockers",
            "grade": "Gate",
            "review_status": "blocking",
            "source_type": "scorecard_gate",
            "source_lane": "product_gate",
            "section_count": len(release_blockers),
            "code_block_count": 0,
            "viewer_path": "",
            "source_url": str(scorecard_path.resolve()),
            "updated_at": _iso_now(),
            "boundary_badge": "Blockers",
            "runtime_truth_label": f"{len(release_blockers)} hard blockers",
            "approval_state": "release",
            "publication_state": "blocking",
        },
        {
            "book_slug": "product_gate__scenarios",
            "title": "Product Gate Scenarios",
            "grade": "Gate",
            "review_status": "scored",
            "source_type": "scorecard_gate",
            "source_lane": "product_gate",
            "section_count": len(scenario_set),
            "code_block_count": 0,
            "viewer_path": "",
            "source_url": str(scorecard_path.resolve()),
            "updated_at": _iso_now(),
            "boundary_badge": "Product Gate",
            "runtime_truth_label": f"{len(scenario_set)} product scenarios",
            "approval_state": "product_gate",
            "publication_state": str(scorecard.get("current_stage") or "paid_poc_candidate"),
        },
    ]
    return {
        "selected_dir": str(scorecard_path.resolve()),
        "books": books,
        "manifest_path": str(scorecard_path.resolve()),
        "summary": {
            "promotion_requirement_count": len(promotion_gate),
            "release_blocker_count": len(release_blockers),
            "scenario_count": len(scenario_set),
            "current_stage": str(scorecard.get("current_stage") or ""),
        },
    }


def _build_product_rehearsal_summary(root: Path) -> dict[str, Any]:
    report_path = root / "reports" / "build_logs" / "product_rehearsal_report.json"
    payload = _safe_read_json(report_path)
    pass_rate = _safe_float(payload.get("critical_scenario_pass_rate"))
    return {
        "report_path": str(report_path.resolve()),
        "exists": report_path.exists() and bool(payload),
        "status": str(payload.get("status") or ("missing" if not payload else "unknown")),
        "current_stage": str(payload.get("current_stage") or ""),
        "scenario_count": _safe_int(payload.get("scenario_count")),
        "pass_count": _safe_int(payload.get("pass_count")),
        "critical_scenario_pass_rate": pass_rate,
        "blockers": list(payload.get("blockers") or []),
    }


def _build_buyer_packet_bundle_bucket(root: Path) -> dict[str, Any]:
    bundle_path = root / "reports" / "build_logs" / "buyer_packet_bundle_index.json"
    payload = _safe_read_json(bundle_path)
    packets = payload.get("packets") if isinstance(payload.get("packets"), list) else []
    books: list[dict[str, Any]] = []
    for entry in packets:
        if not isinstance(entry, dict):
            continue
        packet_id = str(entry.get("id") or "").strip()
        books.append(
            {
                "book_slug": f"buyer_packet__{packet_id}",
                "title": str(entry.get("title") or packet_id),
                "grade": "Packet",
                "review_status": "ready" if str(entry.get("status") or "") == "ok" else "pending",
                "source_type": "buyer_packet_bundle",
                "source_lane": "buyer_packet_bundle",
                "section_count": 1,
                "code_block_count": 0,
                "viewer_path": f"/buyer-packets/{packet_id}",
                "source_url": str(entry.get("markdown_path") or ""),
                "updated_at": _iso_now(),
                "boundary_badge": "Release Packet",
                "runtime_truth_label": str(entry.get("purpose") or ""),
                "approval_state": str(payload.get("current_stage") or ""),
                "publication_state": "ready" if str(entry.get("status") or "") == "ok" else "pending",
            }
        )
    return {
        "selected_dir": str(bundle_path.resolve()),
        "books": books,
        "manifest_path": str(bundle_path.resolve()),
        "summary": {
            "packet_count": len(books),
            "all_ready": bool(payload.get("all_ready")),
        },
    }


def _build_release_candidate_freeze_summary(root: Path) -> dict[str, Any]:
    freeze_path = root / "reports" / "build_logs" / "release_candidate_freeze_packet.json"
    payload = _safe_read_json(freeze_path)
    runtime_snapshot = payload.get("runtime_snapshot") if isinstance(payload.get("runtime_snapshot"), dict) else {}
    product_gate = payload.get("product_gate") if isinstance(payload.get("product_gate"), dict) else {}
    release_gate = payload.get("release_gate") if isinstance(payload.get("release_gate"), dict) else {}
    product_gate_pass_rate = _safe_float(
        product_gate.get("pass_rate")
        if "pass_rate" in product_gate
        else product_gate.get("critical_scenario_pass_rate")
    )
    return {
        "packet_id": "release-candidate-freeze",
        "title": str(payload.get("title") or "Release Candidate Freeze Packet"),
        "viewer_path": "/buyer-packets/release-candidate-freeze",
        "freeze_date": str(payload.get("freeze_date") or ""),
        "current_stage": str(payload.get("current_stage") or ""),
        "commercial_truth": str(payload.get("commercial_truth") or ""),
        "runtime_count": _safe_int(runtime_snapshot.get("runtime_count")),
        "active_group": str(runtime_snapshot.get("active_group") or ""),
        "product_gate_pass_rate": product_gate_pass_rate,
        "product_gate_pass_count": _safe_int(product_gate.get("pass_count")),
        "product_gate_scenario_count": _safe_int(product_gate.get("scenario_count")),
        "promotion_gate_count": _safe_int(release_gate.get("promotion_gate_count")),
        "release_blocker_count": _safe_int(release_gate.get("release_blocker_count")),
        "sell_now": str(release_gate.get("sell_now") or ""),
        "do_not_sell_yet": str(release_gate.get("do_not_sell_yet") or ""),
        "close": str(payload.get("close") or ""),
        "exists": freeze_path.exists() and bool(payload),
        "report_path": str(freeze_path.resolve()),
    }


__all__ = [
    "_build_approved_wiki_runtime_book_bucket",
    "_build_product_gate_bucket",
    "_build_buyer_packet_bundle_bucket",
    "_build_gold_candidate_book_bucket",
    "_build_navigation_backlog_bucket",
    "_build_product_rehearsal_summary",
    "_build_release_candidate_freeze_summary",
    "_build_wiki_usage_signal_bucket",
    "_iso_now",
    "_safe_int",
    "_safe_read_json",
    "_safe_read_yaml",
]
