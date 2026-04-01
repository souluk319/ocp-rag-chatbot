# Stage 6: Multiturn / Red-Team Regression

## 목표

Stage 5 widened corpus retrieval 보정이 멀티턴 메모리와 red-team 안전성 규칙을 해치지 않았는지 확인한다.

이 단계는 다음 질문에 답한다.

- follow-up continuity 가 여전히 안정적인가
- topic shift 가 이전 문맥을 제대로 끊는가
- red-team 질문에서 제품 경계, 버전 경계, 보수적 응답 규칙이 유지되는가
- Stage 10 스타일의 통합 판정으로 현재 상태를 `go / no-go` 로 말할 수 있는가

## 6인 검토 관점

- `Creative-A`: widened corpus 에서도 follow-up 은 같은 문서군을 유지하고, topic shift 는 이전 문맥을 과감히 버려야 한다.
- `Creative-B`: red-team pass 는 정답처럼 보이는 문장보다 정직함, 제품 경계, 버전 경계, 위험 고지, citation 검증 가능성을 강조해야 한다.
- `Expert-A`: multiturn 회귀는 runtime 이 아니라 `SessionMemoryManager` 자체를 직접 평가하는 현재 경로가 가장 깨끗하다.
- `Expert-B`: red-team 회귀는 corpus/index 노이즈를 빼고 현재 policy 구현만 직접 보는 것이 가장 분리도가 높다.
- `Inspector-A`: Stage 6 완료에는 multiturn 상세, red-team 상세, 종합 gate 파일, 사람 읽는 요약 문서가 함께 있어야 한다.
- `Inspector-B`: Stage 6 go/no-go 초안은 Stage 5 retrieval gate + follow-up retrieval gate + multiturn gate + red-team gate 를 같이 묶어야 한다.

## 실행 명령

```powershell
python -m py_compile eval\run_stage06_regression.py
python eval\run_stage06_regression.py
```

## 산출물

- runner: [run_stage06_regression.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_stage06_regression.py)
- multiturn detail: [stage06-multiturn-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-multiturn-report.json)
- red-team detail: [stage06-red-team-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-red-team-report.json)
- combined suite: [stage06-suite-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-suite-report.json)
- combined summary: [stage06-regression-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-regression-summary.json)

## 결과 요약

### Multiturn

- `scenario_count = 2`
- `turn_count = 10`
- `fully_passing_scenarios = 2`
- `classification_pass_rate = 1.0`
- `source_dir_pass_rate = 1.0`
- `topic_pass_rate = 1.0`
- `version_pass_rate = 1.0`

해석:

- follow-up continuity 는 유지됐다.
- topic shift 는 widened corpus retrieval 보정 이후에도 정상적으로 이전 문맥을 끊는다.
- version continuity 는 침묵 없이 유지된다.

### Red-team

- `case_count = 7`
- `passed_count = 7`
- `failed_case_ids = []`

group별 결과:

- `weak grounding = 1.0`
- `product contamination = 1.0`
- `mixed version = 1.0`
- `high risk change = 1.0`
- `topic drift = 1.0`
- `follow-up continuity = 1.0`
- `version ambiguity = 1.0`

해석:

- 근거 부족 시 보수적 응답이 유지된다.
- OCP / ROSA 혼합을 막는다.
- 버전 힌트와 버전 불확실성 고지를 유지한다.
- 고위험 질문에 주의 문구와 citation 요구가 살아 있다.

### Combined Stage 10-style gate

- `retrieval_first_slice_gate = true`
- `multiturn_gate = true`
- `context_traceability_gate = true`
- `red_team_gate = true`
- `follow_up_retrieval_gate = true`
- `overall_decision = go`

## 판정

Stage 6 overall: **pass**

근거:

- Stage 5 widened corpus retrieval gate 유지
- multiturn 5턴 시나리오 전부 통과
- red-team 7건 전부 통과
- follow-up retrieval gate 유지
- known blocker 없음

## 남은 메모

- raw widened corpus retrieval baseline 이 약한 문제는 Stage 5에서 이미 확인된 진단 리스크로 남아 있다.
- Stage 6는 그 약점이 multiturn / red-team 안전장치를 깨뜨리지 않았음을 확인한 단계다.
- 다음 단계는 `7단계. refresh / activate / rollback 재검증` 이다.
