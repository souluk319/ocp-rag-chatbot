<!-- source: ocp-backup-recovery-ko.md -->

# OpenShift Container Platform 백업 및 재해복구 (DR) 가이드

## 1. etcd 백업의 중요성

OpenShift Cluster 의 핵심은 상태 저장소인 **etcd**입니다. etcd 는 클러스터의 모든 구성 정보 (API Objects, 설정, 인증서, 네트워크 정책 등) 를 Key-Value 형태로 영구적으로 저장합니다. **etcd 가 손상되거나 데이터가 손실되면 클러스터 전체가 마비 (Brick) 되어 재부팅이 불가능한 상태가 됩니다.**

따라서 etcd 백업은 애플리케이션 데이터 백업보다 더 우선순위가 높습니다. etcd 백업이 필수적인 이유는 다음과 같습니다.

*   **클러스터 재부팅 (Cluster Restore) 의 유일한 수단**: 노드가 모두 죽거나 디스크가 손상되었을 때, etcd 스냅샷을 이용해 클러스터를 다시 구축할 수 있는 유일한 방법입니다.
*   **일관성 유지**: etcd 는 분산 데이터베이스이므로 일관성을 유지하는 스냅샷 생성이 필수적입니다.
*   **비즈니스 연속성**: 예상치 못한 장애 시 최소한의 다운타임을 보장하기 위한 마지막 방패입니다.

## 2. etcd 백업 절차

etcd 백업은 주기적인 수동 스냅샷 생성과 자동화 스크립트를 통해 수행합니다.

### 2.1 수동 스냅샷 생성
관리자가 직접 `etcdctl` 명령어를 사용하여 스냅샷 파일을 생성합니다.

```bash
# 마스터 노드에서 실행 (root 또는 oc admin 권한 필요)
ETCDCTL_API=3 etcdctl --endpoints=https://[<master-ip>]:2379 \
  --cacert=/etc/etcd/ssl/ca.crt \
  --cert=/etc/etcd/ssl/etcd-server.crt \
  --key=/etc/etcd/ssl/etcd-server.key \
  snapshot save /var/lib/etcd/member/snap/db.bak-$(date +%F).db
```

### 2.2 자동 백업 스크립트 예시
정기적인 백업을 위해 다음과 같은 스크립트를 작성하여 Cron Job 또는 Ansible 과 연동할 수 있습니다.

