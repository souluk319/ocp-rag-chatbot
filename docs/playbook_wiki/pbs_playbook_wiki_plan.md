---
status: reference
doc_type: strategy
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# PBS Playbook Wiki Plan

이 문서는 `PlayBookStudio`가 `LLM Wiki`의 지식 누적 원리를 흡수하되, 최종 산출물을 `PBS 브랜드 Playbook`으로 고정하기 위한 전략 계획서다.

이 문서는 active contract를 대체하지 않는다.
판단 기준은 여전히 아래 다섯 개 active 문서가 우선한다.

- `AGENTS.md`
- `PROJECT.md`
- `RUNTIME_ARCHITECTURE_CONTRACT.md`
- `EXECUTION_HARNESS_CONTRACT.md`
- `SECURITY_BOUNDARY_CONTRACT.md`

## 1. 왜 이 문서가 필요한가

현재 PBS는 이미 다음을 어느 정도 갖고 있다.

- source ingest
- normalize
- wiki runtime viewer
- retrieval corpus
- chat workspace

하지만 이것만으로는 `Playbook`이 완성되지 않는다.

문서를 파싱하고, 위키처럼 보이게 만들고, chunk를 생성하는 것만으로는
`읽고 싶고`, `보기 좋고`, `브랜드 아이덴티티가 있으며`, `챗봇과 같은 truth를 공유하는 책`
이 저절로 생기지 않는다.

지금 필요한 전환은 아래다.

- `parser-first` -> `book-first`
- `one-shot RAG` -> `compounding knowledge`
- `wiki runtime` -> `brand playbook system`

## 2. 외부 원형에서 가져올 핵심

참고 원형:

- Andrej Karpathy, `LLM Wiki`, created `2026-04-04`
- gist: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

이 원형에서 PBS가 가져와야 할 핵심은 세 가지다.

1. `raw sources`는 불변의 진실 소스여야 한다.
2. 새 source가 들어올 때 지식층이 계속 갱신되어야 한다.
3. 질의응답과 탐색 결과도 사라지지 않고 지식층을 강화할 수 있어야 한다.

하지만 PBS는 여기서 멈추면 안 된다.

Karpathy의 원형은 `persistent wiki`가 목적지에 가깝다.
PBS는 `persistent wiki`를 중간층으로 사용하고,
최종 목적지는 `brand-grade Playbook`이어야 한다.

## 3. PBS의 최종 목표

PBS의 최종 목표는 아래 한 문장으로 고정한다.

`공식 기술 문서와 운영 자료를 누적 지식으로 컴파일해, 사람이 읽고 싶어지는 브랜드 Playbook과 챗봇이 신뢰하는 Corpus를 같은 진실 소스에서 생산한다.`

즉 PBS는 아래 제품이어야 한다.

- `문서 뷰어`가 아님
- `markdown 변환기`가 아님
- `일회성 RAG 툴`이 아님
- `지식 누적형 Playbook 출판 시스템`이어야 함

## 4. PBS에 접목할 핵심 원리

### 4.1 Source는 불변

원문 source는 수정하지 않는다.

- official source
- customer/private document
- uploaded assets
- derived evidence

원문은 truth의 바닥층이다.
repair, translation, synthesis, playbook composition은 모두 이 위에서 일어난다.

### 4.2 지식은 누적되어야 한다

새 source를 넣을 때마다 새 책 하나를 만드는 방식은 불충분하다.

대신 아래가 일어나야 한다.

- 기존 entity page가 보강됨
- 기존 concept summary가 갱신됨
- 기존 procedure가 수정/보강됨
- contradiction 또는 supersession이 표시됨
- 기존 playbook chapter가 함께 업데이트됨

즉 `document addition`이 아니라 `knowledge accumulation`이 핵심이다.

### 4.3 책과 챗봇은 같은 truth를 써야 한다

지금 PBS는 viewer와 chat이 서로 가까워졌지만,
궁극적으로는 둘이 완전히 같은 truth에서 파생되어야 한다.

원칙:

- `reader-grade output`는 Playbook renderer가 생산
- `chat-grade output`는 corpus/chunker가 생산
- 둘 다 같은 canonical knowledge layer를 사용

### 4.4 markdown은 최종 진실 소스가 아니다

markdown은 아래 중 하나일 수 있다.

- generated artifact
- export format
- review format
- debug format

하지만 canonical truth는 markdown이 아니라
`knowledge object + source lineage + book composition contract`여야 한다.

## 5. 목표 아키텍처

PBS의 목표 흐름은 아래로 고정한다.

`Source -> Canonical Knowledge Layer -> Playbook Composer -> Viewer/Corpus/Chat`

### 5.1 Source Layer

입력:

- official repo / asciidoc / published html
- uploaded pdf/docx/pptx/xlsx/html
- operator notes
- derived answer artifacts

역할:

- source storage
- metadata capture
- provenance lock
- security boundary enforcement

### 5.2 Canonical Knowledge Layer

이 계층이 PBS의 핵심이다.

여기에 저장되는 것은 페이지가 아니라 `knowledge object`다.

예시 object:

- `entity`
- `concept`
- `procedure`
- `command`
- `claim`
- `evidence`
- `warning`
- `table`
- `figure`
- `source_lineage`
- `contradiction`
- `supersession`

이 계층의 역할:

- source에서 semantic object 추출
- 기존 object와 merge
- freshness/priority 판단
- contradiction 관리
- source lineage 유지

### 5.3 Playbook Composer

이 계층은 누적 지식을 책으로 조립한다.

역할:

- chapter composition
- section rhythm
- procedure/editorial layout
- code/table/figure placement
- related play surface
- source rail
- glossary/entity box
- operator summary/checklist

여기서 중요한 점:

