# retrieval 단계가 주고받는 hit, trace, session context 모델 모음.
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class SessionContext:
    mode: str | None = None
    user_goal: str | None = None
    current_topic: str | None = None
    open_entities: list[str] = field(default_factory=list)
    ocp_version: str | None = None
    selected_draft_ids: list[str] = field(default_factory=list)
    restrict_uploaded_sources: bool = True
    unresolved_question: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "SessionContext":
        if not payload:
            return cls()
        open_entities = payload.get("open_entities") or []
        if isinstance(open_entities, str):
            open_entities = [open_entities]
        selected_draft_ids = payload.get("selected_draft_ids") or []
        if isinstance(selected_draft_ids, str):
            selected_draft_ids = [selected_draft_ids]
        return cls(
            mode=payload.get("mode"),
            user_goal=payload.get("user_goal"),
            current_topic=payload.get("current_topic"),
            open_entities=list(open_entities),
            ocp_version=payload.get("ocp_version"),
            selected_draft_ids=[
                str(item).strip() for item in selected_draft_ids if str(item).strip()
            ],
            restrict_uploaded_sources=bool(payload.get("restrict_uploaded_sources", True)),
            unresolved_question=payload.get("unresolved_question"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
