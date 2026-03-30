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
- Stage 11 front-half dry-run passes for `build -> approve -> validate -> stage` on the validated seed bundle
- Stage 11 back-half local drill passes for `reindex -> runtime smoke -> activate -> rollback`
- Stage 11 archive snapshots are created for displaced active indexes during cutover and rollback
- Stage 11 delta diff path also validates cleanly when the approved baseline and normalized manifest are identical
- Stage 11 runtime smoke verifies ingest, grounding, citation presence, and click-through; retrieval quality itself still follows the Stage 9/10 benchmark gates
- a product-owned runtime gateway now exists to apply Stage 7 multi-turn rewrite and Stage 9 source policy on the live OpenDocuments HTTP path

## Next milestones

1. Verify the new runtime gateway against a live OpenDocuments server path
2. Finish minimal operator-facing UI hardening in Stage 12
3. Expand the approved corpus beyond the validated P0 slice without regressing Stage 10 and Stage 11 gates

## Design docs

- `docs/v2/architecture-blueprint.md`
- `docs/v2/execution-roadmap.md`
- `docs/v2/stage11-readiness.md`
- `docs/v2/stage11-front-half-report.md`
- `docs/v2/stage11-back-half-report.md`
- `docs/v2/chunking-contract.md`
- `docs/v2/context-retention-harness.md`
- `docs/v2/company-runtime-lock.md`
- `docs/v2/live-runtime-gateway.md`
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

## Stage 11 preflight and local dry-run

Before Stage 11 activation work starts, initialize the approved baseline and run the readiness gate:

```powershell
python deployment/initialize_stage11_baseline.py
python deployment/check_stage11_readiness.py
```

The readiness gate is still the correct way to start Stage 11. The local validated drill then closes the first-activation warning by seeding a real baseline index before switching and rolling back.

The currently verified local Stage 11 front-half flow is:

```powershell
python deployment/build_outbound_bundle.py --mode seed --bundle-id stage11-local-seed --force
python deployment/approve_bundle.py --bundle data/packages/outbound/stage11-local-seed --status approved --reviewer codex-local
python deployment/validate_bundle.py data/packages/outbound/stage11-local-seed --require-approved
Copy-Item -Recurse -Force data/packages/outbound/stage11-local-seed data/packages/inbound/stage11-local-seed
python deployment/validate_bundle.py data/packages/inbound/stage11-local-seed --require-approved
python deployment/stage_bundle_for_indexing.py data/packages/inbound/stage11-local-seed --force
```

The verified local Stage 11 back-half flow is:

```powershell
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id baseline-openshift-docs-p0 --force --output data/manifests/generated/stage11-baseline-reindex-report.json
python deployment/run_activation_smoke.py --index baseline-openshift-docs-p0 --output data/manifests/generated/stage11-baseline-smoke-report.json
python deployment/activate_index.py --index baseline-openshift-docs-p0 --bootstrap-current --operator codex-local --smoke-report data/manifests/generated/stage11-baseline-smoke-report.json --reindex-report data/manifests/generated/stage11-baseline-reindex-report.json --output data/manifests/generated/stage11-baseline-activation-report.json
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id stage11-local-seed --force --output data/manifests/generated/stage11-seed-reindex-report.json
python deployment/run_activation_smoke.py --index stage11-local-seed --output data/manifests/generated/stage11-seed-smoke-report.json
python deployment/activate_index.py --index stage11-local-seed --operator codex-local --smoke-report data/manifests/generated/stage11-seed-smoke-report.json --reindex-report data/manifests/generated/stage11-seed-reindex-report.json --output data/manifests/generated/stage11-seed-activation-report.json
python deployment/rollback_index.py --operator codex-local --output data/manifests/generated/stage11-seed-rollback-report.json
```
