<!-- source: ocp-resource-management-ko.md -->

# OCP 리소스 관리 & 최적화 가이드

안녕하세요, 신입 엔지니어 여러분. OpenShift Container Platform (OCP) 에서 안정적인 워크로드를 운영하기 위해서는 단순히 Pod 를 띄우는 것을 넘어, 리소스를 효율적으로 할당하고 모니터링하는 능력이 필수적입니다. 이 가이드에서는 OCP 의 핵심 리소스 관리 도구들을 체계적으로 설명하며, 실제 환경에서 어떻게 적용해야 하는지 실무적인 팁을 제공합니다.

## 1. ResourceQuota: 네임스페이스별 리소스 할당량 설정

### 개념 설명
`ResourceQuota` 는 특정 네임스페이스 (Namespace) 에 할당할 수 있는 리소스의 총량을 제한하는 객체입니다. 이는 "네임스페이스 내의 모든 Pod 가 합쳐서 사용할 수 있는 CPU 와 메모리의 총량"을 정의합니다.

이 기능은 다음과 같은 문제를 해결합니다:
- **무제한 리소스 소비 방지**: 특정 개발자가 작업을 하다가 전체 클러스터의 리소스를 고갈시키는 것을 막습니다.
- **비용 통제**: 각 팀이나 프로젝트별로 예산을 명확히 할 수 있습니다.
- **리소스 예측**: 클러스터의 전체 용량 계획을 수립할 때 기준이 됩니다.

### 핵심 특징
- **적용 범위**: 네임스페이스 단위로만 적용 가능합니다.
- **제한 대상**: Pod 의 `requests` 와 `limits` 를 모두 포함하며, PVC (PersistentVolumeClaim) 의 용량도 제한할 수 있습니다.
- **오버할당 방지**: 할당량을 초과하면 Pod 생성이 거부됩니다.

### YAML 예시
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "4"              # CPU 요청 총량: 4 코어
    requests.memory: 8Gi           # 메모리 요청 총량: 8GB
    limits.cpu: "8"                # CPU 제한 총량: 8 코어
    limits.memory: 16Gi            # 메모리 제한 총량: 16GB
    pods: "50"                     # 최대 Pod 개수: 50 개
    persistentvolumeclaims: "10"   # 최대 PVC 개수: 10 개
```

---

## 2. LimitRange: 컨테이너 기본/최대 리소스 설정

### 개념 설명
`LimitRange` 은 네임스페이스 내의 Pod 에 대한 리소스 제한 (`limits`) 과 최소 요청 (`min`) 을 강제하는 객체입니다. 사용자가 리소스를 명시하지 않고 Pod 를 생성할 때, 자동으로 기본값을 적용하여 "리소스가 누락된 Pod"를 방지합니다.

### 핵심 특징 비교

| 기능 | ResourceQuota | LimitRange |
| :--- | :--- | :--- |
| **적용 단위** | 네임스페이스 전체 (합계) | 네임스페이스 내 개별 컨테이너 |
| **주요 목적** | 총량 제한 (Budgeting) | 기본값 설정 및 안전장치 (Safety) |
| **requests 설정** | 가능 (총량) | 가능 (최소값) |
| **limits 설정** | 가능 (총량) | 가능 (최대값) |
| **Pod 생성 거부** | 할당량 초과 시 | 최소/최대 값 미준수 시 |

### YAML 예시
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: development
spec:
  limits:
    - default:                  # 기본값 (사용자가 명시 안 하면 적용)
        cpu: 500m
        memory: 512Mi
      defaultRequest:          # 기본 요청값
        cpu: 250m
        memory: 256Mi
      type: Container
    - max:                      # 최대 허용값
        cpu: 2
        memory: 4Gi
      min:                      # 최소 허용값
        cpu: 100m
        memory: 128Mi
      type: Container
```

---

## 3. PriorityClass: Pod 우선순위 설정

### 개념 설명
클러스터의 리소스가 부족할 때 (예: 노드 오버로드), 어떤 Pod 가 먼저 리소스를 확보할지 결정하는 기준입니다. `PriorityClass` 는 우선순위 값을 정의하고, Pod 는 이 클래스를 참조하여 우선순위를 갖습니다.

### 동작 원리
1. 노드가 리소스를 확보할 수 없을 때, 우선순위가 낮은 Pod 가 먼저 종료 (Evict) 됩니다.
2. `system-node-critical` 과 `system-cluster-critical` 은 시스템 핵심 Pod 로 설정되어 절대 종료되지 않습니다.
3. 일반 워크로드 간 충돌 시, 높은 우선순위를 가진 Pod 가 리소스를 선점합니다.

