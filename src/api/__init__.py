"""FastAPI 엔드포인트"""
import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from sse_starlette.sse import EventSourceResponse

from src.llm import LLMClient
from src.embedding import EmbeddingEngine
from src.vectorstore import IVFIndex
from src.retriever import Retriever
from src.session import SessionManager
from src.cache import SemanticCache
from src.pipeline import RAGPipeline
from src.config import INDEX_DIR, EMBEDDING_DIM, HOST, PORT

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

    # 인덱스 로드 시도
    try:
        index = IVFIndex.load(INDEX_DIR)
        print(f"인덱스 로드 완료: {index.stats()}")
    except FileNotFoundError:
        print("인덱스 파일이 없습니다. scripts/build_index.py를 먼저 실행하세요.")
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


# === Request/Response 모델 ===

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    top_k: int = 5
    stream: bool = True


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
    result = await pipeline.query(req.query, req.session_id, req.top_k)
    return ChatResponse(**result)


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """스트리밍 채팅 API (SSE)"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="파이프라인이 초기화되지 않았습니다.")

    async def event_generator():
        async for event in pipeline.query_stream(req.query, req.session_id, req.top_k):
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


# Frontend 정적 파일 서빙
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
