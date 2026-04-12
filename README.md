# Play Book Studio

Play Book Studio는 `기업 문서`, `운영 절차`, `벤더 문서`, `사내 runbook`을 `검증 가능한 플레이북`으로 전환하는 플랫폼이다.

## Current Truth

- 현재 정직한 판매 단계는 `paid_poc_candidate` 다.
- 현재 첫 검증 pack은 `OpenShift 4.20` 이다.
- 제품 본체는 `문서-플레이북 플랫폼`이고, OCP는 첫 검증 pack 이다.

정확한 buyer promise 와 pass/fail 기준은 [Q1_8_PRODUCT_CONTRACT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/Q1_8_PRODUCT_CONTRACT.md:1), [OWNER_SCENARIO_SCORECARD.yaml](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/OWNER_SCENARIO_SCORECARD.yaml:1)을 본다.

## What The Product Does

- 문서를 `검색 가능한 근거`, `사람이 읽는 플레이북`, `운영형 답변 표면`으로 연결한다.
- 답변과 플레이북이 `source`, `version`, `anchor` 를 잃지 않게 만든다.
- 고객 문서 PoC 결과를 재사용 가능한 pack 과 운영 자산으로 남긴다.

## Active Rule Set

현재 프로젝트 규칙은 아래 문서만 소유한다.

- [AGENTS.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/AGENTS.md:1)
- [PROJECT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PROJECT.md:1)
- [Q1_8_PRODUCT_CONTRACT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/Q1_8_PRODUCT_CONTRACT.md:1)
- [OWNER_SCENARIO_SCORECARD.yaml](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/OWNER_SCENARIO_SCORECARD.yaml:1)
- [P0_ARCHITECTURE_FREEZE_ADDENDUM.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/P0_ARCHITECTURE_FREEZE_ADDENDUM.md:1)
- [PARSED_ARTIFACT_CONTRACT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PARSED_ARTIFACT_CONTRACT.md:1)
- [SECURITY_BOUNDARY_CONTRACT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/SECURITY_BOUNDARY_CONTRACT.md:1)
- [TASK_BOARD.yaml](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/TASK_BOARD.yaml:1)

이 외의 루트 문서는 소개, 전략, 인덱스 역할만 한다.

## Reference Documents

- [FILE_ROLE_GUIDE.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/FILE_ROLE_GUIDE.md:1)
- [CODEX_OPERATING_CHARTER.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/CODEX_OPERATING_CHARTER.md:1)
- [OWNER_VALUE_CASE.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/OWNER_VALUE_CASE.md:1)
- [BEACHHEAD_ICP_AND_TRIGGER.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/BEACHHEAD_ICP_AND_TRIGGER.md:1)
- [CUSTOMER_POC_BUYER_PACKET.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/CUSTOMER_POC_BUYER_PACKET.md:1)

## Next Thread Start Order

다음 실행 스레드는 아래 순서로만 읽고 시작한다.

1. [AGENTS.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/AGENTS.md:1)
2. [PROJECT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PROJECT.md:1)
3. [TASK_BOARD.yaml](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/TASK_BOARD.yaml:1)
4. [Q1_8_PRODUCT_CONTRACT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/Q1_8_PRODUCT_CONTRACT.md:1)
5. [OWNER_SCENARIO_SCORECARD.yaml](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/OWNER_SCENARIO_SCORECARD.yaml:1)

## Execution

기준 진입점은 `play_book.cmd` 하나다.

```powershell
play_book.cmd ui
play_book.cmd ask --query "etcd 백업은 어떻게 하나?"
play_book.cmd eval
play_book.cmd runtime
```

## Repository Notes

- 규칙 우선순위는 [PROJECT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PROJECT.md:1) 를 본다.
- 저장소 맵은 [FILE_ROLE_GUIDE.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/FILE_ROLE_GUIDE.md:1) 를 본다.
- `archive/` 아래 문서는 현재 판단 기준이 아니다. 분류 기준은 [archive/INDEX.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/archive/INDEX.md:1)를 본다.
