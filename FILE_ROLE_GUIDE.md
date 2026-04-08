# File Role Guide

이 문서는 `manifests/`와 `scripts/`처럼 파일 안에 직접 설명을 넣기 어렵거나, 파일 수가 많아서 첫눈에 역할이 안 들어오는 영역을 정리한 가이드다.

특히 `JSON/JSONL` 파일은 주석을 넣을 수 없기 때문에, 아래 설명을 기준으로 먼저 역할을 파악하고 더 궁금한 파일만 열어보면 된다.

## 1. manifests 폴더

`manifests/`는 실행 결과물이 아니라, **무엇을 수집하고 무엇을 평가할지 정하는 선언 파일 폴더**다.

### 1.1 source / corpus 관련

| 파일 | 역할 | 언제 손대는지 |
|---|---|---|
| `ocp_ko_4_20_html_single.json` | Red Hat OCP 4.20 한국어 `html-single` source catalog 전체 목록 | 원문 문서 목록을 새로 수집하거나 업데이트 차이를 볼 때 |
| `ocp_ko_4_20_approved_ko.json` | 실제 runtime/citation 코퍼스로 승인된 한국어 문서 목록 | 승인 기준이 바뀌거나 새 문서를 runtime에 포함할 때 |

같이 자주 보는 외부 산출물:

- `../ocp-rag-chatbot-data/corpus/source_approval_report.json`
  - 현재 승인 상태, fallback 여부, 책별 한글 비율을 본다.
- `../ocp-rag-chatbot-data/corpus/corpus_gap_report.json`
  - high-value 문서를 `translation_first / manual_review_first`로 나눈 다음 보강 순서를 본다.

### 1.2 retrieval 평가 관련

| 파일 | 역할 | 언제 쓰는지 |
|---|---|---|
| `retrieval_smoke_queries.jsonl` | retrieval이 살아 있는지만 보는 아주 작은 smoke 세트 | endpoint/collection 전환 직후 1차 확인 |
| `retrieval_sanity_cases.jsonl` | 최소 품질 게이트용 sanity 세트 | 큰 변경 뒤 간단한 회귀 확인 |
| `retrieval_eval_cases.jsonl` | 기본 retrieval 평가 세트 | 일반적인 검색 품질 비교 |
| `retrieval_root_cause_cases.jsonl` | miss 원인 재현용 세트 | 특정 실패를 다시 재현하고 파고들 때 |
| `retrieval_benchmark_cases.jsonl` | 비교 실험용 benchmark 세트 | shaping/reranker/코퍼스 변경 전후 비교. `ops / learn / follow_up / ambiguous`를 함께 본다 |

### 1.3 answer / RAGAS 평가 관련

| 파일 | 역할 | 언제 쓰는지 |
|---|---|---|
| `answer_eval_cases.jsonl` | 현재 기본 answer eval 세트 | `play_book.cmd eval` 기본값 |
| `answer_eval_realworld_cases.jsonl` | 더 실전형인 보조 answer eval 세트 | follow-up, 주제 전환, 실무형 질문을 더 세게 확인할 때 |
| `ragas_eval_cases.jsonl` | RAGAS judge 평가 세트 | faithfulness / answer relevancy 경향을 볼 때 |

## 2. scripts 폴더

`scripts/`는 가능한 한 **얇은 실행 진입점**만 두는 게 기준이다.  
진짜 로직은 `src/play_book_studio/` 아래에 있고, 이 폴더는 사람이 직접 실행하기 쉬운 entrypoint를 모아둔다.

### 2.1 제품/운영 실행

| 파일 | 역할 | 메모 |
|---|---|---|
| `play_book.py` | `play_book.cmd`가 호출하는 메인 CLI 진입점 | 실제 명령 처리는 `src/play_book_studio/cli.py` |
| `check_runtime_endpoints.py` | 현재 runtime endpoint/health/report 점검 | 시연 전 점검에 자주 씀 |

### 2.2 ingestion / corpus 구축

| 파일 | 역할 | 메모 |
|---|---|---|
| `build_source_manifest.py` | source manifest/catalog 갱신 | 문서 업데이트 추적 시작점 |
| `build_source_approval.py` | approved 코퍼스/approval report 생성 | runtime 코퍼스 기준선 고정 |
| `run_ingestion.py` | collect -> normalize -> chunk -> embed -> qdrant 전체 실행 | 코퍼스 재구축 표준 진입점 |
| `audit_ingestion_data_quality.py` | 정규화/청킹 품질 감사 | 코퍼스 품질 이슈 점검 |
| `validate_ingestion_outputs.py` | ingestion 산출물 스키마/파일 존재 검증 | 중간 산출물 점검 |

### 2.3 retrieval 디버깅 / 평가

| 파일 | 역할 | 메모 |
|---|---|---|
| `run_retrieval_query.py` | 단일 질문 retrieval trace 출력 | 왜 이 문서를 집었는지 볼 때 |
| `run_retrieval_smoke.py` | retrieval smoke 세트 실행 | 빠른 생존 확인 |
| `run_retrieval_sanity.py` | retrieval sanity 세트 실행 | 최소 품질 게이트 |
| `run_retrieval_eval.py` | 기본 retrieval eval 실행 | hit@k 비교의 기준 |
| `run_retrieval_benchmark.py` | retrieval benchmark 실행 | 실험 전후 비교용 |

### 2.4 answer / LLM 디버깅 / 평가

| 파일 | 역할 | 메모 |
|---|---|---|
| `run_answer_query.py` | 단일 질문 answer JSON 출력 | UI 없이 answerer 직접 확인 |
| `run_answer_eval.py` | answer eval 세트 실행 | `play_book.cmd eval`와 같은 계열 |
| `run_ragas_eval.py` | RAGAS judge 실행 | 정합성/관련성 경향 확인 |

## 3. 처음 보는 사람이 먼저 열어볼 것

파일을 하나씩 이해하고 싶다면 순서는 이 정도가 좋다.

1. `scripts/play_book.py`
2. `src/play_book_studio/cli.py`
3. `manifests/answer_eval_cases.jsonl`
4. `scripts/run_answer_eval.py`
5. `manifests/retrieval_eval_cases.jsonl`
6. `scripts/run_retrieval_eval.py`
7. `scripts/run_ingestion.py`
8. `manifests/ocp_ko_4_20_approved_ko.json`

이 순서면:
- 제품 실행 진입점
- 기본 평가 세트
- 검색 평가 세트
- 코퍼스 구축 기준
을 한 번에 연결해서 이해할 수 있다.

## 4. 파일을 물어볼 때 기준

앞으로 파일을 하나씩 볼 때는 아래 질문으로 보면 된다.

1. 이 파일은 **실행 진입점**인가, **로직**인가, **데이터 선언**인가?
2. 이 파일은 **runtime**에서 쓰이나, **평가**에서만 쓰이나?
3. 이 파일을 바꾸면 **어떤 명령**이 바로 영향을 받나?
4. 이 파일은 **기준선**인가, **실험 보조**인가?

이렇게 보면 “파일이 많아서 복잡하다”가 아니라, “이 파일은 어디 축에 속한다”로 이해하기 쉬워진다.
