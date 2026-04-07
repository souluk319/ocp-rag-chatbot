# VENDOR_NOTES.md

## 목적

이 문서는 vendor-specific API, 외부 dependency, 환경 전제를 기록한다.
이 내용은 `AGENTS.md`에 두지 않고 여기서 짧고 명확하게 관리한다.

원칙:

- 항목은 짧게 유지
- 가능하면 날짜를 남긴다
- 코드에 흩어진 환경 전제를 먼저 여기서 설명 가능해야 한다

## Red Hat OCP Docs

- `Last checked`: 2026-04-07
- `Primary source`: OCP 4.20 Korean official documentation
- `Current collection shape`: html-single source pages normalized into section-aware records
- `Viewer path template`: `/docs/ocp/4.20/ko/{slug}/index.html`
- `Manifest`: [`manifests/ocp_ko_4_20_html_single.json`](/Users/kugnus/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-v2/manifests/ocp_ko_4_20_html_single.json)
- `Do not assume`: future versions or non-OCP corpora are available unless explicitly ingested

## Qdrant

- `Last checked`: 2026-04-07
- `Runtime role`: vector store for retrieval
- `Primary env`: `QDRANT_URL`, `QDRANT_COLLECTION`, `QDRANT_VECTOR_SIZE`, `QDRANT_DISTANCE`
- `Current default collection`: `openshift_docs`
- `Current expected vector size`: `1024`
- `Code`: [`src/ocp_rag_part1/qdrant_store.py`](/Users/kugnus/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-v2/src/ocp_rag_part1/qdrant_store.py)
- `Do not assume`: collection recreation is safe in a shared environment

## Embeddings

- `Last checked`: 2026-04-07
- `Default model`: `dragonkue/bge-m3-ko`
- `Primary env`: `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`, `EMBEDDING_API_KEY`
- `Current implementation note`:
  - single-query chat embeddings prefer current configured path first
  - remote embedding이 가능하면 사용
  - remote가 불안정하면 fallback 여부를 코드 기준으로 점검
- `Code`: [`src/ocp_rag_part1/embedding.py`](/Users/kugnus/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-v2/src/ocp_rag_part1/embedding.py), [`src/ocp_rag_part1/sentence_model.py`](/Users/kugnus/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-v2/src/ocp_rag_part1/sentence_model.py)
- `Do not assume`: remote embedding service is always available

## LLM Endpoint

- `Last checked`: 2026-04-07
- `Runtime contract`: OpenAI-compatible chat/completions-style endpoint
- `Primary env`: `LLM_ENDPOINT`, `LLM_API_KEY`, `LLM_MODEL`
- `Current product assumption`: 사내 Qwen 계열 endpoint 전제
- `Code`: [`src/ocp_rag_part3/llm.py`](/Users/kugnus/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-v2/src/ocp_rag_part3/llm.py)
- `Do not hardcode`: vendor base URL, auth header shape, model name
- `Do not assume`: Windows laptop과 Mac mini가 같은 endpoint를 쓴다고 가정하지 말 것

## Optional Evaluation Stack

- `Last checked`: 2026-04-07
- `Optional deps`: `ragas`, `datasets`
- `Role`: evaluation only
- `Not required for`: normal chatbot runtime
- `Do not assume`: eval extras가 모든 환경에 설치되어 있지 않음

## Local Artifacts

- `Last checked`: 2026-04-07
- `Primary env`: `ARTIFACTS_DIR`
- `Default location`: repo-root [`artifacts`](/Users/kugnus/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-v2/artifacts)
- `Rule`: `.env` artifact path를 source of truth로 본다
- `Do not assume`: 언제나 repo-root `artifacts/`가 canonical store는 아님

## Current UI Config Split

- `Last checked`: 2026-04-07
- `Current file`: [`src/ocp_rag_part4/static/assets/app-config.js`](/Users/kugnus/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-v2/src/ocp_rag_part4/static/assets/app-config.js)
- `Role`: 코어 버전 선택값, empty-state 질문 예시 같은 presentation config를 HTML 본문에서 분리
- `Do not assume`: 이 파일 하나로 모든 UI hardcoding 문제가 해결된 것은 아님

## 마지막 원칙

- vendor 전제는 코드보다 이 파일에서 먼저 설명 가능해야 한다
- 설명이 길어질 정도로 vendor 종속이 커지면 구조 분리가 필요하다
