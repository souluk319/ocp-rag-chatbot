# Install on Any Platform

## Overview

이 문서는 user-provisioned infrastructure 기준으로 OpenShift cluster 를 설치할 때 필요한 핵심 준비 절차와 생성 자산을 정리한다.

특정 cloud provider 설치 세부사항은 포함하지 않는다.
여기서는 `공통 prerequisites`, `install-config.yaml`, `manifest / ignition 생성`, `RHCOS 설치와 bootstrap 시작`, `기본 검증 포인트`만 다룬다.

## When To Use

아래 상황이면 이 문서를 먼저 확인한다.

- 특정 cloud 전용 설치 문서가 아니라 공통 설치 경로가 필요한 경우
- user-provisioned infrastructure 에서 직접 cluster 를 구성하는 경우
- 설치 자산을 어떤 순서로 준비해야 하는지 빠르게 파악해야 하는 경우
- 긴 원문 설치 문서를 모두 읽기 전에 핵심 절차만 먼저 잡아야 하는 경우

## Choose This Installation Path

이 경로는 infrastructure 준비를 사용자가 직접 담당하는 설치 방식에 적합하다.

다음 전제조건이 충족돼야 한다.

- 네트워크, DNS, load balancing 을 직접 준비할 수 있어야 한다.
- control plane 과 compute node 에 필요한 machine 수와 최소 자원을 확보해야 한다.
- 설치 자산을 생성하고 각 노드에 전달할 수 있어야 한다.

## Before You Begin

### Core Prerequisites

- OpenShift 설치 및 업데이트 흐름을 검토해야 한다.
- cluster 설치 방식을 선택하고 사용자 준비 항목을 확인해야 한다.
- firewall 을 사용하는 경우 cluster 가 접근해야 하는 사이트를 허용해야 한다.

### Infrastructure Requirements

user-provisioned infrastructure 설치에서는 필요한 machine 을 직접 준비해야 한다.

특히 아래 항목은 설치 시작 전에 확정하는 편이 안전하다.

- control plane / compute machine 수
- 최소 CPU, memory, storage 자원
- DNS 레코드와 이름 해석
- load balancer 구성
- NTP 설정
- 네트워크 연결성

## Prepare the Installation Configuration

### Purpose

`install-config.yaml` 은 cluster 설치의 기준 입력 파일이다.
설치 프로그램이 기본값 대신 사용자 환경에 맞는 설정을 사용하게 하려면 이 파일을 직접 만든다.

### Prerequisites

- 로컬 환경에 SSH public key 가 있어야 한다.
- OpenShift 설치 프로그램을 확보해야 한다.
- cluster pull secret 을 확보해야 한다.

### Procedure

설치 디렉터리를 새로 만든다.

```shell
mkdir <installation_directory>
```

### Important

- 설치 디렉터리는 재사용하지 않는다.
- bootstrap 인증서 등 일부 자산은 짧은 만료 시간을 가지므로, 이전 설치 디렉터리를 그대로 재사용하면 실패 원인이 된다.
- 파일 일부만 재사용해야 한다면 새 디렉터리에 필요한 파일만 복사한다.

### Configuration Rule

- 파일 이름은 반드시 `install-config.yaml` 이어야 한다.
- 다음 단계에서 설치 프로세스가 파일을 소비하므로, 생성 직후 백업해 두는 편이 좋다.

## Generate Cluster Assets

### 1. Create Kubernetes Manifests

```shell
./openshift-install create manifests --dir <installation_directory>
```

이 단계에서 installation configuration 이 Kubernetes manifest 로 전환된다.

### 2. Review `mastersSchedulable`

three-node cluster 가 아니라면 `cluster-scheduler-02-config.yml` 의 `mastersSchedulable` 값이 `false` 인지 확인한다.

### Warning

- control plane node 를 schedulable 로 바꾸면 운영 모델과 구독 조건이 바뀔 수 있다.
- three-node cluster 는 예외 경로가 있으므로 같은 설정을 그대로 강제하지 않는다.

### 3. Create Ignition Config Files

```shell
./openshift-install create ignition-configs --dir <installation_directory>
```

정상적으로 끝나면 아래 자산이 생성돼야 한다.

