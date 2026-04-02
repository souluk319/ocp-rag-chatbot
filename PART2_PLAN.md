# PART2_PLAN.md

## Goal

Build and validate the retrieval layer separately from answer generation.

## Inputs

- normalized docs
- chunk records
- Qdrant vectors
- BM25 corpus

## Outputs

- retrieval function or API
- per-query retrieval logs
- top-k benchmark results

## Steps

### Step 1. Define query preprocessing

- trim obvious noise
- normalize whitespace and punctuation
- expand simple high-value OCP aliases if needed

### Step 2. Add basic rewrite

- rewrite follow-up or short questions into retrieval-friendly standalone queries
- keep rewrite behavior minimal and inspectable

### Step 3. Implement vector retrieval

- query Qdrant
- return ranked chunks with scores and metadata

### Step 4. Implement BM25 retrieval

- query local text corpus
- return ranked chunks with identity mapping

### Step 5. Implement hybrid ranking

- combine vector and BM25 candidates
- rank with a simple, explainable policy first
- avoid premature complexity

### Step 6. Add retrieval logging

- save query
- save rewrite result
- save top-k candidates
- save source and anchor references

### Step 7. Build top-k verification set

- define a small question set
- mark expected source documents or chunks
- verify whether correct evidence appears in top-k

### Step 8. Measure retrieval quality

- check hit@k
- inspect false positives
- inspect false negatives
- separate retrieval failure from answer failure

## Exit Criteria

Part 2 is ready when:

- the system retrieves plausible evidence for core questions
- top-k logs are inspectable
- retrieval quality can be measured without involving answer generation

## Notes

- Keep retrieval explainable.
- Do not hide weak retrieval behind good answer wording.
