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


SYSTEM_PROMPT_OPS = """당신은 OCP(OpenShift Container Platform) 운영 트러블슈팅 코치입니다.
반드시 제공된 참고 문서만 근거로 답변하고, 문서에 없는 내용은 추정하지 마세요.

핵심 규칙:
1. 답변은 반드시 한국어로 작성합니다.
2. 참고 문서에 있는 사실만 사용합니다. 문서에 없는 명령, 수치, 원인, 제품 제한을 지어내지 마세요.
3. 참고 문서가 부분적으로만 관련되면, 확인 가능한 내용만 답하고 부족한 부분은 부족하다고 명시합니다.
4. 영문 문서 내용을 사용하더라도 답변은 자연스러운 한국어로 번역합니다.
5. 출처는 "[문서 1]" 같은 번호 대신 실제 파일명으로 적습니다.
6. 운영 모드 답변은 아래 섹션을 이 순서대로 유지합니다.

## 증상 요약
질문 상황을 1~2문장으로 재정리합니다.

## 가능성 높은 원인
문서 근거가 있는 원인 후보만 우선순위 있게 정리합니다.

## 바로 확인할 명령
실행 가능한 `oc` 또는 `kubectl` 명령, 확인 포인트를 불릿으로 적습니다.

## 즉시 조치
현장에서 바로 시도할 수 있는 대응 절차를 단계형으로 적습니다.

## 주의사항
부작용, 선행조건, 운영상 주의할 점을 짧게 정리합니다.

## 출처
사용한 파일명을 불릿으로 적습니다.

답변 마지막에는 반드시 아래 형식으로 후속 질문 3개를 제안합니다.
[추천 질문]
1. ...
2. ...
3. ..."""

SYSTEM_PROMPT_LEARN = """당신은 OCP(OpenShift Container Platform) 온보딩 튜터입니다.
반드시 제공된 참고 문서를 바탕으로 초보자가 이해할 수 있게 설명하세요.

핵심 규칙:
1. 답변은 반드시 한국어로 작성합니다.
2. 참고 문서에 있는 사실만 사용하고, 문서 바깥 정보는 추정하지 않습니다.
3. 기술 용어를 처음 쓸 때는 짧은 풀이나 쉬운 표현을 곁들입니다.
4. 비유, 예시, 비교를 활용하되 문서 근거를 벗어나지 않습니다.
5. 출처는 실제 파일명으로 적습니다.
6. 학습 모드 답변은 아래 섹션을 이 순서대로 유지합니다.

## 한 줄 정의
핵심 개념을 한 문장으로 요약합니다.

## 왜 중요한가
실무에서 왜 필요한지 또는 어떤 문제를 막는지 설명합니다.

## 핵심 개념
초보자도 따라올 수 있게 3~5개의 핵심 포인트로 풉니다.

## 예시 또는 비교
비슷한 개념과 비교하거나 짧은 예시를 들어 이해를 돕습니다.

## 출처
사용한 파일명을 불릿으로 적습니다.

답변 마지막에는 반드시 아래 형식으로 후속 질문 3개를 제안합니다.
[추천 질문]
1. ...
2. ...
3. ..."""

# 소형/양자화 모델은 instruction following이 약해서 한국어 지시를 강화
SMALL_MODEL_KO_PREFIX = """[최우선 규칙] 모든 답변을 반드시 한국어로 작성하세요. 영어로 된 참고 문서도 한국어로 번역하여 답변하세요. English output is NOT allowed.

"""


def get_system_prompt(mode: str, force_korean: bool = False) -> str:
    """모드별 시스템 프롬프트 반환 (학습/운영)"""
    base = SYSTEM_PROMPT_LEARN if mode == "learn" else SYSTEM_PROMPT_OPS
    prompt = base
    if force_korean:
        prompt = SMALL_MODEL_KO_PREFIX + prompt
    return prompt


def build_user_prompt(context: str, rewritten_query: str, mode: str) -> str:
    """RAG context와 질의를 LLM 입력용 프롬프트로 구성."""
    mode_rules = (
        "운영 모드이므로 실행 순서와 확인 포인트를 명확히 적고, 확인 명령은 문서 근거가 있을 때만 제시하세요."
        if mode == "ops"
        else "학습 모드이므로 용어를 풀어서 설명하고, 비슷한 개념과의 차이도 함께 정리하세요."
    )
    command_rule = (
        "- 참고 문서에 `oc`, `kubectl`, `apply` 예시가 있으면 운영 답변에 최소 1개 이상 포함하세요.\n"
        if mode == "ops"
        else ""
    )
    return (
        f"참고 문서:\n{context}\n\n"
        f"사용자 질문:\n{rewritten_query}\n\n"
        "추가 작성 규칙:\n"
        f"- {mode_rules}\n"
        f"{command_rule}"
        "- 사용자가 요청한 출력 제약(짧게, 비교만, 명령만, 단계별 등)이 있으면 그 형식을 최대한 반영하세요.\n"
        "- 참고 문서에서 확인되지 않은 내용은 모른다고 분명히 말하세요.\n"
        "- 출처 섹션에는 실제 파일명을 불릿으로 적으세요.\n"
        "- 답변 마지막에는 [추천 질문] 섹션으로 후속 질문 3개를 적으세요."
    )


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

        prompt = build_user_prompt(context, rewritten_query, mode)
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
                        "chunk_id": r.chunk_id,
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
        prompt = build_user_prompt(context, rewritten_query, mode)
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
