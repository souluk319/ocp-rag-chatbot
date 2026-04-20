---
status: reference
doc_type: runtime-plan
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# Runtime Truth Binding Plan v1

이 문서는 PBS의 `canonical knowledge layer`가 실제 런타임 표면에 어떻게 연결되어야 하는지 정의한다.

핵심 질문은 하나다.

`같은 truth가 viewer, corpus, chat, runtime manifest에 어떻게 동시에 공급되는가`

## 1. 목적

PBS는 아래 둘 중 하나여서는 안 된다.

- viewer와 chat이 비슷한 내용을 우연히 공유하는 시스템
- 문서와 코퍼스가 각자 다른 중간 산출물에서 파생되는 시스템

PBS는 아래여야 한다.

`하나의 canonical truth에서 viewer-grade book과 chat-grade corpus가 동시에 파생되는 시스템`

## 2. 기본 원칙

### 2.1 One Truth, Many Surfaces

truth는 하나고 surface는 여러 개다.

surface 예시:

- Playbook Library
- Wiki Runtime Viewer
- Chat Workspace
- citation jump
- runtime manifest
- relations/figures/assets

### 2.2 Rendering is not Authoring

viewer HTML은 최종 표현일 뿐 truth가 아니다.

즉 아래는 truth가 아니다.

- raw html snapshot
- markdown export
- final rendered html
- ad-hoc chat payload

truth는 canonical knowledge layer와 source lineage다.

### 2.3 Retrieval is a Derivative

corpus chunk는 지식의 원본이 아니라 파생물이다.

즉 retrieval이 빨라지거나 chunk 전략이 바뀌어도
truth 자체는 흔들리면 안 된다.

### 2.4 Citation is a Binding Contract

citation은 UI 기능이 아니라 binding 증거다.

좋은 citation은 아래를 보장해야 한다.

- answer claim -> knowledge object
- knowledge object -> source lineage
- source lineage -> viewer landing

## 3. Binding Layers

PBS의 runtime truth binding은 아래 5계층으로 본다.

1. `source layer`
2. `canonical knowledge layer`
3. `playbook composition layer`
4. `retrieval/corpus derivation layer`
5. `runtime delivery layer`

## 3.1 Source Layer

역할:

- immutable raw source storage
- source metadata
- lane identity
- boundary metadata

필수 속성:

- source_id
- source_kind
- source_title
- source_uri or local path
- official/private lane
- freshness metadata
- security boundary metadata

## 3.2 Canonical Knowledge Layer

역할:

- semantic object storage
- merge/update
- contradiction/supersession handling
- evidence linking

이 계층은 아래의 유일한 논리적 진실 소스다.

- viewer page assembly
- chunk generation
- answer grounding

## 3.3 Playbook Composition Layer

역할:

- knowledge object selection
- chapter/page assembly
- source rail generation
- related play linkage

산출물:

- playbook chapter tree
- page block tree
- local citation map

## 3.4 Retrieval/Corpus Derivation Layer

역할:

- chunk derivation
- sparse/vector indexing
- answer context building
- citation-ready retrieval payload

중요:

- corpus는 canonical knowledge layer의 파생물이다
- chunk는 page HTML을 다시 뜯어 만드는 게 아니라,
  knowledge object와 lineage를 기반으로 파생되어야 한다

## 3.5 Runtime Delivery Layer

역할:

- viewer payload delivery
- chat answer payload delivery
- citation jump routing
- manifest exposure

실제 표면:

- library surface
- viewer document API
- chat API
- citation landing route
- related links payload

## 4. Viewer Binding

## 4.1 Viewer Input

viewer는 아래를 입력으로 받는다.

- playbook chapter tree
- page block tree
- section lineage map
- figure/table references
- related play references

viewer는 raw normalized text를 직접 진실처럼 쓰지 않는다.

## 4.2 Viewer Output

viewer 출력은 아래를 포함해야 한다.

- readable chapter/page structure
- local section anchors
- visible source rail
- citation landing affordance
- related play navigation

## 4.3 Viewer Truth Rules

- viewer text는 knowledge object 기반이어야 한다
- viewer section은 source lineage를 추적할 수 있어야 한다
- source가 바뀌면 impacted page만 재조립 가능해야 한다

## 5. Corpus Binding

## 5.1 Corpus Input

corpus는 아래 object를 우선적으로 사용한다.

- claim
- procedure
- command
- warning
- evidence-backed summary

