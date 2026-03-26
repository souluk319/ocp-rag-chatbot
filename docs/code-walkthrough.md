# Code Walkthrough

이 문서는 이 저장소를 실제 코드 기준으로 설명할 때 쓰는 실전용 워크스루다.  
발표나 심사에서 가장 좋은 설명 순서는 `전체 흐름 -> 검색 -> 메모리 -> 캐시 -> 스트리밍 -> 제출 안전장치`다.

## 1. 1분 전체 흐름

1. 사용자가 `frontend/index.html`에서 질문을 입력한다.
2. `src/api/__init__.py`가 `/api/chat` 또는 `/api/chat/stream`으로 요청을 받는다.
3. `src/pipeline.py`가 세션 조회, query rewrite, embedding, cache lookup, retrieval, context build, LLM generation을 순서대로 실행한다.
4. `src/retriever/__init__.py`가 자체 IVF 인덱스와 BM25를 합쳐 문서를 찾고, reranking해서 context 후보를 만든다.
5. `src/llm/__init__.py`가 허용된 모델 `Qwen/Qwen3.5-9B`로만 응답을 생성한다.
6. 응답은 세션과 캐시에 저장되고, streaming 모드면 trace와 token 이벤트가 SSE로 흘러간다.

## 2. 발표 때 읽는 순서

### A. API부터 시작

가장 먼저 `src/api/__init__.py`를 보여주면 좋다.

- `startup()`에서 index, retriever, pipeline을 조립한다.
- `/api/chat`은 비스트리밍 경로다.
- `/api/chat/stream`은 SSE 경로다.
- `/api/stats`는 인덱스, 캐시, submission mode 상태를 보여준다.
- `/api/llm/endpoints`, `/api/llm/endpoint`, `/api/llm/health`는 제출 안전장치를 설명할 때 쓴다.

이 파일은 "사용자 요청이 시스템에 어떻게 들어오는가"를 설명하는 진입점이다.

### B. 파이프라인으로 넘어간다

그 다음은 `src/pipeline.py`다.

- `get_system_prompt()`는 운영/학습 모드 프롬프트를 나눈다.
- `build_user_prompt()`는 context와 질문을 실제 LLM 입력 형태로 묶는다.
- `RAGPipeline.query()`는 일반 응답 생성 경로다.
- `RAGPipeline.query_stream()`는 trace와 token 이벤트를 같이 보내는 스트리밍 경로다.

여기서 중요한 포인트는 "LLM을 바로 호출하지 않고, 그 전에 rewrite -> retrieval -> context build -> cache를 직접 거친다"는 점이다.

## 3. 검색 로직 설명

검색 설명은 `src/retriever/__init__.py` 하나로 충분하다.

### BM25Scorer

- 문서를 토큰화하고 BM25 점수를 계산한다.
- 코퍼스 전체를 대상으로 별도 검색도 할 수 있다.
- 복합 토큰(`ImagePullBackOff`, `CrashLoopBackOff`)과 한글/영문 동의어를 같이 처리한다.

### Retriever

- IVF 검색 후보와 BM25 후보를 합친다.
- `classify_query()`로 질의 유형을 분류한다.
- 트러블슈팅/개념/비교/개요에 따라 가중치를 다르게 준다.
- source prior를 사용해 OCP 도메인에서 중요한 문서를 위로 올린다.
- 한국어 문서 보정, 문서 다양성 제어, 인접 청크 확장을 적용한다.
- 마지막에 relevance 점수와 함께 context를 만든다.

심사에서 핵심적으로 말해야 하는 한 줄은 이것이다.  
`"검색 정확도를 위해 semantic search에 BM25, query-type reranking, source prior, adjacent chunk expansion을 합친 직접 구현형 retrieval을 사용했습니다."`

## 4. 멀티턴 메모리 설명

이 부분은 `src/session/__init__.py`를 보면 된다.

### Session / SessionManager

- 세션마다 user/assistant 메시지를 저장한다.
- 최근 N턴만 history로 꺼낸다.
- TTL 기반 만료 정리도 직접 한다.

### QueryRewriter

- 후속 질문을 독립형 질문으로 바꾼다.
- 짧은 질문, 대명사, `"그다음엔?"`, `"어디부터 봐야 해?"` 같은 표현을 감지한다.
- 먼저 heuristic fallback을 적용하고, 필요하면 LLM rewrite를 쓴다.

