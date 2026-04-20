---
status: reference
doc_type: lane-plan
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# User Upload Repair Promotion Plan v1

이 문서는 PBS의 `user upload lane`을 어떻게 다룰지 정의한다.

핵심 질문은 하나다.

`품질이 들쭉날쭉한 업로드 문서를 어떻게 수리하고, 언제 Playbook으로 승격할 것인가`

## 1. 왜 이 계획이 먼저 필요한가

PBS가 궁극적으로 `LLM Wiki`식 지식 누적을 하려면,
먼저 들어오는 source를 제대로 읽고, 구조를 복원하고, 수리하고,
경계(boundary)를 지키면서 truth layer에 올릴 수 있어야 한다.

즉 user lane에서 아래가 먼저 서야 한다.

- data fidelity
- structure fidelity
- repair discipline
- promotion discipline

이게 약하면 위에 아무리 좋은 knowledge accumulation을 얹어도
`누적되는 건 지식`이 아니라 `누적되는 오염`이 된다.

## 2. 기본 원칙

### 2.1 업로드 직후 자동 Playbook 승격 금지

user upload는 official lane과 다르다.

기본 상태는 아래 둘 중 하나다.

- `draft`
- `review`

즉 업로드 직후 polished Playbook처럼 보이게 과장하지 않는다.

### 2.2 수리 없는 승격 금지

특히 PDF/image 계열은 `flattened structured block`이나
layout loss가 흔하므로 repair를 거쳐야 한다.

### 2.3 수리 결과도 provenance를 잃으면 안 된다

repair는 구조를 복구하는 것이지,
출처 없는 새 문서를 창작하는 것이 아니다.

### 2.4 user lane는 “editable draft”에서 시작한다

user lane의 honest contract는 아래다.

`자동 초안 생성 -> 수리 -> 사용자 보정 -> 승격`

## 3. 현재 PBS가 이미 확인한 실제 gap

현재 user upload lane에서 확인된 실제 문제는 아래다.

- `structured_blocks_flattened`
- code/table/procedure가 paragraph에 눌리는 현상
- quality score가 실제보다 높게 나올 수 있는 현상
- remote OCR을 무조건 태울 수 없는 boundary 제약
- source fidelity가 약한 상태에서 corpus로 너무 빨리 퍼질 위험

즉 지금 user lane의 우선순위는:

- 보기 좋게 만드는 것보다
- `잘못 좋은 것으로 착각하지 않기`

가 먼저다.

## 4. Target Lane

user upload lane의 목표 흐름은 아래로 고정한다.

`Upload -> Capture -> Normalize -> Detect -> Repair -> Review -> Refine -> Promote`

## 5. Stage-by-Stage Plan

## 5.1 Stage A: Capture

목표:

- 원문과 메타데이터를 안정적으로 수집

필수:

- original file preservation
- file kind detection
- source identity
- tenant/workspace boundary metadata
- egress policy metadata

pass 조건:

- 원본 파일이 immutable하게 보존됨
- source metadata가 빠지지 않음

## 5.2 Stage B: Normalize

목표:

- raw source를 canonical book candidate로 변환

형식별 우선 포인트:

- PDF/image: layout-aware recovery
- DOCX: heading/list/table fidelity
- PPTX: slide order, shape text, speaker note fidelity
- XLSX: sheet/table/header fidelity
- HTML: semantic section fidelity

pass 조건:

- section tree 존재
- block kind 최소 구분 존재
- source lineage seed 생성 가능

## 5.3 Stage C: Detect

목표:

- 수리 필요 여부를 정확히 판정

대표 fail 신호:

- `structured_blocks_flattened`
- heading collapse
- code/table loss
- anchor instability
- weak citation landing potential
- noise contamination

pass 조건:

- degraded 여부가 honest하게 표시됨
- good을 good으로, bad를 bad로 분류

## 5.4 Stage D: Repair

목표:

- 구조 손실을 줄이고 reader/chat 품질을 회복

repair 전략:

