# Stage 6 OpenDocuments Baseline Validation

## Purpose

Stage 6 proves that the normalized P0 corpus can be indexed and queried with the OpenDocuments baseline before we move on to multi-turn implementation.

## Validation strategy

The baseline uses:

- OpenDocuments as the RAG runtime
- the Stage 2 normalized text corpus as ingest content
- the Stage 4 HTML citation corpus as the citation target carried in `sourcePath`
- a local OpenAI-compatible bridge that:
  - proxies `/v1/chat/completions` to the company LLM endpoint when a valid bearer token is configured
  - falls back to a local grounded Stage 6 response when company chat auth is not yet available
  - serves `/v1/embeddings` from `sentence-transformers`

This keeps OpenDocuments on a single OpenAI-compatible endpoint while respecting the current company-server constraint that chat is available but embeddings are not.

## Runtime assets

- bridge service: `app/opendocuments_openai_bridge.py`
- validation config template: `deployment/opendocuments-stage6.config.template.ts`
- validation env template: `deployment/opendocuments-stage6.env.template`
- baseline runner: `eval/run_opendocuments_stage6.mjs`

## Actual Stage 6 run

Validation workspace:

- `C:\Users\soulu\cywell\ocp-rag-v2\OpenDocuments\validation\ocp-stage6`

Runtime notes:

- `bootstrap()` is pinned to `dataDir=C:\Users\soulu\cywell\ocp-rag-v2\OpenDocuments\validation\ocp-stage6\.opendocuments-stage6`
- Stage 6 ingests the normalized `.txt` content referenced by `data/manifests/generated/openshift-docs-p0.json`
- each ingested record keeps the Stage 4 `html_path` as its `sourcePath`, so OpenDocuments citations still land on HTML viewer targets

Observed ingest result:

- processed inputs: `281`
- indexed: `281`
- skipped on rerun: `281`
- failed inputs: `0`

Generated evidence files:

- sample query output: `data/manifests/generated/opendocuments-stage6-sample-query.json`
- benchmark results: `data/manifests/generated/opendocuments-stage6-results.jsonl`
- ingest failure report: `data/manifests/generated/opendocuments-stage6-failures.json`

## Sample query check

Sample query:

- `방화벽에서 어떤 도메인과 포트를 열어야 해?`

Observed behavior:

- OpenDocuments returned a grounded answer path
- the answer included a citation-bearing source list
- the top source resolved to `installing/install_config/configuring-firewall.adoc`
- the citation target opened the Stage 4 HTML document path

Note:

- the current environment does not yet provide a valid company bearer token, so the sample answer text came from the Stage 6 local fallback generator
- this is acceptable for Stage 6 baseline plumbing validation, but it is not the final Stage 8 runtime configuration

## Benchmark summary

Stage 6 benchmark run against `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`:

- case count: `13`
- `source_dir_hit@5 = 1.0000`
- `supporting_doc_hit@10 = 0.9231`
- `citation_correctness = 0.6154`
- `retrieval_supporting_doc_hit@5 = 0.9231`
- `reranked_supporting_doc_hit@5 = 0.6154`
- `rerank_lift@5 = -0.3077`
- `click_through_ok = 13 / 13`
- `grounded_answer = 13 / 13`

## Stage 6 decision

Stage 6 is considered complete because:

1. OpenDocuments successfully indexed the normalized validation slice.
2. citation-bearing queries executed end to end.
3. citation targets resolved to the expected HTML outputs.
4. the first retrieval benchmark run was produced from the actual OpenDocuments baseline.

Stage 6 does **not** mean the system passes the first release gate yet.

The main follow-up gaps are:

- reranked citation correctness is still below the release target
- rerank currently regresses the benchmark subset
- the follow-up rewrite case (`RB-011`) still misses the expected supporting document
- company chat auth still needs a real bearer token before Stage 8 can lock the approved runtime path

## Expected Stage 6 evidence

1. OpenDocuments indexes the normalized validation slice without parser failure.
2. Korean questions return grounded answers with sources.
3. Source paths resolve to HTML citation targets.
4. The first Stage 5 benchmark subset can be executed against the OpenDocuments baseline.
