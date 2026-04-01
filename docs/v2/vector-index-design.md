# Vector Index Design

## Purpose

이 문서는 planB에서 “Vector Index 구조 직접 설계 및 구현” 요구를 방어하기 위한 최소 설계와 proof 경로를 정의한다.

현재 운영 경로는 OpenDocuments + LanceDB를 사용한다. 그러나 과제 기준은 단순 라이브러리 호출을 넘어, **직접 설명 가능한 인덱스 계층**을 요구한다.

## Current planB position

- 운영 runtime은 계속 OpenDocuments 경로를 사용한다.
- 별도로 저장소 안에 독립적인 `VectorIndex` 구현을 둔다.
- 이 구현은 제출/설명/확장 출발점 역할을 한다.

즉, planB의 1차 목표는 운영 경로를 즉시 갈아엎는 것이 아니라, **직접 구현 요구를 방어할 수 있는 독립 인덱스 계층을 코드와 증거로 확보하는 것**이다.

## Direct implementation scope

1. 저장 형식 직접 정의
   - JSON 기반 저장
   - `dimensions`, `record_count`, `records` 구조
2. 레코드 구조 직접 정의
   - `chunk_id`
   - `document_id`
   - `document_path`
   - `section_id`
   - `section_title`
   - `viewer_url`
   - `embedding`
   - `metadata`
3. 검색 로직 직접 구현
   - cosine similarity
   - score 정렬
   - top-k 반환
4. 입출력 직접 구현
   - `save()`
   - `load()`

## Current proof files

- 구현: `app/vector_index.py`
- proof report: `eval/vector_index_proof.py`
- 생성 증거:
  - `data/manifests/generated/vector-index-sample.json`
  - `data/manifests/generated/vector-index-proof.json`

## Why this matters

이 경로는 다음 질문에 답하기 위해 필요하다.

- 벡터 인덱스를 직접 설계했다고 말할 수 있는가?
- embedding과 metadata를 어떤 구조로 저장하는가?
- 검색 점수는 어떻게 계산하는가?
- top-k 결과는 어떤 정보와 함께 반환되는가?

현재 proof는 최소 구현이지만, 위 질문에 대해 코드 수준 설명이 가능하다.

## Limitations

- 아직 운영 runtime의 주 검색 경로를 대체하지는 않는다.
- ANN/HNSW 같은 고급 탐색은 아직 없다.
- widened corpus 규모 성능 비교는 아직 없다.

## Next extension path

1. chunk contract 기반 실제 chunk 레코드 생성
2. normalized manifest에서 sample record 자동 추출
3. brute-force baseline vs ANN path 비교
4. runtime sidecar retrieval proof 추가
