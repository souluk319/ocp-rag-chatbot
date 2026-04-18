---
status: reference
doc_type: explainer
audience:
  - engineer
  - codex
last_updated: 2026-04-17
---

# Retrieval Flow

이 문서는 `PlayBookStudio` 의 retrieval 경로를 사람이 빠르게 이해하기 위한 요약이다.
active contract 를 대체하지 않고, 현재 코드가 어떻게 이어지는지 번역해서 보여주는 용도다.

## 먼저 보는 구조

- `src/play_book_studio/`
  - 제품 런타임 코드다.
  - UI 서버, CLI, ingestion, retrieval, answering 이 모두 여기서 import 된다.
  - `pyproject.toml` 이 `src` layout 을 쓰기 때문에, 제품 동작을 바꾸는 코드는 기본적으로 여기서 고친다.
- `scripts/`
  - 운영용 실행 스크립트와 보조 도구다.
  - build, verify, backfill, one-click runtime, harness 준비 같은 task-oriented 진입점이 모여 있다.
  - 원칙적으로 `scripts` 는 제품 로직의 진실 소스가 아니라 `src` 안의 기능을 호출하거나 묶는 래퍼여야 한다.
- `tests/`
  - runtime, retrieval, citation, packet 회귀를 잠그는 곳이다.
- `data/`, `artifacts/`, `reports/`
  - 입력 산출물, 런타임 artifact, 실행 하네스/검증 보고서가 쌓이는 곳이다.

짧게 말하면:

- `src` = 제품 본체
- `scripts` = 제품을 돌리고 검증하는 작업용 입구

그래서 `src` 와 `scripts` 가 둘 다 있는 것은 이상한 구조라기보다 역할 분리 자체는 정상이다.
다만 지금 `scripts/` 가 커 보이는 이유는 운영/검증/패킷 실행 스크립트가 많이 누적되어 있기 때문이다.

## retrieval 경로를 볼 때 먼저 여는 파일

- `src/play_book_studio/answering/answerer.py`
  - 채팅 답변의 최상위 spine
  - `retrieve -> context assembly -> answer -> citation finalize`
- `src/play_book_studio/retrieval/retriever.py`
  - retrieval 런타임 진입점
- `src/play_book_studio/retrieval/retriever_pipeline.py`
  - 실제 retrieval 단계 순서를 묶는 핵심 파일
- `src/play_book_studio/retrieval/retriever_plan.py`
  - 질문 정규화, rewrite, 분해, candidate budget 결정
- `src/play_book_studio/retrieval/retriever_search.py`
  - BM25 / vector 후보 검색
- `src/play_book_studio/retrieval/graph_runtime.py`
  - graph expand 와 local/remote/neo4j fallback
- `src/play_book_studio/retrieval/retriever_rerank.py`
  - rerank 적용 여부와 heuristic rebalance
- `src/play_book_studio/retrieval/models.py`
  - `RetrievalHit`, `RetrievalResult`

## retrieval 흐름 한 장 요약

아래 순서로 읽으면 된다.

1. 질문 진입
   - `ChatAnswerer.answer()` 가 채팅 질문을 받는다.
   - non-RAG 로 바로 보낼 질문이 아니면 `ChatRetriever.retrieve()` 로 내려간다.

2. 질문 정규화
   - `build_retrieval_plan()` 이 먼저 `normalize_query()` 를 호출한다.
   - 공백 정리, 기본 표현 정리, unsupported product 감지 같은 retrieval 준비 단계다.

3. 리라이트와 질문 분해
   - 같은 `build_retrieval_plan()` 안에서 `rewrite_query()` 와 `decompose_retrieval_queries()` 가 돈다.
   - follow-up, 짧은 문맥 의존 질문, 비교 질문일 때 검색용 질의를 더 명확하게 만든다.
   - 필요하면 `candidate_k` 를 `40` 이상으로 늘려서 후보 풀을 넓힌다.

4. BM25 검색
   - `search_bm25_candidates()` 가 `rewritten_queries` 각각에 대해 BM25 검색을 수행한다.
   - customer/uploaded overlay 가 있으면 overlay BM25 도 같이 검색하고, 가중 합쳐서 올린다.

5. Vector 검색
   - `search_vector_candidates()` 가 같은 `rewritten_queries` 로 의미 검색을 수행한다.
   - subquery별 endpoint 사용 정보와 hit 수를 trace 로 남긴다.

6. Hybrid fusion
   - `fuse_ranked_hits()` 가 BM25 결과와 vector 결과를 하나의 후보 리스트로 합친다.
   - top hit 가 BM25+vector 둘 다의 지지를 받는지, 한쪽만 받는지도 trace 에 남긴다.

