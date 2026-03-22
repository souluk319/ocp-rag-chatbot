<!-- source: ocp-troubleshooting-advanced-ko.md -->

# OpenShift Container Platform 고급 트러블슈팅 가이드

안녕하세요, 신규 엔지니어 여러분. OpenShift Container Platform(OCP)은 Kubernetes 기반이지만, 그 위에 Red Hat의 추가 관리 레이어와 강력한 자동화 기능이 구축되어 있습니다. 따라서 일반적인 Kubernetes 문제뿐만 아니라, OCP 고유의 구성 요소에 대한 깊은 이해가 필요합니다.

이 가이드는 실제 운영 환경에서 발생할 수 있는 주요 장애 시나리오를 체계적으로 분석하고, 단계별 해결 방법을 제시합니다.

---

## 1. 노드 (Node) 트러블슈팅

노드는 클러스터의 물리적 또는 가상 기반 장치입니다. 노드가 정상적으로 작동하지 않으면 해당 노드에 배포된 Pod 들이 영향을 받거나 전체 클러스터의 안정성이 위협받을 수 있습니다.

### NotReady 상태 원인 및 해결
노드가 `NotReady` 상태가 된다는 것은 노드가 API 서버와 통신하지 않거나, 노드 상태 정보를 보고하는 `kubelet` 프로세스가 비정상적으로 종료되었음을 의미합니다.

**주요 원인:**
*   `kubelet` 프로세스 종료 또는 CPU/메모리 부족
*   노드 네트워크 인터페이스 (NIC) 문제 또는 라우팅 오류
*   CNI (Container Network Interface) 플러그인 실패
*   노드 커널 파라미터 (sysctl) 설정 오류

**진단 방법:**
먼저 노드 상태 확인 후, 해당 노드의 `kubelet` 로그를 확인해야 합니다.

```bash
# 노드 상태 확인
oc get nodes

# NotReady 노드 상세 정보 확인 (조건부)
oc describe node <not-ready-node-name>

# 노드 로그 확인 (kubelet 로그 위치는 보통 /var/log/kubelet.log)
oc debug node/<not-ready-node-name>
[root@node ~]# tail -f /var/log/kubelet.log
```

### 노드 드레인 및 코든 (Cordon)
고장난 노드에서 Pod 를 안전하게 제거하거나, 유지보수를 위해 노드를 격리해야 할 때 사용합니다.

*   **Cordon**: 노드를 스케줄링 대상에서 제외하지만, 기존에 실행 중인 Pod 은 유지합니다.
*   **Drain**: 노드에서 모든 Pod 을 강제 종료하고 다른 노드로 재스케줄링한 후, 노드를 코든합니다.

```bash
# 노드 코든 (스케줄링 방지)
oc adm cordon <node-name>

# 노드 드레인 (Pod 강제 이동 및 종료)
oc adm drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 다시 활성화 (Uncordon)
oc adm uncordon <node-name>
```

---

## 2. 네트워크 트러블슈팅

OpenShift 에서 네트워크 문제는 Pod 간 통신 불가, DNS 해결 실패, Service 연결 실패 등으로 나타납니다.

### Pod 간 통신 불가
同一 Namespace 내 또는 다른 Namespace 의 Pod 간에 통신이 안 되는 경우, 대부분 네트워크 정책 (NetworkPolicy) 또는 CNI 설정 오류입니다.

*   **NetworkPolicy 확인**: `oc get networkpolicy` 명령어로 해당 Namespace 에 정책이 적용되어 있는지 확인합니다.
*   **CNI 상태 확인**: `oc get pods -n openshift-sdn` (또는 CNI 플러그인 네임스페이스) 로 CNI Pod 가 Running 상태인지 확인합니다.

### DNS 문제
Pod 에서 외부 서비스나 내부 Service 의 호스트네임이 해결되지 않는 경우입니다.

*   **CoreDNS 상태 확인**:
    ```bash
    oc get pods -n kube-system -l app=coredns
    ```
*   **Pod 내부 DNS 테스트**:
    ```bash
    oc debug pod/<target-pod-name>
    # 컨테이너 내부에서 nslookup 실행
    nslookup <service-name>.<namespace>.svc.cluster.local
    ```
*   **Hosts 파일 확인**: `/etc/resolv.conf` 파일의 nameserver 가 올바른지 확인합니다.

### Service 연결 안 됨
Service IP 가 할당되었으나 Pod 에서 접근이 불가능한 경우입니다.

*   **Endpoint 확인**: Service 가 실제 Pod 에 트래픽을 전달하는지 확인합니다.
    ```bash
    oc get endpoints <service-name> -n <namespace>
    ```
    `NotReady` 상태의 Pod 가 Endpoint 에 포함되면, 해당 Pod 을 제거해야 합니다.
