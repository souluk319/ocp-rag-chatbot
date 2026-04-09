# 답변 문장 정리, 의도별 보정, 세션 요약용 helper를 모아 둔 모듈이다.

from __future__ import annotations

import re

from play_book_studio.retrieval import SessionContext
from play_book_studio.retrieval.query import (
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_cluster_node_usage_intent,
    has_command_request,
    has_corrective_follow_up,
    has_deployment_scaling_intent,
    has_node_drain_intent,
    has_openshift_kubernetes_compare_intent,
    has_pod_pending_troubleshooting_intent,
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
NAMESPACE_ADMIN_QUERY_RE = re.compile(r"(namespace|프로젝트|네임스페이스).*(admin|관리자)|(?:admin|관리자).*(namespace|프로젝트|네임스페이스)", re.IGNORECASE)


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
    return updated


def align_answer_to_grounded_commands(answer_text: str, *, query: str, citations) -> str:
    excerpt_text = "\n".join((citation.excerpt or "") for citation in citations).lower()
    updated = answer_text

    if has_cluster_node_usage_intent(query) and "oc adm top nodes" in excerpt_text:
        return (
            "답변: 클러스터 전체 노드의 CPU와 메모리 사용량은 `oc adm top nodes` 명령으로 한 번에 확인합니다 [1].\n\n"
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
        return (
            "답변: 플랫폼 인증서 만료 상태는 아래 명령으로 모니터링해 확인합니다 [1].\n\n"
            "```bash\noc adm ocp-certificates monitor-certificates\n```"
        )

    if (
        NAMESPACE_ADMIN_QUERY_RE.search(query or "")
        and ("권한" in query or "role" in query.lower())
        and "add-role-to-user admin" in excerpt_text
    ):
        return (
            "답변: 특정 프로젝트 또는 namespace에만 `admin` 권한을 주려면 "
            "`oc adm policy add-role-to-user admin <user> -n <project>` 명령으로 "
            "로컬 역할 바인딩을 추가합니다 [1].\n\n"
            "```bash\noc adm policy add-role-to-user admin <user> -n <project>\n```"
        )

    return updated


def shape_etcd_backup_answer(
    answer_text: str,
    *,
    query: str,
    citations,
) -> str:
    excerpt_text = "\n".join(
        f"{citation.section or ''}\n{citation.excerpt or ''}" for citation in citations
    ).lower()
    if "etcd" not in query.lower() or not has_backup_restore_intent(query):
        return answer_text
    if "cluster-backup.sh" not in excerpt_text and "etcdctl snapshot save" not in excerpt_text:
        return answer_text
    return (
        "답변: 컨트롤 플레인 노드에서 `oc debug --as-root node/<node_name>`로 디버그 세션을 시작하고 "
        "`chroot /host`로 전환한 뒤 `/usr/local/bin/cluster-backup.sh /home/core/assets/backup`를 실행해 "
        "etcd 스냅샷과 정적 Pod 리소스를 백업합니다 [1].\n\n"
        "```bash\n/usr/local/bin/cluster-backup.sh /home/core/assets/backup\n```"
    )


def shape_certificate_monitor_answer(
    answer_text: str,
    *,
    query: str,
    citations,
) -> str:
    excerpt_text = "\n".join((citation.excerpt or "") for citation in citations).lower()
    if not has_certificate_monitor_intent(query):
        return answer_text
    if "monitor-certificates" not in excerpt_text:
        return answer_text
    return (
        "답변: 플랫폼 인증서 만료 상태는 `oc adm ocp-certificates monitor-certificates` 명령으로 모니터링해 확인합니다 [1].\n\n"
        "```bash\noc adm ocp-certificates monitor-certificates\n```"
    )


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


def citation_marker(citations, index: int) -> str:
    if not citations:
        return ""
    bounded = index if 1 <= index <= len(citations) else 1
    return f"[{bounded}]"


def shape_pod_lifecycle_explainer(
    answer_text: str,
    *,
    query: str,
    mode: str | None = None,
    citations,
) -> str:
    del mode
    if not has_pod_lifecycle_concept_intent(query) or not citations:
        return answer_text

    primary = citations[0]
    secondary = citations[1] if len(citations) > 1 else citations[0]
    primary_ref = citation_marker(citations, 1)
    secondary_ref = citation_marker(citations, 2)

    return (
        f"답변: Pod 라이프사이클은 Pod가 생성되고 노드에 배치된 뒤 실행되다가, 종료되면 제거되거나 다시 만들어지는 흐름입니다 {primary_ref}.\n\n"
        f"- 생성/배치: Pod가 만들어지면 먼저 어느 노드에서 실행할지 결정되고 그 노드에 배치됩니다 {primary_ref}.\n"
        f"- 실행: Pod는 실행 중 직접 수정하기보다 기존 Pod를 종료하고 새 Pod를 다시 만드는 방식으로 변경을 반영합니다 {primary_ref}.\n"
        f"- 종료/교체: 종료 이유와 로그를 함께 봐야 하고, `{secondary.section}` 문서는 생성 뒤 자동으로 채워지는 특성과 예시를 같이 보여 줍니다 {secondary_ref}."
    )


def shape_pod_pending_troubleshooting(
    answer_text: str,
    *,
    query: str,
    mode: str | None = None,
    citations,
) -> str:
    del mode
    if not has_pod_pending_troubleshooting_intent(query) or not citations:
        return answer_text

    primary = citations[0]
    secondary = citations[1] if len(citations) > 1 else citations[0]
    secondary_section = secondary.section or primary.section or "이벤트 목록"
    primary_ref = citation_marker(citations, 1)
    secondary_ref = citation_marker(citations, 2)
    intro_refs = primary_ref if primary_ref == secondary_ref else f"{primary_ref}{secondary_ref}"

    return (
        f"답변: Pod가 `Pending`이면 가장 먼저 해당 Pod의 `Events`에서 `FailedScheduling` 같은 예약 실패 이유를 확인하면 됩니다 {intro_refs}.\n\n"
        f"1. `oc describe pod <pod-name> -n <pod-namespace>`로 `Events`를 보고 어떤 이유가 반복되는지 먼저 봅니다 {primary_ref}.\n"
        f"2. `{secondary_section}`처럼 node affinity, selector, taint/toleration 같은 스케줄링 제약이 맞는지 확인합니다 {secondary_ref}.\n"
        f"3. 이벤트가 리소스 부족이나 볼륨 바인딩 문제를 가리키면 그 메시지를 기준으로 다음 점검 대상을 좁히면 됩니다 {primary_ref}."
    )


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


def has_grounded_deployment_scale_citation(citations) -> bool:
    for citation in citations:
        lowered_section = (citation.section or "").lower()
        lowered_excerpt = (citation.excerpt or "").lower()
        if citation.book_slug == "cli_tools" and (
            "oc scale" in lowered_section
            or "oc scale" in lowered_excerpt
            or "deployment/" in lowered_excerpt
        ):
            return True
    return False


def extract_replica_counts(query: str) -> list[int]:
    explicit = [int(match.group(1)) for match in REPLICA_COUNT_RE.finditer(query or "")]
    if explicit:
        return explicit
    return [int(token) for token in re.findall(r"(?<![\w.])(\d+)(?![\w.])", query or "")]


def deployment_scaling_signal(query: str, context: SessionContext | None) -> bool:
    if has_deployment_scaling_intent(query):
        return True
    if context is None:
        return False
    if (context.current_topic or "").strip() == "Deployment 스케일링":
        return True
    return has_deployment_scaling_intent(context.user_goal or "")


def build_deployment_scaling_answer(
    *,
    query: str,
    context: SessionContext | None,
    citations,
) -> str | None:
    if not deployment_scaling_signal(query, context):
        return None
    if not has_grounded_deployment_scale_citation(citations):
        if has_command_request(query) or has_corrective_follow_up(query):
            return (
                "답변: 지금 검색된 근거가 `Deployment` 스케일 명령으로 바로 이어지지 않아 "
                "명령을 단정하기 어렵습니다. `deployment/my-app을 5개에서 10개로`처럼 "
                "대상 Deployment와 목표 복제본 수를 함께 다시 말해 주세요."
            )
        return None

    counts = extract_replica_counts(query)
    if not counts:
        if has_command_request(query) or has_corrective_follow_up(query):
            return (
                "답변: 지금은 몇 개로 바꾸려는지 숫자가 현재 질문에 없습니다. "
                "예를 들어 `5개에서 10개로 변경하는 명령어`처럼 목표 복제본 수를 함께 알려주세요."
            )
        return None

    target = counts[-1]
    if len(counts) >= 2:
        current = counts[0]
        command = (
            f"oc scale --current-replicas={current} --replicas={target} "
            "deployment/<deployment-name>"
        )
        return (
            "답변: 실행 중인 Deployment의 복제본 수를 바꾸려면 `oc scale` 명령으로 "
            f"현재 값 {current}개에서 목표 값 {target}개로 조정하면 됩니다 [1].\n\n"
            f"```bash\n{command}\n```\n\n"
            f"* 범위: 지정한 Deployment의 Pod 수만 {target}개로 조정됩니다.\n"
            f"* 예시: `oc scale --current-replicas={current} --replicas={target} deployment/my-app` [1]"
        )

    command = f"oc scale deployment/<deployment-name> --replicas={target}"
    return (
        "답변: 실행 중인 Deployment의 복제본 수를 바꾸려면 `oc scale` 명령으로 "
        f"목표 값을 {target}개로 지정하면 됩니다 [1].\n\n"
        f"```bash\n{command}\n```\n\n"
        f"* 범위: 지정한 Deployment의 Pod 수만 {target}개로 조정됩니다.\n"
        f"* 예시: `oc scale deployment/my-app --replicas={target}` [1]"
    )
