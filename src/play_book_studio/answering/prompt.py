"""grounded answering용 prompt를 조립한다.

retrieval이 모델에게 무엇을 보여줄지 결정한다면, 이 파일은 그 근거를 가지고
어떻게 답하게 할지를 결정한다.
"""

from __future__ import annotations

from play_book_studio.retrieval.query import (
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_cluster_node_usage_intent,
    has_crash_loop_troubleshooting_intent,
    has_deployment_scaling_intent,
    has_project_finalizer_intent,
    has_project_terminating_intent,
    has_openshift_kubernetes_compare_intent,
    has_node_drain_intent,
    has_pod_lifecycle_concept_intent,
    has_pod_pending_troubleshooting_intent,
    has_rbac_intent,
    has_mco_concept_intent,
    has_operator_concept_intent,
    is_generic_intro_query,
)

from .models import ContextBundle


def _intent_shape_hint(query: str) -> str:
    if has_openshift_kubernetes_compare_intent(query):
        return (
            "질문이 비교형이면 '공통 기반 1문장 -> 핵심 차이 2~3개 -> 실무적으로 언제 OpenShift를 쓰는지 1문장' 순서로 답할 것."
        )
    if is_generic_intro_query(query):
        return (
            "질문이 입문형이면 '정의 1문장 -> 핵심 역할/구성 2~3개 -> 실무 포인트 1문장' 순서로 답할 것."
        )
    if has_rbac_intent(query):
        return (
            "권한/설정 질문이면 '무엇을 하는 명령인지 1문장 -> 코드 블록 -> 범위나 확인 방법 1문장' 순서로 답할 것."
        )
    if has_backup_restore_intent(query):
        return (
            "백업/복구 절차 질문이면 전제 조건을 짧게 말한 뒤, 순서대로 필요한 명령과 주의사항만 답할 것."
        )
    if has_project_finalizer_intent(query):
        return (
            "종료 중 프로젝트/finalizer 질문이면 '무엇을 확인하는지 1문장 -> 상태/남은 리소스 확인 명령 -> 필요할 때만 finalizers 정리 순서'로 답할 것."
        )
    if has_project_terminating_intent(query):
        return (
            "삭제가 멈춘 프로젝트 질문이면 '왜 Terminating에 머무는지 1문장 -> 확인 명령 -> 다음 조치 1문장' 순서로 답할 것."
        )
    if has_certificate_monitor_intent(query):
        return (
            "인증서/점검 질문이면 확인 명령을 먼저 주고, 어디를 확인하는 명령인지 한 줄로 설명할 것."
        )
    if has_cluster_node_usage_intent(query):
        return (
            "노드 리소스 확인 질문이면 '무슨 명령인지 1문장 -> 코드 블록 -> 무엇을 한 번에 보는지 1문장' 순서로 답할 것."
        )
    if has_node_drain_intent(query):
        return (
            "drain 질문이면 '무슨 작업인지 1문장 -> 예시 명령 코드 블록 -> 주의점 1~2개' 순서로 답할 것."
        )
    if has_deployment_scaling_intent(query):
        return (
            "Deployment 스케일링 질문이면 대상 리소스가 Deployment인지 DeploymentConfig인지 근거에 맞춰 구분하고, '무엇을 바꾸는 명령인지 1문장 -> oc scale 코드 블록 -> 범위/예시 1문장' 순서로 답할 것."
        )
    if has_pod_pending_troubleshooting_intent(query):
        return (
            "Pod Pending 질문이면 '이벤트로 FailedScheduling 이유 확인 -> node affinity/selector 같은 스케줄링 제약 확인 -> 이벤트에 드러난 리소스/노드 상태 원인 확인' 순서로 답할 것. 첫 단계는 Pod Events 확인으로 시작할 것."
        )
    if has_crash_loop_troubleshooting_intent(query):
        return (
            "CrashLoopBackOff 질문이면 '현재 상태와 이벤트 확인 -> 로그와 이전 종료 원인 확인 -> 이미지/프로브/설정 확인 -> OOM 같은 대표 원인 분기' 순서로 답할 것. OOM은 가능한 원인 중 하나로 설명하되 첫 문장에서 단정하지 말 것."
        )
    if has_pod_lifecycle_concept_intent(query):
        return (
            "Pod lifecycle 질문이면 '정의 1문장 -> 생성/실행/종료 흐름 2~3문장 -> 변경 불가능성과 운영상 의미 1문장' 순서로 답할 것."
        )
    if has_operator_concept_intent(query) or has_mco_concept_intent(query):
        return (
            "개념 질문이면 정의 1문장 뒤에, 실제로 무엇을 관리하거나 자동화하는지 2~3문장으로 설명하고 예시를 짧게 붙일 것."
        )
    return ""


