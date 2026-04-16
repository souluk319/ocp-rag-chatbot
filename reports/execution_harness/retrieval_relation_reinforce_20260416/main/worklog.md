# Local Worklog

- task_id: `retrieval_relation_reinforce_20260416`
- lane_id: `main`
- role: `main`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- retrieval miss 4건(`learn-002`, `learn-003`, `learn-004`, `ambiguous-001`)과 `applied_playbook` latest-only 누락 조건을 먼저 확인했다.
- `retriever_pipeline.py` latest-only filter 에서 `source_lane == official_ko` 강제를 제거해 active approved core playbook 을 retrieval 대상에 유지했다.
- `intent_patterns.py`, `intents.py`, `query_terms_core.py` 에 observability compare / operator / MCO 개념 확장 용어를 추가했다.
- `book_adjustment_discovery_concepts.py` 에 observability compare, logging ambiguity, operator/MCO concept 전용 boost/penalty 를 추가했다.
- `py_compile` 검증 통과 후 `run_retrieval_eval.py` 를 다시 실행했고 `book_hit_at_1=1.0`, `book_hit_at_5=1.0`, `misses_at_5=[]` 를 확인했다.
