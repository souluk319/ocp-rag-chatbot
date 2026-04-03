from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Citation:
    index: int
    chunk_id: str
    book_slug: str
    section: str
    anchor: str
    source_url: str
    viewer_path: str
    excerpt: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ContextBundle:
    prompt_context: str
    citations: list[Citation]

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_context": self.prompt_context,
            "citations": [citation.to_dict() for citation in self.citations],
        }


@dataclass(slots=True)
class AnswerResult:
    query: str
    mode: str
    answer: str
    rewritten_query: str
    citations: list[Citation]
    response_kind: str = "rag"
    cited_indices: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    retrieval_trace: dict[str, Any] = field(default_factory=dict)
    pipeline_trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "mode": self.mode,
            "answer": self.answer,
            "rewritten_query": self.rewritten_query,
            "response_kind": self.response_kind,
            "citations": [citation.to_dict() for citation in self.citations],
            "cited_indices": self.cited_indices,
            "warnings": self.warnings,
            "retrieval_trace": self.retrieval_trace,
            "pipeline_trace": self.pipeline_trace,
        }
