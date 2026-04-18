# Packet Execution Checklist

## Packet A

- Lock source-first OCP 4.20 baseline.
  - Evidence: `manifests/ocp420_source_first_full_rebuild_manifest.json`
  - Evidence: `reports/build_logs/ocp420_full_rebuild_manifest_report.json`
  - Evidence: `data/wiki_runtime_books/full_rebuild_manifest.json`
- Run materialization and confirm corpus/runtime counts and figure/diagram asset coverage.
  - Evidence: `reports/build_logs/ocp420_full_rebuild_report.json`
  - Evidence: `reports/build_logs/ocp420_full_rebuild_materialization_report.json`
  - Evidence: `data/wiki_runtime_books/active_manifest.json`
- Confirm active library visibility and served viewer output for OCP 4.20 Korean runtime.
  - Evidence: `reports/build_logs/ocp420_one_click_runtime_report.json`
  - Evidence: `reports/build_logs/active_runtime_viewer_serving_report.json`
  - Evidence: `artifacts/runtime/served_viewers/docs/ocp/4.20/ko/`
  - Evidence: `artifacts/runtime/served_viewers/playbooks/wiki-runtime/active/`
- Confirm retrieval-side evidence before closing the packet.
  - Evidence: `reports/build_logs/retrieval_landing_precision_report.json`
  - Evidence: `artifacts/retrieval/retrieval_eval_report.json`
- Validation commands:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_retrieval_runtime_core.py tests\test_retrieval_runtime_graph_trace.py -q`
  - `cd presentation-ui; npm run build`
  - `.\.venv\Scripts\python.exe -m play_book_studio.cli --help`

## Packet B

- Lock the multiturn source manifest before execution.
  - Evidence: `manifests/demo_multiturn_scenarios.jsonl`
- Snapshot the executed scenario set into the packet folder before or with the run.
  - Evidence target: `reports/multiturn/ocp420_corpus_multiturn_20260418/manifest_snapshot.jsonl`
- Execute all 5 scenarios and record scenario-level verdicts.
  - Evidence target: `reports/multiturn/ocp420_corpus_multiturn_20260418/scenario_summary.json`
- Record per-turn metrics and failures with one durable trace file each.
  - Evidence target: `reports/multiturn/ocp420_corpus_multiturn_20260418/turn_metrics.jsonl`
  - Evidence target: `reports/multiturn/ocp420_corpus_multiturn_20260418/failure_cases.jsonl`
- Validation commands:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_demo_multiturn_scenarios.py tests\test_app_chat_api_multiturn.py -q`

## Closeout Gates

- Packet A closes only if the build logs, active manifest, served viewer roots, and retrieval report all agree on an OCP 4.20 active baseline.
- Packet B closes only if the manifest still carries 5 scenarios, each executes 6 turns, and scenario plus turn metrics are written under `reports/multiturn/ocp420_corpus_multiturn_20260418/`.
