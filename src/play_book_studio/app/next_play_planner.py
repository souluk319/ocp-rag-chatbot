from __future__ import annotations

from dataclasses import dataclass

from play_book_studio.answering.models import AnswerResult, Citation
from play_book_studio.retrieval.query import (
    ETCD_RE,
    MCO_RE,
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_deployment_scaling_intent,
    has_doc_locator_intent,
    has_openshift_kubernetes_compare_intent,
    has_project_finalizer_intent,
    has_project_terminating_intent,
    has_rbac_intent,
    has_route_ingress_compare_intent,
    is_generic_intro_query,
)


@dataclass(slots=True)
class NextPlayPlan:
    next_action: str
    verification: str
    next_branch: str

    def as_list(self) -> list[str]:
        return [self.next_action, self.verification, self.next_branch]


def _subject_from(result: AnswerResult, citation: Citation | None, topic: str) -> str:
    query = (result.query or "").strip()
    lowered = query.lower()
    if has_route_ingress_compare_intent(query):
        return "Route와 Ingress"
    if ETCD_RE.search(query) or "etcd" in topic.lower():
        return "etcd"
    if MCO_RE.search(query) or "machine config operator" in topic.lower():
        return "Machine Config Operator"
    if "operator" in lowered:
        return "Operator"
    if topic.strip():
        return topic.strip()
    if citation is not None:
        if citation.operator_names:
            return citation.operator_names[0]
        if citation.section:
            return citation.section
    return "이 작업"


def _verification_question(subject: str, citation: Citation | None) -> str:
    if citation is not None and citation.verification_hints:
        hint = citation.verification_hints[0].strip()
        if hint:
            return f"{subject} 적용 후 검증 포인트를 기준으로 다시 정리해줘"
    return f"{subject} 적용 후 검증 방법도 알려줘"


def _branch_question(subject: str, citation: Citation | None) -> str:
    if citation is not None and (citation.error_strings or citation.chunk_type == "troubleshooting"):
        return f"{subject} 진행 중 문제가 나면 어떤 오류나 이벤트부터 봐야 해?"
    return f"{subject} 진행 중 막히면 다음에는 어디부터 확인해야 해?"


def _procedure_plan(subject: str, citation: Citation | None) -> NextPlayPlan:
    next_action = f"{subject} 실행 절차를 순서대로 다시 보여줘"
    if citation is not None and citation.cli_commands:
        next_action = f"{subject} 실행 명령만 추려서 다시 보여줘"
    return NextPlayPlan(
        next_action=next_action,
        verification=_verification_question(subject, citation),
        next_branch=_branch_question(subject, citation),
    )


def build_next_play_plan(
    *,
    session_topic: str,
    result: AnswerResult,
) -> NextPlayPlan | None:
    if result.response_kind != "rag" or not result.citations or not result.cited_indices or result.warnings:
        return None

    query = (result.query or "").strip()
    topic = (session_topic or "").strip()
    citation = result.citations[0] if result.citations else None
    subject = _subject_from(result, citation, topic)

    if has_rbac_intent(query) or topic == "RBAC":
        return NextPlayPlan(
            next_action="같은 권한을 RoleBinding YAML로 적용하는 예시도 보여줘",
            verification="권한이 제대로 들어갔는지 확인하는 명령도 알려줘",
            next_branch="권한이 너무 넓게 들어갔을 때 회수하는 방법도 알려줘",
        )
    if has_project_terminating_intent(query) or has_project_finalizer_intent(query):
        return NextPlayPlan(
            next_action="걸려 있는 리소스를 찾는 절차를 알려줘",
            verification="삭제 진행 상태를 확인하는 방법도 알려줘",
            next_branch="finalizer 제거 전에 확인해야 할 위험 요소도 알려줘",
        )
    if has_certificate_monitor_intent(query):
        return NextPlayPlan(
            next_action="인증서 상태를 점검하는 명령을 다시 정리해줘",
            verification="만료 임박 여부를 확인하는 기준도 알려줘",
            next_branch="갱신이나 점검이 실패하면 어디부터 봐야 하는지 알려줘",
        )
    if ETCD_RE.search(query) or "etcd" in topic.lower():
        if has_backup_restore_intent(query) or "백업" in topic or "복원" in topic:
            return NextPlayPlan(
                next_action="etcd 백업 명령과 순서를 다시 정리해줘",
                verification="백업 파일이 정상적으로 생성됐는지 확인하는 방법도 알려줘",
                next_branch="백업이나 복원 중 문제가 나면 어디부터 확인해야 해?",
            )
        return NextPlayPlan(
            next_action="etcd 운영에서 실제로 먼저 해야 하는 작업 순서를 알려줘",
            verification="etcd 상태를 확인하는 기본 점검 방법도 알려줘",
            next_branch="장애가 나면 어떤 증상부터 확인해야 하는지 알려줘",
        )
    if MCO_RE.search(query) or "machine config operator" in topic.lower():
        return NextPlayPlan(
            next_action="MachineConfigPool 상태를 확인하는 명령을 알려줘",
            verification="노드에 변경이 반영됐는지 확인하는 방법도 알려줘",
            next_branch="MCO가 Degraded일 때 어디부터 봐야 하는지 알려줘",
        )
    if has_deployment_scaling_intent(query):
        return NextPlayPlan(
            next_action="deployment replicas를 바로 변경하는 명령 예시를 보여줘",
            verification="적용 후 replicas가 바뀌었는지 확인하는 명령도 알려줘",
            next_branch="스케일이 반영되지 않으면 어디부터 확인해야 해?",
        )
    if has_route_ingress_compare_intent(query):
        return NextPlayPlan(
            next_action="OpenShift에서 Route를 실제로 만드는 예시를 보여줘",
            verification="노출이 정상인지 확인하는 명령과 체크포인트를 알려줘",
            next_branch="접속이 안 되거나 503이면 어디부터 봐야 하는지 알려줘",
        )
    if has_openshift_kubernetes_compare_intent(query) or is_generic_intro_query(query):
        return NextPlayPlan(
            next_action="실무에서 가장 먼저 하는 OpenShift 작업 3가지를 알려줘",
            verification="클러스터 기본 상태를 확인하는 명령도 알려줘",
            next_branch="운영 중 문제가 생기면 어떤 순서로 접근하는지 알려줘",
        )
    if has_doc_locator_intent(query):
        return NextPlayPlan(
            next_action="이 문서 기준으로 바로 실행할 절차만 추려줘",
            verification="실행 후 검증 포인트도 같이 정리해줘",
            next_branch="실패 시 다음 분기까지 같이 정리해줘",
        )
    if citation is not None and citation.chunk_type in {"procedure", "command", "troubleshooting"}:
        return _procedure_plan(subject, citation)
    if citation is not None and citation.operator_names:
        operator_subject = citation.operator_names[0].strip() or subject
        return NextPlayPlan(
            next_action=f"{operator_subject} 설치나 적용 다음에 무엇을 확인해야 해?",
            verification=f"{operator_subject} 정상 동작 여부를 어디서 확인해?",
            next_branch=f"{operator_subject} 관련 문제가 나면 어디부터 봐야 해?",
        )
    return NextPlayPlan(
        next_action=f"{subject} 관련 다음 작업을 이어서 알려줘",
        verification=_verification_question(subject, citation),
        next_branch=_branch_question(subject, citation),
    )
