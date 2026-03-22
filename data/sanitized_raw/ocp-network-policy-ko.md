<!-- source: ocp-network-policy-ko.md -->

# OpenShift 네트워크 정책 및 서비스 메시 가이드

## 1. NetworkPolicy 개념: Pod 간 트래픽 제어의 방화벽

Kubernetes 및 OpenShift 환경에서 Pod 는 기본적으로 격리되지 않은 상태입니다. 즉, 같은 노드에 있는 모든 Pod 는 서로 통신할 수 있으며, 같은 네임스페이스 내의 모든 Pod 는 네트워크 라우팅을 통해 접근 가능합니다. 이러한 개방성은 개발 및 테스트 환경에는 유리할 수 있으나, 다중 테넌트 환경이나 보안이 중요한 프로덕션 시스템에서는 심각한 리스크가 됩니다.

**NetworkPolicy** 는 이 문제를 해결하기 위해 도입된 개념으로, Pod 들 간의 네트워크 트래픽을 제어하는 논리적 방화벽 역할을 합니다. 네트워크 정책은 특정 Pod(선택자) 에게 들어오는 (Ingress) 나 나가는 (Egress) 트래픽을 허용하거나 차단할 수 있는 규칙을 정의합니다.

NetworkPolicy 는 "Allow-by-default(기본 허용)"가 아닌 **"Deny-by-default(기본 차단)"** 로 동작하는 것이 핵심입니다. 즉, 네트워크 정책이 정의되지 않은 Pod 는 기본적으로 외부나 다른 Pod 들로부터 트래픽을 받지 않으며, 명시적으로 허용 규칙이 추가되어야만 통신이 가능합니다. 이는 최소 권한 원칙 (Principle of Least Privilege) 을 준수하여 보안 취약점을 줄이는 데 필수적입니다.

## 2. OCP SDN vs OVN-Kubernetes: 네트워크 플러그인 비교

OpenShift 는 네트워크 플러그인 (Network Plugin) 을 선택할 수 있으며, 이는 클러스터의 네트워크 아키텍처를 결정합니다. 현재 OCP 4.x 이상에서는 두 가지 주요 옵션이 있습니다.

| 특징 | OpenShift SDN (Software Defined Networking) | OVN-Kubernetes |
| :--- | :--- | :--- |
| **개발자** | Red Hat (기존) | Open Virtual Network (OVN) 프로젝트 |
| **아키텍처** | Overlay 네트워크 기반 (VXLAN) | Native Underlay 기반 (VLAN/VXLAN 혼합) |
| **스케일링** | 대규모 클러스터에서 성능 저하 가능성 | 대규모 노드 및 Pod 수에 더 우수함 |
| **기능** | 기본 L2/L3 네트워킹 제공 | L2/L3/L4 기능, 동적 IP 할당, 고가용성 지원 |
| **복잡도** | 비교적 단순한 설정 | 관리가 복잡할 수 있으나 유연성 높음 |
| **추천 시나리오** | 중소형 클러스터, 기존 SDN 의존성 유지 | 대규모 엔터프라이즈 클러스터, 복잡한 네트워크 요구사항 |
| **현재 상태** | OCP 4.12 이후 단계적 퇴출 예정 (Deprecation) | **OCP 4.12 이후 기본 권장 및 표준** |

**실무 팁:** 새로운 OpenShift 클러스터 구축 시에는 OVN-Kubernetes 를 기본으로 선택하는 것이 장기적인 유지보수와 확장성 측면에서 유리합니다. 기존 SDN 기반 클러스터에서 마이그레이션 시에는 네트워크 정책 규칙의 호환성을 반드시 확인해야 합니다.

## 3. NetworkPolicy YAML 예시 및 기본 정책 패턴

NetworkPolicy 는 `networking.k8s.io/v1` API 그룹을 사용합니다. 아래는 다양한 시나리오에 대한 예시입니다.

### 3-1. 기본 정책 패턴

1.  **Deny-All (모든 트래픽 차단):**
    특정 네임스페이스의 모든 Pod 에게 들어오는 트래픽을 기본적으로 차단합니다. 이는 가장 안전한 시작점입니다.
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: deny-all-ingress
      namespace: production
    spec:
      podSelector: {}  # 모든 Pod 를 선택
      policyTypes:
      - Ingress
    ```

2.  **Allow-Same-Namespace (동일 네임스페이스 허용):**
    위 Deny-All 정책을 적용한 후, 같은 네임스페이스 내의 모든 Pod 로부터 트래픽을 허용합니다.
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: allow-same-namespace
      namespace: production
    spec:
      podSelector: {}
      policyTypes:
      - Ingress
      ingress:
      - from:
        - namespaceSelector: {}  # 같은 네임스페이스의 모든 Pod
    ```

