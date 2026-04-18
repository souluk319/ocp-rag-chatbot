# cleanup_surface_seams_20260418 / main

- scope locked:
  - cleanup packet only
  - no product renaming, no UI copy changes, no retrieval/runtime behavior changes
  - execute only three seams:
    1. `WorkspacePage.tsx` -> page shell plus feature islands
    2. `source_books.py` -> viewer builder vs source/meta resolver split
    3. `test_app_viewers.py` -> surface-based split
- validation target:
  - frontend build passes after island extraction
  - viewer pytest coverage still passes after source_books and viewer-test split
  - harness records companion cleanup lanes before closeout
- companion lanes:
  - explorer `McClintock`: WorkspacePage island seam audit
  - worker `Ramanujan`: source_books.py and test_app_viewers.py seam audit
- implementation notes:
  - `source_books.py`는 cleanup packet 동안 compatibility barrel로 유지했다.
  - viewer payload/render path는 `source_books_viewer_payloads.py`, source/meta resolver path는 `source_books_viewer_resolver.py`로 분리했다.
  - `tests/test_app_viewers.py`는 compatibility shim으로 축소하고, collector는 `routes / citations / runtime` 세 surface로 분리했다.
  - `WorkspacePage.tsx`는 controller를 유지한 채 `WorkspaceHeader.tsx`와 `WorkspaceViewerPanel.tsx` render island를 분리했다.
- validation:
  - `cd presentation-ui; npm run build`
  - `.\.venv\Scripts\python.exe -m pytest tests\test_app_viewers.py tests\test_app_viewers_routes.py tests\test_app_viewers_citations.py tests\test_app_viewers_runtime.py -q`
