<!-- source: ocp-upgrade-ko.md -->

# OpenShift Container Platform (OCP) 클러스터 업그레이드 가이드

## 1. 서론: 왜 업그레이드가 필요한가?

OpenShift Container Platform (OCP) 은 마이크로소프트의 Kubernetes 기반 분산 운영체제입니다. 클라우드 네이티브 환경에서 OCP 를 운영할 때, 정기적인 업그레이드는 보안 패치 적용, 새로운 기능 활용, 그리고 하드웨어/소프트웨어 호환성 유지에 필수적입니다. 그러나 OCP 는 복잡한 내부 컴포넌트 (etcd, CNI, CSI, Control Plane 등) 를 포함하고 있어, 잘못된 업그레이드 절차는 클러스터 전체의 다운타임을 초래할 수 있습니다. 따라서 체계적인 사전 점검, 명확한 경로 설정, 그리고 철저한 모니터링이 요구됩니다.

---

## 2. 업그레이드 채널 (Upgrade Channels)

Red Hat 공식 문서에 따르면, OCP 는 네 가지 주요 업그레이드 채널을 제공합니다. 각 채널은 업데이트의 빈도와 안정성 trade-off 를 다릅니다.

| 채널명 | 설명 | 특징 | 권장 대상 |
| :--- | :--- | :--- | :--- |
| **stable** | 표준 안정성 채널 | 가장 엄격한 테스트를 거친 최신 버전. 보안 패치와 기능 업데이트가 포함되지만, 매우 빈번하지 않음. | **일반 기업 환경**, 생산 시스템 |
| **fast** | 빠른 업데이트 채널 | stable 채널보다 더 자주 업데이트됨. 최신 기능과 보안 패치를 빠르게 받지만, 잠재적인 불안정성 존재. | R&D 환경, 비핵심 프로덕션 |
| **candidate** | 후보 채널 | 아직 완전히 검증되지 않은 버전. 최신 기능 테스트용. | **테스트 환경**, 벤치마킹 |
| **eus** | Extended Update Support | 과거 버전의 장기 지원 채널. 수명 종료 (EOL) 된 버전이 계속 보안 패치 받음. | 레거시 시스템 유지보수, 규정 준수 필수 시스템 |

**설정 확인 명령어:**
```bash
# 현재 설정된 채널 확인
oc get clusteroperator upgrades -o yaml | grep -A 5 "channel"

# 채널 변경 (권장: stable)
oc patch clusterversion cluster-version --type merge -p '{"spec":{"channel":"stable"}}'
```

---

## 3. 업그레이드 경로 (Upgrade Paths)

OCP 는 메이저 버전 간 업그레이드와 마이너 버전 간 업그레이드로 나뉩니다. Red Hat 공식 업그레이드 매트릭스를 반드시 확인해야 합니다.

*   **마이너 업그레이드 (Minor Upgrade):** 예를 들어 `4.12` 에서 `4.13` 으로 업그레이드하는 경우.
    *   **특징:** 비동기 업그레이드가 가능하며, 일반적으로 다운타임이 짧음. 대부분의 마이그레이션이 지원됨.
    *   **경로:** `4.12.x` -> `4.13.x` (직접 업그레이드 가능)

*   **메이저 업그레이드 (Major Upgrade):** 예를 들어 `4.12` 에서 `4.14` 로 업그레이드하는 경우.
    *   **특징:** 비동기 업그레이드 지원 여부가 버전마다 다름. 일부 버전 간에는 직접 업그레이드가 불가능하여 중간 버전을 거치거나 마이그레이션 툴을 사용해야 함.
    *   **주의:** API 그룹 변경, CRD 구조 변경, 네트워크 플러그인 호환성 문제가 발생할 수 있음.

**지원되는 경로 확인:**
```bash
# 공식 업그레이드 매트릭스 다운로드 및 확인
curl -L https://access.redhat.com/errata/RHBA-2024:xxxxx | grep -i upgrade
# 또는 Red Hat Customer Portal 에서 최신 Upgrade Paths 문서 참조
```

---

## 4. 사전 점검 (Pre-Upgrade Checks)

업그레이드 실행 전 필수적인 검증 단계입니다.

### 4.1 ClusterVersion 상태 확인
현재 클러스터 버전과 다음 버전 정보를 확인합니다.
```bash
oc get clusterversion
```

### 4.2 Deprecated API 체크
상업용 API 가 제거될 예정인 경우, 사전에 마이그레이션해야 합니다.
```bash
# deprecated API 사용 여부 확인
oc adm release info --channel stable --latest | grep -i api
# 또는
oc get crd | grep -i deprecated
```

### 4.3 ClusterOperator 상태 확인
모든 핵심 컴포넌트가 `Available` 상태인지 확인합니다.
```bash
oc get co
# 상태가 'Degraded' 인 경우 업그레이드 중단
```

