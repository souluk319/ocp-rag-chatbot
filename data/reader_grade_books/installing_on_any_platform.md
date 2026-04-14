# Install on Any Platform

## Overview

이 문서는 사용자 제공 인프라 환경에서 OpenShift Container Platform 설치 자산을 준비하고, 부트스트랩이 완료될 때까지 확인해야 하는 핵심 절차를 정리한다.

OpenShift Container Platform 4.20 버전에서는 가상화 및 클라우드 환경을 포함한 프로비저닝한 어떤 인프라에서도 클러스터를 설치할 수 있습니다.

> **중요**
> 가상화 또는 클라우드 환경에서 OpenShift Container Platform 클러스터를 설치하려는 경우, 먼저 OpenShift Container Platform 을 비테스트 플랫폼에 배포하는 가이드라인의 정보를 검토하세요.

## Before You Begin

OpenShift Container Platform 설치 및 업데이트 프로세스에 대한 세부 사항을 검토했습니다.

클러스터 설치 방법 선택 및 사용자 준비를 위한 문서를 읽으셨습니다.

방화벽을 사용하는 경우, 클러스터가 액세스해야 하는 사이트에 대한 액세스를 허용하도록 구성했습니다.

> **참고**
> 프록시를 구성하는 경우에도 이 사이트 목록을 확인하십시오.

## Prepare the Infrastructure

OpenShift Container Platform 에서 성공적인 배포를 보장하고 클러스터 요구 사항을 충족하려면 설치 시작 전에 사용자 제공 인프라를 준비해야 합니다. 컴퓨팅, 네트워크, 저장소 구성 요소를 미리 구성하면 설치 프로그램이 올바르게 작동하기 위해 필요한 안정적인 기반을 제공합니다.

이 섹션은 OpenShift Container Platform 설치 준비를 위한 클러스터 인프라를 설정하는 데 필요한 고수준 단계를 자세히 설명합니다. 여기에는 클러스터 노드의 IP 네트워킹 및 네트워크 연결을 구성하고, 방화벽을 통해 필요한 포트를 활성화하며, 필요한 DNS 및 로드 밸런싱 인프라를 설정하는 것이 포함됩니다.

준비 작업이 완료되면 클러스터 인프라는 사용자 제공 인프라를 위한 클러스터 요구 사항 섹션에 명시된 요구 사항을 충족해야 합니다.

> **선행 조건**
> OpenShift Container Platform 4.x 테스트 통합 페이지를 검토했습니다.

사용자 제공 인프라를 위한 클러스터 요구 사항 섹션에 자세히 설명된 인프라 요구 사항을 검토했습니다.

## Create install-config.yaml

OpenShift Container Platform 배포를 사용자 정의하고 특정 네트워크 요구 사항을 충족하려면 설치 구성 파일을 수동으로 생성하세요. 이렇게 하면 설치 프로그램이 설정 과정에서 기본값 대신 사용자 정의된 설정을 사용합니다.

> **선행 조건**
> 로컬 머신에 설치 프로그램을 사용할 SSH 공개 키가 있습니다. 이 키는 디버깅 및 재해 복구 목적으로 클러스터 노드로 SSH 인증을 수행하는 데 사용할 수 있습니다.

OpenShift Container Platform 설치 프로그램과 클러스터용 pull secret 을 획득했습니다.

### 절차

```shell-session
$ mkdir <installation_directory>
```

> **중요**
> 디렉토리를 생성해야 합니다. 부트스트랩 X.509 인증서와 같은 일부 설치 자산은 짧은 만료 기간을 가지므로 설치 디렉토리를 재사용해서는 안 됩니다. 다른 클러스터 설치에서 개별 파일을 재사용하려면 해당 파일을 디렉토리로 복사할 수 있습니다. 그러나 설치 자산의 파일명은 릴리스마다 변경될 수 있습니다. 이전 OpenShift Container Platform 버전에서 설치 파일을 복사할 때는 주의하세요.

제공된 샘플 `install-config.yaml` 파일 템플릿을 커스터마이징하고 파일을 `<installation_directory>`에 저장합니다.

## Generate Manifests and Ignition Files

클러스터 정의를 사용자 정의하고 머신을 수동으로 시작하려면 Kubernetes 매니페스트 및 Ignition 설정 파일을 생성하세요. 이 자산은 특정 배포 요구 사항에 따라 클러스터 인프라를 구성하는 데 필요한 지침을 제공합니다.

설치 구성 파일은 Kubernetes 매니페스트로 변환됩니다. 매니페스트는 Ignition 설정 파일로 감싸지며, 이 파일들은 나중에 클러스터 머신을 구성하는 데 사용됩니다.

> **중요**
> The Ignition configuration file created by the OpenShift Container Platform installer includes a certificate that expires in 24 hours and is renewed at that time. If the cluster shuts down before the certificate is renewed and is restarted later after 24 hours have passed, the cluster automatically recovers the expired certificate. The exception is that you must manually approve a pending `node-bootstrapper` certificate signing request (CSR) to recover the kubelet certificate. For more information, see Recovering from expired control plane certificates.

If a certificate update is running during installation, it is recommended to use the Ignition configuration file within 12 hours after it is created to prevent installation failure. This is because the 24-hour certificate rotates between 16 and 22 hours after the cluster is installed. Using the Ignition configuration file within 12 hours avoids installation failure.

