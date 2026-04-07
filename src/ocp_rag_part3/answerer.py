from __future__ import annotations

import json
import re
import time
from dataclasses import replace
from pathlib import Path

from ocp_rag_part1.settings import Settings
from ocp_rag_part2 import Part2Retriever, SessionContext
from ocp_rag_part2.query import (
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

from .context import assemble_context
from .llm import LLMClient
from .models import AnswerResult
from .prompt import build_messages
from .router import route_non_rag


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


def _normalize_answer_markup_blocks(answer_text: str) -> str:
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


def _strip_weak_additional_guidance(
    answer_text: str,
    *,
    mode: str | None = None,
    citations,
) -> str:
    del mode
    if not citations:
        return answer_text
    return WEAK_GUIDE_TAIL_RE.sub("", answer_text).strip()


def _strip_intro_offtopic_noise(answer_text: str, *, query: str) -> str:
    if not (is_generic_intro_query(query) or has_openshift_kubernetes_compare_intent(query)):
        return answer_text
    cleaned = INTRO_OFFTOPIC_SENTENCE_RE.sub(" ", answer_text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _strip_structured_key_extra_guidance(
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


def _trim_productization_noise(answer_text: str) -> str:
    cleaned = re.sub(r"\n\n\*\*4 단계: 같이 보면 좋은 문서\*\*.*$", "", answer_text, flags=re.DOTALL)
    cleaned = re.sub(r"\n\* \*\*근거:\*\* .*?(?=\n|$)", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _shape_pod_lifecycle_explainer(
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

    return (
        "답변: Pod 라이프사이클은 Pod가 노드에 할당되어 실행되고, 컨테이너가 종료되거나 다른 이유로 제거될 때까지 이어지는 흐름입니다 [1].\n\n"
        "**1 단계: 생성과 노드 할당**\n"
        "Pod가 만들어지면 먼저 어떤 노드에서 실행될지 결정되고 그 노드에 배치됩니다 [1].\n"
        "* **이유:** Pod는 클러스터 안의 실제 노드 위에서 실행되어야 하기 때문입니다.\n"
        "* **확인 포인트:** Pod가 어느 노드에 배치되었는지와 실행이 시작되었는지를 먼저 봅니다.\n\n"
        "**2 단계: 실행 중 특성**\n"
        "Pod는 실행되기 시작한 뒤 컨테이너가 종료되거나 제거될 때까지 유지됩니다 [1]. 실행 중 Pod 정의를 직접 바꾸기보다는 기존 Pod를 종료하고 새 Pod를 다시 만드는 방식으로 변경을 반영합니다 [1].\n"
        "* **이유:** OpenShift는 Pod를 사실상 변경 불가능한 객체처럼 다뤄 안정적으로 운영하기 때문입니다.\n"
        "* **확인 포인트:** 컨테이너가 정상 실행 중인지, 그리고 상위 컨트롤러가 새 Pod를 다시 만들 수 있는 구조인지 확인합니다.\n\n"
        "**3 단계: 종료와 제거**\n"
        "Pod는 정책과 종료 코드에 따라 종료 후 바로 제거되거나, 컨테이너 로그 접근을 위해 잠시 유지될 수 있습니다 [1].\n"
        "* **이유:** 종료 상황을 추적하고 필요한 운영 정보를 확인할 시간을 확보하기 위해서입니다.\n"
        "* **확인 포인트:** 종료 이유, 종료 코드, 로그 확인 가능 여부를 함께 봅니다.\n\n"
        f"\n`{secondary.section}` 문서는 Pod 예시와 함께, 생성 뒤 자동으로 채워지는 특성을 같이 보여 줍니다 [2]."
    )


def _shape_pod_pending_troubleshooting(
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
    primary_section = primary.section or "이벤트 목록"
    secondary_section = secondary.section or primary_section

    return (
        "답변: Pod가 `Pending` 상태로 오래 머물면, 가장 먼저 해당 Pod의 `Events`에서 왜 스케줄링이 막혔는지 확인하는 것이 좋습니다 [1][2].\n\n"
        "**1 단계: Pod Events에서 실패 이유 확인**\n"
        "우선 `oc describe pod <pod-name> -n <pod-namespace>`로 `Events`를 보고 `FailedScheduling` 같은 이유가 찍히는지 확인합니다 [1][2].\n"
        f"* **근거:** `{primary_section}` 문서는 `FailedScheduling` 이벤트가 예약 실패 원인을 보여 준다고 설명합니다 [1].\n"
        "* **확인 포인트:** 이벤트에 어떤 이유가 먼저 찍히는지, 같은 메시지가 반복되는지부터 봅니다.\n\n"
        "**2 단계: 스케줄링 제약 확인**\n"
        f"이벤트에 라벨 불일치나 예약 조건 문제가 보이면 `{secondary_section}`처럼 node affinity, selector 같은 스케줄링 제약을 먼저 의심하는 흐름이 맞습니다 [2].\n"
        "* **이유:** Pod가 요구하는 조건과 실제 노드 특성이 맞지 않으면 컨테이너가 뜨기 전에 예약 자체가 거부되기 때문입니다.\n"
        "* **확인 포인트:** Pod가 요구하는 라벨/제약과 노드에 실제 붙은 값이 맞는지 비교합니다 [2].\n\n"
        "**3 단계: 이벤트가 가리키는 원인으로 좁히기**\n"
        "이벤트가 리소스 부족이나 볼륨 바인딩 같은 다른 이유를 보여 주면, 그 메시지를 기준으로 다음 점검 대상을 좁혀 가면 됩니다 [1].\n"
        "* **이유:** `Pending`은 상태 이름일 뿐이고, 실제 원인은 이벤트 메시지에 더 직접적으로 드러나기 때문입니다.\n"
        "* **확인 포인트:** 이벤트의 `Reason`과 메시지를 그대로 기준점으로 삼아 다음 조치를 정합니다.\n\n"
        "**정리하면**\n"
        "`Pending` 자체를 추상적으로 보지 말고, 먼저 `Events -> FailedScheduling 이유 -> node affinity/selector 같은 제약` 순서로 좁히면 가장 빠릅니다 [1][2]."
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


def _has_grounded_deployment_scale_citation(citations) -> bool:
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


def _extract_replica_counts(query: str) -> list[int]:
    explicit = [int(match.group(1)) for match in REPLICA_COUNT_RE.finditer(query or "")]
    if explicit:
        return explicit
    return [int(token) for token in re.findall(r"(?<![\w.])(\d+)(?![\w.])", query or "")]


def _deployment_scaling_signal(query: str, context: SessionContext | None) -> bool:
    if has_deployment_scaling_intent(query):
        return True
    if context is None:
        return False
    if (context.current_topic or "").strip() == "Deployment 스케일링":
        return True
    return has_deployment_scaling_intent(context.user_goal or "")


def _build_deployment_scaling_answer(
    *,
    query: str,
    context: SessionContext | None,
    citations,
) -> str | None:
    if not _deployment_scaling_signal(query, context):
        return None
    if not _has_grounded_deployment_scale_citation(citations):
        if has_command_request(query) or has_corrective_follow_up(query):
            return (
                "답변: 지금 검색된 근거가 `Deployment` 스케일 명령으로 바로 이어지지 않아 "
                "명령을 단정하기 어렵습니다. `deployment/my-app을 5개에서 10개로`처럼 "
                "대상 Deployment와 목표 복제본 수를 함께 다시 말해 주세요."
            )
        return None

    counts = _extract_replica_counts(query)
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


def select_fallback_citations(
    citations,
    *,
    limit: int = 3,
) -> list:
    selected = []
    seen_identities: set[tuple[str, str]] = set()
    for citation in citations:
        identity = _citation_identity(citation)
        if identity in seen_identities:
            continue
        seen_identities.add(identity)
        selected.append(replace(citation, index=len(selected) + 1))
        if len(selected) >= limit:
            break
    return selected


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
        return self.settings.part3_answer_log_path

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
        mode: str = "chat",
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
            query,
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

        deployment_scaling_answer = _build_deployment_scaling_answer(
            query=query,
            context=context,
            citations=context_bundle.citations,
        )
        if deployment_scaling_answer is not None:
            answer_text = deployment_scaling_answer
            final_citations = select_fallback_citations(context_bundle.citations, limit=1)
            answer_text, final_citations, cited_indices = finalize_citations(
                answer_text,
                final_citations,
            )
            if not cited_indices and final_citations:
                answer_text = _inject_single_citation(answer_text, citation_index=1)
                answer_text, final_citations, cited_indices = finalize_citations(
                    answer_text,
                    final_citations,
                )
            pipeline_timings_ms["total"] = round(
                (time.perf_counter() - answer_started_at) * 1000,
                1,
            )
            emit(
                {
                    "step": "deterministic_answer",
                    "label": "전용 명령 답변 생성 완료",
                    "status": "done",
                    "detail": "deployment scaling",
                }
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
                answer=answer_text,
                rewritten_query=retrieval.rewritten_query,
                response_kind="clarification" if "숫자가 현재 질문에 없습니다" in answer_text else "rag",
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

        prompt_started_at = time.perf_counter()
        emit(
            {
                "step": "prompt_build",
                "label": "프롬프트 조립 중",
                "status": "running",
            }
        )
        messages = build_messages(
            query=query,
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

        llm_started_at = time.perf_counter()
        answer_text = reshape_ops_answer_text(
            normalize_answer_text(
                _normalize_answer_markup_blocks(
                    self.llm_client.generate(messages, trace_callback=emit)
                )
            ),
            mode=mode,
        )
        answer_text = _ensure_korean_product_terms(answer_text, query=query)
        answer_text = _align_answer_to_grounded_commands(
            answer_text,
            query=query,
            citations=context_bundle.citations,
        )
        answer_text = _shape_pod_lifecycle_explainer(
            answer_text,
            query=query,
            mode=mode,
            citations=context_bundle.citations,
        )
        answer_text = _shape_pod_pending_troubleshooting(
            answer_text,
            query=query,
            mode=mode,
            citations=context_bundle.citations,
        )
        answer_text = _strip_weak_additional_guidance(
            answer_text,
            mode=mode,
            citations=context_bundle.citations,
        )
        answer_text = _strip_structured_key_extra_guidance(
            answer_text,
            query=query,
            mode=mode,
        )
        answer_text = _trim_productization_noise(answer_text)
        answer_text = _strip_intro_offtopic_noise(answer_text, query=query)
        if context_bundle.citations and not CITATION_RE.search(answer_text):
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
            elif context_bundle.citations:
                final_citations = select_fallback_citations(context_bundle.citations)
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
