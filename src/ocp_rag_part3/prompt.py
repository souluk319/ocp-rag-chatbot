from __future__ import annotations

from ocp_rag_part2.query import (
    has_backup_restore_intent,
    has_certificate_monitor_intent,
    has_cluster_node_usage_intent,
    has_follow_up_reference,
    has_step_by_step_intent,
    has_project_finalizer_intent,
    has_project_terminating_intent,
    has_openshift_kubernetes_compare_intent,
    has_node_drain_intent,
    has_rbac_intent,
    has_mco_concept_intent,
    has_operator_concept_intent,
    is_generic_intro_query,
)

from .models import ContextBundle


def _step_by_step_hint(query: str, mode: str) -> str:
    if mode != "ops" or not has_step_by_step_intent(query):
        return ""
    return (
        "질문이 단계별 요청이면 답변 본문을 반드시 번호 목록 `1. 2. 3.` 형식으로 쓰고, "
        "각 단계마다 먼저 무엇을 확인하거나 수행하는지 한 줄로 말한 뒤 필요한 명령어나 YAML은 바로 아래 코드 블록으로 붙일 것."
    )


def _procedure_follow_up_hint(query: str) -> str:
    if not has_follow_up_reference(query):
        return ""
    return (
        "If session memory includes procedure steps and the user points to a numbered step or asks for the next step, "
        "answer that referenced step first, preserve the mapped command for that step, and do not restart from step 1 unless the user asks to."
    )


def _command_template_follow_up_hint(query: str) -> str:
    lowered = (query or "").lower()
    if not any(
        token in lowered
        for token in ("그 명령", "그 커맨드", "그 yaml", "serviceaccount", "group", "namespace", "대신", "바꿔", "변경")
    ):
        return ""
    return (
        "If session memory includes a structured recent command template, keep the same operation and mutate only the slots the user requested, "
        "such as namespace, subject kind, or subject name. Do not invent a new command family."
    )


