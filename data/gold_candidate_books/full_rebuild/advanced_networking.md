# 고급 네트워킹

## OpenShift Container Platform의 전문화된 고급 네트워킹 주제

이 문서에서는 OpenShift Container Platform의 MTU 변경, 연결 확인, 스트림 제어 전송 프로토콜, PTP 하드웨어 및 보조 인터페이스 메트릭을 비롯한 고급 네트워킹 주제를 다룹니다.

## 1장. 끝점에 대한 연결 확인

CNO(Cluster Network Operator)는 클러스터 내 리소스 간에 연결 상태 검사를 수행하는 연결 확인 컨트롤러인 컨트롤러를 실행합니다. 상태 점검 결과를 검토하여 연결 문제를 진단하거나 현재 조사하고 있는 문제의 원인으로 네트워크 연결을 제거할 수 있습니다.

### 1.1. 수행되는 연결 상태 점검

클러스터 리소스에 도달할 수 있는지 확인하기 위해 다음 클러스터 API 서비스 각각에 TCP 연결이 수행됩니다.

Kubernetes API 서버 서비스

Kubernetes API 서버 끝점

OpenShift API 서버 서비스

OpenShift API 서버 끝점

로드 밸런서

클러스터의 모든 노드에서 서비스 및 서비스 끝점에 도달할 수 있는지 확인하기 위해 다음 대상 각각에 TCP 연결이 수행됩니다.

상태 점검 대상 서비스

상태 점검 대상 끝점

### 1.2. 연결 상태 점검 구현

연결 검증 컨트롤러는 클러스터의 연결 확인 검사를 오케스트레이션합니다. 연결 테스트의 결과는 `openshift-network-diagnostics` 의 `PodNetworkConnectivity` 오브젝트에 저장됩니다. 연결 테스트는 병렬로 1분마다 수행됩니다.

CNO(Cluster Network Operator)는 클러스터에 여러 리소스를 배포하여 연결 상태 점검을 전달하고 수신합니다.

상태 점검 소스

이 프로그램은 `Deployment` 오브젝트에서 관리하는 단일 포드 복제본 세트에 배포됩니다. 프로그램은 `PodNetworkConnectivity` 오브젝트를 사용하고 각 오브젝트에 지정된 `spec.targetEndpoint` 에 연결됩니다.

상태 점검 대상

클러스터의 모든 노드에서 데몬 세트의 일부로 배포된 포드입니다. 포드는 인바운드 상태 점검을 수신 대기합니다. 모든 노드에 이 포드가 있으면 각 노드로의 연결을 테스트할 수 있습니다.

노드 선택기를 사용하여 네트워크 연결 소스 및 대상이 실행되는 노드를 구성할 수 있습니다. 또한 소스 및 대상 Pod에 대해 허용 가능한 허용 오차 를 지정할 수 있습니다. 구성은 `config.openshift.io/v1` API 그룹에 있는 `네트워크` API의 싱글톤 `클러스터` 사용자 정의 리소스에 정의됩니다.

구성을 업데이트한 후 Pod 예약이 수행됩니다. 따라서 구성을 업데이트하기 전에 선택기에서 사용하려는 노드 레이블을 적용해야 합니다. 네트워크 연결을 업데이트한 후 적용되는 레이블은 Pod 배치가 무시됩니다.

다음 YAML의 기본 구성을 참조하십시오.

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  # ...
    networkDiagnostics:
      mode: "All"
      sourcePlacement:
        nodeSelector:
          checkNodes: groupA
        tolerations:
        - key: myTaint
          effect: NoSchedule
          operator: Exists
      targetPlacement:
        nodeSelector:
          checkNodes: groupB
        tolerations:
        - key: myOtherTaint
          effect: NoExecute
          operator: Exists
```

1. 네트워크 진단 구성을 지정합니다. 값을 지정하지 않거나 빈 오브젝트가 지정되고 `spec.disableNetworkDiagnostics=true` 가 `network.operator.openshift.io` 사용자 정의 리소스에 설정된 경우 네트워크 진단이 비활성화됩니다.

설정된 경우 이 값은 `spec.disableNetworkDiagnostics=true` 를 덮어씁니다.

2. 진단 모드를 지정합니다. 값은 빈 문자열, `All` 또는 `Disabled` 일 수 있습니다. 빈 문자열은 `All` 을 지정하는 것과 동일합니다.

3. 선택 사항: 연결 확인 소스 Pod에 대한 선택기를 지정합니다. `nodeSelector` 및 `tolerations` 필드를 사용하여 `sourceNode` Pod를 추가로 지정할 수 있습니다. 이는 소스 및 대상 Pod 모두에 대해 선택 사항입니다. 생략하거나 둘 다 사용하거나 둘 중 하나만 사용할 수 있습니다.

4. 선택 사항: 연결 확인 대상 Pod에 대한 선택기를 지정합니다. `nodeSelector` 및 `tolerations` 필드를 사용하여 `targetNode` Pod를 추가로 지정할 수 있습니다. 이는 소스 및 대상 Pod 모두에 대해 선택 사항입니다. 생략하거나 둘 다 사용하거나 둘 중 하나만 사용할 수 있습니다.

### 1.3. Pod 연결 점검 배치 구성

클러스터 관리자는 `cluster` 라는 `network.config.openshift.io` 오브젝트를 수정하여 연결 점검 Pod가 실행되는 노드를 구성할 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로세스

다음 명령을 입력하여 연결 점검 구성을 편집합니다.

```shell-session
$ oc edit network.config.openshift.io cluster
```

텍스트 편집기에서 `networkDiagnostics` 스탠자를 업데이트하여 소스 및 대상 Pod에 원하는 노드 선택기를 지정합니다.

변경 사항을 저장하고 텍스트 편집기를 종료합니다.

검증

다음 명령을 입력하여 소스 및 대상 Pod가 의도한 노드에서 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n openshift-network-diagnostics -o wide
```

```plaintext
NAME                                    READY   STATUS    RESTARTS   AGE     IP           NODE                                        NOMINATED NODE   READINESS GATES
network-check-source-84c69dbd6b-p8f7n   1/1     Running   0          9h      10.131.0.8   ip-10-0-40-197.us-east-2.compute.internal   <none>           <none>
network-check-target-46pct              1/1     Running   0          9h      10.131.0.6   ip-10-0-40-197.us-east-2.compute.internal   <none>           <none>
network-check-target-8kwgf              1/1     Running   0          9h      10.128.2.4   ip-10-0-95-74.us-east-2.compute.internal    <none>           <none>
network-check-target-jc6n7              1/1     Running   0          9h      10.129.2.4   ip-10-0-21-151.us-east-2.compute.internal   <none>           <none>
network-check-target-lvwnn              1/1     Running   0          9h      10.128.0.7   ip-10-0-17-129.us-east-2.compute.internal   <none>           <none>
network-check-target-nslvj              1/1     Running   0          9h      10.130.0.7   ip-10-0-89-148.us-east-2.compute.internal   <none>           <none>
network-check-target-z2sfx              1/1     Running   0          9h      10.129.0.4   ip-10-0-60-253.us-east-2.compute.internal   <none>           <none>
```

### 1.4. PodNetworkConnectivityCheck 오브젝트 필드

`PodNetworkConnectivityCheck` 오브젝트 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | 다음과 같은 형식의 오브젝트 이름: `<source>-to-<target>` . `<target>` 에서 설명한 대상에는 다음 문자열 중 하나가 포함되어 있습니다. `load-balancer-api-external` `load-balancer-api-internal` `kubernetes-apiserver-endpoint` `kubernetes-apiserver-service-cluster` `network-check-target` `openshift-apiserver-endpoint` `openshift-apiserver-service-cluster` |
| `metadata.namespace` | `string` | 오브젝트와 연결된 네임스페이스입니다. 이 값은 항상 `openshift-network-diagnostics` 입니다. |
| `spec.sourcePod` | `string` | 연결 확인이 시작된 포드의 이름입니다(예: `network-check-source-596b4c6566-rgh92` ). |
| `spec.targetEndpoint` | `string` | 연결 검사의 대상입니다(예: `api.devcluster.example.com:6443` ). |
| `spec.tlsClientCert` | `object` | 사용할 TLS 인증서 설정입니다. |
| `spec.tlsClientCert.name` | `string` | 해당하는 경우 사용되는 TLS 인증서의 이름입니다. 기본값은 빈 문자열입니다. |
| `status` | `object` | 연결 테스트의 조건 및 최근 연결 성공 및 실패의 로그를 나타내는 오브젝트입니다. |
| `status.conditions` | `array` | 연결 확인의 최신 상태 및 모든 이전 상태입니다. |
| `status.failures` | `array` | 실패한 시도에서의 연결 테스트 로그입니다. |
| `status.outages` | `array` | 중단 기간을 포함하는 테스트 로그를 연결합니다. |
| `status.successes` | `array` | 성공적인 시도에서의 연결 테스트 로그입니다. |

다음 표에서는 `status.conditions` 배열에서 오브젝트 필드를 설명합니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `lastTransitionTime` | `string` | 연결 조건이 하나의 상태에서 다른 상태로 전환된 시간입니다. |
| `message` | `string` | 사람이 읽기 쉬운 형식으로 마지막 전환에 대한 세부 정보입니다. |
| `reason` | `string` | 머신에서 읽을 수 있는 형식으로 전환의 마지막 상태입니다. |
| `status` | `string` | 조건의 상태: |
| `type` | `string` | 조건의 유형입니다. |

다음 표에서는 `status.conditions` 배열에서 오브젝트 필드를 설명합니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `end` | `string` | 연결 오류가 해결될 때부터의 타임 스탬프입니다. |
| `endLogs` | `array` | 서비스 중단의 성공적인 종료와 관련된 로그 항목을 포함한 연결 로그 항목입니다. |
| `message` | `string` | 사람이 읽을 수 있는 형식의 중단 세부 정보에 대한 요약입니다. |
| `start` | `string` | 연결 오류가 먼저 감지될 때부터의 타임 스탬프입니다. |
| `startLogs` | `array` | 원래 오류를 포함한 연결 로그 항목입니다. |

#### 1.4.1. 연결 로그 필드

연결 로그 항목의 필드는 다음 표에 설명되어 있습니다. 오브젝트는 다음 필드에서 사용됩니다.

`status.failures[]`

`status.successes[]`

`status.outages[].startLogs[]`

`status.outages[].endLogs[]`

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `latency` | `string` | 작업 기간을 기록합니다. |
| `message` | `string` | 사람이 읽을 수 있는 형식으로 상태를 제공합니다. |
| `reason` | `string` | 머신에서 읽을 수 있는 형식으로 상태의 이유를 제공합니다. 값은 `TCPConnect` , `TCPConnectError` , `DNSResolve` , `DNSError` 중 하나입니다. |
| `success` | `boolean` | 로그 항목이 성공 또는 실패인지를 나타냅니다. |
| `time` | `string` | 연결 확인 시작 시간입니다. |

### 1.5. 끝점에 대한 네트워크 연결 확인

클러스터 관리자는 API 서버, 로드 밸런서, 서비스 또는 Pod와 같은 끝점의 연결을 확인하고 네트워크 진단이 활성화되어 있는지 확인할 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

다음 명령을 입력하여 네트워크 진단이 활성화되었는지 확인합니다.

```shell-session
$ oc get network.config.openshift.io cluster -o yaml
```

```plaintext
# ...
  status:
  # ...
    conditions:
    - lastTransitionTime: "2024-05-27T08:28:39Z"
      message: ""
      reason: AsExpected
      status: "True"
      type: NetworkDiagnosticsAvailable
```

다음 명령을 입력하여 현재 `PodNetworkConnectivityCheck` 오브젝트를 나열합니다.

```shell-session
$ oc get podnetworkconnectivitycheck -n openshift-network-diagnostics
```

```shell-session
NAME                                                                                                                                AGE
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0   75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-1   73m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-2   75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-kubernetes-apiserver-service-cluster                               75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-kubernetes-default-service-cluster                                 75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-load-balancer-api-external                                         75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-load-balancer-api-internal                                         75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-network-check-target-ci-ln-x5sv9rb-f76d1-4rzrp-master-0            75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-network-check-target-ci-ln-x5sv9rb-f76d1-4rzrp-master-1            75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-network-check-target-ci-ln-x5sv9rb-f76d1-4rzrp-master-2            75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-network-check-target-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh      74m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-network-check-target-ci-ln-x5sv9rb-f76d1-4rzrp-worker-c-n8mbf      74m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-network-check-target-ci-ln-x5sv9rb-f76d1-4rzrp-worker-d-4hnrz      74m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-network-check-target-service-cluster                               75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-openshift-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0    75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-openshift-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-1    75m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-openshift-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-2    74m
network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-openshift-apiserver-service-cluster                                75m
```

연결 테스트 로그를 확인합니다.

이전 명령의 출력에서 연결 로그를 검토할 끝점을 식별합니다.

다음 명령을 입력하여 오브젝트를 확인합니다.

```shell-session
$ oc get podnetworkconnectivitycheck <name> \
  -n openshift-network-diagnostics -o yaml
```

여기서 `<name>` 은 `PodNetworkConnectivityCheck` 오브젝트의 이름을 지정합니다.

```shell-session
apiVersion: controlplane.operator.openshift.io/v1alpha1
kind: PodNetworkConnectivityCheck
metadata:
  name: network-check-source-ci-ln-x5sv9rb-f76d1-4rzrp-worker-b-6xdmh-to-kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0
  namespace: openshift-network-diagnostics
  ...
spec:
  sourcePod: network-check-source-7c88f6d9f-hmg2f
  targetEndpoint: 10.0.0.4:6443
  tlsClientCert:
    name: ""
status:
  conditions:
  - lastTransitionTime: "2021-01-13T20:11:34Z"
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnectSuccess
    status: "True"
    type: Reachable
  failures:
  - latency: 2.241775ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: failed
      to establish a TCP connection to 10.0.0.4:6443: dial tcp 10.0.0.4:6443: connect:
      connection refused'
    reason: TCPConnectError
    success: false
    time: "2021-01-13T20:10:34Z"
  - latency: 2.582129ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: failed
      to establish a TCP connection to 10.0.0.4:6443: dial tcp 10.0.0.4:6443: connect:
      connection refused'
    reason: TCPConnectError
    success: false
    time: "2021-01-13T20:09:34Z"
  - latency: 3.483578ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: failed
      to establish a TCP connection to 10.0.0.4:6443: dial tcp 10.0.0.4:6443: connect:
      connection refused'
    reason: TCPConnectError
    success: false
    time: "2021-01-13T20:08:34Z"
  outages:
  - end: "2021-01-13T20:11:34Z"
    endLogs:
    - latency: 2.032018ms
      message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0:
        tcp connection to 10.0.0.4:6443 succeeded'
      reason: TCPConnect
      success: true
      time: "2021-01-13T20:11:34Z"
    - latency: 2.241775ms
      message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0:
        failed to establish a TCP connection to 10.0.0.4:6443: dial tcp 10.0.0.4:6443:
        connect: connection refused'
      reason: TCPConnectError
      success: false
      time: "2021-01-13T20:10:34Z"
    - latency: 2.582129ms
      message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0:
        failed to establish a TCP connection to 10.0.0.4:6443: dial tcp 10.0.0.4:6443:
        connect: connection refused'
      reason: TCPConnectError
      success: false
      time: "2021-01-13T20:09:34Z"
    - latency: 3.483578ms
      message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0:
        failed to establish a TCP connection to 10.0.0.4:6443: dial tcp 10.0.0.4:6443:
        connect: connection refused'
      reason: TCPConnectError
      success: false
      time: "2021-01-13T20:08:34Z"
    message: Connectivity restored after 2m59.999789186s
    start: "2021-01-13T20:08:34Z"
    startLogs:
    - latency: 3.483578ms
      message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0:
        failed to establish a TCP connection to 10.0.0.4:6443: dial tcp 10.0.0.4:6443:
        connect: connection refused'
      reason: TCPConnectError
      success: false
      time: "2021-01-13T20:08:34Z"
  successes:
  - latency: 2.845865ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:14:34Z"
  - latency: 2.926345ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:13:34Z"
  - latency: 2.895796ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:12:34Z"
  - latency: 2.696844ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:11:34Z"
  - latency: 1.502064ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:10:34Z"
  - latency: 1.388857ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:09:34Z"
  - latency: 1.906383ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:08:34Z"
  - latency: 2.089073ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:07:34Z"
  - latency: 2.156994ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:06:34Z"
  - latency: 1.777043ms
    message: 'kubernetes-apiserver-endpoint-ci-ln-x5sv9rb-f76d1-4rzrp-master-0: tcp
      connection to 10.0.0.4:6443 succeeded'
    reason: TCPConnect
    success: true
    time: "2021-01-13T21:05:34Z"
```

## 2장. 클러스터 네트워크의 MTU 변경

클러스터 관리자는 클러스터 설치 후 클러스터 네트워크의 최대 전송 단위(MTU)를 변경할 수 있습니다. MTU 변경을 종료하려면 클러스터 노드를 재부팅해야 하므로 이러한 변경이 중단됩니다.

### 2.1. 클러스터 MTU 정보

설치 중에 클러스터 네트워크 MTU는 클러스터 노드의 기본 네트워크 인터페이스 MTU에 따라 자동으로 설정됩니다. 일반적으로 감지된 MTU를 재정의할 필요가 없습니다.

다음 이유 중 하나로 클러스터 네트워크의 MTU를 변경할 수 있습니다.

클러스터 설치 중에 감지된 MTU는 인프라에 적합하지 않습니다.

이제 최적의 성능을 위해 다른 MTU가 필요한 노드 추가와 같이 클러스터 인프라에 다른 MTU가 필요합니다.

OVN-Kubernetes 네트워크 플러그인만 MTU 값 변경을 지원합니다.

#### 2.1.1. 서비스 중단 고려 사항

클러스터에서 최대 전송 단위(MTU) 변경을 시작하면 다음과 같은 영향이 서비스 가용성에 영향을 미칠 수 있습니다.

새 MTU로의 마이그레이션을 완료하려면 두 개 이상의 롤링 재부팅이 필요합니다. 이 기간 동안 일부 노드를 다시 시작할 수 없으므로 사용할 수 없습니다.

절대 TCP 시간 간격보다 짧은 시간 초과 간격으로 클러스터에 배포된 특정 애플리케이션은 MTU 변경 중에 중단될 수 있습니다.

#### 2.1.2. MTU 값 선택

MTU(최대 전송 단위) 마이그레이션을 계획할 때 고려해야 할 두 개의 관련 MTU 값이 있습니다.

하드웨어 MTU: 이 MTU 값은 네트워크 인프라의 세부 사항에 따라 설정됩니다.

클러스터 네트워크 MTU: 이 MTU 값은 클러스터 네트워크 오버레이 오버헤드를 고려하여 하드웨어 MTU보다 항상 적습니다. 특정 오버헤드는 네트워크 플러그인에 따라 결정됩니다. OVN-Kubernetes의 경우 오버헤드는 `100` 바이트입니다.

클러스터에 다른 노드에 대한 다른 MTU 값이 필요한 경우 클러스터의 모든 노드에서 사용하는 가장 낮은 MTU 값에서 네트워크 플러그인의 오버헤드 값을 제거해야 합니다. 예를 들어, 클러스터의 일부 노드에 `9001` 의 MTU가 있고 일부에는 `1500` 의 MTU가 있는 경우 이 값을 `1400` 으로 설정해야 합니다.

중요

노드에서 허용되지 않는 MTU 값을 선택하지 않으려면 `ip -d link` 명령을 사용하여 네트워크 인터페이스에서 허용하는 최대 MTU 값(`maxmtu`)을 확인합니다.

#### 2.1.3. 마이그레이션 프로세스의 작동 방식

다음 표는 프로세스의 사용자 시작 단계와 마이그레이션이 수행하는 작업 간에 분할하여 마이그레이션 프로세스를 요약합니다.

| 사용자 시작 단계 | OpenShift Container Platform 활동 |
| --- | --- |
| Cluster Network Operator 구성에서 다음 값을 설정합니다. `spec.migration.mtu.machine.to` `spec.migration.mtu.network.from` `spec.migration.mtu.network.to` | CNO(Cluster Network Operator) : 각 필드가 유효한 값으로 설정되어 있는지 확인합니다. 하드웨어의 MTU가 변경되지 않는 경우 `mtu.machine.to` 를 새 하드웨어 MTU 또는 현재 하드웨어 MTU로 설정해야 합니다. 이 값은 일시적인 값이며 마이그레이션 프로세스의 일부로 사용됩니다. 현재 값과 다른 하드웨어 MTU를 설정하는 경우 유지되도록 수동으로 구성해야 합니다. 머신 구성, DHCP 설정 또는 커널 명령줄과 같은 방법을 사용합니다. `mtu.network.from` 필드는 클러스터 네트워크의 현재 MTU인 `network.status.clusterNetworkMTU` 필드와 같아야 합니다. `mtu.network.to` 필드는 대상 클러스터 네트워크 MTU로 설정해야 합니다. 네트워크 플러그인의 오버레이 오버헤드를 허용하려면 하드웨어 MTU보다 작아야 합니다. OVN-Kubernetes의 경우 오버헤드는 `100` 바이트입니다. 제공된 값이 유효한 경우 CNO는 `mtu.network.to` 필드 값으로 설정된 클러스터 네트워크의 MTU를 사용하여 새 임시 구성을 작성합니다. MCO(Machine Config Operator) : 클러스터의 각 노드에 대해 롤링 재부팅을 수행합니다. |
| 클러스터의 노드에 대한 기본 네트워크 인터페이스의 MTU를 재구성합니다. 다음 방법 중 하나를 사용하여 이 작업을 수행할 수 있습니다. MTU 변경으로 새 NetworkManager 연결 프로필 배포 DHCP 서버 설정을 통해 MTU 변경 부팅 매개변수를 통해 MTU 변경 | 해당 없음 |
| 네트워크 플러그인의 CNO 구성에서 `mtu` 값을 설정하고 `spec.migration` 을 `null` 로 설정합니다. | MCO(Machine Config Operator) : 새 MTU 구성으로 클러스터의 각 노드를 롤링 재부팅합니다. |

### 2.2. 클러스터 네트워크 MTU 변경

클러스터 관리자는 클러스터의 최대 전송 단위(MTU)를 늘리거나 줄일 수 있습니다.

중요

MTU 마이그레이션 프로세스 중에 노드의 MTU 값을 롤백할 수는 없지만 MTU 마이그레이션 프로세스가 완료된 후 값을 롤백할 수 있습니다.

MTU 업데이트가 적용되므로 마이그레이션이 중단되고 클러스터의 노드를 일시적으로 사용할 수 없게 될 수 있습니다.

다음 절차에서는 시스템 구성, DHCP(Dynamic Host Configuration Protocol) 또는 ISO 이미지를 사용하여 클러스터 네트워크 MTU를 변경하는 방법을 설명합니다. DHCP 또는 ISO 접근 방식을 사용하는 경우 절차를 완료하기 위해 클러스터를 설치한 후 유지한 구성 아티팩트를 참조해야 합니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

클러스터의 대상 MTU를 식별했습니다. OVN-Kubernetes 네트워크 플러그인의 MTU는 클러스터에서 가장 낮은 하드웨어 MTU 값보다 `100` 으로 설정해야 합니다.

노드가 물리적 시스템인 경우 클러스터 네트워크와 연결된 네트워크 스위치가 점보 프레임을 지원하는지 확인합니다.

노드가 VM(가상 머신)인 경우 하이퍼바이저 및 연결된 네트워크 스위치가 점보 프레임을 지원하는지 확인합니다.

#### 2.2.1. 현재 클러스터 MTU 값 확인

다음 절차를 사용하여 클러스터 네트워크의 현재 최대 전송 단위(MTU)를 가져옵니다.

프로세스

클러스터 네트워크의 현재 MTU를 가져오려면 다음 명령을 입력합니다.

```shell-session
$ oc describe network.config cluster
```

```plaintext
...
Status:
  Cluster Network:
    Cidr:               10.217.0.0/22
    Host Prefix:        23
  Cluster Network MTU:  1400
  Network Type:         OVNKubernetes
  Service Network:
    10.217.4.0/23
...
```

#### 2.2.2. 하드웨어 MTU 구성 준비

클러스터 노드에 대한 하드웨어 최대 전송 단위(MTU)를 구성하는 방법은 여러 가지가 있습니다. 다음 예제에서는 가장 일반적인 방법만 보여줍니다. 인프라 MTU의 정확성을 확인합니다. 클러스터 노드에서 하드웨어 MTU를 구성하는 기본 방법을 선택합니다.

프로세스

하드웨어 MTU에 대한 구성을 준비합니다.

하드웨어 MTU가 DHCP로 지정된 경우 다음 dnsmasq 구성과 같은 DHCP 구성을 업데이트합니다.

```plaintext
dhcp-option-force=26,<mtu>
```

다음과 같습니다.

`<mtu>`

알릴 DHCP 서버의 하드웨어 MTU를 지정합니다.

하드웨어 MTU가 PXE를 사용하여 커널 명령줄로 지정된 경우 그에 따라 해당 구성을 업데이트합니다.

하드웨어 MTU가 NetworkManager 연결 구성에 지정된 경우 다음 단계를 완료합니다. 이 방법은 DHCP, 커널 명령줄 또는 기타 방법으로 네트워크 구성을 명시적으로 지정하지 않는 경우 OpenShift Container Platform의 기본값입니다. 클러스터 노드는 다음 절차에 따라 수정되지 않은 상태로 작동하도록 동일한 기본 네트워크 구성을 사용해야 합니다.

다음 명령을 입력하여 기본 네트워크 인터페이스를 찾습니다.

```shell-session
$ oc debug node/<node_name> -- chroot /host nmcli -g connection.interface-name c show ovs-if-phys0
```

다음과 같습니다.

`<node_name>`

클러스터에 있는 노드의 이름을 지정합니다.

```shell
interface>-mtu.conf 파일에 다음 NetworkManager 구성을 생성합니다.
```

```plaintext
[connection-<interface>-mtu]
match-device=interface-name:<interface>
ethernet.mtu=<mtu>
```

다음과 같습니다.

`<interface>`

기본 네트워크 인터페이스 이름을 지정합니다.

`<mtu>`

새 하드웨어 MTU 값을 지정합니다.

#### 2.2.3. MachineConfig 오브젝트 생성

다음 절차에 따라 `MachineConfig` 오브젝트를 생성합니다.

프로세스

두 개의 `MachineConfig` 오브젝트를 생성합니다. 하나는 컨트롤 플레인 노드용이고 다른 하나는 클러스터의 작업자 노드에 사용됩니다.

`control-plane-interface.bu` 파일에 다음 Butane 구성을 생성합니다.

참고

구성 파일에 지정하는 Butane 버전이 OpenShift Container Platform 버전과 일치해야 하며 항상 `0` 으로 끝나야 합니다. 예: `4.20.0`. Butane에 대한 자세한 내용은 “Butane 을 사용하여 머신 구성 생성”을 참조하십시오.

```yaml
variant: openshift
version: 4.20.0
metadata:
  name: 01-control-plane-interface
  labels:
    machineconfiguration.openshift.io/role: master
storage:
  files:
    - path: /etc/NetworkManager/conf.d/99-<interface>-mtu.conf
      contents:
        local: <interface>-mtu.conf
      mode: 0600
```

1. 기본 네트워크 인터페이스의 `NetworkManager` 연결 이름을 지정합니다.

2. 이전 단계에서 업데이트된 `NetworkManager` 구성 파일의 로컬 파일 이름을 지정합니다.

`worker-interface.bu` 파일에 다음 Butane 구성을 생성합니다.

참고

구성 파일에 지정하는 Butane 버전이 OpenShift Container Platform 버전과 일치해야 하며 항상 `0` 으로 끝나야 합니다. 예: `4.20.0`. Butane에 대한 자세한 내용은 “Butane 을 사용하여 머신 구성 생성”을 참조하십시오.

```yaml
variant: openshift
version: 4.20.0
metadata:
  name: 01-worker-interface
  labels:
    machineconfiguration.openshift.io/role: worker
storage:
  files:
    - path: /etc/NetworkManager/conf.d/99-<interface>-mtu.conf
      contents:
        local: <interface>-mtu.conf
      mode: 0600
```

1. 기본 네트워크 인터페이스의 `NetworkManager` 연결 이름을 지정합니다.

2. 이전 단계에서 업데이트된 `NetworkManager` 구성 파일의 로컬 파일 이름을 지정합니다.

다음 명령을 실행하여 Butane 구성에서 `MachineConfig` 오브젝트를 생성합니다.

```shell-session
$ for manifest in control-plane-interface worker-interface; do
    butane --files-dir . $manifest.bu > $manifest.yaml
  done
```

주의

이 절차의 뒷부분에서 명시적으로 지시할 때까지 이러한 머신 구성을 적용하지 마십시오. 이러한 머신 구성을 적용하면 클러스터에 대한 안정성이 손실됩니다.

#### 2.2.4. MTU 마이그레이션 시작

다음 절차에 따라 MTU 마이그레이션을 시작합니다.

프로세스

MTU 마이그레이션을 시작하려면 다음 명령을 입력하여 마이그레이션 구성을 지정합니다. Machine Config Operator는 MTU 변경을 준비하기 위해 클러스터에서 노드를 롤링 재부팅합니다.

```shell-session
$ oc patch Network.operator.openshift.io cluster --type=merge --patch \
  '{"spec": { "migration": { "mtu": { "network": { "from": <overlay_from>, "to": <overlay_to> } , "machine": { "to" : <machine_to> } } } } }'
```

다음과 같습니다.

`<overlay_from>`

현재 클러스터 네트워크 MTU 값을 지정합니다.

`<overlay_to>`

클러스터 네트워크의 대상 MTU를 지정합니다. 이 값은 `<machine_to>` 값을 기준으로 설정됩니다. OVN-Kubernetes의 경우 이 값은 `<machine_to>` 값보다 `100` 미만이어야 합니다.

`<machine_to>`

기본 호스트 네트워크의 기본 네트워크 인터페이스에 대한 MTU를 지정합니다.

```shell-session
$ oc patch Network.operator.openshift.io cluster --type=merge --patch \
  '{"spec": { "migration": { "mtu": { "network": { "from": 1400, "to": 9000 } , "machine": { "to" : 9100} } } } }'
```

Machine Config Operator가 각 머신 구성 풀에서 머신을 업데이트할 때 Operator는 각 노드를 하나씩 재부팅합니다. 모든 노드가 업데이트될 때까지 기다려야 합니다. 다음 명령을 입력하여 머신 구성 풀 상태를 확인합니다.

```shell-session
$ oc get machineconfigpools
```

업데이트된 노드의 상태가 `UPDATED=true`, `UPDATING=false`, `DEGRADED=false` 입니다.

참고

기본적으로 Machine Config Operator는 풀당 한 번에 하나의 머신을 업데이트하여 클러스터 크기에 따라 마이그레이션에 걸리는 총 시간을 늘립니다.

#### 2.2.5. 머신 구성 확인

다음 절차에 따라 머신 구성을 확인합니다.

프로세스

호스트의 새 머신 구성 상태를 확인합니다.

머신 구성 상태 및 적용된 머신 구성 이름을 나열하려면 다음 명령을 입력합니다.

```shell-session
$ oc describe node | egrep "hostname|machineconfig"
```

```plaintext
kubernetes.io/hostname=master-0
machineconfiguration.openshift.io/currentConfig: rendered-master-c53e221d9d24e1c8bb6ee89dd3d8ad7b
machineconfiguration.openshift.io/desiredConfig: rendered-master-c53e221d9d24e1c8bb6ee89dd3d8ad7b
machineconfiguration.openshift.io/reason:
machineconfiguration.openshift.io/state: Done
```

다음 구문이 올바른지 확인합니다.

`machineconfiguration.openshift.io/state` 필드의 값은 `Done` 입니다.

`machineconfiguration.openshift.io/currentConfig` 필드의 값은 `machineconfiguration.openshift.io/desiredConfig` 필드의 값과 동일합니다.

머신 구성이 올바른지 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get machineconfig <config_name> -o yaml | grep ExecStart
```

다음과 같습니다.

`<config_name>`

`machineconfiguration.openshift.io/currentConfig` 필드에서 머신 구성의 이름을 지정합니다.

머신 구성은 다음 업데이트를 systemd 구성에 포함해야 합니다.

```plaintext
ExecStart=/usr/local/bin/mtu-migration.sh
```

#### 2.2.6. 새 하드웨어 MTU 값 적용

새 하드웨어 최대 전송 단위(MTU) 값을 적용하려면 다음 절차를 사용하십시오.

프로세스

기본 네트워크 인터페이스 MTU 값을 업데이트합니다.

NetworkManager 연결 구성을 사용하여 새 MTU를 지정하는 경우 다음 명령을 입력합니다. MachineConfig Operator는 클러스터에서 노드의 롤링 재부팅을 자동으로 수행합니다.

```shell-session
$ for manifest in control-plane-interface worker-interface; do
    oc create -f $manifest.yaml
  done
```

DHCP 서버 옵션 또는 커널 명령줄 및 PXE로 새 MTU를 지정하는 경우 인프라에 필요한 변경을 수행합니다.

Machine Config Operator가 각 머신 구성 풀에서 머신을 업데이트할 때 Operator는 각 노드를 하나씩 재부팅합니다. 모든 노드가 업데이트될 때까지 기다려야 합니다. 다음 명령을 입력하여 머신 구성 풀 상태를 확인합니다.

```shell-session
$ oc get machineconfigpools
```

업데이트된 노드의 상태가 `UPDATED=true`, `UPDATING=false`, `DEGRADED=false` 입니다.

참고

기본적으로 Machine Config Operator는 풀당 한 번에 하나의 머신을 업데이트하여 클러스터 크기에 따라 마이그레이션에 걸리는 총 시간을 늘립니다.

호스트의 새 머신 구성 상태를 확인합니다.

머신 구성 상태 및 적용된 머신 구성 이름을 나열하려면 다음 명령을 입력합니다.

```shell-session
$ oc describe node | egrep "hostname|machineconfig"
```

```plaintext
kubernetes.io/hostname=master-0
machineconfiguration.openshift.io/currentConfig: rendered-master-c53e221d9d24e1c8bb6ee89dd3d8ad7b
machineconfiguration.openshift.io/desiredConfig: rendered-master-c53e221d9d24e1c8bb6ee89dd3d8ad7b
machineconfiguration.openshift.io/reason:
machineconfiguration.openshift.io/state: Done
```

다음 구문이 올바른지 확인합니다.

`machineconfiguration.openshift.io/state` 필드의 값은 `Done` 입니다.

`machineconfiguration.openshift.io/currentConfig` 필드의 값은 `machineconfiguration.openshift.io/desiredConfig` 필드의 값과 동일합니다.

머신 구성이 올바른지 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get machineconfig <config_name> -o yaml | grep path:
```

다음과 같습니다.

`<config_name>`

`machineconfiguration.openshift.io/currentConfig` 필드에서 머신 구성의 이름을 지정합니다.

머신 구성이 성공적으로 배포된 경우 이전 출력에는 `/etc/NetworkManager/conf.d/99-<interface>-mtu.conf` 파일 경로와 `ExecStart=/usr/local/bin/mtu-migration.sh` 행이 포함됩니다.

#### 2.2.7. MTU 마이그레이션 완료

다음 절차를 사용하여 MTU 마이그레이션을 완료합니다.

프로세스

MTU 마이그레이션을 완료하려면 OVN-Kubernetes 네트워크 플러그인에 대해 다음 명령을 입력합니다.

```shell-session
$ oc patch Network.operator.openshift.io cluster --type=merge --patch \
  '{"spec": { "migration": null, "defaultNetwork":{ "ovnKubernetesConfig": { "mtu": <mtu> }}}}'
```

다음과 같습니다.

`<mtu>`

<.

```shell
overlay_to>로 지정한 새 클러스터 네트워크 MTU를 지정합니다
```

MTU 마이그레이션을 완료한 후 각 머신 구성 풀 노드는 하나씩 재부팅됩니다. 모든 노드가 업데이트될 때까지 기다려야 합니다. 다음 명령을 입력하여 머신 구성 풀 상태를 확인합니다.

```shell-session
$ oc get machineconfigpools
```

업데이트된 노드의 상태가 `UPDATED=true`, `UPDATING=false`, `DEGRADED=false` 입니다.

검증

클러스터 네트워크의 현재 MTU를 가져오려면 다음 명령을 입력합니다.

```shell-session
$ oc describe network.config cluster
```

노드의 기본 네트워크 인터페이스에 대한 현재 MTU를 가져옵니다.

클러스터의 노드를 나열하려면 다음 명령을 입력합니다.

```shell-session
$ oc get nodes
```

노드에서 기본 네트워크 인터페이스에 대한 현재 MTU 설정을 가져오려면 다음 명령을 입력합니다.

```shell-session
$ oc adm node-logs <node> -u ovs-configuration | grep configure-ovs.sh | grep mtu | grep <interface> | head -1
```

다음과 같습니다.

`<node>`

이전 단계의 출력에서 노드를 지정합니다.

`<interface>`

노드의 기본 네트워크 인터페이스 이름을 지정합니다.

```plaintext
ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 8051
```

### 2.3. 추가 리소스

PXE 및 ISO 설치를 위한 고급 네트워크 옵션 사용

키 파일 형식으로 NetworkManager 프로필을 수동으로 생성

nmcli를 사용하여 동적 이더넷 연결 구성

## 3장. SCTP(Stream Control Transmission Protocol) 사용

클러스터 관리자는 베어 메탈 클러스터에서 SCTP(Stream Control Transmission Protocol)를 사용할 수 있습니다.

### 3.1. OpenShift Container Platform에서 SCTP 지원

클러스터 관리자는 클러스터의 호스트에서 SCTP를 활성화 할 수 있습니다. RHCOS(Red Hat Enterprise Linux CoreOS)에서 SCTP 모듈은 기본적으로 비활성화되어 있습니다.

SCTP는 IP 네트워크에서 실행되는 안정적인 메시지 기반 프로토콜입니다.

