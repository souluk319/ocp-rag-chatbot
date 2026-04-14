# 메트릭 조회 운영 북

## Overview

이 문서는 클러스터 관리자 기준으로 OpenShift metrics를 조회하고, target 상태를 확인하고, dashboard를 검토하는 핵심 경로를 정리한다.  
성능 저하, scrape 누락, 이상 징후를 확인할 때 먼저 이 문서를 본다.

## When To Use

- 특정 component metric이 실제로 수집되는지 확인해야 할 때
- query 결과를 통해 현재 상태를 빠르게 판단해야 할 때
- target 상태나 scrape 이상 여부를 보고 싶을 때
- dashboard에서 cluster-wide 추세를 검토해야 할 때

## Before You Begin

- 클러스터 관리자 권한이 있어야 한다.
- 필요한 경우 Administrator perspective에서 monitoring 관련 메뉴에 접근할 수 있어야 한다.
- query 결과를 해석하려면 metric 이름, label, 시간 범위를 같이 본다.

## List Metrics

1. console에서 metrics 또는 monitoring dashboard로 이동한다.
2. 사용 가능한 metric 목록을 먼저 확인한다.
3. 이름이 비슷한 metric이 여러 개면 label 차이를 같이 본다.

## Query Metrics

1. 조회하려는 component 또는 workload를 정한다.
2. query 입력창에서 대상 metric을 검색한다.
3. 시간 범위를 조정해 급격한 변화가 있는지 확인한다.
4. cluster-wide 값과 특정 namespace 또는 target 값을 구분해서 본다.

## Inspect Targets

메트릭이 비정상으로 보이면 target 상세 정보부터 확인한다.

확인할 항목:

- target이 정상적으로 scrape 되는지
- 마지막 scrape 시점이 너무 오래되지는 않았는지
- 특정 endpoint만 실패하는지
- label이 예상과 다르게 붙었는지

## Review Dashboards

dashboard는 단일 metric보다 상태를 넓게 볼 때 유리하다.

우선 보는 항목:

- cluster component health
- resource usage trend
- 특정 namespace 또는 workload 이상 징후

## Verify

- query 결과가 시간 범위 변경에 따라 일관되게 갱신되는지 확인한다.
- target 상세 정보에서 scrape 상태가 정상인지 확인한다.
- dashboard 값과 직접 query한 값이 크게 어긋나지 않는지 본다.

## Failure Signals

- metric 목록에는 있는데 query 결과가 비어 있다.
- target 상태가 down이거나 scrape 실패가 반복된다.
- dashboard는 비어 있는데 target은 살아 있어 source path를 다시 봐야 한다.
- 너무 넓은 시간 범위 때문에 단기 이상 징후가 묻힌다.

## Source Trace

- `observability/monitoring/accessing-metrics/accessing-metrics-as-an-administrator.adoc`
- included modules for metric listing, querying, target inspection, dashboard review