```bash
#!/bin/bash
# /usr/local/bin/etcd_backup.sh

BACKUP_DIR="/var/backups/etcd"
DATE=$(date +%F)
BACKUP_FILE="${BACKUP_DIR}/etcd-snapshot-${DATE}.db"

mkdir -p ${BACKUP_DIR}

ETCDCTL_API=3 etcdctl --endpoints=[REDACTED_INTERNAL_URL] \
  --cacert=/etc/etcd/ssl/ca.crt \
  --cert=/etc/etcd/ssl/etcd-server.crt \
  --key=/etc/etcd/ssl/etcd-server.key \
  snapshot save ${BACKUP_FILE}

# 30 일 전의 백업 파일 삭제
find ${BACKUP_DIR} -name "etcd-snapshot-*.db" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

## 3. etcd 복구 절차

etcd 스냅샷을 사용하여 클러스터를 복구하는 과정은 매우 까다롭습니다. 이는 클러스터의 모든 노드를 초기화하고 스냅샷에서 재구축해야 합니다.

### 3.1 복구 단계
1.  **클러스터 상태 확인**: 현재 클러스터가 마비되었는지 확인합니다.
2.  **etcdctl snapshot restore 실행**: 백업된 스냅샷 파일로 새로운 etcd 데이터 디렉토리를 생성합니다.
    ```bash
    ETCDCTL_API=3 etcdctl snapshot restore \
      --data-dir=/var/lib/etcd-new \
      /var/backups/etcd-snapshot-2023-10-27.db
    ```
3.  **인증서 및 설정 재구축**: `etcdctl snapshot endpoint-health` 등을 통해 새로운 etcd 가 정상 작동하는지 확인 후, 클러스터 인증서와 설정을 다시 생성합니다.
4.  **OpenShift 클러스터 재부팅**: `oc adm restore` 명령어를 통해 OpenShift API 를 재시작하고 클러스터 상태를 복원합니다.
    ```bash
    oc adm restore --from-dir=/var/lib/etcd-new
    ```
5.  **노드 재부팅**: 모든 마스터 및 워커 노드를 재부팅하여 새 etcd 구성을 적용합니다.

> **주의**: etcd 복구 시에는 반드시 클러스터 내 모든 노드를 정지한 후 수행해야 하며, 데이터 손실 위험이 있으므로 사전에 반드시 테스트 환경에서 검증해야 합니다.

## 4. OADP (OpenShift API for Data Protection)

OADP 는 Red Hat 공식적으로 지원하는 **Velero** 기반의 백업 솔루션입니다. etcd 백업과 달리 애플리케이션, PV(Persistent Volume), 네임스페이스 단위의 로직적 데이터를 백업하는 데 최적화되어 있습니다.

### 4.1 핵심 특징
*   **Velero 통합**: Kubernetes 의 로직적 리소스 (Deployments, ConfigMaps, Secrets 등) 와 볼륨 데이터를 백업합니다.
*   **Cloud Native**: AWS S3, GCS, Azure Blob 등 다양한 클라우드 스토어와 연동하여 백업 데이터를 외부에 저장합니다.
*   **Namespace Backup**: 특정 네임스페이스 전체를 한 번에 백업하여 재해 복구 시 시간을 단축합니다.

### 4.2 설치 및 구성 예시
OADP 를 설치한 후 BackupRepository 와 BackupLocation 을 정의합니다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-cloud-credentials
  namespace: openshift-adp
type: Opaque
stringData:
  accessKeyID: AKIAIOSFODNN7EXAMPLE
  secretAccessKey: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
---
apiVersion: v1
kind: Secret
metadata:
  name: aws-cloud-credentials
  namespace: openshift-adp
type: Opaque
stringData:
  accessKeyID: AKIAIOSFODNN7EXAMPLE
  secretAccessKey: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

## 5. 애플리케이션 백업 전략

OADP 를 통해 애플리케이션을 백업할 때는 데이터가 저장된 PV(Persistent Volume) 를 함께 백업하는 것이 핵심입니다.

### 5.1 PV 데이터 백업
OADP 는 `BackupLocation` 이 설정된 스토어 (예: S3 Bucket) 에 로직 리소스와 볼륨 데이터를 압축하여 저장합니다.

```bash
# 네임스페이스 단위 전체 백업
oc backup create my-app-backup --namespace my-app --include-namespaces my-app

# 특정 리소스만 백업
oc backup create my-deploy-backup --resource=deployments/my-deployment --namespace my-app
```

### 5.2 복구 절차
복구 시에는 백업된 데이터를 새로운 클러스터나 기존 클러스터의 다른 네임스페이스로 복원할 수 있습니다.

```bash
# 네임스페이스 복원
oc restore create my-app-restore --from=backup/my-app-backup --namespace my-app
```

## 6. 재해복구 (DR) 전략

재해복구 계획은 **RPO (Recovery Point Objective)** 와 **RTO (Recovery Time Objective)** 를 기반으로 수립됩니다.

| 전략 유형 | 설명 | RPO | RTO | 적용 사례 |
| :--- | :--- | :--- | :--- :--- |
| **Active-Passive** | 한 클러스터가 서비스 제공, 다른 클러스터는 대기 중. 장애 발생 시 전환. | 낮음 (수 분~시간) | 높음 (수 시간~수 일) | 비용 효율적인 대규모 기업용 DR |
| **Active-Active** | 두 클러스터가 동시에 서비스를 제공. 트래픽 분산. | 매우 낮음 (실시간) | 매우 낮음 (분 단위) | 금융, 실시간 거래 시스템 |
| **Backup & Restore** | 주기적인 백업 파일 저장 후 필요시 수동 복구. | 높음 (백업 주기 의존) | 매우 높음 (복구 작업 시간) | 비임계 중요 애플리케이션 |

**실무 팁**: OCP 환경에서는 Active-Passive 모드를 가장 많이 사용합니다. DR 사이트 (Secondary Cluster) 에 OADP 를 설치하여 Primary Cluster 의 백업을 자동으로 동기화하도록 구성합니다.

## 7. 클러스터 인증서 갱신

OpenShift 클러스터는 CA(Certificate Authority) 인증서를 사용하여 노드 간 통신 및 API 서버 인증을 수행합니다. 인증서가 만료되면 클러스터가 마비될 수 있습니다.

### 7.1 인증서 만료 대응
1.  **확인**: `oc get csr` 또는 `oc adm certificate info` 명령어로 인증서 만료 일자를 확인합니다.
2.  **신규 인증서 생성**: Red Hat 공식 가이드에 따라 새로운 인증서를 생성합니다.
3.  **인증서 교체**: 마스터
