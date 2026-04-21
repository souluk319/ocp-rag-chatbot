---
status: reference
doc_type: interaction-contract
audience:
  - codex
  - engineer
  - designer
  - operator
last_updated: 2026-04-21
---

# Studio Interaction Contract v1

이 문서는 PBS의 `Reader Mode <-> Studio Mode` 전환과
studio 작업의 저장 단위를 정의한다.

핵심 질문:

`사용자는 언제 읽고, 언제 작업하며, 그 작업은 어떤 단위로 남는가`

## 1. 목표

PBS는 책을 읽는 면과 작업하는 면을 함께 가져야 하지만,
둘이 서로를 망치면 안 된다.

이 계약의 목표는 아래다.

- reading context 보존
- studio interaction 명확화
- source overwrite 방지
- overlay and refinement persistence 확보

## 2. Mode Contract

## 2.1 Reader Mode

목적:

- 가장 좋은 독서 경험

기본 상태:

- sidecar 닫힘 또는 최소화
- 편집 도구 비노출
- source rail / related play / outline 중심

허용 작업:

- citation jump
- bookmark/favorite
- chat entry
- quick note 진입

## 2.2 Studio Mode

목적:

- 읽으면서 작업

기본 상태:

- sidecar open
- note, ink, inserted text, edited card 도구 노출
- 현재 section/card context 유지

허용 작업:

- section note 작성
- pen/ink 입력
- inserted text card 추가
- edited card 작성/수정
- refinement review

## 3. Transition Rules

Reader -> Studio 전환 시:

- 현재 section/card context를 유지
- scroll position 유지
- sidecar에 current target 표시

Studio -> Reader 전환 시:

- 본문 위치 유지
- unsaved change signal 표시 가능
- sidecar는 닫히지만 작업 context는 복원 가능해야 함

금지:

- mode 전환 시 본문 jump reset
- 편집 중이던 대상 상실

## 4. Edit Unit Contract

studio 작업은 아래 네 단위로 제한한다.

1. `note`
2. `ink`
3. `inserted_text_card`
4. `edited_card`

## 4.1 note

역할:

- 해석, 메모, 짧은 보조 문장

특성:

- source overwrite 아님
- current section/card에 연결

## 4.2 ink

역할:

- 펜, 낙서, 강조

특성:

- pointer/pen 친화적
- current reading target에 연결

## 4.3 inserted_text_card

역할:

- 본문 옆에 붙는 새로운 사용자 텍스트 카드

특성:

- source와 구분되는 사용자 레이어
- 나중에 refined note 또는 derived play draft로 승격 가능

## 4.4 edited_card

역할:

- 특정 card/section 단위의 수정본

특성:

- source overwrite 금지
- viewer context에서 `refined view`로 보여줄 수 있음
- promotion 전에는 draft truth로 본다

## 5. Current Target Model

모든 studio 작업은 `current target`을 가져야 한다.

current target 후보:

- playbook
- chapter
- section
- card
- block

현재 PBS 방향에 맞는 추천 기본 단위:

- `card/section`

즉 studio 저장은 book 전체보다 작은 단위에서 시작한다.

## 6. Save and Restore Rules

저장 시:

- current target 묶기
- source lineage 유지
- user layer로 저장

복원 시:

- 같은 playbook 재진입
- 같은 chapter/section/card 진입
- reader/studio mode 전환 후에도 복원 가능

## 7. Visibility Rules

각 저장 단위는 보이는 방식이 달라야 한다.

| Unit | Default Visibility |
| --- | --- |
| note | sidecar or compact inline marker |
| ink | overlay on reading surface |
| inserted_text_card | sidecar-first, optional inline reveal |
| edited_card | refined-view indicator plus sidecar detail |

원칙:

- 무엇이 source인지
- 무엇이 user-added인지
- 무엇이 refined draft인지

사용자가 혼동하면 안 된다.

## 8. Promotion Relationship

studio 작업은 곧바로 promoted truth가 아니다.

기본 관계:

- note / ink / inserted_text_card / edited_card
  -> draft truth
  -> review/refinement
  -> promotion candidate

즉 studio는 editing surface이자 repair/refinement surface다.

## 9. Chat Relationship

기본 원칙:

- source-backed truth와 user-added draft truth를 섞지 않는다
- promoted 전 user edits는 chat answer의 공식 truth로 바로 쓰지 않는다
- 단, future mode로는 user-approved note를 derived play draft로 filing 가능

## 10. Tablet/Pen Rule

studio는 tablet pen 입력을 적극 지원해야 한다.

기본 규칙:

- pen first for ink
- palm-rejection friendly pointer flow
- touch viewport에서도 current target 유지

## 11. First Implementation Scope

먼저 구현할 범위:

- reader/studio mode switch
- sidecar open/close
- note save/restore
- ink save/restore
- inserted text card skeleton
- edited card save/restore

나중에 구현할 것:

- full inline editing
- cross-document canvas
- collaborative editing

## 12. Acceptance Criteria

이 contract가 구현 가능 상태라고 보려면 아래를 만족해야 한다.

1. mode 전환 시 reading context가 유지된다
2. 편집 단위가 source overwrite가 아님이 분명하다
3. card/section 기준 저장과 복원이 가능하다
4. user-added layer와 source truth가 시각적으로 구분된다
5. future promotion flow와도 연결 가능하다

## 13. One-Line Test

아래 질문에 yes라고 답할 수 있어야 한다.

`PBS는 좋은 책을 읽는 경험을 깨뜨리지 않으면서, 메모/펜/삽입 텍스트/수정본을 같은 책 위에서 작업할 수 있는가`
