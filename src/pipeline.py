"""전체 RAG 파이프라인을 묶어주는 오케스트레이터. 스트리밍 모드에서는 각 단계별 trace도 같이 보냄."""
import time
from typing import AsyncGenerator, Optional

from src.llm import LLMClient
from src.embedding import EmbeddingEngine
from src.vectorstore import IVFIndex
from src.retriever import Retriever
from src.session import SessionManager, QueryRewriter, Session
from src.cache import SemanticCache
from src.config import TOP_K


SYSTEM_PROMPT = """당신은 OCP(OpenShift Container Platform) 운영 전문가입니다.
아래 제공된 "참고 문서"만을 기반으로 정확하고 실용적인 답변을 제공하세요.

중요 규칙:
1. 반드시 아래 제공된 참고 문서 내용만 사용하여 답변하세요.
2. 참고 문서에 없는 내용은 절대 답변하지 마세요. 대신 "제공된 문서에서 해당 정보를 찾지 못했습니다. 관련 공식 문서를 참조해주세요."라고 답변하세요.
3. 당신의 사전 학습 지식을 사용하지 마세요. 오직 참고 문서의 내용만 활용하세요.
4. 기술 용어는 정확하게 사용하고, 문서에 예시가 있다면 포함하세요.
5. 답변은 구조화된 형태(번호, 불릿, 표 등)로 작성하세요.
6. 한국어로 답변하세요.
7. 출처를 밝힐 때 "[문서 1]" 같은 번호 대신, 실제 파일명(예: "네트워킹.pdf에 따르면", "k8s-workload-types-ko.md에 의하면")을 사용하세요."""


