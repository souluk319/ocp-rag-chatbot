# Stage 5: Stage 9 Retrieval / Citation Regression

## 목표

확장된 `s15c-core` 코퍼스 기준으로 Stage 9 retrieval / citation 회귀를 다시 돌려,
`policy-prepared retrieval` 이 widened corpus 에서도 운영 게이트를 만족하는지 확인한다.

## 범위

- benchmark cases: [`p0_retrieval_benchmark_cases.jsonl`](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/benchmarks/p0_retrieval_benchmark_cases.jsonl)
- corpus manifest: [`staged-manifest.json`](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/staging/s15c/manifests/staged-manifest.json)
- active widened corpus workspace: `indexes/s15c-core/.stage05-workspace`
- reused data dir: `indexes/s15c-core/.activation-smoke-data`

## 실행 명령

```powershell
python -m py_compile eval\run_stage05_regression.py
python eval\run_stage05_regression.py --reuse-existing-data-dir
```

Stage 5 중간에 widened corpus 전체 재인덱싱 시간이 과도하게 길어지는 문제가 확인되어,
기존 활성 데이터 디렉터리를 재사용하는 `--reuse-existing-data-dir` 모드로 회귀 게이트를 고정했다.

## 핵심 산출물

- raw results: [`stage05-raw-results.jsonl`](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-raw-results.jsonl)
- policy results: [`stage05-policy-results.jsonl`](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-policy-results.jsonl)
- policy report: [`stage05-policy-report.json`](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-policy-report.json)
- combined summary: [`stage05-regression-summary.json`](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-regression-summary.json)

## 결과 요약

### Raw retrieval baseline

- `case_count = 13`
- `source_dir_hit@5 = 0.0`
- `supporting_doc_hit@10 = 0.0`

raw retrieval 은 widened corpus 에서 여전히 매우 약하며,
이 수치는 운영 게이트가 아니라 진단용 baseline 으로 본다.

### Policy-prepared retrieval

- `case_count = 13`
- `source_dir_hit@5 = 0.9231`
- `supporting_doc_hit@10 = 0.9231`
- `citation_correctness = 0.9231`

이 값은 [`retrieval-benchmark-plan.md`](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/retrieval-benchmark-plan.md)
에 정의된 widened corpus 게이트를 만족한다.

## 게이트 판정

- `source_dir_hit@5 >= 0.85`: pass
- `supporting_doc_hit@10 >= 0.75`: pass
- `citation_correctness >= 0.90`: pass
- Stage 5 overall: **pass**

## 남은 리스크

- `RB-003` 는 widened corpus 의 disconnected mirroring 계열에서 아직 미해결 케이스다.
- raw retrieval baseline 이 `0.0` 이라서, 현재 품질은 policy-prepared retrieval 과 metadata rescue 에 크게 의존한다.
- 따라서 Stage 6 이후에도 raw recall 개선은 계속 추적해야 한다.

## 결론

Stage 5는 widened corpus 전체 13개 케이스 기준에서
`policy-prepared retrieval` 의 retrieval / citation 회귀 게이트를 통과했다.
다음 활성 단계는 `6단계. multiturn / red-team 회귀 검증` 이다.
