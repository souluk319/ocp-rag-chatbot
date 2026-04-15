# Security Boundary Contract

## Purpose

이 문서는 customer/private 문서가 `customer_source_first_pack` lane 으로 technical wiki runtime 에 들어올 때의 보안 경계를 고정한다.

핵심은 하나다.

`customer pack 은 official runtime 과 연결될 수 있지만, tenant/workspace/pack 경계는 절대 잃지 않는다.`

## Required Security Envelope

모든 private 또는 mixed 자산은 아래 필드를 가진다.

- `tenant_id`
- `workspace_id`
- `pack_id`
- `pack_version`
- `classification`
- `access_groups`
- `provider_egress_policy`
- `approval_state`
- `publication_state`
- `redaction_state`

## Boundary Rules

1. retrieval 은 항상 `tenant_id + workspace_id + pack_version` 경계 안에서만 실행한다.
2. `viewer_path`, `chat citation`, `related navigation` 은 같은 pack 또는 허용된 official bridge 만 가리킨다.
3. `unreviewed` 자산은 runtime surface 에 오르지 않는다.
4. `restricted` 와 `high_risk` 는 human approval 이후에만 published 로 이동한다.
5. `redaction_state = raw` 인 private 자산은 remote provider egress 를 열지 않는다.

## Official Bridge Rules

customer pack 은 official runtime 과 아래 방식으로만 연결된다.

- official entity hub 참조
- official book 참조
- official section 참조

bridge 응답은 아래 truth 를 유지한다.

- `official`
- `private`
- `mixed`

즉 boundary label 없이 official surface 에 private text 를 섞지 않는다.

## Product Surface Rules

1. Control Tower 는 pack boundary, approval, publication 상태를 보여준다.
2. Viewer 는 현재 문서가 속한 pack truth 를 표시할 수 있어야 한다.
3. Chat answer 는 official / private / mixed 출처를 숨기지 않는다.

## Audit Rules

1. session 과 audit trail 은 boundary 안에서 유지한다.
2. debug payload 는 private 원문 전체 dump 대신 trace 와 metadata 를 남긴다.
3. source trace 는 유지하되 cross-pack raw dump 는 만들지 않는다.

## Promotion Gate

customer pack runtime publication 은 아래가 모두 맞을 때만 열린다.

- security envelope complete
- approval state present
- publication state present
- pack identity present
- egress policy present

## Hard Fail

아래는 즉시 fail 이다.

1. cross-tenant citation
2. cross-workspace exposure
3. unreviewed asset exposure
4. unspecified egress 로 remote provider 호출
5. restricted or high_risk published without approval
