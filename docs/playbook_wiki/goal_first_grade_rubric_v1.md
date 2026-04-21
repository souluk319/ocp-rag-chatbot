---
status: reference
doc_type: rubric
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-21
---

# Goal-First Grade Rubric v1

이 문서는 PBS가 새 고정목표를 향해 문서를 `지식 제조 시스템`으로 승급시키기 위해 필요한 평가 기준을 잠근다.

이 문서는 아래를 정의한다.

- 무엇을 `좋은 문서 승급`으로 볼 것인가
- 무엇을 `즉시 차단`할 것인가
- 무엇을 `repair 대상`으로 볼 것인가
- 무엇을 `Playbook` 또는 `Corpus`로 승격할 것인가

이 문서는 `Promotion Gate Matrix v1`을 대체하지 않는다.
역할은 그 위에 `goal-first 평가 축`, `점수 운영`, `evidence`, `fixture 기준선`을 더하는 것이다.

## 1. One-Line Verdict

아래 질문에 `yes`라고 답할 수 있어야 한다.

`이 산출물은 단지 파싱된 문서가 아니라, PBS가 책임지고 승급 여부를 판정할 수 있는 지식 제조 결과물인가`

## 2. 평가 대상

이 rubric은 아래 산출물에 적용한다.

- official source-first lane output
- user upload / customer/private lane draft
- promoted playbook candidate
- viewer-only candidate
- corpus candidate

## 3. Verdict Levels

최종 verdict는 아래 다섯 단계로 잠근다.

1. `blocked_artifact`
2. `bronze`
3. `silver`
4. `gold`
5. `promoted`

의미는 아래와 같다.

### 3.1 blocked_artifact

- 구조 붕괴, provenance 파손, boundary fail, 심각한 quality miss로 인해 등급 부여 대상이 아님
- 기본 조치: repair 또는 quarantine

### 3.2 bronze

- 기계와 운영자가 초벌 검토 가능한 수준
- viewer/corpus 승격 전 최소 repair backlog가 분명해야 함

### 3.3 silver

- reader-grade와 chat-grade의 핵심 축이 상당 부분 회복된 상태
- 내부 운영, 리뷰, 제한적 활용 가능

### 3.4 gold

- 배포 가능한 고신뢰 playbook/corpus 후보
- 증거, citation, structure, reader quality가 안정적으로 맞음

### 3.5 promoted

- lane 조건과 approval까지 통과해 실제 PBS truth/runtime에 편입된 상태
- `gold`는 품질 verdict이고 `promoted`는 운영 상태다

## 4. Scoring Axes

점수는 아래 다섯 축으로 계산한다.

| axis | weight | 질문 |
| --- | ---: | --- |
| `source_fidelity` | 25 | 원문 의미, 절차, 표, 그림, 코드, 출처를 보존했는가 |
| `structure_recovery` | 20 | section/tree/block/layout/anchor를 안정적으로 복원했는가 |
| `reader_grade` | 20 | 사람이 읽고 판단하기 쉬운 위계와 리듬이 있는가 |
| `chat_grade` | 20 | retrieval, citation, answer grounding에 안전한가 |
| `governance_grade` | 15 | provenance, boundary, review, reproducibility가 분명한가 |

총점은 100점 만점이다.

## 5. Grade Threshold

기본 임계값은 아래로 잠근다.

| grade | score threshold | 추가 조건 |
| --- | ---: | --- |
| `blocked_artifact` | fail gate triggered | 점수 무효 |
| `bronze` | 60+ | 치명적 누락 없음 |
| `silver` | 78+ | 표/그림/절차의 치명적 붕괴 없음 |
| `gold` | 90+ | citation, reader, governance 증거 모두 pass |

주의:

- 총점이 높아도 fail gate가 걸리면 `blocked_artifact`
- `gold`여도 promotion approval/boundary 미충족이면 `promoted` 아님

## 6. Fail Gates

아래는 점수와 무관하게 차단하는 fail gate다.

### 6.1 Fidelity Fail

- 원본 페이지/슬라이드 주요 부분 누락
- 코드/명령/표/그림이 의미를 잃을 정도로 붕괴
- 원문과 반대되거나 unsupported LLM prose가 삽입됨

### 6.2 Structure Fail

- heading hierarchy collapse
- section anchor drift
- figure-caption orphaning
- table header/row meaning collapse
- procedure가 paragraph dump로 눌림

### 6.3 Chat Fail

