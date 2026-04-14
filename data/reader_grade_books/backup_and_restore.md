# Backup and Restore

## Overview

이 문서는 OpenShift control plane 작업 전에 필요한 etcd 백업 절차와, 백업본에서 클러스터를 수동으로 복구하는 핵심 절차를 정리한다.

클러스터 관리자로서는 일정 기간 동안 OpenShift Container Platform 클러스터를 중지한 후 나중에 다시 시작해야 할 필요가 있을 수 있습니다. 클러스터를 다시 시작해야 하는 이유는 클러스터에 대한 유지보수를 수행해야 하거나 리소스 비용을 절감하고 싶기 때문일 수 있습니다. OpenShift Container Platform에서는 클러스터를 쉽게 나중에 다시 시작할 수 있도록 클러스터를 정상적으로 종료(shutdown)할 수 있습니다.

클러스터를 종료하기 전에 etcd 데이터를 백업해야 합니다. etcd 는 OpenShift Container Platform 의 모든 리소스 객체 상태를 영구적으로 저장하는 키-값 저장소입니다. etcd 백업은 재해 복구에서 중요한 역할을 합니다. OpenShift Container Platform 에서는 병렬된 etcd 멤버를 교체할 수도 있습니다.

클러스터를 다시 작동시키려면 클러스터를 정상적으로 재시작하세요.

## Before You Begin

etcd 는 OpenShift Container Platform 의 키-값 저장소로, 모든 리소스 객체의 상태를 영구적으로 저장합니다.

클러스터의 etcd 데이터를 정기적으로 백업하여 OpenShift Container Platform 환경 외부의 안전한 위치에 저장하세요. 설치 후 24 시간 이내에 완료되는 첫 번째 인증서 회전 전에 etcd 백업을 수행하지 마십시오. 그렇지 않으면 백업에 만료된 인증서가 포함됩니다. 또한 etcd 스냅샷의 I/O 비용이 높으므로 비피크 사용 시간 동안 etcd 백업을 수행하는 것이 좋습니다.

클러스터를 업데이트하기 전에 etcd 백업을 수행하는 것이 중요합니다. 클러스터를 복원할 때 동일한 z-stream 릴리스에서 수행한 etcd 백업을 사용해야 합니다. 예를 들어, OpenShift Container Platform 4.17.5 클러스터는 4.17.5 에서 수행한 etcd 백업을 사용해야 합니다.

> **중요**
> 컨트롤 플레인 호스트에서 백업 스크립트를 한 번 호출하여 클러스터의 etcd 데이터를 백업하세요. 각 컨트롤 플레인 호스트마다 백업을 수행하지 마세요.

etcd 백업이 있으면 이전 클러스터 상태로 복원할 수 있습니다.

## Back Up etcd Data

etcd 스냅샷을 생성하고 정적 포드에 대한 리소스를 백업하여 etcd 데이터를 백업하는 단계를 따르세요. 이 백업은 나중에 etcd 를 복원해야 하는 경우 저장하여 사용할 수 있습니다.

> **중요**
> 단일 컨트롤 플레인 호스트에서만 백업을 저장하세요. 클러스터 내의 각 컨트롤 플레인 호스트에서 백업을 수행하지 마세요.

> **선행 조건**
> `cluster-admin` 역할을 가진 사용자로서 클러스터에 액세스할 수 있습니다.

클러스터 전체 프록시가 활성화되어 있는지 확인했습니다.

> **팁**
> 프록시가 활성화되어 있는지 확인하려면 다음 명령의 출력을 검토할 수 있습니다. `httpProxy`, `httpsProxy`, 및 `noProxy` 필드에 값이 설정되어 있으면 프록시가 활성화된 것입니다.

```shell
oc get proxy cluster -o yaml
```

### 절차

```shell-session
$ oc debug --as-root node/<node_name>
```

```shell-session
sh-4.4# chroot /host
```

클러스터 전체 프록시가 활성화되어 있으면 다음 명령을 실행하여 `NO_PROXY`, `HTTP_PROXY`, 및 `HTTPS_PROXY` 환경 변수를 내보냅니다:

```shell-session
$ export HTTP_PROXY=http://<your_proxy.example.com>:8080
```

```shell-session
$ export HTTPS_PROXY=https://<your_proxy.example.com>:8080
```

```shell-session
$ export NO_PROXY=<example.com>
```

## Restore Cluster State

