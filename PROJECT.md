# Project

## Product Charter

Play Book Studio는 `기업 문서를 검증 가능한 플레이북으로 전환하는 플랫폼`이다.

- 현재 정직한 판매 단계는 `paid_poc_candidate` 다.
- 현재 첫 검증 pack은 `OpenShift 4.20` 이다.
- 제품 본체는 `문서-플레이북 플랫폼`이고, OCP는 첫 검증 pack 이다.

## Product Output Shape

검증 pack 의 출력은 `원문 매뉴얼 미러`로 끝나지 않는다.

- 기본 자산은 `Manual Book` 이다.
- 제품 자산은 여기에 더해 `Topic Playbook`, `Operation Playbook`, `Troubleshooting Playbook`, `Policy Overlay Book`, `Synthesized Playbook` 을 포함한다.
- raw 문서 수는 playable asset 수의 상한이 아니라 하한이다. 운영 질문과 기술 주제가 분화되면 파생 북 수가 원문 수를 넘는 것이 정상이다.
- 플레이북은 `요약 링크`가 아니라 `사전조건 -> 절차 -> 코드 -> 검증 -> 실패 신호 -> source trace` 를 가진 실행형 책이어야 한다.

## Rule Ownership

현재 프로젝트의 규칙 소유권은 아래로 고정한다.

- `AGENTS.md`
  - 작업 방식과 판단 규칙
- `PROJECT.md`
  - 문서 우선순위와 규칙 소유권
- `Q1_8_PRODUCT_CONTRACT.md`
  - buyer promise, non-promise, promotion prerequisite
- `OWNER_SCENARIO_SCORECARD.yaml`
  - demo / full-sale 수치 게이트
- `P0_ARCHITECTURE_FREEZE_ADDENDUM.md`
  - architecture, security, data-state, product-surface 우선 문서
- `PARSED_ARTIFACT_CONTRACT.md`
  - parsed lineage 운영 계약
- `SECURITY_BOUNDARY_CONTRACT.md`
  - private-doc security 운영 계약
- `TASK_BOARD.yaml`
  - 실행 상태와 작업 순서

## Precedence

문서가 충돌하면 아래 순서를 따른다.

1. `AGENTS.md`
   - 작업 방식에만 적용한다.
2. `P0_ARCHITECTURE_FREEZE_ADDENDUM.md`
   - `architecture`, `security`, `data-state`, `product-surface`
3. `PARSED_ARTIFACT_CONTRACT.md` / `SECURITY_BOUNDARY_CONTRACT.md`
   - intake 와 enterprise-private 운영 계약
4. `Q1_8_PRODUCT_CONTRACT.md` / `OWNER_SCENARIO_SCORECARD.yaml`
   - `buyer promise`, `pass/fail`, `forbidden wording`, `release gate`
5. `TASK_BOARD.yaml`
   - 현재 실행 상태와 선후관계

`README.md` 와 `FILE_ROLE_GUIDE.md` 는 규칙 소유 문서가 아니다.

## Source Authority

Q2와 buyer-facing citation 판단에 쓰는 권위 계층은 아래로 고정한다.

1. `Vendor Official Source`
2. `Reviewed Translation`
3. `Verified Operational Evidence`
4. `Playbook Synthesis`
5. `Model Prose`

하위 tier 는 상위 tier 를 보강할 수는 있어도 뒤집을 수 없다.

## Reference Documents

아래 문서는 제품 정의에 중요하지만 `active rule owner` 는 아니다.

- `README.md`
- `FILE_ROLE_GUIDE.md`
- `CODEX_OPERATING_CHARTER.md`
- `OWNER_VALUE_CASE.md`
- `BEACHHEAD_ICP_AND_TRIGGER.md`
- `CUSTOMER_POC_BUYER_PACKET.md`

이 문서들은 active rule set 을 설명하거나 보조할 수는 있어도, 우선권을 갖지 않는다.

## Drift Ban

아래 상태는 금지한다.

- `README.md` 나 `FILE_ROLE_GUIDE.md` 가 규칙을 다시 소유하는 상태
- `TASK_BOARD.yaml` 상태가 실제 생성된 산출물과 어긋나는 상태
- `archive/INDEX.md` 의 active/reference 분류가 루트 문서와 어긋나는 상태
