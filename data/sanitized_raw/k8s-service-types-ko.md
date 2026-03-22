<!-- source: k8s-service-types-ko.md -->

# Kubernetes/OCP Service 타입별 설정 가이드

## 개요

Service는 Pod 집합에 대한 안정적인 네트워크 엔드포인트를 제공합니다. Pod의 IP는 재시작마다 변경되지만, Service IP(ClusterIP)는 고정됩니다.

---

## 1. ClusterIP (기본값)

클러스터 내부에서만 접근 가능한 서비스입니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

- `port`: Service가 노출하는 포트 (클러스터 내부에서 접근하는 포트)
- `targetPort`: Pod 컨테이너가 실제로 리스닝하는 포트
- 클러스터 내 다른 Pod에서 `my-service:80`으로 접근 가능

---

## 2. NodePort

클러스터 외부에서 `<노드IP>:<NodePort>`로 접근 가능한 서비스입니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 30080    # 30000~32767 범위, 미지정 시 자동 할당
```

접근 방법: `http://<node-ip>:30080`

---

## 3. LoadBalancer

클라우드 환경에서 외부 로드밸런서를 자동 프로비저닝합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

---

## 4. OCP Route (외부 접근 - OCP 전용)

OpenShift에서는 Route를 통해 외부 HTTP/HTTPS 트래픽을 Service로 라우팅합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: my-route
spec:
  host: myapp.apps.example.com
  to:
    kind: Service
    name: my-service
  port:
    targetPort: 8080
  tls:
    termination: edge
```

```bash
# Route 생성 (CLI)
oc expose service my-service --hostname=myapp.apps.example.com

# Route 확인
oc get routes -n <namespace>
```

---

## 5. Headless Service (StatefulSet용)

ClusterIP를 `None`으로 설정하면 개별 Pod IP로 직접 DNS 조회가 가능합니다. StatefulSet과 함께 사용합니다.

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
    targetPort: 3306
```

DNS 조회: `mysql-0.mysql-headless.namespace.svc.cluster.local`

---

## 6. Service 관련 OCP 명령어

```bash
# Service 목록 확인
oc get svc -n <namespace>

# Service 상세 정보 (엔드포인트 포함)
oc describe svc <service-name> -n <namespace>

# Service 엔드포인트 확인 (연결된 Pod IP들)
oc get endpoints <service-name> -n <namespace>

# Service를 Route로 외부 노출
oc expose svc <service-name>

# Service 생성 (CLI)
oc create service clusterip my-svc --tcp=80:8080

# 포트포워딩으로 로컬 테스트
oc port-forward svc/<service-name> 8080:80 -n <namespace>
```

---

## 7. Service 타입 비교 요약

| 타입 | 접근 범위 | 포트 범위 | 사용 사례 |
|------|---------|---------|---------|
| ClusterIP | 클러스터 내부만 | 자유 | 내부 마이크로서비스 간 통신 |
| NodePort | 외부 (노드IP:포트) | 30000-32767 | 개발/테스트 환경 |
| LoadBalancer | 외부 (LB IP) | 자유 | 프로덕션 (클라우드) |
| Route | 외부 (도메인) | 80/443 | OCP 프로덕션 (HTTP/HTTPS) |
| Headless | 클러스터 내부 (Pod 직접) | 자유 | StatefulSet, DB 클러스터 |
