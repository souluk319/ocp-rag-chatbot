from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FREEZE_JSON = ROOT / "reports" / "build_logs" / "release_candidate_freeze_packet.json"
REPORT_JSON = ROOT / "reports" / "build_logs" / "release_candidate_freeze_packet_verification_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "release_candidate_freeze_packet_verification_report.md"


def main() -> int:
    payload = json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    supporting_packets = payload.get("supporting_packets") if isinstance(payload.get("supporting_packets"), list) else []
    live_entry_points = payload.get("live_entry_points") if isinstance(payload.get("live_entry_points"), list) else []
    report = {
        "status": "ok",
        "title": str(payload.get("title") or ""),
        "freeze_id_present": str(payload.get("freeze_id") or "").startswith("rc-freeze-"),
        "current_stage": str(payload.get("current_stage") or ""),
        "runtime_count": int(((payload.get("runtime_snapshot") or {}).get("runtime_count")) or 0),
        "supporting_packet_count": len(supporting_packets),
        "live_entry_point_count": len(live_entry_points),
        "has_tomorrow_start_here": len(payload.get("tomorrow_start_here") or []) >= 3,
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Release Candidate Freeze Packet Verification Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- title: `{report['title']}`\n"
        + f"- freeze_id_present: `{report['freeze_id_present']}`\n"
        + f"- current_stage: `{report['current_stage']}`\n"
        + f"- runtime_count: `{report['runtime_count']}`\n"
        + f"- supporting_packet_count: `{report['supporting_packet_count']}`\n"
        + f"- live_entry_point_count: `{report['live_entry_point_count']}`\n"
        + f"- has_tomorrow_start_here: `{report['has_tomorrow_start_here']}`\n",
        encoding="utf-8",
    )
    ok = (
        report["title"] == "Release Candidate Freeze Packet"
        and report["freeze_id_present"]
        and report["current_stage"] == "paid_poc_candidate"
        and report["runtime_count"] == 29
        and report["supporting_packet_count"] == 4
        and report["live_entry_point_count"] >= 4
        and report["has_tomorrow_start_here"]
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
