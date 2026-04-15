from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE_JSON = ROOT / "reports" / "build_logs" / "buyer_packet_bundle_index.json"
REPORT_JSON = ROOT / "reports" / "build_logs" / "buyer_packet_bundle_index_verification_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "buyer_packet_bundle_index_verification_report.md"


def main() -> int:
    payload = json.loads(BUNDLE_JSON.read_text(encoding="utf-8"))
    packets = payload.get("packets") or []

    report = {
        "status": "ok",
        "packet_count": len(packets),
        "all_ready": bool(payload.get("all_ready")),
        "has_release_candidate_freeze": any(str(item.get("id") or "") == "release-candidate-freeze" for item in packets if isinstance(item, dict)),
        "has_owner_script": any(str(item.get("id") or "") == "owner-demo-script" for item in packets if isinstance(item, dict)),
        "has_buyer_live": any(str(item.get("id") or "") == "buyer-demo-live" for item in packets if isinstance(item, dict)),
        "has_owner_sheet": any(str(item.get("id") or "") == "owner-demo-one-sheet" for item in packets if isinstance(item, dict)),
        "has_release_gate_sheet": any(str(item.get("id") or "") == "release-gate-one-sheet" for item in packets if isinstance(item, dict)),
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Buyer Packet Bundle Index Verification Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- packet_count: `{report['packet_count']}`\n"
        + f"- all_ready: `{report['all_ready']}`\n"
        + f"- has_release_candidate_freeze: `{report['has_release_candidate_freeze']}`\n"
        + f"- has_owner_script: `{report['has_owner_script']}`\n"
        + f"- has_buyer_live: `{report['has_buyer_live']}`\n"
        + f"- has_owner_sheet: `{report['has_owner_sheet']}`\n"
        + f"- has_release_gate_sheet: `{report['has_release_gate_sheet']}`\n",
        encoding="utf-8",
    )
    ok = (
        report["packet_count"] == 5
        and report["all_ready"]
        and report["has_release_candidate_freeze"]
        and report["has_owner_script"]
        and report["has_buyer_live"]
        and report["has_owner_sheet"]
        and report["has_release_gate_sheet"]
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
