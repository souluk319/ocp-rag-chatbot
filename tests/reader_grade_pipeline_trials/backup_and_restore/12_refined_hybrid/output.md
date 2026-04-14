# Backup and Restore

## Overview

이 문서는 OpenShift control plane 작업 전에 필요한 etcd 백업 절차와, 백업본에서 클러스터를 수동으로 복구하는 핵심 경로를 정리한다.

shutdown, restart, hibernation, 장애 복구 전에는 이 문서를 먼저 확인한다.

여기서는 etcd 백업, 수동 복구, 검증 포인트, 실패 신호만 다룬다. application backup, OADP release notes, provider별 상세 절차는 포함하지 않는다.

## When To Use

- control plane 작업 전에 안전한 etcd 백업이 필요한 경우
- shutdown, restart, hibernation 전에 복구 가능 상태를 확보해야 하는 경우
- etcd 백업에서 cluster 를 수동 복구해야 하는 경우
- 원문 전체를 처음부터 읽기 전에 핵심 절차만 먼저 파악해야 하는 경우

## Before You Begin

### Access

- `cluster-admin` 권한이 필요하다.
- 모든 control plane host 에 SSH 접근이 가능해야 한다.
- 복구 절차는 각 control plane host 별도 터미널 세션으로 진행하는 편이 안전하다.

### Backup Artifacts

복구에 필요한 백업 파일은 아래 두 개다.

- `snapshot_<timestamp>.db`
- `static_kuberesources_<timestamp>.tar.gz`

둘 중 하나만 있으면 restore 절차를 진행하지 않는다.

### Important

- 백업은 control plane host 하나에서만 수행한다.
- restore 에는 같은 z-stream release 에서 생성한 백업만 사용한다.
- private 환경에서 encryption 을 사용하는 경우에도 `static_kuberesources` 파일은 반드시 보존해야 한다.

## Back Up etcd Data

### 1. Check Whether Cluster-Wide Proxy Is Enabled

```shell
oc get proxy cluster -o yaml
```

프록시가 켜져 있으면 debug shell 안에서 아래 환경 변수를 먼저 내린다.

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

백업이 끝나면 아래 두 산출물이 생성돼야 한다.

- `snapshot_<timestamp>.db`
- `static_kuberesources_<timestamp>.tar.gz`

## Verify the Backup Artifacts

백업 직후에는 아래 네 가지만 확인한다.

1. 백업 디렉터리에 snapshot 파일이 있는지
2. `static_kuberesources` tarball 이 함께 생성됐는지
3. 백업을 여러 control plane host 에서 중복 수행하지 않았는지
4. 복구에 사용할 백업이 현재 cluster 와 같은 z-stream 기준인지

### Verification Tip

- shutdown, restart, hibernation 전에는 `백업이 있다`가 아니라 `복구에 필요한 두 파일이 함께 있다`를 기준으로 본다.
- 이 단계가 빠지면 이후 절차 전체가 불안정해진다.

## Restore etcd from a Backup

### Restore Path Choice

이 문서는 `control plane node 재생성 없이 직접 3-member etcd 를 다시 올리는 수동 복구 경로`를 기준으로 한다.

이 경로는 아래 상황에서 유용하다.

- UPI 환경이라 control plane 재구성이 번거로운 경우
- 현재 host 에서 빠르게 quorum 을 다시 세워야 하는 경우

### 1. Connect to Every Control Plane Host

- 각 host 에 SSH 세션을 별도로 잡는다.
- restore 가 시작되면 API server 접근이 사라질 수 있으므로, 시작 전에 접속을 확보한다.

### 2. Copy the Backup Directory to Every Control Plane Host

이 문서는 `/home/core/assets/backup` 경로를 기준으로 설명한다.

### 3. Stop Static Pods on Control Plane Nodes

기존 manifest 를 먼저 백업 디렉터리로 이동한다.

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

### 4. Preserve Current etcd Data Before Restore

```shell
mkdir /home/core/assets/old-member-data
mv /var/lib/etcd/member /home/core/assets/old-member-data
```

이 단계는 restore 실패 시 현재 상태로 되돌릴 여지를 남긴다.

### 5. Restore the Snapshot

복구할 snapshot 을 기본 etcd 경로로 복사한다.

```shell
cp /home/core/assets/backup/<snapshot_yyyy-mm-dd_hhmmss>.db /var/lib/etcd
```

필요한 etcd image 를 확인한 뒤 snapshot restore 를 수행한다.

```shell
jq -r '.spec.containers[]|select(.name=="etcdctl")|.image' /root/manifests-backup/etcd-pod.yaml
podman run --rm -it --entrypoint="/bin/bash" -v /var/lib/etcd:/var/lib/etcd:z <image-hash>
ETCDCTL_API=3 /usr/bin/etcdctl snapshot restore /var/lib/etcd/<snapshot_yyyy-mm-dd_hhmmss>.db \
  --name "<ETCD_NAME>" \
  --initial-cluster="<ETCD_INITIAL_CLUSTER>" \
  --initial-cluster-token "openshift-etcd-<UUID>" \
  --initial-advertise-peer-urls "<ETCD_NODE_PEER_URL>" \
  --data-dir="/var/lib/etcd/restore-<UUID>"
```

### 6. Move the Restored Member Data Into Place

```shell
mv /var/lib/etcd/restore-<UUID>/member /var/lib/etcd
restorecon -vR /var/lib/etcd/
rm -rf /var/lib/etcd/restore-<UUID>
rm /var/lib/etcd/<snapshot_yyyy-mm-dd_hhmmss>.db
```

### 7. Bring etcd Back First, Then Restore Control Plane Static Pods

```shell
mv /root/manifests-backup/etcd-pod.yaml /etc/kubernetes/manifests
crictl ps | grep etcd | grep -v operator
crictl exec -it $(crictl ps | grep etcdctl | awk '{print $1}') etcdctl endpoint status -w table
mv /root/manifests-backup/kube-apiserver-pod.yaml /etc/kubernetes/manifests
systemctl restart kubelet
mv /root/manifests-backup/kube-* /etc/kubernetes/manifests/
crictl ps | grep -E 'kube-(apiserver|scheduler|controller-manager)' | grep -v -E 'operator|guard'
```

## Verify Cluster Recovery

복구 후에는 아래 순서로 본다.

1. `etcdctl endpoint status -w table` 로 endpoint 상태 확인
2. control plane static pod 들이 모두 다시 떠 있는지 확인
3. kubelet restart 이후 API server 가 다시 응답하는지 확인
4. cluster operator, node readiness, 핵심 control plane pod 상태를 순차 확인

## Failure Signals

### Backup Side

- snapshot 파일만 있고 `static_kuberesources` tarball 이 없음
- 여러 control plane host 에서 제각각 백업을 떠서 어떤 백업이 기준인지 불명확함
- proxy 환경인데 debug shell 에 proxy 변수가 반영되지 않음

### Restore Side

- restore 시작 전에 SSH 세션을 확보하지 않아 host 접근을 잃음
- API server, scheduler, controller-manager, etcd static pod 가 완전히 멈추기 전에 다음 단계로 진행함
- 현재 cluster 와 다른 z-stream backup 을 사용함
- restored member data 를 `/var/lib/etcd` 에 제대로 옮기지 못함
