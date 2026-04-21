---
status: reference
doc_type: review-board
audience:
  - codex
  - engineer
  - designer
  - operator
last_updated: 2026-04-20
---

# Playbook Reference Board v1

이 문서는 PBS가 어떤 `완성본 감각`을 참고해야 하는지 검토하기 위한 reference board다.

목적은 하나다.

`어떤 서비스 하나를 그대로 따라 하지 말고, 역할별로 가져올 패턴을 분해해 선택한다.`

## 1. Review Rule

이 문서는 아래 질문에 답하기 위해 본다.

1. `책처럼 읽히는가`
2. `지식이 연결되어 자라는가`
3. `메모/펜/삽입 텍스트가 자연스러운가`
4. `챗봇이 붙어도 읽기 경험을 해치지 않는가`
5. `PBS가 직접 만들어야 할 부분은 어디인가`

핵심 원칙:

- `one product to copy`를 찾지 않는다
- `role-specific pattern`을 고른다
- `steal / avoid / adapt`로 판단한다

## 2. Primary Review Table

| Reference | Role | Strong Pattern | Weak Point | PBS Steal | PBS Avoid |
| --- | --- | --- | --- | --- | --- |
| GitBook | product docs system | 정보구조, 계층, 검색, 운영감 | 너무 docs-platform 쪽으로 보일 수 있음 | docs IA, navigation discipline, knowledge that evolves 감각 | 너무 SaaS help-center처럼 보이는 톤 |
| Jupyter Book | book-like reading | 책 흐름, 장/절, cross-reference, long-form narrative | 메모/펜/작업면은 약함 | chapter rhythm, “book” 감각, cross-reference grammar | 계산 노트북스러운 외형 그대로 차용 |
| Starlight | readable web docs shell | 가독성, 속도, 타이포, 코드/탐색 균형 | 주석/편집 작업면은 없음 | clean reading shell, typography, responsive docs rhythm | 너무 generic docs skin처럼 끝나는 것 |
| Obsidian Publish | digital garden/wiki | wiki, knowledge base, digital garden 감각 | 완성된 브랜드 북 느낌은 약할 수 있음 | note graph 감각, wiki publishing mental model | raw note/vault 느낌 그대로 노출 |
| Quartz 4 | knowledge linking | backlinks, wikilinks, graph, popover preview, digital garden | 완성된 editorial book보다는 garden 쪽 성격 강함 | connected knowledge, related play traversal, lightweight wiki linking | graph-first로 가서 책 정체성이 약해지는 것 |
| Readwise Reader | reading + annotation workflow | 하이라이트/노트가 reading 중심으로 붙는 감각, multi-device reading | 실제 PDF/텍스트 뷰 이원화 한계, 본문 자체 커스터마이즈 약함 | notebook-style annotation adjacency, reading-side notes, power-reader workflow | PDF text/original view 분리 같은 UX 단절 |
| LiquidText | heavy annotation workspace | 펜, 연결선, 다중 영역 주석, 병렬 작업면, 문서 간 연결 | 출판된 브랜드 북보다는 분석 워크벤치 느낌 | pen/ink, text insertion, side workspace, cross-document linking | 책보다 canvas/workspace가 앞에 나오는 인상 |
| Obsidian Canvas | visual work surface | 텍스트 카드, PDF/웹 임베드, 연결선, 2D arrangement | 읽는 책의 정적 완성도와는 다른 종류의 surface | editable side-surface, card insertion, visual note graph | main reading surface를 canvas처럼 만드는 것 |
| Obsidian Web Clipper | source capture | durable file, structured clipping, template-based capture | 최종 reader-grade/playbook-grade는 별도 계층이 필요 | template-based source capture, file-over-app 철학 | clipping 결과를 완성본처럼 취급하는 것 |

## 3. Category Decision Table

