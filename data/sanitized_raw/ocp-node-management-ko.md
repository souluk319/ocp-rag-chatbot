<!-- source: ocp-node-management-ko.md -->

# OpenShift Container Platform (OCP) 노드 관리 가이드

## 1. 노드 개요: Master, Worker, Infra 노드 역할 구분

OpenShift Container Platform(OCP) 은 Kubernetes 기반의 기업용 컨테이너 플랫폼으로, 노드(Node) 는 클러스터의 실제 계산 및 저장 자원을 제공하는 물리적 또는 가상 머신입니다. OCP 는 노드의 역할을 명확히 구분하여 안정성과 보안성을 확보합니다.

*   **Master 노드**: 클러스터의 제어 평면(Control Plane) 을 호스팅합니다. API 서버, Scheduler, Controller Manager, etcd 등 핵심 컴포넌트를 포함하며, 사용자 요청을 처리하고 클러스터 상태를 관리합니다. 일반 Pod 은 Master 노드에 스케줄되지 않습니다 (System Pod 제외).
*   **Worker 노드**: 애플리케이션 Pod 를 실행하는 작업 노드입니다. 사용자의 워크로드가 배치되고, 계산 및 메모리 리소스를 제공합니다.
*   **Infra 노드**: 클러스터 인프라 서비스를 호스팅합니다. 로드밸런서, DNS, 네트워크 정책, 인증 서비스 등 클러스터 자체를 유지하기 위한 Pod 들이 실행됩니다.

이러한 역할 분리는 특정 워크로드가 제어 평면에 영향을 주거나, 인프라 서비스의 가용성이 애플리케이션에 의해 방해받지 않도록 보장합니다.

## 2. 노드 상태 확인 및 조건 해석

노드의 건강 상태를 확인하는 것은 운영의 기본입니다. `oc` 명령어를 사용하여 상세한 정보를 조회할 수 있습니다.

### 기본 조회 및 상세 정보
```bash
# 노드 목록 조회 (상태, 버전, 노드 이름 포함)
oc get nodes

# 특정 노드의 상세 정보 조회
oc describe node <node-name>
```

### 노드 조건 (Conditions) 해석
`oc describe node` 출력 결과의 'Conditions' 섹션은 노드의 현재 상태를 결정하는 핵심 지표입니다. 주요 조건은 다음과 같습니다.

| Condition | 상태 (Status) | 의미 | 조치 |
| :--- | :--- | :--- | : |
| **Ready** | `True` | 노드가 정상적으로 작동하며 Pod 스케줄링 가능 | 없음 |
| **Ready** | `False` | 노드에 문제가 발생하여 Pod 스케줄링 불가 | 로그 확인, 재부팅 또는 교체 |
| **MemoryPressure** | `False` | 메모리 여유 공간 충분 | - |
| **MemoryPressure** | `True` | 메모리가 부족하여 새로운 Pod 스케줄링 제한 | 메모리 누수 확인, 노드 확장 |
| **DiskPressure** | `False` | 디스크 공간 충분 | - |
| **DiskPressure** | `True` | 디스크 공간 부족 (일반적으로 /var/lib/kubelet) | 로그 삭제, 노드 확장 |
| **PIDPressure** | `False` | PID 공간 충분 | - |
| **PIDPressure** | `True` | 프로세스 ID 공간 부족 | 프로세스 종료, 노드 확장 |
| **NetworkUnavailable** | `False` | 네트워크 플러그인 정상 작동 | - |
| **NetworkUnavailable** | `True` | CNI 플러그인 오류로 네트워크 연결 불가 | 네트워크 정책, CNI 로그 확인 |

## 3. 노드 Drain: 안전한 워크로드 이식

노드를 유지보수하거나 교체하기 전에는 해당 노드에 실행 중인 Pod 들을 다른 노드로 이동 (Evict) 시켜야 합니다. 이를 **Drain** 이라고 합니다. OCP 는 `oc adm drain` 명령어를 제공합니다.

### 핵심 옵션 설명
*   `--ignore-daemonsets`: 데몬셋 (DaemonSet) Pod 는 각 노드마다 하나씩 실행되므로 강제로 제거할 수 없습니다. 이 옵션을 사용하여 데몬셋 Pod 는 제외하고 다른 Pod 만 이식합니다.
*   `--delete-emptydir-data`: `emptyDir` 볼륨을 사용하는 Pod 가 있다면, 데이터가 영구적으로 손실되지 않도록 주의해야 합니다. 이 옵션은 `emptyDir` 데이터가 포함된 Pod 를 강제로 제거 (Delete) 합니다.

### 명령어 예시
```bash
# drain 실행 (기본값: force=false, graceful=true)
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 강제 이식 (graceful=false)
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data --force
```
> **주의**: `--delete-emptydir-data` 옵션은 데이터 손실을 초래할 수 있으므로, 해당 볼륨에 중요한 데이터가 저장되어 있는지 반드시 확인해야 합니다.

