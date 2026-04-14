# Backup and Restore

## Start Here

운영자는 이 문서에서 두 가지만 먼저 확인한다.

- 지금 백업을 어떻게 남기는가
- 백업본에서 어떻게 복구하는가

## When To Use

아래 상황이면 이 문서를 먼저 확인한다.

- control plane 작업 전에 안전한 etcd 백업이 필요한 경우
- shutdown, restart, hibernation 전에 복구 가능 상태를 확보해야 하는 경우
- etcd 백업에서 cluster 를 수동 복구해야 하는 경우

## Before You Begin

- `cluster-admin` 권한이 필요하다.
- control plane host 에 SSH 접근이 가능해야 한다.
- 백업은 같은 z-stream release 기준으로 사용해야 한다.
- 백업 디렉터리에는 `snapshot_<timestamp>.db`, `static_kuberesources_<timestamp>.tar.gz` 두 파일이 함께 있어야 한다.

## Back Up etcd Data

etcd 스냅샷을 생성하고 정적 포드 리소스를 함께 백업한다. 백업은 control plane host 하나에서만 수행한다.

### 1. Check Cluster-Wide Proxy

```shell
oc get proxy cluster -o yaml
```

프록시가 켜져 있으면 debug shell 안에서 proxy 환경 변수를 먼저 내린다.

```shell
export HTTP_PROXY=http://<your_proxy.example.com>:8080
export HTTPS_PROXY=https://<your_proxy.example.com>:8080
export NO_PROXY=<example.com>
```

### 2. Open a Debug Shell

```shell
oc debug --as-root node/<node_name>
chroot /host
```

### 3. Run the Backup Script

```shell
cluster-backup.sh
```

백업이 끝나면 아래 두 산출물이 생성돼야 한다.

- `snapshot_<timestamp>.db`
- `static_kuberesources_<timestamp>.tar.gz`

## Verify

- 백업 파일 두 개가 모두 있어야 한다.
- 백업을 여러 control plane host 에서 중복 수행하지 않았는지 확인한다.
- 복구에 사용할 백업이 현재 cluster 와 같은 z-stream 기준인지 확인한다.
- 복구 후에는 cluster health 와 etcd 상태를 다시 확인한다.

## Restore

이 문서는 `control plane node 재생성 없이 직접 3-member etcd 를 다시 올리는 수동 복구 경로`를 기준으로 한다.

### 1. Connect to Every Control Plane Host

- 각 host 에 SSH 세션을 별도로 잡는다.
- restore 가 시작되면 API server 접근이 사라질 수 있으므로, 시작 전에 접속을 확보한다.

### 2. Copy the Backup Directory

백업 디렉터리를 각 control plane host 의 작업 경로로 복사한다.

### 3. Stop Static Pods

기존 manifest 를 백업 디렉터리로 이동한다.

```shell
mkdir -p /root/manifests-backup
mv /etc/kubernetes/manifests/kube-apiserver-pod.yaml /root/manifests-backup/
mv /etc/kubernetes/manifests/kube-controller-manager-pod.yaml /root/manifests-backup/
mv /etc/kubernetes/manifests/kube-scheduler-pod.yaml /root/manifests-backup/
mv /etc/kubernetes/manifests/etcd-pod.yaml /root/manifests-backup/
```

각 static pod 가 실제로 멈췄는지 확인한다.

```shell
crictl ps | grep kube-apiserver | grep -E -v "operator|guard"
crictl ps | grep kube-controller-manager | grep -E -v "operator|guard"
crictl ps | grep kube-scheduler | grep -E -v "operator|guard"
crictl ps | grep etcd | grep -E -v "operator|guard"
```

필요하면 남아 있는 container 를 수동으로 stop 한다.

```shell
crictl stop <container_id>
```

## Failure Signals

- backup artifact 가 두 개 다 없으면 restore 절차를 진행하지 않는다.
- 제어 평면 노드 접근을 먼저 확보하지 않으면 restore 중간에 절차가 멈춘다.
- static pod 가 완전히 멈추지 않은 상태에서 restore 를 진행하면 결과가 불안정해진다.
