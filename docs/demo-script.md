# Demo Script

이 문서는 발표자가 그대로 읽어도 되는 실전용 진행 스크립트다.
`Trace` 패널을 켜고, 각 시나리오마다 `sources`와 `rewrite`가 보이는지 같이 보여준다.

## 0. 공통 준비

- 첫 화면에서 `New Chat`을 눌러 세션을 새로 만든다.
- `Trace` 패널은 열린 상태로 둔다.
- 가능하면 `ops`와 `learn` 모드 전환이 보이도록 시작 전에 한 번만 설명한다.

## 1. OPS Walkthrough

- Type: `CrashLoopBackOff 원인하고 바로 확인할 명령 알려줘`
- What should appear in trace/sources:
  - `rewrite` 단계에서 짧고 독립적인 질의로 정리되는지 보인다.
  - `search`와 `rerank`에서 `ocp-crashloop-troubleshooting-ko.md` 또는 비슷한 운영 문서가 상단에 올라와야 한다.
  - `sources`에는 장애 진단 문서와 명령 예시가 함께 잡히는지 본다.
  - 답변에는 `증상 -> 원인 후보 -> 확인 명령 -> 조치` 흐름이 드러나야 한다.
- Rubric item:
  - `RAG 정확성`
  - `시스템 아키텍처`
  - `추가 요구사항(Trace)`
- Fallback line:
  - `문장 순서는 조금 달라도, 핵심은 CrashLoopBackOff의 원인과 바로 확인할 명령을 문서 기반으로 보여준다는 점입니다.`

## 2. Learn Walkthrough

- Type: `OpenShift Route가 뭐야?`
- What should appear in trace/sources:
  - `learn` 모드가 활성화된 상태에서 개념 설명 톤으로 답해야 한다.
  - `sources`에는 `ocp-route-ingress-ko.md`, `ocp_route_config.md`, `ocp-basics.md` 같은 개념/비교 문서가 보이면 좋다.
  - 답변이 너무 운영 명령 위주가 아니라 `정의 -> 왜 중요한가 -> 비교 -> 예시` 흐름을 가져야 한다.
  - `trace`에서 검색된 문서가 라우팅/외부 노출 맥락으로 정렬되는지 확인한다.
- Rubric item:
  - `RAG 정확성`
  - `멀티턴 처리 정확성`이 아니라도, `답변 품질과 맥락 반영`을 보여주는 보조 근거
  - `코드 품질 및 설명`
- Fallback line:
  - `답변 표현은 조금 달라도, Route가 OpenShift의 외부 노출 방식이고 Ingress와 비교해서 설명할 수 있으면 충분합니다.`

## 3. 5-Turn Multiturn Walkthrough

- Turn 1: `ConfigMap이 뭐야?`
- Turn 2: `그럼 Secret이랑 뭐가 달라?`
- Turn 3: `내가 Pod에 넣을 때는?`
- Turn 4: `그걸 YAML로 한 번 보여줘`
- Turn 5: `실수하기 쉬운 포인트는?`
- What should appear in trace/sources:
  - 2턴 이후 `rewrite`가 이전 질문을 이어받아 더 구체적인 질의로 바뀌는지 본다.
  - `session` 단계에서 같은 `session_id`가 유지되는지 확인한다.
  - 3~5턴에서 `ConfigMap`, `Secret`, `Pod mount`, `YAML` 관련 문서가 이어서 잡혀야 한다.
  - 마지막 턴에서 `sources`가 이전 대화를 반영해 더 좁은 문서로 수렴하는지 보여준다.
- Rubric item:
  - `멀티턴 처리 정확성`
  - `대화 이력 기반 Context 관리`
  - `RAG 정확성`
  - `추가 요구사항(Trace, caching)`
- Fallback line:
  - `중간 표현이 달라도, 마지막 질문까지 같은 세션으로 이어지고 ConfigMap과 Secret 차이를 문맥에 맞게 좁혀 설명하면 멀티턴은 성공입니다.`

## 4. 마무리 멘트

- `이 시스템은 단순 검색이 아니라, 세션 메모리와 rewrite, 검색, rerank, streaming을 한 번에 보여주는 OCP RAG 챗봇입니다.`
- `운영 질문은 runbook처럼, 학습 질문은 개념 튜터처럼 답하도록 설계했습니다.`
- `멀티턴에서는 이전 대화를 이어받아 문맥이 실제로 바뀌는지 확인할 수 있습니다.`
