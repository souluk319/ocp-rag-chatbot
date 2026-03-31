# Stage 1 완료 보고서

## 단계명

검증 입력 정합성 복구

## 목표

깨진 한국어 fixture를 복구해서 retrieval, multiturn, red-team, live runtime smoke가 모두 **신뢰 가능한 입력**으로 돌아가게 만드는 것이다.

## 적용 범위

- `deployment/live_runtime_smoke_cases.json`
- `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`
- `eval/benchmarks/p0_red_team_cases.jsonl`
- `eval/benchmarks/p0_multiturn_scenarios.json`

## 6인 역할

- `Creative-A`: live smoke / multiturn 질문 자연스러움 검토
- `Creative-B`: retrieval / red-team 질문 자연스러움 검토
- `Expert-A`: ID, 기대 문서 경로, source/category 정합성 검토
- `Expert-B`: runner 호환성과 필드 보존 여부 검토
- `Inspector-A`: UTF-8, JSON/JSONL 파싱, 잔여 mojibake 검사
- `Inspector-B`: Stage 1 완료 증거와 체크리스트 점검

## 수행 내용

- 깨진 한국어 질문과 설명을 자연스러운 UTF-8 한국어로 복구했다.
- fixture의 ID, 기대 문서 경로, 기대 source/category, 시나리오 구조는 유지했다.
- Stage 1 전용 검사 스크립트를 복구했다.
  - `eval/check_stage01_fixture_integrity.py`

## 테스트

### 파싱 테스트

- `deployment/live_runtime_smoke_cases.json`: JSON 파싱 통과
- `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`: 13개 행 파싱 통과
- `eval/benchmarks/p0_red_team_cases.jsonl`: 7개 행 파싱 통과
- `eval/benchmarks/p0_multiturn_scenarios.json`: JSON 파싱 통과

### 입력 무결성 테스트

- `python eval/check_stage01_fixture_integrity.py`
- 결과: `pass`
- 산출물: `data/manifests/generated/stage01-fixture-integrity-report.json`

### runner 호환성 테스트

- `python -m py_compile eval/retrieval_benchmark_report.py eval/multiturn_rewrite_report.py eval/stage10_red_team_report.py deployment/run_live_runtime_smoke.py`
- 결과: 통과

## 검증 결론

Stage 1은 완료로 판정한다.

판정 근거:

- live smoke, retrieval, red-team, multiturn 입력 질문이 정상 한국어로 복구됐다.
- fixture 구조가 runner 기대 형태를 유지했다.
- Stage 1 검사 스크립트 기준 `issues = []` 를 확인했다.

## 정리 메모

- Stage 1은 **입력 fixture 정합성 복구**만 다룬다.
- retrieval 품질 개선, 런타임 경로 진위 확인, widened corpus 회귀 검증은 다음 단계에서 다룬다.

## 다음 단계

다음 활성 단계는 **2단계. 런타임 경로 진위 검증**이다.
