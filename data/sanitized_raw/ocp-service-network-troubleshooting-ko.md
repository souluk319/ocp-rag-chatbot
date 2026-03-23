<!-- source: ocp-service-network-troubleshooting-ko.md -->

# OpenShift/Kubernetes Service 및 네트워크 트러블슈팅 가이드

안녕하세요, 신입 엔지니어 여러분.
OpenShift Container Platform(OCP)이나 Kubernetes(K8s) 환경에서 애플리케이션이 통신하지 않거나 네트워크 오류가 발생하면, 가장 먼저 의심해야 할 대상은 **Service**와 **네트워크 정책**입니다. 이 문서는 Service 연결 실패, DNS 문제, NetworkPolicy 차단, 노드 장애, 그리고 실제 현장에서 즉시 적용할 수 있는 디버깅 기법들을 체계적으로 정리한 것입니다.

---

## 1. Service 에 연결이 안 될 때 확인사항

Service 는 Pod 의 IP 가 변동되더라도 클라이언트가 일관된 엔드포인트를 사용할 수 있게 해주는 핵심 추상화입니다. Service 가 작동하지 않는 경우, 다음 3 가지 요소를 반드시 순서대로 점검해야 합니다.

### 1.1 핵심 확인 항목
Service 가 Pod 와 제대로 매칭되지 않았을 때, 트래픽은 Service 로는 들어오지만 Pod 로 전달되지 않습니다.

1.  **Selector 매칭 여부**: Service 의 `selector` 라벨이 해당 Pod 의 라벨과 정확히 일치하는지 확인해야 합니다. 한 글자라도 다르면 Endpoint 가 생성되지 않습니다.
2.  **Endpoint 가 생성되었는지**: Service 가 정의되어 있다고 해서 자동으로 Pod 가 연결되는 것은 아닙니다. `endpoints` 리소스에 해당 Service 의 IP 와 포트가 등록되었는지 확인해야 합니다.
3.  **Port 매핑**: Service 의 `targetPort` 가 Pod 에서 실제로 수신 중인 포트 (컨테이너 포트) 와 일치하는지 확인해야 합니다.

### 1.2 진단 명령어 및 예시

```bash
# 1. Service 정의 확인 (Selector 확인)
oc get svc my-app-service -n my-project -o yaml

# 2. Endpoint 확인 (Pod IP 가 등록되었는지)
oc get endpoints my-app-service -n my-project

# 3. Pod 의 실제 라벨 확인 (Selector 매칭 테스트)
oc get pods -n my-project -o custom-columns=NAME:.metadata.name,LABELS:.metadata.labels

# 4. 직접 포트 테스트 (호스트에서)
# <Service IP> 는 'oc get svc' 로 확인
oc exec -it <pod-name> -- nc -zv <service-ip> <service-port>
```

---

## 2. DNS 이름으로 Pod 간 통신이 안 될 때

Kubernetes 내부에서는 서비스명을 DNS 이름으로 접근할 수 있습니다. 하지만 `my-app-service` 만으로는 통신이 안 되며, 반드시 네임스페이스와 도메인을 포함한 완전한 이름 (`my-app-service.my-project.svc.cluster.local`) 을 사용해야 합니다.

### 2.1 CoreDNS 및 DNS 구성 문제
Pod 간 통신이 DNS 를 통해 끊기는 경우, 대부분 **CoreDNS** 포드가 정상적으로 실행되지 않거나, Pod 의 네트워크 이름공간 (Network Namespace) 이 제대로 설정되지 않았을 때 발생합니다.

*   **완전한 DNS 이름**: `service-name.namespace.svc.cluster.local`
*   **단축형 (네임스페이스 내)**: `service-name` (같은 네임스페이스 내 Pod 간에만 유효)

### 2.2 진단 방법
DNS 쿼리가 실패하는지 확인하고, CoreDNS 포드가 정상적으로 라우팅을 처리하는지 확인합니다.

```bash
# 1. Pod 내부에서 nslookup 또는 dig 테스트
oc exec -it <pod-name> -- nslookup my-app-service.my-project.svc.cluster.local

# 2. CoreDNS 포드 상태 확인
oc get pods -n kube-system -l k8s-app=kube-dns

# 3. CoreDNS 로그 확인 (ERR 메시지가 있는지)
oc logs -n kube-system <coredns-pod-name> | grep "my-app-service"
```

---

## 3. NetworkPolicy 때문에 트래픽이 차단되는 경우

OCP 와 K8s 에서 `NetworkPolicy` 는 디폴트 허용 (Default Deny) 모드가 아닌 경우에도 명시적으로 허용되지 않는 트래픽을 차단할 수 있습니다. 특히 OCP 는 네트워크 격리 (Network Segmentation) 를 강력하게 지원합니다.

