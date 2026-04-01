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
- `eval/fixtures/context_harness_sample.jsonl` (fixed reference traces for context-loss classification)
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

The Stage 10 suite records a `go` decision for widening scope on the validated P0 slice.

Why:

- the Stage 9 policy-prepared benchmark now closes the previously open follow-up gap
- the Stage 7 multi-turn replay passes
- the context-retention harness successfully classifies failure modes
- the red-team policy and memory checks pass

## Observed metrics

### Stage 9 policy benchmark

- `source_dir_hit@5 = 1.0000`
- `supporting_doc_hit@10 = 1.0000`
- `citation_correctness = 1.0000`
- `reranked_supporting_doc_hit@5 = 1.0000`
- `rerank_lift@5 = 0.0000`

### Stage 9 raw retrieval diagnostic

- `supporting_doc_hit@10 = 0.9231`
- `follow_up_rewrite supporting_doc_hit@10 = 0.0000`

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

- strong enough to widen without hiding a known grounded follow-up blocker
- still instrumented well enough that retrieval, rerank, assembly, and citation losses can be separated when regressions appear

That is a healthy Stage 10 outcome.

The point of this stage is not to prove raw retrieval is perfect. It is to prove the accepted policy-shaped path is measurable, grounded, and safe enough to broaden deliberately.

## Immediate next action

Next focus:

- Stage 11 approved air-gap refresh loop
- live runtime integration of the validated policy and memory behavior
- keeping raw retrieval diagnostics visible so future follow-up regressions are not hidden by policy rescue
