# pipeline_explain_layer_20260417 / main

- scope locked:
  - keep existing `Overview` and `Forensic`
  - add a user-facing `Explain` layer that summarizes why the answer came out this way
  - do not remove raw JSON, timings, score audit, or stage table from forensic surfaces
- validation target:
  - explain view shows only human-readable summary content
  - overview and forensic continue to exist
  - frontend tests and production build succeed
- implementation:
  - added `presentation-ui/src/components/workspaceExplain.ts` to derive question classification, rewrite rationale, search strategy, graph/rerank summary, and final evidence from existing trace payloads
  - added `Explain` tab to `WorkspaceTracePanel` and kept `Overview` / `Forensic` raw surfaces intact
  - explain view now groups the turn into `질문 해석`, `근거 검색`, `답변 결정`, `최종 근거`
  - added targeted vitest coverage for both the explain helper and the default explain render, and updated runtime UI contract assertions
- validation:
  - `cd presentation-ui; npm run test -- workspaceExplain` -> 2 files / 3 tests passed
  - `cd presentation-ui; npm run build` -> passed
  - `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_app_runtime_ui.py -q` -> 3 passed
