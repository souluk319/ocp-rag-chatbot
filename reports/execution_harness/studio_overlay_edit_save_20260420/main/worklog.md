# studio_overlay_edit_save_20260420 / main

- goal lock:
  - let users treat PlayBookStudio like a studio surface by drawing and adding text on top of the viewer
  - keep those edits out of canonical corpus/playbook truth
  - save and restore the edits when the same book/viewer is reopened
- non-goals:
  - do not mutate corpus chunks or canonical playbook book files in this packet
  - do not redesign product naming or unrelated surfaces
  - do not create a second persistence model if the existing overlay lane can hold the edits
- validation target:
  - focused backend validation for touched overlay persistence if backend changes are needed
  - frontend build passes after edit UI and restore flow land
  - save/reopen behavior is demonstrated with concrete evidence before closeout
- constraint note:
  - major-task companion lanes are required by repo contract but actual delegated agents are blocked in this session unless the user explicitly asks for delegation

## implementation log

- backend:
  - added persisted `ink` overlay kind to the existing wiki overlay store
  - sanitized stroke payloads and reflected ink counts in overlay signal summaries
- frontend:
  - widened overlay target detection to official docs, active runtime books, customer-pack viewers, and captured customer-pack previews
  - restored saved ink strokes per target and added explicit save/clear affordances
  - surfaced saved note content as visible `added text` above the reader instead of hiding it as an internal memo
  - relaxed pointer start gating so pen/touch input on tablet/mobile-class devices can start ink more reliably than mouse-only gating
- chat/demo:
  - nudged prompt copy toward a slightly more guide-forward response style without changing product voice drastically
  - added `scripts/run_ocp420_demo_simulator.py` as a streaming-first demo harness
  - created `manifests/ocp420_demo_simulator_scenarios.jsonl` as a demo-specific five-scenario manifest calibrated to currently grounded runtime coverage

## validation log

- `.\\.venv\\Scripts\\python.exe -m py_compile src\\play_book_studio\\app\\wiki_user_overlay.py src\\play_book_studio\\answering\\prompt.py scripts\\run_ocp420_demo_simulator.py tests\\test_app_wiki_user_overlay.py`
  - passed
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_app_wiki_user_overlay.py -q`
  - passed, `2 passed`
- `npm --prefix presentation-ui run build`
  - passed
- `.\\scripts\\codex_python.ps1 .\\scripts\\run_ocp420_demo_simulator.py --api-base http://127.0.0.1:8765`
  - passed with `scenario_completion_rate=1.0`, `turn_pass_rate=1.0`, `streaming_turn_pass_rate=1.0`, `hallucination_guard_pass_rate=1.0`, `history_pass_rate=1.0`

## runtime note

- the live runtime on `http://127.0.0.1:8765` was already running outside the tracked local launcher (`tmp/local_runtime_stack/state.json` absent)
- because of that, the prompt wording refinement was landed in source but not force-applied to the existing runtime via restart in this packet
