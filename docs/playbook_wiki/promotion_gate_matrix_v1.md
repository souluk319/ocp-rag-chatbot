---
status: reference
doc_type: gate
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# Promotion Gate Matrix v1

이 문서는 PBS 산출물이 어떤 조건에서

- `draft`
- `review`
- `ready`
- `promoted`
- `quarantined`

상태를 갖는지 정의한다.

핵심 목적은 하나다.

`파싱이 됐다는 이유만으로 candidate artifact를 Playbook으로 오판하지 않게 한다.`

## 1. 기본 원칙

Playbook 승격은 단일 점수로 결정하지 않는다.

아래 네 축을 함께 본다.

1. `parse-grade`
2. `reader-grade`
3. `brand-grade`
4. `chat-grade`

원칙:

- 네 축 중 하나라도 fail이면 `Playbook promoted`가 될 수 없다
- `official lane`과 `user lane`은 같은 gate vocabulary를 쓰되, 기대 baseline은 다를 수 있다
- `reader-grade`와 `chat-grade`는 별개이며, 둘 중 하나만 좋아도 승격되지 않는다
- `brand-grade`는 장식 점수가 아니라 PBS identity consistency다

## 2. 상태 정의

### 2.1 draft

의미:

- ingest/normalize는 되었지만 품질이 불안정하다
- repair 또는 human review가 필요한 상태

허용:

- internal review
- workspace refinement

금지:

- Playbook Library gold exposure
- unrestricted corpus promotion

### 2.2 review

의미:

- 구조는 어느 정도 나왔지만 pass/fail 판단 또는 수리가 남아 있다

허용:

- reviewer confirmation
- repair rerun
- section-level edit

### 2.3 ready

의미:

- 특정 lane 목표에는 충분하지만 아직 최종 Playbook 승격 전일 수 있다

예:

- corpus-ready
- viewer-ready
- review-ready

주의:

- `ready`는 곧바로 `Playbook promoted`를 의미하지 않는다

### 2.4 promoted

의미:

- PBS Playbook 또는 corpus truth layer로 공식 승격된 상태

조건:

- required gates pass
- provenance intact
- lane-specific boundary satisfied

### 2.5 quarantined

의미:

- data contamination, broken lineage, severe structural failure, boundary issue 등으로 격리된 상태

## 3. Gate Matrix

## 3.1 Parse-Grade

### 목적

문서 구조와 semantic object를 얼마나 안정적으로 회수했는지 본다.

### pass 조건

- heading hierarchy가 section tree로 복원된다
- code/table/figure가 paragraph에 눌리지 않는다
- anchor 또는 section landing이 가능하다
- command/procedure distinction이 유지된다
- source lineage를 잃지 않는다

### fail 신호

- `structured_blocks_flattened`
- heading collapse
- command/code loss
- table header loss
- figure orphaning
- section anchor drift

### evidence

- normalized section payload
- block kind distribution
- rendered block fidelity sample
- source-to-section trace

### fail 시 기본 조치

- `draft` 또는 `review`로 내림
- repair lane 진입
- corpus promotion 금지

### 현재 PBS 주의 포인트

- PDF flattened structured block
- uploaded source의 table/code fidelity

## 3.2 Reader-Grade

### 목적

사람이 실제로 읽기 좋은가를 본다.

### pass 조건

- chapter opener가 목적을 분명히 전달한다
- section rhythm이 한눈에 보인다
- 절차, 경고, 명령, 설명이 섞이지 않는다
- 스크롤하며 읽을 때 위계가 유지된다
- summary와 detail의 균형이 있다

### fail 신호

- wall-of-text
- weak section hierarchy
- plain dump feel
- missing procedure framing
- unreadable code/table placement

### evidence

- rendered page screenshots
- representative chapter review
- block ordering audit

### fail 시 기본 조치

- `review`
- Playbook promotion 금지
- renderer/composer fix 또는 editorial repair 필요

## 3.3 Brand-Grade

### 목적

그 산출물이 PBS 책처럼 보이는지 본다.

