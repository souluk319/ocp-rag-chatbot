# 100점 기준 구현 갭 분석

## 목적

이 문서는 `PROJECT.md`의 100점 평가 기준을 현재 저장소 상태와 직접 대조해,

- 지금 바로 점수를 받을 수 있는 영역
- 아직 점수를 다 받기 어려운 갭
- 전문가팀이 착수할 때 바로 분업할 수 있는 작업 묶음

을 정리하는 준비 문서다.

## 평가 기준 원천

- 과제 기준: `PROJECT.md`
- 제품/브랜치 기준: `README.md`, `docs/v2/project-plan-summary.md`
- 평가 권위: `docs/v2/evaluation-spec.md`, `docs/v2/stage10-evaluation-report.md`
- 요구사항 추적: `docs/v2/requirements-traceability.md`

## 현재 상태 한 줄 요약

현재 저장소는 **RAG 정확성, 멀티턴, citation, 서빙 경로, 폐쇄망 운영 흐름** 쪽은 이미 강한 근거를 갖고 있다. 반면 **Vector Index 직접 설계/구현**과 **과제형 캐싱 전략의 명시적 구현**은 아직 약하며, 이 두 항목이 100점 저지의 가장 큰 리스크다.

## 보수적 예상 점수

이 점수는 공식 채점이 아니라, 현재 코드/문서/증거를 기준으로 한 보수적 내부 추정치다.

| 평가 항목 | 배점 | 보수적 예상 | 판단 |
|---|---:|---:|---|
| RAG 정확성 | 30 | 24 | 강함. 정책형 retrieval, citation, grounded answer 근거가 있다. 다만 raw retrieval 약세와 section-aware chunk 실구현 공백이 남아 있다. |
| 멀티턴 처리 정확성 | 20 | 18 | 강함. 세션 메모리와 follow-up rewrite는 구현/검증되어 있고, 5턴 시나리오를 4개/20턴까지 확장한 증거도 있다. 다만 실사용 다양성과 runtime 실경로 replay는 더 넓혀야 한다. |
| 시스템 아키텍처 | 20 | 15 | 중상. 계층 분리와 운영 흐름은 좋다. 다만 Vector Index 직접 구현 요구와 OpenDocuments 의존 경계 설명을 더 날카롭게 해야 한다. |
| 코드 품질 및 설명 | 15 | 12 | 중상. 문서와 증거는 풍부하다. 하지만 “왜 이 구조가 과제 기준을 만족하는지”를 설명하는 발표형 자료는 더 필요하다. |
| 추가 요구사항 구현 | 15 | 11 | 보강 중. Streaming은 있고, 1차 query/embedding cache와 cache proof report도 들어갔다. 그러나 Vector Index 직접성과 widened corpus 성능 증거는 아직 부족하다. |
| **총계** | **100** | **80** | **현 상태는 강한 기반이지만 100점 상태는 아님** |

## 항목별 갭 분석표

