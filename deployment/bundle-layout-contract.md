# Stage 11 Bundle Layout Contract

## Purpose

Stage 11 needs one stable bundle shape so export, approval, transfer, import, and rollback all refer to the same artifact layout.

## Outbound bundle root

Each outbound bundle lives under:

- `data/packages/outbound/<bundle-id>/`

Required layout:

```text
data/packages/outbound/<bundle-id>/
  manifest.json
  approval.json
  checksums.sha256
  manifests/
    source-manifest.yaml
    normalized-manifest.json
    previous-approved-baseline.json
  documents/
    ... normalized text payloads ...
  views/
    ... generated HTML citation views ...
  reports/
    diff-summary.json
```

## Inbound bundle root

After transfer, the same bundle must appear under:

- `data/packages/inbound/<bundle-id>/`

Relative paths and file names must remain unchanged.

## Staging layout

After inbound validation, the bundle expands into:

```text
data/staging/<bundle-id>/
  documents/
  views/
  manifests/
  reports/
```

Only the staging directory may feed reindexing.

## Index layout

Indexes are built only inside the closed network:

```text
indexes/
  current.txt
  previous.txt
  <bundle-id>/
  archive/
  failed/
```

Bundles never carry prebuilt indexes from the connected side.

## Required file semantics

- `manifest.json`
  Must conform to `deployment/bundle-schema.yaml`.
- `approval.json`
  Must conform to `deployment/approval-record-schema.yaml`.
- `checksums.sha256`
  Must cover every transferred file except itself.
- `manifests/source-manifest.yaml`
  The source-scope contract used when the bundle was created.
- `manifests/normalized-manifest.json`
  The normalized corpus manifest used to populate this bundle.
- `manifests/previous-approved-baseline.json`
  The approved baseline used to compute diff actions.
- `reports/diff-summary.json`
  Human-readable change summary for review and import validation.

## Rules

1. `bundle_id` is immutable once the bundle is emitted.
2. `documents/` and `views/` paths must match the paths recorded in `manifest.json`.
3. Checksum verification must complete before staging or activation.
4. `approval.json` must exist before inbound import starts.
5. Reimport is allowed only if checksum and schema validation still pass.