- `bootstrap.ign`
- `master.ign`
- `worker.ign`
- `auth/kubeconfig`
- `auth/kubeadmin-password`
- `metadata.json`

### Important

- Ignition config 는 생성 후 오래 묵히지 않는다.
- 인증서 만료 때문에 설치 실패가 날 수 있으므로, 생성 후 짧은 시간 안에 사용하는 것을 기본 원칙으로 둔다.

## Start RHCOS Installation and Bootstrap

### Installation Choices

RHCOS 는 크게 두 경로 중 하나로 설치한다.

- ISO 기반 설치
- PXE 또는 iPXE 기반 설치

### Selection Guidance

- PXE 는 DHCP 와 추가 준비가 필요하지만 대량 설치에 유리하다.
- ISO 는 더 수동적이지만 소수 노드 설치에는 단순하다.

### What The Generated Files Do

생성된 Ignition 파일은 bootstrap, control plane, compute node 의 첫 부팅 설정을 결정한다.

- `bootstrap.ign`
- `master.ign`
- `worker.ign`

적절한 네트워크, DNS, load balancer 구성이 이미 되어 있다면 RHCOS 머신이 재부팅된 뒤 bootstrap 이 자동으로 시작된다.

## Verify Installation Readiness

설치 직전에는 아래 항목을 다시 확인한다.

1. `install-config.yaml` 이 별도 백업돼 있는지
2. manifest 와 ignition 자산이 모두 생성됐는지
3. DNS, load balancing, NTP, 네트워크 전제조건이 준비됐는지
4. bootstrap, master, worker 용 Ignition 파일 전달 경로가 명확한지

## Verify Installation Health

설치가 시작된 뒤에는 아래 순서로 확인한다.

1. bootstrap 프로세스가 실제로 시작됐는지
2. control plane node 가 정상적으로 올라오는지
3. API 와 console 접근이 가능한지
4. operator 와 node readiness 가 안정화되는지

이 slim book 에서는 세부 troubleshooting 을 다루지 않는다.
여기서는 설치가 정상 궤도에 올라갔는지 판단하는 최소 검증 포인트만 본다.

## Common Installation Failures

- 설치 디렉터리를 재사용해서 만료된 자산을 다시 사용함
- `install-config.yaml` 을 백업하지 않아 반복 설치 시 입력을 복원하지 못함
- DNS / load balancer / NTP / 네트워크 전제조건을 확인하지 않고 설치를 시작함
- Ignition 파일을 생성해 놓고 너무 늦게 사용함
- 설치 경로 선택 없이 ISO/PXE 세부 문서만 먼저 읽다가 핵심 준비 흐름을 놓침

## Not Covered In This Slim Book

아래는 원문에 남기고 이 slim book 에서는 제외한다.

- 특정 cloud provider 설치 절차
- DHCP 상세 설정 예시
- DNS / load balancer 상세 예제 전체
- ISO 와 PXE 의 모든 세부 변형

## Source Trace

- Main source:
  [Installing on any platform](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/installing_on_any_platform/index)
- Section anchors:
  - [Prerequisites](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/installing_on_any_platform/index#prerequisites)
  - [Requirements for a cluster with user-provisioned infrastructure](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/installing_on_any_platform/index#installation-requirements-user-infra_installing-platform-agnostic)
  - [Manually creating the installation configuration file](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/installing_on_any_platform/index#installation-initializing-manual_installing-platform-agnostic)
  - [Creating the Kubernetes manifest and Ignition config files](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/installing_on_any_platform/index#installation-user-infra-generate-k8s-manifest-ignition_installing-platform-agnostic)
  - [Installing RHCOS and starting the OpenShift Container Platform bootstrap process](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/installing_on_any_platform/index#creating-machines-bare-metal_installing-platform-agnostic)

## Why This Is Better Than The Current Raw Book

- `1.3.4.7` 같은 번호가 본문 독해를 지배하지 않는다.
- 설치 준비, 자산 생성, bootstrap 시작, 검증 포인트가 분리돼 있다.
- 긴 reference manual 을 처음부터 끝까지 읽지 않아도 된다.
- 설치 담당자가 `지금 무엇을 준비하고 무엇을 생성해야 하는지`를 빠르게 파악할 수 있다.