| 항목 | 현재 근거 | 현재 판정 | 핵심 갭 | 우선순위 |
|---|---|---|---|---|
| RAG 정확성 30점 | `configs/rag-policy.yaml`, `app/ocp_policy.py`, `eval/stage9_policy_report.py`, `docs/v2/stage10-evaluation-report.md` | 강함 | raw retrieval가 여전히 약하고, policy rescue 의존도가 높다. section-aware chunk generation은 정의만 있고 완료 상태가 아니다. | 높음 |
| 멀티턴 20점 | `app/multiturn_memory.py`, `docs/v2/multiturn-memory-plan.md`, `eval/multiturn_rewrite_report.py`, `eval/benchmarks/p0_multiturn_scenarios.json`, `eval/fixtures/multiturn_rewrite_sample_report.json` | 강함 | 5턴 이상 구조와 4개 시나리오/20턴 증거는 확보됐다. 이제 runtime 실경로 replay와 더 넓은 운영형 질문군 확장이 필요하다. | 중상 |
| 아키텍처 20점 | `README.md`, `docs/v2/requirements-traceability.md`, `docs/v2/live-runtime-gateway.md`, `deployment/*` | 중상 | 구조는 설명 가능하지만, “직접 구현” 요구 대비 OpenDocuments/LanceDB 의존 경계와 자체 소유 영역을 더 명확히 정리해야 한다. | 높음 |
| 코드 품질/설명 15점 | `docs/v2/architecture-blueprint.md`, `docs/v2/project-plan-summary.md`, `docs/v2/requirements-traceability.md` | 중상 | 코드 설명 자료는 많지만, 채점자 질의에 바로 대응하는 “설계-코드-증거” 연결표가 아직 없다. | 중간 |
| Streaming | `app/opendocuments_openai_bridge.py`, `app/ocp_runtime_gateway.py`, `docs/v2/stage12-live-runtime-report.md` | 구현됨 | 현재는 pass. 다만 토큰/청크 스트림 품질을 발표형으로 설명할 자료를 더 만들면 좋다. | 중간 |
| Vector Index 직접 구현 | `deployment/run_live_runtime_smoke.py` 의 `vectorDb: 'lancedb'`, `deployment/opendocuments-stage6.config.template.ts` | 취약 | 과제 요구는 직접 설계/구현인데 현재 경로는 LanceDB/OpenDocuments 기반이다. **가장 큰 감점 리스크**. | 최상 |
| 세션 메모리 직접 구현 | `app/multiturn_memory.py`, `app/runtime_gateway_support.py` | 강함 | 과제 요구와 잘 맞는다. 다만 reset boundary / long-session 정책 설명을 더 보강하면 좋다. | 중간 |
| 성능 개선 전략 | `app/ocp_policy.py`, `configs/rag-policy.yaml`, `eval/stage9_policy_report.py` | 구현됨 | rerank/policy bias는 존재한다. 그러나 chunking 전략의 실구현/정량 비교는 더 필요하다. | 높음 |
| 캐싱 전략 | `app/runtime_cache.py`, `app/ocp_runtime_gateway.py`, `app/opendocuments_openai_bridge.py`, `eval/cache_strategy_report.py`, `docs/v2/cache-strategy-proof.md` | 부분 구현 | query cache와 embedding cache의 1차 구현, cache-safe readiness, grounding 유지, hit/miss proof report까지 반영됐다. 다만 query proof 범위는 local rescue payload에 한정되며, widened corpus 기준 성능 비교와 운영형 invalidation 증거가 더 필요하다. | 중상 |

## 점수 저지 리스크 3개

### 1. Vector Index 직접 구현 부족

현재 저장소는 런타임과 검증 경로에서 OpenDocuments + LanceDB 조합을 사용한다.

- 근거: `deployment/run_live_runtime_smoke.py`
- 근거: `deployment/opendocuments-stage6.config.template.ts`

과제 문구는 “Vector Index 구조 직접 설계 및 구현 (단순 라이브러리 호출 지양)”이므로, 현재 상태를 그대로 제출하면 가장 강한 공격 포인트가 된다.

### 2. 캐싱 전략의 제출형 증거 부족

현재 보이는 캐시는 다음 수준이다.

- `lru_cache` 기반 설정/카탈로그 캐시
- 세션 메모리 TTL
- `app/runtime_cache.py` 기반 TTL + LRU query cache
- `app/opendocuments_openai_bridge.py` embedding cache

하지만 아직 부족한 부분은 다음이다.

- widened corpus 기준 hit/miss 반복 보고서
- cache invalidation 정책의 운영 문서화
- widened corpus 기준 재현 가능한 성능 비교

즉, 캐시 자체는 이제 안전한 1차 구현과 proof report까지 들어갔지만 “무엇을 캐시했고 widened corpus에서 얼마나 이득이 있었는가”를 채점 언어로 방어하려면 추가 증거가 더 필요하다.

### 3. raw retrieval 약세와 chunk 전략 실증 부족

정책 보정 후 성능은 좋지만, 과제 질문에서 “단순 LLM 질의가 아니라 RAG 파이프라인으로 어떻게 정확도를 끌어올렸는가”를 물으면 다음 약점이 드러난다.

- raw retrieval baseline 약세
- chunk schema는 정의되어 있지만 section-aware chunk generation 자체는 아직 미완료로 추적됨

## 이미 강점인 영역

### 1. 멀티턴 직접 구현 근거

