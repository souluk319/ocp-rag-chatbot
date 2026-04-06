from __future__ import annotations

from collections import defaultdict
from typing import Any

from ocp_rag.session import SessionContext

from ocp_rag.retrieval.retriever import Part2Retriever


def evaluate_case(
    retriever: Part2Retriever,
    case: dict[str, Any],
    *,
    top_k: int,
    candidate_k: int,
    use_vector: bool = True,
) -> dict[str, Any]:
    context = SessionContext.from_dict(case.get("context"))
    result = retriever.retrieve(
        str(case["query"]),
        context=context,
        top_k=top_k,
        candidate_k=candidate_k,
        use_vector=use_vector,
    )
    top_books = [hit.book_slug for hit in result.hits]
    expected_books = list(case.get("expected_book_slugs", []))

    def matched_at(k: int) -> bool:
        return any(book_slug in top_books[:k] for book_slug in expected_books)

    return {
        "id": case.get("id"),
        "category": case.get("category", "uncategorized"),
        "mode": case.get("mode", "ops"),
        "query": case["query"],
        "context": context.to_dict(),
        "expected_book_slugs": expected_books,
        "matched_at_1": matched_at(1),
        "matched_at_3": matched_at(3),
        "matched_at_5": matched_at(5),
        "top_book_slugs": top_books,
        "top_hits": [
            {
                "book_slug": hit.book_slug,
                "section": hit.section,
                "viewer_path": hit.viewer_path,
                "score": hit.fused_score,
            }
            for hit in result.hits
        ],
        "warnings": result.trace.get("warnings", []),
        "rewritten_query": result.rewritten_query,
    }


def _rate(matched: int, total: int) -> float:
    return round(matched / max(total, 1), 4)


def summarize_results(
    details: list[dict[str, Any]],
    *,
    top_k: int,
    candidate_k: int,
) -> dict[str, Any]:
    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    mode_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    warning_count = 0

    for detail in details:
        category_groups[str(detail["category"])].append(detail)
        mode_groups[str(detail["mode"])].append(detail)
        warning_count += len(detail.get("warnings", []))

    def build_bucket(bucket: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(bucket)
        return {
            "case_count": total,
            "hit_at_1": _rate(sum(int(item["matched_at_1"]) for item in bucket), total),
            "hit_at_3": _rate(sum(int(item["matched_at_3"]) for item in bucket), total),
            "hit_at_5": _rate(sum(int(item["matched_at_5"]) for item in bucket), total),
        }

    overall = build_bucket(details)
    by_category = {
        key: build_bucket(bucket)
        for key, bucket in sorted(category_groups.items())
    }
    by_mode = {
        key: build_bucket(bucket)
        for key, bucket in sorted(mode_groups.items())
    }

    return {
        "case_count": len(details),
        "top_k": top_k,
        "candidate_k": candidate_k,
        "warning_count": warning_count,
        "overall": overall,
        "by_category": by_category,
        "by_mode": by_mode,
        "details": details,
    }
