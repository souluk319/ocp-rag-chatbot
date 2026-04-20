---
status: reference
doc_type: specification
audience:
  - codex
  - engineer
  - designer
  - operator
last_updated: 2026-04-20
---

# Playbook Spec v1

이 문서는 `PlayBookStudio`가 생산해야 하는 `Playbook`의 최종 형태를 정의한다.

이 문서는 parser spec이 아니다.
이 문서는 renderer spec이며, 동시에 promotion target spec이다.

즉 이 문서의 질문은 아래 하나다.

`우리는 어떤 책을 만들어야 하는가`

## 1. Playbook의 정의

Playbook은 다음 조건을 동시에 만족하는 `reader-grade wiki encyclopedia unit`이다.

- 읽고 싶다
- 보기 좋다
- 구조가 안정적이다
- 절차와 코드가 무너지지 않는다
- 출처가 보인다
- 다음 행동을 안내한다
- 챗봇과 같은 truth를 사용한다

아래 중 하나라도 빠지면 `candidate artifact`일 수는 있어도 `Playbook`은 아니다.

## 2. Primary Reader Promise

Playbook은 독자가 아래 세 질문에 빠르게 답을 얻도록 해야 한다.

1. `이 문서는 무엇에 대한 책인가`
2. `지금 내가 무엇을 해야 하는가`
3. `이 내용은 어디서 왔고 얼마나 믿을 수 있는가`

모든 page grammar는 이 세 질문을 빠르게 풀기 위해 존재한다.

## 3. Book Identity

모든 Playbook은 PBS 브랜드 감각을 가져야 한다.

핵심 인상:

- `operational`
- `editorial`
- `trustworthy`
- `structured`
- `alive but not noisy`

브랜드 규칙:

- 단락보다 구조가 먼저 보인다
- decoration보다 navigation이 먼저 보인다
- summary가 먼저, raw detail은 그 다음이다
- source lineage가 숨어 있지 않다
- 경고, 주의, 절차, 명령이 섞이지 않는다

## 4. Page Grammar

모든 Playbook page는 아래 문법을 기본으로 가진다.

### 4.1 Chapter Opener

역할:

- chapter의 목적을 한 번에 알린다
- 독자가 바로 행동할 수 있게 한다

필수 요소:

- chapter title
- one-line promise
- operator summary
- primary source lineage
- last meaningful refresh

### 4.2 Section Rhythm

기본 section 흐름:

1. `What`
2. `Why`
3. `How`
4. `Command/Procedure`
5. `Validation`
6. `Related Plays`

모든 section이 이 순서를 모두 가져야 한다는 뜻은 아니다.
하지만 section은 이 리듬 중 어디에 속하는지 판별 가능해야 한다.

### 4.3 Procedure Block

절차는 일반 단락으로 흩어지면 안 된다.

필수 구조:

- goal
- prerequisites
- ordered steps
- expected result
- validation step
- rollback or caution if relevant

### 4.4 Command Plate

코드/명령은 plain paragraph에 눌리면 안 된다.

필수 구조:

- language or shell kind
- copyable block
- optional explanation
- optional risk note
- optional output example

### 4.5 Table Plate

표는 단순 HTML table이 아니라 해석 가능한 정보 블록이어야 한다.

필수 원칙:

- header fidelity
- row/column meaning preservation
- comparison tables are visually distinguishable
- critical cells can carry emphasis

### 4.6 Figure + Caption

이미지와 도식은 장식이 아니라 evidence다.

필수 요소:

- figure body
- caption
- optional source
- optional interpretation note

### 4.7 Callout System

callout은 아래 semantic type만 허용한다.

- `warning`
- `caution`
- `note`
- `tip`
- `decision`
- `validation`

각각은 시각적으로 다르고, 의미적으로도 다르게 처리한다.

## 5. Information Rails

본문 외에 독자의 판단을 돕는 보조 레일이 필요하다.

### 5.1 Source Lineage Rail

독자는 항상 아래를 알 수 있어야 한다.

- 이 내용이 어느 source에서 왔는지
- official인지 user/private인지
- 최신성이 어떤지
- conflict가 있는지

### 5.2 Citation Grammar

citation은 footnote처럼 숨어 있으면 안 된다.

원칙:

- section/claim 가까이에 있어야 함
- click하면 landing quality가 좋아야 함
- anchor fidelity가 있어야 함
- source preview가 가능해야 함

### 5.3 Related Play Rail

책은 혼자가 아니다.

필수 역할:

- 다음에 읽을 책 안내
- 관련 procedure 연결
- 비교해야 할 operator play 연결

## 6. Content Object Types

Playbook은 아래 content object를 안정적으로 표현해야 한다.

- overview summary
- concept explanation
- entity card
- procedure
- command block
- validation checklist
- comparison table
- warning/caution
- troubleshooting note
- glossary entry
- source excerpt
- derived operator note

## 7. Reader Modes

Playbook은 하나의 본문을 여러 읽기 방식으로 풀 수 있어야 한다.

### 7.1 Read Mode

목적:

- 차분하게 읽고 이해

우선순위:

- chapter coherence
- summary
- callout clarity

### 7.2 Operate Mode

목적:

- 실제 작업 수행

우선순위:

- procedure
- commands
- validation
- rollback/caution

### 7.3 Explore Mode

목적:

- 개념 연결과 추가 탐색

우선순위:

- related plays
- entity/concept traversal
- source lineage

## 8. Acceptance Criteria

Playbook 승격은 아래 기준을 모두 봐야 한다.

### 8.1 Reader-Grade Pass

pass 조건:

- chapter opener가 chapter purpose를 분명히 전달한다
- section hierarchy가 한눈에 보인다
- structured content가 단락에 눌리지 않는다
- 독자가 스크롤만으로도 리듬을 이해할 수 있다

evidence:

- rendered page screenshots
- structured block fidelity check

현재 주의 gap:

- flattened structured PDF
- weak section rhythm

### 8.2 Brand-Grade Pass

pass 조건:

- PBS 고유 문법이 page 전반에 반복된다
- source rail, summary, procedure, validation block이 일관적으로 보인다
- decorative noise 없이 operational identity가 유지된다

evidence:

- representative pages side-by-side
- brand checklist

현재 주의 gap:

- wiki-like but not book-like output

### 8.3 Chat-Grade Pass

pass 조건:

- page에서 보이는 claim이 corpus에서도 trace 가능하다
- citation jump가 유효하다
- procedure/command가 chat answer와 충돌하지 않는다

evidence:

- multi-turn query with landing
- answer/citation consistency

현재 주의 gap:

- viewer/chat truth drift

## 9. Non-Goals

이 spec이 하지 않으려는 것은 아래다.

- raw markdown styling guide가 되는 것
- parser implementation detail을 대신하는 것
- one-off demo layout을 정당화하는 것
- source provenance 없는 synthesis를 허용하는 것

## 10. One-Line Test

아래 질문에 `yes`라고 답할 수 있어야 한다.

`이 page는 단지 렌더된 문서가 아니라, PBS가 편집해 출판한 Playbook처럼 보이는가`
