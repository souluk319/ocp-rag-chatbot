from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class TurnMemory:
    query: str = ""
    topic: str | None = None
    answer_focus: str | None = None
    entities: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "TurnMemory":
        if not payload:
            return cls()
        entities = payload.get("entities") or []
        if isinstance(entities, str):
            entities = [entities]
        references = payload.get("references") or []
        if isinstance(references, str):
            references = [references]
        return cls(
            query=str(payload.get("query") or ""),
            topic=payload.get("topic"),
            answer_focus=payload.get("answer_focus"),
            entities=list(entities),
            references=list(references),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SessionContext:
    mode: str | None = None
    user_goal: str | None = None
    current_topic: str | None = None
    open_entities: list[str] = field(default_factory=list)
    ocp_version: str | None = None
    unresolved_question: str | None = None
    recent_turns: list[TurnMemory] = field(default_factory=list)
    topic_journal: list[str] = field(default_factory=list)
    reference_hints: list[str] = field(default_factory=list)
    recent_steps: list[str] = field(default_factory=list)
    recent_commands: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "SessionContext":
        if not payload:
            return cls()
        open_entities = payload.get("open_entities") or []
        if isinstance(open_entities, str):
            open_entities = [open_entities]
        recent_turns = payload.get("recent_turns") or []
        if isinstance(recent_turns, dict):
            recent_turns = [recent_turns]
        topic_journal = payload.get("topic_journal") or []
        reference_hints = payload.get("reference_hints") or []
        recent_steps = payload.get("recent_steps") or []
        recent_commands = payload.get("recent_commands") or []
        return cls(
            mode=payload.get("mode"),
            user_goal=payload.get("user_goal"),
            current_topic=payload.get("current_topic"),
            open_entities=list(open_entities),
            ocp_version=payload.get("ocp_version"),
            unresolved_question=payload.get("unresolved_question"),
            recent_turns=[
                item if isinstance(item, TurnMemory) else TurnMemory.from_dict(item)
                for item in recent_turns
            ],
            topic_journal=list(topic_journal),
            reference_hints=list(reference_hints),
            recent_steps=list(recent_steps),
            recent_commands=list(recent_commands),
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
