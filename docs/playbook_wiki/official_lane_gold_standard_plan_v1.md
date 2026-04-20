---
status: reference
doc_type: lane-plan
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# Official Lane Gold Standard Plan v1

이 문서는 PBS의 `official source-first lane`을 어떻게 gold standard로 완성할지 정의한다.

핵심 질문은 하나다.

`PBS에서 가장 믿을 수 있고 가장 잘 보여야 하는 책은 무엇이며, 그 기준은 어떻게 고정되는가`

## 1. 왜 official lane이 먼저 gold standard여야 하는가

PBS에는 여러 입력 lane이 있지만,
그중 가장 안정적이고 가장 엄격한 기준선을 세우기 좋은 곳은 official lane이다.

이유:

- source identity가 비교적 안정적이다
- 문서 계보와 최신성 판단이 상대적으로 쉽다
- source-first renewal에 맞는 품질 실험이 가능하다
- user lane보다 noise와 boundary 변수가 적다

즉 official lane은 단지 한 lane이 아니라,
PBS 전체의 `표준선` 역할을 해야 한다.

## 2. 공식 lane의 역할

official lane은 아래 넷을 동시에 보여줘야 한다.

1. `source fidelity`
2. `reader-grade playbook quality`
3. `chat-grade corpus quality`
4. `same-truth runtime discipline`

즉 official lane은
`잘 가져온 source`
`잘 읽히는 책`
`잘 답하는 챗봇`
`정확한 citation`
이 동시에 성립하는 reference implementation이어야 한다.

## 3. 기본 원칙

### 3.1 Source-first

공식 lane은 기본적으로 아래를 따른다.

- repo / AsciiDoc first
- published HTML/PDF는 benchmark, verification, fallback

원칙:

- published artifact를 기본 truth로 삼지 않는다
- repo source가 살아 있으면 source-first를 유지한다

### 3.2 Translation completion, not deletion

공식 lane에서 영어 본문이 보인다고 해서
삭제/격하/격리하는 것이 기본 행위가 아니다.

기본 복구 순서는:

- translation lane 연결
- completion
- gold promotion

### 3.3 Brand-grade is mandatory

official lane 산출물은 단지 structure-grade면 안 된다.

최소 조건:

- reader-grade pass
- brand-grade pass
- chat-grade pass

### 3.4 Same truth across surfaces

official lane은 가장 먼저 아래를 만족해야 한다.

- viewer가 보는 책
- corpus가 검색하는 chunk
- chat이 쓰는 grounding
- citation이 점프하는 landing

이 네 개가 같은 truth를 공유해야 한다.

## 4. Official Lane Target Flow

목표 흐름은 아래로 고정한다.

`Official Source -> Canonical Knowledge -> Playbook Compose -> Corpus Derive -> Viewer/Chat Runtime`

세부 단계:

1. manifest pin
2. source collect
3. normalize
4. semantic object extraction
5. merge/update
6. playbook composition
7. corpus derivation
8. runtime binding
9. validation gate

## 5. What Official Gold Standard Must Guarantee

## 5.1 Source Fidelity

보장해야 할 것:

- source lineage 명확
- chapter/section provenance 추적 가능
- supersession/freshness 판단 가능
- published artifact와의 비교 검증 가능

fail 예:

- source lineage 없음
- 최신 source 반영 실패
- repo truth와 rendered truth drift

## 5.2 Reader-Grade Playbook

보장해야 할 것:

- chapter opener 품질
- section rhythm 안정성
- procedure/code/table/figure fidelity
- summary and detail balance
- 읽고 싶고 읽기 쉬운 editorial quality

fail 예:

- 문서 dump 느낌
- flattened structured block
- hierarchy confusion

## 5.3 Brand-Grade Playbook

보장해야 할 것:

- PBS page grammar 일관성
- source rail 존재
- operator checklist / summary discipline
- related play navigation

fail 예:

- generic wiki feel
- generic markdown export feel
- page family inconsistency

## 5.4 Chat-Grade Corpus

보장해야 할 것:

- grounded chunk derivation
- answer/citation consistency
- procedure and command answerability
- contradiction traceability

fail 예:

- weak citation landing
- viewer/chat truth drift
- unsupported synthesis

## 5.5 Runtime Discipline

보장해야 할 것:

- same-truth binding
- manifest alignment
- partial refresh 가능성
- stable runtime identity

fail 예:

- viewer는 갱신됐는데 corpus는 예전 상태
- answer는 최신인데 viewer는 예전 상태

## 6. Promotion Rules for Official Lane

official lane에서 `promoted`가 되려면 아래를 모두 만족해야 한다.

- parse-grade pass
- reader-grade pass
- brand-grade pass
- chat-grade pass
- source lineage intact
- freshness handling intact

즉 official lane은 `viewer-only ready`로 오래 머무는 것이 기본이 아니다.
goal은 `full promoted standard`다.

## 7. Current Known Risks

현재 official lane에서 계속 주의해야 하는 risk는 아래다.

- translation incompletion
- structure loss during normalize
- same-truth drift between viewer/corpus/chat
- runtime hot path pressure
- citation landing weakness

즉 official lane은 품질 기준선이지만,
동시에 PBS의 hardest correctness test이기도 하다.

## 8. Validation Expectations

official lane closeout에는 아래 evidence가 있어야 한다.

- representative books set
- source-to-page lineage sample
- viewer screenshots
- chunk/citation sample
- multi-turn grounded chat sample
- runtime timing snapshot

## 9. Packet Order for Official Lane

official lane에 대해 바로 들어가야 할 packet 순서는 아래다.

1. source-first truth hardening
2. translation completion discipline
3. knowledge object extraction quality
4. playbook composer application
5. same-truth runtime binding verification
6. representative gold standard validation set

## 10. Relationship to User Lane

official lane와 user lane는 경쟁 관계가 아니다.

관계는 아래다.

- official lane: PBS gold standard
- user lane: repair and promotion discipline lane

즉 official lane이 먼저 잘 되어야
user lane도 `무엇을 향해 올라가야 하는지`를 알 수 있다.

## 11. Non-Goals

- official lane를 데모용 cosmetic lane으로 만들지 않는다
- published HTML만 보고 official lane를 완성된 것으로 간주하지 않는다
- user lane의 느슨한 기준을 official lane에 적용하지 않는다

## 12. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`이 official Playbook은 PBS가 가장 자신 있게 보여줄 수 있는 기준선이며, viewer와 chat이 같은 truth를 쓰고 있는가`
