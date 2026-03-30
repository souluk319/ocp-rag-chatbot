# v2 Requirements Traceability

## Purpose

This document ties together the three inputs that define v2:

1. the OpenDocuments PRD and product direction
2. the `openshift-docs` official source model
3. our project-specific acceptance criteria for the OCP operations assistant

The goal is to make it obvious which requirements are already defined, which are still pending implementation, and which artifact owns each decision.

## Authoritative inputs

- OpenDocuments reference PRD: `C:\Users\soulu\cywell\ocp-rag-v2\OpenDocuments\PRD.md`
- official source repository: `C:\Users\soulu\cywell\openshift-docs`
- main product design: `C:\Users\soulu\cywell\ocp-rag-chatbot\docs\v2\architecture-blueprint.md`

## Traceability matrix

| Requirement axis | Why it matters | Primary design owner | Current artifact | Current status | Exit evidence |
| --- | --- | --- | --- | --- | --- |
| OpenDocuments-style RAG flow | We need one shared mental model for ingest to answer generation | Lead Architect / PM | `docs/v2/architecture-blueprint.md` | defined | Flow remains consistent across ingest, retrieval, generation, and citation |
| Official OCP source of truth | Grounding quality depends on trustworthy source material | Data / Document Onboarding Engineer | `docs/v2/source-scope.md`, `configs/source-manifest.yaml` | defined | Source boundary is fixed and reproducible |
| `.adoc` normalization | `openshift-docs` is not directly ready for indexing | Data / Document Onboarding Engineer | `ingest/normalize_openshift_docs.py` | implemented first pass | Normalized corpus and manifest can be regenerated from source |
| Mixed-product exclusion | OSD, ROSA, and other product lines must not contaminate answers | Data / Document Onboarding Engineer | `docs/v2/source-scope.md`, `configs/source-manifest.yaml` | defined and validated for P0 | Filtered corpus excludes known non-OCP paths |
| Stable metadata contract | Retrieval, ranking, and citation all depend on stable metadata | RAG / Search Engineer | `configs/metadata-schema.yaml` | defined | Each normalized document has the required fields |
| HTML citation view generation | Source click-through must open a readable document, not raw source text | UI / UX Engineer | `docs/v2/architecture-blueprint.md` | defined | Each indexed document can resolve to an internal HTML citation target |
| Section-aware chunking | Answers and citations must point to meaningful sections, not arbitrary text blobs | RAG / Search Engineer | `docs/v2/architecture-blueprint.md`, `docs/v2/chunking-contract.md`, `configs/chunk-schema.yaml` | defined | Chunks preserve heading hierarchy, type, and section identity |
| Hybrid retrieval and reranking | OpenDocuments PRD expects retrieval quality beyond naive vector lookup | RAG / Search Engineer | `docs/v2/architecture-blueprint.md`, `configs/rag-policy.yaml` | planned | Relevant chunks rank ahead of weak lexical or noisy matches |
| Context-retention harness | We need to localize context loss before Stage 5 benchmark failures become opaque | QA / Evaluation / Red Team | `docs/v2/context-retention-harness.md`, `eval/context-harness-schema.yaml`, `eval/context_harness_report.py` | defined | A failing turn can be classified as retrieval miss, rerank loss, assembly loss, citation loss, or version drift |
| Retrieval benchmark and rerank validation | Feedback requires proof that vector retrieval quality is measured, not assumed | QA / Evaluation / Red Team | `docs/v2/evaluation-spec.md` | planned next | Top-k, source-dir, citation, and rerank metrics are tracked on a fixed dataset |
| Korean answer policy | Users will ask in Korean while official documents stay mostly English | LLM Serving / Backend Engineer | `configs/rag-policy.yaml` | defined | Korean answers remain grounded and preserve technical terms correctly |
| Citation rendering | Answers must always disclose evidence | RAG / Search Engineer | `configs/rag-policy.yaml`, `docs/v2/architecture-blueprint.md` | defined | Every answer includes source references |
| Citation click-through | Clicking a citation must open a real readable document | UI / UX Engineer | `docs/v2/architecture-blueprint.md` | planned | A cited source opens a human-readable document or section |
| Multi-turn memory and follow-up rewrite | Feedback requires grounded continuity across more than one turn | LLM Serving / Backend Engineer | `docs/v2/architecture-blueprint.md`, `docs/v2/evaluation-spec.md` | planned next | Session memory, rewrite rules, and 5-turn scenarios are defined and tested |
| Company-approved model usage | The runtime must not drift to local or public providers | LLM Serving / Backend Engineer | `.env`, future runtime config under `app/` | partially defined | Runtime only uses the approved company endpoint |
| Streaming response | OpenDocuments behavior and user experience expect streaming output | LLM Serving / Backend Engineer | `docs/v2/architecture-blueprint.md` | planned | Chat answers stream to the client in chunks |
| Air-gapped update loop | The system must survive document refreshes in a closed network | OCP / Air-gapped Infrastructure Engineer | `deployment/airgap-flow.md`, `deployment/bundle-schema.yaml` | defined | Approved bundle import and rollback are documented and repeatable |
| Evaluation and red-team | We need measurable acceptance, not intuition | QA / Evaluation / Red Team | `docs/v2/evaluation-spec.md` | defined | Baseline dataset and pass criteria exist |
| OCP operations usefulness | The product must solve real install, upgrade, and troubleshooting questions | OCP Operations SME | `docs/v2/evaluation-spec.md` | defined | Scenario coverage includes install, update, disconnected, and troubleshooting |
| Multi-repo workspace discipline | The product repo, OpenDocuments, and openshift-docs must evolve together without mixing Git histories | Lead Architect / PM | `docs/v2/workspace-guide.md` | defined | Team members can work across the three repositories without ownership confusion |

## What is already closed

- source repository choice
- initial source boundary policy
- metadata contract
- answer grounding policy
- air-gap bundle direction

## What still needs implementation

- section-aware chunk generation
- context-retention harness traces and diagnostics
- retrieval benchmark dataset and metrics
- viewer-friendly HTML output with stable `viewer_url`
- OpenDocuments ingestion validation using the normalized P0 corpus
- evaluation dataset assets under `eval/`
- multi-turn memory rules and follow-up rewrite logic
- company-endpoint runtime wiring for the integrated chatbot path

## Interpretation rule

When there is ambiguity between "build it ourselves" and "align with OpenDocuments", v2 follows this rule:

- we directly implement the OCP-specific critical path
- we align the RAG flow and product behavior to the OpenDocuments reference model

This is the controlling interpretation for the project unless a newer written direction replaces it.
