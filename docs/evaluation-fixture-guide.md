# Evaluation Fixture Guide

이 문서는 OCP RAG 챗봇의 고정 평가셋 뼈대를 정의한다. 목적은 검색 품질, rewrite 안정성, 답변 형식 안전성을 수동 감상 대신 반복 가능한 기준으로 고정하는 것이다.

## 파일

- `scripts/eval-fixture.seed.json`
- `scripts/eval-fixture.schema.json`

## 설계 원칙

- 질문은 `overview`, `education`, `operations`, `troubleshooting` 네 클래스로 분리한다.
- 제품 모드는 `education`과 `operations` 두 축으로 둔다.
- fixture 한 건은 "대화 맥락 + 기대 retrieval + 기대 answer"를 같이 가진다.
- 자동 평가 스크립트가 아직 없어도, 사람이 읽고 검토할 수 있어야 한다.
- 이후 자동화 시 line-by-line 판정이 가능하도록 JSON 기반으로 유지한다.

## fixture 한 건의 의미

- `id`: 고정 식별자. 추후 대시보드와 회귀 리포트의 기본 키로 사용.
- `mode_hint`: 제품 모드 의도. `education` 또는 `operations`.
- `query_class`: 평가 질문 분류.
- `conversation`: 마지막 `user` 메시지가 실제 평가 대상 질문이다. 앞선 turn은 rewrite와 session 처리 검증에 사용한다.
- `expected.rewrite`: rewrite가 바뀌어야 하는지, 어떤 토큰은 반드시 살아 있어야 하는지 명시.
- `expected.retrieval.source_any`: top-k 안에 최소 하나는 포함돼야 하는 gold source.
- `expected.retrieval.source_prefer_top3`: 가능하면 top3 안에 올라와야 하는 stronger signal.
- `expected.retrieval.source_exclude_top3`: generic 문서가 잘못 상위에 올라오는 회귀를 막는 용도.
- `expected.answer`: 정답 자체보다는 답변의 구조적 요구를 명시한다.

## 권장 판정 규칙

자동 평가로 확장할 때는 아래 규칙을 권장한다.

1. Retrieval pass
   - `source_any` 중 하나 이상이 top-k에 있으면 pass.
   - `source_prefer_top3`가 있으면 top3 기준 보조 점수로 계산.
   - `source_exclude_top3`가 top3에 있으면 hard fail 또는 감점.
2. Rewrite pass
   - `should_change=true`이면 원문과 동일할 때 fail.
   - `must_include_any`가 있으면 rewrite 문자열에 최소 하나 이상 포함돼야 한다.
3. Answer pass
   - `must_not_include_any`는 하나라도 나오면 fail.
   - `citation_required=true`이면 실제 source filename이 답변 또는 response metadata에 남아 있어야 한다.
   - `requires_step_list=true`이면 번호 목록 또는 순서형 절차가 있어야 한다.
   - `requires_command_example=true`이면 ``oc `` 또는 YAML/명령 예시가 있어야 한다.

## 최소 seed의 역할

현재 seed는 8건뿐이다. 목적은 완전한 coverage가 아니라 아래 네 축의 기반선을 만드는 것이다.

- 개요형 설명이 트러블슈팅 문서에 끌려가지 않는가
- 교육형 비교/설명 질문이 구조화된 답변으로 나오는가
- 운영형 절차 질문이 실제 명령/예시를 포함하는가
- 트러블슈팅 질문이 원인-진단-조치 순서로 답하는가

## 다음 확장 순서

1. 각 클래스별 5건 이상으로 확장
2. 한국어 단일턴과 멀티턴을 분리
3. `expected.answer`에 금지 claim 패턴 추가
4. `expected.retrieval`에 `min_score` 또는 `gold_chunk_any` 확장
5. 이후 `scripts/` 아래 별도 runner를 추가해 API 응답을 fixture와 비교

## 샘플 워크플로우

1. fixture JSON을 로드한다.
2. 각 항목의 `conversation` 마지막 질문을 `/api/chat` 또는 `/api/chat/stream`으로 보낸다.
3. `rewritten_query`, `sources`, `answer`를 fixture의 `expected`와 비교한다.
4. 클래스별 pass rate와 false-authority 사례를 리포트한다.

이 문서는 코드 변경 없이도 평가 기준을 먼저 고정하기 위한 보조 산출물이다.
