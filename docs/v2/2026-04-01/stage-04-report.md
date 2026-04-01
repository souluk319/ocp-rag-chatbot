# 4단계 보고서 - citation 클릭과 viewer 정합성

## 목표

- 답변에 붙는 citation 이 실제 내부 HTML viewer 를 가리키는지 확인한다.
- 기본 질문 2개와 운영 질문 2개에서 최소 1개 이상의 citation 이 붙는지 확인한다.
- Enter 전송 동작이 실제 UI에 반영됐는지 함께 확인한다.

## 변경 내용

- [runtime_chat.html](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/static/runtime_chat.html)
  - `Enter` 전송 / `Shift+Enter` 줄바꿈으로 변경
- [check_stage04_citation_viewer.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage04_citation_viewer.py)
  - 기본 질문 2개, 운영 질문 2개를 실제 `/api/v1/chat` 으로 호출
  - 첫 citation 의 `viewer_url` 이 내부 `/viewer/...` HTML 로 연결되는지 검증

## 테스트

- `python -m py_compile deployment/check_stage04_citation_viewer.py`
- `python deployment/check_stage04_citation_viewer.py`
- 결과 리포트: [stage04-citation-viewer-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage04-citation-viewer-report.json)

## 완료 기준

- UI에 `Enter` 전송 동작이 실제로 들어가 있다.
- 질문 4개 모두 응답 `200`
- 질문 4개 모두 citation 1개 이상
- 질문 4개 모두 첫 citation viewer 가 내부 HTML 문서를 연다.

## 실제 결과

- UI 루트 HTML 에 `Enter` 전송 핸들러 존재
  - `event.key === "Enter" && !event.shiftKey`
- 질문 4개 모두 응답 `200`
- 질문 4개 모두 source `2개`
- 질문 4개 모두 첫 citation viewer `200 text/html`
- 검증 질문:
  - `오픈시프트가 뭐야`
  - `OCP가 뭐야`
  - `방화벽 설정은 왜 필요한가요?`
  - `업데이트 전 확인사항은 무엇인가요?`
- 최종 판정:
  - `overall_pass = true`
