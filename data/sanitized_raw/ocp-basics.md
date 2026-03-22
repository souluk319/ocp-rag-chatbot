<!-- source: ocp-basics.md -->

# OpenShift Container Platform (OCP) 기본 개념

## OCP란?

OpenShift Container Platform(OCP)은 Red Hat이 제공하는 엔터프라이즈급 Kubernetes 기반 컨테이너 플랫폼입니다. Kubernetes를 기반으로 하면서 엔터프라이즈 환경에 필요한 보안, 모니터링, CI/CD, 개발자 도구 등을 추가로 제공합니다.

## OCP 아키텍처

### Control Plane (Master Node)
- **API Server**: 모든 REST 요청을 처리하는 중앙 컴포넌트. kubectl, oc CLI, 웹 콘솔 모두 API Server를 통해 통신합니다.
- **etcd**: 클러스터의 모든 상태 데이터를 저장하는 분산 키-값 저장소. 고가용성을 위해 보통 3개 이상의 인스턴스로 구성합니다.
- **Controller Manager**: Deployment, ReplicaSet 등 컨트롤러를 관리합니다. 선언된 상태(desired state)와 실제 상태(current state)를 비교하여 조정합니다.
- **Scheduler**: 새로 생성된 Pod를 적절한 노드에 배치합니다. 리소스 요청량, 노드 affinity, taint/toleration 등을 고려합니다.

### Worker Node
- **kubelet**: 각 노드에서 실행되며 Pod의 라이프사이클을 관리합니다.
- **Container Runtime**: CRI-O가 기본 컨테이너 런타임으로 사용됩니다.
- **kube-proxy**: 서비스의 네트워크 규칙을 관리합니다.

### Infrastructure Node
- Router (HAProxy)
- Registry (내부 이미지 레지스트리)
- Monitoring (Prometheus, Grafana)
- Logging (EFK Stack)

## 주요 리소스

### Pod
Pod는 Kubernetes에서 배포 가능한 가장 작은 단위입니다. 하나 이상의 컨테이너를 포함하며, 같은 Pod 내의 컨테이너들은 네트워크와 스토리지를 공유합니다.

### Deployment
애플리케이션의 선언적 업데이트를 제공합니다. Rolling Update, Recreate 등의 배포 전략을 지원합니다.

### Service
Pod 그룹에 대한 네트워크 접근을 제공하는 추상화 계층입니다.
- **ClusterIP**: 클러스터 내부에서만 접근 가능 (기본값)
- **NodePort**: 각 노드의 특정 포트로 외부 접근 가능
- **LoadBalancer**: 외부 로드밸런서를 통한 접근

### Route
OCP 고유의 리소스로, 외부에서 서비스에 접근할 수 있는 URL을 제공합니다. TLS 종단 등을 지원합니다.

### ConfigMap & Secret
- **ConfigMap**: 설정 데이터를 키-값 쌍으로 저장
- **Secret**: 민감한 데이터(패스워드, 토큰 등)를 Base64 인코딩하여 저장

### PersistentVolume (PV) & PersistentVolumeClaim (PVC)
- **PV**: 클러스터 관리자가 프로비저닝한 스토리지
- **PVC**: 사용자가 요청하는 스토리지. PV에 바인딩됩니다.

## Namespace & Project
- **Namespace**: Kubernetes의 논리적 격리 단위
- **Project**: OCP에서 Namespace를 확장한 개념. RBAC, 네트워크 정책 등이 추가됩니다.
