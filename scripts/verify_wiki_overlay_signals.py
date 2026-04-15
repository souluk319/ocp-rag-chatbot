from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.data_control_room import build_data_control_room_payload
from play_book_studio.app.wiki_user_overlay import (
    build_wiki_overlay_signal_payload,
    remove_wiki_user_overlay,
    save_wiki_user_overlay,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "build_logs" / "wiki_overlay_usage_signals_report.json"
SMOKE_USER = "smoke-overlay-signals"


def _sample_section_payload() -> dict[str, str]:
    payload = json.loads(
        (ROOT / "data" / "wiki_relations" / "section_relation_index.json").read_text(encoding="utf-8")
    )
    by_book = payload.get("by_book") if isinstance(payload, dict) else {}
    records = by_book.get("backup_and_restore") if isinstance(by_book, dict) else None
    if not isinstance(records, list) or not records:
        raise RuntimeError("backup_and_restore section relation이 필요합니다.")
    first = records[0]
    href = str(first.get("href") or "")
    anchor = href.split("#", 1)[1] if "#" in href else ""
    return {
        "book_slug": "backup_and_restore",
        "anchor": anchor,
        "viewer_path": href,
    }


def _sample_figure_payload() -> dict[str, str]:
    payload = json.loads(
        (ROOT / "data" / "wiki_relations" / "figure_assets.json").read_text(encoding="utf-8")
    )
    entries = payload.get("entries") if isinstance(payload, dict) else {}
    figures = entries.get("architecture") if isinstance(entries, dict) else None
    if not isinstance(figures, list) or not figures:
        raise RuntimeError("architecture figure asset이 필요합니다.")
    first = figures[0]
    return {
        "book_slug": "architecture",
        "asset_name": str(first.get("asset_name") or Path(str(first.get("asset_url") or "")).name),
        "viewer_path": str(first.get("viewer_path") or ""),
    }


def main() -> None:
    overlays: list[str] = []
    section_payload = _sample_section_payload()
    figure_payload = _sample_figure_payload()
    try:
        overlays.append(
            save_wiki_user_overlay(
                ROOT,
                {
                    "user_id": SMOKE_USER,
                    "kind": "favorite",
                    "target_kind": "book",
                    "book_slug": "backup_and_restore",
                    "viewer_path": "/playbooks/wiki-runtime/active/backup_and_restore/index.html",
                    "title": "Backup and Restore",
                },
            )["record"]["overlay_id"]
        )
        overlays.append(
            save_wiki_user_overlay(
                ROOT,
                {
                    "user_id": SMOKE_USER,
                    "kind": "recent_position",
                    "target_kind": "entity_hub",
                    "entity_slug": "etcd",
                    "viewer_path": "/wiki/entities/etcd/index.html",
                },
            )["record"]["overlay_id"]
        )
        overlays.append(
            save_wiki_user_overlay(
                ROOT,
                {
                    "user_id": SMOKE_USER,
                    "kind": "check",
                    "target_kind": "section",
                    **section_payload,
                    "status": "checked",
                },
            )["record"]["overlay_id"]
        )
        overlays.append(
            save_wiki_user_overlay(
                ROOT,
                {
                    "user_id": SMOKE_USER,
                    "kind": "note",
                    "target_kind": "figure",
                    **figure_payload,
                    "body": "figure signal smoke",
                    "pinned": True,
                },
            )["record"]["overlay_id"]
        )

        signal_payload = build_wiki_overlay_signal_payload(ROOT, user_id=SMOKE_USER)
        control_payload = build_data_control_room_payload(ROOT)
        top_targets = signal_payload.get("top_targets") if isinstance(signal_payload.get("top_targets"), list) else []
        user_focus = signal_payload.get("user_focus") if isinstance(signal_payload.get("user_focus"), dict) else {}
        recommended = user_focus.get("recommended_next_plays") if isinstance(user_focus.get("recommended_next_plays"), list) else []
        usage_bucket = control_payload.get("wiki_usage_signals") if isinstance(control_payload.get("wiki_usage_signals"), dict) else {}
        usage_books = usage_bucket.get("books") if isinstance(usage_bucket.get("books"), list) else []
        report = {
            "status": "ok"
            if top_targets and recommended and usage_books
            else "failed",
            "overlay_count": int(signal_payload.get("summary", {}).get("total_overlay_count") or 0),
            "top_target_count": len(top_targets),
            "recommended_next_play_count": len(recommended),
            "usage_bucket_count": len(usage_books),
            "first_top_target": top_targets[0] if top_targets else {},
            "first_recommended_play": recommended[0] if recommended else {},
            "control_room_usage_summary": usage_bucket.get("summary") if isinstance(usage_bucket.get("summary"), dict) else {},
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        for overlay_id in overlays:
            remove_wiki_user_overlay(ROOT, {"user_id": SMOKE_USER, "overlay_id": overlay_id})


if __name__ == "__main__":
    main()
