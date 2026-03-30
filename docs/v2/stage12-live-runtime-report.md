# Stage 12 Live Runtime Report

## Purpose

Stage 12 exists to prove that the validated offline logic from Stage 7, Stage 9, and Stage 10 still behaves correctly on the real serving path:

- bridge
- OpenDocuments HTTP server
- product-owned gateway
- active Stage 11 index

This stage does **not** redefine retrieval quality authority. Stage 9 and Stage 10 remain the retrieval-quality gate. Stage 12 proves serving-path parity and click-through behavior.

## Implemented runtime additions

The Stage 12 baseline added:

- a live viewer route on the product gateway: `GET /viewer/{source_id}/{document_path}`
- env-driven bridge auth forwarding control via `OD_FORWARD_CLIENT_AUTH`
- env-driven embedding-dimension compatibility via `OD_EMBEDDING_DIMENSIONS`
- a reproducible local live smoke runner: `deployment/run_live_runtime_smoke.py`

## Why the embedding-dimension compatibility layer was needed

The active Stage 11 baseline index was built with LanceDB vectors at dimension `1024`.

The embedding baseline is now standardized on `BAAI/bge-m3`, which produces `1024`-dimension dense vectors and fits the active Stage 11 baseline without the earlier 384-to-1024 mismatch.

The compatibility layer remains in place so the live runtime can still defend itself if a future staged index and the currently configured embedding path drift out of alignment.

Stage 12 therefore:

- detects the active index vector dimension from the live LanceDB schema
- injects that dimension into the bridge and OpenDocuments runtime
- pads or truncates bridge-produced embeddings to the active index dimension when a mismatch is detected

This is a runtime compatibility step, not a retrieval-quality claim.

## Live smoke command

```powershell
python deployment/run_live_runtime_smoke.py
```

Authoritative report:

- `data/manifests/generated/stage12-live-runtime-report.json`

Smoke inputs:

- `deployment/live_runtime_smoke_cases.json`

## Verified outcomes

The current live smoke report records:

- bridge `/health`: pass
- bridge `/v1/models`: pass
- OpenDocuments `/api/v1/health`: pass
- gateway `/health`: pass
- first streamed turn: pass
- second streamed follow-up turn: pass
- cookie-backed session continuity: pass
- stable `conversationId` across turns: pass
- follow-up rewrite contains `last_document`: pass
- citation viewer route click-through: pass

## What Stage 12 proves

Stage 12 now proves that:

1. the approved company-backed bridge can serve the live OpenDocuments runtime path
2. the product gateway can preserve session continuity for unmodified clients
3. follow-up rewrite is present on the real HTTP path
4. citations returned on the live path resolve through the product-owned HTML viewer route
5. the serving stack can be recreated locally without hardcoding company endpoint or model values into source files

## What Stage 12 does not prove

Stage 12 does **not** replace:

- Stage 9 policy benchmark results
- Stage 10 evaluation and red-team results

The live smoke is intentionally narrow. It verifies serving mechanics and click-through behavior, not full retrieval-quality acceptance.

## Interpretation

The Stage 12 baseline is now good enough to say:

- the live runtime path is operational
- the citation viewer path is operational
- the serving stack preserves the expected follow-up rewrite contract

Further UI polish is optional product work, not a blocker for understanding the end-to-end serving path.
