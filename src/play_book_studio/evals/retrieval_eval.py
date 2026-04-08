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
    return scores


def summarize_case_results(
    case_results: list[dict],
    *,
    ks: tuple[int, ...] = (1, 3, 5),
) -> dict:
    by_query_type: dict[str, list[dict]] = defaultdict(list)
    by_mode: dict[str, list[dict]] = defaultdict(list)
    for case in case_results:
        by_query_type[str(case.get("query_type", "unknown"))].append(case)
        by_mode[str(case.get("mode", "unknown"))].append(case)

    misses = [
        {
            "id": case.get("id"),
            "query": case["query"],
            "query_type": case.get("query_type"),
            "expected_book_slugs": case["expected_book_slugs"],
            "top_book_slugs": case["top_book_slugs"],
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
        "misses": misses,
    }
