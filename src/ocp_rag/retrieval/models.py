from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ocp_rag.session.models import (
    BranchFocusSnapshot,
    CitationGroupMemory,
    CitationMemory,
    CommandTemplateMemory,
    ProcedureMemory,
    SessionContext,
    TurnMemory,
)


@dataclass(slots=True)
class RetrievalHit:
    chunk_id: str
    book_slug: str
    chapter: str
    section: str
    anchor: str
    source_url: str
    viewer_path: str
    text: str
    source: str
    raw_score: float
    fused_score: float = 0.0
    component_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RetrievalResult:
    query: str
    normalized_query: str
    rewritten_query: str
    top_k: int
    candidate_k: int
    context: dict[str, Any]
    hits: list[RetrievalHit]
    trace: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "normalized_query": self.normalized_query,
            "rewritten_query": self.rewritten_query,
            "top_k": self.top_k,
            "candidate_k": self.candidate_k,
            "context": self.context,
            "hits": [hit.to_dict() for hit in self.hits],
            "trace": self.trace,
        }


__all__ = [
    "BranchFocusSnapshot",
    "CitationGroupMemory",
    "CitationMemory",
    "CommandTemplateMemory",
    "ProcedureMemory",
    "RetrievalHit",
    "RetrievalResult",
    "SessionContext",
    "TurnMemory",
]
