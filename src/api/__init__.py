"""FastAPI 엔드포인트"""
import asyncio
import json
import logging
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from sse_starlette.sse import EventSourceResponse

from src.llm import LLMClient
from src.embedding import EmbeddingEngine
from src.vectorstore import IVFIndex
from src.retriever import Retriever
from src.session import SessionManager
from src.cache import SemanticCache
from src.pipeline import RAGPipeline
from src.config import INDEX_DIR, EMBEDDING_DIM, HOST, PORT, LLM_ENDPOINTS

logger = logging.getLogger(__name__)

app = FastAPI(title="OCP RAG Chatbot", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 컴포넌트 (앱 시작 시 초기화)
llm_client = LLMClient()
embedding_engine = EmbeddingEngine()
session_manager = SessionManager()
semantic_cache = SemanticCache()
pipeline: Optional[RAGPipeline] = None


@app.on_event("startup")
async def startup():
    """서버 시작 시 인덱스 로드"""
    global pipeline

    # Redis 연결 (REDIS_URL 없으면 None — 인메모리 모드)
    from src.redis_client import get_redis
    redis_client = get_redis()
    if redis_client:
        session_manager.set_redis(redis_client)
        semantic_cache.set_redis(redis_client)
        embedding_engine.set_redis(redis_client)
        print("Redis 연결됨 — 세션/캐시 영속화 활성화")
    else:
        print("Redis 없음 — 인메모리 모드로 동작")

    # 인덱스 로드 시도
    try:
        index = IVFIndex.load(INDEX_DIR)
        print(f"인덱스 로드 완료: {index.stats()}")
    except FileNotFoundError:
        print("인덱스 파일이 없습니다. data/sanitized_raw 기준으로 scripts/build_index.py를 먼저 실행하세요.")
        # 빈 인덱스로 시작 (개발용)
        index = IVFIndex(dim=EMBEDDING_DIM)

    retriever = Retriever(index=index, embedding_engine=embedding_engine)
    # BM25 전체 코퍼스 인덱싱 — 임베딩이 못 잡는 키워드 매칭 문서를 독립 검색
    if index.documents:
        retriever.bm25.index_corpus(index.documents)
        print(f"BM25 코퍼스 인덱싱 완료: {len(index.documents)}개 문서")
    pipeline = RAGPipeline(
        llm_client=llm_client,
        embedding_engine=embedding_engine,
        index=index,
        retriever=retriever,
        session_manager=session_manager,
        cache=semantic_cache,
    )

    # 임베딩 모델 워밍업 — lazy loading 대신 서버 시작 시 미리 로드
    # 첫 요청의 ~37초 콜드스타트를 제거하기 위함
    print("임베딩 모델 워밍업 시작...")
    embedding_engine.embed("warmup")
    print("임베딩 모델 워밍업 완료")

    # 만료 세션 주기적 정리 (10분마다)
    asyncio.create_task(_cleanup_sessions_periodically())


async def _cleanup_sessions_periodically():
    """백그라운드 세션 정리 태스크"""
    while True:
        await asyncio.sleep(600)
        session_manager.cleanup_expired()
        logger.debug("만료 세션 정리 완료")


# === Request/Response 모델 ===

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    stream: bool = True
    endpoint_key: Optional[str] = None
    mode: str = Field(default="ops", pattern="^(learn|ops)$")


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[dict]
    rewritten_query: str
    cached: bool


# === API 엔드포인트 ===

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """비스트리밍 채팅 API"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="파이프라인이 초기화되지 않았습니다.")
    try:
        result = await pipeline.query(req.query, req.session_id, req.top_k, req.endpoint_key, req.mode)
        return ChatResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("비스트리밍 채팅 실패")
        raise HTTPException(status_code=502, detail=f"LLM 응답 오류: {e}")


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """스트리밍 채팅 API (SSE)"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="파이프라인이 초기화되지 않았습니다.")

    async def event_generator():
        async for event in pipeline.query_stream(req.query, req.session_id, req.top_k, req.endpoint_key, req.mode):
            # 모든 데이터를 JSON으로 인코딩 (SSE data 필드에 개행 방지)
            yield {
                "event": event["type"],
                "data": json.dumps(event["data"], ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


@app.get("/api/sessions")
async def list_sessions():
    """활성 세션 목록"""
    return {"sessions": session_manager.list_sessions()}


@app.get("/api/session/{session_id}/history")
async def session_history(session_id: str):
    """세션 대화 이력 조회"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    return {"session_id": session_id, "history": session.get_history()}


@app.post("/api/cache/clear")
async def clear_cache():
    """시맨틱 캐시 초기화"""
    semantic_cache.clear()
    return {"status": "ok", "message": "캐시가 초기화되었습니다."}


@app.get("/api/stats")
async def system_stats():
    """시스템 상태 조회"""
    stats = {
        "embedding_cache": embedding_engine.cache_stats(),
        "semantic_cache": semantic_cache.stats(),
        "index": pipeline.index.stats() if pipeline else {},
        "active_sessions": len(session_manager.list_sessions()),
    }
    return stats


# === LLM 엔드포인트 관리 API ===

class EndpointRequest(BaseModel):
    key: str


@app.get("/api/llm/endpoints")
async def list_endpoints():
    """사용 가능한 LLM 엔드포인트 목록 + 현재 선택"""
    endpoints = []
    for key, ep in LLM_ENDPOINTS.items():
        endpoints.append({
            "key": key,
            "name": ep["name"],
            "model": ep["model"],
            "active": key == llm_client.current_endpoint_key,
        })
    return {"endpoints": endpoints, "current": llm_client.current_endpoint_key}


@app.post("/api/llm/endpoint")
async def switch_endpoint(req: EndpointRequest):
    """LLM 엔드포인트 전환 + 모델명 자동 감지"""
    try:
        ep = llm_client.switch_endpoint(req.key)
        # 서버에 연결해서 실제 모델명 자동 감지
        detected = await llm_client.auto_detect_model()
        return {
            "status": "ok",
            "switched_to": ep["name"],
            "url": ep["url"],
            "model": detected or ep["model"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/llm/health")
async def llm_health(key: Optional[str] = Query(default=None)):
    """현재 LLM 엔드포인트 연결 상태 확인"""
    result = await llm_client.health_check(key)
    current_key = key or llm_client.current_endpoint_key
    current = LLM_ENDPOINTS.get(current_key, {})
    return {
        "endpoint": current.get("name", "unknown"),
        "key": current_key,
        **result,
    }


# Frontend 정적 파일 서빙
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(
            os.path.join(frontend_dir, "index.html"),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
