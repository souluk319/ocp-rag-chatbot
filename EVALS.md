# EVALS.md

## Purpose

This file defines the evaluation gates for the current
`chatbot-first 16:9 knowledge/study MVP`.

Use two levels only:

- `baseline`: good enough for experimentation and internal demo iteration
- `release`: required before calling the current MVP shipping-ready

This file covers the current OCP 4.20 dataset and current chatbot/runtime.
It does not define future multi-format Doc-to-Book gates yet.

## Evaluation Layers

The product is evaluated in five layers:

1. retrieval grounding
2. answer grounding and citation retention
3. multi-turn continuity
4. source-view usability
5. runtime/API health

These layers must be evaluated separately.
`retrieval hit`, `final citation`, and `right-panel source rendering` are not the same thing.

## Baseline Gates

All baseline gates must pass together.

### 1. Fixed Canary Set

Run this fixed five-query canary set against `/api/chat`:

1. `Pod Pending 상태는 무엇을 의미해?`
2. `CrashLoopBackOff 문제를 어떻게 확인해?`
3. `oc login 사용법 알려줘`
4. `Pod lifecycle 개념 설명해줘`
5. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`

Pass criteria:

- all 5 return HTTP `200`
- all 5 return `response_kind = rag`
- all 5 return at least 1 citation
- all citations expose a valid `href` or source-view target

### 2. Source Panel Readiness

For the same five canary answers:

- the first citation can be opened in the right-side source panel
- the source view resolves to readable document content
- the source view is not a raw debug dump or empty panel

### 3. Multi-turn Baseline

Run this flow in one session:

1. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`
2. `2번만 더 자세히`
3. `다음은?`

Pass criteria:

- the topic stays on RBAC
- the answer does not reset to an unrelated topic
- the follow-up remains step-aware

### 4. Clarification Boundary

Run one intentionally ambiguous query.
Example:

- `로그는 어디서 봐?`

Pass criteria:

- the assistant asks a short clarification instead of guessing

## Release Gates

All release gates include all baseline gates first.

### 1. Ops Safety

Run curated OCP operational questions including:

- RBAC user/group/serviceaccount distinction
- certificate expiry check
- etcd backup and restore
- terminating project/finalizer
- update or version-sensitive question

Pass criteria:

- no invented commands, flags, or procedures
- no namespace-scope answer for cluster-scope work
- no unsafe subject mutation guessed from follow-up

### 2. Citation Reliability

Pass criteria:

- every grounded answer in the release set retains at least 1 citation
- citation points to a relevant document or section
- citation can be reopened in the source panel
- `그 문서 기준으로 다시` style follow-up keeps the same branch or deliberately refreshes retrieval

### 3. Multi-turn Release Set

Required flows:

- step follow-up: `2번만 더`, `다음은?`
- reference follow-up: `그거 다시`, `그 문서 기준으로 다시`
- branch return: topic A -> topic B -> `아까 그 RBAC 문서 기준으로 다시`

Pass criteria:

- reference resolution remains correct
- the assistant does not drift into a different topic
- the answer does not silently drop grounding

### 4. Runtime Health

Pass criteria:

- `GET /` returns `200`
- `GET /api/health` returns `200`
- `/api/chat` canary set passes
- `/api/chat/stream` streams normally for at least one grounded query

### 5. Human Review

Release is not closed by tests alone.

One human browser-eye review is required for:

- chatbot-first feel is preserved
- source tags are visible and understandable
- the right-side panel feels like a study panel, not a debug inspector
- the page still fits a normal 16:9 desktop screen

## Failure Cases That Must Be Tracked

Track these explicitly during baseline and release reviews:

- ambiguous query answered without clarification
- clear query incorrectly forced into clarification
- wrong or irrelevant citation
- citation disappears even though retrieval found usable evidence
- follow-up drifts to a different topic
- command mutation guessed unsafely
- source panel opens but is unreadable

## Recommended Run Order

1. run unit tests
2. run the fixed five-query canary set
3. run one multi-turn flow
4. run one ambiguity flow
5. run source-panel click/open verification
6. for release only, run the full curated ops set and one human browser-eye review

## Suggested Commands

Use the current venv interpreter for all commands.

Examples:

```powershell
python -m unittest discover -s tests
python scripts/run_console.py --host 127.0.0.1 --port 8770 --no-browser
python scripts/check_runtime_endpoints.py
```

## Scope Note

These gates are for the current OCP 4.20 knowledge/study MVP only.
Future upload-first Doc-to-Book and Playbook features need a separate extension to this file.
