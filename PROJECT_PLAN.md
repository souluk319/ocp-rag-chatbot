# PROJECT_PLAN.md

## Overview

This document defines the full execution plan for the closed-network Korean OCP RAG chatbot.

The work is split into 4 parts:

1. Preprocessing Pipeline
2. Retrieval Pipeline
3. Answer Pipeline
4. UI / Integration / Demo

The reason for this split is simple:

- Part 1 is the heaviest foundation work
- Part 2 validates retrieval separately from answer generation
- Part 3 turns retrieval into a real RAG response flow
- Part 4 turns the system into a usable demo product

## Part 1. Preprocessing Pipeline

### Scope

- collect Korean `html-single` documents
- extract article body
- normalize content
- extract metadata
- test chunking strategy
- generate embeddings
- store vectors in Qdrant
- save BM25 corpus artifacts

### Outputs

- raw HTML
- normalized docs
- chunks
- vector DB
- corpus metadata
- preprocessing log

### Detailed execution plan

See `PART1_PLAN.md`.

## Part 2. Retrieval Pipeline

### Scope

- query preprocessing
- basic rewrite
- vector retrieval
- BM25 retrieval
- hybrid ranking
- top-k verification

### Outputs

- retrieval API or retrieval function
- per-query retrieval logs
- retrieval benchmark results

### Detailed execution plan

See `PART2_PLAN.md`.

## Part 3. Answer Pipeline

### Scope

- build context from retrieval results
- call LLM
- generate Korean answers
- format citations
- connect citation viewer links

### Outputs

- RAG response function
- citation mapping structure
- minimum question-set answer results

### Detailed execution plan

See `PART3_PLAN.md`.

## Part 4. UI / Integration / Demo

### Scope

- chat UI
- Korean answer rendering
- citation click opens internal Korean document
- demo scenario verification

### Outputs

- minimum UI
- demo question set
- end-to-end runnable demo

### Detailed execution plan

See `PART4_PLAN.md`.

## Execution Order

Work in this order:

1. Finish Part 1 foundation
2. Prove Part 2 retrieval quality on a small high-value subset
3. Add Part 3 answer generation on top of verified retrieval
4. Wrap with Part 4 UI and demo flows

Do not expand scope early.
If a later part blocks on an unstable earlier part, fix the earlier part first.

## Current Focus

Current active focus is **Part 1**.

The immediate goal is not a full chatbot.
The immediate goal is a stable document pipeline that can support later retrieval and citations.
