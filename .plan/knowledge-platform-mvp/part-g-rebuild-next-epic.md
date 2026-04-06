# Part G. Rebuild Next Epic

## 1. Goal

The current branch is `rebuild/ko-rag-core-v2`.

That means the next phase should not drift into random feature work.
The next phase should strengthen the actual `core-v2` identity.

## 2. Team-Synthesized Priority

The next epic should run in this order:

1. `Branch-aware grounding core`
2. `Canonical core-v2 cleanup`
3. `Release gate hardening`

## 3. Epic 1. Branch-Aware Grounding Core

### Why First

- false-positive clarification still hurts trust the fastest
- grounded follow-up is the real product differentiator
- `rebuild` should mean stronger reference/citation/session control, not just prettier UI

### Scope

- reduce false-positive clarification on clear operational questions
- strengthen branch-aware citation replay
- strengthen topic return flows
  - `RBAC -> cert -> RBAC`
- keep step, command, citation, and source-panel state aligned

### Required Tests

- clear ops questions go directly to `rag`
- ambiguous questions alone go to `clarification`
- `2번만 더 자세히`, `다음은?`, `그 명령 다시`
- `그 문서 기준으로 다시`
- branch return with preserved grounding

## 4. Epic 2. Canonical Core-v2 Cleanup

### Why Second

- the branch name says `core-v2`, so canonical product layers must become the real public surface
- source-view and retrieval still need a cleaner contract

### Scope

- finish removing legacy `part1~4` surface from public docs/scripts/import paths
- make `src/ocp_rag/*` the only canonical product surface
- separate retrieval artifacts from source-view artifacts more explicitly
- keep `.env` artifact paths as the single source of truth

### Required Tests

- new script entrypoints work
- README examples match real commands
- no accidental repo-root artifact recreation
- source-view still resolves from the canonical dataset

## 5. Epic 3. Release Gate Hardening

### Why Third

- baseline is already passing
- next growth phase needs stronger regression protection before bigger ingestion work starts

### Scope

- harden `EVALS.md` release set
- keep browser-eye checklist short and repeatable
- preserve `citation/source/right-panel` consistency
- preserve `chatbot-first` contract during future UI work

### Required Tests

- fixed canary 5
- selected release ops questions
- one browser automation smoke
- one human browser-eye checklist

## 6. Not In This Epic

These are important, but they are not next:

- full multi-format upload platform
- full Doc-to-Book ingestion generalization
- full Playbook execution engine

Those come after the core-v2 behavior is locked.

## 7. Working Rule

For the next epic, use this sentence as the guardrail:

`더 많이 붙이는 것보다, clear question -> grounded retrieval -> stable follow-up -> consistent source-view 를 더 단단하게 만든다.`
