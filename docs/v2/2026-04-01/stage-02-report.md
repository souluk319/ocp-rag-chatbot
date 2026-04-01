# 2단계 보고서 - UI와 스트리밍 한글 복구

## 목표

- 브라우저 첫 화면의 한글 UI 문구를 정상화한다.
- SSE 스트리밍 경로에서 한글 본문이 깨지지 않게 한다.
- 기본 정의 질문(`오픈시프트가 뭐야`)이 스트리밍 경로에서도 한국어 답변과 출처를 반환하게 한다.

## 변경 내용

- [runtime_chat.html](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/static/runtime_chat.html)
  - 한글 UI 문구를 전체 정리
  - favicon 404 방지를 위한 `data:,` 아이콘 추가
  - SSE 파서에서 `trim()` 의존도를 줄여 chunk 공백 손실을 줄임
  - 상태/세션/오류 문구를 운영자 관점 한국어로 정리
- [ocp_runtime_gateway.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_runtime_gateway.py)
  - 스트리밍 경로의 정의 질문 fallback 조건을 `payload 없음` 에서 `sources 없음` 까지 확장
- [check_stage02_ui_streaming.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage02_ui_streaming.py)
  - 루트 UI, 스트리밍 응답, citation viewer 를 같이 확인하는 전용 검증 스크립트 추가

## 테스트

- `python -m py_compile app/ocp_runtime_gateway.py deployment/check_stage02_ui_streaming.py`
- `python deployment/check_stage02_ui_streaming.py`
- 결과 리포트: [stage02-ui-streaming-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage02-ui-streaming-report.json)

## 완료 기준

- 루트 페이지에 한국어 UI 문구가 보인다.
- 스트리밍 응답에서 한글이 깨지지 않는다.
- `오픈시프트가 뭐야` 질문에 출처가 1개 이상 붙는다.
- 첫 citation 클릭 시 내부 HTML viewer 가 열린다.

## 실제 결과

- 루트 UI 문구 4종 통과
  - `OCP 운영 도우미`
  - `질문 보내기`
  - `응답 아래 출처를 누르면 HTML 문서를 바로 열 수 있습니다.`
  - `서비스 정상`
- 스트리밍 응답 `text/event-stream; charset=utf-8`
- 한글 replacement character 없음
- 영어 fallback 문구 없음
- 기본 정의 질문 출처 `2개`
- 첫 citation:
  - `/viewer/openshift-docs-core-validation/architecture/architecture.html`
- 최종 판정:
  - `overall_pass = true`
