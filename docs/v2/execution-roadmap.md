# v2 Execution Roadmap

## Purpose

This document breaks the v2 rewrite into concrete execution stages so we can move one step at a time with clear visibility.

The rule is simple:

- do not advance because work "looks roughly done"
- advance only when the current stage exit criteria are satisfied

This roadmap is the operational companion to:

- `docs/v2/architecture-blueprint.md`
- `docs/v2/source-scope.md`
- `docs/v2/evaluation-spec.md`
- `docs/v2/feedback-response-plan.md`

## How to use this document

For each stage, we track:

- goal
- why it matters
- primary owners
- inputs
- work items
- expected deliverables
- exit criteria

Only one stage should be treated as the active implementation focus at a time.

## Current stage summary

- Stage 0: complete
- Stage 1: complete
- Stage 2: complete for first pass
- Stage 3: complete
- Stage 4: complete
- Stage 4.5: complete
- Stage 5: complete
- Stage 6: complete
- Stage 7: next active implementation stage

## Stage 0. Freeze the rewrite baseline

### Goal

Reset the branch away from the v1 runtime and establish the v2 design baseline.

### Why it matters

Without a clean rewrite baseline, the project drifts back into v1 assumptions.

### Primary owners

- Lead Architect / PM

### Inputs

- `release/v1`
- `v1.0`
- `rewrite/opendoc-v2`

### Work items

- preserve v1 separately
- reset the rewrite branch
- define repository purpose and layout
- add initial v2 planning documents

### Deliverables

- `README.md`
- `docs/v2/plan.md`
- `docs/v2/workspace-guide.md`

### Exit criteria

- v2 is clearly separated from v1
- the rewrite branch no longer depends on the old runtime

## Stage 1. Lock official source trust and scope

### Goal

Define what counts as trusted official OCP source material and what enters the first corpus.

### Why it matters

Poor source boundary means noisy retrieval and weak trust in answers.

### Primary owners

- Data / Document Onboarding Engineer
- OCP Operations SME
- Lead Architect / PM

### Inputs

- `C:\Users\soulu\cywell\openshift-docs`
- `docs/v2/feedback-response-plan.md`

### Work items

- define official-source trust rule
- define validation slice vs first operational release target
- define top-level exclusions and path-fragment exclusions
- define version-scope rule for operator-facing release

### Deliverables

- `docs/v2/source-scope.md`
- `configs/source-manifest.yaml`

### Exit criteria

- validation slice is explicit
- first operational release target is explicit
- exclusion rules are documented
- official-source trust rule is written down

## Stage 2. Normalize `.adoc` into reproducible working outputs

### Goal

Build a repeatable normalization pipeline that turns `openshift-docs` input into stable working artifacts.

### Why it matters

The RAG system cannot operate reliably on raw `.adoc` alone.

### Primary owners

- Data / Document Onboarding Engineer
- RAG / Search Engineer

### Inputs

- `docs/v2/source-scope.md`
- `configs/source-manifest.yaml`

### Work items

- read the selected `.adoc` files
- normalize them into retrieval-friendly text
- emit metadata manifests
- record accepted and excluded document counts

### Deliverables

- `ingest/normalize_openshift_docs.py`
- `configs/metadata-schema.yaml`
- generated manifests under `data/manifests/generated/`

### Exit criteria

- the same normalized corpus can be regenerated
- excluded paths behave as documented
- manifest output is stable enough for repeated runs

## Stage 3. Define the chunking contract

### Goal

Turn the chunking strategy from a design note into an implementation-ready contract.

### Why it matters

The first presentation feedback explicitly called out weak chunking.

### Primary owners

- RAG / Search Engineer
- Data / Document Onboarding Engineer

### Inputs

- `docs/v2/architecture-blueprint.md`
- `configs/metadata-schema.yaml`
- normalized P0 corpus

### Work items

- define chunk types: `prose`, `procedure`, `code`, `reference`
- define chunk size targets and overlap rules
- define section boundary handling
- define procedure preservation rules
- define section metadata emitted per chunk
- define citation alignment contract from chunk to section

### Deliverables

- `docs/v2/chunking-contract.md`
- `configs/chunk-schema.yaml`
- implementation plan for chunk emission
- sample chunk schema for one normalized document

