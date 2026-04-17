# runtime_graph_compact_integration_20260417 / main

- scope locked: connect compact graph regeneration to the active maintenance path that refreshes runtime `chunks.jsonl` and `playbook_documents.jsonl` outside full ingestion
- do not expand relation richness or change unrelated retrieval scoring
- degradation rule to implement:
  - fresh compact artifact: runtime may use compact relations
  - stale/missing/invalid compact artifact: runtime must ignore it and fall back to bounded local relations
- validation target:
  - promotion path refreshes compact artifact automatically
  - health/runtime payload exposes compact freshness state
  - end-to-end test confirms `source refresh -> compact regenerate -> runtime uses compact artifact`
- implementation summary:
  - selected `translation_gold_promotion` as the first maintenance integration point because it mutates active `chunks.jsonl` and `playbook_documents.jsonl` outside full ingestion
  - promotion now auto-runs compact regeneration and reports `graph_compact_refresh` without aborting the source refresh on compact write failure
  - runtime now refuses stale compact artifacts and degrades to bounded `playbook_documents` fallback
  - health payload and runtime report now expose compact artifact freshness and degrade mode
- validation evidence:
  - `.venv\Scripts\python.exe -m pytest tests\test_translation_gold_promotion.py tests\test_retrieval_graph_runtime.py tests\test_runtime_report.py tests\test_foundry_orchestrator.py -q` -> `27 passed`
  - `.venv\Scripts\python.exe -m pytest tests\test_translation_gold_promotion.py -k compact -q` -> `1 passed, 2 deselected`
