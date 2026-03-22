<!-- source: k8s-pod-operations-ko.md -->

# Kubernetes Pod 운영 가이드

## Health Check (헬스 체크) - Probe

### Probe란?
Probe(프로브)는 Kubernetes가 컨테이너의 상태를 주기적으로 확인하는 메커니즘입니다.
kubelet이 컨테이너에 대해 주기적으로 진단을 수행하여, 컨테이너가 정상인지 판단합니다.

Kubernetes는 3가지 Probe를 제공합니다:
- Liveness Probe: 컨테이너가 살아있는지 확인
- Readiness Probe: 컨테이너가 트래픽을 받을 준비가 되었는지 확인
- Startup Probe: 컨테이너 애플리케이션이 시작되었는지 확인

### Liveness Probe (생존 프로브)

#### 개념
Liveness Probe는 "이 컨테이너가 아직 살아있는가?"를 확인합니다.
Liveness Probe가 실패하면 kubelet이 컨테이너를 **재시작(restart)**합니다.

#### 사용 시점
- 애플리케이션이 데드락에 빠져 응답하지 않는 경우
- 프로세스는 살아있지만 실제로는 동작하지 않는 경우
- 메모리 누수로 점점 느려지다가 멈추는 경우

#### 핵심 동작
- Probe 실패 → kubelet이 컨테이너를 **kill** → restartPolicy에 따라 재시작
- Pod는 그대로 유지되고, 내부 컨테이너만 재시작됨
- 주의: initialDelaySeconds를 충분히 설정하지 않으면 앱 시작 중에 재시작 루프 발생

#### YAML 예시
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-example
spec:
  containers:
  - name: app
    image: my-app:1.0
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 15    # 컨테이너 시작 후 15초 뒤 첫 검사
      periodSeconds: 10          # 10초마다 검사
      failureThreshold: 3        # 3번 연속 실패 시 재시작
      timeoutSeconds: 3          # 응답 대기 시간 3초
```

### Readiness Probe (준비 프로브)

#### 개념
Readiness Probe는 "이 컨테이너가 트래픽을 받을 준비가 되었는가?"를 확인합니다.
Readiness Probe가 실패하면 해당 Pod를 **Service 엔드포인트에서 제거**합니다.
컨테이너를 재시작하지는 않습니다.

#### 사용 시점
- 애플리케이션 시작 시 DB 연결, 캐시 워밍업 등 초기화가 필요한 경우
- 일시적 부하로 요청을 처리할 수 없는 경우
- 외부 의존성(DB, API)이 일시적으로 불가한 경우

#### 핵심 동작
- Probe 실패 → Pod가 Service의 endpoints에서 제외됨 → 트래픽이 안 들어옴
- Probe 성공으로 돌아오면 → 다시 endpoints에 추가됨 → 트래픽 수신 재개
- 컨테이너는 계속 실행 중 (재시작하지 않음)

#### YAML 예시
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-example
spec:
  containers:
  - name: app
    image: my-app:1.0
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 3
```

### Startup Probe (시작 프로브)

#### 개념
Startup Probe는 "이 컨테이너의 애플리케이션이 시작 완료되었는가?"를 확인합니다.
Startup Probe가 설정되면 성공할 때까지 Liveness/Readiness Probe가 비활성화됩니다.

#### 사용 시점
- 시작 시간이 오래 걸리는 레거시 애플리케이션
- JVM 기반 앱처럼 워밍업이 필요한 경우
- Liveness Probe의 initialDelaySeconds를 너무 길게 잡고 싶지 않을 때

#### YAML 예시
```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30     # 30번까지 재시도
  periodSeconds: 10         # 10초마다 → 최대 300초(5분) 대기
```

### Liveness vs Readiness vs Startup Probe 비교

| 비교 항목 | Liveness Probe | Readiness Probe | Startup Probe |
|-----------|---------------|-----------------|---------------|
| 질문 | 살아있는가? | 트래픽 받을 준비 됐는가? | 시작 완료됐는가? |
| 실패 시 동작 | 컨테이너 재시작 | Service에서 제외 | 컨테이너 재시작 |
| Pod 유지 | 유지 (컨테이너만 재시작) | 유지 | 유지 (컨테이너만 재시작) |
| 트래픽 영향 | 재시작 중 트래픽 중단 | 트래픽만 차단 | 시작 전 트래픽 차단 |
| 실행 시점 | 항상 (주기적) | 항상 (주기적) | 시작 시에만 |
| 비유 | 심장이 뛰는가? | 일할 준비 됐는가? | 출근했는가? |

### Probe 방식 3가지

#### 1. HTTP GET
```yaml
httpGet:
  path: /healthz
  port: 8080
```
지정된 경로로 HTTP GET 요청. 2xx~3xx 응답이면 성공.

#### 2. TCP Socket
```yaml
tcpSocket:
  port: 3306
```
지정된 포트로 TCP 연결 시도. 연결되면 성공. DB 등에 적합.

