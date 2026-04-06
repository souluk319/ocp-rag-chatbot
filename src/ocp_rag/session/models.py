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
class CommandTemplateMemory:
    operation: str = ""
    format: str = "command"
    template: str = ""
    rendered: str = ""
    slots: dict[str, str] = field(default_factory=dict)
    references: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "CommandTemplateMemory":
        if not payload:
            return cls()
        slots = payload.get("slots") or {}
        if not isinstance(slots, dict):
            slots = {}
        references = payload.get("references") or []
        if isinstance(references, str):
            references = [references]
        return cls(
            operation=str(payload.get("operation") or ""),
            format=str(payload.get("format") or "command"),
            template=str(payload.get("template") or ""),
            rendered=str(payload.get("rendered") or ""),
            slots={str(key): str(value) for key, value in slots.items() if str(value).strip()},
            references=list(references),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CitationMemory:
    chunk_id: str = ""
    book_slug: str = ""
    section: str = ""
    anchor: str = ""
    source_url: str = ""
    viewer_path: str = ""
    excerpt: str = ""
    origin: str = "retrieved"

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "CitationMemory":
        if not payload:
            return cls()
        return cls(
            chunk_id=str(payload.get("chunk_id") or ""),
            book_slug=str(payload.get("book_slug") or ""),
            section=str(payload.get("section") or ""),
            anchor=str(payload.get("anchor") or ""),
            source_url=str(payload.get("source_url") or ""),
            viewer_path=str(payload.get("viewer_path") or ""),
            excerpt=str(payload.get("excerpt") or ""),
            origin=str(payload.get("origin") or "retrieved"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CitationGroupMemory:
    query: str = ""
    topic: str | None = None
    citations: list[CitationMemory] = field(default_factory=list)
    primary_index: int = 1

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "CitationGroupMemory":
        if not payload:
            return cls()
        citations = payload.get("citations") or []
        if isinstance(citations, dict):
            citations = [citations]
        primary_index = payload.get("primary_index")
        if not isinstance(primary_index, int) or primary_index < 1:
            primary_index = 1
        return cls(
            query=str(payload.get("query") or ""),
            topic=payload.get("topic"),
            citations=[
                item if isinstance(item, CitationMemory) else CitationMemory.from_dict(item)
                for item in citations
                if item
            ],
            primary_index=primary_index,
        )

    def citation_for_index(self, index: int) -> CitationMemory | None:
        if index < 1 or index > len(self.citations):
            return None
        return self.citations[index - 1]

    def primary_citation(self) -> CitationMemory | None:
        return self.citation_for_index(self.primary_index) or (self.citations[0] if self.citations else None)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProcedureMemory:
    goal: str = ""
    steps: list[str] = field(default_factory=list)
    active_step_index: int | None = None
    step_commands: list[str] = field(default_factory=list)
    step_command_templates: list[CommandTemplateMemory | None] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "ProcedureMemory":
        if not payload:
            return cls()
        steps = payload.get("steps") or []
        if isinstance(steps, str):
            steps = [steps]
        step_commands = payload.get("step_commands") or []
        if isinstance(step_commands, str):
            step_commands = [step_commands]
        step_command_templates = payload.get("step_command_templates") or []
        if isinstance(step_command_templates, dict):
            step_command_templates = [step_command_templates]
        references = payload.get("references") or []
        if isinstance(references, str):
            references = [references]
        active_step_index = payload.get("active_step_index")
        if not isinstance(active_step_index, int) or active_step_index < 0:
            active_step_index = None
        return cls(
            goal=str(payload.get("goal") or ""),
            steps=list(steps),
            active_step_index=active_step_index,
            step_commands=list(step_commands),
            step_command_templates=[
                item
                if isinstance(item, CommandTemplateMemory)
                else CommandTemplateMemory.from_dict(item)
                if item
                else None
                for item in step_command_templates
            ],
            references=list(references),
        )

    def active_step(self) -> str | None:
        if self.active_step_index is None:
            return None
        if self.active_step_index < 0 or self.active_step_index >= len(self.steps):
            return None
        return self.steps[self.active_step_index]

    def command_for(self, index: int) -> str | None:
        if index < 0 or index >= len(self.step_commands):
            return None
        command = self.step_commands[index].strip()
        return command or None

    def command_template_for(self, index: int) -> CommandTemplateMemory | None:
        if index < 0 or index >= len(self.step_command_templates):
            return None
        return self.step_command_templates[index]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BranchFocusSnapshot:
    branch_key: str = ""
    topic: str | None = None
    citation_group: CitationGroupMemory | None = None
    procedure_memory: ProcedureMemory | None = None
    recent_steps: list[str] = field(default_factory=list)
    recent_commands: list[str] = field(default_factory=list)
    recent_command_templates: list[CommandTemplateMemory] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "BranchFocusSnapshot":
        if not payload:
            return cls()
        citation_group = payload.get("citation_group")
        procedure_memory = payload.get("procedure_memory")
        recent_command_templates = payload.get("recent_command_templates") or []
        if isinstance(recent_command_templates, dict):
            recent_command_templates = [recent_command_templates]
        return cls(
            branch_key=str(payload.get("branch_key") or ""),
            topic=payload.get("topic"),
            citation_group=(
                citation_group
                if isinstance(citation_group, CitationGroupMemory)
                else CitationGroupMemory.from_dict(citation_group)
                if citation_group
                else None
            ),
            procedure_memory=(
                procedure_memory
                if isinstance(procedure_memory, ProcedureMemory)
                else ProcedureMemory.from_dict(procedure_memory)
                if procedure_memory
                else None
            ),
            recent_steps=list(payload.get("recent_steps") or []),
            recent_commands=list(payload.get("recent_commands") or []),
            recent_command_templates=[
                item
                if isinstance(item, CommandTemplateMemory)
                else CommandTemplateMemory.from_dict(item)
                for item in recent_command_templates
                if item
            ],
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
    recent_command_templates: list[CommandTemplateMemory] = field(default_factory=list)
    procedure_memory: ProcedureMemory | None = None
    active_citation_group: CitationGroupMemory | None = None
    citation_groups: list[CitationGroupMemory] = field(default_factory=list)
    branch_snapshots: list[BranchFocusSnapshot] = field(default_factory=list)

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
        recent_command_templates = payload.get("recent_command_templates") or []
        if isinstance(recent_command_templates, dict):
            recent_command_templates = [recent_command_templates]
        procedure_memory = payload.get("procedure_memory")
        active_citation_group = payload.get("active_citation_group")
        citation_groups = payload.get("citation_groups") or []
        if isinstance(citation_groups, dict):
            citation_groups = [citation_groups]
        branch_snapshots = payload.get("branch_snapshots") or []
        if isinstance(branch_snapshots, dict):
            branch_snapshots = [branch_snapshots]
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
            recent_command_templates=[
                item
                if isinstance(item, CommandTemplateMemory)
                else CommandTemplateMemory.from_dict(item)
                for item in recent_command_templates
            ],
            procedure_memory=(
                procedure_memory
                if isinstance(procedure_memory, ProcedureMemory)
                else ProcedureMemory.from_dict(procedure_memory)
                if procedure_memory
                else None
            ),
            active_citation_group=(
                active_citation_group
                if isinstance(active_citation_group, CitationGroupMemory)
                else CitationGroupMemory.from_dict(active_citation_group)
                if active_citation_group
                else None
            ),
            citation_groups=[
                item
                if isinstance(item, CitationGroupMemory)
                else CitationGroupMemory.from_dict(item)
                for item in citation_groups
                if item
            ],
            branch_snapshots=[
                item
                if isinstance(item, BranchFocusSnapshot)
                else BranchFocusSnapshot.from_dict(item)
                for item in branch_snapshots
                if item
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
