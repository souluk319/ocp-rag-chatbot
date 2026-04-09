# Productization TODO

이 문서는 이 브랜치의 단일 실행 기준 문서다.

- 앞으로는 이 파일 순서대로만 진행한다.
- 새 계획 문서를 따로 만들지 않는다.
- 한 단계가 끝나면 여기 상태를 갱신하고 다음 단계로 넘어간다.

## 0. 현재 상태

### 완료

- [x] `.env` 반영 안 되던 LLM 설정 버그 수정
- [x] `load_settings()`의 전역 env 오염 제거
- [x] 기본 답변/카피 데모톤 1차 정리
- [x] `ops / learn` 런타임 분기 제거
- [x] `play_book.cmd` 중심 실행 진입점 통일
- [x] `play_book.cmd` / eval CLI baseline 복구
- [x] 공개 import surface 1차 shim 복구
- [x] retrieval 1차 복구
- [x] root-cause retrieval 케이스 묶음 생성 및 재평가
- [x] 왜곡되던 `etcd 백업/복구` 기대값 manifest 정리
- [x] 루트 / `scripts/`의 one-off 실험 파일 `tmp/`로 격리
- [x] `Play Book Studio` 브랜딩 1차 반영
- [x] `ingestion / retrieval / answering / app / evals` 기준 구조개편 1차 완료
- [x] `/api/health` runtime snapshot 및 provider trace 노출
- [x] retrieval root-cause 2차 점검 완료
- [x] 기능명 기준 실행 스크립트로 정리 완료

### 남아 있는 핵심 문제

- [ ] `server.py`가 너무 많은 책임을 한 파일에 쥐고 있음
- [x] `OCP Playbook Studio` 우선 전략이 source/config/update pipeline까지 내려오도록 core pack boundary 1차 반영 완료
- [x] 답변 품질 실패 케이스 3개 정리 및 현재 4.20 코퍼스 기준 eval 기대값 정렬 완료
- [ ] retrieval은 여전히 reranker 없이 휴리스틱 의존이 큼
- [ ] weak rewrite / reranker 부재가 남아 있음
- [ ] API/reference-heavy corpus와 과분절 section이 concept retrieval을 계속 오염시킴
- [ ] 한글 미지원 문서에 대한 번역/보강 lane이 아직 없다
- [ ] OCP 문서 업데이트를 따라가는 지속 수집/증분 반영 파이프라인이 아직 없다
- [ ] OCP-specific retrieval/query/UI 정책은 의도적으로 남아 있지만, core runtime pack identity는 한곳으로 몰아두는 1차 작업이 끝났다
- [ ] retrieval benchmark 기준 남은 4건 miss는 대부분 `operators`, `machine_configuration` coverage gap에 묶여 있다
- [ ] 세션은 아직 memory-only라 재현성과 운영성이 약함

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

## 2. 실행 기준 복구 및 레포 정리

상태: `done`

목표:
- 다시 runnable baseline을 확보하고
- 기준 코드와 실험 부산물이 섞이지 않게 만든다.

이번 단계에서 할 일:
- [x] eval wrapper 자기참조 import 제거
- [x] `play_book_studio.*` 공개 import shim 복구
- [x] `load_settings()` 전역 env 변형 제거
- [x] canonical entrypoint를 `play_book.cmd`, `scripts/play_book.py`, `scripts/check_runtime_endpoints.py`로 고정
- [x] 루트 / `scripts/`의 one-off 실험 스크립트와 리포트를 `tmp/`로 격리

완료 조건:
- `play_book.cmd --help` 와 `play_book.cmd ask` 가 다시 돈다.
- 핵심 pytest collection이 다시 산다.
- `scripts/`와 루트에 기준 코드가 아닌 일회성 파일이 남지 않는다.

검증:
- [x] `play_book.cmd --help`
- [x] `play_book.cmd ask --query "OpenShift 아키텍처를 처음 설명해줘" --skip-log`
- [x] `150 passed`

## 3. 제품화 1차 실험

상태: `done`

목표:
- 눈에 보이는 제품 문제를 과감하게 실험한다.

이번 단계에서 할 일:
- [x] 브랜드를 `Play Book Studio` 기준으로 정리
- [x] OCP를 제품명이 아니라 선택된 pack처럼 보이게 정리
- [x] 좌측 패널을 NotebookLM식 자료 선택 경험으로 재설계
- [x] 채팅 카드 메타와 빈 상태 문구를 단순화

완료 조건:
- 첫 화면에서 제품 정체성이 덜 흔들린다.
- 자료 선택 경험이 지금보다 훨씬 직관적이다.

## 4. 답변 품질 보수

상태: `done`

목표:
- 현재 남아 있는 대표 실패 케이스 3개를 잡는다.

완료 조건:
- answer eval 실패 케이스가 줄어든다.
- 지금 남아 있는 실패가 "구체적인 다음 원인"으로 더 좁혀진다.

