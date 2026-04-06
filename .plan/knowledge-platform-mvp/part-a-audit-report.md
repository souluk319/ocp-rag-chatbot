# Part A Audit Report

## 1. Decision

Current judgment:

- `study-grade source viewer for MVP`: `yes`
- `full release-grade source-view architecture`: `partial`

Reason:

- the current OCP 4.20 dataset is not chunk-only
- the repo already has a readable section-level source representation
- the app already has a server-side source viewer that can render those sections
- the MVP does not need an ingestion rebuild

The current gap is not "missing source data".
The current gap is "using the right existing layer consistently and proving it with tests".

## 2. Real Data Representations

Resolved current artifact root from `.env`:

- `ARTIFACTS_DIR = C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data`

Current artifact forms confirmed from real files:

1. Raw source HTML
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data\part1\raw_html\*.html`
- full `html-single` chapter pages collected from OCP 4.20 docs

2. Normalized section-level documents
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data\part1\normalized_docs.jsonl`
- readable source-view backing layer

3. Retrieval chunks
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data\part1\chunks.jsonl`

4. Lexical retrieval corpus
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data\part1\bm25_corpus.jsonl`

5. Retrieval and answer logs
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data\part2\retrieval_eval_report.json`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data\part3\answer_log.jsonl`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-data\part3\runtime_endpoint_report.json`

6. Source manifest
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\manifests\ocp_ko_4_20_html_single.json`

Manifest count confirmed:

- `113` source entries

## 3. Retrieval Text vs Source-View Text

Judgment:

- `already partially separated`

What is retrieval-friendly text:

- `chunks.jsonl`
- `bm25_corpus.jsonl`
- Qdrant payload derived from chunk records

What is source-view text:

- `normalized_docs.jsonl`
- raw fallback HTML in `raw_html`

Why this matters:

- retrieval chunks are optimized for search recall and prompt assembly
- normalized sections preserve enough structure for human reading

This separation already exists in code:

- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\ingest\normalize.py`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\ingest\chunking.py`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\app\server.py`

Important nuance:

- answer citations currently carry chunk-oriented excerpt text
- readable source viewing is produced by resolving `viewer_path` back into normalized sections
- this means citation payload alone is not the full study view
- but the study view can already be derived from existing artifacts without rebuilding ingestion

## 4. Confirmed Metadata Inventory

### 4.1 Manifest Metadata

Confirmed keys in manifest entries:

- `book_slug`
- `title`
- `source_url`
- `viewer_path`
- `high_value`

Related source-governance fields also exist in ingest models:

- `vendor_title`
- `content_status`
- `citation_eligible`
- `citation_block_reason`
- `viewer_strategy`
- `body_language_guess`
- `hangul_section_ratio`
- `hangul_chunk_ratio`
- `approval_status`
- `approval_notes`

### 4.2 Normalized Section Metadata

Confirmed keys in `normalized_docs.jsonl`:

- `book_slug`
- `book_title`
- `heading`
- `section_level`
- `section_path`
- `anchor`
- `source_url`
- `viewer_path`
- `text`

### 4.3 Retrieval Chunk Metadata

Confirmed keys in `chunks.jsonl`:

- `chunk_id`
- `book_slug`
- `book_title`
- `chapter`
- `section`
- `anchor`
- `source_url`
- `viewer_path`
- `text`
- `token_count`
- `ordinal`

Confirmed keys in `bm25_corpus.jsonl`:

- `chunk_id`
- `book_slug`
- `chapter`
- `section`
- `anchor`
- `source_url`
- `viewer_path`
- `text`

### 4.4 Retrieval Result Metadata

From retrieval models:

- `chunk_id`
- `book_slug`
- `chapter`
- `section`
- `anchor`
- `source_url`
- `viewer_path`
- `text`
- `source`
- `raw_score`
- `fused_score`
- `component_scores`

### 4.5 Answer Citation Metadata

From answer models and `answer_log.jsonl`:

- `index`
- `chunk_id`
- `book_slug`
- `section`
- `anchor`
- `source_url`
- `viewer_path`
- `excerpt`
- `origin`

Current implication:

- source tags can be built immediately from current citation payload
- right-panel document opening can be keyed by `viewer_path`
- section-level breadcrumb rendering must still resolve through normalized section data

## 5. Preprocessing Damage Assessment

Judgment:

- `optimized for retrieval, but not destructively enough to block human-readable viewing`

Observed preservation:

- headings: preserved
- section path: preserved
- anchors: preserved
- code blocks: preserved as `[CODE] ... [/CODE]`
- tables: preserved as `[TABLE] ... [/TABLE]`
- list-like structure: partially preserved in text flow

Evidence from code:

- headings are rewritten with anchor-aware markers in `normalize.py`
- normalized rows keep `heading`, `section_level`, `section_path`, `anchor`
- code and table blocks are preserved instead of discarded
- chunking is section-aware and conservative around blocks

Evidence from sampled artifact rows:

- sampled `5000` normalized rows
- level distribution:
  - `2: 139`
  - `3: 952`
  - `4: 2203`
  - `5: 1652`
  - `6: 54`
- rows containing code blocks: `2122`
- rows containing tables: `486`
- list-like rows: `654`

Conclusion:

- enough structure survived to support a study panel
- this is not a raw chunk dump situation
- for MVP, current normalized sections are good enough

## 6. Existing Source Viewer Support

The repo already contains a usable source-view path.

Backend evidence:

- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\app\server.py`

