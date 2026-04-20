---
status: reference
doc_type: contract
audience:
  - codex
  - engineer
  - designer
  - operator
last_updated: 2026-04-20
---

# Playbook Composer Contract v1

이 문서는 PBS가 `knowledge object graph`를 `브랜드 Playbook`으로 조립하는 규칙을 정의한다.

이 문서의 질문은 하나다.

`좋은 지식이 어떻게 좋은 책이 되는가`

## 1. 목적

Composer는 parser가 아니다.
Composer는 renderer만도 아니다.

Composer의 역할은 아래 세 가지다.

1. `knowledge selection`
2. `chapter/page assembly`
3. `reader-grade and brand-grade composition`

즉 composer는 `무엇을`, `어떤 순서로`, `어떤 형식으로`, `어떤 우선순위로` 책에 올릴지를 결정한다.

## 2. 기본 원칙

### 2.1 Source-first, but not source-dump

원문 충실도는 유지하되, source를 page에 그대로 쏟아붓지 않는다.

원칙:

- source lineage는 살아 있어야 한다
- 책은 source dump가 아니라 편집된 결과물이어야 한다

### 2.2 Objects before pages

책은 파일을 이어붙인 결과가 아니라 object를 조립한 결과다.

우선 단위:

- concept
- entity
- procedure
- command
- warning
- table
- figure
- claim
- operator note

### 2.3 Summary first, detail second

독자는 먼저 목적과 방향을 잡고, 그 다음 세부를 읽어야 한다.

모든 chapter/page는 아래 순서를 기본으로 가진다.

- intent
- summary
- operational detail
- validation
- lineage
- related plays

### 2.4 Operational readability beats decorative freedom

Composer는 예쁜 장식보다 작업 가독성을 우선한다.

즉:

- hierarchy first
- procedure clarity
- code/table fidelity
- source visibility

## 3. Inputs

Composer의 입력은 raw markdown이 아니라 아래다.

- `knowledge objects`
- `source lineage`
- `quality gates`
- `lane context`
- `rendering profile`

### 3.1 Knowledge Objects

주요 입력 타입:

- entity
- concept
- procedure
- command
- warning
- table
- figure
- claim
- operator_note

### 3.2 Source Lineage

모든 주요 block은 source lineage를 추적할 수 있어야 한다.

Composer는 최소한 아래를 알고 있어야 한다.

- source kind
- source title
- section anchor
- official/private lane
- freshness

### 3.3 Quality Gates

Composer는 gate를 무시하지 않는다.

예:

- parse-grade fail인 block은 decorated rendering 대상이 아님
- reader-grade fail 산출물은 playbook promotion 대상이 아님
- chat-grade fail object는 corpus promotion에서 제외 가능

### 3.4 Lane Context

lane에 따라 composition strictness가 다를 수 있다.

- official source-first lane
- user upload repair lane
- derived operator note lane

## 4. Outputs

Composer 출력은 최소 세 가지다.

1. `chapter structure`
2. `page block tree`
3. `lineage and related-play rails`

즉 composer는 단순 HTML string이 아니라,
`책을 어떻게 읽게 할지에 대한 구조`를 생산해야 한다.

## 5. Composition Stages

## 5.1 Stage A: Select

목적:

- 어떤 object가 이번 chapter/page에 들어갈지 고른다

기준:

- topic fit
- source trust
- freshness
- operational value
- redundancy

기본 규칙:

- 같은 의미의 중복 block는 줄인다
- 새로운 source가 기존 object를 enrich/revise했으면 최신 상태를 우선한다
- contradiction는 숨기지 않고 별도로 surface한다

## 5.2 Stage B: Group

목적:

- object를 chapter/page 단위로 묶는다

기본 grouping 규칙:

- concept는 개념 section으로
- entity는 sidecard 또는 glossary성 block로
- procedure와 command는 operate cluster로
- warning은 관련 procedure 근처로
- table/figure는 이를 이해하는 section 근처로

중요:

- procedure는 paragraph sea 안에 잠기면 안 된다
- command는 관련 procedure 없이 떠다니면 안 된다

## 5.3 Stage C: Order

목적:

- 읽는 순서를 결정한다

기본 ordering rhythm:

1. chapter opener
2. overview / what
3. why / context
4. how / procedure
5. commands and examples
6. validation
7. cautions and edge cases
8. source lineage
9. related plays