이번 단계에서 한 일:
- [x] `Machine Config Operator` 단일 개념 질문이 복수 엔터티로 오판정되던 라우팅 수정
- [x] 보안 문서 locator 질문을 clarification으로 라우팅
- [x] MCO follow-up에서 `support` 근거가 억지로 밀리던 패널티 제거
- [x] 복수 엔터티 follow-up은 먼저 clarification 하도록 분기 추가
- [x] 현재 4.20 코퍼스 slug 기준으로 answer eval 기대값 정렬

검증:
- [x] `play_book.cmd eval` -> `18 cases`, `pass_rate 1.0`
- [x] `155 passed`

## 5. Retrieval 근원 점검 2차

상태: `done`

목표:
- reranker 도입 전, 지금 남은 retrieval 문제의 근원을 더 분리한다.

이번 단계에서 한 일:
- [x] BM25-only / vector-fusion root-cause eval을 분리 실행하고 결과를 각각 artifact로 저장
- [x] ingestion data-quality audit import 복구 및 재실행
- [x] chunk composition 지표를 다시 뽑아 API/reference 비중, 섹션 분절 강도 확인
- [x] retrieval 근원 판정 메모를 `RETRIEVAL_ROOT_CAUSE_AUDIT.md` 에 고정
- [x] reranker 우선순위를 `코퍼스 cleanup 이후`로 결론 정리

검증:
- [x] `scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --output ...retrieval_eval_root_cause_vector.json`
- [x] `scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --skip-vector --output ...retrieval_eval_root_cause_bm25.json`
- [x] `scripts/audit_ingestion_data_quality.py`

현재 결론:
- vector/fusion은 BM25-only보다 분명히 낫다.
- 남은 retrieval 문제의 1순위 원인은 임베딩 속도가 아니라 API/reference-heavy corpus와 섹션 분절이다.
- 빠른 회사 TEI 서버가 생겼으므로 코퍼스 cleanup 후 재임베딩 비용은 더 이상 큰 문제가 아니다.
- reranker는 필요하지만 지금 당장 1순위는 아니다.

## 6. Config / runtime integrity

상태: `done`

목표:
- `.env`가 진짜 단일 진실원천이 되게 만들고
- 런타임이 실제 어떤 설정으로 도는지 숨김 없이 보이게 한다.

이번 단계에서 한 일:
- [x] `load_settings()`에서 전역 `os.environ` 변형 제거 유지
- [x] answerer runtime signature를 LLM만이 아니라 embedding / qdrant / artifacts / manifest까지 포함하도록 확장
- [x] 설정이 바뀌면 LLM client만 교체하지 않고 answerer 전체를 재구성하도록 refresh 로직 교정
- [x] `/api/health`가 실제 active runtime snapshot을 반환하도록 연결
- [x] chat payload / chat log에도 runtime snapshot을 함께 기록
- [x] LLM provider preference / last provider / fallback 사용 여부를 health와 pipeline trace에 노출

검증:
- [x] `play_book.cmd --help`
- [x] `154 passed`
- [x] health payload smoke 출력 확인

현재 결론:
- 이제 `.env` 변경은 answerer runtime 전체 재구성 기준으로 감지된다.
- `/api/health`에서 active endpoint/model/embedding/qdrant/artifacts 경로를 바로 확인할 수 있다.
- silent fallback은 더 이상 완전히 숨지 않고 health/runtime trace에서 확인 가능하다.

## 7. 후속 구조개편

상태: `done`

이번 단계에서 한 일:
- [x] `indexing` 패키지를 `ingestion`으로 이관하고 소스/스크립트/테스트 import를 전부 새 경로로 정렬
- [x] `evals` 아래로 `benchmark.py`, `sanity.py`를 이동해 평가 로직을 한곳으로 정리
- [x] `run_part*.py` 스크립트를 `run_ingestion.py`, `run_retrieval_*.py`, `run_answer_*.py`, `run_ragas_eval.py`로 교체
- [x] top-level shim (`audit.py`, `bm25.py`, `context.py`, `models.py`, `prompt.py`, `ragas_eval.py`, `server.py`) 제거
- [x] stale `ocp_rag_v2.egg-info` 제거
- [x] `ENTRYPOINTS.md`, `RESTRUCTURE_DRAFT.md`, `README.md`를 새 구조 기준으로 갱신

검증:
- [x] `207 passed`
- [x] `play_book.cmd --help`
- [x] `python scripts/run_retrieval_eval.py --help`
- [x] `python scripts/run_ingestion.py --help`

현재 결론:
- repo 안 코드 구조는 이제 `ingestion / retrieval / answering / app / evals` 기준으로 읽힌다.
- repo 코드 구조와 외부 artifact 디렉토리 모두 `corpus / retrieval / answering / runtime` 기준으로 정리됐다.
- `tmp/` 아래 debug 흔적은 의도적으로 남겨두고, 기준 코드 경로에서는 제외했다.

## 7. 알고 있는 사실

- reranker는 현재 없다.
- rewrite는 현재 있으나 약한 규칙 기반이다.
- GraphRAG는 후보지만 지금 즉시 1순위는 아니다.
- `artifacts`는 repo 안이 아니라 상위 외부 디렉토리로 유지하는 것이 맞다.
- 실험 로그 / 임시 스크립트 / 임시 리포트는 `tmp/` 아래에만 둔다.