### 3.1 차단 원인 분석
트래픽이 차단되는 주된 이유는 다음과 같습니다.
*   **Default Deny Policy 존재**: 해당 네임스페이스에 `ingress: []` 와 `egress: []` 를 모두 비어있는 Policy 가 적용되어 있어, 명시적으로 허용하지 않은 모든 트래픽을 차단합니다.
*   **Selector 미적용**: 발신자 (Source) 와 수신자 (Destination) 의 Pod Selector 가 일치하지 않습니다.
*   **Port/Protocol 제한**: 허용된 포트나 프로토콜 (TCP/UDP) 이 아닙니다.

### 3.2 진단 명령어
```bash
# 1. 네임스페이스 내 NetworkPolicy 목록 확인
oc get networkpolicy -n my-project

# 2. Policy 상세 확인 (Ingress/Egress 규칙)
oc get networkpolicy <policy-name> -n my-project -o yaml

# 3. Pod 에 적용된 Policy 확인
oc get networkpolicy -n my-project -o jsonpath='{.items[*].spec.podSelector}'
```

---

## 4. 노드가 NotReady 상태일 때 대응방법

노드가 `NotReady` 상태가 되면 해당 노드에 스케줄링되지 않으며, 기존 Pod 이 재시도 (Reschedule) 됩니다. 이는 클러스터의 안정성에 치명적입니다.

### 4.1 주요 원인
*   **Kubelet 실패**: 노드 에이전트 자체가 죽거나 통신이 끊김.
*   **리소스 압박**: 디스크 공간 부족 (DiskPressure), 메모리 부족 (MemoryPressure), PID 한계 도달.
*   **네트워크 연결 끊김**: 노드와 Master 노드 간 통신 단절.

### 4.2 단계별 대응 절차
1.  **상태 확인**: 노드가 무엇 때문에 NotReady 인지 확인.
2.  **리소스 점검**: 디스크와 메모리 사용량 확인.
3.  **Kubelet 재시작**: 문제 해결 후 Kubelet 재부팅.
4.  **노드 재부팅**: 최후의 수단.

```bash
# 1. 노드 상태 상세 확인
oc get nodes -o wide

# 2. 노드 상세 정보 확인 (Conditions)
oc describe node <node-name>
# -> Events 섹션에서 DiskPressure, MemoryPressure 등 확인

# 3. 디스크 사용량 확인 (노드 내부 SSH 필요 시)
ssh <node-ip> "df -h"

# 4. Kubelet 재시작 (가장 일반적인 해결책)
oc adm node-drain <node-name> --ignore-daemonsets
oc delete pod -n kubelet -l k8s-app=kubelet -n <node-name> --namespace=kube-system
# 또는 직접 kubelet 서비스 재시작 (SSH 필요)
ssh <node-ip> "systemctl restart kubelet"

# 5. 노드 상태 회복 확인
oc get nodes
```

---

## 5. oc debug 를 이용한 네트워크 디버깅

`oc debug` 명령어는 문제 발생 시 해당 Pod 의 컨텍스트로 진입하여 직접 진단할 수 있는 강력한 도구입니다.

### 5.1 활용 시나리오
*   Pod 내부에서 `curl` 로 서비스 연결 테스트.
*   Pod 내부에서 `nslookup` 로 DNS 테스트.
*   Pod 내부에서 `tcpdump` 로 패킷 캡처.

### 5.2 명령어 예시
```bash
# 1. Pod 내부 shell 진입
oc debug -it -c <container-name> <pod-name> -n <namespace>

# 2. Pod 내부에서 외부 서비스 연결 테스트
# (예: Nginx Service 테스트)
oc exec -it <pod-name> -- curl -v http://my-nginx-service:80

# 3. Pod 내부에서 DNS 테스트
oc exec -it <pod-name> -- nslookup my-nginx-service.default.svc.cluster.local

# 4. 네트워크 패킷 캡처 (tcpdump)
oc debug -it --image=busybox:latest <pod-name> -n <namespace>
# 진입 후 tcpdump 실행
tcpdump -i eth0 -n port 80
```

---

## 6. 실무 디버깅 명령어 모음

일상 업무에서 가장 빈번하게 사용하는 네트워크 관련 명령어들을 정리했습니다.

| 목적 | 명령어 | 비고 |
| :--- | :--- | :--- |
| **Service IP 조회** | `oc get svc <name> -o jsonpath='{.status.loadBalancer.ingress[0].ip}'` | LoadBalancer 타입일 때 |
| **Endpoint IP 조회** | `oc get endpoints <name> -o jsonpath='{.subsets[0].addresses[0].ip}'` | 첫 번째 Pod IP 확인 |
| **Port 매핑 확인** | `oc get svc <name> -o jsonpath='{.spec.ports[0].port}:{.spec.ports[0].targetPort}'` | Service Port : Target Port |
| **DNS 이름 풀이** | `oc exec <pod> -- nslookup <service>.<ns>.svc.cluster.local` | DNS 동작 여부 확인 |
| **내부 연결 테스트**
