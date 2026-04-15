from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "buyer_packet_bundle_index.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "buyer_packet_bundle_index.md"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    owner_script = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_script_packet.json")
    buyer_live = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_live_packet.json")
    owner_sheet = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_one_sheet.json")
    release_gate = _load_json(ROOT / "reports" / "build_logs" / "release_gate_one_sheet.json")
    release_freeze = _load_json(ROOT / "reports" / "build_logs" / "release_candidate_freeze_packet.json")

    packets = [
        {
            "id": "release-candidate-freeze",
            "title": "Release Candidate Freeze Packet",
            "purpose": "오늘 기준 판매/데모/런타임 상태를 내일 바로 다시 여는 freeze packet",
            "json_path": "reports/build_logs/release_candidate_freeze_packet.json",
            "markdown_path": "reports/build_logs/release_candidate_freeze_packet.md",
            "status": release_freeze.get("status"),
        },
        {
            "id": "owner-demo-script",
            "title": "Owner Demo Script Packet",
            "purpose": "오너 질문 5개와 talk track, evidence 를 바로 읽는 packet",
            "json_path": "reports/build_logs/owner_demo_script_packet.json",
            "markdown_path": "reports/build_logs/owner_demo_script_packet.md",
            "status": owner_script.get("status"),
        },
        {
            "id": "buyer-demo-live",
            "title": "Buyer Demo Live Rehearsal Packet",
            "purpose": "실제 클릭 경로와 live runtime URL 을 따라 데모하는 packet",
            "json_path": "reports/build_logs/buyer_demo_live_packet.json",
            "markdown_path": "reports/build_logs/buyer_demo_live_packet.md",
            "status": buyer_live.get("status"),
        },
        {
            "id": "owner-demo-one-sheet",
            "title": "Owner Demo One-Sheet",
            "purpose": "제품 가치와 sale boundary 를 한 장으로 요약한 세일즈 시트",
            "json_path": "reports/build_logs/owner_demo_one_sheet.json",
            "markdown_path": "reports/build_logs/owner_demo_one_sheet.md",
            "status": owner_sheet.get("status"),
        },
        {
            "id": "release-gate-one-sheet",
            "title": "Release Gate One-Sheet",
            "purpose": "지금 팔 수 있는 범위와 full-sale blocker 를 한 장으로 고정한 시트",
            "json_path": "reports/build_logs/release_gate_one_sheet.json",
            "markdown_path": "reports/build_logs/release_gate_one_sheet.md",
            "status": release_gate.get("status"),
        },
    ]

    bundle = {
        "status": "ok",
        "title": "Buyer Packet Bundle Index",
        "current_stage": release_gate.get("current_stage") or owner_script.get("current_stage"),
        "commercial_truth": owner_sheet.get("commercial_truth"),
        "packet_count": len(packets),
        "all_ready": all(str(item.get("status") or "") == "ok" for item in packets),
        "recommended_order": [
            "Release Candidate Freeze Packet",
            "Owner Demo One-Sheet",
            "Release Gate One-Sheet",
            "Owner Demo Script Packet",
            "Buyer Demo Live Rehearsal Packet",
        ],
        "packets": packets,
        "close": "내일 시작할 때는 freeze packet 으로 현재 기준선을 먼저 확인하고, 이후 one-sheet 두 장과 script/live packet 순으로 들어간다.",
    }

    REPORT_JSON.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Buyer Packet Bundle Index",
        "",
        f"- current_stage: `{bundle['current_stage']}`",
        f"- commercial_truth: `{bundle['commercial_truth']}`",
        f"- packet_count: `{bundle['packet_count']}`",
        f"- all_ready: `{bundle['all_ready']}`",
        "",
        "## Recommended Order",
        "",
    ]
    lines.extend(f"- {item}" for item in bundle["recommended_order"])
    lines.extend(["", "## Packets", ""])
    for item in packets:
        lines.extend(
            [
                f"### {item['title']}",
                "",
                f"- purpose: {item['purpose']}",
                f"- status: `{item['status']}`",
                f"- json_path: `{item['json_path']}`",
                f"- markdown_path: `{item['markdown_path']}`",
                "",
            ]
        )
    lines.extend(["## Close", "", bundle["close"], ""])

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(bundle, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
