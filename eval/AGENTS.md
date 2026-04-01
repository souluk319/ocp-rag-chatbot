# EVAL 도메인 가이드

## 개요
`eval/`은 품질 게이트와 회귀 검증 증거를 담당한다. 검색 평가, 멀티턴, 레드팀, 문맥 유지, Stage 10 릴리즈 집계가 여기에 들어간다.

## 어디를 봐야 하나
| 작업 | 위치 | 메모 |
|------|------|------|
| 범위 요약 | `README.md` | 여기서 무엇이 권위인지 설명 |
| 최종 릴리즈 게이트 | `run_stage10_release_gate.py`, `stage10_suite.py` | 앞선 게이트를 집계 |
| 검색 회귀 검증 | `run_stage05_regression.py`, `retrieval_benchmark_report.py` | Stage 5 권위 |
| 멀티턴/레드팀 | `run_stage06_regression.py`, `multiturn_rewrite_report.py`, `stage10_red_team_report.py` | Stage 6 권위 |
| 문맥 유지 | `context_harness_report.py`, `context-harness-schema.yaml` | 대화 메모리 점검 |
| 픽스처와 진실 원천 구분 | `fixtures/` | 샘플일 뿐 현재 게이트 권위는 아님 |

## 로컬 규칙
- 안정적인 샘플 픽스처와 `data/manifests/generated/` 아래의 권위 있는 생성 출력은 명확히 구분한다.
- 평가 코드는 단계 의미를 보존해야 한다. Stage 5/6/10 이름은 임의가 아니라 의미를 가진다.
- 벤치마크와 스키마 파일도 계약의 일부다. 조용한 구조 변형보다 의도적인 스키마 확장을 선호한다.

## 안티패턴
- 픽스처 스냅샷을 현재 검증 결과처럼 다루지 않는다.
- `docs/v2/`의 통제 문서를 갱신하지 않은 채 지표 의미나 기대 필드를 바꾸지 않는다.
- 원시 검색 결과와 정책 보정 검색 결과를 하나의 불투명한 점수로 뭉개지 않는다.

## 변경 체크리스트
- `docs/v2/evaluation-spec.md`와 해당 동작을 소유한 단계 보고서를 함께 대조한다.
- 게이트가 바뀌면 러너와 증거/보고 경로를 둘 다 갱신한다.
- 출력은 기계가 읽을 수 있어야 한다. JSON 보고서는 downstream에서 증거로 사용된다.