*   **Port 매핑 확인**: Service 의 `targetPort` 가 Pod 의 컨테이너 포트와 일치하는지 확인합니다.

---

## 3. 스토리지 트러블슈팅

PersistentVolumeClaim (PVC) 이 Pending 상태이거나 볼륨 마운트가 실패하는 경우가 빈번합니다.

### PVC Pending 원인
*   **StorageClass 부족**: 해당 PVC 가 요청하는 StorageClass 가 클러스터에 존재하지 않거나, 해당 클래스의 Provisioner 가 실행 중이 아닙니다.
    ```bash
    oc get sc
    oc get cs (StorageCluster 확인)
    ```
*   **Quota 초과**: Namespace 의 StorageQuota 를 초과했습니다.
    ```bash
    oc describe quota <quota-name> -n <namespace>
    ```

### 볼륨 마운트 실패 및 디스크 풀
*   **마운트 로그 확인**: PVC 에 바인딩된 PV 의 마운트 로그를 확인합니다.
    ```bash
    oc logs -n <storage-namespace> -l app=rook-ceph-operator # Ceph 기반인 경우
    # 또는 CSI 드라이버 로그 확인
    ```
*   **디스크 풀 (Disk Filling)**: 노드의 디스크가 가득 차면 새로운 Pod 이 스토리지를 마운트할 수 없습니다.
    ```bash
    df -h <node-name>
    ```
    사용률이 90% 이상일 경우, 로그를 정리하거나 불필요한 PVC 를 삭제해야 합니다.

---

## 4. 인증서 문제

OpenShift 는 CA 인증서를 기반으로 한 강력한 인증 체계를 사용합니다. 인증서 만료는 클러스터 전체의 마비로 이어질 수 있습니다.

### 증상
*   API 서버에 접근 불가 (`Connection refused` 또는 `x509: certificate signed by unknown authority`)
*   Web Console 로 로그인 불가
*   `oc login` 실패

### 해결 방법
인증서 만료는 주로 `openshift-config-managed` 또는 `openshift-ingress` 네임스페이스의 Pod 에서 발생합니다.

1.  **만료된 인증서 확인**:
    ```bash
    oc get pods -n openshift-config-managed
    oc logs -f <expired-cert-pod> | grep -i "certificate"
    ```
2.  **자동 리뉴얼 확인**: OpenShift 는 일반적으로 자동 리뉴얼을 수행하지만, 설정 오류로 인해 실패했을 수 있습니다.
    ```bash
    # 인증서 리뉴얼 트리거 (필요 시)
    oc patch csr <csr-name> -p '{"spec":{"signerName":"system:openshift-cluster-ca"}}'
    ```
3.  **API 서버 접근 불가 대응**: 인증서 만료 시 API 서버 Pod 이 재시작되며, 인증서가 재발급됩니다. 이 과정에서 클라이언트 측의 인증서 캐시를 삭제하거나, 임시로 `--insecure-skip-tls-verify` 옵션 (비추천, 테스트용) 을 사용할 수 있으나, 운영 환경에서는 정상적인 인증서 재발급을 기다리거나 수동으로 재발급 절차를 수행해야 합니다.

---

## 5. 리소스 부족

리소스 한계는 Pod 의 성능 저하나 전체적인 장애로 이어집니다.

### CPU/Memory Throttling
*   **증상**: Pod 로그에 `Throttled` 메시지가 자주 출력되거나, 응답 속도가 급격히 느려집니다.
*   **확인**:
    ```bash
    oc top pod <pod-name>
    ```
    `THROTTLED` 이 표시되면 CPU 리미트가 도달했음을 의미합니다.

### OOMKilled (Out Of Memory)
*   **증상**: Pod 가 갑자기 종료되고, 상태가 `OOMKilled` 로 변경됩니다.
*   **확인**:
    ```bash
    oc get pod <pod-name> -o wide
    # 이벤트 확인
    oc get events --field-selector involvedObject.name=<pod-name>
    ```
*   **대응**: 리소스 요청 (Request) 과 할당량 (Limit) 을 증가시켜야 합니다.
    ```yaml
    resources:
      requests:
        memory: "2Gi"
      limits:
        memory: "4Gi"
    ```

### Eviction 대응
노드가 리소스를 모두 소진하면, 우선순위가 낮은 Pod 이 강제로 종료 (Eviction) 됩니다.
*   **확인**: `oc describe node <node-name>` 에서 `Evictions` 항목 확인.
*   **대응**: 노드의 리소스 할당량을 늘리거나, 비효율적인 Pod 을 재스케줄링합니다.

---

## 6. etcd 문제

etcd 는 OpenShift 의 상태 데이터를 저장하는 핵심 저장소입니다. etcd 가 불안정하면 클러스터가 마비됩니다.

### 리더 선출 실패 (Leader Election Failure)
*   **증상**: `oc get nodes` 가 매우 느리게 반응하거나, API 서버
