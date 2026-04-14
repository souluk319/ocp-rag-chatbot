# 15_metrics_admin_book

## Goal

관리자 기준으로 metrics 조회와 dashboard 확인 경로를 하나의 reader-grade book으로 묶는다.

## Source Stack

- AsciiDoc source-first
  - `tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/accessing-metrics/accessing-metrics-as-an-administrator.adoc`
- Tone and structure baseline
  - `backup_and_restore/14_asciidoc_plus_12_tone`

## Technique

1. metrics 목록 확인, query 실행, target 상세 확인, dashboard 검토 경로를 우선 추출한다.
2. Prometheus 개념 설명은 최소화하고 관리자 작업 경로만 남긴다.
3. 구조는 `Overview -> When To Use -> Before You Begin -> List Metrics -> Query Metrics -> Inspect Targets -> Review Dashboards -> Verify -> Failure Signals` 순서로 정리한다.
4. metrics path 자체가 탐색형이므로, 어디서 무엇을 확인해야 하는지를 선명하게 만든다.

## Why This Exists

metrics 문서는 운영자가 “무엇을 먼저 봐야 하는가”가 중요하다. 탐색 경로를 북으로 고정해 두면 later troubleshooting book과도 자연스럽게 연결된다.