## 4. Cordon/Uncordon: 스케줄링 제어

Drain 과 달리 Cordon 은 노드를 격리하지만 워크로드를 즉시 제거하지는 않습니다. 이는 노드가 고장 났을 때 Pod 가 해당 노드로 다시 스케줄되지 않도록 방지하는 데 유용합니다.

*   **Cordon**: 노드에 스케줄링을 비활성화합니다. 이미 있는 Pod 는 계속 실행되지만, 새로운 Pod 는 이 노드로 배치되지 않습니다.
*   **Uncordon**: 스케줄링을 다시 활성화하여 노드를 클러스터에 복귀시킵니다.

### 명령어 예시
```bash
# 노드 격리 (Cordon)
oc adm cordon <node-name>

# 노드 복귀 (Uncordon)
oc adm uncordon <node-name>
```
**시나리오**: 노드를 재부팅하거나 패치할 때, 먼저 `cordon` 한 후 `drain` 하여 워크로드를 이동시키고, 작업이 완료되면 `uncordon` 합니다.

## 5. Taint 와 Toleration: 노드 격리 전략

Taint(타인트) 은 노드에 "이Pod 은 들어오지 마라"라는 표시를 붙이는 메커니즘이며, Toleration(토러레이션) 은 Pod 가 그 표시를 무시하고 노드로 들어갈 수 있도록 허용하는 규칙입니다.

### 개념 및 활용
*   **Taint 적용**: 특정 노드 (예: GPU 노드, 특수 환경 노드) 에만 특정 Pod 가 배치되도록 강제할 때 사용합니다.
*   **Toleration 적용**: Pod 의 스펙 (YAML) 에 `tolerations` 을 추가하여 노드의 Taint 를 무시하고 스케줄링되도록 합니다.

### YAML 예시
다음은 `node-role.kubernetes.io/master` Taint 를 가진 Master 노드로만 실행되도록 하는 Pod 템플릿 예시입니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: master-only-pod
spec:
  tolerations:
  - key: node-role.kubernetes.io/master
    operator: Exists
    effect: NoSchedule
  containers:
  - name: nginx
    image: nginx
```

### Taint 적용 명령어 (Admin)
```bash
# 노드에 Taint 추가 (key=value:effect)
oc adm taint nodes <node-name> node-role.kubernetes.io/master=Exists:NoSchedule

# Taint 제거
oc adm untaint nodes <node-name>
```

## 6. 노드 라벨 (Node Label) 및 Pod 배치 제어

노드 라벨은 노드의 속성을 설명하는 키-값 쌍입니다. 이를 통해 `nodeSelector` 나 `nodeAffinity` 를 사용하여 Pod 를 특정 노드 유형으로 정밀하게 제어할 수 있습니다.

### 라벨 관리
```bash
# 라벨 추가
oc label nodes <node-name> disktype=ssd region=asia

# 라벨 제거
oc label nodes <node-name> disktype-

# 라벨 조회
oc get nodes <node-name> --show-labels
```

### Pod 배치 제어
Pod 의 `spec.nodeSelector` 또는 `spec.affinity` 에 라벨을 매핑하면 해당 라벨이 있는 노드만 선택됩니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ssd-app
spec:
  selector:
    matchLabels:
      app: ssd-app
  template:
    metadata:
      labels:
        app: ssd-app
    spec:
      containers:
      - name: app
        image: my-app
      nodeSelector:
        disktype: ssd
```

## 7. MachineSet: OCP 에서 노드 수 관리

OCP 에서 노드 개수를 직접 `oc scale` 명령어로 관리하는 것은 불가능하며, **MachineSet** 을 통해 관리합니다. MachineSet 은 원하는 수의 노드를 자동으로 생성하고, 노드가 제거되면 새로운 노드를 생성하여 개수를 유지합니다.

### MachineSet 스케일링
```bash
# MachineSet 목록 조회
oc get machineset

# MachineSet 스케일링 (예: 3 개 노드로 증가)
oc scale machineset worker-node-pool --replicas=3

# 특정 노드 풀 삭제 및 재생성 (Rolling Restart)
oc delete machineset worker-node-pool
# (새로운 MachineSet 리소스를 생성해야 함)
oc create -f worker-node-pool.yaml
```
MachineSet 은 노드가 장애로 인해 비정상 상태가 되면 자동으로 새로운 노드를 프로비저닝하여 클러스터의 노드 개수를 복구합니다.

## 8. 노드 리소스 모니터링

노드의 CPU, 메모리 사용량을 실시간으로 모니터링하여 리소스 압박 상태를 파악해야 합니다.

### 명령
