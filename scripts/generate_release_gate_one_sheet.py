from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "build_logs" / "release_gate_one_sheet.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "release_gate_one_sheet.md"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    scorecard = yaml.safe_load((ROOT / "OWNER_SCENARIO_SCORECARD.yaml").read_text(encoding="utf-8")) or {}
    owner_demo = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_rehearsal_report.json")
    owner_sheet = _load_json(ROOT / "reports" / "build_logs" / "owner_demo_one_sheet.json")
    gate_banner = _load_json(ROOT / "reports" / "build_logs" / "buyer_demo_gate_banner_report.json")

    promotion_gate = [str(item) for item in (((scorecard.get("promotion_gate") or {}).get("full_sale_requires")) or [])]
    release_blockers = [str(item) for item in (scorecard.get("release_blockers") or [])]
    current_stage = str(scorecard.get("current_stage") or "")
    current_scope = str(scorecard.get("current_scope") or "")

    sheet = {
        "status": "ok",
        "title": "Release Gate One-Sheet",
        "current_stage": current_stage,
        "current_scope": current_scope,
        "sell_now": "paid PoC candidate",
        "do_not_sell_yet": "full sale",
        "gate_status": gate_banner.get("status"),
        "owner_demo_pass_rate": owner_demo.get("owner_critical_scenario_pass_rate"),
        "owner_demo_blockers": owner_demo.get("blockers") or [],
        "promotion_gate": promotion_gate,
        "release_blockers": release_blockers,
        "commercial_boundary": {
            "now": "OpenShift 4.20 validated pack + customer document PoC",
            "later": "full-sale technical wiki platform",
        },
        "why_not_full_sale_yet": [
            "scorecard gate 는 통과 조건을 명시하지만 현재 stage 는 paid_poc_candidate 로 고정돼 있다.",
            "release blockers 는 unsupported assertion, boundary blur, source trace missing 같은 hard failure 를 포함한다.",
            "full sale 은 owner demo pass 외에도 evidence_linked_answer_rate, persisted_session, audit_trail, customer reference case 를 함께 요구한다.",
        ],
        "entry_points": owner_sheet.get("live_entry_points") or [],
        "close": "지금은 paid PoC candidate 로 제안하고, full sale 은 release gate 전항목 충족 후에만 승격한다.",
        "inputs": [
            "OWNER_SCENARIO_SCORECARD.yaml",
            "reports/build_logs/owner_demo_rehearsal_report.json",
            "reports/build_logs/owner_demo_one_sheet.json",
            "reports/build_logs/buyer_demo_gate_banner_report.json",
        ],
    }

    REPORT_JSON.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Release Gate One-Sheet",
        "",
        f"- current_stage: `{current_stage}`",
        f"- current_scope: `{current_scope}`",
        f"- sell_now: `{sheet['sell_now']}`",
        f"- do_not_sell_yet: `{sheet['do_not_sell_yet']}`",
        f"- owner_demo_pass_rate: `{sheet['owner_demo_pass_rate']}`",
        "",
        "## Commercial Boundary",
        "",
        f"- now: {sheet['commercial_boundary']['now']}",
        f"- later: {sheet['commercial_boundary']['later']}",
        "",
        "## Why Not Full Sale Yet",
        "",
    ]
    lines.extend(f"- {item}" for item in sheet["why_not_full_sale_yet"])
    lines.extend(["", "## Full-Sale Promotion Gate", ""])
    lines.extend(f"- {item}" for item in promotion_gate)
    lines.extend(["", "## Release Blockers", ""])
    lines.extend(f"- {item}" for item in release_blockers)
    lines.extend(["", "## Demo Entry Points", ""])
    for item in sheet["entry_points"]:
        if not isinstance(item, dict):
            continue
        lines.append(f"- {item.get('label')}: `{item.get('route')}`")
    lines.extend(["", "## Close", "", sheet["close"], ""])

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(sheet, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
