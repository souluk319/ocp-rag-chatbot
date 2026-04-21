---
status: reference
doc_type: shell-spec
audience:
  - codex
  - engineer
  - designer
  - operator
last_updated: 2026-04-21
---

# GitBook-Inspired Viewer Shell Spec v1

이 문서는 PBS가 구현할 `reader-first shell`의 목표 형태를 정의한다.

핵심 질문은 하나다.

`GitBook처럼 잘 정돈되고 읽기 좋은 문서 제품 감각을 가져오되, PBS만의 Playbook과 Studio 작업면을 어떻게 얹을 것인가`

## 1. 목적

이 문서는 아래 둘을 동시에 만족시키기 위해 필요하다.

1. `Playbook은 책처럼 읽혀야 한다`
2. `PBS는 스튜디오이므로 메모, 펜, 삽입 텍스트, 수정본 저장이 가능해야 한다`

즉 PBS는 아래 둘 중 하나만 되면 안 된다.

- 예쁜 문서 뷰어
- 강한 작업 캔버스

PBS의 목표는 아래다.

`GitBook급 읽는 경험 + PBS 고유의 Studio sidecar`

## 2. 기준 선언

GitBook은 `채택 대상`이 아니라 `벤치마킹 대상`이다.

즉 우리는 아래를 목표로 한다.

- GitBook의 정보 위계
- GitBook의 읽기 안정감
- GitBook의 문서 제품 완성도

하지만 아래는 PBS가 직접 가져야 한다.

- Playbook brand grammar
- same-truth binding
- studio annotation layer
- edited card / inserted note / ink storage

## 3. One-Line Product Shape

PBS viewer shell의 한 줄 정의:

`GitBook처럼 읽히고, Jupyter Book처럼 책답고, Quartz처럼 연결되며, LiquidText처럼 작업을 이어갈 수 있는 Playbook shell`

## 4. Layout Contract

기본 레이아웃은 4면 구조로 본다.

1. `global header`
2. `left navigation rail`
3. `center reading stage`
4. `right context rail`

필요 시 여기에 `studio sidecar`가 열릴 수 있다.

## 4.1 Global Header

역할:

- 현재 책 identity 표시
- mode 전환
- search / command access
- reading ↔ studio 전환

최소 요소:

- product identity
- current playbook title
- view mode switch
- search entry
- lightweight action cluster

금지:

- 무거운 설명 패널
- 의미 없는 badge 나열

## 4.2 Left Navigation Rail

역할:

- 책장/문서 계층
- 현재 책의 chapter tree
- related play access

구성:

- library / family context
- current playbook section tree
- chapter nesting
- current location highlight

원칙:

- hierarchy first
- 스크롤하면서도 현재 위치가 분명해야 함
- GitBook처럼 안정적이되, PBS book family 문법이 보여야 함

## 4.3 Center Reading Stage

역할:

- 본문 읽기
- chapter opener
- procedure / code / table / figure
- source-backed reading experience

구성:

- chapter opener
- article body
- embedded callout grammar
- code/table/figure plates
- source-aligned citations

원칙:

- 본문은 가장 먼저 읽기 좋아야 함
- 작업 기능이 본문을 오염시키지 않음
- paragraph soup 금지

## 4.4 Right Context Rail

역할:

- 현재 section TOC
- source lineage
- related plays
- AI/chat adjacency

구성 후보:

- on-page outline
- source rail
- related play rail
- current topic signals
- chat entrypoint

원칙:

- 오른쪽은 보조 판단면이지, 본문보다 더 시끄러우면 안 됨

## 4.5 Studio Sidecar

역할:

- 메모
- 펜
- 삽입 텍스트 카드
- 수정본 저장
- draft refinement

형태:

- 본문을 직접 덮지 않는 parallel sidecar
- LiquidText/Canvas 계열의 작업면 참고

원칙:

