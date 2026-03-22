<!-- source: k8s-probe-config-ko.md -->

# Kubernetes/OCP Probe 설정 가이드 (Liveness, Readiness, Startup)

## 개요

Kubernetes의 Probe는 컨테이너의 상태를 확인하는 헬스체크 메커니즘입니다. 3종류의 Probe가 있으며, 각각 다른 목적으로 사용됩니다.

| Probe 종류 | 목적 | 실패 시 동작 |
|-----------|------|------------|
| **Liveness Probe** | 컨테이너가 살아있는지 확인 | 컨테이너 재시작 |
| **Readiness Probe** | 트래픽을 받을 준비가 됐는지 확인 | Service 엔드포인트에서 제거 (재시작 안 함) |
| **Startup Probe** | 앱이 처음 시작 완료됐는지 확인 | 컨테이너 재시작 (시작 중에만 동작) |

---

## 1. Liveness Probe 설정

컨테이너가 데드락 상태에 빠지거나 응답하지 않을 때 자동으로 재시작합니다.

### HTTP 방식 (가장 일반적)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-http
spec:
  containers:
  - name: liveness
    image: registry.k8s.io/liveness
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 3
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
      successThreshold: 1
```

### TCP 방식

```yaml
livenessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
```

### 명령어 방식

```yaml
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## 2. Readiness Probe 설정

트래픽을 받을 준비가 안 된 Pod을 Service 엔드포인트에서 일시적으로 제거합니다. DB 연결 대기, 캐시 로딩 등에 활용합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-http
spec:
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
      failureThreshold: 3
```

### Readiness vs Liveness 동작 차이
- **Readiness 실패**: Pod이 Service 엔드포인트에서 제거됨 → 트래픽 안 받음 → **재시작 안 함**
- **Liveness 실패**: 컨테이너 재시작 → 근본적 문제 해결 시도

---

## 3. Startup Probe 설정

앱 시작이 오래 걸리는 경우 사용합니다. Startup Probe가 성공할 때까지 Liveness/Readiness Probe가 비활성화됩니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: startup-probe
spec:
  containers:
  - name: slow-app
    image: slow-starting-app:1.0
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      periodSeconds: 10
```

위 설정에서 Startup Probe는 최대 **300초 (30 × 10초)** 동안 앱 시작을 기다립니다.

---

## 4. Probe 파라미터 상세

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `initialDelaySeconds` | 0 | 컨테이너 시작 후 첫 Probe 실행까지 대기 시간 |
| `periodSeconds` | 10 | Probe 실행 간격 |
| `timeoutSeconds` | 1 | Probe 응답 타임아웃 |
| `failureThreshold` | 3 | 연속 실패 횟수 (이 횟수 도달 시 실패 판정) |
| `successThreshold` | 1 | 연속 성공 횟수 (Readiness만 1 이상 의미) |

---

## 5. 실전 Deployment 예시 (3개 Probe 모두 적용)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: myapp:2.0
        ports:
        - containerPort: 8080
        startupProbe:
          httpGet:
            path: /healthz
            port: 8080
          failureThreshold: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          periodSeconds: 15
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
```

---

## 6. OCP에서 Probe 확인 명령어

```bash
# Pod의 Probe 설정 확인
oc describe pod <pod-name> -n <namespace>

# Probe 관련 이벤트 확인 (실패 시 이벤트 발생)
oc get events -n <namespace> --sort-by='.lastTimestamp'

# Pod 상태 확인 (Ready 상태)
oc get pods -n <namespace> -o wide

# 특정 Pod의 Probe 설정만 추출
oc get pod <pod-name> -o jsonpath='{.spec.containers[*].livenessProbe}'
```

---

## 7. 자주 발생하는 문제와 해결

| 문제 | 원인 | 해결 |
|------|------|------|
| Pod이 계속 재시작됨 | Liveness Probe 실패 | `initialDelaySeconds` 늘리기, 엔드포인트 확인 |
| Pod이 Ready가 안 됨 | Readiness Probe 실패 | 앱 로그 확인, 포트/경로 확인 |
| 시작 시 바로 죽음 | Startup Probe 없이 Liveness 적용 | Startup Probe 추가, `failureThreshold` × `periodSeconds` 충분히 |
| 트래픽이 안 들어옴 | Readiness Probe 미설정 | Readiness Probe 추가, Service 엔드포인트 확인 |
