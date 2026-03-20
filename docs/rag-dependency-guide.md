# RAG 시스템 패키지 의존성 맵 & 실전 배포 가이드

## Context

이 프로젝트는 실전 RAG 시스템 제작의 **예행 연습**이며, 실전에서는 외부 서버를 못 씀.
따라서 모든 패키지 의존성과 전이 의존성을 정확히 파악하고, 오프라인 배포에 대비해야 함.

**핵심 원칙**: "라이브러리를 쓰느냐"가 아니라 **"핵심 판단과 구조를 누가 하느냐"**
- numpy로 cosine similarity 계산 = 내가 검색기를 만든 것
- Chroma에 넣고 query() = 남의 검색기를 부른 것

---

## 1. 현재 프로젝트 패키지 분류

### A. 핵심 RAG 로직 (직접 구현됨 — 외부에 위임 안 함)

| 모듈 | 파일 | 직접 구현한 것 | 쓰는 패키지 |
|------|------|--------------|------------|
| 벡터 인덱스 | `src/vectorstore/` | K-Means 클러스터링, IVF 검색, brute force | `numpy` |
| 검색+리랭킹 | `src/retriever/` | BM25 스코어링, 전체 코퍼스 검색, hybrid reranking (7:3) | `numpy`, `re`, `math` |
| 시맨틱 캐시 | `src/cache/` | cosine similarity 기반 LRU 캐시 | `numpy` |
| 청킹 | `src/chunker/` | 슬라이딩 윈도우 청커, 기술용어 보호, 문장 분리 | `re` (표준) |
| 세션/리라이팅 | `src/session/` | 멀티턴 세션 관리, 맥락의존 질문 재작성 | (표준 라이브러리) |
| 파이프라인 | `src/pipeline.py` | RAG 오케스트레이션, 스트리밍 트레이스 | (표준 라이브러리) |

### B. 허용 패키지 — 도구로 사용 (핵심 로직 아님)

#### B-1. 임베딩 생성 (`src/embedding/`)
| 패키지 | 버전 | 역할 | 전이 의존성 |
|--------|------|------|------------|
| **sentence-transformers** | 3.0.0 | 텍스트→벡터 변환 | `torch`, `transformers`, `huggingface-hub`, `scipy`, `scikit-learn`, `Pillow`, `tqdm` |
| **torch** | 2.9.0 | 딥러닝 프레임워크 (추론) | `filelock`, `fsspec`, `jinja2`, `networkx`, `sympy`, `typing-extensions` |
| **transformers** | 4.57.1 | 모델 아키텍처/토크나이저 | `huggingface-hub`, `safetensors`, `tokenizers`, `regex`, `pyyaml`, `packaging` |

> **sentence-transformers는 편의 래퍼**일 뿐. 내부적으로 `transformers` + `torch`로 추론.
> 실전에서 `transformers + torch`로 직접 호출하면 sentence-transformers 의존 제거 가능.

#### B-2. LLM 호출 (`src/llm/`)
| 패키지 | 버전 | 역할 |
|--------|------|------|
| **httpx** | 0.27.0 | 비동기 HTTP 클라이언트 (vLLM API 호출) |

> OpenAI SDK와 달리 범용 HTTP 클라이언트. 어떤 LLM 서버든 호출 가능.

#### B-3. 웹 서버 (`src/api/`)
| 패키지 | 버전 | 역할 | 전이 의존성 |
|--------|------|------|------------|
| **fastapi** | 0.115.0 | REST API 프레임워크 | `starlette`, `anyio` |
| **uvicorn** | 0.30.0 | ASGI 서버 | `h11`, `httptools` |
| **sse-starlette** | 2.1.0 | SSE 스트리밍 | `starlette` |
| **pydantic** | 2.9.0 | 요청/응답 검증 | `annotated-types`, `pydantic-core` |

#### B-4. 문서 파싱 (`src/chunker/`)
| 패키지 | 버전 | 역할 |
|--------|------|------|
| **PyPDF2** | 3.0.1 | PDF → 텍스트 |
| **python-docx** | 1.1.0 | Word → 텍스트 |
| **python-pptx** | 1.0.2 | PowerPoint → 텍스트 |

#### B-5. 스크래핑 (`scripts/scrape_docs.py`)
| 패키지 | 버전 | 역할 |
|--------|------|------|
| **requests** | 2.32.3 | HTTP 요청 |
| **beautifulsoup4** | 4.12.3 | HTML 파싱 |
| **lxml** | 5.2.2 | XML/HTML 파서 백엔드 |

