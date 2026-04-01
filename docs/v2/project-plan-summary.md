# v2 프로젝트 계획 및 현황

이 문서는 제품 소개가 아니라, 현재 작업 브랜치의 진행 현황과 다음 작업을 빠르게 파악하기 위한 계획 문서입니다.

## 브랜치 의도

현재 기준 브랜치는 `feat/OCP_v2_planB` 이며, v1 런타임을 이어받아 확장하는 브랜치가 아니라 **OpenDocuments 파이프라인을 기준으로 OCP 운영 가이드 챗봇을 직접 완성하기 위한 브랜치**다.

- v1 런타임과 예전 UI는 제거
- `release/v1` 와 `v1.0` 태그로 이전 버전 보존
- v2 는 OpenDocuments 기준 구조와 OCP 전용 파이프라인으로 재구성
- 공식 평가 데이터 기준은 `openshift-docs` `enterprise-4.20`
- 생성 모델 기준은 `Qwen/Qwen3.5-9B`, 임베딩 기준은 `BAAI/bge-m3`
- 핵심 평가는 정확한 일처리, 설계력, 5턴 이상 멀티턴 안정성이다

## 현재 검증 상태

- Stage 3 widened corpus retrieval root-cause 분석 완료
- Stage 10 평가 게이트 `go`
- Stage 11 validated slice 기준 local refresh loop 검증 완료
- Stage 12 live runtime baseline 검증 완료
- Stage 13 source profile / git lineage abstraction 완료
- Stage 14 one-command operator launch path 검증 완료
- Stage 15 core validation corpus 확대 및 delta activation 완료

## 현재 제품 기준

- 공식 평가 기준 문서 원천은 `openshift-docs` `enterprise-4.20` 브랜치다.
- 이 저장소는 `OpenDocuments` 파이프라인을 기준으로 삼되, OCP 운영 챗봇 제품 레이어와 멀티턴 구조는 직접 설계한다.
- LangSmith 같은 완성형 외부 제품에 기대어 평가를 위임하는 대신, 저장소 내부의 retrieval / multiturn / red-team / runtime gate 로 직접 증명한다.
- 목표는 “문서 검색기”가 아니라 **5턴 이상 멀티턴이 가능한 OCP 운영 가이드 챗봇**이다.

현재 확보된 기준은 다음과 같습니다.

- citation 은 raw `.adoc` 대신 생성된 HTML 로 연결
- Stage 9 policy-prepared retrieval 은 고정 benchmark set 에서 높은 supporting-doc / citation 정확도 확보
- multiturn replay 는 5턴 시나리오 기준 통과
- runtime endpoint / model 설정은 env 기반으로만 사용
- validation mode 와 future operator-release mode 를 source profile 로 분리
- active Stage 11 index 를 기준으로 bridge -> OpenDocuments -> gateway 를 한 번에 띄우는 운영 진입점 확보
- `main` 기반 core validation corpus `1201`문서 생성 및 `s15c-core` 활성화 검증 완료

## 다음 마일스톤

1. **5턴 이상 멀티턴 시나리오 확장**
   - 현재 통과 기준을 2개 시나리오 수준에서 끝내지 말고, 운영형 5턴+ 시나리오 세트로 확장
2. **follow-up rewrite / session memory 정교화**
   - 문서 연속성, 버전 연속성, 주제 전환 복구를 더 안정적으로 만듦
3. **운영 질문 중심 retrieval 품질 강화**
   - 설치/업데이트/장애대응/폐쇄망 질문에 대해 source/category/path bias 를 더 정밀하게 보정
4. **직접 설계한 평가 체계 강화**
   - retrieval / multiturn / red-team / runtime / activation evidence 를 하나의 제품 품질 관점으로 재정렬
5. **widened validation serving hardening**
   - Stage 11 smoke, bridge 기반 runtime, widened validation corpus 사이의 정합성을 더 촘촘히 맞춘다
6. **운영자 사용성 개선**
   - launch, smoke, evidence, rollback 흐름을 운영자 관점에서 더 짧고 명확하게 정리
7. **release-grade hardening**
   - target-minor 운영 기준 확정, corpus 확장, raw retrieval baseline 보강, operator release rehearsal 정리

## 핵심 설계 문서

- `docs/v2/architecture-blueprint.md`
- `docs/v2/execution-roadmap.md`
- `docs/v2/source-scope.md`
- `docs/v2/source-profile-layer.md`
- `docs/v2/evaluation-spec.md`
- `docs/v2/requirements-traceability.md`

## Stage 11 관련 운영 진입점

Stage 11 activation 전에 baseline 초기화와 readiness gate 를 먼저 확인합니다.

```powershell
python deployment/initialize_stage11_baseline.py
python deployment/check_stage11_readiness.py
```