## 8. OCP source strategy / 한글 코퍼스 기준선

상태: `done`

목표:
- 현재 단계의 주제를 분명히 `OCP Playbook Studio`로 고정한다.
- 한글 코퍼스 기준선과 영어 fallback/번역 lane 기준을 먼저 확정한다.

이번 단계에서 한 일:
- [x] OCP 문서군만 현재 범위라는 원칙을 README/TODO/manifest 전략에 명시
- [x] `approved_ko / mixed / en_only / blocked` 분류 기준을 현재 ingestion 기준선으로 확정
- [x] `translated_ko_draft` 번역 lane 상태값과 승인 규칙 초안 정의
- [x] 어떤 문서를 기본 citation 가능 코퍼스에 넣고, 어떤 문서는 번역/검토 대기로 둘지 규칙화
- [x] `docs.redhat.com` published Korean/html-single을 현재 1차 source of truth로 고정
- [x] source approval report에 OCP source policy와 translation lane 상태를 노출

완료 조건:
- 지금 단계의 목표가 `범용 NotebookLM`이 아니라 `OCP Playbook Studio`라는 점이 코드/문서에서 흔들리지 않는다.
- 한글 미지원 문서가 “없음”이 아니라 “어떤 상태로 처리되는지”가 명확해진다.

검증:
- [x] `pytest -q tests/test_ingestion_audit.py`
- [x] `python scripts/build_source_approval.py --help`

## 9. OCP 문서 업데이트 추적 / 지속 반영 파이프라인

상태: `done`

목표:
- OCP 문서 업데이트를 계속 따라갈 수 있는 ingestion/update 루프를 만든다.
- 수동 일회성 크롤링이 아니라 변경 감지 -> 수집 -> 재정규화 -> 재평가 경로를 만든다.

이번 단계에서 한 일:
- [x] manifest refresh 시 신규/삭제/변경 slug diff를 `source_manifest_update_report.json`에 남기게 만들기
- [x] raw html metadata에 `source_fingerprint`와 `raw_html_sha256`를 남겨 증분 수집 기준 초안 만들기
- [x] 한글 페이지 fallback 탐지 결과를 approval report/approved manifest에 영속화
- [x] `SOURCE_CATALOG_PATH`와 `SOURCE_MANIFEST_PATH`를 분리해 source catalog와 runtime approved manifest를 분리
- [x] `docs.redhat.com` published Korean은 source catalog, `approved_ko manifest`는 runtime 입력이라는 update flow를 문서화
- [x] GitHub `openshift/openshift-docs`는 change feed/영문 보조 source 후보로 기록

완료 조건:
- 새 OCP 문서가 나오거나 바뀌었을 때 어떻게 반영할지 팀이 한 문장으로 말할 수 있다.
- “다음 업데이트 때 또 수작업인가?”라는 질문에 답할 수 있다.

검증:
- [x] `pytest -q tests/test_ingestion_manifest.py tests/test_ingestion_audit.py tests/test_settings_paths.py`
- [x] `python scripts/build_source_manifest.py`
- [x] `python scripts/build_source_approval.py`

## 10. Corpus cleanup / 재정규화 / 재임베딩

상태: `done`

목표:
- 현재 retrieval miss의 1순위 원인인 코퍼스 오염을 줄인다.
- 빠른 회사 TEI 서버를 활용해 cleanup -> 재임베딩 루프를 짧게 만든다.

이번 단계에서 한 일:
- [x] `corpus_policy.py`에 API/reference-heavy book lane 기준과 translation/manual-review 우선순위 slug를 고정
- [x] reference-heavy 책은 더 굵은 chunk profile을 쓰도록 청킹 정책 재설계
- [x] concept 질문에서 reference/API 책이 상위를 오염시키지 않도록 기본 감점 규칙 반영
- [x] `approved_ko` runtime manifest 기준으로 코퍼스를 재정규화 / 재임베딩 / Qdrant 재적재
- [x] source approval / data quality / root-cause retrieval eval을 cleanup 이후 기준으로 재생성
- [x] high-value coverage gap을 `translation-first` / `manual-review-first`로 분류

완료 조건:
- root-cause retrieval eval에서 concept 계열 hit가 더 안정된다.
- cleanup 이후 코퍼스 identity와 artifact fingerprint를 문서로 고정한다.

검증:
- [x] `python scripts/build_source_approval.py`
- [x] `python scripts/run_ingestion.py --collect-subset all --process-subset all`
- [x] `python scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_root_cause_vector_cleanup.json`
- [x] `python scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --skip-vector --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_root_cause_bm25_cleanup.json`

