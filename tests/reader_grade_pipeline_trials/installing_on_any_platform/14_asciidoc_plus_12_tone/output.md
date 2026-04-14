# 어떤 플랫폼에서도 설치하기

## Overview

이 문서는 사용자 제공 인프라 환경에서 OpenShift Container Platform 클러스터를 설치할 때, 설치 전에 무엇을 준비해야 하고 설치 중 무엇을 생성하며 설치 후 무엇을 검증해야 하는지 운영자 기준으로 정리한다.

설치 프로그램의 범위는 의도적으로 좁다. 설치 성공에 필요한 핵심 자산과 절차는 먼저 고정하고, 세부 운영 구성은 설치 후 단계에서 확장하는 것을 기준으로 한다.

## When To Use

- 특정 클라우드 전용 설치 가이드보다 공통 설치 경로를 먼저 이해해야 할 때
- 사용자 제공 인프라(UPI)에 맞는 설치 준비 항목을 점검해야 할 때
- `install-config`, manifests, Ignition, bootstrap, 초기 검증 경로를 한 번에 확인해야 할 때

## Before You Begin

- 지원되는 설치 방식과 대상 플랫폼을 먼저 확인한다.
- 설치에 필요한 DNS, 네트워크, 로드 밸런서, 인증서, 접근 경로를 설치 전에 고정한다.
- 방화벽이나 프록시를 사용하는 경우, 설치 중 접근해야 하는 외부 대상과 내부 이름 해석 경로를 먼저 확인한다.
- 설치 완료 후 더 많은 구성을 할 수 있지만, 설치 단계에서는 성공에 필요한 최소 자산을 우선 확보한다.

## Validate Infrastructure Readiness

사용자 제공 인프라 환경에서는 DNS가 가장 먼저 닫혀야 한다. Kubernetes API, 내부 API, 애플리케이션 와일드카드 레코드가 올바른 대상으로 해석되지 않으면 이후 단계 전체가 불안정해진다.

확인 예시:

```shell
dig +noall +answer @<nameserver_ip> api.<cluster_name>.<base_domain>
dig +noall +answer @<nameserver_ip> api-int.<cluster_name>.<base_domain>
dig +noall +answer @<nameserver_ip> random.apps.<cluster_name>.<base_domain>
```

응답의 IP가 API 로드 밸런서와 ingress 로드 밸런서를 정확히 가리키는지 확인한다.

## Create Installation Assets

설치 자산 생성 단계의 핵심은 세 가지다.

- `install-config.yaml`
- Kubernetes manifests
- Ignition config files

이 단계에서 클러스터 이름, base domain, 플랫폼 조건, 네트워크 설계, 프록시 및 인증 관련 설정을 고정한다. 이후 단계는 이 자산을 기준으로 진행된다.

운영자가 먼저 확인할 것:

- install-config에 플랫폼과 네트워크 조건이 맞게 반영되어 있는지
- manifests 생성 전에 필요한 설정이 빠지지 않았는지
- Ignition 파일을 어느 노드에 어떤 방식으로 전달할지 준비되었는지

## Bootstrap the Cluster

설치 자산이 준비되면 bootstrap 노드와 control plane 노드가 새 클러스터를 형성하는 경로를 시작한다. 이 구간에서는 bootstrap이 정상 시작하는지, control plane이 API를 열 수 있는지, 설치 프로그램이 진행 상태를 정상적으로 보고하는지가 중요하다.

이 단계에서는 단순히 설치 명령을 실행하는 것보다, 실패 시 어느 지점에서 멈췄는지 추적 가능한 상태를 먼저 만드는 것이 중요하다.

## Verify Installation Progress

설치 후 검증은 단일 완료 메시지로 끝나지 않는다. 최소한 아래 축을 확인해야 한다.

- 노드가 예상대로 등록되었는지
- API 접근이 안정적으로 가능한지
- bootstrap 완료 후 control plane이 정상적으로 인계되었는지
- 초기 검증 단계에서 필수 서비스와 네트워크가 기대대로 응답하는지

즉, 설치는 `자산 생성 -> bootstrap -> 초기 검증`까지 닫혀야 완료로 본다.

## Failure Signals

다음 징후가 보이면 설치 자산 또는 인프라 준비 단계로 다시 돌아가야 한다.

- DNS 레코드가 API 또는 ingress 대상과 다르게 해석되는 경우
- 방화벽, 프록시, 접근 제어 때문에 설치 경로가 중간에 끊기는 경우
- install-config에 플랫폼 조건이나 네트워크 설정이 잘못 반영된 경우
- manifests 또는 Ignition 생성 이후 bootstrap이 기대한 경로로 진행되지 않는 경우
- 설치는 시작되지만 노드 등록, API 접근, bootstrap handoff 검증이 닫히지 않는 경우

## Source Trace

- AsciiDoc source:
  - `installing/overview/index.adoc`
  - `installing/overview/installing-preparing.adoc`
- Trial inputs:
  - `04_procedure_code_verify`
  - `08_operator_first`
  - `html-single installing_on_any_platform`
