# official_source_fail_closed_fallback_gate_20260418 / main

- active docs re-read: `AGENTS.md`, `PROJECT.md`, `EXECUTION_HARNESS_CONTRACT.md`, `RUNTIME_ARCHITECTURE_CONTRACT.md`
- confirmed `manifest` contract was source-first, but `collector.collect_entry()` still auto-fetched HTML via `entry.source_url`
- confirmed `scripts/materialize_ocp420_full_rebuild_books.py` was still exporting existing `gold_manualbook_ko/playbooks/*.json` plus HTML fallback figures, so it could contaminate a clean rebuild
- tightened active docs to state `published HTML/PDF fallback requires explicit user approval`
- added settings toggles:
  - `PBS_OFFICIAL_HTML_FALLBACK_ALLOWED` default `false`
  - `PBS_ALLOW_STALE_FULL_REBUILD_EXPORT` default `false`
- blocked `collector.collect_entry()` for `source-first` entries unless explicit approval exists
- updated `build_ocp420_full_rebuild_manifest.py` to fail-close when repo source is missing and fallback is not approved
- blocked `materialize_ocp420_full_rebuild_books.py` by default until real repo AsciiDoc parser binding lands
- validation:
  - `py_compile: ok`
  - `pytest tests/test_ingestion_manifest.py -q -> 9 passed`
  - doc sanity -> ok
  - strict manifest script -> blocked with `8` entries pending fallback approval
  - stale full rebuild materializer -> blocked
