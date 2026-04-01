from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config



def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    stage05 = load_json(REPO_ROOT / "data" / "manifests" / "generated" / "stage05-regression-summary.json")
    stage06 = load_json(REPO_ROOT / "data" / "manifests" / "generated" / "stage06-regression-summary.json")
    stage07 = load_json(REPO_ROOT / "data" / "manifests" / "generated" / "stage07-refresh-cycle-summary.json")
    stage08 = load_json(REPO_ROOT / "data" / "manifests" / "generated" / "stage08-live-runtime-report.json")
    stage09 = load_json(REPO_ROOT / "data" / "manifests" / "generated" / "stage09-repository-map-check.json")

    current_index = (REPO_ROOT / "indexes" / "current.txt").read_text(encoding="utf-8").strip()
    previous_index = (REPO_ROOT / "indexes" / "previous.txt").read_text(encoding="utf-8").strip()
    runtime = load_runtime_config()

    policy_summary = stage05["policy_summary"]
    gates = {
        "stage05_policy_gate": (
            policy_summary["source_dir_hit@5"] >= 0.9
            and policy_summary["supporting_doc_hit@10"] >= 0.9
            and policy_summary["citation_correctness"] >= 0.9
        ),
        "stage06_suite_gate": bool(stage06.get("pass")) and stage06.get("overall_decision") == "go",
        "stage07_refresh_gate": bool(stage07.get("pass")) and current_index == "s15c-core" and previous_index == "s07r-core",
        "stage08_serving_gate": bool(stage08.get("overall_pass")),
        "stage09_repository_gate": bool(stage09.get("pass")),
        "runtime_contract_gate": (
            runtime.company_base_url
            and runtime.chat_model
            and runtime.embedding_model == "BAAI/bge-m3"
            and runtime.embedding_dimensions == 1024
            and runtime.runtime_mode() == "company-only"
            and not runtime.allow_local_chat_fallback
        ),
    }

    all_hard_gates = all(gates.values())

    uncertified_items = []
    release_risks = []

    if stage05["raw_summary"]["supporting_doc_hit@10"] < 0.5:
        release_risks.append("raw retrieval baseline is still weak on widened corpus; current quality depends on policy-prepared retrieval")
    if stage07.get("equivalent_smoke_used_for_activation"):
        release_risks.append("Stage 7 activation relied on equivalent widened-corpus smoke evidence instead of a fresh duplicate-index smoke pass")
    if stage08.get("bridge_health", {}).get("company_token_configured") is False:
        release_risks.append("current local runtime succeeds without a configured company bearer token; future auth changes may require token provisioning")
    if current_index != "s15c-core":
        release_risks.append("current active index is not the validated widened corpus baseline")
    if stage08.get("bridge_health", {}).get("missing_gateway_keys"):
        uncertified_items.append("gateway env contract still relies on runtime injection for OD_SERVER_BASE_URL")
    uncertified_items.extend(
        [
            "operator-release minor is not pinned yet; current verdict applies to validation-mode widened corpus",
            "this verdict does not replace Stage 5/6 retrieval authority; it summarizes them",
            "this verdict does not certify future release-profile corpora until a target minor profile is selected and rerun",
        ]
    )

    if all_hard_gates:
        final_verdict = "conditional-go"
        verdict_reason = "The repo is demoable and submission-ready for the current validation-mode widened corpus, but not yet certified as a release-pinned operator deployment."
    else:
        final_verdict = "no-go"
        verdict_reason = "One or more hard gates failed; the current build is not ready for integrated release/demo sign-off."

    report = {
        "stage": 10,
        "current_index": current_index,
        "previous_index": previous_index,
        "gates": gates,
        "policy_summary": {
            "source_dir_hit@5": policy_summary["source_dir_hit@5"],
            "supporting_doc_hit@10": policy_summary["supporting_doc_hit@10"],
            "citation_correctness": policy_summary["citation_correctness"],
            "raw_supporting_doc_hit@10": stage05["raw_summary"]["supporting_doc_hit@10"],
        },
        "multiturn_summary": stage06["multiturn_summary"],
        "red_team_summary": stage06["red_team_summary"],
        "refresh_summary": {
            "pass": stage07["pass"],
            "restored_index_id": stage07["restored_index_id"],
            "equivalent_smoke_used_for_activation": stage07["equivalent_smoke_used_for_activation"],
            "restored_runtime_authority_index_id": stage07["restored_runtime_authority_index_id"],
        },
        "serving_summary": {
            "overall_pass": stage08["overall_pass"],
            "checks": stage08["checks"],
            "runtime_mode": stage08["bridge_evidence"]["runtime_mode"],
            "embedding_model": stage08["bridge_ready"]["embedding_model"],
            "embedding_dimensions": stage08["bridge_ready"]["embedding_dimensions"],
        },
        "repository_summary": {
            "pass": stage09["pass"],
            "missing_core_paths": stage09["missing_core_paths"],
            "missing_support_paths": stage09["missing_support_paths"],
            "missing_directories": stage09["missing_directories"],
            "root_python_files_present": stage09["root_python_files_present"],
        },
        "runtime_contract": {
            "runtime_mode": runtime.runtime_mode(),
            "chat_model": runtime.chat_model,
            "embedding_model": runtime.embedding_model,
            "embedding_dimensions": runtime.embedding_dimensions,
            "local_chat_fallback": runtime.allow_local_chat_fallback,
            "company_base_url_configured": bool(runtime.company_base_url),
        },
        "final_verdict": final_verdict,
        "verdict_reason": verdict_reason,
        "release_risks": release_risks,
        "uncertified_items": uncertified_items,
    }

    output_path = REPO_ROOT / "data" / "manifests" / "generated" / "stage10-final-release-gate.json"
    write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
