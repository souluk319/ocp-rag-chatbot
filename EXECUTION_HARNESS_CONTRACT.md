# EXECUTION HARNESS CONTRACT

## Purpose

이 문서는 milestone 을 조용히 끝까지 밀기 위한 실행 하네스를 정의한다.

핵심 원칙은 아래 하나다.

`중간 진행은 lane worklog 에 모으고, 사용자에게는 closeout packet 으로만 전달한다.`

## Harness Package

모든 execution lane 은 아래 3개 자산을 가진다.

1. `manifest.json`
2. `worklog.md`
3. `final_report.json`

## Manifest Contract

manifest 는 lane 시작 전에 아래를 고정한다.

- `task_id`
- `lane_id`
- `role`
- `shell`
- `cwd`
- `python_path`
- `worktree_path`
- `write_scope`
- `target_outputs`
- `validation_commands`
- `status`

## Worklog Contract

worklog 는 아래 내용을 적재한다.

- 중간 판단
- 자동 복구 기록
- blocker 처리 기록
- 실행 명령 요약
- 검증 메모

worklog 는 사용자 보고를 대신하는 로컬 버퍼다.

## Final Report Contract

final report 는 closeout packet 의 증거를 담는다.

- 코드 수정 범위
- 산출물 경로
- 검증 로그
- smoke 결과
- release gate verdict

## Parallel Lane Contract

milestone 이 크면 lane 을 아래처럼 나눈다.

- `main`
- `explorer`
- `worker`
- `reviewer`

lane 마다 worktree 와 write scope 를 분리한다.
Main lane 은 결과를 통합하고 closeout packet 을 만든다.

## File Convention

하네스 파일 경로는 아래를 따른다.

- `reports/execution_harness/<task_id>/<lane_id>/manifest.json`
- `reports/execution_harness/<task_id>/<lane_id>/worklog.md`
- `reports/execution_harness/<task_id>/<lane_id>/final_report.json`

단일 lane milestone 이면 `<lane_id>` 는 `main` 으로 고정한다.

## Bootstrap Rule

milestone 시작 순서는 아래다.

1. `prepare_execution_harness`
2. `manifest 생성`
3. `worklog 생성`
4. `구현과 검증`
5. `final_report 작성`
6. `TASK_BOARD.yaml` 상태 반영

## Completion Gate

아래가 모두 준비되면 milestone 을 닫는다.

1. 코드 수정
2. 산출물
3. 검증 로그
4. smoke evidence
5. board state update
6. final report
