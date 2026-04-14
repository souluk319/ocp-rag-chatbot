# 16_troubleshooting_book

## Goal

모니터링 장애 대응 문서를 `failure-first` reader-grade book으로 분리해, 운영자가 증상 기준으로 바로 읽을 수 있게 만든다.

## Source Stack

- AsciiDoc source-first
  - `tmp_source/openshift-docs-enterprise-4.20/observability/monitoring/troubleshooting-monitoring-issues.adoc`
- Tone and structure baseline
  - `backup_and_restore/14_asciidoc_plus_12_tone`

## Technique

1. user-defined metrics unavailable, Prometheus disk pressure, `KubePersistentVolumeFillingUp`, `AlertmanagerReceiversNotConfigured` 네 축을 우선 추출한다.
2. 구조는 `Overview -> Start Here -> Symptom Paths -> Verify -> Escalation` 순서로 잡는다.
3. 장애 원인 설명은 줄이고, 실제로 무엇을 확인하고 어떤 조치를 취해야 하는지 우선 배치한다.
4. support case 또는 알림 설정 문서는 escalation / additional path로만 남긴다.

## Why This Exists

monitoring troubleshooting은 참조 문서보다 장애 대응 북에 가깝다. 증상별 분기와 확인 경로가 선명해야 reader-grade 품질이 나온다.
