# Backup and Restore

## Overview

이 문서는 OpenShift control plane 작업 전에 필요한 etcd 백업 절차와, 백업본에서 클러스터를 수동으로 복구하는 핵심 경로를 정리한다.

클러스터 유지보수, shutdown, restart, hibernation, quorum loss 복구 전에는 이 문서를 먼저 확인한다.

여기서는 control plane 백업과 수동 복구만 다룬다. OADP 기반 애플리케이션 백업은 포함하지 않는다.

## When To Use

- control plane 작업 전에 etcd 백업을 남겨야 하는 경우
- quorum loss 또는 치명적 관리 실수로 이전 cluster state 로 되돌려야 하는 경우
- UPI 환경에서 control plane 재생성 없이 수동 복구 경로가 필요한 경우

## Before You Begin

### Access

- `cluster-admin` 권한이 필요하다.
- 모든 control plane host 에 SSH 접근이 가능해야 한다.
- restore 시작 전 각 control plane host 별도 터미널 세션을 확보한다.

### Backup Artifacts

복구에는 아래 두 파일이 모두 필요하다.

- `snapshot_<timestamp>.db`
- `static_kuberesources_<timestamp>.tar.gz`

### Important

- 백업은 control plane host 하나에서만 수행한다.
- 같은 z-stream release 에서 생성한 백업만 restore 에 사용한다.
- etcd restore 는 마지막 수단이다. Kubernetes API 서버로 필요한 데이터를 조회할 수 있다면 restore 를 시작하지 않는다.

## Back Up etcd Data

### 1. Check Cluster-Wide Proxy

```shell
oc get proxy cluster -o yaml
```

프록시가 켜져 있으면 debug shell 에서 아래 변수를 먼저 내린다.

```shell
export HTTP_PROXY=http://<your_proxy.example.com>:8080
export HTTPS_PROXY=https://<your_proxy.example.com>:8080
export NO_PROXY=<example.com>
```

### 2. Open a Debug Shell on a Control Plane Node

```shell
oc debug --as-root node/<node_name>
chroot /host
```

### 3. Run the Backup Script

```shell
/usr/local/bin/cluster-backup.sh /home/core/assets/backup
```

이 스크립트는 `etcdctl snapshot save`를 감싼 래퍼 스크립트다.

### Expected Output

백업이 끝나면 아래 두 산출물이 생겨야 한다.

- `snapshot_<timestamp>.db`
- `static_kuberesources_<timestamp>.tar.gz`

## Verify the Backup Artifacts

1. snapshot 파일이 생성됐는지 확인한다.
2. `static_kuberesources` tarball 이 함께 생성됐는지 확인한다.
3. 백업을 여러 control plane host 에서 중복 수행하지 않았는지 확인한다.
4. 현재 cluster 와 같은 z-stream backup 인지 확인한다.

## Restore etcd from a Backup

### Why This Path

이 경로는 `cluster-restore.sh` 기반 단일 멤버 복구 대신, 현재 control plane host 에서 직접 3-member etcd 를 다시 올리는 수동 복구 경로다.

UPI 환경처럼 control plane 재생성이 번거로운 경우 이 방식이 유리하다.

### 1. Stop Static Pods on Each Control Plane Node

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

### 2. Preserve Current etcd Data

```shell
mkdir /home/core/assets/old-member-data
mv /var/lib/etcd/member /home/core/assets/old-member-data
```

### 3. Restore the Snapshot

```shell
cp /home/core/assets/backup/<snapshot_yyyy-mm-dd_hhmmss>.db /var/lib/etcd
jq -r '.spec.containers[]|select(.name=="etcdctl")|.image' /root/manifests-backup/etcd-pod.yaml
podman run --rm -it --entrypoint="/bin/bash" -v /var/lib/etcd:/var/lib/etcd:z <image-hash>
ETCDCTL_API=3 /usr/bin/etcdctl snapshot restore /var/lib/etcd/<snapshot_yyyy-mm-dd_hhmmss>.db \
  --name "<ETCD_NAME>" \
  --initial-cluster="<ETCD_INITIAL_CLUSTER>" \
  --initial-cluster-token "openshift-etcd-<UUID>" \
  --initial-advertise-peer-urls "<ETCD_NODE_PEER_URL>" \
  --data-dir="/var/lib/etcd/restore-<UUID>" \
  --skip-hash-check=true
```

### 4. Move the Restored Data into Place

```shell
mv /var/lib/etcd/restore-<UUID>/member /var/lib/etcd
restorecon -vR /var/lib/etcd/
rm -rf /var/lib/etcd/restore-<UUID>
rm /var/lib/etcd/<snapshot_yyyy-mm-dd_hhmmss>.db
```

### 5. Bring etcd Back First

```shell
mv /root/manifests-backup/etcd-pod.yaml /etc/kubernetes/manifests
crictl ps | grep etcd | grep -v operator
crictl exec -it $(crictl ps | grep etcdctl | awk '{print $1}') etcdctl endpoint status -w table
```

그 다음 Kubernetes API server, scheduler, controller manager static pod 를 순서대로 복구한다.

## Verify Cluster Recovery

1. `etcdctl endpoint status -w table` 로 endpoint 상태를 확인한다.
2. control plane static pod 들이 모두 다시 떠 있는지 확인한다.
3. API server 가 다시 응답하는지 확인한다.
4. cluster operator, node readiness, 핵심 control plane pod 상태를 순차 확인한다.

## Failure Signals

- snapshot 파일만 있고 `static_kuberesources` tarball 이 없는 경우
- restore 시작 전에 SSH 세션을 확보하지 않은 경우
- static pod 가 완전히 멈추기 전에 다음 단계로 진행한 경우
- 현재 cluster 와 다른 z-stream backup 을 사용한 경우
- `etcd` on-disk 상태와 etcd 내용이 어긋나 Operator churn 이 발생한 경우
