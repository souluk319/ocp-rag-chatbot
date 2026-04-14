# 14_asciidoc_plus_12_tone

## Goal

`machine_configuration` 문서를 AsciiDoc 원문 기준으로 다시 읽고, `12_refined_hybrid`에서 검증된 톤과 구조를 적용해 reader-grade book 후보를 만든다.

## Source Stack

- AsciiDoc source-first
  - `tmp_source/openshift-docs-enterprise-4.20/machine_configuration/index.adoc`
  - `tmp_source/openshift-docs-enterprise-4.20/modules/understanding-machine-config-operator.adoc`
  - `tmp_source/openshift-docs-enterprise-4.20/modules/machine-config-overview.adoc`
  - `tmp_source/openshift-docs-enterprise-4.20/modules/checking-mco-node-status.adoc`
- Trial preservation inputs
  - `04_procedure_code_verify`
  - `08_operator_first`
  - `10_verify_first_ops`

## Technique

1. AsciiDoc 원문에서 `MCO 역할`, `pool 규칙`, `auto reboot`, `degraded drift`, `MachineConfigNode update phases`를 우선 추출한다.
2. 기존 trial에서 살아 있던 명령어와 운영 검증 포인트를 그대로 보존한다.
3. 구조는 `Overview -> When To Use -> Before You Begin -> Configure -> Verify -> Failure Signals` 순서로 정리한다.
4. 장황한 설명은 줄이되, 운영 중 판단에 필요한 경고와 명령어는 버리지 않는다.

## Why This Exists

기존 04/08/10은 각각 장점은 있었지만, `machine_configuration`처럼 도메인 안내형 문서에는 source-level 개요와 운영자용 절차/검증을 같이 가져와야 읽히는 북이 된다. 이 variant는 그 두 축을 합친 결과다.
