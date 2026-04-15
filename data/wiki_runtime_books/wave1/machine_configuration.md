# 머신 구성

## Overview

이 문서는 OpenShift 노드의 운영 체제 설정과 kubelet, CRI-O, NetworkManager 같은 머신 수준 구성을 Machine Config Operator(MCO)로 관리할 때 먼저 봐야 하는 핵심 경로를 정리한다.

MCO는 노드별 수작업 변경을 권장하지 않는다. 운영 체제 파일, kubelet 설정, 커널 인자, 시스템 서비스 변경은 `MachineConfig` 또는 관련 사용자 정의 리소스(CR)로 선언하고, 노드 풀 단위로 적용하는 것을 기준으로 한다.

## When To Use

- worker 또는 control plane 노드의 운영 체제 설정을 일관되게 바꿔야 할 때
- kubelet 설정을 `KubeletConfig` CR로 조정해야 할 때
- 노드 업데이트 진행 상태와 장애 징후를 운영 관점에서 추적해야 할 때

## Before You Begin

- 대상 노드가 속한 Machine Config Pool(MCP)을 먼저 확인한다.
- 한 노드는 여러 레이블을 가질 수 있어도 단 하나의 machine config pool에만 속한다는 점을 전제로 한다.
- MCO가 관리하는 변경은 적용 시 노드 재부팅을 유발할 수 있다. 자동 재부팅을 피해야 하면 먼저 `spec.paused=true` 적용 여부를 검토한다.
- 수동으로 노드 파일을 바꾸는 방식은 피한다. MCO가 관리하는 파일에 충돌이 생기면 노드는 `degraded` 상태가 될 수 있다.

## Understand the Machine Config Model

MCO는 세 가지 핵심 구성 요소로 노드 구성을 관리한다.

- `machine-config-controller`: control plane에서 전체 노드 구성을 조율한다.
- `machine-config-daemon`: 각 노드에서 설정 변경, 드레인, 재부팅을 실제로 수행한다.
- `machine-config-server`: 신규 control plane 노드가 필요한 Ignition 구성을 받을 수 있게 한다.

실제 변경은 `MachineConfig`, `KubeletConfig`, `ContainerRuntime` 같은 선언형 자산으로 전달한다. 운영자는 노드에 직접 접속해 설정을 덧칠하는 대신, 풀 단위로 어떤 설정이 들어가야 하는지 명시해야 한다.

## Configure Kubelet or Machine Settings

`KubeletConfig`는 kubelet 매개변수를 선언형으로 수정하는 기본 경로다. 개별 변경마다 새 CR을 남발하기보다, 같은 풀에 필요한 설정을 한 리소스로 관리하는 편이 운영과 롤백에 유리하다.

중요한 운영 규칙:

- 같은 MCP에 적용할 변경은 가능한 한 하나의 `KubeletConfig` CR에 모은다.
- 다른 풀에 임시 변경을 줄 때만 별도 CR을 분리한다.
- 클러스터당 `KubeletConfig` CR은 최대 10개까지 허용된다.
- `machineConfigSelector`의 사용자 정의 역할은 대상 MCP 이름과 일치해야 한다.
- 기존 머신 구성을 제거할 때는 생성 역순으로 정리한다.

예시 MCP:

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  name: infra
spec:
  machineConfigSelector:
    matchExpressions:
    - {key: machineconfiguration.openshift.io/role, operator: In, values: [worker,infra]}
```

변경 적용 전후 확인 명령:

```shell
oc get kubeletconfig
oc get mc | grep kubelet
```

## Verify Node Rollout

변경 후에는 MCP 상태만 보지 말고 `MachineConfigNode` 기준으로 개별 노드가 어느 단계에 있는지 확인한다. 이 문서군에서 가장 실용적인 검증 포인트는 아래 두 개다.

```shell
oc get machineconfignodes
oc describe machineconfignodes
```

운영자가 봐야 하는 단계:

- `UpdatePrepared`: 새 machine config를 적용할 준비가 끝났는지
- `UpdateExecuted`: cordon, drain, 파일/OS 적용이 수행됐는지
- `RebootedNode`: 재부팅이 실제로 발생했는지
- `UpdateComplete`: uncordon까지 끝났는지
- `Resumed`: drift monitor 재개 후 정상 운영 상태로 돌아왔는지

노드별 `desired config`와 `current config`가 다르면 아직 적용 중이거나 실패 상태일 수 있다. `oc describe machineconfignode/<name>`로 이유를 바로 확인한다.

## Failure Signals

다음 상태가 보이면 바로 중단하고 원인을 먼저 본다.

- `KubeletConfig` 값 오류로 노드가 사용 불가 상태가 되는 경우
- MCP 이름과 사용자 정의 역할이 맞지 않아 설정이 엉뚱한 풀에 적용되는 경우
- `MachineConfigNode`가 `UpdateExecuted` 이후 진행하지 못하고 멈추는 경우
- 수동 변경 충돌로 MCO가 노드를 `degraded`로 표시하는 경우
- 자동 재부팅을 고려하지 않고 변경을 밀어 서비스 영향이 커지는 경우

장애 증거를 넓게 수집할 때는 다음 명령을 우선 사용한다.

```shell
oc adm must-gather
```

Machine Config Daemon 지표와 노드 상태를 함께 보면, 단순 지연인지 실제 실패인지 구분하기 쉽다.

## Source Trace

- AsciiDoc source:
  - `machine_configuration/index.adoc`
  - `modules/understanding-machine-config-operator.adoc`
  - `modules/machine-config-overview.adoc`
  - `modules/checking-mco-node-status.adoc`
- Trial inputs:
  - `04_procedure_code_verify`
  - `08_operator_first`
  - `10_verify_first_ops`
