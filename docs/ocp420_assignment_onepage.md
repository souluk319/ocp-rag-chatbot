# OCP 4.20 Assignment One-Page Review

## What This Product Is

`PlayBookStudio (PBS)` 는 공식 OCP 문서와 업로드 문서를 같은 제품 안에서 `읽기 가능한 Playbook` 과 `검색 가능한 Corpus` 로 연결하는 RAG studio다.

- UI surface: `Playbook Library / Wiki Runtime Viewer / Chat Workspace`
- LLM: `Qwen/Qwen3.5-9B`
- Embedding: `BGE-m3`
- Vector store: `Qdrant`
- Sparse retrieval: repo 내부 구현 `BM25Index`
- Streaming: `POST /api/chat/stream`
- 멀티턴 memory: `SessionContext + turn history` 직접 관리
- 외부 orchestration framework: `미사용`

## Direct-Built Pipeline

`사용자 질문 -> query normalize -> query rewrite -> BM25/vector 검색 -> hybrid fusion -> graph expand(optional) -> rerank -> context assemble -> LLM answer -> citation finalize`

핵심 파일:

- retrieval orchestration: [retriever_pipeline.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/retriever_pipeline.py:1)
- sparse index: [bm25.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/bm25.py:1)
- vector retrieval: [vector.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/vector.py:1)
- answer context: [context.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/context.py:1)
- answer orchestration: [answerer.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/answerer.py:1)
- streaming/chat API: [server_chat.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/server_chat.py:1)
- session memory: [sessions.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/sessions.py:1), [session_flow.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/session_flow.py:140)

## Why It Meets The Rubric

| 평가 항목 | PBS에서 보여줄 것 |
| --- | --- |
| `RAG 정확성` | citation 기반 답변, 공식 OCP 문서 grounding, 문서 밖 명령 억제 |
| `멀티턴 처리 정확성` | 5턴 이상에서 `current_topic`, `history_size`, follow-up 유지 |
| `시스템 아키텍처` | sparse+dense+hybrid+rerank+graph 옵션을 각 모듈로 분리 |
| `코드 품질 및 설명` | retrieval, session, streaming, citation 책임이 파일 단위로 분리 |
| `추가 요구사항` | streaming, cache, rerank, session memory, simulator evidence 존재 |

## Live Demo Order

짧은 시연은 아래 3개만 돌린다.

1. `RBAC namespace admin 6-turn`
2. `Architecture to MCO shift 6-turn`
3. `etcd backup restore 6-turn`

풀 시연은 아래 5개를 돌린다.

1. `RBAC namespace admin 6-turn`
2. `Architecture to MCO shift 6-turn`
3. `etcd backup restore 6-turn`
4. `Deployment scaling 6-turn`
5. `Machine Config Operator 6-turn`

상세 대본: [ocp420_assignment_demo_runbook.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/docs/ocp420_assignment_demo_runbook.md:1)

## Verified Evidence

- simulator scenarios: `5`
- total turns: `30`
- `scenario_completion_rate = 1.0`
- `turn_pass_rate = 1.0`
- `streaming_turn_pass_rate = 1.0`
- `hallucination_guard_pass_rate = 1.0`
- `history_pass_rate = 1.0`

evidence:

- [ocp420_demo_simulator_eval.json](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/reports/demo_simulator/ocp420_demo_simulator_eval.json:1)
- [README.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/README.md:1)

## Before Presentation

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_submission_demo_checks.ps1
```

라이브 점검 항목:

- backend health
- active model / embedding / reranker / qdrant 상태

시뮬레이터까지 다시 돌리려면:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_submission_demo_checks.ps1 -RunSimulator
```

## One-Line Pitch

`PBS는 OCP 공식 문서를 직접 구축한 RAG 파이프라인 위에 올려, 읽기용 Playbook과 챗봇용 Corpus를 같은 근거 체계로 제공하는 멀티턴 운영 지식 스튜디오다.`
