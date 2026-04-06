from __future__ import annotations

import re
from dataclasses import dataclass

from ocp_rag.retrieval.query import (
    detect_out_of_corpus_version,
    detect_unsupported_product,
    has_logging_ambiguity,
    has_update_doc_locator_ambiguity,
)


GREETING_RE = re.compile(
    r"^\s*(안녕(?:하세요)?|하이|ㅎㅇ|hello|hi|hey|반가워|반갑습니다)(?:[!?.~\s]*)$",
    re.IGNORECASE,
)
THANKS_RE = re.compile(
    r"^\s*(고마워|감사(?:합니다|해요)?|thanks|thank you)(?:[!?.~\s]*)$",
    re.IGNORECASE,
)
FAREWELL_RE = re.compile(
    r"^\s*(잘가|바이|bye|수고해|나중에 봐|이따 봐)(?:[!?.~\s]*)$",
    re.IGNORECASE,
)
IDENTITY_RE = re.compile(
    r"^\s*(넌 누구야|너 누구야|누구세요|정체가 뭐야|뭐하는 챗봇이야|뭐하는 봇이야)(?:[!?.~\s]*)$",
    re.IGNORECASE,
)
CAPABILITY_RE = re.compile(
    r"(이 챗봇|너|당신|봇).*(뭐 할 수|무엇을 할 수|뭘 도와|도와줄 수)|"
    r"(뭐 할 수 있어|무엇을 할 수 있어|사용법이 뭐야|어떤 질문을 할 수 있어)",
    re.IGNORECASE,
)


@dataclass(slots=True)
class RoutedResponse:
    route: str
    answer: str


def route_non_rag(query: str) -> RoutedResponse | None:
    normalized = (query or "").strip()
    if not normalized:
        return None

    if GREETING_RE.match(normalized):
        return RoutedResponse(
            route="smalltalk",
            answer=(
                "답변: 안녕하세요. OCP 운영 절차, 개념 설명, 관련 문서 위치를 "
                "한국어 근거와 함께 도와드릴게요. 궁금한 내용을 편하게 물어보세요."
            ),
        )
    if THANKS_RE.match(normalized):
        return RoutedResponse(
            route="smalltalk",
            answer=(
                "답변: 도움이 되었다면 다행입니다. 이어서 OCP 관련 질문을 주시면 "
                "근거와 함께 바로 도와드릴게요."
            ),
        )
    if FAREWELL_RE.match(normalized):
        return RoutedResponse(
            route="smalltalk",
            answer=(
                "답변: 알겠습니다. 다음에 OCP 질문이 생기면 근거와 함께 이어서 도와드리겠습니다."
            ),
        )
    if IDENTITY_RE.match(normalized):
        return RoutedResponse(
            route="meta",
            answer=(
                "답변: 저는 OCP 운영/교육 가이드 RAG 챗봇입니다. "
                "OpenShift 개념 설명, 운영 절차, 관련 문서 위치 찾기를 "
                "한국어 근거와 함께 도와드릴 수 있습니다."
            ),
        )
    if CAPABILITY_RE.search(normalized):
        return RoutedResponse(
            route="meta",
            answer=(
                "답변: 이 챗봇은 OCP 개념 설명, 운영 절차 안내, 문서 위치 찾기, "
                "follow-up 질문 해석을 도와줄 수 있습니다. 실제 OCP 질문을 주시면 "
                "가능한 경우 한국어 출처와 함께 답하겠습니다."
            ),
        )
    if has_logging_ambiguity(normalized):
        return RoutedResponse(
            route="clarification",
            answer=(
                "답변: 지금은 어떤 로그를 보려는지 불명확합니다. "
                "애플리케이션 로그, 인프라 로그, 감사 로그 중 무엇을 찾으시나요?"
            ),
        )
    if has_update_doc_locator_ambiguity(normalized):
        return RoutedResponse(
            route="clarification",
            answer=(
                "답변: 지금은 어떤 업데이트를 찾는지 범위가 불명확합니다. "
                "현재 버전과 목표 버전, 그리고 단일 클러스터 업그레이드인지부터 알려주실 수 있나요?"
            ),
        )
    out_of_corpus_version = detect_out_of_corpus_version(normalized)
    if out_of_corpus_version is not None:
        return RoutedResponse(
            route="no_answer",
            answer=(
                f"답변: 현재 코퍼스는 OpenShift 4.20 기준이라 {out_of_corpus_version} 버전 정보는 근거로 답할 수 없습니다."
            ),
        )
    unsupported_product = detect_unsupported_product(normalized)
    if unsupported_product is not None:
        return RoutedResponse(
            route="no_answer",
            answer=(
                f"답변: 현재 코퍼스에는 {unsupported_product} 관련 설치나 비교 절차를 답할 근거가 없습니다."
            ),
        )
    return None
