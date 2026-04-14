# 14_alerts_admin_book

## Goal

`monitoring` 통문서를 그대로 줄이지 않고, 관리자 기준으로 실제로 자주 쓰는 `alerts / silences / alerting rules` 경로만 reader-grade book으로 분리한다.

## Source Stack

- AsciiDoc source-first
  - `tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/managing-alerts/managing-alerts-as-an-administrator.adoc`
- Tone and structure baseline
  - `backup_and_restore/14_asciidoc_plus_12_tone`

## Technique

1. Alerting UI 접근, alerts 정보 확인, silences 관리, platform alert rules, user-defined project alert rules를 우선 추출한다.
2. 법적 고지, 중복 additional resources, 장황한 배경 설명은 줄인다.
3. 구조는 `Overview -> When To Use -> Before You Begin -> Manage Alerts -> Manage Silences -> Manage Alerting Rules -> Verify -> Failure Signals` 순서로 정리한다.
4. 운영자가 웹 콘솔에서 바로 따라 할 수 있는 행동 경로와 보존해야 할 경고는 유지한다.

## Why This Exists

`monitoring`은 하나의 큰 참조 문서로는 읽기 어렵다. alerts 관리만 따로 떼면 운영자용 book으로 바로 읽히고, 이후 metrics/troubleshooting book과도 역할이 분리된다.
