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
- `deployment/seed_approved_baseline.py`
- `deployment/check_stage11_readiness.py`
- `deployment/bundle-layout-contract.md`
- `deployment/index-activation-contract.md`
- `deployment/manifest-lineage-contract.md`
- `deployment/operator-runbook-stage11.md`
- `data/packages/inbound/.gitkeep`
- `data/packages/outbound/.gitkeep`

These assets do not implement the full bundle flow yet. They establish the minimum contract needed to start Stage 11 without guessing.

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
- the current baseline file was bootstrapped for repository readiness and can later be replaced by the formal reviewer-seeded baseline path

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

If the first approved baseline needs formal reviewer attribution instead of bootstrap initialization:

```powershell
python deployment/seed_approved_baseline.py --manifest data/manifests/generated/openshift-docs-p0.json --output data/manifests/approved-baseline.json --reviewer <reviewer-id> --replace
```

Run the Stage 11 readiness check:

```powershell
python deployment/check_stage11_readiness.py
```

## Interpretation

If readiness passes with only the `indexes/current.txt` warning left, Stage 11 can start but the final activation cutover is not yet production-safe.
