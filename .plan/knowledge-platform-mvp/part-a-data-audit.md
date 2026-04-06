# Part A. Data Audit

## Status

Completed findings are written in:

- [part-a-audit-report.md](C:/Users/soulu/cywell/ocp-rag-chatbot-v2/ocp-rag-chatbot-rebuild/.plan/knowledge-platform-mvp/part-a-audit-report.md)

## 1. Goal

Inspect the current backend, artifact layout, and metadata before changing product behavior.

This part exists to answer one question:

`Can the existing OCP 4.20 dataset already support a good study-grade source viewer, or do we need a light derived layer?`

## 2. Chapter A1. Audit Targets

Inspect these code and data areas first:

- `src/ocp_rag/ingest`
- `src/ocp_rag/retrieval`
- `src/ocp_rag/answering`
- `src/ocp_rag/app`
- `src/ocp_rag/shared/settings.py`
- current external artifacts directory resolved from `.env`

Expected artifact categories to inspect:

- raw source html
- normalized section-level documents
- retrieval chunks
- BM25 corpus or equivalent lexical index input
- embeddings / vector-store inputs
- answer/retrieval logs if useful

## 3. Chapter A2. Mandatory Questions

The audit must answer all of the following from real files:

1. What forms of data currently exist?
2. Is retrieval text and source-view text already separated?
3. What metadata is available on retrieval results and citations?
4. How much source structure survived preprocessing?
5. Can the current dataset support study-grade source viewing now?
6. If partially, what is the smallest missing layer?

## 4. Chapter A3. Evidence Collection Method

For each answer above, collect evidence from:

- code paths that create or read artifacts
- concrete artifact file shapes
- returned citation / retrieval payload fields
- viewer or server helpers that already exist

Evidence must be grounded in:

- file paths
- field names
- actual data shape
- runtime behavior where needed

## 5. Chapter A4. Required Findings Format

The audit write-up must summarize:

### A4.1 Current Data Representations

- source-level raw content
- normalized section/doc records
- retrieval chunks
- citation-friendly fields

### A4.2 Source Viewer Feasibility

- `yes`
- `partial`
- or `no`

and why.

### A4.3 Preprocessing Damage Assessment

Judge whether the current preprocessing mainly preserved:

- headings
- section path
- anchors
- lists
- code blocks
- tables

or destroyed too much for human viewing.

### A4.4 Smallest Data-Layer Change

Name the smallest useful change that would unlock:

- source tags
- right panel source view
- section jump / highlight
- readable study panel

## 6. Chapter A5. Completion Criteria

Part A is complete only when:

- the audit is based on current repo files, not memory
- the team can say exactly what data is being reused
- the MVP implementation path is chosen from the audit result

## 7. Part A Output

Produce:

- a short audit summary for implementation notes
- a decision on whether a derived source-view model is required
- an explicit list of reusable fields and reusable artifact files
