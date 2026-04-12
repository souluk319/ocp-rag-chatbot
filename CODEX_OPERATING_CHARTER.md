# CODEX_OPERATING_CHARTER

이 문서는 `사용자와 Codex가 이 저장소를 어떻게 운영할지`를 정하는 운영 헌장이다.

## 1. Authority

- 이 문서는 `reference doc`다.
- 이 문서는 `AGENTS.md`, `PROJECT.md`, `Q1_8_PRODUCT_CONTRACT.md`, `OWNER_SCENARIO_SCORECARD.yaml`, `TASK_BOARD.yaml`를 대체하지 않는다.
- 이 문서의 목적은 `제품 규칙`이 아니라 `작업 방식`, `승인 단위`, `thread 운영`, `cleanup 기준`, `검증 루프`를 고정하는 것이다.

## 2. Operating Goal

- 목표는 `Codex를 질문 응답기`로 쓰는 것이 아니라 `완성될 때까지 스스로 검증하고 배포 준비까지 밀고 가는 팀`으로 쓰는 것이다.
- 따라서 모든 작업은 `플랜 잠금 -> 실행 -> 검증 -> 정리 -> 다음 단계` 순서로만 진행한다.
- 감정적 재협상, 중간 방향 전환, 규칙 덧붙이기는 예외 상황이 아니면 금지한다.

## 3. Thread Model

### Plan Thread

- 역할: 목표, 범위, 순서, acceptance criteria, stop condition을 잠근다.
- 금지: 코드 구현, 임시 수정, 평가 수치 과장.
- 종료 조건: 아래 다섯 개가 잠기면 끝이다.
  - 목표
  - 범위
  - 검증 명령
  - 병렬 역할
  - 완료 정의

### Execution Thread

- 역할: 잠긴 플랜을 그대로 구현하고 검증한다.
- 금지: 플랜 재협상, 메타 토론 반복, unrelated cleanup 확장.
- 원칙: `한 thread = 한 milestone`.

### Release Thread

- 역할: 배포 전 검증, 산출물 정리, release/no-release 판정.
- 금지: 새 기능 추가.

## 4. Worktree Discipline

- `한 execution thread = 한 worktree`를 원칙으로 한다.
- 하나의 worktree에서는 하나의 목표만 다룬다.
- 이전 실험, 실패한 패치, unrelated diff가 보이면 먼저 cleanup하고 시작한다.
- worktree 안에서만 구현하고, main worktree는 기준선 확인과 최종 통합에만 쓴다.

## 5. Team Model

Codex는 아래 역할로 쪼개서 쓴다.

### Main Agent

- 현재 판단 제시
- 작업 순서 고정
- 결과 통합
- 최종 품질 판정

### Explorer

- 코드 경로, 병목, stale branch, 문서 충돌만 조사한다.
- 구현하지 않는다.

### Worker

- 명시된 파일 범위만 수정한다.
- 수정 후 검증 명령까지 실행한다.

### Reviewer

- diff, 회귀 위험, 빠진 검증만 본다.
- 새 기능을 제안하지 않는다.

### Team Rules

- 각 agent는 소유 파일을 먼저 고정한다.
- 겹치는 write scope를 만들지 않는다.
- 병렬 작업은 `탐색`, `구현`, `리뷰`처럼 서로 독립일 때만 쓴다.
- subagent는 사용자가 명시적으로 요구했거나, 기존 실행 계약에 이미 포함돼 있을 때만 쓴다.

## 6. Execution Loop

모든 execution thread는 아래 루프로만 돈다.

1. `Task Lock`
   - 이번 턴에서 바꿀 파일, 목표, 검증 명령을 먼저 고정한다.
2. `Implementation`
   - 고정된 파일만 수정한다.
3. `Verification`
   - 관련 테스트, 스크립트, 재현 명령을 실행한다.
4. `Cleanup`
   - 임시 플래그, stale file, legacy output path, silent fallback이 새로 생기지 않았는지 확인한다.
5. `Verdict`
   - 완료 / 차단 / 보류를 한 줄로 판정한다.

## 7. Validation And Escalation

실패는 세 종류로만 다룬다.

### Type A. Auto-fixable

- 코드 버그
- stale reference
- 잘못된 기본값
- 테스트 누락

이 경우 사용자 승인 없이 고치고 계속 진행한다.

### Type B. Plan Violation

- 플랜 밖 기능 추가가 필요함
- 기존 계약 문서와 충돌함
- 활성 규칙을 깨야만 진행 가능함

이 경우 바로 멈추고 `무엇이 플랜과 충돌하는지`만 보고한다.

### Type C. User Decision Required

- 제품 방향을 바꾸는 선택
- 데이터 삭제/폐기
- 외부 시스템/비용/보안 판단이 필요한 선택

이 경우에만 사용자에게 결정을 올린다.

## 8. Cleanup Rules

- cleanup은 `정리했다고 말하는 것`이 아니라 아래 네 가지가 끝난 상태를 뜻한다.
  - 삭제 또는 archive
  - 참조선 제거
  - 실행 경로 제거
  - 회귀 검증
- `우회 플래그`, `silent fallback`, `legacy output path`, `stale metric 문서`는 남겨두지 않는다.
- 같은 cleanup 이슈가 두 번 나오면, 개별 수정이 아니라 구조 변경으로 닫는다.

## 9. Done Definition

작업은 아래를 모두 만족할 때만 완료다.

- 코드가 반영됐다.
- 관련 검증 명령이 실제 통과했다.
- 새 stale path를 만들지 않았다.
- active/reference/archive 경계가 맞다.
- 다음 thread가 바로 이어받을 수 있게 로그, 리포트, 문서가 정리돼 있다.

## 10. Prompt Contract

사용자는 Codex에게 아래 형식으로 요청한다.

### Plan Prompt

```text
이번 thread는 구현 금지다.

목표:
- 무엇을 완성할지

범위:
- 무엇을 포함하고 제외할지

검증:
- 어떤 명령/리포트로 통과를 판단할지

출력:
- 현재 판단 1개
- 근거 3개 이하
- 실행 순서
- 병렬 역할
- acceptance criteria
```

### Execution Prompt

```text
플랜은 잠겼다. 이제 실행만 해라.

규칙:
- worktree 기준으로 진행
- subagent를 명시적으로 사용
- 이번 milestone 범위 밖 수정 금지

반드시 할 일:
- 구현
- 관련 테스트
- cleanup 확인
- diff self-review
```

### Release Prompt

```text
배포 전 검증만 해라. 새 기능 추가 금지.

확인 항목:
- 테스트
- 환경 설정
- 실행 경로
- 산출물
- release/no-release verdict
```

## 11. Anti-Patterns

아래 패턴은 금지한다.

- plan thread에서 바로 구현 시작
- execution thread에서 플랜 재협상
- 한 thread에 전략, 구현, 감정 소모를 모두 넣기
- cleanup 없이 계속 덧칠하기
- 테스트 없는 완료 선언
- stale 문서가 reference로 남아 있는 상태 방치
- 사용자가 `승인`만 반복하게 만드는 잘게 쪼갠 운영

## 12. Current Commitment

이 저장소에서 Codex는 아래 원칙을 따른다.

- `현재 판단 1개`를 먼저 제시한다.
- 근거는 로그, 코드, 데이터 기준으로만 든다.
- 플랜이 잠기면 실행 thread에서는 흔들지 않는다.
- cleanup은 실제 삭제와 검증까지 끝내야만 완료라고 부른다.
- 사용자는 `중요한 결정`만 하고, 나머지는 Codex 팀이 계속 밀고 간다.
