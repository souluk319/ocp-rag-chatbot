# OCP Operations Assistant v2 Architecture Blueprint

## 1. Purpose

This document defines the shared design direction for the v2 rewrite.

It resolves the current ambiguity between:

- the original assignment, which emphasized direct implementation of core logic
- the later direction to align RAG with the OpenDocuments project

## 2. Design Interpretation

We will treat **OpenDocuments as the reference architecture for RAG flow and product behavior**, not as a black-box shortcut that replaces understanding.

Our implementation rule is:

- follow the **OpenDocuments-style pipeline**
  - ingest
  - parse or normalize
  - chunk
  - embed
  - retrieve
  - rerank
  - generate
  - cite
- directly own the **OCP-specific critical path**
  - document collection scope
  - `.adoc` normalization
  - metadata contract
  - citation-to-document linking
  - Korean answer policy
  - version-aware source preference
  - closed-network bundle flow

In short:

**OpenDocuments gives the architectural target. Our repository owns the OCP implementation and operating model.**

## 3. Product Goal

Build a closed-network OCP operations assistant that:

- uses official OCP documentation as the main source of truth
- answers in Korean
- always shows citations
- opens the cited document when a source is clicked
- supports controlled document updates for an air-gapped environment

## 4. Repository Roles

### Main product repository

- `C:\Users\soulu\cywell\ocp-rag-chatbot`
- owns manifests, normalization, deployment rules, evaluation, and OCP-specific behavior

### RAG platform reference

- `C:\Users\soulu\cywell\ocp-rag-v2\OpenDocuments`
- used as the baseline for RAG flow, CLI flow, server flow, and expected product behavior

### Official document source

- `C:\Users\soulu\cywell\openshift-docs`
- primary source of official OCP content

## 5. Non-Goals for Phase 1

- full UI redesign
- indexing the entire `openshift-docs` repository at once
- immediate deep modification of OpenDocuments internals
- full automation before one manual end-to-end document update pass succeeds

## 6. Core Requirements We Must Satisfy

### A. Data accuracy

- use official OCP source material
- preserve source path and document lineage
- avoid mixing OSD, ROSA, MicroShift, and unrelated product lines in the first pass

### B. Citation accuracy

- every answer must include source references
- every source reference must map back to a real document
- clicking a source must open a human-readable document view, not just a raw chunk id
- source tracking must be stable at least at the section level

### C. Korean answer quality

- retrieval can use English source content
- final answers should be in Korean
- commands, API names, resource names, and proper nouns should stay in original form when needed
- the system must avoid unsupported guesses when grounding is weak

### D. Closed-network operation

- no direct external sync inside the target environment
- document updates must move through approved bundles
- index activation must be versioned and reversible

## 7. Reference RAG Flow

The v2 chatbot will follow this logical flow:

1. Source collection
2. Parse and normalize `.adoc` into a canonical document model
3. Generate two synchronized outputs from the same canonical model
4. Section-aware chunking for retrieval
5. Embedding
6. Retrieval
7. Reranking
8. Context assembly
9. LLM generation
10. Citation rendering
11. Citation click-through to a document view

### 7.1 Source pipeline branching

The normalization stage must not produce only search text.

It must produce a shared intermediate document structure first, then branch into two outputs:

1. a retrieval-oriented representation
2. a citation-oriented document view

The required shape is:

1. `.adoc` source collection
2. AsciiDoc parsing and cleanup
3. canonical document model with section hierarchy
4. retrieval output generation
   - normalized text or markdown
   - chunk-ready section boundaries
   - section metadata
5. citation output generation
   - internal HTML document view
   - section anchors
   - stable `viewer_url`
6. metadata manifest emission

This design keeps retrieval chunks and citation targets aligned to the same source structure.

### 7.2 Chunking contract

Chunking must be explicit in the design, not left to an implicit library default.

The default rules are:

