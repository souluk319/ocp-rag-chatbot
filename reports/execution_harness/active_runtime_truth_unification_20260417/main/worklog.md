# active_runtime_truth_unification_20260417

- kickoff: confirmed project drift is structural, not cosmetic; `active_manifest.json` still exposes `29` slugs while `playbook_documents.jsonl` and `chunks.jsonl` already materialize `174` official/derived books
- decision: stop letting viewer/control-room/serving trust `active_manifest` alone and move them onto one shared official runtime registry
- non-goal: this packet will not rewrite the one-click activation manifest format itself unless required; it will first remove manifest-only gating from consuming surfaces
- result: shared registry now merges `active_manifest + source_manifest + playbook_documents`, control-room approved runtime count is derived from that registry, and served viewer materialization now emits `174` docs viewers plus `29` active markdown viewers
