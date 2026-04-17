# Local Worklog

- task_id: `test_workspace_scaffolding_cleanup_20260417`
- lane_id: `main`
- role: `main`
- major_task: `false`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- target: `tests/test_ingestion_audit.py`의 `17`개 TemporaryDirectory + repeated path/settings scaffolding, `tests/test_app_viewers.py`의 `23`개 TemporaryDirectory + manual env save/restore + repeated load_settings/playbook_dir lookups
- action: `tests/test_app_viewers.py`에 `_workspace`, `_settings`, `_playbook_dir`, `_patched_env` helper를 추가하고 direct `load_settings(root)`를 helper 경유로 통일했다
- action: `tests/test_app_viewers.py`의 manual env save/restore 3개 블록을 `_patched_env`로 교체했고 `playbook_dir.mkdir(...)` 반복은 `_playbook_dir` helper 안으로 올렸다
- measurement: `tests/test_app_viewers.py`는 direct `load_settings(root)`를 `20 -> 1`(helper 내부)로 줄였고 manual env restore 변수(`old_artifacts`, `old_raw`, `old_manifest`)는 `0`이 됐다
- action: `tests/test_ingestion_audit.py`에 `_workspace`, `_audit_layout`, `_audit_settings` helper를 추가하고 `17`개 temp-root 부팅을 helper 경유로 통일했다
- action: `tests/test_ingestion_audit.py`의 `10`개 `part1` layout block과 `2`개 `corpus` layout block을 `_audit_layout` 호출로 접었고, common data-quality settings block `4`개를 `_audit_settings(root)`로 교체했다
- bugfix: `_audit_settings`의 `viewer_path_template` 기본값을 runtime contract 키(`version/lang/slug`)와 맞췄고, helper 도입 중 발생한 `KeyError: 'ocp_version'` 회귀를 수정했다
- validation: `pytest tests/test_app_viewers.py -q` -> `27 passed, 1 warning, 10 subtests passed`
- validation: `pytest tests/test_ingestion_audit.py -q` -> `23 passed`
- validation: `npm --prefix presentation-ui run lint/test/build` passed; existing vite chunk-size warning remains
- hygiene: post-validation cleanup removed `14` regenerated junk targets totaling `2,845,719` bytes and restored workspace junk count to `0`
