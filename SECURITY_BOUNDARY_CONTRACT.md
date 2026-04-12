# Security Boundary Contract

## Purpose And Scope

이 문서는 enterprise-private 문서 처리를 위한 minimum viable security boundary 를 고정한다.

시작점은 `tenant/workspace/pack 단위 default-deny 경계`다.

이 문서는 user-level 미세 권한 모델이나 full zero-trust 설계를 다루지 않는다. 지금 단계에서 필요한 것은 `private 문서가 무경계로 retrieval/viewer/answer/debug/egress에 떠다니지 못하게 막는 것`이다.

## Current Runtime Truth

현재 저장소의 사실은 아래다.

- `src/play_book_studio/ingestion/models.py` 와 `src/play_book_studio/canonical/models.py` 에는 `tenant_id`, `workspace_id`, `classification`, `access_groups`, `provider_egress_policy`, `approval_state`, `publication_state`, `redaction_state` 가 이미 내려가 있다.
- `validation_gate` 는 위 security / parsed metadata 가 비면 실제 release blocking 으로 처리한다.
- 현재 runtime 기본값은 `provider_egress_policy = unspecified`, `publication_state = candidate | published | restricted | blocked` 계약이다.
- `src/play_book_studio/app/sessions.py` 는 `artifacts/runtime/sessions` filesystem snapshot store 를 사용한다.
- `src/play_book_studio/app/server.py` 는 debug/session endpoint 를 제공한다.
- runtime report 기준 현재 session strategy truth 는 `filesystem_snapshot_store` 다.

즉, 보안 경계는 필드/세션/감사 뼈대는 구현됐고, runtime/filter/export 에서 경계 회귀를 계속 막아야 하는 상태다.

## Security Boundary Objects

경계 객체는 아래 네 층으로 본다.

### 1. Pack Or Bundle

- `tenant_id`
- `workspace_id`
- `pack_id`
- `pack_version`
- `bundle_scope`

### 2. Source, Section, Chunk

- `source_id`
- `parent_pack_id`
- `review_status`
- `classification`
- `access_groups`

### 3. Runtime Answer Context

- `active_tenant_id`
- `active_workspace_id`
- `active_pack_id`
- `resolved_access_groups`
- `approval_snapshot`

### 4. Provider Egress And Debug

- `provider_egress_policy`
- `egress_decision`
- `answer_boundary_ok`

## Required Security Fields

### Pack Or Bundle Level

| field | allowed values | purpose |
|---|---|---|
| `tenant_id` | non-empty string | tenant 경계 |
| `workspace_id` | non-empty string | workspace 경계 |
| `pack_id` | non-empty string | pack 단위 식별 |
| `pack_version` | non-empty string | pack 버전 경계 |
| `bundle_scope` | `official | private | mixed` | 출처 범위 |
| `classification` | `public | internal | restricted | high_risk` | 보안 등급 |
| `access_groups` | string list | 접근 허용 그룹 |
| `provider_egress_policy` | `unspecified | local_only | approved_remote` | 외부 provider 전달 가능성 |
| `approval_state` | `unreviewed | needs_review | approved | rejected` | 승인 상태 |
| `publication_state` | `candidate | published | restricted | blocked` | runtime 출판 상태 |

### Source, Section, Chunk Level

| field | purpose |
|---|---|
| `source_id` | 원문 식별 |
| `parent_pack_id` | pack 연결 |
| `source_type` | 출처 타입 |
| `review_status` | 검토 상태 |
| `updated_at` | 변경 시점 |
| `redaction_state` | `not_required | raw | redacted | blocked` |
| `citation_eligible` | citation 허용 여부 |
| `citation_block_reason` | citation 금지 이유 |

### Runtime And Answer Level

| field | purpose |
|---|---|
| `active_tenant_id` | 현재 tenant 경계 |
| `active_workspace_id` | 현재 workspace 경계 |
| `active_pack_id` | 현재 pack 경계 |
| `resolved_access_groups` | 실제 허용 그룹 |
| `egress_decision` | 로컬/원격 호출 판단 |
| `approval_snapshot` | 답변 시점 승인 스냅샷 |
| `answer_boundary_ok` | answer 경계 통과 여부 |

