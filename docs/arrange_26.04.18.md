설계 판단만 잠갔다. 구현은 아직 하지 않는 게 맞다.

재사용 가능한 PBS 자산은 이미 충분하다.  
[graph_runtime.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/graph_runtime.py:329)의 `LocalGraphSidecar`와 compact artifact 경로, [source_books_viewer_payloads.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books_viewer_payloads.py:54)의 hub/backlinks/related sections, [service.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/service.py:17)의 Docling normalize seam, [presenters.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/presenters.py:408)의 parser/quality trace, [retriever_rerank.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever_rerank.py:177)의 rerank gate를 그대로 쓸 수 있다.

**A. 채택안 3개**
1. `Docling + degraded-PDF detector + Surya/Marker fallback`
- 왜 PBS에 맞는지: retrieval 정확도와 위키 품질을 동시에 올린다. 지금 PBS의 가장 직접적인 품질 손실은 깨진 PDF 정규화다.
- 어디에 꽂는지: [service.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/service.py:17) normalize 경로에 `degraded PDF` 판정만 추가하고, fallback 결과를 [presenters.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/presenters.py:408)와 [source_books_customer_pack.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books_customer_pack.py:34)에 `parser_backend / fallback_used / quality_score`로 남긴다.
- 기대효과: retrieval 정확도 `큼`, 멀티턴 안정성 `중간`, 설명 가능성 `중간`, playbook 위키 품질 `큼`.
- 구현 난이도: `중간`
- 지금 할지 / 나중에 할지: `지금`

2. `Graphify 원리만 차용한 relation-aware retrieval + topic cluster + provenance summary`
- 왜 PBS에 맞는지: PBS는 이미 graph sidecar와 compact graph artifact가 있다. 새 그래프 제품을 들이는 게 아니라, existing graph를 검색 보조와 설명 레이어에 더 잘 쓰면 된다.
- 어디에 꽂는지: [graph_runtime.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/graph_runtime.py:385) compact artifact, [graph_runtime.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/graph_runtime.py:397) playbook documents fallback, 기존 Explain/trace surface.
- 기대효과: retrieval 정확도 `중간`, 멀티턴 안정성 `중간`, 설명 가능성 `큼`, playbook 위키 품질 `중간`.
- 구현 난이도: `중간`
- 지금 할지 / 나중에 할지: `다음 실험`

3. `Obsidian 원리만 차용한 bidirectional links + topic hub + virtual hierarchy`
- 왜 PBS에 맞는지: PBS는 위키 제품이다. 사용자는 문서 하나가 아니라 “연결된 읽기 경로”를 원한다. Obsidian의 강점은 UI가 아니라 링크 구조다.
- 어디에 꽂는지: [source_books_viewer_payloads.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books_viewer_payloads.py:54), [source_books_viewer_payloads.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books_viewer_payloads.py:381), [source_books_viewer_payloads.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books_viewer_payloads.py:432) 위에 hub/backlinks/related sections를 더 일관되게 묶는다.
- 기대효과: retrieval 정확도 `작음`, 멀티턴 안정성 `중간`, 설명 가능성 `중간`, playbook 위키 품질 `큼`.
- 구현 난이도: `작음~중간`
- 지금 할지 / 나중에 할지: `나중에`

**B. 보류안 3개**
1. `FlashRank shadow rerank lane`
- 왜 PBS에 맞는지: LLM rerank 비용과 latency 없이 CPU에서 얇게 precision을 올릴 여지가 있다.
- 어디에 꽂는지: [retriever_rerank.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever_rerank.py:177), [retriever_rerank.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever_rerank.py:211), [retriever_rerank.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever_rerank.py:1225) 뒤에 shadow A/B로 붙이기 쉽다.
- 기대효과: retrieval 정확도 `중간`, 멀티턴 안정성 `작음`, 설명 가능성 `작음`, playbook 위키 품질 `없음`.
- 구현 난이도: `작음`
- 지금 할지 / 나중에 할지: `보류`

