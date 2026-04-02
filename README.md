# OCP RAG v2

This repository currently focuses on **Part 1: preprocessing pipeline** for a closed-network Korean OCP RAG system.

Current objective:

- collect Korean OCP 4.20 `html-single` documents
- normalize them into inspectable records
- test chunking on a high-value subset
- generate embeddings
- store retrieval-ready artifacts

Key entry points:

- [PROJECT_PLAN.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/PROJECT_PLAN.md)
- [PART1_PLAN.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/PART1_PLAN.md)
- [PART3_PLAN.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/PART3_PLAN.md)
- [EVALS.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/EVALS.md)
- `scripts/build_source_manifest.py`
- `scripts/run_part1.py`
- `scripts/run_part2_benchmark.py`
- `scripts/run_part3_answer.py`
- `scripts/run_part3_eval.py`
- `scripts/run_part4_ui.py`

Quick start:

```powershell
python scripts/build_source_manifest.py
python scripts/run_part1.py --skip-embeddings --skip-qdrant --collect-limit 3 --process-limit 3
```

Artifacts are written under `artifacts/` by default.

If the repo gets too heavy, you can move them outside the repository:

```powershell
# Move all generated artifacts out of the repo
ARTIFACTS_DIR=C:\Users\soulu\cywell\ocp-rag-chatbot-data

# Or keep only raw HTML outside the repo
RAW_HTML_DIR=C:\Users\soulu\cywell\ocp-rag-chatbot-raw\part1\raw_html
```

When `ARTIFACTS_DIR` is set, Part 1 and Part 2 outputs are written under that external directory.

Embeddings are generated through the configured remote endpoint at `EMBEDDING_BASE_URL`.
Chunk sizing uses `SentenceTransformer("dragonkue/bge-m3-ko")` locally so tokenizer behavior stays explicit and inspectable.

Part 3 now includes a minimum answer pipeline:

```powershell
python scripts/run_part3_answer.py --mode learn --query "OpenShift 아키텍처를 처음 설명해줘"
python scripts/run_part3_eval.py
```

Part 4 now includes a minimum QA chat UI:

```powershell
python scripts/run_part4_ui.py
```

The UI is intended for manual review of:

- Korean question and follow-up behavior
- visible citations per answer
- rewritten query inspection
- regenerate and session reset
