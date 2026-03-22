<!-- source: ocp-helm-ko.md -->

# OCP Helm & 패키지 관리 가이드

## 1. Helm 개요: Kubernetes 패키지 매니저

Helm 은 Kubernetes 의 공식 패키지 매니저로, 복잡한 Kubernetes 리소스 정의 (YAML) 를 관리하고 배포하는 데 필수적인 도구입니다. Kubernetes 가 초기 단계에서부터 존재했지만, 수많은 마이크로서비스와 애플리케이션을 배포할 때 수백 줄에 달하는 YAML 파일을 직접 작성하고 관리하는 것은 실용성이 떨어집니다. Helm 은 이러한 문제를 해결하기 위해 '앱 스토어'의 개념을 도입했습니다.

Helm 은 다음 세 가지 핵심 개념으로 구성됩니다.

*   **Chart**: 하나의 애플리케이션이나 서비스 배포에 필요한 모든 Kubernetes 리소스 정의의 집합입니다. 예를 들어, WordPress 도커 이미지만이 아닌, ConfigMap, Service, Deployment, Ingress 등을 포함한 전체 패키지입니다.
*   **Release**: 특정 Chart 를 클러스터에 설치했을 때 생성되는 인스턴스입니다. 같은 Chart 를 여러 번 설치하면 각 설치마다 고유한 Release 이름이 부여되어 버전 관리와 상태 추적 (Upgrade, Rollback) 이 가능합니다.
*   **Repository**: 여러 Chart 를 저장하고 공유하는 원격 저장소입니다. 공식 Helm Repository 나 조직 내부의私有 저장소를 통해 Chart 를 검색하고 다운로드할 수 있습니다.

Helm 을 사용하면 `helm install` 명령어로 복잡한 설정을 한 줄로 배포할 수 있으며, `helm upgrade` 로 변경 사항을 적용하고, `helm rollback` 로 이전 상태로 되돌릴 수 있어 운영 안정성이 크게 향상됩니다.

## 2. Helm 3 아키텍처: Tiller 제거 및 보안 개선

Helm 은 크게 v1 과 v2/v3 로 나뉩니다. 초기 Helm 1.x 버전은 클라이언트와 서버 (Tiller) 가 분리된 아키텍처를 가졌습니다. 클라이언트에서 명령을 보내면 Tiller 가 클러스터 내부에서 실행되어 실제 리소스를 생성했습니다.

하지만 Tiller 가 클러스터 내에 항상 실행되어야 한다는 점은 보안상 취약점이 되었습니다. Tiller 가 클러스터의 모든 권한을 가질 수 있기 때문에, Tiller 가 해킹당하면 전체 클러스터가 위험해집니다. 또한 Tiller 가 클러스터 리소스를 지속적으로 점유하여 노드 부하를 유발할 수 있었습니다.

**Helm 3** 는 이러한 문제를 해결하기 위해 아키텍처를 근본적으로 변경했습니다.

*   **Tiller 제거**: Helm 3 에서 Tiller 는 더 이상 존재하지 않습니다. 모든 작업이 클라이언트 측 (Local) 에서 수행됩니다.
*   **API 기반 통신**: Helm 클라이언트가 직접 Kubernetes API 서버에 `CustomResourceDefinition (CRD)` 을 생성하여 HelmRelease 라는 리소스를 배포합니다. 따라서 Helm 서버가 클러스터에常驻하지 않아도 됩니다.
*   **보안 강화**: 클러스터 내부에 항상 실행되는 privileged pod(Tiller) 이 제거되었으므로 공격 표면 (Attack Surface) 이 줄어들었습니다.

OpenShift Container Platform(OCP) 은 기본적으로 Helm 3 를 지원하며, Helm 1.x 기반의 Tiller 를 사용하는 것은 권장되지 않습니다.

## 3. Helm Chart 구조

Helm Chart 는 표준화된 디렉토리 구조를 따릅니다. 이 구조를 이해하는 것이 Chart 를 작성하거나 커스터마이징하는 첫걸음입니다.

```yaml
my-app-chart/
├── Chart.yaml           # Chart 의 메타데이터 (이름, 버전, 설명 등)
├── values.yaml          # 기본 설정값 (사용자가 오버라이드하는 부분)
├── Chart.lock           # 의존성 (Dependency) 의 버전 고정 정보
├── templates/           # Kubernetes 리소스 템플릿 (Go template 문법 사용)
│   ├── _helpers.tpl     # 공통 템플릿 함수 정의
│   ├── deployment.yaml  # Deployment 리소스 정의
│   ├── service.yaml     # Service 리소스 정의
│   └── configmap.yaml   # ConfigMap 리소스 정의
└── charts/              # 의존성 Chart 가 설치될 디렉토리
```

### 핵심 파일 설명

