<!-- source: ocp-pending-pod-troubleshooting-ko.md -->

# OCP/Kubernetes Pod Pending 상태 트러블슈팅 가이드

## 개요

Pod가 `Pending` 상태에 머무르면 아직 노드에 스케줄링되지 않은 것입니다. 스케줄러가 Pod를 배치할 적절한 노드를 찾지 못하거나, 필요한 리소스가 준비되지 않은 경우입니다.

## Pending 관련 상태

| 상태 | 설명 |
|---|---|
| Pending | Pod가 생성되었지만 아직 노드에 배치되지 않음 |
| Unschedulable | 스케줄러가 조건에 맞는 노드를 찾지 못함 |

## 원인별 진단 및 해결 방법

### 1. 리소스 부족 (Insufficient Resources)

클러스터의 모든 노드에 요청된 CPU/메모리를 할당할 여유가 없는 경우입니다.

**진단:**
```bash
# Pod 이벤트 확인
oc describe pod <pod-name> -n <namespace>
# Events:
#   Warning  FailedScheduling  Insufficient cpu / Insufficient memory

# 노드별 리소스 사용량 확인
oc adm top nodes

# 특정 노드의 할당 가능 리소스 확인
oc describe node <node-name>
# Allocatable 섹션의 cpu, memory 확인
# Allocated resources 섹션의 사용량 확인
```

**해결:**
```bash
# Pod의 리소스 요청 줄이기
oc set resources deployment/<deploy-name> --requests=cpu=100m,memory=128Mi

# 또는 노드 추가 (클러스터 관리자)
# MachineSets 조정으로 노드 스케일 아웃

# ResourceQuota 확인 및 조정
oc get resourcequota -n <namespace>
oc describe resourcequota <quota-name> -n <namespace>
```

### 2. NodeSelector/Affinity 조건 불일치

Pod에 설정된 nodeSelector 또는 nodeAffinity 조건을 만족하는 노드가 없는 경우입니다.

**진단:**
```bash
# Pod의 nodeSelector 확인
oc get pod <pod-name> -o jsonpath='{.spec.nodeSelector}'

# Pod의 affinity 확인
oc get pod <pod-name> -o jsonpath='{.spec.affinity}'

# 노드 레이블 확인
oc get nodes --show-labels

# 특정 레이블의 노드 검색
oc get nodes -l <key>=<value>
```

**해결:**
```bash
# 노드에 레이블 추가
oc label node <node-name> <key>=<value>

# 또는 Deployment에서 nodeSelector 수정/제거
oc edit deployment <deploy-name>
# spec.template.spec.nodeSelector 수정
```

### 3. Taint/Toleration 불일치

노드에 Taint가 설정되어 있는데 Pod에 해당 Toleration이 없는 경우입니다.

**진단:**
```bash
# 노드의 Taint 확인
oc describe node <node-name> | grep -A5 Taints

# 모든 노드의 Taint 확인
oc get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints

# Pod의 Toleration 확인
oc get pod <pod-name> -o jsonpath='{.spec.tolerations}'
```

**해결:**
```yaml
# Pod에 Toleration 추가
spec:
  template:
    spec:
      tolerations:
      - key: "node-role.kubernetes.io/infra"
        operator: "Exists"
        effect: "NoSchedule"
```

### 4. PVC Pending (스토리지 미준비)

Pod가 요청한 PersistentVolumeClaim(PVC)이 아직 Bound 되지 않은 경우입니다.

**진단:**
```bash
# PVC 상태 확인
oc get pvc -n <namespace>
# STATUS가 Pending이면 PV가 할당되지 않은 것

# PVC 이벤트 확인
oc describe pvc <pvc-name> -n <namespace>

# StorageClass 확인
oc get storageclass
```

**해결:**
```bash
# 사용 가능한 StorageClass 확인
oc get storageclass

# PVC의 StorageClass가 올바른지 확인
oc get pvc <pvc-name> -o jsonpath='{.spec.storageClassName}'

# StorageClass가 없으면 기본값 설정 또는 PVC에 명시
# Dynamic provisioning이 설정되어 있는지 확인
```

### 5. ImagePullSecrets 누락으로 인한 대기

ServiceAccount에 imagePullSecrets가 없어서 이미지 풀 전에 Pending 상태가 되는 경우입니다.

**진단:**
```bash
# ServiceAccount의 imagePullSecrets 확인
oc get serviceaccount default -o jsonpath='{.imagePullSecrets}' -n <namespace>
```

**해결:**
```bash
# ServiceAccount에 Pull Secret 연결
oc secrets link default <secret-name> --for=pull -n <namespace>
```

## 일반적인 디버깅 순서

1. `oc get pods` 로 Pending 상태 확인
2. `oc describe pod <pod-name>` 으로 Events 섹션 확인
3. 이벤트 메시지에 따라 원인 분류:
   - `Insufficient cpu/memory` → 리소스 부족 → 요청 줄이거나 노드 추가
   - `node(s) didn't match node selector` → nodeSelector 수정 또는 노드 레이블 추가
   - `node(s) had taints` → Toleration 추가
   - `persistentvolumeclaim not found / not bound` → PVC 상태 확인
4. 수정 후 Pod 재생성: `oc delete pod <pod-name>` (Deployment가 자동 재생성)

## 자주 사용하는 명령어 요약

```bash
# Pod 상태 확인
oc get pods -n <namespace>

# Pod 이벤트/스케줄링 실패 원인 확인
oc describe pod <pod-name> -n <namespace>

# 노드별 리소스 사용량
oc adm top nodes

# 노드 상세 (Allocatable, Taints, Labels)
oc describe node <node-name>

# ResourceQuota 확인
oc get resourcequota -n <namespace>

# PVC 상태 확인
oc get pvc -n <namespace>
```
