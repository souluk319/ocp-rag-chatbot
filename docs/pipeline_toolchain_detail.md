---
status: reference
doc_type: explainer
audience:
  - engineer
  - codex
  - operator
last_updated: 2026-04-18
---

# PBS Pipeline Toolchain Detail

이 문서는 `PlayBookStudio`의 현재 파이프라인을 `실제로 호출되는 서비스/함수/오픈소스 이름` 기준으로 정리한 설명서다.

핵심 목적은 두 가지다.

1. `현재 메인 파이프라인이 어디서 시작해서 어디까지 가는지`를 사람이 추적할 수 있게 한다.
2. `어떤 단계가 주 경로이고, 어떤 단계가 조건부 fallback/보조선인지`를 코드 기준으로 고정한다.

이 문서는 active contract를 대체하지 않는다.
현재 코드 상태를 빠르게 이해하기 위한 reference explainer다.

## 먼저 보는 결론

PBS에는 실제로 두 개의 큰 파이프라인 spine이 있다.

1. `official source-first pipeline`
   - OCP 4.20 같은 공식 문서 번들에서 시작
   - manifest -> raw html -> normalized sections -> chunks/playbooks -> qdrant/runtime
2. `customer/private pack pipeline`
   - 사용자가 업로드한 문서에서 시작
   - capture -> normalize -> canonical/playable books -> private corpus -> gated runtime/retrieval

둘은 다른 진입점을 가지지만, 최종 방향은 같다.

- `reader-grade Playbook Library`
- `grounded retrieval corpus`
- `anchor-backed citation`

## 1. Official Source-First Pipeline

### 1.1 Foundry / orchestration entrypoint

실행 진입점:

- `scripts/run_gold_foundry.py`
- `pipelines/foundry_routines.json`
- `src/play_book_studio/ingestion/foundry_orchestrator.py`

실제 job/profile 예:

- `manifest_refresh`
- `high_value_ingestion`
- `source_approval`
- `approved_runtime_rebuild`
- `source_bundle_harvest`
- `source_bundle_quality`
- `synthesis_lane`
- `translation_drafts`
- `translation_gold_promotion`
- `validation_gate`
- `runtime_smoke`

설명:

- `run_gold_foundry.py`는 named profile을 실행하는 wrapper다.
- 실제 orchestration logic은 `foundry_orchestrator.py`에 있다.
- job 정의와 schedule은 `pipelines/foundry_routines.json`에 있다.

### 1.2 Source catalog / manifest

주요 코드:

- `src/play_book_studio/ingestion/pipeline.py`
  - `ensure_manifest()`
- `src/play_book_studio/ingestion/manifest.py`

하는 일:

- 공식 문서 catalog를 manifest로 고정한다.
- 어떤 book slug를 현재 run에서 처리할지 결정한다.

대표 산출물:

- `manifests/ocp_multiversion_html_single_catalog.json`
- `manifests/ocp_ko_4_20_approved_ko.json`

### 1.3 Raw HTML collect

주요 코드:

- `src/play_book_studio/ingestion/collector.py`
  - `fetch_html_response()`
  - `fetch_html_text()`
  - `collect_entry()`
  - `entry_with_collected_metadata()`

실제 사용 도구 / 오픈소스:

- `requests`
- `BeautifulSoup` from `bs4`

하는 일:

- published HTML source를 가져온다.
- raw HTML을 `data/bronze/raw_html/*.html`로 저장한다.
- metadata도 같이 쓴다.

같이 남기는 것:

- `resolved_source_url`
- `resolved_language`
- `raw_html_sha256`
- `legal_notice_url`
- `license_or_terms`
- `updated_at`

### 1.4 Normalize HTML -> canonical sections

주요 코드:

- `src/play_book_studio/ingestion/normalize.py`
  - `extract_document_ast()`
  - `project_normalized_sections()`
- `src/play_book_studio/canonical/*`
  - `build_web_document_ast()`
  - `translate_document_ast()`
  - `validate_document_ast()`
  - `project_corpus_sections()`

실제 사용 도구 / 오픈소스:

- `BeautifulSoup` from `bs4`

하는 일:

- noisy docs HTML을 canonical document AST로 바꾼다.
- section boundary, anchor, code/table/text block를 정리한다.
- 그 결과를 `NormalizedSection` 리스트로 투사한다.