이렇게 설명하면 좋다.  
`"멀티턴은 LLM 히스토리에만 의존하지 않고, 세션 구조와 rewrite 단계에서 직접 맥락을 복원합니다."`

## 5. 캐시 설명

`src/cache/__init__.py`는 두 가지 포인트만 잡으면 된다.

- embedding cache: 같은 텍스트의 임베딩 재계산을 줄인다.
- semantic response cache: 유사 질문이면 LLM 호출을 생략한다.

설명 포인트:

- 같은 질문 반복에서 latency를 줄인다.
- 모드별 캐시 분리로 운영/학습 응답이 섞이지 않게 한다.
- 실패 응답은 캐시하지 않아 오답 고착을 막는다.

## 6. 벡터 인덱스 설명

`src/vectorstore/__init__.py`는 "직접 설계" 근거다.

- `IVFIndex`가 벡터 저장, KMeans 클러스터링, 검색, 저장/로드를 직접 관리한다.
- `n_probe`로 탐색 클러스터 수를 조절한다.
- 현재는 정확도 우선이라 `n_probe=16`으로 recall을 높였다.

심사에서 이렇게 말하면 된다.  
`"벡터 DB 프레임워크를 붙인 게 아니라, numpy 기반 IVF 인덱스를 직접 구현해서 구조와 파라미터를 설명할 수 있게 만들었습니다."`

## 7. LLM / 제출 안전장치 설명

`src/llm/__init__.py`와 `src/config.py`를 함께 보여주면 된다.

- 허용 모델은 `Qwen/Qwen3.5-9B`로 고정된다.
- `SUBMISSION_MODE=1`이면 endpoint switching이 막힌다.
- health 응답도 허용 모델만 보이게 제한한다.
- 프론트 심사 모드와 API 차단이 둘 다 들어가 있어, UI만 숨긴 게 아니다.

이 포인트는 과제 조건 방어용이다.

## 8. 스트리밍 설명

스트리밍은 `src/pipeline.py`와 `src/api/__init__.py`, `frontend/index.html`을 같이 보여주면 이해가 쉽다.

- 파이프라인이 `trace`, `rewrite`, `sources`, `token`, `done` 이벤트를 생성한다.
- API는 이를 SSE로 내보낸다.
- 프론트는 단계별 trace를 렌더링하고 token을 실시간으로 이어 붙인다.

즉, 이 시스템의 streaming은 "출력만 빠르게 보이는 기능"이 아니라 "RAG 파이프라인 자체를 관찰 가능한 형태로 드러내는 기능"이다.

## 9. 파일별 한 줄 설명

- `frontend/index.html`: 심사용 UI, trace, 심사 모드, 데모 런치패드
- `src/api/__init__.py`: API 엔트리포인트와 서비스 조립
- `src/pipeline.py`: 전체 RAG orchestration
- `src/retriever/__init__.py`: retrieval, reranking, context build
- `src/session/__init__.py`: 세션 메모리와 query rewrite
- `src/cache/__init__.py`: 응답/임베딩 캐시
- `src/vectorstore/__init__.py`: IVF 인덱스
- `src/llm/__init__.py`: OpenAI-compatible 모델 호출 및 model lock

## 10. 5분 설명 템플릿

1. `이 프로젝트는 사용자 -> RAG -> LLM 흐름 전체를 직접 구현한 OCP 지식 챗봇입니다.`
2. `검색은 IVF + BM25 + query-type reranking 구조라서 단순 임베딩 검색보다 도메인 정확도가 높습니다.`
3. `멀티턴은 세션 메모리와 query rewrite를 직접 관리해서 짧은 후속 질문도 독립형 질문으로 복원합니다.`
4. `스트리밍은 token만 흘리는 게 아니라 trace도 같이 보내서 retrieval 과정을 보여줍니다.`
5. `제출 모드에서는 모델을 Qwen/Qwen3.5-9B로 고정하고 endpoint 변경도 막아서 평가 조건을 코드 레벨에서 강제합니다.`

## 11. 마지막 한 줄

이 저장소를 설명할 때는 "좋은 답을 한다"보다 "왜 이 답이 나왔는지, 어떤 모듈이 책임지는지, 왜 직접 구현이라고 말할 수 있는지"를 항상 같이 말하면 된다.
