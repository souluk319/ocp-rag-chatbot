# Code Reading Guide

이 문서는 `Play Book Studio` 코드를 처음 읽을 때 어디부터 봐야 하는지, 그리고 각 파일이 전체 파이프라인에서 무슨 역할을 하는지 빠르게 잡기 위한 가이드다.

`manifests/`와 `scripts/`처럼 JSON/JSONL 또는 얇은 진입점 위주의 폴더는 [FILE_ROLE_GUIDE.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/FILE_ROLE_GUIDE.md)를 같이 보면 훨씬 빠르다.
남은 구조개편 후보와 우선순위는 [STRUCTURE_REFACTOR_BACKLOG.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/STRUCTURE_REFACTOR_BACKLOG.md)에 따로 정리해 두었다.

## 1. 가장 먼저 볼 파일 순서

1. [cli.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/cli.py)
- 제품 기준 단일 실행 진입점이다.
- `ui / ask / eval / ragas / runtime`가 어디로 연결되는지 먼저 본다.

2. [settings.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/settings.py)
- `.env`가 어떻게 읽히는지, artifacts/manifest/path/endpoint가 어디서 결정되는지 본다.
- LLM, embedding, qdrant, reranker, pack 버전이 여기서 결정된다.

3. [packs.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/packs.py)
- 앱 정체성(`Play Book Studio`)과 현재 코퍼스 정체성(`OpenShift 4.20 core pack`)을 분리해서 이해할 수 있다.
- 버전/언어별 viewer path와 manifest naming도 여기서 본다.

여기까지 읽고 나면, 다음으로는 `공통 AST`를 먼저 보는 것이 좋다.

- [models.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/models.py)
- [html.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/html.py)
- [project_corpus.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_corpus.py)
- [project_playbook.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_playbook.py)
- [validate.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/validate.py)

이 묶음은 `고품질 코퍼스 + 사람이 읽는 플레이북 문서`를 같은 원천 구조에서 만들기 위한 새 기준선이다.
즉 `heading / prerequisite / procedure / code / note-warning / table / anchor`를 typed block으로 보관하고,
`html.py`가 현재 HTML 정규화 결과를 AST로 올리고, 이후 corpus projection과 playbook projection이 둘 다 여기서 나온다.

4. [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/server.py)
- 실제 채팅 요청이 들어와서 어떤 순서로 answerer를 호출하고 세션을 업데이트하는지 본다.
- route wiring과 request 흐름은 여기에 있다.
- 다만 session log/debug는 [chat_debug.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/chat_debug.py), 세션 문맥/follow-up 규칙은 [session_flow.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/session_flow.py), doc-to-book draft lifecycle은 [intake_api.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/intake_api.py), source viewer/canonical source book helper는 [source_books.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books.py)로 분리됐다.

5. [answerer.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/answerer.py)
- 이 프로젝트의 핵심 런타임 spine이다.
- `retrieve -> context -> prompt -> llm -> answer shaping -> citation finalize` 흐름을 본다.

6. [answer_text.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/answer_text.py), [citations.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/citations.py)
- 예전 `answerer.py`에 몰려 있던 답변 문장 정리와 citation 후처리 helper를 떼어낸 파일이다.
- answerer 본체가 너무 길게 느껴질 때 바로 같이 보면 이해가 빨라진다.

7. [context.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/context.py)
- retrieval 결과 중 무엇을 실제 근거로 채택할지 결정한다.
- clarification이 왜 발생하는지도 여기서 본다.

8. [prompt.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/prompt.py)
- grounded prompt와 답변 스타일 지침이 어떻게 만들어지는지 본다.

9. [llm.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/llm.py)
- 실제 LLM endpoint 호출 방식과 provider fallback 관련 동작을 본다.

10. [query.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query.py)
- retrieval 질문 해석의 공개 허브다.
- 지금은 실제 구현을 `intents.py`, `rewrite.py`, `ambiguity.py`, `decompose.py`로 나누고, 바깥 import 경로만 유지한다.

