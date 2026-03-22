<!-- source: ocp-monitoring-ko.md -->

# OCP/Kubernetes 모니터링 및 로깅 가이드

안녕하세요, 신입 엔지니어 여러분.
오늘날 클라우드 네이티브 환경에서는 애플리케이션의 가용성과 성능을 유지하기 위해 **모니터링 (Monitoring)**과 **로깅 (Logging)**이 필수적입니다. 특히 OpenShift Container Platform (OCP) 과 같은 관리형 플랫폼에서는 수천 개의 Pod 이 동적으로 생성되고 소멸하기 때문에, 체계적인 관찰 가능성 (Observability) 체계를 구축하지 않으면 장애 발생 시 원인 파악이 거의 불가능해집니다.

이 가이드는 OCP 환경에서 메트릭, 로그, 트레이스를 효과적으로 수집하고 분석하는 방법을 단계별로 설명합니다.

---

## 1. 모니터링 개요: 관찰 가능성의 3 가지 축

전통적인 모니터링은 "시스템이 정상적으로 작동하는지 확인"하는 데 주력했으나, 현대의 분산 시스템에서는 **"왜 문제가 발생했는지, 그리고 어떻게 해결할 수 있는지"**에 대한 깊은 통찰이 필요합니다. 이를 위해 **관찰 가능성 (Observability)**이라는 개념이 등장했습니다.

관찰 가능성은 다음 3 가지 핵심 축으로 구성됩니다.

*   **메트릭 (Metrics)**: 시스템의 상태와 성능을 수치화한 데이터입니다. CPU 사용률, 메모리 점유율, 요청 처리 지연 시간 (Latency) 등이 여기에 해당합니다. 메트릭은 주로 "현재 상태가 어떻게 되는가?"를 파악하는 데 사용됩니다.
*   **로그 (Logs)**: 애플리케이션이나 시스템에서 발생하는 이벤트에 대한 상세한 텍스트 기록입니다. "왜 에러가 발생했는가?"라는 질문에 답할 때 가장 중요한 정보원입니다.
*   **트레이스 (Traces)**: 분산 애플리케이션 내에서 하나의 요청이 여러 마이크로서비스를 거쳐 이동하는 경로를 추적하는 데이터입니다. 성능 병목 현상을 특정 서비스로 좁히는 데 필수적입니다.

OCP 환경에서는 이 세 가지 축을 통합하여 관리할 때 가장 높은 가시성을 확보할 수 있습니다.

---

## 2. Prometheus: 메트릭 수집의 표준

Prometheus 는 Cloud Native Foundation 에서 관리하는 오픈소스 모니터링 시스템으로, 현재 K8s 생태계에서 사실상의 표준으로 자리 잡았습니다.

### 개념 및 아키텍처
Prometheus 는 **Pull-based** 모델로 동작합니다. 즉, 모니터링 서버가 주기적으로 모니터링 대상 (Exporter) 에서 메트릭을 가져옵니다. 주요 구성 요소는 다음과 같습니다.

*   **Prometheus Server**: 메트릭을 수집, 저장, 쿼리하는 핵심 엔진입니다.
*   **AlertManager**: 서버에서 정의된 규칙 (Rule) 을 위반했을 때 알림을 생성하고, 알림을 그룹화하여 발송하는 컴포넌트입니다.
*   **Exporter**: 모니터링 대상 애플리케이션이나 인프라 (예: Node Exporter, Blackbox Exporter) 에서 Prometheus 가 읽을 수 있는 형식 (Prometheus Text Format) 으로 메트릭을 노출하는 프로그램입니다.
*   **Service Discovery**: Kubernetes 클러스터 내의 Pod 이나 노드가 생성/소멸될 때마다 자동으로 모니터링 대상 목록을 업데이트합니다.

### 메트릭 수집 방식
Kubernetes 에서 Prometheus 는 `ServiceMonitor` 또는 `PodMonitor` 라는 Kubernetes 리소스를 통해 자동으로 Exporter 를 찾아 메트릭을 수집합니다. 이는 수동으로 Exporter 를 설치하고 IP 를 관리하는 번거로움을 없애줍니다.

### PromQL 기본 쿼리 예시
Prometheus 는 자체 쿼링 언어인 **PromQL**을 사용합니다.

```promql
# 전체 노드의 CPU 사용률 평균 계산
sum(rate(node_cpu_seconds_total{mode!="idle"}[5m])) / count(node_cpu_seconds_total{mode!="idle"})

# 특정 네임스페이스의 Pod 당 메모리 사용량 상위 3 개 찾기
topk(3, sum by (pod) (container_memory_usage_bytes{namespace="my-app"}))

# HTTP 5xx 에러율 계산 (지난 1 분 동안)
sum(rate(http_requests_total{status=~"5.."}[1m])) / sum(rate(http_requests_total[1m]))
```

---

## 3. Grafana: 시각화와 대시보드

수집된 메트릭을 그래프나 차트로 직관적으로 보여주는 도구인 **Grafana**는 Prometheus 와의 연동이 매우 뛰어납니다.