- primary chunk unit is the section or subsection under one heading path
- narrative chunks should target `350-650` tokens
- soft overlap of `60-100` tokens is allowed only for long narrative sections
- chunk boundaries must respect heading hierarchy
- ordered procedures should stay intact whenever possible
- code blocks should become their own chunk type but keep the nearest heading and short explanatory context
- a chunk must not cross unrelated sections just to satisfy a size target
- every chunk must map back to one `document_id`, one section identity, and one citation target

The first chunking contract should include:

- chunk types such as `prose`, `procedure`, `code`, and `reference`
- required metadata such as `section_title`, `heading_hierarchy`, `position`, and `viewer_url`

This is the minimum design bar for saying the chunking plan is no longer underspecified.

### 7.3 Retrieval benchmark requirements

The design must not rely on answer fluency alone to claim retrieval quality.

The first benchmark contract should record:

- top-k hit rate against expected supporting documents
- expected source-directory hit rate
- version-match rate for version-sensitive questions
- citation correctness on grounded answers
- rerank delta between pre-rerank and post-rerank ordering
- query classes such as install, update, troubleshooting, disconnected, and follow-up queries

### 7.3.1 Context-retention harness

Before we treat benchmark failures as retrieval failures, we need one diagnostic layer that traces where expected evidence disappears.

The harness must record:

- the user turn and rewritten retrieval query
- retrieval candidates
- reranked candidates
- final assembled prompt context
- dropped chunks and the reason they were dropped
- citations emitted for the answer
- version context before and after the turn

This harness exists to separate:

- retrieval miss
- rerank loss
- assembly loss
- citation loss
- truncation pressure
- version drift on follow-up turns

The first implementation does not need deep UI.

It does need a stable trace record and a repeatable reporter.

### 7.4 Multi-turn context flow

Multi-turn behavior is a product requirement, not a later enhancement.

The system should support grounded follow-up turns by:

1. storing a bounded session-local turn history
2. keeping structured memory for at least the last `5` turns
3. classifying each new turn as standalone or follow-up
4. rewriting referential follow-up turns into a standalone retrieval query when needed
5. preserving version context unless the user explicitly changes it
6. preserving citation continuity across related turns
7. warning or resetting context when the conversation shifts to a conflicting version or topic

The design goal is grounded continuity, not unrestricted memory growth.

The first implementation should prefer:

- a bounded session memory window
- explicit follow-up rewrite logic
- conservative behavior when the prior turn does not contain enough grounding

## 8. Why `.adoc` Matters

The `openshift-docs` repository stores the documentation source in AsciiDoc.

- `.adoc` is the official authoring source
- HTML and PDF are rendered delivery formats
- for accuracy and traceability, we should collect from the `.adoc` source

However:

- OpenDocuments does not cleanly ingest `openshift-docs` directly as-is
- phase 1 therefore requires our own normalization step before indexing

## 8.1 Official source trust rule

This repository is treated as an official source only when all of the following are true:

1. the repository is owned by the `openshift` organization
2. the repository README states that OpenShift documentation is sourced there
3. the repository README states that the published output is delivered through `docs.openshift.com`

Repository avatars or profile images are not used as a trust signal.

## 9. Phase 1 Source Boundary

### P0 initial include set

- `installing`
- `post_installation_configuration`
- `updating`
- `disconnected`
- `support`

### P1 immediate follow-up set

- `networking`
- `nodes`
- `operators`
- `storage`
- `security`
- `authentication`
- `observability`
- `backup_and_restore`
- `etcd`

### P2 later extension

- `release_notes`
- `cli_reference`
- `rest_api`

### Phase 1 exclusions

- `osd_*`
- `rosa_*`
- `microshift_*`
- `cloud_experts_*`
- `ocm`
- `hosted_control_planes`
- `lightspeed`
- `migration_toolkit_for_containers`
- `contributing_to_docs`
- `modules`
- `snippets`
- `_topic_maps`
- `_images`
- `_templates`
- `_attributes`
- `_stylesheets`
- `_javascripts`
- `_converters`
- `_gemfiles`

