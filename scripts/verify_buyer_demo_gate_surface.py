from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.app.data_control_room import build_data_control_room_payload


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    payload = build_data_control_room_payload(root)
    tsx = (root / "presentation-ui" / "src" / "pages" / "PlaybookLibraryPage.tsx").read_text(encoding="utf-8")
    runtime_api = (root / "presentation-ui" / "src" / "lib" / "runtimeApi.ts").read_text(encoding="utf-8")

    buyer_gate = payload.get("buyer_demo_gate") if isinstance(payload.get("buyer_demo_gate"), dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    books = buyer_gate.get("books") if isinstance(buyer_gate.get("books"), list) else []
    titles = {str(item.get("title") or "") for item in books if isinstance(item, dict)}

    report = {
        "status": "ok",
        "payload_has_buyer_demo_gate_bucket": bool(buyer_gate),
        "summary_has_buyer_demo_gate_count": int(summary.get("buyer_demo_gate_count") or 0) == len(books) and len(books) == 3,
        "payload_has_promotion_gate_card": "Full-Sale Promotion Gate" in titles,
        "payload_has_release_blockers_card": "Release Blockers" in titles,
        "payload_has_owner_scenarios_card": "Owner Demo Scenarios" in titles,
        "tsx_has_buyer_gate_metric": "Buyer Demo Gate" in tsx and "openMetricPopover('buyerGate')" in tsx,
        "runtime_api_has_buyer_gate_types": "buyer_demo_gate_count?: number;" in runtime_api and "buyer_demo_gate?: LibraryBucket;" in runtime_api,
    }
    if not all(report.values()):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    out = root / "reports" / "build_logs" / "buyer_demo_gate_surface_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