class RAGPipeline:
    """RAG 전체 파이프라인"""

    def __init__(
        self,
        llm_client: LLMClient,
        embedding_engine: EmbeddingEngine,
        index: IVFIndex,
        retriever: Retriever,
        session_manager: SessionManager,
        cache: SemanticCache,
    ):
        self.llm = llm_client
        self.embedding = embedding_engine
        self.index = index
        self.retriever = retriever
        self.session_mgr = session_manager
        self.cache = cache
        self.query_rewriter = QueryRewriter(llm_client)

    async def query(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> dict:
        """비스트리밍 RAG 응답"""
        session = self.session_mgr.get_or_create(session_id)
        rewritten_query = await self.query_rewriter.rewrite(user_query, session)
        query_embedding = self.embedding.embed(rewritten_query)

        cached = await self.cache.async_lookup(rewritten_query, query_embedding)
        if cached:
            session.add_message("user", user_query)
            session.add_message("assistant", cached.response)
            return {
                "session_id": session.session_id,
                "answer": cached.response,
                "sources": [],
                "rewritten_query": rewritten_query,
                "cached": True,
            }

        results = self.retriever.retrieve(rewritten_query, top_k=top_k)
        context = self.retriever.build_context(results)

        prompt = f"참고 문서:\n{context}\n\n질문: {rewritten_query}"
        history = session.get_history()
        answer = await self.llm.generate(SYSTEM_PROMPT, prompt, history)

        session.add_message("user", user_query)
        session.add_message("assistant", answer)
        await self.cache.async_store(rewritten_query, query_embedding, answer, context)

        return {
            "session_id": session.session_id,
            "answer": answer,
            "sources": [
                {"chunk_id": r.chunk_id, "score": r.score, "source": r.metadata.get("source", "")}
                for r in results
            ],
            "rewritten_query": rewritten_query,
            "cached": False,
        }

    async def query_stream(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> AsyncGenerator[dict, None]:
        """스트리밍 RAG 응답 - SSE용 이벤트 생성 (트레이스 포함)"""
        pipeline_start = time.time()
        session = self.session_mgr.get_or_create(session_id)

        # === TRACE: Session 조회 ===
        yield {"type": "trace", "data": {
            "step": "session",
            "status": "done",
            "detail": {
                "session_id": session.session_id,
                "history_turns": len(session.messages) // 2,
            },
            "ms": 0,
        }}

        # === 1. Query Rewriting ===
        t = time.time()
        rewritten_query = await self.query_rewriter.rewrite(user_query, session)
        yield {"type": "trace", "data": {
            "step": "rewrite",
            "status": "done",
            "detail": {
                "original": user_query,
                "rewritten": rewritten_query,
                "changed": user_query != rewritten_query,
            },
            "ms": round((time.time() - t) * 1000),
        }}
        yield {"type": "rewrite", "data": rewritten_query}

        # === 2. Embedding ===
        t = time.time()
        query_embedding = self.embedding.embed(rewritten_query)
        embed_ms = round((time.time() - t) * 1000)
        cache_stats = self.embedding.cache_stats()
        yield {"type": "trace", "data": {
            "step": "embedding",
            "status": "done",
            "detail": {
                "dim": len(query_embedding),
                "cache_hit": embed_ms < 1,
                "embedding_cache_size": cache_stats["cached_items"],
            },
            "ms": embed_ms,
        }}

        # === 3. Cache 확인 ===
        t = time.time()
        cached = await self.cache.async_lookup(rewritten_query, query_embedding)
        cache_ms = round((time.time() - t) * 1000)
        if cached:
            yield {"type": "trace", "data": {
                "step": "cache",
                "status": "hit",
                "detail": {
                    "cached_query": cached.query[:80],
                    "hit_count": cached.hit_count,
                },
                "ms": cache_ms,
            }}
            session.add_message("user", user_query)
            session.add_message("assistant", cached.response)
            yield {"type": "cached", "data": cached.response}
            yield {"type": "done", "data": {
                "session_id": session.session_id,
                "cached": True,
                "total_ms": round((time.time() - pipeline_start) * 1000),
            }}
            return

        yield {"type": "trace", "data": {
            "step": "cache",
            "status": "miss",
            "detail": {"semantic_cache_size": self.cache.stats()["cached_queries"]},
            "ms": cache_ms,
        }}

        # === 4. Vector 검색 ===
        # top_k*3으로 넉넉히 뽑고 reranker에서 걸러냄. *2로 했을 때 recall 좀 아쉬워서 *3으로.
        t = time.time()
        search_results = self.index.search(query_embedding, top_k=top_k * 3)
        search_ms = round((time.time() - t) * 1000)
        yield {"type": "trace", "data": {
            "step": "vector_search",
            "status": "done",
            "detail": {
                "candidates": len(search_results),
                "top_score": round(search_results[0].score, 4) if search_results else 0,
                "index_type": "IVF",
                "n_clusters": self.index.n_clusters,
                "n_probe": self.index.n_probe,
            },
            "ms": search_ms,
        }}

        # === 5. Reranking ===
        t = time.time()
        results = self.retriever.retrieve(rewritten_query, top_k=top_k)
        rerank_ms = round((time.time() - t) * 1000)
        yield {"type": "trace", "data": {
            "step": "reranking",
            "status": "done",
            "detail": {
                "method": "Semantic + BM25 Hybrid",
                "results": [
                    {
                        "source": r.metadata.get("source", ""),
                        "score": round(r.score, 4),
                        "semantic": round(r.semantic_score, 4),
                        "keyword": round(r.keyword_score, 4),
                        "text_preview": r.text[:100],
                    }
                    for r in results
                ],
            },
            "ms": rerank_ms,
        }}

        context = self.retriever.build_context(results)
        sources = [
            {"chunk_id": r.chunk_id, "score": r.score, "source": r.metadata.get("source", "")}
            for r in results
        ]
        yield {"type": "sources", "data": sources}

        # === 6. Context 구성 ===
        yield {"type": "trace", "data": {
            "step": "context",
            "status": "done",
            "detail": {
                "context_length": len(context),
                "num_documents": len(results),
            },
            "ms": 0,
        }}

        # === 7. LLM 스트리밍 ===
        prompt = f"참고 문서:\n{context}\n\n질문: {rewritten_query}"
        history = session.get_history()

        yield {"type": "trace", "data": {
            "step": "llm",
            "status": "streaming",
            "detail": {
                "model": self.llm.model,
                "prompt_length": len(prompt),
                "history_messages": len(history),
                "max_tokens": self.llm.max_tokens,
            },
            "ms": 0,
        }}

        full_answer = []
        llm_start = time.time()
        token_count = 0
        try:
            async for token in self.llm.generate_stream(SYSTEM_PROMPT, prompt, history):
                full_answer.append(token)
                token_count += 1
                yield {"type": "token", "data": token}
        except Exception as e:
            detail = str(e)[:200] if str(e) else type(e).__name__
            error_msg = f"LLM 응답 오류: {detail}"
            yield {"type": "token", "data": error_msg}
            full_answer.append(error_msg)

        llm_ms = round((time.time() - llm_start) * 1000)
        answer = "".join(full_answer)

        yield {"type": "trace", "data": {
            "step": "llm",
            "status": "done",
            "detail": {
                "tokens": token_count,
                "answer_length": len(answer),
                "tokens_per_sec": round(token_count / (llm_ms / 1000), 1) if llm_ms > 0 else 0,
            },
            "ms": llm_ms,
        }}

        # === 8. 세션 저장 + 캐시 ===
        session.add_message("user", user_query)
        session.add_message("assistant", answer)

        # 에러 응답은 캐시에 넣으면 안 됨 — 한번 잘못된 응답 캐시되면 계속 나옴
        if not answer.startswith("LLM 응답 오류"):
            await self.cache.async_store(rewritten_query, query_embedding, answer, context)

        total_ms = round((time.time() - pipeline_start) * 1000)
        yield {"type": "trace", "data": {
            "step": "complete",
            "status": "done",
            "detail": {"cached_after": not answer.startswith("LLM 응답 오류")},
            "ms": total_ms,
        }}

        yield {"type": "done", "data": {"session_id": session.session_id, "cached": False, "total_ms": total_ms}}
