# VENDOR_NOTES.md

## Purpose

This file records vendor-specific API and dependency notes that should not live in `AGENTS.md`.

Keep entries short and date-stamped.

## Red Hat OCP Docs

- `Last checked`: 2026-04-06
- `Primary source`: OCP 4.20 Korean official documentation
- `Current collection shape`: html-single source pages normalized into section-aware records
- `Viewer path template`: `/docs/ocp/4.20/ko/{slug}/index.html`
- `Do not assume`: future versions or non-OCP corpora are available unless they are explicitly ingested

## Qdrant

- `Last checked`: 2026-04-06
- `Runtime role`: vector store for retrieval
- `Primary env`: `QDRANT_URL`, `QDRANT_COLLECTION`, `QDRANT_VECTOR_SIZE`, `QDRANT_DISTANCE`
- `Current default collection`: `openshift_docs`
- `Current expected vector size`: `1024`
- `Do not assume`: collection recreation is safe in a shared environment

## Embeddings

- `Last checked`: 2026-04-06
- `Default model`: `dragonkue/bge-m3-ko`
- `Primary env`: `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`, `EMBEDDING_API_KEY`
- `Current implementation note`:
  - single-query chat embeddings prefer local model loading first
  - if remote embedding is configured and available, it can still be used
  - if remote embedding is unavailable, local fallback is used
- `Do not assume`: remote embedding service is always available

## LLM Endpoint

- `Last checked`: 2026-04-06
- `Runtime contract`: OpenAI-compatible chat/completions-style endpoint
- `Primary env`: `LLM_ENDPOINT`, `LLM_API_KEY`, `LLM_MODEL`
- `Do not hardcode`: vendor base URL, auth header shape, or model name in product logic
- `Do not assume`: the same endpoint is used across Windows laptop and Mac mini

## Optional Evaluation Stack

- `Last checked`: 2026-04-06
- `Optional deps`: `ragas`, `datasets`, `openai`, `langchain-openai`
- `Role`: evaluation only
- `Not required for`: normal chatbot runtime
- `Do not assume`: eval extras are installed in every environment

## Local Artifacts

- `Last checked`: 2026-04-06
- `Primary env`: `ARTIFACTS_DIR`
- `Rule`: treat `.env` artifact paths as the source of truth
- `Do not assume`: repo-root `artifacts/` is the canonical store