현재 결론:
- runtime approved corpus는 `74 books / 14,656 sections / 50,977 chunks` 기준으로 재구성됐다.
- artifact fingerprint는 `approved_manifest=2165e920...`, `normalized_docs=b25c1a63...`, `chunks=1ea95f61...`, `bm25_corpus=1db3e7e0...` 로 고정했다.
- `corpus_gap_report.json` 기준 high-value source gap은 `translation_first(4) / manual_review_first(2)`로 정리했다.
- vector/fusion은 cleanup 이후에도 BM25-only보다 전체적으로 낫고, 특히 mixed/ops에서 안정적이다.
- concept miss 2건은 검색기 자체보다 `operators`, `machine_configuration`이 승인 코퍼스 밖이라는 coverage gap의 영향이 더 크다.
- 다음 번역/보강 우선순위는 `backup_and_restore`, `installing_on_any_platform`, `machine_configuration`, `monitoring` 이고, 수동 검토 우선순위는 `etcd`, `operators` 이다.

## 11. Retrieval shaping 3차

상태: `done`

목표:
- 더 깨끗해진 코퍼스를 바탕으로 retrieval 자체를 제품 수준으로 다듬는다.

이번 단계에서 한 일:
- [x] update 문서 locator 질의에 대해 `updating_clusters / release_notes / overview` 우선 subquery 및 book shaping 추가
- [x] `Operator`, `Machine Config Operator` 개념 질문의 candidate shaping을 현재 승인 코퍼스 slug 기준으로 재정렬
- [x] concept 질문에서 한 책이 상위 후보를 독식하지 않도록 diversification 규칙을 `operator / mco / pod lifecycle` 계열에 적용
- [x] `extensions / architecture / overview / cli_tools` 계열 fusion 규칙을 지금 코퍼스 기준으로 재조정
- [x] root-cause retrieval eval 기대값을 현재 승인 코퍼스(`extensions`, `architecture`, `overview`) 기준으로 재정렬

완료 조건:
- 대표 concept 질문에서 command/reference 조각이 앞을 먹는 비율이 줄어든다.
- follow-up과 locator 질의가 더 적은 예외규칙으로 안정된다.

검증:
- [x] `pytest -q tests/test_retrieval_core.py`
- [x] `pytest -q tests/test_retrieval_core.py tests/test_answering_context.py tests/test_answering_answerer.py`
- [x] `python scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_root_cause_vector_shaping3.json`
- [x] `python scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --skip-vector --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_root_cause_bm25_shaping3.json`

현재 결론:
- vector/fusion root-cause eval은 `12 cases / hit@1 1.0 / hit@5 1.0` 으로 회복됐다.
- BM25-only는 같은 케이스 기준 `hit@1 0.6667 / hit@5 0.9167` 이라서, 현재 OCP 코퍼스에서는 fusion 이점이 다시 분명하다.
- update locator 질의는 더 이상 `cli_tools > oc explain`에 먼저 끌리지 않고 `updating_clusters` 중심으로 수렴한다.
- `Operator`, `Machine Config Operator` 계열 기대값은 현재 승인 코퍼스에 맞춰 `extensions / overview / architecture` 기준으로 보는 것이 맞다.

## 12. 답변 품질 / citation UX 2차

상태: `done`

목표:
- 답변이 더 짧고 분명하게 끝나고, citation은 보조 정보로 물러서게 만든다.

이번 단계에서 한 일:
- [x] 질문 유형별 답변 템플릿을 짧은 기본형으로 재정리
- [x] `추가 가이드`, 자기설명형 문구, 과한 citation 반복을 프롬프트 규칙에서 축소
- [x] `Pod lifecycle`, `Pod Pending` 같은 대표 concept / troubleshooting shaped answer를 더 짧게 재구성
- [x] clarification / no-answer / source fallback 문구를 짧은 제품 톤으로 정리
- [x] answer eval + ragas를 현재 제품 톤 기준으로 다시 점검

완료 조건:
- 근거는 유지되지만 본문이 더 짧고 직관적으로 읽힌다.
- “설명하는 챗봇”보다 “바로 답하는 제품”에 가까워진다.

검증:
- [x] `pytest -q tests/test_answering_answerer.py tests/test_app_ui.py` -> `75 passed`
- [x] `play_book.cmd eval` -> `18 cases`, `pass_rate 1.0`
- [x] `python scripts/run_ragas_eval.py` -> `faithfulness 0.4139 / answer_relevancy 0.6119 / context_precision 1.0 / context_recall 0.75`

현재 결론:
- answer eval 기준으로는 현재 제품 톤 변경이 회귀 없이 닫혔다.
- citation은 필요한 케이스에서만 남고, clarification / no-answer 답변은 더 짧게 정리됐다.
- 다만 RAGAS에서는 `faithfulness 0.4139`가 여전히 낮아서, 답변 길이를 줄였다고 해서 근거 정합성 문제가 자동으로 해결되진 않았다.
- 즉 이번 단계는 “말투와 밀도 정리”는 끝났고, 남은 품질 리스크는 이후 retrieval / reranker / 답변 정합성 쪽에서 계속 봐야 한다.

## 13. UI productization 2차

상태: `done`

목표:
- 현재 내부 검증용 패널을 유지하되, 화면 위계를 제품답게 다시 잡는다.

