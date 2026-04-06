# Knowledge Platform MVP Plan

## 1. Purpose

This plan replaces the earlier ambiguous "workspace" direction with a stricter target:

- keep the existing OCP RAG chatbot working
- inspect the real data architecture first
- validate whether the current OCP 4.20 dataset can support study-grade source viewing
- implement the smallest viable code changes to turn the chatbot into a 16:9 knowledge/study platform MVP

This is not a pure UI redesign task.
This is a data/view-model integration task with a limited product-direction upgrade.

## 2. Product Understanding

The intended product is:

- `chatbot-first`
- `source-aware`
- `study-friendly`
- `16:9 desktop-ready`

The intended product is not:

- a document-first search workspace
- a raw chunk dump viewer
- a full multi-format Doc-to-Book platform yet
- a full Playbook execution engine yet

The main interaction should remain:

1. ask a question in chat
2. receive a readable grounded answer
3. inspect source tags under the answer
4. open the relevant source document/section in a right-side study panel

## 3. Execution Order

Read and execute the plan in this order:

1. [part-a-data-audit.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-a-data-audit.md)
2. [part-a-audit-report.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-a-audit-report.md)
3. [part-b-mvp-implementation.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-b-mvp-implementation.md)
4. [part-b-implementation-report.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-b-implementation-report.md)
5. [part-c-validation-and-demo.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-c-validation-and-demo.md)
6. [part-c-validation-report.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-c-validation-report.md)
7. [part-d-boundaries-and-next-step.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-d-boundaries-and-next-step.md)
8. [part-e-completion-status.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-e-completion-status.md)
9. [part-f-release-gate-report.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-f-release-gate-report.md)
10. [part-g-rebuild-next-epic.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-g-rebuild-next-epic.md)

## 4. Hard Rules

- Do not guess about data shape. Inspect real code and real artifacts first.
- Do not break the current RAG flow in the name of UI changes.
- Do not dump ugly retrieval chunks directly into the source panel if a more readable representation already exists.
- Do not over-build future Doc-to-Book features inside this MVP slice.
- Every major implementation change must have a test implication.

## 5. Immediate Deliverables

This MVP cycle must produce:

1. a data audit summary grounded in the current repository and artifact layout
2. a written audit report with evidence and implementation guardrails
3. a clear judgment on whether the current dataset already supports study-grade source viewing
4. the minimum backend support needed for source tags and source-view rendering
5. a chatbot-first 16:9 UI with a right-side source panel
6. real-query validation with at least 5 OCP-style questions
7. a short limitations list and the next step toward Doc-to-Book / Playbook evolution

## 6. Definition of Success

This cycle is successful only if all of the following are true:

- the chatbot still answers real OCP questions correctly
- source tags appear below assistant answers
- clicking a source tag opens the relevant source content on the right
- the right-side source panel is readable enough for study
- the UX still feels like a chatbot with source-study support, not a document search tool
- the implementation is small enough that future ingestion/platform work is still easy
