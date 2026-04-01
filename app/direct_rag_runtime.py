from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from sentence_transformers import SentenceTransformer

from app.runtime_config import load_runtime_config
from app.runtime_source_index import load_active_source_catalog
from app.vector_index import VectorIndex, VectorRecord, VectorSearchResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _build_document_text(document: dict[str, Any]) -> str:
    title = str(document.get("title", "")).strip()
    document_path = str(document.get("document_path", "")).strip()
    category = str(document.get("category", "")).strip()
    source_dir = str(document.get("top_level_dir", "")).strip()
    sections = document.get("sections", []) or []
    section_titles = [
        str(section.get("section_title", "")).strip()
        for section in sections[:8]
        if str(section.get("section_title", "")).strip()
    ]
    body = _read_text(str(document.get("normalized_path", "")))
    excerpt = body[:4000]
    return "\n".join(
        part
        for part in [
            title,
            document_path,
            source_dir,
            category,
            " ; ".join(section_titles),
            excerpt,
        ]
        if part
    )


@lru_cache(maxsize=1)
def load_sentence_embedder() -> SentenceTransformer:
    config = load_runtime_config()
    return SentenceTransformer(config.embedding_model, device="cpu")


@dataclass(frozen=True)
class DirectRagSource:
    sourcePath: str
    headingHierarchy: list[str]
    score: float


def _direct_index_path(index_id: str) -> Path:
    return (
        _repo_root()
        / "data"
        / "manifests"
        / "generated"
        / f"direct-rag-{index_id}.json"
    )


def _persist_vector_index(index: VectorIndex, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    index.save(path)


def _load_vector_index_from_disk(path: Path) -> VectorIndex:
    return VectorIndex.load(path)


@lru_cache(maxsize=1)
def load_direct_vector_index() -> tuple[VectorIndex, dict[str, dict[str, Any]]]:
    catalog = load_active_source_catalog()
    config = load_runtime_config()
    documents = list(catalog.documents)
    by_chunk_id: dict[str, dict[str, Any]] = {}
    for document in documents:
        chunk_id = (
            str(document.get("document_id", "")).strip()
            or str(document.get("document_path", "")).strip()
        )
        by_chunk_id[chunk_id] = document

    cache_path = _direct_index_path(catalog.index_id)
    if cache_path.exists():
        return _load_vector_index_from_disk(cache_path), by_chunk_id

    embedder = load_sentence_embedder()
    corpus = [_build_document_text(document) for document in documents]
    vectors = embedder.encode(corpus, normalize_embeddings=False).tolist()
    index = VectorIndex(dimensions=config.embedding_dimensions)

    for document, vector in zip(documents, vectors, strict=False):
        sections = document.get("sections", []) or []
        first_section = sections[0] if sections else {}
        chunk_id = (
            str(document.get("document_id", "")).strip()
            or str(document.get("document_path", "")).strip()
        )
        record = VectorRecord(
            chunk_id=chunk_id,
            document_id=str(document.get("document_id", "")).strip(),
            document_path=str(document.get("document_path", "")).strip(),
            section_id=str(first_section.get("section_id", "")).strip(),
            section_title=str(first_section.get("section_title", "")).strip()
            or str(document.get("title", "")).strip(),
            viewer_url=str(document.get("viewer_url", "")).strip(),
            embedding=tuple(float(value) for value in vector),
            metadata={
                "html_path": str(document.get("html_path", "")).strip(),
                "top_level_dir": str(document.get("top_level_dir", "")).strip(),
                "category": str(document.get("category", "")).strip(),
                "title": str(document.get("title", "")).strip(),
            },
        )
        index.add(record)

    _persist_vector_index(index, cache_path)
    return index, by_chunk_id


def reset_direct_vector_index() -> None:
    load_direct_vector_index.cache_clear()


def search_direct_sources(query: str, *, top_k: int = 12) -> list[DirectRagSource]:
    embedder = load_sentence_embedder()
    query_vector = embedder.encode([query], normalize_embeddings=False).tolist()[0]
    index, by_chunk_id = load_direct_vector_index()
    results: list[VectorSearchResult] = index.search(
        tuple(float(value) for value in query_vector), top_k=top_k
    )
    sources: list[DirectRagSource] = []
    for result in results:
        document = by_chunk_id.get(result.chunk_id, {})
        html_path = str(document.get("html_path", "")).strip()
        viewer_url = str(document.get("viewer_url", "")).strip()
        source_path = html_path or viewer_url
        heading = (
            str(result.section_title).strip() or str(document.get("title", "")).strip()
        )
        sources.append(
            DirectRagSource(
                sourcePath=source_path,
                headingHierarchy=[heading] if heading else [],
                score=float(result.score),
            )
        )
    return sources