### 대시보드 개념
Grafana 대시보드는 사용자가 정의한 레이아웃으로, 여러 데이터 소스 (Data Source) 의 메트릭을 하나의 화면에 배치하여 상태 한눈에 파악할 수 있게 합니다. 예를 들어, 클러스터 전체의 CPU/메모리 사용률과 특정 애플리케이션의 요청 수를 동시에 표시할 수 있습니다.

### Prometheus 데이터 소스 연동
OCP 환경에서는 Grafana 가 이미 `openshift-monitoring` 네임스페이스에 설치되어 있어, 별도의 설정 없이 Prometheus 데이터 소스를 선택하면 즉시 대시보드를 사용할 수 있습니다.
1.  Grafana UI 로 접속합니다.
2.  `Configuration` -> `Data Sources` 에서 `Prometheus` 를 선택합니다.
3.  URL 에 `https://prometheus-k8s.openshift-monitoring.svc:9090` 을 입력합니다.
4.  `Dashboard` 메뉴에서 OCP 제공 대시보드를 불러와 커스터마이징할 수 있습니다.

---

## 4. OCP 내장 모니터링

OpenShift 는 자체적인 모니터링 스택인 **OpenShift Monitoring Stack**을 제공합니다. 이는 Prometheus 와 Grafana 를 기반으로 하며, `openshift-monitoring` 네임스페이스에 설치되어 있습니다.

*   **장점**: 설치 및 유지보수가 자동화되어 있으며, OCP 의 고유 리소스 (MachineConfig, ClusterOperator 등) 에 대한 모니터링 템플릿이 기본적으로 제공됩니다.
*   **기본 제공 대시보드**:
    *   **Cluster Overview**: 클러스터 전체의 고가용성 상태, 노드 상태, Pod 상태 등을 한눈에 봅니다.
    *   **Workload**: 특정 프로젝트 내 애플리케이션의 성능을 모니터링합니다.
    *   **Node**: 각 노드의 리소스 사용률과 디스크 상태를 확인합니다.

---

## 5. 로깅 스택: EFK/ELK 개요

로그 관리는 **EFK 스택** 또는 **ELK 스택**이라고 불리며, 다음 3 가지 컴포넌트로 구성됩니다.

1.  **Elasticsearch**: 로그 데이터를 저장하고 검색하는 분산 검색 엔진입니다. 대용량 로그를 효율적으로 관리합니다.
2.  **Fluentd / Fluent Bit**: 로그 수집 에이전트입니다. 각 노드나 컨테이너에서 발생하는 로그를 수집하여 Elasticsearch 로 전송합니다. (Fluent Bit 는 가볍고 K8s 환경에 최적화되어 있습니다.)
3.  **Kibana**: 로그 데이터를 시각화하고 검색, 분석하기 위한 웹 인터페이스입니다.

---

## 6. OCP Logging Operator 를 통한 로그 수집

OpenShift 는 EFK 스택을 직접 설치할 필요가 없이 **Logging Operator**를 통해 로그 관리를 제공합니다.

*   **작동 원리**: Logging Operator 는 `LogCollector` 와 같은 리소스를 통해 각 노드에서 **Fluent Bit**를 자동으로 설치하고 구성합니다.
*   **설정**: 사용자는 `ClusterLogStreamer` 와 같은 리소스를 생성하여 로그를 Elasticsearch 로 스트리밍하도록만 지시하면 됩니다.
*   **접근**: 설치된 후 `openshift-logging` 네임스페이스의 Kibana 서비스 (예: `https://kibana-openshift-logging.openshift-logging.svc`) 를 통해 로그를 검색할 수 있습니다.

---

## 7. 알림 (Alert) 설정: PrometheusRule 및 AlertManager

장애 발생 시 신속한 대응을 위해 알림 설정이 필수적입니다.

### PrometheusRule
OCP 환경에서는 `PrometheusRule`이라는 커스텀 리소스를 사용하여 모니터링 규칙을 정의합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: high-cpu-alert
  namespace: monitoring
spec:
  groups:
    - name: node-alerts
      rules:
        - alert: HighCPUUsage
          expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High CPU usage on {{ $labels.instance }}"
            description: "CPU usage is above 80% for more than 5 minutes."
```

### AlertManager 라우팅
규칙이 위반되면 AlertManager 가 알림을 처리합니다. 라우팅 규칙을 통해 어떤 채널 (Slack, Email, PagerDuty 등) 에 알람을 보내는지 정의할 수 있습니다.

---

## 8. 실무 명령어 및 팁

일상적인 작업에서 유용한 `oc` 및 `kubectl` 명령어들을 정리합니다.

### 주요 명령어

*   **노드 및 Pod 리소스 확인**
    ```bash
    # OCP 의 oc adm top 명령어 (kubectl top 과 유사하지만 OCP 특화)
    oc adm top nodes
    oc adm top pods -n <namespace>

    # 상세한 노드 정보 확인
    oc get
