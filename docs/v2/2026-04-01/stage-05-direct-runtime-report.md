# Stage 5 Direct Runtime Report

## Verdict
`pass`

## Canonical localhost check
This is the user-visible runtime proof that Stage 6 must preserve.

- Base URL: `http://127.0.0.1:8000`
- Health: `200`
- Chat route: `200`
- Viewer route: `200 text/html`

## Direct checks
The following prompts were checked directly against `localhost:8000`:

- `오픈시프트가 뭐야`
- `OCP가 뭐야`
- `설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?`
- `업데이트 전에 확인해야 할 사항은 무엇인가요?`
- `폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?`

## Observed behavior
- All checks returned Korean answers.
- All checks returned at least one citation.
- The first citation viewer opened successfully as HTML.
- The runtime did not fall back to an English-only failure message.

## Evidence
- [stage05-direct-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-direct-runtime-report.json)

## Guardrail
Do not retell this as a widened-corpus regression result.
This file is only the direct localhost proof that Stage 6 must preserve.
