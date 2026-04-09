from __future__ import annotations

import time

from .models import RetrievalHit, RetrievalResult, SessionContext
from .retriever_plan import build_retrieval_plan
from .retriever_rerank import maybe_rerank_hits
from .retriever_search import search_bm25_candidates, search_vector_candidates
from .ranking import summarize_hit_list as _summarize_hit_list
from .scoring import fuse_ranked_hits
from .trace import build_retrieval_trace, duration_ms as _duration_ms, emit_trace_event as _emit_trace_event


def execute_retrieval_pipeline(
    retriever,
    query: str,
    *,
    context: SessionContext | None = None,
    top_k: int = 8,
    candidate_k: int = 20,
    use_bm25: bool = True,
    use_vector: bool = True,
    trace_callback=None,
) -> RetrievalResult:
    retrieve_started_at = time.perf_counter()
    context = context or SessionContext()
    timings_ms: dict[str, float] = {}
    plan = build_retrieval_plan(query, context=context, candidate_k=candidate_k)
    timings_ms["normalize_query"] = plan.normalize_query_ms
    _emit_trace_event(
        trace_callback,
        step="normalize_query",
        label="질문 정규화 완료",
        status="done",
        detail=plan.normalized_query[:180],
        duration_ms=timings_ms["normalize_query"],
    )
    warnings: list[str] = []
    unsupported_product = plan.unsupported_product
    timings_ms["rewrite_query"] = plan.rewrite_query_ms
    _emit_trace_event(
        trace_callback,
        step="rewrite_query",
        label="검색 질의 준비 완료",
        status="done",
        detail=plan.rewritten_query[:180],
        duration_ms=timings_ms["rewrite_query"],
    )
    if len(plan.decomposed_queries) > 1:
        _emit_trace_event(
            trace_callback,
            step="decompose_query",
            label="질문 분해 완료",
            status="done",
            detail=" | ".join(plan.decomposed_queries[:3]),
            meta={"subqueries": plan.decomposed_queries},
        )

    if unsupported_product is not None:
        warnings.append(f"query appears outside OCP corpus: {unsupported_product}")
        return RetrievalResult(
            query=query,
            normalized_query=plan.normalized_query,
            rewritten_query=plan.rewritten_query,
            top_k=top_k,
            candidate_k=candidate_k,
            context=context.to_dict(),
            hits=[],
            trace={
                "warnings": warnings,
                "bm25": [],
                "vector": [],
                "timings_ms": {
                    **timings_ms,
                    "total": _duration_ms(retrieve_started_at),
                },
                "decomposed_queries": plan.decomposed_queries,
            },
        )

    effective_candidate_k = plan.effective_candidate_k

    bm25_hits: list[RetrievalHit] = []
    if use_bm25:
        bm25_hits = search_bm25_candidates(
            retriever,
            rewritten_queries=plan.rewritten_queries,
            effective_candidate_k=effective_candidate_k,
            trace_callback=trace_callback,
            timings_ms=timings_ms,
        )
    vector_hits: list[RetrievalHit] = []
    if use_vector:
        vector_hits = search_vector_candidates(
            retriever,
            rewritten_queries=plan.rewritten_queries,
            effective_candidate_k=effective_candidate_k,
            trace_callback=trace_callback,
            timings_ms=timings_ms,
            warnings=warnings,
        )

    _emit_trace_event(
        trace_callback,
        step="fusion",
        label="검색 결과 결합 중",
        status="running",
    )
    fusion_started_at = time.perf_counter()
    reranker_top_n = (
        max(top_k, retriever.reranker.top_n)
        if retriever.reranker is not None
        else top_k
    )
    fusion_output_k = max(top_k, min(effective_candidate_k, reranker_top_n))
    hybrid_hits = fuse_ranked_hits(
        plan.rewritten_query,
        {
            "bm25": bm25_hits,
            "vector": vector_hits,
        },
        context=context,
        top_k=fusion_output_k,
    )
    timings_ms["fusion"] = _duration_ms(fusion_started_at)
    top_hit = hybrid_hits[0] if hybrid_hits else None
    top_detail = (
        f"{top_hit.book_slug} · {top_hit.section}"
        if top_hit is not None
        else "상위 근거 없음"
    )
    _emit_trace_event(
        trace_callback,
        step="fusion",
        label="검색 결과 결합 완료",
        status="done",
        detail=top_detail,
        duration_ms=timings_ms["fusion"],
        meta={"summary": _summarize_hit_list(hybrid_hits, score_key="fused_score")},
    )
    hits, reranker_trace = maybe_rerank_hits(
        retriever,
        query=plan.rewritten_query,
        hybrid_hits=hybrid_hits,
        top_k=top_k,
        trace_callback=trace_callback,
        timings_ms=timings_ms,
        warnings=warnings,
    )
    trace = build_retrieval_trace(
        warnings=warnings,
        bm25_hits=bm25_hits,
        vector_hits=vector_hits,
        hybrid_hits=hybrid_hits,
        reranked_hits=hits,
        reranker_trace=reranker_trace,
        decomposed_queries=plan.decomposed_queries,
        effective_candidate_k=effective_candidate_k,
        fusion_output_k=fusion_output_k,
        timings_ms={
            **timings_ms,
            "total": _duration_ms(retrieve_started_at),
        },
        candidate_k=candidate_k,
        top_k=top_k,
    )
    return RetrievalResult(
        query=query,
        normalized_query=plan.normalized_query,
        rewritten_query=plan.rewritten_query,
        top_k=top_k,
        candidate_k=candidate_k,
        context=context.to_dict(),
        hits=hits,
        trace=trace,
    )