*   **Chart.yaml**: 이 Chart 의 식별자 역할을 합니다. `apiVersion`, `appVersion`, `version`, `description` 등을 정의합니다.
*   **values.yaml**: 사용자가 실제 배포 시 설정할 값을 저장합니다. 템플릿 파일에서 `{{ .Values.xxx }}` 형태로 참조됩니다. 이 파일을 수정하여 환경별 (Dev, Stage, Prod) 설정을 관리합니다.
*   **templates/**: 실제 Kubernetes YAML 파일이 생성되는 곳입니다. 여기서 Go 템플릿 문법을 사용하여 동적인 값을 대입합니다.

## 4. 기본 명령어

Helm 을 사용한 주요 작업 흐름은 다음과 같습니다.

### 설치 (Install)
새로운 애플리케이션을 배포합니다.
```bash
helm install my-release ./my-app-chart
# 또는 레포지토리에서 설치
helm install my-release bitnami/nginx
```

### 업그레이드 (Upgrade)
기존 릴리스를 수정하여 업데이트합니다.
```bash
helm upgrade my-release ./my-app-chart --set image.tag=latest
```

### 롤백 (Rollback)
업그레이드 중 문제가 발생했을 때 이전 버전으로 되돌립니다.
```bash
helm rollback my-release 1
# 1 은 성공한 이전 릴리스의 버전 번호
```

### 목록 확인 (List)
클러스터에 설치된 모든 릴리스를 확인합니다.
```bash
helm list --all-namespaces
```

### 제거 (Uninstall)
클러스터에서 릴리스와 관련된 모든 리소스를 삭제합니다.
```bash
helm uninstall my-release
```

## 5. OCP 에서 Helm 사용: OperatorHub vs Helm

OpenShift 에서 소프트웨어를 배포하는 방법은 크게 **OperatorHub** 와 **Helm** 으로 나뉩니다. 두 방식의 차이점과 선택 기준은 다음과 같습니다.

| 특징 | OperatorHub (OLM) | Helm |
| :--- | :--- | :--- |
| **관리 주체** | Red Hat 공식 지원 및 커뮤니티 | 오픈소스 커뮤니티 |
| **라이프사이클 관리** | OLM(Operator Lifecycle Manager) 이 자동 관리 | Helm 이 수동 또는 스크립트로 관리 |
| **업데이트** | 자동 업데이트 지원 (Subscription 기반) | 수동 upgrade 명령어 필요 |
| **설정 커스터마이징** | CRD (Custom Resource) 를 통해 제한적 | values.yaml 을 통해 유연한 커스터마이징 |
| **적합 시나리오** | 엔터프라이즈 표준, 자동화 요구사항이 높은 경우 | 빠른 프로토타이핑, 특정 도구 배포, 유연한 설정 필요 시 |
| **예시** | PostgreSQL Operator, Kafka Operator | Prometheus, Grafana, Jenkins (Helm Chart) |

**사용 시나리오 비교:**
*   **OperatorHub 를 선택할 때**: 애플리케이션의 장기적인 운영, 자동화된 백업/복구, 패치 관리, Red Hat 인증된 안정성을 원할 때 적합합니다.
*   **Helm 을 선택할 때**: 최신 버전의 도구를 빠르게 도입해야 하거나, Operator 가 존재하지 않는 오픈소스 도구 (예: 특정 버전의 Redis, 복잡한 CI/CD 파이프라인) 를 배포해야 할 때 적합합니다. 또한, `values.yaml` 을 통해 매우 세밀하게 설정을 제어해야 하는 경우 Helm 이 유리합니다.

## 6. values.yaml 커스터마이징: 환경별 설정 오버라이드

Helm 의 가장 강력한 기능 중 하나는 `values.yaml` 을 통해 배포 설정을 동적으로 제어하는 것입니다. OCP 환경에서는 개발 (dev), 통합 (stg), 운영 (prod) 환경마다 다른 설정 (이미지 태그, 리소스 할당량, 보안 설정 등) 이 필요합니다.

### 방법 1: --set 플래그를 사용하여 명령어 수준 오버라이드
가장 간단한 방법으로, 설치 시 직접 값을 덮어씁니다.
```bash
helm install my-app ./my-app-chart \
  --set image.tag=1.16.0 \
  --set replicaCount=3 \
  --set service.type=ClusterIP
```

### 방법 2: values 파일 로드
별도의 YAML 파일을 만들어 설정을 관리합니다.
```bash
helm install my-app ./my-app-chart -f values-dev.yaml
```

### 방법 3: OCP 의 ConfigMap 과 결합 (추천)
OCP 에서 Secrets 나 ConfigMap 을 활용하여 민감한 정보나 환경별 설정을 외부에서 관리할 수 있습니다.
```bash
helm install my-app ./my-app-chart \
  --set-file configMapPath=/path/to/config.yaml \
  --set secretKey=my-secret-value
```
또는 Helm 의 `--set-string` 등을 조합하여 환경 변수를 주입합니다.

**주의사항**: `--set` 과 `-f` 플래그는 **마지막으로 지정된 값이 우선**이 됩니다. 따라서 명령어 순서에 유의해야 합니다.

## 7. Helm Chart 작성: 간단한 Chart 만들기 예시

Helm Chart 를 직접 작성하여 학습해 보겠습니다. 다음 예시는 간단한 Nginx Deployment 와 Service 를 생성하는 Chart 입니다.

**1. Chart.yaml 작성**
```yaml
apiVersion: v2
name: my-nginx
description: A simple Helm chart for deploying Ngin
