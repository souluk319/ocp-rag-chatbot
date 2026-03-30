# Stage 10 Evaluation and Red-Team Report

## Purpose

Stage 10 answers one question:

Is the current validation slice trustworthy enough to widen safely?

This report aggregates:

- the Stage 9 policy-shaped retrieval benchmark
- the Stage 7 multi-turn replay result
- the Stage 4.5 context-retention harness
- the Stage 10 red-team checks

## Evidence inputs

- `data/manifests/generated/stage9-policy-report.json`
- `data/manifests/generated/stage10-multiturn-report.json`
- `eval/fixtures/context_harness_sample.jsonl`
- `data/manifests/generated/stage10-red-team-report.json`
- `data/manifests/generated/stage10-suite-report.json`

## Decision rule

The current slice can widen only if all of the following are true:

1. retrieval first-slice gate passes
2. multi-turn gate passes
3. context failures are traceable through the harness
4. red-team checks pass
5. follow-up retrieval for the known weak class no longer misses grounded evidence

## Current result

The Stage 10 suite records a `no-go` decision for widening scope.

Why:

- the Stage 9 benchmark is strong on citation correctness and source-family preference
- the Stage 7 multi-turn replay passes
- the context-retention harness successfully classifies failure modes
- the red-team policy and memory checks pass
- but the known follow-up retrieval gap for `RB-011` is still open

## Observed metrics

### Stage 9 policy benchmark

- `source_dir_hit@5 = 1.0000`
- `supporting_doc_hit@10 = 0.9231`
- `citation_correctness = 0.9231`
- `rerank_lift@5 = 0.0000`

### Stage 7 multi-turn replay

- `scenario_count = 2`
- `fully_passing_scenarios = 2`
- `classification_pass_rate = 1.0000`
- `version_pass_rate = 1.0000`

### Context-retention harness

- `assembly_loss = 1`
- `truncation_applied = 1`
- `invalid_records = 0`

### Stage 10 red-team

- `case_count = 7`
- `passed_count = 7`
- `failed_case_ids = []`

## Interpretation

This means the slice is:

- good enough to keep improving on the current P0 boundary
- not yet safe enough to widen without hiding a real follow-up retrieval weakness

That is a healthy Stage 10 outcome.

The point of this stage is to stop scope expansion when evidence says "not yet."

## Immediate next action

Before Stage 11 or wider corpus expansion, the next iteration must close:

- `RB-011` follow-up retrieval miss

The likely focus area is:

- retrieval candidate generation for short follow-up turns
- stronger memory-aware query rewriting or query expansion for follow-up turns
- optional follow-up-specific boosting using the active document path
