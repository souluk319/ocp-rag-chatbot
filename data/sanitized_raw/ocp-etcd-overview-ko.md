<!-- source: ocp-etcd-overview-ko.md -->

# etcd 개요 및 운영 가이드 (OCP/Kubernetes용)

## 1. etcd: 왜 필요한가?

**etcd**는 Kubernetes 및 OpenShift Container Platform(OCP)의 핵심 구성 요소로, 모든 클러스터의 상태를 저장하는 분산 키-값 저장소입니다. Kubernetes는 이를 "관찰 가능한 상태의 단일 진실 공급원(Single Source of Truth)"으로 간주합니다.

### 핵심 역할
- **클러스터 상태 저장**: Pod, Deployment, Service, ConfigMap, Secret 등 모든 리소스의 현재 상태 (Spec 와 Status) 를 영구적으로 저장합니다.
- **동기화 메커니즘**: 여러 노드 (Control Plane) 에서 구성 변경 사항이 어떻게 동기화되는지 관리합니다.
- **선도선추 (Leader Election)**: Control Plane 구성 요소 (API Server, Scheduler, Controller Manager) 가 누가 리더인지 결정하는 기반이 됩니다.

### 왜 중요한가?
etcd 가 다운되거나 데이터가 손상되면 **Kubernetes 클러스터 전체가 마비**됩니다. API Server 가 etcd 에 접근할 수 없으면 새로운 Pod 를 생성하거나 기존 Pod 를 스케줄링하는 것이 불가능해지며, 이는 클러스터의 가용성과 신뢰성을 근본적으로 위협합니다. 따라서 etcd 는 "클러스터의 심장"과 비유될 만큼 그 중요도가 절대적입니다.

---

## 2. OCP 아키텍처에서 etcd 의 위치

OpenShift 에서 etcd 는 **Master 노드** (Control Plane) 에 설치되며, 보통 3 개 이상의 인스턴스를 구성하여 고가용성 (HA) 을 보장합니다.

### 아키텍처 흐름
1. **User/API Server**: 사용자가 CLI (`oc` 또는 `kubectl`) 로 요청을 보냅니다.
2. **etcd**: API Server 는 요청을 처리한 결과를 etcd 에 저장하거나, etcd 에서 최신 상태를 읽어옵니다.
3. **Controller Manager**: etcd 에서 상태 변경을 감지하고, 실제 노드에서 Pod 를 생성/삭제하는 명령을 내려 실행합니다.
4. **Scheduler**: etcd 에 있는 Pod 의 요청을 받아 적절한 노드로 할당합니다.

### OCP 내 구성 특징
- OCP 는 etcd 를 직접 관리하는 것이 아니라, **etcd Operator** 를 통해 관리합니다.
- 기본적으로 3 개의 etcd 인스턴스를 Master 노드에서 실행하며, 데이터는 이 3 개 노드 간에 복제 (Replication) 됩니다.
- OCP 4.x 이후에는 etcd 가 Master 노드와 별도의 Pod 로 실행되기도 하지만, 여전히 Master 노드 리소스를 공유합니다.

---

## 3. etcd 백업 방법

etcd 백업은 `etcdctl` 명령어를 사용하여 수행하며, OCP 환경에서는 `oc adm` 명령어를 통해 백업 스크립트를 실행할 수 있습니다.

### 필수 조건
- etcd 클라이언트 툴 (`etcdctl`) 이 설치되어 있어야 합니다.
- Master 노드에 접근할 수 있어야 합니다.

### 방법 A: OCP 내장 백업 스크립트 사용 (권장)
OCP 는 `oc adm etcd backup` 명령어를 제공합니다. 이 명령어는 etcd 데이터를 백업하고 S3, GCS, 또는 로컬 파일로 저장합니다.

```bash
# S3 (AWS) 에 백업 저장
oc adm etcd backup --to-storage s3://my-bucket/backup/ --cluster-version 4.14

# 로컬 파일로 백업 (Master 노드에서 실행)
oc adm etcd backup --to-storage local --output-dir /tmp/etcd-backup
```

### 방법 B: 수동 etcdctl 을 통한 백업
만약 수동 백업이 필요하다면, etcd 클라이언트 툴을 사용하여 백업 파일을 생성합니다.

```bash
# Master 노드에서 실행 (root 권한 필요)
export ETCDCTL_API=3
export ETCDCTL_ENDPOINTS="https://<master-node-ip>:2379"
export ETCDCTL_CACERT=/etc/kubernetes/static-pod-resources/etcd-peer-serving-kubeconfig.crt
export ETCDCTL_CERT=/etc/kubernetes/static-pod-resources/etcd-peer-serving-kubeconfig.crt
export ETCDCTL_KEY=/etc/kubernetes/static-pod-resources/etcd-peer-serving-kubeconfig.key

# 백업 생성 (etcd.db 파일로 저장)
etcdctl snapshot save /tmp/etcd-backup.db

# 백업 상태 확인
ls -lh /tmp/etcd-backup.db
```

