from __future__ import annotations

import time

from .models import RetrievalHit
from .ranking import (
    rrf_merge_hit_lists as _rrf_merge_hit_lists,
    summarize_hit_list as _summarize_hit_list,
)
from .trace import duration_ms as _duration_ms, emit_trace_event as _emit_trace_event


def search_bm25_candidates(
    retriever,
    *,
    rewritten_queries: list[str],
    effective_candidate_k: int,
    trace_callback,
    timings_ms: dict[str, float],
) -> list[RetrievalHit]:
    _emit_trace_event(
        trace_callback,
        step="bm25_search",
        label="키워드 검색 중",
        status="running",
    )
    bm25_started_at = time.perf_counter()
    bm25_hit_sets = [
        retriever.bm25_index.search(subquery, top_k=effective_candidate_k)
        for subquery in rewritten_queries
    ]
    bm25_hits = _rrf_merge_hit_lists(
        bm25_hit_sets,
        source_name="bm25",
        top_k=effective_candidate_k,
    )
    timings_ms["bm25_search"] = _duration_ms(bm25_started_at)
    _emit_trace_event(
        trace_callback,
        step="bm25_search",
        label="키워드 검색 완료",
        status="done",
        detail=f"후보 {len(bm25_hits)}개",
        duration_ms=timings_ms["bm25_search"],
        meta={
            "candidate_k": effective_candidate_k,
            "count": len(bm25_hits),
            "summary": _summarize_hit_list(bm25_hits),
        },
    )
    return bm25_hits


def search_vector_candidates(
    retriever,
    *,
    rewritten_queries: list[str],
    effective_candidate_k: int,
    trace_callback,
    timings_ms: dict[str, float],
    warnings: list[str],
) -> list[RetrievalHit]:
    if retriever.vector_retriever is None:
        warnings.append("vector retriever is not configured")
        _emit_trace_event(
            trace_callback,
            step="vector_search",
            label="벡터 검색 생략",
            status="warning",
            detail="vector retriever is not configured",
        )
        return []
    try:
        _emit_trace_event(
            trace_callback,
            step="vector_search",
            label="의미 검색 중",
            status="running",
        )
        vector_started_at = time.perf_counter()
        vector_hit_sets = [
            retriever.vector_retriever.search(subquery, top_k=effective_candidate_k)
            for subquery in rewritten_queries
        ]
        vector_hits = _rrf_merge_hit_lists(
            vector_hit_sets,
            source_name="vector",
            top_k=effective_candidate_k,
        )
        timings_ms["vector_search"] = _duration_ms(vector_started_at)
        _emit_trace_event(
            trace_callback,
            step="vector_search",
            label="의미 검색 완료",
            status="done",
            detail=f"후보 {len(vector_hits)}개",
            duration_ms=timings_ms["vector_search"],
            meta={
                "candidate_k": effective_candidate_k,
                "summary": _summarize_hit_list(vector_hits),
            },
        )
        return vector_hits
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"vector search failed: {exc}")
        _emit_trace_event(
            trace_callback,
            step="vector_search",
            label="의미 검색 실패",
            status="warning",
            detail=str(exc),
        )
        return []
