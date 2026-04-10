# Project

## Product Definition

`Play Book Studio`의 중심은 챗봇 데모가 아니라 `OpenShift 지식 제련소`다. 이 저장소의 본체는 원천 데이터를 정제해 아래 두 산출물로 승격하는 것이다.

1. `Gold-Corpus`
2. `Gold-Manualbook`

챗봇, runtime UI, answer API는 이 산출물을 소비하는 인터페이스일 뿐이다. 코퍼스 품질, 메타데이터 보존, 매뉴얼북 가독성, 앵커 추적성이 약하면 데모가 그럴듯해 보여도 제품은 미완성이다.

이 제품의 계약은 아래와 같다.

- OpenShift 운영/학습에 바로 쓸 수 있는 `고품질 한국어 지식 베이스`를 만든다.
- `공식 KO 문서`, `공식 EN fallback 문서`, `GitHub 원본/응용 트러블슈팅 데이터`를 플레이북급 지식 단위로 제련한다.
- 수집부터 답변까지 `출처`, `버전`, `번역 상태`, `법적 출처`, `신뢰도`, `앵커`, `검증 가능성`을 보존한다.
- 모든 답변은 아래 구조를 강제한다.
  - `Situation Summary`
  - `Judgment Basis`
  - `Action Steps`
  - `Verification`
  - `Next Branch`
  - `Evidence Anchors`

## Scope

### Initial Scope

초기 출하 범위는 `OpenShift 4.20` 단일 버전이다.

포함 범위:

- OpenShift 4.20 `공식 KO 문서`
- KO 커버리지가 비는 경우 보강용으로 쓰는 OpenShift 4.20 `공식 EN fallback 문서`
- 근거와 재현 가능성이 확인된 `GitHub 원본 트러블슈팅 데이터`
- 같은 지식을 동시에 만드는 이중 산출물
  - retrieval용 코퍼스
  - 사람이 읽는 한국어 매뉴얼북

초기 비포함 범위:

- 버전 경계를 무시한 멀티버전 혼합 검색
- 리뷰되지 않은 기계번역 결과의 최종 매뉴얼북 승격
- 프로젝트 데이터와 무관한 범용 챗봇 품질 경쟁

### Expansion Path

버전 확장은 `4.20`에서 시작하고, 이후 `4.18 -> 4.19 -> 4.21` 순으로 넓힌다.

확장 규칙:

- 각 버전은 독립적인 pack 경계로 유지한다.
- 공통 canonical 개념은 허용하되 출하 산출물은 반드시 버전 식별 가능해야 한다.
- `4.20`이 코퍼스, 매뉴얼북, 앵커, 답변 acceptance를 통과하기 전에는 새 버전을 추가하지 않는다.

## Lane Definitions

### Source Lanes

`Lane 1. Official KO`

- 한국어 지식의 최우선 원천 lane
- 정규화와 품질 검사를 통과하면 바로 승격 후보가 된다

`Lane 2. Official EN Fallback`

- 공식 KO가 없거나 약한 영역만 메운다
- 한국어 Gold 자산으로 승격되기 전에 번역 및 리뷰 gate를 통과해야 한다

`Lane 3. GitHub Raw Troubleshooting`

- issue, discussion, PR 맥락, 운영 장애 기록 같은 GitHub 원본 근거
- 추출, 정규화, 재현성 검토 없이 최종 사용자 가이드로 출하할 수 없다

`Lane 4. Applied Playbook`

- 신뢰 가능한 여러 lane에서 추출한 운영형 조치 가이드
- 항상 원본 근거 앵커를 역추적할 수 있어야 한다

### Refining Pipeline

`Bronze -> Silver -> Silver-KO -> Gold-Corpus -> Gold-Manualbook -> Index`

`Bronze`

- 수집 직후의 원천 단위
- `original_url`, 버전 주장, 수집 시각, `legal_source`, 원문 본문을 보존한다

`Silver`

- canonical 정규화 구조
- 중복, 깨진 조각, 비정상 섹션을 정리한다
- 안정적인 section identity와 source lineage를 부여한다

