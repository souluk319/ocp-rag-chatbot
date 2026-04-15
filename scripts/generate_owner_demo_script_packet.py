from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "owner_demo_script_packet.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "owner_demo_script_packet.md"


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def _extract_bullets(section_title: str, text: str) -> list[str]:
    marker = f"## {section_title}"
    start = text.find(marker)
    if start < 0:
        return []
    remainder = text[start + len(marker) :]
    next_header = remainder.find("\n## ")
    block = remainder if next_header < 0 else remainder[:next_header]
    bullets: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
            continue
        if ". " in stripped:
            head, tail = stripped.split(". ", 1)
            if head.isdigit() and tail.strip():
                bullets.append(tail.strip())
    return bullets


def _question_talk_track(question_id: str) -> str:
    mapping = {
        "owner-001": "문서 저장소가 아니라 source-first technical wiki runtime 이라는 점을 먼저 말하고, 현재 상업 단계가 paid PoC candidate 임을 바로 밝힌다.",
        "owner-002": "책, 엔터티 허브, related section, figure page, 챗봇이 같은 runtime 위에서 이어진다는 점을 실제 화면 흐름으로 보여준다.",
        "owner-003": "답변에서 citation 을 열고 viewer jump 와 source trace 를 바로 이어서 보여준다.",
        "owner-004": "customer pack 은 별도 boundary 안에서만 다루며 official/private/mixed truth 를 숨기지 않는다고 설명한다.",
        "owner-005": "related navigation, next play, overlay signals 로 운영형 사용성이 생긴다는 점을 짧게 시연한다.",
    }
    return mapping.get(question_id, "현재 runtime truth 와 evidence 를 짧게 보여준다.")


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    scorecard = yaml.safe_load((ROOT / "OWNER_SCENARIO_SCORECARD.yaml").read_text(encoding="utf-8")) or {}
    contract_text = (ROOT / "Q1_8_PRODUCT_CONTRACT.md").read_text(encoding="utf-8")
    project_text = (ROOT / "PROJECT.md").read_text(encoding="utf-8")

    rehearsal = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_rehearsal_report.json")
    gate_surface = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_gate_surface_report.json")
    gate_banner = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_gate_banner_report.json")
    owner_surface = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_surface_report.json")
    runtime_report = _load_json(ROOT / "reports" / "build_logs" / "ocp420_one_click_runtime_report.json")
    relation_report = _load_json(ROOT / "reports" / "build_logs" / "full_rebuild_wiki_relations_report.json")

    current_stage = str(scorecard.get("current_stage") or "")
    current_scope = str(scorecard.get("current_scope") or "")
    promotion_gate = list(((scorecard.get("promotion_gate") or {}).get("full_sale_requires") or []))
    release_blockers = list(scorecard.get("release_blockers") or [])

    promise_now = _extract_bullets("What We Promise Now", contract_text)
    non_promises = _extract_bullets("What We Explicitly Do Not Promise Yet", contract_text)
    hard_blockers = _extract_bullets("Hard Blockers", contract_text)

    scenario_rows = []
    for row in rehearsal.get("scenarios") or []:
        if not isinstance(row, dict):
            continue
        scenario_id = str(row.get("id") or "")
        scenario_rows.append(
            {
                "id": scenario_id,
                "question": str(row.get("question") or ""),
                "passed": bool(row.get("passed")),
                "talk_track": _question_talk_track(scenario_id),
                "evidence": [str(item) for item in (row.get("evidence") or []) if str(item).strip()],
            }
        )

    demo_flow = [
        {
            "step": 1,
            "title": "제품 정체성 먼저 잠그기",
            "show": "Playbook Library banner 와 current stage",
            "why": "문서 저장소가 아니라 technical wiki runtime 이라는 점을 먼저 고정한다.",
        },
        {
            "step": 2,
            "title": "connected runtime 보여주기",
            "show": "book -> entity hub -> related section -> figure page 흐름",
            "why": "static viewer 가 아니라 연결된 운영형 위키라는 점을 바로 체감시킨다.",
        },
        {
            "step": 3,
            "title": "grounded chat 보여주기",
            "show": "citation / related navigation / source trace",
            "why": "답변이 같은 runtime 과 provenance 위에 있다는 점을 증명한다.",
        },
        {
            "step": 4,
            "title": "customer pack boundary 보여주기",
            "show": "Private Runtime / Mixed Runtime truth surfaces",
            "why": "고객 문서도 다루지만 경계를 흐리지 않는다는 점을 설명한다.",
        },
        {
            "step": 5,
            "title": "현재 판매 경계 마무리",
            "show": "owner demo pass rate 와 full-sale gate",
            "why": "지금 어디까지 팔 수 있고 무엇이 아직 blocker 인지 정직하게 닫는다.",
        },
    ]

    packet = {
        "status": "ok",
        "title": "Owner Demo Script Packet",
        "current_stage": current_stage,
        "current_scope": current_scope,
        "north_star": str(scorecard.get("north_star") or ""),
        "opening_statement": "Play Book Studio 는 source-first technical wiki runtime 으로, 운영과 학습을 같은 runtime 위에서 연결해 주는 제품입니다.",
        "demo_positioning": {
            "product_identity": "connected technical wiki for operation and learning"
            if "connected technical wiki for operation and learning" in project_text
            else "source-first technical wiki runtime",
            "commercial_truth": "OpenShift 4.20 source-first validated pack + customer document PoC",
            "sale_boundary": "paid_poc_candidate",
        },
        "demo_flow": demo_flow,
        "questions": scenario_rows,
        "evidence_snapshot": {
            "owner_demo_pass_rate": rehearsal.get("owner_critical_scenario_pass_rate"),
            "owner_demo_blockers": rehearsal.get("blockers"),
            "runtime_book_count": 29 if runtime_report.get("approved_wiki_runtime_book_count") is None else runtime_report.get("approved_wiki_runtime_book_count"),
            "relation_book_count": relation_report.get("candidate_relation_count"),
            "gate_surface_status": gate_surface.get("status"),
            "gate_banner_status": gate_banner.get("status"),
            "owner_surface_status": owner_surface.get("status"),
        },
        "promise_now": promise_now,
        "non_promises": non_promises,
        "promotion_gate": [str(item) for item in promotion_gate],
        "release_blockers": [str(item) for item in release_blockers],
        "hard_blockers": hard_blockers,
        "closing_statement": "지금은 paid PoC candidate 단계이며, owner demo 와 runtime evidence 는 통과했지만 full-sale gate 는 scorecard 기준으로만 승격합니다.",
        "inputs": [
            "OWNER_SCENARIO_SCORECARD.yaml",
            "Q1_8_PRODUCT_CONTRACT.md",
            "PROJECT.md",
            "reports/build_logs/owner_demo_rehearsal_report.json",
            "reports/build_logs/buyer_demo_gate_surface_report.json",
            "reports/build_logs/buyer_demo_gate_banner_report.json",
            "reports/build_logs/owner_demo_surface_report.json",
            "reports/build_logs/ocp420_one_click_runtime_report.json",
            "reports/build_logs/full_rebuild_wiki_relations_report.json",
        ],
    }

    REPORT_JSON.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Owner Demo Script Packet",
        "",
        f"- current_stage: `{current_stage}`",
        f"- current_scope: `{current_scope}`",
        f"- owner_demo_pass_rate: `{rehearsal.get('owner_critical_scenario_pass_rate')}`",
        f"- blockers: `{', '.join(str(x) for x in (rehearsal.get('blockers') or [])) or 'none'}`",
        "",
        "## Opening Statement",
        "",
        packet["opening_statement"],
        "",
        "## Demo Flow",
        "",
    ]
    for row in demo_flow:
        lines.extend(
            [
                f"### Step {row['step']}. {row['title']}",
                "",
                f"- show: {row['show']}",
                f"- why: {row['why']}",
                "",
            ]
        )
    lines.extend(["## Owner Questions", ""])
    for row in scenario_rows:
        lines.extend(
            [
                f"### {row['id']} :: {row['question']}",
                "",
                f"- passed: `{row['passed']}`",
                f"- talk_track: {row['talk_track']}",
                "- evidence:",
            ]
        )
        for evidence in row["evidence"]:
            lines.append(f"  - {evidence}")
        lines.append("")
    lines.extend(["## What We Promise Now", ""])
    lines.extend([f"- {item}" for item in promise_now] or ["- none"])
    lines.extend(["", "## What We Explicitly Do Not Promise Yet", ""])
    lines.extend([f"- {item}" for item in non_promises] or ["- none"])
    lines.extend(["", "## Full-Sale Promotion Gate", ""])
    lines.extend([f"- {item}" for item in promotion_gate] or ["- none"])
    lines.extend(["", "## Hard Blockers", ""])
    lines.extend([f"- {item}" for item in hard_blockers] or ["- none"])
    lines.extend(["", "## Closing Statement", "", packet["closing_statement"], ""])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(packet, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
