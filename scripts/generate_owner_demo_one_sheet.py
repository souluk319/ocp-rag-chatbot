from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "owner_demo_one_sheet.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "owner_demo_one_sheet.md"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    owner_packet = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_script_packet.json")
    live_packet = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_live_packet.json")
    live_verify = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_live_packet_verification_report.json")

    value_points = [
        "공식 source 우선 + fallback 경로를 가진 technical wiki runtime",
        "book, entity hub, related section, figure, grounded chat 가 같은 runtime 위에서 연결됨",
        "customer pack 도 official/private/mixed truth 를 숨기지 않고 boundary 안에서 수용 가능",
    ]
    not_yet = [str(item) for item in (owner_packet.get("non_promises") or [])[:4]]
    blockers = [str(item) for item in (owner_packet.get("hard_blockers") or [])[:5]]
    entry_points = [
        {
            "label": "Playbook Library",
            "route": "/playbook-library",
            "purpose": "현재 판매 경계, buyer demo gate, owner demo pass rate 확인",
        },
        {
            "label": "Validated Runtime Book",
            "route": "http://127.0.0.1:8765/playbooks/wiki-runtime/active/backup_and_restore/index.html?embed=1",
            "purpose": "connected wiki runtime reading experience 시연",
        },
        {
            "label": "Entity Hub",
            "route": "http://127.0.0.1:8765/wiki/entities/etcd/index.html?embed=1",
            "purpose": "entity hub 를 통한 위키 재진입 시연",
        },
        {
            "label": "Workspace",
            "route": "/workspace",
            "purpose": "grounded chat, citation, mixed runtime truth 시연",
        },
    ]

    sheet = {
        "status": "ok",
        "title": "Owner Demo One-Sheet",
        "commercial_truth": owner_packet.get("demo_positioning", {}).get("commercial_truth"),
        "current_stage": owner_packet.get("current_stage"),
        "north_star": owner_packet.get("north_star"),
        "one_line_value": "기업 문서와 운영 지식을 source-first technical wiki runtime 으로 연결해, 운영과 학습을 같은 surface 에서 다루는 제품.",
        "why_buy_now": value_points,
        "sale_boundary": {
            "current_stage": owner_packet.get("current_stage"),
            "what_we_sell_now": "OpenShift 4.20 validated pack + customer document PoC",
            "what_we_do_not_sell_yet": not_yet,
        },
        "release_gate_summary": {
            "owner_demo_pass_rate": owner_packet.get("evidence_snapshot", {}).get("owner_demo_pass_rate"),
            "gate_status": live_verify.get("status"),
            "blockers_to_watch": blockers,
        },
        "live_entry_points": entry_points,
        "truth_badges": live_packet.get("expected_truth_badges") or [],
        "close": "지금은 paid PoC candidate 를 정직하게 제안할 수 있고, full-sale 은 scorecard gate 를 통과한 뒤에만 승격한다.",
        "inputs": [
            "reports/build_logs/owner_demo_script_packet.json",
            "reports/build_logs/buyer_demo_live_packet.json",
            "reports/build_logs/buyer_demo_live_packet_verification_report.json",
        ],
    }

    REPORT_JSON.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Owner Demo One-Sheet",
        "",
        f"- current_stage: `{sheet['current_stage']}`",
        f"- commercial_truth: `{sheet['commercial_truth']}`",
        f"- owner_demo_pass_rate: `{sheet['release_gate_summary']['owner_demo_pass_rate']}`",
        "",
        "## One-Line Value",
        "",
        sheet["one_line_value"],
        "",
        "## Why Buy Now",
        "",
    ]
    lines.extend(f"- {item}" for item in value_points)
    lines.extend(["", "## Sale Boundary", ""])
    lines.append(f"- what_we_sell_now: {sheet['sale_boundary']['what_we_sell_now']}")
    lines.append("- what_we_do_not_sell_yet:")
    for item in not_yet:
        lines.append(f"  - {item}")
    lines.extend(["", "## Release Gate Summary", ""])
    lines.append(f"- gate_status: `{sheet['release_gate_summary']['gate_status']}`")
    lines.append(f"- owner_demo_pass_rate: `{sheet['release_gate_summary']['owner_demo_pass_rate']}`")
    lines.append("- blockers_to_watch:")
    for item in blockers:
        lines.append(f"  - {item}")
    lines.extend(["", "## Live Entry Points", ""])
    for item in entry_points:
        lines.extend(
            [
                f"- {item['label']}: `{item['route']}`",
                f"  - {item['purpose']}",
            ]
        )
    lines.extend(["", "## Truth Badges", ""])
    for item in sheet["truth_badges"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Close", "", sheet["close"], ""])

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(sheet, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
