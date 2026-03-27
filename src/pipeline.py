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
아래 제공된 "참고 문서"를 기반으로 답변하세요.

핵심 규칙:
1. 질문의 범위에 정확히 맞춰서 답변하세요. 질문하지 않은 내용까지 확장하지 마세요.
2. 핵심을 3~5문장으로 먼저 전달하고, 필요한 경우에만 구체적 명령어나 예시를 추가하세요.
3. 참고 문서에 없는 내용은 "제공된 문서에서 해당 정보를 찾지 못했습니다."라고 답변하세요.
4. 한국어로 답변하세요. 영문 문서 내용도 한국어로 번역하세요.
5. 출처는 실제 파일명으로 밝히세요 (예: "ocp-etcd-overview-ko.md에 따르면").
6. 한 번에 모든 것을 설명하려 하지 말고, 사용자가 추가 질문할 수 있도록 간결하게 답변하세요."""

SYSTEM_PROMPT_LEARN = """당신은 OCP(OpenShift Container Platform) 학습 도우미입니다.
아래 제공된 "참고 문서"를 기반으로 초보자가 이해하기 쉽게 설명하세요.

핵심 규칙:
1. 질문한 내용에 대해서만 간결하게 설명하세요. 관련 없는 내용으로 확장하지 마세요.
2. 핵심 개념을 먼저 2~3문장으로 요약하고, 필요하면 예시를 추가하세요.
3. 참고 문서에 없는 내용은 "제공된 문서에서 해당 정보를 찾지 못했습니다."라고 답변하세요.
4. 기술 용어를 처음 사용할 때는 간단한 설명을 괄호 안에 덧붙이세요.
5. 한국어로 답변하세요. 출처는 실제 파일명으로 밝히세요.
6. 한 번에 모든 것을 설명하지 말고, 사용자가 더 물어볼 수 있도록 핵심만 전달하세요."""

FOLLOWUP_SUFFIX = """

마지막으로, 답변이 끝난 후 반드시 아래 형식으로 사용자가 이어서 물어볼 수 있는 관련 질문 3개를 제안하세요:

[추천 질문]
1. (첫 번째 추천 질문)
2. (두 번째 추천 질문)
3. (세 번째 추천 질문)"""

# 소형/양자화 모델은 instruction following이 약해서 한국어 지시를 강화
SMALL_MODEL_KO_PREFIX = """[최우선 규칙] 모든 답변을 반드시 한국어로 작성하세요. 영어로 된 참고 문서도 한국어로 번역하여 답변하세요. English output is NOT allowed.

"""


def get_system_prompt(mode: str, force_korean: bool = False) -> str:
    """모드별 시스템 프롬프트 반환 (학습/운영)"""
    base = SYSTEM_PROMPT_LEARN if mode == "learn" else SYSTEM_PROMPT_OPS
    prompt = base + FOLLOWUP_SUFFIX
    if force_korean:
        prompt = SMALL_MODEL_KO_PREFIX + prompt
    return prompt


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
        target = self.llm._resolve_target(effective_endpoint_key)
        is_small_model = any(tag in target["model"].lower() for tag in ("4bit", "3b", "4b", "2b", "1b", "gguf"))
        system_prompt = get_system_prompt(mode, force_korean=is_small_model)
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
        # 소형/양자화 모델이면 한국어 지시 강화 (4bit, 3b, 4b 등)
        is_small_model = any(tag in target["model"].lower() for tag in ("4bit", "3b", "4b", "2b", "1b", "gguf"))
        system_prompt = get_system_prompt(mode, force_korean=is_small_model)

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
                    "sources": cached.sources,  # 프론트 fallback용
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
                "query_type": query_profile["type"],
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

        yield {"type": "done", "data": {
            "session_id": session.session_id,
            "cached": False,
            "query_type": query_profile["type"],
            "total_ms": total_ms,
        }}