활성화하면 Pod, 서비스, 네트워크 정책에서 SCTP를 프로토콜로 사용할 수 있습니다. `type` 매개변수를 `ClusterIP` 또는 `NodePort` 값으로 설정하여 `Service` 를 정의해야 합니다.

#### 3.1.1. SCTP 프로토콜을 사용하는 구성의 예

`protocol` 매개변수를 포드 또는 서비스 오브젝트의 `SCTP` 값으로 설정하여 SCTP를 사용하도록 포드 또는 서비스를 구성할 수 있습니다.

다음 예에서는 pod가 SCTP를 사용하도록 구성되어 있습니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  namespace: project1
  name: example-pod
spec:
  containers:
    - name: example-pod
...
      ports:
        - containerPort: 30100
          name: sctpserver
          protocol: SCTP
```

다음 예에서는 서비스가 SCTP를 사용하도록 구성되어 있습니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: project1
  name: sctpserver
spec:
...
  ports:
    - name: sctpserver
      protocol: SCTP
      port: 30100
      targetPort: 30100
  type: ClusterIP
```

다음 예에서 `NetworkPolicy` 오브젝트는 특정 레이블이 있는 모든 Pod의 포트 `80` 에서 SCTP 네트워크 트래픽에 적용되도록 구성되어 있습니다.

```yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-sctp-on-http
spec:
  podSelector:
    matchLabels:
      role: web
  ingress:
  - ports:
    - protocol: SCTP
      port: 80
```

### 3.2. SCTP(스트림 제어 전송 프로토콜) 활성화

클러스터 관리자는 클러스터의 작업자 노드에 블랙리스트 SCTP 커널 모듈을 로드하고 활성화할 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

다음 YAML 정의가 포함된 `load-sctp-module.yaml` 파일을 생성합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  name: load-sctp-module
  labels:
    machineconfiguration.openshift.io/role: worker
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /etc/modprobe.d/sctp-blacklist.conf
          mode: 0644
          overwrite: true
          contents:
            source: data:,
        - path: /etc/modules-load.d/sctp-load.conf
          mode: 0644
          overwrite: true
          contents:
            source: data:,sctp
```

`MachineConfig` 오브젝트를 생성하려면 다음 명령을 입력합니다.

```shell-session
$ oc create -f load-sctp-module.yaml
```

선택 사항: MachineConfig Operator가 구성 변경 사항을 적용하는 동안 노드의 상태를 보려면 다음 명령을 입력합니다. 노드 상태가 `Ready` 로 전환되면 구성 업데이트가 적용됩니다.

```shell-session
$ oc get nodes
```

### 3.3. SCTP(Stream Control Transmission Protocol)의 활성화 여부 확인

SCTP 트래픽을 수신하는 애플리케이션으로 pod를 만들고 서비스와 연결한 다음, 노출된 서비스에 연결하여 SCTP가 클러스터에서 작동하는지 확인할 수 있습니다.

사전 요구 사항

클러스터에서 인터넷에 액세스하여 `nc` 패키지를 설치합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

SCTP 리스너를 시작하는 포드를 생성합니다.

다음 YAML로 pod를 정의하는 `sctp-server.yaml` 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sctpserver
  labels:
    app: sctpserver
spec:
  containers:
    - name: sctpserver
      image: registry.access.redhat.com/ubi9/ubi
      command: ["/bin/sh", "-c"]
      args:
        ["dnf install -y nc && sleep inf"]
      ports:
        - containerPort: 30102
          name: sctpserver
          protocol: SCTP
```

다음 명령을 입력하여 pod를 생성합니다.

```shell-session
$ oc create -f sctp-server.yaml
```

SCTP 리스너 pod에 대한 서비스를 생성합니다.

다음 YAML을 사용하여 서비스를 정의하는 `sctp-service.yaml` 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: sctpservice
  labels:
    app: sctpserver
spec:
  type: NodePort
  selector:
    app: sctpserver
  ports:
    - name: sctpserver
      protocol: SCTP
      port: 30102
      targetPort: 30102
```

서비스를 생성하려면 다음 명령을 입력합니다.

```shell-session
$ oc create -f sctp-service.yaml
```

SCTP 클라이언트에 대한 pod를 생성합니다.

다음 YAML을 사용하여 `sctp-client.yaml` 파일을 만듭니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sctpclient
  labels:
    app: sctpclient
spec:
  containers:
    - name: sctpclient
      image: registry.access.redhat.com/ubi9/ubi
      command: ["/bin/sh", "-c"]
      args:
        ["dnf install -y nc && sleep inf"]
```

`Pod` 오브젝트를 생성하려면 다음 명령을 입력합니다.

```shell-session
$ oc apply -f sctp-client.yaml
```

서버에서 SCTP 리스너를 실행합니다.

서버 Pod에 연결하려면 다음 명령을 입력합니다.

```shell-session
$ oc rsh sctpserver
```

SCTP 리스너를 시작하려면 다음 명령을 입력합니다.

```shell-session
$ nc -l 30102 --sctp
```

서버의 SCTP 리스너에 연결합니다.

터미널 프로그램에서 새 터미널 창 또는 탭을 엽니다.

`sctpservice` 서비스의 IP 주소를 얻습니다. 다음 명령을 실행합니다.

```shell-session
$ oc get services sctpservice -o go-template='{{.spec.clusterIP}}{{"\n"}}'
```

클라이언트 Pod에 연결하려면 다음 명령을 입력합니다.

```shell-session
$ oc rsh sctpclient
```

SCTP 클라이언트를 시작하려면 다음 명령을 입력합니다. `<cluster_IP>` 를 `sctpservice` 서비스의 클러스터 IP 주소로 변경합니다.

```shell-session
# nc <cluster_IP> 30102 --sctp
```

## 4장. 보조 인터페이스 지표와 네트워크 연결 연관 짓기

관리자는 `pod_network_info` 지표를 사용하여 보조 네트워크 인터페이스를 분류하고 모니터링할 수 있습니다. 지표는 일반적으로 연결된 `NetworkAttachmentDefinition` 리소스를 기반으로 인터페이스 유형을 식별하는 레이블을 추가하여 이 작업을 수행합니다.

### 4.1. 모니터링을 위한 보조 네트워크 메트릭 확장

보조 장치 또는 인터페이스는 다양한 용도로 사용됩니다. 효과적인 집계 및 모니터링을 허용하려면 보조 네트워크 인터페이스의 지표를 분류해야 합니다.

노출된 지표는 인터페이스를 포함하지만 인터페이스가 시작되는 위치는 지정하지 않습니다. 추가 인터페이스가 없는 경우 이 작업을 수행할 수 있습니다. 그러나 인터페이스 이름에만 의존하는 것은 목적을 식별하고 메트릭을 효과적으로 사용하기 어렵기 때문에 보조 인터페이스를 추가할 때 문제가 됩니다.

보조 인터페이스를 추가할 때 해당 이름은 추가 순서에 따라 달라집니다. 보조 인터페이스는 각각 다른 목적을 제공할 수 있는 별도의 네트워크에 속할 수 있습니다.

`pod_network_name_info` 를 사용하면 인터페이스 유형을 식별하는 추가 정보를 사용하여 현재 지표를 확장할 수 있습니다. 이러한 방식으로 지표를 집계하고 특정 인터페이스 유형에 특정 경보를 추가할 수 있습니다.

네트워크 유형은 `NetworkAttachmentDefinition` 리소스의 이름과 생성되며 서로 다른 보조 네트워크 클래스를 구분합니다. 예를 들어 서로 다른 네트워크에 속하거나 서로 다른 CNI를 사용하는 서로 다른 인터페이스는 서로 다른 네트워크 연결 정의 이름을 사용합니다.

### 4.2. 네트워크 지표 데몬

네트워크 지표 데몬은 네트워크 관련 지표를 수집하고 게시하는 데몬 구성 요소입니다.

kubelet은 이미 관찰 가능한 네트워크 관련 지표를 게시하고 있습니다. 이러한 지표는 다음과 같습니다.

`container_network_receive_bytes_total`

`container_network_receive_errors_total`

`container_network_receive_packets_total`

`container_network_receive_packets_dropped_total`

`container_network_transmit_bytes_total`

`container_network_transmit_errors_total`

`container_network_transmit_packets_total`

`container_network_transmit_packets_dropped_total`

이러한 지표의 레이블에는 다음이 포함됩니다.

포드 이름

포드 네임스페이스

인터페이스 이름(예: `eth0`)

이러한 지표는 예를 들면 Multus 를 통해 Pod에 새 인터페이스를 추가할 때까지는 인터페이스 이름이 무엇을 나타내는지 명확하지 않기 때문에 잘 작동합니다.

인터페이스 레이블은 인터페이스 이름을 나타내지만 해당 인터페이스가 무엇을 의미하는지는 명확하지 않습니다. 인터페이스가 다양한 경우 모니터링 중인 지표에서 어떤 네트워크를 참조하는지 파악하기란 불가능합니다.

이 문제는 다음 섹션에 설명된 새로운 `pod_network_name_info` 를 도입하여 해결됩니다.

### 4.3. 네트워크 이름이 있는 지표

네트워크 지표 데몬 세트에서는 고정 값이 `0` 인 `pod_network_name_info` 게이지 지표를 게시합니다.

```bash
pod_network_name_info{interface="net0",namespace="namespacename",network_name="nadnamespace/firstNAD",pod="podname"} 0
```

네트워크 이름 레이블은 Multus에서 추가한 주석을 사용하여 생성됩니다. 네트워크 연결 정의가 속하는 네임스페이스와 네트워크 연결 정의의 이름입니다.

새 지표 단독으로는 많은 가치를 제공하지 않지만 네트워크 관련 `container_network_*` 지표와 결합되는 경우 보조 네트워크 모니터링을 더 잘 지원합니다.

다음과 같은 `promql` 쿼리를 사용하면 값이 포함된 새 메트릭과 `k8s.v1.cni.cncf.io/network-status` 주석에서 검색된 네트워크 이름을 가져올 수 있습니다.

```bash
(container_network_receive_bytes_total) + on(namespace,pod,interface) group_left(network_name) ( pod_network_name_info )
(container_network_receive_errors_total) + on(namespace,pod,interface) group_left(network_name) ( pod_network_name_info )
(container_network_receive_packets_total) + on(namespace,pod,interface) group_left(network_name) ( pod_network_name_info )
(container_network_receive_packets_dropped_total) + on(namespace,pod,interface) group_left(network_name) ( pod_network_name_info )
(container_network_transmit_bytes_total) + on(namespace,pod,interface) group_left(network_name) ( pod_network_name_info )
(container_network_transmit_errors_total) + on(namespace,pod,interface) group_left(network_name) ( pod_network_name_info )
(container_network_transmit_packets_total) + on(namespace,pod,interface) group_left(network_name) ( pod_network_name_info )
(container_network_transmit_packets_dropped_total) + on(namespace,pod,interface) group_left(network_name)
```

### 5.1. BGP 라우팅 정보

이 기능은 클러스터에 대한 기본 BGP(Border Gateway Protocol) 라우팅 기능을 제공합니다.

중요

MetalLB Operator를 사용하고 MetalLB Operator 이외의 클러스터 관리자 또는 타사 클러스터 구성 요소에서 생성한 `metallb-system` 네임스페이스에 기존 `FRRConfiguration` CR이 있는 경우 해당 CR이 `openshift-frr-k8s` 네임스페이스에 복사되거나 해당 타사 클러스터 구성 요소가 새 네임스페이스를 사용하는지 확인해야 합니다.

자세한 내용은 FRR-K8s 리소스 마이그레이션 을 참조하십시오.

#### 5.1.1. BGP(Border Gateway Protocol) 라우팅 정보

OpenShift Container Platform은 Linux, UNIX 및 유사한 운영 체제용 무료 오픈 소스 인터넷 라우팅 프로토콜 제품군인 FRRouting(FRR)을 통한 BGP 라우팅을 지원합니다. FR-K8s는 Kubernetes 호환 방식으로 FRR API의 하위 집합을 표시하는 Kubernetes 기반 데몬 세트입니다.

클러스터 관리자는 `FRRConfiguration` CR(사용자 정의 리소스)을 사용하여 FRRR 서비스에 액세스할 수 있습니다.

#### 5.1.1.1. 지원되는 플랫폼

BGP 라우팅은 다음 인프라 유형에서 지원됩니다.

베어 메탈

BGP 라우팅을 사용하려면 네트워크 공급자에 대해 BGP를 올바르게 구성해야 합니다. 네트워크 공급자의 중단 또는 잘못된 구성으로 인해 클러스터 네트워크가 중단될 수 있습니다.

#### 5.1.1.2. MetalLB Operator와 함께 사용할 고려 사항

MetalLB Operator는 클러스터에 대한 애드온으로 설치됩니다. MetalLB Operator를 배포하면 추가 라우팅 기능 공급자로 FRR-K8s를 자동으로 활성화하고 이 기능에 의해 설치된 FRR-K8s 데몬을 사용합니다.

4.18로 업그레이드하기 전에 MetalLB Operator(클러스터 관리자 또는 기타 구성 요소에 의해 추가됨)에서 관리하지 않는 `metallb-system` 네임스페이스의 기존 `FRRConfiguration` 을 `openshift-frr-k8s` 네임스페이스에 수동으로 복사하여 필요한 경우 네임스페이스를 생성해야 합니다.

중요

MetalLB Operator를 사용하고 클러스터 관리자 또는 MetalLB Operator 이외의 타사 클러스터 구성 요소가 생성된 `metallb-system` 네임스페이스에 기존 `FRRConfiguration` CR이 있는 경우 다음을 수행해야 합니다.

이러한 기존 `FRRConfiguration` CR이 `openshift-frr-k8s` 네임스페이스에 복사되었는지 확인합니다.

타사 클러스터 구성 요소가 생성한 `FRRConfiguration` CR에 새 네임스페이스를 사용하는지 확인합니다.

#### 5.1.1.3. CNO(Cluster Network Operator) 구성

Cluster Network Operator API는 다음 API 필드를 노출하여 BGP 라우팅을 구성합니다.

`spec.additionalRoutingCapabilities`: 클러스터의 FRR-K8s 데몬 배포를 활성화합니다. 이 데몬은 경로 알림과 독립적으로 사용할 수 있습니다. 활성화되면 FRR-K8s 데몬이 모든 노드에 배포됩니다.

#### 5.1.1.4. BGP 라우팅 사용자 정의 리소스

다음 사용자 정의 리소스는 BGP 라우팅을 구성하는 데 사용됩니다.

`FRRConfiguration`

이 사용자 정의 리소스는 BGP 라우팅에 대한 FRR 구성을 정의합니다. 이 CR은 네임스페이스가 지정됩니다.

#### 5.1.2. FRRConfiguration CRD 구성

다음 섹션에서는 `FRRConfiguration` CR(사용자 정의 리소스)을 사용하는 참조 예제를 제공합니다.

#### 5.1.2.1. 라우터 필드

router 필드를 사용하여 각 VRF(Virtual Routing and Forwarding) 리소스에 대해 여러 라우터를 구성할 수 있습니다. 각 라우터에 대해 Autonomous System Number (ASN)를 정의해야 합니다.

다음 예와 같이 BGP(Border Gateway Protocol) 조합 조합 목록을 정의할 수도 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 4200000000
        ebgpMultiHop: true
        port: 180
      - address: 172.18.0.6
        asn: 4200000000
        port: 179
```

#### 5.1.2.2. toAdvertise 필드

기본적으로 `FRR-K8s` 는 라우터 구성의 일부로 구성된 접두사를 알리지 않습니다. 이를 광고하기 위해, 귀하는 `toAdvertise` 필드를 사용합니다.

다음 예제와 같이 접두사의 하위 집합을 알릴 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 4200000000
        ebgpMultiHop: true
        port: 180
        toAdvertise:
          allowed:
            prefixes:
            - 192.168.2.0/24
      prefixes:
        - 192.168.2.0/24
        - 192.169.2.0/24
```

1. 접두사의 하위 집합을 알립니다.

다음 예제에서는 모든 접두사를 알리는 방법을 보여줍니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 4200000000
        ebgpMultiHop: true
        port: 180
        toAdvertise:
          allowed:
            mode: all
      prefixes:
        - 192.168.2.0/24
        - 192.169.2.0/24
```

1. 모든 접두사를 알립니다.

#### 5.1.2.3. 수신자 필드

기본적으로 `FRR-K8s` 는 인접자가 알리는 접두사를 처리하지 않습니다. `toReceive` 필드를 사용하여 이러한 주소를 처리할 수 있습니다.

다음 예제와 같이 접두사의 하위 집합에 대해 구성할 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.18.0.5
          asn: 64512
          port: 179
          toReceive:
            allowed:
              prefixes:
              - prefix: 192.168.1.0/24
              - prefix: 192.169.2.0/24
                ge: 25
                le: 28
```

1. 2

접두사 길이가 `le` 접두사 길이보다 작거나 같고 접두사 길이보다 크거나 같은 경우 접두사 `가` 적용됩니다.

다음 예제에서는 발표된 모든 접두사를 처리하도록 FRR을 구성합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.18.0.5
          asn: 64512
          port: 179
          toReceive:
            allowed:
              mode: all
```

#### 5.1.2.4. bgp 필드

`bgp` 필드를 사용하여 다양한 `BFD` 프로필을 정의하고 이를 인접지와 연결할 수 있습니다. 다음 예에서 `BFD` 는 `BGP` 세션을 백업하고 `FRR` 은 링크 실패를 감지할 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 64512
        port: 180
        bfdProfile: defaultprofile
    bfdProfiles:
      - name: defaultprofile
```

#### 5.1.2.5. nodeSelector 필드

기본적으로 `FRR-K8s` 는 데몬이 실행 중인 모든 노드에 구성을 적용합니다. `nodeSelector` 필드를 사용하여 구성을 적용할 노드를 지정할 수 있습니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
  nodeSelector:
    labelSelector:
    foo: "bar"
```

#### 5.1.2.6. 인터페이스 필드

`interface` 필드를 사용하여 다음 예제 구성을 사용하여 번호가 지정되지 않은 BGP 피어링을 구성할 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    bfdProfiles:
    - echoMode: false
      name: simple
      passiveMode: false
    routers:
    - asn: 64512
      neighbors:
      - asn: 64512
        bfdProfile: simple
        disableMP: false
        interface: net10
        port: 179
        toAdvertise:
          allowed:
            mode: filtered
            prefixes:
            - 5.5.5.5/32
        toReceive:
          allowed:
            mode: filtered
      prefixes:
      - 5.5.5.5/32
```

1. 번호가 지정되지 않은 BGP 피어링을 활성화합니다.

참고

`interface` 필드를 사용하려면 두 BGP 피어 간에 지점 간 계층 2 연결을 설정해야 합니다. IPv4, IPv6 또는 듀얼 스택과 함께 번호가 지정되지 않은 BGP 피어링을 사용할 수 있지만 IPv6 RAs(Router Advertisements)를 활성화해야 합니다. 각 인터페이스는 하나의 BGP 연결로 제한됩니다.

이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.address` 필드에 값을 지정할 수 없습니다.

`FRRConfiguration` 사용자 정의 리소스의 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `spec.bgp.routers` | `array` | FRR이 구성할 라우터를 지정합니다( VRF당 하나씩). |
| `spec.bgp.routers.asn` | `integer` | 세션의 로컬 종료에 사용할 자동 시스템 번호(ASN)입니다. |
| `spec.bgp.routers.id` | `string` | `bgp` 라우터의 ID를 지정합니다. |
| `spec.bgp.routers.vrf` | `string` | 이 라우터에서 세션을 설정하는 데 사용되는 호스트 vrf를 지정합니다. |
| `spec.bgp.routers.neighbors` | `array` | BGP 세션을 설정하는 포인을 지정합니다. |
| `spec.bgp.routers.neighbors.asn` | `integer` | 세션의 원격 끝에 사용할 ASN을 지정합니다. 이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.dynamicASN` 필드에 값을 지정할 수 없습니다. |
| `spec.bgp.routers.neighbors.dynamicASN` | `string` | 명시적으로 설정하지 않고 세션의 원격 끝에 사용할 ASN을 감지합니다. 동일한 ASN이 있는 인접지의 `내부` 또는 다른 ASN을 가진 인접자의 경우 `외부` 를 지정합니다. 이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.asn` 필드에 값을 지정할 수 없습니다. |
| `spec.bgp.routers.neighbors.address` | `string` | 세션을 설정할 IP 주소를 지정합니다. 이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.interface` 필드에 값을 지정할 수 없습니다. |
| `spec.bgp.routers.neighbors.interface` | `string` | 세션을 설정할 때 사용할 인터페이스 이름을 지정합니다. 이 필드를 사용하여 번호가 지정되지 않은 BGP 피어링을 구성합니다. 두 BGP 피어 간에 지점 간 계층 2 연결이 있어야 합니다. IPv4, IPv6 또는 듀얼 스택과 함께 번호가 지정되지 않은 BGP 피어링을 사용할 수 있지만 IPv6 RAs(Router Advertisements)를 활성화해야 합니다. 각 인터페이스는 하나의 BGP 연결로 제한됩니다. |
| `spec.bgp.routers.neighbors.port` | `integer` | 세션을 설정할 때 사용할 포트를 지정합니다. 기본값은 179입니다. |
| `spec.bgp.routers.neighbors.password` | `string` | BGP 세션을 설정하는 데 사용할 암호를 지정합니다. `password` 와 `PasswordSecret` 은 함께 사용할 수 없습니다. |
| `spec.bgp.routers.neighbors.passwordSecret` | `string` | 피어에 대한 인증 시크릿의 이름을 지정합니다. 시크릿은 "kubernetes.io/basic-auth" 유형이어야 하며 FRR-K8s 데몬과 동일한 네임스페이스에 있어야 합니다. "password" 키는 암호를 시크릿에 저장합니다. `password` 와 `PasswordSecret` 은 함께 사용할 수 없습니다. |
| `spec.bgp.routers.neighbors.holdTime` | `duration` | RFC4271에 따라 요청된 BGP 보류 시간을 지정합니다. 기본값은 180s입니다. |
| `spec.bgp.routers.neighbors.keepaliveTime` | `duration` | RFC4271에 따라 요청된 BGP keepalive 시간을 지정합니다. 기본값은 `60s` 입니다. |
| `spec.bgp.routers.neighbors.connectTime` | `duration` | BGP가 인접한 연결 시도 사이에 대기하는 시간을 지정합니다. |
| `spec.bgp.routers.neighbors.ebgpMultiHop` | `boolean` | BGPPeer가 멀티 홉 떨어져 있는지 여부를 나타냅니다. |
| `spec.bgp.routers.neighbors.bfdProfile` | `string` | BGP 세션과 연결된 BFD 세션에 사용할 BFD 프로필의 이름을 지정합니다. 설정되지 않은 경우 BFD 세션이 설정되지 않습니다. |
| `spec.bgp.routers.neighbors.toAdvertise.allowed` | `array` | 인접지 및 관련 속성에 알리는 접두사 목록을 나타냅니다.Represents the list of prefixes to advertise to a neighbor, and the associated properties. |
| `spec.bgp.routers.neighbors.toAdvertise.allowed.prefixes` | `문자열 배열` | 인접지에게 알리기 위한 접두사 목록을 지정합니다. 이 목록은 라우터에서 정의한 접두사와 일치해야 합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.allowed.mode` | `string` | 접두사를 처리할 때 사용할 모드를 지정합니다. 접두사 목록의 접두사만 허용하도록 `filtered` 로 설정할 수 있습니다. 라우터에 구성된 모든 접두사를 허용하도록 `all` 으로 설정할 수 있습니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withLocalPref` | `array` | 공개된 로컬 기본 설정과 연결된 접두사를 지정합니다. 광고할 수 있도록 허용된 접두사에 로컬 기본 설정과 연결된 접두사를 지정해야 합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withLocalPref.prefixes` | `문자열 배열` | 로컬 기본 설정과 연결된 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withLocalPref.localPref` | `integer` | 접두사와 연결된 로컬 기본 설정을 지정합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withCommunity` | `array` | 공개된 BGP 커뮤니티와 관련된 접두사를 지정합니다. 광고하려는 접두사 목록에 로컬 기본 설정과 연결된 접두사를 포함해야 합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withCommunity.prefixes` | `문자열 배열` | 커뮤니티와 연결된 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withCommunity.community` | `string` | 접두사와 연결된 커뮤니티를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive` | `array` | 인접자로부터 수신할 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive.allowed` | `array` | 인접자로부터 수신하려는 정보를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive.allowed.prefixes` | `array` | 인접지에서 허용되는 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive.allowed.mode` | `string` | 접두사를 처리할 때 사용할 모드를 지정합니다. `filtered` 로 설정하면 `prefixes` 목록의 접두사만 허용됩니다. `all` 로 설정하면 라우터에 구성된 모든 접두사가 허용됩니다. |
| `spec.bgp.routers.neighbors.disableMP` | `boolean` | IPv4 및 IPv6 경로 교환을 별도의 BGP 세션으로 분리하지 못하도록 MP BGP를 비활성화합니다. |
| `spec.bgp.routers.prefixes` | `문자열 배열` | 이 라우터 인스턴스에서 알릴 접두사를 모두 지정합니다. |
| `spec.bgp.bfdProfiles` | `array` | 토론을 구성할 때 사용할 bfd 프로필 목록을 지정합니다. |
| `spec.bgp.bfdProfiles.name` | `string` | 구성의 다른 부분에서 참조할 BFD 프로필의 이름입니다. |
| `spec.bgp.bfdProfiles.receiveInterval` | `integer` | 이 시스템에서 제어 패킷을 수신할 수 있는 최소 간격(밀리초)을 지정합니다. 기본값은 `300ms` 입니다. |
| `spec.bgp.bfdProfiles.transmitInterval` | `integer` | 이 시스템에서 BFD 제어 패킷을 밀리초 단위로 보내는 데 사용할 최소 전송 간격을 지정합니다. 기본값은 `300ms` 입니다. |
| `spec.bgp.bfdProfiles.detectMultiplier` | `integer` | 패킷 손실을 확인하기 위해 감지 수를 구성합니다. 연결 손실 감지 타이머를 확인하려면 원격 전송 간격을 이 값으로 곱합니다. |
| `spec.bgp.bfdProfiles.echoInterval` | `integer` | 이 시스템에서 처리할 수 있는 최소 에코 수신 전송 간격을 밀리초 단위로 구성합니다. 기본값은 `50ms` 입니다. |
| `spec.bgp.bfdProfiles.echoMode` | `boolean` | 에코 전송 모드를 활성화하거나 비활성화합니다. 이 모드는 기본적으로 비활성화되어 있으며 멀티 홉 설정에서 지원되지 않습니다. |
| `spec.bgp.bfdProfiles.passiveMode` | `boolean` | 세션을 패시브로 표시합니다. 수동 세션은 연결을 시작하지 않고 응답을 시작하기 전에 피어의 제어 패킷을 기다립니다. |
| `spec.bgp.bfdProfiles.MinimumTtl` | `integer` | 멀티 홉 세션만 사용할 수 있습니다. 들어오는 BFD 제어 패킷에 대해 예상되는 최소 TTL을 구성합니다. |
| `spec.nodeSelector` | `string` | 이 구성을 적용하려는 노드를 제한합니다. 지정된 경우 라벨이 지정된 선택기와 일치하는 노드만 구성을 적용하려고 합니다. 지정하지 않으면 모든 노드에서 이 구성을 적용하려고 합니다. |
| `status` | `string` | FRRConfiguration의 관찰 상태를 정의합니다. |

#### 5.1.3. 추가 리소스

FRRouting 사용자 가이드: BGP

### 5.2. BGP 라우팅 활성화

클러스터 관리자는 클러스터에 대한 OVN-Kubernetes BGP(Border Gateway Protocol) 라우팅 지원을 활성화할 수 있습니다.

#### 5.2.1. BGP(Border Gateway Protocol) 라우팅 활성화

클러스터 관리자는 베어 메탈 인프라에서 클러스터에 대한 BGP(Border Gateway Protocol) 라우팅 지원을 활성화할 수 있습니다.

MetalLB Operator와 함께 BGP 라우팅을 사용하는 경우 필요한 BGP 라우팅 지원이 자동으로 활성화됩니다. BGP 라우팅 지원을 수동으로 활성화할 필요가 없습니다.

#### 5.2.1.1. BGP 라우팅 지원 활성화

클러스터 관리자는 클러스터에 대한 BGP 라우팅 지원을 활성화할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 로그인되어 있습니다.

클러스터는 호환 가능한 인프라에 설치됩니다.

프로세스

동적 라우팅 공급자를 활성화하려면 다음 명령을 입력합니다.

```shell-session
$ oc patch Network.operator.openshift.io/cluster --type=merge -p '{
  "spec": {
    "additionalRoutingCapabilities": {
      "providers": ["FRR"]
    }
  }
}'
```

### 5.3. BGP 라우팅 비활성화

클러스터 관리자는 클러스터에 대한 OVN-Kubernetes BGP(Border Gateway Protocol) 라우팅 지원을 활성화할 수 있습니다.

#### 5.3.1. BGP(Border Gateway Protocol) 라우팅 비활성화

클러스터 관리자는 베어 메탈 인프라에서 클러스터에 대한 BGP(Border Gateway Protocol) 라우팅 지원을 비활성화할 수 있습니다.

#### 5.3.1.1. BGP 라우팅 지원 활성화

클러스터 관리자는 클러스터에 대한 BGP 라우팅 지원을 비활성화할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 로그인되어 있습니다.

클러스터는 호환 가능한 인프라에 설치됩니다.

프로세스

동적 라우팅을 비활성화하려면 다음 명령을 입력합니다.

```shell-session
$ oc patch Network.operator.openshift.io/cluster --type=merge -p '{
  "spec": { "additionalRoutingCapabilities": null }
}'
```

### 5.4. FRR-K8s 리소스 마이그레이션

OpenShift Container Platform 4.17 및 이전 릴리스의 `metallb-system` 네임스페이스에 있는 모든 사용자가 생성한 FRR-K8s CR(사용자 정의 리소스)은 `openshift-frr-k8s` 네임스페이스로 마이그레이션해야 합니다. 클러스터 관리자는 이 절차의 단계를 완료하여 FRR-K8s 사용자 정의 리소스를 마이그레이션합니다.

#### 5.4.1. FRR-K8s 리소스 마이그레이션

FRR-K8s `FRRConfiguration` 사용자 정의 리소스를 `metallb-system` 네임스페이스에서 `openshift-frr-k8s` 네임스페이스로 마이그레이션할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 로그인되어 있습니다.

프로세스

Metal LB Operator가 배포된 이전 버전의 OpenShift Container Platform에서 업그레이드할 때 사용자 정의 `FRRConfiguration` 구성을 `metallb-system` 네임스페이스에서 `openshift-frr-k8s` 네임스페이스로 수동으로 마이그레이션해야 합니다. 이러한 CR을 이동하려면 다음 명령을 입력합니다.

`openshift-frr-k8s` 네임스페이스를 생성하려면 다음 명령을 입력합니다.

```shell-session
$ oc create namespace openshift-frr-k8s
```

마이그레이션을 자동화하려면 다음 콘텐츠를 사용하여 라는 쉘 스크립트를 생성합니다.

```shell
migrate.sh
```

```bash
#!/bin/bash
OLD_NAMESPACE="metallb-system"
NEW_NAMESPACE="openshift-frr-k8s"
FILTER_OUT="metallb-"
oc get frrconfigurations.frrk8s.metallb.io -n "${OLD_NAMESPACE}" -o json |\
  jq -r '.items[] | select(.metadata.name | test("'"${FILTER_OUT}"'") | not)' |\
  jq -r '.metadata.namespace = "'"${NEW_NAMESPACE}"'"' |\
  oc create -f -
```

마이그레이션을 실행하려면 다음 명령을 실행합니다.

```shell-session
$ bash migrate.sh
```

검증

마이그레이션이 성공했는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get frrconfigurations.frrk8s.metallb.io -n openshift-frr-k8s
```

마이그레이션이 완료되면 `metallb-system` 네임스페이스에서 `FRRConfiguration` 사용자 정의 리소스를 제거할 수 있습니다.

### 6.1. 경로 알림 정보

이 기능은 OVN-Kubernetes 네트워크 플러그인에 대한 경로 알림 기능을 제공합니다. BGP(Border Gateway Router) 공급자가 필요합니다. 자세한 내용은 BGP 라우팅 정보를 참조하십시오.

#### 6.1.1. Border Gateway Protocol을 사용하여 클러스터 네트워크 경로 광고

OVN-Kubernetes 네트워크 플러그인은 라우팅 알림이 활성화된 상태에서 기본 Pod 네트워크 및 CUDN(클러스터 사용자 정의) 네트워크에 대한 네트워크 경로 광고(EgressIPs 포함)를 지원하고 공급자 네트워크에서 기본 pod 네트워크 및 CUDN으로 경로를 가져옵니다.

공급자 네트워크에서 기본 Pod 네트워크 및 CUDN에서 공개된 IP 주소에 직접 연결할 수 있습니다.

예를 들어 기본 Pod 네트워크로 경로를 가져올 수 있으므로 더 이상 각 노드에서 경로를 수동으로 구성할 필요가 없습니다. 이전에는 `routingViaHost` 매개변수를 `true` 로 설정하고 각 노드의 경로를 수동으로 구성하여 유사한 구성에 근접할 수 있었습니다.

경로 알림을 사용하면 `routingViaHost` 매개변수가 `false` 로 설정된 상태에서 이 작업을 원활하게 수행할 수 있습니다.

클러스터의 `Network` 사용자 정의 리소스 CR에서 `routingViaHost` 매개변수를 `true` 로 설정할 수도 있지만 유사한 구성을 시뮬레이션하려면 각 노드의 경로를 수동으로 구성해야 합니다. 경로 알림을 활성화하면 각 노드 하나씩 수동으로 경로를 구성하지 않고도 `Network` CR에 `routingViaHost=false` 를 설정할 수 있습니다.

공급자 네트워크의 경로 리플렉터가 지원되며 대규모 네트워크에서 경로를 알리는 데 필요한 BGP 연결 수를 줄일 수 있습니다.

경로 알림 활성화와 함께 EgressIP를 사용하는 경우 계층 3 공급자 네트워크는 EgressIP 페일오버를 인식합니다. 즉, 다른 계층 2 세그먼트에서 EgressIP를 호스팅하는 클러스터 노드를 찾을 수 있지만 계층 2 공급자 네트워크만 인식하기 전에 모든 송신 노드가 동일한 계층 2 세그먼트에 있어야 했습니다.

#### 6.1.1.1. 지원되는 플랫폼

BGP(Border Gateway Protocol)를 사용하는 광고 경로는 베어 메탈 인프라 유형에서 지원됩니다.

#### 6.1.1.2. 인프라 요구사항

라우팅 알림을 사용하려면 네트워크 인프라에 대해 BGP를 구성해야 합니다. 네트워크 인프라의 중단 또는 잘못된 구성으로 인해 클러스터 네트워크가 중단될 수 있습니다.

#### 6.1.1.3. 다른 네트워킹 기능과의 호환성

경로 알림은 다음 OpenShift Container Platform 네트워킹 기능을 지원합니다.

여러 외부 게이트웨이(MEG)

이 기능에서는 MEG가 지원되지 않습니다.

EgressIPs

EgressIP의 사용 및 알림을 지원합니다. 송신 IP 주소가 있는 노드는 EgressIP를 알립니다. 송신 IP 주소는 송신 노드와 동일한 계층 2 네트워크 서브넷에 있어야 합니다. 다음과 같은 제한 사항이 적용됩니다.

계층 2 모드에서 작동하는 CUDN(사용자 정의 네트워크)의 EgressIP는 지원되지 않습니다.

추가 네트워크 인터페이스에 할당된 송신 IP 주소와 송신 IP 주소가 모두 할당된 네트워크의 EgressIP는 비현실적입니다.

모든 EgressIP는 EgressIP가 할당되는 것과 동일한 인터페이스를 통해 이러한 세션이 설정되는지 여부에 관계없이 선택한 FRRConfiguration 인스턴스의 모든 BGP 세션에 광고되며 이로 인해 원하지 않는 광고가 발생할 수 있습니다.

서비스

MetalLB Operator와 함께 작동하여 공급자 네트워크에 서비스를 알립니다.

송신 서비스

완전 지원.

송신 방화벽

완전 지원.

송신 QoS

완전 지원.

네트워크 정책

완전 지원.

직접 Pod 수신

기본 클러스터 네트워크 및 CUDN(클러스터 사용자 정의) 네트워크에 대한 완전한 지원

#### 6.1.1.4. MetalLB Operator와 함께 사용할 고려 사항

MetalLB Operator는 클러스터에 대한 애드온으로 설치됩니다. MetalLB Operator를 배포하면 FRR-K8s를 추가 라우팅 기능 공급자로 자동으로 활성화합니다. 이 기능과 MetalLB Operator는 동일한 FRR-K8s 배포를 사용합니다.

#### 6.1.1.5. 클러스터 사용자 정의 네트워크 이름 지정 (CUDN) 고려 사항

`FRRConfiguration` CR에서 VRF 장치를 참조할 때 VRF 이름은 15자 미만의 VRF 이름의 CUDN 이름과 동일합니다. VRF 이름을 CUDN 이름에서 유추할 수 있도록 VRF 이름을 15자를 넘지 않는 것이 좋습니다.

#### 6.1.1.6. BGP 라우팅 사용자 정의 리소스

다음 CR(사용자 정의 리소스)은 BGP를 사용하여 경로 알림을 구성하는 데 사용됩니다.

`RouteAdvertisements`

이 CR은 BGP 라우팅에 대한 알림을 정의합니다. 이 CR에서 OVN-Kubernetes 컨트롤러는 클러스터 네트워크 경로를 알리도록 FRR 데몬을 구성하는 `FRRConfiguration` 오브젝트를 생성합니다. 이 CR은 클러스터 범위입니다.

`FRRConfiguration`

