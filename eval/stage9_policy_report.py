from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.ocp_policy import load_policy_engine
from eval.retrieval_benchmark_report import load_records, summarize_by_case


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply Stage 9 OCP retrieval and answer policies to benchmark results.")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mode", default="operations")
    parser.add_argument("--output-results", type=Path)
    parser.add_argument("--output-report", type=Path)
    return parser.parse_args()


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lower()


def build_manifest_index(manifest_path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    documents = payload.get("documents", []) if isinstance(payload, dict) else payload
    manifest_index: dict[str, dict[str, Any]] = {}

    for document in documents:
        source_url = str(document.get("source_url", ""))
        if "/blob/main/" in source_url:
            relative_path = source_url.split("/blob/main/", 1)[1]
            manifest_index[normalize_path(relative_path)] = document
            continue

        local_path = str(document.get("local_path", ""))
        if local_path:
            marker = "openshift-docs\\"
            if marker in local_path:
                relative_path = local_path.split(marker, 1)[1]
                manifest_index[normalize_path(relative_path)] = document
    return manifest_index


def enrich_candidate(candidate: dict[str, Any], manifest_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    enriched = dict(candidate)
    document_path = normalize_path(str(candidate.get("document_path", "")))
    manifest_doc = manifest_index.get(document_path, {})

    for field in (
        "title",
        "product",
        "version",
        "category",
        "trust_level",
        "top_level_dir",
        "viewer_url",
    ):
        if field not in enriched or not enriched.get(field):
            enriched[field] = manifest_doc.get(field, enriched.get(field, ""))

    if not enriched.get("source_dir"):
        enriched["source_dir"] = manifest_doc.get("top_level_dir", "")

    sections = manifest_doc.get("sections", [])
    if sections and not enriched.get("section_title"):
        enriched["section_title"] = sections[0].get("section_title", "")
    return enriched


def build_citations(ranked_candidates: list[dict[str, Any]], max_sources: int = 3) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for candidate in ranked_candidates[:max_sources]:
        citations.append(
            {
                "document_path": candidate.get("document_path", ""),
                "viewer_url": candidate.get("viewer_url", ""),
                "section_title": candidate.get("section_title", ""),
            }
        )
    return citations


def main() -> None:
    args = parse_args()
    cases_raw = load_records(args.cases)
    results_raw = load_records(args.results)
    policy_engine = load_policy_engine()
    manifest_index = build_manifest_index(args.manifest)

    case_map = {str(case["id"]): case for case in cases_raw}
    ordered_cases = sorted(case_map.values(), key=lambda item: (str(item["scenario_id"]), int(item["turn_index"])))
    raw_results_by_id = {str(record["benchmark_case_id"]): record for record in results_raw}
    scenario_memory: dict[str, dict[str, Any]] = {}
    policy_results: list[dict[str, Any]] = []

    for case in ordered_cases:
        case_id = str(case["id"])
        raw_result = raw_results_by_id.get(case_id)
        if raw_result is None:
            continue

        scenario_id = str(case["scenario_id"])
        memory_state = dict(scenario_memory.get(scenario_id, {}))
        enriched_candidates = [
            enrich_candidate(candidate, manifest_index) for candidate in raw_result.get("retrieval_candidates", [])
        ]
        reranked_candidates, signals = policy_engine.rerank_candidates(
            case["question_ko"],
            enriched_candidates,
            mode=args.mode,
            memory_state=memory_state,
        )
        citations = build_citations(reranked_candidates)
        answer_contract = policy_engine.build_answer_contract(
            case["question_ko"],
            reranked_candidates,
            mode=args.mode,
            grounded=bool(citations),
            memory_state=memory_state,
        )

        top_candidate = reranked_candidates[0] if reranked_candidates else {}
        scenario_memory[scenario_id] = {
            "active_source_dirs": [top_candidate.get("source_dir", "")] if top_candidate.get("source_dir") else [],
            "active_categories": [top_candidate.get("category", "")] if top_candidate.get("category") else [],
            "active_version": top_candidate.get("version", memory_state.get("active_version", "")),
            "active_document_path": top_candidate.get("document_path", memory_state.get("active_document_path", "")),
        }

        policy_results.append(
            {
                "benchmark_case_id": case_id,
                "retrieval_candidates": enriched_candidates,
                "reranked_candidates": reranked_candidates,
                "citations": citations,
                "grounded_answer": bool(citations),
                "click_through_ok": all(bool(item.get("viewer_url")) for item in citations),
                "policy_signals": signals.to_dict(),
                "answer_contract": answer_contract,
            }
        )

    report = summarize_by_case(case_map, policy_results)
    report["policy_mode"] = args.mode
    report["policy_result_count"] = len(policy_results)

    if args.output_results:
        args.output_results.write_text(
            "\n".join(json.dumps(record, ensure_ascii=False) for record in policy_results) + "\n",
            encoding="utf-8",
        )
    if args.output_report:
        args.output_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