- reading stage를 보존
- source truth를 덮어쓰지 않음
- overlay / edited card / inserted note로 저장

## 5. Reader vs Studio Mode

### 5.1 Reader Mode

목표:

- 가장 좋은 독서 경험

우선순위:

- chapter rhythm
- structure clarity
- source-backed reading
- calm shell

### 5.2 Studio Mode

목표:

- 작업하면서 읽기

우선순위:

- notes
- ink
- inserted text cards
- section-level refinement
- edited card persistence

원칙:

- Studio mode가 Reader mode를 대체하지 않는다
- 기본값은 Reader-first

## 6. Article Frame Contract

모든 page는 아래 frame을 기본으로 가진다.

1. `chapter opener`
2. `summary band`
3. `article body`
4. `source rail and citations`
5. `related plays`
6. `studio overlays when enabled`

### 6.1 Chapter Opener

필수:

- title
- one-line promise
- operator summary
- current source lineage hint

### 6.2 Summary Band

필수:

- what this chapter gives you
- who this chapter is for
- what to do next if relevant

### 6.3 Article Body

필수:

- concept/procedure rhythm
- code/table fidelity
- callout grammar

### 6.4 Source Rail

필수:

- primary lineage
- freshness
- official/private signal
- jump affordance

### 6.5 Related Plays

필수:

- nearby concepts
- next operational step
- adjacent procedures

## 7. Editing Boundary Contract

viewer shell은 editor를 안쪽에 품되,
원문을 직접 수정하는 워드프로세서처럼 동작하면 안 된다.

편집은 아래 단위로 본다.

- `note`
- `ink`
- `inserted text card`
- `edited card`

즉 편집은 source overwrite가 아니라
`book-aware overlay and refinement layer`다.

## 8. Mobile and Tablet Rule

PBS는 desktop-first이지만 tablet/pen도 고려해야 한다.

원칙:

- tablet에서 펜 입력이 자연스러워야 함
- mobile에서는 reading 우선, studio는 절제
- narrow viewport에서 left/right rail은 collapse 가능
- center reading stage는 항상 안정적이어야 함

## 9. What to Steal from GitBook

가져올 것:

- clean shell
- strong left navigation
- calm header
- predictable right-side TOC/context
- consistent spacing rhythm
- “문서 제품”다운 안정감

## 10. What Not to Copy from GitBook

가져오지 않을 것:

- generic SaaS help-center tone
- docs-only 느낌
- studio 기능 부재
- source truth와 editing truth를 분리하지 않는 관성

## 11. Acceptance Criteria

이 shell spec이 유효하다고 보려면 아래가 가능해야 한다.

1. 사용자가 처음 봐도 `잘 정돈된 문서 제품`으로 느낀다
2. 조금 읽으면 `책처럼 읽히는 리듬`이 있다
3. 더 깊게 보면 `PBS만의 source rail / related play / studio layer`가 보인다
4. 메모와 펜 기능이 본문을 망치지 않고 옆에서 살아 있다
5. same-truth binding을 깨지 않고 viewer와 studio가 공존한다

## 12. Non-Goals

- GitBook 픽셀 복제
- full inline word processor
- canvas-first main reading surface
- source overwrite editing

## 13. Immediate Design Decision Questions

다음 구체화 회의에서 먼저 정해야 할 질문은 아래다.

1. left rail은 `library + current book tree`를 한 패널에 둘지, 분리할지?
2. right rail에서 `TOC`, `source rail`, `chat adjacency` 중 무엇이 기본으로 보여야 하는지?
3. studio sidecar는 `dock형`으로 열지, `split pane`으로 열지?
4. inserted text card는 본문 inline에 보일지, sidecar에 보일지?
5. reader mode와 studio mode 사이 전환을 얼마나 분명히 나눌지?

## 14. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`이 화면은 GitBook처럼 안정적으로 읽히지만, 동시에 PBS만의 Playbook과 Studio 정체성을 분명히 갖고 있는가`
