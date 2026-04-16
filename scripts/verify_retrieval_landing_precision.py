from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "reports" / "build_logs" / "retrieval_landing_precision_report.json"
OUTPUT_JSON = ROOT / "reports" / "build_logs" / "retrieval_landing_precision_summary.json"
OUTPUT_MD = ROOT / "reports" / "build_logs" / "retrieval_landing_precision_report.md"


def main() -> int:
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    overall = payload.get("overall") if isinstance(payload.get("overall"), dict) else {}
    summary = {
        "status": "ok",
        "case_count": int(payload.get("case_count") or 0),
        "book_hit_at_1": float(overall.get("book_hit_at_1") or 0.0),
        "book_hit_at_3": float(overall.get("book_hit_at_3") or 0.0),
        "book_hit_at_5": float(overall.get("book_hit_at_5") or 0.0),
        "landing_case_count": int(overall.get("landing_case_count") or 0),
        "landing_hit_at_1": float(overall.get("landing_hit_at_1") or 0.0),
        "landing_hit_at_3": float(overall.get("landing_hit_at_3") or 0.0),
        "landing_hit_at_5": float(overall.get("landing_hit_at_5") or 0.0),
        "warning_free_rate": float(overall.get("warning_free_rate") or 0.0),
        "similar_document_risk_rate": float(overall.get("similar_document_risk_rate") or 0.0),
        "relation_aware_miss_rate": float(overall.get("relation_aware_miss_rate") or 0.0),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# Retrieval Landing Precision Report",
                "",
                f"- case_count: `{summary['case_count']}`",
                f"- book_hit_at_1: `{summary['book_hit_at_1']}`",
                f"- book_hit_at_3: `{summary['book_hit_at_3']}`",
                f"- book_hit_at_5: `{summary['book_hit_at_5']}`",
                f"- landing_case_count: `{summary['landing_case_count']}`",
                f"- landing_hit_at_1: `{summary['landing_hit_at_1']}`",
                f"- landing_hit_at_3: `{summary['landing_hit_at_3']}`",
                f"- landing_hit_at_5: `{summary['landing_hit_at_5']}`",
                f"- warning_free_rate: `{summary['warning_free_rate']}`",
                f"- similar_document_risk_rate: `{summary['similar_document_risk_rate']}`",
                f"- relation_aware_miss_rate: `{summary['relation_aware_miss_rate']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
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