### pass 조건

- chapter opener, source rail, checklist, callout grammar가 일관적이다
- PBS 고유의 page grammar가 반복된다
- decorative noise 없이 operational identity가 유지된다
- related play / next action affordance가 있다

### fail 신호

- generic wiki feel
- generic markdown export feel
- page마다 문법이 달라짐
- source rail 부재
- operator summary 부재

### evidence

- representative pages side-by-side
- brand checklist
- same family page consistency review

### fail 시 기본 조치

- `review`
- renderer/composer packet으로 환송

## 3.4 Chat-Grade

### 목적

챗봇이 이 truth를 grounded answer에 안전하게 쓸 수 있는지 본다.

### pass 조건

- claim과 chunk가 provenance를 유지한다
- citation jump landing이 유효하다
- contradictory claim이 표시되거나 정리된다
- procedure/command answer가 source-backed다
- multi-turn에서도 context drift가 작다

### fail 신호

- weak citation landing
- unsupported synthesis
- answer/viewer truth drift
- stale claim leakage
- ambiguous source boundary

### evidence

- multi-turn chat harness
- answer/citation consistency
- source landing smoke
- contradiction trace

### fail 시 기본 조치

- chat corpus promotion 금지
- chunking/retrieval/citation lane 수정

## 4. Lane-Specific Promotion Rules

## 4.1 Official Source-First Lane

기본 목표:

- `parse-grade: pass`
- `reader-grade: pass`
- `brand-grade: pass`
- `chat-grade: pass`

결과:

- `promoted playbook`
- `promoted corpus`

예외:

- 번역 미완료
- source lineage break
- contradiction unresolved

이 경우 `review` 또는 `quarantined`

## 4.2 User Upload Lane

기본 목표:

- ingest 직후 자동으로 `Playbook promoted` 금지
- 기본 상태는 `draft` 또는 `review`

승격 조건:

- repair pass
- section fidelity pass
- reader-grade pass
- chat-grade pass if corpus promotion is desired
- boundary contract satisfied

결과:

- `workspace draft`
- `review-ready candidate`
- 조건 충족 시에만 `promoted playbook`

## 5. Promotion Decision Table

### Case A

- parse: pass
- reader: fail
- brand: fail
- chat: pass

판정:

- `review`

설명:

- 검색은 되더라도 책은 아니다

### Case B

- parse: pass
- reader: pass
- brand: fail
- chat: pass

판정:

- `review`

설명:

- usable wiki일 수는 있어도 PBS Playbook은 아니다

### Case C

- parse: fail
- reader: fail
- brand: fail
- chat: fail

판정:

- `draft` 또는 `quarantined`

설명:

- repair 먼저

### Case D

- parse: pass
- reader: pass
- brand: pass
- chat: fail

판정:

- viewer-only `ready`
- corpus `not promoted`

설명:

- 읽을 책은 될 수 있어도 챗봇 truth로는 아직 위험하다

### Case E

- parse: pass
- reader: pass
- brand: pass
- chat: pass

판정:

- `promoted`

설명:

- PBS Playbook 승격 가능

## 6. Evidence Contract

승격 closeout에는 아래 evidence가 있어야 한다.

- representative rendered page
- source lineage sample
- chunk/citation sample
- chat answer landing sample
- known gap list

evidence 없는 승격은 허용하지 않는다.

## 7. Operational Rules

- `ready`와 `promoted`를 혼동하지 않는다
- user lane는 기본적으로 conservative promotion을 쓴다
- severe boundary issue는 quality score와 무관하게 `quarantined`
- promotion은 reversible해야 하며 source lineage는 남아야 한다

## 8. Non-Goals

- 이 문서는 scoring algorithm 자체가 아니다
- 이 문서는 UI badge copy 문서가 아니다
- 이 문서는 parser implementation detail 문서가 아니다

## 9. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`이 산출물은 parse가 된 문서가 아니라, PBS가 책임지고 승격해도 되는 Playbook 또는 Corpus인가`
