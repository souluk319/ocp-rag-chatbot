# Local Worklog

- task_id: `ui_identity_fix_20260416`
- lane_id: `main`
- role: `main`
- major_task: `true`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- `presentation-ui` 내부에서 `/studio` 와 `data-situation-room` 을 active route 처럼 쓰는 경로를 확인했다.
- `src/play_book_studio/app/server.py` 에 legacy redirect map 을 분리하고 `/studio -> /workspace`, `/data-situation-room -> /playbook-library` 로 격하시켰다.
- `presentation-ui/src/App.tsx` 에 canonical route `/workspace` 를 추가하고 `/studio` 는 `Navigate` alias 로만 유지했다.
- `Hero.tsx`, `ProductSurfaces.tsx`, `PlaybookLibraryPage.tsx`, `ProjectDetailsPage.tsx`, `index.html` 의 copy/links 를 canonical surface naming 으로 정리했다.
- `tests/test_app_runtime_ui.py` 는 source-string smoke 를 현재 계약에 맞게 갱신했다.
- validation 은 `tests.test_app_runtime_ui` 와 `npm --prefix presentation-ui run build` 둘 다 통과했다.
