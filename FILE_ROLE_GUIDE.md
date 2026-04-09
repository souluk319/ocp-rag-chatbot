# File Role Guide

자주 헷갈리는 폴더만 적는다.

## manifests

`manifests/`는 실행 결과물이 아니라 입력 선언 파일이다.

- `ocp_multiversion_html_single_catalog.json`
  - 수집 후보 전체 catalog
- `ocp_ko_4_20_approved_ko.json`
  - 현재 runtime 코퍼스 기준선
- `ocp_ko_4_20_translated_ko_draft.json`
  - 영어 fallback 문서의 번역 draft 대상
- `ocp_ko_4_20_corpus_working_set.json`
  - approved + translated draft를 합친 작업용 manifest
- `retrieval_*.jsonl`
  - retrieval 평가 질문 세트
- `answer_*.jsonl`
  - answer 평가 질문 세트
- `ragas_eval_cases.jsonl`
  - judge 평가 질문 세트
- `demo_safe_questions.jsonl`
  - 첫 화면 예시 질문과 시연용 single-turn 질문 기준선
- `demo_multiturn_scenarios.jsonl`
  - 멀티턴 시연/복구용 질문 시나리오 기준선

## scripts

`scripts/`는 얇은 실행 진입점이다.

- `play_book.py`
  - 메인 CLI
- `run_ingestion.py`
  - collect -> normalize -> chunk -> embed
- `build_source_approval.py`
  - approval / gap / translation lane report 생성
- `build_translation_draft_manifest.py`
  - 영어 fallback 문서를 translated draft로 올림
- `run_retrieval_eval.py`
  - retrieval 평가
- `run_answer_eval.py`
  - answer 평가
- `run_ragas_eval.py`
  - judge 평가
- `check_runtime_endpoints.py`
  - 시연 전 런타임 점검

## src/play_book_studio

- `canonical`
  - 코퍼스와 매뉴얼북이 같이 쓰는 공통 AST
- `ingestion`
  - 공식 문서 수집/정규화/청킹
- `retrieval`
  - query rewrite, BM25, vector, scoring
- `answering`
  - context, prompt, LLM, answer shaping
- `app`
  - server, session, viewer, static UI
- `evals`
  - 평가 실행 로직
