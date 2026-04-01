# 6단계 - widened corpus 회귀 검증

## 목표

앞 단계 수정이 widened corpus 기준으로 실제로 유지되는지 회귀 검증한다.

## 왜 이 단계가 필요한가

기본 질문만 고쳐놓고 운영 질문이나 멀티턴이 깨지면 심사 직전에 다시 무너진다.

## 담당 역할

- Ramanujan: 회귀 실패 패턴 분류
- Arendt: 한국어 응답 품질 후퇴 여부 검토
- Peirce: 정답 출처가 유지되는지 확인
- Gibbs: benchmark / smoke 러너 보정
- Feynman: stage 5~8 성격의 실검증
- Russell: 결과 문서와 실제 실행 증거 정리

## 작업 내용

1. retrieval 회귀
2. multiturn 회귀
3. red-team 회귀
4. runtime smoke 재검증

## 테스트

- benchmark set
- 멀티턴 시나리오
- red-team case
- live runtime smoke

## 완료 기준

- 이전보다 나빠진 축이 없어야 한다.
- 최소한 basic query / citation / runtime 은 유지된다.
- 회귀 결과를 문서로 남긴다.

## 산출물

- 회귀 검증 결과
- pass/fail 판정
- 짧은 완료 보고
