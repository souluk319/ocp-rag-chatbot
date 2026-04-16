# Local Worklog

- task_id: `ui_identity_lock_20260416`
- lane_id: `main`
- role: `main`
- major_task: `true`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- 남은 UI 정체성 흔적을 `server.py`, `cli.py`, `runtime_report.py`, cleanup tests 범위로 한정했다.
- `DEFAULT_PLAYBOOK_UI_ORIGIN` 와 `DEFAULT_PLAYBOOK_UI_BASE_URL` 를 도입해 5173 기본값을 상수화했다.
- legacy route alias 는 유지하되, runtime report probe 와 entrypoint cleanup test 도 같은 상수를 바라보게 정리했다.
- validation 통과: `python -m unittest tests.test_app_runtime_ui tests.test_entrypoint_cleanup`, `npm --prefix presentation-ui run build`
