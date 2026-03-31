# Stage 1 완료 보고서 - 검증 입력 정합성 복구

## 단계 목표

Stage 1의 목표는 깨진 한국어 검증 입력을 복구해서 retrieval, multiturn, red-team, live runtime smoke 결과를 신뢰 가능한 상태로 만드는 것이다.

## 적용 범위

- `deployment/live_runtime_smoke_cases.json`
- `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`
- `eval/benchmarks/p0_red_team_cases.jsonl`
- `eval/benchmarks/p0_multiturn_scenarios.json`

## 6인 역할 배정

- `Creative-A`: live smoke / multiturn 질문 자연어 품질 검토
- `Creative-B`: retrieval / red-team 질문 자연어 품질 검토
- `Expert-A`: ID, 기대 문서 경로, 메타데이터 정합성 검토
- `Expert-B`: runner 호환성과 필드 보존성 검토
- `Inspector-A`: JSON / JSONL / UTF-8 / 잔여 mojibake 검사
- `Inspector-B`: Stage 1 완료 증거 체크리스트 검토

## 작업 내용

- 깨진 한국어 질문과 설명을 자연스러운 한국어로 복구
- ID, 기대 source, 기대 문서 경로, 시나리오 구조는 유지
- 테스트 로직에 직접 쓰이는 영문 키워드는 유지
- UTF-8 파싱과 줄 수를 다시 검증

## 테스트

### 파싱 테스트

- `deployment/live_runtime_smoke_cases.json`: JSON 파싱 성공
- `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl`: JSONL 13줄 파싱 성공
- `eval/benchmarks/p0_red_team_cases.jsonl`: JSONL 7줄 파싱 성공
- `eval/benchmarks/p0_multiturn_scenarios.json`: JSON 파싱 성공

### 문자열 검증

- live smoke 질문 2개를 UTF-8로 직접 로드해 한국어 정상 출력 확인
- retrieval benchmark 질문 13개를 UTF-8로 직접 로드해 한국어 정상 출력 확인
- red-team 질문과 memory turns를 UTF-8로 직접 로드해 한국어 정상 출력 확인
- multiturn turns를 UTF-8로 직접 로드해 한국어 정상 출력 확인

### 재현 가능한 검증 스크립트

- `python -m py_compile eval/check_stage01_fixture_integrity.py`
- `python eval/check_stage01_fixture_integrity.py`

생성 리포트:

- `data/manifests/generated/stage01-fixture-integrity-report.json`

## 검증 결론

Stage 1은 현재 기준으로 **완료**다.

- 네 개의 입력 fixture는 UTF-8 기준으로 정상 파싱된다.
- 질문 문자열은 한국어 기준으로 직접 로드했을 때 정상 출력된다.
- `U+FFFD` replacement character가 남아 있지 않다.
- retrieval benchmark 13건, red-team 7건, multiturn 2개 시나리오 10턴, live smoke 2건이 모두 구조를 유지한다.

## 정리 메모

- Stage 1은 **입력 fixture 정합성**만 다룬다.
- runtime 코드 보강과 retrieval 품질 개선은 Stage 2 이후에서 다룬다.
- 다음 활성 단계는 `2단계. 런타임 경로 진위 검증` 이다.
