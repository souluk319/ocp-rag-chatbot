from __future__ import annotations

import html
import json
import re
import threading
import uuid
import webbrowser
from dataclasses import dataclass, field, replace
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ocp_rag.ingest.settings import HIGH_VALUE_SLUGS, load_settings
from ocp_rag.ingest.validation import read_jsonl
from ocp_rag.retrieval.command_memory import (
    build_command_template_follow_up_answer,
    build_command_template_memory,
)
from ocp_rag.retrieval.models import (
    CitationGroupMemory,
    CitationMemory,
    CommandTemplateMemory,
    ProcedureMemory,
    SessionContext,
    TurnMemory,
)
from ocp_rag.retrieval.query import (
    ARCHITECTURE_RE,
    ETCD_RE,
    MCO_RE,
    OCP_RE,
    OPENSHIFT_RE,
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_follow_up_reference,
    has_logging_ambiguity,
    has_doc_locator_intent,
    has_openshift_kubernetes_compare_intent,
    has_rbac_intent,
    has_update_doc_locator_ambiguity,
    is_generic_intro_query,
    STEP_REFERENCE_RE,
)
from ocp_rag.answering import Part3Answerer
from ocp_rag.answering.models import AnswerResult, Citation


STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML_PATH = STATIC_DIR / "index.html"
NORMALIZED_BLOCK_RE = re.compile(r"(\[CODE\].*?\[/CODE\]|\[TABLE\].*?\[/TABLE\])", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
ANSWER_PREFIX_RE = re.compile(r"^\s*답변:\s*")
CITATION_MARK_RE = re.compile(r"\[\d+\]")
STEP_LINE_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$", re.MULTILINE)
STEP_BLOCK_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)(?=^\s*\d+\.\s+|\Z)", re.MULTILINE | re.DOTALL)
CODE_BLOCK_RE = re.compile(r"```(?:[\w.+-]*)\n(.*?)```", re.DOTALL)
DOC_HEADING_RE = re.compile(r"^\d+(?:\.\d+)+(?:\.\d+)*\.\s*")
PROCEDURE_NEXT_STEP_RE = re.compile(r"(다음(?:\s*단계)?|그 다음|이어서|다음으로|계속(?:해서)?)", re.IGNORECASE)
PROCEDURE_CURRENT_STEP_RE = re.compile(
    r"(이 단계|현재 단계|여기서|여기부터|방금 단계|해당 단계)",
    re.IGNORECASE,
)
PROCEDURE_DONE_UNTIL_RE = re.compile(
    r"(?<!\d)(1[0-2]|[1-9])번(?:\s*단계)?(?:까지|까진|까지는).*(했|끝|완료)",
    re.IGNORECASE,
)
PROCEDURE_GOAL_NOISE_RE = re.compile(
    r"(단계별(?:로)?|순서대로|차근차근|하나씩|알려줘|알려 줘|설명해줘|설명해 줘|"
    r"보여줘|보여 줘|정리해줘|정리해 줘|다시|예시로|예시만|기준으로|만 더 자세히)",
    re.IGNORECASE,
)
ROLE_BINDING_COMMAND_RE = re.compile(
    r"^oc\s+adm\s+policy\s+add-role-to-(user|group)\s+(\S+)\s+(\S+)(?:\s+-n\s+(\S+))?\s*$",
    re.IGNORECASE,
)
NAMESPACE_FLAG_RE = re.compile(r"(?:^|\s)(?:-n|--namespace)\s+(\S+)")
INLINE_NAMESPACE_FLAG_RE = re.compile(r"--namespace=(\S+)")
SERVICEACCOUNT_SUBJECT_RE = re.compile(
    r"^system:serviceaccount:([A-Za-z0-9._-]+):([A-Za-z0-9._-]+)$",
    re.IGNORECASE,
)
COMMAND_MUTATION_HINT_RE = re.compile(
    r"(대신|바꿔|변경|수정|기준|serviceaccount|service account|서비스어카운트|\bsa\b|user|사용자|group|그룹|namespace|네임스페이스)",
    re.IGNORECASE,
)
COMMAND_REPLACE_RE = re.compile(
    r"([A-Za-z0-9:._-]+)\s+대신\s+([A-Za-z0-9:._-]+|serviceaccount|service account|서비스어카운트|sa|user|사용자|group|그룹)",
    re.IGNORECASE,
)
COMMAND_NAMESPACE_RE = re.compile(
    r"(?:namespace|네임스페이스)(?:는|를|만)?\s*([A-Za-z0-9:._-]+)\s*(?:로|기준)|([A-Za-z0-9:._-]+)\s*(?:namespace|네임스페이스)\s*기준",
    re.IGNORECASE,
)
COMMAND_USER_RE = re.compile(r"(?:user|사용자)(?:는|를|만)?\s*([A-Za-z0-9:._-]+)\s*로", re.IGNORECASE)
COMMAND_GROUP_RE = re.compile(r"(?:group|그룹)(?:는|를|만)?\s*([A-Za-z0-9:._-]+)\s*로", re.IGNORECASE)
COMMAND_SERVICEACCOUNT_NAME_RE = re.compile(
    r"(?:serviceaccount|service account|서비스어카운트|\bsa\b)(?:는|를|만)?\s*([A-Za-z0-9:._-]+)?\s*(?:로|기준)?",
    re.IGNORECASE,
)


@dataclass(slots=True)
class Turn:
    query: str
    mode: str
    answer: str


@dataclass(slots=True)
class ChatSession:
    session_id: str
    mode: str = "ops"
    context: SessionContext = field(
        default_factory=lambda: SessionContext(mode="ops", ocp_version="4.20")
    )
    history: list[Turn] = field(default_factory=list)

    @property
    def last_query(self) -> str:
        if not self.history:
            return ""
        return self.history[-1].query


class SessionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, ChatSession] = {}

    def get(self, session_id: str) -> ChatSession:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = ChatSession(session_id=session_id)
                self._sessions[session_id] = session
            return session

    def reset(self, session_id: str) -> ChatSession:
        with self._lock:
            session = ChatSession(session_id=session_id)
            self._sessions[session_id] = session
            return session

    def update(self, session: ChatSession) -> None:
        with self._lock:
            self._sessions[session.session_id] = session


def _citation_href(citation: Citation) -> str:
    viewer_path = (citation.viewer_path or "").strip()
    if viewer_path:
        return viewer_path
    if citation.anchor:
        return f"{citation.source_url}#{citation.anchor}"
    return citation.source_url


def _merge_memory_items(
    existing: list[str],
    additions: list[str],
    *,
    limit: int = 6,
) -> list[str]:
    merged: list[str] = []
    for raw in [*existing, *additions]:
        cleaned = " ".join((raw or "").split()).strip()
        if not cleaned:
            continue
        if cleaned in merged:
            merged.remove(cleaned)
        merged.append(cleaned[:160])
    return merged[-limit:]


def _compact_memory_text(text: str, *, limit: int = 160) -> str:
    cleaned = CODE_BLOCK_RE.sub(" ", text or "")
    cleaned = CITATION_MARK_RE.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -:|")
    return cleaned[:limit]


def _extract_answer_focus(answer_text: str) -> str:
    body = ANSWER_PREFIX_RE.sub("", answer_text or "", count=1).strip()
    if not body:
        return ""
    for part in re.split(r"(?:\n\s*\n+|[.!?]\s+)", body):
        cleaned = _compact_memory_text(part, limit=140)
        if cleaned:
            return cleaned
    return _compact_memory_text(body, limit=140)


