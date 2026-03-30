# First Presentation Feedback Response Plan

## Purpose

This document translates the first presentation feedback into explicit v2 design responses.

The feedback items were:

1. insufficient collection of official OpenShift material
2. weak chunking strategy
3. no demonstrated vector retrieval validation
4. weak multi-turn behavior

The goal is to make each item:

- visible in the design
- owned by a role
- measurable before expansion

## Response matrix

| Feedback item | v2 design response | Primary artifacts | Exit evidence |
| --- | --- | --- | --- |
| Official OpenShift data collection is insufficient | Treat `openshift-docs` as the official source of truth, document validation slice vs first operational release scope, and keep product-family exclusions explicit | `docs/v2/source-scope.md`, `configs/source-manifest.yaml`, `ingest/normalize_openshift_docs.py` | The corpus boundary is fixed, reproducible, and free of known non-OCP contamination |
| Chunking strategy is weak | Add section-aware chunking rules tied to the canonical document model and the HTML citation view | `docs/v2/architecture-blueprint.md`, `configs/metadata-schema.yaml` | Chunk units, overlap, and citation alignment rules are defined before implementation |
| Vector retrieval quality is not validated | Add a retrieval benchmark with query classes, top-k hit metrics, citation correctness, rerank deltas, and a context-retention harness that shows where evidence was lost | `docs/v2/evaluation-spec.md`, `docs/v2/context-retention-harness.md`, `docs/v2/requirements-traceability.md` | Retrieval quality is measured on a fixed baseline dataset and failing cases can be localized to a pipeline stage |
| Multi-turn capability is weak | Add explicit session memory, follow-up rewrite, citation continuity, 5+ turn evaluation scenarios, and trace hooks for version drift and follow-up rewrite failure | `docs/v2/architecture-blueprint.md`, `docs/v2/evaluation-spec.md`, `docs/v2/context-retention-harness.md`, `docs/v2/requirements-traceability.md` | Multi-turn behavior is tested and remains grounded across at least 5 turns |

## Concrete design upgrades

### 1. Official data collection

The design now distinguishes between:

- the smallest validated ingest slice
- the first operator-facing release scope
- later expansion scope

This prevents confusion between "what we can validate now" and "what the product must eventually cover."

### 2. Chunking strategy

The design must define:

- default chunk unit: section or subsection
- procedural chunking: keep ordered steps intact
- code chunking: separate fenced code from prose while keeping nearby explanatory text
- overlap policy for long sections
- metadata required for citation alignment

Chunking must be driven from the canonical document model, not from raw text slicing.

### 3. Retrieval benchmark

The benchmark must include:

- query classes by operational intent
- vector retrieval hit rates
- source directory hit rates
- citation correctness
- rerank before and after comparison

This is the minimum proof that retrieval quality is improving, not just changing.

### 4. Multi-turn behavior

The design must define:

- session memory scope
- follow-up query rewriting
- version continuity
- citation continuity
- memory reset boundaries

The goal is not "chatty conversation" but grounded operational continuity.

## Required benchmark categories

The baseline benchmark should include at least:

1. install and prerequisite questions
2. update and upgrade questions
3. disconnected environment questions
4. networking and node health questions
5. troubleshooting and recovery questions
6. citation click-through checks
7. multi-turn follow-up chains

## Release gating rule

We must not widen corpus scope beyond the current validation slice until all of the following are true:

1. official-source boundary is stable
2. chunking rules are fixed
3. retrieval benchmark exists and passes the initial gate
4. multi-turn baseline scenarios remain grounded
5. citations open a real HTML document target

## Immediate next implementation order

1. formalize chunking contract
2. formalize retrieval benchmark metrics
3. add the context-retention harness
4. formalize multi-turn memory and rewrite rules
5. validate OpenDocuments against the normalized validation slice
6. build the first benchmark dataset
