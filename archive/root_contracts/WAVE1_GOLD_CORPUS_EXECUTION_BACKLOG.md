# Wave 1 Gold Corpus Execution Backlog

## 목적

이 문서는 `GOLD_CORPUS_PRIORITY_FOR_OCP_OPERATIONS.md`의 Wave 1 항목을 바로 실행 가능한 backlog로 쪼갠다.

핵심 목표는 단순하다.

- `무엇을 먼저 가져올지`
- `어떤 형태의 북을 만들지`
- `언제 gold 승격 후보로 볼지`

를 한 번에 고정한다.

## 현재 판단

Wave 1은 `공식 source repo 확보`와 `운영형 reader-grade book 4권`으로 닫는 게 맞다.

즉, 첫 마일스톤은 아래 다섯 개다.

1. `openshift/openshift-docs` source mirror
2. `backup_and_restore`
3. `installing_on_any_platform`
4. `machine_configuration`
5. `monitoring`

## Wave 1 Execution Table

| ID | Target | Input Source | Target Book Family | Current Status | Gold Candidate Condition |
|---|---|---|---|---|---|
| W1-0 | `openshift/openshift-docs` | GitHub repo `enterprise-4.20` branch | source mirror + source trace catalog | sparse checkout와 source-first 실험은 됨 | branch / path / source trace / authority metadata 를 catalog로 고정 |
| W1-1 | `backup_and_restore` | AsciiDoc source-first + html-single fallback | `Operation Book` + `Troubleshooting Book` | `14_asciidoc_plus_12_tone` 기준선 확보 | restore 명령, verify, failure signals, critical flags 누락 없이 reader-grade md 고정 |
| W1-2 | `installing_on_any_platform` | AsciiDoc source-first + html-single fallback | `Operation Book` | trial은 있으나 legal/generic noise 제거가 덜 됨 | install-config, manifests, ignition, bootstrap, verify path 가 reader-grade md 로 고정 |
| W1-3 | `machine_configuration` | AsciiDoc source-first + existing trials | `Manual Book` + `Operation Book` | `14_asciidoc_plus_12_tone` 신규 확보 | MCO 역할, pool rules, rollout verify, failure signals 가 reader-grade md 로 고정 |
| W1-4 | `monitoring` | official source-first preferred, html-single fallback | `Manual Book` -> task-split `Operation Book` | 아직 문서 타입 분기가 약함 | 전체 문서 요약이 아니라 대표 운영 task 단위 book 으로 분해 |

## Item Detail

### W1-0. `openshift/openshift-docs` Source Mirror

#### Goal

공식 repo 를 `gold corpus`의 기준 입력으로 고정한다.

#### Must Have

- branch: `enterprise-4.20`
- source trace:
  - repo
  - branch
  - relative path
  - optional module include chain
- authority badge:
  - `Official Source Repo`
- html-single fallback link

#### Evidence

- [backup_and_restore 14 pipeline](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/backup_and_restore/14_asciidoc_plus_12_tone/pipeline.md:1)
- [machine_configuration 14 pipeline](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/machine_configuration/14_asciidoc_plus_12_tone/pipeline.md:1)

### W1-1. `backup_and_restore`

#### Goal

운영 절차 북의 기준선을 먼저 확정한다.

#### Baseline

- current winner:
  - [14_asciidoc_plus_12_tone/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/backup_and_restore/14_asciidoc_plus_12_tone/output.md:1)

#### Required Preservation

- etcd backup artifacts
- restore path choice
- manual restore command sequence
- `--skip-hash-check=true`
- verify 단계
- failure signals

#### Gold Candidate Condition

- `12`보다 tone이 나쁘지 않다
- `14` 수준의 정보 보존을 유지한다
- restore critical flags가 빠지지 않는다

### W1-2. `installing_on_any_platform`

#### Goal

설치 문서의 `noise 제거 + 절차 보존` 기준선을 만든다.

#### Known Problem

- legal notice / generic preface 가 앞부분을 오염시킨다
- 설치형 문서는 backup 복구형과 다른 구조를 요구한다

#### Required Preservation

- DNS / infra readiness
- `install-config.yaml`
- manifests / ignition generation
- bootstrap start
- completion / verify path

#### Gold Candidate Condition

- 앞부분 잡음이 제거된다
- install path 전체가 끊기지 않는다
- 설치 후 무엇을 확인해야 하는지 바로 읽힌다

### W1-3. `machine_configuration`

#### Goal

도메인 안내형 문서도 reader-grade 북으로 승격 가능한지 증명한다.

#### Baseline

- current candidate:
  - [14_asciidoc_plus_12_tone/output.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/tests/reader_grade_pipeline_trials/machine_configuration/14_asciidoc_plus_12_tone/output.md:1)

#### Required Preservation

- MCO 역할
- MCP 단일 pool 규칙
- auto reboot / paused mode
- degraded drift
- `oc get machineconfignodes`
- `oc describe machineconfignodes`

#### Gold Candidate Condition

- 문서 전체 목적이 운영자에게 바로 읽힌다
- 개요/절차/검증/실패 신호가 분리된다
- 도메인 문서인데도 읽는 순서가 보인다

### W1-4. `monitoring`

#### Goal

넓은 참조형 문서를 작업 단위 북으로 분해하는 방식을 정한다.

#### Known Problem

- 전체 monitoring 문서는 너무 넓다
- 하나의 slim book으로 뽑으면 대표성이 흐려진다

#### Required Split

- alerts
- dashboards
- metrics access
- user workload monitoring
- troubleshooting monitoring issues

#### Gold Candidate Condition

- 통문서 요약이 아니다
- task/unit 기반 book family가 나온다
- 추천질문과 직접 연결되는 운영형 북이 나온다

## Recommended Execution Order

1. `W1-0`
2. `W1-2`
3. `W1-4`
4. 필요시 `W1-1`, `W1-3`는 기준선 유지 점검만 한다

이 순서인 이유:

- `W1-1`, `W1-3`는 이미 기준선이 어느 정도 생겼다
- `W1-2`, `W1-4`가 아직 더 많이 흔들린다
- source mirror 를 먼저 고정해야 이후 모든 승격이 흔들리지 않는다

## Done Definition

Wave 1 항목을 완료로 보려면 아래가 필요하다.

- source provenance가 문서에 남아 있다
- `md` 최종 산출물이 있다
- reader-grade 구조가 있다
- critical command / verify / failure signal 누락이 없다
- 기존 pipeline 대비 좋아진 점을 비교 근거로 설명할 수 있다

## 현재 결론

Wave 1은 이미 막연한 아이디어 단계가 아니다.

지금부터는 아래 순서로 닫으면 된다.

- `official source mirror`
- `backup / install / machine config / monitoring` reader-grade gold 후보

이 backlog 를 기준으로 중요 문서부터 실제 골드 코퍼스로 승격한다.