def _build_turn_memory(
    *,
    query: str,
    result: AnswerResult,
    topic: str | None,
    entities: list[str],
    references: list[str] | None = None,
) -> TurnMemory:
    turn_references = list(references or [])
    if not turn_references:
        for citation in result.citations[:2]:
            label = citation.section or citation.anchor or citation.book_slug
            reference = _compact_memory_text(f"{citation.book_slug} · {label}", limit=120)
            if reference and reference not in turn_references:
                turn_references.append(reference)
    return TurnMemory(
        query=_compact_memory_text(query, limit=120),
        topic=_compact_memory_text(topic or "", limit=120) or None,
        answer_focus=_extract_answer_focus(result.answer) or None,
        entities=[_compact_memory_text(entity, limit=80) for entity in entities[:4] if entity],
        references=turn_references[:3],
    )


def _merge_recent_turns(
    existing: list[TurnMemory],
    addition: TurnMemory,
    *,
    limit: int = 12,
) -> list[TurnMemory]:
    merged = [
        turn
        for turn in existing
        if turn.query or turn.topic or turn.answer_focus or turn.references or turn.entities
    ]
    if addition.query or addition.topic or addition.answer_focus or addition.references or addition.entities:
        if merged and merged[-1].query == addition.query and merged[-1].topic == addition.topic:
            merged[-1] = addition
        else:
            merged.append(addition)
    return merged[-limit:]


def _extract_step_entries(answer_text: str) -> list[tuple[str, str | None]]:
    entries: list[tuple[str, str | None]] = []
    body = re.sub(r"^\s*답변:\s*", "", answer_text or "", count=1).strip()
    for match in STEP_BLOCK_RE.finditer(body):
        block = match.group(0)
        raw_title = match.group(2).strip().splitlines()[0]
        step_text = re.sub(r"\*\*([^*]+)\*\*", r"\1", raw_title)
        step_text = step_text.strip(" -*")
        step_text = re.sub(r"\s+", " ", step_text).rstrip(".:")
        if not step_text:
            continue
        command: str | None = None
        code_match = CODE_BLOCK_RE.search(block)
        if code_match:
            command = next((line.strip() for line in code_match.group(1).splitlines() if line.strip()), None)
        entries.append((step_text[:140], (command or "")[:160] or None))
        if len(entries) >= 5:
            break
    return entries


def _extract_answer_steps(answer_text: str) -> list[str]:
    steps: list[str] = []
    for step_text, _ in _extract_step_entries(answer_text):
        if step_text in steps:
            continue
        steps.append(step_text)
    return steps


def _extract_step_commands(answer_text: str) -> list[str]:
    commands: list[str] = []
    for _, command in _extract_step_entries(answer_text):
        commands.append(command or "")
    return commands


def _extract_answer_commands(answer_text: str) -> list[str]:
    commands: list[str] = []
    for match in CODE_BLOCK_RE.finditer(answer_text or ""):
        block = match.group(1).strip()
        if not block:
            continue
        first_line = next((line.strip() for line in block.splitlines() if line.strip()), "")
        if not first_line or first_line in commands:
            continue
        commands.append(first_line[:160])
        if len(commands) >= 3:
            break
    return commands


def _normalize_step_commands(step_commands: list[str], step_count: int) -> list[str]:
    normalized = [""] * step_count
    for index, command in enumerate(step_commands[:step_count]):
        normalized[index] = command.strip()
    return normalized


def _extract_namespace_from_command(command: str) -> str | None:
    match = NAMESPACE_FLAG_RE.search(command)
    if match:
        return match.group(1).strip()
    inline_match = INLINE_NAMESPACE_FLAG_RE.search(command)
    if inline_match:
        return inline_match.group(1).strip()
    return None


def _render_command_template(template: CommandTemplateMemory) -> str:
    slots = dict(template.slots)
    if template.operation == "oc_adm_policy_subject_binding":
        role = (slots.get("role") or "<role>").strip()
        namespace = (slots.get("namespace") or "").strip()
        subject_kind = (slots.get("subject_kind") or "user").strip().lower()
        subject_name = (slots.get("subject_name") or "").strip()
        if subject_kind == "serviceaccount":
            subject_namespace = (
                slots.get("subject_namespace")
                or namespace
                or "<namespace>"
            ).strip()
            subject_name = subject_name or "<serviceaccount>"
            subject_token = f"system:serviceaccount:{subject_namespace}:{subject_name}"
            verb = "add-role-to-user"
        else:
            subject_token = subject_name or "<subject>"
            verb = "add-role-to-group" if subject_kind == "group" else "add-role-to-user"
        parts = ["oc", "adm", "policy", verb, role, subject_token]
        if namespace:
            parts.extend(["-n", namespace])
        return " ".join(parts)

    if template.operation == "namespace_scoped_command":
        namespace = (slots.get("namespace") or "").strip()
        rendered = (template.rendered or template.template).strip()
        if not namespace or not rendered:
            return rendered
        replaced = re.sub(r"((?:^|\s)(?:-n|--namespace)\s+)\S+", rf"\1{namespace}", rendered, count=1)
        if replaced != rendered:
            return " ".join(replaced.split())
        replaced = re.sub(r"(--namespace=)\S+", rf"\1{namespace}", rendered, count=1)
        return " ".join(replaced.split())

    return (template.rendered or template.template).strip()


def _build_command_template(
    command: str,
    *,
    references: list[str] | None = None,
) -> CommandTemplateMemory | None:
    return build_command_template_memory(command, references=references)


def _normalize_step_command_templates(
    step_commands: list[str],
    step_count: int,
    *,
    references: list[str],
) -> list[CommandTemplateMemory | None]:
    normalized: list[CommandTemplateMemory | None] = [None] * step_count
    for index, command in enumerate(step_commands[:step_count]):
        normalized[index] = _build_command_template(command, references=references)
    return normalized


def _command_template_subject_display(template: CommandTemplateMemory) -> str:
    slots = template.slots
    subject_kind = (slots.get("subject_kind") or "").strip().lower()
    subject_name = (slots.get("subject_name") or "").strip()
    if subject_kind == "serviceaccount":
        subject_namespace = (
            slots.get("subject_namespace")
            or slots.get("namespace")
            or "<namespace>"
        ).strip()
        return f"system:serviceaccount:{subject_namespace}:{subject_name or '<serviceaccount>'}"
    return subject_name or "<subject>"


def _select_command_template(query: str, context: SessionContext | None) -> CommandTemplateMemory | None:
    if context is None:
        return None

    procedure = context.procedure_memory
    if procedure is not None and procedure.step_command_templates:
        focus_index = _resolve_procedure_step_index(query, procedure)
        if focus_index is not None:
            candidate = procedure.command_template_for(focus_index)
            if candidate is not None:
                return candidate
        if procedure.active_step_index is not None:
            candidate = procedure.command_template_for(procedure.active_step_index)
            if candidate is not None:
                return candidate

    for template in context.recent_command_templates:
        if template.rendered or template.template:
            return template

    for command in context.recent_commands:
        candidate = _build_command_template(command, references=context.reference_hints)
        if candidate is not None:
            return candidate
    return None