#### B-6. 설정
| 패키지 | 버전 | 역할 |
|--------|------|------|
| **python-dotenv** | 1.0.1 | `.env` 파일 로드 |

---

## 2. 의존성 트리 (전이 의존성 포함)

```
sentence-transformers (3.0.0)  ← 가장 무거운 의존성 체인
├── torch (2.9.0) .................. ~387MB (CPU), ~2GB+ (CUDA)
│   ├── filelock, fsspec, jinja2
│   ├── networkx, sympy
│   └── typing-extensions
├── transformers (4.57.1) .......... 모델 아키텍처
│   ├── huggingface-hub ............ 모델 다운로드
│   ├── tokenizers ................. Rust 기반 토크나이저
│   ├── safetensors ................ 모델 가중치 포맷
│   ├── regex, pyyaml, packaging
│   └── requests
├── scipy (1.16.2) ................. 수치 계산
│   └── numpy
├── scikit-learn (1.7.2) ........... (sentence-transformers 내부 사용)
│   ├── joblib, threadpoolctl
│   └── scipy → numpy
├── Pillow ......................... (이미지 처리, 이 프로젝트에선 불필요)
├── tqdm ........................... 진행률 표시
└── numpy (1.26.0) ................. 핵심 수치 연산

fastapi (0.115.0)
├── starlette ...................... ASGI 프레임워크
├── pydantic (2.9.0) ............... 데이터 검증
│   └── pydantic-core (Rust 바인딩)
└── anyio .......................... 비동기 I/O

httpx (0.27.0)
├── httpcore ....................... HTTP/1.1, HTTP/2
├── certifi ........................ SSL 인증서
└── idna ........................... 국제화 도메인
```

---

## 3. 실전 배포 (오프라인/에어갭) 대비 체크리스트

### 사전 다운로드 필요 항목
1. **Python 패키지**: `pip download -r requirements.txt -d ./packages/`
2. **임베딩 모델 가중치**: `paraphrase-multilingual-MiniLM-L12-v2` (~470MB)
   - `huggingface-hub`에서 사전 다운로드 → 로컬 경로 지정
   - `EMBEDDING_MODEL` 환경변수를 로컬 경로로 변경
3. **PyTorch**: CPU 전용 빌드 권장 (CUDA 불필요 시 용량 대폭 절감)
   - `pip install torch --index-url https://download.pytorch.org/whl/cpu`

### 실전에서 sentence-transformers 없이 직접 추론하는 방법
```python
# sentence-transformers 대신 transformers + torch 직접 사용
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("./models/multilingual-MiniLM")
model = AutoModel.from_pretrained("./models/multilingual-MiniLM")

def embed(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Mean pooling + L2 normalize
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return torch.nn.functional.normalize(embeddings, p=2, dim=1).numpy()
```
→ sentence-transformers, scipy, scikit-learn, Pillow 의존성 제거 가능

---

## 4. 금지/허용 판단 근거 정리

### 금지 (핵심 로직을 외부에 위임)
| 종류 | 예시 | 왜 금지? |
|------|------|---------|
| RAG 프레임워크 | LangChain, LlamaIndex, Haystack | 검색/컨텍스트 구성/체인을 통째로 맡김 |
| 벡터 DB | Chroma, Qdrant, Pinecone | 인덱싱/검색/유사도 계산을 DB에 위임 |
| 인덱스 라이브러리 | FAISS, hnswlib, Annoy | IVF/HNSW 구현을 라이브러리에 위임 |
| 외부 임베딩 API | OpenAI Embeddings API | 네트워크 의존, 통제 불가 |

### 허용 (도구로 사용, 핵심 판단은 우리가)
| 종류 | 예시 | 왜 허용? |
|------|------|---------|
| 수치 계산 | numpy | 행렬 곱/정규화 = 저수준 연산 도구 |
| 모델 추론 | torch, transformers | 모델 가중치 로딩+포워드패스 = 인프라 |
| 웹 프레임워크 | fastapi, uvicorn | API 서빙 = 인프라 |
| 파일 파싱 | PyPDF2, python-docx | 파일 포맷 디코딩 = 유틸리티 |
| HTTP 클라이언트 | httpx | 네트워크 요청 = 유틸리티 |

---

## 5. 프로젝트 모듈별 의존성 다이어그램

