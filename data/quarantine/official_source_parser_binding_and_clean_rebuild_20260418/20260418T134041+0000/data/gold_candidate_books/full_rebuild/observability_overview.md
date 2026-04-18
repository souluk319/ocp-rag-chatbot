# 관찰 기능 개요

## OpenShift Container Platform의 관찰 기능에 대한 정보 포함

Red Hat OpenShift Observability는 다양한 시스템 지표, 로그, 추적 및 이벤트에 대한 실시간 가시성, 모니터링 및 분석을 제공하여 사용자가 시스템 또는 애플리케이션에 영향을 미치기 전에 문제를 신속하게 진단하고 해결할 수 있도록 지원합니다.

## 1장. Observability 정보

Red Hat OpenShift Observability는 다양한 시스템 지표, 로그, 추적 및 이벤트에 대한 실시간 가시성, 모니터링 및 분석을 제공하여 사용자가 시스템 또는 애플리케이션에 영향을 미치기 전에 문제를 신속하게 진단하고 해결할 수 있도록 지원합니다.

OpenShift Container Platform은 애플리케이션 및 인프라의 안정성, 성능 및 보안을 보장하기 위해 다음과 같은 Observability 구성 요소를 제공합니다.

모니터링

로깅

분산 추적

Red Hat build of OpenTelemetry

네트워크 관찰 기능

전원 모니터링

Red Hat OpenShift Observability는 오픈 소스 관찰 툴 및 기술을 연결하여 통합된 Observability 솔루션을 생성합니다. Red Hat OpenShift Observability의 구성 요소는 함께 협력하여 데이터를 수집, 저장, 제공, 분석 및 시각화할 수 있습니다.

참고

모니터링을 제외하고 Red Hat OpenShift Observability 구성 요소에는 코어 OpenShift Container Platform 릴리스 사이클과는 별도로 별도의 릴리스 사이클이 있습니다. 릴리스 호환성은 Red Hat OpenShift Operator 라이프 사이클 페이지를 참조하십시오.

### 1.1. 모니터링

CPU 및 메모리 사용량, 네트워크 연결 및 기타 리소스 사용에 대한 메트릭 및 사용자 지정 경고를 사용하여 OpenShift Container Platform에서 실행되는 애플리케이션의 클러스터 내 상태 및 성능을 모니터링합니다. 모니터링 스택 구성 요소는 Cluster Monitoring Operator에 의해 배포 및 관리됩니다.

모니터링 스택 구성 요소는 기본적으로 모든 OpenShift Container Platform 설치에 배포되며 CCMO(Cluster Monitoring Operator)에서 관리합니다. 이러한 구성 요소에는 Prometheus, Alertmanager, Thanos Querier 등이 포함됩니다.

CMO는 플랫폼 Prometheus 인스턴스에서 Red Hat으로 데이터의 하위 집합을 전송하여 클러스터의 원격 상태 모니터링을 용이하게 하는 Telemeter Client도 배포합니다.

자세한 내용은 OpenShift Container Platform 모니터링

정보 및 원격 상태 모니터링 정보를 참조하십시오.

### 1.2. 로깅

로그 데이터를 수집, 시각화, 전달 및 저장하여 문제를 해결하고 성능 병목 현상을 식별하고 보안 위협을 감지합니다. 5.7 이상 버전을 로깅할 때 사용자는 사용자 지정 경고 및 기록된 메트릭을 생성하도록 LokiStack 배포를 구성할 수 있습니다.

### 1.3. 분산 추적

분산 시스템을 통해 전달되는 대량의 요청, 전체 마이크로 서비스 스택, 많은 부하에서 발생하는 대량의 요청을 저장하고 시각화합니다.

분산 트랜잭션을 모니터링하고, 조정된 서비스, 네트워크 프로파일링, 성능 및 대기 시간 최적화, 근본 원인 분석, 최신 클라우드 네이티브 마이크로 서비스 기반 애플리케이션의 구성 요소 간 상호 작용 문제 해결에 대한 인사이트를 수집하는 데 사용합니다.

자세한 내용은 분산 추적 아키텍처를 참조하십시오.

### 1.4. Red Hat build of OpenTelemetry

소프트웨어의 성능 및 동작을 분석하고 이해하기 위해 원격 분석 추적, 메트릭 및 로그를 측정, 생성, 수집 및 내보냅니다. Tempo 또는 Prometheus와 같은 오픈 소스 백엔드를 사용하거나 상용 제품을 사용합니다. 단일 API 및 규칙 세트를 알아보고 사용자가 생성하는 데이터를 소유합니다.

자세한 내용은 Red Hat build of OpenTelemetry 에서 참조하십시오.

### 1.5. 네트워크 관찰 기능

OpenShift Container Platform 클러스터의 네트워크 트래픽을 관찰하고 Network Observability Operator를 사용하여 네트워크 흐름을 생성합니다. 자세한 정보 및 문제 해결을 위해 OpenShift Container Platform 콘솔에서 저장된 네트워크 흐름 정보를 보고 분석합니다.

자세한 내용은 Network Observability 개요 를 참조하십시오.

### 1.6. 전원 모니터링

워크로드의 전력 사용량을 모니터링하고 컨테이너 수준에서 측정된 CPU 또는 DRAM과 같이 주요 전력 소비 메트릭을 사용하여 클러스터에서 실행되는 가장 많은 전력 소비 네임스페이스를 식별합니다. Power Monitoring Operator를 통해 전원 관련 시스템 통계를 시각화하세요.

자세한 내용은 전원 모니터링 개요 를 참조하십시오.
