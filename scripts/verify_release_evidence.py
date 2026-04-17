from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _build_logs_path(root: Path, filename: str) -> Path:
    return root / "reports" / "build_logs" / filename


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_release_evidence_report(root: Path = ROOT) -> dict:
    product_rehearsal_report = _build_logs_path(root, "product_rehearsal_report.json")
    buyer_packet_path = _build_logs_path(root, "buyer_packet_bundle_index.json")
    release_packet_path = _build_logs_path(root, "release_candidate_freeze_packet.json")

    product_rehearsal = _load_json(product_rehearsal_report)
    buyer_packet = _load_json(buyer_packet_path)
    release_packet = _load_json(release_packet_path)
    product_gate = release_packet.get("product_gate") if isinstance(release_packet.get("product_gate"), dict) else {}
    blockers: list[str] = []

    if not product_rehearsal_report.exists():
        blockers.append("product_rehearsal_report_missing")
    critical_pass_rate = product_rehearsal.get("critical_scenario_pass_rate")
    if product_rehearsal_report.exists() and not isinstance(critical_pass_rate, (int, float)):
        blockers.append("product_rehearsal_report_missing_critical_scenario_pass_rate")
    if not release_packet_path.exists():
        blockers.append("release_candidate_freeze_packet_missing")
    if release_packet_path.exists() and not product_gate:
        blockers.append("release_candidate_freeze_packet_missing_product_gate")

    report = {
        "status": "ok" if not blockers else "blocked",
        "product_rehearsal_exists": product_rehearsal_report.exists(),
        "product_rehearsal_blocker_count": len(product_rehearsal.get("blockers") or []),
        "critical_scenario_pass_rate": float(critical_pass_rate) if isinstance(critical_pass_rate, (int, float)) else None,
        "buyer_packet_exists": buyer_packet_path.exists(),
        "buyer_packet_count": int(buyer_packet.get("packet_count") or 0),
        "release_packet_exists": release_packet_path.exists(),
        "release_supporting_packet_count": len(release_packet.get("supporting_packets") or []),
        "release_packet_has_product_gate": bool(product_gate),
        "blockers": blockers,
    }
    return report


def main() -> int:
    report = build_release_evidence_report()
    output_json = _build_logs_path(ROOT, "release_evidence_report.json")
    output_md = _build_logs_path(ROOT, "release_evidence_report.md")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(
        "\n".join(
            [
                "# Release Evidence Report",
                "",
                f"- product_rehearsal_exists: `{report['product_rehearsal_exists']}`",
                f"- product_rehearsal_blocker_count: `{report['product_rehearsal_blocker_count']}`",
                f"- critical_scenario_pass_rate: `{report['critical_scenario_pass_rate']}`",
                f"- buyer_packet_exists: `{report['buyer_packet_exists']}`",
                f"- buyer_packet_count: `{report['buyer_packet_count']}`",
                f"- release_packet_exists: `{report['release_packet_exists']}`",
                f"- release_supporting_packet_count: `{report['release_supporting_packet_count']}`",
                f"- release_packet_has_product_gate: `{report['release_packet_has_product_gate']}`",
                f"- blockers: `{', '.join(report['blockers']) if report['blockers'] else 'none'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
