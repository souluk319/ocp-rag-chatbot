# Evaluation Scope

This directory now contains the v2 evaluation assets used to gate the validated P0 slice.

Current contents include:

- OCP operations benchmark questions and expected source targets
- citation checks and click-through evidence
- context-retention harness traces and summarizers
- retrieval benchmark case sets and scoring reports
- multi-turn scenario datasets and rewrite replay reports
- red-team prompts for unsafe or weakly grounded answers
- Stage 10 suite aggregation reports and release-gate evidence

Authoritative generated outputs live under `data/manifests/generated/`.
Files under `eval/fixtures/` are stable sample snapshots for documentation and test wiring, not the authoritative current gate state.

The controlling evaluation documents are:

- `docs/v2/evaluation-spec.md`
- `docs/v2/context-retention-harness.md`
- `docs/v2/retrieval-benchmark-plan.md`
- `docs/v2/stage10-evaluation-report.md`
