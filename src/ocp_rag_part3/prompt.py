from __future__ import annotations

from .models import ContextBundle


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
        "- 추가 가이드는 꼭 필요할 때만 짧게 덧붙일 것\n"
        "- 세션 맥락은 현재 질문 해석을 돕는 힌트로만 사용할 것\n"
        "- follow-up이라도 현재 검색 근거가 약하면 단정하지 말고 확인 질문을 할 것\n"
        "- 여러 문서가 비슷하게 경쟁하면 안전한 단정 대신 확인 질문을 우선할 것\n"
        "- 이전 맥락 때문에 현재 근거와 맞지 않는 대상을 끌어오지 말 것\n"
        "- 질문이 애매하면 무엇이 불명확한지 한 줄로 말하고, 바로 한 줄짜리 clarification 질문을 붙일 것\n"
        "- 질문이 애매한 경우 '근거가 없습니다'로만 끝내지 말 것\n"
        "- 근거 자체가 없는 negative/no-answer 상황에서는 단정 답변을 하지 말 것\n"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
