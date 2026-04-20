# OCP 4.20 Assignment Demo Runbook

## Purpose

이 문서는 PBS 시연을 `평가기준에 맞는 데모`로 바로 실행하기 위한 운영 대본이다.

- 목표: `사용자 -> RAG -> LLM` 구조를 실제 제품 UI와 런타임에서 보여준다
- 완료 조건:
  - 최소 5턴 이상 멀티턴 대화를 실제로 시연한다
  - 답변이 citation 기반으로 grounding 되는 것을 보여준다
  - 세션 맥락 유지와 topic shift 처리를 분명히 보여준다
  - streaming trace, cache/rerank/hybrid retrieval 같은 구현 포인트를 설명 가능 상태로 둔다
- 하지 않을 것:
  - 제품 소개성 슬라이드 발표로 시간을 쓰지 않는다
  - 문서 없는 추정 답변을 시연 포인트로 삼지 않는다
  - customer/private lane 혼합 데모를 기본 시나리오로 쓰지 않는다

## Demo Setup

- 제품 URL:
  - UI: `http://127.0.0.1:5173`
  - Backend/API: `http://127.0.0.1:8765`
- 사전 점검:
  - `powershell -ExecutionPolicy Bypass -File scripts\run_submission_demo_checks.ps1 -RunSimulator`
- 핵심 관측 포인트:
  - 답변 본문에 실제 조치나 첫 행동이 먼저 나온다
  - citation이 따라온다
  - `history_size`, `current_topic`, `retrieval_trace`, `pipeline_trace`가 일관되다
  - streaming 응답에서는 trace event 뒤에 result가 도착한다

## Recommended Order

발표 시간이 짧으면 아래 3개만 시연해도 된다.

1. `RBAC namespace admin 6-turn`
2. `Architecture to MCO shift 6-turn`
3. `etcd backup restore 6-turn`

시간이 충분하면 아래 5개를 전부 돌린다.

1. `RBAC namespace admin 6-turn`
2. `Architecture to MCO shift 6-turn`
3. `etcd backup restore 6-turn`
4. `Deployment scaling 6-turn`
5. `Machine Config Operator 6-turn`

## Scenario 1: RBAC Namespace Admin

- 평가기준 연결:
  - `RAG 정확성`
  - `멀티턴 처리 정확성`
  - `Streaming 응답 처리`
- 왜 이 시나리오를 쓰는가:
  - 같은 주제를 6턴 동안 유지하면서 명령, YAML, 확인, 회수, 개념 비교까지 이어진다
- 질문 순서:
  1. `특정 namespace에 admin 권한 주는 법 알려줘`
  2. `RoleBinding YAML 예시도 보여줘`
  3. `권한이 잘 들어갔는지 확인하는 명령도 알려줘`
  4. `RoleBinding을 삭제해서 권한을 회수하려면 어떻게 해?`
  5. `특정 이름공간에 어드민 권한 주는법은?`
  6. `cluster-admin이랑 차이도 짧게 말해줘`
- 기대 관측:
  - `current_topic=RBAC` 유지
  - `authentication_and_authorization` 계열 citation 유지
  - YAML 예시와 확인 명령이 문서 근거 안에서 나온다
- 발표 멘트:
  - `이 장면은 같은 운영 주제가 멀티턴에서 흔들리지 않는지 보는 장면입니다.`
  - `단순 chat history가 아니라 session context가 topic을 유지합니다.`

## Scenario 2: Architecture To MCO Shift

- 평가기준 연결:
  - `멀티턴 처리 정확성`
  - `시스템 아키텍처 설명력`
  - `성능 개선 전략`
- 왜 이 시나리오를 쓰는가:
  - 개요 설명에서 Operator, 그중에서도 MCO 운영 주제로 자연스럽게 topic shift 되는지 보여준다
- 질문 순서:
  1. `OpenShift 아키텍처를 처음 설명해줘`
  2. `컨트롤 플레인과 worker 차이도 설명해줘`
  3. `Operator가 왜 중요한지도 설명해줘`
  4. `Machine Config Operator가 뭐야?`
  5. `Machine Config Operator 설정은 어디서 확인해?`
  6. `Machine Config Operator 관련 명령도 알려줘`
- 기대 관측:
  - 앞 2턴은 `architecture`
  - 뒤 4턴은 `operators / machine_configuration` 계열로 중심이 옮겨간다
  - 주제가 바뀌면 retrieval도 그에 맞춰 재정렬된다
- 발표 멘트:
  - `이 장면은 follow-up 유지뿐 아니라, 주제 전환도 직접 관리한다는 증거입니다.`
  - `PBS는 질의 재작성과 rerank gating으로 shift를 처리합니다.`

## Scenario 3: etcd Backup Restore

- 평가기준 연결:
  - `RAG 정확성`
  - `운영 절차 답변 품질`
  - `근거 밖 환각 억제`