## 5.2 Chunk Contract

각 chunk는 최소한 아래를 가져야 한다.

- chunk_id
- parent_object_id
- source_refs[]
- viewer_path
- section_anchor
- chunk_text
- chunk_type

## 5.3 Corpus Truth Rules

- chunk는 source excerpt 없이 고립되지 않는다
- chunk는 어떤 page와 어떤 object에서 왔는지 추적 가능해야 한다
- chunk refresh는 source change 또는 object change에 반응해야 한다

## 6. Chat Binding

## 6.1 Chat Input

chat answerer는 아래를 사용해야 한다.

- query
- session memory
- retrieved knowledge objects/chunks
- source lineage
- contradiction/supersession signals

## 6.2 Chat Output

chat output은 아래를 포함해야 한다.

- grounded answer
- citations
- related plays
- next action guidance if relevant

## 6.3 Chat Truth Rules

- answer는 viewer와 다른 truth를 만들면 안 된다
- unsupported synthesis는 lineage 없이 나오면 안 된다
- viewer에 있는 핵심 claim은 chat에서도 trace 가능해야 한다

## 7. Citation Binding

citation은 세 단계를 잇는다.

1. `answer or page claim`
2. `knowledge object`
3. `source landing`

좋은 citation binding의 조건:

- jump가 실제 section 근처로 간다
- source preview가 일치한다
- claim과 source가 semantic mismatch를 일으키지 않는다
- official/private boundary가 유지된다

## 8. Runtime Manifest Binding

manifest는 단순 파일 목록이 아니라 runtime binding의 공개 요약이다.

manifest가 최소한 표현해야 하는 것:

- playbook identity
- chapter inventory
- source inventory
- figure/table assets
- lineage availability
- corpus availability
- related play links

즉 manifest는 `이 책이 어떤 truth에서 파생되었는가`를 런타임 차원에서 보여줘야 한다.

## 9. Update Flow

새 source가 들어왔을 때 이상적인 흐름:

1. source ingest
2. canonical knowledge update
3. impacted object detection
4. affected playbook recomposition
5. affected chunk refresh
6. citation map refresh
7. runtime manifest refresh

즉 source 추가는 `새 파일 하나 더`가 아니라,
`기존 truth graph와 surfaces가 부분적으로 갱신되는 이벤트`여야 한다.

## 10. Lane-Specific Binding

## 10.1 Official Lane

원칙:

- stable source identity
- stronger freshness/supersession handling
- promoted corpus/viewer coupling 강함

## 10.2 User Upload Lane

원칙:

- draft truth와 promoted truth를 구분
- repair confidence가 충분하지 않으면 viewer-only draft 가능
- boundary metadata를 더 강하게 유지

즉 user lane는 같은 binding 구조를 쓰되, promotion 전에는 더 보수적으로 surface해야 한다.

## 11. Failure Modes to Avoid

아래는 막아야 할 대표 실패다.

### 11.1 Viewer/Chat Drift

viewer에는 있는데 chat은 모르는 경우, 또는 그 반대.

### 11.2 HTML-As-Truth

rendered HTML을 다시 읽어 corpus를 만들면서 truth drift가 생기는 경우.

### 11.3 Weak Citation Landing

citation이 source는 가리키지만 실제 의미 단위와 멀리 떨어지는 경우.

### 11.4 Lineage Loss

synthesis는 남았지만 원문 근거를 잃는 경우.

### 11.5 Draft Contamination

repair 전 draft가 promoted corpus나 official-like surface로 섞이는 경우.

## 12. Acceptance Criteria

이 binding plan이 성공했다고 보려면 아래가 가능해야 한다.

1. 같은 knowledge object가 viewer와 chat에서 모두 trace된다
2. source 하나가 바뀌면 affected playbook/page/chunk만 부분 갱신 가능하다
3. citation jump가 knowledge object 기반으로 landing한다
4. user lane draft truth와 promoted truth를 구분할 수 있다
5. manifest가 runtime truth binding 상태를 반영한다

## 13. Non-Goals

- 이 문서는 API 스펙 문서가 아니다
- 이 문서는 DB migration 문서가 아니다
- 이 문서는 UI 컴포넌트 명세만 적는 문서가 아니다

## 14. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`viewer, corpus, chat, citation이 서로 비슷한 내용을 우연히 공유하는 것이 아니라, 같은 truth에서 체계적으로 파생되었는가`