| Category | Best Reference | Why | PBS Decision |
| --- | --- | --- | --- |
| Book grammar | Jupyter Book | 장/절 흐름, cross-reference, “book” 감각이 강함 | chapter opener와 section rhythm 참고 |
| Docs shell | Starlight, GitBook | 웹 문서의 가독성과 운영성이 좋음 | reader shell과 IA 참고 |
| Wiki growth | Quartz, Obsidian Publish | knowledge linking, digital garden, note graph 감각이 강함 | related play / backlinks / knowledge growth 참고 |
| Annotation workflow | Readwise Reader | 읽기 흐름 안에서 하이라이트/노트가 잘 붙음 | notebook-adjacent note UX 참고 |
| Ink and workspace | LiquidText, Canvas | 펜, 연결, 병렬 작업면, 삽입 카드가 강함 | studio-side editing surface 참고 |
| Capture pipeline | Obsidian Web Clipper | template capture, file ownership 철학이 선명함 | source capture contract 참고 |

## 4. PBS Synthesis Direction

PBS는 아래 셋을 합쳐야 한다.

### 4.1 Book Layer

목표:

- `읽고 싶은 책`

가져올 것:

- Jupyter Book의 chapter rhythm
- Starlight의 readable shell
- GitBook의 information architecture

### 4.2 Knowledge Layer

목표:

- `지식이 연결되어 자라는 위키`

가져올 것:

- Quartz의 backlinks / wikilinks / preview
- Obsidian Publish의 digital garden mental model

### 4.3 Studio Layer

목표:

- `메모, 펜, 텍스트 삽입, 작업면`

가져올 것:

- LiquidText의 parallel workspace
- Canvas의 text card / connection / placement
- Readwise Reader의 reading-side annotation adjacency

## 5. Preliminary Product Judgment

현재 판단은 아래다.

### PBS가 통째로 닮아야 할 단일 서비스는 없다

이유:

- docs 서비스는 책과 펜 입력이 약하다
- annotation 앱은 브랜드 Playbook 출판성이 약하다
- wiki/garden 툴은 editorial finish가 약할 수 있다

### PBS가 직접 만들어야 하는 것

아래는 결국 PBS가 직접 가져야 할 고유 계층이다.

- `Playbook Composer`
- `Brand Renderer`
- `Same-Truth Binding`
- `Studio Annotation Surface`

즉 레퍼런스는 참고 대상이고,
최종 완성본은 PBS 고유 조합이어야 한다.

## 6. Anti-Reference Table

| Avoid Pattern | Why PBS Should Avoid It |
| --- | --- |
| generic markdown export feel | Playbook이 아니라 dump처럼 보임 |
| raw vault/note feel | 브랜드 북이 아니라 개인 메모 저장소처럼 보임 |
| graph-first overreading | 지식 연결은 강하지만 책 정체성이 약해질 수 있음 |
| docs-only shell | 운영 문서 같아 보일 수 있으나 “읽고 싶은 책” 감각이 약함 |
| annotation-only workspace | 분석툴처럼 보이고 출판물 감각이 약함 |

## 7. Review Questions for Meeting

다음 회의에서는 아래 질문을 기준으로 검토한다.

1. PBS의 기본 독서 경험은 `GitBook/Starlight형`에 더 가까워야 하나, `Jupyter Book형`에 더 가까워야 하나?
2. `메모/펜/삽입 텍스트`는 본문 안에 녹일지, LiquidText처럼 병렬 작업면으로 둘지?
3. `related play / backlinks / graph`는 얼마나 드러낼지?
4. PBS main surface는 `책`이 먼저인지, `스튜디오 작업면`이 먼저인지?
5. user lane 결과를 언제부터 polished playbook처럼 보여줄지?

## 8. Immediate Recommendation

지금 당장 디자인/제품 방향으로는 아래 조합을 추천한다.

- `Main reading shell`: Starlight + GitBook
- `Book rhythm`: Jupyter Book
- `Knowledge linking`: Quartz + Obsidian Publish
- `Annotation/studio`: LiquidText + Canvas + Reader

즉 PBS의 한 줄 방향은 아래다.

`Starlight/GitBook처럼 읽히고, Jupyter Book처럼 책답고, Quartz/Obsidian처럼 지식이 연결되며, LiquidText처럼 메모와 펜이 살아 있는 Playbook system`

## 9. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`우리는 지금 무엇을 참고하는지뿐 아니라, 무엇을 참고하지 않을지도 분명히 알고 있는가`
