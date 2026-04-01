# Stage 15 Core Validation Corpus

## Purpose

Stage 15 widens the validated corpus without forcing an operator-facing minor-version pin too early.

The goal is to pressure the real pipeline with a broader OCP operations surface while keeping the source-profile abstraction intact.

## Why this stage exists

Stage 14 closed the operator launch path, but the validated slice is still narrow.

We need a broader validation corpus so we can:

- test retrieval stability on a more realistic operator scope
- test citation alignment and viewer coverage on more categories
- test runtime and refresh behavior before a target minor is approved

## Profile choice

This stage uses:

- `ocp-validation-main-core`

This keeps:

- `git_ref = main`
- `purpose = validation`
- `corpus_scope = core_validation`

while widening the include directories significantly beyond P0.

## Scope choice

The core validation corpus includes the first operator-facing surface areas that add the most practical value without prematurely pulling in highly version-sensitive or very large reference families.

Included:

- install / post-install / update
- backup / restore
- networking
- security
- storage
- nodes / operators / observability / etcd
- disconnected / registry / cli_reference
- authentication / architecture / machine configuration / machine management
- web console / applications / cicd
- troubleshooting support

Deferred:

- `release_notes`
- `rest_api`

## Exit criteria

Stage 15 is complete when:

- the wider validation profile normalizes successfully
- HTML citation views are generated for the wider corpus
- manifest lineage is preserved
- the resulting corpus is ready for Stage 9~12 regression runs

## Validation evidence

The current local Stage 15 run produced:

- profile: `ocp-validation-main-core`
- source ref: `main`
- source commit: `b046c68e01e8032863200271caf7c95a73760364`
- scanned `.adoc`: `1233`
- accepted documents: `1201`

Top-level distribution highlights:

- `networking`: `158`
- `observability`: `133`
- `security`: `121`
- `nodes`: `87`
- `backup_and_restore`: `66`
- `cicd`: `64`

Generated artifacts:

- normalized manifest: `data/manifests/generated/openshift-docs-core-validation.json`
- duplicate-anchor report: `data/manifests/generated/core-duplicate-anchor-report.json`
- HTML citation root: `data/views/openshift-docs-core-validation/`

## Anchor and citation alignment note

During Stage 15, section-anchor generation was hardened so repeated headings inside the same document receive unique HTML ids.

Observed result:

- documents with duplicate anchors: `0`
- documents with duplicate titles: `102`

Interpretation:

- repeated section titles still exist in the source corpus
- but the generated HTML anchor ids are now unique, which keeps click-through alignment stable
- runtime citation resolution now prefers full `heading_hierarchy` matches before falling back to section title only

## Delta activation evidence

The widened corpus was exercised through the Stage 11 path with a short Windows-safe bundle id:

- bundle id: `s15c`
- mode: `delta`
- added: `920`
- changed: `281`
- removed: `0`
- activated index: `s15c-core`

Evidence:

- `data/manifests/generated/s15c-core-reindex-report.json`
- `data/manifests/generated/s15c-core-smoke-report.json`
- `data/manifests/generated/s15c-core-activation-report.json`
- `data/manifests/generated/s15c-core-live-runtime-report.json`

## Current warning

There are two important warnings after Stage 15:

1. Windows path length can still affect bundle generation if bundle ids are too long.
2. Stage 11 activation smoke currently uses a weaker OpenDocuments bootstrap path than the bridge-driven runtime, so retrieval-alignment failures there are conservative but still meaningful.

## Decision

Stage 15 is considered complete for corpus expansion and runtime activation.

The next focus is not more source breadth immediately.

The next focus is:

- widened-corpus retrieval regression
- better parity between Stage 11 activation smoke and the approved bridge-driven runtime
