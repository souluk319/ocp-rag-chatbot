# 1단계 완료 보고 - 기본 질문 구조 복구

## 단계 결과

1단계는 **완료**다.

핵심 목표였던 아래 세 질문이 모두 한국어 답변과 공식 citation 을 포함해 응답한다.

- `오픈시프트가 뭐야`
- `OCP가 뭐야`
- `OpenShift가 뭐야`

## 이번 단계에서 한 일

### 1. 정의 질문 판별 규칙 보강

- 기본 개념 질문을 `definition_intro` 규칙으로 인식하도록 보강했다.
- 한국어와 영문 혼합 질문 모두 intro 문서군으로 유도되게 했다.

관련 파일:

- [ocp_policy.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_policy.py)

### 2. 공식 소개 문서 기반 fallback 경로 추가

- retrieval 결과가 비어 있어도 기본 정의 질문은 공식 소개 문서로 안전하게 연결되도록 했다.
- 현재는 `architecture/index.adoc`, `architecture/architecture.adoc` 계열을 우선 사용한다.

관련 파일:

- [ocp_runtime_gateway.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_runtime_gateway.py)
- [runtime_gateway_support.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/runtime_gateway_support.py)

### 3. 답변 문장 정리

- 기본 개념 설명을 한국어 중심의 짧은 정의로 정리했다.
- `OCP` 질문에는 약자 풀어쓰기를 포함했다.
- 답변 끝에는 citation 블록이 붙도록 유지했다.

관련 파일:

- [runtime_gateway_support.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/runtime_gateway_support.py)

## 테스트

아래 테스트를 실제로 수행했다.

1. `POST /api/v1/chat`
2. 질의:
   - `오픈시프트가 뭐야`
   - `OCP가 뭐야`
   - `OpenShift가 뭐야`
3. viewer 링크 직접 호출:
   - `/viewer/openshift-docs-core-validation/architecture/architecture.html`

## 테스트 결과

- 세 질문 모두 `HTTP 200`
- 세 질문 모두 `matched_rules = ["definition_intro"]`
- 세 질문 모두 `source_count = 2`
- 첫 citation 은 `/viewer/openshift-docs-core-validation/architecture/architecture.html`
- viewer 직접 호출 `HTTP 200`
- viewer 응답 `text/html; charset=utf-8`

## 6명 검토 요약

### Ramanujan

- 정의 질문은 `architecture-first` 가 맞다고 판단
- intro 문서 rescue 가 필요하다는 의견 반영

### Arendt

- 답변은 짧고 설명적이어야 하며, Red Hat / 엔터프라이즈 Kubernetes 플랫폼 표현이 적절하다고 봄

### Peirce

- 현재 active corpus 에서 intro 근거로 가장 적절한 문서는 `architecture/index.adoc`, `architecture/architecture.adoc` 라고 판단

### Gibbs

- gateway / bridge / fallback 조합만으로 1단계는 충분히 닫을 수 있다고 봄

### Feynman

- pass 기준:
  - 한국어 답변
  - citation 존재
  - viewer 링크 정상성

### Russell

- 1단계는 backend 와 단계 완료 증거 문서 중심으로 묶는 것이 가장 깔끔하다고 판단

## 현재 판정

1단계는 **pass** 다.

## 다음 단계

다음은 2단계다.

- UI 문구 한글
- 스트리밍 한글
- 화면 상태 문구
- 브라우저 기준 최종 확인
