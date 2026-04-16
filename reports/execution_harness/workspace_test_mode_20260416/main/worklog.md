# Local Worklog

- task_id: `workspace_test_mode_20260416`
- lane_id: `main`
- role: `main`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- `presentation-ui/src/lib/runtimeApi.ts` 에 `/api/chat/stream` NDJSON 소비 경로 `sendChatStream()` 추가.
- `presentation-ui/src/pages/WorkspacePage.tsx` 에 `TEST` 토글, `activeTestTrace`, stream trace 누적, 하단 forensic panel 연결.
- `presentation-ui/src/components/WorkspaceTracePanel.tsx` 추가. 실제 `trace` event, `retrieval_trace`, `pipeline_trace` 만 렌더한다.
- `presentation-ui/src/pages/WorkspacePage.css` 에 TEST 버튼과 하단 trace panel 스타일 추가.
- `tests/test_app_runtime_ui.py`, `tests/test_app_chat_api_multiturn.py` 로 UI 계약과 stream trace/result payload 회귀를 묶음.
- validation:
  - `npm --prefix presentation-ui run build` passed
  - `& .\.venv\Scripts\python.exe -m unittest tests.test_app_runtime_ui tests.test_app_chat_api_multiturn` passed
  - `curl.exe -s -D - http://127.0.0.1:8765/ -o NUL` 기준 `307 -> http://127.0.0.1:5173/`
