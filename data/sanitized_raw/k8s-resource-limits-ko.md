<!-- source: k8s-resource-limits-ko.md -->

# Kubernetes/OCP Pod 리소스 제한 설정 가이드

## 개요

Pod의 컨테이너에 CPU와 메모리 리소스를 할당하려면 `resources.requests`와 `resources.limits`를 설정해야 합니다.

- **requests**: 컨테이너가 보장받는 최소 리소스. 스케줄러가 노드 배치 시 이 값을 참고합니다.
- **limits**: 컨테이너가 사용할 수 있는 최대 리소스. 이 값을 초과하면 메모리는 OOMKill, CPU는 스로틀링됩니다.

---

## 1. 메모리 리소스 설정

### 기본 YAML 예시

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: memory-demo
  namespace: mem-example
spec:
  containers:
  - name: memory-demo-ctr
    image: polinux/stress
    resources:
      requests:
        memory: "100Mi"
      limits:
        memory: "200Mi"
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "150M", "--vm-hang", "1"]
```

### 메모리 단위
| 단위 | 의미 | 예시 |
|------|------|------|
| Mi | 메비바이트 (1024² 바이트) | `128Mi` = 약 134MB |
| Gi | 기비바이트 (1024³ 바이트) | `1Gi` = 약 1.07GB |
| M | 메가바이트 (10⁶ 바이트) | `128M` = 128,000,000 바이트 |
| G | 기가바이트 (10⁹ 바이트) | `1G` = 1,000,000,000 바이트 |

### 메모리 limits 초과 시 동작
- 컨테이너가 limits 이상의 메모리를 사용하면 **OOMKilled** (Out of Memory) 됩니다.
- Pod의 `restartPolicy`에 따라 자동 재시작됩니다.
- `kubectl describe pod <pod-name>` 또는 `oc describe pod <pod-name>`으로 OOMKilled 상태를 확인할 수 있습니다.

---

## 2. CPU 리소스 설정

### 기본 YAML 예시

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-demo
  namespace: cpu-example
spec:
  containers:
  - name: cpu-demo-ctr
    image: vish/stress
    resources:
      requests:
        cpu: "0.5"
      limits:
        cpu: "1"
    args: ["--cpus", "2"]
```

### CPU 단위
| 표기 | 의미 |
|------|------|
| `1` | 1 vCPU (1 코어) |
| `0.5` | 0.5 vCPU (반 코어) |
| `500m` | 500 밀리코어 = 0.5 vCPU |
| `100m` | 100 밀리코어 = 0.1 vCPU |

`0.5`와 `500m`은 동일한 값입니다.

### CPU limits 초과 시 동작
- 메모리와 달리 CPU는 OOMKill되지 않고 **스로틀링** (throttling)됩니다.
- 컨테이너가 limits보다 많은 CPU를 사용하려고 하면 CPU 시간이 제한됩니다.
- 애플리케이션 성능이 저하되지만 강제 종료되지는 않습니다.

---

## 3. requests와 limits 모두 설정하는 실전 예시

### Deployment에 리소스 제한 적용

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "250m"
            memory: "64Mi"
          limits:
            cpu: "500m"
            memory: "128Mi"
```

### OCP에서 리소스 확인 명령어

```bash
# Pod의 리소스 사용량 확인
oc adm top pods -n <namespace>

# 특정 Pod의 리소스 설정 확인
oc describe pod <pod-name> -n <namespace>

# 노드별 리소스 사용량 확인
oc adm top nodes

# Pod의 리소스 requests/limits 확인
oc get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'
```

---

## 4. QoS (Quality of Service) 클래스

requests와 limits 설정에 따라 Pod의 QoS 클래스가 자동으로 결정됩니다.

| QoS 클래스 | 조건 | 우선순위 |
|-----------|------|---------|
| **Guaranteed** | 모든 컨테이너에 requests = limits 설정 | 가장 높음 (마지막에 eviction) |
| **Burstable** | 최소 하나의 컨테이너에 requests 설정 (limits와 다름) | 중간 |
| **BestEffort** | requests/limits 모두 미설정 | 가장 낮음 (먼저 eviction) |

### Guaranteed QoS 예시

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "128Mi"
```

### Burstable QoS 예시

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "64Mi"
  limits:
    cpu: "500m"
    memory: "128Mi"
```

---

## 5. LimitRange로 기본값 설정

네임스페이스에 LimitRange를 생성하면, 리소스 설정이 없는 Pod에 자동으로 기본 requests/limits가 적용됩니다.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: my-namespace
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "64Mi"
    type: Container
```

```bash
# LimitRange 생성
oc apply -f limitrange.yaml -n my-namespace

# LimitRange 확인
oc describe limitrange default-limits -n my-namespace
```

---

## 6. ResourceQuota로 네임스페이스 전체 제한

ResourceQuota는 네임스페이스 단위로 총 리소스 사용량을 제한합니다.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: my-namespace
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "20"
```

```bash
# ResourceQuota 생성
oc apply -f quota.yaml -n my-namespace

# ResourceQuota 사용 현황 확인
oc describe resourcequota compute-quota -n my-namespace
```

---

## 7. 리소스 설정 권장 사항

| 항목 | 권장 사항 |
|------|---------|
| requests | 평상시 사용량 기준으로 설정 |
| limits | 피크 사용량 × 1.2~1.5 정도로 설정 |
| CPU limits | 필수는 아니지만 멀티테넌트 환경에서는 설정 권장 |
| 메모리 limits | 반드시 설정 (OOMKill 방지를 위한 적절한 값) |
| QoS 클래스 | 중요 워크로드는 Guaranteed, 일반은 Burstable |
| LimitRange | 네임스페이스마다 기본값 설정 권장 |
| ResourceQuota | 프로젝트별 리소스 남용 방지를 위해 설정 |
