# Folder Restructure Draft

이 문서는 **실제 폴더 재배치 초안**이다.

목표는 세 가지다.

1. 문제 발생 시 기능 기준으로 한 번에 위치를 좁힐 수 있어야 한다.
2. 제품 기준 실행 경로는 `play_book.cmd` 하나로 유지되어야 한다.
3. 전면 이사보다 `안전한 단계 이동 + 호환 레이어` 방식으로 진행해야 한다.

## 1. 현재 구조의 문제

현재 구조는 `part1~4`가 기능보다 **개발 단계 이름**에 가깝다.

- `ocp_rag_part1`: corpus 준비
- `ocp_rag_part2`: retrieval
- `ocp_rag_part3`: answering
- `ocp_rag_part4`: app runtime

이 구조는 내부 제작 순서를 기억하기엔 좋지만, 제품 유지보수 기준에선 불리하다.

- 검색 문제인데 `part2`를 떠올려야 한다
- 답변 문제인데 `part3`를 떠올려야 한다
- intake는 `ocp_doc_to_book`로 따로 흩어져 있다
- 실행 스크립트도 `run_part*.py`가 너무 많다

즉 지금은 “어떻게 만들었는가”가 보이지, “무엇이 어디 있는가”가 직관적이지 않다.

## 2. 목표 구조

새 기준 패키지는 `src/play_book_studio/` 하나로 모은다.

```text
src/
└─ play_book_studio/
   ├─ __init__.py
   ├─ config/
   │  ├─ __init__.py
   │  ├─ settings.py
   │  └─ validation.py
   ├─ corpus/
   │  ├─ __init__.py
   │  ├─ audit.py
   │  ├─ chunking.py
   │  ├─ collector.py
   │  ├─ embedding.py
   │  ├─ manifest.py
   │  ├─ models.py
   │  ├─ normalize.py
   │  ├─ pipeline.py
   │  ├─ qdrant_store.py
   │  └─ sentence_model.py
   ├─ retrieval/
   │  ├─ __init__.py
   │  ├─ benchmark.py
   │  ├─ bm25.py
   │  ├─ models.py
   │  ├─ query.py
   │  ├─ retriever.py
   │  └─ sanity.py
   ├─ answering/
   │  ├─ __init__.py
   │  ├─ answerer.py
   │  ├─ context.py
   │  ├─ llm.py
   │  ├─ models.py
   │  ├─ prompt.py
   │  └─ router.py
   ├─ app/
   │  ├─ __init__.py
   │  ├─ server.py
   │  └─ static/
   ├─ intake/
   │  ├─ __init__.py
   │  ├─ models.py
   │  ├─ service.py
   │  ├─ books/
   │  │  ├─ __init__.py
   │  │  └─ store.py
   │  ├─ ingestion/
   │  │  ├─ __init__.py
   │  │  ├─ capture.py
   │  │  ├─ pdf.py
   │  │  └─ web.py
   │  └─ normalization/
   │     ├─ __init__.py
   │     ├─ pdf.py
   │     └─ service.py
   └─ evals/
      ├─ __init__.py
      ├─ answer_eval.py
      ├─ ragas_eval.py
      └─ retrieval_eval.py
```

핵심 원칙:

- `config`: 환경설정과 검증
- `corpus`: 문서 준비와 적재
- `retrieval`: 검색
- `answering`: grounded answer generation
- `app`: 서버와 UI
- `intake`: 업로드 문서 처리
- `evals`: 평가

## 3. old -> new 파일 매핑

### 3.1 config

```text
src/ocp_rag_part1/settings.py     -> src/play_book_studio/config/settings.py
src/ocp_rag_part1/validation.py   -> src/play_book_studio/config/validation.py
```

### 3.2 corpus

