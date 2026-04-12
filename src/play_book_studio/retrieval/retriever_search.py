from __future__ import annotations

import time

from .intake_overlay import filter_customer_pack_hits_by_selection
from .models import RetrievalHit
from .ranking import (
    rrf_merge_hit_lists as _rrf_merge_hit_lists,
    rrf_merge_named_hit_lists as _rrf_merge_named_hit_lists,
    summarize_hit_list as _summarize_hit_list,
)
from .trace import duration_ms as _duration_ms, emit_trace_event as _emit_trace_event


def _vector_subquery_runtime(
    *,
    query: str,
    runtime: dict[str, object],
) -> dict[str, object]:
    return {
        "query": query,
        "endpoint_used": str(runtime.get("endpoint_used", "")),
        "attempted_endpoints": [str(item) for item in (runtime.get("attempted_endpoints") or [])],
        "hit_count": int(runtime.get("hit_count", 0) or 0),
        "top_score": runtime.get("top_score"),
    }


def _aggregate_vector_runtime(subqueries: list[dict[str, object]]) -> dict[str, object]:
    endpoints_used = sorted(
        {
            str(item.get("endpoint_used", "")).strip()
            for item in subqueries
            if str(item.get("endpoint_used", "")).strip()
        }
    )
    return {
        "subquery_count": len(subqueries),
        "subqueries": subqueries,
        "endpoints_used": endpoints_used,
        "endpoint_used": endpoints_used[0] if len(endpoints_used) == 1 else "mixed" if endpoints_used else "",
        "empty_subqueries": sum(int(item.get("hit_count", 0) == 0) for item in subqueries),
    }


def search_bm25_candidates(
    retriever,
    *,
    context,
    rewritten_queries: list[str],
    effective_candidate_k: int,
    trace_callback,
    timings_ms: dict[str, float],
) -> dict[str, list[RetrievalHit]]:
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
    core_hits = _rrf_merge_hit_lists(
        bm25_hit_sets,
        source_name="bm25",
        top_k=effective_candidate_k,
    )
    overlay_hits: list[RetrievalHit] = []
    overlay_index = retriever.customer_pack_overlay_index()
    if overlay_index is not None:
        overlay_hit_sets = [
            filter_customer_pack_hits_by_selection(
                overlay_index.search(subquery, top_k=effective_candidate_k),
                context=context,
            )
            for subquery in rewritten_queries
        ]
        overlay_hits = _rrf_merge_hit_lists(
            overlay_hit_sets,
            source_name="overlay_bm25",
            top_k=effective_candidate_k,
        )
    bm25_hits = (
        _rrf_merge_named_hit_lists(
            {
                "bm25": core_hits,
                "overlay_bm25": overlay_hits,
            },
            source_name="bm25",
            top_k=effective_candidate_k,
            weights={"bm25": 1.0, "overlay_bm25": 1.35},
        )
        if overlay_hits
        else core_hits
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
            "overlay_count": len(overlay_hits),
            "summary": _summarize_hit_list(bm25_hits),
        },
    )
    return {
        "core_hits": core_hits,
        "overlay_hits": overlay_hits,
        "hits": bm25_hits,
    }


def search_vector_candidates(
    retriever,
    *,
    rewritten_queries: list[str],
    effective_candidate_k: int,
    trace_callback,
    timings_ms: dict[str, float],
) -> dict[str, object]:
    if retriever.vector_retriever is None:
        _emit_trace_event(
            trace_callback,
            step="vector_search",
            label="의미 검색 실패",
            status="error",
            detail="vector retriever is not configured",
        )
        raise RuntimeError("vector retriever is not configured")
    try:
        _emit_trace_event(
            trace_callback,
            step="vector_search",
            label="의미 검색 중",
            status="running",
        )
        vector_started_at = time.perf_counter()
        vector_hit_sets: list[list[RetrievalHit]] = []
        vector_subqueries: list[dict[str, object]] = []
        for subquery in rewritten_queries:
            if hasattr(retriever.vector_retriever, "search_with_trace"):
                hits, runtime = retriever.vector_retriever.search_with_trace(
                    subquery,
                    top_k=effective_candidate_k,
                )
            else:
                hits = retriever.vector_retriever.search(subquery, top_k=effective_candidate_k)
                runtime = {
                    "endpoint_used": "",
                    "attempted_endpoints": [],
                    "hit_count": len(hits),
                    "top_score": float(hits[0].raw_score) if hits else None,
                }
            vector_hit_sets.append(hits)
            vector_subqueries.append(_vector_subquery_runtime(query=subquery, runtime=runtime))
        vector_hits = _rrf_merge_hit_lists(
            vector_hit_sets,
            source_name="vector",
            top_k=effective_candidate_k,
        )
        vector_runtime = _aggregate_vector_runtime(vector_subqueries)
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
                "count": len(vector_hits),
                "endpoint_used": vector_runtime["endpoint_used"],
                "endpoints_used": vector_runtime["endpoints_used"],
                "empty_subqueries": vector_runtime["empty_subqueries"],
                "summary": _summarize_hit_list(vector_hits),
            },
        )
        return {
            "hits": vector_hits,
            "runtime": vector_runtime,
        }
    except Exception as exc:  # noqa: BLE001
        _emit_trace_event(
            trace_callback,
            step="vector_search",
            label="의미 검색 실패",
            status="error",
            detail=str(exc),
        )
        raise RuntimeError(f"vector search failed: {exc}") from exc
