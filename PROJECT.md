---
status: active
doc_type: product_charter
audience:
  - codex
  - engineer
  - product
precedence: 2
supersedes:
  - PROJECT.md (legacy version)
  - README.md
  - P0_ARCHITECTURE_FREEZE_ADDENDUM.md (product naming portions)
last_updated: 2026-04-17
---

# PROJECT

## Product One-Liner

Playbook Studio 는 `공식 문서, 운영 가이드, 트러블슈팅 자료를 연결된 위키 대백과와 grounded chat runtime 으로 바꾸는 제품`이다.

핵심은 문서를 저장하는 것이 아니라 아래를 자동으로 만드는 것이다.

- `reader-grade technical library`
- `connected wiki navigation`
- `grounded chat corpus`
- `precise citation landing`
- `buyer/demo/release packet evidence`

## Renewal Frame

PBS 는 이미 `award-winning enterprise product` 이고 `2026 best product` 중 하나로 선정된 상태다.

현재 단계는 `reinvention` 이 아니라 아래 기준의 `renewal` 이다.

- `refinement`
- `hardening`
- `validation`
- `customer order execution`

현재 주문은 `OCP operators` 를 위한 `OpenShift playbook package delivery` 이며,
이 작업은 `기존 PBS architecture 안에서 수행` 해야 한다.

## Current Renewal Scope

현재 운영 기준선은 아래다.

- `renewal_hardening_validation stage`
- `OpenShift 4.20 official source-first validated pack`
- `customer order: OCP operator playbook package delivery`
- `customer/private pack lane when explicitly ordered`

## Product Surfaces

제품 표면은 아래 세 가지로 고정한다.

1. `Playbook Library`
   - library index
   - runtime / candidate / signal state
   - control-tower style status view
2. `Wiki Runtime Viewer`
   - 본문 읽기
   - related books / sections / figures / entities 탐색
   - 정확한 anchor jump
3. `Chat Workspace`
   - grounded answer
   - citation
   - next play
   - related navigation

`Control Tower` 는 별도 최상위 surface 가 아니라 `Playbook Library` 안의 운영 view 로 취급한다.

## What Must Beat Vendor Docs

최종 문서는 최소한 vendor official docs 보다 아래 항목에서 더 나아야 한다.

1. `findability`
   - 필요한 절차/개념/트러블슈팅을 더 빨리 찾을 수 있어야 한다.
2. `readability`
   - 긴 문서를 더 적은 피로도로 읽을 수 있어야 한다.
3. `grounded jump`
   - 챗봇 citation 이 문서의 정확한 문단/표/그림으로 점프해야 한다.
4. `figure-aware learning`
   - 그림, 표, 캡션, 절차가 끊기지 않아야 한다.
5. `connected navigation`
   - 문서, 엔터티, 절차, 관련 그림이 자연스럽게 이어져야 한다.

## Product Promises

이 제품은 아래를 약속한다.

1. 공식 source 와 허용된 fallback source 를 수집해 재현 가능한 corpus 를 만든다.
2. raw 문서를 사람이 읽을 수 있는 technical library 로 재구성한다.
3. 같은 기준선에서 library 와 chatbot 이 동작하게 만든다.
4. 챗봇 답변은 library anchor 로 되돌아갈 수 있어야 한다.
5. customer/private 문서는 같은 아키텍처 안에서 `pack boundary labeled runtime` 으로 다룬다.
6. 고객 주문용 package output 도 기존 PBS shared truth 와 surface model 안에서 파생한다.

## Non-Promises

현재 단계에서 아래는 아직 약속하지 않는다.

- 모든 포맷 완벽 지원
- 임의 문서의 zero-touch product-grade 승격
- full-sale stage
- 완전 자동 semantic parsing for every diagram
- renewal 기간 중 무근거한 product reinvention

## Source Authority

진실 계층은 아래로 고정한다.

1. `Vendor Official Source`
2. `Reviewed Translation`
3. `Verified Operational Evidence`
4. `Playbook Synthesis`
5. `Model Prose`

하위 tier 는 상위 tier 를 보강할 수는 있어도 뒤집을 수 없다.

## Locked Product Doctrine

- 이 제품은 `markdown viewer` 가 아니다.
- 이 제품은 `connected technical wiki + grounded chat` 다.
- chat 은 library 와 다른 진실을 말하면 안 된다.
- library 는 corpus 와 다른 원천을 가지면 안 된다.
- overlay 는 본문을 덮지 않고 보조 레이어로 남는다.
- buyer/demo/release packet 은 제품 증거 surface 이지, core reader surface 를 대체하지 않는다.
- commercial packet 이나 rehearsal score 는 supporting evidence 일 뿐이며, core runtime/retrieval/citation quality gate 를 대체하지 않는다.
- 현재 주문은 PBS 자체를 다시 정의하는 작업이 아니라, 기존 PBS architecture 위에서 deliverable 을 실행하는 작업이다.

## Current Focus

현재 우선순위는 아래다.

1. `renewal hardening and validation`
2. `OCP operator playbook package delivery`
3. `corpus 와 citation 정합성 고정`
4. `official source-first operator coverage`
5. `reader / runtime hardening`
6. `customer/private pack lane stability when ordered`