이번 단계에서 한 일:
- [x] 좌측 자료 선택 패널의 밀도와 카드 톤을 더 낮춰 문서 선택기처럼 읽히게 조정
- [x] 우측 탭을 `primary / secondary` 계층으로 나눠 `참조 / 보관함 / 업로드`와 `질문 / 세션 / 파이프라인` 위계를 분리
- [x] 채팅 패널 shadow / header / composer / answer card 대비를 높여 가운데 패널 집중도를 강화
- [x] 참조 카드, source empty state, 상단 카피를 더 짧고 덜 시끄럽게 정리

완료 조건:
- 첫 화면에서 “질문하고 답 얻는 제품”으로 먼저 읽힌다.
- 검증용 요소가 남아 있어도 메인 경험을 잡아먹지 않는다.

검증:
- [x] `pytest -q tests/test_app_ui.py` -> `34 passed`

현재 결론:
- 구조는 유지한 채 가운데 채팅 패널이 더 또렷하게 보이도록 위계를 조정했다.
- 좌측은 `문서 선택`, 우측은 `참조 / 보관함 / 업로드` 중심으로 읽히고, 진단 탭은 남기되 한 단계 뒤로 물러났다.
- 아직 완전한 최종 UI는 아니지만, 내부 검증 요소를 유지한 상태에서 제품 화면처럼 보이기 시작하는 기준선은 만들었다.

## 14. OCP 우선 구조 정리 / pack boundary 준비

상태: `done`

목표:
- OCP 우선 제품을 흔들지 않으면서, 나중에 범용 NotebookLM 쪽으로 확장 가능한 경계를 만든다.

이번 단계에서 한 일:
- [x] OCP literal / version / viewer path / collection naming이 남아 있는 core 경로를 `packs.py` 기준으로 재정리
- [x] app identity와 selected corpus identity를 분리하는 최소 pack config 초안 작성
- [x] `Settings.active_pack` 기준으로 core settings와 OCP pack settings 경계를 고정
- [x] `PACK_BOUNDARY_AUDIT.md`로 이후 일반화 시 뜯어야 할 곳 목록 문서화

검증:
- [x] `pytest -q tests/test_settings_paths.py tests/test_ingestion_manifest.py tests/test_app_ui.py`

현재 결론:
- 앱 정체성은 `Play Book Studio`, 현재 코퍼스 정체성은 `OpenShift 4.20 core pack`으로 분리해서 보게 됐다.
- `settings / presenters / sessions / viewers / manifest / audit`는 더 이상 `4.20` literal을 흩뿌리지 않고 pack config를 본다.
- 아직 `retrieval/query`, `router`, UI 예시 질문은 OCP-specific 이지만, 이건 현재 제품 범위상 의도된 부분이며 다음 일반화 때 건드릴 곳도 문서로 고정했다.

완료 조건:
- 지금 단계에서는 OCP 우선으로 단순하게 가되, 나중에 확장할 때 어디를 건드릴지 한눈에 보인다.
- `NotebookLM이 궁극 목표`와 `지금은 OCP Playbook Studio 우선`이 충돌하지 않는다.

## 15. Reranker / 고급 retrieval 도입

상태: `done`

목표:
- 코퍼스 cleanup 이후에 reranker를 붙여 retrieval ceiling을 한 단계 올린다.

이번 단계에서 한 일:
- [x] cross-encoder reranker 도입 범위와 비용 기준 확정
- [x] 현재 fusion top-n 이후 rerank slot 삽입
- [x] reranker on/off 비교 평가
- [x] 현재 기본값은 `off`, 실험은 `--enable-reranker`/`.env` 기준으로만 켜도록 정리

검증:
- [x] `pytest -q tests/test_settings_paths.py tests/test_retrieval_core.py tests/test_app_ui.py tests/test_answering_answerer.py` -> `165 passed`
- [x] `python scripts/run_retrieval_eval.py --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_report_reranker_off.json`
- [x] `python scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_root_cause_reranker_off.json`
- [x] `python scripts/run_retrieval_eval.py --enable-reranker --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_report_reranker_on.json`
- [x] `python scripts/run_retrieval_eval.py --cases manifests/retrieval_root_cause_cases.jsonl --enable-reranker --output ..\\ocp-rag-chatbot-data\\retrieval\\retrieval_eval_root_cause_reranker_on.json`

현재 결론:
- reranker slot 자체는 들어갔다. 현재 구조는 `fusion top-N -> reranker -> final top-k`다.
- 기본 실험 모델 `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` 는 현재 OCP 한국어 코퍼스에선 **개선보다 회귀**가 컸다.
- default eval 기준:
  - reranker off: `hit@1 0.8125 / hit@3 0.875 / hit@5 0.9375`
  - reranker on: `hit@1 0.6875 / hit@3 0.9375 / hit@5 0.9375`
- root-cause eval 기준:
  - reranker off: `hit@1 1.0 / hit@3 1.0 / hit@5 1.0`
  - reranker on: `hit@1 0.8333 / hit@3 0.9167 / hit@5 1.0`