클러스터를 이전 상태로 복원하려면 `etcd` 데이터를 백업하기 위해 스냅샷을 생성했어야 합니다. 이 스냅샷을 사용하여 클러스터 상태를 복원합니다. 자세한 내용은 "etcd 데이터 백업"을 참조하십시오.

etcd 백업을 사용하여 클러스터를 이전 상태로 복원할 수 있습니다. 이는 다음 상황으로부터 복구하는 데 사용할 수 있습니다:

클러스터가 제어 평면 호스트의 다수를 잃었습니다 (쿼럼 손실).

관리자가 중요한 항목을 삭제하여 클러스터를 복구해야 하는 상황이 발생했습니다.

> **주의**
> 이전 클러스터 상태로 복원하는 것은 실행 중인 클러스터에 대해 파괴적이고 불안정하게 만드는 조치입니다. 이는 최후의 수단으로만 사용해야 합니다.

Kubernetes API 서버를 사용하여 데이터를 가져올 수 있는 경우 etcd 가 사용 가능하므로 etcd 백업 파일을 사용하여 복원해서는 안 됩니다.

etcd 복원 작업은 클러스터를 과거 상태로 되돌리게 되며, 모든 클라이언트는 충돌하는 병렬 역사를 경험하게 됩니다. 이는 kubelets, Kubernetes 컨트롤러 매니저, 영구 볼륨 컨트롤러 및 OpenShift Container Platform 오퍼레이터(네트워크 오퍼레이터 포함) 와 같은 감시 컴포넌트의 동작에 영향을 미칠 수 있습니다.

etcd 내의 내용이 디스크의 실제 내용과 일치하지 않을 경우 Operator churn 을 유발할 수 있습니다. 디스크의 파일이 etcd 내의 내용과 충돌하면 Kubernetes API 서버, Kubernetes 컨트롤러 매니저, Kubernetes 스케줄러, 및 etcd 를 위한 Operator 가 멈출 수 있습니다. 이러한 문제를 해결하려면 수동 작업이 필요할 수 있습니다.

극단적인 경우 클러스터는 퍼시스턴트 볼륨을 추적하지 못하거나, 더 이상 존재하지 않는 중요한 워크로드를 삭제하고, 머신을 다시 이미지화하며, 만료된 인증서를 가진 CA 번들을 다시 작성할 수 있습니다.

## Manual Restore from etcd Backup

"이전 클러스터 상태로 복원" 섹션에서 설명한 복원 절차:

2 개 제어 평면 노드의 완전한 재구성을 필요로 하며, UPI 설치 방법으로 설치된 클러스터의 경우 복잡한 절차일 수 있습니다. UPI 설치에서는 제어 평면 노드를 위한 `Machine` 또는 `ControlPlaneMachineset` 이 생성되지 않기 때문입니다.

/usr/local/bin/cluster-restore.sh 스크립트를 사용하여 새 단일 멤버 etcd 클러스터를 시작한 다음 이를 3 개 멤버로 확장합니다.

반면, 이 절차는:

어떤 제어 평면 노드도 재구성할 필요가 없습니다.

직접 3 멤버 etcd 클러스터를 시작합니다.

클러스터가 제어 평면을 위한 `MachineSet` 을 사용하는 경우, 더 간단한 etcd 복구 절차로 "이전 클러스터 상태로 복원"을 사용하는 것이 좋습니다.

클러스터를 복원할 때는 동일한 z-stream 릴리스에서 가져온 etcd 백업을 사용해야 합니다. 예를 들어, OpenShift Container Platform 4.7.2 클러스터는 4.7.2 에서 가져온 etcd 백업을 사용해야 합니다.

선결 조건

cluster-admin 역할을 가진 사용자로 클러스터에 액세스합니다. 예를 들어, kubeadmin 사용자.

모든 제어 평면 호스트에 SSH 액세스 권한이 있으며, root 로 전환할 수 있는 호스트 사용자가 필요합니다. 예를 들어, 기본 core 호스트 사용자.

이전 etcd 스냅샷과 동일한 백업에서 정적 포드에 대한 리소스를 모두 포함하는 백업 디렉터리입니다. 디렉터리 내 파일 이름은 다음 형식을 따라야 합니다: snapshot_<날짜시간>.db 와 static_kuberesources_<날짜시간>.tar.gz.

> **절차**
> SSH 를 사용하여 각 제어 평면 노드에 연결합니다.

복원 프로세스가 시작되면 Kubernetes API 서버에 액세스할 수 없게 되므로 제어 평면 노드에 액세스할 수 없습니다. 이 때문에 각 제어 평면 호스트에 액세스할 때 별도의 터미널에서 SSH 연결을 사용하는 것이 좋습니다.