def _intent_shape_hint(query: str, mode: str) -> str:
    if has_openshift_kubernetes_compare_intent(query):
        return (
            "질문이 비교형이면 '공통 기반 1문장 -> 핵심 차이 2~3개 -> 실무적으로 언제 OpenShift를 쓰는지 1문장' 순서로 답할 것."
        )
    if is_generic_intro_query(query):
        return (
            "질문이 입문형이면 '정의 1문장 -> 핵심 역할/구성 2~3개 -> 실무 포인트 1문장' 순서로 답할 것."
        )
    if mode == "ops" and has_rbac_intent(query):
        return (
            "권한/설정 질문이면 '무엇을 하는 명령인지 1문장 -> 코드 블록 -> 범위나 확인 방법 1문장' 순서로 답할 것."
        )
    if mode == "ops" and has_backup_restore_intent(query):
        return (
            "백업/복구 절차 질문이면 전제 조건을 짧게 말한 뒤, 순서대로 필요한 명령과 주의사항만 답할 것."
        )
    if mode == "ops" and has_project_finalizer_intent(query):
        return (
            "종료 중 프로젝트/finalizer 질문이면 '무엇을 확인하는지 1문장 -> 상태/남은 리소스 확인 명령 -> 필요할 때만 finalizers 정리 순서'로 답할 것."
        )
    if mode == "ops" and has_project_terminating_intent(query):
        return (
            "삭제가 멈춘 프로젝트 질문이면 '왜 Terminating에 머무는지 1문장 -> 확인 명령 -> 다음 조치 1문장' 순서로 답할 것."
        )
    if mode == "ops" and has_certificate_monitor_intent(query):
        return (
            "인증서/점검 질문이면 확인 명령을 먼저 주고, 어디를 확인하는 명령인지 한 줄로 설명할 것."
        )
    if mode == "ops" and has_cluster_node_usage_intent(query):
        return (
            "노드 리소스 확인 질문이면 '무슨 명령인지 1문장 -> 코드 블록 -> 무엇을 한 번에 보는지 1문장' 순서로 답할 것."
        )
    if mode == "ops" and has_node_drain_intent(query):
        return (
            "drain 질문이면 '무슨 작업인지 1문장 -> 예시 명령 코드 블록 -> 주의점 1~2개' 순서로 답할 것."
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
    style = (
        "운영자가 바로 실행할 수 있게 짧고 실무적으로 답변"
        if mode == "ops"
        else "초보자도 따라올 수 있게 단계적으로 설명"
    )
    system = (
        "당신은 OCP 운영/교육 가이드 RAG 챗봇이다. "
        "반드시 제공된 근거만 사용해서 답하고, 근거가 부족하면 부족하다고 말하라. "
        "추측하거나 문서에 없는 명령어, 버전, 절차를 만들지 마라. "
        "답변은 항상 '답변:'으로 시작하라. "
        "핵심 제품명과 기술명은 처음 등장할 때 한국어를 먼저 쓰고 필요하면 괄호 안에 영문을 덧붙여라. "
        "ops 모드에서 명령이나 절차를 답할 때는 bare command만 던지지 말고, "
        "먼저 무엇을 쓰는지 한 문장으로 말한 뒤 코드 블록으로 명령이나 YAML을 제시하라. "
        "질문에 '단계별' 또는 '순서대로'가 있으면 답변 본문을 반드시 번호 목록 `1. 2. 3.` 형식으로 구성하라. "
        "가능하면 바로 아래에 범위, 영향, 전제, 예시 중 필요한 것만 한 줄로 덧붙여라. "
        "필요할 때만 빈 줄 뒤에 '추가 가이드:' 섹션을 붙여라. "
        "인사말, 군더더기, 장황한 서론은 쓰지 마라. "
        "각 문장 뒤에는 직접 근거가 있는 경우에만 [1], [2]처럼 citation을 붙여라. "
        "질문이 애매하거나 여러 해석이 가능하면 많이 말하지 말고 짧게 되물어라. "
        "특히 근거가 비어 있거나 너무 약한데 질문 자체가 넓거나 모호하면, "
        "'답변: 지금은 <불명확한 점>이 불명확합니다. <짧은 확인 질문>?' 형식으로 답하라. "
        "이때 '제공된 근거가 없습니다'로만 끝내지 마라. "
        "반대로 버전이나 기능 자체가 근거에 없어서 답할 수 없는 경우에는 확인 질문으로 돌리지 말고, "
        "해당 정보가 근거에 없다고 짧게 말하라. "
        "이전 대화 맥락은 해석 힌트일 뿐이며, 현재 검색 근거가 뒷받침할 때만 사용하라. "
        "이전 맥락과 현재 근거가 충돌하거나 현재 근거가 비어 있으면 단정하지 말고 다시 확인하라."
    )
    shape_hint = _intent_shape_hint(query, mode)
    step_by_step_hint = _step_by_step_hint(query, mode)
    procedure_follow_up_hint = _procedure_follow_up_hint(query)
    command_template_follow_up_hint = _command_template_follow_up_hint(query)
    session_block = f"세션 맥락:\n{session_summary}\n\n" if session_summary else ""
    user = (
        f"모드: {mode}\n"
        f"답변 스타일: {style}\n"
        f"질문: {query}\n\n"
        f"{session_block}"
        "근거:\n"
        f"{context_bundle.prompt_context}\n\n"
        "규칙:\n"
        "- 근거에 없는 내용은 쓰지 말 것\n"
        "- citation 번호는 제공된 근거 번호만 사용할 것\n"
        "- 답변 본문은 현재 질문에 바로 답할 것\n"
        "- ops 모드에서 명령 질문이면 '한 줄 설명 -> 코드 블록 -> 짧은 범위/예시' 순서를 우선할 것\n"
        "- ops 모드에서 명령만 한 줄로 툭 던지지 말 것\n"
        "- 추가 가이드는 꼭 필요할 때만 짧게 덧붙일 것\n"
        "- 세션 맥락은 현재 질문 해석을 돕는 힌트로만 사용할 것\n"
        "- follow-up이라도 현재 검색 근거가 약하면 단정하지 말고 확인 질문을 할 것\n"
        "- 세션 맥락에 진행 중 절차가 있으면 현재 단계와 다음 단계를 섞지 말 것\n"
        "- 여러 문서가 비슷하게 경쟁하면 안전한 단정 대신 확인 질문을 우선할 것\n"
        "- 이전 맥락 때문에 현재 근거와 맞지 않는 대상을 끌어오지 말 것\n"
        "- 질문이 애매하면 무엇이 불명확한지 한 줄로 말하고, 바로 한 줄짜리 clarification 질문을 붙일 것\n"
        "- 질문이 애매한 경우 '근거가 없습니다'로만 끝내지 말 것\n"
        "- 근거 자체가 없는 negative/no-answer 상황에서는 단정 답변을 하지 말 것\n"
    )
    if step_by_step_hint:
        user += f"- 단계별 출력 규칙: {step_by_step_hint}\n"
    if procedure_follow_up_hint:
        user += f"- Procedure follow-up rule: {procedure_follow_up_hint}\n"
    if command_template_follow_up_hint:
        user += f"- Command template follow-up rule: {command_template_follow_up_hint}\n"
    if shape_hint:
        user += f"- 답변 구조 힌트: {shape_hint}\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
