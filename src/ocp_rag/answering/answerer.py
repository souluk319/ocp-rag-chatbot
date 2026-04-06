from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, replace
from pathlib import Path

from ocp_rag.shared.settings import Settings
from ocp_rag.retrieval import Part2Retriever
from ocp_rag.retrieval.command_memory import build_command_template_follow_up_answer
from ocp_rag.retrieval.query import (
    STEP_REFERENCE_RE,
    has_certificate_monitor_intent,
    has_cluster_node_usage_intent,
    has_doc_locator_intent,
    has_follow_up_reference,
    has_node_drain_intent,
    has_openshift_kubernetes_compare_intent,
    has_rbac_assignment_intent,
    has_step_by_step_intent,
    is_generic_intro_query,
)
from ocp_rag.session import CitationGroupMemory, SessionContext

from .context import assemble_context, build_context_bundle_from_citations
from .llm import LLMClient
from .models import AnswerResult, Citation
from .prompt import build_messages
from .router import route_non_rag


CITATION_RE = re.compile(r"\[(\d+)\]")
ANSWER_HEADER_RE = re.compile(
    r"^\s*(?:[#>*\-\s`]*)(?:답변|answer)\s*[:：]?\s*",
    re.IGNORECASE,
)
GUIDE_HEADER_RE = re.compile(
    r"(?:^|\n)\s*(?:[#>*\-\s`]*)(?:추가\s*가이드|additional guidance)\s*[:：]?\s*",
    re.IGNORECASE,
)
WEAK_GUIDE_TAIL_RE = re.compile(
    r"\n\n추가 가이드:\s*.*?(?:명시되어 있지 않습니다|포함되어 있지 않습니다|정보가 없습니다)\.?\s*$",
    re.DOTALL,
)
INTRO_OFFTOPIC_SENTENCE_RE = re.compile(
    r"(?:\s|^)(?:[^.\n]*?(?:etcd 백업|snapshot|cluster-backup\.sh)[^.\n]*)(?:\.|$)",
    re.IGNORECASE,
)
GREETING_PREFIXES = (
    "안녕하세요",
    "물론입니다",
    "좋습니다",
    "네,",
)
ADJACENT_DUPLICATE_CITATION_RE = re.compile(r"(\[\d+\])(?:\s*\1)+")
BARE_COMMAND_ANSWER_RE = re.compile(
    r"^답변:\s*(?P<command>\$?\s*(?:oc|kubectl|etcdctl|podman|curl|openssl|openshift-install|journalctl|systemctl|helm)\b[^\n]*?)(?P<citations>(?:\s*\[\d+\])*)\s*$",
    re.IGNORECASE,
)
RBAC_NAMESPACE_RE = re.compile(
    r"(?P<name>[A-Za-z0-9][A-Za-z0-9._:-]*)\s*(?:namespace|project|네임스페이스|프로젝트)",
    re.IGNORECASE,
)
RBAC_ROLE_RE = re.compile(
    r"(?P<role>cluster-admin|admin|edit|view|[A-Za-z0-9][A-Za-z0-9._:-]*)\s*(?:역할|role|권한)",
    re.IGNORECASE,
)
RBAC_USER_SUBJECT_RE = re.compile(
    r"(?P<name>[A-Za-z0-9][A-Za-z0-9._:-]*)\s*(?:사용자|유저|user)",
    re.IGNORECASE,
)
RBAC_ASSIGNMENT_VERB_RE = re.compile(r"(부여|추가|바인딩|grant|assign)", re.IGNORECASE)
RBAC_VERIFY_RE = re.compile(r"(확인|검증|verify|check)", re.IGNORECASE)
RBAC_COMMAND_SUPPORT_RE = re.compile(r"oc\s+adm\s+policy\s+add-role-to-user", re.IGNORECASE)
RBAC_ROLEBINDING_SUPPORT_RE = re.compile(r"rolebinding", re.IGNORECASE)
CITATION_EXPLICIT_REF_RE = re.compile(
    r"(그\s*문서|위\s*근거|방금\s*(?:본|인용한)?\s*(?:문서|근거|출처|자료)|아까\s*(?:본|인용한)?\s*(?:문서|근거|출처|자료)|같은\s*문서|(?:근거|출처|자료|문서)\s*(?:다시|기준)|(?:(?<!\d)(1[0-9]|[1-9])\s*번|첫\s*번째|두\s*번째|세\s*번째|네\s*번째)\s*(?:근거|출처|자료|문서))",
    re.IGNORECASE,
)
CITATION_DIGIT_ORDINAL_RE = re.compile(r"(?<!\d)(1[0-9]|[1-9])\s*번\s*(?:근거|출처|자료|문서)", re.IGNORECASE)
CITATION_SOURCE_LOOKUP_RE = re.compile(
    r"(근거|출처|어느\s*파일|어떤\s*파일|문서\s*위치|문서.*(?:보여|열어)|source|citation|document)",
    re.IGNORECASE,
)
CITATION_SAFE_RECAP_RE = re.compile(
    r"(다시\s*(?:설명|정리|요약)|짧게\s*(?:정리|요약)|brief\s+recap|restate|summarize\s+again|same\s+document)",
    re.IGNORECASE,
)
CITATION_RISKY_EXPANSION_RE = re.compile(
    r"(\uc65c|\uc5b4\ub5bb\uac8c|\ucc28\uc774|\ube44\uad50|\ub2e4\ub978|\ub300\uc548|\uc6d0\uc778|\ud574\uacb0|\ubc29\ubc95|\ub2e8\uacc4|why|how|difference|compare|alternative|step|serviceaccount|yaml|json|namespace|user|group|command|\uba85\ub839)",
    re.IGNORECASE,
)
ORDINAL_WORDS = {
    "첫번째": 1,
    "첫 번째": 1,
    "두번째": 2,
    "두 번째": 2,
    "세번째": 3,
    "세 번째": 3,
    "네번째": 4,
    "네 번째": 4,
}
BRANCH_RETURN_RE = re.compile(
    r"(\uc544\uae4c|\uadf8\ub54c|\uc6d0\ub798|\ub3cc\uc544\uac00|\ub2e4\uc2dc \ucc98\uc74c \uc8fc\uc81c|\ucc98\uc74c \uc8fc\uc81c|back to|return to|go back)",
    re.IGNORECASE,
)
BRANCH_TOPIC_TOKEN_RE = re.compile(r"[A-Za-z0-9._:-]+|[\uac00-\ud7a3]{2,}")


