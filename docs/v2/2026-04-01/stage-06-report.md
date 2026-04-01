# Stage 6 Report

## Verdict
`go` on the widened-corpus regression gate.

This is not a production-readiness claim.
It only means the policy-supported path still passes after widening the corpus.

## Canonical localhost baseline
The direct user-visible proof remains Stage 5.

- [Stage 5 direct runtime report](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-05-direct-runtime-report.md)
- [Stage 5 direct runtime JSON](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-direct-runtime-report.json)

That proof showed:
- `localhost:8000` responded correctly
- Korean answers were returned
- citations were present
- HTML viewer links opened successfully

## Stage 6 widened-corpus regression
The widened-corpus suite passed on the policy-prepared path.

- Raw baseline diagnostics:
  - `source_dir_hit@5 = 0.0`
  - `supporting_doc_hit@10 = 0.0`
- Policy-prepared metrics:
  - `source_dir_hit@5 = 0.9231`
  - `supporting_doc_hit@10 = 0.9231`
  - `citation_correctness = 0.9231`
  - `rerank_lift@5 = 0.0`
- Multiturn:
  - `2/2` scenarios passed
  - `10/10` turns passed the planned checks
- Red-team:
  - `7/7` cases passed
- Overall regression gate:
  - `go`

## Reporting rule
When writing about Stage 6, always separate:
- `Policy-supported behavior`: the answer path after routing, rescue, and policy augmentation.
- `Raw baseline`: the unassisted retrieval diagnostic result.

Use this wording:
- "The localhost runtime is still green."
- "Widened-corpus regression passes on the policy-prepared path."
- "Raw retrieval is still weak and remains a diagnostic risk."
- "We should not present this as full production readiness yet."

## Evidence
- [stage06-suite-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-suite-report.json)
- [stage06-regression-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-regression-summary.json)