```text
src/ocp_rag_part1/audit.py          -> src/play_book_studio/corpus/audit.py
src/ocp_rag_part1/chunking.py       -> src/play_book_studio/corpus/chunking.py
src/ocp_rag_part1/collector.py      -> src/play_book_studio/corpus/collector.py
src/ocp_rag_part1/embedding.py      -> src/play_book_studio/corpus/embedding.py
src/ocp_rag_part1/manifest.py       -> src/play_book_studio/corpus/manifest.py
src/ocp_rag_part1/models.py         -> src/play_book_studio/corpus/models.py
src/ocp_rag_part1/normalize.py      -> src/play_book_studio/corpus/normalize.py
src/ocp_rag_part1/pipeline.py       -> src/play_book_studio/corpus/pipeline.py
src/ocp_rag_part1/qdrant_store.py   -> src/play_book_studio/corpus/qdrant_store.py
src/ocp_rag_part1/sentence_model.py -> src/play_book_studio/corpus/sentence_model.py
```

### 3.3 retrieval

```text
src/ocp_rag_part2/benchmark.py   -> src/play_book_studio/retrieval/benchmark.py
src/ocp_rag_part2/bm25.py        -> src/play_book_studio/retrieval/bm25.py
src/ocp_rag_part2/models.py      -> src/play_book_studio/retrieval/models.py
src/ocp_rag_part2/query.py       -> src/play_book_studio/retrieval/query.py
src/ocp_rag_part2/retriever.py   -> src/play_book_studio/retrieval/retriever.py
src/ocp_rag_part2/sanity.py      -> src/play_book_studio/retrieval/sanity.py
src/ocp_rag_part2/eval.py        -> src/play_book_studio/evals/retrieval_eval.py
```

### 3.4 answering

```text
src/ocp_rag_part3/answerer.py -> src/play_book_studio/answering/answerer.py
src/ocp_rag_part3/context.py  -> src/play_book_studio/answering/context.py
src/ocp_rag_part3/llm.py      -> src/play_book_studio/answering/llm.py
src/ocp_rag_part3/models.py   -> src/play_book_studio/answering/models.py
src/ocp_rag_part3/prompt.py   -> src/play_book_studio/answering/prompt.py
src/ocp_rag_part3/router.py   -> src/play_book_studio/answering/router.py
src/ocp_rag_part3/eval.py     -> src/play_book_studio/evals/answer_eval.py
src/ocp_rag_part3/ragas_eval.py -> src/play_book_studio/evals/ragas_eval.py
```

### 3.5 app

```text
src/ocp_rag_part4/server.py         -> src/play_book_studio/app/server.py
src/ocp_rag_part4/static/*          -> src/play_book_studio/app/static/*
```

### 3.6 intake

```text
src/ocp_doc_to_book/models.py                  -> src/play_book_studio/intake/models.py
src/ocp_doc_to_book/service.py                 -> src/play_book_studio/intake/service.py
src/ocp_doc_to_book/books/store.py             -> src/play_book_studio/intake/books/store.py
src/ocp_doc_to_book/ingestion/capture.py       -> src/play_book_studio/intake/ingestion/capture.py
src/ocp_doc_to_book/ingestion/pdf.py           -> src/play_book_studio/intake/ingestion/pdf.py
src/ocp_doc_to_book/ingestion/web.py           -> src/play_book_studio/intake/ingestion/web.py
src/ocp_doc_to_book/normalization/pdf.py       -> src/play_book_studio/intake/normalization/pdf.py
src/ocp_doc_to_book/normalization/service.py   -> src/play_book_studio/intake/normalization/service.py
```

## 4. scripts 재배치 초안

스크립트도 역할 기준으로 정리한다.

