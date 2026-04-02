# PART1_PLAN.md

## Goal

Build the preprocessing pipeline that turns Korean OCP 4.20 `html-single` documents into inspectable retrieval assets.

## Inputs

- official Korean OpenShift Container Platform 4.20 documentation
- `html-single` pages
- embedding endpoint
- local Qdrant instance

## Outputs

- raw HTML snapshots
- normalized docs
- chunk records
- Qdrant vectors
- BM25-ready corpus
- preprocessing log

## Steps

### Step 1. Define source manifest

- build the list of Korean OCP 4.20 `html-single` URLs
- assign stable `book_slug` values
- mark high-value subset for early chunking tests

### Step 2. Implement raw collector

- fetch each source URL with retry logic
- save raw HTML snapshots
- record fetch status, timestamp, and source URL

### Step 3. Implement article extraction

- remove navigation and site chrome
- preserve meaningful body structure
- preserve headings, anchors, code blocks, and tables as much as practical

### Step 4. Implement normalization

- normalize whitespace and HTML entities
- keep code blocks readable
- convert tables into consistent text form
- store normalized records in a stable schema

### Step 5. Define metadata schema

Each normalized record and chunk should preserve:

- `book_slug`
- `chapter`
- `section`
- `anchor`
- `source_url`
- `viewer_path`
- `text`

### Step 6. Build high-value subset

- select core operational and educational documents
- use this subset for chunking experiments before full expansion

### Step 7. Implement chunking experiment harness

- split by document structure first
- apply token-based fallback splitting only when needed
- avoid cutting code blocks in unstable ways
- compare chunk outputs on the high-value subset

### Step 8. Connect embedding endpoint

- define embedding client settings
- batch chunk embedding requests
- log failures and retry behavior

### Step 9. Store vectors in Qdrant

- define collection schema
- upsert chunk vectors with metadata payloads
- keep chunk IDs stable across reruns when possible

### Step 10. Export BM25-ready corpus

- save searchable text artifacts with metadata
- do not store text-only lists without identity mapping

### Step 11. Add preprocessing logging

- save source-level fetch results
- save normalization counts
- save chunk counts
- save embedding and Qdrant write results
- record failures explicitly

### Step 12. Validate Part 1 outputs

- verify raw HTML exists
- verify normalized docs are inspectable
- verify chunk metadata is complete
- verify Qdrant collection is populated
- verify BM25 corpus maps back to chunk IDs and sources

## Exit Criteria

Part 1 is ready when:

- the Korean corpus is collectible and reproducible
- normalized documents are inspectable
- chunk metadata supports later citations
- embeddings are generated successfully
- Qdrant and BM25 artifacts are usable by the next stage

## Notes

- Start with full collection, but test chunking on a smaller high-value subset first.
- Avoid designs that require full re-embedding on every chunking change.
