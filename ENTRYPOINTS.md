# Entrypoints

앞으로는 실행 진입점을 `play_book.cmd` 하나로 봅니다.

기본 명령:

```bash
play_book.cmd ui
play_book.cmd ask --query "Pod lifecycle 개념을 설명해줘"
play_book.cmd eval
play_book.cmd ragas --dry-run
```

의미:

- `ui`: 로컬 챗봇 UI 실행
- `ask`: 단건 질의 실행
- `eval`: 멀티케이스 답변 평가 실행
- `ragas`: RAGAS 평가 실행

참고:

- `play_book.cmd`는 저장소 `.venv`가 있으면 그 인터프리터를 우선 사용합니다.
- 기존 `scripts/run_part*.py` 파일들은 레거시 진입점입니다.
- 제품 기준 실행 경로는 `play_book.cmd`만 따라가면 됩니다.
