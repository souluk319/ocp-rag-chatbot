<!-- source: ocp-oomkilled-troubleshooting-ko.md -->

# OOMKilled 트러블슈팅 가이드: OpenShift 및 Kubernetes 메모리 오버플로우 대응

## 1. OOMKilled 란 무엇인가

**OOMKilled (Out Of Memory Killed)** 는 컨테이너나 프로세스가 운영체제가 할당해주고 있는 메모리 한도를 초과하여 실행을 중단했을 때 발생하는 상태입니다. OpenShift Container Platform(OCP) 과 Kubernetes(K8s) 환경에서 이는 매우 빈번하게 발생하는 트러블슈팅 사례 중 하나입니다.

일반적인 운영체제에서는 메모리 부족 시 프로세스를 강제 종료할 수 있지만, K8s 와 같은 오케스트레이션 플랫폼은 노드(Node) 전체의 메모리 사용을 통제해야 하므로 개별 컨테이너의 메모리 사용을 엄격히 제한합니다. OOMKilled 가 발생하면 해당 Pod 은 즉시 `Running` 상태에서 `Terminated` 로 넘어가며, 재시작 정책 (RestartPolicy) 에 따라 다시 시작되거나 실패 상태로 남을 수 있습니다. 이는 애플리케이션의 가용성 저하로 이어질 수 있으므로 신속한 원인 분석과 조치가 필수적입니다.

## 2. 발생 원인

OOMKilled 가 발생하는 주된 원인은 크게 **리소스 설정의 부재**와 **애플리케이션의 메모리 누수**로 나눌 수 있습니다.

*   **Requests/Limits 미설정 또는 설정 부족**: Pod 의 메모리 리소스 `limits` 가 설정되지 않았거나, 애플리케이션이 실제로 필요로 하는 메모리보다 설정된 `limits` 가 너무 낮을 경우 발생합니다. K8s 는 `limits` 가 설정되지 않은 경우 노드 전체의 여유 메모리를 사용할 수 있게 하지만, 노드가 메모리 부족으로 인해 OOM Killer 를 시스템 수준에서 트리거하면 Pod 전체가 죽을 수 있습니다.
*   **메모리 누수 (Memory Leak)**: 애플리케이션 코드 내에 메모리 할당 후 해제되지 않는 버그가 있어, 시간이 지날수록 메모리 사용량이 지속적으로 증가하여 한도를 초과하는 경우입니다.
*   **갑작스러운 트래픽 급증**: 예상치 못한 대량 트래픽으로 인해 순간적으로 메모리 사용량이 피크를 찍어 한도를 넘은 경우입니다.

## 3. 진단 방법

OOMKilled 가 발생했을 때 가장 먼저 확인해야 할 것은 해당 Pod 의 상태와 에러 로그입니다.

### Pod 상세 정보 확인 (`oc describe` / `kubectl describe`)
`oc describe pod <pod-name>` 명령어를 실행하면 Pod 의 상태, 이벤트, 그리고 **Reason** 필드에 `OOMKilled` 라는 키워드가 명시적으로 표시됩니다. 또한, `Last State` 섹션에서 종료 코드가 `137` (SIGKILL) 인 경우 대부분 OOMKilled 입니다.

```bash
# OpenShift CLI 사용
oc describe pod <pod-name> -n <namespace>

# Kubernetes CLI 사용
kubectl describe pod <pod-name> -n <namespace>
```

### 노드 및 Pod 수준 리소스 사용량 확인
현재 클러스터 내 Pod 들의 메모리 사용량을 실시간으로 모니터링할 수 있습니다.

```bash
# OpenShift 관리자로 노드 및 Pod 사용량 확인
oc adm top pods -n <namespace>

# Kubernetes CLI 사용
kubectl top pods -n <namespace>
```

*주의: `oc adm top` 은 클러스터 내 모든 Pod 의 리소스 사용량을 보여주며, 특정 Pod 이 메모리 한도에 근접하거나 한도를 초과하는지 파악하는 데 유용합니다.*

## 4. 해결: 리소스 Limits 조정

가장 일반적인 해결책은 Pod 의 메모리 `limits` 를 적절히 조정하는 것입니다. 메모리 누수가 의심될 경우 `requests` 와 `limits` 를 동일하게 설정하여 컨테이너가 할당받은 메모리 내에서 동작하도록 강제할 수도 있습니다.

