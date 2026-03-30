# OCP Operations Assistant v2

This branch is a clean rewrite of the project for a new closed-network OCP operations assistant chatbot.

The previous Python RAG pipeline, legacy web UI, and old local corpus have been intentionally removed from this branch. The legacy system is preserved on `release/v1` and the `v1.0` tag.

## v2 goals

- Build on top of OpenDocuments instead of the custom v1 pipeline
- Rebuild data onboarding from scratch with official and approved internal sources
- Support Korean operations answers with citations and conservative grounding
- Add an approval-based document refresh path for air-gapped environments

## Development model

This repository is the main v2 project. External repositories stay separate and are referenced as inputs:

- `../OpenDocuments`
- `../openshift-docs`
- `../internal-ocp-docs`

Use a multi-root workspace in Antigravity or VS Code so these folders can be opened together without mixing their Git histories.

## Repository layout

```text
app/           thin integration layer and product-specific code
configs/       source manifests, metadata schema, retrieval policy examples
data/          tracked placeholders for manifests and local working directories
deployment/    closed-network deployment notes and bundle flow
docs/v2/       rewrite-specific planning and workspace guidance
eval/          evaluation plan and question-set ownership
indexes/       generated indexes kept out of Git except for placeholders
ingest/        document onboarding pipeline notes
```

## Current validation status

- Stage 10 evaluation currently records `go` on the validated P0 slice
- citations resolve to generated internal HTML views instead of raw `.adoc`
- Stage 9 policy-prepared retrieval reaches `13/13` supporting-document hits and `1.0` citation correctness on the fixed benchmark set
- multi-turn replay passes `2/2` five-turn scenarios with explicit version continuity
- runtime endpoint and model selection stay env-driven and company-only by default

## Next milestones

1. Wire the validated memory and policy path into the live runtime end to end
2. Build the Stage 11 approved air-gap refresh loop
3. Finish streaming and minimal operator-facing UI hardening in Stage 12

## Design docs

- `docs/v2/architecture-blueprint.md`
- `docs/v2/execution-roadmap.md`
- `docs/v2/stage11-readiness.md`
- `docs/v2/chunking-contract.md`
- `docs/v2/context-retention-harness.md`
- `docs/v2/company-runtime-lock.md`
- `docs/v2/ocp-policy-application.md`
- `docs/v2/stage10-evaluation-report.md`
- `docs/v2/retrieval-benchmark-plan.md`
- `docs/v2/source-scope.md`
- `docs/v2/requirements-traceability.md`
- `docs/v2/evaluation-spec.md`
- `docs/v2/feedback-response-plan.md`
- `docs/v2/plan.md`
- `docs/v2/team-execution-order.md`
- `docs/v2/workspace-guide.md`

## Branch rules

- `main` remains the stable line until v2 is ready
- `release/v1` stores the legacy implementation
- `rewrite/opendoc-v2` is the only branch for this rewrite
- Do not reintroduce the v1 runtime into this branch

## Stage 11 preflight

Before Stage 11 activation work starts, initialize the approved baseline and run the readiness gate:

```powershell
python deployment/initialize_stage11_baseline.py
python deployment/check_stage11_readiness.py
```

The current expected result is `ready_for_stage11 = true` with a warning that `indexes/current.txt` is still uninitialized. That warning is acceptable for starting Stage 11, but it must be closed before the first real activation cutover.
