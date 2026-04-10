# System Rules

## System Mission

이 저장소는 챗봇 외형을 키우기 위해 존재하지 않는다. 시스템은 항상 `corpus quality`, `manualbook quality`, `metadata fidelity`, `anchor traceability`를 답변 말투나 데모 인상보다 우선한다.

## Task Contract

모든 태스크는 아래 계약을 먼저 선언하고 끝까지 보존해야 한다.

- 1급 산출물 대상
  - `Bronze`
  - `Silver`
  - `Silver-KO`
  - `Gold-Corpus`
  - `Gold-Manualbook`
  - `Index`
- 대상 버전 스코프
  - 시작점은 `OCP 4.20`
- 대상 source lane
  - `Official KO`
  - `Official EN Fallback`
  - `GitHub Raw Troubleshooting`
  - `Applied Playbook`

기본 개선 순서는 고정이다.

1. `Input data / corpus quality`
2. `Normalization / preprocessing`
3. `Retrieval / retriever`
4. `Multi-turn / session behavior`
5. `Generation quality`

상위 데이터 문제가 있는데도 프롬프트나 표면 렌더링만 만져서 덮는 것은 금지한다.

## Trust Hierarchy

신뢰도는 암묵값이 아니라 명시값이어야 하며 파이프라인 전체로 전파되어야 한다.

`Tier 1. Official KO`

- 스코프된 OpenShift 버전에 대한 vendor 공식 한국어 문서

`Tier 2. Official EN with Reviewed KO Promotion`

- vendor 공식 영어 문서
- 한국어 승격은 translation review gate를 통과한 경우만 허용

`Tier 3. GitHub Verified Evidence`

- GitHub issue, PR, discussion, 코드 연계 트러블슈팅 근거
- 재현 가능한 증상, 해결 논리, 또는 상위 근거와의 교차 검증이 필요

`Tier 4. Applied Playbook Synthesis`

- Tier 1~3 근거에서 추출한 운영형 조치 가이드
- 상위 근거 앵커를 반드시 보존

`Tier 5. Model Prose`

- 생성 문장 자체
- 어떤 경우에도 권위 있는 원천으로 취급하지 않음

상위 tier는 하위 tier를 덮는다. 하위 tier는 설명을 보강할 수는 있어도 상위 근거와 충돌하면 안 된다.

## Grounding Rules

모든 출하 답변과 승격 지식 단위는 retrievable evidence에 묶여 있어야 한다.

필수 답변 구조:

1. `Situation Summary`
2. `Judgment Basis`
3. `Action Steps`
4. `Verification`
5. `Next Branch`
6. `Evidence Anchors`

Grounding 규칙:

- 명령, 아키텍처, 제한, 기본값, 운영 동작에 대한 주장에는 source anchor가 있어야 한다.
- 버전이 섞인 근거를 쓸 때는 한 버전으로 답변을 고정하거나 버전 차이를 명시적으로 분리해야 한다.
- 근거가 약하거나 충돌하면 답변이 그 불확실성을 드러내야 한다.
- 챗봇은 grounded asset의 렌더링 층이지 독립적인 권위자가 아니다.

## Version Contract

버전은 부가 메모가 아니라 1급 필드다.

- source unit, normalized node, corpus chunk, manualbook section, index entry는 모두 명시적 버전 스코프를 가져야 한다.
- 초기 출하 범위는 `OpenShift 4.20` 단일 버전이다.
- `4.18~4.21` 확장 시 버전별 격리, pack identity, answer scoping을 유지해야 한다.
- 버전 분리를 명시하지 않은 cross-version synthesis는 금지한다.

## Provenance and Legal Preservation

아래 메타데이터는 모든 파이프라인 단계에서 살아남아야 한다.

- `product`
- `version`
- `source_lane`
- `source_type`
- `original_url`
- `original_title`
- `legal_source`
- `license_or_terms`
- `retrieved_at`
- `translation_status`
- `review_status`
- `trust_level`
- `anchor_id`
- `anchor_text`
- `verifiability`

`original_url`, `legal_source`, `version identity`를 드롭하거나 조용히 바꾸는 merge는 금지한다.

## Anchor Contract

앵커는 제품의 척추다.

승격 단위는 반드시 아래를 만족해야 한다.

- 안정적인 `anchor_id`
- 사람이 읽을 수 있는 anchor label
- 상위 `original_url` 또는 그에 준하는 immutable source locator
- section 또는 step 단위 재진입 가능성
- answer citation에서 corpus, manualbook, source까지 역추적 가능한 경로

앵커 규칙:

- `Gold-Corpus`, `Gold-Manualbook`, `Index`는 같은 anchor lineage를 참조해야 한다.
- 답변 citation이 근거 원문을 다시 열지 못하면 계약 실패다.
- anchor 재작성에는 migration 또는 redirect가 필요하며, silent breakage는 금지한다.

## Translation Review Gate

기계번역만으로는 Gold 승격이 불가능하다.

규칙:

- EN fallback은 명시적 번역 상태와 함께 `Silver-KO`까지는 올라갈 수 있다.
- `Silver-KO`에서 `Gold-Corpus` 또는 `Gold-Manualbook`으로 가려면 review 상태, source 보존, 원문과의 anchor parity가 필요하다.
- 핵심 절차, 경고, prerequisite, command block, rollback guidance는 의미 보존 검토를 통과해야 한다.
- 리뷰가 끝나지 않았으면 Gold 아래 단계에 남기거나 비최종 상태를 명시해야 한다.

## Eval Gate

어떤 자산도 해당 gate를 통과하지 않으면 승격하거나 출하할 수 없다.

최소 eval 기준:

- `Bronze -> Silver`
  - source completeness
  - parse success
  - source metadata retention
- `Silver -> Silver-KO`
  - translation traceability
  - anchor parity
  - critical block untranslated detection
- `Silver-KO -> Gold-Corpus`
  - retrieval usefulness
  - metadata completeness
  - promoted unit의 broken anchor rate 0
- `Gold-Corpus -> Gold-Manualbook`
  - readability
  - procedure structure integrity
  - source 및 original URL visibility
- `Gold assets -> Index`
  - 승인된 Gold 자산만 index에 포함
  - version leakage 0
- `Runtime Answer Surface`
  - 6단 답변 구조 유지
  - answer-to-anchor traceability
  - missing evidence 위에 unsupported claim 없음

## Merge Gate

merge 요청은 최소한 아래를 밝혀야 한다.

- target phase
- target version
- target lane
- target pipeline stage
- 영향을 받는 metadata field
- eval gate 결과 근거
- anchor가 추가, 변경, 유지 중 무엇인지

아래 중 하나라도 해당하면 merge를 막아야 한다.

- 답변 외형은 좋아졌지만 source trust를 무시하거나 훼손한다.
- 지식 콘텐츠를 추가했는데 `original_url`, `legal_source`, `version identity`가 없다.
- fallback 번역을 review 상태 없이 승격한다.
- corpus, manualbook, runtime 중 하나에서라도 anchor resolution이 깨진다.
- 여러 OpenShift 버전을 명시 없이 섞는다.

## Runtime Discipline

runtime은 foundry 산출물을 소비해야지 재정의하면 안 된다.

- retrieval은 승인된 indexed asset만 검색할 수 있다.
- 답변은 grounded input에서 나온 판단과 조치만 표면화해야 한다.
- 검색 근거가 부족하면 단정 대신 한계를 드러내야 한다.
- UI나 데모가 좋아 보여도 corpus/manualbook 계약 실패를 덮을 수 없다.