def _parse_command_mutation_request(
    query: str,
    template: CommandTemplateMemory,
) -> dict[str, str] | None:
    normalized = query or ""
    lowered = normalized.lower()
    if not COMMAND_MUTATION_HINT_RE.search(normalized):
        return None

    request: dict[str, str] = {}
    namespace_match = COMMAND_NAMESPACE_RE.search(normalized)
    if namespace_match:
        request["namespace"] = (namespace_match.group(1) or namespace_match.group(2) or "").strip()

    replace_match = COMMAND_REPLACE_RE.search(normalized)
    if replace_match:
        before = replace_match.group(1).strip()
        after = replace_match.group(2).strip()
        after_lower = after.lower()
        current_namespace = (template.slots.get("namespace") or "").strip()
        current_subject_name = (template.slots.get("subject_name") or "").strip()
        current_subject_token = _command_template_subject_display(template)
        current_role = (template.slots.get("role") or "").strip()
        if before == current_namespace:
            request["namespace"] = after
        elif before in {current_subject_name, current_subject_token}:
            if after_lower in {"serviceaccount", "service account", "서비스어카운트", "sa"}:
                request["subject_kind"] = "serviceaccount"
            elif after_lower in {"user", "사용자"}:
                request["subject_kind"] = "user"
            elif after_lower in {"group", "그룹"}:
                request["subject_kind"] = "group"
            else:
                request["subject_name"] = after
        elif before == current_role:
            request["role"] = after

    user_match = COMMAND_USER_RE.search(normalized)
    if user_match:
        request["subject_kind"] = "user"
        request["subject_name"] = user_match.group(1).strip()

    group_match = COMMAND_GROUP_RE.search(normalized)
    if group_match:
        request["subject_kind"] = "group"
        request["subject_name"] = group_match.group(1).strip()

    serviceaccount_match = COMMAND_SERVICEACCOUNT_NAME_RE.search(normalized)
    if "serviceaccount" in lowered or "service account" in lowered or "서비스어카운트" in normalized or re.search(r"\bsa\b", lowered):
        request["subject_kind"] = "serviceaccount"
        if serviceaccount_match and serviceaccount_match.group(1):
            request["subject_name"] = serviceaccount_match.group(1).strip()

    if not request:
        return None

    subject_kind = request.get("subject_kind") or template.slots.get("subject_kind") or ""
    if subject_kind == "serviceaccount":
        request["subject_kind"] = "serviceaccount"
        request["subject_name"] = request.get("subject_name") or template.slots.get("subject_name") or "<serviceaccount>"
        request["subject_namespace"] = (
            request.get("subject_namespace")
            or request.get("namespace")
            or template.slots.get("subject_namespace")
            or template.slots.get("namespace")
            or "<namespace>"
        )
    elif "subject_kind" in request and "subject_name" not in request:
        request["subject_name"] = template.slots.get("subject_name") or "<subject>"

    return request


def _apply_command_mutation(
    template: CommandTemplateMemory,
    request: dict[str, str],
) -> CommandTemplateMemory:
    updated = CommandTemplateMemory.from_dict(template.to_dict())
    updated.slots = dict(updated.slots)
    for key in ("namespace", "role", "subject_name", "subject_kind", "subject_namespace"):
        if request.get(key):
            updated.slots[key] = request[key]
    updated.rendered = _render_command_template(updated)
    return updated


def _summarize_command_template_diffs(
    original: CommandTemplateMemory,
    updated: CommandTemplateMemory,
) -> list[str]:
    diffs: list[str] = []
    original_namespace = (original.slots.get("namespace") or "").strip()
    updated_namespace = (updated.slots.get("namespace") or "").strip()
    if original_namespace != updated_namespace and updated_namespace:
        diffs.append(f"namespace {original_namespace or '-'} -> {updated_namespace}")

    original_subject = _command_template_subject_display(original)
    updated_subject = _command_template_subject_display(updated)
    if original_subject != updated_subject:
        diffs.append(f"subject {original_subject} -> {updated_subject}")

    original_role = (original.slots.get("role") or "").strip()
    updated_role = (updated.slots.get("role") or "").strip()
    if original_role != updated_role and updated_role:
        diffs.append(f"role {original_role or '-'} -> {updated_role}")
    return diffs


def _infer_procedure_goal(
    *,
    query: str,
    topic: str | None,
    previous: ProcedureMemory | None,
) -> str:
    if previous and previous.goal and (has_follow_up_reference(query) or not _infer_explicit_topic(query)):
        return previous.goal

    cleaned_query = PROCEDURE_GOAL_NOISE_RE.sub(" ", query or "")
    cleaned_goal = _compact_memory_text(cleaned_query, limit=120)
    if cleaned_goal:
        return cleaned_goal
    if topic:
        return _compact_memory_text(f"{topic} 절차", limit=120)
    if previous and previous.goal:
        return previous.goal
    return ""


def _resolve_procedure_step_index(query: str, procedure: ProcedureMemory | None) -> int | None:
    if procedure is None or not procedure.steps:
        return None

    normalized = query or ""
    match = STEP_REFERENCE_RE.search(normalized)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(procedure.steps):
            return index

    completed_match = PROCEDURE_DONE_UNTIL_RE.search(normalized)
    if completed_match:
        index = int(completed_match.group(1))
        return min(index, len(procedure.steps) - 1)

    if PROCEDURE_CURRENT_STEP_RE.search(normalized):
        return procedure.active_step_index

    if PROCEDURE_NEXT_STEP_RE.search(normalized):
        if procedure.active_step_index is None:
            return 0 if procedure.steps else None
        return min(procedure.active_step_index + 1, len(procedure.steps) - 1)

    return None


def _derive_procedure_memory(
    previous: ProcedureMemory | None,
    *,
    query: str,
    topic: str | None,
    reference_hints: list[str],
    explicit_topic: str | None,
    prior_topic: str | None,
    answer_text: str,
) -> ProcedureMemory | None:
    extracted_steps = _extract_answer_steps(answer_text)
    extracted_step_commands = _normalize_step_commands(
        _extract_step_commands(answer_text),
        len(extracted_steps),
    )
    extracted_step_command_templates = _normalize_step_command_templates(
        extracted_step_commands,
        len(extracted_steps),
        references=reference_hints,
    )

    if extracted_steps:
        seeded_previous = previous if previous and previous.steps else None
        seeded_procedure = ProcedureMemory(
            goal=_infer_procedure_goal(query=query, topic=topic, previous=seeded_previous),
            steps=list(extracted_steps),
            active_step_index=0,
            step_commands=list(extracted_step_commands),
            step_command_templates=list(extracted_step_command_templates),
            references=_merge_memory_items(
                seeded_previous.references if seeded_previous else [],
                reference_hints,
                limit=4,
            ),
        )
        focused_index = _resolve_procedure_step_index(query, seeded_procedure)
        if focused_index is not None:
            seeded_procedure.active_step_index = focused_index
        return seeded_procedure

    if explicit_topic and prior_topic and explicit_topic != prior_topic:
        return None

    if previous is None or not previous.steps:
        return None

    updated = ProcedureMemory.from_dict(previous.to_dict())
    updated.goal = _infer_procedure_goal(query=query, topic=topic, previous=updated)
    updated.references = _merge_memory_items(updated.references, reference_hints, limit=4)
    focused_index = _resolve_procedure_step_index(query, updated)
    if focused_index is not None:
        updated.active_step_index = focused_index

    extracted_commands = _extract_answer_commands(answer_text)
    if extracted_commands and updated.steps:
        step_commands = _normalize_step_commands(updated.step_commands, len(updated.steps))
        step_command_templates = list(updated.step_command_templates[: len(updated.steps)])
        if len(step_command_templates) < len(updated.steps):
            step_command_templates.extend([None] * (len(updated.steps) - len(step_command_templates)))
        focus_index = updated.active_step_index if updated.active_step_index is not None else 0
        if 0 <= focus_index < len(step_commands):
            step_commands[focus_index] = extracted_commands[0]
            step_command_templates[focus_index] = _build_command_template(
                extracted_commands[0],
                references=updated.references,
            )
        updated.step_commands = step_commands
        updated.step_command_templates = step_command_templates

    return updated


