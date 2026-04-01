# Stage 8 Demo Readiness Report

## Verdict

`pass`

Stage 8 is about live demo readiness only.
It is not a production-readiness claim.

## Direct demo checks

- checked_at: `2026-04-01T03:33:27.075946+00:00`
- base_url: `http://127.0.0.1:8000`
- health_status: `200`
- ui_status: `200`
- primary_passed: `4/4`
- follow_up_pass: `True`

## Primary demo questions

| id | status | sources | viewer | route |
| --- | --- | --- | --- | --- |
| demo-01-definition | pass | 2 | 200 text/html | manifest_runtime_rescue |
| demo-02-firewall | pass | 1 | 200 text/html | manifest_runtime_rescue |
| demo-03-update | pass | 2 | 200 text/html | manifest_runtime_rescue |
| demo-04-disconnected | pass | 2 | 200 text/html | manifest_runtime_rescue |

Primary live demo order:

1. `오픈시프트가 뭐야`
2. `설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?`
3. `업데이트 전에 확인해야 할 사항은 무엇인가요?`
4. `폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?`

## Follow-up demo

- turn_2 status: `pass`
- turn_2 sources: `2`
- turn_2 viewer: `200 text/html`

Follow-up pair:

1. `업데이트 전에 확인해야 할 사항은 무엇인가요?`
2. `그 문서 기준으로 제일 먼저 볼 항목은 뭐야?`

## Secondary watchlist

- `OperatorHub와 Operator Lifecycle Manager는 어떤 역할을 하나요?`
  - currently unstable for the live demo because it can still drift into support/troubleshooting citations
- `설치 후 Operator 상태를 점검하려면 어떤 문서를 봐야 하나요?`
  - still drifts between installing and support families
- `네트워크 문제를 진단하려면 어떤 문서를 먼저 봐야 하나요?`
  - question phrasing is still sensitive and can fall back to weak RAG behavior
- `인증서 유지보수나 보안 관련해서 먼저 볼 문서는 무엇인가요?`
  - still sensitive across security/authentication/post-install families
- `스토리지 문제를 점검할 때 먼저 볼 문서는 무엇인가요?`
  - not yet stable enough for the primary live demo set

## User-visible checkpoint

- Open `http://127.0.0.1:8000`
- Ask these four questions in order:
  - `오픈시프트가 뭐야`
  - `설치 시 방화벽에서 어떤 포트와 예외를 허용해야 하나요?`
  - `업데이트 전에 확인해야 할 사항은 무엇인가요?`
  - `폐쇄망 설치에서 oc-mirror 플러그인으로 이미지를 미러링하려면 어떤 문서를 봐야 하나요?`
- Click the first citation on each answer
- Run the follow-up pair after the update question

## Output

- JSON: `C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-08-report.json`
