# OCP RAG Chatbot — 시스템 학습 가이드

> 이 문서는 OCP RAG Chatbot의 전체 시스템을 처음부터 이해하기 위한 학습 자료입니다.
> 각 컴포넌트가 왜 필요한지, 어떤 알고리즘을 쓰는지, 코드가 어떻게 동작하는지를 설명합니다.

---

## 목차

1. [RAG란 무엇인가](#1-rag란-무엇인가)
2. [전체 아키텍처 — 질문이 답변이 되기까지](#2-전체-아키텍처--질문이-답변이-되기까지)
3. [문서 파싱과 청킹 (src/chunker)](#3-문서-파싱과-청킹-srcchunker)
4. [임베딩 (src/embedding)](#4-임베딩-srcembedding)
5. [IVF 벡터 인덱스 (src/vectorstore)](#5-ivf-벡터-인덱스-srcvectorstore)
6. [BM25 키워드 검색 (src/retriever — BM25Scorer)](#6-bm25-키워드-검색-srcretriever--bm25scorer)
7. [하이브리드 리트리버 (src/retriever — Retriever)](#7-하이브리드-리트리버-srcretriever--retriever)
8. [쿼리 분류기와 동적 가중치](#8-쿼리-분류기와-동적-가중치)
9. [인접 청크 확장 (Adjacent Chunk Expansion)](#9-인접-청크-확장-adjacent-chunk-expansion)
10. [시맨틱 캐시 (src/cache)](#10-시맨틱-캐시-srccache)
11. [세션과 쿼리 리라이터 (src/session)](#11-세션과-쿼리-리라이터-srcsession)
12. [LLM 클라이언트 (src/llm)](#12-llm-클라이언트-srcllm)
13. [파이프라인 오케스트레이터 (src/pipeline)](#13-파이프라인-오케스트레이터-srcpipeline)
14. [API 서버 (src/api)](#14-api-서버-srcapi)
15. [프론트엔드 (frontend/index.html)](#15-프론트엔드-frontendindexhtml)
16. [데이터 수집과 정제 (scripts/)](#16-데이터-수집과-정제-scripts)
17. [평가 프레임워크 (scripts/eval_questions.py)](#17-평가-프레임워크-scriptseval_questionspy)
18. [설정 파라미터 튜닝 가이드](#18-설정-파라미터-튜닝-가이드)
19. [트러블슈팅에서 배운 교훈들](#19-트러블슈팅에서-배운-교훈들)
20. [용어 사전](#20-용어-사전)

---

## 1. RAG란 무엇인가

### 기본 개념

RAG(Retrieval-Augmented Generation)는 LLM(대형 언어 모델)이 답변할 때, 외부 문서를 검색해서 그 내용을 참고하게 하는 기법입니다.

**왜 필요한가?**

LLM은 학습 데이터에 있는 내용만 알고 있습니다. 우리 회사의 OCP 운영 문서, 내부 트러블슈팅 가이드 같은 건 모릅니다. RAG를 쓰면:

1. 사용자가 질문함
2. 질문과 관련된 문서를 검색함 (Retrieval)
3. 검색된 문서를 LLM에게 "참고 자료"로 전달함 (Augmented)
4. LLM이 그 자료를 기반으로 답변을 생성함 (Generation)

이렇게 하면 LLM이 우리 문서에 있는 내용으로 정확하게 답변할 수 있습니다.

### RAG vs 파인튜닝

| 방식 | 장점 | 단점 |
|------|------|------|
| RAG | 문서 추가/수정이 즉시 반영, 출처 추적 가능, 학습 비용 없음 | 검색 품질에 의존, 컨텍스트 길이 제한 |
| 파인튜닝 | 모델이 지식을 내재화, 추론 속도 빠름 | 데이터 변경 시 재학습 필요, GPU 비용 큼 |

이 프로젝트는 RAG 방식을 채택했습니다. OCP 문서는 자주 업데이트되고, 새 트러블슈팅 가이드도 수시로 추가되니까 RAG가 적합합니다.

### 이 프로젝트의 RAG 파이프라인 흐름

```
사용자: "Pod가 CrashLoopBackOff일 때 어떻게 해?"
    │
    ▼ ① 세션 확인 + 쿼리 리라이트
    "Pod가 CrashLoopBackOff 상태일 때 해결방법은?" (멀티턴이면 재작성)
    │
    ▼ ② 임베딩 변환
    "Pod가 CrashLoop..." → [0.12, -0.34, 0.56, ...] (384차원 벡터)
    │
    ▼ ③ 시맨틱 캐시 확인
    이전에 비슷한 질문 한 적 있으면 → 바로 응답 반환 (LLM 호출 생략)
    │
    ▼ ④ 벡터 검색 (IVF)
    14,373개 문서 벡터와 비교 → 유사한 문서 15개 후보
    │
    ▼ ⑤ 키워드 검색 (BM25)
    "CrashLoopBackOff" 키워드로 전체 코퍼스 검색 → 10개 후보
    │
    ▼ ⑥ 하이브리드 리랭킹
    벡터 점수 + 키워드 점수 합산 → 최종 5개 선택
    │
    ▼ ⑦ 컨텍스트 구성
    5개 문서의 텍스트를 하나로 합침 (최대 6000자)
    │
    ▼ ⑧ LLM 응답 생성
    시스템 프롬프트 + 컨텍스트 + 질문 → Qwen3.5-9B가 답변 생성
    │
    ▼ ⑨ 스트리밍 전송
    토큰 단위로 실시간 전송 (SSE)
```

---

## 2. 전체 아키텍처 — 질문이 답변이 되기까지

### 파일 구조와 역할

```
src/
├── config.py          # 모든 설정값의 중앙 관리소
├── pipeline.py        # 전체 흐름을 조율하는 오케스트레이터
├── api/               # HTTP 요청을 받아서 pipeline에 전달
├── llm/               # LLM 서버와 통신 (OpenAI 호환 API)
├── embedding/         # 텍스트 → 벡터 변환
├── vectorstore/       # 벡터 인덱스 (IVF, K-Means)
├── retriever/         # 검색 + 리랭킹의 핵심 두뇌
├── chunker/           # 문서를 적당한 크기로 자르기
├── session/           # 대화 이력 관리 + 쿼리 재작성
└── cache/             # 비슷한 질문 캐싱
```

### 데이터 흐름 (오프라인 — 인덱싱)

서버가 질문에 답하려면 먼저 문서를 벡터로 변환해서 저장해야 합니다. 이걸 "인덱싱"이라고 합니다.

```
data/sanitized_raw/ (98개 마크다운 문서)
    │
    ▼ [Chunker] 문서를 512자씩 잘라서 14,373개 청크 생성
    │
    ▼ [EmbeddingEngine] 각 청크를 384차원 벡터로 변환
    │
    ▼ [IVFIndex.build()] K-Means로 16개 클러스터 생성
    │
    ▼ data/index/ 에 저장
        ├── vectors.npy      (14,373 × 384 float32 배열)
        ├── centroids.npy    (16 × 384 클러스터 중심 벡터)
        └── index_meta.json  (문서 메타데이터, 클러스터 매핑)
```

### 데이터 흐름 (온라인 — 질의응답)

```
브라우저 → POST /api/chat/stream → FastAPI → RAGPipeline.query_stream()
    → SessionManager (세션 조회/생성)
    → QueryRewriter (멀티턴이면 질문 재작성)
    → EmbeddingEngine (질문 → 벡터)
    → SemanticCache (캐시 히트면 바로 반환)
    → IVFIndex.search() (벡터 검색)
    → BM25Scorer.search_corpus() (키워드 검색)
    → Retriever.retrieve() (하이브리드 리랭킹)
    → Retriever.build_context() (컨텍스트 구성)
    → LLMClient.generate_stream() (LLM 스트리밍)
    → SSE로 토큰 단위 전송
```

---

## 3. 문서 파싱과 청킹 (src/chunker)

### 왜 청킹이 필요한가

LLM에는 컨텍스트 길이 제한이 있습니다. 10페이지짜리 문서를 통째로 넣을 수 없습니다.
또한, 긴 문서 전체를 벡터로 만들면 의미가 평균화되어 검색 정확도가 떨어집니다.

그래서 문서를 적당한 크기(512자)로 잘라서 각각을 독립적인 검색 단위로 만듭니다.

### 청킹 전략: 슬라이딩 윈도우

```
원본 문서 (2000자):
┌──────────────────────────────────────────┐
│ ## Pod 개요                              │
│ Pod는 Kubernetes의 최소 배포 단위...      │
│                                          │
│ ## Pod 생명주기                           │
│ Pod는 여러 상태를 거칩니다...              │
│ - Pending: 스케줄링 대기                  │
│ - Running: 실행 중                       │
│ - CrashLoopBackOff: 반복 실패            │
│                                          │
│ ## 트러블슈팅                             │
│ CrashLoopBackOff 발생 시...              │
└──────────────────────────────────────────┘

청킹 후 (512자씩, 128자 겹침):
┌─────── Chunk 0 (512자) ───────┐
│ ## Pod 개요                   │
│ Pod는 Kubernetes의 최소...    │
│ ## Pod 생명주기               │
│ Pod는 여러 상태를...          │──┐ 128자 겹침
└───────────────────────────────┘  │
          ┌─────── Chunk 1 (512자) ┤──────┐
          │ - Pending: 스케줄링... │      │
          │ - Running: 실행 중     │      │
          │ - CrashLoopBackOff... │      │ 128자 겹침
          │ ## 트러블슈팅          │──────┤
          └────────────────────────┘      │
                    ┌─────── Chunk 2 (512자) ┤
                    │ CrashLoopBackOff 발생..│
                    │ 시...                  │
                    └────────────────────────┘
```

**겹침(overlap)이 필요한 이유**: chunk 0 끝에 있는 "CrashLoopBackOff" 언급이 chunk 1에도 포함되어야 검색에 잡힙니다. 겹침 없으면 청크 경계에서 문맥이 끊깁니다.

### 청킹 코드의 핵심 로직

```python
# 1단계: 문단으로 분리
paragraphs = text.split("\n\n")

# 2단계: 문단들을 chunk_size(512자) 이내로 합치기
for paragraph in paragraphs:
    if len(current_chunk) + len(paragraph) <= chunk_size:
        current_chunk += paragraph  # 아직 공간 있으면 합치기
    else:
        chunks.append(current_chunk)  # 꽉 찼으면 저장
        # overlap만큼 뒤에서 가져와서 새 청크 시작
        current_chunk = current_chunk[-overlap:] + paragraph

# 3단계: 각 청크에 메타데이터 부여
# chunk_id = "파일명::청크번호" (예: "ocp-crashloop-ko.md::2")
```

### 기술 용어 보호

"StatefulSet"이나 "CrashLoopBackOff" 같은 용어가 "Stateful Set"이나 "Crash Loop Back Off"로 분리되면 검색이 안 됩니다. 70개 이상의 K8s/OCP 기술 용어를 보호 리스트에 등록해서 분리를 방지합니다.

```python
PROTECTED_TERMS = [
    "StatefulSet", "DaemonSet", "ReplicaSet", "ConfigMap",
    "CrashLoopBackOff", "ImagePullBackOff", "NetworkPolicy",
    "ServiceAccount", "ClusterRole", "ResourceQuota", ...
]
```

---

## 4. 임베딩 (src/embedding)

### 임베딩이란

텍스트를 숫자 벡터(배열)로 변환하는 것입니다. 의미가 비슷한 텍스트는 비슷한 벡터가 됩니다.

```
"Pod가 뭐야?"          → [0.12, -0.34, 0.56, 0.78, ...] (384개 숫자)
"Pod란 무엇인가?"       → [0.11, -0.33, 0.55, 0.79, ...] ← 거의 비슷!
"etcd 백업 방법"        → [-0.45, 0.22, -0.11, 0.33, ...] ← 완전 다름
```

이 벡터들 사이의 "거리"를 계산하면 의미적 유사도를 알 수 있습니다.

### 사용 모델

`paraphrase-multilingual-MiniLM-L12-v2`
- 384차원 벡터 출력
- 다국어 지원 (한국어 질문 → 영어 문서 매칭 가능)
- sentence-transformers 라이브러리 사용
- 처음에는 `all-MiniLM-L6-v2`(영어 전용)를 쓰다가 한국어 매칭이 약해서 교체

### 코사인 유사도 (Cosine Similarity)

두 벡터가 얼마나 같은 방향을 가리키는지 측정합니다. -1~1 범위이고, 1에 가까울수록 유사합니다.

```
         벡터 A (질문)
        ↗
       / θ (각도가 작을수록 유사)
      /
origin ────────→ 벡터 B (문서)

cosine_similarity = cos(θ) = (A · B) / (|A| × |B|)
```

이 프로젝트에서는 벡터를 미리 정규화(길이를 1로 만듦)해서, 코사인 유사도 = 단순 dot product로 계산합니다.

```python
# 정규화된 벡터의 코사인 유사도 = dot product
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
normalized = vectors / norms
similarity = normalized @ query  # 행렬 곱 한 번으로 전체 유사도 계산
```

### LRU 캐시

같은 텍스트를 반복 임베딩하면 낭비입니다. SHA256 해시를 키로 사용하는 LRU(Least Recently Used) 캐시로 중복 계산을 방지합니다.

```python
def embed(self, text):
    key = hashlib.sha256(text.encode()).hexdigest()
    if key in self._cache:
        return self._cache[key]  # 캐시 히트! 바로 반환

    vector = self._model.encode(text)  # 실제 계산 (수~수십 ms)
    self._cache[key] = vector
    return vector
```

최대 5000개 캐시. 가장 오래 안 쓴 항목부터 제거.

---

## 5. IVF 벡터 인덱스 (src/vectorstore)

### 왜 인덱스가 필요한가

14,373개 벡터와 질문 벡터를 전부 비교하면(brute force) 매번 14,373번의 코사인 유사도 계산이 필요합니다. 지금은 26ms로 빠르지만, 벡터가 수십만~수백만 개가 되면 느려집니다.

IVF(Inverted File Index)는 벡터들을 미리 그룹(클러스터)으로 나눠놓고, 검색할 때는 관련 있는 그룹만 탐색합니다.

### K-Means 클러스터링

인덱스 빌드 시 벡터들을 16개 그룹으로 분류합니다.

```
14,373개 벡터
    │
    ▼ K-Means 알고리즘 (최대 20회 반복)

[클러스터 0]  [클러스터 1]  ...  [클러스터 15]
  1200개        637개              519개

각 클러스터에는 "중심 벡터"(centroid)가 있음
```

**K-Means 동작 원리:**

```
1. 랜덤으로 16개 벡터를 중심점으로 선택 (seed=42 고정)
2. 모든 벡터를 가장 가까운 중심점에 배정
3. 각 그룹의 평균을 새 중심점으로 업데이트
4. 2~3을 배정이 안 바뀔 때까지 반복
```

```python
for _ in range(max_iter):  # 최대 20회
    # 모든 벡터와 모든 중심점의 유사도 계산
    similarities = normalized @ self.centroids.T  # (14373, 16)

    # 각 벡터를 가장 유사한 중심점에 배정
    new_assignments = np.argmax(similarities, axis=1)

    # 수렴 체크
    if np.array_equal(assignments, new_assignments):
        break  # 변화 없으면 종료

    # 중심점 업데이트: 해당 그룹 벡터들의 평균
    for k in range(n_clusters):
        mask = assignments == k
        centroid = normalized[mask].mean(axis=0)
        self.centroids[k] = centroid / np.linalg.norm(centroid)
```

### 검색 과정

```
질문 벡터 (384차원)
    │
    ▼ 16개 중심점과 유사도 계산

[C0: 0.32] [C1: 0.78] [C2: 0.15] ... [C15: 0.65]
                ↑                           ↑
    n_probe=16이면 전부 탐색 (전수검색)
    │
    ▼ 선택된 클러스터 내 벡터들과 코사인 유사도 계산
    │
    ▼ 상위 top_k(15)개 반환
```

### n_probe 파라미터의 의미

- `n_probe=1`: 가장 가까운 1개 클러스터만 탐색 → 빠르지만 문서 누락 위험
- `n_probe=6`: 6개 클러스터 탐색 → 일반적인 설정
- `n_probe=16`: 전체 16개 클러스터 탐색 → 전수검색과 동일, 누락 없음

**이 프로젝트에서 n_probe=16으로 설정한 이유:**
14,373개 벡터에서 16개 클러스터 전부 탐색해도 26ms밖에 안 걸립니다. 클러스터 경계에 있는 문서가 누락되는 것보다 26ms를 쓰는 게 낫습니다. 실제로 CrashLoopBackOff 문서가 n_probe=6에서 누락되는 버그가 있었습니다.

### load() 시 주의사항

인덱스를 디스크에서 로드할 때, `n_probe` 값은 `index_meta.json`에 저장된 값이 아니라 config에서 읽습니다. 인덱스를 빌드한 시점과 검색하는 시점의 n_probe가 다를 수 있기 때문입니다.

```python
@classmethod
def load(cls, dirpath):
    meta = json.load(...)
    index = cls(
        dim=meta["dim"],
        n_clusters=meta["n_clusters"],
        n_probe=IVF_N_PROBE,  # config 값 우선! meta["n_probe"] 아님!
    )
```

---

## 6. BM25 키워드 검색 (src/retriever — BM25Scorer)

### BM25란

BM25는 문서에서 특정 키워드가 얼마나 중요한지 계산하는 전통적인 정보 검색 알고리즘입니다.
"CrashLoopBackOff"라는 단어가 문서에 있으면 높은 점수를 줍니다.

### 임베딩 검색과의 차이

```
질문: "CrashLoopBackOff 해결방법"

[임베딩 검색]
→ "Pod 상태 이상"이나 "컨테이너 재시작" 같은 의미적으로 유사한 문서를 잘 찾음
→ 하지만 "CrashLoopBackOff"라는 정확한 단어가 있는 문서를 못 잡을 수 있음

[BM25 검색]
→ "CrashLoopBackOff"라는 단어가 정확히 포함된 문서를 확실하게 잡음
→ 하지만 "Pod 반복 실패"처럼 다른 표현으로 된 문서는 못 찾음
```

그래서 둘을 합쳐서 씁니다 (Dual-Path).

### BM25 점수 계산 공식

```
BM25(q, D) = Σ IDF(qi) × (tf(qi, D) × (k1 + 1)) / (tf(qi, D) + k1 × (1 - b + b × |D|/avgdl))
```

쉽게 설명하면:
- **IDF(qi)**: 단어 qi가 전체 코퍼스에서 얼마나 드문지 (드물수록 중요)
  - "Pod"는 거의 모든 문서에 있으니 IDF 낮음
  - "CrashLoopBackOff"는 일부 문서에만 있으니 IDF 높음
- **tf(qi, D)**: 단어 qi가 문서 D에 몇 번 나오는지
- **k1, b**: 튜닝 파라미터 (k1=1.5, b=0.75 — 일반적인 기본값)
- **|D|/avgdl**: 문서 길이 보정 (긴 문서에 페널티)

### 한국어 토크나이저

BM25는 텍스트를 단어(토큰)로 분리해야 합니다. 영어는 공백으로 쉽게 되지만, 한국어는 조사 처리가 필요합니다.

```python
# "오픈시프트에서" → "오픈시프트" (조사 "에서" 제거)
# "파드를" → "파드" (조사 "를" 제거)

JOSA_SUFFIXES = ["에서", "으로", "에는", "이란", "의", "에", "를", "을", ...]

def _strip_josa(self, token):
    for suffix in sorted(JOSA_SUFFIXES, key=len, reverse=True):
        if token.endswith(suffix) and len(token) > len(suffix) + 1:
            return token[:-len(suffix)]
    return token
```

### 동의어 사전 (91쌍)

한국어 질문으로 영어 문서를 찾으려면 동의어 매핑이 필요합니다.

```python
_SYNONYMS = {
    "pod": ["파드"],
    "파드": ["pod"],
    "openshift": ["오픈시프트", "ocp"],
    "drain": ["드레인"],
    "oomkilled": ["oom", "메모리초과", "메모리부족"],
    "crashloopbackoff": ["크래시루프", "크래시"],
    "argocd": ["아르고cd", "아르고"],
    "helm": ["헬름"],
    "etcd": ["이티씨디"],
    # ... 총 91쌍
}
```

검색할 때 "파드"라고 입력하면 "pod"도 함께 검색됩니다.

### 두 가지 모드

BM25Scorer는 두 가지 모드로 동작합니다:

1. **코퍼스 검색** (`search_corpus`): 전체 14,373개 문서를 대상으로 키워드 검색
   - IVF가 못 찾는 문서를 보완하는 역할
   - 서버 시작 시 전체 코퍼스를 인덱싱 (IDF 계산)

2. **후보 리랭킹** (`score`): 이미 검색된 후보 문서들에 키워드 점수 부여
   - IVF + BM25 코퍼스 검색으로 모은 후보들을 최종 정렬할 때 사용

---

## 7. 하이브리드 리트리버 (src/retriever — Retriever)

### Dual-Path 검색

```
                    "CrashLoopBackOff 해결방법"
                              │
               ┌──────────────┼──────────────┐
               ▼                             ▼
        [경로 1: IVF 검색]            [경로 2: BM25 검색]
        질문 벡터 vs 문서 벡터         키워드 매칭
        top_k × 3 = 15개             top_k × 2 = 10개
               │                             │
               └──────────────┬──────────────┘
                              ▼
                    중복 제거 + 합치기
                    (최대 25개 후보)
                              │
                              ▼
                    하이브리드 스코어링
                    (semantic × W1 + BM25 × W2)
                              │
                              ▼
                    소스 다양성 필터
                    (문서당 최대 1개)
                              │
                              ▼
                    최종 5개 선택
```

### 왜 Dual-Path인가

IVF 벡터 검색만으로는 부족한 경우가 있습니다:

```
질문: "ImagePullBackOff 에러"

IVF 벡터 검색 결과:
  1위: "이미지 관련 오류 해결" (0.65) — 의미적으로 비슷
  2위: "컨테이너 이미지 관리" (0.58) — 비슷한 주제

  → "ImagePullBackOff"라는 정확한 에러명이 있는 문서는 3위 밖

BM25 키워드 검색 결과:
  1위: "Pod 에러 상태 표" (0.89) — "ImagePullBackOff" 정확히 포함!

  → 벡터 검색이 놓친 문서를 키워드로 잡음
```

### 하이브리드 스코어링

두 경로의 후보를 합친 후, 각 후보에 대해 최종 점수를 계산합니다:

```python
combined_score = semantic_weight × semantic_score + keyword_weight × keyword_score
```

가중치는 쿼리 유형에 따라 달라집니다 (다음 섹션에서 자세히 설명).

### 소스 다양성 필터 (max_per_source=1)

같은 문서의 여러 청크가 상위를 독점하는 것을 방지합니다.

```
리랭킹 후 (max_per_source 적용 전):
  1위: ocp_troubleshooting_os.md::3  (0.72)
  2위: ocp_troubleshooting_os.md::5  (0.70)  ← 같은 문서!
  3위: ocp_troubleshooting_os.md::1  (0.69)  ← 같은 문서!
  4위: k8s_pod_disruptions.md::2     (0.68)
  5위: ocp-crashloop-ko.md::0        (0.67)  ← 실제로 필요한 문서가 밀려남

max_per_source=1 적용 후:
  1위: ocp_troubleshooting_os.md::3  (0.72)  ← 1개만 선택
  2위: k8s_pod_disruptions.md::2     (0.68)
  3위: ocp-crashloop-ko.md::0        (0.67)  ← 진입 성공!
  4위: ocp-core-concepts-ko.md::0    (0.65)
  5위: k8s_workload_types.md::1      (0.63)
```

---

## 8. 쿼리 분류기와 동적 가중치

### 쿼리 유형별 최적 가중치가 다른 이유

```
질문 A: "CrashLoopBackOff 해결방법"  (트러블슈팅)
  → "CrashLoopBackOff"라는 정확한 키워드가 중요
  → BM25 키워드 매칭 가중치를 높여야 함

질문 B: "Pod란 무엇이고 왜 필요한가?"  (개념)
  → "Pod의 역할", "컨테이너 오케스트레이션" 같은 의미적 유사성이 중요
  → 임베딩 벡터 검색 가중치를 높여야 함
```

### 쿼리 분류기

BM25 토크나이저로 질문을 분석하고, 힌트 키워드와 매칭하여 유형을 판단합니다.

```python
def classify_query(self, query):
    query_tokens = set(self.bm25._tokenize(query))

    if query_tokens & {"에러", "문제", "안됨", "실패", "crashloopbackoff", "pending", "oom"}:
        return "troubleshooting"
    elif query_tokens & {"방법", "설정", "생성", "삭제", "yaml", "어떻게"}:
        return "procedure"
    elif query_tokens & {"뭐야", "무엇", "이란", "개념", "설명"}:
        return "concept"
    elif query_tokens & {"차이", "비교", "vs"}:
        return "comparison"
    # ...
```

### 동적 가중치 테이블

| 쿼리 유형 | Semantic 가중치 | BM25 가중치 | 이유 |
|-----------|---------------|------------|------|
| troubleshooting | 0.6 | 0.4 | 에러명/명령어 키워드 매칭 중요 |
| procedure | 0.6 | 0.4 | 명령어/설정 키워드 매칭 중요 |
| concept | 0.8 | 0.2 | 의미적 유사성으로 관련 개념 문서 찾기 |
| comparison | 0.7 | 0.3 | 균형 |
| overview | 0.7 | 0.3 | 균형 |
| general | 0.7 | 0.3 | 기본값 |

### 한국어 문서 부스트

한국어로 질문하면 한국어 문서(`-ko.md`)에 +0.08 점수 부스트를 줍니다.

**왜 필요한가**: BM25 토크나이저가 공백 기반이라 영어에 유리합니다. "CrashLoopBackOff"라는 영단어는 영문 문서에서 정확히 매칭되어 BM25 점수가 0.79~0.80으로 뜀니다. 반면 한국어 문서의 BM25 점수는 0.40~0.60으로 낮습니다. 이 편향을 보정하지 않으면 한국어 질문에 영문 문서만 올라옵니다.

```python
has_korean = bool(re.search(r'[\uac00-\ud7af]', query))

if has_korean:
    source = candidate.metadata.get("source", "")
    if source.endswith("-ko.md"):
        combined_score += 0.08  # 한국어 문서 부스트
```

---

## 9. 인접 청크 확장 (Adjacent Chunk Expansion)

### 문제

검색에서 chunk 0(개요)만 잡히면, LLM이 "해결 방법"이 있는 chunk 1, 2의 내용을 모릅니다.

```
ocp-crashloop-ko.md::0  "CrashLoopBackOff 개요..." ← 검색됨
ocp-crashloop-ko.md::1  "원인별 진단 방법..."      ← 검색 안 됨
ocp-crashloop-ko.md::2  "해결 명령어 모음..."      ← 검색 안 됨

→ LLM: "CrashLoopBackOff에 대한 개요는 있지만 해결 방법 데이터가 부족합니다"
```

### 해결: 앞뒤 ±2 청크 자동 병합

```python
def _expand_adjacent_chunks(self, results, window=2):
    for r in results:
        source, chunk_num = r.chunk_id.rsplit("::", 1)

        texts = []
        for offset in range(-window, window + 1):  # -2, -1, 0, +1, +2
            adj_id = f"{source}::{chunk_num + offset}"
            if adj_id in self._chunk_id_to_idx:
                texts.append(문서[adj_id].text)

        r.text = "\n\n".join(texts)  # 최대 5개 청크 합침
```

```
검색 결과: ocp-crashloop-ko.md::0

확장 후:
┌─ chunk -2 (없으면 스킵) ─┐
├─ chunk -1 (없으면 스킵) ─┤
├─ chunk  0 (검색된 것)    ─┤  → 하나의 텍스트로 합침
├─ chunk  1               ─┤
└─ chunk  2               ─┘

→ LLM이 개요 + 진단 방법 + 해결 명령어까지 볼 수 있음
```

---

## 10. 시맨틱 캐시 (src/cache)

### 왜 캐싱하는가

같은 질문을 다시 하면 검색 + LLM 호출을 반복하는 건 낭비입니다.
비슷한 질문이면 이전 답변을 재활용합니다.

### 동작 원리

```
새 질문: "Pod CrashLoopBackOff 해결"
    │
    ▼ 질문 임베딩 생성
    [0.12, -0.34, ...]
    │
    ▼ 캐시에 저장된 모든 질문 임베딩과 코사인 유사도 계산

    캐시 항목 1: "Pod CrashLoopBackOff 대처법"  → 유사도 0.97 > 0.95 ✓
    캐시 항목 2: "etcd 백업 방법"              → 유사도 0.23 < 0.95 ✗
    │
    ▼ 유사도 0.95 이상이면 캐시 히트 → 호환성 검증
    │
    ▼ 3중 호환성 검증 통과하면 → 캐시된 답변 바로 반환 (LLM 호출 안 함)
```

### 3중 호환성 검증 (오탐 방지)

코사인 유사도만으로는 부족합니다. 실제 겪은 문제들:

```
문제 1: "세줄요약" vs "네줄요약"
→ 코사인 유사도 0.97 (거의 같아 보임)
→ 하지만 답변은 완전히 달라야 함
→ 숫자 비교로 캐시 미스 처리

문제 2: "OpenShift 개요" vs "Kubernetes 개요"
→ 코사인 유사도 0.96 (비슷해 보임)
→ 하지만 다른 제품에 대한 질문
→ 엔티티 비교로 캐시 미스 처리
```

```python
def _is_cache_compatible(cls, query, cached_query):
    # 검증 1: 숫자가 다르면 미스
    if cls._extract_numbers(query) != cls._extract_numbers(cached_query):
        return False  # "3줄" vs "4줄"

    # 검증 2: 핵심 엔티티가 다르면 미스
    query_entity = cls._detect_entity(query_tokens)
    cached_entity = cls._detect_entity(cached_tokens)
    if query_entity and cached_entity and query_entity != cached_entity:
        return False  # "OpenShift" vs "Kubernetes"

    # 검증 3: 핵심 토큰이 하나도 안 겹치면 미스
    if not (informative_query & informative_cached):
        return False  # 완전히 다른 주제

    return True
```

---

## 11. 세션과 쿼리 리라이터 (src/session)

### 세션 관리

멀티턴 대화를 위해 세션별로 대화 이력을 관리합니다.

```
세션 "abc123":
  [user]      "OCP에서 Pod를 생성하는 방법은?"
  [assistant] "oc run 명령어를 사용하거나 YAML을 apply..."
  [user]      "그거 삭제하려면?"        ← "그거"가 뭔지 이전 대화를 봐야 함
```

- 세션 ID: UUID 기반 8자리 (예: "dfd36486")
- 최대 10턴 보관 (MAX_HISTORY_TURNS)
- TTL 3600초 (1시간) 후 자동 만료
- 10분마다 만료 세션 정리 (백그라운드 태스크)

### 쿼리 리라이터

멀티턴에서 "그거", "이거", "더 알려줘" 같은 맥락 의존적 질문을 독립적 질문으로 변환합니다.

```
대화 이력: "OCP에서 Pod 생성 방법"
새 질문: "그거 삭제하려면?"
→ 리라이트: "OCP에서 Pod를 삭제하려면?"
```

**핵심 규칙**: 최신 질문의 **동사는 절대 바꾸지 않음**. "삭제"를 "생성"으로 바꾸면 안 됩니다.

```
Few-shot 프롬프트 예시:
  이력: "OCP에서 Pod 생성 방법" → 최신: "그거 삭제하려면?"
  출력: "OCP에서 Pod를 삭제하려면?"  (동사 "삭제" 보존!)
```

소형 LLM(9B)에는 복잡한 규칙보다 구체적인 예시가 효과적입니다.

### 리라이트 판단 로직

모든 질문을 리라이트하지 않습니다:

```python
# 리라이트가 필요한 경우
- 대명사 포함: "그거", "이거", "그것", "저거"
- 짧은 질문: 15자 이하
- 맥락 의존 키워드: "더", "좀", "자세히", "다시"
- 이전 대화 있음 (history > 0)

# 리라이트 안 하는 경우
- 첫 질문 (이력 없음)
- 이미 독립적인 질문 ("readiness probe가 뭐야?")
- "OpenShift 개요" 같은 직접 패턴
```

---

## 12. LLM 클라이언트 (src/llm)

### OpenAI 호환 API

이 프로젝트의 LLM(Qwen3.5-9B)은 vLLM/Ollama/MLX 서버에서 구동되며, 모두 OpenAI 호환 API를 제공합니다.

```
POST http://서버주소/v1/chat/completions
{
    "model": "Qwen/Qwen3.5-9B",
    "messages": [
        {"role": "system", "content": "시스템 프롬프트..."},
        {"role": "user", "content": "질문..."}
    ],
    "stream": true,
    "max_tokens": 2048,
    "temperature": 0.7
}
```

### 스트리밍 응답

토큰 단위로 응답을 받아서 프론트엔드에 실시간 전달합니다:

```python
async def generate_stream(self, system_prompt, prompt, history):
    async with client.stream("POST", url, json=payload) as response:
        async for line in response.aiter_lines():
            # "data: {"choices":[{"delta":{"content":"Pod"}}]}"
            chunk = json.loads(line.removeprefix("data: "))
            token = chunk["choices"][0]["delta"].get("content", "")
            yield token  # "Pod", "는", " ", "쿠버", "네티", "스의", ...
```

### 멀티 엔드포인트

`.env`에 여러 LLM 서버를 등록하고 UI에서 전환할 수 있습니다:

```env
LLM_EP_COMPANY_URL=http://회사서버/v1
LLM_EP_MACMINI_URL=http://맥미니IP:8080/v1
LLM_EP_RTX_URL=http://RTX데스크탑IP:8080/v1
```

전환 시 `/v1/models` API를 호출해서 실제 모델명을 자동 감지합니다.

### Qwen3.5 Thinking 모드 비활성화

Qwen3.5는 기본적으로 "사고 과정"을 출력하는 thinking 모드가 있는데, 챗봇에서는 불필요합니다.
백엔드별로 다른 방법으로 비활성화합니다:

- vLLM: `chat_template_kwargs: {"enable_thinking": false}`
- Ollama: `options: {"reasoning_effort": "none"}`

---

## 13. 파이프라인 오케스트레이터 (src/pipeline)

### 역할

모든 컴포넌트를 순서대로 호출하고, 각 단계의 트레이스(실행 로그)를 SSE로 전송합니다.

### 듀얼 모드 시스템 프롬프트

| 모드 | 프롬프트 특징 |
|------|-------------|
| 운영 (ops) | "참고 문서를 최대한 활용하여 정확하고 실용적인 답변 제공" |
| 학습 (learn) | "비유나 예시를 적극 활용, 단계별 설명, 기술 용어에 괄호 설명" |

공통 규칙:
- 참고 문서 기반 답변 (hallucination 방지)
- 한국어 답변
- 구조화된 형태 (번호, 불릿, 표)
- 영문 참고 문서도 한국어로 번역하여 답변에 포함
- 출처는 실제 파일명 사용 ("ocp-crashloop-ko.md에 따르면")

### 캐시 전략

- 캐시 키에 모드 접두사: `[ops]CrashLoopBackOff 해결` vs `[learn]CrashLoopBackOff 해결`
- 실패 응답(`"LLM 응답 오류"`)은 캐시하지 않음

### 추천 질문

시스템 프롬프트에 `FOLLOWUP_SUFFIX`를 추가하여 LLM이 답변 끝에 관련 질문 3개를 제안하도록 합니다.

```
[추천 질문]
1. CrashLoopBackOff 외에 자주 발생하는 Pod 에러는?
2. Pod 로그를 확인하는 다른 방법은?
3. 컨테이너가 OOMKilled될 때 대처법은?
```

프론트엔드에서 이를 파싱하여 클릭 가능한 칩으로 렌더링합니다.

---

## 14. API 서버 (src/api)

### FastAPI 기반

```python
app = FastAPI(title="OCP RAG Chatbot")
```

### 핵심 엔드포인트

**`POST /api/chat/stream`** — 메인 채팅 API
```json
// 요청
{
    "query": "Pod가 CrashLoopBackOff일 때 어떻게 해?",
    "session_id": "abc123",     // 없으면 자동 생성
    "top_k": 5,                 // 검색 결과 수
    "stream": true,
    "mode": "ops",              // "ops" 또는 "learn"
    "endpoint_key": "company"   // LLM 서버 선택
}
```

```
// SSE 응답 (이벤트 스트림)
event: trace
data: {"step":"session","status":"done","detail":{...},"ms":0}

event: trace
data: {"step":"rewrite","status":"done","detail":{...},"ms":15}

event: sources
data: [{"chunk_id":"ocp-crashloop-ko.md::0","score":0.72,"source":"ocp-crashloop-ko.md"}]

event: token
data: "Pod"

event: token
data: "가"

event: token
data: " CrashLoopBackOff"

event: done
data: {"session_id":"abc123","cached":false,"total_ms":1350}
```

### 서버 시작 시 초기화

```python
@app.on_event("startup")
async def startup():
    index = IVFIndex.load(INDEX_DIR)      # 디스크에서 벡터 인덱스 로드
    retriever = Retriever(index, engine)   # 리트리버 초기화
    retriever.bm25.index_corpus(docs)      # BM25 전체 코퍼스 인덱싱
    pipeline = RAGPipeline(...)            # 파이프라인 조립
```

**중요**: 인덱스는 서버 시작 시 1회만 로드됩니다. `data/index/`를 변경해도 서버를 재시작하지 않으면 반영되지 않습니다.

---

## 15. 프론트엔드 (frontend/index.html)

### 단일 파일 구조

프레임워크 없이 순수 HTML/CSS/JS 한 파일로 구성됩니다.

### 주요 UI 기능

- **다크 테마**: 어두운 배경, Pretendard 폰트
- **모드 셀렉터**: 운영(⚙️) / 학습(💡) 전환
- **웰컴 화면**: 모드별 추천 질문 3개 (랜덤 선택)
- **Pipeline Trace 패널**: 각 단계의 실행 상태 실시간 표시
- **마크다운 렌더링**: 볼드, 코드블록, 리스트, 테이블 지원
- **추천 질문 칩**: LLM 답변 끝의 추천 질문을 클릭 가능한 버튼으로 표시
- **"최신 대화" 점프 버튼**: 스크롤 올렸을 때 하단 표시
- **LLM 서버 선택**: 드롭다운으로 서버 전환 + 연결 상태 표시

### SSE 스트리밍 처리

```javascript
const eventSource = new EventSource('/api/chat/stream', { method: 'POST', body: ... });

eventSource.addEventListener('trace', (e) => {
    // Pipeline Trace 패널 업데이트
    updateTracePanel(JSON.parse(e.data));
});

eventSource.addEventListener('token', (e) => {
    // 답변 영역에 토큰 추가 (타자치는 효과)
    appendToken(JSON.parse(e.data));
});

eventSource.addEventListener('done', (e) => {
    // 스트리밍 완료 → 추천 질문 파싱 + 칩 렌더링
    finalizeResponse();
});
```

---

## 16. 데이터 수집과 정제 (scripts/)

### 데이터 파이프라인

```
[1단계] 데이터 수집
├── scripts/scrape_docs.py     → OCP/K8s 공식 문서 크롤링 → data/raw/
├── scripts/generate_docs.py   → LLM으로 한국어 합성 문서 생성 → data/raw/
└── 수동 추가                   → PDF, PPTX, 자체 문서 → data/raw/

[2단계] 정제
└── scripts/sanitize_corpus.py → 민감정보 치환 → data/sanitized_raw/
    - IP 주소 → [REDACTED_PRIVATE_IP]
    - 비밀번호 → [REDACTED_SECRET]
    - 이메일 → [REDACTED_EMAIL]
    - 내부 URL → [REDACTED_INTERNAL_URL]

[3단계] 인덱싱
└── scripts/build_index.py → 청킹 → 임베딩 → IVF 빌드 → data/index/

[4단계] 서비스
└── 서버 시작 → data/index/ 로드 → 질의응답 가능
```

### 합성 문서 생성

코퍼스에 특정 주제가 없으면 LLM으로 문서를 생성합니다.

```python
TOPICS = [
    {"filename": "ocp-crashloop-troubleshooting-ko.md",
     "prompt": "OCP/Kubernetes에서 CrashLoopBackOff 트러블슈팅 가이드를..."},
    {"filename": "k8s-core-concepts-ko.md",
     "prompt": "Kubernetes 핵심 개념을 한국어로..."},
    # ... 18개 토픽
]
```

**주의**: LLM이 생성한 문서에는 할루시네이션(사실과 다른 내용)이 포함될 수 있으므로 검수가 필요합니다. 중요한 명령어나 YAML 예시는 공식 문서와 대조해야 합니다.

---

## 17. 평가 프레임워크 (scripts/eval_questions.py)

### 왜 평가가 필요한가

"체감상 잘 되는 것 같다"로는 부족합니다. 72개 질문으로 체계적으로 측정해야 어디가 약한지 알 수 있습니다.

### 평가 방법

LLM을 호출하지 않고, **검색(retrieval)만** 테스트합니다. 검색 품질이 답변 품질의 상한선이기 때문입니다.

```python
# 평가 흐름
for question in 72_QUESTIONS:
    results = retriever.retrieve(question, top_k=5)
    top_score = results[0].score

    if top_score >= 0.6:  status = "PASS"
    elif top_score >= 0.4: status = "WEAK"
    else:                  status = "FAIL"
```

### 카테고리별 질문 예시

| 카테고리 | 수 | 예시 |
|---------|-----|------|
| concept | 20 | "쿠버네티스가 뭐야?", "Service 종류와 차이점" |
| procedure | 15 | "HPA 설정 방법", "Secret을 환경변수로 주입하는 방법" |
| troubleshooting | 14 | "CrashLoopBackOff 해결", "노드 NotReady 대응" |
| operations | 10 | "etcd 백업", "클러스터 리소스 사용량 확인" |
| cicd | 5 | "Blue-Green vs Canary 배포" |
| security | 4 | "Pod Security Standards 종류" |
| commands | 4 | "oc login 방법", "kubectl apply vs create" |

### 품질 변화 추적

| 시점 | 정확도 | 주요 변경 |
|------|--------|----------|
| 초기 | 59.7% | 기존 코드 + 데이터 |
| Phase 1 | 70.8% | BM25 동의어, 동적 가중치, n_probe 수정 |
| Phase 2 | 80.6% | 한국어 합성 문서 5개, 기존 문서 키워드 보강 |
| Phase 3 | 미측정 | max_per_source=1, 한국어 부스트, 프롬프트 완화 |

---

## 18. 설정 파라미터 튜닝 가이드

### 성능에 영향 큰 파라미터

| 파라미터 | 기본값 | 올리면 | 내리면 |
|---------|--------|-------|-------|
| CHUNK_SIZE | 512 | 청크가 길어짐 → 문맥 많지만 검색 정확도 ↓ | 청크 짧아짐 → 정확하지만 문맥 부족 |
| CHUNK_OVERLAP | 128 | 겹침 많아짐 → 벡터 수 증가, 경계 누락 ↓ | 겹침 적어짐 → 경계에서 문맥 끊김 |
| TOP_K | 5 | 더 많은 문서 참고 → 컨텍스트 커짐 | 적은 문서 → 빠르지만 정보 부족 가능 |
| IVF_N_PROBE | 16 | 더 많은 클러스터 탐색 → 정확도 ↑ 속도 ↓ | 적은 클러스터 → 빠르지만 문서 누락 |
| CACHE_SIMILARITY_THRESHOLD | 0.95 | 더 정확한 매칭만 캐시 히트 | 느슨한 매칭 → 캐시 히트 많지만 오탐 위험 |
| max_chars (context) | 6000 | 더 많은 텍스트 → LLM이 더 많은 정보 활용 | 적은 텍스트 → 빠르지만 정보 누락 |

### 현재 설정의 근거

- **CHUNK_SIZE=512, OVERLAP=128**: 한국어 문서에서 적절한 의미 단위. 너무 크면 "Pod 개요 + 트러블슈팅"이 한 청크에 섞여서 검색 부정확
- **IVF_N_PROBE=16**: 14K 벡터에서 전수탐색해도 26ms. 클러스터 누락 사고 방지
- **CACHE_THRESHOLD=0.95**: 0.92에서 "모니터링"과 "리소스 제한"이 오탐됨. 0.95 + 3중 검증
- **max_per_source=1**: 영문 문서가 BM25로 슬롯 독점하는 문제 해결
- **context max_chars=6000**: 4000에서 5위 문서가 잘렸음. 6000으로 5개 문서 전부 포함

---

## 19. 트러블슈팅에서 배운 교훈들

### 교훈 1: eval 점수 ≠ 실제 답변 품질

eval 스크립트에서 CrashLoopBackOff 검색 점수가 0.732(PASS)인데, 실제 챗봇에서는 "데이터가 부족합니다"라고 답했습니다.

**원인**: eval은 "가장 높은 점수의 문서"만 보지만, 실제로는 "LLM에 전달되는 5개 문서 전체의 컨텍스트"가 중요합니다. 1위 문서가 일반 개념(점수 높음)이고, 실제 해결방법 문서가 top 5에서 밀려나면 LLM은 답할 수 없습니다.

### 교훈 2: 서버 재시작 없이는 인덱스가 반영 안 됨

인덱스를 재빌드해도 서버 메모리에는 이전 인덱스가 올라가 있습니다. `--reload` 모드는 코드 변경만 감지하고 데이터 파일 변경은 감지하지 않습니다. **인덱스 변경 후에는 반드시 서버 재시작**.

### 교훈 3: 캐시가 "실패 응답"을 저장하면 영원히 실패

데이터 추가 전에 "찾지 못했습니다" 응답이 캐시되면, 데이터 추가 후에도 캐시가 옛날 실패 응답을 반환합니다. 서버 재시작으로 캐시를 초기화하거나 실패 응답 캐시 방지 로직이 필요합니다.

### 교훈 4: BM25의 언어 편향

공백 기반 BM25 토크나이저는 영어에 유리합니다. "CrashLoopBackOff"는 영문 문서에서 한 단어로 정확히 매칭되어 BM25 점수 0.79를 받지만, 한국어 문서에서는 주변 한국어 텍스트와 섞여서 0.40 수준입니다. 한국어 문서 부스트(+0.08)로 보정합니다.

### 교훈 5: 소형 LLM에는 Few-shot이 규칙보다 효과적

Qwen3.5-9B(4bit)에 장황한 규칙을 주면 잘 안 따릅니다. "대명사를 구체적 대상으로 바꿔라, 단 동사는 바꾸지 마라"보다, 구체적인 예시 3개를 보여주는 게 훨씬 효과적입니다.

### 교훈 6: RAG 시스템은 코퍼스가 답변 품질의 상한선

검색이나 리랭킹을 아무리 튜닝해도, 코퍼스에 해당 주제 문서가 없으면 답을 못합니다. "답변이 이상하다" → 먼저 코퍼스에 관련 문서가 있는지 확인.

---

## 20. 용어 사전

| 용어 | 설명 |
|------|------|
| **RAG** | Retrieval-Augmented Generation. 검색 + LLM 결합 기법 |
| **임베딩 (Embedding)** | 텍스트를 숫자 벡터로 변환하는 것 |
| **벡터 (Vector)** | 숫자 배열. [0.12, -0.34, 0.56, ...] 형태 |
| **코사인 유사도** | 두 벡터가 가리키는 방향의 유사도. -1~1 범위 |
| **IVF** | Inverted File Index. 벡터를 클러스터로 분류해서 빠르게 검색 |
| **K-Means** | 데이터를 K개 그룹으로 분류하는 알고리즘 |
| **n_probe** | IVF 검색 시 탐색할 클러스터 수 |
| **BM25** | 전통적인 키워드 기반 문서 검색 알고리즘 |
| **IDF** | Inverse Document Frequency. 단어의 희귀도 |
| **청킹 (Chunking)** | 긴 문서를 작은 조각으로 나누는 것 |
| **리랭킹 (Reranking)** | 검색 결과의 순위를 재조정하는 것 |
| **하이브리드 검색** | 벡터 검색 + 키워드 검색을 합치는 방식 |
| **시맨틱 캐시** | 의미적으로 비슷한 질문의 답변을 재활용하는 캐시 |
| **SSE** | Server-Sent Events. 서버 → 클라이언트 단방향 실시간 통신 |
| **LRU** | Least Recently Used. 가장 오래 안 쓴 항목부터 제거하는 캐시 정책 |
| **토큰** | LLM이 처리하는 텍스트의 최소 단위 (보통 2~4글자) |
| **vLLM** | LLM 서빙 프레임워크. OpenAI 호환 API 제공 |
| **Qwen** | 알리바바에서 만든 LLM 시리즈 |
| **컨텍스트** | LLM에 전달하는 참고 자료 텍스트 |
| **파이프라인** | 여러 처리 단계를 순서대로 연결한 것 |
| **코퍼스 (Corpus)** | 검색 대상이 되는 전체 문서 집합 |
| **동의어 확장** | 검색 시 유사 단어도 함께 검색하는 기법 |
| **조사 제거** | "파드에서" → "파드"처럼 한국어 조사를 떼어내는 것 |
| **할루시네이션** | LLM이 사실과 다른 내용을 생성하는 현상 |
| **Few-shot** | LLM에 예시 몇 개를 보여줘서 원하는 동작을 유도하는 기법 |
| **Pipeline Trace** | 파이프라인 각 단계의 실행 로그 |