11. [followups.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/followups.py)
- follow-up 신호와 문맥 참조 판별 helper를 query 본체에서 분리한 파일이다.
- “이 질문이 이전 턴을 가리키는가”를 먼저 보고 싶을 때 여기부터 보면 된다.

12. [ambiguity.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/ambiguity.py)
- clarification이 필요한 질문 판별만 따로 떼어낸 파일이다.
- logging ambiguity, multi-entity ambiguity, follow-up entity ambiguity를 볼 때 여기부터 보면 된다.

13. [decompose.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/decompose.py)
- retrieval용 subquery 분해 전용 파일이다.
- compare, route timeout, node NotReady, update locator 질문이 어떤 보조 쿼리로 늘어나는지 여기서 본다.

14. [corpus_scope.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/corpus_scope.py)
- 코퍼스 밖 제품 질문과 버전 mismatch를 판별하는 helper다.
- “왜 이 질문이 아예 검색 전에 걸러졌나”를 볼 때 먼저 보면 된다.

15. [text_utils.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/text_utils.py)
- query 전처리에 공통으로 쓰는 공백 정리, dedupe, 토큰 수 계산 helper다.
- 이후 `query.py`를 더 쪼갤 때 기준이 되는 가장 작은 기반 파일이다.

16. [intents.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/intents.py), [rewrite.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/rewrite.py), [book_adjustments.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/book_adjustments.py), [book_adjustment_discovery.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/book_adjustment_discovery.py), [book_adjustment_operations.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/book_adjustment_operations.py), [query_terms.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query_terms.py), [query_terms_core.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query_terms_core.py), [query_terms_operations.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query_terms_operations.py), [query_terms_etcd.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query_terms_etcd.py)
- 질문 의도 판별과 query rewrite 축은 이제 아홉 층으로 읽는다.
- `intents.py`는 질문 종류 판별, `rewrite.py`는 공개 허브와 follow-up rewrite 판단, `book_adjustments.py`는 façade, `book_adjustment_discovery.py`는 개념/문서 탐색 규칙, `book_adjustment_operations.py`는 운영/트러블슈팅 규칙을 맡는다.
- `query_terms.py`는 façade, `query_terms_core.py`는 공통 개념/문서 탐색 용어, `query_terms_operations.py`는 운영형 용어, `query_terms_etcd.py`는 etcd 특수 용어를 맡는다.

17. [retriever.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever.py)
- BM25/vector/reranker를 오케스트레이션하는 메인 런타임이다.
- 이제는 intake overlay, trace 조립, vector 검색, fusion/scoring 본체가 밖으로 빠져서 진짜 런타임 흐름 위주로 읽을 수 있다.

18. [scoring.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/scoring.py)
- hybrid 후보를 실제 순위로 바꾸는 fusion/scoring 본체다.
- “왜 support가 이겼지?”, “왜 intake 문서가 generic 문서를 이겼지?” 같은 질문은 여기서 본다.

19. [ranking.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/ranking.py)
- RRF merge, 노이즈 필터, hit summary 같은 ranking 보조를 모아 둔 파일이다.
- trace 지표나 merge 동작을 이해할 때 retriever 본체와 같이 보면 좋다.

20. [trace.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/trace.py)
- retrieval 단계 trace 이벤트와 최종 trace payload를 조립한다.
- 검색 과정 디버깅 포맷을 바꿀 때 여기부터 보는 게 맞다.

21. [intake_overlay.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/intake_overlay.py)
- 업로드 자료를 retrieval overlay로 섞는 helper다.
- draft 선택 필터와 overlay BM25 인덱스 생성이 여기 있다.

22. [vector.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/vector.py)
- Qdrant vector 검색 전용 모듈이다.
- embedding 호출과 `/points/search` 또는 `/points/query` fallback이 여기 있다.

23. [reranker.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/reranker.py)
- 현재는 optional 실험 경로다.
- 기본값은 off지만, 실험 시 top-N 2차 재정렬이 어디서 일어나는지 이해할 수 있다.

