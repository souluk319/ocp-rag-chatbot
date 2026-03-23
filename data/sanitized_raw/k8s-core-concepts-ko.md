<!-- source: k8s-core-concepts-ko.md -->

# Kubernetes 핵심 개념 입문

## 1. 쿠버네티스란 무엇인가, 왜 필요한가

쿠버네티스 (Kubernetes, 약칭 K8s) 는 구글에서 개발한 오픈소스 컨테이너 오케스트레이션 플랫폼입니다. 수많은 컨테이너 애플리케이션을 자동으로 배포, 확장, 운영 및 관리하는 데 사용됩니다.

### 왜 필요한가?
단일 서버에서 수백 개의 컨테이너를 실행할 때, 수동 관리만으로는 다음과 같은 문제를 해결하기 어렵습니다.
*   **자동 복구**: 컨테이너가 실패했을 때 자동으로 재시작하거나 다른 노드로 이동해야 합니다.
*   **수평 확장**: 트래픽이 급증할 때 인스턴스를 자동으로 늘리고 줄여야 합니다.
*   **서비스 발견**: 여러 Pod 이 분산되어 있을 때, 서로 어떻게 통신할지 관리해야 합니다.
*   **고용력성**: 노드가 고장 나도 서비스 가동 중단 없이 운영되어야 합니다.

쿠버네티스는 이러한 문제를 해결하기 위해 '마스터 노드'와 '워커 노드'로 구성된 클러스터 아키텍처를 제공합니다. 마스터 노드는 클러스터의 상태를 관리하고, 워커 노드는 실제 애플리케이션을 실행합니다.

## 2. Pod 개념과 필요성, 컨테이너와 Pod 의 관계

쿠버네티스에서 가장 기본적이고 최소 단위의 실행 객체는 **Pod**입니다.

### 컨테이너와 Pod 의 관계
일반적으로 하나의 Pod 에는 하나의 컨테이너가 들어가는 것이 가장 흔하지만, 하나의 Pod 에 여러 개의 컨테이너가 들어갈 수도 있습니다. 이 경우 컨테이너들은 같은 네트워크 스페이스와 같은 저장소 볼륨을 공유합니다.

*   **왜 Pod 이 필요한가?**: 컨테이너 엔진 (Docker, containerd 등) 은 컨테이너를 직접 관리하지 않습니다. 쿠버네티스는 Pod 단위로 컨테이너를 스케줄링하고 관리합니다. Pod 는 "컨테이너의 묶음"이라 할 수 있으며, 같은 Pod 속 컨테이너들은 마치 하나의 프로세스처럼 동작합니다.
*   **Sidecar 패턴**: 로그 수집, 인증 등 부가 기능을 수행하는 컨테이너를 메인 애플리케이션 컨테이너와 함께 Pod 에 묶어둘 때 유용합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.14
    ports:
    - containerPort: 80
  - name: log-agent
    image: fluentd:latest
    volumeMounts:
    - name: log-volume
      mountPath: /var/log
  volumes:
  - name: log-volume
    emptyDir: {}
```

## 3. ReplicaSet 의 역할

**ReplicaSet** 은 Pod 의 정확한 개수를 유지하도록 보장하는 컨트롤러입니다.

### 주요 기능
*   **수평 복제**: 사용자가 원하는 개수 (예: 3 개) 의 Pod 을 생성합니다.
*   **자동 복구**: Pod 이 삭제되거나 실패하면 즉시 새로운 Pod 을 생성하여 개수를 유지합니다.
*   **롤링 업데이트**: 이미지 변경 시, 기존 Pod 을 점진적으로 교체하며 서비스를 중단 없이 업데이트합니다.

ReplicaSet 은 보통 **Deployment** 라는 고수준 리소스를 통해 관리됩니다. Deployment 는 ReplicaSet 을 생성하고 관리하는 상위 개념으로, 버전 관리와 롤백 기능이 추가되어 있습니다.

## 4. DaemonSet 은 언제 사용하나

**DaemonSet** 은 클러스터의 각 노드 (Node) 하나당 하나의 Pod 을 실행하도록 보장하는 컨트롤러입니다.

### 사용 시나리오
특정 노드마다 반드시 실행되어야 하는 시스템용 애플리케이션을 배포할 때 사용합니다.
*   **로깅 에이전트**: ELK 스택의 Fluentd, Filebeat 등 (각 노드의 로그를 수집).
*   **모니터링**: Prometheus Node Exporter, cAdvisor 등 (노드 상태 감시).
*   **보안**: antivirus, 네트워크 보안 에이전트 등.

DaemonSet 은 노드가 추가될 때마다 자동으로 새로운 Pod 을 생성하며, 노드가 삭제되면 해당 Pod 도 함께 제거됩니다.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-daemonset
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:latest
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

## 5. Service 종류 비교 (ClusterIP, NodePort, LoadBalancer)

쿠버네티스 내부의 Pod 이 외부 세계와 통신하기 위해 **Service** 가 필요합니다. Service 는 Pod 의 IP 가 자주 변하는 문제를 해결하여, 고정된 IP 와 포트에 접근할 수 있게 합니다.

| Service 유형 | 설명 | 사용 사례 | 접근 방식 |
| :--- | :--- | :--- | : |
| **ClusterIP** | 쿠버네티스 클러스터 내부에서만 접근 가능한 가상 IP | 클러스터 내 애플리케이션 간 통신 (내부 API) | `kubectl proxy` 또는 내부 IP |
| **NodePort** | 클러스터 내 각 노드의 특정 포트 (예: 30007) 를 엽니다 | 외부에서 클러스터 내 서비스 접근 (테스트 환경) | `http://<노드 IP>:<포트>` |
| **LoadBalancer** | 클라우드 제공자 (AWS, GCP 등) 에서 외부 로드밸런서를 생성 | 클라우드 환경의公网 (Public) 서비스 노출 | 클라우드 LB 엔드포인트 IP |

