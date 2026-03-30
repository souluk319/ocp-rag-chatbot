from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


CASE_REQUIRED_FIELDS = {
    "id",
    "scenario_id",
    "turn_index",
    "turn_type",
    "group",
    "question_ko",
    "expected_source_dirs",
    "expected_document_paths",
    "expected_category",
    "expected_version_behavior",
    "expected_query_class",
    "expected_memory_behavior",
    "citation_required",
    "click_through_required",
    "context_harness_required",
    "notes",
}

RESULT_REQUIRED_FIELDS = {
    "benchmark_case_id",
    "retrieval_candidates",
    "reranked_candidates",
    "citations",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute Stage 5 retrieval benchmark metrics from fixed cases and run results."
    )
    parser.add_argument("--cases", type=Path, required=True, help="Path to benchmark case JSONL or JSON file.")
    parser.add_argument("--results", type=Path, required=True, help="Path to benchmark result JSONL or JSON file.")
    return parser.parse_args()


def load_records(path: Path) -> list[dict]:
    if path.suffix.lower() == ".jsonl":
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return payload["records"]
    raise ValueError("Unsupported file shape. Use JSONL, JSON array, or an object with a 'records' list.")


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lower()


def missing_fields(record: dict, required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in record)


def top_k_hits(candidates: list[dict], k: int) -> list[dict]:
    ordered = sorted(candidates, key=lambda item: item.get("rank", 999999))
    with_explicit_rank = [item for item in ordered if isinstance(item.get("rank"), int)]
    if with_explicit_rank:
        return [item for item in with_explicit_rank if item.get("rank", 999999) <= k]
    return ordered[:k]


def has_source_dir_hit(candidates: list[dict], expected_source_dirs: set[str], k: int) -> bool:
    return any(
        normalize_path(str(candidate.get("source_dir", ""))) in expected_source_dirs
        for candidate in top_k_hits(candidates, k)
    )


def has_document_hit(candidates: list[dict], expected_document_paths: set[str], k: int) -> bool:
    return any(
        normalize_path(str(candidate.get("document_path", ""))) in expected_document_paths
        for candidate in top_k_hits(candidates, k)
    )


def has_citation_hit(citations: list[dict], expected_document_paths: set[str]) -> bool:
    return any(
        normalize_path(str(citation.get("document_path", ""))) in expected_document_paths
        for citation in citations
    )


def metric_rate(values: list[bool]) -> float:
    if not values:
        return 0.0
    return round(sum(1 for value in values if value) / len(values), 4)


