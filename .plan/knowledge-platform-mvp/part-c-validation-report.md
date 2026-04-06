# Part C Validation Report

## 1. Validation Goal

Validate the MVP against real question flows, not only static contracts.

This report separates:

- `UI/API smoke that passed`
- `real question themes that currently fail`

That split matters because the data/view-model path is valid, but runtime grounding quality is still affected by retrieval availability.

## 2. UI/API Smoke That Passed

Runtime smoke check:

- local server on `127.0.0.1:8781`
- `/api/health` returned `ok=true`
- `/api/chat` on `OCP가 뭐야?`
  - `response_kind = rag`
  - `citation_count = 2`
  - first citation contained `book_title = 아키텍처`
  - first citation `href = /docs/ocp/4.20/ko/architecture/index.html#architecture-custom-os_architecture`

Meaning:

- source tag payload is real
- right-panel viewer target is real
- human-readable document labeling is real

## 3. Direct Question Validation Against Part C Themes

Validation method:

- direct `Part3Answerer.answer(...)`
- real current settings from `.env`
- for the first citation, `_internal_viewer_html(...)` was checked

Question set used:

1. `Pod Pending 상태는 무엇을 의미해?`
2. `CrashLoopBackOff 문제를 어떻게 확인해?`
3. `oc login 사용법 알려줘`
4. `Pod lifecycle 개념 설명해줘`
5. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`

### 3.1 Results

Passed with grounded source-view:

- `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`
  - `response_kind = rag`
  - `citation_count = 1`
  - first citation book = `authentication_and_authorization`
  - first section = `9.6. 사용자 역할 추가`
  - viewer path resolved
  - internal viewer rendered readable section content

Failed to ground during current runtime:

- `Pod Pending 상태는 무엇을 의미해?`
- `CrashLoopBackOff 문제를 어떻게 확인해?`
- `oc login 사용법 알려줘`
- `Pod lifecycle 개념 설명해줘`

For those failed cases:

- `response_kind = rag`
- `citation_count = 0`
- warnings included:
  - `no context citations assembled`
  - `answer has no inline citations`
  - `vector search failed: Failed to fetch embeddings from http://100.99.152.52:8091/v1 using model 'dragonkue/bge-m3-ko'`

## 4. What This Means

Validated:

- the source-view UX path is real
- citation -> viewer mapping is real
- normalized section rendering is real
- right-panel study view is backed by real source data

Not yet validated for release:

- stable grounded coverage across broader operational question themes
- especially when vector retrieval is degraded

## 5. Current Interpretation

The MVP is now strong in this narrow sense:

- when citations are available, the source-study experience is grounded and readable

The MVP is not yet strong in this broader sense:

- it does not currently guarantee grounded coverage for all common OCP operational query themes under the present runtime conditions

## 6. Immediate Next Step

Before calling this demo-ready for broad OCP questions, the next validation-driven work item should be:

- retrieval robustness under vector endpoint failure

Practical direction:

1. investigate why BM25-only grounding is not rescuing the failed themes
2. add or tighten fallback retrieval behavior for operational and CLI questions
3. repeat the same 5-question validation set until all 5 produce grounded citations

## 7. 2026-04-06 Retrieval Robustness Follow-Up

Scope completed in this slice:

- relaxed the BM25-only clarification gate when low-score hits are still topically coherent
- added targeted query expansion and book routing for:
  - `oc login`
  - `Pod Pending`
  - `CrashLoopBackOff`
  - `Pod lifecycle`
- added regression tests for:
  - vector failure -> BM25 fallback
  - low-score coherent context retention
  - retrieval warning propagation

### 7.1 Updated Runtime Result

Re-run method:

- direct `Part3Answerer.answer(...)`
- real current `.env`
- vector endpoint still unavailable during the check

Updated result summary:

1. `Pod Pending ...`
   - `response_kind = rag`
   - `citation_count = 1`
   - top citation book = `cli_tools`
2. `CrashLoopBackOff ...`
   - `response_kind = rag`
   - `citation_count = 2`
   - top citation books = `support`, `support`
3. `oc login ...`
   - `response_kind = rag`
   - `citation_count = 1`
   - top citation book = `cli_tools`
4. `Pod lifecycle ...`
   - `response_kind = rag`
   - `citation_count = 2`
   - top citation books = `workloads_apis`, `workloads_apis`
5. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`
   - `response_kind = rag`
   - `citation_count = 1`
   - top citation book = `authentication_and_authorization`

Common warning still present during this validation:

- `vector search failed: Failed to fetch embeddings from http://100.99.152.52:8091/v1 using model 'dragonkue/bge-m3-ko'`

### 7.2 Interpretation After The Fix

What improved:

- the previous `citation_count = 0` failure set is now grounded even with vector retrieval down
- the fallback path is now visible in warnings instead of silently collapsing to ungrounded answers

What is still limited:

- `Pod lifecycle` is only partially grounded right now
- the current corpus path surfaces `initContainers` and Pod spec details, but not a clean end-to-end lifecycle explainer section for that query

Updated next priority:

1. keep the vector-failure regression suite green
2. improve concept-question source coverage/readability where the corpus is only partially aligned
3. validate the right-side source-study panel against the same 5 queries in-browser
