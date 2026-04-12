# Parsed Artifact Contract

## Purpose And Scope

이 문서는 `bronze_parsed` 계층을 현재 `normalized document -> chunk -> manualbook` 계약 앞단에 강제로 추가하는 상위 계약이다.

목표는 하나다.

- raw PDF, scanned PDF, HTML, 고객 문서가 `page-level provenance`, `parser routing`, `security envelope` 없이 바로 silver로 뛰지 못하게 막는다.

이 문서는 buyer-facing 약속 문서가 아니다. `Q1_8_PRODUCT_CONTRACT.md` 이전에 무엇이 upstream 계약으로 존재해야 하는지 고정하는 운영 계약이다.

## Current Repo Truth

현재 저장소의 사실은 아래다.

- `schemas/document.schema.json` 은 이미 `Normalized section row` 부터 시작한다.
- `schemas/chunk.schema.json` 은 이미 retrieval-ready chunk 부터 시작한다.
- `schemas/manualbook.schema.json` 은 이미 reader-facing manualbook 부터 시작한다.
- `src/play_book_studio/ingestion/models.py` 에는 `SourceManifestEntry`, `NormalizedSection`, `ChunkRecord` 는 있지만 `parsed artifact` 모델은 없다.

즉, 현재는 `bronze_parsed` 와 `page provenance` 가 계약으로 잠겨 있지 않다.

## Position In The Data State Ladder

정식 data state ladder 는 아래다.

`bronze_raw -> bronze_parsed -> silver_structured -> candidate -> gold -> gold_restricted -> gold_degraded -> archived`

여기서 `bronze_parsed` 는 다음 의미를 가진다.

- 원본 파일이 실제로 어떻게 읽혔는지 남긴다.
- OCR 여부와 parser route 를 남긴다.
- page/block/table/figure 단위의 근거를 남긴다.
- security envelope 를 silver 이전부터 부착한다.

## Artifact Identity And Provenance

`bronze_parsed` 는 최소 아래 identity/provenance 필드를 가져야 한다.

| field | required subfields | purpose |
|---|---|---|
| `parsed_artifact_id` | `parsed_artifact_id` | bronze_parsed 단일 식별자 |
| `source_ref` | `source_id`, `source_url_or_uri`, `source_type`, `source_lane`, `source_collection`, `product`, `version`, `locale` | downstream source 계열 필드를 upstream부터 유지 |
| `raw_asset_ref` | `raw_asset_uri`, `source_fingerprint`, `raw_asset_hash` | 원본 자산과 parsed 결과를 재현 가능하게 연결 |
| `language_state` | `source_language`, `display_language`, `translation_status`, `translation_source_language`, `translation_source_url` | 번역 계보와 언어 상태 유지 |
| `quality_state` | `parse_status`, `extraction_confidence`, `review_status`, `trust_score`, `updated_at` | quality/review/update 축 유지 |
| `promotion_trace` | `promotion_run_id`, `normalized_section_ids`, `chunk_ids`, `manualbook_section_ids` | parsed 결과가 어디로 승격됐는지 추적 |

## Parser Routing And Extraction Rules

`bronze_parsed` 는 parser route 를 필수 메타로 남겨야 한다.

필수 필드:

- `parser_route`
- `parser_backend`
- `parser_version`
- `ocr_strategy`
- `ocr_used`

필수 규칙:

- parser route 가 비어 있으면 `silver_structured` 승격 금지
- OCR fallback 이 발생하면 `ocr_used = true` 와 `ocr_strategy` 기록 필수
- `다양한 포맷 지원` 같은 문구는 `parser_route`와 `ocr_strategy`가 없는 한 금지

## Page-Level Parsed Payload Contract

모든 parsed artifact 는 최소 `page_refs[]` 를 가져야 한다.

각 page payload 최소 필드:

- `page_id`
- `page_no`
- `page_asset_uri`
- `page_text`
- `ocr_text`
- `page_confidence`

규칙:

