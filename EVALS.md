# EVALS.md

## Purpose

This file defines the evaluation policy, datasets, and pass criteria for the OCP Korean RAG project.

Evaluation must keep retrieval quality and answer quality separate.
Good wording must not hide weak retrieval.

## Current Scope

Current active evaluation scope:

- Part 2 retrieval quality on the 29-book high-value subset
- Part 3 minimum answer quality on top of validated retrieval
- Korean-first operational and learning questions
- visible follow-up rewrite behavior

Not yet in scope for release judgment:

- full 113-book corpus answer quality
- final UI quality
- end-to-end demo polish

## Active Datasets

Current benchmark assets:

- `manifests/part2_smoke_queries.jsonl`
- `manifests/part2_retrieval_benchmark.jsonl`
- `manifests/part3_answer_eval_cases.jsonl`
- `manifests/part3_ragas_golden_cases.jsonl`

Recommended output reports:

- `part2/smoke_report.json`
- `part2/retrieval_benchmark_report.json`
- `part3/answer_eval_report.json`
- `part3/ragas_eval_report.json`

## Retrieval Metrics

Use these metrics for Part 2:

- `hit@1`: at least one expected source appears in top 1
- `hit@3`: at least one expected source appears in top 3
- `hit@5`: at least one expected source appears in top 5
- `follow_up_hit@5`: `hit@5` measured only on follow-up cases
- `warning_free_rate`: proportion of cases with no retrieval warnings

Track these cuts separately:

- overall
- `ops`
- `learn`
- `follow-up`
- `broad`

## Baseline Thresholds

Baseline is good enough to continue iteration.

For the 29-book high-value subset benchmark:

- overall `hit@1 >= 0.80`
- overall `hit@3 >= 0.95`
- overall `hit@5 >= 0.95`
- `follow-up hit@5 >= 0.90`
- `warning_free_rate = 1.0`

Additional baseline gates:

- all retrieval hits must preserve source metadata
- benchmark misses must be written to the report
- known source-language anomalies must be documented in `VENDOR_NOTES.md`

## Release Thresholds

Release is the ship-readiness bar, not the early MVP bar.

For the broadened benchmark over the validated corpus:

- overall `hit@1 >= 0.90`
- overall `hit@3 >= 0.97`
- overall `hit@5 >= 0.92`
- `follow-up hit@5 >= 0.95`
- `warning_free_rate = 1.0`
- no `Legal Notice` or other known boilerplate chunks in top 5

Additional release gates:

- citation metadata must be present for every retrieved hit shown to users
- false positives must be inspected by source family
- retrieval regressions must be compared against the previous benchmark report

## Failure Buckets

Every benchmark miss should be tagged into one primary bucket:

- source gap
- chunking issue
- BM25 ranking miss
- vector ranking miss
- hybrid fusion miss
- follow-up rewrite miss
- reference resolution miss
- language mismatch

## Answer Metrics

Use these metrics for Part 3 minimum answer evaluation:

- `answer_present_rate`: answer body is non-empty
- `korean_answer_rate`: answer contains Korean text
- `answer_format_rate`: answer starts with the fixed `답변:` contract
- `inline_citation_rate`: answer includes inline citation numbers like `[1]`
- `citation_valid_rate`: cited indices resolve to returned citation entries
- `expected_citation_rate`: at least one cited source belongs to the expected source family
- `unexpected_citation_rate`: proportion of cases citing books outside expected or explicitly forbidden families
- `strict_expected_only_rate`: cited sources stay inside the allowed source family
- `avg_citation_precision`: average share of cited sources that belong to the expected source family
- `clarification_needed_but_answered_rate`: rate of clarification-expected cases that still answered assertively
- `no_evidence_but_asserted_rate`: rate of no-answer-expected cases that still answered assertively
- `warning_free_rate`: no answer or retrieval warnings
- `pass_rate`: all checks above pass for the same case

Track these cuts separately:

- overall
- `ops`
- `learn`
- `follow_up`
- `ambiguous`
- `clarification_required`
- `negative`

## Part 3 Baseline Thresholds

Baseline is good enough to continue toward UI integration.

For the minimum answer set:

- `answer_present_rate = 1.0`
- `korean_answer_rate >= 0.95`
- `answer_format_rate >= 0.95`
- `inline_citation_rate >= 0.80`
- `citation_valid_rate = 1.0`
- `expected_citation_rate >= 0.80`
- `unexpected_citation_rate <= 0.20`
- `strict_expected_only_rate >= 0.70`
- `avg_citation_precision >= 0.85`
- `clarification_needed_but_answered_rate <= 0.20`
- `no_evidence_but_asserted_rate = 0.0`
- `warning_free_rate >= 0.75`
- `pass_rate >= 0.85`

Additional baseline gates:

- failures must be written to the report
- clarification-expected and no-answer-expected cases must be tagged explicitly
- failure entries must include question, rewritten query, retrieved books, final citations, and answer text

## Part 3 Release Thresholds

Release is the ship-readiness bar, not the MVP bar.

For the broadened answer set:

- `answer_present_rate = 1.0`
- `korean_answer_rate = 1.0`
- `answer_format_rate >= 0.98`
- `inline_citation_rate >= 0.85`
- `citation_valid_rate = 1.0`
- `expected_citation_rate >= 0.85`
- `unexpected_citation_rate <= 0.10`
- `strict_expected_only_rate >= 0.85`
- `avg_citation_precision >= 0.92`
- `clarification_needed_but_answered_rate <= 0.10`
- `no_evidence_but_asserted_rate = 0.0`
- `warning_free_rate >= 0.80`
- `pass_rate >= 0.92`

Additional release gates:

- no fabricated citations
- no unanswered follow-up reference when context is sufficient
- ambiguous questions should prefer clarification over speculative expansion
- answer failures must be comparable against the previous report

## Part 3 RAGAS Gate

Use RAGAS only on answerable golden cases with a reference answer.

Do not mix these cases with:

- clarification-required cases
- no-answer-required cases
- pure UI checks such as internal viewer link behavior

Track these metrics:

- `faithfulness`
- `answer_relevance`
- `context_precision`
- `context_recall`

Baseline for iteration:

- golden-set `case_count >= 10`
- average `faithfulness >= 0.75`
- average `answer_relevance >= 0.75`
- average `context_precision >= 0.70`
- average `context_recall >= 0.70`

Release guidance:

- golden-set `case_count >= 30`
- average `faithfulness >= 0.85`
- average `answer_relevance >= 0.85`
- average `context_precision >= 0.80`
- average `context_recall >= 0.80`

Important:

- RAGAS does not replace product checks for citation shape, internal `/docs/...` links, forbidden books, or clarification behavior.
- RAGAS should be reported alongside the existing Part 3 custom eval, not instead of it.

## Current Interpretation

At the current stage:

- passing baseline means Part 3 answer work can continue without UI expansion
- failing release does not block MVP exploration
- failing baseline means stay in Part 3 and tighten answer gate first
