from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "release_candidate_freeze_packet.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "release_candidate_freeze_packet.md"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    owner_sheet = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_one_sheet.json")
    release_gate = _load_json(ROOT / "reports" / "build_logs" / "release_gate_one_sheet.json")
    buyer_live = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_live_packet.json")
    owner_rehearsal = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_rehearsal_report.json")
    active_manifest = _load_json(ROOT / "data" / "wiki_runtime_books" / "active_manifest.json")

    freeze_date = datetime.now().strftime("%Y-%m-%d")
    runtime_count = int(active_manifest.get("runtime_count") or 0)
    stage = str(release_gate.get("current_stage") or owner_sheet.get("current_stage") or "")
    promotion_gate = [str(item) for item in (release_gate.get("promotion_gate") or [])]
    release_blockers = [str(item) for item in (release_gate.get("release_blockers") or [])]
    live_entry_points = owner_sheet.get("live_entry_points") or release_gate.get("entry_points") or []

    packet = {
        "status": "ok",
        "title": "Release Candidate Freeze Packet",
        "freeze_id": f"rc-freeze-{freeze_date}",
        "freeze_date": freeze_date,
        "current_stage": stage,
        "current_scope": release_gate.get("current_scope"),
        "commercial_truth": owner_sheet.get("commercial_truth"),
        "runtime_snapshot": {
            "active_group": active_manifest.get("active_group"),
            "runtime_count": runtime_count,
        },
        "owner_demo": {
            "scenario_count": owner_rehearsal.get("scenario_count"),
            "pass_count": owner_rehearsal.get("pass_count"),
            "pass_rate": owner_rehearsal.get("owner_critical_scenario_pass_rate"),
            "blockers": owner_rehearsal.get("blockers") or [],
        },
        "release_gate": {
            "sell_now": release_gate.get("sell_now"),
            "do_not_sell_yet": release_gate.get("do_not_sell_yet"),
            "promotion_gate_count": len(promotion_gate),
            "release_blocker_count": len(release_blockers),
        },
        "live_entry_points": live_entry_points,
        "demo_flow_titles": [str(step.get("title") or "") for step in (buyer_live.get("steps") or []) if isinstance(step, dict)],
        "supporting_packets": [
            {
                "title": "Owner Demo One-Sheet",
                "markdown_path": "reports/build_logs/owner_demo_one_sheet.md",
            },
            {
                "title": "Release Gate One-Sheet",
                "markdown_path": "reports/build_logs/release_gate_one_sheet.md",
            },
            {
                "title": "Owner Demo Script Packet",
                "markdown_path": "reports/build_logs/owner_demo_script_packet.md",
            },
            {
                "title": "Buyer Demo Live Rehearsal Packet",
                "markdown_path": "reports/build_logs/buyer_demo_live_packet.md",
            },
        ],
        "tomorrow_start_here": [
            "Playbook Library 에서 Buyer Packet Bundle 을 연다.",
            "Release Candidate Freeze Packet 으로 현재 stage 와 runtime count 를 확인한다.",
            "Owner Demo One-Sheet 와 Release Gate One-Sheet 로 세일즈/데모 경계를 다시 확인한다.",
            "Buyer Demo Live Rehearsal Packet 순서대로 실제 화면을 시연한다.",
        ],
        "close": "이 freeze packet 은 오늘 상태의 판매/데모/런타임 기준선을 고정한다. 내일은 이 packet 을 첫 화면으로 열고 시작한다.",
        "inputs": [
            "reports/build_logs/owner_demo_one_sheet.json",
            "reports/build_logs/release_gate_one_sheet.json",
            "reports/build_logs/buyer_demo_live_packet.json",
            "reports/build_logs/owner_demo_rehearsal_report.json",
            "data/wiki_runtime_books/active_manifest.json",
        ],
    }

    REPORT_JSON.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Release Candidate Freeze Packet",
        "",
        f"- freeze_id: `{packet['freeze_id']}`",
        f"- freeze_date: `{packet['freeze_date']}`",
        f"- current_stage: `{packet['current_stage']}`",
        f"- current_scope: `{packet['current_scope']}`",
        f"- commercial_truth: `{packet['commercial_truth']}`",
        f"- active_group: `{packet['runtime_snapshot']['active_group']}`",
        f"- runtime_count: `{packet['runtime_snapshot']['runtime_count']}`",
        "",
        "## Owner Demo Snapshot",
        "",
        f"- scenario_count: `{packet['owner_demo']['scenario_count']}`",
        f"- pass_count: `{packet['owner_demo']['pass_count']}`",
        f"- pass_rate: `{packet['owner_demo']['pass_rate']}`",
        f"- blockers: `{packet['owner_demo']['blockers']}`",
        "",
        "## Release Gate Snapshot",
        "",
        f"- sell_now: `{packet['release_gate']['sell_now']}`",
        f"- do_not_sell_yet: `{packet['release_gate']['do_not_sell_yet']}`",
        f"- promotion_gate_count: `{packet['release_gate']['promotion_gate_count']}`",
        f"- release_blocker_count: `{packet['release_gate']['release_blocker_count']}`",
        "",
        "## Live Entry Points",
        "",
    ]
    for item in live_entry_points:
        if not isinstance(item, dict):
            continue
        lines.append(f"- {item.get('label')}: `{item.get('route')}`")
    lines.extend(["", "## Tomorrow Start Here", ""])
    lines.extend(f"- {item}" for item in packet["tomorrow_start_here"])
    lines.extend(["", "## Supporting Packets", ""])
    for item in packet["supporting_packets"]:
        lines.append(f"- {item['title']}: `{item['markdown_path']}`")
    lines.extend(["", "## Close", "", packet["close"], ""])

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(packet, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
