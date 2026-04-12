# retrieval 단계의 trace 이벤트와 결과 요약 조립을 담당한다.
# 검색 단계별 진행 로그와 최종 trace payload를 한 군데에서 관리한다.
from __future__ import annotations

import time
from typing import Any

from .models import RetrievalHit
from .ranking import summarize_hit_list


def duration_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 1)


def emit_trace_event(
    trace_callback,
    *,
    step: str,
    label: str,
    status: str,
    detail: str = "",
    duration_ms: float | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    if trace_callback is None:
        return
    event = {
        "type": "trace",
        "step": step,
        "label": label,
        "status": status,
    }
    if detail:
        event["detail"] = detail
    if duration_ms is not None:
        event["duration_ms"] = duration_ms
    if meta:
        event["meta"] = meta
    trace_callback(event)


def build_retrieval_trace(
    *,
    warnings: list[str],
    bm25_hits: list[RetrievalHit],
    overlay_bm25_hits: list[RetrievalHit] | None = None,
    vector_hits: list[RetrievalHit],
    hybrid_hits: list[RetrievalHit],
    graph_trace: dict[str, Any],
    reranked_hits: list[RetrievalHit],
    reranker_trace: dict[str, Any],
    decomposed_queries: list[str],
    effective_candidate_k: int,
    fusion_output_k: int,
    timings_ms: dict[str, float],
    candidate_k: int,
    top_k: int,
) -> dict[str, Any]:
    bm25_summary = summarize_hit_list(bm25_hits)
    overlay_bm25_summary = summarize_hit_list(overlay_bm25_hits or [])
    vector_summary = summarize_hit_list(vector_hits)
    hybrid_summary = summarize_hit_list(hybrid_hits, score_key="fused_score")
    reranked_summary = summarize_hit_list(reranked_hits, score_key="fused_score")
    trace = {
        "warnings": warnings,
        "bm25": [hit.to_dict() for hit in bm25_hits[: min(candidate_k, 10)]],
        "vector": [hit.to_dict() for hit in vector_hits[: min(candidate_k, 10)]],
        "hybrid": [hit.to_dict() for hit in hybrid_hits[: min(fusion_output_k, 5)]],
        "graph": graph_trace,
        "reranked": [hit.to_dict() for hit in reranked_hits[: min(top_k, 5)]],
        "reranker": reranker_trace,
        "metrics": {
            "bm25": bm25_summary,
            "vector": vector_summary,
            "hybrid": hybrid_summary,
            "reranked": reranked_summary,
        },
        "decomposed_queries": decomposed_queries,
        "effective_candidate_k": effective_candidate_k,
        "fusion_output_k": fusion_output_k,
        "timings_ms": timings_ms,
    }
    if overlay_bm25_hits:
        trace["overlay_bm25"] = [hit.to_dict() for hit in overlay_bm25_hits[: min(candidate_k, 10)]]
        trace["metrics"]["overlay_bm25"] = overlay_bm25_summary
    return trace
