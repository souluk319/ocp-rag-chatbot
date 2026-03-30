# Stage 11 Manifest Lineage Contract

## Purpose

Stage 11 uses several manifest types. This contract fixes their relationship so diffs, approvals, and rollback decisions stay reproducible.

## Manifest types

### Source manifest

Path:

- `configs/source-manifest.yaml`

Purpose:

- defines trusted sources
- defines include and exclude rules
- defines collection roots

Identity field:

- `version`

### Normalized corpus manifest

Example path:

- `data/manifests/generated/openshift-docs-p0.json`

Purpose:

- records the exact normalized corpus built from the source manifest
- records document IDs, checksums, metadata, and viewer paths

Identity field:

- `manifest_id`

### Approved baseline manifest

Path:

- `data/manifests/approved-baseline.json`

Purpose:

- stores the currently approved baseline used for future bundle diffs

Identity fields:

- `manifest_id`
- `approved_at`

### Bundle manifest

Example path:

- `data/packages/outbound/<bundle-id>/manifest.json`

Purpose:

- records one refresh bundle built from a normalized manifest and an approved baseline

Identity fields:

- `bundle_id`
- `source_manifest_version`
- `baseline_manifest_id`

## Lineage rule

Allowed lineage:

```text
source-manifest.yaml
  -> normalized-manifest.json
      -> approved-baseline.json
          -> bundle manifest
              -> staged import
                  -> active index pointer
```

## Diff rule

Bundle diffs are always computed as:

- `normalized corpus manifest` minus `approved baseline manifest`

They are never computed directly from raw source snapshots.

## First-cycle rule

When no approved baseline exists yet:

- `data/manifests/approved-baseline.json` remains explicitly uninitialized
- the first approved seed must be created from a validated normalized corpus manifest
- that seeded manifest becomes the next `baseline_manifest_id`

## ID stability rule

These identifiers must stay stable once emitted for an approved artifact:

- `manifest_id`
- `bundle_id`
- `document_id`
- `section_id`
