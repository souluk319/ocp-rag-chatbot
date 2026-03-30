# Stage 11 Front-Half Report

## Purpose

This document records the first verified Stage 11 dry-run for the repository-side air-gap refresh loop.

It covers only the front half of Stage 11:

- outbound bundle build
- approval record update
- inbound bundle validation
- staging for indexing

It does not yet cover:

- reindex
- smoke against the new index
- activation pointer flip
- rollback drill

## Verified run

Validated local bundle id:

- `stage11-local-seed`

Bundle mode:

- `seed`

Why `seed` was used:

- the approved baseline and current normalized manifest are the same validated P0 slice
- `seed` exercises the transfer packaging path without waiting for a later corpus delta

## Commands executed

Initialize the approved baseline with per-document snapshots:

```powershell
python deployment/initialize_stage11_baseline.py --force
```

Build the outbound seed bundle:

```powershell
python deployment/build_outbound_bundle.py --mode seed --bundle-id stage11-local-seed --force
```

Approve the outbound bundle and refresh checksums:

```powershell
python deployment/approve_bundle.py --bundle data/packages/outbound/stage11-local-seed --status approved --reviewer codex-local --note "Local Stage 11 seed dry-run approval"
```

Validate the outbound bundle:

```powershell
python deployment/validate_bundle.py data/packages/outbound/stage11-local-seed --require-approved --output data/manifests/generated/stage11-seed-outbound-validation.json
```

Simulate transfer into inbound:

```powershell
Copy-Item -Recurse -Force data/packages/outbound/stage11-local-seed data/packages/inbound/stage11-local-seed
```

Validate the inbound bundle:

```powershell
python deployment/validate_bundle.py data/packages/inbound/stage11-local-seed --require-approved --output data/manifests/generated/stage11-seed-inbound-validation.json
```

Stage the inbound bundle for indexing:

```powershell
python deployment/stage_bundle_for_indexing.py data/packages/inbound/stage11-local-seed --force --output data/manifests/generated/stage11-seed-staging-report.json
```

## Results

- outbound validation: `valid = true`
- inbound validation: `valid = true`
- staging completed successfully
- staged summary: `added = 281`, `changed = 0`, `removed = 0`
- separate delta verification on `stage11-local-delta` produced `added = 0`, `changed = 0`, `removed = 0` and still passed bundle validation

Generated evidence:

- `data/manifests/generated/stage11-seed-outbound-validation.json`
- `data/manifests/generated/stage11-seed-inbound-validation.json`
- `data/manifests/generated/stage11-seed-staging-report.json`
- `data/manifests/generated/stage11-delta-outbound-validation.json`

## Interpretation

The Stage 11 contracts are now more than design notes.

The repository can already:

- build a reproducible bundle from the normalized manifest and approved baseline
- stamp an approval record without hardcoding runtime secrets
- validate schema, payload files, and checksums
- expand an inbound bundle into a versioned staging directory

The remaining Stage 11 work starts after staging:

- build the new index under `indexes/<bundle-id>/`
- run the smoke subset
- update `indexes/previous.txt` and `indexes/current.txt`
- capture rollback evidence