#### 3. Exec Command
```yaml
exec:
  command:
  - cat
  - /tmp/healthy
```
컨테이너 내에서 명령어 실행. 종료 코드 0이면 성공.

### 실무 권장 설정

```yaml
containers:
- name: app
  image: my-app:1.0
  # 시작 프로브: 최대 5분 대기
  startupProbe:
    httpGet:
      path: /healthz
      port: 8080
    failureThreshold: 30
    periodSeconds: 10
  # 생존 프로브: 30초 무응답 시 재시작
  livenessProbe:
    httpGet:
      path: /healthz
      port: 8080
    periodSeconds: 10
    failureThreshold: 3
    timeoutSeconds: 3
  # 준비 프로브: 15초 무응답 시 트래픽 차단
  readinessProbe:
    httpGet:
      path: /ready
      port: 8080
    periodSeconds: 5
    failureThreshold: 3
    timeoutSeconds: 3
```

## Pod 리소스 관리

### Resource Requests와 Limits

#### 개념
- Requests: Pod가 최소한 필요한 리소스량 (스케줄링 기준)
- Limits: Pod가 사용할 수 있는 최대 리소스량 (초과 시 제한/종료)

#### YAML 예시
```yaml
containers:
- name: app
  resources:
    requests:
      cpu: 100m        # 0.1 CPU 코어
      memory: 128Mi    # 128MB 메모리
    limits:
      cpu: 500m        # 0.5 CPU 코어
      memory: 512Mi    # 512MB 메모리
```

#### CPU 단위
- 1 = 1 CPU 코어
- 100m = 0.1 코어 (밀리코어)
- Limits 초과 시: CPU throttling (느려짐, 종료하지 않음)

#### Memory 단위
- Mi = 메비바이트 (1Mi = 1,048,576 bytes)
- Gi = 기비바이트
- Limits 초과 시: OOMKilled (강제 종료)

### QoS (Quality of Service) 클래스

Pod의 리소스 설정에 따라 QoS 클래스가 자동으로 결정됩니다:

| QoS 클래스 | 조건 | 우선순위 |
|-----------|------|---------|
| Guaranteed | 모든 컨테이너에 requests = limits 설정 | 최고 (가장 마지막에 퇴출) |
| Burstable | requests와 limits가 다르거나 일부만 설정 | 중간 |
| BestEffort | requests, limits 모두 미설정 | 최저 (가장 먼저 퇴출) |

노드 리소스가 부족할 때 BestEffort → Burstable → Guaranteed 순서로 Pod가 퇴출(Eviction)됩니다.

## Pod 스케줄링

### Node Selector
특정 라벨이 있는 노드에만 Pod를 배치합니다.
```yaml
spec:
  nodeSelector:
    disktype: ssd
    zone: ap-northeast-2a
```

### Node Affinity
nodeSelector보다 유연한 노드 선택 규칙입니다.
```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: zone
            operator: In
            values: ["ap-northeast-2a", "ap-northeast-2c"]
```

### Taints와 Tolerations
Taint: 노드에 설정하여 특정 Pod만 배치되도록 제한
Toleration: Pod에 설정하여 Taint가 있는 노드에도 배치 가능

```bash
# 노드에 Taint 추가
oc adm taint nodes node1 key=value:NoSchedule

# Pod에 Toleration 추가 (YAML)
tolerations:
- key: "key"
  operator: "Equal"
  value: "value"
  effect: "NoSchedule"
```

### Pod Anti-Affinity
같은 종류의 Pod가 같은 노드에 배치되지 않도록 설정합니다.
고가용성(HA)을 위해 중요합니다.

```yaml
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values: ["my-app"]
        topologyKey: kubernetes.io/hostname
```

## HPA (Horizontal Pod Autoscaler)

### 개념
HPA는 CPU, 메모리 사용률 등 메트릭을 기반으로 Pod 수를 자동으로 조절합니다.

### 설정 예시
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### oc 명령어
```bash
# HPA 생성
oc autoscale deployment my-app --min=2 --max=10 --cpu-percent=70

# HPA 상태 확인
oc get hpa

# HPA 상세
oc describe hpa my-app-hpa
```

## Pod 디버깅 명령어

```bash
# Pod 로그 확인
oc logs pod-name
oc logs pod-name -c container-name    # 멀티컨테이너 Pod
oc logs pod-name --previous           # 이전(크래시) 컨테이너 로그
oc logs -f pod-name                   # 실시간 로그 스트리밍

# Pod 접속
oc rsh pod-name
oc exec -it pod-name -- /bin/bash

# Pod 상세 정보 (이벤트 포함)
oc describe pod pod-name

# Pod 리소스 사용량
oc adm top pods
oc adm top pods --containers          # 컨테이너별

# Pod 이벤트
oc get events --sort-by=.lastTimestamp

# Pod YAML 확인
oc get pod pod-name -o yaml
```
