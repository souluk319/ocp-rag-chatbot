from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ONE_SHEET_JSON = ROOT / "reports" / "build_logs" / "owner_demo_one_sheet.json"
REPORT_JSON = ROOT / "reports" / "build_logs" / "owner_demo_one_sheet_verification_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "owner_demo_one_sheet_verification_report.md"


def main() -> int:
    payload = json.loads(ONE_SHEET_JSON.read_text(encoding="utf-8"))
    entry_points = payload.get("live_entry_points") or []
    truth_badges = payload.get("truth_badges") or []
    why_buy_now = payload.get("why_buy_now") or []
    not_yet = (payload.get("sale_boundary") or {}).get("what_we_do_not_sell_yet") or []
    blockers = (payload.get("release_gate_summary") or {}).get("blockers_to_watch") or []

    report = {
        "status": "ok",
        "entry_point_count": len(entry_points),
        "has_playbook_library_entry": any(str(item.get("route") or "") == "/playbook-library" for item in entry_points if isinstance(item, dict)),
        "has_workspace_entry": any(str(item.get("route") or "") == "/workspace" for item in entry_points if isinstance(item, dict)),
        "has_runtime_url_entry": any("playbooks/wiki-runtime/active" in str(item.get("route") or "") for item in entry_points if isinstance(item, dict)),
        "has_entity_hub_entry": any("/wiki/entities/" in str(item.get("route") or "") for item in entry_points if isinstance(item, dict)),
        "truth_badge_count": len(truth_badges),
        "why_buy_now_count": len(why_buy_now),
        "not_yet_count": len(not_yet),
        "blocker_count": len(blockers),
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Owner Demo One-Sheet Verification Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- entry_point_count: `{report['entry_point_count']}`\n"
        + f"- truth_badge_count: `{report['truth_badge_count']}`\n"
        + f"- why_buy_now_count: `{report['why_buy_now_count']}`\n"
        + f"- not_yet_count: `{report['not_yet_count']}`\n"
        + f"- blocker_count: `{report['blocker_count']}`\n",
        encoding="utf-8",
    )
    ok = (
        report["entry_point_count"] >= 4
        and report["has_playbook_library_entry"]
        and report["has_workspace_entry"]
        and report["has_runtime_url_entry"]
        and report["has_entity_hub_entry"]
        and report["truth_badge_count"] >= 3
        and report["why_buy_now_count"] >= 3
        and report["not_yet_count"] >= 3
        and report["blocker_count"] >= 3
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
