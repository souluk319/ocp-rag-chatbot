"""FastAPI application."""
import asyncio
import json
import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.cache import SemanticCache
from src.config import (
    EMBEDDING_DIM,
    EXPOSE_DEBUG_ENDPOINTS,
    EXPOSE_LLM_ENDPOINT_SWITCHER,
    INDEX_DIR,
    LOCKED_LLM_MODEL,
    LLM_ENDPOINTS,
    PRIMARY_LLM_ENDPOINT_KEY,
    SUBMISSION_MODE,
)
from src.embedding import EmbeddingEngine
from src.llm import LLMClient
from src.pipeline import RAGPipeline
from src.retriever import Retriever
from src.session import SessionManager
from src.vectorstore import IVFIndex

logger = logging.getLogger(__name__)

app = FastAPI(title="OCP RAG Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_client = LLMClient()
embedding_engine = EmbeddingEngine()
session_manager = SessionManager()
semantic_cache = SemanticCache()
pipeline: Optional[RAGPipeline] = None
source_chunk_lookup: dict[str, dict] = {}
source_group_lookup: dict[str, list[dict]] = {}
source_chunk_index_lookup: dict[tuple[str, int], dict] = {}


def endpoint_switching_enabled() -> bool:
    return (not SUBMISSION_MODE) and EXPOSE_LLM_ENDPOINT_SWITCHER


def debug_api_enabled() -> bool:
    return EXPOSE_DEBUG_ENDPOINTS


def _public_endpoint_keys() -> list[str]:
    if endpoint_switching_enabled():
        return list(LLM_ENDPOINTS.keys())
    current = llm_client.current_endpoint_key
    if current in LLM_ENDPOINTS:
        return [current]
    if PRIMARY_LLM_ENDPOINT_KEY in LLM_ENDPOINTS:
        return [PRIMARY_LLM_ENDPOINT_KEY]
    return [next(iter(LLM_ENDPOINTS))]


def _rebuild_source_lookup(index: IVFIndex) -> None:
    """Build in-memory lookups so the UI can preview retrieved source chunks."""
    global source_chunk_lookup, source_group_lookup, source_chunk_index_lookup

    source_chunk_lookup = {}
    source_group_lookup = {}
    source_chunk_index_lookup = {}

    for doc in index.documents:
        chunk_id = doc.get("chunk_id")
        metadata = doc.get("metadata", {})
        source_name = metadata.get("source") or (chunk_id.split("::", 1)[0] if chunk_id else "")
        chunk_index = metadata.get("chunk_index")

        if chunk_id:
            source_chunk_lookup[chunk_id] = doc
        if source_name:
            source_group_lookup.setdefault(source_name, []).append(doc)
        if source_name and isinstance(chunk_index, int):
            source_chunk_index_lookup[(source_name, chunk_index)] = doc

    for docs in source_group_lookup.values():
        docs.sort(key=lambda item: item.get("metadata", {}).get("chunk_index", 0))


def _find_source_doc(chunk_id: Optional[str], source: Optional[str]) -> Optional[dict]:
    if chunk_id:
        doc = source_chunk_lookup.get(chunk_id)
        if doc:
            return doc
    if source:
        docs = source_group_lookup.get(source)
        if docs:
            return docs[0]
    return None


@app.on_event("startup")
async def startup():
    """Load index and prepare the pipeline."""
    global pipeline

    try:
        index = IVFIndex.load(INDEX_DIR)
        print(f"Index loaded: {index.stats()}")
    except FileNotFoundError:
        print("Index not found. Run scripts/build_index.py first.")
        index = IVFIndex(dim=EMBEDDING_DIM)

    retriever = Retriever(index=index, embedding_engine=embedding_engine)
    if index.documents:
        retriever.bm25.index_corpus(index.documents)
        _rebuild_source_lookup(index)
        print(f"BM25 corpus indexed: {len(index.documents)} documents")

    pipeline = RAGPipeline(
        llm_client=llm_client,
        embedding_engine=embedding_engine,
        index=index,
        retriever=retriever,
        session_manager=session_manager,
        cache=semantic_cache,
    )

    print("Warming up embedding model...")
    embedding_engine.embed("warmup")
    print("Embedding model ready.")

    asyncio.create_task(_cleanup_sessions_periodically())


async def _cleanup_sessions_periodically():
    """Remove expired sessions in the background."""
    while True:
        await asyncio.sleep(600)
        session_manager.cleanup_expired()
        logger.debug("Expired sessions cleaned up")


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


class SourcePreviewResponse(BaseModel):
    source: str
    chunk_id: str
    chunk_index: Optional[int] = None
    total_chunks: int
    text: str
    previous_chunk: Optional[dict] = None
    next_chunk: Optional[dict] = None


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat API."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline is not initialized.")
    try:
        endpoint_key = req.endpoint_key if endpoint_switching_enabled() else None
        result = await pipeline.query(req.query, req.session_id, req.top_k, endpoint_key, req.mode)
        return ChatResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=502, detail=f"LLM request failed: {e}")


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming chat API (SSE)."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline is not initialized.")

    async def event_generator():
        endpoint_key = req.endpoint_key if endpoint_switching_enabled() else None
        async for event in pipeline.query_stream(req.query, req.session_id, req.top_k, endpoint_key, req.mode):
            yield {
                "event": event["type"],
                "data": json.dumps(event["data"], ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


@app.get("/api/source", response_model=SourcePreviewResponse)
async def source_preview(
    chunk_id: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
):
    """Return the retrieved chunk so the UI can show citation previews."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline is not initialized.")
    if not chunk_id and not source:
        raise HTTPException(status_code=400, detail="chunk_id or source is required.")

    doc = _find_source_doc(chunk_id, source)
    if not doc:
        raise HTTPException(status_code=404, detail="Source chunk not found.")

    metadata = doc.get("metadata", {})
    source_name = metadata.get("source") or source or ""
    chunk_index = metadata.get("chunk_index")
    total_chunks = len(source_group_lookup.get(source_name, []))

    previous_chunk = None
    next_chunk = None
    if source_name and isinstance(chunk_index, int):
        prev_doc = source_chunk_index_lookup.get((source_name, chunk_index - 1))
        next_doc = source_chunk_index_lookup.get((source_name, chunk_index + 1))
        if prev_doc:
            previous_chunk = {
                "chunk_id": prev_doc.get("chunk_id", ""),
                "chunk_index": prev_doc.get("metadata", {}).get("chunk_index"),
                "text": prev_doc.get("text", ""),
            }
        if next_doc:
            next_chunk = {
                "chunk_id": next_doc.get("chunk_id", ""),
                "chunk_index": next_doc.get("metadata", {}).get("chunk_index"),
                "text": next_doc.get("text", ""),
            }

    return SourcePreviewResponse(
        source=source_name,
        chunk_id=doc.get("chunk_id", ""),
        chunk_index=chunk_index if isinstance(chunk_index, int) else None,
        total_chunks=total_chunks,
        text=doc.get("text", ""),
        previous_chunk=previous_chunk,
        next_chunk=next_chunk,
    )


@app.get("/api/sessions")
async def list_sessions():
    if not debug_api_enabled():
        raise HTTPException(status_code=403, detail="Session inspection is disabled in submission mode.")
    return {"sessions": session_manager.list_sessions()}


@app.get("/api/session/{session_id}/history")
async def session_history(session_id: str):
    if not debug_api_enabled():
        raise HTTPException(status_code=403, detail="Session inspection is disabled in submission mode.")
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": session_id, "history": session.get_history()}


@app.post("/api/cache/clear")
async def clear_cache():
    if not debug_api_enabled():
        raise HTTPException(status_code=403, detail="Cache controls are disabled in submission mode.")
    semantic_cache.clear()
    return {"status": "ok", "message": "Cache cleared."}


@app.get("/api/stats")
async def system_stats():
    stats = {
        "embedding_cache": embedding_engine.cache_stats(),
        "semantic_cache": semantic_cache.stats(),
        "index": pipeline.index.stats() if pipeline else {},
        "active_sessions": len(session_manager.list_sessions()),
        "submission_mode": SUBMISSION_MODE,
        "endpoint_switching": endpoint_switching_enabled(),
        "debug_api_enabled": debug_api_enabled(),
        "locked_model": LOCKED_LLM_MODEL,
    }
    return stats


class EndpointRequest(BaseModel):
    key: str


@app.get("/api/llm/endpoints")
async def list_endpoints():
    """Return only the endpoints that should be visible in the UI."""
    visible_keys = _public_endpoint_keys()
    endpoints = []
    for key in visible_keys:
        ep = LLM_ENDPOINTS[key]
        endpoints.append(
            {
                "key": key,
                "name": ep["name"],
                "model": LOCKED_LLM_MODEL,
                "active": key == llm_client.current_endpoint_key,
            }
        )

    return {
        "endpoints": endpoints,
        "current": llm_client.current_endpoint_key,
        "submission_mode": SUBMISSION_MODE,
        "allow_endpoint_switch": endpoint_switching_enabled(),
        "show_endpoint_selector": endpoint_switching_enabled() and len(visible_keys) > 1,
        "debug_api_enabled": debug_api_enabled(),
        "locked_model": LOCKED_LLM_MODEL,
    }


@app.post("/api/llm/endpoint")
async def switch_endpoint(req: EndpointRequest):
    if not endpoint_switching_enabled():
        raise HTTPException(status_code=403, detail="Endpoint switching is disabled in submission mode.")
    try:
        ep = llm_client.switch_endpoint(req.key)
        detected = await llm_client.auto_detect_model()
        return {
            "status": "ok",
            "switched_to": ep["name"],
            "url": ep["url"],
            "model": detected or LOCKED_LLM_MODEL,
            "allow_endpoint_switch": endpoint_switching_enabled(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/llm/health")
async def llm_health(key: Optional[str] = Query(default=None)):
    target_key = key if endpoint_switching_enabled() else llm_client.current_endpoint_key
    result = await llm_client.health_check(target_key)
    current_key = target_key or llm_client.current_endpoint_key
    current = LLM_ENDPOINTS.get(current_key, {})
    return {
        "endpoint": current.get("name", "unknown"),
        "key": current_key,
        "model": LOCKED_LLM_MODEL,
        "submission_mode": SUBMISSION_MODE,
        "allow_endpoint_switch": endpoint_switching_enabled(),
        **result,
    }


frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(
            os.path.join(frontend_dir, "index.html"),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
