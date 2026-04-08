# Entrypoints

앞으로는 실행 진입점을 `play_book.cmd` 하나로 봅니다.

공식 기준 경로:

- `play_book.cmd`
- `scripts/play_book.py`
- `scripts/check_runtime_endpoints.py`
- `scripts/build_source_manifest.py`
- `scripts/build_source_approval.py`
- `scripts/run_ingestion.py`
- `scripts/run_retrieval_eval.py`
- `scripts/run_answer_eval.py`
- `scripts/run_ragas_eval.py`

기본 명령:

```bash
play_book.cmd ui
play_book.cmd ask --query "Pod lifecycle 개념을 설명해줘"
play_book.cmd eval
play_book.cmd ragas --dry-run
play_book.cmd runtime
```

의미:

- `ui`: 로컬 챗봇 UI 실행
- `ask`: 단건 질의 실행
- `eval`: 멀티케이스 답변 평가 실행
- `ragas`: RAGAS 평가 실행
- `runtime`: 현재 활성 runtime / artifact / endpoint readiness report 생성

보조 스크립트:

- `build_source_manifest.py`: published Korean source catalog 갱신 + slug diff 기록
- `build_source_approval.py`: source catalog -> approved runtime manifest 생성
- `run_ingestion.py`: 문서 수집/정규화/청킹/임베딩 적재
- `run_retrieval_query.py`: 검색 파이프라인 단건 확인
- `run_retrieval_sanity.py`: retrieval sanity gate
- `run_retrieval_eval.py`: retrieval eval
- `run_answer_query.py`: 답변 파이프라인 단건 확인
- `run_answer_eval.py`: answer eval
- `run_ragas_eval.py`: RAGAS eval

참고:

- `play_book.cmd`는 저장소 `.venv`가 있으면 그 인터프리터를 우선 사용합니다.
- 일회성 디버그 스크립트, 로그, 검증 리포트는 `tmp/` 아래에만 둡니다.
- 제품 기준 실행 경로는 `play_book.cmd`만 따라가면 됩니다.

freeze 기준:

- 새 `run_part*` 스크립트는 더 이상 만들지 않습니다.
- 새 top-level shim 파일은 더 이상 만들지 않습니다.
- 새 실행 명령은 `play_book.cmd` 또는 기능명 기준 `scripts/run_*` 아래로만 추가합니다.
