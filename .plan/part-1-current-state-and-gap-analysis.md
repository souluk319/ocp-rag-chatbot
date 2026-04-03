# Part 1. Current State And Gap Analysis

## Chapter 1.1 현재 시스템 관찰

### UI / Console

- 프론트는 단일 `index.html` 기반 스트리밍 UI다.
- 대기 상태용 스타일 자산은 있으나, 실제 메시지 렌더링에서는 단순 텍스트 갱신 비중이 크다.
- citation 카드가 존재하지만 링크는 새 탭으로 열린다.
- 우측 패널은 trace/rewritten query/debug 정보 중심이다.

### Multi-turn / Session

- 세션 저장은 존재한다.
- 세션 유지 한도는 20턴이다.
- 그러나 답변 생성 시 전체 대화 이력을 직접 주입하지 않고 `SessionContext`만 요약해서 전달한다.
- 따라서 긴 멀티턴일수록 reference resolution이 약해질 가능성이 높다.

### Retrieval / Answering

- 현재 retrieval은 chunk 단위 hybrid retrieval이다.
- BM25 + dense vector + RRF 중심이며 sentence-level similarity 단계는 없다.
- step-by-step 요청을 위한 전용 실행계획 구조는 없고, 프롬프트 힌트에 의존한다.

### Document / Viewer

- HTML 기반 전처리와 내부 viewer 경로 체계는 있다.
- 다중 포맷 업로드, parse job, normalized doc entity, ingestion status는 아직 없다.

## Chapter 1.2 피드백별 갭 매핑

| ID | 피드백 | 현재 상태 | 핵심 갭 | 주관 역할 | 우선순위 |
|---|---|---|---|---|---|
| 1 | 기다릴 때 너무 정적임 | 스트리밍은 있으나 체감 로딩 UX 약함 | pending 상태의 시각화 부족 | Console | P0 |
| 2 | 10턴 이상 멀티턴 약함 | 세션은 있으나 메모리 구조 단순 | reference resolution / compaction 부족 | Echo | P0 |
| 3 | 새 탭 문서 뷰어 불편 | 내부 viewer는 있으나 새 탭 링크 | side-by-side 문서 패널 부재 | Console | P0 |
| 4 | PDF/PPT/HTML 업로드 원함 | HTML 전처리 중심 | 업로드 ingest 파이프라인 부재 | Sieve | P1 |
| 5 | 업로드 문서의 보기 좋은 정규화 원함 | HTML normalized sections만 존재 | document record / viewer schema 부재 | Sieve | P1 |
| 6 | 답변마다 파일 태그 원함 | citation card는 있으나 answer tag 약함 | answer-level source tag 설계 필요 | Console + Runbook | P0 |
| 7 | 명령어 질문 빠른 답 원함 | 일부 휴리스틱 존재 | command fast lane / curated snippets 부재 | Runbook + Sieve | P0 |
| 8 | 단계별 요청 시 엇나감 | 프롬프트 힌트 위주 | structured step mode / verifier 부재 | Echo + Runbook | P0 |
| 9 | 문장 단위 유사도 질문 | chunk retrieval만 존재 | 설명 문서와 차세대 rerank 계획 필요 | Sieve + RedPen | P1 |

## Chapter 1.3 이미 있는 자산

이번 계획은 아래 자산을 버리지 않고 확장하는 방향을 따른다.

- 스트리밍 채팅 기본 구조
- 세션 상태 객체
- follow-up rewrite 휴리스틱
- 내부 문서 viewer 엔드포인트
- normalized docs / chunks / retrieval logs
- ops/learn 모드 분리

## Chapter 1.4 이번 계획의 비목표

이번 계획에서 당장 하지 않는 것:

- 무제한 장기 메모리
- 완전한 SaaS 멀티테넌시
- 대규모 외부 커넥터 전체 구현
- 벤치마크 숫자 맞추기용 과도한 복잡도

## Chapter 1.5 즉시 선행조건

가장 먼저 필요한 선행작업은 두 가지다.

1. 현재 로컬 변경사항을 안정화 커밋 단위로 정리
2. 계획 문서에 맞춰 후속 문서 `EVALS.md`, `TEAM_OPS.md`, `VENDOR_NOTES.md` 생성 준비
