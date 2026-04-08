# 질문을 smalltalk / meta / clarification / grounded answer로 분기하는 규칙 집합.
from __future__ import annotations

import re
from dataclasses import dataclass

from play_book_studio.config.packs import default_core_pack
from play_book_studio.retrieval.query import (
    detect_out_of_corpus_version,
    detect_unsupported_product,
    has_logging_ambiguity,
    has_multiple_entity_ambiguity,
    has_security_doc_locator_ambiguity,
    has_update_doc_locator_ambiguity,
)

DEFAULT_CORE_PACK = default_core_pack()

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


def route_non_rag(
    query: str,
    *,
    corpus_label: str = DEFAULT_CORE_PACK.product_label,
    corpus_version: str = DEFAULT_CORE_PACK.version,
) -> RoutedResponse | None:
    normalized = (query or "").strip()
    if not normalized:
        return None

    if GREETING_RE.match(normalized):
        return RoutedResponse(route="smalltalk", answer="답변: OCP 질문을 입력해 주세요.")
    if THANKS_RE.match(normalized):
        return RoutedResponse(route="smalltalk", answer="답변: 필요하면 이어서 질문해 주세요.")
    if FAREWELL_RE.match(normalized):
        return RoutedResponse(route="smalltalk", answer="답변: 필요하면 다시 불러 주세요.")
    if IDENTITY_RE.match(normalized):
        return RoutedResponse(route="meta", answer="답변: 저는 OCP 질문에 답하는 챗봇입니다.")
    if CAPABILITY_RE.search(normalized):
        return RoutedResponse(
            route="meta",
            answer="답변: OCP 개념, 운영 절차, 트러블슈팅 질문에 답할 수 있습니다.",
        )
    if has_logging_ambiguity(normalized):
        return RoutedResponse(
            route="clarification",
            answer=(
                "답변: 어떤 로그를 보는지 먼저 정해야 합니다. 애플리케이션, 인프라, 감사 로그 중 어떤 건가요?"
            ),
        )
    if has_security_doc_locator_ambiguity(normalized):
        return RoutedResponse(
            route="clarification",
            answer=(
                "답변: 보안 범위를 먼저 정해야 합니다. 플랫폼 보안, 인증·권한, 네트워크 보안 중 어디부터 볼까요?"
            ),
        )
    if has_multiple_entity_ambiguity(normalized):
        return RoutedResponse(
            route="clarification",
            answer=(
                "답변: 지금은 대상이 여러 개라 범위를 먼저 정하는 편이 좋습니다. 하나씩 질문해 주시겠어요?"
            ),
        )
    if has_update_doc_locator_ambiguity(normalized):
        return RoutedResponse(
            route="clarification",
            answer=(
                "답변: 지금은 업데이트 범위가 불명확합니다. 현재 버전, 목표 버전, 단일 클러스터 업그레이드인지부터 확인해 주시겠어요?"
            ),
        )
    out_of_corpus_version = detect_out_of_corpus_version(normalized, corpus_version=corpus_version)
    if out_of_corpus_version is not None:
        return RoutedResponse(
            route="no_answer",
            answer=(
                f"답변: 현재 코퍼스는 {corpus_label} {corpus_version} 기준이라 {out_of_corpus_version} 버전 정보는 근거로 답할 수 없습니다."
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