중요한 조건부 분기:

- `manual_synthesis` source는 raw HTML 재파싱 대신
  - `src/play_book_studio/ingestion/playbook_materialization.py`
  - `load_approved_playbook_payload()`
  - `project_playbook_payload_sections()`
  를 우선 사용한다.

### 1.5 Chunk / playbook / embedding / Qdrant

주요 코드:

- `src/play_book_studio/ingestion/chunking.py`
  - `chunk_sections()`
- `src/play_book_studio/ingestion/embedding.py`
  - `EmbeddingClient`
- `src/play_book_studio/ingestion/qdrant_store.py`
  - `ensure_collection()`
  - `upsert_chunks()`
- `src/play_book_studio/canonical/project_playbook_document`
- `src/play_book_studio/ingestion/topic_playbooks.py`
  - `materialize_derived_playbooks()`
- `src/play_book_studio/ingestion/runtime_catalog_library.py`
  - `materialize_runtime_corpus_from_playbooks()`

실제 사용 도구 / 오픈소스:

- remote `embedding endpoint` via `requests`
- `sentence-transformers`
  - tokenizer 사용은 `chunking.py`
  - local fallback encoding은 `sentence_model.py`
- `Qdrant`
- `requests`

하는 일:

- `NormalizedSection`을 retrieval chunk로 나눈다.
- BM25용 JSONL과 vector용 벡터를 만든다.
- Qdrant collection을 맞추고 point upsert를 한다.
- reader용 playbook document와 derived playbook family를 함께 materialize한다.

대표 산출물:

- `data/silver/normalized_docs.jsonl`
- `data/gold_corpus_ko/chunks.jsonl`
- `data/gold_manualbook_ko/playbook_documents.jsonl`
- `data/gold_manualbook_ko/playbooks/*.json`
- `qdrant: openshift_docs`

### 1.6 Graph artifact refresh

주요 코드:

- `src/play_book_studio/ingestion/graph_sidecar.py`
- `src/play_book_studio/ingestion/pipeline.py`
  - `refresh_active_runtime_graph_artifacts()`

하는 일:

- retrieval runtime이 쓸 graph sidecar와 compact artifact를 만든다.
- 현재 안정화 이후 `compact graph artifact`가 local fallback의 기본 보조선이다.

대표 산출물:

- `artifacts/retrieval/graph_sidecar.json`
- `artifacts/retrieval/graph_sidecar_compact.json`

## 2. Customer / Private Pack Pipeline

### 2.1 API / lifecycle entrypoint

주요 코드:

- `src/play_book_studio/app/intake_api.py`

실제 진입 함수:

- `create_customer_pack_draft()`
- `upload_customer_pack_draft()`
- `capture_customer_pack_draft()`
- `normalize_customer_pack_draft()`
- `ingest_customer_pack()`

이 경로가 사용하는 핵심 서비스:

- `CustomerPackPlanner`
- `CustomerPackCaptureService`
- `CustomerPackNormalizeService`

### 2.2 Planning / support matrix

주요 코드:

- `src/play_book_studio/intake/planner.py`
  - `CustomerPackPlanner`
  - `build_customer_pack_support_matrix()`

하는 일:

- source type별 허용 경로를 정한다.
- title / product / version / pack id를 추론한다.
- 지원 상태를 `supported / staged / rejected`로 정리한다.

현재 source type:

- `web`
- `pdf`
- `md`
- `asciidoc`
- `txt`
- `docx`
- `pptx`
- `xlsx`
- `image`

### 2.3 Capture

주요 코드:

- `src/play_book_studio/intake/capture/service.py`
  - `CustomerPackCaptureService.capture()`

실제 사용 도구 / 오픈소스:

- `requests`
- `mimetypes`
- `shutil`
- `hashlib`
- `fetch_html_text()` from `ingestion.collector`

source type별 실제 동작:

- `web`
  - local HTML/text file 읽기 또는 remote HTML fetch
- `pdf`
  - 파일 복사
- `docx/pptx/xlsx/image`
  - local binary copy 또는 remote binary download
- `md/asciidoc/txt`
  - UTF-8 text capture

남기는 것:

- `capture_artifact_path`
- `capture_content_type`
- `capture_byte_size`
- `source_fingerprint` (sha256)

