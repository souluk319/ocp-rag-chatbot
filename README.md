# OCP RAG Chatbot

OCP(OpenShift Container Platform) 운영 지식 기반 RAG 챗봇

## 개요

OCP 공식 문서 및 기술 자료를 기반으로 질의응답이 가능한 RAG(Retrieval-Augmented Generation) 챗봇입니다.
오픈소스 프레임워크(LangChain 등)를 사용하지 않고, 모든 RAG 파이프라인 컴포넌트를 구현했습니다.

### 주요 특징
- 프레임워크 없이 전체 RAG 파이프라인 구현
- IVF(Inverted File Index) 벡터 인덱스 설계 (numpy 기반 K-Means)
- Dual-Path 검색: IVF 벡터 검색 + BM25 독립 코퍼스 키워드 검색
- Semantic + BM25 하이브리드 Reranking (7:3 가중치)
- 인접 청크 확장 (Adjacent Chunk Expansion) — 검색된 청크의 앞뒤 ±2 청크 자동 병합
- 세션 기반 멀티턴 대화 지원 (5턴 이상, Query Rewriting)
- SSE 기반 실시간 토큰 스트리밍
- Pipeline Trace 패널 (LangSmith 유사 관찰가능성)
- 2단계 캐싱 (Embedding LRU + Semantic Response Cache)
- LLM 기반 합성 문서 자동 생성 (Synthetic Data Generation)

## 아키텍처

```
사용자 질의
    │
    ▼
[Web UI] ──SSE 스트리밍──▶ [FastAPI Server]
(Dark Theme,                     │
 Pipeline Trace,          ┌──────┼──────────────┐
 마크다운 렌더링)          ▼      ▼              ▼
                    Session   Semantic        Query
                    Manager   Cache           Rewriter
                    (대화 이력) (유사 질의 캐싱)  (맥락 기반 재구성)
                         │       │              │
                         └───────┼──────────────┘
                                 ▼
                          [Embedding Engine]
                          multilingual sentence-transformers + LRU 캐싱
                                 │
                    ┌────────────┼────────────┐
                    ▼                         ▼
             [IVF Vector Index]        [BM25 Corpus Search]
             K-Means 클러스터링         전체 코퍼스 키워드 검색
             n_probe=6 탐색            (IVF가 못 잡는 문서 보완)
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    [Hybrid Retriever + Reranker]
                    Semantic 70% + BM25 30% 결합
                                 │
                                 ▼
                    [Adjacent Chunk Expansion]
                    검색된 청크의 앞뒤 ±2 청크 병합
                                 │
                                 ▼
                    Context 구성 (max 4000자)
                                 │
                                 ▼
                    [LLM Client - Qwen3.5-9B]
                    토큰 단위 스트리밍
                                 │
                                 ▼
                   ┌─────────────┼───────────┐
                   ▼             ▼           ▼
               응답 반환      세션 저장    캐시 저장
```

### Pipeline Trace (관찰가능성)

각 파이프라인 단계의 실행 과정을 실시간으로 모니터링할 수 있는 Trace 패널:

```
Session  ✓  0ms   → session_id, history_turns
Rewrite  ✓  15ms  → original vs rewritten query
Embed    ✓  7ms   → dimension, cache_hit
Cache    — miss   → semantic_cache_size
Search   ✓  3ms   → candidates, top_score, IVF clusters
Rerank   ✓  2ms   → hybrid scores per document
Context  ✓  0ms   → context_length, num_documents
LLM      ✓  1.2s  → model, tokens, tokens/sec
Complete ✓  1.3s  → total pipeline time
```

## 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| Backend | Python 3.11+, FastAPI | REST API + SSE 스트리밍 |
| LLM | Qwen/Qwen3.5-9B | vLLM 서버, OpenAI-compatible API |
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 | 384차원, 다국어(한/영) 지원 |
| Vector Index | numpy IVF | K-Means 클러스터링 직접 구현 |
| Retrieval | Dual-Path (IVF + BM25) | 벡터 검색 + 독립 키워드 검색 병렬 |
| Reranking | Semantic + BM25 Hybrid | 7:3 가중치 하이브리드 스코어링 |
| Frontend | HTML/CSS/JS | 프레임워크 미사용, 다크 테마 |
| 문서 파싱 | PyPDF2, python-docx, python-pptx | 다양한 포맷 지원 |

## 프로젝트 구조