### 실무 팁
- 우선순위 값은 정수이며, 클러스터마다 고유해야 합니다.
- 너무 높은 우선순위를 주는 Pod 가 많으면, 낮은 우선순위의 Pod 가 계속 종료되는 "리소스 쉘터" 현상이 발생할 수 있으니 주의하세요.

---

## 4. VPA (Vertical Pod Autoscaler): CPU/Memory 자동 조절

### 개념 설명
`Vertical Pod Autoscaler (VPA)` 는 Pod 의 개수 (Horizontal) 가 아닌, **개별 Pod 의 CPU 와 메모리 사용량**을 실시간으로 모니터링하여 `requests` 와 `limits` 를 자동으로 조정합니다.

### 장점과 한계
- **장점**: 오버프로비저닝 (과도한 할당) 을 줄여 비용을 절감하고, 언더프로비저닝으로 인한 성능 저하를 방지합니다.
- **한계**:
  - 수평 확장 (HPA) 과는 달리 Pod 개수를 늘리지 않습니다.
  - 일부 컨트롤러 (StatefulSet, Deployment 등) 에서 재시작 시 기존 Pod 의 리소스를 유지하지 못할 수 있어, 사용 시 주의가 필요합니다.
  - OpenShift 환경에서는 `ResourceQuota` 와 충돌할 수 있으므로, VPA 가 리소스를 증가시킬 때 할당량을 초과하지 않도록 모니터링해야 합니다.

---

## 5. HPA (Horizontal Pod Autoscaler): 메트릭 기반 Pod 수 자동 조절

### 개념 설명
`Horizontal Pod Autoscaler (HPA)` 는 CPU 사용률, 메모리 사용량, 커스텀 메트릭 등 특정 조건을 만족하면 Pod 의 개수를 자동으로 늘리거나 줄입니다. 트래픽이 급증할 때 대응하는 가장 일반적인 스케일링 방식입니다.

### YAML 예시
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: development
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # CPU 사용률이 70% 를 넘으면 Pod 추가
```

---

## 6. Cluster Autoscaler: 노드 수 자동 조절

### 개념 설명
클라우드 환경 (AWS, Azure, GCP 등) 에서 HPA 가 Pod 를 늘렸는데, 해당 Pod 가 실행될 노드가 없다면 어떻게 할까요? `Cluster Autoscaler` 가 이 문제를 해결합니다.

Cluster Autoscaler 는 다음과 같은 시나리오에서 동작합니다:
1. HPA 가 Pod 를 추가하려 하지만 노드 자원이 부족함을 감지합니다.
2. Cluster Autoscaler 가 클라우드 공급자에게 새로운 노드를 프로비저닝합니다.
3. 새로운 노드가 준비되면 Pod 가 그 노드로 스케줄링됩니다.
4. 트래픽이 줄어든 후 노드가 비어있으면 자동으로 노드를 삭제합니다 (비용 절감).

### 주의사항
- 온프레미스 (On-premise) 환경에서는 Cluster Autoscaler 를 사용하지 않으며, 노드 풀 (Node Pool) 을 수동으로 관리하거나 다른 스케일링 전략을 사용해야 합니다.

---

## 7. 용량 계획: 노드 사이징 및 워크로드 산정

### 노드 사이징 전략
올바른 노드 크기를 선택하는 것이 비용과 성능의 핵심입니다.

1. **작업 부하 분석**: 워크로드의 평균 CPU/Memory 사용량을 확인합니다.
2. **부스트 팩터 고려**: 트래픽이 급증할 때를 대비하여 평균 사용량의 1.5~2 배 정도를 고려합니다.
3. **노드 풀 분리**:
   - **Compute Optimized**: CPU 집약적 워크로드 (예: 데이터 처리, 머신러닝).
   - **Memory Optimized**: 메모리 집약적 워크로드 (예: 인메모리 캐시, DB).
   - **General Purpose**: 일반 웹 서버 및 마이크로서비스.

### 워크로드별 리소스 산정 방법
- **비동기 작업 (Batch Jobs)**: `requests` 는 낮게, `limits` 는 높게 설정하여 다른 워크로드와 리소스를 공유하도록 합니다.
- **실시간 서비스**: `requests` 와 `limits` 를 동일하게 설정하여 오버헤드를 방지하고, H
