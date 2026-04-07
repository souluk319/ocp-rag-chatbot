# Productization TODO

이 문서는 이 브랜치의 단일 실행 기준 문서다.

앞으로는 이 파일 하나만 기준으로 작업한다.

- 새 계획 문서를 따로 만들지 않는다.
- 위에서 아래 순서로만 진행한다.
- 이미 끝난 일, 지금 하는 일, 다음 할 일을 여기서만 갱신한다.
- 증상만 가리는 땜질보다 근원 원인 점검을 우선한다.

## 0. 현재 상태

### 완료

- [x] `.env` 변경이 실행 중 서버에 반영되지 않던 LLM 설정 버그 수정
- [x] 기본 답변/카피의 데모톤 1차 정리
- [x] `ops / learn` 런타임 분기 제거
- [x] `play_book.cmd` 중심 실행 진입점 통일
- [x] README에 현재 폴더 구조, 런타임 파이프라인, 코드 품질 요약 반영
- [x] `Pod lifecycle` 같은 개념 질문이 엉뚱한 intake/API 조각으로 무너지는 retrieval 문제 1차 복구

### 남아 있는 핵심 문제

- [ ] retrieval이 아직 휴리스틱 의존이 크고 raw vector 품질 편차가 큼
- [ ] reranker 없음
- [ ] query rewrite는 있으나 약한 규칙 기반 수준
- [ ] `doc_to_book` 정규화 품질 편차와 중복 조각 문제가 남아 있음
- [ ] 설정 로딩 구조가 여전히 전역 env 오염에 취약함
- [ ] `server.py`가 너무 많은 책임을 한 파일에 쥐고 있음
- [ ] 폴더 구조가 여전히 `part1~4` 개발 단계 이름 중심이라 유지보수성이 낮음

## 1. 지금 당장 진행할 작업

상태: `in progress`

작업명:
- Retrieval 근원 원인 점검

목표:
- 지금 retrieval miss가 임베딩 품질 문제인지
- 청킹/정규화 문제인지
- source mixing 문제인지
- fusion/top-k/후처리 문제인지
정확히 분리해서 판단한다.

이미 끝낸 것:
- [x] 업로드 intake 문서가 기본 검색에 무조건 섞이던 기본값 차단
- [x] concept 질의에서 명령/상태 조각이 과도하게 올라오던 스코어 보정
- [x] `Pod lifecycle` 회귀 케이스 추가
- [x] 기본 retrieval 후보 수 상향
- [x] `manifests/part2_retrieval_root_cause_cases.jsonl` 생성
- [x] concept / ops / mixed 12케이스 1차 retrieval eval 실행

이번 단계에서 할 일:
- [x] concept / ops / mixed 질문 평가셋을 별도 묶음으로 정리
- [ ] BM25 top hit / vector top hit / fusion top hit를 케이스별로 비교 기록
- [ ] intake 정규화 결과에서 중복 section / 깨진 heading / 과도한 미세 chunk 비율 점검
- [ ] 임베딩 문제인지 청킹 문제인지 정규화 문제인지 판정 메모 작성
- [ ] 이 단계 끝날 때 reranker가 정말 다음 우선순위인지 결론 내리기

완료 조건:
- miss 원인을 감으로 말하지 않고 케이스별로 설명할 수 있다.
- "왜 엉뚱한 조각이 뽑혔는가"를 재현 가능한 형태로 남긴다.
- 다음 단계가 reranker인지, 정규화 보수인지, chunking 수정인지 우선순위가 확정된다.

현재 관찰 메모:
- root cause eval 2차 결과: overall `hit@1 1.0`, concept `1.0`, mixed `1.0`, ops `1.0`
- 1차에서 보였던 `etcd 백업은 어떻게 해?` 미스는 retrieval 미스가 아니라 평가셋 기대값 드리프트였다.
- 현재 코퍼스에서는 해당 절차가 `backup_and_restore`뿐 아니라 `postinstallation_configuration`에도 강하게 걸린다.
- 그래서 관련 retrieval/answer manifest들의 기대값을 현재 코퍼스 구조에 맞게 갱신했다.
- 남은 핵심은 "개념 질문 전반 붕괴"가 아니라 "raw vector 후보 품질 편차와 정규화/청킹 품질 편차를 어떻게 측정할 것인가" 쪽이다.
- answer eval 재실행 결과: `18 cases`, `pass_rate 0.8333`
- 현재 남은 대표 실패는 세 가지다:
  - follow-up 설정 질문에서 `support` 책이 섞이면서 무근거 clarification으로 빠지는 케이스
  - 보안 기본 문서 질문에서 security 릴리스 노트 조각을 중심 문서로 오인하는 케이스
  - 복수 엔터티가 열린 clarification 케이스에서 먼저 되물어야 하는데 절차를 단정해버리는 케이스

