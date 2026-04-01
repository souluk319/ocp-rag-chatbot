# 2026-04-01 Stage Index

## How to read this folder
- Start with [fixed-context-brief.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/fixed-context-brief.md).
- Use [fixed-context.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/fixed-context.md) only when you need the full project context.
- Use this folder for stage-by-stage execution notes and reports only.

## Current status
- Stage 1: done
- Stage 2: done
- Stage 3: done
- Stage 4: done
- Stage 5: done
- Stage 6: guardrails documented

## Stage 5 and Stage 6 boundary
- Stage 5 is the canonical direct `localhost:8000` proof.
- Stage 6 is the widened-corpus regression report and guardrail layer.
- Do not merge those claims.

## Stage 5 files
- [Stage 5 summary](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-05-report.md)
- [Stage 5 direct runtime report](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-05-direct-runtime-report.md)

## Stage 6 files
- [Stage 6 guardrails](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-06-regression.md)
- [Stage 6 report](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-06-report.md)

## Reporting rule
When writing status updates, always separate:
- `localhost:8000` direct runtime evidence
- raw baseline diagnostics
- policy-prepared regression results
- production-readiness claims

## Current shorthand
- `localhost:8000`: user-visible runtime checkpoint
- `raw baseline`: diagnostic only
- `policy-prepared`: the answer path we can report for Stage 6
