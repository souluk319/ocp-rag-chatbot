# Reader-Grade Book Strategy

## 목적

이 문서는 현재 대화에서 정리된 `reader-grade book` 방향을 고정한다.

핵심 목표는 단순하다.

- 원문을 보기 좋게 옮기는 것이 아니라
- 실제로 읽히고, 표시하고, 다시 찾아볼 수 있는 `북`을 만든다

## 현재 판단

지금의 `gold`, `approved`, `materialized` 같은 데이터 상태 용어만으로는 사용자가 느끼는 `좋은 북` 품질을 설명할 수 없다.

우리가 원하는 북은 아래 조건을 가져야 한다.

- 세분화가 잘 되어 있다
- 제목이 사람이 읽기 좋다
- 번호 찌꺼기가 독해를 방해하지 않는다
- 설명 밀도가 과하지 않다
- 절차, 코드, 검증, 주의가 분리돼 있다
- 하이라이트, 밑줄, 메모를 얹고 싶은 표면을 가진다

## 제품 방향

### 1. 용어를 분리한다

- `runtime-approved`
  - 데이터 상태
- `reader-grade book`
  - 사용자 표면 품질

즉, 승인된 문서가 있다고 해서 곧바로 `좋은 북`이 되는 것은 아니다.

### 2. 두 가지 뷰어를 분리한다

- `Manual Book Viewer`
  - 긴 공식 문서를 읽는 용도
  - 좌측 목차, 현재 섹션 하이라이트, anchor jump 가 중요하다
- `Derived Playbook Viewer`
  - 짧고 실행형 문서를 보는 용도
  - 목차보다 절차, 검증, 경고, 관련 섹션이 더 중요하다

### 3. 목차 UX를 적극 도입한다

OCP 계열 manual book 에는 공식 문서형 목차가 필요하다.

- 좌측 목차
- 현재 섹션 하이라이트
- 검색 또는 필터
- anchor jump

단, 모든 문서에 이 구조를 강제하지는 않는다.
긴 manual book 에는 적합하지만, slim derived playbook 에는 과하다.

## 문서 구조 기준

reader-grade book 은 기본적으로 아래 역할 단위를 따른다.

- `Overview`
- `When To Use`
- `Prerequisites`
- `Procedure`
- `Commands / YAML`
- `Verify`
- `Failure Signals`
- `Source Trace`

문서를 그대로 흘려보내지 않고, 이 역할에 맞게 다시 배치해야 한다.

## 문체 기준

우리는 새로운 말투를 발명하지 않는다.
이미 검증된 기술 가이드 / runbook 톤을 사용한다.

### 금지

- 제작자 시점
  - `이 shadow book은`
  - `이 초안은`
  - `reader-grade`
- 내부 메모 톤
  - `우리가 다시 묶었다`
  - `이 문서는 실험용이다`

### 권장

- `이 문서는 ... 절차를 설명한다`
- `다음 조건을 충족해야 한다`
- `다음 순서로 진행한다`
- `다음 항목으로 결과를 확인한다`
- `다음 경우에는 이 절차를 사용하지 않는다`

## 오픈소스 레퍼런스

현재 방향은 아래 조합을 따른다.

- `Material for MkDocs`
  - heading hierarchy
  - admonition
  - code block readability
  - table readability
- `Runbook structure`
  - prerequisite
  - procedure
  - verify
  - failure signals

즉, 새로운 스타일을 발명하는 대신 이미 검증된 문서 경험을 흡수한다.

## 샘플 전략

현재 첫 shadow sample 은 아래 두 권으로 고정한다.

- `backup_and_restore`
- `installing_on_any_platform`

이 둘을 먼저 마음에 드는 형태로 고정한 뒤, 그 규칙을 일반화한다.

## 실행 원칙

1. 현재 live corpus 는 건드리지 않는다.
2. 새 샘플 데이터셋으로 shadow pipeline 을 돌린다.
3. 먼저 마음에 드는 북 1권을 만든다.
4. 그 다음 같은 규칙으로 두 번째 북을 만든다.
5. 그 후에만 자동화 일반화를 논의한다.

## Decision Log

### 2026-04-13

- `tone_is_a_primary_quality_axis`
  - 형태가 깔끔해도 문체가 내부 메모처럼 보이면 북 품질은 fail 로 본다.
- `record_before_confusion`
  - 대화 중 합의된 방향은 바로 문서에 남긴다.
- `manual_book_needs_toc_viewer`
  - OCP 계열 manual book 은 좌측 목차와 현재 섹션 하이라이트를 갖는 viewer 를 목표로 한다.
- `compare_rendered_output_not_ast`
  - 자동화 품질 비교는 JSON AST 가 아니라 같은 원문의 실제 viewer 렌더 결과와 reference book 을 기준으로 본다.

## 현재 결론

지금 필요한 것은 더 많은 점수표가 아니다.

지금 필요한 것은 아래 두 가지다.

- `좋은 북의 정답 형태`
- `그 정답 형태를 실제로 보여주는 샘플 북`

이 문서는 그 방향을 현재 기준으로 고정한다.
