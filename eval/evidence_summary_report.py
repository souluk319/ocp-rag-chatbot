from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize current planB evidence artifacts."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "data"
        / "manifests"
        / "generated"
        / "evidence-summary-report.json",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_pointer(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    args = parse_args()
    generated = REPO_ROOT / "data" / "manifests" / "generated"
    cache_report = read_json(generated / "cache-strategy-report.json")
    vector_report = read_json(generated / "vector-index-proof.json")
    stage11_reindex = read_json(generated / "stage11-4-20-seed-reindex-report.json")
    stage11_smoke = read_json(generated / "stage11-4-20-seed-smoke-report.json")
    stage11_activation = read_json(
        generated / "stage11-4-20-seed-activation-report.json"
    )
    stage12_live = read_json(generated / "stage12-live-runtime-report.json")
    multiturn_report = read_json(
        REPO_ROOT / "eval" / "fixtures" / "multiturn_rewrite_sample_report.json"
    )
    current_index = read_pointer(REPO_ROOT / "indexes" / "current.txt")

    report = {
        "trace_version": "evidence-summary-v1",
        "current_index": current_index,
        "evidence": {
            "stage11_reindex": {
                "path": "data/manifests/generated/stage11-4-20-seed-reindex-report.json",
                "index_id": stage11_reindex.get("index_id"),
                "overall_pass": bool(stage11_reindex.get("valid_for_activation")),
            },
            "stage11_activation": {
                "path": "data/manifests/generated/stage11-4-20-seed-activation-report.json",
                "current_after": stage11_activation.get("current_after"),
                "activation_succeeded": bool(
                    stage11_activation.get("activation_succeeded")
                ),
            },
            "stage11_smoke": {
                "path": "data/manifests/generated/stage11-4-20-seed-smoke-report.json",
                "overall_pass": bool(stage11_smoke.get("overall_pass")),
                "runtime_smoke_pass": bool(stage11_smoke.get("runtime_smoke_pass")),
                "retrieval_alignment_pass": bool(
                    stage11_smoke.get("retrieval_alignment_pass")
                ),
                "failed_case_ids": stage11_smoke.get("failed_case_ids", []),
                "retrieval_alignment_failed_case_ids": stage11_smoke.get(
                    "retrieval_alignment_failed_case_ids", []
                ),
            },
            "stage12_live_runtime": {
                "path": "data/manifests/generated/stage12-live-runtime-report.json",
                "overall_pass": bool(stage12_live.get("overall_pass")),
                "bridge_embedding_transport": stage12_live.get("bridge_ready", {}).get(
                    "embedding_transport"
                ),
                "bridge_embedding_dimensions": stage12_live.get("bridge_ready", {}).get(
                    "embedding_dimensions"
                ),
                "gateway_active_index_id": stage12_live.get("gateway_health", {}).get(
                    "active_index_id"
                ),
                "local_chat_fallback": bool(
                    stage12_live.get("bridge_health", {}).get("local_chat_fallback")
                ),
            },
            "cache_strategy": {
                "path": "data/manifests/generated/cache-strategy-report.json",
                "overall_pass": bool(cache_report.get("overall_pass")),
                "embedding_cache_pass": bool(
                    cache_report.get("embedding_cache_report", {}).get("pass")
                ),
                "query_cache_pass": bool(
                    cache_report.get("query_cache_report", {}).get("pass")
                ),
            },
            "vector_index_proof": {
                "path": "data/manifests/generated/vector-index-proof.json",
                "overall_pass": bool(vector_report.get("overall_pass")),
                "record_count": vector_report.get("record_count"),
                "dimensions": vector_report.get("dimensions"),
            },
            "multiturn_proof": {
                "path": "eval/fixtures/multiturn_rewrite_sample_report.json",
                "scope": "sample-fixture-proof",
                "scenario_count": multiturn_report.get("summary", {}).get(
                    "scenario_count"
                ),
                "turn_count": multiturn_report.get("summary", {}).get("turn_count"),
                "fully_passing_scenarios": multiturn_report.get("summary", {}).get(
                    "fully_passing_scenarios"
                ),
                "rewrite_term_pass_rate": multiturn_report.get("summary", {}).get(
                    "rewrite_term_pass_rate"
                ),
            },
        },
        "summary": {
            "runtime_stack_ready": bool(stage12_live.get("overall_pass")),
            "retrieval_alignment_ready": bool(
                stage11_smoke.get("retrieval_alignment_pass")
            ),
            "cache_proof_ready": bool(cache_report.get("overall_pass")),
            "vector_index_proof_ready": bool(vector_report.get("overall_pass")),
            "multiturn_sample_proof_ready": bool(
                multiturn_report.get("summary", {}).get("fully_passing_scenarios")
                == multiturn_report.get("summary", {}).get("scenario_count")
            ),
        },
    }
    report["summary"]["overall_ready_for_score_defense"] = all(
        report["summary"].values()
    )

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
