# 스토리지

## When To Use

OpenShift Container Platform은 VMDK(Virtual Machine Disk) 볼륨용 CSI(Container Storage Interface) VMware vSphere 드라이버를 사용하여 영구 볼륨(PV)을 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

## Prerequisites

- 사용하는 구성 요소의 요구사항을 충족하는 VMware vSphere 버전 6 인스턴스에 OpenShift Container Platform 클러스터가 설치되어 있어야 합니다. vSphere 버전 지원에 대한 자세한 내용은 vSphere에 클러스터 설치를 참조하십시오.

- 다음 절차 중 하나를 사용하여 기본 스토리지 클래스를 사용하여 이러한 볼륨을 동적으로 프로비저닝할 수 있습니다.

## Procedure

계정 간 지원을 통해 AWS EBS(Elastic File System) CSI(Container Storage Interface) 드라이버를 사용하여 하나의 AWS 계정에 OpenShift Container Platform 클러스터를 마운트하고 다른 AWS 계정에 파일 시스템을 마운트할 수 있습니다.

> **사전 요구 사항** > 관리자 권한을 사용하여 OpenShift Container Platform 클러스터에 액세스

두 개의 유효한 AWS 계정

EFS CSI Operator가 설치되었습니다. EFS CSI Operator 설치에 대한 자세한 내용은 AWS EFS CSI Driver Operator 설치 섹션을 참조하십시오.

OpenShift Container Platform 클러스터 및 EFS 파일 시스템은 모두 동일한 AWS 리전에 있어야 합니다.

다음 절차에서 사용되는 두 개의 가상 프라이빗 클라우드(VPC)가 다른 네트워크 CIDR(Classless Inter-Domain Routing) 범위를 사용하는지 확인합니다.

OpenShift Container Platform CLI()에 액세스합니다.

```shell oc ```

AWS CLI에 액세스합니다.

아래 명령줄 JSON 프로세서에 액세스합니다.

```shell jq ```

프로세스

다음 절차에서는 설정 방법을 설명합니다.

OpenShift Container Platform AWS 계정 A: VPC 내에 배포된 Red Hat OpenShift Container Platform 클러스터 v4.16 이상을 포함합니다.

AWS 계정 B: VPC(네트워크, 라우팅 테이블, 네트워크 연결 포함)를 포함합니다. EFS 파일 시스템은 이 VPC에서 생성됩니다.

계정에서 AWS EFS를 사용하려면 다음을 수행합니다.

환경을 설정합니다.
