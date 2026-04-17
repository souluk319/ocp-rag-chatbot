# Local Worklog

- task_id: `repo_wide_code_inspection_20260417`
- lane_id: `main`
- role: `main`
- major_task: `false`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- inventory: tracked concentration remains `data 184 / src 162 / reports 130 / tests 64 / scripts 57 / presentation-ui 38`
- inventory: largest files remain `curated_gold.py 129650 bytes`, `source_books.py 114333`, `WorkspacePage.tsx 134361`, `PlaybookLibraryPage.tsx 92230`, `test_ingestion_audit.py 98533`, `test_retrieval_runtime.py 86304`
- finding: `test_retrieval_runtime.py` imports in `47.74s`; direct pytest and unittest invocations for even a single selected test exceeded timeout, confirming file-level runtime debt rather than a narrow test failure
- finding: `test_ingestion_audit.py` still contains `17` `TemporaryDirectory` blocks inside a single `Part1AuditTests` class; `test_app_viewers.py` contains `23`
- action: added `SeededBm25` support helper and replaced every inline `StubBm25` in `test_retrieval_runtime.py`; remaining inline count is `0`
- action: removed dead imports from `_support_retrieval.py`
- action: split retrieval runtime monolith into `tests/test_retrieval_runtime.py` (reranker-focused, `15` tests), `tests/test_retrieval_runtime_core.py` (`10` tests), and `tests/test_retrieval_runtime_graph_trace.py` (`11` tests)
- measurement: `tests/test_retrieval_runtime.py` dropped from `86304` bytes to `54839`; new focused files measure `20094` and `14663` bytes; reranker import timing dropped to `26.58s`, while core/graph focused imports are `0.01s`
- validation: sequential pytest now passes for all three retrieval files: reranker `15 passed in 35.63s`, core `10 passed in 19.46s`, graph trace `11 passed in 7.94s`
- note: parallel pytest execution of all three files still hit timeout due concurrent startup/resource contention, so packet validation is recorded as sequential
- validation: frontend lint/test/build passed after the split
- hygiene: post-validation cleanup removed `13` regenerated junk targets totaling `2,393,089` bytes and restored workspace junk count to `0`
