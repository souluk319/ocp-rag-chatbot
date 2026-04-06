# Part F. Release Gate Report

## 1. Scope

This report records one release-gate run against [EVALS.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/EVALS.md).

The run covers:

- unit-test health
- runtime health
- fixed five-query canary set
- selected release questions
- one RBAC multi-turn flow
- one stream endpoint smoke

## 2. Automated Verdict

- `baseline`: pass
- `release`: pending human review

## 3. Automated Evidence

### 3.1 Unit Tests

- `176 passed`
- `2 skipped`

### 3.2 Runtime Health

- `GET /` -> `200`
- `GET /api/health` -> `200`

### 3.3 Fixed Canary Set

Independent-session run on `/api/chat`:

1. `Pod Pending 상태는 무엇을 의미해?`
2. `CrashLoopBackOff 문제를 어떻게 확인해?`
3. `oc login 사용법 알려줘`
4. `Pod lifecycle 개념 설명해줘`
5. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`

Observed result:

- all `200`
- all `response_kind = rag`
- all returned at least `1` citation
- all first citation `href` values resolved with `200`

### 3.4 Selected Release Questions

Observed result:

- `OCP API 서버 인증서 만료 확인 방법 알려줘`
  - grounded answer
  - `citation_count = 1`
- `etcd 백업과 복구 절차를 단계별로 설명해줘`
  - grounded answer
  - `citation_count = 1`
- `프로젝트가 Terminating 에서 안 끝날 때 finalizer 확인 방법 알려줘`
  - grounded answer
  - `citation_count = 1`
- `로그는 어디서 봐?`
  - short clarification
  - no unsupported guess

### 3.5 Multi-turn Flow

One-session RBAC flow:

1. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`
2. `2번만 더 자세히`
3. `다음은?`

Observed result:

- topic stayed on RBAC
- follow-up stayed step-aware
- grounding remained present

### 3.6 Stream Smoke

- `/api/chat/stream` returned `200`
- trace lines streamed in order:
  - `request_received`
  - `route_query`
  - `retrieval`
  - `normalize_query`
  - `rewrite_query`
  - `bm25_search`
  - `vector_search`
  - `fusion`

### 3.7 Browser Automation Smoke

Viewport:

- `1600 x 900`

Observed result:

- initial shell state was `chatbot-first`
  - shell class: `shell inspector-hidden`
  - chat panel width was dominant
  - side panel width was `0` before open
- after one grounded answer:
  - answer rendered normally
  - source tag appeared under the assistant answer
- after clicking the source tag:
  - shell class changed to `shell`
  - right-side panel opened
  - active tab changed to `문서`
  - iframe source resolved to the cited OCP document
- after the follow-up query `그 문서 기준으로 다시 정리해줘`:
  - the document frame remained pinned
  - assistant follow-up answer rendered normally

Fix applied during this smoke:

- `resetPipelineTrace()` no longer clears the currently open document during a normal follow-up send
- session reset still clears the panel as before

## 4. Remaining Release Blocker

The remaining blocker is not an automated failure.
It is the required human browser-eye review from [EVALS.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/EVALS.md):

- chatbot-first feel is preserved
- source tags are visible and understandable
- right-side source panel feels like a study panel
- the page still fits a normal 16:9 desktop screen

## 5. Team Verdict

Role review summary:

- `Atlas`: `release candidate`, final approval pending browser-eye review
- `Console`: `baseline pass`, `release candidate`, UX sign-off pending
- `RedPen`: automatic gates passed, final sign-off pending human review

## 6. Current Judgment

The current product state is good enough for:

- internal demo
- iteration
- baseline MVP freeze

The current product state is not yet fully closed for:

- final release sign-off

until one human browser review is recorded.
