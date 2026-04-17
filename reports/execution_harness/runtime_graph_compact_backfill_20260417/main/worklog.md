# runtime_graph_compact_backfill_20260417 / main

- scope locked: replace the ad hoc compact-artifact regeneration script with a repo-supported command
- do not change runtime retrieval behavior, UI, or unrelated retrieval tuning
- validate with focused CLI/ingestion tests plus a real `graph-compact` CLI smoke
- implementation intent:
  - add a streaming artifact-derived compact payload builder in `graph_sidecar.py`
  - expose it through `play_book_studio.cli graph-compact`
  - keep output schema identical to the existing compact artifact contract
- implementation summary:
  - added `build_graph_sidecar_compact_payload_from_artifacts()` to rebuild the compact graph payload directly from `chunks.jsonl` and `playbook_documents.jsonl`
  - added `write_graph_sidecar_compact_from_artifacts()` as the reusable writer entrypoint
  - added `graph-compact` to the canonical CLI so compact backfill is no longer an ad hoc inline script
- validation summary:
  - `.venv\Scripts\python.exe -m pytest tests\test_cli.py tests\test_ingestion_graph_sidecar.py tests\test_ingestion_pipeline.py tests\test_retrieval_graph_runtime.py tests\test_retrieval_runtime_graph_trace.py -q` => `35 passed`
  - `.\.venv\Scripts\python.exe -m play_book_studio.cli graph-compact` rewrote `artifacts/retrieval/graph_sidecar_compact.json`
  - command output reported `174 books`, `7003 relations`, and relation group counts for `shared_k8s_objects/shared_operator_names/shared_error_strings/shared_verification_hints`
  - regenerated artifact size after smoke: `2534246 bytes`
