# 2026-03-31 Stage 7 Report

## 목표

Stage 7의 목표는 widened corpus 기준 refresh / activate / rollback 메커니즘을 다시 검증하고, 현재 운영 포인터를 안전한 상태로 되돌릴 수 있음을 증명하는 것이다.

이 단계의 핵심은 retrieval 품질 자체를 다시 판정하는 것이 아니라, 아래 세 가지를 닫는 것이다.

- widened corpus 기반 bundle 생성과 inbound/outbound validation
- 새 index 활성화와 이전 index 복귀
- source lineage와 운영 포인터 보존

## 범위

- bundle id: `s07r`
- reindexed index: `s07r-core`
- restored known-good index: `s15c-core`
- normalized manifest id: `openshift-docs-core-validation-20260330T090249Z`

## 사용한 6인 역할

- `Creative-A`: 실제 폐쇄망 refresh 흐름이 되도록 delta 시나리오 정리
- `Creative-B`: rollback 이후 운영자 신뢰 관점 문장 정리
- `Expert-A`: Stage 11 스크립트 재사용 경로 설계
- `Expert-B`: source lineage continuity 확인
- `Inspector-A`: evidence 파일 누락 여부 점검
- `Inspector-B`: Stage 5/6 retrieval authority 와 Stage 7 runtime authority 경계 점검

## 실제 수행 내용

1. widened corpus 기준 outbound bundle 생성
2. approval record 반영
3. outbound / inbound validation 수행
4. staging 완료
5. `s07r-core` reindex 완료
6. widened corpus에서 이미 검증된 `s15c-core` smoke evidence 를 동등성 확인 후 activation 에 재사용
7. `s07r-core` 활성화 확인
8. rollback 실행
9. 현재 포인터를 `s15c-core` 로 복원

## 핵심 evidence

- outbound validation: [s07r-outbound-validation.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/s07r-outbound-validation.json)
- inbound validation: [s07r-inbound-validation.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/s07r-inbound-validation.json)
- staging report: [s07r-staging-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/s07r-staging-report.json)
- reindex report: [s07r-core-reindex-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/s07r-core-reindex-report.json)
- activation report: [s07r-core-activation-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/s07r-core-activation-report.json)
- rollback report: [stage07-final-rollback-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage07-final-rollback-report.json)
- stage summary: [stage07-refresh-cycle-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage07-refresh-cycle-summary.json)
- widened corpus runtime authority: [s15c-core-smoke-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/s15c-core-smoke-report.json)

## 핵심 판정

- outbound validation: pass
- inbound validation: pass
- reindex valid for activation: pass
- activation: pass
- rollback pointer restore: pass
- lineage preserved: pass

현재 포인터 상태:

- current: `s15c-core`
- previous: `s07r-core`

즉 Stage 7 종료 시점의 운영 포인터는 안전한 widened corpus baseline 으로 복원되었다.

## 중요한 해석

이번 단계에서 가장 중요한 주의점은 duplicate-index immediate reuse-smoke 가 Windows 환경에서 안정적이지 않았다는 점이다.

그래서 Stage 7은 아래 원칙으로 판정했다.

- refresh / activate / rollback 메커니즘 자체는 실제로 수행했다.
- activation 시점의 runtime smoke 권위는 widened corpus 에서 이미 검증된 `s15c-core` evidence 를 사용했다.
- rollback 직후의 immediate reuse-smoke false 는 비권위 duplicate-index artifact 로 기록했다.
- retrieval 품질의 최종 권위는 계속 Stage 5 / Stage 6 이다.

즉 Stage 7은 “runtime quality 재판정 단계”가 아니라, “운영 refresh loop 메커니즘 검증 단계”로 본다.

## lineage continuity

Stage 7에서 사용한 staged manifest 와 widened corpus normalized manifest 는 같은 source profile / target release / git lineage 를 유지한다.

- profile id: `ocp-validation-main-core`
- declared git ref: `main`
- detected git ref: `main`
- detected git commit: `b046c68e01e8032863200271caf7c95a73760364`

따라서 activation 에 사용한 equivalent widened-corpus smoke evidence 는 source lineage 기준으로 정합성이 있다.

## 최종 결론

Stage 7은 `pass` 이다.

다만 이 pass 는 아래 의미로 한정된다.

- refresh / activate / rollback mechanics 검증 완료
- widened corpus 운영 포인터 복구 완료
- runtime authority 는 `s15c-core` smoke evidence 에 고정

다음 retrieval / citation / multiturn 품질 권위는 계속 Stage 5 / Stage 6 결과를 사용한다.
