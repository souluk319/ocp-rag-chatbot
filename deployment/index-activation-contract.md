# Stage 11 Index Activation Contract

## Purpose

Stage 11 must define how a newly built index becomes active without destroying the last known-good state.

## Pointer files

Tracked pointers:

- `indexes/current.txt`
- `indexes/previous.txt`

`indexes/current.txt` names the currently active index ID.

`indexes/previous.txt` names the most recent previously active index ID.

## Index states

- `uninitialized`
- `staged`
- `active`
- `previous`
- `failed`

## Activation rule

An index may become active only if all of the following are true:

1. inbound bundle validation passed
2. staged file counts match the bundle manifest
3. reindex completed without fatal errors
4. smoke queries passed
5. citation click-through passed on the staged index

## Pointer update sequence

1. Read `indexes/current.txt`.
2. Write its previous value into `indexes/previous.txt`.
3. Write the new `bundle-id` into `indexes/current.txt`.
4. Record activation metadata in the import report.

## Rollback rule

Rollback is allowed only to the value stored in `indexes/previous.txt`.

Rollback requires:

1. restoring `indexes/current.txt`
2. recording the operator and timestamp
3. rerunning the smoke-query subset against the restored index

## Archive rule

At least one previous active index must remain available under:

- `indexes/archive/`

Failed build artifacts may be moved under:

- `indexes/failed/`

## Minimum smoke checks before activation

- one update-preparation query
- one disconnected query
- one troubleshooting query
- citation click-through on at least one result from each group
