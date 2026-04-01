# OCP 운영 도우미 v2

폐쇄망에서 사용할 수 있는 **OCP 운영 가이드 챗봇**입니다.  
OpenShift 공식 문서 원천을 기반으로 검색하고, 한국어로 답변하며, 답변에 붙은 출처를 누르면 내부 HTML 문서가 열리도록 구성했습니다.

## 이 프로젝트가 하는 일

- 한국어 질문을 받습니다.
- 공식 OCP 문서를 근거로 답변합니다.
- 답변에 출처를 붙입니다.
- 출처를 누르면 HTML 문서가 열립니다.
- 멀티턴 문맥을 유지합니다.
- 폐쇄망 반입과 refresh/activate/rollback 흐름을 고려한 구조를 갖고 있습니다.

## 현재 상태

현재 `main` 기준으로 아래가 확인되었습니다.

- 로컬 UI: `http://127.0.0.1:8000`
- 스트리밍 응답 동작
- 한국어 기본 질문 응답
- citation click-through 동작
- 멀티턴 세션 유지
- validation corpus 기준 retrieval / multiturn / red-team / runtime smoke 검증 완료

다만 최종 판정은 **conditional-go** 입니다.

뜻:

- 시연, 검증, 내부 개발용으로는 충분히 동작합니다.
- 하지만 특정 minor 버전에 고정된 운영 릴리즈로 보기에는 추가 검증이 더 필요합니다.

## 빠르게 보기

- 실행용 기준 문서: [fixed-context-brief.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/fixed-context-brief.md)
- 절대 기준 문서: [fixed-context.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/fixed-context.md)
- 저장소 구조 안내: [repository-map.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/repository-map.md)
- 현재 진행 요약: [project-plan-summary.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/project-plan-summary.md)
- 10단계 검증 계획: [ten-stage-verification-plan.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/ten-stage-verification-plan.md)
- 라이브 런타임 검증: [stage08-live-runtime-quality-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage08-live-runtime-quality-report.md)
- 최종 릴리즈 판정: [stage10-final-release-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage10-final-release-report.md)

## v2 본체

핵심 런타임 파일:

- 게이트웨이: [ocp_runtime_gateway.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_runtime_gateway.py)
- OpenDocuments 브리지: [opendocuments_openai_bridge.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/opendocuments_openai_bridge.py)
- 정책 엔진: [ocp_policy.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_policy.py)
- 멀티턴 메모리: [multiturn_memory.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/multiturn_memory.py)
- UI: [runtime_chat.html](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/static/runtime_chat.html)

데이터 파이프라인:

- 정규화: [normalize_openshift_docs.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/ingest/normalize_openshift_docs.py)
- source profile: [source-profiles.yaml](/C:/Users/soulu/cywell/ocp-rag-chatbot/configs/source-profiles.yaml)

운영/배포 경로:

- 기동: [start_runtime_stack.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/start_runtime_stack.py)
- smoke: [run_live_runtime_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_live_runtime_smoke.py)
- refresh: [build_outbound_bundle.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/build_outbound_bundle.py)
- activate: [activate_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/activate_index.py)
- rollback: [rollback_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/rollback_index.py)

## 데이터와 RAG 구조

```text
openshift-docs / approved docs
  -> normalize (.adoc -> text + HTML viewer + metadata)
  -> OpenDocuments-compatible retrieval flow
  -> runtime gateway
  -> Korean answer + clickable citations
```

역할 분리는 이렇게 봐야 합니다.

- `openshift-docs`: 공식 문서 원천
- `OpenDocuments`: RAG 엔진 방향
- `ocp-rag-chatbot`: 실제 제품 레이어

## 로컬 실행

### 1. 런타임 계약 확인

```powershell
python deployment/check_runtime_contract.py
```

### 2. 런타임 기동

```powershell
python deployment/start_runtime_stack.py
```

브라우저에서 아래 주소로 접속합니다.

- [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 3. 라이브 smoke

```powershell
python deployment/run_live_runtime_smoke.py --output data/manifests/generated/manual-live-runtime-report.json
```

## 출처 방식

이 프로젝트에서 citation은 보조 정보가 아니라 핵심 요구사항입니다.

- 검색용 텍스트와 별도로 HTML viewer를 생성합니다.
- 문서 metadata에 `viewer_url` 과 section 정보가 들어갑니다.
- 답변의 출처를 누르면 실제 HTML 문서가 열립니다.

즉 “인용이 붙는다”가 아니라 **눌렀을 때 실제 문서가 열리는 것**까지 포함해서 검증합니다.

## 폐쇄망 운영 흐름

1. source mirror 갱신
2. 정규화 / diff 계산
3. outbound bundle 생성
4. 승인
5. inbound 반입
6. staging / reindex
7. smoke
8. activate
9. 필요 시 rollback

## 권위 문서

- retrieval / citation: [stage05-stage9-regression-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage05-stage9-regression-report.md)
- multiturn / red-team: [stage06-multiturn-redteam-regression-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage06-multiturn-redteam-regression-report.md)
- refresh / rollback: [stage07-refresh-activate-rollback-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage07-refresh-activate-rollback-report.md)
- live runtime / viewer: [stage08-live-runtime-quality-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage08-live-runtime-quality-report.md)
- 최종 gate: [stage10-final-release-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage10-final-release-report.md)
