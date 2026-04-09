# 채팅 세션 문맥, follow-up, 추천 질문 규칙을 담당한다.
from __future__ import annotations

from typing import Any

from play_book_studio.answering.models import AnswerResult
from play_book_studio.app.sessions import ChatSession, RUNTIME_CHAT_MODE
from play_book_studio.config.packs import default_core_pack
from play_book_studio.retrieval.models import SessionContext
from play_book_studio.retrieval.query import (
    ARCHITECTURE_RE,
    ETCD_RE,
    MCO_RE,
    OCP_RE,
    OPENSHIFT_RE,
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_logging_ambiguity,
    has_deployment_scaling_intent,
    has_doc_locator_intent,
    has_follow_up_reference,
    has_openshift_kubernetes_compare_intent,
    has_pod_lifecycle_concept_intent,
    has_pod_pending_troubleshooting_intent,
    has_rbac_intent,
    has_route_ingress_compare_intent,
    has_update_doc_locator_ambiguity,
    is_generic_intro_query,
)

DEFAULT_CORE_VERSION = default_core_pack().version


def context_with_request_overrides(
    previous: SessionContext | None,
    *,
    payload: dict[str, Any],
    mode: str,
    default_ocp_version: str = DEFAULT_CORE_VERSION,
) -> SessionContext:
    del mode
    context = SessionContext.from_dict(previous.to_dict() if previous else None)
    context.mode = RUNTIME_CHAT_MODE
    requested_version = str(payload.get("ocp_version") or "").strip()
    if requested_version:
        context.ocp_version = requested_version
    elif not context.ocp_version:
        context.ocp_version = default_ocp_version

    selected_draft_ids = payload.get("selected_draft_ids")
    if isinstance(selected_draft_ids, list):
        context.selected_draft_ids = [
            str(item).strip()
            for item in selected_draft_ids
            if str(item).strip()
        ]
    context.restrict_uploaded_sources = bool(payload.get("restrict_uploaded_sources", True))
    return context


def is_task_topic(topic: str) -> bool:
    normalized = (topic or "").strip()
    if not normalized:
        return False
    return normalized in {
        "Deployment 스케일링",
        "etcd 백업/복원",
        "RBAC",
        "Machine Config Operator",
        "OpenShift 아키텍처",
        "OpenShift",
        "Route와 Ingress 비교",
    }


def infer_explicit_topic(query: str) -> str | None:
    normalized = (query or "").strip()
    if not normalized:
        return None
    if has_deployment_scaling_intent(normalized):
        return "Deployment 스케일링"
    if has_route_ingress_compare_intent(normalized):
        return "Route와 Ingress 비교"
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


def infer_open_entities(topic: str) -> list[str]:
    normalized = (topic or "").lower()
    if "deployment" in normalized and "스케일" in normalized:
        return ["Deployment", "replicas"]
    if "etcd" in normalized:
        return ["etcd"]
    if "machine config operator" in normalized or "mco" in normalized:
        return ["Machine Config Operator"]
    if "rbac" in normalized:
        return ["RBAC"]
    if "route와 ingress 비교" in normalized:
        return ["OpenShift", "Route", "Ingress"]
    if "openshift" in normalized:
        return ["OpenShift"]
    return []


def derive_next_context(
    previous: SessionContext | None,
    *,
    query: str,
    mode: str,
    result: AnswerResult,
    default_ocp_version: str = DEFAULT_CORE_VERSION,
) -> SessionContext:
    # 멀티턴 채팅에서 세션과 follow-up 맥락을 이어 주는 helper.
    del mode
    next_context = SessionContext.from_dict(previous.to_dict() if previous else None)
    next_context.mode = RUNTIME_CHAT_MODE
    next_context.ocp_version = next_context.ocp_version or default_ocp_version
    normalized_query = (query or "").strip()
    follow_up_reference = has_follow_up_reference(normalized_query)
    prior_goal = (next_context.user_goal or "").strip()
    prior_unresolved = (next_context.unresolved_question or "").strip()

    if result.response_kind in {"smalltalk", "meta"}:
        return next_context
    if result.response_kind in {"clarification", "no_answer"}:
        if normalized_query and not follow_up_reference:
            next_context.user_goal = normalized_query
        elif not prior_goal and prior_unresolved:
            next_context.user_goal = prior_unresolved
        next_context.unresolved_question = query
        return next_context

    explicit_topic = infer_explicit_topic(query)
    if normalized_query:
        if follow_up_reference:
            next_context.user_goal = prior_goal or prior_unresolved or normalized_query
        else:
            next_context.user_goal = normalized_query
    if explicit_topic:
        next_context.current_topic = explicit_topic
        next_context.open_entities = infer_open_entities(explicit_topic)
        next_context.unresolved_question = None if result.citations else query
    elif result.citations:
        primary = result.citations[0]
        if not (follow_up_reference and is_task_topic(next_context.current_topic or "")):
            next_context.current_topic = primary.section or next_context.current_topic
        next_context.unresolved_question = None
    else:
        next_context.unresolved_question = query
    return next_context


def dedupe_suggestions(candidates: list[str], *, query: str, limit: int = 3) -> list[str]:
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


def fallback_follow_up_questions(*, query: str) -> list[str]:
    if (
        is_generic_intro_query(query)
        or has_openshift_kubernetes_compare_intent(query)
        or has_pod_lifecycle_concept_intent(query)
        or has_pod_pending_troubleshooting_intent(query)
    ):
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


def suggest_follow_up_questions(*, session: ChatSession, result: AnswerResult) -> list[str]:
    query = (result.query or "").strip()
    normalized = query.lower()
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
        return fallback_follow_up_questions(query=query)

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

    merged = dedupe_suggestions(candidates + fallback_follow_up_questions(query=query), query=query)
    return merged[:3]


__all__ = [
    "context_with_request_overrides",
    "dedupe_suggestions",
    "derive_next_context",
    "fallback_follow_up_questions",
    "infer_explicit_topic",
    "infer_open_entities",
    "is_task_topic",
    "suggest_follow_up_questions",
]
