# Live Runtime Gateway

## Purpose

Stage 11 closed the refresh and activation mechanics. The next runtime gap was that the validated Stage 7 and Stage 9 logic still lived mostly in offline evaluation paths.

The runtime gateway closes that gap by placing a thin product-owned layer in front of the OpenDocuments HTTP server.

## What the gateway does

The gateway is implemented in:

- `app/ocp_runtime_gateway.py`
- `app/runtime_gateway_support.py`
- `app/runtime_source_index.py`

It owns:

1. session continuity for unmodified clients
2. follow-up rewrite before the request reaches OpenDocuments
3. policy-shaped source reranking after OpenDocuments retrieval
4. citation normalization against the active Stage 11 index manifest
5. conservative answer shaping for operator-facing output

## Why it exists

OpenDocuments already provides:

- retrieval
- generation
- streaming
- conversation persistence

But our validated v2 requirements also need:

- OCP-specific multi-turn memory
- OCP-specific retrieval policy
- stable citation links backed by our manifest lineage
- env-driven runtime control

Those concerns belong in the product-owned layer, not in the upstream repository.

## Request path

```text
Client
  -> OCP Runtime Gateway
    -> Session memory lookup
    -> follow-up rewrite
    -> upstream /api/v1/chat or /api/v1/chat/stream
    -> source normalization against active index manifest
    -> policy rerank
    -> answer guardrail shaping
  -> Client
```

## Session strategy

The gateway uses this priority order:

1. `conversationId` from request body
2. `ocp_runtime_session` cookie
3. upstream-created conversation from `POST /api/v1/conversations`

This lets the existing OpenDocuments web UI keep multi-turn continuity even before it is modified to persist `conversationId` explicitly.

## Source normalization strategy

OpenDocuments returns search results with runtime `sourcePath` values.

The gateway resolves those results against the active Stage 11 manifest:

- active pointer: `indexes/current.txt`
- index manifest: `indexes/<current>/manifests/index-manifest.json`
- detailed staged manifest when available: `staged_manifest_path`

That lookup restores:

- `document_path`
- `source_dir`
- `category`
- `version`
- `trust_level`
- `viewer_url`
- section anchor when the heading matches a known section

## Policy application strategy

The gateway does not replace Stage 9 and Stage 10 as the quality authority.

Instead it applies the already validated policy logic in the runtime path:

- query analysis
- follow-up candidate rescue
- OCP source reranking
- conservative answer shaping

This means Stage 9 policy behavior is no longer isolated to offline reports.

## Runtime contracts

Required env values for the gateway path:

- `OD_SERVER_BASE_URL`
- `OD_COMPANY_BASE_URL`
- `OD_CHAT_MODEL`
- `OD_EMBEDDING_MODEL`

Optional:

- `OD_COMPANY_BEARER_TOKEN`
- `OD_DEFAULT_MODE`
- `OD_BRIDGE_TIMEOUT_SECONDS`

## Current scope

This gateway is the runtime integration layer for Stage 12 preparation.

It does not yet replace the OpenDocuments web UI. Instead it makes the backend behavior ready so that Stage 12 UI work can point to a stable, policy-aware runtime path.
