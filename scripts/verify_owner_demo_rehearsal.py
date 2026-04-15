from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import yaml

from play_book_studio.app.data_control_room import build_data_control_room_payload


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "owner_demo_rehearsal_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "owner_demo_rehearsal_report.md"
CHAT_URL = "http://127.0.0.1:8765/api/chat"


def _post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    scorecard = yaml.safe_load((ROOT / "OWNER_SCENARIO_SCORECARD.yaml").read_text(encoding="utf-8"))
    project = (ROOT / "PROJECT.md").read_text(encoding="utf-8")
    contract = (ROOT / "Q1_8_PRODUCT_CONTRACT.md").read_text(encoding="utf-8")
    control_payload = build_data_control_room_payload(ROOT)

    relation_report = _load_json(ROOT / "reports" / "build_logs" / "full_rebuild_wiki_relations_report.json")
    overlay_report = _load_json(ROOT / "reports" / "build_logs" / "wiki_overlay_usage_signals_report.json")
    customer_surface_report = _load_json(ROOT / "reports" / "build_logs" / "customer_pack_surface_report.json")
    buyer_gate_surface_report = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_gate_surface_report.json")

    chat_response = _post_json(
        CHAT_URL,
        {
            "query": "etcd 백업 절차와 관련 문서를 보여줘",
            "session_id": "owner-demo-rehearsal",
            "mode": "ops",
            "user_id": "owner-demo-rehearsal",
        },
    )
    citations = [item for item in (chat_response.get("citations") or []) if isinstance(item, dict)]
    related_links = [item for item in (chat_response.get("related_links") or []) if isinstance(item, dict)]
    related_sections = [item for item in (chat_response.get("related_sections") or []) if isinstance(item, dict)]

    scenarios = []

    scenario_1_pass = (
        "connected technical wiki for operation and learning" in contract
        and "paid_poc_candidate" in contract
        and "What We Explicitly Do Not Promise Yet" in contract
    )
    scenarios.append(
        {
            "id": "owner-001",
            "question": "왜 이걸 사야 하나?",
            "passed": scenario_1_pass,
            "evidence": [
                "Q1_8_PRODUCT_CONTRACT.md declares connected technical wiki runtime",
                "Q1_8_PRODUCT_CONTRACT.md fixes current stage as paid_poc_candidate",
                "current non-promises remain explicit",
            ],
        }
    )

    approved_runtime_count = int(((control_payload.get("summary") or {}).get("approved_wiki_runtime_book_count") or 0))
    relation_book_count = int(relation_report.get("candidate_relation_count") or 0)
    scenario_2_pass = approved_runtime_count >= 29 and relation_book_count >= 29
    scenarios.append(
        {
            "id": "owner-002",
            "question": "실제로 뭘 보게 되나?",
            "passed": scenario_2_pass,
            "evidence": [
                f"approved_wiki_runtime_book_count={approved_runtime_count}",
                f"relation_book_count={relation_book_count}",
                "runtime is surfaced as connected book/entity/figure wiki",
            ],
        }
    )

    scenario_3_pass = any(str(item.get("viewer_path") or "").strip() for item in citations) and any(
        str(item.get("source_url") or "").strip() for item in citations
    )
    scenarios.append(
        {
            "id": "owner-003",
            "question": "이 답이 어디서 왔나?",
            "passed": scenario_3_pass,
            "evidence": [
                f"citation_count={len(citations)}",
                f"related_links={len(related_links)}",
                "chat response includes viewer_path and source_url on citations",
            ],
        }
    )

    scenario_4_pass = (
        customer_surface_report.get("status") == "ok"
        and str(customer_surface_report.get("citation_boundary_truth") or "") == "private_customer_pack_runtime"
        and buyer_gate_surface_report.get("status") == "ok"
    )
    scenarios.append(
        {
            "id": "owner-004",
            "question": "고객 문서도 넣을 수 있나?",
            "passed": scenario_4_pass,
            "evidence": [
                f"customer_pack_surface_status={customer_surface_report.get('status')}",
                f"customer_boundary_truth={customer_surface_report.get('citation_boundary_truth')}",
                "buyer demo gate surface is active for commercial boundary explanation",
            ],
        }
    )

    scenario_5_pass = (
        overlay_report.get("status") == "ok"
        and len(related_links) > 0
        and len(related_sections) > 0
        and int(overlay_report.get("recommended_next_play_count") or 0) > 0
    )
    scenarios.append(
        {
            "id": "owner-005",
            "question": "운영에 실제로 도움이 되나?",
            "passed": scenario_5_pass,
            "evidence": [
                f"related_links={len(related_links)}",
                f"related_sections={len(related_sections)}",
                f"recommended_next_play_count={overlay_report.get('recommended_next_play_count')}",
            ],
        }
    )

    passed_count = sum(1 for item in scenarios if item["passed"])
    pass_rate = round(passed_count / len(scenarios), 4) if scenarios else 0.0
    blockers = [item["id"] for item in scenarios if not item["passed"]]

    report = {
        "status": "ok" if not blockers else "failed",
        "current_stage": str(scorecard.get("current_stage") or ""),
        "scenario_count": len(scenarios),
        "pass_count": passed_count,
        "owner_critical_scenario_pass_rate": pass_rate,
        "blockers": blockers,
        "scenarios": scenarios,
        "chat_probe": {
            "citation_count": len(citations),
            "related_link_count": len(related_links),
            "related_section_count": len(related_sections),
        },
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Owner Demo Rehearsal Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- current_stage: `{report['current_stage']}`\n"
        + f"- scenario_count: `{report['scenario_count']}`\n"
        + f"- pass_count: `{report['pass_count']}`\n"
        + f"- owner_critical_scenario_pass_rate: `{report['owner_critical_scenario_pass_rate']}`\n"
        + f"- blockers: `{', '.join(blockers) if blockers else 'none'}`\n\n"
        + "\n".join(
            f"- {row['id']} `{row['passed']}` :: " + " | ".join(str(item) for item in row["evidence"])
            for row in scenarios
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
