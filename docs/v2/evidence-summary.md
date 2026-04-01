# Evidence Summary

## Purpose

이 문서는 planB의 현재 상태를 **점수 방어용 증거 묶음**으로 한 번에 읽을 수 있게 정리한다.

핵심 질문은 아래다.

- 지금 실제로 무엇이 통과했는가?
- 어떤 파일이 권위 있는 증거인가?
- 아직 남은 리스크는 무엇인가?

## Generated summary report

자동 집계 리포트:

```bash
python3 eval/evidence_summary_report.py
```

기본 출력:

- `data/manifests/generated/evidence-summary-report.json`

## Current high-value evidence

### 1. Stage 11 reindex / activation / smoke

- `data/manifests/generated/stage11-4-20-seed-reindex-report.json`
- `data/manifests/generated/stage11-4-20-seed-activation-report.json`
- `data/manifests/generated/stage11-4-20-seed-smoke-report.json`

이 세 파일은 다음을 보여준다.

- 4.20 balanced corpus가 실제 Stage 11 index로 재구축됨
- `stage11-4-20-seed`가 bootstrap current가 됨
- smoke runtime이 실제로 동작함
- retrieval alignment도 현재 smoke 기준에서는 모두 통과함

### 2. Stage 12 live runtime

- `data/manifests/generated/stage12-live-runtime-report.json`

이 파일은 다음을 보여준다.

- bridge `/health`, `/ready`, `/v1/models`
- local `BAAI/bge-m3` embedding path
- OpenDocuments runtime
- gateway stream
- viewer click-through

즉, 현재 planB는 **local embeddings + live gateway** 경로에서 실제로 동작하고, Stage 12 smoke 기준으로는 explicit local chat fallback까지 포함한 serving-path 증거를 갖고 있다.

### 3. Cache strategy proof

- `data/manifests/generated/cache-strategy-report.json`
- `docs/v2/cache-strategy-proof.md`

이 증거는 다음을 보여준다.

- embedding cache hit/miss
- query cache hit/miss
- grounding 유지
- cache-safe readiness

### 4. Vector index proof

- `data/manifests/generated/vector-index-proof.json`
- `docs/v2/vector-index-design.md`

이 증거는 다음을 보여준다.

- 저장 형식 직접 정의
- cosine similarity 검색
- top-k 결과 구조
- save/load 경로

다만 이건 아직 **운영 runtime의 주 검색 경로**가 아니라 direct implementation proof다.

### 5. Multiturn proof

- `eval/fixtures/multiturn_rewrite_sample_report.json`

이 증거는 다음을 보여준다.

- 4개 시나리오
- 총 20턴
- source_dir / topic / version / rewrite term pass 유지

주의: 이 파일은 `eval/fixtures/` 아래 sample proof이며, 현재 gate의 유일한 권위 문서는 아니다.

## How to read the current score story

현재 상태는 아래처럼 읽는 것이 가장 정확하다.

1. **제품은 실제로 동작한다**
   - Stage 11/12 evidence가 있다.
2. **정확도는 smoke 기준으로 회복됐다**
   - retrieval alignment가 smoke path에서 통과한다.
3. **멀티턴과 캐시는 직접 구현 증거가 있다**
   - dedicated proof reports가 있다.
4. **Vector Index 직접성은 아직 proof 단계다**
   - 운영 주경로 대체까지는 아니다.

그리고 범위를 이렇게 읽어야 한다.

- Stage 12는 live serving-path 증거다.
- 하지만 현재 smoke는 company token 없이 explicit local chat fallback을 허용한 상태에서 통과했다.
- 따라서 이 문서는 “company upstream chat까지 완전히 검증됐다”는 주장용이 아니라, **현 planB serving-path가 실제로 동작한다는 증거**로 읽어야 한다.

## Remaining risks

가장 큰 남은 리스크는 아래 순서다.

1. **Vector Index 직접 구현성 부족**
2. **widened corpus 기준 성능 비교 증거 부족**
3. **raw retrieval 자체의 근본 개선 부족**

## Bottom line

현재 planB는 더 이상 “준비 중인 실험”이 아니라,

- 4.20 corpus 재구축
- Stage 11 activation
- Stage 12 live runtime
- cache proof
- vector index proof
- multiturn proof

까지 갖춘 **실동작 + 증거 보유 상태**다.

즉, 이제 남은 일은 제품이 안 돌아서 고치는 일이 아니라, **100점에 더 가까운 설명 가능성과 직접 구현성 증거를 더 쌓는 일**이다.
