# VENDOR_NOTES.md

## 목적

이 문서는 vendor-specific API, 외부 dependency, 환경 전제를 짧고 현재 코드 기준으로 기록한다.
설명 대상은 `Play Book Studio` 현재 런타임이며, 과거 구조 설명은 남기지 않는다.

원칙:

- 항목은 짧게 유지
- 마지막 확인 날짜를 남긴다
- 코드에서 암묵적으로 기대하는 환경 전제를 먼저 여기서 설명한다

## Red Hat OCP Docs

- `Last checked`: 2026-04-09
- `Primary source`: [docs.redhat.com OCP 4.20 Korean docs](https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20)
- `Current collection shape`: published `html-single` 페이지를 section-aware record로 정규화
- `Runtime source catalog`: [manifests/ocp_ko_4_20_html_single.json](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/manifests/ocp_ko_4_20_html_single.json)
- `Runtime approved manifest`: [manifests/ocp_ko_4_20_approved_ko.json](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/manifests/ocp_ko_4_20_approved_ko.json)
- `Viewer path template`: `/docs/ocp/4.20/ko/{slug}/index.html`
- `Do not assume`: future OCP versions, English-only docs, non-OCP corpora가 기본으로 준비되어 있다고 가정하지 말 것

## Qdrant

- `Last checked`: 2026-04-09
- `Runtime role`: retrieval vector store
- `Primary env`: `QDRANT_URL`, `QDRANT_COLLECTION`, `QDRANT_VECTOR_SIZE`, `QDRANT_DISTANCE`
- `Current default collection`: `openshift_docs`
- `Current expected vector size`: `1024`
- `Code`: [src/play_book_studio/ingestion/qdrant_store.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/qdrant_store.py)
- `Do not assume`: shared Qdrant 환경에서 collection 재생성이 안전하다고 가정하지 말 것

## Embeddings

- `Last checked`: 2026-04-09
- `Default model`: `dragonkue/bge-m3-ko`
- `Primary env`: `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`, `EMBEDDING_API_KEY`
- `Current implementation note`:
  - remote embedding endpoint를 우선 사용
  - remote probe가 실패하면 runtime report에서 바로 확인 가능해야 함
- `Code`: [src/play_book_studio/ingestion/embedding.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/embedding.py), [src/play_book_studio/ingestion/sentence_model.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/sentence_model.py)
- `Do not assume`: remote embedding service가 항상 `/models` probe를 지원한다고 가정하지 말 것

## LLM Endpoint

- `Last checked`: 2026-04-09
- `Runtime contract`: OpenAI-compatible `chat/completions` endpoint
- `Primary env`: `LLM_ENDPOINT`, `LLM_API_KEY`, `LLM_MODEL`
- `Current product assumption`: 사내 Qwen 계열 endpoint 전제
- `Code`: [src/play_book_studio/answering/llm.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/llm.py)
- `Do not hardcode`: vendor base URL, auth header shape, model name
- `Do not assume`: 개발용 PC, 운영용 PC, 다른 장비가 동일 endpoint를 쓴다고 가정하지 말 것

## Optional Evaluation Stack

- `Last checked`: 2026-04-09
- `Optional deps`: `ragas`, `datasets`
- `Role`: evaluation only
- `Not required for`: normal chatbot runtime
- `Do not assume`: eval extras가 모든 환경에 설치되어 있지 않음

## Local Artifacts

- `Last checked`: 2026-04-09
- `Primary env`: `ARTIFACTS_DIR`
- `Current canonical location`: repo 밖 [ocp-rag-chatbot-data](/C:/Users/soulu/cywell/ocp-play-studio/ocp-rag-chatbot-data)
- `Current semantic dirs`: `corpus / retrieval / answering / runtime / doc_to_book`
- `Rule`: `.env`의 artifact path를 source of truth로 본다
- `Do not assume`: repo-root `artifacts/`가 canonical store라고 가정하지 말 것

## UI Config

- `Last checked`: 2026-04-09
- `Current file`: [src/play_book_studio/app/static/assets/app-config.js](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-config.js)
- `Role`: core pack label, empty-state sample prompts 같은 presentation config를 모아 둔다
- `Do not assume`: 이 파일 하나로 UI hardcoding 문제가 전부 해결된 것은 아님

## 마지막 원칙

- vendor 전제는 코드보다 이 문서에서 먼저 설명 가능해야 한다
- 설명이 길어질 정도로 vendor 종속이 커지면 구조 분리가 필요하다
