# P0 Architecture Freeze Addendum

## Purpose And Authority

이 문서는 external enterprise review pack을 반영해 기존 헌장을 `enterprise-private scope`까지 보강하는 `P0 refreeze` 문서다.

참조한 review pack:

- `../play-book-studio-enterprise-review-pack/play-book-studio-enterprise-gap-report.md`
- `../play-book-studio-enterprise-review-pack/play-book-studio-enterprise-plan-v2.md`
- `../play-book-studio-enterprise-review-pack/play-book-studio-enterprise-repo-tree-v2.txt`
- `../play-book-studio-enterprise-review-pack/play-book-studio-enterprise-task-board-v2.yaml`

이 문서는 기존 헌장을 폐기하지 않는다. 다만 아래 범위에서는 이 문서가 우선한다.

- `architecture`
- `security boundary`
- `data states`
- `product surfaces`

아래 범위는 기존 buyer contract 문서가 우선한다.

- `buyer-facing promise`
- `pass/fail gate`
- `forbidden wording`

즉, `P0_ARCHITECTURE_FREEZE_ADDENDUM.md`는 시스템 헌장이고, `Q1_8_PRODUCT_CONTRACT.md`는 구매 검증표다.

## What Stays True

아래 사실은 바뀌지 않는다.

- 현재 정직한 판매 단계는 여전히 `paid_poc_candidate` 다.
- 첫 검증 pack은 여전히 `OpenShift 4.20` 이다.
- 검증 순서는 유지한다.
  - `Q1 -> Q5 -> Q2 -> Q4 -> Q3 -> Q6 -> Q7 -> Q8`
- 현재 하드 블로커도 유지된다.
  - `unsupported assertion`
  - `clarification miss`
  - `format/OCR gap`
- validated pack 출력은 `raw manual mirror` 가 아니라 `manual book + derived playable books` 여야 한다.

즉, 이번 refreeze는 판매 단계를 올리는 문서가 아니라, enterprise 완성도에 필요한 축을 기존 헌장에 추가하는 문서다.

## Immediate Adoption Decisions

### 1. Document Intelligence Contract

기존 `bronze -> silver -> gold`만으로는 private PDF 와 scanned document 를 다루기에 부족하다.

정식 data state는 아래로 보강한다.

`bronze_raw -> bronze_parsed -> silver_structured -> candidate -> gold -> gold_restricted -> gold_degraded -> archived`

여기서 `bronze_parsed`는 필수다. 이 계층은 최소 아래 정보를 보존해야 한다.

- `page text`
- `ocr output`
- `layout blocks`
- `bbox or page-region trace`
- `tables and figures refs`
- `parser_version`
- `extraction_confidence`
- `page assets`

또한 `parser routing`, `OCR fallback`, `review queue`는 선택 기능이 아니라 입력 제련 계약으로 취급한다.

### 2. Security Boundary Contract

private-doc enterprise scope에서는 provenance만으로 부족하다. 아래 보안 경계를 정식 계약으로 추가한다.

- `tenant_id`
- `workspace_id`
- `classification`
- `access_group`
- `redaction_state`
- `provider_egress_policy`

기본 정책은 `default deny` 다. private document 는 retrieval, viewer, answer 어디에서도 workspace 경계를 넘겨 노출되면 안 된다.

`restricted` 또는 `high-risk` 등급 자산은 human approval 없이는 gold publication 으로 승격하지 않는다.

### 3. Product Surface Contract

제품 표면은 아래 3면 구조로 다시 정의한다.

- `Marketing Website`
- `Playbook Workspace`
- `Data Automation Factory`

세 면은 서로 다른 역할을 갖지만, 하나의 `Knowledge Refinery Runtime` 을 공유한다.

이 판단은 `지금 즉시 세 개의 독립 앱으로 쪼갠다`는 뜻이 아니다. 현재 표면을 이 3개 역할로 재정렬하는 것이 먼저다.
현재 `Playbook Workspace` 는 별도 제품이 아니라 단일 앱 내부의 `derived playbook viewing / publication surface` 로 본다.

### 3A. Playbook Asset Contract

`Playbook Workspace` 의 기본 자산은 아래 두 계층이다.

- `Manual Book`
  - 원문 매뉴얼을 canonical section / provenance / quality metadata 와 함께 다시 묶은 책
- `Derived Playbook Family`
  - `Topic Playbook`
  - `Operation Playbook`
  - `Troubleshooting Playbook`
  - `Policy Overlay Book`
  - `Synthesized Playbook`

raw 문서 수는 playable asset 수의 상한이 아니라 하한이다. 하나의 매뉴얼에서 여러 운영 과업과 기술 주제가 파생되면 파생 북 수가 원문 수를 넘는 것이 정상이다.