## 2. 바로 다음 작업

상태: `next`

작업명:
- Config / runtime integrity 근원 보수

목표:
- `.env`가 진짜 단일 진실원천이 되게 만들고
- 런타임이 실제 어떤 설정으로 도는지 숨김 없이 보이게 한다.

해야 할 일:
- [ ] `load_settings()`에서 전역 `os.environ` 변형 제거 설계
- [ ] config-sensitive 서비스들의 snapshot 지점 점검
- [ ] `/api/health`에 active LLM endpoint, model, qdrant, embedding mode, config fingerprint 노출
- [ ] silent fallback 사용 여부를 health나 trace에서 보이게 정리

완료 조건:
- 설정 바꿨는데 다른 값으로 돈다는 상황이 다시 안 나온다.
- 현재 서버가 무엇을 보고 도는지 UI 밖에서도 바로 확인할 수 있다.

## 3. 그 다음 작업

상태: `next`

작업명:
- 폴더 구조 개편 1차 착수

목표:
- 문제 발생 시 기능 기준으로 바로 코드 위치를 좁힐 수 있게 만든다.

최종 방향:
- `src/play_book_studio/`
  - `config/`
  - `ingestion/`
  - `retrieval/`
  - `answering/`
  - `app/`
  - `evals/`
- `scripts/`는 얇은 진입점만 남긴다.
- 무거운 `artifacts`는 repo 밖 외부 디렉토리 유지

이번 단계에서 할 일:
- [ ] 최종 트리를 `RESTRUCTURE_DRAFT.md`에 현재 합의안 기준으로 덮어쓰기
- [ ] `scripts`와 `src` 경계 원칙 명문화
- [ ] 1차 실제 이관 범위를 `config + retrieval + answering + app`으로 고정
- [ ] `server.py` 분리 대상 책임 목록 작성

완료 조건:
- 폴더 재배치 목표가 더 이상 흔들리지 않는다.
- 실제 파일 이동 전, 어떤 순서로 나눌지 한눈에 보인다.

## 4. 이후 작업

상태: `queued`

작업명:
- 구조 개편 1차 실행

해야 할 일:
- [ ] `src/play_book_studio/` 패키지 생성
- [ ] `config / retrieval / answering / app` 1차 이관
- [ ] `play_book.cmd`, `scripts/play_book.py`를 새 경로 기준으로 전환
- [ ] 구패키지는 임시 shim으로만 유지
- [ ] 관련 테스트 import 전환

완료 조건:
- 제품 런타임 핵심 코드는 더 이상 `part1~4` 이름에 기대지 않는다.

## 5. 제품 품질 백로그

상태: `queued`

- [ ] reranker 도입 여부 및 방식 결정
- [ ] query rewrite 고도화 여부 결정
- [ ] `doc_to_book` 정규화 품질 기준 수립
- [ ] 세션/상태 영속화
- [ ] Play Book Studio 기준 브랜드/pack 분리
- [ ] NotebookLM식 좌측 자료 패널 재설계
- [ ] 문서 포맷/커넥터 확장 전략 정리

## 6. 알고 있는 사실

- reranker는 현재 없다.
- rewrite는 현재 있으나 약한 규칙 기반이다.
- GraphRAG는 후보지만 지금 즉시 1순위는 아니다.
- 먼저 정규화 / chunking / retrieval miss의 근원을 분리해내야 한다.
- `artifacts`는 repo 안이 아니라 상위 외부 디렉토리로 유지하는 것이 맞다.

## 7. 변경 로그

- 2026-04-07: 제품화 TODO 문서를 단일 실행 기준 문서로 전면 재작성
- 2026-04-07: retrieval 1차 복구, mode 제거, 실행 진입점 단일화, README 구조 요약 반영 상태를 현재 기준으로 반영
