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
2. Normalization from `.adoc` to indexable text or markdown
3. Section-aware chunking
4. Embedding
5. Retrieval
6. Reranking
7. Context assembly
8. LLM generation
9. Citation rendering
10. Citation click-through to a document view

## 8. Why `.adoc` Matters

The `openshift-docs` repository stores the documentation source in AsciiDoc.

- `.adoc` is the official authoring source
- HTML and PDF are rendered delivery formats
- for accuracy and traceability, we should collect from the `.adoc` source

However:

- OpenDocuments does not cleanly ingest `openshift-docs` directly as-is
- phase 1 therefore requires our own normalization step before indexing

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

For phase 1, the minimum acceptable approach is:

- normalized text for indexing
- a source viewer path or rendered document path stored in metadata

Longer-term preferred approach:

- render internal HTML views with section anchors

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
9. define the first evaluation questions
10. add version-aware and source-aware retrieval improvements
11. build citation click-through behavior
12. automate the approved document update loop

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
- Korean questions can be answered from that subset
- answers include citations
- citations point to a real document path

If any of these fail, we are not ready to expand scope.
