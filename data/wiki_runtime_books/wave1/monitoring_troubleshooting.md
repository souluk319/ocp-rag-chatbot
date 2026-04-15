# 모니터링 트러블슈팅 북

## Overview

이 문서는 OpenShift monitoring에서 자주 만나는 장애 징후를 증상 기준으로 정리한다.  
metrics가 보이지 않거나, Prometheus 디스크 사용량이 급증하거나, 주요 alert가 firing 중일 때 먼저 이 문서를 본다.

## Start Here

먼저 아래에서 가장 가까운 증상을 고른다.

- 사용자 정의 프로젝트 metrics가 보이지 않는다.
- Prometheus가 디스크를 과도하게 사용한다.
- `KubePersistentVolumeFillingUp` alert가 firing 중이다.
- `AlertmanagerReceiversNotConfigured` alert가 firing 중이다.

## Symptom Paths

### 1. User-Defined Project Metrics Are Unavailable

먼저 확인할 것:

1. user-defined project monitoring이 실제로 활성화돼 있는지 확인한다.
2. service monitor 또는 scrape 설정이 올바른지 본다.
3. target 상세 정보에서 scrape 상태를 확인한다.

추가로 본다:

- namespace 범위가 맞는지
- metric endpoint가 실제로 노출되는지
- target label이 기대와 다르지 않은지

### 2. Prometheus Consumes Too Much Disk Space

먼저 확인할 것:

1. Prometheus storage 사용량 추세를 확인한다.
2. retention, scrape interval, evaluation interval 설정을 다시 본다.
3. 특정 workload나 metrics path가 과도한 cardinality를 만들지 않는지 점검한다.

이 경우는 support case까지 이어질 수 있으므로, disk pressure가 빠르게 증가하면 지체하지 말고 escalation한다.

### 3. `KubePersistentVolumeFillingUp` Alert Fires for Prometheus

확인 순서:

1. 어떤 Prometheus volume이 찬 것인지 확인한다.
2. 사용량 증가 속도가 일시적인지 지속적인지 본다.
3. retention 조정 또는 storage 확장이 필요한지 판단한다.

### 4. `AlertmanagerReceiversNotConfigured` Alert Fires

의미:

- alert는 생성되지만, 실제 receiver 구성이 부족해 notification delivery가 되지 않을 가능성이 높다.

확인 순서:

1. alert notification 설정이 존재하는지 확인한다.
2. default platform monitoring과 user workload monitoring 쪽 설정이 모두 맞는지 확인한다.
3. receiver route가 실제 alert를 받을 수 있는지 다시 검토한다.

## Verify

- user-defined metrics가 다시 query 결과에 보이는지 확인한다.
- target scrape 상태가 정상으로 돌아왔는지 본다.
- Prometheus disk usage가 완만해졌는지 확인한다.
- alert receiver 구성 후 동일 경고가 해소되는지 다시 확인한다.

## Escalation

다음 조건이면 support case 또는 상위 운영 escalation로 넘긴다.

- Prometheus disk pressure가 빠르게 증가한다.
- target 설정과 service monitor가 정상인데도 metrics가 계속 비어 있다.
- alert routing을 수정했는데도 receiver misconfiguration 경고가 계속 firing 된다.

## Source Trace

- `observability/monitoring/troubleshooting-monitoring-issues.adoc`
- included modules for user-defined metrics unavailable, Prometheus disk usage, `KubePersistentVolumeFillingUp`, `AlertmanagerReceiversNotConfigured`
