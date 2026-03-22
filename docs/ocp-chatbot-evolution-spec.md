# OCP Chatbot Evolution Spec

`feat/ocp-chatbot-evolution` 브랜치에서 진행할 교육형/운영형 고도화의 실행 문서.

이 문서는 큰 재개발 대신 현재 구조를 살리면서 실제 도입 가능성을 높이는 순서만 다룬다.
기준 구조는 `src/api/__init__.py`, `src/pipeline.py`, `src/retriever/__init__.py`, `src/session/__init__.py`, `src/cache/__init__.py`, `frontend/index.html`이다.

## 목표

이 챗봇을 다음 두 역할을 동시에 수행하는 사내 도구로 끌어올린다.

- `education`: 신입 교육용 OCP 개념 학습 어시스턴트
- `operations`: 실제 운영/트러블슈팅 지원 어시스턴트

단, 다음 원칙은 유지한다.

- 기존 RAG 파이프라인을 버리지 않는다.
- `main`을 기준으로 과도한 구조 재작성은 하지 않는다.
- 먼저 `더 똑똑해 보이게`가 아니라 `덜 위험하게` 만든다.

## 답변 계약

### 1. Education Contract

교육형 답변은 설명의 구조가 고정되어야 한다.

필수 출력 순서:

1. `한 줄 정의`
2. `왜 중요한가`
3. `핵심 개념 3개 내외`
4. `짧은 예시 또는 비교`
5. `다음에 이어서 물어볼 질문`

금지:

- 명령어 위주로만 답하기
- 근거 없이 운영 판단처럼 말하기
- 출처 없이 단정하기

### 2. Operations Contract

운영형 답변은 실행 순서가 고정되어야 한다.

필수 출력 순서:

1. `증상 요약`
2. `가장 가능성 높은 원인 후보`
3. `바로 확인할 명령어 또는 확인 포인트`
4. `즉시 조치 순서`
5. `주의사항 또는 롤백 포인트`
6. `출처`

금지:

- 원인과 조치를 섞어 쓰기
- 확인 없이 단정적 복구 절차를 제시하기
- cache/rewrite/trace를 근거처럼 보이게 쓰기

### 3. Provenance Contract

모든 모드에서 다음을 지킨다.

- 답변 근거는 `retrieved source`만 사용한다.
- `trace`는 디버그 정보다. 답변 근거가 아니다.
- `rewrite`는 내부 보정이다. 사용 사실은 보여줄 수 있지만 정답의 증거가 아니다.
- `cache hit` 응답도 source/provenance를 유지해야 한다.
- source가 약하거나 없으면 모른다고 말하는 것이 맞다.

## 구현 순서

### Phase 1. 신뢰도 착시 차단

목표: 그럴듯한 오답을 줄인다.

실행 항목:

1. cache hit에서도 source/provenance를 유지한다.
2. trace/rewrite/cache 표시는 `디버그 정보`로 낮춘다.
3. 전역 LLM endpoint switch를 운영 기능이 아니라 개발 기능으로 재정의한다.

완료 기준:

- cached 응답에도 출처가 보인다.
- 사용자는 trace를 보고 답변 근거라고 오해하지 않는다.
- 다른 사용자가 전역 endpoint 변경의 영향을 받지 않는다.

### Phase 2. 교육형/운영형 계약 분리

목표: 하나의 챗봇 안에서 두 제품 성격을 분리한다.

실행 항목:

1. 질문을 `education`, `operations`, `mixed` 정도로 얕게 분류한다.
2. 분류 결과에 따라 답변 포맷을 다르게 적용한다.
3. 프론트에서 모드 노출은 최소화하고, 먼저 내부 계약부터 분리한다.

완료 기준:

- 개념 질문은 설명형 구조로 답한다.
- 트러블슈팅 질문은 조치형 구조로 답한다.
- UI를 크게 바꾸지 않아도 답변 톤과 구조가 분리된다.

### Phase 3. Retrieval 신호 강화

목표: 질문 유형에 맞는 문서를 더 잘 올린다.

실행 항목:

1. 인덱싱 시 최소 metadata를 추가한다.
2. 추천 metadata:
   - `doc_kind`
   - `section_type`
   - `heading_path`
   - `has_command`
   - `has_yaml`
   - `has_error_pattern`
3. query type에 따라 ranking 우선순위를 다르게 준다.
   - 개념/개요 질문: concept/example/overview 우대
   - 운영/장애 질문: procedure/troubleshooting/command 우대

완료 기준:

- 교육형 질문에서 개요/설명 문서가 먼저 뜬다.
- 운영형 질문에서 절차/트러블슈팅 문서가 먼저 뜬다.
- heuristic 추가보다 metadata 기반 설명이 가능해진다.

### Phase 4. 상태 외부화

목표: 단일 프로세스 데모 한계를 넘는다.

실행 항목:

1. `SessionManager` 저장소를 외부화한다.
2. `SemanticCache` 저장소를 외부화한다.
3. 먼저 저장소만 교체하고 파이프라인 경계는 유지한다.

완료 기준:

- 재시작 후에도 필요한 세션 상태를 유지할 수 있다.
- 멀티 사용자 환경에서 cache/session 일관성이 깨지지 않는다.
- 벡터 검색과 LLM 계층은 그대로 유지된다.

### Phase 5. 품질 게이트 고정

목표: 도입 판단을 감으로 하지 않는다.

실행 항목:

1. 질문셋을 최소 4종으로 분리한다.
   - 교육 개념
   - 운영 절차
   - 개요/비교
   - 트러블슈팅
2. 핵심 측정 항목을 고정한다.
   - `Top1 source correctness`
   - `Recall@5`
   - `rewrite precision`
   - `false cache hit rate`
   - `unsupported claim rate`

완료 기준:

- 변경 전후 품질을 같은 질문셋으로 비교할 수 있다.
- retrieval, rewrite, cache 수정이 답변 신뢰도를 해치지 않는지 판단할 수 있다.

## 구현 순서 요약

우선순위는 다음 순서로 고정한다.

1. `cache provenance 보존`
2. `trace/rewrite/cache의 근거성 과장 제거`
3. `전역 endpoint switch 위험 축소`
4. `education/operations 계약 분리`
5. `retrieval metadata 추가`
6. `query-type aware ranking`
7. `session/cache 외부화`
8. `평가셋과 품질 게이트 고정`

## 이번 스펙의 범위 밖

다음은 당장 하지 않는다.

- UI 전면 재설계
- 외부 RAG 프레임워크 도입
- 벡터 저장소 전면 교체
- 대규모 멀티에이전트 오케스트레이션

## 첫 구현 권장 항목

첫 구현은 `cache provenance 보존`이 맞다.

이유:

- 현재 구조를 거의 깨지 않는다.
- 사용자 신뢰도와 제품 완성도를 동시에 올린다.
- 이후 모드 분리와 retrieval 개선의 전제 조건이 된다.
