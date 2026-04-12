from __future__ import annotations

import re

from play_book_studio.retrieval import SessionContext
from play_book_studio.retrieval.query import (
    has_openshift_kubernetes_compare_intent,
    has_operator_concept_intent,
    has_mco_concept_intent,
    has_pod_lifecycle_concept_intent,
    is_generic_intro_query,
)

CITATION_RE = re.compile(r"\[(\d+)\]")
ANSWER_CODE_BLOCK_RE = re.compile(r"\[CODE\]\s*\n?(.*?)\n?\[(?:/)?CODE\]", re.DOTALL)
ANSWER_TABLE_BLOCK_RE = re.compile(r"\[TABLE\]\s*\n?(.*?)\n?\[(?:/)?TABLE\]", re.DOTALL)
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
STRUCTURED_QUERY_RE = re.compile(r"[a-z0-9_.-]+/[a-z0-9_.-]+(?:=[a-z0-9_.-]+)?", re.IGNORECASE)
REPLICA_COUNT_RE = re.compile(r"(?<!\d)(\d+)\s*개")
INLINE_COMMAND_RE = re.compile(r"`([^`\n]+)`")
TRAILING_CITATIONS_RE = re.compile(r"(\s*(?:\[\d+\]\s*)+)$")
NAMESPACE_ADMIN_QUERY_RE = re.compile(
    r"(namespace|프로젝트|네임스페이스|이름공간).*(admin|관리자|어드민)|"
    r"(?:admin|관리자|어드민).*(namespace|프로젝트|네임스페이스|이름공간)",
    re.IGNORECASE,
)
RBAC_YAML_QUERY_RE = re.compile(r"(yaml|manifest|예시|rolebinding|clusterrolebinding)", re.IGNORECASE)
RBAC_VERIFY_QUERY_RE = re.compile(
    r"(확인|검증|잘 들어갔|반영|적용|명령|can-i|describe|accessreview|subjectaccessreview)",
    re.IGNORECASE,
)
RBAC_REVOKE_QUERY_RE = re.compile(r"(회수|제거|삭제|해제|remove|revoke|unbind)", re.IGNORECASE)
RBAC_CLUSTER_ADMIN_DIFF_RE = re.compile(
    r"(cluster-admin).*(차이|다르|비교)|(?:차이|다르|비교).*(cluster-admin)",
    re.IGNORECASE,
)
ACTIONABLE_GUIDE_QUERY_RE = re.compile(
    r"(어떻게|방법|절차|명령|예시|실행|확인|복구|회수|부여|디버깅|주의사항|상태|보여줘|알려줘)",
    re.IGNORECASE,
)


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
    normalized = GUIDE_HEADER_RE.sub("\n\n", normalized)
    normalized = normalized.strip()

    if not normalized:
        return "답변:"
    if normalized.startswith("답변:"):
        return normalized
    return f"답변: {normalized}"


def normalize_answer_markup_blocks(answer_text: str) -> str:
    normalized = (answer_text or "").strip()
    if not normalized:
        return normalized

    normalized = ANSWER_CODE_BLOCK_RE.sub(
        lambda match: f"\n```bash\n{match.group(1).strip()}\n```\n",
        normalized,
    )
    normalized = ANSWER_TABLE_BLOCK_RE.sub(
        lambda match: f"\n```text\n{match.group(1).strip()}\n```\n",
        normalized,
    )
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _split_trailing_citations(answer_text: str) -> tuple[str, str]:
    match = TRAILING_CITATIONS_RE.search(answer_text or "")
    if not match:
        return (answer_text or "").rstrip(), ""
    return (answer_text or "")[: match.start()].rstrip(), match.group(1).strip()


def _append_sentence_before_trailing_citations(answer_text: str, sentence: str) -> str:
    body, citations = _split_trailing_citations(answer_text)
    if citations:
        return f"{body} {sentence} {citations}".strip()
    return f"{body} {sentence}".strip()


def _needs_conceptual_guide_tail(query: str, answer_text: str) -> bool:
    if "```" in (answer_text or ""):
        return False
    if any(
        marker in (answer_text or "")
        for marker in (
            "실무에서는",
            "원하면",
            "다음에는",
            "다음에",
            "운영상 의미",
        )
    ):
        return False
    normalized = re.sub(r"\s+", " ", (answer_text or "").strip())
    if not normalized:
        return False
    sentence_count = len([part for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()])
    if sentence_count >= 3 and len(normalized) >= 180:
        return False
    return (
        is_generic_intro_query(query)
        or has_openshift_kubernetes_compare_intent(query)
        or has_operator_concept_intent(query)
        or has_mco_concept_intent(query)
        or has_pod_lifecycle_concept_intent(query)
    )