- page 단위 trace 가 없으면 `page-to-section trace` 완성 불가로 판단한다.
- text-native PDF 여도 `page_id`, `page_no`, `page_confidence` 는 남긴다.
- scan PDF 는 `ocr_text` 와 `page_confidence` 가 필수다.

## Layout Block And Table/Figure Contract

`bronze_parsed` 는 단순 page text dump 로 끝나면 안 된다.

### layout_blocks[]

각 block 최소 필드:

- `block_id`
- `page_id`
- `kind`
- `bbox`
- `reading_order`
- `text`
- `block_confidence`

### table_refs[]

각 table 최소 필드:

- `table_id`
- `page_id`
- `bbox`
- `table_payload`
- `confidence`

### figure_refs[]

각 figure 최소 필드:

- `figure_id`
- `page_id`
- `bbox`
- `asset_uri`
- `caption_text`

## Lineage To Silver, Chunk, And Manualbook

`bronze_parsed` 는 downstream lineage 를 직접 지원해야 한다.

필수 보조 필드:

- `section_trace_hints[]`
  - `block_id`
  - `candidate_section_key`
  - `anchor_hint`

필수 승격 규칙:

- `bronze_parsed -> silver_structured` 승격 시 `normalized_section_ids` 를 기록한다.
- `silver_structured -> chunk` 승격 시 `chunk_ids` 를 기록한다.
- `silver_structured -> manualbook` 승격 시 `manualbook_section_ids` 를 기록한다.
- parsed page/block 이 downstream 어디로 갔는지 역추적되지 않으면 `gold` 승격 금지다.

## Security Envelope Required At Parsed Stage

private-doc 은 parsed 단계부터 아래 보안 외피를 가져야 한다.

- `tenant_id`
- `workspace_id`
- `classification`
- `access_group`
- `redaction_state`
- `provider_egress_policy`

규칙:

- 이 필드들이 비면 parsed artifact 는 `candidate` 까지도 승격 금지다.
- private-doc 이 security envelope 없이 silver 로 올라가면 fail 이다.
- `redaction_state = raw` 이면 remote provider 전달 금지다.

## Quality Gates And Promotion Rules

`bronze_parsed` 가 통과해야 할 최소 gate 는 아래다.

- `parser_route` 가 기록되어 있다.
- `page_refs[]` 가 존재한다.
- `layout_blocks[]` 또는 동등한 구조 trace 가 존재한다.
- `extraction_confidence` 가 기록되어 있다.
- `review_status` 와 `trust_score` 가 기록되어 있다.
- `security envelope` 가 private-doc 에서 채워져 있다.
- `promotion_trace` 가 downstream 산출물과 연결된다.

## Rejection And Degradation Rules

아래 중 하나면 `gold` 승격이 아니라 `gold_degraded` 또는 reject 다.

- page trace 없음
- bbox/block trace 없음
- parser route 없음
- OCR fallback 발생했는데 `ocr_strategy` 미기록
- security envelope 누락
- table/figure 손실이 수용 기준을 넘김
- promotion trace 누락

## Stop Conditions

아래 중 하나라도 발생하면 이 계약은 실패다.

1. `bronze_parsed` 없이 silver schema 재서술로 끝나는 경우
2. `page_id`, `block_id`, `bbox`, `extraction_confidence` 중 하나라도 빠지는 경우
3. `tenant_id`, `workspace_id`, `classification`, `access_group`, `provider_egress_policy` 를 optional 취급하는 경우
4. `parser_route` 와 `ocr_strategy` 없이 포맷 지원만 선언하는 경우
5. parsed 결과에서 `normalized_section/chunk/manualbook` 로 이어지는 `promotion_trace` 가 없는 경우
6. buyer promise 나 chat answer policy 를 이 문서에 섞는 경우

## Non-Promises

이 문서는 아래를 약속하지 않는다.

- 모든 포맷 즉시 지원
- OCR 엔진 단일 선택
- day-1 GraphDB 도입
- buyer-facing 세일즈 문구

이 문서가 잠그는 것은 `parsed artifact 없이는 enterprise-private 문서 처리가 시작되지 않는다` 는 사실뿐이다.