이 CR은 BGP 피어를 정의하고 공급자 네트워크에서 클러스터 네트워크로 경로 가져오기를 구성하는 데 사용됩니다. `RouteAdvertisements` 오브젝트를 적용하기 전에 BGP 피어를 구성하기 위해 처음에 하나 이상의 FRRConfiguration 오브젝트를 정의해야 합니다. 이 CR은 네임스페이스가 지정됩니다.

#### 6.1.1.7. FRRConfiguration 오브젝트의 OVN-Kubernetes 컨트롤러 생성

`FRRConfiguration` 오브젝트는 각 노드에 적용되는 적절한 광고 접두사를 사용하여 `RouteAdvertisements` CR에서 선택한 각 네트워크 및 노드에 대해 생성됩니다.

OVN-Kubernetes 컨트롤러는 `RouteAdvertisements` -CR 선택 노드가 `RouteAdvertisements` -CR-selected FRR 구성에서 선택한 노드의 서브 세트인지 확인합니다.

수신할 접두사의 모든 필터링 또는 선택은 `RouteAdvertisement` CR에서 생성된 `FRRConfiguration` 오브젝트에서는 고려되지 않습니다. 다른 `FRRConfiguration` 개체에서 수신하도록 접두사를 구성합니다. OVN-Kubernetes는 VRF에서 적절한 네트워크로 경로를 가져옵니다.

#### 6.1.1.8. CNO(Cluster Network Operator) 구성

CNO(Cluster Network Operator) API는 여러 필드를 노출하여 경로 알림을 구성합니다.

`spec.additionalRoutingCapabilities.providers`: 경로를 알리는 데 필요한 추가 라우팅 공급자를 지정합니다. 지원되는 유일한 값은 `FRR` -K8S 데몬을 클러스터에 배포할 수 있는 FRR입니다. 활성화되면 FRR-K8S 데몬이 모든 노드에 배포됩니다.

`spec.defaultNetwork.ovnKubernetesConfig.routeAdvertisements`: 기본 클러스터 네트워크 및 CUDN 네트워크에 대한 경로 알림을 활성화합니다. 이 기능을 활성화하려면 `spec.additionalRoutingCapabilities` 필드를 `FRR` 로 설정해야 합니다.

#### 6.1.2. RouteAdvertisements 오브젝트 구성

다음 속성을 사용하여 클러스터 범위인 `RouteAdvertisements` 오브젝트를 정의할 수 있습니다.

`RouteAdvertisements` CR(사용자 정의 리소스)의 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | `RouteAdvertisements` 오브젝트의 이름을 지정합니다. |
| `알림` | `array` | 알릴 다양한 유형의 네트워크 목록을 포함할 수 있는 배열을 지정합니다. `"PodNetwork"` 및 `"EgressIP"` 값만 지원합니다. |
| `frrConfigurationSelector` | `object` | OVN-Kubernetes 기반 `FRRConfiguration` CR이 기반으로 하는 `FRRConfiguration` CR을 결정합니다. |
| `networkSelector` | `object` | 기본 클러스터 네트워크 및 클러스터 사용자 정의 네트워크(CUDN)에서 알릴 네트워크를 지정합니다. |
| `nodeSelector` | `object` | 선택한 노드로 알림을 제한합니다. advertisement `="PodNetwork"` 를 선택하면 모든 노드를 선택해야 합니다. advertisement `="EgressIP"` 를 선택하면 선택한 노드에 할당된 송신 IP 주소만 광고됩니다. |
| `targetVRF` | `string` | 에서 경로를 알릴 라우터를 결정합니다. 경로는 선택한 `FRRConfiguration` CR에 지정된 대로 이 가상 라우팅 및 전달(VRF) 대상과 연결된 라우터에서 광고됩니다. 생략하면 기본 VRF가 대상으로 사용됩니다. `auto` 로 지정하면 네트워크 이름과 이름이 같은 VRF가 대상과 사용됩니다. |

#### 6.1.3. BGP를 사용한 Pod IP 주소 광고의 예

다음 예제에서는 BGP(Border Gateway Protocol)를 사용하여 Pod IP 주소 및 EgressIP를 알리기 위한 몇 가지 구성을 설명합니다. 외부 네트워크 테두리 라우터에는 `172.18.0.5` IP 주소가 있습니다. 이러한 구성에서는 클러스터 네트워크의 모든 노드로 경로를 릴레이할 수 있는 외부 경로 리플렉션을 구성했다고 가정합니다.

#### 6.1.3.1. 기본 클러스터 네트워크 알림

이 시나리오에서는 기본 클러스터 네트워크가 외부 네트워크에 노출되므로 Pod IP 주소와 EgressIP가 공급자 네트워크에 광고됩니다.

이 시나리오는 다음 `FRRConfiguration` 오브젝트에 의존합니다.

```yaml
apiVersion: k8s.ovn.org/v1
kind: RouteAdvertisements
metadata:
  name: default
spec:
  advertisements:
  - PodNetwork
  - EgressIP
  networkSelectors:
  - networkSelectionType: DefaultNetwork
  frrConfigurationSelector:
    matchLabels:
      routeAdvertisements: receive-all
  nodeSelector: {}
```

OVN-Kubernetes 컨트롤러에서 이 `RouteAdvertisements` CR을 볼 때 기본 클러스터 네트워크의 경로를 알리기 위해 선택한 FRR 데몬을 기반으로 추가 `FRRConfiguration` 개체를 생성합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: ovnk-generated-abcdef
  namespace: openshift-frr-k8s
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
        - address: 172.18.0.5
          asn: 64512
          toReceive:
            allowed:
              mode: filtered
          toAdvertise:
            allowed:
              prefixes:
              - <default_network_host_subnet>
      prefixes:
      - <default_network_host_subnet>
  nodeSelector:
    matchLabels:
      kubernetes.io/hostname: ovn-worker
```

생성된 `FRRConfiguration` 오브젝트에서 < `default_network_host_subnet` >은 공급자 네트워크에 알리는 기본 클러스터 네트워크의 서브넷입니다.

#### 6.1.3.2. BGP를 통해 클러스터 사용자 정의 네트워크에서 Pod IP 광고

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/524-openshift-bgp-ovn-k8s-no-vpn-0325.png" alt="BGP를 통해 클러스터 사용자 정의 네트워크에서 Pod IP 광고" kind="figure" diagram_type="image_figure"]
BGP를 통해 클러스터 사용자 정의 네트워크에서 Pod IP 광고
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/165d490fe578e346140de7b712caf5c7/524-openshift-bgp-ovn-k8s-no-vpn-0325.png`_


이 시나리오에서는 Blue 클러스터 사용자 정의 네트워크(CUDN)가 외부 네트워크에 노출되므로 네트워크의 Pod IP 주소 및 EgressIP가 공급자 네트워크에 광고됩니다.

이 시나리오는 다음 `FRRConfiguration` 오브젝트에 의존합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: receive-all
  namespace: openshift-frr-k8s
  labels:
    routeAdvertisements: receive-all
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.18.0.5
        asn: 64512
        disableMP: true
        toReceive:
          allowed:
            mode: all
```

이 `FRRConfiguration` 오브젝트를 사용하면 인접한 `172.18.0.5` 에서 기본 VRF로 경로를 가져오고 기본 클러스터 네트워크에서 사용할 수 있습니다.

다음 다이어그램에 설명된 대로 CUDN은 기본 VRF를 통해 광고됩니다.

Red CUDN

`빨간색` 이라는 CUDN과 연결된 `red` VRF라는 VRF

서브넷 `10.0.0.0/24`

Blue CUDN

`blue` 라는 CUDN과 연결된 `blue` 라는 VRF

`10.0.1.0/24` 서브넷

이 구성에서는 별도의 두 개의 CUDN이 정의됩니다. 빨간색 네트워크는 `10.0.0.0/24` 서브넷을 처리하고 blue 네트워크는 `10.0.1.0/24` 서브넷을 다룹니다. 빨간색 및 파란색 네트워크는 `export: true` 로 레이블이 지정됩니다.

다음 `RouteAdvertisements` CR은 빨간색 및 파란색 테넌트에 대한 구성을 설명합니다.

```yaml
apiVersion: k8s.ovn.org/v1
kind: RouteAdvertisements
metadata:
  name: advertise-cudns
spec:
  advertisements:
  - PodNetwork
  - EgressIP
  networkSelectors:
  - networkSelectionType: ClusterUserDefinedNetworks
    clusterUserDefinedNetworkSelector:
      networkSelector:
        matchLabels:
          export: "true"
  frrConfigurationSelector:
    matchLabels:
      routeAdvertisements: receive-all
  nodeSelector: {}
```

OVN-Kubernetes 컨트롤러에서 이 `RouteAdvertisements` CR을 볼 때 해당 경로를 알리기 위해 선택한 FRR 데몬을 기반으로 추가 `FRRConfiguration` 오브젝트를 생성합니다. 다음 예제는 선택된 노드 및 네트워크에 따라 생성된 `FRRConfiguration` 오브젝트 수를 사용하여 이러한 구성 오브젝트 중 하나입니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: ovnk-generated-abcdef
  namespace: openshift-frr-k8s
spec:
  bgp:
    routers:
    - asn: 64512
      vrf: blue
      imports:
      - vrf: default
    - asn: 64512
      neighbors:
        - address: 172.18.0.5
          asn: 64512
          toReceive:
            allowed:
              mode: filtered
          toAdvertise:
            allowed:
              prefixes:
              - 10.0.1.0/24
      prefixes:
      - 10.0.1.0/24
      imports:
      - vrf: blue
  nodeSelector:
    matchLabels:
      kubernetes.io/hostname: ovn-worker
```

생성된 `FRRConfiguration` 오브젝트는 네트워크 blue에 속하는 서브넷 `10.0.1.0/24` 를 구성하여 기본 VRF로 가져오고 `172.18.0.5` 인접자에게 광고합니다.

`FRRConfiguration` 오브젝트는 각 노드에 적용되는 적절한 접두사를 사용하여 `RouteAdvertisements` CR에서 선택한 각 네트워크 및 노드에 대해 생성됩니다.

`targetVRF` 필드를 생략하면 경로가 유출되고 기본 VRF를 통해 광고됩니다. 또한 초기 FRRConfiguration 오브젝트 정의 후 기본 VRF로 가져온 경로도 blue VRF로 가져옵니다.

#### 6.1.3.3. VPN을 사용하여 BGP를 통해 클러스터 사용자 정의 네트워크에서 Pod IP 광고

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/524-openshift-bgp-ovn-k8s-vrf-lite-0325.png" alt="VPN을 사용하여 BGP를 통해 클러스터 사용자 정의 네트워크에서 Pod IP 광고" kind="figure" diagram_type="image_figure"]
VPN을 사용하여 BGP를 통해 클러스터 사용자 정의 네트워크에서 Pod IP 광고
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/bdc0fd4c0dd6cb5bbbd2f1102cb5497d/524-openshift-bgp-ovn-k8s-vrf-lite-0325.png`_


이 시나리오에서는 VLAN 인터페이스가 파란색 네트워크와 연결된 VRF 장치에 연결됩니다. 이 설정은 VRF lite 설계를 제공합니다.

여기서 FRR-K8S는 파란색 네트워크 VRF/VLAN 링크의 해당 BGP 세션을 다음 홉 제공 에지(PE) 라우터에 통해서만 파란색 네트워크를 알리는 데 사용됩니다. 빨간색 테넌트는 동일한 구성을 사용합니다.

파란색 및 빨간색 네트워크는 `export: true` 로 레이블이 지정됩니다.

중요

이 시나리오에서는 EgressIP 사용을 지원하지 않습니다.

다음 다이어그램에서는 이 구성을 보여줍니다.

Red CUDN

`빨간색` 이라는 CUDN과 연결된 `red` VRF라는 VRF

VRF 장치에 연결되어 외부 PE 라우터에 연결된 VLAN 인터페이스

`10.0.2.0/24` 의 할당된 서브넷

Blue CUDN

`blue` 라는 CUDN과 연결된 `blue` 라는 VRF

VRF 장치에 연결되어 외부 PE 라우터에 연결된 VLAN 인터페이스

`10.0.1.0/24` 의 할당된 서브넷

참고

이 방법은 OVN-Kubernetes 네트워크 플러그인의 `ovnKubernetesConfig.gatewayConfig` 사양에 `routingViaHost=true` 를 설정하는 경우에만 사용할 수 있습니다.

다음 구성에서 추가 `FRRConfiguration` CR은 파란색 및 빨간색 VLAN의 PE 라우터로 피어링을 구성합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: vpn-blue-red
  namespace: openshift-frr-k8s
  labels:
    routeAdvertisements: vpn-blue-red
spec:
  bgp:
    routers:
    - asn: 64512
      vrf: blue
      neighbors:
      - address: 182.18.0.5
        asn: 64512
        toReceive:
          allowed:
            mode: filtered
    - asn: 64512
      vrf: red
      neighbors:
      - address: 192.18.0.5
        asn: 64512
        toReceive:
          allowed:
            mode: filtered
```

다음 `RouteAdvertisements` CR은 파란색 및 빨간색 테넌트에 대한 구성을 설명합니다.

```yaml
apiVersion: k8s.ovn.org/v1
kind: RouteAdvertisements
metadata:
  name: advertise-vrf-lite
spec:
  targetVRF: auto
  advertisements:
  - "PodNetwork"
  nodeSelector: {}
  frrConfigurationSelector:
    matchLabels:
      routeAdvertisements: vpn-blue-red
  networkSelectors:
  - networkSelectionType: ClusterUserDefinedNetworks
    clusterUserDefinedNetworkSelector:
      networkSelector:
        matchLabels:
          export: "true"
```

`RouteAdvertisements` CR에서 `targetVRF` 가 `auto` 로 설정되어 선택한 개별 네트워크에 해당하는 VRF 장치 내에서 알림이 발생합니다. 이 시나리오에서는 blue의 Pod 서브넷이 Blue VRF 장치를 통해 알려지고 빨간색의 pod 서브넷은 빨간색 VRF 장치를 통해 광고됩니다.

또한 각 BGP 세션은 초기 `FRRConfiguration` 개체에서 정의한 대로 해당 CUDN VRF로만 경로를 가져옵니다.

OVN-Kubernetes 컨트롤러에서 이 `RouteAdvertisements` CR을 볼 때 파란색 및 빨간색 테넌트의 경로를 알리도록 FRR 데몬을 구성하는 선택된 항목을 기반으로 추가 `FRRConfiguration` 개체를 생성합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: ovnk-generated-abcde
  namespace: openshift-frr-k8s
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 182.18.0.5
        asn: 64512
        toReceive:
          allowed:
            mode: filtered
        toAdvertise:
          allowed:
            prefixes:
            - 10.0.1.0/24
      vrf: blue
      prefixes:
        - 10.0.1.0/24
    - asn: 64512
      neighbors:
      - address: 192.18.0.5
        asn: 64512
        toReceive:
          allowed:
            mode: filtered
        toAdvertise:
          allowed:
            prefixes:
            - 10.0.2.0/24
      vrf: red
      prefixes:
         - 10.0.2.0/24
  nodeSelector:
     matchLabels:
        kubernetes.io/hostname: ovn-worker
```

이 시나리오에서는 피어링 관계를 정의하는 `FRRConfiguration` CR에서 수신할 경로 필터링 또는 선택을 수행해야 합니다.

#### 6.1.4. 추가 리소스

FRRConfiguration CRD 구성

격리된 VRF 네트워크 내에서 서비스 시작

FRRouting 사용자 가이드: BGP

### 6.2. 경로 알림 활성화

클러스터 관리자는 클러스터에 대한 추가 경로 알림을 구성할 수 있습니다. OVN-Kubernetes 네트워크 플러그인을 사용해야 합니다.

#### 6.2.1. 경로 알림 활성화

클러스터 관리자는 클러스터에 대한 추가 라우팅 지원을 활성화할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 로그인되어 있습니다.

클러스터는 호환 가능한 인프라에 설치됩니다.

프로세스

라우팅 공급자 및 추가 경로 알림을 활성화하려면 다음 명령을 입력합니다.

```shell-session
$ oc patch Network.operator.openshift.io cluster --type=merge \
  -p='{
    "spec": {
      "additionalRoutingCapabilities": {
        "providers": ["FRR"]
        },
        "defaultNetwork": {
          "ovnKubernetesConfig": {
            "routeAdvertisements": "Enabled"
    }}}}'
```

### 6.3. 경로 알림 비활성화

클러스터 관리자는 클러스터에 대한 추가 경로 알림을 비활성화할 수 있습니다.

#### 6.3.1. 경로 알림 비활성화

클러스터 관리자는 클러스터에 대한 추가 경로 알림을 비활성화할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 로그인되어 있습니다.

클러스터는 호환 가능한 인프라에 설치됩니다.

프로세스

추가 라우팅 지원을 비활성화하려면 다음 명령을 입력합니다.

```shell-session
$ oc patch network.operator cluster -p '{
  "spec": {
    "defaultNetwork": {
      "ovnKubernetesConfig": {
        "routeAdvertisements": "Disabled"
      }
    }
  }
}'
```

### 6.4. 경로 알림 설정 예

클러스터 관리자는 클러스터에 대한 다음 예제 경로 알림 설정을 구성할 수 있습니다. 이 구성은 경로 알림을 구성하는 방법을 보여주는 샘플로 사용됩니다.

#### 6.4.1. 샘플 경로 알림 설정

클러스터 관리자는 클러스터에 대한 BGP(Border Gateway Protocol) 라우팅 지원을 활성화할 수 있습니다. 이 구성은 경로 알림을 구성하는 방법을 보여주는 샘플로 사용됩니다. 구성은 전체 메시 설정이 아닌 경로 리플렉션을 사용합니다.

참고

BGP 라우팅은 베어 메탈 인프라에서만 지원됩니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 클러스터에 로그인합니다.

클러스터는 베어 메탈 인프라에 설치됩니다.

FRR 데몬 컨테이너를 실행하려는 클러스터에 액세스할 수 있는 베어 메탈 시스템이 있어야 합니다.

프로세스

다음 명령을 실행하여 `RouteAdvertisements` 기능 게이트가 활성화되어 있는지 확인합니다.

```shell-session
$ oc get featuregate -oyaml | grep -i routeadvertisement
```

```yaml
- name: RouteAdvertisements
```

다음 명령을 실행하여 CNO(Cluster Network Operator)를 구성합니다.

```shell-session
$ oc patch Network.operator.openshift.io cluster --type=merge \
  -p='
    {"spec":{
      "additionalRoutingCapabilities": {
        "providers": ["FRR"]},
        "defaultNetwork":{"ovnKubernetesConfig"{
          "routeAdvertisements":"Enabled"
          }}}}'
```

CNO가 모든 노드를 다시 시작하는 데 몇 분이 걸릴 수 있습니다.

다음 명령을 실행하여 노드의 IP 주소를 가져옵니다.

```shell-session
$ oc get node -owide
```

```plaintext
NAME                                       STATUS   ROLES                  AGE   VERSION   INTERNAL-IP      EXTERNAL-IP   OS-IMAGE                                                KERNEL-VERSION                 CONTAINER-RUNTIME
master-0                                   Ready    control-plane,master   27h   v1.31.3   192.168.111.20   <none>        Red Hat Enterprise Linux CoreOS 418.94.202501062026-0   5.14.0-427.50.1.el9_4.x86_64   cri-o://1.31.4-2.rhaos4.18.git33d7598.el9
master-1                                   Ready    control-plane,master   27h   v1.31.3   192.168.111.21   <none>        Red Hat Enterprise Linux CoreOS 418.94.202501062026-0   5.14.0-427.50.1.el9_4.x86_64   cri-o://1.31.4-2.rhaos4.18.git33d7598.el9
master-2                                   Ready    control-plane,master   27h   v1.31.3   192.168.111.22   <none>        Red Hat Enterprise Linux CoreOS 418.94.202501062026-0   5.14.0-427.50.1.el9_4.x86_64   cri-o://1.31.4-2.rhaos4.18.git33d7598.el9
worker-0                                   Ready    worker                 27h   v1.31.3   192.168.111.23   <none>        Red Hat Enterprise Linux CoreOS 418.94.202501062026-0   5.14.0-427.50.1.el9_4.x86_64   cri-o://1.31.4-2.rhaos4.18.git33d7598.el9
worker-1                                   Ready    worker                 27h   v1.31.3   192.168.111.24   <none>        Red Hat Enterprise Linux CoreOS 418.94.202501062026-0   5.14.0-427.50.1.el9_4.x86_64   cri-o://1.31.4-2.rhaos4.18.git33d7598.el9
worker-2                                   Ready    worker                 27h   v1.31.3   192.168.111.25   <none>        Red Hat Enterprise Linux CoreOS 418.94.202501062026-0   5.14.0-427.50.1.el9_4.x86_64   cri-o://1.31.4-2.rhaos4.18.git33d7598.el9
```

다음 명령을 실행하여 각 노드의 기본 Pod 네트워크를 가져옵니다.

```shell-session
$ oc get node <node_name> -o=jsonpath={.metadata.annotations.k8s\\.ovn\\.org/node-subnets}
```

```plaintext
{"default":["10.129.0.0/23"],"ns1.udn-network-primary-layer3":["10.150.6.0/24"]}
```

베어 메탈 하이퍼바이저에서 다음 명령을 실행하여 사용할 외부 FRR 컨테이너의 IP 주소를 가져옵니다.

```shell-session
$ ip -j -d route get <a cluster node's IP> | jq -r '.[] | .dev' | xargs ip -d -j address show | jq -r '.[] | .addr_info[0].local'
```

다음 예와 같이 각 노드의 IP 주소를 포함하는 FRR용 `frr.conf` 파일을 만듭니다.

```plaintext
router bgp 64512
 no bgp default ipv4-unicast
 no bgp default ipv6-unicast
 no bgp network import-check
 neighbor 192.168.111.20 remote-as 64512
 neighbor 192.168.111.20 route-reflector-client
 neighbor 192.168.111.21 remote-as 64512
 neighbor 192.168.111.21 route-reflector-client
 neighbor 192.168.111.22 remote-as 64512
 neighbor 192.168.111.22 route-reflector-client
 neighbor 192.168.111.40 remote-as 64512
 neighbor 192.168.111.40 route-reflector-client
 neighbor 192.168.111.47 remote-as 64512
 neighbor 192.168.111.47 route-reflector-client
 neighbor 192.168.111.23 remote-as 64512
 neighbor 192.168.111.23 route-reflector-client
 neighbor 192.168.111.24 remote-as 64512
 neighbor 192.168.111.24 route-reflector-client
 neighbor 192.168.111.25 remote-as 64512
 neighbor 192.168.111.25 route-reflector-client
 address-family ipv4 unicast
  network 192.168.1.0/24
  network 192.169.1.1/32
 exit-address-family
 address-family ipv4 unicast
  neighbor 192.168.111.20 activate
  neighbor 192.168.111.20 next-hop-self
  neighbor 192.168.111.21 activate
  neighbor 192.168.111.21 next-hop-self
  neighbor 192.168.111.22 activate
  neighbor 192.168.111.22 next-hop-self
  neighbor 192.168.111.40 activate
  neighbor 192.168.111.40 next-hop-self
  neighbor 192.168.111.47 activate
  neighbor 192.168.111.47 next-hop-self
  neighbor 192.168.111.23 activate
  neighbor 192.168.111.23 next-hop-self
  neighbor 192.168.111.24 activate
  neighbor 192.168.111.24 next-hop-self
  neighbor 192.168.111.25 activate
  neighbor 192.168.111.25 next-hop-self
 exit-address-family
 neighbor  remote-as 64512
 neighbor  route-reflector-client
 address-family ipv6 unicast
  network 2001:db8::/128
 exit-address-family
 address-family ipv6 unicast
  neighbor  activate
  neighbor  next-hop-self
 exit-address-family
```

다음 콘텐츠가 포함된 `데몬` 이라는 파일을 생성합니다.

```plaintext
# This file tells the frr package which daemons to start.
#
# Sample configurations for these daemons can be found in
# /usr/share/doc/frr/examples/.
#
# ATTENTION:
#
# When activating a daemon for the first time, a config file, even if it is
# empty, has to be present *and* be owned by the user and group "frr", else
# the daemon will not be started by /etc/init.d/frr. The permissions should
# be u=rw,g=r,o=.
# When using "vtysh" such a config file is also needed. It should be owned by
# group "frrvty" and set to ug=rw,o= though. Check /etc/pam.d/frr, too.
#
# The watchfrr and zebra daemons are always started.
#
bgpd=yes
ospfd=no
ospf6d=no
ripd=no
ripngd=no
isisd=no
pimd=no
ldpd=no
nhrpd=no
eigrpd=no
babeld=no
sharpd=no
pbrd=no
bfdd=yes
fabricd=no
vrrpd=no

#
# If this option is set the /etc/init.d/frr script automatically loads
# the config via "vtysh -b" when the servers are started.
# Check /etc/pam.d/frr if you intend to use "vtysh"!
#
vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
bgpd_options="   -A 127.0.0.1"
ospfd_options="  -A 127.0.0.1"
ospf6d_options=" -A ::1"
ripd_options="   -A 127.0.0.1"
ripngd_options=" -A ::1"
isisd_options="  -A 127.0.0.1"
pimd_options="   -A 127.0.0.1"
ldpd_options="   -A 127.0.0.1"
nhrpd_options="  -A 127.0.0.1"
eigrpd_options=" -A 127.0.0.1"
babeld_options=" -A 127.0.0.1"
sharpd_options=" -A 127.0.0.1"
pbrd_options="   -A 127.0.0.1"
staticd_options="-A 127.0.0.1"
bfdd_options="   -A 127.0.0.1"
fabricd_options="-A 127.0.0.1"
vrrpd_options="  -A 127.0.0.1"

# configuration profile
#
#frr_profile="traditional"
#frr_profile="datacenter"

#
# This is the maximum number of FD's that will be available.
# Upon startup this is read by the control files and ulimit
# is called. Uncomment and use a reasonable value for your
# setup if you are expecting a large number of peers in
# say BGP.
#MAX_FDS=1024

# The list of daemons to watch is automatically generated by the init script.
#watchfrr_options=""

# for debugging purposes, you can specify a "wrap" command to start instead
# of starting the daemon directly, e.g. to use valgrind on ospfd:
#   ospfd_wrap="/usr/bin/valgrind"
# or you can use "all_wrap" for all daemons, e.g. to use perf record:
#   all_wrap="/usr/bin/perf record --call-graph -"
# the normal daemon command is added to this at the end.
```

`frr.conf` 와 `데몬` 파일을 모두 동일한 디렉토리에 저장합니다(예: `/tmp/frr`).

다음 명령을 실행하여 외부 FRR 컨테이너를 생성합니다.

```shell-session
$ sudo podman run -d --privileged --network host --rm --ulimit core=-1 --name frr --volume /tmp/frr:/etc/frr quay.io/frrouting/frr:9.1.0
```

다음 `FRRConfiguration` 및 `RouteAdvertisements` 구성을 생성합니다.

다음 콘텐츠를 포함하는 `receive_all.yaml` 파일을 생성합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: receive-all
  namespace: openshift-frr-k8s
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 192.168.111.1
        asn: 64512
        toReceive:
          allowed:
            mode: all
```

다음 콘텐츠가 포함된 `ra.yaml` 파일을 생성합니다.

```yaml
apiVersion: k8s.ovn.org/v1
kind: RouteAdvertisements
metadata:
  name: default
spec:
  nodeSelector: {}
  frrConfigurationSelector: {}
  networkSelectors:
  - networkSelectionType: DefaultNetwork
  advertisements:
  - "PodNetwork"
  - "EgressIP"
```

다음 명령을 실행하여 `receive_all.yaml` 및 `ra.yaml` 파일을 적용합니다.

```shell-session
$ for f in receive_all.yaml ra.yaml; do oc apply -f $f; done
```

검증

구성이 적용되었는지 확인합니다.

다음 명령을 실행하여 `FRRConfiguration` 구성이 생성되었는지 확인합니다.

```shell-session
$ oc get frrconfiguration -A
```

```plaintext
NAMESPACE           NAME                   AGE
openshift-frr-k8s   ovnk-generated-6lmfb   4h47m
openshift-frr-k8s   ovnk-generated-bhmnm   4h47m
openshift-frr-k8s   ovnk-generated-d2rf5   4h47m
openshift-frr-k8s   ovnk-generated-f958l   4h47m
openshift-frr-k8s   ovnk-generated-gmsmw   4h47m
openshift-frr-k8s   ovnk-generated-kmnqg   4h47m
openshift-frr-k8s   ovnk-generated-wpvgb   4h47m
openshift-frr-k8s   ovnk-generated-xq7v6   4h47m
openshift-frr-k8s   receive-all            4h47m
```

다음 명령을 실행하여 `RouteAdvertisements` 구성이 생성되었는지 확인합니다.

```shell-session
$ oc get ra -A
```

```plaintext
NAME      STATUS
default   Accepted
```

다음 명령을 실행하여 외부 FRR 컨테이너 ID를 가져옵니다.

```shell-session
$ sudo podman ps | grep frr
```

```plaintext
22cfc713890e  quay.io/frrouting/frr:9.1.0              /usr/lib/frr/dock...  5 hours ago   Up 5 hours ago               frr
```

이전 단계에서 얻은 컨테이너 ID를 사용하여 외부 FRR 컨테이너의 `vtysh` 세션의 BGP 주변 및 경로를 확인합니다. 다음 명령을 실행합니다.

```shell-session
$ sudo podman exec -it <container_id> vtysh -c "show ip bgp"
```

```plaintext
BGP table version is 10, local router ID is 192.168.111.1, vrf id 0
Default local pref 100, local AS 64512
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *>i10.128.0.0/23    192.168.111.22           0    100      0 i
 *>i10.128.2.0/23    192.168.111.23           0    100      0 i
 *>i10.129.0.0/23    192.168.111.20           0    100      0 i
 *>i10.129.2.0/23    192.168.111.24           0    100      0 i
 *>i10.130.0.0/23    192.168.111.21           0    100      0 i
 *>i10.130.2.0/23    192.168.111.40           0    100      0 i
 *>i10.131.0.0/23    192.168.111.25           0    100      0 i
 *>i10.131.2.0/23    192.168.111.47           0    100      0 i
 *> 192.168.1.0/24   0.0.0.0                  0         32768 i
 *> 192.169.1.1/32   0.0.0.0                  0         32768 i
```

다음 명령을 실행하여 각 클러스터 노드에 대해 `frr-k8s` Pod를 찾습니다.

```shell-session
$ oc -n openshift-frr-k8s get pod -owide
```

```plaintext
NAME                                      READY   STATUS    RESTARTS   AGE   IP               NODE                                       NOMINATED NODE   READINESS GATES
frr-k8s-86wmq                             6/6     Running   0          25h   192.168.111.20   master-0                                   <none>           <none>
frr-k8s-h2wl6                             6/6     Running   0          25h   192.168.111.21   master-1                                   <none>           <none>
frr-k8s-jlbgs                             6/6     Running   0          25h   192.168.111.40   node1.example.com   <none>           <none>
frr-k8s-qc6l5                             6/6     Running   0          25h   192.168.111.25   worker-2                                   <none>           <none>
frr-k8s-qtxdc                             6/6     Running   0          25h   192.168.111.47   node2.example.com   <none>           <none>
frr-k8s-s5bxh                             6/6     Running   0          25h   192.168.111.24   worker-1                                   <none>           <none>
frr-k8s-szgj9                             6/6     Running   0          25h   192.168.111.22   master-2                                   <none>           <none>
frr-k8s-webhook-server-6cd8b8d769-kmctw   1/1     Running   0          25h   10.131.2.9       node3.example.com   <none>           <none>
frr-k8s-zwmgh                             6/6     Running   0          25h   192.168.111.23   worker-0                                   <none>           <none>
```

OpenShift Container Platform 클러스터에서 다음 명령을 실행하여 FRR 컨테이너의 클러스터 노드의 `frr-k8s` Pod에서 BGP 경로를 확인합니다.

```shell-session
$ oc -n openshift-frr-k8s -c frr rsh frr-k8s-86wmq
```

다음 명령을 실행하여 클러스터 노드의 IP 경로를 확인합니다.

```shell-session
sh-5.1# vtysh
```

```plaintext
Hello, this is FRRouting (version 8.5.3).
Copyright 1996-2005 Kunihiro Ishiguro, et al.
```

다음 명령을 실행하여 IP 경로를 확인합니다.

```shell-session
worker-2# show ip bgp
```

```plaintext
BGP table version is 10, local router ID is 192.168.111.25, vrf id 0
Default local pref 100, local AS 64512
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *>i10.128.0.0/23    192.168.111.22           0    100      0 i
 *>i10.128.2.0/23    192.168.111.23           0    100      0 i
 *>i10.129.0.0/23    192.168.111.20           0    100      0 i
 *>i10.129.2.0/23    192.168.111.24           0    100      0 i
 *>i10.130.0.0/23    192.168.111.21           0    100      0 i
 *>i10.130.2.0/23    192.168.111.40           0    100      0 i
 *> 10.131.0.0/23    0.0.0.0                  0         32768 i
 *>i10.131.2.0/23    192.168.111.47           0    100      0 i
 *>i192.168.1.0/24   192.168.111.1            0    100      0 i
 *>i192.169.1.1/32   192.168.111.1            0    100      0 i

Displayed  10 routes and 10 total paths
```

OpenShift Container Platform 클러스터에서 다음 명령을 실행하여 노드를 디버깅합니다.

```shell-session
$ oc debug node/<node_name>
```

```plaintext
Temporary namespace openshift-debug-lbtgh is created for debugging node...
Starting pod/worker-2-debug-zrg4v ...
To use host binaries, run `chroot /host`
Pod IP: 192.168.111.25
If you don't see a command prompt, try pressing enter.
```

다음 명령을 실행하여 BGP 경로가 광고되고 있는지 확인합니다.

```shell-session
sh-5.1# ip route show | grep bgp
```

```plaintext
10.128.0.0/23 nhid 268 via 192.168.111.22 dev br-ex proto bgp metric 20
10.128.2.0/23 nhid 259 via 192.168.111.23 dev br-ex proto bgp metric 20
10.129.0.0/23 nhid 260 via 192.168.111.20 dev br-ex proto bgp metric 20
10.129.2.0/23 nhid 261 via 192.168.111.24 dev br-ex proto bgp metric 20
10.130.0.0/23 nhid 266 via 192.168.111.21 dev br-ex proto bgp metric 20
10.130.2.0/23 nhid 262 via 192.168.111.40 dev br-ex proto bgp metric 20
10.131.2.0/23 nhid 263 via 192.168.111.47 dev br-ex proto bgp metric 20
192.168.1.0/24 nhid 264 via 192.168.111.1 dev br-ex proto bgp metric 20
192.169.1.1 nhid 264 via 192.168.111.1 dev br-ex proto bgp metric 20
```

### 7.1. OpenShift 클러스터 노드의 PTP 정보

PTP(Precision Time Protocol)는 네트워크의 클럭을 동기화하는 데 사용됩니다. 하드웨어 지원과 함께 사용할 경우 PTP는 마이크로초 미만의 정확성을 수행할 수 있으며 NTP(Network Time Protocol)보다 더 정확합니다.

중요

PTP가 있는 `openshift-sdn` 클러스터에서 하드웨어 타임스탬프에 UDP(User Datagram Protocol)를 사용하고 OVN-Kubernetes 플러그인으로 마이그레이션하는 경우 OVS(Open vSwitch) 브리지와 같은 기본 인터페이스 장치에 하드웨어 타임스탬프를 적용할 수 없습니다.

결과적으로 UDP 버전 4 구성은 `br-ex` 인터페이스에서 작동할 수 없습니다.

OpenShift Container Platform 클러스터 노드에서 `linuxptp` 서비스를 구성하고 PTP 가능 하드웨어를 사용할 수 있습니다.

PTP Operator를 배포하여 OpenShift Container Platform 웹 콘솔 또는 CLI(OpenShift CLI)를 사용하여 PTP를 설치합니다. PTP Operator는 `linuxptp` 서비스를 생성 및 관리하고 다음 기능을 제공합니다.

```shell
oc
```

클러스터에서 PTP 가능 장치 검색.

`linuxptp` 서비스의 구성 관리.

PTP Operator `cloud-event-proxy` 사이드카를 사용하여 애플리케이션의 성능 및 안정성에 부정적인 영향을 주는 PTP 클록 이벤트 알림

참고

PTP Operator는 베어 메탈 인프라에서만 프로비저닝된 클러스터에서 PTP 가능 장치와 함께 작동합니다.