> **주의**: OCP 환경에서는 인증 (TLS) 이 필수이므로, 환경 변수를 설정하지 않으면 연결이 거부됩니다.

---

## 4. etcd 복구 절차

etcd 데이터가 손상되거나 노드가 고장 났을 때 복원하는 과정은 매우 민감합니다. 잘못된 복구 시 클러스터가 부팅되지 않을 수 있습니다.

### 단계별 복구 가이드

#### 1 단계: 손상된 노드 격리
고장 난 노드를 클러스터에서 제거합니다.
```bash
# 노드에서 etcd Pod 삭제
oc delete pod -n openshift-etcd <etcd-pod-name>

# 노드 자체를 클러스터에서 제외 (필요시)
oc adm node-cordon <master-node-name>
oc adm node-unschedule <master-node-name>
```

#### 2 단계: 백업 파일 준비
3 단계에서 생성한 백업 파일 (`etcd-backup.db`) 을 준비합니다.

#### 3 단계: etcd Pod 수동 시작 및 데이터 복원
etcd Pod 를 수동으로 시작하여 백업 데이터를 적용합니다.

```bash
# etcd Pod 에 진입
oc rsh -n openshift-etcd <etcd-pod-name>

# 백업 데이터 적용
etcdctl snapshot restore \
  --data-dir=/var/lib/etcd/member \
  --name=<node-name> \
  --initial-cluster=<cluster-config> \
  --initial-cluster-token=[REDACTED_SECRET] \
  --initial-advertise-peer-urls=https://<ip>:2380 \
  --listen-client-urls=https://0.0.0.0:2379 \
  --listen-peer-urls=https://0.0.0.0:2380 \
  --advertise-client-urls=https://<ip>:2379 \
  --advertise-peer-urls=https://<ip>:2380 \
  /tmp/etcd-backup.db

# Pod 재시작
exit
oc delete pod -n openshift-etcd <etcd-pod-name>
oc start pod -n openshift-etcd <etcd-pod-name>
```

#### 4 단계: 클러스터 상태 확인
복구된 etcd 가 정상적으로 동작하고 클러스터가 동기화되었는지 확인합니다.
```bash
oc get pods -n openshift-etcd
oc get nodes
```

---

## 5. etcd 성능 모니터링

etcd 의 성능 저하는 클러스터 전체의 지연 시간 증가로 이어집니다. 주요 지표는 다음과 같습니다.

### 핵심 지표
| 지표 | 설명 | 경고 기준 |
| :--- | :--- | :--- |
| **Backend Commit Duration** | 데이터 커밋에 걸리는 시간 | 100ms 이상 지속 시 주의 |
| **Backend Commit Latency** | 백엔드 커밋 지연 시간 | 50ms 이상 |
| **Leader Lease Duration** | 리더십 유지 시간 | 10 초 미만 (리더 변경 위험) |
| **Disk I/O Wait** | 디스크 대기 시간 | CPU 와 I/O 병목 신호 |
| **Memory Usage** | 메모리 사용량 | 고갈 시 OOM Kill 위험 |

### 모니터링 방법
1. **Prometheus + Grafana**: OCP 는 기본적으로 Prometheus 를 포함합니다. `openshift-etcd` 이름공간에서 `etcd_*` 메트릭을 확인하세요.
   ```bash
   oc get pods -n openshift-monitor
   ```
2. **oc describe 명령어**:
   ```bash
   oc describe pod -n openshift-etcd <etcd-pod-name>
   ```
   여기서 `Events` 섹션에 메모리 부족이나 디스크 공간 부족 관련 경고가 있는지 확인합니다.

---

## 6. etcd 장애 시 증상과 대응

etcd 장애는 즉각적인 클러스터 마비를 유발합니다.

### 주요 증상
- **API Server 연결 불가**: `oc get nodes` 명령어가 시간 초과 (Timeout) 또는 연결 거부 (Connection Refused) 를 반환합니다.
- **Pod 상태 불명확**: Pod 가 `Pending` 상태로 영원히 걸리거나, `CrashLoopBackOff` 를 반복합니다.
- **Scheduler 정지**: 새로운 Pod 의 스케줄링이 전혀 일어나지 않습니다.
- **API Server 로그 오류**: API Server 로그에 `etcd: mvcc: store full` 또는 `context deadline exceeded` 오류가 반복됩니다.

### 대응 전략
1. **즉각적인 격리**: 고장 난 Master 노드를 즉시 격리하여 클러스터가 완전히 마비되는 것을 방지합니다.
2. **로그 분석**: `etcd` Pod 의 로그를 확인하여 디스크 공간 부족, 메모리 부족, 또는 네트워크 분할 (
