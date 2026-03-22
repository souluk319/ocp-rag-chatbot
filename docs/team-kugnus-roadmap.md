# Team Kugnus Roadmap

`feat/ocp-chatbot-evolution` 브랜치에서 진행하는 고도화 작업의 기준 문서.

## 목표

이 프로젝트를 `데모용 RAG 챗봇`에서 다음 두 역할을 동시에 수행할 수 있는 사내 도구로 끌어올린다.

- 신입사원 교육용 OCP 개념 학습 어시스턴트
- 실제 운영/트러블슈팅 지원 OCP 어시스턴트

단, 다음 원칙은 고정한다.

- `main`은 직접 건드리지 않는다.
- 외부 RAG 프레임워크에 의존하지 않는다.
- 기존에 되는 기능을 무리하게 깨지 않는다.

## 현재 합의된 핵심 문제

1. 교육형 설명과 운영형 진단이 하나의 파이프라인과 하나의 UI 안에서 섞여 있다.
2. 전역 상태가 많다.
   - 전역 LLM endpoint switch
   - 프로세스 메모리 기반 session/cache
3. retrieval이 문서 구조 신호보다 휴리스틱 보정에 더 많이 기대고 있다.
4. trace, rewrite, cache가 답변의 신뢰도를 과장할 수 있다.
5. 평가셋과 품질 게이트가 약하다.

## 구현 순서

### Phase 1. 신뢰성/경계 정리

가장 먼저 할 일:

1. cache hit에서도 source/provenance를 잃지 않게 한다.
2. trace/rewrite/cache 노출을 `답변 근거`가 아니라 `디버그 정보`로 낮춘다.
3. 전역 endpoint switch를 운영 기능이 아니라 개발 기능으로 재정의한다.

이 단계에서 목표는 `더 똑똑해 보이는 것`이 아니라 `오답이 그럴듯해 보이지 않게 만드는 것`이다.

### Phase 2. 교육/운영 분기

UI를 갈아엎기 전에 먼저 계약부터 분리한다.

- `education` 모드
  - 정의
  - 왜 중요한지
  - 핵심 개념
  - 간단 예시
  - 다음 학습 질문

- `operations` 모드
  - 증상 요약
  - 가능한 원인
  - 확인 명령
  - 즉시 조치
  - 주의사항
  - 출처

초기에는 얕은 mode 분기만 넣고, 나중에 retrieval/ranking 정책으로 확장한다.

### Phase 3. Retrieval 구조 강화

우선 모델을 바꾸는 게 아니라 metadata를 늘린다.

추가 후보 metadata:

- `doc_kind`
- `section_type`
- `heading_path`
- `lang`
- `has_command`
- `has_yaml`
- `has_error_pattern`

그다음 query-type aware ranking을 넣는다.

- 개요/개념 질문: intro/concept/example 우대
- 운영/트러블슈팅 질문: procedure/troubleshooting/command 우대

### Phase 4. 상태 외부화

현재 클래스 경계를 유지한 채 저장소만 교체한다.

- session: 외부 저장소로 이동
- cache: provenance 포함해 외부 저장소로 이동

벡터 검색과 LLM 계층은 최대한 그대로 둔다.

### Phase 5. 품질 게이트 고정

질문셋을 최소 4종으로 나눈다.

- 교육 개념 질문
- 운영 절차 질문
- 개요/비교 질문
- 트러블슈팅 질문

초기 측정 항목:

- `Recall@5`
- `Top1 source correctness`
- `rewrite precision`
- `false cache hit rate`
- `unsupported claim rate`

## 지금 바로 해도 되는 저위험/고효과 변경

1. cache provenance 보존
2. query type을 trace/eval 전용으로 먼저 수집
3. retrieval metadata를 기록용으로 먼저 확장

## 지금 당장 하면 안 되는 것

1. UI 토글만 먼저 넣는 교육/운영 분리
2. 평가셋 없이 ranking heuristic을 더 복잡하게 만드는 일
3. trace를 더 화려하게 전면 노출하는 UX 개선

## Team Kugnus 역할

- Planck: 제품 원칙과 단계별 구조 정리
- Euclid: retrieval/search 품질 백로그 정리
- Galileo: 교육/운영 UX 흐름과 답변 형식 정리
- Russell: 실패 가능성과 위험한 착시를 비판적으로 검토

## 첫 구현

첫 구현 항목은 `cache provenance 보존`이다.

이유:

- 위험이 낮다.
- 사용자가 cached 응답에서도 출처를 잃지 않는다.
- 이후 교육/운영 분기와 trace 정리의 기반이 된다.
