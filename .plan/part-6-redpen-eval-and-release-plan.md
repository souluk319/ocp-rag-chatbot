# Part 6. RedPen Eval And Release Plan

## Chapter 6.1 목적

이번 피드백 대응은 “예뻐 보이는 개선”이 아니라, baseline과 release 기준이 분리된 검증 체계로 관리해야 한다.

## Chapter 6.2 새로 만들어야 하는 문서

### `EVALS.md`

- baseline / release 기준
- 테스트 세트
- 실패 유형
- pass criteria

### `TEAM_OPS.md`

- 회의 흐름
- 리뷰 흐름
- artifact 템플릿

### `VENDOR_NOTES.md`

- LLM/embedding/vendor API 메모
- last checked 날짜
- implementation caveat

## Chapter 6.3 Baseline vs Release

| 항목 | Baseline | Release |
|---|---|---|
| 대기 UX | 정적 상태만 보이지 않음 | 단계/진행감/중단 UX 모두 검증 |
| 멀티턴 | 6턴 이상 유지 | 12턴 이상 유지 |
| command QA | 핵심 15문항 통과 | 핵심 30문항 통과 |
| step-by-step | 구조 붕괴 없음 | 단계 정확도와 citation 일치 검증 |
| source tag | answer-level 표시 | tag-citation-viewer 전부 일치 |
| 문서 viewer | same-page open | anchor highlight + trace sync |
| 업로드 ingest | 최소 2포맷 smoke | 우선 4포맷 안정화 |

## Chapter 6.4 평가 세트 설계

### 세트 A: Demo trust

- 대기 상태
- citation visibility
- same-page viewer

### 세트 B: Multi-turn

- 12턴 대화
- 지시어 follow-up
- topic shift
- clarification fallback

### 세트 C: Ops fast lane

- 명령어 질문
- 짧은 운영 질문
- 비교적 애매한 운영 질문

### 세트 D: Stepwise

- 단계별 설치
- 단계별 점검
- 단계별 장애 대응

### 세트 E: Upload / ingest

- pdf
- ppt/pptx
- html
- md/txt

## Chapter 6.5 회귀 기준

- 기존에 고친 no-evidence 회귀 질문은 반드시 유지
- compare / intro / cert / rbac / finalizer 회귀 질문 유지
- 새 UI 변경은 UX 스냅샷과 동작 테스트를 같이 둔다

## Chapter 6.6 릴리즈 게이트

릴리즈 전 최소 확인 항목:

- 주요 데모 질문 세트 통과
- 멀티턴 세트 통과
- step-by-step 세트 통과
- source tag와 viewer 매핑 오류 없음
- 업로드 파이프라인 실패 처리 확인
