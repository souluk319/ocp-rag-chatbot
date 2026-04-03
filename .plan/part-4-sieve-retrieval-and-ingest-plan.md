# Part 4. Sieve Retrieval And Ingest Plan

## Chapter 4.1 목표

검색 정밀도와 문서 수집 범위를 동시에 확장하되, 구조는 단순하고 검사 가능하게 유지한다.

## Chapter 4.2 현재 진단

### 현재 구조

- HTML 전처리 -> normalized sections -> chunks -> BM25/vector retrieval -> RRF fusion
- dense retrieval은 chunk 단위다.
- sentence-level similarity 전용 단계는 없다.

### 현재 답변

문장 단위 유사도 로직이 있냐는 질문에는 현재 기준으로 “없다”가 맞다.

- 현재 있는 것: chunk-level vector similarity
- 현재 없는 것: sentence-level retrieval, sentence-level rerank, answer-span extraction

## Chapter 4.3 Workstream A: Command Fast Lane

### 문제

- 운영 질문은 개념형 검색 경로보다 더 빠른 경로가 필요하다.

### 계획

- 명령어/단축 질문 전용 `ops snippet index`를 만든다.
- 대상은 `oc`, `oc adm`, `kubectl`, `etcd`, 인증서, RBAC, drain, logs, finalizers`다.
- retrieval 앞단에서 `fast lane candidate`를 평가하고, hit 시 짧은 grounded answer를 우선 생성한다.

### 테스트 영향

- 상위 30개 운영 질문 top-1 grounded hit 테스트
- command answer format golden test

## Chapter 4.4 Workstream B: Sentence Window Rerank

### 문제

- chunk는 맞는데 문장 수준 근거가 약한 상황이 있다.

### 계획

- 1차는 기존 chunk retrieval 유지
- 2차는 top-k chunk 내부에서 sentence/window split 후 rerank
- answer에는 sentence/window evidence를 다시 citation excerpt에 반영

### 목표

- “근거는 있는데 답이 엇나감”을 줄인다.
- step-by-step와 compare 답변의 본문 밀도를 올린다.

## Chapter 4.5 Workstream C: Upload Ingest Pipeline

### 지원 우선순위

1. `pdf`
2. `ppt/pptx`
3. `html`
4. `md/txt`

### 엔티티 설계

- `Document`
- `DocumentVersion`
- `ParseJob`
- `NormalizedDocument`
- `ChunkSet`
- `IndexStatus`

### 파이프라인

1. 업로드 저장
2. MIME/type 검증
3. parser 선택
4. normalized document 생성
5. viewer-friendly render 생성
6. chunking / embedding / indexing
7. status 기록

## Chapter 4.6 Workstream D: 보기 좋은 정규화 문서 시스템

### 계획

- 모든 업로드 문서를 동일 viewer schema로 변환한다.
- chapter / section / block / table / code 단위 메타데이터를 통일한다.
- 채팅 citation과 viewer anchor가 항상 1:1 대응되게 만든다.

## Chapter 4.7 테스트 영향

- 파일 타입별 ingest smoke test
- parse failure handling test
- normalized viewer rendering test
- chunk-to-viewer anchor consistency test
- sentence-window rerank quality regression test