다음은 메모리 한도를 2Gi 로 조정하는 YAML 예시입니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memory-intensive-app
  namespace: production
spec:
  replicas: 1
  selector:
    matchLabels:
      app: memory-intensive-app
  template:
    metadata:
      labels:
        app: memory-intensive-app
    spec:
      containers:
      - name: app
        image: myregistry/app:v1.2.3
        resources:
          requests:
            memory: "1Gi"   # 최소 보장 메모리
            cpu: "500m"
          limits:
            memory: "2Gi"   # 최대 허용 메모리 (OOMKilled 방지용)
            cpu: "1000m"
```

이 YAML 을 적용하기 위해 `oc edit` 또는 `oc apply` 명령어를 사용할 수 있습니다.

```bash
# 기존 리소스 설정을 수정하여 적용
oc edit deployment memory-intensive-app -n production
```

## 5. 클러스터 리소스 사용량 확인 방법

OOMKilled 를 방지하기 위해서는 클러스터 전체의 메모리 여유량을 파악하는 것이 중요합니다. 노드가 메모리 부족 상태 (Pressure) 에 있다면, 새로운 Pod 이 스키줄될 수 없거나 기존 Pod 이 OOMKilled 될 위험이 높습니다.

```bash
# 노드 상태 및 메모리 사용량 확인
oc get nodes -o wide

# 노드 상세 정보에서 메모리 사용률 확인
oc describe node <node-name>
```

`oc describe node` 출력 결과의 `Conditions` 섹션에서 `MemoryPressure` 가 `True` 로 표시된다면 해당 노드는 메모리 부족 상태임을 의미하며, 해당 노드에서 실행 중인 Pod 의 리소스 할당을 재검토해야 합니다.

## 6. 이전 컨테이너 로그 보는 방법

Pod 이 OOMKilled 되어 재시작 (Restart) 되었다면, 현재 실행 중인 컨테이너는 종료된 직후의 로그를 포함하지 않을 수 있습니다. 종료된 컨테이너의 로그를 확인하려면 `--previous` 플래그를 사용하여 이전 인스턴스의 로그를 조회해야 합니다.

```bash
# 이전 컨테이너의 로그 확인 (OpenShift/Kubernetes 동일)
oc logs <pod-name> -c <container-name> --previous -n <namespace>
kubectl logs <pod-name> -c <container-name> --previous -n <namespace>
```

로그를 통해 애플리케이션이 메모리 부족 에러 (예: `java.lang.OutOfMemoryError`, `std::bad_alloc`) 를 발생시키기 직전의 동작을 확인할 수 있습니다.

## 7. 실무 팁 및 주의사항

1.  **Memory Leak 판단**: 단순히 `limits` 를 높여 문제를 해결하는 것은 임시 방편일 수 있습니다. `--previous` 로그를 확인하여 메모리 누수인지, 아니면 트래픽 스파이크인지 구분해야 합니다. 누수라면 코드 수정이 필수적입니다.
2.  **Ephemeral Containers 활용**: 문제가 지속될 경우, 개발자가 노드 내부로 진입하여 직접 프로세스를 확인하거나 디버깅할 수 있도록 `oc debug` 또는 `kubectl debug` 명령어를 사용하여 일시적인 디버깅 컨테이너를 생성할 수 있습니다.
    ```bash
    oc debug pod/<pod-name> -n <namespace>
    ```
3.  **Vertical Pod Autoscaler (VPA)**: 수동으로 리소스를 조정하기 번거롭다면, K8s 의 VPA 를 도입하여 애플리케이션의 실제 사용 패턴에 따라 메모리 리소스를 자동으로 조정할 수 있습니다.
4.  **노드 재부팅 주의**: OOMKilled 가 발생한 노드가 메모리 누수로 인해 지속적으로 문제를 일으킨다면, 해당 노드를 교체하거나 재부팅하여 노드 자체의 메모리 관리 문제를 확인해야 합니다.
5.  **HugePages 고려**: 특정 애플리케이션 (예: 고주파 거래 시스템, 머신러닝 추론) 의 경우 일반 메모리 대신 HugePages 를 사용하여 메모리 할당 오버헤드를 줄일 수 있는지 검토해 볼 가치가 있습니다.

이 가이드를 통해 OOMKilled 에 대한 근본 원인을 파악하고, 적절한 리소스 조정 및 모니터링을 통해 클러스터의 안정성을 유지하시기 바랍니다.