```
┌─────────────────────────────────────────────────────┐
│  src/api/         FastAPI + SSE                      │
│  (fastapi, uvicorn, sse-starlette, pydantic)        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  src/pipeline.py    RAG 오케스트레이터 (직접 구현)     │
│  (표준 라이브러리만)                                   │
└──┬───────┬────────┬────────┬────────┬───────────────┘
   │       │        │        │        │
   ▼       ▼        ▼        ▼        ▼
┌──────┐┌───────┐┌───────┐┌───────┐┌───────┐
│LLM   ││Embed  ││Vector ││Retri- ││Cache  │
│Client││Engine ││Store  ││ever   ││       │
│      ││       ││(IVF)  ││+BM25  ││Seman- │
│httpx ││sent-  ││numpy  ││numpy  ││tic    │
│      ││trans  ││       ││re,math││numpy  │
└──────┘└───────┘└───────┘└───────┘└───────┘
                    ▲
          ┌─────────┘
┌─────────┴──────────────────────────────────┐
│  src/chunker/    문서 파싱 + 청킹 (직접 구현) │
│  PyPDF2, python-docx, python-pptx, re      │
└────────────────────────────────────────────┘
```

---

## 6. requirements.txt 최종 정리 (역할 주석 포함)

```
# === 웹 서버 ===
fastapi==0.115.0          # REST API 프레임워크
uvicorn==0.30.0           # ASGI 서버
sse-starlette==2.1.0      # SSE 스트리밍
pydantic==2.9.0           # 요청/응답 검증

# === 임베딩 (모델 추론) ===
sentence-transformers==3.0.0  # 편의 래퍼 (실전에서 transformers+torch 직접 호출로 대체 가능)
# ↳ 전이: torch, transformers, scipy, scikit-learn, huggingface-hub, Pillow, tqdm
numpy==1.26.0             # 벡터 연산 (IVF, BM25, 캐시 전부 사용)

# === LLM 호출 ===
httpx==0.27.0             # 비동기 HTTP (vLLM API)

# === 문서 파싱 ===
PyPDF2==3.0.1             # PDF → 텍스트
python-docx==1.1.0        # DOCX → 텍스트
python-pptx==1.0.2        # PPTX → 텍스트

# === 스크래핑 (빌드 타임만 사용) ===
beautifulsoup4==4.12.3    # HTML 파싱
requests==2.32.3          # HTTP 요청
lxml==5.2.2               # XML 파서

# === 설정 ===
python-dotenv==1.0.1      # .env 환경변수
```

### 전이 의존성 총 설치 크기 (추정)
- **torch CPU**: ~387MB
- **transformers + tokenizers**: ~50MB
- **scipy + scikit-learn**: ~80MB
- **기타**: ~30MB
- **임베딩 모델 가중치**: ~470MB
- **합계**: ~1GB+

---

## 7. 향후 고려사항

- **sentence-transformers → transformers+torch 직접 호출**: 의존성 3개 제거, 패키지 이해도 향상
- **torch CPU 전용 빌드**: GPU 없는 환경에서 용량 절감
- **모델 가중치 로컬 캐싱**: 오프라인 환경 필수
- **한국어 토크나이저**: 현재 정규식 기반 → `konlpy`나 `kiwi` 추가 시 BM25 정확도 향상 (의존성 트레이드오프)

---

## 8. 기존 챗봇 vs 우리 RAG 챗봇 — 무엇이 다른가

### 일반적인 "기존 챗봇" (LangChain + Chroma 등)

```
사용자 질문
    → LangChain의 RetrievalQA.from_chain_type() 호출
        → Chroma.similarity_search() ← 벡터 DB가 검색 전부 처리
        → LangChain이 프롬프트 조합 + LLM 호출
    → 답변
```

**특징**:
- 코드 3~5줄로 RAG 완성 가능
- 검색 알고리즘을 모름 (Chroma 내부의 HNSW? brute force? 모름)
- 인덱싱 구조를 모름 (Chroma가 알아서 함)
- 리랭킹 없음 (DB가 준 순서 그대로)
- 캐시/세션을 LangChain Memory에 위임
- **문제 발생 시**: 디버깅 불가. "왜 이 문서를 못 찾지?"에 대답 못 함

### 우리 RAG 챗봇 (직접 구현)

