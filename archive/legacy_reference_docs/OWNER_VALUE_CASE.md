# OWNER_VALUE_CASE

> Legacy reference only. 현재 기준선이 아니며, buyer-facing 현재 truth 는 루트 active rule set 과 scorecard 를 우선한다.

## Current Judgment

현재 이 제품의 정직한 판매 단계는 `본판매`가 아니라 `유료 PoC 후보`다.

확인된 사실은 아래 세 가지다.

- 최신 runtime answer eval 은 현재 질문셋에서 `pass_rate = 1.0`, `clarification_needed_but_answered_rate = 0.0`, `no_evidence_but_asserted_rate = 0.0` 까지 올라왔다.
- 첫 검증 pack 은 `OpenShift 4.20` 이고, 비-OCP 고객 문서에 대한 실증은 아직 없다.
- 세션 영속성, 감사 추적, 운영 배포 책임 경계는 아직 기업 도입 문서로 닫히지 않았다.

따라서 지금 오너에게 팔 수 있는 것은 `완성된 범용 플랫폼`이 아니라, `고객 문서를 운영 플레이북 자산으로 바꿀 수 있는지 검증하는 유료 PoC`다.

## What The Buyer Actually Buys

오너가 사는 것은 아래 네 가지다.

1. 사람 머릿속 운영 지식을 문서 자산으로 옮기는 구조
2. 질문 답변과 원문 근거를 한 화면에서 검증하는 운영 표면
3. 고객 문서를 pack 과 playbook 으로 재사용 가능하게 만드는 체계
4. 향후 다른 제품군과 고객 계정으로 확장 가능한 문서 운영 기반

## Confirmed Facts

### 1. 확인된 강점

- OCP 검증 pack 에서는 검색 hit 가 높다.
- 메인 표면은 채팅, 원문 뷰어, 상황실로 연결되어 있다.
- 루트 지침은 구매자 언어, provenance, review gate 를 우선하도록 정리됐다.

### 2. 확인된 약점

- 최신 answer eval green 하나만으로는 full-sale gate 를 닫지 못한다.
- 비-OCP 고객 문서에 대한 승인 가능한 reference case 는 아직 없다.
- 세션 영속화와 replayable audit trail 은 들어갔지만, 운영 유지보수/고객 확장 gate 는 아직 미완료다.

## Value Hypothesis

아래는 현재 `검증 전 가설`이다. 사실로 포장하지 않는다.

이 제품이 가장 큰 가치를 내는 조직은 다음 조건을 가진다.

- 벤더 문서, 내부 runbook, 장애 회고가 흩어져 있다.
- 반복 문의와 반복 장애 대응이 senior 인력에게 몰린다.
- 새 인력 온보딩과 교대 인수인계가 느리다.
- 감사, 승인, 고객 대응에서 답변 근거를 요구받는다.

이 조직에서 가치가 발생하는 경로는 아래다.

1. 문서 탐색 시간을 줄인다.
2. senior 인력 의존도를 낮춘다.
3. 반복 대응을 플레이북으로 표준화한다.
4. 고객 대응과 운영 판단의 근거를 남긴다.

## Economic Model

아래 수치는 `첫 구매 가설`을 위한 운영 기준선이다. 고객 데이터로 대체하기 전까지는 내부 목표치로만 쓴다.

### Target Organization

- 플랫폼/운영/기술지원 인력 `10~30명`
- 월간 문서 의존 문의/장애/변경 판단 `80~300건`
- 핵심 운영 지식이 특정 senior `3~5명`에게 집중

### Buyer-Visible Improvement Threshold

오너가 돈을 낼 최소 조건은 아래다.

- `time-to-first-approved-corpus <= 10 business days`
- `owner-critical scenario pass rate >= 90%`
- `evidence-linked answer rate >= 95%`
- `unsupported assertion rate = 0` on owner demo set
- 반복 질문의 최초 탐색 시간 `30%+` 단축
- 신규 인력 온보딩용 기준 플레이북 준비 시간 `40%+` 단축

## Why This Can Become Worth Buying

아래 세 가지가 동시에 성립할 때만 결재 명분이 생긴다.

1. 고객 문서가 실제로 승인 가능한 pack 과 playbook 으로 바뀐다.
2. 대표 시연 질문에서 틀리거나 과장하지 않는다.
3. PoC 결과가 다음 조직과 다음 문서군으로 재사용 가능하다.

## What Does Not Count As Value

아래는 오너 가치로 인정하지 않는다.

- 답변 문장만 그럴듯해진 것
- OCP 문서량이 더 많아진 것
- 데모 랜딩이 화려해진 것
- 내부 파이프라인 용어가 더 정교해진 것
- 실전 owner-demo 셋이 아닌 내부 평가셋만 초록불인 것

## No-Buy Conditions

아래 중 하나라도 true 면 결재 문서에 올리지 않는다.

- 고객 문서 1종도 승인 가능한 corpus 로 만드는 데 실패한다.
- 대표 데모 질문에서 하드미스가 난다.
- 애매한 질문을 명확화하지 않고 단정한다.
- 세션, 감사, 운영 책임 경계가 문서로 설명되지 않는다.
- OCP 밖 확장성 주장을 실증 없이 전면에 건다.

## Immediate Product Consequence

지금 단계의 제품 정의는 아래로 제한한다.

- 파는 것: `고객 문서 PoC + enterprise playbook runtime 검증`
- 아직 안 파는 것: `범용 기업용 플랫폼 본판매`
- 다음 승격 조건: `OWNER_SCENARIO_SCORECARD.yaml` 과 `CUSTOMER_POC_BUYER_PACKET.md` 의 gate 통과