- 따라서 현재 generic multilingual cross-encoder는 제품 기본값으로 켜지 않는다.
- 다음 실험은 더 강한 한국어/다국어 reranker 후보를 `--reranker-model` override로 비교하는 방식으로 가는 게 맞다.

## 16. 운영성 / 재현성 / 출시 준비

상태: `done`

목표:
- 제품 시연과 운영 테스트를 다시 하기 쉬운 상태로 만든다.

이번 단계에서 한 일:
- [x] 세션 영속화 대신 최소 재현 로그 전략을 `chat_turns.jsonl + runtime snapshot` 기준으로 확정
- [x] `play_book.cmd runtime` / `scripts/check_runtime_endpoints.py` 기준 runtime report 자동화
- [x] [QUICKSTART.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/QUICKSTART.md) 로 배포/시연용 quickstart 정리
- [x] `ENTRYPOINTS.md`에 legacy shim / entrypoint freeze 기준 확정

검증:
- [x] `pytest -q tests/test_runtime_report.py tests/test_settings_paths.py tests/test_app_ui.py`
- [x] `play_book.cmd runtime --skip-samples`
- [x] `play_book.cmd --help`

현재 결론:
- 세션은 여전히 memory-only지만, `chat_turns.jsonl`에 per-turn runtime snapshot이 남아서 재현 기준선은 확보됐다.
- 운영자는 이제 `play_book.cmd runtime` 한 번으로 앱/pack 정체성, endpoint probe, artifact 존재 여부, 최근 turn 요약을 한 파일로 볼 수 있다.
- 시연 순서는 [QUICKSTART.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/QUICKSTART.md), canonical entrypoint와 freeze 기준은 [ENTRYPOINTS.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/ENTRYPOINTS.md)에 고정했다.

## 17. 변경 로그

- 2026-04-07: 구조개편 우선 순서에 맞춰 TODO 문서 전면 재작성
- 2026-04-07: 최소 구조개편 1차 완료. `play_book_studio` 패키지, 새 CLI 경로, `server.py` 1차 책임 분리 반영
- 2026-04-08: CLI/eval baseline 복구, 공개 import surface 1차 shim 복구, `load_settings()` env 오염 제거, one-off 실험 파일 `tmp/` 격리
- 2026-04-08: `Play Book Studio` 브랜딩 적용, OCP pack 위계 정리, 좌측 자료 선택 패널과 답변 메타 1차 단순화
- 2026-04-08: answer quality 보수 완료. MCO/보안/follow-up 분기 수정, 4.20 코퍼스 기준 eval 기대값 정렬, `play_book.cmd eval` 1.0 회복
- 2026-04-08: 구조개편 1차 이후 제품화 다음 단계 순서를 8~14번으로 재정의
- 2026-04-08: OCP 우선 전략, 한글/번역 lane, 지속 업데이트 파이프라인 요구를 반영해 다음 단계 순서를 8~16번으로 재정의
- 2026-04-08: source catalog와 approved runtime manifest를 분리하고, manifest diff / raw html fingerprint 기반 업데이트 추적 1차를 반영
- 2026-04-08: retrieval shaping 3차 완료. update locator / operator / MCO / concept diversification 규칙을 정리하고 root-cause retrieval eval을 현재 승인 코퍼스 기준으로 재정렬
- 2026-04-08: 답변 품질 / citation UX 2차 완료. 짧은 답변 템플릿, clarification 톤 정리, answer eval 1.0 회복, RAGAS 재점검 결과를 고정
- 2026-04-08: UI productization 2차 완료. 채팅 패널 중심 대비 강화, 좌우 패널 밀도 축소, 우측 탭 primary/secondary 위계 정리
- 2026-04-08: 품질 라운드 재점검. `.env` 기반 RAGAS judge 설정을 복구했고, 운영 답변 grounding(`etcd 백업`, `oc adm top nodes`, `namespace admin`, `monitor-certificates`)을 더 보수적으로 조정한 뒤 `answer eval 1.0`, `RAGAS faithfulness 0.8125`, `retrieval benchmark hit@5 0.8667`를 다시 확인

## 18. 멀티버전 코퍼스 / 플레이북 제품화 순서

상태: `in_progress`

이 단계부터는 단순 RAG MVP가 아니라, `고품질 한글 코퍼스 + 사람이 읽는 플레이북 문서`를 함께 만드는 제품 단계로 본다.

합의된 실행 순서는 아래와 같다.

### 18-1. version-aware crawler 설계

목표:
- OCP 버전과 언어를 인지하는 자동 크롤러 기준선을 만든다.

이번 단계에서 할 일:
- [x] 버전별 / 언어별 / `html-single` URL catalog 생성 규칙 설계
- [x] 한글 페이지 fallback 탐지 규칙 설계
- [x] `source_fingerprint` / 원문 hash 저장 규칙 설계
- [x] `4.16 ~ 4.21` 범위를 같은 구조로 수집할 수 있게 source catalog schema 확장
- [x] `settings -> models -> manifest -> collector -> build_source_manifest.py` 1차 구현 반영
- [x] runtime은 global catalog 중 현재 `ocp_version/docs_language` subset만 읽도록 연결

