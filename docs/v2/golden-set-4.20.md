# Golden Set 100 for OCP 4.20

## 목적

이 문서는 `enterprise-4.20` 기준 OCP RAG 평가 질문 세트를 정의합니다.  
Golden Set은 코퍼스 범위, retrieval 성능, 답변 정확도, citation 정확도를 모두 검증하는 **절대 기준 자산**입니다.

## 고정 소스 기준

1. 공식 원천 저장소: `https://github.com/openshift/openshift-docs.git`
2. 고정 브랜치: `enterprise-4.20`
3. 로컬 고정 worktree: `C:\Users\soulu\cywell\openshift-docs-4.20`
4. 현재 고정 커밋: `683c38e6291e20bf951edff517b15810f5ce7abc`

## 질문 세트 파일

- [C:\Users\soulu\cywell\ocp-rag-chatbot\eval\benchmarks\golden_set_100.csv](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/benchmarks/golden_set_100.csv)

## 각 문항의 필수 항목

1. `question_ko`
2. `intent_category`
3. `expected_source_scope`
4. `expected_answer_shape`

추가로 `id`, `group`, `scope_policy` 를 둬서 평가 자동화와 범위 밖 테스트를 쉽게 합니다.

## 질문 구성 원칙

1. 한국어 질문 기준
2. 설치/업데이트/운영 질문 비중 강화
3. Disconnected, 복합 설정, 장애 상황 포함
4. 단순 정의 질문만이 아니라 실제 필드 엔지니어 질문 포함
5. `ROSA`, `OSD`, `OCM`, `MicroShift`, `managed service` 관련 범위 밖 질문 포함

## 분포

1. `core_concept`: 10
2. `install_prepare`: 20
3. `disconnected`: 15
4. `update_upgrade`: 18
5. `operations`: 22
6. `out_of_scope`: 15

합계: 100

## Success Criteria

Golden Set 평가는 아래 기준을 만족해야 통과입니다.

1. 검색 재현율(Recall): 90% 이상
2. 답변 정확도(Accuracy): 85% 이상
3. 환각율(Hallucination): 0%
4. 출처 연결 정확도: 100%

## modules와 canonical model

이번 4.20 재설계에서 가장 중요한 점은 `modules/` 관계를 살리는 것입니다.

평가 기준상 반드시 지켜야 할 설계:

1. 상위 가이드 `.adoc`와 `include::modules/...` 관계를 읽는다.
2. `xref:` 를 따라 연결된 후속/보조 가이드를 식별한다.
3. canonical document model은 상위 가이드, 포함 모듈, 참조 링크를 함께 보존한다.
4. 검색은 이 canonical 구조를 기반으로 해야 하고, 답변은 절차가 끊기지 않게 조합해야 한다.
5. citation은 상위 문서와 관련 절차의 실제 위치를 추적할 수 있어야 한다.

## 다음 단계

1. `enterprise-4.20` 기준 균형 코퍼스 설계
2. `modules` / `xref` 관계를 포함한 canonical ingestion 설계
3. Golden Set 100으로 코퍼스 후보군 비교
4. Success Criteria 만족 시에만 런타임에 반영
