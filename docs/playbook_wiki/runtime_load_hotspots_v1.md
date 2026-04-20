---
status: reference
doc_type: perf-register
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# Runtime Load Hotspots v1

이 문서는 PBS에서 현재 확인된 `부하가 큰 지점`을 고정해 두는 레지스터다.

목적은 두 가지다.

1. `느리다`를 감으로 말하지 않고, 실제 hotspot 단위로 기억한다.
2. 이후 packet이 무엇을 줄였고 무엇이 아직 남았는지 closeout에서 비교 가능하게 만든다.

## 1. 운영 원칙

- hotspot은 `체감`이 아니라 `실제 경로`로 기록한다
- 원인은 `느림`이 아니라 `data-control-room cold`, `chat first-turn cold`, `reranker load`처럼 명명한다
- 성능 관련 packet은 이 문서를 갱신하거나 closeout에서 이 문서를 참조해야 한다

## 2. 현재 기준선

기준 ref:

- branch: `feat/ocp29-presentation-cutdown`
- head at measurement family: `588f65fe731cf80d90b5a3650559115995596759`

## 3. Hotspot Register

## 3.1 data-control-room cold build

### 현상

Studio / Control Tower 진입 시 첫 payload 생성이 매우 무겁다.

### 관측값

- cold request: 대략 `21s ~ 24s`
- log 예시:
  - `data-control-room 24.571s`
  - `data-control-room 22.194s`
  - `data-control-room 21.366s`
- cache hit after optimization:
  - `0.097s`
  - 실측 재호출 `176.7ms`, `222.0ms`, `523.5ms`

### 현재 판단

- 이건 `component swap` 문제가 아니라 `cold build / precompute / cache / bootstrap split` 문제다
- 반복 호출 비용은 많이 줄었고, 남은 문제는 `첫 계산 자체`

### 현재 조치 상태

- fingerprint-based cache 적용됨
- 다음 후보:
  - startup precompute
  - workspace bootstrap slimming

## 3.2 first chat cold-start

### 현상

backend 재기동 직후 첫 질문이 비정상적으로 느리다.

### 관측값

- 과거 baseline: 약 `30.6s`
- reranker warm-up 후 first chat: 약 `18.0s`
- second chat: 약 `9.3s`
- steady-state family: 약 `6.9s ~ 7.5s`

### 현재 판단

- `cold-start`는 줄었지만 아직 큼
- reranker warm-up만으로는 충분하지 않고,
  초기 runtime 경쟁과 first-answer path 최적화가 더 필요함

### 현재 조치 상태

- startup reranker warm-up 적용됨
- 다음 후보:
  - startup precompute 확대
  - first-turn answer path additional warm-up

## 3.3 LLM generate latency

### 현상

steady-state chat에서도 LLM generation이 큰 비중을 차지한다.

### 관측값

- external LLM direct call: 약 `2.5s`
- app steady trace family:
  - `llm_generate_total ~= 5.9s ~ 6.0s`

### 현재 판단

- 외부 LLM이 병목의 일부는 맞음
- 하지만 전체 느림의 유일 원인은 아님
- app 내부 local path를 같이 봐야 함

### 현재 조치 상태

- 별도 축소 없음
- 다음 후보:
  - prompt slimming
  - first-turn warm-up
  - retrieval context 압축 재검토

## 3.4 reranker local cost

### 현상

현재 reranker는 로컬 cross-encoder이고 cold-load와 steady 비용이 있다.

### 관측값

- current model:
  - `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
- steady trace family:
  - `rerank ~= 641ms`
- cold path:
  - backend logs에 `Loading weights` 확인

### 현재 판단

- 가장 비싼 한 방은 아니지만 `효율 대비 교체 후보`로는 강하다
- same-quality 혹은 multilingual quality가 더 좋은 대체재 검토 가치가 있음

### 현재 조치 상태

- startup warm-up 적용됨
- 다음 후보:
  - reranker externalization
  - lighter/stronger multilingual reranker 검토
  - 운영 토글 분리

## 3.5 chat post-processing

### 현상

예전에는 answer 뒤 payload build와 audit persist가 과하게 컸다.

### 관측값

예전 family:

- `payload_build` 최대 `4.3s`
- `chat_audit_persist` 약 `1.7s ~ 2.7s`

최적화 후 steady-state:

- `payload_build ~= 63ms`
- `payload_related_links ~= 39ms`
- `post_answer_total ~= 108ms`

### 현재 판단

- 이 hotspot은 많이 정리된 상태
- 완전히 제거된 건 아니지만 우선순위는 내려감

### 현재 조치 상태

- heavy runtime payload 제거
- audit/unanswered logging 경량화
- overlay signal short TTL cache 적용

## 3.6 upload / gold / corpus pipeline contention

### 현상

문서 생성 또는 gold/corpus 작업이 돌 때 chat 체감이 더 나빠질 수 있다.

### 관측 근거

- 발표 중 체감 이슈 반복
- gold embed / qdrant progress 로그 확인
- pipeline와 chat이 같은 로컬 자원을 경쟁하는 징후

### 현재 판단

- `pipeline/chat resource isolation`이 필요하다
- 일시정지/재개/우선순위 제어가 미래 기능 후보

### 현재 조치 상태

- 구조적 분리는 아직 없음
- 다음 후보:
  - background priority 분리
  - pause/resume orchestration
  - separate worker/resource lane

## 4. Hotspot Priority

현재 우선순위는 아래로 본다.

1. `user upload repair/promotion`
2. `data-control-room cold build`
3. `first chat cold-start`
4. `pipeline/chat contention`
5. `reranker replacement or externalization`

이 순서인 이유:

- 잘못된 source를 빨리 넣는 것보다, 정확한 truth를 늦게 넣는 편이 낫다
- same-truth product에선 부하보다 오염이 더 위험하다

## 5. Reporting Rule

앞으로 성능이나 부하와 관련된 packet closeout에는 아래 중 하나가 반드시 있어야 한다.

1. 이 문서 갱신
2. 이 문서 항목 번호를 인용한 변경/미변경 보고

최소 보고 형식:

- 어떤 hotspot을 건드렸는지
- 이전 관측값
- 이후 관측값
- 남은 gap
- 다음 우선순위

추가로 아래 판단도 반드시 남긴다.

- `계속 내부 유지`
- `교체 후보`
- `외부화 후보`

즉 hotspot packet은 단순히 느리다고 끝내지 않고,
`계속 안고 갈지`, `툴을 바꿀지`, `외부 고성능 리소스로 분리할지`
중 하나를 기록해야 한다.

## 6. Tool Swap / Externalization Rule

특정 단계가 품질 대비 과하게 무겁다면 아래를 검토한다.

1. 더 적합한 오픈소스 툴로 교체
2. 고성능 외부 리소스로 분리
3. 별도 worker/resource lane으로 격리

단, 아래는 금지다.

- provenance 손실
- source lineage 약화
- boundary contract 우회
- draft truth와 promoted truth 혼합

## 7. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`지금 PBS에서 무엇이 느리고, 왜 느리고, 어디까지 줄였고, 다음엔 무엇을 줄일지 문서로 설명할 수 있는가`
