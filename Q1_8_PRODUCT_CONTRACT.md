# Q1-8 Product Contract

## Purpose

이 문서는 구매자 질문 8개에 답하기 위한 `세일즈 스크립트`가 아니다.

이 문서는 현재 제품이 무엇을 약속할 수 있고, 무엇을 아직 약속할 수 없는지, 그리고 어떤 상태가 되어야 다음 상업 단계로 승격할 수 있는지를 잠그는 `제품 계약 문서`다.

이 문서의 기준선은 `문서 저장 / 문서 요약 / markdown viewer` 가 아니라 아래다.

`source-first figure-aware technical wiki runtime`

## Current Commercial Truth

현재 정직한 commercial truth 는 아래로 고정한다.

- 현재 단계: `paid_poc_candidate`
- 현재 범위: `OpenShift 4.20 source-first validated pack + customer document PoC + buyer/release packet surface`
- 현재 제품 정체성: `connected technical wiki for operation and learning`
- 현재 canonical form: `structured technical book + relation graph + figure asset + user overlay`

이 truth 를 흐리면 이 문서는 무효다.

## Product Identity Contract

Play Book Studio 는 아래를 만드는 제품이다.

1. `source-first corpus`
2. `structured technical books`
3. `entity / section / figure relation graph`
4. `chatbot grounded on the same runtime`
5. `user overlay for operation and learning`
6. `buyer/demo/release packet surface`

즉 이 제품은

- raw manual mirror 가 아니고
- markdown viewer 가 아니고
- generic chatbot wrapper 가 아니고
- static knowledge base 도 아니다.

이 제품은 `문서와 실행 맥락을 연결한 technical wiki runtime` 이다.

## What We Promise Now

현재 단계에서 약속하는 것은 아래다.

### 1. Source-First Technical Wiki

- 공식 source repo 를 우선 사용한다.
- repo source 가 없을 때만 html-single fallback 을 쓴다.
- source provenance 를 잃지 않는다.

### 2. Runtime-Level Reading Experience

- 문서는 `book` 으로 읽힌다.
- 엔터티는 `entity hub` 로 탐색된다.
- 절차는 `related section` 으로 다시 진입 가능하다.
- 그림은 `figure asset` 및 `figure page` 로 연결된다.

### 2A. Runtime Reader Contract

- 위키 본문은 `reader-grade paragraph shaping` 을 유지해야 한다.
- 긴 설명 본문은 문단 단위로 분리되어야 하며, 과도한 한 문단 몰아쓰기를 허용하지 않는다.
- 절차, 코드, 표, 주의문은 paragraph 와 다른 block 으로 유지한다.
- 본문 가독성은 `paragraph width`, `line-height`, `section spacing` 을 기준으로 관리한다.
- figure 와 diagram 은 기본적으로 `본문보다 약간 좁은 comfortable width` 로 렌더한다.
- figure 는 기본 화면에서 과도하게 가로폭을 점유하지 않아야 하며, 필요할 때만 확대 또는 원문 이동으로 상세 확인을 유도한다.
- screenshot 성격 figure 와 semantic diagram 은 같은 크기 정책으로 묶지 않는다.
- viewer CSS 기본값이 reader contract 를 대신하면 안 되며, contract 위반은 product issue 로 본다.

### 3. Grounded Chat

- 챗봇은 같은 active runtime 위에서 답한다.
- 답변은 `citation -> viewer -> source trace` 로 이어진다.
- related navigation 은 `book / entity / optional section` 우선순위로 제공된다.

### 4. Personalization Overlay

- favorites
- checks
- private notes
- recent positions

을 저장할 수 있다.

- overlay 행동은 `next plays` 와 `usage signals` 로 다시 제품에 반영된다.
- overlay 는 공용 본문을 수정하지 않는다.

### 5. Customer Pack Boundary

- customer document 는 별도 pack 경계 안에서만 취급한다.
- customer document 도 `customer_source_first_pack` lane 으로 parsed lineage 를 가진다.
- public / official / private / mixed bundle truth 를 숨기지 않는다.
- customer PoC 는 product boundary 안에서만 약속한다.

## What We Explicitly Do Not Promise Yet

현재 단계에서 아직 약속하지 않는 것은 아래다.

1. 모든 포맷 완벽 지원
2. 모든 diagram semantic parsing 완성
3. 모든 고객 문서의 zero-touch automatic promotion
4. full-sale 단계
5. unrestricted remote provider usage
6. 완성된 범용 enterprise knowledge platform

## Runtime Requirements

현재 제품이 technical wiki 라고 부르려면 최소 아래가 살아 있어야 한다.

### A. Book Layer

- active runtime books
- source trace
- section anchor
- code block
- figure support
- reader-grade paragraph shaping
- figure comfortable-width rendering

