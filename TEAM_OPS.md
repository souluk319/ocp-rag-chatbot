# TEAM_OPS.md

## Purpose

This file defines the lightweight review flow for the six stable AGENTS roles.

## When To Use All 6 Roles

Use all six roles together for:

- architecture review
- eval design
- major refactors
- release decisions

For routine implementation, use only the relevant perspectives.

## Review Flow

1. Atlas frames scope and decision to be made.
2. Runbook checks OCP domain correctness and usefulness.
3. Sieve checks ingestion, chunking, retrieval, and ranking implications.
4. Echo checks follow-up handling and session behavior.
5. Console checks output shape, citations, and UX implications.
6. RedPen sets required tests and pass/fail implications.

## Output Template

Each role should report in this format:

1. Claim
2. Evidence
3. Required Tests
4. Recommendation

Keep reports short and concrete.

## Meeting Artifacts

Store moving evaluation and decision details in:

- `EVALS.md`
- `VENDOR_NOTES.md`
- benchmark report files under `part2/`

Do not turn review flow into ceremony.
The goal is clear decisions with observable test impact.
