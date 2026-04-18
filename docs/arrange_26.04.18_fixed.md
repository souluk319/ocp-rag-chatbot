결론은 `전략은 유지`, `실행 단위는 더 좁힘`으로 바뀌었다.

지금 기준 최종 잠금은 이렇다.

1. `지금 할 것`
`degraded_pdf_detector_and_evidence`

- 왜: PM 지적대로 `Surya/Marker 도입`까지 한 packet에 넣으면 바로 커진다. 지금 1차 목표는 새 파서를 잘 돌리는 게 아니라, `무슨 PDF가 degraded인지 판정`하고 `fallback seam`과 `evidence contract`를 먼저 고정하는 것이다.
- 어디에 꽂는지:
  - [service.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/service.py:17)
  - [presenters.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/presenters.py:408)
  - [source_books_customer_pack.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books_customer_pack.py:34)
- 이번 packet 완료 조건:
  - degraded PDF 판정 기준이 코드/테스트로 고정됨
  - normalize 단계에 fallback seam이 생김
  - `parser_backend`, `fallback_used`, `quality_score`, `degraded_reason` 같은 evidence가 남음
  - 실제 fallback parser 호출은 optional 상태여도 됨
- 이번 packet에서 하지 않을 것:
  - Marker/Surya 대량 backfill
  - viewer perfection
  - OCR 성능 튜닝
  - parser 품질 완전 해결
- 검증:
  - degraded / non-degraded fixture 판정 테스트
  - normalize evidence payload 테스트
  - customer-pack viewer metadata 노출 테스트

2. `다음 실험`
`graph_relation_rerank_signal`

- 왜: `relation-aware retrieval + topic cluster + provenance summary`는 한 번에 묶으면 다시 커진다. 1차 실험은 retrieval 정확도에 직접 닿는 하나만 잡는 게 맞다.
- 어디에 꽂는지:
  - [graph_runtime.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/graph_runtime.py:329)
  - [retriever_rerank.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever_rerank.py:177)
- 실험 정의:
  - compact graph relation hit를 `추가 rerank signal`로만 사용
  - shadow metric 또는 gated rollout으로 비교
  - topic cluster / provenance summary는 이 packet에 넣지 않음

3. `나중에 할 것`
`obsidian_hub_normalization`

- 범위는 나중에 아래 셋 중 하나만 고른다.
  - `topic hub auto-generation`
  - `backlinks normalization`
  - `virtual hierarchy for messy uploads`

**하드웨어 판단**
- `지금 할 packet 1`은 RTX 서버 필요 없다. 로직/계약/증거 설계 중심이라 현재 PC로 충분하다.
- `Surya/Marker 실제 fallback 실행`은 CPU로도 가능하지만 느려질 수 있다.
  - Marker는 `GPU, CPU, or MPS` 지원
  - Surya는 CPU에서 더 느리다고 명시
- `ColBERTv2` 방향으로 가면 얘기는 달라진다.
  - 공식 repo 기준 `GPU is required for training and indexing`
  - 즉 ColBERT lane을 진짜 채택하는 순간은 RTX endpoint 확보가 맞다.
- `FlashRank`는 CPU 친화적이다.
  - 공식 README 기준 `No Torch or Transformers needed. Runs on CPU.`
- `Memgraph`는 GPU 이슈가 아니라 CPU/RAM/운영복잡도 이슈다.

즉, 지금 당장은 외부 RTX 서버를 붙일 필요 없다.  
외부 GPU를 붙여야 하는 분기점은 `Marker/Surya를 대량 실운영 backfill에 태우는 시점`이나 `ColBERT indexing lane`으로 넘어갈 때다.

근거:
- [Marker](https://github.com/datalab-to/marker)
- [Surya](https://github.com/datalab-to/surya)
- [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank)
- [ColBERT](https://github.com/stanford-futuredata/ColBERT)
- [ColBERTv2 paper](https://cs.stanford.edu/~matei/papers/2022/naacl_colbert_v2.pdf)

한 줄로 다시 잠그면 이거다.  
`다음 packet은 degraded PDF detector + evidence contract만 닫고, 그래프는 그 다음에 compact relation rerank 실험 1개만 한다.`