#### 7.1.1. PTP 도메인의 요소

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/319_OpenShift_PTP_bare-metal_OCP_nodes_1123_PTP_network.png" alt="PTP 할 마스터 클록을 보여주는 다이어그램" kind="diagram" diagram_type="semantic_diagram"]
PTP 할 마스터 클록을 보여주는 다이어그램
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/856d5ea9436ee3f775fb0dffb913534f/319_OpenShift_PTP_bare-metal_OCP_nodes_1123_PTP_network.png`_


PTP는 네트워크에 연결된 여러 노드를 각 노드의 클럭과 동기화하는 데 사용됩니다. PTP에 의해 동기화된 클록은 리더 후속 계층 구조로 구성됩니다. 계층 구조는 모든 클럭에서 실행되는 최상의 마스터 클럭(BMC) 알고리즘에 의해 자동으로 생성되고 업데이트됩니다. 후속 클럭은 리더 클록과 동기화되며 후속 클럭은 다른 다운스트림 클록의 소스가 될 수 있습니다.

그림 7.1. 네트워크의 PTP 노드

다음은 3가지 기본 PTP 클록 유형에 대해 설명합니다.

GRandmaster 클록

마스터 클록은 네트워크의 다른 클록에 표준 시간 정보를 제공하며 정확하고 안정적인 동기화를 보장합니다. 타임스탬프를 작성하고 다른 클록의 시간 요청에 응답합니다.

Grandmaster 클럭은 GNSS(Global Navigation Satellite System) 시간 소스와 동기화됩니다. Grandmaster 클록은 네트워크에서 신뢰할 수 있는 시간 소스이며 다른 모든 장치에 시간 동기화를 제공할 책임이 있습니다.

경계 클록

경계 클록에는 두 개 이상의 통신 경로에 포트가 있으며, 동시에 소스와 다른 대상 클록의 대상일 수 있습니다. 경계 클록은 대상 클록으로 작동합니다.

대상 클럭이 타이밍 메시지를 수신하고 지연을 조정한 다음 네트워크를 전달하기 위한 새 소스 시간 신호를 생성합니다. 경계 클록은 소스 클록과 정확하게 동기화되는 새로운 타이밍 패킷을 생성하며 소스 클럭에 직접 보고하는 연결된 장치의 수를 줄일 수 있습니다.

일반 클록

일반 클록에는 네트워크의 위치에 따라 소스 또는 대상 클록의 역할을 수행할 수 있는 단일 포트가 연결되어 있습니다. 일반 클록은 타임스탬프를 읽고 쓸 수 있습니다.

#### 7.1.1.1. NTP를 통한 PTP의 이점

PTP가 NTP를 능가하는 주요 이점 중 하나는 다양한 NIC(네트워크 인터페이스 컨트롤러) 및 네트워크 스위치에 있는 하드웨어 지원입니다. 특수 하드웨어를 사용하면 PTP가 메시지 전송 지연을 고려하여 시간 동기화의 정확성을 향상시킬 수 있습니다.

최대한의 정확성을 달성하려면 PTP 클록 사이의 모든 네트워킹 구성 요소를 PTP 하드웨어를 사용하도록 설정하는 것이 좋습니다.

NIC는 전송 및 수신 즉시 PTP 패킷을 타임스탬프할 수 있으므로 하드웨어 기반 PTP는 최적의 정확성을 제공합니다. 이를 운영 체제에서 PTP 패킷을 추가로 처리해야 하는 소프트웨어 기반 PTP와 비교합니다.

중요

PTP를 활성화하기 전에 필수 노드에 대해 NTP가 비활성화되어 있는지 확인합니다. `MachineConfig` 사용자 정의 리소스를 사용하여 chrony 타임 서비스 (`chronyd`)를 비활성화할 수 있습니다. 자세한 내용은 chrony 타임 서비스 비활성화를 참조하십시오.

#### 7.1.2. OpenShift Container Platform 노드에서 linuxptp 및 gpsd 개요

OpenShift Container Platform은 높은 정밀 네트워크 동기화를 위해 `linuxptp` 및 `gpsd` 패키지와 함께 PTP Operator를 사용합니다. `linuxptp` 패키지는 네트워크에서 PTP 타이밍을 위한 툴과 데몬을 제공합니다.

GNSS(Global Navigation Satellite System)가 있는 클러스터 호스트는 `gpsd` 를 사용하여 GNSS 클럭 소스와 상호 작용할 수 있습니다.

`linuxptp` 패키지에는 시스템 클럭 동기화를 위한 `ts2phc`, `pmc`, `ptp4l`, `phc2sys` 프로그램이 포함되어 있습니다.

ts2phc

`ts2phc` 는 PTP 장치에서 PTP 하드웨어 클럭(PHC)을 높은 수준의 정확성으로 동기화합니다. `ts2phc` 는 마스터 클록 구성에 사용됩니다.

정확한 타이밍은 GNSS(Global Navigation Satellite System)와 같은 높은 정확도의 클럭 소스를 신호로 수신합니다. GNSS는 대규모 분산 네트워크에서 사용하기 위해 정확하고 신뢰할 수 있는 동기화 시간 소스를 제공합니다.

GNSS 클록은 일반적으로 몇 나노초의 정확도로 시간 정보를 제공합니다.

`ts2phc` 시스템 데몬은 할드마스터 클록에서 시간 정보를 읽고 CryostatC 형식으로 변환하여 네트워크의 다른 PTP 장치로 타이밍 정보를 보냅니다. CryostatC 시간은 네트워크의 다른 장치에서 시계를 마스터 클록과 동기화하는 데 사용됩니다.

pmc

`PMC` 는 IEEE 표준 1588.1588에 따라 PTP 관리 클라이언트(`pmc`)를 구현합니다. `PMC` 는 `ptp4l` 시스템 데몬에 대한 기본 관리 액세스를 제공합니다. `PMC` 는 표준 입력에서 읽고 선택한 전송을 통해 출력을 전송하여 수신하는 응답을 출력합니다.

ptp4l

`ptp4l` 은 PTP 경계 클록과 일반 클록을 구현하고 시스템 데몬으로 실행됩니다. `ptp4l` 은 다음을 수행합니다.

하드웨어 타임스탬프를 사용하여 소스 클록과 synchronizes the source clock with hardware time stamping

소프트웨어 타임스탬프를 사용하여 시스템 클록을 소스 클록에 동기화

phc2sys

`phc2sys` 는 네트워크 인터페이스 컨트롤러(NIC)의 CryostatC에 시스템 시계를 동기화합니다. `phc2sys` 시스템 데몬은 타이밍 정보를 지속적으로 모니터링합니다. 타이밍 오류를 감지하면 CryostatC가 시스템 시계를 수정합니다.

`gpsd` 패키지에는 호스트 클럭과 GNSS 클럭 동기화를 위한 `ubxtool`, `gspipe`, `gpsd` 프로그램이 포함되어 있습니다.

ubxtool

`ubxtool` CLI를 사용하면 u-blox GPS 시스템과 통신할 수 있습니다. `ubxtool` CLI는 u-blox 바이너리 프로토콜을 사용하여 GPS와 통신합니다.

gpspipe

`gpspipe` 는 `gpsd` 출력에 연결하여 `stdout` 에 파이프합니다.

gpsd

`GPS` D는 호스트에 연결된 하나 이상의 GPS 또는 AIS 수신기를 모니터링하는 서비스 데몬입니다.

#### 7.1.3. PTP 할 마스터 클록에 대한 GNSS 타이밍 개요

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/319_OpenShift_PTP_bare-metal_OCP_nodes_1023_PTP.png" alt="GNSS 및 T-GM 시스템 아키텍처" kind="diagram" diagram_type="semantic_diagram"]
GNSS 및 T-GM 시스템 아키텍처
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/093c31cf4bb480146b063570d4cbb976/319_OpenShift_PTP_bare-metal_OCP_nodes_1023_PTP.png`_


OpenShift Container Platform은 클러스터에서 GNSS(Global Navigation Satellite System) 소스 및 마스터 클록(T-GM)에서 정확한 PTP 타이밍을 수신할 수 있습니다.

중요

OpenShift Container Platform은 Intel E810 Westport 채널 NIC가 있는 GNSS 소스의 PTP 타이밍만 지원합니다.

그림 7.2. GNSS 및 T-GM과의 동기화 개요

GNSS(Global navigation Satellite System)

GNSS는 전 세계 수신기에 위치 지정, 탐색 및 타이밍 정보를 제공하는 데 사용되는 Satellite 기반 시스템입니다. PTP에서 GNSS 수신기는 종종 매우 정확하고 안정적인 참조 클록 소스로 사용됩니다.

이러한 수신기는 여러 GNSS Satellite에서 신호를 수신하므로 정확한 시간 정보를 계산할 수 있습니다. GNSS에서 얻은 타이밍 정보는 PTP 할 마스터 클록에 의해 참조로 사용됩니다.

GNSS를 참조로 사용하면 PTP 네트워크의 마스터 클록은 다른 장치에 매우 정확한 타임스탬프를 제공하여 전체 네트워크에서 정확한 동기화를 가능하게 할 수 있습니다.

Digital Phase-Locked Cryostat (DPLL)

DPLL은 네트워크의 다양한 PTP 노드 간에 클럭 동기화를 제공합니다. DPLL은 로컬 시스템 클럭 신호의 단계를 들어오는 동기화 신호의 단계와 비교합니다(예: PTP 할 마스터 클록에서 PTP 메시지). DPLL은 로컬 클럭과 참조 클록 사이의 단계 차이를 최소화하기 위해 현지 클록 빈도 및 단계를 지속적으로 조정합니다.

#### 7.1.3.1. GNSS 동기화 PTP grandmaster 클록에서 윤초 이벤트 처리

윤초는 국제 Atomic Time(TAI)과 동기화된 유지를 위해 UTC(Coordinated Universal Time)에 때때로 적용되는 1초 조정입니다. UTC 윤초는 예측할 수 없습니다.

국제적으로 합의된 윤초는 leap-seconds.list 에 나열됩니다. 이 파일은 IERS(International Earth Rotation and Reference Systems Service)에 의해 정기적으로 업데이트됩니다.

처리되지 않은 윤초는 훨씬 엣지 RAN 네트워크에 상당한 영향을 미칠 수 있습니다. 이를 통해 far edge RAN 애플리케이션이 즉시 음성 통화 및 데이터 세션의 연결을 끊을 수 있습니다.

#### 7.1.4. PTP 및 클럭 동기화 오류 이벤트 정보

vRAN(가상 RAN)과 같은 클라우드 네이티브 애플리케이션에서는 전체 네트워크의 작동에 중요한 하드웨어 타이밍 이벤트에 대한 알림에 액세스해야 합니다. PTP 클럭 동기화 오류는 대기 시간이 짧은 애플리케이션의 성능 및 안정성에 부정적인 영향을 미칠 수 있습니다(예: 분산 장치(DU)에서 실행되는 vRAN 애플리케이션).

PTP 동기화 손실은 RAN 네트워크에 심각한 오류입니다. 노드에서 동기화가 손실된 경우 라디오가 종료될 수 있으며 네트워크 Over the Air (OTA) 트래픽이 무선 네트워크의 다른 노드로 이동될 수 있습니다.

클러스터 노드에서 PTP 클럭 동기화 상태를 DU에서 실행 중인 vRAN 애플리케이션에 통신할 수 있도록 함으로써 이벤트 알림이 워크로드 오류와 비교하여 완화됩니다.

이벤트 알림은 동일한 DU 노드에서 실행되는 vRAN 애플리케이션에서 사용할 수 있습니다. 게시/서브스크립션 REST API는 이벤트 알림을 메시징 버스에 전달합니다. 게시/서브스크립션 메시징 또는 pub-sub 메시징은 주제에 게시된 모든 메시지가 주제에 대한 모든 구독자에 의해 즉시 수신되는 비동기 서비스 간 통신 아키텍처입니다.

PTP Operator는 모든 PTP 가능 네트워크 인터페이스에 대한 빠른 이벤트 알림을 생성합니다. 소비자 애플리케이션은 PTP 이벤트 REST API v2를 사용하여 PTP 이벤트를 구독할 수 있습니다.

참고

PTP 빠른 이벤트 알림은 PTP 일반 클럭, PTP 할 마스터 클록 또는 PTP 경계 클록을 사용하도록 구성된 네트워크 인터페이스에 사용할 수 있습니다.

#### 7.1.5. 2 카드 E810 NIC 구성 참조

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/openshift-ptp-using-dual-nic-ptp.png" alt="GNSS 타이밍 소스 및 다운스트림 PTP 경계 및 일반 클럭에 연결된 듀얼 NIC PTP 마스터 클럭" kind="diagram" diagram_type="semantic_diagram"]
GNSS 타이밍 소스 및 다운스트림 PTP 경계 및 일반 클럭에 연결된 듀얼 NIC PTP 마스터 클럭
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/9dfce0e5e2968f44f7f3960f26791673/openshift-ptp-using-dual-nic-ptp.png`_


OpenShift Container Platform은 T-GM (T-GM) 및 경계 클럭 (T-BC)의 PTP 타이밍을 위해 단일 및 듀얼 NIC Intel E810 하드웨어를 지원합니다.

듀얼 NIC 할드 마스터 클록

듀얼 NIC 하드웨어가 있는 클러스터 호스트를 PTP 할 마스터 클록으로 사용할 수 있습니다. 하나의 NIC는 글로벌 탐색 Satellite 시스템(GNSS)에서 타이밍 정보를 수신합니다.

두 번째 NIC는 E810 NIC faceplate에서 SMA1 Tx/Rx 연결을 사용하여 첫 번째 NIC에서 타이밍 정보를 수신합니다. 클러스터 호스트의 시스템 클럭은 GNSS satellite에 연결된 NIC에서 동기화됩니다.

듀얼 NIC 할 마스터 클록은 RRU(Remote radio Unit) 및 BBU(Baseband Unit)가 동일한 라디오 셀 사이트에 있는 분산 RAN(D-RAN) 구성의 기능입니다. D-RAN은 여러 사이트에 라디오 기능을 배포하고 이를 코어 네트워크에 백홀 연결로 연결합니다.

그림 7.3. 듀얼 NIC 할드 마스터 클록

참고

듀얼 NIC T-GM 구성에서 단일 `ts2phc` 프로그램은 각 NIC에 대해 하나씩 두 개의 PTP 하드웨어 클럭(PHC)에서 작동합니다.

듀얼 NIC 경계 클록

중반 대역(VDU)을 제공하는 5G 통신 네트워크의 경우 각 가상 분산 장치(vDU)는 6개의 무선 장치(RU)에 대한 연결이 필요합니다. 이러한 연결을 위해 각 vDU 호스트에는 경계 클록으로 구성된 두 개의 NIC가 필요합니다.

듀얼 NIC 하드웨어를 사용하면 각 NIC가 다운스트림 클록에 대해 별도의 `ptp4l` 인스턴스를 사용하여 각 NIC를 동일한 업스트림 리더 클록에 연결할 수 있습니다.

듀얼 NIC 경계 클럭을 사용하는 고가용성 시스템 클럭

Intel E810-XXVDA4 Salem 채널 듀얼 NIC 하드웨어를 고가용성 시스템 클록에 대한 타이밍을 제공하는 듀얼 PTP 경계 클록으로 구성할 수 있습니다. 이 구성은 다른 NIC에 여러 시간 소스가 있는 경우 유용합니다. 고가용성을 통해 두 타이밍 소스 중 하나가 손실되거나 연결이 끊어진 경우 노드가 타이밍 동기화를 손실하지 않습니다.

각 NIC는 동일한 업스트림 리더 클록에 연결됩니다. 고가용성 경계 클록은 여러 PTP 도메인을 사용하여 대상 시스템 클록과 동기화합니다.

T-BC를 고가용성으로 사용할 수 있는 경우 NIC CryostatC 클럭을 동기화하는 하나 이상의 `ptp4l` 인스턴스가 실패하더라도 호스트 시스템 클럭이 올바른 오프셋을 유지할 수 있습니다. 단일 SFP 포트 또는 케이블 오류가 발생하면 경계 클록은 리더 클록과 동기화됩니다.

경계 클럭 리더 소스 선택은 A-BMCA 알고리즘을 사용하여 수행됩니다. 자세한 내용은 ITU-T 권장 사항 G.8275.1 을 참조하십시오.

#### 7.1.6. 듀얼 포트 NIC를 사용하여 PTP 일반 클록의 중복 개선

OpenShift Container Platform은 PTP 타이밍에 대한 일반 클록으로 단일 포트 NIC(네트워크 인터페이스 카드)를 지원합니다. 중복성을 개선하기 위해 하나의 포트를 active로 사용하고 다른 하나는 대기 상태로 듀얼 포트 NIC를 구성할 수 있습니다.

중요

이중 포트 NIC 중복을 사용하는 일반 클록으로 linuxptp 서비스를 구성하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다.

따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

이 구성에서 듀얼 포트 NIC의 포트는 다음과 같이 작동합니다.

활성 포트는 `다음` 포트 상태에서 일반 클록으로 작동합니다.

대기 포트는 `Listening` 포트 상태에 남아 있습니다.

활성 포트가 실패하면 대기 포트가 활성 상태로 전환되어 계속 PTP 타이밍 동기화를 보장합니다.

두 포트 모두 결함이 발생하면 클럭 상태가 `HOLDOVER` 상태로 이동하면 리더 클록으로 다시 동기화되기 전에 holdover 제한 시간이 만료될 때 free `RUN` 상태가 됩니다.

#### 7.1.6.1. 하드웨어 요구 사항

x86_64 또는 AArch64 아키텍처 노드에 중복성을 추가하여 PTP 일반 클록을 구성할 수 있습니다.

x86_64 아키텍처 노드의 경우 노드는 PTP를 지원하고 Intel E810과 같은 NIC당 단일 PTP 하드웨어 클럭(PHC)을 노출하는 듀얼 포트 NIC를 제공해야 합니다.

AArch64 아키텍처 노드의 경우 다음 듀얼 포트 NIC만 사용할 수 있습니다.

NVIDIA ConnectX-7 시리즈

NIC 모드에서 NVIDIA BlueField-3 시리즈

인터페이스를 중복성이 향상된 일반 클록으로 구성하기 전에 NIC 모드에서 NVIDIA BlueField-3 시리즈 DPU를 구성해야 합니다.

NIC 모드 구성에 대한 자세한 내용은 BlueField-3 (NVIDIA 문서), BlueField Management (NVIDIA 문서) 및 Host BIOS HII UEFI 메뉴 (NVIDIA 문서)에서 BlueField-3의 NIC 모드 구성 을 참조하십시오.

NIC 모드로 변경한 후 카드를 다시 시작해야 합니다. 카드를 다시 시작하는 방법에 대한 자세한 내용은 NVIDIA BlueField Reset and Reboot Procedures (NVIDIA 문서)를 참조하십시오.

지원되는 최신 NVIDIA 드라이버 및 펌웨어를 사용하여 적절한 PTP 지원을 보장하고 NIC당 단일 CryostatC를 노출합니다.

#### 7.1.7. 3-card Intel E810 PTP grandmaster 클록

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/openshift-ptp-3-card-grandmaster.png" alt="GNSS 타이밍 소스 및 다운스트림 PTP 경계 및 일반 클럭에 연결된 3- 카드 PTP 할 마스터 클럭" kind="figure" diagram_type="image_figure"]
GNSS 타이밍 소스 및 다운스트림 PTP 경계 및 일반 클럭에 연결된 3- 카드 PTP 할 마스터 클럭
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/6e29e49f2a41893e66c8cab5ddbbc16e/openshift-ptp-3-card-grandmaster.png`_


OpenShift Container Platform은 Intel E810 NIC가 PTP grandmaster 클럭(T-GM)인 클러스터 호스트를 지원합니다.

3 카드 할드 마스터 클록

NIC가 3개인 클러스터 호스트를 PTP 할 마스터 클록으로 사용할 수 있습니다. 하나의 NIC는 글로벌 탐색 Satellite 시스템(GNSS)에서 타이밍 정보를 수신합니다.

두 번째 및 세 번째 NIC는 E810 NIC faceplate에서 SMA1 Tx/Rx 연결을 사용하여 첫 번째 NIC에서 타이밍 정보를 수신합니다. 클러스터 호스트의 시스템 클럭은 GNSS satellite에 연결된 NIC에서 동기화됩니다.

3- 카드 NIC 할 마스터 클록은 분산 RAN (D-RAN) 구성에 사용할 수 있습니다. 여기서 radio Unit (RU)는 프론트 haul 스위치없이 분산 장치 (DU)에 직접 연결되어 있습니다. 예를 들어 RU와 DU가 동일한 라디오 셀 사이트에 있는 경우입니다. D-RAN은 여러 사이트에 라디오 기능을 배포하고 이를 코어 네트워크에 백홀 연결로 연결합니다.

그림 7.4. 3-card Intel E810 PTP grandmaster 클록

참고

3 카드 T-GM 구성에서 단일 `ts2phc` 프로세스는 시스템의 3 `ts2phc` 인스턴스로 보고합니다.

### 7.2. PTP 장치 구성

PTP Operator는 `NodePtpDevice.ptp.openshift.io` CRD(custom resource definition)를 OpenShift Container Platform에 추가합니다.

설치 시 PTP Operator는 각 노드에서 PTP(Precision Time Protocol) 가능 네트워크 장치를 클러스터에서 검색합니다. Operator는 호환되는 PTP 가능 네트워크 장치를 제공하는 각 노드에 대해 `NodePtpDevice` CR(사용자 정의 리소스) 오브젝트를 생성하고 업데이트합니다.

기본 제공 PTP 기능이 있는 NIC(네트워크 인터페이스 컨트롤러) 하드웨어에는 장치별 구성이 필요한 경우가 있습니다. `PtpConfig` CR(사용자 정의 리소스)에서 플러그인을 구성하여 PTP Operator에서 지원되는 하드웨어에 하드웨어별 NIC 기능을 사용할 수 있습니다.

`linuxptp-daemon` 서비스는 `plugin` 스탠자에서 named 매개 변수를 사용하여 특정 하드웨어 구성에 따라 `linuxptp` 프로세스 `ptp4l` 및 `phc2sys` 를 시작합니다.

중요

OpenShift Container Platform 4.20에서 Intel E810 NIC는 `PtpConfig` 플러그인에서 지원됩니다.

#### 7.2.1. CLI를 사용하여 PTP Operator 설치

클러스터 관리자는 CLI를 사용하여 Operator를 설치할 수 있습니다.

사전 요구 사항

PTP를 지원하는 하드웨어가 있는 노드로 베어 메탈 하드웨어에 설치된 클러스터

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

PTP Operator의 네임스페이스를 생성합니다.

다음 YAML을 `ptp-namespace.yaml` 파일에 저장합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-ptp
  annotations:
    workload.openshift.io/allowed: management
  labels:
    name: openshift-ptp
    openshift.io/cluster-monitoring: "true"
```

`Namespace` CR을 생성합니다.

```shell-session
$ oc create -f ptp-namespace.yaml
```

PTP Operator에 대한 Operator 그룹을 생성합니다.

다음 YAML을 `ptp-operatorgroup.yaml` 파일에 저장합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: ptp-operators
  namespace: openshift-ptp
spec:
  targetNamespaces:
  - openshift-ptp
```

`OperatorGroup` CR을 생성합니다.

```shell-session
$ oc create -f ptp-operatorgroup.yaml
```

PTP Operator에 등록합니다.

다음 YAML을 `ptp-sub.yaml` 파일에 저장합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: ptp-operator-subscription
  namespace: openshift-ptp
spec:
  channel: "stable"
  name: ptp-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

`Subscription` CR을 생성합니다.

```shell-session
$ oc create -f ptp-sub.yaml
```

Operator가 설치되었는지 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get csv -n openshift-ptp -o custom-columns=Name:.metadata.name,Phase:.status.phase
```

```shell-session
Name                         Phase
4.20.0-202301261535          Succeeded
```

#### 7.2.2. 웹 콘솔을 사용하여 PTP Operator 설치

클러스터 관리자는 웹 콘솔을 사용하여 PTP Operator를 설치할 수 있습니다.

참고

이전 섹션에서 언급한 것처럼 네임스페이스 및 Operator group을 생성해야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔을 사용하여 PTP Operator를 설치합니다.

OpenShift Container Platform 웹 콘솔에서 에코시스템 → 소프트웨어 카탈로그 를 클릭합니다.

사용 가능한 Operator 목록에서 PTP Operator 를 선택한 다음 설치 를 클릭합니다.

Operator 설치 페이지의 클러스터의 특정 네임스페이스 에서 openshift-ptp 를 선택합니다. 그런 다음, 설치 를 클릭합니다.

선택 사항: PTP Operator가 설치되었는지 확인합니다.

에코시스템 → 설치된 Operator 페이지로 전환합니다.

PTP Operator 가 openshift-ptp 프로젝트에 InstallSucceeded

상태 로 나열되어 있는지 확인합니다.

참고

설치 중에 Operator는 실패 상태를 표시할 수 있습니다. 나중에 InstallSucceeded 메시지와 함께 설치에 성공하면 이 실패 메시지를 무시할 수 있습니다.

Operator가 설치된 것으로 나타나지 않으면 다음과 같이 추가 문제 해결을 수행합니다.

에코시스템 → 설치된 Operator 페이지로 이동하여 Operator 서브스크립션 및 설치 계획 탭의 상태에 장애 또는 오류가 있는지 검사합니다.

Workloads → Pod 페이지로 이동하여 `openshift-ptp` 프로젝트에서 Pod 로그를 확인합니다.

#### 7.2.3. 클러스터에서 PTP 가능 네트워크 장치 검색

클러스터에 존재하는 PTP 가능 네트워크 장치를 식별하여 구성할 수 있습니다.

전제 조건

PTP Operator를 설치했습니다.

프로세스

클러스터에서 PTP 가능 네트워크 장치의 전체 목록을 반환하려면 다음 명령을 실행합니다.

```shell-session
$ oc get NodePtpDevice -n openshift-ptp -o yaml
```

```shell-session
apiVersion: v1
items:
- apiVersion: ptp.openshift.io/v1
  kind: NodePtpDevice
  metadata:
    creationTimestamp: "2022-01-27T15:16:28Z"
    generation: 1
    name: dev-worker-0
    namespace: openshift-ptp
    resourceVersion: "6538103"
    uid: d42fc9ad-bcbf-4590-b6d8-b676c642781a
  spec: {}
  status:
    devices:
    - name: eno1
    - name: eno2
    - name: eno3
    - name: eno4
    - name: enp5s0f0
    - name: enp5s0f1
...
```

1. `name` 매개변수의 값은 상위 노드의 이름과 동일합니다.

2. `장치` 컬렉션에는 PTP Operator가 노드에 대해 검색하는 PTP 가능 장치 목록이 포함되어 있습니다.

#### 7.2.4. linuxptp 서비스를 할 마스터 클록으로 구성

호스트 NIC를 구성하는 `PtpConfig` CR(사용자 정의 리소스)을 생성하여 `linuxptp` 서비스(`ptp4l`, `phc2sys`, `ts2phc`)를 마스터 클록(T-GM)으로 구성할 수 있습니다.

`ts2phc` 유틸리티를 사용하면 시스템 시계를 PTP 할 마스터 클록과 동기화하여 노드가 PTP 일반 클럭 및 경계 클록으로 정밀한 클럭을 스트리밍할 수 있습니다.

참고

다음 예제 `PtpConfig` CR을 기반으로 하여 Intel Westport Channel E810-XXVDA4T 네트워크 인터페이스의 `linuxptp` 서비스를 T-GM으로 구성합니다.

PTP 빠른 이벤트를 구성하려면 `ptp4lOpts`, `ptp4lConf` 및 `ptpClockThreshold` 에 적절한 값을 설정합니다. `ptpClockThreshold` 는 이벤트가 활성화된 경우에만 사용됩니다. 자세한 내용은 " PTP 빠른 이벤트 알림 게시자 구성"을 참조하십시오.

사전 요구 사항

프로덕션 환경의 T-GM 클록의 경우 베어 메탈 클러스터 호스트에 Intel E810 Westport 채널 NIC를 설치합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

`PtpConfig` CR을 생성합니다. 예를 들면 다음과 같습니다.

요구 사항에 따라 배포에 다음 T-GM 구성 중 하나를 사용하십시오. YAML을 `grandmaster-clock-ptp-config.yaml` 파일에 저장합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: grandmaster
  namespace: openshift-ptp
  annotations: {}
spec:
  profile:
    - name: "grandmaster"
      ptp4lOpts: "-2 --summary_interval -4"
      phc2sysOpts: -r -u 0 -m -N 8 -R 16 -s $iface_master -n 24
      ptpSchedulingPolicy: SCHED_FIFO
      ptpSchedulingPriority: 10
      ptpSettings:
        logReduce: "true"
      plugins:
        e810:
          enableDefaultConfig: false
          settings:
            LocalMaxHoldoverOffSet: 1500
            LocalHoldoverTimeout: 14400
            MaxInSpecOffset: 1500
          pins: $e810_pins
          #  "$iface_master":
          #    "U.FL2": "0 2"
          #    "U.FL1": "0 1"
          #    "SMA2": "0 2"
          #    "SMA1": "0 1"
          ublxCmds:
            - args: #ubxtool -P 29.20 -z CFG-HW-ANT_CFG_VOLTCTRL,1
                - "-P"
                - "29.20"
                - "-z"
                - "CFG-HW-ANT_CFG_VOLTCTRL,1"
              reportOutput: false
            - args: #ubxtool -P 29.20 -e GPS
                - "-P"
                - "29.20"
                - "-e"
                - "GPS"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d Galileo
                - "-P"
                - "29.20"
                - "-d"
                - "Galileo"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d GLONASS
                - "-P"
                - "29.20"
                - "-d"
                - "GLONASS"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d BeiDou
                - "-P"
                - "29.20"
                - "-d"
                - "BeiDou"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d SBAS
                - "-P"
                - "29.20"
                - "-d"
                - "SBAS"
              reportOutput: false
            - args: #ubxtool -P 29.20 -t -w 5 -v 1 -e SURVEYIN,600,50000
                - "-P"
                - "29.20"
                - "-t"
                - "-w"
                - "5"
                - "-v"
                - "1"
                - "-e"
                - "SURVEYIN,600,50000"
              reportOutput: true
            - args: #ubxtool -P 29.20 -p MON-HW
                - "-P"
                - "29.20"
                - "-p"
                - "MON-HW"
              reportOutput: true
            - args: #ubxtool -P 29.20 -p CFG-MSG,1,38,248
                - "-P"
                - "29.20"
                - "-p"
                - "CFG-MSG,1,38,248"
              reportOutput: true
      ts2phcOpts: " "
      ts2phcConf: |
        [nmea]
        ts2phc.master 1
        [global]
        use_syslog  0
        verbose 1
        logging_level 7
        ts2phc.pulsewidth 100000000
        #cat /dev/GNSS to find available serial port
        #example value of gnss_serialport is /dev/ttyGNSS_1700_0
        ts2phc.nmea_serialport $gnss_serialport
        [$iface_master]
        ts2phc.extts_polarity rising
        ts2phc.extts_correction 0
      ptp4lConf: |
        [$iface_master]
        masterOnly 1
        [$iface_master_1]
        masterOnly 1
        [$iface_master_2]
        masterOnly 1
        [$iface_master_3]
        masterOnly 1
        [global]
        #
        # Default Data Set
        #
        twoStepFlag 1
        priority1 128
        priority2 128
        domainNumber 24
        #utc_offset 37
        clockClass 6
        clockAccuracy 0x27
        offsetScaledLogVariance 0xFFFF
        free_running 0
        freq_est_interval 1
        dscp_event 0
        dscp_general 0
        dataset_comparison G.8275.x
        G.8275.defaultDS.localPriority 128
        #
        # Port Data Set
        #
        logAnnounceInterval -3
        logSyncInterval -4
        logMinDelayReqInterval -4
        logMinPdelayReqInterval 0
        announceReceiptTimeout 3
        syncReceiptTimeout 0
        delayAsymmetry 0
        fault_reset_interval -4
        neighborPropDelayThresh 20000000
        masterOnly 0
        G.8275.portDS.localPriority 128
        #
        # Run time options
        #
        assume_two_step 0
        logging_level 6
        path_trace_enabled 0
        follow_up_info 0
        hybrid_e2e 0
        inhibit_multicast_service 0
        net_sync_monitor 0
        tc_spanning_tree 0
        tx_timestamp_timeout 50
        unicast_listen 0
        unicast_master_table 0
        unicast_req_duration 3600
        use_syslog 1
        verbose 0
        summary_interval -4
        kernel_leap 1
        check_fup_sync 0
        clock_class_threshold 7
        #
        # Servo Options
        #
        pi_proportional_const 0.0
        pi_integral_const 0.0
        pi_proportional_scale 0.0
        pi_proportional_exponent -0.3
        pi_proportional_norm_max 0.7
        pi_integral_scale 0.0
        pi_integral_exponent 0.4
        pi_integral_norm_max 0.3
        step_threshold 2.0
        first_step_threshold 0.00002
        clock_servo pi
        sanity_freq_limit  200000000
        ntpshm_segment 0
        #
        # Transport options
        #
        transportSpecific 0x0
        ptp_dst_mac 01:1B:19:00:00:00
        p2p_dst_mac 01:80:C2:00:00:0E
        udp_ttl 1
        udp6_scope 0x0E
        uds_address /var/run/ptp4l
        #
        # Default interface options
        #
        clock_type BC
        network_transport L2
        delay_mechanism E2E
        time_stamping hardware
        tsproc_mode filter
        delay_filter moving_median
        delay_filter_length 10
        egressLatency 0
        ingressLatency 0
        boundary_clock_jbod 0
        #
        # Clock description
        #
        productDescription ;;
        revisionData ;;
        manufacturerIdentity 00:00:00
        userDescription ;
        timeSource 0x20
  recommend:
    - profile: "grandmaster"
      priority: 4
      match:
        - nodeLabel: "node-role.kubernetes.io/$mcp"
```

참고

E810 Westport Channel NIC의 경우 `ts2phc.nmea_serialport` 값을 `/dev/gnss0` 로 설정합니다.

다음 명령을 실행하여 CR을 생성합니다.

```shell-session
$ oc create -f grandmaster-clock-ptp-config.yaml
```

검증

`PtpConfig` 프로필이 노드에 적용되었는지 확인합니다.

다음 명령을 실행하여 `openshift-ptp` 네임스페이스에서 Pod 목록을 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                          READY   STATUS    RESTARTS   AGE     IP             NODE
linuxptp-daemon-74m2g         3/3     Running   3          4d15h   10.16.230.7    compute-1.example.com
ptp-operator-5f4f48d7c-x7zkf  1/1     Running   1          4d15h   10.128.1.145   compute-1.example.com
```

프로필이 올바른지 확인합니다. `PtpConfig` 프로필에 지정한 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다. 다음 명령을 실행합니다.

```shell-session
$ oc logs linuxptp-daemon-74m2g -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
ts2phc[94980.334]: [ts2phc.0.config] nmea delay: 98690975 ns
ts2phc[94980.334]: [ts2phc.0.config] ens3f0 extts index 0 at 1676577329.999999999 corr 0 src 1676577330.901342528 diff -1
ts2phc[94980.334]: [ts2phc.0.config] ens3f0 master offset         -1 s2 freq      -1
ts2phc[94980.441]: [ts2phc.0.config] nmea sentence: GNRMC,195453.00,A,4233.24427,N,07126.64420,W,0.008,,160223,,,A,V
phc2sys[94980.450]: [ptp4l.0.config] CLOCK_REALTIME phc offset       943 s2 freq  -89604 delay    504
phc2sys[94980.512]: [ptp4l.0.config] CLOCK_REALTIME phc offset      1000 s2 freq  -89264 delay    474
```

#### 7.2.4.1. linuxptp 서비스를 2 E810 NIC의 할마스터 클록으로 구성

NIC를 구성하는 `PtpConfig` CR(사용자 정의 리소스)을 2 E810 NIC의 grandmaster 클럭(T-GM)으로 `linuxptp` 서비스(`ptp4l`, `phc2sys`, `ts2phc`)를 구성할 수 있습니다.

다음 E810 NIC의 경우 `linuxptp` 서비스를 T-GM으로 구성할 수 있습니다.

Intel E810-XXVDA4T Westport 채널 NIC

Intel E810-CQDA2T Logan Beach NIC

분산 RAN(D-RAN) 사용 사례의 경우 다음과 같이 2개의 NIC에 대해 PTP를 구성할 수 있습니다.

NIC 1은 GNSS(Global navigation satellite System) 시간 소스와 동기화됩니다.

NIC 2는 NIC가 제공하는 1PPS 타이밍 출력과 동기화됩니다. 이 구성은 `PtpConfig` CR의 PTP 하드웨어 플러그인에서 제공합니다.

2 카드 PTP T-GM 구성에서는 `ptp4l` 의 인스턴스 1개와 `ts2phc` 의 인스턴스 1개를 사용합니다. `ptp4l` 및 `ts2phc` 프로그램은 각각 NIC마다 하나씩 두 개의 PTP 하드웨어 클럭(PHC)에서 작동하도록 구성됩니다. 호스트 시스템 클록은 GNSS 시간 소스에 연결된 NIC에서 동기화됩니다.

참고

다음 예제 `PtpConfig` CR을 기반으로 하여 이중 Intel E810 네트워크 인터페이스의 경우 `linuxptp` 서비스를 T-GM으로 구성합니다.

PTP 빠른 이벤트를 구성하려면 `ptp4lOpts`, `ptp4lConf` 및 `ptpClockThreshold` 에 적절한 값을 설정합니다. `ptpClockThreshold` 는 이벤트가 활성화된 경우에만 사용됩니다. 자세한 내용은 " PTP 빠른 이벤트 알림 게시자 구성"을 참조하십시오.

사전 요구 사항

프로덕션 환경의 T-GM 클록의 경우 베어 메탈 클러스터 호스트에 두 개의 Intel E810 NIC를 설치합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

`PtpConfig` CR을 생성합니다. 예를 들면 다음과 같습니다.

다음 YAML을 `grandmaster-clock-ptp-config-dual-nics.yaml` 파일에 저장합니다.

```yaml
# In this example two cards $iface_nic1 and $iface_nic2 are connected via
# SMA1 ports by a cable and $iface_nic2 receives 1PPS signals from $iface_nic1
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: grandmaster
  namespace: openshift-ptp
  annotations: {}
