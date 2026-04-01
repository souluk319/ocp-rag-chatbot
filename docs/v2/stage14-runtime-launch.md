# Stage 14 Runtime Launch

## Purpose

Stage 12 proved that the live runtime path can work.

Stage 14 makes that path operator-usable by turning it into a repeatable launch flow instead of a smoke-only script.

## What Stage 14 adds

- `deployment/start_runtime_stack.py`
- `deployment/operator-runbook-stage14.md`

## Scope

Stage 14 is intentionally narrow.

It focuses on:

- launch repeatability
- active-index wiring
- startup health
- viewer availability

It does not try to redesign retrieval or expand the corpus by itself.

## Launch contract

The launcher resolves:

- active index from `indexes/current.txt`
- active Stage 11 workspace
- runtime workspace under `workspace/stage12/<active-index>`
- active vector dimensions from the live LanceDB schema

Then it starts:

1. local bridge
2. OpenDocuments server
3. product runtime gateway

The launcher injects `OD_SERVER_BASE_URL` into the gateway process, so the gateway path can be managed even when that value is not permanently written to `.env`.

For local Windows operation, the recommended wrapper is:

```powershell
powershell -ExecutionPolicy Bypass -File deployment/start_local_runtime.ps1
```

The locked local path is:

- bridge: `18101`
- OpenDocuments: `18102`
- gateway/UI: `8000`

## Exit criteria

Stage 14 is complete when:

- one command can start the runtime stack
- startup health checks pass
- gateway viewer click-through passes
- the launcher writes a reproducible report and log set

## Validation evidence

The current local validation was executed with:

```powershell
python deployment/start_runtime_stack.py --hold-seconds 10
```

Observed results:

- `startup_pass = true`
- active index: `baseline-openshift-docs-p0`
- active vector dimensions: `1024`
- embedding baseline: `BAAI/bge-m3`
- gateway viewer click-through returned `200 text/html`

Evidence paths:

- `data/manifests/generated/stage14-runtime-launch-report.json`
- `data/manifests/generated/stage14-runtime-launch-logs/bridge.log`
- `data/manifests/generated/stage14-runtime-launch-logs/opendocuments.log`
- `data/manifests/generated/stage14-runtime-launch-logs/gateway.log`

## Current warnings

The current launch evidence includes two important notes:

1. OpenDocuments logs a model-plugin embed probe failure and falls back to stub-model startup behavior during boot.
2. OpenDocuments reports that the upstream web UI is not built in the current local runtime path.

Interpretation:

- Stage 14 is still considered complete because the operator launch contract, gateway health, and citation-viewer path all passed.
- Retrieval quality remains governed by Stage 9 and Stage 10.
- If we later want the upstream OpenDocuments web UI itself, that is a separate packaging/build concern, not a Stage 14 launch blocker.

## Relationship to previous stages

- Stage 11 remains the authority for refresh / activate / rollback
- Stage 12 remains the serving-path parity proof
- Stage 14 adds the operator-facing launch discipline on top of those stages
