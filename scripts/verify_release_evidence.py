from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER_DEMO_REPORT = ROOT / "reports" / "build_logs" / "owner_demo_rehearsal_report.json"
BUYER_PACKET = ROOT / "reports" / "build_logs" / "buyer_packet_bundle_index.json"
RELEASE_PACKET = ROOT / "reports" / "build_logs" / "release_candidate_freeze_packet.json"
OUTPUT_JSON = ROOT / "reports" / "build_logs" / "release_evidence_report.json"
OUTPUT_MD = ROOT / "reports" / "build_logs" / "release_evidence_report.md"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    owner_demo = _load_json(OWNER_DEMO_REPORT)
    buyer_packet = _load_json(BUYER_PACKET)
    release_packet = _load_json(RELEASE_PACKET)
    report = {
        "status": "ok",
        "owner_demo_exists": OWNER_DEMO_REPORT.exists(),
        "owner_demo_blocker_count": len(owner_demo.get("blockers") or []),
        "owner_critical_scenario_pass_rate": float(owner_demo.get("owner_critical_scenario_pass_rate") or 0.0),
        "buyer_packet_exists": BUYER_PACKET.exists(),
        "buyer_packet_count": int(buyer_packet.get("packet_count") or 0),
        "release_packet_exists": RELEASE_PACKET.exists(),
        "release_supporting_packet_count": len(release_packet.get("supporting_packets") or []),
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Release Evidence Report",
                "",
                f"- owner_demo_exists: `{report['owner_demo_exists']}`",
                f"- owner_demo_blocker_count: `{report['owner_demo_blocker_count']}`",
                f"- owner_critical_scenario_pass_rate: `{report['owner_critical_scenario_pass_rate']}`",
                f"- buyer_packet_exists: `{report['buyer_packet_exists']}`",
                f"- buyer_packet_count: `{report['buyer_packet_count']}`",
                f"- release_packet_exists: `{report['release_packet_exists']}`",
                f"- release_supporting_packet_count: `{report['release_supporting_packet_count']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