@dataclass(slots=True)
class RbacAssignmentRequest:
    subject_name: str
    namespace: str
    role: str


@dataclass(slots=True)
class CitationReplaySelection:
    citations: list[Citation]
    scope: str
    detail: str
    direct_answer: str | None = None


def normalize_answer_text(answer_text: str) -> str:
    normalized = (answer_text or "").strip()
    if not normalized:
        return "답변:"

    lines = [line.strip() for line in normalized.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and any(lines[0].startswith(prefix) for prefix in GREETING_PREFIXES):
        lines.pop(0)

    normalized = "\n".join(lines).strip()
    normalized = ANSWER_HEADER_RE.sub("", normalized, count=1)
    for prefix in GREETING_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :].lstrip(" ,:\n")
            break
    normalized = GUIDE_HEADER_RE.sub("\n\n추가 가이드: ", normalized)
    normalized = normalized.strip()

    if not normalized:
        return "답변:"
    if normalized.startswith("답변:"):
        return normalized
    return f"답변: {normalized}"


def reshape_ops_answer_text(answer_text: str, *, mode: str) -> str:
    if mode != "ops":
        return answer_text

    match = BARE_COMMAND_ANSWER_RE.match(answer_text.strip())
    if not match:
        return answer_text

    command = match.group("command").strip()
    citations = (match.group("citations") or "").strip()
    intro = "답변: 아래 명령을 사용하세요"
    if citations:
        intro = f"{intro} {citations}."
    else:
        intro = f"{intro}."
    return f"{intro}\n\n```bash\n{command}\n```"


def _ensure_korean_product_terms(answer_text: str, *, query: str) -> str:
    updated = re.sub(r"오픈\s*시프트", "오픈시프트", answer_text)
    if "쿠버네티스" in query and "쿠버네티스" not in updated and "Kubernetes" in updated:
        updated = updated.replace("Kubernetes", "쿠버네티스(Kubernetes)", 1)
    if (
        (
            "쿠버네티스" in query
            or has_openshift_kubernetes_compare_intent(query)
            or is_generic_intro_query(query)
        )
        and "오픈시프트" in updated
        and "OpenShift" not in updated
    ):
        updated = updated.replace("오픈시프트", "오픈시프트(OpenShift)", 1)
    if (
        any(token in query for token in ("오픈시프트", "OpenShift", "OCP"))
        and "오픈시프트" not in updated
        and "OpenShift" in updated
    ):
        updated = updated.replace("OpenShift", "오픈시프트(OpenShift)", 1)
    return updated


def _align_answer_to_grounded_commands(answer_text: str, *, query: str, citations) -> str:
    excerpt_text = "\n".join((citation.excerpt or "") for citation in citations).lower()
    updated = answer_text

    if has_cluster_node_usage_intent(query) and "oc adm top nodes" in excerpt_text:
        if "oc adm top nodes" not in updated.lower():
            return (
                "답변: 클러스터 전체 노드의 CPU와 메모리 사용량은 아래 명령으로 한 번에 확인할 수 있습니다 [1].\n\n"
                "```bash\noc adm top nodes\n```"
            )

    if has_node_drain_intent(query) and "oc adm drain" in excerpt_text:
        updated = re.sub(r"\bkubectl\s+drain\b", "oc adm drain", updated, flags=re.IGNORECASE)
        if "oc adm drain" not in updated.lower():
            return (
                "답변: 점검 전에는 아래 명령으로 해당 노드를 안전하게 drain 하면 됩니다 [1].\n\n"
                "```bash\noc adm drain <노드명> --ignore-daemonsets --delete-emptydir-data\n```"
            )

    if has_certificate_monitor_intent(query) and "monitor-certificates" in excerpt_text:
        if "monitor-certificates" not in updated.lower():
            return (
                "답변: 인증서 만료 상태는 아래 명령으로 바로 확인할 수 있습니다 [1].\n\n"
                "```bash\noc adm ocp-certificates monitor-certificates\n```"
            )

    return updated


def _strip_weak_additional_guidance(answer_text: str, *, mode: str, citations) -> str:
    if mode != "ops" or not citations:
        return answer_text
    return WEAK_GUIDE_TAIL_RE.sub("", answer_text).strip()


