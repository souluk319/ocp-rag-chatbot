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
| Version-selectable source profile layer | The pipeline must survive future branch pinning without structural rewrites | Data / Document Onboarding Engineer, Lead Architect / PM | `configs/source-profiles.yaml`, `configs/active-source-profile.yaml`, `docs/v2/source-profile-layer.md`, `docs/v2/stage13-source-profile-report.md`, `ingest/normalize_openshift_docs.py` | implemented for validation mode | Validation mode and future operator-release mode are both expressible as configuration and emitted lineage |
| `.adoc` normalization | `openshift-docs` is not directly ready for indexing | Data / Document Onboarding Engineer | `ingest/normalize_openshift_docs.py` | implemented first pass | Normalized corpus and manifest can be regenerated from source |
| Mixed-product exclusion | OSD, ROSA, and other product lines must not contaminate answers | Data / Document Onboarding Engineer | `docs/v2/source-scope.md`, `configs/source-manifest.yaml` | defined and validated for P0 | Filtered corpus excludes known non-OCP paths |
| Stable metadata contract | Retrieval, ranking, and citation all depend on stable metadata | RAG / Search Engineer | `configs/metadata-schema.yaml` | defined | Each normalized document has the required fields |
| HTML citation view generation | Source click-through must open a readable document, not raw source text | UI / UX Engineer | `docs/v2/architecture-blueprint.md`, `ingest/normalize_openshift_docs.py` | implemented for the validation slice | Each normalized document resolves to a generated internal HTML citation target |
| Section-aware chunking | Answers and citations must point to meaningful sections, not arbitrary text blobs | RAG / Search Engineer | `docs/v2/architecture-blueprint.md`, `docs/v2/chunking-contract.md`, `configs/chunk-schema.yaml` | defined | Chunks preserve heading hierarchy, type, and section identity |
| Hybrid retrieval and reranking | OpenDocuments PRD expects retrieval quality beyond naive vector lookup | RAG / Search Engineer | `docs/v2/architecture-blueprint.md`, `configs/rag-policy.yaml`, `app/ocp_policy.py`, `eval/stage9_policy_report.py` | implemented for Stage 9 baseline | Relevant chunks rank ahead of weak lexical or noisy matches on the fixed benchmark set |
| Context-retention harness | We need to localize context loss before Stage 5 benchmark failures become opaque | QA / Evaluation / Red Team | `docs/v2/context-retention-harness.md`, `eval/context-harness-schema.yaml`, `eval/context_harness_report.py`, `data/manifests/generated/stage10-suite-report.json` | implemented through Stage 10 evidence | A failing turn can be classified as retrieval miss, rerank loss, assembly loss, citation loss, or version drift |
| Retrieval benchmark and rerank validation | Feedback requires proof that vector retrieval quality is measured, not assumed | QA / Evaluation / Red Team | `docs/v2/evaluation-spec.md`, `docs/v2/retrieval-benchmark-plan.md`, `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`, `eval/retrieval_benchmark_report.py`, `data/manifests/generated/stage9-policy-report.json` | implemented with Stage 10 evaluation evidence | Top-k, source-dir, citation, and rerank metrics are tracked on a fixed dataset |
| Korean answer policy | Users will ask in Korean while official documents stay mostly English | LLM Serving / Backend Engineer | `configs/rag-policy.yaml`, `app/ocp_policy.py`, `docs/v2/ocp-policy-application.md` | implemented for Stage 9 baseline | Korean answer guardrails are explicit and preserve technical terms correctly |
| Citation rendering | Answers must always disclose evidence | RAG / Search Engineer | `configs/rag-policy.yaml`, `docs/v2/architecture-blueprint.md` | defined | Every answer includes source references |
| Citation click-through | Clicking a citation must open a real readable document | UI / UX Engineer | `docs/v2/architecture-blueprint.md`, `ingest/normalize_openshift_docs.py` | defined with generated HTML targets | A cited source resolves to a human-readable HTML document or section target |
| Multi-turn memory and follow-up rewrite | Feedback requires grounded continuity across more than one turn | LLM Serving / Backend Engineer | `docs/v2/multiturn-memory-plan.md`, `app/multiturn_memory.py`, `eval/benchmarks/p0_multiturn_scenarios.json`, `eval/multiturn_rewrite_report.py` | implemented for Stage 7 baseline | Session memory, rewrite rules, and 5-turn scenarios are defined and replayable |
| Company-approved model usage | The runtime must not drift to local or public providers | LLM Serving / Backend Engineer | `.env`, `app/runtime_config.py`, `app/opendocuments_openai_bridge.py`, `docs/v2/company-runtime-lock.md`, `deployment/check_runtime_contract.py` | implemented for Stage 8 baseline | Runtime only uses env-driven approved endpoint settings and local fallback is opt-in |
| Streaming response | OpenDocuments behavior and user experience expect streaming output | LLM Serving / Backend Engineer | `docs/v2/architecture-blueprint.md`, `app/opendocuments_openai_bridge.py`, `docs/v2/company-runtime-lock.md` | implemented in the bridge baseline | Chat answers stream through the approved bridge path in chunks |
| Live runtime memory + policy integration | Stage 7 and Stage 9 behavior must not remain offline-only | LLM Serving / Backend Engineer, RAG / Search Engineer | `app/ocp_runtime_gateway.py`, `app/runtime_gateway_support.py`, `app/runtime_source_index.py`, `app/opendocuments_openai_bridge.py`, `deployment/run_live_runtime_smoke.py`, `docs/v2/live-runtime-gateway.md`, `docs/v2/stage12-live-runtime-report.md`, `data/manifests/generated/stage12-live-runtime-report.json` | implemented and live-validated for the Stage 12 baseline | The live HTTP path rewrites follow-up queries, reranks sources against the active manifest, preserves session continuity, and serves clickable citation HTML through the gateway |
| Air-gapped update loop | The system must survive document refreshes in a closed network | OCP / Air-gapped Infrastructure Engineer | `deployment/airgap-flow.md`, `deployment/bundle-schema.yaml`, `deployment/approval-record-schema.yaml`, `deployment/bundle-layout-contract.md`, `deployment/manifest-lineage-contract.md`, `deployment/index-activation-contract.md`, `deployment/operator-runbook-stage11.md`, `deployment/check_stage11_readiness.py`, `deployment/initialize_stage11_baseline.py`, `deployment/build_outbound_bundle.py`, `deployment/approve_bundle.py`, `deployment/validate_bundle.py`, `deployment/stage_bundle_for_indexing.py`, `deployment/reindex_staged_bundle.py`, `deployment/run_activation_smoke.py`, `deployment/activate_index.py`, `deployment/rollback_index.py`, `docs/v2/stage11-front-half-report.md`, `docs/v2/stage11-back-half-report.md` | implemented for the validated slice through a local end-to-end drill | Approved bundle build, approval, validation, staging, reindex, runtime smoke, activation, archive, and rollback are reproducible on the seed slice |
| Evaluation and red-team | We need measurable acceptance, not intuition | QA / Evaluation / Red Team | `docs/v2/evaluation-spec.md`, `eval/benchmarks/p0_red_team_cases.jsonl`, `eval/stage10_red_team_report.py`, `eval/stage10_suite.py`, `docs/v2/stage10-evaluation-report.md` | implemented with Stage 10 go decision | Baseline dataset, pass criteria, policy-prepared retrieval notes, and blockers are documented in a reproducible suite report |
| OCP operations usefulness | The product must solve real install, upgrade, and troubleshooting questions | OCP Operations SME | `docs/v2/evaluation-spec.md` | defined | Scenario coverage includes install, update, disconnected, and troubleshooting |
| Multi-repo workspace discipline | The product repo, OpenDocuments, and openshift-docs must evolve together without mixing Git histories | Lead Architect / PM | `docs/v2/workspace-guide.md` | defined | Team members can work across the three repositories without ownership confusion |

## What is already closed

- source repository choice
- initial source boundary policy
- metadata contract
- answer grounding policy
- OpenDocuments ingestion validation on the normalized P0 corpus
- Stage 9 policy-shaped retrieval benchmark on the fixed dataset
- Stage 10 evaluation and red-team execution path
- validation-slice follow-up analysis for `RB-011`
- Stage 11 repository-side preflight contracts and readiness gate
- Stage 11 front-half bundle workflow
- Stage 11 back-half reindex, runtime smoke, activation, and rollback drill
- Stage 12 live runtime smoke and citation viewer baseline
- Stage 13 source-profile and git-lineage abstraction

## What still needs implementation

- section-aware chunk generation
- optional operator-facing UI polish beyond the current citation viewer baseline

## Interpretation rule

When there is ambiguity between "build it ourselves" and "align with OpenDocuments", v2 follows this rule:

- we directly implement the OCP-specific critical path
- we align the RAG flow and product behavior to the OpenDocuments reference model

This is the controlling interpretation for the project unless a newer written direction replaces it.
