from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "buyer_demo_live_packet.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "buyer_demo_live_packet.md"
RUNTIME_BASE_URL = "http://127.0.0.1:8765"
APP_PLAYBOOK_LIBRARY = "/playbook-library"
APP_WORKSPACE = "/workspace"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    owner_packet = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_script_packet.json")
    owner_surface = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_surface_report.json")
    customer_surface = _load_json(ROOT / "reports" / "build_logs" / "customer_pack_library_surface_report.json")
    mixed_surface = _load_json(ROOT / "reports" / "build_logs" / "mixed_runtime_end_to_end_report.json")
    taxonomy_surface = _load_json(ROOT / "reports" / "build_logs" / "chat_truth_taxonomy_report.json")

    steps = [
        {
            "step": 1,
            "title": "Playbook Library 에서 현재 판매 경계 보여주기",
            "app_route": APP_PLAYBOOK_LIBRARY,
            "runtime_url": f"{RUNTIME_BASE_URL}/api/data-control-room",
            "click_targets": [
                "Buyer Demo Gate",
                "Owner Demo Pass Rate",
                "Customer Pack Runtime",
            ],
            "expected_truth": "paid_poc_candidate + buyer_demo_gate + owner_demo_pass_rate",
            "talk_track": "현재 제품이 문서 저장소가 아니라 source-first technical wiki runtime 이며, 현재 판매 단계가 paid PoC candidate 라는 점을 먼저 잠근다.",
        },
        {
            "step": 2,
            "title": "Runtime book 에서 connected wiki 흐름 보여주기",
            "app_route": APP_PLAYBOOK_LIBRARY,
            "runtime_url": f"{RUNTIME_BASE_URL}/playbooks/wiki-runtime/active/backup_and_restore/index.html?embed=1",
            "click_targets": [
                "Backup and Restore",
                "Start Here",
                "Explore",
            ],
            "expected_truth": "validated_runtime",
            "talk_track": "단일 문서가 아니라 book, related section, figure, navigation 이 붙은 runtime 이라는 점을 바로 보여준다.",
        },
        {
            "step": 3,
            "title": "Entity hub 로 넘어가서 위키 재진입 보여주기",
            "app_route": APP_PLAYBOOK_LIBRARY,
            "runtime_url": f"{RUNTIME_BASE_URL}/wiki/entities/etcd/index.html?embed=1",
            "click_targets": [
                "etcd",
                "Related Books",
                "Related Sections",
            ],
            "expected_truth": "entity_hub",
            "talk_track": "정적인 문서 열람이 아니라 entity hub 를 통해 다시 runtime 으로 재진입할 수 있다는 점을 보여준다.",
        },
        {
            "step": 4,
            "title": "Workspace 에서 grounded chat 와 source trace 보여주기",
            "app_route": APP_WORKSPACE,
            "runtime_url": f"{RUNTIME_BASE_URL}/api/chat",
            "query": "etcd 백업 절차와 관련 문서를 보여줘",
            "click_targets": [
                "Validated Runtime citation",
                "related navigation",
                "source trace",
            ],
            "expected_truth": "validated_runtime",
            "talk_track": "챗봇이 별도 지식원이 아니라 같은 runtime 위에서 답하고, citation 과 source trace 로 바로 이어진다는 점을 보여준다.",
        },
        {
            "step": 5,
            "title": "Customer Pack Runtime 과 Mixed Runtime truth 보여주기",
            "app_route": APP_WORKSPACE,
            "runtime_url": f"{RUNTIME_BASE_URL}/api/chat",
            "query": "고객 절차와 openshift 공식 postinstallation 설정을 함께 보여줘",
            "click_targets": [
                "Customer Pack Runtime",
                "Mixed Runtime",
                "OpenShift 4.20 Runtime + Customer Source-First Pack",
            ],
            "expected_truth": "private_customer_pack_runtime + mixed_runtime_bridge",
            "talk_track": "고객 문서를 다루더라도 official/private/mixed truth 를 숨기지 않고 boundary 를 유지한다는 점을 보여준다.",
        },
        {
            "step": 6,
            "title": "마지막으로 sales boundary 를 다시 닫기",
            "app_route": APP_PLAYBOOK_LIBRARY,
            "runtime_url": f"{RUNTIME_BASE_URL}/api/data-control-room",
            "click_targets": [
                "Buyer Demo Gate",
                "Owner Demo Pass Rate",
                "current blockers",
            ],
            "expected_truth": "paid_poc_candidate with explicit full-sale gate",
            "talk_track": "owner demo 는 통과했지만 full-sale 은 scorecard gate 기준으로만 승격한다는 점을 마지막에 정직하게 닫는다.",
        },
    ]

    packet = {
        "status": "ok",
        "title": "Buyer Demo Live Rehearsal Packet",
        "current_stage": owner_packet.get("current_stage"),
        "current_scope": owner_packet.get("current_scope"),
        "owner_demo_pass_rate": owner_packet.get("evidence_snapshot", {}).get("owner_demo_pass_rate"),
        "steps": steps,
        "surface_checks": {
            "owner_demo_surface_status": owner_surface.get("status"),
            "customer_pack_surface_status": customer_surface.get("status"),
            "mixed_runtime_status": mixed_surface.get("status"),
            "taxonomy_status": taxonomy_surface.get("status"),
        },
        "expected_truth_badges": [
            "Validated Runtime",
            "Private Runtime",
            "Mixed Runtime",
        ],
        "notes": [
            "앱 route 는 /playbook-library 와 /workspace 로 고정한다.",
            "runtime viewer 와 entity hub 는 8765 기준 live URL 로 바로 열 수 있어야 한다.",
            "mixed runtime 시연은 official + private citation 이 함께 보이는 답변을 사용한다.",
        ],
        "inputs": [
            "reports/build_logs/owner_demo_script_packet.json",
            "reports/build_logs/owner_demo_surface_report.json",
            "reports/build_logs/customer_pack_library_surface_report.json",
            "reports/build_logs/mixed_runtime_end_to_end_report.json",
            "reports/build_logs/chat_truth_taxonomy_report.json",
        ],
    }

    REPORT_JSON.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Buyer Demo Live Rehearsal Packet",
        "",
        f"- current_stage: `{packet['current_stage']}`",
        f"- current_scope: `{packet['current_scope']}`",
        f"- owner_demo_pass_rate: `{packet['owner_demo_pass_rate']}`",
        "",
        "## Live Demo Steps",
        "",
    ]
    for row in steps:
        lines.extend(
            [
                f"### Step {row['step']}. {row['title']}",
                "",
                f"- app_route: `{row['app_route']}`",
                f"- runtime_url: `{row['runtime_url']}`",
                f"- expected_truth: `{row['expected_truth']}`",
                f"- talk_track: {row['talk_track']}",
            ]
        )
        if row.get("query"):
            lines.append(f"- query: `{row['query']}`")
        lines.append("- click_targets:")
        for item in row["click_targets"]:
            lines.append(f"  - {item}")
        lines.append("")
    lines.extend(["## Expected Truth Badges", ""])
    lines.extend([f"- {item}" for item in packet["expected_truth_badges"]])
    lines.extend(["", "## Surface Checks", ""])
    for key, value in packet["surface_checks"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(packet, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