완료 조건:
- 새 버전이 올라와도 수집 규칙을 다시 손으로 짜지 않는다.
- `어떤 버전 / 어떤 언어 / 어떤 source 상태인지`를 catalog만 보고 설명할 수 있다.

현재 결과:
- [x] default source catalog 경로를 `manifests/ocp_multiversion_html_single_catalog.json` 로 전환
- [x] `SourceManifestEntry` 에 `product/version/language/source_state/resolved_*` 필드 추가
- [x] `build_source_manifest.py --versions --languages` 지원
- [x] approval / data quality / runtime manifest loading 이 global catalog subset 구조를 이해함
- [x] 검증: `tests/test_settings_paths.py tests/test_ingestion_manifest.py tests/test_ingestion_audit.py tests/test_ingestion_normalize.py` `30 passed`
- [x] 검증: `tests/test_runtime_report.py tests/test_app_ui.py tests/test_answering_answerer.py tests/test_retrieval_core.py` `166 passed`

### 18-2. canonical doc AST 설계

목표:
- 코퍼스용 구조와 사람이 읽는 문서 구조를 동시에 만들어낼 공통 AST를 정의한다.

이번 단계에서 할 일:
- [x] 아래 노드를 공통 schema로 설계
  - `heading`
  - `prerequisite`
  - `procedure step`
  - `code block`
  - `note / warning`
  - `table`
  - `anchor`
- [x] `src/play_book_studio/canonical` 패키지 생성
- [x] `CanonicalDocumentAst / CanonicalSectionAst / typed block` 모델 추가
- [x] `AST -> corpus projection` baseline 추가
- [x] `AST -> playbook projection` baseline 추가
- [x] `validate_document_ast()` 기본 검증 규칙 추가
- [x] 현재 `normalized section`과 새 AST의 관계를 설계 문서로 정리
- [x] HTML 정규화 결과가 실제로 `AST -> corpus projection -> NormalizedSection` 경로를 타게 연결
- [ ] PDF / 업로드 자료가 같은 AST로 들어오게 실제 정규화 경계 연결
- [ ] 현재 `normalized section` 생성 경로를 AST projection 기반으로 전부 전환

완료 조건:
- 한 번 정규화하면 이후 `코퍼스 출력`과 `문서 출력`이 같은 원천 구조에서 나온다.

현재 결과:
- [x] [CANONICAL_AST_DESIGN.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/CANONICAL_AST_DESIGN.md) 로 공통 AST 설계 기준 고정
- [x] [models.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/models.py) 에 `heading / prerequisite / procedure / code / note-warning / table / anchor` typed block 구현
- [x] [project_corpus.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_corpus.py) 에서 corpus projection baseline 구현
- [x] [project_playbook.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_playbook.py) 에서 playbook projection baseline 구현
- [x] [validate.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/validate.py) 에서 기본 validation 구현
- [x] [html.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/html.py) 에서 HTML section -> AST 조립 baseline 구현
- [x] [normalize.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/normalize.py) 가 이제 `AST -> corpus projection` 결과를 `NormalizedSection`으로 내보냄
- [x] 검증: `tests/test_canonical_models.py tests/test_ingestion_normalize.py tests/test_retrieval_core.py tests/test_answering_answerer.py tests/test_app_ui.py` `171 passed`

### 18-3. dual output pipeline

목표:
- 정규화 결과를 두 가지 제품 출력으로 만든다.

이번 단계에서 할 일:
- [x] `AST -> corpus artifacts` 경로 설계
- [x] `AST -> playbook document / viewer artifacts` 경로 설계
- [x] 코드 블록 박스, 복사 버튼, wrap / overflow 제어 등 매뉴얼형 렌더링 요구 반영
- [x] “검색 잘 되는 데이터”와 “읽기 좋은 문서”가 같은 소스에서 일관되게 생성되게 만들기

현재 결과:
- [x] `ingestion/pipeline.py`가 같은 HTML source에서 `normalized_docs.jsonl`과 `playbook_documents.jsonl`/`playbooks/<slug>.json`을 같이 만든다.
- [x] `source_books.py`가 internal viewer에서 playbook artifact를 우선 열고, 없을 때만 normalized section fallback을 쓴다.
- [x] viewer code block에 `복사 / 줄바꿈 / 넓게 보기` 컨트롤을 넣었다.
- [x] 검증: `tests/test_settings_paths.py tests/test_ingestion_normalize.py tests/test_canonical_models.py tests/test_app_ui.py tests/test_answering_answerer.py tests/test_retrieval_core.py` `189 passed`

완료 조건:
- 같은 source에서 retrieval용 코퍼스와 viewer용 플레이북 문서가 동시에 생성된다.

### 18-4. translation lane

목표:
- 영어 fallback 문서를 제외하지 않고 제품 파이프라인 안으로 넣는다.

이번 단계에서 할 일:
- [x] 상태 흐름을 `en_only -> translated_ko_draft -> approved_ko`로 고정
- [x] 번역 대상 우선순위와 승인 기준 정리
- [x] 코퍼스 출력과 문서 출력 둘 다 번역 lane을 타게 설계
- [x] 영문 원문 / 번역 초안 / 승인본의 provenance를 남기기

