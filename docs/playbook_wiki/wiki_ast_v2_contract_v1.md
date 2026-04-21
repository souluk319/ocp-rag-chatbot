---
status: reference
doc_type: contract
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-21
---

# Wiki AST v2 Contract v1

이 문서는 PBS의 다음 공통 truth 구조를 `Wiki AST v2`로 잠근다.

핵심 질문은 하나다.

`parser, viewer, corpus, citation, repair, dashboard가 모두 같은 문서 truth를 보려면 어떤 구조가 최소한 필요 한가`

## 1. 왜 v2가 필요한가

현재 `src/play_book_studio/canonical/models.py`의 AST v1은 좋은 출발점이다.

이미 가지고 있는 장점:

- section 중심 구조
- provenance 기본 필드
- block 기반 viewer/corpus 파생 가능성
- playbook artifact와 연결되는 최소 모델

하지만 새 goal-first 기준에서는 아래가 부족하다.

- page_id / slide_id
- bbox / reading order / layout trace
- figure-caption 연결
- block-level source trace
- parser/OCR confidence
- validation issue attachment
- repair planner 대상 지정
- corpus/render derivation hints

즉 v1은 `문서를 표현하기 위한 AST` 였고,
v2는 `문서를 해석하고 승급시키기 위한 AST` 가 되어야 한다.

## 2. One-Line Contract

`Wiki AST v2는 source fidelity를 잃지 않으면서, viewer render, corpus derivation, citation landing, repair planning, grade judgement를 모두 같은 구조 위에서 수행하게 하는 canonical document graph다.`

## 3. Relation to Other Truth Layers

### 3.1 Source Layer

source는 immutable input이다.

Wiki AST v2는 source를 대체하지 않는다.
source에서 파생된 canonical structural truth다.

### 3.2 Knowledge Object Layer

knowledge object graph는 AST 위에 올라간다.

순서:

1. source ingest
2. wiki ast v2 normalization
3. object extraction / merge / contradiction handling

즉 object graph는 상위 semantic layer이고, AST는 그 바닥층이다.

### 3.3 Viewer / Corpus / Repair

이 세 개는 AST를 직접 또는 간접적으로 사용해야 한다.

- viewer: section/block/page/figure trace
- corpus: chunk derivation + citation anchor
- repair: issue target + rerun comparison

## 4. Top-Level Model

Wiki AST v2 문서 한 건은 아래 7개 묶음으로 본다.

1. `document`
2. `pages`
3. `sections`
4. `blocks`
5. `relations`
6. `validation`
7. `derivations`

## 5. Required Top-Level Fields

### 5.1 document

문서 정체성과 provenance를 담는다.

필수:

- `ast_version`
- `document_id`
- `book_slug`
- `title`
- `source_type`
- `source_uri`
- `source_lane`
- `source_fingerprint`
- `parsed_artifact_id`
- `parser_route`
- `parser_backend`
- `parser_version`
- `translation_status`
- `review_status`
- `tenant_id`
- `workspace_id`
- `pack_id`

### 5.2 pages

원본 문서의 page/slide/sheet surface를 담는다.

필수:

- `page_id`
- `page_kind`
- `ordinal`
- `width`
- `height`

선택:

- `image_path`
- `thumbnail_path`
- `speaker_notes`
- `ocr_confidence`

## 6. Sections

section은 사람이 읽는 구조와 chat landing 구조를 동시에 담당한다.

필수:

- `section_id`
- `heading`
- `level`
- `ordinal`
- `path`
- `anchor`
- `page_span`
- `semantic_role`

원칙:

- section은 최소 한 개 이상의 block을 가진다
- section은 page span 또는 source span이 추적 가능해야 한다

## 7. Blocks

block은 viewer/corpus/citation의 최소 truth 단위다.

필수:

- `block_id`
- `block_type`
- `section_id`
- `page_id`
- `order`
- `reading_order`
- `source_trace`

선택:

- `bbox`
- `text`
- `items`
- `code`
- `language`
- `headers`
- `rows`
- `caption`
- `figure_asset_id`
- `parser_confidence`
- `ocr_confidence`
- `render_hints`
- `corpus_hints`

## 8. Block Types

