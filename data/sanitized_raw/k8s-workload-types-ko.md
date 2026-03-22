<!-- source: k8s-workload-types-ko.md -->

# Kubernetes 워크로드 리소스 비교 가이드

## 워크로드 리소스란?

Kubernetes에서 워크로드 리소스는 Pod의 생명주기를 관리하는 상위 컨트롤러입니다.
직접 Pod를 생성하는 대신, 워크로드 리소스를 통해 원하는 상태(desired state)를 선언하면
컨트롤러가 자동으로 Pod를 생성, 삭제, 재시작합니다.

주요 워크로드 리소스:
- Deployment: 무상태(Stateless) 애플리케이션 관리
- StatefulSet: 상태 유지(Stateful) 애플리케이션 관리
- DaemonSet: 모든 노드에 Pod 배포
- Job / CronJob: 일회성 또는 주기적 작업 실행
- ReplicaSet: Deployment 내부에서 사용되는 복제 관리자
- DeploymentConfig: OCP 전용 레거시 배포 관리자 (Deployment 사용 권장)

## Deployment (디플로이먼트)

### 개념
Deployment는 무상태(Stateless) 애플리케이션을 배포하고 관리하는 가장 기본적인 워크로드 리소스입니다.
내부적으로 ReplicaSet을 생성하여 지정된 수의 Pod 복제본을 유지합니다.

### 핵심 특징
- Pod 간에 서로 구분이 없으며 대체 가능(interchangeable)
- Pod가 죽으면 새로운 Pod로 교체 (이름이 랜덤으로 변경됨)
- 롤링 업데이트와 롤백을 자동으로 지원
- 수평 스케일링(HPA)과 함께 사용 가능
- Pod에 고유한 네트워크 ID나 영구 스토리지가 필요 없는 경우 적합

### 사용 사례
- 웹 서버 (Nginx, Apache)
- API 서버 (REST API 백엔드)
- 마이크로서비스의 Stateless 컴포넌트
- 프론트엔드 애플리케이션

