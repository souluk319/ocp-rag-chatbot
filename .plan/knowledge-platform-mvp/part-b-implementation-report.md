# Part B Implementation Report

## 1. Scope Used

This batch followed the Part A audit result and stayed inside the smallest viable MVP path.

Chosen implementation path:

- `reuse existing readable source representation`

Not chosen:

- new ingestion pipeline
- new viewer artifact
- document-first workspace redesign

## 2. What Was Reused

Reused backend pieces:

- `normalized_docs.jsonl` as the readable source-view backing layer
- `viewer_path` and `anchor` from citations
- existing internal viewer renderer in `src/ocp_rag/app/server.py`
- existing chat-first `chat panel + side panel` structure in `src/ocp_rag/app/static/index.html`

Reused frontend flow:

- source tags below assistant answers
- right-side panel opening on citation click
- hidden/collapsible side panel

## 3. What Was Added

### 3.1 Backend

Changed file:

- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\app\server.py`

Added:

- citation payload enrichment with `book_title`
- cached title lookup based on normalized docs
- payload builder now resolves human-readable document labels without changing ingestion artifacts

Reason:

- source tags and source cards should show readable document names, not only `book_slug`

### 3.2 Frontend

Changed file:

- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\app\static\index.html`

Added or refined:

- display helpers for `book_title` and section label rendering
- answer-level source tags now prefer readable document labels
- source cards in the side panel now prefer readable document labels
- document panel meta now shows readable book/section context
- source/document/trace tabs were renamed toward a Korean-first UI
- answer meta chips now prefer `출처` wording over purely debug-oriented copy

Product intent:

- keep chat primary
- make the source panel feel like a study surface
- avoid another document-search style takeover

### 3.3 Tests

Changed file:

- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\tests\test_app_ui.py`

Added:

- payload test proving citations are enriched with `book_title`
- updated static UI expectations for readable source labels

## 4. Changed Files For This Slice

- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\app\server.py`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\src\ocp_rag\app\static\index.html`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\tests\test_app_ui.py`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\.plan\knowledge-platform-mvp\README.md`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\.plan\knowledge-platform-mvp\part-a-data-audit.md`
- `C:\Users\soulu\cywell\ocp-rag-chatbot-v2\ocp-rag-chatbot-rebuild\.plan\knowledge-platform-mvp\part-a-audit-report.md`

## 5. Verification

Unit and contract checks:

- `python -m unittest tests.test_app_ui tests.test_answering_context`
- result: passed

Frontend syntax check:

- extracted `<script>` from `index.html`
- `node --check`
- result: passed

Whole-suite regression:

- `python -m unittest discover -s tests`
- result: `160` tests passed, `2` skipped

Runtime smoke:

- local server on `127.0.0.1:8781`
- `/api/health` returned `ok=true`
- `/api/chat` for `OCP가 뭐야?` returned `response_kind=rag`
- same payload returned `citation_count=2`
- first citation carried `book_title=아키텍처`

## 6. MVP Status After Part B

Current status:

- chat-first layout preserved
- source tags exist under answers
- source tags can open a right-side source viewer
- source viewer can use readable source content backed by normalized sections
- human-readable document labels are now available in citation payloads

## 7. Known Gaps Still Visible

1. Runtime retrieval reliability is not fully stable.
- vector endpoint failures were observed during validation
- some real questions still produce `0` citations

2. The source-study panel is improved, but still shares space with debug-oriented trace surfaces.
- acceptable for MVP iteration
- should be tightened further before a polished demo freeze

3. No dedicated viewer artifact exists yet.
- acceptable for this MVP
- a thin derived viewer index remains a future hardening option, not a blocker