- PDF/image:
  - layout repair
  - structured block recovery
  - trusted OCR fallback
  - repair 전/후 비교
- DOCX/PPTX/XLSX:
  - structure-first repair
  - heading/list/table/speaker note recovery

중요:

- OCR은 만능이 아님
- 형식별로 다른 repair strategy가 필요함

pass 조건:

- flattened block 감소
- code/table/procedure fidelity 개선
- source lineage 유지

## 5.5 Stage E: Review

목표:

- repair 후 결과를 gate 기준으로 평가

평가 축:

- parse-grade
- reader-grade
- brand-grade
- chat-grade

판정 결과:

- `draft 유지`
- `review-ready`
- `viewer-only ready`
- `promoted candidate`

## 5.6 Stage F: Refine

목표:

- 사람이 손봐야 하는 부분을 명시적으로 보정

예:

- section title 보정
- misplaced code/table 정리
- summary 보강
- note/caution 추가
- user annotation/overlay 저장

pass 조건:

- refinement가 source lineage를 훼손하지 않음
- 수정 흔적이 draft truth와 promoted truth를 섞지 않음

## 5.7 Stage G: Promote

목표:

- 조건을 통과한 산출물만 Playbook 또는 corpus truth로 승격

가능한 promotion:

- `viewer-only promotion`
- `viewer + corpus promotion`
- `workspace draft only`

기본 규칙:

- parse fail -> promotion 금지
- reader fail -> Playbook promotion 금지
- chat fail -> corpus promotion 금지
- boundary fail -> quarantine 또는 draft 유지

## 6. Promotion Matrix for User Lane

### Case 1

- parse: pass
- reader: fail
- chat: fail

결과:

- `draft`

### Case 2

- parse: pass
- reader: pass
- chat: fail

결과:

- `viewer-only ready`

### Case 3

- parse: pass
- reader: pass
- brand: fail

결과:

- `review-ready`

### Case 4

- parse: pass
- reader: pass
- brand: pass
- chat: pass
- boundary: pass

결과:

- `promoted playbook/corpus candidate`

## 7. Boundary Rules

user lane는 security contract를 더 엄격히 본다.

특히 아래는 승격 전에 반드시 확인해야 한다.

- provider egress policy
- redaction state
- approval state
- tenant/workspace identity
- official/private bridge contamination

원칙:

- boundary fail은 quality score로 덮지 않는다
- quality가 좋아도 boundary fail이면 promoted 금지

## 8. Human-in-the-Loop Rules

user lane에서 사람 역할은 선택이 아니라 구조적 단계다.

필요 포인트:

- ambiguous title/section review
- code/table fidelity review
- promotion approval
- optional manual refinement

즉 user lane는 `full auto magic`보다
`strong auto draft + strong repair + disciplined promotion`이 맞다.

## 9. Acceptance Criteria

이 계획이 성공했다고 보려면 아래가 가능해야 한다.

1. 품질 낮은 upload가 good/100으로 잘못 승격되지 않는다
2. repaired output이 unrepaired output보다 분명히 좋아졌음을 evidence로 설명할 수 있다
3. draft truth와 promoted truth가 섞이지 않는다
4. user lane 문서도 조건을 통과하면 Playbook 승격이 가능하다
5. corpus promotion은 chat-grade 통과본만 대상으로 한다

## 10. Immediate Packet Order

user lane에서 바로 들어가야 할 packet 순서는 아래다.

1. degraded detection hardening
2. format-aware repair strengthening
3. repair before/after evaluation harness
4. refinement surface discipline
5. promotion gate enforcement
6. viewer/corpus split promotion

## 11. Non-Goals

- user upload를 official lane처럼 즉시 polished book으로 보이게 포장하지 않는다
- repair가 안 된 산출물을 corpus에 서둘러 넣지 않는다
- boundary를 무시한 remote OCR 자동화를 허용하지 않는다

## 12. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`이 업로드 문서는 그냥 파싱된 초안이 아니라, 수리와 검토를 거쳐 PBS가 책임질 수 있는 수준으로 승격되었는가`