```text
scripts/
├─ play_book.py              # canonical entrypoint 유지
├─ runtime/
│  └─ check_runtime_endpoints.py
├─ corpus/
│  ├─ build_source_approval.py
│  ├─ build_source_manifest.py
│  ├─ run_corpus_pipeline.py      # run_part1.py 대체
│  ├─ audit_data_quality.py       # audit_part1_data_quality.py 대체
│  └─ validate_outputs.py         # validate_part1_outputs.py 대체
├─ retrieval/
│  ├─ eval.py                     # run_part2_eval.py 대체
│  ├─ sanity.py                   # run_part2_sanity.py 대체
│  ├─ benchmark.py                # run_part2_benchmark.py 대체
│  ├─ smoke.py                    # run_part2_smoke.py 대체
│  └─ inspect.py                  # run_part2_retrieval.py 대체
├─ evals/
│  ├─ answer_eval.py              # run_part3_eval.py 대체
│  └─ ragas_eval.py               # run_part3_ragas_eval.py 대체
└─ legacy/
   ├─ run_part1.py
   ├─ run_part2_*.py
   ├─ run_part3_*.py
   └─ run_part4_ui.py
```

정리 원칙:

- `play_book.py`는 유지
- 새 이름이 준비되면 `run_part*.py`는 `scripts/legacy/`로 이동
- 문서와 운영 가이드는 새 경로만 가리키게 변경

## 5. tests 재배치 초안

테스트도 기능 기준 디렉터리로 나누는 편이 맞다.

```text
tests/
├─ config/
├─ corpus/
├─ retrieval/
├─ answering/
├─ app/
├─ intake/
└─ evals/
```

예:

```text
tests/test_part2_retrieval.py -> tests/retrieval/test_retriever.py
tests/test_part3_answerer.py  -> tests/answering/test_answerer.py
tests/test_part4_ui.py        -> tests/app/test_server_and_ui.py
tests/test_settings_paths.py  -> tests/config/test_settings.py
```

## 6. 호환 레이어 초안

전면 이동 시 import 파손을 막기 위해 **한 턴에 다 지우지 않는다.**

### 6.1 1단계

- 새 패키지 `play_book_studio` 생성
- 새 위치로 코드 복사/이동
- `play_book.cmd`, `scripts/play_book.py`는 새 패키지만 보게 수정

### 6.2 2단계

기존 패키지는 shim으로 남긴다.

예:

```python
# src/ocp_rag_part3/answerer.py
from play_book_studio.answering.answerer import *  # noqa
```

이렇게 두면:

- 기존 테스트
- 기존 스크립트
- 외부에서 쓰던 import

를 한 번에 다 안 깨도 된다.

### 6.3 3단계

- 테스트와 스크립트 import를 새 경로로 전부 전환
- 레거시 shim 사용처가 0이 되면 구패키지 삭제

## 7. 실제 이동 순서

이 순서로 가는 게 제일 안전하다.

1. `config`, `retrieval`, `answering`, `app` 새 패키지 생성
2. `play_book.py`를 새 패키지 import로 전환
3. `tests`를 새 경로 import 기준으로 정리
4. `corpus`와 `intake` 이동
5. `scripts/legacy/` 분리
6. 마지막에 `ocp_rag_part1~4`, `ocp_doc_to_book` shim 제거

## 8. 첫 번째 실제 이관 단위

처음부터 전부 옮기지 않는다.

### 범위

- `src/ocp_rag_part1/settings.py`
- `src/ocp_rag_part1/validation.py`
- `src/ocp_rag_part2/*`
- `src/ocp_rag_part3/*`
- `src/ocp_rag_part4/server.py`
- `src/ocp_rag_part4/static/*`

### 이유

- 지금 제품 런타임의 핵심은 `config + retrieval + answering + app`
- 사용자가 실제로 매일 보는 동작은 여기서 결정된다
- `intake/corpus`는 그 다음으로 분리해도 된다

## 9. 이 초안의 의도

이 문서는 “언젠가 예쁘게 고치자”가 아니라, 실제로 다음 구조개편 턴에서 바로 적용할 수 있는 **실행 가능한 초안**이다.

한 줄 결론:

- 루트 실행 진입점은 `play_book.cmd` 유지
- 내부 패키지는 `play_book_studio` 아래 기능 기준으로 재배치
- 구패키지는 shim으로 한 번 더 거쳐서 안전하게 제거
