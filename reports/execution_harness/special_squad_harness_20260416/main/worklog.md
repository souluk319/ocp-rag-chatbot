# Local Worklog

- task_id: `special_squad_harness_20260416`
- lane_id: `main`
- role: `main`
- major_task: `true`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- active 계약을 확인한 결과 기존 harness 는 병렬 lane 권장은 있었지만 major task 특공대 강제는 없었다.
- `AGENTS.md` 와 `EXECUTION_HARNESS_CONTRACT.md` 를 수정해 major task 에 `main + explorer + worker/reviewer` 최소 구성을 고정했다.
- `scripts/prepare_execution_harness.py` 에 `--major-task`, `--companion-lane` 지원과 companion lane skeleton 생성 로직을 추가했다.
- `tests/test_prepare_execution_harness.py` 를 추가해 major task 강제 규칙과 companion lane skeleton 생성을 검증했다.
- smoke 로 `special_squad_harness_20260416` packet 을 생성했고 `explorer`, `reviewer` companion lane manifest 가 함께 생겼다.
