<!-- source: ocp-core-concepts-ko.md -->

# OpenShift Container Platform 핵심 개념 가이드

## Pod (파드)

### 개념
Pod는 Kubernetes에서 배포할 수 있는 가장 작은 단위입니다.
하나 이상의 컨테이너를 포함하며, 같은 Pod 내의 컨테이너는 네트워크와 스토리지를 공유합니다.

### 핵심 특징
- 하나의 Pod = 하나 이상의 컨테이너
- 같은 Pod 내 컨테이너는 localhost로 통신
- Pod는 일시적(ephemeral) - 언제든 삭제/재생성 가능
- 직접 생성보다 Deployment, StatefulSet 등으로 관리하는 것이 권장

### Pod 생명주기 상태
- Pending: Pod가 스케줄링 대기 중
- Running: Pod가 노드에 배치되어 실행 중
- Succeeded: 모든 컨테이너가 성공적으로 종료
- Failed: 하나 이상의 컨테이너가 실패로 종료
- Unknown: Pod 상태를 알 수 없음 (노드 통신 문제)

### 자주 발생하는 Pod 상태 이상
- CrashLoopBackOff: 컨테이너가 반복적으로 시작 후 즉시 종료
- ImagePullBackOff: 컨테이너 이미지를 가져올 수 없음
- Pending: 리소스 부족 또는 스케줄링 불가
- OOMKilled: 메모리 한도 초과로 강제 종료
- Evicted: 노드 리소스 부족으로 퇴출

## Service (서비스)

### 개념
Service는 Pod 집합에 대한 네트워크 접근을 제공하는 추상화 계층입니다.
Pod는 언제든 재생성될 수 있고 IP가 변경되므로, Service가 안정적인 엔드포인트를 제공합니다.

### Service 유형
- ClusterIP (기본값): 클러스터 내부에서만 접근 가능한 가상 IP
- NodePort: 모든 노드의 특정 포트로 외부 접근 가능 (30000-32767)
- LoadBalancer: 클라우드 로드밸런서를 프로비저닝하여 외부 접근 제공
- Headless Service: ClusterIP를 None으로 설정, StatefulSet과 함께 사용

### Headless Service 예시 (StatefulSet용)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None
  selector:
    app: mysql
  ports:
  - port: 3306
```

이 설정으로 mysql-0.mysql-headless.namespace.svc.cluster.local 같은 DNS로 개별 Pod에 접근 가능합니다.

## Route (라우트) - OCP 전용

### 개념
Route는 OpenShift에서 외부 트래픽을 Service로 라우팅하는 리소스입니다.
Kubernetes의 Ingress와 유사하지만 OCP에 특화된 기능을 제공합니다.

### 핵심 특징
- 도메인 기반 라우팅 (예: myapp.apps.cluster.example.com)
- TLS 종료 지원 (Edge, Passthrough, Re-encrypt)
- 자동 DNS 와일드카드 설정
- A/B 테스트, 블루-그린 배포를 위한 가중치 기반 라우팅

### 예시
```bash
# Route 생성
oc expose service my-app-service

# TLS Route 생성
oc create route edge my-app-route --service=my-app-service

# Route 확인
oc get routes
```

## Namespace와 Project

### Namespace (네임스페이스)
Kubernetes에서 리소스를 논리적으로 격리하는 단위입니다.
같은 클러스터 내에서 팀, 환경(dev/staging/prod), 프로젝트별로 리소스를 분리합니다.

### Project (프로젝트) - OCP 전용
OpenShift의 Project는 Namespace를 확장한 개념입니다.
- 추가 메타데이터 (설명, 표시 이름)
- 기본 RBAC 정책 자동 적용
- 리소스 쿼터와 제한 범위 설정

```bash
# 프로젝트 생성
oc new-project my-project --description="내 프로젝트" --display-name="My Project"

# 프로젝트 전환
oc project my-project

# 프로젝트 목록
oc get projects
```

## ConfigMap과 Secret

### ConfigMap
애플리케이션 설정을 Pod와 분리하여 관리하는 리소스입니다.
환경 변수, 설정 파일, 커맨드 라인 인자 등을 저장합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_HOST: "mysql-0.mysql-headless"
  DATABASE_PORT: "3306"
  LOG_LEVEL: "info"
```

### Secret
민감한 정보(비밀번호, 토큰, 인증서)를 저장하는 리소스입니다.
Base64로 인코딩되어 저장되며, RBAC으로 접근을 제어합니다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: [REDACTED_ACCOUNT]      # base64 encoded "admin"
  password: [REDACTED_SECRET]  # base64 encoded "password"
