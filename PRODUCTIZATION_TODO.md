# Productization TODO

이 문서는 이 브랜치의 단일 실행 기준 문서다.

- 앞으로는 이 파일 순서대로만 진행한다.
- 새 계획 문서를 따로 만들지 않는다.
- 한 단계가 끝나면 여기 상태를 갱신하고 다음 단계로 넘어간다.

## 0. 현재 상태

### 완료

- [x] `.env` 반영 안 되던 LLM 설정 버그 수정
- [x] 기본 답변/카피 데모톤 1차 정리
- [x] `ops / learn` 런타임 분기 제거
- [x] `play_book.cmd` 중심 실행 진입점 통일
- [x] retrieval 1차 복구
- [x] root-cause retrieval 케이스 묶음 생성 및 재평가
- [x] 왜곡되던 `etcd 백업/복구` 기대값 manifest 정리

### 남아 있는 핵심 문제

- [ ] 폴더 구조가 `part1~4` 개발 단계 이름 중심이라 유지보수성이 낮음
- [ ] `server.py`가 너무 많은 책임을 한 파일에 쥐고 있음
- [ ] Play Book Studio 정체성이 아직 코드/화면에 반영되지 않음
- [ ] 답변 품질 실패 케이스 3개가 남아 있음
- [ ] retrieval은 여전히 reranker 없이 휴리스틱 의존이 큼
- [ ] 설정 로딩 구조는 여전히 전역 env 오염에 취약함

## 1. 최소 구조개편

상태: `done`

목표:
- `play_book_studio`라는 새 제품 패키지 기준을 먼저 세운다.
- app/runtime을 먼저 분리해서 이후 제품화 작업이 구조적으로 덜 꼬이게 만든다.

이번 단계에서 한 일:
- [x] `RESTRUCTURE_DRAFT.md`를 현재 합의안 기준으로 전면 갱신
- [x] `src/play_book_studio/` 패키지 생성
- [x] `config / retrieval / answering / app / evals` 최소 골격 생성
- [x] `scripts/play_book.py`가 새 `play_book_studio.cli`를 보게 전환
- [x] `server.py`에서 세션 / 표시 / 뷰어 보조를 새 app 모듈로 1차 분리

완료 조건:
- `play_book.cmd --help` 와 기본 명령이 새 패키지 경로를 거쳐도 동작한다.
- 구조개편 기준 패키지가 실제로 생긴다.
- `server.py` 책임이 지금보다 분리되기 시작한다.

검증:
- [x] `play_book.cmd --help`
- [x] `play_book.cmd ask --query "OpenShift 아키텍처를 처음 설명해줘" --skip-log`
- [x] `150 passed`

## 2. 제품화 1차 실험

상태: `in progress`

목표:
- 눈에 보이는 제품 문제를 과감하게 실험한다.

이번 단계에서 할 일:
- [ ] 브랜드를 `Play Book Studio` 기준으로 정리
- [ ] OCP를 제품명이 아니라 선택된 pack처럼 보이게 정리
- [ ] 좌측 패널을 NotebookLM식 자료 선택 경험으로 재설계
- [ ] 채팅 중심 위계로 화면을 재정렬

완료 조건:
- 첫 화면에서 제품 정체성이 덜 흔들린다.
- 자료 선택 경험이 지금보다 훨씬 직관적이다.

## 3. 답변 품질 보수

상태: `next`

목표:
- 현재 남아 있는 대표 실패 케이스 3개를 잡는다.

현재 남은 대표 실패:
- [ ] follow-up 설정 질문이 `support`로 새는 문제
- [ ] 보안 기본 문서 질문이 릴리스 노트 조각으로 새는 문제
- [ ] 복수 엔터티 clarification에서 먼저 되물어야 하는데 절차를 단정하는 문제

완료 조건:
- answer eval 실패 케이스가 줄어든다.
- 지금 남아 있는 실패가 "구체적인 다음 원인"으로 더 좁혀진다.

## 4. Retrieval 근원 점검 2차

상태: `queued`

목표:
- reranker 도입 전, 지금 남은 retrieval 문제의 근원을 더 분리한다.

해야 할 일:
- [ ] BM25 top hit / vector top hit / fusion top hit 비교 기록
- [ ] intake 정규화 결과에서 중복 section / 깨진 heading / 과도한 미세 chunk 비율 점검
- [ ] 임베딩 문제인지 청킹 문제인지 정규화 문제인지 판정 메모 작성
- [ ] reranker가 정말 다음 우선순위인지 결론 정리

현재 관찰:
- root-cause retrieval eval: overall `hit@1 1.0`
- answer eval: `18 cases`, `pass_rate 0.8333`
- retrieval 전반 붕괴보다 raw vector 품질 편차와 정규화 편차가 더 남아 있다.

## 5. Config / runtime integrity

상태: `queued`

목표:
- `.env`가 진짜 단일 진실원천이 되게 만들고
- 런타임이 실제 어떤 설정으로 도는지 숨김 없이 보이게 한다.

해야 할 일:
- [ ] `load_settings()`에서 전역 `os.environ` 변형 제거 설계
- [ ] config-sensitive 서비스들의 snapshot 지점 점검
- [ ] `/api/health`에 active runtime snapshot 노출
- [ ] silent fallback 사용 여부를 health나 trace에서 보이게 정리

## 6. 후속 구조개편

상태: `queued`

해야 할 일:
- [ ] `ingestion` 영역 이관
- [ ] `evals` 정리
- [ ] 구패키지 shim 정리
- [ ] `part1~4` 이름 제거

## 7. 알고 있는 사실

- reranker는 현재 없다.
- rewrite는 현재 있으나 약한 규칙 기반이다.
- GraphRAG는 후보지만 지금 즉시 1순위는 아니다.
- `artifacts`는 repo 안이 아니라 상위 외부 디렉토리로 유지하는 것이 맞다.

## 8. 변경 로그

- 2026-04-07: 구조개편 우선 순서에 맞춰 TODO 문서 전면 재작성
- 2026-04-07: 최소 구조개편 1차 완료. `play_book_studio` 패키지, 새 CLI 경로, `server.py` 1차 책임 분리 반영