`Silver-KO`

- EN fallback 문서의 한국어 렌더링 층
- `translation_status`와 reviewer 상태가 필수다

`Gold-Corpus`

- retrieval 최적화된 한국어 지식 단위
- chunking, 메타데이터, 앵커 매핑, 신뢰 신호를 확정한다

`Gold-Manualbook`

- 사람이 읽는 한국어 매뉴얼북 산출물
- 절차, 개념, 경고, 검증 단계, 근거 링크를 읽기 좋게 렌더링한다

`Index`

- 승인된 Gold 자산만으로 만드는 검색/runtime 인덱스
- 검색 편의가 출처 신뢰와 메타데이터 보존을 앞서면 안 된다

## Success Criteria

이 repo는 아래가 동시에 성립할 때만 성공이다.

- `Gold-Corpus`가 OpenShift 4.20 운영형/학습형 질문의 hard miss를 실제로 줄인다.
- `Gold-Manualbook`이 번역 찌꺼기가 아니라 읽을 수 있는 한국어 기술 매뉴얼 수준이다.
- 모든 출하 단위가 `version`, `translation_status`, `source_type`, `original_url`, `legal_source`, `trust_level`, `anchor`, `verifiability`를 보존한다.
- 챗봇 답변 표면이 항상 `Situation Summary -> Judgment Basis -> Action Steps -> Verification -> Next Branch -> Evidence Anchors` 구조를 유지한다.
- 사용자가 답변에서 출발해 앵커, 매뉴얼북 섹션, 원문 출처까지 provenance를 잃지 않고 이동할 수 있다.

## Non-Goals

아래는 제품의 중심 목표가 아니다.

- 말투만 좋은 범용 챗봇 데모
- 약한 소스 데이터와 깨진 retrieval을 프롬프트 튜닝으로 덮는 것
- 명시적 버전 스코프 없이 여러 버전을 한 답변에 섞는 것
- GitHub 일화를 공식 제품 사실처럼 출하하는 것
- 리뷰되지 않은 fallback 번역을 최종 지식 자산으로 승격하는 것

## Phases

`Phase 0. OCP 4.20 Foundry Contract`

- 파이프라인, 메타데이터, 앵커, 리뷰 계약을 고정한다
- `4.20`을 유일한 출하 버전 경계로 둔다

`Phase 1. OCP 4.20 Official KO Core Completion`

- 고가치 운영 영역의 공식 KO lane 커버리지를 끌어올린다
- KO 우선 소스로 Gold-Corpus와 Gold-Manualbook을 만든다

`Phase 2. OCP 4.20 EN Fallback to Reviewed KO`

- KO 공백 영역을 EN fallback으로 메운다
- 리뷰된 한국어 번역만 Gold 자산으로 승격한다

`Phase 3. GitHub Troubleshooting Playbook Integration`

- GitHub 원본 근거를 foundry에 편입한다
- 검증된 패턴만 applied troubleshooting playbook으로 승격한다

`Phase 4. Multi-Version Expansion`

- `4.20`에서 `4.18~4.21`로 확장한다
- 버전별 pack, index, answer scoping을 무너뜨리지 않는다

## Acceptance Criteria

제품 계약은 아래가 모두 충족될 때만 합격이다.

- `4.20`이 명확한 버전 경계를 가진 단일 지식 pack으로 출하 가능하다.
- 공식 KO, EN fallback 번역, GitHub 트러블슈팅의 세 source lane이 실제로 동작한다.
- provenance와 안정적인 anchor 없이 존재하는 Gold 자산이 없다.
- EN fallback 기반 한국어 매뉴얼북 최종본에는 반드시 번역 리뷰 상태가 있다.
- 동일한 source를 corpus, manualbook, runtime answer에서 일관되게 추적할 수 있다.
- 최종 답변이 6단 구조를 지키고 unsupported synthesis 대신 evidence anchor를 제시한다.
- `4.18~4.21`로 넓혀도 버전 식별이 무너지지 않는 확장 경로가 문서상 분명하다.
