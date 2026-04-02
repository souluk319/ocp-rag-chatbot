# CURRENT_PHASE.md

## Current Focus

The project is currently in **Part 1: preprocessing pipeline**.

This phase is about building the document foundation first.

Primary scope:
- collect Korean OCP 4.20 documents
- normalize and parse collected documents
- preserve metadata needed for later citations
- test chunking strategy on a smaller high-value subset
- generate embeddings
- store vector and BM25-ready artifacts

This phase does **not** require:
- full chatbot UX
- final multi-turn runtime
- OpenDocuments integration
- release-grade answer generation
- full production deployment

If there is a conflict between future architecture work and preprocessing work, prefer preprocessing work.

## Source Rules

For the current phase, use these source rules:

1. Primary user-facing corpus source:
   - official Korean OpenShift Container Platform 4.20 documentation
   - `html-single` pages

2. Runtime target:
   - internal mirrored corpus for closed-network use
   - no live internet dependency at runtime

3. Optional later validation source:
   - English upstream docs may be used later for cross-checking
   - they are not required for the current milestone

4. PDFs are not the default corpus source.

## Deliverables

Part 1 should produce inspectable artifacts.

Minimum expected outputs:
- raw HTML snapshots
- normalized document records
- chunk records with metadata
- vector store contents
- BM25-ready searchable corpus
- preprocessing logs

Recommended artifact layout:
- `raw_html/`
- `normalized_docs.jsonl`
- `chunks.jsonl`
- `bm25_corpus.jsonl`
- `preprocessing_log.json`

Each chunk should preserve enough metadata to support later citation rendering.

Minimum chunk metadata:
- `chunk_id`
- `book_slug`
- `chapter`
- `section`
- `anchor`
- `source_url`
- `viewer_path`
- `text`

## Retrieval and Chunking Principles

- Collect the full Korean `html-single` corpus first.
- Do not immediately expose the full corpus to active experiments.
- Establish chunking and retrieval behavior on a smaller high-value subset first.
- After chunking strategy becomes stable, expand embedding and indexing to the full corpus.
- Avoid designs that require full re-embedding on every chunking change.
- Prefer incremental reprocessing using stable chunk identifiers and content hashes.

## Prototype Quality Rules

During this phase:
- retrieval quality and answer quality must be evaluated separately
- retrieval success must not be inferred from answer fluency
- citations must remain traceable to the right Korean source section
- visible failure cases should be recorded instead of ignored

## Error And Warning Rules

- Do not ignore error or warning logs.
- When a warning appears, explicitly classify it as either:
  - `continue_possible`: non-fatal but must be tracked
  - `fix_now`: pipeline risk that must be corrected before trusting outputs
- Treat these as pipeline issues first, not prompt issues:
  - version mismatch
  - token overflow / overlength inputs
  - contract or schema violations
- When proposing a fix, always report:
  - current value
  - changed value
  - verification criteria
- Do not summarize a warning away without tracing where it occurred in the pipeline.

## Immediate Principle

Build the foundation for a closed-network Korean OCP RAG system.
Do not expand scope before the document pipeline is stable.