def _build_reference_hints(result: AnswerResult, *, topic: str | None) -> list[str]:
    hints: list[str] = []
    if topic:
        hints.append(topic)
    for citation in result.citations[:3]:
        label = citation.section or citation.anchor or citation.book_slug
        hints.append(f"{citation.book_slug} · {label}")
    return hints[:6]


def _build_citation_group_memory(
    *,
    query: str,
    topic: str | None,
    result: AnswerResult,
) -> CitationGroupMemory | None:
    if not result.citations:
        return None
    return CitationGroupMemory(
        query=_compact_memory_text(query, limit=140),
        topic=_compact_memory_text(topic or "", limit=120) or None,
        citations=[
            CitationMemory(
                chunk_id=citation.chunk_id,
                book_slug=citation.book_slug,
                section=citation.section,
                anchor=citation.anchor,
                source_url=citation.source_url,
                viewer_path=citation.viewer_path,
                excerpt=_compact_memory_text(citation.excerpt, limit=320),
                origin=citation.origin or "retrieved",
            )
            for citation in result.citations[:4]
        ],
        primary_index=1,
    )


def _citation_group_identity(group: CitationGroupMemory) -> str:
    primary = group.primary_citation()
    if group.topic:
        return f"topic::{group.topic.lower()}"
    if primary is not None:
        viewer = (primary.viewer_path or primary.source_url).strip().lower()
        if viewer:
            return f"viewer::{viewer}"
        if primary.book_slug:
            return f"book::{primary.book_slug.lower()}"
    return f"query::{(group.query or '').strip().lower()}"


def _merge_citation_groups(
    existing: list[CitationGroupMemory],
    addition: CitationGroupMemory,
    *,
    limit: int = 6,
) -> list[CitationGroupMemory]:
    identity = _citation_group_identity(addition)
    merged: list[CitationGroupMemory] = [
        group
        for group in existing
        if group.citations and _citation_group_identity(group) != identity
    ]
    merged.append(addition)
    return merged[-limit:]


def _resolve_procedure_follow_up_index(
    query: str,
    context: SessionContext | None,
) -> int | None:
    if context is None or context.procedure_memory is None or not context.procedure_memory.steps:
        return None

    procedure = context.procedure_memory
    normalized = query or ""
    match = STEP_REFERENCE_RE.search(normalized)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(procedure.steps):
            return index

    if PROCEDURE_CURRENT_STEP_RE.search(normalized):
        return procedure.active_step_index

    if PROCEDURE_NEXT_STEP_RE.search(normalized):
        if procedure.active_step_index is None:
            return 0
        return min(procedure.active_step_index + 1, len(procedure.steps) - 1)

    return None


def _override_answer_with_procedure_follow_up(
    *,
    query: str,
    context: SessionContext | None,
    result: AnswerResult,
) -> AnswerResult:
    focus_index = _resolve_procedure_follow_up_index(query, context)
    if focus_index is None or context is None or context.procedure_memory is None:
        return result

    procedure = context.procedure_memory
    if focus_index < 0 or focus_index >= len(procedure.steps):
        return result

    step = procedure.steps[focus_index]
    command = procedure.command_for(focus_index)
    citation_mark = " [1]" if result.citations else ""
    lines = [f"답변: {focus_index + 1}번 단계는 {step}입니다.{citation_mark}"]
    if command:
        lines.extend(["", "```bash", command, "```"])

    next_index = focus_index + 1
    lowered = (query or "").lower()
    if (
        next_index < len(procedure.steps)
        and ("자세히" in (query or "") or "detail" in lowered or "explain" in lowered)
    ):
        lines.extend(["", f"다음 단계: {next_index + 1}. {procedure.steps[next_index]}"])

    return replace(result, answer="\n".join(lines))


def _override_answer_with_command_template_follow_up(
    *,
    query: str,
    context: SessionContext | None,
    result: AnswerResult,
) -> AnswerResult:
    template = _select_command_template(query, context)
    if template is None:
        return result

    request = _parse_command_mutation_request(query, template)
    if request is None:
        return result

    updated = _apply_command_mutation(template, request)
    if updated.rendered == template.rendered:
        return result

    citation_mark = " [1]" if result.citations else ""
    lines = [f"답변: 이전 명령에서 요청한 값만 바꿔 다시 적었습니다{citation_mark}."]
    diffs = _summarize_command_template_diffs(template, updated)
    if diffs:
        lines.extend(["", "변경: " + " / ".join(diffs)])
    fence = "yaml" if updated.format == "yaml" else "bash"
    lines.extend(["", f"```{fence}", updated.rendered, "```"])
    return replace(result, answer="\n".join(lines))


def _viewer_path_to_local_html(root_dir: Path, viewer_path: str) -> Path | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None
    book_slug, _ = parsed
    settings = load_settings(root_dir)
    candidate = settings.raw_html_dir / f"{book_slug}.html"
    if not candidate.exists():
        return None
    return candidate


def _parse_viewer_path(viewer_path: str) -> tuple[str, str] | None:
    parsed = urlparse((viewer_path or "").strip())
    request_path = parsed.path.strip()
    prefix = "/docs/ocp/4.20/ko/"
    if not request_path.startswith(prefix):
        return None
    remainder = request_path[len(prefix) :]
    parts = [part for part in remainder.split("/") if part]
    if len(parts) != 2 or parts[1] != "index.html":
        return None
    return parts[0], parsed.fragment.strip()


def _render_inline_html(text: str) -> str:
    fragments: list[str] = []
    last_index = 0
    for match in INLINE_CODE_RE.finditer(text):
        if match.start() > last_index:
            fragments.append(html.escape(text[last_index:match.start()]))
        fragments.append(f"<code>{html.escape(match.group(1))}</code>")
        last_index = match.end()
    if last_index < len(text):
        fragments.append(html.escape(text[last_index:]))
    return "".join(fragments)


def _looks_like_subheading(text: str) -> bool:
    stripped = text.strip()
    if not stripped or len(stripped) > 36:
        return False
    if re.search(r"(?:니다|합니다|하십시오|하세요|[\.\?\!])", stripped):
        return False
    return True


def _render_code_block_html(code_text: str, *, language: str = "shell") -> str:
    copy_payload = html.escape(json.dumps(code_text), quote=True)
    return """
    <section class="code-block">
      <div class="code-header">
        <span class="code-label">{language}</span>
        <button type="button" class="copy-button" data-copy="{copy_payload}" onclick="copyViewerCode(this)">복사</button>
      </div>
      <pre><code>{code}</code></pre>
    </section>
    """.format(
        language=html.escape(language),
        copy_payload=copy_payload,
        code=html.escape(code_text),
    ).strip()


