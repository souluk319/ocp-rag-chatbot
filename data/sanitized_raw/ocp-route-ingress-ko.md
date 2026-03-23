<!-- source: ocp-route-ingress-ko.md -->

# OpenShift Container Platform (OCP) Route & Ingress 심화 가이드

안녕하세요, 신입 엔지니어 여러분. 이번 가이드는 OpenShift 환경에서 외부 트래픽을 서비스 내부로 연결하는 핵심 메커니즘인 **Route**를 깊이 있게 이해하고 실무에서 활용하는 방법을 다룹니다. Kubernetes 기반의 오픈소스 프로젝트인 Kubernetes Ingress 와 OpenShift 특유의 Route 는 기능상 유사하지만, 구현 방식과 관리 전략에서 중요한 차이가 있습니다. 본 문서를 통해 개념부터 고급 설정, 트러블슈팅까지 체계적으로 학습하시기 바랍니다.

---

## 1. Route 개요: OCP Route vs Kubernetes Ingress 차이점

Kubernetes 생태계에서 외부에서 클러스터 내부의 서비스를 접근하려면 반드시 엔드포인트가 필요합니다. 일반적인 Kubernetes 클러스터에서는 **Ingress**를 사용하지만, OpenShift 플랫폼은 **Route**를 기본 네트워킹 리소스로 제공합니다.

두者的의 근본적인 차이는 다음과 같습니다.

*   **Kubernetes Ingress**: Ingress Controller(예: NGINX, HAProxy)가 클러스터 외부의 트래픽을 받아서 정의된 규칙에 따라 내부 Service 로 라우팅합니다. 사용자가 직접 Ingress Controller 를 설치하고 구성해야 하며, 로드 밸런싱 및 SSL 종료 설정을 관리해야 합니다.
*   **OpenShift Route**: OpenShift 의 네임스페이스 네임스페이스 (Namespace) 레벨 리소스로, 클러스터 내부에 이미 설치된 **HAProxy 기반 Router**를 자동으로 사용합니다. Route 리소스만 정의하면 SSL 종료, 도메인 해결, 로드 밸런싱이 자동으로 처리됩니다. 즉, "Route 는 Ingress 를 더 쉽게 사용한 OpenShift 특화 버전"이라고 볼 수 있습니다.

### 핵심 특징 비교

| 비교 항목 | Kubernetes Ingress | OpenShift Route |
| :--- | :--- | :--- |
| **리소스 위치** | 클러스터 전체 또는 특정 네임스페이스 (Controller 의존) | 네임스페이스 단위 리소스 |
| **로드 밸런서** | 사용자가 설치한 Ingress Controller (NGINX 등) | OpenShift 기본 HAProxy Router |
| **SSL/TLS 설정** | Ingress Annotation 으로 수동 설정 필요 | Route Annotation (`tls`, `termination`) 으로 자동 관리 |
| **도메인 관리** | 외부 DNS 레코드와 직접 매핑 | Route 에 호스트네임 직접 지정 가능 |
| **가용성 (HA)** | Ingress Controller 설정에 따라 다름 | Router Cluster 가 자동으로 HA 구성 |
| **사용 용이성** | 상대적으로 복잡 (Annotation 등) | 매우 직관적 (`oc expose` 명령어 등) |

---

## 2. Route 생성: `oc expose service` 및 `oc create route`

OpenShift 에서 Route 를 생성하는 가장 빠르고 효율적인 방법은 `oc expose` 명령어를 사용하는 것입니다. 이 명령어는 자동으로 적절한 Route 리소스를 생성하고, 필요한 경우 Secret(SSL 인증서) 을 생성합니다.

### 명령어 예시

가장 기본적인 HTTP Route 생성:
```bash
# 기존 Service 'my-service' 가 있을 때
oc expose service my-service --port=8080 --name=my-route
```

TLS(HTTPS) 를 활성화하고 특정 도메인을 지정:
```bash
oc expose service my-service \
  --port=8080 \
  --name=my-secure-route \
  --route=edge \
  --insecure-edge-termination=false \
  --host=myapp.example.com
```

여기서 `--route=edge` 옵션은 TLS 종료를 Edge 에서 수행한다는 것을 의미하며, `--insecure-edge-termination=false` 는 Edge 에서 SSL 인증서를 검증하고 내부로 암호화된 트래픽을 보낸다는 설정입니다.

---

## 3. TLS 종류: Edge, Passthrough, Re-encrypt 비교

OpenShift Route 는 트래픽이 클러스터 경계를 넘을 때 SSL/TLS 처리 방식을 세 가지 모드로 지원합니다. 각 모드는 보안 정책과 네트워크 아키텍처에 따라 선택해야 합니다.