24. [service.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/service.py), [builders.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/builders.py), [pdf_rows.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_rows.py), [pdf_helpers.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_helpers.py), [pdf_outline.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_outline.py), [pdf_cleanup.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_cleanup.py)
- 업로드 문서 정규화는 이제 네 층으로 읽으면 된다.
- `service.py`는 normalize 저장/상태 갱신, `builders.py`는 web/pdf canonical book 조립, `pdf_rows.py`는 PDF row 조립, `pdf_helpers.py`는 공개 facade, `pdf_outline.py`는 outline/anchor 탐색, `pdf_cleanup.py`는 page/docling cleanup을 맡는다.

25. [pipeline.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/pipeline.py)
- ingestion 전체 orchestration이다.
- `manifest -> collect -> normalize -> chunk -> embed -> qdrant` 순서를 본다.
- 현재 normalize 단계는 `canonical AST`를 거쳐 retrieval용 `normalized_docs.jsonl`과 viewer용 `playbook_documents.jsonl`/`playbooks/<slug>.json`을 같이 만든다.

26. [collector.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/collector.py)
- 실제 원문 HTML을 가져와 raw cache로 저장하는 부분이다.
- source fingerprint 기반 재수집 정책도 여기서 본다.

27. [normalize.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/normalize.py)
- HTML에서 법적 공지, 목차, 버튼 같은 노이즈를 걷어내고 canonical section으로 바꾸는 부분이다.
- 코퍼스 품질 문제가 의심되면 여기부터 다시 본다.

28. [chunking.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/chunking.py)
- canonical section이 어떤 chunk 크기와 경계로 잘리는지 본다.
- chunk size/overlap, book별 chunk profile 튜닝 지점이다.

29. [audit.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/audit.py), [audit_rules.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/audit_rules.py), [data_quality.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/data_quality.py), [approval_report.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/approval_report.py), [translation_lane.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/translation_lane.py)
- ingestion audit는 이제 네 층으로 읽는다.
- `audit.py`는 공개 façade, `audit_rules.py`는 언어/승인 판정 규칙, `data_quality.py`는 제목/본문/경로 품질 리포트, `approval_report.py`는 승인 리포트와 runtime manifest 조립, `translation_lane.py`는 `en_only -> translated_ko_draft -> approved_ko` provenance 규칙을 맡는다.

30. [presenters.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/presenters.py)
- UI에 내려가는 health payload, citation payload, runtime fingerprint, source viewer payload를 만든다.

31. [chat_debug.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/chat_debug.py)
- 최근 대화 snapshot, turn diagnosis, 단계 요약, chat log 기록을 담당한다.

32. [session_flow.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/session_flow.py)
- 세션 문맥 갱신, 후속 질문 추천, request override 규칙을 담당한다.

33. [intake_api.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/intake_api.py)
- 업로드 문서 draft 생성/업로드/capture/normalize API helper를 담당한다.

34. [source_books.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books.py)
- 내부 reference viewer, canonical source book, intake draft viewer helper를 담당한다.
- 지금은 `corpus/playbooks/<slug>.json` playbook artifact를 우선 열고, 없을 때만 normalized section fallback을 쓴다.

35. [runtime_report.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/runtime_report.py)
- 지금 프로세스가 어느 endpoint/collection/artifact를 보고 있는지 자동 리포트로 뽑아낸다.

36. [answer_eval.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/evals/answer_eval.py), [retrieval_eval.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/evals/retrieval_eval.py), [ragas_eval.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/evals/ragas_eval.py)
- 회귀 검증이 어떻게 도는지 확인한다.

## 2. 런타임 질문 처리 파이프라인

```text
play_book.cmd ui / ask
-> cli.py
-> server.py or answerer.py
-> query.py
-> retriever.py
-> context.py
-> prompt.py
-> llm.py
-> answerer.py post-processing
-> presenters.py / server.py
-> UI or JSON response
```

핵심 관찰 포인트:
- 질문 해석: [query.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query.py)
- 근거 검색: [retriever.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever.py)
- 근거 선택: [context.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/context.py)
- 답변 형태: [prompt.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/prompt.py), [answerer.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/answerer.py)

