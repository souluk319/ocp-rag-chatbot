# Part 3. Echo Multi-turn Plan

## Chapter 3.1 목표

멀티턴 10회 이상에서도 follow-up 해석, 참조 해결, step-by-step 응답 안정성을 유지한다.

## Chapter 3.2 현재 진단

### 현재 강점

- follow-up rewrite 휴리스틱이 이미 있다.
- 세션 상태 객체가 최소 슬롯 구조로 존재한다.
- 세션 히스토리는 서버에 유지된다.

### 현재 한계

- 답변 프롬프트는 전체 히스토리 대신 `SessionContext` 요약만 사용한다.
- reference candidate 목록이 없다.
- 장기 세션 compaction이 없다.
- `단계별로` 요청을 강제하는 plan state가 없다.

## Chapter 3.3 Session State V2 설계

### 유지 슬롯

- `mode`
- `user_goal`
- `current_topic`
- `open_entities`
- `ocp_version`
- `unresolved_question`

### 추가 슬롯

- `recent_turn_summaries`
- `recent_grounded_facts`
- `reference_candidates`
- `active_plan_state`
- `compaction_epoch`

### 설계 원칙

- raw history를 무한정 넣지 않는다.
- 최근 몇 턴의 요약과 grounded facts를 분리한다.
- follow-up rewrite는 요약이 아니라 참조 후보를 먼저 본다.

## Chapter 3.4 Follow-up Resolution 개선

### 계획

- 지시어 해석 계층을 추가한다.
- 우선순위는 `명시 엔티티 -> 최근 grounded facts -> 최근 citation section -> clarification` 순으로 둔다.
- `그거`, `아까 말한 거`, `3번`, `거기서`, `차이도` 같은 지시형 표현을 별도 규칙군으로 관리한다.

### 기대 효과

- 2~3턴 follow-up뿐 아니라 10턴 이상에서도 주제 전환과 참조 복원이 분리된다.
- 틀린 참조를 억지로 이어붙이는 빈도가 줄어든다.

## Chapter 3.5 Long-session Compaction

### 계획

- 6턴 단위 soft compaction
- 12턴 단위 hard compaction
- compaction 결과는 `recent_grounded_facts`와 `reference_candidates`에 반영
- compaction은 answer text가 아니라 grounded facts 위주로 생성

### 완료 기준

- 12턴 이후에도 follow-up answer quality가 급격히 무너지지 않는다.
- 세션 크기 증가가 프롬프트 길이 폭증으로 이어지지 않는다.

## Chapter 3.6 Step-by-step 안정화

### 계획

- `단계별`, `순서대로`, `하나씩`, `step-by-step`을 전용 intent로 분리한다.
- answer 전에 outline을 먼저 고정하고, 본문은 outline 순서만 채우게 한다.
- ops 모드와 learn 모드의 단계 수를 다르게 한다.
- 단계별 응답에는 각 단계별 근거 citation을 명시적으로 붙인다.

## Chapter 3.7 테스트 영향

- 12턴 follow-up regression 세트
- 참조형 follow-up 해석 테스트
- compaction 전/후 정답 일관성 테스트
- `단계별로` 질문의 구조 안정성 테스트
- 잘못된 참조 상황에서 clarification으로 빠지는 테스트
