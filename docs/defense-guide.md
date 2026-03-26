# Defense Guide

이 문서는 심사 중 코드 설명을 빠르게 방어하기 위한 발표용 치트시트다. 핵심은 `사용자 -> RAG -> LLM` 흐름을 직접 구현했고, 검색과 세션 메모리, 스트리밍, 캐시, 모델 제한을 모두 코드로 제어한다는 점이다.

## 30초 요약

이 프로젝트는 OCP 문서를 직접 수집하고, 자체 벡터 인덱스를 만든 뒤, 하이브리드 검색과 세션 메모리를 거쳐 Qwen/Qwen3.5-9B로 답변을 생성하는 RAG 챗봇이다.  
오픈소스 RAG 프레임워크에 의존하지 않고, 인덱스, 검색, 리라이트, 캐시, SSE 스트리밍, UI까지 직접 구현했다.

## 아키텍처 설명

`frontend/index.html`은 입력, 모드 선택, 심사 모드, trace, 데모 카드, 추천 질문을 담당한다.  
`src/api/__init__.py`가 FastAPI 엔드포인트를 제공하고, `src/pipeline.py`가 전체 오케스트레이션을 맡는다.  
`src/session/__init__.py`는 세션과 쿼리 재작성, `src/retriever/__init__.py`는 검색과 리랭킹, `src/cache/__init__.py`는 응답 캐시, `src/llm/__init__.py`는 OpenAI-compatible LLM 호출을 담당한다.  
`src/vectorstore/__init__.py`는 numpy 기반 IVF 인덱스를 직접 관리한다.

## Retrieval 설명

검색은 단순 벡터 검색이 아니라 `IVF + BM25 + reranking` 구조다.

1. 쿼리를 임베딩하고 IVF에서 1차 후보를 찾는다.
2. BM25로 전체 코퍼스에서 키워드 후보를 보강한다.
3. 쿼리 유형을 분류한다. 예를 들어 `troubleshooting`, `concept`, `comparison`, `overview`로 나눈다.
4. 유형에 따라 semantic/keyword 가중치를 다르게 준다.
5. OCP 도메인에 맞는 source prior, 복합어 확장, 한국어 보정, 선택적 인접 청크 확장을 적용한다.
6. 최종 context는 relevance 점수와 함께 잘라서 LLM에 전달한다.

심사에서 이렇게 말하면 된다.  
`"벡터 검색만 쓰면 정확도는 높아 보이지만 OCP처럼 문서명이 강한 도메인에서 키워드가 중요한 케이스를 놓치기 때문에, BM25와 source prior, chunk expansion을 같이 넣었습니다."`

## Memory 설명

멀티턴은 LLM의 대화 히스토리에만 의존하지 않고 `SessionManager`가 직접 관리한다.

1. 세션별로 user/assistant 메시지를 저장한다.
2. 최근 N턴만 `get_history()`로 가져온다.
3. `QueryRewriter`가 맥락 의존 질문을 독립형 질문으로 바꾼다.
4. 후속 질문이 너무 짧거나 `"어디부터 봐야 해?"`, `"그다음엔?"` 같은 형태면 휴리스틱 fallback을 먼저 쓴다.

심사 포인트는 이 부분이다.  
`"히스토리는 그냥 LLM에 통째로 넘기지 않고, 세션 객체와 rewrite 단계에서 직접 관리한다."`

## Streaming 설명

`/api/chat/stream`은 SSE로 동작한다. 파이프라인이 `trace`, `rewrite`, `sources`, `token`, `done` 같은 이벤트를 순서대로 내보내고, 프론트는 이를 받아서 토큰 단위로 화면에 뿌린다.  
즉, 스트리밍은 단순 출력이 아니라 파이프라인 진행 상황까지 같이 보이게 하는 관찰성 도구다.

심사에서 이렇게 말하면 된다.  
`"스트리밍은 LLM 토큰만 흘리는 게 아니라, rewrite, retrieval, rerank, context build, generation 단계를 trace 이벤트로 같이 보여줘서 디버깅 가능하게 만들었습니다."`

## Model Lock 설명

`SUBMISSION_MODE=1`이면 모델은 `Qwen/Qwen3.5-9B`로 고정된다.  
엔드포인트 전환 UI는 숨기고, `/api/llm/endpoint`는 차단한다. `/api/llm/endpoints`와 `/api/llm/health`는 허용 모델만 보이도록 제한한다.

이렇게 한 이유는 평가 조건이 특정 모델 고정이고, 데모 중 잘못된 endpoint로 바뀌는 리스크를 제거하기 위해서다.  
심사에서 이렇게 말하면 된다.  
`"운영 편의보다 제출 안정성을 우선했고, 평가 조건을 코드 레벨에서 강제했습니다."`

## Direct Implementation 설명

이 프로젝트가 과제 조건을 충족하는 이유는 다음과 같다.

1. RAG 파이프라인을 직접 구현했다.
2. vector index를 직접 설계하고 numpy로 관리했다.
3. session memory와 query rewrite를 직접 구현했다.
4. streaming, cache, reranking, chunk expansion을 직접 붙였다.
5. 오픈소스 RAG 프레임워크에 의존하지 않았다.

심사에서 `"프레임워크를 왜 안 썼냐"`는 질문에는 이렇게 답하면 된다.  
`"과제의 목적이 RAG 내부 구조 이해와 설명 능력이라, 검색/메모리/스트리밍/캐시를 블랙박스 없이 직접 구현해야 했습니다."`

## Tradeoffs

- `정확도 vs 단순성`: hybrid retrieval을 넣어 정확도를 올렸지만, 규칙과 가중치가 많아졌다.
- `재현성 vs 유연성`: submission mode와 model lock으로 안정성은 올렸지만 endpoint 자유도는 줄였다.
- `문맥 충분성 vs 노이즈`: adjacent chunk expansion을 하되 상위 결과에만 제한해서 context bloat를 막았다.
- `설명력 vs 완전 자동화`: heuristic rewrite를 넣어 멀티턴 안정성을 높였지만, 완전한 LLM-only 구성은 아니다.

## 자주 나오는 질문

- `"왜 단순 벡터 검색이 아니라 BM25를 같이 썼나?"` -> OCP 문서는 명령어, 에러명, 문서명 같은 정확 토큰이 중요해서다.
- `"왜 context를 길게 안 넣나?"` -> 길게 넣으면 노이즈와 비용이 늘어서 relevance가 떨어진다.
- `"캐시는 왜 필요한가?"` -> 같은 질문과 유사 질문이 반복되면 latency와 LLM 호출 비용을 줄일 수 있다.
- `"왜 모델을 잠갔나?"` -> 평가 조건과 데모 안정성을 코드로 보장하기 위해서다.

