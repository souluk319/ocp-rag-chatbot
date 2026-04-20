---
status: reference
doc_type: execution-plan
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# Implementation Packet Order v1

이 문서는 현재 PBS 상태에서 궁극 목표까지 가기 위한 실행 순서를 고정한다.

궁극 목표:

`공식/사설 source를 누적 지식으로 컴파일해, reader-grade and brand-grade Playbook과 grounded chat corpus를 같은 truth에서 생산하는 PBS를 완성한다.`

## 1. 왜 순서가 중요한가

지금 PBS는 아래를 동시에 갖고 있다.

- 이미 좋은 뼈대
- 이미 동작하는 런타임
- 아직 남아 있는 품질 gap
- 아직 남아 있는 truth binding gap
- 아직 남아 있는 성능 gap

그래서 순서를 잘못 잡으면 아래가 생긴다.

- 예쁜 표면 위에 약한 truth
- 빠른 답변 위에 약한 provenance
- 누적 지식 위에 오염된 source

즉 순서는 `보기 좋게`보다 `제대로 가져오기`가 먼저다.

## 2. Packet Order

## Packet 1: User Upload Repair Promotion

목표:

- user lane 품질과 승격 discipline 먼저 확립

완료 조건:

- degraded detection 강화
- repair lane 강화
- viewer/corpus split promotion 가능
- user lane draft/promoted 구분 명확

왜 먼저:

- 데이터를 제대로 못 가져오면 위키도 못 만들고 책도 못 만든다

## Packet 2: Runtime Truth Binding Implementation

목표:

- knowledge object, viewer, corpus, chat, citation, manifest가 같은 truth를 쓰게 실제 배선

완료 조건:

- viewer/chat drift 완화
- citation binding 강화
- chunk lineage 강화

왜 지금:

- repair된 결과가 제대로 퍼지려면 same-truth binding이 뒤따라야 함

## Packet 3: Official Lane Playbook Standardization

목표:

- official source-first lane을 PBS gold standard로 먼저 완성

완료 조건:

- 대표 OCP 책들이 reader/brand/chat grade 동시 통과

왜 여기:

- 가장 안정적인 source lane을 먼저 완성해야 나머지 품질 기준선이 흔들리지 않음

## Packet 4: Playbook Composer Implementation

목표:

- plan/spec/composer contract를 실제 renderer/composer 계층으로 구현

완료 조건:

- knowledge object 기반 chapter/page assembly
- source rail and related plays 일관화
- procedure/code/table fidelity 향상

## Packet 5: LLM Wiki Accumulation Core

목표:

- 새 source가 기존 playbook/world model을 갱신하는 누적 원리 구현

완료 조건:

- enrich/revise/contradict/supersede 동작
- existing playbook partial recomposition

왜 나중:

- 앞단의 source fidelity, promotion discipline, runtime truth binding이 먼저여야 누적이 의미 있음

## Packet 6: Chat-to-Wiki Feedback

목표:

- 좋은 질의응답을 derived operator note / play draft로 다시 축적

완료 조건:

- validated answer filing
- note lineage 유지

## Packet 7: Runtime Performance Hardening

목표:

- 같은 truth 구조를 유지한 채 체감 속도 개선

우선순위:

- bootstrap slimming
- startup warm-up
- chat post-processing slimming
- data-control-room precompute/cache
- pipeline/chat resource isolation

## Packet 8: Release Validation Packet

목표:

- README, harness, demo, quality evidence, timing evidence를 한 묶음으로 닫기

## 3. Successive Validation

각 packet은 아래 순서로 닫는다.

1. contract/spec update if needed
2. minimal implementation
3. local focused validation
4. representative evidence
5. packet closeout

## 4. Guardrails

- repair 없는 accumulation 금지
- same-truth binding 없는 renderer 미화 금지
- provenance 약화시키는 성능 최적화 금지
- official/private boundary 혼합 금지

## 5. Overload Response Rule

구현 중 특정 단계가 `품질 대비 시간/자원 소모`가 과하면
그 단계를 무조건 내부에 붙들어 두지 않는다.

판단 옵션은 아래 셋이다.

1. `계속 내부 유지`
   - 현재 툴이 품질과 속도 모두 허용 범위일 때

2. `더 맞는 툴로 교체`
   - 같은 역할을 더 정확하거나 더 가볍게 수행하는 오픈소스 대체재가 있을 때

3. `외부 고성능 리소스로 분리`
   - 로컬 병목이 크고, truth/provenance/boundary를 지키면서 외부화할 수 있을 때

원칙:

- tool swap 또는 externalization은 `진실 소스`를 바꾸는 행위가 아니라
  `비싼 처리 단계의 실행 위치`를 바꾸는 행위여야 한다
- provenance, source lineage, boundary contract를 약화시키는 방향은 금지
- closeout에는 아래 셋 중 무엇을 선택했는지 남긴다
  - 내부 유지
  - 교체 후보
  - 외부화 후보

## 6. One-Line Execution Rule

`앞단 truth를 먼저 단단히 하고, 그 위에 지식 누적과 브랜드 출판을 쌓는다.`