## 3. 코퍼스 구축 파이프라인

```text
source catalog / approved manifest
-> collector.py
-> normalize.py
-> canonical AST
-> chunking.py
-> embedding.py
-> qdrant_store.py
-> retrieval runtime
```

핵심 관찰 포인트:
- 원문 source URL/승인 manifest: [manifest.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/manifest.py)
- 원문 HTML 수집: [collector.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/collector.py)
- section 정규화: [normalize.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/normalize.py)
- 공통 원천 구조: [models.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/models.py), [html.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/html.py), [project_corpus.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_corpus.py), [project_playbook.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_playbook.py)
- 주요 AST 산출물: `../ocp-rag-chatbot-data/corpus/normalized_docs.jsonl`, `../ocp-rag-chatbot-data/corpus/playbook_documents.jsonl`, `../ocp-rag-chatbot-data/corpus/playbooks/<slug>.json`
- chunk 생성: [chunking.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/chunking.py)
- vector 적재: [embedding.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/embedding.py), [qdrant_store.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/qdrant_store.py)

## 4. 디테일 튜닝할 때 먼저 보는 포인트

### 답변이 엉뚱한 근거를 집을 때
- [query.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query.py)
- [retriever.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever.py)
- [context.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/context.py)

### 정규화가 지저분할 때
- [normalize.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/normalize.py)
- [models.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/models.py)
- [validate.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/validate.py)
- [project_playbook.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_playbook.py)
- [chunking.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/chunking.py)
- [audit.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/audit.py)
- [data_quality.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/data_quality.py)
- [approval_report.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/approval_report.py)
- [translation_lane.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/translation_lane.py)

### endpoint/모델/collection이 헷갈릴 때
- [settings.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/settings.py)
- [presenters.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/presenters.py)
- [runtime_report.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/runtime_report.py)

### UI payload가 이상할 때
- [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/server.py)
- [presenters.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/presenters.py)
- [index.html](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/index.html)
- [panel-controller.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/panel-controller.js)
- [app-shell-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-shell-state.js)
- [app-bootstrap.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-bootstrap.js)
- [shell-helpers.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/shell-helpers.js)
- [message-shells.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/message-shells.js)
- [workspace-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/workspace-state.js)
- [chat-renderer.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/chat-renderer.js)
- [chat-session.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/chat-session.js)
- [intake-renderer.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/intake-renderer.js)
- [intake-actions.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/intake-actions.js)
- [diagnostics-renderer.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/diagnostics-renderer.js)
- [source-workflows.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/source-workflows.js)
- [STRUCTURE_REFACTOR_BACKLOG.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/STRUCTURE_REFACTOR_BACKLOG.md)

여기서 DOM ref 수집과 mutable shell state 기본값은 [app-shell-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-shell-state.js)에서 보고, 앱 부팅 순서와 모듈 wiring은 [app-bootstrap.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-bootstrap.js)에서 본다. 공통 DOM helper와 shell 상태 동기화는 [shell-helpers.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/shell-helpers.js)에서 본다. empty state, pending panel, citation chip, 메시지 wrapper 조립은 [message-shells.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/message-shells.js)에서 본다. 팩 선택/업로드 자료 선택 집합/보관함/최근 초안 목록은 [workspace-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/workspace-state.js)에서 보고, 채팅 송수신/스트리밍 소비/세션 리셋은 [chat-session.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/chat-session.js)에서 보면 된다.

## 5. 발표/설명할 때 쓰기 좋은 한 문장

- 이 프로젝트는 `OCP 문서 정리 -> 하이브리드 검색 -> grounded answer generation -> citation/viewer/UI`를 직접 분리 구현한 OCP Playbook Studio다.
- 기술적으로는 `ingestion`, `retrieval`, `answering`, `app`, `evals` 다섯 축으로 설명하면 가장 깔끔하다.
- 실무 튜닝은 보통 `normalize/chunking`, `query/retriever`, `prompt/answer shaping` 세 곳에서 일어난다.
