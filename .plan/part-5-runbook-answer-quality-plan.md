# Part 5. Runbook Answer Quality Plan

## Chapter 5.1 목표

이 챗봇이 OCP 운영/교육용으로 “믿을 만한 답을 한다”는 인상을 주도록 answer shape를 고정한다.

## Chapter 5.2 Ops Mode 계약

ops 모드 답변은 아래 순서를 강제한다.

1. 무엇을 하는 명령인지 한 문장
2. 코드 블록 또는 절차
3. 범위/영향/주의사항
4. 근거 태그

금지사항:

- bare command만 던지기
- 근거 없는 버전/옵션 추가
- 필요 없는 장황한 설명

## Chapter 5.3 Learn Mode 계약

learn 모드 답변은 아래 순서를 강제한다.

1. 개념 정의
2. 왜 필요한지
3. 구성 요소 또는 흐름
4. 실무 연결
5. 근거 태그

## Chapter 5.4 명령어 질문 전용 답변 기준

다음 질문군은 짧고 빠른 답을 우선한다.

- 로그 확인
- 인증서 점검
- node drain
- RBAC 부여
- finalizer/terminating
- 리소스 상태 확인

이 질문군은 “짧은 정의 + 명령 + 최소 주의사항”으로 수렴해야 한다.

## Chapter 5.5 Step-by-step 질문 전용 답변 기준

### 규칙

- 단계 수를 먼저 고정한다.
- 각 단계는 하나의 행위만 담는다.
- 단계별 citation을 붙인다.
- 근거가 없는 단계는 만들지 않는다.

### clarification 규칙

- 환경 조건이 빠진 경우 짧게 묻는다.
- 근거가 없는 경우 추측하지 않고 범위를 줄여 묻는다.

## Chapter 5.6 Source Tag 기준

answer-level tag는 아래 순서로 보여준다.

1. 문서군
2. 문서명 또는 slug
3. section
4. citation count

ops 답변에서는 태그가 citation card보다 먼저 보여야 한다.

## Chapter 5.7 테스트 영향

- ops answer golden set
- learn answer golden set
- command answer latency/shape test
- step-by-step structure test
- source tag consistency test
