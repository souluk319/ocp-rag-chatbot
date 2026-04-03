# Part 7. Roadmap And Ownership

## Chapter 7.1 역할 배치

| 역할 | 책임 |
|---|---|
| Atlas | 전체 범위 통제, 우선순위, 최종 의사결정 |
| Console | 대기 UX, citation UX, 문서 패널, 에러 상태 |
| Echo | 멀티턴, follow-up rewrite, compaction, step-by-step 안정화 |
| Sieve | retrieval, rerank, command fast lane, upload ingest |
| Runbook | ops/learn 답변 모양, 운영 정확성, 교육 유용성 |
| RedPen | 기준 수립, regression, baseline/release gate |

## Chapter 7.2 Phase Plan

### Phase 0. 브랜치 안정화

- 현재 로컬 변경사항 정리
- `.plan` 검토 후 범위 고정
- 이후 구현 브랜치 분리

### Phase 1. Demo Trust Pack

범위:

- waiting animation
- answer-level source tag
- same-page document panel

목표:

- 발표/시연에서 즉시 체감 개선

### Phase 2. Multi-turn Quality Pack

범위:

- session state v2
- follow-up resolution
- compaction
- step-by-step mode

목표:

- 10턴 이상 대화 유지

### Phase 3. Ops Fast Lane Pack

범위:

- command snippet index
- ops intent routing
- answer shape enforcement

목표:

- 운영 질문의 응답 속도와 실용성 개선

### Phase 4. Upload And SaaS-like Doc Pack

범위:

- upload ingest
- normalized viewer schema
- document entity model

목표:

- “문서 업로드형 RAG 플랫폼” 방향의 첫 버전 확보

## Chapter 7.3 권장 순서

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4

이 순서를 추천하는 이유는 다음과 같다.

- 사용자가 즉시 체감하는 문제를 먼저 제거한다.
- 긴 멀티턴과 답변 안정성은 플랫폼 확장 전에 고쳐야 한다.
- 업로드 기능은 가장 크고 무거운 트랙이므로 앞선 UX/품질 기반이 필요하다.

## Chapter 7.4 즉시 실행 가능한 첫 작업 목록

1. `EVALS.md` 초안 생성
2. waiting/pending UI 렌더 경로 명세서 작성
3. citation same-page viewer 이벤트 플로우 정리
4. `SessionContext V2` 슬롯 설계 확정
5. 멀티턴 regression 질문 세트 20개 수집
6. command fast lane 대상 질문 30개 선정
7. upload ingest 도메인 모델 초안 작성

## Chapter 7.5 리스크

- UI만 바꾸고 retrieval/answer 품질이 그대로면 체감 개선이 오래 못 간다.
- 멀티턴을 raw history 중심으로 키우면 프롬프트 비용과 노이즈가 같이 커진다.
- 업로드 파이프라인을 너무 빨리 넣으면 viewer/normalization 일관성이 먼저 무너질 수 있다.
- sentence-level rerank를 급히 넣으면 explainability가 떨어질 수 있다.

## Chapter 7.6 의사결정 기준

갈등 상황에서는 아래 순서를 따른다.

1. correctness
2. groundedness
3. inspectability
4. UX trust
5. feature breadth
