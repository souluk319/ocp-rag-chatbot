from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REALWORLD_REPORT = ROOT / "reports" / "build_logs" / "corpus_long_test_answer_eval_realworld_report.json"
OUTPUT_JSON = ROOT / "reports" / "build_logs" / "answer_quality_gate_report.json"
OUTPUT_MD = ROOT / "reports" / "build_logs" / "answer_quality_gate_report.md"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    realworld = _load_json(REALWORLD_REPORT)
    overall = realworld.get("overall") if isinstance(realworld.get("overall"), dict) else {}
    assessment = realworld.get("realworld_assessment") if isinstance(realworld.get("realworld_assessment"), dict) else {}
    report = {
        "status": "ok",
        "case_count": int(realworld.get("case_count") or 0),
        "pass_rate": float(overall.get("pass_rate") or 0.0),
        "unsupported_assertion_rate": float(overall.get("no_evidence_but_asserted_rate") or 0.0),
        "clarification_needed_but_answered_rate": float(overall.get("clarification_needed_but_answered_rate") or 0.0),
        "evidence_linked_answer_rate": float(overall.get("expected_citation_rate") or 0.0),
        "strict_expected_only_rate": float(overall.get("strict_expected_only_rate") or 0.0),
        "pass_with_provenance_noise_rate": float(overall.get("pass_with_provenance_noise_rate") or 0.0),
        "realworld_status": str(assessment.get("status") or ""),
        "realworld_failed_case_count": int(assessment.get("failed_case_count") or 0),
        "provenance_noise_case_count": len(assessment.get("provenance_noise_case_ids") or []),
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Answer Quality Gate Report",
                "",
                f"- case_count: `{report['case_count']}`",
                f"- pass_rate: `{report['pass_rate']}`",
                f"- unsupported_assertion_rate: `{report['unsupported_assertion_rate']}`",
                f"- clarification_needed_but_answered_rate: `{report['clarification_needed_but_answered_rate']}`",
                f"- evidence_linked_answer_rate: `{report['evidence_linked_answer_rate']}`",
                f"- strict_expected_only_rate: `{report['strict_expected_only_rate']}`",
                f"- pass_with_provenance_noise_rate: `{report['pass_with_provenance_noise_rate']}`",
                f"- realworld_status: `{report['realworld_status']}`",
                f"- realworld_failed_case_count: `{report['realworld_failed_case_count']}`",
                f"- provenance_noise_case_count: `{report['provenance_noise_case_count']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
