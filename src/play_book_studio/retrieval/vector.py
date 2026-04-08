# Qdrant 기반 의미 검색을 담당하는 최소 vector retriever다.
# hybrid retrieval에서는 이 모듈이 semantic 후보만 준비하고, 최종 결합은 retriever가 맡는다.
from __future__ import annotations

from typing import Any

import requests

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.embedding import EmbeddingClient

from .models import RetrievalHit


def hit_from_payload(payload: dict[str, Any], *, source: str, score: float) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=str(payload["chunk_id"]),
        book_slug=str(payload["book_slug"]),
        chapter=str(payload.get("chapter", "")),
        section=str(payload.get("section", "")),
        anchor=str(payload.get("anchor", "")),
        source_url=str(payload.get("source_url", "")),
        viewer_path=str(payload.get("viewer_path", "")),
        text=str(payload.get("text", "")),
        source=source,
        raw_score=float(score),
        fused_score=float(score),
    )


class VectorRetriever:
    """hybrid retrieval의 한 신호로 쓰이는 최소 Qdrant vector retriever."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedding_client = EmbeddingClient(settings)

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        vector = self.embedding_client.embed_texts([query])[0]
        payloads = [
            (
                f"{self.settings.qdrant_url}/collections/{self.settings.qdrant_collection}/points/search",
                {
                    "vector": vector,
                    "limit": top_k,
                    "with_payload": True,
                    "with_vector": False,
                },
            ),
            (
                f"{self.settings.qdrant_url}/collections/{self.settings.qdrant_collection}/points/query",
                {
                    "query": vector,
                    "limit": top_k,
                    "with_payload": True,
                    "with_vector": False,
                },
            ),
        ]

        last_error = "vector search failed"
        for url, payload in payloads:
            response = requests.post(
                url,
                json=payload,
                timeout=max(self.settings.request_timeout_seconds, 30),
            )
            if not response.ok:
                last_error = response.text[:500]
                continue
            result = response.json()["result"]
            points = result["points"] if isinstance(result, dict) and "points" in result else result
            hits: list[RetrievalHit] = []
            for point in points:
                payload_row = point.get("payload") or {}
                if not payload_row:
                    continue
                hits.append(
                    hit_from_payload(
                        payload_row,
                        source="vector",
                        score=float(point.get("score", 0.0)),
                    )
                )
            return hits

        raise ValueError(last_error)
