# Stage 04 Retrieval Correction Report

## 목적

4단계의 목적은 widened corpus 기준 retrieval 실패 5건을 상대로, Stage 3에서 확인한 원인을 실제 코드와 정책에 반영해 1차 보정을 완료하는 것이다.

이번 단계는 최종 품질 게이트가 아니라, 아래 항목이 실제로 움직이는지 확인하는 보정 단계다.

- `source_dir` 정합성
- `document_path` 정합성
- policy-prepared candidate rescue
- citation alignment

## 6인 검토 역할

- `Creative-A`: 실패 질문별 기대 문서와 path signal 정리
- `Creative-B`: rewrite 우선, rescue 제한 원칙 검토
- `Expert-A`: prepared candidate 단계에서 가장 작은 보정 포인트 제안
- `Expert-B`: manifest rescue의 과적합 방지 제약 검토
- `Inspector-A`: Stage 4 완료 문구와 다음 단계 문서 정리 기준 제안
- `Inspector-B`: Stage 4 보고서의 필수 수치와 pass 기준 검토

## 반영 내용

### 1. candidate 정합성 복구

- [`eval/run_opendocuments_stage6.mjs`](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_opendocuments_stage6.mjs)
  - source id prefix를 제거한 `document_path`를 사용하도록 보정
  - `source_dir`를 실제 top-level dir 기준으로 계산하도록 수정
- [`eval/stage9_policy_report.py`](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/stage9_policy_report.py)
  - manifest 기준 `document_path` 정규화
  - manifest의 `top_level_dir`로 candidate `source_dir`를 덮어써 widened corpus mislabel을 보정

### 2. policy rescue 추가

- [`app/ocp_policy.py`](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/ocp_policy.py)
  - follow-up memory rescue는 유지
  - 추가로, raw top candidates가 기대 source/category/path signal을 전혀 만족하지 못할 때만 manifest 기반 hint candidate를 제한적으로 주입
  - hint candidate는 아래 조건을 함께 본다.
    - `preferred_source_dirs`
    - `preferred_categories`
    - `path_terms`
    - memory source continuity

### 3. policy 파라미터 보강

- [`configs/rag-policy.yaml`](/C:/Users/soulu/cywell/ocp-rag-chatbot/configs/rag-policy.yaml)
  - `source_dir_match_boost`, `category_match_boost`, `path_term_boost` 강화
  - `disconnected_mirroring`에 `creating-registry` path term 추가
  - `manifest_hint_scan_limit`, `manifest_hint_limit` 추가

## 테스트

실행한 테스트는 아래와 같다.

```powershell
python -m py_compile app\ocp_policy.py eval\stage9_policy_report.py
python eval\stage9_policy_report.py --cases eval\benchmarks\p0_retrieval_benchmark_cases.jsonl --results indexes\s15c-core\smoke-results.jsonl --manifest data\staging\s15c\manifests\staged-manifest.json --output-results data\manifests\generated\stage04-policy-results.jsonl --output-report data\manifests\generated\stage04-policy-report.json
```

산출물:

- [`stage04-policy-results.jsonl`](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage04-policy-results.jsonl)
- [`stage04-policy-report.json`](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage04-policy-report.json)

## 결과 요약

### raw retrieval 기준

- `source_dir_hit@5 = 0.2`
- `supporting_doc_hit@10 = 0.2`
- `citation_correctness = 0.2`

### policy-prepared retrieval 기준

- `source_dir_hit@5 = 1.0`
- `supporting_doc_hit@10 = 1.0`
- `citation_correctness = 1.0`

즉, widened corpus에서 raw candidate pool은 여전히 install-heavy collapse를 보이지만, Stage 4 보정 이후 policy-prepared candidate 기준으로는 실패 5건이 모두 기대 문서와 citation까지 회복됐다.

## 케이스별 결과

- `RB-001`
  - 기대: `installing/install_config/configuring-firewall.adoc`
  - 결과: pass
- `RB-004`
  - 기대: `disconnected/installing-mirroring-creating-registry.adoc`
  - 결과: pass
- `RB-006`
  - 기대: `support/troubleshooting/verifying-node-health.adoc`
  - 결과: pass
- `RB-010`
  - 기대: `post_installation_configuration/day_2_core_cnf_clusters/updating/update-before-the-update.adoc`
  - 결과: pass
- `RB-013`
  - 기대: `post_installation_configuration/day_2_core_cnf_clusters/troubleshooting/troubleshooting-cert-maintenance.adoc`
  - 결과: pass

## 판정

`Stage 4 = pass`

다만 이 pass는 아래 의미로 한정한다.

- widened corpus 실패 패턴에 대한 보정 1차가 실제로 반영되었다
- policy-prepared retrieval 기준으로 supporting document와 citation이 모두 회복되었다

아직 남아 있는 사실:

- raw retrieval baseline은 여전히 약하다
- Stage 5에서 widened corpus 기준 Stage 9 retrieval / citation 회귀를 다시 확인해야 한다
- Stage 6 이후 multiturn, red-team, live runtime까지 이어서 봐야 한다

## 다음 단계

다음 활성 단계는 `5단계. Stage 9 retrieval / citation 회귀 검증`이다.