### 4.4 etcd 백업 (가장 중요)
etcd 데이터베이스는 클러스터의 단일 진실 공급원입니다. 업그레이드 전 반드시 백업해야 합니다.
```bash
# etcd 백업 스크립트 실행 (예시)
oc exec -n openshift-etcd etcd-0 -- /usr/local/bin/etcdctl snapshot save backup.db --endpoints=[REDACTED_PRIVATE_IP]:2379 --cacert=/etc/etcd/ca.crt --cert=/etc/etcd/server.crt --key=/etc/etcd/server.key
```

---

## 5. 업그레이드 절차 (Upgrade Procedure)

OCP 는 비동기 업그레이드를 지원하므로, 웹 콘솔 또는 CLI 를 통해 시작할 수 있습니다.

### 5.1 웹 콘솔을 통한 업그레이드
1.  **Console -> Administration -> Cluster Version** 메뉴로 이동합니다.
2.  **Upgrade** 버튼을 클릭합니다.
3.  다음 버전 (Next Version) 을 선택하고 **Upgrade**를 누릅니다.
4.  진행 상황을 모니터링합니다.

### 5.2 CLI 를 통한 업그레이드
```bash
# 업그레이드 시작 (자동 채널 설정 시)
oc adm upgrade

# 특정 버전으로 강제 업그레이드 (권장하지 않음, 안정성 저하)
oc adm upgrade --to 4.14.0
```

---

## 6. 업그레이드 모니터링 (Monitoring)

업그레이드 중에는 `ClusterVersion` 과 `ClusterOperator` 상태를 지속적으로 모니터링해야 합니다.

### 6.1 ClusterVersion 상태 추적
```bash
# 업그레이드 진행 상태 확인
oc get clusterversion cluster-version -w
```
*   **Status:** `Upgrading` -> `Available`
*   **Ready:** `True`

### 6.2 ClusterOperator 상태 확인
모든 컴포넌트가 정상 작동하는지 확인합니다.
```bash
# 모든 ClusterOperator 상태 확인
oc get co -w
```
*   **Status:** `Available` (Degraded 상태가 지속되면 즉시 대응 필요)

### 6.3 Upgrade Status 상세 정보
```bash
oc get clusteroperator upgrades -o jsonpath='{.status.conditions[?(@.type=="Available")].message}'
```

---

## 7. 롤백 (Rollback) 전략

**중요:** OCP 는 기본적으로 **자동 롤백 기능을 지원하지 않습니다.** 업그레이드가 실패하거나 문제가 발생하면, 수동으로 이전 버전으로 되돌려야 합니다.

### 7.1 실패 시 대응 방법
1.  **etcd 복구:** 가장 중요한 단계입니다. 사전에 백업한 etcd 스냅샷을 복원해야 합니다.
    ```bash
    # etcd 스냅샷 복원 (예시)
    oc exec -n openshift-etcd etcd-0 -- /usr/local/bin/etcdctl snapshot restore backup.db --data-dir=/var/lib/etcd-from-backup
    ```
2.  **Control Plane 재부팅:** 복원된 etcd 를 기반으로 Control Plane 노드를 재부팅합니다.
    ```bash
    oc adm release upgrade --to 4.12.0 --force
    ```
3.  **Worker 노드 재부팅:** Control Plane 이 정상 작동하면 Worker 노드를 순차적으로 재부팅합니다.

**주의:** etcd 복구 실패 시 클러스터 데이터 손실이 발생할 수 있으므로, 백업의 중요성을 다시 한번 강조합니다.

---

## 8. Operator 업그레이드 (OLM)

OCP 는 Operator Lifecycle Manager (OLM) 을 통해 애플리케이션과 플랫폼 컴포넌트를 관리합니다.

*   **자동 업그레이드:** `Auto Upgrade` 전략을 설정하면 OLM 이 최신 버전으로 자동으로 업그레이드합니다.
    ```yaml
    # Subscription 예시
    apiVersion: operators.coreos.com/v1alpha1
    kind: Subscription
    metadata:
      name: example-operator
      namespace: openshift-operators
    spec:
      channel: fast
      installPlanApproval: Automatic
      name: example-operator
      source: redhat-operators
      sourceNamespace: openshift-marketplace
      config:
        params:
          - name: autoUpgrade
            value: "true"
    ```
*   **수동 업그레이드:** `oc patch subscription` 명령어를 사용하여 특정 버전으로 업그레이드하거나, `InstallPlan` 상태를 확인합니다.
    ```bash
    # 수동 업그레이드 요청
    oc patch subscription <operator-name> -n <namespace> --type merge -p '{"spec":{"channel":"fast"}}'
    ```

---

## 9. EUS (Extended Update Support) 전략

EUS 는 수명 종료 (EOL) 된 OCP 버전에도 보안 패치를 제공하는 장기 지원 채널입니다.

*   **활용 전략:**
    *   **규
