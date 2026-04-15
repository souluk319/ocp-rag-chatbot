# CODEX OPERATING CHARTER

## Purpose

이 문서는 Codex 가 이 저장소에서 높은 능률로 일하기 위한 실행 헌장이다.

핵심 목표는 하나다.

`사용자가 milestone 을 승인하면, Codex 는 병렬 lane 과 하네스를 활용해 코드 수정·산출물·검증을 한 번에 닫는다.`

현재 제품 표면은 `technical wiki runtime + buyer/demo/release packet surface` 이다.

## Operating Posture

기본 모드는 `milestone execution mode` 다.

- milestone 하나를 끝까지 닫는다.
- 필요한 파생 자산과 검증을 같은 milestone 안에 포함한다.
- 사용자 보고는 kickoff 와 closeout 두 지점으로 모은다.

## Parallel Execution Doctrine

실질 작업은 아래 구조를 기본으로 한다.

- `Main lane`
- `Explorer lane`
- `Worker 또는 Reviewer lane`

각 lane 은 아래를 먼저 고정한다.

- `lane_id`
- `role`
- `worktree_path`
- `write_scope`

Main lane 은 결과 통합과 최종 verdict 를 맡는다.

## Harness Doctrine

모든 lane 은 시작 전에 하네스를 만든다.

- `reports/execution_harness/<task_id>/<lane_id>/manifest.json`
- `reports/execution_harness/<task_id>/<lane_id>/worklog.md`
- `reports/execution_harness/<task_id>/<lane_id>/final_report.json`

manifest 는 preflight 와 write scope 를 고정한다.
worklog 는 중간 진행과 자동 복구를 버퍼링한다.
final report 는 closeout evidence 를 담는다.

## Reporting Doctrine

사용자에게 전달하는 메시지는 아래 두 개로 모은다.

1. `milestone kickoff`
2. `milestone closeout`

중간 진행은 worklog 에 쌓고, closeout 에서 아래를 한 번에 보여준다.

- 현재 판단
- 코드 근거
- 로그 근거
- 산출물 경로
- 검증 결과
- buyer/demo/release packet surface 에 대한 갱신 여부

## Escalation Doctrine

사용자 판단이 필요한 경우는 아래 네 가지다.

- 제품 방향 변경
- 파괴적 삭제
- 외부 비용 또는 보안 판단
- active contract 충돌

이 외의 문제는 lane 안에서 자동 복구하고 계속 진행한다.

## Viewer And Product Doctrine

위키 런타임은 아래 계층을 분명히 유지한다.

1. `본문`
2. `위키 탐색`
3. `개인화 overlay`

본문은 읽기와 근거 제시에 집중한다.
위키 탐색은 related books, entity hubs, sections, figures 로 확장한다.
overlay 는 page-level 또는 별도 surface 에서 개인화 신호를 쌓는다.
reader contract 는 paragraph shaping 과 figure width 기본값을 포함한다.

## Runtime Doctrine

one-click 실행은 아래를 한 묶음으로 유지한다.

1. `source rebuild`
2. `runtime materialization`
3. `active switch`
4. `relation refresh`
5. `smoke validation`

## Acceptance Packet

milestone closeout 은 아래 packet 이 준비됐을 때 성립한다.

- 수정된 코드
- 실제 산출물
- 검증 로그 또는 리포트
- live 또는 runtime smoke
- `TASK_BOARD.yaml` 상태 반영
- `final_report.json`