- citation landing 불가
- answer/viewer truth drift
- unsupported synthesis
- contradiction 미표시 상태의 answer risk

### 6.4 Governance Fail

- provenance chain 없음
- source lane / boundary / review state 누락
- private/customer 경계 blur
- 승인되지 않은 remote egress 또는 policy mismatch

## 7. Axis-Level Checks

### 7.1 source_fidelity

pass if:

- source trace가 block 또는 section 수준으로 이어진다
- 코드/표/그림/절차가 의미를 유지한다
- source excerpt 또는 anchor jump가 가능하다

evidence:

- source-to-block trace sample
- page/slide coverage sample
- structured block fidelity sample

### 7.2 structure_recovery

pass if:

- section tree와 block typing이 안정적이다
- page/slide ordering이 유지된다
- table/figure/procedure 분리가 보인다
- anchor/citation target이 재현 가능하다

evidence:

- block distribution
- section tree sample
- representative layout or bbox sample

### 7.3 reader_grade

pass if:

- summary와 detail이 구분된다
- 절차, 경고, 명령, 설명이 섞이지 않는다
- reader가 스크롤만으로도 구조를 판별할 수 있다

evidence:

- rendered screenshot set
- representative page review

### 7.4 chat_grade

pass if:

- chunk가 source-backed다
- citation jump landing이 유효하다
- answer가 supporting section/block로 되돌아간다
- ambiguous question에서 honest no-answer가 가능하다

evidence:

- retrieval sample
- answer/citation sample
- multi-turn grounded sample

### 7.5 governance_grade

pass if:

- source_lane, source_ref, fingerprint, review_state가 있다
- boundary와 approval 상태가 노출 가능하다
- rerun / repair history를 설명할 수 있다

evidence:

- manifest sample
- approval/boundary sample
- run history sample

## 8. Lane Interpretation

### 8.1 Official Lane

기본 기대치:

- `gold`를 목표로 한다
- `source_fidelity`, `reader_grade`, `chat_grade` 모두 강하게 요구한다

### 8.2 User Upload / Customer Lane

기본 기대치:

- 시작 verdict는 보수적으로 본다
- upload 직후 `promoted` 금지
- `bronze -> repair -> silver -> review -> gold candidate` 흐름이 정상이다

## 9. Evidence Minimum

각 verdict closeout에는 최소 아래 evidence가 있어야 한다.

- representative rendered page or slide sample
- source lineage sample
- citation landing sample
- known issues list
- recommended next action

evidence 없는 high score는 무효다.

## 10. Fixture Set Minimum

rubric 검증용 fixture는 아래 최소 세트를 가진다.

1. `official_html_clean`
2. `official_pdf_text`
3. `official_pdf_figure_heavy`
4. `ppt_partner_dense_layout`
5. `ppt_partner_training_slide`
6. `docx_report_structured`
7. `xlsx_table_heavy`
8. `scan_pdf_ocr_heavy`
9. `bad_document_noise_case`

이 fixture set은 실제 파일 수집 전에라도 category 기준선을 먼저 잠가야 한다.

## 11. Packet Acceptance Criteria

이 rubric packet이 성공했다고 보려면 아래가 가능해야 한다.

1. 같은 문서를 두고 `왜 blocked인지`, `왜 bronze인지`, `왜 silver인지` 설명할 수 있다
2. score와 fail gate를 분리해 말할 수 있다
3. `gold`와 `promoted`를 혼동하지 않는다
4. official lane와 upload lane의 기대 baseline 차이를 설명할 수 있다
5. viewer/chat/governance를 한 판정표에서 다룰 수 있다

## 12. Non-Goals

- parser 구현 순서를 정하는 문서가 아니다
- UI badge 문구를 정하는 문서가 아니다
- promotion approval workflow 상세 문서가 아니다

## 13. Relation to Other Docs

- `goal_first_upgrade_operation_v1.md`
  - 왜 이 rubric이 필요한지 설명하는 상위 전략 문서
- `promotion_gate_matrix_v1.md`
  - 상태 전이와 승격 판정 vocabulary
- `playbook_spec_v1.md`
  - reader-grade / brand-grade 결과물의 최종 형태
- `user_upload_repair_promotion_plan_v1.md`
  - upload lane에서 이 rubric을 어떻게 적용할지

## 14. Ref Stamp

- `branch`: `feat/pbs-v3`
- `head_sha`: `f71719898cd6e8e85fa192a0c0008ecd6d241632`
