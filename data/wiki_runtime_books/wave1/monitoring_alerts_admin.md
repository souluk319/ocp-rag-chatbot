# 경고 관리 운영 북

## Overview

이 문서는 OpenShift 클러스터 관리자 기준으로 alerts, silences, alerting rules를 운영하는 핵심 경로를 정리한다.  
알림이 너무 많거나, 특정 경고를 잠시 무시해야 하거나, 기본 규칙 임계값을 조정해야 할 때 먼저 이 문서를 본다.

## When To Use

- 어떤 alert가 발생했는지 빠르게 확인해야 할 때
- 유지보수 시간 동안 특정 alert를 잠시 silence 해야 할 때
- 기본 플랫폼 alert rule의 임계값이나 label을 조정해야 할 때
- 사용자 프로젝트용 alerting rule을 새로 추가하거나 정리해야 할 때

## Before You Begin

- 클러스터 관리자 권한으로 OpenShift web console에 접근할 수 있어야 한다.
- Alerting UI는 계정 권한에 따라 보이는 alerts, silences, alerting rules 범위가 달라진다.
- Alertmanager에 persistent storage를 설정하지 않으면 silence 정보가 모든 pod 재시작 시 사라질 수 있다.

## Manage Alerts

### Access the Alerting UI

1. OpenShift web console에 로그인한다.
2. Administrator perspective에서 **Observe** 또는 **Monitoring / Alerting** 경로로 이동한다.
3. 현재 firing 또는 pending 상태인 alert를 우선 확인한다.

### Review Alert Details

- alert 이름, severity, state를 먼저 확인한다.
- 어떤 label과 annotation이 붙어 있는지 본다.
- 같은 증상으로 반복 firing 중인지, 특정 node나 workload에만 집중되는지 확인한다.
- silence, notification, rule 수정 중 무엇이 필요한지 판단한다.

## Manage Silences

### Create a Silence

1. alert 상세 화면에서 silence 생성 경로로 이동한다.
2. match 조건을 검토한다.
3. 시작 시간과 종료 시간을 설정한다.
4. 사유를 남기고 silence를 생성한다.

### Review and Change Existing Silences

- 현재 silence가 어떤 label matcher를 대상으로 하는지 확인한다.
- 너무 넓은 matcher면 필요한 경고까지 숨길 수 있으니 축소한다.
- 유지보수 종료 후 즉시 expire 처리한다.

## Manage Alerting Rules

### Core Platform Alert Rules

기본 플랫폼 모니터링에는 이미 많은 alert rule이 들어 있다.  
운영자는 기존 rule의 threshold를 조정하거나, label을 수정해 알림 라우팅과 triage 우선순위를 바꿀 수 있다.

확인할 항목:

- 기존 rule의 threshold가 현재 운영 환경과 맞는지
- `severity` label이 triage 정책과 맞는지
- 불필요한 noise를 만드는 rule인지

### User-Defined Project Alert Rules

사용자 프로젝트용 alert rule은 선택한 metric 값에 따라 직접 생성할 수 있다.

주요 작업:

1. 새 alerting rule 생성
2. cross-project rule 생성 여부 검토
3. 기존 rule 목록 조회
4. 불필요한 rule 제거

## Verify

- Alerting UI에서 대상 alert가 원하는 matcher로 필터링되는지 확인한다.
- 생성한 silence가 즉시 목록에 나타나는지 확인한다.
- 수정한 rule이 의도한 severity와 label을 유지하는지 확인한다.
- 사용자 프로젝트 rule이 올바른 metric query를 사용하는지 다시 본다.

## Failure Signals

- silence를 만들었는데도 같은 alert notification이 계속 발생한다.
- 너무 넓은 matcher 때문에 필요한 alert까지 가려진다.
- Alertmanager storage가 없어 재시작 후 silence가 사라진다.
- threshold 변경 후 과도한 noise 또는 반대로 alert 미발생이 생긴다.

## Source Trace

- `observability/monitoring/managing-alerts/managing-alerts-as-an-administrator.adoc`
- included modules for alerting UI, silence management, core platform alert rules, user-defined project alert rules
