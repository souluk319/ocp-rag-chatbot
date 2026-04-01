# Stage 3 완료 보고서

## 단계명

widened corpus retrieval 실패 원인 해부

## 목표

확장 코퍼스에서 실패하는 retrieval 케이스를 `question`, `rewrite`, `source_dir`, `document_path`, `citation` 관점으로 분해해서, 4단계 보정이 정확히 어디를 겨냥해야 하는지 고정하는 것이다.

## 적용 범위

- [s15c-core-smoke-report-bridge.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/s15c-core-smoke-report-bridge.json)
- [smoke-results.jsonl](/C:/Users/soulu/cywell/ocp-rag-chatbot/indexes/s15c-core/smoke-results.jsonl)
- [p0_retrieval_benchmark_cases.jsonl](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/benchmarks/p0_retrieval_benchmark_cases.jsonl)
- [staged-manifest.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/staging/s15c/manifests/staged-manifest.json)
- [analyze_stage03_retrieval_failures.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/analyze_stage03_retrieval_failures.py)

## 6인 역할

- `Creative-A`: 실패 질문을 사용자 의도 기준으로 재서술
- `Creative-B`: source drift와 install 편향 가설 정리
- `Expert-A`: raw retrieval / rerank 패턴 분석
- `Expert-B`: source_dir / metadata 표현 문제 분석
- `Inspector-A`: 실패 케이스별 question / expected / actual 표 정리
- `Inspector-B`: `question -> rewrite -> source_dir -> document_path -> citation` 축별 원인표 작성

## 수행 내용

- widened corpus smoke에서 retrieval alignment가 실패한 5개 케이스를 고정했다.
  - `RB-001`
  - `RB-004`
  - `RB-006`
  - `RB-010`
  - `RB-013`
- 실패 케이스별로 기대 문서와 실제 raw / reranked / citation 결과를 대조했다.
- Stage 3 전용 분석 스크립트를 추가했다.
  - [analyze_stage03_retrieval_failures.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/analyze_stage03_retrieval_failures.py)
- 현재 정책이 기대하는 source_dir / category 신호와 실제 retrieval 결과가 어디서 끊기는지 확인했다.

## 테스트

### 문법 검증

- `python -m py_compile eval\analyze_stage03_retrieval_failures.py`

### Stage 3 분석 실행

- `python eval\analyze_stage03_retrieval_failures.py --output data\manifests\generated\stage03-retrieval-root-cause-report.json`

생성 리포트:

- [stage03-retrieval-root-cause-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage03-retrieval-root-cause-report.json)

## 검증 결과

Stage 3은 완료로 판정한다.

핵심 요약:

- 실패 케이스 수: `5`
- `raw_installing_bias_count = 5`
- `source_id_mislabel_count = 5`
- `uniform_score_plateau_count = 5`
- `expected_doc_missing_from_raw_top10_count = 4`
- `citation_expected_miss_count = 5`

핵심 원인:

1. raw candidate의 `source_dir` 가 실제 top-level dir가 아니라 `openshift-docs-core-validation` 으로 기록되어, source_dir 기반 정책 신호가 사실상 먹지 않는다.
   - 현재 [run_opendocuments_stage6.mjs](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_opendocuments_stage6.mjs) 는 `document_path` 에서 source id를 제거하기 전에 `split('/')[0]` 으로 `source_dir` 를 계산한다.
2. raw retrieval top-10 점수가 케이스별로 거의 동일해서, 질문 차이가 dense candidate set에 반영되지 않는다.
3. raw candidate pool이 전부 `installing/*` 로 붕괴한다.
4. reranker는 잘못된 후보군 안에서만 재정렬하므로, 기대 문서를 구조적으로 구제하지 못한다.
5. citation 오류는 별도 1차 원인이 아니라, 잘못된 reranked top-1을 정확히 인용하는 downstream 결과다.

케이스별 해석:

- `RB-001`
  - 기대 문서는 raw top-10 안에 있었지만 reranker가 AWS install config 문서로 잘못 바꿨다.
- `RB-004`, `RB-006`, `RB-010`, `RB-013`
  - 기대 문서가 raw top-10 안에 아예 없었다.
  - 따라서 reranker가 구제할 수 없는 상태였다.

축별 결론:

- `question`
  - 질문 자체가 깨진 문제는 아니다.
  - 사용자 의도는 분명하지만 retrieval이 그 의도를 candidate set에 반영하지 못한다.
- `rewrite`
  - Stage 3 분석 기준 standalone rewrite는 기대 source_dir과 topic을 이미 포함한다.
  - 즉 rewrite 신호가 아예 없는 것이 아니라, retrieval path로 충분히 전달되지 않는다.
- `source_dir`
  - 현재 가장 큰 구조적 실패 지점이다.
  - 기대 source_dir가 `disconnected`, `support`, `post_installation_configuration` 이어도 실제 candidate는 `installing` 으로 무너진다.
- `document_path`
  - source_dir collapse의 결과로 generic install 문서가 top-1을 차지한다.
- `citation`
  - retrieval 실패의 downstream 결과다.
  - 잘못된 문서를 정확히 인용하는 상태에 가깝다.

## 정리 메모

- 4단계의 초점은 `reranker 튜닝` 자체가 아니라 아래 3개여야 한다.
  1. candidate `source_dir` 표현 복구
  2. raw retrieval 분별력 복구
  3. install 편향 완화

## 다음 단계

다음 활성 단계는 **4단계. retrieval 보정 1차**다.
