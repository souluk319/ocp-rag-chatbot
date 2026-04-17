# Local Worklog

- task_id: `wiki_runtime_viewer_rebuild_20260417`
- lane_id: `main`
- role: `main`
- major_task: `true`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- viewer, intake, retrieval, settings, runtime-report 회귀를 집중 복구했다.
- repo root `.env` 가 서드파티 import 중 pytest 프로세스 env 를 오염시키는 경로를 확인했고 패키지 엔트리포인트에서 차단했다.
- Quick Navigation 회귀는 정적 `href` 앵커 누락으로 확인했고 최소 수정으로 복구했다.
