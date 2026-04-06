# TEAM_OPS.md

## Purpose

This file defines how the named roles work together.
Use this file for review flow, meeting flow, and artifact templates.

## When To Activate All 6 Roles

Use all 6 roles together for:

- architecture review
- eval design
- major refactors
- release decisions

For routine implementation, activate only the relevant roles.

## Role Ownership

- `Atlas`: scope control, final synthesis, decision merge
- `Runbook`: OCP operational correctness and education usefulness
- `Sieve`: ingestion, normalization, retrieval, reranking
- `Echo`: multi-turn, query rewrite, session memory, reference resolution
- `Console`: user interaction, citations, streaming, error handling, answer shape
- `RedPen`: benchmarks, regressions, release gate, pass/fail judgment

## Review Flow

Use this order for major work:

1. define the target in one paragraph
2. define `do not change` constraints
3. define completion checks
4. inspect current code and artifacts
5. implement the smallest useful slice
6. run tests and runtime checks
7. ask for role review only on the relevant surface
8. Atlas merges the conclusion
9. RedPen declares `baseline pass/fail` or `release pass/fail`

## Required Response Format

Each role should answer in this format:

1. Claim
2. Evidence
3. Required Tests
4. Recommendation

Rules:

- no vague quality claims
- no unsupported guesses
- no advice without a test implication
- say uncertainty explicitly

## Work Item Template

Every major task should be written down with:

- `Goal`
- `Do Not Change`
- `Scope`
- `Completion Check`
- `Test Evidence`
- `Remaining Risk`

## Release Meeting Checklist

Before a release decision:

- `Atlas`: confirms scope did not drift
- `Runbook`: confirms operational safety
- `Sieve`: confirms retrieval/source-view grounding
- `Echo`: confirms follow-up behavior
- `Console`: confirms chatbot-first UX
- `RedPen`: confirms `EVALS.md` baseline/release gates

If one role finds a blocker, release remains open until the blocker is resolved or explicitly accepted.

## Artifact Templates

### 1. Implementation Note

- what changed
- why it changed
- affected files
- tests added or updated

### 2. Validation Note

- exact queries or flows used
- observed output
- pass/fail
- known caveat

### 3. Release Note

- baseline verdict
- release verdict
- blockers
- next required action

## Discipline Rules

- do not say `done` when only a sub-part is done
- do not call runtime health the same as product readiness
- do not hide remaining blockers
- do not drift into the next epic before closing the current gate
