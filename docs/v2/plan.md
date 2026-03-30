# v2 Rewrite Plan

## Branch intent

`rewrite/opendoc-v2` is a clean reset branch for a new chatbot. It does not inherit the v1 runtime, UI, or document-processing stack.

## Product target

Build a closed-network OCP operations assistant that:

- ingests official OCP documentation and approved internal guidance
- uses OpenDocuments as the RAG platform baseline
- answers in Korean with clear citations
- supports controlled document refresh for air-gapped deployment

## Phase 0: Reset the repository

- remove the v1 runtime and generated data from this branch
- define the v2 repository layout
- document the external repositories used during development

## Phase 1: Rebuild document onboarding

- create the source manifest
- create the metadata schema
- define normalization rules for official and internal documents
- package collected content in a repeatable way

## Phase 2: Validate OpenDocuments

- connect the local OpenDocuments workspace
- ingest a small OCP subset
- confirm citation behavior and Korean query handling

## Phase 3: Add OCP-specific policies

- source trust ordering
- version preference rules
- operations mode and study mode
- conservative answer rules when evidence is incomplete

## Phase 4: Closed-network refresh flow

- collect document deltas outside the air-gapped environment
- produce an approval bundle
- import and reindex inside the target environment
- preserve rollback history for document and index versions

## Phase 5: Evaluation

- define OCP operations questions
- verify answer quality, source grounding, and version correctness
- add red-team scenarios before production use
