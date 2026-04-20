---
status: reference
doc_type: schema
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# Knowledge Object Schema v1

이 문서는 PBS가 `source -> playbook -> corpus` 사이에 둘 공통 truth layer의 최소 스키마를 정의한다.

핵심 원칙은 하나다.

`페이지를 저장하지 말고, 지식을 저장한다.`

## 1. 목적

이 스키마는 아래 문제를 해결하기 위해 필요하다.

- 새 source가 들어와도 기존 책 전체를 지능적으로 갱신하지 못하는 문제
- viewer와 chat이 같은 truth를 완전히 공유하지 못하는 문제
- repair 결과가 구조적으로 축적되지 않는 문제
- source lineage와 contradiction가 표면에 잘 드러나지 않는 문제

## 2. 기본 계층

모든 knowledge object는 아래 4개 계층을 가진다.

1. `identity`
2. `content`
3. `evidence`
4. `lifecycle`

## 3. 공통 필드

모든 object는 최소한 아래 필드를 가져야 한다.

- `object_id`
- `object_type`
- `canonical_key`
- `title`
- `summary`
- `source_refs[]`
- `confidence`
- `freshness`
- `status`
- `updated_at`

### 3.1 object_id

시스템 내부 고유 식별자.

### 3.2 object_type

허용 타입:

- `entity`
- `concept`
- `procedure`
- `command`
- `claim`
- `warning`
- `table`
- `figure`
- `glossary_term`
- `operator_note`

### 3.3 canonical_key

source마다 이름이 조금 달라도 같은 object로 병합하기 위한 기준 키.

예:

- `concept:rbac`
- `entity:machine-config-operator`
- `procedure:drain-node`

## 4. 핵심 object 타입

### 4.1 Entity

대상:

- component
- operator
- resource kind
- subsystem

예시:

- etcd
- MachineConfigOperator
- IngressController

주요 필드:

- aliases[]
- category
- short_definition
- related_concepts[]
- related_procedures[]

### 4.2 Concept

대상:

- RBAC
- disconnected install
- agent-based installer

주요 필드:

- explanation
- prerequisites[]
- related_entities[]
- related_procedures[]
- conflict_notes[]

### 4.3 Procedure

대상:

- backup etcd
- drain node
- grant cluster role

주요 필드:

- goal
- prerequisites[]
- ordered_steps[]
- validation_steps[]
- rollback_steps[]
- commands[]
- expected_outcome

### 4.4 Command

대상:

- shell command
- yaml snippet
- config fragment

주요 필드:

- language
- code
- command_kind
- risk_level
- related_procedure_id

### 4.5 Claim

대상:

- 사실 주장
- 버전 의존 설명
- 비교 판단

주요 필드:

- claim_text
- evidence_refs[]
- scope
- version_window
- superseded_by
- contradicted_by[]

### 4.6 Warning

대상:

- 주의 사항
- 실패 가능성
- destructive action note

주요 필드:

- severity
- warning_text
- trigger_condition
- mitigation

### 4.7 Table

대상:

- 비교표
- 설정표
- 매핑표

주요 필드:

- headers[]
- rows[]
- table_kind
- interpretation

### 4.8 Figure

대상:

- diagram
- image
- architecture view

주요 필드:

- figure_path
- caption
- figure_kind
- interpretation

### 4.9 Operator Note

대상:

- 검증된 질의응답 파생 노트
- 운영 팁
- 비교 요약

주요 필드:

- note_text
- derived_from
- supporting_objects[]
- approval_state

## 5. Evidence Model

모든 object는 source lineage를 잃으면 안 된다.

최소 evidence ref 필드:

- `source_id`
- `source_kind`
- `source_title`
- `viewer_path`
- `section_anchor`
- `excerpt`
- `confidence`

원칙:

- object는 evidence 없이 존재할 수 없다
- synthesis도 evidence chain을 가져야 한다
- user/private source는 boundary 정보도 같이 달려야 한다

## 6. Lifecycle Model

모든 object는 고정값이 아니라 진화한다.

최소 lifecycle 상태:

- `draft`
- `review`
- `ready`
- `promoted`
- `superseded`
- `quarantined`

## 7. Merge Rules

새 source가 들어왔을 때 object는 아래 중 하나를 선택한다.

1. `enrich`
2. `revise`
3. `contradict`
4. `supersede`
5. `create_new`

### 7.1 enrich

기존 object와 같은 의미이고 새 evidence가 추가된 경우.

### 7.2 revise

기존 object의 설명/절차를 더 정확히 수정하는 경우.

### 7.3 contradict

새 source가 기존 claim과 충돌하지만, 어느 쪽이 이긴다고 확정할 수 없는 경우.

### 7.4 supersede

새 source가 더 최신이고 더 강한 source로 기존 내용을 대체하는 경우.

### 7.5 create_new

새 object인 경우.

## 8. Playbook/Corpus 파생 규칙

### 8.1 Playbook

Playbook composer는 아래 object를 우선 사용한다.

- concept
- entity
- procedure
- command
- warning
- table
- figure
- operator_note

### 8.2 Corpus

chunker는 아래를 우선 사용한다.

- claim
- procedure
- command
- warning
- evidence-backed summary

즉 book과 corpus는 같은 object graph를 다른 방식으로 푼다.

## 9. Pass/Fail 기준

이 스키마가 충분하다고 보려면 아래가 가능해야 한다.

- 새 source 하나가 여러 기존 playbook에 동시에 반영될 수 있다
- 같은 object의 source lineage를 추적할 수 있다
- contradiction와 supersession를 별도로 표현할 수 있다
- viewer와 chat이 같은 object를 서로 다른 표현으로 쓸 수 있다

## 10. Non-Goals

- 이 문서는 DB 테이블 설계서가 아니다
- 이 문서는 parser 구현 디테일 문서가 아니다
- 이 문서는 UI 카피 문서가 아니다

## 11. 한 줄 결론

PBS의 다음 truth layer는 `page collection`이 아니라 `knowledge object graph`여야 한다.
