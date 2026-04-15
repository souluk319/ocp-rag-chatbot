# P0 Architecture Freeze Addendum

## Purpose

이 문서는 현재 제품 아키텍처를 `source-first figure-aware technical wiki runtime` 기준으로 다시 고정한다.

이 문서가 우선하는 범위는 아래다.

- architecture
- product surface
- runtime data states
- figure / relation / overlay runtime shape

## Architecture Truth

현재 제품은 아래 5층으로 본다.

1. `Source Intake`
   - official repo
   - html-single fallback
   - customer documents
2. `Parse And Normalize`
   - parsed artifact
   - structured book blocks
3. `Wiki Runtime Materialization`
   - runtime books
   - figure assets
   - relation graph
4. `Product Surfaces`
   - Playbook Library / Control Tower
   - Wiki Viewer
   - Chat Workspace
5. `User Overlay`
   - favorites
   - checks
   - notes
   - recent position

customer documents 는 같은 Source Intake 층에 오더라도 `customer_source_first_pack` lane 으로만 들어온다.

## Product Surface Freeze

제품 표면은 아래 3면으로 고정한다.

- `Control Tower`
  - corpus, runtime, signal, backlog 상태 확인
- `Wiki Runtime Viewer`
  - 본문 읽기와 위키 탐색
- `Chat Workspace`
  - grounded answer 와 next play

viewer 본문은 `읽는 면`이고, overlay 는 본문을 점유하지 않는 보조 레이어로 다룬다.

## Data State Freeze

정식 상태 사다리는 아래다.

`bronze_raw -> bronze_parsed -> silver_structured -> gold_candidate -> wiki_runtime -> active_runtime -> archived`

여기서 `wiki_runtime` 은 최소 아래를 포함해야 한다.

- runtime book
- figure asset
- entity relation
- section relation
- figure relation

customer pack runtime 은 위 항목에 더해 `pack boundary metadata` 를 유지해야 한다.

## Canonical Asset Freeze

canonical asset 은 `markdown` 이 아니라 아래다.

- `structured book`
- `wiki relation json`
- `figure asset catalog`
- `active runtime manifest`

markdown 은 export 로만 취급한다.

## One-Click Runtime Freeze

one-click execution path 는 최소 아래를 묶어야 한다.

1. source-first rebuild
2. runtime materialization
3. relation refresh
4. active switch
5. smoke validation

이 중 하나라도 빠지면 one-click 이 아니다.

## Stop Conditions

아래 중 하나라도 발생하면 architecture freeze 위반이다.

1. raw manual mirror 를 최종 제품 표면처럼 다루는 경우
2. text-only runtime 을 기술 위키의 기본형으로 다시 채택하는 경우
3. relation graph 없이 viewer 만 남는 경우
4. overlay 가 본문을 덮어 읽기 경험을 망치는 경우
5. active runtime 과 contract 문서가 서로 다른 목표를 가리키는 경우
