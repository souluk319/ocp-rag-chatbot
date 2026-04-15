# Parsed Artifact Contract

## Purpose

이 문서는 source-first technical wiki 의 upstream 실행 계약을 고정한다.

핵심은 하나다.

`official source 와 customer source 는 모두 parsed artifact 를 남긴 뒤에만 runtime 사다리로 들어간다.`

## Supported Source Lanes

현재 인정하는 source lane 은 아래다.

- `vendor_official_source`
- `reviewed_translation`
- `customer_source_first_pack`

lane 이름은 lineage 와 security envelope 에 그대로 남아야 한다.

## Required Data Ladder

정식 상태는 아래다.

`bronze_raw -> bronze_parsed -> silver_structured -> gold_candidate -> wiki_runtime -> active_runtime -> archived`

customer pack 은 아래 확장 사다리, 즉 `pack runtime` 경로를 함께 쓴다.

`customer source -> bronze_parsed -> silver_structured -> pack_candidate -> pack_runtime -> approved_pack_runtime`

## Required Parsed Fields

모든 parsed artifact 는 최소 아래를 가져야 한다.

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

customer lane 은 아래를 추가로 가져야 한다.

- `tenant_id`
- `workspace_id`
- `pack_id`
- `pack_version`
- `approval_state`
- `publication_state`

## Block-Level Contract

parsed artifact 는 최소 아래 블록을 복원해야 한다.

- paragraph
- heading
- code
- table
- figure
- xref

figure 가 있는 문서는 최소 아래를 남긴다.

- `figure_id`
- `asset_uri`
- `caption_text`
- `source_ref`
- `anchor_hint`

## Lineage Contract

parsed artifact 는 downstream 으로 이어져야 한다.

- `parsed -> structured book`
- `structured book -> wiki_runtime or pack_runtime`
- `wiki_runtime -> active_runtime`

pack lane 은 `target_ref` 와 `pack identity` 를 잃지 않는다.

## Promotion Gate

parsed artifact 는 아래 조건을 만족하면 다음 단계로 이동할 수 있다.

- parser route 존재
- source fingerprint 존재
- figure 있는 문서의 figure trace 존재
- anchor 또는 section trace 존재
- customer lane 인 경우 security envelope 존재

## Non-Goal

이 문서는 buyer promise 문서가 아니다.

이 문서는 `source-first runtime 은 parsed artifact 와 lane identity 없이는 성립하지 않는다`는 사실을 고정한다.
