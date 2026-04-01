# Stage 6 Guardrails

## Purpose
Stage 6 is a widened-corpus regression checkpoint. Its job is to protect us from overclaiming.
Use this file when reporting upward so `localhost:8000` evidence stays separate from regression metrics.

## What is canonical
- `localhost:8000` is the user-visible runtime checkpoint.
- The Stage 5 direct runtime report remains the canonical direct localhost proof:
  - [stage-05-direct-runtime-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-05-direct-runtime-report.md)
  - [stage05-direct-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-direct-runtime-report.json)
- Stage 6 does not replace that baseline. It checks whether widened-corpus behavior still holds.

## What Stage 6 may claim
- Policy-prepared retrieval on widened corpus passed the regression gate.
- Multiturn, red-team, and context-traceability gates passed.
- The system remains runnable from `localhost:8000` when the direct runtime baseline is healthy.

## What Stage 6 must not claim
- Do not say the raw baseline is strong.
- Do not say the whole chatbot is production-ready.
- Do not describe policy-supported behavior as if it were raw retrieval behavior.
- Do not collapse the Stage 5 direct localhost proof into the Stage 6 regression result.

## Reporting rule
When summarizing Stage 6, always separate these two statements:
- `Policy-supported behavior`: the answer path after routing, rescue, and policy augmentation.
- `Raw baseline`: the unassisted retrieval diagnostic result.

## Current Stage 6 regression summary
- Raw baseline:
  - `source_dir_hit@5 = 0.0`
  - `supporting_doc_hit@10 = 0.0`
- Policy-prepared path:
  - `source_dir_hit@5 = 1.0`
  - `supporting_doc_hit@10 = 1.0`
  - `citation_correctness = 1.0`
  - `rerank_lift@5 = 0.0`
- Multiturn:
  - `2/2` scenarios passed
  - `10/10` turns passed the planned checks
- Red-team:
  - `7/7` cases passed
- Overall regression gate:
  - `policy-go/raw-gap-present`

## User-facing wording to use
Use this wording when reporting upward:
- "The localhost runtime is still green."
- "Widened-corpus regression passes on the policy-prepared path."
- "Raw retrieval is still weak and remains a diagnostic risk."
- "We should not present this as full production readiness yet."