- 왜 이 시나리오를 쓰는가:
  - 백업, 복원, 확인, 주의사항, 실행 위치처럼 실무 절차형 질문이 이어진다
- 질문 순서:
  1. `etcd 백업은 어떻게 하나?`
  2. `etcd 복원 절차도 알려줘`
  3. `etcd 백업 파일이 정상인지 확인하는 방법도 알려줘`
  4. `etcd 백업 작업 중 주의사항도 정리해줘`
  5. `etcd 백업 명령은 어느 노드에서 실행해?`
  6. `정적 Pod 리소스 백업은 어디에 저장돼?`
- 기대 관측:
  - `postinstallation_configuration / etcd` 계열 citation
  - 문서에 없는 직접 검증 명령은 지어내지 않고, 복원 절차 기준으로 설명
  - 절차형 답변에서 첫 행동과 확인 포인트가 앞에 나온다
- 발표 멘트:
  - `이 장면은 hallucination을 줄이는 방식도 같이 보여줍니다.`
  - `없는 명령을 만들어내지 않고, 문서가 허용하는 복구 절차로 안내합니다.`

## Scenario 4: Deployment Scaling

- 평가기준 연결:
  - `RAG 정확성`
  - `Streaming / 운영 가이드 품질`
- 왜 이 시나리오를 쓰는가:
  - 명령형 질의에서 바로 실행 가능한 답변과 검증 명령이 나오는지 보여준다
- 질문 순서:
  1. `Deployment의 복제본 개수를 늘리는 방법을 알려줘`
  2. `Deployment 복제본을 10개로 늘리는 예시 명령을 보여줘`
  3. `Deployment 복제본 수가 반영됐는지 확인하는 명령을 알려줘`
  4. `Deployment 복제본 수를 원래대로 되돌리는 방법을 알려줘`
  5. `Deployment 스케일링할 때 운영상 주의사항을 정리해줘`
  6. `Deployment 스케일링 핵심만 짧게 요약해줘`
- 기대 관측:
  - `cli_tools` 중심 citation
  - `oc scale` 과 `oc get deployment` 계열 확인 흐름이 같이 제시된다

## Scenario 5: Machine Config Operator

- 평가기준 연결:
  - `멀티턴 처리 정확성`
  - `시스템 아키텍처 설명력`
  - `코드 설명 능력`
- 왜 이 시나리오를 쓰는가:
  - MCO 개념, 중요성, 설정 위치, 재부팅 이유, 문서 진입, 요약까지 한 주제를 길게 간다
- 질문 순서:
  1. `Machine Config Operator가 뭐야?`
  2. `그럼 실무에서 왜 중요한지도 설명해줘`
  3. `그 설정은 어디서 바꿔?`
  4. `그럼 노드 재부팅이 왜 필요한지도 알려줘`
  5. `Machine Config Operator 관련 문서는 뭐부터 읽어야 해?`
  6. `Machine Config Operator 핵심만 짧게 정리해줘`
- 기대 관측:
  - `current_topic=Machine Config Operator` 유지
  - 문서 추천 질문에도 운영 관련 book route가 citation과 함께 나온다

## What To Say About Implementation

심사자가 구현 방식 질문을 하면 아래 순서로 답하면 된다.

1. `Sparse + dense + hybrid`
2. `질의 재작성과 follow-up context는 repo 내부 코드로 직접 관리`
3. `rerank는 항상 쓰지 않고 의미상 필요한 질문에서만 켠다`
4. `streaming은 trace event와 final result를 분리해서 내려준다`
5. `session memory는 SessionContext와 turn history를 직접 저장한다`

## Code Anchors

- 채팅 스트리밍: `src/play_book_studio/app/server_chat.py`
- 세션 메모리: `src/play_book_studio/app/sessions.py`
- 다음 turn context 파생: `src/play_book_studio/app/session_flow.py`
- BM25 구현: `src/play_book_studio/retrieval/bm25.py`
- Qdrant vector 검색: `src/play_book_studio/retrieval/vector.py`
- hybrid retrieval / graph / rerank: `src/play_book_studio/retrieval/retriever_pipeline.py`
- answer context 조립: `src/play_book_studio/answering/context.py`
- answer orchestration: `src/play_book_studio/answering/answerer.py`
- 데모 시뮬레이터 시나리오: `manifests/ocp420_demo_simulator_scenarios.jsonl`
- 데모 시뮬레이터 결과: `reports/demo_simulator/ocp420_demo_simulator_eval.json`

## Fallback Plan

- 라이브 시연 전:
  - `scripts\run_submission_demo_checks.ps1 -RunSimulator`
- 실시간 질의가 흔들리면:
  - `reports/demo_simulator/ocp420_demo_simulator_eval.json` 을 열어 5개 시나리오와 30턴 통과 결과를 바로 근거로 제시
- 코드 설명 질문이 나오면:
  - 위 `Code Anchors` 순서대로 파일을 열어 설명