2. `ColBERTv2 late-interaction retrieval lane`
- 왜 PBS에 맞는지: 문단 의미가 비슷하지만 lexical hit가 약한 long-tail 질의에 강할 수 있다.
- 어디에 꽂는지: official/private corpus materialization 옆에 별도 index lane으로만 꽂아야 한다. 기존 Qdrant/compact graph를 바로 대체하면 안 된다.
- 기대효과: retrieval 정확도 `중간~큼`, 멀티턴 안정성 `중간`, 설명 가능성 `작음`, playbook 위키 품질 `없음`.
- 구현 난이도: `큼`
- 지금 할지 / 나중에 할지: `나중에`

3. `Memgraph를 offline graph analytics lab로만 제한 사용`
- 왜 PBS에 맞는지: community detection이나 impact analysis를 batch/offline으로 시험해볼 수는 있다.
- 어디에 꽂는지: live request path가 아니라 graph artifact build 후 별도 분석 lane으로만 둔다.
- 기대효과: retrieval 정확도 `작음~중간`, 멀티턴 안정성 `작음`, 설명 가능성 `중간`, playbook 위키 품질 `중간`.
- 구현 난이도: `중간~큼`
- 지금 할지 / 나중에 할지: `나중에`

**C. 폐기안 3개**
1. `Graphify 자체를 PBS 안에 통째로 들여오는 것`
- 왜 PBS에 맞지 않는지: Graphify는 자체 추출기, 자체 graph JSON, 자체 report를 만든다. PBS는 이미 canonical truth, graph sidecar, playbook documents, trace surface가 있다. 중복 계층이 된다.
- 어디에 꽂는지: 꽂지 않는다.
- 기대효과: 기능은 일부 겹치지만 구조 중복과 운영 복잡도가 더 크다.
- 구현 난이도: `큼`
- 지금 할지 / 나중에 할지: `하지 않음`

2. `Obsidian식 markdown vault / block reference를 PBS canonical source로 채택하는 것`
- 왜 PBS에 맞지 않는지: PBS의 진실 소스는 structured wiki runtime이어야 한다. Obsidian block reference는 Obsidian 특화 문법이라 상호운용성이 약하다.
- 어디에 꽂는지: 꽂지 않는다.
- 기대효과: 위키 감성은 줄 수 있어도 retrieval/citation contract를 더 복잡하게 만든다.
- 구현 난이도: `중간`
- 지금 할지 / 나중에 할지: `하지 않음`

3. `Memgraph로 Neo4j/Qdrant/live graph path를 지금 바로 교체하는 것`
- 왜 PBS에 맞지 않는지: PBS는 방금 graph/runtime instability를 hardening한 상태다. 이 시점의 DB 교체는 안정화 축을 다시 흔든다.
- 어디에 꽂는지: 꽂지 않는다.
- 기대효과: 이론상 성능 이점은 있어도, 지금 PBS 핵심가치 대비 infra churn이 더 크다.
- 구현 난이도: `큼`
- 지금 할지 / 나중에 할지: `하지 않음`

**최종 판단**
- 지금 할 1개: `OCR / parsing fallback 전략`
- 다음 실험 1개: `compact graph artifact 기반 relation-aware retrieval + provenance summary`
- 보류 1개: `FlashRank shadow rerank lane`

**짧은 결론**
- PBS 핵심가치를 가장 직접 올리는 건 `parser quality hardening`이다.
- 그다음은 `기존 graph 자산을 더 설명 가능하게 쓰는 것`이다.
- `새 그래프 DB`와 `새 retrieval 엔진`은 지금 당장 제품가치보다 infra churn이 더 크다.

**근거 원전**
- Graphify: [site](https://graphify.net/knowledge-graph-for-ai-coding-assistants.html), [Leiden](https://graphify.net/leiden-community-detection.html), [README.ko-KR](https://github.com/safishamsi/graphify/blob/v4/README.ko-KR.md)
- Obsidian: [Backlinks](https://obsidian.md/help/plugins/backlinks), [Graph view](https://obsidian.md/help/plugins/graph), [Internal links](https://obsidian.md/help/links)
- Surya / Marker: [Surya](https://github.com/datalab-to/surya), [Marker](https://github.com/datalab-to/marker)
- Memgraph: [Memgraph](https://memgraph.com/), [MAGE](https://github.com/memgraph/mage), [Vector Search](https://memgraph.com/vector-search)
- Rerank: [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank), [ColBERT repo](https://github.com/stanford-futuredata/ColBERT), [ColBERTv2 paper](https://cs.stanford.edu/~matei/papers/2022/naacl_colbert_v2.pdf)