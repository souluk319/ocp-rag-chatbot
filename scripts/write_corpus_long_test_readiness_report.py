from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_effective_env, load_settings


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else []


def _foundry_eval_wiring_status(path: Path) -> dict:
    payload = _read_json(path)
    jobs = payload.get("jobs", {}) if isinstance(payload, dict) else {}
    profiles = payload.get("profiles", []) if isinstance(payload, dict) else []
    eval_job_ids = [
        job_id
        for job_id in jobs
        if any(token in job_id for token in ("retrieval", "answer", "ragas", "corpus"))
    ]
    profiled_eval_jobs = []
    for profile in profiles if isinstance(profiles, list) else []:
        if not isinstance(profile, dict):
            continue
        for job_id in profile.get("jobs", []):
            if any(token in str(job_id) for token in ("retrieval", "answer", "ragas", "corpus")):
                profiled_eval_jobs.append(
                    {
                        "profile_id": str(profile.get("id", "")),
                        "job_id": str(job_id),
                    }
                )
    return {
        "job_ids": eval_job_ids,
        "profiled_eval_jobs": profiled_eval_jobs,
        "scheduled_eval_profile_exists": bool(profiled_eval_jobs),
    }


def _artifact_record(path: Path) -> dict:
    return {
        "path": str(path),
        "exists": path.exists(),
    }


def _bundle_commands() -> list[dict]:
    return [
        {
            "id": "retrieval_eval",
            "kind": "runner",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\codex_python.ps1 -ScriptPath scripts\\run_retrieval_eval.py -WriteScope \"src/play_book_studio/evals/retrieval_eval.py;manifests/retrieval_eval_cases.jsonl;artifacts/retrieval/retrieval_eval_report.json\" -VerifyCmd \"artifacts/retrieval/retrieval_eval_report.json updated\" --output artifacts/retrieval/retrieval_eval_report.json",
        },
        {
            "id": "answer_eval_core",
            "kind": "runner",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\codex_python.ps1 -ScriptPath scripts\\run_answer_eval.py -WriteScope \"scripts/run_answer_eval.py;manifests/answer_eval_cases.jsonl;artifacts/answering/answer_eval_report.json\" -VerifyCmd \"artifacts/answering/answer_eval_report.json updated\" --cases manifests\\answer_eval_cases.jsonl",
        },
        {
            "id": "answer_eval_realworld",
            "kind": "runner",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\codex_python.ps1 -ScriptPath scripts\\run_answer_eval.py -WriteScope \"scripts/run_answer_eval.py;manifests/answer_eval_realworld_cases.jsonl;reports/build_logs/corpus_long_test_answer_eval_realworld_report.json\" -VerifyCmd \"reports/build_logs/corpus_long_test_answer_eval_realworld_report.json updated\" --cases manifests\\answer_eval_realworld_cases.jsonl",
        },
        {
            "id": "ragas_dry_run",
            "kind": "runner",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\codex_python.ps1 -ScriptPath scripts\\run_ragas_eval.py -WriteScope \"scripts/run_ragas_eval.py;manifests/ragas_eval_cases.jsonl;artifacts/answering/ragas_eval_dataset_preview.json\" -VerifyCmd \"artifacts/answering/ragas_eval_dataset_preview.json updated\" --cases manifests\\ragas_eval_cases.jsonl --dry-run",
        },
        {
            "id": "continuity_and_no_answer_unit",
            "kind": "unit-test",
            "command": ".\\.venv\\Scripts\\python.exe -m unittest tests.test_answer_eval tests.test_app_session_flow.TestAppSessionFlow.test_derive_next_context_preserves_route_ingress_topic_for_compare_follow_up tests.test_app_session_flow.TestAppSessionFlow.test_derive_next_context_marks_unresolved_when_no_citations tests.test_app_session_flow.TestAppSessionFlow.test_suggest_follow_up_questions_for_route_ingress_follow_play_flow tests.test_app_session_flow.TestAppSessionFlow.test_suggest_follow_up_questions_uses_citation_metadata_for_procedure_flow tests.test_app_session_flow.TestAppSessionFlow.test_suggest_follow_up_questions_for_no_answer_returns_fallback_triplet tests.test_app_session_flow.TestAppSessionFlow.test_suggest_follow_up_questions_with_warnings_returns_empty tests.test_answering_output.TestAnsweringOutput.test_finalize_citations_collapses_duplicate_targets tests.test_answering_output.TestAnsweringOutput.test_answerer_deduplicates_same_section_citations tests.test_answering_output.TestAnsweringOutput.test_answerer_blocks_single_missing_inline_citation",
        },
    ]