def summarize_by_case(cases: dict[str, dict], results: list[dict]) -> dict:
    invalid_results = []
    missing_case_ids = []
    per_case = []

    source_dir_hit_3: list[bool] = []
    source_dir_hit_5: list[bool] = []
    supporting_hit_5: list[bool] = []
    supporting_hit_10: list[bool] = []
    citation_correctness: list[bool] = []
    retrieval_supporting_hit_5: list[bool] = []
    reranked_supporting_hit_5: list[bool] = []

    per_query_class: dict[str, dict[str, list[bool] | int]] = defaultdict(
        lambda: {
            "case_count": 0,
            "source_dir_hit@5": [],
            "supporting_doc_hit@10": [],
            "citation_correctness": [],
        }
    )

    for index, result in enumerate(results):
        missing = missing_fields(result, RESULT_REQUIRED_FIELDS)
        if missing:
            invalid_results.append(
                {"index": index, "benchmark_case_id": result.get("benchmark_case_id"), "missing_fields": missing}
            )
            continue

        case_id = str(result["benchmark_case_id"])
        if case_id not in cases:
            missing_case_ids.append(case_id)
            continue

        case = cases[case_id]
        expected_source_dirs = {normalize_path(item) for item in case.get("expected_source_dirs", [])}
        expected_document_paths = {normalize_path(item) for item in case.get("expected_document_paths", [])}
        retrieval_candidates = result.get("retrieval_candidates", [])
        reranked_candidates = result.get("reranked_candidates", [])
        citations = result.get("citations", [])

        case_source_hit_3 = has_source_dir_hit(retrieval_candidates, expected_source_dirs, 3)
        case_source_hit_5 = has_source_dir_hit(retrieval_candidates, expected_source_dirs, 5)
        case_support_hit_5 = has_document_hit(retrieval_candidates, expected_document_paths, 5)
        case_support_hit_10 = has_document_hit(retrieval_candidates, expected_document_paths, 10)
        case_reranked_support_hit_5 = has_document_hit(reranked_candidates, expected_document_paths, 5)
        case_citation_correct = has_citation_hit(citations, expected_document_paths)

        source_dir_hit_3.append(case_source_hit_3)
        source_dir_hit_5.append(case_source_hit_5)
        supporting_hit_5.append(case_support_hit_5)
        supporting_hit_10.append(case_support_hit_10)
        citation_correctness.append(case_citation_correct)
        retrieval_supporting_hit_5.append(case_support_hit_5)
        reranked_supporting_hit_5.append(case_reranked_support_hit_5)

        query_class = str(case["expected_query_class"])
        per_query_class[query_class]["case_count"] += 1
        per_query_class[query_class]["source_dir_hit@5"].append(case_source_hit_5)
        per_query_class[query_class]["supporting_doc_hit@10"].append(case_support_hit_10)
        per_query_class[query_class]["citation_correctness"].append(case_citation_correct)

        per_case.append(
            {
                "benchmark_case_id": case_id,
                "query_class": query_class,
                "source_dir_hit@3": case_source_hit_3,
                "source_dir_hit@5": case_source_hit_5,
                "supporting_doc_hit@5": case_support_hit_5,
                "supporting_doc_hit@10": case_support_hit_10,
                "reranked_supporting_doc_hit@5": case_reranked_support_hit_5,
                "citation_correctness": case_citation_correct,
                "rerank_improved@5": (not case_support_hit_5) and case_reranked_support_hit_5,
            }
        )

    rerank_lift = metric_rate(reranked_supporting_hit_5) - metric_rate(retrieval_supporting_hit_5)
    rerank_lift = round(rerank_lift, 4)

    summarized_query_classes = {}
    for query_class, values in per_query_class.items():
        summarized_query_classes[query_class] = {
            "case_count": values["case_count"],
            "source_dir_hit@5": metric_rate(values["source_dir_hit@5"]),
            "supporting_doc_hit@10": metric_rate(values["supporting_doc_hit@10"]),
            "citation_correctness": metric_rate(values["citation_correctness"]),
        }

    summary = {
        "case_count": len(per_case),
        "invalid_result_count": len(invalid_results),
        "missing_case_count": len(missing_case_ids),
        "source_dir_hit@3": metric_rate(source_dir_hit_3),
        "source_dir_hit@5": metric_rate(source_dir_hit_5),
        "supporting_doc_hit@5": metric_rate(supporting_hit_5),
        "supporting_doc_hit@10": metric_rate(supporting_hit_10),
        "citation_correctness": metric_rate(citation_correctness),
        "retrieval_supporting_doc_hit@5": metric_rate(retrieval_supporting_hit_5),
        "reranked_supporting_doc_hit@5": metric_rate(reranked_supporting_hit_5),
        "rerank_lift@5": rerank_lift,
        "query_class_distribution": dict(Counter(case["query_class"] for case in per_case)),
    }

    return {
        "summary": summary,
        "by_query_class": summarized_query_classes,
        "invalid_results": invalid_results,
        "missing_case_ids": missing_case_ids,
        "per_case": per_case,
    }


def main() -> None:
    args = parse_args()
    cases_raw = load_records(args.cases)
    results_raw = load_records(args.results)

    invalid_cases = []
    cases: dict[str, dict] = {}
    for index, case in enumerate(cases_raw):
        missing = missing_fields(case, CASE_REQUIRED_FIELDS)
        if missing:
            invalid_cases.append({"index": index, "id": case.get("id"), "missing_fields": missing})
            continue
        cases[str(case["id"])] = case

    report = summarize_by_case(cases, results_raw)
    report["invalid_cases"] = invalid_cases
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
