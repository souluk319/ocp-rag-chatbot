# retrieval_flow_docs_20260417 / main

- scope locked:
  - add one human-readable retrieval explainer doc
  - explain repo structure at the level needed to understand why `src` and `scripts` both exist
- do not change runtime behavior or retrieval policy in this packet
- validation target:
  - `docs/retrieval_flow.md` exists
  - retrieval stages and main file entrypoints are discoverable from one doc
- implementation:
  - added `docs/retrieval_flow.md` as a reference explainer rather than a root active contract
  - documented why `src` and `scripts` both exist, which files own the runtime spine, and the end-to-end retrieval sequence from normalize to `RetrievalResult`
- validation:
  - `Test-Path docs\retrieval_flow.md` -> `True`
  - `Select-String -Path docs\retrieval_flow.md -Pattern '^## '` -> section headings found for repo structure, entry files, retrieval flow, debug signals, and cleanup candidates