def _render_table_block_html(table_text: str) -> str:
    rows = [
        [cell.strip() for cell in row.split(" | ")]
        for row in table_text.splitlines()
        if row.strip()
    ]
    if not rows:
        return ""

    body_rows: list[str] = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return """
    <div class="table-wrap">
      <table>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
    """.format(rows="".join(body_rows)).strip()


def _render_normalized_section_html(text: str) -> str:
    blocks: list[str] = []
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    for part in NORMALIZED_BLOCK_RE.split(normalized):
        if not part:
            continue
        stripped = part.strip()
        if not stripped:
            continue
        if stripped.startswith("[CODE]") and stripped.endswith("[/CODE]"):
            code_text = stripped[len("[CODE]") : -len("[/CODE]")].strip("\n")
            blocks.append(_render_code_block_html(code_text))
            continue
        if stripped.startswith("[TABLE]") and stripped.endswith("[/TABLE]"):
            table_text = stripped[len("[TABLE]") : -len("[/TABLE]")].strip("\n")
            blocks.append(_render_table_block_html(table_text))
            continue
        for paragraph in re.split(r"\n\s*\n+", stripped):
            cleaned = re.sub(r"\s*\n\s*", " ", paragraph).strip()
            if not cleaned:
                continue
            if _looks_like_subheading(cleaned):
                blocks.append(f"<h3>{html.escape(cleaned)}</h3>")
            else:
                blocks.append(f"<p>{_render_inline_html(cleaned)}</p>")
    return "\n".join(blocks)


@lru_cache(maxsize=8)
def _load_normalized_sections(
    normalized_docs_path: str,
    mtime_ns: int,
) -> dict[str, list[dict[str, Any]]]:
    del mtime_ns
    sections_by_book: dict[str, list[dict[str, Any]]] = {}
    for row in read_jsonl(Path(normalized_docs_path)):
        sections_by_book.setdefault(str(row.get("book_slug", "")), []).append(row)
    return sections_by_book


@lru_cache(maxsize=4)
def _load_library_index(
    normalized_docs_path: str,
    mtime_ns: int,
) -> list[dict[str, Any]]:
    del mtime_ns
    by_book: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(Path(normalized_docs_path)):
        book_slug = str(row.get("book_slug") or "").strip()
        if not book_slug:
            continue
        book_title = str(row.get("book_title") or book_slug).strip() or book_slug
        heading = str(row.get("heading") or "").strip()
        viewer_path = str(row.get("viewer_path") or "").strip()
        source_url = str(row.get("source_url") or "").strip()
        entry = by_book.setdefault(
            book_slug,
            {
                "book_slug": book_slug,
                "book_title": book_title,
                "section_count": 0,
                "source_url": source_url,
                "viewer_path": viewer_path.split("#", 1)[0] if viewer_path else "",
                "sample_sections": [],
                "high_value": book_slug in HIGH_VALUE_SLUGS,
            },
        )
        entry["section_count"] += 1
        if not entry["source_url"] and source_url:
            entry["source_url"] = source_url
        if not entry["viewer_path"] and viewer_path:
            entry["viewer_path"] = viewer_path.split("#", 1)[0]
        if heading and heading not in entry["sample_sections"] and len(entry["sample_sections"]) < 3:
            entry["sample_sections"].append(heading)
    return sorted(
        by_book.values(),
        key=lambda item: (
            0 if item["high_value"] else 1,
            -int(item["section_count"]),
            str(item["book_title"]).lower(),
        ),
    )


def _build_library_payload(root_dir: Path) -> dict[str, Any]:
    settings = load_settings(root_dir)
    normalized_docs_path = settings.normalized_docs_path
    if not normalized_docs_path.exists():
        return {
            "available": False,
            "items": [],
            "total_books": 0,
            "total_sections": 0,
        }

    items = _load_library_index(
        str(normalized_docs_path),
        normalized_docs_path.stat().st_mtime_ns,
    )
    return {
        "available": True,
        "items": items,
        "total_books": len(items),
        "total_sections": sum(int(item["section_count"]) for item in items),
    }


def _internal_viewer_html(root_dir: Path, viewer_path: str) -> str | None:
    parsed = _parse_viewer_path(viewer_path)
    if parsed is None:
        return None

    book_slug, target_anchor = parsed
    settings = load_settings(root_dir)
    normalized_docs_path = settings.normalized_docs_path
    if not normalized_docs_path.exists():
        return None

    sections_by_book = _load_normalized_sections(
        str(normalized_docs_path),
        normalized_docs_path.stat().st_mtime_ns,
    )
    sections = sections_by_book.get(book_slug) or []
    if not sections:
        return None

    first_row = sections[0]
    book_title = str(first_row.get("book_title") or book_slug)
    source_url = str(first_row.get("source_url") or "")
    cards: list[str] = []

    for row in sections:
        anchor = str(row.get("anchor") or "")
        heading = str(row.get("heading") or "")
        section_path = [str(item) for item in (row.get("section_path") or []) if str(item).strip()]
        breadcrumb = " > ".join(section_path) if section_path else heading
        section_text = str(row.get("text") or "").strip()
        is_target = bool(target_anchor) and anchor == target_anchor
        cards.append(
            """
            <section id="{anchor}" class="section-card{target_class}">
              <div class="section-meta">{breadcrumb}</div>
              <h2>{heading}</h2>
              <div class="section-body">{text}</div>
            </section>
            """.format(
                anchor=html.escape(anchor, quote=True),
                target_class=" is-target" if is_target else "",
                breadcrumb=html.escape(breadcrumb),
                heading=html.escape(heading),
                text=_render_normalized_section_html(section_text),
            ).strip()
        )

    return """
    <!DOCTYPE html>
    <html lang="ko">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{title} - OCP 출처 뷰어</title>
        <style>
          :root {{
            color-scheme: light;
            --bg: #f5f1e8;
            --panel: #fffdf8;
            --line: #d8ccb8;
            --ink: #1f1c18;
            --muted: #675f54;
            --accent: #8a2d1c;
            --accent-soft: #f7e1da;
          }}
          * {{
            box-sizing: border-box;
          }}
          body {{
            margin: 0;
            background:
              radial-gradient(circle at top right, rgba(214, 123, 92, 0.16), transparent 24rem),
              linear-gradient(180deg, #f7f0e6 0%, var(--bg) 100%);
            color: var(--ink);
            font-family: "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
          }}
          main {{
            max-width: 980px;
            margin: 0 auto;
            padding: 32px 20px 48px;
          }}
          .hero {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(75, 48, 26, 0.06);
          }}
          .eyebrow {{
            color: var(--accent);
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }}
          h1 {{
            margin: 10px 0 8px;
            font-size: clamp(1.8rem, 3vw, 2.7rem);
            line-height: 1.15;
          }}
          .summary {{
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
          }}
          .actions {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 18px;
          }}
          .actions a {{
            text-decoration: none;
            color: var(--accent);
            font-weight: 700;
          }}
          .section-list {{
            display: grid;
            gap: 16px;
            margin-top: 20px;
          }}
          .section-card {{
            background: rgba(255, 253, 248, 0.94);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 18px;
            scroll-margin-top: 20px;
          }}
          .section-card.is-target {{
            border-color: var(--accent);
            background: var(--accent-soft);
          }}
          .section-card h2 {{
            margin: 6px 0 10px;
            font-size: 1.15rem;
            line-height: 1.4;
          }}
          .section-body {{
            display: grid;
            gap: 14px;
          }}
          .section-body p,
          .section-body h3 {{
            margin: 0;
          }}
          .section-body h3 {{
            font-size: 1rem;
            color: var(--accent);
          }}
          .section-body code {{
            display: inline-block;
            padding: 0.08rem 0.42rem;
            border-radius: 999px;
            background: rgba(138, 45, 28, 0.08);
            color: var(--accent);
            font-family: "SF Mono", "Menlo", monospace;
            font-size: 0.92em;
          }}
          .code-block {{
            border: 1px solid rgba(138, 45, 28, 0.14);
            border-radius: 16px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.92);
          }}
          .code-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 10px 12px;
            background: rgba(138, 45, 28, 0.08);
            border-bottom: 1px solid rgba(138, 45, 28, 0.12);
          }}
          .code-label {{
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }}
          .copy-button {{
            border: 0;
            border-radius: 999px;
            padding: 7px 12px;
            background: rgba(31, 28, 24, 0.08);
            color: var(--ink);
            font: inherit;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
          }}
          .copy-button.is-copied {{
            background: rgba(138, 45, 28, 0.14);
            color: var(--accent);
          }}
          .code-block pre {{
            margin: 0;
            padding: 14px 16px 16px;
            overflow-x: auto;
            white-space: pre;
            font-family: "SF Mono", "Menlo", monospace;
            font-size: 0.92rem;
            line-height: 1.65;
          }}
          .table-wrap {{
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.88);
          }}
          table {{
            width: 100%;
            border-collapse: collapse;
          }}
          td {{
            padding: 10px 12px;
            border-bottom: 1px solid rgba(216, 204, 184, 0.7);
            text-align: left;
            vertical-align: top;
            font-size: 0.94rem;
            line-height: 1.5;
          }}
          tr:last-child td {{
            border-bottom: 0;
          }}
          .section-meta {{
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.5;
          }}
        </style>
        <script>
          async function copyViewerCode(button) {{
            try {{
              const text = JSON.parse(button.dataset.copy || '""');
              if (navigator.clipboard && navigator.clipboard.writeText) {{
                await navigator.clipboard.writeText(text);
              }}
              const original = button.textContent;
              button.textContent = "복사됨";
              button.classList.add("is-copied");
              window.setTimeout(() => {{
                button.textContent = original;
                button.classList.remove("is-copied");
              }}, 1400);
            }} catch (error) {{
              button.textContent = "실패";
              window.setTimeout(() => {{
                button.textContent = "복사";
              }}, 1400);
            }}
          }}
        </script>
      </head>
      <body>
        <main>
          <section class="hero">
            <div class="eyebrow">Internal Citation Viewer</div>
            <h1>{title}</h1>
            <p class="summary">
              정규화된 한국어 본문 기준으로 출처를 보여줍니다.
              필요한 경우 원문 문서도 함께 열 수 있습니다.
            </p>
            <div class="actions">
              <span>섹션 수: {section_count}</span>
              <a href="{source_url}" target="_blank" rel="noreferrer">원문 문서 열기</a>
            </div>
          </section>
          <div class="section-list">
            {cards}
          </div>
        </main>
      </body>
    </html>
    """.format(
        title=html.escape(book_title),
        section_count=len(sections),
        source_url=html.escape(source_url, quote=True),
        cards="\n".join(cards),
    ).strip()


