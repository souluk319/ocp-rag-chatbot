from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "reports" / "build_logs" / "owner_demo_script_packet.json"
REPORT_JSON = ROOT / "reports" / "build_logs" / "owner_demo_script_packet_verification_report.json"
REPORT_MD = ROOT / "reports" / "build_logs" / "owner_demo_script_packet_verification_report.md"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object json: {path}")
    return payload


def main() -> int:
    packet = _load_json(PACKET_JSON)
    questions = [item for item in packet.get("questions") or [] if isinstance(item, dict)]
    demo_flow = [item for item in packet.get("demo_flow") or [] if isinstance(item, dict)]
    promise_now = [str(item) for item in (packet.get("promise_now") or []) if str(item).strip()]
    non_promises = [str(item) for item in (packet.get("non_promises") or []) if str(item).strip()]
    promotion_gate = [str(item) for item in (packet.get("promotion_gate") or []) if str(item).strip()]
    release_blockers = [str(item) for item in (packet.get("release_blockers") or []) if str(item).strip()]
    hard_blockers = [str(item) for item in (packet.get("hard_blockers") or []) if str(item).strip()]
    evidence_snapshot = packet.get("evidence_snapshot") if isinstance(packet.get("evidence_snapshot"), dict) else {}

    report = {
        "status": "ok",
        "title": str(packet.get("title") or ""),
        "current_stage": str(packet.get("current_stage") or ""),
        "current_scope": str(packet.get("current_scope") or ""),
        "opening_statement_present": bool(str(packet.get("opening_statement") or "").strip()),
        "demo_flow_count": len(demo_flow),
        "question_count": len(questions),
        "passed_question_count": sum(1 for item in questions if bool(item.get("passed"))),
        "promise_count": len(promise_now),
        "non_promise_count": len(non_promises),
        "promotion_gate_count": len(promotion_gate),
        "release_blocker_count": len(release_blockers),
        "hard_blocker_count": len(hard_blockers),
        "owner_demo_pass_rate": evidence_snapshot.get("owner_demo_pass_rate"),
        "runtime_book_count": evidence_snapshot.get("runtime_book_count"),
        "relation_book_count": evidence_snapshot.get("relation_book_count"),
        "gate_surface_status": evidence_snapshot.get("gate_surface_status"),
        "gate_banner_status": evidence_snapshot.get("gate_banner_status"),
        "owner_surface_status": evidence_snapshot.get("owner_surface_status"),
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(
        "# Owner Demo Script Packet Verification Report\n\n"
        + f"- status: `{report['status']}`\n"
        + f"- title: `{report['title']}`\n"
        + f"- current_stage: `{report['current_stage']}`\n"
        + f"- current_scope: `{report['current_scope']}`\n"
        + f"- opening_statement_present: `{report['opening_statement_present']}`\n"
        + f"- demo_flow_count: `{report['demo_flow_count']}`\n"
        + f"- question_count: `{report['question_count']}`\n"
        + f"- passed_question_count: `{report['passed_question_count']}`\n"
        + f"- promise_count: `{report['promise_count']}`\n"
        + f"- non_promise_count: `{report['non_promise_count']}`\n"
        + f"- promotion_gate_count: `{report['promotion_gate_count']}`\n"
        + f"- release_blocker_count: `{report['release_blocker_count']}`\n"
        + f"- hard_blocker_count: `{report['hard_blocker_count']}`\n"
        + f"- owner_demo_pass_rate: `{report['owner_demo_pass_rate']}`\n"
        + f"- runtime_book_count: `{report['runtime_book_count']}`\n"
        + f"- relation_book_count: `{report['relation_book_count']}`\n"
        + f"- gate_surface_status: `{report['gate_surface_status']}`\n"
        + f"- gate_banner_status: `{report['gate_banner_status']}`\n"
        + f"- owner_surface_status: `{report['owner_surface_status']}`\n",
        encoding="utf-8",
    )

    ok = (
        report["title"] == "Owner Demo Script Packet"
        and report["current_stage"] == "paid_poc_candidate"
        and report["current_scope"] == "openshift_4_20_source_first_validated_pack_plus_customer_document_poc"
        and report["opening_statement_present"]
        and report["demo_flow_count"] >= 5
        and report["question_count"] == 5
        and report["passed_question_count"] == 5
        and report["promise_count"] >= 15
        and report["non_promise_count"] >= 5
        and report["promotion_gate_count"] >= 8
        and report["release_blocker_count"] >= 7
        and report["hard_blocker_count"] >= 7
        and float(report["owner_demo_pass_rate"] or 0) == 1.0
        and int(report["runtime_book_count"] or 0) == 29
        and int(report["relation_book_count"] or 0) == 29
        and str(report["gate_surface_status"]) == "ok"
        and str(report["gate_banner_status"]) == "ok"
        and str(report["owner_surface_status"]) == "ok"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
