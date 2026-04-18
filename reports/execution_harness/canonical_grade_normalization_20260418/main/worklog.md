# canonical_grade_normalization_20260418

- backend canonical grade source in `data_control_room.py` still emitted `Silver Draft`, `Mixed Review`, `English Only`, `Blocked`, `Unknown`
- runtime buckets were already 3-tier in `data_control_room_buckets.py`, so authority drift existed between release surfaces
- Workspace rendered grade as part of metadata text instead of a first-class badge
- Playbook Library already had explicit badges on primary operational cards, but several secondary surfaces still displayed plain-text grade
- explorers confirmed the minimal safe path: normalize exposed grade only, keep raw `content_status / review_status / translation_status` intact
- implemented `Bronze / Silver / Gold` normalization in backend authority and swapped stale fallback labels to `Bronze`
- added explicit grade badges to Workspace outline and Source Books list
- normalized remaining Library grade spots to badge form and normalized client-side grade comparisons to 3-tier semantics
- focused validation passed: `py_compile`, `pytest tests/test_app_data_control_room.py tests/test_app_runtime_ui.py -q`, `npm run build`
