# File Role Guide

저장소는 `active rule docs`, `reference docs`, `구현 폴더` 기준으로 보면 된다.

## Active Rule Docs

- `AGENTS.md`
  - 작업 방식과 판단 규칙
- `PROJECT.md`
  - 제품 헌장과 문서 우선순위
- `Q1_8_PRODUCT_CONTRACT.md`
  - buyer acceptance 와 non-promise
- `OWNER_SCENARIO_SCORECARD.yaml`
  - demo / full-sale 수치 게이트
- `P0_ARCHITECTURE_FREEZE_ADDENDUM.md`
  - architecture, security, data-state, product-surface 우선 문서
- `PARSED_ARTIFACT_CONTRACT.md`
  - parsed lineage 운영 계약
- `SECURITY_BOUNDARY_CONTRACT.md`
  - private-doc security 운영 계약
- `TASK_BOARD.yaml`
  - 실행 상태와 작업 순서

## Reference Docs

- `README.md`
  - 제품 개요와 진입점
- `CODEX_OPERATING_CHARTER.md`
  - 사용자와 Codex의 협업 방식, 승인 원칙, cleanup 기준을 정리한 운영 헌장
- `OWNER_VALUE_CASE.md`
  - 판매 단계와 가치 가설
- `BEACHHEAD_ICP_AND_TRIGGER.md`
  - 첫 구매 고객과 trigger
- `CUSTOMER_POC_BUYER_PACKET.md`
  - 고객 문서 PoC 계약 문서
- `archive/INDEX.md`
  - active / reference / archive 분류 기준

## Product Surface

- `src/play_book_studio/app/`
  - 서버, 뷰어, UI, 상황실
- `src/play_book_studio/app/static/`
  - 메인페이지, 채팅, 상황실, static asset
- `apps/`
  - 장기적으로 제품 표면을 분리할 자리

## Pipeline And Governance

- `manifests/`
  - runtime pack 기준선
- `schemas/`
  - document / chunk / playbook 산출물 계약
- `src/play_book_studio/ingestion/`
  - 수집, 정규화, 승격, 품질 검사
- `src/play_book_studio/canonical/`
  - 공통 문서 모델과 변환
- `src/play_book_studio/intake/`
  - 외부 문서와 고객 문서 intake
- `reports/`
  - 품질, 런타임, 승격, 평가 리포트

## Runtime And Evaluation

- `src/play_book_studio/retrieval/`
  - 검색과 세션 추적
- `src/play_book_studio/answering/`
  - 답변 생성과 근거 연결
- `tests/`
  - 회귀 테스트와 계약 테스트
- `reports/build_logs/`
  - 빌드와 승격 로그

## Operations

- `play_book.cmd`
  - 표준 실행 진입점
- `src/play_book_studio/cli.py`
  - canonical CLI
- `scripts/`
  - 배치, 승격, 평가 스크립트
- `docker-compose.yml`
  - 로컬 의존 서비스 실행

## Archive

- `archive/legacy_reference_docs/`
  - 오래된 참고 문서
- `archive/root_contracts/retired/`
  - 더 이상 기준 문서가 아닌 루트 유물