spec:
  profile:
    - name: "grandmaster"
      ptp4lOpts: "-2 --summary_interval -4"
      phc2sysOpts: -r -u 0 -m -N 8 -R 16 -s $iface_nic1 -n 24
      ptpSchedulingPolicy: SCHED_FIFO
      ptpSchedulingPriority: 10
      ptpSettings:
        logReduce: "true"
      plugins:
        e810:
          enableDefaultConfig: false
          settings:
            LocalMaxHoldoverOffSet: 1500
            LocalHoldoverTimeout: 14400
            MaxInSpecOffset: 1500
          pins: $e810_pins
          #  "$iface_nic1":
          #    "U.FL2": "0 2"
          #    "U.FL1": "0 1"
          #    "SMA2": "0 2"
          #    "SMA1": "2 1"
          #  "$iface_nic2":
          #    "U.FL2": "0 2"
          #    "U.FL1": "0 1"
          #    "SMA2": "0 2"
          #    "SMA1": "1 1"
          ublxCmds:
            - args: #ubxtool -P 29.20 -z CFG-HW-ANT_CFG_VOLTCTRL,1
                - "-P"
                - "29.20"
                - "-z"
                - "CFG-HW-ANT_CFG_VOLTCTRL,1"
              reportOutput: false
            - args: #ubxtool -P 29.20 -e GPS
                - "-P"
                - "29.20"
                - "-e"
                - "GPS"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d Galileo
                - "-P"
                - "29.20"
                - "-d"
                - "Galileo"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d GLONASS
                - "-P"
                - "29.20"
                - "-d"
                - "GLONASS"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d BeiDou
                - "-P"
                - "29.20"
                - "-d"
                - "BeiDou"
              reportOutput: false
            - args: #ubxtool -P 29.20 -d SBAS
                - "-P"
                - "29.20"
                - "-d"
                - "SBAS"
              reportOutput: false
            - args: #ubxtool -P 29.20 -t -w 5 -v 1 -e SURVEYIN,600,50000
                - "-P"
                - "29.20"
                - "-t"
                - "-w"
                - "5"
                - "-v"
                - "1"
                - "-e"
                - "SURVEYIN,600,50000"
              reportOutput: true
            - args: #ubxtool -P 29.20 -p MON-HW
                - "-P"
                - "29.20"
                - "-p"
                - "MON-HW"
              reportOutput: true
            - args: #ubxtool -P 29.20 -p CFG-MSG,1,38,248
                - "-P"
                - "29.20"
                - "-p"
                - "CFG-MSG,1,38,248"
              reportOutput: true
      ts2phcOpts: " "
      ts2phcConf: |
        [nmea]
        ts2phc.master 1
        [global]
        use_syslog  0
        verbose 1
        logging_level 7
        ts2phc.pulsewidth 100000000
        #cat /dev/GNSS to find available serial port
        #example value of gnss_serialport is /dev/ttyGNSS_1700_0
        ts2phc.nmea_serialport $gnss_serialport
        [$iface_nic1]
        ts2phc.extts_polarity rising
        ts2phc.extts_correction 0
        [$iface_nic2]
        ts2phc.master 0
        ts2phc.extts_polarity rising
        #this is a measured value in nanoseconds to compensate for SMA cable delay
        ts2phc.extts_correction -10
      ptp4lConf: |
        [$iface_nic1]
        masterOnly 1
        [$iface_nic1_1]
        masterOnly 1
        [$iface_nic1_2]
        masterOnly 1
        [$iface_nic1_3]
        masterOnly 1
        [$iface_nic2]
        masterOnly 1
        [$iface_nic2_1]
        masterOnly 1
        [$iface_nic2_2]
        masterOnly 1
        [$iface_nic2_3]
        masterOnly 1
        [global]
        #
        # Default Data Set
        #
        twoStepFlag 1
        priority1 128
        priority2 128
        domainNumber 24
        #utc_offset 37
        clockClass 6
        clockAccuracy 0x27
        offsetScaledLogVariance 0xFFFF
        free_running 0
        freq_est_interval 1
        dscp_event 0
        dscp_general 0
        dataset_comparison G.8275.x
        G.8275.defaultDS.localPriority 128
        #
        # Port Data Set
        #
        logAnnounceInterval -3
        logSyncInterval -4
        logMinDelayReqInterval -4
        logMinPdelayReqInterval 0
        announceReceiptTimeout 3
        syncReceiptTimeout 0
        delayAsymmetry 0
        fault_reset_interval -4
        neighborPropDelayThresh 20000000
        masterOnly 0
        G.8275.portDS.localPriority 128
        #
        # Run time options
        #
        assume_two_step 0
        logging_level 6
        path_trace_enabled 0
        follow_up_info 0
        hybrid_e2e 0
        inhibit_multicast_service 0
        net_sync_monitor 0
        tc_spanning_tree 0
        tx_timestamp_timeout 50
        unicast_listen 0
        unicast_master_table 0
        unicast_req_duration 3600
        use_syslog 1
        verbose 0
        summary_interval -4
        kernel_leap 1
        check_fup_sync 0
        clock_class_threshold 7
        #
        # Servo Options
        #
        pi_proportional_const 0.0
        pi_integral_const 0.0
        pi_proportional_scale 0.0
        pi_proportional_exponent -0.3
        pi_proportional_norm_max 0.7
        pi_integral_scale 0.0
        pi_integral_exponent 0.4
        pi_integral_norm_max 0.3
        step_threshold 2.0
        first_step_threshold 0.00002
        clock_servo pi
        sanity_freq_limit  200000000
        ntpshm_segment 0
        #
        # Transport options
        #
        transportSpecific 0x0
        ptp_dst_mac 01:1B:19:00:00:00
        p2p_dst_mac 01:80:C2:00:00:0E
        udp_ttl 1
        udp6_scope 0x0E
        uds_address /var/run/ptp4l
        #
        # Default interface options
        #
        clock_type BC
        network_transport L2
        delay_mechanism E2E
        time_stamping hardware
        tsproc_mode filter
        delay_filter moving_median
        delay_filter_length 10
        egressLatency 0
        ingressLatency 0
        boundary_clock_jbod 1
        #
        # Clock description
        #
        productDescription ;;
        revisionData ;;
        manufacturerIdentity 00:00:00
        userDescription ;
        timeSource 0x20
  recommend:
    - profile: "grandmaster"
      priority: 4
      match:
        - nodeLabel: "node-role.kubernetes.io/$mcp"
```

참고

`ts2phc.nmea_serialport` 의 값을 `/dev/gnss0` 로 설정합니다.

다음 명령을 실행하여 CR을 생성합니다.

```shell-session
$ oc create -f grandmaster-clock-ptp-config-dual-nics.yaml
```

검증

`PtpConfig` 프로필이 노드에 적용되었는지 확인합니다.

다음 명령을 실행하여 `openshift-ptp` 네임스페이스에서 Pod 목록을 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                          READY   STATUS    RESTARTS   AGE     IP             NODE
linuxptp-daemon-74m2g         3/3     Running   3          4d15h   10.16.230.7    compute-1.example.com
ptp-operator-5f4f48d7c-x7zkf  1/1     Running   1          4d15h   10.128.1.145   compute-1.example.com
```

프로필이 올바른지 확인합니다. `PtpConfig` 프로필에 지정한 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다. 다음 명령을 실행합니다.

```shell-session
$ oc logs linuxptp-daemon-74m2g -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
ts2phc[509863.660]: [ts2phc.0.config] nmea delay: 347527248 ns
ts2phc[509863.660]: [ts2phc.0.config] ens2f0 extts index 0 at 1705516553.000000000 corr 0 src 1705516553.652499081 diff 0
ts2phc[509863.660]: [ts2phc.0.config] ens2f0 master offset          0 s2 freq      -0
I0117 18:35:16.000146 1633226 stats.go:57] state updated for ts2phc =s2
I0117 18:35:16.000163 1633226 event.go:417] dpll State s2, gnss State s2, tsphc state s2, gm state s2,
ts2phc[1705516516]:[ts2phc.0.config] ens2f0 nmea_status 1 offset 0 s2
GM[1705516516]:[ts2phc.0.config] ens2f0 T-GM-STATUS s2
ts2phc[509863.677]: [ts2phc.0.config] ens7f0 extts index 0 at 1705516553.000000010 corr -10 src 1705516553.652499081 diff 0
ts2phc[509863.677]: [ts2phc.0.config] ens7f0 master offset          0 s2 freq      -0
I0117 18:35:16.016597 1633226 stats.go:57] state updated for ts2phc =s2
phc2sys[509863.719]: [ptp4l.0.config] CLOCK_REALTIME phc offset        -6 s2 freq  +15441 delay    510
phc2sys[509863.782]: [ptp4l.0.config] CLOCK_REALTIME phc offset        -7 s2 freq  +15438 delay    502
```

#### 7.2.4.2. linuxptp 서비스를 3 E810 NIC의 할마스터 클록으로 구성

NIC를 구성하는 `PtpConfig` CR(사용자 정의 리소스)을 3 E810 NIC의 grandmaster 클럭(T-GM)으로 `linuxptp` 서비스(`ptp4l`, `phc2sys`, `ts2phc`)를 구성할 수 있습니다.

다음 E810 NIC에 대해 3개의 NIC를 사용하여 `linuxptp` 서비스를 T-GM으로 구성할 수 있습니다.

Intel E810-XXVDA4T Westport 채널 NIC

Intel E810-CQDA2T Logan Beach NIC

분산 RAN(D-RAN) 사용 사례의 경우 다음과 같이 3개의 NIC에 대해 PTP를 구성할 수 있습니다.

NIC 1이 GNSS(Global Navigation Satellite System)와 동기화됩니다.

NIC 2 및 3은 1PPS faceplate 연결을 사용하여 NIC 1과 동기화됩니다.

다음 예제 `PtpConfig` CR을 기반으로 `linuxptp` 서비스를 3 카드 Intel E810 T-GM으로 구성합니다.

사전 요구 사항

프로덕션 환경의 T-GM 클록의 경우 베어 메탈 클러스터 호스트에 3개의 Intel E810 NIC를 설치합니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

`PtpConfig` CR을 생성합니다. 예를 들면 다음과 같습니다.

다음 YAML을 `three-nic-grandmaster-clock-ptp-config.yaml` 파일에 저장합니다.

```yaml
# In this example, the three cards are connected via SMA cables:
# - $iface_timeTx1 has the GNSS signal input
# - $iface_timeTx2 SMA1 is connected to $iface_timeTx1 SMA1
# - $iface_timeTx3 SMA1 is connected to $iface_timeTx1 SMA2
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: gm-3card
  namespace: openshift-ptp
  annotations:
    ran.openshift.io/ztp-deploy-wave: "10"
spec:
  profile:
  - name: grandmaster
    ptp4lOpts: -2 --summary_interval -4
    phc2sysOpts: -r -u 0 -m -N 8 -R 16 -s $iface_timeTx1 -n 24
    ptpSchedulingPolicy: SCHED_FIFO
    ptpSchedulingPriority: 10
    ptpSettings:
      logReduce: "true"
    plugins:
      e810:
        enableDefaultConfig: false
        settings:
          LocalHoldoverTimeout: 14400
          LocalMaxHoldoverOffSet: 1500
          MaxInSpecOffset: 1500
        pins:
          # Syntax guide:
          # - The 1st number in each pair must be one of:
          #    0 - Disabled
          #    1 - RX
          #    2 - TX
          # - The 2nd number in each pair must match the channel number
          $iface_timeTx1:
            SMA1: 2 1
            SMA2: 2 2
            U.FL1: 0 1
            U.FL2: 0 2
          $iface_timeTx2:
            SMA1: 1 1
            SMA2: 0 2
            U.FL1: 0 1
            U.FL2: 0 2
          $iface_timeTx3:
            SMA1: 1 1
            SMA2: 0 2
            U.FL1: 0 1
            U.FL2: 0 2
        ublxCmds:
          - args: #ubxtool -P 29.20 -z CFG-HW-ANT_CFG_VOLTCTRL,1
              - "-P"
              - "29.20"
              - "-z"
              - "CFG-HW-ANT_CFG_VOLTCTRL,1"
            reportOutput: false
          - args: #ubxtool -P 29.20 -e GPS
              - "-P"
              - "29.20"
              - "-e"
              - "GPS"
            reportOutput: false
          - args: #ubxtool -P 29.20 -d Galileo
              - "-P"
              - "29.20"
              - "-d"
              - "Galileo"
            reportOutput: false
          - args: #ubxtool -P 29.20 -d GLONASS
              - "-P"
              - "29.20"
              - "-d"
              - "GLONASS"
            reportOutput: false
          - args: #ubxtool -P 29.20 -d BeiDou
              - "-P"
              - "29.20"
              - "-d"
              - "BeiDou"
            reportOutput: false
          - args: #ubxtool -P 29.20 -d SBAS
              - "-P"
              - "29.20"
              - "-d"
              - "SBAS"
            reportOutput: false
          - args: #ubxtool -P 29.20 -t -w 5 -v 1 -e SURVEYIN,600,50000
              - "-P"
              - "29.20"
              - "-t"
              - "-w"
              - "5"
              - "-v"
              - "1"
              - "-e"
              - "SURVEYIN,600,50000"
            reportOutput: true
          - args: #ubxtool -P 29.20 -p MON-HW
              - "-P"
              - "29.20"
              - "-p"
              - "MON-HW"
            reportOutput: true
          - args: #ubxtool -P 29.20 -p CFG-MSG,1,38,248
              - "-P"
              - "29.20"
              - "-p"
              - "CFG-MSG,1,38,248"
            reportOutput: true
    ts2phcOpts: " "
    ts2phcConf: |
      [nmea]
      ts2phc.master 1
      [global]
      use_syslog  0
      verbose 1
      logging_level 7
      ts2phc.pulsewidth 100000000
      #example value of nmea_serialport is /dev/gnss0
      ts2phc.nmea_serialport (?<gnss_serialport>[/\w\s/]+)
      leapfile /usr/share/zoneinfo/leap-seconds.list
      [$iface_timeTx1]
      ts2phc.extts_polarity rising
      ts2phc.extts_correction 0
      [$iface_timeTx2]
      ts2phc.master 0
      ts2phc.extts_polarity rising
      #this is a measured value in nanoseconds to compensate for SMA cable delay
      ts2phc.extts_correction -10
      [$iface_timeTx3]
      ts2phc.master 0
      ts2phc.extts_polarity rising
      #this is a measured value in nanoseconds to compensate for SMA cable delay
      ts2phc.extts_correction -10
    ptp4lConf: |
      [$iface_timeTx1]
      masterOnly 1
      [$iface_timeTx1_1]
      masterOnly 1
      [$iface_timeTx1_2]
      masterOnly 1
      [$iface_timeTx1_3]
      masterOnly 1
      [$iface_timeTx2]
      masterOnly 1
      [$iface_timeTx2_1]
      masterOnly 1
      [$iface_timeTx2_2]
      masterOnly 1
      [$iface_timeTx2_3]
      masterOnly 1
      [$iface_timeTx3]
      masterOnly 1
      [$iface_timeTx3_1]
      masterOnly 1
      [$iface_timeTx3_2]
      masterOnly 1
      [$iface_timeTx3_3]
      masterOnly 1
      [global]
      #
      # Default Data Set
      #
      twoStepFlag 1
      priority1 128
      priority2 128
      domainNumber 24
      #utc_offset 37
      clockClass 6
      clockAccuracy 0x27
      offsetScaledLogVariance 0xFFFF
      free_running 0
      freq_est_interval 1
      dscp_event 0
      dscp_general 0
      dataset_comparison G.8275.x
      G.8275.defaultDS.localPriority 128
      #
      # Port Data Set
      #
      logAnnounceInterval -3
      logSyncInterval -4
      logMinDelayReqInterval -4
      logMinPdelayReqInterval 0
      announceReceiptTimeout 3
      syncReceiptTimeout 0
      delayAsymmetry 0
      fault_reset_interval -4
      neighborPropDelayThresh 20000000
      masterOnly 0
      G.8275.portDS.localPriority 128
      #
      # Run time options
      #
      assume_two_step 0
      logging_level 6
      path_trace_enabled 0
      follow_up_info 0
      hybrid_e2e 0
      inhibit_multicast_service 0
      net_sync_monitor 0
      tc_spanning_tree 0
      tx_timestamp_timeout 50
      unicast_listen 0
      unicast_master_table 0
      unicast_req_duration 3600
      use_syslog 1
      verbose 0
      summary_interval -4
      kernel_leap 1
      check_fup_sync 0
      clock_class_threshold 7
      #
      # Servo Options
      #
      pi_proportional_const 0.0
      pi_integral_const 0.0
      pi_proportional_scale 0.0
      pi_proportional_exponent -0.3
      pi_proportional_norm_max 0.7
      pi_integral_scale 0.0
      pi_integral_exponent 0.4
      pi_integral_norm_max 0.3
      step_threshold 2.0
      first_step_threshold 0.00002
      clock_servo pi
      sanity_freq_limit 200000000
      ntpshm_segment 0
      #
      # Transport options
      #
      transportSpecific 0x0
      ptp_dst_mac 01:1B:19:00:00:00
      p2p_dst_mac 01:80:C2:00:00:0E
      udp_ttl 1
      udp6_scope 0x0E
      uds_address /var/run/ptp4l
      #
      # Default interface options
      #
      clock_type BC
      network_transport L2
      delay_mechanism E2E
      time_stamping hardware
      tsproc_mode filter
      delay_filter moving_median
      delay_filter_length 10
      egressLatency 0
      ingressLatency 0
      boundary_clock_jbod 1
      #
      # Clock description
      #
      productDescription ;;
      revisionData ;;
      manufacturerIdentity 00:00:00
      userDescription ;
      timeSource 0x20
    ptpClockThreshold:
      holdOverTimeout: 5
      maxOffsetThreshold: 1500
      minOffsetThreshold: -1500
  recommend:
  - profile: grandmaster
    priority: 4
    match:
    - nodeLabel: node-role.kubernetes.io/$mcp
```

참고

`ts2phc.nmea_serialport` 의 값을 `/dev/gnss0` 로 설정합니다.

다음 명령을 실행하여 CR을 생성합니다.

```shell-session
$ oc create -f three-nic-grandmaster-clock-ptp-config.yaml
```

검증

`PtpConfig` 프로필이 노드에 적용되었는지 확인합니다.

다음 명령을 실행하여 `openshift-ptp` 네임스페이스에서 Pod 목록을 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                          READY   STATUS    RESTARTS   AGE     IP             NODE
linuxptp-daemon-74m3q         3/3     Running   3          4d15h   10.16.230.7    compute-1.example.com
ptp-operator-5f4f48d7c-x6zkn  1/1     Running   1          4d15h   10.128.1.145   compute-1.example.com
```

프로필이 올바른지 확인합니다. 다음 명령을 실행하고 `PtpConfig` 프로필에 지정한 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다.

```shell-session
$ oc logs linuxptp-daemon-74m3q -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
ts2phc[2527.586]: [ts2phc.0.config:7] adding tstamp 1742826342.000000000 to clock /dev/ptp11
ts2phc[2527.586]: [ts2phc.0.config:7] adding tstamp 1742826342.000000000 to clock /dev/ptp7
ts2phc[2527.586]: [ts2phc.0.config:7] adding tstamp 1742826342.000000000 to clock /dev/ptp14
ts2phc[2527.586]: [ts2phc.0.config:7] nmea delay: 56308811 ns
ts2phc[2527.586]: [ts2phc.0.config:6] /dev/ptp14 offset          0 s2 freq      +0
ts2phc[2527.587]: [ts2phc.0.config:6] /dev/ptp7 offset          0 s2 freq      +0
ts2phc[2527.587]: [ts2phc.0.config:6] /dev/ptp11 offset          0 s2 freq      -0
I0324 14:25:05.000439  106907 stats.go:61] state updated for ts2phc =s2
I0324 14:25:05.000504  106907 event.go:419] dpll State s2, gnss State s2, tsphc state s2, gm state s2,
I0324 14:25:05.000906  106907 stats.go:61] state updated for ts2phc =s2
I0324 14:25:05.001059  106907 stats.go:61] state updated for ts2phc =s2
ts2phc[1742826305]:[ts2phc.0.config] ens4f0 nmea_status 1 offset 0 s2
GM[1742826305]:[ts2phc.0.config] ens4f0 T-GM-STATUS s2
```

1. 2

3. `ts2phc` 가 PTP 하드웨어 클록을 업데이트하고 있습니다.

4. 5

6. PTP 장치와 참조 클럭 간의 예상 PTP 장치 오프셋은 0 나노초입니다. PTP 장치는 리더 클록과 동기화됩니다.

7. T-GM은 잠긴 상태(s2)입니다.

추가 리소스

PTP 빠른 이벤트 알림 게시자 구성

#### 7.2.5. Grandmaster 클럭 PtpConfig 구성 참조

다음 참조 정보는 `linuxptp` 서비스(`ptp4l`, `phc2sys`, `ts2phc`)를 마스터 클록으로 구성하는 `PtpConfig` CR(사용자 정의 리소스)의 구성 옵션을 설명합니다.

| PtpConfig CR 필드 | 설명 |
| --- | --- |
| `plugins` | 마스터 클록 작업에 대한 NIC를 구성하는 `.exec.cmdline` 옵션 배열을 지정합니다. Grandmaster 클럭 구성을 사용하려면 특정 PTP 핀을 비활성화해야 합니다. 플러그인 메커니즘을 사용하면 PTP Operator가 자동화된 하드웨어 구성을 수행할 수 있습니다. Intel Westport Channel NIC 또는 Intel Logan Beach NIC의 경우 `enableDefaultConfig` 필드가 `true` 로 설정된 경우 PTP Operator는 NIC에 필요한 구성을 수행하기 위해 하드 코딩된 스크립트를 실행합니다. |
| `ptp4lOpts` | `ptp4l` 서비스에 대한 시스템 구성 옵션을 지정합니다. 옵션은 네트워크 인터페이스 이름과 서비스 구성 파일이 자동으로 추가되므로 네트워크 인터페이스 이름 `-i <interface>` 및 서비스 구성 파일 `-f /etc/ptp4l.conf` 를 포함하지 않아야 합니다. |
| `ptp4lConf` | `ptp4l` 을 할 마스터 클록으로 시작하는 데 필요한 구성을 지정합니다. 예를 들어 `ens2f1` 인터페이스는 다운스트림 연결 장치를 동기화합니다. 마스터 클록의 경우 `clockClass` 를 `6` 으로 설정하고 `clockAccuracy` 를 `0x27` 로 설정합니다. GNSS(Global navigation satellite system)에서 타이밍 신호를 수신할 때 `timeSource` 를 `0x20` 으로 설정합니다. |
| `tx_timestamp_timeout` | 데이터를 삭제하기 전에 발신자로부터 전송(TX) 타임스탬프를 대기할 최대 시간(TX)을 지정합니다. |
| `boundary_clock_jbod` | JBOD 경계 클럭 시간 지연 값을 지정합니다. 이 값은 네트워크 시간 장치 간에 전달되는 시간 값을 수정하는 데 사용됩니다. |
| `phc2sysOpts` | `phc2sys` 서비스에 대한 시스템 구성 옵션을 지정합니다. 이 필드가 비어 있으면 PTP Operator에서 `phc2sys` 서비스를 시작하지 않습니다. 참고 여기에 나열된 네트워크 인터페이스가 grandmaster로 구성되어 있고 `ts2phcConf` 및 `ptp4lConf` 필드에서 필요에 따라 참조되는지 확인합니다. |
| `ptpSchedulingPolicy` | `ptp4l` 및 `phc2sys` 프로세스에 대한 스케줄링 정책을 구성합니다. 기본값은 Cryo `stat_OTHER` 입니다. FIFO 스케줄링을 지원하는 시스템에서 Cryostat `_FIFO` 를 사용합니다. |
| `ptpSchedulingPriority` | `ptpSchedulingPolicy` 가 Cryostat `_FIFO` 로 설정된 경우 `ptp4l` 및 `phc2sys` 프로세스의 FIFO 우선 순위를 구성하도록 1-65의 정수 값을 설정합니다. `ptpSchedulingPolicy` 가 ptpSchedulingPolicy로 설정된 경우 `ptpSchedulingPriority` 필드는 사용되지 `않습니다` . |
| `ptpClockThreshold` | 선택 사항: `ptpClockThreshold` 스탠자가 없으면 `ptpClockThreshold` 필드에 기본값이 사용됩니다. 스탠자는 기본 `ptpClockThreshold` 값을 표시합니다. `ptpClockThreshold` 값은 PTP 이벤트가 트리거되기 전에 PTP 마스터 클록의 연결이 해제된 후의 시간을 구성합니다. `holdOverTimeout` 은 PTP 마스터 클록의 연결이 끊어지면 PTP 클럭 이벤트 상태가 Free `RUN` 으로 변경되기 전의 시간(초)입니다. `maxOffsetThreshold` 및 `minOffsetThreshold` 설정은 `CLOCK_REALTIME` ( `phc2sys` ) 또는 master 오프셋( `ptp4l` )의 값과 비교하는 오프셋 값을 나노초로 구성합니다. `ptp4l` 또는 `phc2sys` 오프셋 값이 이 범위를 벗어나는 경우 PTP 클럭 상태가 Free `RUN으로` 설정됩니다. 오프셋 값이 이 범위 내에 있으면 PTP 클럭 상태가 `LOCKED` 로 설정됩니다. |
| `ts2phcConf` | `ts2phc` 명령의 구성을 설정합니다. `leapfile` 은 PTP Operator 컨테이너 이미지의 현재 윤초 정의 파일의 기본 경로입니다. `ts2phc.nmea_serialport` 는 NMEA GPS 클럭 소스에 연결된 직렬 포트 장치입니다. 구성되면 / `dev/gnss<id> 에서 GNSS 수신자에 액세스할 수 있습니다` . 호스트에 GNSS 수신자가 여러 개 있는 경우 다음 장치 중 하나를 열거하여 올바른 장치를 찾을 수 있습니다. `/sys/class/net/<eth_port>/device/gnss/` `/sys/class/gnss/gnss<id>/device/` |
| `ts2phcOpts` | `ts2phc` 명령에 대한 옵션을 설정합니다. |
| `권장` | `프로필` 을 노드에 적용하는 방법에 대한 규칙을 정의하는 하나 이상의 `recommend` 오브젝트 배열을 지정합니다. |
| `.recommend.profile` | `profile` 섹션에 정의된 `.recommend.profile` 오브젝트 이름을 지정합니다. |
| `.recommend.priority` | `0` 에서 `99` 사이의 정수 값으로 `priority` 를 지정합니다. 숫자가 클수록 우선순위가 낮으므로 우선순위 `99` 는 우선순위 `10` 보다 낮습니다. `match` 필드에 정의된 규칙에 따라 여러 프로필과 노드를 일치시킬 수 있는 경우 우선 순위가 높은 프로필이 해당 노드에 적용됩니다. |
| `.recommend.match` | `nodeLabel` 또는 `nodeName` 값을 사용하여 `.recommend.match` 규칙을 지정합니다. |
| `.recommend.match.nodeLabel` | `oc get nodes --show-labels` 명령을 사용하여 노드 오브젝트에서 `node.Labels` 필드의 `키로` `nodeLabel` 을 설정합니다. 예: `node-role.kubernetes.io/worker` . |
| `.recommend.match.nodeName` | `oc get nodes` 명령을 사용하여 노드 오브젝트의 `node.Name` 필드 값으로 `nodeName` 을 설정합니다. 예를 들면 `compute-1.example.com` 입니다. |

#### 7.2.5.1. Grandmaster 클럭 클래스 동기화 상태 참조

다음 표는 PTP 할 마스터 클록 (T-GM) `gm.ClockClass` 상태를 설명합니다. 클럭 클래스는 PRTC(Basic Reference Time Clock) 또는 기타 타이밍 소스와 관련하여 정확성 및 안정성을 기반으로 T-GM 시계를 분류합니다.

홀드오버 사양은 PTP 클럭이 기본 시간 소스에서 업데이트를 수신하지 않고도 동기화를 유지할 수 있는 시간입니다.

| 클럭 클래스 상태 | 설명 |
| --- | --- |
| `gm.ClockClass 6` | T-GM 클록은 `LOCKED` 모드의 PRTC에 연결됩니다. 예를 들어 PRTC는 GNSS 시간 소스에서 추적할 수 있습니다. |
| `gm.ClockClass 7` | T-GM 클록은 `HOLDOVER` 모드 및 홀드오버 사양에 있습니다. 클럭 소스는 카테고리 1 빈도 소스에서 추적되지 않을 수 있습니다. |
| `gm.ClockClass 248` | T-GM 시계는 `freeRUN` 모드입니다. |

자세한 내용은 "상시/시간 추적 정보", ITU-T G.8275.1/Y.1369.1 권장 사항을 참조하십시오.

#### 7.2.5.2. Intel E810 NIC 하드웨어 구성 참조

이 정보를 사용하여 Intel E810 하드웨어 플러그인을 사용하여 E810 네트워크 인터페이스를 PTP 마스터 클록으로 구성하는 방법을 파악합니다. 하드웨어 핀 구성은 네트워크 인터페이스가 시스템의 다른 구성 요소 및 장치와 상호 작용하는 방식을 결정합니다.

Intel E810 NIC에는 외부 1PPS 신호를 위한 네 개의 커넥터가 있습니다: `SMA1`, `SMA2`, `U.FL1` 및 `U.FL2`.

| 하드웨어 핀 | 권장 설정 | 설명 |
| --- | --- | --- |
| `U.FL1` | `0 1` | `U.FL1` 커넥터 입력을 비활성화합니다. `U.FL1` 커넥터는 출력 전용입니다. |
| `U.FL2` | `0 2` | `U.FL2` 커넥터 출력을 비활성화합니다. `U.FL2` 커넥터는 입력 전용입니다. |
| `SMA1` | `0 1` | `SMA1` 커넥터 입력을 비활성화합니다. `SMA1` 커넥터는 양방향입니다. |
| `SMA2` | `0 2` | `SMA2` 커넥터 출력을 비활성화합니다. `SMA2` 커넥터는 양방향입니다. |

다음 예와 같이 `spec.profile.plugins.e810.pins` 매개변수를 사용하여 Intel E810 NIC에서 핀 구성을 설정할 수 있습니다.

```yaml
pins:
      <interface_name>:
        <connector_name>: <function> <channel_number>
```

다음과 같습니다.

`<function` >: 핀의 역할을 지정합니다. 다음 값은 pin 역할과 연결됩니다.

`0`: disabled

`1`: RX (Receive timestamping)

`2`: TX (Transmit timestamping)

다음 명령>: 물리적 커넥터와 관련된 번호입니다. 다음 채널 번호는 물리적 커넥터와 연결되어 있습니다.

```shell
<channel number
```

`1`: `SMA1` 또는 `U.FL1`

`2`: `SMA2` 또는 `U.FL2`

예:

`0 1`: `SMA1` 또는 `U.FL1` 에 매핑된 핀을 비활성화합니다.

`1 2`: Rx 함수를 `SMA2` 또는 `U.FL2` 에 할당합니다.

참고

`SMA1` 및 `U.FL1` 커넥터는 채널 1을 공유합니다. `SMA2` 및 `U.FL2` 커넥터는 채널 2를 공유합니다.

`spec.profile.plugins.e810.ublxCmds` 매개변수를 설정하여 `PtpConfig` CR(사용자 정의 리소스)에서 GNSS 시계를 구성합니다.

중요

T-GM GPS 마케이터 케이블 신호 지연을 보완하려면 오프셋 값을 구성해야 합니다. 최적의 T-GM radio offset 값을 구성하려면 GNSS radio cable signal 지연을 정확하게 측정하십시오. Red Hat은 이러한 측정을 지원하거나 필요한 지연 오프셋에 대한 값을 제공할 수 없습니다.

이러한 `ublxCmds` 스탠자 각각 `ubxtool` 명령을 사용하여 호스트 NIC에 적용되는 구성에 해당합니다. 예를 들면 다음과 같습니다.

```yaml
ublxCmds:
  - args:
      - "-P"
      - "29.20"
      - "-z"
      - "CFG-HW-ANT_CFG_VOLTCTRL,1"
      - "-z"
      - "CFG-TP-ANT_CABLEDELAY,<antenna_delay_offset>"
    reportOutput: false
```

1. 나노초 단위의 T-GM 마더레이션 지연 오프셋입니다. 필요한 지연 오프셋 값을 얻으려면 외부 테스트 장치를 사용하여 케이블 지연을 측정해야 합니다.

다음 표에서는 동일한 `ubxtool` 명령을 설명합니다.

| ubxtool 명령 | 설명 |
| --- | --- |
| `ubxtool -P 29.20 -z CFG-HW-ANT_CFG_VOLTCTRL,1 -z CFG-TP-ANT_CABLEDELAY,<antenna_delay_offset>` | 사도전압 제어를 가능하게 하고, `UBX-MON-RF` 및 `UBX-INF-NOTICE` 로그 메시지에서 마케도 상태를 보고할 수 있으며, GPS 마케도 신호 지연을 상쇄하는 나노초 내에 < `antenna_delay_offset` > 값을 설정합니다. |
| `ubxtool -P 29.20 -e GPS` | Angon이 GPS 신호를 수신할 수 있도록 합니다. |
| `ubxtool -P 29.20 -d Galileo` | Galileo GPS satellite에서 신호를 수신하도록 Angalileo GPS Satellite를 구성합니다. |
| `ubxtool -P 29.20 -d GLONASS` | GLONASS GPS Satellite에서 신호를 수신하지 못하게 합니다. |
| `ubxtool -P 29.20 -d BeiDou` | 마진이 BeiDou GPS Satellite에서 신호를 수신하지 못하도록 비활성화합니다. |
| `ubxtool -P 29.20 -d SBAS` | SBAS GPS Satellite에서 신호를 수신하지 못하게 합니다. |
| `ubxtool -P 29.20 -t -w 5 -v 1 -e SURVEYIN,600,50000` | 초기 위치 추정을 개선하도록 GNSS 수신기 설문 조사 프로세스를 구성합니다. 최적의 결과를 얻으려면 최대 24 시간이 걸릴 수 있습니다. |
| `ubxtool -P 29.20 -p MON-HW` | 하드웨어의 자동화된 단일 검사를 실행하고 NIC 상태 및 구성 설정에 대해 보고합니다. |

#### 7.2.5.3. Dual E810 NIC 구성 참조

이 정보를 사용하여 Intel E810 하드웨어 플러그인을 사용하여 E810 네트워크 인터페이스를 PTP 할 마스터 클록(T-GM)으로 구성하는 방법을 파악합니다.

듀얼 NIC 클러스터 호스트를 구성하기 전에 1PPS faceplace 연결을 사용하여 두 NIC를 SMA1 케이블과 연결해야 합니다.

듀얼 NIC T-GM을 구성할 때 SMA1 연결 포트를 사용하여 NIC를 연결할 때 발생하는 1PPS 신호 지연을 보완해야 합니다. 케이블 길이, 주변 온도 및 구성 요소 및 제조 허용 오차와 같은 다양한 요인은 신호 지연에 영향을 미칠 수 있습니다. 지연을 보완하려면 신호 지연을 오프셋하는 데 사용하는 특정 값을 계산해야 합니다.

| PtpConfig field | 설명 |
| --- | --- |
| `spec.profile.plugins.e810.pins` | PTP Operator E810 하드웨어 플러그인을 사용하여 E810 하드웨어 핀을 구성합니다. Pin `2 1` 은 NIC에서 `SMA1` 에 대한 `1PPS OUT` 연결을 활성화합니다. Pin `1` 은 NIC에서 `SMA1` 에 대한 `1PPS IN` 연결을 활성화합니다. |
| `spec.profile.ts2phcConf` | `ts2phcConf` 필드를 사용하여 NIC 1과 NIC 2에 대한 매개변수를 구성합니다. NIC 2의 경우 `ts2phc.master 0` 을 설정합니다. 이렇게 하면 GNSS가 아닌 1PPS 입력에서 NIC 2의 타이밍 소스를 구성합니다. NIC 2에 대해 `ts2phc.extts_correction` 값을 구성하여 사용하는 특정 SMA 케이블 및 케이블 길이에 대해 발생하는 지연을 보완합니다. 구성하는 값은 특정 측정 및 SMA1 케이블 길이에 따라 다릅니다. |
| `spec.profile.ptp4lConf` | `boundary_clock_jbod` 값을 1로 설정하여 여러 NIC에 대한 지원을 활성화합니다. |

`spec.profile.plugins.e810.pins` 목록의 각 값은 < `function` > < `channel_number` > 형식을 따릅니다.

다음과 같습니다.

`<function` >: 핀 역할을 지정합니다. 다음 값은 pin 역할과 연결됩니다.

`0`: disabled

`1`: 수신 (Rx) - 1PPS IN의 경우

`2`: 전송 (Tx) - 1PPS OUT 용

`<channel_number` >: 물리적 커넥터와 관련된 번호입니다. 다음 채널 번호는 물리적 커넥터와 연결되어 있습니다.

`1`: `SMA1` 또는 `U.FL1`

`2`: `SMA2` 또는 `U.FL2`

예:

`2 1`: `SMA1` 에서 `1PPS OUT` (Tx)을 활성화합니다.

`1 1`: `SMA1` 에서 `1PPS IN` (Rx)을 활성화합니다.

PTP Operator는 이러한 값을 Intel E810 하드웨어 플러그인에 전달하여 각 NIC의 sysfs 핀 구성 인터페이스에 씁니다.

#### 7.2.5.4. 3-card E810 NIC 구성 참조

이 정보를 사용하여 E810 NIC를 PTP 할 마스터 클록(T-GM)으로 구성하는 방법을 파악합니다.

3 카드 클러스터 호스트를 구성하기 전에 1PPS faceplate 연결을 사용하여 3 NIC를 연결해야 합니다. 기본 NIC `1PPS_out` 출력은 다른 2 NIC를 제공합니다.

3 카드 T-GM을 구성할 때 SMA1 연결 포트를 사용하여 NIC를 연결할 때 발생하는 1PPS 신호 지연을 보완해야 합니다. 케이블 길이, 주변 온도 및 구성 요소 및 제조 허용 오차와 같은 다양한 요인은 신호 지연에 영향을 미칠 수 있습니다. 지연을 보완하려면 신호 지연을 오프셋하는 데 사용하는 특정 값을 계산해야 합니다.

| PtpConfig field | 설명 |
| --- | --- |
| `spec.profile.plugins.e810.pins` | PTP Operator E810 하드웨어 플러그인을 사용하여 E810 하드웨어 핀을 구성합니다. `$iface_timeTx1.SMA1` 은 NIC 1에서 `SMA1` 에 대한 `1PPS OUT` 연결을 활성화합니다. `$iface_timeTx1.SMA2` 는 NIC 1에서 `SMA2` 에 대한 `1PPS OUT` 연결을 활성화합니다. `$iface_timeTx2.SMA1` 및 `$iface_timeTx3.SMA1` 은 NIC 2 및 NIC 3에서 `SMA1` 에 대해 `1PPS IN` 연결을 활성화합니다. `$iface_timeTx2. SMA2` 및 `$iface_timeTx3.SMA2` 는 NIC 2 및 NIC 3에서 SMA2 연결을 비활성화합니다. |
| `spec.profile.ts2phcConf` | `ts2phcConf` 필드를 사용하여 NIC의 매개변수를 구성합니다. NIC 2 및 NIC 3의 경우 `ts2phc.master 0` 을 설정합니다. 이렇게 하면 GNSS가 아닌 1PPS 입력에서 NIC 2 및 NIC 3의 타이밍 소스를 구성합니다. 사용하는 특정 SMA 케이블 및 케이블 길이에 대해 발생하는 지연을 보완하도록 NIC 2 및 NIC 3에 대해 `ts2phc.extts_correction` 값을 구성합니다. 구성하는 값은 특정 측정 및 SMA1 케이블 길이에 따라 다릅니다. |
| `spec.profile.ptp4lConf` | `boundary_clock_jbod` 값을 1로 설정하여 여러 NIC에 대한 지원을 활성화합니다. |

#### 7.2.6. GNSS를 소스로 사용하는 마스터 클록의 홀드오버

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/openshift-ptp-holdover-tgm-clock-with-gnss.png" alt="GNSS를 소스로 사용하는 T-GM 클록의 홀드오버" kind="figure" diagram_type="image_figure"]
GNSS를 소스로 사용하는 T-GM 클록의 홀드오버
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/2f9b8ca1e24780ff73ac4afcef8b9256/openshift-ptp-holdover-tgm-clock-with-gnss.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/darkcircle-1.png" alt="20" kind="figure" diagram_type="image_figure"]
20
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/066d390945eb233d66d1b10310fec9e7/darkcircle-1.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/darkcircle-2.png" alt="20" kind="figure" diagram_type="image_figure"]
20
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/dffcf5a2ed44061a19f38d92a8a3d1bb/darkcircle-2.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/darkcircle-3.png" alt="20" kind="figure" diagram_type="image_figure"]
20
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/e4171dd0f615beb50be5dc701259f444/darkcircle-3.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/darkcircle-4.png" alt="20" kind="figure" diagram_type="image_figure"]
20
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/dd170f3f40e17838a75352ca1962f9bb/darkcircle-4.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/darkcircle-5.png" alt="20" kind="figure" diagram_type="image_figure"]
20
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/b86066dfcdf40a6c7ce19b770a9d3868/darkcircle-5.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/darkcircle-6.png" alt="20" kind="figure" diagram_type="image_figure"]
20
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/3355b6bb1a911bd888724ef147bddf81/darkcircle-6.png`_


