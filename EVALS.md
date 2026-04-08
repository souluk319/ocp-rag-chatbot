# EVALS.md

## 목적

이 문서는 현재 `chatbot-first knowledge/study MVP`의 평가 기준을 정의한다.
핵심 원칙은 두 가지다.

- 평가는 `baseline`과 `release` 두 단계만 쓴다.
- retrieval, answer, multi-turn, source-view, runtime은 따로 본다.

이 문서는 현재 OCP 4.20 중심 코퍼스와 현재 runtime/UI를 기준으로 한다.
future Doc-to-Book 확장 평가 기준은 여기서 바로 확정하지 않는다.

## 평가 레벨

### baseline

- 실험과 내부 데모 반복이 가능한 수준
- 명백한 회귀가 없는지 확인하는 수준
- 멀티턴, grounding, UI 기본 동작이 깨졌는지 빠르게 잡는 용도

### release

- 발표나 배포 전 최종 확인 수준
- 실제 사용자 질문에서 신뢰를 줄 수 있어야 하는 수준
- baseline 전부 통과 후, 고가치 실패 케이스까지 같이 본다

## 평가 레이어

현재 평가는 아래 다섯 레이어로 분리한다.

1. retrieval grounding
2. answer grounding and citation retention
3. multi-turn continuity
4. source-view usability
5. runtime / API health

중요:

- retrieval hit과 final citation은 다르다
- final citation과 right-panel source rendering도 다르다
- 각 레이어는 별도 실패로 기록해야 한다

## Baseline Gates

baseline은 아래 항목을 함께 통과해야 한다.

### 1. Fixed Canary Set

다음 5개 질문을 고정 canary set으로 사용한다.

