# Part B. MVP Implementation

## 1. Goal

Build the smallest useful 16:9 knowledge/study platform MVP without breaking the current RAG chatbot.

The product shape for this part is:

- main area = chat
- right area = source viewer
- source viewer hidden/collapsible by default
- answer readability improved
- source tags shown under each assistant answer

## 2. Chapter B1. Non-Negotiable Boundaries

Do now:

- improve answer readability
- show source tags under answers
- open relevant source content in a right-side panel
- reuse current OCP 4.20 data
- add the lightest missing source-view support only if necessary

Do not do now:

- full multi-format ingestion
- full Doc-to-Book pipeline generalization
- playbook engine
- hot reload indexing
- large architecture rewrite

## 3. Chapter B2. Backend Work Order

### B2.1 Source Metadata Reuse

Re-check what is already available in:

- retrieval hits
- answer citations
- internal viewer helpers
- normalized docs or equivalent section-level records

### B2.2 Minimum Source-View API

Implement only the smallest necessary backend support for:

- source tag rendering data
- opening a source document/section by a stable source reference
- best-effort section jump / anchor targeting
- readable source-panel content

### B2.3 Source-View Model Decision

Choose exactly one implementation path:

1. `reuse existing readable source representation`
2. `derive a minimal grouped source view from current normalized data`
3. `derive a minimal grouped source view from chunk data only`

Prefer the earliest viable option in that order.

## 4. Chapter B3. Frontend Work Order

### B3.1 Chat Stays Primary

The left/main side must remain the chatbot.

Required outcomes:

- readable typography
- stable streaming UX
- source chips under assistant answers
- no document-first takeover of the layout

### B3.2 Right Source Panel

Required outcomes:

- hidden or collapsed by default
- opens when a source chip is clicked
- shows readable source content
- feels like a study panel, not a debug dump

### B3.3 16:9 Behavior

The layout should use desktop width well, but without changing product identity.

Interpretation:

- `16:9 optimization` means using horizontal space effectively
- it does not mean turning chat into a side feature

## 5. Chapter B4. Smallest Useful UI Contract

The UI contract for this slice is:

1. user asks in chat
2. assistant streams readable answer
3. answer ends with source chips
4. clicking a source chip opens right-side panel
5. panel shows source title, section context, and readable content
6. user can keep chatting while the source panel stays visible

## 6. Chapter B5. Completion Criteria

Part B is complete only when:

- current RAG still works
- answers remain grounded
- source chips appear consistently
- source panel opens from real citation/source data
- source content is readable enough for study

## 7. Part B Output

Produce:

- minimal backend additions or adapters
- minimal frontend changes
- changed-file list
- notes on what was reused versus newly added