### Exit criteria

- chunk boundaries are no longer ambiguous
- chunk metadata requirements are explicit
- procedure and code handling rules are fixed

## Stage 4. Emit HTML citation views and section metadata

### Goal

Produce the human-readable citation target alongside the retrieval output.

### Why it matters

Citation click-through is a hard product requirement.

### Primary owners

- UI / UX Engineer
- Data / Document Onboarding Engineer
- RAG / Search Engineer

### Inputs

- canonical document model
- chunking contract

### Work items

- generate internal HTML documents from normalized source structure
- generate stable section anchors
- generate `viewer_url`
- verify that chunk metadata and HTML anchors stay aligned

### Deliverables

- generated HTML citation views under `data/views/openshift-docs-p0/`
- metadata fields including `viewer_url`, `section_title`, and `heading_hierarchy`
- manifest records with `html_path`, `section_count`, and section metadata
- one sample rendered document with working anchors

### Exit criteria

- every chunk can resolve to a readable HTML citation target
- section-level click-through is possible on a sample corpus

## Stage 4.5. Add the context-retention harness

### Goal

Create a diagnostic harness that shows where grounded context is lost before formal retrieval benchmarking begins.

### Why it matters

If Stage 5 fails, we need to know whether the problem came from retrieval, rerank, context assembly, truncation, or citation rendering.

### Primary owners

- RAG / Search Engineer
- QA / Evaluation / Red Team
- LLM Serving / Backend Engineer

### Inputs

- `docs/v2/context-retention-harness.md`
- `docs/v2/evaluation-spec.md`
- Stage 4 metadata and `viewer_url` outputs

### Work items

- define the trace record used for per-turn context diagnostics
- define context-loss classes such as retrieval miss, rerank loss, and assembly loss
- add a reporter that summarizes trace findings
- add sample traces that prove the reporter can classify loss modes

### Deliverables

- `docs/v2/context-retention-harness.md`
- `eval/context-harness-schema.yaml`
- `eval/context_harness_report.py`
- `eval/fixtures/context_harness_sample.jsonl`

### Exit criteria

- the trace format is fixed for upcoming benchmark cases
- a reporter can classify the main context-loss modes
- at least one sample trace can be summarized end to end
- Stage 5 explicitly uses this harness instead of bypassing it

## Stage 5. Build the retrieval benchmark dataset

### Goal

Create a fixed dataset that measures retrieval quality instead of relying on intuition.

### Why it matters

The earlier review explicitly said vector search quality was not validated.

### Primary owners

- QA / Evaluation / Red Team
- RAG / Search Engineer
- OCP Operations SME

### Inputs

- `docs/v2/evaluation-spec.md`
- `docs/v2/context-retention-harness.md`
- normalized P0 corpus

### Work items

- define query classes
- write Korean evaluation questions
- define expected source directories and expected supporting documents
- define benchmark metrics and first-slice gates
- define rerank comparison method

### Deliverables

- `docs/v2/retrieval-benchmark-plan.md`
- `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`
- `eval/retrieval-benchmark-schema.yaml`
- `eval/retrieval_benchmark_report.py`
- `eval/fixtures/retrieval_benchmark_sample_results.jsonl`

### Exit criteria

- top-k metrics can be computed consistently
- rerank deltas can be reported
- expected source behavior is documented per query

## Stage 6. Validate OpenDocuments on the normalized validation slice

### Goal

Prove that the normalized corpus can actually be indexed and queried with the OpenDocuments baseline.

### Why it matters

This is the first end-to-end RAG proof point for v2.

### Primary owners

- RAG / Search Engineer
- LLM Serving / Backend Engineer

### Inputs

- normalized P0 corpus
- HTML citation outputs
- benchmark dataset draft

### Work items

- connect the local OpenDocuments workspace
- ingest the normalized P0 corpus
- run citation-bearing queries
- check Korean answers
- confirm streaming behavior

### Deliverables

- minimal ingest and query validation notes
- first benchmark run against OpenDocuments baseline

### Exit criteria

- OpenDocuments indexes the normalized slice
- answers cite sources
- citations open the expected HTML target

## Stage 7. Add multi-turn memory and follow-up rewrite

### Goal

Make grounded multi-turn behavior an implemented feature, not a hope.

