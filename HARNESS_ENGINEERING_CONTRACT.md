# Harness Engineering Contract

## 목적

이 문서는 사용자가 한 번 승인하면 Codex 가 최소 몇 시간은 재협상 없이 굴러갈 수 있게 만드는 `execution harness` 계약을 고정한다.

핵심 목표는 단순하다.

- 목표를 1개로 잠그고
- 입력과 출력 경계를 먼저 고정하고
- 비교 기준과 탈락 기준을 문서로 남기고
- winner 가 없는 작업을 끝냈다고 말하지 않게 만드는 것

## Current Judgment

이 프로젝트의 병목은 코드량보다 `실행 계약 부재`였다.

그래서 이후 장시간 작업은 `execution harness` 없이 시작하지 않는다.

## Execution Harness Fields

모든 장시간 execution thread 는 아래 8개를 가진다.

1. `goal`
   - 최종 산출물 1개
2. `source_input`
   - 공식 입력 경로
   - fallback 허용 여부
3. `output_paths`
   - 반드시 남겨야 하는 결과 파일 경로
4. `comparison_target`
   - 모범답안 또는 기준 파일
5. `trial_budget`
   - trial, hybrid, final candidate 개수
6. `bans`
   - 금지 경로와 금지 결과 형태
7. `done_definition`
   - 완료라고 말할 수 있는 조건
8. `verification`
   - build, test, log, or explicit file existence check

## Default 3-Hour Harness

사용자가 “하자”, “돌려”, “태워라”처럼 execution 만 승인한 경우 아래 harness 를 먼저 적용한다.

### Goal

이번 milestone 에서 실제로 남겨야 하는 결과물 1개를 정한다.

예:

- `backup_and_restore reader-grade gold candidate`
- `Wave 1 fresh build report`
- `Gold candidate books UI 연결`

### Inputs

- 공식 source 1개
- fallback 1개 이하
- 기존 winner 또는 reference 1개

### Outputs

- 사용자 검토용 결과물은 `md`
- trial 이면:
  - `output.md`
  - `pipeline.md`
  - `meta.json`
- 승격이면:
  - promoted `md`
  - manifest
  - report
  - catalog

### Comparison

비교 축은 항상 아래 중 하나로 고정한다.

- `원본 -> 자동 결과 -> 모범답안`
- `기존 winner -> 신규 candidate`
- `현재 service output -> 새 gold candidate`

### Limits

기본 한도:

- base trials: `10`
- hybrid variants: `3` 이내
- final candidates: `1~3`

### Bans

- `json/html` 을 사용자 검토 결과처럼 먼저 제시하지 않는다
- 기존 실패 라인을 “조금만 더” 보정하지 않는다
- winner 없이 완료를 선언하지 않는다
- output path 없는 산출물을 만들지 않는다

### Done Definition

아래를 모두 만족해야 한다.

- 결과 파일이 있다
- 사용자가 바로 열 수 있다
- 어떤 source 에서 나왔는지 남아 있다
- 어떤 규칙/파이프라인인지 남아 있다
- winner 또는 gold candidate 가 명시돼 있다
- 검증 로그가 있다

## Promotion Harness

reader-grade 결과를 실제 서비스 경로로 올릴 때는 아래 추가 조건을 쓴다.

- `candidate source path`
- `promoted path`
- `manifest path`
- `report path`
- `catalog path`
- `UI reflection 여부`
- `runtime reflection 여부`

`UI 반영`과 `chatbot/viewer runtime 반영`은 다른 단계로 분리해서 기록한다.

## Output Discipline

사용자에게 먼저 보여줄 것은 항상 아래 순서를 따른다.

1. `md 결과물`
2. `pipeline 설명서`
3. `manifest / report`
4. 내부 점검용 `json/html`

## Completion Language

다음 표현은 금지한다.

- “거의 됐다”
- “품질은 아직 부족하다”
- “이론상 가능하다”

대신 아래 중 하나만 쓴다.

- `쓸 수 있다`
- `쓸 수 없다`
- `UI 반영 완료`
- `runtime 반영 미완료`
- `gold candidate 승격 완료`

## Current Adoption

이 계약은 아래 작업들에 즉시 적용한다.

- 공식 source repo 기반 reader-grade book build
- official source repo 기반 wiki-grade book / entity hub build
- Wave 1 gold corpus promotion
- Control Tower / Library surface reflection
- repository source-first ingestion