7. Graph expand 여부 결정
   - `_should_expand_graph()` 가 graph 단계를 탈지 말지 정한다.
   - 보통 아래 조건이면 탄다.
   - follow-up 질문
   - 분해된 질문 수가 2개 이상
   - explainer/compare/operator/MCO 같은 graph-worthy intent
   - derived runtime hit 또는 non-core hit 존재
   - 상위 후보의 cross-book ambiguity

8. Graph expand 실행
   - `RetrievalGraphRuntime.enrich_hits()` 가 graph payload 를 붙인다.
   - 우선순위는 설정에 따라 `neo4j -> remote endpoint -> local sidecar` 가 아니라, `resolved mode` 기준으로 시도하고 실패 시 local sidecar fallback 으로 내려간다.
   - 현재 안정화 작업 이후 local sidecar 는 oversized full sidecar eager-load 를 피하고 compact artifact 를 우선 사용한다.

9. Rerank 조건 판단
   - `maybe_rerank_hits()` 가 reranker 모델을 실제로 돌릴지, heuristic-only 재정렬만 할지 결정한다.
   - derived/non-core hit, follow-up, semantic intent, cross-book ambiguity 가 있으면 model rerank 쪽으로 기운다.
   - explanation query 에서는 candidate budget 을 줄여 과도한 rerank 비용을 막는다.

10. Rerank / heuristic rebalance
   - model rerank 가 켜지면 cross-encoder 가 상위 후보만 다시 읽는다.
   - 그 다음에도 `retriever_rerank.py` 의 규칙들이 top hit 를 다시 조정할 수 있다.
   - 예: topic playbook 우선, uploaded customer pack 우선, generic intro rescue, registry/MCO/etcd 같은 intent별 재배치

11. RetrievalResult 생성
   - 마지막에 `RetrievalResult` 가 만들어진다.
   - 여기에는 아래가 들어간다.
   - `normalized_query`
   - `rewritten_query`
   - 최종 `hits`
   - BM25 / vector / graph / rerank / timings 가 담긴 `trace`

12. Answer 단계로 복귀
   - `answerer.py` 로 돌아가서 citation context 조립, deterministic fast path 여부 판단, LLM 호출, citation finalize 를 수행한다.

## 코드처럼 보면 이런 흐름이다

```text
ChatAnswerer.answer
  -> ChatRetriever.retrieve
    -> build_retrieval_plan
      -> normalize_query
      -> rewrite_query
      -> decompose_retrieval_queries
    -> search_bm25_candidates
    -> search_vector_candidates
    -> fuse_ranked_hits
    -> maybe graph expand
      -> RetrievalGraphRuntime.enrich_hits
    -> maybe rerank
      -> maybe_rerank_hits
    -> RetrievalResult
  -> assemble_context
  -> prompt / deterministic answer / LLM
  -> finalize_citations
```

## 각 단계에서 주로 보는 신호

- 질문이 이상하게 바뀌면:
  - `retriever_plan.py`
  - `query.py`
  - `rewrite.py`
- BM25/vector 후보가 이상하면:
  - `retriever_search.py`
  - `bm25.py`
  - `vector.py`
- top hit 순서가 납득이 안 되면:
  - `scoring.py`
  - `graph_runtime.py`
  - `retriever_rerank.py`
- 답변은 나오는데 citation landing 이 이상하면:
  - `answering/context.py`
  - `answering/citations.py`
  - `answering/answerer.py`

## 지금 구조를 이해할 때의 현실적인 포인트

- retrieval 복잡도의 대부분은 "검색기 하나"보다 "후보를 언제 넓히고 언제 다시 줄이는가" 에 있다.
- `retriever_pipeline.py` 는 순서 제어 파일이고, 실제 정책의 무게는 `query/rewrite`, `graph_runtime`, `retriever_rerank` 쪽에 분산돼 있다.
- 그래서 retrieval 버그를 볼 때는 보통 한 파일만 읽어서는 부족하고 아래 세 축을 같이 봐야 한다.
  - 질의 준비
  - 후보 생성과 fusion
  - graph/rerank 재정렬

## 다음에 더 정리하고 싶다면

문서만으로도 이해는 되지만, 구조를 더 단단하게 보이게 하려면 다음 정리 후보가 있다.

- `scripts/` 를 `build / verify / runtime / harness` 식으로 하위 폴더 재배치
- `retriever_rerank.py` 의 intent별 rebalance 규칙을 별도 policy 모듈로 분리
- `docs/` 에 `repo_structure.md` 와 `answer_flow.md` 를 추가해 retrieval 설명과 저장소 설명을 분리
