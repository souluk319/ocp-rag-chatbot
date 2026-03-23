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


SYSTEM_PROMPT_OPS = """당신은 OCP(OpenShift Container Platform) 운영 전문가입니다.
아래 제공된 "참고 문서"만을 기반으로 정확하고 실용적인 답변을 제공하세요.

중요 규칙:
1. 반드시 아래 제공된 참고 문서를 최대한 활용하여 답변하세요.
2. 참고 문서에 관련 내용이 조금이라도 있으면, 그 내용을 기반으로 최선의 답변을 제공하세요.
3. 참고 문서에 전혀 관련 없는 질문일 때만 "제공된 문서에서 해당 정보를 찾지 못했습니다."라고 답변하세요.
4. 기술 용어는 정확하게 사용하고, 문서에 예시가 있다면 포함하세요.
5. 답변은 구조화된 형태(번호, 불릿, 표 등)로 작성하세요.
6. 한국어로 답변하세요.
7. 출처를 밝힐 때 "[문서 1]" 같은 번호 대신, 실제 파일명(예: "네트워킹.pdf에 따르면", "k8s-workload-types-ko.md에 의하면")을 사용하세요.
8. 영문 참고 문서의 내용도 한국어로 번역하여 자연스럽게 답변에 포함하세요."""

SYSTEM_PROMPT_LEARN = """당신은 OCP(OpenShift Container Platform) 학습 도우미입니다.
아래 제공된 "참고 문서"를 기반으로 초보자가 이해하기 쉽게 설명하세요.

중요 규칙:
1. 반드시 아래 제공된 참고 문서를 최대한 활용하여 답변하세요.
2. 참고 문서에 관련 내용이 조금이라도 있으면 그것을 기반으로 답변하세요. 전혀 관련 없을 때만 "제공된 문서에서 해당 정보를 찾지 못했습니다."라고 답변하세요.
3. 개념을 설명할 때 비유나 예시를 적극 활용하세요.
4. 복잡한 내용은 단계별로 나누어 설명하세요.
5. 기술 용어를 처음 사용할 때는 간단한 설명을 괄호 안에 덧붙이세요.
6. 답변은 구조화된 형태(번호, 불릿, 표 등)로 작성하세요.
7. 한국어로 답변하세요.
8. 출처를 밝힐 때 실제 파일명을 사용하세요."""

FOLLOWUP_SUFFIX = """

마지막으로, 답변이 끝난 후 반드시 아래 형식으로 사용자가 이어서 물어볼 수 있는 관련 질문 3개를 제안하세요:

[추천 질문]
1. (첫 번째 추천 질문)
2. (두 번째 추천 질문)
3. (세 번째 추천 질문)"""


def get_system_prompt(mode: str) -> str:
    """모드별 시스템 프롬프트 반환 (학습/운영)"""
    base = SYSTEM_PROMPT_LEARN if mode == "learn" else SYSTEM_PROMPT_OPS
    return base + FOLLOWUP_SUFFIX


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
        endpoint_key: Optional[str] = None,
        mode: str = "ops",
    ) -> dict:
        """비스트리밍 RAG 응답"""
        session = self.session_mgr.get_or_create(session_id)
        rewritten_query = await self.query_rewriter.rewrite(user_query, session)
        query_embedding = self.embedding.embed(rewritten_query)
        effective_endpoint_key = endpoint_key or self.llm.current_endpoint_key
        cache_query = f"[{mode}]{rewritten_query}"

        cached = await self.cache.async_lookup(cache_query, query_embedding)
        if cached:
            session.add_message("user", user_query)
            session.add_message("assistant", cached.response)
            return {
                "session_id": session.session_id,
                "answer": cached.response,
                "sources": cached.sources,
                "rewritten_query": rewritten_query,
                "cached": True,
            }

        results = self.retriever.retrieve(rewritten_query, top_k=top_k)
        sources = [
            {"chunk_id": r.chunk_id, "score": r.score, "source": r.metadata.get("source", "")}
            for r in results
        ]
        context = self.retriever.build_context(results)

        prompt = f"참고 문서:\n{context}\n\n질문: {rewritten_query}"
        history = session.get_history()
        system_prompt = get_system_prompt(mode)
        answer = await self.llm.generate(system_prompt, prompt, history, endpoint_key=effective_endpoint_key)

        session.add_message("user", user_query)
        session.add_message("assistant", answer)
        await self.cache.async_store(
            cache_query,
            query_embedding,
            answer,
            context,
            sources,
            effective_endpoint_key,
            self.llm._resolve_target(effective_endpoint_key)["model"],
        )

        return {
            "session_id": session.session_id,
            "answer": answer,
            "sources": sources,
            "rewritten_query": rewritten_query,
            "cached": False,
        }

    async def query_stream(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        top_k: int = TOP_K,
        endpoint_key: Optional[str] = None,
        mode: str = "ops",
    ) -> AsyncGenerator[dict, None]:
        """스트리밍 RAG 응답 - SSE용 이벤트 생성 (트레이스 포함)"""
        pipeline_start = time.time()
        session = self.session_mgr.get_or_create(session_id)
        effective_endpoint_key = endpoint_key or self.llm.current_endpoint_key
        target = self.llm._resolve_target(effective_endpoint_key)
        system_prompt = get_system_prompt(mode)

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
        query_profile = self.retriever.classify_query(rewritten_query)
        yield {"type": "trace", "data": {
            "step": "rewrite",
            "status": "done",
            "detail": {
                "original": user_query,
                "rewritten": rewritten_query,
                "changed": user_query != rewritten_query,
                "query_type": query_profile["type"],
                "entity": query_profile["entity"],
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
        cache_query = f"[{mode}]{rewritten_query}"
        cached = await self.cache.async_lookup(cache_query, query_embedding)
        cache_ms = round((time.time() - t) * 1000)
        if cached:
            yield {"type": "trace", "data": {
                "step": "cache",
                "status": "hit",
                "detail": {
                    "cached_query": cached.query[:80],
                    "hit_count": cached.hit_count,
                    "source_count": len(cached.sources),
                    "endpoint": cached.endpoint_key,
                    "model": cached.model,
                },
                "ms": cache_ms,
            }}
            session.add_message("user", user_query)
            session.add_message("assistant", cached.response)
            yield {"type": "sources", "data": cached.sources}
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
                "model": target["model"],
                "endpoint": effective_endpoint_key,
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
            async for token in self.llm.generate_stream(
                system_prompt,
                prompt,
                history,
                endpoint_key=effective_endpoint_key,
            ):
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
            await self.cache.async_store(
                cache_query,
                query_embedding,
                answer,
                context,
                sources,
                effective_endpoint_key,
                target["model"],
            )

        total_ms = round((time.time() - pipeline_start) * 1000)
        yield {"type": "trace", "data": {
            "step": "complete",
            "status": "done",
            "detail": {"cached_after": not answer.startswith("LLM 응답 오류")},
            "ms": total_ms,
        }}

        yield {"type": "done", "data": {"session_id": session.session_id, "cached": False, "total_ms": total_ms}}
