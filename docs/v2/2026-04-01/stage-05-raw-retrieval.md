# 5단계 - raw retrieval baseline 개선

## 목표

widened corpus 기준 raw retrieval 이 너무 약한 상태를 보강한다.

## 왜 이 단계가 중요한가

policy-prepared 결과가 좋아도 raw retrieval 이 약하면 심사나 운영에서 쉽게 무너진다.

## 담당 역할

- Ramanujan: 실패 질문군과 query signal 분해
- Arendt: 한국어 질문 표현과 검색 의도 간 차이 정리
- Peirce: source_dir / category / intro 문서 후보 검증
- Gibbs: policy / query handling / metadata 기반 보정 구현
- Feynman: 실패 케이스 재실행
- Russell: 임시 땜질인지 구조적 개선인지 감사

## 작업 내용

1. widened corpus 실패 케이스를 다시 확인한다.
2. source_dir, category, path term 보정 포인트를 정리한다.
3. 기본 질문과 운영 질문이 적절한 문서군으로 가게 만든다.

## 테스트

- stage03 / stage05 기준 실패 케이스
- basic definition query
- upgrade / disconnected / operator 계열 질문

## 완료 기준

- raw retrieval 기준 실패 케이스가 줄어든다.
- 기대 source_dir 이 더 자주 top-k 안에 들어온다.
- policy-prepared 없이도 이전보다 덜 흔들린다.

## 산출물

- retrieval 보정
- 비교 결과
- 짧은 완료 보고
