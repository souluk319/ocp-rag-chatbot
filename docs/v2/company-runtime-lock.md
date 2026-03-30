# Stage 8 Company Runtime Lock

## Purpose

Stage 8 locks the integrated v2 runtime to the approved company path and removes silent drift to convenience defaults.

The target operating path is:

- OpenDocuments uses a local OpenAI-compatible bridge
- the bridge proxies chat requests to the approved company endpoint
- the bridge serves embeddings locally for the current validation setup
- the current embedding baseline is `BAAI/bge-m3` so Korean questions and English source documents share one multilingual embedding space
- endpoint and model values come from `.env` or process environment, never from committed code defaults

## Why this stage exists

Stage 6 was allowed to use a local fallback because the company chat token was not yet available. That was acceptable for plumbing validation, but it is not acceptable as a stable runtime contract.

Stage 8 therefore makes these rules explicit:

1. runtime endpoint and model settings must come from environment variables
2. the approved company path is the default operating mode
3. local chat fallback is diagnostic-only and must be enabled explicitly
4. secrets stay outside Git

## Runtime contract

### OpenDocuments-facing variables

These are used by the OpenDocuments config template.

- `OPENAI_BASE_URL`
- `OPENAI_API_KEY`
- `OD_CHAT_MODEL`
- `OD_EMBEDDING_MODEL`
- `OD_EMBEDDING_DIMENSIONS`

`OPENAI_BASE_URL` should point to the local bridge that exposes `/v1/chat/completions` and `/v1/embeddings`.

### Bridge-facing variables

These are used by the Python bridge and the integrated runtime check.

- `OD_COMPANY_BASE_URL`
- `OD_COMPANY_BEARER_TOKEN`
- `OD_ALLOW_LOCAL_CHAT_FALLBACK`
- `OD_BRIDGE_TIMEOUT_SECONDS`

### Compatible project-level fallbacks

If `OD_*` values are not set, the bridge can read these project-level names:

- `LLM_EP_COMPANY_URL`
- `LLM_EP_COMPANY_MODEL`
- `LLM_EP_COMPANY_BEARER_TOKEN`
- `LLM_ENDPOINT`
- `LLM_MODEL`
- `EMBEDDING_MODEL`

This keeps Stage 8 compatible with the existing project `.env` layout without hardcoding values in source files.

Current baseline:

- chat model: company-provided `Qwen/Qwen3.5-9B`
- embedding model: `BAAI/bge-m3`
- embedding dimensions: `1024`

## Approved behavior

### Default mode

Default mode is `company-only`.

That means:

- the bridge reads endpoint and model settings from env
- no local fallback answer is used unless explicitly enabled
- health output shows configuration state without exposing secrets

### Diagnostic mode

Diagnostic mode is enabled only when:

- `OD_ALLOW_LOCAL_CHAT_FALLBACK=1`

This mode is allowed only for temporary local validation. It is not the release target.

## Validation steps

Stage 8 is considered complete when:

1. `app/opendocuments_openai_bridge.py` no longer hardcodes company endpoint or model values
2. `deployment/opendocuments-stage6.config.template.ts` fails fast if required env vars are missing
3. `deployment/check_runtime_contract.py` reports the runtime contract state without printing secrets
4. `.env.example` documents the env contract without including real values
5. local fallback is off by default

## Evidence files

- `app/runtime_config.py`
- `app/opendocuments_openai_bridge.py`
- `deployment/opendocuments-stage6.config.template.ts`
- `deployment/opendocuments-stage6.env.template`
- `deployment/check_runtime_contract.py`
- `.env.example`

## Operational note

The current integrated path still allows the bridge to pass through the incoming `Authorization` header when no company bearer token is configured locally.

This is intentional because:

- some environments inject auth at the caller layer
- we must not force secrets into Git-tracked files

The runtime contract only requires that the approved company endpoint and model selection are env-driven and that local fallback is opt-in.
