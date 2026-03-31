# 2026-04-01 계획표

## 1. target release 방향 확정

- validation profile 유지 여부 확인
- operator-release target minor 가 정해지면 source profile 전환 준비
- `main` 기반 검증 모드와 `enterprise-4.x` 운영 모드 차이를 명확히 문서화

## 2. raw retrieval baseline 개선

- widened corpus 에서 raw retrieval 이 약한 케이스 재분석
- category metadata 오분류 정리
- query classification / source_dir bias / chunk metadata 보강

## 3. release-profile rehearsal

- target minor profile 이 있으면 실제 mirror/worktree 연결
- 정규화 -> reindex -> smoke -> activation rehearsal 수행
- validation-mode 와 release-mode evidence 분리

## 4. Stage 7 refresh loop 재현성 강화

- duplicate-index fresh smoke 가 Windows 에서 흔들리는 원인 추가 조사
- equivalent smoke 의존도를 줄일 수 있는 경로 탐색

## 5. 운영 문서 다듬기

- runbook 을 더 짧고 실무형으로 정리
- README 에 데모/운영 구분 표기 강화
- 필요한 경우 UI 경고 문구 최소 보강

## 6. 최종 목표

내일의 핵심 목표는 **validation-mode conditional-go 를 release-profile 준비 단계로 한 단계 더 끌어올리는 것**이다.
