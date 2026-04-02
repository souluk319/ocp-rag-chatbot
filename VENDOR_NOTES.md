# VENDOR_NOTES.md

## Purpose

This file records vendor-specific notes, external endpoint assumptions, and source quirks that affect implementation.

## Last Checked

- 2026-04-02

## Corpus Source Notes

- Primary corpus target is Korean OCP 4.20 `html-single` pages from `docs.redhat.com`.
- Some pages in the Korean path currently contain English-heavy content or fallback behavior.
- High-value subset books currently flagged as low-Hangul in validation:
  - `backup_and_restore`
  - `installing_on_any_platform`
  - `machine_configuration`
  - `monitoring`

Implication:

- retrieval evaluation must keep these books visible as a source-quality risk
- Korean-first answer generation should not assume all Korean-path sources are fully localized

## Endpoint Notes

- Embeddings are requested from the remote `EMBEDDING_BASE_URL` endpoint
- Chunk sizing uses local `SentenceTransformer("dragonkue/bge-m3-ko")`
- The local model repository resolves in this environment and exposes an `XLMRobertaTokenizerFast` tokenizer
- Qdrant is local through `QDRANT_URL`
- LLM endpoint is configured through `LLM_ENDPOINT`
- Current Qwen/vLLM-style answer generation requires `reasoning=false` and `chat_template_kwargs.enable_thinking=false` to return final answer content reliably

These are currently build/runtime dependencies for experimentation.
Closed-network runtime should avoid any unnecessary live dependency beyond approved internal services.

## Artifact Path Notes

- Generated artifacts are now configurable through `ARTIFACTS_DIR`
- Raw HTML can also be split out through `RAW_HTML_DIR`
- Current local setup uses an external sibling artifact directory outside the repo

## Retrieval Notes

- `Legal Notice` chunks are filtered during normalization
- current Part 2 uses BM25 + vector + hybrid fusion with a small vector tie-break preference
- follow-up rewrite is intentionally minimal and inspectable
- First local model load downloads from Hugging Face cache, so air-gapped packaging will need the model pre-cached or vendored

## Update Guidance

When a vendor endpoint changes, or when Korean-path source behavior changes, update this file with:

- what changed
- why it matters
- the date it was re-checked
