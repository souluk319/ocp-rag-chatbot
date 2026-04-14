# 14_asciidoc_plus_12_tone

## Goal

`installing_on_any_platform` 문서를 AsciiDoc source-first 입력으로 다시 읽고, `12_refined_hybrid`에서 검증된 문체와 구조를 설치형 문서에 맞게 적용한 reader-grade 후보를 만든다.

## Source Stack

- AsciiDoc source-first
  - `tmp_source/openshift-docs-enterprise-4.20/installing/overview/index.adoc`
  - `tmp_source/openshift-docs-enterprise-4.20/installing/overview/installing-preparing.adoc`
- Trial preservation inputs
  - `04_procedure_code_verify`
  - `08_operator_first`
  - current html-single `installing_on_any_platform`

## Technique

1. AsciiDoc 원문에서 설치 범위, 플랫폼 선택, 사전 준비, 설치 단계, 초기 검증 축을 먼저 추출한다.
2. 기존 trial에서 살아 있던 DNS 검증과 절차형 표현을 보존한다.
3. 구조는 `Overview -> When To Use -> Before You Begin -> Validate Infrastructure -> Create Installation Assets -> Bootstrap -> Verify -> Failure Signals` 순서로 고정한다.
4. 법적 고지, generic preface, 군더더기 배경 설명은 줄이고, 설치를 닫는 데 필요한 경로는 남긴다.

## Why This Exists

`installing_on_any_platform`는 복구 런북이 아니라 설치형 문서라서, `backup_and_restore`와 같은 절차 구조를 그대로 복사하면 맞지 않는다. 이 variant는 source cleanliness와 설치형 first-reading path를 같이 잡기 위한 결과다.
