# workspace_card_edit_bundle_20260420 / main

- kickoff lock
  - goal: keep original viewer/corpus immutable and save user edits as section-card-level modified documents
  - scope: viewer active-card tracking, edited-card overlay bundle save/restore, favorites-based edited filter
  - non-goals: source mutation, corpus mutation, new top-level surface naming
  - validation: `pytest tests/test_app_wiki_user_overlay.py -q`, `npm --prefix presentation-ui run build`

- companion lane note
  - repo contract marks this as a major task
  - session rule blocks unauthorized sub-agent spawning, so blocked companion skeletons are recorded in manifest

- baseline findings
  - current multi-view save target is first-section heuristic, not actual visible card tracking
  - note and ink are stored independently, so there is no single edited-card truth bundle yet
  - favorites/signals currently cannot isolate edited items

- implementation notes
  - added `edited_card` overlay kind as the section-card-level modified document bundle
  - kept source HTML immutable and moved user text/ink/style into the overlay bundle only
  - changed viewer section targeting from first-card parse fallback to live active-card tracking inside the shadow-root viewer
  - kept the existing `Favorites` surface and added an `edited` filter instead of adding a new top-level surface

- validation
  - `pytest tests/test_app_wiki_user_overlay.py -q` -> `3 passed`
  - `python -m py_compile src/play_book_studio/app/wiki_user_overlay.py tests/test_app_wiki_user_overlay.py` -> pass
  - `npm --prefix presentation-ui run build` -> pass
  - live backend on `http://127.0.0.1:8765` initially rejected `edited_card` because runtime was stale; after `docker compose restart backend`, save/list/remove smoke passed
