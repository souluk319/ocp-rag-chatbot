# 2026-03-31 Stage 10 Final Release Report

## 목표

Stage 10의 목표는 앞선 1~9단계 증거를 바탕으로 **현재 상태를 실제 제출/시연 가능한 수준으로 묶어서 판정**하는 것이다.

## 사용한 입력 증거

- Stage 5 retrieval / citation: [stage05-regression-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage05-regression-summary.json)
- Stage 6 multiturn / red-team: [stage06-regression-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage06-regression-summary.json)
- Stage 7 refresh loop: [stage07-refresh-cycle-summary.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage07-refresh-cycle-summary.json)
- Stage 8 live runtime: [stage08-live-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage08-live-runtime-report.json)
- Stage 9 repository clarity: [stage09-repository-map-check.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage09-repository-map-check.json)
- 최종 집계: [stage10-final-release-gate.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage10-final-release-gate.json)

## 최종 판정

**Final Release Verdict: conditional-go**

의미:

- 현재 widened validation corpus 기준으로는 **제출/시연/검증용 결과물**로 충분하다.
- 하지만 아직 **target-minor-pinned operator release** 로는 인증하지 않는다.

한 줄로 줄이면:

**validation release 는 pass, full operator certification 은 아직 아님**

## 하드 게이트 결과

- Stage 5 policy gate: pass
- Stage 6 suite gate: pass
- Stage 7 refresh gate: pass
- Stage 8 serving gate: pass
- Stage 9 repository gate: pass
- runtime contract gate: pass

현재 활성 포인터:

- current: `s15c-core`
- previous: `s07r-core`

## 지금 pass 라고 말할 수 있는 것

현재 시스템은 다음을 함께 증명한다.

- retrieval / citation 품질은 Stage 5 기준으로 통과
- multiturn / red-team 은 Stage 6 기준으로 통과
- refresh / activate / rollback 메커니즘은 Stage 7 기준으로 통과
- live runtime / viewer / citation click-through 는 Stage 8 기준으로 통과
- 저장소 가시성은 Stage 9 기준으로 통과
- runtime contract 는 `company-only`, `BAAI/bge-m3`, `1024` 기준으로 유지

즉, 지금 상태는 **validation-grade OCP RAG assistant** 라고 부를 수 있다.

## 아직 인증하지 않는 것

아래는 이번 판정이 의도적으로 인증하지 않는 범위다.

- 특정 target minor 예: `enterprise-4.17` 에 고정된 operator release
- 전체 `openshift-docs` 전 범위를 다 포함하는 full-corpus 품질 보장
- 검증셋 밖의 모든 운영 질문에 대한 보장
- future source update 가 refresh/regression loop 를 거치지 않은 상태의 자동 승인

## 남은 리스크

1. raw retrieval baseline 이 widened corpus 에서 여전히 약하다.
2. Stage 7 activation 은 equivalent widened-corpus smoke evidence 를 사용했다.
3. 현재 로컬 런타임은 company bearer token 없이도 동작하지만, 추후 인증 정책이 바뀌면 token provisioning 이 필요할 수 있다.
4. target minor 가 아직 정해지지 않아 operator-release profile 검증이 남아 있다.

## 결론

이번 최종 판정은 **과장 없는 conditional-go** 가 맞다.

- 데모 가능
- 제출 가능
- 설명 가능
- 실제로 질문/답변/citation/viewer/multiturn/refresh loop 를 시연 가능

하지만 아직은 **validation-mode widened corpus 기준 합격** 이지, 특정 minor 버전에 고정된 운영 릴리즈 합격은 아니다.
