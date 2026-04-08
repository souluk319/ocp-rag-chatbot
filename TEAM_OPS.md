# TEAM_OPS.md

## 목적

이 문서는 named roles가 어떻게 함께 일하는지, 그리고 major work를 어떤 흐름으로 검토할지 정리한 운영 문서다.
리뷰 흐름, meeting 흐름, artifact 템플릿은 여기서 관리한다.

## 언제 6개 역할을 모두 켜는가

아래 작업에는 6개 역할을 모두 같이 쓴다.

- architecture review
- eval design
- major refactors
- release decisions

routine implementation은 관련 역할만 쓴다.

## 역할 책임

- `Atlas`: scope control, final synthesis, decision merge
- `Runbook`: OCP operational correctness, terminology, education usefulness
- `Sieve`: ingestion, normalization, retrieval, reranking
- `Echo`: multi-turn, query rewrite, session memory, reference resolution
- `Console`: user interaction, citations, streaming, error handling, answer shape
- `RedPen`: benchmarks, regressions, release gate, pass/fail judgment

## 기본 리뷰 흐름

major work는 아래 순서로 진행한다.

1. target을 한 문단으로 정의
2. `do not change` 제약 정의
3. completion check 정의
4. 현재 코드와 산출물 inspect
5. 가장 작은 유효 slice 구현
6. 테스트와 runtime check 실행
7. 필요한 surface에만 role review 요청
8. Atlas가 결론 merge
9. RedPen이 `baseline pass/fail` 또는 `release pass/fail` 선언

## 구현 리뷰 흐름

### 1. 변경 의도 확인

- 이 변경이 corpus / retrieval / answer / runtime 중 어디에 걸치는지 먼저 밝힌다
- 변경 이유를 사용자 문제로 설명한다

### 2. 책임 범위 확인

- preprocessing 변경이면 [`src/play_book_studio/ingestion`](src/play_book_studio/ingestion)
- retrieval 변경이면 [`src/play_book_studio/retrieval`](src/play_book_studio/retrieval)
- answer 변경이면 [`src/play_book_studio/answering`](src/play_book_studio/answering)
- runtime / UI 변경이면 [`src/play_book_studio/app`](src/play_book_studio/app)
- 업로드 문서 파이프라인이면 [src/play_book_studio/intake](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake)

### 3. 테스트 영향 확인

- 최소 하나의 테스트 영향이 있어야 한다
- 테스트 추가가 어렵다면 이유와 수동 검증 포인트를 같이 남긴다

### 4. 결과 기록

- 바뀐 파일
- 바뀐 사용자 동작
- 실행한 테스트
- 남아 있는 리스크

## Required Response Format

각 역할은 아래 형식으로 답한다.

1. Claim
2. Evidence
3. Required Tests
4. Recommendation

규칙:

- vague quality claim 금지
- unsupported guess 금지
- test implication 없는 조언 금지
- uncertainty는 명시

## Work Item Template

major task는 아래 항목으로 기록한다.

- `Goal`
- `Do Not Change`
- `Scope`
- `Completion Check`
- `Test Evidence`
- `Remaining Risk`

## 권장 산출물 템플릿

### 1. Implementation Note

- what changed
- why it changed
- affected files
- tests added or updated

### 2. Validation Note

- exact queries or flows used
- observed output
- pass/fail
- known caveat

### 3. Release Note

- baseline verdict
- release verdict
- blockers
- next required action

## 발표 / release 직전 점검

1. `.env`와 endpoint 연결 확인
2. retrieval sanity 확인
3. answer eval 확인
4. UI 수동 시나리오 확인
5. demo 질문 세트 최종 확인

release decision 직전에는 각 역할이 아래를 확인한다.

- `Atlas`: scope drift 없음
- `Runbook`: operational safety
- `Sieve`: retrieval / source-view grounding
- `Echo`: follow-up behavior
- `Console`: chatbot-first UX
- `RedPen`: [`EVALS.md`](EVALS.md) baseline/release gates

한 역할이라도 blocker를 잡으면, 해소되거나 명시적으로 수용되기 전까지 release는 열어두어야 한다.

## 금지 패턴

- 부분 완료를 `done`이라고 부르기
- runtime health를 product readiness와 같게 취급하기
- 남은 blocker 숨기기
- README와 실제 경로가 다른 상태 방치하기
- 테스트 없이 retrieval / answer 로직 바꾸기
- UI 문제를 설명 문구 추가로 덮기
- corpus / retrieval / answer 책임을 한 파일에 다시 섞기
