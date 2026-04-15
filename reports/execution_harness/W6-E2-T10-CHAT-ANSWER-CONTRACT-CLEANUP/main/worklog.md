# Local Worklog

- task_id: `W6-E2-T10-CHAT-ANSWER-CONTRACT-CLEANUP`
- lane_id: `main`
- role: `main`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- 2026-04-15: no-answer 계약을 먼저 정리했다. rude copy를 `질문에 대한 근거가 부족합니다`로 교체하고, no-answer/clarification에서도 추천질문 3개를 보장하도록 session_flow를 조정했다.
- 2026-04-15: answer command shaping에서 `#` comment line을 grounded command에서 제외하고 command block limit를 2개로 줄였다.
- 2026-04-15: related navigation/section link dedupe를 추가하고, assistant truth badge fallback이 근거 없는 no-answer에서 `Runtime`으로 뜨지 않게 Workspace truth fallback을 비웠다.
