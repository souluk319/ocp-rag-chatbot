# 5단계 결과 보고

## 판정

`pass`

## 이번 단계에서 바꾼 것

- 정의형 질문은 `OpenDocuments` upstream 이 느리거나 흔들려도 게이트웨이에서 바로 답할 수 있게 fast path 를 추가했습니다.
- `runtime_gateway_support.py` 안의 `NameError` 때문에 local runtime rescue 가 500으로 죽던 문제를 고쳤습니다.
- `disconnected`, `architecture`, `post_installation_configuration` 계열이 이후 재인덱싱에서도 더 정확히 분류되도록 policy / category 규칙을 보강했습니다.
- Stage 5 직접 검증 스크립트를 추가해 `localhost:8000` 기준으로 바로 다시 확인할 수 있게 했습니다.

## 핵심 파일

- [app/ocp_runtime_gateway.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_runtime_gateway.py)
- [app/runtime_gateway_support.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/runtime_gateway_support.py)
- [app/ocp_policy.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_policy.py)
- [configs/rag-policy.yaml](/C:/Users/soulu/cywell/ocp-rag-chatbot/configs/rag-policy.yaml)
- [ingest/normalize_openshift_docs.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/ingest/normalize_openshift_docs.py)
- [deployment/check_stage05_direct_runtime.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage05_direct_runtime.py)

## 누가 검증했는가

- `Godel`: 정의형 질문 rescue 와 query-routing 최소 수정안 검토
- `Beauvoir`: corpus / metadata / source alignment 분석
- `Galileo`: direct runtime check 기준 제안
- 메인 에이전트: 실제 `localhost:8000` 재기동, 질문/출처/HTML viewer 직접 재현

## 직접 검증 결과

결과 파일:
- [stage05-direct-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-direct-runtime-report.json)

직접 통과한 질문:
- `오픈시프트가 뭐야`
- `OCP가 뭐야`
- `설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?`
- `업데이트 전에 확인해야 할 사항은 무엇인가요?`
- `폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?`

모든 케이스에서 확인한 것:
- `status_code = 200`
- 한국어 답변 존재
- citation 1개 이상 존재
- 첫 citation viewer 가 `200 text/html`

## 사용자 확인 체크포인트

1. [http://127.0.0.1:8000](http://127.0.0.1:8000) 접속
2. 아래 질문 중 하나 입력
   - `오픈시프트가 뭐야`
   - `설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?`
   - `업데이트 전에 확인해야 할 사항은 무엇인가요?`
   - `폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?`
3. 답변 하단 출처 클릭
4. HTML 원문이 열리면 통과

## 남긴 메모

- 이번 단계는 `localhost:8000` 에서 눈으로 확인되는 최소 동작 복구를 우선한 단계입니다.
- widened corpus 전체 raw retrieval benchmark 를 완전히 닫은 것은 아니므로, 다음 단계에서는 회귀 검증과 runtime/corpus 정합성을 이어서 봐야 합니다.