현재 결과:
- [x] `translation_lane.py`가 번역 단계, 다음 상태, corpus/playbook 출력 모드, provenance를 공통 규칙으로 계산한다.
- [x] `approval_report.py`와 `build_source_approval.py`가 `translation_lane_report.json`을 같이 만든다.
- [x] HTML -> AST -> `normalized_docs.jsonl` / `playbook_documents.jsonl` 경로에 `translation_stage`, `translation_source_language`, `translation_source_url`, `translation_source_fingerprint`가 남는다.
- [x] 검증: `tests/test_settings_paths.py tests/test_canonical_models.py tests/test_ingestion_normalize.py tests/test_ingestion_audit.py tests/test_retrieval_core.py tests/test_answering_answerer.py tests/test_app_ui.py` `197 passed`
- [x] 실제 리포트: `translation_lane_report.json` 기준 `book_count=113`, `active_queue_count=39`, `translation_required=23`, `translated_ko_draft=0`

완료 조건:
- “한글이 없으니 제외”가 아니라 “어떤 단계로 제품 안에 편입되는지”가 분명해진다.

### 18-5. 4.20 품질 완성

목표:
- 현재 서비스 기준 버전인 4.20에서 먼저 제품 품질 기준선을 완성한다.

이번 단계에서 할 일:
- [x] retrieval 품질 강화
- [x] answer quality 강화
- [x] viewer quality 강화
- [x] code block UX를 공식 매뉴얼 수준에 가깝게 다듬기

현재 결과:
- [x] `retrieval_benchmark_cases.jsonl`의 MCO 계열 기대값을 현재 `approved_ko` 코퍼스 현실에 맞게 정렬했다.
- [x] `book_adjustment_discovery.py`, `book_adjustment_operations.py`, `scoring.py`에서 MCO concept / reboot follow-up이 `support`나 `hosted_control_planes`로 과도하게 새는 가중치를 바로잡았다.
- [x] retrieval benchmark: `30 cases / hit@1 0.9 / hit@3 0.9333 / hit@5 1.0`
- [x] answer eval: `18 cases / pass_rate 1.0`
- [x] RAGAS: `faithfulness 0.6875 / answer_relevancy 0.4516 / context_precision 1.0 / context_recall 0.75`
- [x] 플레이북 viewer를 공식 매뉴얼처럼 읽히도록 hero / section card / procedure card / note / table / code toolbar 위계를 한 단계 더 정리했다.
- [x] 플레이북 문서에서 `법적 공지 초록` 잔존 `0`, 숫자 콜아웃은 `1. ...` 형식으로 병합, 코드 캡션과 표 헤더가 viewer까지 연결된다.
- [x] RAGAS 입력은 `답변:` prefix, citation, fenced code 노이즈를 제거한 semantic response 기준으로 정규화했다.
- [x] 검증: `pytest -q` -> `264 passed, 8 warnings`

완료 조건:
- 4.20 기준으로 `코퍼스 품질`과 `플레이북 문서 품질` 둘 다 제품 수준 기준선을 만족한다.

### 18-6. 4.16 ~ 4.21 확장

목표:
- 4.20에서 검증된 파이프라인을 다른 버전으로 확장한다.

이번 단계에서 할 일:
- [ ] `4.16 ~ 4.21`에 대해 full 또는 delta 방식으로 확장
- [ ] 버전별 catalog / manifest / corpus / playbook 산출물 생성
- [ ] 버전 차이로 인한 source gap / 번역 lane / 문서 품질 차이를 추적

완료 조건:
- 멀티버전 OCP 문서가 같은 제품 규칙으로 수집/정규화/문서화된다.

현재 원칙:
- 아키텍처는 처음부터 멀티버전 기준으로 설계한다.
- 품질 완성은 먼저 4.20에서 닫는다.
- 이후 `4.16 ~ 4.21`은 full 또는 delta 전략으로 확장한다.
- 2026-04-08: 제품 문구 2차 정리. 참조 패널/자료 패널/상단 액션의 문구를 더 짧고 자연스럽게 다듬고, 관련 UI 회귀 테스트를 현재 톤 기준으로 갱신
- 2026-04-08: 제품 UX 3차 정리. 보관함/업로드 패널의 헤더 위계와 빈 상태 문구를 단순화하고, 업로드 액션 버튼 우선순위를 `초안 저장 -> 초안 보기 -> 수집 -> 정리 -> 결과 보기` 흐름으로 정리
- 2026-04-09: semantic artifact contract 정리 완료. `part1~part4` alias를 코드에서 제거하고 외부 data dir도 `corpus / retrieval / answering / runtime` 기준으로 정리
- 2026-04-09: 문서 기준선 정리 완료. 핵심 운영 문서를 `.gitignore`에서 해제하고, `VENDOR_NOTES.md`와 구조 백로그를 현재 `play_book_studio` 기준으로 전면 갱신