## Default-Deny Access Rules

기본 정책은 `default deny` 다.

아래 중 하나라도 비면 `retrieve`, `view`, `cite`, `publish` 를 모두 금지한다.

- `tenant_id`
- `workspace_id`
- `pack_id`
- `classification`
- `access_groups`

추가 규칙:

- retrieval 은 항상 `tenant_id + workspace_id + pack_version` 필터를 먼저 건 뒤에만 실행한다.
- `unreviewed` 또는 `rejected` 자산은 viewer 와 answer citation 에 노출 금지다.
- `mixed` bundle 은 허용하되, answer 에서 `official` 과 `private` 출처 표기를 분리해야 한다.
- cross-tenant, cross-workspace citation 은 즉시 fail 이다.

## Approval And Publication Rules

승격 규칙은 아래로 고정한다.

- `official` 은 `approved + citation_eligible` 면 `published` 가능
- `private` 와 `mixed` 는 human approval 전에는 `candidate` 까지만 허용
- `restricted` 와 `high_risk` 는 human approval 없이는 `published` 금지
- `rejected` 자산은 `publication_state = blocked` 로 본다
- `redaction_state = raw` 인 private 자산은 remote provider 전송 금지, `published` 승격 금지
- `unreviewed asset` 은 answer, viewer, publication 어디에도 고객-facing 상태로 노출 금지

## Provider Egress Rules

기본값은 `provider_egress_policy = unspecified` 다.

허용 규칙:

- `unspecified` 는 remote 호출 승인 상태가 아님을 뜻한다.
- remote LLM/embedding 호출은 `approved_remote` 인 pack 만 허용
- `local_only` 는 로컬 provider 로만 호출 가능함을 뜻한다.
- `restricted` 또는 `high_risk` 는 remote egress 금지
- egress 판단 결과는 `egress_decision` 으로 남긴다.

금지 규칙:

- 정책 없이 remote provider 호출
- `raw` private payload 전체를 원격 provider 로 전달
- debug/session/chat log 에 private 원문 전체 저장

## Session, Debug, And Audit Minimums

현재 truth 는 `filesystem snapshot + chat turn audit envelope` 이다. 따라서 이 문서는 아래를 minimum 으로 고정한다.

- debug/session payload 는 `source_id`, `pack_id`, `anchor/citation id` 중심으로 남긴다.
- private 원문 전체와 raw OCR text 를 debug payload 에 그대로 남기지 않는다.
- `persisted_session`, `audit_trail`, `replayable turn history` 는 확보됐다고 해도, workspace 경계와 private raw text minimization 이 깨지면 enterprise full-sale readiness 주장 금지다.
- debug endpoint 는 workspace 경계 없이 session/chat log 를 보여주면 안 된다.

## Stop Conditions

아래 중 하나라도 발생하면 이 계약은 실패다.

1. cross-tenant 또는 cross-workspace citation 이 1건이라도 나오는 경우
2. `unreviewed asset` 이 answer, viewer, debug payload 에 노출되는 경우
3. `provider_egress_policy = unspecified` 인데도 remote provider 호출이 가능한 경우
4. `restricted` 또는 `high_risk` 자산이 human approval 없이 `published` 나 citation 으로 올라오는 경우
5. `pack/version boundary` 가 흐려지는 경우
6. session persistence / audit trail 이 회귀했는데 enterprise full-sale readiness 를 주장하는 경우
7. debug endpoint 가 workspace 경계 없이 session/chat log 를 보여주는 경우

## Non-Goals For P0

이 문서는 아래를 지금 요구하지 않는다.

- user-level ABAC 세분화
- 전사 zero-trust 전체 설계
- 완전한 IAM 제품 연동
- GraphDB 기반 security reasoning

지금 단계의 목표는 `tenant/workspace/pack 단위 default-deny 경계`를 계약으로 먼저 잠그는 것이다.
