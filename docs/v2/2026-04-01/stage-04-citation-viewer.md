# 4단계 - citation 클릭과 viewer 정합성

## 목표

답변의 citation 이 실제로 맞는 문서를 가리키고, 클릭 시 HTML 원문이 열리도록 안정화한다.

## 왜 이 단계가 중요한가

출처가 잘못되면 “근거 기반 챗봇”이 아니라 “링크만 붙는 챗봇”이 된다.

## 담당 역할

- Ramanujan: 답변과 citation 간 의미 불일치 패턴 분석
- Arendt: 사용자 관점에서 citation 표시 방식 확인
- Peirce: 어떤 문서가 소개/운영 답변의 정답 출처가 되어야 하는지 검토
- Gibbs: viewer_url / gateway viewer route / source normalization 보정
- Feynman: 클릭 테스트와 원문 일치 검증
- Russell: citation 구조 문서와 구현 정합성 감사

## 작업 내용

1. 답변에 붙는 citation 구조를 점검한다.
2. viewer_url 이 실제 HTML 을 여는지 본다.
3. 기본 질문과 운영 질문에서 citation 이 과하게 엇나가지 않는지 점검한다.

## 테스트

- 기본 질문 2건
- 운영 질문 2건
- 각 응답의 citation click-through

## 완료 기준

- citation 링크가 정상 열림
- citation 이 엉뚱한 무관 문서를 가리키지 않음
- 최소 1개의 핵심 citation 은 문맥상 맞는 문서임

## 산출물

- citation / viewer 보정
- 테스트 결과
- 짧은 완료 보고