예외:

- reference-heavy chapter는 concept/entity를 더 앞에 둘 수 있다
- procedure-heavy chapter는 operate cluster를 더 빨리 올릴 수 있다

## 5.4 Stage D: Frame

목적:

- 각 object를 어떤 visual/semantic frame에 넣을지 결정한다

예:

- procedure -> procedure block
- command -> command plate
- warning -> warning/caution callout
- table -> table plate
- entity -> entity card
- note -> operator note block

원칙:

- frame은 object 의미를 강화해야지 흐리면 안 된다

## 5.5 Stage E: Link

목적:

- chapter 내부와 책 전체의 연결을 만든다

필수 연결:

- entity -> related concept
- concept -> related procedure
- procedure -> validation
- section -> source lineage
- page -> related plays

좋은 책은 단지 잘 정리된 page collection이 아니라,
`다음에 어디를 읽어야 할지 자연스럽게 이어지는 책`이어야 한다.

## 5.6 Stage F: Compress

목적:

- 너무 많이 담겨서 흐려지는 것을 막는다

규칙:

- 중요 summary를 먼저 남긴다
- 중복 detail은 줄인다
- 동일 claim의 반복은 피한다
- 덜 중요한 raw detail은 progressive disclosure로 내린다

즉 composer는 많이 넣는 엔진이 아니라,
`독자가 가장 잘 읽게 정리하는 엔진`이어야 한다.

## 6. Chapter Contract

모든 chapter는 아래 6개 중 최소 4개를 가져야 한다.

- chapter opener
- overview block
- concept or procedure core
- validation block
- source rail
- related play block

procedure-heavy chapter는 아래를 추가로 우선한다.

- prerequisites
- ordered steps
- rollback or caution
- output example

## 7. Page Block Contract

page는 아래 block만 허용한다.

- opener
- section header
- summary block
- concept block
- entity card
- procedure block
- command plate
- table plate
- figure block
- warning/caution/note
- validation block
- source rail
- related play rail
- glossary card

block 자유도는 무한정 열지 않는다.
PBS identity는 제한된 block grammar에서 나온다.

## 8. Lineage Contract

Composer는 source lineage를 장식처럼 다루지 않는다.

최소 규칙:

- chapter 단위 primary lineage
- section 단위 local lineage
- claim 또는 procedure 근처 citation trace
- stale/conflict signal

독자는 아래를 항상 볼 수 있어야 한다.

- 이 말이 어디서 왔는가
- 최신인가
- 공식인가
- 충돌하는 source가 있는가

## 9. Lane-Specific Composition

## 9.1 Official Lane

원칙:

- chapter coherence를 강하게 본다
- source authority를 높게 반영한다
- translation completeness가 중요하다
- brand-grade 기준을 엄격히 적용한다

## 9.2 User Upload Lane

원칙:

- repair confidence를 먼저 본다
- structure confidence가 낮으면 draft framing 유지
- human refinement affordance를 남긴다
- source boundary를 더 명확히 드러낸다

즉 user lane는 처음부터 polished playbook처럼 과장하지 않는다.

## 10. Fail-Safe Rules

아래 경우 composer는 멋지게 포장하지 않는다.

- flattened structured block
- weak lineage
- unresolved contradiction
- missing procedure framing
- unstable anchor

대신:

- draft/review framing 유지
- promotion 금지
- repair or review lane로 되돌린다

## 11. Acceptance Criteria

Composer contract가 유효하다고 보려면 아래가 가능해야 한다.

1. 같은 object set으로도 chapter/page 조립 이유를 설명할 수 있다
2. procedure-heavy page가 paragraph soup로 무너지지 않는다
3. source lineage가 책 품질을 해치지 않으면서도 보인다
4. official lane와 user lane의 책 느낌 차이를 설명할 수 있다
5. viewer-grade page와 chat-grade truth가 같은 object graph를 공유한다

## 12. Non-Goals

- 이 문서는 CSS guide가 아니다
- 이 문서는 parser spec이 아니다
- 이 문서는 단순 컴포넌트 목록표가 아니다

## 13. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`이 chapter는 문서 조각을 모아놓은 것이 아니라, PBS가 의도를 가지고 편집한 Playbook처럼 읽히는가`