def main() -> int:
    settings = load_settings(ROOT)
    effective_env = load_effective_env(ROOT)

    retrieval_report_path = settings.retrieval_eval_report_path
    answer_report_path = settings.answer_eval_report_path
    ragas_preview_path = settings.ragas_dataset_preview_path
    ragas_eval_report_path = settings.ragas_eval_report_path
    answer_core_report_path = ROOT / "reports" / "build_logs" / "corpus_long_test_answer_eval_core_report.json"
    answer_realworld_report_path = ROOT / "reports" / "build_logs" / "corpus_long_test_answer_eval_realworld_report.json"
    foundry_profiles_path = ROOT / "pipelines" / "foundry_routines.json"
    runtime_smoke_latest_path = ROOT / "reports" / "build_logs" / "foundry_runs" / "profiles" / "runtime_smoke_hourly" / "latest.json"
    output_path = ROOT / "reports" / "build_logs" / "corpus_long_test_readiness_report.json"

    retrieval_report = _read_json(retrieval_report_path)
    answer_report = _read_json(answer_report_path)
    answer_core_report = _read_json(answer_core_report_path)
    answer_realworld_report = _read_json(answer_realworld_report_path)
    ragas_preview = _read_json_list(ragas_preview_path)
    runtime_smoke_latest = _read_json(runtime_smoke_latest_path)
    foundry_eval_status = _foundry_eval_wiring_status(foundry_profiles_path)

    retrieval_overall = retrieval_report.get("overall", {}) if isinstance(retrieval_report, dict) else {}
    retrieval_by_category = retrieval_report.get("by_category", {}) if isinstance(retrieval_report, dict) else {}
    answer_overall = answer_core_report.get("overall", {}) if isinstance(answer_core_report, dict) else {}
    answer_realworld = (
        answer_realworld_report.get("realworld_assessment", {})
        if isinstance(answer_realworld_report, dict)
        else {}
    )
    runtime_artifacts = (
        runtime_smoke_latest.get("job_results", [{}])[0].get("payload", {}).get("artifacts", {})
        if isinstance(runtime_smoke_latest, dict)
        else {}
    )

    known_gaps: list[str] = []
    if answer_realworld.get("status") == "insufficient":
        known_gaps.append("realworld answer gate is still insufficient and needs provenance/generation fixes")
    if not foundry_eval_status["scheduled_eval_profile_exists"]:
        known_gaps.append("foundry schedules do not yet include retrieval/answer/ragas corpus eval jobs")
    if not effective_env.get("OPENAI_API_KEY", "").strip():
        known_gaps.append("live ragas judge is not ready because OPENAI_API_KEY is absent; dry-run only is available")
    known_gaps.extend(
        [
            "answer-side anchor landing is not scored separately from retrieval landing",
            "no-answer and follow-up quality are protected by unit tests but not yet aggregated into a numeric runtime report",
        ]
    )

    report = {
        "status": "ready",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "meta": {
            "task_id": "corpus_long_test_readiness_20260416",
            "pack_id": settings.active_pack_id,
            "pack_label": settings.active_pack_label,
            "ocp_version": settings.ocp_version,
            "docs_language": settings.docs_language,
            "retrieval_case_count": retrieval_report.get("case_count", 0),
            "answer_core_case_count": answer_core_report.get("case_count", 0),
            "answer_realworld_case_count": answer_realworld_report.get("case_count", 0),
            "ragas_preview_case_count": len(ragas_preview),
        },
        "test_settings": {
            "active_runners": [
                "scripts/run_retrieval_eval.py",
                "scripts/run_answer_eval.py",
                "scripts/run_ragas_eval.py",
            ],
            "active_manifests": [
                "manifests/retrieval_eval_cases.jsonl",
                "manifests/answer_eval_cases.jsonl",
                "manifests/answer_eval_realworld_cases.jsonl",
                "manifests/ragas_eval_cases.jsonl",
            ],
            "active_unit_focus": [
                "tests/test_retrieval_eval.py",
                "tests/test_answer_eval.py",
                "tests/test_app_session_flow.py",
                "tests/test_answering_output.py",
            ],
        },
        "retrieval_gate": {
            "ready": retrieval_report_path.exists(),
            "book_hit_at_5": retrieval_overall.get("book_hit_at_5", 0.0),
            "landing_hit_at_5": retrieval_overall.get("landing_hit_at_5", 0.0),
            "warning_free_rate": retrieval_overall.get("warning_free_rate", 0.0),
            "similar_document_risk_rate": retrieval_overall.get("similar_document_risk_rate", 0.0),
            "relation_aware_miss_rate": retrieval_overall.get("relation_aware_miss_rate", 0.0),
            "ambiguous_case_count": (retrieval_by_category.get("ambiguous") or {}).get("case_count", 0),
        },
        "answer_gate": {
            "ready": answer_core_report_path.exists(),
            "pass_rate": answer_overall.get("pass_rate", 0.0),
            "inline_citation_rate": answer_overall.get("inline_citation_rate", 0.0),
            "avg_citation_precision": answer_overall.get("avg_citation_precision", 0.0),
            "clarification_needed_but_answered_rate": answer_overall.get("clarification_needed_but_answered_rate", 0.0),
            "no_evidence_but_asserted_rate": answer_overall.get("no_evidence_but_asserted_rate", 0.0),
            "pass_with_provenance_noise_rate": answer_overall.get("pass_with_provenance_noise_rate", 0.0),
            "realworld_status": answer_realworld.get("status", ""),
            "realworld_failed_case_count": answer_realworld.get("failed_case_count", 0),
            "realworld_root_cause_counts": answer_realworld.get("root_cause_counts", {}),
            "realworld_provenance_noise_case_ids": answer_realworld.get("provenance_noise_case_ids", []),
        },
        "continuity_gate": {
            "ready": True,
            "verification_mode": "targeted_unit_tests",
            "tests": [
                "test_derive_next_context_preserves_route_ingress_topic_for_compare_follow_up",
                "test_derive_next_context_marks_unresolved_when_no_citations",
                "test_suggest_follow_up_questions_for_route_ingress_follow_play_flow",
                "test_suggest_follow_up_questions_uses_citation_metadata_for_procedure_flow",
            ],
            "current_metric_status": "unit-test coverage only",
        },
        "no_answer_gate": {
            "ready": True,
            "verification_mode": "targeted_unit_tests",
            "tests": [
                "test_suggest_follow_up_questions_for_no_answer_returns_fallback_triplet",
                "test_suggest_follow_up_questions_with_warnings_returns_empty",
            ],
            "fallback_behavior": "returns three contextual questions when no retrieval-backed suggestions exist",
        },
        "ragas_gate": {
            "ready": ragas_preview_path.exists(),
            "mode": "dry_run",
            "preview_case_count": len(ragas_preview),
            "live_judge_ready": bool(effective_env.get("OPENAI_API_KEY", "").strip()),
            "live_report_exists": ragas_eval_report_path.exists(),
            "coverage_note": "current ragas cases are ops-only",
        },
        "bundle_orchestration": {
            "ready": True,
            "foundry_eval_wiring": foundry_eval_status,
            "runtime_smoke_latest": {
                "path": str(runtime_smoke_latest_path),
                "exists": runtime_smoke_latest_path.exists(),
                "answer_eval_report_exists": bool((runtime_artifacts.get("answer_eval_report") or {}).get("exists", False)),
                "ragas_eval_report_exists": bool((runtime_artifacts.get("ragas_eval_report") or {}).get("exists", False)),
                "retrieval_eval_report_exists": bool((runtime_artifacts.get("retrieval_eval_report") or {}).get("exists", False)),
            },
            "command_bundle": _bundle_commands(),
        },
        "artifact_paths": {
            "retrieval_eval_report": _artifact_record(retrieval_report_path),
            "answer_eval_report_active": _artifact_record(answer_report_path),
            "answer_eval_report_core": _artifact_record(answer_core_report_path),
            "answer_eval_report_realworld": _artifact_record(answer_realworld_report_path),
            "ragas_dataset_preview": _artifact_record(ragas_preview_path),
            "ragas_eval_report": _artifact_record(ragas_eval_report_path),
            "runtime_smoke_latest": _artifact_record(runtime_smoke_latest_path),
        },
        "known_gaps": known_gaps,
        "long_run_bundle": {
            "ready": True,
            "entrypoint": "reports/build_logs/corpus_long_test_readiness_report.json",
            "phases": [
                "retrieval_eval",
                "answer_eval_core",
                "answer_eval_realworld",
                "ragas_dry_run",
                "continuity_and_no_answer_unit",
            ],
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote corpus long test readiness report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
