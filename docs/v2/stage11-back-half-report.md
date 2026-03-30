# Stage 11 Back-Half Report

## Purpose

This report records the local end-to-end validation of the Stage 11 back half:

- reindex
- activation smoke
- pointer cutover
- rollback drill

The goal was not to widen the corpus yet. The goal was to prove that the approved refresh loop can execute end to end on the validated P0 seed bundle without losing citation integrity, while using a real OpenDocuments runtime smoke pass for the staged index.

## Implemented scripts

- `deployment/reindex_staged_bundle.py`
- `deployment/run_activation_smoke.py`
- `deployment/activate_index.py`
- `deployment/rollback_index.py`
- `deployment/stage11_activation_utils.py`

This stage also depends on the Stage 11 front-half staging manifest emitted by:

- `deployment/stage_bundle_for_indexing.py`

## Local execution sequence

### 1. Build a baseline index artifact from the staged seed bundle

```powershell
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id baseline-openshift-docs-p0 --force --output data/manifests/generated/stage11-baseline-reindex-report.json
python deployment/run_activation_smoke.py --index baseline-openshift-docs-p0 --output data/manifests/generated/stage11-baseline-smoke-report.json
python deployment/activate_index.py --index baseline-openshift-docs-p0 --bootstrap-current --operator codex-local --smoke-report data/manifests/generated/stage11-baseline-smoke-report.json --reindex-report data/manifests/generated/stage11-baseline-reindex-report.json --output data/manifests/generated/stage11-baseline-activation-report.json
```

Observed outcome:

- `281` staged documents verified
- `281` HTML citation views verified
- runtime smoke subset completed with `5 / 5` observed cases
- `runtime_smoke_pass = true`
- `retrieval_alignment_pass = false` under the current stub-model path, so Stage 9 and Stage 10 remain the authoritative retrieval-quality gate
- first active pointer was seeded with `baseline-openshift-docs-p0`

### 2. Build and validate the incoming seed index

```powershell
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id stage11-local-seed --force --output data/manifests/generated/stage11-seed-reindex-report.json
python deployment/run_activation_smoke.py --index stage11-local-seed --output data/manifests/generated/stage11-seed-smoke-report.json
python deployment/activate_index.py --index stage11-local-seed --operator codex-local --smoke-report data/manifests/generated/stage11-seed-smoke-report.json --reindex-report data/manifests/generated/stage11-seed-reindex-report.json --output data/manifests/generated/stage11-seed-activation-report.json
```

Observed outcome:

- `281` staged documents verified
- `281` HTML citation views verified
- runtime smoke subset completed with `5 / 5` observed cases
- `runtime_smoke_pass = true`
- `retrieval_alignment_pass = false` under the current stub-model path, so Stage 9 and Stage 10 remain the authoritative retrieval-quality gate
- activation switched from `baseline-openshift-docs-p0` to `stage11-local-seed`
- previous active index metadata was archived under `indexes/archive/baseline-openshift-docs-p0`

### 3. Roll back to the previous active index

```powershell
python deployment/rollback_index.py --operator codex-local --output data/manifests/generated/stage11-seed-rollback-report.json
```

Observed outcome:

- rollback restored `baseline-openshift-docs-p0`
- post-rollback runtime smoke passed
- rollback archived the displaced index metadata under `indexes/archive/stage11-local-seed`

## Evidence paths

- `data/manifests/generated/stage11-baseline-reindex-report.json`
- `data/manifests/generated/stage11-baseline-smoke-report.json`
- `data/manifests/generated/stage11-baseline-activation-report.json`
- `data/manifests/generated/stage11-seed-reindex-report.json`
- `data/manifests/generated/stage11-seed-smoke-report.json`
- `data/manifests/generated/stage11-seed-activation-report.json`
- `data/manifests/generated/stage11-seed-rollback-report.json`
- `indexes/baseline-openshift-docs-p0/manifests/index-manifest.json`
- `indexes/stage11-local-seed/manifests/index-manifest.json`
- `indexes/baseline-openshift-docs-p0/reports/post-rollback-smoke-report.json`
- `indexes/archive/baseline-openshift-docs-p0/archive-entry.json`
- `indexes/archive/stage11-local-seed/archive-entry.json`

## What this closes

Stage 11 now has local evidence for:

1. approved bundle build
2. import validation
3. staging
4. reindex artifact creation
5. activation smoke against the staged index
6. pointer cutover
7. rollback with post-rollback smoke

## Stage 11 smoke interpretation

Stage 11 smoke is not the primary retrieval-quality benchmark.

Stage 11 smoke answers a different question:

- can the staged corpus be ingested again by the OpenDocuments runtime
- do grounded answers come back
- do citations exist
- do citation targets open
- can cutover and rollback happen without breaking those basics

Retrieval-quality authority still lives in:

- `docs/v2/stage10-evaluation-report.md`
- `data/manifests/generated/stage10-suite-report.json`

That is why the Stage 11 smoke report records both:

- `runtime_smoke_pass`
- `retrieval_alignment_pass`

Only the runtime smoke gate is used for Stage 11 cutover. Retrieval alignment remains a diagnostic signal until the live runtime and policy path are fully unified.

## Remaining interpretation

This closes the repository-side Stage 11 loop for the validated slice.

It does **not** yet mean:

- a widened corpus has been approved
- runtime chat integration is fully wired through the live serving path
- Stage 12 operator UI work is finished
