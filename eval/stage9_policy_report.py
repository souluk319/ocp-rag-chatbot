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


def build_scenario_memory_state(
    signals: Any,
    top_candidate: dict[str, Any],
    memory_state: dict[str, Any],
) -> dict[str, Any]:
    active_source_dirs = list(signals.preferred_source_dirs)
    if not active_source_dirs and top_candidate.get("source_dir"):
        active_source_dirs = [top_candidate.get("source_dir", "")]

    active_categories = list(signals.preferred_categories)
    if not active_categories and top_candidate.get("effective_category"):
        active_categories = [top_candidate.get("effective_category", "")]

    return {
        "active_source_dirs": active_source_dirs,
        "active_categories": active_categories,
        "active_version": top_candidate.get("version", memory_state.get("active_version", "")),
        "active_document_path": top_candidate.get("document_path", memory_state.get("active_document_path", "")),
    }


def rerank_prepared_retrieval(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        [dict(candidate) for candidate in candidates],
        key=lambda item: (-float(item.get("score", 0.0)), int(item.get("rank", 999999))),
    )
    for index, candidate in enumerate(ordered, start=1):
        candidate["rank"] = index
    return ordered


def extract_raw_retrieval_view(report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    summary = report.get("summary", {})
    raw_summary = {
        key: summary.get(key)
        for key in (
            "case_count",
            "invalid_result_count",
            "missing_case_count",
            "source_dir_hit@3",
            "source_dir_hit@5",
            "supporting_doc_hit@5",
            "supporting_doc_hit@10",
            "retrieval_supporting_doc_hit@5",
            "query_class_distribution",
        )
    }

    raw_by_query_class: dict[str, dict[str, Any]] = {}
    for query_class, values in report.get("by_query_class", {}).items():
        raw_by_query_class[query_class] = {
            "case_count": values.get("case_count", 0),
            "source_dir_hit@5": values.get("source_dir_hit@5", 0.0),
            "supporting_doc_hit@10": values.get("supporting_doc_hit@10", 0.0),
        }
    return raw_summary, raw_by_query_class


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
        query_signals = policy_engine.analyze_query(
            case["question_ko"],
            mode=args.mode,
            memory_state=memory_state,
        )
        prepared_candidates, query_signals = policy_engine.augment_follow_up_candidates(
            case["question_ko"],
            enriched_candidates,
            manifest_index=manifest_index,
            mode=args.mode,
            memory_state=memory_state,
            signals=query_signals,
        )
        prepared_candidates = rerank_prepared_retrieval(prepared_candidates)
        reranked_candidates, signals = policy_engine.rerank_candidates(
            case["question_ko"],
            prepared_candidates,
            mode=args.mode,
            memory_state=memory_state,
            signals=query_signals,
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
        scenario_memory[scenario_id] = build_scenario_memory_state(signals, top_candidate, memory_state)

        policy_results.append(
            {
                "benchmark_case_id": case_id,
                "raw_retrieval_candidates": enriched_candidates,
                "policy_prepared_candidates": prepared_candidates,
                "retrieval_candidates": prepared_candidates,
                "reranked_candidates": reranked_candidates,
                "citations": citations,
                "grounded_answer": bool(citations),
                "click_through_ok": all(bool(item.get("viewer_url")) for item in citations),
                "policy_signals": signals.to_dict(),
                "answer_contract": answer_contract,
            }
        )

    report = summarize_by_case(case_map, policy_results)
    raw_results = []
    for record in policy_results:
        raw_record = dict(record)
        raw_record["retrieval_candidates"] = record.get("raw_retrieval_candidates", [])
        raw_results.append(raw_record)
    raw_report = summarize_by_case(case_map, raw_results)
    raw_summary, raw_by_query_class = extract_raw_retrieval_view(raw_report)
    report["policy_mode"] = args.mode
    report["policy_result_count"] = len(policy_results)
    report["summary_basis"] = "policy_prepared_candidates"
    report["summary_note"] = (
        "The Stage 9 summary metrics are computed on policy-prepared retrieval candidates after memory-aware "
        "augmentation. Raw baseline retrieval recall is preserved separately for diagnostics."
    )
    report["raw_retrieval_summary"] = raw_summary
    report["raw_retrieval_by_query_class"] = raw_by_query_class

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