holdover를 사용하면 GNSS(Global navigation satellite system) 소스를 사용할 수 없는 경우 T-GM(T-GM) 클럭을 동기화 성능을 유지할 수 있습니다. 이 기간 동안 T-GM 클럭은 타이밍 중단을 줄이기 위해 내부 오실레이터 및 홀드오버 매개변수에 의존합니다.

`PTPConfig` CR(사용자 정의 리소스)에서 다음 holdover 매개변수를 구성하여 홀드오버 동작을 정의할 수 있습니다.

`MaxInSpecOffset`

나노초 단위로 허용되는 최대 오프셋을 지정합니다. T-GM 시계가 `MaxInSpecOffset` 값을 초과하면 free `RUN` 상태(clock 클래스 상태 `gm.ClockClass 248`)로 전환됩니다.

`LocalHoldoverTimeout`

free `RUN` 상태로 전환하기 전에 T-GM 클럭이 홀드오버 상태에 남아 있는 최대 기간(초)을 지정합니다.

`LocalMaxHoldoverOffSet`

T-GM 클럭이 나노초 단위의 홀드오버 상태 중에 도달할 수 있는 최대 오프셋을 지정합니다.

`MaxInSpecOffset` 값이 `LocalMaxHoldoverOffset` 값보다 적고 T-GM 클럭이 최대 오프셋 값을 초과하면 T-GM 클럭이 홀드오버 상태에서 free `RUN` 상태로 전환됩니다.

중요

`LocalMaxHoldoverOffSet` 값이 `MaxInSpecOffset` 값보다 작으면 클럭이 최대 오프셋에 도달하기 전에 홀오버 타임아웃이 수행됩니다. 이 문제를 해결하려면 `MaxInSpecOffset` 필드와 `LocalMaxHoldoverOffset` 필드를 동일한 값으로 설정합니다.

클럭 클래스 상태에 대한 자세한 내용은 "Grandmaster clock class sync state reference" 문서를 참조하십시오.

T-GM 클록은 `로컬MaxHoldoverOffSet 및 LocalHoldover Timeout` 매개 변수를 사용하여 기울기를 계산합니다. 슬로프는 시간 경과에 따라 단계 오프셋이 변경되는 비율입니다. 이는 초당 나노초 단위로 측정되며, 여기서 set 값은 지정된 기간 동안 오프셋이 얼마나 증가했는지를 나타냅니다.

T-GM 클록은 슬로프 값을 사용하여 시간 변동을 예측 및 보완하여 홀드 중에 타이밍 중단을 줄입니다. T-GM 클록은 슬로프를 계산하기 위해 다음 공식을 사용합니다.

Slope = `localMaxHoldoverOffSet` / `localHoldoverTimeout`

예를 들어 `LocalHoldOverTimeout` 매개변수가 60초로 설정되고 `LocalMaxHoldoverOffset` 매개변수가 3000 나노초로 설정된 경우 슬로프는 다음과 같이 계산됩니다.

기울기 = 3000 나노초 / 60 초 = 초당 50 나노초

T-GM 클록은 60초 내에 최대 오프셋에 도달합니다.

참고

단계 오프셋은 picoseconds에서 나노초로 변환됩니다. 결과적으로 홀드오버 중 계산된 단계 오프셋은 나노초로 표시되고 결과 슬로프는 초당 나노초 단위로 표시됩니다.

다음 그림은 GNSS를 소스로 사용하여 T-GM 클록의 홀드오버 동작을 보여줍니다.

그림 7.5. GNSS를 소스로 사용하는 T-GM 클록의 홀드오버

GNSS 신호가 손실되어 T-GM 시계가 `HOLDOVER` 모드로 전환됩니다. T-GM 클록은 내부 시계를 사용하여 시간 정확성을 유지합니다.

GNSS 신호가 복원되고 T-GM 클럭이 `LOCKED` 모드를 다시 입력합니다. GNSS 신호가 복원되면 `ts2phc` offset, digital phase-locked loop (DPLL) 단계 오프셋, GNSS 오프셋과 같은 동기화 체인의 모든 종속 구성 요소만 T-GM 클럭을 다시 입력하고 GNSS 오프셋에 도달합니다.

GNSS 신호가 다시 손실되고 T-GM 클럭이 `HOLDOVER` 모드로 다시 들어갑니다. 시간 오류가 증가하기 시작합니다.

시간 오류는 추적 기능의 긴 손실로 인해 `MaxInSpecOffset` 임계값을 초과합니다.

GNSS 신호가 복원되고 T-GM 클럭이 동기화를 재개합니다. 시간 오류가 줄어들기 시작합니다.

시간 오류는 `MaxInSpecOffset` 임계값 내에 감소하고 대체합니다.

#### 7.2.7. 경계 클럭 및 시간 슬레이브 클록에 대한 보조 유지 관리 적용

지원되지 않은 홀드오버 기능을 사용하면 PTP 경계 클럭(T-BC) 또는 PTP 시간 슬레이브 클럭(T-TSC)으로 구성된 Intel E810-XXVDA4T 네트워크 인터페이스 카드(NIC)를 사용하여 업스트림 타이밍 신호가 손실된 경우에도 정확한 시간 동기화를 유지할 수 있습니다.

이를 위해 NIC의 내부 오실레이터에 의존하여 안정적인 제어 드리프트 상태를 전환할 수 있습니다.

`ts2phc` 서비스는 타이밍 수신자(TR) 포트에 바인딩된 `ptp4l` 인스턴스를 모니터링합니다. 예를 들어 TR 포트가 시간 수신기로 작동을 중지하고 업스트림 할 마스터 클록 (T-GM)이 품질 또는 링크의 연결이 끊어지면 시스템이 홀드오버 모드로 전환되고 동적으로 재구성됩니다.

중요

T-BC 및 T-TSC에 대한 보조 홀더를 적용하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다.

따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

Intel E810-XXVDA4T NIC입니다.

프로세스

트리플 포트 T-BC NIC를 구성합니다. `PtpConfig` 리소스에는 시간 송신기 포트(00-tbc-tt) 및 모든 하드웨어, TR 포트, `ts2phc` 및 `phc2sys` 프로세스를 구성하는 두 개의 프로필이 포함되어 있습니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: t-bc
  namespace: openshift-ptp
spec:
  profile:
  - name: 00-tbc-tt
    ptp4lConf: |
      [ens4f0]
      masterOnly 1
      [ens8f0]
      masterOnly 1
      [ens1f0]
      masterOnly 1
      [global]
      #
      # Default Data Set
      #
      twoStepFlag 1
      slaveOnly 0
      priority1 128
      priority2 128
      domainNumber 25
      clockClass 248
      clockAccuracy 0xFE
      offsetScaledLogVariance 0xFFFF
      free_running 0
      freq_est_interval 1
      dscp_event 0
      dscp_general 0
      dataset_comparison G.8275.x
      G.8275.defaultDS.localPriority 128
      #
      # Port Data Set
      #
      logAnnounceInterval -3
      logSyncInterval -4
      logMinDelayReqInterval -4
      logMinPdelayReqInterval -4
      announceReceiptTimeout 3
      syncReceiptTimeout 0
      delayAsymmetry 0
      fault_reset_interval -4
      neighborPropDelayThresh 20000000
      masterOnly 0
      G.8275.portDS.localPriority 128
      #
      # Run time options
      #
      assume_two_step 0
      logging_level 6
      path_trace_enabled 0
      follow_up_info 0
      hybrid_e2e 0
      inhibit_multicast_service 0
      net_sync_monitor 0
      tc_spanning_tree 0
      tx_timestamp_timeout 50
      unicast_listen 0
      unicast_master_table 0
      unicast_req_duration 3600
      use_syslog 1
      verbose 0
      summary_interval 0
      kernel_leap 1
      check_fup_sync 0
      clock_class_threshold 135
      #
      # Servo Options
      #
      pi_proportional_const 0.60
      pi_integral_const 0.001
      pi_proportional_scale 0.0
      pi_proportional_exponent -0.3
      pi_proportional_norm_max 0.7
      pi_integral_scale 0.0
      pi_integral_exponent 0.4
      pi_integral_norm_max 0.3
      step_threshold 2.0
      first_step_threshold 0.00002
      max_frequency 900000000
      clock_servo pi
      sanity_freq_limit 200000000
      ntpshm_segment 0
      #
      # Transport options
      #
      transportSpecific 0x0
      ptp_dst_mac AA:BB:CC:DD:EE:FF
      p2p_dst_mac BB:CC:DD:EE:FF:GG
      udp_ttl 1
      udp6_scope 0x0E
      uds_address /var/run/ptp4l
      #
      # Default interface options
      #
      clock_type BC
      network_transport L2
      delay_mechanism E2E
      time_stamping hardware
      tsproc_mode filter
      delay_filter moving_median
      delay_filter_length 10
      egressLatency 0
      ingressLatency 0
      boundary_clock_jbod 1
      #
      # Clock description
      #
      productDescription ;;
      revisionData ;;
      manufacturerIdentity 00:00:00
      userDescription ;
      timeSource 0xA0
    ptp4lOpts: -2 --summary_interval -4
    ptpSchedulingPolicy: SCHED_FIFO
    ptpSchedulingPriority: 10
    ptpSettings:
      controllingProfile: 01-tbc-tr
      logReduce: "false"
  - name: 01-tbc-tr
    phc2sysOpts: -r -n 25 -N 8 -R 16 -u 0 -m -s ens4f1
    plugins:
      e810:
        enableDefaultConfig: false
        interconnections:
        - gnssInput: false
          id: ens4f0
          part: E810-XXVDA4T
          phaseOutputConnectors:
          - SMA1
          - SMA2
          upstreamPort: ens4f1
        - id: ens1f0
          inputConnector:
            connector: SMA1
          part: E810-XXVDA4T
        - id: ens8f0
          inputConnector:
            connector: SMA1
          part: E810-XXVDA4T
        pins:
          ens4f0:
            SMA1: 2 1
            SMA2: 2 2
            U.FL1: 0 1
            U.FL2: 0 2
          ens1f0:
            SMA1: 1 1
            SMA2: 0 2
            U.FL1: 0 1
            U.FL2: 0 2
          ens8f0:
            SMA1: 1 1
            SMA2: 0 2
            U.FL1: 0 1
            U.FL2: 0 2
        settings:
          LocalHoldoverTimeout: 14400
          LocalMaxHoldoverOffSet: 1500
          MaxInSpecOffset: 100
    ptp4lConf: |
      # The interface name is hardware-specific
      [ens4f1]
      masterOnly 0
      [global]
      #
      # Default Data Set
      #
      twoStepFlag 1
      slaveOnly 0
      priority1 128
      priority2 128
      domainNumber 25
      clockClass 248
      clockAccuracy 0xFE
      offsetScaledLogVariance 0xFFFF
      free_running 0
      freq_est_interval 1
      dscp_event 0
      dscp_general 0
      dataset_comparison G.8275.x
      G.8275.defaultDS.localPriority 128
      #
      # Port Data Set
      #
      logAnnounceInterval -3
      logSyncInterval -4
      logMinDelayReqInterval -4
      logMinPdelayReqInterval -4
      announceReceiptTimeout 3
      syncReceiptTimeout 0
      delayAsymmetry 0
      fault_reset_interval -4
      neighborPropDelayThresh 20000000
      masterOnly 0
      G.8275.portDS.localPriority 128
      #
      # Run time options
      #
      assume_two_step 0
      logging_level 6
      path_trace_enabled 0
      follow_up_info 0
      hybrid_e2e 0
      inhibit_multicast_service 0
      net_sync_monitor 0
      tc_spanning_tree 0
      tx_timestamp_timeout 50
      unicast_listen 0
      unicast_master_table 0
      unicast_req_duration 3600
      use_syslog 1
      verbose 0
      summary_interval 0
      kernel_leap 1
      check_fup_sync 0
      clock_class_threshold 135
      #
      # Servo Options
      #
      pi_proportional_const 0.60
      pi_integral_const 0.001
      pi_proportional_scale 0.0
      pi_proportional_exponent -0.3
      pi_proportional_norm_max 0.7
      pi_integral_scale 0.0
      pi_integral_exponent 0.4
      pi_integral_norm_max 0.3
      step_threshold 2.0
      first_step_threshold 0.00002
      max_frequency 900000000
      clock_servo pi
      sanity_freq_limit 200000000
      ntpshm_segment 0
      #
      # Transport options
      #
      transportSpecific 0x0
      ptp_dst_mac AA:BB:CC:DD:EE:HH
      p2p_dst_mac BB:CC:DD:EE:FF:II
      udp_ttl 1
      udp6_scope 0x0E
      uds_address /var/run/ptp4l
      #
      # Default interface options
      #
      clock_type OC
      network_transport L2
      delay_mechanism E2E
      time_stamping hardware
      tsproc_mode filter
      delay_filter moving_median
      delay_filter_length 10
      egressLatency 0
      ingressLatency 0
      boundary_clock_jbod 1
      #
      # Clock description
      #
      productDescription ;;
      revisionData ;;
      manufacturerIdentity 00:00:00
      userDescription ;
      timeSource 0xA0
    ptp4lOpts: -2 --summary_interval -4
    ptpSchedulingPolicy: SCHED_FIFO
    ptpSchedulingPriority: 10
    ptpSettings:
      inSyncConditionThreshold: "10"
      inSyncConditionTimes: "12"
      logReduce: "false"
    ts2phcConf: |
      [global]
      use_syslog  0
      verbose 1
      logging_level 7
      ts2phc.pulsewidth 100000000
      leapfile  /usr/share/zoneinfo/leap-seconds.list
      domainNumber 25
      uds_address /var/run/ptp4l.0.socket
      [ens4f0]
      ts2phc.extts_polarity rising
      ts2phc.extts_correction -10
      ts2phc.master 0
      [ens1f0]
      ts2phc.extts_polarity rising
      ts2phc.extts_correction -27
      ts2phc.master 0
      [ens8f0]
      ts2phc.extts_polarity rising
      ts2phc.extts_correction -27
      ts2phc.master 0
    ts2phcOpts: -s generic -a --ts2phc.rh_external_pps 1
  recommend:
  - match:
    - nodeLabel: node-role.kubernetes.io/master
    priority: 4
    profile: 00-tbc-tt
  - match:
    - nodeLabel: node-role.kubernetes.io/master
    priority: 4
    profile: 01-tbc-tr
```

1. 2

3. 모든 TT 포트는 `masterOnly` 를 1로 설정합니다.

4. TR 프로필의 `phc2sysOpts` 설정은 노드 시간 동기화의 소스로 업스트림 포트 `ens4f1` 을 지정합니다.

5. TR 프로필에는 하드웨어 플러그인 섹션이 포함되어 있습니다.

6. 하드웨어 플러그인의 상호 연결 섹션에는 `ens4f0`, `ens1f0` 및 `ens8f0` 의 세 개의 NIC가 있습니다. 주요 NIC `ens4f0` 은 `gnnsInput` 필드가 있고 `false` 로 설정된 유일한 NIC이며 TR 포트를 지정하는 `upstreamPort` 필드입니다.

또한 `단계OutputConnectors`, `SMA1` 및 `SMA2` 목록이 있습니다. 다음 NIC에는 `inputConnector` 필드가 있습니다.

T-BC 및 T-TSC 구성 모두에 대해 `upstreamPort: ens4f1` 인 시간 수신자 NIC `ens4f0` 및 특정 TR 포트를 설정합니다.

7. `ts2phc` 구성에는 업스트림 PTP 도메인의 `domainNumber` 가 포함되어 있습니다.

8. `ts2phc` 구성에는 `uds_address` 가 포함되어 있습니다. 데몬이 올바른 주소로 패치되므로 그 값은 중요하지 않습니다.

9. `ts2phc` 설정에는 이 설정에 참여하는 모든 NIC(`ens4f0, ens1f0` 및 `ens8f0`)가 포함되어야 합니다.

10. `ts2phcOpts`

`-s generic` 및 automatic with `-a` 를 사용하여 소스를 일반으로 설정합니다. 마지막 옵션인 `--ts2phc.rh_external_pps 1` 에서는 외부 단계 소스(DPLL)인 디지털 단계 잠금 루프(DPLL)로 작동하도록 구성합니다.

참고

단일 NIC 사례에서 모든 핀을 비활성화하거나 1PPS 측정에 사용하는 경우 출력을 활성화합니다.

참고

T-TSC 작업에 대한 이 구성을 렌더링하려면 `00-tbc-tt` 프로필을 제거하고 TR NIC만 나열하도록 `ts2phcConf` 섹션을 조정합니다.

검증

T-BC 상태를 가져오려면 다음 명령을 실행합니다.

```shell-session
$ oc -linuxptp-daemon-container logs ds/linuxptp-daemon --since=1s -f |grep T-BC
```

```shell-session
T-BC[1760525446]:[ts2phc.1.config] ens4f0 offset 1 T-BC-STATUS s2
T-BC[1760525447]:[ts2phc.1.config] ens4f0 offset 1 T-BC-STATUS s2
T-BC[1760525448]:[ts2phc.1.config] ens4f0 offset -1 T-BC-STATUS s2
```

이는 매 초에 보고되며, 여기서 `s2` 는 잠겼다는 것을 나타내며, `s1` 은 holdover가 활성화되고 `s0` 이 잠금 해제되었음을 나타냅니다.

추가 리소스

Grandmaster 클럭 클래스 동기화 상태 참조

#### 7.2.8. PTP grandmaster 클록에 대한 동적 윤초 처리 구성

PTP Operator 컨테이너 이미지에는 릴리스 시 사용할 수 있는 최신 `leap-seconds.list` 파일이 포함되어 있습니다. PTP Operator는 GPS(Global positioning System) 발표를 사용하여 윤초 파일을 자동으로 업데이트하도록 구성할 수 있습니다.

윤초 정보는 `openshift-ptp` 네임스페이스에 `leap-configmap` 이라는 자동으로 생성된 `ConfigMap` 리소스에 저장됩니다. PTP Operator는 `ts2phc` 프로세스에서 액세스할 수 있는 `linuxptp-daemon` Pod에 `leap-configmap` 리소스를 볼륨으로 마운트합니다.

GPS satellite에서 새 윤초 데이터를 브로드캐스트하는 경우 PTP Operator는 `leap-configmap` 리소스를 새 데이터로 업데이트합니다. `ts2phc` 프로세스는 변경 사항을 자동으로 선택합니다.

참고

다음 절차는 참조로 제공됩니다. PTP Operator의 4.20 버전은 기본적으로 자동 윤초 관리를 활성화합니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인했습니다.

PTP Operator를 설치하고 클러스터에 PTP 할 마스터 클럭 (T-GM)을 구성했습니다.

프로세스

`PtpConfig` CR의 `phc2sysOpts` 섹션에서 자동 윤초 처리를 구성합니다. 다음 옵션을 설정합니다.

```yaml
phc2sysOpts: -r -u 0 -m -N 8 -R 16 -S 2 -s ens2f0 -n 24
```

참고

이전에는 T-GM에서 과거 윤초를 고려하여 `phc2sys` 구성(`-O -37`)에 오프셋 조정이 필요했습니다. 더 이상 필요하지 않습니다.

`PtpConfig` CR의 `spec.profile.plugins.e810.ublxCmds` 섹션에서 GPS 수신자가 `NAV-TIMELS` 메시지의 정기 보고를 사용하도록 Intel e810 NIC를 구성합니다. 예를 들면 다음과 같습니다.

```yaml
- args: #ubxtool -P 29.20 -p CFG-MSG,1,38,248
    - "-P"
    - "29.20"
    - "-p"
    - "CFG-MSG,1,38,248"
```

검증

구성된 T-GM이 연결된 GPS에서 `NAV-TIMELS` 메시지를 수신하는지 확인합니다. 다음 명령을 실행합니다.

```shell-session
$ oc -n openshift-ptp -c linuxptp-daemon-container exec -it $(oc -n openshift-ptp get pods -o name | grep daemon) -- ubxtool -t -p NAV-TIMELS -P 29.20
```

```shell-session
1722509534.4417
UBX-NAV-STATUS:
  iTOW 384752000 gpsFix 5 flags 0xdd fixStat 0x0 flags2 0x8
  ttff 18261, msss 1367642864

1722509534.4419
UBX-NAV-TIMELS:
  iTOW 384752000 version 0 reserved2 0 0 0 srcOfCurrLs 2
  currLs 18 srcOfLsChange 2 lsChange 0 timeToLsEvent 70376866
  dateOfLsGpsWn 2441 dateOfLsGpsDn 7 reserved2 0 0 0
  valid x3

1722509534.4421
UBX-NAV-CLOCK:
  iTOW 384752000 clkB 784281 clkD 435 tAcc 3 fAcc 215

1722509535.4477
UBX-NAV-STATUS:
  iTOW 384753000 gpsFix 5 flags 0xdd fixStat 0x0 flags2 0x8
  ttff 18261, msss 1367643864

1722509535.4479
UBX-NAV-CLOCK:
  iTOW 384753000 clkB 784716 clkD 435 tAcc 3 fAcc 218
```

PTP Operator에서 `leap-configmap` 리소스가 성공적으로 생성되었으며 최신 버전의 leap-seconds.list 를 사용하여 최신 상태인지 확인합니다. 다음 명령을 실행합니다.

```shell-session
$ oc -n openshift-ptp get configmap leap-configmap -o jsonpath='{.data.<node_name>}'
```

1. 1

PTP T-GM 시계를 자동 윤초 관리로 설치 및 구성한 노드로 < `node_name` >을 바꿉니다. 노드 이름에 특수 문자를 이스케이프합니다. 예: `node-1\.example\.com`.

```shell-session
# Do not edit
# This file is generated automatically by linuxptp-daemon
#$  3913697179
#@  4291747200
2272060800     10    # 1 Jan 1972
2287785600     11    # 1 Jul 1972
2303683200     12    # 1 Jan 1973
2335219200     13    # 1 Jan 1974
2366755200     14    # 1 Jan 1975
2398291200     15    # 1 Jan 1976
2429913600     16    # 1 Jan 1977
2461449600     17    # 1 Jan 1978
2492985600     18    # 1 Jan 1979
2524521600     19    # 1 Jan 1980
2571782400     20    # 1 Jul 1981
2603318400     21    # 1 Jul 1982
2634854400     22    # 1 Jul 1983
2698012800     23    # 1 Jul 1985
2776982400     24    # 1 Jan 1988
2840140800     25    # 1 Jan 1990
2871676800     26    # 1 Jan 1991
2918937600     27    # 1 Jul 1992
2950473600     28    # 1 Jul 1993
2982009600     29    # 1 Jul 1994
3029443200     30    # 1 Jan 1996
3076704000     31    # 1 Jul 1997
3124137600     32    # 1 Jan 1999
3345062400     33    # 1 Jan 2006
3439756800     34    # 1 Jan 2009
3550089600     35    # 1 Jul 2012
3644697600     36    # 1 Jul 2015
3692217600     37    # 1 Jan 2017

#h  e65754d4 8f39962b aa854a61 661ef546 d2af0bfa
```

#### 7.2.9. linuxptp 서비스를 경계 클록으로 구성

`PtpConfig` CR(사용자 정의 리소스) 오브젝트를 생성하여 `linuxptp` 서비스(`ptp4l`, `phc2sys`)를 경계 클록으로 구성할 수 있습니다.

참고

다음 예제 `PtpConfig` CR을 기준으로 사용하여 `linuxptp` 서비스를 특정 하드웨어 및 환경의 경계 클록으로 구성합니다. 이 예제 CR에서는 PTP 빠른 이벤트를 구성하지 않습니다.

PTP 빠른 이벤트를 구성하려면 `ptp4lOpts`, `ptp4lConf` 및 `ptpClockThreshold` 에 적절한 값을 설정합니다. `ptpClockThreshold` 는 이벤트가 활성화된 경우에만 사용됩니다.

자세한 내용은 " PTP 빠른 이벤트 알림 게시자 구성"을 참조하십시오.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

다음 `PtpConfig` CR을 만든 다음 YAML을 `boundary-clock-ptp-config.yaml` 파일에 저장합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: boundary-clock
  namespace: openshift-ptp
  annotations: {}
spec:
  profile:
    - name: boundary-clock
      ptp4lOpts: "-2"
      phc2sysOpts: "-a -r -n 24"
      ptpSchedulingPolicy: SCHED_FIFO
      ptpSchedulingPriority: 10
      ptpSettings:
        logReduce: "true"
      ptp4lConf: |
        # The interface name is hardware-specific
        [$iface_slave]
        masterOnly 0
        [$iface_master_1]
        masterOnly 1
        [$iface_master_2]
        masterOnly 1
        [$iface_master_3]
        masterOnly 1
        [global]
        #
        # Default Data Set
        #
        twoStepFlag 1
        slaveOnly 0
        priority1 128
        priority2 128
        domainNumber 24
        #utc_offset 37
        clockClass 248
        clockAccuracy 0xFE
        offsetScaledLogVariance 0xFFFF
        free_running 0
        freq_est_interval 1
        dscp_event 0
        dscp_general 0
        dataset_comparison G.8275.x
        G.8275.defaultDS.localPriority 128
        #
        # Port Data Set
        #
        logAnnounceInterval -3
        logSyncInterval -4
        logMinDelayReqInterval -4
        logMinPdelayReqInterval -4
        announceReceiptTimeout 3
        syncReceiptTimeout 0
        delayAsymmetry 0
        fault_reset_interval -4
        neighborPropDelayThresh 20000000
        masterOnly 0
        G.8275.portDS.localPriority 128
        #
        # Run time options
        #
        assume_two_step 0
        logging_level 6
        path_trace_enabled 0
        follow_up_info 0
        hybrid_e2e 0
        inhibit_multicast_service 0
        net_sync_monitor 0
        tc_spanning_tree 0
        tx_timestamp_timeout 50
        unicast_listen 0
        unicast_master_table 0
        unicast_req_duration 3600
        use_syslog 1
        verbose 0
        summary_interval 0
        kernel_leap 1
        check_fup_sync 0
        clock_class_threshold 135
        #
        # Servo Options
        #
        pi_proportional_const 0.0
        pi_integral_const 0.0
        pi_proportional_scale 0.0
        pi_proportional_exponent -0.3
        pi_proportional_norm_max 0.7
        pi_integral_scale 0.0
        pi_integral_exponent 0.4
        pi_integral_norm_max 0.3
        step_threshold 2.0
        first_step_threshold 0.00002
        max_frequency 900000000
        clock_servo pi
        sanity_freq_limit 200000000
        ntpshm_segment 0
        #
        # Transport options
        #
        transportSpecific 0x0
        ptp_dst_mac 01:1B:19:00:00:00
        p2p_dst_mac 01:80:C2:00:00:0E
        udp_ttl 1
        udp6_scope 0x0E
        uds_address /var/run/ptp4l
        #
        # Default interface options
        #
        clock_type BC
        network_transport L2
        delay_mechanism E2E
        time_stamping hardware
        tsproc_mode filter
        delay_filter moving_median
        delay_filter_length 10
        egressLatency 0
        ingressLatency 0
        boundary_clock_jbod 0
        #
        # Clock description
        #
        productDescription ;;
        revisionData ;;
        manufacturerIdentity 00:00:00
        userDescription ;
        timeSource 0xA0
  recommend:
    - profile: boundary-clock
      priority: 4
      match:
        - nodeLabel: "node-role.kubernetes.io/$mcp"
```

| CR 필드 | 설명 |
| --- | --- |
| `name` | `PtpConfig` CR의 이름입니다. |
| `profile` | 하나 이상의 `profile` 오브젝트의 배열을 지정합니다. |
| `name` | 프로파일 오브젝트를 고유하게 식별하는 프로파일 오브젝트의 이름을 지정합니다. |
| `ptp4lOpts` | `ptp4l` 서비스에 대한 시스템 구성 옵션을 지정합니다. 옵션은 네트워크 인터페이스 이름과 서비스 구성 파일이 자동으로 추가되므로 네트워크 인터페이스 이름 `-i <interface>` 및 서비스 구성 파일 `-f /etc/ptp4l.conf` 를 포함하지 않아야 합니다. |
| `ptp4lConf` | `ptp4l` 을 경계 클록으로 시작하는 데 필요한 구성을 지정합니다. 예를 들어 `ens1f0` 은 그랜드 마스터 클록에서 동기화되고 `ens1f3` 은 연결된 장치를 동기화합니다. |
| `<interface_1>` | 동기화 시계를 수신하는 인터페이스입니다. |
| `<interface_2>` | 동기화 시계를 전송하는 인터페이스입니다. |
| `tx_timestamp_timeout` | Intel Columbiaville 800 시리즈 NIC의 경우 `tx_timestamp_timeout` 을 `50` 으로 설정합니다. |
| `boundary_clock_jbod` | Intel Columbiaville 800 시리즈 NIC의 경우 `boundary_clock_jbod` 가 `0` 으로 설정되어 있는지 확인합니다. Intel Fortville X710 시리즈 NIC의 경우 `boundary_clock_jbod` 가 `1` 로 설정되어 있는지 확인합니다. |
| `phc2sysOpts` | `phc2sys` 서비스에 대한 시스템 구성 옵션을 지정합니다. 이 필드가 비어 있으면 PTP Operator에서 `phc2sys` 서비스를 시작하지 않습니다. |
| `ptpSchedulingPolicy` | ptp4l 및 phc2sys 프로세스에 대한 스케줄링 정책. 기본값은 Cryo `stat_OTHER` 입니다. FIFO 스케줄링을 지원하는 시스템에서 Cryostat `_FIFO` 를 사용합니다. |
| `ptpSchedulingPriority` | `ptpSchedulingPolicy` 가 Cryostat `_FIFO` 로 설정된 경우 `ptp4l` 및 `phc2sys` 프로세스의 FIFO 우선 순위를 설정하는 데 사용되는 1-65의 정수 값입니다. `ptpSchedulingPolicy` 가 ptpSchedulingPolicy로 설정된 경우 `ptpSchedulingPriority` 필드는 사용되지 `않습니다` . |
| `ptpClockThreshold` | 선택 사항: `ptpClockThreshold` 가 없으면 `ptpClockThreshold` 필드에 기본값이 사용됩니다. `ptpClockThreshold` 는 PTP 이벤트가 트리거되기 전에 PTP 마스터 클록의 연결이 해제된 후의 시간을 구성합니다. `holdOverTimeout` 은 PTP 마스터 클록의 연결이 끊어지면 PTP 클럭 이벤트 상태가 Free `RUN` 으로 변경되기 전의 시간(초)입니다. `maxOffsetThreshold` 및 `minOffsetThreshold` 설정은 `CLOCK_REALTIME` ( `phc2sys` ) 또는 master 오프셋( `ptp4l` )의 값과 비교하는 오프셋 값을 나노초로 구성합니다. `ptp4l` 또는 `phc2sys` 오프셋 값이 이 범위를 벗어나는 경우 PTP 클럭 상태가 Free `RUN으로` 설정됩니다. 오프셋 값이 이 범위 내에 있으면 PTP 클럭 상태가 `LOCKED` 로 설정됩니다. |
| `권장` | `프로필` 을 노드에 적용하는 방법에 대한 규칙을 정의하는 하나 이상의 `recommend` 오브젝트 배열을 지정합니다. |
| `.recommend.profile` | profile 섹션에 정의된 `.recommend. profile` 오브젝트 이름을 지정합니다. |
| `.recommend.priority` | `0` 에서 `99` 사이의 정수 값으로 `priority` 를 지정합니다. 숫자가 클수록 우선순위가 낮으므로 우선순위 `99` 는 우선순위 `10` 보다 낮습니다. `match` 필드에 정의된 규칙에 따라 여러 프로필과 노드를 일치시킬 수 있는 경우 우선 순위가 높은 프로필이 해당 노드에 적용됩니다. |
| `.recommend.match` | `nodeLabel` 또는 `nodeName` 값을 사용하여 `.recommend.match` 규칙을 지정합니다. |
| `.recommend.match.nodeLabel` | `oc get nodes --show-labels` 명령을 사용하여 노드 오브젝트에서 `node.Labels` 필드의 `키로` `nodeLabel` 을 설정합니다. 예: `node-role.kubernetes.io/worker` . |
| `.recommend.match.nodeName` | `oc get nodes` 명령을 사용하여 노드 오브젝트의 `node.Name` 필드 값으로 `nodeName` 을 설정합니다. 예를 들면 `compute-1.example.com` 입니다. |

다음 명령을 실행하여 CR을 생성합니다.

```shell-session
$ oc create -f boundary-clock-ptp-config.yaml
```

검증

`PtpConfig` 프로필이 노드에 적용되었는지 확인합니다.

다음 명령을 실행하여 `openshift-ptp` 네임스페이스에서 Pod 목록을 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE   IP               NODE
linuxptp-daemon-4xkbb           1/1     Running   0          43m   10.1.196.24      compute-0.example.com
linuxptp-daemon-tdspf           1/1     Running   0          43m   10.1.196.25      compute-1.example.com
ptp-operator-657bbb64c8-2f8sj   1/1     Running   0          43m   10.129.0.61      control-plane-1.example.com
```

프로필이 올바른지 확인합니다. `PtpConfig` 프로필에 지정한 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다. 다음 명령을 실행합니다.

```shell-session
$ oc logs linuxptp-daemon-4xkbb -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
I1115 09:41:17.117596 4143292 daemon.go:107] in applyNodePTPProfile
I1115 09:41:17.117604 4143292 daemon.go:109] updating NodePTPProfile to:
I1115 09:41:17.117607 4143292 daemon.go:110] ------------------------------------
I1115 09:41:17.117612 4143292 daemon.go:102] Profile Name: profile1
I1115 09:41:17.117616 4143292 daemon.go:102] Interface:
I1115 09:41:17.117620 4143292 daemon.go:102] Ptp4lOpts: -2
I1115 09:41:17.117623 4143292 daemon.go:102] Phc2sysOpts: -a -r -n 24
I1115 09:41:17.117626 4143292 daemon.go:116] ------------------------------------
```

추가 리소스

PTP 하드웨어에 대한 FIFO 우선순위 스케줄링 구성

PTP 빠른 이벤트 알림 게시자 구성

#### 7.2.9.1. linuxptp 서비스를 듀얼 NIC 하드웨어의 경계 클럭으로 구성

각 NIC에 대해 `PtpConfig` CR(사용자 정의 리소스) 오브젝트를 생성하여 `linuxptp` 서비스(`ptp4l`, `phc2sys`)를 듀얼 NIC 하드웨어의 경계 클록으로 구성할 수 있습니다.

듀얼 NIC 하드웨어를 사용하면 각 NIC가 다운스트림 클록에 대해 별도의 `ptp4l` 인스턴스를 사용하여 각 NIC를 동일한 업스트림 리더 클록에 연결할 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

각 CR의 기준으로 "linuxptp 서비스를 경계 클록으로 구성"의 참조 CR을 사용하여 각 NIC에 대해 하나씩 두 개의 개별 `PtpConfig` CR을 생성합니다. 예를 들면 다음과 같습니다.

`phc2sysOpts`: 값을 지정하여 `boundary-clock-ptp-config-nic1.yaml` 을 생성합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: boundary-clock-ptp-config-nic1
  namespace: openshift-ptp
spec:
  profile:
  - name: "profile1"
    ptp4lOpts: "-2 --summary_interval -4"
    ptp4lConf: |
      [ens5f1]
      masterOnly 1
      [ens5f0]
      masterOnly 0
    ...
    phc2sysOpts: "-a -r -m -n 24 -N 8 -R 16"
```

