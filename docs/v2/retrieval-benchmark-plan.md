# v2 Retrieval Benchmark Plan

## Purpose

This document defines the first fixed benchmark set for retrieval quality on the normalized P0 corpus.

The benchmark exists to answer one question with evidence:

**Can the system reliably retrieve the right OCP document family and the expected supporting document before we expand scope?**

## Benchmark design principles

1. Every benchmark case must point to a real document in the normalized P0 corpus.
2. The benchmark must be written in Korean because that is the operator-facing input language.
3. Benchmark scoring must separate raw retrieval from reranked retrieval.
4. Follow-up turns must be present as benchmark items, not treated as an afterthought.
5. Failing cases must be traceable through the Stage 4.5 context-retention harness.

## Input corpus for Stage 5

The first benchmark is restricted to the validated P0 slice:

- `installing`
- `post_installation_configuration`
- `updating`
- `disconnected`
- `support`

Non-OCP product lines remain excluded according to:

- `docs/v2/source-scope.md`
- `configs/source-manifest.yaml`

## Query classes

The first benchmark must cover at least these query classes:

- `install_prereq`
- `install_config`
- `disconnected_mirroring`
- `disconnected_install`
- `troubleshooting_node_health`
- `troubleshooting_network`
- `troubleshooting_operator`
- `update_version_check`
- `update_prereq`
- `follow_up_rewrite`
- `certificate_maintenance`

## Benchmark assets

The Stage 5 assets are:

- benchmark cases: `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`
- case schema: `eval/retrieval-benchmark-schema.yaml`
- sample run results: `eval/fixtures/retrieval_benchmark_sample_results.jsonl`
- metric reporter: `eval/retrieval_benchmark_report.py`

## Case-writing rules

Each benchmark case must include:

- a Korean operator question
- one or more expected source directories
- one or more expected supporting document paths
- an expected query class
- an expected memory behavior
- citation and click-through requirements
- notes describing why the case exists

Follow-up benchmark cases must also include:

- `scenario_id`
- `turn_index > 1`
- `turn_type = follow_up`
- an expected memory behavior such as `follow_up_rewrite_required`

## Metrics

The benchmark reporter computes:

- `source_dir_hit@3`
- `source_dir_hit@5`
- `supporting_doc_hit@5`
- `supporting_doc_hit@10`
- `citation_correctness`
- `retrieval_supporting_doc_hit@5`
- `reranked_supporting_doc_hit@5`
- `rerank_lift@5`

`rerank_lift@5` is defined as:

- `reranked_supporting_doc_hit@5 - retrieval_supporting_doc_hit@5`

The reporter must also provide:

- per-query-class summaries
- per-case summaries
- benchmark coverage counts by query class

## First-slice gates

Stage 5 preserves the gates already defined in `docs/v2/evaluation-spec.md`.

The baseline target is:

- `source_dir_hit@5 >= 0.85`
- `supporting_doc_hit@10 >= 0.75`
- `citation_correctness >= 0.90` on grounded answers
- reranking must improve or at least not regress the ambiguous-query subset

## Relationship to Stage 4.5

The benchmark is not allowed to operate as a black box.

If a benchmark case fails, it should be possible to attach the matching Stage 4.5 trace and answer:

- did retrieval miss the expected document
- did rerank demote the expected document
- did context assembly drop the expected chunk
- did citation output fail to reflect the grounded source

## Deliverables

Stage 5 is complete only if all of the following exist:

1. a fixed benchmark case set
2. a benchmark schema
3. a scoring script that computes the required metrics
4. a sample run result that proves the script works
5. roadmap and design documents that treat the benchmark as the entry point for Stage 6 validation
