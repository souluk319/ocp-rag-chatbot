# OCP RAG Chatbot

OCP(OpenShift Container Platform) 운영 지식 기반 RAG 챗봇  
Mobile 대응

## 개요

OCP 공식 문서 및 기술 자료를 기반으로 질의응답이 가능한 RAG(Retrieval-Augmented Generation) 챗봇입니다.
RAG 파이프라인의 각 컴포넌트(인덱싱, 검색, 리랭킹, 캐싱 등)를 개별 모듈로 구성했습니다.

**[테스트 서버 URL](https://hillary-unsecluding-unphilosophically.ngrok-free.dev/)**  (로컬호스트 연결되어있을 때만 가능함)  

> 📄 **[파이프라인 구조 설명 자료 (PDF)](docs/OCP_Hybrid_RAG.pdf)** — 전체 아키텍처와 설계 정리 자료  
> 🎬 **[프로젝트 설계 영상](https://youtu.be/zeXrMJcLidg)** — 파이프라인 구조와 설계 의사결정 설명  
> 🎬 **[개인 학습 영상](https://youtu.be/MCdhsMPzt5o)** — RAG 개념 및 구현 과정 학습 정리  

### 주요 특징
- RAG 파이프라인 (인덱싱 → 검색 → 리랭킹 → 응답)
- IVF(Inverted File Index) 벡터 인덱스 설계 (numpy 기반 K-Means)
- Dual-Path 검색: IVF 벡터 검색 + BM25 독립 코퍼스 키워드 검색
- **쿼리 유형별 동적 하이브리드 Reranking** (트러블슈팅 6:4, 개념 8:2, 기본 7:3)
- **에러 복합어 확장 BM25** (`ImagePullBackOff`, `CrashLoopBackOff`, `PullSecret` 등 복합 토큰 분해)
- **한국어 쿼리 시 한국어 문서 부스트** (+0.08 스코어 보정)
- **선택적 인접 청크 확장** — 상위 결과에만 앞뒤 청크를 붙여 문맥은 늘리고 노이즈는 줄임
- 세션 기반 멀티턴 대화 지원 (10턴, Few-shot Query Rewriting)
- SSE 기반 실시간 토큰 스트리밍
- Pipeline Trace 패널 (LangSmith 유사 관찰가능성)
- 2단계 캐싱 (Embedding LRU + Semantic Response Cache, 3중 호환성 검증)
- **듀얼 모드 시스템** (운영 모드 / 학습 모드, 모드별 시스템 프롬프트)
- **심사 모드 UI** (Qwen/Qwen3.5-9B 고정 안내, 엔드포인트 전환 숨김, 데모 런치패드)
- **Perplexity 스타일 후속 추천 질문** (클릭으로 이어서 질문)
- LLM 기반 합성 문서 자동 생성 (Synthetic Data Generation)
- **fixture 기반 평가 러너** (JSON API / SSE 둘 다 재현 가능)
- **제출 안전장치** (기본값 Submission Mode, 허용 모델 `Qwen/Qwen3.5-9B` 고정)
- 멀티 엔드포인트 라우팅 지원 (발표/개발 모드에서만 전환 노출)

## 아키텍처

```
사용자 질의
    │
    ▼
[Web UI] ──SSE 스트리밍──▶ [FastAPI Server]
(Warm Light Theme,               │
 Dual Mode,              ┌──────┼──────────────┐
 Pipeline Trace,         ▼      ▼              ▼
 추천 질문,           Session   Semantic        Query
 마크다운 렌더링)     Manager   Cache           Rewriter
                    (대화 이력) (3중 호환성 검증)  (Few-shot 기반)
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
             n_probe=16 전수탐색       91쌍 동의어 + 쿼리 확장
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    [Query Classifier]
                    쿼리 유형 자동 분류 (6가지)
                                 │
                                 ▼
                    [Hybrid Retriever + Reranker]
                    쿼리 유형별 동적 가중치 + 한국어 문서 부스트
                    + 소스 다양성 제어 (max_per_source=1)
                                 │
                                 ▼
                    [Adjacent Chunk Expansion]
                    상위 결과만 앞뒤 청크 선택 병합
                                 │
                                 ▼
                    Context 구성 (max 5600자)
                                 │
                                 ▼
                    [LLM Client - Submission Safe]
                    듀얼 모드 시스템 프롬프트 (운영/학습)
                    허용 모델: Qwen/Qwen3.5-9B 고정
                    토큰 단위 스트리밍
                                 │
                                 ▼
                   ┌─────────────┼───────────┐
                   ▼             ▼           ▼
               응답 반환      세션 저장    캐시 저장
               + 추천 질문                (실패 응답 제외)
```

### Pipeline Trace (관찰가능성)

각 파이프라인 단계의 실행 과정을 실시간으로 모니터링할 수 있는 Trace 패널:

```
Session  ✓  0ms   → session_id, history_turns
Rewrite  ✓  15ms  → original vs rewritten query, query_type, entity
Embed    ✓  7ms   → dimension, cache_hit
Cache    — miss   → semantic_cache_size
Search   ✓  26ms  → candidates, top_score, IVF n_probe=16
Rerank   ✓  120ms → hybrid scores per document (semantic + keyword + ko_boost)
Context  ✓  0ms   → context_length, num_documents
LLM      ✓  1.2s  → model, tokens, tokens/sec
Complete ✓  1.3s  → total pipeline time
```

## 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| Backend | Python 3.13, FastAPI | REST API + SSE 스트리밍 |
| LLM | Qwen/Qwen3.5-9B | 제출 기본값은 단일 허용 모델로 고정, 필요 시 내부 엔드포인트만 라우팅 |
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 | 384차원, 다국어(한/영) 지원 |
| Vector Index | numpy IVF | K-Means 클러스터링, 14,373 벡터, 16 클러스터 |
| Retrieval | Dual-Path (IVF + BM25) | 벡터 검색 + 독립 키워드 검색 병렬, 91쌍 동의어 |
| Reranking | Dynamic Hybrid | 쿼리 유형별 동적 가중치 + 한국어 부스트 |
| Frontend | HTML/CSS/JS | 프레임워크 미사용, 웜 라이트 테마, Pretendard 폰트 |
| 문서 파싱 | PyPDF2, python-docx, python-pptx | 다양한 포맷 지원 |
| 평가 | eval_questions.py | 72문항 자동 검색 품질 평가 |

## 프로젝트 구조

```
ocp-rag-chatbot/
├── src/                          # 핵심 RAG 파이프라인
│   ├── config.py                 # 전역 설정 관리 (.env 로드)
│   ├── pipeline.py               # RAG 오케스트레이터 + 듀얼 모드 프롬프트 + 트레이스
│   ├── api/                      # FastAPI 엔드포인트 (SSE)
│   ├── llm/                      # LLM 클라이언트 (멀티 endpoint)
│   ├── embedding/                # 임베딩 엔진 + LRU 캐싱
│   ├── vectorstore/              # IVF 벡터 인덱스
│   ├── retriever/                # Dual-Path 검색 + 쿼리 분류 + 동적 Hybrid Reranking
│   ├── chunker/                  # 문서 청킹 (Sliding Window)
│   ├── session/                  # 세션 관리 + Few-shot Query Rewriting
│   └── cache/                    # Semantic Response Cache (3중 호환성 검증)
├── frontend/
│   └── index.html                # 웹 UI (웜 라이트 테마, 듀얼 모드, Trace 패널, 추천 질문)
├── scripts/
│   ├── scrape_docs.py            # OCP/K8s 공식 문서 스크래핑
│   ├── generate_docs.py          # LLM 기반 합성 문서 생성
│   ├── sanitize_corpus.py        # 비공개 raw → 공개 가능한 정제본 변환
│   ├── build_index.py            # 정제본 인덱싱 (청킹→임베딩→IVF)
│   ├── eval_questions.py         # 72문항 검색 품질 자동 평가
│   └── test_multiturn.py         # 멀티턴 대화 테스트
├── data/
│   ├── raw/                      # 비공개 원본 문서 (Git 제외)
│   ├── sanitized_raw/            # 챗봇이 읽는 정제본 문서 (Git 포함, 98개)
│   └── index/                    # 벡터 인덱스 (Git 제외, make index로 재생성)
├── docs/
│   ├── worklog-*.md              # 일별 워크로그
│   ├── troubleshooting/          # 일별 트러블슈팅 기록
│   ├── plan-*.md                 # 고도화 계획
│   ├── rag-dependency-guide.md   # 패키지 의존성 맵 & 배포 가이드
│   └── README-v1-initial.md      # 초기 버전 README
├── Makefile                      # 단축 명령어 (make run/stop/index) — Mac/Linux
├── run.bat / kill.bat / index.bat  # Windows 실행 스크립트
└── requirements.txt              # Python 의존성
```

## 실행 방법

### Mac / Linux

```bash
# 1. 환경 설정
cp .env.example .env
# .env 파일에서 LLM_ENDPOINT를 실제 엔드포인트로 변경

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 인덱스 생성 (최초 1회)
make index

# 4. 서버 실행
make run
# → http://localhost:8000
```

### Windows

```batch
# 0. 가상환경
.\venv\Scripts\Activate  

# 1. 환경 설정
copy .env.example .env
# .env 파일에서 LLM_ENDPOINT를 실제 엔드포인트로 변경

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 인덱스 생성 (최초 1회)
index.bat

# 4. 서버 실행
run.bat
# → http://localhost:8000

# 서버 종료
kill.bat
```

### 심사 / 발표 모드

- 기본값은 `SUBMISSION_MODE=1` 이며, UI에서 모델 전환이 숨겨지고 `Qwen/Qwen3.5-9B` 만 사용합니다.
- 발표용으로 엔드포인트 전환을 보여주고 싶다면 `.env` 에서 `SUBMISSION_MODE=0`, `EXPOSE_LLM_ENDPOINT_SWITCHER=1` 로 실행합니다.
- 브라우저에서 `http://localhost:8000/?presentation=review` 로 열면 심사 모드 UI가 바로 적용됩니다.
- 웰컴 화면의 데모 카드 3개로 운영형 / 학습형 / 멀티턴 흐름을 즉시 재현할 수 있습니다.

### 코퍼스 재생성

코퍼스를 수정하거나 새 문서를 추가할 때:

```bash
# 비공개 raw를 정제본으로 변환
python scripts/sanitize_corpus.py    # Mac/Linux
# 또는
python scripts\sanitize_corpus.py    # Windows

# 정제본 기준으로 인덱스 재생성
make index                           # Mac/Linux
index.bat                            # Windows

# 중요: 인덱스 재빌드 후 반드시 서버 재시작 필요
# (--reload 모드로는 인덱스 파일 변경이 반영되지 않음)
```

### 단축 명령어 (Makefile — Mac/Linux)

```bash
make install    # pip install -r requirements.txt
make sanitize   # 비공개 raw → 정제본 변환
make index      # 정제본 인덱싱 (build_index.py)
make run        # 서버 시작 (uvicorn, port 8000)
make stop       # 서버 종료
make scrape     # OCP 공식 문서 스크래핑
make test       # 멀티턴 대화 테스트
make clean      # __pycache__ 정리
```

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/chat` | 비스트리밍 채팅 |
| POST | `/api/chat/stream` | SSE 스트리밍 채팅 (mode: "ops" / "learn") |
| GET | `/api/sessions` | 활성 세션 목록 |
| GET | `/api/session/{id}/history` | 세션 대화 이력 |
| GET | `/api/stats` | 시스템 상태 (캐시, 인덱스, n_probe 등) |
| POST | `/api/cache/clear` | 시맨틱 캐시 초기화 |
| GET | `/api/llm/endpoints` | 현재 노출 가능한 LLM 엔드포인트 목록 + 심사 모드 플래그 |
| POST | `/api/llm/endpoint` | LLM 엔드포인트 전환 (`SUBMISSION_MODE=1` 에서는 403) |
| GET | `/api/llm/health` | 현재 LLM 연결 상태 확인 |

## 평가 및 검증

### 빠른 스모크 체크

```powershell
python scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --endpoint http://127.0.0.1:8000 --format both --output data/eval_report.json
```

### 스트리밍 경로까지 포함한 검증

```powershell
python scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --endpoint http://127.0.0.1:8000 --transport stream --format both --output data/eval_report.json
```

- 결과물은 `data/eval_report.json`, `data/eval_report.md` 에 저장됩니다.
- 체크 항목은 `rewrite / retrieval / answer` 3단계이며, 하나라도 실패하면 종료 코드 `1` 을 반환합니다.
- 상세 설명은 `docs/evaluation-runner.md` 참고.

## 핵심 설계 상세

### 1. IVF Vector Index

numpy 기반 벡터 검색 엔진:

```
전체 벡터 (14,373개)
    │
    ▼ K-Means 클러스터링 (Lloyd's algorithm, seed=42)
[C0] [C1] [C2] ... [C15]    ← 16개 클러스터
                             ← 클러스터별 벡터 분배

검색 시:
Query 벡터 → n_probe=16 (전체 클러스터 탐색)
→ Cosine Similarity 계산
→ ~26ms (14K 벡터 규모에서 전수탐색 성능 영향 없음)
```

- K-Means 클러스터링 (Lloyd's algorithm, seed=42 고정으로 재현성 보장)
- Cosine Similarity 기반 유사도 계산 (벡터 정규화 → dot product)
- `n_probe=16` — 14K 벡터 규모에서는 전수탐색이 안전 (클러스터 누락 방지, 26ms)
- `IVFIndex.load()` 시 config의 `IVF_N_PROBE` 우선 적용 (저장된 meta 값 무시)
- 인덱스 저장/로드 지원 (vectors.npy, centroids.npy, index_meta.json)

### 2. Dual-Path 검색 + 동적 Hybrid Reranking

임베딩 벡터 검색과 BM25 키워드 검색을 병렬로 수행하여 상호 보완:

```
                    Query
                      │
                      ▼
               [Query Classifier]
               쿼리 유형 자동 분류
               (troubleshooting / procedure / concept / comparison / overview / general)
                      │
           ┌──────────┼──────────┐
           ▼                     ▼
    [경로 1: IVF 검색]    [경로 2: BM25 코퍼스 검색]
    top_k × 3 = 15개      top_k × 2 = 10개
    (임베딩 유사도 기반)    (키워드 정확 매칭 + 91쌍 동의어)
           │                     │
           └──────────┬──────────┘
                      ▼
               중복 제거 + 합치기
               (BM25 전용 후보의 semantic score 계산)
                      │
                      ▼
            Dynamic Hybrid Reranking
            ┌─────────────────────────────────────────┐
            │ troubleshooting/procedure:               │
            │   Score = 0.6 × Semantic + 0.4 × BM25   │
            │   (키워드 매칭 중요: 에러명, 명령어)       │
            │                                         │
            │ concept:                                 │
            │   Score = 0.8 × Semantic + 0.2 × BM25   │
            │   (의미적 유사성 중요: "~란 무엇인가")     │
            │                                         │
            │ 기본:                                    │
            │   Score = 0.7 × Semantic + 0.3 × BM25   │
            │                                         │
            │ + 한국어 쿼리 & -ko.md 문서: +0.08 부스트 │
            └─────────────────────────────────────────┘
                      │
                      ▼ 소스 다양성 필터 (max_per_source=1)
                      │ → 같은 문서에서 최대 1개만 선택
                      ▼ 상위 top_k(5)개 선택
                      │
                      ▼
            Adjacent Chunk Expansion
            상위 결과에 한해 앞뒤 청크 선택 병합
            (같은 문서의 연속 청크를 합쳐서 문맥 보완하되 노이즈는 제한)
```

**쿼리 유형별 동적 가중치가 필요한 이유:**
트러블슈팅 질문("CrashLoopBackOff 해결")은 에러명/명령어 등 키워드 매칭이 중요하고,
개념 질문("Pod란 무엇인가")은 의미적 유사성이 더 중요합니다.
고정 가중치로는 양쪽 다 최적화할 수 없어서 쿼리 분류기가 유형을 판단하고 가중치를 조절합니다.

**한국어 문서 부스트가 필요한 이유:**
BM25 토크나이저가 공백 기반이라 영어에 유리합니다. 한국어 쿼리인데 영문 문서가
BM25 점수로 상위를 독점하면, 실제 해결방법이 담긴 한국어 문서가 밀려납니다.
+0.08 부스트로 이 편향을 보정합니다.

**소스 다양성 제어 (max_per_source=1)가 필요한 이유:**
같은 영문 문서의 여러 청크가 BM25로 상위를 독점하면 한국어 해결방법 문서가 top 5에서 탈락합니다.
문서당 1개로 제한하면 다양한 소스에서 정보를 수집할 수 있습니다.

**인접 청크 확장이 필요한 이유:**
chunk 0(개요)만 검색되면 LLM이 해결 방법을 답변하지 못합니다.
인접 청크 확장으로 chunk 0 + 1 + 2를 합쳐서 진단 명령어와 해결 절차까지 context에 포함시킵니다.

### 3. Query Classifier (쿼리 유형 분류기)

BM25 토큰 + 힌트 키워드 매칭으로 쿼리 유형을 자동 분류:

| 유형 | 힌트 키워드 예시 | 동적 가중치 |
|------|---------------|-----------|
| troubleshooting | 에러, 안됨, 실패, crashloop, pending, oom | Semantic 0.6 + BM25 0.4 |
| procedure | 방법, 설정, 생성, 삭제, 변경, yaml | Semantic 0.6 + BM25 0.4 |
| concept | 뭐야, 무엇, 개념, 설명, 원리 | Semantic 0.8 + BM25 0.2 |
| comparison | 차이, 비교, vs | Semantic 0.7 + BM25 0.3 |
| overview | 종류, 목록, 모음, 총정리 | Semantic 0.7 + BM25 0.3 |
| general | (기본값) | Semantic 0.7 + BM25 0.3 |

분류 결과는 Pipeline Trace 패널의 "Rewrite" 단계에서 `query_type`으로 확인 가능.

### 4. Query Rewriter (멀티턴 지원)

Few-shot 예시 기반으로 맥락 의존적 질문을 독립적 질문으로 변환:

| 대화 맥락 | 사용자 질문 | 재작성된 질문 |
|-----------|-----------|-------------|
| OCP Pod 생성 방법 설명 후 | "그거 삭제하려면?" | "OCP에서 Pod를 삭제하려면?" |
| Deployment 설명 후 | "더 알려줘" | "OCP Deployment의 롤링 업데이트 전략을 설명해줘" |
| 첫 질문 | "readiness probe가 뭐야?" | (변경 없음) |

소형 LLM(9B)에서는 장황한 규칙보다 구체적 Few-shot 예시가 더 효과적.
핵심 규칙: 대명사 → 구체적 대상 교체, **최신 질문의 동사는 절대 바꾸지 않음**.

### 5. 2단계 캐싱 전략

**Embedding Cache (LRU):**
- SHA256 해시 기반 키로 동일 텍스트의 중복 임베딩 방지
- 최대 5000개 캐시, OrderedDict 기반 LRU 구현

**Semantic Response Cache (3중 호환성 검증):**
- Cosine Similarity 임계값(0.95) 기반 유사 질의 매칭
- 캐시 히트 시 LLM 호출 없이 즉시 응답 (레이턴시 99% 감소)
- **3중 호환성 검증**으로 오탐 방지:
  1. **숫자 비교**: "세줄요약" vs "네줄요약" → 숫자가 다르면 캐시 미스
  2. **엔티티 비교**: "OpenShift" vs "Kubernetes" → 대상이 다르면 캐시 미스
  3. **토큰 교집합**: 핵심 토큰이 하나도 안 겹치면 캐시 미스
- LRU 방식으로 최대 200개 캐시 항목 관리
- 실패 응답("찾지 못했습니다" 등)은 캐시하지 않음

### 6. 듀얼 모드 시스템

| 모드 | 아이콘 | 시스템 프롬프트 특징 | 추천 질문 |
|------|--------|-------------------|----------|
| 운영 (ops) | ⚙️ | 간결, 실용적, 명령어 중심 | CrashLoopBackOff, drain, PVC, 업그레이드 등 |
| 학습 (learn) | 💡 | 비유/예시 적극 활용, 단계별 설명, 용어 괄호 설명 | Pod/Deployment/Service 개념, OCP vs K8s 등 |

- 모드별 시스템 프롬프트 분리 (같은 질문이라도 모드에 따라 답변 스타일 다름)
- 캐시 키에 `[mode]` 접두사 → 모드 간 캐시 간섭 방지
- 웰컴 화면에 모드별 추천 질문 풀 (각 8개) → 랜덤 3개 표시
- 후속 추천 질문: LLM이 답변 끝에 3개 관련 질문 제안 → 클릭으로 자동 전송

### 7. 데이터 수집 전략

4가지 데이터 소스를 조합하여 98개 문서, 14,373 벡터 구축:

| 소스 | 방법 | 문서 수 | 특징 |
|------|------|--------|------|
| 한국어 합성 문서 | LLM(Qwen3.5-9B) 생성 | ~20개 | 핵심 개념, 트러블슈팅, 운영 가이드 등 주제별 한국어 문서 |
| 커스텀 가이드 | 수동 작성 | ~10개 | 트러블슈팅 가이드 (CrashLoop/ImagePull/Pending/OOMKilled 등) |
| 웹 스크래핑 | 공식 문서 크롤링 | ~50개 | OCP 4.17 + K8s 공식 문서 기반 |
| 추가 문서 | PPTX/PDF 파싱 | 가변 | 운영/교육용 보조 자료 |

**텍스트 전처리:**
- 스크래핑 데이터의 공백 누락 자동 수정 (camelCase 경계 분리)
- K8s 기술 용어 보호 리스트 (StatefulSet 등 40개 용어)
- PPTX 임시 파일(~$) 자동 필터링

### 8. BM25 동의어 사전

91쌍의 한국어-영어 동의어 매핑으로 BM25 키워드 검색의 다국어 매칭 강화:

```python
# 예시
"pod" ↔ "파드"
"openshift" ↔ ["오픈시프트", "ocp"]
"drain" ↔ ["드레인"]
"oomkilled" ↔ ["oom", "메모리초과", "메모리부족"]
"crashloopbackoff" ↔ ["크래시루프", "크래시"]
"argocd" ↔ ["아르고cd", "아르고"]
# ... 총 91쌍
```

### 9. 제출 안전장치 + 엔드포인트 라우팅

기본값은 심사 친화적인 고정 모드이며, 필요할 때만 내부 엔드포인트 라우팅을 노출:

| 서버 | 백엔드 | GPU | 특징 |
|------|--------|-----|------|
| 회사 서버 | vLLM | - | 기본 제출/심사 경로, `Qwen/Qwen3.5-9B` 고정 |
| Mac Mini | MLX | Apple GPU | 발표/개발 모드에서만 선택 가능 |
| RTX Desktop | Ollama | RTX 4070 Ti | 발표/개발 모드에서만 선택 가능 |

- `SUBMISSION_MODE=1` 이면 UI 전환 숨김 + `/api/llm/endpoint` 차단
- 허용 모델은 코드에서 `Qwen/Qwen3.5-9B` 로 강제 고정
- 연결 상태 실시간 표시 (🟢/🔴)
- 백엔드별 thinking 모드 자동 비활성화 (vLLM: `chat_template_kwargs`, Ollama: `reasoning_effort`)
- 엔드포인트 URL/이름은 `.env`에서 설정

### 10. Streaming + Pipeline Trace

SSE(Server-Sent Events)를 통한 실시간 응답:
- 토큰 단위 스트리밍으로 체감 응답 속도 향상
- 각 파이프라인 단계별 trace 이벤트 전송 (9단계)
- 프론트엔드 Trace 패널에서 실시간 모니터링
- 단계별 소요 시간, 중간 결과, 메트릭 표시

### 11. 검색 품질 평가 프레임워크

기존 `eval_questions.py` 외에, 심사 증빙용 fixture runner를 추가하여 검색 품질을 재현 가능하게 측정:

```bash
# 전체 검색 질문 평가
python scripts/eval_questions.py

# 질문 목록만 확인
python scripts/eval_questions.py --dry-run

# 카테고리별 평가
python scripts/eval_questions.py --category troubleshooting

# fixture 기반 심사 리포트 생성
python scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --endpoint http://127.0.0.1:8000 --format both --output data/eval_report.json
```

| 카테고리 | 질문 수 | 예시 |
|---------|--------|------|
| concept | 20 | "쿠버네티스가 뭐야?", "Pod란 무엇이고 왜 필요한가?" |
| procedure | 15 | "Deployment를 롤백하는 방법은?", "HPA를 설정하는 방법은?" |
| troubleshooting | 14 | "Pod가 CrashLoopBackOff일 때 해결방법은?", "OOMKilled가 발생하면?" |
| operations | 10 | "etcd 백업하는 방법", "노드를 drain하는 방법과 주의사항" |
| cicd | 5 | "Blue-Green 배포와 Canary 배포의 차이" |
| security | 4 | "Pod Security Standards 종류는?" |
| commands | 4 | "자주 쓰는 oc 명령어 모음" |

점수 기준: **PASS**(>=0.6), **WEAK**(0.4~0.6), **FAIL**(<0.4)
결과 저장: `data/eval_results.json`

## 설정 파라미터

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| CHUNK_SIZE | 512 | 청크 크기 (문자 수) |
| CHUNK_OVERLAP | 128 | 청크 간 겹침 크기 |
| TOP_K | 5 | 최종 검색 결과 수 |
| IVF_N_CLUSTERS | 16 | IVF 클러스터 수 |
| IVF_N_PROBE | 16 | 검색 시 탐색 클러스터 수 (16=전수탐색) |
| CACHE_SIMILARITY_THRESHOLD | 0.95 | 캐시 히트 유사도 임계값 |
| MAX_HISTORY_TURNS | 10 | 최대 대화 이력 턴 수 |
| LLM_MAX_TOKENS | 2048 | LLM 최대 생성 토큰 |
| LLM_TEMPERATURE | 0.7 | LLM 생성 온도 |

## 주요 구현 체크리스트

### 필수 요구사항
- [x] RAG → LLM 파이프라인 + 웹 UI 구현
- [x] Vector Index 설계 (IVF - K-Means, numpy)
- [x] 멀티턴 대화 10턴 이상 (세션 + Few-shot Query Rewriting)
- [x] LLM 연동 - Qwen/Qwen3.5-9B (제출 기본값 고정, 내부 엔드포인트 라우팅 지원)
- [x] Streaming 응답 (SSE 토큰 스트리밍)

### 추가 구현
- [x] Dual-Path 검색 (IVF 벡터 + BM25 독립 코퍼스 검색, 91쌍 동의어)
- [x] 쿼리 유형 분류기 (6가지: troubleshooting, procedure, concept, comparison, overview, general)
- [x] 동적 Hybrid Reranking (쿼리 유형별 가중치 + 한국어 문서 부스트)
- [x] 소스 다양성 제어 (max_per_source=1)
- [x] 인접 청크 확장 (상위 결과 선택 확장, query type별 window 제어)
- [x] 2단계 캐싱 (Embedding LRU + Semantic Cache, 3중 호환성 검증)
- [x] Pipeline Trace 관찰가능성 패널 (9단계 실시간 모니터링)
- [x] 듀얼 모드 시스템 (운영 / 학습, 모드별 프롬프트 + 캐시 분리)
- [x] Perplexity 스타일 후속 추천 질문 (클릭으로 이어서 질문)
- [x] 검색 품질 평가 프레임워크 (`eval_questions.py` + `eval_fixture_runner.py`)
- [x] LLM 기반 합성 문서 자동 생성 (18개 토픽)
- [x] 텍스트 전처리 (스크래핑 데이터 정규화)
- [x] 한국어 트러블슈팅 문서 (CrashLoop/ImagePull/Pending/OOMKilled/Service네트워크)
- [x] 캐시 초기화 API
- [x] 한국어 IME 처리 (compositionstart/end)
- [x] 마크다운 렌더링 (표/코드블록/리스트/볼드)
- [x] 웜 라이트 테마 UI (Pretendard 폰트, 커스텀 스크롤바, fadeIn 애니메이션)
- [x] 멀티 LLM 엔드포인트 (UI 서버 선택 + 모델 자동 감지)
- [x] Qwen3.5 thinking 모드 자동 비활성화 (vLLM/Ollama/MLX 호환)
- [x] Windows 지원 (run.bat / kill.bat / index.bat)

## 향후 과제

- [ ] Playwright 스크래핑 업그레이드 (Red Hat JS SPA 렌더링 대응)
- [ ] 코드 블록 복사 버튼
- [ ] 답변 출처 인라인 표기 (Perplexity 스타일 [1][2] 각주)
- [ ] 사용자 피드백 👍👎 (SQLite 저장)
- [ ] 시맨틱 청킹 (마크다운 헤딩 기반)
- [ ] 세션 영속화 + 대화 히스토리 (SQLite → 사이드바 목록)
- [ ] 단위 테스트 추가 (현재 통합 테스트만 존재)
- [ ] CORS 제한 (`allow_origins=["*"]` → 배포 환경별 제한)
- [ ] 프롬프트 인젝션 방어
- [ ] 동의어 사전 외부 파일 분리 (현재 코드 내 하드코딩)

## 관련 문서

- [패키지 의존성 맵 & 배포 가이드](docs/rag-dependency-guide.md) — 오프라인/에어갭 배포 대비
- [초기 버전 README](docs/README-v1-initial.md) — Day 1~2 시점의 시스템 설명
- [고도화 계획](docs/plan-2026-03-23.md) — 우선순위별 실행 계획
- [워크로그](docs/) — 일별 개발 기록 (worklog-*.md)
- [트러블슈팅](docs/troubleshooting/) — 일별 문제 해결 기록
