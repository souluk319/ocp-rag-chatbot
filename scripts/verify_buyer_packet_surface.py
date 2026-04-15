from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "buyer_packet_surface_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "buyer_packet_surface_report.md"


def _get_json(url: str) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    control = _get_json("http://127.0.0.1:8765/api/data-control-room")
    preview = _get_json("http://127.0.0.1:8765/api/buyer-packet?packet_id=owner-demo-one-sheet")
    freeze_packet_html = urllib.request.urlopen(
        "http://127.0.0.1:8765/buyer-packets/release-candidate-freeze?embed=1",
        timeout=60,
    ).read().decode("utf-8")
    tsx = (ROOT / "presentation-ui" / "src" / "pages" / "PlaybookLibraryPage.tsx").read_text(encoding="utf-8")
    runtime_api = (ROOT / "presentation-ui" / "src" / "lib" / "runtimeApi.ts").read_text(encoding="utf-8")

    summary = control.get("summary") if isinstance(control.get("summary"), dict) else {}
    buyer_bundle = control.get("buyer_packet_bundle") if isinstance(control.get("buyer_packet_bundle"), dict) else {}
    freeze_summary = control.get("release_candidate_freeze") if isinstance(control.get("release_candidate_freeze"), dict) else {}
    books = buyer_bundle.get("books") if isinstance(buyer_bundle.get("books"), list) else []

    report = {
        "status": "ok",
        "payload_has_bundle": bool(buyer_bundle),
        "payload_bundle_count": int(summary.get("buyer_packet_bundle_count") or len(books)),
        "payload_has_release_candidate_freeze": any(
            str(item.get("book_slug") or "") == "buyer_packet__release-candidate-freeze"
            for item in books
            if isinstance(item, dict)
        ),
        "payload_has_release_packet_badge": any(
            str(item.get("boundary_badge") or "") == "Release Packet"
            for item in books
            if isinstance(item, dict)
        ),
        "payload_has_release_candidate_freeze_summary": bool(freeze_summary),
        "payload_freeze_summary_points_to_viewer": str(freeze_summary.get("viewer_path") or "") == "/buyer-packets/release-candidate-freeze",
        "freeze_packet_route_has_viewer": "Release Candidate Freeze Packet" in freeze_packet_html and "Release Packet" in freeze_packet_html,
        "preview_title": str(preview.get("title") or ""),
        "preview_status": str(preview.get("status") or ""),
        "preview_body_has_value": "One-Line Value" in str(preview.get("body") or ""),
        "tsx_has_buyer_packet_metric": "Release Candidate Packets" in tsx and "Release Gate Surface" in tsx,
        "tsx_opens_packet_in_book_viewer": "grade: 'Release Packet'" in tsx and "setBookViewer({" in tsx,
        "tsx_has_release_freeze_hero": "Open Freeze Packet" in tsx and "Today Start" in tsx,
        "runtime_api_has_buyer_packet_types": "BuyerPacketPreview" in runtime_api and "loadBuyerPacket" in runtime_api,
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Buyer Packet Surface Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- payload_has_bundle: `{report['payload_has_bundle']}`\n"
        + f"- payload_bundle_count: `{report['payload_bundle_count']}`\n"
        + f"- payload_has_release_candidate_freeze: `{report['payload_has_release_candidate_freeze']}`\n"
        + f"- payload_has_release_packet_badge: `{report['payload_has_release_packet_badge']}`\n"
        + f"- payload_has_release_candidate_freeze_summary: `{report['payload_has_release_candidate_freeze_summary']}`\n"
        + f"- payload_freeze_summary_points_to_viewer: `{report['payload_freeze_summary_points_to_viewer']}`\n"
        + f"- freeze_packet_route_has_viewer: `{report['freeze_packet_route_has_viewer']}`\n"
        + f"- preview_title: `{report['preview_title']}`\n"
        + f"- preview_status: `{report['preview_status']}`\n"
        + f"- preview_body_has_value: `{report['preview_body_has_value']}`\n"
        + f"- tsx_has_buyer_packet_metric: `{report['tsx_has_buyer_packet_metric']}`\n"
        + f"- tsx_opens_packet_in_book_viewer: `{report['tsx_opens_packet_in_book_viewer']}`\n"
        + f"- tsx_has_release_freeze_hero: `{report['tsx_has_release_freeze_hero']}`\n"
        + f"- runtime_api_has_buyer_packet_types: `{report['runtime_api_has_buyer_packet_types']}`\n",
        encoding="utf-8",
    )
    ok = (
        report["payload_has_bundle"]
        and report["payload_bundle_count"] >= 5
        and report["payload_has_release_candidate_freeze"]
        and report["payload_has_release_packet_badge"]
        and report["payload_has_release_candidate_freeze_summary"]
        and report["payload_freeze_summary_points_to_viewer"]
        and report["freeze_packet_route_has_viewer"]
        and report["preview_title"] == "Owner Demo One-Sheet"
        and report["preview_status"] == "ok"
        and report["preview_body_has_value"]
        and report["tsx_has_buyer_packet_metric"]
        and report["tsx_opens_packet_in_book_viewer"]
        and report["tsx_has_release_freeze_hero"]
        and report["runtime_api_has_buyer_packet_types"]
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