- `app/multiturn_memory.py`에 세션 메모리, follow-up cue, topic shift cue, version continuity, TTL, rewrite가 직접 구현되어 있다.
- `docs/v2/evaluation-spec.md` Track I가 5턴 grounded continuity를 직접 요구한다.
- `docs/v2/stage10-evaluation-report.md`는 multi-turn gate pass를 권위 문서로 남긴다.

### 2. 스트리밍 구현 근거

- `app/opendocuments_openai_bridge.py`는 `/v1/chat/completions`에서 streaming path를 제공한다.
- `app/ocp_runtime_gateway.py`는 `/api/v1/chat/stream` 경로에서 `sources`, `chunk`, `done` 이벤트를 유지한다.
- `docs/v2/stage12-live-runtime-report.md`는 live streaming smoke와 session continuity를 검증한다.

### 3. 운영형 구조와 설명 가능성

- `docs/v2/requirements-traceability.md`는 요구사항별 소유 문서와 exit evidence를 명확히 연결한다.
- `deployment/`는 bundle → stage → reindex → activate → rollback 흐름을 코드와 문서로 같이 갖고 있다.
- 이 구조는 단순 데모가 아니라 운영형 제품 설계라는 점에서 아키텍처 점수에 유리하다.

## 100점 달성을 위한 우선 작업 묶음

### A. 최상 우선순위

1. **Vector Index 직접 설계/구현 경로 확보**
   - 최소 제출용이라도 자체 index abstraction, 저장 형식, 검색 API, 근사/정확 검색 전략을 설명 가능한 코드로 확보해야 한다.
2. **캐싱 전략 운영형 증거 확장**
   - widened corpus 기준 query cache hit/miss 검증
   - widened corpus 기준 embedding cache hit/miss 검증
   - TTL / invalidation / evidence 정리

### B. 높은 우선순위

3. **멀티턴 시나리오 확장**
   - 운영형 5턴+ 시나리오 묶음 확대
   - topic shift / version shift / insufficient grounding 케이스 보강
4. **chunking 전략 실구현 및 정량 비교**
   - 현재는 schema/contract 중심이다.
   - chunking 전략이 정확도에 미친 영향을 정량으로 보여줘야 한다.

### C. 제출 설명력 강화

5. **설계-코드-증거 연결표 작성**
   - 질문 받았을 때 “어디 코드 / 어떤 보고서 / 어떤 지표”로 답할지 준비
6. **발표형 아키텍처 설명 자료 작성**
   - RAG → memory → policy → stream → citation → rollback 흐름을 한 장으로 설명 가능해야 한다.

## 전문가팀 착수안

| 역할 | 1차 책임 | 바로 시작할 일 |
|---|---|---|
| RAG/Search 엔지니어 | Vector Index, chunking, retrieval | 자체 index 구조 설계안, chunk 전략 비교 실험 |
| Backend/Serving 엔지니어 | streaming, session memory, cache | query/embedding cache 추가, 멀티턴 경계 정책 강화 |
| Evaluation/QA 엔지니어 | 점수화와 증거 자동화 | 100점 rubric 기반 리포트 자동 집계 |
| Architecture/Docs 리드 | 설명 가능성 | 설계-코드-증거 연결표, 질의 대응 문서 |

## 전문가팀 시작 전 준비 완료 조건

아래가 준비되면 바로 착수해도 된다.

- `PROJECT.md` 기준 해석 확정
- 현재 강점/약점 문서화 완료
- 최고 리스크가 Vector Index 직접성과 캐싱이라는 점 합의
- 작업을 A/B/C 우선순위로 자를 수 있음
- 각 역할이 “무엇을 만들면 점수가 오르는지” 바로 이해 가능함

## 결론

현재 저장소는 **작동하는 OCP 운영형 RAG 챗봇의 기반과 검증 증거**는 충분히 갖췄다. 하지만 `PROJECT.md` 기준 100점을 노리려면, 앞으로의 핵심은 기능 추가의 양이 아니라 아래 두 가지다.

1. **직접 구현 요구를 정면으로 만족시키는 Vector Index / Cache 경로 확보**
2. **이미 강한 멀티턴·retrieval·streaming·운영 구조를 채점 기준 언어로 다시 정리**

즉, 현재는 “좋은 제품형 프로토타입”에 가깝고, 100점 상태는 “과제 채점 언어로 방어 가능한 직접 구현형 시스템”까지 한 단계 더 올라가야 한다.
