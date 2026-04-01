# DEPLOYMENT 도메인 가이드

## 개요
`deployment/`는 폐쇄망 운영 흐름 전체를 책임진다. 사전 준비 상태 점검, 번들 생성/승인, 반입 스테이징, 재인덱싱, 스모크, 활성화, 롤백이 모두 여기에 속한다.

## 어디를 봐야 하나
| 작업 | 위치 | 메모 |
|------|------|------|
| 범위 요약 | `README.md` | 진입점과 현재 단계 범위 |
| 준비 상태 게이트 | `check_stage11_readiness.py`, `stage11-readiness.md` | Stage 11 선행조건 |
| 번들 생성/승인 | `build_outbound_bundle.py`, `approve_bundle.py`, `validate_bundle.py` | 승인 메타데이터가 중요 |
| 반입 스테이징 | `stage_bundle_for_indexing.py`, `reindex_staged_bundle.py` | 가져오기는 승인 상태를 존중해야 함 |
| 활성화/롤백 | `activate_index.py`, `rollback_index.py`, `stage11_activation_utils.py` | 이전 정상 상태를 보존 |
| 라이브 스모크 | `run_live_runtime_smoke.py`, `run_activation_smoke.py` | 서빙 경로 증거 |
| 운영자 런치 | `start_runtime_stack.py`, `operator-runbook-stage14.md` | 원커맨드 Stage 14 런치 경로 |
| 계약/런북 | 이 디렉터리 아래 `*.md`, `*.yaml` | 운영 권위 문서로 취급 |

## 로컬 규칙
- 배포 변경은 계약 중심으로 다룬다. 스크립트를 바꾸기 전에 대응하는 계약/런북 문서를 먼저 본다.
- 승인 상태는 파일명 추정이 아니라 명시적인 JSON 메타데이터다.
- 활성화는 반드시 롤백 가능성을 보존해야 한다. `current`, `previous`, `archive` 동작도 정합성의 일부다.
- 단계 이름 체계는 중요하다. 스크립트와 보고서는 의도적으로 Stage 11/12/14 흐름을 반영한다.

## 안티패턴
- 편의상 검증이나 승인 체크를 생략하지 않는다.
- 이전 정상 상태를 남기지 않은 채 active index pointer를 덮어쓰지 않는다.
- 대응하는 단계 문서가 아니라고 말하는데도 스모크 보고서를 권위 문서처럼 취급하지 않는다.
- 임시방편식 번들 레이아웃을 도입하지 않는다. 번들 구조는 계약으로 고정되어 있다.

## 변경 체크리스트
- 수정 전 `deployment/README.md`와 관련 계약/런북을 다시 읽는다.
- 배포 경로 의미가 바뀌면 단계 문서와 증거 참조도 같이 갱신한다.
- 재현 가능성을 지킨다. 경로, 매니페스트, 체크섬, 승인 필드, 보고서 출력은 안정적으로 유지되어야 한다.
