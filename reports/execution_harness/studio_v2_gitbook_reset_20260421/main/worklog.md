# studio_v2_gitbook_reset_20260421 / main

## kickoff

- goal: rebuild `/studio-v2` as a distinct GitBook/Starlight-inspired reader shell with PBS studio sidecar, not a legacy workspace variant
- acceptance:
  - `/studio` remains untouched
  - `/studio-v2` no longer imports `WorkspacePage.css`
  - `/studio-v2` no longer uses `WorkspaceViewerPanel`
  - reader-first center canvas feels materially different from legacy workspace
  - existing overlay contracts for `note`, `ink`, and `edited_card` remain usable
- non_goals:
  - deleting or rewriting `/studio`
  - changing runtime truth / overlay persistence contracts
  - shipping full inline editing
- validation:
  - `npm --prefix presentation-ui run build`
  - browser smoke for `/studio-v2`

## lane_notes

- `Nash`: legacy dependency audit and rewrite boundary
- `Tesla`: visual grammar and reference translation
- `Mendel`: runtime/viewer reusable primitives and extraction map
- `Schrodinger`: presentational shell scaffold under `presentation-ui/src/pages/studio-v2/`
