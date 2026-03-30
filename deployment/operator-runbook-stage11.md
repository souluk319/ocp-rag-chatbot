# Stage 11 Operator Runbook

## Purpose

This runbook turns the Stage 11 contracts into an operator sequence.

## Roles

- External collection operator
- Approval reviewer
- Closed-network import operator

## Procedure

### 1. Collect and normalize outside the closed network

- refresh approved source mirrors
- regenerate the normalized corpus manifest
- confirm manifest ID and document counts

### 2. Build the outbound bundle

- diff the generated normalized manifest against `data/manifests/approved-baseline.json`
- assemble the outbound bundle using `deployment/bundle-layout-contract.md`
- generate checksums

### 3. Review and approve

- inspect added, changed, and removed counts
- inspect removal impact
- record the decision in `approval.json`

### 4. Transfer into the closed network

- copy the approved bundle into `data/packages/inbound/<bundle-id>/`
- preserve the exact relative paths

### 5. Validate the inbound bundle

- validate `manifest.json`
- validate `approval.json`
- verify checksums
- stop immediately on any validation failure

### 6. Stage for indexing

- expand the approved bundle into `data/staging/<bundle-id>/`
- verify staged file counts

### 7. Reindex

- build the new index under `indexes/<bundle-id>/`
- record indexing failures before activation is considered
- local entry point:

```powershell
python deployment/reindex_staged_bundle.py data/staging/<bundle-id> --index-id <bundle-id>
```

### 8. Smoke test before activation

- run the minimum smoke-query subset
- verify citation click-through
- confirm the currently active index is still unchanged
- interpret this as a runtime health gate, not the main retrieval-quality benchmark
- local entry point:

```powershell
python deployment/run_activation_smoke.py --index <bundle-id>
```

Retrieval quality remains governed by the Stage 10 benchmark suite. Stage 11 smoke only blocks cutover when the staged runtime cannot ingest, ground, or cite correctly.

### 9. Activate

- update `indexes/previous.txt`
- update `indexes/current.txt`
- record operator, time, and activated bundle ID
- archive the displaced current index metadata under `indexes/archive/`
- local entry point:

```powershell
python deployment/activate_index.py --index <bundle-id> --operator <operator-name>
```

### 10. Roll back if needed

- restore the previous pointer
- rerun the smoke subset
- record rollback time and operator
- archive the displaced current index metadata under `indexes/archive/`
- local entry point:

```powershell
python deployment/rollback_index.py --operator <operator-name>
```
