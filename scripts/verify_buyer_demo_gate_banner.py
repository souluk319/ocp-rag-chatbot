from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.data_control_room import build_data_control_room_payload


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    payload = build_data_control_room_payload(root)
    tsx = (root / "presentation-ui" / "src" / "pages" / "PlaybookLibraryPage.tsx").read_text(encoding="utf-8")
    css = (root / "presentation-ui" / "src" / "pages" / "PlaybookLibraryPage.css").read_text(encoding="utf-8")
    runtime_api = (root / "presentation-ui" / "src" / "lib" / "runtimeApi.ts").read_text(encoding="utf-8")

    gate = payload.get("gate") if isinstance(payload.get("gate"), dict) else {}
    report = {
        "status": "ok",
        "payload_has_gate_object": bool(gate),
        "payload_gate_has_status": bool(str(gate.get("status") or "").strip()),
        "payload_gate_has_release_blocking": isinstance(gate.get("release_blocking"), bool),
        "tsx_uses_gate_banner_copy": "gateBannerCopy" in tsx and "truth-banner-copy" in tsx,
        "tsx_renders_gate_banner_conditionally": "(gate || hasMetricSourceDrift)" in tsx,
        "runtime_api_has_gate_type": "gate?:" in runtime_api and "release_blocking: boolean;" in runtime_api,
        "css_has_truth_banner_copy": ".truth-banner-copy" in css and ".truth-banner-copy strong" in css,
    }
    if not all(report.values()):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    out = root / "reports" / "build_logs" / "buyer_demo_gate_banner_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
