# Quickstart

이 문서는 `OCP Playbook Studio`를 시연하거나 운영 점검할 때 가장 짧은 순서를 적는다.

## 1. 런타임 상태 확인

```bash
play_book.cmd runtime
```

확인 결과:

- 현재 앱/pack 정체성
- LLM / embedding / Qdrant probe
- 핵심 artifact 존재 여부
- 최근 채팅 로그와 runtime snapshot

기본 출력 파일:

- `settings.runtime_report_path`

## 2. 소스 catalog / 승인 manifest 갱신

```bash
python scripts/build_source_manifest.py
python scripts/build_source_approval.py
```

이 단계는 `docs.redhat.com` published Korean source catalog와 runtime approved manifest를 다시 맞춘다.

## 3. 코퍼스 재생성

```bash
python scripts/run_ingestion.py --collect-subset all --process-subset all
```

빠른 회사 TEI 서버가 있으므로 재정규화/재청킹/재임베딩 루프를 반복할 수 있다.

## 4. 기본 동작 확인

```bash
play_book.cmd ask --query "Pod lifecycle 개념을 초보자 관점에서 설명해줘"
play_book.cmd ui
```

## 5. 평가

```bash
play_book.cmd eval
play_book.cmd ragas --dry-run
python scripts/run_retrieval_eval.py
```

## 운영 기준선

- canonical entrypoint는 `play_book.cmd`
- legacy `run_part*` 스크립트는 더 이상 추가하지 않는다
- 일회성 실험 스크립트와 로그는 `tmp/` 아래에만 둔다
- session은 memory-only지만, `chat_turns.jsonl` 에 per-turn runtime snapshot이 남아 재현 기준으로 쓴다