### Why it matters

The earlier review explicitly said multi-turn support was weak.

### Primary owners

- LLM Serving / Backend Engineer
- RAG / Search Engineer

### Inputs

- `docs/v2/architecture-blueprint.md`
- `docs/v2/evaluation-spec.md`

### Work items

- define session memory structure
- retain active topic and version state
- implement follow-up rewrite behavior
- add memory reset and conflict rules
- validate 5-turn continuity

### Deliverables

- memory and rewrite implementation plan
- first multi-turn test scenarios

### Exit criteria

- at least one 5-turn scenario remains grounded
- version continuity does not drift silently
- follow-up turns still retrieve relevant sources

## Stage 8. Lock the runtime to the approved company endpoint

### Goal

Ensure the runtime cannot drift to unapproved model providers.

### Why it matters

Closed-network operation and evaluation consistency both depend on controlled runtime settings.

### Primary owners

- LLM Serving / Backend Engineer
- Lead Architect / PM

### Inputs

- local `.env`
- OpenDocuments config points

### Work items

- define the approved endpoint configuration
- remove fallback ambiguity
- document startup assumptions

### Deliverables

- runtime configuration notes
- single-endpoint assumption documented in the integrated path

### Exit criteria

- one approved endpoint is the only supported runtime target

## Stage 9. Apply OCP retrieval and answer policies

### Goal

Make the system behave like an OCP operations assistant instead of a generic document bot.

### Why it matters

Official-source preference and version safety are central to trust.

### Primary owners

- RAG / Search Engineer
- OCP Operations SME
- LLM Serving / Backend Engineer

### Inputs

- `configs/rag-policy.yaml`
- retrieval benchmark results

### Work items

- enforce source trust ordering
- enforce version preference rules
- define conservative answer behavior
- define operations vs study mode behavior

### Deliverables

- refined retrieval and answer policy
- updated benchmark expectations if needed

### Exit criteria

- answers prefer the correct source family
- version-safe behavior is visible and testable

## Stage 10. Run evaluation and red-team checks

### Goal

Decide whether the validation slice is good enough to widen safely.

### Why it matters

Without this stage, scope expands before the baseline is trustworthy.

### Primary owners

- QA / Evaluation / Red Team
- OCP Operations SME
- RAG / Search Engineer

### Inputs

- retrieval benchmark dataset
- multi-turn scenarios
- OpenDocuments validation result

### Work items

- run retrieval benchmark
- run citation click-through checks
- run multi-turn continuity tests
- run red-team prompts
- record failures and gating status

### Deliverables

- benchmark report
- red-team notes
- go/no-go decision for widening scope

### Exit criteria

- first-slice gates in `docs/v2/evaluation-spec.md` pass
- known blockers are documented if any remain

## Stage 11. Build the approved air-gap refresh loop

### Goal

Turn the working prototype into an updateable closed-network system.

### Why it matters

The target product is not just a demo; it must survive document updates.

### Primary owners

- OCP / Air-gapped Infrastructure Engineer
- Data / Document Onboarding Engineer
- LLM Serving / Backend Engineer

### Inputs

- `deployment/airgap-flow.md`
- `deployment/bundle-schema.yaml`

### Work items

- define bundle generation
- define import validation
- define reindex and activation flow
- define rollback rule

### Deliverables

- repeatable bundle workflow
- documented approval and rollback path

### Exit criteria

- one document refresh cycle can be performed end to end

## Stage 12. Touch UI last

### Goal

Make the working assistant usable without distracting from core retrieval quality.

### Why it matters

UI polish before retrieval quality wastes time and hides core problems.

### Primary owners

- UI / UX Engineer
- RAG / Search Engineer

### Inputs

- stable citation flow
- stable benchmark baseline

### Work items

- keep the default OpenDocuments UI first
- add only the minimum OCP-specific UX
- surface citations and HTML document links clearly

### Deliverables

- minimal operator-facing UI improvements

### Exit criteria

- users can ask questions, inspect citations, and open supporting documents easily

## Stage advancement rule

We only move to the next stage when:

1. the current stage deliverables exist
2. the current stage exit criteria are met
3. any known exceptions are written down explicitly

This is how we keep the project understandable and avoid hidden scope drift.
