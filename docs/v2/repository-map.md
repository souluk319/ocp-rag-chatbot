# v2 저장소 안내

이 문서는 **지금 이 저장소에서 무엇이 v2 본체이고, 무엇이 생성물이며, 무엇이 검증 자산인지** 빠르게 구분하기 위한 안내서다.

## 가장 먼저 볼 것

1. 제품 개요와 실행 진입점: [README.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/README.md)
2. 현재 단계와 상태 요약: [project-plan-summary.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/project-plan-summary.md)
3. 10단계 검증 기준: [ten-stage-verification-plan.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/ten-stage-verification-plan.md)

## v2 본체

### 제품 런타임

- 게이트웨이: [ocp_runtime_gateway.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_runtime_gateway.py)
- OpenDocuments 브리지: [opendocuments_openai_bridge.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/opendocuments_openai_bridge.py)
- 정책: [ocp_policy.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_policy.py)
- 멀티턴 메모리: [multiturn_memory.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/multiturn_memory.py)
- 런타임 보조: [runtime_gateway_support.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/runtime_gateway_support.py), [runtime_source_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/runtime_source_index.py), [runtime_config.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/runtime_config.py)

### 문서 온보딩 파이프라인

- 정규화 파이프라인: [normalize_openshift_docs.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/ingest/normalize_openshift_docs.py)

### 운영/실행 진입점

- 원커맨드 런치: [start_runtime_stack.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/start_runtime_stack.py)
- live runtime smoke: [run_live_runtime_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_live_runtime_smoke.py)
- refresh/reindex/activate/rollback: [build_outbound_bundle.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/build_outbound_bundle.py), [reindex_staged_bundle.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/reindex_staged_bundle.py), [activate_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/activate_index.py), [rollback_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/rollback_index.py)

### 설정

- source profile: [source-profiles.yaml](/C:/Users/soulu/cywell/ocp-rag-chatbot/configs/source-profiles.yaml)
- active source profile: [active-source-profile.yaml](/C:/Users/soulu/cywell/ocp-rag-chatbot/configs/active-source-profile.yaml)
- retrieval/answer policy: [rag-policy.yaml](/C:/Users/soulu/cywell/ocp-rag-chatbot/configs/rag-policy.yaml)

## 검증 자산

### retrieval / multiturn / red-team

- Stage 5 runner: [run_stage05_regression.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_stage05_regression.py)
- Stage 6 runner: [run_stage06_regression.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_stage06_regression.py)
- benchmark 입력: [p0_retrieval_benchmark_cases.jsonl](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/benchmarks/p0_retrieval_benchmark_cases.jsonl)
- multiturn 입력: [p0_multiturn_scenarios.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/benchmarks/p0_multiturn_scenarios.json)
- red-team 입력: [p0_red_team_cases.jsonl](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/benchmarks/p0_red_team_cases.jsonl)

### 단계별 권위 문서

- retrieval / citation 권위: [stage05-stage9-regression-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage05-stage9-regression-report.md)
- multiturn / red-team 권위: [stage06-multiturn-redteam-regression-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage06-multiturn-redteam-regression-report.md)
- refresh loop 권위: [stage07-refresh-activate-rollback-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage07-refresh-activate-rollback-report.md)
- serving path 권위: [stage08-live-runtime-quality-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage08-live-runtime-quality-report.md)

## 생성물과 운영 산출물

- generated evidence: `data/manifests/generated/`
- bundle / staging: `data/packages/`, `data/staging/`
- HTML citation views: `data/views/`
- 활성 index pointer: `indexes/current.txt`, `indexes/previous.txt`
- active runtime workspace: `workspace/stage11/`, `workspace/stage12/`

이 경로들은 대부분 **실행 결과물**이다. 코드의 본체가 아니라, 코드를 실행해 나온 증거와 런타임 데이터라고 보면 된다.

## 지금 기준으로 혼동하지 말아야 할 것

- 이 저장소의 현재 기준은 `rewrite/opendoc-v2` 이다.
- `release/v1` 과 `main` 은 별도 기준선이다.
- `docs/v2/` 안의 문서는 설계와 단계별 검증 문서다.
- `data/manifests/generated/` 안의 JSON 은 문서보다 더 낮은 수준의 실행 증거다.
- `OpenDocuments` 자체 코드는 이 저장소 안이 아니라 외부 경로에서 참조한다.
- `openshift-docs` 는 외부 공식 원천이고, 이 저장소는 그 위에 온보딩/정규화/정책/운영 계층을 얹는 제품 레포다.

## 지금 이 저장소를 보는 가장 빠른 순서

1. [README.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/README.md)
2. [repository-map.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/repository-map.md)
3. [project-plan-summary.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/project-plan-summary.md)
4. [stage08-live-runtime-quality-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage08-live-runtime-quality-report.md)
5. [start_runtime_stack.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/start_runtime_stack.py)
