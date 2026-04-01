# Stage 6 Report

## Verdict
`pass`

Stage 6 is complete because:
- `localhost:8000` direct regression still passes.
- widened corpus regression is now reported honestly with raw and policy paths separated.

This is **not** a production-readiness claim.

## 1. Direct localhost regression

Direct runtime evidence now passes on the live stack.

- health: `200`
- checked cases: `5`
- passed cases: `5`
- all answers returned in Korean
- all answers returned at least one citation
- all first citation viewers opened as `200 text/html`

Directly checked prompts:

- `오픈시프트가 뭐야`
- `OCP가 뭐야`
- `설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?`
- `업데이트 전에 확인해야 할 사항은 무엇인가요?`
- `폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?`

Direct evidence:

- [Stage 5 direct runtime report](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-05-direct-runtime-report.md)
- [stage05-direct-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-direct-runtime-report.json)
- [stage-06-direct-runtime-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-06-direct-runtime-report.md)
- [stage-06-direct-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-06-direct-runtime-report.json)

## 2. Widened-corpus regression

Stage 6 widened-corpus results must always be split into raw and policy-supported behavior.

### Raw baseline

- `source_dir_hit@5 = 0.0`
- `supporting_doc_hit@10 = 0.0`

Raw widened-corpus retrieval is still weak.

### Policy-prepared path

- `source_dir_hit@5 = 1.0`
- `supporting_doc_hit@10 = 1.0`
- `citation_correctness = 1.0`
- `rerank_lift@5 = 0.0`

### Companion gates

- Multiturn: `2/2` scenarios passed
- Red-team: `7/7` cases passed
- Runtime gate: `pass`

### Honest summary

- `overall_decision = policy-go/raw-gap-present`

That means the live answer path is currently acceptable, but the raw widened-corpus baseline is still a diagnostic risk.

## 3. Reporting rule

When reporting upward, keep these statements separate:

- `localhost:8000 direct runtime is green.`
- `Widened-corpus regression passes on the policy-prepared path.`
- `Raw retrieval remains weak and should not be presented as solved.`

## 4. Evidence

- [stage06-regression-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-regression-summary.json)
- [stage06-suite-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-suite-report.json)