*   **ClusterIP** 는 기본값이며 가장 안전합니다.
*   **NodePort** 는 클라우드 환경보다 온프레미스나 멀티 클라우드 환경에서 자주 사용됩니다.
*   **LoadBalancer** 는 클라우드 네이티브 환경에서 외부 트래픽을 분산시키기에 최적입니다.

## 6. Secret 개념과 종류, 환경변수 주입

비밀번호, API 키, 인증 토큰 등 민감한 정보를 코드에 하드코딩하지 않고 안전하게 관리하기 위해 **Secret** 을 사용합니다.

### Secret 의 종류
1.  **Opaque**: 일반적인 텍스트 데이터 (예: DB 비밀번호). 기본 타입입니다.
2.  **kubernetes.io/dockerconfigjson**: Docker 인증 정보를 저장할 때 사용합니다.
3.  **kubernetes.io/tls**: TLS 인증서와 키를 저장할 때 사용합니다.

### 환경변수 주입 방법
Secret 을 생성한 후, Pod 의 환경변수로 주입하거나 파일로 마운트할 수 있습니다.

```bash
# Secret 생성 (Opaque 타입)
kubectl create secret generic db-credentials \
  --from-literal=username=[REDACTED_ACCOUNT] \
  --from-literal=password=[REDACTED_SECRET]

# Pod 에 환경변수로 주입
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
```

## 7. RBAC 개요 (Role vs ClusterRole)

**RBAC (Role-Based Access Control)** 은 사용자가 리소스에 대해 어떤 권한을 가지는지를 정의하는 권한 관리 시스템입니다.

### 왜 필요한가?
보안 강화 및 최소 권한 원칙 (Principle of Least Privilege) 을 준수하기 위해 필요합니다. 모든 사용자에게 모든 권한을 주면 사고 발생 시 피해가 커집니다.

### Role vs ClusterRole
*   **Role**: 특정 **Namespace** 내에서만 유효한 권한을 정의합니다. (예: `dev` Namespace 에서만 Pod 을 수정할 수 있는 권한)
*   **ClusterRole**: 클러스터 전체 (**Namespace 제한 없음**) 에서 유효한 권한을 정의합니다. (예: 모든 Namespace 에서 Pod 을 삭제할 수 있는 권한)

권한을 실제로 부여하려면 **RoleBinding** (Namespace 단위) 또는 **ClusterRoleBinding** (클러스터 단위) 이 필요합니다.

## 8. Namespace 개념

**Namespace** 는 클러스터 내의 리소스를 논리적으로 분리하여 그룹화하는 가상 공간입니다. 물리적으로 리소스를 분리하지 않지만, 이름 충돌을 방지하고 리소스 사용량을 관리할 수 있게 합니다.

### 주요 용도
*   **환경 분리**: 개발 (dev), 테스트 (test), 프로덕션 (prod) 환경을 하나의 클러스터에서 구분하여 운영합니다.
*   **팀별 분리**: 여러 팀이 동일한 클러스터를 공유하더라도 각 팀의 리소스가 섞이지 않게 관리합니다.
*   **리소스 할당**: Namespace 단위로 리소스 할당량 (Quota)