1. `Pod Pending 상태는 무엇을 의미해?`
2. `CrashLoopBackOff 문제를 어떻게 확인해?`
3. `oc login 사용법 알려줘`
4. `Pod lifecycle 개념 설명해줘`
5. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`

Pass criteria:

- 전부 HTTP `200`
- 전부 grounded answer로 반환
- 전부 citation 1개 이상 포함
- citation에 열 수 있는 `href` 또는 source-view target이 있음

### 2. Source Panel Readiness

같은 canary 답변에 대해 확인한다.

- 첫 citation을 우측 source panel에서 열 수 있어야 한다
- source view가 읽을 수 있는 문서 내용이어야 한다
- raw debug dump나 빈 패널이면 실패다

### 3. Multi-turn Baseline

한 세션에서 아래 흐름을 확인한다.

1. `특정 namespace만 admin 권한 주는 방법 단계별로 알려줘`
2. `2번만 더 자세히`
3. `다음은?`

Pass criteria:

- 주제가 RBAC에서 벗어나지 않는다
- follow-up이 unrelated topic으로 리셋되지 않는다
- step-aware follow-up으로 이어진다

### 4. Clarification Boundary

의도적으로 애매한 질문 하나를 넣는다.

예:

- `로그는 어디서 봐?`

Pass criteria:

- 근거 없이 찍지 않고 짧은 clarification으로 꺾는다

## Release Gates

release는 baseline 전부 통과가 선행 조건이다.

### 1. Ops Safety

다음 범주의 운영 질문 세트를 확인한다.

- RBAC user / group / serviceaccount 구분
- certificate expiry check
- etcd backup and restore
- terminating project / finalizer
- update / version-sensitive question

Pass criteria:

- invented command, flag, procedure가 없어야 한다
- cluster-scope 작업을 namespace-scope로 축소 답변하면 실패다
- follow-up에서 unsafe subject mutation이 있으면 실패다

### 2. Citation Reliability

Pass criteria:

- release set의 grounded answer는 citation 1개 이상 유지
- citation이 실제 관련 문서/섹션을 가리킴
- citation이 source panel에서 다시 열림
- `그 문서 기준으로 다시` 같은 follow-up에서 branch가 유지되거나 의도적으로 refresh됨

### 3. Multi-turn Release Set

필수 흐름:

- step follow-up: `2번만 더`, `다음은?`
- reference follow-up: `그거 다시`, `그 문서 기준으로 다시`
- branch return: topic A -> topic B -> `아까 그 RBAC 문서 기준으로 다시`

Pass criteria:

- reference resolution이 맞아야 한다
- 다른 topic으로 drift하면 실패다
- grounding이 조용히 사라지면 실패다

### 4. Runtime Health

Pass criteria:

- `GET /` returns `200`
- `GET /api/health` returns `200`
- `/api/chat` canary set 통과
- `/api/chat/stream`이 grounded query에서 정상 streaming

### 5. Human Review

release는 자동 테스트만으로 닫지 않는다.

브라우저 눈검토 1회가 필요하다.

- chatbot-first feel 유지
- source tag가 보이고 이해 가능
- right-side panel이 debug inspector가 아니라 study panel처럼 보임
- 일반 16:9 데스크톱 화면에서 무리 없이 보임

## 현재 코드와 연결되는 평가 축

### corpus / preprocessing

- 정규화 섹션 수
- 청크 생성 수
- `viewer_path`, `source_url`, `section_path` 보존 여부
- 코드/표 블록 손실 여부

관련:

- [tests/test_ingestion_normalize.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/test_ingestion_normalize.py)
- [tests/test_ingestion_chunking.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/test_ingestion_chunking.py)
- [tests/test_ingestion_audit.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/test_ingestion_audit.py)

### retrieval

- follow-up rewrite가 standalone query로 재작성되는지
- `forbidden_book_slugs`로 새지 않는지
- 고가치 질의에서 기대 문서를 상위 결과에 포함하는지
- no-answer / clarify가 필요한 경우 과잉 답변하지 않는지

관련:

- [`manifests/retrieval_sanity_cases.jsonl`](manifests/retrieval_sanity_cases.jsonl)
- [`manifests/retrieval_eval_cases.jsonl`](manifests/retrieval_eval_cases.jsonl)
- [tests/test_retrieval_core.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/test_retrieval_core.py)

### answer generation

- 답변이 실제 citation과 정합적인지
- 질문 유형별 답변 스타일 차이가 유지되는지
- 근거 부족 시 과장 답변 대신 경고/질문으로 꺾는지
- corrective follow-up에서도 주제가 유지되는지

관련:

- [`manifests/answer_eval_cases.jsonl`](manifests/answer_eval_cases.jsonl)
- [`manifests/ragas_eval_cases.jsonl`](manifests/ragas_eval_cases.jsonl)
- [tests/test_answering_answerer.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/test_answering_answerer.py)

### runtime / UI

- Enter 전송, Shift+Enter 개행, IME 조합 중 오동작 방지
- streaming, citation 표시, 세션 리셋, 새 세션 동작
- empty state 질문 예시, 좌측 데이터 선택, source panel 연동
- 업로드 소스 체크 상태가 요청 payload에 반영되는지

관련:

- [tests/test_app_ui.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/test_app_ui.py)

## 추적해야 하는 실패 케이스

- ambiguous query answered without clarification
- clear query incorrectly forced into clarification
- wrong or irrelevant citation
- retrieval은 맞았는데 final citation이 사라짐
- follow-up drift
- unsafe command mutation guessed from follow-up
- source panel opens but is unreadable

## 권장 실행 순서

1. unit tests
2. fixed five-query canary set
3. one multi-turn flow
4. one ambiguity flow
5. source-panel click/open verification
6. release라면 full curated ops set + one browser-eye review

## 운영 규칙

- 새로운 기능을 넣으면 최소 하나의 테스트 또는 eval 영향 설명이 필요하다
- README에는 평가 목적과 구조만 적고, 세부 기준 변경은 이 파일에서 관리한다
- release 직전에는 평균 점수보다 고가치 실패 케이스를 우선 확인한다
- future upload-first Doc-to-Book gate는 현재 gate를 오염시키지 말고 별도 확장으로 추가한다
