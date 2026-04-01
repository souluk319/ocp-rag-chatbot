# 3단계 보고서 - 로컬 런타임 경로 고정

## 목표

- `localhost:8000` 을 로컬 게이트웨이의 권위 경로로 고정한다.
- bridge, OpenDocuments, gateway 의 기본 포트를 문서와 실행 스크립트에서 일치시킨다.
- 현재 health, active index, active manifest, 기본 질문 응답이 같은 런타임을 가리킨다는 증거를 남긴다.

## 변경 내용

- [start_local_runtime.ps1](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/start_local_runtime.ps1)
  - 로컬 표준 시작 래퍼 추가
- [stop_local_runtime.ps1](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/stop_local_runtime.ps1)
  - 8000/18101/18102 정리용 중지 스크립트 추가
- [check_stage03_runtime_lock.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage03_runtime_lock.py)
  - health, 포트, active index, 기본 질문 응답, runbook 정합성까지 같이 검사하는 잠금 검증기 추가
- [operator-runbook-stage14.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/operator-runbook-stage14.md)
  - gateway 엔드포인트를 `8000` 기준으로 정정
- [stage14-runtime-launch.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage14-runtime-launch.md)
  - 로컬 권장 실행 경로를 `start_local_runtime.ps1` 로 명시

## 테스트

- `powershell -NoProfile -ExecutionPolicy Bypass -File deployment/start_local_runtime.ps1 -HoldSeconds 5`
- `python -m py_compile deployment/check_stage03_runtime_lock.py`
- `python deployment/check_stage03_runtime_lock.py`
- 결과 리포트: [stage03-runtime-lock-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage03-runtime-lock-report.json)

## 완료 기준

- 8000, 18101, 18102 가 모두 살아 있다.
- `/health` 의 active index 가 `indexes/current.txt` 와 일치한다.
- `/` 과 `/api/v1/chat` 이 정상 응답한다.
- Stage 14 runbook 과 실제 로컬 포트 계약이 일치한다.

## 실제 결과

- 표준 래퍼로 `startup_pass = true`
- 고정 포트 확인
  - `8000`
  - `18101`
  - `18102`
- `/health` active index:
  - `s15c-core`
- `indexes/current.txt`:
  - `s15c-core`
- 기본 질문 `/api/v1/chat` 응답 `200`
- 첫 viewer:
  - `/viewer/openshift-docs-core-validation/architecture/architecture.html`
- 최종 판정:
  - `overall_pass = true`
