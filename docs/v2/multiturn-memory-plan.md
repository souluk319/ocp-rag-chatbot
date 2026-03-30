# Stage 7 Multi-turn Memory and Follow-up Rewrite

## Purpose

Stage 7 turns multi-turn support into an explicit design and validation asset instead of leaving it to whatever the underlying model happens to remember.

The main idea is simple:

- keep bounded structured session state
- classify each turn as standalone, follow-up, or topic shift
- rewrite referential follow-up turns into retrieval-ready standalone queries
- preserve version and topic continuity unless the user clearly changes them

## Why this stage matters

The first presentation feedback explicitly called out weak multi-turn behavior.

Stage 6 also showed a concrete miss:

- `RB-011` failed to keep the update context through the follow-up turn

Stage 7 exists to close that gap before we broaden the corpus or polish the UI.

## Design constraints

1. Multi-turn state must be bounded.
2. Version continuity must be explicit.
3. Topic shifts must reset the right parts of memory.
4. Follow-up rewrite must be inspectable.
5. Endpoint and model wiring must remain environment-driven.

Stage 7 does **not** introduce hardcoded LLM endpoint or model values.

Runtime-sensitive values stay in environment variables such as:

- `LLM_ENDPOINT`
- `LLM_MODEL`
- `MAX_HISTORY_TURNS`
- `SESSION_TTL_SECONDS`

## Session memory contract

The Stage 7 session state tracks:

- `session_id`
- `active_topic`
- `source_dir`
- `active_version`
- `reference_doc_path`
- `retrieval_hints`
- `turn_count`
- `last_updated_epoch`
- `recent_turns`

The implementation is intentionally small and conservative:

- `recent_turns` is bounded by `MAX_HISTORY_TURNS`
- session expiry is controlled by `SESSION_TTL_SECONDS`
- if the session expires, we reset instead of guessing

## Turn classification

Each incoming user turn is classified as one of:

- `standalone`
- `follow_up`
- `topic_shift`

### Standalone

Use this when:

- the conversation has no active session context
- the turn introduces a clear fresh topic

### Follow-up

Use this when:

- the turn contains referential language such as `그 전에`, `그럼`, `같은 흐름`
- the turn is short but clearly depends on the active topic
- the turn stays within the same topic family

### Topic shift

Use this when:

- the user explicitly pivots with phrases such as `아니`, `다른 질문`
- the new turn introduces a different topic family than the active one

## Rewrite strategy

The rewrite target is not a polished user answer.

It is a retrieval-ready query that keeps:

- the current user wording
- the active source family
- the active topic identifier
- the active version
- the nearest reference document when the turn is a follow-up
- topic hints that stabilize retrieval against English source material

Example shape:

- original question
- `source <source_dir>`
- `topic <topic_id>`
- `OpenShift <version>`
- `last_document <doc_path>`
- `hints <retrieval hints>`

This is intentionally transparent and debuggable.

## Version continuity rules

The state starts at:

- `DEFAULT_VERSION` if present
- otherwise `4.x`

Rules:

1. If the user mentions `4.16`, `4.17`, and so on, that version becomes active.
2. If the user does not mention a version, the active version is preserved.
3. If a different explicit version appears, we record a `version_switch` issue.
4. Version changes are allowed, but they must not be silent.

## Topic reset rules

When a topic shift is detected:

- carry the version forward unless the user changes it
- replace `active_topic`
- replace `source_dir`
- replace `retrieval_hints`
- replace `reference_doc_path` when a new document anchor is known

This avoids contaminating the new turn with stale topic hints from the previous conversation.

## Stage 7 validation assets

Stage 7 adds four concrete assets:

- `app/multiturn_memory.py`
- `docs/v2/multiturn-memory-plan.md`
- `eval/multiturn-scenario-schema.yaml`
- `eval/benchmarks/p0_multiturn_scenarios.json`
- `eval/multiturn_rewrite_report.py`

## Scenario design

The first Stage 7 dataset intentionally uses:

- one 5-turn update-preparation scenario
- one 5-turn disconnected-to-support reset scenario

These cover:

- stable follow-up continuity
- version carry-over
- version switch
- topic shift reset
- source-dir continuity

## Exit criteria for Stage 7

Stage 7 is considered complete when:

1. the session memory contract is documented
2. the follow-up rewrite logic is implemented in a reusable module
3. at least one 5-turn scenario can be replayed end to end
4. the replay report shows whether classification, source-dir continuity, topic continuity, and version continuity passed
5. no LLM endpoint or model values are newly hardcoded in the Stage 7 assets

## What Stage 7 does not solve yet

Stage 7 does not itself fix:

- reranker regressions from Stage 6
- citation correctness gaps from Stage 6
- company bearer-token provisioning

Those remain part of later stages.
