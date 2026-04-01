# 7단계 - 실런타임과 실코퍼스 정합성

## 목표

health 에 보이는 코퍼스와 실제 OpenDocuments runtime 이 사용하는 코퍼스가 최대한 일치하도록 검증한다.

## 왜 이 단계가 중요한가

“문서상으로는 1201개인데 실제 런타임은 다른 데이터를 쓴다”면 심사에서 매우 위험하다.

## 담당 역할

- Ramanujan: 무엇을 “같은 코퍼스”라고 볼지 기준 정리
- Arendt: 이 문제를 사용자/심사 관점에서 설명 가능한 형태로 정리
- Peirce: manifest / staged data / active source 구조 비교
- Gibbs: runtime DB / active index / launch path 검증
- Feynman: 실제 stats / sqlite / health 재검증
- Russell: 문서와 실제 상태의 불일치 포인트 감사

## 작업 내용

1. active index, staged manifest, runtime DB 관계를 재확인한다.
2. stale data reuse 가능성을 본다.
3. 지금 구조에서 가장 안전한 launch path 를 정리한다.

## 테스트

- `/health`
- OD stats
- active manifest / runtime db count 비교

## 완료 기준

- 현재 기준 어떤 코퍼스가 실제 serving 에 쓰이는지 명확히 설명 가능
- 문서와 실제 상태가 크게 어긋나지 않음
- launch path 기준이 정리됨

## 현재 결과 요약

- active profile: `ocp-validation-main-core`
- active index: `s15c-core`
- active manifest: `data/staging/s15c/manifests/staged-manifest.json`
- active document count: `1201`
- declared/detected git ref: `main`

## 산출물

- 정합성 보고
- 필요 시 launch path 보정
- 짧은 완료 보고
