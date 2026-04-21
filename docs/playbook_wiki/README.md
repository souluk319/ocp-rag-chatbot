---
status: reference
doc_type: index
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-20
---

# Playbook Wiki Docs

이 폴더는 `LLM Wiki 원리 -> PBS Playbook System` 전환을 고정하는 문서 세트다.

## 문서 순서

1. `goal_first_upgrade_operation_v1.md`
   - 현재 코드 우선이 아니라 고정 목표 우선으로 업그레이드 기준점을 다시 잠그는 문서
   - 무엇을 유지/대체/신설할지 판단하는 foundation packet
   - 이후 packet의 실행 순서를 `goal-first` 기준으로 재정렬

2. `goal_first_grade_rubric_v1.md`
   - goal-first 평가 축, 점수, fail gate, evidence, fixture set을 잠그는 rubric
   - `gold`와 `promoted`를 분리하고, `blocked_artifact`를 명시적으로 도입
   - 이후 AST / router / repair / dashboard packet의 판정 기준선

3. `wiki_ast_v2_contract_v1.md`
   - parser, viewer, corpus, repair가 함께 참조할 canonical document graph 계약
   - page/layout/trace/validation/derivation 계층을 추가한 AST v2 정의
   - machine-readable pair: `schemas/wiki_ast_v2.schema.json`

4. `pbs_playbook_wiki_plan.md`
   - 왜 PBS가 `persistent wiki` 원리를 가져와야 하는지
   - 어떻게 `brand playbook system`으로 바꿀지
   - ordered execution packet은 무엇인지

5. `playbook_spec_v1.md`
   - PBS Playbook의 최종 형태
   - page grammar
   - block grammar
   - promotion target 정의

6. `knowledge_object_schema_v1.md`
   - source와 playbook/corpus 사이 공통 truth layer
   - knowledge object 타입
   - merge/update 기본 규칙

7. `promotion_gate_matrix_v1.md`
   - draft/review/ready/promoted/quarantined 상태 규칙
   - parse/reader/brand/chat gate 기준
   - 승격 pass/fail 판단표

8. `playbook_composer_contract_v1.md`
   - knowledge object를 책으로 조립하는 규칙
   - chapter/page assembly 단계
   - lineage와 related play를 어디에 붙일지에 대한 계약

9. `runtime_truth_binding_plan_v1.md`
   - canonical knowledge가 viewer/corpus/chat/manifest에 묶이는 방식
   - citation과 lineage가 실제 런타임에서 어떻게 연결되는지
   - same-truth runtime 원칙

10. `user_upload_repair_promotion_plan_v1.md`
   - user lane를 draft -> repair -> refine -> promote로 다루는 규칙
   - degraded detection, repair, boundary, promotion discipline

11. `implementation_packet_order_v1.md`
   - 궁극 목표까지의 단계별 execution order
   - 왜 repair와 truth binding이 accumulation보다 앞서는지

12. `runtime_load_hotspots_v1.md`
   - 현재 PBS의 무거운 경로 레지스터
   - 어떤 hotspot을 줄였고 무엇이 남았는지 비교 기준
   - 성능 packet closeout에서 인용할 기준선

13. `official_lane_gold_standard_plan_v1.md`
   - official source-first lane을 PBS gold standard로 만드는 계획
   - 가장 엄격한 품질 기준선
   - viewer/chat/corpus same-truth reference lane 정의

14. `reference_board_v1.md`
   - 역할별 reference board
   - steal / avoid / adapt 판단표
   - 다음 구체화 회의용 질문 축

15. `gitbook_inspired_viewer_shell_spec_v1.md`
   - GitBook-inspired reader shell spec
   - left rail / center reading stage / right context rail / studio sidecar 정의
   - viewer와 editor의 경계

16. `viewer_shell_wireframe_v1.md`
   - 구현 직전 수준의 viewer shell 와이어
   - panel responsibility, viewport rule, mode layout

17. `studio_interaction_contract_v1.md`
   - Reader Mode / Studio Mode 전환 계약
   - note / ink / inserted_text_card / edited_card 저장 단위
   - source truth와 user layer의 경계

## 이 폴더의 역할

이 문서들은 active contract를 대체하지 않는다.
역할은 아래와 같다.

- 목표를 흔들리지 않게 고정
- parser-first 사고를 book-first 사고로 전환
- 이후 packet의 기준선 제공

## 다음 예정 문서

- LLM wiki accumulation core plan
- measurement closeout template