def _strip_intro_offtopic_noise(answer_text: str, *, query: str) -> str:
    if not (is_generic_intro_query(query) or has_openshift_kubernetes_compare_intent(query)):
        return answer_text
    cleaned = INTRO_OFFTOPIC_SENTENCE_RE.sub(" ", answer_text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def summarize_session_context(context: SessionContext | None) -> str:
    if context is None:
        return ""

    parts: list[str] = []
    if context.current_topic:
        parts.append(f"- 현재 주제: {context.current_topic}")
    if context.open_entities:
        parts.append(f"- 열린 엔터티: {', '.join(context.open_entities)}")
    if context.unresolved_question:
        parts.append(f"- 미해결 질문: {context.unresolved_question}")
    elif context.user_goal:
        parts.append(f"- 사용자 목표: {context.user_goal}")
    if context.topic_journal:
        parts.append(f"- 최근 주제 흐름: {' -> '.join(context.topic_journal[-3:])}")
    if context.reference_hints:
        parts.append(f"- 최근 근거 메모: {' | '.join(context.reference_hints[-3:])}")
    if context.recent_turns:
        recent_turn_notes = " | ".join(
            (
                f"{index + 1}. {turn.query}"
                if not turn.topic and not turn.answer_focus
                else f"{index + 1}. {turn.query} -> {turn.topic or turn.answer_focus}"
            )
            for index, turn in enumerate(context.recent_turns[-3:])
        )
        parts.append(f"- 최근 대화 캡슐: {recent_turn_notes}")
    if context.recent_steps:
        numbered_steps = " | ".join(
            f"{index + 1}. {step}"
            for index, step in enumerate(context.recent_steps[:3])
        )
        parts.append(f"- 최근 단계 메모: {numbered_steps}")
    if context.recent_commands:
        parts.append(f"- 최근 명령 메모: {' | '.join(context.recent_commands[:2])}")
    if context.procedure_memory and context.procedure_memory.steps:
        active_index = context.procedure_memory.active_step_index
        if active_index is not None and 0 <= active_index < len(context.procedure_memory.steps):
            parts.append(
                f"- 진행 중 절차: {context.procedure_memory.goal or context.current_topic or '절차'} "
                f"(현재 {active_index + 1}번: {context.procedure_memory.steps[active_index]})"
            )
        else:
            parts.append(f"- 진행 중 절차: {context.procedure_memory.goal or context.current_topic or '절차'}")
        step_command_pairs: list[str] = []
        for index, step in enumerate(context.procedure_memory.steps[:4]):
            command = context.procedure_memory.command_for(index)
            if command:
                step_command_pairs.append(f"{index + 1}. {step} => {command}")
        if step_command_pairs:
            parts.append(f"- procedure step command map: {' | '.join(step_command_pairs)}")
        if context.procedure_memory.references:
            parts.append(f"- 절차 근거 메모: {' | '.join(context.procedure_memory.references[:2])}")
    if context.ocp_version:
        parts.append(f"- OCP 버전: {context.ocp_version}")
    if context.mode:
        parts.append(f"- 세션 모드: {context.mode}")
    return "\n".join(parts)


def _augment_query_with_procedure_focus(query: str, context: SessionContext | None) -> str:
    if context is None or context.procedure_memory is None or not context.procedure_memory.steps:
        return query
    match = STEP_REFERENCE_RE.search(query or "")
    if match:
        candidate = int(match.group(1)) - 1
        if 0 <= candidate < len(context.procedure_memory.steps):
            focused_index = candidate
        else:
            focused_index = context.procedure_memory.active_step_index
    else:
        if not has_follow_up_reference(query):
            return query
        focused_index = context.procedure_memory.active_step_index

    if focused_index is None or focused_index < 0 or focused_index >= len(context.procedure_memory.steps):
        return query

    step = context.procedure_memory.steps[focused_index]
    command = context.procedure_memory.command_for(focused_index)
    parts = [query, f"Focused procedure step: {focused_index + 1}. {step}"]
    if context.procedure_memory.goal:
        parts.append(f"Procedure goal: {context.procedure_memory.goal}")
    if command:
        parts.append(f"Expected step command: {command}")
    return "\n".join(parts)


def _resolve_procedure_follow_up_index(query: str, context: SessionContext | None) -> int | None:
    if context is None or context.procedure_memory is None or not context.procedure_memory.steps:
        return None

    procedure = context.procedure_memory
    normalized = query or ""
    match = STEP_REFERENCE_RE.search(normalized)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(procedure.steps):
            return index

    if not has_follow_up_reference(query):
        return None

    lowered = normalized.lower()
    if "다음" in normalized or "next" in lowered:
        if procedure.active_step_index is None:
            return 0
        return min(procedure.active_step_index + 1, len(procedure.steps) - 1)
    if "현재" in normalized or "해당 단계" in normalized or "this step" in lowered or "current step" in lowered:
        return procedure.active_step_index
    return procedure.active_step_index


def _build_procedure_follow_up_answer(
    query: str,
    context: SessionContext | None,
    citations: list,
) -> str | None:
    focus_index = _resolve_procedure_follow_up_index(query, context)
    if focus_index is None or context is None or context.procedure_memory is None:
        return None

    procedure = context.procedure_memory
    if focus_index < 0 or focus_index >= len(procedure.steps):
        return None

    step = procedure.steps[focus_index]
    command = procedure.command_for(focus_index)
    citation_mark = " [1]" if citations else ""
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

    return "\n".join(lines)


def _extract_rbac_assignment_request(query: str) -> RbacAssignmentRequest | None:
    if not has_rbac_assignment_intent(query) and not RBAC_ASSIGNMENT_VERB_RE.search(query or ""):
        return None

    namespace_match = RBAC_NAMESPACE_RE.search(query or "")
    role_match = RBAC_ROLE_RE.search(query or "")
    subject_match = RBAC_USER_SUBJECT_RE.search(query or "")
    if namespace_match is None or role_match is None or subject_match is None:
        return None

    return RbacAssignmentRequest(
        subject_name=subject_match.group("name").strip(),
        namespace=namespace_match.group("name").strip(),
        role=role_match.group("role").strip(),
    )


def _supports_rbac_assignment_fast_lane(citations: list) -> bool:
    excerpt_blob = "\n".join((citation.excerpt or "") for citation in citations)
    return bool(RBAC_COMMAND_SUPPORT_RE.search(excerpt_blob)) and bool(
        RBAC_ROLEBINDING_SUPPORT_RE.search(excerpt_blob)
    )


def _build_first_turn_rbac_assignment_answer(
    query: str,
    citations: list,
    *,
    context: SessionContext | None,
) -> str | None:
    if context is not None and context.procedure_memory is not None and context.procedure_memory.steps:
        return None
    if not has_step_by_step_intent(query) and not RBAC_VERIFY_RE.search(query or ""):
        return None

    request = _extract_rbac_assignment_request(query)
    if request is None or not _supports_rbac_assignment_fast_lane(citations):
        return None

    citation_mark = " [1]" if citations else ""
    grant_command = (
        f"oc adm policy add-role-to-user {request.role} {request.subject_name} -n {request.namespace}"
    )
    verify_command = f"oc describe rolebinding -n {request.namespace}"
    lines = [
        (
            "답변: namespace 범위에서 사용자에게 역할을 부여하고 확인하는 기본 절차는 다음과 같습니다"
            f"{citation_mark}."
        ),
        "",
        f"1. 사용자 `{request.subject_name}`에게 `{request.namespace}` namespace의 `{request.role}` 역할을 부여합니다.",
        "",
        "```bash",
        grant_command,
        "```",
        "",
        f"2. RoleBinding이 생성되었는지 `{request.namespace}` namespace에서 확인합니다.",
        "",
        "```bash",
        verify_command,
        "```",
    ]
    return "\n".join(lines)


def _citation_origin(citation: Citation) -> str:
    return (citation.origin or "retrieved").strip() or "retrieved"


def _citation_memory_to_citation(memory, *, index: int) -> Citation:
    return Citation(
        index=index,
        chunk_id=memory.chunk_id,
        book_slug=memory.book_slug,
        section=memory.section,
        anchor=memory.anchor,
        source_url=memory.source_url,
        viewer_path=memory.viewer_path,
        excerpt=memory.excerpt,
        origin="replayed",
    )


def _extract_citation_reference_index(query: str) -> int | None:
    match = CITATION_DIGIT_ORDINAL_RE.search(query or "")
    if match:
        return int(match.group(1))
    normalized = " ".join((query or "").split())
    for token, index in ORDINAL_WORDS.items():
        if token in normalized:
            return index
    return None


def _has_explicit_citation_reference(query: str) -> bool:
    return bool(CITATION_EXPLICIT_REF_RE.search(query or ""))


def _is_source_lookup_query(query: str) -> bool:
    normalized = query or ""
    return bool(CITATION_SOURCE_LOOKUP_RE.search(normalized)) and not bool(
        CITATION_RISKY_EXPANSION_RE.search(normalized)
    )


def _is_safe_citation_recap_query(query: str) -> bool:
    normalized = query or ""
    if not _has_explicit_citation_reference(normalized):
        return False
    if CITATION_RISKY_EXPANSION_RE.search(normalized):
        return False
    return bool(CITATION_SAFE_RECAP_RE.search(normalized))


def _build_citation_replay_lookup_answer(citations: list[Citation]) -> str:
    if not citations:
        return ""
    if len(citations) == 1:
        citation = citations[0]
        section = citation.section or citation.anchor or "-"
        return "\n".join(
            [
                "답변: 방금 근거로 사용한 문서를 다시 고정했습니다 [1].",
                "",
                f"- 문서: `{citation.book_slug}`",
                f"- 섹션: `{section}`",
                "- 같은 화면 문서 패널에서 바로 다시 확인할 수 있습니다.",
            ]
        )

    lines = ["답변: 방금 근거로 사용한 문서를 다시 고정했습니다."]
    for citation in citations:
        section = citation.section or citation.anchor or "-"
        lines.append(f"- [{citation.index}] `{citation.book_slug}` / `{section}`")
    lines.append("- 같은 화면 문서 패널에서 바로 다시 확인할 수 있습니다.")
    return "\n".join(lines)


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


def _citation_group_list(context: SessionContext | None) -> list[CitationGroupMemory]:
    if context is None:
        return []
    groups = [group for group in context.citation_groups if group.citations]
    if context.active_citation_group is not None and context.active_citation_group.citations:
        active_identity = _citation_group_identity(context.active_citation_group)
        if not any(_citation_group_identity(group) == active_identity for group in groups):
            groups.append(context.active_citation_group)
    return groups


def _branch_tokens(text: str) -> set[str]:
    return {token.lower() for token in BRANCH_TOPIC_TOKEN_RE.findall(text or "") if len(token.strip()) >= 2}


def _citation_group_tokens(group: CitationGroupMemory) -> set[str]:
    primary = group.primary_citation()
    texts = [group.topic or "", group.query or ""]
    if primary is not None:
        texts.extend([primary.book_slug or "", primary.section or "", primary.anchor or ""])
    return _branch_tokens(" ".join(texts))


def _explicit_branch_match_score(normalized_query: str, group: CitationGroupMemory) -> int:
    score = 0
    topic_lower = (group.topic or "").strip().lower()
    if topic_lower and topic_lower in normalized_query:
        score += 5
    query_lower = (group.query or "").strip().lower()
    if query_lower and query_lower in normalized_query:
        score += 4

    primary = group.primary_citation()
    if primary is not None:
        book_slug = (primary.book_slug or "").strip().lower()
        section = (primary.section or "").strip().lower()
        if book_slug and book_slug in normalized_query:
            score += 3
        if section and section in normalized_query:
            score += 2
    return score


def _select_citation_group_for_query(
    query: str,
    context: SessionContext | None,
) -> tuple[CitationGroupMemory | None, str | None]:
    if context is None:
        return None, None
    groups = _citation_group_list(context)
    if not groups:
        return None, None

    normalized = " ".join((query or "").split()).lower()
    if not normalized:
        return context.active_citation_group, "active_branch"
    if "\ucc98\uc74c \uc8fc\uc81c" in normalized or "\ucc98\uc74c \ubb38\uc11c" in normalized:
        return groups[0], "initial_branch"

    active_identity = (
        _citation_group_identity(context.active_citation_group)
        if context.active_citation_group is not None and context.active_citation_group.citations
        else None
    )
    query_tokens = _branch_tokens(normalized)
    explicit_citation_reference = _has_explicit_citation_reference(query)
    branch_return = bool(BRANCH_RETURN_RE.search(query or ""))
    explicit_matches: list[tuple[int, int, CitationGroupMemory]] = []
    scored: list[tuple[int, int, CitationGroupMemory]] = []

    for index, group in enumerate(groups):
        score = 0
        group_tokens = _citation_group_tokens(group)
        score += len(query_tokens & group_tokens)
        explicit_score = _explicit_branch_match_score(normalized, group)
        score += explicit_score
        if explicit_score > 0:
            explicit_matches.append((explicit_score, index, group))
        if active_identity is not None and _citation_group_identity(group) == active_identity:
            score += 1 if not branch_return else 0
        scored.append((score, index, group))

    if explicit_matches:
        explicit_matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
        top_score = explicit_matches[0][0]
        top_groups = [item for item in explicit_matches if item[0] == top_score]
        if len(top_groups) > 1:
            return None, "ambiguous_branch_reference"
        chosen = top_groups[0][2]
        return chosen, f"branch topic={chosen.topic or chosen.query or 'session'}"

    if explicit_citation_reference and context.active_citation_group is not None and context.active_citation_group.citations:
        return context.active_citation_group, "active_branch"

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    if scored and scored[0][0] > 0:
        top_score = scored[0][0]
        top_groups = [item for item in scored if item[0] == top_score]
        if len(top_groups) > 1:
            return None, "ambiguous_branch_reference"
        chosen = top_groups[0][2]
        return chosen, f"branch topic={chosen.topic or chosen.query or 'session'}"

    if context.active_citation_group is not None and context.active_citation_group.citations:
        return context.active_citation_group, "active_branch"
    return groups[-1], "latest_branch"


def _augment_query_with_branch_focus(query: str, group: CitationGroupMemory) -> str:
    primary = group.primary_citation()
    parts = [query]
    if group.topic:
        parts.append(f"Focused prior topic: {group.topic}")
    if group.query:
        parts.append(f"Focused prior question: {group.query}")
    if primary is not None:
        if primary.book_slug:
            parts.append(f"Focused prior book: {primary.book_slug}")
        if primary.section:
            parts.append(f"Focused prior section: {primary.section}")
    return "\n".join(parts)


def _resolve_citation_replay_selection(
    query: str,
    context: SessionContext | None,
    *,
    target_group: CitationGroupMemory | None = None,
) -> tuple[CitationReplaySelection | None, str | None]:
    if context is None:
        return None, None
    if not _has_explicit_citation_reference(query):
        return None, None
    group = target_group or context.active_citation_group
    if group is None or not group.citations:
        return None, None

    if CITATION_RISKY_EXPANSION_RE.search(query or "") and not _is_source_lookup_query(query):
        return None, "requires_fresh_retrieval"
    requested_index = _extract_citation_reference_index(query)
    if requested_index is not None:
        target = group.citation_for_index(requested_index)
        if target is None:
            return None, "ambiguous_reference"
        citations = [_citation_memory_to_citation(target, index=1)]
        detail = f"session citation ordinal={requested_index}"
        return CitationReplaySelection(
            citations=citations,
            scope="ordinal",
            detail=detail,
            direct_answer=_build_citation_replay_lookup_answer(citations) if _is_source_lookup_query(query) else None,
        ), None

    primary = group.primary_citation()
    if primary is None:
        return None, "missing_primary_citation"
    citations = [_citation_memory_to_citation(primary, index=1)]

    if _is_source_lookup_query(query):
        return CitationReplaySelection(
            citations=citations,
            scope="primary",
            detail="session citation primary lookup",
            direct_answer=_build_citation_replay_lookup_answer(citations),
        ), None
    if _is_safe_citation_recap_query(query):
        return CitationReplaySelection(
            citations=citations,
            scope="primary",
            detail="session citation primary replay",
        ), None
    return None, "requires_fresh_retrieval"


def _answer_from_citation_replay(
    *,
    query: str,
    mode: str,
    context: SessionContext | None,
    replay_selection: CitationReplaySelection,
    llm_client: LLMClient,
    answer_started_at: float,
    pipeline_timings_ms: dict[str, float],
    emit,
) -> AnswerResult:
    emit(
        {
            "step": "citation_replay",
            "label": "citation replay cache hit",
            "status": "done",
            "detail": replay_selection.detail,
        }
    )
    emit(
        {
            "step": "retrieval",
            "label": "evidence retrieval skipped",
            "status": "done",
            "detail": f"session replay {len(replay_selection.citations)} citation(s)",
        }
    )
    pipeline_timings_ms["retrieval_total"] = 0.0

    context_started_at = time.perf_counter()
    emit(
        {
            "step": "context_assembly",
            "label": "citation context replay",
            "status": "running",
        }
    )
    context_bundle = build_context_bundle_from_citations(replay_selection.citations)
    pipeline_timings_ms["context_assembly"] = round(
        (time.perf_counter() - context_started_at) * 1000,
        1,
    )
    emit(
        {
            "step": "context_assembly",
            "label": "citation context replay ready",
            "status": "done",
            "detail": f"citation {len(context_bundle.citations)}",
            "duration_ms": pipeline_timings_ms["context_assembly"],
            "meta": {
                "selected": len(context_bundle.citations),
                "selected_hits": _summarize_selected_citations(
                    context_bundle.citations,
                    [],
                ),
            },
        }
    )

    prompt_started_at = time.perf_counter()
    emit(
        {
            "step": "prompt_build",
            "label": "prompt build",
            "status": "running",
        }
    )
    messages = build_messages(
        query=_augment_query_with_procedure_focus(query, context),
        mode=mode,
        context_bundle=context_bundle,
        session_summary=summarize_session_context(context),
    )
    pipeline_timings_ms["prompt_build"] = round(
        (time.perf_counter() - prompt_started_at) * 1000,
        1,
    )
    emit(
        {
            "step": "prompt_build",
            "label": "prompt build",
            "status": "done",
            "detail": f"messages {len(messages)}",
            "duration_ms": pipeline_timings_ms["prompt_build"],
        }
    )

    llm_started_at = time.perf_counter()
    if replay_selection.direct_answer is not None:
        emit(
            {
                "step": "citation_replay_lookup",
                "label": "direct replay answer",
                "status": "done",
                "detail": replay_selection.detail,
            }
        )
        answer_text = replay_selection.direct_answer
        pipeline_timings_ms["llm_generate_total"] = 0.0
    else:
        answer_text = reshape_ops_answer_text(
            normalize_answer_text(
                llm_client.generate(messages, trace_callback=emit)
            ),
            mode=mode,
        )
        answer_text = _ensure_korean_product_terms(answer_text, query=query)
        answer_text = _align_answer_to_grounded_commands(
            answer_text,
            query=query,
            citations=context_bundle.citations,
        )
        answer_text = _strip_weak_additional_guidance(
            answer_text,
            mode=mode,
            citations=context_bundle.citations,
        )
        answer_text = _strip_intro_offtopic_noise(answer_text, query=query)
        if mode == "ops" and context_bundle.citations and not CITATION_RE.search(answer_text):
            answer_text = _inject_single_citation(answer_text, citation_index=1)
        pipeline_timings_ms["llm_generate_total"] = round(
            (time.perf_counter() - llm_started_at) * 1000,
            1,
        )

    finalize_started_at = time.perf_counter()
    emit(
        {
            "step": "citation_finalize",
            "label": "citation finalize",
            "status": "running",
        }
    )
    answer_text, final_citations, cited_indices = finalize_citations(
        answer_text,
        context_bundle.citations,
    )
    auto_repaired_citations = False
    if not cited_indices:
        answer_text, auto_repaired_citations = maybe_autorepair_inline_citations(
            answer_text,
            context_bundle.citations,
        )
        if auto_repaired_citations:
            answer_text, final_citations, cited_indices = finalize_citations(
                answer_text,
                context_bundle.citations,
            )
    pipeline_timings_ms["citation_finalize"] = round(
        (time.perf_counter() - finalize_started_at) * 1000,
        1,
    )
    emit(
        {
            "step": "citation_finalize",
            "label": "citation finalize",
            "status": "done",
            "detail": f"final citations {len(final_citations)}",
            "duration_ms": pipeline_timings_ms["citation_finalize"],
        }
    )

    warnings: list[str] = []
    if not cited_indices:
        warnings.append("answer has no inline citations")
    elif auto_repaired_citations:
        warnings.append("inline citations auto-repaired")

    pipeline_timings_ms["total"] = round(
        (time.perf_counter() - answer_started_at) * 1000,
        1,
    )
    emit(
        {
            "step": "pipeline_complete",
            "label": "answer complete",
            "status": "done",
            "detail": f"total {pipeline_timings_ms['total']}ms",
            "duration_ms": pipeline_timings_ms["total"],
        }
    )

    retrieval_trace = {
        "warnings": [],
        "timings_ms": {"citation_replay": 0.0},
        "citation_replay": {
            "status": "hit",
            "scope": replay_selection.scope,
            "count": len(context_bundle.citations),
            "detail": replay_selection.detail,
        },
    }
    return AnswerResult(
        query=query,
        mode=mode,
        answer=answer_text,
        rewritten_query=query,
        response_kind="rag",
        citations=final_citations,
        cited_indices=cited_indices,
        warnings=warnings,
        retrieval_trace=retrieval_trace,
        pipeline_trace={
            "events": [],
            "timings_ms": dict(pipeline_timings_ms),
            "selection": {
                "selected_hits": _summarize_selected_citations(
                    context_bundle.citations,
                    [],
                )
            },
            "citation_replay": retrieval_trace["citation_replay"],
        },
    )


def _citation_identity(citation) -> tuple[str, str]:
    viewer_path = (citation.viewer_path or "").strip().lower()
    if viewer_path:
        return citation.book_slug, viewer_path
    source_url = (citation.source_url or "").strip().lower()
    anchor = (citation.anchor or "").strip().lower()
    return citation.book_slug, f"{source_url}#{anchor}"


def finalize_citations(
    answer_text: str,
    citations,
) -> tuple[str, list, list[int]]:
    referenced_indices: list[int] = []
    for match in CITATION_RE.finditer(answer_text):
        index = int(match.group(1))
        if 1 <= index <= len(citations):
            referenced_indices.append(index)

    if not referenced_indices:
        return answer_text, [], []

    canonical_index_by_source: dict[tuple[str, str], int] = {}
    remapped_index_by_original: dict[int, int] = {}
    final_citations = []

    for original_index in referenced_indices:
        if original_index in remapped_index_by_original:
            continue
        citation = citations[original_index - 1]
        identity = _citation_identity(citation)
        canonical_index = canonical_index_by_source.get(identity)
        if canonical_index is None:
            canonical_index = len(final_citations) + 1
            canonical_index_by_source[identity] = canonical_index
            final_citations.append(replace(citation, index=canonical_index))
        remapped_index_by_original[original_index] = canonical_index

    rewritten_answer = CITATION_RE.sub(
        lambda match: (
            f"[{remapped_index_by_original[int(match.group(1))]}]"
            if int(match.group(1)) in remapped_index_by_original
            else match.group(0)
        ),
        answer_text,
    )
    rewritten_answer = ADJACENT_DUPLICATE_CITATION_RE.sub(r"\1", rewritten_answer)

    cited_indices: list[int] = []
    seen_indices: set[int] = set()
    for match in CITATION_RE.finditer(rewritten_answer):
        index = int(match.group(1))
        if 1 <= index <= len(final_citations) and index not in seen_indices:
            cited_indices.append(index)
            seen_indices.add(index)

    return rewritten_answer, final_citations, cited_indices


def _inject_single_citation(answer_text: str, *, citation_index: int = 1) -> str:
    blocks = answer_text.split("\n\n")
    for index, block in enumerate(blocks):
        stripped = block.strip()
        if not stripped or stripped.startswith("```"):
            continue
        if CITATION_RE.search(stripped):
            return answer_text
        blocks[index] = f"{stripped} [{citation_index}]"
        return "\n\n".join(blocks).strip()
    return f"{answer_text.rstrip()} [{citation_index}]".strip()


def _summarize_selected_citations(citations, retrieval_hits) -> list[dict[str, str | float | int]]:
    hit_by_chunk_id = {hit.chunk_id: hit for hit in retrieval_hits}
    summaries: list[dict[str, str | float | int]] = []
    for citation in citations:
        hit = hit_by_chunk_id.get(citation.chunk_id)
        summary: dict[str, str | float | int] = {
            "index": citation.index,
            "book_slug": citation.book_slug,
            "section": citation.section,
            "origin": _citation_origin(citation),
        }
        if hit is not None:
            summary["fused_score"] = round(float(hit.fused_score), 4)
            for key in ("bm25_score", "bm25_rank", "vector_score", "vector_rank"):
                if key in hit.component_scores:
                    summary[key] = round(float(hit.component_scores[key]), 4)
        summaries.append(summary)
    return summaries


def maybe_autorepair_inline_citations(
    answer_text: str,
    citations,
) -> tuple[str, bool]:
    if CITATION_RE.search(answer_text) or not citations:
        return answer_text, False

    unique_identities = {
        _citation_identity(citation)
        for citation in citations
    }
    if len(unique_identities) != 1:
        return answer_text, False
    return _inject_single_citation(answer_text, citation_index=1), True


class Part3Answerer:
    def __init__(
        self,
        settings: Settings,
        retriever: Part2Retriever,
        llm_client: LLMClient,
    ) -> None:
        self.settings = settings
        self.retriever = retriever
        self.llm_client = llm_client

    @classmethod
    def from_settings(cls, settings: Settings) -> "Part3Answerer":
        return cls(
            settings=settings,
            retriever=Part2Retriever.from_settings(settings, enable_vector=True),
            llm_client=LLMClient(settings),
        )

    def default_log_path(self) -> Path:
        return self.settings.answer_log_path

    def append_log(self, result: AnswerResult, log_path: Path | None = None) -> Path:
        target = log_path or self.default_log_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        return target

    def answer(
        self,
        query: str,
        *,
        mode: str = "ops",
        context: SessionContext | None = None,
        top_k: int = 5,
        candidate_k: int = 20,
        max_context_chunks: int = 6,
        trace_callback=None,
    ) -> AnswerResult:
        answer_started_at = time.perf_counter()
        pipeline_timings_ms: dict[str, float] = {}
        pipeline_events: list[dict] = []

        def emit(event: dict) -> None:
            payload = dict(event)
            payload.setdefault("type", "trace")
            payload.setdefault(
                "timestamp_ms",
                round((time.perf_counter() - answer_started_at) * 1000, 1),
            )
            pipeline_events.append(payload)
            if trace_callback is not None:
                trace_callback(payload)

        route_started_at = time.perf_counter()
        emit(
            {
                "step": "route_query",
                "label": "질문 라우팅 중",
                "status": "running",
                "detail": query[:180],
            }
        )
        routed_response = route_non_rag(query)
        pipeline_timings_ms["route_query"] = round(
            (time.perf_counter() - route_started_at) * 1000,
            1,
        )
        if routed_response is not None:
            emit(
                {
                    "step": "route_query",
                    "label": "질문 라우팅 완료",
                    "status": "done",
                    "detail": f"non-rag route={routed_response.route}",
                    "duration_ms": pipeline_timings_ms["route_query"],
                }
            )
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "pipeline_complete",
                    "label": "답변 생성 완료",
                    "status": "done",
                    "detail": f"총 {pipeline_timings_ms['total']}ms",
                    "duration_ms": pipeline_timings_ms["total"],
                }
            )
            return AnswerResult(
                query=query,
                mode=mode,
                answer=routed_response.answer.strip(),
                rewritten_query=query,
                response_kind=routed_response.route,
                citations=[],
                cited_indices=[],
                warnings=[],
                retrieval_trace={"route": routed_response.route, "warnings": []},
                pipeline_trace={"events": pipeline_events, "timings_ms": pipeline_timings_ms},
            )

        emit(
            {
                "step": "route_query",
                "label": "질문 라우팅 완료",
                "status": "done",
                "detail": "rag",
                "duration_ms": pipeline_timings_ms["route_query"],
            }
        )
        target_group, target_group_detail = _select_citation_group_for_query(query, context)
        if target_group is None and target_group_detail == "ambiguous_branch_reference":
            replay_selection, replay_miss_reason = None, "ambiguous_branch_reference"
        else:
            replay_selection, replay_miss_reason = _resolve_citation_replay_selection(
                query,
                context,
                target_group=target_group,
            )
        if replay_selection is not None:
            replay_result = _answer_from_citation_replay(
                query=query,
                mode=mode,
                context=context,
                replay_selection=replay_selection,
                llm_client=self.llm_client,
                answer_started_at=answer_started_at,
                pipeline_timings_ms=pipeline_timings_ms,
                emit=emit,
            )
            return replace(
                replay_result,
                pipeline_trace={
                    **replay_result.pipeline_trace,
                    "events": pipeline_events,
                    "timings_ms": dict(pipeline_timings_ms),
                },
            )
        retrieval_query = query
        if replay_miss_reason:
            emit(
                {
                    "step": "citation_replay",
                    "label": "citation replay cache miss",
                    "status": "done",
                    "detail": replay_miss_reason,
                }
            )
            if replay_miss_reason == "ambiguous_branch_reference":
                pipeline_timings_ms["total"] = round(
                    (time.perf_counter() - answer_started_at) * 1000,
                    1,
                )
                emit(
                    {
                        "step": "pipeline_complete",
                        "label": "answer complete",
                        "status": "done",
                        "detail": f"total {pipeline_timings_ms['total']}ms",
                        "duration_ms": pipeline_timings_ms["total"],
                    }
                )
                return AnswerResult(
                    query=query,
                    mode=mode,
                    answer="답변: 어떤 이전 주제로 돌아가야 하는지 불명확합니다. 돌아갈 주제나 문서 이름을 한 번만 더 지정해 주세요.",
                    rewritten_query=query,
                    response_kind="clarification",
                    citations=[],
                    cited_indices=[],
                    warnings=[],
                    retrieval_trace={"warnings": [], "citation_replay": {"status": "ambiguous"}},
                    pipeline_trace={"events": pipeline_events, "timings_ms": dict(pipeline_timings_ms)},
                )
            if replay_miss_reason == "requires_fresh_retrieval" and target_group is not None:
                retrieval_query = _augment_query_with_branch_focus(query, target_group)
                emit(
                    {
                        "step": "citation_branch",
                        "label": "citation branch focus",
                        "status": "done",
                        "detail": target_group_detail or "focused prior branch",
                    }
                )
        emit(
            {
                "step": "retrieval",
                "label": "근거 검색 시작",
                "status": "running",
                "detail": query[:180],
            }
        )
        retrieval_started_at = time.perf_counter()
        retrieval = self.retriever.retrieve(
            retrieval_query,
            context=context,
            top_k=top_k,
            candidate_k=candidate_k,
            trace_callback=emit,
        )
        pipeline_timings_ms["retrieval_total"] = round(
            (time.perf_counter() - retrieval_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "retrieval",
                "label": "근거 검색 완료",
                "status": "done",
                "detail": f"상위 근거 {len(retrieval.hits)}개",
                "duration_ms": pipeline_timings_ms["retrieval_total"],
            }
        )

        context_started_at = time.perf_counter()
        emit(
            {
                "step": "context_assembly",
                "label": "citation 컨텍스트 조립 중",
                "status": "running",
            }
        )
        context_bundle = assemble_context(
            retrieval.hits,
            query=query,
            max_chunks=max_context_chunks,
        )
        pipeline_timings_ms["context_assembly"] = round(
            (time.perf_counter() - context_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "context_assembly",
                "label": "citation 컨텍스트 조립 완료",
                "status": "done",
                "detail": f"citation {len(context_bundle.citations)}개",
                "duration_ms": pipeline_timings_ms["context_assembly"],
                "meta": {
                    "selected": len(context_bundle.citations),
                    "selected_hits": _summarize_selected_citations(
                        context_bundle.citations,
                        retrieval.hits,
                    ),
                },
            }
        )
        warnings: list[str] = []
        if not context_bundle.citations:
            warnings.append("no context citations assembled")

        prompt_started_at = time.perf_counter()
        emit(
            {
                "step": "prompt_build",
                "label": "프롬프트 조립 중",
                "status": "running",
            }
        )
        prompt_query = _augment_query_with_procedure_focus(query, context)
        if replay_miss_reason == "requires_fresh_retrieval" and target_group is not None:
            prompt_query = retrieval_query
        messages = build_messages(
            query=prompt_query,
            mode=mode,
            context_bundle=context_bundle,
            session_summary=summarize_session_context(context),
        )
        pipeline_timings_ms["prompt_build"] = round(
            (time.perf_counter() - prompt_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "prompt_build",
                "label": "프롬프트 조립 완료",
                "status": "done",
                "detail": f"messages {len(messages)}개",
                "duration_ms": pipeline_timings_ms["prompt_build"],
            }
        )

        direct_answer = None
        direct_answer_step = ""
        direct_answer_detail = ""
        if mode == "ops":
            direct_answer = _build_procedure_follow_up_answer(
                query,
                context,
                context_bundle.citations,
            )
            if direct_answer is not None:
                direct_answer_step = "procedure_follow_up"
                direct_answer_detail = "session procedure memory"
            if direct_answer is None:
                direct_answer = build_command_template_follow_up_answer(
                    query,
                    context,
                    context_bundle.citations,
                )
                if direct_answer is not None:
                    direct_answer_step = "command_template_follow_up"
                    direct_answer_detail = "session command template"
            if direct_answer is None:
                direct_answer = _build_first_turn_rbac_assignment_answer(
                    query,
                    context_bundle.citations,
                    context=context,
                )
                if direct_answer is not None:
                    direct_answer_step = "rbac_fast_lane"
                    direct_answer_detail = "first-turn rbac assignment runbook"

        llm_started_at = time.perf_counter()
        if direct_answer is not None:
            emit(
                {
                    "step": direct_answer_step or "direct_answer",
                    "label": "직접 응답 구성 완료",
                    "status": "done",
                    "detail": direct_answer_detail or "deterministic path",
                }
            )
            answer_text = direct_answer
            pipeline_timings_ms["llm_generate_total"] = 0.0
        else:
            answer_text = reshape_ops_answer_text(
                normalize_answer_text(
                    self.llm_client.generate(messages, trace_callback=emit)
                ),
                mode=mode,
            )
            answer_text = _ensure_korean_product_terms(answer_text, query=query)
            answer_text = _align_answer_to_grounded_commands(
                answer_text,
                query=query,
                citations=context_bundle.citations,
            )
            answer_text = _strip_weak_additional_guidance(
                answer_text,
                mode=mode,
                citations=context_bundle.citations,
            )
            answer_text = _strip_intro_offtopic_noise(answer_text, query=query)
            if mode == "ops" and context_bundle.citations and not CITATION_RE.search(answer_text):
                answer_text = _inject_single_citation(answer_text, citation_index=1)
            pipeline_timings_ms["llm_generate_total"] = round(
                (time.perf_counter() - llm_started_at) * 1000,
                1,
            )

        finalize_started_at = time.perf_counter()
        emit(
            {
                "step": "citation_finalize",
                "label": "citation 정리 중",
                "status": "running",
            }
        )
        answer_text, final_citations, cited_indices = finalize_citations(
            answer_text,
            context_bundle.citations,
        )
        auto_repaired_citations = False
        if not cited_indices:
            answer_text, auto_repaired_citations = maybe_autorepair_inline_citations(
                answer_text,
                context_bundle.citations,
            )
            if auto_repaired_citations:
                answer_text, final_citations, cited_indices = finalize_citations(
                    answer_text,
                    context_bundle.citations,
                )
        pipeline_timings_ms["citation_finalize"] = round(
            (time.perf_counter() - finalize_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "citation_finalize",
                "label": "citation 정리 완료",
                "status": "done",
                "detail": f"최종 citation {len(final_citations)}개",
                "duration_ms": pipeline_timings_ms["citation_finalize"],
            }
        )
        if not cited_indices:
            warnings.append("answer has no inline citations")
        elif auto_repaired_citations:
            warnings.append("inline citations auto-repaired")

        pipeline_timings_ms["total"] = round(
            (time.perf_counter() - answer_started_at) * 1000,
            1,
        )
        emit(
            {
                "step": "pipeline_complete",
                "label": "답변 생성 완료",
                "status": "done",
                "detail": f"총 {pipeline_timings_ms['total']}ms",
                "duration_ms": pipeline_timings_ms["total"],
            }
        )

        result = AnswerResult(
            query=query,
            mode=mode,
            answer=answer_text,
            rewritten_query=retrieval.rewritten_query,
            response_kind="rag",
            citations=final_citations,
            cited_indices=cited_indices,
            warnings=warnings + list(retrieval.trace.get("warnings", [])),
            retrieval_trace=retrieval.trace,
            pipeline_trace={
                "events": pipeline_events,
                "timings_ms": {
                    **retrieval.trace.get("timings_ms", {}),
                    **pipeline_timings_ms,
                },
                "selection": {
                    "selected_hits": _summarize_selected_citations(
                        context_bundle.citations,
                        retrieval.hits,
                    )
                },
            },
        )
        return result
