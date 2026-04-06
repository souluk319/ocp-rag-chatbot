# Part D. Boundaries And Next Step

## 1. Goal

Keep the MVP small, defend the product direction, and prepare a clean next step toward future platform evolution.

## 2. Chapter D1. What This MVP Proves

This MVP should prove:

- the existing OCP 4.20 corpus can support more than raw QA
- grounded answers and study-grade source viewing can coexist
- the chatbot can evolve toward a knowledge platform without becoming a document search product

## 3. Chapter D2. What This MVP Does Not Yet Prove

This MVP does not yet prove:

- generalized multi-format ingestion
- polished Doc-to-Book transformation
- upload-time document normalization workflows
- playbook/checklist execution
- live re-indexing or tenant-style platform operation

## 4. Chapter D3. Immediate Follow-Up After MVP

The recommended next step after this slice is:

1. keep the vector-failure fallback tests and validation set green
2. improve partially grounded concept coverage, especially questions like `Pod lifecycle`
3. validate the right-side source-study panel against the same 5 questions in-browser
4. then formalize a reusable source-view model
5. then define Doc-to-Book requirements from the current OCP source-view lessons
6. only after that design upload-path contracts for `pdf`, `ppt/pptx`, `html`, and text formats
7. only then expand toward Playbook mechanics

Current reason for that priority:

- the source-study UX path is now real
- vector-failure grounding is now materially better and protected by tests
- the next meaningful gap is partial concept coverage, not total fallback collapse
- Part C now shows the source-view path and fallback grounding path both working, with concept coverage as the remaining weaker area

## 5. Chapter D4. Documentation Outputs To Maintain

After implementation, the repo should have:

- this plan set in `.plan/knowledge-platform-mvp`
- an implementation summary
- validation notes
- a short limitations section

Current files that satisfy those outputs:

- `part-a-audit-report.md`
- `part-b-implementation-report.md`
- `part-c-validation-report.md`

If needed in the next slice, create:

- `EVALS.md`
- `TEAM_OPS.md`
- `VENDOR_NOTES.md`

but do not bloat this MVP cycle with speculative documents that are not yet used.

## 6. Final Constraint

If forced to trade off, choose:

- correctness over flash
- readability over layout novelty
- source trust over UI gimmicks
- small useful delivery over ambitious overreach