### B. Wiki Layer

- entity hub
- related books
- related sections
- backlinks
- related figures

### C. Chat Layer

- grounded citations
- related navigation
- active runtime path usage

### D. Personalization Layer

- overlay storage
- next play derivation
- control tower usage signal

### E. Customer Pack Layer

- customer source-first lane
- pack identity
- approval and publication state
- official/private/mixed boundary label

이 중 하나라도 빠지면 `technical wiki runtime` 이 아니라 기능 축소 상태로 본다.

## Eight Buyer Questions Reframed

기존의 Q1~Q8 표는 이제 질문 목록이 아니라 `제품 계약 축`으로 해석한다.

### Q1. 이 제품은 정확히 무엇인가?

답: `source-first technical wiki runtime`

fail 조건:

- raw manual mirror 로 설명됨
- markdown viewer 로 설명됨
- generic chatbot 로 설명됨

### Q2. 공식성과 근거는 어떻게 보장하나?

답: `source provenance + authority tier + runtime citation`

fail 조건:

- source trace 부재
- authority tier 부재
- fallback source 가 공식 source 처럼 보임

### Q3. 문서 품질은 어떻게 product-grade 로 올라가나?

답: `parse -> structured book -> relation runtime -> active runtime`

fail 조건:

- parsed artifact 없음
- runtime lineage 없음
- figure 있는 문서가 text-only 로만 노출됨

### Q4. 사용자는 실제로 무엇을 보게 되나?

답: `book + entity hub + figure + chat jump + related navigation`

fail 조건:

- static 문서 열람 수준에 머묾
- 위키 탐색이 안 됨
- 절차 재진입이 안 됨

### Q5. 기술 문서의 코드와 그림을 다루나?

답: `code block + figure asset + figure relation`

fail 조건:

- 코드가 raw text 로 노출됨
- figure-heavy 문서가 text-only 로 노출됨
- figure 가 source trace 없이 분리됨
- 긴 본문이 reader-grade 개행 없이 벽처럼 노출됨
- figure 가 viewer 폭을 과도하게 점유해 읽기 경험을 방해함

### Q6. 고객사 문서도 다룰 수 있나?

답: `customer document PoC within security boundary`

fail 조건:

- pack boundary 없음
- public/private 혼합
- unreviewed private asset 노출

### Q7. 사용자가 자기 작업공간처럼 쓸 수 있나?

답: `overlay + next play + usage signal`

fail 조건:

- overlay 가 공용 본문을 오염시킴
- 개인화가 runtime 랭킹과 분리됨
- 사용 흔적이 운영 신호로 환원되지 않음

### Q8. 지금 사도 되나?

답: `paid PoC 는 가능, full sale 은 아직 아니다`

fail 조건:

- unsupported assertion 존재
- owner scorecard 미통과
- audit/session 조건 미충족

## Release And Promotion Boundary

현재 단계에서 `full sale` 로 승격하려면 아래가 모두 충족되어야 한다.

- `owner_critical_scenario_pass_rate >= 0.90`
- `evidence_linked_answer_rate >= 0.95`
- `unsupported_assertion_rate == 0`
- `clarification_miss_count == 0`
- `demo_hard_miss_count == 0`
- `persisted_session == true`
- `audit_trail == true`
- `customer_document_reference_case_count >= 1`

하나라도 비면 `paid_poc_candidate` 또는 `pilot` 까지만 허용한다.

## Hard Blockers

아래는 즉시 fail 이다.

1. unsupported assertion
2. clarification miss
3. unreviewed asset exposure
4. source trace missing
5. pack boundary blur
6. text-only runtime for figure-heavy docs
7. active runtime 와 citation path 불일치
8. overlay 가 공용 본문 편집처럼 동작

## Forbidden Framing

아래 표현은 금지한다.

- `그냥 문서를 예쁘게 보여주는 제품`
- `markdown 으로 정리된 문서 플랫폼`
- `generic chatbot with docs`
- `어떤 문서든 바로 product-grade 위키가 된다`
- `지금 바로 full sale 가능`
- `그림이나 다이어그램은 나중에 붙이면 된다`
- `개인화는 부가 기능이라 나중에 해도 된다`

## Required Evidence Pointers

이 문서의 주장에 붙는 핵심 증거 자산은 아래로 고정한다.

- `TASK_BOARD.yaml`
- `OWNER_SCENARIO_SCORECARD.yaml`
- `data/wiki_runtime_books/active_manifest.json`
- `data/wiki_relations/*`
- `reports/build_logs/ocp420_one_click_runtime_report.json`
- `reports/build_logs/full_rebuild_wiki_relations_report.json`

이 증거 자산이 현재 truth 와 어긋나면, 이 계약 문서는 다시 검토해야 한다.
