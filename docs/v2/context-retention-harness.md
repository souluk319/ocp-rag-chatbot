# v2 Context Retention Harness

## Purpose

This document defines the lightweight harness we will use between Stage 4 and Stage 5.

Its job is simple:

- make context loss visible before we start claiming retrieval quality
- separate retrieval failure from rerank failure, assembly failure, and citation failure
- give us a reproducible trace format for follow-up and multi-turn debugging

The harness is intentionally narrow.

It is not a full evaluation framework.
It is a diagnostic layer that sits between implementation and formal benchmarking.

## Why Stage 4.5 exists

Stage 4 gave us:

- section-aware source metadata
- stable `viewer_url`
- HTML citation documents

Before we build the retrieval benchmark dataset, we need to make sure we can answer:

1. did the expected evidence enter retrieval at all
2. did reranking remove good evidence
3. did context assembly drop the right chunk because of token budget
4. did the final citation omit the chunk that actually supported the answer
5. did a follow-up turn lose version or topic continuity

Without this harness, Stage 5 can tell us that a benchmark failed, but it cannot reliably tell us where the failure happened.

## Scope

The Stage 4.5 harness covers four boundaries:

1. user turn to rewritten retrieval query
2. retrieved candidates to reranked candidates
3. reranked candidates to assembled prompt context
4. assembled prompt context to final citations

It also records:

- token-budget pressure
- truncation events
- version-context continuity
- follow-up handling on multi-turn traces

## Harness outputs

Each traced turn should emit a machine-readable record with:

- input question
- rewritten question, if any
- expected support chunk ids
- retrieved candidate chunk ids
- reranked candidate chunk ids
- final assembled context chunk ids
- cited chunk ids
- dropped chunk ids and reason
- token budget usage
- version context before and after the turn

The trace format is defined in:

- `eval/context-harness-schema.yaml`

The first diagnostic reporter lives in:

- `eval/context_harness_report.py`

## Required trace probes

Every traced turn must record the following checkpoints.

### Probe 1. Turn intake

- `turn_id`
- `turn_index`
- `turn_type`
- `user_query`
- `rewritten_query`

### Probe 2. Expected grounding

- `expected_support_chunk_ids`
- `expected_source_dirs`
- `expected_version_behavior`

This is required so we can distinguish missing evidence from weak answer generation.

### Probe 3. Retrieval output

- `retrieval_candidates`
- raw retrieval score when available
- source metadata needed to inspect product line and section identity

### Probe 4. Rerank output

- `reranked_candidates`
- rerank score when available
- ordering relative to retrieval candidates

### Probe 5. Context assembly

- `assembled_context`
- `token_budget`
- `truncation`
- `dropped_candidates`

### Probe 6. Citation alignment

- `citations`
- section-level `viewer_url`
- citation chunk ids or section ids

### Probe 7. Version continuity

- `version_context.before`
- `version_context.after`
- `version_context.change_reason`

## Context-loss classes

The harness must be able to classify at least these failure modes.

### A. Retrieval miss

The expected supporting chunk is absent from `retrieval_candidates`.

### B. Rerank loss

The expected supporting chunk appears in retrieval but disappears from the reranked set.

### C. Assembly loss

The expected supporting chunk survives reranking but is dropped from the final assembled prompt context.

### D. Citation loss

The expected supporting chunk survives assembly but is not represented in the final citation list.

### E. Version drift

The turn changes version context without an explicit user signal or documented reset.

### F. Follow-up rewrite failure

The turn is marked as a follow-up, but the rewritten retrieval query is missing or fails to preserve the grounded topic.

## Required first-pass fields

The first pass does not need every possible debug field.

It must, however, include enough information to answer:

- what should have been kept
- what was actually kept
- where it was dropped

That means the minimum required turn record is:

- `trace_version`
- `run_id`
- `scenario_id`
- `turn_id`
- `turn_index`
- `turn_type`
- `user_query`
- `rewritten_query`
- `expected_support_chunk_ids`
- `retrieval_candidates`
- `reranked_candidates`
- `assembled_context`
- `citations`
- `token_budget`
- `truncation`
- `version_context`

## Relationship to Stage 5

Stage 5 will measure benchmark quality.

Stage 4.5 makes that benchmark explainable.

The rule is:

- Stage 5 can only start after the trace format and reporter exist
- Stage 5 benchmark items should be runnable through the same trace harness

This allows one failing benchmark query to be diagnosed across retrieval, rerank, assembly, and citation.

## Deliverables

- `docs/v2/context-retention-harness.md`
- `eval/context-harness-schema.yaml`
- `eval/context_harness_report.py`
- `eval/fixtures/context_harness_sample.jsonl`

## Exit criteria

Stage 4.5 is complete only if all of the following are true:

1. the trace format is fixed enough to reuse across upcoming benchmark cases
2. a reporter can summarize retrieval miss, rerank loss, assembly loss, citation loss, and version drift
3. at least one sample trace can be validated end to end through the reporter
4. the execution roadmap points Stage 5 to this harness instead of bypassing it
