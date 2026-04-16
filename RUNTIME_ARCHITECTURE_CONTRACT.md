---
status: active
doc_type: architecture_contract
audience:
  - codex
  - engineer
precedence: 3
supersedes:
  - P0_ARCHITECTURE_FREEZE_ADDENDUM.md
  - PARSED_ARTIFACT_CONTRACT.md
  - PIPELINE_PLAIN_GUIDE.md
last_updated: 2026-04-16
---

# RUNTIME ARCHITECTURE CONTRACT

## Purpose

이 문서는 제품의 기술적 불변조건을 고정한다.
Codex 는 runtime, corpus, viewer, parsing 작업 시 이 문서를 기준으로 구현한다.

## Locked System Model

현재 시스템은 아래 다섯 층으로 본다.

1. `Source Intake`
   - official repo source such as AsciiDoc
   - official published HTML fallback
   - source assets such as images, figures, diagrams
   - customer/private documents
2. `Parse And Normalize`
   - parsed artifact
   - source lineage
   - block recovery
3. `Structured Runtime Core`
   - structured book
   - relation assets
   - figure asset catalog
   - runtime manifest
   - citation map
4. `Derived Products`
   - Playbook Library render assets
   - Playbook Corpus retrieval assets
   - evaluation assets
5. `Product Surfaces`
   - Playbook Library
   - Wiki Runtime Viewer
   - Chat Workspace

## Canonical Truth

제품의 진실 소스는 `단일 markdown 파일`이 아니다.

canonical truth 는 아래 묶음이다.

- `structured book`
- `relation assets`
- `figure asset catalog`
- `runtime manifest`
- `citation map`

`markdown` 과 `html` 은 generated artifact 일 수 있지만, 단독 truth owner 로 취급하지 않는다.

## Shared Source Rule

Playbook Library 와 Playbook Corpus 는 서로 다른 raw truth 를 가지면 안 된다.

정답 구조는 아래다.

`shared raw sources -> parsed artifact -> structured book/core -> library + corpus`

즉:

- 사람용 library 와 챗봇용 corpus 는 같은 parsed/structured 기준선에서 파생된다.
- 둘 중 하나가 다른 원천에서 따로 자라면 citation mismatch 가 생기므로 금지한다.

## Source Lanes

허용하는 source lane 은 아래다.

- `vendor_official_source`
- `reviewed_translation`
- `verified_operational_evidence`
- `customer_source_first_pack`

각 산출물은 최소 `source_lane`, `source_ref`, `source_fingerprint`, `updated_at` 를 잃지 않는다.

## Data Ladder

기본 상태 사다리는 아래다.

`bronze_raw -> bronze_parsed -> silver_structured -> gold_candidate -> wiki_runtime -> active_runtime -> archived`

customer/private lane 은 아래 확장 경로를 가진다.

`customer_source -> bronze_parsed -> silver_structured -> pack_candidate -> pack_runtime -> approved_pack_runtime`

## Parsed Artifact Minimum

모든 parsed artifact 는 최소 아래 필드를 가진다.

- `parsed_artifact_id`
- `source_ref`
- `source_type`
- `source_lane`
- `source_fingerprint`
- `parser_route`
- `parser_backend`
- `parser_version`
- `ocr_used`
- `extraction_confidence`
- `updated_at`

복원해야 하는 최소 블록 타입은 아래다.

- `heading`
- `paragraph`
- `code`
- `table`
- `figure`
- `xref`
- `admonition`
- `procedure_step` when applicable

## Figure And Bilingual Contract

- figure 가 있는 문서는 `figure asset + caption + anchor trace` 를 유지한다.
- OCR 은 `text recovery` 를 위한 보조 수단이지, figure preservation 의 대체물이 아니다.
- 번역이 존재할 경우 `source_text` 와 `ko_text` 를 함께 유지한다.
- 명령어, 리소스명, error string, code 는 source fidelity 를 잃지 않는다.

## Corpus Contract

Playbook Corpus 는 아래 묶음이다.

- retrieval chunks
- sparse/vector index inputs
- citation context
- retrieval metadata

모든 chunk 는 최소 아래를 가진다.

- `chunk_id`
- `doc_id`
- `section_id`
- `block_id`
- `anchor_id`
- `source_lane`
- `truth_tier`
- `version or runtime id`

chunk 는 사람이 읽는 문서에서 분리되어 저장될 수 있지만, 항상 library anchor 로 되돌아갈 수 있어야 한다.

## Corpus Quality Gate

Playbook Corpus 는 아래 gate 를 통과할 때만 `active runtime quality` 로 본다.

1. `book family retrieval`
   - retrieval regression set 에서 expected playbook family hit 를 유지한다.
2. `landing precision`
   - retrieval 결과는 expected book 뿐 아니라 expected anchor / section landing 도 함께 맞아야 한다.
3. `context coverage`
   - 최소 `ops`, `learn`, `follow-up`, `ambiguous` query set 을 회귀군에 포함한다.
4. `warning cleanliness`
   - outside-corpus, relation-aware miss, similar-document risk 를 보고서에 남긴다.
5. `shared truth discipline`
   - gate 는 library 와 다른 raw truth 가 아니라 active corpus/runtime 기준선으로만 측정한다.

즉 `book slug hit 만 맞는 평가` 는 corpus quality gate 로 충분하지 않다.
active gate 는 `retrieval family + anchor landing + context query coverage` 를 함께 본다.

## Library Contract

Playbook Library 는 사용자가 보는 최종 문서 surface 다.

- 본문은 `HTML viewer` 를 기준으로 한다.
- library 는 relation, figure, anchor jump, bilingual presentation 을 지원해야 한다.
- overlay 는 본문을 점유하지 않는 보조 레이어로 유지한다.

## One-Click Runtime Contract

one-click runtime 은 아래 순서를 한 묶음으로 수행해야 한다.

1. `source rebuild`
2. `parse / normalize`
3. `runtime materialization`
4. `relation refresh`
5. `active switch`
6. `smoke validation`

`relation refresh` 는 `active switch` 뒤로 밀리면 안 된다.
smoke validation 은 post-switch 상태를 검증해야 한다.

## Stop Conditions

아래는 architecture 위반이다.

1. library 와 corpus 가 서로 다른 raw truth 를 쓰는 경우
2. markdown 하나를 canonical truth 인 것처럼 취급하는 경우
3. relation graph 없이 viewer 만 남기는 경우
4. figure/diagram 을 text-only fallback 으로 대체하는 경우
5. citation 이 문서 루트로만 가고 정확한 anchor landing 을 잃는 경우
6. customer/private pack 이 boundary label 없이 official output 에 섞이는 경우