1. `ptp4l` 을 경계 클록으로 시작하는 데 필요한 인터페이스를 지정합니다. 예를 들어 `ens5f0` 은 마스터 클록에서 동기화되고 `ens5f1` 은 연결된 장치를 동기화합니다.

2. 필수 `phc2sysOpts` 값. `-m` 은 메시지를 `stdout` 에 출력합니다. `linuxptp-daemon`

`DaemonSet` 은 로그를 구문 분석하고 Prometheus 지표를 생성합니다.

`boundary-clock-ptp-config-nic2.yaml` 을 생성하여 `phc2sysOpts` 필드를 완전히 제거하여 두 번째 NIC에 대한 `phc2sys` 서비스를 비활성화합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: boundary-clock-ptp-config-nic2
  namespace: openshift-ptp
spec:
  profile:
  - name: "profile2"
    ptp4lOpts: "-2 --summary_interval -4"
    ptp4lConf: |
      [ens7f1]
      masterOnly 1
      [ens7f0]
      masterOnly 0
...
```

1. `ptp4l` 을 두 번째 NIC에서 경계 클록으로 시작하는 데 필요한 인터페이스를 지정합니다.

참고

두 번째 NIC에서 `phc2sys` 서비스를 비활성화하려면 두 번째 `PtpConfig` CR에서 `phc2sys` 필드를 완전히 제거해야 합니다.

다음 명령을 실행하여 듀얼 NIC `PtpConfig` CR을 생성합니다.

첫 번째 NIC에 대해 PTP를 구성하는 CR을 생성합니다.

```shell-session
$ oc create -f boundary-clock-ptp-config-nic1.yaml
```

두 번째 NIC에 대해 PTP를 구성하는 CR을 생성합니다.

```shell-session
$ oc create -f boundary-clock-ptp-config-nic2.yaml
```

검증

PTP Operator가 두 NIC 모두에 `PtpConfig` CR을 적용했는지 확인합니다. 듀얼 NIC 하드웨어가 설치된 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다. 예를 들어 다음 명령을 실행합니다.

```shell-session
$ oc logs linuxptp-daemon-cvgr6 -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
ptp4l[80828.335]: [ptp4l.1.config] master offset          5 s2 freq   -5727 path delay       519
ptp4l[80828.343]: [ptp4l.0.config] master offset         -5 s2 freq  -10607 path delay       533
phc2sys[80828.390]: [ptp4l.0.config] CLOCK_REALTIME phc offset         1 s2 freq  -87239 delay    539
```

#### 7.2.9.2. 듀얼 NIC Intel E810 PTP 경계 클록의 고가용성 시스템 클럭으로 linuxptp 구성

이중 PTP 경계 클럭(T-BC)의 `linuxptp` 서비스 `ptp4l` 및 `phc2sys` 를 고가용성(HA) 시스템 클럭으로 구성할 수 있습니다.

고가용성 시스템 클록은 두 개의 경계 클럭으로 구성된 듀얼 NIC Intel E810 Salesm 채널 하드웨어의 여러 시간 소스를 사용합니다. 두 개의 경계 클럭 인스턴스가 HA 설정에 참여하며 각각 고유한 구성 프로필이 있습니다. 각 NIC에 대해 별도의 `ptp4l` 인스턴스를 사용하여 각 NIC를 동일한 업스트림 리더 클록에 연결합니다.

NIC를 T-BC로 구성하는 두 개의 `PtpConfig` CR(사용자 정의 리소스) 오브젝트와 두 NIC 간에 고가용성을 구성하는 세 번째 `PtpConfig` CR을 생성합니다.

중요

HA를 구성하는 `PtpConfig` CR에서 `phc2SysOpts` 옵션을 한 번 설정합니다. 두 NIC를 구성하는 `PtpConfig` CR의 `phc2sysOpts` 필드를 빈 문자열로 설정합니다. 이렇게 하면 두 프로필에 대해 개별 `phc2sys` 프로세스가 설정되지 않습니다.

세 번째 `PtpConfig` CR은 고가용성 시스템 클럭 서비스를 구성합니다. CR은 `ptp4l` 프로세스가 실행되지 않도록 `ptp4lOpts` 필드를 빈 문자열로 설정합니다.

CR은 `spec.profile.ptpSettings.haProfiles` 키 아래에 `ptp4l` 구성에 대한 프로필을 추가하고 해당 프로필의 커널 소켓 경로를 `phc2sys` 서비스에 전달합니다. `ptp4l` 오류가 발생하면 `phc2sys` 서비스가 백업 `ptp4l` 구성으로 전환됩니다.

기본 프로필이 다시 활성화되면 `phc2sys` 서비스가 원래 상태로 되돌아갑니다.

중요

HA를 구성하는 데 사용하는 세 가지 `PtpConfig` CR 모두에 대해 `spec.recommend.priority` 를 동일한 값으로 설정해야 합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

Intel E810 Salem 채널 듀얼 NIC로 클러스터 노드를 구성합니다.

프로세스

각 CR에 대한 참조로 "linuxptp 서비스를 경계 클록으로 구성"의 CR을 사용하여 각 NIC에 대해 하나씩 두 개의 개별 `PtpConfig` CR을 생성합니다.

`phc2sysOpts` 필드에 빈 문자열을 지정하여 `ha-ptp-config-nic1.yaml` 파일을 생성합니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: ha-ptp-config-nic1
  namespace: openshift-ptp
spec:
  profile:
  - name: "ha-ptp-config-profile1"
    ptp4lOpts: "-2 --summary_interval -4"
    ptp4lConf: |
      [ens5f1]
      masterOnly 1
      [ens5f0]
      masterOnly 0
    #...
    phc2sysOpts: ""
```

1. `ptp4l` 을 경계 클록으로 시작하는 데 필요한 인터페이스를 지정합니다. 예를 들어 `ens5f0` 은 마스터 클록에서 동기화되고 `ens5f1` 은 연결된 장치를 동기화합니다.

2. 빈 문자열로 `phc2sysOpts` 를 설정합니다. 이러한 값은 고가용성을 구성하는 `PtpConfig` CR의 `spec.profile.ptpSettings.haProfiles` 필드에서 채워집니다.

다음 명령을 실행하여 NIC 1에 대해 `PtpConfig` CR을 적용합니다.

```shell-session
$ oc create -f ha-ptp-config-nic1.yaml
```

`phc2sysOpts` 필드에 빈 문자열을 지정하여 `ha-ptp-config-nic2.yaml` 파일을 생성합니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: ha-ptp-config-nic2
  namespace: openshift-ptp
spec:
  profile:
  - name: "ha-ptp-config-profile2"
    ptp4lOpts: "-2 --summary_interval -4"
    ptp4lConf: |
      [ens7f1]
      masterOnly 1
      [ens7f0]
      masterOnly 0
    #...
    phc2sysOpts: ""
```

다음 명령을 실행하여 NIC 2에 대해 `PtpConfig` CR을 적용합니다.

```shell-session
$ oc create -f ha-ptp-config-nic2.yaml
```

HA 시스템 시계를 구성하는 `PtpConfig` CR을 생성합니다. 예를 들면 다음과 같습니다.

`ptp-config-for-ha.yaml` 파일을 생성합니다. 두 NIC를 구성하는 `PtpConfig` CR에 설정된 `metadata.name` 필드와 일치하도록 `haProfiles` 를 설정합니다. 예: `haProfiles: ha-ptp-config-nic1,ha-ptp-config-nic2`

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: boundary-ha
  namespace: openshift-ptp
  annotations: {}
spec:
  profile:
    - name: "boundary-ha"
      ptp4lOpts: ""
      phc2sysOpts: "-a -r -n 24"
      ptpSchedulingPolicy: SCHED_FIFO
      ptpSchedulingPriority: 10
      ptpSettings:
        logReduce: "true"
        haProfiles: "$profile1,$profile2"
  recommend:
    - profile: "boundary-ha"
      priority: 4
      match:
        - nodeLabel: "node-role.kubernetes.io/$mcp"
```

1. `ptp4lOpts` 필드를 빈 문자열로 설정합니다. 비어 있지 않으면 `p4ptl` 프로세스가 중요한 오류로 시작됩니다.

중요

개별 NIC를 구성하는 `PtpConfig` CR 전에 고가용성 `PtpConfig` CR을 적용하지 마십시오.

다음 명령을 실행하여 HA `PtpConfig` CR을 적용합니다.

```shell-session
$ oc create -f ptp-config-for-ha.yaml
```

검증

PTP Operator에서 `PtpConfig` CR을 올바르게 적용했는지 확인합니다. 다음 단계를 수행합니다.

다음 명령을 실행하여 `openshift-ptp` 네임스페이스에서 Pod 목록을 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE   IP               NODE
linuxptp-daemon-4xkrb           1/1     Running   0          43m   10.1.196.24      compute-0.example.com
ptp-operator-657bbq64c8-2f8sj   1/1     Running   0          43m   10.129.0.61      control-plane-1.example.com
```

참고

`linuxptp-daemon` Pod가 하나만 있어야 합니다.

다음 명령을 실행하여 프로필이 올바른지 확인합니다. `PtpConfig` 프로필에 지정한 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다.

```shell-session
$ oc logs linuxptp-daemon-4xkrb -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
I1115 09:41:17.117596 4143292 daemon.go:107] in applyNodePTPProfile
I1115 09:41:17.117604 4143292 daemon.go:109] updating NodePTPProfile to:
I1115 09:41:17.117607 4143292 daemon.go:110] ------------------------------------
I1115 09:41:17.117612 4143292 daemon.go:102] Profile Name: ha-ptp-config-profile1
I1115 09:41:17.117616 4143292 daemon.go:102] Interface:
I1115 09:41:17.117620 4143292 daemon.go:102] Ptp4lOpts: -2
I1115 09:41:17.117623 4143292 daemon.go:102] Phc2sysOpts: -a -r -n 24
I1115 09:41:17.117626 4143292 daemon.go:116] ------------------------------------
```

#### 7.2.10. linuxptp 서비스를 일반 클록으로 구성

`PtpConfig` CR(사용자 정의 리소스) 오브젝트를 생성하여 `linuxptp` 서비스(`ptp4l`, `phc2sys`)를 일반 클록으로 구성할 수 있습니다.

참고

다음 예제 `PtpConfig` CR을 기반으로 `linuxptp` 서비스를 특정 하드웨어 및 환경의 일반 클록으로 구성합니다. 이 예제 CR에서는 PTP 빠른 이벤트를 구성하지 않습니다.

PTP 빠른 이벤트를 구성하려면 `ptp4lOpts`, `ptp4lConf` 및 `ptpClockThreshold` 에 적절한 값을 설정합니다. `ptpClockThreshold` 는 이벤트가 활성화된 경우에만 필요합니다.

자세한 내용은 " PTP 빠른 이벤트 알림 게시자 구성"을 참조하십시오.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

다음 `PtpConfig` CR을 생성한 다음 YAML을 `ordinary-clock-ptp-config.yaml` 파일에 저장합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: ordinary-clock
  namespace: openshift-ptp
  annotations: {}
spec:
  profile:
    - name: ordinary-clock
      # The interface name is hardware-specific
      interface: $interface
      ptp4lOpts: "-2 -s"
      phc2sysOpts: "-a -r -n 24"
      ptpSchedulingPolicy: SCHED_FIFO
      ptpSchedulingPriority: 10
      ptpSettings:
        logReduce: "true"
      ptp4lConf: |
        [global]
        #
        # Default Data Set
        #
        twoStepFlag 1
        slaveOnly 1
        priority1 128
        priority2 128
        domainNumber 24
        #utc_offset 37
        clockClass 255
        clockAccuracy 0xFE
        offsetScaledLogVariance 0xFFFF
        free_running 0
        freq_est_interval 1
        dscp_event 0
        dscp_general 0
        dataset_comparison G.8275.x
        G.8275.defaultDS.localPriority 128
        #
        # Port Data Set
        #
        logAnnounceInterval -3
        logSyncInterval -4
        logMinDelayReqInterval -4
        logMinPdelayReqInterval -4
        announceReceiptTimeout 3
        syncReceiptTimeout 0
        delayAsymmetry 0
        fault_reset_interval -4
        neighborPropDelayThresh 20000000
        masterOnly 0
        G.8275.portDS.localPriority 128
        #
        # Run time options
        #
        assume_two_step 0
        logging_level 6
        path_trace_enabled 0
        follow_up_info 0
        hybrid_e2e 0
        inhibit_multicast_service 0
        net_sync_monitor 0
        tc_spanning_tree 0
        tx_timestamp_timeout 50
        unicast_listen 0
        unicast_master_table 0
        unicast_req_duration 3600
        use_syslog 1
        verbose 0
        summary_interval 0
        kernel_leap 1
        check_fup_sync 0
        clock_class_threshold 7
        #
        # Servo Options
        #
        pi_proportional_const 0.0
        pi_integral_const 0.0
        pi_proportional_scale 0.0
        pi_proportional_exponent -0.3
        pi_proportional_norm_max 0.7
        pi_integral_scale 0.0
        pi_integral_exponent 0.4
        pi_integral_norm_max 0.3
        step_threshold 2.0
        first_step_threshold 0.00002
        max_frequency 900000000
        clock_servo pi
        sanity_freq_limit 200000000
        ntpshm_segment 0
        #
        # Transport options
        #
        transportSpecific 0x0
        ptp_dst_mac 01:1B:19:00:00:00
        p2p_dst_mac 01:80:C2:00:00:0E
        udp_ttl 1
        udp6_scope 0x0E
        uds_address /var/run/ptp4l
        #
        # Default interface options
        #
        clock_type OC
        network_transport L2
        delay_mechanism E2E
        time_stamping hardware
        tsproc_mode filter
        delay_filter moving_median
        delay_filter_length 10
        egressLatency 0
        ingressLatency 0
        boundary_clock_jbod 0
        #
        # Clock description
        #
        productDescription ;;
        revisionData ;;
        manufacturerIdentity 00:00:00
        userDescription ;
        timeSource 0xA0
  recommend:
    - profile: ordinary-clock
      priority: 4
      match:
        - nodeLabel: "node-role.kubernetes.io/$mcp"
```

| CR 필드 | 설명 |
| --- | --- |
| `name` | `PtpConfig` CR의 이름입니다. |
| `profile` | 하나 이상의 `profile` 오브젝트의 배열을 지정합니다. 각 프로필의 이름은 고유해야 합니다. |
| `인터페이스` | `ptp4l` 서비스에서 사용할 네트워크 인터페이스를 지정합니다(예: `ens787f1` ). |
| `ptp4lOpts` | `ptp4l` 서비스에 대한 시스템 구성 옵션을 지정합니다(예: `-` 2)는 IEEE 802.3 네트워크 전송을 선택합니다. 옵션은 네트워크 인터페이스 이름과 서비스 구성 파일이 자동으로 추가되므로 네트워크 인터페이스 이름 `-i <interface>` 및 서비스 구성 파일 `-f /etc/ptp4l.conf` 를 포함하지 않아야 합니다. 이 인터페이스에서 PTP 빠른 이벤트를 사용하려면 `--summary_interval -4` 를 추가합니다. |
| `phc2sysOpts` | `phc2sys` 서비스에 대한 시스템 구성 옵션을 지정합니다. 이 필드가 비어 있으면 PTP Operator에서 `phc2sys` 서비스를 시작하지 않습니다. Intel Columbiaville 800 시리즈 NIC의 경우 `phc2sysOpts` 옵션을 `-a -r -m -n 24 -N 8 -R 16` 으로 설정합니다. `-m` 은 메시지를 `stdout` 에 출력합니다. `linuxptp-daemon` `DaemonSet` 은 로그를 구문 분석하고 Prometheus 지표를 생성합니다. |
| `ptp4lConf` | 기본 `/etc/ptp4l.conf` 파일을 대체할 구성이 포함된 문자열을 지정합니다. 기본 구성을 사용하려면 필드를 비워 둡니다. |
| `tx_timestamp_timeout` | Intel Columbiaville 800 시리즈 NIC의 경우 `tx_timestamp_timeout` 을 `50` 으로 설정합니다. |
| `boundary_clock_jbod` | Intel Columbiaville 800 시리즈 NIC의 경우 `boundary_clock_jbod` 를 `0` 으로 설정합니다. |
| `ptpSchedulingPolicy` | `ptp4l` 및 `phc2sys` 프로세스에 대한 스케줄링 정책. 기본값은 Cryo `stat_OTHER` 입니다. FIFO 스케줄링을 지원하는 시스템에서 Cryostat `_FIFO` 를 사용합니다. |
| `ptpSchedulingPriority` | `ptpSchedulingPolicy` 가 Cryostat `_FIFO` 로 설정된 경우 `ptp4l` 및 `phc2sys` 프로세스의 FIFO 우선 순위를 설정하는 데 사용되는 1-65의 정수 값입니다. `ptpSchedulingPolicy` 가 ptpSchedulingPolicy로 설정된 경우 `ptpSchedulingPriority` 필드는 사용되지 `않습니다` . |
| `ptpClockThreshold` | 선택 사항: `ptpClockThreshold` 가 없으면 `ptpClockThreshold` 필드에 기본값이 사용됩니다. `ptpClockThreshold` 는 PTP 이벤트가 트리거되기 전에 PTP 마스터 클록의 연결이 해제된 후의 시간을 구성합니다. `holdOverTimeout` 은 PTP 마스터 클록의 연결이 끊어지면 PTP 클럭 이벤트 상태가 Free `RUN` 으로 변경되기 전의 시간(초)입니다. `maxOffsetThreshold` 및 `minOffsetThreshold` 설정은 `CLOCK_REALTIME` ( `phc2sys` ) 또는 master 오프셋( `ptp4l` )의 값과 비교하는 오프셋 값을 나노초로 구성합니다. `ptp4l` 또는 `phc2sys` 오프셋 값이 이 범위를 벗어나는 경우 PTP 클럭 상태가 Free `RUN으로` 설정됩니다. 오프셋 값이 이 범위 내에 있으면 PTP 클럭 상태가 `LOCKED` 로 설정됩니다. |
| `권장` | `프로필` 을 노드에 적용하는 방법에 대한 규칙을 정의하는 하나 이상의 `recommend` 오브젝트 배열을 지정합니다. |
| `.recommend.profile` | profile 섹션에 정의된 `.recommend. profile` 오브젝트 이름을 지정합니다. |
| `.recommend.priority` | 일반 클록의 경우 `.recommend.priority` 를 `0` 으로 설정합니다. |
| `.recommend.match` | `nodeLabel` 또는 `nodeName` 값을 사용하여 `.recommend.match` 규칙을 지정합니다. |
| `.recommend.match.nodeLabel` | `oc get nodes --show-labels` 명령을 사용하여 노드 오브젝트에서 `node.Labels` 필드의 `키로` `nodeLabel` 을 설정합니다. 예: `node-role.kubernetes.io/worker` . |
| `.recommend.match.nodeName` | `oc get nodes` 명령을 사용하여 노드 오브젝트의 `node.Name` 필드 값으로 `nodeName` 을 설정합니다. 예를 들면 `compute-1.example.com` 입니다. |

다음 명령을 실행하여 `PtpConfig` CR을 생성합니다.

```shell-session
$ oc create -f ordinary-clock-ptp-config.yaml
```

검증

`PtpConfig` 프로필이 노드에 적용되었는지 확인합니다.

다음 명령을 실행하여 `openshift-ptp` 네임스페이스에서 Pod 목록을 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE   IP               NODE
linuxptp-daemon-4xkbb           1/1     Running   0          43m   10.1.196.24      compute-0.example.com
linuxptp-daemon-tdspf           1/1     Running   0          43m   10.1.196.25      compute-1.example.com
ptp-operator-657bbb64c8-2f8sj   1/1     Running   0          43m   10.129.0.61      control-plane-1.example.com
```

프로필이 올바른지 확인합니다. `PtpConfig` 프로필에 지정한 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다. 다음 명령을 실행합니다.

```shell-session
$ oc logs linuxptp-daemon-4xkbb -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
I1115 09:41:17.117596 4143292 daemon.go:107] in applyNodePTPProfile
I1115 09:41:17.117604 4143292 daemon.go:109] updating NodePTPProfile to:
I1115 09:41:17.117607 4143292 daemon.go:110] ------------------------------------
I1115 09:41:17.117612 4143292 daemon.go:102] Profile Name: profile1
I1115 09:41:17.117616 4143292 daemon.go:102] Interface: ens787f1
I1115 09:41:17.117620 4143292 daemon.go:102] Ptp4lOpts: -2 -s
I1115 09:41:17.117623 4143292 daemon.go:102] Phc2sysOpts: -a -r -n 24
I1115 09:41:17.117626 4143292 daemon.go:116] ------------------------------------
```

추가 리소스

PTP 하드웨어에 대한 FIFO 우선순위 스케줄링 구성

PTP 빠른 이벤트 알림 게시자 구성

#### 7.2.10.1. Intel Columbiaville E800 시리즈 NIC를 PTP 일반 클럭 참조

다음 표에서는 Intel Columbiaville E800 시리즈 NIC를 일반 클록으로 사용하기 위해 참조 PTP 구성에 대해 설명합니다. 클러스터에 적용하는 `PtpConfig` CR(사용자 정의 리소스)을 변경합니다.

| PTP 구성 | 권장 설정 |
| --- | --- |
| `phc2sysOpts` | `-a -r -m -n 24 -N 8 -R 16` |
| `tx_timestamp_timeout` | `50` |
| `boundary_clock_jbod` | `0` |

참고

`phc2sysOpts` 의 경우 `-m` 은 메시지를 `stdout` 에 출력합니다. `linuxptp-daemon`

`DaemonSet` 은 로그를 구문 분석하고 Prometheus 지표를 생성합니다.

#### 7.2.10.2. 이중 포트 NIC 중복성을 사용하여 linuxptp 서비스를 일반 클록으로 구성

`PtpConfig` CR(사용자 정의 리소스) 오브젝트를 생성하여 `linuxptp` 서비스(`ptp4l`, `phc2sys`)를 듀얼 포트 NIC 중복성을 사용하여 일반 클록으로 구성할 수 있습니다. 일반 클록에 대한 듀얼 포트 NIC 구성에서 하나의 포트가 실패하면 대기 포트를 인수하여 PTP 타이밍 동기화를 유지합니다.

중요

이중 포트 NIC 중복을 사용하는 일반 클록으로 linuxptp 서비스를 구성하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다.

따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

이중 포트 NIC를 중복성이 추가된 일반 클록으로 사용하기 위한 하드웨어 요구 사항을 확인합니다. 자세한 내용은 "다중 포트 NIC를 사용하여 PTP 일반 클록의 중복성 개선"을 참조하십시오.

프로세스

다음 `PtpConfig` CR을 생성한 다음 YAML을 파일에 저장합니다.

```shell
oc-dual-port-ptp-config.yaml
```

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: ordinary-clock-1
  namespace: openshift-ptp
spec:
  profile:
  - name: oc-dual-port
    phc2sysOpts: -a -r -n 24 -N 8 -R 16 -u 0
    ptp4lConf: |-
      [ens3f2]
      masterOnly 0
      [ens3f3]
      masterOnly 0

      [global]
      #
      # Default Data Set
      #
      slaveOnly 1
#...
```

1. `ptp4l` 서비스에 대한 시스템 구성 옵션을 지정합니다.

2. `ptp4l` 서비스의 인터페이스 구성을 지정합니다. 이 예에서 `ens3f2` 및 `ens3f3` 인터페이스에 대해 `masterOnly 0` 을 설정하면 `ens3` 인터페이스의 두 포트가 모두 리더 또는 후속 클록으로 실행될 수 있습니다.

`slaveOnly 1` 사양과 함께 이 구성은 하나의 포트가 활성 일반 클록으로 작동하고 다른 포트는 `Listening` 포트 상태에서 대기 일반 클록으로 작동합니다.

3. 일반 클록으로만 실행되도록 `ptp4l` 을 구성합니다.

다음 명령을 실행하여 `PtpConfig` CR을 생성합니다.

```shell-session
$ oc create -f oc-dual-port-ptp-config.yaml
```

검증

`PtpConfig` 프로필이 노드에 적용되었는지 확인합니다.

다음 명령을 실행하여 `openshift-ptp` 네임스페이스에서 Pod 목록을 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE   IP               NODE
linuxptp-daemon-4xkbb           1/1     Running   0          43m   10.1.196.24      compute-0.example.com
linuxptp-daemon-tdspf           1/1     Running   0          43m   10.1.196.25      compute-1.example.com
ptp-operator-657bbb64c8-2f8sj   1/1     Running   0          43m   10.129.0.61      control-plane-1.example.com
```

프로필이 올바른지 확인합니다. `PtpConfig` 프로필에 지정한 노드에 해당하는 `linuxptp` 데몬의 로그를 검사합니다. 다음 명령을 실행합니다.

```shell-session
$ oc logs linuxptp-daemon-4xkbb -n openshift-ptp -c linuxptp-daemon-container
```

```shell-session
I1115 09:41:17.117596 4143292 daemon.go:107] in applyNodePTPProfile
I1115 09:41:17.117604 4143292 daemon.go:109] updating NodePTPProfile to:
I1115 09:41:17.117607 4143292 daemon.go:110] ------------------------------------
I1115 09:41:17.117612 4143292 daemon.go:102] Profile Name: oc-dual-port
I1115 09:41:17.117616 4143292 daemon.go:102] Interface: ens787f1
I1115 09:41:17.117620 4143292 daemon.go:102] Ptp4lOpts: -2 --summary_interval -4
I1115 09:41:17.117623 4143292 daemon.go:102] Phc2sysOpts: -a -r -n 24 -N 8 -R 16 -u 0
I1115 09:41:17.117626 4143292 daemon.go:116] ------------------------------------
```

추가 리소스

PTP 빠른 이벤트를 사용하여 `linuxptp` 서비스를 일반 클록으로 구성하는 전체 예제 CR은 linuxptp 서비스를 일반 클록으로 구성을 참조하십시오.

듀얼 포트 NIC를 사용하여 PTP 일반 클록의 중복 개선

#### 7.2.11. PTP 하드웨어에 대한 FIFO 우선순위 스케줄링 구성

대기 시간이 짧은 통신 또는 기타 배포 유형에서는 PTP 데몬 스레드는 나머지 인프라 구성 요소와 함께 제한된 CPU 풋프린트에서 실행됩니다. 기본적으로 PTP 스레드는 Cryostat `_OTHER` 정책으로 실행됩니다. 로드가 높은 상태에서 이러한 스레드는 오류가 없는 작업에 필요한 스케줄링 대기 시간을 얻지 못할 수 있습니다.

잠재적인 스케줄링 대기 시간 오류를 완화하기 위해 PTP Operator `linuxptp` 서비스를 구성하여 스레드가 a Cryostat `_FIFO` 정책으로 실행되도록 할 수 있습니다.

`PtpConfig` CR에 대해 Cryostat `_FIFO` 가 설정된 경우 `ptp4l` 및 `phc2sys` 는 `PtpConfig` CR의 `ptpSchedulingPriority` 필드에 의해 설정된 우선순위를 가진 `chrt` 아래의 상위 컨테이너에서 실행됩니다.

참고

`ptpSchedulingPolicy` 설정은 선택 사항이며 대기 시간 오류가 발생하는 경우에만 필요합니다.

프로세스

`PtpConfig` CR 프로필을 편집합니다.

```shell-session
$ oc edit PtpConfig -n openshift-ptp
```

`ptpSchedulingPolicy` 및 `ptpSchedulingPriority` 필드를 변경합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: <ptp_config_name>
  namespace: openshift-ptp
...
spec:
  profile:
  - name: "profile1"
...
    ptpSchedulingPolicy: SCHED_FIFO
    ptpSchedulingPriority: 10
```

1. `ptp4l` 및 `phc2sys` 프로세스에 대한 스케줄링 정책. FIFO 스케줄링을 지원하는 시스템에서 Cryostat `_FIFO` 를 사용합니다.

2. 필수 항목입니다. `ptp4l` 및 `phc2sys` 프로세스의 FIFO 우선 순위를 구성하는 데 사용되는 정수 값 1-65를 설정합니다.

저장하고 종료하여 `PtpConfig` CR에 변경 사항을 적용합니다.

검증

`linuxptp-daemon` Pod의 이름과 `PtpConfig` CR이 적용된 해당 노드를 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE     IP            NODE
linuxptp-daemon-gmv2n           3/3     Running   0          1d17h   10.1.196.24   compute-0.example.com
linuxptp-daemon-lgm55           3/3     Running   0          1d17h   10.1.196.25   compute-1.example.com
ptp-operator-3r4dcvf7f4-zndk7   1/1     Running   0          1d7h    10.129.0.61   control-plane-1.example.com
```

업데이트된 `chrt` FIFO 우선 순위로 `ptp4l` 프로세스가 실행 중인지 확인합니다.

```shell-session
$ oc -n openshift-ptp logs linuxptp-daemon-lgm55 -c linuxptp-daemon-container|grep chrt
```

```shell-session
I1216 19:24:57.091872 1600715 daemon.go:285] /bin/chrt -f 65 /usr/sbin/ptp4l -f /var/run/ptp4l.0.config -2  --summary_interval -4 -m
```

#### 7.2.12. PTP 로그 감소 구성

`linuxptp-daemon` 은 디버깅을 위해 사용할 수 있는 로그를 생성합니다. 제한된 스토리지 용량을 제공하는 통신 또는 기타 배포 유형에서는 이러한 로그가 스토리지 요구에 추가할 수 있습니다. 현재 기본 로깅 속도가 높으므로 24시간 이내에 로그가 순환되어 변경 사항을 추적하고 문제를 식별하기가 어렵습니다.

마스터 오프셋 값을 보고하는 로그 메시지를 제외하도록 `PtpConfig` CR(사용자 정의 리소스)을 구성하여 기본 로그 감소를 얻을 수 있습니다. 마스터 오프셋 로그 메시지는 현재 노드의 클럭과 나노초의 마스터 클록 간의 차이를 보고합니다.

그러나 이 방법을 사용하면 필터링된 로그의 요약 상태가 없습니다. 향상된 로그 감소 기능을 사용하면 PTP 로그의 로깅 속도를 구성할 수 있습니다.

문제 해결에 필수 정보를 유지하면서 `linuxptp-daemon` 에서 생성한 로그 볼륨을 줄이는 데 도움이 되는 특정 로깅 속도를 설정할 수 있습니다. 향상된 로그 감소 기능을 사용하면 오프셋이 해당 임계값보다 높으면 여전히 오프셋 로그를 표시하는 임계값을 지정할 수도 있습니다.

#### 7.2.12.1. PTP에 대한 로그 필터링 구성

`PtpConfig` CR(사용자 정의 리소스)을 수정하여 기본 로그 필터링을 구성하고 master 오프셋 값을 보고하는 로그 메시지를 제외합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

`PtpConfig` CR을 편집합니다.

```shell-session
$ oc edit PtpConfig -n openshift-ptp
```

`spec.profile` 에서 `ptpSettings.logReduce` 사양을 추가하고 값을 `true` 로 설정합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: <ptp_config_name>
  namespace: openshift-ptp
...
spec:
  profile:
  - name: "profile1"
...
    ptpSettings:
      logReduce: "true"
```

참고

디버깅을 위해 이 사양을 `False` 로 되돌리고 마스터 오프셋 메시지를 포함할 수 있습니다.

저장하고 종료하여 `PtpConfig` CR에 변경 사항을 적용합니다.

검증

`linuxptp-daemon` Pod의 이름과 `PtpConfig` CR이 적용된 해당 노드를 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE     IP            NODE
linuxptp-daemon-gmv2n           3/3     Running   0          1d17h   10.1.196.24   compute-0.example.com
linuxptp-daemon-lgm55           3/3     Running   0          1d17h   10.1.196.25   compute-1.example.com
ptp-operator-3r4dcvf7f4-zndk7   1/1     Running   0          1d7h    10.129.0.61   control-plane-1.example.com
```

다음 명령을 실행하여 마스터 오프셋 메시지가 로그에서 제외되었는지 확인합니다.

```shell-session
$ oc -n openshift-ptp logs <linux_daemon_container> -c linuxptp-daemon-container | grep "master offset"
```

1. <linux_daemon_container>는 `linuxptp-daemon` Pod의 이름입니다(예: `linuxptp-daemon-gmv2n`).

`logReduce` 사양을 구성할 때 이 명령은 `linuxptp` 데몬의 로그에 `마스터 오프셋` 의 인스턴스를 보고하지 않습니다.

#### 7.2.12.2. 향상된 PTP 로그 감소 구성

기본 로그 감소는 자주 로그를 필터링합니다. 그러나 필터링된 로그를 정기적으로 요약하려면 향상된 로그 감소 기능을 사용합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP Operator를 설치합니다.

프로세스

`PtpConfig` CR(사용자 정의 리소스)을 편집합니다.

```shell-session
$ oc edit PtpConfig -n openshift-ptp
```

`spec.profile` 섹션에 `ptpSettings.logReduce` 사양을 추가하고 값을 `enhanced` 로 설정합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: <ptp_config_name>
  namespace: openshift-ptp
...
spec:
  profile:
  - name: "profile1"
...
    ptpSettings:
      logReduce: "enhanced"
```

선택 사항: 요약 로그의 간격과 마스터 오프셋 로그의 경우 나노초 단위의 임계값을 구성합니다. 예를 들어 간격을 60초로 설정하고 임계값을 100 나노초로 설정하려면 `spec.profile` 섹션에 `ptpSettings.logReduce` 사양을 추가하고 값을 `60s 100` 으로 설정합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: <ptp_config_name>
  namespace: openshift-ptp
spec:
  profile:
  - name: "profile1"
    ptpSettings:
      logReduce: "enhanced 60s 100"
```

1. 기본적으로 `linuxptp-daemon` 은 값이 지정되지 않은 경우 30초마다 요약 로그를 생성하도록 구성됩니다. 예제 구성에서 데몬은 60초마다 요약 로그를 생성하고 마스터 오프셋 로그에 대한 임계값이 100 나노초로 설정됩니다.

즉, 데몬은 지정된 간격으로 요약 로그만 생성합니다. 그러나 마스터의 클럭 오프셋이 더하기 또는 - 100 나노초를 초과하면 특정 로그 항목이 기록됩니다.

선택 사항: 마스터 오프셋 임계값 없이 간격을 설정하려면 `logReduce` 필드를 YAML `의 60` 으로 구성합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpConfig
metadata:
  name: <ptp_config_name>
  namespace: openshift-ptp
spec:
  profile:
  - name: "profile1"
    ptpSettings:
      logReduce: "enhanced 60s"
```

저장하고 종료하여 `PtpConfig` CR에 변경 사항을 적용합니다.

검증

다음 명령을 실행하여 `linuxptp-daemon` Pod의 이름과 `PtpConfig` CR이 적용되는 해당 노드를 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE     IP            NODE
linuxptp-daemon-gmv2n           3/3     Running   0          1d17h   10.1.196.24   compute-0.example.com
linuxptp-daemon-lgm55           3/3     Running   0          1d17h   10.1.196.25   compute-1.example.com
ptp-operator-3r4dcvf7f4-zndk7   1/1     Running   0          1d7h    10.129.0.61   control-plane-1.example.com
```

다음 명령을 실행하여 마스터 오프셋 메시지가 로그에서 제외되었는지 확인합니다.

```shell-session
$ oc -n openshift-ptp logs <linux_daemon_container> -c linuxptp-daemon-container | grep "master offset"
```

1. <linux_daemon_container>는 `linuxptp-daemon` Pod의 이름입니다(예: `linuxptp-daemon-gmv2n`).

#### 7.2.13. 일반적인 PTP Operator 문제 해결

다음 단계를 수행하여 PTP Operator의 일반적인 문제를 해결합니다.

사전 요구 사항

OpenShift Container Platform CLI ()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP를 지원하는 호스트가 있는 베어 메탈 클러스터에 PTP Operator를 설치합니다.

프로세스

구성된 노드를 위해 Operator 및 Operand가 클러스터에 성공적으로 배포되었는지 확인합니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE     IP            NODE
linuxptp-daemon-lmvgn           3/3     Running   0          4d17h   10.1.196.24   compute-0.example.com
linuxptp-daemon-qhfg7           3/3     Running   0          4d17h   10.1.196.25   compute-1.example.com
ptp-operator-6b8dcbf7f4-zndk7   1/1     Running   0          5d7h    10.129.0.61   control-plane-1.example.com
```

참고

PTP 빠른 이벤트 버스가 활성화되면 준비된 `linuxptp-daemon` Pod 수는 `3/3` 가 됩니다. PTP 빠른 이벤트 버스가 활성화되지 않으면 `2/2` 가 표시됩니다.

지원되는 하드웨어가 클러스터에 있는지 확인합니다.

```shell-session
$ oc -n openshift-ptp get nodeptpdevices.ptp.openshift.io
```

```shell-session
NAME                                  AGE
control-plane-0.example.com           10d
control-plane-1.example.com           10d
compute-0.example.com                 10d
compute-1.example.com                 10d
compute-2.example.com                 10d
```

노드에 사용 가능한 PTP 네트워크 인터페이스를 확인합니다.

```shell-session
$ oc -n openshift-ptp get nodeptpdevices.ptp.openshift.io <node_name> -o yaml
```

다음과 같습니다.

<node_name>

쿼리할 노드를 지정합니다 (예: `compute-0.example.com`).

```yaml
apiVersion: ptp.openshift.io/v1
kind: NodePtpDevice
metadata:
  creationTimestamp: "2021-09-14T16:52:33Z"
  generation: 1
  name: compute-0.example.com
  namespace: openshift-ptp
  resourceVersion: "177400"
  uid: 30413db0-4d8d-46da-9bef-737bacd548fd
spec: {}
status:
  devices:
  - name: eno1
  - name: eno2
  - name: eno3
  - name: eno4
  - name: enp5s0f0
  - name: enp5s0f1
```

해당 노드의 `linuxptp-daemon` Pod에 액세스하여 PTP 인터페이스가 기본 클록에 성공적으로 동기화되었는지 확인합니다.

