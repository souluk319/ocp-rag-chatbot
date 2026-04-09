"""Play Book Studio의 hybrid retrieval 오케스트레이션.

BM25, vector search, 업로드 문서 overlay, fusion 이후 shaping이 모두 여기에 있다.
답이 엉뚱한 근거를 물고 오면 `query.py` 다음으로 가장 먼저 볼 파일이다.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from play_book_studio.config.settings import Settings

from .bm25 import BM25Index
from .intake_overlay import (
    doc_to_book_books_fingerprint,
    filter_doc_to_book_hits_by_selection as _filter_doc_to_book_hits_by_selection,
    filter_doc_to_book_hits_by_selection,
    load_doc_to_book_overlay_index,
)
from .models import RetrievalHit, RetrievalResult, SessionContext
from .ranking import (
    round_score as _round_score,
    rrf_merge_hit_lists as _rrf_merge_hit_lists,
    summarize_hit as _summarize_hit,
    summarize_hit_list as _summarize_hit_list,
)
from .reranker import CrossEncoderReranker
from .scoring import fuse_ranked_hits
from .trace import build_retrieval_trace, duration_ms as _duration_ms, emit_trace_event as _emit_trace_event
from .vector import VectorRetriever
from .query import (
    CRASH_LOOP_RE,
    decompose_retrieval_queries,
    detect_unsupported_product,
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_cluster_node_usage_intent,
    has_doc_locator_intent,
    has_follow_up_reference,
    has_hosted_control_plane_signal,
    has_openshift_kubernetes_compare_intent,
    has_update_doc_locator_intent,
    has_crash_loop_troubleshooting_intent,
    has_pod_pending_troubleshooting_intent,
    normalize_query,
    rewrite_query,
)

# retrieval 본체는 hybrid 후보를 만들고 fusion/rerank를 orchestration하는 데 집중한다.
# trace 조립과 intake overlay 세부 구현은 바깥 모듈로 분리했다.


class Part2Retriever:
    """answerer와 eval이 공통으로 사용하는 메인 retrieval 런타임."""

    def __init__(
        self,
        settings: Settings,
        bm25_index: BM25Index,
        *,
        vector_retriever: VectorRetriever | None = None,
        reranker: CrossEncoderReranker | None = None,
    ) -> None:
        self.settings = settings
        self.bm25_index = bm25_index
        self.vector_retriever = vector_retriever
        self.reranker = reranker

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        *,
        enable_vector: bool = True,
        enable_reranker: bool | None = None,
    ) -> "Part2Retriever":
        bm25_index = BM25Index.from_jsonl(settings.bm25_corpus_path)
        vector_retriever = VectorRetriever(settings) if enable_vector else None
        reranker_enabled = settings.reranker_enabled if enable_reranker is None else enable_reranker
        reranker = CrossEncoderReranker(settings) if reranker_enabled else None
        return cls(settings, bm25_index, vector_retriever=vector_retriever, reranker=reranker)

    def default_log_path(self) -> Path:
        return self.settings.retrieval_log_path

    def append_log(self, result: RetrievalResult, log_path: Path | None = None) -> Path:
        target = log_path or self.default_log_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        return target

    def _doc_to_book_overlay_index(self) -> BM25Index | None:
        books_dir = self.settings.doc_to_book_books_dir
        fingerprint = doc_to_book_books_fingerprint(books_dir)
        if not fingerprint:
            return None
        return load_doc_to_book_overlay_index(str(books_dir), fingerprint)

    def _search_bm25_candidates(
        self,
        *,
        rewritten_queries: list[str],
        effective_candidate_k: int,
        context: SessionContext,
        trace_callback,
        timings_ms: dict[str, float],
    ) -> tuple[list[RetrievalHit], list[RetrievalHit]]:
        _emit_trace_event(
            trace_callback,
            step="bm25_search",
            label="키워드 검색 중",
            status="running",
        )
        bm25_started_at = time.perf_counter()
        bm25_hit_sets = [
            self.bm25_index.search(subquery, top_k=effective_candidate_k)
            for subquery in rewritten_queries
        ]
        bm25_hits = _rrf_merge_hit_lists(
            bm25_hit_sets,
            source_name="bm25",
            top_k=effective_candidate_k,
        )
        custom_bm25_hits: list[RetrievalHit] = []
        # 사용자 추가 문서 overlay는 현재 품질이 안정화되지 않아 기본 retrieval 경로에서 비활성화한다.
        # 필요 시 custom_bm25 전용 opt-in 경로로 다시 연결한다.
        # overlay_index = self._doc_to_book_overlay_index()
        # if overlay_index is not None:
        #     intake_hit_sets = [
        #         overlay_index.search(subquery, top_k=effective_candidate_k)
        #         for subquery in rewritten_queries
        #     ]
        #     custom_bm25_hits = _rrf_merge_hit_lists(
        #         intake_hit_sets,
        #         source_name="custom_bm25",
        #         top_k=effective_candidate_k,
        #     )
        #     custom_bm25_hits = filter_doc_to_book_hits_by_selection(
        #         custom_bm25_hits,
        #         context=context,
        #     )
        timings_ms["bm25_search"] = _duration_ms(bm25_started_at)
        _emit_trace_event(
            trace_callback,
            step="bm25_search",
            label="키워드 검색 완료",
            status="done",
            detail=f"코어 {len(bm25_hits)}개 · custom {len(custom_bm25_hits)}개",
            duration_ms=timings_ms["bm25_search"],
            meta={
                "candidate_k": effective_candidate_k,
                "core_hits": len(bm25_hits),
                "custom_hits": len(custom_bm25_hits),
                "summary": _summarize_hit_list(bm25_hits),
            },
        )
        return bm25_hits, custom_bm25_hits

    def _search_vector_candidates(
        self,
        *,
        rewritten_queries: list[str],
        effective_candidate_k: int,
        trace_callback,
        timings_ms: dict[str, float],
        warnings: list[str],
    ) -> list[RetrievalHit]:
        if self.vector_retriever is None:
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
                self.vector_retriever.search(subquery, top_k=effective_candidate_k)
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

    def _maybe_rerank_hits(
        self,
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
            "enabled": self.reranker is not None,
            "applied": False,
            "model": getattr(self.reranker, "model_name", ""),
            "top_n": getattr(self.reranker, "top_n", 0),
        }
        if self.reranker is None or not hybrid_hits:
            return hits, reranker_trace
        try:
            _emit_trace_event(
                trace_callback,
                step="rerank",
                label="리랭킹 중",
                status="running",
            )
            rerank_started_at = time.perf_counter()
            reranked_hits = self.reranker.rerank(
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
                    "reranked_count": min(len(hybrid_hits), max(top_k, self.reranker.top_n)),
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

    def retrieve(
        self,
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
        normalize_started_at = time.perf_counter()
        normalized_query = normalize_query(query)
        timings_ms["normalize_query"] = _duration_ms(normalize_started_at)
        _emit_trace_event(
            trace_callback,
            step="normalize_query",
            label="질문 정규화 완료",
            status="done",
            detail=normalized_query[:180],
            duration_ms=timings_ms["normalize_query"],
        )
        warnings: list[str] = []
        unsupported_product = detect_unsupported_product(normalized_query)
        decomposed_queries = decompose_retrieval_queries(query)
        rewrite_started_at = time.perf_counter()
        rewritten_query = rewrite_query(normalized_query, context)
        timings_ms["rewrite_query"] = _duration_ms(rewrite_started_at)
        _emit_trace_event(
            trace_callback,
            step="rewrite_query",
            label="검색 질의 준비 완료",
            status="done",
            detail=rewritten_query[:180],
            duration_ms=timings_ms["rewrite_query"],
        )
        if len(decomposed_queries) > 1:
            _emit_trace_event(
                trace_callback,
                step="decompose_query",
                label="질문 분해 완료",
                status="done",
                detail=" | ".join(decomposed_queries[:3]),
                meta={"subqueries": decomposed_queries},
            )

        if unsupported_product is not None:
            warnings.append(f"query appears outside OCP corpus: {unsupported_product}")
            return RetrievalResult(
                query=query,
                normalized_query=normalized_query,
                rewritten_query=rewritten_query,
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
                    "decomposed_queries": decomposed_queries,
                },
            )

        effective_candidate_k = candidate_k
        if (
            len(decomposed_queries) > 1
            or has_openshift_kubernetes_compare_intent(normalized_query)
            or has_doc_locator_intent(normalized_query)
            or has_backup_restore_intent(normalized_query)
            or has_certificate_monitor_intent(normalized_query)
            or has_follow_up_reference(query)
        ):
            effective_candidate_k = max(candidate_k, 40)

        rewritten_queries = [
            rewrite_query(normalize_query(subquery), context)
            for subquery in decomposed_queries
        ]

        bm25_hits = []
        custom_bm25_hits: list[RetrievalHit] = []
        if use_bm25:
            bm25_hits, custom_bm25_hits = self._search_bm25_candidates(
                rewritten_queries=rewritten_queries,
                effective_candidate_k=effective_candidate_k,
                context=context,
                trace_callback=trace_callback,
                timings_ms=timings_ms,
            )
        vector_hits: list[RetrievalHit] = []
        if use_vector:
            vector_hits = self._search_vector_candidates(
                rewritten_queries=rewritten_queries,
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
            max(top_k, self.reranker.top_n)
            if self.reranker is not None
            else top_k
        )
        fusion_output_k = max(top_k, min(effective_candidate_k, reranker_top_n))
        hybrid_hits = fuse_ranked_hits(
            rewritten_query,
            {
                "bm25": bm25_hits,
                "custom_bm25": custom_bm25_hits,
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
        hits, reranker_trace = self._maybe_rerank_hits(
            query=rewritten_query,
            hybrid_hits=hybrid_hits,
            top_k=top_k,
            trace_callback=trace_callback,
            timings_ms=timings_ms,
            warnings=warnings,
        )
        trace = build_retrieval_trace(
            warnings=warnings,
            bm25_hits=bm25_hits,
            custom_bm25_hits=custom_bm25_hits,
            vector_hits=vector_hits,
            hybrid_hits=hybrid_hits,
            reranked_hits=hits,
            reranker_trace=reranker_trace,
            decomposed_queries=decomposed_queries,
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
            normalized_query=normalized_query,
            rewritten_query=rewritten_query,
            top_k=top_k,
            candidate_k=candidate_k,
            context=context.to_dict(),
            hits=hits,
            trace=trace,
        )