What already exists there:

- `viewer_path -> local raw html` resolution
- normalized section loading grouped by `book_slug`
- internal viewer HTML renderer
- target anchor highlighting
- paragraph rendering
- code block rendering
- table rendering
- source URL exposure

Runtime spot check:

- `_internal_viewer_html(...)` returned valid HTML for a real viewer path
- rendered output length was `1395964`
- rendered HTML contained `section-card`
- rendered HTML contained `code-block`

Decision:

- a right-side readable study panel is already technically possible with current data

## 7. Current Frontend State

Current UI judgment:

- `chatbot-first layout already exists`
- `source-study side panel already exists`
- `trace prominence is still high and should be toned for MVP`

Confirmed current behavior from:

- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\app\static\index.html`

Observed structure:

- main workspace is `chat panel + side panel`
- side panel is hidden by default
- default inspector tab is `Sources`
- source tags are rendered under assistant answers
- clicking source tags or citation cards opens the right-side document viewer

Important product implication:

- Part B should refine this chat-first pattern
- Part B should not redesign the product into a document-first workspace

## 8. Runtime Caveat Found During Audit

Current caveat:

- vector retrieval endpoint failure was observed during audit runs

Observed warning:

- `vector search failed: Failed to fetch embeddings from http://100.99.152.52:8091/v1 using model 'dragonkue/bge-m3-ko'`

Impact:

- some queries still returned grounded citations through remaining retrieval path
- some queries returned `rag` answers with `0` citations

Interpretation:

- this does **not** invalidate the data-layer audit
- it **does** matter for demo reliability and Part C validation

Action implication:

- Part B should not assume vector retrieval is always healthy
- Part C must explicitly validate grounded answers with real queries

## 9. Smallest Useful Data-Layer Change

MVP decision:

- `no ingestion rebuild required`
- `no multi-format ingestion work required`
- `no document-book platform layer required for this slice`

Smallest useful change for MVP:

1. Treat `normalized_docs.jsonl` as the canonical source-view backing model.
2. Keep citations chunk-based for retrieval grounding.
3. Resolve right-panel source viewing from `citation.viewer_path`.
4. Use normalized section metadata to render readable document sections and anchor focus.

This means:

- source tags under answers: already supported
- right-side source panel: already technically supported
- section jump/highlight: already technically supported through `viewer_path#anchor`
- readable study panel: already supported through normalized section rendering

Optional thin follow-up layer for later:

- a dedicated `viewer_index.jsonl` or similar derived artifact
- useful for release hardening, source policy metadata, and faster viewer lookup
- not required for tomorrow-morning MVP

## 10. AGENTS Cross-Check Summary

### Atlas

- use the existing layer split
- keep the product chatbot-first
- treat this as data/view-model integration, not a broad UI rewrite

### Runbook

- raw retrieval chunks are not good enough for learning or operations
- users need section-level readable source with context, not excerpt fragments

### Sieve

- retrieval text and source-view text are already partially separated
- current normalized sections are enough for MVP
- a dedicated viewer artifact is optional hardening, not a prerequisite

### Echo

- source panel does not conflict with multi-turn memory
- selected citation/source can later be tied to current citation group memory

### Console

- current app can stay chat-first
- right panel should stay secondary and user-invoked

### RedPen

- tests must prove real artifact-backed source viewing
- tests must prove the UI remains chatbot-first in behavior, not only in markup

## 11. Part B Guardrails

Part B implementation must follow these rules:

1. Keep the current RAG flow working.
2. Keep chat as the primary desktop surface.
3. Do not show raw chunk text as the study panel body.
4. Use citation payload for source tags.
5. Use normalized sections for readable source viewing.
6. Keep the right-side study panel collapsible.
7. Reduce debug/trace dominance in the main experience.

## 12. Final Recommendation

Proceed to Part B with a minimal MVP scope.

Recommended implementation path:

1. keep current chat-first layout
2. improve answer readability and source-tag styling
3. keep source tags directly under each answer
4. open source documents in the right-side panel using current `viewer_path`
5. make the document panel feel like a study panel, not a debug iframe dump
6. add tests proving real citation -> readable source-view behavior

This is the smallest useful path that:

- preserves the current RAG system
- fits the clarified NotebookLM-like direction
- avoids another architecture detour