```
ocp-rag-chatbot/
├── src/                          # 핵심 RAG 파이프라인
│   ├── config.py                 # 전역 설정 관리 (.env 로드)
│   ├── pipeline.py               # RAG 오케스트레이터 + 트레이스
│   ├── api/                      # FastAPI 엔드포인트 (SSE)
│   ├── llm/                      # LLM 클라이언트 (Qwen3.5-9B)
│   ├── embedding/                # 임베딩 엔진 + LRU 캐싱
│   ├── vectorstore/              # IVF 벡터 인덱스 (직접 구현)
│   ├── retriever/                # Dual-Path 검색 + Hybrid Reranking
│   ├── chunker/                  # 문서 청킹 (Sliding Window)
│   ├── session/                  # 세션 관리 + Query Rewriting
│   └── cache/                    # Semantic Response Cache
├── frontend/
│   └── index.html                # 웹 UI (다크테마, Trace 패널)
├── scripts/
│   ├── scrape_docs.py            # OCP/K8s 공식 문서 스크래핑
│   ├── generate_docs.py          # LLM 기반 합성 문서 생성
│   ├── build_index.py            # 문서 인덱싱 (청킹→임베딩→IVF)
│   └── test_multiturn.py         # 멀티턴 대화 테스트
├── data/
│   ├── raw/                      # 원본 문서 (71개 파일)
│   │   └── cywell/               # Cywell 교육자료 (PPT, PDF)
│   └── index/                    # 벡터 인덱스 저장소
├── docs/
│   ├── rag-dependency-guide.md   # 패키지 의존성 맵 & 배포 가이드
│   ├── README-v1-initial.md      # 초기 버전 README
│   └── worklog-*.md              # 일별 워크로그
└── requirements.txt              # Python 의존성
```

## 실행 방법

```bash
# 1. 환경 설정
cp .env.example .env
# .env 파일에서 LLM_ENDPOINT를 실제 엔드포인트로 변경

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 데이터 수집 (선택)
python3 scripts/scrape_docs.py          # 공식 문서 스크래핑
python3 scripts/generate_docs.py        # LLM 기반 합성 문서 생성

# 4. 문서 인덱싱
python3 scripts/build_index.py

# 5. 서버 실행
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# 6. 브라우저 접속
# http://localhost:8000
```

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/chat` | 비스트리밍 채팅 |
| POST | `/api/chat/stream` | SSE 스트리밍 채팅 |
| GET | `/api/sessions` | 활성 세션 목록 |
| GET | `/api/session/{id}/history` | 세션 대화 이력 |
| GET | `/api/stats` | 시스템 상태 (캐시, 인덱스) |
| POST | `/api/cache/clear` | 시맨틱 캐시 초기화 |

## 핵심 설계 상세

### 1. IVF Vector Index (직접 구현)

FAISS 등의 라이브러리 없이 numpy만으로 구현한 벡터 검색 엔진:

```
전체 벡터 (7489개)
    │
    ▼ K-Means 클러스터링
[C0] [C1] [C2] ... [C15]    ← 16개 클러스터
                             ← 클러스터별 벡터 분배

검색 시:
Query 벡터 → 가장 가까운 n_probe(6)개 클러스터 선택
→ 해당 클러스터 내에서만 Cosine Similarity 계산
→ 전체 탐색 대비 속도 향상 (16개 중 6개만 탐색)
```

- K-Means 클러스터링 직접 구현 (Lloyd's algorithm)
- Cosine Similarity 기반 유사도 계산
- `n_probe` 파라미터로 정확도/속도 트레이드오프 조절 (3→6으로 상향, 7489 벡터 대응)
- 인덱스 저장/로드 지원 (vectors.npy, centroids.npy, index_meta.json)

### 2. Dual-Path 검색 + Hybrid Reranking

임베딩 벡터 검색과 BM25 키워드 검색을 병렬로 수행하여 상호 보완:

```
                    Query
                      │
           ┌──────────┼──────────┐
           ▼                     ▼
    [경로 1: IVF 검색]    [경로 2: BM25 코퍼스 검색]
    top_k × 3 = 15개      top_k × 2 = 10개
    (임베딩 유사도 기반)    (키워드 정확 매칭 기반)
           │                     │
           └──────────┬──────────┘
                      ▼
               중복 제거 + 합치기
               (BM25 전용 후보의 semantic score 계산)
                      │
                      ▼
            Hybrid Reranking
            Score = 0.7 × Semantic + 0.3 × BM25
                      │
                      ▼ 상위 top_k(5)개 선택
                      │
                      ▼
            Adjacent Chunk Expansion
            검색된 chunk의 앞뒤 ±2 청크 병합
            (같은 문서의 연속 청크를 합쳐서 문맥 보완)
