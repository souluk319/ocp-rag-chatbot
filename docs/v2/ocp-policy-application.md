# Stage 9 OCP Retrieval and Answer Policy

## Purpose

Stage 9 turns the RAG baseline into an OCP operations assistant by applying policy at two layers:

1. retrieval reranking
2. answer guardrails

The goal is not only to retrieve relevant text, but to prefer the right OCP source family, preserve version safety, and answer conservatively when grounding is weak.

## Retrieval policy

Stage 9 retrieval policy is defined in `configs/rag-policy.yaml` and executed by `app/ocp_policy.py`.

The reranker now combines:

- baseline similarity score
- trust-level priority
- source-directory preference
- category preference
- product-family blocking
- version continuity
- follow-up memory hints
- path-term matches derived from the user question

### Product-family rule

Allowed:

- `ocp`
- `internal`

Blocked:

- `okd`
- `rosa`
- `osd`
- `microshift`

This means Stage 9 explicitly penalizes product-family drift instead of relying on retrieval to avoid it by luck.

### Source priority rule

Highest trust:

- official OCP docs

Then:

- approved internal runbooks
- training material
- low-trust reference material

### Query-signal routing

The policy recognizes operational query families such as:

- install and prerequisites
- disconnected mirroring
- node and network troubleshooting
- operator troubleshooting
- update and upgrade preparation
- certificate maintenance

These rules do not replace retrieval. They reshape ordering so the top cited documents are more likely to come from the right source family and source directory.

## Answer policy

Stage 9 answer policy is also defined in `configs/rag-policy.yaml` and exposed through `app/ocp_policy.py`.

The default rules are:

- answer in Korean
- keep technical terms in original form when translation would reduce precision
- always attach citations
- refuse overconfident answers when grounding is weak
- keep upgrade, security, and troubleshooting answers conservative

### Operations mode

Operations mode is the default.

Behavior:

- concise
- checklist-like
- risk-aware for high-impact operations
- version continuity preserved when possible

### Study mode

Study mode is still supported for later UI integration.

Behavior:

- explanatory
- still grounded
- still citation-required

## Stage 9 evidence

The policy benchmark runner is:

- `eval/stage9_policy_report.py`

It consumes:

- Stage 5 benchmark cases
- Stage 6 baseline results
- the generated P0 manifest

It then produces:

- policy-reranked candidates
- policy-driven citation selection
- answer contract traces
- a retrieval benchmark summary using the existing Stage 5 reporter

## Actual Stage 9 benchmark summary

Actual run inputs:

- cases: `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`
- baseline results: `data/manifests/generated/opendocuments-stage6-results.jsonl`
- manifest: `data/manifests/generated/openshift-docs-p0.json`

Observed policy summary:

- `case_count = 13`
- `source_dir_hit@5 = 1.0000`
- `supporting_doc_hit@10 = 1.0000`
- `citation_correctness = 1.0000`
- `reranked_supporting_doc_hit@5 = 1.0000`
- `rerank_lift@5 = 0.0000`

Interpretation:

- Stage 9 policy closes the citation-quality gap from the Stage 6 baseline for the current slice
- Stage 9 now closes the `RB-011` follow-up miss on the accepted policy-prepared path
- Stage 9 keeps raw baseline retrieval recall visible as a separate diagnostic instead of hiding it inside the policy summary
- memory-aware rescue only activates when the active document still matches the follow-up source/category context

Additional diagnostic note:

- `raw_retrieval_summary.supporting_doc_hit@10 = 0.9231`
- `raw_retrieval_by_query_class.follow_up_rewrite.supporting_doc_hit@10 = 0.0000`

This means the product gate is satisfied on the policy-prepared path while the raw retrieval baseline remains observable for regression analysis.

## Deliverables

- `configs/rag-policy.yaml`
- `app/ocp_policy.py`
- `eval/stage9_policy_report.py`

## Exit criteria

Stage 9 is complete when:

1. OCP-specific retrieval ordering is implemented in code
2. answer guardrails are explicit in code and config
3. the benchmark runner can show policy-shaped rerank behavior
4. Stage 10 can use this policy as the baseline under test
