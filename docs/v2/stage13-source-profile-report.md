# Stage 13 Source Profile Report

## Purpose

Stage 13 closes the gap between:

- a working validation slice on `main`
- a future operator-facing release pinned to an approved target minor

The goal is not to decide the target minor yet.

The goal is to make that future decision a configuration change instead of a pipeline redesign.

## What was added

- `configs/source-profiles.yaml`
- `configs/active-source-profile.yaml`
- source-profile resolution in `ingest/normalize_openshift_docs.py`
- git-ref mismatch protection in `ingest/normalize_openshift_docs.py`
- branch and commit lineage in normalized manifests
- branch and commit lineage propagation into Stage 11 baseline, bundle, and index manifests

## Current active state

The repository currently stays in validation mode:

- active profile: `ocp-validation-main-p0`
- target minor: unset
- expected git ref: `main`

This keeps the existing validated slice stable while making the future operator-mode switch explicit.

## Why this matters

Before Stage 13:

- `source-manifest.yaml` showed what we wanted to ingest
- but not how branch or target-minor selection should evolve safely

After Stage 13:

- source mirror identity is explicit
- profile identity is explicit
- target release state is explicit
- normalization records the exact commit used
- a ref mismatch is treated as an error by default

## Verified behavior

The normalization pipeline now supports:

- active-profile driven runs without hardcoding branch assumptions
- target-minor templated profiles
- commit-specific source URLs in the emitted manifest
- manifest lineage that survives Stage 11 packaging and reindex

## Interpretation

Stage 13 does not widen the corpus by itself.

It makes widening and branch pinning safe to do later.

That is the correct next step for the project because the system pipeline is still the first priority.