v2 최소 허용 block type은 아래다.

- `heading`
- `paragraph`
- `list`
- `procedure_step`
- `code`
- `table`
- `figure`
- `callout`
- `quote`
- `xref`
- `anchor`

PPT/diagram 계열을 위해 아래도 허용한다.

- `slide_summary`
- `speaker_note`
- `diagram_summary`

## 9. Relations

relation은 block/section/page/object 사이 연결을 표현한다.

최소 relation type:

- `caption_of`
- `child_of`
- `next_of`
- `refers_to`
- `duplicate_of`
- `prerequisite_of`
- `derived_from`
- `visual_source_of`

예시:

- figure block -> caption block
- procedure step 2 -> prerequisite callout
- answer-ready chunk group -> source block set

## 10. Source Trace

모든 section/block은 source trace를 잃으면 안 된다.

최소 source trace 필드:

- `source_id`
- `source_kind`
- `page_number`
- `source_locator`
- `excerpt`
- `confidence`

PPT/PDF/Image 계열에서는 아래를 추가로 허용한다.

- `bbox`
- `z_index`
- `rendered_image_path`

## 11. Validation

validation은 AST 바깥 리포트가 아니라 AST 안의 연결 구조여야 한다.

최소 issue 필드:

- `issue_id`
- `issue_type`
- `severity`
- `target_kind`
- `target_id`
- `message`
- `status`

대표 issue type:

- `structured_blocks_flattened`
- `heading_collapse`
- `figure_orphaned`
- `table_structure_broken`
- `anchor_unstable`
- `citation_risk`
- `ocr_low_confidence`
- `boundary_metadata_missing`

## 12. Derivations

AST는 파생 힌트를 갖되, 파생 결과 자체를 truth로 삼지 않는다.

### 12.1 render_hints

예:

- `chapter_opener`
- `checklist`
- `architecture_figure`
- `two_column`
- `table_appendix`

### 12.2 corpus_hints

예:

- `chunk_group`
- `parent_section`
- `citation_anchor`
- `keyword_boost`
- `entity_key`

## 13. Lane Rules

### 13.1 Official Lane

- source trace와 review 상태를 강하게 요구
- reader/chat-grade 고품질 승급의 기준선

### 13.2 User Upload / Customer Lane

- boundary metadata와 repair issue attachment를 더 강하게 요구
- draft truth와 promoted truth 구분 필수

## 14. Binding Rules

Wiki AST v2는 아래 규칙을 만족해야 한다.

1. viewer는 html export가 아니라 AST에서 렌더한다
2. corpus는 rendered html를 다시 뜯지 않고 AST에서 파생한다
3. repair planner는 validation issue와 target_id로 rerun 대상을 잡는다
4. citation은 answer claim -> block_id -> source trace 순으로 돌아간다
5. object extraction은 AST를 바닥층으로 삼는다

## 15. Migration from Current AST v1

유지:

- provenance 골격
- section 중심 구조
- playbook artifact 연결 가능성

확장:

- page model
- generic block trace
- relation set
- validation set
- derivation hint set

대체:

- `viewer_path` 하나에 과도하게 묶인 추적 방식
- block type 부족 문제
- page/layout 정보를 잃는 단순 section-only 구조

## 16. Acceptance Criteria

이 contract가 충분하다고 보려면 아래가 가능해야 한다.

1. html/pdf/pptx가 같은 top-level 구조로 normalize될 수 있다
2. viewer와 corpus가 AST를 직접 참조해 같은 truth를 공유한다
3. repair planner가 issue target 단위로 rerun 대상을 잡을 수 있다
4. figure/table/procedure/citation이 모두 block-level trace를 가진다
5. knowledge object layer가 AST 위에서 안정적으로 파생될 수 있다

## 17. Non-Goals

- DB table 설계 문서가 아니다
- renderer component 문서가 아니다
- parser vendor 선택 문서가 아니다

## 18. Machine-Readable Pair

이 contract의 machine-readable pair는 아래 파일이다.

- `schemas/wiki_ast_v2.schema.json`

## 19. Ref Stamp

- `branch`: `feat/pbs-v3`
- `head_sha`: `f71719898cd6e8e85fa192a0c0008ecd6d241632`
