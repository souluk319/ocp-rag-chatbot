# Stage 11 Readiness

## Purpose

This document records the repository-side prerequisites that must exist before Stage 11 can begin as a real air-gap refresh loop instead of a vague design note.

The canonical operational readiness contract lives in:

- `deployment/stage11-readiness.md`

Stage 11 should only start after two things are true:

1. the validated slice has an approved baseline record
2. the closed-network activation path has a concrete preflight check

## What was added before Stage 11

- `deployment/activation-smoke-case-ids.json`
- `deployment/initialize_stage11_baseline.py`
- `deployment/check_stage11_readiness.py`
- `deployment/approval-record-schema.yaml`
- `deployment/bundle-layout-contract.md`
- `deployment/index-activation-contract.md`
- `deployment/manifest-lineage-contract.md`
- `deployment/operator-runbook-stage11.md`
- `data/packages/inbound/.gitkeep`
- `data/packages/outbound/.gitkeep`
- `data/staging/.gitkeep`
- `indexes/previous.txt`

These assets no longer stop at preflight. The repository now implements the full local Stage 11 loop:

- outbound bundle build
- approval record update
- inbound validation
- staging for indexing
- reindex artifact generation
- activation smoke
- pointer cutover
- rollback drill

## Repository-side prerequisites

The repository is considered Stage 11-ready only when all of the following are true:

1. `data/manifests/approved-baseline.json` is initialized from a validated manifest and Stage 10 `go` report
2. `deployment/activation-smoke-case-ids.json` exists and references fixed benchmark ids
3. `data/packages/inbound/` and `data/packages/outbound/` exist as stable handoff locations
4. `deployment/check_stage11_readiness.py` reports no repository-side blockers
5. `indexes/current.txt` points to a real validated local index directory before activation is attempted

## Current status

The current preflight report is:

- `data/manifests/generated/stage11-readiness-report.json`

Current interpretation:

- `ready_for_stage11 = true`
- repository-side preflight passes
- the readiness warning about `indexes/current.txt` was closed locally by bootstrapping `baseline-openshift-docs-p0`
- a full local Stage 11 cutover and rollback drill has now been executed

## Commands

Initialize the approved baseline:

```powershell
python deployment/initialize_stage11_baseline.py
```

If a validated local index id is already known:

```powershell
python deployment/initialize_stage11_baseline.py --active-index-id <real-index-id>
```

Run the Stage 11 readiness check:

```powershell
python deployment/check_stage11_readiness.py
```

Run the verified local front-half dry-run:

```powershell
python deployment/build_outbound_bundle.py --mode seed --bundle-id stage11-local-seed --force
python deployment/approve_bundle.py --bundle data/packages/outbound/stage11-local-seed --status approved --reviewer codex-local
python deployment/validate_bundle.py data/packages/outbound/stage11-local-seed --require-approved
Copy-Item -Recurse -Force data/packages/outbound/stage11-local-seed data/packages/inbound/stage11-local-seed
python deployment/validate_bundle.py data/packages/inbound/stage11-local-seed --require-approved
python deployment/stage_bundle_for_indexing.py data/packages/inbound/stage11-local-seed --force
```

Run the verified local back-half drill:

```powershell
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id baseline-openshift-docs-p0 --force --output data/manifests/generated/stage11-baseline-reindex-report.json
python deployment/run_activation_smoke.py --index baseline-openshift-docs-p0 --output data/manifests/generated/stage11-baseline-smoke-report.json
python deployment/activate_index.py --index baseline-openshift-docs-p0 --bootstrap-current --operator codex-local --smoke-report data/manifests/generated/stage11-baseline-smoke-report.json --reindex-report data/manifests/generated/stage11-baseline-reindex-report.json --output data/manifests/generated/stage11-baseline-activation-report.json
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id stage11-local-seed --force --output data/manifests/generated/stage11-seed-reindex-report.json
python deployment/run_activation_smoke.py --index stage11-local-seed --output data/manifests/generated/stage11-seed-smoke-report.json
python deployment/activate_index.py --index stage11-local-seed --operator codex-local --smoke-report data/manifests/generated/stage11-seed-smoke-report.json --reindex-report data/manifests/generated/stage11-seed-reindex-report.json --output data/manifests/generated/stage11-seed-activation-report.json
python deployment/rollback_index.py --operator codex-local --output data/manifests/generated/stage11-seed-rollback-report.json
```

## Interpretation

Stage 11 is now considered closed for the validated slice because:

- a real local index id seeded `indexes/current.txt`
- reindex and runtime smoke were recorded against a staged bundle
- activation and rollback evidence exist
- archive snapshots exist for both the displaced baseline and the rolled-back seed index

Important interpretation:

- Stage 11 smoke validates runtime ingest, grounding, citation presence, and citation click-through on the staged index
- Stage 9 and Stage 10 remain the authoritative retrieval-quality benchmark for the validated slice
