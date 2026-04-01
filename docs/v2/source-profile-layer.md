# Source Profile Layer

## Purpose

The pipeline must survive a change in document branch or target OCP minor without forcing a code rewrite.

This document defines the indirection layer that separates:

1. where the source mirror lives
2. which source profile is active
3. which target release, if any, is approved for operator-facing use

## Why this layer exists

`openshift-docs` contains many branches.

For v2, the important rule is:

- the system pipeline should stay stable
- only the selected source profile and target release state should change

That means:

- validation can stay on `main`
- operator-facing release can later move to `enterprise-4.17`, `enterprise-4.21`, or another approved minor
- the ingest and Stage 11 refresh flow should not need structural rewrites when that switch happens

## The three layers

### 1. Source mirror

Defined in:

- `configs/source-profiles.yaml`

The mirror layer answers:

- which upstream repository is trusted
- which local checkout path is used
- what trust, product, and language defaults belong to that mirror

Current mirror:

- `openshift-docs`

### 2. Source profile

Defined in:

- `configs/source-profiles.yaml`

The source profile answers:

- which git ref is expected
- which corpus scope is intended
- which include and exclude rules are active
- whether a target minor is required

Current built-in profiles:

- `ocp-validation-main-p0`
- `ocp-target-minor-p0`
- `ocp-target-minor-core`

### 3. Active source profile state

Defined in:

- `configs/active-source-profile.yaml`

The active state answers:

- which source profile is currently active
- whether a target minor has been approved

Current repository state:

- validation profile is active
- target minor is not yet declared

## Git lineage rule

The normalization pipeline now records:

- declared git ref from the resolved source profile
- detected git ref from the local checkout
- detected git commit
- whether the detected ref matches the profile expectation

By default, normalization stops when the profile expects one ref and the local checkout is on another ref.

This prevents accidental operator-facing runs against the wrong branch.

## Output contract

The normalized manifest now carries:

- `source_profile`
- `target_release`
- `source_lineage`

Each normalized document now carries:

- `source_mirror_id`
- `source_profile_id`
- `source_git_ref`
- `source_git_commit`
- `target_minor`

This makes each index and Stage 11 bundle traceable back to the exact source profile and commit.

## Practical switching rule

When the approved operator-facing target minor becomes known:

1. prepare a local checkout or worktree that actually matches that branch
2. switch `configs/active-source-profile.yaml` to the correct operator profile
3. set `target_minor`
4. rerun normalization and the Stage 9 to Stage 12 gates

The system pipeline stays the same. Only the profile state and validated corpus change.

## Current interpretation

For now:

- `main` remains acceptable for validation and pipeline construction
- operator-facing release must not rely on `main` indefinitely
- the Stage 13 layer exists so that the eventual switch is configuration-driven, not rewrite-driven
