# 머신 관리

## 클러스터 머신 추가 및 유지 보수

이 문서에서는 OpenShift Container Platform 클러스터를 구성하는 머신을 관리하는 방법을 설명합니다. 일부 작업은 OpenShift Container Platform 클러스터의 고급 자동 머신 관리 기능을 사용하며 일부 작업은 수동으로 완료해야 합니다. 이 문서에서 설명하는 모든 작업이 모든 설치 유형에서 사용 가능한 것은 아닙니다.

## 1장. 머신 관리 개요

머신 관리를 사용하여 AWS(Amazon Web Services), Microsoft Azure, Google Cloud, RHOSP(Red Hat OpenStack Platform) 및 VMware vSphere와 같은 기본 인프라에서 유연하게 작업하여 OpenShift Container Platform 클러스터를 관리할 수 있습니다. 특정 워크로드 정책에 따라 클러스터를 제어하고 클러스터 확장 및 축소와 같은 자동 확장을 수행할 수 있습니다.

워크로드 변경에 적합한 클러스터를 사용하는 것이 중요합니다. 로드가 증가하거나 감소하면 OpenShift Container Platform 클러스터는 수평으로 확장 및 축소할 수 있습니다.

머신 관리는 CRD(사용자 정의 리소스 정의)로 구현됩니다. CRD 오브젝트는 클러스터에서 새로운 고유한 오브젝트 `Kind` 를 정의하고 Kubernetes API 서버에서 오브젝트의 전체 라이프사이클을 처리할 수 있습니다.

Machine API Operator는 다음 리소스를 프로비저닝합니다.

`MachineSet`

`머신`

`ClusterAutoscaler`

`MachineAutoscaler`

`MachineHealthCheck`

### 1.1. Machine API 개요

Machine API는 업스트림 Cluster API 프로젝트 및 사용자 정의 OpenShift Container Platform 리소스를 기반으로 하는 주요 리소스의 조합입니다.

OpenShift Container Platform 4.20 클러스터의 경우 Machine API는 클러스터 설치가 완료된 후 모든 노드 호스트 프로비저닝 관리 작업을 수행합니다. 이 시스템으로 인해 OpenShift Container Platform 4.20은 퍼블릭 또는 프라이빗 클라우드 인프라에 더하여 탄력적이고 동적인 프로비저닝 방법을 제공합니다.

두 가지 주요 리소스는 다음과 같습니다.

Machine

노드의 호스트를 설명하는 기본 단위입니다. 머신에는 `providerSpec` 사양이 있으며 이는 다른 클라우드 플랫폼에 제공되는 컴퓨팅 노드 유형을 설명합니다. 예를 들어 컴퓨팅 노드의 머신 유형은 특정 시스템 유형과 필수 메타데이터를 정의할 수 있습니다.

머신 세트

`MachineSet` 리소스는 컴퓨팅 머신 그룹입니다. 컴퓨팅 머신 세트는 컴퓨팅 머신에 연관되어 있고 복제본 세트는 pod에 연관되어 있습니다. 더 많은 컴퓨팅 머신이 필요하거나 확장해야 하는 경우 컴퓨팅 요구 사항에 맞게 `MachineSet` 리소스의 `replicas` 필드를 변경합니다.

주의

컨트롤 플레인 시스템은 컴퓨팅 머신 세트로 관리할 수 없습니다.

컨트롤 플레인 머신 세트는 컴퓨팅 머신에 제공하는 컴퓨팅 머신 세트와 유사한 지원되는 컨트롤 플레인 시스템에 대한 관리 기능을 제공합니다.

자세한 내용은 "컨트롤 플레인 머신 관리"를 참조하십시오.

다음 사용자 지정 리소스는 클러스터에 더 많은 기능을 추가할 수 있습니다.

머신 자동 스케일러

`MachineAutoscaler` 리소스는 클라우드에서 컴퓨팅 머신을 자동으로 확장합니다. 지정된 컴퓨팅 머신 세트에서 노드의 최소 및 최대 스케일링 경계를 설정할 수 있으며 머신 자동 스케일러는 해당 노드 범위를 유지합니다.

`MachineAutoscaler` 객체는 `ClusterAutoscaler` 객체를 설정한 후에 사용할 수 있습니다. `ClusterAutoscaler` 및 `MachineAutoscaler` 리소스는 모두 `ClusterAutoscalerOperator` 오브젝트에서 사용 가능합니다.

Cluster autoscaler

이 리소스는 업스트림 클러스터 자동 스케일러 프로젝트를 기반으로 합니다. OpenShift Container Platform 구현에서는 컴퓨팅 머신 세트 API를 확장하여 Machine API와 통합됩니다. 클러스터 자동 스케일러를 사용하여 다음과 같은 방법으로 클러스터를 관리할 수 있습니다.

코어, 노드, 메모리, GPU와 같은 리소스에 대한 클러스터 전체 스케일링 제한을 설정합니다.

중요도가 낮은 Pod에 대해 클러스터가 Pod 및 새 노드가 온라인 상태가 되지 않도록 우선 순위를 설정합니다.

노드를 확장할 수는 있지만 축소할 수 없도록 스케일링 정책을 설정합니다.

머신 상태 점검

`MachineHealthCheck` 리소스는 머신의 비정상적인 상태를 감지하여 삭제한 후 지원되는 플랫폼에서 새 머신을 생성합니다.

OpenShift Container Platform 버전 3.11에서는 클러스터가 머신 프로비저닝을 관리하지 않았기 때문에 다중 영역 아키텍처를 쉽게 롤아웃할 수 없었습니다. OpenShift Container Platform 버전 4.1부터 이러한 프로세스가 더 쉬워졌습니다. 각 컴퓨팅 머신 세트의 범위는 단일 영역으로 지정되므로 설치 프로그램은 사용자를 대신하여 가용성 영역 전체에 컴퓨팅 머신 세트를 보냅니다. 또한 계산이 동적이고 영역 장애가 발생하여 머신을 재조정해야하는 경우 처리할 수 있는 영역을 확보할 수 있습니다. 여러 가용성 영역이 없는 글로벌 Azure 리전에서는 가용성 세트를 사용하여 고가용성을 보장할 수 있습니다. Autoscaler는 클러스터의 수명 기간 동안 최적의 균형을 유지합니다.

추가 리소스

머신 단계 및 라이프사이클

### 1.2. 컴퓨팅 머신 관리

클러스터 관리자는 다음 작업을 수행할 수 있습니다.

다음 클라우드 공급자에 대한 컴퓨팅 머신 세트를 생성합니다.

AWS

Azure

Azure Stack Hub

Google Cloud

IBM Cloud

IBM Power Virtual Server

Nutanix

RHOSP

vSphere

베어 메탈 배포를 위한 머신 세트 생성: 베어 메탈에서 컴퓨팅 머신 세트 생성

컴퓨팅 머신 세트에서 머신을 추가하거나 제거하여 컴퓨팅 머신 세트를 수동으로 확장합니다.

`MachineSet` YAML 구성 파일을 통해 컴퓨팅 머신 세트를 수정합니다.

머신을 삭제합니다.

인프라 컴퓨팅 머신 세트를 생성합니다.

머신 풀에서 손상된 머신을 자동으로 수정하도록 머신 상태 점검을 구성하고 배포합니다.

### 1.3. 컨트롤 플레인 시스템 관리

클러스터 관리자는 다음 작업을 수행할 수 있습니다.

다음 클라우드 공급자에 대한 컨트롤 플레인 머신 세트로 컨트롤 플레인 구성을 업데이트합니다.

Amazon Web Services

Google Cloud

Microsoft Azure

Nutanix

Red Hat OpenStack Platform (RHOSP)

VMware vSphere

머신 상태 점검을 구성하고 배포하여 비정상 컨트롤 플레인 시스템을 자동으로 복구합니다.

### 1.4. OpenShift Container Platform 클러스터에 자동 스케일링 적용

OpenShift Container Platform 클러스터를 자동으로 스케일링하여 워크로드 변경에 대한 유연성을 보장할 수 있습니다. 클러스터를 자동 스케일링 하려면 먼저 클러스터 자동 스케일러를 배포한 다음 각 컴퓨팅 머신 세트의 머신 자동 스케일러를 배포해야 합니다.

클러스터 자동 스케일러 는 배포 요구 사항에 따라 클러스터 크기를 늘리고 줄입니다.

머신 자동 스케일러 는 OpenShift Container Platform 클러스터에 배포하는 컴퓨팅 머신 세트의 머신 수를 조정합니다.

### 1.5. 사용자 프로비저닝 인프라에 컴퓨팅 머신 추가

사용자 프로비저닝 인프라는 OpenShift Container Platform을 호스팅하는 컴퓨팅, 네트워크 및 스토리지 리소스와 같은 인프라를 배포할 수 있는 환경입니다. 설치 프로세스 중 또는 설치 프로세스 후 사용자 프로비저닝 인프라의 클러스터에 컴퓨팅 머신을 추가할 수 있습니다.

### 2.1. AWS에서 컴퓨팅 머신 세트 생성

AWS(Amazon Web Services)의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.1.1. AWS에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

샘플 YAML은 `us-east-1a` AWS(Amazon Web Services) 로컬 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 생성합니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>-<zone>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<zone>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<zone>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          ami:
            id: ami-046fe691f52a953f9
          apiVersion: machine.openshift.io/v1beta1
          blockDevices:
            - ebs:
                iops: 0
                volumeSize: 120
                volumeType: gp2
          credentialsSecret:
            name: aws-cloud-credentials
          deviceIndex: 0
          iamInstanceProfile:
            id: <infrastructure_id>-worker-profile
          instanceType: m6i.large
          kind: AWSMachineProviderConfig
          placement:
            availabilityZone: <zone>
            region: <region>
          securityGroups:
            - filters:
                - name: tag:Name
                  values:
                    - <infrastructure_id>-node
            - filters:
                - name: tag:Name
                  values:
                    - <infrastructure_id>-lb
          subnet:
            filters:
              - name: tag:Name
                values:
                  - <infrastructure_id>-private-<zone>
          tags:
            - name: kubernetes.io/cluster/<infrastructure_id>
              value: owned
            - name: <custom_tag_name>
              value: <custom_tag_value>
          userDataSecret:
            name: worker-user-data
```

1. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 인프라 ID, 역할 노드 레이블 및 영역을 지정합니다.

3. 추가할 역할 노드 레이블을 지정합니다.

4. OpenShift Container Platform 노드의 AWS 영역에 유효한 RHCOS(Red Hat Enterprise Linux CoreOS) Amazon 머신 이미지(AMI)를 지정합니다. AWS Marketplace 이미지를 사용하려면 해당 리전의 AMI ID를 받으려면 AWS Marketplace 에서 OpenShift Container Platform 서브스크립션을 완료해야 합니다.

```shell-session
$ oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.ami.id}{"\n"}' \
    get machineset/<infrastructure_id>-<role>-<zone>
```

5. 영역 이름을 지정합니다(예: `us-east-1a`).

6. 리전을 지정합니다(예: `us-east-1`).

7. 인프라 ID 및 영역을 지정합니다.

8. 선택 사항: 클러스터의 사용자 지정 태그 데이터를 지정합니다. 예를 들어 `Email:admin-email@example.com` 의 `name:value` 쌍을 지정하여 관리자 연락처 이메일 주소를 추가할 수 있습니다.

참고

`install-config.yml` 파일에서 설치 중에 사용자 지정 태그를 지정할 수도 있습니다. `install-config.yml` 파일과 머신 세트에 동일한 `name` 데이터가 있는 태그가 포함된 경우 머신 세트의 태그 값이 `install-config.yml` 파일의 태그 값보다 우선합니다.

#### 2.1.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

다른 가용성 영역에 컴퓨팅 머신 세트가 필요한 경우 이 프로세스를 반복하여 더 많은 컴퓨팅 머신 세트를 생성합니다.

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.1.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

#### 2.1.4. 머신 세트를 사용하여 Elastic Fabric Adapter 인스턴스에 대한 배치 그룹에 머신 할당

기존 AWS 배치 그룹 내에서 EBS(Elastic Fabric Adapter) 인스턴스에 머신을 배포하도록 머신 세트를 구성할 수 있습니다.

EFA 인스턴스에는 배치 그룹이 필요하지 않으며 EFA 구성 이외의 용도로 배치 그룹을 사용할 수 있습니다. 이 예에서는 둘 다 사용하여 지정된 배치 그룹 내의 시스템의 네트워크 성능을 향상시킬 수 있는 구성을 보여줍니다.

사전 요구 사항

AWS 콘솔에 배치 그룹을 생성하셨습니다.

참고

생성하는 배치 그룹 유형에 대한 규칙 및 제한 사항이 의도한 사용 사례와 호환되는지 확인합니다.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          instanceType: <supported_instance_type>
          networkInterfaceType: EFA
          placement:
            availabilityZone: <zone>
            region: <region>
          placementGroupName: <placement_group>
          placementGroupPartition: <placement_group_partition_number>
# ...
```

1. EFA를 지원하는 인스턴스 유형을 지정합니다.

2. `EFA` 네트워크 인터페이스 유형을 지정합니다.

3. 영역을 지정합니다(예: `us-east-1a`).

4. 리전을 지정합니다(예: `us-east-1`).

5. 머신을 배포할 기존 AWS 배치 그룹의 이름을 지정합니다.

6. 선택 사항: 시스템을 배포할 기존 AWS 배치 그룹의 파티션 번호를 지정합니다.

검증

AWS 콘솔에서 머신 세트가 생성된 머신을 찾아 머신 속성에서 다음을 확인합니다.

placement group 필드에는 시스템 세트의 `placementGroupName` 매개변수에 대해 지정한 값이 있습니다.

파티션 번호 필드에는 머신 세트의 `placementGroup Cryostat` 매개변수에 대해 지정한 값이 있습니다.

interface 유형 필드는 EFA를 사용함을 나타냅니다.

#### 2.1.5. Amazon EC2 인스턴스 메타데이터 서비스에 대한 머신 세트 옵션

머신 세트를 사용하여 특정 버전의 Amazon EC2 인스턴스 메타데이터 서비스(IMDS)를 사용하는 머신을 생성할 수 있습니다. 머신 세트는 IMDSv1 및 IMDSv2 또는 IMDSv2 를 사용해야 하는 머신을 생성할 수 있습니다.

참고

OpenShift Container Platform 버전 4.6 또는 이전 버전으로 생성된 AWS 클러스터에서 IMDSv2를 사용하려면 부팅 이미지를 업데이트해야 합니다. 자세한 내용은 "업데이트된 부팅 이미지"를 참조하십시오.

원하는 IMDS 구성으로 새 컴퓨팅 머신을 배포하려면 적절한 값으로 컴퓨팅 머신 세트 YAML 파일을 생성합니다. 머신 세트가 확장될 때 기존 머신 세트를 편집하여 기본 IMDS 구성으로 새 머신을 생성할 수도 있습니다.

중요

IMDSv2가 필요한 머신을 생성하도록 머신 세트를 구성하기 전에 AWS 메타데이터 서비스와 상호 작용하는 모든 워크로드가 IMDSv2를 지원하는지 확인합니다.

추가 리소스

업데이트된 부팅 이미지

#### 2.1.5.1. 머신 세트를 사용하여 IMDS 구성

머신의 머신 세트 YAML 파일에서 `metadataServiceOptions.authentication` 값을 추가하거나 편집하여 IMDSv2의 사용이 필요한지 여부를 지정할 수 있습니다.

사전 요구 사항

IMDSv2를 사용하려면 OpenShift Container Platform 버전 4.7 이상을 사용하여 AWS 클러스터가 생성되어 있어야 합니다.

프로세스

`providerSpec` 필드 아래에 다음 행을 추가하거나 편집합니다.

```yaml
providerSpec:
  value:
    metadataServiceOptions:
      authentication: Required
```

1. IMDSv2를 요구하려면 매개 변수 값을 `Required` 로 설정합니다. IMDSv1 및 IMDSv2를 모두 사용할 수 있도록 하려면 매개 변수 값을 `Optional` 로 설정합니다. 값을 지정하지 않으면 IMDSv1 및 IMDSv2가 모두 허용됩니다.

#### 2.1.6. 머신을 Dedicated 인스턴스로 배포하는 머신 세트

AWS에서 실행 중인 머신 세트를 생성하여 머신을 Dedicated 인스턴스로 배포할 수 있습니다. Dedicated 인스턴스는 단일 고객 전용 하드웨어의 VPC(가상 프라이빗 클라우드)에서 실행됩니다. 이러한 Amazon EC2 인스턴스는 호스트 하드웨어 수준에서 물리적으로 분리됩니다. Dedicated 인스턴스의 분리는 인스턴스가 하나의 유료 계정에 연결된 다른 AWS 계정에 속하는 경우에도 발생합니다. 하지만 전용이 아닌 다른 인스턴스는 동일한 AWS 계정에 속하는 경우 Dedicated 인스턴스와 하드웨어를 공유할 수 있습니다.

공용 또는 전용 테넌시가 있는 인스턴스는 Machine API에서 지원됩니다. 공용 테넌시가 있는 인스턴스는 공유 하드웨어에서 실행됩니다. 공용 테넌시는 기본 테넌시입니다. 전용 테넌트가 있는 인스턴스는 단일 테넌트 하드웨어에서 실행됩니다.

#### 2.1.6.1. 머신 세트를 사용하여 Dedicated 인스턴스 생성

Machine API 통합을 사용하여 Dedicated 인스턴스에서 지원하는 머신을 실행할 수 있습니다. 머신 세트 YAML 파일의 `tenancy` 필드를 설정하여 AWS에서 전용 인스턴스를 시작합니다.

프로세스

`providerSpec` 필드에서 전용 테넌트를 지정합니다.

```yaml
providerSpec:
  placement:
    tenancy: dedicated
```

#### 2.1.7. 머신을 Spot 인스턴스로 배포하는 머신 세트

AWS에서 실행되는 컴퓨팅 머신 세트를 생성하여 보장되지 않는 Spot 인스턴스로 머신을 배포하면 비용을 절감할 수 있습니다. Spot 인스턴스는 사용되지 않는 AWS EC2 용량을 사용하며 온 디맨드 인스턴스보다 저렴합니다. 일괄 처리 또는 상태 비저장, 수평적으로 확장 가능한 워크로드와 같이 인터럽트를 허용할 수 있는 워크로드에 Spot 인스턴스를 사용할 수 있습니다.

AWS EC2는 언제든지 Spot 인스턴스를 종료할 수 있습니다. AWS는 중단이 발생하면 사용자에게 2 분 동안 경고 메세지를 보냅니다. OpenShift Container Platform은 AWS가 종료에 대한 경고를 발행할 때 영향을 받는 인스턴스에서 워크로드를 제거하기 시작합니다.

다음과 같은 이유로 Spot 인스턴스를 사용할 때 중단될 수 있습니다.

인스턴스 가격이 최대 가격을 초과합니다.

Spot 인스턴스에 대한 수요가 증가합니다.

Spot 인스턴스의 공급이 감소합니다.

AWS가 인스턴스를 종료하면 Spot 인스턴스 노드에서 실행중인 종료 프로세스가 머신 리소스를 삭제합니다. 컴퓨팅 머신 세트 `replicas` 수량을 충족하기 위해 컴퓨팅 머신 세트는 Spot 인스턴스를 요청하는 머신을 생성합니다.

#### 2.1.7.1. 컴퓨팅 머신 세트를 사용하여 Spot 인스턴스 생성

컴퓨팅 머신 세트 YAML 파일에 `spotMarketOptions` 를 추가하여 AWS에서 Spot 인스턴스를 시작할 수 있습니다.

프로세스

`providerSpec` 필드 아래에 다음 행을 추가합니다.

```yaml
providerSpec:
  value:
    spotMarketOptions: {}
```

선택 옵션으로 `spotMarketOptions.maxPrice` 필드를 설정하여 Spot 인스턴스의 비용을 제한할 수 있습니다. 예를 들어 `maxPrice: '2.50'` 을 설정할 수 있습니다.

`maxPrice` 가 설정된 경우 이 값은 시간당 최대 Spot 가격으로 사용됩니다. 이 값이 설정되지 않은 경우 기본적으로 최대 가격은 온 디맨드 인스턴스 가격까지 청구됩니다.

참고

기본적인 온 디맨드 가격을 `maxPrice` 값으로 사용하여 Spot 인스턴스의 최대 가격을 설정하지 않는 것이 좋습니다.

#### 2.1.8. 머신 세트를 사용하여 용량 예약 구성

OpenShift Container Platform 버전 4.20 이상에서는 온디맨드 용량 예약 및 ML의 용량 블록을 포함하여 Amazon Web Services 클러스터에서 용량 예약을 지원합니다.

사용자가 정의한 용량 요청의 매개변수와 일치하는 사용 가능한 리소스에 머신을 배포하도록 머신 세트를 구성할 수 있습니다. 이러한 매개변수는 예약할 인스턴스 유형, 리전 및 인스턴스 수를 지정합니다. 용량 예약이 용량 요청을 수용할 수 있는 경우 배포에 성공합니다.

이 AWS 오퍼링에 대한 제한 사항 및 제안된 사용 사례를 포함한 자세한 내용은 AWS 문서의 온디맨드 용량 예약 및 ML 용량 블록을 참조하십시오.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

온디맨드 용량 예약 또는 ML의 용량 블록을 구입하셨습니다. 자세한 내용은 AWS 문서의 온디맨드 용량 예약 및 ML 용량 블록을 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          capacityReservationId: <capacity_reservation>
          marketType: <market_type>
# ...
```

1. 머신 세트에서 머신을 배포할 ML 또는 온 디맨드 용량 예약의 용량 블록 ID를 지정합니다.

2. 사용할 시장 유형을 지정합니다. 다음 값이 유효합니다.

`CapacityBlock`

ML 용 용량 블록과 함께 이 시장 유형을 사용합니다.

`OnDemand`

온디맨드 용량 예약과 함께 이 시장 유형을 사용합니다.

`스팟`

Spot 인스턴스와 함께 이 시장 유형을 사용합니다. 이 옵션은 용량 예약과 호환되지 않습니다.

검증

시스템 배포를 확인하려면 다음 명령을 실행하여 머신 세트에서 생성한 머신을 나열합니다.

```shell-session
$ oc get machines.machine.openshift.io \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machineset=<machine_set_name>
```

여기서 `<machine_set_name>` 은 컴퓨팅 머신 세트의 이름입니다.

출력에서 나열된 시스템의 특성이 용량 예약의 매개변수와 일치하는지 확인합니다.

#### 2.1.9. 기존 OpenShift Container Platform 클러스터에 GPU 노드 추가

기본 컴퓨팅 머신 세트 구성을 복사하고 수정하여 AWS EC2 클라우드 공급자에 대한 GPU 사용 머신 세트 및 머신을 생성할 수 있습니다.

지원되는 인스턴스 유형에 대한 자세한 내용은 다음 NVIDIA 설명서를 참조하십시오.

NVIDIA GPU Operator 커뮤니티 지원 매트릭스

NVIDIA AI Enterprise 지원 매트릭스

프로세스

다음 명령을 실행하여 기존 노드, 시스템 및 머신 세트를 확인합니다. 각 노드는 특정 AWS 리전 및 OpenShift Container Platform 역할을 사용하는 머신 정의 인스턴스입니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME                                        STATUS   ROLES                  AGE     VERSION
ip-10-0-52-50.us-east-2.compute.internal    Ready    worker                 3d17h   v1.33.4
ip-10-0-58-24.us-east-2.compute.internal    Ready    control-plane,master   3d17h   v1.33.4
ip-10-0-68-148.us-east-2.compute.internal   Ready    worker                 3d17h   v1.33.4
ip-10-0-68-68.us-east-2.compute.internal    Ready    control-plane,master   3d17h   v1.33.4
ip-10-0-72-170.us-east-2.compute.internal   Ready    control-plane,master   3d17h   v1.33.4
ip-10-0-74-50.us-east-2.compute.internal    Ready    worker                 3d17h   v1.33.4
```

다음 명령을 실행하여 `openshift-machine-api` 네임스페이스에 있는 머신 및 머신 세트를 확인합니다. 각 컴퓨팅 머신 세트는 AWS 리전 내의 다른 가용성 영역과 연결되어 있습니다. 설치 프로그램은 가용성 영역에서 컴퓨팅 시스템을 자동으로 로드 밸런싱합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                        DESIRED   CURRENT   READY   AVAILABLE   AGE
preserve-dsoc12r4-ktjfc-worker-us-east-2a   1         1         1       1           3d11h
preserve-dsoc12r4-ktjfc-worker-us-east-2b   2         2         2       2           3d11h
```

다음 명령을 실행하여 `openshift-machine-api` 네임스페이스에 있는 머신을 확인합니다. 현재 머신 세트당 하나의 컴퓨팅 시스템만 있지만, 컴퓨팅 머신 세트를 확장하여 특정 리전 및 영역에 노드를 추가할 수 있습니다.

```shell-session
$ oc get machines -n openshift-machine-api | grep worker
```

```shell-session
preserve-dsoc12r4-ktjfc-worker-us-east-2a-dts8r      Running   m5.xlarge   us-east-2   us-east-2a   3d11h
preserve-dsoc12r4-ktjfc-worker-us-east-2b-dkv7w      Running   m5.xlarge   us-east-2   us-east-2b   3d11h
preserve-dsoc12r4-ktjfc-worker-us-east-2b-k58cw      Running   m5.xlarge   us-east-2   us-east-2b   3d11h
```

다음 명령을 실행하여 기존 컴퓨팅 `MachineSet` 정의 중 하나의 사본을 만들고 결과를 JSON 파일로 출력합니다. GPU 지원 컴퓨팅 머신 세트 정의의 기반이 됩니다.

```shell-session
$ oc get machineset preserve-dsoc12r4-ktjfc-worker-us-east-2a -n openshift-machine-api -o json > <output_file.json>
```

JSON 파일을 편집하고 새 `MachineSet` 정의를 다음과 같이 변경합니다.

`worker` 를 `gpu` 로 바꿉니다. 이 이름은 새 머신 세트의 이름이 됩니다.

새 `MachineSet` 정의의 인스턴스 유형을 NVIDIA Cryostat T4 GPU를 포함하는 `g4dn` 으로 변경합니다. AWS `g4dn` 인스턴스 유형에 대한 자세한 내용은 가속 컴퓨팅 을 참조하십시오.

```shell-session
$ jq .spec.template.spec.providerSpec.value.instanceType preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a.json

"g4dn.xlarge"
```

< `output_file.json` > 파일은 `preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a.json` 로 저장됩니다.

`preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a.json` 에서 다음 필드를 업데이트합니다.

`.metadata.name` 은 `gpu` 가 포함된 이름의 이름입니다.

`.spec.selector.matchLabels["machine.openshift.io/cluster-api-machineset"]` 을 새 `.metadata.name` 과 일치시킵니다.

`.spec.template.metadata.labels["machine.openshift.io/cluster-api-machineset"]` 을 새 `.metadata.name` 과 일치시킵니다.

`.spec.template.spec.providerSpec.value.instanceType` 을 `g4dn.xlarge` 으로 설정합니다.

변경 사항을 확인하려면 다음 명령을 실행하여 원래 컴퓨팅 정의와 새 GPU 사용 노드 정의의 `diff` 를 수행합니다.

```shell-session
$ oc -n openshift-machine-api get preserve-dsoc12r4-ktjfc-worker-us-east-2a -o json | diff preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a.json -
```

```shell-session
10c10

< "name": "preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a",
---
> "name": "preserve-dsoc12r4-ktjfc-worker-us-east-2a",

21c21

< "machine.openshift.io/cluster-api-machineset": "preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a"
---
> "machine.openshift.io/cluster-api-machineset": "preserve-dsoc12r4-ktjfc-worker-us-east-2a"

31c31

< "machine.openshift.io/cluster-api-machineset": "preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a"
---
> "machine.openshift.io/cluster-api-machineset": "preserve-dsoc12r4-ktjfc-worker-us-east-2a"

60c60

< "instanceType": "g4dn.xlarge",
---
> "instanceType": "m5.xlarge",
```

다음 명령을 실행하여 정의에서 GPU 지원 컴퓨팅 머신 세트를 생성합니다.

```shell-session
$ oc create -f preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a.json
```

```shell-session
machineset.machine.openshift.io/preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a created
```

검증

다음 명령을 실행하여 생성한 머신 세트를 확인합니다.

```shell-session
$ oc -n openshift-machine-api get machinesets | grep gpu
```

MachineSet 복제본 수는 `1` 로 설정되므로 새 `Machine` 개체가 자동으로 생성됩니다.

```shell-session
preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a   1         1         1       1           4m21s
```

다음 명령을 실행하여 머신 세트에서 생성한 `Machine` 오브젝트를 확인합니다.

```shell-session
$ oc -n openshift-machine-api get machines | grep gpu
```

```shell-session
preserve-dsoc12r4-ktjfc-worker-gpu-us-east-2a    running    g4dn.xlarge   us-east-2   us-east-2a  4m36s
```

노드에 네임스페이스를 지정할 필요가 없습니다. 노드 정의는 클러스터 범위입니다.

#### 2.1.10. Node Feature Discovery Operator 배포

GPU 지원 노드를 생성한 후 예약할 수 있도록 GPU 사용 노드를 검색해야 합니다. 이렇게 하려면 NFD(Node Feature Discovery) Operator를 설치합니다. NFD Operator는 노드에서 하드웨어 장치 기능을 식별합니다. 이는 인프라 노드에서 하드웨어 리소스를 식별하고 카탈로그하는 일반적인 문제를 해결하여 OpenShift Container Platform에서 사용할 수 있도록 합니다.

프로세스

OpenShift Container Platform 콘솔의 소프트웨어 카탈로그에서 Node Feature Discovery Operator를 설치합니다.

NFD Operator를 설치한 후 설치된 Operator 목록에서 Node Feature Discovery 를 선택하고 Create instance 를 선택합니다. 이렇게 하면 각 컴퓨팅 노드에 대해 `nfd-master` 및 `nfd-worker`, 하나의 `nfd-worker` Pod가 `openshift-nfd` 네임스페이스에 설치됩니다.

다음 명령을 실행하여 Operator가 설치되어 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n openshift-nfd
```

```shell-session
NAME                                       READY    STATUS     RESTARTS   AGE

nfd-controller-manager-8646fcbb65-x5qgk    2/2      Running 7  (8h ago)   1d
```

콘솔에 설치된 Oerator로 이동하여 Create Node Feature Discovery 를 선택합니다.

생성 을 선택하여 NFD 사용자 정의 리소스를 빌드합니다. 이렇게 하면 하드웨어 리소스에 대해 OpenShift Container Platform 노드를 폴링하고 카탈로그하는 `openshift-nfd` 네임스페이스에 NFD Pod가 생성됩니다.

검증

빌드에 성공하면 다음 명령을 실행하여 NFD Pod가 각 노드에서 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n openshift-nfd
```

```shell-session
NAME                                       READY   STATUS      RESTARTS        AGE
nfd-controller-manager-8646fcbb65-x5qgk    2/2     Running     7 (8h ago)      12d
nfd-master-769656c4cb-w9vrv                1/1     Running     0               12d
nfd-worker-qjxb2                           1/1     Running     3 (3d14h ago)   12d
nfd-worker-xtz9b                           1/1     Running     5 (3d14h ago)   12d
```

NFD Operator는 벤더 PCI ID를 사용하여 노드의 하드웨어를 식별합니다. NVIDIA는 PCI ID `10de` 를 사용합니다.

다음 명령을 실행하여 NFD Operator가 검색한 NVIDIA GPU를 확인합니다.

```shell-session
$ oc describe node ip-10-0-132-138.us-east-2.compute.internal | egrep 'Roles|pci'
```

```shell-session
Roles: worker

feature.node.kubernetes.io/pci-1013.present=true

feature.node.kubernetes.io/pci-10de.present=true

feature.node.kubernetes.io/pci-1d0f.present=true
```

`10de` 는 GPU 사용 노드의 노드 기능 목록에 나타납니다. 즉, NFD Operator가 GPU 지원 MachineSet에서 노드를 올바르게 식별했습니다.

### 2.2. Azure에서 컴퓨팅 머신 세트 생성

Microsoft Azure의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.2.1. Azure에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 리전의 `1` Microsoft Azure 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 만듭니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <role>
    machine.openshift.io/cluster-api-machine-type: <role>
  name: <infrastructure_id>-<role>-<region>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
    spec:
      metadata:
        creationTimestamp: null
        labels:
          machine.openshift.io/cluster-api-machineset: <machineset_name>
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/<infrastructure_id>-rg/providers/Microsoft.Compute/galleries/gallery_<infrastructure_id>/images/<infrastructure_id>-gen2/versions/latest
            sku: ""
            version: ""
          internalLoadBalancer: ""
          kind: AzureMachineProviderSpec
          location: <region>
          managedIdentity: <infrastructure_id>-identity
          metadata:
            creationTimestamp: null
          natRule: null
          networkResourceGroup: ""
          osDisk:
            diskSizeGB: 128
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: ""
          resourceGroup: <infrastructure_id>-rg
          sshPrivateKey: ""
          sshPublicKey: ""
          tags:
            <custom_tag_name_1>: <custom_tag_value_1>
            <custom_tag_name_2>: <custom_tag_value_2>
          subnet: <infrastructure_id>-<role>-subnet
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_D4s_v3
          vnet: <infrastructure_id>-vnet
          zone: "1"
```

1. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

다음 명령을 실행하여 서브넷을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.subnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

다음 명령을 실행하여 vnet을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.vnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

2. 추가할 노드 레이블을 지정합니다.

3. 인프라 ID, 노드 레이블, 리전을 지정합니다.

4. 컴퓨팅 머신 세트의 이미지 세부 정보를 지정합니다. Azure Marketplace 이미지를 사용하려면 "Azure Marketplace 오퍼링 사용"을 참조하십시오.

5. 인스턴스 유형과 호환되는 이미지를 지정합니다. 설치 프로그램에서 생성한 Hyper-V generation V2 이미지에는 `-gen2` 접미사가 있지만 V1 이미지의 접미사 없이 이름이 동일합니다.

6. 머신을 배치할 리전을 지정합니다.

7. 선택 사항: 머신 세트에서 사용자 지정 태그를 지정합니다. < `custom_tag_name` > 필드에 태그 이름과 < `custom_tag_value` > 필드에 해당 태그 값을 입력합니다.

8. 머신을 배치할 리전 내 영역을 지정합니다. 해당 리전에서 지정하는 영역을 지원하는지 확인합니다.

중요

리전에서 가용성 영역을 지원하는 경우 영역을 지정해야 합니다. 영역을 지정하면 Pod에 영구 볼륨 연결이 필요한 경우 볼륨 노드 유사성 오류가 발생하지 않습니다. 이를 위해 동일한 리전의 각 영역에 대한 컴퓨팅 머신 세트를 생성할 수 있습니다.

#### 2.2.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.2.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

#### 2.2.4. Azure Marketplace 오퍼링 사용

Azure에서 실행되는 머신 세트를 생성하여 Azure Marketplace 오퍼링을 사용하는 머신을 배포할 수 있습니다. 이 오퍼링을 사용하려면 먼저 Azure Marketplace 이미지를 가져와야 합니다. 이미지를 가져올 때 다음을 고려하십시오.

이미지가 동일하지만 Azure Marketplace 게시자는 지역에 따라 다릅니다. 북미에 있는 경우 게시자로 `redhat` 을 지정합니다. EMEA에 있는 경우 게시자로 `redhat-limited` 를 지정합니다.

이 제안에는 `rh-ocp-worker` SKU 및 `rh-ocp-worker-gen1` SKU가 포함됩니다. `rh-ocp-worker` SKU는 Hyper-V 생성 버전 2 VM 이미지를 나타냅니다. OpenShift Container Platform에서 사용되는 기본 인스턴스 유형은 버전 2와 호환됩니다. 버전 1과 호환되는 인스턴스 유형을 사용하려면 `rh-ocp-worker-gen1` SKU와 연결된 이미지를 사용합니다. `rh-ocp-worker-gen1` SKU는 Hyper-V 버전 1 VM 이미지를 나타냅니다.

중요

Azure Marketplace를 사용하여 이미지 설치는 64비트 ARM 인스턴스가 있는 클러스터에서 지원되지 않습니다.

Azure Marketplace 이미지를 사용하도록 컴퓨팅 머신의 RHCOS 이미지만 수정해야 합니다. 컨트롤 플레인 머신 및 인프라 노드에는 OpenShift Container Platform 서브스크립션이 필요하지 않으며 기본적으로 공용 RHCOS 기본 이미지를 사용하므로 Azure에서 서브스크립션 비용이 발생하지 않습니다. 따라서 클러스터 기본 부팅 이미지 또는 컨트롤 플레인 부팅 이미지를 수정해서는 안 됩니다. Azure Marketplace 이미지를 적용하면 복구할 수 없는 추가 라이센싱 비용이 발생합니다.

사전 요구 사항

Azure CLI 클라이언트 `(az)` 를 설치했습니다.

Azure 계정은 제공할 수 있으며 Azure CLI 클라이언트를 사용하여 이 계정에 로그인했습니다.

프로세스

다음 명령 중 하나를 실행하여 사용 가능한 모든 OpenShift Container Platform 이미지를 표시합니다.

```shell-session
$  az vm image list --all --offer rh-ocp-worker --publisher redhat -o table
```

```shell-session
Offer          Publisher       Sku                 Urn                                                             Version
-------------  --------------  ------------------  --------------------------------------------------------------  -----------------
rh-ocp-worker  RedHat          rh-ocp-worker       RedHat:rh-ocp-worker:rh-ocp-worker:4.17.2024100419              4.17.2024100419
rh-ocp-worker  RedHat          rh-ocp-worker-gen1  RedHat:rh-ocp-worker:rh-ocp-worker-gen1:4.17.2024100419         4.17.2024100419
```

```shell-session
$  az vm image list --all --offer rh-ocp-worker --publisher redhat-limited -o table
```

```shell-session
Offer          Publisher       Sku                 Urn                                                                     Version
-------------  --------------  ------------------  --------------------------------------------------------------          -----------------
rh-ocp-worker  redhat-limited  rh-ocp-worker       redhat-limited:rh-ocp-worker:rh-ocp-worker:4.17.2024100419              4.17.2024100419
rh-ocp-worker  redhat-limited  rh-ocp-worker-gen1  redhat-limited:rh-ocp-worker:rh-ocp-worker-gen1:4.17.2024100419         4.17.2024100419
```

참고

컴퓨팅 및 컨트롤 플레인 노드에 사용할 수 있는 최신 이미지를 사용합니다. 필요한 경우 설치 프로세스의 일부로 VM이 자동으로 업그레이드됩니다.

다음 명령 중 하나를 실행하여 제안의 이미지를 검사합니다.

```shell-session
$ az vm image show --urn redhat:rh-ocp-worker:rh-ocp-worker:<version>
```

```shell-session
$ az vm image show --urn redhat-limited:rh-ocp-worker:rh-ocp-worker:<version>
```

다음 명령 중 하나를 실행하여 제안 조건을 검토합니다.

```shell-session
$ az vm image terms show --urn redhat:rh-ocp-worker:rh-ocp-worker:<version>
```

```shell-session
$ az vm image terms show --urn redhat-limited:rh-ocp-worker:rh-ocp-worker:<version>
```

다음 명령 중 하나를 실행하여 제공 조건을 수락하십시오.

```shell-session
$ az vm image terms accept --urn redhat:rh-ocp-worker:rh-ocp-worker:<version>
```

```shell-session
$ az vm image terms accept --urn redhat-limited:rh-ocp-worker:rh-ocp-worker:<version>
```

제안의 이미지 세부 정보, 특히 `publisher`, `offer`, `sku`, `version` 값을 기록합니다.

제안의 이미지 세부 정보를 사용하여 머신 세트 YAML 파일의 `providerSpec` 섹션에 다음 매개변수를 추가합니다.

```yaml
providerSpec:
  value:
    image:
      offer: rh-ocp-worker
      publisher: redhat
      resourceID: ""
      sku: rh-ocp-worker
      type: MarketplaceWithPlan
      version: 413.92.2023101700
```

#### 2.2.5. Azure 부팅 진단 활성화

머신 세트에서 생성하는 Azure 머신에서 부팅 진단을 활성화할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

스토리지 유형에 적용할 수 있는 `diagnostics` 구성을 머신 세트 YAML 파일의 `providerSpec` 필드에 추가합니다.

```yaml
providerSpec:
  diagnostics:
    boot:
      storageAccountType: AzureManaged
```

1. Azure 관리 스토리지 계정을 지정합니다.

```yaml
providerSpec:
  diagnostics:
    boot:
      storageAccountType: CustomerManaged
      customerManaged:
        storageAccountURI: https://<storage-account>.blob.core.windows.net
```

1. Azure Unmanaged 스토리지 계정을 지정합니다.

2. `<storage-account>` 를 스토리지 계정 이름으로 바꿉니다.

참고

Azure Blob Storage 데이터 서비스만 지원됩니다.

검증

Microsoft Azure 포털에서 머신 세트에서 배포한 머신의 부팅 진단 페이지를 검토하고 시스템의 직렬 로그를 볼 수 있는지 확인합니다.

#### 2.2.6. 머신을 Spot 가상머신으로 배포하는 머신 세트

Azure에서 실행되는 컴퓨팅 머신 세트를 생성하여 머신을 보장되지 않는 Spot 가상 머신으로 배포하면 비용을 절감할 수 있습니다. Spot 가상 머신은 사용되지 않은 Azure 용량을 사용하며 표준 가상 머신보다 비용이 저렴합니다. 일괄 처리 또는 상태 비저장, 수평적으로 확장 가능한 워크로드와 같이 인터럽트를 허용할 수 있는 워크로드에 Spot 가상 머신을 사용할 수 있습니다.

Azure는 언제든지 Spot 가상 머신을 종료 할 수 있습니다. Azure는 중단이 발생하면 사용자에게 30 초 동안 경고 메세지를 보냅니다. OpenShift Container Platform은 Azure가 종료 경고를 발행할 때 영향을 받는 인스턴스에서 워크로드를 제거하기 시작합니다.

다음과 같은 이유로 Spot 가상 머신을 사용할 때 중단될 수 있습니다.

인스턴스 가격이 최대 가격을 초과합니다.

Spot 가상 머신의 공급이 감소합니다.

Azure는 용량을 복원해야합니다.

Azure가 인스턴스를 종료하면 Spot 가상 머신 노드에서 실행되는 종료 프로세스가 머신 리소스를 삭제합니다. 컴퓨팅 머신 세트 `replicas` 수량을 충족하기 위해 컴퓨팅 머신 세트는 Spot 가상 머신을 요청하는 머신을 생성합니다.

#### 2.2.6.1. 컴퓨팅 머신 세트를 사용하여 Spot 가상 머신 생성

컴퓨팅 머신 세트 YAML 파일에 `spotVMOptions` 를 추가하여 Azure에서 Spot 가상 머신을 시작할 수 있습니다.

프로세스

`providerSpec` 필드 아래에 다음 행을 추가합니다.

```yaml
providerSpec:
  value:
    spotVMOptions: {}
```

필요한 경우 `spotVMOptions.maxPrice` 필드를 설정하여 Spot 가상 머신의 비용을 제한할 수 있습니다. 예를 들어 `maxPrice: '0.98765'` 를 설정할 수 있습니다. `maxPrice` 가 설정된 경우 이 값은 시간당 최대 Spot 가격으로 사용됩니다. 설정되지 않은 경우 최대 가격은 기본적으로 `-1` 로 설정된 표준 가상 머신 가격까지 청구됩니다.

Azure는 Spot 가상 머신 가격을 표준 가격으로 제한합니다. 인스턴스가 기본 `maxPrice` 로 설정된 경우 Azure는 가격 설정에 따라 인스턴스를 제거하지 않습니다. 그러나 용량 제한으로 인해 인스턴스를 제거할 수 있습니다.

참고

기본 표준 가상 머신 가격을 `maxPrice` 값으로 사용하고 Spot 가상 머신의 최대 가격을 설정하지 않는 것이 좋습니다.

#### 2.2.7. 임시 OS 디스크에 머신을 배포하는 머신 세트

Azure에서 실행되는 컴퓨팅 머신 세트를 생성하여 임시 OS 디스크에 머신을 배포할 수 있습니다. 임시 OS 디스크는 원격 Azure Storage가 아닌 로컬 VM 용량을 사용합니다. 따라서 이 구성에서는 추가 비용이 발생하지 않으며 읽기, 쓰기, 다시 시작에 더 짧은 대기 시간을 제공합니다.

추가 리소스

자세한 내용은 Azure VM용 임시 OS 디스크에 대한 Microsoft Azure 설명서를 참조하십시오.

#### 2.2.7.1. 컴퓨팅 머신 세트를 사용하여 임시 OS 디스크에 머신 생성

컴퓨팅 머신 세트 YAML 파일을 편집하여 Azure의 임시 OS 디스크에서 머신을 시작할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

다음 명령을 실행하여 CR(사용자 정의 리소스)을 편집합니다.

```shell-session
$ oc edit machineset <machine-set-name>
```

여기서 `<machine-set-name` >은 임시 OS 디스크에 머신을 프로비저닝하려는 컴퓨팅 머신 세트입니다.

`providerSpec` 필드에 다음을 추가합니다.

```yaml
providerSpec:
  value:
    ...
    osDisk:
       ...
       diskSettings:
         ephemeralStorageLocation: Local
       cachingType: ReadOnly
       managedDisk:
         storageAccountType: Standard_LRS
       ...
```

1. 2

3. 이러한 줄은 임시 OS 디스크를 사용할 수 있습니다.

4. 임시 OS 디스크는 표준 LRS 스토리지 계정 유형을 사용하는 VM 또는 스케일 세트 인스턴스에 대해서만 지원됩니다.

중요

OpenShift Container Platform에서 임시 OS 디스크 지원 구현에서는 `CacheDisk` 배치 유형만 지원합니다. `placement` 구성 설정은 변경하지 마십시오.

업데이트된 구성을 사용하여 컴퓨팅 머신 세트를 생성합니다.

```shell-session
$ oc create -f <machine-set-config>.yaml
```

검증

Microsoft Azure 포털에서 컴퓨팅 머신 세트에서 배포한 머신의 개요 페이지를 검토하고 `Ephemeral OS disk` 필드가 `OS cache placement` 로 설정되어 있는지 확인합니다.

#### 2.2.8. 울트라 디스크가 있는 머신을 데이터 디스크로 배포하는 머신 세트

Azure에서 실행되는 머신 세트를 생성하여 울트라 디스크가 있는 머신을 배포할 수 있습니다. Ultra 디스크는 가장 까다로운 데이터 워크로드에 사용하기 위한 고성능 스토리지입니다.

Azure Ultra 디스크가 지원하는 스토리지 클래스에 동적으로 바인딩하고 Pod에 마운트하는 PVC(영구 볼륨 클레임)를 생성할 수도 있습니다.

참고

데이터 디스크는 디스크 처리량 또는 디스크 IOPS를 지정하는 기능을 지원하지 않습니다. PVC를 사용하여 이러한 속성을 구성할 수 있습니다.

추가 리소스

Microsoft Azure Ultra 디스크 문서

CSI PVC를 사용하여 울트라 디스크에 머신을 배포하는 머신 세트

트리 내 PVC를 사용하여 울트라 디스크에 머신을 배포하는 머신 세트

#### 2.2.8.1. 머신 세트를 사용하여 울트라 디스크가 있는 머신 생성

머신 세트 YAML 파일을 편집하여 Azure에 울트라 디스크가 있는 머신을 배포할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

다음 명령을 실행하여 `worker` 데이터 시크릿을 사용하여 `openshift-machine-api` 네임스페이스에 사용자 정의 시크릿을 생성합니다.

```shell-session
$ oc -n openshift-machine-api \
get secret <role>-user-data \
--template='{{index .data.userData | base64decode}}' | jq > userData.txt
```

1. `<role>` 을 `worker` 로 바꿉니다.

2. `userData.txt` 를 새 사용자 지정 시크릿의 이름으로 지정합니다.

텍스트 편집기에서 `userData.txt` 파일을 열고 파일에서 최종 `}` 문자를 찾습니다.

바로 앞의 줄에서 `,` 을 추가합니다.

뒤에 새 행을 생성하고 `,` 다음에 구성 세부 정보를 추가합니다.

```plaintext
"storage": {
  "disks": [
    {
      "device": "/dev/disk/azure/scsi1/lun0",
      "partitions": [
        {
          "label": "lun0p1",
          "sizeMiB": 1024,
          "startMiB": 0
        }
      ]
    }
  ],
  "filesystems": [
    {
      "device": "/dev/disk/by-partlabel/lun0p1",
      "format": "xfs",
      "path": "/var/lib/lun0p1"
    }
  ]
},
"systemd": {
  "units": [
    {
      "contents": "[Unit]\nBefore=local-fs.target\n[Mount]\nWhere=/var/lib/lun0p1\nWhat=/dev/disk/by-partlabel/lun0p1\nOptions=defaults,pquota\n[Install]\nWantedBy=local-fs.target\n",
      "enabled": true,
      "name": "var-lib-lun0p1.mount"
    }
  ]
}
```

1. 울트라 디스크로 노드에 연결하려는 디스크의 구성 세부 정보입니다.

2. 사용 중인 머신 세트의 `dataDisks` 스탠자에 정의된 `lun` 값을 지정합니다. 예를 들어 시스템 세트에 `lun: 0` 이 포함된 경우 `lun0` 을 지정합니다. 이 구성 파일에서 여러 `"disks"` 항목을 지정하여 여러 데이터 디스크를 초기화할 수 있습니다. 여러 개의 `"disks"` 항목을 지정하는 경우 각 항목의 `lun` 값이 머신 세트의 값과 일치하는지 확인합니다.

3. 디스크의 새 파티션의 구성 세부 정보입니다.

4. 파티션의 레이블을 지정합니다. `lun0` 의 첫 번째 파티션에 `lun0` 과 같은 계층적 이름을 사용하는 것이 유용할 수 있습니다.

5. 파티션의 총 크기(MiB)를 지정합니다.

6. 파티션을 포맷할 때 사용할 파일 시스템을 지정합니다. 파티션 레이블을 사용하여 파티션을 지정합니다.

7. 부팅 시 파티션을 마운트할 `systemd` 장치를 지정합니다. 파티션 레이블을 사용하여 파티션을 지정합니다. 이 구성 파일에서 여러 개의 `"partitions"` 항목을 지정하여 여러 파티션을 만들 수 있습니다. 여러 개의 `"partitions"` 항목을 지정하는 경우 각각에 대해 `systemd` 장치를 지정해야 합니다.

8. `Where` 는 `storage.filesystems.path` 의 값을 지정합니다. `What` 에 대해 `storage.filesystems.device` 값을 지정합니다.

다음 명령을 실행하여 template 값을 `disableTemplating.txt` 라는 파일에 추출합니다.

```shell-session
$ oc -n openshift-machine-api get secret <role>-user-data \
--template='{{index .data.disableTemplating | base64decode}}' | jq > disableTemplating.txt
```

1. `<role>` 을 `worker` 로 바꿉니다.

`userData.txt` 파일과 `disableTemplating.txt` 파일을 결합하여 다음 명령을 실행하여 데이터 시크릿 파일을 생성합니다.

```shell-session
$ oc -n openshift-machine-api create secret generic <role>-user-data-x5 \
--from-file=userData=userData.txt \
--from-file=disableTemplating=disableTemplating.txt
```

1. `<role>-user-data-x5` 의 경우 시크릿 이름을 지정합니다. `<role>` 을 `worker` 로 바꿉니다.

기존 Azure `MachineSet` CR(사용자 정의 리소스)을 복사하고 다음 명령을 실행하여 편집합니다.

```shell-session
$ oc edit machineset <machine_set_name>
```

여기서 `<machine_set_name` >은 울트라 디스크가 있는 머신을 프로비저닝하려는 머신 세트입니다.

표시된 위치에 다음 행을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
spec:
  template:
    spec:
      metadata:
        labels:
          disk: ultrassd
      providerSpec:
        value:
          ultraSSDCapability: Enabled
          dataDisks:
          - nameSuffix: ultrassd
            lun: 0
            diskSizeGB: 4
            deletionPolicy: Delete
            cachingType: None
            managedDisk:
              storageAccountType: UltraSSD_LRS
          userDataSecret:
            name: <role>-user-data-x5
```

1. 이 머신 세트에서 생성한 노드를 선택하는 데 사용할 라벨을 지정합니다. 이 절차에서는 이 값에 `disk.ultrassd` 를 사용합니다.

2. 3

이 라인은 울트라 디스크를 사용할 수 있습니다. `dataDisks` 의 경우 전체 스탠자를 포함합니다.

4. 이전에 생성한 사용자 데이터 시크릿을 지정합니다. `<role>` 을 `worker` 로 바꿉니다.

다음 명령을 실행하여 업데이트된 구성을 사용하여 머신 세트를 생성합니다.

```shell-session
$ oc create -f <machine_set_name>.yaml
```

검증

다음 명령을 실행하여 머신이 생성되었는지 확인합니다.

```shell-session
$ oc get machines
```

시스템은 `Running` 상태여야 합니다.

실행 중이고 노드가 연결된 시스템의 경우 다음 명령을 실행하여 파티션을 검증합니다.

```shell-session
$ oc debug node/<node_name> -- chroot /host lsblk
```

이 명령에서 >은 노드 < `node_name` >에서 디버깅 쉘을 시작하고 `--` --로 명령을 전달합니다. 전달된 명령 는 기본 호스트 OS 바이너리에 대한 액세스를 제공하며 `lsblk` 에는 호스트 OS 시스템에 연결된 블록 장치가 표시됩니다.

```shell
oc debug node/<node_name
```

```shell
chroot /host
```

다음 단계

Pod 내에서 울트라 디스크를 사용하려면 마운트 지점을 사용하는 워크로드를 생성합니다. 다음 예와 유사한 YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssd-benchmark1
spec:
  containers:
  - name: ssd-benchmark1
    image: nginx
    ports:
      - containerPort: 80
        name: "http-server"
    volumeMounts:
    - name: lun0p1
      mountPath: "/tmp"
  volumes:
    - name: lun0p1
      hostPath:
        path: /var/lib/lun0p1
        type: DirectoryOrCreate
  nodeSelector:
    disktype: ultrassd
```

#### 2.2.8.2. 울트라 디스크를 활성화하는 머신 세트의 리소스 문제 해결

이 섹션의 정보를 사용하여 발생할 수 있는 문제를 이해하고 복구하십시오.

#### 2.2.8.2.1. 잘못된 울트라 디스크 구성

`UltraSSDCapability` 매개변수의 잘못된 구성이 머신 세트에 지정되면 머신 프로비저닝에 실패합니다.

예를 들어 `UltraSSDCapability` 매개변수가 `Disabled` 로 설정되어 있지만 `dataDisks` 매개변수에 울트라 디스크가 지정되면 다음과 같은 오류 메시지가 표시됩니다.

```shell-session
StorageAccountType UltraSSD_LRS can be used only when additionalCapabilities.ultraSSDEnabled is set.
```

이 문제를 해결하려면 머신 세트 구성이 올바른지 확인합니다.

#### 2.2.8.2.2. 지원되지 않는 디스크 매개변수

울트라 디스크와 호환되지 않는 리전, 가용성 영역 또는 인스턴스 크기가 머신 세트에 지정되면 시스템 프로비저닝이 실패합니다. 로그에 다음 오류 메시지가 있는지 확인합니다.

```shell-session
failed to create vm <machine_name>: failure sending request for machine <machine_name>: cannot create vm: compute.VirtualMachinesClient#CreateOrUpdate: Failure sending request: StatusCode=400 -- Original Error: Code="BadRequest" Message="Storage Account type 'UltraSSD_LRS' is not supported <more_information_about_why>."
```

이 문제를 해결하려면 지원되는 환경에서 이 기능을 사용하고 있으며 머신 세트 구성이 올바른지 확인합니다.

#### 2.2.8.2.3. 디스크를 삭제할 수 없음

데이터 디스크가 예상대로 작동하지 않으므로 울트라 디스크를 삭제하면 머신이 삭제되고 데이터 디스크가 분리됩니다. 필요한 경우 고립된 디스크를 수동으로 삭제해야 합니다.

#### 2.2.9. 머신 세트의 고객 관리 암호화 키 활성화

Azure에 암호화 키를 제공하여 관리 대상 디스크의 데이터를 암호화할 수 있습니다. 시스템 API를 사용하여 고객 관리 키로 서버 측 암호화를 활성화할 수 있습니다.

고객 관리 키를 사용하려면 Azure Key Vault, 디스크 암호화 세트 및 암호화 키가 필요합니다. 디스크 암호화 세트는 CCO(Cloud Credential Operator)에 권한이 부여된 리소스 그룹에 있어야 합니다. 그렇지 않은 경우 디스크 암호화 세트에 추가 reader 역할을 부여해야 합니다.

사전 요구 사항

Azure Key Vault 인스턴스를 만듭니다.

디스크 암호화 세트의 인스턴스를 만듭니다.

key vault에 디스크 암호화 세트 액세스 권한을 부여합니다.

프로세스

머신 세트 YAML 파일의 `providerSpec` 필드에 설정된 디스크 암호화를 구성합니다. 예를 들면 다음과 같습니다.

```yaml
providerSpec:
  value:
    osDisk:
      diskSizeGB: 128
      managedDisk:
        diskEncryptionSet:
          id: /subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/providers/Microsoft.Compute/diskEncryptionSets/<disk_encryption_set_name>
        storageAccountType: Premium_LRS
```

추가 리소스

고객 관리 키에 대한 Azure 문서

#### 2.2.10. 머신 세트를 사용하여 Azure 가상 머신에 대한 신뢰할 수 있는 시작 구성

OpenShift Container Platform 4.20은 Azure VM(가상 머신)에 대한 신뢰할 수 있는 시작을 지원합니다. 머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 신뢰할 수 있는 시작 옵션을 구성할 수 있습니다. 예를 들어 Secure Boot 또는 전용 가상 신뢰할 수 있는 플랫폼 모듈(vTPM) 인스턴스와 같은 UEFI 보안 기능을 사용하도록 이러한 머신을 구성할 수 있습니다.

참고

일부 기능 조합은 잘못된 구성을 생성합니다.

| Secure Boot [1] | vTPM [2] | 유효한 구성 |
| --- | --- | --- |
| 활성화됨 | 활성화됨 | 제공됨 |
| 활성화됨 | 비활성화됨 | 제공됨 |
| 활성화됨 | 생략됨 | 제공됨 |
| 비활성화됨 | 활성화됨 | 제공됨 |
| 생략됨 | 활성화됨 | 제공됨 |
| 비활성화됨 | 비활성화됨 | 없음 |
| 생략됨 | 비활성화됨 | 없음 |
| 생략됨 | 생략됨 | 없음 |

`secureBoot` 필드 사용.

`virtualizedTrustedPlatformModule` 필드 사용

관련 기능 및 기능에 대한 자세한 내용은 Azure 가상 머신의 신뢰할 수 있는 시작에 대한 Microsoft Azure 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집하여 유효한 구성을 제공합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    machines_v1beta1_machine_openshift_io:
      spec:
        providerSpec:
          value:
            securityProfile:
              settings:
                securityType: TrustedLaunch
                trustedLaunch:
                  uefiSettings:
                    secureBoot: Enabled
                    virtualizedTrustedPlatformModule: Enabled
# ...
```

1. Azure 가상 머신에 대한 신뢰할 수 있는 시작 기능을 활성화합니다. 이 값은 모든 유효한 구성에 필요합니다.

2. 사용할 UEFI 보안 기능을 지정합니다. 이 섹션은 모든 유효한 구성에 필요합니다.

3. UEFI Secure Boot를 활성화합니다.

4. vTPM 사용을 활성화합니다.

검증

Azure 포털에서 머신 세트에서 배포한 머신의 세부 정보를 검토하고 신뢰할 수 있는 시작 옵션이 구성한 값과 일치하는지 확인합니다.

#### 2.2.11. 머신 세트를 사용하여 Azure 기밀 가상 머신 구성

OpenShift Container Platform 4.20은 Azure 기밀 가상 머신(VM)을 지원합니다.

참고

현재 기밀 VM은 64비트 ARM 아키텍처에서 지원되지 않습니다.

머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 기밀 VM 옵션을 구성할 수 있습니다. 예를 들어 Secure Boot 또는 전용 가상 신뢰할 수 있는 플랫폼 모듈(vTPM) 인스턴스와 같은 UEFI 보안 기능을 사용하도록 이러한 머신을 구성할 수 있습니다.

관련 기능 및 기능에 대한 자세한 내용은 기밀 가상 머신에 대한 Microsoft Azure 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          osDisk:
            # ...
            managedDisk:
              securityProfile:
                securityEncryptionType: VMGuestStateOnly
            # ...
          securityProfile:
            settings:
                securityType: ConfidentialVM
                confidentialVM:
                  uefiSettings:
                    secureBoot: Disabled
                    virtualizedTrustedPlatformModule: Enabled
          vmSize: Standard_DC16ads_v5
# ...
```

1. 기밀 VM을 사용할 때 관리 디스크에 대한 보안 프로필 설정을 지정합니다.

2. VMGS(VM 게스트 상태) Blob의 암호화를 활성화합니다. 이 설정을 사용하려면 vTPM을 사용해야 합니다.

3. 기밀 VM의 보안 프로필 설정을 지정합니다.

4. 기밀 VM을 사용할 수 있습니다. 이 값은 모든 유효한 구성에 필요합니다.

5. 사용할 UEFI 보안 기능을 지정합니다. 이 섹션은 모든 유효한 구성에 필요합니다.

6. UEFI Secure Boot를 비활성화합니다.

7. vTPM 사용을 활성화합니다.

8. 기밀 VM을 지원하는 인스턴스 유형을 지정합니다.

검증

Azure 포털에서 머신 세트에서 배포한 머신의 세부 정보를 검토하고 기밀 VM 옵션이 구성한 값과 일치하는지 확인합니다.

#### 2.2.12. Microsoft Azure VM용 가속화 네트워킹

가속화 네트워킹은 단일 루트 I/O 가상화(SR-IOV)를 사용하여 Microsoft Azure VM에 더 직접적인 전환 경로를 제공합니다. 이렇게 하면 네트워크 성능이 향상됩니다. 이 기능은 설치 중 또는 설치 후 활성화할 수 있습니다.

#### 2.2.12.1. 제한

가속 네트워킹 사용 여부를 결정할 때 다음 제한 사항을 고려하십시오.

가속화 네트워킹은 Machine API가 작동하는 클러스터에서만 지원됩니다.

Azure 작업자 노드의 최소 요구 사항은 vCPU 2개이지만 가속 네트워킹에는 vCPU가 4개 이상 포함된 Azure VM 크기가 필요합니다. 이 요구 사항을 충족하기 위해 머신 세트의 `vmSize` 값을 변경할 수 있습니다. Azure VM 크기에 대한 자세한 내용은 Microsoft Azure 설명서를 참조하십시오.

기존 Azure 클러스터에서 이 기능을 활성화하면 새로 프로비저닝된 노드만 영향을 받습니다. 현재 실행 중인 노드가 조정되지 않습니다. 모든 노드에서 기능을 활성화하려면 기존 각 머신을 교체해야 합니다. 이 작업은 각 시스템에 대해 개별적으로 수행하거나 복제본을 0으로 축소한 다음 원하는 복제본 수로 다시 확장하여 수행할 수 있습니다.

#### 2.2.13. 머신 세트를 사용하여 용량 예약 구성

OpenShift Container Platform 버전 4.20 이상에서는 Microsoft Azure 클러스터에서 용량 예약 그룹을 사용하여 온디맨드 용량 예약을 지원합니다.

사용자가 정의한 용량 요청의 매개변수와 일치하는 사용 가능한 리소스에 머신을 배포하도록 머신 세트를 구성할 수 있습니다. 이러한 매개변수는 VM 크기, 리전 및 예약할 인스턴스 수를 지정합니다. Azure 서브스크립션 할당량이 용량 요청을 수용할 수 있는 경우 배포에 성공합니다.

이 Azure 오퍼링 에 대한 제한 사항 및 제안된 사용 사례를 비롯한 자세한 내용은 Microsoft Azure 설명서의 요청 용량 예약을 참조하십시오.

참고

머신 세트의 기존 용량 예약 구성은 변경할 수 없습니다. 다른 용량 예약 그룹을 사용하려면 머신 세트와 이전 머신 세트가 배포된 머신을 교체해야 합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

용량 예약 그룹을 생성했습니다. 자세한 내용은 Microsoft Azure 설명서에서 용량 예약 만들기 를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          capacityReservationGroupID: <capacity_reservation_group>
# ...
```

1. 시스템이 머신을 배포하도록 설정할 용량 예약 그룹의 ID를 지정합니다.

검증

시스템 배포를 확인하려면 다음 명령을 실행하여 머신 세트에서 생성한 머신을 나열합니다.

```shell-session
$ oc get machines.machine.openshift.io \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machineset=<machine_set_name>
```

여기서 `<machine_set_name>` 은 컴퓨팅 머신 세트의 이름입니다.

출력에서 나열된 시스템의 특성이 용량 예약의 매개변수와 일치하는지 확인합니다.

#### 2.2.14. 기존 OpenShift Container Platform 클러스터에 GPU 노드 추가

기본 컴퓨팅 머신 세트 구성을 복사하고 수정하여 Azure 클라우드 공급자에 대한 GPU 사용 머신 세트 및 머신을 생성할 수 있습니다.

다음 표에는 검증된 인스턴스 유형이 나열되어 있습니다.

| vmSize | NVIDIA GPU 액셀러레이터 | 최대 GPU 수 | 아키텍처 |
| --- | --- | --- | --- |
| `Standard_NC24s_v3` | V100 | 4 | x86 |
| `Standard_NC4as_T4_v3` | T4 | 1 | x86 |
| `ND A100 v4` | A100 | 8 | x86 |

참고

기본적으로 Azure 서브스크립션에는 GPU를 사용하는 Azure 인스턴스 유형에 대한 할당량이 없습니다. 고객은 위에 나열된 Azure 인스턴스 제품군에 대한 할당량 증가를 요청해야 합니다.

프로세스

다음 명령을 실행하여 `openshift-machine-api` 네임스페이스에 있는 머신 및 머신 세트를 확인합니다. 각 컴퓨팅 머신 세트는 Azure 리전 내의 다른 가용성 영역과 연결되어 있습니다. 설치 프로그램은 가용성 영역에서 컴퓨팅 시스템을 자동으로 로드 밸런싱합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                              DESIRED   CURRENT   READY   AVAILABLE   AGE
myclustername-worker-centralus1   1         1         1       1           6h9m
myclustername-worker-centralus2   1         1         1       1           6h9m
myclustername-worker-centralus3   1         1         1       1           6h9m
```

다음 명령을 실행하여 기존 컴퓨팅 `MachineSet` 정의 중 하나의 사본을 만들고 결과를 YAML 파일로 출력합니다. GPU 지원 컴퓨팅 머신 세트 정의의 기반이 됩니다.

```shell-session
$ oc get machineset -n openshift-machine-api myclustername-worker-centralus1 -o yaml > machineset-azure.yaml
```

머신 세트 콘텐츠를 확인합니다.

```shell-session
$ cat machineset-azure.yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  annotations:
    machine.openshift.io/GPU: "0"
    machine.openshift.io/memoryMb: "16384"
    machine.openshift.io/vCPU: "4"
  creationTimestamp: "2023-02-06T14:08:19Z"
  generation: 1
  labels:
    machine.openshift.io/cluster-api-cluster: myclustername
    machine.openshift.io/cluster-api-machine-role: worker
    machine.openshift.io/cluster-api-machine-type: worker
  name: myclustername-worker-centralus1
  namespace: openshift-machine-api
  resourceVersion: "23601"
  uid: acd56e0c-7612-473a-ae37-8704f34b80de
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: myclustername
      machine.openshift.io/cluster-api-machineset: myclustername-worker-centralus1
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: myclustername
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: myclustername-worker-centralus1
    spec:
      lifecycleHooks: {}
      metadata: {}
      providerSpec:
        value:
          acceleratedNetworking: true
          apiVersion: machine.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          diagnostics: {}
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/myclustername-rg/providers/Microsoft.Compute/galleries/gallery_myclustername_n6n4r/images/myclustername-gen2/versions/latest
            sku: ""
            version: ""
          kind: AzureMachineProviderSpec
          location: centralus
          managedIdentity: myclustername-identity
          metadata:
            creationTimestamp: null
          networkResourceGroup: myclustername-rg
          osDisk:
            diskSettings: {}
            diskSizeGB: 128
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: myclustername
          resourceGroup: myclustername-rg
          spotVMOptions: {}
          subnet: myclustername-worker-subnet
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_D4s_v3
          vnet: myclustername-vnet
          zone: "1"
status:
  availableReplicas: 1
  fullyLabeledReplicas: 1
  observedGeneration: 1
  readyReplicas: 1
  replicas: 1
```

다음 명령을 실행하여 `machineset-azure.yaml` 파일의 사본을 만듭니다.

```shell-session
$ cp machineset-azure.yaml machineset-azure-gpu.yaml
```

`machineset-azure-gpu.yaml` 에서 다음 필드를 업데이트합니다.

`.metadata.name` 을 `gpu` 가 포함된 이름으로 변경합니다.

새.metadata.name과 일치하도록 `.spec.selector.matchLabels["machine.openshift.io/cluster-api-machineset"]` 을 변경합니다.

새 `.metadata.name` 과 일치하도록 `.spec.template.metadata.labels["machine.openshift.io/cluster-api-machineset"]` 을 변경합니다.

Change `.spec.template.spec.providerSpec.value.vmSize` to `Standard_NC4as_T4_v3`.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  annotations:
    machine.openshift.io/GPU: "1"
    machine.openshift.io/memoryMb: "28672"
    machine.openshift.io/vCPU: "4"
  creationTimestamp: "2023-02-06T20:27:12Z"
  generation: 1
  labels:
    machine.openshift.io/cluster-api-cluster: myclustername
    machine.openshift.io/cluster-api-machine-role: worker
    machine.openshift.io/cluster-api-machine-type: worker
  name: myclustername-nc4ast4-gpu-worker-centralus1
  namespace: openshift-machine-api
  resourceVersion: "166285"
  uid: 4eedce7f-6a57-4abe-b529-031140f02ffa
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: myclustername
      machine.openshift.io/cluster-api-machineset: myclustername-nc4ast4-gpu-worker-centralus1
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: myclustername
        machine.openshift.io/cluster-api-machine-role: worker
        machine.openshift.io/cluster-api-machine-type: worker
        machine.openshift.io/cluster-api-machineset: myclustername-nc4ast4-gpu-worker-centralus1
    spec:
      lifecycleHooks: {}
      metadata: {}
      providerSpec:
        value:
          acceleratedNetworking: true
          apiVersion: machine.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          diagnostics: {}
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/myclustername-rg/providers/Microsoft.Compute/galleries/gallery_myclustername_n6n4r/images/myclustername-gen2/versions/latest
            sku: ""
            version: ""
          kind: AzureMachineProviderSpec
          location: centralus
          managedIdentity: myclustername-identity
          metadata:
            creationTimestamp: null
          networkResourceGroup: myclustername-rg
          osDisk:
            diskSettings: {}
            diskSizeGB: 128
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: myclustername
          resourceGroup: myclustername-rg
          spotVMOptions: {}
          subnet: myclustername-worker-subnet
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_NC4as_T4_v3
          vnet: myclustername-vnet
          zone: "1"
status:
  availableReplicas: 1
  fullyLabeledReplicas: 1
  observedGeneration: 1
  readyReplicas: 1
  replicas: 1
```

변경 사항을 확인하려면 다음 명령을 실행하여 원래 컴퓨팅 정의와 새 GPU 사용 노드 정의의 `diff` 를 수행합니다.

```shell-session
$ diff machineset-azure.yaml machineset-azure-gpu.yaml
```

```shell-session
14c14
<   name: myclustername-worker-centralus1
---
>   name: myclustername-nc4ast4-gpu-worker-centralus1
23c23
<       machine.openshift.io/cluster-api-machineset: myclustername-worker-centralus1
---
>       machine.openshift.io/cluster-api-machineset: myclustername-nc4ast4-gpu-worker-centralus1
30c30
<         machine.openshift.io/cluster-api-machineset: myclustername-worker-centralus1
---
>         machine.openshift.io/cluster-api-machineset: myclustername-nc4ast4-gpu-worker-centralus1
67c67
<           vmSize: Standard_D4s_v3
---
>           vmSize: Standard_NC4as_T4_v3
```

다음 명령을 실행하여 정의 파일에서 GPU 지원 컴퓨팅 머신 세트를 생성합니다.

```shell-session
$ oc create -f machineset-azure-gpu.yaml
```

```shell-session
machineset.machine.openshift.io/myclustername-nc4ast4-gpu-worker-centralus1 created
```

다음 명령을 실행하여 `openshift-machine-api` 네임스페이스에 있는 머신 및 머신 세트를 확인합니다. 각 컴퓨팅 머신 세트는 Azure 리전 내의 다른 가용성 영역과 연결되어 있습니다. 설치 프로그램은 가용성 영역에서 컴퓨팅 시스템을 자동으로 로드 밸런싱합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                               DESIRED   CURRENT   READY   AVAILABLE   AGE
clustername-n6n4r-nc4ast4-gpu-worker-centralus1    1         1         1       1           122m
clustername-n6n4r-worker-centralus1                1         1         1       1           8h
clustername-n6n4r-worker-centralus2                1         1         1       1           8h
clustername-n6n4r-worker-centralus3                1         1         1       1           8h
```

다음 명령을 실행하여 `openshift-machine-api` 네임스페이스에 있는 머신을 확인합니다. 집합당 하나의 컴퓨팅 시스템만 구성할 수 있지만 특정 리전 및 영역에 노드를 추가하도록 컴퓨팅 시스템 세트를 확장할 수 있습니다.

```shell-session
$ oc get machines -n openshift-machine-api
```

```shell-session
NAME                                                PHASE     TYPE                   REGION      ZONE   AGE
myclustername-master-0                              Running   Standard_D8s_v3        centralus   2      6h40m
myclustername-master-1                              Running   Standard_D8s_v3        centralus   1      6h40m
myclustername-master-2                              Running   Standard_D8s_v3        centralus   3      6h40m
myclustername-nc4ast4-gpu-worker-centralus1-w9bqn   Running      centralus   1      21m
myclustername-worker-centralus1-rbh6b               Running   Standard_D4s_v3        centralus   1      6h38m
myclustername-worker-centralus2-dbz7w               Running   Standard_D4s_v3        centralus   2      6h38m
myclustername-worker-centralus3-p9b8c               Running   Standard_D4s_v3        centralus   3      6h38m
```

다음 명령을 실행하여 기존 노드, 시스템 및 머신 세트를 확인합니다. 각 노드는 특정 Azure 리전 및 OpenShift Container Platform 역할을 사용하는 머신 정의 인스턴스입니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME                                                STATUS   ROLES                  AGE     VERSION
myclustername-master-0                              Ready    control-plane,master   6h39m   v1.33.4
myclustername-master-1                              Ready    control-plane,master   6h41m   v1.33.4
myclustername-master-2                              Ready    control-plane,master   6h39m   v1.33.4
myclustername-nc4ast4-gpu-worker-centralus1-w9bqn   Ready    worker                 14m     v1.33.4
myclustername-worker-centralus1-rbh6b               Ready    worker                 6h29m   v1.33.4
myclustername-worker-centralus2-dbz7w               Ready    worker                 6h29m   v1.33.4
myclustername-worker-centralus3-p9b8c               Ready    worker                 6h31m   v1.33.4
```

컴퓨팅 머신 세트 목록을 표시합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                   DESIRED   CURRENT   READY   AVAILABLE   AGE
myclustername-worker-centralus1        1         1         1       1           8h
myclustername-worker-centralus2        1         1         1       1           8h
myclustername-worker-centralus3        1         1         1       1           8h
```

다음 명령을 실행하여 정의 파일에서 GPU 지원 컴퓨팅 머신 세트를 생성합니다.

```shell-session
$ oc create -f machineset-azure-gpu.yaml
```

컴퓨팅 머신 세트 목록을 표시합니다.

```shell-session
oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                          DESIRED   CURRENT   READY   AVAILABLE   AGE
myclustername-nc4ast4-gpu-worker-centralus1   1         1         1       1           121m
myclustername-worker-centralus1               1         1         1       1           8h
myclustername-worker-centralus2               1         1         1       1           8h
myclustername-worker-centralus3               1         1         1       1           8h
```

검증

다음 명령을 실행하여 생성한 머신 세트를 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api | grep gpu
```

MachineSet 복제본 수는 `1` 로 설정되므로 새 `Machine` 개체가 자동으로 생성됩니다.

```shell-session
myclustername-nc4ast4-gpu-worker-centralus1   1         1         1       1           121m
```

다음 명령을 실행하여 머신 세트에서 생성한 `Machine` 오브젝트를 확인합니다.

```shell-session
$ oc -n openshift-machine-api get machines | grep gpu
```

```shell-session
myclustername-nc4ast4-gpu-worker-centralus1-w9bqn   Running   Standard_NC4as_T4_v3   centralus   1      21m
```

참고

노드에 네임스페이스를 지정할 필요가 없습니다. 노드 정의는 클러스터 범위입니다.

#### 2.2.15. Node Feature Discovery Operator 배포

GPU 지원 노드를 생성한 후 예약할 수 있도록 GPU 사용 노드를 검색해야 합니다. 이렇게 하려면 NFD(Node Feature Discovery) Operator를 설치합니다. NFD Operator는 노드에서 하드웨어 장치 기능을 식별합니다. 이는 인프라 노드에서 하드웨어 리소스를 식별하고 카탈로그하는 일반적인 문제를 해결하여 OpenShift Container Platform에서 사용할 수 있도록 합니다.

프로세스

OpenShift Container Platform 콘솔의 소프트웨어 카탈로그에서 Node Feature Discovery Operator를 설치합니다.

NFD Operator를 설치한 후 설치된 Operator 목록에서 Node Feature Discovery 를 선택하고 Create instance 를 선택합니다. 이렇게 하면 각 컴퓨팅 노드에 대해 `nfd-master` 및 `nfd-worker`, 하나의 `nfd-worker` Pod가 `openshift-nfd` 네임스페이스에 설치됩니다.

다음 명령을 실행하여 Operator가 설치되어 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n openshift-nfd
```

```shell-session
NAME                                       READY    STATUS     RESTARTS   AGE

nfd-controller-manager-8646fcbb65-x5qgk    2/2      Running 7  (8h ago)   1d
```

콘솔에 설치된 Oerator로 이동하여 Create Node Feature Discovery 를 선택합니다.

생성 을 선택하여 NFD 사용자 정의 리소스를 빌드합니다. 이렇게 하면 하드웨어 리소스에 대해 OpenShift Container Platform 노드를 폴링하고 카탈로그하는 `openshift-nfd` 네임스페이스에 NFD Pod가 생성됩니다.

검증

빌드에 성공하면 다음 명령을 실행하여 NFD Pod가 각 노드에서 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n openshift-nfd
```

```shell-session
NAME                                       READY   STATUS      RESTARTS        AGE
nfd-controller-manager-8646fcbb65-x5qgk    2/2     Running     7 (8h ago)      12d
nfd-master-769656c4cb-w9vrv                1/1     Running     0               12d
nfd-worker-qjxb2                           1/1     Running     3 (3d14h ago)   12d
nfd-worker-xtz9b                           1/1     Running     5 (3d14h ago)   12d
```

NFD Operator는 벤더 PCI ID를 사용하여 노드의 하드웨어를 식별합니다. NVIDIA는 PCI ID `10de` 를 사용합니다.

다음 명령을 실행하여 NFD Operator가 검색한 NVIDIA GPU를 확인합니다.

```shell-session
$ oc describe node ip-10-0-132-138.us-east-2.compute.internal | egrep 'Roles|pci'
```

```shell-session
Roles: worker

feature.node.kubernetes.io/pci-1013.present=true

feature.node.kubernetes.io/pci-10de.present=true

feature.node.kubernetes.io/pci-1d0f.present=true
```

`10de` 는 GPU 사용 노드의 노드 기능 목록에 나타납니다. 즉, NFD Operator가 GPU 지원 MachineSet에서 노드를 올바르게 식별했습니다.

추가 리소스

설치 중 가속 네트워킹 활성화

#### 2.2.15.1. 기존 Microsoft Azure 클러스터에서 가속 네트워킹 활성화

머신 세트 YAML 파일에 `acceleratedNetworking` 을 추가하여 Azure에서 가속 네트워킹을 활성화할 수 있습니다.

사전 요구 사항

Machine API가 작동하는 기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

`providerSpec` 필드에 다음을 추가합니다.

```yaml
providerSpec:
  value:
    acceleratedNetworking: true
    vmSize: <azure-vm-size>
```

1. 이 라인은 가속 네트워킹을 활성화합니다.

2. vCPU가 4개 이상인 Azure VM 크기를 지정합니다. VM 크기에 대한 자세한 내용은 Microsoft Azure 설명서 를 참조하십시오.

다음 단계

현재 실행 중인 노드에서 기능을 활성화하려면 기존 각 머신을 교체해야 합니다. 이 작업은 각 시스템에 대해 개별적으로 수행하거나 복제본을 0으로 축소한 다음 원하는 복제본 수로 다시 확장하여 수행할 수 있습니다.

검증

Microsoft Azure 포털에서 머신 세트에 의해 프로비저닝된 머신의 네트워킹 설정 페이지를 검토하고 `Accelerated networking` 필드가 `Enabled` 로 설정되어 있는지 확인합니다.

추가 리소스

컴퓨팅 머신 세트 수동 스케일링

### 2.3. Azure Stack Hub에서 컴퓨팅 머신 세트 생성

Microsoft Azure Stack Hub의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.3.1. Azure Stack Hub에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 리전의 `1` Microsoft Azure 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 만듭니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <role>
    machine.openshift.io/cluster-api-machine-type: <role>
  name: <infrastructure_id>-<role>-<region>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
    spec:
      metadata:
        creationTimestamp: null
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          availabilitySet: <availability_set>
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/<infrastructure_id>-rg/providers/Microsoft.Compute/images/<infrastructure_id>
            sku: ""
            version: ""
          internalLoadBalancer: ""
          kind: AzureMachineProviderSpec
          location: <region>
          managedIdentity: <infrastructure_id>-identity
          metadata:
            creationTimestamp: null
          natRule: null
          networkResourceGroup: ""
          osDisk:
            diskSizeGB: 128
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: ""
          resourceGroup: <infrastructure_id>-rg
          sshPrivateKey: ""
          sshPublicKey: ""
          subnet: <infrastructure_id>-<role>-subnet
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_DS4_v2
          vnet: <infrastructure_id>-vnet
          zone: "1"
```

1. 5

7. 13

15. 16

17. 20

클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

다음 명령을 실행하여 서브넷을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.subnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

다음 명령을 실행하여 vnet을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.vnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

2. 3

8. 9

11. 18

19. 추가할 노드 레이블을 지정합니다.

4. 6

10. 인프라 ID, 노드 레이블, 리전을 지정합니다.

14. 머신을 배치할 리전을 지정합니다.

21. 머신을 배치할 리전 내 영역을 지정합니다. 해당 리전이 지정한 영역을 지원하는지 확인합니다.

12. 클러스터의 가용성 세트를 지정합니다.

#### 2.3.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

Azure Stack Hub 컴퓨팅 시스템을 배포할 가용성 세트를 생성합니다.

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

< `availabilitySet` >, < `clusterID` >, < `role` > 매개변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.3.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

#### 2.3.4. Azure 부팅 진단 활성화

머신 세트에서 생성하는 Azure 머신에서 부팅 진단을 활성화할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure Stack Hub 클러스터가 있어야 합니다.

프로세스

스토리지 유형에 적용할 수 있는 `diagnostics` 구성을 머신 세트 YAML 파일의 `providerSpec` 필드에 추가합니다.

```yaml
providerSpec:
  diagnostics:
    boot:
      storageAccountType: AzureManaged
```

1. Azure 관리 스토리지 계정을 지정합니다.

```yaml
providerSpec:
  diagnostics:
    boot:
      storageAccountType: CustomerManaged
      customerManaged:
        storageAccountURI: https://<storage-account>.blob.core.windows.net
```

1. Azure Unmanaged 스토리지 계정을 지정합니다.

2. `<storage-account>` 를 스토리지 계정 이름으로 바꿉니다.

참고

Azure Blob Storage 데이터 서비스만 지원됩니다.

검증

Microsoft Azure 포털에서 머신 세트에서 배포한 머신의 부팅 진단 페이지를 검토하고 시스템의 직렬 로그를 볼 수 있는지 확인합니다.

#### 2.3.5. 머신 세트의 고객 관리 암호화 키 활성화

Azure에 암호화 키를 제공하여 관리 대상 디스크의 데이터를 암호화할 수 있습니다. 시스템 API를 사용하여 고객 관리 키로 서버 측 암호화를 활성화할 수 있습니다.

고객 관리 키를 사용하려면 Azure Key Vault, 디스크 암호화 세트 및 암호화 키가 필요합니다. 디스크 암호화 세트는 CCO(Cloud Credential Operator)에 권한이 부여된 리소스 그룹에 있어야 합니다. 그렇지 않은 경우 디스크 암호화 세트에 추가 reader 역할을 부여해야 합니다.

사전 요구 사항

Azure Key Vault 인스턴스를 만듭니다.

디스크 암호화 세트의 인스턴스를 만듭니다.

key vault에 디스크 암호화 세트 액세스 권한을 부여합니다.

프로세스

머신 세트 YAML 파일의 `providerSpec` 필드에 설정된 디스크 암호화를 구성합니다. 예를 들면 다음과 같습니다.

```yaml
providerSpec:
  value:
    osDisk:
      diskSizeGB: 128
      managedDisk:
        diskEncryptionSet:
          id: /subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/providers/Microsoft.Compute/diskEncryptionSets/<disk_encryption_set_name>
        storageAccountType: Premium_LRS
```

추가 리소스

고객 관리 키에 대한 Azure 문서

### 2.4. Google Cloud에서 컴퓨팅 머신 세트 생성

Google Cloud의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.4.1. Google Cloud에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 Google Cloud에서 실행되는 컴퓨팅 머신 세트를 정의하고 여기서 < `role` >은 추가할 노드 레이블입니다.

```shell
node-role.kubernetes.io/<role>: "" 로 레이블이 지정된 노드를 생성합니다.
```

#### 2.4.1.1. OpenShift CLI를 사용하여 얻은 값

다음 예제에서는 OpenShift CLI를 사용하여 클러스터의 일부 값을 가져올 수 있습니다.

인프라 ID

`<infrastructure_id>` 문자열은 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

이미지 경로

`<path_to_image>` 문자열은 디스크를 생성하는 데 사용된 이미지의 경로입니다. OpenShift CLI가 설치되어 있으면 다음 명령을 실행하여 이미지에 대한 경로를 얻을 수 있습니다.

```shell-session
$ oc -n openshift-machine-api \
  -o jsonpath='{.spec.template.spec.providerSpec.value.disks[0].image}{"\n"}' \
  get machineset/<infrastructure_id>-worker-a
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-w-a
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-w-a
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-w-a
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          canIPForward: false
          credentialsSecret:
            name: gcp-cloud-credentials
          deletionProtection: false
          disks:
          - autoDelete: true
            boot: true
            image: <path_to_image>
            labels: null
            sizeGb: 128
            type: pd-ssd
          gcpMetadata:
          - key: <custom_metadata_key>
            value: <custom_metadata_value>
          kind: GCPMachineProviderSpec
          machineType: n1-standard-4
          metadata:
            creationTimestamp: null
          networkInterfaces:
          - network: <infrastructure_id>-network
            subnetwork: <infrastructure_id>-worker-subnet
          projectID: <project_name>
          region: us-central1
          serviceAccounts:
          - email: <infrastructure_id>-w@<project_name>.iam.gserviceaccount.com
            scopes:
            - https://www.googleapis.com/auth/cloud-platform
          tags:
            - <infrastructure_id>-worker
          userDataSecret:
            name: worker-user-data
          zone: us-central1-a
```

1. `<infrastructure_id>` 의 경우 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다.

2. `<node>` 에 대해 추가할 노드 레이블을 지정합니다.

3. 현재 컴퓨팅 머신 세트에 사용되는 이미지의 경로를 지정합니다.

Google Cloud Marketplace 이미지를 사용하려면 다음을 사용할 제안을 지정합니다.

OpenShift Container Platform: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-ocp-413-x86-64-202305021736`

OpenShift Platform Plus: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-opp-413-x86-64-202305021736`

OpenShift Kubernetes Engine: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-oke-413-x86-64-202305021736`

4. 선택 사항: `key:value` 쌍 형식으로 사용자 지정 메타데이터를 지정합니다. 사용 사례의 예는 사용자 지정 메타데이터 설정에 대한 Google Cloud 설명서를 참조하십시오.

5. & `lt;project_name` > 의 경우 클러스터에 사용하는 Google Cloud 프로젝트의 이름을 지정합니다.

6. 단일 서비스 계정을 지정합니다. 여러 서비스 계정이 지원되지 않습니다.

#### 2.4.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.4.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

#### 2.4.4. 머신 세트를 사용하여 영구 디스크 유형 구성

머신 세트가 머신 세트 YAML 파일을 편집하여 머신을 배포하는 영구 디스크 유형을 구성할 수 있습니다.

영구 디스크 유형, 호환성, 지역 가용성 및 제한에 대한 자세한 내용은 영구 디스크에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
...
spec:
  template:
    spec:
      providerSpec:
        value:
          disks:
            type: <pd-disk-type>
```

1. 영구 디스크 유형을 지정합니다. 유효한 값은 `pd-ssd`, `pd-standard`, `pd-balanced` 입니다. 기본값은 `pd-standard` 입니다.

검증

Google Cloud 콘솔을 사용하여 머신 세트에서 배포한 시스템의 세부 정보를 검토하고 `Type` 필드가 구성된 디스크 유형과 일치하는지 확인합니다.

#### 2.4.5. 머신 세트를 사용하여 기밀성 VM 구성

머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 기밀성 VM 옵션을 구성할 수 있습니다.

Confidential VM 기능, 기능 및 호환성에 대한 자세한 내용은 Confidential VM 에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

참고

현재 기밀 VM은 64비트 ARM 아키텍처에서 지원되지 않습니다. 기밀성 VM을 사용하는 경우 지원되는 리전을 선택해야 합니다. 지원되는 리전 및 구성에 대한 자세한 내용은 지원되는 영역에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          confidentialCompute: Enabled
          onHostMaintenance: Terminate
          machineType: n2d-standard-8
# ...
```

1. 기밀성 VM이 활성화되었는지 여부를 지정합니다. 다음 값이 유효합니다.

`활성화됨`

기본 Confidential VM 기술을 선택하여 기밀성 VM을 활성화합니다. 기본 선택은 AMD Secure Encrypted Virtualization(AMD SEV)입니다.

중요

`Enabled` 값은 더 이상 사용되지 않는 AMD Secure Encrypted Virtualization(AMD SEV)을 사용한 기밀성 컴퓨팅을 선택합니다.

`비활성화됨`

기밀성 VM을 비활성화합니다.

`AMDEncryptedVirtualizationNestedPaging`

AMD Secure Encrypted Virtualization Secure Nested Paging(AMD SEV-SNP)을 사용하여 기밀 VM을 활성화합니다. AMD SEV-SNP는 n2d 머신을 지원합니다.

`AMDEncryptedVirtualization`

AMD SEV를 사용한 기밀성 VM 활성화. AMD SEV는 c2d, n2d 및 c3d 시스템을 지원합니다.

중요

AMD Secure Encrypted Virtualization(AMD SEV)에서 기밀 컴퓨팅을 사용하는 것은 더 이상 사용되지 않으며 향후 릴리스에서 제거됩니다.

`IntelTrustedDomainExtensions`

Intel TDX(Intel Trusted Domain Extensions)를 사용하여 기밀성 VM을 활성화합니다. Intel TDX는 n2d 머신을 지원합니다.

2. 호스트 유지 관리 이벤트 중 하드웨어 또는 소프트웨어 업데이트와 같은 VM의 동작을 지정합니다. 기밀성 VM을 사용하는 시스템의 경우 이 값은 VM을 중지하도록 `Terminate` 로 설정해야 합니다. 기밀 VM은 실시간 VM 마이그레이션을 지원하지 않습니다.

3. `confidentialCompute` 필드에 지정한 기밀성 VM 옵션을 지원하는 머신 유형을 지정합니다.

검증

Google Cloud 콘솔에서 시스템 세트에서 배포한 시스템의 세부 정보를 검토하고 기밀성 VM 옵션이 구성한 값과 일치하는지 확인합니다.

#### 2.4.6. 머신을 선점할 수 있는 가상 머신 인스턴스로 배포하는 머신 세트

머신을 보장되지 않는 선점 가능한 가상 머신 인스턴스로 배포하는 Google Cloud에서 실행되는 컴퓨팅 머신 세트를 생성하여 비용을 절감할 수 있습니다. 선점 가능한 가상 머신 인스턴스는 과도한 Compute Engine 용량을 사용하며 일반 인스턴스보다 비용이 저렴합니다. 일괄 처리 또는 상태 비저장, 수평적으로 확장 가능한 워크로드와 같이 인터럽트를 허용할 수있는 워크로드에 선점 가능한 가상 머신 인스턴스를 사용할 수 있습니다.

Google Cloud Compute Engine은 언제든지 선점 가능한 가상 머신 인스턴스를 종료할 수 있습니다. Compute Engine은 인터럽션이 30 초 후에 발생하는 것을 알리는 선점 알림을 사용자에게 보냅니다. OpenShift Container Platform은 Compute Engine이 선점 알림을 발행할 때 영향을 받는 인스턴스에서 워크로드를 제거하기 시작합니다. 인스턴스가 중지되지 않은 경우 ACPI G3 Mechanical Off 신호는 30 초 후에 운영 체제로 전송됩니다. 다음으로 선점 가능한 가상 머신 인스턴스가 Compute Engine에 의해 `TERMINATED` 상태로 전환됩니다.

다음과 같은 이유로 선점 가능한 가상 머신 인스턴스를 사용할 때 중단될 수 있습니다.

시스템 또는 유지 관리 이벤트가 있는 경우

선점 가능한 가상 머신 인스턴스의 공급이 감소하는 경우

인스턴스가 선점 가능한 가상 머신 인스턴스에 할당된 24 시간 후에 종료되는 경우

Google Cloud가 인스턴스를 종료하면 선점 가능한 가상 머신 인스턴스 노드에서 실행되는 종료 프로세스가 머신 리소스를 삭제합니다. 컴퓨팅 머신 세트 `replicas` 수량을 충족하기 위해 컴퓨팅 머신 세트는 선점 가능한 가상 머신 인스턴스를 요청하는 머신을 생성합니다.

#### 2.4.6.1. 컴퓨팅 머신 세트를 사용하여 선점 가능한 가상 머신 인스턴스 생성

컴퓨팅 머신 세트 YAML 파일에 `preemptible` 을 추가하여 Google Cloud에서 선점 가능한 가상 머신 인스턴스를 시작할 수 있습니다.

프로세스

`providerSpec` 필드 아래에 다음 행을 추가합니다.

```yaml
providerSpec:
  value:
    preemptible: true
```

`preemptible` 이 `true` 로 설정되면 인스턴스가 시작된 후 머신에 `interruptible-instance` 로 레이블이 지정됩니다.

#### 2.4.7. 머신 세트를 사용하여 Shielded VM 옵션 구성

머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 Shielded VM 옵션을 구성할 수 있습니다.

Shielded VM 기능 및 기능에 대한 자세한 내용은 Shielded VM 에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          shieldedInstanceConfig:
            integrityMonitoring: Enabled
            secureBoot: Disabled
            virtualizedTrustedPlatformModule: Enabled
# ...
```

1. 이 섹션에서는 원하는 모든 Shielded VM 옵션을 지정합니다.

2. 무결성 모니터링이 활성화되었는지 여부를 지정합니다. 유효한 값은 `Disabled` 또는 `Enabled` 입니다.

참고

무결성 모니터링이 활성화되면 신뢰할 수 있는 가상 플랫폼 모듈(vTPM)을 비활성화해서는 안 됩니다.

3. UEFI Secure Boot가 활성화되었는지 여부를 지정합니다. 유효한 값은 `Disabled` 또는 `Enabled` 입니다.

4. vTPM이 활성화되었는지 여부를 지정합니다. 유효한 값은 `Disabled` 또는 `Enabled` 입니다.

검증

Google Cloud 콘솔을 사용하여 머신 세트에서 배포한 머신의 세부 정보를 검토하고 Shielded VM 옵션이 구성한 값과 일치하는지 확인합니다.

추가 리소스

Shielded VM이란 무엇입니까?

Secure Boot

가상 신뢰할 수 있는 플랫폼 모듈(vTPM)

무결성 모니터링

#### 2.4.8. 머신 세트의 고객 관리 암호화 키 활성화

Google Cloud Compute Engine을 사용하면 암호화 키를 제공하여 디스크의 데이터를 암호화할 수 있습니다. 키는 고객의 데이터를 암호화하는 것이 아니라 데이터 암호화 키를 암호화하는 데 사용됩니다. 기본적으로 Compute Engine은 Compute Engine 키를 사용하여 이 데이터를 암호화합니다.

Machine API를 사용하는 클러스터에서 고객 관리 키로 암호화를 활성화할 수 있습니다. 먼저 KMS 키를 생성 하고 서비스 계정에 올바른 권한을 할당해야 합니다. 서비스 계정에서 키를 사용하려면 KMS 키 이름, 키 링 이름 및 위치가 필요합니다.

참고

KMS 암호화에 전용 서비스 계정을 사용하지 않는 경우 Compute Engine 기본 서비스 계정이 대신 사용됩니다. 전용 서비스 계정을 사용하지 않는 경우 키에 액세스할 수 있는 기본 서비스 계정 권한을 부여해야 합니다. Compute Engine 기본 서비스 계정 이름은 `service-<project_number>@compute-system.iam.gserviceaccount.com` 패턴을 기반으로 합니다.

프로세스

특정 서비스 계정이 KMS 키를 사용하도록 허용하고 서비스 계정에 올바른 IAM 역할을 부여하려면 KMS 키 이름, 키 링 이름 및 위치로 다음 명령을 실행합니다.

```shell-session
$ gcloud kms keys add-iam-policy-binding <key_name> \
  --keyring <key_ring_name> \
  --location <key_ring_location> \
  --member "serviceAccount:service-<project_number>@compute-system.iam.gserviceaccount.com” \
  --role roles/cloudkms.cryptoKeyEncrypterDecrypter
```

사용자가 머신 세트 YAML 파일의 `providerSpec` 필드에 암호화 키를 구성할 수 있습니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
...
spec:
  template:
    spec:
      providerSpec:
        value:
          disks:
          - type:
            encryptionKey:
              kmsKey:
                name: machine-encryption-key
                keyRing: openshift-encrpytion-ring
                location: global
                projectID: openshift-gcp-project
              kmsKeyServiceAccount: openshift-service-account@openshift-gcp-project.iam.gserviceaccount.com
```

1. 디스크 암호화에 사용되는 고객 관리 암호화 키의 이름입니다.

2. KMS 키가 속한 KMS 키 링의 이름입니다.

3. KMS 키 링이 있는 Google Cloud 위치입니다.

4. 선택 사항: KMS 키 링이 존재하는 프로젝트의 ID입니다. 프로젝트 ID가 설정되지 않은 경우 머신 세트가 사용된 머신 세트의 `projectID` 를 설정합니다.

5. 선택 사항: 지정된 KMS 키의 암호화 요청에 사용되는 서비스 계정입니다. 서비스 계정이 설정되지 않은 경우 Compute Engine 기본 서비스 계정이 사용됩니다.

업데이트된 `providerSpec` 오브젝트 구성을 사용하여 새 머신을 생성하면 디스크 암호화 키가 KMS 키로 암호화됩니다.

#### 2.4.9. 컴퓨팅 머신 세트에 대한 GPU 지원 활성화

Google Cloud Compute Engine을 사용하면 VM 인스턴스에 GPU를 추가할 수 있습니다. GPU 리소스에 액세스할 수 있는 워크로드는 이 기능이 활성화된 컴퓨팅 머신에서 더 효과적으로 수행할 수 있습니다. Google Cloud의 OpenShift Container Platform은 A2 및 N1 머신 시리즈의 NVIDIA GPU 모델을 지원합니다.

| 모델 이름 | GPU 유형 | 머신 유형 [1] |
| --- | --- | --- |
| NVIDIA A100 | `nvidia-tesla-a100` | `a2-highgpu-1g` `a2-highgpu-2g` `a2-highgpu-4g` `a2-highgpu-8g` `a2-megagpu-16g` |
| NVIDIA K80 | `nvidia-tesla-k80` | `n1-standard-1` `n1-standard-2` `n1-standard-4` `n1-standard-8` `n1-standard-16` `n1-standard-32` `n1-standard-64` `n1-standard-96` `n1-highmem-2` `n1-highmem-4` `n1-highmem-8` `n1-highmem-16` `n1-highmem-32` `n1-highmem-64` `n1-highmem-96` `n1-highcpu-2` `n1-highcpu-4` `n1-highcpu-8` `n1-highcpu-16` `n1-highcpu-32` `n1-highcpu-64` `n1-highcpu-96` |
| NVIDIA P100 | `nvidia-tesla-p100` |
| NVIDIA P4 | `nvidia-tesla-p4` |
| NVIDIA T4 | `nvidia-tesla-t4` |
| NVIDIA V100 | `nvidia-tesla-v100` |

사양, 호환성, 지역 가용성 및 제한을 포함한 머신 유형에 대한 자세한 내용은 N1 머신 시리즈,A2 머신 시리즈 및 GPU 리전 및 영역 가용성에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

Machine API를 사용하여 인스턴스에 사용할 지원되는 GPU를 정의할 수 있습니다.

지원되는 GPU 유형 중 하나로 배포하도록 N1 머신 시리즈에서 머신을 구성할 수 있습니다. A2 머신 시리즈의 시스템에는 연결된 GPU가 제공되며 게스트 가속기를 사용할 수 없습니다.

참고

그래픽 워크로드에 대한 GPU는 지원되지 않습니다.

프로세스

텍스트 편집기에서 기존 컴퓨팅 머신 세트의 YAML 파일을 열거나 새 파일을 생성합니다.

컴퓨팅 머신 세트 YAML 파일의 `providerSpec` 필드에 GPU 구성을 지정합니다. 유효한 구성의 다음 예제를 참조하십시오.

```yaml
providerSpec:
    value:
      machineType: a2-highgpu-1g
      onHostMaintenance: Terminate
      restartPolicy: Always
```

1. 머신 유형을 지정합니다. 시스템 유형이 A2 시스템 시리즈에 포함되어 있는지 확인합니다.

2. GPU 지원을 사용하는 경우 `onHostMaintenance` 을 `Terminate` 로 설정해야 합니다.

3. 컴퓨팅 머신 세트에서 배포한 머신에 대한 재시작 정책을 지정합니다. 허용되는 값은 `Always` 또는 `Never` 입니다.

```yaml
providerSpec:
  value:
    gpus:
    - count: 1
      type: nvidia-tesla-p100
    machineType: n1-standard-1
    onHostMaintenance: Terminate
    restartPolicy: Always
```

1. 머신에 연결할 GPU 수를 지정합니다.

2. 머신에 연결할 GPU 유형을 지정합니다. 머신 유형 및 GPU 유형이 호환되는지 확인합니다.

3. 머신 유형을 지정합니다. 머신 유형 및 GPU 유형이 호환되는지 확인합니다.

4. GPU 지원을 사용하는 경우 `onHostMaintenance` 을 `Terminate` 로 설정해야 합니다.

5. 컴퓨팅 머신 세트에서 배포한 머신에 대한 재시작 정책을 지정합니다. 허용되는 값은 `Always` 또는 `Never` 입니다.

#### 2.4.10. 기존 OpenShift Container Platform 클러스터에 GPU 노드 추가

기본 컴퓨팅 머신 세트 구성을 복사하고 수정하여 Google Cloud 클라우드 공급자에 대한 GPU 사용 머신 세트 및 머신을 생성할 수 있습니다.

다음 표에는 검증된 인스턴스 유형이 나열되어 있습니다.

| 인스턴스 유형 | NVIDIA GPU 액셀러레이터 | 최대 GPU 수 | 아키텍처 |
| --- | --- | --- | --- |
| `a2-highgpu-1g` | A100 | 1 | x86 |
| `n1-standard-4` | T4 | 1 | x86 |

프로세스

기존 `MachineSet` 의 사본을 만듭니다.

새 사본에서 `metadata. name` 및 `machine.openshift.io/cluster-api-machineset` 의 두 인스턴스에서 머신 세트 이름을 변경합니다.

새로 복사한 `MachineSet` 에 다음 두 행을 추가하도록 인스턴스 유형을 변경합니다.

```plaintext
machineType: a2-highgpu-1g
onHostMaintenance: Terminate
```

```plaintext
{
    "apiVersion": "machine.openshift.io/v1beta1",
    "kind": "MachineSet",
    "metadata": {
        "annotations": {
            "machine.openshift.io/GPU": "0",
            "machine.openshift.io/memoryMb": "16384",
            "machine.openshift.io/vCPU": "4"
        },
        "creationTimestamp": "2023-01-13T17:11:02Z",
        "generation": 1,
        "labels": {
            "machine.openshift.io/cluster-api-cluster": "myclustername-2pt9p"
        },
        "name": "myclustername-2pt9p-worker-gpu-a",
        "namespace": "openshift-machine-api",
        "resourceVersion": "20185",
        "uid": "2daf4712-733e-4399-b4b4-d43cb1ed32bd"
    },
    "spec": {
        "replicas": 1,
        "selector": {
            "matchLabels": {
                "machine.openshift.io/cluster-api-cluster": "myclustername-2pt9p",
                "machine.openshift.io/cluster-api-machineset": "myclustername-2pt9p-worker-gpu-a"
            }
        },
        "template": {
            "metadata": {
                "labels": {
                    "machine.openshift.io/cluster-api-cluster": "myclustername-2pt9p",
                    "machine.openshift.io/cluster-api-machine-role": "worker",
                    "machine.openshift.io/cluster-api-machine-type": "worker",
                    "machine.openshift.io/cluster-api-machineset": "myclustername-2pt9p-worker-gpu-a"
                }
            },
            "spec": {
                "lifecycleHooks": {},
                "metadata": {},
                "providerSpec": {
                    "value": {
                        "apiVersion": "machine.openshift.io/v1beta1",
                        "canIPForward": false,
                        "credentialsSecret": {
                            "name": "gcp-cloud-credentials"
                        },
                        "deletionProtection": false,
                        "disks": [
                            {
                                "autoDelete": true,
                                "boot": true,
                                "image": "projects/rhcos-cloud/global/images/rhcos-412-86-202212081411-0-gcp-x86-64",
                                "labels": null,
                                "sizeGb": 128,
                                "type": "pd-ssd"
                            }
                        ],
                        "kind": "GCPMachineProviderSpec",
                        "machineType": "a2-highgpu-1g",
                        "onHostMaintenance": "Terminate",
                        "metadata": {
                            "creationTimestamp": null
                        },
                        "networkInterfaces": [
                            {
                                "network": "myclustername-2pt9p-network",
                                "subnetwork": "myclustername-2pt9p-worker-subnet"
                            }
                        ],
                        "preemptible": true,
                        "projectID": "myteam",
                        "region": "us-central1",
                        "serviceAccounts": [
                            {
                                "email": "myclustername-2pt9p-w@myteam.iam.gserviceaccount.com",
                                "scopes": [
                                    "https://www.googleapis.com/auth/cloud-platform"
                                ]
                            }
                        ],
                        "tags": [
                            "myclustername-2pt9p-worker"
                        ],
                        "userDataSecret": {
                            "name": "worker-user-data"
                        },
                        "zone": "us-central1-a"
                    }
                }
            }
        }
    },
    "status": {
        "availableReplicas": 1,
        "fullyLabeledReplicas": 1,
        "observedGeneration": 1,
        "readyReplicas": 1,
        "replicas": 1
    }
}
```

다음 명령을 실행하여 기존 노드, 시스템 및 머신 세트를 확인합니다. 각 노드는 특정 Google Cloud 리전 및 OpenShift Container Platform 역할을 사용하는 머신 정의 인스턴스입니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME                                                             STATUS     ROLES                  AGE     VERSION
myclustername-2pt9p-master-0.c.openshift-qe.internal             Ready      control-plane,master   8h      v1.33.4
myclustername-2pt9p-master-1.c.openshift-qe.internal             Ready      control-plane,master   8h      v1.33.4
myclustername-2pt9p-master-2.c.openshift-qe.internal             Ready      control-plane,master   8h      v1.33.4
myclustername-2pt9p-worker-a-mxtnz.c.openshift-qe.internal       Ready      worker                 8h      v1.33.4
myclustername-2pt9p-worker-b-9pzzn.c.openshift-qe.internal       Ready      worker                 8h      v1.33.4
myclustername-2pt9p-worker-c-6pbg6.c.openshift-qe.internal       Ready      worker                 8h      v1.33.4
myclustername-2pt9p-worker-gpu-a-wxcr6.c.openshift-qe.internal   Ready      worker                 4h35m   v1.33.4
```

다음 명령을 실행하여 `openshift-machine-api` 네임스페이스에 있는 머신 및 머신 세트를 확인합니다. 각 컴퓨팅 머신 세트는 Google Cloud 리전 내의 다른 가용성 영역과 연결되어 있습니다. 설치 프로그램은 가용성 영역에서 컴퓨팅 시스템을 자동으로 로드 밸런싱합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                               DESIRED   CURRENT   READY   AVAILABLE   AGE
myclustername-2pt9p-worker-a       1         1         1       1           8h
myclustername-2pt9p-worker-b       1         1         1       1           8h
myclustername-2pt9p-worker-c       1         1                             8h
myclustername-2pt9p-worker-f       0         0                             8h
```

다음 명령을 실행하여 `openshift-machine-api` 네임스페이스에 있는 머신을 확인합니다. 집합당 하나의 컴퓨팅 시스템만 구성할 수 있지만 특정 리전 및 영역에 노드를 추가하도록 컴퓨팅 시스템 세트를 확장할 수 있습니다.

```shell-session
$ oc get machines -n openshift-machine-api | grep worker
```

```shell-session
myclustername-2pt9p-worker-a-mxtnz       Running   n2-standard-4   us-central1   us-central1-a   8h
myclustername-2pt9p-worker-b-9pzzn       Running   n2-standard-4   us-central1   us-central1-b   8h
myclustername-2pt9p-worker-c-6pbg6       Running   n2-standard-4   us-central1   us-central1-c   8h
```

다음 명령을 실행하여 기존 컴퓨팅 `MachineSet` 정의 중 하나의 사본을 만들고 결과를 JSON 파일로 출력합니다. GPU 지원 컴퓨팅 머신 세트 정의의 기반이 됩니다.

```shell-session
$ oc get machineset myclustername-2pt9p-worker-a -n openshift-machine-api -o json  > <output_file.json>
```

JSON 파일을 편집하여 새 `MachineSet` 정의를 다음과 같이 변경합니다.

`metadata.name` 에 하위 문자열 `gpu` 를 삽입하고 `machine.openshift.io/cluster-api-machineset` 의 두 인스턴스에 하위 문자열 gpu를 삽입하여 머신 세트 `name` 의 이름을 바꿉니다.

새 `MachineSet` 정의의 `machineType` 을 NVIDIA A100 GPU를 포함하는 `a2-highgpu-1g` 로 변경합니다.

```shell-session
jq .spec.template.spec.providerSpec.value.machineType ocp_4.20_machineset-a2-highgpu-1g.json

"a2-highgpu-1g"
```

& `lt;output_file.json` > 파일은 `ocp_4.20_machineset-a2-highgpu-1g.json` 로 저장됩니다.

`ocp_4.20_machineset-a2-highgpu-1g.json` 에서 다음 필드를 업데이트합니다.

`.metadata.name` 을 `gpu` 가 포함된 이름으로 변경합니다.

새 `.metadata.name` 과 일치하도록 `.spec.selector.matchLabels["machine.openshift.io/cluster-api-machineset"]` 을 변경합니다.

새 `.metadata.name` 과 일치하도록 `.spec.template.metadata.labels["machine.openshift.io/cluster-api-machineset"]` 을 변경합니다.

`.spec.template.spec.providerSpec.value.MachineType` 을 `a2-highgpu-1g` 로 변경합니다.

`machineType`: '"onHostMaintenance": "Terminate" 아래에 다음 행을 추가합니다. 예를 들면 다음과 같습니다.

```plaintext
"machineType": "a2-highgpu-1g",
"onHostMaintenance": "Terminate",
```

변경 사항을 확인하려면 다음 명령을 실행하여 원래 컴퓨팅 정의와 새 GPU 사용 노드 정의의 `diff` 를 수행합니다.

```shell-session
$ oc get machineset/myclustername-2pt9p-worker-a -n openshift-machine-api -o json | diff ocp_4.20_machineset-a2-highgpu-1g.json -
```

```shell-session
15c15
<         "name": "myclustername-2pt9p-worker-gpu-a",
---
>         "name": "myclustername-2pt9p-worker-a",
25c25
<                 "machine.openshift.io/cluster-api-machineset": "myclustername-2pt9p-worker-gpu-a"
---
>                 "machine.openshift.io/cluster-api-machineset": "myclustername-2pt9p-worker-a"
34c34
<                     "machine.openshift.io/cluster-api-machineset": "myclustername-2pt9p-worker-gpu-a"
---
>                     "machine.openshift.io/cluster-api-machineset": "myclustername-2pt9p-worker-a"
59,60c59
<                         "machineType": "a2-highgpu-1g",
<                         "onHostMaintenance": "Terminate",
---
>                         "machineType": "n2-standard-4",
```

다음 명령을 실행하여 정의 파일에서 GPU 지원 컴퓨팅 머신 세트를 생성합니다.

```shell-session
$ oc create -f ocp_4.20_machineset-a2-highgpu-1g.json
```

```shell-session
machineset.machine.openshift.io/myclustername-2pt9p-worker-gpu-a created
```

검증

다음 명령을 실행하여 생성한 머신 세트를 확인합니다.

```shell-session
$ oc -n openshift-machine-api get machinesets | grep gpu
```

MachineSet 복제본 수는 `1` 로 설정되므로 새 `Machine` 개체가 자동으로 생성됩니다.

```shell-session
myclustername-2pt9p-worker-gpu-a   1         1         1       1           5h24m
```

다음 명령을 실행하여 머신 세트에서 생성한 `Machine` 오브젝트를 확인합니다.

```shell-session
$ oc -n openshift-machine-api get machines | grep gpu
```

```shell-session
myclustername-2pt9p-worker-gpu-a-wxcr6   Running   a2-highgpu-1g   us-central1   us-central1-a   5h25m
```

참고

노드에 네임스페이스를 지정할 필요가 없습니다. 노드 정의는 클러스터 범위입니다.

#### 2.4.11. Node Feature Discovery Operator 배포

GPU 지원 노드를 생성한 후 예약할 수 있도록 GPU 사용 노드를 검색해야 합니다. 이렇게 하려면 NFD(Node Feature Discovery) Operator를 설치합니다. NFD Operator는 노드에서 하드웨어 장치 기능을 식별합니다. 이는 인프라 노드에서 하드웨어 리소스를 식별하고 카탈로그하는 일반적인 문제를 해결하여 OpenShift Container Platform에서 사용할 수 있도록 합니다.

프로세스

OpenShift Container Platform 콘솔의 소프트웨어 카탈로그에서 Node Feature Discovery Operator를 설치합니다.

NFD Operator를 설치한 후 설치된 Operator 목록에서 Node Feature Discovery 를 선택하고 Create instance 를 선택합니다. 이렇게 하면 각 컴퓨팅 노드에 대해 `nfd-master` 및 `nfd-worker`, 하나의 `nfd-worker` Pod가 `openshift-nfd` 네임스페이스에 설치됩니다.

다음 명령을 실행하여 Operator가 설치되어 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n openshift-nfd
```

```shell-session
NAME                                       READY    STATUS     RESTARTS   AGE

nfd-controller-manager-8646fcbb65-x5qgk    2/2      Running 7  (8h ago)   1d
```

콘솔에 설치된 Oerator로 이동하여 Create Node Feature Discovery 를 선택합니다.

생성 을 선택하여 NFD 사용자 정의 리소스를 빌드합니다. 이렇게 하면 하드웨어 리소스에 대해 OpenShift Container Platform 노드를 폴링하고 카탈로그하는 `openshift-nfd` 네임스페이스에 NFD Pod가 생성됩니다.

검증

빌드에 성공하면 다음 명령을 실행하여 NFD Pod가 각 노드에서 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n openshift-nfd
```

```shell-session
NAME                                       READY   STATUS      RESTARTS        AGE
nfd-controller-manager-8646fcbb65-x5qgk    2/2     Running     7 (8h ago)      12d
nfd-master-769656c4cb-w9vrv                1/1     Running     0               12d
nfd-worker-qjxb2                           1/1     Running     3 (3d14h ago)   12d
nfd-worker-xtz9b                           1/1     Running     5 (3d14h ago)   12d
```

NFD Operator는 벤더 PCI ID를 사용하여 노드의 하드웨어를 식별합니다. NVIDIA는 PCI ID `10de` 를 사용합니다.

다음 명령을 실행하여 NFD Operator가 검색한 NVIDIA GPU를 확인합니다.

```shell-session
$ oc describe node ip-10-0-132-138.us-east-2.compute.internal | egrep 'Roles|pci'
```

```shell-session
Roles: worker

feature.node.kubernetes.io/pci-1013.present=true

feature.node.kubernetes.io/pci-10de.present=true

feature.node.kubernetes.io/pci-1d0f.present=true
```

`10de` 는 GPU 사용 노드의 노드 기능 목록에 나타납니다. 즉, NFD Operator가 GPU 지원 MachineSet에서 노드를 올바르게 식별했습니다.

### 2.5. IBM Cloud에서 컴퓨팅 머신 세트 생성

IBM Cloud®의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.5.1. IBM Cloud에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 리전의 지정된 IBM Cloud® 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 만듭니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <role>
    machine.openshift.io/cluster-api-machine-type: <role>
  name: <infrastructure_id>-<role>-<region>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: ibmcloudproviderconfig.openshift.io/v1beta1
          credentialsSecret:
            name: ibmcloud-credentials
          image: <infrastructure_id>-rhcos
          kind: IBMCloudMachineProviderSpec
          primaryNetworkInterface:
              securityGroups:
              - <infrastructure_id>-sg-cluster-wide
              - <infrastructure_id>-sg-openshift-net
              subnet: <infrastructure_id>-subnet-compute-<zone>
          profile: <instance_profile>
          region: <region>
          resourceGroup: <resource_group>
          userDataSecret:
              name: <role>-user-data
          vpc: <vpc_name>
          zone: <zone>
```

1. 5

7. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 3

8. 9

16. 추가할 노드 레이블입니다.

4. 6

10. 인프라 ID, 노드 레이블 및 리전입니다.

11. 클러스터 설치에 사용된 사용자 지정 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지입니다.

12. 머신을 배치할 리전 내의 인프라 ID 및 영역입니다. 해당 리전이 지정한 영역을 지원하는지 확인합니다.

13. IBM Cloud® 인스턴스 프로필을 지정합니다.

14. 머신을 배치할 리전을 지정합니다.

15. 시스템 리소스가 배치되는 리소스 그룹입니다. 이는 설치 시 지정된 기존 리소스 그룹 또는 인프라 ID를 기반으로 이름이 지정된 설치 관리자 생성 리소스 그룹입니다.

17. VPC 이름입니다.

18. 머신을 배치할 리전 내 영역을 지정합니다. 해당 리전이 지정한 영역을 지원하는지 확인합니다.

#### 2.5.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.5.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

### 2.6. IBM Power Virtual Server에서 컴퓨팅 머신 세트 생성

IBM Power® Virtual Server의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.6.1. IBM Power Virtual Server에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML 파일은 리전의 지정된 IBM Power® Virtual Server 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 생성합니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <role>
    machine.openshift.io/cluster-api-machine-type: <role>
  name: <infrastructure_id>-<role>-<region>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<region>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1
          credentialsSecret:
            name: powervs-credentials
          image:
            name: rhcos-<infrastructure_id>
            type: Name
          keyPairName: <infrastructure_id>-key
          kind: PowerVSMachineProviderConfig
          memoryGiB: 32
          network:
            regex: ^DHCPSERVER[0-9a-z]{32}_Private$
            type: RegEx
          processorType: Shared
          processors: "0.5"
          serviceInstance:
            id: <ibm_power_vs_service_instance_id>
            type: ID
          systemType: s922
          userDataSecret:
            name: <role>-user-data
```

1. 5

7. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 3

8. 9

추가할 노드 레이블입니다.

4. 6

10. 인프라 ID, 노드 레이블 및 리전입니다.

11. 클러스터 설치에 사용된 사용자 지정 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지입니다.

12. 머신을 배치할 리전 내 인프라 ID입니다.

#### 2.6.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.6.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

### 2.7. Nutanix에서 컴퓨팅 머신 세트 생성

Nutanix의 OpenShift Container Platform 클러스터에서 특정 목적을 수행하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.7.1. Nutanix에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 다음 명령으로 레이블이 지정된 노드를 생성하는 Nutanix 컴퓨팅 머신 세트를 정의합니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

#### 2.7.1.1. OpenShift CLI를 사용하여 얻은 값

다음 예제에서는 OpenShift CLI()를 사용하여 클러스터의 일부 값을 가져올 수 있습니다.

```shell
oc
```

인프라 ID

`<infrastructure_id>` 문자열은 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <role>
    machine.openshift.io/cluster-api-machine-type: <role>
  name: <infrastructure_id>-<role>-<zone>
  namespace: openshift-machine-api
  annotations:
    machine.openshift.io/memoryMb: "16384"
    machine.openshift.io/vCPU: "4"
spec:
  replicas: 3
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<zone>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>-<zone>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1
          bootType: ""
          categories:
          - key: <category_name>
            value: <category_value>
          cluster:
            type: uuid
            uuid: <cluster_uuid>
          credentialsSecret:
            name: nutanix-credentials
          image:
            name: <infrastructure_id>-rhcos
            type: name
          kind: NutanixMachineProviderConfig
          memorySize: 16Gi
          project:
            type: name
            name: <project_name>
          subnets:
          - type: uuid
            uuid: <subnet_uuid>
          systemDiskSize: 120Gi
          userDataSecret:
            name: <user_data_secret>
          vcpuSockets: 4
          vcpusPerSocket: 1
```

1. `<infrastructure_id>` 의 경우 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다.

2. 추가할 노드 레이블을 지정합니다.

3. 인프라 ID, 노드 레이블 및 영역을 지정합니다.

4. 클러스터 자동 스케일러에 대한 주석입니다.

5. 컴퓨팅 시스템에서 사용하는 부팅 유형을 지정합니다. 부팅 유형에 대한 자세한 내용은 가상화 된 환경에서 UEFI, Secure Boot 및 TPM 이해를 참조하십시오. 유효한 값은 `Legacy`, `SecureBoot` 또는 `UEFI` 입니다. 기본값은 `Legacy` 입니다.

참고

OpenShift Container Platform 4.20에서 `레거시` 부팅 유형을 사용해야 합니다.

6. 컴퓨팅 머신에 적용할 하나 이상의 Nutanix Prism 카테고리를 지정합니다. 이 스탠자에는 Prism Central에 존재하는 카테고리 키-값 쌍에 대한 `key` 및 `value` 매개변수가 필요합니다. 카테고리에 대한 자세한 내용은 카테고리 관리를 참조하십시오.

7. Nutanix Prism Element 클러스터 구성을 지정합니다. 이 예에서 클러스터 유형은 `uuid` 이므로 `uuid` 스탠자가 있습니다.

8. 사용할 이미지를 지정합니다. 클러스터의 기존 기본 컴퓨팅 머신 세트의 이미지를 사용합니다.

9. Gi에 클러스터의 메모리 양을 지정합니다.

10. 클러스터에 사용하는 Nutanix 프로젝트를 지정합니다. 이 예에서 프로젝트 유형은 `name` 이므로 `name` 스탠자가 있습니다.

11. Prism Element 서브넷 오브젝트에 대해 하나 이상의 UUID를 지정합니다. 지정된 서브넷 중 하나에 대한 CIDR IP 주소 접두사에는 OpenShift Container Platform 클러스터가 사용하는 가상 IP 주소가 포함되어야 합니다. 클러스터의 각 Prism Element 장애 도메인에 대해 최대 32 서브넷이 지원됩니다. 모든 서브넷 UUID 값은 고유해야 합니다.

12. Gi에서 시스템 디스크 크기를 지정합니다.

13. `openshift-machine-api` 네임스페이스에 있는 사용자 데이터 YAML 파일에서 시크릿 이름을 지정합니다. 설치 프로그램이 기본 컴퓨팅 시스템 세트에 채우는 값을 사용합니다.

14. vCPU 소켓 수를 지정합니다.

15. 소켓당 vCPU 수를 지정합니다.

#### 2.7.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.7.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

#### 2.7.4. Nutanix 클러스터의 실패 도메인

Nutanix 클러스터에서 장애 도메인 구성을 추가하거나 업데이트하려면 여러 리소스를 조정해야 합니다. 다음 작업이 필요합니다.

클러스터 인프라 CR(사용자 정의 리소스)을 수정합니다.

클러스터 컨트롤 플레인 머신 세트 CR을 수정합니다.

컴퓨팅 머신 세트 CR을 수정하거나 교체합니다.

자세한 내용은 설치 후 구성 콘텐츠의 "기존 Nutanix 클러스터에 장애 도메인 추가"를 참조하십시오.

추가 리소스

기존 Nutanix 클러스터에 장애 도메인 추가

### 2.8. OpenStack에서 컴퓨팅 머신 세트 생성

RHOSP(Red Hat OpenStack Platform)의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.8.1. RHOSP에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 RHOSP(Red Hat OpenStack Platform)에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 생성합니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <role>
    machine.openshift.io/cluster-api-machine-type: <role>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: <number_of_replicas>
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1alpha1
          cloudName: openstack
          cloudsSecret:
            name: openstack-cloud-credentials
            namespace: openshift-machine-api
          flavor: <nova_flavor>
          image: <glance_image_name_or_location>
          serverGroupID: <optional_UUID_of_server_group>
          kind: OpenstackProviderSpec
          networks:
          - filter: {}
            subnets:
            - filter:
                name: <subnet_name>
                tags: openshiftClusterID=<infrastructure_id>
          primarySubnet: <rhosp_subnet_UUID>
          securityGroups:
          - filter: {}
            name: <infrastructure_id>-worker
          serverMetadata:
            Name: <infrastructure_id>-worker
            openshiftClusterID: <infrastructure_id>
          tags:
          - openshiftClusterID=<infrastructure_id>
          trunk: true
          userDataSecret:
            name: worker-user-data
          availabilityZone: <optional_openstack_availability_zone>
```

1. 5

7. 13

15. 16

17. 18

클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 3

8. 9

19. 추가할 노드 레이블을 지정합니다.

4. 6

10. 인프라 ID 및 노드 레이블을 지정합니다.

11. MachineSet의 서버 그룹 정책을 설정하려면, 서버 그룹 생성 에서 반환된 값을 입력합니다. 대부분의 배포에는 `anti-affinity` 또는 `soft-anti-affinity` 정책이 권장됩니다.

12. 여러 네트워크에 배포해야 합니다. 여러 네트워크를 지정하려면 네트워크 배열에 다른 항목을 추가합니다. 또한 `primarySubnet` 값으로 사용되는 네트워크를 포함해야 합니다.

14. 노드 엔드포인트를 게시할 RHOSP 서브넷을 지정합니다. 일반적으로 이 서브넷은 `install-config.yaml` 파일에서 `machineSubnet` 값으로 사용되는 서브넷과 동일합니다.

#### 2.8.2. RHOSP에서 SR-IOV를 사용하는 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

SR-IOV(Single-root I/O Virtualization)에 대해 클러스터를 구성한 경우 해당 기술을 사용하는 컴퓨팅 머신 세트를 생성할 수 있습니다.

이 샘플 YAML은 SR-IOV 네트워크를 사용하는 컴퓨팅 머신 세트를 정의합니다. 생성된 노드에는 다음 명령으로 레이블이 지정됩니다.

```shell
node-role.openshift.io/<node_role>: ""
```

이 샘플에서 `infrastructure_id` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `node_role` 은 추가할 노드 레이블입니다.

이 샘플은 "radio" 및 "uplink"라는 두 개의 SR-IOV 네트워크를 가정합니다. 네트워크는 `spec.template.spec.providerSpec.value.ports` 목록의 포트 정의에 사용됩니다.

참고

SR-IOV 배포와 관련된 매개변수만 이 샘플에 설명되어 있습니다. 더 일반적인 샘플을 검토하려면 "RHOSP에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML"을 참조하십시오.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <node_role>
    machine.openshift.io/cluster-api-machine-type: <node_role>
  name: <infrastructure_id>-<node_role>
  namespace: openshift-machine-api
spec:
  replicas: <number_of_replicas>
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<node_role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <node_role>
        machine.openshift.io/cluster-api-machine-type: <node_role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<node_role>
    spec:
      metadata:
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1alpha1
          cloudName: openstack
          cloudsSecret:
            name: openstack-cloud-credentials
            namespace: openshift-machine-api
          flavor: <nova_flavor>
          image: <glance_image_name_or_location>
          serverGroupID: <optional_UUID_of_server_group>
          kind: OpenstackProviderSpec
          networks:
            - subnets:
              - UUID: <machines_subnet_UUID>
          ports:
            - networkID: <radio_network_UUID>
              nameSuffix: radio
              fixedIPs:
                - subnetID: <radio_subnet_UUID>
              tags:
                - sriov
                - radio
              vnicType: direct
              portSecurity: false
            - networkID: <uplink_network_UUID>
              nameSuffix: uplink
              fixedIPs:
                - subnetID: <uplink_subnet_UUID>
              tags:
                - sriov
                - uplink
              vnicType: direct
              portSecurity: false
          primarySubnet: <machines_subnet_UUID>
          securityGroups:
          - filter: {}
            name: <infrastructure_id>-<node_role>
          serverMetadata:
            Name: <infrastructure_id>-<node_role>
            openshiftClusterID: <infrastructure_id>
          tags:
          - openshiftClusterID=<infrastructure_id>
          trunk: true
          userDataSecret:
            name: <node_role>-user-data
          availabilityZone: <optional_openstack_availability_zone>
          configDrive: true
```

1. 5

각 포트의 네트워크 UUID를 입력합니다.

2. 6

각 포트의 서브넷 UUID를 입력합니다.

3. 7

`vnicType` 매개 변수의 값은 각 포트에 대해 `direct` 이어야 합니다.

4. 8

`portSecurity` 매개변수 값은 각 포트에 대해 `false` 여야 합니다.

포트 보안이 비활성화되면 포트에 대해 보안 그룹 및 허용되는 주소 쌍을 설정할 수 없습니다. 인스턴스에서 보안 그룹을 설정하면 그룹이 연결된 모든 포트에 적용됩니다.

9. `configDrive` 매개변수 값은 `true` 여야 합니다.

중요

SR-IOV를 사용할 수 있는 컴퓨팅 머신을 배포한 후 레이블을 지정해야 합니다. 예를 들어 명령줄에서 다음을 입력합니다.

```shell-session
$ oc label node <NODE_NAME> feature.node.kubernetes.io/network-sriov.capable="true"
```

참고

네트워크 및 서브넷 목록의 항목을 통해 생성된 포트에 대해 트렁킹이 활성화됩니다. 이러한 목록에서 생성된 포트의 이름은 `<machine_name>-<nameSuffix>` 패턴을 따릅니다. `nameSuffix` 필드는 포트 정의에 필요합니다.

각 포트에 대해 트렁킹을 활성화할 수 있습니다.

선택적으로 태그 목록의 일부로 포트에 `tags` 를 추가할 수 있습니다.

추가 리소스

OpenStack에서 SR-IOV 또는 OVS-DPDK를 사용하는 클러스터 설치 준비

#### 2.8.3. 포트 보안이 비활성화된 SR-IOV 배포를 위한 샘플 YAML

포트 보안이 비활성화된 네트워크에서 SR-IOV(Single-root I/O Virtualization) 포트를 생성하려면 `spec.template.spec.providerSpec.value.ports` 목록에 포트를 포함하는 컴퓨팅 머신 세트를 정의합니다. 표준 SR-IOV 컴퓨팅 머신 세트와 이러한 차이점은 네트워크 및 서브넷 인터페이스를 사용하여 생성된 포트에 대해 발생하는 자동 보안 그룹 및 허용되는 주소 쌍 구성 때문입니다.

머신 서브넷에 대해 정의한 포트에는 다음이 필요합니다.

API 및 ingress 가상 IP 포트에 허용되는 주소 쌍

컴퓨팅 보안 그룹

머신 네트워크 및 서브넷에 연결

참고

포트 보안이 비활성화된 SR-IOV 배포와 관련된 매개변수만 이 샘플에 설명되어 있습니다. 더 일반적인 샘플을 검토하려면 RHOSP에서 SR-IOV를 사용하는 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML을 참조하십시오.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <node_role>
    machine.openshift.io/cluster-api-machine-type: <node_role>
  name: <infrastructure_id>-<node_role>
  namespace: openshift-machine-api
spec:
  replicas: <number_of_replicas>
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<node_role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <node_role>
        machine.openshift.io/cluster-api-machine-type: <node_role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<node_role>
    spec:
      metadata: {}
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1alpha1
          cloudName: openstack
          cloudsSecret:
            name: openstack-cloud-credentials
            namespace: openshift-machine-api
          flavor: <nova_flavor>
          image: <glance_image_name_or_location>
          kind: OpenstackProviderSpec
          ports:
            - allowedAddressPairs:
              - ipAddress: <API_VIP_port_IP>
              - ipAddress: <ingress_VIP_port_IP>
              fixedIPs:
                - subnetID: <machines_subnet_UUID>
              nameSuffix: nodes
              networkID: <machines_network_UUID>
              securityGroups:
                  - <compute_security_group_UUID>
            - networkID: <SRIOV_network_UUID>
              nameSuffix: sriov
              fixedIPs:
                - subnetID: <SRIOV_subnet_UUID>
              tags:
                - sriov
              vnicType: direct
              portSecurity: False
          primarySubnet: <machines_subnet_UUID>
          serverMetadata:
            Name: <infrastructure_ID>-<node_role>
            openshiftClusterID: <infrastructure_id>
          tags:
          - openshiftClusterID=<infrastructure_id>
          trunk: false
          userDataSecret:
            name: worker-user-data
          configDrive: true
```

1. API 및 수신 포트에 허용되는 주소 쌍을 지정합니다.

2. 3

시스템 네트워크 및 서브넷을 지정합니다.

4. 컴퓨팅 시스템 보안 그룹을 지정합니다.

5. `configDrive` 매개변수 값은 `true` 여야 합니다.

참고

네트워크 및 서브넷 목록의 항목을 통해 생성된 포트에 대해 트렁킹이 활성화됩니다. 이러한 목록에서 생성된 포트의 이름은 `<machine_name>-<nameSuffix>` 패턴을 따릅니다. `nameSuffix` 필드는 포트 정의에 필요합니다.

각 포트에 대해 트렁킹을 활성화할 수 있습니다.

선택적으로 태그 목록의 일부로 포트에 `tags` 를 추가할 수 있습니다.

#### 2.8.4. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.8.5. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

### 2.9. vSphere에서 컴퓨팅 머신 세트 생성

VMware vSphere의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.9.1. vSphere에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 VMware vSphere에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 생성합니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  creationTimestamp: null
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      metadata:
        creationTimestamp: null
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          credentialsSecret:
            name: vsphere-cloud-credentials
          dataDisks:
          - name: "<disk_name>"
            provisioningMode: "<mode>"
            sizeGiB: 20
          diskGiB: 120
          kind: VSphereMachineProviderSpec
          memoryMiB: 8192
          metadata:
            creationTimestamp: null
          network:
            devices:
            - networkName: "<vm_network_name>"
          numCPUs: 4
          numCoresPerSocket: 1
          snapshot: ""
          template: <vm_template_name>
          userDataSecret:
            name: worker-user-data
          workspace:
            datacenter: <vcenter_data_center_name>
            datastore: <vcenter_datastore_name>
            folder: <vcenter_vm_folder_path>
            resourcepool: <vsphere_resource_pool>
            server: <vcenter_server_ip>
```

1. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로하는 인프라 ID를 지정합니다. OpenShift CLI () 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell
oc
```

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 인프라 ID 및 노드 레이블을 지정합니다.

3. 추가할 노드 레이블을 지정합니다.

4. 하나 이상의 데이터 디스크 정의를 지정합니다. 자세한 내용은 "머신 세트를 사용하여 데이터 디스크 구성"을 참조하십시오.

5. 컴퓨팅 머신 세트를 배포할 vSphere VM 네트워크를 지정합니다. 이 VM 네트워크는 다른 컴퓨팅 시스템이 클러스터에 상주하는 위치여야 합니다.

6. 사용할 vSphere VM 템플릿 (예: `user-5ddjd-rhcos)` 을 지정합니다.

7. 컴퓨팅 머신 세트를 배포할 vCenter 데이터 센터를 지정합니다.

8. 컴퓨팅 머신 세트를 배포할 vCenter 데이터 저장소를 지정합니다.

9. vCenter의 vSphere VM 폴더에 경로(예: `/dc1/vm/user-inst-5ddjd`)를 지정합니다.

10. VM의 vSphere 리소스 풀을 지정합니다.

11. vCenter 서버 IP 또는 정규화된 도메인 이름을 지정합니다.

#### 2.9.2. 컴퓨팅 머신 세트 관리에 필요한 최소 vCenter 권한

vCenter의 OpenShift Container Platform 클러스터에서 컴퓨팅 머신 세트를 관리하려면 필요한 리소스를 읽고, 생성하고, 삭제하려면 권한이 있는 계정을 사용해야 합니다. 필요한 모든 권한에 액세스할 수 있는 가장 간단한 방법은 글로벌 관리 권한이 있는 계정을 사용하는 것입니다.

글로벌 관리 권한이 있는 계정을 사용할 수 없는 경우 필요한 최소 권한을 부여하려면 역할을 생성해야 합니다. 다음 표에는 컴퓨팅 머신 세트를 생성, 확장 및 삭제하고 OpenShift Container Platform 클러스터에서 머신을 삭제하는 데 필요한 최소 vCenter 역할 및 권한이 나열되어 있습니다.

| 역할의 vSphere 개체 | 필요한 경우 | 필요한 권한 |
| --- | --- | --- |
| vSphere vCenter | Always | `InventoryService.Tagging.AttachTag` `InventoryService.Tagging.CreateCategory` `InventoryService.Tagging.CreateTag` `InventoryService.Tagging.DeleteCategory` `InventoryService.Tagging.DeleteTag` `InventoryService.Tagging.EditCategory` `InventoryService.Tagging.EditTag` InventoryService.Tagging.EditTag `Sessions.ValidateSession` `StorageProfile. Update` 1 |
| vSphere vCenter Cluster | Always | `Resource.AssignVMToPool` |
| vSphere 데이터 저장소 | Always | `Datastore.AllocateSpace` `Datastore.Browse` |
| vSphere Port Group | Always | `Network.Assign` |
| 가상 머신 폴더 | Always | `VirtualMachine.Config.AddRemoveDevice` `VirtualMachine.Config.AdvancedConfig` `VirtualMachine.Config.CPUCount VirtualMachine.Config. DiskExtend` `VirtualMachine.Config.Memory` VirtualMachine.Config.Memory `VirtualMachine.Config.Settings` VirtualMachine.PowerOff VirtualMachine. `PowerOff VirtualMachine. PowerOn Cryostat. CreateFromExisting Cryostat VirtualMachine. Cryostat VirtualMachine.ECDHE VirtualMachine.Provision VirtualMachine.` Config.DiskExtend `VirtualMachine.` Config.MemoryExtend `VirtualMachine.` Cryostat |
| vSphere vCenter 데이터 센터 | 설치 프로그램이 가상 머신 폴더를 생성하는 경우 | `Resource.AssignVMToPool` `VirtualMachine.Provisioning.DeployTemplate` |
| 1 `StorageProfile.Update` 및 `StorageProfile.View` 권한은 CSI(Container Storage Interface)를 사용하는 스토리지 백엔드에만 필요합니다. |

다음 표에서는 컴퓨팅 머신 세트 관리에 필요한 권한 및 전파 설정을 자세히 설명합니다.

| vSphere 오브젝트 | 폴더 유형 | 하위 항목으로 권한 부여 | 권한 필요 |
| --- | --- | --- | --- |
| vSphere vCenter | Always | 필요하지 않음 | 나열된 필수 권한 |
| vSphere vCenter 데이터 센터 | 기존 폴더 | 필요하지 않음 | `ReadOnly` 권한 |
| 설치 프로그램은 폴더를 생성 | 필수 항목 | 나열된 필수 권한 |
| vSphere vCenter Cluster | Always | 필수 항목 | 나열된 필수 권한 |
| vSphere vCenter 데이터 저장소 | Always | 필요하지 않음 | 나열된 필수 권한 |
| vSphere Switch | Always | 필요하지 않음 | `ReadOnly` 권한 |
| vSphere Port Group | Always | 필요하지 않음 | 나열된 필수 권한 |
| vSphere vCenter Virtual Machine Folder | 기존 폴더 | 필수 항목 | 나열된 필수 권한 |

필요한 권한만으로 계정을 생성하는 방법에 대한 자세한 내용은 vSphere 문서에서 vSphere 권한 및 사용자 관리 작업 을 참조하십시오.

#### 2.9.3. 컴퓨팅 머신 세트를 사용하기 위해 사용자 프로비저닝 인프라가 있는 클러스터의 요구사항

사용자 프로비저닝 인프라가 있는 클러스터에서 컴퓨팅 머신 세트를 사용하려면 클러스터 구성이 Machine API 사용을 지원하는지 확인해야 합니다.

#### 2.9.3.1. 인프라 ID 가져오기

컴퓨팅 머신 세트를 생성하려면 클러스터의 인프라 ID를 제공할 수 있어야 합니다.

프로세스

클러스터의 인프라 ID를 가져오려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.infrastructureName}'
```

#### 2.9.3.2. vSphere 인증 정보 요구 사항 충족

컴퓨팅 머신 세트를 사용하려면 Machine API가 vCenter와 상호 작용할 수 있어야 합니다. Machine API 구성 요소가 vCenter와 상호 작용하도록 권한을 부여하는 인증 정보는 `openshift-machine-api` 네임스페이스의 시크릿에 있어야 합니다.

프로세스

필요한 인증 정보가 있는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get secret \
  -n openshift-machine-api vsphere-cloud-credentials \
  -o go-template='{{range $k,$v := .data}}{{printf "%s: " $k}}{{if not $v}}{{$v}}{{else}}{{$v | base64decode}}{{end}}{{"\n"}}{{end}}'
```

```shell-session
<vcenter-server>.password=<openshift-user-password>
<vcenter-server>.username=<openshift-user>
```

여기서 < `vcenter-server` >는 vCenter 서버의 IP 주소 또는 FQDN(정규화된 도메인 이름)이며 < `openshift-user` > 및 < `openshift-user-password` >는 사용할 OpenShift Container Platform 관리자 인증 정보입니다.

보안이 없는 경우 다음 명령을 실행하여 시크릿을 생성합니다.

```shell-session
$ oc create secret generic vsphere-cloud-credentials \
  -n openshift-machine-api \
  --from-literal=<vcenter-server>.username=<openshift-user> --from-literal=<vcenter-server>.password=<openshift-user-password>
```

#### 2.9.3.3. Ignition 구성 요구 사항 충족

VM(가상 머신) 프로비저닝에는 유효한 Ignition 구성이 필요합니다. Ignition 구성에는 Machine Config Operator에서 추가 Ignition 구성을 가져오기 위한 `machine-config-server` 주소와 시스템 신뢰 번들이 포함되어 있습니다.

기본적으로 이 구성은 `machine-api-operator` 네임스페이스의 `worker-user-data` 시크릿에 저장됩니다. 컴퓨팅 머신 세트는 머신 생성 프로세스 중에 시크릿을 참조합니다.

프로세스

필요한 시크릿이 있는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get secret \
  -n openshift-machine-api worker-user-data \
  -o go-template='{{range $k,$v := .data}}{{printf "%s: " $k}}{{if not $v}}{{$v}}{{else}}{{$v | base64decode}}{{end}}{{"\n"}}{{end}}'
```

```shell-session
disableTemplating: false
userData:
  {
    "ignition": {
      ...
      },
    ...
  }
```

1. 전체 출력은 여기에서 생략되지만 이 형식이 있어야 합니다.

보안이 없는 경우 다음 명령을 실행하여 시크릿을 생성합니다.

```shell-session
$ oc create secret generic worker-user-data \
  -n openshift-machine-api \
  --from-file=<installation_directory>/worker.ign
```

여기서 `<installation_directory` >는 클러스터 설치 중에 설치 자산을 저장하는 데 사용된 디렉터리입니다.

추가 리소스

Machine Config Operator 이해

RHCOS 설치 및 OpenShift Container Platform 부트스트랩 프로세스 시작

#### 2.9.4. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

참고

사용자 프로비저닝 인프라로 설치된 클러스터에는 설치 프로그램에서 프로비저닝한 인프라가 있는 클러스터와 다른 네트워킹 스택이 있습니다. 이러한 차이로 인해 사용자 프로비저닝 인프라가 있는 클러스터에서 자동 로드 밸런서 관리가 지원되지 않습니다. 이러한 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

vCenter 인스턴스에 가상 머신을 배포하는데 필요한 권한이 있고 지정된 데이터 저장소에 필요한 액세스 권한이 있습니다.

클러스터가 사용자 프로비저닝 인프라를 사용하는 경우 해당 구성에 대한 특정 머신 API 요구 사항을 충족했습니다.

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

사용자 프로비저닝 인프라가 있는 클러스터에 대한 컴퓨팅 머신 세트를 생성하는 경우 다음과 같은 중요한 값을 기록하십시오.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
...
template:
  ...
  spec:
    providerSpec:
      value:
        apiVersion: machine.openshift.io/v1beta1
        credentialsSecret:
          name: vsphere-cloud-credentials
        dataDisks:
        - name: <disk_name>
          provisioningMode: <mode>
          sizeGiB: 10
        diskGiB: 120
        kind: VSphereMachineProviderSpec
        memoryMiB: 16384
        network:
          devices:
            - networkName: "<vm_network_name>"
        numCPUs: 4
        numCoresPerSocket: 4
        snapshot: ""
        template: <vm_template_name>
        userDataSecret:
          name: worker-user-data
        workspace:
          datacenter: <vcenter_data_center_name>
          datastore: <vcenter_datastore_name>
          folder: <vcenter_vm_folder_path>
          resourcepool: <vsphere_resource_pool>
          server: <vcenter_server_address>
```

1. 필요한 vCenter 인증 정보가 포함된 `openshift-machine-api` 네임스페이스의 시크릿 이름입니다.

2. 데이터 디스크 정의의 컬렉션입니다. 자세한 내용은 "머신 세트를 사용하여 데이터 디스크 구성"을 참조하십시오.

3. 설치 중에 생성된 클러스터의 RHCOS VM 템플릿 이름입니다.

4. 필요한 Ignition 구성 인증 정보가 포함된 `openshift-machine-api` 네임스페이스의 시크릿 이름입니다.

5. vCenter 서버의 IP 주소 또는 FQDN(정규화된 도메인 이름)입니다.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.9.5. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

#### 2.9.6. 머신 세트를 사용하여 머신에 태그 추가

OpenShift Container Platform은 생성된 각 VM(가상 머신)에 클러스터별 태그를 추가합니다. 설치 프로그램은 이러한 태그를 사용하여 클러스터를 제거할 때 삭제할 VM을 선택합니다.

VM에 할당된 클러스터별 태그 외에도 프로비저닝하는 VM에 최대 10개의 vSphere 태그를 추가하도록 머신 세트를 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 vSphere에 설치된 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

클러스터와 연결된 VMware vCenter 콘솔에 액세스할 수 있습니다.

vCenter 콘솔에 태그가 생성되어 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

vCenter 콘솔을 사용하여 시스템에 추가할 태그의 태그 ID를 찾습니다.

vCenter 콘솔에 로그인합니다.

홈 메뉴에서 태그 및 사용자 지정 속성을 클릭합니다.

시스템에 추가할 태그를 선택합니다.

선택한 태그의 브라우저 URL을 사용하여 태그 ID를 식별합니다.

```plaintext
https://vcenter.example.com/ui/app/tags/tag/urn:vmomi:InventoryServiceTag:208e713c-cae3-4b7f-918e-4051ca7d1f97:GLOBAL/permissions
```

```plaintext
urn:vmomi:InventoryServiceTag:208e713c-cae3-4b7f-918e-4051ca7d1f97:GLOBAL
```

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          tagIDs:
          - <tag_id_value>
# ...
```

1. 이 시스템이 프로비저닝한 머신에 추가할 최대 10개의 태그 목록을 지정합니다.

2. 시스템에 추가할 태그 값을 지정합니다. 예를 들어 `urn:vmomi:인벤토리ServiceTag:208e713c-cae3-4b7f-918e-4051ca7d1f97:GLOBAL`.

#### 2.9.7. 머신 세트를 사용하여 여러 네트워크 인터페이스 컨트롤러 구성

VMware vSphere의 OpenShift Container Platform 클러스터는 최대 10개의 NIC(네트워크 인터페이스 컨트롤러)를 노드에 연결할 수 있습니다. 여러 NIC를 구성하면 스토리지 또는 데이터베이스와 같은 사용을 위해 노드 VM(가상 머신)에 전용 네트워크 링크를 제공할 수 있습니다.

머신 세트를 사용하여 이 구성을 관리할 수 있습니다.

설치 중에 구성되지 않은 vSphere 클러스터에서 여러 NIC를 사용하려면 머신 세트를 사용하여 이 구성을 구현할 수 있습니다.

여러 NIC를 사용하도록 설치 중에 클러스터가 설정된 경우 생성한 머신 세트는 기존 장애 도메인 구성을 사용할 수 있습니다.

장애 도메인 구성이 변경되면 머신 세트를 사용하여 해당 변경 사항을 반영할 수 있습니다.

사전 요구 사항

vSphere의 OpenShift Container Platform 클러스터의 경우 CLI(OpenShift CLI)에 대한 관리자 액세스 권한이 있습니다.

```shell
oc
```

프로세스

이미 여러 NIC를 사용하는 클러스터의 경우 다음 명령을 실행하여 `Infrastructure` 리소스에서 다음 값을 가져옵니다.

```shell-session
$ oc get infrastructure cluster -o=jsonpath={.spec.platformSpec.vsphere.failureDomains}
```

| `Infrastructure` 리소스 값 | 샘플 머신 세트의 자리 표시자 값 | 설명 |
| --- | --- | --- |
| `failureDomain.topology.networks[0]` | `<vm_network_name_1>` | 사용할 첫 번째 NIC의 이름입니다. |
| `failureDomain.topology.networks[1]` | `<vm_network_name_2>` | 사용할 두 번째 NIC의 이름입니다. |
| `failureDomain.topology.networks[<n-1>]` | `<vm_network_name_n>` | 사용할 n th NIC의 이름입니다. `Infrastructure` 리소스에서 각 NIC의 이름을 수집합니다. |
| `failureDomain.topology.template` | `<vm_template_name>` | 사용할 vSphere VM 템플릿입니다. |
| `failureDomain.topology.datacenter` | `<vcenter_data_center_name>` | 머신 세트를 배포할 vCenter 데이터 센터입니다. |
| `failureDomain.topology.datastore` | `<vcenter_datastore_name>` | 머신 세트를 배포할 vCenter 데이터 저장소입니다. |
| `failureDomain.topology.folder` | `<vcenter_vm_folder_path>` | vCenter의 vSphere VM 폴더 경로입니다(예: `/dc1/vm/user-inst-5ddjd` ). |
| `failureDomain.topology.computeCluster` + `/Resources` | `<vsphere_resource_pool>` | VM의 vSphere 리소스 풀입니다. |
| `failureDomain.server` | `<vcenter_server_ip>` | vCenter 서버 IP 또는 FQDN(정규화된 도메인 이름)입니다. |

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

다음 예와 같이 포맷된 머신 세트 구성을 사용합니다.

현재 여러 NIC를 사용하는 클러스터의 경우 `Infrastructure` 리소스의 값을 사용하여 머신 세트 사용자 정의 리소스의 값을 채웁니다.

여러 NIC를 사용하지 않는 클러스터의 경우 머신 세트 사용자 정의 리소스에서 사용할 값을 채웁니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          network:
            devices:
            - networkName: "<vm_network_name_1>"
            - networkName: "<vm_network_name_2>"
          template: <vm_template_name>
          workspace:
            datacenter: <vcenter_data_center_name>
            datastore: <vcenter_datastore_name>
            folder: <vcenter_vm_folder_path>
            resourcepool: <vsphere_resource_pool>
            server: <vcenter_server_ip>
# ...
```

1. 사용할 최대 10개의 NIC 목록을 지정합니다.

2. 사용할 vSphere VM 템플릿 (예: `user-5ddjd-rhcos)` 을 지정합니다.

3. 머신 세트를 배포할 vCenter 데이터 센터를 지정합니다.

4. 머신 세트를 배포할 vCenter 데이터 저장소를 지정합니다.

5. vCenter의 vSphere VM 폴더에 경로(예: `/dc1/vm/user-inst-5ddjd`)를 지정합니다.

6. VM의 vSphere 리소스 풀을 지정합니다.

7. vCenter 서버 IP 또는 FQDN(정규화된 도메인 이름)을 지정합니다.

#### 2.9.8. 머신 세트를 사용하여 데이터 디스크 구성

VMware vSphere의 OpenShift Container Platform 클러스터는 VM(가상 머신) 컨트롤러에 최대 29개의 디스크를 추가할 수 있도록 지원합니다.

중요

vSphere 데이터 디스크 구성은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

데이터 디스크를 구성하면 디스크를 VM에 연결하고 이를 사용하여 etcd, 컨테이너 이미지 및 기타 용도의 데이터를 저장할 수 있습니다. 데이터를 분리하면 업그레이드와 같은 중요한 작업에 필요한 리소스가 있도록 기본 디스크를 채우지 않도록 할 수 있습니다.

참고

데이터 디스크를 추가하면 VM에 연결하여 RHCOS가 지정하는 위치에 마운트합니다.

사전 요구 사항

vSphere의 OpenShift Container Platform 클러스터의 경우 CLI(OpenShift CLI)에 대한 관리자 액세스 권한이 있습니다.

```shell
oc
```

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          dataDisks:
          - name: "<disk_name>"
            provisioningMode: "<mode>"
            sizeGiB: 20
          - name: "<disk_name>"
            provisioningMode: "<mode>"
            sizeGiB: 20
# ...
```

1. 1-29 데이터 디스크 정의 컬렉션을 지정합니다. 이 샘플 구성은 두 개의 데이터 디스크 정의를 포함하는 포맷을 보여줍니다.

2. 데이터 디스크의 이름을 지정합니다. 이름은 다음 요구 사항을 충족해야 합니다.

영숫자 문자로 시작 및 끝

영숫자, 하이픈(`-`) 및 밑줄(`_`)으로만 구성됩니다.

최대 길이는 80자입니다.

3. 데이터 디스크 프로비저닝 방법을 지정합니다. 이 값은 설정되지 않은 경우 기본적으로 vSphere 기본 스토리지 정책으로 설정됩니다. 유효한 값은 `Thin`, `Thick`, `EagerlyZeroed` 입니다.

4. 데이터 디스크 크기를 GiB 단위로 지정합니다. 최대 크기는 16384GiB입니다.

### 2.10. 베어 메탈에서 컴퓨팅 머신 세트 생성

베어 메탈의 OpenShift Container Platform 클러스터에서 특정 목적을 충족하기 위해 다른 컴퓨팅 머신 세트를 생성할 수 있습니다. 예를 들어, 지원되는 워크로드를 새 머신으로 이동할 수 있도록 인프라 머신 세트 및 관련 머신을 작성할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

#### 2.10.1. 베어 메탈에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 베어 메탈에서 실행되는 컴퓨팅 머신 세트를 정의하고 다음 명령으로 레이블이 지정된 노드를 생성합니다.

```shell
node-role.kubernetes.io/<role>: ""
```

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<role>` 은 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  creationTimestamp: null
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      metadata:
        creationTimestamp: null
        labels:
          node-role.kubernetes.io/<role>: ""
      providerSpec:
        value:
          apiVersion: baremetal.cluster.k8s.io/v1alpha1
          hostSelector: {}
          image:
            checksum: http:/172.22.0.3:6181/images/rhcos-<version>.<architecture>.qcow2.<md5sum>
            url: http://172.22.0.3:6181/images/rhcos-<version>.<architecture>.qcow2
          kind: BareMetalMachineProviderSpec
          metadata:
            creationTimestamp: null
          userData:
            name: worker-user-data-managed
```

1. 3

5. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로하는 인프라 ID를 지정합니다. OpenShift CLI () 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell
oc
```

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 4

8. 인프라 ID 및 노드 레이블을 지정합니다.

6. 7

9. 추가할 노드 레이블을 지정합니다.

10. API VIP 주소를 사용하도록 `checksum` URL을 편집합니다.

11. API VIP 주소를 사용하도록 `url` URL을 편집합니다.

#### 2.10.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 2.10.3. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

추가 리소스

클러스터 자동 스케일러 리소스 정의

## 3장. 컴퓨팅 머신 세트 수동 스케일링

컴퓨팅 머신 세트에서 머신 인스턴스를 추가하거나 제거할 수 있습니다.

참고

스케일링 이외의 컴퓨팅 머신 세트의 측면을 변경해야하는 경우 컴퓨팅 머신 세트 수정을 참조하십시오.

### 3.1. 사전 요구 사항

클러스터 전체 프록시를 활성화하고 설치 구성에서 `networking.machineNetwork[].cidr` 에 포함되지 않은 컴퓨팅 머신을 확장한 경우 연결 문제를 방지하기 위해 프록시 오브젝트의 `noProxy` 필드에 컴퓨팅 머신을 추가해야 합니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

### 3.2. 컴퓨팅 머신 세트 수동 스케일링

컴퓨팅 머신 세트에서 머신 인스턴스를 추가하거나 제거하려면 컴퓨팅 머신 세트를 수동으로 스케일링할 수 있습니다.

이는 완전히 자동화된 설치 프로그램에 의해 프로비저닝된 인프라 설치와 관련이 있습니다. 사용자 지정 사용자 프로비저닝 인프라 설치에는 컴퓨팅 머신 세트가 없습니다.

사전 요구 사항

OpenShift Container Platform 클러스터 및 아래 명령행을 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터에 있는 컴퓨팅 머신 세트를 확인합니다.

```shell-session
$ oc get machinesets.machine.openshift.io -n openshift-machine-api
```

컴퓨팅 머신 세트는 `<clusterid>-worker-<aws-region-az>` 형식으로 나열됩니다.

다음 명령을 실행하여 클러스터에 있는 컴퓨팅 시스템을 확인합니다.

```shell-session
$ oc get machines.machine.openshift.io -n openshift-machine-api
```

다음 명령을 실행하여 삭제할 컴퓨팅 머신에 주석을 설정합니다.

```shell-session
$ oc annotate machines.machine.openshift.io/<machine_name> -n openshift-machine-api machine.openshift.io/delete-machine="true"
```

다음 명령 중 하나를 실행하여 컴퓨팅 머신 세트를 확장합니다.

```shell-session
$ oc scale --replicas=2 machinesets.machine.openshift.io <machineset> -n openshift-machine-api
```

또는 다음을 수행합니다.

```shell-session
$ oc edit machinesets.machine.openshift.io <machineset> -n openshift-machine-api
```

작은 정보

다음 YAML을 적용하여 컴퓨팅 머신 세트를 확장할 수 있습니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: <machineset>
  namespace: openshift-machine-api
spec:
  replicas: 2
```

컴퓨팅 머신 세트를 확장 또는 축소할 수 있습니다. 새 머신을 사용할 수 있을 때 까지 몇 분 정도 소요됩니다.

중요

기본적으로 머신 컨트롤러는 성공할 때까지 머신이 지원하는 노드를 드레이닝하려고 합니다. Pod 중단 예산을 잘못 구성하는 등 일부 상황에서는 드레이닝 작업이 성공하지 못할 수 있습니다. 드레이닝 작업이 실패하면 머신 컨트롤러에서 머신 제거를 진행할 수 없습니다.

특정 머신에서 `machine.openshift.io/exclude-node-draining` 에 주석을 달아 노드 드레이닝을 건너뛸 수 있습니다.

검증

다음 명령을 실행하여 의도한 시스템의 삭제를 확인합니다.

```shell-session
$ oc get machines.machine.openshift.io
```

### 3.3. 컴퓨팅 머신 세트 삭제 정책

`Random`, `Newest` 및 `Oldest` 의 세 가지 삭제 옵션이 지원됩니다. 기본값은 `Random` 입니다. 즉, 컴퓨팅 머신 세트를 축소할 때 임의의 머신이 선택되어 삭제됩니다. 특정 컴퓨팅 머신 세트를 수정하여 유스 케이스에 따라 삭제 정책을 설정할 수 있습니다.

```yaml
spec:
  deletePolicy: <delete_policy>
  replicas: <desired_replica_count>
```

삭제 정책에 관계없이 관심 머신에 `machine.openshift.io/delete-machine=true` 주석을 추가하여 특정 머신의 삭제 우선 순위를 지정할 수도 있습니다.

중요

기본적으로 OpenShift Container Platform 라우터 Pod는 작업자에게 배포됩니다. 라우터는 웹 콘솔을 포함한 일부 클러스터 리소스에 액세스해야 하므로 먼저 라우터 Pod를 재배치하지 않는 한 작업자 컴퓨팅 머신 세트를 `0` 으로 스케일링하지 마십시오.

참고

사용자 정의 컴퓨팅 머신 세트는 특정 노드에서 서비스가 실행되고 작업자 컴퓨팅 머신 세트가 축소될 때 컨트롤러에서 해당 서비스를 무시해야 하는 유스 케이스에 사용할 수 있습니다. 이로 인해 서비스 중단을 피할 수 있습니다.

### 3.4. 추가 리소스

머신 삭제 단계에 대한 라이프사이클 후크

## 4장. 컴퓨팅 머신 세트 수정

레이블 추가, 인스턴스 유형 변경 또는 블록 스토리지 변경과 같은 컴퓨팅 머신 세트를 수정할 수 있습니다.

참고

다른 변경없이 컴퓨팅 머신 세트를 확장해야하는 경우 컴퓨팅 머신 세트 수동 스케일링을 참조하십시오.

### 4.1. CLI를 사용하여 컴퓨팅 머신 세트 수정

컴퓨팅 머신 세트의 구성을 수정한 다음 CLI를 사용하여 변경 사항을 클러스터의 머신에 전파할 수 있습니다.

컴퓨팅 머신 세트 구성을 업데이트하면 기능을 활성화하거나 생성하는 시스템의 속성을 변경할 수 있습니다. 컴퓨팅 머신 세트를 수정할 때 변경 사항은 업데이트된 `MachineSet` CR(사용자 정의 리소스)을 저장한 후 생성된 컴퓨팅 머신에만 적용됩니다. 변경 사항은 기존 머신에는 영향을 미치지 않습니다.

참고

기본 클라우드 공급자의 변경 사항은 `Machine` 또는 `MachineSet` CR에 반영되지 않습니다. 클러스터 관리 인프라에서 인스턴스 구성을 조정하려면 클러스터 측 리소스를 사용합니다.

컴퓨팅 머신 세트를 스케일링하여 복제본 수를 두 배로 만든 다음 원래 복제본 수로 축소하여 업데이트된 구성을 반영하는 기존 머신을 새 시스템으로 교체할 수 있습니다.

다른 변경을 수행하지 않고 컴퓨팅 머신 세트를 확장해야하는 경우 머신을 삭제할 필요가 없습니다.

참고

기본적으로 OpenShift Container Platform 라우터 Pod는 컴퓨팅 머신에 배포됩니다. 라우터는 웹 콘솔을 포함한 일부 클러스터 리소스에 액세스해야 하므로 먼저 라우터 Pod를 재배치하지 않는 한 컴퓨팅 머신 세트를 `0` 으로 스케일링하지 마십시오.

이 절차의 출력 예제에서는 AWS 클러스터 값을 사용합니다.

사전 요구 사항

OpenShift Container Platform 클러스터는 Machine API를 사용합니다.

OpenShift CLI()를 사용하여 관리자로 클러스터에 로그인했습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터의 컴퓨팅 머신 세트를 나열합니다.

```shell-session
$ oc get machinesets.machine.openshift.io -n openshift-machine-api
```

```plaintext
NAME                           DESIRED   CURRENT   READY   AVAILABLE   AGE
<compute_machine_set_name_1>   1         1         1       1           55m
<compute_machine_set_name_2>   1         1         1       1           55m
```

다음 명령을 실행하여 컴퓨팅 머신 세트를 편집합니다.

```shell-session
$ oc edit machinesets.machine.openshift.io <machine_set_name> \
  -n openshift-machine-api
```

변경 사항을 적용하기 위해 머신 세트를 스케일링할 때 필요하므로 `spec.replicas` 필드의 값을 확인합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-machine-api
spec:
  replicas: 2
# ...
```

1. 이 절차의 예제에서는 `replicas` 값이 `2` 인 컴퓨팅 머신 세트를 보여줍니다.

원하는 구성 옵션을 사용하여 컴퓨팅 머신 세트 CR을 업데이트하고 변경 사항을 저장합니다.

다음 명령을 실행하여 업데이트된 컴퓨팅 머신 세트에서 관리하는 머신을 나열합니다.

```shell-session
$ oc get machines.machine.openshift.io \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machineset=<machine_set_name>
```

```plaintext
NAME                        PHASE     TYPE         REGION      ZONE         AGE
<machine_name_original_1>   Running   m6i.xlarge   us-west-1   us-west-1a   4h
<machine_name_original_2>   Running   m6i.xlarge   us-west-1   us-west-1a   4h
```

업데이트된 컴퓨팅 머신 세트에서 관리하는 각 머신에 대해 다음 명령을 실행하여 `삭제` 주석을 설정합니다.

```shell-session
$ oc annotate machine.machine.openshift.io/<machine_name_original_1> \
  -n openshift-machine-api \
  machine.openshift.io/delete-machine="true"
```

새 구성으로 대체 머신을 생성하려면 다음 명령을 실행하여 컴퓨팅 머신 세트를 복제본 수의 두 배로 스케일링합니다.

```shell-session
$ oc scale --replicas=4 \
  machineset.machine.openshift.io <machine_set_name> \
  -n openshift-machine-api
```

1. 원래 예제 값 `2` 는 `4` 로 두 배가됩니다.

다음 명령을 실행하여 업데이트된 컴퓨팅 머신 세트에서 관리하는 머신을 나열합니다.

```shell-session
$ oc get machines.machine.openshift.io \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machineset=<machine_set_name>
```

```plaintext
NAME                        PHASE          TYPE         REGION      ZONE         AGE
<machine_name_original_1>   Running        m6i.xlarge   us-west-1   us-west-1a   4h
<machine_name_original_2>   Running        m6i.xlarge   us-west-1   us-west-1a   4h
<machine_name_updated_1>    Provisioned    m6i.xlarge   us-west-1   us-west-1a   55s
<machine_name_updated_2>    Provisioning   m6i.xlarge   us-west-1   us-west-1a   55s
```

새 머신이 `Running` 단계에 있는 경우 컴퓨팅 머신 세트를 원래 복제본 수로 확장할 수 있습니다.

이전 구성으로 생성된 머신을 제거하려면 다음 명령을 실행하여 컴퓨팅 머신 세트를 원래 복제본 수로 확장합니다.

```shell-session
$ oc scale --replicas=2 \
  machineset.machine.openshift.io <machine_set_name> \
  -n openshift-machine-api
```

1. 원래 예제 값인 `2` 입니다.

검증

업데이트된 머신 세트로 생성된 머신에 올바른 구성이 있는지 확인하려면 다음 명령을 실행하여 새 머신 중 하나에 대해 CR의 관련 필드를 검사합니다.

```shell-session
$ oc describe machine.machine.openshift.io <machine_name_updated_1> \
  -n openshift-machine-api
```

업데이트된 구성이 없는 컴퓨팅 머신이 삭제되었는지 확인하려면 다음 명령을 실행하여 업데이트된 컴퓨팅 시스템 세트에서 관리하는 머신을 나열합니다.

```shell-session
$ oc get machines.machine.openshift.io \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machineset=<machine_set_name>
```

```plaintext
NAME                        PHASE           TYPE         REGION      ZONE         AGE
<machine_name_original_1>   Deleting        m6i.xlarge   us-west-1   us-west-1a   4h
<machine_name_original_2>   Deleting        m6i.xlarge   us-west-1   us-west-1a   4h
<machine_name_updated_1>    Running         m6i.xlarge   us-west-1   us-west-1a   5m41s
<machine_name_updated_2>    Running         m6i.xlarge   us-west-1   us-west-1a   5m41s
```

```plaintext
NAME                        PHASE           TYPE         REGION      ZONE         AGE
<machine_name_updated_1>    Running         m6i.xlarge   us-west-1   us-west-1a   6m30s
<machine_name_updated_2>    Running         m6i.xlarge   us-west-1   us-west-1a   6m30s
```

추가 리소스

머신 삭제 단계에 대한 라이프사이클 후크

컴퓨팅 머신 세트 수동 스케일링

스케줄러를 사용하여 Pod 배치 제어

## 5장. 머신 단계 및 라이프사이클

머신은 정의된 여러 단계가 있는 라이프사이클을 통해 이동합니다. 시스템 라이프사이클 및 해당 단계를 이해하면 프로시저가 완료되었는지 또는 원하지 않는 동작의 문제를 해결하는 데 도움이 될 수 있습니다. OpenShift Container Platform에서는 지원되는 모든 클라우드 공급자에서 머신 라이프사이클이 일관되게 유지됩니다.

### 5.1. 머신 단계

머신이 라이프사이클을 통과할 때 다양한 단계를 거칩니다. 각 단계는 머신 상태에 대한 기본 표현입니다.

`프로비저닝`

새 시스템을 프로비저닝하라는 요청이 있습니다. 시스템은 아직 존재하지 않으며 인스턴스, 공급자 ID 또는 주소가 없습니다.

`provisioned`

시스템이 존재하고 공급자 ID 또는 주소가 있습니다. 클라우드 공급자가 시스템에 대한 인스턴스를 생성했습니다. 시스템이 아직 노드가 되지 않았으며 머신 오브젝트의 `status.nodeRef` 섹션이 아직 채워지지 않았습니다.

`Running`

시스템이 존재하고 공급자 ID 또는 주소가 있습니다. Ignition이 성공적으로 실행되었으며 클러스터 시스템 승인자가 CSR(인증서 서명 요청)을 승인했습니다. 머신이 노드가 되어 머신 오브젝트의 `status.nodeRef` 섹션에 노드 세부 정보가 포함되어 있습니다.

`삭제 중`

머신을 삭제하라는 요청이 있습니다. 머신 오브젝트에는 삭제 요청 시간을 나타내는 `DeletionTimestamp` 필드가 있습니다.

`Failed`

시스템에 복구할 수 없는 문제가 있습니다. 예를 들어 클라우드 공급자가 머신의 인스턴스를 삭제하는 경우 이러한 상황이 발생할 수 있습니다.

### 5.2. 머신 라이프사이클

라이프사이클은 시스템 프로비저닝 요청으로 시작하여 시스템이 더 이상 존재하지 않을 때까지 계속됩니다.

머신 라이프사이클은 다음 순서로 진행됩니다. 오류 또는 라이프사이클 후크로 인한 중단은 이 개요에 포함되어 있지 않습니다.

다음 이유 중 하나를 위해 새 시스템을 프로비저닝하라는 요청이 있습니다.

클러스터 관리자는 추가 시스템이 필요하므로 머신 세트를 확장합니다.

자동 스케일링 정책은 추가 머신이 필요하므로 머신 세트를 스케일링합니다.

머신 세트에서 관리하는 머신이 실패하거나 삭제되고 머신 세트는 필요한 수를 유지하기 위해 교체를 생성합니다.

시스템이 `프로비저닝` 단계에 들어갑니다.

인프라 공급자는 시스템에 대한 인스턴스를 생성합니다.

시스템에는 공급자 ID 또는 주소가 있으며 `프로비저닝된` 단계를 입력합니다.

Ignition 구성 파일이 처리됩니다.

kubelet은 CSR(인증서 서명 요청)을 발행합니다.

클러스터 시스템 승인자가 CSR을 승인합니다.

시스템이 노드가 되어 `Running` 단계로 들어갑니다.

다음 이유 중 하나로 기존 머신이 삭제될 예정입니다.

`cluster-admin` 권한이 있는 사용자는 아래 명령을 사용합니다.

```shell
oc delete machine
```

머신에 `machine.openshift.io/delete-machine` 주석이 표시됩니다.

머신을 관리하는 머신 세트는 삭제를 위해 이를 표시하여 복제본 수를 조정의 일부로 줄입니다.

클러스터 자동 스케일러는 클러스터의 배포 요구를 충족하기 위해 필요하지 않은 노드를 식별합니다.

비정상 머신을 대체하도록 머신 상태 점검이 구성되어 있습니다.

머신은 `Deleting` 으로 표시되었지만 여전히 API에 존재하는 삭제 단계에 들어갑니다.

머신 컨트롤러는 인프라 공급자에서 인스턴스를 제거합니다.

머신 컨트롤러에서 `Node` 오브젝트를 삭제합니다.

### 5.3. 머신의 단계 확인

OpenShift CLI()를 사용하거나 웹 콘솔을 사용하여 머신의 단계를 찾을 수 있습니다. 이 정보를 사용하여 프로시저가 완료되었는지 또는 원하지 않는 동작의 문제를 해결할 수 있습니다.

```shell
oc
```

#### 5.3.1. CLI를 사용하여 머신의 단계 확인

OpenShift CLI()를 사용하여 머신의 단계를 찾을 수 있습니다.

```shell
oc
```

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

다음 명령CLI를 설치했습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터의 머신을 나열합니다.

```shell-session
$ oc get machine -n openshift-machine-api
```

```plaintext
NAME                                      PHASE     TYPE         REGION      ZONE         AGE
mycluster-5kbsp-master-0                  Running   m6i.xlarge   us-west-1   us-west-1a   4h55m
mycluster-5kbsp-master-1                  Running   m6i.xlarge   us-west-1   us-west-1b   4h55m
mycluster-5kbsp-master-2                  Running   m6i.xlarge   us-west-1   us-west-1a   4h55m
mycluster-5kbsp-worker-us-west-1a-fmx8t   Running   m6i.xlarge   us-west-1   us-west-1a   4h51m
mycluster-5kbsp-worker-us-west-1a-m889l   Running   m6i.xlarge   us-west-1   us-west-1a   4h51m
mycluster-5kbsp-worker-us-west-1b-c8qzm   Running   m6i.xlarge   us-west-1   us-west-1b   4h51m
```

출력의 `PHASE` 열에는 각 시스템의 단계가 포함됩니다.

#### 5.3.2. 웹 콘솔을 사용하여 머신의 단계 확인

OpenShift Container Platform 웹 콘솔을 사용하여 머신의 단계를 찾을 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

프로세스

`cluster-admin` 역할의 사용자로 웹 콘솔에 로그인합니다.

컴퓨팅 → 머신으로 이동합니다.

머신 페이지에서 단계를 찾을 머신의 이름을 선택합니다.

머신 세부 정보 페이지에서 YAML 탭을 선택합니다.

YAML 블록에서 `status.phase` 필드의 값을 찾습니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: Machine
metadata:
  name: mycluster-5kbsp-worker-us-west-1a-fmx8t
# ...
status:
  phase: Running
```

1. 이 예제에서 단계는 `실행` 중입니다.

### 5.4. 추가 리소스

머신 삭제 단계에 대한 라이프사이클 후크

## 6장. 머신 삭제

특정 머신을 삭제할 수 있습니다.

### 6.1. 특정 머신 삭제

특정 머신을 삭제할 수 있습니다.

중요

클러스터가 컨트롤 플레인 시스템 세트를 사용하지 않는 경우 컨트롤 플레인 시스템을 삭제하지 마십시오.

사전 요구 사항

OpenShift Container Platform 클러스터를 설치합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터에 있는 머신을 확인합니다.

```shell-session
$ oc get machine -n openshift-machine-api
```

명령 출력에는 `<clusterid>-<role>-<cloud_region>` 형식의 머신 목록이 포함되어 있습니다.

삭제할 머신을 확인합니다.

다음 명령을 실행하여 시스템을 삭제합니다.

```shell-session
$ oc delete machine <machine> -n openshift-machine-api
```

중요

기본적으로 머신 컨트롤러는 성공할 때까지 머신이 지원하는 노드를 드레이닝하려고 합니다. Pod 중단 예산을 잘못 구성하는 등 일부 상황에서는 드레이닝 작업이 성공하지 못할 수 있습니다. 드레이닝 작업이 실패하면 머신 컨트롤러에서 머신 제거를 진행할 수 없습니다.

특정 머신에서 `machine.openshift.io/exclude-node-draining` 에 주석을 달아 노드 드레이닝을 건너뛸 수 있습니다.

삭제한 머신이 머신 세트에 속하는 경우 지정된 복제본 수를 충족하기 위해 새 머신이 즉시 생성됩니다.

### 6.2. 머신 삭제 단계에 대한 라이프사이클 후크

머신 라이프사이클 후크는 일반 라이프사이클 프로세스가 중단될 수 있는 머신의 조정 라이프사이클에 있는 지점입니다. 머신 `Deleting` 단계에서 이러한 중단은 구성 요소가 머신 삭제 프로세스를 수정할 수 있는 기회를 제공합니다.

#### 6.2.1. 용어 및 정의

머신 삭제 단계에 대한 라이프사이클 후크 동작을 이해하려면 다음 개념을 이해해야 합니다.

조정

조정은 컨트롤러가 클러스터의 실제 상태 및 오브젝트 사양의 요구 사항과 일치하는 오브젝트를 시도하는 프로세스입니다.

머신 컨트롤러

머신 컨트롤러는 머신의 조정 라이프사이클을 관리합니다. 클라우드 플랫폼의 머신의 경우 머신 컨트롤러는 클라우드 공급자의 OpenShift Container Platform 컨트롤러와 플랫폼별 액추에이터의 조합입니다.

머신 삭제 컨텍스트에서 머신 컨트롤러는 다음 작업을 수행합니다.

머신에서 지원하는 노드를 드레이닝합니다.

클라우드 공급자에서 머신 인스턴스를 삭제합니다.

`Node` 오브젝트를 삭제합니다.

라이프사이클 후크

라이프사이클 후크는 일반 라이프사이클 프로세스가 중단될 수 있는 오브젝트의 조정 라이프사이클에 정의된 지점입니다. 구성 요소는 라이프사이클 후크를 사용하여 프로세스에 변경 사항을 삽입하여 원하는 결과를 수행할 수 있습니다.

머신 `Deleting` 단계에는 두 가지 라이프사이클 후크가 있습니다.

머신에서 지원하는 노드를 드레이닝하기 전에 `preDrain` 라이프사이클 후크를 확인해야 합니다.

인프라 공급자에서 인스턴스를 제거하려면 먼저 `preTerminate` 라이프사이클 후크를 확인해야 합니다.

후크 구현 컨트롤러

후크 구현 컨트롤러는 시스템 컨트롤러가 아닌 컨트롤러이며 라이프사이클 후크와 상호 작용할 수 있습니다. 후크 구현 컨트롤러는 다음 작업 중 하나 이상을 수행할 수 있습니다.

라이프사이클 후크를 추가합니다.

라이프사이클 후크에 응답합니다.

라이프사이클 후크를 제거합니다.

각 라이프사이클 후크에는 단일 후크 구현 컨트롤러가 있지만 후크 구현 컨트롤러는 하나 이상의 후크를 관리할 수 있습니다.

#### 6.2.2. 머신 삭제 처리 순서

[FIGURE src="/playbooks/wiki-assets/full_rebuild/machine_management/310_OpenShift_machine_deletion_hooks_0223.png" alt="시스템 'Deleting' 단계의 이벤트 시퀀스입니다." kind="figure" diagram_type="image_figure"]
시스템 'Deleting' 단계의 이벤트 시퀀스입니다.
[/FIGURE]

_Source: `machine_management.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Machine_management-ko-KR/images/7072018272ecd1a19846843f926ad414/310_OpenShift_machine_deletion_hooks_0223.png`_


OpenShift Container Platform 4.20에는 머신 삭제 단계를 위한 두 가지 라이프사이클 후크(`preDrain` 및 `preTerminate`)가 있습니다. 지정된 라이프사이클 지점의 모든 후크가 제거되면 조정이 정상적으로 계속됩니다.

그림 6.1. 머신 삭제 흐름

머신 `Deleting` 단계는 다음 순서로 진행됩니다.

다음 이유 중 하나로 기존 머신이 삭제될 예정입니다.

`cluster-admin` 권한이 있는 사용자는 아래 명령을 사용합니다.

```shell
oc delete machine
```

머신에 `machine.openshift.io/delete-machine` 주석이 표시됩니다.

머신을 관리하는 머신 세트는 삭제를 위해 이를 표시하여 복제본 수를 조정의 일부로 줄입니다.

클러스터 자동 스케일러는 클러스터의 배포 요구를 충족하기 위해 필요하지 않은 노드를 식별합니다.

비정상 머신을 대체하도록 머신 상태 점검이 구성되어 있습니다.

머신은 `Deleting` 으로 표시되었지만 여전히 API에 존재하는 삭제 단계에 들어갑니다.

`preDrain` 라이프사이클 후크가 있는 경우 이를 관리하는 후크 구현 컨트롤러에서 지정된 작업을 수행합니다.

모든 `preDrain` 라이프사이클 후크가 충족될 때까지 머신 상태 조건 `Drainable` 은 `False` 로 설정됩니다.

해결되지 않은 `preDrain` 라이프사이클 후크가 없으며 시스템 상태 조건 `Drainable` 은 `True` 로 설정됩니다.

머신 컨트롤러는 머신에서 지원하는 노드를 드레이닝하려고 합니다.

드레이닝에 실패하면 `Drained` 가 `False` 로 설정되고 머신 컨트롤러에서 노드를 다시 드레이닝하려고 합니다.

드레이닝이 성공하면 `Drained` 가 `True` 로 설정됩니다.

시스템 상태 조건 `Drained` 가 `True` 로 설정됩니다.

`preTerminate` 라이프사이클 후크가 있는 경우 이를 관리하는 후크 구현 컨트롤러에서 지정된 작업을 수행합니다.

모든 `preTerminate` 라이프사이클 후크가 충족될 때까지 머신 상태 `Terminable` 은 `False` 로 설정됩니다.

해결되지 않은 `preTerminate` 라이프사이클 후크가 없으며 시스템 상태 조건 `Terminable` 은 `True` 로 설정됩니다.

머신 컨트롤러는 인프라 공급자에서 인스턴스를 제거합니다.

머신 컨트롤러에서 `Node` 오브젝트를 삭제합니다.

#### 6.2.3. 라이프사이클 후크 구성 삭제

다음 YAML 스니펫에서는 머신 세트 내에서 라이프사이클 후크 구성의 형식 및 배치를 보여줍니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: Machine
metadata:
  ...
spec:
  lifecycleHooks:
    preDrain:
    - name: <hook_name>
      owner: <hook_owner>
  ...
```

1. `preDrain` 라이프사이클 후크의 이름입니다.

2. `preDrain` 라이프사이클 후크를 관리하는 후크 구현 컨트롤러입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: Machine
metadata:
  ...
spec:
  lifecycleHooks:
    preTerminate:
    - name: <hook_name>
      owner: <hook_owner>
  ...
```

1. `preTerminate` 라이프사이클 후크의 이름입니다.

2. `preTerminate` 사전 라이프사이클 후크를 관리하는 후크 구현 컨트롤러입니다.

#### 6.2.3.1. 라이프사이클 후크 구성의 예

다음 예제에서는 머신 삭제 프로세스를 중단하는 여러 가상 라이프사이클 후크를 구현하는 방법을 보여줍니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: Machine
metadata:
  ...
spec:
  lifecycleHooks:
    preDrain:
    - name: MigrateImportantApp
      owner: my-app-migration-controller
    preTerminate:
    - name: BackupFileSystem
      owner: my-backup-controller
    - name: CloudProviderSpecialCase
      owner: my-custom-storage-detach-controller
    - name: WaitForStorageDetach
      owner: my-custom-storage-detach-controller
  ...
```

1. 단일 라이프사이클 후크가 포함된 `preDrain` 라이프사이클 후크입니다.

2. 3개의 라이프사이클 후크가 포함된 `preTerminate` 라이프사이클 후크 스탠자입니다.

3. 두 개의 `preTerminate` 라이프사이클 후크를 관리하는 후크 구현 컨트롤러: `CloudProviderSpecialCase` 및 `WaitForStorageDetach`.

#### 6.2.4. Operator 개발자의 머신 삭제 라이프사이클 후크 예

Operator는 머신 삭제 단계에 라이프사이클 후크를 사용하여 머신 삭제 프로세스를 수정할 수 있습니다. 다음 예제에서는 Operator에서 이 기능을 사용할 수 있는 방법을 보여줍니다.

#### 6.2.4.1. preDrain 라이프사이클 후크 사용 사례 예

사전 교체

Operator는 `preDrain` 라이프사이클 후크를 사용하여 삭제된 머신 인스턴스를 제거하기 전에 교체 머신이 성공적으로 생성되고 클러스터에 가입되었는지 확인할 수 있습니다. 이렇게 하면 머신 교체 중 또는 즉시 초기화되지 않는 대체 인스턴스 중에 중단의 영향을 완화할 수 있습니다.

사용자 정의 드레이닝 논리 구현

Operator는 `preDrain` 라이프사이클 후크를 사용하여 머신 컨트롤러 드레이닝 논리를 다른 드레이닝 컨트롤러로 교체할 수 있습니다. Operator는 드레이닝 논리를 교체하면 각 노드의 워크로드 수명 주기에 대한 유연성 및 제어가 향상됩니다.

예를 들어 머신 컨트롤러 드레이닝 라이브러리는 순서가 지원되지 않지만 사용자 정의 드레이닝 공급자가 이 기능을 제공할 수 있습니다. Operator는 사용자 정의 드레이닝 공급자를 사용하여 노드 드레이닝 전에 미션 크리티컬 애플리케이션 이동 우선 순위를 지정하여 클러스터 용량이 제한된 경우 서비스 중단을 최소화할 수 있습니다.

#### 6.2.4.2. preTerminate 라이프사이클 후크의 사용 사례 예

스토리지 분리 확인

Operator는 `preTerminate` 라이프사이클 후크를 사용하여 인프라 공급자에서 머신을 제거하기 전에 머신에 연결된 스토리지를 확인할 수 있습니다.

로그 안정성 개선

노드를 드레이닝한 후 로그 내보내기 데몬은 로그를 중앙 집중식 로깅 시스템에 동기화하는 데 약간의 시간이 필요합니다.

로깅 Operator는 `preTerminate` 라이프사이클 후크를 사용하여 노드를 드레이닝하는 시점과 인프라 공급자에서 머신이 제거될 때의 지연을 추가할 수 있습니다. 이 지연을 통해 Operator에서 기본 워크로드가 제거되고 더 이상 로그 백로그에 추가되지 않도록 하는 시간을 제공합니다. 로그 백로그에 새 데이터가 추가되지 않으면 로그 내보내기가 동기화 프로세스를 따라 이동하여 모든 애플리케이션 로그를 캡처할 수 있습니다.

#### 6.2.5. 머신 라이프사이클 후크를 통한 쿼럼 보호

Machine API Operator를 사용하는 OpenShift Container Platform 클러스터의 경우 etcd Operator는 머신 삭제 단계에 라이프사이클 후크를 사용하여 쿼럼 보호 메커니즘을 구현합니다.

etcd Operator는 `preDrain` 라이프사이클 후크를 사용하여 컨트롤 플레인 머신의 Pod를 드레이닝하고 제거하는 시기를 제어할 수 있습니다. etcd 쿼럼을 보호하기 위해 etcd Operator는 클러스터 내의 새 노드로 해당 멤버를 마이그레이션할 때까지 etcd 멤버를 제거하지 않습니다.

이 메커니즘을 사용하면 etcd Operator가 etcd 쿼럼의 멤버를 정확하게 제어할 수 있으며 Machine API Operator가 etcd 클러스터에 대한 특정 운영 지식없이 컨트롤 플레인 머신을 안전하게 생성하고 제거할 수 있습니다.

#### 6.2.5.1. 쿼럼 보호 처리 순서를 사용하여 컨트롤 플레인 삭제

컨트롤 플레인 시스템 세트를 사용하는 클러스터에서 컨트롤 플레인 시스템을 교체하면 클러스터에 일시적으로 4개의 컨트롤 플레인 시스템이 있습니다. 네 번째 컨트롤 플레인 노드가 클러스터에 결합되면 etcd Operator가 교체 노드에서 새 etcd 멤버를 시작합니다. etcd Operator에서 이전 컨트롤 플레인 머신이 삭제로 표시된 것을 관찰하면 이전 노드에서 etcd 멤버를 중지하고 교체 etcd 멤버가 클러스터의 쿼럼에 참여하도록 승격합니다.

컨트롤 플레인 머신 `Deleting` 단계는 다음 순서로 진행됩니다.

삭제를 위해 컨트롤 플레인 시스템이 지정되었습니다.

컨트롤 플레인 시스템은 `Deleting` 단계에 들어갑니다.

`preDrain` 라이프사이클 후크를 충족하기 위해 etcd Operator는 다음 작업을 수행합니다.

etcd Operator는 네 번째 컨트롤 플레인 머신이 클러스터에 etcd 멤버로 추가될 때까지 기다립니다. 이 새 etcd 멤버의 상태는 `Running` 이지만 etcd 리더에서 전체 데이터베이스 업데이트가 수신될 때까지 `ready` 되지 않았습니다.

새 etcd 멤버가 전체 데이터베이스 업데이트를 수신하면 etcd Operator는 새 etcd 멤버를 투표 멤버로 승격하고 클러스터에서 이전 etcd 멤버를 제거합니다.

이 전환이 완료되면 이전 etcd pod 및 해당 데이터를 제거하는 것이 안전하므로 `preDrain` 라이프사이클 후크가 제거됩니다.

컨트롤 플레인 시스템 상태 `Drainable` 은 `True` 로 설정됩니다.

머신 컨트롤러는 컨트롤 플레인 시스템에서 지원하는 노드를 드레이닝하려고 합니다.

드레이닝에 실패하면 `Drained` 가 `False` 로 설정되고 머신 컨트롤러에서 노드를 다시 드레이닝하려고 합니다.

드레이닝이 성공하면 `Drained` 가 `True` 로 설정됩니다.

컨트롤 플레인 시스템 상태 `Drained` 가 `True` 로 설정됩니다.

다른 Operator에서 `preTerminate` 라이프사이클 후크를 추가하지 않은 경우 컨트롤 플레인 머신 상태 조건 `Terminable` 이 `True` 로 설정됩니다.

머신 컨트롤러는 인프라 공급자에서 인스턴스를 제거합니다.

머신 컨트롤러에서 `Node` 오브젝트를 삭제합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: Machine
metadata:
  ...
spec:
  lifecycleHooks:
    preDrain:
    - name: EtcdQuorumOperator
      owner: clusteroperator/etcd
  ...
```

1. `preDrain` 라이프사이클 후크의 이름입니다.

2. `preDrain` 라이프사이클 후크를 관리하는 후크 구현 컨트롤러입니다.

### 6.3. 추가 리소스

머신 단계 및 라이프사이클

비정상적인 etcd 멤버 교체

컨트롤 플레인 머신 세트를 사용하여 컨트롤 플레인 시스템 관리

## 7장. OpenShift Container Platform 클러스터에 자동 스케일링 적용

배포 요구 사항에 맞게 클러스터 크기를 자동으로 조정하려면 OpenShift Container Platform 클러스터에 자동 스케일링을 적용합니다. 클러스터 자동 스케일러를 배포한 다음 클러스터의 각 머신 유형에 대한 머신 자동 스케일러를 배포할 수 있습니다. 클러스터 자동 스케일러를 구성한 후 하나 이상의 머신 자동 스케일러를 구성해야 합니다.

중요

Machine API Operator가 작동하는 클러스터에서만 클러스터 자동 스케일러를 구성할 수 있습니다.

### 7.1. 클러스터 자동 스케일러 정보

클러스터 자동 스케일러는 현재 배포 요구 사항에 따라 OpenShift Container Platform 클러스터의 크기를 조정합니다. 이는 Kubernetes 형식의 선언적 인수를 사용하여 특정 클라우드 공급자의 개체에 의존하지 않는 인프라 관리를 제공합니다. 클러스터 자동 스케일러에는 클러스터 범위가 있으며 특정 네임 스페이스와 연결되어 있지 않습니다.

리소스가 부족하여 현재 작업자 노드에서 Pod를 예약할 수 없거나 배포 요구를 충족하기 위해 다른 노드가 필요한 경우 클러스터 자동 스케일러는 클러스터 크기를 늘립니다. 클러스터 자동 스케일러는 사용자가 지정한 제한을 초과하여 클러스터 리소스를 늘리지 않습니다.

클러스터 자동 스케일러는 컨트롤 플레인 노드를 관리하지 않더라도 클러스터의 모든 노드에서 총 메모리, CPU 및 GPU를 계산합니다. 이러한 값은 단일 시스템 지향이 아닙니다. 이는 전체 클러스터에 있는 모든 리소스를 집계한 것입니다. 예를 들어 최대 메모리 리소스 제한을 설정하면 현재 메모리 사용량을 계산할 때 클러스터 자동 스케일러에 클러스터의 모든 노드가 포함됩니다. 그런 다음 이 계산은 클러스터 자동 스케일러에 더 많은 작업자 리소스를 추가할 수 있는 용량이 있는지 확인하는 데 사용됩니다.

중요

작성한 `ClusterAutoscaler` 리솟스 정의의 `maxNodesTotal` 값이 클러스터에서 예상되는 총 머신 수를 대응하기에 충분한 크기의 값인지 확인합니다. 이 값에는 컨트롤 플레인 머신 수 및 확장 가능한 컴퓨팅 머신 수가 포함되어야 합니다.

#### 7.1.1. 자동 노드 제거

10초마다 클러스터 자동 스케일러는 클러스터에서 불필요한 노드를 확인하고 제거합니다. 다음 조건이 적용되는 경우 클러스터 자동 스케일러는 노드가 제거되도록 간주합니다.

노드 사용률은 클러스터의 노드 사용률 수준 임계값보다 적습니다. 노드 사용률 수준은 요청된 리소스의 합계를 노드에 할당된 리소스로 나눈 값입니다. `ClusterAutoscaler` 사용자 지정 리소스에서 값을 지정하지 않으면 클러스터 자동 스케일러는 기본값 `0.5` 를 사용하며 이는 사용률 50%에 해당합니다.

클러스터 자동 스케일러는 노드에서 실행 중인 모든 Pod를 다른 노드로 이동할 수 있습니다. Kubernetes 스케줄러는 노드에 Pod를 예약해야 합니다.

클러스터 자동 스케일러에는 축소 비활성화 주석이 없습니다.

노드에 다음 유형의 pod가 있는 경우 클러스터 자동 스케일러는 해당 노드를 제거하지 않습니다.

제한적인 PDB (Pod Disruption Budgets)가 있는 pod

기본적으로 노드에서 실행되지 않는 Kube 시스템 pod

PDB가 없거나 제한적인 PDB가있는 Kube 시스템 pod

deployment, replica set 또는 stateful set와 같은 컨트롤러 객체가 지원하지 않는 pod

로컬 스토리지가 있는 pod

리소스 부족, 호환되지 않는 노드 선택기 또는 어피니티(affinity), 안티-어피니티(anti-affinity) 일치 등으로 인해 다른 위치로 이동할 수 없는 pod

`"cluster-autoscaler.kubernetes.io/safe-to-evict": "true"` 주석이없는 경우 `"cluster-autoscaler.kubernetes.io/safe-to-evict": "false"` 주석이 있는 pod

예를 들어 최대 CPU 제한을 64코어로 설정하고 각각 코어가 8개인 머신만 생성하도록 클러스터 자동 스케일러를 구성합니다. 클러스터가 30개의 코어로 시작하는 경우 클러스터 자동 스케일러는 총 62개에 대해 32개의 코어가 있는 노드를 최대 4개까지 추가할 수 있습니다.

#### 7.1.2. 제한

클러스터 자동 스케일러를 구성하면 추가 사용 제한이 적용됩니다.

자동 스케일링된 노드 그룹에 있는 노드를 직접 변경하지 마십시오. 동일한 노드 그룹 내의 모든 노드는 동일한 용량 및 레이블을 가지며 동일한 시스템 pod를 실행합니다.

pod 요청을 지정합니다.

pod가 너무 빨리 삭제되지 않도록 해야 하는 경우 적절한 PDB를 구성합니다.

클라우드 제공자 할당량이 구성하는 최대 노드 풀을 지원할 수 있는 충분한 크기인지를 확인합니다.

추가 노드 그룹 Autoscaler, 특히 클라우드 제공자가 제공하는 Autoscaler를 실행하지 마십시오.

참고

클러스터 자동 스케일러는 예약 가능한 Pod가 생성되는 경우에만 자동 스케일링된 노드 그룹에 노드를 추가합니다. 사용 가능한 노드 유형이 Pod 요청에 대한 요구 사항을 충족할 수 없거나 이러한 요구 사항을 충족할 수 있는 노드 그룹이 최대 크기에 있는 경우 클러스터 자동 스케일러를 확장할 수 없습니다.

#### 7.1.3. 다른 스케줄링 기능과의 상호 작용

HPA (Horizond Pod Autoscaler) 및 클러스터 자동 스케일러는 다른 방식으로 클러스터 리소스를 변경합니다. HPA는 현재 CPU 로드를 기준으로 배포 또는 복제 세트의 복제 수를 변경합니다. 로드가 증가하면 HPA는 클러스터에 사용 가능한 리소스 양에 관계없이 새 복제본을 만듭니다. 리소스가 충분하지 않은 경우 클러스터 자동 스케일러는 리소스를 추가하고 HPA가 생성한 pod를 실행할 수 있도록 합니다. 로드가 감소하면 HPA는 일부 복제를 중지합니다. 이 동작으로 일부 노드가 충분히 활용되지 않거나 완전히 비어 있을 경우 클러스터 자동 스케일러가 불필요한 노드를 삭제합니다.

클러스터 자동 스케일러는 pod 우선 순위를 고려합니다. Pod 우선 순위 및 선점 기능을 사용하면 클러스터에 충분한 리소스가 없는 경우 우선 순위에 따라 pod를 예약할 수 있지만 클러스터 자동 스케일러는 클러스터에 모든 pod를 실행하는 데 필요한 리소스가 있는지 확인합니다. 두 기능을 충족하기 위해 클러스터 자동 스케일러에는 우선 순위 컷오프 기능이 포함되어 있습니다. 이 컷오프 기능을 사용하여 "best-effort" pod를 예약하면 클러스터 자동 스케일러가 리소스를 늘리지 않고 사용 가능한 예비 리소스가 있을 때만 실행됩니다.

컷오프 값보다 우선 순위가 낮은 pod는 클러스터가 확장되지 않거나 클러스터가 축소되지 않도록합니다. pod를 실행하기 위해 추가된 새 노드가 없으며 이러한 pod를 실행하는 노드는 리소스를 확보하기 위해 삭제될 수 있습니다.

#### 7.1.4. 클러스터 자동 스케일러 리소스 정의

이 `ClusterAutoscaler` 리소스 정의는 클러스터 자동 스케일러의 매개 변수 및 샘플 값을 표시합니다.

참고

기존 클러스터 자동 스케일러의 구성을 변경하면 다시 시작됩니다.

```yaml
apiVersion: "autoscaling.openshift.io/v1"
kind: "ClusterAutoscaler"
metadata:
  name: "default"
spec:
  podPriorityThreshold: -10
  resourceLimits:
    maxNodesTotal: 24
    cores:
      min: 8
      max: 128
    memory:
      min: 4
      max: 256
    gpus:
    - type: <gpu_type>
      min: 0
      max: 16
  logVerbosity: 4
  scaleDown:
    enabled: true
    delayAfterAdd: 10m
    delayAfterDelete: 5m
    delayAfterFailure: 30s
    unneededTime: 5m
    utilizationThreshold: "0.4"
  scaleUp:
    newPodScaleUpDelay: "10s"
  expanders: ["Random"]
```

| 매개변수 | 설명 |
| --- | --- |
| `podPriorityThreshold` | 클러스터 자동 스케일러가 추가 노드를 배포하도록 하려면 pod가 초과해야하는 우선 순위를 지정합니다. 32 비트 정수 값을 입력합니다. `podPriorityThreshold` 값은 각 pod에 할당한 `PriorityClass` 의 값과 비교됩니다. |
| `maxNodesTotal` | 배포할 최대 노드 수를 지정합니다. 이 값은 Autoscaler가 제어하는 머신뿐 만 아니라 클러스터에 배치 된 총 머신 수입니다. 이 값이 모든 컨트롤 플레인 및 컴퓨팅 머신과 `MachineAutoscaler` 리소스에 지정한 총 복제본 수에 대응할 수 있을 만큼 충분한 크기의 값인지 확인합니다. |
| `cores.min` | 클러스터에 배포할 최소 코어 수를 지정합니다. |
| `cores.max` | 클러스터에 배포할 최대 코어 수를 지정합니다. |
| `memory.min` | 클러스터에서 최소 메모리 크기를 GiB 단위로 지정합니다. |
| `memory.max` | 클러스터에서 최대 메모리 크기를 GiB단위로 지정합니다. |
| `gpus.type` | 선택 사항: GPU 사용 노드를 배포하도록 클러스터 자동 스케일러를 구성하려면 `유형` 값을 지정합니다. 이 값은 해당 유형의 GPU 사용 노드를 관리하는 머신 세트의 `spec.template.spec.metadata.labels[cluster-api/accelerator]` 레이블 값과 일치해야 합니다. 예를 들어 이 값은 Nvidia T4 GPU를 나타내는 `nvidia-t4` 이거나 A10G GPU의 경우 `nvidia-a10g` 일 수 있습니다. 자세한 내용은 "클러스터 자동 스케일러의 GPU 머신 세트 레이블"을 참조하십시오. |
| `gpus.min` | 클러스터에 배포할 지정된 유형의 최소 GPU 수를 지정합니다. |
| `gpus.max` | 클러스터에 배포할 지정된 유형의 최대 GPU 수를 지정합니다. |
| `logVerbosity` | `0` 에서 `10` 사이의 로깅 상세 정보 표시 수준을 지정합니다. 지침에는 다음 로그 수준 임계값이 제공됩니다. `1` : (기본값) 변경 사항에 대한 기본 정보입니다. `4` : 일반적인 문제 해결을 위한 디버그 수준 상세 정보 표시 `9:` 광범위한 프로토콜 수준 디버깅 정보입니다. 값을 지정하지 않으면 기본값 `1` 이 사용됩니다. |
| `scaleDown` | 이 섹션에서는 `ns` , `us` , `ms` , `s` , `m` 및 `h를` 포함하여 유효한 ParseDuration 간격을 사용하여 각 작업에 대해 대기하는 기간을 지정할 수 있습니다. |
| `scaleDown.enabled` | 클러스터 자동 스케일러가 불필요한 노드를 제거할 수 있는지 여부를 지정합니다. |
| `scaleDown.delayAfterAdd` | 선택 사항: 최근에 노드를 추가한 후 노드를 삭제하기 전에 대기할 기간을 지정합니다. 값을 지정하지 않으면 기본값으로 `10m` 이 사용됩니다. |
| `scaleDown.delayAfterDelete` | 선택 사항: 최근에 노드가 삭제된 후 노드를 삭제하기 전에 대기할 기간을 지정합니다. 값을 지정하지 않으면 기본값인 `0` 이 사용됩니다. |
| `scaleDown.delayAfterFailure` | 선택 사항: 축소 실패 후 노드를 삭제하기 전에 대기할 기간을 지정합니다. 값을 지정하지 않으면 기본값으로 `3m` 가 사용됩니다. |
| `scaleDown.unneededTime` | 선택 사항: 불필요한 노드를 삭제할 수 있을 때까지 기간을 지정합니다. 값을 지정하지 않으면 기본값으로 `10m` 이 사용됩니다. |
| `scaleDown.utilizationThreshold` | 선택 사항: 노드 사용률 수준을 지정합니다. 이 사용률 수준의 노드는 삭제할 수 있습니다. 노드 사용률 수준은 요청된 리소스를 노드에 대해 할당된 리소스로 나눈 합계이며 `"0"` 보다 크지만 `"1"` 미만이어야 합니다. 값을 지정하지 않으면 클러스터 자동 스케일러는 기본값 `"0.5"` 를 사용하며 이는 사용률 50%에 해당합니다. 이 값을 문자열로 표현해야 합니다. |
| `scaleUp` | 이 섹션에서는 `ns` , `us` , `ms` , `s` , `m` 및 `h` 를 포함하여 유효한 ParseDuration 간격을 사용하여 새로 보류 중인 포드를 인식하기 전에 대기할 기간을 지정할 수 있습니다. |
| `scaleUp.newPodScaleUpDelay` | 선택 사항: 새 노드를 추가하기 전에 예약할 수 없는 새 Pod를 무시하도록 기간을 지정합니다. 값을 지정하지 않으면 기본값인 `0` 이 사용됩니다. |
| `펼치기` | 선택 사항: 클러스터 자동 스케일러를 사용할 확장기를 지정합니다. 다음 값이 유효합니다. `LeastWaste` : 확장 후 유휴 CPU를 최소화하는 머신 세트를 선택합니다. 여러 머신 세트가 동일한 양의 유휴 CPU를 생성하는 경우 선택 사항으로 사용되지 않는 메모리가 최소화됩니다. `Priority` : 사용자가 할당한 우선 순위가 가장 높은 머신 세트를 선택합니다. 이 확장기를 사용하려면 머신 세트의 우선 순위를 정의하는 구성 맵을 생성해야 합니다. 자세한 내용은 "클러스터 자동 스케일러의 우선 순위 확장기 구성"을 참조하십시오. `random` : (기본값) 머신 세트를 임의로 선택합니다. 값을 지정하지 않으면 기본값 `Random` 이 사용됩니다. `[LeastWaste, Priority]` 형식을 사용하여 여러 확장자를 지정할 수 있습니다. 클러스터 자동 스케일러는 지정된 순서에 따라 각 확장기를 적용합니다. `[LeastWaste, Priority]` 예에서 클러스터 자동 스케일러는 먼저 `LeastWaste` 기준에 따라 평가됩니다. 둘 이상의 머신 세트가 `LeastWaste` 기준을 동일하게 충족하면 클러스터 자동 스케일러가 `우선 순위` 기준에 따라 평가됩니다. 두 개 이상의 머신 세트가 지정된 모든 확장기를 동일하게 충족하는 경우 클러스터 자동 스케일러는 무작위로 사용할 머신을 선택합니다. |

참고

스케일링 작업을 수행할 때 클러스터 자동 스케일러는 클러스터에서 배포할 최소 및 최대 코어 수 또는 메모리 양과 같은 `ClusterAutoscaler` 리소스 정의에 설정된 범위 내에 유지됩니다. 그러나 클러스터 자동 스케일러는 해당 범위 내에 있는 클러스터의 현재 값을 수정하지 않습니다.

클러스터 자동 스케일러가 노드를 관리하지 않더라도 최소 및 최대 CPU, 메모리 및 GPU 값은 클러스터의 모든 노드에서 해당 리소스를 계산하여 결정됩니다. 예를 들어 클러스터 자동 스케일러가 컨트롤 플레인 노드를 관리하지 않더라도 컨트롤 플레인 노드는 클러스터의 총 메모리에서 고려됩니다.

#### 7.1.5. 클러스터 자동 스케일러의 우선 순위 확장기 구성

클러스터 자동 스케일러가 클러스터 크기를 늘릴 때 확장되는 머신 세트를 제어하도록 우선 순위 확장기를 구성합니다. 우선순위 값과 머신 세트를 정의하는 정규식을 나열하여 우선순위 확장기 구성 맵을 생성할 수 있습니다.

사전 요구 사항

Machine API를 사용하는 OpenShift Container Platform 클러스터를 배포했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터의 컴퓨팅 머신 세트를 나열합니다.

```shell-session
$ oc get machinesets.machine.openshift.io
```

```shell-session
NAME                                        DESIRED   CURRENT   READY   AVAILABLE   AGE
archive-agl030519-vplxk-worker-us-east-1c   1         1         1       1           25m
fast-01-agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
fast-02-agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
fast-03-agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
fast-04-agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
prod-01-agl030519-vplxk-worker-us-east-1a   1         1         1       1           33m
prod-02-agl030519-vplxk-worker-us-east-1c   1         1         1       1           33m
```

정규 표현식을 사용하여 우선 순위 수준을 설정할 컴퓨팅 머신 세트의 이름과 일치하는 패턴을 하나 이상 구성합니다.

예를 들어 정규식 패턴 `*fast*` 을 사용하여 이름에 문자열이 `빠르게` 포함된 모든 컴퓨팅 머신 세트와 일치합니다.

다음과 유사한 구성 맵을 정의하는 `cluster-autoscaler-priority-expander.yml` YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-priority-expander
  namespace: openshift-machine-api
data:
  priorities: |-
    10:
      - .*fast.*
      - .*archive.*
    40:
      - .*prod.*
```

머신 세트의 우선 순위를 정의합니다. `우선순위` 값은 양의 정수여야 합니다. 클러스터 자동 스케일러는 낮은 값 우선 순위보다 높은 값 우선 순위를 사용합니다. 각 우선 순위 수준에 사용할 머신 세트에 해당하는 정규식을 지정합니다.

다음 명령을 실행하여 구성 맵을 생성합니다.

```shell-session
$ oc create configmap cluster-autoscaler-priority-expander \
  --from-file=<location_of_config_map_file>/cluster-autoscaler-priority-expander.yml
```

검증

다음 명령을 실행하여 구성 맵을 검토합니다.

```shell-session
$ oc get configmaps cluster-autoscaler-priority-expander -o yaml
```

다음 단계

priority expander를 사용하려면 `ClusterAutoscaler` 리소스 정의가 `expanders: ["Priority"]` 매개변수를 사용하도록 구성되어 있는지 확인합니다.

#### 7.1.6. 클러스터 자동 스케일러의 GPU 머신 세트 레이블 지정

머신 세트 레이블을 사용하여 클러스터 자동 스케일러가 GPU 지원 노드를 배포하는 데 사용할 수 있는 시스템을 표시할 수 있습니다.

사전 요구 사항

클러스터는 클러스터 자동 스케일러를 사용합니다.

프로세스

GPU 사용 노드를 배포하는 데 사용할 클러스터 자동 스케일러 시스템을 생성할 머신 세트에서 `cluster-api/accelerator` 레이블을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: machine-set-name
spec:
  template:
    spec:
      metadata:
        labels:
          cluster-api/accelerator: <accelerator_name>
```

다음과 같습니다.

<accelerator_name>

영숫자 문자 `-`, `_` 또는 `.` 로 구성되고 영숫자 문자로 시작하고 끝나는 레이블을 지정합니다. 예를 들어 `nvidia-t4` 를 사용하여 Nvidia T4 GPU를 표시하거나 A10G GPU의 경우 `nvidia-a10g` 를 사용할 수 있습니다.

참고

`ClusterAutoscaler` CR의 `spec.resourceLimits.gpus.type` 매개변수에 대해 이 레이블의 값을 지정해야 합니다. 자세한 내용은 "클러스터 자동 스케일러 리소스 정의"를 참조하십시오.

#### 7.1.7. 클러스터 자동 스케일러 배포

클러스터 자동 스케일러를 배포하려면 `ClusterAutoscaler` 리소스의 인스턴스를 만듭니다.

프로세스

사용자 지정 리소스 정의가 포함된 `ClusterAutoscaler` 리소스에 대한 YAML 파일을 만듭니다.

다음 명령을 실행하여 클러스터에 사용자 지정 리소스를 생성합니다.

```shell-session
$ oc create -f <filename>.yaml
```

다음과 같습니다.

<filename>

생성한 YAML 파일의 이름을 지정합니다.

### 7.2. 머신 자동 스케일러 정보

머신 자동 스케일러는 OpenShift Container Platform 클러스터에 배포하는 컴퓨팅 머신 세트의 머신 수를 조정합니다. 기본 `worker` 컴퓨팅 머신 세트와 사용자가 생성한 다른 컴퓨팅 머신 세트를 모두 확장할 수 있습니다. 머신 자동 스케일러는 클러스터에 더 많은 배포를 지원하기에 충분한 리소스가 없으면 Machine을 추가합니다. 최소 또는 최대 인스턴스 수와 같은 `MachineAutoscaler` 리소스의 값에 대한 모든 변경 사항은 대상이 되는 컴퓨팅 머신 세트에 즉시 적용됩니다.

중요

머신을 확장하려면 클러스터 자동 스케일러의 머신 자동 스케일러를 배포해야합니다. 클러스터 자동 스케일러는 머신 자동 스케일러가 설정한 컴퓨팅 머신 세트의 주석을 사용하여 확장할 수 있는 리소스를 결정합니다. 머신 자동 스케일러도 정의하지 않고 클러스터 자동 스케일러를 정의하면 클러스터 자동 스케일러는 클러스터를 확장하지 않습니다.

#### 7.2.1. 머신 자동 스케일러 구성

클러스터 자동 스케일러를 배포한 후 클러스터를 확장하는 데 사용되는 컴퓨팅 머신 세트를 참조하는 `MachineAutoscaler` 리소스를 배포합니다.

중요

`ClusterAutoscaler` 리소스를 배포 한 후 하나 이상의 `MachineAutoscaler` 리소스를 배포해야합니다.

참고

각 컴퓨팅 머신 세트에 대해 별도의 리소스를 구성해야 합니다. 컴퓨팅 머신 세트는 리전마다 다르므로 여러 리전에서 머신 스케일링을 활성화할지 여부를 고려하십시오. 스케일링하는 컴퓨팅 머신 세트에는 하나 이상의 시스템이 있어야 합니다.

#### 7.2.1.1. 머신 자동 스케일러 리소스 정의

이 `MachineAutoscaler` 리소스 정의는 머신 자동 스케일러의 매개 변수 및 샘플 값을 표시합니다.

```yaml
apiVersion: "autoscaling.openshift.io/v1beta1"
kind: "MachineAutoscaler"
metadata:
  name: "worker-us-east-1a"
  namespace: "openshift-machine-api"
spec:
  minReplicas: 1
  maxReplicas: 12
  scaleTargetRef:
    apiVersion: machine.openshift.io/v1beta1
    kind: MachineSet
    name: worker-us-east-1a
```

다음과 같습니다.

<name>

머신 자동 스케일러 이름을 지정합니다. 이 머신 자동 스케일러가 스케일링하는 컴퓨팅 머신 세트를 더 쉽게 식별할 수 있도록 스케일링할 컴퓨팅 머신 세트의 이름을 지정하거나 포함합니다. 컴퓨팅 머신 세트 이름의 형식은 `<clusterid>-<machineset>-<region>` 입니다.

<minReplicas>

클러스터 자동 스케일러가 클러스터 스케일링을 시작한 후 지정된 영역에 남아 있어야하는 지정된 유형의 최소 머신 수를 지정하십시오. AWS, Google Cloud, Azure, RHOSP 또는 vSphere에서 실행중인 경우 이 값을 `0` 으로 설정할 수 있습니다. 다른 공급 업체의 경우 이 값을 `0` 으로 설정하지 마십시오.

특수 워크로드에 사용되는 비용이 많이 드는 하드웨어 또는 대규모 머신으로 컴퓨팅 머신 세트를 확장하는 등의 사용 사례에 이 값을 `0` 으로 설정하여 비용을 절감할 수 있습니다. 시스템을 사용하지 않는 경우 클러스터 자동 스케일러는 컴퓨팅 머신 세트를 0으로 축소합니다.

중요

설치 관리자 프로비저닝 인프라의 OpenShift Container Platform 설치 프로세스 중에 생성된 세 개의 컴퓨팅 머신 세트의 경우 `spec.minReplicas` 값을 `0` 으로 설정하지 마십시오.

<maxReplicas>

클러스터 자동 스케일러가 클러스터 스케일링을 초기화한 후 지정된 영역에 배포할 수 있는 지정된 유형의 최대 머신 수를 지정합니다. `ClusterAutoscaler` 리소스 정의에서 `maxNodesTotal` 값이 머신 자동 스케일러가 머신 수를 배포할 수 있는 충분한 크기의 값임을 확인합니다.

<scaleTargetRef>

이 섹션에서는 스케일링할 기존 컴퓨팅 시스템 세트를 설명하는 값을 제공합니다.

<kind>

`kind` 매개 변수 값은 항상 `MachineSet` 입니다.

<name>

`metadata.name` 매개변수 값에 표시된 대로 `name` 값은 기존 컴퓨팅 머신 세트의 이름과 일치해야 합니다.

#### 7.2.2. 머신 자동 스케일러 배포

머신 자동 스케일러를 배포하려면 `MachineAutoscaler` 리소스의 인스턴스를 만듭니다.

프로세스

사용자 지정 리소스 정의가 포함된 `MachineAutoscaler` 리소스에 대한 YAML 파일을 생성합니다.

다음 명령을 실행하여 클러스터에 사용자 지정 리소스를 생성합니다.

```shell-session
$ oc create -f <filename>.yaml
```

다음과 같습니다.

<filename>

생성한 YAML 파일의 이름을 지정합니다.

### 7.3. 머신 자동 스케일러 비활성화

머신 자동 스케일러를 비활성화하려면 해당 `MachineAutoscaler` CR(사용자 정의 리소스)을 삭제합니다.

참고

머신 자동 스케일러를 비활성화해도 클러스터 자동 스케일러가 비활성화되지 않습니다. 클러스터 자동 스케일러를 비활성화하려면 "클러스터 자동 스케일러 비활성화"의 지침을 따르십시오.

프로세스

다음 명령을 실행하여 클러스터의 `MachineAutoscaler` CR을 나열합니다.

```shell-session
$ oc get MachineAutoscaler -n openshift-machine-api
```

```shell-session
NAME                 REF KIND     REF NAME             MIN   MAX   AGE
compute-us-east-1a   MachineSet   compute-us-east-1a   1     12    39m
compute-us-west-1a   MachineSet   compute-us-west-1a   2     4     37m
```

선택 사항: 다음 명령을 실행하여 `MachineAutoscaler` CR의 YAML 파일 백업을 생성합니다.

```shell-session
$ oc get MachineAutoscaler/<machine_autoscaler_name> \
  -n openshift-machine-api \
  -o yaml> <machine_autoscaler_name_backup>.yaml
```

다음과 같습니다.

<machine_autoscaler_name_backup>

백업을 저장할 파일 이름을 지정합니다.

다음 명령을 실행하여 `MachineAutoscaler` CR을 삭제합니다.

```shell-session
$ oc delete MachineAutoscaler/<machine_autoscaler_name> -n openshift-machine-api
```

```shell-session
machineautoscaler.autoscaling.openshift.io "compute-us-east-1a" deleted
```

검증

머신 자동 스케일러가 비활성화되어 있는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get MachineAutoscaler -n openshift-machine-api
```

비활성화된 머신 자동 스케일러가 머신 자동 스케일러 목록에 표시되지 않습니다.

다음 단계

머신 자동 스케일러를 다시 활성화해야 하는 경우 < `machine_autoscaler_name_backup>.yaml` 백업 파일을 사용하고 "머신 자동 스케일러 배포"의 지침을 따르십시오.

### 7.4. 클러스터 자동 스케일러 비활성화

클러스터 자동 스케일러를 비활성화하려면 해당 `ClusterAutoscaler` 리소스를 삭제합니다.

참고

클러스터 자동 스케일러를 비활성화하면 클러스터에 기존 머신 자동 스케일러가 있더라도 클러스터에서 자동 스케일링을 비활성화합니다.

프로세스

다음 명령을 실행하여 클러스터의 `ClusterAutoscaler` 리소스를 나열합니다.

```shell-session
$ oc get ClusterAutoscaler
```

```shell-session
NAME      AGE
default   42m
```

선택 사항: 다음 명령을 실행하여 `ClusterAutoscaler` CR의 YAML 파일 백업을 만듭니다.

```shell-session
$ oc get ClusterAutoscaler/default \
  -o yaml> <cluster_autoscaler_backup_name>.yaml
```

다음과 같습니다.

<cluster_autoscaler_backup_name>

백업을 저장할 파일 이름을 지정합니다.

다음 명령을 실행하여 `ClusterAutoscaler` CR을 삭제합니다.

```shell-session
$ oc delete ClusterAutoscaler/default
```

```shell-session
clusterautoscaler.autoscaling.openshift.io "default" deleted
```

검증

클러스터 자동 스케일러가 비활성화되어 있는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get ClusterAutoscaler
```

```shell-session
No resources found
```

다음 단계

`ClusterAutoscaler` CR을 삭제하여 클러스터 자동 스케일러를 비활성화하면 클러스터가 자동 스케일링되지 않지만 클러스터의 기존 머신 자동 스케일러는 삭제되지 않습니다. 불필요한 머신 자동 스케일러를 정리하려면 "시스템 자동 스케일러 비활성화"를 참조하십시오.

클러스터 자동 스케일러를 다시 활성화해야 하는 경우 < `cluster_autoscaler_name_backup>.yaml` 백업 파일을 사용하고 "클러스터 자동 스케일러 배포"의 지침을 따르십시오.

### 7.5. 추가 리소스

OpenShift Container Platform의 Pod 예약 결정에 Pod 우선순위 포함

## 8장. 인프라 머신 세트 생성

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

인프라 머신 세트를 사용하여 기본 라우터, 통합 컨테이너 이미지 레지스트리 및 클러스터 지표 및 모니터링과 같은 인프라 구성 요소만 호스팅하는 머신을 생성할 수 있습니다. 이러한 인프라 머신은 환경을 실행하는 데 필요한 총 서브스크립션 수에 포함되지 않습니다.

### 8.1. OpenShift Container Platform 인프라 구성 요소

각 자체 관리형 Red Hat OpenShift 서브스크립션에는 OpenShift Container Platform 및 기타 OpenShift 관련 구성 요소에 대한 권한이 포함되어 있습니다. 이러한 권한은 OpenShift Container Platform 컨트롤 플레인 및 인프라 워크로드를 실행하는 데 포함되며 크기 조정 중에 고려하지 않아도 됩니다.

인프라 노드로 자격을 부여하고 포함된 인타이틀먼트를 사용하려면 최종 사용자 애플리케이션의 일부가 아닌 클러스터를 지원하는 구성 요소만 해당 인스턴스에서 실행할 수 있습니다. 예를 들면 다음과 같은 구성 요소가 있습니다.

Kubernetes 및 OpenShift Container Platform 컨트롤 플레인 서비스

기본 라우터

통합된 컨테이너 이미지 레지스트리

HAProxy 기반 Ingress 컨트롤러

사용자 정의 프로젝트를 모니터링하기위한 구성 요소를 포함한 클러스터 메트릭 수집 또는 모니터링 서비스

클러스터 집계 로깅

Red Hat Quay

Red Hat OpenShift Data Foundation

Red Hat Advanced Cluster Security for Kubernetes

Red Hat Advanced Cluster Security for Kubernetes

Red Hat OpenShift GitOps

Red Hat OpenShift Pipelines

Red Hat OpenShift Service Mesh

다른 컨테이너, Pod 또는 구성 요소를 실행하는 모든 노드는 서브스크립션을 적용해야 하는 작업자 노드입니다.

인프라 노드 및 인프라 노드에서 실행할 수 있는 구성 요소에 대한 자세한 내용은 엔터프라이즈 Kubernetes 문서의 OpenShift 크기 조정 및 서브스크립션 가이드의 "Red Hat OpenShift 컨트롤 플레인 및 인프라 노드" 섹션을 참조하십시오.

인프라 노드를 생성하려면 머신 세트를 사용 하거나 노드에 레이블을 지정 하거나 머신 구성 풀을 사용 할 수 있습니다.

#### 8.1.1. 다른 클라우드의 인프라 머신 세트 생성

클라우드에 샘플 컴퓨팅 머신 세트를 사용합니다.

#### 8.1.1.1. AWS에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

샘플 YAML은 `us-east-1a` AWS(Amazon Web Services) 로컬 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 생성합니다.

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<infra>` 는 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-infra-<zone>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra-<zone>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: infra
        machine.openshift.io/cluster-api-machine-type: infra
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra-<zone>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/infra: ""
      providerSpec:
        value:
          ami:
            id: ami-046fe691f52a953f9
          apiVersion: machine.openshift.io/v1beta1
          blockDevices:
            - ebs:
                iops: 0
                volumeSize: 120
                volumeType: gp2
          credentialsSecret:
            name: aws-cloud-credentials
          deviceIndex: 0
          iamInstanceProfile:
            id: <infrastructure_id>-worker-profile
          instanceType: m6i.large
          kind: AWSMachineProviderConfig
          placement:
            availabilityZone: <zone>
            region: <region>
          securityGroups:
            - filters:
                - name: tag:Name
                  values:
                    - <infrastructure_id>-node
            - filters:
                - name: tag:Name
                  values:
                    - <infrastructure_id>-lb
          subnet:
            filters:
              - name: tag:Name
                values:
                  - <infrastructure_id>-private-<zone>
          tags:
            - name: kubernetes.io/cluster/<infrastructure_id>
              value: owned
            - name: <custom_tag_name>
              value: <custom_tag_value>
          userDataSecret:
            name: worker-user-data
      taints:
        - key: node-role.kubernetes.io/infra
          effect: NoSchedule
```

1. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 인프라 ID, `infra` 역할 노드 레이블 및 영역을 지정합니다.

3. `infra` 역할 노드 레이블을 지정합니다.

4. OpenShift Container Platform 노드의 AWS 영역에 유효한 RHCOS(Red Hat Enterprise Linux CoreOS) Amazon 머신 이미지(AMI)를 지정합니다. AWS Marketplace 이미지를 사용하려면 해당 리전의 AMI ID를 받으려면 AWS Marketplace 에서 OpenShift Container Platform 서브스크립션을 완료해야 합니다.

```shell-session
$ oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.ami.id}{"\n"}' \
    get machineset/<infrastructure_id>-<role>-<zone>
```

5. 영역 이름을 지정합니다(예: `us-east-1a`).

6. 리전을 지정합니다(예: `us-east-1`).

7. 인프라 ID 및 영역을 지정합니다.

8. 선택 사항: 클러스터의 사용자 지정 태그 데이터를 지정합니다. 예를 들어 `Email:admin-email@example.com` 의 `name:value` 쌍을 지정하여 관리자 연락처 이메일 주소를 추가할 수 있습니다.

참고

`install-config.yml` 파일에서 설치 중에 사용자 지정 태그를 지정할 수도 있습니다. `install-config.yml` 파일과 머신 세트에 동일한 `name` 데이터가 있는 태그가 포함된 경우 머신 세트의 태그 값이 `install-config.yml` 파일의 태그 값보다 우선합니다.

9. 사용자 워크로드가 `infra` 노드에서 예약되지 않도록 테인트를 지정합니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

AWS에서 실행되는 머신 세트는 보장되지 않는 Spot 인스턴스를 지원합니다. AWS의 온 디맨드 인스턴스에 비해 저렴한 가격으로 Spot 인스턴스를 사용하여 비용을 절약할 수 있습니다. `spotMarketOptions` 를 `MachineSet` YAML 파일에 추가하여 Spot 인스턴스를 구성합니다.

#### 8.1.1.2. Azure에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 리전의 `1` Microsoft Azure 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 만듭니다.

이 샘플에서 < `infrastructure_id` >는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `infra` 는 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: infra
    machine.openshift.io/cluster-api-machine-type: infra
  name: <infrastructure_id>-infra-<region>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra-<region>
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: infra
        machine.openshift.io/cluster-api-machine-type: infra
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra-<region>
    spec:
      metadata:
        creationTimestamp: null
        labels:
          machine.openshift.io/cluster-api-machineset: <machineset_name>
          node-role.kubernetes.io/infra: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/<infrastructure_id>-rg/providers/Microsoft.Compute/galleries/gallery_<infrastructure_id>/images/<infrastructure_id>-gen2/versions/latest
            sku: ""
            version: ""
          internalLoadBalancer: ""
          kind: AzureMachineProviderSpec
          location: <region>
          managedIdentity: <infrastructure_id>-identity
          metadata:
            creationTimestamp: null
          natRule: null
          networkResourceGroup: ""
          osDisk:
            diskSizeGB: 128
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: ""
          resourceGroup: <infrastructure_id>-rg
          sshPrivateKey: ""
          sshPublicKey: ""
          tags:
            <custom_tag_name_1>: <custom_tag_value_1>
            <custom_tag_name_2>: <custom_tag_value_2>
          subnet: <infrastructure_id>-<role>-subnet
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_D4s_v3
          vnet: <infrastructure_id>-vnet
          zone: "1"
      taints:
      - key: node-role.kubernetes.io/infra
        effect: NoSchedule
```

1. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

다음 명령을 실행하여 서브넷을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.subnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

다음 명령을 실행하여 vnet을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.vnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

2. `infra` 노드 레이블을 지정합니다.

3. 인프라 ID, 인프라 노드 `레이블` 및 리전을 지정합니다.

4. 컴퓨팅 머신 세트의 이미지 세부 정보를 지정합니다. Azure Marketplace 이미지를 사용하려면 "Azure Marketplace 오퍼링 사용"을 참조하십시오.

5. 인스턴스 유형과 호환되는 이미지를 지정합니다. 설치 프로그램에서 생성한 Hyper-V generation V2 이미지에는 `-gen2` 접미사가 있지만 V1 이미지의 접미사 없이 이름이 동일합니다.

6. 머신을 배치할 리전을 지정합니다.

7. 선택 사항: 머신 세트에서 사용자 지정 태그를 지정합니다. < `custom_tag_name` > 필드에 태그 이름과 < `custom_tag_value` > 필드에 해당 태그 값을 입력합니다.

8. 머신을 배치할 리전 내 영역을 지정합니다. 해당 리전에서 지정하는 영역을 지원하는지 확인합니다.

중요

리전에서 가용성 영역을 지원하는 경우 영역을 지정해야 합니다. 영역을 지정하면 Pod에 영구 볼륨 연결이 필요한 경우 볼륨 노드 유사성 오류가 발생하지 않습니다. 이를 위해 동일한 리전의 각 영역에 대한 컴퓨팅 머신 세트를 생성할 수 있습니다.

9. 사용자 워크로드가 인프라 노드에서 예약되지 않도록 테인트를 지정합니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

Azure에서 실행되는 머신 세트는 보장되지 않는 Spot 가상 머신을 지원합니다. Azure의 표준 가상 머신에 비해 더 낮은 가격으로 Spot 가상 머신을 사용하여 비용을 절감할 수 있습니다. `spotVMOptions` 를 `MachineSet` YAML 파일에 추가하여 Spot 가상 머신을 구성할 수 있습니다.

추가 리소스

Azure Marketplace 오퍼링 사용

#### 8.1.1.3. Azure Stack Hub에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 리전의 `1` Microsoft Azure 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 만듭니다.

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<infra>` 는 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <infra>
    machine.openshift.io/cluster-api-machine-type: <infra>
  name: <infrastructure_id>-infra-<region>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra-<region>
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <infra>
        machine.openshift.io/cluster-api-machine-type: <infra>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra-<region>
    spec:
      metadata:
        creationTimestamp: null
        labels:
          node-role.kubernetes.io/infra: ""
      taints:
      - key: node-role.kubernetes.io/infra
        effect: NoSchedule
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          availabilitySet: <availability_set>
          credentialsSecret:
            name: azure-cloud-credentials
            namespace: openshift-machine-api
          image:
            offer: ""
            publisher: ""
            resourceID: /resourceGroups/<infrastructure_id>-rg/providers/Microsoft.Compute/images/<infrastructure_id>
            sku: ""
            version: ""
          internalLoadBalancer: ""
          kind: AzureMachineProviderSpec
          location: <region>
          managedIdentity: <infrastructure_id>-identity
          metadata:
            creationTimestamp: null
          natRule: null
          networkResourceGroup: ""
          osDisk:
            diskSizeGB: 128
            managedDisk:
              storageAccountType: Premium_LRS
            osType: Linux
          publicIP: false
          publicLoadBalancer: ""
          resourceGroup: <infrastructure_id>-rg
          sshPrivateKey: ""
          sshPublicKey: ""
          subnet: <infrastructure_id>-<role>-subnet
          userDataSecret:
            name: worker-user-data
          vmSize: Standard_DS4_v2
          vnet: <infrastructure_id>-vnet
          zone: "1"
```

1. 5

7. 14

16. 17

18. 21

클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

다음 명령을 실행하여 서브넷을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.subnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

다음 명령을 실행하여 vnet을 가져올 수 있습니다.

```shell-session
$  oc -n openshift-machine-api \
    -o jsonpath='{.spec.template.spec.providerSpec.value.vnet}{"\n"}' \
    get machineset/<infrastructure_id>-worker-centralus1
```

2. 3

8. 9

11. 19

20. `<infra>` 노드 레이블을 지정합니다.

4. 6

10. 인프라 ID, `<infra>` 노드 레이블 및 리전을 지정합니다.

12. 사용자 워크로드가 인프라 노드에서 예약되지 않도록 테인트를 지정합니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

15. 머신을 배치할 리전을 지정합니다.

13. 클러스터의 가용성 세트를 지정합니다.

22. 머신을 배치할 리전 내 영역을 지정합니다. 해당 리전이 지정한 영역을 지원하는지 확인합니다.

참고

Azure Stack Hub에서 실행되는 머신 세트는 보장되지 않는 Spot 가상 머신을 지원하지 않습니다.

#### 8.1.1.4. IBM Cloud에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 리전의 지정된 IBM Cloud® 영역에서 실행되는 컴퓨팅 머신 세트를 정의하고 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 생성합니다.

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<infra>` 는 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <infra>
    machine.openshift.io/cluster-api-machine-type: <infra>
  name: <infrastructure_id>-<infra>-<region>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<infra>-<region>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <infra>
        machine.openshift.io/cluster-api-machine-type: <infra>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<infra>-<region>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/infra: ""
      providerSpec:
        value:
          apiVersion: ibmcloudproviderconfig.openshift.io/v1beta1
          credentialsSecret:
            name: ibmcloud-credentials
          image: <infrastructure_id>-rhcos
          kind: IBMCloudMachineProviderSpec
          primaryNetworkInterface:
              securityGroups:
              - <infrastructure_id>-sg-cluster-wide
              - <infrastructure_id>-sg-openshift-net
              subnet: <infrastructure_id>-subnet-compute-<zone>
          profile: <instance_profile>
          region: <region>
          resourceGroup: <resource_group>
          userDataSecret:
              name: <role>-user-data
          vpc: <vpc_name>
          zone: <zone>
        taints:
        - key: node-role.kubernetes.io/infra
          effect: NoSchedule
```

1. 5

7. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 3

8. 9

16. `<infra>` 노드 레이블입니다.

4. 6

10. 인프라 ID, `<infra>` 노드 레이블 및 리전입니다.

11. 클러스터 설치에 사용된 사용자 지정 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지입니다.

12. 머신을 배치할 리전 내의 인프라 ID 및 영역입니다. 해당 리전이 지정한 영역을 지원하는지 확인합니다.

13. IBM Cloud® 인스턴스 프로필을 지정합니다.

14. 머신을 배치할 리전을 지정합니다.

15. 시스템 리소스가 배치되는 리소스 그룹입니다. 이는 설치 시 지정된 기존 리소스 그룹 또는 인프라 ID를 기반으로 이름이 지정된 설치 관리자 생성 리소스 그룹입니다.

17. VPC 이름입니다.

18. 머신을 배치할 리전 내 영역을 지정합니다. 해당 리전이 지정한 영역을 지원하는지 확인합니다.

19. 사용자 워크로드가 인프라 노드에서 예약되지 않도록 하는 테인트입니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

#### 8.1.1.5. Google Cloud에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 Google Cloud에서 실행되는 컴퓨팅 머신 세트를 정의하고 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 생성합니다. 여기서 `infra` 는 추가할 노드 레이블입니다.

#### 8.1.1.5.1. OpenShift CLI를 사용하여 얻은 값

다음 예제에서는 OpenShift CLI를 사용하여 클러스터의 일부 값을 가져올 수 있습니다.

인프라 ID

`<infrastructure_id>` 문자열은 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

이미지 경로

`<path_to_image>` 문자열은 디스크를 생성하는 데 사용된 이미지의 경로입니다. OpenShift CLI가 설치되어 있으면 다음 명령을 실행하여 이미지에 대한 경로를 얻을 수 있습니다.

```shell-session
$ oc -n openshift-machine-api \
  -o jsonpath='{.spec.template.spec.providerSpec.value.disks[0].image}{"\n"}' \
  get machineset/<infrastructure_id>-worker-a
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-w-a
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-w-a
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <infra>
        machine.openshift.io/cluster-api-machine-type: <infra>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-w-a
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/infra: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          canIPForward: false
          credentialsSecret:
            name: gcp-cloud-credentials
          deletionProtection: false
          disks:
          - autoDelete: true
            boot: true
            image: <path_to_image>
            labels: null
            sizeGb: 128
            type: pd-ssd
          gcpMetadata:
          - key: <custom_metadata_key>
            value: <custom_metadata_value>
          kind: GCPMachineProviderSpec
          machineType: n1-standard-4
          metadata:
            creationTimestamp: null
          networkInterfaces:
          - network: <infrastructure_id>-network
            subnetwork: <infrastructure_id>-worker-subnet
          projectID: <project_name>
          region: us-central1
          serviceAccounts:
          - email: <infrastructure_id>-w@<project_name>.iam.gserviceaccount.com
            scopes:
            - https://www.googleapis.com/auth/cloud-platform
          tags:
            - <infrastructure_id>-worker
          userDataSecret:
            name: worker-user-data
          zone: us-central1-a
      taints:
      - key: node-role.kubernetes.io/infra
        effect: NoSchedule
```

1. `<infrastructure_id>` 의 경우 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다.

2. `<infra>` 의 경우 `<infra>` 노드 레이블을 지정합니다.

3. 현재 컴퓨팅 머신 세트에 사용되는 이미지의 경로를 지정합니다.

Google Cloud Marketplace 이미지를 사용하려면 다음을 사용할 제안을 지정합니다.

OpenShift Container Platform: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-ocp-413-x86-64-202305021736`

OpenShift Platform Plus: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-opp-413-x86-64-202305021736`

OpenShift Kubernetes Engine: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-oke-413-x86-64-202305021736`

4. 선택 사항: `key:value` 쌍 형식으로 사용자 지정 메타데이터를 지정합니다. 사용 사례의 예는 사용자 지정 메타데이터 설정에 대한 Google Cloud 설명서를 참조하십시오.

5. & `lt;project_name` > 의 경우 클러스터에 사용하는 Google Cloud 프로젝트의 이름을 지정합니다.

6. 단일 서비스 계정을 지정합니다. 여러 서비스 계정이 지원되지 않습니다.

7. 사용자 워크로드가 인프라 노드에서 예약되지 않도록 테인트를 지정합니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

Google Cloud에서 실행되는 머신 세트는 보장되지 않는 선점 가능한 가상 머신 인스턴스를 지원합니다. Google Cloud의 일반 인스턴스에 비해 더 낮은 가격으로 선점 가능한 가상 머신 인스턴스를 사용하여 비용을 절감할 수 있습니다. preemptible 을 `MachineSet` YAML 파일에 `preemptible` 추가하여 선점 가능한 가상 머신 인스턴스를 구성할 수 있습니다.

#### 8.1.1.6. Nutanix에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 생성하는 Nutanix 컴퓨팅 머신 세트를 정의합니다.

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<infra>` 는 추가할 노드 레이블입니다.

#### 8.1.1.6.1. OpenShift CLI를 사용하여 얻은 값

다음 예제에서는 OpenShift CLI()를 사용하여 클러스터의 일부 값을 가져올 수 있습니다.

```shell
oc
```

인프라 ID

`<infrastructure_id>` 문자열은 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <infra>
    machine.openshift.io/cluster-api-machine-type: <infra>
  name: <infrastructure_id>-<infra>-<zone>
  namespace: openshift-machine-api
  annotations:
    machine.openshift.io/memoryMb: "16384"
    machine.openshift.io/vCPU: "4"
spec:
  replicas: 3
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<infra>-<zone>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <infra>
        machine.openshift.io/cluster-api-machine-type: <infra>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<infra>-<zone>
    spec:
      metadata:
        labels:
          node-role.kubernetes.io/infra: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1
          bootType: ""
          categories:
          - key: <category_name>
            value: <category_value>
          cluster:
            type: uuid
            uuid: <cluster_uuid>
          credentialsSecret:
            name: nutanix-credentials
          image:
            name: <infrastructure_id>-rhcos
            type: name
          kind: NutanixMachineProviderConfig
          memorySize: 16Gi
          project:
            type: name
            name: <project_name>
          subnets:
          - type: uuid
            uuid: <subnet_uuid>
          systemDiskSize: 120Gi
          userDataSecret:
            name: <user_data_secret>
          vcpuSockets: 4
          vcpusPerSocket: 1
      taints:
      - key: node-role.kubernetes.io/infra
        effect: NoSchedule
```

1. `<infrastructure_id>` 의 경우 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다.

2. `<infra>` 노드 레이블을 지정합니다.

3. 인프라 ID, `<infra>` 노드 레이블 및 영역을 지정합니다.

4. 클러스터 자동 스케일러에 대한 주석입니다.

5. 컴퓨팅 시스템에서 사용하는 부팅 유형을 지정합니다. 부팅 유형에 대한 자세한 내용은 가상화 된 환경에서 UEFI, Secure Boot 및 TPM 이해를 참조하십시오. 유효한 값은 `Legacy`, `SecureBoot` 또는 `UEFI` 입니다. 기본값은 `Legacy` 입니다.

참고

OpenShift Container Platform 4.20에서 `레거시` 부팅 유형을 사용해야 합니다.

6. 컴퓨팅 머신에 적용할 하나 이상의 Nutanix Prism 카테고리를 지정합니다. 이 스탠자에는 Prism Central에 존재하는 카테고리 키-값 쌍에 대한 `key` 및 `value` 매개변수가 필요합니다. 카테고리에 대한 자세한 내용은 카테고리 관리를 참조하십시오.

7. Nutanix Prism Element 클러스터 구성을 지정합니다. 이 예에서 클러스터 유형은 `uuid` 이므로 `uuid` 스탠자가 있습니다.

8. 사용할 이미지를 지정합니다. 클러스터의 기존 기본 컴퓨팅 머신 세트의 이미지를 사용합니다.

9. Gi에 클러스터의 메모리 양을 지정합니다.

10. 클러스터에 사용하는 Nutanix 프로젝트를 지정합니다. 이 예에서 프로젝트 유형은 `name` 이므로 `name` 스탠자가 있습니다.

11. Prism Element 서브넷 오브젝트에 대해 하나 이상의 UUID를 지정합니다. 지정된 서브넷 중 하나에 대한 CIDR IP 주소 접두사에는 OpenShift Container Platform 클러스터가 사용하는 가상 IP 주소가 포함되어야 합니다. 클러스터의 각 Prism Element 장애 도메인에 대해 최대 32 서브넷이 지원됩니다. 모든 서브넷 UUID 값은 고유해야 합니다.

12. Gi에서 시스템 디스크 크기를 지정합니다.

13. `openshift-machine-api` 네임스페이스에 있는 사용자 데이터 YAML 파일에서 시크릿 이름을 지정합니다. 설치 프로그램이 기본 컴퓨팅 시스템 세트에 채우는 값을 사용합니다.

14. vCPU 소켓 수를 지정합니다.

15. 소켓당 vCPU 수를 지정합니다.

16. 사용자 워크로드가 인프라 노드에서 예약되지 않도록 테인트를 지정합니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

#### 8.1.1.7. RHOSP에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 RHOSP(Red Hat OpenStack Platform)에서 실행되는 컴퓨팅 머신 세트를 정의하고 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 생성합니다.

이 샘플에서 `<infrastructure_id>` 는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `<infra>` 는 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
    machine.openshift.io/cluster-api-machine-role: <infra>
    machine.openshift.io/cluster-api-machine-type: <infra>
  name: <infrastructure_id>-infra
  namespace: openshift-machine-api
spec:
  replicas: <number_of_replicas>
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <infra>
        machine.openshift.io/cluster-api-machine-type: <infra>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra
    spec:
      metadata:
        creationTimestamp: null
        labels:
          node-role.kubernetes.io/infra: ""
      taints:
      - key: node-role.kubernetes.io/infra
        effect: NoSchedule
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1alpha1
          cloudName: openstack
          cloudsSecret:
            name: openstack-cloud-credentials
            namespace: openshift-machine-api
          flavor: <nova_flavor>
          image: <glance_image_name_or_location>
          serverGroupID: <optional_UUID_of_server_group>
          kind: OpenstackProviderSpec
          networks:
          - filter: {}
            subnets:
            - filter:
                name: <subnet_name>
                tags: openshiftClusterID=<infrastructure_id>
          primarySubnet: <rhosp_subnet_UUID>
          securityGroups:
          - filter: {}
            name: <infrastructure_id>-worker
          serverMetadata:
            Name: <infrastructure_id>-worker
            openshiftClusterID: <infrastructure_id>
          tags:
          - openshiftClusterID=<infrastructure_id>
          trunk: true
          userDataSecret:
            name: worker-user-data
          availabilityZone: <optional_openstack_availability_zone>
```

1. 5

7. 14

16. 17

18. 19

클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 3

8. 9

20. `<infra>` 노드 레이블을 지정합니다.

4. 6

10. 인프라 ID 및 `<infra>` 노드 레이블을 지정합니다.

11. 사용자 워크로드가 인프라 노드에서 예약되지 않도록 테인트를 지정합니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

12. MachineSet의 서버 그룹 정책을 설정하려면, 서버 그룹 생성 에서 반환된 값을 입력합니다. 대부분의 배포에는 `anti-affinity` 또는 `soft-anti-affinity` 정책이 권장됩니다.

13. 여러 네트워크에 배포해야 합니다. 여러 네트워크에 배포하는 경우 이 목록에는 `primarySubnet` 값으로 사용되는 네트워크를 포함해야 합니다.

15. 노드 엔드포인트를 게시할 RHOSP 서브넷을 지정합니다. 일반적으로 이 서브넷은 `install-config.yaml` 파일에서 `machineSubnet` 값으로 사용되는 서브넷과 동일합니다.

#### 8.1.1.8. vSphere에서 컴퓨팅 머신 세트 사용자 정의 리소스의 샘플 YAML

이 샘플 YAML은 VMware vSphere에서 실행되는 컴퓨팅 머신 세트를 정의하고 `node-role.kubernetes.io/infra: ""` 로 레이블이 지정된 노드를 생성합니다.

이 샘플에서 < `infrastructure_id` >는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID 레이블이며 `infra` 는 추가할 노드 레이블입니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  creationTimestamp: null
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-infra
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra
  template:
    metadata:
      creationTimestamp: null
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: infra
        machine.openshift.io/cluster-api-machine-type: infra
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-infra
    spec:
      metadata:
        creationTimestamp: null
        labels:
          node-role.kubernetes.io/infra: ""
      providerSpec:
        value:
          apiVersion: machine.openshift.io/v1beta1
          credentialsSecret:
            name: vsphere-cloud-credentials
          dataDisks:
          - name: "<disk_name>"
            provisioningMode: "<mode>"
            sizeGiB: 20
          diskGiB: 120
          kind: VSphereMachineProviderSpec
          memoryMiB: 8192
          metadata:
            creationTimestamp: null
          network:
            devices:
            - networkName: "<vm_network_name>"
          numCPUs: 4
          numCoresPerSocket: 1
          snapshot: ""
          template: <vm_template_name>
          userDataSecret:
            name: worker-user-data
          workspace:
            datacenter: <vcenter_data_center_name>
            datastore: <vcenter_datastore_name>
            folder: <vcenter_vm_folder_path>
            resourcepool: <vsphere_resource_pool>
            server: <vcenter_server_ip>
      taints:
      - key: node-role.kubernetes.io/infra
        effect: NoSchedule
```

1. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다. OpenShift CLI () 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell
oc
```

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. 인프라 ID 및 인프라 `노드` 레이블을 지정합니다.

3. `infra` 노드 레이블을 지정합니다.

4. 하나 이상의 데이터 디스크 정의를 지정합니다. 자세한 내용은 "머신 세트를 사용하여 데이터 디스크 구성"을 참조하십시오.

5. 컴퓨팅 머신 세트를 배포할 vSphere VM 네트워크를 지정합니다. 이 VM 네트워크는 다른 컴퓨팅 시스템이 클러스터에 상주하는 위치여야 합니다.

6. 사용할 vSphere VM 템플릿 (예: `user-5ddjd-rhcos)` 을 지정합니다.

7. 컴퓨팅 머신 세트를 배포할 vCenter 데이터 센터를 지정합니다.

8. 컴퓨팅 머신 세트를 배포할 vCenter 데이터 저장소를 지정합니다.

9. vCenter의 vSphere VM 폴더에 경로(예: `/dc1/vm/user-inst-5ddjd`)를 지정합니다.

10. VM의 vSphere 리소스 풀을 지정합니다.

11. vCenter 서버 IP 또는 정규화된 도메인 이름을 지정합니다.

12. 사용자 워크로드가 인프라 노드에서 예약되지 않도록 테인트를 지정합니다.

참고

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드에서 실행 중인 기존 DNS Pod가 `misscheduled` 로 표시됩니다.

`misscheduled` DNS Pod에서 허용 오차를 삭제하거나 추가해야 합니다.

#### 8.1.2. 컴퓨팅 머신 세트 생성

설치 프로그램에서 생성한 컴퓨팅 머신 세트 외에도 고유한 머신 세트를 생성하여 선택한 특정 워크로드의 머신 컴퓨팅 리소스를 동적으로 관리할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인합니다.

```shell
oc
```

프로세스

컴퓨팅 머신 세트 CR(사용자 정의 리소스) 샘플이 포함된 새 YAML 파일을 만들고 `<file_name>.yaml` 이라는 이름을 지정합니다.

`<clusterID>` 및 `<role>` 매개 변수 값을 설정해야 합니다.

선택 사항: 특정 필드에 설정할 값이 확실하지 않은 경우 클러스터에서 기존 컴퓨팅 머신 세트를 확인할 수 있습니다.

클러스터의 컴퓨팅 머신 세트를 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinesets -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

특정 컴퓨팅 머신 세트 CR(사용자 정의 리소스)의 값을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get machineset <machineset_name> \
  -n openshift-machine-api -o yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: <infrastructure_id>
  name: <infrastructure_id>-<role>
  namespace: openshift-machine-api
spec:
  replicas: 1
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <infrastructure_id>
      machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
  template:
    metadata:
      labels:
        machine.openshift.io/cluster-api-cluster: <infrastructure_id>
        machine.openshift.io/cluster-api-machine-role: <role>
        machine.openshift.io/cluster-api-machine-type: <role>
        machine.openshift.io/cluster-api-machineset: <infrastructure_id>-<role>
    spec:
      providerSpec:
        ...
```

1. 클러스터 인프라 ID입니다.

2. 기본 노드 레이블입니다.

참고

사용자 프로비저닝 인프라가 있는 클러스터의 경우 컴퓨팅 머신 세트는 `worker` 및 `infra` 유형 머신만 생성할 수 있습니다.

3. 컴퓨팅 머신 세트 CR의 `<providerSpec>` 섹션에 있는 값은 플랫폼에 따라 다릅니다. CR의 `<providerSpec>` 매개변수에 대한 자세한 내용은 공급자의 샘플 컴퓨팅 머신 세트 CR 구성을 참조하십시오.

다음 명령을 실행하여 `MachineSet` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

검증

다음 명령을 실행하여 컴퓨팅 머신 세트 목록을 확인합니다.

```shell-session
$ oc get machineset -n openshift-machine-api
```

```shell-session
NAME                                DESIRED   CURRENT   READY   AVAILABLE   AGE
agl030519-vplxk-infra-us-east-1a    1         1         1       1           11m
agl030519-vplxk-worker-us-east-1a   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1b   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1c   1         1         1       1           55m
agl030519-vplxk-worker-us-east-1d   0         0                             55m
agl030519-vplxk-worker-us-east-1e   0         0                             55m
agl030519-vplxk-worker-us-east-1f   0         0                             55m
```

새 컴퓨팅 머신 세트를 사용할 수 있으면 `DESIRED` 및 `CURRENT` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

#### 8.1.3. 인프라 노드 생성

중요

설치 관리자 프로비저닝 인프라 환경 또는 머신 API에서 컨트롤 플레인 노드를 관리하는 클러스터의 인프라 머신 세트 생성을 참조하십시오.

클러스터의 요구 사항은 인프라(infra) 노드를 프로비저닝하도록 지정합니다. 설치 프로그램은 컨트롤 플레인 및 작업자 노드만 프로비저닝합니다. 작업자 노드는 레이블을 통해 인프라 노드로 지정할 수 있습니다. 그런 다음 테인트 및 허용 오차를 사용하여 적절한 워크로드를 인프라 노드로 이동할 수 있습니다. 자세한 내용은 "인프라 머신 세트에 리소스 전달"을 참조하십시오.

선택적으로 기본 클러스터 수준 노드 선택기를 생성할 수 있습니다. 기본 노드 선택기는 모든 네임스페이스에서 생성된 Pod에 적용되며 Pod의 기존 노드 선택기와 교차점을 생성하므로 Pod의 선택기가 추가로 제한됩니다.

중요

기본 노드 선택기 키가 Pod 라벨 키와 충돌하는 경우 기본 노드 선택기가 적용되지 않습니다.

그러나 Pod를 예약할 수 없게 만들 수 있는 기본 노드 선택기를 설정하지 마십시오. 예를 들어 Pod의 라벨이 `node-role.kubernetes.io/master=""` 와 같은 다른 노드 역할로 설정된 경우 기본 노드 선택기를 `node-role.kubernetes.io/infra=""` 와 같은 특정 노드 역할로 설정하면 Pod를 예약할 수 없게 될 수 있습니다. 따라서 기본 노드 선택기를 특정 노드 역할로 설정할 때 주의해야 합니다.

또는 프로젝트 노드 선택기를 사용하여 클러스터 수준 노드 선택기 키 충돌을 방지할 수 있습니다.

프로세스

인프라 노드 역할을 수행할 작업자 노드에 레이블을 추가합니다.

```shell-session
$ oc label node <node-name> node-role.kubernetes.io/infra=""
```

해당 노드에 `infra` 역할이 있는지 확인합니다.

```shell-session
$ oc get nodes
```

선택 사항: 기본 클러스터 수준 노드 선택기를 생성합니다.

`Scheduler` 오브젝트를 편집합니다.

```shell-session
$ oc edit scheduler cluster
```

적절한 노드 선택기를 사용하여 `defaultNodeSelector` 필드를 추가합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  name: cluster
spec:
  defaultNodeSelector: node-role.kubernetes.io/infra=""
# ...
```

1. 이 예제 노드 선택기는 기본적으로 인프라 노드에 Pod를 배포합니다.

파일을 저장하여 변경 사항을 적용합니다.

이제 인프라 리소스를 새 인프라 노드로 이동할 수 있습니다. 또한 원하지 않거나 속하지 않는 워크로드를 새 인프라 노드에서 제거합니다. "OpenShift Container Platform 인프라 구성 요소"의 인프라 노드에서 사용할 수 있도록 지원되는 워크로드 목록을 참조하십시오.

추가 리소스

인프라 머신 세트로 리소스 이동

#### 8.1.4. 인프라 머신의 머신 구성 풀 생성

전용 구성을 위한 인프라 머신이 필요한 경우 인프라 풀을 생성해야 합니다.

중요

사용자 지정 머신 구성 풀을 생성하면 동일한 파일 또는 장치를 참조하는 경우 기본 작업자 풀 구성이 재정의됩니다.

프로세스

특정 레이블이 있는 인프라 노드로 할당하려는 노드에 레이블을 추가합니다.

```shell-session
$ oc label node <node_name> <label>
```

```shell-session
$ oc label node ci-ln-n8mqwr2-f76d1-xscn2-worker-c-6fmtx node-role.kubernetes.io/infra=
```

작업자 역할과 사용자 지정 역할을 모두 포함하는 머신 구성 풀을 머신 구성 선택기로 생성합니다.

```shell-session
$ cat infra.mcp.yaml
```

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  name: infra
spec:
  machineConfigSelector:
    matchExpressions:
      - {key: machineconfiguration.openshift.io/role, operator: In, values: [worker,infra]}
  nodeSelector:
    matchLabels:
      node-role.kubernetes.io/infra: ""
```

1. 작업자 역할 및 사용자 지정 역할을 추가합니다.

2. 노드에 추가한 레이블을 `nodeSelector` 로 추가합니다.

참고

사용자 지정 머신 구성 풀은 작업자 풀의 머신 구성을 상속합니다. 사용자 지정 풀은 작업자 풀을 대상으로 하는 머신 구성을 사용하지만 사용자 지정 풀을 대상으로 하는 변경 사항만 배포할 수 있는 기능을 추가합니다. 사용자 지정 풀은 작업자 풀에서 리소스를 상속하므로 작업자 풀을 변경하면 사용자 지정 풀에도 영향을 줍니다.

YAML 파일이 있으면 머신 구성 풀을 생성할 수 있습니다.

```shell-session
$ oc create -f infra.mcp.yaml
```

머신 구성을 확인하고 인프라 구성이 성공적으로 렌더링되었는지 확인합니다.

```shell-session
$ oc get machineconfig
```

```shell-session
NAME                                                        GENERATEDBYCONTROLLER                      IGNITIONVERSION   CREATED
00-master                                                   365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
00-worker                                                   365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
01-master-container-runtime                                 365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
01-master-kubelet                                           365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
01-worker-container-runtime                                 365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
01-worker-kubelet                                           365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
99-master-1ae2a1e0-a115-11e9-8f14-005056899d54-registries   365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
99-master-ssh                                                                                          3.2.0             31d
99-worker-1ae64748-a115-11e9-8f14-005056899d54-registries   365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             31d
99-worker-ssh                                                                                          3.2.0             31d
rendered-infra-4e48906dca84ee702959c71a53ee80e7             365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             23m
rendered-master-072d4b2da7f88162636902b074e9e28e            5b6fb8349a29735e48446d435962dec4547d3090   3.5.0             31d
rendered-master-3e88ec72aed3886dec061df60d16d1af            02c07496ba0417b3e12b78fb32baf6293d314f79   3.5.0             31d
rendered-master-419bee7de96134963a15fdf9dd473b25            365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             17d
rendered-master-53f5c91c7661708adce18739cc0f40fb            365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             13d
rendered-master-a6a357ec18e5bce7f5ac426fc7c5ffcd            365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             7d3h
rendered-master-dc7f874ec77fc4b969674204332da037            5b6fb8349a29735e48446d435962dec4547d3090   3.5.0             31d
rendered-worker-1a75960c52ad18ff5dfa6674eb7e533d            5b6fb8349a29735e48446d435962dec4547d3090   3.5.0             31d
rendered-worker-2640531be11ba43c61d72e82dc634ce6            5b6fb8349a29735e48446d435962dec4547d3090   3.5.0             31d
rendered-worker-4e48906dca84ee702959c71a53ee80e7            365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             7d3h
rendered-worker-4f110718fe88e5f349987854a1147755            365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             17d
rendered-worker-afc758e194d6188677eb837842d3b379            02c07496ba0417b3e12b78fb32baf6293d314f79   3.5.0             31d
rendered-worker-daa08cc1e8f5fcdeba24de60cd955cc3            365c1cfd14de5b0e3b85e0fc815b0060f36ab955   3.5.0             13d
```

`rendered-infra-*` 접두사가 있는 새 머신 구성이 표시되어야 합니다.

선택 사항: 사용자 지정 풀에 변경 사항을 배포하려면 `infra` 와 같은 사용자 지정 풀 이름을 레이블로 사용하는 머신 구성을 생성합니다. 필수 사항은 아니며 지침 용도로만 표시됩니다. 이렇게 하면 인프라 노드에 고유한 사용자 지정 구성을 적용할 수 있습니다.

참고

새 머신 구성 풀을 생성한 후 MCO는 해당 풀에 대해 새로 렌더링된 구성과 해당 풀의 관련 노드를 다시 부팅하여 새 구성을 적용합니다.

머신 구성을 생성합니다.

```shell-session
$ cat infra.mc.yaml
```

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  name: 51-infra
  labels:
    machineconfiguration.openshift.io/role: infra
spec:
  config:
    ignition:
      version: 3.5.0
    storage:
      files:
      - path: /etc/infratest
        mode: 0644
        contents:
          source: data:,infra
```

1. 노드에 추가한 레이블을 `nodeSelector` 로 추가합니다.

머신 구성을 인프라 레이블 노드에 적용합니다.

```shell-session
$ oc create -f infra.mc.yaml
```

새 머신 구성 풀을 사용할 수 있는지 확인합니다.

```shell-session
$ oc get mcp
```

```shell-session
NAME     CONFIG                                             UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
infra    rendered-infra-60e35c2e99f42d976e084fa94da4d0fc    True      False      False      1              1                   1                     0                      4m20s
master   rendered-master-9360fdb895d4c131c7c4bebbae099c90   True      False      False      3              3                   3                     0                      91m
worker   rendered-worker-60e35c2e99f42d976e084fa94da4d0fc   True      False      False      2              2                   2                     0                      91m
```

이 예에서는 작업자 노드가 인프라 노드로 변경되었습니다.

추가 리소스

머신 구성 풀을 사용한 노드 구성 관리.

### 8.2. 인프라 노드에 머신 세트 리소스 할당

인프라 머신 세트를 생성 한 후 `worker` 및 `infra` 역할이 새 인프라 노드에 적용됩니다. `infra` 역할이 적용된 노드는 `worker` 역할이 적용된 경우에도 환경을 실행하는 데 필요한 총 서브스크립션 수에 포함되지 않습니다.

그러나 인프라 노드가 작업자로 할당되면 사용자 워크로드가 실수로 인프라 노드에 할당될 수 있습니다. 이를 방지하려면 제어하려는 pod에 대한 허용 오차를 적용하고 인프라 노드에 테인트를 적용할 수 있습니다.

#### 8.2.1. 테인트 및 허용 오차를 사용하여 인프라 노드 워크로드 바인딩

`infra` 및 `worker` 역할이 할당된 인프라 노드가 있는 경우 사용자 워크로드가 할당되지 않도록 노드를 구성해야 합니다.

중요

인프라 노드에 대해 생성된 이중 `infra,worker` 레이블을 유지하고 테인트 및 허용 오차를 사용하여 사용자 워크로드가 예약된 노드를 관리하는 것이 좋습니다. 노드에서 `worker` 레이블을 제거하는 경우 이를 관리할 사용자 지정 풀을 생성해야 합니다. `master` 또는 `worker` 이외의 레이블이 있는 노드는 사용자 지정 풀없이 MCO에서 인식되지 않습니다. `worker` 레이블을 유지 관리하면 사용자 정의 레이블을 선택하는 사용자 정의 풀이 없는 경우 기본 작업자 머신 구성 풀에서 노드를 관리할 수 있습니다. `infra` 레이블은 총 서브스크립션 수에 포함되지 않는 클러스터와 통신합니다.

사전 요구 사항

OpenShift Container Platform 클러스터에서 추가 `MachineSet` 개체를 구성합니다.

프로세스

인프라 노드에 테인트를 추가하여 사용자 워크로드를 예약하지 않도록 합니다.

노드에 테인트가 있는지 확인합니다.

```shell-session
$ oc describe nodes <node_name>
```

```plaintext
oc describe node ci-ln-iyhx092-f76d1-nvdfm-worker-b-wln2l
Name:               ci-ln-iyhx092-f76d1-nvdfm-worker-b-wln2l
Roles:              worker
 ...
Taints:             node-role.kubernetes.io/infra=reserved:NoSchedule
 ...
```

이 예에서는 노드에 테인트가 있음을 보여줍니다. 다음 단계에서 Pod에 허용 오차를 추가할 수 있습니다.

사용자 워크로드를 예약하지 않도록 테인트를 구성하지 않은 경우 다음을 수행합니다.

```shell-session
$ oc adm taint nodes <node_name> <key>=<value>:<effect>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc adm taint nodes node1 node-role.kubernetes.io/infra=reserved:NoSchedule
```

작은 정보

또는 Pod 사양을 편집하여 테인트를 추가할 수 있습니다.

```yaml
apiVersion: v1
kind: Node
metadata:
  name: node1
# ...
spec:
  taints:
    - key: node-role.kubernetes.io/infra
      value: reserved
      effect: NoSchedule
# ...
```

이 예에서는 `node-role.kubernetes.io/infra` 키와 `NoSchedule` 테인트 효과가 있는 `node1` 에 taint를 배치합니다. `NoSchedule` 효과가 있는 노드는 taint를 허용하는 pod만 예약하지만 기존 pod는 노드에서 예약된 상태를 유지할 수 있습니다.

인프라 노드에 `NoSchedule` 테인트를 추가하면 해당 노드의 데몬 세트에 의해 제어되는 모든 Pod가 `잘못 예약` 됨으로 표시됩니다. Red Hat 지식베이스 솔루션에

`잘못 예약` DNS Pod에 허용 오차를 추가하여 Pod에 Pod를 삭제하거나 Pod에 허용 오차를 추가해야 합니다. Operator가 관리하는 데몬 세트 오브젝트에 허용 오차를 추가할 수 없습니다.

참고

descheduler를 사용하면 노드 taint를 위반하는 pod가 클러스터에서 제거될 수 있습니다.

라우터, 레지스트리, 모니터링 워크로드와 같이 인프라 노드에서 예약할 Pod에 허용 오차를 추가합니다. 이전 예제를 참조하여 `Pod` 오브젝트 사양에 다음 허용 오차를 추가합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:

# ...
spec:
# ...
  tolerations:
    - key: node-role.kubernetes.io/infra
      value: reserved
      effect: NoSchedule
      operator: Equal
```

1. 노드에 추가한 키를 지정합니다.

2. 노드에 추가한 키-값 쌍 taint의 값을 지정합니다.

3. 노드에 추가한 효과를 지정합니다.

4. 노드에 `node-role.kubernetes.io/infra` 키가 있는 테인트를 요구하도록 `Equal` Operator를 지정합니다.

이 허용 오차는 아래 명령으로 생성된 taint와 일치합니다. 이 허용 오차가 있는 Pod를 인프라 노드에 예약할 수 있습니다.

```shell
oc adm taint
```

참고

OLM을 통해 설치된 Operator의 Pod를 인프라 노드로 이동하는 것은 항상 가능한 것은 아닙니다. Operator pod를 이동하는 기능은 각 Operator의 구성에 따라 다릅니다.

스케줄러를 사용하여 인프라 노드에 Pod를 예약합니다. 자세한 내용은 " scheduler를 사용하여 Pod 배치 제어"에 대한 설명서를 참조하십시오.

새 인프라 노드에서 원하지 않거나 속하지 않는 워크로드를 제거합니다. "OpenShift Container Platform 인프라 구성 요소"의 인프라 노드에서 사용할 수 있도록 지원되는 워크로드 목록을 참조하십시오.

추가 리소스

스케줄러를 사용하여 Pod 배치 제어

인프라 머신 세트로 리소스 이동.

테인트 및 허용 오차 이해

### 8.3. 인프라 머신 세트로 리소스 이동

일부 인프라 리소스는 기본적으로 클러스터에 배포됩니다. 다음과 같이 인프라 노드 선택기를 추가하여 생성한 인프라 머신 세트로 이동할 수 있습니다.

```yaml
apiVersion: imageregistry.operator.openshift.io/v1
kind: Config
metadata:
  name: cluster
# ...
spec:
  nodePlacement:
    nodeSelector:
      matchLabels:
        node-role.kubernetes.io/infra: ""
    tolerations:
    - effect: NoSchedule
      key: node-role.kubernetes.io/infra
      value: reserved
    - effect: NoExecute
      key: node-role.kubernetes.io/infra
      value: reserved
```

1. 적절한 값이 설정된 `nodeSelector` 매개변수를 이동하려는 구성 요소에 추가합니다. 표시된 형식으로 `nodeSelector` 를 사용하거나 노드에 지정된 값에 따라 쌍을 사용할 수 있습니다. infrasructure 노드에 테인트를 추가한 경우 일치하는 톨러레이션도 추가합니다.

```shell
<key>: <value>
```

모든 인프라 구성 요소에 특정 노드 선택기를 적용하면 OpenShift Container Platform에서 해당 라벨이 있는 노드에 해당 워크로드를 예약합니다.

#### 8.3.1. 라우터 이동

라우터 Pod를 다른 컴퓨팅 머신 세트에 배포할 수 있습니다. 기본적으로 Pod는 작업자 노드에 배포됩니다.

사전 요구 사항

OpenShift Container Platform 클러스터에서 추가 컴퓨팅 머신 세트를 구성합니다.

프로세스

라우터 Operator의 `IngressController` 사용자 정의 리소스를 표시합니다.

```shell-session
$ oc get ingresscontroller default -n openshift-ingress-operator -o yaml
```

명령 출력은 다음 예제와 유사합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  creationTimestamp: 2019-04-18T12:35:39Z
  finalizers:
  - ingresscontroller.operator.openshift.io/finalizer-ingresscontroller
  generation: 1
  name: default
  namespace: openshift-ingress-operator
  resourceVersion: "11341"
  selfLink: /apis/operator.openshift.io/v1/namespaces/openshift-ingress-operator/ingresscontrollers/default
  uid: 79509e05-61d6-11e9-bc55-02ce4781844a
spec: {}
status:
  availableReplicas: 2
  conditions:
  - lastTransitionTime: 2019-04-18T12:36:15Z
    status: "True"
    type: Available
  domain: apps.<cluster>.example.com
  endpointPublishingStrategy:
    type: LoadBalancerService
  selector: ingresscontroller.operator.openshift.io/deployment-ingresscontroller=default
```

`ingresscontroller` 리소스를 편집하고 `infra` 레이블을 사용하도록 `nodeSelector` 를 변경합니다.

```shell-session
$ oc edit ingresscontroller default -n openshift-ingress-operator
```

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  creationTimestamp: "2025-03-26T21:15:43Z"
  finalizers:
  - ingresscontroller.operator.openshift.io/finalizer-ingresscontroller
  generation: 1
  name: default
# ...
spec:
  nodePlacement:
    nodeSelector:
      matchLabels:
        node-role.kubernetes.io/infra: ""
    tolerations:
    - effect: NoSchedule
      key: node-role.kubernetes.io/infra
      value: reserved
# ...
```

1. 적절한 값이 설정된 `nodeSelector` 매개변수를 이동하려는 구성 요소에 추가합니다. 표시된 형식으로 `nodeSelector` 매개변수를 사용하거나 노드에 지정된 값에 따라 쌍을 사용할 수 있습니다. 인프라 노드에 테인트를 추가한 경우 일치하는 허용 오차도 추가합니다.

```shell
<key>: <value>
```

라우터 pod가 `infra` 노드에서 실행되고 있는지 확인합니다.

라우터 pod 목록을 표시하고 실행중인 pod의 노드 이름을 기록해 둡니다.

```shell-session
$ oc get pod -n openshift-ingress -o wide
```

```shell-session
NAME                              READY     STATUS        RESTARTS   AGE       IP           NODE                           NOMINATED NODE   READINESS GATES
router-default-86798b4b5d-bdlvd   1/1      Running       0          28s       10.130.2.4   ip-10-0-217-226.ec2.internal   <none>           <none>
router-default-955d875f4-255g8    0/1      Terminating   0          19h       10.129.2.4   ip-10-0-148-172.ec2.internal   <none>           <none>
```

이 예에서 실행중인 pod는 `ip-10-0-217-226.ec2.internal` 노드에 있습니다.

실행중인 pod의 노드 상태를 표시합니다.

```shell-session
$ oc get node <node_name>
```

1. pod 목록에서 얻은 `<node_name>` 을 지정합니다.

```shell-session
NAME                          STATUS  ROLES         AGE   VERSION
ip-10-0-217-226.ec2.internal  Ready   infra,worker  17h   v1.33.4
```

역할 목록에 `infra` 가 포함되어 있으므로 pod가 올바른 노드에서 실행됩니다.

#### 8.3.2. 기본 레지스트리 이동

Pod를 다른 노드에 배포하도록 레지스트리 Operator를 구성합니다.

사전 요구 사항

OpenShift Container Platform 클러스터에서 추가 컴퓨팅 머신 세트를 구성합니다.

프로세스

`config/instance` 개체를 표시합니다.

```shell-session
$ oc get configs.imageregistry.operator.openshift.io/cluster -o yaml
```

```yaml
apiVersion: imageregistry.operator.openshift.io/v1
kind: Config
metadata:
  creationTimestamp: 2019-02-05T13:52:05Z
  finalizers:
  - imageregistry.operator.openshift.io/finalizer
  generation: 1
  name: cluster
  resourceVersion: "56174"
  selfLink: /apis/imageregistry.operator.openshift.io/v1/configs/cluster
  uid: 36fd3724-294d-11e9-a524-12ffeee2931b
spec:
  httpSecret: d9a012ccd117b1e6616ceccb2c3bb66a5fed1b5e481623
  logging: 2
  managementState: Managed
  proxy: {}
  replicas: 1
  requests:
    read: {}
    write: {}
  storage:
    s3:
      bucket: image-registry-us-east-1-c92e88cad85b48ec8b312344dff03c82-392c
      region: us-east-1
status:
...
```

`config/instance` 개체를 편집합니다.

```shell-session
$ oc edit configs.imageregistry.operator.openshift.io/cluster
```

```yaml
apiVersion: imageregistry.operator.openshift.io/v1
kind: Config
metadata:
  name: cluster
# ...
spec:
  logLevel: Normal
  managementState: Managed
  nodeSelector:
    node-role.kubernetes.io/infra: ""
  tolerations:
  - effect: NoSchedule
    key: node-role.kubernetes.io/infra
    value: reserved
```

1. 적절한 값이 설정된 `nodeSelector` 매개변수를 이동하려는 구성 요소에 추가합니다. 표시된 형식으로 `nodeSelector` 매개변수를 사용하거나 노드에 지정된 값에 따라 쌍을 사용할 수 있습니다. infrasructure 노드에 테인트를 추가한 경우 일치하는 톨러레이션도 추가합니다.

```shell
<key>: <value>
```

레지스트리 pod가 인프라 노드로 이동되었는지 검증합니다.

다음 명령을 실행하여 레지스트리 pod가 있는 노드를 식별합니다.

```shell-session
$ oc get pods -o wide -n openshift-image-registry
```

노드에 지정된 레이블이 있는지 확인합니다.

```shell-session
$ oc describe node <node_name>
```

명령 출력을 확인하고 `node-role.kubernetes.io/infra` 가 `LABELS` 목록에 있는지 확인합니다.

#### 8.3.3. 모니터링 솔루션 이동

모니터링 스택에는 Prometheus, Thanos Querier 및 Alertmanager를 포함한 여러 구성 요소가 포함됩니다. Cluster Monitoring Operator는 이 스택을 관리합니다. 모니터링 스택을 인프라 노드에 재배포하려면 사용자 정의 구성 맵을 생성하고 적용할 수 있습니다.

사전 요구 사항

`cluster-admin` 클러스터 역할의 사용자로 클러스터에 액세스할 수 있습니다.

`cluster-monitoring-config`

`ConfigMap` 오브젝트를 생성하셨습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

`cluster-monitoring-config` 구성 맵을 편집하고 `infra` 레이블을 사용하도록 `nodeSelector` 를 변경합니다.

```shell-session
$ oc edit configmap cluster-monitoring-config -n openshift-monitoring
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |+
    alertmanagerMain:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    prometheusK8s:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    prometheusOperator:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    metricsServer:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    kubeStateMetrics:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    telemeterClient:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    openshiftStateMetrics:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    thanosQuerier:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
    monitoringPlugin:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: node-role.kubernetes.io/infra
        value: reserved
        effect: NoSchedule
```

1. 적절한 값이 설정된 `nodeSelector` 매개변수를 이동하려는 구성 요소에 추가합니다. 표시된 형식으로 `nodeSelector` 매개변수를 사용하거나 노드에 지정된 값에 따라 쌍을 사용할 수 있습니다. 인프라 노드에 테인트를 추가한 경우 일치하는 허용 오차도 추가합니다.

```shell
<key>: <value>
```

모니터링 pod가 새 머신으로 이동하는 것을 확인합니다.

```shell-session
$ watch 'oc get pod -n openshift-monitoring -o wide'
```

구성 요소가 `infra` 노드로 이동하지 않은 경우 이 구성 요소가 있는 pod를 제거합니다.

```shell-session
$ oc delete pod -n openshift-monitoring <pod>
```

삭제된 pod의 구성 요소가 `infra` 노드에 다시 생성됩니다.

#### 8.3.4. Vertical Pod Autoscaler Operator 구성 요소 이동

VPA(Vertical Pod Autoscaler Operator)는 권장 사항, 업데이트 관리자 및 승인 컨트롤러의 세 가지 구성 요소로 구성됩니다. Operator 및 각 구성 요소에는 컨트롤 플레인 노드의 VPA 네임스페이스에 자체 Pod가 있습니다. VPA 서브스크립션 및 `VerticalPodAutoscalerController` CR에 노드 선택기를 추가하여 VPA Operator 및 구성 요소 Pod를 인프라 노드로 이동할 수 있습니다.

다음 예제에서는 컨트롤 플레인 노드에 VPA Pod의 기본 배포를 보여줍니다.

```shell-session
NAME                                                READY   STATUS    RESTARTS   AGE     IP            NODE                  NOMINATED NODE   READINESS GATES
vertical-pod-autoscaler-operator-6c75fcc9cd-5pb6z   1/1     Running   0          7m59s   10.128.2.24   c416-tfsbj-master-1   <none>           <none>
vpa-admission-plugin-default-6cb78d6f8b-rpcrj       1/1     Running   0          5m37s   10.129.2.22   c416-tfsbj-master-1   <none>           <none>
vpa-recommender-default-66846bd94c-dsmpp            1/1     Running   0          5m37s   10.129.2.20   c416-tfsbj-master-0   <none>           <none>
vpa-updater-default-db8b58df-2nkvf                  1/1     Running   0          5m37s   10.129.2.21   c416-tfsbj-master-1   <none>           <none>
```

프로세스

VPA Operator의 `Subscription` CR(사용자 정의 리소스)에 노드 선택기를 추가하여 VPA Operator Pod를 이동합니다.

```shell-session
$ oc edit Subscription vertical-pod-autoscaler -n openshift-vertical-pod-autoscaler
```

인프라 노드의 노드 역할 레이블과 일치하도록 노드 선택기를 추가합니다.

```shell-session
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  labels:
    operators.coreos.com/vertical-pod-autoscaler.openshift-vertical-pod-autoscaler: ""
  name: vertical-pod-autoscaler
# ...
spec:
  config:
    nodeSelector:
      node-role.kubernetes.io/infra: ""
```

1. 인프라 노드의 노드 역할을 지정합니다.

참고

인프라 노드에서 taint를 사용하는 경우 `서브스크립션` CR에 허용 오차를 추가해야 합니다.

예를 들면 다음과 같습니다.

```shell-session
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  labels:
    operators.coreos.com/vertical-pod-autoscaler.openshift-vertical-pod-autoscaler: ""
  name: vertical-pod-autoscaler
# ...
spec:
  config:
    nodeSelector:
      node-role.kubernetes.io/infra: ""
    tolerations:
    - key: "node-role.kubernetes.io/infra"
      operator: "Exists"
      effect: "NoSchedule"
```

1. 인프라 노드의 테인트에 대한 허용 오차를 지정합니다.

`VerticalPodAutoscaler` CR(사용자 정의 리소스)에 노드 선택기를 추가하여 각 VPA 구성 요소를 이동합니다.

```shell-session
$ oc edit VerticalPodAutoscalerController default -n openshift-vertical-pod-autoscaler
```

인프라 노드의 노드 역할 레이블과 일치하도록 노드 선택기를 추가합니다.

```shell-session
apiVersion: autoscaling.openshift.io/v1
kind: VerticalPodAutoscalerController
metadata:
  name: default
  namespace: openshift-vertical-pod-autoscaler
# ...
spec:
  deploymentOverrides:
    admission:
      container:
        resources: {}
      nodeSelector:
        node-role.kubernetes.io/infra: ""
    recommender:
      container:
        resources: {}
      nodeSelector:
        node-role.kubernetes.io/infra: ""
    updater:
      container:
        resources: {}
      nodeSelector:
        node-role.kubernetes.io/infra: ""
```

1. 선택 사항: VPA 승인 Pod의 노드 역할을 지정합니다.

2. 선택 사항: VPA recommender Pod의 노드 역할을 지정합니다.

3. 선택 사항: VPA 업데이트 프로그램 Pod의 노드 역할을 지정합니다.

참고

대상 노드에서 테인트를 사용하는 경우 `VerticalPodAutoscalerController` CR에 허용 오차를 추가해야 합니다.

예를 들면 다음과 같습니다.

```shell-session
apiVersion: autoscaling.openshift.io/v1
kind: VerticalPodAutoscalerController
metadata:
  name: default
  namespace: openshift-vertical-pod-autoscaler
# ...
spec:
  deploymentOverrides:
    admission:
      container:
        resources: {}
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: "my-example-node-taint-key"
        operator: "Exists"
        effect: "NoSchedule"
    recommender:
      container:
        resources: {}
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: "my-example-node-taint-key"
        operator: "Exists"
        effect: "NoSchedule"
    updater:
      container:
        resources: {}
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      tolerations:
      - key: "my-example-node-taint-key"
        operator: "Exists"
        effect: "NoSchedule"
```

1. 인프라 노드의 테인트에 대한 허용 오차를 지정합니다.

2. 인프라 노드의 테인트에 대한 권장 Pod에 대한 허용 오차를 지정합니다.

3. 인프라 노드의 테인트에 대한 업데이트 프로그램 Pod에 대한 허용 오차를 지정합니다.

검증

다음 명령을 사용하여 Pod가 이동했는지 확인할 수 있습니다.

```shell-session
$ oc get pods -n openshift-vertical-pod-autoscaler -o wide
```

Pod는 더 이상 컨트롤 플레인 노드에 배포되지 않습니다. 다음 예제 출력에서 노드는 이제 컨트롤 플레인 노드가 아닌 인프라 노드입니다.

```shell-session
NAME                                                READY   STATUS    RESTARTS   AGE     IP            NODE                              NOMINATED NODE   READINESS GATES
vertical-pod-autoscaler-operator-6c75fcc9cd-5pb6z   1/1     Running   0          7m59s   10.128.2.24   c416-tfsbj-infra-eastus3-2bndt   <none>           <none>
vpa-admission-plugin-default-6cb78d6f8b-rpcrj       1/1     Running   0          5m37s   10.129.2.22   c416-tfsbj-infra-eastus1-lrgj8   <none>           <none>
vpa-recommender-default-66846bd94c-dsmpp            1/1     Running   0          5m37s   10.129.2.20   c416-tfsbj-infra-eastus1-lrgj8   <none>           <none>
vpa-updater-default-db8b58df-2nkvf                  1/1     Running   0          5m37s   10.129.2.21   c416-tfsbj-infra-eastus1-lrgj8   <none>           <none>
```

#### 8.3.5. Cluster Resource Override Operator Pod 이동

기본적으로 Cluster Resource Override Operator 설치 프로세스는 `clusterresourceoverride-operator` 네임스페이스의 노드에서 Operator Pod 및 Cluster Resource Override Pod를 생성합니다. 필요에 따라 이러한 Pod를 인프라 노드와 같은 다른 노드로 이동할 수 있습니다.

다음 예제에서는 Cluster Resource Override Pod가 컨트롤 플레인 노드에 배포되고 Cluster Resource Override Operator Pod가 작업자 노드에 배포됩니다.

```shell-session
NAME                                                READY   STATUS    RESTARTS   AGE   IP            NODE                                        NOMINATED NODE   READINESS GATES
clusterresourceoverride-786b8c898c-9wrdq            1/1     Running   0          23s   10.128.2.32   ip-10-0-14-183.us-west-2.compute.internal   <none>           <none>
clusterresourceoverride-786b8c898c-vn2lf            1/1     Running   0          26s   10.130.2.10   ip-10-0-20-140.us-west-2.compute.internal   <none>           <none>
clusterresourceoverride-operator-6b8b8b656b-lvr62   1/1     Running   0          56m   10.131.0.33   ip-10-0-2-39.us-west-2.compute.internal     <none>           <none>
```

```shell-session
NAME                                        STATUS   ROLES                  AGE   VERSION
ip-10-0-14-183.us-west-2.compute.internal   Ready    control-plane,master   65m   v1.33.4
ip-10-0-2-39.us-west-2.compute.internal     Ready    worker                 58m   v1.33.4
ip-10-0-20-140.us-west-2.compute.internal   Ready    control-plane,master   65m   v1.33.4
ip-10-0-23-244.us-west-2.compute.internal   Ready    infra                  55m   v1.33.4
ip-10-0-77-153.us-west-2.compute.internal   Ready    control-plane,master   65m   v1.33.4
ip-10-0-99-108.us-west-2.compute.internal   Ready    worker                 24m   v1.33.4
ip-10-0-24-233.us-west-2.compute.internal   Ready    infra                  55m   v1.33.4
ip-10-0-88-109.us-west-2.compute.internal   Ready    worker                 24m   v1.33.4
ip-10-0-67-453.us-west-2.compute.internal   Ready    infra                  55m   v1.33.4
```

프로세스

Cluster Resource Override Operator의 `Subscription` CR(사용자 정의 리소스)에 노드 선택기를 추가하여 Cluster Resource Override Operator를 이동합니다.

```shell-session
$ oc edit -n clusterresourceoverride-operator subscriptions.operators.coreos.com clusterresourceoverride
```

Cluster Resource Override Operator Pod를 설치하려는 노드의 노드 역할 레이블과 일치하도록 노드 선택기를 추가합니다.

```shell-session
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: clusterresourceoverride
  namespace: clusterresourceoverride-operator
# ...
spec:
  config:
    nodeSelector:
      node-role.kubernetes.io/infra: ""
# ...
```

1. Cluster Resource Override Operator Pod를 배포할 노드의 역할을 지정합니다.

참고

인프라 노드에서 taint를 사용하는 경우 `서브스크립션` CR에 허용 오차를 추가해야 합니다.

예를 들면 다음과 같습니다.

```shell-session
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: clusterresourceoverride
  namespace: clusterresourceoverride-operator
# ...
spec:
  config:
    nodeSelector:
      node-role.kubernetes.io/infra: ""
    tolerations:
    - key: "node-role.kubernetes.io/infra"
      operator: "Exists"
      effect: "NoSchedule"
```

1. 인프라 노드의 테인트에 대한 허용 오차를 지정합니다.

`ClusterResourceOverride` 사용자 정의 리소스(CR)에 노드 선택기를 추가하여 Cluster Resource Override Pod를 이동합니다.

```shell-session
$ oc edit ClusterResourceOverride cluster -n clusterresourceoverride-operator
```

인프라 노드의 노드 역할 레이블과 일치하도록 노드 선택기를 추가합니다.

```shell-session
apiVersion: operator.autoscaling.openshift.io/v1
kind: ClusterResourceOverride
metadata:
  name: cluster
  resourceVersion: "37952"
spec:
  podResourceOverride:
    spec:
      cpuRequestToLimitPercent: 25
      limitCPUToMemoryPercent: 200
      memoryRequestToLimitPercent: 50
  deploymentOverrides:
    replicas: 1
    nodeSelector:
      node-role.kubernetes.io/infra: ""
# ...
```

1. 선택 사항: 배포할 클러스터 리소스 덮어쓰기 Pod 수를 지정합니다. 기본값은 `2` 입니다. 노드당 하나의 Pod만 허용됩니다.

2. 선택 사항: Cluster Resource Override Pod를 배포할 노드의 역할을 지정합니다.

참고

인프라 노드에서 taint를 사용하는 경우 `ClusterResourceOverride` CR에 허용 오차를 추가해야 합니다.

예를 들면 다음과 같습니다.

```shell-session
apiVersion: operator.autoscaling.openshift.io/v1
kind: ClusterResourceOverride
metadata:
  name: cluster
# ...
spec:
  podResourceOverride:
    spec:
      memoryRequestToLimitPercent: 50
      cpuRequestToLimitPercent: 25
      limitCPUToMemoryPercent: 200
  deploymentOverrides:
    replicas: 3
    nodeSelector:
      node-role.kubernetes.io/worker: ""
    tolerations:
    - key: "key"
      operator: "Equal"
      value: "value"
      effect: "NoSchedule"
```

1. 인프라 노드의 테인트에 대한 허용 오차를 지정합니다.

검증

다음 명령을 사용하여 Pod가 이동했는지 확인할 수 있습니다.

```shell-session
$ oc get pods -n clusterresourceoverride-operator -o wide
```

이제 Cluster Resource Override Pod가 인프라 노드에 배포됩니다.

```shell-session
NAME                                                READY   STATUS    RESTARTS   AGE   IP            NODE                                        NOMINATED NODE   READINESS GATES
clusterresourceoverride-786b8c898c-9wrdq            1/1     Running   0          23s   10.127.2.25   ip-10-0-23-244.us-west-2.compute.internal   <none>           <none>
clusterresourceoverride-786b8c898c-vn2lf            1/1     Running   0          26s   10.128.0.80   ip-10-0-24-233.us-west-2.compute.internal   <none>           <none>
clusterresourceoverride-operator-6b8b8b656b-lvr62   1/1     Running   0          56m   10.129.0.71   ip-10-0-67-453.us-west-2.compute.internal   <none>           <none>
```

추가 리소스

다른 노드로 모니터링 구성 요소 이동

### 9.1. 사용자 프로비저닝 인프라가 있는 클러스터에 수동으로 컴퓨팅 머신 추가

설치 프로세스의 일부 또는 설치 후 사용자 프로비저닝 인프라의 클러스터에 컴퓨팅 머신을 추가할 수 있습니다. 설치 후 프로세스에는 설치 중에 사용된 것과 동일한 구성 파일과 매개 변수 중 일부가 필요합니다.

#### 9.1.1. Amazon Web Services에 컴퓨팅 머신 추가

AWS(Amazon Web Services)의 OpenShift Container Platform 클러스터에 컴퓨팅 머신을 추가하려면 CloudFormation 템플릿을 사용하여 AWS에 컴퓨팅 머신 추가 를 참조하십시오.

#### 9.1.2. Microsoft Azure에 컴퓨팅 머신 추가

Microsoft Azure의 OpenShift Container Platform 클러스터에 컴퓨팅 머신을 추가하려면 Azure에서 추가 작업자 머신 생성 을 참조하십시오.

#### 9.1.3. Azure Stack Hub에 컴퓨팅 머신 추가

Azure Stack Hub의 OpenShift Container Platform 클러스터에 컴퓨팅 머신을 추가하려면 Azure Stack Hub 에서 추가 작업자 머신 생성 을 참조하십시오.

#### 9.1.4. Google Cloud에 컴퓨팅 머신 추가

Google Cloud의 OpenShift Container Platform 클러스터에 컴퓨팅 머신을 추가하려면 Google Cloud 에서 추가 작업자 머신 생성 을 참조하십시오.

#### 9.1.5. vSphere에 컴퓨팅 머신 추가

컴퓨팅 머신 세트를 사용하여 vSphere에서 OpenShift Container Platform 클러스터에 대한 추가 컴퓨팅 머신 생성을 자동화할 수 있습니다.

클러스터에 컴퓨팅 머신을 수동으로 추가하려면 vSphere에 컴퓨팅 머신 추가를 참조하십시오.

#### 9.1.6. 베어 메탈에 컴퓨팅 머신 추가

베어 메탈의 OpenShift Container Platform 클러스터에 컴퓨팅 머신을 추가하려면 베어 메탈에 컴퓨팅 머신 추가를 참조하십시오.

### 9.2. CloudFormation 템플릿을 사용하여 AWS에 컴퓨팅 머신 추가

샘플 CloudFormation 템플릿을 사용하여 생성한 AWS(Amazon Web Services)의 OpenShift Container Platform 클러스터에 더 많은 컴퓨팅 머신을 추가할 수 있습니다.

#### 9.2.1. 사전 요구 사항

제공된 AWS CloudFormation 템플릿을 사용하여 AWS에 클러스터가 설치되어 있어야 합니다.

클러스터 설치 중에 컴퓨팅 시스템을 생성하는 데 사용한 JSON 파일 및 CloudFormation 템플릿이 있습니다. 이러한 파일이 없는 경우 설치 절차에 따라 파일을 다시 생성해야 합니다.

#### 9.2.2. CloudFormation 템플릿을 사용하여 AWS 클러스터에 추가

샘플 CloudFormation 템플릿을 사용하여 생성한 AWS(Amazon Web Services)의 OpenShift Container Platform 클러스터에 더 많은 컴퓨팅 머신을 추가할 수 있습니다.

중요

CloudFormation 템플릿은 하나의 컴퓨팅 시스템을 나타내는 스택을 생성합니다. 각 컴퓨팅 시스템의 스택을 생성해야 합니다.

참고

컴퓨팅 노드를 생성하는 데 제공된 CloudFormation 템플릿을 사용하지 않는 경우, 제공된 정보를 검토하고 수동으로 인프라를 생성해야 합니다.. 클러스터가 올바르게 초기화되지 않은 경우, Red Hat 지원팀에 설치 로그를 제시하여 문의해야 할 수도 있습니다.

사전 요구 사항

CloudFormation 템플릿을 사용하여 OpenShift Container Platform 클러스터를 설치하고 클러스터 설치 중에 컴퓨팅 시스템을 생성하는 데 사용한 JSON 파일 및 CloudFormation 템플릿에 액세스할 수 있습니다.

AWS CLI를 설치했습니다.

프로세스

다른 컴퓨팅 스택을 생성합니다.

템플릿을 시작합니다.

```shell-session
$ aws cloudformation create-stack --stack-name <name> \
     --template-body file://<template>.yaml \
     --parameters file://<parameters>.json
```

1. `<name>` 은 CloudFormation 스택의 이름입니다(예: `cluster-workers)`. 클러스터를 제거하는 경우 이 스택의 이름을 제공해야 합니다.

2. `<template>` 은 저장한 CloudFormation 템플릿 YAML 파일의 상대 경로 및 이름입니다.

3. `<parameters>` 는 CloudFormation 매개변수 JSON 파일의 상대 경로 및 이름입니다.

템플릿 구성 요소가 있는지 확인합니다.

```shell-session
$ aws cloudformation describe-stacks --stack-name <name>
```

클러스터에 충분한 컴퓨팅 시스템을 생성할 때까지 계속해서 컴퓨팅 스택을 생성합니다.

#### 9.2.3. 머신의 인증서 서명 요청 승인

클러스터에 시스템을 추가하면 추가한 시스템별로 보류 중인 인증서 서명 요청(CSR)이 두 개씩 생성됩니다. 이러한 CSR이 승인되었는지 확인해야 하며, 필요한 경우 이를 직접 승인해야 합니다. 클라이언트 요청을 먼저 승인한 다음 서버 요청을 승인해야 합니다.

사전 요구 사항

클러스터에 시스템을 추가했습니다.

프로세스

클러스터가 시스템을 인식하는지 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME      STATUS    ROLES   AGE  VERSION
master-0  Ready     master  63m  v1.33.4
master-1  Ready     master  63m  v1.33.4
master-2  Ready     master  64m  v1.33.4
```

출력에 생성된 모든 시스템이 나열됩니다.

참고

이전 출력에는 일부 CSR이 승인될 때까지 컴퓨팅 노드(작업자 노드라고도 함)가 포함되지 않을 수 있습니다.

보류 중인 CSR을 검토하고 클러스터에 추가한 각 시스템에 대해 `Pending` 또는 `Approved` 상태의 클라이언트 및 서버 요청이 표시되는지 확인합니다.

```shell-session
$ oc get csr
```

```shell-session
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
...
```

예에서는 두 시스템이 클러스터에 참여하고 있습니다. 목록에는 승인된 CSR이 더 많이 나타날 수도 있습니다.

CSR이 승인되지 않은 경우, 추가된 시스템에 대한 모든 보류 중인 CSR이 `Pending` 상태로 전환된 후 클러스터 시스템의 CSR을 승인합니다.

참고

CSR은 교체 주기가 자동으로 만료되므로 클러스터에 시스템을 추가한 후 1시간 이내에 CSR을 승인하십시오. 한 시간 내에 승인하지 않으면 인증서가 교체되고 각 노드에 대해 두 개 이상의 인증서가 표시됩니다. 이러한 인증서를 모두 승인해야 합니다. 클라이언트 CSR이 승인되면 Kubelet은 인증서에 대한 보조 CSR을 생성하므로 수동 승인이 필요합니다. 그러면 Kubelet에서 동일한 매개변수를 사용하여 새 인증서를 요청하는 경우 인증서 갱신 요청은 `machine-approver` 에 의해 자동으로 승인됩니다.

참고

베어 메탈 및 기타 사용자 프로비저닝 인프라와 같이 머신 API를 사용하도록 활성화되지 않는 플랫폼에서 실행되는 클러스터의 경우 CSR(Kubelet service Certificate Request)을 자동으로 승인하는 방법을 구현해야 합니다. 요청이 승인되지 않으면 API 서버가 kubelet에 연결될 때 서비스 인증서가 필요하므로,, 아래 명령을 성공적으로 수행할 수 없습니다. Kubelet 엔드 포인트에 연결하는 모든 작업을 수행하려면 이 인증서 승인이 필요합니다. 이 방법은 새 CSR을 감시하고 CSR이 `system:node` 또는 `system:admin` 그룹의 `node-bootstrapper` 서비스 계정에 의해 제출되었는지 확인하고 노드의 ID를 확인합니다.

```shell
oc exec
```

```shell
oc rsh
```

```shell
oc logs
```

개별적으로 승인하려면 유효한 CSR 각각에 대해 다음 명령을 실행하십시오.

```shell-session
$ oc adm certificate approve <csr_name>
```

1. `<csr_name>` 은 현재 CSR 목록에 있는 CSR의 이름입니다.

보류 중인 CSR을 모두 승인하려면 다음 명령을 실행하십시오.

```shell-session
$ oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve
```

참고

일부 Operator는 일부 CSR이 승인될 때까지 사용할 수 없습니다.

이제 클라이언트 요청이 승인되었으므로 클러스터에 추가한 각 머신의 서버 요청을 검토해야 합니다.

```shell-session
$ oc get csr
```

```shell-session
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending
csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...
```

나머지 CSR이 승인되지 않고 `Pending` 상태인 경우 클러스터 머신의 CSR을 승인합니다.

개별적으로 승인하려면 유효한 CSR 각각에 대해 다음 명령을 실행하십시오.

```shell-session
$ oc adm certificate approve <csr_name>
```

1. `<csr_name>` 은 현재 CSR 목록에 있는 CSR의 이름입니다.

보류 중인 CSR을 모두 승인하려면 다음 명령을 실행하십시오.

```shell-session
$ oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs oc adm certificate approve
```

모든 클라이언트 및 서버 CSR이 승인된 후 머신은 `Ready` 상태가 됩니다. 다음 명령을 실행하여 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME      STATUS    ROLES   AGE  VERSION
master-0  Ready     master  73m  v1.33.4
master-1  Ready     master  73m  v1.33.4
master-2  Ready     master  74m  v1.33.4
worker-0  Ready     worker  11m  v1.33.4
worker-1  Ready     worker  11m  v1.33.4
```

참고

머신이 `Ready` 상태로 전환하는 데 서버 CSR의 승인 후 몇 분이 걸릴 수 있습니다.

추가 정보

인증서 서명 요청

### 9.3. vSphere에 수동으로 컴퓨팅 머신 추가

VMware vSphere의 OpenShift Container Platform 클러스터에 컴퓨팅 머신을 수동으로 추가할 수 있습니다.

참고

컴퓨팅 머신 세트를 사용하여 클러스터에 대한 추가 VMware vSphere 컴퓨팅 머신 생성을 자동화할 수도 있습니다.

#### 9.3.1. 사전 요구 사항

vSphere에 클러스터가 설치되어 있어야 합니다.

클러스터를 생성하는 데 사용한 설치 미디어 및 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지가 있습니다. 이러한 파일이 없는 경우 설치 절차에 따라 파일을 가져와야 합니다.

중요

클러스터를 생성하는 데 사용된 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지에 액세스할 수 없는 경우 최신 버전의 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지를 사용하여 OpenShift Container Platform 클러스터에 더 많은 컴퓨팅 머신을 추가할 수 있습니다. 자세한 내용은 OpenShift 4.6+로 업그레이드한 후 UPI 클러스터에 새 노드 추가 실패 를 참조하십시오.

#### 9.3.2. vSphere의 클러스터에 더 많은 컴퓨팅 머신 추가

VMware vSphere에서 사용자가 프로비저닝한 OpenShift Container Platform 클러스터에 더 많은 컴퓨팅 머신을 추가할 수 있습니다.

vSphere 템플릿이 OpenShift Container Platform 클러스터에 배포된 후 해당 클러스터의 머신용 VM(가상 머신)을 배포할 수 있습니다.

사전 요구 사항

컴퓨팅 머신의 base64로 인코딩된 Ignition 파일을 가져옵니다.

클러스터에 생성한 vSphere 템플릿에 액세스할 수 있습니다.

프로세스

템플릿 이름을 마우스 오른쪽 버튼으로 클릭하고 Clone → Clone to Virtual Machine 을 클릭합니다.

Select a name and folder 탭에서 가상 머신의 이름을 지정합니다. `compute-1` 과 같은 머신 유형을 이름에 포함할 수 있습니다.

참고

vSphere 설치의 모든 가상 머신 이름이 고유한지 확인합니다.

Select a name and folder 탭에서 클러스터에 대해 생성한 폴더의 이름을 선택합니다.

Select a compute resource 탭에서 데이터 센터에서 호스트 이름을 선택합니다.

스토리지 선택 탭에서 구성 및 디스크 파일에 대한 스토리지를 선택합니다.

복제 옵션 선택 탭에서 이 가상 머신의 하드웨어 사용자 지정 을 선택합니다.

하드웨어 사용자 지정 탭에서 고급 매개 변수 를 클릭합니다.

속성 및 값 필드에 데이터를 지정하여 다음 구성 매개 변수 이름 및 값을 추가합니다. 생성한 각 매개변수에 대한 추가 버튼을 선택해야 합니다.

`guestinfo.ignition.config.data`: 이 머신 유형에 대해 base64로 인코딩된 컴퓨팅 Ignition 구성 파일의 내용을 붙여넣습니다.

`guestinfo.ignition.config.data.encoding`: `base64` 를 지정합니다.

`disk.EnableUUID`: `TRUE` 를 지정합니다.

Customize hardware 탭의 Virtual Hardware 패널에서 지정된 값을 필요에 따라 수정합니다. RAM, CPU 및 디스크 스토리지의 양이 시스템 유형에 대한 최소 요구사항을 충족하는지 확인합니다. 많은 네트워크가 있는 경우 새 장치 추가 > 네트워크 어댑터 를 선택한 다음 새 네트워크 메뉴 항목에서 제공하는 필드에 네트워크 정보를 입력합니다.

나머지 구성 단계를 완료합니다. 완료 버튼을 클릭하면 복제 작업을 완료했습니다.

가상 머신 탭에서 VM을 마우스 오른쪽 버튼으로 클릭한 다음 전원 → 전원 켜기 을 선택합니다.

다음 단계

계속해서 클러스터에 추가 컴퓨팅 머신을 만듭니다.

#### 9.3.3. 시스템의 인증서 서명 요청 승인

클러스터에 시스템을 추가하면 추가한 시스템별로 보류 중인 인증서 서명 요청(CSR)이 두 개씩 생성됩니다. 이러한 CSR이 승인되었는지 확인해야 하며, 필요한 경우 이를 직접 승인해야 합니다. 클라이언트 요청을 먼저 승인한 다음 서버 요청을 승인해야 합니다.

사전 요구 사항

클러스터에 시스템을 추가했습니다.

프로세스

클러스터가 시스템을 인식하는지 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME      STATUS    ROLES   AGE  VERSION
master-0  Ready     master  63m  v1.33.4
master-1  Ready     master  63m  v1.33.4
master-2  Ready     master  64m  v1.33.4
```

출력에 생성된 모든 시스템이 나열됩니다.

참고

이전 출력에는 일부 CSR이 승인될 때까지 컴퓨팅 노드(작업자 노드라고도 함)가 포함되지 않을 수 있습니다.

보류 중인 CSR을 검토하고 클러스터에 추가한 각 시스템에 대해 `Pending` 또는 `Approved` 상태의 클라이언트 및 서버 요청이 표시되는지 확인합니다.

```shell-session
$ oc get csr
```

```shell-session
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
...
```

예에서는 두 시스템이 클러스터에 참여하고 있습니다. 목록에는 승인된 CSR이 더 많이 나타날 수도 있습니다.

CSR이 승인되지 않은 경우, 추가된 시스템에 대한 모든 보류 중인 CSR이 `Pending` 상태로 전환된 후 클러스터 시스템의 CSR을 승인합니다.

참고

CSR은 교체 주기가 자동으로 만료되므로 클러스터에 시스템을 추가한 후 1시간 이내에 CSR을 승인하십시오. 한 시간 내에 승인하지 않으면 인증서가 교체되고 각 노드에 대해 두 개 이상의 인증서가 표시됩니다. 이러한 인증서를 모두 승인해야 합니다. 클라이언트 CSR이 승인되면 Kubelet은 인증서에 대한 보조 CSR을 생성하므로 수동 승인이 필요합니다. 그러면 Kubelet에서 동일한 매개변수를 사용하여 새 인증서를 요청하는 경우 인증서 갱신 요청은 `machine-approver` 에 의해 자동으로 승인됩니다.

참고

베어 메탈 및 기타 사용자 프로비저닝 인프라와 같이 머신 API를 사용하도록 활성화되지 않는 플랫폼에서 실행되는 클러스터의 경우 CSR(Kubelet service Certificate Request)을 자동으로 승인하는 방법을 구현해야 합니다. 요청이 승인되지 않으면 API 서버가 kubelet에 연결될 때 서비스 인증서가 필요하므로,, 아래 명령을 성공적으로 수행할 수 없습니다. Kubelet 엔드 포인트에 연결하는 모든 작업을 수행하려면 이 인증서 승인이 필요합니다. 이 방법은 새 CSR을 감시하고 CSR이 `system:node` 또는 `system:admin` 그룹의 `node-bootstrapper` 서비스 계정에 의해 제출되었는지 확인하고 노드의 ID를 확인합니다.

```shell
oc exec
```

```shell
oc rsh
```

```shell
oc logs
```

개별적으로 승인하려면 유효한 CSR 각각에 대해 다음 명령을 실행하십시오.

```shell-session
$ oc adm certificate approve <csr_name>
```

1. `<csr_name>` 은 현재 CSR 목록에 있는 CSR의 이름입니다.

보류 중인 CSR을 모두 승인하려면 다음 명령을 실행하십시오.

```shell-session
$ oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve
```

참고

일부 Operator는 일부 CSR이 승인될 때까지 사용할 수 없습니다.

이제 클라이언트 요청이 승인되었으므로 클러스터에 추가한 각 머신의 서버 요청을 검토해야 합니다.

```shell-session
$ oc get csr
```

```shell-session
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending
csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...
```

나머지 CSR이 승인되지 않고 `Pending` 상태인 경우 클러스터 머신의 CSR을 승인합니다.

개별적으로 승인하려면 유효한 CSR 각각에 대해 다음 명령을 실행하십시오.

```shell-session
$ oc adm certificate approve <csr_name>
```

1. `<csr_name>` 은 현재 CSR 목록에 있는 CSR의 이름입니다.

보류 중인 CSR을 모두 승인하려면 다음 명령을 실행하십시오.

```shell-session
$ oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs oc adm certificate approve
```

모든 클라이언트 및 서버 CSR이 승인된 후 머신은 `Ready` 상태가 됩니다. 다음 명령을 실행하여 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME      STATUS    ROLES   AGE  VERSION
master-0  Ready     master  73m  v1.33.4
master-1  Ready     master  73m  v1.33.4
master-2  Ready     master  74m  v1.33.4
worker-0  Ready     worker  11m  v1.33.4
worker-1  Ready     worker  11m  v1.33.4
```

참고

머신이 `Ready` 상태로 전환하는 데 서버 CSR의 승인 후 몇 분이 걸릴 수 있습니다.

추가 정보

인증서 서명 요청

### 9.4. 베어 메탈에 컴퓨팅 머신 추가

베어 메탈 또는 플랫폼과 무관한 클러스터의 OpenShift Container Platform 클러스터에 더 많은 컴퓨팅 머신을 추가할 수 있습니다.

#### 9.4.1. 사전 요구 사항

베어 메탈에 클러스터가 설치되어 있어야 합니다.

모든 플랫폼에 클러스터가 설치되어 있어야 합니다.

클러스터를 생성하는 데 사용한 설치 미디어 및 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지가 있습니다. 이러한 파일이 없는 경우 설치 절차에 따라 파일을 가져와야 합니다.

사용자 프로비저닝 인프라에 DHCP 서버를 사용할 수 있는 경우 추가 컴퓨팅 머신의 세부 정보를 DHCP 서버 구성에 추가했습니다. 여기에는 영구 IP 주소, DNS 서버 정보 및 각 시스템의 호스트 이름이 포함됩니다.

추가하려는 각 컴퓨팅 시스템의 레코드 이름 및 IP 주소를 포함하도록 DNS 구성을 업데이트했습니다. DNS 조회 및 역방향 DNS 조회가 올바르게 확인되었는지 확인했습니다.

중요

클러스터를 생성하는 데 사용된 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지에 액세스할 수 없는 경우 최신 버전의 RHCOS(Red Hat Enterprise Linux CoreOS) 이미지를 사용하여 OpenShift Container Platform 클러스터에 더 많은 컴퓨팅 머신을 추가할 수 있습니다. 자세한 내용은 OpenShift 4.6+로 업그레이드한 후 UPI 클러스터에 새 노드 추가 실패 를 참조하십시오.

#### 9.4.2. RHCOS(Red Hat Enterprise Linux CoreOS) 머신 생성

베어메탈 인프라에 설치된 클러스터에 컴퓨팅 머신을 추가하기 전에 사용할 RHCOS 머신을 생성해야 합니다. ISO 이미지 또는 네트워크 PXE 부팅을 사용하여 시스템을 생성합니다.

참고

클러스터의 모든 새 노드를 배포하려면 클러스터를 설치하는 데 사용한 것과 동일한 ISO 이미지를 사용해야 합니다. 동일한 Ignition 구성 파일을 사용하는 것이 좋습니다. 노드는 워크로드를 실행하기 전에 첫 번째 부팅 시 자동으로 업그레이드됩니다. 업그레이드 전이나 후에 노드를 추가할 수 있습니다.

#### 9.4.2.1. ISO 이미지를 사용하여 RHCOS 머신 생성

ISO 이미지를 사용하여 머신을 생성하여 베어 메탈 클러스터에 대해 RHCOS(Red Hat Enterprise Linux CoreOS) 컴퓨팅 머신을 추가로 생성할 수 있습니다.

사전 요구 사항

클러스터의 컴퓨팅 머신에 대한 Ignition 구성 파일의 URL을 가져옵니다. 설치 중에 이 파일은 HTTP 서버에 업로드되어 있어야 합니다.

OpenShift CLI()가 설치되어 있어야 합니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터에서 Ignition 구성 파일을 추출합니다.

```shell-session
$ oc extract -n openshift-machine-api secret/worker-user-data-managed --keys=userData --to=- > worker.ign
```

클러스터에서 내보낸 `worker.ign` Ignition 구성 파일을 HTTP 서버로 업로드합니다. 해당 파일의 URL을 기록해 둡니다.

Ignition 파일을 URL에서 사용할 수 있는지 확인할 수 있습니다. 다음 예제에서는 컴퓨팅 노드에 대한 Ignition 구성 파일을 가져옵니다.

```shell-session
$ curl -k http://<HTTP_server>/worker.ign
```

다음 명령으로 실행하여 새 머신을 부팅하기 위해 ISO 이미지에 액세스할 수 있습니다.

```shell-session
RHCOS_VHD_ORIGIN_URL=$(oc -n openshift-machine-config-operator get configmap/coreos-bootimages -o jsonpath='{.data.stream}' | jq -r '.architectures.<architecture>.artifacts.metal.formats.iso.disk.location')
```

ISO 파일을 사용하여 추가 컴퓨팅 머신에 RHCOS를 설치합니다. 클러스터를 설치하기 전에 머신을 만들 때 사용한 것과 동일한 방법을 사용합니다.

ISO 이미지를 디스크에 굽고 직접 부팅합니다.

LOM 인터페이스에서 ISO 리디렉션을 사용합니다.

옵션을 지정하거나 라이브 부팅 시퀀스를 중단하지 않고 RHCOS ISO 이미지를 부팅합니다. 설치 프로그램이 RHCOS 라이브 환경에서 쉘 프롬프트로 부팅될 때까지 기다립니다.

참고

RHCOS 설치 부팅 프로세스를 중단하여 커널 인수를 추가할 수 있습니다. 그러나 이 ISO 절차에서는 커널 인수를 추가하는 대신 다음 단계에 설명된 대로 `coreos-installer` 명령을 사용해야 합니다.

`coreos-installer` 명령을 실행하고 설치 요구 사항을 충족하는 옵션을 지정합니다. 최소한 노드 유형에 대한 Ignition 구성 파일과 설치할 장치를 가리키는 URL을 지정해야 합니다.

```shell-session
$ sudo coreos-installer install --ignition-url=http://<HTTP_server>/<node_type>.ign <device> --ignition-hash=sha512-<digest>
```

1. `core` 사용자에게 설치를 수행하는 데 필요한 root 권한이 없으므로 `sudo` 를 사용하여 `coreos-installer` 명령을 실행해야 합니다.

2. 클러스터 노드에서 Ignition 구성 파일을 HTTP URL을 통해 가져오려면 `--ignition-hash` 옵션이 필요합니다. `<digest>` 는 이전 단계에서 얻은 Ignition 구성 파일 SHA512 다이제스트입니다.

참고

TLS를 사용하는 HTTPS 서버를 통해 Ignition 구성 파일을 제공하려는 경우 `coreos-installer` 를 실행하기 전에 내부 인증 기관(CA)을 시스템 신뢰 저장소에 추가할 수 있습니다.

다음 예제에서는 컴퓨팅 노드 설치를 `/dev/sda` 장치에 초기화합니다. 컴퓨팅 노드의 Ignition 구성 파일은 IP 주소 192.168.1.2가 있는 HTTP 웹 서버에서 가져옵니다.

```shell-session
$ sudo coreos-installer install --ignition-url=http://192.168.1.2:80/installation_directory/worker.ign /dev/sda --ignition-hash=sha512-a5a2d43879223273c9b60af66b44202a1d1248fc01cf156c46d4a79f552b6bad47bc8cc78ddf0116e80c59d2ea9e32ba53bc807afbca581aa059311def2c3e3b
```

머신 콘솔에서 RHCOS 설치 진행률을 모니터링합니다.

중요

OpenShift Container Platform 설치를 시작하기 전에 각 노드에서 성공적으로 설치되었는지 확인합니다. 설치 프로세스를 관찰하면 발생할 수 있는 RHCOS 설치 문제의 원인을 파악하는 데 도움이 될 수 있습니다.

계속해서 클러스터에 추가 컴퓨팅 머신을 만듭니다.

#### 9.4.2.2. PXE 또는 iPXE 부팅을 통해 RHCOS 머신 생성

PXE 또는 iPXE 부팅을 사용하여 베어 메탈 클러스터에 대해 RHCOS(Red Hat Enterprise Linux CoreOS) 컴퓨팅 머신을 추가로 생성할 수 있습니다.

사전 요구 사항

클러스터의 컴퓨팅 머신에 대한 Ignition 구성 파일의 URL을 가져옵니다. 설치 중에 이 파일은 HTTP 서버에 업로드되어 있어야 합니다.

클러스터 설치 중에 HTTP 서버에 업로드 한 RHCOS ISO 이미지, 압축된 메탈 BIOS, `kernel` 및 `initramfs` 파일의 URL을 가져옵니다.

설치 중에 OpenShift Container Platform 클러스터에 대한 머신을 생성하는 데 사용한 PXE 부팅 인프라에 액세스할 수 있습니다. RHCOS가 설치된 후 로컬 디스크에서 머신을 부팅해야합니다.

UEFI를 사용하는 경우 OpenShift Container Platform 설치 중에 수정 한 `grub.conf` 파일에 액세스할 수 있습니다.

프로세스

RHCOS 이미지의 PXE 또는 iPXE가 올바르게 설치되었는지 확인합니다.

```plaintext
DEFAULT pxeboot
TIMEOUT 20
PROMPT 0
LABEL pxeboot
    KERNEL http://<HTTP_server>/rhcos-<version>-live-kernel-<architecture>
    APPEND initrd=http://<HTTP_server>/rhcos-<version>-live-initramfs.<architecture>.img coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://<HTTP_server>/worker.ign coreos.live.rootfs_url=http://<HTTP_server>/rhcos-<version>-live-rootfs.<architecture>.img
```

1. HTTP 서버에 업로드한 라이브 `kernel` 파일의 위치를 지정합니다.

2. HTTP 서버에 업로드한 RHCOS 파일의 위치를 지정합니다. `initrd` 매개변수 값은 `initramfs` 파일의 위치이고 `coreos.inst.ignition_url` 매개변수 값은 작업자 Ignition 설정 파일의 위치이며 `coreos.live.rootfs_url` 매개 변수 값은 라이브 `rootfs` 파일의 위치입니다. `coreos.inst.ignition_url` 및 `coreos.live.rootfs_url` 매개변수는 HTTP 및 HTTPS만 지원합니다.

참고

이 구성은 그래픽 콘솔이 있는 시스템에서 직렬 콘솔 액세스를 활성화하지 않습니다. 다른 콘솔을 구성하려면 `APPEND` 행에 하나 이상의 `console=` 인수를 추가합니다. 예를 들어 `console=tty0 console=ttyS0` 을 추가하여 첫 번째 PC 직렬 포트를 기본 콘솔로 설정하고 그래픽 콘솔을 보조 콘솔로 설정합니다. 자세한 내용은 Red Hat Enterprise Linux에서 직렬 터미널 및/또는 콘솔 설정 방법 을 참조하십시오.

```plaintext
kernel http://<HTTP_server>/rhcos-<version>-live-kernel-<architecture> initrd=main coreos.live.rootfs_url=http://<HTTP_server>/rhcos-<version>-live-rootfs.<architecture>.img coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://<HTTP_server>/worker.ign
initrd --name main http://<HTTP_server>/rhcos-<version>-live-initramfs.<architecture>.img
boot
```

1. HTTP 서버에 업로드한 RHCOS 파일의 위치를 지정합니다. `kernel` 매개변수 값은 `커널` 파일의 위치이며 `initrd=main` 인수는 UEFI 시스템에서 부팅하는 데 필요하며 `coreos.live.rootfs_url` 매개변수 값은 `rootfs` 파일의 위치이며 `coreos.inst.ignition_url` 매개변수 값은 작업자 Ignition 구성 파일의 위치입니다.

2. NIC를 여러 개 사용하는 경우 `ip` 옵션에 단일 인터페이스를 지정합니다. 예를 들어, `eno1` 라는 NIC에서 DHCP를 사용하려면 `ip=eno1:dhcp` 를 설정하십시오.

3. HTTP 서버에 업로드한 `initramfs` 파일의 위치를 지정합니다.

참고

이 구성은 그래픽 콘솔이 있는 머신에서 직렬 콘솔 액세스를 활성화하지 않습니다. 다른 콘솔을 구성하려면 `kernel` 행에 하나 이상의 `console=` 인수를 추가합니다. 예를 들어 `console=tty0 console=ttyS0` 을 추가하여 첫 번째 PC 직렬 포트를 기본 콘솔로 설정하고 그래픽 콘솔을 보조 콘솔로 설정합니다. 자세한 내용은 How does one set up a serial terminal and/or console in Red Hat Enterprise Linux? 및 "Enabling the serial console for PXE and ISO installation" 섹션을 참조하십시오.

참고

`aarch64` 아키텍처에서 CoreOS `kernel` 을 부팅하려면 `IMAGE_GZIP` 옵션이 활성화된 iPXE 빌드 버전을 사용해야 합니다. iPXE의 `IMAGE_GZIP` 옵션 을 참조하십시오.

```plaintext
menuentry 'Install CoreOS' {
    linux rhcos-<version>-live-kernel-<architecture>  coreos.live.rootfs_url=http://<HTTP_server>/rhcos-<version>-live-rootfs.<architecture>.img coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://<HTTP_server>/worker.ign
    initrd rhcos-<version>-live-initramfs.<architecture>.img
}
```

1. HTTP/TFTP 서버에 업로드한 RHCOS 파일의 위치를 지정합니다. `kernel` 매개변수 값은 TFTP 서버의 파일의 위치입니다. `coreos.live.rootfs_url` 매개변수 값은 `rootfs` 파일의 위치이고, `coreos.inst.ignition_url` 매개변수 값은 HTTP 서버의 Worker Ignition 구성 파일의 위치입니다.

2. NIC를 여러 개 사용하는 경우 `ip` 옵션에 단일 인터페이스를 지정합니다. 예를 들어, `eno1` 라는 NIC에서 DHCP를 사용하려면 `ip=eno1:dhcp` 를 설정하십시오.

3. TFTP 서버에 업로드한 `initramfs` 파일의 위치를 지정합니다.

PXE 또는 iPXE 인프라를 사용하여 클러스터에 필요한 컴퓨팅 머신을 만듭니다.

#### 9.4.3. 시스템의 인증서 서명 요청 승인

클러스터에 시스템을 추가하면 추가한 시스템별로 보류 중인 인증서 서명 요청(CSR)이 두 개씩 생성됩니다. 이러한 CSR이 승인되었는지 확인해야 하며, 필요한 경우 이를 직접 승인해야 합니다. 클라이언트 요청을 먼저 승인한 다음 서버 요청을 승인해야 합니다.

사전 요구 사항

클러스터에 시스템을 추가했습니다.

프로세스

클러스터가 시스템을 인식하는지 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME      STATUS    ROLES   AGE  VERSION
master-0  Ready     master  63m  v1.33.4
master-1  Ready     master  63m  v1.33.4
master-2  Ready     master  64m  v1.33.4
```

출력에 생성된 모든 시스템이 나열됩니다.

참고

이전 출력에는 일부 CSR이 승인될 때까지 컴퓨팅 노드(작업자 노드라고도 함)가 포함되지 않을 수 있습니다.

보류 중인 CSR을 검토하고 클러스터에 추가한 각 시스템에 대해 `Pending` 또는 `Approved` 상태의 클라이언트 및 서버 요청이 표시되는지 확인합니다.

```shell-session
$ oc get csr
```

```shell-session
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
...
```

예에서는 두 시스템이 클러스터에 참여하고 있습니다. 목록에는 승인된 CSR이 더 많이 나타날 수도 있습니다.

CSR이 승인되지 않은 경우, 추가된 시스템에 대한 모든 보류 중인 CSR이 `Pending` 상태로 전환된 후 클러스터 시스템의 CSR을 승인합니다.

참고

CSR은 교체 주기가 자동으로 만료되므로 클러스터에 시스템을 추가한 후 1시간 이내에 CSR을 승인하십시오. 한 시간 내에 승인하지 않으면 인증서가 교체되고 각 노드에 대해 두 개 이상의 인증서가 표시됩니다. 이러한 인증서를 모두 승인해야 합니다. 클라이언트 CSR이 승인되면 Kubelet은 인증서에 대한 보조 CSR을 생성하므로 수동 승인이 필요합니다. 그러면 Kubelet에서 동일한 매개변수를 사용하여 새 인증서를 요청하는 경우 인증서 갱신 요청은 `machine-approver` 에 의해 자동으로 승인됩니다.

참고

베어 메탈 및 기타 사용자 프로비저닝 인프라와 같이 머신 API를 사용하도록 활성화되지 않는 플랫폼에서 실행되는 클러스터의 경우 CSR(Kubelet service Certificate Request)을 자동으로 승인하는 방법을 구현해야 합니다. 요청이 승인되지 않으면 API 서버가 kubelet에 연결될 때 서비스 인증서가 필요하므로,, 아래 명령을 성공적으로 수행할 수 없습니다. Kubelet 엔드 포인트에 연결하는 모든 작업을 수행하려면 이 인증서 승인이 필요합니다. 이 방법은 새 CSR을 감시하고 CSR이 `system:node` 또는 `system:admin` 그룹의 `node-bootstrapper` 서비스 계정에 의해 제출되었는지 확인하고 노드의 ID를 확인합니다.

```shell
oc exec
```

```shell
oc rsh
```

```shell
oc logs
```

개별적으로 승인하려면 유효한 CSR 각각에 대해 다음 명령을 실행하십시오.

```shell-session
$ oc adm certificate approve <csr_name>
```

1. `<csr_name>` 은 현재 CSR 목록에 있는 CSR의 이름입니다.

보류 중인 CSR을 모두 승인하려면 다음 명령을 실행하십시오.

```shell-session
$ oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve
```

참고

일부 Operator는 일부 CSR이 승인될 때까지 사용할 수 없습니다.

이제 클라이언트 요청이 승인되었으므로 클러스터에 추가한 각 머신의 서버 요청을 검토해야 합니다.

```shell-session
$ oc get csr
```

```shell-session
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending
csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...
```

나머지 CSR이 승인되지 않고 `Pending` 상태인 경우 클러스터 머신의 CSR을 승인합니다.

개별적으로 승인하려면 유효한 CSR 각각에 대해 다음 명령을 실행하십시오.

```shell-session
$ oc adm certificate approve <csr_name>
```

1. `<csr_name>` 은 현재 CSR 목록에 있는 CSR의 이름입니다.

보류 중인 CSR을 모두 승인하려면 다음 명령을 실행하십시오.

```shell-session
$ oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs oc adm certificate approve
```

모든 클라이언트 및 서버 CSR이 승인된 후 머신은 `Ready` 상태가 됩니다. 다음 명령을 실행하여 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME      STATUS    ROLES   AGE  VERSION
master-0  Ready     master  73m  v1.33.4
master-1  Ready     master  73m  v1.33.4
master-2  Ready     master  74m  v1.33.4
worker-0  Ready     worker  11m  v1.33.4
worker-1  Ready     worker  11m  v1.33.4
```

참고

머신이 `Ready` 상태로 전환하는 데 서버 CSR의 승인 후 몇 분이 걸릴 수 있습니다.

추가 정보

인증서 서명 요청

### 10.1. 컨트롤 플레인 머신 세트 정보

컨트롤 플레인 머신 세트를 사용하면 OpenShift Container Platform 클러스터 내에서 컨트롤 플레인 머신 리소스 관리를 자동화할 수 있습니다.

중요

컨트롤 플레인 머신 세트는 컴퓨팅 머신을 관리할 수 없으며 컴퓨팅 머신 세트는 컨트롤 플레인 시스템을 관리할 수 없습니다.

컨트롤 플레인 머신 세트는 컴퓨팅 머신에 제공하는 컴퓨팅 머신 세트와 유사한 관리 기능을 컨트롤 플레인 시스템에 제공합니다. 그러나 이러한 두 가지 유형의 머신 세트는 Machine API 내에 정의된 별도의 사용자 지정 리소스이며 아키텍처 및 기능에 몇 가지 근본적인 차이점이 있습니다.

#### 10.1.1. Control Plane Machine Set Operator 개요

Control Plane Machine Set Operator는 `ControlPlaneMachineSet` CR(사용자 정의 리소스)을 사용하여 OpenShift Container Platform 클러스터 내의 컨트롤 플레인 머신 리소스 관리를 자동화합니다.

클러스터 컨트롤 플레인 머신 세트의 상태가 `Active` 로 설정된 경우 Operator는 클러스터에 지정된 구성이 있는 컨트롤 플레인 머신 수가 올바르게 있는지 확인합니다. 이를 통해 성능이 저하된 컨트롤 플레인 시스템을 자동으로 교체하고 컨트롤 플레인에 변경 사항을 롤아웃할 수 있습니다.

클러스터에는 하나의 컨트롤 플레인 머신 세트만 있으며 Operator는 `openshift-machine-api` 네임스페이스의 오브젝트만 관리합니다.

#### 10.1.1.1. Control Plane Machine Set Operator 제한 사항

Control Plane Machine Set Operator에는 다음과 같은 제한 사항이 있습니다.

AWS(Amazon Web Services), Google Cloud, IBM Power® Virtual Server, Microsoft Azure, Nutanix, VMware vSphere 및 RHOSP(Red Hat OpenStack Platform) 클러스터만 지원됩니다.

컨트롤 플레인 노드를 나타내는 기존 머신이 없는 클러스터는 컨트롤 플레인 머신 세트를 사용하거나 설치 후 컨트롤 플레인 머신 세트를 사용할 수 없습니다. 일반적으로 기존 컨트롤 플레인 시스템은 설치 프로그램에서 프로비저닝한 인프라를 사용하여 클러스터를 설치한 경우에만 존재합니다.

클러스터에 기존 컨트롤 플레인 시스템이 필요한지 확인하려면 관리자 권한이 있는 사용자로 다음 명령을 실행합니다.

```shell-session
$ oc get machine \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machine-role=master
```

```plaintext
NAME                    PHASE     TYPE         REGION      ZONE         AGE
<infrastructure_id>-master-0   Running   m6i.xlarge   us-west-1   us-west-1a   5h19m
<infrastructure_id>-master-1   Running   m6i.xlarge   us-west-1   us-west-1b   5h19m
<infrastructure_id>-master-2   Running   m6i.xlarge   us-west-1   us-west-1a   5h19m
```

```plaintext
No resources found in openshift-machine-api namespace.
```

Operator는 Machine API Operator가 작동해야 하므로 수동으로 프로비저닝된 머신이 있는 클러스터에서는 지원되지 않습니다. 활성으로 생성된 `ControlPlaneMachineSet` 사용자 정의 리소스(CR)를 생성하는 플랫폼에 대해 수동으로 프로비저닝된 머신을 사용하여 OpenShift Container Platform 클러스터를 설치할 때 설치 프로세스에서 컨트롤 플레인 머신 세트를 정의하는 Kubernetes 매니페스트 파일을 제거해야 합니다.

컨트롤 플레인 시스템이 3개인 클러스터만 지원됩니다.

컨트롤 플레인의 수평 스케일링은 지원되지 않습니다.

임시 OS 디스크에 Azure 컨트롤 플레인 시스템을 배포하면 데이터 손실 위험이 증가하고 지원되지 않습니다.

컨트롤 플레인 머신을 AWS Spot 인스턴스, Google Cloud 선점 가능 VM 또는 Azure Spot 가상 머신으로 배포하는 것은 지원되지 않습니다.

중요

컨트롤 플레인 머신을 AWS Spot 인스턴스, Google Cloud 선점 가능 가상 머신 또는 Azure Spot 가상 머신으로 배포하려고 하면 클러스터에서 etcd 쿼럼이 손실될 수 있습니다. 모든 컨트롤 플레인 시스템을 동시에 손실하는 클러스터는 복구할 수 없습니다.

설치 중 또는 설치 전에 컨트롤 플레인 머신 세트를 변경하는 것은 지원되지 않습니다. 설치 후만 컨트롤 플레인 머신 세트를 변경해야 합니다.

#### 10.1.2. 추가 리소스

Control Plane Machine Set Operator 참조

`ControlPlaneMachineSet` 사용자 정의 리소스

### 10.2. 컨트롤 플레인 머신 세트 시작하기

컨트롤 플레인 머신 세트를 시작하는 프로세스는 클러스터의 `ControlPlaneMachineSet` CR(사용자 정의 리소스)의 상태에 따라 다릅니다.

활성 생성된 CR이 있는 클러스터

활성 상태의 CR이 생성된 클러스터는 기본적으로 컨트롤 플레인 머신 세트를 사용합니다. 관리자 작업이 필요하지 않습니다.

비활성 생성된 CR이 있는 클러스터

비활성 생성된 CR이 포함된 클러스터의 경우 CR 구성을 검토하고 CR을 활성화해야 합니다.

생성된 CR이 없는 클러스터

생성된 CR을 포함하지 않는 클러스터의 경우 클러스터에 적절한 구성으로 CR을 생성하고 활성화해야 합니다.

클러스터에서 `ControlPlaneMachineSet` CR의 상태에 대해 확신이 있는 경우 CR 상태를 확인할 수 있습니다.

#### 10.2.1. 지원되는 클라우드 공급자

OpenShift Container Platform 4.20에서 컨트롤 플레인 머신 세트는 AWS(Amazon Web Services), Google Cloud, Microsoft Azure, Nutanix 및 VMware vSphere 클러스터에서 지원됩니다.

설치 후 컨트롤 플레인 머신 세트의 상태는 클라우드 공급자 및 클러스터에 설치한 OpenShift Container Platform 버전에 따라 다릅니다.

| 클라우드 공급자 | 기본적으로 활성 상태 | 생성된 CR | 수동 CR 필요 |
| --- | --- | --- | --- |
| AWS(Amazon Web Services) | X [1] | X |  |
| Google Cloud | X [2] | X |  |
| Microsoft Azure | X [2] | X |  |
| Nutanix | X [3] | X |  |
| Red Hat OpenStack Platform (RHOSP) | X [3] | X |  |
| VMware vSphere | X [4] | X |  |

버전 4.11 또는 이전 버전에서 업그레이드된 AWS 클러스터에는 CR 활성화 가 필요합니다.

버전 4.12 또는 이전 버전에서 업그레이드된 Google Cloud 및 Azure 클러스터에는 CR 활성화 가 필요합니다.

버전 4.13 또는 이전 버전에서 업그레이드된 Nutanix 및 RHOSP 클러스터에는 CR 활성화 가 필요합니다.

버전 4.15 또는 이전 버전에서 업그레이드된 vSphere 클러스터에는 CR 활성화 가 필요합니다.

#### 10.2.2. 컨트롤 플레인 머신 세트 사용자 정의 리소스 상태 확인

`ControlPlaneMachineSet` CR(사용자 정의 리소스)의 존재 및 상태를 확인할 수 있습니다.

프로세스

다음 명령을 실행하여 CR의 상태를 확인합니다.

```shell-session
$ oc get controlplanemachineset.machine.openshift.io cluster \
  --namespace openshift-machine-api
```

`Active` 의 결과는 `ControlPlaneMachineSet` CR이 존재하고 활성화되어 있음을 나타냅니다. 관리자 작업이 필요하지 않습니다.

`Inactive` 의 결과는 `ControlPlaneMachineSet` CR이 존재하지만 활성화되지 않았음을 나타냅니다.

`NotFound` 의 결과는 기존 `ControlPlaneMachineSet` CR이 없음을 나타냅니다.

다음 단계

컨트롤 플레인 머신 세트를 사용하려면 클러스터에 대한 올바른 설정이 있는 `ControlPlaneMachineSet` CR이 있는지 확인해야 합니다.

클러스터에 기존 CR이 있는 경우 CR의 구성이 클러스터에 적합한지 확인해야 합니다.

클러스터에 기존 CR이 없는 경우 클러스터에 대한 올바른 구성으로 클러스터를 생성해야 합니다.

#### 10.2.3. 컨트롤 플레인 머신 세트 사용자 정의 리소스 활성화

컨트롤 플레인 머신 세트를 사용하려면 클러스터에 대한 올바른 설정이 있는 `ControlPlaneMachineSet` CR(사용자 정의 리소스)이 있는지 확인해야 합니다. 생성된 CR이 있는 클러스터에서 CR의 구성이 클러스터에 적합한지 확인하고 활성화해야 합니다.

참고

CR의 매개변수에 대한 자세한 내용은 "Control Plane 머신 세트 구성"을 참조하십시오.

프로세스

다음 명령을 실행하여 CR의 구성을 확인합니다.

```shell-session
$ oc --namespace openshift-machine-api edit controlplanemachineset.machine.openshift.io cluster
```

클러스터 구성에 잘못된 필드의 값을 변경합니다.

구성이 올바르면 `.spec.state` 필드를 `Active` 로 설정하고 변경 사항을 저장하여 CR을 활성화합니다.

중요

CR을 활성화하려면 CR 구성을 업데이트하는 데 사용하는 것과 동일한 세션에서 `.spec.state` 필드를 `Active` 로 변경해야 합니다. CR이 `Inactive` 상태로 저장된 경우 컨트롤 플레인 머신 세트 생성기는 CR을 원래 설정으로 재설정합니다.

```shell
oc edit
```

추가 리소스

컨트롤 플레인 머신 세트 구성

#### 10.2.4. 컨트롤 플레인 머신 세트 사용자 정의 리소스 생성

컨트롤 플레인 머신 세트를 사용하려면 클러스터에 대한 올바른 설정이 있는 `ControlPlaneMachineSet` CR(사용자 정의 리소스)이 있는지 확인해야 합니다. 생성된 CR이 없는 클러스터에서 CR을 수동으로 생성하고 활성화해야 합니다.

참고

CR의 구조 및 매개변수에 대한 자세한 내용은 "Control Plane 머신 세트 구성"을 참조하십시오.

프로세스

다음 템플릿을 사용하여 YAML 파일을 생성합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
  replicas: 3
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <cluster_id>
      machine.openshift.io/cluster-api-machine-role: master
      machine.openshift.io/cluster-api-machine-type: master
  state: Active
  strategy:
    type: RollingUpdate
  template:
    machineType: machines_v1beta1_machine_openshift_io
    machines_v1beta1_machine_openshift_io:
      failureDomains:
        platform: <platform>
        <platform_failure_domains>
      metadata:
        labels:
          machine.openshift.io/cluster-api-cluster: <cluster_id>
          machine.openshift.io/cluster-api-machine-role: master
          machine.openshift.io/cluster-api-machine-type: master
      spec:
        providerSpec:
          value:
            <platform_provider_spec>
```

1. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다. `ControlPlaneMachineSet` CR을 생성할 때 이 값을 지정해야 합니다. OpenShift CLI () 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell
oc
```

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

2. Operator 상태를 지정합니다. 상태가 `Inactive` 이면 Operator가 작동하지 않습니다. 값을 `Active` 로 설정하여 Operator를 활성화할 수 있습니다.

중요

CR을 활성화하기 전에 클러스터 요구 사항에 맞게 구성이 올바른지 확인해야 합니다.

3. 클러스터의 업데이트 전략을 지정합니다. 유효한 값은 `OnDelete` 및 `RollingUpdate` 입니다. 기본값은 `RollingUpdate` 입니다. 업데이트 전략에 대한 자세한 내용은 "컨트롤 플레인 구성 업그레이드"를 참조하십시오.

4. 클라우드 공급자 플랫폼 이름을 지정합니다. 유효한 값은 `AWS`, `Azure`, `GCP`, `Nutanix`, `VSphere`, `OpenStack` 입니다.

5. 클러스터에 대한 & `lt;platform_failure_domains&` gt; 구성을 추가합니다. 이 섹션의 형식과 값은 공급자에 따라 다릅니다. 자세한 내용은 클라우드 공급자에 대한 샘플 실패 도메인 구성을 참조하십시오.

6. 인프라 ID를 지정합니다.

7. 클러스터에 대한 `<platform_provider_spec>` 구성을 추가합니다. 이 섹션의 형식과 값은 공급자에 따라 다릅니다. 자세한 내용은 클라우드 공급자의 샘플 공급자 사양을 참조하십시오.

컨트롤 플레인 머신 세트 CR의 샘플 YAML을 참조하여 클러스터 구성에 적합한 값으로 파일을 채웁니다.

클라우드 공급자의 샘플 실패 도메인 구성 및 샘플 공급자 사양을 참조하여 파일의 해당 섹션을 적절한 값으로 업데이트합니다.

구성이 올바르면 `.spec.state` 필드를 `Active` 로 설정하고 변경 사항을 저장하여 CR을 활성화합니다.

다음 명령을 실행하여 YAML 파일에서 CR을 생성합니다.

```shell-session
$ oc create -f <control_plane_machine_set>.yaml
```

여기서 `<control_plane_machine_set` >은 CR 구성이 포함된 YAML 파일의 이름입니다.

추가 리소스

컨트롤 플레인 구성 업데이트

컨트롤 플레인 머신 세트 구성

공급자별 구성 옵션

### 10.3. 컨트롤 플레인 머신 세트를 사용하여 컨트롤 플레인 시스템 관리

컨트롤 플레인 머신 세트는 컨트롤 플레인 관리의 몇 가지 필수 측면을 자동화합니다.

#### 10.3.1. 컨트롤 플레인 구성 업데이트

컨트롤 플레인 머신 세트 CR(사용자 정의 리소스)에서 사양을 업데이트하여 컨트롤 플레인의 머신 구성을 변경할 수 있습니다.

컨트롤 플레인 머신 세트 Operator는 컨트롤 플레인 머신을 모니터링하고 컨트롤 플레인 머신 세트 CR의 사양과 해당 구성을 비교합니다. CR의 사양과 컨트롤 플레인 머신 구성 사이에 불일치가 있는 경우 Operator는 교체를 위해 해당 컨트롤 플레인 머신을 표시합니다.

참고

CR의 매개변수에 대한 자세한 내용은 "Control Plane 머신 세트 구성"을 참조하십시오.

사전 요구 사항

클러스터에는 컨트롤 플레인 머신 세트 Operator가 활성화되어 있습니다.

프로세스

다음 명령을 실행하여 컨트롤 플레인 머신 세트 CR을 편집합니다.

```shell-session
$ oc edit controlplanemachineset.machine.openshift.io cluster \
  -n openshift-machine-api
```

클러스터 구성에서 업데이트할 필드의 값을 변경합니다.

변경 사항을 저장하십시오.

다음 단계

기본 `RollingUpdate` 업데이트 전략을 사용하는 클러스터의 경우 컨트롤 플레인 머신 세트는 변경 사항을 컨트롤 플레인 구성에 자동으로 전파합니다.

`OnDelete` 업데이트 전략을 사용하도록 구성된 클러스터의 경우 컨트롤 플레인 시스템을 수동으로 교체해야 합니다.

#### 10.3.1.1. 컨트롤 플레인 구성 자동 업데이트

`RollingUpdate` 업데이트 전략에서는 변경 사항을 컨트롤 플레인 구성에 자동으로 전파합니다. 이 업데이트 전략은 컨트롤 플레인 머신 세트의 기본 구성입니다.

`RollingUpdate` 업데이트 전략을 사용하는 클러스터의 경우 Operator는 CR에 지정된 구성으로 교체 컨트롤 플레인 머신을 생성합니다. 교체 컨트롤 플레인 머신이 준비되면 Operator에서 교체용으로 표시된 컨트롤 플레인 머신을 삭제합니다. 그런 다음 교체 머신이 컨트롤 플레인에 결합합니다.

여러 컨트롤 플레인 머신이 교체용으로 표시된 경우 Operator는 각 머신을 교체할 때까지 이 교체 프로세스를 한 번에 하나씩 반복하여 교체하는 동안 etcd 상태를 보호합니다.

#### 10.3.1.2. 컨트롤 플레인 구성에 대한 수동 업데이트

`OnDelete` 업데이트 전략을 사용하여 머신을 수동으로 교체하여 컨트롤 플레인 구성에 변경 사항을 전파할 수 있습니다. 머신을 수동으로 교체하면 변경 사항을 보다 광범위하게 적용하기 전에 단일 머신에서 구성 변경 사항을 테스트할 수 있습니다.

`OnDelete` 업데이트 전략을 사용하도록 구성된 클러스터의 경우 Operator는 기존 머신을 삭제할 때 교체 컨트롤 플레인 머신을 생성합니다. 교체 컨트롤 플레인 머신이 준비되면 etcd Operator에서 기존 머신을 삭제할 수 있습니다. 그런 다음 교체 머신이 컨트롤 플레인에 결합합니다.

여러 컨트롤 플레인 머신이 삭제되면 Operator에서 필요한 모든 교체 머신을 동시에 생성합니다. Operator는 한 번에 두 개 이상의 머신이 컨트롤 플레인에서 제거되지 않도록 하여 etcd 상태를 유지합니다.

#### 10.3.2. 컨트롤 플레인 시스템 교체

컨트롤 플레인 머신 세트가 있는 클러스터에서 컨트롤 플레인 시스템을 교체하려면 머신을 수동으로 삭제합니다. 컨트롤 플레인 머신 세트는 컨트롤 플레인 머신 세트 CR(사용자 정의 리소스)의 사양을 사용하여 삭제된 머신을 하나로 대체합니다.

사전 요구 사항

클러스터가 RHOSP(Red Hat OpenStack Platform)에서 실행되고 업그레이드와 같은 컴퓨팅 서버를 비워야 하는 경우 다음 명령을 실행하여 머신이 실행되는 RHOSP 컴퓨팅 노드를 비활성화해야 합니다.

```shell-session
$ openstack compute service set <target_node_host_name> nova-compute --disable
```

자세한 내용은 RHOSP 설명서에서 마이그레이션 준비를 참조하십시오.

프로세스

다음 명령을 실행하여 클러스터의 컨트롤 플레인 시스템을 나열합니다.

```shell-session
$ oc get machines \
  -l machine.openshift.io/cluster-api-machine-role==master \
  -n openshift-machine-api
```

다음 명령을 실행하여 컨트롤 플레인 시스템을 삭제합니다.

```shell-session
$ oc delete machine \
  -n openshift-machine-api \
  <control_plane_machine_name>
```

1. 삭제할 컨트롤 플레인 시스템의 이름을 지정합니다.

참고

여러 컨트롤 플레인 시스템을 삭제하면 컨트롤 플레인 머신 세트가 구성된 업데이트 전략에 따라 이를 대체합니다.

기본 `RollingUpdate` 업데이트 전략을 사용하는 클러스터의 경우 Operator는 각 머신이 교체될 때까지 한 번에 하나의 머신을 교체합니다.

`OnDelete` 업데이트 전략을 사용하도록 구성된 클러스터의 경우 Operator는 필요한 모든 대체 머신을 동시에 생성합니다.

두 전략 모두 컨트롤 플레인 머신 교체 중에 etcd 상태를 유지합니다.

#### 10.3.3. 추가 리소스

컨트롤 플레인 머신 세트 구성

공급자별 구성 옵션

### 10.4. 컨트롤 플레인 머신 세트 구성

이 예제 YAML 스니펫에서는 컨트롤 플레인 머신 세트 CR(사용자 정의 리소스)의 기본 구조를 보여줍니다.

#### 10.4.1. 컨트롤 플레인 머신 세트 사용자 정의 리소스의 샘플 YAML

`ControlPlaneMachineSet` CR의 기반은 모든 플랫폼에 대해 동일한 방식으로 구성됩니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
  replicas: 3
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-cluster: <cluster_id>
      machine.openshift.io/cluster-api-machine-role: master
      machine.openshift.io/cluster-api-machine-type: master
  state: Active
  strategy:
    type: RollingUpdate
  template:
    machineType: machines_v1beta1_machine_openshift_io
    machines_v1beta1_machine_openshift_io:
      failureDomains:
        platform: <platform>
        <platform_failure_domains>
      metadata:
        labels:
          machine.openshift.io/cluster-api-cluster: <cluster_id>
          machine.openshift.io/cluster-api-machine-role: master
          machine.openshift.io/cluster-api-machine-type: master
      spec:
        providerSpec:
          value:
            <platform_provider_spec>
```

1. `cluster` 인 `ControlPlaneMachineSet` CR의 이름을 지정합니다. 이 값은 변경하지 마십시오.

2. 컨트롤 플레인 시스템의 수를 지정합니다. 컨트롤 플레인 시스템이 3개인 클러스터만 지원되므로 `replicas` 값은 `3` 입니다. 수평 스케일링은 지원되지 않습니다. 이 값은 변경하지 마십시오.

3. 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID를 지정합니다. `ControlPlaneMachineSet` CR을 생성할 때 이 값을 지정해야 합니다. OpenShift CLI () 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell
oc
```

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

4. Operator 상태를 지정합니다. 상태가 `Inactive` 이면 Operator가 작동하지 않습니다. 값을 `Active` 로 설정하여 Operator를 활성화할 수 있습니다.

중요

Operator를 활성화하기 전에 클러스터 요구 사항에 대해 `ControlPlaneMachineSet` CR 구성이 올바른지 확인해야 합니다. 컨트롤 플레인 머신 세트 Operator 활성화에 대한 자세한 내용은 "컨트롤 플레인 머신 세트 시작하기"를 참조하십시오.

5. 클러스터의 업데이트 전략을 지정합니다. 허용되는 값은 `OnDelete` 및 `RollingUpdate` 입니다. 기본값은 `RollingUpdate` 입니다. 업데이트 전략에 대한 자세한 내용은 "컨트롤 플레인 구성 업그레이드"를 참조하십시오.

6. 클라우드 공급자 플랫폼 이름을 지정합니다. 이 값은 변경하지 마십시오.

7. 클러스터의 `<platform_failure_domains>` 구성을 지정합니다. 이 섹션의 형식과 값은 공급자에 따라 다릅니다. 자세한 내용은 클라우드 공급자에 대한 샘플 실패 도메인 구성을 참조하십시오.

8. 클러스터의 `<platform_provider_spec>` 구성을 지정합니다. 이 섹션의 형식과 값은 공급자에 따라 다릅니다. 자세한 내용은 클라우드 공급자의 샘플 공급자 사양을 참조하십시오.

추가 리소스

컨트롤 플레인 머신 세트 시작하기

컨트롤 플레인 구성 업데이트

#### 10.4.2. 컨트롤 플레인 머신 세트 구성 옵션

필요에 따라 클러스터를 사용자 지정하도록 컨트롤 플레인 머신 세트를 구성할 수 있습니다.

#### 10.4.2.1. 컨트롤 플레인 머신 이름에 사용자 정의 접두사 추가

컨트롤 플레인 머신 세트에서 생성하는 머신 이름의 접두사를 사용자 지정할 수 있습니다. 이 작업은 `ControlPlaneMachineSet` 사용자 정의 리소스(CR)를 편집하여 수행할 수 있습니다.

프로세스

다음 명령을 실행하여 `ControlPlaneMachineSet` CR을 편집합니다.

```shell-session
$ oc edit controlplanemachineset.machine.openshift.io cluster \
  -n openshift-machine-api
```

`ControlPlaneMachineSet` CR의 `.spec.machineNamePrefix` 필드를 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
  machineNamePrefix: <machine_prefix>
# ...
```

여기서 `<machine_prefix` >는 소문자 RFC 1123 하위 도메인에 대한 요구 사항을 따르는 접두사 이름을 지정합니다.

중요

소문자 RFC 1123 하위 도메인은 소문자 영숫자, 하이픈('-') 및 마침표(.')로만 구성되어야 합니다. 마침표로 구분된 각 블록은 영숫자 문자로 시작하고 끝나야 합니다. 하이픈은 블록 시작 또는 종료 시 허용되지 않으며 연속 기간은 허용되지 않습니다.

변경 사항을 저장하십시오.

다음 단계

`machineNamePrefix` 매개변수 값만 변경한 경우 기본 `RollingUpdate` 업데이트 전략을 사용하는 클러스터는 자동으로 업데이트되지 않습니다. 이 변경 사항을 전파하려면 클러스터의 업데이트 전략에 관계없이 컨트롤 플레인 시스템을 수동으로 교체해야 합니다. 자세한 내용은 "컨트롤 플레인 시스템 교체"를 참조하십시오.

추가 리소스

컨트롤 플레인 시스템 교체

#### 10.4.3. 공급자별 구성 옵션

컨트롤 플레인 머신 세트 매니페스트의 `<platform_provider_spec>` 및 `<platform_failure_domains>` 섹션은 공급자마다 다릅니다. 클러스터의 공급자별 구성 옵션은 다음 리소스를 참조하십시오.

Amazon Web Services의 컨트롤 플레인 구성 옵션

Google Cloud의 컨트롤 플레인 구성 옵션

Microsoft Azure의 컨트롤 플레인 구성 옵션

Nutanix의 컨트롤 플레인 구성 옵션

RHOSP(Red Hat OpenStack Platform)의 컨트롤 플레인 구성 옵션

VMware vSphere의 컨트롤 플레인 구성 옵션

#### 10.5.1. Amazon Web Services의 컨트롤 플레인 구성 옵션

AWS(Amazon Web Services) 컨트롤 플레인 머신의 구성을 변경하고 컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다. 컨트롤 플레인 머신 세트에 대한 업데이트를 저장하면 컨트롤 플레인 머신 세트 Operator가 구성된 업데이트 전략에 따라 컨트롤 플레인 시스템을 업데이트합니다.

#### 10.5.1.1. Amazon Web Services 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 스니펫에서는 AWS 클러스터의 공급자 사양 및 실패 도메인 구성을 보여줍니다.

#### 10.5.1.1.1. 샘플 AWS 공급자 사양

기존 클러스터에 대한 컨트롤 플레인 머신 세트를 생성할 때 공급자 사양은 설치 프로그램이 생성하는 컨트롤 플레인 머신 CR(사용자 정의 리소스)의 `providerSpec` 구성과 일치해야 합니다. CR의 실패 도메인 섹션에 설정된 필드를 생략할 수 있습니다.

다음 예에서 < `cluster_id` >는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
      spec:
        providerSpec:
          value:
            ami:
              id: ami-<ami_id_string>
            apiVersion: machine.openshift.io/v1beta1
            blockDevices:
            - ebs:
                encrypted: true
                iops: 0
                kmsKey:
                  arn: ""
                volumeSize: 120
                volumeType: gp3
            credentialsSecret:
              name: aws-cloud-credentials
            deviceIndex: 0
            iamInstanceProfile:
              id: <cluster_id>-master-profile
            instanceType: m6i.xlarge
            kind: AWSMachineProviderConfig
            loadBalancers:
            - name: <cluster_id>-int
              type: network
            - name: <cluster_id>-ext
              type: network
            metadata:
              creationTimestamp: null
            metadataServiceOptions: {}
            placement:
              region: <region>
              availabilityZone: ""
              tenancy:
            securityGroups:
            - filters:
              - name: tag:Name
                values:
                - <cluster_id>-master-sg
            subnet: {}
            userDataSecret:
              name: master-user-data
```

1. 클러스터의 RHCOS(Red Hat Enterprise Linux CoreOS) AMI(Amazon Machine Images) ID를 지정합니다. AMI는 클러스터와 동일한 리전에 속해 있어야 합니다. AWS Marketplace 이미지를 사용하려면 해당 리전의 AMI ID를 받으려면 AWS Marketplace 에서 OpenShift Container Platform 서브스크립션을 완료해야 합니다.

2. 암호화된 EBS 볼륨의 구성을 지정합니다.

3. 클러스터의 시크릿 이름을 지정합니다. 이 값은 변경하지 마십시오.

4. AWS IAM(Identity and Access Management) 인스턴스 프로필을 지정합니다. 이 값은 변경하지 마십시오.

5. 컨트롤 플레인의 AWS 인스턴스 유형을 지정합니다.

6. 클라우드 공급자 플랫폼 유형을 지정합니다. 이 값은 변경하지 마십시오.

7. 클러스터의 내부(`int`) 및 외부(`ext`) 로드 밸런서를 지정합니다.

참고

프라이빗 OpenShift Container Platform 클러스터에서 외부(`ext`) 로드 밸런서 매개변수를 생략할 수 있습니다.

8. AWS에서 컨트롤 플레인 인스턴스를 생성할 위치를 지정합니다.

9. 클러스터의 AWS 리전을 지정합니다.

10. 이 매개변수는 실패 도메인에 구성되며 여기에 빈 값으로 표시됩니다. 이 매개변수에 지정된 값이 실패 도메인의 값과 다른 경우 컨트롤 플레인 머신 세트 Operator는 실패 도메인의 값으로 이를 덮어씁니다.

11. 컨트롤 플레인에 대한 AWS Dedicated 인스턴스 구성을 지정합니다. 자세한 내용은 Dedicated Instances 에 대한 AWS 설명서를 참조하십시오. 다음 값이 유효합니다.

`Default`: Dedicated 인스턴스는 공유 하드웨어에서 실행됩니다.

`전용`: Dedicated 인스턴스는 단일 테넌트 하드웨어에서 실행됩니다.

`호스트`: Dedicated 인스턴스는 제어할 수 있는 구성이 있는 격리된 서버인 전용 호스트에서 실행됩니다.

12. 컨트롤 플레인 시스템 보안 그룹을 지정합니다.

13. 이 매개변수는 실패 도메인에 구성되며 여기에 빈 값으로 표시됩니다. 이 매개변수에 지정된 값이 실패 도메인의 값과 다른 경우 컨트롤 플레인 머신 세트 Operator는 실패 도메인의 값으로 이를 덮어씁니다.

참고

실패 도메인 구성이 값을 지정하지 않으면 공급자 사양의 값이 사용됩니다. 실패 도메인에서 서브넷을 구성하면 공급자 사양의 서브넷 값이 덮어씁니다.

14. 컨트롤 플레인 사용자 데이터 시크릿을 지정합니다. 이 값은 변경하지 마십시오.

#### 10.5.1.1.2. 샘플 AWS 실패 도메인 구성

실패 도메인의 컨트롤 플레인 머신 세트 개념은 가용성 영역(AZ) 의 기존 AWS 개념과 유사합니다. `ControlPlaneMachineSet` CR은 가능한 경우 컨트롤 플레인 시스템을 여러 개의 장애 도메인에 분배합니다.

컨트롤 플레인 머신 세트에서 AWS 실패 도메인을 구성할 때 사용할 가용성 영역 이름과 서브넷을 지정해야 합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    machines_v1beta1_machine_openshift_io:
      failureDomains:
        aws:
        - placement:
            availabilityZone: <aws_zone_a>
          subnet:
            filters:
            - name: tag:Name
              values:
              - <cluster_id>-private-<aws_zone_a>
            type: Filters
        - placement:
            availabilityZone: <aws_zone_b>
          subnet:
            filters:
            - name: tag:Name
              values:
              - <cluster_id>-private-<aws_zone_b>
            type: Filters
        platform: AWS
# ...
```

1. 첫 번째 실패 도메인의 AWS 가용성 영역을 지정합니다.

2. 서브넷 구성을 지정합니다. 이 예에서 subnet 유형은 `Filters` 이므로 `filters` 스탠자가 있습니다.

3. 인프라 ID 및 AWS 가용성 영역을 사용하여 첫 번째 실패 도메인의 서브넷 이름을 지정합니다.

4. 서브넷 유형을 지정합니다. 허용되는 값은 `ARN`, `Filters` 및 `ID` 입니다. 기본값은 `Filters` 입니다.

5. 인프라 ID 및 AWS 가용성 영역을 사용하여 추가 실패 도메인의 서브넷 이름을 지정합니다.

6. 추가 장애 도메인의 클러스터 인프라 ID 및 AWS 가용성 영역을 지정합니다.

7. 클라우드 공급자 플랫폼 이름을 지정합니다. 이 값은 변경하지 마십시오.

#### 10.5.1.2. 컨트롤 플레인 시스템에 대한 Amazon Web Services 기능 활성화

컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다.

#### 10.5.1.2.1. API 서버를 프라이빗으로 제한

AWS(Amazon Web Services)에 클러스터를 배포한 후 프라이빗 영역만 사용하도록 API 서버를 재구성할 수 있습니다.

사전 요구 사항

OpenShift CLI ()를 설치합니다.

```shell
oc
```

`admin` 권한이 있는 사용자로 웹 콘솔에 액세스합니다.

프로세스

클라우드 공급자의 웹 포털 또는 콘솔에서 다음 작업을 수행합니다.

적절한 로드 밸런서 구성 요소를 찾아서 삭제합니다.

AWS 클러스터: 외부 로드 밸런서를 삭제합니다. 프라이빗 영역의 API DNS 항목은 동일한 설정을 사용하는 내부 로드 밸런서를 가리키므로 내부 로드 밸런서를 변경할 필요가 없습니다.

퍼블릭 영역의 `api.$clustername.$yourdomain` DNS 항목을 삭제합니다.

컨트롤 플레인 머신 세트 사용자 정의 리소스에서 다음 표시된 행을 삭제하여 외부 로드 밸런서를 제거합니다.

```yaml
# ...
providerSpec:
  value:
# ...
    loadBalancers:
    - name: lk4pj-ext
      type: network
    - name: lk4pj-int
      type: network
# ...
```

1. `-ext` 로 끝나는 외부 로드 밸런서의 `name` 값을 삭제합니다.

2. 외부 로드 밸런서의 `유형` 값을 삭제합니다.

추가 리소스

Ingress 컨트롤러 끝점에서 내부로 범위 게시 구성

#### 10.5.1.2.2. 컨트롤 플레인 머신 세트를 사용하여 Amazon Web Services 인스턴스 유형 변경

컨트롤 플레인 머신 세트 CR(사용자 정의 리소스)에서 사양을 업데이트하여 컨트롤 플레인 시스템에서 사용하는 AWS(Amazon Web Services) 인스턴스 유형을 변경할 수 있습니다.

사전 요구 사항

AWS 클러스터는 컨트롤 플레인 머신 세트를 사용합니다.

프로세스

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
providerSpec:
  value:
    ...
    instanceType: <compatible_aws_instance_type>
```

1. 이전 선택과 동일한 기준으로 더 큰 AWS 인스턴스 유형을 지정합니다. 예를 들어 `m6i.xlarge` 를 `m6i.2xlarge` 또는 `m6i.4xlarge` 로 변경할 수 있습니다.

변경 사항을 저장하십시오.

#### 10.5.1.2.3. 머신 세트를 사용하여 Elastic Fabric Adapter 인스턴스에 대한 배치 그룹에 머신 할당

기존 AWS 배치 그룹 내에서 EBS(Elastic Fabric Adapter) 인스턴스에 머신을 배포하도록 머신 세트를 구성할 수 있습니다.

EFA 인스턴스에는 배치 그룹이 필요하지 않으며 EFA 구성 이외의 용도로 배치 그룹을 사용할 수 있습니다. 이 예에서는 둘 다 사용하여 지정된 배치 그룹 내의 시스템의 네트워크 성능을 향상시킬 수 있는 구성을 보여줍니다.

사전 요구 사항

AWS 콘솔에 배치 그룹을 생성하셨습니다.

참고

생성하는 배치 그룹 유형에 대한 규칙 및 제한 사항이 의도한 사용 사례와 호환되는지 확인합니다. 컨트롤 플레인 머신 세트는 가능한 경우 컨트롤 플레인 시스템을 여러 개의 장애 도메인에 분배합니다. 컨트롤 플레인에 배치 그룹을 사용하려면 여러 가용 영역에 걸쳐 있는 배치 그룹 유형을 사용해야 합니다.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          instanceType: <supported_instance_type>
          networkInterfaceType: EFA
          placement:
            availabilityZone: <zone>
            region: <region>
          placementGroupName: <placement_group>
          placementGroupPartition: <placement_group_partition_number>
# ...
```

1. EFA를 지원하는 인스턴스 유형을 지정합니다.

2. `EFA` 네트워크 인터페이스 유형을 지정합니다.

3. 영역을 지정합니다(예: `us-east-1a`).

4. 리전을 지정합니다(예: `us-east-1`).

5. 머신을 배포할 기존 AWS 배치 그룹의 이름을 지정합니다.

6. 선택 사항: 시스템을 배포할 기존 AWS 배치 그룹의 파티션 번호를 지정합니다.

검증

AWS 콘솔에서 머신 세트가 생성된 머신을 찾아 머신 속성에서 다음을 확인합니다.

placement group 필드에는 시스템 세트의 `placementGroupName` 매개변수에 대해 지정한 값이 있습니다.

파티션 번호 필드에는 머신 세트의 `placementGroup Cryostat` 매개변수에 대해 지정한 값이 있습니다.

interface 유형 필드는 EFA를 사용함을 나타냅니다.

#### 10.5.1.2.4. Amazon EC2 인스턴스 메타데이터 서비스에 대한 머신 세트 옵션

머신 세트를 사용하여 특정 버전의 Amazon EC2 인스턴스 메타데이터 서비스(IMDS)를 사용하는 머신을 생성할 수 있습니다. 머신 세트는 IMDSv1 및 IMDSv2 또는 IMDSv2 를 사용해야 하는 머신을 생성할 수 있습니다.

참고

OpenShift Container Platform 버전 4.6 또는 이전 버전으로 생성된 AWS 클러스터에서 IMDSv2를 사용하려면 부팅 이미지를 업데이트해야 합니다. 자세한 내용은 "업데이트된 부팅 이미지"를 참조하십시오.

중요

IMDSv2가 필요한 머신을 생성하도록 머신 세트를 구성하기 전에 AWS 메타데이터 서비스와 상호 작용하는 모든 워크로드가 IMDSv2를 지원하는지 확인합니다.

추가 리소스

업데이트된 부팅 이미지

#### 10.5.1.2.4.1. 머신 세트를 사용하여 IMDS 구성

머신의 머신 세트 YAML 파일에서 `metadataServiceOptions.authentication` 값을 추가하거나 편집하여 IMDSv2의 사용이 필요한지 여부를 지정할 수 있습니다.

사전 요구 사항

IMDSv2를 사용하려면 OpenShift Container Platform 버전 4.7 이상을 사용하여 AWS 클러스터가 생성되어 있어야 합니다.

프로세스

`providerSpec` 필드 아래에 다음 행을 추가하거나 편집합니다.

```yaml
providerSpec:
  value:
    metadataServiceOptions:
      authentication: Required
```

1. IMDSv2를 요구하려면 매개 변수 값을 `Required` 로 설정합니다. IMDSv1 및 IMDSv2를 모두 사용할 수 있도록 하려면 매개 변수 값을 `Optional` 로 설정합니다. 값을 지정하지 않으면 IMDSv1 및 IMDSv2가 모두 허용됩니다.

#### 10.5.1.2.5. 머신을 Dedicated 인스턴스로 배포하는 머신 세트

AWS에서 실행 중인 머신 세트를 생성하여 머신을 Dedicated 인스턴스로 배포할 수 있습니다. Dedicated 인스턴스는 단일 고객 전용 하드웨어의 VPC(가상 프라이빗 클라우드)에서 실행됩니다. 이러한 Amazon EC2 인스턴스는 호스트 하드웨어 수준에서 물리적으로 분리됩니다. Dedicated 인스턴스의 분리는 인스턴스가 하나의 유료 계정에 연결된 다른 AWS 계정에 속하는 경우에도 발생합니다. 하지만 전용이 아닌 다른 인스턴스는 동일한 AWS 계정에 속하는 경우 Dedicated 인스턴스와 하드웨어를 공유할 수 있습니다.

공용 또는 전용 테넌시가 있는 인스턴스는 Machine API에서 지원됩니다. 공용 테넌시가 있는 인스턴스는 공유 하드웨어에서 실행됩니다. 공용 테넌시는 기본 테넌시입니다. 전용 테넌트가 있는 인스턴스는 단일 테넌트 하드웨어에서 실행됩니다.

#### 10.5.1.2.5.1. 머신 세트를 사용하여 Dedicated 인스턴스 생성

Machine API 통합을 사용하여 Dedicated 인스턴스에서 지원하는 머신을 실행할 수 있습니다. 머신 세트 YAML 파일의 `tenancy` 필드를 설정하여 AWS에서 전용 인스턴스를 시작합니다.

프로세스

`providerSpec` 필드에서 전용 테넌트를 지정합니다.

```yaml
providerSpec:
  placement:
    tenancy: dedicated
```

#### 10.5.1.2.6. 머신 세트를 사용하여 용량 예약 구성

OpenShift Container Platform 버전 4.20 이상에서는 온디맨드 용량 예약 및 ML의 용량 블록을 포함하여 Amazon Web Services 클러스터에서 용량 예약을 지원합니다.

사용자가 정의한 용량 요청의 매개변수와 일치하는 사용 가능한 리소스에 머신을 배포하도록 머신 세트를 구성할 수 있습니다. 이러한 매개변수는 예약할 인스턴스 유형, 리전 및 인스턴스 수를 지정합니다. 용량 예약이 용량 요청을 수용할 수 있는 경우 배포에 성공합니다.

이 AWS 오퍼링에 대한 제한 사항 및 제안된 사용 사례를 포함한 자세한 내용은 AWS 문서의 온디맨드 용량 예약 및 ML 용량 블록을 참조하십시오.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

온디맨드 용량 예약 또는 ML의 용량 블록을 구입하셨습니다. 자세한 내용은 AWS 문서의 온디맨드 용량 예약 및 ML 용량 블록을 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    machines_v1beta1_machine_openshift_io:
      spec:
        providerSpec:
          value:
            capacityReservationId: <capacity_reservation>
            marketType: <market_type>
# ...
```

1. 머신 세트에서 머신을 배포할 ML 또는 온 디맨드 용량 예약의 용량 블록 ID를 지정합니다.

2. 사용할 시장 유형을 지정합니다. 다음 값이 유효합니다.

`CapacityBlock`

ML 용 용량 블록과 함께 이 시장 유형을 사용합니다.

`OnDemand`

온디맨드 용량 예약과 함께 이 시장 유형을 사용합니다.

검증

시스템 배포를 확인하려면 다음 명령을 실행하여 머신 세트에서 생성한 머신을 나열합니다.

```shell-session
$ oc get machine \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machine-role=master
```

출력에서 나열된 시스템의 특성이 용량 예약의 매개변수와 일치하는지 확인합니다.

#### 10.5.2. Microsoft Azure의 컨트롤 플레인 구성 옵션

컨트롤 플레인 머신 세트의 구성을 변경하고 컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다. 컨트롤 플레인 머신 세트에 대한 업데이트를 저장하면 컨트롤 플레인 머신 세트 Operator가 구성된 업데이트 전략에 따라 컨트롤 플레인 시스템을 업데이트합니다.

#### 10.5.2.1. Microsoft Azure 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 스니펫에서는 Azure 클러스터의 공급자 사양 및 실패 도메인 구성을 보여줍니다.

#### 10.5.2.1.1. Azure 공급자 사양 샘플

기존 클러스터에 대한 컨트롤 플레인 머신 세트를 생성할 때 공급자 사양은 설치 프로그램에서 생성한 컨트롤 플레인 `Machine` CR의 `providerSpec` 구성과 일치해야 합니다. CR의 실패 도메인 섹션에 설정된 필드를 생략할 수 있습니다.

다음 예에서 < `cluster_id` >는 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
      spec:
        providerSpec:
          value:
            acceleratedNetworking: true
            apiVersion: machine.openshift.io/v1beta1
            credentialsSecret:
              name: azure-cloud-credentials
              namespace: openshift-machine-api
            diagnostics: {}
            image:
              offer: ""
              publisher: ""
              resourceID: /resourceGroups/<cluster_id>-rg/providers/Microsoft.Compute/galleries/gallery_<cluster_id>/images/<cluster_id>-gen2/versions/412.86.20220930
              sku: ""
              version: ""
            internalLoadBalancer: <cluster_id>-internal
            kind: AzureMachineProviderSpec
            location: <region>
            managedIdentity: <cluster_id>-identity
            metadata:
              creationTimestamp: null
              name: <cluster_id>
            networkResourceGroup: <cluster_id>-rg
            osDisk:
              diskSettings: {}
              diskSizeGB: 1024
              managedDisk:
                storageAccountType: Premium_LRS
              osType: Linux
            publicIP: false
            publicLoadBalancer: <cluster_id>
            resourceGroup: <cluster_id>-rg
            subnet: <cluster_id>-master-subnet
            userDataSecret:
              name: master-user-data
            vmSize: Standard_D8s_v3
            vnet: <cluster_id>-vnet
            zone: "1"
```

1. 클러스터의 시크릿 이름을 지정합니다. 이 값은 변경하지 마십시오.

2. 컨트롤 플레인 머신 세트의 이미지 세부 정보를 지정합니다.

3. 인스턴스 유형과 호환되는 이미지를 지정합니다. 설치 프로그램에서 생성한 Hyper-V generation V2 이미지에는 `-gen2` 접미사가 있지만 V1 이미지의 접미사 없이 이름이 동일합니다.

4. 컨트롤 플레인의 내부 로드 밸런서를 지정합니다. 이 필드는 사전 구성되지 않을 수 있지만 `ControlPlaneMachineSet` 및 컨트롤 플레인 `Machine` CR 모두에 필요합니다.

5. 클라우드 공급자 플랫폼 유형을 지정합니다. 이 값은 변경하지 마십시오.

6. 컨트롤 플레인 시스템을 배치할 리전을 지정합니다.

7. 컨트롤 플레인의 디스크 구성을 지정합니다.

8. 컨트롤 플레인의 공용 로드 밸런서를 지정합니다.

참고

사용자 정의 아웃 바운드 라우팅이 있는 프라이빗 OpenShift Container Platform 클러스터에서 `publicLoadBalancer` 매개변수를 생략할 수 있습니다.

9. 컨트롤 플레인의 서브넷을 지정합니다.

10. 컨트롤 플레인 사용자 데이터 시크릿을 지정합니다. 이 값은 변경하지 마십시오.

11. 모든 장애 도메인에 단일 영역을 사용하는 클러스터의 영역 구성을 지정합니다.

참고

클러스터가 각 장애 도메인에 다른 영역을 사용하도록 구성된 경우 이 매개변수는 실패 도메인에 구성됩니다. 각 장애 도메인에 다른 영역을 사용할 때 공급자 사양에 이 값을 지정하면 컨트롤 플레인 머신 세트 Operator에서 해당 영역을 무시합니다.

#### 10.5.2.1.2. 샘플 Azure 실패 도메인 구성

실패 도메인의 컨트롤 플레인 머신 세트 개념은 Azure 가용성 영역의 기존 Azure 개념과 유사합니다. `ControlPlaneMachineSet` CR은 가능한 경우 컨트롤 플레인 시스템을 여러 개의 장애 도메인에 분배합니다.

컨트롤 플레인 머신 세트에서 Azure 장애 도메인을 구성할 때 가용성 영역 이름을 지정해야 합니다. Azure 클러스터는 여러 영역에 걸쳐 있는 단일 서브넷을 사용합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    machines_v1beta1_machine_openshift_io:
      failureDomains:
        azure:
        - zone: "1"
        - zone: "2"
        - zone: "3"
        platform: Azure
# ...
```

1. `영역` 의 각 인스턴스는 장애 도메인의 Azure 가용성 영역을 지정합니다.

참고

클러스터가 모든 장애 도메인에 단일 영역을 사용하도록 구성된 경우 `zone` 매개변수는 실패 도메인 구성 대신 공급자 사양에 구성됩니다.

2. 클라우드 공급자 플랫폼 이름을 지정합니다. 이 값은 변경하지 마십시오.

#### 10.5.2.2. 컨트롤 플레인 시스템에 대한 Microsoft Azure 기능 활성화

컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다.

#### 10.5.2.2.1. API 서버를 프라이빗으로 제한

AWS(Amazon Web Services)에 클러스터를 배포한 후 프라이빗 영역만 사용하도록 API 서버를 재구성할 수 있습니다.

사전 요구 사항

OpenShift CLI ()를 설치합니다.

```shell
oc
```

`admin` 권한이 있는 사용자로 웹 콘솔에 액세스합니다.

프로세스

클라우드 공급자의 웹 포털 또는 콘솔에서 다음 작업을 수행합니다.

적절한 로드 밸런서 구성 요소를 찾아서 삭제합니다.

퍼블릭 영역의 `api.$clustername.$yourdomain` DNS 항목을 삭제합니다.

컨트롤 플레인 머신 세트 사용자 정의 리소스에서 다음 표시된 행을 삭제하여 외부 로드 밸런서를 제거합니다.

```yaml
# ...
providerSpec:
  value:
# ...
    loadBalancers:
    - name: lk4pj-ext
      type: network
    - name: lk4pj-int
      type: network
# ...
```

1. `-ext` 로 끝나는 외부 로드 밸런서의 `name` 값을 삭제합니다.

2. 외부 로드 밸런서의 `유형` 값을 삭제합니다.

추가 리소스

Ingress 컨트롤러 끝점에서 내부로 범위 게시 구성

#### 10.5.2.2.2. Azure Marketplace 오퍼링 사용

Azure에서 실행되는 머신 세트를 생성하여 Azure Marketplace 오퍼링을 사용하는 머신을 배포할 수 있습니다. 이 오퍼링을 사용하려면 먼저 Azure Marketplace 이미지를 가져와야 합니다. 이미지를 가져올 때 다음을 고려하십시오.

이미지가 동일하지만 Azure Marketplace 게시자는 지역에 따라 다릅니다. 북미에 있는 경우 게시자로 `redhat` 을 지정합니다. EMEA에 있는 경우 게시자로 `redhat-limited` 를 지정합니다.

이 제안에는 `rh-ocp-worker` SKU 및 `rh-ocp-worker-gen1` SKU가 포함됩니다. `rh-ocp-worker` SKU는 Hyper-V 생성 버전 2 VM 이미지를 나타냅니다. OpenShift Container Platform에서 사용되는 기본 인스턴스 유형은 버전 2와 호환됩니다. 버전 1과 호환되는 인스턴스 유형을 사용하려면 `rh-ocp-worker-gen1` SKU와 연결된 이미지를 사용합니다. `rh-ocp-worker-gen1` SKU는 Hyper-V 버전 1 VM 이미지를 나타냅니다.

중요

Azure Marketplace를 사용하여 이미지 설치는 64비트 ARM 인스턴스가 있는 클러스터에서 지원되지 않습니다.

Azure Marketplace 이미지를 사용하도록 컴퓨팅 머신의 RHCOS 이미지만 수정해야 합니다. 컨트롤 플레인 머신 및 인프라 노드에는 OpenShift Container Platform 서브스크립션이 필요하지 않으며 기본적으로 공용 RHCOS 기본 이미지를 사용하므로 Azure에서 서브스크립션 비용이 발생하지 않습니다. 따라서 클러스터 기본 부팅 이미지 또는 컨트롤 플레인 부팅 이미지를 수정해서는 안 됩니다. Azure Marketplace 이미지를 적용하면 복구할 수 없는 추가 라이센싱 비용이 발생합니다.

사전 요구 사항

Azure CLI 클라이언트 `(az)` 를 설치했습니다.

Azure 계정은 제공할 수 있으며 Azure CLI 클라이언트를 사용하여 이 계정에 로그인했습니다.

프로세스

다음 명령 중 하나를 실행하여 사용 가능한 모든 OpenShift Container Platform 이미지를 표시합니다.

```shell-session
$  az vm image list --all --offer rh-ocp-worker --publisher redhat -o table
```

```shell-session
Offer          Publisher       Sku                 Urn                                                             Version
-------------  --------------  ------------------  --------------------------------------------------------------  -----------------
rh-ocp-worker  RedHat          rh-ocp-worker       RedHat:rh-ocp-worker:rh-ocp-worker:4.17.2024100419              4.17.2024100419
rh-ocp-worker  RedHat          rh-ocp-worker-gen1  RedHat:rh-ocp-worker:rh-ocp-worker-gen1:4.17.2024100419         4.17.2024100419
```

```shell-session
$  az vm image list --all --offer rh-ocp-worker --publisher redhat-limited -o table
```

```shell-session
Offer          Publisher       Sku                 Urn                                                                     Version
-------------  --------------  ------------------  --------------------------------------------------------------          -----------------
rh-ocp-worker  redhat-limited  rh-ocp-worker       redhat-limited:rh-ocp-worker:rh-ocp-worker:4.17.2024100419              4.17.2024100419
rh-ocp-worker  redhat-limited  rh-ocp-worker-gen1  redhat-limited:rh-ocp-worker:rh-ocp-worker-gen1:4.17.2024100419         4.17.2024100419
```

참고

컴퓨팅 및 컨트롤 플레인 노드에 사용할 수 있는 최신 이미지를 사용합니다. 필요한 경우 설치 프로세스의 일부로 VM이 자동으로 업그레이드됩니다.

다음 명령 중 하나를 실행하여 제안의 이미지를 검사합니다.

```shell-session
$ az vm image show --urn redhat:rh-ocp-worker:rh-ocp-worker:<version>
```

```shell-session
$ az vm image show --urn redhat-limited:rh-ocp-worker:rh-ocp-worker:<version>
```

다음 명령 중 하나를 실행하여 제안 조건을 검토합니다.

```shell-session
$ az vm image terms show --urn redhat:rh-ocp-worker:rh-ocp-worker:<version>
```

```shell-session
$ az vm image terms show --urn redhat-limited:rh-ocp-worker:rh-ocp-worker:<version>
```

다음 명령 중 하나를 실행하여 제공 조건을 수락하십시오.

```shell-session
$ az vm image terms accept --urn redhat:rh-ocp-worker:rh-ocp-worker:<version>
```

```shell-session
$ az vm image terms accept --urn redhat-limited:rh-ocp-worker:rh-ocp-worker:<version>
```

제안의 이미지 세부 정보, 특히 `publisher`, `offer`, `sku`, `version` 값을 기록합니다.

제안의 이미지 세부 정보를 사용하여 머신 세트 YAML 파일의 `providerSpec` 섹션에 다음 매개변수를 추가합니다.

```yaml
providerSpec:
  value:
    image:
      offer: rh-ocp-worker
      publisher: redhat
      resourceID: ""
      sku: rh-ocp-worker
      type: MarketplaceWithPlan
      version: 413.92.2023101700
```

#### 10.5.2.2.3. Azure 부팅 진단 활성화

머신 세트에서 생성하는 Azure 머신에서 부팅 진단을 활성화할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

스토리지 유형에 적용할 수 있는 `diagnostics` 구성을 머신 세트 YAML 파일의 `providerSpec` 필드에 추가합니다.

```yaml
providerSpec:
  diagnostics:
    boot:
      storageAccountType: AzureManaged
```

1. Azure 관리 스토리지 계정을 지정합니다.

```yaml
providerSpec:
  diagnostics:
    boot:
      storageAccountType: CustomerManaged
      customerManaged:
        storageAccountURI: https://<storage-account>.blob.core.windows.net
```

1. Azure Unmanaged 스토리지 계정을 지정합니다.

2. `<storage-account>` 를 스토리지 계정 이름으로 바꿉니다.

참고

Azure Blob Storage 데이터 서비스만 지원됩니다.

검증

Microsoft Azure 포털에서 머신 세트에서 배포한 머신의 부팅 진단 페이지를 검토하고 시스템의 직렬 로그를 볼 수 있는지 확인합니다.

#### 10.5.2.2.4. 울트라 디스크가 있는 머신을 데이터 디스크로 배포하는 머신 세트

Azure에서 실행되는 머신 세트를 생성하여 울트라 디스크가 있는 머신을 배포할 수 있습니다. Ultra 디스크는 가장 까다로운 데이터 워크로드에 사용하기 위한 고성능 스토리지입니다.

추가 리소스

Microsoft Azure Ultra 디스크 문서

#### 10.5.2.2.4.1. 머신 세트를 사용하여 울트라 디스크가 있는 머신 생성

머신 세트 YAML 파일을 편집하여 Azure에 울트라 디스크가 있는 머신을 배포할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

다음 명령을 실행하여 `master` 데이터 시크릿을 사용하여 `openshift-machine-api` 네임스페이스에 사용자 지정 시크릿을 생성합니다.

```shell-session
$ oc -n openshift-machine-api \
get secret <role>-user-data \
--template='{{index .data.userData | base64decode}}' | jq > userData.txt
```

1. `<role>` 을 `master` 로 바꿉니다.

2. `userData.txt` 를 새 사용자 지정 시크릿의 이름으로 지정합니다.

텍스트 편집기에서 `userData.txt` 파일을 열고 파일에서 최종 `}` 문자를 찾습니다.

바로 앞의 줄에서 `,` 을 추가합니다.

뒤에 새 행을 생성하고 `,` 다음에 구성 세부 정보를 추가합니다.

```plaintext
"storage": {
  "disks": [
    {
      "device": "/dev/disk/azure/scsi1/lun0",
      "partitions": [
        {
          "label": "lun0p1",
          "sizeMiB": 1024,
          "startMiB": 0
        }
      ]
    }
  ],
  "filesystems": [
    {
      "device": "/dev/disk/by-partlabel/lun0p1",
      "format": "xfs",
      "path": "/var/lib/lun0p1"
    }
  ]
},
"systemd": {
  "units": [
    {
      "contents": "[Unit]\nBefore=local-fs.target\n[Mount]\nWhere=/var/lib/lun0p1\nWhat=/dev/disk/by-partlabel/lun0p1\nOptions=defaults,pquota\n[Install]\nWantedBy=local-fs.target\n",
      "enabled": true,
      "name": "var-lib-lun0p1.mount"
    }
  ]
}
```

1. 울트라 디스크로 노드에 연결하려는 디스크의 구성 세부 정보입니다.

2. 사용 중인 머신 세트의 `dataDisks` 스탠자에 정의된 `lun` 값을 지정합니다. 예를 들어 시스템 세트에 `lun: 0` 이 포함된 경우 `lun0` 을 지정합니다. 이 구성 파일에서 여러 `"disks"` 항목을 지정하여 여러 데이터 디스크를 초기화할 수 있습니다. 여러 개의 `"disks"` 항목을 지정하는 경우 각 항목의 `lun` 값이 머신 세트의 값과 일치하는지 확인합니다.

3. 디스크의 새 파티션의 구성 세부 정보입니다.

4. 파티션의 레이블을 지정합니다. `lun0` 의 첫 번째 파티션에 `lun0` 과 같은 계층적 이름을 사용하는 것이 유용할 수 있습니다.

5. 파티션의 총 크기(MiB)를 지정합니다.

6. 파티션을 포맷할 때 사용할 파일 시스템을 지정합니다. 파티션 레이블을 사용하여 파티션을 지정합니다.

7. 부팅 시 파티션을 마운트할 `systemd` 장치를 지정합니다. 파티션 레이블을 사용하여 파티션을 지정합니다. 이 구성 파일에서 여러 개의 `"partitions"` 항목을 지정하여 여러 파티션을 만들 수 있습니다. 여러 개의 `"partitions"` 항목을 지정하는 경우 각각에 대해 `systemd` 장치를 지정해야 합니다.

8. `Where` 는 `storage.filesystems.path` 의 값을 지정합니다. `What` 에 대해 `storage.filesystems.device` 값을 지정합니다.

다음 명령을 실행하여 template 값을 `disableTemplating.txt` 라는 파일에 추출합니다.

```shell-session
$ oc -n openshift-machine-api get secret <role>-user-data \
--template='{{index .data.disableTemplating | base64decode}}' | jq > disableTemplating.txt
```

1. `<role>` 을 `master` 로 바꿉니다.

`userData.txt` 파일과 `disableTemplating.txt` 파일을 결합하여 다음 명령을 실행하여 데이터 시크릿 파일을 생성합니다.

```shell-session
$ oc -n openshift-machine-api create secret generic <role>-user-data-x5 \
--from-file=userData=userData.txt \
--from-file=disableTemplating=disableTemplating.txt
```

1. `<role>-user-data-x5` 의 경우 시크릿 이름을 지정합니다. `<role>` 을 `master` 로 바꿉니다.

다음 명령을 실행하여 컨트롤 플레인 머신 세트 CR을 편집합니다.

```shell-session
$ oc --namespace openshift-machine-api edit controlplanemachineset.machine.openshift.io cluster
```

표시된 위치에 다음 행을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: ControlPlaneMachineSet
spec:
  template:
    spec:
      metadata:
        labels:
          disk: ultrassd
      providerSpec:
        value:
          ultraSSDCapability: Enabled
          dataDisks:
          - nameSuffix: ultrassd
            lun: 0
            diskSizeGB: 4
            deletionPolicy: Delete
            cachingType: None
            managedDisk:
              storageAccountType: UltraSSD_LRS
          userDataSecret:
            name: <role>-user-data-x5
```

1. 이 머신 세트에서 생성한 노드를 선택하는 데 사용할 라벨을 지정합니다. 이 절차에서는 이 값에 `disk.ultrassd` 를 사용합니다.

2. 3

이 라인은 울트라 디스크를 사용할 수 있습니다. `dataDisks` 의 경우 전체 스탠자를 포함합니다.

4. 이전에 생성한 사용자 데이터 시크릿을 지정합니다. `<role>` 을 `master` 로 바꿉니다.

변경 사항을 저장하십시오.

기본 `RollingUpdate` 업데이트 전략을 사용하는 클러스터의 경우 Operator는 변경 사항을 컨트롤 플레인 구성에 자동으로 전파합니다.

`OnDelete` 업데이트 전략을 사용하도록 구성된 클러스터의 경우 컨트롤 플레인 시스템을 수동으로 교체해야 합니다.

검증

다음 명령을 실행하여 머신이 생성되었는지 확인합니다.

```shell-session
$ oc get machines
```

시스템은 `Running` 상태여야 합니다.

실행 중이고 노드가 연결된 시스템의 경우 다음 명령을 실행하여 파티션을 검증합니다.

```shell-session
$ oc debug node/<node_name> -- chroot /host lsblk
```

이 명령에서 >은 노드 < `node_name` >에서 디버깅 쉘을 시작하고 `--` --로 명령을 전달합니다. 전달된 명령 는 기본 호스트 OS 바이너리에 대한 액세스를 제공하며 `lsblk` 에는 호스트 OS 시스템에 연결된 블록 장치가 표시됩니다.

```shell
oc debug node/<node_name
```

```shell
chroot /host
```

다음 단계

컨트롤 플레인에서 울트라 디스크를 사용하려면 컨트롤 플레인의 울트라 디스크 마운트 지점을 사용하도록 워크로드를 재구성합니다.

#### 10.5.2.2.4.2. 울트라 디스크를 활성화하는 머신 세트의 리소스 문제 해결

이 섹션의 정보를 사용하여 발생할 수 있는 문제를 이해하고 복구하십시오.

#### 10.5.2.2.4.2.1. 잘못된 울트라 디스크 구성

`UltraSSDCapability` 매개변수의 잘못된 구성이 머신 세트에 지정되면 머신 프로비저닝에 실패합니다.

예를 들어 `UltraSSDCapability` 매개변수가 `Disabled` 로 설정되어 있지만 `dataDisks` 매개변수에 울트라 디스크가 지정되면 다음과 같은 오류 메시지가 표시됩니다.

```shell-session
StorageAccountType UltraSSD_LRS can be used only when additionalCapabilities.ultraSSDEnabled is set.
```

이 문제를 해결하려면 머신 세트 구성이 올바른지 확인합니다.

#### 10.5.2.2.4.2.2. 지원되지 않는 디스크 매개변수

울트라 디스크와 호환되지 않는 리전, 가용성 영역 또는 인스턴스 크기가 머신 세트에 지정되면 시스템 프로비저닝이 실패합니다. 로그에 다음 오류 메시지가 있는지 확인합니다.

```shell-session
failed to create vm <machine_name>: failure sending request for machine <machine_name>: cannot create vm: compute.VirtualMachinesClient#CreateOrUpdate: Failure sending request: StatusCode=400 -- Original Error: Code="BadRequest" Message="Storage Account type 'UltraSSD_LRS' is not supported <more_information_about_why>."
```

이 문제를 해결하려면 지원되는 환경에서 이 기능을 사용하고 있으며 머신 세트 구성이 올바른지 확인합니다.

#### 10.5.2.2.4.2.3. 디스크를 삭제할 수 없음

데이터 디스크가 예상대로 작동하지 않으므로 울트라 디스크를 삭제하면 머신이 삭제되고 데이터 디스크가 분리됩니다. 필요한 경우 고립된 디스크를 수동으로 삭제해야 합니다.

#### 10.5.2.2.5. 머신 세트의 고객 관리 암호화 키 활성화

Azure에 암호화 키를 제공하여 관리 대상 디스크의 데이터를 암호화할 수 있습니다. 시스템 API를 사용하여 고객 관리 키로 서버 측 암호화를 활성화할 수 있습니다.

고객 관리 키를 사용하려면 Azure Key Vault, 디스크 암호화 세트 및 암호화 키가 필요합니다. 디스크 암호화 세트는 CCO(Cloud Credential Operator)에 권한이 부여된 리소스 그룹에 있어야 합니다. 그렇지 않은 경우 디스크 암호화 세트에 추가 reader 역할을 부여해야 합니다.

사전 요구 사항

Azure Key Vault 인스턴스를 만듭니다.

디스크 암호화 세트의 인스턴스를 만듭니다.

key vault에 디스크 암호화 세트 액세스 권한을 부여합니다.

프로세스

머신 세트 YAML 파일의 `providerSpec` 필드에 설정된 디스크 암호화를 구성합니다. 예를 들면 다음과 같습니다.

```yaml
providerSpec:
  value:
    osDisk:
      diskSizeGB: 128
      managedDisk:
        diskEncryptionSet:
          id: /subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/providers/Microsoft.Compute/diskEncryptionSets/<disk_encryption_set_name>
        storageAccountType: Premium_LRS
```

추가 리소스

고객 관리 키에 대한 Azure 문서

#### 10.5.2.2.6. 머신 세트를 사용하여 Azure 가상 머신에 대한 신뢰할 수 있는 시작 구성

OpenShift Container Platform 4.20은 Azure VM(가상 머신)에 대한 신뢰할 수 있는 시작을 지원합니다. 머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 신뢰할 수 있는 시작 옵션을 구성할 수 있습니다. 예를 들어 Secure Boot 또는 전용 가상 신뢰할 수 있는 플랫폼 모듈(vTPM) 인스턴스와 같은 UEFI 보안 기능을 사용하도록 이러한 머신을 구성할 수 있습니다.

참고

일부 기능 조합은 잘못된 구성을 생성합니다.

| Secure Boot [1] | vTPM [2] | 유효한 구성 |
| --- | --- | --- |
| 활성화됨 | 활성화됨 | 제공됨 |
| 활성화됨 | 비활성화됨 | 제공됨 |
| 활성화됨 | 생략됨 | 제공됨 |
| 비활성화됨 | 활성화됨 | 제공됨 |
| 생략됨 | 활성화됨 | 제공됨 |
| 비활성화됨 | 비활성화됨 | 없음 |
| 생략됨 | 비활성화됨 | 없음 |
| 생략됨 | 생략됨 | 없음 |

`secureBoot` 필드 사용.

`virtualizedTrustedPlatformModule` 필드 사용

관련 기능 및 기능에 대한 자세한 내용은 Azure 가상 머신의 신뢰할 수 있는 시작에 대한 Microsoft Azure 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집하여 유효한 구성을 제공합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    machines_v1beta1_machine_openshift_io:
      spec:
        providerSpec:
          value:
            securityProfile:
              settings:
                securityType: TrustedLaunch
                trustedLaunch:
                  uefiSettings:
                    secureBoot: Enabled
                    virtualizedTrustedPlatformModule: Enabled
# ...
```

1. Azure 가상 머신에 대한 신뢰할 수 있는 시작 기능을 활성화합니다. 이 값은 모든 유효한 구성에 필요합니다.

2. 사용할 UEFI 보안 기능을 지정합니다. 이 섹션은 모든 유효한 구성에 필요합니다.

3. UEFI Secure Boot를 활성화합니다.

4. vTPM 사용을 활성화합니다.

검증

Azure 포털에서 머신 세트에서 배포한 머신의 세부 정보를 검토하고 신뢰할 수 있는 시작 옵션이 구성한 값과 일치하는지 확인합니다.

#### 10.5.2.2.7. 머신 세트를 사용하여 Azure 기밀 가상 머신 구성

OpenShift Container Platform 4.20은 Azure 기밀 가상 머신(VM)을 지원합니다.

참고

현재 기밀 VM은 64비트 ARM 아키텍처에서 지원되지 않습니다.

머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 기밀 VM 옵션을 구성할 수 있습니다. 예를 들어 Secure Boot 또는 전용 가상 신뢰할 수 있는 플랫폼 모듈(vTPM) 인스턴스와 같은 UEFI 보안 기능을 사용하도록 이러한 머신을 구성할 수 있습니다.

주의

모든 인스턴스 유형이 기밀 VM을 지원하는 것은 아닙니다. 기밀 VM을 호환되지 않는 유형으로 사용하도록 구성된 컨트롤 플레인 머신 세트의 인스턴스 유형을 변경하지 마십시오. 호환되지 않는 인스턴스 유형을 사용하면 클러스터가 불안정해질 수 있습니다.

관련 기능 및 기능에 대한 자세한 내용은 기밀 가상 머신에 대한 Microsoft Azure 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          osDisk:
            # ...
            managedDisk:
              securityProfile:
                securityEncryptionType: VMGuestStateOnly
            # ...
          securityProfile:
            settings:
                securityType: ConfidentialVM
                confidentialVM:
                  uefiSettings:
                    secureBoot: Disabled
                    virtualizedTrustedPlatformModule: Enabled
          vmSize: Standard_DC16ads_v5
# ...
```

1. 기밀 VM을 사용할 때 관리 디스크에 대한 보안 프로필 설정을 지정합니다.

2. VMGS(VM 게스트 상태) Blob의 암호화를 활성화합니다. 이 설정을 사용하려면 vTPM을 사용해야 합니다.

3. 기밀 VM의 보안 프로필 설정을 지정합니다.

4. 기밀 VM을 사용할 수 있습니다. 이 값은 모든 유효한 구성에 필요합니다.

5. 사용할 UEFI 보안 기능을 지정합니다. 이 섹션은 모든 유효한 구성에 필요합니다.

6. UEFI Secure Boot를 비활성화합니다.

7. vTPM 사용을 활성화합니다.

8. 기밀 VM을 지원하는 인스턴스 유형을 지정합니다.

검증

Azure 포털에서 머신 세트에서 배포한 머신의 세부 정보를 검토하고 기밀 VM 옵션이 구성한 값과 일치하는지 확인합니다.

#### 10.5.2.2.8. 머신 세트를 사용하여 용량 예약 구성

OpenShift Container Platform 버전 4.20 이상에서는 Microsoft Azure 클러스터에서 용량 예약 그룹을 사용하여 온디맨드 용량 예약을 지원합니다.

사용자가 정의한 용량 요청의 매개변수와 일치하는 사용 가능한 리소스에 머신을 배포하도록 머신 세트를 구성할 수 있습니다. 이러한 매개변수는 VM 크기, 리전 및 예약할 인스턴스 수를 지정합니다. Azure 서브스크립션 할당량이 용량 요청을 수용할 수 있는 경우 배포에 성공합니다.

이 Azure 오퍼링 에 대한 제한 사항 및 제안된 사용 사례를 비롯한 자세한 내용은 Microsoft Azure 설명서의 요청 용량 예약을 참조하십시오.

참고

머신 세트의 기존 용량 예약 구성은 변경할 수 없습니다. 다른 용량 예약 그룹을 사용하려면 머신 세트와 이전 머신 세트가 배포된 머신을 교체해야 합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

용량 예약 그룹을 생성했습니다. 자세한 내용은 Microsoft Azure 설명서에서 용량 예약 만들기 를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    machines_v1beta1_machine_openshift_io:
      spec:
        providerSpec:
          value:
            capacityReservationGroupID: <capacity_reservation_group>
# ...
```

1. 시스템이 머신을 배포하도록 설정할 용량 예약 그룹의 ID를 지정합니다.

검증

시스템 배포를 확인하려면 다음 명령을 실행하여 머신 세트에서 생성한 머신을 나열합니다.

```shell-session
$ oc get machine \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machine-role=master
```

출력에서 나열된 시스템의 특성이 용량 예약의 매개변수와 일치하는지 확인합니다.

#### 10.5.2.2.9. Microsoft Azure VM용 가속화 네트워킹

가속화 네트워킹은 단일 루트 I/O 가상화(SR-IOV)를 사용하여 Microsoft Azure VM에 더 직접적인 전환 경로를 제공합니다. 이렇게 하면 네트워크 성능이 향상됩니다. 이 기능은 설치 후 활성화할 수 있습니다.

#### 10.5.2.2.9.1. 제한

가속 네트워킹 사용 여부를 결정할 때 다음 제한 사항을 고려하십시오.

가속화 네트워킹은 Machine API가 작동하는 클러스터에서만 지원됩니다.

가속화 네트워킹에는 vCPU가 4개 이상 포함된 Azure VM 크기가 필요합니다. 이 요구 사항을 충족하기 위해 머신 세트의 `vmSize` 값을 변경할 수 있습니다. Azure VM 크기에 대한 자세한 내용은 Microsoft Azure 설명서를 참조하십시오.

#### 10.5.2.2.9.2. 기존 Microsoft Azure 클러스터에서 가속 네트워킹 활성화

머신 세트 YAML 파일에 `acceleratedNetworking` 을 추가하여 Azure에서 가속 네트워킹을 활성화할 수 있습니다.

사전 요구 사항

Machine API가 작동하는 기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

`providerSpec` 필드에 다음을 추가합니다.

```yaml
providerSpec:
  value:
    acceleratedNetworking: true
    vmSize: <azure-vm-size>
```

1. 이 라인은 가속 네트워킹을 활성화합니다.

2. vCPU가 4개 이상인 Azure VM 크기를 지정합니다. VM 크기에 대한 자세한 내용은 Microsoft Azure 설명서 를 참조하십시오.

검증

Microsoft Azure 포털에서 머신 세트에 의해 프로비저닝된 머신의 네트워킹 설정 페이지를 검토하고 `Accelerated networking` 필드가 `Enabled` 로 설정되어 있는지 확인합니다.

#### 10.5.3. Google Cloud의 컨트롤 플레인 구성 옵션

Google Cloud 컨트롤 플레인 머신의 구성을 변경하고 컨트롤 플레인 머신 세트의 값을 업데이트하여 기능을 활성화할 수 있습니다. 컨트롤 플레인 머신 세트에 대한 업데이트를 저장하면 컨트롤 플레인 머신 세트 Operator가 구성된 업데이트 전략에 따라 컨트롤 플레인 시스템을 업데이트합니다.

#### 10.5.3.1. Google Cloud 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 스니펫에서는 Google Cloud 클러스터의 공급자 사양 및 실패 도메인 구성을 보여줍니다.

#### 10.5.3.1.1. 샘플 Google Cloud 공급자 사양

기존 클러스터에 대한 컨트롤 플레인 머신 세트를 생성할 때 공급자 사양은 설치 프로그램이 생성하는 컨트롤 플레인 머신 CR(사용자 정의 리소스)의 `providerSpec` 구성과 일치해야 합니다. CR의 실패 도메인 섹션에 설정된 필드를 생략할 수 있습니다.

#### 10.5.3.1.1.1. OpenShift CLI를 사용하여 얻은 값

다음 예제에서는 OpenShift CLI를 사용하여 클러스터의 일부 값을 가져올 수 있습니다.

인프라 ID

`<cluster_id>` 문자열은 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

이미지 경로

`<path_to_image>` 문자열은 디스크를 생성하는 데 사용된 이미지의 경로입니다. OpenShift CLI가 설치되어 있으면 다음 명령을 실행하여 이미지에 대한 경로를 얻을 수 있습니다.

```shell-session
$ oc -n openshift-machine-api \
  -o jsonpath='{.spec.template.machines_v1beta1_machine_openshift_io.spec.providerSpec.value.disks[0].image}{"\n"}' \
  get ControlPlaneMachineSet/cluster
```

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
      spec:
        providerSpec:
          value:
            apiVersion: machine.openshift.io/v1beta1
            canIPForward: false
            credentialsSecret:
              name: gcp-cloud-credentials
            deletionProtection: false
            disks:
            - autoDelete: true
              boot: true
              image: <path_to_image>
              labels: null
              sizeGb: 200
              type: pd-ssd
            kind: GCPMachineProviderSpec
            machineType: e2-standard-4
            metadata:
              creationTimestamp: null
            metadataServiceOptions: {}
            networkInterfaces:
            - network: <cluster_id>-network
              subnetwork: <cluster_id>-master-subnet
            projectID: <project_name>
            region: <region>
            serviceAccounts:
            - email: <cluster_id>-m@<project_name>.iam.gserviceaccount.com
              scopes:
              - https://www.googleapis.com/auth/cloud-platform
            shieldedInstanceConfig: {}
            tags:
            - <cluster_id>-master
            targetPools:
            - <cluster_id>-api
            userDataSecret:
              name: master-user-data
            zone: ""
```

1. 클러스터의 시크릿 이름을 지정합니다. 이 값은 변경하지 마십시오.

2. 디스크를 만드는 데 사용된 이미지의 경로를 지정합니다.

Google Cloud Marketplace 이미지를 사용하려면 다음을 사용할 제안을 지정합니다.

OpenShift Container Platform: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-ocp-413-x86-64-202305021736`

OpenShift Platform Plus: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-opp-413-x86-64-202305021736`

OpenShift Kubernetes Engine: `https://www.googleapis.com/compute/v1/projects/redhat-marketplace-public/global/images/redhat-coreos-oke-413-x86-64-202305021736`

3. 클라우드 공급자 플랫폼 유형을 지정합니다. 이 값은 변경하지 마십시오.

4. 클러스터에 사용하는 Google Cloud 프로젝트의 이름을 지정합니다.

5. 클러스터의 Google Cloud 리전을 지정합니다.

6. 단일 서비스 계정을 지정합니다. 여러 서비스 계정이 지원되지 않습니다.

7. 컨트롤 플레인 사용자 데이터 시크릿을 지정합니다. 이 값은 변경하지 마십시오.

8. 이 매개변수는 실패 도메인에 구성되며 여기에 빈 값이 표시됩니다. 이 매개변수에 지정된 값이 실패 도메인의 값과 다른 경우 Operator는 실패 도메인의 값으로 덮어씁니다.

#### 10.5.3.1.2. 샘플 Google Cloud 실패 도메인 구성

장애 도메인의 컨트롤 플레인 머신 세트 개념은 영역 의 기존 Google Cloud 개념과 유사합니다. `ControlPlaneMachineSet` CR은 가능한 경우 컨트롤 플레인 시스템을 여러 개의 장애 도메인에 분배합니다.

컨트롤 플레인 머신 세트에서 Google Cloud 장애 도메인을 구성할 때 사용할 영역 이름을 지정해야 합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    machines_v1beta1_machine_openshift_io:
      failureDomains:
        gcp:
        - zone: <gcp_zone_a>
        - zone: <gcp_zone_b>
        - zone: <gcp_zone_c>
        - zone: <gcp_zone_d>
        platform: GCP
# ...
```

1. 첫 번째 실패 도메인의 Google Cloud 영역을 지정합니다.

2. 추가 실패 도메인을 지정합니다. 추가 실패 도메인도 동일한 방식으로 추가됩니다.

3. 클라우드 공급자 플랫폼 이름을 지정합니다. 이 값은 변경하지 마십시오.

#### 10.5.3.2. 컨트롤 플레인 시스템의 Google Cloud 기능 활성화

컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다.

#### 10.5.3.2.1. 머신 세트를 사용하여 영구 디스크 유형 구성

머신 세트가 머신 세트 YAML 파일을 편집하여 머신을 배포하는 영구 디스크 유형을 구성할 수 있습니다.

영구 디스크 유형, 호환성, 지역 가용성 및 제한에 대한 자세한 내용은 영구 디스크에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
...
spec:
  template:
    spec:
      providerSpec:
        value:
          disks:
            type: pd-ssd
```

1. 컨트롤 플레인 노드는 `pd-ssd` 디스크 유형을 사용해야 합니다.

검증

Google Cloud 콘솔을 사용하여 머신 세트에서 배포한 시스템의 세부 정보를 검토하고 `Type` 필드가 구성된 디스크 유형과 일치하는지 확인합니다.

#### 10.5.3.2.2. 머신 세트를 사용하여 기밀성 VM 구성

머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 기밀성 VM 옵션을 구성할 수 있습니다.

Confidential VM 기능, 기능 및 호환성에 대한 자세한 내용은 Confidential VM 에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

참고

현재 기밀 VM은 64비트 ARM 아키텍처에서 지원되지 않습니다. 기밀성 VM을 사용하는 경우 지원되는 리전을 선택해야 합니다. 지원되는 리전 및 구성에 대한 자세한 내용은 지원되는 영역에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
    machines_v1beta1_machine_openshift_io:
      spec:
        providerSpec:
          value:
            confidentialCompute: Enabled
            onHostMaintenance: Terminate
            machineType: n2d-standard-8
# ...
```

1. 기밀성 VM이 활성화되었는지 여부를 지정합니다. 다음 값이 유효합니다.

`활성화됨`

기본 Confidential VM 기술을 선택하여 기밀성 VM을 활성화합니다. 기본 선택은 AMD Secure Encrypted Virtualization(AMD SEV)입니다.

중요

`Enabled` 값은 더 이상 사용되지 않는 AMD Secure Encrypted Virtualization(AMD SEV)을 사용한 기밀성 컴퓨팅을 선택합니다.

`비활성화됨`

기밀성 VM을 비활성화합니다.

`AMDEncryptedVirtualizationNestedPaging`

AMD Secure Encrypted Virtualization Secure Nested Paging(AMD SEV-SNP)을 사용하여 기밀 VM을 활성화합니다. AMD SEV-SNP는 n2d 머신을 지원합니다.

`AMDEncryptedVirtualization`

AMD SEV를 사용한 기밀성 VM 활성화. AMD SEV는 c2d, n2d 및 c3d 시스템을 지원합니다.

중요

AMD Secure Encrypted Virtualization(AMD SEV)에서 기밀 컴퓨팅을 사용하는 것은 더 이상 사용되지 않으며 향후 릴리스에서 제거됩니다.

`IntelTrustedDomainExtensions`

Intel TDX(Intel Trusted Domain Extensions)를 사용하여 기밀성 VM을 활성화합니다. Intel TDX는 n2d 머신을 지원합니다.

2. 호스트 유지 관리 이벤트 중 하드웨어 또는 소프트웨어 업데이트와 같은 VM의 동작을 지정합니다. 기밀성 VM을 사용하는 시스템의 경우 이 값은 VM을 중지하도록 `Terminate` 로 설정해야 합니다. 기밀 VM은 실시간 VM 마이그레이션을 지원하지 않습니다.

3. `confidentialCompute` 필드에 지정한 기밀성 VM 옵션을 지원하는 머신 유형을 지정합니다.

검증

Google Cloud 콘솔에서 시스템 세트에서 배포한 시스템의 세부 정보를 검토하고 기밀성 VM 옵션이 구성한 값과 일치하는지 확인합니다.

#### 10.5.3.2.3. 머신 세트를 사용하여 Shielded VM 옵션 구성

머신 세트 YAML 파일을 편집하여 머신 세트가 배포하는 머신에 사용하는 Shielded VM 옵션을 구성할 수 있습니다.

Shielded VM 기능 및 기능에 대한 자세한 내용은 Shielded VM 에 대한 Google Cloud Compute Engine 설명서를 참조하십시오.

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 섹션을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          shieldedInstanceConfig:
            integrityMonitoring: Enabled
            secureBoot: Disabled
            virtualizedTrustedPlatformModule: Enabled
# ...
```

1. 이 섹션에서는 원하는 모든 Shielded VM 옵션을 지정합니다.

2. 무결성 모니터링이 활성화되었는지 여부를 지정합니다. 유효한 값은 `Disabled` 또는 `Enabled` 입니다.

참고

무결성 모니터링이 활성화되면 신뢰할 수 있는 가상 플랫폼 모듈(vTPM)을 비활성화해서는 안 됩니다.

3. UEFI Secure Boot가 활성화되었는지 여부를 지정합니다. 유효한 값은 `Disabled` 또는 `Enabled` 입니다.

4. vTPM이 활성화되었는지 여부를 지정합니다. 유효한 값은 `Disabled` 또는 `Enabled` 입니다.

검증

Google Cloud 콘솔을 사용하여 머신 세트에서 배포한 머신의 세부 정보를 검토하고 Shielded VM 옵션이 구성한 값과 일치하는지 확인합니다.

추가 리소스

Shielded VM이란 무엇입니까?

Secure Boot

가상 신뢰할 수 있는 플랫폼 모듈(vTPM)

무결성 모니터링

#### 10.5.3.2.4. 머신 세트의 고객 관리 암호화 키 활성화

Google Cloud Compute Engine을 사용하면 암호화 키를 제공하여 디스크의 데이터를 암호화할 수 있습니다. 키는 고객의 데이터를 암호화하는 것이 아니라 데이터 암호화 키를 암호화하는 데 사용됩니다. 기본적으로 Compute Engine은 Compute Engine 키를 사용하여 이 데이터를 암호화합니다.

Machine API를 사용하는 클러스터에서 고객 관리 키로 암호화를 활성화할 수 있습니다. 먼저 KMS 키를 생성 하고 서비스 계정에 올바른 권한을 할당해야 합니다. 서비스 계정에서 키를 사용하려면 KMS 키 이름, 키 링 이름 및 위치가 필요합니다.

참고

KMS 암호화에 전용 서비스 계정을 사용하지 않는 경우 Compute Engine 기본 서비스 계정이 대신 사용됩니다. 전용 서비스 계정을 사용하지 않는 경우 키에 액세스할 수 있는 기본 서비스 계정 권한을 부여해야 합니다. Compute Engine 기본 서비스 계정 이름은 `service-<project_number>@compute-system.iam.gserviceaccount.com` 패턴을 기반으로 합니다.

프로세스

특정 서비스 계정이 KMS 키를 사용하도록 허용하고 서비스 계정에 올바른 IAM 역할을 부여하려면 KMS 키 이름, 키 링 이름 및 위치로 다음 명령을 실행합니다.

```shell-session
$ gcloud kms keys add-iam-policy-binding <key_name> \
  --keyring <key_ring_name> \
  --location <key_ring_location> \
  --member "serviceAccount:service-<project_number>@compute-system.iam.gserviceaccount.com” \
  --role roles/cloudkms.cryptoKeyEncrypterDecrypter
```

사용자가 머신 세트 YAML 파일의 `providerSpec` 필드에 암호화 키를 구성할 수 있습니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
...
spec:
  template:
    spec:
      providerSpec:
        value:
          disks:
          - type:
            encryptionKey:
              kmsKey:
                name: machine-encryption-key
                keyRing: openshift-encrpytion-ring
                location: global
                projectID: openshift-gcp-project
              kmsKeyServiceAccount: openshift-service-account@openshift-gcp-project.iam.gserviceaccount.com
```

1. 디스크 암호화에 사용되는 고객 관리 암호화 키의 이름입니다.

2. KMS 키가 속한 KMS 키 링의 이름입니다.

3. KMS 키 링이 있는 Google Cloud 위치입니다.

4. 선택 사항: KMS 키 링이 존재하는 프로젝트의 ID입니다. 프로젝트 ID가 설정되지 않은 경우 머신 세트가 사용된 머신 세트의 `projectID` 를 설정합니다.

5. 선택 사항: 지정된 KMS 키의 암호화 요청에 사용되는 서비스 계정입니다. 서비스 계정이 설정되지 않은 경우 Compute Engine 기본 서비스 계정이 사용됩니다.

업데이트된 `providerSpec` 오브젝트 구성을 사용하여 새 머신을 생성하면 디스크 암호화 키가 KMS 키로 암호화됩니다.

#### 10.5.4. Nutanix의 컨트롤 플레인 구성 옵션

컨트롤 플레인 머신 세트의 값을 업데이트하여 Nutanix 컨트롤 플레인 머신의 구성을 변경할 수 있습니다. 컨트롤 플레인 머신 세트에 대한 업데이트를 저장하면 컨트롤 플레인 머신 세트 Operator가 구성된 업데이트 전략에 따라 컨트롤 플레인 시스템을 업데이트합니다.

#### 10.5.4.1. Nutanix 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 스니펫에서는 Nutanix 클러스터의 공급자 사양 구성을 보여줍니다.

#### 10.5.4.1.1. 샘플 Nutanix 공급자 사양

기존 클러스터에 대한 컨트롤 플레인 머신 세트를 생성할 때 공급자 사양은 설치 프로그램이 생성하는 컨트롤 플레인 머신 CR(사용자 정의 리소스)의 `providerSpec` 구성과 일치해야 합니다.

#### 10.5.4.1.1.1. OpenShift CLI를 사용하여 얻은 값

다음 예제에서는 OpenShift CLI를 사용하여 클러스터의 일부 값을 가져올 수 있습니다.

인프라 ID

`<cluster_id>` 문자열은 클러스터를 프로비저닝할 때 설정한 클러스터 ID를 기반으로 하는 인프라 ID입니다. OpenShift CLI 패키지가 설치되어 있으면 다음 명령을 실행하여 인프라 ID를 얻을 수 있습니다.

```shell-session
$ oc get -o jsonpath='{.status.infrastructureName}{"\n"}' infrastructure cluster
```

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
      spec:
        providerSpec:
          value:
            apiVersion: machine.openshift.io/v1
            bootType: ""
            categories:
            - key: <category_name>
              value: <category_value>
            cluster:
              type: uuid
              uuid: <cluster_uuid>
            credentialsSecret:
              name: nutanix-credentials
            image:
              name: <cluster_id>-rhcos
              type: name
            kind: NutanixMachineProviderConfig
            memorySize: 16Gi
            metadata:
              creationTimestamp: null
            project:
              type: name
              name: <project_name>
            subnets:
            - type: uuid
              uuid: <subnet_uuid>
            systemDiskSize: 120Gi
            userDataSecret:
              name: master-user-data
            vcpuSockets: 8
            vcpusPerSocket: 1
```

1. 컨트롤 플레인 시스템이 사용하는 부팅 유형을 지정합니다. 부팅 유형에 대한 자세한 내용은 가상화 된 환경에서 UEFI, Secure Boot 및 TPM 이해를 참조하십시오. 유효한 값은 `Legacy`, `SecureBoot` 또는 `UEFI` 입니다. 기본값은 `Legacy` 입니다.

참고

OpenShift Container Platform 4.20에서 `레거시` 부팅 유형을 사용해야 합니다.

2. 컨트롤 플레인 시스템에 적용할 하나 이상의 Nutanix Prism 카테고리를 지정합니다. 이 스탠자에는 Prism Central에 존재하는 카테고리 키-값 쌍에 대한 `key` 및 `value` 매개변수가 필요합니다. 카테고리에 대한 자세한 내용은 카테고리 관리를 참조하십시오.

3. Nutanix Prism Element 클러스터 구성을 지정합니다. 이 예에서 클러스터 유형은 `uuid` 이므로 `uuid` 스탠자가 있습니다.

참고

OpenShift Container Platform 버전 4.15 이상을 사용하는 클러스터는 장애 도메인 구성을 사용할 수 있습니다.

클러스터에서 실패 도메인을 사용하는 경우 실패 도메인에서 이 매개 변수를 구성합니다. 장애 도메인을 사용할 때 공급자 사양에 이 값을 지정하면 Control Plane Machine Set Operator가 이를 무시합니다.

4. 클러스터의 시크릿 이름을 지정합니다. 이 값은 변경하지 마십시오.

5. 디스크를 만드는 데 사용된 이미지를 지정합니다.

6. 클라우드 공급자 플랫폼 유형을 지정합니다. 이 값은 변경하지 마십시오.

7. 컨트롤 플레인 시스템에 할당된 메모리를 지정합니다.

8. 클러스터에 사용하는 Nutanix 프로젝트를 지정합니다. 이 예에서 프로젝트 유형은 `name` 이므로 `name` 스탠자가 있습니다.

9. 하나 이상의 Prism Element 서브넷 오브젝트를 지정합니다. 이 예에서 서브넷 유형은 `uuid` 이므로 `uuid` 스탠자가 있습니다. 클러스터의 각 Prism Element 장애 도메인에 대해 최대 32 서브넷이 지원됩니다.

중요

OpenShift Container Platform 버전 4.18에 컨트롤 플레인 머신 세트를 사용하여 기존 Nutanix 클러스터에 대해 여러 서브넷을 구성하는 데 대한 알려진 문제는 다음과 같습니다.

`subnets` 스탠자에서 기존 서브넷 위에 서브넷을 추가하면 컨트롤 플레인 노드가 `Deleting` 상태가 됩니다. 이 문제를 해결하려면 `subnets` 스탠자의 기존 서브넷 아래에만 서브넷을 추가합니다.

서브넷을 추가한 후 업데이트된 컨트롤 플레인 머신이 Nutanix 콘솔에 표시되지만 OpenShift Container Platform 클러스터에 연결할 수 없습니다. 이 문제에 대한 해결방법이 없습니다.

이러한 문제는 컨트롤 플레인 머신 세트를 사용하여 서브넷이 실패 도메인 또는 공급자 사양에 지정되었는지 여부와 관계없이 서브넷을 구성하는 클러스터에서 발생합니다. 자세한 내용은 OCPBUGS-50904 를 참조하십시오.

지정된 서브넷 중 하나에 대한 CIDR IP 주소 접두사에는 OpenShift Container Platform 클러스터가 사용하는 가상 IP 주소가 포함되어야 합니다. 모든 서브넷 UUID 값은 고유해야 합니다.

참고

OpenShift Container Platform 버전 4.15 이상을 사용하는 클러스터는 장애 도메인 구성을 사용할 수 있습니다.

클러스터에서 실패 도메인을 사용하는 경우 실패 도메인에서 이 매개 변수를 구성합니다. 장애 도메인을 사용할 때 공급자 사양에 이 값을 지정하면 Control Plane Machine Set Operator가 이를 무시합니다.

10. 컨트롤 플레인 시스템의 VM 디스크 크기를 지정합니다.

11. 컨트롤 플레인 사용자 데이터 시크릿을 지정합니다. 이 값은 변경하지 마십시오.

12. 컨트롤 플레인 시스템에 할당된 vCPU 소켓 수를 지정합니다.

13. 각 컨트롤 플레인 vCPU 소켓의 vCPU 수를 지정합니다.

#### 10.5.4.1.2. Nutanix 클러스터의 실패 도메인

Nutanix 클러스터에서 장애 도메인 구성을 추가하거나 업데이트하려면 여러 리소스를 조정해야 합니다. 다음 작업이 필요합니다.

클러스터 인프라 CR(사용자 정의 리소스)을 수정합니다.

클러스터 컨트롤 플레인 머신 세트 CR을 수정합니다.

컴퓨팅 머신 세트 CR을 수정하거나 교체합니다.

자세한 내용은 설치 후 구성 콘텐츠의 "기존 Nutanix 클러스터에 장애 도메인 추가"를 참조하십시오.

추가 리소스

기존 Nutanix 클러스터에 장애 도메인 추가

#### 10.5.5. Red Hat OpenStack Platform의 컨트롤 플레인 구성 옵션

RHOSP(Red Hat OpenStack Platform) 컨트롤 플레인 머신의 구성을 변경하고 컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다. 컨트롤 플레인 머신 세트에 대한 업데이트를 저장하면 컨트롤 플레인 머신 세트 Operator가 구성된 업데이트 전략에 따라 컨트롤 플레인 시스템을 업데이트합니다.

#### 10.5.5.1. RHOSP(Red Hat OpenStack Platform) 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 스니펫에서는 RHOSP 클러스터의 공급자 사양 및 실패 도메인 구성을 보여줍니다.

#### 10.5.5.1.1. RHOSP 공급자 사양 샘플

기존 클러스터에 대한 컨트롤 플레인 머신 세트를 생성할 때 공급자 사양은 설치 프로그램이 생성하는 컨트롤 플레인 머신 CR(사용자 정의 리소스)의 `providerSpec` 구성과 일치해야 합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
      spec:
        providerSpec:
          value:
            apiVersion: machine.openshift.io/v1alpha1
            cloudName: openstack
            cloudsSecret:
              name: openstack-cloud-credentials
              namespace: openshift-machine-api
            flavor: m1.xlarge
            image: ocp1-2g2xs-rhcos
            kind: OpenstackProviderSpec
            metadata:
              creationTimestamp: null
            networks:
            - filter: {}
              subnets:
              - filter:
                  name: ocp1-2g2xs-nodes
                  tags: openshiftClusterID=ocp1-2g2xs
            securityGroups:
            - filter: {}
              name: ocp1-2g2xs-master
            serverGroupName: ocp1-2g2xs-master
            serverMetadata:
              Name: ocp1-2g2xs-master
              openshiftClusterID: ocp1-2g2xs
            tags:
            - openshiftClusterID=ocp1-2g2xs
            trunk: true
            userDataSecret:
              name: master-user-data
```

1. 클러스터의 시크릿 이름입니다. 이 값은 변경하지 마십시오.

2. 컨트롤 플레인의 RHOSP 플레이버 유형입니다.

3. RHOSP 클라우드 공급자 플랫폼 유형입니다. 이 값은 변경하지 마십시오.

4. 컨트롤 플레인 시스템 보안 그룹입니다.

#### 10.5.5.1.2. RHOSP 장애 도메인 구성 샘플

실패 도메인의 컨트롤 플레인 머신 세트 개념은 가용성 영역 의 기존 RHOSP(Red Hat OpenStack Platform) 개념과 유사합니다. `ControlPlaneMachineSet` CR은 가능한 경우 컨트롤 플레인 시스템을 여러 개의 장애 도메인에 분배합니다.

다음 예제에서는 여러 Nova 가용성 영역과 Cinder 가용성 영역을 사용하는 방법을 보여줍니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    machines_v1beta1_machine_openshift_io:
      failureDomains:
        platform: OpenStack
        openstack:
        - availabilityZone: nova-az0
          rootVolume:
            availabilityZone: cinder-az0
        - availabilityZone: nova-az1
          rootVolume:
            availabilityZone: cinder-az1
        - availabilityZone: nova-az2
          rootVolume:
            availabilityZone: cinder-az2
# ...
```

#### 10.5.5.2. 컨트롤 플레인 시스템에 대한 RHOSP(Red Hat OpenStack Platform) 기능 활성화

컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다.

#### 10.5.5.2.1. 컨트롤 플레인 머신 세트를 사용하여 RHOSP 컴퓨팅 플레이버 변경

컨트롤 플레인 머신 세트 사용자 정의 리소스에서 사양을 업데이트하여 컨트롤 플레인 시스템에서 사용하는 RHOSP(Red Hat OpenStack Platform) 컴퓨팅 서비스(Nova) 플레이버를 변경할 수 있습니다.

RHOSP에서 플레이버는 컴퓨팅 인스턴스의 컴퓨팅, 메모리 및 스토리지 용량을 정의합니다. 플레이버 크기를 늘리거나 줄이면 컨트롤 플레인을 수직으로 확장할 수 있습니다.

사전 요구 사항

RHOSP 클러스터는 컨트롤 플레인 머신 세트를 사용합니다.

프로세스

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
providerSpec:
  value:
# ...
    flavor: m1.xlarge
```

1. 기존 선택 사항과 동일한 기반이 있는 RHOSP 플레이버 유형을 지정합니다. 예를 들어 `m6i.xlarge` 를 `m6i.2xlarge` 또는 `m6i.4xlarge` 로 변경할 수 있습니다. 수직 확장 요구 사항에 따라 더 크거나 작은 플레이버를 선택할 수 있습니다.

변경 사항을 저장하십시오.

변경 사항을 저장하면 시스템이 선택한 플레이버를 사용하는 시스템으로 교체됩니다.

#### 10.5.6. VMware vSphere의 컨트롤 플레인 구성 옵션

컨트롤 플레인 시스템 세트에서 값을 업데이트하여 VMware vSphere 컨트롤 플레인 시스템의 구성을 변경할 수 있습니다. 컨트롤 플레인 머신 세트에 대한 업데이트를 저장하면 컨트롤 플레인 머신 세트 Operator가 구성된 업데이트 전략에 따라 컨트롤 플레인 시스템을 업데이트합니다.

#### 10.5.6.1. VMware vSphere 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 스니펫에서는 vSphere 클러스터의 공급자 사양 및 실패 도메인 구성을 보여줍니다.

#### 10.5.6.1.1. VMware vSphere 공급자 사양 샘플

기존 클러스터에 대한 컨트롤 플레인 머신 세트를 생성할 때 공급자 사양은 설치 프로그램이 생성하는 컨트롤 플레인 머신 CR(사용자 정의 리소스)의 `providerSpec` 구성과 일치해야 합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
      spec:
        providerSpec:
          value:
            apiVersion: machine.openshift.io/v1beta1
            credentialsSecret:
              name: vsphere-cloud-credentials
            dataDisks:
            - name: "<disk_name>"
              provisioningMode: "<mode>"
              sizeGiB: 20
            diskGiB: 120
            kind: VSphereMachineProviderSpec
            memoryMiB: 16384
            metadata:
              creationTimestamp: null
            network:
              devices:
              - networkName: <vm_network_name>
            numCPUs: 4
            numCoresPerSocket: 4
            snapshot: ""
            template: <vm_template_name>
            userDataSecret:
              name: master-user-data
            workspace:
              datacenter: <vcenter_data_center_name>
              datastore: <vcenter_datastore_name>
              folder: <path_to_vcenter_vm_folder>
              resourcePool: <vsphere_resource_pool>
              server: <vcenter_server_ip>
```

1. 클러스터의 시크릿 이름을 지정합니다. 이 값은 변경하지 마십시오.

2. 하나 이상의 데이터 디스크 정의를 지정합니다. 자세한 내용은 "머신 세트를 사용하여 데이터 디스크 구성"을 참조하십시오.

3. 컨트롤 플레인 시스템의 VM 디스크 크기를 지정합니다.

4. 클라우드 공급자 플랫폼 유형을 지정합니다. 이 값은 변경하지 마십시오.

5. 컨트롤 플레인 시스템에 할당된 메모리를 지정합니다.

6. 컨트롤 플레인이 배포되는 네트워크를 지정합니다.

참고

클러스터가 실패 도메인을 사용하도록 구성된 경우 이 매개변수는 실패 도메인에 구성됩니다. 장애 도메인을 사용할 때 공급자 사양에 이 값을 지정하면 Control Plane Machine Set Operator가 이를 무시합니다.

7. 컨트롤 플레인 시스템에 할당된 CPU 수를 지정합니다.

8. 각 컨트롤 플레인 CPU의 코어 수를 지정합니다.

9. 사용할 vSphere VM 템플릿을 지정합니다(예: `user-5ddjd-rhcos`).

참고

클러스터가 실패 도메인을 사용하도록 구성된 경우 이 매개변수는 실패 도메인에 구성됩니다. 장애 도메인을 사용할 때 공급자 사양에 이 값을 지정하면 Control Plane Machine Set Operator가 이를 무시합니다.

10. 컨트롤 플레인 사용자 데이터 시크릿을 지정합니다. 이 값은 변경하지 마십시오.

11. 컨트롤 플레인의 작업 공간 세부 정보를 지정합니다.

참고

클러스터가 장애 도메인을 사용하도록 구성된 경우 이러한 매개변수는 실패 도메인에 구성됩니다. 장애 도메인을 사용할 때 공급자 사양에 이러한 값을 지정하면 Control Plane Machine Set Operator가 해당 값을 무시합니다.

12. 컨트롤 플레인의 vCenter 데이터 센터를 지정합니다.

13. 컨트롤 플레인의 vCenter 데이터 저장소를 지정합니다.

14. vCenter의 vSphere VM 폴더 경로(예: `/dc1/vm/user-inst-5ddjd`)를 지정합니다.

15. VM의 vSphere 리소스 풀을 지정합니다.

16. vCenter 서버 IP 또는 정규화된 도메인 이름을 지정합니다.

#### 10.5.6.1.2. VMware vSphere 장애 도메인 구성 샘플

VMware vSphere 인프라에서 클러스터 전체 인프라 CRD(Custom Resource Definition), infrastructure `.config.openshift.io` 에서는 클러스터의 실패 도메인을 정의합니다. `ControlPlaneMachineSet` CR(사용자 정의 리소스)의 `providerSpec` 은 컨트롤 플레인 머신 세트가 적절한 장애 도메인에 배포되도록 컨트롤 플레인 머신 세트가 사용하는 장애 도메인의 이름을 지정합니다. 장애 도메인은 컨트롤 플레인 머신 세트, vCenter 데이터 센터, vCenter 데이터 저장소 및 네트워크로 구성된 인프라 리소스입니다.

장애 도메인 리소스를 사용하면 컨트롤 플레인 머신 세트를 사용하여 별도의 클러스터 또는 데이터 센터에 컨트롤 플레인 시스템을 배포할 수 있습니다. 컨트롤 플레인 머신 세트도 정의된 장애 도메인에서 컨트롤 플레인 시스템의 균형을 유지하여 인프라에 내결함성 기능을 제공합니다.

참고

`ControlPlaneMachineSet` CR에서 `ProviderSpec` 구성을 수정하면 컨트롤 플레인 머신 세트는 기본 인프라 및 각 장애 도메인 인프라에 배포된 모든 컨트롤 플레인 시스템을 업데이트합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
metadata:
  name: cluster
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    machines_v1beta1_machine_openshift_io:
      failureDomains:
        platform: VSphere
        vsphere:
        - name: <failure_domain_name_1>
        - name: <failure_domain_name_2>
# ...
```

1. OpenShift Container Platform 클러스터 노드의 vCenter 위치를 지정합니다.

2. 컨트롤 플레인 머신 세트의 이름으로 실패 도메인을 지정합니다.

중요

이 섹션의 각 `name` 필드 값은 클러스터 전체 인프라 CRD의 `failureDomains.name` 필드 값과 일치해야 합니다. 다음 명령을 실행하여 `failureDomains.name` 필드의 값을 찾을 수 있습니다.

```shell-session
$ oc get infrastructure cluster -o=jsonpath={.spec.platformSpec.vsphere.failureDomains[0].name}
```

`name` 필드는 `ControlPlaneMachineSet` CR에 지정할 수 있는 유일한 장애 도메인 필드입니다.

각 장애 도메인의 리소스를 정의하는 클러스터 전체 인프라 CRD의 예는 " vSphere에서 클러스터에 대한 여러 리전 및 영역 연결"을 참조하십시오.

추가 리소스

vSphere에서 클러스터의 여러 리전 및 영역 지정

#### 10.5.6.2. 컨트롤 플레인 시스템의 VMware vSphere 기능 활성화

컨트롤 플레인 머신 세트에서 값을 업데이트하여 기능을 활성화할 수 있습니다.

#### 10.5.6.2.1. 머신 세트를 사용하여 머신에 태그 추가

OpenShift Container Platform은 생성된 각 VM(가상 머신)에 클러스터별 태그를 추가합니다. 설치 프로그램은 이러한 태그를 사용하여 클러스터를 제거할 때 삭제할 VM을 선택합니다.

VM에 할당된 클러스터별 태그 외에도 프로비저닝하는 VM에 최대 10개의 vSphere 태그를 추가하도록 머신 세트를 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 vSphere에 설치된 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

클러스터와 연결된 VMware vCenter 콘솔에 액세스할 수 있습니다.

vCenter 콘솔에 태그가 생성되어 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

vCenter 콘솔을 사용하여 시스템에 추가할 태그의 태그 ID를 찾습니다.

vCenter 콘솔에 로그인합니다.

홈 메뉴에서 태그 및 사용자 지정 속성을 클릭합니다.

시스템에 추가할 태그를 선택합니다.

선택한 태그의 브라우저 URL을 사용하여 태그 ID를 식별합니다.

```plaintext
https://vcenter.example.com/ui/app/tags/tag/urn:vmomi:InventoryServiceTag:208e713c-cae3-4b7f-918e-4051ca7d1f97:GLOBAL/permissions
```

```plaintext
urn:vmomi:InventoryServiceTag:208e713c-cae3-4b7f-918e-4051ca7d1f97:GLOBAL
```

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    spec:
      providerSpec:
        value:
          tagIDs:
          - <tag_id_value>
# ...
```

1. 이 시스템이 프로비저닝한 머신에 추가할 최대 10개의 태그 목록을 지정합니다.

2. 시스템에 추가할 태그 값을 지정합니다. 예를 들어 `urn:vmomi:인벤토리ServiceTag:208e713c-cae3-4b7f-918e-4051ca7d1f97:GLOBAL`.

#### 10.5.6.2.2. 머신 세트를 사용하여 데이터 디스크 구성

VMware vSphere의 OpenShift Container Platform 클러스터는 VM(가상 머신) 컨트롤러에 최대 29개의 디스크를 추가할 수 있도록 지원합니다.

중요

vSphere 데이터 디스크 구성은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

데이터 디스크를 구성하면 디스크를 VM에 연결하고 이를 사용하여 etcd, 컨테이너 이미지 및 기타 용도의 데이터를 저장할 수 있습니다. 데이터를 분리하면 업그레이드와 같은 중요한 작업에 필요한 리소스가 있도록 기본 디스크를 채우지 않도록 할 수 있습니다.

참고

데이터 디스크를 추가하면 VM에 연결하여 RHCOS가 지정하는 위치에 마운트합니다.

사전 요구 사항

vSphere의 OpenShift Container Platform 클러스터의 경우 CLI(OpenShift CLI)에 대한 관리자 액세스 권한이 있습니다.

```shell
oc
```

프로세스

텍스트 편집기에서 기존 머신 세트의 YAML 파일을 열거나 새 머신을 생성합니다.

`providerSpec` 필드 아래의 다음 행을 편집합니다.

```yaml
apiVersion: machine.openshift.io/v1
kind: ControlPlaneMachineSet
# ...
spec:
  template:
    machines_v1beta1_machine_openshift_io:
      spec:
        providerSpec:
          value:
            dataDisks:
            - name: "<disk_name>"
              provisioningMode: "<mode>"
              sizeGiB: 20
            - name: "<disk_name>"
              provisioningMode: "<mode>"
              sizeGiB: 20
# ...
```

1. 1-29 데이터 디스크 정의 컬렉션을 지정합니다. 이 샘플 구성은 두 개의 데이터 디스크 정의를 포함하는 포맷을 보여줍니다.

2. 데이터 디스크의 이름을 지정합니다. 이름은 다음 요구 사항을 충족해야 합니다.

영숫자 문자로 시작 및 끝

영숫자, 하이픈(`-`) 및 밑줄(`_`)으로만 구성됩니다.

최대 길이는 80자입니다.

3. 데이터 디스크 프로비저닝 방법을 지정합니다. 이 값은 설정되지 않은 경우 기본적으로 vSphere 기본 스토리지 정책으로 설정됩니다. 유효한 값은 `Thin`, `Thick`, `EagerlyZeroed` 입니다.

4. 데이터 디스크 크기를 GiB 단위로 지정합니다. 최대 크기는 16384GiB입니다.

### 10.6. 컨트롤 플레인 복원력 및 복구

컨트롤 플레인 머신 세트를 사용하여 OpenShift Container Platform 클러스터의 컨트롤 플레인의 복원력을 향상시킬 수 있습니다.

#### 10.6.1. 장애 도메인을 통한 고가용성 및 내결함성

가능한 경우 컨트롤 플레인 머신 세트는 컨트롤 플레인 시스템을 여러 장애 도메인에 분배합니다. 이 구성은 컨트롤 플레인 내에서 고가용성 및 내결함성을 제공합니다. 이 전략은 인프라 공급자 내에서 문제가 발생할 때 컨트롤 플레인을 보호하는 데 도움이 될 수 있습니다.

#### 10.6.1.1. 장애 도메인 플랫폼 지원 및 구성

장애 도메인의 컨트롤 플레인 머신 세트 개념은 클라우드 공급자의 기존 개념과 유사합니다. 모든 플랫폼이 장애 도메인 사용을 지원하는 것은 아닙니다.

| 클라우드 공급자 | 실패 도메인 지원 | 공급자 nomenclature |
| --- | --- | --- |
| AWS(Amazon Web Services) | X | 가용성 영역(AZ) |
| Google Cloud | X | 영역 |
| Microsoft Azure | X | Azure 가용성 영역 |
| Nutanix | X | 실패 도메인 |
| Red Hat OpenStack Platform (RHOSP) | X | OpenStack Nova 가용성 영역 및 OpenStack Cinder 가용성 영역 |
| VMware vSphere | X | vSphere 영역에 매핑된 실패 도메인 [1] |

자세한 내용은 " VMware vCenter의 지역 및 영역"을 참조하십시오.

컨트롤 플레인 머신 세트 CR(사용자 정의 리소스)의 장애 도메인 구성은 플랫폼에 따라 다릅니다. CR의 실패 도메인 매개변수에 대한 자세한 내용은 공급자의 샘플 실패 도메인 구성을 참조하십시오.

추가 리소스

샘플 Amazon Web Services 실패 도메인 구성

샘플 Google Cloud 실패 도메인 구성

Microsoft Azure 실패 도메인 구성 샘플

기존 Nutanix 클러스터에 장애 도메인 추가

샘플 RHOSP(Red Hat OpenStack Platform) 장애 도메인 구성

VMware vSphere 장애 도메인 구성 샘플

VMware vCenter의 지역 및 영역

#### 10.6.1.2. 컨트롤 플레인 시스템 밸런싱

컨트롤 플레인 머신 세트는 CR(사용자 정의 리소스)에 지정된 장애 도메인에서 컨트롤 플레인 시스템의 균형을 조정합니다.

가능한 경우 컨트롤 플레인 머신 세트는 각 장애 도메인을 동일하게 사용하여 적절한 내결함성을 보장합니다. 컨트롤 플레인 시스템보다 장애 도메인이 적은 경우 이름으로 알파벳순으로 재사용하기 위해 장애 도메인을 선택합니다. 장애 도메인이 지정되지 않은 클러스터의 경우 모든 컨트롤 플레인 시스템이 단일 장애 도메인에 배치됩니다.

장애 도메인 구성을 변경하면 컨트롤 플레인 머신 세트가 컨트롤 플레인 시스템을 재조정합니다. 예를 들어 컨트롤 플레인 시스템보다 장애 도메인이 적은 클러스터에 장애 도메인을 추가하는 경우 컨트롤 플레인 머신 세트는 사용 가능한 모든 장애 도메인에서 시스템을 재조정합니다.

#### 10.6.2. 실패한 컨트롤 플레인 시스템 복구

Control Plane Machine Set Operator는 컨트롤 플레인 머신의 복구를 자동화합니다. 컨트롤 플레인 머신이 삭제되면 Operator는 `ControlPlaneMachineSet` CR(사용자 정의 리소스)에 지정된 구성으로 교체를 생성합니다.

컨트롤 플레인 머신 세트를 사용하는 클러스터의 경우 머신 상태 점검을 구성할 수 있습니다. 머신 상태 점검에서 비정상 컨트롤 플레인 머신이 삭제되어 교체됩니다.

중요

컨트롤 플레인에 대해 `MachineHealthCheck` 리소스를 구성하는 경우 `maxUnhealthy` 값을 `1` 로 설정합니다.

이 구성을 사용하면 여러 컨트롤 플레인 머신이 비정상으로 표시될 때 머신 상태 점검에서 아무 작업도 수행하지 않습니다. 여러 비정상적인 컨트롤 플레인 시스템은 etcd 클러스터의 성능이 저하되거나 실패한 머신을 교체하는 확장 작업이 진행 중임을 나타낼 수 있습니다.

etcd 클러스터의 성능이 저하된 경우 수동 개입이 필요할 수 있습니다. 스케일링 작업이 진행 중인 경우 머신 상태 점검에서 이 작업을 완료할 수 있어야 합니다.

추가 리소스

머신 상태 확인

#### 10.6.3. 머신 라이프사이클 후크를 통한 쿼럼 보호

Machine API Operator를 사용하는 OpenShift Container Platform 클러스터의 경우 etcd Operator는 머신 삭제 단계에 라이프사이클 후크를 사용하여 쿼럼 보호 메커니즘을 구현합니다.

etcd Operator는 `preDrain` 라이프사이클 후크를 사용하여 컨트롤 플레인 머신의 Pod를 드레이닝하고 제거하는 시기를 제어할 수 있습니다. etcd 쿼럼을 보호하기 위해 etcd Operator는 클러스터 내의 새 노드로 해당 멤버를 마이그레이션할 때까지 etcd 멤버를 제거하지 않습니다.

이 메커니즘을 사용하면 etcd Operator가 etcd 쿼럼의 멤버를 정확하게 제어할 수 있으며 Machine API Operator가 etcd 클러스터에 대한 특정 운영 지식없이 컨트롤 플레인 머신을 안전하게 생성하고 제거할 수 있습니다.

#### 10.6.3.1. 쿼럼 보호 처리 순서를 사용하여 컨트롤 플레인 삭제

컨트롤 플레인 시스템 세트를 사용하는 클러스터에서 컨트롤 플레인 시스템을 교체하면 클러스터에 일시적으로 4개의 컨트롤 플레인 시스템이 있습니다. 네 번째 컨트롤 플레인 노드가 클러스터에 결합되면 etcd Operator가 교체 노드에서 새 etcd 멤버를 시작합니다. etcd Operator에서 이전 컨트롤 플레인 머신이 삭제로 표시된 것을 관찰하면 이전 노드에서 etcd 멤버를 중지하고 교체 etcd 멤버가 클러스터의 쿼럼에 참여하도록 승격합니다.

컨트롤 플레인 머신 `Deleting` 단계는 다음 순서로 진행됩니다.

삭제를 위해 컨트롤 플레인 시스템이 지정되었습니다.

컨트롤 플레인 시스템은 `Deleting` 단계에 들어갑니다.

`preDrain` 라이프사이클 후크를 충족하기 위해 etcd Operator는 다음 작업을 수행합니다.

etcd Operator는 네 번째 컨트롤 플레인 머신이 클러스터에 etcd 멤버로 추가될 때까지 기다립니다. 이 새 etcd 멤버의 상태는 `Running` 이지만 etcd 리더에서 전체 데이터베이스 업데이트가 수신될 때까지 `ready` 되지 않았습니다.

새 etcd 멤버가 전체 데이터베이스 업데이트를 수신하면 etcd Operator는 새 etcd 멤버를 투표 멤버로 승격하고 클러스터에서 이전 etcd 멤버를 제거합니다.

이 전환이 완료되면 이전 etcd pod 및 해당 데이터를 제거하는 것이 안전하므로 `preDrain` 라이프사이클 후크가 제거됩니다.

컨트롤 플레인 시스템 상태 `Drainable` 은 `True` 로 설정됩니다.

머신 컨트롤러는 컨트롤 플레인 시스템에서 지원하는 노드를 드레이닝하려고 합니다.

드레이닝에 실패하면 `Drained` 가 `False` 로 설정되고 머신 컨트롤러에서 노드를 다시 드레이닝하려고 합니다.

드레이닝이 성공하면 `Drained` 가 `True` 로 설정됩니다.

컨트롤 플레인 시스템 상태 `Drained` 가 `True` 로 설정됩니다.

다른 Operator에서 `preTerminate` 라이프사이클 후크를 추가하지 않은 경우 컨트롤 플레인 머신 상태 조건 `Terminable` 이 `True` 로 설정됩니다.

머신 컨트롤러는 인프라 공급자에서 인스턴스를 제거합니다.

머신 컨트롤러에서 `Node` 오브젝트를 삭제합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: Machine
metadata:
  ...
spec:
  lifecycleHooks:
    preDrain:
    - name: EtcdQuorumOperator
      owner: clusteroperator/etcd
  ...
```

1. `preDrain` 라이프사이클 후크의 이름입니다.

2. `preDrain` 라이프사이클 후크를 관리하는 후크 구현 컨트롤러입니다.

추가 리소스

머신 삭제 단계에 대한 라이프사이클 후크

### 10.7. 컨트롤 플레인 머신 세트 문제 해결

이 섹션의 정보를 사용하여 발생할 수 있는 문제를 이해하고 복구하십시오.

#### 10.7.1. 컨트롤 플레인 머신 세트 사용자 정의 리소스 상태 확인

`ControlPlaneMachineSet` CR(사용자 정의 리소스)의 존재 및 상태를 확인할 수 있습니다.

프로세스

다음 명령을 실행하여 CR의 상태를 확인합니다.

```shell-session
$ oc get controlplanemachineset.machine.openshift.io cluster \
  --namespace openshift-machine-api
```

`Active` 의 결과는 `ControlPlaneMachineSet` CR이 존재하고 활성화되어 있음을 나타냅니다. 관리자 작업이 필요하지 않습니다.

`Inactive` 의 결과는 `ControlPlaneMachineSet` CR이 존재하지만 활성화되지 않았음을 나타냅니다.

`NotFound` 의 결과는 기존 `ControlPlaneMachineSet` CR이 없음을 나타냅니다.

다음 단계

컨트롤 플레인 머신 세트를 사용하려면 클러스터에 대한 올바른 설정이 있는 `ControlPlaneMachineSet` CR이 있는지 확인해야 합니다.

클러스터에 기존 CR이 있는 경우 CR의 구성이 클러스터에 적합한지 확인해야 합니다.

클러스터에 기존 CR이 없는 경우 클러스터에 대한 올바른 구성으로 클러스터를 생성해야 합니다.

추가 리소스

컨트롤 플레인 머신 세트 사용자 정의 리소스 활성화

컨트롤 플레인 머신 세트 사용자 정의 리소스 생성

#### 10.7.2. 누락된 Azure 내부 로드 밸런서 추가

Azure의 `ControlPlaneMachineSet` 및 컨트롤 플레인 `Machine` CR(사용자 정의 리소스) 모두에 `internalLoadBalancer` 매개변수가 필요합니다. 이 매개변수가 클러스터에 사전 구성되지 않은 경우 두 CR에 모두 추가해야 합니다.

이 매개변수가 Azure 공급자 사양에 있는 위치에 대한 자세한 내용은 샘플 Azure 공급자 사양을 참조하십시오. 컨트롤 플레인 `Machine` CR의 배치는 비슷합니다.

프로세스

다음 명령을 실행하여 클러스터의 컨트롤 플레인 시스템을 나열합니다.

```shell-session
$ oc get machines \
  -l machine.openshift.io/cluster-api-machine-role==master \
  -n openshift-machine-api
```

각 컨트롤 플레인 머신에 대해 다음 명령을 실행하여 CR을 편집합니다.

```shell-session
$ oc edit machine <control_plane_machine_name>
```

클러스터에 대한 올바른 세부 정보를 사용하여 `internalLoadBalancer` 매개변수를 추가하고 변경 사항을 저장합니다.

다음 명령을 실행하여 컨트롤 플레인 머신 세트 CR을 편집합니다.

```shell-session
$ oc edit controlplanemachineset.machine.openshift.io cluster \
  -n openshift-machine-api
```

클러스터에 대한 올바른 세부 정보를 사용하여 `internalLoadBalancer` 매개변수를 추가하고 변경 사항을 저장합니다.

다음 단계

기본 `RollingUpdate` 업데이트 전략을 사용하는 클러스터의 경우 Operator는 변경 사항을 컨트롤 플레인 구성에 자동으로 전파합니다.

`OnDelete` 업데이트 전략을 사용하도록 구성된 클러스터의 경우 컨트롤 플레인 시스템을 수동으로 교체해야 합니다.

추가 리소스

Microsoft Azure 공급자 사양 샘플

#### 10.7.3. 성능 저하된 etcd Operator 복구

특정 상황에서 etcd Operator의 성능이 저하될 수 있습니다.

예를 들어 수정을 수행하는 동안 머신 상태 점검에서 etcd를 호스팅하는 컨트롤 플레인 시스템을 삭제할 수 있습니다. 그 시점에서 etcd 멤버에 연결할 수 없는 경우 etcd Operator의 성능이 저하됩니다.

etcd Operator의 성능이 저하되면 Operator에서 실패한 멤버를 강제로 제거하고 클러스터 상태를 복원하려면 수동 개입이 필요합니다.

프로세스

다음 명령을 실행하여 클러스터의 컨트롤 플레인 시스템을 나열합니다.

```shell-session
$ oc get machines \
  -l machine.openshift.io/cluster-api-machine-role==master \
  -n openshift-machine-api \
  -o wide
```

다음 조건 중 하나라도 실패한 컨트롤 플레인 시스템을 나타낼 수 있습니다.

`STATE` 값이 `중지되었습니다`.

`PHASE` 값은 `Failed` 입니다.

`PHASE` 값은 10 분 이상 `Deleting` 됩니다.

중요

계속하기 전에 클러스터에 두 개의 정상 컨트롤 플레인 시스템이 있는지 확인합니다. 둘 이상의 컨트롤 플레인 시스템에서 이 절차의 작업을 수행하면 etcd 쿼럼이 손실되어 데이터가 손실될 수 있습니다.

대부분의 컨트롤 플레인 호스트가 손실되어 etcd 쿼럼이 손실된 경우 이 절차 대신 재해 복구 절차 "이전 클러스터 상태"를 따라야 합니다.

다음 명령을 실행하여 실패한 컨트롤 플레인 머신의 머신 CR을 편집합니다.

```shell-session
$ oc edit machine <control_plane_machine_name>
```

실패한 컨트롤 플레인 시스템에서 `lifecycleHooks` 매개변수의 내용을 제거하고 변경 사항을 저장합니다.

etcd Operator는 클러스터에서 실패한 머신을 제거한 다음 새 etcd 멤버를 안전하게 추가할 수 있습니다.

추가 리소스

이전 클러스터 상태로 복원

#### 10.7.4. RHOSP에서 실행되는 클러스터 업그레이드

OpenShift Container Platform 4.13 또는 이전 버전으로 생성된 RHOSP(Red Hat OpenStack Platform)에서 실행되는 클러스터의 경우 컨트롤 플레인 머신 세트를 사용하기 전에 업그레이드 후 작업을 수행해야 할 수 있습니다.

#### 10.7.4.1. 업그레이드 후 루트 볼륨 가용성 영역이 있는 시스템이 있는 RHOSP 클러스터 구성

업그레이드하는 RHOSP(Red Hat OpenStack Platform)에서 실행되는 일부 클러스터의 경우 다음 구성이 true인 경우 컨트롤 플레인 머신 세트를 사용하기 전에 머신 리소스를 수동으로 업데이트해야 합니다.

업그레이드된 클러스터는 OpenShift Container Platform 4.13 또는 이전 버전을 사용하여 생성되었습니다.

클러스터 인프라는 설치 관리자 프로비저닝입니다.

시스템은 여러 가용성 영역에 분산되어 있었습니다.

시스템은 블록 스토리지 가용성 영역이 정의되지 않은 루트 볼륨을 사용하도록 구성되었습니다.

이 절차가 필요한 이유를 이해하려면 솔루션 #7024383 을 참조하십시오.

프로세스

모든 컨트롤 플레인 시스템의 경우 환경과 일치하는 모든 컨트롤 플레인 시스템의 공급자 사양을 편집합니다. 예를 들어 머신 `master-0` 을 편집하려면 다음 명령을 입력합니다.

```shell-session
$ oc edit machine/<cluster_id>-master-0 -n openshift-machine-api
```

다음과 같습니다.

`<cluster_id>`

업그레이드된 클러스터의 ID를 지정합니다.

provider 사양에서 `rootVolume.availabilityZone` 속성 값을 사용하려는 가용성 영역의 볼륨으로 설정합니다.

```yaml
providerSpec:
  value:
    apiVersion: machine.openshift.io/v1alpha1
    availabilityZone: az0
      cloudName: openstack
    cloudsSecret:
      name: openstack-cloud-credentials
      namespace: openshift-machine-api
    flavor: m1.xlarge
    image: rhcos-4.14
    kind: OpenstackProviderSpec
    metadata:
      creationTimestamp: null
    networks:
    - filter: {}
      subnets:
      - filter:
          name: refarch-lv7q9-nodes
          tags: openshiftClusterID=refarch-lv7q9
    rootVolume:
        availabilityZone: nova
        diskSize: 30
        sourceUUID: rhcos-4.12
        volumeType: fast-0
    securityGroups:
    - filter: {}
      name: refarch-lv7q9-master
    serverGroupName: refarch-lv7q9-master
    serverMetadata:
      Name: refarch-lv7q9-master
      openshiftClusterID: refarch-lv7q9
    tags:
    - openshiftClusterID=refarch-lv7q9
    trunk: true
    userDataSecret:
      name: master-user-data
```

1. 영역 이름을 이 값으로 설정합니다.

참고

초기 클러스터 배포 후 머신 리소스를 편집하거나 다시 생성한 경우 구성에 대해 이러한 단계를 조정해야 할 수 있습니다.

RHOSP 클러스터에서 시스템의 루트 볼륨의 가용성 영역을 찾아 값으로 사용합니다.

다음 명령을 실행하여 컨트롤 플레인 머신 세트 리소스에 대한 정보를 검색합니다.

```shell-session
$ oc describe controlplanemachineset.machine.openshift.io/cluster --namespace openshift-machine-api
```

다음 명령을 실행하여 리소스를 편집합니다.

```shell-session
$ oc edit controlplanemachineset.machine.openshift.io/cluster --namespace openshift-machine-api
```

해당 리소스의 경우 `spec.state` 속성 값을 `Active` 로 설정하여 클러스터의 컨트롤 플레인 머신 세트를 활성화합니다.

Cluster Control Plane Machine Set Operator에서 컨트롤 플레인을 관리할 수 있습니다.

#### 10.7.4.2. 업그레이드 후 가용성 영역이 있는 컨트롤 플레인 시스템이 있는 RHOSP 클러스터 구성

업그레이드하는 RHOSP(Red Hat OpenStack Platform)에서 실행되는 일부 클러스터의 경우 다음 구성이 true인 경우 컨트롤 플레인 머신 세트를 사용하기 전에 머신 리소스를 수동으로 업데이트해야 합니다.

업그레이드된 클러스터는 OpenShift Container Platform 4.13 또는 이전 버전을 사용하여 생성되었습니다.

클러스터 인프라는 설치 관리자 프로비저닝입니다.

컨트롤 플레인 시스템은 여러 컴퓨팅 가용 영역에 분산되어 있었습니다.

이 절차가 필요한 이유를 이해하려면 솔루션 #7013893 을 참조하십시오.

프로세스

`master-1` 및 `master-2` 컨트롤 플레인 시스템의 경우 편집을 위해 공급자 사양을 엽니다. 예를 들어 첫 번째 머신을 편집하려면 다음 명령을 입력합니다.

```shell-session
$ oc edit machine/<cluster_id>-master-1 -n openshift-machine-api
```

다음과 같습니다.

`<cluster_id>`

업그레이드된 클러스터의 ID를 지정합니다.

`master-1` 및 `master-2` 컨트롤 플레인 시스템의 경우 공급자 사양의 `serverGroupName` 속성 값을 머신 `master-0` 과 일치하도록 편집합니다.

```yaml
providerSpec:
  value:
    apiVersion: machine.openshift.io/v1alpha1
    availabilityZone: az0
      cloudName: openstack
    cloudsSecret:
      name: openstack-cloud-credentials
      namespace: openshift-machine-api
    flavor: m1.xlarge
    image: rhcos-4.20
    kind: OpenstackProviderSpec
    metadata:
      creationTimestamp: null
    networks:
    - filter: {}
      subnets:
      - filter:
          name: refarch-lv7q9-nodes
          tags: openshiftClusterID=refarch-lv7q9
    securityGroups:
    - filter: {}
      name: refarch-lv7q9-master
    serverGroupName: refarch-lv7q9-master-az0
    serverMetadata:
      Name: refarch-lv7q9-master
      openshiftClusterID: refarch-lv7q9
    tags:
    - openshiftClusterID=refarch-lv7q9
    trunk: true
    userDataSecret:
      name: master-user-data
```

1. 이 값은 시스템 `master-0`, `master-1` 및 `master-3` 의 경우 일치해야 합니다.

참고

초기 클러스터 배포 후 머신 리소스를 편집하거나 다시 생성한 경우 구성에 대해 이러한 단계를 조정해야 할 수 있습니다.

RHOSP 클러스터에서 컨트롤 플레인 인스턴스가 있는 서버 그룹을 찾아 값으로 사용합니다.

다음 명령을 실행하여 컨트롤 플레인 머신 세트 리소스에 대한 정보를 검색합니다.

```shell-session
$ oc describe controlplanemachineset.machine.openshift.io/cluster --namespace openshift-machine-api
```

다음 명령을 실행하여 리소스를 편집합니다.

```shell-session
$ oc edit controlplanemachineset.machine.openshift.io/cluster --namespace openshift-machine-api
```

해당 리소스의 경우 `spec.state` 속성 값을 `Active` 로 설정하여 클러스터의 컨트롤 플레인 머신 세트를 활성화합니다.

Cluster Control Plane Machine Set Operator에서 컨트롤 플레인을 관리할 수 있습니다.

### 10.8. 컨트롤 플레인 머신 세트 비활성화

활성화된 `ControlPlaneMachineSet` CR(사용자 정의 리소스)의 `.spec.state` 필드는 `Active` 에서 `Inactive` 로 변경할 수 없습니다. 컨트롤 플레인 머신 세트를 비활성화하려면 클러스터에서 제거되도록 CR을 삭제해야 합니다.

CR을 삭제하면 컨트롤 플레인 머신 세트 Operator에서 정리 작업을 수행하고 컨트롤 플레인 머신 세트를 비활성화합니다. 그런 다음 Operator는 클러스터에서 CR을 제거하고 기본 설정으로 비활성 컨트롤 플레인 머신 세트를 생성합니다.

#### 10.8.1. 컨트롤 플레인 머신 세트 삭제

클러스터에서 컨트롤 플레인 머신 세트를 사용하여 컨트롤 플레인 시스템 관리를 중지하려면 `ControlPlaneMachineSet` 사용자 정의 리소스(CR)를 삭제해야 합니다.

프로세스

다음 명령을 실행하여 컨트롤 플레인 머신 세트 CR을 삭제합니다.

```shell-session
$ oc delete controlplanemachineset.machine.openshift.io cluster \
  -n openshift-machine-api
```

검증

컨트롤 플레인 머신 세트 사용자 정의 리소스 상태를 확인합니다. `Inactive` 의 결과는 제거 및 교체 프로세스가 성공했음을 나타냅니다. `ControlPlaneMachineSet` CR이 존재하지만 활성화되지는 않습니다.

#### 10.8.2. 컨트롤 플레인 머신 세트 사용자 정의 리소스 상태 확인

`ControlPlaneMachineSet` CR(사용자 정의 리소스)의 존재 및 상태를 확인할 수 있습니다.

프로세스

다음 명령을 실행하여 CR의 상태를 확인합니다.

```shell-session
$ oc get controlplanemachineset.machine.openshift.io cluster \
  --namespace openshift-machine-api
```

`Active` 의 결과는 `ControlPlaneMachineSet` CR이 존재하고 활성화되어 있음을 나타냅니다. 관리자 작업이 필요하지 않습니다.

`Inactive` 의 결과는 `ControlPlaneMachineSet` CR이 존재하지만 활성화되지 않았음을 나타냅니다.

`NotFound` 의 결과는 기존 `ControlPlaneMachineSet` CR이 없음을 나타냅니다.

#### 10.8.3. 컨트롤 플레인 머신 세트 다시 활성화

컨트롤 플레인 머신 세트를 다시 활성화하려면 CR의 구성이 클러스터에 적합한지 확인하고 활성화해야 합니다.

추가 리소스

컨트롤 플레인 머신 세트 사용자 정의 리소스 활성화

### 10.9. 컨트롤 플레인 시스템 수동 스케일링

베어 메탈 인프라에 클러스터를 설치할 때 클러스터의 컨트롤 플레인 노드를 4개 또는 5개로 수동으로 확장할 수 있습니다. 성능이 저하된 상태에서 클러스터를 복구하거나, 깊은 수준 디버깅을 수행하거나, 복잡한 시나리오에서 컨트롤 플레인의 안정성 및 보안을 보장해야 하는 경우 이 사용 사례를 고려하십시오.

중요

Red Hat은 베어 메탈 인프라에서만 4 또는 5개의 컨트롤 플레인 노드가 있는 클러스터를 지원합니다.

#### 10.9.1. 클러스터에 컨트롤 플레인 노드 추가

베어 메탈 인프라에 클러스터를 설치할 때 클러스터의 컨트롤 플레인 노드를 4개 또는 5개로 수동으로 확장할 수 있습니다. 절차의 예제에서는 `node-5` 를 새 컨트롤 플레인 노드로 사용합니다.

사전 요구 사항

컨트롤 플레인 노드가 3개 이상인 정상 클러스터가 설치되어 있습니다.

postinstalltion 작업으로 클러스터에 추가하려는 단일 컨트롤 플레인 노드를 생성했습니다.

프로세스

다음 명령을 입력하여 새 컨트롤 플레인 노드에 대해 보류 중인 인증서 서명 요청(CSR)을 검색합니다.

```shell-session
$ oc get csr | grep Pending
```

다음 명령을 입력하여 컨트롤 플레인 노드에 보류 중인 모든 CSR을 승인합니다.

```shell-session
$ oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve
```

중요

설치를 완료하려면 CSR을 승인해야 합니다.

다음 명령을 입력하여 컨트롤 플레인 노드가 `Ready` 상태에 있는지 확인합니다.

```shell-session
$ oc get nodes
```

참고

설치 관리자 프로비저닝 인프라에서 etcd Operator는 Machine API를 사용하여 컨트롤 플레인을 관리하고 etcd 쿼럼을 확인합니다. 그런 다음 Machine API는 `Machine` CR을 사용하여 기본 컨트롤 플레인 노드를 표시하고 관리합니다.

`BareMetalHost` 및 `Machine` CR을 생성하여 컨트롤 플레인 노드의 `Node` CR에 연결합니다.

다음 예와 같이 고유한 `.metadata.name` 값을 사용하여 `BareMetalHost` CR을 생성합니다.

```yaml
apiVersion: metal3.io/v1alpha1
kind: BareMetalHost
metadata:
  name: node-5
  namespace: openshift-machine-api
spec:
  automatedCleaningMode: metadata
  bootMACAddress: 00:00:00:00:00:02
  bootMode: UEFI
  customDeploy:
    method: install_coreos
  externallyProvisioned: true
  online: true
  userData:
    name: master-user-data-managed
    namespace: openshift-machine-api
# ...
```

다음 명령을 입력하여 `BareMetalHost` CR을 적용합니다.

```shell-session
$ oc apply -f <filename>
```

1. <filename>을 `BareMetalHost` CR의 이름으로 바꿉니다.

다음 예와 같이 고유한 `.metadata.name` 값을 사용하여 `Machine` CR을 생성합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: Machine
metadata:
  annotations:
    machine.openshift.io/instance-state: externally provisioned
    metal3.io/BareMetalHost: openshift-machine-api/node-5
  finalizers:
  - machine.machine.openshift.io
  labels:
    machine.openshift.io/cluster-api-cluster: <cluster_name>
    machine.openshift.io/cluster-api-machine-role: master
    machine.openshift.io/cluster-api-machine-type: master
  name: node-5
  namespace: openshift-machine-api
spec:
  metadata: {}
  providerSpec:
    value:
      apiVersion: baremetal.cluster.k8s.io/v1alpha1
      customDeploy:
        method: install_coreos
      hostSelector: {}
      image:
        checksum: ""
        url: ""
      kind: BareMetalMachineProviderSpec
      metadata:
        creationTimestamp: null
      userData:
        name: master-user-data-managed
# ...
```

1. & `lt;cluster_name` >을 특정 클러스터의 이름으로 바꿉니다(예: `test-day2-1-6qv96`).

다음 명령을 실행하여 클러스터 이름을 가져옵니다.

```shell-session
$ oc get infrastructure cluster -o=jsonpath='{.status.infrastructureName}{"\n"}'
```

다음 명령을 입력하여 `머신` CR을 적용합니다.

```shell-session
$ oc apply -f <filename>
```

1. & `lt;filename&` gt;을 `Machine` CR의 이름으로 바꿉니다.

다음 명령스크립트를 실행하여 `BareMetalHost`, `Machine` 및 `Node` 오브젝트를 연결합니다.

```shell
link-machine-and-node.sh
```

다음 스크립트를 로컬 머신에 복사합니다.

```shell
link-machine-and-node.sh
```

```plaintext
#!/bin/bash

# Credit goes to
# https://bugzilla.redhat.com/show_bug.cgi?id=1801238.
# This script will link Machine object
# and Node object. This is needed
# in order to have IP address of
# the Node present in the status of the Machine.

set -e

machine="$1"
node="$2"

if [ -z "$machine" ] || [ -z "$node" ]; then
    echo "Usage: $0 MACHINE NODE"
    exit 1
fi

node_name=$(echo "${node}" | cut -f2 -d':')

oc proxy &
proxy_pid=$!
function kill_proxy {
    kill $proxy_pid
}
trap kill_proxy EXIT SIGINT

HOST_PROXY_API_PATH="http://localhost:8001/apis/metal3.io/v1alpha1/namespaces/openshift-machine-api/baremetalhosts"

function print_nics() {
    local ips
    local eob
    declare -a ips

    readarray -t ips < <(echo "${1}" \
                         | jq '.[] | select(. | .type == "InternalIP") | .address' \
                         | sed 's/"//g')

    eob=','
    for (( i=0; i<${#ips[@]}; i++ )); do
        if [ $((i+1)) -eq ${#ips[@]} ]; then
            eob=""
        fi
        cat <<- EOF
          {
            "ip": "${ips[$i]}",
            "mac": "00:00:00:00:00:00",
            "model": "unknown",
            "speedGbps": 10,
            "vlanId": 0,
            "pxe": true,
            "name": "eth1"
          }${eob}
EOF
    done
}

function wait_for_json() {
    local name
    local url
    local curl_opts
    local timeout

    local start_time
    local curr_time
    local time_diff

    name="$1"
    url="$2"
    timeout="$3"
    shift 3
    curl_opts="$@"
    echo -n "Waiting for $name to respond"
    start_time=$(date +%s)
    until curl -g -X GET "$url" "${curl_opts[@]}" 2> /dev/null | jq '.' 2> /dev/null > /dev/null; do
        echo -n "."
        curr_time=$(date +%s)
        time_diff=$((curr_time - start_time))
        if [[ $time_diff -gt $timeout ]]; then
            printf '\nTimed out waiting for %s' "${name}"
            return 1
        fi
        sleep 5
    done
    echo " Success!"
    return 0
}
wait_for_json oc_proxy "${HOST_PROXY_API_PATH}" 10 -H "Accept: application/json" -H "Content-Type: application/json"

addresses=$(oc get node -n openshift-machine-api "${node_name}" -o json | jq -c '.status.addresses')

machine_data=$(oc get machines.machine.openshift.io -n openshift-machine-api -o json "${machine}")
host=$(echo "$machine_data" | jq '.metadata.annotations["metal3.io/BareMetalHost"]' | cut -f2 -d/ | sed 's/"//g')

if [ -z "$host" ]; then
    echo "Machine $machine is not linked to a host yet." 1>&2
    exit 1
fi

# The address structure on the host doesn't match the node, so extract
# the values we want into separate variables so we can build the patch
# we need.
hostname=$(echo "${addresses}" | jq '.[] | select(. | .type == "Hostname") | .address' | sed 's/"//g')

set +e
read -r -d '' host_patch << EOF
{
  "status": {
    "hardware": {
      "hostname": "${hostname}",
      "nics": [
$(print_nics "${addresses}")
      ],
      "systemVendor": {
        "manufacturer": "Red Hat",
        "productName": "product name",
        "serialNumber": ""
      },
      "firmware": {
        "bios": {
          "date": "04/01/2014",
          "vendor": "SeaBIOS",
          "version": "1.11.0-2.el7"
        }
      },
      "ramMebibytes": 0,
      "storage": [],
      "cpu": {
        "arch": "x86_64",
        "model": "Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz",
        "clockMegahertz": 2199.998,
        "count": 4,
        "flags": []
      }
    }
  }
}
EOF
set -e

echo "PATCHING HOST"
echo "${host_patch}" | jq .

curl -s \
     -X PATCH \
     "${HOST_PROXY_API_PATH}/${host}/status" \
     -H "Content-type: application/merge-patch+json" \
     -d "${host_patch}"

oc get baremetalhost -n openshift-machine-api -o yaml "${host}"
```

다음 명령을 입력하여 스크립트를 실행 가능하게 만듭니다.

```shell-session
$ chmod +x link-machine-and-node.sh
```

다음 명령을 입력하여 스크립트를 실행합니다.

```shell-session
$ bash link-machine-and-node.sh node-5 node-5
```

참고

첫 번째 `node-5` 인스턴스는 시스템을 나타내며 두 번째 인스턴스는 노드를 나타냅니다.

검증

기존 컨트롤 플레인 노드 중 하나로 실행하여 etcd의 멤버를 확인합니다.

다음 명령을 입력하여 컨트롤 플레인 노드에 대한 원격 쉘 세션을 엽니다.

```shell-session
$ oc rsh -n openshift-etcd etcd-node-0
```

etcd 멤버를 나열합니다.

```shell-session
# etcdctl member list -w table
```

다음 명령을 입력하여 완료할 때까지 etcd Operator 설정 프로세스를 확인합니다. 예상 출력은 `PROGRESSING` 열에 `False` 를 표시합니다.

```shell-session
$ oc get clusteroperator etcd
```

다음 명령을 실행하여 etcd 상태를 확인합니다.

컨트롤 플레인 노드에 대한 원격 쉘 세션을 엽니다.

```shell-session
$ oc rsh -n openshift-etcd etcd-node-0
```

끝점 상태를 확인합니다. 예상 `출력은 끝점에` 대해 정상입니다.

```shell-session
# etcdctl endpoint health
```

다음 명령을 입력하여 모든 노드가 준비되었는지 확인합니다. 예상 출력에는 각 노드 항목 옆에 `Ready` 상태가 표시됩니다.

```shell-session
$ oc get nodes
```

다음 명령을 입력하여 클러스터 Operator를 모두 사용할 수 있는지 확인합니다. 예상 출력은 각 Operator를 나열하고 각 나열된 Operator 옆에 `True` 로 사용 가능한 상태를 표시합니다.

```shell-session
$ oc get ClusterOperators
```

다음 명령을 입력하여 클러스터 버전이 올바른지 확인합니다.

```shell-session
$ oc get ClusterVersion
```

```shell-session
NAME      VERSION   AVAILABLE   PROGRESSING   SINCE   STATUS
version   OpenShift Container Platform.5    True        False         5h57m   Cluster version is OpenShift Container Platform.5
```

### 11.1. 클러스터 API 정보

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

Cluster API 는 OpenShift Container Platform에 AWS(Amazon Web Services), Google Cloud, Microsoft Azure, RHOSP(Red Hat OpenStack Platform), VMware vSphere 및 베어 메탈의 기술 프리뷰로 통합된 업스트림 프로젝트입니다.

#### 11.1.1. 클러스터 API 개요

Cluster API를 사용하여 OpenShift Container Platform 클러스터에서 컴퓨팅 머신 세트 및 컴퓨팅 머신을 생성하고 관리할 수 있습니다. 이 기능은 Machine API를 사용하여 머신 관리하는 것에 대한 대안이나 추가 기능입니다.

OpenShift Container Platform 4.20 클러스터의 경우 Cluster API를 사용하여 클러스터 설치가 완료된 후 노드 호스트 프로비저닝 관리 작업을 수행할 수 있습니다. 이 시스템을 사용하면 퍼블릭 또는 프라이빗 클라우드 인프라에 더하여 탄력적이고 동적인 프로비저닝 방법을 사용할 수 있습니다.

Cluster API 기술 프리뷰를 사용하면 지원되는 공급자를 위해 OpenShift Container Platform 클러스터에서 컴퓨팅 머신 및 컴퓨팅 머신 세트를 생성할 수 있습니다. Machine API에서 사용할 수 없는 이 구현에서 사용하도록 설정된 기능을 탐색할 수도 있습니다.

#### 11.1.1.1. 클러스터 API의 이점

OpenShift Container Platform 사용자 및 개발자는 Cluster API를 사용하여 다음과 같은 이점을 얻을 수 있습니다.

Machine API에서 지원하지 않을 수 있는 업스트림 커뮤니티 Cluster API 인프라 공급자를 사용하는 옵션입니다.

인프라 공급업체를 위한 머신 컨트롤러를 유지 관리하는 타사와 협업할 수 있는 기회

OpenShift Container Platform에서 인프라 관리에 동일한 Kubernetes 툴 세트를 사용하는 기능

Machine API에서 사용할 수 없는 기능을 지원하는 클러스터 API를 사용하여 컴퓨팅 머신 세트를 생성하는 기능입니다.

#### 11.1.1.2. 클러스터 API 제한 사항

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능이며 다음과 같은 제한 사항이 있습니다.

이 기능을 사용하려면 `TechPreviewNoUpgrade` 기능 세트를 활성화해야 합니다.

중요

이 기능 세트를 활성화하면 실행 취소할 수 없으며 마이너 버전 업데이트가 허용되지 않습니다.

AWS(Amazon Web Services), Google Cloud, Microsoft Azure, RHOSP(Red Hat OpenStack Platform), VMware vSphere 및 베어 메탈 클러스터에서는 클러스터 API를 사용할 수 있습니다.

클러스터 API에 필요한 기본 리소스 중 일부를 수동으로 생성해야 합니다. 자세한 내용은 "Cluster API 시작하기"를 참조하십시오.

클러스터 API를 사용하여 컨트롤 플레인 시스템을 관리할 수 없습니다.

Machine API에서 Cluster API로 생성한 기존 컴퓨팅 머신 세트 마이그레이션은 지원되지 않습니다.

Machine API와의 전체 기능 패리티를 사용할 수 없습니다.

Cluster API를 사용하는 클러스터의 경우 OpenShift CLI() 명령은 Machine API 오브젝트를 통해 Cluster API 오브젝트를 우선시합니다. 이 동작은 Cluster API 및 Machine API 둘 다에 표시되는 모든 오브젝트에 대해 작동하는 아래 명령에 영향을 미칩니다.

```shell
oc
```

```shell
oc
```

자세한 내용 및 이 문제에 대한 해결 방법은 문제 해결 콘텐츠에서 "CLI를 사용할 때 의도한 오브젝트 참조"를 참조하십시오.

추가 리소스

기능 게이트를 사용한 기능 활성화

클러스터 API 시작하기

CLI를 사용할 때 의도된 오브젝트 참조

#### 11.1.2. 클러스터 API 아키텍처

업스트림 Cluster API의 OpenShift Container Platform 통합은 Cluster CAPI Operator에 의해 구현 및 관리됩니다. Cluster CAPI Operator 및 해당 피연산자는 `openshift-machine-api` 네임스페이스를 사용하는 Machine API와 달리 `openshift-cluster-api` 네임스페이스에 프로비저닝됩니다.

#### 11.1.2.1. Cluster CAPI Operator

Cluster CAPI Operator는 Cluster API 리소스의 라이프사이클을 유지 관리하는 OpenShift Container Platform Operator입니다. 이 Operator는 OpenShift Container Platform 클러스터 내에서 Cluster API 프로젝트 배포와 관련된 모든 관리 작업을 담당합니다.

Cluster API 사용을 허용하도록 클러스터가 올바르게 구성된 경우 Cluster CAPI Operator는 클러스터에 Cluster API 구성 요소를 설치합니다.

자세한 내용은 Cluster Operators 참조 콘텐츠의 "Cluster CAPI Operator" 항목을 참조하십시오.

추가 리소스

Cluster CAPI Operator

#### 11.1.2.2. 클러스터 API 기본 리소스

Cluster API는 다음과 같은 기본 리소스로 구성됩니다. 이 기능의 기술 프리뷰의 경우 `openshift-cluster-api` 네임스페이스에서 이러한 리소스 중 일부를 수동으로 생성해야 합니다.

Cluster

클러스터 API에서 관리하는 클러스터를 나타내는 기본 단위입니다.

인프라 클러스터

지역 및 서브넷과 같이 클러스터 공유의 모든 컴퓨팅 머신 세트 속성을 정의하는 공급자별 리소스입니다.

머신 템플릿

컴퓨팅 머신 세트에서 생성하는 시스템의 속성을 정의하는 공급자별 템플릿입니다.

머신 세트

시스템 그룹입니다.

컴퓨팅 머신 세트는 머신에 연관되어 있으며 복제본 세트는 pod에 연관되어 있습니다. 머신을 추가하거나 축소하려면 컴퓨팅 요구 사항에 맞게 컴퓨팅 머신 세트 사용자 정의 리소스의 `replicas` 필드를 변경합니다.

클러스터 API를 사용하면 컴퓨팅 머신 세트는 `Cluster` 오브젝트 및 공급자별 머신 템플릿을 참조합니다.

머신

노드의 호스트를 설명하는 기본 단위입니다.

Cluster API는 머신 템플릿의 구성을 기반으로 시스템을 생성합니다.

### 11.2. 클러스터 API 시작하기

Machine API 및 Cluster API는 유사한 리소스가 있는 별도의 API 그룹입니다. 이러한 API 그룹을 사용하여 OpenShift Container Platform 클러스터에서 인프라 리소스 관리를 자동화할 수 있습니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

3개의 제어 평면 노드, 3개의 컴퓨팅 노드가 있고 기본 구성 옵션을 사용하는 표준 OpenShift Container Platform 클러스터를 설치하는 경우 설치 프로그램은 `openshift-machine-api` 네임스페이스에 다음 인프라 리소스를 프로비저닝합니다.

3개의 컨트롤 플레인 머신을 관리하는 하나의 컨트롤 플레인 머신 세트입니다.

3개의 컴퓨팅 머신을 관리하는 하나 이상의 컴퓨팅 머신 세트입니다.

스팟 인스턴스를 관리하는 하나의 머신 상태 점검입니다.

Cluster API를 사용하여 인프라 리소스 관리를 지원하는 클러스터를 설치할 때 설치 프로그램은 `openshift-cluster-api` 네임스페이스에 다음 리소스를 프로비저닝합니다.

클러스터 리소스 1개

공급자별 인프라 클러스터 리소스 1개

Machine API 리소스를 클러스터 API 리소스로 마이그레이션하는 클러스터에서는 양방향 동기화 컨트롤러에서 이러한 기본 리소스를 자동으로 생성합니다. 자세한 내용은 클러스터 API 리소스로 머신 API 리소스 마이그레이션을 참조하십시오.

#### 11.2.1. Cluster API 기본 리소스 생성

Machine API 리소스를 클러스터 API 리소스로 마이그레이션하지 않는 클러스터의 경우 `openshift-cluster-api` 네임스페이스에서 다음 Cluster API 리소스를 수동으로 생성해야 합니다.

컴퓨팅 머신 세트에 해당하는 하나 이상의 머신 템플릿입니다.

3개의 컴퓨팅 머신을 관리하는 하나 이상의 컴퓨팅 머신 세트입니다.

#### 11.2.1.1. 클러스터 API 머신 템플릿 생성

YAML 매니페스트 파일을 생성하고 OpenShift CLI()로 적용하여 공급자별 머신 템플릿 리소스를 생성할 수 있습니다.

```shell
oc
```

사전 요구 사항

OpenShift Container Platform 클러스터를 배포했습니다.

클러스터 API 사용을 활성화했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음과 유사한 YAML 파일을 생성합니다. 이 절차에서는 & `lt;machine_template_resource_file>.yaml` 을 예제 파일 이름으로 사용합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: <machine_template_kind>
metadata:
  name: <template_name>
  namespace: openshift-cluster-api
spec:
  template:
    spec:
```

1. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다. 다음 값이 유효합니다.

| 클러스터 인프라 공급자 | 현재의 |
| --- | --- |
| AWS(Amazon Web Services) | `AWSMachineTemplate` |
| Google Cloud | `GCPMachineTemplate` |
| Microsoft Azure | `AzureMachineTemplate` |
| Red Hat OpenStack Platform (RHOSP) | `OpenStackMachineTemplate` |
| VMware vSphere | `VSphereMachineTemplate` |
| 베어 메탈 | `Metal3MachineTemplate` |

2. 머신 템플릿의 이름을 지정합니다.

3. 환경에 대한 세부 정보를 지정합니다. 이러한 매개변수는 공급자별로 다릅니다. 자세한 내용은 공급자의 샘플 Cluster API 머신 템플릿 YAML을 참조하십시오.

다음 명령을 실행하여 머신 템플릿 CR을 생성합니다.

```shell-session
$ oc create -f <machine_template_resource_file>.yaml
```

검증

다음 명령을 실행하여 머신 템플릿 CR이 생성되었는지 확인합니다.

```shell-session
$ oc get <machine_template_kind> -n openshift-cluster-api
```

여기서 `<machine_template_kind` >는 플랫폼에 해당하는 값입니다.

```plaintext
NAME              AGE
<template_name>   77m
```

추가 리소스

Amazon Web Services에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

Google Cloud에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

Microsoft Azure의 클러스터 API 머신 템플릿 리소스의 샘플 YAML

RHOSP에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

VMware vSphere에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

베어 메탈의 Cluster API 머신 템플릿 리소스의 샘플 YAML

#### 11.2.1.2. 클러스터 API 컴퓨팅 머신 세트 생성

Cluster API를 사용하여 선택한 특정 워크로드에 대한 머신 컴퓨팅 리소스를 동적으로 관리하는 컴퓨팅 머신 세트를 생성할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 배포했습니다.

클러스터 API 사용을 활성화했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

머신 템플릿 리소스가 생성되어 있습니다.

프로세스

다음과 유사한 YAML 파일을 생성합니다. 이 절차에서는 & `lt;machine_set_resource_file>.yaml` 을 예제 파일 이름으로 사용합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
  template:
    metadata:
      labels:
        test: example
    spec:
# ...
```

1. 컴퓨팅 머신 세트의 이름을 지정합니다. 클러스터 ID, 머신 역할 및 리전은 < `cluster_name>-<role>-<region` > 형식으로 이 값에 대한 일반적인 패턴을 형성합니다.

2. 클러스터 이름을 지정합니다. 다음 명령을 실행하여 클러스터 ID의 값을 가져옵니다.

```shell-session
$  oc get infrastructure cluster \
   -o jsonpath='{.status.infrastructureName}'
```

3. 환경에 대한 세부 정보를 지정합니다. 이러한 매개변수는 공급자별로 다릅니다. 자세한 내용은 공급자의 샘플 Cluster API 컴퓨팅 머신 세트 YAML을 참조하십시오.

다음 명령을 실행하여 컴퓨팅 머신 세트 CR을 생성합니다.

```shell-session
$ oc create -f <machine_set_resource_file>.yaml
```

다음 명령을 실행하여 컴퓨팅 머신 세트 CR이 생성되었는지 확인합니다.

```shell-session
$ oc get machineset.cluster.x-k8s.io -n openshift-cluster-api
```

```plaintext
NAME                 CLUSTER          REPLICAS   READY   AVAILABLE   AGE   VERSION
<machine_set_name>   <cluster_name>   1          1       1           17m
```

새 컴퓨팅 머신 세트가 사용 가능한 경우 `REPLICAS` 및 `AVAILABLE` 값이 일치합니다. 컴퓨팅 머신 세트를 사용할 수 없는 경우 몇 분 기다렸다가 명령을 다시 실행합니다.

검증

컴퓨팅 머신 세트가 필수 구성에 따라 시스템을 생성하고 있는지 확인하려면 다음 명령을 실행하여 클러스터의 시스템 및 노드 목록을 검토합니다.

클러스터 API 머신 목록을 확인합니다.

```shell-session
$ oc get machine.cluster.x-k8s.io -n openshift-cluster-api
```

```plaintext
NAME                             CLUSTER          NODENAME                                 PROVIDERID      PHASE     AGE     VERSION
<machine_set_name>-<string_id>   <cluster_name>   <ip_address>.<region>.compute.internal   <provider_id>   Running   8m23s
```

노드 목록을 확인합니다.

```shell-session
$ oc get node
```

```plaintext
NAME                                       STATUS   ROLES    AGE     VERSION
<ip_address_1>.<region>.compute.internal   Ready    worker   5h14m   v1.28.5
<ip_address_2>.<region>.compute.internal   Ready    master   5h19m   v1.28.5
<ip_address_3>.<region>.compute.internal   Ready    worker   7m      v1.28.5
```

추가 리소스

Amazon Web Services에서 클러스터 API 컴퓨팅 머신 세트 리소스의 샘플 YAML

Google Cloud에서 클러스터 API 컴퓨팅 머신 세트 리소스의 샘플 YAML

Microsoft Azure의 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

RHOSP에서 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

VMware vSphere에서 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

베어 메탈의 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

#### 11.2.2. 클러스터 API 리소스로 머신 API 리소스 마이그레이션

Machine API 리소스를 클러스터 API 리소스로 마이그레이션하는 클러스터에서는 양방향 동기화 컨트롤러에서 `openshift-cluster-api` 네임스페이스에 다음 Cluster API 리소스를 생성합니다.

컴퓨팅 머신 세트에 해당하는 하나 이상의 머신 템플릿입니다.

3개의 컴퓨팅 머신을 관리하는 하나 이상의 컴퓨팅 머신 세트입니다.

각 머신 API 컴퓨팅 머신에 해당하는 하나 이상의 클러스터 API 컴퓨팅 머신입니다.

참고

양방향 동기화 컨트롤러는 `TechPreviewNoUpgrade` 기능 세트의 `MachineAPIMigration` 기능 게이트가 활성화된 클러스터에서만 작동합니다.

이러한 클러스터 API 리소스는 설치 프로그램이 기본 구성 옵션을 사용하는 클러스터의 `openshift-machine-api` 네임스페이스에 프로비저닝하는 리소스에 해당합니다. Cluster API 리소스는 Machine API와 동일한 이름이 있으며, 해당 리소스를 나열하는 명령의 출력에 표시됩니다. 동기화 컨트롤러는 의도하지 않은 조정을 방지하기 위해 프로비저닝되지 않은 (중지된) 상태로 클러스터 API 리소스를 생성합니다.

```shell
oc get
```

지원되는 구성의 경우 권한이 있다고 간주하는 API를 변경하여 Machine API 리소스를 동등한 클러스터 API 리소스로 마이그레이션할 수 있습니다. Machine API 리소스를 Cluster API로 마이그레이션하면 리소스 관리를 Cluster API로 전송합니다.

Cluster API를 사용하도록 Machine API 리소스를 마이그레이션하면 프로덕션 클러스터에서 Cluster API를 사용하기 전에 모든 항목이 예상대로 작동하는지 확인할 수 있습니다. Machine API 리소스를 동등한 Cluster API 리소스로 마이그레이션한 후 새 리소스를 검사하여 기능 및 구성이 원래 Machine API 리소스와 일치하는지 확인할 수 있습니다.

컴퓨팅 머신 세트의 권한 있는 API를 변경하면 컴퓨팅 머신 세트에서 관리하는 기존 컴퓨팅 시스템은 원래의 권한 있는 API를 유지합니다. 결과적으로 다른 권한 있는 API를 사용하는 머신을 관리하는 컴퓨팅 머신 세트는 이러한 API 유형 간에 마이그레이션을 지원하는 클러스터에서 유효하고 예상되는 발생입니다.

컴퓨팅 머신에 대해 권한 있는 API를 변경하면 시스템을 백업하는 기본 인프라의 인스턴스가 다시 생성되거나 다시 프로비저닝되지 않습니다. 레이블, 태그, 테인트 또는 주석 수정과 같은 인플레이스 변경 사항은 API 그룹이 머신을 백업하는 기본 인스턴스를 변경할 수 있는 유일한 변경 사항입니다.

참고

지원되는 인프라 유형에서만 일부 리소스를 마이그레이션할 수 있습니다.

| 인프라 | 컴퓨팅 시스템 | 컴퓨팅 머신 세트 | 머신 상태 점검 | 컨트롤 플레인 머신 세트 | Cluster autoscaler |
| --- | --- | --- | --- | --- | --- |
| AWS | 기술 프리뷰 | 기술 프리뷰 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 |
| 기타 모든 인프라 유형 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 |

#### 11.2.2.1. 신뢰할 수 있는 API 유형의 컴퓨팅 시스템

컴퓨팅 시스템의 권한 있는 API는 이를 생성하는 Machine API 컴퓨팅 머신 세트의 `.spec.authoritativeAPI` 및 `.spec.template.spec.authoritativeAPI` 필드의 값에 따라 다릅니다.

| `.spec.authoritativeAPI` value | `ClusterAPI` | `ClusterAPI` | `MachineAPI` | `MachineAPI` |
| --- | --- | --- | --- | --- |
| `.spec.template.spec.authoritativeAPI` value | `ClusterAPI` | `MachineAPI` | `MachineAPI` | `ClusterAPI` |
| 새 컴퓨팅 시스템에 대한 `authoritativeAPI` 값 | `ClusterAPI` | `ClusterAPI` | `MachineAPI` | `ClusterAPI` |

참고

`.spec.authoritativeAPI` 값이 `ClusterAPI` 인 경우 Machine API 머신 세트가 권한이 없으며 `.spec.template.spec.authoritativeAPI` 값이 사용되지 않습니다. 결과적으로 `Machine API` 를 사용하여 권한 있는 대로 컴퓨팅 머신을 생성하는 유일한 조합은 `.spec.authoritativeAPI` 및 `.spec.template.spec.authoritativeAPI` 값이 MachineAPI인 입니다.

#### 11.2.2.2. 클러스터 API를 사용하도록 머신 API 리소스 마이그레이션

개별 Machine API 오브젝트를 동등한 Cluster API 오브젝트로 마이그레이션할 수 있습니다.

중요

클러스터 API를 사용하도록 머신 API 리소스를 마이그레이션하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

사전 요구 사항

지원되는 인프라 유형에 OpenShift Container Platform 클러스터를 배포했습니다.

클러스터 API 사용을 활성화했습니다.

`TechPreviewNoUpgrade` 기능 세트에서 `MachineAPIMigration` 기능 게이트를 활성화했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터 API 리소스로 마이그레이션할 Machine API 리소스를 식별합니다.

```shell-session
$ oc get <resource_kind> -n openshift-machine-api
```

여기서 `<resource_kind` >는 다음 값 중 하나입니다.

`machine.machine.openshift.io`

컴퓨팅 또는 컨트롤 플레인 시스템에 대한 리소스 종류의 정규화된 이름입니다.

`machineset.machine.openshift.io`

컴퓨팅 머신 세트의 리소스 유형의 정규화된 이름입니다.

다음 명령을 실행하여 리소스 사양을 편집합니다.

```shell-session
$ oc edit <resource_kind>/<resource_name> -n openshift-machine-api
```

다음과 같습니다.

`<resource_kind>`

`machineset.machine.openshift.io` 를 사용하여 `machine.machine.openshift.io` 또는 컴퓨팅 머신 세트를 사용하여 컴퓨팅 머신을 지정합니다.

`<resource_name>`

Cluster API 리소스로 마이그레이션할 Machine API 리소스의 이름을 지정합니다.

리소스 사양에서 `spec.authoritativeAPI` 필드의 값을 업데이트합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: <resource_kind>
metadata:
  name: <resource_name>
  [...]
spec:
  authoritativeAPI: ClusterAPI
  [...]
status:
  authoritativeAPI: MachineAPI
  [...]
```

1. 리소스 종류는 리소스 유형에 따라 다릅니다. 예를 들어 컴퓨팅 머신 세트의 리소스 종류는 `MachineSet` 이고 컴퓨팅 머신의 리소스 종류는 `Machine` 입니다.

2. 마이그레이션할 리소스의 이름입니다.

3. 이 리소스를 사용할 권한 있는 API를 지정합니다. 예를 들어 Machine API 리소스를 클러스터 API로 마이그레이션하려면 `ClusterAPI` 를 지정합니다.

4. 현재 권한 있는 API의 값입니다. 이 값은 현재 이 리소스를 관리하는 API를 나타냅니다. 사양의 이 부분에서 값을 변경하지 마십시오.

검증

다음 명령을 실행하여 변환 상태를 확인합니다.

```shell-session
$ oc -n openshift-machine-api get <resource_kind>/<resource_name> -o json | jq .status.authoritativeAPI
```

다음과 같습니다.

`<resource_kind>`

`machineset.machine.openshift.io` 를 사용하여 `machine.machine.openshift.io` 또는 컴퓨팅 머신 세트를 사용하여 컴퓨팅 머신을 지정합니다.

`<resource_name>`

Cluster API 리소스로 마이그레이션할 Machine API 리소스의 이름을 지정합니다.

변환이 진행되는 동안 이 명령은 `Migrating` 값을 반환합니다. 이 값이 장기간 지속되는 경우 `openshift-cluster-api` 네임스페이스에서 `cluster-capi-operator` 배포의 로그를 확인하고 잠재적인 문제를 확인합니다.

변환이 완료되면 이 명령은 `ClusterAPI` 값을 반환합니다.

#### 11.2.2.3. Machine API 컴퓨팅 머신 세트를 사용하여 클러스터 API 컴퓨팅 머신 배포

클러스터 API 컴퓨팅 머신을 배포하도록 머신 API 컴퓨팅 머신 세트를 구성할 수 있습니다. 이 프로세스를 사용하면 Cluster API 컴퓨팅 머신 세트를 생성하고 확장하지 않고도 Cluster API 컴퓨팅 머신 생성 워크플로를 테스트할 수 있습니다.

이 구성이 포함된 머신 API 컴퓨팅 머신 세트는 Cluster API를 권한 있는 것으로 사용하는 권한 없는 머신 API 컴퓨팅 머신을 생성합니다. 그런 다음 양방향 동기화 컨트롤러는 기본 인프라에서 프로비저닝하는 해당 권한 있는 클러스터 API 머신을 생성합니다.

중요

Machine API 컴퓨팅 머신 세트를 사용하여 클러스터 API 컴퓨팅 머신을 배포하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

사전 요구 사항

지원되는 인프라 유형에 OpenShift Container Platform 클러스터를 배포했습니다.

클러스터 API 사용을 활성화했습니다.

`TechPreviewNoUpgrade` 기능 세트에서 `MachineAPIMigration` 기능 게이트를 활성화했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터에 있는 Machine API 컴퓨팅 머신 세트를 나열하세요.

```shell-session
$ oc get machineset.machine.openshift.io -n openshift-machine-api
```

다음 명령을 실행하여 리소스 사양을 편집합니다.

```shell-session
$ oc edit machineset.machine.openshift.io <machine_set_name> \
  -n openshift-machine-api
```

여기서 `<machine_set_name` >은 클러스터 API 컴퓨팅 머신을 배포하도록 구성할 Machine API 컴퓨팅 머신 세트의 이름입니다.

리소스 사양에서 `spec.template.spec.authoritativeAPI` 필드의 값을 업데이트합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  [...]
  name: <machine_set_name>
  [...]
spec:
  authoritativeAPI: MachineAPI
  [...]
  template:
    [...]
    spec:
      authoritativeAPI: ClusterAPI
status:
  authoritativeAPI: MachineAPI
  [...]
```

1. Machine API 컴퓨팅 머신 세트의 조정되지 않은 값입니다. 사양의 이 부분에서 값을 변경하지 마십시오.

2. `ClusterAPI` 를 지정하여 클러스터 API 컴퓨팅 시스템을 배포하도록 컴퓨팅 머신 세트를 구성합니다.

3. Machine API 컴퓨팅 머신 세트의 현재 값입니다. 사양의 이 부분에서 값을 변경하지 마십시오.

검증

다음 명령을 실행하여 업데이트된 컴퓨팅 머신 세트에서 관리하는 머신을 나열합니다.

```shell-session
$ oc get machines.machine.openshift.io \
  -n openshift-machine-api \
  -l machine.openshift.io/cluster-api-machineset=<machine_set_name>
```

업데이트된 머신 세트로 생성한 머신에 올바른 구성이 있는지 확인하려면 다음 명령을 실행하여 새 머신 중 하나에 대해 CR의 `status.authoritativeAPI` 필드를 검사합니다.

```shell-session
$ oc describe machines.machine.openshift.io <machine_name> \
  -n openshift-machine-api
```

Cluster API 컴퓨팅 머신의 경우 필드 값은 `ClusterAPI` 입니다.

추가 리소스

리소스 마이그레이션 문제 해결

클러스터 API 리소스를 머신 API 리소스로 마이그레이션

### 11.3. 클러스터 API를 사용하여 머신 관리

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.3.1. 클러스터 API 머신 템플릿 수정

YAML 매니페스트 파일을 수정하고 OpenShift CLI()로 적용하여 클러스터의 머신 템플릿 리소스를 업데이트할 수 있습니다.

```shell
oc
```

사전 요구 사항

클러스터 API를 사용하는 OpenShift Container Platform 클러스터를 배포했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터의 머신 템플릿 리소스를 나열합니다.

```shell-session
$ oc get <machine_template_kind>
```

1. 플랫폼에 해당하는 값을 지정합니다. 다음 값이 유효합니다.

| 클러스터 인프라 공급자 | 현재의 |
| --- | --- |
| Amazon Web Services | `AWSMachineTemplate` |
| Google Cloud | `GCPMachineTemplate` |
| Microsoft Azure | `AzureMachineTemplate` |
| RHOSP | `OpenStackMachineTemplate` |
| VMware vSphere | `VSphereMachineTemplate` |
| 베어 메탈 | `Metal3MachineTemplate` |

```plaintext
NAME              AGE
<template_name>   77m
```

다음 명령을 실행하여 편집할 수 있는 파일에 클러스터의 머신 템플릿 리소스를 작성합니다.

```shell-session
$ oc get <machine_template_kind> <template_name> -o yaml > <template_name>.yaml
```

여기서 `<template_name` >은 클러스터의 머신 템플릿 리소스의 이름입니다.

다른 이름으로 < `template_name>.yaml` 파일의 사본을 만듭니다. 이 절차에서는 & `lt;modified_template_name>.yaml` 을 예제 파일 이름으로 사용합니다.

텍스트 편집기를 사용하여 클러스터에 대해 업데이트된 머신 템플릿 리소스를 정의하는 < `modified_template_name>.yaml` 파일을 변경합니다. 머신 템플릿 리소스를 편집할 때 다음을 관찰합니다.

`spec` 스탠자의 매개변수는 공급자별로 다릅니다. 자세한 내용은 공급자의 샘플 Cluster API 머신 템플릿 YAML을 참조하십시오.

기존 값과 다른 `metadata.name` 매개변수에 값을 사용해야 합니다.

중요

이 템플릿을 참조하는 Cluster API 컴퓨팅 머신 세트의 경우 새 머신 템플릿 리소스의 `metadata.name` 값과 일치하도록 `spec.template.spec.infrastructureRef.name` 매개변수를 업데이트해야 합니다.

다음 명령을 실행하여 머신 템플릿 CR을 적용합니다.

```shell-session
$ oc apply -f <modified_template_name>.yaml
```

1. 편집된 YAML 파일을 새 이름으로 사용합니다.

다음 단계

이 템플릿을 참조하는 Cluster API 컴퓨팅 머신 세트의 경우 새 머신 템플릿 리소스의 `metadata.name` 값과 일치하도록 `spec.template.spec.infrastructureRef.name` 매개변수를 업데이트합니다. 자세한 내용은 "CLI를 사용하여 설정된 컴퓨팅 머신 수정"을 참조하십시오.

추가 리소스

Amazon Web Services에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

Google Cloud에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

Microsoft Azure의 클러스터 API 머신 템플릿 리소스의 샘플 YAML

RHOSP에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

VMware vSphere에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

CLI를 사용하여 컴퓨팅 머신 세트 수정

#### 11.3.2. CLI를 사용하여 컴퓨팅 머신 세트 수정

컴퓨팅 머신 세트의 구성을 수정한 다음 CLI를 사용하여 변경 사항을 클러스터의 머신에 전파할 수 있습니다.

컴퓨팅 머신 세트 구성을 업데이트하면 기능을 활성화하거나 생성하는 시스템의 속성을 변경할 수 있습니다. 컴퓨팅 머신 세트를 수정할 때 변경 사항은 업데이트된 `MachineSet` CR(사용자 정의 리소스)을 저장한 후 생성된 컴퓨팅 머신에만 적용됩니다. 변경 사항은 기존 머신에는 영향을 미치지 않습니다.

참고

기본 클라우드 공급자의 변경 사항은 `Machine` 또는 `MachineSet` CR에 반영되지 않습니다. 클러스터 관리 인프라에서 인스턴스 구성을 조정하려면 클러스터 측 리소스를 사용합니다.

컴퓨팅 머신 세트를 스케일링하여 복제본 수를 두 배로 만든 다음 원래 복제본 수로 축소하여 업데이트된 구성을 반영하는 기존 머신을 새 시스템으로 교체할 수 있습니다.

다른 변경을 수행하지 않고 컴퓨팅 머신 세트를 확장해야하는 경우 머신을 삭제할 필요가 없습니다.

참고

기본적으로 OpenShift Container Platform 라우터 Pod는 컴퓨팅 머신에 배포됩니다. 라우터는 웹 콘솔을 포함한 일부 클러스터 리소스에 액세스해야 하므로 먼저 라우터 Pod를 재배치하지 않는 한 컴퓨팅 머신 세트를 `0` 으로 스케일링하지 마십시오.

이 절차의 출력 예제에서는 AWS 클러스터 값을 사용합니다.

사전 요구 사항

OpenShift Container Platform 클러스터는 클러스터 API를 사용합니다.

OpenShift CLI()를 사용하여 관리자로 클러스터에 로그인했습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 클러스터의 컴퓨팅 머신 세트를 나열합니다.

```shell-session
$ oc get machinesets.cluster.x-k8s.io -n openshift-cluster-api
```

```plaintext
NAME                          CLUSTER             REPLICAS   READY   AVAILABLE   AGE   VERSION
<compute_machine_set_name_1>  <cluster_name>      1          1       1           26m
<compute_machine_set_name_2>  <cluster_name>      1          1       1           26m
```

다음 명령을 실행하여 컴퓨팅 머신 세트를 편집합니다.

```shell-session
$ oc edit machinesets.cluster.x-k8s.io <machine_set_name> \
  -n openshift-cluster-api
```

변경 사항을 적용하기 위해 머신 세트를 스케일링할 때 필요하므로 `spec.replicas` 필드의 값을 확인합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
spec:
  replicas: 2
# ...
```

1. 이 절차의 예제에서는 `replicas` 값이 `2` 인 컴퓨팅 머신 세트를 보여줍니다.

원하는 구성 옵션을 사용하여 컴퓨팅 머신 세트 CR을 업데이트하고 변경 사항을 저장합니다.

다음 명령을 실행하여 업데이트된 컴퓨팅 머신 세트에서 관리하는 머신을 나열합니다.

```shell-session
$ oc get machines.cluster.x-k8s.io \
  -n openshift-cluster-api \
  -l cluster.x-k8s.io/set-name=<machine_set_name>
```

```plaintext
NAME                        CLUSTER          NODENAME                                    PROVIDERID                              PHASE           AGE     VERSION
<machine_name_original_1>   <cluster_name>   <original_1_ip>.<region>.compute.internal   aws:///us-east-2a/i-04e7b2cbd61fd2075   Running         4h
<machine_name_original_2>   <cluster_name>   <original_2_ip>.<region>.compute.internal   aws:///us-east-2a/i-04e7b2cbd61fd2075   Running         4h
```

업데이트된 컴퓨팅 머신 세트에서 관리하는 각 머신에 대해 다음 명령을 실행하여 `삭제` 주석을 설정합니다.

```shell-session
$ oc annotate machines.cluster.x-k8s.io/<machine_name_original_1> \
  -n openshift-cluster-api \
  cluster.x-k8s.io/delete-machine="true"
```

새 구성으로 대체 머신을 생성하려면 다음 명령을 실행하여 컴퓨팅 머신 세트를 복제본 수의 두 배로 스케일링합니다.

```shell-session
$ oc scale --replicas=4 \
  machinesets.cluster.x-k8s.io <machine_set_name> \
  -n openshift-cluster-api
```

1. 원래 예제 값 `2` 는 `4` 로 두 배가됩니다.

다음 명령을 실행하여 업데이트된 컴퓨팅 머신 세트에서 관리하는 머신을 나열합니다.

```shell-session
$ oc get machines.cluster.x-k8s.io \
  -n openshift-cluster-api \
  -l cluster.x-k8s.io/set-name=<machine_set_name>
```

```plaintext
NAME                        CLUSTER          NODENAME                                    PROVIDERID                              PHASE           AGE     VERSION
<machine_name_original_1>   <cluster_name>   <original_1_ip>.<region>.compute.internal   aws:///us-east-2a/i-04e7b2cbd61fd2075   Running         4h
<machine_name_original_2>   <cluster_name>   <original_2_ip>.<region>.compute.internal   aws:///us-east-2a/i-04e7b2cbd61fd2075   Running         4h
<machine_name_updated_1>    <cluster_name>   <updated_1_ip>.<region>.compute.internal    aws:///us-east-2a/i-04e7b2cbd61fd2075   Provisioned     55s
<machine_name_updated_2>    <cluster_name>   <updated_2_ip>.<region>.compute.internal    aws:///us-east-2a/i-04e7b2cbd61fd2075   Provisioning    55s
```

새 머신이 `Running` 단계에 있는 경우 컴퓨팅 머신 세트를 원래 복제본 수로 확장할 수 있습니다.

이전 구성으로 생성된 머신을 제거하려면 다음 명령을 실행하여 컴퓨팅 머신 세트를 원래 복제본 수로 확장합니다.

```shell-session
$ oc scale --replicas=2 \
  machinesets.cluster.x-k8s.io <machine_set_name> \
  -n openshift-cluster-api
```

1. 원래 예제 값인 `2` 입니다.

검증

업데이트된 머신 세트로 생성된 머신에 올바른 구성이 있는지 확인하려면 다음 명령을 실행하여 새 머신 중 하나에 대해 CR의 관련 필드를 검사합니다.

```shell-session
$ oc describe machines.cluster.x-k8s.io <machine_name_updated_1> \
  -n openshift-cluster-api
```

업데이트된 구성이 없는 컴퓨팅 머신이 삭제되었는지 확인하려면 다음 명령을 실행하여 업데이트된 컴퓨팅 시스템 세트에서 관리하는 머신을 나열합니다.

```shell-session
$ oc get machines.cluster.x-k8s.io \
  -n openshift-cluster-api \
  cluster.x-k8s.io/set-name=<machine_set_name>
```

```plaintext
NAME                        CLUSTER          NODENAME                                    PROVIDERID                              PHASE      AGE     VERSION
<machine_name_original_1>   <cluster_name>   <original_1_ip>.<region>.compute.internal   aws:///us-east-2a/i-04e7b2cbd61fd2075   Running    18m
<machine_name_original_2>   <cluster_name>   <original_2_ip>.<region>.compute.internal   aws:///us-east-2a/i-04e7b2cbd61fd2075   Running    18m
<machine_name_updated_1>    <cluster_name>   <updated_1_ip>.<region>.compute.internal    aws:///us-east-2a/i-04e7b2cbd61fd2075   Running    18m
<machine_name_updated_2>    <cluster_name>   <updated_2_ip>.<region>.compute.internal    aws:///us-east-2a/i-04e7b2cbd61fd2075   Running    18m
```

```plaintext
NAME                        CLUSTER          NODENAME                                    PROVIDERID                              PHASE      AGE     VERSION
<machine_name_updated_1>    <cluster_name>   <updated_1_ip>.<region>.compute.internal    aws:///us-east-2a/i-04e7b2cbd61fd2075   Running    18m
<machine_name_updated_2>    <cluster_name>   <updated_2_ip>.<region>.compute.internal    aws:///us-east-2a/i-04e7b2cbd61fd2075   Running    18m
```

추가 리소스

Amazon Web Services에서 클러스터 API 컴퓨팅 머신 세트 리소스의 샘플 YAML

Google Cloud에서 클러스터 API 컴퓨팅 머신 세트 리소스의 샘플 YAML

Microsoft Azure의 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

RHOSP에서 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

VMware vSphere에서 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

#### 11.4.1. Amazon Web Services의 클러스터 API 구성 옵션

Cluster API 사용자 정의 리소스 매니페스트에서 값을 업데이트하여 AWS(Amazon Web Services) 클러스터 API 머신의 구성을 변경할 수 있습니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.4.1.1. Amazon Web Services 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 파일은 Amazon Web Services 클러스터에 대한 구성을 보여줍니다.

#### 11.4.1.1.1. Amazon Web Services에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

머신 템플릿 리소스는 공급자마다 다르며 컴퓨팅 머신 세트에서 생성하는 시스템의 기본 속성을 정의합니다. 머신을 생성할 때 컴퓨팅 머신 세트는 이 템플릿을 참조합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSMachineTemplate
metadata:
  name: <template_name>
  namespace: openshift-cluster-api
spec:
  template:
    spec:
      iamInstanceProfile: # ...
      instanceType: m5.large
      ignition:
        storageType: UnencryptedUserData
        version: "3.4"
      ami:
        id: # ...
      subnet:
        filters:
        - name: tag:Name
          values:
          - # ...
      additionalSecurityGroups:
      - filters:
        - name: tag:Name
          values:
          - # ...
```

1. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

2. 머신 템플릿의 이름을 지정합니다.

3. 환경에 대한 세부 정보를 지정합니다. 여기에 있는 값은 예입니다.

#### 11.4.1.1.2. Amazon Web Services에서 클러스터 API 컴퓨팅 머신 세트 리소스의 샘플 YAML

컴퓨팅 머신 세트 리소스는 생성하는 시스템의 추가 속성을 정의합니다. 컴퓨팅 머신 세트는 머신을 생성할 때 클러스터 리소스 및 머신 템플릿도 참조합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
  labels:
    cluster.x-k8s.io/cluster-name: <cluster_name>
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
      cluster.x-k8s.io/cluster-name: <cluster_name>
      cluster.x-k8s.io/set-name: <machine_set_name>
  template:
    metadata:
      labels:
        test: example
        cluster.x-k8s.io/cluster-name: <cluster_name>
        cluster.x-k8s.io/set-name: <machine_set_name>
        node-role.kubernetes.io/<role>: ""
    spec:
      bootstrap:
         dataSecretName: worker-user-data
      clusterName: <cluster_name>
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: AWSMachineTemplate
        name: <template_name>
```

1. 컴퓨팅 머신 세트의 이름을 지정합니다. 클러스터 ID, 머신 역할 및 리전은 < `cluster_name>-<role>-<region` > 형식으로 이 값에 대한 일반적인 패턴을 형성합니다.

2. 3

클러스터 ID를 클러스터 이름으로 지정합니다.

4. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

5. 머신 템플릿 이름을 지정합니다.

#### 11.4.1.2. 클러스터 API를 사용하여 Amazon Web Services 기능 활성화

Cluster API 사용자 정의 리소스 매니페스트에서 값을 업데이트하여 다음 기능을 활성화할 수 있습니다.

#### 11.4.1.2.1. Elastic Fabric Adapter 인스턴스 및 배치 그룹 옵션

기존 AWS 배치 그룹 내에서 EBS(Elastic Fabric Adapter) 인스턴스에 컴퓨팅 머신을 배포할 수 있습니다.

EFA 인스턴스에는 배치 그룹이 필요하지 않으며 EFA 구성 이외의 용도로 배치 그룹을 사용할 수 있습니다. 다음 예제에서는 EFA 및 배치 그룹을 함께 사용하여 지정된 배치 그룹 내의 시스템의 네트워크 성능을 향상시킬 수 있는 구성을 보여줍니다.

구성에 따라 컴퓨팅 머신을 배포하려면 머신 템플릿 YAML 파일에서 적절한 값을 구성합니다. 그런 다음, 머신을 배포할 때 머신 템플릿을 참조하도록 머신 세트 YAML 파일을 구성합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSMachineTemplate
# ...
spec:
  template:
    spec:
      instanceType: <supported_instance_type>
      networkInterfaceType: efa
      placementGroupName: <placement_group>
      placementGroupPartition: <placement_group_partition_number>
# ...
```

1. EFA를 지원하는 인스턴스 유형을 지정합니다.

2. `efa` 네트워크 인터페이스 유형을 지정합니다.

3. 머신을 배포할 기존 AWS 배치 그룹의 이름을 지정합니다.

4. 선택 사항: 시스템을 배포하려는 기존 AWS 배치 그룹의 파티션 번호를 지정합니다.

참고

생성하는 배치 그룹 유형에 대한 규칙 및 제한 사항이 의도한 사용 사례와 호환되는지 확인합니다.

#### 11.4.1.2.2. Amazon EC2 인스턴스 메타데이터 서비스 구성 옵션

AWS(Amazon Web Services) 클러스터에서 사용하는 Amazon EC2 인스턴스 메타데이터 서비스(IMDS) 버전을 제한할 수 있습니다. 머신은 IMDSv2(AWS 문서)를 사용하거나 IMDSv2 외에 IMDSv1 사용을 허용할 수 있습니다.

구성에 따라 컴퓨팅 머신을 배포하려면 머신 템플릿 YAML 파일에서 적절한 값을 구성합니다. 그런 다음, 머신을 배포할 때 머신 템플릿을 참조하도록 머신 세트 YAML 파일을 구성합니다.

중요

IMDSv2가 필요한 머신을 생성하기 전에 IMDS와 상호 작용하는 모든 워크로드가 IMDSv2를 지원하는지 확인합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSMachineTemplate
# ...
spec:
  template:
    spec:
      instanceMetadataOptions:
        httpEndpoint: enabled
        httpPutResponseHopLimit: 1
        httpTokens: optional
        instanceMetadataTags: disabled
# ...
```

1. IMDSv2 호출에 허용되는 네트워크 홉 수를 지정합니다. 값을 지정하지 않으면 이 매개변수는 기본적으로 `1` 로 설정됩니다.

2. IMDSv2를 사용해야 하는지 여부를 지정합니다. 값을 지정하지 않으면 이 매개변수는 기본적으로 `선택 사항으로` 설정됩니다. 다음 값이 유효합니다.

`optional`

IMDSv1과 IMDSv2를 모두 사용하도록 허용합니다.

`필수 항목`

IMDSv2가 필요합니다.

참고

머신 API는 `httpEndpoint`, `httpPutResponseHopLimit` 및 `instanceMetadataTags` 필드를 지원하지 않습니다. 이 기능을 사용하는 클러스터 API 머신 템플릿을 Machine API 컴퓨팅 머신 세트로 마이그레이션하는 경우 생성되는 모든 머신 API 머신에는 이러한 필드가 없으며 기본 인스턴스에서 이러한 설정을 사용하지 않습니다. 마이그레이션된 머신 세트가 관리하는 기존 머신은 이러한 필드를 유지하며 기본 인스턴스는 이러한 설정을 계속 사용합니다.

IMDSv2를 사용해야 하는 경우 시간 초과가 발생할 수 있습니다. 완화 전략을 비롯한 자세한 내용은 AWS 설명서(인스턴스 메타데이터 액세스 고려 사항)를 참조하십시오.

#### 11.4.1.2.3. 전용 인스턴스 구성 옵션

AWS(Amazon Web Services) 클러스터에서 Dedicated Instances가 지원하는 머신을 배포할 수 있습니다.

Dedicated 인스턴스는 단일 고객 전용 하드웨어의 VPC(가상 프라이빗 클라우드)에서 실행됩니다. 이러한 Amazon EC2 인스턴스는 호스트 하드웨어 수준에서 물리적으로 분리됩니다. Dedicated 인스턴스의 분리는 인스턴스가 하나의 유료 계정에 연결된 다른 AWS 계정에 속하는 경우에도 발생합니다. 하지만 전용이 아닌 다른 인스턴스는 동일한 AWS 계정에 속하는 경우 Dedicated 인스턴스와 하드웨어를 공유할 수 있습니다.

OpenShift Container Platform은 공용 또는 전용 테넌시가 있는 인스턴스를 지원합니다.

구성에 따라 컴퓨팅 머신을 배포하려면 머신 템플릿 YAML 파일에서 적절한 값을 구성합니다. 그런 다음, 머신을 배포할 때 머신 템플릿을 참조하도록 머신 세트 YAML 파일을 구성합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSMachineTemplate
# ...
spec:
  template:
    spec:
      tenancy: dedicated
# ...
```

1. 단일 테넌트 하드웨어에서 실행되는 전용 테넌시가 있는 인스턴스를 사용하도록 지정합니다. 이 값을 지정하지 않으면 공유 하드웨어에서 실행되는 공용 테넌시가 있는 인스턴스가 기본적으로 사용됩니다.

#### 11.4.1.2.4. 보장되지 않는 Spot 인스턴스 및 시간별 비용 제한

AWS(Amazon Web Services)에서 보장되지 않는 Spot 인스턴스로 머신을 배포할 수 있습니다. 스팟 인스턴스는 AWS EC2 용량을 사용하며 온 디맨드 인스턴스보다 비용이 저렴합니다. 일괄 처리 또는 상태 비저장, 수평적으로 확장 가능한 워크로드와 같이 인터럽트를 허용할 수 있는 워크로드에 Spot 인스턴스를 사용할 수 있습니다.

구성에 따라 컴퓨팅 머신을 배포하려면 머신 템플릿 YAML 파일에서 적절한 값을 구성합니다. 그런 다음, 머신을 배포할 때 머신 템플릿을 참조하도록 머신 세트 YAML 파일을 구성합니다.

중요

AWS EC2는 언제든지 Spot 인스턴스의 용량을 회수할 수 있습니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSMachineTemplate
# ...
spec:
  template:
    spec:
      spotMarketOptions:
        maxPrice: <price_per_hour>
# ...
```

1. Spot 인스턴스의 사용을 지정합니다.

2. 선택 사항: Spot 인스턴스의 미국 달러로 시간별 비용 제한을 지정합니다. 예를 들어 < `price_per_hour` > 값을 `2.50` 으로 설정하면 Spot 인스턴스의 비용이 시간당 amount 2.50으로 제한됩니다. 이 값을 설정하지 않으면 최대 가격은 온 디맨드 인스턴스 가격까지 청구됩니다.

주의

특정 > 값을 설정하면 기본 온 디맨드 인스턴스 가격 사용과 비교하여 중단 빈도가 증가할 수 있습니다. 기본 온 디맨드 인스턴스 가격을 사용하고 Spot 인스턴스의 최대 가격을 설정하지 않는 것이 좋습니다.

```shell
maxPrice: < price_per_hour
```

다음과 같은 이유로 Spot 인스턴스를 사용할 때 중단될 수 있습니다.

인스턴스 가격이 최대 가격을 초과합니다.

Spot 인스턴스에 대한 수요가 증가합니다.

Spot 인스턴스의 공급이 감소합니다.

AWS는 중단이 발생하면 사용자에게 2 분 동안 경고 메세지를 보냅니다. OpenShift Container Platform은 AWS가 종료에 대한 경고를 발행할 때 영향을 받는 인스턴스에서 워크로드를 제거하기 시작합니다.

AWS가 인스턴스를 종료하면 Spot 인스턴스 노드에서 실행중인 종료 프로세스가 머신 리소스를 삭제합니다. 컴퓨팅 머신 세트 `replicas` 수량을 충족하기 위해 컴퓨팅 머신 세트는 Spot 인스턴스를 요청하는 머신을 생성합니다.

#### 11.4.1.2.5. 용량 예약 구성 옵션

OpenShift Container Platform 버전 4.20 이상에서는 온디맨드 용량 예약 및 ML의 용량 블록을 포함하여 Amazon Web Services 클러스터에서 용량 예약을 지원합니다.

사용자가 정의한 용량 요청의 매개변수와 일치하는 사용 가능한 리소스에 머신을 배포할 수 있습니다. 이러한 매개변수는 예약할 인스턴스 유형, 리전 및 인스턴스 수를 지정합니다. 용량 예약이 용량 요청을 수용할 수 있는 경우 배포에 성공합니다.

구성에 따라 컴퓨팅 머신을 배포하려면 머신 템플릿 YAML 파일에서 적절한 값을 구성합니다. 그런 다음, 머신을 배포할 때 머신 템플릿을 참조하도록 머신 세트 YAML 파일을 구성합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSMachineTemplate
# ...
spec:
  template:
    spec:
      capacityReservationId: <capacity_reservation>
      capacityReservationPreference: <reservation_preference>
      marketType: <market_type>
# ...
```

1. 머신을 배포하려는 ML 또는 온 디맨드 용량 예약의 용량 블록 ID를 지정합니다.

2. 기본 용량 예약 동작을 지정합니다. 다음 값이 유효합니다.

`CapacityReservationsOnly`

일치하는 용량 예약이 필요한 경우 이 옵션을 사용합니다. 일치하는 용량 예약이 없는 경우 인스턴스가 시작되지 않습니다.

`open`

가용성 영역 및 인스턴스 유형과 일치하는 오픈 용량 예약을 사용하려면 이 옵션을 사용합니다.

`없음`

용량 예약을 금지하려면 이 옵션을 사용합니다. 이 옵션을 사용하면 사용하려는 워크로드에 대해 용량 예약을 사용할 수 있습니다.

3. 사용할 시장 유형을 지정합니다. 다음 값이 유효합니다.

`CapacityBlock`

ML 용 용량 블록과 함께 이 시장 유형을 사용합니다.

`OnDemand`

온디맨드 용량 예약과 함께 이 시장 유형을 사용합니다.

`스팟`

Spot 인스턴스와 함께 이 시장 유형을 사용합니다. 이 옵션은 용량 예약과 호환되지 않습니다.

이 오퍼링에 대한 제한 사항 및 제안된 사용 사례를 포함한 자세한 내용은 AWS 문서의 온디맨드 용량 예약 및 ML 용량 블록을 참조하십시오.

#### 11.4.1.2.6. GPU 지원 머신 옵션

AWS(Amazon Web Services)에 GPU 지원 컴퓨팅 머신을 배포할 수 있습니다. 다음 샘플 구성에서는 AWS G4dn 인스턴스 유형을 사용합니다. 이 인스턴스 유형은 NVIDIA Cryostat T4 Tensor Core GPU를 포함합니다.

지원되는 인스턴스 유형에 대한 자세한 내용은 NVIDIA 설명서의 다음 페이지를 참조하십시오.

NVIDIA GPU Operator 커뮤니티 지원 매트릭스

NVIDIA AI Enterprise 지원 매트릭스

구성을 사용하여 컴퓨팅 머신을 배포하려면 머신 템플릿 YAML 파일에 적절한 값과 머신을 배포할 때 머신 템플릿을 참조하는 머신 세트 YAML 파일을 구성합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
kind: AWSMachineTemplate
# ...
spec:
  template:
    spec:
      instanceType: g4dn.xlarge
# ...
```

1. G4dn 인스턴스 유형을 지정합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <cluster_name>-gpu-<region>
  namespace: openshift-cluster-api
  labels:
    cluster.x-k8s.io/cluster-name: <cluster_name>
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
      cluster.x-k8s.io/cluster-name: <cluster_name>
      cluster.x-k8s.io/set-name: <cluster_name>-gpu-<region>
  template:
    metadata:
      labels:
        test: example
        cluster.x-k8s.io/cluster-name: <cluster_name>
        cluster.x-k8s.io/set-name: <cluster_name>-gpu-<region>
        node-role.kubernetes.io/<role>: ""
# ...
```

1. `gpu` 역할을 포함하는 이름을 지정합니다. 이름에는 클러스터 ID를 접두사로 포함하고 리전은 접미사로 포함됩니다.

2. 머신 세트 이름과 일치하는 선택기 레이블을 지정합니다.

3. 머신 세트 이름과 일치하는 템플릿 레이블을 지정합니다.

#### 11.4.2. Google Cloud의 클러스터 API 구성 옵션

Cluster API 사용자 정의 리소스 매니페스트에서 값을 업데이트하여 Google Cloud Cluster API 머신의 구성을 변경할 수 있습니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.4.2.1. Google Cloud 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 파일은 Google Cloud 클러스터에 대한 구성을 보여줍니다.

#### 11.4.2.1.1. Google Cloud에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

머신 템플릿 리소스는 공급자마다 다르며 컴퓨팅 머신 세트에서 생성하는 시스템의 기본 속성을 정의합니다. 머신을 생성할 때 컴퓨팅 머신 세트는 이 템플릿을 참조합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: GCPMachineTemplate
metadata:
  name: <template_name>
  namespace: openshift-cluster-api
spec:
  template:
    spec:
      rootDeviceType: pd-ssd
      rootDeviceSize: 128
      instanceType: n1-standard-4
      image: projects/rhcos-cloud/global/images/rhcos-411-85-202203181601-0-gcp-x86-64
      subnet: <cluster_name>-worker-subnet
      serviceAccounts:
        email: <service_account_email_address>
        scopes:
          - https://www.googleapis.com/auth/cloud-platform
      additionalLabels:
        kubernetes-io-cluster-<cluster_name>: owned
      additionalNetworkTags:
        - <cluster_name>-worker
      ipForwarding: Disabled
```

1. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

2. 머신 템플릿의 이름을 지정합니다.

3. 환경에 대한 세부 정보를 지정합니다. 여기에 있는 값은 예입니다.

#### 11.4.2.1.2. Google Cloud에서 클러스터 API 컴퓨팅 머신 세트 리소스의 샘플 YAML

컴퓨팅 머신 세트 리소스는 생성하는 시스템의 추가 속성을 정의합니다. 컴퓨팅 머신 세트는 머신을 생성할 때 클러스터 리소스 및 머신 템플릿도 참조합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
  labels:
    cluster.x-k8s.io/cluster-name: <cluster_name>
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
      cluster.x-k8s.io/cluster-name: <cluster_name>
      cluster.x-k8s.io/set-name: <machine_set_name>
  template:
    metadata:
      labels:
        test: example
        cluster.x-k8s.io/cluster-name: <cluster_name>
        cluster.x-k8s.io/set-name: <machine_set_name>
        node-role.kubernetes.io/<role>: ""
    spec:
      bootstrap:
         dataSecretName: worker-user-data
      clusterName: <cluster_name>
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: GCPMachineTemplate
        name: <template_name>
      failureDomain: <failure_domain>
```

1. 컴퓨팅 머신 세트의 이름을 지정합니다. 클러스터 ID, 머신 역할 및 리전은 < `cluster_name>-<role>-<region` > 형식으로 이 값에 대한 일반적인 패턴을 형성합니다.

2. 3

클러스터 ID를 클러스터 이름으로 지정합니다.

4. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

5. 머신 템플릿 이름을 지정합니다.

6. Google Cloud 리전 내에서 실패 도메인을 지정합니다.

#### 11.4.3. Microsoft Azure의 클러스터 API 구성 옵션

Cluster API 사용자 정의 리소스 매니페스트에서 값을 업데이트하여 Microsoft Azure Cluster API 머신의 구성을 변경할 수 있습니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.4.3.1. Microsoft Azure 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 파일은 Azure 클러스터에 대한 구성을 보여줍니다.

#### 11.4.3.1.1. Microsoft Azure의 클러스터 API 머신 템플릿 리소스의 샘플 YAML

머신 템플릿 리소스는 공급자마다 다르며 컴퓨팅 머신 세트에서 생성하는 시스템의 기본 속성을 정의합니다. 머신을 생성할 때 컴퓨팅 머신 세트는 이 템플릿을 참조합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: AzureMachineTemplate
metadata:
  name: <template_name>
  namespace: openshift-cluster-api
spec:
  template:
    spec:
      disableExtensionOperations: true
      identity: UserAssigned
      image:
        id: /subscriptions/<subscription_id>/resourceGroups/<cluster_name>-rg/providers/Microsoft.Compute/galleries/gallery_<compliant_cluster_name>/images/<cluster_name>-gen2/versions/latest
      networkInterfaces:
        - acceleratedNetworking: true
          privateIPConfigs: 1
          subnetName: <cluster_name>-worker-subnet
      osDisk:
        diskSizeGB: 128
        managedDisk:
          storageAccountType: Premium_LRS
        osType: Linux
      sshPublicKey: <ssh_key_value>
      userAssignedIdentities:
        - providerID: 'azure:///subscriptions/<subscription_id>/resourcegroups/<cluster_name>-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<cluster_name>-identity'
      vmSize: Standard_D4s_v3
```

1. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

2. 머신 템플릿의 이름을 지정합니다.

3. 환경에 대한 세부 정보를 지정합니다. 여기에 있는 값은 예입니다.

4. 인스턴스 유형과 호환되는 이미지를 지정합니다. 설치 프로그램에서 생성한 Hyper-V generation V2 이미지에는 `-gen2` 접미사가 있지만 V1 이미지의 접미사 없이 이름이 동일합니다.

참고

기본 OpenShift Container Platform 클러스터 이름에 하이픈(`-`)이 포함되어 있으며, 이는 Azure everyone 이름 요구 사항과 호환되지 않습니다. 이 구성의 < `compliant_cluster_name` > 값은 하이픈 대신 밑줄(`_`)을 사용하여 이러한 요구 사항을 준수해야 합니다. < `cluster_name` >의 다른 인스턴스는 변경되지 않습니다.

예를 들어, `jdoe-test-2m2np` 클러스터 이름은 `jdoe_test_2m2np` 로 변환됩니다. 이 예제의 Cryostat `_<compliant_cluster_name` >에 대한 전체 문자열은LOCAL `_jdoe_test_2m2np` 이며, ring `_jdoe-test-2m2np`. 이 예제의 `spec.template.spec.image.id` 의 전체 값은 입니다.

```shell
/subscriptions/<subscription_id>/resourceGroups/jdoe-test-2m2np-rg/providers/Microsoft.Compute/galleries/gallery_jdoe_test_2m2np/images/jdoe-test-2m2np2/versions latest
```

#### 11.4.3.1.2. Microsoft Azure의 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

컴퓨팅 머신 세트 리소스는 생성하는 시스템의 추가 속성을 정의합니다. 컴퓨팅 머신 세트는 머신을 생성할 때 클러스터 리소스 및 머신 템플릿도 참조합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
  labels:
    cluster.x-k8s.io/cluster-name: <cluster_name>
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
      cluster.x-k8s.io/cluster-name: <cluster_name>
      cluster.x-k8s.io/set-name: <machine_set_name>
  template:
    metadata:
      labels:
        test: example
        cluster.x-k8s.io/cluster-name: <cluster_name>
        cluster.x-k8s.io/set-name: <machine_set_name>
        node-role.kubernetes.io/<role>: ""
    spec:
      bootstrap:
         dataSecretName: worker-user-data
      clusterName: <cluster_name>
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: AzureMachineTemplate
        name: <template_name>
```

1. 컴퓨팅 머신 세트의 이름을 지정합니다. 클러스터 ID, 머신 역할 및 리전은 < `cluster_name>-<role>-<region` > 형식으로 이 값에 대한 일반적인 패턴을 형성합니다.

2. 클러스터 ID를 클러스터 이름으로 지정합니다.

3. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

4. 머신 템플릿 이름을 지정합니다.

#### 11.4.4. Red Hat OpenStack Platform의 클러스터 API 구성 옵션

Cluster API 사용자 정의 리소스 매니페스트에서 값을 업데이트하여 RHOSP(Red Hat OpenStack Platform) 클러스터 API 머신의 구성을 변경할 수 있습니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.4.4.1. RHOSP 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 파일은 RHOSP 클러스터에 대한 구성을 보여줍니다.

#### 11.4.4.1.1. RHOSP에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

머신 템플릿 리소스는 공급자마다 다르며 컴퓨팅 머신 세트에서 생성하는 시스템의 기본 속성을 정의합니다. 머신을 생성할 때 컴퓨팅 머신 세트는 이 템플릿을 참조합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: OpenStackMachineTemplate
metadata:
  name: <template_name>
  namespace: openshift-cluster-api
spec:
  template:
    spec:
      flavor: <openstack_node_machine_flavor>
      image:
        filter:
          name: <openstack_image>
```

1. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

2. 머신 템플릿의 이름을 지정합니다.

3. 환경에 대한 세부 정보를 지정합니다. 여기에 있는 값은 예입니다.

4. 사용할 RHOSP 플레이버를 지정합니다. 자세한 내용은 인스턴스 시작을 위한 플레이버 생성 을 참조하십시오.

5. 사용할 이미지를 지정합니다.

#### 11.4.4.1.2. RHOSP에서 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

컴퓨팅 머신 세트 리소스는 생성하는 시스템의 추가 속성을 정의합니다. 컴퓨팅 머신 세트는 머신을 생성할 때 인프라 리소스 및 머신 템플릿도 참조합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
      cluster.x-k8s.io/cluster-name: <cluster_name>
      cluster.x-k8s.io/set-name: <machine_set_name>
  template:
    metadata:
      labels:
        test: example
        cluster.x-k8s.io/cluster-name: <cluster_name>
        cluster.x-k8s.io/set-name: <machine_set_name>
        node-role.kubernetes.io/<role>: ""
    spec:
      bootstrap:
         dataSecretName: worker-user-data
      clusterName: <cluster_name>
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: OpenStackMachineTemplate
        name: <template_name>
      failureDomain: <nova_availability_zone>
```

1. 컴퓨팅 머신 세트의 이름을 지정합니다.

2. 클러스터 ID를 클러스터 이름으로 지정합니다.

3. Cluster API 기술 프리뷰의 경우 Operator는 `openshift-machine-api` 네임스페이스의 작업자 사용자 데이터 시크릿을 사용할 수 있습니다.

4. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

5. 머신 템플릿 이름을 지정합니다.

6. 선택 사항: 시스템을 생성할 시스템 세트의 Nova 가용성 영역의 이름을 지정합니다. 값을 지정하지 않으면 시스템은 특정 가용성 영역으로 제한되지 않습니다.

#### 11.4.5. VMware vSphere의 클러스터 API 구성 옵션

Cluster API 사용자 정의 리소스 매니페스트에서 값을 업데이트하여 VMware vSphere Cluster API 머신의 구성을 변경할 수 있습니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.4.5.1. VMware vSphere 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 파일은 VMware vSphere 클러스터에 대한 구성을 보여줍니다.

#### 11.4.5.1.1. VMware vSphere에서 클러스터 API 머신 템플릿 리소스의 샘플 YAML

머신 템플릿 리소스는 공급자마다 다르며 컴퓨팅 머신 세트에서 생성하는 시스템의 기본 속성을 정의합니다. 머신을 생성할 때 컴퓨팅 머신 세트는 이 템플릿을 참조합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: VSphereMachineTemplate
metadata:
  name: <template_name>
  namespace: openshift-cluster-api
spec:
  template:
    spec:
      template: <vm_template_name>
      server: <vcenter_server_ip>
      diskGiB: 128
      cloneMode: linkedClone
      datacenter: <vcenter_data_center_name>
      datastore: <vcenter_datastore_name>
      folder: <vcenter_vm_folder_path>
      resourcePool: <vsphere_resource_pool>
      numCPUs: 4
      memoryMiB: 16384
      network:
        devices:
        - dhcp4: true
          networkName: "<vm_network_name>"
```

1. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

2. 머신 템플릿의 이름을 지정합니다.

3. 환경에 대한 세부 정보를 지정합니다. 여기에 있는 값은 예입니다.

4. 사용할 vSphere VM 템플릿 (예: `user-5ddjd-rhcos)` 을 지정합니다.

5. vCenter 서버 IP 또는 정규화된 도메인 이름을 지정합니다.

6. 사용할 VM 복제 유형을 지정합니다. 다음 값이 유효합니다.

`fullClone`

`linkedClone`

`linkedClone` 유형을 사용하는 경우 디스크 크기는 `diskGiB` 값을 사용하는 대신 복제 소스와 일치합니다. 자세한 내용은 VM 복제 유형에 대한 vSphere 설명서를 참조하십시오.

7. 컴퓨팅 머신 세트를 배포할 vCenter 데이터 센터를 지정합니다.

8. 컴퓨팅 머신 세트를 배포할 vCenter 데이터 저장소를 지정합니다.

9. vCenter의 vSphere VM 폴더에 경로(예: `/dc1/vm/user-inst-5ddjd`)를 지정합니다.

10. VM의 vSphere 리소스 풀을 지정합니다.

11. 컴퓨팅 머신 세트를 배포할 vSphere VM 네트워크를 지정합니다. 이 VM 네트워크는 다른 컴퓨팅 시스템이 클러스터에 상주하는 위치여야 합니다.

#### 11.4.5.1.2. VMware vSphere에서 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

컴퓨팅 머신 세트 리소스는 생성하는 시스템의 추가 속성을 정의합니다. 컴퓨팅 머신 세트는 머신을 생성할 때 클러스터 리소스 및 머신 템플릿도 참조합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
  labels:
    cluster.x-k8s.io/cluster-name: <cluster_name>
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
      cluster.x-k8s.io/cluster-name: <cluster_name>
      cluster.x-k8s.io/set-name: <machine_set_name>
  template:
    metadata:
      labels:
        test: example
        cluster.x-k8s.io/cluster-name: <cluster_name>
        cluster.x-k8s.io/set-name: <machine_set_name>
        node-role.kubernetes.io/<role>: ""
    spec:
      bootstrap:
         dataSecretName: worker-user-data
      clusterName: <cluster_name>
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: VSphereMachineTemplate
        name: <template_name>
      failureDomain:
        - name: <failure_domain_name>
          region: <region_a>
          zone: <zone_a>
          server: <vcenter_server_name>
          topology:
            datacenter: <region_a_data_center>
            computeCluster: "</region_a_data_center/host/zone_a_cluster>"
            resourcePool: "</region_a_data_center/host/zone_a_cluster/Resources/resource_pool>"
            datastore: "</region_a_data_center/datastore/datastore_a>"
            networks:
            - port-group
```

1. 컴퓨팅 머신 세트의 이름을 지정합니다. 클러스터 ID, 머신 역할 및 리전은 < `cluster_name>-<role>-<region` > 형식으로 이 값에 대한 일반적인 패턴을 형성합니다.

2. 3

클러스터 ID를 클러스터 이름으로 지정합니다.

4. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

5. 머신 템플릿 이름을 지정합니다.

6. 실패 도메인 구성 세부 정보를 지정합니다.

참고

클러스터 API를 사용하는 vSphere 클러스터에서 여러 리전 및 영역을 사용하는 것은 검증된 구성이 아닙니다.

#### 11.4.6. 베어 메탈의 클러스터 API 구성 옵션

Cluster API 사용자 정의 리소스 매니페스트에서 값을 업데이트하여 베어 메탈 클러스터 API 머신의 구성을 변경할 수 있습니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.4.6.1. 베어 메탈 클러스터 구성을 위한 샘플 YAML

다음 예제 YAML 파일은 베어 메탈 클러스터에 대한 구성을 보여줍니다.

#### 11.4.6.1.1. 베어 메탈의 Cluster API 머신 템플릿 리소스의 샘플 YAML

머신 템플릿 리소스는 공급자마다 다르며 컴퓨팅 머신 세트에서 생성하는 시스템의 기본 속성을 정의합니다. 머신을 생성할 때 컴퓨팅 머신 세트는 이 템플릿을 참조합니다.

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: Metal3MachineTemplate
metadata:
  name: <template_name>
  namespace: openshift-cluster-api
spec:
  template:
    spec:
      customDeploy: install_coreos
      userData:
        name: worker-user-data-managed
```

1. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

2. 머신 템플릿의 이름을 지정합니다.

3. 환경에 대한 세부 정보를 지정합니다. 여기에 있는 값은 예입니다.

4. `userData` 매개변수는 설치 중에 Machine API Operator가 생성하는 Ignition 구성을 나타냅니다. 다음 명령을 실행하여 클러스터가 보안에 액세스할 수 있도록 `openshift-cluster-api` 네임스페이스를 적용해야 합니다.

```shell-session
$ oc get secret worker-user-data-managed \
  -n openshift-machine-api -o yaml | \
  sed 's/namespace: .*/namespace: openshift-cluster-api/' | oc apply -f -
```

#### 11.4.6.1.2. 베어 메탈의 Cluster API 컴퓨팅 머신 세트 리소스의 샘플 YAML

컴퓨팅 머신 세트 리소스는 생성하는 시스템의 추가 속성을 정의합니다. 컴퓨팅 머신 세트는 머신을 생성할 때 클러스터 리소스 및 머신 템플릿도 참조합니다.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineSet
metadata:
  name: <machine_set_name>
  namespace: openshift-cluster-api
  labels:
    cluster.x-k8s.io/cluster-name: <cluster_name>
spec:
  clusterName: <cluster_name>
  replicas: 1
  selector:
    matchLabels:
      test: example
      cluster.x-k8s.io/cluster-name: <cluster_name>
      cluster.x-k8s.io/set-name: <machine_set_name>
  template:
    metadata:
      labels:
        test: example
        cluster.x-k8s.io/cluster-name: <cluster_name>
        cluster.x-k8s.io/set-name: <machine_set_name>
        node-role.kubernetes.io/worker: ""
    spec:
      bootstrap:
         dataSecretName: worker-user-data-managed
      clusterName: <cluster_name>
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: Metal3MachineTemplate
        name: <template_name>
```

1. 컴퓨팅 머신 세트의 이름을 지정합니다. 클러스터 ID, 머신 역할 및 리전은 < `cluster_name>-<role>-<region` > 형식으로 이 값에 대한 일반적인 패턴을 형성합니다.

2. 클러스터 ID를 클러스터 이름으로 지정합니다.

3. 머신 템플릿 유형을 지정합니다. 이 값은 플랫폼의 값과 일치해야 합니다.

4. 머신 템플릿 이름을 지정합니다.

### 11.5. 클러스터 API를 사용하는 클러스터 문제 해결

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

이 섹션의 정보를 사용하여 발생할 수 있는 문제를 이해하고 복구하십시오. 일반적으로 클러스터 API 문제 해결 단계는 Machine API 문제 해결 단계와 유사합니다.

Cluster CAPI Operator 및 해당 피연산자는 `openshift-cluster-api` 네임스페이스에 프로비저닝되지만 Machine API는 `openshift-machine-api` 네임스페이스를 사용합니다. 네임스페이스를 참조하는 아래 명령을 사용하는 경우 올바른 명령을 참조해야 합니다.

```shell
oc
```

#### 11.5.1. CLI를 사용할 때 의도된 오브젝트 참조

Cluster API를 사용하는 클러스터의 경우 OpenShift CLI() 명령은 Machine API 오브젝트를 통해 Cluster API 오브젝트를 우선시합니다.

```shell
oc
```

이 동작은 Cluster API 및 Machine API 둘 다에 표시되는 모든 오브젝트에 대해 작동하는 아래 명령에 영향을 미칩니다. 이 설명에서는 아래 명령을 사용하여 시스템을 삭제합니다. 예를 들면 다음과 같습니다.

```shell
oc
```

```shell
oc delete machine
```

원인

아래 명령을 실행할 때 는 Kube API 서버와 통신하여 작업할 오브젝트를 결정합니다. Kube API 서버는 아래 명령이 실행될 때 알파벳순으로 표시되는 첫 번째 설치된 CRD(사용자 정의 리소스 정의)를 사용합니다.

```shell
oc
```

```shell
oc
```

```shell
oc
```

Cluster API 오브젝트의 CRD는 `cluster.x-k8s.io` 그룹에 있으며 Machine API 오브젝트의 CRD는 `machine.openshift.io` 그룹에 있습니다. 문자 `c` 는 알파벳순으로 `m` 문자 앞에 있기 때문에 Kube API 서버는 Cluster API 오브젝트 CRD에서 일치합니다. 결과적으로 아래 명령은 Cluster API 오브젝트에서 작동합니다.

```shell
oc
```

결과

이 동작으로 인해 Cluster API를 사용하는 클러스터에서 다음과 같은 의도하지 않은 결과가 발생할 수 있습니다.

두 유형의 오브젝트가 모두 포함된 네임스페이스의 경우 다음 명령과 같은 명령은 Cluster API 오브젝트만 반환합니다.

```shell
oc get machine
```

Machine API 오브젝트만 포함하는 네임스페이스의 경우 다음 명령과 같은 명령은 결과를 반환하지 않습니다.

```shell
oc get machine
```

해결방법

아래 명령이 정규화된 해당 이름을 사용하여 원하는 오브젝트 유형에서 작동하는지 확인할 수 있습니다.

```shell
oc
```

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

Machine API 머신을 삭제하려면 아래 명령을 실행할 때 정규화된 이름 `machine.machine.openshift.io` 를 사용합니다.

```shell
oc delete machine
```

```shell-session
$ oc delete machine.machine.openshift.io <machine_name>
```

클러스터 API 머신을 삭제하려면 아래 명령을 실행할 때 정규화된 이름 `machine.cluster.x-k8s.io` 를 사용합니다.

```shell
oc delete machine
```

```shell-session
$ oc delete machine.cluster.x-k8s.io <machine_name>
```

#### 11.5.2. 중복 머신 세트 및 머신 리소스

Machine API 리소스를 Cluster API 리소스로 마이그레이션하는 것을 지원하는 클러스터에서 일부 리소스에는 리소스 및 OpenShift Container Platform 웹 콘솔을 나열하는 OpenShift CLI() 명령의 출력에 중복 인스턴스가 있는 것처럼 보입니다.

```shell
oc
```

원인

기본 구성 옵션을 사용하는 OpenShift Container Platform 클러스터를 설치할 때 설치 프로그램은 `openshift-machine-api` 네임스페이스에 다음 인프라 리소스를 프로비저닝합니다.

3개의 컨트롤 플레인 머신을 관리하는 하나의 컨트롤 플레인 머신 세트입니다.

3개의 컴퓨팅 머신을 관리하는 하나 이상의 컴퓨팅 머신 세트입니다.

스팟 인스턴스를 관리하는 하나의 머신 상태 점검입니다.

컴퓨팅 머신 세트 사양에 따라 생성된 컴퓨팅 머신입니다.

Machine API 리소스를 클러스터 API 리소스로 마이그레이션하는 클러스터에서는 양방향 동기화 컨트롤러에서 `openshift-cluster-api` 네임스페이스에 다음 Cluster API 리소스를 생성합니다.

클러스터 리소스 1개

공급자별 인프라 클러스터 리소스 1개

컴퓨팅 머신 세트에 해당하는 하나 이상의 머신 템플릿입니다.

3개의 컴퓨팅 머신을 관리하는 하나 이상의 컴퓨팅 머신 세트입니다.

머신 템플릿 및 컴퓨팅 머신 세트 사양에 따라 생성된 컴퓨팅 머신입니다.

컴퓨팅 시스템에 해당하는 인프라 시스템입니다.

이러한 클러스터 API 리소스의 이름은 `openshift-machine-api` 네임스페이스에 있는 해당 이름과 동일합니다.

결과

이 동작으로 인해 리소스 및 OpenShift Container Platform 웹 콘솔을 나열하는 아래 명령의 출력에 중복된 것처럼 보이는 머신 세트 및 머신 리소스의 인스턴스가 표시됩니다.

```shell
oc
```

해결방법

리소스의 이름이 다른 네임스페이스에 있는 해당 이름과 동일하지만 현재 권한 있는 API를 사용하는 리소스만 활성화됩니다. 동기화 컨트롤러는 의도하지 않은 조정을 방지하기 위해 프로비저닝되지 않은(사용되지 않은) 상태에서 현재 권한 있는 API를 사용하지 않는 해당 리소스를 생성하고 유지 관리합니다.

결과

중복된 것처럼 보이는 각 리소스 중 하나만 한 번에 활성화됩니다. 비활성 비인증 리소스는 기능에 영향을 미치지 않습니다.

중요

현재 권한 있는 API를 사용하는 해당 리소스를 삭제하려면 현재 권한 있는 API를 사용하지 않는 권한 없는 리소스는 삭제하지 마십시오.

현재 권한 있는 API를 사용하지 않는 권한 없는 리소스를 삭제하면 동기화 컨트롤러에서 현재 권한 있는 API를 사용하는 해당 리소스를 삭제합니다. 자세한 내용은 "Unexpected resource deletion behavior"를 참조하십시오.

#### 11.5.3. 예기치 않은 리소스 삭제 동작

Machine API와 Cluster API 간에 리소스 마이그레이션을 지원하는 클러스터에서는 사용자가 Machine API 권한이 있는 클러스터에서 클러스터 API 리소스를 삭제할 때 예기치 않은 동작이 발생할 수 있습니다.

원인

권한 있는 API를 사용하는 모든 리소스에 대해 양방향 동기화 컨트롤러는 현재 권한 있는 API를 사용하지 않는 해당 리소스를 생성하고 유지 관리합니다.

현재 권한 있는 API를 사용하지 않는 리소스에 대한 삭제 동작은 권한이 있는 API에 따라 달라집니다.

Machine API가 권한이 있는 클러스터에서 클러스터 API 리소스를 삭제하면 동기화 컨트롤러에서 해당 Machine API 리소스를 삭제합니다.

클러스터 API가 권한이 있는 클러스터에서 Machine API 리소스를 삭제하면 동기화 컨트롤러에서 해당 Cluster API 리소스를 삭제하지 않습니다. 이러한 동작의 차이점은 Machine API 사용에서 클러스터 API 사용으로의 마이그레이션을 지원합니다.

이 동작은 리소스를 직접 삭제하고 축소 작업을 수행할 때 발생합니다.

결과

권한 있는 API에 따라 다음과 같은 결과가 발생합니다.

클러스터 API가 권한이 있는 클러스터의 경우 해당 Cluster API 리소스에 영향을 주지 않고 Machine API 리소스를 제거할 수 있습니다.

Machine API가 권한이 있는 클러스터의 경우 해당 Machine API 리소스도 삭제하지 않고 클러스터 API 리소스를 제거할 수 없습니다.

해결방법

Machine API가 권한이 있는 클러스터의 경우 해당 Machine API 리소스를 삭제하려는 경우를 제외하고 Cluster API 리소스를 삭제하지 마십시오.

#### 11.5.4. 리소스 마이그레이션 문제 해결

다른 권한 있는 API를 사용하도록 리소스를 마이그레이션하면 마이그레이션 프로세스 중에 문제가 발생할 수 있습니다. Cluster API와 Machine API 간의 차이로 인해 예기치 않은 동작이 표시될 수도 있습니다.

#### 11.5.4.1. 신뢰할 수 있는 API 유형의 컴퓨팅 시스템

컴퓨팅 시스템의 권한 있는 API는 이를 생성하는 Machine API 컴퓨팅 머신 세트의 `.spec.authoritativeAPI` 및 `.spec.template.spec.authoritativeAPI` 필드의 값에 따라 다릅니다.

| `.spec.authoritativeAPI` value | `ClusterAPI` | `ClusterAPI` | `MachineAPI` | `MachineAPI` |
| --- | --- | --- | --- | --- |
| `.spec.template.spec.authoritativeAPI` value | `ClusterAPI` | `MachineAPI` | `MachineAPI` | `ClusterAPI` |
| 새 컴퓨팅 시스템에 대한 `authoritativeAPI` 값 | `ClusterAPI` | `ClusterAPI` | `MachineAPI` | `ClusterAPI` |

참고

`.spec.authoritativeAPI` 값이 `ClusterAPI` 인 경우 Machine API 머신 세트가 권한이 없으며 `.spec.template.spec.authoritativeAPI` 값이 사용되지 않습니다. 결과적으로 `Machine API` 를 사용하여 권한 있는 대로 컴퓨팅 머신을 생성하는 유일한 조합은 `.spec.authoritativeAPI` 및 `.spec.template.spec.authoritativeAPI` 값이 MachineAPI인 입니다.

#### 11.5.4.2. 스케일링 후 예기치 않은 머신 수

Machine API와 Cluster API 간에 리소스 마이그레이션을 지원하는 클러스터에서는 컴퓨팅 머신 수를 스케일링할 때 예기치 않은 동작이 발생할 수 있습니다. 권한 있는 API를 사용하지 않는 컴퓨팅 머신 세트의 아래 명령의 출력에 `CURRENT`, `READY` 및 `AVAILABLE` 열의 부정확한 값이 포함될 수 있습니다.

```shell
oc get
```

원인

`CURRENT`, `READY`, `AVAILABLE` 열을 채우는 값은 컴퓨팅 시스템 세트의 `.status` 스탠자에서 시작됩니다. 권한 있는 API 유형 간의 리소스 변환을 처리하는 양방향 동기화 컨트롤러는 현재 `.status` 스탠자의 값을 동기화하지 않습니다.

`DESIRED` 열의 값은 컴퓨팅 머신 세트의 `.spec.replicas` 값을 반영합니다. 양방향 동기화 컨트롤러는 `.spec` 스탠자의 값을 동기화합니다.

결과

마이그레이션된 머신 세트를 스케일링할 때 사용자는 다음 동작을 확인할 수 있습니다.

기존 시스템으로 컴퓨팅 머신 세트로 시작합니다.

다른 권한 있는 API를 사용하도록 머신 세트를 마이그레이션합니다.

`.spec.replicas` 필드에 더 큰 값을 설정하여 권한 있는 시스템을 확장합니다.

머신 세트는 요청된 복제본 수를 충족하기 위해 현재 권한 있는 API가 있는 머신을 생성합니다.

다음 조건 중 하나가 현재 권한 있는 API를 사용하지 않는 머신을 삭제하도록 권한 있는 머신 세트를 축소합니다.

요청된 총 복제본 수는 현재 권한 있는 API를 사용하지 않는 머신 수보다 적습니다.

머신 세트의 머신 삭제 정책은 현재 권한 있는 API를 사용하지 않는 머신을 선택합니다.

아래 명령을 실행하여 권한 없는 컴퓨팅 머신 세트의 상태를 확인합니다.

```shell
oc get
```

출력의 `DESIRED` 열의 값은 `.spec.replicas` 값을 반영합니다.

`CURRENT`, `READY`, `AVAILABLE` 열의 값은 머신 세트를 스케일링하기 전에 존재했던 원래 복제본 수를 반영합니다.

해결방법

현재 권한 있는 API를 사용하지 않는 컴퓨팅 시스템을 축소 작업을 성공적으로 삭제하려면 권한 없는 컴퓨팅 시스템을 나열하는 아래 명령을 실행합니다.

```shell
oc get
```

결과

스케일 다운 작업이 성공하면 권한이 없는 컴퓨팅 시스템에 대한 아래 명령의 출력에 있는 수가 머신 세트의 `.spec.replicas` 값을 반영합니다.

```shell
oc get
```

#### 11.5.4.3. 라벨 및 주석의 동기화 완료

레이블 및 주석 동기화 동작은 Machine API와 Cluster API 간에 다릅니다. 이러한 차이로 인해 마이그레이션 중에 양방향 동기화 컨트롤러에서 클러스터 API 머신의 레이블을 덮어씁니다.

원인

머신 API를 사용하면 머신 세트 레이블 및 주석으로 변경해도 기존 머신 및 노드로 전달되지 않습니다. 이러한 변경 사항은 업데이트 후 배포된 시스템에만 적용됩니다.

Cluster API를 사용하여 머신 세트 레이블 및 주석을 변경하면 기존 머신 및 노드로 전파됩니다. 머신 세트의 권한 있는 API가 Machine API에서 Cluster API로 변경되면 해당 레이블이 관리하는 Cluster API 시스템으로 전파됩니다. 클러스터 API 시스템이 권한 있는 것으로 표시되기 전에 전파가 수행됩니다.

결과

양방향 동기화 컨트롤러는 전파된 라벨 및 주석을 이전 값으로 덮어씁니다. 이로 인해 불일치가 발생하지 않습니다. 이 결과는 레이블 또는 주석을 제거하는 경우에만 발생합니다. 업데이트 및 추가 레이블 또는 주석으로 인해 이러한 불일치가 발생하지 않습니다.

해결방법

이 문제에 대한 해결방법이 없습니다. 자세한 내용은 OCPBUGS-54333 을 참조하십시오.

#### 11.5.4.4. 지원되지 않는 설정 옵션

머신 API는 클러스터 API의 모든 구성 옵션을 지원하지 않습니다. 일부 머신 API 구성은 클러스터 API로 마이그레이션할 수 없습니다. 추가 구성 옵션은 향후 릴리스에서 지원될 수 있습니다.

다음 구성을 사용하려고 하면 마이그레이션이 실패하거나 오류가 발생할 수 있습니다.

참고

이 목록은 완전하지 않을 수 있습니다.

#### 11.5.4.4.1. 일반적인 제한 사항

다음 제한 사항은 모든 클러스터에 적용됩니다.

`NodeDeletionTimeout` 필드에 클러스터 API 기본값이 `10s` 인 경우 Machine API 컴퓨팅 머신은 클러스터 API로 마이그레이션할 수 없습니다.

OpenShift Container Platform은 머신 세트의 `spec.template.spec` 스탠자 또는 머신의 `spec` 스탠자에서 다음 Cluster API 필드 사용을 지원하지 않습니다.

`version`

`readinessGates`

머신 API는 다음 Cluster API 드레이닝 구성 옵션 사용을 지원하지 않습니다.

`nodeDrainTimeout`

`nodeVolumeDetachTimeout`

`nodeDeletionTimeout`

클러스터 API는 시스템에서 노드로의 레이블 또는 테인트를 전파하는 것을 지원하지 않습니다.

#### 11.5.4.4.2. AWS(Amazon Web Services) 제한 사항

다음 제한 사항은 AWS 클러스터에 적용됩니다.

머신 API 컴퓨팅 머신은 AWS 로드 밸런서를 사용할 수 없습니다.

머신 API는 다음 Amazon EC2 인스턴스 메타데이터 서비스(IMDS) 구성 옵션 사용을 지원하지 않습니다.

`httpEndpoint`

`httpPutResponseHopLimit`

`instanceMetadataTags`

IMDS 구성 옵션을 사용하는 Cluster API 머신 템플릿을 Machine API 컴퓨팅 머신 세트로 마이그레이션하는 경우 다음과 같은 동작이 필요합니다.

마이그레이션된 머신 API 머신 세트에는 이러한 필드가 없습니다. 기본 인스턴스는 이러한 설정을 사용하지 않습니다.

마이그레이션된 머신 세트가 관리하는 기존 머신은 이러한 필드를 유지합니다. 기본 인스턴스는 이러한 설정을 계속 사용합니다.

OpenShift Container Platform은 다음 AWS 머신 템플릿 필드 사용을 지원하지 않습니다.

`spec.ami.eksLookupType`

`spec.cloudInit`

`spec.ignition.proxy`

`spec.ignition.tls`

`spec.imageLookupBaseOS`

`spec.imageLookupFormat`

`spec.imageLookupOrg`

`spec.networkInterfaces`

`spec.privateDNSName`

`spec.securityGroupOverrides`

`spec.uncompressedUserData`

기본 AWS EC2 인스턴스가 제거되면 클러스터 API는 nonroot EBS 볼륨 분리를 지원하지 않습니다. 인스턴스가 종료되면 Cluster API는 모든 종속 볼륨을 제거합니다.

Machine API 리소스를 Cluster API로 마이그레이션할 때 ignition 버전은 하드 코딩되어 전달되는 사용자 데이터 시크릿과 일치하지 않을 수 있습니다.

### 11.6. 클러스터 API 비활성화

클러스터 API 사용을 중지하여 OpenShift Container Platform 클러스터에서 인프라 리소스 관리를 자동화하려면 클러스터의 Cluster API 리소스를 동등한 Machine API 리소스로 변환합니다.

중요

클러스터 API를 사용하여 머신을 관리하는 것은 기술 프리뷰 기능만 해당합니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 11.6.1. 클러스터 API 리소스를 머신 API 리소스로 마이그레이션

Machine API 및 Cluster API 리소스 간 마이그레이션을 지원하는 클러스터에서는 양방향 동기화 컨트롤러에서 클러스터 API 리소스를 Machine API 리소스로 변환할 수 있습니다.

참고

양방향 동기화 컨트롤러는 `TechPreviewNoUpgrade` 기능 세트의 `MachineAPIMigration` 기능 게이트가 활성화된 클러스터에서만 작동합니다.

원래 Machine API에서 Cluster API로 마이그레이션한 리소스 또는 Cluster API 리소스로 생성한 리소스를 마이그레이션할 수 있습니다. 원래 머신 API 리소스를 클러스터 API 리소스로 마이그레이션한 다음 다시 마이그레이션하면 마이그레이션 프로세스가 예상대로 작동하는지 확인할 수 있습니다.

참고

지원되는 인프라 유형에서만 일부 리소스를 마이그레이션할 수 있습니다.

| 인프라 | 컴퓨팅 시스템 | 컴퓨팅 머신 세트 | 머신 상태 점검 | 컨트롤 플레인 머신 세트 | Cluster autoscaler |
| --- | --- | --- | --- | --- | --- |
| AWS | 기술 프리뷰 | 기술 프리뷰 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 |
| 기타 모든 인프라 유형 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 | 사용할 수 없음 |

#### 11.6.1.1. Machine API를 사용하도록 클러스터 API 리소스 마이그레이션

개별 Cluster API 오브젝트를 동등한 Machine API 오브젝트로 마이그레이션할 수 있습니다.

중요

Machine API를 사용하도록 클러스터 API 리소스를 마이그레이션하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

사전 요구 사항

지원되는 인프라 유형에 OpenShift Container Platform 클러스터를 배포했습니다.

`TechPreviewNoUpgrade` 기능 세트에서 `MachineAPIMigration` 기능 게이트를 활성화했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 Machine API 리소스로 마이그레이션할 클러스터 API 리소스를 식별합니다.

```shell-session
$ oc get <resource_kind> -n openshift-cluster-api
```

여기서 `<resource_kind` >는 다음 값 중 하나입니다.

`machine.cluster.x-k8s.io`

컴퓨팅 또는 컨트롤 플레인 시스템에 대한 리소스 종류의 정규화된 이름입니다.

`machineset.cluster.x-k8s.io`

컴퓨팅 머신 세트의 리소스 유형의 정규화된 이름입니다.

다음 명령을 실행하여 리소스 사양을 편집합니다.

```shell-session
$ oc edit <resource_kind>/<resource_name> -n openshift-machine-api
```

다음과 같습니다.

`<resource_kind>`

`machineset.machine.openshift.io` 를 사용하여 `machine.machine.openshift.io` 또는 컴퓨팅 머신 세트를 사용하여 컴퓨팅 머신을 지정합니다.

`<resource_name>`

Machine API로 마이그레이션할 클러스터 API 리소스에 해당하는 Machine API 리소스의 이름을 지정합니다.

리소스 사양에서 `spec.authoritativeAPI` 필드의 값을 업데이트합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: <resource_kind>
metadata:
  name: <resource_name>
  [...]
spec:
  authoritativeAPI: MachineAPI
  [...]
status:
  authoritativeAPI: ClusterAPI
  [...]
```

1. 리소스 종류는 리소스 유형에 따라 다릅니다. 예를 들어 컴퓨팅 머신 세트의 리소스 종류는 `MachineSet` 이고 컴퓨팅 머신의 리소스 종류는 `Machine` 입니다.

2. 마이그레이션할 리소스의 이름입니다.

3. 이 리소스를 사용할 권한 있는 API를 지정합니다. 예를 들어, 클러스터 API 리소스를 Machine API로 마이그레이션하려면 `MachineAPI` 를 지정합니다.

4. 현재 권한 있는 API의 값입니다. 이 값은 현재 이 리소스를 관리하는 API를 나타냅니다. 사양의 이 부분에서 값을 변경하지 마십시오.

검증

다음 명령을 실행하여 변환 상태를 확인합니다.

```shell-session
$ oc -n openshift-machine-api get <resource_kind>/<resource_name> -o json | jq .status.authoritativeAPI
```

다음과 같습니다.

`<resource_kind>`

`machineset.machine.openshift.io` 를 사용하여 `machine.machine.openshift.io` 또는 컴퓨팅 머신 세트를 사용하여 컴퓨팅 머신을 지정합니다.

`<resource_name>`

Machine API로 마이그레이션할 클러스터 API 리소스에 해당하는 Machine API 리소스의 이름을 지정합니다.

변환이 진행되는 동안 이 명령은 `Migrating` 값을 반환합니다. 이 값이 장기간 지속되는 경우 `openshift-cluster-api` 네임스페이스에서 `cluster-capi-operator` 배포의 로그를 확인하고 잠재적인 문제를 확인합니다.

변환이 완료되면 이 명령은 `MachineAPI` 값을 반환합니다.

중요

현재 권한 있는 API를 사용하는 해당 리소스를 삭제하려면 현재 권한 있는 API를 사용하지 않는 권한 없는 리소스는 삭제하지 마십시오.

현재 권한 있는 API를 사용하지 않는 권한 없는 리소스를 삭제하면 동기화 컨트롤러에서 현재 권한 있는 API를 사용하는 해당 리소스를 삭제합니다. 자세한 내용은 리소스 마이그레이션 문제 해결 콘텐츠에서 "Unexpected resource deletion behavior"를 참조하십시오.

#### 11.6.1.2. 신뢰할 수 있는 API 유형의 컴퓨팅 시스템

컴퓨팅 시스템의 권한 있는 API는 이를 생성하는 Machine API 컴퓨팅 머신 세트의 `.spec.authoritativeAPI` 및 `.spec.template.spec.authoritativeAPI` 필드의 값에 따라 다릅니다.

| `.spec.authoritativeAPI` value | `ClusterAPI` | `ClusterAPI` | `MachineAPI` | `MachineAPI` |
| --- | --- | --- | --- | --- |
| `.spec.template.spec.authoritativeAPI` value | `ClusterAPI` | `MachineAPI` | `MachineAPI` | `ClusterAPI` |
| 새 컴퓨팅 시스템에 대한 `authoritativeAPI` 값 | `ClusterAPI` | `ClusterAPI` | `MachineAPI` | `ClusterAPI` |

참고

`.spec.authoritativeAPI` 값이 `ClusterAPI` 인 경우 Machine API 머신 세트가 권한이 없으며 `.spec.template.spec.authoritativeAPI` 값이 사용되지 않습니다. 결과적으로 `Machine API` 를 사용하여 권한 있는 대로 컴퓨팅 머신을 생성하는 유일한 조합은 `.spec.authoritativeAPI` 및 `.spec.template.spec.authoritativeAPI` 값이 MachineAPI인 입니다.

추가 리소스

리소스 마이그레이션 문제 해결

클러스터 API 리소스로 머신 API 리소스 마이그레이션

## 12장. 머신 상태 확인

머신 풀에서 손상된 머신을 자동으로 복구하도록 머신 상태 점검을 구성하고 배포할 수 있습니다.

중요

머신 API가 작동하는 클러스터에서만 고급 머신 관리 및 스케일링 기능을 사용할 수 있습니다. 사용자 프로비저닝 인프라가 있는 클러스터에는 Machine API를 사용하기 위해 추가 검증 및 구성이 필요합니다.

인프라 플랫폼 유형이 `none` 인 클러스터는 Machine API를 사용할 수 없습니다. 이 제한은 클러스터에 연결된 컴퓨팅 머신이 기능을 지원하는 플랫폼에 설치된 경우에도 적용됩니다. 설치 후에는 이 매개변수를 변경할 수 없습니다.

클러스터의 플랫폼 유형을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get infrastructure cluster -o jsonpath='{.status.platform}'
```

### 12.1. 머신 상태 점검 정보

참고

컴퓨팅 머신 세트 또는 컨트롤 플레인 머신 세트에서 관리하는 머신에만 머신 상태 점검을 적용할 수 있습니다.

머신 상태를 모니터링하기 위해 컨트롤러 구성을 정의할 리소스를 만듭니다. `NotReady` 상태를 5 분 동안 유지하거나 노드 문제 탐지기(node-problem-detector)에 영구적인 조건을 표시하는 등 검사할 조건과 모니터링할 머신 세트의 레이블을 설정합니다.

`MachineHealthCheck` 리소스를 관찰하는 컨트롤러에서 정의된 상태를 확인합니다. 머신이 상태 확인에 실패하면 머신이 자동으로 삭제되고 대체할 머신이 만들어집니다. 머신이 삭제되면 `machine deleted` 이벤트가 표시됩니다.

머신 삭제로 인한 영향을 제한하기 위해 컨트롤러는 한 번에 하나의 노드 만 드레인하고 삭제합니다. 대상 머신 풀에서 허용된 `maxUnhealthy` 임계값 보다 많은 비정상적인 머신이 있는 경우 수동 개입이 수행될 수 있도록 복구가 중지됩니다.

참고

워크로드 및 요구 사항을 살펴보고 신중하게 시간 초과를 고려하십시오.

시간 제한이 길어지면 비정상 머신의 워크로드에 대한 다운타임이 길어질 수 있습니다.

시간 초과가 너무 짧으면 수정 루프가 발생할 수 있습니다. 예를 들어 `NotReady` 상태를 확인하는 시간은 머신이 시작 프로세스를 완료할 수 있을 만큼 충분히 길어야 합니다.

검사를 중지하려면 리소스를 제거합니다.

#### 12.1.1. 머신 상태 검사 배포 시 제한 사항

머신 상태 점검을 배포하기 전에 고려해야 할 제한 사항은 다음과 같습니다.

머신 세트가 소유한 머신만 머신 상태 검사를 통해 업데이트를 적용합니다.

머신의 노드가 클러스터에서 제거되면 머신 상태 점검에서 이 머신을 비정상적으로 간주하고 즉시 업데이트를 적용합니다.

`nodeStartupTimeout` 후 시스템의 해당 노드가 클러스터에 참여하지 않으면 업데이트가 적용됩니다.

`Machine` 리소스 단계가 `Failed` 하면 즉시 머신에 업데이트를 적용합니다.

추가 리소스

클러스터의 모든 노드 나열 정보

쇼트 서킷 (Short Circuit) 머신 상태 점검 및 수정

컨트롤 플레인 머신 세트 Operator 정보

### 12.2. MachineHealthCheck 리소스 샘플

베어 메탈 이외의 모든 클라우드 기반 설치 유형에 대한 `MachineHealthCheck` 리소스는 다음 YAML 파일과 유사합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: example
  namespace: openshift-machine-api
spec:
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-machine-role: <role>
      machine.openshift.io/cluster-api-machine-type: <role>
      machine.openshift.io/cluster-api-machineset: <cluster_name>-<label>-<zone>
  unhealthyConditions:
  - type:    "Ready"
    timeout: "300s"
    status: "False"
  - type:    "Ready"
    timeout: "300s"
    status: "Unknown"
  maxUnhealthy: "40%"
  nodeStartupTimeout: "10m"
```

1. 배포할 머신 상태 점검의 이름을 지정합니다.

2. 3

확인할 머신 풀의 레이블을 지정합니다.

4. 추적할 머신 세트를 `<cluster_name>-<label>-<zone>` 형식으로 지정합니다. 예를 들어 `prod-node-us-east-1a` 입니다.

5. 6

노드 상태에 대한 시간 제한을 지정합니다. 시간 제한 기간 중 상태가 일치되면 머신이 수정됩니다. 시간 제한이 길어지면 비정상 머신의 워크로드에 대한 다운타임이 길어질 수 있습니다.

7. 대상 풀에서 동시에 복구할 수 있는 시스템 수를 지정합니다. 이는 백분율 또는 정수로 설정할 수 있습니다. 비정상 머신의 수가 `maxUnhealthy` 에서의 설정 제한을 초과하면 복구가 수행되지 않습니다.

8. 머신 상태가 비정상으로 확인되기 전에 노드가 클러스터에 참여할 때까지 기다려야 하는 시간 초과 기간을 지정합니다.

참고

`matchLabels` 는 예제일 뿐입니다. 특정 요구에 따라 머신 그룹을 매핑해야 합니다.

#### 12.2.1. 쇼트 서킷 (Short Circuit) 머신 상태 점검 및 수정

쇼트 서킷은 클러스터가 정상일 때만 머신 상태 점검에서 머신을 수정할 수 있도록 합니다. 쇼트 서킷은 `MachineHealthCheck` 리소스의 `maxUnhealthy` 필드를 통해 구성됩니다.

사용자가 시스템을 조정하기 전에 `maxUnhealthy` 필드 값을 정의하는 경우 `MachineHealthCheck` 는 비정상적으로 결정된 대상 풀 내의 `maxUnhealthy` 값과 비교합니다. 비정상 머신의 수가 `maxUnhealthy` 제한을 초과하면 수정을 위한 업데이트가 수행되지 않습니다.

중요

`maxUnhealthy` 가 설정되지 않은 경우 기본값은 `100%` 로 설정되고 클러스터 상태와 관계없이 머신이 수정됩니다.

적절한 `maxUnhealthy` 값은 배포하는 클러스터의 규모와 `MachineHealthCheck에서` 다루는 시스템 수에 따라 달라집니다. 예를 들어, `maxUnhealthy` 값을 사용하여 여러 가용성 영역에 걸쳐 여러 컴퓨팅 머신 세트를 포괄할 수 있으므로 전체 영역이 손실되더라도 `maxUnhealthy` 설정으로 인해 클러스터 내에서 추가적인 수정이 불가능합니다. 여러 가용성 영역이 없는 글로벌 Azure 리전에서는 가용성 세트를 사용하여 고가용성을 보장할 수 있습니다.

중요

컨트롤 플레인에 대해 `MachineHealthCheck` 리소스를 구성하는 경우 `maxUnhealthy` 값을 `1` 로 설정합니다.

이 구성을 사용하면 여러 컨트롤 플레인 머신이 비정상으로 표시될 때 머신 상태 점검에서 아무 작업도 수행하지 않습니다. 여러 비정상적인 컨트롤 플레인 시스템은 etcd 클러스터의 성능이 저하되거나 실패한 머신을 교체하는 확장 작업이 진행 중임을 나타낼 수 있습니다.

etcd 클러스터의 성능이 저하된 경우 수동 개입이 필요할 수 있습니다. 스케일링 작업이 진행 중인 경우 머신 상태 점검에서 이 작업을 완료할 수 있어야 합니다.

`maxUnhealthy` 필드는 정수 또는 백분율로 설정할 수 있습니다. `maxUnhealthy` 값에 따라 다양한 수정을 적용할 수 있습니다.

#### 12.2.1.1. 절대 값을 사용하여 maxUnhealthy 설정

`maxUnhealthy` 가 `2` 로 설정된 경우

2개 이상의 노드가 비정상인 경우 수정을 위한 업데이트가 수행됩니다.

3개 이상의 노드가 비정상이면 수정을 위한 업데이트가 수행되지 않습니다

이러한 값은 머신 상태 점검에서 확인할 수 있는 머신 수와 관련이 없습니다.

#### 12.2.1.2. 백분율을 사용하여 maxUnhealthy 설정

`maxUnhealthy` 가 `40%` 로 설정되어 있고 25 대의 시스템이 확인되고 있는 경우 다음을 수행하십시오.

10개 이상의 노드가 비정상인 경우 수정을 위한 업데이트가 수행됩니다.

11개 이상의 노드가 비정상인 경우 수정을 위한 업데이트가 수행되지 않습니다.

`maxUnhealthy` 가 `40%` 로 설정되어 있고 6 대의 시스템이 확인되고 있는 경우 다음을 수행하십시오.

2개 이상의 노드가 비정상인 경우 수정을 위한 업데이트가 수행됩니다.

3개 이상의 노드가 비정상이면 수정을 위한 업데이트가 수행되지 않습니다

참고

`maxUnhealthy` 머신의 백분율이 정수가 아닌 경우 허용되는 머신 수가 반올림됩니다.

### 12.3. 머신 상태 점검 리소스 생성

클러스터에서 머신 세트에 대한 `MachineHealthCheck` 리소스를 생성할 수 있습니다.

참고

컴퓨팅 머신 세트 또는 컨트롤 플레인 머신 세트에서 관리하는 머신에만 머신 상태 점검을 적용할 수 있습니다.

사전 요구 사항

아래 명령줄 인터페이스를 설치합니다.

```shell
oc
```

프로세스

머신 상태 점검 정의가 포함된 `healthcheck.yml` 파일을 생성합니다.

`healthcheck.yml` 파일을 클러스터에 적용합니다.

```shell-session
$ oc apply -f healthcheck.yml
```

머신 상태 점검을 구성하고 배포하여 비정상적인 베어 메탈 노드를 감지하고 복구할 수 있습니다.

### 12.4. 베어 메탈의 전원 기반 업데이트 적용 정보

베어 메탈 클러스터에서 노드의 업데이트 적용은 클러스터의 전반적인 상태를 보장하는 데 중요합니다. 물리적으로 클러스터에 업데이트를 적용하는 것은 어려움이 있을 수 있으며 머신을 안전하거나 운영 체제로 전환하기 위한 지연으로 인해 클러스터가 성능 저하된 상태로 유지되는 시간이 길어지고 이후의 장애 발생으로 인해 클러스터가 클러스터를 오프라인 상태가 될 수 있습니다. 전원 기반 문제 해결은 이러한 문제에 대응하는 데 도움이 됩니다.

전원 기반 업데이트 적용에서는 노드를 재프로비저닝하는 대신 전원 컨트롤러를 사용하여 작동하지 않는 노드의 전원을 끕니다. 이러한 유형의 수정을 전원 펜싱이라고 합니다.

OpenShift Container Platform은 `MachineHealthCheck` 컨트롤러를 사용하여 문제가 있는 베어 메탈 노드를 감지합니다. 전원 기반 업데이트 적용은 신속하게 수행되며 클러스터에서 문제가 있는 노드를 제거하는 대신 재부팅합니다.

전원 기반 업데이트 적용은 다음과 같은 기능을 제공합니다.

컨트롤 플레인 노드를 복구 가능

하이퍼컨버지드 환경의 데이터 손실 위험을 줄입니다.

물리적 머신 복구와 관련된 다운타임 감소

#### 12.4.1. 베어 메탈에서 MachineHealthCheck

베어 메탈 클러스터에서 머신 삭제를 사용하면 베어 메탈 호스트의 재프로비저닝이 트리거됩니다. 일반적으로 베어 메탈 재프로비저닝은 시간이 오래 걸리는 프로세스로, 이 과정에서 클러스터에 컴퓨팅 리소스가 누락되고 애플리케이션이 중단될 수 있습니다.

기본 수정 프로세스를 시스템 삭제에서 호스트 전원 사이클로 변경하는 방법은 다음 두 가지가 있습니다.

`machine.openshift.io/remediation-strategy: external-baremetal` 주석을 사용하여 `MachineHealthCheck` 리소스에 주석을 답니다.

`Metal3RemediationTemplate` 리소스를 생성하고 `MachineHealthCheck` 의 `spec.remediationTemplate` 에서 참조하십시오.

이러한 방법 중 하나를 사용하면 비정상 머신이 BMC(Baseboard Management Controller) 인증 정보를 사용하여 전원을 켭니다.

#### 12.4.2. 주석 기반 수정 프로세스 이해

수정 프로세스는 다음과 같이 작동합니다.

MHC(MachineHealthCheck) 컨트롤러는 노드가 비정상임을 감지합니다.

MHC는 비정상 노드의 전원을 끄도록 요청하는 베어 메탈 머신 컨트롤러에 통지합니다.

전원이 꺼지면 노드가 삭제되어 클러스터가 다른 노드에서 영향을 받는 워크로드를 다시 예약할 수 있습니다.

베어 메탈 머신 컨트롤러에서 노드의 전원을 켜도록 요청합니다.

노드가 가동되면 노드가 클러스터와 함께 다시 등록되어 새 노드가 생성됩니다.

노드가 다시 생성되면 베어 메탈 머신 컨트롤러는 삭제하기 전에 비정상 노드에 존재하는 주석 및 레이블을 복원합니다.

참고

전원 작업이 완료되지 않은 경우 베어 메탈 머신 컨트롤러는 컨트롤 플레인 노드 또는 외부 프로비저닝 노드가 아닌 한 비정상 노드의 재프로비저닝을 트리거합니다.

#### 12.4.3. metal3- 기반 수정 프로세스 이해

수정 프로세스는 다음과 같이 작동합니다.

MHC(MachineHealthCheck) 컨트롤러는 노드가 비정상임을 감지합니다.

MHC는 metal3 수정 컨트롤러에 대한 metal3 수정 사용자 정의 리소스를 생성하여 비정상 노드의 전원을 끄도록 요청합니다.

전원이 꺼지면 노드가 삭제되어 클러스터가 다른 노드에서 영향을 받는 워크로드를 다시 예약할 수 있습니다.

metal3 수정 컨트롤러에서 노드의 전원을 켜도록 요청합니다.

노드가 가동되면 노드가 클러스터와 함께 다시 등록되어 새 노드가 생성됩니다.

노드가 다시 생성되면 metal3 수정 컨트롤러에서 삭제하기 전에 비정상 노드에 존재하는 주석 및 레이블을 복원합니다.

참고

전원 작업이 완료되지 않으면 metal3 수정 컨트롤러에서 컨트롤 플레인 노드 또는 외부 프로비저닝 노드가 아닌 한 비정상 노드의 재프로비저닝을 트리거합니다.

#### 12.4.4. 베어 메탈의 MachineHealthCheck 리소스 생성

사전 요구 사항

OpenShift Container Platform은 설치 관리자 프로비저닝 인프라(IPI)를 사용하여 설치됩니다.

BMC 자격 증명(또는 각 노드에 대한 BMC 액세스)에 액세스합니다.

비정상 노드의 BMC 인터페이스에 대한 네트워크 액세스가 있어야 합니다.

프로세스

머신 상태 점검 정의가 포함된 `healthcheck.yaml` 파일을 생성합니다.

다음 명령을 사용하여 `healthcheck.yaml` 파일을 클러스터에 적용합니다.

```shell-session
$ oc apply -f healthcheck.yaml
```

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: example
  namespace: openshift-machine-api
  annotations:
    machine.openshift.io/remediation-strategy: external-baremetal
spec:
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-machine-role: <role>
      machine.openshift.io/cluster-api-machine-type: <role>
      machine.openshift.io/cluster-api-machineset: <cluster_name>-<label>-<zone>
  unhealthyConditions:
  - type:    "Ready"
    timeout: "300s"
    status: "False"
  - type:    "Ready"
    timeout: "300s"
    status: "Unknown"
  maxUnhealthy: "40%"
  nodeStartupTimeout: "10m"
```

1. 배포할 머신 상태 점검의 이름을 지정합니다.

2. 베어 메탈 클러스터의 경우 전원 사이클 수정을 활성화하려면 `annotations` 섹션에 `machine.openshift.io/remediation-strategy: external-baremetal` 주석을 포함해야 합니다. 이 업데이트 적용 전략으로 비정상 호스트가 클러스터에서 제거되지 않고 재부팅됩니다.

3. 4

확인할 머신 풀의 레이블을 지정합니다.

5. 추적할 컴퓨팅 머신 세트를 < `cluster_name>-<label>-<zone` > 형식으로 지정합니다. 예를 들어 `prod-node-us-east-1a` 입니다.

6. 7

노드 상태에 대한 시간 제한을 지정합니다. 시간 제한 기간 중 상태가 일치되면 머신이 수정됩니다. 시간 제한이 길어지면 비정상 머신의 워크로드에 대한 다운타임이 길어질 수 있습니다.

8. 대상 풀에서 동시에 복구할 수 있는 시스템 수를 지정합니다. 이는 백분율 또는 정수로 설정할 수 있습니다. 비정상 머신의 수가 `maxUnhealthy` 에서의 설정 제한을 초과하면 복구가 수행되지 않습니다.

9. 머신 상태가 비정상으로 확인되기 전에 노드가 클러스터에 참여할 때까지 기다려야 하는 시간 초과 기간을 지정합니다.

참고

`matchLabels` 는 예제일 뿐입니다. 특정 요구에 따라 머신 그룹을 매핑해야 합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: example
  namespace: openshift-machine-api
spec:
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-machine-role: <role>
      machine.openshift.io/cluster-api-machine-type: <role>
      machine.openshift.io/cluster-api-machineset: <cluster_name>-<label>-<zone>
  remediationTemplate:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: Metal3RemediationTemplate
    name: metal3-remediation-template
    namespace: openshift-machine-api
  unhealthyConditions:
  - type:    "Ready"
    timeout: "300s"
```

```yaml
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: Metal3RemediationTemplate
metadata:
  name: metal3-remediation-template
  namespace: openshift-machine-api
spec:
  template:
    spec:
      strategy:
        type: Reboot
        retryLimit: 1
        timeout: 5m0s
```

참고

`matchLabels` 는 예제일 뿐입니다. 특정 요구에 따라 머신 그룹을 매핑해야 합니다. `annotations` 섹션은 metal3- 기반 수정에는 적용되지 않습니다. 주석 기반 수정 및 metal3- 기반 수정은 함께 사용할 수 없습니다.

#### 12.4.5. 전원 기반 수정 문제 해결

전원 기반 수정 문제를 해결하려면 다음을 확인합니다.

BMC에 액세스할 수 있습니다.

BMC는 수정 작업을 실행하는 컨트롤 플레인 노드에 연결됩니다.
