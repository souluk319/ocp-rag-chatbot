from __future__ import annotations

import time
from typing import Any

from .models import RetrievalHit
from .ranking import summarize_hit_list as _summarize_hit_list
from .trace import duration_ms as _duration_ms, emit_trace_event as _emit_trace_event


def maybe_rerank_hits(
    retriever,
    *,
    query: str,
    hybrid_hits: list[RetrievalHit],
    top_k: int,
    trace_callback,
    timings_ms: dict[str, float],
    warnings: list[str],
) -> tuple[list[RetrievalHit], dict[str, Any]]:
    hits = hybrid_hits[:top_k]
    reranker_trace: dict[str, Any] = {
        "enabled": retriever.reranker is not None,
        "applied": False,
        "model": getattr(retriever.reranker, "model_name", ""),
        "top_n": getattr(retriever.reranker, "top_n", 0),
    }
    if retriever.reranker is None or not hybrid_hits:
        return hits, reranker_trace
    try:
        _emit_trace_event(
            trace_callback,
            step="rerank",
            label="리랭킹 중",
            status="running",
        )
        rerank_started_at = time.perf_counter()
        reranked_hits = retriever.reranker.rerank(
            query,
            hybrid_hits,
            top_k=top_k,
        )
        timings_ms["rerank"] = _duration_ms(rerank_started_at)
        hits = reranked_hits[:top_k]
        reranker_trace.update(
            {
                "applied": True,
                "candidate_count": len(hybrid_hits),
                "reranked_count": min(len(hybrid_hits), max(top_k, retriever.reranker.top_n)),
            }
        )
        _emit_trace_event(
            trace_callback,
            step="rerank",
            label="리랭킹 완료",
            status="done",
            detail=(
                f"{hits[0].book_slug} · {hits[0].section}"
                if hits
                else "상위 근거 없음"
            ),
            duration_ms=timings_ms["rerank"],
            meta={"summary": _summarize_hit_list(hits, score_key="fused_score")},
        )
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"reranker failed: {exc}")
        reranker_trace["error"] = str(exc)
        _emit_trace_event(
            trace_callback,
            step="rerank",
            label="리랭킹 실패",
            status="warning",
            detail=str(exc),
        )
    return hits, reranker_trace