def _derive_next_context(
    previous: SessionContext | None,
    *,
    query: str,
    mode: str,
    result: AnswerResult,
) -> SessionContext:
    next_context = SessionContext.from_dict(previous.to_dict() if previous else None)
    next_context.mode = mode
    next_context.ocp_version = next_context.ocp_version or "4.20"
    prior_topic = next_context.current_topic

    if result.response_kind in {"smalltalk", "meta"}:
        return next_context

    explicit_topic = _infer_explicit_topic(query)
    if result.response_kind in {"clarification", "no_answer"}:
        next_context.unresolved_question = query
    elif explicit_topic:
        next_context.current_topic = explicit_topic
        next_context.open_entities = _infer_open_entities(explicit_topic)
        next_context.unresolved_question = None if result.citations else query
    elif result.citations:
        primary = result.citations[0]
        inferred_topic = _infer_topic_from_citation(primary)
        if inferred_topic:
            next_context.current_topic = inferred_topic
            next_context.open_entities = _infer_open_entities(inferred_topic)
        next_context.unresolved_question = None
    else:
        next_context.unresolved_question = query

    stabilized_topic = _stabilize_topic_from_entities(
        next_context.current_topic,
        next_context.open_entities,
    )
    if stabilized_topic:
        next_context.current_topic = stabilized_topic

    if next_context.current_topic:
        next_context.topic_journal = _merge_memory_items(
            next_context.topic_journal,
            [next_context.current_topic],
        )

    next_context.reference_hints = _merge_memory_items(
        next_context.reference_hints,
        _build_reference_hints(result, topic=next_context.current_topic),
    )
    updated_citation_group = _build_citation_group_memory(
        query=query,
        topic=next_context.current_topic,
        result=result,
    )
    if updated_citation_group is not None:
        next_context.active_citation_group = updated_citation_group
        next_context.citation_groups = _merge_citation_groups(
            next_context.citation_groups,
            updated_citation_group,
        )
    next_context.procedure_memory = _derive_procedure_memory(
        next_context.procedure_memory,
        query=query,
        topic=next_context.current_topic,
        reference_hints=next_context.reference_hints,
        explicit_topic=explicit_topic,
        prior_topic=prior_topic,
        answer_text=result.answer,
    )

    if next_context.procedure_memory and next_context.procedure_memory.steps:
        next_context.recent_steps = list(next_context.procedure_memory.steps[:5])
        procedure_commands = [command for command in next_context.procedure_memory.step_commands if command]
        next_context.recent_commands = procedure_commands[:3]
        next_context.recent_command_templates = [
            template
            for template in next_context.procedure_memory.step_command_templates
            if template is not None
        ][:3]
    else:
        extracted_steps = _extract_answer_steps(result.answer)
        if extracted_steps:
            next_context.recent_steps = extracted_steps
        elif explicit_topic and prior_topic and explicit_topic != prior_topic:
            next_context.recent_steps = []

        extracted_commands = _extract_answer_commands(result.answer)
        if extracted_commands:
            next_context.recent_commands = extracted_commands
            next_context.recent_command_templates = [
                template
                for template in (
                    _build_command_template(command, references=next_context.reference_hints)
                    for command in extracted_commands
                )
                if template is not None
            ][:3]
        elif explicit_topic and prior_topic and explicit_topic != prior_topic:
            next_context.recent_commands = []
            next_context.recent_command_templates = []

    next_context.recent_turns = _merge_recent_turns(
        next_context.recent_turns,
        _build_turn_memory(
            query=query,
            result=result,
            topic=next_context.current_topic,
            entities=next_context.open_entities,
            references=next_context.reference_hints,
        ),
    )
    return next_context


def _infer_explicit_topic(query: str) -> str | None:
    normalized = (query or "").strip()
    if not normalized:
        return None
    if ETCD_RE.search(normalized):
        if has_backup_restore_intent(normalized):
            return "etcd 백업/복원"
        return "etcd"
    if MCO_RE.search(normalized):
        return "Machine Config Operator"
    if has_rbac_intent(normalized):
        return "RBAC"
    if OPENSHIFT_RE.search(normalized) or OCP_RE.search(normalized):
        if ARCHITECTURE_RE.search(normalized):
            return "OpenShift 아키텍처"
        return "OpenShift"
    return None


