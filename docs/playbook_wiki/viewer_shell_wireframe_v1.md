---
status: reference
doc_type: wireframe-spec
audience:
  - codex
  - engineer
  - designer
  - operator
last_updated: 2026-04-21
---

# Viewer Shell Wireframe v1

이 문서는 PBS의 `reader-first shell`을 구현 직전 수준의 와이어 기준으로 정의한다.

핵심 질문:

`화면의 어느 면이 무엇을 책임지고, 사용자는 어떤 순서로 읽고 움직이며, 어느 순간 studio sidecar가 개입하는가`

## 1. Primary Screen Model

기본 화면은 아래 네 면으로 고정한다.

1. `Top Bar`
2. `Left Rail`
3. `Center Reading Stage`
4. `Right Context Rail`

추가로 필요 시 `Studio Sidecar`가 열린다.

기본 우선순위:

- 읽기
- 탐색
- 판단 보조
- 편집

즉 편집은 읽기를 깨뜨리지 않는 보조 계층이어야 한다.

## 2. Desktop Default Wireframe

```text
+----------------------------------------------------------------------------------+
| Top Bar: product / playbook title / search / mode switch / actions              |
+-------------------------+--------------------------------+-----------------------+
| Left Rail               | Center Reading Stage           | Right Context Rail    |
| - library context       | - chapter opener               | - on-page outline     |
| - current book tree     | - summary band                 | - source rail         |
| - chapter nesting       | - article body                 | - related plays       |
| - current location      | - procedure/code/table blocks  | - chat adjacency      |
|                         | - citations                    |                       |
+-------------------------+--------------------------------+-----------------------+
| Optional Studio Sidecar opens as docked split beside center/right area           |
+----------------------------------------------------------------------------------+
```

## 3. Panel Responsibility Table

| Surface | Primary Role | Must Show | Must Not Become |
| --- | --- | --- | --- |
| Top Bar | global orientation and mode control | title, search, reader/studio switch | badge dump or noisy dashboard |
| Left Rail | structural navigation | library context, current book tree, active section | generic file explorer |
| Center Reading Stage | actual reading | chapter opener, summary, body, code/table/callout | editing canvas |
| Right Context Rail | contextual judgment | TOC, source rail, related plays, chat entry | second main content area |
| Studio Sidecar | annotation and refinement | note, ink, inserted text card, edited card tools | full replacement for reading stage |

## 4. Top Bar Contract

필수 요소:

- PBS identity
- current playbook title
- reader/studio mode switch
- search or command entry
- lightweight action cluster

선택 요소:

- current lane signal
- view density toggle

금지:

- 긴 설명
- 상태 badge 나열
- 운영 대시보드 정보 과밀 노출

## 5. Left Rail Contract

왼쪽은 `책장 + 현재 책 구조`를 동시에 품는다.

기본 블록:

1. `book family context`
2. `current playbook tree`
3. `active location`

기본 규칙:

- current playbook tree가 주인공이다
- library 전체보다 현재 책 탐색이 우선이다
- active section이 스크롤 중에도 유지되어야 한다

추천 상호작용:

- chapter collapse/expand
- section click jump
- active section auto-follow

## 6. Center Reading Stage Contract

가장 중요한 면이다.

기본 구성 순서:

1. chapter opener
2. summary band
3. article body
4. local citations
5. related continuation

필수 block:

- chapter title
- operator summary
- concept/procedure body
- code/table/figure plates
- warning/caution blocks
- local citation anchors

금지:

- inline 편집 컨트롤 과다 노출
- context rail 정보 중복
- paragraph soup

## 7. Right Context Rail Contract

오른쪽은 `판단 보조` 면이다.

기본 순서:

1. current outline
2. source rail
3. related plays
4. chat adjacency

기본 규칙:

- 오른쪽은 조용해야 한다
- 본문보다 강하게 시선을 끌면 안 된다
- source rail은 여기서 가장 중요하다

채팅은 이 rail에서 `진입점`만 주고,
대화 자체는 workspace 전환 또는 drawer로 분리하는 방향이 안전하다.

## 8. Studio Sidecar Contract

studio sidecar는 `reading을 지키면서 작업을 붙이는 면`이다.

기본 역할:

- note 작성
- ink/pencil 입력
- inserted text card 생성
- edited card 편집
- refinement review

기본 원칙:

- source overwrite 금지
- reading stage 보존
- card/section 기준 저장

추천 형태:

- desktop: docked split pane
- tablet: slide-over panel or split pane

## 9. Viewport Rules

## 9.1 Wide Desktop

기본:

- left rail visible
- right rail visible
- center reading stage 최대 가독성 폭 유지
- studio sidecar는 dock 가능

## 9.2 Narrow Desktop / Small Laptop

기본:

- left rail collapsible
- right rail collapsible
- center reading stage 우선
- sidecar는 overlay dock 우선

## 9.3 Tablet

기본:

- reading stage 우선
- rails는 on-demand
- pen input 우선권 고려
- sidecar는 split 혹은 overlay

## 9.4 Mobile

기본:

- reading first
- rails는 drawer
- studio 기능은 최소화
- note/quick highlight 정도만 허용

## 10. Reading Flow

권장 읽기 흐름:

1. top bar에서 현재 책 identity 파악
2. left rail에서 현재 chapter 선택
3. center reading stage에서 chapter opener와 summary 확인
4. right rail에서 source와 related play 판단
5. 필요 시 studio sidecar 열어 메모 또는 수정본 작업

즉 사용자의 기본 흐름은 `탐색 -> 읽기 -> 판단 -> 작업`이다.

## 11. Mode Transitions

모드 전환은 아래 두 개만 먼저 둔다.

- `Reader Mode`
- `Studio Mode`

Reader Mode:

- reading shell 최대화
- sidecar 닫힘 또는 최소화
- context rail은 source/outline 중심

Studio Mode:

- sidecar 열림
- note/ink/inserted text/edited card 도구 노출
- reading stage는 유지하되 보조 작업 공간과 나란히 감

중요:

- mode가 바뀌어도 현재 reading context는 유지된다

## 12. Storage Unit Mapping

화면의 작업 요소는 아래 저장 단위와 직접 연결돼야 한다.

| UI Action | Storage Unit |
| --- | --- |
| quick note | `note` |
| pen stroke | `ink` |
| inserted text panel | `inserted_text_card` |
| refined block text | `edited_card` |
| bookmarked section | `favorite` or equivalent signal |

즉 wireframe은 시각 layout만이 아니라 저장 단위와 연결된 UX여야 한다.

## 13. First Implementation Scope

처음 구현 범위는 아래만 포함한다.

- top bar
- left rail
- center reading stage
- right context rail
- studio sidecar shell
- reader/studio mode switch

나중으로 미루는 것:

- full inline editing
- graph-heavy knowledge surface
- mobile advanced studio tools

## 14. Acceptance Criteria

이 wireframe이 구현 가능 상태라고 보려면 아래를 만족해야 한다.

1. 개발자가 panel responsibility를 헷갈리지 않는다
2. designer가 어디에 어떤 정보가 살아야 할지 분명하다
3. reader/studio 경계가 명확하다
4. source rail과 related play가 보조면으로 자리 잡는다
5. sidecar가 reading stage를 대체하지 않는다

## 15. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`이 와이어만 봐도 PBS가 GitBook급 reading shell 위에 Studio 작업면을 얹는 구조라는 점이 분명한가`
