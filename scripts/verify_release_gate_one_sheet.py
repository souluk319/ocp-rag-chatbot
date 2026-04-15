from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ONE_SHEET_JSON = ROOT / "reports" / "build_logs" / "release_gate_one_sheet.json"
REPORT_JSON = ROOT / "reports" / "build_logs" / "release_gate_one_sheet_verification_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "release_gate_one_sheet_verification_report.md"


def main() -> int:
    payload = json.loads(ONE_SHEET_JSON.read_text(encoding="utf-8"))
    promotion_gate = payload.get("promotion_gate") or []
    release_blockers = payload.get("release_blockers") or []
    why_not = payload.get("why_not_full_sale_yet") or []
    entry_points = payload.get("entry_points") or []

    report = {
        "status": "ok",
        "current_stage": payload.get("current_stage"),
        "sell_now": payload.get("sell_now"),
        "do_not_sell_yet": payload.get("do_not_sell_yet"),
        "promotion_gate_count": len(promotion_gate),
        "release_blocker_count": len(release_blockers),
        "why_not_count": len(why_not),
        "entry_point_count": len(entry_points),
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Release Gate One-Sheet Verification Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- current_stage: `{report['current_stage']}`\n"
        + f"- sell_now: `{report['sell_now']}`\n"
        + f"- do_not_sell_yet: `{report['do_not_sell_yet']}`\n"
        + f"- promotion_gate_count: `{report['promotion_gate_count']}`\n"
        + f"- release_blocker_count: `{report['release_blocker_count']}`\n"
        + f"- why_not_count: `{report['why_not_count']}`\n"
        + f"- entry_point_count: `{report['entry_point_count']}`\n",
        encoding="utf-8",
    )
    ok = (
        report["current_stage"] == "paid_poc_candidate"
        and report["sell_now"] == "paid PoC candidate"
        and report["do_not_sell_yet"] == "full sale"
        and report["promotion_gate_count"] >= 5
        and report["release_blocker_count"] >= 5
        and report["why_not_count"] >= 3
        and report["entry_point_count"] >= 3
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
