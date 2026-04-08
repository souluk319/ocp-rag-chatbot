# Folder Restructure Draft

이 문서는 `feat/playbook-studio` 브랜치의 구조개편 기준 초안이다.

## 1. 구조개편 원칙

- `src/`에는 실제 로직만 둔다.
- `scripts/`는 얇은 진입점만 둔다.
- 일회성 디버그 스크립트와 리포트는 `tmp/` 아래로 격리한다.
- 무거운 `artifacts`는 repo 밖 외부 디렉토리로 유지한다.
- 전면 이사보다 `새 패키지 생성 -> 진입점 전환 -> 구패키지 shim 정리` 순서로 간다.

## 2. 최종 방향

### repo 안 코드 구조

```text
.
├─ manifests/
├─ scripts/
│  ├─ play_book.py
│  ├─ check_runtime_endpoints.py
│  ├─ run_ingestion.py
│  ├─ run_retrieval_eval.py
│  ├─ run_answer_eval.py
│  └─ run_ragas_eval.py
├─ src/
│  └─ play_book_studio/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ config/
│     │  ├─ __init__.py
│     │  ├─ settings.py
│     │  └─ validation.py
│     ├─ ingestion/
│     │  ├─ __init__.py
│     │  ├─ audit.py
│     │  ├─ chunking.py
│     │  ├─ collector.py
│     │  ├─ embedding.py
│     │  ├─ manifest.py
│     │  ├─ models.py
│     │  ├─ normalize.py
│     │  ├─ pipeline.py
│     │  ├─ qdrant_store.py
│     │  ├─ sentence_model.py
│     │  └─ validation.py
│     ├─ intake/
│     │  ├─ __init__.py
│     │  ├─ models.py
│     │  ├─ planner.py
│     │  ├─ service.py
│     │  ├─ books/
│     │  ├─ capture/
│     │  └─ normalization/
│     ├─ retrieval/
│     │  ├─ __init__.py
│     │  ├─ bm25.py
│     │  ├─ models.py
│     │  ├─ query.py
│     │  ├─ retriever.py
│     │  └─ reranker.py
│     ├─ answering/
│     │  ├─ __init__.py
│     │  ├─ answerer.py
│     │  ├─ context.py
│     │  ├─ llm.py
│     │  ├─ models.py
│     │  ├─ prompt.py
│     │  └─ router.py
│     ├─ app/
│     │  ├─ __init__.py
│     │  ├─ server.py
│     │  ├─ sessions.py
│     │  ├─ presenters.py
│     │  ├─ viewers.py
│     │  └─ static/
│     └─ evals/
│        ├─ __init__.py
│        ├─ benchmark.py
│        ├─ retrieval_eval.py
│        ├─ answer_eval.py
│        ├─ ragas_eval.py
│        └─ sanity.py
├─ tests/
├─ play_book.cmd
├─ README.md
└─ PRODUCTIZATION_TODO.md
```

### repo 밖 데이터 구조

```text
..\\ocp-rag-chatbot-data\\
├─ corpus/
│  └─ raw_html/
├─ retrieval/
├─ answering/
├─ runtime/
└─ doc_to_book/
```

## 3. 지금 단계의 실제 범위

현재 단계 기준으로 이관 완료된 축:

- `config`
- `ingestion`
- `intake`
- `retrieval`
- `answering`
- `app`
- `evals`

남은 축:

- retrieval/runtime cluster 추가 분리
- intake normalization 잔여 helper 분리
- app/static의 shell/helper 잔여 분리
- 문서 최종 동기화

## 4. scripts 와 src 경계

- `src/play_book_studio/...`
  - 실제 비즈니스 로직
- `scripts/play_book.py`
  - `play_book_studio.cli.main()` 호출만 담당
- `scripts/check_runtime_endpoints.py`
  - 런타임 endpoint 확인용 공식 진단 스크립트
- `scripts/run_*.py`
  - 기능별 진단/평가/단건 실행 진입점
- `tmp/`
  - scratch/debug/test 산출물과 one-off 스크립트 보관용

## 5. server.py 분리 목표

현재 [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/server.py)는 여전히 많은 책임을 가지지만, 1차 분리는 이미 진행됐다.

이미 분리된 축:

- `chat_debug.py`
- `intake_api.py`
- `source_books.py`
- `session_flow.py`

남은 분리 후보:

- route registration/helper
- HTTP response writer
- runtime refresh / health assembly

나중 분리 대상:

- retrieval/query 대형 파일이 줄어든 뒤 다시 판단

## 6. 실제 이동 순서

1. `play_book_studio` 패키지 생성
2. `cli.py` 생성
3. `scripts/play_book.py`를 새 CLI로 전환
4. `app/sessions.py`, `app/presenters.py`, `app/viewers.py` 1차 분리
5. `config / retrieval / answering / evals` 최소 facade 생성
6. `intake`, `server`, `frontend renderer` 축 분리
7. 이후 retrieval/query 대형 파일 구조개편

## 7. 한 줄 결론

이번 구조개편의 목적은 "예쁘게 정리"가 아니라,

- 문제 위치를 빨리 좁히고
- 제품화 실험이 가능한 새 기준 경로를 만들고
- 구구절절한 단계명 중심 사고에서 빠져나오는 것

이다.
