# runtime_graph_compact_fallback_20260417 / main

- scope locked: generate compact graph artifact and teach retrieval local fallback to consume it before full sidecar
- do not change UI, answerer structure, or unrelated retrieval tuning
- validate with focused ingestion/retrieval tests and live smoke if the compact artifact is materialized for the current runtime
- design choice:
  - compact artifact schema keeps `books + relations + summary` only
  - request path prefers compact artifact for relation index, falls back to full sidecar only when compact is absent and full sidecar is safely readable
  - current runtime backfill was materialized from `data/gold_corpus_ko/chunks.jsonl` + `data/gold_manualbook_ko/playbook_documents.jsonl`
- implementation summary:
  - added `graph_sidecar_compact_path`
  - ingestion now writes `artifacts/retrieval/graph_sidecar_compact.json` alongside the existing full sidecar
  - retrieval local fallback now loads compact relations first and reports their count in `summary.sidecar_relation_count`
- validation summary:
  - `.venv\Scripts\python.exe -m pytest tests\test_ingestion_graph_sidecar.py tests\test_ingestion_pipeline.py tests\test_retrieval_graph_runtime.py tests\test_retrieval_runtime_graph_trace.py -q` => `29 passed`
  - current runtime compact artifact materialized: `174 books`, `7003 relations`, `2534246 bytes`
  - restarted `8765` with current code and compact artifact present
  - live `POST /api/chat` with `OpenShift 아키텍처를 설명해줘` completed in `7391.3 ms`
  - live retrieval trace showed `adapter_mode=local_sidecar`, `fallback_reason=neo4j_unhealthy:connect failed: timed out|sidecar_eager_load_skipped:file_too_large:7876461484`, `summary.sidecar_relation_count=7003`
  - live `/api/health` remained `ok: true` after compact artifact smoke
