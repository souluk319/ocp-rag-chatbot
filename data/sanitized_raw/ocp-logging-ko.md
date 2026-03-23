<!-- source: ocp-logging-ko.md -->

# OCP 로깅 & 로그 수집 가이드

## 1. 로깅 개요: 컨테이너 로그의 특성과 중앙 집중식 필요성

컨테이너 기반 아키텍처로 전환되면서 로깅 전략은 근본적인 변화를 겪었습니다. 기존의 가상머신 (VM) 환경에서는 파일 시스템에 직접 로그를 기록할 수 있었으나, 컨테이너는 **임시성 (Ephemeral)**을 갖습니다. 이는 컨테이너가 종료되거나 리부팅될 때 해당 컨테이너 내부의 파일 시스템이 즉시 삭제됨을 의미합니다.

따라서 애플리케이션 개발자가 `console.log` 나 `System.out.println` 으로 출력한 로그는 컨테이너가 종료되는 순간 사라집니다. 만약 문제를 디버깅하기 위해 해당 컨테이너를 다시 시작하면, 과거의 로그는 영구적으로 손실됩니다. 이러한 특성을 극복하기 위해 **중앙 집중식 로깅 (Centralized Logging)**이 필수적입니다.

중앙 집중식 로깅은 다음과 같은 문제를 해결합니다:
*   **가용성 보장**: 컨테이너가 죽더라도 로그 데이터는 안전합니다.
*   **통합 관측성**: 수백 개의 노드에 배포된 Pod 의 로그를 한 곳에서 검색하고 분석할 수 있습니다.
*   **보안 및 감사**: 시스템 이벤트나 사용자 접근 이력을 체계적으로 보관하여 규제 준수를 지원합니다.

## 2. OCP 로깅 스택 (OpenShift Logging Stack)

OpenShift Container Platform 은 자체적인 로깅 스택을 제공하며, 이를 통해 로그의 수집, 전송, 저장, 시각화를 손쉽게 관리할 수 있습니다. OpenShift Logging Operator 는 이 스택을 구성하는 모든 컴포넌트를 자동 프로비저닝하고 관리합니다.

주요 컴포넌트들은 다음과 같습니다:

| 컴포넌트 | 역할 및 설명 |
| :--- | :--- |
| **OpenShift Logging Operator** | 로깅 스택 전체를 관리하는 제어 평면 (Control Plane). 다른 컴포넌트의 설치, 업데이트, 백업/복구를 담당합니다. |
| **Log Collector (Fluentd/Vector)** | 각 노드의 DaemonSet 으로 설치되어 Pod 의 stdout/stderr 를 캡처합니다. Vector 는 최신 버전에서 성능과 리소스 효율성이 뛰어납니다. |
| **Log Forwarder** | 수집된 로그를 저장소 (Elasticsearch) 나 외부 시스템 (Splunk, Kafka 등) 으로 전송하는 역할입니다. |
| **Storage Backend (Elasticsearch/Loki)** | 로그 데이터를 저장하는 엔진입니다. OCP 기본 제공은 Elasticsearch 기반이며, 일부 배포에서는 Loki 를 지원합니다. |
| **Visualization (Kibana)** | 저장된 로그를 검색, 필터링, 시각화하여 제공하는 웹 인터페이스입니다. |

## 3. 로그 종류: 애플리케이션, 인프라, 감사 로그

중앙 집중식 로깅은 단순한 애플리케이션 로그뿐만 아니라 다양한 원천의 로그를 포함합니다.

*   **애플리케이션 로그**: 개발자가 코드로 출력한 비즈니스 로직 관련 로그 (예: 주문 처리, API 호출 결과). 주로 JSON 형식으로 구조화되어 있는 것이 이상적입니다.
*   **인프라 로그**: Pod 의 시작/종료 이벤트, 컨테이너 오케스트레이션 상태, 네트워크 오류 등 Kubernetes 및 노드 수준의 로그.
*   **감사 (Audit) 로그**: 클러스터 내에서의 중요한 작업 (예: ConfigMap 수정, Role Binding 변경) 이 수행되었음을 기록하는 로그. 보안 규정 준수를 위해 반드시 보관해야 합니다.

## 4. 로그 조회 명령어: `oc logs` 활용법

일상적인 디버깅을 위해 Pod 의 로그를 직접 조회하는 명령어는 매우 유용합니다.

*   **기본 조회**: 특정 Pod 의 최신 로그를 한 번에 출력합니다.
    ```bash
    oc logs <pod-name>
    ```
*   **실시간 스트리밍**: 로그가 생성되는 대로 실시간으로 출력합니다. (디버깅 시 가장 많이 사용)
    ```bash
    oc logs -f <pod-name>
    ```
    *주의: 컨테이너가 종료된 후에도 `-f` 를 사용하면 더 이상 로그가 나오지 않습니다.*
