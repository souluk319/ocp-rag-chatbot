# Worklog

- 목표: `no context citations assembled` 로 떨어지던 follow-up status query 와 wiki navigation query 를 runtime 답변으로 복구.
- 판단:
  - `삭제 진행 상태를 확인하는 방법도 알려줘` 는 follow-up detector 누락 때문에 rewrite/context carry가 깨져 있었다.
  - `문제가 생기면 위키 안에서 어떤 순서로 이동해야 하는지 알려줘` 는 doc-locator intent 누락과 clarification gate 때문에 citation selection 전에 비워졌다.
- 수정:
  - doc-locator regex 에 `위키/wiki + 이동/순서/경로` 패턴 추가
  - follow-up regex 에 `진행 상태를 확인하는 방법` 패턴 추가
  - troubleshooting doc-locator query 에 `support`, `validation_and_troubleshooting` 우선 순서와 `release_notes`, `web_console` 패널티 추가
  - context clarification gate 가 doc-locator query 를 비우지 않도록 조정
  - doc-locator 답변이 `순서/이동` 질문에 더 직접적으로 응답하도록 보정
- 검증:
  - `./.venv/Scripts/python.exe -m pytest tests/test_retrieval_query_intents.py tests/test_answering_context.py -q`
  - `./.venv/Scripts/python.exe -m pytest tests/test_answering_output.py tests/test_answering_routes.py tests/test_app_session_flow.py tests/test_app_chat_api_multiturn.py -q`
  - live smoke:
    - `프로젝트가 Terminating에서 안 지워질 때 어떻게 해?` -> `삭제 진행 상태를 확인하는 방법도 알려줘`
    - `문제가 생기면 위키 안에서 어떤 순서로 이동해야 하는지 알려줘`