### 2.4 Normalize orchestration

주요 코드:

- `src/play_book_studio/intake/normalization/service.py`
  - `CustomerPackNormalizeService.normalize()`

이 파일이 실제 customer/private normalize spine이다.

여기서 같이 처리되는 것:

- format-specific parse
- degraded 판단
- optional fallback seam
- evidence patch
- playable book write
- private corpus materialization

즉 customer pack 쪽에서는 아래가 `한 서비스 안에서 같이 묶여` 돈다.

- parse
- OCR / fallback
- evidence
- private corpus

### 2.5 Format-specific normalize backends

주요 코드:

- `src/play_book_studio/intake/normalization/builders.py`
  - `build_canonical_book()`

#### 2.5.1 Web

실제 경로:

- `_build_web_canonical_book()`
- `ingestion.normalize.extract_sections()`

실제 사용 도구 / 오픈소스:

- `BeautifulSoup` via ingestion normalize path

#### 2.5.2 Markdown / AsciiDoc / Text

실제 경로:

- `_build_text_canonical_book()`
- `_replace_fenced_code_blocks()`
- `_replace_markdown_tables()`

하는 일:

- heading, fenced code, markdown table, numeric heading을 section 구조로 정리한다.

#### 2.5.3 PDF / DOCX / PPTX / XLSX primary path

실제 경로:

- `MARKITDOWN_SOURCE_TYPES = {"pdf", "docx", "pptx", "xlsx"}`
- `_build_markitdown_first_canonical_book()`
- `convert_with_markitdown()`

주요 코드:

- `src/play_book_studio/intake/normalization/markitdown_adapter.py`

실제 사용 도구 / 오픈소스:

- `MarkItDown`

중요:

- 현재 customer/private lane에서 `pdf`의 1차 경로는 Docling보다 `MarkItDown first`다.
- 즉 예전 설명처럼 “PDF 메인 파서 = Docling”이라고만 적으면 현재 코드 기준으로는 정확하지 않다.

#### 2.5.4 PDF legacy fallback path

실제 경로:

- `_build_pdf_canonical_book()`
- `extract_pdf_markdown_with_docling()`
- `extract_pdf_markdown_with_docling_ocr()`
- `extract_pdf_pages()`
- `extract_pdf_outline()`

주요 코드:

- `src/play_book_studio/intake/normalization/pdf.py`

실제 사용 도구 / 오픈소스:

- `docling`
  - `DocumentConverter`
  - `PdfPipelineOptions`
- `pypdf`
- `mdls`
  - macOS Spotlight text fallback
- raw `string scan`
- `pypdfium2`
- `rapidocr`

실제 fallback 순서:

1. `Docling markdown`
2. `Docling OCR markdown`
3. `pypdf`
4. `mdls`
5. `string_scan`
6. `pypdfium2 + RapidOCR`

#### 2.5.5 DOCX legacy fallback path

실제 사용 도구 / 오픈소스:

- `python-docx`

#### 2.5.6 PPTX legacy fallback path

실제 사용 도구 / 오픈소스:

- `python-pptx`

#### 2.5.7 XLSX legacy fallback path

실제 사용 도구 / 오픈소스:

- `openpyxl`

#### 2.5.8 Image OCR path

실제 경로:

- `_build_image_book_with_optional_fallback()`
- `extract_image_markdown_with_docling()`

하는 일:

- image OCR 결과를 canonical section으로 만든다.
- 저품질이면 optional fallback seam을 태울 수 있다.

### 2.6 Degraded detector + optional OCR fallback seam

주요 코드:

- `src/play_book_studio/intake/normalization/degraded_pdf.py`
  - `assess_degraded_pdf_payload()`
  - `attempt_optional_pdf_markdown_fallback()`
  - `attempt_optional_image_markdown_fallback()`
- `src/play_book_studio/intake/normalization/surya_adapter.py`

실제 사용 도구 / 오픈소스:

- optional `Surya`
- `requests`
- `pypdfium2` for Surya PDF page rendering

하는 일:

- 품질 flag를 보고 degraded PDF인지 판정
- 설정과 경계 조건이 맞으면 optional OCR fallback을 시도
- 실패해도 `backend_unavailable`, `adapter_failed`, `blocked` 같은 evidence를 남기고 normalize를 이어간다