`Derived Playbook Family` 는 `개요 링크 + 요약` 이 아니라 최소 `사전조건 -> 절차 -> 코드 -> 검증 -> 실패 신호 -> source trace` 를 가진 실행형 자산이어야 한다.

### 4. Gold Grade Policy V2

gold는 더 이상 내용 품질만을 뜻하지 않는다. 아래 bundle truth를 도입한다.

- `official`
- `private`
- `mixed`

특히 `private` 와 `mixed` bundle 에는 기존 gold 기준 외에 아래 gate 를 추가한다.

- `ACL coverage = 100%`
- `classification coverage = 100%`
- `page parse success >= 98%`
- `page-to-section trace >= 99%`
- `manualbook render success >= 99%`
- `topic playbook render success >= 99%`
- `PII/secret scan pass`
- `restricted/high-risk asset requires human approval`

즉 gold는 `content quality + provenance + security + publication readiness` 를 모두 포함한다.

## Conditional Adoption Decision

`Knowledge Graph Plane` 은 now-or-never 항목이 아니다. 하지만 enterprise 단계에서 재검토가 반드시 필요한 축으로 올린다.

현재 정의는 아래와 같다.

- `Qdrant` 는 1차 recall 과 filter-aware retrieval 을 맡는다.
- `Graph sidecar` 는 유사 문서 검증, relation-aware retrieval, provenance traversal, playbook branching 을 맡는다.

그래프는 `Qdrant 대체`가 아니다. 또한 day-1 필수 구현도 아니다.
trigger 를 닫기 전까지 `Graph sidecar` 는 현재 런타임 의존성이 아니라 `architecture reference only` 다.

아래 조건이 확인될 때만 정식 구현 task 로 승격한다.

- `Q1`
- `Q5`
- `Q2`
- `Q3`
- `Q6`

를 닫은 뒤에도 `유사 문서 검증`, `relation-aware retrieval`, `provenance traversal` 이 남은 병목으로 확인될 것.

## Explicit Non-Adoption Now

아래는 지금 채택하지 않는다.

- `Qdrant + GraphDB + PostgreSQL + Object Storage` 전면 재플랫폼
- `15 minute sync` 같은 near-real-time 반영 약속
- `모든 파일 형식을 즉시 지원`한다는 선언
- `Marketing Website`, `Playbook Workspace`, `Data Automation Factory` 를 즉시 독립 앱 3개로 분리하는 리팩터

## Impact On Existing Contracts

- `Q1_8_PRODUCT_CONTRACT.md`
  - buyer 질문 8개를 이 헌장 기준으로 검증하는 pass/fail 계약표 역할만 유지한다.
- `OWNER_SCENARIO_SCORECARD.yaml`
  - owner-demo 와 full-sale gate 는 그대로 유지한다.
- `CUSTOMER_POC_BUYER_PACKET.md`
  - 이후 `format support matrix`, `OCR routing policy`, `self-service rebuild scope` 와 정렬돼야 한다.
- `TASK_BOARD.yaml`
  - 새 phase 는 추가하지 않고, 기존 `P0-E2`, `P2-E1`, `P4-E1`에 최소 task 만 추가한다.

## Stop Conditions

아래 중 하나라도 발생하면 이 addendum 은 실패다.

1. `paid_poc_candidate` truth 를 흐리거나, 기존 `Q1 -> Q5 -> Q2 -> Q4 -> Q3 -> Q6 -> Q7 -> Q8` 검증 순서를 바꾸는 경우
2. `bronze_parsed`, page provenance, parser routing, OCR review queue 중 하나라도 빠진 채 `다양한 문서 지원` 같은 문구로 뭉개는 경우
3. `tenant/workspace/classification/access_group/provider egress` 를 명시하지 않는 경우
4. `official/private/mixed` bundle truth 와 private-doc extra gate 없이 기존 gold 기준만 반복하는 경우
5. graph를 `day-1 필수 코어`로 과장하거나, 반대로 `완전히 불필요`하다고 고정하거나, `유사 문서 검증` 병목을 증거 없이 무시하는 경우

## Root Document Linkage

루트 문서와 보드는 이 문서를 아래 문구로 연결한다.

`P0_ARCHITECTURE_FREEZE_ADDENDUM.md` - external enterprise review를 반영해 parsed-artifact, security-boundary, product-surface, Gold-grade v2, graph-sidecar 조건을 기존 헌장 위에 덧씌우는 P0 보강 기준 문서.

external review pack 자체는 참조 근거이며, 이 addendum이 저장소 내부의 공식 기준 문서다.
