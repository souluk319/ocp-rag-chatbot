# File Role Guide

자주 헷갈리는 폴더만 적는다.

## root contracts

- `PROJECT.md`
  - 제품 정의와 phase/acceptance 기준
- `SYSTEM_RULES.md`
  - source trust, translation gate, merge/eval gate
- `TASK_BOARD.yaml`
  - phase/epic/task 단위 실행 계약
- `schemas/`
  - document/chunk/manualbook 산출물 스키마

## data

`data/`는 foundry lane 기준 디렉터리다.

- `bronze/`
  - 원문 수집 보관
- `silver/`
  - canonical 정규화 중간층
- `silver_ko/`
  - 영어 fallback의 한국어화 중간층
- `gold_corpus_ko/`
  - retrieval용 최종 한국어 코퍼스
- `gold_manualbook_ko/`
  - 읽기용 최종 한국어 매뉴얼북

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

## pipelines

`pipelines/`는 앞으로 collector/normalize/translate/chunk/index 실행 계약을 분리할 자리다.

## eval

`eval/`은 goldens/retrieval/answer/translation 기준선을 쌓는 자리다.

## reports

`reports/`는 build log와 eval report를 버전/phase 기준으로 남길 자리다.

## apps

`apps/`는 studio-ui/api/manualbook-viewer처럼 제품 표면을 분리하는 자리다.

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