### YAML 예시
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
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
```

### 업데이트 전략
- RollingUpdate (기본값): 새 Pod를 하나씩 생성하고 기존 Pod를 하나씩 제거
- Recreate: 기존 Pod를 모두 삭제 후 새 Pod를 한꺼번에 생성

## StatefulSet (스테이트풀셋)

### 개념
StatefulSet은 상태를 유지해야 하는(Stateful) 애플리케이션을 관리하는 워크로드 리소스입니다.
각 Pod에 고유한 ID와 영구 스토리지를 부여하여, Pod가 재시작되더라도 동일한 ID와 데이터를 유지합니다.

### 핵심 특징
- 각 Pod에 고유하고 안정적인 네트워크 ID 부여 (pod-0, pod-1, pod-2 순서)
- Pod 이름이 순서대로 고정됨 (예: mysql-0, mysql-1, mysql-2)
- 순서대로 생성되고 역순으로 삭제됨 (ordered graceful deployment)
- 각 Pod에 전용 PersistentVolumeClaim(PVC)이 연결됨
- Pod가 재시작되어도 같은 PVC에 다시 마운트됨
- Headless Service와 함께 사용하여 각 Pod에 DNS로 접근 가능

### 사용 사례
- 데이터베이스 (MySQL, PostgreSQL, MongoDB)
- 메시지 큐 (Kafka, RabbitMQ)
- 분산 스토리지 (Elasticsearch, Cassandra)
- 리더-팔로워 구조가 필요한 애플리케이션
- ZooKeeper 같은 분산 코디네이터

### YAML 예시
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql-headless
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

## Deployment vs StatefulSet 핵심 비교

| 비교 항목 | Deployment | StatefulSet |
|-----------|------------|-------------|
| 상태 유지 | 무상태(Stateless) | 상태 유지(Stateful) |
| Pod 이름 | 랜덤 해시 (nginx-abc123) | 순번 고정 (mysql-0, mysql-1) |
| Pod 교체 | 새 Pod = 새 이름 | 같은 이름으로 재생성 |
| 스토리지 | 공유 또는 임시 볼륨 | Pod별 전용 PVC |
| 네트워크 ID | Service를 통한 로드밸런싱 | Headless Service로 개별 접근 |
| 배포 순서 | 동시(병렬) 배포 | 순차적 배포 (0→1→2) |
| 삭제 순서 | 동시(병렬) 삭제 | 역순 삭제 (2→1→0) |
| 스케일링 | 빠름 (병렬) | 느림 (순차) |
| 롤링 업데이트 | 지원 | 지원 (역순으로) |
| DNS | service-name.namespace | pod-name.service-name.namespace |
| 복잡도 | 단순 | 복잡 (Headless Service, PVC 필요) |
| 대표 용도 | 웹서버, API서버 | 데이터베이스, 메시지큐 |

### 선택 기준: 언제 무엇을 쓸까?

**Deployment를 선택하는 경우:**
- 애플리케이션이 상태를 저장하지 않음
- 어떤 Pod가 요청을 처리해도 결과가 동일
- 빠른 스케일링이 필요
- 데이터를 외부 시스템(DB, Redis 등)에 저장

**StatefulSet을 선택하는 경우:**
- 각 Pod가 고유한 데이터를 가져야 함
- Pod 간 순서가 중요 (리더 선출, 복제 등)
- Pod 재시작 후에도 동일한 스토리지에 접근해야 함
- 각 Pod에 개별적으로 접근해야 함 (예: mysql-0에만 쓰기)

## DaemonSet (데몬셋)

### 개념
DaemonSet은 클러스터의 모든 노드(또는 특정 노드)에 정확히 하나의 Pod를 배포하는 워크로드 리소스입니다.
새로운 노드가 추가되면 자동으로 해당 노드에도 Pod가 생성됩니다.

### 핵심 특징
- 모든 노드에 1개씩 Pod 배포 (노드 수 = Pod 수)
- 노드 추가 시 자동 배포, 노드 제거 시 자동 삭제
- nodeSelector나 tolerations로 특정 노드만 대상 가능

### 사용 사례
- 로그 수집 (Fluentd, Filebeat)
- 모니터링 에이전트 (Prometheus Node Exporter, Datadog Agent)
- 네트워크 플러그인 (Calico, Flannel, OVN-Kubernetes)
- 스토리지 데몬 (Ceph, GlusterFS)

### OCP에서의 DaemonSet
OpenShift에서는 다음 컴포넌트가 DaemonSet으로 배포됩니다:
- OVN-Kubernetes 네트워크 플러그인
- Node Exporter (모니터링)
- Machine Config Daemon (노드 설정 관리)

## Job과 CronJob

### Job
일회성 작업을 실행하고 완료되면 종료되는 워크로드 리소스입니다.
- 배치 처리, 데이터 마이그레이션, 백업 작업에 적합
- completions: 성공해야 할 Pod 수
- parallelism: 동시 실행할 Pod 수
- backoffLimit: 실패 시 재시도 횟수

### CronJob
주기적으로 Job을 생성하는 스케줄러입니다.
- Linux cron 문법으로 스케줄 지정 (예: "0 2 * * *" = 매일 새벽 2시)
- 정기 백업, 리포트 생성, 캐시 정리 등에 사용

## OCP 전용: DeploymentConfig vs Deployment

### DeploymentConfig (레거시)
OpenShift 3.x에서 사용하던 배포 리소스입니다.
- OCP 전용이며 Kubernetes 표준이 아님
- lifecycle hook, custom strategy 등 OCP 전용 기능 제공
- **OCP 4.x부터는 Deployment 사용을 권장**

### 마이그레이션
기존 DeploymentConfig를 Deployment로 전환할 때:
```bash
# DeploymentConfig 확인
oc get dc

# Deployment로 전환 (수동)
oc get dc my-app -o yaml > my-app-dc.yaml
# kind: DeploymentConfig → kind: Deployment로 변경
# apiVersion: apps.openshift.io/v1 → apiVersion: apps/v1로 변경
# triggers, strategy 등 OCP 전용 필드 제거
```

## 워크로드 관련 oc 명령어

```bash
# Deployment 관리
oc get deployment                    # Deployment 목록
oc describe deployment my-app        # 상세 정보
oc scale deployment my-app --replicas=5  # 스케일링
oc rollout status deployment my-app  # 롤아웃 상태
oc rollout undo deployment my-app    # 롤백
oc rollout history deployment my-app # 롤아웃 이력

# StatefulSet 관리
oc get statefulset                   # StatefulSet 목록
oc describe statefulset my-db        # 상세 정보
oc scale statefulset my-db --replicas=3  # 스케일링

# DaemonSet 관리
oc get daemonset                     # DaemonSet 목록
oc describe daemonset my-agent       # 상세 정보

# Job / CronJob 관리
oc get jobs                          # Job 목록
oc get cronjobs                      # CronJob 목록
oc create job my-job --from=cronjob/my-cronjob  # CronJob에서 수동 실행

# Pod 상태 확인
oc get pods -l app=my-app            # 특정 앱의 Pod 목록
oc get pods -o wide                  # 노드 배치 정보 포함
```