```

**BM25 독립 검색이 필요한 이유:**
임베딩 모델이 특정 키워드("이미지 풀 에러")에 대해 낮은 유사도(0.12~0.42)를 반환할 때,
BM25가 키워드 정확 매칭으로 해당 문서를 찾아 보완합니다.

**인접 청크 확장이 필요한 이유:**
chunk 0(개요)만 검색되면 LLM이 해결 방법을 답변하지 못합니다.
인접 청크 확장으로 chunk 0 + 1 + 2를 합쳐서 진단 명령어와 해결 절차까지 context에 포함시킵니다.

### 3. Query Rewriter (멀티턴 지원)

멀티턴 대화에서 맥락 의존적 질문을 독립적 질문으로 변환:

| 대화 맥락 | 사용자 질문 | 재작성된 질문 |
|-----------|-----------|-------------|
| OCP Pod 설명 후 | "그건 뭐야?" | "OCP에서 Pod의 CrashLoopBackOff 상태란?" |
| Deployment 설명 후 | "더 알려줘" | "OCP Deployment의 롤링 업데이트 전략을 설명해줘" |
| 첫 질문 | "readiness probe가 뭐야?" | (변경 없음) |

### 4. 2단계 캐싱 전략

**Embedding Cache (LRU):**
- SHA256 해시 기반 키로 동일 텍스트의 중복 임베딩 방지
- 최대 5000개 캐시, OrderedDict 기반 LRU 구현

**Semantic Response Cache:**
- Cosine Similarity 임계값(0.95) 기반 유사 질의 매칭
- 캐시 히트 시 LLM 호출 없이 즉시 응답 (레이턴시 99% 감소)
- LRU 방식으로 최대 200개 캐시 항목 관리

### 5. 데이터 수집 전략

3가지 데이터 소스를 조합:

| 소스 | 방법 | 문서 수 | 특징 |
|------|------|--------|------|
| 직접 작성 | 한국어 기술 문서 | 9개 | 트러블슈팅 가이드 포함 (이미지풀/CrashLoop/Pending) |
| 웹 스크래핑 | 공식 문서 크롤링 | 20개 | OCP 4.17 공식 문서 기반 |
| LLM 합성 | Qwen3.5-9B 생성 | 8개 | 검수 필요, 빈 주제 보완 |
| 교육 자료 | PPTX/PDF 파싱 | 5개 | Cywell 교육자료 (PPT 1 + PDF 4) |

**텍스트 전처리:**
- 스크래핑 데이터의 공백 누락 자동 수정 (camelCase 경계 분리)
- K8s 기술 용어 보호 리스트 (StatefulSet 등 40개 용어)
- PPTX 임시 파일(~$) 자동 필터링

### 6. Streaming + Pipeline Trace

SSE(Server-Sent Events)를 통한 실시간 응답:
- 토큰 단위 스트리밍으로 체감 응답 속도 향상
- 각 파이프라인 단계별 trace 이벤트 전송
- 프론트엔드 Trace 패널에서 실시간 모니터링
- 단계별 소요 시간, 중간 결과, 메트릭 표시

## 설정 파라미터

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| CHUNK_SIZE | 512 | 청크 크기 (문자 수) |
| CHUNK_OVERLAP | 128 | 청크 간 겹침 크기 |
| TOP_K | 5 | 최종 검색 결과 수 |
| IVF_N_CLUSTERS | 16 | IVF 클러스터 수 |
| IVF_N_PROBE | 6 | 검색 시 탐색 클러스터 수 |
| CACHE_SIMILARITY_THRESHOLD | 0.95 | 캐시 히트 유사도 임계값 |
| MAX_HISTORY_TURNS | 10 | 최대 대화 이력 턴 수 |
| LLM_MAX_TOKENS | 2048 | LLM 최대 생성 토큰 |
| LLM_TEMPERATURE | 0.7 | LLM 생성 온도 |

## 주요 구현 체크리스트

### 필수 요구사항
- [x] RAG → LLM 파이프라인 + 웹 UI 직접 구현
- [x] Vector Index 직접 설계 (IVF - K-Means, numpy)
- [x] 멀티턴 대화 5턴 이상 (세션 + Query Rewriting)
- [x] LLM 연동 - Qwen/Qwen3.5-9B (vLLM)
- [x] Streaming 응답 (SSE 토큰 스트리밍)

### 추가 구현
- [x] Dual-Path 검색 (IVF 벡터 + BM25 독립 코퍼스 검색)
- [x] Hybrid Reranking (Semantic 70% + BM25 30%)
- [x] 인접 청크 확장 (Adjacent Chunk Expansion, ±2 window)
- [x] 2단계 캐싱 (Embedding LRU + Semantic Cache)
- [x] Pipeline Trace 관찰가능성 패널
- [x] LLM 기반 합성 문서 자동 생성
- [x] 텍스트 전처리 (스크래핑 데이터 정규화)
- [x] 한국어 트러블슈팅 문서 (이미지풀/CrashLoop/Pending)
- [x] 캐시 초기화 API
- [x] 한국어 IME 처리 (compositionstart/end)
- [x] 마크다운 렌더링
- [x] 다크 테마 UI

## 관련 문서

- [패키지 의존성 맵 & 배포 가이드](docs/rag-dependency-guide.md) — 오프라인/에어갭 배포 대비
- [초기 버전 README](docs/README-v1-initial.md) — Day 1~2 시점의 시스템 설명
