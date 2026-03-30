# Air-Gap Update Flow

## Goal

Move approved document updates from a connected collection environment into the closed network without allowing direct external synchronization in production.

## Flow

1. Collect outside the closed network
- mirror or pull approved document sources
- normalize selected content into `data/normalized/`
- emit a manifest into `data/manifests/`

2. Build an outbound bundle
- compare the current manifest with the last approved baseline
- package changed normalized files and metadata into `data/packages/outbound/<bundle-id>/`

3. Approve the bundle
- confirm source scope, metadata validity, and removal impact
- record reviewer and approval timestamp

4. Transfer into the closed network
- copy the approved bundle into `data/packages/inbound/<bundle-id>/`
- validate checksums and manifest schema

5. Stage documents for indexing
- expand the approved bundle into a versioned staging directory
- do not overwrite the currently active index

6. Reindex
- build a new index under `indexes/<bundle-id>/`
- run smoke queries before activation

7. Activate
- update `indexes/current.txt` to point at the approved index version

8. Roll back if needed
- restore the previous index pointer
- keep at least one previous approved bundle and index version available

## Operational Rules

- No internet sync inside the closed network
- No index activation without an approved manifest
- No destructive replacement of the currently active index before validation
- Every bundle must be versioned and reproducible