def _infer_topic_from_citation(citation: Citation) -> str | None:
    book_slug = (citation.book_slug or "").lower()
    section = (citation.section or "").lower()
    anchor = (citation.anchor or "").lower()
    combined = " ".join(part for part in [book_slug, section, anchor] if part)

    if "authentication_and_authorization" in book_slug or "role" in combined or "rbac" in combined:
        return "RBAC"
    if "etcd" in combined or "backup_and_restore" in book_slug:
        if "backup" in combined or "restore" in combined or "백업" in combined or "복원" in combined:
            return "etcd 백업/복원"
        return "etcd"
    if "machine_configuration" in book_slug or "machine config" in combined or "mco" in combined:
        return "Machine Config Operator"
    if book_slug in {"architecture", "overview"}:
        if "architecture" in combined or "아키텍처" in combined:
            return "OpenShift 아키텍처"
        return "OpenShift"
    if "openshift" in combined or "ocp" in combined:
        return "OpenShift"
    return None


def _stabilize_topic_from_entities(topic: str | None, open_entities: list[str]) -> str | None:
    cleaned_topic = (topic or "").strip()
    if not cleaned_topic or not open_entities:
        return None
    if not DOC_HEADING_RE.match(cleaned_topic):
        return None

    entity_set = set(open_entities)
    lowered = cleaned_topic.lower()
    if "RBAC" in entity_set:
        return "RBAC"
    if "Machine Config Operator" in entity_set:
        return "Machine Config Operator"
    if "OpenShift" in entity_set:
        if "architecture" in lowered or "아키텍처" in cleaned_topic:
            return "OpenShift 아키텍처"
        return "OpenShift"
    if "etcd" in entity_set:
        if any(token in lowered for token in ["backup", "restore", "백업", "복원"]):
            return "etcd 백업/복원"
        return "etcd"
    return None


def _infer_open_entities(topic: str) -> list[str]:
    normalized = (topic or "").lower()
    if "etcd" in normalized:
        return ["etcd"]
    if "machine config operator" in normalized or "mco" in normalized:
        return ["Machine Config Operator"]
    if "rbac" in normalized:
        return ["RBAC"]
    if "openshift" in normalized:
        return ["OpenShift"]
    return []


def _dedupe_suggestions(candidates: list[str], *, query: str, limit: int = 3) -> list[str]:
    normalized_query = (query or "").strip().lower()
    seen: set[str] = set()
    unique: list[str] = []
    for candidate in candidates:
        cleaned = (candidate or "").strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered == normalized_query or lowered in seen:
            continue
        seen.add(lowered)
        unique.append(cleaned)
        if len(unique) >= limit:
            break
    return unique


def _fallback_follow_up_questions(*, mode: str) -> list[str]:
    if mode == "learn":
        return [
            "초보자 기준으로 단계별로 설명해줘",
            "관련 문서 위치도 같이 알려줘",
            "실무에서 왜 중요한지도 설명해줘",
        ]
    return [
        "실행 예시도 같이 보여줘",
        "주의사항도 함께 정리해줘",
        "관련 문서 위치도 같이 알려줘",
    ]


def _suggest_follow_up_questions(*, session: ChatSession, result: AnswerResult) -> list[str]:
    query = (result.query or "").strip()
    normalized = query.lower()
    mode = result.mode or session.mode or "ops"
    topic = (session.context.current_topic or "").strip()
    primary = result.citations[0] if result.citations else None
    book_slug = (primary.book_slug if primary else "").lower()
    section = (primary.section if primary else "").lower()

    if result.response_kind in {"smalltalk", "meta"}:
        return [
            "오픈시프트가 뭐야?",
            "특정 namespace에 admin 권한 주는 법 알려줘",
            "프로젝트가 Terminating에서 안 지워질 때 어떻게 해?",
        ]
    if result.response_kind == "clarification":
        if has_logging_ambiguity(query):
            return [
                "애플리케이션 로그를 보고 싶어",
                "인프라 로그를 보고 싶어",
                "감사 로그 위치 알려줘",
            ]
        if has_update_doc_locator_ambiguity(query):
            return [
                "4.20에서 4.21로 업그레이드할 때 문서 뭐부터 봐?",
                "단일 클러스터 업데이트 문서부터 알려줘",
                "업데이트 전 체크리스트 문서도 같이 알려줘",
            ]
        return _fallback_follow_up_questions(mode=mode)

    candidates: list[str] = []

    if has_rbac_intent(query) or topic == "RBAC" or book_slug == "authentication_and_authorization":
        candidates = [
            "RoleBinding YAML 예시도 보여줘",
            "권한이 잘 들어갔는지 확인하는 명령도 알려줘",
            "권한을 회수하려면 어떻게 해?",
            "edit 나 view 권한을 줄 때는 어떻게 달라?",
        ]
    elif "terminating" in normalized or "finalizer" in normalized or "삭제" in query:
        candidates = [
            "걸려 있는 리소스 찾는 명령도 알려줘",
            "finalizers를 안전하게 제거하는 절차를 알려줘",
            "강제 삭제 전에 확인할 점은 뭐야?",
            "namespace 이벤트를 먼저 확인하는 방법도 알려줘",
        ]
    elif has_certificate_monitor_intent(query) or "인증서" in query:
        candidates = [
            "만료 전에 자동 점검하는 방법도 알려줘",
            "인증서 갱신 절차도 같이 알려줘",
            "어떤 인증서를 우선 확인해야 하는지 정리해줘",
        ]
    elif ETCD_RE.search(query) or "etcd" in topic.lower() or book_slug == "etcd":
        if has_backup_restore_intent(query) or "백업" in topic or "복원" in topic:
            candidates = [
                "복원 절차도 같이 알려줘",
                "백업 파일이 정상인지 확인하는 방법도 알려줘",
                "운영 중 주의사항도 함께 정리해줘",
            ]
        else:
            candidates = [
                "etcd가 왜 중요한지도 설명해줘",
                "etcd 백업은 어떻게 해?",
                "etcd 복원은 언제 써야 해?",
                "장애가 나면 어떤 증상이 먼저 보이는지 알려줘",
            ]
    elif MCO_RE.search(query) or "machine config" in topic.lower() or book_slug in {
        "machine_configuration",
        "operators",
    }:
        candidates = [
            "MachineConfigPool 상태는 어떻게 확인해?",
            "노드 설정 변경 시 재부팅 여부는 어떻게 판단해?",
            "MCO가 관리하는 범위를 설명해줘",
        ]
    elif has_openshift_kubernetes_compare_intent(query):
        candidates = [
            "OpenShift에서 추가되는 운영 기능은 뭐야?",
            "쿠버네티스 대신 OpenShift를 쓰는 이유는?",
            "Operator가 왜 중요한지도 설명해줘",
        ]
    elif is_generic_intro_query(query) or topic.startswith("OpenShift") or book_slug in {
        "architecture",
        "overview",
    }:
        candidates = [
            "쿠버네티스와 차이도 설명해줘",
            "Operator가 뭐야?",
            "아키텍처를 한 장으로 요약해줘",
            "실무에서 주로 어떤 기능을 쓰는지도 알려줘",
        ]
    elif has_doc_locator_intent(query):
        candidates = [
            "관련 문서 위치를 바로 알려줘",
            "실행 예시도 같이 보여줘",
            "주의사항도 함께 정리해줘",
        ]

    if not candidates and "operator" in section:
        candidates = [
            "Operator가 왜 필요한지 설명해줘",
            "설치 후 상태는 어떻게 확인해?",
            "문제가 나면 어디부터 봐야 해?",
        ]

    if not candidates and "backup" in section:
        candidates = [
            "복원 절차도 같이 알려줘",
            "백업 파일 확인 방법도 알려줘",
            "운영 중 주의사항도 정리해줘",
        ]

    merged = _dedupe_suggestions(candidates + _fallback_follow_up_questions(mode=mode), query=query)
    return merged[:3]