Prerequisites

You have obtained the OpenShift Container Platform installer.

You have created an `install-config.yaml` installation configuration file.

Procedure

Navigate to the directory containing the OpenShift Container Platform installer and create the Kubernetes manifests for the cluster:

```shell-session
$ ./openshift-install create manifests --dir <installation_directory>
```

Here

## Start Bootstrap

제공한 bare-metal 인프라에 OpenShift Container Platform 을 설치하려면 생성된 Ignition 설정 파일을 사용하여 Red Hat Enterprise Linux CoreOS(RHCOS) 를 설치합니다. 이러한 파일을 제공하면 기계가 재부팅된 후 부트스트랩 프로세스가 자동으로 시작되도록 보장합니다.

적절한 네트워킹, DNS, 및 로드 밸런싱 인프라를 구성한 경우, RHCOS 기계가 재부팅된 후 OpenShift Container Platform 부트스트랩 프로세스가 자동으로 시작됩니다.

기계에 RHCOS 를 설치하려면 ISO 이미지 사용 단계 또는 네트워크 PXE 부팅 단계를 따르십시오.

> **참고**
> 이 설치 문서에 포함된 컴퓨팅 노드 배포 단계는 RHCOS 전용입니다. 대신 RHEL 기반 컴퓨팅 노드를 배포하기로 선택한 경우, 시스템 업데이트 수행, 패치 적용 및 기타 모든 필요한 작업을 완료하는 것을 포함하여 모든 운영 체제 수명 주기 관리 및 유지보수에 대해 책임을 집니다. 지원되는 것은 RHEL 8 컴퓨팅 기계만입니다.

ISO 및 PXE 설치 동안 RHCOS 를 구성하려면 다음 방법을 사용할 수 있습니다:

커널 인자: 커널 인자를 사용하여 설치별 정보를 제공할 수 있습니다. 예를 들어, HTTP 서버에 업로드한 RHCOS 설치 파일의 위치 및 설치하는 노드 유형에 대한 Ignition 설정 파일의 위치를 지정할 수 있습니다. PXE 설치의 경우 `APPEND` 매개변수를 사용하여 라이브 설치程序的 커널에 인자를 전달할 수 있습니다. ISO 설치의 경우 라이브 설치 부팅 프로세스를 중단하여 커널 인자를 추가할 수 있습니다. 두 설치 경우 모두 라이브 설치程序的 지시를 위해 특수 `coreos.inst.*` 인자를 사용할 수 있으며, 표준 커널 서비스를 켜거나 끄기 위한 표준 설치 부팅 인자도 사용할 수 있습니다.

Ignition 설정: OpenShift Container Platform Ignition 설정 파일(`*.ign`) 은 설치하는 노드의 유형에 따라 다릅니다. RHCOS 설치 중에 부트스트랩, 컨트롤 플레인 또는 컴퓨팅 노드 Ignition 설정 파일의 위치를 전달하여 첫 번째 부트 시 적용되도록 합니다. 특수한 경우, 라이브 시스템에 전달할 별도의 제한된 Ignition 설정을 생성할 수 있습니다. 해당 Ignition 설정은 설치 완료 후 프로비저닝 시스템에 성공을 보고하는 것과 같은 특정 작업 집합을 수행할 수 있습니다. 이 특수 Ignition 설정은 설치된 시스템의 첫 번째 부트 시 적용되도록 `coreos-installer`에 의해 소비됩니다. 표준 컨트롤 플레인 및 컴퓨팅 노드 Ignition 설정을 라이브 ISO 에 직접 제공하지 마십시오.

`coreos-installer`: 라이브 ISO 설치자를 쉘 프롬프트로 부팅하여 첫 번째 부트 전에 다양한 방법으로 영구 시스템을 준비할 수 있습니다. 특히, `coreos-installer` 명령을 실행하여 포함할 다양한 아티팩트를 식별하고 디스크 파티션과 작업하며 네트워킹을 설정할 수 있습니다. 일부 경우에는 라이브 시스템에서 기능을 구성하고 설치된 시스템으로 복사할 수 있습니다.

## Verify Installation Readiness

OpenShift Container Platform 을 설치하려면, 클러스터 노드가 RHCOS 로 부팅된 후 Ignition 설정 파일을 사용하여 부트스트랩 프로세스를 시작해야 합니다. 클러스터가 완전히 설치되었음을 보장하려면 이 프로세스가 완료될 때까지 기다려야 합니다.

> **선행 조건**
> 클러스터에 대한 Ignition 설정 파일을 생성했습니다.

적합한 네트워크, DNS, 및 로드 밸런싱 인프라를 구성했습니다.

설치 프로그램을 획득하고 클러스터에 대한 Ignition 설정 파일을 생성했습니다.

클러스터 머신에 RHCOS 를 설치하고 OpenShift Container Platform 설치 프로그램이 생성한 Ignition 설정 파일을 제공했습니다.

머신에 직접 인터넷 액세스가 있거나 HTTP 또는 HTTPS 프록시가 사용 가능합니다.

### 절차

```shell-session
$ ./openshift-install --dir <installation_directory> wait-for bootstrap-complete \
    --log-level=info
```

여기서:

## Source Trace

- 원문 slug: `installing_on_any_platform`
- 기준 축: `install-config / manifests / ignition / bootstrap / verify`