현재 fallback backend map:

- `surya`
- `marker`는 seam만 있고 현재 binding은 optional

### 2.7 Evidence contract

주요 코드:

- `_finalize_pdf_evidence()` in `normalization/service.py`

남기는 실제 필드 예:

- `parser_route`
- `parser_backend`
- `parser_version`
- `ocr_used`
- `extraction_confidence`
- `quality_status`
- `quality_score`
- `quality_flags`
- `quality_summary`
- `degraded_pdf`
- `degraded_reason`
- `fallback_used`
- `fallback_backend`
- `fallback_status`
- `fallback_reason`

### 2.8 Playable books / derived playbooks

주요 코드:

- `src/play_book_studio/intake/service.py`
  - `build_customer_pack_playable_books()`

실제 파생 family:

- `topic_playbook`
- `operation_playbook`
- `troubleshooting_playbook`
- `policy_overlay_book`
- `synthesized_playbook`

하는 일:

- canonical manual book 1권을 만든다.
- 그 canonical sections에서 family별 playable asset을 파생한다.

### 2.9 Private corpus materialization

주요 코드:

- `src/play_book_studio/intake/private_corpus.py`
  - `build_customer_pack_private_corpus_rows()`
  - `materialize_customer_pack_private_corpus()`

실제 사용 도구 / 오픈소스:

- `chunk_sections()` from ingestion chunking
- `sentence-transformers`
  - `load_sentence_model()`
- local JSONL artifact write

실제 산출물:

- `artifacts/customer_packs/corpus/<draft_id>/chunks.jsonl`
- `artifacts/customer_packs/corpus/<draft_id>/bm25_corpus.jsonl`
- `artifacts/customer_packs/corpus/<draft_id>/vector_store.jsonl`
- `artifacts/customer_packs/corpus/<draft_id>/manifest.json`

현재 상태:

- materialization 실패가 나도 normalize 전체를 무너뜨리지 않도록 graceful 쪽으로 보강돼 있다.

### 2.10 Private boundary gates

주요 코드:

- `src/play_book_studio/intake/private_boundary.py`
  - `summarize_private_runtime_boundary()`
  - `summarize_private_remote_ocr_boundary()`
- `src/play_book_studio/app/customer_pack_read_boundary.py`

하는 일:

- private/customer asset이 runtime surface와 retrieval ingress에 들어가도 되는지 판정한다.

현재 핵심 조건:

- `tenant_id` placeholder 아님
- `workspace_id` placeholder 아님
- `approval_state=approved`
- `publication_state` 존재
- private manifest가 있으면 `runtime_eligible=true`
- remote OCR은 `provider_egress_policy`와 `redaction_state`까지 만족해야 함

## 3. Retrieval / Graph / Answer Runtime

### 3.1 Main retrieval entrypoint

주요 코드:

- `src/play_book_studio/retrieval/retriever.py`
  - `ChatRetriever`
  - `ChatRetriever.from_settings()`

실제 구성 요소:

- `BM25Index`
- `VectorRetriever`
- optional `CrossEncoderReranker`
- `RetrievalGraphRuntime`

### 3.2 Query planning

주요 코드:

- `src/play_book_studio/retrieval/retriever_pipeline.py`
  - `execute_retrieval_pipeline()`
- `src/play_book_studio/retrieval/retriever_plan.py`
  - `build_retrieval_plan()`
- `src/play_book_studio/retrieval/rewrite.py`
- `src/play_book_studio/retrieval/decompose.py`

하는 일:

- normalize query
- rewrite
- decomposition
- candidate budget 결정

### 3.3 BM25

주요 코드:

- `src/play_book_studio/retrieval/bm25.py`
  - `BM25Index.from_jsonl()`
  - `BM25Index.search()`
- `src/play_book_studio/retrieval/retriever_search.py`
  - `search_bm25_candidates()`

특징:

- pure Python BM25 index다.
- tokenization은 `TOKEN_RE` 기반이다.
- private overlay BM25와 official BM25를 합성할 수 있다.

### 3.4 Vector retrieval

주요 코드:

- `src/play_book_studio/retrieval/vector.py`
  - `VectorRetriever`
  - `search_with_trace()`