현재 검증된 front-half 흐름:

```powershell
python deployment/build_outbound_bundle.py --mode seed --bundle-id stage11-local-seed --force
python deployment/approve_bundle.py --bundle data/packages/outbound/stage11-local-seed --status approved --reviewer codex-local
python deployment/validate_bundle.py data/packages/outbound/stage11-local-seed --require-approved
Copy-Item -Recurse -Force data/packages/outbound/stage11-local-seed data/packages/inbound/stage11-local-seed
python deployment/validate_bundle.py data/packages/inbound/stage11-local-seed --require-approved
python deployment/stage_bundle_for_indexing.py data/packages/inbound/stage11-local-seed --force
```

현재 검증된 back-half 흐름:

```powershell
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id baseline-openshift-docs-p0 --force --output data/manifests/generated/stage11-baseline-reindex-report.json
python deployment/run_activation_smoke.py --index baseline-openshift-docs-p0 --output data/manifests/generated/stage11-baseline-smoke-report.json
python deployment/activate_index.py --index baseline-openshift-docs-p0 --bootstrap-current --operator codex-local --smoke-report data/manifests/generated/stage11-baseline-smoke-report.json --reindex-report data/manifests/generated/stage11-baseline-reindex-report.json --output data/manifests/generated/stage11-baseline-activation-report.json
python deployment/reindex_staged_bundle.py data/staging/stage11-local-seed --index-id stage11-local-seed --force --output data/manifests/generated/stage11-seed-reindex-report.json
python deployment/run_activation_smoke.py --index stage11-local-seed --output data/manifests/generated/stage11-seed-smoke-report.json
python deployment/activate_index.py --index stage11-local-seed --operator codex-local --smoke-report data/manifests/generated/stage11-seed-smoke-report.json --reindex-report data/manifests/generated/stage11-seed-reindex-report.json --output data/manifests/generated/stage11-seed-activation-report.json
python deployment/rollback_index.py --operator codex-local --output data/manifests/generated/stage11-seed-rollback-report.json
```

## 참고

제품 설명은 루트 `README.md` 에서 확인하고, 이 문서는 구현 진행과 단계별 작업 판단 기준을 보는 용도로 사용합니다.

## 2026-03-31 Stage 4 Update

- Stage 4: widened corpus 실패 패턴을 기준으로 retrieval 보정 1차 반영 완료
- 반영 범위:
  - `source_dir/document_path` 정합성 복구
  - manifest 기반 제한적 hint rescue
  - disconnected/update/certificate/node-health 계열 path term 보강
- 결과:
  - raw retrieval 기준 `supporting_doc_hit@10 = 0.2`
  - policy-prepared retrieval 기준 `supporting_doc_hit@10 = 1.0`
  - policy-prepared retrieval 기준 `citation_correctness = 1.0`
- 주의:
  - Stage 4는 보정 반영 단계이며, widened corpus 품질 게이트 확정은 아니다
  - 다음 단계인 Stage 5에서 retrieval / citation 회귀 검증을 다시 수행한다

## 2026-03-31 Stage 5 Update

- Stage 5: widened corpus 전체 `13개` benchmark 케이스 기준 Stage 9 retrieval / citation 회귀 완료
- 추가 구현:
  - [`run_stage05_regression.py`](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_stage05_regression.py) 추가
  - widened corpus 회귀 전용 `--skip-ingest` / `--reuse-existing-data-dir` 경로 정리
  - disconnected / update / install 관련 policy term 보강
- 결과:
  - raw retrieval baseline `source_dir_hit@5 = 0.0`
  - policy-prepared retrieval `source_dir_hit@5 = 0.9231`
  - policy-prepared retrieval `supporting_doc_hit@10 = 0.9231`
  - policy-prepared retrieval `citation_correctness = 0.9231`
- 판정:
  - widened corpus 기준 Stage 5 gate 는 `pass`
- 남은 리스크:
  - `RB-003` 1건 미해결
  - raw retrieval baseline 이 여전히 약함
- 다음 단계:
  - `6단계. multiturn / red-team 회귀 검증`

## 2026-03-31 Stage 6 Update

- Stage 6: widened corpus 기준 multiturn / red-team 회귀 완료
- 추가 구현:
  - [`run_stage06_regression.py`](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_stage06_regression.py) 추가
  - Stage 5 policy gate + multiturn + red-team + Stage 10-style suite 를 순차 실행하는 재현 경로 고정
- 결과:
  - multiturn `2/2` 시나리오 통과
  - red-team `7/7` 통과
  - combined suite `overall_decision = go`
- 해석:
  - retrieval 보정이 follow-up continuity, topic shift, version continuity, 보수 응답 규칙을 깨지 않았다
- 다음 단계:
  - `7단계. refresh / activate / rollback 재검증`

