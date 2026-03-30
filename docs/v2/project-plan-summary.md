# v2 프로젝트 계획 및 현황

이 문서는 제품 소개가 아니라, `rewrite/opendoc-v2` 브랜치의 진행 현황과 다음 작업을 빠르게 파악하기 위한 계획 문서입니다.

## 브랜치 의도

`rewrite/opendoc-v2` 는 v1 런타임을 이어받아 확장하는 브랜치가 아니라, 새 OCP 운영도우미 챗봇을 위한 리라이트 브랜치입니다.

- v1 런타임과 예전 UI는 제거
- `release/v1` 와 `v1.0` 태그로 이전 버전 보존
- v2 는 OpenDocuments 기준 구조와 OCP 전용 파이프라인으로 재구성

## 현재 검증 상태

- Stage 10 평가 기준 `go`
- Stage 11 validated slice 기준 local refresh loop 검증 완료
- Stage 12 live runtime baseline 검증 완료
- Stage 13 source profile / git lineage abstraction 완료
- Stage 14 one-command operator launch path 검증 완료

현재 확보된 기준은 다음과 같습니다.

- citation 은 raw `.adoc` 대신 생성된 HTML 로 연결
- Stage 9 policy-prepared retrieval 은 고정 benchmark set 에서 높은 supporting-doc / citation 정확도 확보
- multiturn replay 는 5턴 시나리오 기준 통과
- runtime endpoint / model 설정은 env 기반으로만 사용
- validation mode 와 future operator-release mode 를 source profile 로 분리
- active Stage 11 index 를 기준으로 bridge -> OpenDocuments -> gateway 를 한 번에 띄우는 운영 진입점 확보

## 다음 마일스톤

1. 운영 대상 minor 버전이 확정되면 target-minor source profile 활성화
2. validated P0 이후 core corpus 확장
3. corpus 확대 후 Stage 9 ~ Stage 12 게이트 재검증
4. Stage 11 delta refresh 실데이터 기준 재실행
5. 필요 시 최소 UI hardening

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
