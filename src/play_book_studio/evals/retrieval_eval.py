# retrieval 결과의 book hit / rank 품질을 평가 보고서로 만든다.
from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def hit_at_k(top_book_slugs: list[str], expected_book_slugs: list[str], k: int) -> bool:
    expected = set(expected_book_slugs)
    return any(book_slug in expected for book_slug in top_book_slugs[:k])


def _score_group(case_results: list[dict], ks: Iterable[int]) -> dict[str, float]:
    total = len(case_results)
    if total == 0:
        return {f"hit@{k}": 0.0 for k in ks}

    scores: dict[str, float] = {}
    for k in ks:
        hits = sum(
            1
            for case in case_results
            if hit_at_k(case["top_book_slugs"], case["expected_book_slugs"], k)
        )
        scores[f"hit@{k}"] = round(hits / total, 4)

    warning_free = sum(1 for case in case_results if not case.get("warnings"))
    scores["warning_free_rate"] = round(warning_free / total, 4)
    scores["similar_document_risk_rate"] = round(
        sum(int(case.get("graph_signal_tag") == "similar-document") for case in case_results) / total,
        4,
    )
    scores["policy_overlay_warning_rate"] = round(
        sum(int(case.get("graph_signal_tag") == "policy-overlay") for case in case_results) / total,
        4,
    )
    scores["relation_aware_miss_rate"] = round(
        sum(int(case.get("graph_signal_tag") == "relation-aware-retrieval") for case in case_results) / total,
        4,
    )
    return scores


def classify_graph_signal(case: dict, *, max_k: int) -> tuple[str, str]:
    warnings = [str(item) for item in case.get("warnings", [])]
    if any("outside OCP corpus" in warning for warning in warnings):
        return ("policy-overlay", "query fell outside the active OCP corpus boundary")
    if hit_at_k(case["top_book_slugs"], case["expected_book_slugs"], 1):
        return ("clean", "expected playbook family ranked first")
    if hit_at_k(case["top_book_slugs"], case["expected_book_slugs"], max_k):
        return ("similar-document", "expected family was retrieved but lost rank to a similar or adjacent manual")
    if str(case.get("query_type", "")) in {"follow-up", "ambiguous", "topic_switch"}:
        return ("relation-aware-retrieval", "context-dependent query missed the expected playbook family")
    return ("retrieval-miss", "retriever missed the expected playbook family within the evaluation cutoff")


def build_graph_sidecar_evidence_packet(
    retrieval_summary: dict,
    *,
    answer_report: dict | None = None,
) -> dict[str, object]:
    answer_report = answer_report or {}
    graph_signal_counts = dict(retrieval_summary.get("graph_signal_counts", {}))
    similar_document_count = int(graph_signal_counts.get("similar-document", 0))
    policy_overlay_count = int(graph_signal_counts.get("policy-overlay", 0))
    relation_aware_count = int(graph_signal_counts.get("relation-aware-retrieval", 0))
    retrieval_miss_count = int(graph_signal_counts.get("retrieval-miss", 0))
    graph_shaped_count = similar_document_count + policy_overlay_count + relation_aware_count
    answer_assessment = dict(answer_report.get("realworld_assessment", {}))
    provenance_noise_case_ids = list(answer_assessment.get("provenance_noise_case_ids", []))
    provenance_noise_count = len(provenance_noise_case_ids)

    if relation_aware_count > 0:
        decision = "revisit_graph_sidecar"
        next_trigger = "relation_aware_retrieval"
        reason = "context-dependent misses still lose the expected playbook family, so relation-aware retrieval should stay open"
    elif policy_overlay_count > 0:
        decision = "revisit_graph_sidecar"
        next_trigger = "policy_overlay_branching"
        reason = "queries that cross policy or corpus boundaries still need stronger overlay-aware routing"
    elif similar_document_count > 0:
        decision = "revisit_graph_sidecar"
        next_trigger = "similar_document_validation"
        reason = "adjacent manuals still outrank the expected playbook family in similar-document follow-up cases"
    elif retrieval_miss_count > 0:
        decision = "defer_graph_sidecar"
        next_trigger = "retrieval_baseline"
        reason = "generic retrieval misses remain, so baseline recall should be fixed before attributing the gap to graph needs"
    elif provenance_noise_count > 0:
        decision = "defer_graph_sidecar"
        reason = "retrieval eval is clean; the remaining issue is provenance noise on passing answers"
        next_trigger = "provenance_traversal"
    else:
        decision = "defer_graph_sidecar"
        reason = "current retrieval and answer evidence does not show a graph-shaped bottleneck"
        next_trigger = "none"

    return {
        "decision": decision,
        "reason": reason,
        "next_trigger_to_revisit": next_trigger,
        "retrieval_evidence": {
            "hit_at_1": retrieval_summary.get("overall", {}).get("hit@1", 0.0),
            "hit_at_5": retrieval_summary.get("overall", {}).get("hit@5", 0.0),
            "similar_document_count": similar_document_count,
            "policy_overlay_count": policy_overlay_count,
            "relation_aware_miss_count": relation_aware_count,
            "retrieval_miss_count": retrieval_miss_count,
            "graph_shaped_count": graph_shaped_count,
        },
        "answer_evidence": {
            "pass_rate": answer_report.get("overall", {}).get("pass_rate", 0.0),
            "assessment_status": answer_assessment.get("status", ""),
            "provenance_noise_count": provenance_noise_count,
            "provenance_noise_case_ids": provenance_noise_case_ids,
        },
    }


def summarize_case_results(
    case_results: list[dict],
    *,
    ks: tuple[int, ...] = (1, 3, 5),
) -> dict:
    by_query_type: dict[str, list[dict]] = defaultdict(list)
    by_mode: dict[str, list[dict]] = defaultdict(list)
    graph_signal_counts: dict[str, int] = defaultdict(int)
    for case in case_results:
        graph_signal_tag, graph_signal_reason = classify_graph_signal(case, max_k=max(ks))
        case["graph_signal_tag"] = graph_signal_tag
        case["graph_signal_reason"] = graph_signal_reason
        by_query_type[str(case.get("query_type", "unknown"))].append(case)
        by_mode[str(case.get("mode", "unknown"))].append(case)
        if graph_signal_tag != "clean":
            graph_signal_counts[graph_signal_tag] += 1

    misses = [
        {
            "id": case.get("id"),
            "query": case["query"],
            "query_type": case.get("query_type"),
            "expected_book_slugs": case["expected_book_slugs"],
            "top_book_slugs": case["top_book_slugs"],
            "graph_signal_tag": case.get("graph_signal_tag", ""),
            "graph_signal_reason": case.get("graph_signal_reason", ""),
        }
        for case in case_results
        if not hit_at_k(case["top_book_slugs"], case["expected_book_slugs"], max(ks))
    ]

    return {
        "case_count": len(case_results),
        "overall": _score_group(case_results, ks),
        "by_query_type": {
            query_type: _score_group(items, ks)
            for query_type, items in sorted(by_query_type.items())
        },
        "by_mode": {
            mode: _score_group(items, ks)
            for mode, items in sorted(by_mode.items())
        },
        "graph_signal_counts": dict(sorted(graph_signal_counts.items())),
        "misses": misses,
    }
