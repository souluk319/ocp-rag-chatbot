# private_lane_boundary_hardening_20260418

- scope locked: fail-close private runtime exposure for incomplete/default envelope and unreviewed approval state
- preserve explicit internal review surfaces where possible; do not redesign customer-pack product flow
- validation locked: `.\.venv\Scripts\python.exe -m pytest tests\test_private_lane_smoke.py tests\test_retrieval_query_core.py tests\test_app_intake_ui.py tests\test_server_chat.py -q`
- companion lanes:
  - explorer_boundary_map
  - worker_test_impact
  - reviewer_security
- implemented:
  - shared private runtime boundary helper
  - runtime eligibility stamps on private corpus manifest
  - fail-close retrieval gating for selected private drafts without runtime-eligible manifest
  - intake API sanitizes private corpus payload and supports explicit boundary overrides for smoke/admin flows
  - private lane smoke upgraded to approved boundary baseline
- validation:
  - `.\.venv\Scripts\python.exe -m py_compile src\play_book_studio\intake\private_boundary.py src\play_book_studio\intake\private_corpus.py src\play_book_studio\app\intake_api.py src\play_book_studio\retrieval\intake_overlay.py src\play_book_studio\retrieval\retriever_search.py src\play_book_studio\app\private_lane_smoke.py tests\test_retrieval_query_core.py tests\test_app_intake_ui.py tests\test_private_lane_smoke.py`
  - `.\.venv\Scripts\python.exe -m pytest tests\test_private_lane_smoke.py tests\test_retrieval_query_core.py tests\test_app_intake_ui.py tests\test_server_chat.py -q`
  - `.\.venv\Scripts\python.exe -m pytest tests\test_cli.py -k private_lane_smoke -q`
