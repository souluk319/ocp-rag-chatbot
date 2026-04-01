# Cache Strategy Proof

## Purpose

이 문서는 planB에서 추가한 캐싱 전략이 단순 코드 존재 여부를 넘어, 실제로 **hit/miss**, **TTL/LRU**, **grounding 유지**를 증거로 보여줄 수 있음을 정리한다.

## What is currently implemented

### 1. Embedding cache

- 위치: `app/opendocuments_openai_bridge.py`
- 구조: process-local TTL + LRU
- 대상: 로컬 `BAAI/bge-m3` 임베딩 결과
- 키: `model + input + dimensions`

### 2. Query cache

- 위치: `app/ocp_runtime_gateway.py`
- 구조: process-local TTL + LRU
- 대상: deterministic local rescue payload
- 키: `route + query + mode + rewritten_query + active_index_id + selected memory fields`

## Safety rules

- cache hit가 나도 `commit_runtime_grounding(...)`를 다시 수행해 멀티턴 세션 정합성을 유지한다.
- bridge `/ready`는 embedding cache를 우회하고 실제 local embedding readiness를 본다.
- `max_items <= 0` 또는 `ttl_seconds <= 0`이면 캐시는 비활성화된다.

## Evidence script

캐시 전략 증거는 아래 스크립트로 생성한다.

```bash
python3 eval/cache_strategy_report.py
```

기본 출력 경로:

- `data/manifests/generated/cache-strategy-report.json`

## What the report proves

### Embedding cache proof

- 첫 동일 요청은 miss
- 두 번째 동일 요청은 hit
- local embedding generation은 1회
- 차원 계약은 `1024`
- local embedding error는 0

### Query cache proof

- deterministic local rescue payload가 cache write 후 hit됨
- cached payload의 answer/sources가 원본과 동일함
- cache hit 후에도 grounding state가 top source를 유지함

이 proof는 **live gateway 전체 응답 캐시**를 증명하는 것이 아니다. 현재 증명 범위는 manifest-backed local rescue payload reuse에 한정된다.

또한 이 리포트는 TTL/LRU 구현 자체가 존재함을 전제로 삼지만, **TTL 만료나 eviction을 직접 재현하는 성능/수명 테스트 리포트는 아직 아니다.**

## Scope note

현재 query cache는 **전체 chat path**를 캐시하지 않는다.

현재 증명 범위는 다음으로 한정된다.

- manifest-backed local rescue path

즉, 이 문서는 “모든 질의 응답을 캐시한다”는 주장용이 아니라, **과제 요구사항의 캐싱 전략을 실제 코드와 증거로 설명하기 위한 좁은 범위의 1차 proof**다.

## Next evidence gap

이후 추가로 보강할 증거는 다음이다.

- widened corpus 기준 hit/miss 리포트
- cache invalidation 운영 문서
- 실제 성능 차이 비교 보고서