def _build_chat_payload(
    *,
    session: ChatSession,
    result: AnswerResult,
) -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "mode": session.mode,
        "answer": result.answer,
        "rewritten_query": result.rewritten_query,
        "response_kind": result.response_kind,
        "warnings": list(result.warnings),
        "cited_indices": list(result.cited_indices),
        "citations": [
            {
                **citation.to_dict(),
                "href": _citation_href(citation),
            }
            for citation in result.citations
        ],
        "suggested_queries": _suggest_follow_up_questions(session=session, result=result),
        "context": session.context.to_dict(),
        "history_size": len(session.history),
        "retrieval_trace": dict(result.retrieval_trace),
        "pipeline_trace": dict(result.pipeline_trace),
    }


def _build_handler(
    *,
    answerer: Part3Answerer,
    store: SessionStore,
    root_dir: Path,
) -> type[BaseHTTPRequestHandler]:
    class ChatHandler(BaseHTTPRequestHandler):
        server_version = "OCPRAGPart4/0.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return None

        def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _start_ndjson_stream(self) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

        def _stream_event(self, payload: dict[str, Any]) -> None:
            try:
                body = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
                self.wfile.write(body)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return

        def do_GET(self) -> None:  # noqa: N802
            if self.path in {"/", "/index.html"}:
                self._send_html(INDEX_HTML_PATH.read_text(encoding="utf-8"))
                return
            if self.path == "/api/health":
                self._send_json({"ok": True})
                return
            if self.path == "/api/library":
                self._send_json(_build_library_payload(root_dir))
                return
            internal_viewer = _internal_viewer_html(root_dir, self.path)
            if internal_viewer is not None:
                self._send_html(internal_viewer)
                return
            local_html = _viewer_path_to_local_html(root_dir, self.path)
            if local_html is not None:
                self._send_html(local_html.read_text(encoding="utf-8"))
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self) -> None:  # noqa: N802
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            try:
                payload = json.loads(raw_body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_json({"error": "잘못된 JSON 요청입니다."}, HTTPStatus.BAD_REQUEST)
                return

            if self.path == "/api/chat":
                self._handle_chat(payload)
                return
            if self.path == "/api/chat/stream":
                self._handle_chat_stream(payload)
                return
            if self.path == "/api/reset":
                self._handle_reset(payload)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def _handle_chat(self, payload: dict[str, Any]) -> None:
            session_id = str(payload.get("session_id") or uuid.uuid4().hex)
            session = store.get(session_id)
            mode = str(payload.get("mode") or session.mode or "ops")
            regenerate = bool(payload.get("regenerate", False))
            query = str(payload.get("query") or "").strip()
            if regenerate and not query:
                query = session.last_query

            if not query:
                self._send_json({"error": "질문을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
                return

            try:
                result = answerer.answer(
                    query,
                    mode=mode,
                    context=session.context,
                    top_k=5,
                    candidate_k=20,
                    max_context_chunks=6,
                )
                result = _override_answer_with_procedure_follow_up(
                    query=query,
                    context=session.context,
                    result=result,
                )
                result = _override_answer_with_command_template_follow_up(
                    query=query,
                    context=session.context,
                    result=result,
                )
                answerer.append_log(result)
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    {"error": f"답변 생성 중 오류가 발생했습니다: {exc}"},
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
                return

            session.mode = mode
            session.context = _derive_next_context(
                session.context,
                query=query,
                mode=mode,
                result=result,
            )
            session.history.append(Turn(query=query, mode=mode, answer=result.answer))
            session.history = session.history[-40:]
            store.update(session)
            self._send_json(_build_chat_payload(session=session, result=result))

        def _handle_chat_stream(self, payload: dict[str, Any]) -> None:
            session_id = str(payload.get("session_id") or uuid.uuid4().hex)
            session = store.get(session_id)
            mode = str(payload.get("mode") or session.mode or "ops")
            regenerate = bool(payload.get("regenerate", False))
            query = str(payload.get("query") or "").strip()
            if regenerate and not query:
                query = session.last_query

            if not query:
                self._send_json({"error": "질문을 입력해 주세요."}, HTTPStatus.BAD_REQUEST)
                return

            self._start_ndjson_stream()
            self._stream_event(
                {
                    "type": "trace",
                    "step": "request_received",
                    "label": "질문 접수 완료",
                    "status": "done",
                    "detail": query[:180],
                }
            )

            def emit_trace(event: dict[str, Any]) -> None:
                self._stream_event(event)

            try:
                result = answerer.answer(
                    query,
                    mode=mode,
                    context=session.context,
                    top_k=5,
                    candidate_k=20,
                    max_context_chunks=6,
                    trace_callback=emit_trace,
                )
                result = _override_answer_with_procedure_follow_up(
                    query=query,
                    context=session.context,
                    result=result,
                )
                result = _override_answer_with_command_template_follow_up(
                    query=query,
                    context=session.context,
                    result=result,
                )
                answerer.append_log(result)
            except Exception as exc:  # noqa: BLE001
                self._stream_event(
                    {
                        "type": "error",
                        "error": f"답변 생성 중 오류가 발생했습니다: {exc}",
                    }
                )
                return

            session.mode = mode
            session.context = _derive_next_context(
                session.context,
                query=query,
                mode=mode,
                result=result,
            )
            session.history.append(Turn(query=query, mode=mode, answer=result.answer))
            session.history = session.history[-40:]
            store.update(session)
            self._stream_event(
                {
                    "type": "result",
                    "payload": _build_chat_payload(session=session, result=result),
                }
            )

        def _handle_reset(self, payload: dict[str, Any]) -> None:
            session_id = str(payload.get("session_id") or uuid.uuid4().hex)
            session = store.reset(session_id)
            self._send_json(
                {
                    "session_id": session.session_id,
                    "mode": session.mode,
                    "context": session.context.to_dict(),
                }
            )

    return ChatHandler


def _override_answer_with_command_template_follow_up(
    *,
    query: str,
    context: SessionContext | None,
    result: AnswerResult,
) -> AnswerResult:
    answer = build_command_template_follow_up_answer(query, context, result.citations)
    if not answer:
        return result
    return replace(result, answer=answer)


def serve(
    *,
    answerer: Part3Answerer,
    root_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8770,
    open_browser: bool = True,
) -> None:
    store = SessionStore()
    handler = _build_handler(answerer=answerer, store=store, root_dir=root_dir)
    server = ThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{port}"
    print(f"Part 4 QA UI running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


__all__ = [
    "ChatSession",
    "SessionStore",
    "_citation_href",
    "_build_library_payload",
    "_internal_viewer_html",
    "_viewer_path_to_local_html",
    "_derive_next_context",
    "serve",
]
