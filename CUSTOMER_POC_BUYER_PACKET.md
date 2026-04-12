# CUSTOMER_POC_BUYER_PACKET

## Current Judgment

이 문서는 `고객 문서 PoC`를 어떻게 팔고, 무엇을 납품하고, 어디까지를 약속하지 않을지 정의한다.

현재 정직한 계약 범위는 `유료 PoC 또는 파일럿`이다. 아래 조건을 충족하기 전에는 `전사 본판매`로 말하지 않는다.

- owner demo scorecard 통과
- persisted session 과 audit trail 확보
- 고객 문서 1종 이상의 승인 가능한 참조 사례 확보

## What The Customer Is Buying

고객이 PoC 에서 사는 것은 아래다.

1. 고객 문서 1종 이상을 pack 과 playbook 구조로 바꾸는 작업
2. 대표 시연 질문에 대한 근거 기반 runtime 검증
3. 향후 rollout 가능성을 판단하는 scorecard 와 readout

즉, 단순 데모가 아니라 `고객 문서가 실제 운영 자산으로 바뀌는지 검증하는 계약`이다.

## Required Customer Inputs

PoC 시작 전에 고객이 반드시 제공해야 하는 것은 아래다.

- 문서 범위 1~3종
- 문서 소유자와 리뷰 승인자
- owner-demo 질문 5~10개
- 버전 범위와 금지 범위
- 법무/보안상 사용 가능한 문서 목록

이 중 하나라도 비어 있으면 PoC 시작 조건이 아니다.

## Our 10-Business-Day PoC Shape

### Day 0

- kickoff
- success question 확정
- 문서 범위와 승인자 확정

### Day 1-2

- intake
- 문서 구조 파악
- source / version / ownership 확인

### Day 3-5

- normalization
- playbook draft 생성
- 검증용 runtime 경로 연결

### Day 6-7

- owner-demo 질문셋 실행
- hard miss, unsupported assertion, clarification miss 확인

### Day 8-9

- 보수성, 근거, scope wording 수정
- readout 초안 준비

### Day 10

- buyer readout
- scorecard 결과 공유
- rollout 전환 여부 판단

## PoC Deliverables

PoC 종료 시 납품물은 아래다.

- 고객 문서 기반 pack 초안
- 사람이 읽는 playbook 초안
- owner-demo 결과 요약
- scorecard pass/fail 결과
- 다음 단계 권고

## Acceptance Criteria

PoC 는 아래가 충족될 때만 `성공`으로 본다.

- 고객 문서에서 승인 가능한 corpus 초안이 나온다
- 대표 질문셋에서 하드미스가 없다
- 애매한 질문에서 임의 단정이 없다
- 답변과 원문 근거가 클릭 가능한 형태로 이어진다
- 고객이 다음 확장 pack 범위를 상상할 수 있다

## Stop Conditions

아래 중 하나라도 발생하면 PoC readout 에서 `본판매 전환 불가`로 기록한다.

- 문서 소유자와 승인자가 끝까지 비어 있다
- owner-demo 질문셋에서 하드미스가 난다
- 고객 문서가 review 가능한 자산으로 정리되지 않는다
- pack 경계와 버전 경계가 흐려진다
- unsupported assertion 이 남는다

## Explicit Non-Promises

현재 단계에서 아래는 약속하지 않는다.

- 범용 문서 플랫폼 본판매
- 전사 배포 완료형 제품
- 장기 SLA
- enterprise SSO/감사 체계가 완결된 운영 배포
- 고객 문서 없이도 같은 품질을 보장한다는 주장

## Rollout Conversion Rule

PoC 이후 `본판매 검토`로 올릴 수 있는 조건은 아래다.

1. `OWNER_SCENARIO_SCORECARD.yaml` 의 full-sale 조건 충족
2. 고객 문서 PoC 성공 사례 1건 이상 확보
3. 운영 통제, 세션 영속성, 감사 추적 문서화
4. 확장 pack 계획이 buyer readout 에서 합의됨

## Commercial Truth

지금 이 제품은 `될 수도 있는 플랫폼`을 파는 단계가 아니다.

지금 파는 것은 오직 하나다.

`고객 문서를 넣었을 때 이 팀이 정말로 돈 낼 만한 enterprise playbook runtime 이 되는지 확인하는 유료 PoC`
