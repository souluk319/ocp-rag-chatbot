정리됐다. 이제 `의견 모음`이 아니라 `실행 사양` 수준이다.

**잠금본**
1. `degraded_pdf_detector_and_evidence`
- 목표: 깨진 PDF를 기계적으로 판정하고, normalize 결과에 evidence를 남긴다.
- 변경 범위: degraded 판정 함수, normalize fallback seam, evidence 필드 노출
- 비목표: Surya/Marker 본도입, 대량 backfill, viewer 품질 완성, OCR 튜닝
- 완료 조건:
  - degraded fixture는 degraded로 잡힘
  - 정상 fixture는 degraded로 오탐되지 않음
  - fallback parser 미설치 상태에서도 normalize와 evidence가 깨지지 않음
  - `parser_backend`, `fallback_used`, `quality_score`, `degraded_reason`가 남음
- 검증:
  - degraded positive test
  - normal negative test
  - fallback-missing graceful test
  - evidence payload/UI metadata test

2. `graph_relation_rerank_signal`
- 목표: compact graph relation을 retrieval 보조 신호로 쓸 가치가 있는지 본다.
- 변경 범위: graph signal 계산, shadow metric 수집, trace 비교
- 비목표: live ranking 교체, topic cluster, provenance summary 확장
- 완료 조건:
  - 기존 ranking을 덮어쓰지 않음
  - graph on/off shadow 비교가 가능함
  - `hit@k`, citation relevance, 이상치 query 샘플 비교가 남음
- 검증:
  - shadow run 결과 저장
  - query set 전/후 비교
  - 회귀 없는지 확인

3. `obsidian_hub_normalization`
- 상태: 나중
- 1차 실험 후보는 나중에 아래 셋 중 하나만 고른다.
- `topic hub auto-generation`
- `backlinks normalization`
- `virtual hierarchy for messy uploads`

**순서**
- 먼저 `PDF 품질 판정 계약`
- 그다음 `graph rerank 최소 실험`
- Obsidian 원리는 그 이후

**하드웨어 판단**
- packet 1은 현재 PC로 충분하다.
- RTX 서버가 필요한 분기점은 `Surya/Marker 실운영 fallback`을 실제로 돌리거나 `ColBERT indexing`으로 갈 때다.
- 지금은 외부 GPU endpoint를 붙일 단계가 아니다.

**한 줄 결론**
지금 PBS에 맞는 다음 행동은 `신형 파서 도입`이 아니라 `degraded PDF 판정 계약 잠금`이다. 그다음에만 graph signal 실험으로 간다.