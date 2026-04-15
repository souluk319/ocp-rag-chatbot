from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.data_control_room import build_data_control_room_payload


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    payload = build_data_control_room_payload(root)
    tsx = (root / "presentation-ui" / "src" / "pages" / "PlaybookLibraryPage.tsx").read_text(encoding="utf-8")
    runtime_api = (root / "presentation-ui" / "src" / "lib" / "runtimeApi.ts").read_text(encoding="utf-8")

    owner_demo = payload.get("owner_demo_rehearsal") if isinstance(payload.get("owner_demo_rehearsal"), dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}

    report = {
        "status": "ok",
        "payload_has_owner_demo_rehearsal": bool(owner_demo),
        "payload_pass_rate_is_one": float(owner_demo.get("owner_critical_scenario_pass_rate") or 0.0) == 1.0,
        "payload_blockers_empty": owner_demo.get("blockers") == [],
        "summary_has_owner_demo_pass_rate": float(summary.get("owner_demo_pass_rate") or 0.0) == 1.0,
        "tsx_has_owner_demo_metric": "Owner Demo Pass Rate" in tsx and "ownerDemoPassRate" in tsx,
        "tsx_has_owner_demo_banner_copy": "Owner demo {ownerDemo.pass_count}/{ownerDemo.scenario_count} passed" in tsx,
        "runtime_api_has_owner_demo_type": "owner_demo_rehearsal?:" in runtime_api and "owner_demo_pass_rate?: number;" in runtime_api,
    }
    if not all(report.values()):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    out = root / "reports" / "build_logs" / "owner_demo_surface_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
