# runtime_graph_maintenance_guard_20260417 / main

- scope locked:
  - seal active runtime writer paths so graph refresh policy cannot be skipped after `chunks.jsonl` / `playbook_documents.jsonl` mutation
  - formalize a maintenance live smoke routine that refreshes graph fallback state and verifies `/api/health` plus `/api/chat`
- do not expand graph richness or add operator warning rules
- validation target:
  - known active writer paths route through one graph refresh contract
  - a regression test fails when a new writer path bypasses the contract
  - maintenance live smoke is callable from the canonical runtime entrypoint and leaves a report artifact
  - focused pytest subset and one live smoke command succeed
- implementation:
  - added `refresh_active_runtime_graph_artifacts()` so active runtime writer paths cannot refresh `chunks.jsonl` / `playbook_documents.jsonl` without also applying the graph artifact policy
  - routed `pipeline`, `runtime_catalog_library`, `translation_gold_promotion`, `curated_gold`, and hidden active path `topic_playbooks` through that one contract
  - added `maintenance-smoke` CLI + `runtime_maintenance_smoke.py`; command now fails closed when compact refresh, `/api/health`, `/api/chat`, and compact artifact exposure do not all succeed
- validation:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_ingestion_graph_sidecar.py tests\test_translation_gold_promotion.py tests\test_curated_gold.py tests\test_runtime_catalog_library.py tests\test_topic_playbooks.py tests\test_foundry_orchestrator.py tests\test_cli.py tests\test_runtime_maintenance_smoke.py -q` -> `48 passed in 13.12s`
  - fresh temp server on `8878` + `maintenance-smoke` succeeded; report written to `reports/build_logs/runtime_maintenance_smoke.json`
- deferred:
  - operator warning rules stay memo-only in this packet; freshness signal is exposed, but no alerting policy was implemented