다음 명령을 실행하여 `linuxptp-daemon` Pod의 이름과 문제를 해결하려는 해당 노드를 가져옵니다.

```shell-session
$ oc get pods -n openshift-ptp -o wide
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE     IP            NODE
linuxptp-daemon-lmvgn           3/3     Running   0          4d17h   10.1.196.24   compute-0.example.com
linuxptp-daemon-qhfg7           3/3     Running   0          4d17h   10.1.196.25   compute-1.example.com
ptp-operator-6b8dcbf7f4-zndk7   1/1     Running   0          5d7h    10.129.0.61   control-plane-1.example.com
```

```shell-session
$ oc rsh -n openshift-ptp -c linuxptp-daemon-container <linux_daemon_container>
```

다음과 같습니다.

<linux_daemon_container>

진단할 컨테이너입니다 (예: `linuxptp-daemon-lmvgn`).

`linuxptp-daemon` 컨테이너에 대한 원격 쉘 연결에서 PTP 관리 클라이언트(`pmc`) 툴을 사용하여 네트워크 인터페이스를 진단합니다. 다음 `pmc` 명령을 실행하여 PTP 장치의 동기화 상태를 확인합니다(예: `ptp4l`).

```shell-session
# pmc -u -f /var/run/ptp4l.0.config -b 0 'GET PORT_DATA_SET'
```

```shell-session
sending: GET PORT_DATA_SET
    40a6b7.fffe.166ef0-1 seq 0 RESPONSE MANAGEMENT PORT_DATA_SET
        portIdentity            40a6b7.fffe.166ef0-1
        portState               SLAVE
        logMinDelayReqInterval  -4
        peerMeanPathDelay       0
        logAnnounceInterval     -3
        announceReceiptTimeout  3
        logSyncInterval         -4
        delayMechanism          1
        logMinPdelayReqInterval -4
        versionNumber           2
```

GNSS 소싱 할 마스터 클록의 경우 in-tree NIC 아이스크림 드라이버가 다음 명령을 실행하여 올바른지 확인합니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc rsh -n openshift-ptp -c linuxptp-daemon-container linuxptp-daemon-74m2g ethtool -i ens7f0
```

```shell-session
driver: ice
version: 5.14.0-356.bz2232515.el9.x86_64
firmware-version: 4.20 0x8001778b 1.3346.0
```

GNSS 소싱된 마스터 클록의 경우 `linuxptp-daemon` 컨테이너가 GNSS radio에서 신호를 수신하고 있는지 확인합니다. 컨테이너가 GNSS 신호를 수신하지 않으면 `/dev/gnss0` 파일이 채워지지 않습니다. 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc rsh -n openshift-ptp -c linuxptp-daemon-container linuxptp-daemon-jnz6r cat /dev/gnss0
```

```shell-session
$GNRMC,125223.00,A,4233.24463,N,07126.64561,W,0.000,,300823,,,A,V*0A
$GNVTG,,T,,M,0.000,N,0.000,K,A*3D
$GNGGA,125223.00,4233.24463,N,07126.64561,W,1,12,99.99,98.6,M,-33.1,M,,*7E
$GNGSA,A,3,25,17,19,11,12,06,05,04,09,20,,,99.99,99.99,99.99,1*37
$GPGSV,3,1,10,04,12,039,41,05,31,222,46,06,50,064,48,09,28,064,42,1*62
```

#### 7.2.14. Intel 800 시리즈 NIC에서 CGU의 DPLL 펌웨어 버전 가져오기

클러스터 노드에 디버그 쉘을 열고 NIC 하드웨어를 쿼리하여 Intel 800 시리즈 NIC에서 Clock Generation Unit (CGU)의 Clock Generation Unit (CGU)의 디지털 DPLL(phase-locked loop) 펌웨어 버전을 가져올 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인했습니다.

클러스터 호스트에 Intel 800 시리즈 NIC를 설치했습니다.

PTP를 지원하는 호스트를 사용하여 베어 메탈 클러스터에 PTP Operator를 설치했습니다.

프로세스

다음 명령을 실행하여 디버그 Pod를 시작합니다.

```shell-session
$ oc debug node/<node_name>
```

다음과 같습니다.

<node_name>

Intel 800 시리즈 NIC를 설치한 노드입니다.

`devlink` 툴과 NIC가 설치된 버스 및 장치 이름을 사용하여 NIC의 CGU 펌웨어 버전을 확인합니다. 예를 들어 다음 명령을 실행합니다.

```shell-session
sh-4.4# devlink dev info <bus_name>/<device_name> | grep cgu
```

다음과 같습니다.

<bus_name>

NIC가 설치된 버스입니다. 예: `pci`.

<device_name>

NIC 장치 이름입니다. 예를 들면 `0000:51:00.0` 입니다.

```shell-session
cgu.id 36
fw.cgu 8032.16973825.6021
```

1. CGU 하드웨어 버전 번호

2. CGU에서 실행되는 DPLL 펌웨어 버전입니다. 여기서 DPLL 펌웨어 버전은 `6201` 이고 DPLL 모델은 `8032` 입니다. 문자열 `16973825` 는 DPLL 펌웨어 버전의 바이너리 버전(`1.3.0.1`)의 단축 표현입니다.

참고

펌웨어 버전에는 버전 번호의 각 부분에 대해 선행 nibble 및 3 옥텟이 있습니다. 바이너리의 `16973825` 번호는 `0001 0000 0011 0000 0000 0001` 입니다. 바이너리 값을 사용하여 펌웨어 버전을 디코딩합니다. 예를 들면 다음과 같습니다.

| 바이너리 부분 | 10진수 값 |
| --- | --- |
| `0001` | 1 |
| `0000 0011` | 3 |
| `0000 0000` | 0 |
| `0000 0001` | 1 |

#### 7.2.15. PTP Operator 데이터 수집

아래 명령을 사용하여 PTP Operator와 관련된 기능 및 오브젝트를 포함하여 클러스터에 대한 정보를 수집할 수 있습니다.

```shell
oc adm must-gather
```

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

PTP Operator를 설치했습니다.

프로세스

`must-gather` 를 사용하여 PTP Operator 데이터를 수집하려면 PTP Operator `must-gather` 이미지를 지정해야 합니다.

```shell-session
$ oc adm must-gather --image=registry.redhat.io/openshift4/ptp-must-gather-rhel9:v4.20
```

### 7.3. REST API v2를 사용하여 PTP 이벤트 소비자 애플리케이션 개발

베어 메탈 클러스터 노드에서 PTP(Precision Time Protocol) 이벤트를 사용하는 소비자 애플리케이션을 개발할 때 별도의 애플리케이션 포드에 소비자 애플리케이션을 배포합니다. 소비자 애플리케이션은 PTP 이벤트 REST API v2를 사용하여 PTP 이벤트를 서브스크립션합니다.

참고

다음 정보는 PTP 이벤트를 사용하는 소비자 애플리케이션을 개발하기 위한 일반적인 지침을 제공합니다. 전체 이벤트 소비자 애플리케이션 예제는 이 정보의 범위를 벗어납니다.

추가 리소스

PTP 이벤트 REST API v2 참조

#### 7.3.1. PTP 빠른 이벤트 알림 프레임워크 정보

PTP(Precision Time Protocol) 빠른 이벤트 REST API v2를 사용하여 베어 메탈 클러스터 노드에서 생성하는 PTP 이벤트에 클러스터 애플리케이션을 서브스크립션합니다.

참고

빠른 이벤트 알림 프레임워크는 통신에 REST API를 사용합니다. PTP 이벤트 REST API v2는 O-RAN ALLIANCE 사양에서 사용할 수 있는 이벤트 소비자 4.0의 O-RAN O-Cloud 알림 API 사양

을 기반으로 합니다.

#### 7.3.2. PTP 이벤트 REST API v2를 사용하여 PTP 이벤트 검색

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/319_OpenShift_PTP_bare-metal_OCP_nodes_0323_4.17.png" alt="PTP 이벤트 생산자 REST API의 PTP 빠른 이벤트 사용 개요" kind="diagram" diagram_type="semantic_diagram"]
PTP 이벤트 생산자 REST API의 PTP 빠른 이벤트 사용 개요
[/FIGURE]

_Source: `advanced_networking.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Advanced_networking-ko-KR/images/ae8f8ceef9bfbe28b158ea6eeabe9118/319_OpenShift_PTP_bare-metal_OCP_nodes_0323_4.17.png`_


애플리케이션은 생산자 측 클라우드 이벤트 프록시 사이드카에서 O-RAN v4 호환 REST API를 사용하여 PTP 이벤트에 서브스크립션합니다. `cloud-event-proxy` 사이드카 컨테이너는 기본 애플리케이션의 리소스를 사용하지 않고 대기 시간 없이 기본 애플리케이션 컨테이너와 동일한 리소스에 액세스할 수 있습니다.

그림 7.6. PTP 이벤트 생산자 REST API v2의 PTP 빠른 이벤트 사용 개요

클러스터 호스트에서 이벤트가 생성됩니다.

PTP Operator 관리 Pod의 `linuxptp-daemon` 프로세스는 Kubernetes `DaemonSet` 로 실행되며 다양한 `linuxptp` 프로세스(`ptp4l`, `phc2sys`, 선택 사항으로 마스터 클록, `ts2phc`)를 관리합니다. `linuxptp-daemon` 은 이벤트를 UNIX 도메인 소켓에 전달합니다.

이벤트는 cloud-event-proxy 사이드카에 전달됩니다.

PTP 플러그인은 UNIX 도메인 소켓에서 이벤트를 읽고 PTP Operator 관리 Pod의 `cloud-event-proxy` 사이드카에 전달합니다. `cloud-event-proxy` 는 Kubernetes 인프라에서 대기 시간이 짧은 CNF(Cloud-Native Network Functions)로 이벤트를 제공합니다.

이벤트가 게시됨

PTP Operator 관리 Pod의 `cloud-event-proxy` 사이드카는 이벤트를 처리하고 PTP 이벤트 REST API v2를 사용하여 이벤트를 게시합니다.

소비자 애플리케이션은 서브스크립션을 요청하고 서브스크립션 이벤트를 수신

소비자 애플리케이션은 API 요청을 생산자 `cloud-event-proxy` 사이드카로 전송하여 PTP 이벤트 서브스크립션을 생성합니다. 서브스크립션하면 소비자 애플리케이션은 리소스 한정자에 지정된 주소를 수신 대기하고 PTP 이벤트를 수신하고 처리합니다.

#### 7.3.3. PTP 빠른 이벤트 알림 게시자 구성

클러스터에서 네트워크 인터페이스에 PTP 빠른 이벤트 알림을 사용하려면 PTP Operator `PtpOperatorConfig` CR(사용자 정의 리소스)에서 빠른 이벤트 게시자를 활성화하고 생성한 `PtpConfig` CR에서 `ptpClockThreshold` 값을 구성해야 합니다.

사전 요구 사항

OpenShift Container Platform CLI()를 설치했습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인했습니다.

PTP Operator를 설치했습니다.

프로세스

기본 PTP Operator 구성을 수정하여 PTP 빠른 이벤트를 활성화합니다.

다음 YAML을 `ptp-operatorconfig.yaml` 파일에 저장합니다.

```yaml
apiVersion: ptp.openshift.io/v1
kind: PtpOperatorConfig
metadata:
  name: default
  namespace: openshift-ptp
spec:
  daemonNodeSelector:
    node-role.kubernetes.io/worker: ""
  ptpEventConfig:
    enableEventPublisher: true
```

1. `enableEventPublisher` 를 `true` 로 설정하여 PTP 빠른 이벤트 알림을 활성화합니다.

`PtpOperatorConfig` CR을 업데이트합니다.

```shell-session
$ oc apply -f ptp-operatorconfig.yaml
```

PTP가 활성화된 인터페이스에 대한 `PtpConfig` CR(사용자 정의 리소스)을 생성하고 `ptpClockThreshold` 및 `ptp4lOpts` 에 필요한 값을 설정합니다. 다음 YAML은 `PtpConfig` CR에 설정해야 하는 필수 값을 보여줍니다.

```yaml
spec:
  profile:
  - name: "profile1"
    interface: "enp5s0f0"
    ptp4lOpts: "-2 -s --summary_interval -4"
    phc2sysOpts: "-a -r -m -n 24 -N 8 -R 16"
    ptp4lConf: ""
    ptpClockThreshold:
      holdOverTimeout: 5
      maxOffsetThreshold: 100
      minOffsetThreshold: -100
```

1. PTP 빠른 이벤트를 사용하려면 `--summary_interval -4` 를 추가합니다.

2. 필수 `phc2sysOpts` 값. `-m` 은 메시지를 `stdout` 에 출력합니다. `linuxptp-daemon`

`DaemonSet` 은 로그를 구문 분석하고 Prometheus 지표를 생성합니다.

3. 기본 `/etc/ptp4l.conf` 파일을 대체할 구성이 포함된 문자열을 지정합니다. 기본 구성을 사용하려면 필드를 비워 둡니다.

4. 선택 사항입니다. `ptpClockThreshold` 스탠자가 없으면 `ptpClockThreshold` 필드에 기본값이 사용됩니다.

스탠자는 기본 `ptpClockThreshold` 값을 표시합니다. `ptpClockThreshold` 값은 PTP 이벤트가 트리거되기 전에 PTP 마스터 클록의 연결이 해제된 후의 시간을 구성합니다.

`holdOverTimeout` 은 PTP 마스터 클록의 연결이 끊어지면 PTP 클럭 이벤트 상태가 Free `RUN` 으로 변경되기 전의 시간(초)입니다.

`maxOffsetThreshold` 및 `minOffsetThreshold` 설정은 `CLOCK_REALTIME` (`phc2sys`) 또는 master 오프셋(`ptp4l`)의 값과 비교하는 오프셋 값을 나노초로 구성합니다. `ptp4l` 또는 `phc2sys` 오프셋 값이 이 범위를 벗어나는 경우 PTP 클럭 상태가 Free `RUN으로` 설정됩니다.

오프셋 값이 이 범위 내에 있으면 PTP 클럭 상태가 `LOCKED` 로 설정됩니다.

추가 리소스

PTP 빠른 이벤트를 사용하여 `linuxptp` 서비스를 일반 클록으로 구성하는 전체 예제 CR은 linuxptp 서비스를 일반 클록으로 구성을 참조하십시오.

#### 7.3.4. PTP 이벤트 REST API v2 소비자 애플리케이션 참조

PTP 이벤트 소비자 애플리케이션에는 다음 기능이 필요합니다.

클라우드 기본 PTP 이벤트 JSON 페이로드를 수신하기 위해 `POST` 처리기로 실행되는 웹 서비스

PTP 이벤트 생산자를 구독하는 `createSubscription` 함수

PTP 이벤트 생산자의 현재 상태를 폴링하는 `getCurrentState` 함수

다음 예제 Go 스니펫에서는 다음 요구 사항을 보여줍니다.

```plaintext
func server() {
  http.HandleFunc("/event", getEvent)
  http.ListenAndServe(":9043", nil)
}

func getEvent(w http.ResponseWriter, req *http.Request) {
  defer req.Body.Close()
  bodyBytes, err := io.ReadAll(req.Body)
  if err != nil {
    log.Errorf("error reading event %v", err)
  }
  e := string(bodyBytes)
  if e != "" {
    processEvent(bodyBytes)
    log.Infof("received event %s", string(bodyBytes))
  }
  w.WriteHeader(http.StatusNoContent)
}
```

```plaintext
import (
"github.com/redhat-cne/sdk-go/pkg/pubsub"
"github.com/redhat-cne/sdk-go/pkg/types"
v1pubsub "github.com/redhat-cne/sdk-go/v1/pubsub"
)

// Subscribe to PTP events using v2 REST API
s1,_:=createsubscription("/cluster/node/<node_name>/sync/sync-status/sync-state")
s2,_:=createsubscription("/cluster/node/<node_name>/sync/ptp-status/lock-state")
s3,_:=createsubscription("/cluster/node/<node_name>/sync/gnss-status/gnss-sync-status")
s4,_:=createsubscription("/cluster/node/<node_name>/sync/sync-status/os-clock-sync-state")
s5,_:=createsubscription("/cluster/node/<node_name>/sync/ptp-status/clock-class")

// Create PTP event subscriptions POST
func createSubscription(resourceAddress string) (sub pubsub.PubSub, err error) {
  var status int
  apiPath := "/api/ocloudNotifications/v2/"
  localAPIAddr := "consumer-events-subscription-service.cloud-events.svc.cluster.local:9043" // vDU service API address
  apiAddr := "ptp-event-publisher-service-<node_name>.openshift-ptp.svc.cluster.local:9043"
  apiVersion := "2.0"

  subURL := &types.URI{URL: url.URL{Scheme: "http",
    Host: apiAddr
    Path: fmt.Sprintf("%s%s", apiPath, "subscriptions")}}
  endpointURL := &types.URI{URL: url.URL{Scheme: "http",
    Host: localAPIAddr,
    Path: "event"}}

  sub = v1pubsub.NewPubSub(endpointURL, resourceAddress, apiVersion)
  var subB []byte

  if subB, err = json.Marshal(&sub); err == nil {
    rc := restclient.New()
    if status, subB = rc.PostWithReturn(subURL, subB); status != http.StatusCreated {
      err = fmt.Errorf("error in subscription creation api at %s, returned status %d", subURL, status)
    } else {
      err = json.Unmarshal(subB, &sub)
    }
  } else {
    err = fmt.Errorf("failed to marshal subscription for %s", resourceAddress)
  }
  return
}
```

1. & `lt;node_name` >을 PTP 이벤트를 생성하는 노드의 FQDN으로 바꿉니다. 예를 들면 `compute-1.example.com` 입니다.

```plaintext
//Get PTP event state for the resource
func getCurrentState(resource string) {
  //Create publisher
  url := &types.URI{URL: url.URL{Scheme: "http",
    Host: "ptp-event-publisher-service-<node_name>.openshift-ptp.svc.cluster.local:9043",
    Path: fmt.SPrintf("/api/ocloudNotifications/v2/%s/CurrentState",resource}}
  rc := restclient.New()
  status, event := rc.Get(url)
  if status != http.StatusOK {
    log.Errorf("CurrentState:error %d from url %s, %s", status, url.String(), event)
  } else {
    log.Debugf("Got CurrentState: %s ", event)
  }
}
```

1. & `lt;node_name` >을 PTP 이벤트를 생성하는 노드의 FQDN으로 바꿉니다. 예를 들면 `compute-1.example.com` 입니다.

#### 7.3.5. PTP 이벤트 REST API v2를 사용하여 이벤트 소비자 배포 및 서비스 CR 참조

PTP 이벤트 REST API v2와 함께 사용할 PTP 이벤트 소비자 소비자 소비자 소비자 애플리케이션을 배포할 때 다음 예제 PTP 이벤트 소비자 CR(사용자 정의 리소스)을 참조로 사용합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cloud-events
  labels:
    security.openshift.io/scc.podSecurityLabelSync: "false"
    pod-security.kubernetes.io/audit: "privileged"
    pod-security.kubernetes.io/enforce: "privileged"
    pod-security.kubernetes.io/warn: "privileged"
    name: cloud-events
    openshift.io/cluster-monitoring: "true"
  annotations:
    workload.openshift.io/allowed: management
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloud-consumer-deployment
  namespace: cloud-events
  labels:
    app: consumer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: consumer
  template:
    metadata:
      annotations:
        target.workload.openshift.io/management: '{"effect": "PreferredDuringScheduling"}'
      labels:
        app: consumer
    spec:
      nodeSelector:
        node-role.kubernetes.io/worker: ""
      serviceAccountName: consumer-sa
      containers:
        - name: cloud-event-consumer
          image: cloud-event-consumer
          imagePullPolicy: Always
          args:
            - "--local-api-addr=consumer-events-subscription-service.cloud-events.svc.cluster.local:9043"
            - "--api-path=/api/ocloudNotifications/v2/"
            - "--http-event-publishers=ptp-event-publisher-service-NODE_NAME.openshift-ptp.svc.cluster.local:9043"
          env:
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: CONSUMER_TYPE
              value: "PTP"
            - name: ENABLE_STATUS_CHECK
              value: "true"
      volumes:
        - name: pubsubstore
          emptyDir: {}
```

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: consumer-sa
  namespace: cloud-events
```

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    prometheus.io/scrape: "true"
  name: consumer-events-subscription-service
  namespace: cloud-events
  labels:
    app: consumer-service
spec:
  ports:
    - name: sub-port
      port: 9043
  selector:
    app: consumer
  sessionAffinity: None
  type: ClusterIP
```

#### 7.3.6. REST API v2를 사용하여 PTP 이벤트 구독

`cloud-event-consumer` 애플리케이션 컨테이너를 배포하고 `cloud-event-consumer` 애플리케이션을 PTP Operator가 관리하는 Pod의 `cloud-event-proxy` 컨테이너에 게시한 PTP 이벤트에 등록합니다.

적절한 서브스크립션 요청 페이로드를 전달하여 `http://ptp-event-publisher-service-NODE_NAME.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2/subscriptions` 에 `POST` 요청을 전송하여 소비자 애플리케이션을 PTP 이벤트에 구독합니다.

참고

`9043` 은 PTP 이벤트 생산자 Pod에 배포된 `cloud-event-proxy` 컨테이너의 기본 포트입니다. 필요에 따라 애플리케이션에 대해 다른 포트를 구성할 수 있습니다.

추가 리소스

api/ocloudNotifications/v2/subscriptions

#### 7.3.7. PTP 이벤트 REST API v2 소비자 애플리케이션이 이벤트를 수신하고 있는지 확인

애플리케이션 Pod의 `cloud-event-consumer` 컨테이너에 PTP(Precision Time Protocol) 이벤트가 수신되는지 확인합니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인했습니다.

PTP Operator를 설치하고 구성했습니다.

클라우드 이벤트 애플리케이션 Pod 및 PTP 이벤트 소비자 애플리케이션을 배포했습니다.

프로세스

배포된 이벤트 소비자 애플리케이션의 로그를 확인합니다. 예를 들어 다음 명령을 실행합니다.

```shell-session
$ oc -n cloud-events logs -f deployment/cloud-consumer-deployment
```

```shell-session
time = "2024-09-02T13:49:01Z"
level = info msg = "transport host path is set to  ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043"
time = "2024-09-02T13:49:01Z"
level = info msg = "apiVersion=2.0, updated apiAddr=ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043, apiPath=/api/ocloudNotifications/v2/"
time = "2024-09-02T13:49:01Z"
level = info msg = "Starting local API listening to :9043"
time = "2024-09-02T13:49:06Z"
level = info msg = "transport host path is set to  ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043"
time = "2024-09-02T13:49:06Z"
level = info msg = "checking for rest service health"
time = "2024-09-02T13:49:06Z"
level = info msg = "health check http://ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2/health"
time = "2024-09-02T13:49:07Z"
level = info msg = "rest service returned healthy status"
time = "2024-09-02T13:49:07Z"
level = info msg = "healthy publisher; subscribing to events"
time = "2024-09-02T13:49:07Z"
level = info msg = "received event {\"specversion\":\"1.0\",\"id\":\"ab423275-f65d-4760-97af-5b0b846605e4\",\"source\":\"/sync/ptp-status/clock-class\",\"type\":\"event.sync.ptp-status.ptp-clock-class-change\",\"time\":\"2024-09-02T13:49:07.226494483Z\",\"data\":{\"version\":\"1.0\",\"values\":[{\"ResourceAddress\":\"/cluster/node/compute-1.example.com/ptp-not-set\",\"data_type\":\"metric\",\"value_type\":\"decimal64.3\",\"value\":\"0\"}]}}"
```

선택 사항입니다. `linuxptp-daemon` 배포에서 및 port-forwarding 포트 `9043` 을 사용하여 REST API를 테스트합니다. 예를 들어 다음 명령을 실행합니다.

```shell
oc
```

```shell-session
$ oc port-forward -n openshift-ptp ds/linuxptp-daemon 9043:9043
```

```shell-session
Forwarding from 127.0.0.1:9043 -> 9043
Forwarding from [::1]:9043 -> 9043
Handling connection for 9043
```

새 쉘 프롬프트를 열고 REST API v2 끝점을 테스트합니다.

```shell-session
$ curl -X GET http://localhost:9043/api/ocloudNotifications/v2/health
```

```shell-session
OK
```

#### 7.3.8. PTP 빠른 이벤트 메트릭 모니터링

`linuxptp-daemon` 이 실행 중인 클러스터 노드에서 PTP 빠른 이벤트 메트릭을 모니터링할 수 있습니다. 사전 구성 및 자체 업데이트 Prometheus 모니터링 스택을 사용하여 OpenShift Container Platform 웹 콘솔에서 PTP 빠른 이벤트 메트릭을 모니터링할 수도 있습니다.

사전 요구 사항

OpenShift Container Platform CLI 다음 명령을 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

PTP 가능 하드웨어를 사용하여 노드에 PTP Operator를 설치하고 구성합니다.

프로세스

다음 명령을 실행하여 노드의 디버그 Pod를 시작합니다.

```shell-session
$ oc debug node/<node_name>
```

`linuxptp-daemon` 컨테이너에서 노출하는 PTP 메트릭을 확인합니다. 예를 들어 다음 명령을 실행합니다.

```shell-session
sh-4.4# curl http://localhost:9091/metrics
```

```shell-session
# HELP cne_api_events_published Metric to get number of events published by the rest api
# TYPE cne_api_events_published gauge
cne_api_events_published{address="/cluster/node/compute-1.example.com/sync/gnss-status/gnss-sync-status",status="success"} 1
cne_api_events_published{address="/cluster/node/compute-1.example.com/sync/ptp-status/lock-state",status="success"} 94
cne_api_events_published{address="/cluster/node/compute-1.example.com/sync/ptp-status/class-change",status="success"} 18
cne_api_events_published{address="/cluster/node/compute-1.example.com/sync/sync-status/os-clock-sync-state",status="success"} 27
```

선택 사항입니다. `cloud-event-proxy` 컨테이너의 로그에서 PTP 이벤트를 찾을 수도 있습니다. 예를 들어 다음 명령을 실행합니다.

```shell-session
$ oc logs -f linuxptp-daemon-cvgr6 -n openshift-ptp -c cloud-event-proxy
```

OpenShift Container Platform 웹 콘솔에서 PTP 이벤트를 보려면 쿼리할 PTP 지표의 이름을 복사합니다(예: `openshift_ptp_offset_ns`).

OpenShift Container Platform 웹 콘솔에서 모니터링 → 메트릭 을 클릭합니다.

PTP 메트릭 이름을 표현식 필드에 붙여넣고 쿼리 실행을 클릭합니다.

추가 리소스

개발자로 메트릭 액세스

#### 7.3.9. PTP 빠른 이벤트 메트릭 참조

다음 표는 `linuxptp-daemon` 서비스가 실행 중인 클러스터 노드에서 사용할 수 있는 PTP 빠른 이벤트 메트릭을 설명합니다.

| 지표 | 설명 | 예 |
| --- | --- | --- |
| `openshift_ptp_clock_class` | 인터페이스의 PTP 클럭 클래스를 반환합니다. PTP 클럭 클래스에 대한 가능한 값은 6 ( `LOCKED` ), 7 ( `PRC UNLOCKED IN-SPEC` ), 52 ( `PRC UNLOCKED OUT-OF-SPEC` ), 187 ( `PRC UNLOCKED OUT-OF-SPEC` ), 135 ( `T-BC HOLDOVER IN-SPEC` )입니다. 165 (t `-BC HOLDOVER OUT-OF-SPEC` ), 248 ( `DEFAULT` ), 255 ( `SLAVE ONLY CLOCK` ) | `{node="compute-1.example.com",process="ptp4l"} 6` |
| `openshift_ptp_clock_state` | 인터페이스의 현재 PTP 클럭 상태를 반환합니다. PTP 클럭 상태에 사용 가능한 값은 free `RUN` , `LOCKED` 또는 `HOLDOVER` 입니다. | `{iface="CLOCK_REALTIME", node="compute-1.example.com", process="phc2sys"} 1` |
| `openshift_ptp_delay_ns` | 타이밍 패킷을 전송하는 기본 클록과 타이밍 패킷을 수신하는 보조 클럭 사이의 지연 나노초를 반환합니다. | `{from="master", iface="ens2fx", node="compute-1.example.com", process="ts2phc"} 0` |
| `openshift_ptp_ha_profile_status` | 다른 NIC에 여러 시간 소스가 있는 경우 고가용성 시스템 클록의 현재 상태를 반환합니다. 가능한 값은 0( `ACTIVE` ) 및 1( `ACTIVE` )입니다. | `{node="node1",process="phc2sys",profile="profile1"} 1` `{node="node1",process="phc2sys",profile2"} 0` |
| `openshift_ptp_frequency_adjustment_ns` | 2 PTP 클록 사이의 나노초 단위로 빈도 조정을 반환합니다. 예를 들어, 시스템 클럭과 NIC 사이의 업스트림 클럭과 NIC 사이 또는 PTP 하드웨어 클록 ( `phc` )과 NIC 사이입니다. | `{from="phc", iface="CLOCK_REALTIME", node="compute-1.example.com", process="phc2sys"} -6768` |
| `openshift_ptp_interface_role` | 인터페이스에 대해 구성된 PTP 클럭 역할을 반환합니다. 가능한 값은 0 ( `PASSIVE` ), 1 ( `SLAVE` ), 2 ( `MASTER` ), 3 (RFC `ULTY` ), 4 ( `UNKNOWN` ) 또는 5 ( `LISTENING` )입니다. | `{iface="ens2f0", node="compute-1.example.com", process="ptp4l"} 2` |
| `openshift_ptp_max_offset_ns` | 2 클럭 또는 인터페이스 사이의 나노초의 최대 오프셋을 반환합니다. 예를 들어 업스트림 GNSS 클록과 NIC( `ts2phc` ) 간에 또는 PTP 하드웨어 클록( `phc` )과 시스템 클럭( `phc2sys` ) 사이에 있습니다. | `{from="master", iface="ens2fx", node="compute-1.example.com", process="ts2phc"} 1.038099569e+09` |
| `openshift_ptp_offset_ns` | DPLL 클록 또는 GNSS 클록 소스와 NIC 하드웨어 클록 사이에 나노초 단위로 오프셋을 반환합니다. | `{from="phc", iface="CLOCK_REALTIME", node="compute-1.example.com", process="phc2sys"} -9` |
| `openshift_ptp_process_restart_count` | `ptp4l` 및 `ts2phc` 프로세스가 재시작된 횟수를 반환합니다. | `{config="ptp4l.0.config", node="compute-1.example.com",process="phc2sys"} 1` |
| `openshift_ptp_process_status` | PTP 프로세스가 실행 중인지 여부를 나타내는 상태 코드를 반환합니다. | `{config="ptp4l.0.config", node="compute-1.example.com",process="phc2sys"} 1` |
| `openshift_ptp_threshold` | `HoldOverTimeout` , `MaxOffsetThreshold` , `MinOffsetThreshold` 의 값을 반환합니다. `holdOverTimeout` 은 PTP 마스터 클록의 연결이 끊어지면 PTP 클럭 이벤트 상태가 Free `RUN` 으로 변경되기 전의 시간(초)입니다. `maxOffsetThreshold` 및 `minOffsetThreshold` 는 NIC의 `PtpConfig` CR에서 구성하는 `CLOCK_REALTIME` ( `phc2sys` ) 또는 마스터 오프셋( `ptp4l` ) 값과 비교하는 나노초의 오프셋 값입니다. | `{node="compute-1.example.com", profile="grandmaster", threshold="HoldOverTimeout"} 5` |

#### 7.3.9.1. T-GM이 활성화된 경우에만 PTP 빠른 이벤트 메트릭

다음 표에서는 PTP grandmaster 클럭(T-GM)이 활성화된 경우에만 사용할 수 있는 PTP 빠른 이벤트 메트릭을 설명합니다.

| 지표 | 설명 | 예 |
| --- | --- | --- |
| `openshift_ptp_frequency_status` | NIC에 대한 디지털 DPLL( phase-locked loop) 빈도의 현재 상태를 반환합니다. 가능한 값은 -1 ( `UNKNOWN` ), 0 ( `INVALID` ), 1 (free `RUN` ), 2 ( `LOCKED` ), 3 ( `LOCKED_HO_ACQ` ) 또는 4 ( `HOLDOVER` )입니다. | `{from="dpll",iface="ens2fx",node="compute-1.example.com",process="dpll"} 3` |
| `openshift_ptp_nmea_status` | NMEA 연결의 현재 상태를 반환합니다. NMEA는 1PPS NIC 연결에 사용되는 프로토콜입니다. 가능한 값은 0 ( `UNAVAILABLE` ) 및 1 ( `AVAILABLE` )입니다. | `{iface="ens2fx",node="compute-1.example.com",process="ts2phc"} 1` |
| `openshift_ptp_phase_status` | NIC의 DPLL 단계 상태를 반환합니다. 가능한 값은 -1 ( `UNKNOWN` ), 0 ( `INVALID` ), 1 (free `RUN` ), 2 ( `LOCKED` ), 3 ( `LOCKED_HO_ACQ` ) 또는 4 ( `HOLDOVER` )입니다. | `{from="dpll",iface="ens2fx",node="compute-1.example.com",process="dpll"} 3` |
| `openshift_ptp_pps_status` | NIC 1PPS 연결의 현재 상태를 반환합니다. 1PPS 연결을 사용하여 연결된 NIC 간에 타이밍을 동기화합니다. 가능한 값은 0 ( `UNAVAILABLE` ) 및 1 ( `AVAILABLE` )입니다. | `{from="dpll",iface="ens2fx",node="compute-1.example.com",process="dpll"} 1` |
| `openshift_ptp_gnss_status` | 글로벌 탐색 Satellite 시스템(GNSS) 연결의 현재 상태를 반환합니다. GNSS는 전 세계적으로 Satellite 기반 위치 지정, 탐색 및 타이밍 서비스를 제공합니다. 가능한 값은 0 ( `NOFIX` ), 1 ( `DEAD RECKONING 만` ), `2 (D-FIX` ), 3 ( `3D-FIX` ), 4 ( `GPS+DEAD RECKONING FIX` ), 5, ( `시간 만 FIX` ). | `{from="gnss",iface="ens2fx",node="compute-1.example.com",process="gnss"} 3` |

### 7.4. PTP 이벤트 REST API v2 참조

다음 REST API v2 끝점을 사용하여 `cloud-event-consumer` 애플리케이션을 PTP 이벤트 생산자 Pod에 게시한 PTP(Precision Time Protocol) 이벤트에 등록합니다.

`api/ocloudNotifications/v2/subscriptions`

`POST`: 새 서브스크립션을 생성합니다.

`GET`: 서브스크립션 목록 검색합니다.

`DELETE`: 모든 서브스크립션 삭제

`api/ocloudNotifications/v2/subscriptions/{subscription_id}`

`GET`: 지정된 서브스크립션 ID에 대한 세부 정보를 반환합니다.

`DELETE`: 지정된 서브스크립션 ID와 연결된 서브스크립션 삭제

`api/ocloudNotifications/v2/health`

`GET`: `ocloudNotifications` API의 상태를 반환합니다.

`api/ocloudNotifications/v2/publishers`

`GET`: 클러스터 노드의 PTP 이벤트 게시자 목록을 반환합니다.

`api/ocloudnotifications/v2/{resource_address}/CurrentState`

`GET`: `{resouce_address}` 에서 지정한 이벤트 유형의 현재 상태를 반환합니다.

#### HTTP 방법

`GET api/ocloudNotifications/v2/subscriptions`

#### 설명

서브스크립션 목록을 반환합니다. 서브스크립션이 존재하는 경우 `200 OK` 상태 코드가 서브스크립션 목록과 함께 반환됩니다.

```plaintext
[
 {
  "ResourceAddress": "/cluster/node/compute-1.example.com/sync/sync-status/os-clock-sync-state",
  "EndpointUri": "http://consumer-events-subscription-service.cloud-events.svc.cluster.local:9043/event",
  "SubscriptionId": "ccedbf08-3f96-4839-a0b6-2eb0401855ed",
  "UriLocation": "http://ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2/subscriptions/ccedbf08-3f96-4839-a0b6-2eb0401855ed"
 },
 {
  "ResourceAddress": "/cluster/node/compute-1.example.com/sync/ptp-status/clock-class",
  "EndpointUri": "http://consumer-events-subscription-service.cloud-events.svc.cluster.local:9043/event",
  "SubscriptionId": "a939a656-1b7d-4071-8cf1-f99af6e931f2",
  "UriLocation": "http://ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2/subscriptions/a939a656-1b7d-4071-8cf1-f99af6e931f2"
 },
 {
  "ResourceAddress": "/cluster/node/compute-1.example.com/sync/ptp-status/lock-state",
  "EndpointUri": "http://consumer-events-subscription-service.cloud-events.svc.cluster.local:9043/event",
  "SubscriptionId": "ba4564a3-4d9e-46c5-b118-591d3105473c",
  "UriLocation": "http://ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2/subscriptions/ba4564a3-4d9e-46c5-b118-591d3105473c"
 },
 {
  "ResourceAddress": "/cluster/node/compute-1.example.com/sync/gnss-status/gnss-sync-status",
  "EndpointUri": "http://consumer-events-subscription-service.cloud-events.svc.cluster.local:9043/event",
  "SubscriptionId": "ea0d772e-f00a-4889-98be-51635559b4fb",
  "UriLocation": "http://ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2/subscriptions/ea0d772e-f00a-4889-98be-51635559b4fb"
 },
 {
  "ResourceAddress": "/cluster/node/compute-1.example.com/sync/sync-status/sync-state",
  "EndpointUri": "http://consumer-events-subscription-service.cloud-events.svc.cluster.local:9043/event",
  "SubscriptionId": "762999bf-b4a0-4bad-abe8-66e646b65754",
  "UriLocation": "http://ptp-event-publisher-service-compute-1.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2/subscriptions/762999bf-b4a0-4bad-abe8-66e646b65754"
 }
]
```