```
사용자 질문
    → QueryRewriter: 맥락의존 질문 재작성 (직접 구현)
    → EmbeddingEngine: sentence-transformers로 벡터 생성
    → SemanticCache: cosine similarity 기반 캐시 조회 (직접 구현)
    → [캐시 미스]
    → IVFIndex: K-Means 클러스터링 + IVF 검색 (직접 구현, numpy)
    → BM25Scorer: 전체 코퍼스 키워드 독립 검색 (직접 구현)
    → Retriever: 두 결과 합치기 + hybrid reranking 7:3 (직접 구현)
    → ContextBuilder: 4000자 제한 + 출처 포맷팅 (직접 구현)
    → LLM 호출: httpx로 vLLM API 직접 호출
    → 스트리밍 + 트레이스 이벤트 (직접 구현)
    → 답변
```

### 핵심 차이점 상세 비교

| 항목 | 기존 (LangChain+Chroma) | 우리 (직접 구현) |
|------|------------------------|-----------------|
| **벡터 인덱스** | Chroma가 HNSW 자동 구성 | K-Means 16클러스터 IVF 직접 구현 (numpy) |
| **검색 과정** | `chroma.query()` 한 줄 | IVF 검색 → BM25 전체검색 → 합치기 → hybrid reranking |
| **BM25** | 없거나 LangChain Retriever에 위임 | 직접 구현 (토크나이즈, IDF, TF-norm, 정규화) |
| **리랭킹** | 대부분 없음 | semantic 70% + keyword 30% hybrid scoring |
| **캐시** | LangChain Cache 또는 없음 | cosine similarity 기반 LRU 캐시 (threshold 0.95) |
| **세션/멀티턴** | LangChain Memory | 직접 구현 (TTL, 히스토리 제한, 쿼리 리라이팅) |
| **청킹** | LangChain TextSplitter | 슬라이딩 윈도우 + 기술용어 보호 + 문장 분리 (직접 구현) |
| **오케스트레이션** | LangChain Chain/Agent | pipeline.py에서 각 단계 직접 연결 + 트레이스 |
| **디버깅** | 블랙박스 | 모든 단계 추적 가능 (semantic score, keyword score, 클러스터 배치 등) |
| **오프라인 배포** | Chroma 서버 필요 | numpy 파일로 인덱스 저장, 서버 불필요 |

### 이번에 추가된 BM25 독립 검색이 왜 중요한가

**기존 문제 (Day 3에서 발견)**:
```
"이미지 풀 에러 해결법?"
  → 임베딩 유사도: 0.12~0.42 (top-15 진입 못 함, 0.49+ 필요)
  → BM25는 IVF 후보 15개 안에서만 작동
  → 결과: "제공된 문서에서 찾을 수 없습니다" ← 문서가 있는데도!
```

**해결 후**:
```
"이미지 풀 에러 해결법?"
  → IVF: 임베딩 유사도 0.29 (낮음) → top-15에 안 잡힘
  → BM25 전체검색: "이미지", "풀", "에러" 키워드 정확 매칭 → 1위!
  → 합치기: 트러블슈팅 문서가 후보에 추가됨
  → hybrid reranking: semantic 0.29 x 0.7 + keyword 1.0 x 0.3 = 0.50
  → 결과: 트러블슈팅 문서 1위 검색 성공
```

이게 바로 **"핵심 로직을 직접 구현해야 하는 이유"**:
- Chroma였으면 "왜 못 찾지?"에서 멈춤 → 모델 바꾸거나 문서 구조 뜯어고치는 수밖에
- 직접 구현이니까 "IVF가 못 잡으면 BM25가 보완하자" 같은 **구조적 해결**이 가능

### 우리가 이해해야 하는 것들

1. **IVF (Inverted File Index)**: 벡터를 K-Means로 클러스터링하고, 검색 시 가까운 클러스터 몇 개만 탐색. 전수검색 대비 속도 향상, 정확도 약간 감소
2. **BM25**: TF-IDF의 발전형. 문서 내 키워드 빈도(TF)와 전체 문서에서의 희귀도(IDF)를 결합. 길이 정규화(b) 포함
3. **Hybrid Reranking**: 의미 검색(임베딩)과 키워드 검색(BM25)의 장단점 보완. 가중치 비율이 성능에 직결
4. **Cosine Similarity**: 벡터 간 각도 기반 유사도. 정규화된 벡터의 dot product와 동일
5. **시맨틱 캐시**: 같은 의미의 질문이면 LLM 재호출 없이 응답. threshold가 낮으면 오탐, 높으면 미탐
6. **쿼리 리라이팅**: "그것도 알려줘" → "OCP에서 Pod 리소스 제한 설정도 알려줘"로 변환. 멀티턴의 핵심