## 2026-03-31 Stage 7 Update

- Stage 7: widened corpus 기준 refresh / activate / rollback 재검증 완료
- 추가 구현:
  - [run_stage07_refresh_cycle.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_stage07_refresh_cycle.py) 추가
  - [summarize_stage07_cycle.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/summarize_stage07_cycle.py) 추가
  - [run_activation_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_activation_smoke.py) 에 existing data dir reuse 옵션 보강
  - [rollback_index.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/rollback_index.py) 에 same-path rollback smoke 옵션 보강
- 실제 수행:
  - widened corpus bundle `s07r` 생성
  - outbound / inbound validation 수행
  - staging / reindex 로 `s07r-core` 생성
  - widened corpus 에서 이미 검증된 `s15c-core` runtime smoke evidence 를 동등성 확인 후 activation 에 사용
  - rollback 으로 현재 포인터를 다시 `s15c-core` 로 복원
- 결과:
  - Stage 7 summary `pass = true`
  - current pointer `s15c-core`
  - previous pointer `s07r-core`
  - lineage preserved `true`
- 주의:
  - duplicate-index immediate reuse-smoke 는 Windows 환경에서 안정적이지 않아 final runtime authority 로 사용하지 않았다
  - widened corpus runtime authority 는 계속 `s15c-core-smoke-report.json` 이다
  - retrieval / citation 품질 권위는 계속 Stage 5 / Stage 6 이다
- 결과 문서:
  - [stage07-refresh-activate-rollback-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage07-refresh-activate-rollback-report.md)
  - [stage07-refresh-cycle-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage07-refresh-cycle-summary.json)
- 다음 단계:
  - `8단계. live runtime / viewer / citation 경로 품질 재검증`

## 2026-03-31 Stage 8 Update

- Stage 8: widened corpus 기준 live runtime / viewer / citation 경로 품질 재검증 완료
- 추가 구현:
  - [run_live_runtime_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_live_runtime_smoke.py) 에 bridge evidence gate 추가
  - same session cookie value 검증 추가
  - citation viewer 의 `section_title_present` 검증 추가
  - [live_runtime_smoke_cases.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/live_runtime_smoke_cases.json) 의 1턴 한국어 질문을 더 운영자다운 표현으로 수정
- 결과:
  - Stage 8 live runtime smoke `overall_pass = true`
  - same conversation id `true`
  - same session cookie value `true`
  - follow-up rewrite contains `last_document` `true`
  - viewer click-through `true`
  - viewer section title alignment `true`
  - bridge runtime mode `company-only`
  - bridge embedding model `BAAI/bge-m3`
  - bridge embedding dimensions `1024`
  - fallback chat `0`
- 해석:
  - Stage 8은 serving-path integrity 와 citation-viewer behavior 의 pass 이다
  - retrieval-quality authority 는 계속 Stage 5 / Stage 6 이다
- 결과 문서:
  - [stage08-live-runtime-quality-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage08-live-runtime-quality-report.md)
  - [stage08-live-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage08-live-runtime-report.json)
- 다음 단계:
  - `9단계. 저장소 정리와 v2 본체 가시화`

## 2026-03-31 Stage 9 Update

- Stage 9: 저장소 정리와 v2 본체 가시화 완료
- 추가 구현:
  - [repository-map.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/repository-map.md) 추가
  - [check_stage09_repository_map.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage09_repository_map.py) 추가
  - [README.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/README.md) 를 제품 설명서 중심으로 재정리
- 결과:
  - `stage09-repository-map-check.json` 기준 `pass = true`
  - missing core/support paths 없음
  - root stray python entrypoint 없음
- 결과 문서:
  - [stage09-repository-clarity-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage09-repository-clarity-report.md)
  - [stage09-repository-map-check.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage09-repository-map-check.json)
- 다음 단계:
  - `10단계. 최종 통합 검증과 릴리즈 판정`

## 2026-03-31 Stage 10 Update

- Stage 10: 최종 통합 검증과 릴리즈 판정 완료
- 추가 구현:
  - [run_stage10_release_gate.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_stage10_release_gate.py) 추가
- 결과:
  - Stage 5 policy gate pass
  - Stage 6 suite gate pass
  - Stage 7 refresh gate pass
  - Stage 8 serving gate pass
  - Stage 9 repository gate pass
  - runtime contract gate pass
  - 최종 판정 `conditional-go`
- 해석:
  - widened validation corpus 기준 제출/시연/검증용으로는 pass
  - target-minor-pinned operator release 로는 아직 미인증
- 결과 문서:
  - [stage10-final-release-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage10-final-release-report.md)
  - [stage10-final-release-gate.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage10-final-release-gate.json)
- 다음 단계:
  - target release profile 확정
  - raw retrieval baseline 개선
  - release-profile rehearsal