> **중요**
> 이 단계를 완료하지 않으면 제어 평면 호스트에 액세스하여 복원 절차를 완료할 수 없으며, 해당 상태에서 클러스터를 복구할 수 없습니다.

etcd 백업 디렉터리를 각 제어 평면 호스트로 복사합니다.

이 절차는 etcd 스냅샷과 정적 포드에 대한 리소스를 포함하는 backup 디렉터리를 각 제어 평면 호스트의 /home/core/assets 디렉터리로 복사했다고 가정합니다. 아직 존재하지 않는 경우 해당 assets 폴더를 생성해야 할 수 있습니다.

모든 제어 평면 노드의 정적 포드를 중지합니다. 한 번에 하나의 호스트씩 진행합니다.

기존 Kubernetes API 서버 정적 포드 매니페스트를 kubelet 매니페스트 디렉터리에서 이동합니다.

```shell-session
$ mkdir -p /root/manifests-backup
```

```shell-session
$ mv /etc/kubernetes/manifests/kube-apiserver-pod.yaml /root/manifests-backup/
```

다음 명령어로 Kubernetes API 서버 컨테이너가 중지되었는지 확인합니다:

## Failure Signals

OpenShift Container Platform 클러스터가 어떤 형태의 지속 가능한 저장을 사용하는 경우, 클러스터의 상태는 일반적으로 etcd 외부에 저장됩니다. etcd 백업에서 복원할 때 OpenShift Container Platform 내의 워크로드 상태도 함께 복원됩니다. 그러나 etcd 스냅샷이 오래된 경우 상태가 무효하거나 구식일 수 있습니다.

> **중요**
> 지속 가능한 볼륨 (PV) 의 내용은 etcd 스냅샷의 일부가 절대 아닙니다. etcd 스냅샷에서 OpenShift Container Platform 클러스터를 복원할 때 비중요 워크로드가 중요 데이터에 접근하거나 그 반대의 상황이 발생할 수 있습니다.

다음은 구식 상태를 생성하는 몇 가지 예시 시나리오입니다.

PV 객체로 백업된 포드에서 MySQL 데이터베이스가 실행 중입니다. etcd 스냅샷에서 OpenShift Container Platform 을 복원하면 스토리지 제공자에서 볼륨이 다시 복원되지 않으며, 포드가 반복적으로 시작을 시도함에도 불구하고 실행 중인 MySQL 포드가 생성되지 않습니다. 스토리지 제공자에서 볼륨을 수동으로 복원한 후 PV 를 수정하여 새 볼륨을 지시하도록 해야 합니다.

포드 P1 이 노드 X 에 연결된 볼륨 A 를 사용하고 있습니다. etcd 스냅샷이 노드 Y 에서 동일한 볼륨을 사용하는 다른 포드가 실행 중인 동안 촬영된 경우, etcd 복원이 수행될 때 포드 P1 이 볼륨이 여전히 노드 Y 에 연결되어 있어 올바르게 시작할 수 없을 수 있습니다. OpenShift Container Platform 은 연결 상태를 인식하지 못하며 자동으로 분리하지 않습니다. 이 경우 볼륨이 노드 X 에 연결될 수 있도록 볼륨을 노드 Y 에서 수동으로 분리해야 하며, 이후 포드 P1 이 시작할 수 있습니다.

etcd 스냅샷이 촬영된 후 클라우드 제공자 또는 스토리지 제공자 자격 증명이 업데이트되었습니다. 이는 해당 자격 증명을 의존하는 CSI 드라이버나 Operators 가 작동하지 않도록 합니다. 해당 드라이버나 Operators 가 필요한 자격 증명을 수동으로 업데이트해야 할 수 있습니다.

etcd 스냅샷이 촬영된 후 OpenShift Container Platform 노드에서 디바이스가 제거되거나 이름이 변경되었습니다. Local Storage Operator 는 관리하는 각 PV 에 대해 `/dev/disk/by-id` 또는 `/dev` 디렉토리에서 심링크를 생성합니다. 이 상황은 로컬 PV 가 더 이상 존재하지 않는 디바이스를 참조하도록 할 수 있습니다.

이 문제를 해결하려면 관리자가 다음 작업을 수행해야 합니다:

무효한 디바이스를 가진 PV 를 수동으로 제거합니다.

## Source Trace

- 원문 slug: `backup_and_restore`
- 기준 축: `etcd backup / manual restore / failure signals`