*   **이전 컨테이너 로그 조회**: Pod 가 재시작 (Restart) 되었을 때, 현재 실행 중인 컨테이너가 아닌 **이전** 컨테이너의 로그를 봅니다.
    ```bash
    oc logs --previous <pod-name>
    ```
*   **시간 범위 제한**: 특정 시간대의 로그만 추출합니다.
    ```bash
    oc logs <pod-name> --since=10m --tail=100
    ```

## 5. 멀티 컨테이너 Pod 로그 조회

하나의 Pod 안에 여러 개의 컨테이너 (예: 애플리케이션 컨테이너와 Sidecar 컨테이너) 가 존재할 경우, 특정 컨테이너의 로그만 선택적으로 조회해야 합니다.

```bash
# 컨테이너 이름으로 필터링
oc logs <pod-name> -c <container-name>

# 예시: 'app' 컨테이너의 로그만 보기
oc logs my-web-app-pod -c app
```

## 6. Logging Operator 설치 및 구성

OpenShift 클러스터에서 로깅 스택을 활성화하려면 `ClusterLogging` 커스텀 리소스 (CR) 를 생성해야 합니다. 이는 Operator 가 필요한 컴포넌트 (DaemonSet, Service, Storage 등) 를 자동으로 설치합니다.

### ClusterLogging CR 예시
```yaml
apiVersion: logging.openshift.io/v1
kind: ClusterLogging
metadata:
  name: cluster-logging
spec:
  collection:
    type: fluentd
    fluentd:
      logging:
        type: file
        file:
          logFile: /var/log/fluentd.log
          maxSize: 100M
          maxAge: 3d
          maxBackups: 7
  forwarding:
    type: elasticsearch
    elasticsearch:
      logging:
        type: file
        file:
          logFile: /var/log/fluentd-elasticsearch.log
          maxSize: 100M
          maxAge: 3d
          maxBackups: 7
  visualization:
    type: kibana
    kibana:
      logging:
        type: file
        file:
          logFile: /var/log/kibana.log
          maxSize: 100M
          maxAge: 3d
          maxBackups: 7
```

### ClusterLogForwarder 설정
로그를 특정 스토리지나 외부 시스템으로 보낼 경우 `ClusterLogForwarder` CR 을 사용합니다.

```yaml
apiVersion: logging.openshift.io/v1
kind: ClusterLogForwarder
metadata:
  name: cluster-log-forwarder
spec:
  pipelines:
    - name: default-pipeline
      input: application
      filters:
        - type: exclude
          expression: 'labels.app == "kube-apiserver"' # 시스템 로그 제외
      outputs:
        - name: elasticsearch
          type: elasticsearch
          namespace: logging
          config:
            hosts:
              - logging-es-http.logging.svc:9200
```

## 7. 로그 포워딩: 외부 시스템으로 전송

내부 Elasticsearch 가 포화 상태이거나, 더 강력한 분석 엔진 (Splunk, Datadog) 이나 메시지 큐 (Kafka) 를 사용해야 할 때 로그 포워딩이 필요합니다.

*   **Splunk**: 로그 데이터를 Splunk HEC (HTTP Event Collector) 로 전송하여 엔터프라이즈급 분석을 수행합니다.
*   **CloudWatch**: AWS 환경에서 CloudWatch Logs 를 통합하여 모니터링합니다.
*   **Kafka**: 실시간 스트리밍 처리를 위해 로그를 Kafka 토픽으로 발행합니다.

`ClusterLogForwarder` 의 `outputs` 섹션에서 타입을 `splunk`, `cloudwatch`, `kafka` 등으로 변경하여 구성합니다.

## 8. 로그 필터링 & 파싱: 구조화된 로그의 중요성

인덱스 기반 검색이 아닌 **필드 기반 검색**을 위해서는 로그가 구조화되어야 합니다.

*   **구조화된 로그 (JSON)**:
    ```json
    {"timestamp": "2023-10-27T10:00:00Z", "level": "ERROR", "service": "payment", "message": "DB Connection Failed"}
    ```
    이를 기반으로 다음과 같은 복잡한 쿼리가 가능합니다.
    ```kql
    service="payment" AND level="ERROR"
    ```
*   **파싱 (Parsing)**: 비구조화된 로그 (예: `2023-10-27 ERROR [payment] DB failed`) 를 JSON 형식으로 변환하는 플러그인 (Fluentd/Parsers) 을 적용해야 합니다.

## 9. 실무 팁 및 주의사항

성공적인 로깅 운영을 위한 실무적 조언입니다.

1.  **로그 보존 기간 설정**: 로그는 무한정 보관하면 안 됩니다. `ClusterLogForwarder` 또는 Elasticsearch 설정에서 `retention` 을 적절히 설정하여 디스크 공간을 확보하세요. (예: 7 일~30 일)
2.  **디
