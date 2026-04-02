from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import requests

from ocp_rag_part1.embedding import EmbeddingClient
from ocp_rag_part1.settings import Settings

from .bm25 import BM25Index
from .models import RetrievalHit, RetrievalResult, SessionContext
from .query import (
    contains_hangul,
    detect_unsupported_product,
    has_doc_locator_intent,
    is_generic_intro_query,
    normalize_query,
    query_book_adjustments,
    rewrite_query,
)


NOISE_SECTION_RE = re.compile(r"^Legal Notice$", re.IGNORECASE)


def _hit_from_payload(payload: dict, *, source: str, score: float) -> RetrievalHit:
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


def _is_noise_hit(hit: RetrievalHit) -> bool:
    return bool(NOISE_SECTION_RE.match(hit.section.strip()))


def fuse_ranked_hits(
    query: str,
    ranked_lists: dict[str, list[RetrievalHit]],
    *,
    top_k: int,
    rrf_k: int = 60,
    weights: dict[str, float] | None = None,
) -> list[RetrievalHit]:
    # Give semantic hits a small edge during ties while keeping fusion explainable.
    weights = weights or {"bm25": 1.0, "vector": 1.1}
    fused_by_id: dict[str, RetrievalHit] = {}
    book_sources: dict[str, set[str]] = {}
    query_has_hangul = contains_hangul(query)
    book_boosts, book_penalties = query_book_adjustments(query)
    doc_locator_intent = has_doc_locator_intent(query)

    for source_name, hits in ranked_lists.items():
        weight = weights.get(source_name, 1.0)
        for rank, hit in enumerate(hits, start=1):
            if _is_noise_hit(hit):
                continue
            if rank <= 10:
                book_sources.setdefault(hit.book_slug, set()).add(source_name)
            if hit.chunk_id not in fused_by_id:
                fused_hit = copy.deepcopy(hit)
                fused_hit.source = "hybrid"
                fused_hit.fused_score = 0.0
                fused_hit.component_scores = {}
                fused_by_id[hit.chunk_id] = fused_hit
            fused = fused_by_id[hit.chunk_id]
            fused.component_scores[f"{source_name}_score"] = float(hit.raw_score)
            fused.component_scores[f"{source_name}_rank"] = float(rank)
            fused.fused_score += weight / (rrf_k + rank)

    fused_hits = list(fused_by_id.values())
    for hit in fused_hits:
        if len(book_sources.get(hit.book_slug, set())) >= 2:
            hit.fused_score *= 1.1
        elif query_has_hangul and "vector_score" in hit.component_scores and "bm25_score" not in hit.component_scores:
            hit.fused_score *= 0.95
        if query_has_hangul:
            if contains_hangul(hit.text):
                hit.fused_score *= 1.05
            else:
                hit.fused_score *= 0.85
        if is_generic_intro_query(query):
            if hit.book_slug == "architecture":
                hit.fused_score *= 1.22
            elif hit.book_slug == "overview":
                hit.fused_score *= 1.16
            elif hit.book_slug.endswith("_overview"):
                hit.fused_score *= 0.84
            elif hit.book_slug in {"api_overview", "networking_overview", "project_apis"}:
                hit.fused_score *= 0.88
        if doc_locator_intent and hit.book_slug.endswith("_apis"):
            hit.fused_score *= 0.82
        if hit.book_slug in book_boosts:
            hit.fused_score *= book_boosts[hit.book_slug]
        if hit.book_slug in book_penalties:
            hit.fused_score *= book_penalties[hit.book_slug]
        hit.raw_score = hit.fused_score

    fused_hits.sort(
        key=lambda item: (
            -item.fused_score,
            -int(contains_hangul(item.text)),
            item.book_slug,
            item.chunk_id,
        )
    )
    return fused_hits[:top_k]


class VectorRetriever:
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
                    _hit_from_payload(
                        payload_row,
                        source="vector",
                        score=float(point.get("score", 0.0)),
                    )
                )
            return hits

        raise ValueError(last_error)


class Part2Retriever:
    def __init__(
        self,
        settings: Settings,
        bm25_index: BM25Index,
        *,
        vector_retriever: VectorRetriever | None = None,
    ) -> None:
        self.settings = settings
        self.bm25_index = bm25_index
        self.vector_retriever = vector_retriever

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        *,
        enable_vector: bool = True,
    ) -> "Part2Retriever":
        bm25_index = BM25Index.from_jsonl(settings.bm25_corpus_path)
        vector_retriever = VectorRetriever(settings) if enable_vector else None
        return cls(settings, bm25_index, vector_retriever=vector_retriever)

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
    ) -> RetrievalResult:
        context = context or SessionContext()
        normalized_query = normalize_query(query)
        warnings: list[str] = []
        unsupported_product = detect_unsupported_product(normalized_query)
        rewritten_query = rewrite_query(normalized_query, context)

        if unsupported_product is not None:
            warnings.append(f"query appears outside OCP corpus: {unsupported_product}")
            return RetrievalResult(
                query=query,
                normalized_query=normalized_query,
                rewritten_query=rewritten_query,
                top_k=top_k,
                candidate_k=candidate_k,
                context=context.to_dict(),
                hits=[],
                trace={"warnings": warnings, "bm25": [], "vector": []},
            )

        bm25_hits = self.bm25_index.search(rewritten_query, top_k=candidate_k) if use_bm25 else []
        vector_hits: list[RetrievalHit] = []
        if use_vector:
            if self.vector_retriever is None:
                warnings.append("vector retriever is not configured")
            else:
                try:
                    vector_hits = self.vector_retriever.search(rewritten_query, top_k=candidate_k)
                except Exception as exc:  # noqa: BLE001
                    warnings.append(f"vector search failed: {exc}")

        hits = fuse_ranked_hits(
            rewritten_query,
            {"bm25": bm25_hits, "vector": vector_hits},
            top_k=top_k,
        )
        trace = {
            "warnings": warnings,
            "bm25": [hit.to_dict() for hit in bm25_hits[: min(candidate_k, 10)]],
            "vector": [hit.to_dict() for hit in vector_hits[: min(candidate_k, 10)]],
        }
        return RetrievalResult(
            query=query,
            normalized_query=normalized_query,
            rewritten_query=rewritten_query,
            top_k=top_k,
            candidate_k=candidate_k,
            context=context.to_dict(),
            hits=hits,
            trace=trace,
        )