`좋은 파싱 결과`가 자동으로 `좋은 책`이 되는 게 아니라,
composer가 `좋은 책`을 책임진다.

### 5.4 Corpus/Chat Layer

같은 canonical knowledge에서 아래를 생산한다.

- retrieval chunks
- sparse/vector index
- citation context
- related links
- grounded answer support

Chat은 raw source를 바로 뒤지는 것이 아니라
canonical knowledge와 source lineage를 함께 활용해야 한다.

## 6. Playbook의 브랜드 정의

PBS 책은 최소한 아래 감각을 가져야 한다.

- `읽고 싶다`
- `한눈에 위계가 보인다`
- `코드/표/절차가 무너지지 않는다`
- `출처와 최신성이 눈에 보인다`
- `다음에 무엇을 해야 할지 안내한다`
- `이건 PBS 책이다`라는 반복 문법이 있다

이를 위해 Playbook Spec v1에서 아래를 먼저 고정한다.

- chapter opener
- section header hierarchy
- procedure block
- command/code plate
- table plate
- warning/caution/note
- figure/caption
- source lineage rail
- citation grammar
- operator checklist
- entity/glossary card

## 7. 품질 게이트

Playbook 승격은 단일 점수로 결정하지 않는다.

최소 네 축으로 본다.

### 7.1 parse-grade

문서 구조를 얼마나 정확히 추출했는가

- heading fidelity
- block typing
- code/table/figure recovery
- anchor stability

### 7.2 reader-grade

사람이 읽기 좋은가

- section 흐름
- visual hierarchy
- structured content fidelity
- chapter coherence

### 7.3 brand-grade

PBS 책처럼 보이는가

- consistent composition
- source rail presence
- operator summary quality
- repeated book grammar

### 7.4 chat-grade

챗봇이 이 책/지식을 안전하게 사용할 수 있는가

- chunk landing quality
- provenance traceability
- contradiction handling
- citation answerability

이 네 개 중 하나라도 미달이면 `Playbook` 승격을 막는다.

## 8. Official Lane과 User Lane의 분리

### 8.1 Official Source-First Lane

이 lane은 PBS의 gold standard다.

목표:

- repo/asciidoc first
- translation completion
- structured extraction fidelity
- brand-grade playbook
- chat-grade corpus

### 8.2 User Upload Lane

이 lane은 처음부터 `자동 완성책`으로 취급하지 않는다.

기본 계약:

- ingest
- normalize
- repair
- editable draft
- human-guided refinement
- promotion gate

즉 user lane 산출물은 우선 `workspace draft`이며,
기준을 통과한 것만 `Playbook` 승격한다.

## 9. Repair Lane 원칙

품질이 안 좋은 문서를 버리는 게 아니라 수리한다.

하지만 수리는 무작정 OCR 한 번 더 태우는 것이 아니다.
format-aware repair가 필요하다.

### 9.1 PDF/Image

- flattened structured block 검출
- layout-aware repair
- trusted OCR fallback
- repair 전/후 비교

### 9.2 DOCX/PPTX/XLSX

- OCR보다 structure recovery 우선
- heading/bullet/table/shape text recovery 강화

### 9.3 Promotion before Corpus

수리되지 않은 품질 낮은 결과가
viewer나 corpus에 그대로 퍼지지 않게 한다.

## 10. Query 결과의 누적

질의응답은 사라지는 output이 아니라,
검증되면 knowledge layer를 강화하는 입력이 될 수 있다.

예:

- operator checklist
- comparison note
- migration note
- troubleshooting pattern
- related play draft

이 원리는 Karpathy식 `query can become wiki`를
PBS식 `derived play / operator note`로 바꾸는 것이다.

## 11. Lint와 Health Check

지식 누적형 제품은 주기적 건강검진이 필요하다.

PBS lint가 확인해야 할 것:

- orphan section
- orphan play
- contradiction
- stale claim
- weak citation landing
- broken source lineage
- flattened structured block
- empty or shallow chapter
- brand grammar break

이 lint는 백엔드 내부 진단이 아니라
궁극적으로는 제품 표면에도 드러날 수 있어야 한다.

## 12. Ordered Execution Packets

아래 순서로 진행한다.

1. `Playbook Spec v1`
2. `Knowledge Object Schema v1`
3. `Merge Rule + Promotion Gate Matrix`
4. `Playbook Composer Foundation`
5. `Official Source-First Renewal`
6. `User Upload Repair Lane`
7. `Same-Truth Corpus/Chat Renewal`
8. `Runtime Performance Hardening`
9. `Validation + Release Packet`

## 13. 완료 조건

이 계획이 성공했다고 말하려면 아래가 동시에 충족되어야 한다.

1. official lane 대표 책이 `reader-grade + brand-grade + chat-grade`를 통과한다.
2. user lane 문서는 `repair -> refinement -> promotion` 흐름을 가진다.
3. viewer와 chat이 같은 truth를 사용한다.
4. Playbook이 visually and structurally PBS identity를 가진다.
5. runtime이 실사용 가능한 속도와 안정성을 갖는다.

## 14. 하지 않을 것

이 계획에서 하지 않을 것을 명확히 잠근다.

- markdown을 최종 진실 소스로 격상하지 않는다
- user lane을 자동 완성책으로 과장하지 않는다
- 성능 때문에 provenance나 source lineage를 훼손하지 않는다
- security boundary를 무시한 remote egress를 자동 허용하지 않는다
- one-off demo용 임시 구조를 제품 구조로 포장하지 않는다

## 15. 한 줄 결론

PBS는 `문서를 보여주는 RAG 앱`이 아니라,
`지식을 누적해 브랜드 Playbook을 출판하는 시스템`으로 진화해야 한다.
