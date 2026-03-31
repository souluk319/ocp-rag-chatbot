# OCP Operations Assistant v2

폐쇄망에서 사용할 수 있는 **OCP 운영도우미 RAG 챗봇**입니다.

이 저장소는 OpenShift 공식 문서 원천을 정규화하고, OpenDocuments 기반 RAG 흐름 위에 OCP 전용 정책, 멀티턴 메모리, HTML 출처 클릭, 폐쇄망 refresh loop 를 얹은 **제품 레이어**를 담고 있습니다.

## 이 프로젝트가 하는 일

- 한국어 질문을 받는다
- OCP 공식 문서를 근거로 답한다
- 답변에 citation 을 붙인다
- citation 을 누르면 실제 HTML 문서가 열린다
- follow-up 질문에서도 문맥과 버전을 유지한다
- 문서 갱신 시 bundle -> reindex -> activate -> rollback 흐름을 갖는다

## 지금 무엇이 통과됐나

현재 `rewrite/opendoc-v2` 기준으로 아래가 검증되어 있습니다.

- widened corpus 기준 retrieval / citation gate 통과
- multiturn / red-team gate 통과
- refresh / activate / rollback 메커니즘 통과
- live runtime / viewer / citation click-through 통과
- company-only runtime contract 유지
- 임베더 baseline `BAAI/bge-m3`, `1024` 차원 유지

다만 최종 판정은 **validation-mode 기준 conditional-go** 입니다.

이 뜻은:

- 제출/시연/검증용으로는 충분히 설명 가능하고 실제로 동작한다
- 하지만 특정 operator-release minor 에 고정된 최종 운영 릴리즈로는 아직 미인증이다

## 가장 먼저 어디를 보면 되나

1. 저장소 구조 안내: [repository-map.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/repository-map.md)
2. 현재 상태 요약: [project-plan-summary.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/project-plan-summary.md)
3. 10단계 검증 계획: [ten-stage-verification-plan.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/ten-stage-verification-plan.md)
4. 최근 serving-path 권위 문서: [stage08-live-runtime-quality-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage08-live-runtime-quality-report.md)

## v2 본체

### 제품 런타임

- gateway: [ocp_runtime_gateway.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_runtime_gateway.py)
- bridge: [opendocuments_openai_bridge.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/opendocuments_openai_bridge.py)
- policy: [ocp_policy.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_policy.py)
- memory: [multiturn_memory.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/multiturn_memory.py)

### 온보딩 파이프라인

- 정규화: [normalize_openshift_docs.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/ingest/normalize_openshift_docs.py)
- source profile: [source-profiles.yaml](/C:/Users/soulu/cywell/ocp-rag-chatbot/configs/source-profiles.yaml)

### 실행/운영 경로

- 런타임 기동: [start_runtime_stack.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/start_runtime_stack.py)
- live smoke: [run_live_runtime_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_live_runtime_smoke.py)
- refresh/activate/rollback: [build_outbound_bundle.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/build_outbound_bundle.py), [activate_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/activate_index.py), [rollback_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/rollback_index.py)

## 데이터와 RAG 구조

```text
openshift-docs / approved docs
  -> normalize (.adoc -> text + HTML viewer + metadata)
  -> index through OpenDocuments-compatible flow
  -> runtime gateway
  -> Korean grounded answer + clickable citations
```

역할 분리는 이렇게 봐야 합니다.

- `openshift-docs`: 공식 원천 데이터
- `OpenDocuments`: RAG 엔진 기준 구현
- `ocp-rag-chatbot`: 제품화 레이어

## 빠른 실행

### 1. 런타임 계약 확인

```powershell
python deployment/check_runtime_contract.py
```

### 2. 런타임 기동

```powershell
python deployment/start_runtime_stack.py --hold-seconds 10
```

### 3. live runtime smoke

```powershell
python deployment/run_live_runtime_smoke.py --output data/manifests/generated/manual-live-runtime-report.json
```

## 출처 방식

이 프로젝트의 citation 은 보조 정보가 아니라 핵심 요구사항입니다.

- 검색용 text 와 별도로 HTML viewer 를 생성한다
- source metadata 에 `viewer_url` 과 section 정보가 있다
- 응답의 citation 을 누르면 HTML 문서가 열린다
- Stage 8 기준으로 section title alignment 까지 확인한다

즉 “문서가 열린다”가 아니라, **인용한 섹션이 실제로 보이는가**를 검증한다.

## 폐쇄망 운영 방식

문서 업데이트는 자동 반영이 아니라 승인형 refresh loop 기준입니다.

1. source mirror 갱신
2. 정규화와 diff 계산
3. outbound bundle 생성
4. 승인
5. inbound 반입
6. staging / reindex
7. smoke
8. activate
9. 필요 시 rollback

## 관련 권위 문서

- retrieval / citation: [stage05-stage9-regression-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage05-stage9-regression-report.md)
- multiturn / red-team: [stage06-multiturn-redteam-regression-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage06-multiturn-redteam-regression-report.md)
- refresh / rollback: [stage07-refresh-activate-rollback-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage07-refresh-activate-rollback-report.md)
- live runtime / viewer: [stage08-live-runtime-quality-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage08-live-runtime-quality-report.md)

## 브랜치 기준

- `main`: 안정 기준선
- `release/v1`: 이전 구현 보존
- `rewrite/opendoc-v2`: 현재 v2 작업 브랜치