### TLS 종결 모드 비교

| TLS 모드 | 동작 원리 | 사용 시나리오 |
| :--- | :--- | :--- |
| **Edge** | Route(Edge) 에서 SSL 인증서를 검증하고 종결합니다. 종결된 HTTP 트래픽이 내부 Service 로 전달됩니다. | 클라이언트 인증서가 Route 에 있고, 백엔드 서비스는 HTTP 만 지원하거나, 외부 인증서 관리가 용이할 때. |
| **Passthrough** | Route 는 SSL 인증서를 검증하지 않고, 트래픽을 암호화된 상태로 그대로 백엔드 Service 로 전달합니다. | 백엔드 서비스 (예: 외부 SaaS, 기존 애플리케이션) 가 자체 SSL 인증서를 보유하고 있고, Route 가 인증서를 관리할 수 없을 때. |
| **Re-encrypt** | Route 에서 SSL 인증서를 종결하고 (Edge), 내부로 다시 새로운 SSL 인증서를 사용하여 암호화합니다. | **가장 권장되는 보안 모드**. 외부에서 인증서를 관리하되, 클러스터 내부에서는 별도의 인증서로 보안 계층을 유지할 때. |

---

## 4. Route YAML 예시

명령어로 생성하지 않고 YAML 파일로 직접 정의하는 경우를 대비해 주요 시나리오별 예시를 살펴봅니다.

### HTTP Route (기본)
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: http-only-route
  namespace: my-project
spec:
  host: http-example.com
  to:
    kind: Service
    name: my-service
    weight: 100
  port:
    targetPort: 8080
```

### TLS Edge Route (SSL 종료)
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: tls-edge-route
spec:
  host: secure-example.com
  to:
    kind: Service
    name: my-service
  port:
    targetPort: 8080
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
    certificate: /path/to/cert.crt
    key: /path/to/key.key
```

### Passthrough Route (중계)
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: passthrough-route
spec:
  host: passthrough-example.com
  to:
    kind: Service
    name: my-service
  port:
    targetPort: 8443
  tls:
    termination: passthrough
    insecureEdgeTerminationPolicy: Redirect
```

---

## 5. Path 기반 라우팅

하나의 Route 호스트에 여러 개의 Service 를 연결하고 싶을 때, URL 경로 (`/api`, `/web` 등) 를 기준으로 트래픽을 분배할 수 있습니다. 이는 하나의 도메인으로 여러 마이크로서비스를 노출할 때 유용합니다.

### 예시: `/api` 경로만 `api-service`, 나머지는 `web-service` 로 연결
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: path-based-routing
spec:
  host: myapp.example.com
  to:
    kind: Service
    name: web-service
  port:
    targetPort: 8080
  path: /
  pathType: Prefix
  wildcardPolicy: Subdomain

---
# 별도의 Route 에서 /api 경로를 덮어쓰거나 추가할 수 있음
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: api-path-route
spec:
  host: myapp.example.com
  to:
    kind: Service
    name: api-service
  port:
    targetPort: 8080
  path: /api
  pathType: Prefix
```
*참고: 최신 OpenShift 버전에서는 `path` 와 `pathType` 필드를 통해 더 정교한 라우팅이 가능합니다.*

---

## 6. 커스텀 도메인 설정

OpenShift 에서 Route 를 생성할 때 기본적으로 생성된 Wildcard 도메인 (`myapp-1234567890-abcde-1234567890.apps.cluster-domain.example.com`) 대신 조직의 공식 도메인을 사용해야 합니다.

이는 Route 생성 시 `--host` 플래그를 지정하거나, YAML 에서 `spec.host` 를 명시적으로 설정하여 해결합니다.

```yaml
spec:
  host: "production.mycompany.com"
```

이 경우, DNS 관리자는 `production.mycompany.com` 을 OpenShift Cluster 의 Ingress Router IP 로 포워딩하는 A 레코드를 생성해야 합니다.

---

## 7. Ingress Controller: HAProxy 기반 OCP Router 및 샤딩

OpenShift 의 Route 는 기본적으로 **HAProxy** 기반의 Router Cluster 를 사용합니다. 이 클러스터는 고가용성 (High Availability) 을 보장하기 위해 여러 노드에 분산되어 있습니다.

### 샤딩 (Sharding) 개념
클러스터가 커지면 하나의 HAProxy 인스턴스만으로는 트래픽 처리 능력이 부족해질 수 있습니다. 이를 해결하기 위해 OpenShift 는 **Sharding** 기술을 사용합니다.
*   **원리**: 모든 Route 가 모든 Router 노드를 스캔하는 것이 아니라, 각 Route 가 특정 노