These exclusions must apply at two levels:

- top-level directories
- path fragments inside mixed directories such as `support`

## 10. Metadata Contract

Every normalized document must carry stable metadata.

Required fields:

- `document_id`
- `title`
- `source_id`
- `source_type`
- `source_url`
- `local_path`
- `normalized_path`
- `product`
- `version`
- `category`
- `language`
- `trust_level`
- `collected_at`
- `checksum`

Additional fields we should preserve when possible:

- `top_level_dir`
- `heading_hierarchy`
- `section_title`
- `viewer_url`

This metadata is the prerequisite for:

- source trust ordering
- version-aware ranking
- source click-through
- repeatable document update bundles

## 11. Citation and Document Viewing Design

This is a hard product requirement.

The chatbot must not stop at displaying a filename or a chunk id.

### Required citation behavior

- each cited chunk must point back to a document and section
- citations in the answer UI must be clickable
- clicking should open a readable document view in the target environment

### Design implication

We must produce two outputs from the source pipeline:

1. an **indexable normalized representation**
2. a **human-readable view representation**

For v2, the default citation view format should be:

- rendered internal HTML
- readable without exposing raw `.adoc`
- anchorable at the section level

Phase 1 minimum implementation target:

- normalized text for indexing
- rendered HTML documents for source viewing
- `viewer_url` stored in metadata
- section-level anchors when available

Non-goal for citation click-through:

- opening raw `.adoc` files as the user-facing citation target

## 12. Korean Quality Strategy

To improve Korean answer quality while using English source material:

1. keep official English content as the source of truth
2. retrieve from normalized official content
3. answer in Korean
4. preserve technical terms where translation would reduce precision
5. add OCP terminology rules and evaluation prompts

We should not start by translating the entire corpus.

## 13. Ownership Boundaries

### We own directly in `ocp-rag-chatbot`

- source manifests
- metadata schema
- normalization pipeline
- bundle schema and air-gap flow
- evaluation set
- citation viewer strategy
- OCP answer policies

### We treat as reference or validation baseline in `OpenDocuments`

- init or start model for local validation
- CLI and server request flow
- ingest to query control flow
- default web experience in phase 1

### We should avoid changing early

- advanced OpenDocuments web customization
- MCP or widget features
- deep retrieval internals before the normalized corpus is proven

## 14. Execution Order

1. lock the `openshift-docs` source boundary
2. finalize `configs/source-manifest.yaml`
3. finalize `configs/metadata-schema.yaml`
4. finalize `configs/rag-policy.yaml`
5. implement `.adoc` normalization into `data/normalized/`
6. emit stable manifests into `data/manifests/`
7. define bundle format for air-gap transfer
8. run a minimal OpenDocuments indexing and query validation on the normalized subset
9. define the first retrieval benchmark and evaluation questions
10. define multi-turn session and follow-up rewrite rules
11. add version-aware and source-aware retrieval improvements
12. build citation click-through behavior
13. automate the approved document update loop

## 15. Immediate Deliverables

These files define the first real baseline:

- `configs/source-manifest.yaml`
- `configs/metadata-schema.yaml`
- `configs/rag-policy.yaml`
- `deployment/airgap-flow.md`
- `deployment/bundle-schema.yaml`
- `ingest/normalize_openshift_docs.py`

## 16. Acceptance Criteria for the First Working Slice

The first slice is successful only if:

- selected `openshift-docs` directories can be normalized into indexable files
- manifest output is reproducible
- OpenDocuments can index the normalized subset
- chunk boundaries are section-aware and citation-safe
- Korean questions can be answered from that subset
- retrieval quality is measured on a fixed benchmark set
- 5-turn follow-up scenarios remain grounded
- answers include citations
- citations point to a real document path

If any of these fail, we are not ready to expand scope.
