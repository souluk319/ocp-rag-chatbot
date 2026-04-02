# PART3_PLAN.md

## Goal

Turn verified retrieval results into grounded Korean answers with usable citations.

## Inputs

- retrieval function
- retrieved chunks and metadata
- LLM endpoint

## Outputs

- RAG response function
- citation mapping structure
- minimum answer test results

## Steps

### Step 1. Build context assembly

- choose top chunks
- remove obvious duplicates
- preserve source traceability

### Step 2. Define answer contract

- answer in Korean
- stay grounded in retrieved evidence
- distinguish direct answer from extra guidance

### Step 3. Connect LLM endpoint

- define request format
- define timeout and retry behavior
- log prompt inputs at a safe debug level if needed

### Step 4. Implement citation formatting

- map generated answer to source metadata
- preserve document, section, and anchor references

### Step 5. Connect viewer links

- convert source metadata into internal viewer targets
- ensure each citation can open the right Korean document location

### Step 6. Build minimum answer test set

- test concept questions
- test operational questions
- test follow-up questions
- inspect hallucinations and citation mismatches

## Exit Criteria

Part 3 is ready when:

- Korean answers are grounded in retrieved evidence
- citations are visible and traceable
- minimum question set behaves predictably

## Notes

- Do not optimize for style before correctness.
- Good answer fluency does not compensate for bad evidence.
