# Folder Restructure Draft

이 문서는 `feat/playbook-studio` 브랜치의 구조개편 기준 초안이다.

## 1. 구조개편 원칙

- `src/`에는 실제 로직만 둔다.
- `scripts/`는 얇은 진입점만 둔다.
- 무거운 `artifacts`는 repo 밖 외부 디렉토리로 유지한다.
- 전면 이사보다 `새 패키지 생성 -> 진입점 전환 -> 구패키지 shim 정리` 순서로 간다.

## 2. 최종 방향

### repo 안 코드 구조

```text
.
├─ manifests/
├─ scripts/
│  ├─ play_book.py
│  └─ check_runtime_endpoints.py
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
│     │  ├─ models.py
│     │  ├─ sources/
│     │  ├─ normalize/
│     │  ├─ chunking.py
│     │  ├─ indexing.py
│     │  ├─ qdrant_store.py
│     │  ├─ manifest.py
│     │  ├─ audit.py
│     │  └─ sentence_model.py
│     ├─ retrieval/
│     │  ├─ __init__.py
│     │  ├─ benchmark.py
│     │  ├─ bm25.py
│     │  ├─ models.py
│     │  ├─ query.py
│     │  ├─ retriever.py
│     │  ├─ sanity.py
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
│        ├─ retrieval_eval.py
│        ├─ answer_eval.py
│        └─ ragas_eval.py
├─ tests/
├─ play_book.cmd
├─ README.md
└─ PRODUCTIZATION_TODO.md
```

### repo 밖 데이터 구조

```text
..\\ocp-rag-chatbot-data\\
├─ part1/
├─ part2/
├─ part3/
├─ part4/
└─ raw_html/
```

## 3. 지금 단계의 실제 범위

이번 1차 구조개편은 전부 옮기지 않는다.

먼저 옮기는 축:

- `config`
- `retrieval`
- `answering`
- `app`
- `evals`

나중에 옮기는 축:

- `ingestion`
- 구패키지 shim 제거

## 4. scripts 와 src 경계

- `src/play_book_studio/...`
  - 실제 비즈니스 로직
- `scripts/play_book.py`
  - `play_book_studio.cli.main()` 호출만 담당
- 나머지 `run_part*.py`
  - 당장은 유지해도 되지만 점진적으로 축소 대상

## 5. server.py 분리 목표

현재 [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part4/server.py)는 너무 많은 책임을 가진다.

1차 분리 대상:

- `sessions.py`
  - `Turn`
  - `ChatSession`
  - `SessionStore`
- `presenters.py`
  - citation / book label / pack payload 직렬화 보조
- `viewers.py`
  - viewer path 파싱
  - 로컬 html 탐색

나중 분리 대상:

- doc-to-book draft 핸들링
- normalized viewer 렌더링
- chat payload assembly
- HTTP handler

## 6. 실제 이동 순서

1. `play_book_studio` 패키지 생성
2. `cli.py` 생성
3. `scripts/play_book.py`를 새 CLI로 전환
4. `app/sessions.py`, `app/presenters.py`, `app/viewers.py` 1차 분리
5. `config / retrieval / answering / evals` 최소 facade 생성
6. 이후 제품화 작업을 새 패키지 기준으로 진행

## 7. 한 줄 결론

이번 구조개편의 목적은 "예쁘게 정리"가 아니라,

- 문제 위치를 빨리 좁히고
- 제품화 실험이 가능한 새 기준 경로를 만들고
- 구구절절한 `part1~4` 중심 사고에서 빠져나오는 것

이다.
