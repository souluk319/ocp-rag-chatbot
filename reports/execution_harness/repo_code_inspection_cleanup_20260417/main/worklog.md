# Local Worklog

- task_id: `repo_code_inspection_cleanup_20260417`
- lane_id: `main`
- role: `main`
- major_task: `false`
- user-visible progress는 milestone 종료 전까지 기록하지 않는다.
- 중간 자동 복구, 실행 메모, 임시 판단은 이 파일에만 적는다.
- action: introduced shared `wikiVision` contract in frontend and replaced page-local duplicated mode metadata
- action: fixed dead vision persistence path by loading stored `wikiVisionMode` instead of always forcing `atlas_canvas`
- action: moved repeated fake reranker scaffolding for retrieval runtime tests into `_support_retrieval.py` and removed seven inline copies
- evidence: `presentation-ui` vitest suite increased from 6 to 9 passing tests after adding `wikiVision.test.ts`
- evidence: changed-path retrieval reranker subset passed `7 passed, 29 deselected`; full `tests/test_retrieval_runtime.py -q` exceeded 300s and remains a file-size/runtime debt
- hygiene: post-validation cleanup removed 11 regenerated junk targets totaling `1,486,124` bytes and restored workspace junk count to zero