- `src/play_book_studio/ingestion/embedding.py`
  - `EmbeddingClient`

실제 사용 도구 / 오픈소스:

- remote embeddings endpoint
- `requests`
- `Qdrant`

특징:

- query embedding은 remote `/embeddings` endpoint를 친다.
- vector search는 Qdrant `/points/search` 또는 `/points/query`를 호출한다.
- private vector artifact도 같이 merge할 수 있다.

### 3.5 Fusion

주요 코드:

- `src/play_book_studio/retrieval/scoring.py`
- `src/play_book_studio/retrieval/ranking.py`

하는 일:

- BM25와 vector 후보를 RRF 기반으로 fuse한다.

### 3.6 Rerank

주요 코드:

- `src/play_book_studio/retrieval/retriever_rerank.py`
  - `maybe_rerank_hits()`
- `src/play_book_studio/retrieval/reranker.py`
  - `CrossEncoderReranker`

실제 사용 도구 / 오픈소스:

- `sentence-transformers`
- `CrossEncoder`
- 기본 모델:
  - `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`

특징:

- 기본값은 optional이다.
- explanation query, follow-up, ambiguity, derived/non-core hit 등에 따라 model rerank를 탈지 결정한다.

### 3.7 Graph runtime

주요 코드:

- `src/play_book_studio/retrieval/graph_runtime.py`
  - `RetrievalGraphRuntime`
  - `LocalGraphSidecar`

실제 사용 도구 / 오픈소스:

- local graph sidecar JSON
- compact graph artifact
- optional `Neo4j`
- optional remote graph endpoint
- `requests`

현재 중요한 구현 사실:

- local sidecar는 oversized full payload eager-load를 피한다.
- `LOCAL_SIDECAR_EAGER_LOAD_MAX_BYTES = 64 MiB`
- compact artifact를 우선 쓰고, full sidecar는 필요할 때만 제한적으로 읽는다.

즉 현재 graph path는:

- `local_sidecar` 우선 안정화
- 필요 시 `remote` / `neo4j`
- 실패 시 bounded local fallback

### 3.8 Answer assembly

주요 코드:

- `src/play_book_studio/answering/answerer.py`
- `src/play_book_studio/answering/context.py`
- `src/play_book_studio/answering/citations.py`
- `src/play_book_studio/answering/prompt.py`
- `src/play_book_studio/answering/llm.py`

하는 일:

- retrieval result를 context로 조립
- prompt build
- LLM 호출
- citation finalize
- mixed/private boundary가 있으면 truth label 유지

## 4. 조건부 보조선 vs 메인 spine

### 메인 spine

official lane:

- `manifest -> collect -> normalize -> chunk -> embed/qdrant -> playbook/runtime -> retrieval -> answer`

customer/private lane:

- `draft/create -> capture -> normalize -> playable books -> private corpus -> gated retrieval/viewer`

### 조건부 보조선

- `MarkItDown first`
  - `pdf/docx/pptx/xlsx`
- `Docling fallback`
  - PDF legacy/quality fallback
- `pypdf / mdls / string scan / pypdfium2 + RapidOCR`
  - PDF text recovery chain
- `Surya`
  - degraded PDF / low-confidence image OCR일 때 optional
- `CrossEncoder rerank`
  - query intent와 ambiguity 조건부
- `Neo4j / remote graph`
  - graph mode 조건부

## 5. 지금 파이프라인을 한 줄로 줄이면

### official source-first

`Foundry -> raw HTML collect -> canonical normalize -> chunks/playbooks -> embeddings/Qdrant -> retrieval/answer`

### customer/private

`Draft -> capture -> normalize(parse/fallback/evidence) -> playable books -> private corpus -> boundary-gated viewer/retrieval`

## 6. 지금 이 문서를 읽을 때 주의할 점

1. `PDF 메인 파서 = Docling`이라고만 이해하면 현재 코드와 어긋난다.
   - customer lane에서는 `MarkItDown first`가 먼저다.
2. `private boundary`는 한 단계가 아니라 cross-cutting gate다.
   - normalize, remote OCR, private corpus, retrieval, read surface에 모두 걸친다.
3. `graph`는 메인 진실 소스가 아니라 retrieval 보조층이다.
   - canonical truth는 여전히 structured book / playbook / chunk 쪽이다.