3.  **Allow-From-Specific-Pod (특정 Pod 에서만 허용):**
    특정 레이블을 가진 Pod 만 트래픽을 보낼 수 있도록 제한합니다.
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: allow-from-frontend
      namespace: production
    spec:
      podSelector:
        matchLabels:
          app: backend-api
      policyTypes:
      - Ingress
      ingress:
      - from:
        - podSelector:
            matchLabels:
              app: frontend-web
        ports:
        - protocol: TCP
          port: 8080
    ```

### 3-2. 네임스페이스 간 통신 제어 (Egress)

서버 (Backend) 가 외부 데이터베이스나 다른 네임스페이스의 서비스 (Database) 에만 연결되도록 제한하는 예시입니다.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress-db-access
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: payment-service
  policyTypes:
  - Egress
  egress:
  # 같은 네임스페이스 내의 모든 Pod 로 나가는 트래픽 허용
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 80
  # 외부 DB 네임스페이스 (database-ns) 로만 포트 5432 트래픽 허용
  - to:
    - namespaceSelector:
        matchLabels:
          name: database-ns
    ports:
    - protocol: TCP
      port: 5432
  # 나머지는 차단됨
```

## 4. Service Mesh 개요 및 OpenShift Service Mesh

서비스 메시 (Service Mesh) 는 마이크로서비스 아키텍처 (MSA) 에서 서비스 간 통신을 관리하는 인프라 레이어입니다. 애플리케이션 코드에 직접 로직을 넣지 않고, 네트워크 레벨에서 트래픽 관리, 보안, 관찰가능성을 처리합니다.

### 4-1. 사이드카 패턴 (Sidecar Pattern)
서비스 메시의 핵심 구현 방식은 **사이드카 패턴**입니다. 각 Pod 에에는 애플리케이션 컨테이너와 별도로 메시 에이전트 (예: Istio Proxy) 가 추가되어 실행됩니다.
*   **데이터 플레인 (Data Plane):** 실제 트래픽을 처리하는 사이드카 프로세스.
*   **컨트롤 플레인 (Control Plane):** 사이드카들을 구성하고 관리하는 중앙 관리 시스템 (Istio Pilot 등).

### 4-2. Istio 와 OpenShift Service Mesh
OpenShift 는 자체적인 서비스 메시 솔루션인 **OpenShift Service Mesh** 를 제공합니다. 이는 Red Hat 에서 공식 지원하는 솔루션으로, 내부적으로 **Istio** 기술을 기반으로 하지만 Red Hat 의 관리 도구와 통합되어 있습니다.

*   **트래픽 관리:**金丝雀 배포 (Canary), A/B 테스트, 회귀 (Rollback), 지연 시간 최적화.
*   **보안 (mTLS):** 서비스 간 통신에 대해 자동으로 **mTLS (Mutual TLS)** 을 활성화하여 암호화된 통신을 보장합니다. 인증서 관리가 복잡하지 않도록 자동화된 인증 체인을 제공합니다.
*   **관찰가능성:** 분산 트레이싱 (Jaeger 통합), 메트릭 수집 (Prometheus), 로깅을 하나의 대시보드에서 시각화합니다.

**실무 팁:** OpenShift 에서 Service Mesh 를 활성화하려면 `oc project` 명령어로 프로젝트에 진입한 후, `oc apply -f <mesh-config>.yaml` 로 구성을 적용하거나, OCP Console 의 'Service Mesh' 메뉴를 통해 UI 로 설정할 수 있습니다.

## 5. Ingress/Route 심화: TLS 와 경로 기반 라우팅

OpenShift 에서 외부에서 클러스터로 들어오는 트래픽은 **Ingress** (일반 K8s) 나 **Route** (OpenShift 확장) 를 통해 처리됩니다. OpenShift Route 는 Ingress Controller 와 통합되어 더 강력한 기능을 제공합니다.

### 5-1. TLS 종류
Route 설정 시 TLS 모드를 선택할 수 있으며, 각각의 동작 방식은 다음과 같습니다.

| TLS 모드 | 설명 | 사용 시나리오 |
| :--- | :--- | :--- |
| **Edge** | 클라이언트와 Ingress Controller 간에 TLS 핸드셰이크가 발생하며, Ingress Controller 는 받은 트래픽을 **Plaintext** 로 백엔드 Pod 에 전달합니다. | 클라이언트 인증서 검증이 필요하지 않은 일반적인 경우. 가장 성능이 좋음. |
| **Passthrough** | Ingress Controller 는 TLS 핸드셰이크를 수행하지 않고, 트래픽을 **원본 그대로** 백엔드 Pod 에 전달
