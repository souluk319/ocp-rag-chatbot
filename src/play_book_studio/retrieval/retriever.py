"""Play Book Studio의 hybrid retrieval 오케스트레이션.

BM25, vector search, fusion 이후 shaping이 모두 여기에 있다.
답이 엉뚱한 근거를 물고 오면 `query.py` 다음으로 가장 먼저 볼 파일이다.
"""

from __future__ import annotations

import json
from pathlib import Path

from play_book_studio.config.settings import Settings

from .bm25 import BM25Index
from .models import RetrievalResult, SessionContext
from .reranker import CrossEncoderReranker
from .scoring import fuse_ranked_hits
from .vector import VectorRetriever
from .retriever_pipeline import execute_retrieval_pipeline


class ChatRetriever:
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
    ) -> "ChatRetriever":
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
        return execute_retrieval_pipeline(
            self,
            query,
            context=context,
            top_k=top_k,
            candidate_k=candidate_k,
            use_bm25=use_bm25,
            use_vector=use_vector,
            trace_callback=trace_callback,
        )