def _conceptual_guide_tail(query: str) -> str:
    if has_openshift_kubernetes_compare_intent(query):
        return "실무에서는 공통점보다 운영 기능의 차이와 사용 위치부터 보면 선택이 쉬워집니다."
    if is_generic_intro_query(query):
        return "실무에서는 이 플랫폼이 무엇을 관리하고 어떤 운영 작업을 대신해 주는지부터 보면 이해가 빨라집니다."
    if has_operator_concept_intent(query) or has_mco_concept_intent(query):
        return "실무에서는 설치보다 자동화, 업그레이드, 장애 대응에서 무엇을 맡는지 함께 보면 좋습니다."
    if has_pod_lifecycle_concept_intent(query):
        return "실무에서는 생성보다 상태 전이와 재생성 시점을 함께 보는 게 중요합니다."
    return ""


def reshape_ops_answer_text(answer_text: str, *, mode: str | None = None) -> str:
    del mode
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


def ensure_korean_product_terms(answer_text: str, *, query: str) -> str:
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
    if _needs_conceptual_guide_tail(query, updated):
        tail = _conceptual_guide_tail(query)
        if tail:
            updated = _append_sentence_before_trailing_citations(updated, tail)
    return updated


def strip_weak_additional_guidance(
    answer_text: str,
    *,
    mode: str | None = None,
    citations,
) -> str:
    del mode
    if not citations:
        return answer_text
    return WEAK_GUIDE_TAIL_RE.sub("", answer_text).strip()


def strip_intro_offtopic_noise(answer_text: str, *, query: str) -> str:
    if not (is_generic_intro_query(query) or has_openshift_kubernetes_compare_intent(query)):
        return answer_text
    cleaned = INTRO_OFFTOPIC_SENTENCE_RE.sub(" ", answer_text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def strip_structured_key_extra_guidance(
    answer_text: str,
    *,
    query: str,
    mode: str | None = None,
) -> str:
    del mode
    if not STRUCTURED_QUERY_RE.search(query):
        return answer_text
    parts = re.split(r"\n\n(?:추가 가이드|참고):", answer_text, maxsplit=1)
    if len(parts) < 2:
        return answer_text
    return parts[0].strip()


def trim_productization_noise(answer_text: str) -> str:
    cleaned = re.sub(r"\n\n\*\*4 단계: 같이 보면 좋은 문서\*\*.*$", "", answer_text, flags=re.DOTALL)
    cleaned = re.sub(r"\n\* \*\*근거:\*\* .*?(?=\n|$)", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


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
    if context.ocp_version:
        parts.append(f"- OCP 버전: {context.ocp_version}")
    return "\n".join(parts)


__all__ = [
    "ADJACENT_DUPLICATE_CITATION_RE",
    "ACTIONABLE_GUIDE_QUERY_RE",
    "ANSWER_CODE_BLOCK_RE",
    "ANSWER_HEADER_RE",
    "ANSWER_TABLE_BLOCK_RE",
    "BARE_COMMAND_ANSWER_RE",
    "CITATION_RE",
    "GREETING_PREFIXES",
    "GUIDE_HEADER_RE",
    "INLINE_COMMAND_RE",
    "INTRO_OFFTOPIC_SENTENCE_RE",
    "NAMESPACE_ADMIN_QUERY_RE",
    "REPLICA_COUNT_RE",
    "RBAC_CLUSTER_ADMIN_DIFF_RE",
    "RBAC_REVOKE_QUERY_RE",
    "RBAC_VERIFY_QUERY_RE",
    "RBAC_YAML_QUERY_RE",
    "STRUCTURED_QUERY_RE",
    "TRAILING_CITATIONS_RE",
    "WEAK_GUIDE_TAIL_RE",
    "ensure_korean_product_terms",
    "normalize_answer_markup_blocks",
    "normalize_answer_text",
    "reshape_ops_answer_text",
    "strip_intro_offtopic_noise",
    "strip_structured_key_extra_guidance",
    "strip_weak_additional_guidance",
    "summarize_session_context",
    "trim_productization_noise",
]