```

## PersistentVolume과 PersistentVolumeClaim

### PersistentVolume (PV)
클러스터 관리자가 프로비저닝한 스토리지 리소스입니다.
노드와 독립적으로 존재하며, Pod가 삭제되어도 데이터가 유지됩니다.

### PersistentVolumeClaim (PVC)
사용자가 스토리지를 요청하는 리소스입니다.
PVC를 생성하면 조건에 맞는 PV가 자동으로 바인딩됩니다.

### 접근 모드
- ReadWriteOnce (RWO): 하나의 노드에서만 읽기/쓰기 가능
- ReadOnlyMany (ROX): 여러 노드에서 읽기만 가능
- ReadWriteMany (RWX): 여러 노드에서 읽기/쓰기 가능

### StorageClass
동적 프로비저닝을 위한 스토리지 설정입니다.
PVC 생성 시 StorageClass를 지정하면 자동으로 PV가 생성됩니다.

```bash
# PV/PVC 확인
oc get pv
oc get pvc

# StorageClass 확인
oc get storageclass
```

## ResourceQuota와 LimitRange

### ResourceQuota
Namespace별 총 리소스 사용량을 제한합니다.
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
```

### LimitRange
개별 Pod/Container의 리소스 기본값과 최대값을 설정합니다.
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
```

## RBAC (Role-Based Access Control)

### 개념
사용자와 서비스 계정의 권한을 역할(Role) 기반으로 관리하는 시스템입니다.

### 핵심 리소스
- Role: Namespace 내의 권한 정의
- ClusterRole: 클러스터 전체 권한 정의
- RoleBinding: Role을 사용자/그룹에 연결
- ClusterRoleBinding: ClusterRole을 사용자/그룹에 연결

### OCP 기본 역할
- admin: 프로젝트 내 모든 리소스 관리 가능
- edit: 프로젝트 내 리소스 수정 가능 (RBAC 제외)
- view: 프로젝트 내 리소스 조회만 가능
- cluster-admin: 클러스터 전체 관리자

```bash
# 역할 부여
oc adm policy add-role-to-user admin user1 -n my-project
oc adm policy add-cluster-role-to-user cluster-reader user2

# 권한 확인
oc auth can-i create pods -n my-project
oc auth can-i '*' '*' --all-namespaces  # cluster-admin 확인
```

## Operator (오퍼레이터)

### 개념
Operator는 Kubernetes 애플리케이션의 설치, 업그레이드, 관리를 자동화하는 확장 패턴입니다.
Custom Resource Definition(CRD)과 Custom Controller를 조합하여 복잡한 운영 작업을 자동화합니다.

### OCP에서의 Operator
OpenShift 4.x는 Operator 기반으로 설계되었습니다:
- Cluster Version Operator (CVO): 클러스터 버전 관리
- Machine Config Operator (MCO): 노드 설정 관리
- OLM (Operator Lifecycle Manager): Operator 설치/관리
- OperatorHub: Operator 카탈로그 (Red Hat, 커뮤니티)

```bash
# 설치된 Operator 확인
oc get csv -n openshift-operators
oc get subscriptions -n openshift-operators

# OperatorHub에서 설치 가능한 Operator 목록
oc get packagemanifest -n openshift-marketplace
```

## ImageStream - OCP 전용

### 개념
ImageStream은 컨테이너 이미지의 추적과 관리를 위한 OCP 전용 리소스입니다.
외부 레지스트리의 이미지를 추상화하여, 이미지 변경 시 자동으로 빌드/배포를 트리거할 수 있습니다.

```bash
# ImageStream 목록
oc get imagestream -n openshift

# ImageStream에서 이미지 태그 확인
oc describe imagestream nodejs -n openshift
```

## BuildConfig - OCP 전용

### 개념
BuildConfig는 소스 코드를 컨테이너 이미지로 빌드하는 방법을 정의합니다.

### 빌드 전략
- Source-to-Image (S2I): 소스 코드를 자동으로 이미지로 변환
- Docker: Dockerfile 기반 빌드
- Pipeline: Jenkins 파이프라인 기반 빌드
- Custom: 사용자 정의 빌드

```bash
# 빌드 시작
oc start-build my-app

# 빌드 로그 확인
oc logs build/my-app-1

# 빌드 목록
oc get builds
```
