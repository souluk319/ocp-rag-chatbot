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

These assets no longer stop at preflight. The repository now implements the Stage 11 front half:

- outbound bundle build
- approval record update
- inbound validation
- staging for indexing

The remaining gap is the back half:

- reindex
- smoke before cutover
- activation pointer update
- rollback drill

## Repository-side prerequisites

The repository is considered Stage 11-ready only when all of the following are true:

1. `data/manifests/approved-baseline.json` is initialized from a validated manifest and Stage 10 `go` report
2. `deployment/activation-smoke-case-ids.json` exists and references fixed benchmark ids
3. `data/packages/inbound/` and `data/packages/outbound/` exist as stable handoff locations
4. `deployment/check_stage11_readiness.py` reports no repository-side blockers
5. `indexes/current.txt` points to a real validated local index directory

## Current status

The current preflight report is:

- `data/manifests/generated/stage11-readiness-report.json`

Current interpretation:

- `ready_for_stage11 = true`
- repository-side preflight passes
- `indexes/current.txt` is still `uninitialized`, but this is currently treated as an activation warning rather than a Stage 11 start blocker

That warning still matters. Before the first real index flip or rollback drill, `indexes/current.txt` must be seeded with the id of a real validated local index.

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

## Interpretation

If readiness passes with only the `indexes/current.txt` warning left, Stage 11 can start and the front-half bundle path can be exercised safely.

It is still not production-safe for cutover until:

- a real local index id seeds `indexes/current.txt`
- reindex and smoke are recorded against a staged bundle
- activation and rollback evidence exist