def build_messages(
    *,
    query: str,
    mode: str,
    context_bundle: ContextBundle,
    session_summary: str = "",
) -> list[dict[str, str]]:
    # prompt 조립을 최대한 결정적으로 유지해야, 답변 회귀가 생겼을 때
    # 원인을 숨은 prompt drift가 아니라 retrieval/context 변화로 좁힐 수 있다.
    del mode
    style = (
        "핵심부터 짧고 분명하게 답하되, 명령/절차 질문은 바로 실행 흐름이 보이게 쓰고 "
        "개념 질문은 정의와 흐름만 간결하게 설명하며, 트러블슈팅 질문은 확인 순서를 짧게 분명히 답변"
    )
    system = (
        "당신은 OCP 운영/교육 가이드 RAG 챗봇이다. "
        "반드시 제공된 근거만 사용해서 답하고, 근거가 부족하면 부족하다고 말하라. "
        "추측하거나 문서에 없는 명령어, 버전, 절차를 만들지 마라. "
        "답변은 항상 '답변:'으로 시작하라. "
        "핵심 제품명과 기술명은 처음 등장할 때 한국어를 먼저 쓰고 필요하면 괄호 안에 영문을 덧붙여라. "
        "질문이 한국어면 답변 서술도 자연스러운 한국어 문장으로만 쓰고, CLI 옵션/상태명/고유명사 외의 불필요한 영문 단어를 섞지 마라. "
        "명령이나 절차를 답할 때는 bare command만 던지지 말고, "
        "먼저 무엇을 쓰는지 한 문장으로 말한 뒤 코드 블록으로 명령이나 YAML을 제시하라. "
        "가능하면 바로 아래에 범위, 영향, 전제, 예시 중 필요한 것만 한 줄로 덧붙여라. "
        "개념 질문이나 트러블슈팅 질문에서는 필요한 흐름과 이유와 확인 포인트를 충분히 설명하라. "
        "다만 길게 늘이지 말고 짧게 정리하라. "
        "답변은 보통 3개 이하의 짧은 문단이나 bullet 안에서 끝내라. "
        "추가 가이드라는 제목은 만들지 말고, 정말 필요할 때만 마지막에 한 줄만 덧붙여라. "
        "인사말, 군더더기, 장황한 서론은 쓰지 마라. "
        "근거 문서에 포함된 [CODE], [/CODE], [TABLE], [/TABLE] 같은 내부 태그를 답변에 그대로 노출하지 말고, 일반 markdown 코드 블록이나 자연어 설명으로 바꿔라. "
        "citation은 꼭 필요한 문장이나 문단 끝에만 [1], [2]처럼 붙여라. 같은 문단의 모든 문장에 반복하지 마라. "
        "질문이 애매하거나 여러 해석이 가능하면 많이 말하지 말고 짧게 되물어라. "
        "특히 근거가 비어 있거나 너무 약한데 질문 자체가 넓거나 모호하면, "
        "'답변: 지금은 <불명확한 점>이 불명확합니다. <짧은 확인 질문>?' 형식으로 답하라. "
        "이때 '제공된 근거가 없습니다'로만 끝내지 마라. "
        "반대로 버전이나 기능 자체가 근거에 없어서 답할 수 없는 경우에는 확인 질문으로 돌리지 말고, "
        "해당 정보가 근거에 없다고 짧게 말하라. "
        "이전 대화 맥락은 해석 힌트일 뿐이며, 현재 검색 근거가 뒷받침할 때만 사용하라. "
        "이전 맥락과 현재 근거가 충돌하거나 현재 근거가 비어 있으면 단정하지 말고 다시 확인하라."
    )
    shape_hint = _intent_shape_hint(query)
    session_block = f"세션 맥락:\n{session_summary}\n\n" if session_summary else ""
    user = (
        f"답변 스타일: {style}\n"
        f"질문: {query}\n\n"
        f"{session_block}"
        "근거:\n"
        f"{context_bundle.prompt_context}\n\n"
        "규칙:\n"
        "- 근거에 없는 내용은 쓰지 말 것\n"
        "- citation 번호는 제공된 근거 번호만 사용할 것\n"
        "- 답변 본문은 현재 질문에 바로 답할 것\n"
        "- 근거에 없는 예시 명령, 가상의 리소스명, 추정 절차를 새로 만들지 말 것\n"
        "- 특히 annotation/key/flag 값을 묻는 질문에서는 값과 근거만 답하고, 문서에 없는 후속 명령 예시는 덧붙이지 말 것\n"
        "- 명령 질문이면 '한 줄 설명 -> 코드 블록 -> 짧은 범위/예시' 순서를 우선할 것\n"
        "- 명령만 한 줄로 툭 던지지 말 것\n"
        "- 개념 질문과 트러블슈팅 질문에서는 단계마다 왜 필요한지와 무엇을 확인해야 하는지 1~2문장씩 덧붙일 것\n"
        "- 다만 필요 이상으로 길게 늘이지 말고 짧게 정리할 것\n"
        "- 질문이 한국어면 서술 문장은 한국어로만 쓰고, 영문은 명령어/옵션/상태명/고유명사처럼 꼭 필요한 경우에만 쓸 것\n"
        "- [CODE], [/CODE], [TABLE], [/TABLE] 같은 내부 태그를 답변에 그대로 쓰지 말 것\n"
        "- 추가 가이드는 꼭 필요할 때만 마지막 한 줄로만 덧붙일 것\n"
        "- citation은 핵심 문장이나 문단 끝에만 붙일 것\n"
        "- 같은 단락의 모든 문장에 citation을 반복하지 말 것\n"
        "- 답변은 가능하면 3개 이하의 짧은 문단이나 bullet 안에서 끝낼 것\n"
        "- 세션 맥락은 현재 질문 해석을 돕는 힌트로만 사용할 것\n"
        "- follow-up이라도 현재 검색 근거가 약하면 단정하지 말고 확인 질문을 할 것\n"
        "- 여러 문서가 비슷하게 경쟁하면 안전한 단정 대신 확인 질문을 우선할 것\n"
        "- 이전 맥락 때문에 현재 근거와 맞지 않는 대상을 끌어오지 말 것\n"
        "- 질문이 애매하면 무엇이 불명확한지 한 줄로 말하고, 바로 한 줄짜리 clarification 질문을 붙일 것\n"
        "- 질문이 애매한 경우 '근거가 없습니다'로만 끝내지 말 것\n"
        "- 근거 자체가 없는 negative/no-answer 상황에서는 단정 답변을 하지 말 것\n"
    )
    if shape_hint:
        user += f"- 답변 구조 힌트: {shape_hint}\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
