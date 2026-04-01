# App Scope

This directory will hold the product-specific layer for the v2 assistant.

Expected responsibilities:

- OpenDocuments integration points
- OCP-specific prompt and retrieval policy wiring
- any thin glue code needed for deployment in the target environment
- runtime gateway behavior that sits in front of OpenDocuments without modifying the upstream repository

Current runtime-owned entry points:

- `app/opendocuments_openai_bridge.py`
- `app/ocp_runtime_gateway.py`
- `app/runtime_gateway_support.py`
- `app/runtime_source_index.py`

Current live runtime baseline responsibilities:

- bridge the approved company endpoint into an OpenAI-compatible local runtime path
- preserve session continuity and follow-up rewrite on the live HTTP path
- normalize runtime sources against the active Stage 11 manifest
- serve HTML citation targets through `/viewer/...`
