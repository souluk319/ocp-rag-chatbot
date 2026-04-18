# Operator 운영 플레이북

## OpenShift Container Platform의 Operator 작업

이 문서에서는 OpenShift Container Platform에서 Operator를 사용하는 방법에 대해 설명합니다. 여기에는 클러스터 관리자를 위한 Operator 설치 및 관리 방법과 설치된 Operator에서 애플리케이션을 생성하는 방법에 대한 지침이 포함됩니다.

또한 Operator SDK를 사용하여 자체 Operator를 빌드하는 방법에 대한 지침이 포함되어 있습니다.

## 1장. Operator 개요

Operator는 OpenShift Container Platform의 가장 중요한 구성 요소 중 하나입니다. 컨트롤 플레인에서 서비스를 패키징, 배포 및 관리하는 데 선호되는 방법입니다. 또한 사용자가 실행하는 애플리케이션에 이점을 제공할 수 있습니다.

Operator는 Kubernetes API 및 및 OpenShift CLI()와 같은 CLI 툴과 통합됩니다. 애플리케이션을 모니터링하고, 상태 점검 수행, OTA(Over-the-Air) 업데이트를 관리하며 애플리케이션이 지정된 상태로 유지되도록 합니다.

```shell
kubectl
```

```shell
oc
```

Operator는 Kubernetes 네이티브 애플리케이션이 설치 및 구성과 같은 일반적인 Day 1 작업을 구현하고 자동화하도록 특별히 설계되었습니다. Operator는 자동 스케일링 또는 축소 및 백업 생성과 같은 2일차 작업을 자동화할 수도 있습니다. 이러한 모든 작업은 클러스터에서 실행되는 소프트웨어의 일부로 전달됩니다.

두 가지 모두 유사한 Operator 개념과 목표를 따르지만 OpenShift Container Platform의 Operator는 목적에 따라 두 가지 다른 시스템에서 관리합니다.

클러스터 Operator

CVO(Cluster Version Operator)에 의해 관리되고 클러스터 기능을 수행하기 위해 기본적으로 설치됩니다.

선택적 애드온 Operator

OLM(Operator Lifecycle Manager)에서 관리하며 사용자가 애플리케이션에서 실행할 수 있도록 할 수 있습니다. OLM 기반 Operator라고도 합니다.

### 1.1. 개발자의 경우

Operator 작성자는 OLM 기반 Operator에 대해 다음 개발 작업을 수행할 수 있습니다.

Operator를 설치하고 네임스페이스에 등록합니다.

웹 콘솔을 통해 설치된 Operator에서 애플리케이션을 생성합니다.

추가 리소스

Operator 개발자의 머신 삭제 라이프사이클 후크 예

### 1.2. 관리자의 경우

클러스터 관리자는 OLM 기반 Operator에 대해 다음 관리 작업을 수행할 수 있습니다.

사용자 정의 카탈로그를 관리합니다.

비 클러스터 관리자가 Operator를 설치할 수 있도록 허용합니다.

소프트웨어 카탈로그에서 Operator를 설치합니다.

Operator 상태를 확인합니다.

Operator 조건을 관리합니다.

설치된 Operator를 업그레이드합니다.

설치된 Operator를 삭제합니다.

프록시 지원을 구성합니다.

연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

Red Hat에서 제공하는 클러스터 Operator에 대한 자세한 내용은 Cluster Operators 참조를 참조하십시오.

### 1.3. 다음 단계

Operator란 무엇인가?

### 2.1. Operator란 무엇인가?

개념적으로 Operator 는 사람의 운영 지식을 소비자와 더 쉽게 공유할 수 있는 소프트웨어로 인코딩합니다.

Operator는 다른 소프트웨어를 실행하는 데 따르는 운영의 복잡성을 완화해주는 소프트웨어입니다. 이는 소프트웨어 벤더의 엔지니어링 팀의 확장 기능으로, Kubernetes 환경(예: OpenShift Container Platform)을 모니터링하고 현재 상태를 사용하여 실시간으로 의사 결정을 내립니다.

고급 Operator는 업그레이드를 원활하게 처리하고 오류에 자동으로 대응하며 시간을 절약하기 위해 소프트웨어 백업 프로세스를 생략하는 등의 바로 가기를 실행하지 않습니다.

Operator는 Kubernetes 애플리케이션을 패키징, 배포, 관리하는 메서드입니다.

Kubernetes 애플리케이션은 Kubernetes API 및 또는 툴링을 사용하여 Kubernetes API에 배포하고 관리하는 앱입니다. Kubernetes를 최대한 활용하기 위해서는 Kubernetes에서 실행되는 앱을 제공하고 관리하기 위해 확장할 응집력 있는 일련의 API가 필요합니다.

```shell
kubectl
```

```shell
oc
```

Operator는 Kubernetes에서 이러한 유형의 앱을 관리하는 런타임으로 생각할 수 있습니다.

#### 2.1.1. Operator를 사용하는 이유는 무엇입니까?

Operator는 다음과 같은 기능을 제공합니다.

반복된 설치 및 업그레이드.

모든 시스템 구성 요소에 대한 지속적인 상태 점검.

OpenShift 구성 요소 및 ISV 콘텐츠에 대한 OTA(Over-The-Air) 업데이트

필드 엔지니어의 지식을 캡슐화하여 한두 명이 아닌 모든 사용자에게 전파.

Kubernetes에 배포하는 이유는 무엇입니까?

Kubernetes, 더 나아가 OpenShift Container Platform에는 온프레미스 및 클라우드 공급자에 걸쳐 작동하는 복잡한 분산 시스템을 빌드하는 데 필요한 모든 기본 기능(보안 처리, 부하 분산, 서비스 검색, 자동 스케일링)이 포함됩니다.

Kubernetes API 및 툴링으로 앱을 관리하는 이유는 무엇입니까?

```shell
kubectl
```

이러한 API는 기능이 다양하고 모든 플랫폼에 대한 클라이언트가 있으며 클러스터의 액세스 제어/감사에 연결됩니다. Operator는 Kubernetes 확장 메커니즘인 CRD(사용자 정의 리소스 정의)를 사용하므로 사용자 정의 오브젝트(예: `MongoDB`)가 기본 제공되는 네이티브 Kubernetes 오브젝트처럼 보이고 작동합니다.

Operator는 서비스 브로커와 어떻게 다릅니까?

서비스 브로커는 앱의 프로그래밍 방식 검색 및 배포를 위한 단계입니다. 그러나 오래 실행되는 프로세스가 아니므로 업그레이드, 장애 조치 또는 스케일링과 같은 2일 차 작업을 실행할 수 없습니다.

튜닝할 수 있는 항목에 대한 사용자 정의 및 매개변수화는 설치 시 제공되지만 Operator는 클러스터의 현재 상태를 지속적으로 관찰합니다. 클러스터 외부 서비스는 서비스 브로커에 적합하지만 해당 서비스를 위한 Operator도 있습니다.

#### 2.1.2. Operator 프레임워크

Operator 프레임워크는 위에서 설명한 고객 경험을 제공하는 툴 및 기능 제품군입니다. 코드를 작성하는 데 그치지 않고 Operator를 테스트, 제공, 업데이트하는 것이 중요합니다. Operator 프레임워크 구성 요소는 이러한 문제를 해결하는 오픈 소스 툴로 구성됩니다.

Operator Lifecycle Manager

OLM(Operator Lifecycle Manager)은 클러스터에서 Operator의 설치, 업그레이드, RBAC(역할 기반 액세스 제어)를 제어합니다. OpenShift Container Platform 4.20에 기본적으로 배포됩니다.

Operator 레지스트리

Operator 레지스트리는 CSV(클러스터 서비스 버전) 및 CRD(사용자 정의 리소스 정의)를 클러스터에 생성하기 위해 저장하고 패키지 및 채널에 대한 Operator 메타데이터를 저장합니다. 이 Operator 카탈로그 데이터를 OLM에 제공하기 위해 Kubernetes 또는 OpenShift 클러스터에서 실행됩니다.

소프트웨어 카탈로그

소프트웨어 카탈로그는 클러스터 관리자가 클러스터에 설치할 Operator를 검색하고 선택할 수 있는 웹 콘솔입니다. OpenShift Container Platform에 기본적으로 배포됩니다.

이러한 툴은 구성 가능하도록 설계되어 있어 유용한 툴을 모두 사용할 수 있습니다.

#### 2.1.3. Operator 완성 모델

[FIGURE src="/playbooks/wiki-assets/full_rebuild/operators/operator-maturity-model.png" alt="Operator 완성 모델" kind="figure" diagram_type="image_figure"]
Operator 완성 모델
[/FIGURE]

_Source: `operators.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Operators-ko-KR/images/e38967efb4c184f997b0d177edfb868f/operator-maturity-model.png`_


Operator 내에 캡슐화된 관리 논리의 세분화 수준은 다를 수 있습니다. 이 논리는 일반적으로 Operator에서 표시하는 서비스 유형에 따라 크게 달라집니다.

그러나 대부분의 Operator에 포함될 수 있는 특정 기능 세트의 경우 캡슐화된 Operator 작업의 완성 정도를 일반화할 수 있습니다. 이를 위해 다음 Operator 완성 모델에서는 Operator의 일반적인 2일 차 작업에 대해 5단계의 완성도를 정의합니다.

그림 2.1. Operator 완성 모델

### 2.2. Operator 프레임워크 패키지 형식

이 가이드에서는 OpenShift Container Platform의 OLM(Operator Lifecycle Manager)에서 지원하는 Operator의 패키지 형식에 대해 간단히 설명합니다.

#### 2.2.1. 번들 형식

Operator의 번들 형식 은 Operator 프레임워크에서 도입한 패키지 형식입니다. 번들 형식 사양에서는 확장성을 개선하고 자체 카탈로그를 호스팅하는 업스트림 사용자를 더 효과적으로 지원하기 위해 Operator 메타데이터의 배포를 단순화합니다.

Operator 번들은 단일 버전의 Operator를 나타냅니다. 디스크상의 번들 매니페스트 는 컨테이너화되어 번들 이미지 (Kubernetes 매니페스트와 Operator 메타데이터를 저장하는 실행 불가능한 컨테이너 이미지)로 제공됩니다.

그런 다음 명령과 같은 기존 컨테이너 툴과 Quay와 같은 컨테이너 레지스트리를 사용하여 번들 이미지의 저장 및 배포를 관리합니다.

```shell
podman
```

```shell
docker
```

Operator 메타데이터에는 다음이 포함될 수 있습니다.

Operator 확인 정보(예: 이름 및 버전)

UI를 구동하는 추가 정보(예: 아이콘 및 일부 예제 CR(사용자 정의 리소스))

필요한 API 및 제공된 API.

관련 이미지.

Operator 레지스트리 데이터베이스에 매니페스트를 로드할 때 다음 요구 사항이 검증됩니다.

번들의 주석에 하나 이상의 채널이 정의되어 있어야 합니다.

모든 번들에 정확히 하나의 CSV(클러스터 서비스 버전)가 있습니다.

CSV에 CRD(사용자 정의 리소스 정의)가 포함된 경우 해당 CRD가 번들에 있어야 합니다.

#### 2.2.1.1. 매니페스트

번들 매니페스트는 Operator의 배포 및 RBAC 모델을 정의하는 Kubernetes 매니페스트 세트를 나타냅니다.

번들에는 디렉터리당 하나의 CSV와 일반적으로 `/manifests` 디렉터리에서 CSV의 고유 API를 정의하는 CRD가 포함됩니다.

```shell-session
etcd
├── manifests
│   ├── etcdcluster.crd.yaml
│   └── etcdoperator.clusterserviceversion.yaml
│   └── secret.yaml
│   └── configmap.yaml
└── metadata
    └── annotations.yaml
    └── dependencies.yaml
```

#### 2.2.1.1.1. 추가 지원 오브젝트

다음과 같은 오브젝트 유형도 번들의 `/manifests` 디렉터리에 선택적으로 포함될 수 있습니다.

지원되는 선택적 오브젝트 유형

`ClusterRole`

`ClusterRoleBinding`

`ConfigMap`

`ConsoleCLIDownload`

`ConsoleLink`

`ConsoleQuickStart`

`ConsoleYamlSample`

`PodDisruptionBudget`

`PriorityClass`

`PrometheusRule`

`Role`

`RoleBinding`

`Secret`

`서비스`

`ServiceAccount`

`ServiceMonitor`

`VerticalPodAutoscaler`

이러한 선택적 오브젝트가 번들에 포함된 경우 OLM(Operator Lifecycle Manager)은 번들에서 해당 오브젝트를 생성하고 CSV와 함께 해당 라이프사이클을 관리할 수 있습니다.

선택적 오브젝트의 라이프사이클

CSV가 삭제되면 OLM은 선택적 오브젝트를 삭제합니다.

CSV가 업그레이드되면 다음을 수행합니다.

선택적 오브젝트의 이름이 동일하면 OLM에서 해당 오브젝트를 대신 업데이트합니다.

버전 간 선택적 오브젝트의 이름이 변경된 경우 OLM은 해당 오브젝트를 삭제하고 다시 생성합니다.

#### 2.2.1.2. 주석

번들의 `/metadata` 디렉터리에는 `annotations.yaml` 파일도 포함되어 있습니다. 이 파일에서는 번들을 번들 인덱스에 추가하는 방법에 대한 형식 및 패키지 정보를 설명하는 데 도움이 되는 고급 집계 데이터를 정의합니다.

```yaml
annotations:
  operators.operatorframework.io.bundle.mediatype.v1: "registry+v1"
  operators.operatorframework.io.bundle.manifests.v1: "manifests/"
  operators.operatorframework.io.bundle.metadata.v1: "metadata/"
  operators.operatorframework.io.bundle.package.v1: "test-operator"
  operators.operatorframework.io.bundle.channels.v1: "beta,stable"
  operators.operatorframework.io.bundle.channel.default.v1: "stable"
```

1. Operator 번들의 미디어 유형 또는 형식입니다. `registry+v1` 형식은 CSV 및 관련 Kubernetes 오브젝트가 포함됨을 나타냅니다.

2. Operator 매니페스트가 포함된 디렉터리의 이미지 경로입니다. 이 라벨은 나중에 사용할 수 있도록 예약되어 있으며 현재 기본값은 `manifests/` 입니다. 값 `manifests.v1` 은 번들에 Operator 매니페스트가 포함되어 있음을 나타냅니다.

3. 번들에 대한 메타데이터 파일이 포함된 디렉터리의 이미지의 경로입니다. 이 라벨은 나중에 사용할 수 있도록 예약되어 있으며 현재 기본값은 `metadata/` 입니다. 값 `metadata.v1` 은 이 번들에 Operator 메타데이터가 있음을 나타냅니다.

4. 번들의 패키지 이름입니다.

5. Operator 레지스트리에 추가될 때 번들이 서브스크립션되는 채널 목록입니다.

6. 레지스트리에서 설치할 때 Operator를 서브스크립션해야 하는 기본 채널입니다.

참고

불일치하는 경우 이러한 주석을 사용하는 클러스터상의 Operator 레지스트리만 이 파일에 액세스할 수 있기 때문에 `annotations.yaml` 파일을 신뢰할 수 있습니다.

#### 2.2.1.3. 종속 항목

Operator의 종속 항목은 번들의 `metadata/` 폴더에 있는 `dependencies.yaml` 파일에 나열되어 있습니다. 이 파일은 선택 사항이며 현재는 명시적인 Operator 버전 종속 항목을 지정하는 데만 사용됩니다.

종속성 목록에는 종속성의 유형을 지정하기 위해 각 항목에 대한 `type` 필드가 포함되어 있습니다. 다음과 같은 유형의 Operator 종속 항목이 지원됩니다.

`olm.package`

이 유형은 특정 Operator 버전에 대한 종속성을 나타냅니다. 종속 정보에는 패키지 이름과 패키지 버전이 semver 형식으로 포함되어야 합니다. 예를 들어 `0.5.2` 와 같은 정확한 버전이나 `>0.5.1` 과 같은 버전 범위를 지정할 수 있습니다.

`olm.gvk`

이 유형을 사용하면 작성자는 CSV의 기존 CRD 및 API 기반 사용과 유사하게 GVK(그룹/버전/종류) 정보를 사용하여 종속성을 지정할 수 있습니다. 이 경로를 통해 Operator 작성자는 모든 종속 항목, API 또는 명시적 버전을 동일한 위치에 통합할 수 있습니다.

`olm.constraint`

이 유형은 임의의 Operator 속성에 대한 일반 제약 조건을 선언합니다.

다음 예제에서는 Prometheus Operator 및 etcd CRD에 대한 종속 항목을 지정합니다.

```yaml
dependencies:
  - type: olm.package
    value:
      packageName: prometheus
      version: ">0.27.0"
  - type: olm.gvk
    value:
      group: etcd.database.coreos.com
      kind: EtcdCluster
      version: v1beta2
```

추가 리소스

Operator Lifecycle Manager 종속성 확인

#### 2.2.1.4. opm CLI 정보

`opm` CLI 툴은 Operator 번들 형식과 함께 사용할 수 있도록 Operator 프레임워크에서 제공합니다. 이 툴을 사용하면 소프트웨어 리포지토리와 유사한 Operator 번들 목록에서 Operator 카탈로그를 생성하고 유지 관리할 수 있습니다. 결과적으로 컨테이너 레지스트리에 저장한 다음 클러스터에 설치할 수 있는 컨테이너 이미지가 생성됩니다.

카탈로그에는 컨테이너 이미지가 실행될 때 제공되는 포함된 API를 통해 쿼리할 수 있는 Operator 매니페스트 콘텐츠에 대한 포인터 데이터베이스가 포함되어 있습니다.

OpenShift Container Platform에서 OLM(Operator Lifecycle Manager)은 `CatalogSource` 오브젝트에서 정의한 카탈로그 소스의 이미지를 참조할 수 있으며 주기적으로 이미지를 폴링하여 클러스터에 설치된 Operator를 자주 업데이트할 수 있습니다.

`opm`

CLI 설치 단계는 CLI 툴 을 참조하십시오.

#### 2.2.2. 주요 사항

파일 기반 카탈로그 는 OLM(Operator Lifecycle Manager) 카탈로그 형식의 최신 버전입니다. 일반 텍스트 기반(JSON 또는 YAML)과 이전 SQLite 데이터베이스 형식의 선언적 구성 진화이며 완전히 이전 버전과 호환됩니다. 이 형식의 목표는 Operator 카탈로그 편집, 구성 가능성 및 확장성을 활성화하는 것입니다.

편집

파일 기반 카탈로그를 사용하면 카탈로그 내용과 상호 작용하는 사용자가 형식을 직접 변경하고 변경 사항이 유효한지 확인할 수 있습니다. 이 형식은 일반 텍스트 JSON 또는 YAML이므로 카탈로그 유지 관리자는 CLI와 같이 널리 알려진 지원되는 JSON 또는 YAML 툴을 사용하여 카탈로그 메타데이터를 쉽게 조작할 수 있습니다.

```shell
jq
```

이 편집 기능을 사용하면 다음과 같은 기능 및 사용자 정의 확장 기능을 사용할 수 있습니다.

기존 번들을 새 채널로 승격

패키지의 기본 채널 변경

업그레이드 경로 추가, 업데이트 및 제거를 위한 사용자 정의 알고리즘

호환성

파일 기반 카탈로그는 카탈로그 구성이 가능한 임의의 디렉터리 계층 구조에 저장됩니다. 예를 들어 별도의 파일 기반 카탈로그 디렉터리인 `catalogA` 및 `catalogB` 를 고려해 보십시오. 카탈로그 관리자는 새 디렉토리 `catalogC` 를 만들고 `catalogA` 및 `catalogB` 를 복사하여 새로 결합된 카탈로그를 만들 수 있습니다.

이 구성 가능성을 통해 분산된 카탈로그를 사용할 수 있습니다. 이 형식을 사용하면 Operator 작성자가 Operator별 카탈로그를 유지 관리할 수 있으며 유지 관리자가 개별 Operator 카탈로그로 구성된 카탈로그를 단순하게 빌드할 수 있습니다.

파일 기반 카탈로그는 하나의 카탈로그의 하위 집합을 추출하거나 두 개의 카탈로그를 조합하여 다른 여러 카탈로그를 결합하여 구성할 수 있습니다.

참고

패키지 내의 중복 패키지 및 중복 번들은 허용되지 않습니다. `opm validate` 명령은 중복이 발견되면 오류를 반환합니다.

Operator 작성자는 Operator, 해당 종속 항목 및 업그레이드 호환성에 가장 익숙하므로 자체 Operator별 카탈로그를 유지 관리하고 해당 콘텐츠를 직접 제어할 수 있습니다. Operator 작성자는 파일 기반 카탈로그를 사용하여 카탈로그에서 패키지를 빌드하고 유지 관리하는 작업을 소유합니다.

그러나 복합 카탈로그 유지 관리자만 카탈로그의 패키지를 큐레이션하고 카탈로그를 사용자에게 게시하는 작업만 소유합니다.

확장성

파일 기반 카탈로그 사양은 카탈로그의 하위 수준 형식입니다. 카탈로그 유지 관리자는 낮은 수준의 형식으로 직접 유지 관리할 수 있지만, 카탈로그 유지 관리자는 고유한 사용자 지정 툴링에서 원하는 수의 변경을 수행할 수 있는 확장 기능을 구축할 수 있습니다.

예를 들어 툴은 `(mode=semver)` 와 같은 고급 API를 업그레이드 경로의 하위 수준 파일 기반 카탈로그 형식으로 변환할 수 있습니다. 또는 카탈로그 유지 관리자는 특정 기준을 충족하는 번들에 새 속성을 추가하여 모든 번들 메타데이터를 사용자 지정해야 할 수 있습니다.

이러한 확장성을 통해 향후 OpenShift Container Platform 릴리스를 위해 하위 수준 API에서 추가 공식 툴을 개발할 수 있지만, 카탈로그 유지 관리자도 이러한 기능을 사용할 수 있다는 것이 가장 큰 장점입니다.

중요

OpenShift Container Platform 4.11부터 파일 기반 카탈로그 형식으로 기본 Red Hat 제공 Operator 카탈로그 릴리스입니다. 더 이상 사용되지 않는 SQLite 데이터베이스 형식으로 릴리스된 OpenShift Container Platform 4.6에 대한 기본 Red Hat 제공 Operator 카탈로그입니다.

SQLite 데이터베이스 형식과 관련된 `opm` 하위 명령, 플래그 및 기능은 더 이상 사용되지 않으며 향후 릴리스에서 제거됩니다. 이 기능은 계속 지원되며 더 이상 사용되지 않는 SQLite 데이터베이스 형식을 사용하는 카탈로그에 사용해야 합니다.

`opm index prune` 와 같은 SQLite 데이터베이스 형식을 사용하기 위한 `opm` 하위 명령 및 플래그는 파일 기반 카탈로그 형식에서는 작동하지 않습니다. 파일 기반 카탈로그 작업에 대한 자세한 내용은 oc-mirror 플러그인을 사용하여 사용자 정의 카탈로그 관리 및 연결이 끊긴 설치의 이미지 미러링 을 참조하십시오.

#### 2.2.2.1. 디렉토리 구조

디렉토리 기반 파일 시스템에서 파일 기반 카탈로그를 저장하고 로드할 수 있습니다. `opm` CLI는 루트 디렉토리로 이동하고 하위 디렉토리로 재귀하여 카탈로그를 로드합니다. CLI는 발견한 모든 파일을 로드 시도하여 오류가 발생하면 실패합니다.

비카탈로그 파일은 `.gitignore` 파일과 패턴 및 우선 순위에 대해 동일한 규칙이 있는 `.indexignore` 파일을 사용하여 무시할 수 있습니다.

```shell-session
# Ignore everything except non-object .json and .yaml files
**/*
!*.json
!*.yaml
**/objects/*.json
**/objects/*.yaml
```

카탈로그 유지 관리자는 원하는 레이아웃을 선택할 수 있는 유연성을 가지지만 각 패키지의 파일 기반 카탈로그 Blob을 별도의 하위 디렉터리에 저장하는 것이 좋습니다. 각 개별 파일은 JSON 또는 YAML일 수 있습니다. 카탈로그의 모든 파일에서 동일한 형식을 사용할 필요는 없습니다.

```shell-session
catalog
├── packageA
│   └── index.yaml
├── packageB
│   ├── .indexignore
│   ├── index.yaml
│   └── objects
│       └── packageB.v0.1.0.clusterserviceversion.yaml
└── packageC
    └── index.json
    └── deprecations.yaml
```

이 권장 구조에는 디렉터리 계층 구조의 각 하위 디렉터리가 자체 포함된 카탈로그이므로 카탈로그 구성, 검색 및 탐색 간단한 파일 시스템 작업이 가능합니다. 카탈로그는 상위 카탈로그의 루트 디렉터리에 복사하여 상위 카탈로그에 포함할 수도 있습니다.

#### 2.2.2.2. 스키마

파일 기반 카탈로그는 임의의 스키마로 확장할 수 있는 CUE 언어 사양 을 기반으로 하는 형식을 사용합니다. 다음 `_Meta` CUE 스키마는 모든 파일 기반 카탈로그 Blob이 준수해야 하는 형식을 정의합니다.

```plaintext
_Meta: {
  // schema is required and must be a non-empty string
  schema: string & !=""

  // package is optional, but if it's defined, it must be a non-empty string
  package?: string & !=""

  // properties is optional, but if it's defined, it must be a list of 0 or more properties
  properties?: [... #Property]
}

#Property: {
  // type is required
  type: string & !=""

  // value is required, and it must not be null
  value: !=null
}
```

참고

이 사양에 나열된 CUE 스키마는 완전한 것으로 간주되어서는 안 됩니다. `opm validate` 명령에는 CUE에서 간결하게 표현하기가 어렵거나 불가능한 추가 유효성 검사가 있습니다.

OLM(Operator Lifecycle Manager) 카탈로그에서는 현재 OLM의 기존 패키지 및 번들 개념에 해당하는 3개의 스키마 (`olm.package`, `olm.channel`, `olm.bundle`)를 사용합니다.

카탈로그의 각 Operator 패키지에는 정확히 하나의 `olm.package` blob, 하나 이상의 `olm.channel` blob, 하나 이상의 `olm.bundle` blob이 필요합니다.

참고

모든 `olm.*` 스키마는 OLM 정의 스키마용으로 예약됩니다. 사용자 지정 스키마는 소유한 도메인과 같이 고유한 접두사를 사용해야 합니다.

#### 2.2.2.2.1. olm.package 스키마

`olm.package` 스키마는 Operator에 대한 패키지 수준 메타데이터를 정의합니다. 이에는 이름, 설명, 기본 채널 및 아이콘이 포함됩니다.

```plaintext
#Package: {
  schema: "olm.package"

  // Package name
  name: string & !=""

  // A description of the package
  description?: string

  // The package's default channel
  defaultChannel: string & !=""

  // An optional icon
  icon?: {
    base64data: string
    mediatype:  string
  }
}
```

#### 2.2.2.2.2. olm.channel 스키마

`olm.channel` 스키마는 패키지 내 채널, 채널의 멤버인 번들 항목 및 해당 번들의 업그레이드 경로를 정의합니다.

번들 항목이 여러 `olm.channel` blob의 에지를 나타내는 경우 채널당 한 번만 표시될 수 있습니다.

항목의 값이 이 카탈로그 또는 `다른` 카탈로그에서 찾을 수 없는 다른 번들 이름을 참조하는 것은 유효합니다. 그러나 여러 헤드가 없는 채널과 같이 다른 모든 채널 불변성은 true를 유지해야 합니다.

```plaintext
#Channel: {
  schema: "olm.channel"
  package: string & !=""
  name: string & !=""
  entries: [...#ChannelEntry]
}

#ChannelEntry: {
  // name is required. It is the name of an `olm.bundle` that
  // is present in the channel.
  name: string & !=""

  // replaces is optional. It is the name of bundle that is replaced
  // by this entry. It does not have to be present in the entry list.
  replaces?: string & !=""

  // skips is optional. It is a list of bundle names that are skipped by
  // this entry. The skipped bundles do not have to be present in the
  // entry list.
  skips?: [...string & !=""]

  // skipRange is optional. It is the semver range of bundle versions
  // that are skipped by this entry.
  skipRange?: string & !=""
}
```

주의

`skipRange` 필드를 사용하는 경우 건너뛰는 Operator 버전이 업데이트 그래프에서 정리되며 `Subscription` 오브젝트의 `spec.startingCSV` 속성이 있는 사용자가 더 오래 설치할 수 있습니다.

`skipRange` 및 `replaces` 필드를 모두 사용하여 향후 설치를 위해 사용자가 이전에 설치한 버전을 사용할 수 있는 동안 Operator를 점진적으로 업데이트할 수 있습니다. `replaces` 필드가 해당 Operator 버전의 즉시 이전 버전을 가리키는지 확인합니다.

#### 2.2.2.2.3. olm.bundle 스키마

```plaintext
#Bundle: {
  schema: "olm.bundle"
  package: string & !=""
  name: string & !=""
  image: string & !=""
  properties: [...#Property]
  relatedImages?: [...#RelatedImage]
}

#Property: {
  // type is required
  type: string & !=""

  // value is required, and it must not be null
  value: !=null
}

#RelatedImage: {
  // image is the image reference
  image: string & !=""

  // name is an optional descriptive name for an image that
  // helps identify its purpose in the context of the bundle
  name?: string & !=""
}
```

#### 2.2.2.2.4. olm.deprecations 스키마

선택적 `olm.deprecations` 스키마는 카탈로그의 패키지, 번들 및 채널에 대한 사용 중단 정보를 정의합니다. Operator 작성자는 이 스키마를 사용하여 카탈로그에서 해당 Operator를 실행하는 사용자에게 지원 상태 및 권장 업그레이드 경로와 같은 Operator에 대한 관련 메시지를 제공할 수 있습니다.

이 스키마가 정의되면 OpenShift Container Platform 웹 콘솔은 소프트웨어 카탈로그의 설치 전 및 설치 후 페이지에서 사용자 정의 사용 중단 메시지를 포함하여 Operator의 영향을 받는 요소에 대한 경고 배지를 표시합니다.

`olm.deprecations` 스키마 항목에는 사용 중단 범위를 나타내는 다음 `참조` 유형 중 하나 이상이 포함되어 있습니다. Operator가 설치되면 지정된 메시지를 관련 `Subscription` 오브젝트에서 상태 조건으로 볼 수 있습니다.

| 유형 | 범위 | 상태 조건 |
| --- | --- | --- |
| `olm.package` | 전체 패키지를 나타냅니다. | `PackageDeprecated` |
| `olm.channel` | 하나의 채널을 나타냅니다. | `ChannelDeprecated` |
| `olm.bundle` | 하나의 번들 버전을 나타냅니다. | `BundleDeprecated` |

각 `참조` 유형에는 다음 예에 설명된 대로 자체 요구 사항이 있습니다.

```yaml
schema: olm.deprecations
package: my-operator
entries:
  - reference:
      schema: olm.package
    message: |
    The 'my-operator' package is end of life. Please use the
    'my-operator-new' package for support.
  - reference:
      schema: olm.channel
      name: alpha
    message: |
    The 'alpha' channel is no longer supported. Please switch to the
    'stable' channel.
  - reference:
      schema: olm.bundle
      name: my-operator.v1.68.0
    message: |
    my-operator.v1.68.0 is deprecated. Uninstall my-operator.v1.68.0 and
    install my-operator.v1.72.0 for support.
```

1. 각 사용 중단 스키마에는 `패키지` 값이 있어야 하며 해당 패키지 참조는 카탈로그 전체에서 고유해야 합니다. 연결된 `이름` 필드가 없어야 합니다.

2. `olm.package` 스키마는 스키마의 앞부분에서 정의한 `package` 필드에 의해 결정되므로 `name` 필드를 포함하지 않아야 합니다.

3. 모든 `참조` 유형에 관계없이 모든 `message` 필드는길이가 0이 아닌 불투명한 텍스트 블롭(opaque text blob)으로 표현되어야 합니다.

4. `olm.channel` 스키마의 `name` 필드가 필요합니다.

5. `olm.bundle` 스키마의 `name` 필드가 필요합니다.

참고

사용 중단 기능은 중복 사용 중단(예: 패키지 대 채널 대 번들)을 고려하지 않습니다.

Operator 작성자는 `olm.deprecations` 스키마 항목을 패키지의 `index.yaml` 파일과 동일한 디렉터리에 `deprecations.yaml` 파일로 저장할 수 있습니다.

```shell-session
my-catalog
└── my-operator
    ├── index.yaml
    └── deprecations.yaml
```

추가 리소스

파일 기반 카탈로그 이미지 업데이트 또는 필터링

#### 2.2.2.3. 속성

속성은 파일 기반 카탈로그 스키마에 연결할 수 있는 임의 메타데이터입니다. `type` 필드는 `value` 필드의 의미 및 구문 의미를 효과적으로 지정하는 문자열입니다. 이 값은 임의의 JSON 또는 YAML일 수 있습니다.

OLM은 예약된 `olm.*` 접두사를 사용하여 몇 가지 속성 유형을 다시 정의합니다.

#### 2.2.2.3.1. olm.package 속성

`olm.package` 속성은 패키지 이름과 버전을 정의합니다. 이는 번들의 필수 속성이며, 이러한 속성 중 정확히 하나가 있어야 합니다. `packageName` 필드는 번들의 최상위 `package` 필드와 일치해야 하며 `version` 필드는 유효한 의미 체계 버전이어야 합니다.

```plaintext
#PropertyPackage: {
  type: "olm.package"
  value: {
    packageName: string & !=""
    version: string & !=""
  }
}
```

#### 2.2.2.3.2. olm.gvk 속성

`olm.gvk` 속성은 이 번들에서 제공하는 Kubernetes API의 GVK(그룹/버전/종류)를 정의합니다. 이 속성은 OLM에서 이 속성이 포함된 번들을 필수 API와 동일한 GVK를 나열하는 다른 번들의 종속성으로 확인하는 데 사용됩니다. GVK는 Kubernetes GVK 검증을 준수해야 합니다.

```plaintext
#PropertyGVK: {
  type: "olm.gvk"
  value: {
    group: string & !=""
    version: string & !=""
    kind: string & !=""
  }
}
```

#### 2.2.2.3.3. olm.package.required

`olm.package.required` 속성은 이 번들에 필요한 다른 패키지의 패키지 이름 및 버전 범위를 정의합니다. 번들 목록이 필요한 모든 패키지 속성에 대해 OLM은 나열된 패키지 및 필수 버전 범위에 대한 클러스터에 Operator가 설치되어 있는지 확인합니다. `versionRange` 필드는 유효한 의미 버전(semver) 범위여야 합니다.

```plaintext
#PropertyPackageRequired: {
  type: "olm.package.required"
  value: {
    packageName: string & !=""
    versionRange: string & !=""
  }
}
```

#### 2.2.2.3.4. olm.gvk.required

`olm.gvk.required` 속성은 이 번들에 필요한 Kubernetes API의 GVK(그룹/버전/종류)를 정의합니다. 번들 목록이 필요한 모든 GVK 속성에 대해 OLM은 이를 제공하는 클러스터에 Operator가 설치되어 있는지 확인합니다. GVK는 Kubernetes GVK 검증을 준수해야 합니다.

```shell-session
#PropertyGVKRequired: {
  type: "olm.gvk.required"
  value: {
    group: string & !=""
    version: string & !=""
    kind: string & !=""
  }
}
```

#### 2.2.2.4. 카탈로그의 예

파일 기반 카탈로그를 사용하면 카탈로그 유지 관리자가 Operator 큐레이션 및 호환성에 중점을 둘 수 있습니다. Operator 작성자는 Operator에 대한 Operator별 카탈로그를 이미 생성했기 때문에 카탈로그 유지 관리자는 각 Operator 카탈로그를 카탈로그의 루트 디렉터리의 하위 디렉터리에 렌더링하여 카탈로그를 빌드할 수 있습니다.

파일 기반 카탈로그를 구축하는 방법은 여러 가지가 있습니다. 다음 단계에서는 간단한 접근 방식을 간략하게 설명합니다.

카탈로그의 각 Operator에 대한 이미지 참조가 포함된 카탈로그의 단일 구성 파일을 유지 관리합니다.

```yaml
name: community-operators
repo: quay.io/community-operators/catalog
tag: latest
references:
- name: etcd-operator
  image: quay.io/etcd-operator/index@sha256:5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03
- name: prometheus-operator
  image: quay.io/prometheus-operator/index@sha256:e258d248fda94c63753607f7c4494ee0fcbe92f1a76bfdac795c9d84101eb317
```

구성 파일을 구문 분석하고 참조에서 새 카탈로그를 생성하는 스크립트를 실행합니다.

```plaintext
name=$(yq eval '.name' catalog.yaml)
mkdir "$name"
yq eval '.name + "/" + .references[].name' catalog.yaml | xargs mkdir
for l in $(yq e '.name as $catalog | .references[] | .image + "|" + $catalog + "/" + .name + "/index.yaml"' catalog.yaml); do
  image=$(echo $l | cut -d'|' -f1)
  file=$(echo $l | cut -d'|' -f2)
  opm render "$image" > "$file"
done
opm generate dockerfile "$name"
indexImage=$(yq eval '.repo + ":" + .tag' catalog.yaml)
docker build -t "$indexImage" -f "$name.Dockerfile" .
docker push "$indexImage"
```

#### 2.2.2.5. 지침

파일 기반 카탈로그를 유지 관리할 때 다음 지침을 고려하십시오.

#### 2.2.2.5.1. 변경할 수 없는 번들

OLM(Operator Lifecycle Manager)의 일반적인 지침은 번들 이미지 및 해당 메타데이터를 변경할 수 없음으로 간주해야 한다는 것입니다.

손상된 번들이 카탈로그로 푸시된 경우 사용자 중 한 명이 해당 번들로 업그레이드되었다고 가정해야 합니다. 이러한 가정에 따라 손상된 번들이 설치된 사용자가 업그레이드를 수신할 수 있도록 손상된 번들에서 업그레이드 경로를 사용하여 다른 번들을 릴리스해야 합니다. 해당 번들의 콘텐츠가 카탈로그에서 업데이트되는 경우 OLM은 설치된 번들을 다시 설치하지 않습니다.

그러나 카탈로그 메타데이터의 변경이 권장되는 몇 가지 사례가 있습니다.

채널 승격: 번들을 이미 릴리스하고 나중에 다른 채널에 추가할 것을 결정한 경우, 다른 `olm.channel` blob에 번들에 대한 항목을 추가할 수 있습니다.

새로운 업그레이드 경로: 새로운 `1.2.z` 번들 버전 (예: `1.2.4`)을 릴리스했지만 `1.3.0` 이 이미 릴리스된 경우 `1.3.0` 의 카탈로그 메타데이터를 업데이트하여 `1.2.4` 를 건너뛸 수 있습니다.

#### 2.2.2.5.2. 소스 제어

카탈로그 메타데이터는 소스 제어에 저장되고 정보 소스로 처리되어야 합니다. 카탈로그 이미지 업데이트에는 다음 단계가 포함되어야 합니다.

소스 제어 카탈로그 디렉터리를 새 커밋으로 업데이트합니다.

카탈로그 이미지를 빌드하고 내보냅니다. 사용자가 사용 가능하게 되면 카탈로그 업데이트를 수신할 수 있도록 `:latest` 또는 `:<target_cluster_version>` 과 같은 일관된 태그 지정 용어를 사용합니다.

#### 2.2.2.6. CLI 사용

`opm` CLI를 사용하여 파일 기반 카탈로그를 생성하는 방법에 대한 자세한 내용은 사용자 정의 카탈로그 관리를 참조하십시오.

파일 기반 카탈로그 관리와 관련된 `opm` CLI 명령에 대한 참조 문서는 CLI 툴 을 참조하십시오.

#### 2.2.2.7. 자동화

Operator 작성자 및 카탈로그 유지 관리자는 CI/CD 워크플로를 사용하여 카탈로그 유지 관리를 자동화하는 것이 좋습니다. 카탈로그 유지 관리자는 다음 작업을 수행하도록 GitOps 자동화를 빌드하여 이 작업을 추가로 개선할 수 있습니다.

예를 들어 패키지의 이미지 참조를 업데이트하여 해당 PR(pull request) 작성자가 요청된 변경을 수행할 수 있는지 확인합니다.

카탈로그 업데이트가 `opm validate` 명령을 전달하는지 확인합니다.

업데이트된 번들 또는 카탈로그 이미지 참조가 있는지, 카탈로그 이미지가 클러스터에서 성공적으로 실행되며 해당 패키지의 Operator가 성공적으로 설치될 수 있는지 확인합니다.

이전 검사를 통과하는 PR을 자동으로 병합합니다.

카탈로그 이미지를 자동으로 다시 빌드하고 다시 게시합니다.

### 2.3. Operator 프레임워크 일반 용어집

이 주제에서는 OLM(Operator Lifecycle Manager)을 포함하여 Operator 프레임워크와 관련된 일반 용어집을 제공합니다.

#### 2.3.1. 번들

번들 형식에서 번들 은 Operator CSV, 매니페스트, 메타데이터로 이루어진 컬렉션입니다. 이러한 구성 요소가 모여 클러스터에 설치할 수 있는 고유한 버전의 Operator를 형성합니다.

#### 2.3.2. 번들 이미지

번들 형식에서 번들 이미지 는 Operator 매니페스트에서 빌드하고 하나의 번들을 포함하는 컨테이너 이미지입니다. 번들 이미지는 Quay.io 또는 DockerHub와 같은 OCI(Open Container Initiative) 사양 컨테이너 레지스트리에서 저장 및 배포합니다.

#### 2.3.3. 카탈로그 소스

카탈로그 소스 는 OLM에서 Operator 및 해당 종속 항목을 검색하고 설치하기 위해 쿼리할 수 있는 메타데이터 저장소를 나타냅니다.

#### 2.3.4. 채널

채널 은 Operator의 업데이트 스트림을 정의하고 구독자에게 업데이트를 배포하는 데 사용됩니다. 헤드는 해당 채널의 최신 버전을 가리킵니다. 예를 들어 `stable` 채널에는 Operator의 모든 안정적인 버전이 가장 오래된 것부터 최신 순으로 정렬되어 있습니다.

Operator에는 여러 개의 채널이 있을 수 있으며 특정 채널에 대한 서브스크립션 바인딩에서는 해당 채널의 업데이트만 찾습니다.

#### 2.3.5. 채널 헤드

채널 헤드 는 알려진 특정 채널의 최신 업데이트를 나타냅니다.

#### 2.3.6. 클러스터 서비스 버전

CSV(클러스터 서비스 버전) 는 Operator 메타데이터에서 생성하는 YAML 매니페스트로, OLM이 클러스터에서 Operator를 실행하는 것을 지원합니다. 로고, 설명, 버전과 같은 정보로 사용자 인터페이스를 채우는 데 사용되는 Operator 컨테이너 이미지와 함께 제공되는 메타데이터입니다.

또한 필요한 RBAC 규칙 및 관리하거나 사용하는 CR(사용자 정의 리소스)과 같이 Operator를 실행하는 데 필요한 기술 정보의 소스이기도 합니다.

#### 2.3.7. 종속성

Operator는 클러스터에 있는 다른 Operator에 종속 되어 있을 수 있습니다. 예를 들어 Vault Operator는 데이터 지속성 계층과 관련하여 etcd Operator에 종속됩니다.

OLM은 설치 단계 동안 지정된 모든 버전의 Operator 및 CRD가 클러스터에 설치되도록 하여 종속 항목을 해결합니다. 이러한 종속성은 필수 CRD API를 충족하고 패키지 또는 번들과 관련이 없는 카탈로그에서 Operator를 찾아 설치함으로써 해결할 수 있습니다.

#### 2.3.8. 확장

클러스터 관리자는 확장 기능을 통해 OpenShift Container Platform 클러스터에서 사용자의 기능을 확장할 수 있습니다. 확장 기능은 OLM(Operator Lifecycle Manager) v1에서 관리합니다.

`ClusterExtension` API는 사용자용 API를 단일 오브젝트로 통합하여 `registry+v1` 번들 형식을 통해 Operator를 포함하는 설치된 확장 기능을 간소화합니다. 관리자와 SRE는 API를 사용하여 GitOps 원칙을 사용하여 프로세스를 자동화하고 원하는 상태를 정의할 수 있습니다.

#### 2.3.9. 인덱스 이미지

번들 형식에서 인덱스 이미지 는 모든 버전의 CSV 및 CRD를 포함하여 Operator 번들에 대한 정보를 포함하는 데이터베이스 이미지(데이터베이스 스냅샷)를 나타냅니다. 이 인덱스는 클러스터에서 Operator 기록을 호스팅하고 `opm` CLI 툴을 사용하여 Operator를 추가하거나 제거하는 방식으로 유지 관리할 수 있습니다.

#### 2.3.10. 설치 계획

설치 계획 은 CSV를 자동으로 설치하거나 업그레이드하기 위해 생성하는 계산된 리소스 목록입니다.

#### 2.3.11. 멀티 테넌시

OpenShift Container Platform의 테넌트 는 배포된 워크로드 세트(일반적으로 네임스페이스 또는 프로젝트로 표시되는)에 대한 공통 액세스 및 권한을 공유하는 사용자 또는 사용자 그룹입니다. 테넌트를 사용하여 다른 그룹 또는 팀 간에 격리 수준을 제공할 수 있습니다.

여러 사용자 또는 그룹에서 클러스터를 공유하는 경우 다중 테넌트 클러스터로 간주됩니다.

#### 2.3.12. Operator

Operator는 Kubernetes 애플리케이션을 패키징, 배포 및 관리하는 방법입니다. Kubernetes 애플리케이션은 Kubernetes API 및 또는 툴링을 사용하여 Kubernetes API에 배포하고 관리하는 앱입니다.

```shell
kubectl
```

```shell
oc
```

OLM(Operator Lifecycle Manager) v1에서 `ClusterExtension` API는 `레지스트리+v1` 번들 형식을 통해 Operator를 포함하는 설치된 확장 확장의 관리를 간소화합니다.

#### 2.3.13. Operator group

Operator group 은 동일한 네임스페이스에 배포된 모든 Operator를 `OperatorGroup` 오브젝트로 구성하여 네임스페이스 목록 또는 클러스터 수준에서 CR을 조사합니다.

#### 2.3.14. 패키지

번들 형식에서 패키지 는 각 버전과 함께 Operator의 모든 릴리스 내역을 포함하는 디렉터리입니다. 릴리스된 Operator 버전은 CRD와 함께 CSV 매니페스트에 설명되어 있습니다.

#### 2.3.15. 레지스트리

레지스트리 는 각각 모든 채널의 최신 버전 및 이전 버전이 모두 포함된 Operator의 번들 이미지를 저장하는 데이터베이스입니다.

#### 2.3.16. Subscription

서브스크립션 은 패키지의 채널을 추적하여 CSV를 최신 상태로 유지합니다.

#### 2.3.17. 업데이트 그래프

업데이트 그래프 는 패키지된 다른 소프트웨어의 업데이트 그래프와 유사하게 CSV 버전을 함께 연결합니다. Operator를 순서대로 설치하거나 특정 버전을 건너뛸 수 있습니다. 업데이트 그래프는 최신 버전이 추가됨에 따라 앞부분에서만 증가할 것으로 예상됩니다.

update edges 또는 update paths 라고도 합니다.

#### 2.4.1. Operator Lifecycle Manager 개념 및 리소스

이 가이드에서는 OpenShift Container Platform에서 OLM(Operator Lifecycle Manager)을 구동하는 개념에 대한 개요를 제공합니다.

#### 2.4.1.1. OLM(Operator Lifecycle Manager) Classic이란 무엇입니까?

[FIGURE src="/playbooks/wiki-assets/full_rebuild/operators/olm-workflow.png" alt="olm 워크플로" kind="diagram" diagram_type="semantic_diagram"]
olm 워크플로
[/FIGURE]

_Source: `operators.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Operators-ko-KR/images/c8a00bac5df42a702ff1b826333610d0/olm-workflow.png`_


OLM(Operator Lifecycle Manager) Classic은 사용자가 OpenShift Container Platform 클러스터에서 실행되는 Kubernetes 네이티브 애플리케이션(Operator) 및 관련 서비스의 라이프사이클을 설치, 업데이트 및 관리하는 데 도움이 됩니다.

Operator 프레임워크 의 일부로, 효과적이고 자동화되었으며 확장 가능한 방식으로 Operator를 관리하도록 설계된 오픈 소스 툴킷입니다.

그림 2.2. OLM (Classic) 워크플로

OLM은 OpenShift Container Platform 4.20에서 기본적으로 실행되므로 클러스터 관리자가 클러스터에서 실행되는 Operator를 설치, 업그레이드 및 액세스 권한을 부여할 수 있습니다.

OpenShift Container Platform 웹 콘솔은 클러스터 관리자가 Operator를 설치할 수 있는 관리 화면을 제공하고, 클러스터에 제공되는 Operator 카탈로그를 사용할 수 있는 액세스 권한을 특정 프로젝트에 부여합니다.

개발자의 경우 분야별 전문가가 아니어도 셀프서비스 경험을 통해 데이터베이스, 모니터링, 빅 데이터 서비스의 인스턴스를 프로비저닝하고 구성할 수 있습니다. Operator에서 해당 지식을 제공하기 때문입니다.

#### 2.4.1.2. OLM 리소스

다음 CRD(사용자 정의 리소스 정의)는 OLM(Operator Lifecycle Manager)에서 정의하고 관리합니다.

| 리소스 | 짧은 이름 | 설명 |
| --- | --- | --- |
| `ClusterServiceVersion` (CSV) | `csv` | 애플리케이션 메타데이터입니다. 예를 들면 이름, 버전, 아이콘, 필수 리소스입니다. |
| `CatalogSource` | `catsrc` | 애플리케이션을 정의하는 CSV, CRD, 패키지의 리포지토리입니다. |
| `서브스크립션` | `sub` | 패키지의 채널을 추적하여 CSV를 최신 상태로 유지합니다. |
| `InstallPlan` | `ip` | CSV를 자동으로 설치하거나 업그레이드하기 위해 생성하는 계산된 리소스 목록입니다. |
| `OperatorGroup` | `og` | 동일한 네임스페이스에 배포된 모든 Operator를 `OperatorGroup` 오브젝트로 구성하여 네임스페이스 목록 또는 클러스터 수준에서 CR(사용자 정의 리소스)을 조사합니다. |
| `OperatorConditions` | - | OLM과 OLM에서 관리하는 Operator 간 통신 채널을 생성합니다. Operator는 복잡한 상태를 OLM에 보고하기 위해 `Status.Conditions` 어레이에 작성할 수 있습니다. |

#### 2.4.1.2.1. 클러스터 서비스 버전

CSV(클러스터 서비스 버전)는 OpenShift Container Platform 클러스터에서 실행 중인 특정 버전의 Operator를 나타냅니다. 클러스터에서 Operator를 실행할 때 OLM(Operator Lifecycle Manager)을 지원하는 Operator 메타데이터에서 생성한 YAML 매니페스트입니다.

이러한 Operator 관련 메타데이터는 OLM이 클러스터에서 Operator가 계속 안전하게 실행되도록 유지하고 새 버전의 Operator가 게시되면 업데이트 적용 방법에 대한 정보를 제공하는 데 필요합니다. 이는 기존 운영 체제의 패키징 소프트웨어와 유사합니다. OLM 패키징 단계를 `rpm`, `deb` 또는 `apk` 번들을 생성하는 단계로 고려해 보십시오.

CSV에는 Operator 컨테이너 이미지와 함께 제공되는 메타데이터가 포함되며 이러한 데이터는 이름, 버전, 설명, 라벨, 리포지토리 링크, 로고와 같은 정보로 사용자 인터페이스를 채우는 데 사용됩니다.

CSV는 Operator를 실행하는 데 필요한 기술 정보의 소스이기도 합니다(예: RBAC 규칙, 클러스터 요구 사항, 설치 전략을 관리하고 사용하는 CR(사용자 정의 리소스)). 이 정보는 OLM에 필요한 리소스를 생성하고 Operator를 배포로 설정하는 방법을 지정합니다.

#### 2.4.1.2.2. 카탈로그 소스

카탈로그 소스 는 일반적으로 컨테이너 레지스트리에 저장된 인덱스 이미지 를 참조하여 메타데이터 저장소를 나타냅니다. OLM(Operator Lifecycle Manager)은 카탈로그 소스를 쿼리하여 Operator 및 해당 종속성을 검색하고 설치합니다.

OpenShift Container Platform 웹 콘솔의 소프트웨어 카탈로그에는 카탈로그 소스에서 제공하는 Operator도 표시됩니다.

작은 정보

클러스터 관리자는 웹 콘솔의 관리 → 클러스터 설정 → 구성 → OperatorHub 페이지를 사용하여 클러스터에서 활성화된 카탈로그 소스에서 제공하는 전체 Operator 목록을 볼 수 있습니다.

`CatalogSource` 오브젝트의 `spec` 은 Pod를 구성하는 방법 또는 Operator Registry gRPC API를 제공하는 서비스와 통신하는 방법을 나타냅니다.

```yaml
﻿apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  generation: 1
  name: example-catalog
  namespace: openshift-marketplace
  annotations:
    olm.catalogImageTemplate:
      "quay.io/example-org/example-catalog:v{kube_major_version}.{kube_minor_version}.{kube_patch_version}"
spec:
  displayName: Example Catalog
  image: quay.io/example-org/example-catalog:v1
  priority: -400
  publisher: Example Org
  sourceType: grpc
  grpcPodConfig:
    securityContextConfig: <security_mode>
    nodeSelector:
      custom_label: <label>
    priorityClassName: system-cluster-critical
    tolerations:
      - key: "key1"
        operator: "Equal"
        value: "value1"
        effect: "NoSchedule"
  updateStrategy:
    registryPoll:
      interval: 30m0s
status:
  connectionState:
    address: example-catalog.openshift-marketplace.svc:50051
    lastConnect: 2021-08-26T18:14:31Z
    lastObservedState: READY
  latestImageRegistryPoll: 2021-08-26T18:46:25Z
  registryService:
    createdAt: 2021-08-26T16:16:37Z
    port: 50051
    protocol: grpc
    serviceName: example-catalog
    serviceNamespace: openshift-marketplace
```

1. `CatalogSource` 오브젝트의 이름입니다. 이 값은 요청된 네임스페이스에 생성된 관련 Pod의 이름으로도 사용됩니다.

2. 카탈로그를 생성할 네임스페이스입니다. 카탈로그를 모든 네임스페이스에서 클러스터 전체로 사용하려면 이 값을 `openshift-marketplace` 로 설정합니다.

기본 Red Hat 제공 카탈로그 소스에서도 `openshift-marketplace` 네임스페이스를 사용합니다. 그러지 않으면 해당 네임스페이스에서만 Operator를 사용할 수 있도록 값을 특정 네임스페이스로 설정합니다.

3. 선택 사항: 클러스터 업그레이드를 통해 Operator 설치가 지원되지 않거나 지속적인 업데이트 경로가 없는 경우 클러스터 업그레이드의 일부로 Operator 카탈로그의 인덱스 이미지 버전을 자동으로 변경할 수 있습니다.

`olm.catalogImageTemplate` 주석을 인덱스 이미지 이름으로 설정하고 이미지 태그의 템플릿을 구성할 때 표시된 대로 하나 이상의 Kubernetes 클러스터 버전 변수를 사용합니다. 이 주석은 런타임 시 `spec.image` 필드를 덮어씁니다. 자세한 내용은 "사용자 지정 카탈로그 소스의 이미지 템플릿" 섹션을 참조하십시오.

4. 웹 콘솔 및 CLI에 있는 카탈로그의 표시 이름입니다.

5. 카탈로그의 인덱스 이미지입니다. 선택적으로 런타임 시 pull 사양을 설정하는 `olm.catalogImageTemplate` 주석을 사용할 때 생략할 수 있습니다.

6. 카탈로그 소스의 가중치입니다. OLM은 종속성 확인 중에 가중치를 사용하여 우선순위를 지정합니다. 가중치가 높을수록 가중치가 낮은 카탈로그보다 카탈로그가 선호됨을 나타냅니다.

7. 소스 유형에는 다음이 포함됩니다.

`image` 참조가 있는 `grpc`: OLM이 이미지를 가져온 후 Pod를 실행합니다. Pod는 규격 API를 제공할 것으로 예상됩니다.

`address` 필드가 있는 `grpc`: OLM이 지정된 주소에서 gRPC API에 연결을 시도합니다. 대부분의 경우 사용해서는 안 됩니다.

`ConfigMap`: OLM은 구성 맵 데이터를 구문 분석하고 이에 대해 gRPC API를 제공할 수 있는 Pod를 실행합니다.

8. `legacy` 또는 `restricted` 를 지정합니다. 필드가 설정되지 않은 경우 기본값은 `legacy` 입니다. 향후 OpenShift Container Platform 릴리스에서는 기본값이 `제한` 될 예정입니다. `제한된` 권한으로 카탈로그를 실행할 수 없는 경우 이 필드를 기존으로 수동으로 설정하는 것이 `좋습니다`.

9. 선택 사항: `grpc` 유형 카탈로그 소스의 경우 정의된 경우 `spec.image` 의 콘텐츠를 제공하는 Pod의 기본 노드 선택기를 덮어씁니다.

10. 선택 사항: `grpc` 유형 카탈로그 소스의 경우 정의된 경우 `spec.image` 의 콘텐츠를 제공하는 Pod의 기본 우선순위 클래스 이름을 덮어씁니다. Kubernetes는 기본적으로 `system-cluster-critical` 및 `system-node-critical` 우선순위 클래스를 제공합니다.

필드를 empty(`""`)로 설정하면 Pod에 기본 우선순위가 할당됩니다. 다른 우선순위 클래스를 수동으로 정의할 수 있습니다.

11. 선택 사항: `grpc` 유형 카탈로그 소스의 경우 정의된 경우 `spec.image` 의 콘텐츠를 제공하는 Pod의 기본 허용 오차를 덮어씁니다.

12. 지정된 간격으로 새 버전을 자동으로 확인하여 최신 상태를 유지합니다.

13. 카탈로그 연결의 마지막으로 관찰된 상태입니다. 예를 들면 다음과 같습니다.

`READY`: 성공적으로 연결되었습니다.

`CONNECTING`: 계속 연결을 시도합니다.

`TRANSIENT_FAILURE`: 연결을 시도하는 동안 시간 초과와 같은 일시적인 문제가 발생했습니다. 상태는 결국 `CONNECTING` 으로 다시 전환되고 다시 연결 시도합니다.

자세한 내용은 gRPC 문서의 연결 상태 를 참조하십시오.

14. 카탈로그 이미지를 저장하는 컨테이너 레지스트리가 폴링되어 이미지가 최신 상태인지 확인할 수 있는 마지막 시간입니다.

15. 카탈로그의 Operator 레지스트리 서비스의 상태 정보입니다.

서브스크립션의 `CatalogSource` 오브젝트 `name` 을 참조하면 요청된 Operator를 찾기 위해 검색할 위치를 OLM에 지시합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: example-operator
  namespace: example-namespace
spec:
  channel: stable
  name: example-operator
  source: example-catalog
  sourceNamespace: openshift-marketplace
```

추가 리소스

소프트웨어 카탈로그 이해

Red Hat 제공 Operator 카탈로그

클러스터에 카탈로그 소스 추가

카탈로그 우선순위

CLI를 사용하여 Operator 카탈로그 소스 상태 보기

Pod 보안 허용 이해 및 관리

카탈로그 소스 Pod 예약

#### 2.4.1.2.2.1. 사용자 정의 카탈로그 소스의 이미지 템플릿

기본 클러스터와의 Operator 호환성은 다양한 방법으로 카탈로그 소스로 표시할 수 있습니다. 기본 Red Hat 제공 카탈로그 소스에 사용되는 한 가지 방법은 특정 플랫폼 릴리스(예: OpenShift Container Platform 4.20)에 대해 특별히 생성된 인덱스 이미지의 이미지 태그를 식별하는 것입니다.

클러스터 업그레이드 중에 기본 Red Hat 제공 카탈로그 소스의 인덱스 이미지 태그는 CVO(Cluster Version Operator)에서 자동으로 업데이트하여 OLM(Operator Lifecycle Manager)이 업데이트된 버전의 카탈로그를 가져옵니다.

예를 들어 OpenShift Container Platform 4.19에서 4.20으로 업그레이드하는 동안 `redhat-operators` 카탈로그의 `CatalogSource` 오브젝트의 `spec.image` 필드가 다음과 같이 업데이트됩니다.

```shell-session
registry.redhat.io/redhat/redhat-operator-index:v4.20
```

다음으로 변경합니다.

```shell-session
registry.redhat.io/redhat/redhat-operator-index:v4.20
```

그러나 CVO는 사용자 정의 카탈로그의 이미지 태그를 자동으로 업데이트하지 않습니다. 클러스터 업그레이드 후 사용자가 호환 가능하고 지원되는 Operator 설치를 유지하려면 업데이트된 인덱스 이미지를 참조하도록 사용자 정의 카탈로그도 업데이트해야 합니다.

OpenShift Container Platform 4.9부터 클러스터 관리자는 사용자 정의 카탈로그의 `CatalogSource` 오브젝트에 `olm.catalogImageTemplate` 주석을 템플릿이 포함된 이미지 참조에 추가할 수 있습니다. 템플릿에서 사용할 수 있도록 지원되는 Kubernetes 버전 변수는 다음과 같습니다.

`kube_major_version`

`kube_minor_version`

`kube_patch_version`

참고

현재 템플릿에 사용할 수 없으므로 OpenShift Container Platform 클러스터 버전이 아닌 Kubernetes 클러스터 버전을 지정해야 합니다.

업데이트된 Kubernetes 버전을 지정하는 태그로 인덱스 이미지를 생성하고 푸시한 경우 이 주석을 설정하면 사용자 정의 카탈로그의 인덱스 이미지 버전이 클러스터 업그레이드 후 자동으로 변경될 수 있습니다. 주석 값은 `CatalogSource` 오브젝트의 `spec.image` 필드에서 이미지 참조를 설정하거나 업데이트하는 데 사용됩니다.

이로 인해 Operator가 지원되지 않는 상태이거나 지속적인 업데이트 경로가 없는 클러스터 업그레이드가 방지됩니다.

중요

업데이트된 태그가 있는 인덱스 이미지에 저장되어 있는 레지스트리가 클러스터 업그레이드 시 클러스터에서 액세스할 수 있는지 확인해야 합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  generation: 1
  name: example-catalog
  namespace: openshift-marketplace
  annotations:
    olm.catalogImageTemplate:
      "quay.io/example-org/example-catalog:v{kube_major_version}.{kube_minor_version}"
spec:
  displayName: Example Catalog
  image: quay.io/example-org/example-catalog:v1.33
  priority: -400
  publisher: Example Org
```

참고

`spec.image` 필드와 `olm.catalogImageTemplate` 주석이 둘 다 설정된 경우 주석의 확인된 값으로 `spec.image` 필드를 덮어씁니다. 주석이 사용 가능한 풀 사양으로 확인되지 않으면 카탈로그 소스는 설정된 `spec.image` 값으로 대체됩니다.

`spec.image` 필드가 설정되지 않고 주석이 사용 가능한 풀 사양으로 확인되지 않으면 OLM에서 카탈로그 소스의 조정을 중지하고 사람이 읽을 수 있는 오류 조건으로 설정합니다.

Kubernetes 1.33을 사용하는 OpenShift Container Platform 4.20 클러스터의 경우 이전 예제의 `olm.catalogImageTemplate` 주석은 다음 이미지 참조로 확인됩니다.

```shell-session
quay.io/example-org/example-catalog:v1.33
```

향후 OpenShift Container Platform 릴리스에서는 이후 OpenShift Container Platform 버전에서 사용하는 이후 Kubernetes 버전을 대상으로 하는 사용자 정의 카탈로그의 업데이트된 인덱스 이미지를 생성할 수 있습니다.

업그레이드 전에 `olm.catalogImageTemplate` 주석을 설정하여 클러스터를 이후 OpenShift Container Platform 버전으로 업그레이드하면 카탈로그의 인덱스 이미지도 자동으로 업데이트됩니다.

#### 2.4.1.2.2.2. 카탈로그 상태 요구 사항

클러스터의 Operator 카탈로그는 설치 확인 관점에서 서로 바꿔 사용할 수 있습니다. `서브스크립션` 오브젝트는 특정 카탈로그를 참조할 수 있지만 클러스터의 모든 카탈로그를 사용하여 종속성을 해결합니다.

예를 들어 카탈로그 A가 비정상이면 카탈로그 A를 참조하는 서브스크립션은 일반적으로 A보다 카탈로그 우선 순위가 낮기 때문에 클러스터 관리자가 예상하지 못할 수 있는 카탈로그 B의 종속성을 확인할 수 있습니다.

결과적으로 OLM에서는 지정된 글로벌 네임스페이스(예: 기본 `openshift-marketplace` 네임스페이스 또는 사용자 정의 글로벌 네임스페이스)가 있는 모든 카탈로그가 정상이어야 합니다.

카탈로그가 비정상이면 공유 글로벌 네임스페이스 내의 모든 Operator 설치 또는 업데이트 작업이 `CatalogSourcesUnhealthy` 조건으로 실패합니다. 비정상적인 상태에서 이러한 작업이 허용된 경우 OLM에서 클러스터 관리자에게 예기치 않은 확인 및 설치 결정을 내릴 수 있습니다.

클러스터 관리자는 비정상 카탈로그를 관찰하고 카탈로그를 유효하지 않은 것으로 간주하고 Operator 설치를 재개하려는 경우 비정상 카탈로그 제거에 대한 자세한 내용은 "사용자 정의 카탈로그 제거" 또는 "기본 소프트웨어 카탈로그 소스 비활성화" 섹션을 참조하십시오.

추가 리소스

사용자 정의 카탈로그 제거

기본 OperatorHub 카탈로그 소스 비활성화

#### 2.4.1.2.3. 서브스크립션

`Subscription` 오브젝트에서 정의하는 서브스크립션 은 Operator를 설치하려는 의도를 나타냅니다. Operator와 카탈로그 소스를 연결하는 사용자 정의 리소스입니다.

서브스크립션은 Operator 패키지에서 구독할 채널과 업데이트를 자동 또는 수동으로 수행할지를 나타냅니다. 자동으로 설정된 경우 OLM(Operator Lifecycle Manager)은 서브스크립션을 통해 클러스터에서 항상 최신 버전의 Operator가 실행되도록 Operator를 관리하고 업그레이드합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: example-operator
  namespace: example-namespace
spec:
  channel: stable
  name: example-operator
  source: example-catalog
  sourceNamespace: openshift-marketplace
```

이 `Subscription` 오브젝트는 Operator의 이름 및 네임스페이스, Operator 데이터를 확인할 수 있는 카탈로그를 정의합니다. `alpha`, `beta` 또는 `stable` 과 같은 채널은 카탈로그 소스에서 설치해야 하는 Operator 스트림을 결정하는 데 도움이 됩니다.

서브스크립션에서 채널 이름은 Operator마다 다를 수 있지만 이름 지정 스키마는 지정된 Operator 내의 공통 규칙을 따라야 합니다. 예를 들어 채널 이름은 Operator(`1.2`, `1.3`) 또는 릴리스 빈도(`stable`, `fast`)에서 제공하는 애플리케이션의 마이너 릴리스 업데이트 스트림을 따를 수 있습니다.

OpenShift Container Platform 웹 콘솔에서 쉽게 확인할 수 있을 뿐만 아니라 관련 서브스크립션의 상태를 검사하여 사용 가능한 최신 버전의 Operator가 있는 경우 이를 확인할 수 있습니다. `currentCSV` 필드와 연결된 값은 OLM에 알려진 최신 버전이고 `installedCSV` 는 클러스터에 설치된 버전입니다.

추가 리소스

멀티 테넌시 및 Operator 공동 배치

CLI를 사용하여 Operator 서브스크립션 상태 보기

#### 2.4.1.2.4. 설치 계획

`InstallPlan` 오브젝트에서 정의하는 설치 계획 은 OLM(Operator Lifecycle Manager)에서 특정 버전의 Operator로 설치 또는 업그레이드하기 위해 생성하는 리소스 세트를 설명합니다. 버전은 CSV(클러스터 서비스 버전)에서 정의합니다.

Operator, 클러스터 관리자 또는 Operator 설치 권한이 부여된 사용자를 설치하려면 먼저 `Subscription` 오브젝트를 생성해야 합니다. 서브스크립션은 카탈로그 소스에서 사용 가능한 Operator 버전의 스트림을 구독하려는 의도를 나타냅니다.

그런 다음 서브스크립션을 통해 Operator의 리소스를 쉽게 설치할 수 있도록 `InstallPlan` 오브젝트가 생성됩니다.

그런 다음 다음 승인 전략 중 하나에 따라 설치 계획을 승인해야 합니다.

서브스크립션의 `spec.installPlanApproval` 필드가 `Automatic` 로 설정된 경우 설치 계획이 자동으로 승인됩니다.

서브스크립션의 `spec.installPlanApproval` 필드가 `Manual` 로 설정된 경우 클러스터 관리자 또는 적절한 권한이 있는 사용자가 설치 계획을 수동으로 승인해야 합니다.

설치 계획이 승인되면 OLM에서 지정된 리소스를 생성하고 서브스크립션에서 지정한 네임스페이스에 Operator를 설치합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: InstallPlan
metadata:
  name: install-abcde
  namespace: operators
spec:
  approval: Automatic
  approved: true
  clusterServiceVersionNames:
    - my-operator.v1.0.1
  generation: 1
status:
  ...
  catalogSources: []
  conditions:
    - lastTransitionTime: '2021-01-01T20:17:27Z'
      lastUpdateTime: '2021-01-01T20:17:27Z'
      status: 'True'
      type: Installed
  phase: Complete
  plan:
    - resolving: my-operator.v1.0.1
      resource:
        group: operators.coreos.com
        kind: ClusterServiceVersion
        manifest: >-
        ...
        name: my-operator.v1.0.1
        sourceName: redhat-operators
        sourceNamespace: openshift-marketplace
        version: v1alpha1
      status: Created
    - resolving: my-operator.v1.0.1
      resource:
        group: apiextensions.k8s.io
        kind: CustomResourceDefinition
        manifest: >-
        ...
        name: webservers.web.servers.org
        sourceName: redhat-operators
        sourceNamespace: openshift-marketplace
        version: v1beta1
      status: Created
    - resolving: my-operator.v1.0.1
      resource:
        group: ''
        kind: ServiceAccount
        manifest: >-
        ...
        name: my-operator
        sourceName: redhat-operators
        sourceNamespace: openshift-marketplace
        version: v1
      status: Created
    - resolving: my-operator.v1.0.1
      resource:
        group: rbac.authorization.k8s.io
        kind: Role
        manifest: >-
        ...
        name: my-operator.v1.0.1-my-operator-6d7cbc6f57
        sourceName: redhat-operators
        sourceNamespace: openshift-marketplace
        version: v1
      status: Created
    - resolving: my-operator.v1.0.1
      resource:
        group: rbac.authorization.k8s.io
        kind: RoleBinding
        manifest: >-
        ...
        name: my-operator.v1.0.1-my-operator-6d7cbc6f57
        sourceName: redhat-operators
        sourceNamespace: openshift-marketplace
        version: v1
      status: Created
      ...
```

추가 리소스

멀티 테넌시 및 Operator 공동 배치

비 클러스터 관리자가 Operator를 설치하도록 허용

#### 2.4.1.2.5. Operator groups

`OperatorGroup` 리소스에서 정의하는 Operator group 에서는 OLM에서 설치한 Operator에 다중 테넌트 구성을 제공합니다. Operator group은 멤버 Operator에 필요한 RBAC 액세스 권한을 생성할 대상 네임스페이스를 선택합니다.

대상 네임스페이스 세트는 쉼표로 구분된 문자열 형식으로 제공되며 CSV(클러스터 서비스 버전)의 `olm.targetNamespaces` 주석에 저장되어 있습니다. 이 주석은 멤버 Operator의 CSV 인스턴스에 적용되며 해당 배포에 프로젝션됩니다.

추가 리소스

Operator groups

#### 2.4.1.2.6. Operator 상태

OLM(Operator Lifecycle Manager)에서는 Operator의 라이프사이클을 관리하는 역할의 일부로, Operator를 정의하는 Kubernetes 리소스의 상태에서 Operator의 상태를 유추합니다.

이 접근 방식에서는 Operator가 지정된 상태에 있도록 어느 정도는 보장하지만 Operator에서 다른 방법으로는 유추할 수 없는 정보를 OLM에 보고해야 하는 경우가 많습니다. 그러면 OLM에서 이러한 정보를 사용하여 Operator의 라이프사이클을 더 효과적으로 관리할 수 있습니다.

OLM에서는 Operator에서 OLM에 조건을 보고할 수 있는 `OperatorCondition` 이라는 CRD(사용자 정의 리소스 정의)를 제공합니다. `OperatorCondition` 리소스의 `Spec.Conditions` 어레이에 있는 경우 OLM의 Operator 관리에 영향을 줄 수 있는 일련의 조건이 지원됩니다.

참고

기본적으로 `Spec.Conditions` 어레이는 사용자가 추가하거나 사용자 정의 Operator 논리의 결과로 `OperatorCondition` 오브젝트에 존재하지 않습니다.

추가 리소스

Operator 상태

#### 2.4.2. Operator Lifecycle Manager 아키텍처

이 가이드에서는 OpenShift Container Platform의 OLM(Operator Lifecycle Manager) 구성 요소 아키텍처를 간략하게 설명합니다.

#### 2.4.2.1. 구성 요소의 역할

OLM(Operator Lifecycle Manager)은 OLM Operator와 Catalog Operator의 두 Operator로 구성됩니다.

OLM 및 Catalog Operator는 OLM 프레임워크의 기반인 CRD(사용자 정의 리소스 정의)를 관리합니다.

| 리소스 | 짧은 이름 | 소유자 | Description |
| --- | --- | --- | --- |
| `ClusterServiceVersion` (CSV) | `csv` | OLM | 애플리케이션 메타데이터: 이름, 버전, 아이콘, 필수 리소스, 설치 등입니다. |
| `InstallPlan` | `ip` | 카탈로그 | CSV를 자동으로 설치하거나 업그레이드하기 위해 생성하는 계산된 리소스 목록입니다. |
| `CatalogSource` | `catsrc` | 카탈로그 | 애플리케이션을 정의하는 CSV, CRD, 패키지의 리포지토리입니다. |
| `서브스크립션` | `sub` | 카탈로그 | 패키지의 채널을 추적하여 CSV를 최신 상태로 유지하는 데 사용됩니다. |
| `OperatorGroup` | `og` | OLM | 동일한 네임스페이스에 배포된 모든 Operator를 `OperatorGroup` 오브젝트로 구성하여 네임스페이스 목록 또는 클러스터 수준에서 CR(사용자 정의 리소스)을 조사합니다. |

또한 각 Operator는 다음 리소스를 생성합니다.

| 리소스 | 소유자 |
| --- | --- |
| `Deployments` | OLM |
| `ServiceAccounts` |
| `(Cluster)Roles` |
| `(Cluster)RoleBindings` |
| CRD( `CustomResourceDefinitions` ) | 카탈로그 |
| `ClusterServiceVersions` |

#### 2.4.2.2. OLM Operator

CSV에 지정된 필수 리소스가 클러스터에 제공되면 OLM Operator는 CSV 리소스에서 정의하는 애플리케이션을 배포합니다.

OLM Operator는 필수 리소스 생성과는 관련이 없습니다. CLI 또는 Catalog Operator를 사용하여 이러한 리소스를 수동으로 생성하도록 선택할 수 있습니다. 이와 같은 분리를 통해 사용자는 애플리케이션에 활용하기 위해 선택하는 OLM 프레임워크의 양을 점차 늘리며 구매할 수 있습니다.

OLM Operator에서는 다음 워크플로를 사용합니다.

네임스페이스에서 CSV(클러스터 서비스 버전)를 조사하고 해당 요구 사항이 충족되는지 확인합니다.

요구사항이 충족되면 CSV에 대한 설치 전략을 실행합니다.

참고

설치 전략을 실행하기 위해서는 CSV가 Operator group의 활성 멤버여야 합니다.

#### 2.4.2.3. Catalog Operator

Catalog Operator는 CSV(클러스터 서비스 버전) 및 CSV에서 지정하는 필수 리소스를 확인하고 설치합니다. 또한 채널에서 패키지 업데이트에 대한 카탈로그 소스를 조사하고 원하는 경우 사용 가능한 최신 버전으로 자동으로 업그레이드합니다.

채널에서 패키지를 추적하려면 원하는 패키지를 구성하는 `Subscription` 오브젝트, 채널, 업데이트를 가져오는 데 사용할 `CatalogSource` 오브젝트를 생성하면 됩니다. 업데이트가 확인되면 사용자를 대신하여 네임스페이스에 적절한 `InstallPlan` 오브젝트를 기록합니다.

Catalog Operator에서는 다음 워크플로를 사용합니다.

클러스터의 각 카탈로그 소스에 연결합니다.

사용자가 생성한 설치 계획 중 확인되지 않은 계획이 있는지 조사하고 있는 경우 다음을 수행합니다.

요청한 이름과 일치하는 CSV를 찾아 확인된 리소스로 추가합니다.

각 관리 또는 필수 CRD의 경우 CRD를 확인된 리소스로 추가합니다.

각 필수 CRD에 대해 이를 관리하는 CSV를 확인합니다.

확인된 설치 계획을 조사하고 사용자의 승인에 따라 또는 자동으로 해당 계획에 대해 검색된 리소스를 모두 생성합니다.

카탈로그 소스 및 서브스크립션을 조사하고 이에 따라 설치 계획을 생성합니다.

#### 2.4.2.4. 카탈로그 레지스트리

Catalog 레지스트리는 클러스터에서 생성할 CSV 및 CRD를 저장하고 패키지 및 채널에 대한 메타데이터를 저장합니다.

패키지 매니페스트 는 패키지 ID를 CSV 세트와 연결하는 카탈로그 레지스트리의 항목입니다. 패키지 내에서 채널은 특정 CSV를 가리킵니다. CSV는 교체하는 CSV를 명시적으로 참조하므로 패키지 매니페스트는 Catalog Operator에 각 중간 버전을 거쳐 CSV를 최신 버전으로 업데이트하는 데 필요한 모든 정보를 제공합니다.

#### 2.4.3. Operator Lifecycle Manager 워크플로

이 가이드에서는 OpenShift Container Platform의 OLM(Operator Lifecycle Manager)의 워크플로를 간략하게 설명합니다.

#### 2.4.3.1. OLM의 Operator 설치 및 업그레이드 워크플로

[FIGURE src="/playbooks/wiki-assets/full_rebuild/operators/olm-catalogsource.png" alt="olm catalogsource" kind="diagram" diagram_type="semantic_diagram"]
olm catalogsource
[/FIGURE]

_Source: `operators.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Operators-ko-KR/images/a4756a206580a0a1ab0e6a170ddc75e3/olm-catalogsource.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/operators/olm-channels.png" alt="olm channels" kind="diagram" diagram_type="semantic_diagram"]
olm channels
[/FIGURE]

_Source: `operators.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Operators-ko-KR/images/52025648e55a627b8be314426148fb97/olm-channels.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/operators/olm-replaces.png" alt="OLM 대체" kind="diagram" diagram_type="semantic_diagram"]
OLM 대체
[/FIGURE]

_Source: `operators.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Operators-ko-KR/images/6990efb545ef499e93732227bbe7df68/olm-replaces.png`_


OLM(Operator Lifecycle Manager) 에코시스템에서 다음 리소스를 사용하여 Operator 설치 및 업그레이드를 확인합니다.

`ClusterServiceVersion` (CSV)

`CatalogSource`

`서브스크립션`

CSV에 정의된 Operator 메타데이터는 카탈로그 소스라는 컬렉션에 저장할 수 있습니다. OLM은 Operator Registry API 를 사용하는 카탈로그 소스를 통해 사용 가능한 Operator와 설치된 Operator의 업그레이드를 쿼리합니다.

그림 2.3. 카탈로그 소스 개요

Operator는 카탈로그 소스 내에서 패키지 와 채널 이라는 업데이트 스트림으로 구성되는데, 채널은 웹 브라우저와 같이 연속 릴리스 주기에서 OpenShift Container Platform 또는 기타 소프트웨어에 친숙한 업데이트 패턴이어야 합니다.

그림 2.4. 카탈로그 소스의 패키지 및 채널

사용자는 서브스크립션 의 특정 카탈로그 소스에서 특정 패키지 및 채널(예: `etcd` 패키지 및 해당 `alpha` 채널)을 나타냅니다. 네임스페이스에 아직 설치되지 않은 패키지에 서브스크립션이 생성되면 해당 패키지의 최신 Operator가 설치됩니다.

참고

OLM에서는 의도적으로 버전을 비교하지 않으므로 지정된 카탈로그 → 채널 → 패키지 경로에서 사용 가능한 "최신" Operator의 버전 번호가 가장 높은 버전 번호일 필요는 없습니다. Git 리포지토리와 유사하게 채널의 헤드 참조로 간주해야 합니다.

각 CSV에는 교체 대상 Operator를 나타내는 `replaces` 매개변수가 있습니다. 이 매개변수를 통해 OLM에서 쿼리할 수 있는 CSV 그래프가 빌드되고 업데이트를 채널 간에 공유할 수 있습니다. 채널은 업데이트 그래프의 진입점으로 간주할 수 있습니다.

그림 2.5. 사용 가능한 채널 업데이트의 OLM 그래프

```yaml
packageName: example
channels:
- name: alpha
  currentCSV: example.v0.1.2
- name: beta
  currentCSV: example.v0.1.3
defaultChannel: alpha
```

OLM에서 카탈로그 소스, 패키지, 채널, CSV와 관련된 업데이트를 쿼리하려면 카탈로그에서 입력 CSV를 `replaces` 하는 단일 CSV를 모호하지 않게 결정적으로 반환할 수 있어야 합니다.

#### 2.4.3.1.1. 업그레이드 경로의 예

업그레이드 시나리오 예제에서는 CSV 버전 `0.1.1` 에 해당하는 Operator가 설치되어 있는 것으로 간주합니다. OLM은 카탈로그 소스를 쿼리하고 구독 채널에서 이전 버전이지만 설치되지 않은 CSV 버전 `0.1.2` 를 교체하는(결국 설치된 이전 CSV 버전 `0.1.1` 을 교체함) 새 CSV 버전 `0.1.3` 이 포함된 업그레이드를 탐지합니다.

OLM은 CSV에 지정된 `replaces` 필드를 통해 채널 헤드에서 이전 버전으로 돌아가 업그레이드 경로 `0.1.3` → `0.1.2` → `0.1.1` 을 결정합니다. 화살표 방향은 전자가 후자를 대체함을 나타냅니다. OLM은 채널 헤드에 도달할 때까지 Operator 버전을 한 번에 하나씩 업그레이드합니다.

지정된 이 시나리오의 경우 OLM은 Operator 버전 `0.1.2` 를 설치하여 기존 Operator 버전 `0.1.1` 을 교체합니다. 그런 다음 Operator 버전 `0.1.3` 을 설치하여 이전에 설치한 Operator 버전 `0.1.2` 를 대체합니다. 이 시점에 설치한 Operator 버전 `0.1.3` 이 채널 헤드와 일치하며 업그레이드가 완료됩니다.

#### 2.4.3.1.2. 업그레이드 건너뛰기

[FIGURE src="/playbooks/wiki-assets/full_rebuild/operators/olm-skipping-updates.png" alt="업데이트를 건너뛰는 OLM" kind="figure" diagram_type="image_figure"]
업데이트를 건너뛰는 OLM
[/FIGURE]

_Source: `operators.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Operators-ko-KR/images/da1fe891cee5ba712308b9d0e08b91e0/olm-skipping-updates.png`_


OLM의 기본 업그레이드 경로는 다음과 같습니다.

카탈로그 소스는 Operator에 대한 하나 이상의 업데이트로 업데이트됩니다.

OLM은 카탈로그 소스에 포함된 최신 버전에 도달할 때까지 Operator의 모든 버전을 트래버스합니다.

그러나 경우에 따라 이 작업을 수행하는 것이 안전하지 않을 수 있습니다. 게시된 버전의 Operator가 아직 설치되지 않은 경우 클러스터에 설치해서는 안 되는 경우가 있습니다. 예를 들면 버전에 심각한 취약성이 있기 때문입니다.

이러한 경우 OLM에서는 두 가지 클러스터 상태를 고려하여 다음을 둘 다 지원하는 업데이트 그래프를 제공해야 합니다.

"잘못"된 중간 Operator가 클러스터에 표시되고 설치되었습니다.

"잘못된" 중간 Operator가 클러스터에 아직 설치되지 않았습니다.

새 카탈로그를 제공하고 건너뛰기 릴리스를 추가하면 클러스터 상태 및 잘못된 업데이트가 있는지와 관계없이 OLM에서 항상 고유한 단일 업데이트를 가져올 수 있습니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: ClusterServiceVersion
metadata:
  name: etcdoperator.v0.9.2
  namespace: placeholder
  annotations:
spec:
    displayName: etcd
    description: Etcd Operator
    replaces: etcdoperator.v0.9.0
    skips:
    - etcdoperator.v0.9.1
```

기존 CatalogSource 및 새 CatalogSource 의 다음 예제를 고려하십시오.

그림 2.6. 업데이트 건너뛰기

이 그래프에는 다음이 유지됩니다.

기존 CatalogSource 에 있는 모든 Operator에는 새 CatalogSource 에 단일 대체 항목이 있습니다.

새 CatalogSource 에 있는 모든 Operator에는 새 CatalogSource 에 단일 대체 항목이 있습니다.

잘못된 업데이트가 아직 설치되지 않은 경우 설치되지 않습니다.

#### 2.4.3.1.3. 여러 Operator 교체

설명된 새 CatalogSource 를 생성하려면 하나의 Operator를 `replace` 하지만 여러 Operator를 `건너뛸` 수 있는 CSV를 게시해야 합니다. 이 작업은 `skipRange` 주석을 사용하여 수행할 수 있습니다.

```yaml
olm.skipRange: <semver_range>
```

여기서 `<semver_range>` 에는 semver 라이브러리 에서 지원하는 버전 범위 형식이 있습니다.

카탈로그에서 업데이트를 검색할 때 채널 헤드에 `skipRange` 주석이 있고 현재 설치된 Operator에 범위에 해당하는 버전 필드가 있는 경우 OLM이 채널의 최신 항목으로 업데이트됩니다.

우선순위 순서는 다음과 같습니다.

기타 건너뛰기 기준이 충족되는 경우 서브스크립션의 `sourceName` 에 지정된 소스의 채널 헤드

`sourceName` 에 지정된 소스의 현재 Operator를 대체하는 다음 Operator

기타 건너뛰기 조건이 충족되는 경우 서브스크립션에 표시되는 다른 소스의 채널 헤드.

서브스크립션에 표시되는 모든 소스의 현재 Operator를 대체하는 다음 Operator.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: ClusterServiceVersion
metadata:
    name: elasticsearch-operator.v4.1.2
    namespace: <namespace>
    annotations:
        olm.skipRange: '>=4.1.0 <4.1.2'
```

#### 2.4.3.1.4. z-stream 지원

[FIGURE src="/playbooks/wiki-assets/full_rebuild/operators/olm-z-stream.png" alt="olm z 스트림" kind="figure" diagram_type="image_figure"]
olm z 스트림
[/FIGURE]

_Source: `operators.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Operators-ko-KR/images/9d8f445a920be612fe82454a3a545e70/olm-z-stream.png`_


마이너 버전이 동일한 경우 z-stream 또는 패치 릴리스로 이전 z-stream 릴리스를 모두 교체해야 합니다. OLM은 메이저, 마이너 또는 패치 버전을 구분하지 않으므로 카탈로그에 올바른 그래프만 빌드해야 합니다.

즉 OLM은 이전 CatalogSource 에서와 같이 그래프를 가져올 수 있어야 하고 이전과 유사하게 새 CatalogSource 에서와 같이 그래프를 생성할 수 있어야 합니다.

그림 2.7. 여러 Operator 교체

이 그래프에는 다음이 유지됩니다.

기존 CatalogSource 에 있는 모든 Operator에는 새 CatalogSource 에 단일 대체 항목이 있습니다.

새 CatalogSource 에 있는 모든 Operator에는 새 CatalogSource 에 단일 대체 항목이 있습니다.

이전 CatalogSource 의 모든 z-stream 릴리스가 새 CatalogSource 의 최신 z-stream 릴리스로 업데이트됩니다.

사용할 수 없는 릴리스는 "가상" 그래프 노드로 간주할 수 있습니다. 해당 콘텐츠가 존재할 필요는 없으며 그래프가 이와 같은 경우 레지스트리에서 응답하기만 하면 됩니다.

#### 2.4.4. Operator Lifecycle Manager 종속성 확인

이 가이드에서는 OpenShift Container Platform의 OLM(Operator Lifecycle Manager)을 사용한 종속성 해결 및 CRD(사용자 정의 리소스 정의) 업그레이드 라이프사이클에 대해 간단히 설명합니다.

#### 2.4.4.1. 종속성 확인 정보

OLM(Operator Lifecycle Manager)은 실행 중인 Operator의 종속성 확인 및 업그레이드 라이프사이클을 관리합니다. OLM에서 발생하는 문제는 여러 가지 면에서 `yum` 및 `rpm` 과 같은 다른 시스템 또는 언어 패키지 관리자와 유사합니다.

그러나 OLM에는 유사한 시스템에는 일반적으로 해당하지 않는 한 가지 제약 조건이 있습니다. 즉 Operator가 항상 실행되고 있으므로 OLM에서 서로 함께 작동하지 않는 Operator 세트를 제공하지 않도록 합니다.

결과적으로 OLM에서 다음 시나리오를 생성하지 않아야 합니다.

제공할 수 없는 API가 필요한 Operator 세트를 설치합니다.

Operator에 종속된 다른 Operator를 중단하는 방식으로 업데이트

이는 다음 두 가지 유형의 데이터로 가능합니다.

| 속성 | 종속성 확인기에서 공용 인터페이스를 구성하는 Operator에 대한 입력된 메타데이터입니다. 예를 들면 Operator에서 제공하는 API의 GVK(그룹/버전/종류)와 Operator의 의미 버전(semver)이 있습니다. |
| --- | --- |
| 제약 조건 또는 종속 항목 | 대상 클러스터에 이미 설치되어 있거나 설치되지 않았을 수 있는 다른 Operator에서 충족해야 하는 Operator의 요구 사항입니다. 이는 사용 가능한 모든 Operator에 대한 쿼리 또는 필터 역할을 하며 종속성 확인 및 설치 중에 선택을 제한합니다. 예를 들면 클러스터에서 특정 API를 사용하거나 특정 버전이 설치된 특정 Operator가 설치되어 있어야 하는 경우가 있습니다. |

OLM은 이러한 속성 및 제약 조건을 부울 공식 시스템으로 변환하고 이를 설치해야 하는 Operator를 결정하는 작업을 수행하는 부울 만족 가능성을 설정하는 프로그램인 SAT 솔버에 전달합니다.

#### 2.4.4.2. Operator 속성

카탈로그의 모든 Operator에는 다음과 같은 속성이 있습니다.

`olm.package`

패키지 이름 및 Operator 버전이 포함됩니다.

`olm.gvk`

CSV(클러스터 서비스 버전)에서 제공되는 각 API의 단일 속성

Operator 번들의 `metadata/` 디렉터리에 `properties.yaml` 파일을 포함하여 Operator 작성자가 추가 속성을 직접 선언할 수도 있습니다.

```yaml
properties:
- type: olm.kubeversion
  value:
    version: "1.16.0"
```

#### 2.4.4.2.1. 임의의 속성

Operator 작성자는 Operator 번들의 `metadata/` 디렉터리에 있는 `properties.yaml` 파일에서 임의의 속성을 선언할 수 있습니다. 이러한 속성은 런타임 시 OLM(Operator Lifecycle Manager) 확인기에 대한 입력으로 사용되는 맵 데이터 구조로 변환됩니다.

이러한 속성은 속성을 이해할 수 없으므로 확인자에게 불투명하지만, 해당 속성에 대한 일반 제약 조건을 평가하여 속성 목록을 충족할 수 있는지 여부를 결정할 수 있습니다.

```yaml
properties:
  - property:
      type: color
      value: red
  - property:
      type: shape
      value: square
  - property:
      type: olm.gvk
      value:
        group: olm.coreos.io
        version: v1alpha1
        kind: myresource
```

이 구조를 사용하여 일반 제약 조건에 대한 CEL(Common Expression Language) 표현식을 구성할 수 있습니다.

추가 리소스

CEL(Common Expression Language) 제약 조건

#### 2.4.4.3. Operator 종속 항목

Operator의 종속 항목은 번들의 `metadata/` 폴더에 있는 `dependencies.yaml` 파일에 나열되어 있습니다. 이 파일은 선택 사항이며 현재는 명시적인 Operator 버전 종속 항목을 지정하는 데만 사용됩니다.

종속성 목록에는 종속성의 유형을 지정하기 위해 각 항목에 대한 `type` 필드가 포함되어 있습니다. 다음과 같은 유형의 Operator 종속 항목이 지원됩니다.

`olm.package`

이 유형은 특정 Operator 버전에 대한 종속성을 나타냅니다. 종속 정보에는 패키지 이름과 패키지 버전이 semver 형식으로 포함되어야 합니다. 예를 들어 `0.5.2` 와 같은 정확한 버전이나 `>0.5.1` 과 같은 버전 범위를 지정할 수 있습니다.

`olm.gvk`

이 유형을 사용하면 작성자는 CSV의 기존 CRD 및 API 기반 사용과 유사하게 GVK(그룹/버전/종류) 정보를 사용하여 종속성을 지정할 수 있습니다. 이 경로를 통해 Operator 작성자는 모든 종속 항목, API 또는 명시적 버전을 동일한 위치에 통합할 수 있습니다.

`olm.constraint`

이 유형은 임의의 Operator 속성에 대한 일반 제약 조건을 선언합니다.

다음 예제에서는 Prometheus Operator 및 etcd CRD에 대한 종속 항목을 지정합니다.

```yaml
dependencies:
  - type: olm.package
    value:
      packageName: prometheus
      version: ">0.27.0"
  - type: olm.gvk
    value:
      group: etcd.database.coreos.com
      kind: EtcdCluster
      version: v1beta2
```

#### 2.4.4.4. 일반 제약 조건

`olm.constraint` 속성은 특정 유형의 종속성 제약 조건을 선언하여 non-constraint 및 constraint 속성을 구분합니다. 해당 `value` 필드는 제약 조건 메시지의 문자열 표시가 있는 `failureMessage` 필드를 포함하는 오브젝트입니다. 이 메시지는 런타임 시 제약 조건이 만족스럽지 않은 경우 사용자에게 유용한 주석으로 표시됩니다.

다음 키는 사용 가능한 제약 조건 유형을 나타냅니다.

`gvk`

`olm.gvk` 유형과 동일한 값 및 해석을 입력합니다.

`패키지`

`olm.package` 유형과 동일한 값 및 해석을 입력합니다.

`EL`

임의의 번들 속성 및 클러스터 정보를 통해 OLM(Operator Lifecycle Manager) 확인자에 의해 런타임 시 평가되는 CEL(Common Expression Language) 표현식

`all`, `any`, `not`

`gvk` 또는 중첩된 복합 제약 조건과 같은 하나 이상의 구체적인 제약 조건을 각각 포함하는 결합, 제거 및 부정 제약 조건

#### 2.4.4.4.1. CEL(Common Expression Language) 제약 조건

Cel `제약` 조건 유형은 CEL(Common Expression Language) 을 표현식 언어로 지원합니다. `cel` struct에는 Operator가 제약 조건을 충족하는지 확인하기 위해 런타임 시 Operator 속성에 대해 평가되는 CEL 표현식 문자열이 포함된 `rule` 필드가 있습니다.

```yaml
type: olm.constraint
value:
  failureMessage: 'require to have "certified"'
  cel:
    rule: 'properties.exists(p, p.type == "certified")'
```

CEL 구문은 `AND` 및 `OR` 와 같은 다양한 논리 연산자를 지원합니다. 결과적으로 단일 CEL 표현식에는 이러한 논리 연산자가 함께 연결된 여러 조건에 대해 여러 규칙이 있을 수 있습니다.

이러한 규칙은 번들 또는 지정된 소스와 다른 여러 속성의 데이터 집합에 대해 평가되며 단일 제약 조건 내에서 모든 규칙을 충족하는 단일 번들 또는 Operator로 출력이 해결됩니다.

```yaml
type: olm.constraint
value:
  failureMessage: 'require to have "certified" and "stable" properties'
  cel:
    rule: 'properties.exists(p, p.type == "certified") && properties.exists(p, p.type == "stable")'
```

#### 2.4.4.4.2. 복합 제약 조건 (모두, 일부, 아님)

복합 제약 조건 유형은 논리 정의에 따라 평가됩니다.

다음은 두 패키지의 연속 제약 조건(`모두`)과 하나의 GVK의 예입니다. 즉, 설치된 번들로 모두 충족해야 합니다.

```yaml
schema: olm.bundle
name: red.v1.0.0
properties:
- type: olm.constraint
  value:
    failureMessage: All are required for Red because...
    all:
      constraints:
      - failureMessage: Package blue is needed for...
        package:
          name: blue
          versionRange: '>=1.0.0'
      - failureMessage: GVK Green/v1 is needed for...
        gvk:
          group: greens.example.com
          version: v1
          kind: Green
```

다음은 동일한 GVK의 세 가지 버전의 disjunctive 제약 조건 (`any`)의 예입니다. 즉, 설치된 번들로 하나 이상을 충족해야 합니다.

```yaml
schema: olm.bundle
name: red.v1.0.0
properties:
- type: olm.constraint
  value:
    failureMessage: Any are required for Red because...
    any:
      constraints:
      - gvk:
          group: blues.example.com
          version: v1beta1
          kind: Blue
      - gvk:
          group: blues.example.com
          version: v1beta2
          kind: Blue
      - gvk:
          group: blues.example.com
          version: v1
          kind: Blue
```

다음은 하나의 GVK 버전의 부정 제약 조건(`Not`)의 예입니다. 즉 결과 집합의 모든 번들에서 GVK를 제공할 수 없습니다.

```yaml
schema: olm.bundle
name: red.v1.0.0
properties:
- type: olm.constraint
  value:
  all:
    constraints:
    - failureMessage: Package blue is needed for...
      package:
        name: blue
        versionRange: '>=1.0.0'
    - failureMessage: Cannot be required for Red because...
      not:
        constraints:
        - gvk:
            group: greens.example.com
            version: v1alpha1
            kind: greens
```

부정 의미 체계는 제약 조건이 `아닌 컨텍스트에서 명확하지 않을` 수 있습니다. 명확히하기 위해 부정은 특정 GVK, 버전에서 패키지 또는 결과 세트에서 일부 하위 복합 제약 조건을 충족하는 가능한 솔루션을 제거하도록 해결자에게 실제로 지시하고 있습니다.

코롤리(corollary)로서, `not` compound constraint는 `모든` 또는 `임의의` 제약 조건 내에서만 사용해야 하는데, 이는 우선 가능한 종속성 세트를 선택하지 않고 부정하는 것은 의미가 없기 때문입니다.

#### 2.4.4.4.3. 중첩된 복합 제약 조건

0개 이상의 간단한 제약 조건과 함께 하나 이상의 하위 복합 제약 조건을 포함하는 중첩된 복합 제약 조건은 이전에 설명한 각 제약 조건 유형에 대한 프로시저에 따라 평가됩니다.A nested compound constraint, one that contains at least one child compound constraint along with zero or more simple constraints, is evaluated from the bottom up the procedures for each previously described constraint type.

다음은 연결 해제의 예이며, 여기서 하나, 다른 또는 둘 다 제약 조건을 충족할 수 있습니다.

```yaml
schema: olm.bundle
name: red.v1.0.0
properties:
- type: olm.constraint
  value:
    failureMessage: Required for Red because...
    any:
      constraints:
      - all:
          constraints:
          - package:
              name: blue
              versionRange: '>=1.0.0'
          - gvk:
              group: blues.example.com
              version: v1
              kind: Blue
      - all:
          constraints:
          - package:
              name: blue
              versionRange: '<1.0.0'
          - gvk:
              group: blues.example.com
              version: v1beta1
              kind: Blue
```

참고

`olm.constraint` 유형의 최대 원시 크기는 리소스 소진 공격을 제한하는 64KB입니다.

#### 2.4.4.5. 종속 기본 설정

Operator의 종속성을 동등하게 충족하는 옵션이 여러 개가 있을 수 있습니다. OLM(Operator Lifecycle Manager)의 종속성 확인자는 요청된 Operator의 요구 사항에 가장 적합한 옵션을 결정합니다. Operator 작성자 또는 사용자에게는 명확한 종속성 확인을 위해 이러한 선택이 어떻게 이루어지는지 이해하는 것이 중요할 수 있습니다.

#### 2.4.4.5.1. 카탈로그 우선순위

OpenShift Container Platform 클러스터에서 OLM은 카탈로그 소스를 읽고 설치에 사용할 수 있는 Operator를 확인합니다.

```yaml
apiVersion: "operators.coreos.com/v1alpha1"
kind: "CatalogSource"
metadata:
  name: "my-operators"
  namespace: "operators"
spec:
  sourceType: grpc
  grpcPodConfig:
    securityContextConfig: <security_mode>
  image: example.com/my/operator-index:v1
  displayName: "My Operators"
  priority: 100
```

1. `legacy` 또는 `restricted` 를 지정합니다. 필드가 설정되지 않은 경우 기본값은 `legacy` 입니다. 향후 OpenShift Container Platform 릴리스에서는 기본값이 `제한` 될 예정입니다.

참고

`제한된` 권한으로 카탈로그를 실행할 수 없는 경우 이 필드를 기존으로 수동으로 설정하는 것이 `좋습니다`.

`CatalogSource` 오브젝트에는 `priority` 필드가 있으며 확인자는 이 필드를 통해 종속성에 대한 옵션의 우선순위를 부여하는 방법을 확인합니다.

카탈로그 기본 설정을 관리하는 규칙에는 다음 두 가지가 있습니다.

우선순위가 높은 카탈로그의 옵션이 우선순위가 낮은 카탈로그의 옵션보다 우선합니다.

종속 항목과 동일한 카탈로그의 옵션이 다른 카탈로그보다 우선합니다.

#### 2.4.4.5.2. 채널 순서

카탈로그의 Operator 패키지는 사용자가 OpenShift Container Platform 클러스터에서 구독할 수 있는 업데이트 채널 컬렉션입니다. 채널은 마이너 릴리스(`1.2`, `1.3`) 또는 릴리스 빈도(`stable`, `fast`)에 대해 특정 업데이트 스트림을 제공하는 데 사용할 수 있습니다.

동일한 패키지에 있지만 채널이 다른 Operator로 종속성을 충족할 수 있습니다. 예를 들어 버전 `1.2` 의 Operator는 `stable` 및 `fast` 채널 모두에 존재할 수 있습니다.

각 패키지에는 기본이 채널이 있으며 항상 기본이 아닌 채널에 우선합니다. 기본 채널의 옵션으로 종속성을 충족할 수 없는 경우 남아 있는 채널의 옵션을 채널 이름의 사전 순으로 고려합니다.

#### 2.4.4.5.3. 채널 내 순서

대부분의 경우 단일 채널 내에는 종속성을 충족하는 옵션이 여러 개 있습니다. 예를 들어 하나의 패키지 및 채널에 있는 Operator에서는 동일한 API 세트를 제공합니다.

이는 사용자가 서브스크립션을 생성할 때 업데이트를 수신하는 채널을 나타냅니다. 이를 통해 검색 범위가 이 하나의 채널로 즉시 줄어듭니다. 하지만 채널 내에서 다수의 Operator가 종속성을 충족할 수 있습니다.

채널 내에서는 업데이트 그래프에서 더 높이 있는 최신 Operator가 우선합니다. 채널 헤드에서 종속성을 충족하면 먼저 시도됩니다.

#### 2.4.4.5.4. 기타 제약 조건

패키지 종속 항목에서 제공하는 제약 조건 외에도 OLM에는 필요한 사용자 상태를 나타내고 확인 불변성을 적용하는 추가 제약 조건이 포함됩니다.

#### 2.4.4.5.4.1. 서브스크립션 제약 조건

서브스크립션 제약 조건은 서브스크립션을 충족할 수 있는 Operator 세트를 필터링합니다. 서브스크립션은 종속성 확인자에 대한 사용자 제공 제약 조건입니다. Operator가 클러스터에 없는 경우 새 Operator를 설치하거나 기존 Operator를 계속 업데이트할지를 선언합니다.

#### 2.4.4.5.4.2. 패키지 제약 조건

하나의 네임스페이스 내에 동일한 패키지의 두 Operator가 제공되지 않을 수 있습니다.

#### 2.4.4.5.5. 추가 리소스

카탈로그 상태 요구 사항

#### 2.4.4.6. CRD 업그레이드

OLM은 CRD(사용자 정의 리소스 정의)가 단수형 CSV(클러스터 서비스 버전)에 속하는 경우 CRD를 즉시 업그레이드합니다. CRD가 여러 CSV에 속하는 경우에는 다음과 같은 하위 호환 조건을 모두 충족할 때 CRD가 업그레이드됩니다.

현재 CRD의 기존 서비스 버전은 모두 새 CRD에 있습니다.

CRD 제공 버전과 연결된 기존의 모든 인스턴스 또는 사용자 정의 리소스는 새 CRD의 검증 스키마에 대해 검증할 때 유효합니다.

#### 2.4.4.7. 종속성 모범 사례

종속 항목을 지정할 때는 모범 사례를 고려해야 합니다.

API 또는 특정 버전의 Operator 범위에 따라

Operator는 언제든지 API를 추가하거나 제거할 수 있습니다. 항상 Operator에서 요구하는 API에 `olm.gvk` 종속성을 지정합니다. 이에 대한 예외는 대신 `olm.package` 제약 조건을 지정하는 경우입니다.

최소 버전 설정

API 변경에 대한 Kubernetes 설명서에서는 Kubernetes 스타일 Operator에 허용되는 변경 사항을 설명합니다. 이러한 버전 관리 규칙을 사용하면 API가 이전 버전과 호환되는 경우 Operator에서 API 버전 충돌 없이 API를 업데이트할 수 있습니다.

Operator 종속 항목의 경우 이는 API 버전의 종속성을 확인하는 것으로는 종속 Operator가 의도한 대로 작동하는지 확인하는 데 충분하지 않을 수 있을 의미합니다.

예를 들면 다음과 같습니다.

TestOperator v1.0.0에서는 v1alpha1 API 버전의 `MyObject` 리소스를 제공합니다.

TestOperator v1.0.1에서는 새 필드 `spec.newfield` 를 `MyObject` 에 추가하지만 여전히 v1alpha1입니다.

Operator에 `spec.newfield` 를 `MyObject` 리소스에 쓰는 기능이 필요할 수 있습니다. `olm.gvk` 제약 조건만으로는 OLM에서 TestOperator v1.0.0이 아닌 TestOperator v1.0.1이 필요한 것으로 판단하는 데 충분하지 않습니다.

가능한 경우 API를 제공하는 특정 Operator를 미리 알고 있는 경우 추가 `olm.package` 제약 조건을 지정하여 최솟값을 설정합니다.

최대 버전 생략 또는 광범위한 범위 허용

Operator는 API 서비스 및 CRD와 같은 클러스터 범위의 리소스를 제공하기 때문에 짧은 종속성 기간을 지정하는 Operator는 해당 종속성의 다른 소비자에 대한 업데이트를 불필요하게 제한할 수 있습니다.

가능한 경우 최대 버전을 설정하지 마십시오. 또는 다른 Operator와 충돌하지 않도록 매우 광범위한 의미 범위를 설정하십시오. 예를 들면 다음 명령과 같습니다.

```shell
>1.0.0 <2.0.0
```

기존 패키지 관리자와 달리 Operator 작성자는 OLM의 채널을 통해 업데이트가 안전함을 명시적으로 인코딩합니다. 기존 서브스크립션에 대한 업데이트가 제공되면 Operator 작성자가 이전 버전에서 업데이트할 수 있음을 나타내는 것으로 간주합니다. 종속성에 최대 버전을 설정하면 특정 상한에서 불필요하게 잘라 작성자의 업데이트 스트림을 덮어씁니다.

참고

클러스터 관리자는 Operator 작성자가 설정한 종속 항목을 덮어쓸 수 없습니다.

그러나 피해야 하는 알려진 비호환성이 있는 경우 최대 버전을 설정할 수 있으며 설정해야 합니다. 버전 범위 구문을 사용하여 특정 버전을 생략할 수 있습니다(예:).

```shell
> 1.0.0!1.2.1
```

추가 리소스

Kubernetes 설명서: API 변경

#### 2.4.4.8. 종속성 경고

종속성을 지정할 때 고려해야 할 경고 사항이 있습니다.

혼합 제약 조건(AND) 없음

현재 제약 조건 간 AND 관계를 지정할 수 있는 방법은 없습니다. 즉 하나의 Operator가 지정된 API를 제공하면서 버전이 `>1.1.0` 인 다른 Operator에 종속되도록 지정할 수 없습니다.

즉 다음과 같은 종속성을 지정할 때를 나타냅니다.

```yaml
dependencies:
- type: olm.package
  value:
    packageName: etcd
    version: ">3.1.0"
- type: olm.gvk
  value:
    group: etcd.database.coreos.com
    kind: EtcdCluster
    version: v1beta2
```

OLM은 EtcdCluster를 제공하는 Operator와 버전이 `>3.1.0` 인 Operator를 사용하여 이러한 조건을 충족할 수 있습니다. 이러한 상황이 발생하는지 또는 두 제약 조건을 모두 충족하는 Operator가 선택되었는지는 잠재적 옵션을 방문하는 순서에 따라 다릅니다.

종속성 기본 설정 및 순서 지정 옵션은 잘 정의되어 있으며 추론할 수 있지만 주의를 기울이기 위해 Operator는 둘 중 하나의 메커니즘을 유지해야 합니다.

네임스페이스 간 호환성

OLM은 네임스페이스 범위에서 종속성 확인을 수행합니다. 한 네임스페이스의 Operator를 업데이트하면 다른 네임스페이스의 Operator에 문제가 되고 반대의 경우도 마찬가지인 경우 업데이트 교착 상태에 빠질 수 있습니다.

#### 2.4.4.9. 종속성 확인 시나리오 예제

다음 예제에서 공급자 는 CRD 또는 API 서비스를 "보유"한 Operator입니다.

#### 2.4.4.9.1. 예: 종속 API 사용 중단

A 및 B는 다음과 같은 API입니다(CRD).

A 공급자는 B에 의존합니다.

B 공급자에는 서브스크립션이 있습니다.

C를 제공하도록 B 공급자를 업데이트하지만 B를 더 이상 사용하지 않습니다.

결과는 다음과 같습니다.

B에는 더 이상 공급자가 없습니다.

A가 더 이상 작동하지 않습니다.

이는 OLM에서 업그레이드 전략으로 방지하는 사례입니다.

#### 2.4.4.9.2. 예: 버전 교착 상태

A 및 B는 다음과 같은 API입니다.

A 공급자에는 B가 필요합니다.

B 공급자에는 A가 필요합니다.

A 공급자를 업데이트(A2 제공, B2 요청)하고 A를 더 이상 사용하지 않습니다.

B 공급자를 업데이트(A2 제공, B2 요청)하고 B를 더 이상 사용하지 않습니다.

OLM에서 B를 동시에 업데이트하지 않고 A를 업데이트하거나 반대 방향으로 시도하는 경우 새 호환 가능 세트가 있는 경우에도 새 버전의 Operator로 진행할 수 없습니다.

이는 OLM에서 업그레이드 전략으로 방지하는 또 다른 사례입니다.

#### 2.4.5. Operator groups

이 가이드에서는 OpenShift Container Platform의 OLM(Operator Lifecycle Manager)에서 Operator groups을 사용하는 방법을 간략하게 설명합니다.

#### 2.4.5.1. Operator groups 정의

`OperatorGroup` 리소스에서 정의하는 Operator group 에서는 OLM에서 설치한 Operator에 다중 테넌트 구성을 제공합니다. Operator group은 멤버 Operator에 필요한 RBAC 액세스 권한을 생성할 대상 네임스페이스를 선택합니다.

대상 네임스페이스 세트는 쉼표로 구분된 문자열 형식으로 제공되며 CSV(클러스터 서비스 버전)의 `olm.targetNamespaces` 주석에 저장되어 있습니다. 이 주석은 멤버 Operator의 CSV 인스턴스에 적용되며 해당 배포에 프로젝션됩니다.

#### 2.4.5.2. Operator group 멤버십

다음 조건이 충족되면 Operator가 Operator group의 멤버 로 간주됩니다.

Operator의 CSV는 Operator group과 동일한 네임스페이스에 있습니다.

Operator의 CSV 설치 모드에서는 Operator group이 대상으로 하는 네임스페이스 세트를 지원합니다.

CSV의 설치 모드는 `InstallModeType` 필드 및 부울 `Supported` 필드로 구성됩니다. CSV 사양에는 다음 네 가지 `InstallModeTypes` 로 구성된 설치 모드 세트가 포함될 수 있습니다.

| InstallModeType | 설명 |
| --- | --- |
| `OwnNamespace` | Operator가 자체 네임스페이스를 선택하는 Operator group의 멤버일 수 있습니다. |
| `SingleNamespace` | Operator가 하나의 네임스페이스를 선택하는 Operator group의 멤버일 수 있습니다. |
| `MultiNamespace` | Operator가 네임스페이스를 두 개 이상 선택하는 Operator group의 멤버일 수 있습니다. |
| `AllNamespaces` | Operator가 네임스페이스를 모두 선택하는 Operator group의 멤버일 수 있습니다(대상 네임스페이스 세트는 빈 문자열( `""` )임). |

참고

CSV 사양에서 `InstallModeType` 항목이 생략되면 암시적으로 지원하는 기존 항목에서 지원을 유추할 수 있는 경우를 제외하고 해당 유형을 지원하지 않는 것으로 간주합니다.

#### 2.4.5.3. 대상 네임스페이스 선택

`spec.targetNamespaces` 매개변수를 사용하여 Operator group의 대상 네임스페이스의 이름을 명시적으로 지정할 수 있습니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: my-group
  namespace: my-namespace
spec:
  targetNamespaces:
  - my-namespace
```

또는 라벨 선택기를 `spec.selector` 매개변수와 함께 사용하여 네임스페이스를 지정할 수도 있습니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: my-group
  namespace: my-namespace
spec:
  selector:
    cool.io/prod: "true"
```

중요

`spec.targetNamespaces` 를 통해 여러 네임스페이스를 나열하거나 `spec.selector` 를 통해 라벨 선택기를 사용하는 것은 바람직하지 않습니다. Operator group의 대상 네임스페이스 두 개 이상에 대한 지원이 향후 릴리스에서 제거될 수 있습니다.

`spec.targetNamespaces` 및 `spec.selector` 를 둘 다 정의하면 `spec.selector` 가 무시됩니다. 또는 모든 네임스페이스를 선택하는 global Operator group을 지정하려면 `spec.selector` 및 `spec.targetNamespaces` 를 둘 다 생략하면 됩니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: my-group
  namespace: my-namespace
```

선택된 네임스페이스의 확인된 세트는 Opeator group의 `status.namespaces` 매개변수에 표시됩니다. 글로벌 Operator group의 `status.namespace` 에는 사용 중인 Operator에 모든 네임스페이스를 조사해야 함을 알리는 빈 문자열(`""`)이 포함됩니다.

#### 2.4.5.4. Operator group CSV 주석

Operator group의 멤버 CSV에는 다음과 같은 주석이 있습니다.

| 주석 | 설명 |
| --- | --- |
| `olm.operatorGroup=<group_name>` | Operator group의 이름을 포함합니다. |
| `olm.operatorNamespace=<group_namespace>` | Operator group의 네임스페이스를 포함합니다. |
| `olm.targetNamespaces=<target_namespaces>` | Operator group의 대상 네임스페이스 선택 사항을 나열하는 쉼표로 구분된 문자열을 포함합니다. |

참고

`olm.targetNamespaces` 를 제외한 모든 주석은 CSV 복사본에 포함됩니다. CSV 복제본에서 `olm.targetNamespaces` 주석을 생략하면 테넌트 간에 대상 네임스페이스를 복제할 수 없습니다.

#### 2.4.5.5. 제공된 API 주석

GVK(그룹/버전/종류) 는 Kubernetes API의 고유 ID입니다. Operator group에서 제공하는 GVK에 대한 정보는 `olm.providedAPIs` 주석에 표시됩니다.

주석 값은 `<kind>.<version>.<group>` 으로 구성된 문자열로, 쉼표로 구분됩니다. Operator group의 모든 활성 멤버 CSV에서 제공하는 CRD 및 API 서비스의 GVK가 포함됩니다.

`PackageManifest` 리소스를 제공하는 하나의 활성 멤버 CSV에서 `OperatorGroup` 오브젝트의 다음 예제를 검토합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  annotations:
    olm.providedAPIs: PackageManifest.v1alpha1.packages.apps.redhat.com
  name: olm-operators
  namespace: local
  ...
spec:
  selector: {}
  serviceAccountName:
    metadata:
      creationTimestamp: null
  targetNamespaces:
  - local
status:
  lastUpdated: 2019-02-19T16:18:28Z
  namespaces:
  - local
```

#### 2.4.5.6. 역할 기반 액세스 제어

Operator v이 생성되면 세 개의 클러스터 역할이 생성됩니다. 클러스터 역할이 생성되면 해시 값으로 자동으로 접미사가 지정되어 각 클러스터 역할이 고유한지 확인합니다. 각 Operator group에는 다음 표에 표시된 대로 라벨과 일치하도록 클러스터 역할 선택기가 설정된 단일 집계 규칙이 포함되어 있습니다.

| 클러스터 역할 | 일치해야 하는 라벨 |
| --- | --- |
| `olm.og.<operatorgroup_name>-admin-<hash_value>` | `olm.opgroup.permissions/aggregate-to-admin: <operatorgroup_name>` |
| `olm.og.<operatorgroup_name>-edit-<hash_value>` | `olm.opgroup.permissions/aggregate-to-edit: <operatorgroup_name>` |
| `olm.og.<operatorgroup_name>-view-<hash_value>` | `olm.opgroup.permissions/aggregate-to-view: <operatorgroup_name>` |

참고

Operator group의 클러스터 역할을 사용하여 리소스에 역할 기반 액세스 제어(RBAC)를 할당하려면 다음 명령을 실행하여 클러스터 역할 및 해시 값의 전체 이름을 가져옵니다.

```shell-session
$ oc get clusterroles | grep <operatorgroup_name>
```

Operator group이 생성될 때 해시 값이 생성되므로 클러스터 역할의 전체 이름을 찾으려면 Operator 그룹을 생성해야 합니다.

다음 RBAC 리소스는 CSV가 `AllNamespaces` 설치 모드로 모든 네임스페이스를 조사하고 이유가 `InterOperatorGroupOwnerConflict` 인 실패 상태가 아닌 한 CSV가 Operator group의 활성 멤버가 될 때 생성됩니다.

CRD의 각 API 리소스에 대한 클러스터 역할

API 서비스의 각 API 리소스에 대한 클러스터 역할

추가 역할 및 역할 바인딩

| 클러스터 역할 | 설정 |
| --- | --- |
| `<kind>.<group>-<version>-admin` | `<kind>` 의 동사: `*` 집계 라벨: `rbac.authorization.k8s.io/aggregate-to-admin: true` `olm.opgroup.permissions/aggregate-to-admin: <operatorgroup_name>` |
| `<kind>.<group>-<version>-edit` | `<kind>` 의 동사: `create` `update` `patch` `delete` 집계 라벨: `rbac.authorization.k8s.io/aggregate-to-edit: true` `olm.opgroup.permissions/aggregate-to-edit: <operatorgroup_name>` |
| `<kind>.<group>-<version>-view` | `<kind>` 의 동사: `get` `list` `watch` 집계 라벨: `rbac.authorization.k8s.io/aggregate-to-view: true` `olm.opgroup.permissions/aggregate-to-view: <operatorgroup_name>` |
| `<kind>.<group>-<version>-view-crdview` | `apiextensions.k8s.io` `customresourcedefinitions` `<crd-name>` 의 동사: `get` 집계 라벨: `rbac.authorization.k8s.io/aggregate-to-view: true` `olm.opgroup.permissions/aggregate-to-view: <operatorgroup_name>` |

| 클러스터 역할 | 설정 |
| --- | --- |
| `<kind>.<group>-<version>-admin` | `<kind>` 의 동사: `*` 집계 라벨: `rbac.authorization.k8s.io/aggregate-to-admin: true` `olm.opgroup.permissions/aggregate-to-admin: <operatorgroup_name>` |
| `<kind>.<group>-<version>-edit` | `<kind>` 의 동사: `create` `update` `patch` `delete` 집계 라벨: `rbac.authorization.k8s.io/aggregate-to-edit: true` `olm.opgroup.permissions/aggregate-to-edit: <operatorgroup_name>` |
| `<kind>.<group>-<version>-view` | `<kind>` 의 동사: `get` `list` `watch` 집계 라벨: `rbac.authorization.k8s.io/aggregate-to-view: true` `olm.opgroup.permissions/aggregate-to-view: <operatorgroup_name>` |

추가 역할 및 역할 바인딩

CSV에서 `*` 를 포함하는 정확히 하나의 대상 네임스페이스를 정의하는 경우 CSV의 `permissions` 필드에 정의된 각 권한에 대해 클러스터 역할 및 해당 클러스터 역할 바인딩이 생성됩니다. 생성된 모든 리소스에는 및 라벨이 지정됩니다.

```shell
olm.owner: <csv_name>
```

```shell
olm.owner.namespace: <csv_namespace>
```

CSV에서 `*` 를 포함하는 정확히 하나의 대상 네임스페이스를 정의하지 않는 경우에는 및 라벨이 있는 Operator 네임스페이스의 모든 역할 및 역할 바인딩이 대상 네임스페이스에 복사됩니다.

```shell
olm.owner: <csv_name>
```

```shell
olm.owner.namespace: <csv_namespace>
```

#### 2.4.5.7. CSV 복사본

OLM은 해당 Operator group의 각 대상 네임스페이스에서 Operator group의 모든 활성 멤버에 대한 CSV 복사본을 생성합니다. CSV 복사본의 용도는 대상 네임스페이스의 사용자에게 특정 Operator가 그곳에서 생성된 리소스를 조사하도록 구성됨을 알리는 것입니다.

CSV 복사본은 상태 이유가 `Copied` 이고 해당 소스 CSV의 상태와 일치하도록 업데이트됩니다. `olm.targetNamespaces` 주석은 해당 주석이 클러스터에서 생성되기 전에 CSV 복사본에서 제거됩니다. 대상 네임스페이스 선택 단계를 생략하면 테넌트 간 대상 네임스페이스가 중복되지 않습니다.

CSV 복사본은 복사본의 소스 CSV가 더 이상 존재하지 않거나 소스 CSV가 속한 Operator group이 더 이상 CSV 복사본의 네임스페이스를 대상으로 하지 않는 경우 삭제됩니다.

참고

기본적으로 `disableCopiedCSVs` 필드는 비활성화되어 있습니다. `disableCopiedCSVs` 필드를 활성화하면 OLM에서 클러스터에서 기존 복사된 CSV를 삭제합니다. `disableCopiedCSVs` 필드가 비활성화되면 OLM에서 복사된 CSV를 다시 추가합니다.

`disableCopiedCSVs` 필드를 비활성화합니다.

```yaml
$ cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1
kind: OLMConfig
metadata:
  name: cluster
spec:
  features:
    disableCopiedCSVs: false
EOF
```

`disableCopiedCSVs` 필드를 활성화합니다.

```yaml
$ cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1
kind: OLMConfig
metadata:
  name: cluster
spec:
  features:
    disableCopiedCSVs: true
EOF
```

#### 2.4.5.8. 정적 Operator groups

`spec.staticProvidedAPIs` 필드가 `true` 로 설정된 경우 Operator group은 static 입니다. 결과적으로 OLM은 Operator group의 `olm.providedAPIs` 주석을 수정하지 않으므로 사전에 설정할 수 있습니다.

이는 사용자가 Operator group을 사용하여 일련의 네임스페이스에서 리소스 경합을 방지하려고 하지만 해당 리소스에 대한 API를 제공하는 활성 멤버 CSV가 없는 경우 유용합니다.

다음은 `something.cool.io/cluster-monitoring: "true"` 주석을 사용하여 모든 네임스페이스에서 `Prometheus` 리소스를 보호하는 Operator group의 예입니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: cluster-monitoring
  namespace: cluster-monitoring
  annotations:
    olm.providedAPIs: Alertmanager.v1.monitoring.coreos.com,Prometheus.v1.monitoring.coreos.com,PrometheusRule.v1.monitoring.coreos.com,ServiceMonitor.v1.monitoring.coreos.com
spec:
  staticProvidedAPIs: true
  selector:
    matchLabels:
      something.cool.io/cluster-monitoring: "true"
```

#### 2.4.5.9. Operator group 교집합

대상 네임스페이스 세트의 교집합이 빈 세트가 아니고 `olm.providedAPIs` 주석으로 정의되어 제공된 API 세트의 교집합이 빈 세트가 아닌 경우 두 Operator groups을 교차 제공 API 가 있다고 합니다.

잠재적인 문제는 교차 제공 API가 있는 Operator groups이 교차 네임스페이스 세트에서 동일한 리소스에 대해 경쟁할 수 있다는 점입니다.

참고

교집합 규칙을 확인할 때는 Operator group 네임스페이스가 항상 선택한 대상 네임스페이스의 일부로 포함됩니다.

#### 2.4.5.9.1. 교집합 규칙

활성 멤버 CSV가 동기화될 때마다 OLM은 CSV의 Operator group 및 기타 모든 그룹 간에 교차 제공되는 API 세트에 대한 클러스터를 쿼리합니다. 그런 다음 OLM은 해당 세트가 빈 세트인지 확인합니다.

`true` 및 CSV 제공 API가 Operator group의 서브 세트인 경우:

계속 전환합니다.

`true` 및 CSV 제공 API가 Operator group의 서브 세트가 아닌 경우:

Operator group이 정적이면 다음을 수행합니다.

CSV에 속하는 배포를 정리합니다.

상태 이유 `CannotModifyStaticOperatorGroupProvidedAPIs` 와 함께 CSV를 실패 상태로 전환합니다.

Operator group이 정적이 아니면 다음을 수행합니다.

Operator group의 `olm.providedAPIs` 주석을 주석 자체와 CSV 제공 API를 결합한 내용으로 교체합니다.

`false` 및 CSV 제공 API가 Operator group의 서브 세트가 아닌 경우:

CSV에 속하는 배포를 정리합니다.

상태 이유 `InterOperatorGroupOwnerConflict` 와 함께 CSV를 실패 상태로 전환합니다.

`false` 및 CSV 제공 API가 Operator group의 서브 세트인 경우:

Operator group이 정적이면 다음을 수행합니다.

CSV에 속하는 배포를 정리합니다.

상태 이유 `CannotModifyStaticOperatorGroupProvidedAPIs` 와 함께 CSV를 실패 상태로 전환합니다.

Operator group이 정적이 아니면 다음을 수행합니다.

Operator group의 `olm.providedAPIs` 주석을 주석 자체와 CSV 제공 API 간의 차이로 교체합니다.

참고

Operator group으로 인한 실패 상태는 터미널이 아닙니다.

Operator group이 동기화될 때마다 다음 작업이 수행됩니다.

활성 멤버 CSV에서 제공되는 API 세트는 클러스터에서 계산됩니다. CSV 복사본은 무시됩니다.

클러스터 세트는 `olm.providedAPIs` 와 비교되며 `olm.providedAPIs` 에 추가 API가 포함된 경우 해당 API가 정리됩니다.

모든 네임스페이스에서 동일한 API를 제공하는 모든 CSV가 다시 큐에 추가됩니다. 그러면 충돌하는 CSV의 크기 조정 또는 삭제를 통해 충돌이 해결되었을 수 있음을 교차 group의 충돌하는 CSV에 알립니다.

#### 2.4.5.10. 다중 테넌트 Operator 관리에 대한 제한 사항

OpenShift Container Platform은 동일한 클러스터에 다른 버전의 Operator를 동시에 설치할 수 있도록 제한된 지원을 제공합니다. OLM(Operator Lifecycle Manager)은 다른 네임스페이스에 Operator를 여러 번 설치합니다. 이에 대한 한 가지 제한 사항은 Operator의 API 버전이 동일해야 한다는 것입니다.

Operator는 Kubernetes의 글로벌 리소스인 CRD(`CustomResourceDefinition` 오브젝트)를 사용하므로 컨트롤 플레인 확장입니다. Operator의 다른 주요 버전에는 종종 호환되지 않는 CRD가 있습니다. 이로 인해 클러스터의 다른 네임스페이스에 동시에 설치할 수 없습니다.

모든 테넌트 또는 네임스페이스는 클러스터의 동일한 컨트롤 플레인을 공유합니다. 따라서 다중 테넌트 클러스터의 테넌트는 글로벌 CRD도 공유하므로 동일한 클러스터에서 동일한 Operator의 다른 인스턴스를 병렬로 사용할 수 있는 시나리오를 제한합니다.

지원되는 시나리오에는 다음이 포함됩니다.

정확히 동일한 CRD 정의를 제공하는 다양한 버전의 Operator(버전이 지정된 CRD인 경우 정확히 동일한 버전)

CRD를 제공하지 않는 다른 버전의 Operator는 대신 소프트웨어 카탈로그의 별도의 번들에서 CRD를 사용할 수 있습니다.

동일한 클러스터에서 조정할 다른 Operator 버전에서 여러 개의 경쟁 또는 중복 CRD가 있는 경우 클러스터 데이터의 무결성을 보장할 수 없기 때문에 다른 시나리오는 지원되지 않습니다.

추가 리소스

OLM(Operator Lifecycle Manager) → 멀티 테넌시 및 Operator 공동 배치

다중 테넌트 클러스터의 Operator

비 클러스터 관리자가 Operator를 설치하도록 허용

#### 2.4.5.11.1. 멤버십

설치 계획의 네임스페이스에는 하나의 Operator 그룹만 포함되어야 합니다. 네임스페이스에서 CSV(클러스터 서비스 버전)를 생성하려고 할 때 설치 계획은 다음 시나리오에서 Operator 그룹이 유효하지 않은 것으로 간주합니다.

설치 계획의 네임스페이스에 Operator 그룹이 없습니다.

설치 계획의 네임스페이스에 여러 Operator 그룹이 있습니다.

Operator 그룹에 잘못된 서비스 계정 이름이 지정되어 있습니다.

설치 계획이 유효하지 않은 Operator group이 발생하면 CSV가 생성되지 않고 `InstallPlan` 리소스가 관련 메시지와 함께 계속 설치됩니다. 예를 들어 동일한 네임스페이스에 둘 이상의 Operator 그룹이 있는 경우 다음 메시지가 제공됩니다.

```shell-session
attenuated service account query failed - more than one operator group(s) are managing this namespace count=2
```

여기서 `count=` 은 네임스페이스에서 Operator 그룹 수를 지정합니다.

CSV의 설치 모드가 해당 네임스페이스에서 Operator group의 대상 네임스페이스 선택을 지원하지 않는 경우 CSV는 `UnsupportedOperatorGroup` 이유와 함께 실패 상태로 전환됩니다.

이러한 이유로 실패 상태에 있는 CSV는 Operator group의 대상 네임스페이스 선택이 지원되는 구성으로 변경된 후 보류 중으로 전환되거나 대상 네임스페이스 선택을 지원하도록 CSV의 설치 모드가 수정됩니다.

#### 2.4.6. 멀티 테넌시 및 Operator 공동 배치

이 가이드에서는 OLM(Operator Lifecycle Manager)의 멀티 테넌시 및 Operator 공동 배치에 대해 간단히 설명합니다.

#### 2.4.6.1. 네임스페이스에 Operator 공동 배치

OLM(Operator Lifecycle Manager)은 동일한 네임스페이스에 설치된 OLM 관리 Operator를 처리합니다. 즉, `서브스크립션` 리소스가 관련 Operator와 동일한 네임스페이스에 배치됩니다. 실제로 관련이 없는 경우에도 OLM은 해당 버전 및 업데이트 정책 중 하나가 업데이트될 때 해당 상태를 고려합니다.

이 기본 동작은 다음 두 가지 방법으로 발생합니다.

보류 중인 업데이트의 `InstallPlan` 리소스에는 동일한 네임스페이스에 있는 다른 모든 Operator의 CSV(`ClusterServiceVersion`) 리소스가 포함됩니다.

동일한 네임스페이스의 모든 Operator는 동일한 업데이트 정책을 공유합니다. 예를 들어 하나의 Operator가 수동 업데이트로 설정된 경우 다른 모든 Operator 업데이트 정책도 manual로 설정됩니다.

이러한 시나리오에서는 다음과 같은 문제가 발생할 수 있습니다.

업데이트된 Operator보다 더 많은 리소스가 정의되기 때문에 Operator 업데이트에 대한 설치 계획에 대한 이유하기가 어렵습니다.

클러스터 관리자의 일반적인 요구 사항은 다른 Operator를 수동으로 업데이트하는 동안 네임스페이스에 일부 Operator를 자동으로 업데이트할 수 없습니다.

이러한 문제는 OpenShift Container Platform 웹 콘솔을 사용하여 Operator를 설치할 때 모든 네임스페이스 설치 모드를 지원하는 Operator를 기본 `openshift-operators` 글로벌 네임스페이스에 설치하므로 일반적으로 발생합니다.

클러스터 관리자는 다음 워크플로우를 사용하여 이 기본 동작을 수동으로 무시할 수 있습니다.

Operator 설치를 위한 네임스페이스를 생성합니다.

모든 네임스페이스를 감시하는 Operator group인 사용자 정의 글로벌 Operator group을 생성합니다. 이 Operator group을 방금 생성한 네임스페이스와 연결하면 설치 네임스페이스가 글로벌 네임스페이스로 만들어 모든 네임스페이스에 Operator를 설치할 수 있습니다.

설치 네임스페이스에 원하는 Operator를 설치합니다.

Operator에 종속 항목이 있는 경우 사전 생성된 네임스페이스에 종속 항목이 자동으로 설치됩니다. 결과적으로 종속성 Operator에 동일한 업데이트 정책 및 공유 설치 계획이 있는 것이 유효합니다. 자세한 절차는 "사용자 정의 네임스페이스에 글로벌 Operator 설치"를 참조하십시오.

추가 리소스

사용자 정의 네임스페이스에 글로벌 Operator 설치

다중 테넌트 클러스터의 Operator

#### 2.4.7. Operator 상태

이 가이드에서는 OLM(Operator Lifecycle Manager)에서 Operator 조건을 사용하는 방법을 간단히 설명합니다.

#### 2.4.7.1. Operator 조건 정보

OLM(Operator Lifecycle Manager)에서는 Operator의 라이프사이클을 관리하는 역할의 일부로, Operator를 정의하는 Kubernetes 리소스의 상태에서 Operator의 상태를 유추합니다.

이 접근 방식에서는 Operator가 지정된 상태에 있도록 어느 정도는 보장하지만 Operator에서 다른 방법으로는 유추할 수 없는 정보를 OLM에 보고해야 하는 경우가 많습니다. 그러면 OLM에서 이러한 정보를 사용하여 Operator의 라이프사이클을 더 효과적으로 관리할 수 있습니다.

OLM에서는 Operator에서 OLM에 조건을 보고할 수 있는 `OperatorCondition` 이라는 CRD(사용자 정의 리소스 정의)를 제공합니다. `OperatorCondition` 리소스의 `Spec.Conditions` 어레이에 있는 경우 OLM의 Operator 관리에 영향을 줄 수 있는 일련의 조건이 지원됩니다.

참고

기본적으로 `Spec.Conditions` 어레이는 사용자가 추가하거나 사용자 정의 Operator 논리의 결과로 `OperatorCondition` 오브젝트에 존재하지 않습니다.

#### 2.4.7.2. 지원되는 조건

OLM(Operator Lifecycle Manager)에서는 다음과 같은 Operator 조건을 지원합니다.

#### 2.4.7.2.1. 업그레이드 가능한 조건

`Upgradeable` Operator 조건을 사용하면 기존 CSV(클러스터 서비스 버전)가 최신 버전의 CSV로 교체되지 않습니다. 이 조건은 다음과 같은 경우 유용합니다.

Operator에서 중요한 프로세스를 시작할 예정이며 프로세스가 완료될 때까지 업그레이드해서는 안 됩니다.

Operator에서 Operator를 업그레이드하기 위해 준비하기 전에 완료해야 하는 CR(사용자 정의 리소스) 마이그레이션을 수행하고 있습니다.

중요

`Upgradeable` Operator 조건을 `False` 값으로 설정하면 Pod가 중단되지 않습니다. Pod가 중단되지 않도록 해야 하는 경우 "Pod 중단 예산을 사용하여 가동해야 하는 Pod 수" 및 "추가 리소스" 섹션의 "Graceful termination"를 참조하십시오.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorCondition
metadata:
  name: my-operator
  namespace: operators
spec:
  conditions:
  - type: Upgradeable
    status: "False"
    reason: "migration"
    message: "The Operator is performing a migration."
    lastTransitionTime: "2020-08-24T23:15:55Z"
```

1. 조건의 이름입니다.

2. `False` 값은 Operator를 업그레이드할 준비가 되지 않았음을 나타냅니다. OLM에서는 Operator의 기존 CSV를 대체하는 CSV가 `Pending` 상태가 되지 않도록 합니다. `False` 값은 클러스터 업그레이드를 차단하지 않습니다.

#### 2.4.7.3. 추가 리소스

Operator 조건 관리

Pod 중단 예산을 사용하여 가동해야 하는 Pod 수 지정

정상적인 종료

#### 2.4.8.1. 표시되는 지표

OLM(Operator Lifecycle Manager)에서는 Prometheus 기반 OpenShift Container Platform 클러스터 모니터링 스택에서 사용할 특정 OLM 관련 리소스를 표시합니다.

| 이름 | 설명 |
| --- | --- |
| `catalog_source_count` | 카탈로그 소스 수입니다. |
| `catalogsource_ready` | 카탈로그 소스의 상태. 값 `1` 은 카탈로그 소스가 `READY` 상태에 있음을 나타냅니다. 값 `0` 은 카탈로그 소스가 `READY` 상태가 아님을 나타냅니다. |
| `csv_abnormal` | CSV(클러스터 서비스 버전)를 조정할 때 CSV 버전이 `Succeeded` 이외의 상태가 될 때마다(예: 설치되지 않은 경우) 표시됩니다. `name` , `namespace` , `phase` , `reason` , `version` 라벨이 포함됩니다. 이 지표가 표시되면 Prometheus 경고가 생성됩니다. |
| `csv_count` | 성공적으로 등록된 CSV 수입니다. |
| `csv_succeeded` | CSV를 재조정할 때 CSV 버전이 `Succeeded` 상태(값 `1` )인지 아닌지(값 `0` )를 나타냅니다. `name` , `namespace` , `version` 라벨이 포함됩니다. |
| `csv_upgrade_count` | CSV 업그레이드의 단조 수입니다. |
| `install_plan_count` | 설치 계획 수입니다. |
| `installplan_warnings_total` | 설치 계획에 포함된 더 이상 사용되지 않는 리소스와 같이 리소스에서 생성한 경고의 단조 수입니다. |
| `olm_resolution_duration_seconds` | 종속성 확인 시도의 기간입니다. |
| `subscription_count` | 서브스크립션 수입니다. |
| `subscription_sync_total` | 서브스크립션 동기화의 단조 수입니다. `channel` , `installed` CSV, 서브스크립션 `name` 라벨이 포함됩니다. |

#### 2.4.9. Operator Lifecycle Manager의 Webhook 관리

Operator 작성자는 Webhook를 통해 리소스를 오브젝트 저장소에 저장하고 Operator 컨트롤러에서 이를 처리하기 전에 리소스를 가로채기, 수정, 수락 또는 거부할 수 있습니다. Operator와 함께 webhook 가 제공 될 때 OLM (Operator Lifecycle Manager)은 이러한 Webhook의 라이프 사이클을 관리할 수 있습니다.

#### 2.4.9.1. 추가 리소스

웹 후크 승인 플러그인의 유형

Kubernetes 설명서:

승인 Webhook 검증

변경 승인 Webhook

변환 Webhook

#### 2.5.1. 소프트웨어 카탈로그 정보

소프트웨어 카탈로그 는 클러스터 관리자가 Operator를 검색하고 설치하는 데 사용하는 OpenShift Container Platform의 웹 콘솔 인터페이스입니다.

한 번의 클릭으로 Operator를 클러스터 외부 소스에서 가져와서 클러스터에 설치 및 구독하고 엔지니어링 팀에서 OLM(Operator Lifecycle Manager)을 사용하여 배포 환경에서 제품을 셀프서비스로 관리할 수 있습니다.

클러스터 관리자는 다음 카테고리로 그룹화된 카탈로그에서 선택할 수 있습니다.

| 카테고리 | 설명 |
| --- | --- |
| Red Hat Operator | Red Hat에서 Red Hat 제품을 패키지 및 제공합니다. Red Hat에서 지원합니다. |
| 인증된 Operator | 선도적인 ISV(독립 소프트웨어 벤더)의 제품입니다. Red Hat은 패키지 및 제공을 위해 ISV와 협력합니다. ISV에서 지원합니다. |
| 커뮤니티 Operator | redhat-openshift-ecosystem/community-operators-prod/operators GitHub 리포지토리의 관련 담당자가 유지 관리하는 선택적 표시 소프트웨어입니다. 공식적으로 지원되지 않습니다. |
| 사용자 정의 Operator | 클러스터에 직접 추가하는 Operator입니다. 사용자 정의 Operator를 추가하지 않은 경우 사용자 정의 카테고리가 웹 콘솔 소프트웨어 카탈로그에 표시되지 않습니다. |

소프트웨어 카탈로그의 Operator는 OLM에서 실행되도록 패키지됩니다. 여기에는 Operator를 설치하고 안전하게 실행하는 데 필요한 모든 CRD, RBAC 규칙, 배포, 컨테이너 이미지가 포함된 CSV(클러스터 서비스 버전)라는 YAML 파일이 포함됩니다.

또한 해당 기능 및 지원되는 Kubernetes 버전에 대한 설명과 같이 사용자가 볼 수 있는 정보가 포함됩니다.

#### 2.5.2. 소프트웨어 카탈로그 아키텍처

소프트웨어 카탈로그 UI 구성 요소는 기본적으로 `openshift-marketplace` 네임스페이스의 OpenShift Container Platform에서 Marketplace Operator에 의해 구동됩니다.

#### 2.5.2.1. OperatorHub 사용자 정의 리소스

Marketplace Operator는 소프트웨어 카탈로그와 함께 제공되는 기본 `CatalogSource` 오브젝트를 관리하는 `cluster` 라는 `OperatorHub` CR(사용자 정의 리소스)을 관리합니다.

이 리소스를 수정하여 기본 카탈로그를 활성화하거나 비활성화할 수 있어 제한된 네트워크 환경에서 OpenShift Container Platform을 구성할 때 유용합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: OperatorHub
metadata:
  name: cluster
spec:
  disableAllDefaultSources: true
  sources: [
    {
      name: "community-operators",
      disabled: false
    }
  ]
```

1. `disableAllDefaultSources` 는 OpenShift Container Platform 설치 중 기본적으로 구성되는 모든 기본 카탈로그의 가용성을 제어하는 덮어쓰기입니다.

2. 소스에 따라 `disabled` 매개변수 값을 변경하여 기본 카탈로그를 개별적으로 비활성화합니다.

#### 2.5.3. 추가 리소스

카탈로그 소스

OLM의 Operator 설치 및 업그레이드 워크플로

Red Hat Partner Connect

### 2.6. Red Hat 제공 Operator 카탈로그

Red Hat은 기본적으로 OpenShift Container Platform에 포함된 여러 Operator 카탈로그를 제공합니다.

중요

OpenShift Container Platform 4.11부터 파일 기반 카탈로그 형식으로 기본 Red Hat 제공 Operator 카탈로그 릴리스입니다. 더 이상 사용되지 않는 SQLite 데이터베이스 형식으로 릴리스된 OpenShift Container Platform 4.6에 대한 기본 Red Hat 제공 Operator 카탈로그입니다.

SQLite 데이터베이스 형식과 관련된 `opm` 하위 명령, 플래그 및 기능은 더 이상 사용되지 않으며 향후 릴리스에서 제거됩니다. 이 기능은 계속 지원되며 더 이상 사용되지 않는 SQLite 데이터베이스 형식을 사용하는 카탈로그에 사용해야 합니다.

`opm index prune` 와 같은 SQLite 데이터베이스 형식을 사용하기 위한 `opm` 하위 명령 및 플래그는 파일 기반 카탈로그 형식에서는 작동하지 않습니다.

파일 기반 카탈로그 작업에 대한 자세한 내용은 Managing custom catalogs, Operator Framework 패키징 형식, oc-mirror 플러그인을 사용하여 연결이 끊긴 설치의 이미지 미러링 을 참조하십시오.

#### 2.6.1. Operator 카탈로그 정보

Operator 카탈로그는 OLM(Operator Lifecycle Manager)에서 쿼리하여 Operator 및 해당 종속성을 검색하고 설치할 수 있는 메타데이터 리포지토리입니다. OLM은 항상 최신 버전의 카탈로그에 있는 Operator를 설치합니다.

Operator 번들 형식을 기반으로 하는 인덱스 이미지는 컨테이너화된 카탈로그 스냅샷입니다. 일련의 Operator 매니페스트 콘텐츠에 대한 포인터의 데이터베이스를 포함하는 변경 불가능한 아티팩트입니다. 카탈로그는 인덱스 이미지를 참조하여 클러스터에서 OLM에 대한 콘텐츠를 소싱할 수 있습니다.

카탈로그가 업데이트되면 최신 버전의 Operator가 변경되고 이전 버전은 제거되거나 변경될 수 있습니다. 또한 OLM이 네트워크가 제한된 환경의 OpenShift Container Platform 클러스터에서 실행되면 최신 콘텐츠를 가져오기 위해 인터넷에서 카탈로그에 직접 액세스할 수 없습니다.

클러스터 관리자는 Red Hat에서 제공하는 카탈로그를 기반으로 또는 처음부터 자체 사용자 정의 인덱스 이미지를 생성할 수 있습니다. 이 이미지는 클러스터에서 카탈로그 콘텐츠를 소싱하는 데 사용할 수 있습니다.

자체 인덱스 이미지를 생성하고 업데이트하면 클러스터에서 사용 가능한 Operator 세트를 사용자 정의할 수 있을 뿐만 아니라 앞서 언급한 제한된 네트워크 환경 문제도 방지할 수 있습니다.

중요

Kubernetes는 후속 릴리스에서 제거된 특정 API를 주기적으로 사용하지 않습니다. 결과적으로 Operator는 API를 제거한 Kubernetes 버전을 사용하는 OpenShift Container Platform 버전에서 시작하여 제거된 API를 사용할 수 없습니다.

참고

OpenShift Container Platform 4.8 이상에서는 레거시 형식을 사용하는 사용자 지정 카탈로그를 포함하여 Operators에 대한 레거시 패키지 매니페스트 형식 에 대한 지원이 제거되었습니다.

사용자 정의 카탈로그 이미지를 생성할 때 이전 버전의 OpenShift Container Platform 4에서는 아래 명령을 사용해야 했습니다. 이 명령은 여러 릴리스에서 더 이상 사용되지 않으며 지금은 제거되었습니다.

```shell
oc adm catalog build
```

OpenShift Container Platform 4.6부터 Red Hat 제공 인덱스 이미지를 사용할 수 있으므로 카탈로그 빌더는 `opm index` 명령을 사용하여 인덱스 이미지를 관리해야 합니다.

추가 리소스

사용자 정의 카탈로그 관리

패키지 형식

연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

#### 2.6.2. Red Hat 제공 Operator 카탈로그 정보

Red Hat 제공 카탈로그 소스는 `openshift-marketplace` 네임스페이스에 기본적으로 설치되므로 모든 네임스페이스에서 카탈로그를 클러스터 전체에서 사용할 수 있습니다.

다음은 Red Hat에서 제공하는 Operator 카탈로그입니다.

| 카탈로그 | 인덱스 이미지 | 설명 |
| --- | --- | --- |
| `redhat-operators` | `registry.redhat.io/redhat/redhat-operator-index:v4.20` | Red Hat에서 Red Hat 제품을 패키지 및 제공합니다. Red Hat에서 지원합니다. |
| `certified-operators` | `registry.redhat.io/redhat/certified-operator-index:v4.20` | 선도적인 ISV(독립 소프트웨어 벤더)의 제품입니다. Red Hat은 패키지 및 제공을 위해 ISV와 협력합니다. ISV에서 지원합니다. |
| `community-operators` | `registry.redhat.io/redhat/community-operator-index:v4.20` | redhat-openshift-ecosystem/community-operators-prod/operators GitHub 리포지토리의 관련 담당자가 유지 관리하는 소프트웨어입니다. 공식적으로 지원되지 않습니다. |

클러스터 업그레이드 중에 기본 Red Hat 제공 카탈로그 소스의 인덱스 이미지 태그는 CVO(Cluster Version Operator)에서 자동으로 업데이트하여 OLM(Operator Lifecycle Manager)이 업데이트된 버전의 카탈로그를 가져옵니다.

예를 들어 OpenShift Container Platform 4.8에서 4.9로 업그레이드하는 동안 `redhat-operators` 카탈로그의 `CatalogSource` 오브젝트의 `spec.image` 필드가 업데이트됩니다.

```shell-session
registry.redhat.io/redhat/redhat-operator-index:v4.8
```

다음으로 변경합니다.

```shell-session
registry.redhat.io/redhat/redhat-operator-index:v4.9
```

### 2.7. 다중 테넌트 클러스터의 Operator

OLM(Operator Lifecycle Manager)의 기본 동작은 Operator 설치 중에 단순성을 제공하는 것을 목표로 합니다. 그러나 이 동작에는 특히 다중 테넌트 클러스터에서 유연성이 부족할 수 있습니다.

OpenShift Container Platform 클러스터의 여러 테넌트가 Operator를 사용하려면 OLM의 기본 동작을 수행하려면 관리자가 최소 권한 원칙을 위반하는 것으로 간주할 수 있는 모든 네임스페이스 모드에서 Operator를 설치해야 합니다.

다음 시나리오를 고려하여 환경 및 요구 사항에 가장 적합한 Operator 설치 워크플로를 확인합니다.

추가 리소스

일반 용어: 멀티 테넌트

다중 테넌트 Operator 관리에 대한 제한 사항

#### 2.7.1. 기본 Operator 설치 모드 및 동작

웹 콘솔을 사용하여 Operator를 관리자로 설치할 때 일반적으로 Operator의 기능에 따라 설치 모드에 대한 두 가지 선택 사항이 있습니다.

단일 네임스페이스

선택한 단일 네임스페이스에 Operator를 설치하고 해당 네임스페이스에서 Operator에서 사용할 수 있는 모든 권한을 만듭니다.

모든 네임스페이스

기본 `openshift-operators` 네임스페이스에 Operator를 설치하여 클러스터의 모든 네임스페이스를 감시하고 사용할 수 있습니다. Operator에서 요청하는 모든 권한을 모든 네임스페이스에서 사용할 수 있도록 합니다.

경우에 따라 Operator 작성자는 메타데이터를 정의하여 사용자에게 해당 Operator의 제안된 네임스페이스에 두 번째 옵션을 제공할 수 있습니다.

또한 영향을 받는 네임스페이스의 사용자는 네임스페이스의 역할에 따라 자신이 소유한 CR(사용자 정의 리소스)을 활용할 수 있는 Operator API에 액세스할 수 있습니다.

`namespace-admin` 및 `namespace-edit` 역할은 Operator API를 읽고 쓸 수 있으므로 사용할 수 있습니다.

`namespace-view` 역할은 해당 Operator의 CR 오브젝트를 읽을 수 있습니다.

Operator 자체가 선택한 네임스페이스에 설치되므로 단일 네임스페이스 모드의 경우 해당 Pod 및 서비스 계정도 있습니다. 모든 네임스페이스 모드의 경우 Operator의 권한이 모두 클러스터 역할로 자동 향상되므로 Operator에는 모든 네임스페이스에 이러한 권한이 있습니다.

추가 리소스

클러스터에 Operator 추가

설치 모드 유형

#### 2.7.2. 다중 테넌트 클러스터에 권장되는 솔루션

다중 네임스페이스 설치 모드가 존재하지만 매우 적은 Operator에서 지원합니다. 표준 All namespaces 및 Single namespace 설치 모드 간의 중간 솔루션으로 다음 워크플로를 사용하여 각 테넌트에 대해 동일한 Operator의 인스턴스를 여러 개 설치할 수 있습니다.

테넌트의 네임스페이스와 별도의 테넌트 Operator의 네임스페이스를 생성합니다.

테넌트 Operator 범위의 Operator group을 테넌트의 네임스페이스에만 생성합니다.

테넌트 Operator 네임스페이스에 Operator를 설치합니다.

결과적으로 Operator는 테넌트 Operator 네임스페이스에 상주하며 테넌트 네임스페이스를 감시하지만, 테넌트에서 Operator Pod 및 해당 서비스 계정을 볼 수 없거나 사용할 수 없습니다.

이 솔루션을 사용하면 더 나은 테넌트 분리, 리소스 사용 비용의 최소 권한 원칙, 제약 조건이 충족되도록 하는 추가 오케스트레이션을 제공합니다. 자세한 절차는 "다중 테넌트 클러스터용 Operator의 여러 인스턴스 준비"를 참조하십시오.

제한 사항 및 고려 사항

이 솔루션은 다음 제약 조건이 충족되는 경우에만 작동합니다.

동일한 Operator의 모든 인스턴스가 동일한 버전이어야 합니다.

Operator는 다른 Operator에 대한 종속성을 가질 수 없습니다.

Operator는 CRD 변환 Webhook를 제공할 수 없습니다.

중요

동일한 클러스터에서 동일한 Operator의 다른 버전을 사용할 수 없습니다. 결국 다음 조건을 충족하면 Operator의 다른 인스턴스 설치가 차단됩니다.

인스턴스가 최신 버전의 Operator가 아닙니다.

인스턴스는 클러스터에서 이미 사용 중인 최신 버전 또는 버전이 없는 이전 버전의 CRD를 제공합니다.

주의

관리자는 "클러스터 이외의 관리자가 Operator를 설치할 수 있도록 허용"에 설명된 대로 클러스터 이외의 관리자가 Operator를 직접 설치할 수 있도록 허용할 때 주의해야 합니다. 이러한 테넌트는 종속 항목이 없는 것으로 알려진 Operator의 선별된 카탈로그에만 액세스할 수 있어야 합니다.

이러한 테넌트는 CRD가 변경되지 않도록 하려면 Operator의 동일한 버전 행을 사용해야 합니다. 이를 위해서는 네임스페이스 범위 카탈로그를 사용해야 하며 글로벌 기본 카탈로그를 비활성화해야 합니다.

추가 리소스

다중 테넌트 클러스터를 위한 Operator의 여러 인스턴스 준비

비 클러스터 관리자가 Operator를 설치하도록 허용

기본 OperatorHub 카탈로그 소스 비활성화

#### 2.7.3. Operator colocation 및 Operator groups

OLM(Operator Lifecycle Manager)은 동일한 네임스페이스에 설치된 OLM 관리 Operator를 처리합니다. 즉, `서브스크립션` 리소스가 관련 Operator와 동일한 네임스페이스에 배치됩니다. 실제로 관련이 없는 경우에도 OLM은 해당 버전 및 업데이트 정책 중 하나가 업데이트될 때 해당 상태를 고려합니다.

Operator 공동 배치 및 Operator 그룹을 효과적으로 사용하는 방법에 대한 자세한 내용은 OLM(Operator Lifecycle Manager) → 멀티 테넌시 및 Operator 공동 배치를 참조하십시오.

#### 2.8.1. 사용자 정의 리소스 정의를 사용하여 Kubernetes API 확장

Operator는 Kubernetes 확장 메커니즘인 CRD(사용자 정의 리소스 정의)를 사용하므로 Operator에서 관리하는 사용자 정의 오브젝트가 네이티브 Kubernetes 오브젝트처럼 보이고 작동합니다. 이 가이드에서는 클러스터 관리자가 CRD를 생성하고 관리하여 OpenShift Container Platform 클러스터를 확장할 수 있는 방법을 설명합니다.

#### 2.8.1.1. 사용자 정의 리소스 정의

Kubernetes API에서 리소스 는 특정 종류의 API 오브젝트 컬렉션을 저장하는 끝점입니다. 예를 들어 기본 제공 `Pod` 리소스에는 `Pod` 오브젝트의 컬렉션이 포함됩니다.

CRD(사용자 정의 리소스 정의) 오브젝트는 클러스터에서 종류 라는 새로운 고유한 오브젝트 유형을 정의하고 Kubernetes API 서버에서 전체 라이프사이클을 처리하도록 합니다.

CR(사용자 정의 리소스) 오브젝트는 클러스터 관리자가 클러스터에 추가한 CRD에서 생성하므로 모든 클러스터 사용자가 새 리소스 유형을 프로젝트에 추가할 수 있습니다.

클러스터 관리자가 새 CRD를 클러스터에 추가하면 Kubernetes API 서버는 전체 클러스터 또는 단일 프로젝트(네임스페이스)에서 액세스할 수 있는 새 RESTful 리소스 경로를 생성하여 반응하고 지정된 CR을 제공하기 시작합니다.

클러스터 관리자가 다른 사용자에게 CRD에 대한 액세스 권한을 부여하려면 클러스터 역할 집계를 사용하여 `admin`, `edit` 또는 `view` 기본 클러스터 역할이 있는 사용자에게 액세스 권한을 부여할 수 있습니다. 클러스터 역할 집계를 사용하면 이러한 클러스터 역할에 사용자 정의 정책 규칙을 삽입할 수 있습니다.

이 동작은 새 리소스를 기본 제공 리소스인 것처럼 클러스터의 RBAC 정책에 통합합니다.

특히 운영자는 CRD를 필수 RBAC 정책 및 기타 소프트웨어별 논리와 함께 패키지로 제공하는 방식으로 CRD를 사용합니다. 또한 클러스터 관리자는 Operator의 라이프사이클 외부에서 클러스터에 CRD를 수동으로 추가하여 모든 사용자에게 제공할 수 있습니다.

참고

클러스터 관리자만 CRD를 생성할 수 있지만 기존 CRD에 대한 읽기 및 쓰기 권한이 있는 개발자의 경우 기존 CRD에서 CR을 생성할 수 있습니다.

#### 2.8.1.2. 사용자 정의 리소스 정의 생성

사용자 정의 리소스(CR) 오브젝트를 생성하려면 클러스터 관리자가 먼저 CRD(사용자 정의 리소스 정의)를 생성해야 합니다.

사전 요구 사항

`cluster-admin` 사용자 권한을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

프로세스

CRD를 생성하려면 다음을 수행합니다.

다음 필드 유형을 포함하는 YAML 파일을 생성합니다.

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: crontabs.stable.example.com
spec:
  group: stable.example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                cronSpec:
                  type: string
                image:
                  type: string
                replicas:
                  type: integer
  scope: Namespaced
  names:
    plural: crontabs
    singular: crontab
    kind: CronTab
    shortNames:
    - ct
```

1. `apiextensions.k8s.io/v1` API를 사용합니다.

2. 정의의 이름을 지정합니다. `group` 및 `plural` 필드의 값을 사용하는 `<plural-name>.<group>` 형식이어야 합니다.

3. API의 그룹 이름을 지정합니다. API 그룹은 논리적으로 관련된 오브젝트의 컬렉션입니다. 예를 들어 `Job` 또는 `ScheduledJob` 과 같은 배치 오브젝트는 모두 배치 API 그룹(예: `batch.api.example.com`)에 있을 수 있습니다. 조직의 FQDN(정규화된 도메인 이름)을 사용하는 것이 좋습니다.

4. URL에 사용할 버전 이름을 지정합니다. 각 API 그룹은 여러 버전(예: `v1alpha`, `v1beta`, `v1`)에 있을 수 있습니다.

5. 특정 프로젝트(`Namespaced`) 또는 클러스터의 모든 프로젝트(`Cluster`)에서 사용자 정의 오브젝트를 사용할 수 있는지 지정합니다.

6. URL에서 사용할 복수형 이름을 지정합니다. `plural` 필드는 API URL의 리소스와 동일합니다.

7. CLI 및 디스플레이에서 별칭으로 사용할 단수형 이름을 지정합니다.

8. 생성할 수 있는 오브젝트의 종류를 지정합니다. 유형은 CamelCase에 있을 수 있습니다.

9. CLI의 리소스와 일치하는 짧은 문자열을 지정합니다.

참고

기본적으로 CRD는 클러스터 범위이며 모든 프로젝트에서 사용할 수 있습니다.

CRD 오브젝트를 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

다음에 새 RESTful API 끝점이 생성됩니다.

```shell-session
/apis/<spec:group>/<spec:version>/<scope>/*/<names-plural>/...
```

예를 들어 예제 파일을 사용하면 다음 끝점이 생성됩니다.

```shell-session
/apis/stable.example.com/v1/namespaces/*/crontabs/...
```

이 끝점 URL을 사용하여 CR을 생성하고 관리할 수 있습니다. 오브젝트 종류는 생성한 CRD 오브젝트의 `spec.kind` 필드를 기반으로 합니다.

#### 2.8.1.3. 사용자 정의 리소스 정의에 대한 클러스터 역할 생성

클러스터 관리자는 기존 클러스터 범위의 CRD(사용자 정의 리소스 정의)에 권한을 부여할 수 있습니다. `admin`, `edit`, `view` 기본 클러스터 역할을 사용하는 경우 해당 규칙에 클러스터 역할 집계를 활용할 수 있습니다.

중요

이러한 각 역할에 대한 권한을 명시적으로 할당해야 합니다. 권한이 더 많은 역할은 권한이 더 적은 역할의 규칙을 상속하지 않습니다.

역할에 규칙을 할당하는 경우 권한이 더 많은 역할에 해당 동사를 할당해야 합니다. 예를 들어 보기 역할에 `get crontabs` 권한을 부여하는 경우 `edit` 및 `admin` 역할에도 부여해야 합니다.

`admin` 또는 `edit` 역할은 일반적으로 프로젝트 템플릿을 통해 프로젝트를 생성한 사용자에게 할당됩니다.

사전 요구 사항

CRD를 생성합니다.

프로세스

CRD의 클러스터 역할 정의 파일을 생성합니다. 클러스터 역할 정의는 각 클러스터 역할에 적용되는 규칙이 포함된 YAML 파일입니다. OpenShift Container Platform 컨트롤러는 지정하는 규칙을 기본 클러스터 역할에 추가합니다.

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: aggregate-cron-tabs-admin-edit
  labels:
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
rules:
- apiGroups: ["stable.example.com"]
  resources: ["crontabs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete", "deletecollection"]
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: aggregate-cron-tabs-view
  labels:
    # Add these permissions to the "view" default role.
    rbac.authorization.k8s.io/aggregate-to-view: "true"
    rbac.authorization.k8s.io/aggregate-to-cluster-reader: "true"
rules:
- apiGroups: ["stable.example.com"]
  resources: ["crontabs"]
  verbs: ["get", "list", "watch"]
```

1. `rbac.authorization.k8s.io/v1` API를 사용합니다.

2. 8

정의의 이름을 지정합니다.

3. 관리 기본 역할에 권한을 부여하려면 이 라벨을 지정합니다.

4. 편집 기본 역할에 권한을 부여하려면 이 라벨을 지정합니다.

5. 11

CRD의 그룹 이름을 지정합니다.

6. 12

이러한 규칙이 적용되는 CRD의 복수형 이름을 지정합니다.

7. 13

역할에 부여된 권한을 나타내는 동사를 지정합니다. 예를 들어 `admin` 및 `edit` 역할에는 읽기 및 쓰기 권한을 적용하고 `view` 역할에는 읽기 권한만 적용합니다.

9. `view` 기본 역할에 권한을 부여하려면 이 라벨을 지정합니다.

10. `cluster-reader` 기본 역할에 권한을 부여하려면 이 라벨을 지정합니다.

클러스터 역할을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

#### 2.8.1.4. 파일에서 사용자 정의 리소스 생성

CRD(사용자 정의 리소스 정의)가 클러스터에 추가되면 CR 사양을 사용하여 파일에서 CLI를 사용하여 CR(사용자 정의 리소스)을 생성할 수 있습니다.

사전 요구 사항

클러스터 관리자가 클러스터에 CRD를 추가했습니다.

프로세스

CR에 대한 YAML 파일을 생성합니다. 다음 예제 정의에서 `cronSpec` 및 `image` 사용자 정의 필드는 `Kind: CronTab` 의 CR에 설정됩니다. `Kind` 는 CRD 오브젝트의 `spec.kind` 필드에서 제공합니다.

```yaml
apiVersion: "stable.example.com/v1"
kind: CronTab
metadata:
  name: my-new-cron-object
  finalizers:
  - finalizer.stable.example.com
spec:
  cronSpec: "* * * * /5"
  image: my-awesome-cron-image
```

1. CRD에서 그룹 이름 및 API 버전(이름/버전)을 지정합니다.

2. CRD에 유형을 지정합니다.

3. 오브젝트의 이름을 지정합니다.

4. 해당하는 경우 오브젝트의 종료자 를 지정합니다. 종료자를 사용하면 컨트롤러에서 오브젝트를 삭제하기 전에 완료해야 하는 조건을 구현할 수 있습니다.

5. 오브젝트 유형별 조건을 지정합니다.

파일을 생성한 후 오브젝트를 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

#### 2.8.1.5. 사용자 정의 리소스 검사

CLI를 사용하여 클러스터에 존재하는 CR(사용자 정의 리소스) 오브젝트를 검사할 수 있습니다.

사전 요구 사항

CR 오브젝트는 액세스할 수 있는 네임스페이스에 있습니다.

프로세스

특정 종류의 CR에 대한 정보를 얻으려면 다음을 실행합니다.

```shell-session
$ oc get <kind>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc get crontab
```

```shell-session
NAME                 KIND
my-new-cron-object   CronTab.v1.stable.example.com
```

리소스 이름은 대소문자를 구분하지 않으며 CRD에 정의된 단수형 또는 복수형 양식이나 짧은 이름을 사용할 수 있습니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc get crontabs
```

```shell-session
$ oc get crontab
```

```shell-session
$ oc get ct
```

CR의 원시 YAML 데이터를 볼 수도 있습니다.

```shell-session
$ oc get <kind> -o yaml
```

예를 들면 다음과 같습니다.

```shell-session
$ oc get ct -o yaml
```

```shell-session
apiVersion: v1
items:
- apiVersion: stable.example.com/v1
  kind: CronTab
  metadata:
    clusterName: ""
    creationTimestamp: 2017-05-31T12:56:35Z
    deletionGracePeriodSeconds: null
    deletionTimestamp: null
    name: my-new-cron-object
    namespace: default
    resourceVersion: "285"
    selfLink: /apis/stable.example.com/v1/namespaces/default/crontabs/my-new-cron-object
    uid: 9423255b-4600-11e7-af6a-28d2447dc82b
  spec:
    cronSpec: '* * * * /5'
    image: my-awesome-cron-image
```

1. 2

오브젝트를 생성하는 데 사용한 YAML의 사용자 정의 데이터가 표시됩니다.

#### 2.8.2. 사용자 정의 리소스 정의에서 리소스 관리

이 가이드에서는 개발자가 CRD(사용자 정의 리소스 정의)에서 제공하는 CR(사용자 정의 리소스)을 관리하는 방법을 설명합니다.

#### 2.8.2.1. 사용자 정의 리소스 정의

Kubernetes API에서 리소스 는 특정 종류의 API 오브젝트 컬렉션을 저장하는 끝점입니다. 예를 들어 기본 제공 `Pod` 리소스에는 `Pod` 오브젝트의 컬렉션이 포함됩니다.

CRD(사용자 정의 리소스 정의) 오브젝트는 클러스터에서 종류 라는 새로운 고유한 오브젝트 유형을 정의하고 Kubernetes API 서버에서 전체 라이프사이클을 처리하도록 합니다.

CR(사용자 정의 리소스) 오브젝트는 클러스터 관리자가 클러스터에 추가한 CRD에서 생성하므로 모든 클러스터 사용자가 새 리소스 유형을 프로젝트에 추가할 수 있습니다.

특히 운영자는 CRD를 필수 RBAC 정책 및 기타 소프트웨어별 논리와 함께 패키지로 제공하는 방식으로 CRD를 사용합니다. 또한 클러스터 관리자는 Operator의 라이프사이클 외부에서 클러스터에 CRD를 수동으로 추가하여 모든 사용자에게 제공할 수 있습니다.

참고

클러스터 관리자만 CRD를 생성할 수 있지만 기존 CRD에 대한 읽기 및 쓰기 권한이 있는 개발자의 경우 기존 CRD에서 CR을 생성할 수 있습니다.

#### 2.8.2.2. 파일에서 사용자 정의 리소스 생성

CRD(사용자 정의 리소스 정의)가 클러스터에 추가되면 CR 사양을 사용하여 파일에서 CLI를 사용하여 CR(사용자 정의 리소스)을 생성할 수 있습니다.

사전 요구 사항

클러스터 관리자가 클러스터에 CRD를 추가했습니다.

프로세스

CR에 대한 YAML 파일을 생성합니다. 다음 예제 정의에서 `cronSpec` 및 `image` 사용자 정의 필드는 `Kind: CronTab` 의 CR에 설정됩니다. `Kind` 는 CRD 오브젝트의 `spec.kind` 필드에서 제공합니다.

```yaml
apiVersion: "stable.example.com/v1"
kind: CronTab
metadata:
  name: my-new-cron-object
  finalizers:
  - finalizer.stable.example.com
spec:
  cronSpec: "* * * * /5"
  image: my-awesome-cron-image
```

1. CRD에서 그룹 이름 및 API 버전(이름/버전)을 지정합니다.

2. CRD에 유형을 지정합니다.

3. 오브젝트의 이름을 지정합니다.

4. 해당하는 경우 오브젝트의 종료자 를 지정합니다. 종료자를 사용하면 컨트롤러에서 오브젝트를 삭제하기 전에 완료해야 하는 조건을 구현할 수 있습니다.

5. 오브젝트 유형별 조건을 지정합니다.

파일을 생성한 후 오브젝트를 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

#### 2.8.2.3. 사용자 정의 리소스 검사

CLI를 사용하여 클러스터에 존재하는 CR(사용자 정의 리소스) 오브젝트를 검사할 수 있습니다.

사전 요구 사항

CR 오브젝트는 액세스할 수 있는 네임스페이스에 있습니다.

프로세스

특정 종류의 CR에 대한 정보를 얻으려면 다음을 실행합니다.

```shell-session
$ oc get <kind>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc get crontab
```

```shell-session
NAME                 KIND
my-new-cron-object   CronTab.v1.stable.example.com
```

리소스 이름은 대소문자를 구분하지 않으며 CRD에 정의된 단수형 또는 복수형 양식이나 짧은 이름을 사용할 수 있습니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc get crontabs
```

```shell-session
$ oc get crontab
```

```shell-session
$ oc get ct
```

CR의 원시 YAML 데이터를 볼 수도 있습니다.

```shell-session
$ oc get <kind> -o yaml
```

예를 들면 다음과 같습니다.

```shell-session
$ oc get ct -o yaml
```

```shell-session
apiVersion: v1
items:
- apiVersion: stable.example.com/v1
  kind: CronTab
  metadata:
    clusterName: ""
    creationTimestamp: 2017-05-31T12:56:35Z
    deletionGracePeriodSeconds: null
    deletionTimestamp: null
    name: my-new-cron-object
    namespace: default
    resourceVersion: "285"
    selfLink: /apis/stable.example.com/v1/namespaces/default/crontabs/my-new-cron-object
    uid: 9423255b-4600-11e7-af6a-28d2447dc82b
  spec:
    cronSpec: '* * * * /5'
    image: my-awesome-cron-image
```

1. 2

오브젝트를 생성하는 데 사용한 YAML의 사용자 정의 데이터가 표시됩니다.

### 3.1. 설치된 Operator에서 애플리케이션 생성

이 가이드에서는 개발자에게 OpenShift Container Platform 웹 콘솔을 사용하여 설치한 Operator에서 애플리케이션을 생성하는 예제를 안내합니다.

#### 3.1.1. Operator를 사용하여 etcd 클러스터 생성

이 절차에서는 OLM(Operator Lifecycle Manager)에서 관리하는 etcd Operator를 사용하여 새 etcd 클러스터를 생성하는 과정을 안내합니다.

사전 요구 사항

OpenShift Container Platform 4.20 클러스터에 액세스할 수 있습니다.

관리자가 클러스터 수준에 etcd Operator를 이미 설치했습니다.

프로세스

이 절차를 위해 OpenShift Container Platform 웹 콘솔에 새 프로젝트를 생성합니다. 이 예제에서는 `my-etcd` 라는 프로젝트를 사용합니다.

에코시스템 → 설치된 Operator 페이지로 이동합니다. 이 페이지에는 클러스터 관리자가 클러스터에 설치하여 사용할 수 있는 Operator가 CSV(클러스터 서비스 버전) 목록으로 표시됩니다. CSV는 Operator에서 제공하는 소프트웨어를 시작하고 관리하는 데 사용됩니다.

작은 정보

다음을 사용하여 CLI에서 이 목록을 가져올 수 있습니다.

```shell-session
$ oc get csv
```

자세한 내용과 사용 가능한 작업을 확인하려면 설치된 Operator 페이지에서 etcd Operator를 클릭합니다.

이 Operator에서는 제공된 API 아래에 표시된 것과 같이 etcd 클러스터 (`EtcdCluster` 리소스)용 하나를 포함하여 새로운 리소스 유형 세 가지를 사용할 수 있습니다. 이러한 오브젝트는 내장된 네이티브 Kubernetes 오브젝트(예: `Deployment` 또는 `ReplicaSet`)와 비슷하게 작동하지만 etcd 관리와 관련된 논리가 포함됩니다.

새 etcd 클러스터를 생성합니다.

etcd 클러스터 API 상자에서 인스턴스 생성 을 클릭합니다.

다음 페이지에서는 클러스터 크기와 같은 `EtcdCluster` 오브젝트의 최소 시작 템플릿을 수정할 수 있습니다. 지금은 생성 을 클릭하여 종료하십시오. 그러면 Operator에서 새 etcd 클러스터의 Pod, 서비스 및 기타 구성 요소를 가동합니다.

예제 etcd 클러스터를 클릭한 다음 리소스 탭을 클릭하여 Operator에 의해 자동으로 생성 및 구성된 여러 리소스가 프로젝트에 포함되어 있는지 확인합니다.

프로젝트의 다른 Pod에서 데이터베이스에 액세스할 수 있도록 Kubernetes 서비스가 생성되었는지 확인합니다.

지정된 프로젝트에서 `edit` 역할을 가진 모든 사용자는 클라우드 서비스와 마찬가지로 셀프 서비스 방식으로 프로젝트에 이미 생성된 Operator에서 관리하는 애플리케이션 인스턴스(이 예제의 etcd 클러스터)를 생성, 관리, 삭제할 수 있습니다. 이 기능을 사용하여 추가 사용자를 활성화하려면 프로젝트 관리자가 다음 명령을 사용하여 역할을 추가하면 됩니다.

```shell-session
$ oc policy add-role-to-user edit <user> -n <target_project>
```

이제 Pod가 비정상적인 상태가 되거나 클러스터의 다른 노드로 마이그레이션되면 오류에 반응하고 데이터를 재조정할 etcd 클러스터가 생성되었습니다. 가장 중요한 점은 적절한 액세스 권한이 있는 클러스터 관리자 또는 개발자가 애플리케이션과 함께 데이터베이스를 쉽게 사용할 수 있다는 점입니다.

### 3.2. 네임스페이스에 Operator 설치

클러스터 관리자가 계정에 Operator 설치 권한을 위임한 경우 셀프서비스 방식으로 Operator를 설치하고 네임스페이스에 등록할 수 있습니다.

#### 3.2.1. 사전 요구 사항

클러스터 관리자는 셀프서비스 Operator를 네임스페이스에 설치할 수 있도록 OpenShift Container Platform 사용자 계정에 특정 권한을 추가해야 합니다. 자세한 내용은 비 클러스터 관리자가 Operator를 설치할 수 있도록 허용 을 참조하십시오.

#### 3.2.2. 소프트웨어 카탈로그에서 Operator 설치 정보

소프트웨어 카탈로그는 Operator를 검색하는 사용자 인터페이스입니다. 이는 클러스터에 Operator를 설치하고 관리하는 OLM(Operator Lifecycle Manager)과 함께 작동합니다.

적절한 권한이 있는 사용자는 OpenShift Container Platform 웹 콘솔 또는 CLI를 사용하여 소프트웨어 카탈로그에서 Operator를 설치할 수 있습니다.

설치하는 동안 Operator의 다음 초기 설정을 결정해야합니다.

설치 모드

Operator를 설치할 특정 네임스페이스를 선택합니다.

업데이트 채널

여러 채널을 통해 Operator를 사용할 수있는 경우 구독할 채널을 선택할 수 있습니다. 예를 들어, stable 채널에서 배치하려면 (사용 가능한 경우) 목록에서 해당 채널을 선택합니다.

승인 전략

자동 또는 수동 업데이트를 선택할 수 있습니다.

설치된 Operator에 대해 자동 업데이트를 선택하는 경우 선택한 채널에 해당 Operator의 새 버전이 제공되면 OLM(Operator Lifecycle Manager)에서 Operator의 실행 중인 인스턴스를 개입 없이 자동으로 업그레이드합니다.

수동 업데이트를 선택하면 최신 버전의 Operator가 사용 가능할 때 OLM이 업데이트 요청을 작성합니다. 클러스터 관리자는 Operator를 새 버전으로 업데이트하려면 OLM 업데이트 요청을 수동으로 승인해야 합니다.

소프트웨어 카탈로그 이해

#### 3.2.3. 웹 콘솔을 사용하여 소프트웨어 카탈로그에서 설치

OpenShift Container Platform 웹 콘솔을 사용하여 소프트웨어 카탈로그에서 Operator를 설치하고 구독할 수 있습니다.

사전 요구 사항

Operator 설치 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

프로세스

웹 콘솔에서 Ecosystem → Software Catalog 페이지로 이동합니다.

원하는 Operator를 찾으려면 키워드를 Filter by keyword 상자에 입력하거나 스크롤합니다. 예를 들어 Kubernetes Operator의 고급 클러스터 관리 기능을 찾으려면 `advanced` 를 입력합니다.

인프라 기능 에서 옵션을 필터링할 수 있습니다. 예를 들어, 연결이 끊긴 환경 (제한된 네트워크 환경이라고도 함)에서 작업하는 Operator를 표시하려면 Disconnected 를 선택합니다.

Operator를 선택하여 추가 정보를 표시합니다.

참고

커뮤니티 Operator를 선택하면 Red Hat이 커뮤니티 Operator를 인증하지 않는다고 경고합니다. 계속하기 전에 경고를 확인해야합니다.

Operator에 대한 정보를 확인하고 Install 을 클릭합니다.

Operator 설치 페이지에서 Operator 설치를 구성합니다.

특정 버전의 Operator를 설치하려면 목록에서 업데이트 채널 및 버전을 선택합니다. 보유할 수 있는 채널에서 다양한 버전의 Operator를 검색하고 해당 채널 및 버전의 메타데이터를 보고 설치할 정확한 버전을 선택할 수 있습니다.

참고

버전 선택 기본값은 선택한 채널의 최신 버전입니다. 채널의 최신 버전이 선택되어 있으면 기본적으로 자동 승인 전략이 활성화됩니다. 그렇지 않으면 선택한 채널의 최신 버전을 설치하지 않는 경우 수동 승인이 필요합니다.

수동 승인을 사용하여 Operator를 설치하면 네임스페이스 내에 설치된 모든 Operator가 수동 승인 전략과 함께 작동하고 모든 Operator가 함께 업데이트됩니다. Operator를 독립적으로 업데이트하려면 Operator를 별도의 네임스페이스에 설치합니다.

Operator를 설치할 특정 단일 네임스페이스를 선택합니다. Operator는 이 단일 네임 스페이스에서만 모니터링 및 사용할 수 있게 됩니다.

토큰 인증이 활성화된 클라우드 공급자의 클러스터의 경우:

클러스터가 웹 콘솔에서 AWS Security Token Service(TS 모드)를 사용하는 경우 역할 ARN 필드에 서비스 계정의 AWS IAM 역할의 Amazon Resource Name(ARN)을 입력합니다. 역할의 ARN을 생성하려면 AWS 계정 준비에 설명된 절차를 따르십시오.

클러스터에서 Microsoft Entra Workload ID(웹 콘솔에서 워크로드 ID / Federated Identity Mode)를 사용하는 경우 적절한 필드에 클라이언트 ID, 테넌트 ID 및 구독 ID를 추가합니다.

클러스터가 Google Cloud Platform Workload Identity(웹 콘솔에서 GCP Workload Identity/Federated Identity Mode)를 사용하는 경우 적절한 필드에 프로젝트 번호, 풀 ID, 공급자 ID 및 서비스 계정 이메일을 추가합니다.

업데이트 승인 의 경우 자동 또는 수동 승인 전략을 선택합니다.

중요

웹 콘솔에서 클러스터가 AWS STS, Microsoft Entra Workload ID 또는 GCP Workload Identity를 사용함을 표시하는 경우 업데이트 승인을

Manual 로 설정해야 합니다.

업데이트에 대한 자동 승인이 있는 서브스크립션은 업데이트하기 전에 권한을 변경할 수 있으므로 권장되지 않습니다. 업데이트에 대한 수동 승인이 있는 서브스크립션을 통해 관리자는 최신 버전의 권한을 확인하고 필요한 단계를 수행한 다음 업데이트할 수 있습니다.

이 OpenShift Container Platform 클러스터에서 선택한 네임스페이스에서 Operator를 사용할 수 있도록 하려면 설치를 클릭합니다.

수동 승인 전략을 선택한 경우 설치 계획을 검토하고 승인할 때까지 서브스크립션의 업그레이드 상태가 업그레이드 중 으로 유지됩니다.

Install Plan 페이지에서 승인 한 후 subscription 업그레이드 상태가 Up to date 로 이동합니다.

자동 승인 전략을 선택한 경우 업그레이드 상태가 개입 없이 최신 상태로 확인되어야 합니다.

검증

서브스크립션 업그레이드 상태가 최신이면

Ecosystem → Installed Operators 를 선택하여 설치된 Operator의 CSV(클러스터 서비스 버전)가 최종적으로 표시되는지 확인합니다. Status 는 결국 관련 네임스페이스에서 Succeeded 로 확인되어야 합니다.

참고

All namespaces…​ 설치 모드의 경우 `openshift-operators` 네임스페이스에서 상태는 Succeeded 로 확인되지만 다른 네임스페이스에서 확인하는 경우 상태가 복사 됩니다.

그렇지 않은 경우 다음을 수행합니다.

작업 부하 → Pod 페이지에서 `openshift-operators` 프로젝트(또는 특정 네임스페이스… ​ 설치 모드가 선택된 경우 다른 관련 네임스페이스)의 모든 Pod에서 로그를 확인하여 문제를 보고하고 추가적으로 문제를 해결합니다.

Operator가 설치되면 메타데이터에서 설치된 채널 및 버전을 나타냅니다.

참고

이 카탈로그 컨텍스트에서 채널 및 버전 드롭다운 메뉴를 계속 사용하여 다른 버전 메타데이터를 볼 수 있습니다.

#### 3.2.4. CLI를 사용하여 소프트웨어 카탈로그에서 설치

OpenShift Container Platform 웹 콘솔을 사용하는 대신 CLI를 사용하여 소프트웨어 카탈로그에서 Operator를 설치할 수 있습니다. 아래 명령을 사용하여 `Subscription` 개체를 만들거나 업데이트합니다.

```shell
oc
```

`SingleNamespace` 설치 모드의 경우 관련 네임스페이스에 적절한 Operator group이 있는지 확인해야 합니다. `OperatorGroup` 오브젝트로 정의되는 Operator group에서 Operator group과 동일한 네임스페이스에 있는 모든 Operator에 대해 필요한 RBAC 액세스 권한을 생성할 대상 네임스페이스를 선택합니다.

작은 정보

대부분의 경우 `SingleNamespace` 모드를 선택할 때 `OperatorGroup` 및 `Subscription` 오브젝트 생성을 자동으로 처리하는 등 백그라운드에서 작업을 자동화하기 때문에 이 절차의 웹 콘솔 방법이 권장됩니다.

사전 요구 사항

Operator 설치 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

소프트웨어 카탈로그에서 클러스터에서 사용할 수 있는 Operator 목록을 확인합니다.

```shell-session
$ oc get packagemanifests -n openshift-marketplace
```

```shell-session
NAME                               CATALOG               AGE
3scale-operator                    Red Hat Operators     91m
advanced-cluster-management        Red Hat Operators     91m
amq7-cert-manager                  Red Hat Operators     91m
# ...
couchbase-enterprise-certified     Certified Operators   91m
crunchy-postgres-operator          Certified Operators   91m
mongodb-enterprise                 Certified Operators   91m
# ...
etcd                               Community Operators   91m
jaeger                             Community Operators   91m
kubefed                            Community Operators   91m
# ...
```

필요한 Operator의 카탈로그를 기록해 둡니다.

필요한 Operator를 검사하여 지원되는 설치 모드 및 사용 가능한 채널을 확인합니다.

```shell-session
$ oc describe packagemanifests <operator_name> -n openshift-marketplace
```

```shell-session
# ...
Kind:         PackageManifest
# ...
      Install Modes:
        Supported:  true
        Type:       OwnNamespace
        Supported:  true
        Type:       SingleNamespace
        Supported:  false
        Type:       MultiNamespace
        Supported:  true
        Type:       AllNamespaces
# ...
    Entries:
      Name:       example-operator.v3.7.11
      Version:    3.7.11
      Name:       example-operator.v3.7.10
      Version:    3.7.10
    Name:         stable-3.7
# ...
   Entries:
      Name:         example-operator.v3.8.5
      Version:      3.8.5
      Name:         example-operator.v3.8.4
      Version:      3.8.4
    Name:           stable-3.8
  Default Channel:  stable-3.8
```

1. 지원되는 설치 모드를 나타냅니다.

2. 3

채널 이름 예.

4. 하나가 지정되지 않은 경우 기본적으로 선택한 채널입니다.

작은 정보

다음 명령을 실행하여 Operator 버전 및 채널 정보를 YAML 형식으로 출력할 수 있습니다.

```shell-session
$ oc get packagemanifests <operator_name> -n <catalog_namespace> -o yaml
```

네임스페이스에 두 개 이상의 카탈로그가 설치된 경우 다음 명령을 실행하여 특정 카탈로그에서 사용 가능한 버전 및 Operator 채널을 조회합니다.

```shell-session
$ oc get packagemanifest \
   --selector=catalog=<catalogsource_name> \
   --field-selector metadata.name=<operator_name> \
   -n <catalog_namespace> -o yaml
```

중요

Operator 카탈로그를 지정하지 않으면 다음 조건이 충족되는 경우 및 아래 명령을 실행하면 예기치 않은 카탈로그에서 패키지를 반환할 수 있습니다.

```shell
oc get packagemanifest
```

```shell
oc describe packagemanifest
```

여러 카탈로그가 동일한 네임스페이스에 설치됩니다.

카탈로그에는 동일한 이름의 Operator 또는 Operator가 포함됩니다.

설치하려는 Operator가 `AllNamespaces` 설치 모드를 지원하며 이 모드를 사용하도록 선택한 경우 `openshift-operators` 네임스페이스에 기본적으로 `global-operators` 라는 적절한 Operator 그룹이 있으므로 이 단계를 건너뜁니다.

설치하려는 Operator가 `SingleNamespace` 설치 모드를 지원하며 이 모드를 사용하도록 선택한 경우 관련 네임스페이스에 적절한 Operator group이 있는지 확인해야 합니다. 존재하지 않는 경우 다음 단계에 따라 생성을 생성할 수 있습니다.

중요

네임스페이스당 하나의 Operator 그룹만 있을 수 있습니다. 자세한 내용은 “Operator 그룹"을 참조하십시오.

`SingleNamespace` 설치 모드의 경우 `OperatorGroup` 오브젝트 YAML 파일(예: `operatorgroup.yaml`)을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: <operatorgroup_name>
  namespace: <namespace>
spec:
  targetNamespaces:
  - <namespace>
```

1. 2

`SingleNamespace` 설치 모드의 경우 `metadata.namespace` 및 `spec.targetNamespaces` 필드 모두에 동일한 `<namespace>` 값을 사용합니다.

`OperatorGroup` 개체를 생성합니다.

```shell-session
$ oc apply -f operatorgroup.yaml
```

Operator에 네임스페이스를 서브스크립션할 `Subscription` 오브젝트를 생성합니다.

`Subscription` 오브젝트에 대한 YAML 파일을 생성합니다(예: `subscription.yaml`).

참고

특정 버전의 Operator를 구독하려면 `startingCSV` 필드를 원하는 버전으로 설정하고 이후 버전이 카탈로그에 있는 경우 Operator가 자동으로 업그레이드되지 않도록 `installPlanApproval` 필드를 `Manual` 로 설정합니다. 자세한 내용은 다음 "특정 시작 Operator 버전이 있는 `서브스크립션` 오브젝트 예"를 참조하십시오.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: <subscription_name>
  namespace: <namespace_per_install_mode>
spec:
  channel: <channel_name>
  name: <operator_name>
  source: <catalog_name>
  sourceNamespace: <catalog_source_namespace>
  config:
    env:
    - name: ARGS
      value: "-v=10"
    envFrom:
    - secretRef:
        name: license-secret
    volumes:
    - name: <volume_name>
      configMap:
        name: <configmap_name>
    volumeMounts:
    - mountPath: <directory_name>
      name: <volume_name>
    tolerations:
    - operator: "Exists"
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    nodeSelector:
      foo: bar
```

1. 기본 `AllNamespaces` 설치 모드 사용량의 경우 `openshift-operators` 네임스페이스를 지정합니다. 또는 사용자 지정 글로벌 네임스페이스를 생성한 경우 지정할 수 있습니다. `SingleNamespace` 설치 모드 사용의 경우 관련 단일 네임스페이스를 지정합니다.

2. 등록할 채널의 이름입니다.

3. 등록할 Operator의 이름입니다.

4. Operator를 제공하는 카탈로그 소스의 이름입니다.

5. 카탈로그 소스의 네임스페이스입니다. 기본 소프트웨어 카탈로그 소스에는 `openshift-marketplace` 를 사용합니다.

6. `env` 매개변수는 OLM에서 생성한 Pod의 모든 컨테이너에 있어야 하는 환경 변수 목록을 정의합니다.

7. `envFrom` 매개 변수는 컨테이너에서 환경 변수를 채울 소스 목록을 정의합니다.

8. `volumes` 매개변수는 OLM에서 생성한 Pod에 있어야 하는 볼륨 목록을 정의합니다.

9. `volumeMounts` 매개변수는 OLM에서 생성한 Pod의 모든 컨테이너에 있어야 하는 볼륨 마운트 목록을 정의합니다. `volumeMount` 가 존재하지 않는 `볼륨` 을 참조하는 경우 OLM에서 Operator를 배포하지 못합니다.

10. `tolerations` 매개변수는 OLM에서 생성한 Pod의 허용 오차 목록을 정의합니다.

11. `resources` 매개변수는 OLM에서 생성한 Pod의 모든 컨테이너에 대한 리소스 제약 조건을 정의합니다.

12. `nodeSelector` 매개변수는 OLM에서 생성한 Pod에 대한 `NodeSelector` 를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: example-operator
  namespace: example-operator
spec:
  channel: stable-3.7
  installPlanApproval: Manual
  name: example-operator
  source: custom-operators
  sourceNamespace: openshift-marketplace
  startingCSV: example-operator.v3.7.10
```

1. 지정된 버전이 카탈로그의 이후 버전으로 대체될 경우 승인 전략을 `Manual` 로 설정합니다. 이 계획에서는 이후 버전으로 자동 업그레이드할 수 없으므로 시작 CSV에서 설치를 완료하려면 수동 승인이 필요합니다.

2. Operator CSV의 특정 버전을 설정합니다.

AWS(Amazon Web Services) Security Token Service(STS), Microsoft Entra Workload ID 또는 Google Cloud Platform Workload Identity와 같이 토큰 인증이 활성화된 클라우드 공급자의 클러스터의 경우 다음 단계를 수행하여 `서브스크립션` 오브젝트를 구성합니다.

`Subscription` 오브젝트가 수동 업데이트 승인으로 설정되어 있는지 확인합니다.

```yaml
kind: Subscription
# ...
spec:
  installPlanApproval: Manual
```

1. 업데이트에 대한 자동 승인이 있는 서브스크립션은 업데이트하기 전에 권한을 변경할 수 있으므로 권장되지 않습니다. 업데이트에 대한 수동 승인이 있는 서브스크립션을 통해 관리자는 최신 버전의 권한을 확인하고 필요한 단계를 수행한 다음 업데이트할 수 있습니다.

`Subscription` 오브젝트의 `config` 섹션에 관련 클라우드 공급자별 필드를 포함합니다.

클러스터가 AWS STS 모드에 있는 경우 다음 필드를 포함합니다.

```yaml
kind: Subscription
# ...
spec:
  config:
    env:
    - name: ROLEARN
      value: "<role_arn>"
```

1. 역할 ARN 세부 정보를 포함합니다.

클러스터가 Workload ID 모드에 있는 경우 다음 필드를 포함합니다.

```yaml
kind: Subscription
# ...
spec:
 config:
   env:
   - name: CLIENTID
     value: "<client_id>"
   - name: TENANTID
     value: "<tenant_id>"
   - name: SUBSCRIPTIONID
     value: "<subscription_id>"
```

1. 클라이언트 ID를 포함합니다.

2. 테넌트 ID를 포함합니다.

3. 서브스크립션 ID를 포함합니다.

클러스터가 GCP Workload Identity 모드에 있는 경우 다음 필드를 포함합니다.

```yaml
kind: Subscription
# ...
spec:
 config:
   env:
   - name: AUDIENCE
     value: "<audience_url>"
   - name: SERVICE_ACCOUNT_EMAIL
     value: "<service_account_email>"
```

다음과 같습니다.

`<audience>`

GCP Workload Identity를 설정할 때 관리자가 Google Cloud에서 생성한 `AUDIENCE` 값은 다음 형식의 사전 형식의 URL이어야 합니다.

```plaintext
//iam.googleapis.com/projects/<project_number>/locations/global/workloadIdentityPools/<pool_id>/providers/<provider_id>
```

`<service_account_email>`

`SERVICE_ACCOUNT_EMAIL` 값은 Operator 작업 중에 가장하는 Google Cloud 서비스 계정 이메일입니다. 예를 들면 다음과 같습니다.

```plaintext
<service_account_name>@<project_id>.iam.gserviceaccount.com
```

다음 명령을 실행하여 서브스크립션 오브젝트를 생성합니다.

```shell-session
$ oc apply -f subscription.yaml
```

`installPlanApproval` 필드를 `Manual` 로 설정하는 경우 보류 중인 설치 계획을 수동으로 승인하여 Operator 설치를 완료합니다. 자세한 내용은 "Manually approving a pending Operator update"를 참조하십시오.

이 시점에서 OLM은 이제 선택한 Operator를 인식합니다. Operator의 CSV(클러스터 서비스 버전)가 대상 네임스페이스에 표시되고 Operator에서 제공하는 API를 생성에 사용할 수 있어야 합니다.

검증

다음 명령을 실행하여 설치된 Operator의 `Subscription` 오브젝트의 상태를 확인합니다.

```shell-session
$ oc describe subscription <subscription_name> -n <namespace>
```

`SingleNamespace` 설치 모드에 대한 Operator group을 생성한 경우 다음 명령을 실행하여 `OperatorGroup` 오브젝트의 상태를 확인합니다.

```shell-session
$ oc describe operatorgroup <operatorgroup_name> -n <namespace>
```

추가 리소스

Operator groups

채널 이름

추가 리소스

보류 중인 Operator 업데이트 수동 승인

### 4.1. 클러스터에 Operator 추가

OLM(Operator Lifecycle Manager)을 사용하여 클러스터 관리자는 OLM 기반 Operator를 OpenShift Container Platform 클러스터에 설치할 수 있습니다.

참고

OLM에서 동일한 네임스페이스에 배치된 설치된 Operator에 대한 업데이트를 처리하는 방법과 사용자 정의 글로벌 Operator 그룹을 사용하여 Operator를 설치하는 대체 방법은 Multitenancy 및 Operator colocation 을 참조하십시오.

#### 4.1.1. 소프트웨어 카탈로그에서 Operator 설치 정보

소프트웨어 카탈로그는 Operator를 검색하는 사용자 인터페이스입니다. 이는 클러스터에 Operator를 설치하고 관리하는 OLM(Operator Lifecycle Manager)과 함께 작동합니다.

클러스터 관리자는 OpenShift Container Platform 웹 콘솔 또는 CLI를 사용하여 소프트웨어 카탈로그에서 Operator를 설치할 수 있습니다. 그런 다음 Operator를 하나 이상의 네임 스페이스에 가입시켜 Operator를 클러스터의 개발자가 사용할 수 있도록 합니다.

설치하는 동안 Operator의 다음 초기 설정을 결정해야합니다.

설치 모드

All namespaces on the cluster (default) 를 선택하여 Operator를 모든 네임 스페이스에 설치하거나 사용 가능한 경우 개별 네임 스페이스를 선택하여 선택한 네임 스페이스에만 Operator를 설치합니다. 이 예에서는 모든 사용자와 프로젝트 Operator를 사용할 수 있도록 All namespaces…​ 선택합니다.

업데이트 채널

여러 채널을 통해 Operator를 사용할 수있는 경우 구독할 채널을 선택할 수 있습니다. 예를 들어, stable 채널에서 배치하려면 (사용 가능한 경우) 목록에서 해당 채널을 선택합니다.

승인 전략

자동 또는 수동 업데이트를 선택할 수 있습니다.

설치된 Operator에 대해 자동 업데이트를 선택하는 경우 선택한 채널에 해당 Operator의 새 버전이 제공되면 OLM(Operator Lifecycle Manager)에서 Operator의 실행 중인 인스턴스를 개입 없이 자동으로 업그레이드합니다.

수동 업데이트를 선택하면 최신 버전의 Operator가 사용 가능할 때 OLM이 업데이트 요청을 작성합니다. 클러스터 관리자는 Operator를 새 버전으로 업데이트하려면 OLM 업데이트 요청을 수동으로 승인해야 합니다.

추가 리소스

소프트웨어 카탈로그 이해

#### 4.1.2. 웹 콘솔을 사용하여 소프트웨어 카탈로그에서 설치

OpenShift Container Platform 웹 콘솔을 사용하여 소프트웨어 카탈로그에서 Operator를 설치하고 구독할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

프로세스

웹 콘솔에서 Ecosystem → Software Catalog 페이지로 이동합니다.

원하는 Operator를 찾으려면 키워드를 Filter by keyword 상자에 입력하거나 스크롤합니다. 예를 들어 Kubernetes Operator의 고급 클러스터 관리 기능을 찾으려면 `advanced` 를 입력합니다.

인프라 기능 에서 옵션을 필터링할 수 있습니다. 예를 들어, 연결이 끊긴 환경 (제한된 네트워크 환경이라고도 함)에서 작업하는 Operator를 표시하려면 Disconnected 를 선택합니다.

Operator를 선택하여 추가 정보를 표시합니다.

참고

커뮤니티 Operator를 선택하면 Red Hat이 커뮤니티 Operator를 인증하지 않는다고 경고합니다. 계속하기 전에 경고를 확인해야합니다.

Operator에 대한 정보를 확인하고 Install 을 클릭합니다.

Operator 설치 페이지에서 Operator 설치를 구성합니다.

특정 버전의 Operator를 설치하려면 목록에서 업데이트 채널 및 버전을 선택합니다. 보유할 수 있는 채널에서 다양한 버전의 Operator를 검색하고 해당 채널 및 버전의 메타데이터를 보고 설치할 정확한 버전을 선택할 수 있습니다.

참고

버전 선택 기본값은 선택한 채널의 최신 버전입니다. 채널의 최신 버전이 선택되어 있으면 기본적으로 자동 승인 전략이 활성화됩니다. 그렇지 않으면 선택한 채널의 최신 버전을 설치하지 않는 경우 수동 승인이 필요합니다.

수동 승인을 사용하여 Operator를 설치하면 네임스페이스 내에 설치된 모든 Operator가 수동 승인 전략과 함께 작동하고 모든 Operator가 함께 업데이트됩니다. Operator를 독립적으로 업데이트하려면 Operator를 별도의 네임스페이스에 설치합니다.

Operator의 설치 모드를 확인합니다.

All namespaces on the cluster (default) 에서는 기본 `openshift-operators` 네임스페이스에 Operator가 설치되므로 Operator가 클러스터의 모든 네임스페이스를 모니터링하고 사용할 수 있습니다. 이 옵션을 항상 사용할 수있는 것은 아닙니다.

A specific namespace on the cluster 를 사용하면 Operator를 설치할 특정 단일 네임 스페이스를 선택할 수 있습니다. Operator는 이 단일 네임 스페이스에서만 모니터링 및 사용할 수 있게 됩니다.

토큰 인증이 활성화된 클라우드 공급자의 클러스터의 경우:

클러스터가 웹 콘솔에서 AWS Security Token Service(TS 모드)를 사용하는 경우 역할 ARN 필드에 서비스 계정의 AWS IAM 역할의 Amazon Resource Name(ARN)을 입력합니다. 역할의 ARN을 생성하려면 AWS 계정 준비에 설명된 절차를 따르십시오.

클러스터에서 Microsoft Entra Workload ID(웹 콘솔에서 워크로드 ID / Federated Identity Mode)를 사용하는 경우 적절한 필드에 클라이언트 ID, 테넌트 ID 및 구독 ID를 추가합니다.

클러스터가 Google Cloud Platform Workload Identity(웹 콘솔에서 GCP Workload Identity/Federated Identity Mode)를 사용하는 경우 적절한 필드에 프로젝트 번호, 풀 ID, 공급자 ID 및 서비스 계정 이메일을 추가합니다.

업데이트 승인 의 경우 자동 또는 수동 승인 전략을 선택합니다.

중요

웹 콘솔에서 클러스터가 AWS STS, Microsoft Entra Workload ID 또는 GCP Workload Identity를 사용함을 표시하는 경우 업데이트 승인을

Manual 로 설정해야 합니다.

업데이트에 대한 자동 승인이 있는 서브스크립션은 업데이트하기 전에 권한을 변경할 수 있으므로 권장되지 않습니다. 업데이트에 대한 수동 승인이 있는 서브스크립션을 통해 관리자는 최신 버전의 권한을 확인하고 필요한 단계를 수행한 다음 업데이트할 수 있습니다.

이 OpenShift Container Platform 클러스터에서 선택한 네임스페이스에서 Operator를 사용할 수 있도록 하려면 설치를 클릭합니다.

수동 승인 전략을 선택한 경우 설치 계획을 검토하고 승인할 때까지 서브스크립션의 업그레이드 상태가 업그레이드 중 으로 유지됩니다.

Install Plan 페이지에서 승인 한 후 subscription 업그레이드 상태가 Up to date 로 이동합니다.

자동 승인 전략을 선택한 경우 업그레이드 상태가 개입 없이 최신 상태로 확인되어야 합니다.

검증

서브스크립션 업그레이드 상태가 최신이면

Ecosystem → Installed Operators 를 선택하여 설치된 Operator의 CSV(클러스터 서비스 버전)가 최종적으로 표시되는지 확인합니다. Status 는 결국 관련 네임스페이스에서 Succeeded 로 확인되어야 합니다.

참고

All namespaces…​ 설치 모드의 경우 `openshift-operators` 네임스페이스에서 상태는 Succeeded 로 확인되지만 다른 네임스페이스에서 확인하는 경우 상태가 복사 됩니다.

그렇지 않은 경우 다음을 수행합니다.

작업 부하 → Pod 페이지에서 `openshift-operators` 프로젝트(또는 특정 네임스페이스… ​ 설치 모드가 선택된 경우 다른 관련 네임스페이스)의 모든 Pod에서 로그를 확인하여 문제를 보고하고 추가적으로 문제를 해결합니다.

Operator가 설치되면 메타데이터에서 설치된 채널 및 버전을 나타냅니다.

참고

이 카탈로그 컨텍스트에서 채널 및 버전 드롭다운 메뉴를 계속 사용하여 다른 버전 메타데이터를 볼 수 있습니다.

추가 리소스

보류 중인 Operator 업데이트 수동 승인

#### 4.1.3. CLI를 사용하여 소프트웨어 카탈로그에서 설치

OpenShift Container Platform 웹 콘솔을 사용하는 대신 CLI를 사용하여 소프트웨어 카탈로그에서 Operator를 설치할 수 있습니다. 아래 명령을 사용하여 `Subscription` 개체를 만들거나 업데이트합니다.

```shell
oc
```

`SingleNamespace` 설치 모드의 경우 관련 네임스페이스에 적절한 Operator group이 있는지 확인해야 합니다. `OperatorGroup` 오브젝트로 정의되는 Operator group에서 Operator group과 동일한 네임스페이스에 있는 모든 Operator에 대해 필요한 RBAC 액세스 권한을 생성할 대상 네임스페이스를 선택합니다.

작은 정보

대부분의 경우 `SingleNamespace` 모드를 선택할 때 `OperatorGroup` 및 `Subscription` 오브젝트 생성을 자동으로 처리하는 등 백그라운드에서 작업을 자동화하기 때문에 이 절차의 웹 콘솔 방법이 권장됩니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

소프트웨어 카탈로그에서 클러스터에서 사용할 수 있는 Operator 목록을 확인합니다.

```shell-session
$ oc get packagemanifests -n openshift-marketplace
```

```shell-session
NAME                               CATALOG               AGE
3scale-operator                    Red Hat Operators     91m
advanced-cluster-management        Red Hat Operators     91m
amq7-cert-manager                  Red Hat Operators     91m
# ...
couchbase-enterprise-certified     Certified Operators   91m
crunchy-postgres-operator          Certified Operators   91m
mongodb-enterprise                 Certified Operators   91m
# ...
etcd                               Community Operators   91m
jaeger                             Community Operators   91m
kubefed                            Community Operators   91m
# ...
```

필요한 Operator의 카탈로그를 기록해 둡니다.

필요한 Operator를 검사하여 지원되는 설치 모드 및 사용 가능한 채널을 확인합니다.

```shell-session
$ oc describe packagemanifests <operator_name> -n openshift-marketplace
```

```shell-session
# ...
Kind:         PackageManifest
# ...
      Install Modes:
        Supported:  true
        Type:       OwnNamespace
        Supported:  true
        Type:       SingleNamespace
        Supported:  false
        Type:       MultiNamespace
        Supported:  true
        Type:       AllNamespaces
# ...
    Entries:
      Name:       example-operator.v3.7.11
      Version:    3.7.11
      Name:       example-operator.v3.7.10
      Version:    3.7.10
    Name:         stable-3.7
# ...
   Entries:
      Name:         example-operator.v3.8.5
      Version:      3.8.5
      Name:         example-operator.v3.8.4
      Version:      3.8.4
    Name:           stable-3.8
  Default Channel:  stable-3.8
```

1. 1

지원되는 설치 모드를 나타냅니다.

2. 2

3. 채널 이름 예.

4. 하나가 지정되지 않은 경우 기본적으로 선택한 채널입니다.

작은 정보

다음 명령을 실행하여 Operator 버전 및 채널 정보를 YAML 형식으로 출력할 수 있습니다.

```shell-session
$ oc get packagemanifests <operator_name> -n <catalog_namespace> -o yaml
```

네임스페이스에 두 개 이상의 카탈로그가 설치된 경우 다음 명령을 실행하여 특정 카탈로그에서 사용 가능한 버전 및 Operator 채널을 조회합니다.

```shell-session
$ oc get packagemanifest \
   --selector=catalog=<catalogsource_name> \
   --field-selector metadata.name=<operator_name> \
   -n <catalog_namespace> -o yaml
```

중요

Operator 카탈로그를 지정하지 않으면 다음 조건이 충족되는 경우 및 아래 명령을 실행하면 예기치 않은 카탈로그에서 패키지를 반환할 수 있습니다.

```shell
oc get packagemanifest
```

```shell
oc describe packagemanifest
```

여러 카탈로그가 동일한 네임스페이스에 설치됩니다.

카탈로그에는 동일한 이름의 Operator 또는 Operator가 포함됩니다.

설치하려는 Operator가 `AllNamespaces` 설치 모드를 지원하며 이 모드를 사용하도록 선택한 경우 `openshift-operators` 네임스페이스에 기본적으로 `global-operators` 라는 적절한 Operator 그룹이 있으므로 이 단계를 건너뜁니다.

설치하려는 Operator가 `SingleNamespace` 설치 모드를 지원하며 이 모드를 사용하도록 선택한 경우 관련 네임스페이스에 적절한 Operator group이 있는지 확인해야 합니다. 존재하지 않는 경우 다음 단계에 따라 생성을 생성할 수 있습니다.

중요

네임스페이스당 하나의 Operator 그룹만 있을 수 있습니다. 자세한 내용은 “Operator 그룹"을 참조하십시오.

`SingleNamespace` 설치 모드의 경우 `OperatorGroup` 오브젝트 YAML 파일(예: `operatorgroup.yaml`)을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: <operatorgroup_name>
  namespace: <namespace>
spec:
  targetNamespaces:
  - <namespace>
```

1. 2

`SingleNamespace` 설치 모드의 경우 `metadata.namespace` 및 `spec.targetNamespaces` 필드 모두에 동일한 `<namespace>` 값을 사용합니다.

`OperatorGroup` 개체를 생성합니다.

```shell-session
$ oc apply -f operatorgroup.yaml
```

Operator에 네임스페이스를 서브스크립션할 `Subscription` 오브젝트를 생성합니다.

`Subscription` 오브젝트에 대한 YAML 파일을 생성합니다(예: `subscription.yaml`).

참고

특정 버전의 Operator를 구독하려면 `startingCSV` 필드를 원하는 버전으로 설정하고 이후 버전이 카탈로그에 있는 경우 Operator가 자동으로 업그레이드되지 않도록 `installPlanApproval` 필드를 `Manual` 로 설정합니다. 자세한 내용은 다음 "특정 시작 Operator 버전이 있는 `서브스크립션` 오브젝트 예"를 참조하십시오.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: <subscription_name>
  namespace: <namespace_per_install_mode>
spec:
  channel: <channel_name>
  name: <operator_name>
  source: <catalog_name>
  sourceNamespace: <catalog_source_namespace>
  config:
    env:
    - name: ARGS
      value: "-v=10"
    envFrom:
    - secretRef:
        name: license-secret
    volumes:
    - name: <volume_name>
      configMap:
        name: <configmap_name>
    volumeMounts:
    - mountPath: <directory_name>
      name: <volume_name>
    tolerations:
    - operator: "Exists"
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    nodeSelector:
      foo: bar
```

1. 기본 `AllNamespaces` 설치 모드 사용량의 경우 `openshift-operators` 네임스페이스를 지정합니다. 또는 사용자 지정 글로벌 네임스페이스를 생성한 경우 지정할 수 있습니다. `SingleNamespace` 설치 모드 사용의 경우 관련 단일 네임스페이스를 지정합니다.

2. 등록할 채널의 이름입니다.

3. 등록할 Operator의 이름입니다.

4. Operator를 제공하는 카탈로그 소스의 이름입니다.

5. 카탈로그 소스의 네임스페이스입니다. 기본 소프트웨어 카탈로그 소스에는 `openshift-marketplace` 를 사용합니다.

6. `env` 매개변수는 OLM에서 생성한 Pod의 모든 컨테이너에 있어야 하는 환경 변수 목록을 정의합니다.

7. `envFrom` 매개 변수는 컨테이너에서 환경 변수를 채울 소스 목록을 정의합니다.

8. `volumes` 매개변수는 OLM에서 생성한 Pod에 있어야 하는 볼륨 목록을 정의합니다.

9. `volumeMounts` 매개변수는 OLM에서 생성한 Pod의 모든 컨테이너에 있어야 하는 볼륨 마운트 목록을 정의합니다. `volumeMount` 가 존재하지 않는 `볼륨` 을 참조하는 경우 OLM에서 Operator를 배포하지 못합니다.

10. `tolerations` 매개변수는 OLM에서 생성한 Pod의 허용 오차 목록을 정의합니다.

11. `resources` 매개변수는 OLM에서 생성한 Pod의 모든 컨테이너에 대한 리소스 제약 조건을 정의합니다.

12. `nodeSelector` 매개변수는 OLM에서 생성한 Pod에 대한 `NodeSelector` 를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: example-operator
  namespace: example-operator
spec:
  channel: stable-3.7
  installPlanApproval: Manual
  name: example-operator
  source: custom-operators
  sourceNamespace: openshift-marketplace
  startingCSV: example-operator.v3.7.10
```

1. 지정된 버전이 카탈로그의 이후 버전으로 대체될 경우 승인 전략을 `Manual` 로 설정합니다. 이 계획에서는 이후 버전으로 자동 업그레이드할 수 없으므로 시작 CSV에서 설치를 완료하려면 수동 승인이 필요합니다.

2. Operator CSV의 특정 버전을 설정합니다.

AWS(Amazon Web Services) Security Token Service(STS), Microsoft Entra Workload ID 또는 Google Cloud Platform Workload Identity와 같이 토큰 인증이 활성화된 클라우드 공급자의 클러스터의 경우 다음 단계를 수행하여 `서브스크립션` 오브젝트를 구성합니다.

`Subscription` 오브젝트가 수동 업데이트 승인으로 설정되어 있는지 확인합니다.

```yaml
kind: Subscription
# ...
spec:
  installPlanApproval: Manual
```

1. 업데이트에 대한 자동 승인이 있는 서브스크립션은 업데이트하기 전에 권한을 변경할 수 있으므로 권장되지 않습니다. 업데이트에 대한 수동 승인이 있는 서브스크립션을 통해 관리자는 최신 버전의 권한을 확인하고 필요한 단계를 수행한 다음 업데이트할 수 있습니다.

`Subscription` 오브젝트의 `config` 섹션에 관련 클라우드 공급자별 필드를 포함합니다.

클러스터가 AWS STS 모드에 있는 경우 다음 필드를 포함합니다.

```yaml
kind: Subscription
# ...
spec:
  config:
    env:
    - name: ROLEARN
      value: "<role_arn>"
```

1. 역할 ARN 세부 정보를 포함합니다.

클러스터가 Workload ID 모드에 있는 경우 다음 필드를 포함합니다.

```yaml
kind: Subscription
# ...
spec:
 config:
   env:
   - name: CLIENTID
     value: "<client_id>"
   - name: TENANTID
     value: "<tenant_id>"
   - name: SUBSCRIPTIONID
     value: "<subscription_id>"
```

1. 클라이언트 ID를 포함합니다.

2. 테넌트 ID를 포함합니다.

3. 서브스크립션 ID를 포함합니다.

클러스터가 GCP Workload Identity 모드에 있는 경우 다음 필드를 포함합니다.

```yaml
kind: Subscription
# ...
spec:
 config:
   env:
   - name: AUDIENCE
     value: "<audience_url>"
   - name: SERVICE_ACCOUNT_EMAIL
     value: "<service_account_email>"
```

다음과 같습니다.

`<audience>`

GCP Workload Identity를 설정할 때 관리자가 Google Cloud에서 생성한 `AUDIENCE` 값은 다음 형식의 사전 형식의 URL이어야 합니다.

```plaintext
//iam.googleapis.com/projects/<project_number>/locations/global/workloadIdentityPools/<pool_id>/providers/<provider_id>
```

`<service_account_email>`

`SERVICE_ACCOUNT_EMAIL` 값은 Operator 작업 중에 가장하는 Google Cloud 서비스 계정 이메일입니다. 예를 들면 다음과 같습니다.

```plaintext
<service_account_name>@<project_id>.iam.gserviceaccount.com
```

다음 명령을 실행하여 서브스크립션 오브젝트를 생성합니다.

```shell-session
$ oc apply -f subscription.yaml
```

`installPlanApproval` 필드를 `Manual` 로 설정하는 경우 보류 중인 설치 계획을 수동으로 승인하여 Operator 설치를 완료합니다. 자세한 내용은 "Manually approving a pending Operator update"를 참조하십시오.

이 시점에서 OLM은 이제 선택한 Operator를 인식합니다. Operator의 CSV(클러스터 서비스 버전)가 대상 네임스페이스에 표시되고 Operator에서 제공하는 API를 생성에 사용할 수 있어야 합니다.

검증

다음 명령을 실행하여 설치된 Operator의 `Subscription` 오브젝트의 상태를 확인합니다.

```shell-session
$ oc describe subscription <subscription_name> -n <namespace>
```

`SingleNamespace` 설치 모드에 대한 Operator group을 생성한 경우 다음 명령을 실행하여 `OperatorGroup` 오브젝트의 상태를 확인합니다.

```shell-session
$ oc describe operatorgroup <operatorgroup_name> -n <namespace>
```

추가 리소스

Operator groups 정의

사용자 정의 네임스페이스에 글로벌 Operator 설치

보류 중인 Operator 업데이트 수동 승인

#### 4.1.4. 다중 테넌트 클러스터를 위한 Operator의 여러 인스턴스 준비

클러스터 관리자는 다중 테넌트 클러스터에서 사용할 Operator의 여러 인스턴스를 추가할 수 있습니다. 이는 최소 권한의 원칙을 위반하는 것으로 간주될 수 있는 표준 All namespaces 설치 모드 또는 널리 채택되지 않은 Multinamespace 모드의 대체 솔루션입니다. 자세한 내용은 "테넌트 클러스터의 Operator"를 참조하십시오.

다음 절차에서는 배포된 워크로드 집합에 대한 공통 액세스 및 권한을 공유하는 사용자 또는 사용자 그룹입니다.

테넌트 Operator 는 해당 테넌트에서만 사용할 수 있는 Operator의 인스턴스입니다.

사전 요구 사항

설치하려는 Operator의 모든 인스턴스가 지정된 클러스터에서 동일한 버전이어야 합니다.

중요

이 제한 및 기타 제한 사항에 대한 자세한 내용은 "테넌트 클러스터의 Operator"를 참조하십시오.

프로세스

Operator를 설치하기 전에 테넌트의 네임스페이스와 별도의 테넌트 Operator의 네임스페이스를 생성합니다. 예를 들어 테넌트의 네임스페이스가 `team1` 인 경우 `team1-operator` 네임스페이스를 생성할 수 있습니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team1-operator
```

다음 명령을 실행하여 네임스페이스를 생성합니다.

```shell-session
$ oc create -f team1-operator.yaml
```

`spec.targetNamespaces` 목록에 하나의 네임스페이스 항목만 사용하여 테넌트의 네임스페이스에 범위가 지정된 Operator group을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: team1-operatorgroup
  namespace: team1-operator
spec:
  targetNamespaces:
  - team1
```

1. 1

`spec.targetNamespaces` 목록에 테넌트의 네임스페이스만 정의합니다.

다음 명령을 실행하여 Operator group을 생성합니다.

```shell-session
$ oc create -f team1-operatorgroup.yaml
```

다음 단계

테넌트 Operator 네임스페이스에 Operator를 설치합니다. 이 작업은 CLI 대신 웹 콘솔에서 소프트웨어 카탈로그를 사용하여 더 쉽게 수행됩니다. 자세한 절차의 경우 "웹 콘솔을 사용하여 소프트웨어 카탈로그에서 설치".

참고

Operator 설치를 완료한 후 Operator는 테넌트 Operator 네임스페이스에 상주하며 테넌트 네임스페이스를 감시하지만 Operator의 Pod 및 서비스 계정은 테넌트에서 보거나 사용할 수 없습니다.

추가 리소스

다중 테넌트 클러스터의 Operator

#### 4.1.5. 사용자 정의 네임스페이스에 글로벌 Operator 설치

OpenShift Container Platform 웹 콘솔을 사용하여 Operator를 설치할 때 기본 동작은 All namespaces 설치 모드를 지원하는 Operator를 기본 `openshift-operators` 글로벌 네임스페이스에 설치합니다.

이로 인해 공유 설치 계획과 관련된 문제가 발생하고 네임스페이스의 모든 Operator 간에 정책을 업데이트할 수 있습니다. 이러한 제한 사항에 대한 자세한 내용은 "Multitenancy and Operator colocation"을 참조하십시오.

클러스터 관리자는 사용자 정의 글로벌 네임스페이스를 생성하고 해당 네임스페이스를 사용하여 개별 또는 범위가 지정된 Operator 및 해당 종속 항목을 설치하여 이 기본 동작을 수동으로 바이패스할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

Operator를 설치하기 전에 원하는 Operator를 설치할 네임스페이스를 생성합니다. 이 설치 네임스페이스는 사용자 정의 글로벌 네임스페이스가 됩니다.

`네임스페이스` 리소스를 정의하고 YAML 파일(예: `global-operators.yaml`)을 저장합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: global-operators
```

다음 명령을 실행하여 네임스페이스를 생성합니다.

```shell-session
$ oc create -f global-operators.yaml
```

모든 네임스페이스를 감시하는 Operator group인 사용자 정의 글로벌 Operator group을 생성합니다.

`OperatorGroup` 리소스를 정의하고 YAML 파일(예: `global-operatorgroup.yaml`)을 저장합니다. `spec.selector` 및 `spec.targetNamespaces` 필드를 모두 생략하여 모든 네임스페이스를 선택하는 글로벌 Operator group 으로 설정합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: global-operatorgroup
  namespace: global-operators
```

참고

생성된 글로벌 Operator group의 `status.namespaces` 에는 사용 중인 Operator에 모든 네임스페이스를 조사해야 한다는 신호를 보내는 빈 문자열(`""`)이 포함되어 있습니다.

다음 명령을 실행하여 Operator group을 생성합니다.

```shell-session
$ oc create -f global-operatorgroup.yaml
```

다음 단계

사용자 정의 글로벌 네임스페이스에 원하는 Operator를 설치합니다. Operator 설치 중에 웹 콘솔에서 사용자 정의 글로벌 네임스페이스로 설치된 네임스페이스 메뉴를 채우지 않으므로 설치 작업은 OpenShift CLI()로만 수행할 수 있습니다. 자세한 설치 절차는 "CLI를 사용하여 OperatorHub에서 설치"를 참조하십시오.

```shell
oc
```

참고

Operator 설치를 시작할 때 Operator에 종속 항목이 있는 경우 사용자 정의 글로벌 네임스페이스에 종속성도 자동으로 설치됩니다. 결과적으로 종속성 Operator에 동일한 업데이트 정책 및 공유 설치 계획이 있는 것이 유효합니다.

추가 리소스

멀티 테넌시 및 Operator 공동 배치

#### 4.1.6. Operator 워크로드의 Pod 배치

기본적으로 OLM(Operator Lifecycle Manager)은 Operator를 설치하거나 Operand 워크로드를 배포할 때 임의의 작업자 노드에 Pod를 배치합니다. 관리자는 노드 선택기, 테인트 및 허용 오차가 결합된 프로젝트를 사용하여 특정 노드에 Operator 및 Operand 배치를 제어할 수 있습니다.

Operator 및 Operand 워크로드의 Pod 배치 제어에는 다음과 같은 사전 요구 사항이 있습니다.

요구 사항에 따라 Pod를 대상으로 할 노드 또는 노드 집합을 결정합니다. 사용 가능한 경우 노드 또는 노드를 식별하는 `node-role.kubernetes.io/app` 과 같은 기존 레이블을 확인합니다.

그렇지 않으면 컴퓨팅 머신 세트를 사용하거나 노드를 직접 편집하여 `myoperator` 와 같은 레이블을 추가합니다. 이후 단계에서 이 레이블을 프로젝트의 노드 선택기로 사용합니다.

특정 레이블이 있는 Pod만 노드에서 실행되도록 허용하지만 관련이 없는 워크로드를 다른 노드에 추가하려면 컴퓨팅 머신 세트를 사용하거나 노드를 직접 편집하여 노드 또는 노드에 테인트를 추가합니다. 테인트와 일치하지 않는 새 Pod를 노드에서 예약할 수 없도록 하는 효과를 사용합니다.

예를 들어 `myoperator:NoSchedule` 테인트를 사용하면 테인트와 일치하지 않는 새 Pod가 해당 노드에 예약되지 않지만 노드의 기존 Pod는 그대로 유지됩니다.

기본 노드 선택기와 테인트를 추가한 경우 일치하는 허용 오차로 구성된 프로젝트를 만듭니다.

이 시점에서 생성한 프로젝트를 사용하여 다음 시나리오에서 지정된 노드로 Pod를 이동할 수 있습니다.

Operator Pod의 경우

관리자는 다음 섹션에 설명된 대로 프로젝트에서 `Subscription` 오브젝트를 생성할 수 있습니다. 결과적으로 Operator Pod가 지정된 노드에 배치됩니다.

Operand Pod의 경우

설치된 Operator를 사용하여 프로젝트에 애플리케이션을 생성할 수 있습니다. 그러면 Operator가 프로젝트에 소유한 CR(사용자 정의 리소스)이 배치됩니다. 결과적으로 Operator가 다른 네임스페이스에 클러스터 수준 오브젝트 또는 리소스를 배포하지 않는 한 피연산자 Pod가 지정된 노드에 배치됩니다. 이 경우 사용자 정의 Pod 배치가 적용되지 않습니다.

추가 리소스

노드에 수동으로 또는 컴퓨팅 머신 세트를사용하여 테인트 및 허용 오차 추가

프로젝트 수준 노드 선택기 생성

노드 선택기 및 허용 오차를 사용하여 프로젝트 생성

#### 4.1.7. Operator가 설치된 위치 제어

기본적으로 Operator를 설치할 때 OpenShift Container Platform은 Operator Pod를 임의로 작업자 노드 중 하나에 설치합니다. 그러나 특정 노드 또는 노드 세트에 해당 Pod를 예약하려는 경우가 있을 수 있습니다.

다음 예제에서는 Operator Pod를 특정 노드 또는 노드 세트에 예약해야 하는 상황을 설명합니다.

Operator에 `amd64` 또는 `arm64` 와 같은 특정 플랫폼이 필요한 경우

Operator에 Linux 또는 Windows와 같은 특정 운영 체제가 필요한 경우

동일한 호스트에서 또는 동일한 랙에 있는 호스트에서 예약된 Operator를 원하는 경우

네트워크 또는 하드웨어 문제로 인해 다운타임을 방지하기 위해 인프라 전체에 Operator를 분산하려는 경우

Operator의 `Subscription` 오브젝트에 노드 유사성, Pod 유사성 또는 Pod 유사성 방지 제약 조건을 추가하여 Operator Pod가 설치된 위치를 제어할 수 있습니다. 노드 유사성은 스케줄러에서 Pod를 배치할 수 있는 위치를 결정하는 데 사용하는 규칙 세트입니다.

Pod 유사성을 사용하면 관련 Pod가 동일한 노드에 예약되도록 할 수 있습니다. Pod 유사성 방지를 사용하면 노드에서 Pod가 예약되지 않도록 할 수 있습니다.

다음 예제에서는 노드 유사성 또는 Pod 유사성 방지를 사용하여 클러스터의 특정 노드에 Custom Metrics Autoscaler Operator 인스턴스를 설치하는 방법을 보여줍니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-custom-metrics-autoscaler-operator
  namespace: openshift-keda
spec:
  name: my-package
  source: my-operators
  sourceNamespace: operator-registries
  config:
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
          - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
              - ip-10-0-163-94.us-west-2.compute.internal
#...
```

1. `ip-10-0-163-94.us-west-2.compute.internal` 이라는 노드에 Operator의 Pod를 예약해야 하는 노드 유사성입니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-custom-metrics-autoscaler-operator
  namespace: openshift-keda
spec:
  name: my-package
  source: my-operators
  sourceNamespace: operator-registries
  config:
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
          - matchExpressions:
            - key: kubernetes.io/arch
              operator: In
              values:
              - arm64
            - key: kubernetes.io/os
              operator: In
              values:
              - linux
#...
```

1. `kubernetes.io/arch=arm64` 및 `kubernetes.io/os=linux` 라벨이 있는 노드에 Operator의 Pod를 예약해야 하는 노드 유사성입니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-custom-metrics-autoscaler-operator
  namespace: openshift-keda
spec:
  name: my-package
  source: my-operators
  sourceNamespace: operator-registries
  config:
    affinity:
      podAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - test
          topologyKey: kubernetes.io/hostname
#...
```

1. `app=test` 레이블이 있는 Pod가 있는 노드에 Operator의 Pod를 배치하는 Pod 유사성입니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-custom-metrics-autoscaler-operator
  namespace: openshift-keda
spec:
  name: my-package
  source: my-operators
  sourceNamespace: operator-registries
  config:
    affinity:
      podAntiAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
            - key: cpu
              operator: In
              values:
              - high
          topologyKey: kubernetes.io/hostname
#...
```

1. `cpu=high` 라벨이 있는 Pod가 있는 노드에서 Operator의 Pod를 예약하지 않도록 하는 Pod 유사성 방지입니다.

프로세스

Operator Pod 배치를 제어하려면 다음 단계를 완료합니다.

Operator를 정상적으로 설치합니다.

필요한 경우 선호도에 올바르게 응답하도록 노드에 레이블이 지정되어 있는지 확인합니다.

Operator `Subscription` 오브젝트를 편집하여 선호도를 추가합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-custom-metrics-autoscaler-operator
  namespace: openshift-keda
spec:
  name: my-package
  source: my-operators
  sourceNamespace: operator-registries
  config:
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
          - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
              - ip-10-0-185-229.ec2.internal
#...
```

1. `nodeAffinity`, `podAffinity` 또는 `podAntiAffinity` 를 추가합니다. 선호도 생성에 대한 정보는 다음 추가 리소스 섹션을 참조하십시오.

검증

Pod가 특정 노드에 배포되도록 하려면 다음 명령을 실행합니다.

```yaml
$ oc get pods -o wide
```

```shell-session
NAME                                                  READY   STATUS    RESTARTS   AGE   IP            NODE                           NOMINATED NODE   READINESS GATES
custom-metrics-autoscaler-operator-5dcc45d656-bhshg   1/1     Running   0          50s   10.131.0.20   ip-10-0-185-229.ec2.internal   <none>           <none>
```

추가 리소스

Pod 유사성 이해

노드 유사성 이해

노드에서 라벨을 업데이트하는 방법 이해

### 4.2. 설치된 Operator 업데이트

클러스터 관리자는 OpenShift Container Platform 클러스터에서 OLM(Operator Lifecycle Manager)을 사용하여 이전에 설치한 Operator를 업데이트할 수 있습니다.

참고

OLM에서 동일한 네임스페이스에 배치된 설치된 Operator에 대한 업데이트를 처리하는 방법과 사용자 정의 글로벌 Operator 그룹을 사용하여 Operator를 설치하는 대체 방법은 Multitenancy 및 Operator colocation 을 참조하십시오.

#### 4.2.1. Operator 업데이트 준비

설치된 Operator의 서브스크립션은 Operator를 추적하고 업데이트를 수신하는 업데이트 채널을 지정합니다. 업데이트 채널을 변경하여 추적을 시작하고 최신 채널에서 업데이트를 수신할 수 있습니다.

서브스크립션의 업데이트 채널 이름은 Operator마다 다를 수 있지만 이름 지정 체계는 일반적으로 지정된 Operator 내의 공통 규칙을 따릅니다. 예를 들어 채널 이름은 Operator(`1.2`, `1.3`) 또는 릴리스 빈도(`stable`, `fast`)에서 제공하는 애플리케이션의 마이너 릴리스 업데이트 스트림을 따를 수 있습니다.

참고

설치된 Operator는 현재 채널보다 오래된 채널로 변경할 수 없습니다.

Red Hat Customer Portal 랩에는 관리자가 Operator 업데이트를 준비하는 데 도움이 되는 다음 애플리케이션이 포함되어 있습니다.

Red Hat OpenShift Container Platform Operator 업데이트 정보 확인기

애플리케이션을 사용하여 Operator Lifecycle Manager 기반 Operator를 검색하고 다양한 OpenShift Container Platform 버전에서 업데이트 채널별로 사용 가능한 Operator 버전을 확인할 수 있습니다. Cluster Version Operator 기반 Operator는 포함되어 있지 않습니다.

#### 4.2.2. Operator의 업데이트 채널 변경

OpenShift Container Platform 웹 콘솔을 사용하여 Operator의 업데이트 채널을 변경할 수 있습니다.

작은 정보

서브스크립션의 승인 전략이 자동 으로 설정된 경우 선택한 채널에서 새 Operator 버전을 사용할 수 있는 즉시 업데이트 프로세스가 시작됩니다. 승인 전략이 수동 으로 설정된 경우 보류 중인 업데이트를 수동으로 승인해야 합니다.

사전 요구 사항

OLM(Operator Lifecycle Manager)을 사용하여 이전에 설치한 Operator입니다.

프로세스

웹 콘솔에서 Ecosystem → Installed Operators 로 이동합니다.

업데이트 채널을 변경할 Operator 이름을 클릭합니다.

서브스크립션 탭을 클릭합니다.

업데이트 채널 아래에서 업데이트 채널 의 이름을 클릭합니다.

변경할 최신 업데이트 채널을 클릭한 다음 저장 을 클릭합니다.

자동 승인 전략이 있는 서브스크립션의 경우 업데이트가 자동으로 시작됩니다. 에코시스템 → 설치된 Operator 페이지로 이동하여 업데이트 진행 상황을 모니터링합니다. 완료되면 상태가 성공 및 최신 으로 변경됩니다.

수동 승인 전략이 있는 서브스크립션의 경우 서브스크립션 탭에서 업데이트를 수동으로 승인할 수 있습니다.

#### 4.2.3. 보류 중인 Operator 업데이트 수동 승인

설치된 Operator의 서브스크립션에 있는 승인 전략이 수동 으로 설정된 경우 새 업데이트가 현재 업데이트 채널에 릴리스될 때 업데이트를 수동으로 승인해야 설치가 시작됩니다.

사전 요구 사항

OLM(Operator Lifecycle Manager)을 사용하여 이전에 설치한 Operator입니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 Ecosystem → Installed Operators 로 이동합니다.

보류 중인 업데이트가 있는 Operator에 업그레이드 사용 가능 상태가 표시됩니다. 업데이트할 Operator 이름을 클릭합니다.

서브스크립션 탭을 클릭합니다. 승인이 필요한 업데이트는 업그레이드 상태 옆에 표시됩니다. 예를 들어 1 승인 필요 가 표시될 수 있습니다.

1 승인 필요 를 클릭한 다음 설치 계획 프리뷰 를 클릭합니다.

업데이트에 사용 가능한 것으로 나열된 리소스를 검토합니다. 문제가 없는 경우 승인 을 클릭합니다.

에코시스템 → 설치된 Operator 페이지로 이동하여 업데이트 진행 상황을 모니터링합니다. 완료되면 상태가 성공 및 최신 으로 변경됩니다.

#### 4.2.4. 추가 리소스

연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

### 4.3. 클러스터에서 Operator 삭제

다음은 OpenShift Container Platform 클러스터에서 OLM(Operator Lifecycle Manager)을 사용하여 이전에 설치한 Operator를 삭제하거나 제거하는 방법을 설명합니다.

중요

동일한 Operator를 다시 설치하기 전에 Operator를 성공적으로 제거하고 완전히 제거해야 합니다. Operator를 완전히 설치 해제하지 않으면 프로젝트 또는 네임스페이스와 같은 리소스를 "Terminating" 상태가 되고 Operator를 다시 설치하려고 할 때 "error resolving resource" 메시지가 확인될 수 있습니다.

자세한 내용은 제거 실패 후 Operator 다시 설치를 참조하십시오.

#### 4.3.1. 웹 콘솔을 사용하여 클러스터에서 Operator 삭제

클러스터 관리자는 웹 콘솔을 사용하여 선택한 네임스페이스에서 설치된 Operator를 삭제할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터 웹 콘솔에 액세스할 수 있습니다.

프로세스

에코시스템 → 설치된 Operator 페이지로 이동합니다.

제거하려는 Operator를 찾으려면 이름으로 필터링 필드에 키워드를 스크롤하거나 입력합니다. 그런 다음 해당 Operator를 클릭합니다.

Operator 세부 정보 페이지 오른쪽에 있는 작업 목록에서 Operator 제거를 선택합니다.

Operator를 설치 제거하시겠습니까? 대화 상자가 표시됩니다.

설치 제거 를 선택하여 Operator, Operator 배포 및 Pod를 제거합니다. 이 작업 후에 Operator는 실행을 중지하고 더 이상 업데이트가 수신되지 않습니다.

참고

이 작업은 CRD(사용자 정의 리소스 정의) 및 CR(사용자 정의 리소스)을 포함하여 Operator에서 관리하는 리소스를 제거하지 않습니다. 웹 콘솔에서 활성화된 대시보드 및 탐색 항목과 계속 실행되는 클러스터 외부 리소스는 수동 정리가 필요할 수 있습니다.

Operator를 설치 제거한 후 해당 항목을 제거하려면 Operator CRD를 수동으로 삭제해야 할 수 있습니다.

#### 4.3.2. CLI를 사용하여 클러스터에서 Operator 삭제

클러스터 관리자는 CLI를 사용하여 선택한 네임스페이스에서 설치된 Operator를 삭제할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

OpenShift CLI()가 워크스테이션에 설치되어 있습니다.

```shell
oc
```

프로세스

구독된 Operator의 최신 버전(예: `서버리스-operator`)이 `currentCSV` 필드에서 식별되는지 확인합니다.

```shell-session
$ oc get subscription.operators.coreos.com serverless-operator -n openshift-serverless -o yaml | grep currentCSV
```

```shell-session
currentCSV: serverless-operator.v1.28.0
```

서브스크립션을 삭제합니다(예: `서버리스-operator`).

```shell-session
$ oc delete subscription.operators.coreos.com serverless-operator -n openshift-serverless
```

```shell-session
subscription.operators.coreos.com "serverless-operator" deleted
```

이전 단계의 `currentCSV` 값을 사용하여 대상 네임스페이스에서 Operator의 CSV를 삭제합니다.

```shell-session
$ oc delete clusterserviceversion serverless-operator.v1.28.0 -n openshift-serverless
```

```shell-session
clusterserviceversion.operators.coreos.com "serverless-operator.v1.28.0" deleted
```

#### 4.3.3. 실패한 서브스크립션 새로 고침

OLM(Operator Lifecycle Manager)에서는 네트워크상에서 액세스할 수 없는 이미지를 참조하는 Operator를 구독하는 경우 `openshift-marketplace` 네임스페이스에 다음 오류로 인해 실패하는 작업을 확인할 수 있습니다.

```shell-session
ImagePullBackOff for
Back-off pulling image "example.com/openshift4/ose-elasticsearch-operator-bundle@sha256:6d2587129c846ec28d384540322b40b05833e7e00b25cca584e004af9a1d292e"
```

```shell-session
rpc error: code = Unknown desc = error pinging docker registry example.com: Get "https://example.com/v2/": dial tcp: lookup example.com on 10.0.0.1:53: no such host
```

결과적으로 서브스크립션이 이러한 장애 상태에 고착되어 Operator를 설치하거나 업그레이드할 수 없습니다.

서브스크립션, CSV(클러스터 서비스 버전) 및 기타 관련 오브젝트를 삭제하여 실패한 서브스크립션을 새로 고칠 수 있습니다. 서브스크립션을 다시 생성하면 OLM에서 올바른 버전의 Operator를 다시 설치합니다.

사전 요구 사항

액세스할 수 없는 번들 이미지를 가져올 수 없는 실패한 서브스크립션이 있습니다.

올바른 번들 이미지에 액세스할 수 있는지 확인했습니다.

프로세스

Operator가 설치된 네임스페이스에서 `Subscription` 및 `ClusterServiceVersion` 오브젝트의 이름을 가져옵니다.

```shell-session
$ oc get sub,csv -n <namespace>
```

```shell-session
NAME                                                       PACKAGE                  SOURCE             CHANNEL
subscription.operators.coreos.com/elasticsearch-operator   elasticsearch-operator   redhat-operators   5.0

NAME                                                                         DISPLAY                            VERSION    REPLACES   PHASE
clusterserviceversion.operators.coreos.com/elasticsearch-operator.5.0.0-65   OpenShift Elasticsearch Operator   5.0.0-65              Succeeded
```

서브스크립션을 삭제합니다.

```shell-session
$ oc delete subscription <subscription_name> -n <namespace>
```

클러스터 서비스 버전을 삭제합니다.

```shell-session
$ oc delete csv <csv_name> -n <namespace>
```

`openshift-marketplace` 네임스페이스에서 실패한 모든 작업 및 관련 구성 맵의 이름을 가져옵니다.

```shell-session
$ oc get job,configmap -n openshift-marketplace
```

```shell-session
NAME                                                                        COMPLETIONS   DURATION   AGE
job.batch/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   1/1           26s        9m30s

NAME                                                                        DATA   AGE
configmap/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   3      9m30s
```

작업을 삭제합니다.

```shell-session
$ oc delete job <job_name> -n openshift-marketplace
```

이렇게 하면 액세스할 수 없는 이미지를 가져오려는 Pod가 다시 생성되지 않습니다.

구성 맵을 삭제합니다.

```shell-session
$ oc delete configmap <configmap_name> -n openshift-marketplace
```

웹 콘솔의 소프트웨어 카탈로그를 사용하여 Operator를 다시 설치합니다.

검증

Operator가 제대로 다시 설치되었는지 확인합니다.

```shell-session
$ oc get sub,csv,installplan -n <namespace>
```

### 4.4. Operator Lifecycle Manager 기능 구성

OLM(Operator Lifecycle Manager) 컨트롤러는 `cluster` 라는 `OLMConfig` CR(사용자 정의 리소스)에 의해 구성됩니다. 클러스터 관리자는 이 리소스를 수정하여 특정 기능을 활성화하거나 비활성화할 수 있습니다.

이 문서에서는 `OLMConfig` 리소스에서 구성한 OLM에서 현재 지원하는 기능에 대해 간단히 설명합니다.

#### 4.4.1. 복사된 CSV 비활성화

OLM(Operator Lifecycle Manager)에서 Operator를 설치하면 Operator가 조사하도록 구성된 모든 네임스페이스에서 기본적으로 CSV(클러스터 서비스 버전)의 단순화된 사본이 생성됩니다. 이러한 CSV는 복사된 CSV 라고 하며 지정된 네임스페이스에서 컨트롤러가 리소스 이벤트를 적극적으로 조정하는 사용자와 통신합니다.

Operator가 `AllNamespaces` 설치 모드를 사용하도록 구성된 경우 단일 또는 지정된 네임스페이스 집합을 대상으로 하는 대신 클러스터의 모든 네임스페이스에서 Operator의 복사본 CSV가 생성됩니다.

특히 대규모 클러스터에서는 수백 또는 수천 개의 복사된 Operator가 있는 대규모 클러스터에서는 OLM의 메모리 사용량, 클러스터 etcd 제한 및 네트워킹과 같은 리소스가 사용되지 않을 수 있습니다.

클러스터 관리자는 이러한 대규모 클러스터를 지원하기 위해 `AllNamespaces` 모드를 사용하여 전역적으로 설치된 Operator에 대해 복사된 CSV를 비활성화할 수 있습니다.

참고

복사된 CSV를 비활성화하면 `AllNamespaces` 모드에 설치된 Operator의 CSV가 클러스터의 모든 네임스페이스가 아니라 `openshift` 네임스페이스에만 복사됩니다. 비활성화된 CSV 모드에서 동작은 웹 콘솔과 CLI 간에 다릅니다.

웹 콘솔에서 CSV가 실제로 모든 네임스페이스에 복사되지 않더라도 모든 네임스페이스의 `openshift` 네임스페이스에서 복사된 CSV가 표시되도록 기본 동작이 수정되었습니다. 이를 통해 일반 사용자는 여전히 네임스페이스에서 이러한 Operator의 세부 정보를 보고 관련 CR(사용자 정의 리소스)을 생성할 수 있습니다.

OpenShift CLI()에서 일반 사용자는 아래 명령을 사용하여 네임스페이스에 직접 설치된 Operator를 볼 수 있지만 `openshift` 네임스페이스에서 복사한 CSV는 네임스페이스에 표시되지 않습니다. 이 제한에 영향을 받는 Operator를 계속 사용할 수 있으며 사용자 네임스페이스에서 이벤트를 계속 조정할 수 있습니다.

```shell
oc
```

```shell
oc get csvs
```

웹 콘솔 동작과 유사하게 설치된 전체 글로벌 Operator 목록을 보려면 인증된 모든 사용자가 다음 명령을 실행할 수 있습니다.

```shell-session
$ oc get csvs -n openshift
```

프로세스

`cluster` 라는 `OLMConfig` 오브젝트를 편집하고 `spec.features.disableCopiedCSVs` 필드를 `true` 로 설정합니다.

```shell-session
$ oc apply -f - <<EOF
apiVersion: operators.coreos.com/v1
kind: OLMConfig
metadata:
  name: cluster
spec:
  features:
    disableCopiedCSVs: true
EOF
```

1. `AllNamespaces` 설치 모드 Operator에 대해 복사된 CSV를 비활성화

검증

CSV 복사본이 비활성화되면 OLM은 Operator의 네임 스페이스의 이벤트에서 이 정보를 캡처합니다.

```shell-session
$ oc get events
```

```shell-session
LAST SEEN   TYPE      REASON               OBJECT                                MESSAGE
85s         Warning   DisabledCopiedCSVs   clusterserviceversion/my-csv.v1.0.0   CSV copying disabled for operators/my-csv.v1.0.0
```

`spec.features.disableCopiedCSVs` 필드가 없거나 `false` 로 설정된 경우 OLM은 `AllNamespaces` 모드로 설치된 모든 Operator에 대해 복사된 CSV를 다시 생성하고 이전에 언급한 이벤트를 삭제합니다.

추가 리소스

설치 모드

### 4.5. Operator Lifecycle Manager에서 프록시 지원 구성

OpenShift Container Platform 클러스터에 글로벌 프록시가 구성된 경우 OLM(Operator Lifecycle Manager)은 클러스터 전체 프록시로 관리하는 Operator를 자동으로 구성합니다. 그러나 설치된 Operator를 글로벌 프록시를 덮어쓰거나 사용자 정의 CA 인증서를 삽입하도록 구성할 수도 있습니다.

추가 리소스

클러스터 전체 프록시 구성

사용자 정의 PKI 구성 (사용자 정의 CA 인증서)

#### 4.5.1. Operator의 프록시 설정 덮어쓰기

클러스터 수준 송신 프록시가 구성된 경우 OLM(Operator Lifecycle Manager)에서 실행되는 Operator는 배포 시 클러스터 수준 프록시 설정을 상속합니다. 클러스터 관리자는 Operator 서브스크립션을 구성하여 이러한 프록시 설정을 덮어쓸 수도 있습니다.

중요

Operator에서는 관리형 Operand에 대해 Pod의 프록시 설정을 위한 환경 변수 설정을 처리해야 합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

프로세스

웹 콘솔에서 Ecosystem → Software Catalog 페이지로 이동합니다.

Operator를 선택하고 설치 를 클릭합니다.

Operator 설치 페이지에서 `spec` 섹션에 다음 환경 변수를 하나 이상 포함하도록 `Subscription` 오브젝트를 수정합니다.

`HTTP_PROXY`

`HTTPS_PROXY`

`NO_PROXY`

예를 들면 다음과 같습니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: etcd-config-test
  namespace: openshift-operators
spec:
  config:
    env:
    - name: HTTP_PROXY
      value: test_http
    - name: HTTPS_PROXY
      value: test_https
    - name: NO_PROXY
      value: test
  channel: clusterwide-alpha
  installPlanApproval: Automatic
  name: etcd
  source: community-operators
  sourceNamespace: openshift-marketplace
  startingCSV: etcdoperator.v0.9.4-clusterwide
```

참고

이러한 환경 변수는 이전에 설정한 클러스터 수준 또는 사용자 정의 프록시 설정을 제거하기 위해 빈 값을 사용하여 설정을 해제할 수도 있습니다.

OLM에서는 이러한 환경 변수를 단위로 처리합니다. 환경 변수가 한 개 이상 설정되어 있으면 세 개 모두 덮어쓰는 것으로 간주하며 구독한 Operator의 배포에 클러스터 수준 기본값이 사용되지 않습니다.

선택한 네임스페이스에서 Operator를 사용할 수 있도록 설치 를 클릭합니다.

Operator의 CSV가 관련 네임스페이스에 표시되면 사용자 정의 프록시 환경 변수가 배포에 설정되어 있는지 확인할 수 있습니다. 예를 들면 CLI를 사용합니다.

```shell-session
$ oc get deployment -n openshift-operators \
    etcd-operator -o yaml \
    | grep -i "PROXY" -A 2
```

```shell-session
- name: HTTP_PROXY
          value: test_http
        - name: HTTPS_PROXY
          value: test_https
        - name: NO_PROXY
          value: test
        image: quay.io/coreos/etcd-operator@sha256:66a37fd61a06a43969854ee6d3e21088a98b93838e284a6086b13917f96b0d9c
...
```

#### 4.5.2. 사용자 정의 CA 인증서 삽입

클러스터 관리자가 구성 맵을 사용하여 클러스터에 사용자 정의 CA 인증서를 추가하면 Cluster Network Operator는 사용자 제공 인증서와 시스템 CA 인증서를 단일 번들로 병합합니다.

이 병합된 번들은 OLM(Operator Lifecycle Manager)에서 실행 중인 Operator에 삽입할 수 있는데 이러한 작업은 중간자 HTTPS 프록시를 사용하는 경우 유용합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

구성 맵을 사용하여 사용자 정의 CA 인증서를 클러스터에 추가했습니다.

필요한 Operator가 OLM에 설치되어 실행되고 있습니다.

프로세스

Operator의 서브스크립션이 존재하고 다음 라벨을 포함하는 네임스페이스에 빈 구성 맵을 생성합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trusted-ca
  labels:
    config.openshift.io/inject-trusted-cabundle: "true"
```

1. 구성 맵의 이름입니다.

2. CNO(Cluster Network Operator)에 병합된 번들을 삽입하도록 요청합니다.

이 구성 맵이 생성되면 병합된 번들의 인증서 콘텐츠로 즉시 채워집니다.

사용자 정의 CA가 필요한 Pod 내의 각 컨테이너에 `trusted-ca` 구성 맵을 볼륨으로 마운트하는 `spec.config` 섹션을 포함하도록 `Subscription` 오브젝트를 업데이트합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: my-operator
spec:
  package: etcd
  channel: alpha
  config:
    selector:
      matchLabels:
        <labels_for_pods>
    volumes:
    - name: trusted-ca
      configMap:
        name: trusted-ca
        items:
          - key: ca-bundle.crt
            path: tls-ca-bundle.pem
    volumeMounts:
    - name: trusted-ca
      mountPath: /etc/pki/ca-trust/extracted/pem
      readOnly: true
```

1. `config` 섹션이 없는 경우 추가합니다.

2. Operator에서 보유한 Pod와 일치하도록 라벨을 지정합니다.

3. `trusted-ca` 볼륨을 생성합니다.

4. 구성 맵 키로 `ca-bundle.crt` 가 필요합니다.

5. 구성 맵 경로로 `tls-ca-bundle.pem` 이 필요합니다.

6. `trusted-ca` 볼륨 마운트를 생성합니다.

참고

Operator 배포는 기관을 검증하지 못하고 `알 수 없는 권한 오류로 서명된 x509 인증서` 를 표시할 수 있습니다. 이 오류는 Operator 서브스크립션을 사용할 때 사용자 정의 CA를 삽입한 후에도 발생할 수 있습니다.

이 경우 Operator 서브스크립션을 사용하여 `mountPath` 를 trusted-ca의 `/etc/ssl/certs` 로 설정할 수 있습니다.

#### 4.5.3. 추가 리소스

프록시 인증서

기본 수신 인증서 교체

CA 번들 업데이트

### 4.6. Operator 상태 보기

OLM(Operator Lifecycle Manager)의 시스템 상태를 이해하는 것은 설치된 Operator와 관련된 결정을 내리고 문제를 디버깅하는 데 중요합니다. OLM에서는 서브스크립션 및 관련 카탈로그 소스의 상태 및 수행된 작업과 관련된 통찰력을 제공합니다. 이를 통해 사용자는 Operator의 상태를 더 잘 이해할 수 있습니다.

#### 4.6.1. Operator 서브스크립션 상태 유형

서브스크립션은 다음 상태 유형을 보고할 수 있습니다.

| 상태 | 설명 |
| --- | --- |
| `CatalogSourcesUnhealthy` | 해결에 사용되는 일부 또는 모든 카탈로그 소스가 정상 상태가 아닙니다. |
| `InstallPlanMissing` | 서브스크립션 설치 계획이 없습니다. |
| `InstallPlanPending` | 서브스크립션 설치 계획이 설치 대기 중입니다. |
| `InstallPlanFailed` | 서브스크립션 설치 계획이 실패했습니다. |
| `ResolutionFailed` | 서브스크립션의 종속성 확인에 실패했습니다. |

참고

기본 OpenShift Container Platform 클러스터 Operator는 CVO(Cluster Version Operator)에서 관리하며 `Subscription` 오브젝트가 없습니다. 애플리케이션 Operator는 OLM(Operator Lifecycle Manager)에서 관리하며 `Subscription` 오브젝트가 있습니다.

추가 리소스

실패한 서브스크립션 새로 고침

#### 4.6.2. CLI를 사용하여 Operator 서브스크립션 상태 보기

CLI를 사용하여 Operator 서브스크립션 상태를 볼 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

Operator 서브스크립션을 나열합니다.

```shell-session
$ oc get subs -n <operator_namespace>
```

아래 명령을 사용하여 `Subscription` 리소스를 검사합니다.

```shell
oc describe
```

```shell-session
$ oc describe sub <subscription_name> -n <operator_namespace>
```

명령 출력에서 Operator 서브스크립션 조건 유형의 상태에 대한 `Conditions` 섹션을 확인합니다. 다음 예에서 사용 가능한 모든 카탈로그 소스가 정상이므로 `CatalogSourcesUnhealthy` 조건 유형의 상태가 `false` 입니다.

```shell-session
Name:         cluster-logging
Namespace:    openshift-logging
Labels:       operators.coreos.com/cluster-logging.openshift-logging=
Annotations:  <none>
API Version:  operators.coreos.com/v1alpha1
Kind:         Subscription
# ...
Conditions:
   Last Transition Time:  2019-07-29T13:42:57Z
   Message:               all available catalogsources are healthy
   Reason:                AllCatalogSourcesHealthy
   Status:                False
   Type:                  CatalogSourcesUnhealthy
# ...
```

참고

기본 OpenShift Container Platform 클러스터 Operator는 CVO(Cluster Version Operator)에서 관리하며 `Subscription` 오브젝트가 없습니다. 애플리케이션 Operator는 OLM(Operator Lifecycle Manager)에서 관리하며 `Subscription` 오브젝트가 있습니다.

#### 4.6.3. CLI를 사용하여 Operator 카탈로그 소스 상태 보기

CLI를 사용하여 Operator 카탈로그 소스의 상태를 볼 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

네임스페이스의 카탈로그 소스를 나열합니다. 예를 들어 클러스터 전체 카탈로그 소스에 사용되는 `openshift-marketplace` 네임스페이스를 확인할 수 있습니다.

```shell-session
$ oc get catalogsources -n openshift-marketplace
```

```shell-session
NAME                  DISPLAY               TYPE   PUBLISHER   AGE
certified-operators   Certified Operators   grpc   Red Hat     55m
community-operators   Community Operators   grpc   Red Hat     55m
example-catalog       Example Catalog       grpc   Example Org 2m25s
redhat-operators      Red Hat Operators     grpc   Red Hat     55m
```

아래 명령을 사용하여 카탈로그 소스에 대한 자세한 내용 및 상태를 가져옵니다.

```shell
oc describe
```

```shell-session
$ oc describe catalogsource example-catalog -n openshift-marketplace
```

```shell-session
Name:         example-catalog
Namespace:    openshift-marketplace
Labels:       <none>
Annotations:  operatorframework.io/managed-by: marketplace-operator
              target.workload.openshift.io/management: {"effect": "PreferredDuringScheduling"}
API Version:  operators.coreos.com/v1alpha1
Kind:         CatalogSource
# ...
Status:
  Connection State:
    Address:              example-catalog.openshift-marketplace.svc:50051
    Last Connect:         2021-09-09T17:07:35Z
    Last Observed State:  TRANSIENT_FAILURE
  Registry Service:
    Created At:         2021-09-09T17:05:45Z
    Port:               50051
    Protocol:           grpc
    Service Name:       example-catalog
    Service Namespace:  openshift-marketplace
# ...
```

앞의 예제 출력에서 마지막으로 관찰된 상태는 `TRANSIENT_FAILURE` 입니다. 이 상태는 카탈로그 소스에 대한 연결을 설정하는 데 문제가 있음을 나타냅니다.

카탈로그 소스가 생성된 네임스페이스의 Pod를 나열합니다.

```shell-session
$ oc get pods -n openshift-marketplace
```

```shell-session
NAME                                    READY   STATUS             RESTARTS   AGE
certified-operators-cv9nn               1/1     Running            0          36m
community-operators-6v8lp               1/1     Running            0          36m
marketplace-operator-86bfc75f9b-jkgbc   1/1     Running            0          42m
example-catalog-bwt8z                   0/1     ImagePullBackOff   0          3m55s
redhat-operators-smxx8                  1/1     Running            0          36m
```

카탈로그 소스가 네임스페이스에 생성되면 해당 네임스페이스에 카탈로그 소스의 Pod가 생성됩니다. 위 예제 출력에서 `example-catalog-bwt8z` pod의 상태는 `ImagePullBackOff` 입니다. 이 상태는 카탈로그 소스의 인덱스 이미지를 가져오는 데 문제가 있음을 나타냅니다.

자세한 정보는 아래 명령을 사용하여 Pod를 검사합니다.

```shell
oc describe
```

```shell-session
$ oc describe pod example-catalog-bwt8z -n openshift-marketplace
```

```shell-session
Name:         example-catalog-bwt8z
Namespace:    openshift-marketplace
Priority:     0
Node:         ci-ln-jyryyg2-f76d1-ggdbq-worker-b-vsxjd/10.0.128.2
...
Events:
  Type     Reason          Age                From               Message
  ----     ------          ----               ----               -------
  Normal   Scheduled       48s                default-scheduler  Successfully assigned openshift-marketplace/example-catalog-bwt8z to ci-ln-jyryyf2-f76d1-fgdbq-worker-b-vsxjd
  Normal   AddedInterface  47s                multus             Add eth0 [10.131.0.40/23] from openshift-sdn
  Normal   BackOff         20s (x2 over 46s)  kubelet            Back-off pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          20s (x2 over 46s)  kubelet            Error: ImagePullBackOff
  Normal   Pulling         8s (x3 over 47s)   kubelet            Pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          8s (x3 over 47s)   kubelet            Failed to pull image "quay.io/example-org/example-catalog:v1": rpc error: code = Unknown desc = reading manifest v1 in quay.io/example-org/example-catalog: unauthorized: access to the requested resource is not authorized
  Warning  Failed          8s (x3 over 47s)   kubelet            Error: ErrImagePull
```

앞의 예제 출력에서 오류 메시지는 권한 부여 문제로 인해 카탈로그 소스의 인덱스 이미지를 성공적으로 가져오지 못한 것으로 표시됩니다. 예를 들어 인덱스 이미지는 로그인 인증 정보가 필요한 레지스트리에 저장할 수 있습니다.

추가 리소스

Operator Lifecycle Manager 개념 및 리소스 → 카탈로그 소스

gRPC 문서: 연결 상태

프라이빗 레지스트리에서 Operator용 이미지에 액세스

### 4.7. Operator 조건 관리

클러스터 관리자는 OLM(Operator Lifecycle Manager)을 사용하여 Operator 상태를 관리할 수 있습니다.

#### 4.7.1. Operator 상태 덮어쓰기

클러스터 관리자는 Operator에서 보고한 지원되는 Operator 상태를 무시해야 할 수 있습니다. 이러한 상태가 있는 경우 `Spec.Overrides` 어레이의 Operator 상태가 `Spec.Conditions` 어레이의 상태를 덮어씁니다.

그러면 클러스터 관리자가 Operator에서 OLM(Operator Lifecycle Manager)에 상태를 잘못 보고하는 상황을 처리할 수 있습니다.

참고

기본적으로 `Spec.Overrides` 어레이는 클러스터 관리자가 추가할 때까지 `OperatorCondition` 오브젝트에 존재하지 않습니다. 사용자가 추가하거나 사용자 정의 Operator 논리의 결과로 `Spec.Conditions` 배열도 존재하지 않습니다.

예를 들어 항상 업그레이드할 수 없다고 보고하는 알려진 버전의 Operator를 떠올려 보십시오. 이 경우 Operator에서 업그레이드할 수 없다고 보고하더라도 Operator를 업그레이드해야 할 수 있습니다.

이 작업은 `OperatorCondition` 오브젝트의 `Spec.Overrides` 배열에 조건 `유형` 및 `상태를` 추가하여 Operator 조건을 재정의하여 수행할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OLM을 사용하여 `OperatorCondition` 오브젝트가 설치된 Operator입니다.

프로세스

Operator의 `OperatorCondition` 오브젝트를 편집합니다.

```shell-session
$ oc edit operatorcondition <name>
```

오브젝트에 `Spec.Overrides` 어레이를 추가합니다.

```yaml
apiVersion: operators.coreos.com/v2
kind: OperatorCondition
metadata:
  name: my-operator
  namespace: operators
spec:
  overrides:
  - type: Upgradeable
    status: "True"
    reason: "upgradeIsSafe"
    message: "This is a known issue with the Operator where it always reports that it cannot be upgraded."
  conditions:
  - type: Upgradeable
    status: "False"
    reason: "migration"
    message: "The operator is performing a migration."
    lastTransitionTime: "2020-08-24T23:15:55Z"
```

1. 클러스터 관리자는 업그레이드 준비 상태를 `True` 로 변경할 수 있습니다.

#### 4.7.2. Operator 조건을 사용하도록 Operator 업데이트

OLM(Operator Lifecycle Manager)은 OLM에서 조정하는 각 `ClusterServiceVersion` 리소스에 대해 `OperatorCondition` 리소스를 자동으로 생성합니다. CSV의 모든 서비스 계정에는 Operator에 속하는 `OperatorCondition` 과 상호 작용할 수 있도록 RBAC가 부여됩니다.

Operator 작성자는 Operator가 OLM에 의해 배포된 후 `operator-lib` 라이브러리를 사용하여 자체 조건을 설정할 수 있도록 Operator를 개발할 수 있습니다. Operator 조건을 Operator 작성자로 설정하는 방법에 대한 자세한 내용은 Operator 조건 활성화 페이지를 참조하십시오.

#### 4.7.2.1. 기본값 설정

OLM은 이전 버전과의 호환성을 유지하기 위해 `OperatorCondition` 리소스의 부재를 조건을 옵트아웃하는 것으로 처리합니다. 따라서 Operator 조건 사용에 옵트인하는 Operator는 Pod의 준비 상태 프로브를 `true` 로 설정하기 전에 기본 조건을 설정해야 합니다.

그러면 Operator에 조건을 올바른 상태로 업데이트할 수 있는 유예 기간이 제공됩니다.

#### 4.7.3. 추가 리소스

Operator 상태

### 4.8. 비 클러스터 관리자가 Operator를 설치하도록 허용

클러스터 관리자는 Operator 그룹을 사용하여 일반 사용자가 Operator 를 설치할 수 있도록 허용할 수 있습니다.

추가 리소스

Operator groups

#### 4.8.1. Operator 설치 정책 이해

Operator를 실행하는 데 광범위한 권한이 필요할 수 있으며 필요한 권한이 버전에 따라 다를 수 있습니다. OLM(Operator Lifecycle Manager)은 `cluster-admin` 권한으로 실행됩니다. 기본적으로 Operator 작성자는 CSV(클러스터 서비스 버전)에서 권한 세트를 지정할 수 있으며 OLM은 이를 Operator에 부여합니다.

Operator가 클러스터 범위 권한을 달성할 수 없고 사용자가 OLM을 사용하여 권한을 에스컬레이션할 수 없도록 클러스터 관리자는 클러스터에 추가되기 전에 Operator를 수동으로 감사할 수 있습니다. 클러스터 관리자에게는 서비스 계정을 사용하여 Operator를 설치 또는 업그레이드하는 동안 수행할 수 있는 작업을 결정하고 제한하는 툴도 제공됩니다.

클러스터 관리자는 일련의 권한이 부여된 서비스 계정과 Operator group을 연결할 수 있습니다. 서비스 계정은 RBAC(역할 기반 액세스 제어) 규칙을 사용하여 사전 정의된 범위 내에서만 실행되도록 Operator에 정책을 설정합니다. 결과적으로 Operator는 해당 규칙에서 명시적으로 허용하지 않는 작업을 수행할 수 없습니다.

Operator 그룹을 사용하면 충분한 권한이 있는 사용자는 범위가 제한된 Operator를 설치할 수 있습니다. 결과적으로 더 많은 사용자가 더 많은 Operator 프레임워크 툴을 안전하게 사용할 수 있어 Operator를 사용하여 애플리케이션을 빌드할 수 있는 풍부한 환경을 제공할 수 있습니다.

참고

`Subscription` 오브젝트에 대한 RBAC(역할 기반 액세스 제어)는 네임스페이스에서 `edit` 또는 `admin` 역할이 있는 모든 사용자에게 자동으로 부여됩니다. 그러나 `OperatorGroup` 오브젝트에 RBAC가 존재하지 않습니다.

이 경우 일반 사용자가 Operator를 설치하지 못하도록 합니다. Operator group을 사전 설치하는 것은 효과적으로 설치 권한을 부여하는 것입니다.

Operator 그룹을 서비스 계정과 연결할 때 다음 사항에 유의하십시오.

`APIService` 및 `CustomResourceDefinition` 리소스는 항상 `cluster-admin` 역할을 사용하여 OLM에 의해 생성됩니다. Operator group과 연결된 서비스 계정에는 이러한 리소스를 작성할 수 있는 권한을 부여해서는 안 됩니다.

이제 Operator group에 연결된 모든 Operator의 권한이 지정된 서비스 계정에 부여된 권한으로 제한됩니다. Operator에서 서비스 계정 범위를 벗어나는 권한을 요청하면 클러스터 관리자가 문제를 해결하고 해결할 수 있도록 적절한 오류와 함께 설치에 실패합니다.

#### 4.8.1.1. 설치 시나리오

Operator를 클러스터에서 설치하거나 업그레이드할 수 있는지 결정하는 경우 OLM(Operator Lifecycle Manager)은 다음 시나리오를 고려합니다.

클러스터 관리자가 새 Operator group을 생성하고 서비스 계정을 지정합니다. 이 Operator group과 연결된 모든 Operator가 설치되고 서비스 계정에 부여된 권한에 따라 실행됩니다.

클러스터 관리자가 새 Operator group을 생성하고 서비스 계정을 지정하지 않습니다. OpenShift Container Platform은 이전 버전과의 호환성을 유지하므로 기본 동작은 그대로 유지되면서 Operator 설치 및 업그레이드가 허용됩니다.

서비스 계정을 지정하지 않는 기존 Operator group의 경우 기본 동작은 그대로 유지되면서 Operator 설치 및 업그레이드가 허용됩니다.

클러스터 관리자가 기존 Operator group을 업데이트하고 서비스 계정을 지정합니다. OLM을 사용하면 현재 권한을 사용하여 기존 Operator를 계속 실행될 수 있습니다. 이러한 기존 Operator에서 업그레이드를 수행하면 기존 Operator가 새 Operator와 같이 서비스 계정에 부여된 권한에 따라 다시 설치되어 실행됩니다.

권한을 추가하거나 제거함으로써 Operator group에서 지정하는 서비스 계정이 변경되거나 기존 서비스 계정을 새 서비스 계정과 교체합니다. 기존 Operator에서 업그레이드를 수행하면 기존 Operator가 새 Operator와 같이 업데이트된 서비스 계정에 부여된 권한에 따라 다시 설치되어 실행됩니다.

클러스터 관리자는 Operator group에서 서비스 계정을 제거합니다. 기본 동작은 유지되고 Operator 설치 및 업그레이드는 허용됩니다.

#### 4.8.1.2. 설치 워크플로

Operator group이 서비스 계정에 연결되고 Operator가 설치 또는 업그레이드되면 OLM(Operator Lifecycle Manager)에서 다음과 같은 워크플로를 사용합니다.

OLM에서 지정된 `Subscription` 오브젝트를 선택합니다.

OLM에서 이 서브스크립션에 연결된 Operator group을 가져옵니다.

OLM에서 Operator group에 서비스 계정이 지정되었는지 확인합니다.

OLM에서 서비스 계정에 대한 클라이언트 범위를 생성하고 범위가 지정된 클라이언트를 사용하여 Operator를 설치합니다. 이렇게 하면 Operator에서 요청한 모든 권한이 항상 Operator group 서비스 계정의 권한으로 제한됩니다.

OLM은 CSV에 지정된 권한 세트를 사용하여 새 서비스 계정을 생성하고 Operator에 할당합니다. Operator는 할당된 서비스 계정으로 실행됩니다.

#### 4.8.2. Operator 설치 범위 지정

OLM(Operator Lifecycle Manager)의 Operator 설치 및 업그레이드에 대한 범위 지정 규칙을 제공하려면 서비스 계정을 Operator group에 연결합니다.

클러스터 관리자는 다음 예제를 통해 일련의 Operator를 지정된 네임스페이스로 제한할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

새 네임스페이스를 생성합니다.

```shell-session
$ cat <<EOF | oc create -f -
apiVersion: v1
kind: Namespace
metadata:
  name: scoped
EOF
```

Operator를 제한할 권한을 할당합니다. 이를 위해서는 새로 생성된 지정된 네임스페이스에 새 서비스 계정, 관련 역할 및 역할 바인딩을 생성해야 합니다.

다음 명령을 실행하여 서비스 계정을 생성합니다.

```shell-session
$ cat <<EOF | oc create -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: scoped
  namespace: scoped
EOF
```

다음 명령을 실행하여 보안을 생성합니다.

```shell-session
$ cat <<EOF | oc create -f -
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: scoped
  namespace: scoped
  annotations:
    kubernetes.io/service-account.name: scoped
EOF
```

1. 시크릿은 서비스 계정에서 사용하는 수명이 긴 API 토큰이어야 합니다.

다음 명령을 실행하여 역할을 생성합니다.

주의

이 예에서 역할은 서비스 계정 권한을 부여하여 지정된 네임 스페이스에서 데모 목적으로만 모든 작업을 수행할 수 있습니다. 프로덕션 환경에서는 더 세분화된 권한 세트를 생성해야 합니다. 자세한 내용은 "Fine-grained permissions"를 참조하십시오.

```shell-session
$ cat <<EOF | oc create -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: scoped
  namespace: scoped
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: scoped-bindings
  namespace: scoped
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: scoped
subjects:
- kind: ServiceAccount
  name: scoped
  namespace: scoped
EOF
```

다음 명령을 실행하여 지정된 네임스페이스에 `OperatorGroup` 오브젝트를 생성합니다. 이 Operator group은 지정된 네임스페이스를 대상으로 하여 테넌시가 제한되도록 합니다. 또한 Operator group에서는 사용자가 서비스 계정을 지정할 수 있습니다.

```shell-session
$ cat <<EOF | oc create -f -
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: scoped
  namespace: scoped
spec:
  serviceAccountName: scoped
  targetNamespaces:
  - scoped
EOF
```

1. 이전 단계에서 생성한 서비스 계정을 지정합니다. 지정된 네임스페이스에 설치된 Operator는 모두 이 Operator group 및 지정된 서비스 계정에 연결됩니다.

지정된 네임스페이스에 `Subscription` 오브젝트를 생성하여 Operator를 설치합니다.

```shell-session
$ cat <<EOF | oc create -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-cert-manager-operator
  namespace: scoped
spec:
  channel: stable-v1
  name: openshift-cert-manager-operator
  source: <catalog_source_name>
  sourceNamespace: <catalog_source_namespace>
EOF
```

1. 지정된 네임스페이스에 이미 존재하는 카탈로그 소스 또는 글로벌 카탈로그 네임스페이스에 있는 카탈로그 소스를 지정합니다(예: `redhat-operators`).

2. 카탈로그 소스가 생성된 네임스페이스를 지정합니다(예: `redhat-operators` 카탈로그의 `openshift-marketplace`).

Operator group에 연결된 모든 Operator의 권한이 지정된 서비스 계정에 부여된 권한으로 제한됩니다. Operator에서 서비스 계정 외부에 있는 권한을 요청하는 경우 설치가 실패하고 관련 오류가 표시됩니다.

#### 4.8.2.1. 세분화된 권한

OLM(Operator Lifecycle Manager)은 Operator group에 지정된 서비스 계정을 사용하여 설치 중인 Operator와 관련하여 다음 리소스를 생성하거나 업데이트합니다.

`ClusterServiceVersion`

`서브스크립션`

`Secret`

`ServiceAccount`

`Service`

`ClusterRole` 및 `ClusterRoleBinding`

`Role` 및 `RoleBinding`

Operator를 지정된 네임스페이스로 제한하려면 클러스터 관리자가 서비스 계정에 다음 권한을 부여하여 시작하면 됩니다.

참고

다음 역할은 일반적인 예이며 특정 Operator를 기반으로 추가 규칙이 필요할 수 있습니다.

```yaml
kind: Role
rules:
- apiGroups: ["operators.coreos.com"]
  resources: ["subscriptions", "clusterserviceversions"]
  verbs: ["get", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["services", "serviceaccounts"]
  verbs: ["get", "create", "update", "patch"]
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["roles", "rolebindings"]
  verbs: ["get", "create", "update", "patch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["list", "watch", "get", "create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["list", "watch", "get", "create", "update", "patch", "delete"]
```

1. 2

여기에 표시된 배포 및 Pod와 같은 기타 리소스를 생성하는 권한을 추가합니다.

또한 Operator에서 가져오기 보안을 지정하는 경우 다음 권한도 추가해야 합니다.

```yaml
kind: ClusterRole
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
---
kind: Role
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["create", "update", "patch"]
```

1. OLM 네임스페이스에서 보안을 가져오는 데 필요합니다.

#### 4.8.3. Operator 카탈로그 액세스 제어

글로벌 카탈로그 네임스페이스 `openshift-marketplace` 에 Operator 카탈로그가 생성되면 카탈로그의 Operator가 모든 네임스페이스에 클러스터 전체에서 사용할 수 있습니다. 다른 네임스페이스에 생성된 카탈로그는 카탈로그의 동일한 네임스페이스에서만 Operator를 사용할 수 있도록 합니다.

비 클러스터 관리자 사용자가 Operator 설치 권한을 위임한 클러스터에서 클러스터 관리자는 해당 사용자가 설치할 수 있는 Operator 집합을 추가로 제어하거나 제한하려고 할 수 있습니다. 이 작업은 다음 작업을 통해 수행할 수 있습니다.

기본 글로벌 카탈로그를 모두 비활성화합니다.

관련 Operator 그룹이 사전 설치된 동일한 네임스페이스에서 사용자 정의 큐레이션 카탈로그를 활성화합니다.

추가 리소스

기본 OperatorHub 카탈로그 소스 비활성화

클러스터에 카탈로그 소스 추가

#### 4.8.4. 권한 장애 문제 해결

권한 부족으로 인해 Operator 설치가 실패하는 경우 다음 절차를 사용하여 오류를 확인합니다.

프로세스

`Subscription` 오브젝트를 검토합니다. 해당 상태에는 Operator에 필요한 `[Cluster]Role[Binding]` 오브젝트를 생성하는 `InstallPlan` 오브젝트를 가리키는 오브젝트 참조 `installPlanRef` 가 있습니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: Subscription
metadata:
  name: etcd
  namespace: scoped
status:
  installPlanRef:
    apiVersion: operators.coreos.com/v1
    kind: InstallPlan
    name: install-4plp8
    namespace: scoped
    resourceVersion: "117359"
    uid: 2c1df80e-afea-11e9-bce3-5254009c9c23
```

`InstallPlan` 오브젝트의 상태에 오류가 있는지 확인합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: InstallPlan
status:
  conditions:
  - lastTransitionTime: "2019-07-26T21:13:10Z"
    lastUpdateTime: "2019-07-26T21:13:10Z"
    message: 'error creating clusterrole etcdoperator.v0.9.4-clusterwide-dsfx4: clusterroles.rbac.authorization.k8s.io
      is forbidden: User "system:serviceaccount:scoped:scoped" cannot create resource
      "clusterroles" in API group "rbac.authorization.k8s.io" at the cluster scope'
    reason: InstallComponentFailed
    status: "False"
    type: Installed
  phase: Failed
```

오류 메시지에는 다음이 표시됩니다.

리소스의 API 그룹을 포함하여 생성할 수 없는 리소스 유형. 이 경우 `rbac.authorization.k8s.io` 그룹의 `clusterroles` 입니다.

리소스의 이름.

오류 유형 `is forbidden` 은 사용자에게 작업을 수행할 수 있는 권한이 충분하지 않음을 나타냅니다.

리소스를 생성하거나 업데이트하려고 시도한 사용자의 이름. 이 경우 Operator group에 지정된 서비스 계정을 나타냅니다.

작업 범위: `cluster scope` 여부

사용자는 서비스 계정에 누락된 권한을 추가한 다음 다시 수행할 수 있습니다.

참고

OLM(Operator Lifecycle Manager)은 현재 첫 번째 시도에서 전체 오류 목록을 제공하지 않습니다.

### 4.9. 사용자 정의 카탈로그 관리

클러스터 관리자와 Operator 카탈로그 유지 관리자는 OpenShift Container Platform의 OLM(Operator Lifecycle Manager)에서 번들 형식을 사용하여 패키지된 사용자 정의 카탈로그를 생성하고 관리할 수 있습니다.

중요

Kubernetes는 후속 릴리스에서 제거된 특정 API를 주기적으로 사용하지 않습니다. 결과적으로 Operator는 API를 제거한 Kubernetes 버전을 사용하는 OpenShift Container Platform 버전에서 시작하여 제거된 API를 사용할 수 없습니다.

추가 리소스

Red Hat 제공 Operator 카탈로그

#### 4.9.1. 사전 요구 사항

`opm` CLI 를 설치했습니다.

#### 4.9.2. 파일 기반 카탈로그

파일 기반 카탈로그 는 OLM(Operator Lifecycle Manager) 카탈로그 형식의 최신 버전입니다. 일반 텍스트 기반(JSON 또는 YAML)과 이전 SQLite 데이터베이스 형식의 선언적 구성 진화이며 완전히 이전 버전과 호환됩니다.

중요

OpenShift Container Platform 4.11부터 파일 기반 카탈로그 형식으로 기본 Red Hat 제공 Operator 카탈로그 릴리스입니다. 더 이상 사용되지 않는 SQLite 데이터베이스 형식으로 릴리스된 OpenShift Container Platform 4.6에 대한 기본 Red Hat 제공 Operator 카탈로그입니다.

SQLite 데이터베이스 형식과 관련된 `opm` 하위 명령, 플래그 및 기능은 더 이상 사용되지 않으며 향후 릴리스에서 제거됩니다. 이 기능은 계속 지원되며 더 이상 사용되지 않는 SQLite 데이터베이스 형식을 사용하는 카탈로그에 사용해야 합니다.

`opm index prune` 와 같은 SQLite 데이터베이스 형식을 사용하기 위한 `opm` 하위 명령 및 플래그는 파일 기반 카탈로그 형식에서는 작동하지 않습니다. 파일 기반 카탈로그 작업에 대한 자세한 내용은 Operator Framework 패키징 형식 및 oc-mirror 플러그인을 사용하여 연결이 끊긴 설치의 이미지 미러링 을 참조하십시오.

#### 4.9.2.1. 파일 기반 카탈로그 이미지 생성

`opm` CLI를 사용하여 더 이상 사용되지 않는 SQLite 데이터베이스 형식을 대체하는 일반 텍스트 파일 기반 카탈로그 형식(JSON 또는 YAML)을 사용하는 카탈로그 이미지를 생성할 수 있습니다.

사전 요구 사항

`opm` CLI를 설치했습니다.

다음 명령버전 1.9.3+이 있습니다.

```shell
podman
```

번들 이미지가 빌드되어 Docker v2-2 를 지원하는 레지스트리로 푸시됩니다.

프로세스

카탈로그를 초기화합니다.

다음 명령을 실행하여 카탈로그의 디렉터리를 생성합니다.

```shell-session
$ mkdir <catalog_dir>
```

`opm generate dockerfile` 명령을 실행하여 카탈로그 이미지를 빌드할 수 있는 Dockerfile을 생성합니다.

```shell-session
$ opm generate dockerfile <catalog_dir> \
    -i registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20
```

1. `-i` 플래그를 사용하여 공식 Red Hat 기본 이미지를 지정합니다. 그러지 않으면 Dockerfile에서 기본 업스트림 이미지를 사용합니다.

Dockerfile은 이전 단계에서 생성한 카탈로그 디렉터리와 동일한 상위 디렉터리에 있어야 합니다.

```shell-session
.
├── <catalog_dir>
└── <catalog_dir>.Dockerfile
```

1. 상위 디렉터리

2. 카탈로그 디렉터리

3. `opm generate dockerfile` 명령으로 생성된 Dockerfile

`opm init` 명령을 실행하여 카탈로그를 Operator의 패키지 정의로 채웁니다.

```shell-session
$ opm init <operator_name> \
    --default-channel=preview \
    --description=./README.md \
    --icon=./operator-icon.svg \
    --output yaml \
    > <catalog_dir>/index.yaml
```

1. Operator 또는 패키지, 이름

2. 서브스크립션이 지정되지 않은 경우 기본값으로 설정된 채널

3. Operator의 `README.md` 또는 기타 문서 경로

4. Operator 아이콘 경로

5. 출력 형식: JSON 또는 YAML

6. 카탈로그 구성 파일을 생성하는 경로

이 명령은 지정된 카탈로그 구성 파일에 `olm.package` 선언적 구성 blob을 생성합니다.

`opm render` 명령을 실행하여 카탈로그에 번들을 추가합니다.

```shell-session
$ opm render <registry>/<namespace>/<bundle_image_name>:<tag> \
    --output=yaml \
    >> <catalog_dir>/index.yaml
```

1. 번들 이미지의 가져오기 사양

2. 카탈로그 구성 파일의 경로

참고

채널에는 하나 이상의 번들이 포함되어야 합니다.

번들에 채널 항목을 추가합니다. 예를 들어 다음 예제를 사양에 맞게 수정하고 < `catalog_dir>/index.yaml` 파일에 추가합니다.

```yaml
---
schema: olm.channel
package: <operator_name>
name: preview
entries:
  - name: <operator_name>.v0.1.0
```

1. `<operator_name>` 뒤의 마침표(`.`)를 버전 `v` 앞에 포함해야 합니다. 그렇지 않으면 항목이 `opm validate` 명령을 전달하지 못합니다.

파일 기반 카탈로그를 확인합니다.

카탈로그 디렉터리에 대해 `opm validate` 명령을 실행합니다.

```shell-session
$ opm validate <catalog_dir>
```

오류 코드가 `0` 인지 확인합니다.

```shell-session
$ echo $?
```

```shell-session
0
```

아래 명령을 실행하여 카탈로그 이미지를 빌드합니다.

```shell
podman build
```

```shell-session
$ podman build . \
    -f <catalog_dir>.Dockerfile \
    -t <registry>/<namespace>/<catalog_image_name>:<tag>
```

카탈로그 이미지를 레지스트리로 푸시합니다.

필요한 경우 아래 명령을 실행하여 대상 레지스트리로 인증합니다.

```shell
podman login
```

```shell-session
$ podman login <registry>
```

아래 명령을 실행하여 카탈로그 이미지를 푸시합니다.

```shell
podman push
```

```shell-session
$ podman push <registry>/<namespace>/<catalog_image_name>:<tag>
```

추가 리소스

`opm` CLI 참조

#### 4.9.2.2. 파일 기반 카탈로그 이미지 업데이트 또는 필터링

`opm` CLI를 사용하여 파일 기반 카탈로그 형식을 사용하는 카탈로그 이미지를 업데이트하거나 필터링할 수 있습니다. 기존 카탈로그 이미지의 콘텐츠를 추출하면 필요에 따라 카탈로그를 수정할 수 있습니다. 예를 들면 다음과 같습니다.

패키지 추가

패키지 제거

기존 패키지 항목 업데이트

패키지, 채널 및 번들당 사용 중단 메시지 세부 정보

그런 다음 업데이트된 카탈로그 버전으로 이미지를 다시 빌드할 수 있습니다.

참고

또는 미러 레지스트리에 카탈로그 이미지가 이미 있는 경우 oc-mirror CLI 플러그인을 사용하여 업데이트된 카탈로그 버전의 해당 카탈로그 이미지에서 제거된 이미지를 자동으로 정리하고 대상 레지스트리에 미러링할 수 있습니다.

oc-mirror 플러그인 및 이 사용 사례에 대한 자세한 내용은 "미러 미러 레지스트리 콘텐츠 업데이트" 섹션, 특히 "oc-mirror 플러그인을 사용하여 연결이 끊긴 설치를 위한 이미지 미러링" 섹션, 특히 "이미지 실행" 섹션을 참조하십시오.

사전 요구 사항

워크스테이션에 다음이 있습니다.

`opm` CLI입니다.

다음 명령버전 1.9.3 이상.

```shell
podman
```

파일 기반 카탈로그 이미지입니다.

이 카탈로그와 관련된 워크스테이션에서 최근에 초기화된 카탈로그 디렉터리 구조입니다.

초기화된 카탈로그 디렉터리가 없는 경우 디렉터리를 생성하고 Dockerfile을 생성합니다. 자세한 내용은 "파일 기반 카탈로그 이미지 생성" 절차의 " catalog" 단계를 참조하십시오.

프로세스

YAML 형식의 카탈로그 이미지의 콘텐츠를 카탈로그 디렉터리의 `index.yaml` 파일에 추출합니다.

```shell-session
$ opm render <registry>/<namespace>/<catalog_image_name>:<tag> \
    -o yaml > <catalog_dir>/index.yaml
```

참고

또는 `-o json` 플래그를 사용하여 JSON 형식으로 출력할 수 있습니다.

결과 `index.yaml` 파일의 내용을 사양으로 수정합니다.

중요

번들이 카탈로그에 게시되면 사용자 중 하나가 설치되었다고 가정합니다. 해당 버전이 설치된 사용자를 방지하려면 카탈로그의 이전에 게시된 모든 번들에 현재 또는 최신 채널 헤드에 대한 업데이트 경로가 있는지 확인합니다.

Operator를 추가하려면 "파일 기반 카탈로그 이미지 생성" 프로세스에서 패키지, 번들 및 채널 항목을 생성하는 단계를 수행합니다.

Operator를 제거하려면 패키지와 관련된 `olm.package`, `olm.channel`, `olm.bundle` blobs 세트를 삭제합니다. 다음 예제에서는 카탈로그에서 `example-operator` 패키지를 제거하려면 삭제해야 하는 세트를 보여줍니다.

```yaml
---
defaultChannel: release-2.7
icon:
  base64data: <base64_string>
  mediatype: image/svg+xml
name: example-operator
schema: olm.package
---
entries:
- name: example-operator.v2.7.0
  skipRange: '>=2.6.0 <2.7.0'
- name: example-operator.v2.7.1
  replaces: example-operator.v2.7.0
  skipRange: '>=2.6.0 <2.7.1'
- name: example-operator.v2.7.2
  replaces: example-operator.v2.7.1
  skipRange: '>=2.6.0 <2.7.2'
- name: example-operator.v2.7.3
  replaces: example-operator.v2.7.2
  skipRange: '>=2.6.0 <2.7.3'
- name: example-operator.v2.7.4
  replaces: example-operator.v2.7.3
  skipRange: '>=2.6.0 <2.7.4'
name: release-2.7
package: example-operator
schema: olm.channel
---
image: example.com/example-inc/example-operator-bundle@sha256:<digest>
name: example-operator.v2.7.0
package: example-operator
properties:
- type: olm.gvk
  value:
    group: example-group.example.io
    kind: MyObject
    version: v1alpha1
- type: olm.gvk
  value:
    group: example-group.example.io
    kind: MyOtherObject
    version: v1beta1
- type: olm.package
  value:
    packageName: example-operator
    version: 2.7.0
- type: olm.bundle.object
  value:
    data: <base64_string>
- type: olm.bundle.object
  value:
    data: <base64_string>
relatedImages:
- image: example.com/example-inc/example-related-image@sha256:<digest>
  name: example-related-image
schema: olm.bundle
---
```

Operator에 대한 사용 중단 메시지를 추가하거나 업데이트하려면 패키지의 `index.yaml` 파일과 같은 디렉토리에 `deprecations.yaml` 파일이 있는지 확인하세요. `deprecations.yaml` 파일 형식에 대한 자세한 내용은 "olm.deprecations 스키마"를 참조하십시오.

변경 사항을 저장하십시오.

카탈로그를 확인합니다.

```shell-session
$ opm validate <catalog_dir>
```

카탈로그를 다시 빌드합니다.

```shell-session
$ podman build . \
    -f <catalog_dir>.Dockerfile \
    -t <registry>/<namespace>/<catalog_image_name>:<tag>
```

업데이트된 카탈로그 이미지를 레지스트리로 푸시합니다.

```shell-session
$ podman push <registry>/<namespace>/<catalog_image_name>:<tag>
```

검증

웹 콘솔에서 관리 → 클러스터 설정 → 구성 페이지의 OperatorHub 구성 리소스로 이동합니다.

업데이트된 카탈로그 이미지의 pull 사양을 사용하도록 카탈로그 소스를 추가하거나 기존 카탈로그 소스를 업데이트합니다.

자세한 내용은 이 섹션의 "추가 리소스"의 "클러스터에 카탈로그 소스 추가"를 참조하십시오.

카탈로그 소스가 READY 상태에 있으면 Ecosystem → Software Catalog 페이지로 이동합니다. 유형 제목에서 Operator를 선택하고 Operator 목록에 변경 사항이 반영되었는지 확인합니다.

추가 리소스

패키징 형식 → 스키마 → olm.deprecations 스키마

oc-mirror 플러그인을 사용하여 연결이 끊긴 설치의 이미지 미러링 → 미러 레지스트리 콘텐츠 유지

클러스터에 카탈로그 소스 추가

#### 4.9.3. SQLite 기반 카탈로그

중요

Operator 카탈로그의 SQLite 데이터베이스 형식은 더 이상 사용되지 않는 기능입니다. 더 이상 사용되지 않는 기능은 여전히 OpenShift Container Platform에 포함되어 있으며 계속 지원됩니다. 그러나 이 기능은 향후 릴리스에서 제거될 예정이므로 새로운 배포에는 사용하지 않는 것이 좋습니다.

OpenShift Container Platform에서 더 이상 사용되지 않거나 삭제된 주요 기능의 최신 목록은 OpenShift Container Platform 릴리스 노트에서 더 이상 사용되지 않고 삭제된 기능 섹션을 참조하십시오.

#### 4.9.3.1. SQLite 기반 인덱스 이미지 생성

`opm` CLI를 사용하여 SQLite 데이터베이스 형식을 기반으로 인덱스 이미지를 생성할 수 있습니다.

사전 요구 사항

`opm` CLI를 설치했습니다.

다음 명령버전 1.9.3+이 있습니다.

```shell
podman
```

번들 이미지가 빌드되어 Docker v2-2 를 지원하는 레지스트리로 푸시됩니다.

프로세스

새 인덱스를 시작합니다.

```shell-session
$ opm index add \
    --bundles <registry>/<namespace>/<bundle_image_name>:<tag> \
    --tag <registry>/<namespace>/<index_image_name>:<tag> \
    [--binary-image <registry_base_image>]
```

1. 인덱스에 추가할 번들 이미지를 쉼표로 구분한 목록입니다.

2. 인덱스 이미지에 포함할 이미지 태그입니다.

3. 선택 사항: 카탈로그 제공에 사용할 대체 레지스트리 기본 이미지입니다.

인덱스 이미지를 레지스트리로 내보냅니다.

필요한 경우 대상 레지스트리로 인증합니다.

```shell-session
$ podman login <registry>
```

인덱스 이미지를 내보냅니다.

```shell-session
$ podman push <registry>/<namespace>/<index_image_name>:<tag>
```

#### 4.9.3.2. SQLite 기반 인덱스 이미지 업데이트

사용자 정의 인덱스 이미지를 참조하는 카탈로그 소스를 사용하도록 소프트웨어 카탈로그를 구성한 후 클러스터 관리자는 인덱스 이미지에 번들 이미지를 추가하여 클러스터에서 사용 가능한 Operator를 최신 상태로 유지할 수 있습니다.

`opm index add` 명령을 사용하여 기존 인덱스 이미지를 업데이트할 수 있습니다.

사전 요구 사항

`opm` CLI를 설치했습니다.

다음 명령버전 1.9.3+이 있습니다.

```shell
podman
```

인덱스 이미지가 빌드되어 레지스트리로 푸시됩니다.

인덱스 이미지를 참조하는 기존 카탈로그 소스가 있습니다.

프로세스

번들 이미지를 추가하여 기존 인덱스를 업데이트합니다.

```shell-session
$ opm index add \
    --bundles <registry>/<namespace>/<new_bundle_image>@sha256:<digest> \
    --from-index <registry>/<namespace>/<existing_index_image>:<existing_tag> \
    --tag <registry>/<namespace>/<existing_index_image>:<updated_tag> \
    --pull-tool podman
```

1. `--bundles` 플래그는 인덱스에 추가할 쉼표로 구분된 추가 번들 이미지 목록을 지정합니다.

2. `--from-index` 플래그는 이전에 내보낸 인덱스를 지정합니다.

3. `--tag` 플래그는 업데이트된 인덱스 이미지에 적용할 이미지 태그를 지정합니다.

4. `--pull-tool` 플래그는 컨테이너 이미지를 가져오는 데 사용되는 툴을 지정합니다.

다음과 같습니다.

`<registry>`

`quay.io` 또는 `mirror.example.com` 과 같은 레지스트리의 호스트 이름을 지정합니다.

`<namespace>`

`ocs-dev` 또는 `abc` 와 같은 레지스트리의 네임스페이스를 지정합니다.

`<new_bundle_image>`

`ocs-operator` 와 같이 레지스트리에 추가할 새 번들 이미지를 지정합니다.

`<digest>`

번들 이미지의 SHA 이미지 ID 또는 다이제스트(예: `c7f11097a628f092d8bad148406aa0e0951094a03445fd4bc0775431ef683a41`)를 지정합니다.

`<existing_index_image>`

이전에 내보낸 이미지(예: `abc-redhat-operator-index`)를 지정합니다.

`<existing_tag>`

이전에 내보낸 이미지 태그(예: `4.20`)를 지정합니다.

`<updated_tag>`

`4.20.1` 과 같이 업데이트된 인덱스 이미지에 적용할 이미지 태그를 지정합니다.

```shell-session
$ opm index add \
    --bundles quay.io/ocs-dev/ocs-operator@sha256:c7f11097a628f092d8bad148406aa0e0951094a03445fd4bc0775431ef683a41 \
    --from-index mirror.example.com/abc/abc-redhat-operator-index:4.20 \
    --tag mirror.example.com/abc/abc-redhat-operator-index:4.20.1 \
    --pull-tool podman
```

업데이트된 인덱스 이미지를 내보냅니다.

```shell-session
$ podman push <registry>/<namespace>/<existing_index_image>:<updated_tag>
```

OLM(Operator Lifecycle Manager)이 정기적으로 카탈로그 소스에서 참조하는 인덱스 이미지를 자동으로 폴링하면 새 패키지가 성공적으로 추가되었는지 확인합니다.

```shell-session
$ oc get packagemanifests -n openshift-marketplace
```

#### 4.9.3.3. SQLite 기반 인덱스 이미지 필터링

Operator 번들 포맷을 기반으로 하는 인덱스 이미지는 Operator 카탈로그의 컨테이너화된 스냅샷입니다. 지정된 패키지 목록을 제외한 모든 인덱스를 필터링하거나 정리할 수 있습니다. 이 목록은 원하는 Operator만 포함하는 소스 인덱스 복사본을 생성합니다.

사전 요구 사항

다음 명령버전 1.9.3+이 있습니다.

```shell
podman
```

`grpcurl` (타사 명령줄 툴)이 있습니다.

`opm` CLI를 설치했습니다.

Docker v2-2 를 지원하는 레지스트리에 액세스할 수 있습니다.

프로세스

대상 레지스트리로 인증합니다.

```shell-session
$ podman login <target_registry>
```

정리된 인덱스에 포함하려는 패키지 목록을 결정합니다.

컨테이너에서 정리하려는 소스 인덱스 이미지를 실행합니다. 예를 들면 다음과 같습니다.

```shell-session
$ podman run -p50051:50051 \
    -it registry.redhat.io/redhat/redhat-operator-index:v4.20
```

```shell-session
Trying to pull registry.redhat.io/redhat/redhat-operator-index:v4.20...
Getting image source signatures
Copying blob ae8a0c23f5b1 done
...
INFO[0000] serving registry                              database=/database/index.db port=50051
```

별도의 터미널 세션에서 `grpcurl` 명령을 사용하여 인덱스에서 제공하는 패키지 목록을 가져옵니다.

```shell-session
$ grpcurl -plaintext localhost:50051 api.Registry/ListPackages > packages.out
```

`packages.out` 파일을 검사하고 정리된 인덱스에 보관할 이 목록에 있는 패키지 이름을 확인합니다. 예를 들면 다음과 같습니다.

```plaintext
...
{
  "name": "advanced-cluster-management"
}
...
{
  "name": "jaeger-product"
}
...
{
{
  "name": "quay-operator"
}
...
```

아래 명령을 실행한 터미널 세션에서 Ctrl 및 C 를 눌러 컨테이너 프로세스를 중지합니다.

```shell
podman run
```

다음 명령을 실행하여 지정된 패키지를 제외한 소스 인덱스를 모두 정리합니다.

```plaintext
$ opm index prune \
    -f registry.redhat.io/redhat/redhat-operator-index:v4.20 \
    -p advanced-cluster-management,jaeger-product,quay-operator \
    [-i registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20] \
    -t <target_registry>:<port>/<namespace>/redhat-operator-index:v4.20
```

1. 정리할 인덱스입니다.

2. 쉼표로 구분된 보관할 패키지 목록입니다.

3. IBM Power® 및 IBM Z® 이미지에만 필요합니다. 대상 OpenShift Container Platform 클러스터 주 버전 및 마이너 버전과 일치하는 태그가 있는 Operator 레지스트리 기본 이미지입니다.

4. 빌드 중인 새 인덱스 이미지에 대한 사용자 정의 태그입니다.

다음 명령을 실행하여 새 인덱스 이미지를 대상 레지스트리로 내보냅니다.

```plaintext
$ podman push <target_registry>:<port>/<namespace>/redhat-operator-index:v4.20
```

`<namespace>` 는 레지스트리의 기존 네임스페이스입니다.

#### 4.9.4. 카탈로그 소스 및 Pod 보안 승인

Pod 보안 표준을 보장하기 위해 OpenShift Container Platform 4.11에 Pod 보안 승인이 도입되었습니다. SQLite 기반 카탈로그 형식 및 OpenShift Container Platform 4.11 이전에 릴리스된 `opm` CLI 툴 버전을 사용하여 빌드된 카탈로그 소스는 제한된 Pod 보안 적용에서 실행할 수 없습니다.

OpenShift Container Platform 4.20에서 네임스페이스에는 기본적으로 제한된 Pod 보안 적용 기능이 없으며 기본 카탈로그 소스 보안 모드는 `legacy` 로 설정됩니다.

모든 네임스페이스에 대한 기본 제한된 적용은 향후 OpenShift Container Platform 릴리스에 포함될 예정입니다. 제한된 적용이 발생하면 카탈로그 소스 Pod에 대한 Pod 사양의 보안 컨텍스트가 제한된 Pod 보안 표준과 일치해야 합니다.

카탈로그 소스 이미지에 다른 Pod 보안 표준이 필요한 경우 네임스페이스의 Pod 보안 승인 레이블을 명시적으로 설정해야 합니다.

참고

restricted로 SQLite 기반 카탈로그 소스 Pod를 실행하지 않으려면 OpenShift Container Platform 4.20에서 카탈로그 소스를 업데이트할 필요가 없습니다.

그러나 제한된 Pod 보안 적용에서 카탈로그 소스를 실행하려면 지금 작업을 수행하는 것이 좋습니다. 카탈로그 소스가 제한된 Pod 보안 적용에서 실행되도록 하지 않으면 향후 OpenShift Container Platform 릴리스에서 카탈로그 소스가 실행되지 않을 수 있습니다.

카탈로그 작성자는 다음 작업 중 하나를 완료하여 제한된 Pod 보안 적용과 호환성을 활성화할 수 있습니다.

카탈로그를 파일 기반 카탈로그 형식으로 마이그레이션합니다.

OpenShift Container Platform 4.11 이상에서 릴리스된 `opm` CLI 툴 버전으로 카탈로그 이미지를 업데이트합니다.

참고

SQLite 데이터베이스 카탈로그 형식은 더 이상 사용되지 않지만 Red Hat에서 계속 지원합니다. 향후 릴리스에서는 SQLite 데이터베이스 형식이 지원되지 않으며 카탈로그를 파일 기반 카탈로그 형식으로 마이그레이션해야 합니다.

OpenShift Container Platform 4.11부터 기본 Red Hat 제공 Operator 카탈로그는 파일 기반 카탈로그 형식으로 릴리스됩니다. 파일 기반 카탈로그는 제한된 Pod 보안 적용과 호환됩니다.

SQLite 데이터베이스 카탈로그 이미지를 업데이트하거나 카탈로그를 파일 기반 카탈로그 형식으로 마이그레이션하지 않으려면 승격된 권한으로 실행되도록 카탈로그를 구성할 수 있습니다.

추가 리소스

Pod 보안 허용 이해 및 관리

#### 4.9.4.1. SQLite 데이터베이스 카탈로그를 파일 기반 카탈로그 형식으로 마이그레이션

더 이상 사용되지 않는 SQLite 데이터베이스 형식 카탈로그를 파일 기반 카탈로그 형식으로 업데이트할 수 있습니다.

사전 요구 사항

SQLite 데이터베이스 카탈로그 소스가 있습니다.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

워크스테이션에 OpenShift Container Platform 4.20과 함께 릴리스된 `opm` CLI 툴의 최신 버전이 있습니다.

프로세스

다음 명령을 실행하여 SQLite 데이터베이스 카탈로그를 파일 기반 카탈로그로 마이그레이션합니다.

```shell-session
$ opm migrate <registry_image> <fbc_directory>
```

다음 명령을 실행하여 파일 기반 카탈로그에 대한 Dockerfile을 생성합니다.

```shell-session
$ opm generate dockerfile <fbc_directory> \
  --binary-image \
  registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20
```

다음 단계

생성된 Dockerfile을 빌드, 태그를 지정하고 레지스트리로 내보낼 수 있습니다.

추가 리소스

클러스터에 카탈로그 소스 추가

#### 4.9.4.2. SQLite 데이터베이스 카탈로그 이미지 다시 빌드

OpenShift Container Platform 버전과 함께 릴리스된 `opm` CLI 툴의 최신 버전으로 SQLite 데이터베이스 카탈로그 이미지를 다시 빌드할 수 있습니다.

사전 요구 사항

SQLite 데이터베이스 카탈로그 소스가 있습니다.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

워크스테이션에 OpenShift Container Platform 4.20과 함께 릴리스된 `opm` CLI 툴의 최신 버전이 있습니다.

프로세스

다음 명령을 실행하여 최신 버전의 `opm` CLI 툴로 카탈로그를 다시 빌드합니다.

```shell-session
$ opm index add --binary-image \
  registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20 \
  --from-index <your_registry_image> \
  --bundles "" -t \<your_registry_image>
```

#### 4.9.4.3. 승격된 권한으로 실행되도록 카탈로그 구성

SQLite 데이터베이스 카탈로그 이미지를 업데이트하거나 카탈로그를 파일 기반 카탈로그 형식으로 마이그레이션하지 않으려면 다음 작업을 수행하여 기본 Pod 보안 적용이 restricted로 변경될 때 카탈로그 소스가 실행되도록 할 수 있습니다.

카탈로그 소스 정의에서 카탈로그 보안 모드를 legacy로 수동으로 설정합니다. 이 작업을 수행하면 기본 카탈로그 보안 모드가 restricted로 변경되는 경우에도 기존 권한으로 카탈로그가 실행됩니다.

기준 또는 권한 있는 Pod 보안 시행을 위해 카탈로그 소스 네임스페이스에 레이블을 지정합니다.

참고

SQLite 데이터베이스 카탈로그 형식은 더 이상 사용되지 않지만 Red Hat에서 계속 지원합니다. 향후 릴리스에서는 SQLite 데이터베이스 형식이 지원되지 않으며 카탈로그를 파일 기반 카탈로그 형식으로 마이그레이션해야 합니다. 파일 기반 카탈로그는 제한된 Pod 보안 적용과 호환됩니다.

사전 요구 사항

SQLite 데이터베이스 카탈로그 소스가 있습니다.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

`기준선` 또는 `권한` 있는 Pod 보안 승인 표준으로 Pod 실행을 지원하는 대상 네임스페이스가 있습니다.

프로세스

다음 예와 같이 `spec.grpcPodConfig.securityContextConfig` 레이블을 `legacy` 로 설정하여 `CatalogSource` 정의를 편집합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: my-catsrc
  namespace: my-ns
spec:
  sourceType: grpc
  grpcPodConfig:
    securityContextConfig: legacy
  image: my-image:latest
```

작은 정보

OpenShift Container Platform 4.20에서 `spec.grpcPodConfig.securityContextConfig` 필드는 기본적으로 `legacy` 로 설정됩니다. 향후 OpenShift Container Platform 릴리스에서는 기본 설정이 `restricted` 로 변경될 예정입니다.

제한된 적용으로 카탈로그를 실행할 수 없는 경우 이 필드를 기존으로 수동으로 설정하는 것이 `좋습니다`.

다음 예와 같이 `<namespace>.yaml` 파일을 편집하여 카탈로그 소스 네임스페이스에 승격된 Pod 보안 승인 표준을 추가합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
...
  labels:
    security.openshift.io/scc.podSecurityLabelSync: "false"
    openshift.io/cluster-monitoring: "true"
    pod-security.kubernetes.io/enforce: baseline
  name: "<namespace_name>"
```

1. 네임스페이스에 `security.openshift.io/scc.podSecurityLabelSync=false` 라벨을 추가하여 Pod 보안 레이블 동기화를 끕니다.

2. Pod 보안 승인 `pod-security.kubernetes.io/enforce` 레이블을 적용합니다. 레이블을 `baseline` 또는 `privileged` 로 설정합니다. 네임스페이스의 다른 워크로드에 `권한 있는` 프로필이 필요하지 않는 한 `기준` Pod 보안 프로필을 사용합니다.

#### 4.9.5. 클러스터에 카탈로그 소스 추가

OpenShift Container Platform 클러스터에 카탈로그 소스를 추가하면 사용자를 위한 Operator를 검색하고 설치할 수 있습니다. 클러스터 관리자는 인덱스 이미지를 참조하는 `CatalogSource` 오브젝트를 생성할 수 있습니다. 소프트웨어 카탈로그는 카탈로그 소스를 사용하여 사용자 인터페이스를 채웁니다.

작은 정보

또는 웹 콘솔을 사용하여 카탈로그 소스를 관리할 수 있습니다. 관리 → 클러스터 설정 → 구성 → OperatorHub 페이지에서 개별 소스 를 생성, 업데이트, 삭제, 비활성화 및 활성화할 수 있는 소스 탭을 클릭합니다.

사전 요구 사항

인덱스 이미지를 빌드하여 레지스트리로 내보냈습니다.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

인덱스 이미지를 참조하는 `CatalogSource` 오브젝트를 생성합니다.

다음을 사양에 맞게 수정하고 `catalogsource.yaml` 파일로 저장합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: my-operator-catalog
  namespace: openshift-marketplace
  annotations:
    olm.catalogImageTemplate:
      "<registry>/<namespace>/<index_image_name>:v{kube_major_version}.{kube_minor_version}.{kube_patch_version}"
spec:
  sourceType: grpc
  grpcPodConfig:
    securityContextConfig: <security_mode>
  image: <registry>/<namespace>/<index_image_name>:<tag>
  displayName: My Operator Catalog
  publisher: <publisher_name>
  updateStrategy:
    registryPoll:
      interval: 30m
```

1. 카탈로그 소스를 모든 네임스페이스의 사용자가 전역적으로 사용할 수 있도록 하려면 `openshift-marketplace` 네임스페이스를 지정합니다. 그러지 않으면 카탈로그의 범위가 지정되고 해당 네임스페이스에 대해서만 사용할 수 있도록 다른 네임스페이스를 지정할 수 있습니다.

2. 선택 사항: `olm.catalogImageTemplate` 주석을 인덱스 이미지 이름으로 설정하고 이미지 태그의 템플릿을 구성할 때 표시된 대로 하나 이상의 Kubernetes 클러스터 버전 변수를 사용합니다.

3. `legacy` 또는 `restricted` 를 지정합니다. 필드가 설정되지 않은 경우 기본값은 `legacy` 입니다. 향후 OpenShift Container Platform 릴리스에서는 기본값이 `제한` 될 예정입니다.

참고

`제한된` 권한으로 카탈로그를 실행할 수 없는 경우 이 필드를 기존으로 수동으로 설정하는 것이 `좋습니다`.

4. 인덱스 이미지를 지정합니다. 이미지 이름 다음에 태그를 지정하는 경우(예: `:v4.20`) 카탈로그 소스 Pod는 `Always` 의 이미지 가져오기 정책을 사용합니다.

즉, Pod는 컨테이너를 시작하기 전에 항상 이미지를 가져옵니다. 다이제스트를 지정하는 경우(예: `@sha256:<id` >) 이미지 가져오기 정책은 `IfNotPresent` 입니다.

즉 Pod는 노드에 없는 경우에만 이미지를 가져옵니다.

5. 카탈로그를 게시하는 이름 또는 조직 이름을 지정합니다.

6. 카탈로그 소스는 새 버전을 자동으로 확인하여 최신 상태를 유지할 수 있습니다.

파일을 사용하여 `CatalogSource` 오브젝트를 생성합니다.

```shell-session
$ oc apply -f catalogSource.yaml
```

다음 리소스가 성공적으로 생성되었는지 확인합니다.

Pod를 확인합니다.

```shell-session
$ oc get pods -n openshift-marketplace
```

```shell-session
NAME                                    READY   STATUS    RESTARTS  AGE
my-operator-catalog-6njx6               1/1     Running   0         28s
marketplace-operator-d9f549946-96sgr    1/1     Running   0         26h
```

카탈로그 소스를 확인합니다.

```shell-session
$ oc get catalogsource -n openshift-marketplace
```

```shell-session
NAME                  DISPLAY               TYPE PUBLISHER  AGE
my-operator-catalog   My Operator Catalog   grpc            5s
```

패키지 매니페스트 확인합니다.

```shell-session
$ oc get packagemanifest -n openshift-marketplace
```

```shell-session
NAME                          CATALOG               AGE
jaeger-product                My Operator Catalog   93s
```

이제 OpenShift Container Platform 웹 콘솔의 소프트웨어 카탈로그 페이지에서 Operator를 설치할 수 있습니다.

추가 리소스

Operator Lifecycle Manager 개념 및 리소스 → 카탈로그 소스

프라이빗 레지스트리에서 Operator용 이미지에 액세스

이미지 가져오기 정책

#### 4.9.6. 프라이빗 레지스트리에서 Operator용 이미지에 액세스

OLM(Operator Lifecycle Manager)에서 관리하는 Operator와 관련된 특정 이미지가 프라이빗 레지스트리라고도 하는 인증된 컨테이너 이미지 레지스트리에서 호스팅되는 경우 OLM 및 소프트웨어 카탈로그는 기본적으로 이미지를 가져올 수 없습니다. 액세스를 활성화하려면 레지스트리의 인증 정보가 포함된 풀 시크릿을 생성할 수 있습니다.

OLM은 카탈로그 소스에서 하나 이상의 가져오기 보안을 참조함으로써 Operator 및 카탈로그 네임스페이스에 보안을 배치하여 설치를 허용할 수 있습니다.

Operator 또는 해당 Operand에 필요한 기타 이미지에서도 프라이빗 레지스트리에 액세스해야 할 수 있습니다. 이 시나리오에서 OLM은 대상 테넌트 네임스페이스에 보안을 배치하지 않지만 필요한 액세스 권한을 활성화하기 위해 글로벌 클러스터 가져오기 보안 또는 개별 네임스페이스 서비스 계정에 인증 자격 증명을 추가할 수 있습니다.

OLM에서 관리하는 Operator에 적절한 가져오기 액세스 권한이 있는지 확인할 때는 다음 유형의 이미지를 고려해야 합니다.

인덱스 이미지

`CatalogSource` 오브젝트는 Operator 번들 형식을 사용하고 이미지 레지스트리에서 호스팅되는 컨테이너 이미지로 패키지된 카탈로그 소스에 해당하는 인덱스 이미지를 참조할 수 있습니다. 인덱스 이미지가 프라이빗 레지스트리에서 호스팅되는 경우 시크릿을 사용하여 가져오기 액세스 권한을 활성화할 수 있습니다.

번들 이미지

Operator 번들 이미지는 컨테이너 이미지로 패키지되어 Operator의 고유 버전을 나타내는 메타데이터와 매니페스트입니다. 카탈로그 소스에서 참조한 번들 이미지가 하나 이상의 프라이빗 레지스트리에서 호스팅되는 경우 보안을 사용하여 가져오기 액세스 권한을 활성화할 수 있습니다.

Operator 및 Operand 이미지

카탈로그 소스에서 설치한 Operator에서 Operator 이미지 자체 또는 조사하는 Operand 이미지 중 하나로 프라이빗 이미지를 사용하는 경우 Operator가 설치되지 않습니다. 배포에 필수 레지스트리 인증에 대한 액세스 권한이 없기 때문입니다.

카탈로그 소스의 보안을 참조해도 OLM에서 Operand가 설치된 대상 테넌트 네임스페이스에 보안을 배치할 수 없습니다.

대신 클러스터의 모든 네임스페이스에 대한 액세스 권한을 제공하는 `openshift-config` 네임스페이스의 글로벌 클러스터 가져오기 보안에 인증 세부 정보를 추가하면 됩니다. 또는 전체 클러스터에 대한 액세스 권한을 제공할 수 없는 경우 대상 테넌트 네임스페이스의 `default` 서비스 계정에 가져오기 보안을 추가할 수 있습니다.

레지스트리 인증 정보에 대한 보안을 생성하고 관련 카탈로그와 함께 사용할 보안을 추가하여 프라이빗 레지스트리에서 Operator에서 이미지에 액세스할 수 있습니다.

사전 요구 사항

프라이빗 레지스트리에서 다음 중 하나 이상 호스팅해야 합니다.

인덱스 이미지 또는 카탈로그 이미지.

Operator 번들 이미지.

Operator 또는 Operand 이미지.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

필요한 각 프라이빗 레지스트리에 대해 보안을 생성합니다.

프라이빗 레지스트리에 로그인하여 레지스트리 자격 증명 파일을 생성하거나 업데이트합니다.

```shell-session
$ podman login <registry>:<port>
```

참고

레지스트리 자격 증명의 파일 경로는 레지스트리에 로그인하는 데 사용하는 컨테이너 툴에 따라 다를 수 있습니다. CLI의 경우 기본 위치는 `${XDG_RUNTIME_DIR}/containers/auth.json` 입니다. CLI의 경우 기본 위치는 `/root/.docker/config.json` 입니다.

```shell
podman
```

```shell
docker
```

보안당 하나의 레지스트리에 대한 자격 증명만 포함하고 여러 레지스트리의 자격 증명은 별도의 보안에서 관리하는 것이 좋습니다. 이후 단계에서 `CatalogSource` 오브젝트에 여러 보안을 포함할 수 있으며 OpenShift Container Platform은 이미지를 가져오는 동안 사용할 수 있도록 보안을 단일 가상 자격 증명 파일에 병합합니다.

기본적으로 레지스트리 자격 증명 파일은 둘 이상의 레지스트리 또는 하나의 레지스트리에 있는 여러 리포지토리의 세부 정보를 저장할 수 있습니다. 파일의 현재 콘텐츠를 확인합니다. 예를 들면 다음과 같습니다.

```plaintext
{
    "auths": {
        "registry.redhat.io": {
            "auth": "FrNHNydQXdzclNqdg=="
        },
        "quay.io": {
            "auth": "fegdsRib21iMQ=="
        },
        "https://quay.io/my-namespace/my-user/my-image": {
            "auth": "eWfjwsDdfsa221=="
        },
        "https://quay.io/my-namespace/my-user": {
            "auth": "feFweDdscw34rR=="
        },
        "https://quay.io/my-namespace": {
            "auth": "frwEews4fescyq=="
        }
    }
}
```

이 파일은 이후 단계에서 보안을 생성하는 데 사용되므로 파일마다 하나의 레지스트리에만 세부 정보를 저장해야 합니다. 이 작업은 다음 방법 중 하나를 사용하여 수행할 수 있습니다.

아래 명령을 사용하여 원하는 레지스트리 하나만 남을 때까지 추가 레지스트리의 자격 증명을 제거합니다.

```shell
podman logout <registry>
```

레지스트리 자격 증명 파일을 편집하고 레지스트리 세부 정보를 분리하여 여러 파일에 저장합니다. 예를 들면 다음과 같습니다.

```plaintext
{
        "auths": {
                "registry.redhat.io": {
                        "auth": "FrNHNydQXdzclNqdg=="
                }
        }
}
```

```plaintext
{
        "auths": {
                "quay.io": {
                        "auth": "Xd2lhdsbnRib21iMQ=="
                }
        }
}
```

프라이빗 레지스트리의 인증 자격 증명 정보가 포함된 `openshift-marketplace` 네임스페이스에 보안을 생성합니다.

```shell-session
$ oc create secret generic <secret_name> \
    -n openshift-marketplace \
    --from-file=.dockerconfigjson=<path/to/registry/credentials> \
    --type=kubernetes.io/dockerconfigjson
```

이 단계를 반복하여 다른 필수 프라이빗 레지스트리에 대한 추가 보안을 생성하고 `--from-file` 플래그를 업데이트하여 다른 레지스트리 자격 증명 파일 경로를 지정합니다.

기존 `CatalogSource` 오브젝트를 생성하거나 업데이트하여 하나 이상의 보안을 참조합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: my-operator-catalog
  namespace: openshift-marketplace
spec:
  sourceType: grpc
  secrets:
  - "<secret_name_1>"
  - "<secret_name_2>"
  grpcPodConfig:
    securityContextConfig: <security_mode>
  image: <registry>:<port>/<namespace>/<image>:<tag>
  displayName: My Operator Catalog
  publisher: <publisher_name>
  updateStrategy:
    registryPoll:
      interval: 30m
```

1. `spec.secrets` 섹션을 추가하고 필요한 보안을 지정합니다.

2. `legacy` 또는 `restricted` 를 지정합니다. 필드가 설정되지 않은 경우 기본값은 `legacy` 입니다. 향후 OpenShift Container Platform 릴리스에서는 기본값이 `제한` 될 예정입니다.

참고

`제한된` 권한으로 카탈로그를 실행할 수 없는 경우 이 필드를 기존으로 수동으로 설정하는 것이 `좋습니다`.

구독한 Operator에서 참조하는 Operator 또는 Operand 이미지에 프라이빗 레지스트리에 대한 액세스 권한이 필요한 경우 클러스터의 모든 네임스페이스 또는 개별 대상 테넌트 네임스페이스에 액세스 권한을 제공하면 됩니다.

클러스터의 모든 네임스페이스에 액세스 권한을 제공하려면 `openshift-config` 네임스페이스의 글로벌 클러스터 가져오기 보안에 인증 세부 정보를 추가합니다.

주의

클러스터 리소스는 클러스터의 사용성을 일시적으로 제한할 수 있는 새 글로벌 가져오기 보안에 맞게 조정해야 합니다.

글로벌 가져오기 보안에서 `.dockerconfigjson` 파일을 추출합니다.

```shell-session
$ oc extract secret/pull-secret -n openshift-config --confirm
```

필요한 프라이빗 레지스트리 또는 레지스트리에 대한 인증 자격 증명을 사용하여 `.dockerconfigjson` 파일을 업데이트한 후 새 파일로 저장합니다.

```shell-session
$ cat .dockerconfigjson | \
    jq --compact-output '.auths["<registry>:<port>/<namespace>/"] |= . + {"auth":"<token>"}' \
    > new_dockerconfigjson
```

1. `<registry>:<port>/<namespace>` 를 프라이빗 레지스트리 세부 정보로 교체하고 `<token>` 을 인증 자격 증명으로 교체합니다.

새 파일을 사용하여 글로벌 가져오기 보안을 업데이트합니다.

```shell-session
$ oc set data secret/pull-secret -n openshift-config \
    --from-file=.dockerconfigjson=new_dockerconfigjson
```

개별 네임스페이스를 업데이트하려면 대상 테넌트 네임스페이스에 액세스해야 하는 Operator의 서비스 계정에 가져오기 보안을 추가합니다.

테넌트 네임스페이스에서 `openshift-marketplace` 용으로 생성한 보안을 다시 생성합니다.

```shell-session
$ oc create secret generic <secret_name> \
    -n <tenant_namespace> \
    --from-file=.dockerconfigjson=<path/to/registry/credentials> \
    --type=kubernetes.io/dockerconfigjson
```

테넌트 네임스페이스를 검색하여 Operator의 서비스 계정 이름을 확인합니다.

```shell-session
$ oc get sa -n <tenant_namespace>
```

1. Operator가 개별 네임스페이스에 설치된 경우 해당 네임스페이스를 검색합니다. Operator가 모든 네임스페이스에 설치된 경우 `openshift-operators` 네임스페이스를 검색합니다.

```shell-session
NAME            SECRETS   AGE
builder         2         6m1s
default         2         6m1s
deployer        2         6m1s
etcd-operator   2         5m18s
```

1. 설치된 etcd Operator의 서비스 계정입니다.

Operator의 서비스 계정에 보안을 연결합니다.

```shell-session
$ oc secrets link <operator_sa> \
    -n <tenant_namespace> \
     <secret_name> \
    --for=pull
```

추가 리소스

레지스트리 자격 증명에 사용되는 보안 유형을 포함하여 보안 유형에 대한 자세한 내용은 보안이란? 을 참조하십시오.

이 시크릿 변경에 대한 자세한 내용은 글로벌 클러스터 풀 시크릿 업데이트를 참조하십시오.

가져오기 보안 을 네임스페이스당 서비스 계정에 연결하는 방법에 대한 자세한 내용은 Pod에서 다른 보안 레지스트리의 이미지를 참조하도록 허용 을 참조하십시오.

#### 4.9.7. 기본 소프트웨어 카탈로그 소스 비활성화

Red Hat 및 커뮤니티 프로젝트에서 제공하는 콘텐츠를 소싱하는 Operator 카탈로그는 OpenShift Container Platform 설치 중에 기본적으로 소프트웨어 카탈로그용으로 구성됩니다. 클러스터 관리자는 기본 카탈로그 세트를 비활성화할 수 있습니다.

프로세스

`OperatorHub` 오브젝트에 `disableAllDefaultSources: true` 를 추가하여 기본 카탈로그의 소스를 비활성화합니다.

```shell-session
$ oc patch OperatorHub cluster --type json \
    -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'
```

작은 정보

또는 웹 콘솔을 사용하여 카탈로그 소스를 관리할 수 있습니다. 관리 → 클러스터 설정 → 구성 → OperatorHub 페이지에서 개별 소스 를 생성, 업데이트, 삭제, 비활성화 및 활성화할 수 있는 소스 탭을 클릭합니다.

#### 4.9.8. 사용자 정의 카탈로그 제거

클러스터 관리자는 관련 카탈로그 소스를 삭제하여 이전에 클러스터에 추가된 사용자 정의 Operator 카탈로그를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

웹 콘솔의 관리자 화면에서 관리자 → 클러스터 설정 으로 이동합니다.

구성 탭을 클릭한 다음 OperatorHub 를 클릭합니다.

소스 탭을 클릭합니다.

제거할 카탈로그의 옵션 메뉴

를 선택한 다음 CatalogSource 삭제 를 클릭합니다.

### 4.10. 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

연결이 끊긴 환경의 OpenShift Container Platform 클러스터의 경우 OLM(Operator Lifecycle Manager)은 기본적으로 원격 레지스트리에서 호스팅되는 Red Hat 제공 OperatorHub 소스에 액세스할 수 없습니다. 이러한 원격 소스에는 완전한 인터넷 연결이 필요하기 때문입니다.

그러나 클러스터 관리자는 워크스테이션에 완전한 인터넷 액세스 권한이 있는 경우 연결이 끊긴 환경에서 OLM을 사용하도록 클러스터를 활성화할 수 있습니다. 원격 OperatorHub 콘텐츠를 가져오는 데 완전한 인터넷 액세스 권한이 필요한 워크스테이션은 원격 소스의 로컬 미러를 준비하고 콘텐츠를 미러 레지스트리로 내보내는 데 사용됩니다.

미러 레지스트리는 워크스테이션 및 연결이 끊긴 클러스터 모두에 연결해야 하는 베스천 호스트에 있거나 미러링된 콘텐츠를 연결이 끊긴 환경에 물리적으로 이동하기 위해 이동식 미디어가 필요한 완전히 연결이 끊긴 호스트 또는 에어갭(Airgap) 호스트에 있을 수 있습니다.

이 가이드에서는 연결이 끊긴 환경에서 OLM을 활성화하는 데 필요한 다음 프로세스를 설명합니다.

OLM의 기본 원격 OperatorHub 소스를 비활성화합니다.

완전한 인터넷 액세스가 가능한 워크스테이션을 사용하여 OperatorHub 콘텐츠의 로컬 미러를 생성하고 미러 레지스트리로 내보냅니다.

기본 원격 소스가 아닌 미러 레지스트리의 로컬 소스에서 Operator를 설치하고 관리하도록 OLM을 구성합니다.

연결이 끊긴 환경에서 OLM을 활성화한 후 무제한 워크스테이션을 계속 사용하여 최신 버전의 Operator가 릴리스되면 로컬 OperatorHub 소스를 업데이트할 수 있습니다.

자세한 내용은 연결이 끊긴 환경의 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용 섹션을 참조하십시오.

### 4.11. 카탈로그 소스 Pod 예약

OLM(Operator Lifecycle Manager) 소스 유형 `grpc` 에서 `spec.image` 를 정의하는 경우 Catalog Operator는 정의된 이미지 콘텐츠를 제공하는 Pod를 생성합니다. 기본적으로 이 Pod는 사양에 다음을 정의합니다.

`kubernetes.io/os=linux` 노드 선택기만 있습니다.

기본 우선순위 클래스 이름: `system-cluster-critical`.

허용 오차가 없습니다.

관리자는 `CatalogSource` 오브젝트의 선택적 `spec.grpcPodConfig` 섹션의 필드를 수정하여 이러한 값을 덮어쓸 수 있습니다.

중요

Marketplace Operator인 `openshift-marketplace` 는 기본 `OperatorHub` CR(사용자 정의 리소스)을 관리합니다. 이 CR은 `CatalogSource` 오브젝트를 관리합니다.

`CatalogSource` 오브젝트의 `spec.grpcPodConfig` 섹션에서 필드를 수정하려고 하면 Marketplace Operator가 이러한 수정 사항을 자동으로 되돌립니다.

기본적으로 `CatalogSource` 오브젝트의 `spec.grpcPodConfig` 섹션에서 필드를 수정하면 Marketplace Operator에서 이러한 변경 사항을 자동으로 되돌립니다.

`CatalogSource` 오브젝트에 영구 변경 사항을 적용하려면 먼저 기본 `CatalogSource` 오브젝트를 비활성화해야 합니다.

추가 리소스

OLM 개념 및 리소스 → 카탈로그 소스

#### 4.11.1. 로컬 수준에서 기본 CatalogSource 오브젝트 비활성화

기본 `CatalogSource` 오브젝트를 비활성화하여 로컬 수준에서 catalog source Pod와 같은 `CatalogSource` 오브젝트에 영구 변경 사항을 적용할 수 있습니다. 기본 `CatalogSource` 오브젝트 구성이 조직의 요구 사항을 충족하지 않는 경우 기본 구성을 고려하십시오.

기본적으로 `CatalogSource` 오브젝트의 `spec.grpcPodConfig` 섹션에서 필드를 수정하면 Marketplace Operator에서 이러한 변경 사항을 자동으로 되돌립니다.

Marketplace Operator인 `openshift-marketplace` 는 `OperatorHub` 의 기본 CR(사용자 정의 리소스)을 관리합니다. `OperatorHub` 는 `CatalogSource` 오브젝트를 관리합니다.

`CatalogSource` 오브젝트에 영구 변경 사항을 적용하려면 먼저 기본 `CatalogSource` 오브젝트를 비활성화해야 합니다.

프로세스

로컬 수준에서 기본 `CatalogSource` 오브젝트를 모두 비활성화하려면 다음 명령을 입력합니다.

```shell-session
$ oc patch operatorhub cluster -p '{"spec": {"disableAllDefaultSources": true}}' --type=merge
```

참고

모든 `CatalogSource` 오브젝트를 비활성화하거나 특정 오브젝트를 비활성화하도록 기본 `OperatorHub` CR을 구성할 수도 있습니다.

추가 리소스

OperatorHub 사용자 정의 리소스

기본 OperatorHub 카탈로그 소스 비활성화

#### 4.11.2. 카탈로그 소스 Pod의 노드 선택기 덮어쓰기

사전 요구 사항

`spec.image` 가 있는 소스 유형 `grpc` 의 `CatalogSource` 오브젝트가 정의됩니다.

프로세스

`CatalogSource` 오브젝트를 편집하고 다음을 포함하도록 `spec.grpcPodConfig` 섹션을 추가하거나 수정합니다.

```yaml
grpcPodConfig:
    nodeSelector:
      custom_label: <label>
```

여기서 `<label` >은 카탈로그 소스 Pod가 스케줄링에 사용할 노드 선택기의 레이블입니다.

추가 리소스

노드 선택기를 사용하여 특정 노드에 Pod 배치

#### 4.11.3. 카탈로그 소스 Pod의 우선순위 클래스 이름 덮어쓰기

사전 요구 사항

`spec.image` 가 있는 소스 유형 `grpc` 의 `CatalogSource` 오브젝트가 정의됩니다.

프로세스

`CatalogSource` 오브젝트를 편집하고 다음을 포함하도록 `spec.grpcPodConfig` 섹션을 추가하거나 수정합니다.

```yaml
grpcPodConfig:
    priorityClassName: <priority_class>
```

여기서 `<priority_class` >는 다음 중 하나입니다.

Kubernetes에서 제공하는 기본 우선 순위 클래스 중 하나: `system-cluster-critical` 또는 `system-node-critical`

기본 우선 순위를 할당할 빈 세트(`""`)

기존 및 사용자 정의 우선순위 클래스

참고

이전에는 재정의할 수 있는 유일한 Pod 예약 매개변수가 `priorityClassName` 이었습니다. 이 작업은 `operatorframework.io/priorityclass` 주석을 `CatalogSource` 오브젝트에 추가하여 수행되었습니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: example-catalog
  namespace: openshift-marketplace
  annotations:
    operatorframework.io/priorityclass: system-cluster-critical
```

`CatalogSource` 오브젝트에서 주석과 `spec.grpcPodConfig.priorityClassName` 을 모두 정의하는 경우 주석이 구성 매개변수보다 우선합니다.

추가 리소스

Pod 우선순위 클래스

#### 4.11.4. 카탈로그 소스 Pod에 대한 허용 오차 덮어쓰기

사전 요구 사항

`spec.image` 가 있는 소스 유형 `grpc` 의 `CatalogSource` 오브젝트가 정의됩니다.

프로세스

`CatalogSource` 오브젝트를 편집하고 다음을 포함하도록 `spec.grpcPodConfig` 섹션을 추가하거나 수정합니다.

```yaml
grpcPodConfig:
    tolerations:
      - key: "<key_name>"
        operator: "<operator_type>"
        value: "<value>"
        effect: "<effect>"
```

추가 리소스

테인트(Taints) 및 톨러레이션(Tolerations)의 이해

### 4.12. Operator 문제 해결

Operator 문제가 발생하면 Operator 서브스크립션 상태를 확인하십시오. 클러스터 전체에서 Operator Pod 상태를 확인하고 진단을 위해 Operator 로그를 수집합니다.

#### 4.12.1. Operator 서브스크립션 상태 유형

서브스크립션은 다음 상태 유형을 보고할 수 있습니다.

| 상태 | 설명 |
| --- | --- |
| `CatalogSourcesUnhealthy` | 해결에 사용되는 일부 또는 모든 카탈로그 소스가 정상 상태가 아닙니다. |
| `InstallPlanMissing` | 서브스크립션 설치 계획이 없습니다. |
| `InstallPlanPending` | 서브스크립션 설치 계획이 설치 대기 중입니다. |
| `InstallPlanFailed` | 서브스크립션 설치 계획이 실패했습니다. |
| `ResolutionFailed` | 서브스크립션의 종속성 확인에 실패했습니다. |

참고

기본 OpenShift Container Platform 클러스터 Operator는 CVO(Cluster Version Operator)에서 관리하며 `Subscription` 오브젝트가 없습니다. 애플리케이션 Operator는 OLM(Operator Lifecycle Manager)에서 관리하며 `Subscription` 오브젝트가 있습니다.

추가 리소스

카탈로그 상태 요구 사항

#### 4.12.2. CLI를 사용하여 Operator 서브스크립션 상태 보기

CLI를 사용하여 Operator 서브스크립션 상태를 볼 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

Operator 서브스크립션을 나열합니다.

```shell-session
$ oc get subs -n <operator_namespace>
```

아래 명령을 사용하여 `Subscription` 리소스를 검사합니다.

```shell
oc describe
```

```shell-session
$ oc describe sub <subscription_name> -n <operator_namespace>
```

명령 출력에서 Operator 서브스크립션 조건 유형의 상태에 대한 `Conditions` 섹션을 확인합니다. 다음 예에서 사용 가능한 모든 카탈로그 소스가 정상이므로 `CatalogSourcesUnhealthy` 조건 유형의 상태가 `false` 입니다.

```shell-session
Name:         cluster-logging
Namespace:    openshift-logging
Labels:       operators.coreos.com/cluster-logging.openshift-logging=
Annotations:  <none>
API Version:  operators.coreos.com/v1alpha1
Kind:         Subscription
# ...
Conditions:
   Last Transition Time:  2019-07-29T13:42:57Z
   Message:               all available catalogsources are healthy
   Reason:                AllCatalogSourcesHealthy
   Status:                False
   Type:                  CatalogSourcesUnhealthy
# ...
```

참고

기본 OpenShift Container Platform 클러스터 Operator는 CVO(Cluster Version Operator)에서 관리하며 `Subscription` 오브젝트가 없습니다. 애플리케이션 Operator는 OLM(Operator Lifecycle Manager)에서 관리하며 `Subscription` 오브젝트가 있습니다.

#### 4.12.3. CLI를 사용하여 Operator 카탈로그 소스 상태 보기

CLI를 사용하여 Operator 카탈로그 소스의 상태를 볼 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

네임스페이스의 카탈로그 소스를 나열합니다. 예를 들어 클러스터 전체 카탈로그 소스에 사용되는 `openshift-marketplace` 네임스페이스를 확인할 수 있습니다.

```shell-session
$ oc get catalogsources -n openshift-marketplace
```

```shell-session
NAME                  DISPLAY               TYPE   PUBLISHER   AGE
certified-operators   Certified Operators   grpc   Red Hat     55m
community-operators   Community Operators   grpc   Red Hat     55m
example-catalog       Example Catalog       grpc   Example Org 2m25s
redhat-operators      Red Hat Operators     grpc   Red Hat     55m
```

아래 명령을 사용하여 카탈로그 소스에 대한 자세한 내용 및 상태를 가져옵니다.

```shell
oc describe
```

```shell-session
$ oc describe catalogsource example-catalog -n openshift-marketplace
```

```shell-session
Name:         example-catalog
Namespace:    openshift-marketplace
Labels:       <none>
Annotations:  operatorframework.io/managed-by: marketplace-operator
              target.workload.openshift.io/management: {"effect": "PreferredDuringScheduling"}
API Version:  operators.coreos.com/v1alpha1
Kind:         CatalogSource
# ...
Status:
  Connection State:
    Address:              example-catalog.openshift-marketplace.svc:50051
    Last Connect:         2021-09-09T17:07:35Z
    Last Observed State:  TRANSIENT_FAILURE
  Registry Service:
    Created At:         2021-09-09T17:05:45Z
    Port:               50051
    Protocol:           grpc
    Service Name:       example-catalog
    Service Namespace:  openshift-marketplace
# ...
```

앞의 예제 출력에서 마지막으로 관찰된 상태는 `TRANSIENT_FAILURE` 입니다. 이 상태는 카탈로그 소스에 대한 연결을 설정하는 데 문제가 있음을 나타냅니다.

카탈로그 소스가 생성된 네임스페이스의 Pod를 나열합니다.

```shell-session
$ oc get pods -n openshift-marketplace
```

```shell-session
NAME                                    READY   STATUS             RESTARTS   AGE
certified-operators-cv9nn               1/1     Running            0          36m
community-operators-6v8lp               1/1     Running            0          36m
marketplace-operator-86bfc75f9b-jkgbc   1/1     Running            0          42m
example-catalog-bwt8z                   0/1     ImagePullBackOff   0          3m55s
redhat-operators-smxx8                  1/1     Running            0          36m
```

카탈로그 소스가 네임스페이스에 생성되면 해당 네임스페이스에 카탈로그 소스의 Pod가 생성됩니다. 위 예제 출력에서 `example-catalog-bwt8z` pod의 상태는 `ImagePullBackOff` 입니다. 이 상태는 카탈로그 소스의 인덱스 이미지를 가져오는 데 문제가 있음을 나타냅니다.

자세한 정보는 아래 명령을 사용하여 Pod를 검사합니다.

```shell
oc describe
```

```shell-session
$ oc describe pod example-catalog-bwt8z -n openshift-marketplace
```

```shell-session
Name:         example-catalog-bwt8z
Namespace:    openshift-marketplace
Priority:     0
Node:         ci-ln-jyryyg2-f76d1-ggdbq-worker-b-vsxjd/10.0.128.2
...
Events:
  Type     Reason          Age                From               Message
  ----     ------          ----               ----               -------
  Normal   Scheduled       48s                default-scheduler  Successfully assigned openshift-marketplace/example-catalog-bwt8z to ci-ln-jyryyf2-f76d1-fgdbq-worker-b-vsxjd
  Normal   AddedInterface  47s                multus             Add eth0 [10.131.0.40/23] from openshift-sdn
  Normal   BackOff         20s (x2 over 46s)  kubelet            Back-off pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          20s (x2 over 46s)  kubelet            Error: ImagePullBackOff
  Normal   Pulling         8s (x3 over 47s)   kubelet            Pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          8s (x3 over 47s)   kubelet            Failed to pull image "quay.io/example-org/example-catalog:v1": rpc error: code = Unknown desc = reading manifest v1 in quay.io/example-org/example-catalog: unauthorized: access to the requested resource is not authorized
  Warning  Failed          8s (x3 over 47s)   kubelet            Error: ErrImagePull
```

앞의 예제 출력에서 오류 메시지는 권한 부여 문제로 인해 카탈로그 소스의 인덱스 이미지를 성공적으로 가져오지 못한 것으로 표시됩니다. 예를 들어 인덱스 이미지는 로그인 인증 정보가 필요한 레지스트리에 저장할 수 있습니다.

추가 리소스

Operator Lifecycle Manager 개념 및 리소스 → 카탈로그 소스

gRPC 문서: 연결 상태

프라이빗 레지스트리에서 Operator용 이미지에 액세스

#### 4.12.4. Operator Pod 상태 쿼리

클러스터 내의 Operator Pod 및 해당 상태를 나열할 수 있습니다. 자세한 Operator Pod 요약을 수집할 수도 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

API 서비스가 작동하고 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

클러스터에서 실행중인 Operator를 나열합니다. 출력에는 Operator 버전, 가용성 및 가동 시간 정보가 포함됩니다.

```shell-session
$ oc get clusteroperators
```

Operator의 네임스페이스에서 실행 중인 Operator Pod와 Pod 상태, 재시작, 경과 시간을 표시합니다.

```shell-session
$ oc get pod -n <operator_namespace>
```

자세한 Operator Pod 요약을 출력합니다.

```shell-session
$ oc describe pod <operator_pod_name> -n <operator_namespace>
```

Operator 문제가 노드와 관련된 경우 해당 노드에서 Operator 컨테이너 상태를 쿼리합니다.

노드의 디버그 Pod를 시작합니다.

```shell-session
$ oc debug node/my-node
```

디버그 쉘 내에서 `/host` 를 root 디렉터리로 설정합니다. 디버그 Pod는 Pod 내의 `/host` 에 호스트의 루트 파일 시스템을 마운트합니다. root 디렉토리를 `/host` 로 변경하면 호스트의 실행 경로에 포함된 바이너리를 실행할 수 있습니다.

```shell-session
# chroot /host
```

참고

RHCOS(Red Hat Enterprise Linux CoreOS)를 실행하는 OpenShift Container Platform 4.20 클러스터 노드는 변경할 수 없으며 Operator를 사용하여 클러스터 변경 사항을 적용합니다. SSH를 사용하여 클러스터 노드에 액세스하는 것은 권장되지 않습니다.

그러나 OpenShift Container Platform API를 사용할 수 없거나 kubelet이 대상 노드에서 제대로 작동하지 않는 경우 작업이 영향을 받습니다. 이러한 상황에서 대신 다음 명령을 사용하여 노드에 액세스할 수 있습니다.

```shell
oc
```

```shell
ssh core @ <node>.<cluster_name>.<base_domain>
```

상태 및 관련 Pod ID를 포함하여 노드의 컨테이너에 대한 세부 정보를 나열합니다.

```shell-session
# crictl ps
```

노드의 특정 Operator 컨테이너에 대한 정보를 나열합니다. 다음 예는 `network-operator` 컨테이너에 대한 정보를 나열합니다.

```shell-session
# crictl ps --name network-operator
```

디버그 쉘을 종료합니다.

#### 4.12.5. Operator 로그 수집

Operator 문제가 발생하면 Operator Pod 로그에서 자세한 진단 정보를 수집할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

API 서비스가 작동하고 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

컨트롤 플레인 또는 컨트롤 플레인 시스템의 정규화된 도메인 이름이 있어야 합니다.

프로세스

Operator의 네임스페이스에서 실행 중인 Operator Pod와 Pod 상태, 재시작, 경과 시간을 표시합니다.

```shell-session
$ oc get pods -n <operator_namespace>
```

Operator Pod의 로그를 검토합니다.

```shell-session
$ oc logs pod/<pod_name> -n <operator_namespace>
```

Operator Pod에 컨테이너가 여러 개 있는 경우 위 명령에 의해 각 컨테이너의 이름이 포함된 오류가 생성됩니다. 개별 컨테이너의 로그를 쿼리합니다.

```shell-session
$ oc logs pod/<operator_pod_name> -c <container_name> -n <operator_namespace>
```

API가 작동하지 않는 경우 대신 SSH를 사용하여 각 컨트롤 플레인 노드에서 Operator Pod 및 컨테이너 로그를 검토합니다. `<master-node>.<cluster_name>.<base_domain>` 을 적절한 값으로 바꿉니다.

각 컨트롤 플레인 노드에 Pod를 나열합니다.

```shell-session
$ ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl pods
```

`Ready` 상태가 표시되지 않는 Operator Pod의 경우 Pod 상태를 자세히 검사합니다. `<operator_pod_id>` 를 이전 명령의 출력에 나열된 Operator Pod의 ID로 교체합니다.

```shell-session
$ ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspectp <operator_pod_id>
```

Operator Pod와 관련된 컨테이너를 나열합니다.

```shell-session
$ ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl ps --pod=<operator_pod_id>
```

`Ready` 상태가 표시되지 않는 Operator 컨테이너의 경우 컨테이너 상태를 자세히 검사합니다. `<container_id>` 를 이전 명령의 출력에 나열된 컨테이너 ID로 바꿉니다.

```shell-session
$ ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspect <container_id>
```

`Ready` 상태가 표시되지 않는 Operator 컨테이너의 로그를 확인합니다. `<container_id>` 를 이전 명령의 출력에 나열된 컨테이너 ID로 바꿉니다.

```shell-session
$ ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>
```

참고

RHCOS(Red Hat Enterprise Linux CoreOS)를 실행하는 OpenShift Container Platform 4.20 클러스터 노드는 변경할 수 없으며 Operator를 사용하여 클러스터 변경 사항을 적용합니다. SSH를 사용하여 클러스터 노드에 액세스하는 것은 권장되지 않습니다.

SSH를 통해 진단 데이터를 수집하기 전에 및 기타 아래 명령을 실행하여 충분한 데이터를 수집할 수 있는지 확인하십시오. 그러나 OpenShift Container Platform API를 사용할 수 없거나 kubelet이 대상 노드에서 제대로 작동하지 않는 경우 작업이 영향을 받습니다.

```shell
oc adm must gather
```

```shell
oc
```

```shell
oc
```

이러한 상황에서 다음 명령을 사용하여 노드에 액세스할 수 있습니다.

```shell
ssh core@<node>.<cluster_name>.<base_domain>
```

#### 4.12.6. Machine Config Operator가 자동으로 재부팅되지 않도록 비활성화

Machine Config Operator(MCO)에서 구성을 변경하는 경우 변경 사항을 적용하려면 RHCOS(Red Hat Enterprise Linux CoreOS)를 재부팅해야 합니다. 구성 변경이 자동이든 수동이든 RHCOS 노드는 일시 중지되지 않는 한 자동으로 재부팅됩니다.

참고

MCO가 다음 변경 사항을 감지하면 노드를 드레이닝하거나 재부팅하지 않고 업데이트를 적용합니다.

머신 구성의 `spec.config.passwd.users.sshAuthorizedKeys` 매개변수에서 SSH 키 변경

`openshift-config` 네임 스페이스에서 글로벌 풀 시크릿 또는 풀 시크릿 관련 변경 사항

Kubernetes API Server Operator의 `/etc/kubernetes/kubelet-ca.crt` 인증 기관(CA) 자동 교체

MCO가 `ImageDigestMirrorSet`, `ImageTagMirrorSet` 또는 `ImageContentSourcePolicy` 개체 편집과 같은 `/etc/containers/registries.conf` 파일의 변경을 감지하면 해당 노드를 비우고 변경 사항을 적용한 다음 노드를 분리합니다. 다음 변경에는 노드 드레이닝이 발생하지 않습니다.

각 미러에 대해 설정된 `pull-from-mirror = "digest-only"` 매개변수를 사용하여 레지스트리를 추가합니다.

레지스트리에 설정된 `pull-from-mirror = "digest-only"` 매개변수를 사용하여 미러를 추가합니다.

`unqualified-search-registries` 목록에 항목이 추가되었습니다.

원치 않는 중단을 방지하기 위해 Operator에서 머신 구성을 변경한 후 자동 재부팅되지 않도록 머신 구성 풀(MCP)을 수정할 수 있습니다.

#### 4.12.6.1. 콘솔을 사용하여 Machine Config Operator가 자동으로 재부팅되지 않도록 비활성화

MCO(Machine Config Operator)에서 원하지 않는 변경을 방지하기 위해 OpenShift Container Platform 웹 콘솔을 사용하여 MCO가 해당 풀의 노드를 변경하지 않도록 MCP(머신 구성 풀)를 수정할 수 있습니다. 이렇게 하면 일반적으로 MCO 업데이트 프로세스의 일부인 재부팅을 방지할 수 있습니다.

참고

Machine Config Operator가 자동으로 재부팅되지 않도록 설정할 때 두 번째 `참고` 사항을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

자동 MCO 업데이트 재부팅을 일시 중지하거나 일시 중지 해제하려면 다음을 수행합니다.

자동 재부팅 프로세스를 일시 중지합니다.

`cluster-admin` 역할의 사용자로 OpenShift Container Platform 웹 콘솔에 로그인합니다.

컴퓨팅 → MachineConfigPools 를 클릭합니다.

MachineConfigPools 페이지에서 재부팅을 일시 정지하려는 노드에 따라 마스터 또는 작업자 를 클릭합니다.

마스터 또는 작업자 페이지에서 YAML 을 클릭합니다.

YAML에서 `spec.paused` 필드를 `true` 로 업데이트합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: true
# ...
```

1. `spec.paused` 필드를 `true` 로 업데이트하여 재부팅을 일시 중지합니다.

MCP가 일시 중지되었는지 확인하려면 MachineConfigPools 페이지로 돌아갑니다.

MachineConfigPools 페이지에서 일시 중지된 열에 수정한 MCP에 대해 True 가 보고됩니다.

일시 중지된 동안 MCP에 보류 중인 변경 사항이 있는 경우 Updated 열은 False 이고 Updating 열은 False 입니다. Updated 이 True 이고 Updating 이 False 인 경우 보류 중인 변경 사항이 없습니다.

중요

Updated 및 Updating 열이 모두 False 인 보류 중인 변경 사항이 있는 경우 최대한 빨리 재부팅할 수 있도록 유지 관리 기간을 예약하는 것이 좋습니다. 자동 재부팅 프로세스를 일시 중지 해제하려면 다음 단계를 사용하여 마지막 재부팅 이후 대기열에 있는 변경 사항을 적용합니다.

자동 재부팅 프로세스의 일시 중지를 해제합니다.

`cluster-admin` 역할의 사용자로 OpenShift Container Platform 웹 콘솔에 로그인합니다.

컴퓨팅 → MachineConfigPools 를 클릭합니다.

MachineConfigPools 페이지에서 재부팅을 일시 정지하려는 노드에 따라 마스터 또는 작업자 를 클릭합니다.

마스터 또는 작업자 페이지에서 YAML 을 클릭합니다.

YAML에서 `spec.paused` 필드를 `false` 로 업데이트합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: false
# ...
```

1. 재부팅을 허용하도록 `spec.paused` 필드를 `false` 로 업데이트합니다.

참고

MCP의 일시 중지를 해제하면 MCO는 모든 일시 중지된 변경 사항이 필요에 따라 RHCOS(Red Hat Enterprise Linux CoreOS) 재부팅을 적용합니다.

MCP가 일시 중지되었는지 확인하려면 MachineConfigPools 페이지로 돌아갑니다.

MachineConfigPools 페이지에서 일시 중지된 열에 수정한 MCP에 대해 False 를 보고합니다.

MCP가 보류 중인 변경 사항을 적용하는 경우 Updated 열은 False 이고 Updating 인 열은 True 입니다. 업데이트됨 이 True 이고 업데이트 중 이 False 인 경우 추가 변경 사항이 적용되지 않습니다.

#### 4.12.6.2. CLI를 사용하여 Machine Config Operator가 자동으로 재부팅되지 않도록 비활성화

MCO(Machine Config Operator)의 변경으로 인한 원치 않는 중단을 방지하려면 OpenShift CLI(oc)를 사용하여 MCP(Machine Config Pool)를 수정하여 MCO가 해당 풀의 노드를 변경하지 못하도록 할 수 있습니다. 이렇게 하면 일반적으로 MCO 업데이트 프로세스의 일부인 재부팅을 방지할 수 있습니다.

참고

Machine Config Operator가 자동으로 재부팅되지 않도록 설정할 때 두 번째 `참고` 사항을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

자동 MCO 업데이트 재부팅을 일시 중지하거나 일시 중지 해제하려면 다음을 수행합니다.

자동 재부팅 프로세스를 일시 중지합니다.

`MachineConfigPool` 사용자 정의 리소스를 업데이트하여 `spec.paused` 필드를 `true` 로 설정합니다.

```shell-session
$ oc patch --type=merge --patch='{"spec":{"paused":true}}' machineconfigpool/master
```

```shell-session
$ oc patch --type=merge --patch='{"spec":{"paused":true}}' machineconfigpool/worker
```

MCP가 일시 중지되었는지 확인합니다.

```shell-session
$ oc get machineconfigpool/master --template='{{.spec.paused}}'
```

```shell-session
$ oc get machineconfigpool/worker --template='{{.spec.paused}}'
```

```shell-session
true
```

`spec.paused` 필드가 `true` 이고 MCP가 일시 중지되었습니다.

MCP에 보류 중인 변경 사항이 있는지 확인합니다.

```shell-session
# oc get machineconfigpool
```

```plaintext
NAME     CONFIG                                             UPDATED   UPDATING
master   rendered-master-33cf0a1254318755d7b48002c597bf91   True      False
worker   rendered-worker-e405a5bdb0db1295acea08bcca33fa60   False     False
```

UPDATED 열이 False 이고 UPDATING 이 False 이면 보류 중인 변경 사항이 있습니다. UPDATED 가 True 이고 UPDATING 이 False 인 경우 보류 중인 변경 사항이 없습니다. 이전 예에서 작업자 노드에 보류 중인 변경 사항이 있습니다. 컨트롤 플레인 노드에는 보류 중인 변경 사항이 없습니다.

중요

Updated 및 Updating 열이 모두 False 인 보류 중인 변경 사항이 있는 경우 최대한 빨리 재부팅할 수 있도록 유지 관리 기간을 예약하는 것이 좋습니다. 자동 재부팅 프로세스를 일시 중지 해제하려면 다음 단계를 사용하여 마지막 재부팅 이후 대기열에 있는 변경 사항을 적용합니다.

자동 재부팅 프로세스의 일시 중지를 해제합니다.

`MachineConfigPool` 사용자 정의 리소스에서 `spec.paused` 필드를 `false` 로 업데이트합니다.

```shell-session
$ oc patch --type=merge --patch='{"spec":{"paused":false}}' machineconfigpool/master
```

```shell-session
$ oc patch --type=merge --patch='{"spec":{"paused":false}}' machineconfigpool/worker
```

참고

MCP의 일시 중지를 해제하면 MCO는 일시 중지된 모든 변경 사항을 적용하고 필요에 따라 RHCOS(Red Hat Enterprise Linux CoreOS)를 재부팅합니다.

MCP가 일시 중지되지 않았는지 확인합니다.

```shell-session
$ oc get machineconfigpool/master --template='{{.spec.paused}}'
```

```shell-session
$ oc get machineconfigpool/worker --template='{{.spec.paused}}'
```

```shell-session
false
```

`spec.paused` 필드가 `false` 이고 MCP가 일시 중지되지 않습니다.

MCP에 보류 중인 변경 사항이 있는지 확인합니다.

```shell-session
$ oc get machineconfigpool
```

```plaintext
NAME     CONFIG                                   UPDATED  UPDATING
master   rendered-master-546383f80705bd5aeaba93   True     False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False    True
```

MCP에서 보류 중인 변경 사항을 적용하는 경우 UPDATED 열은 False 이고 UPDATING 열은 True 입니다. UPDATED 가 True 이고 UPDATING 이 False 이면 추가 변경 사항이 없습니다. 이전 예에서 MCO는 작업자 노드를 업데이트하고 있습니다.

#### 4.12.7. 실패한 서브스크립션 새로 고침

OLM(Operator Lifecycle Manager)에서는 네트워크상에서 액세스할 수 없는 이미지를 참조하는 Operator를 구독하는 경우 `openshift-marketplace` 네임스페이스에 다음 오류로 인해 실패하는 작업을 확인할 수 있습니다.

```shell-session
ImagePullBackOff for
Back-off pulling image "example.com/openshift4/ose-elasticsearch-operator-bundle@sha256:6d2587129c846ec28d384540322b40b05833e7e00b25cca584e004af9a1d292e"
```

```shell-session
rpc error: code = Unknown desc = error pinging docker registry example.com: Get "https://example.com/v2/": dial tcp: lookup example.com on 10.0.0.1:53: no such host
```

결과적으로 서브스크립션이 이러한 장애 상태에 고착되어 Operator를 설치하거나 업그레이드할 수 없습니다.

서브스크립션, CSV(클러스터 서비스 버전) 및 기타 관련 오브젝트를 삭제하여 실패한 서브스크립션을 새로 고칠 수 있습니다. 서브스크립션을 다시 생성하면 OLM에서 올바른 버전의 Operator를 다시 설치합니다.

사전 요구 사항

액세스할 수 없는 번들 이미지를 가져올 수 없는 실패한 서브스크립션이 있습니다.

올바른 번들 이미지에 액세스할 수 있는지 확인했습니다.

프로세스

Operator가 설치된 네임스페이스에서 `Subscription` 및 `ClusterServiceVersion` 오브젝트의 이름을 가져옵니다.

```shell-session
$ oc get sub,csv -n <namespace>
```

```shell-session
NAME                                                       PACKAGE                  SOURCE             CHANNEL
subscription.operators.coreos.com/elasticsearch-operator   elasticsearch-operator   redhat-operators   5.0

NAME                                                                         DISPLAY                            VERSION    REPLACES   PHASE
clusterserviceversion.operators.coreos.com/elasticsearch-operator.5.0.0-65   OpenShift Elasticsearch Operator   5.0.0-65              Succeeded
```

서브스크립션을 삭제합니다.

```shell-session
$ oc delete subscription <subscription_name> -n <namespace>
```

클러스터 서비스 버전을 삭제합니다.

```shell-session
$ oc delete csv <csv_name> -n <namespace>
```

`openshift-marketplace` 네임스페이스에서 실패한 모든 작업 및 관련 구성 맵의 이름을 가져옵니다.

```shell-session
$ oc get job,configmap -n openshift-marketplace
```

```shell-session
NAME                                                                        COMPLETIONS   DURATION   AGE
job.batch/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   1/1           26s        9m30s

NAME                                                                        DATA   AGE
configmap/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   3      9m30s
```

작업을 삭제합니다.

```shell-session
$ oc delete job <job_name> -n openshift-marketplace
```

이렇게 하면 액세스할 수 없는 이미지를 가져오려는 Pod가 다시 생성되지 않습니다.

구성 맵을 삭제합니다.

```shell-session
$ oc delete configmap <configmap_name> -n openshift-marketplace
```

웹 콘솔의 소프트웨어 카탈로그를 사용하여 Operator를 다시 설치합니다.

검증

Operator가 제대로 다시 설치되었는지 확인합니다.

```shell-session
$ oc get sub,csv,installplan -n <namespace>
```

#### 4.12.8. 실패한 제거 후 Operator 다시 설치

동일한 Operator를 다시 설치하기 전에 Operator를 성공적으로 제거하고 완전히 제거해야 합니다. Operator를 완전히 제거하지 못하면 프로젝트 또는 네임스페이스와 같은 리소스가 "종료 중" 상태에 고정되어 "리소스 해결 오류" 메시지가 나타날 수 있습니다. 예를 들면 다음과 같습니다.

```plaintext
...
    message: 'Failed to delete all resource types, 1 remaining: Internal error occurred:
      error resolving resource'
...
```

이러한 유형의 문제로 인해 Operator가 다시 설치되지 않을 수 있습니다.

주의

네임스페이스를 강제로 삭제해도 "종료 중" 상태 문제가 해결되지 않고 불안정하거나 예측할 수 없는 클러스터 동작이 발생할 수 있으므로 네임스페이스 삭제를 방해할 수 있는 관련 리소스를 찾는 것이 좋습니다. 자세한 내용은 Red Hat Knowledgebase Solution #4165791 을 참조하십시오.

다음 절차에서는 이전 Operator 설치의 기존 CRD(사용자 정의 리소스 정의)에서 관련 네임스페이스가 삭제되지 않기 때문에 Operator를 다시 설치할 수 없는 경우 문제를 해결하는 방법을 보여줍니다.

프로세스

"종료 중" 상태로 중단된 Operator와 관련된 네임스페이스가 있는지 확인합니다.

```shell-session
$ oc get namespaces
```

```plaintext
operator-ns-1                                       Terminating
```

실패한 제거 후에도 여전히 존재하는 Operator와 관련된 CRD가 있는지 확인합니다.

```shell-session
$ oc get crds
```

참고

CRD는 글로벌 클러스터 정의입니다. CRD와 관련된 실제 CR(사용자 정의 리소스) 인스턴스는 다른 네임스페이스에 있거나 글로벌 클러스터 인스턴스일 수 있습니다.

Operator에서 제공하거나 관리하는 CRD가 있고 제거 후 삭제해야 하는 CRD가 있는 경우 CRD를 삭제합니다.

```shell-session
$ oc delete crd <crd_name>
```

제거 후에도 여전히 존재하는 Operator와 관련된 나머지 CR 인스턴스가 있는지 확인하고 CR을 삭제합니다.

검색할 CR 유형은 제거 후 결정하기 어려울 수 있으며 Operator에서 관리하는 CRD를 알아야 할 수 있습니다. 예를 들어 `EtcdCluster` CRD를 제공하는 etcd Operator의 설치 제거 문제를 해결하는 경우 네임스페이스에서 나머지 `EtcdCluster` CR을 검색할 수 있습니다.

```shell-session
$ oc get EtcdCluster -n <namespace_name>
```

또는 모든 네임스페이스에서 검색할 수 있습니다.

```shell-session
$ oc get EtcdCluster --all-namespaces
```

제거해야 하는 나머지 CR이 있는 경우 인스턴스를 삭제합니다.

```shell-session
$ oc delete <cr_name> <cr_instance_name> -n <namespace_name>
```

네임스페이스 삭제가 성공적으로 해결되었는지 확인합니다.

```shell-session
$ oc get namespace <namespace_name>
```

중요

네임스페이스 또는 기타 Operator 리소스가 여전히 제거되지 않은 경우 Red Hat 지원팀에 문의하십시오.

웹 콘솔의 소프트웨어 카탈로그를 사용하여 Operator를 다시 설치합니다.

검증

Operator가 제대로 다시 설치되었는지 확인합니다.

```shell-session
$ oc get sub,csv,installplan -n <namespace>
```

추가 리소스

클러스터에서 Operator 삭제

클러스터에 Operator 추가

#### 5.1.1. 클라우드 공급자의 Operator에 대한 토큰 인증

많은 클라우드 공급자는 단기적이고 제한된 권한 보안 인증 정보를 제공하는 계정 토큰을 사용하여 인증을 활성화할 수 있습니다.

OpenShift Container Platform에는 클라우드 공급자 인증 정보를 CRD(사용자 정의 리소스 정의)로 관리하는 CCO(Cloud Credential Operator)가 포함되어 있습니다.

CCO는 `CredentialsRequest` CR(사용자 정의 리소스)에서 동기화되므로 OpenShift Container Platform 구성 요소가 필요한 특정 권한으로 클라우드 공급자 인증 정보를 요청할 수 있습니다.

이전 버전에서는 CCO가 수동 모드인 클러스터에서 OLM(Operator Lifecycle Manager)에서 관리하는 Operator에 종종 사용자가 필요한 클라우드 인증 정보를 수동으로 프로비저닝하는 방법에 대한 자세한 지침이 제공되었습니다.

OpenShift Container Platform 4.14부터 CCO는 특정 클라우드 공급자에서 단기 인증 정보를 사용하도록 활성화된 클러스터에서 실행되는 시기를 감지할 수 있습니다. 그러면 Operator 작성자가 Operator에서 업데이트된 CCO를 지원할 수 있는 경우 특정 인증 정보를 반자동으로 프로비저닝할 수 있습니다.

추가 리소스

Cloud Credential Operator 정보

AWS STS를 사용하여 OLM 관리 Operator의 CCO 기반 워크플로

Microsoft Entra Workload ID가 있는 OLM 관리 Operator의 CCO 기반 워크플로

GCP 워크로드 ID를 사용하는 OLM 관리 Operator의 CCO 기반 워크플로

#### 5.1.2. AWS STS를 사용하여 OLM 관리 Operator의 CCO 기반 워크플로

AWS에서 실행되는 OpenShift Container Platform 클러스터가 STS(Security Token Service) 모드인 경우 클러스터가 AWS 및 OpenShift Container Platform의 기능을 사용하여 애플리케이션 수준에서 IAM 역할을 사용하고 있음을 의미합니다.

STS를 사용하면 애플리케이션에서 IAM 역할을 가정할 수 있는 JSON 웹 토큰(JWT)을 제공할 수 있습니다.

JWT에는 서비스 계정에 대한 임시 부여 권한을 허용하는 `sts:AssumeRoleWithWebIdentity` IAM 작업에 대한 Amazon Resource Name(ARN)이 포함됩니다. JWT에는 AWS IAM에서 검증할 수 있는 `ProjectedServiceAccountToken` 의 서명 키가 포함되어 있습니다.

서명된 서비스 계정 토큰 자체는 AWS 역할을 가정하는 데 필요한 JWT로 사용됩니다.

CCO(Cloud Credential Operator)는 기본적으로 클라우드 공급자에서 실행되는 OpenShift Container Platform 클러스터에 설치된 클러스터 Operator입니다. STS의 목적을 위해 CCO는 다음 기능을 제공합니다.

STS 지원 클러스터에서 실행 중인 시기 감지

AWS 리소스에 대한 Operator 액세스 권한을 부여하는 데 필요한 정보를 제공하는 필드가 있는지 `CredentialsRequest` 오브젝트를 확인합니다.

CCO는 수동 모드에서도 이 탐지를 수행합니다. 올바르게 구성되면 CCO는 Operator 네임스페이스에 필요한 액세스 정보가 있는 `Secret` 오브젝트를 생성합니다.

OpenShift Container Platform 4.14부터 CCO는 STS 워크플로우에 필요한 정보가 포함된 `시크릿` 생성을 요청할 수 있는 `CredentialsRequest` 오브젝트의 확장된 사용을 통해 이 작업을 반자동화할 수 있습니다. 사용자는 웹 콘솔 또는 CLI에서 Operator를 설치할 때 역할 ARN을 제공할 수 있습니다.

참고

업데이트에 대한 자동 승인이 있는 서브스크립션은 업데이트하기 전에 권한을 변경할 수 있으므로 권장되지 않습니다. 업데이트에 대한 수동 승인이 있는 서브스크립션을 통해 관리자는 최신 버전의 권한을 확인하고 필요한 단계를 수행한 다음 업데이트할 수 있습니다.

OpenShift Container Platform 4.14 이상에서 업데이트된 CCO와 함께 Operator를 사용할 수 있도록 Operator 작성자로서 STS 토큰 인증을 처리하는 것 외에도 사용자와 이전 CCO 버전의 차이점을 처리하도록 코드를 추가해야 합니다(Operator가 STS 활성화되지 않은 경우).

권장되는 방법은 올바르게 채워진 STS 필드를 사용하여 `CredentialsRequest` 오브젝트를 제공하고 CCO가 `시크릿` 을 생성하도록 하는 것입니다.

중요

버전 4.14 이전의 OpenShift Container Platform 클러스터를 지원하려는 경우 CCO 유틸리티(`ccoctl`)를 사용하여 STS-enabling 정보를 사용하여 시크릿을 수동으로 생성하는 방법에 대한 지침을 사용자에게 제공하는 것이 좋습니다. 이전 CCO 버전은 클러스터에서 STS 모드를 인식하지 못하며 시크릿을 생성할 수 없습니다.

코드는 나타나지 않는 시크릿을 확인하고 사용자가 제공한 대체 지침을 따르도록 경고해야 합니다. 자세한 내용은 "Alternative Method" 하위 섹션을 참조하십시오.

추가 리소스

AWS STS를 통한 인증에 대한 OLM 관리 Operator 지원

웹 콘솔을 사용하여 OperatorHub에서 설치

CLI를 사용하여 OperatorHub에서 설치

#### 5.1.2.1. Operator가 AWS STS를 사용하여 CCO 기반 워크플로우를 지원하도록 활성화

OLM(Operator Lifecycle Manager)에서 프로젝트를 실행하도록 프로젝트를 설계하는 Operator 작성자는 CCO(Cloud Credential Operator)를 지원하도록 프로젝트를 사용자 정의하여 Operator를 STS 사용 OpenShift Container Platform 클러스터에서 AWS에 대해 인증할 수 있습니다.

이 방법을 사용하면 Operator에서 `CredentialsRequest` 오브젝트를 생성하고 결과 `Secret` 오브젝트를 읽는 데 필요한 RBAC 권한이 필요합니다.

참고

기본적으로 Operator 배포와 관련된 Pod는 `serviceAccountToken` 볼륨을 마운트하여 결과 `Secret` 오브젝트에서 서비스 계정 토큰을 참조할 수 있습니다.

전제 조건

OpenShift Container Platform 4.14 이상

STS 모드의 클러스터

OLM 기반 Operator 프로젝트

프로세스

Operator 프로젝트의 CSV(`ClusterServiceVersion`) 오브젝트를 업데이트합니다.

Operator에 `CredentialsRequests` 오브젝트를 생성할 수 있는 RBAC 권한이 있는지 확인합니다.

```yaml
# ...
install:
  spec:
    clusterPermissions:
    - rules:
      - apiGroups:
        - "cloudcredential.openshift.io"
        resources:
        - credentialsrequests
        verbs:
        - create
        - delete
        - get
        - list
        - patch
        - update
        - watch
```

AWS STS를 사용하여 이 CCO 기반 워크플로우 방법에 대한 지원을 클레임하려면 다음 주석을 추가합니다.

```yaml
# ...
metadata:
 annotations:
   features.operators.openshift.io/token-auth-aws: "true"
```

Operator 프로젝트 코드를 업데이트합니다.

`Subscription` 오브젝트를 통해 Pod에 설정된 환경 변수에서 ARN 역할을 가져옵니다. 예를 들면 다음과 같습니다.

```plaintext
// Get ENV var
roleARN := os.Getenv("ROLEARN")
setupLog.Info("getting role ARN", "role ARN = ", roleARN)
webIdentityTokenPath := "/var/run/secrets/openshift/serviceaccount/token"
```

`CredentialsRequest` 개체를 패치하고 적용할 준비가 되었는지 확인합니다. 예를 들면 다음과 같습니다.

```plaintext
import (
   minterv1 "github.com/openshift/cloud-credential-operator/pkg/apis/cloudcredential/v1"
   corev1 "k8s.io/api/core/v1"
   metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

var in = minterv1.AWSProviderSpec{
   StatementEntries: []minterv1.StatementEntry{
      {
         Action: []string{
            "s3:*",
         },
         Effect:   "Allow",
         Resource: "arn:aws:s3:*:*:*",
      },
   },
    STSIAMRoleARN: "<role_arn>",
}

var codec = minterv1.Codec
var ProviderSpec, _ = codec.EncodeProviderSpec(in.DeepCopyObject())

const (
   name      = "<credential_request_name>"
   namespace = "<namespace_name>"
)

var CredentialsRequestTemplate = &minterv1.CredentialsRequest{
   ObjectMeta: metav1.ObjectMeta{
       Name:      name,
       Namespace: "openshift-cloud-credential-operator",
   },
   Spec: minterv1.CredentialsRequestSpec{
      ProviderSpec: ProviderSpec,
      SecretRef: corev1.ObjectReference{
         Name:      "<secret_name>",
         Namespace: namespace,
      },
      ServiceAccountNames: []string{
         "<service_account_name>",
      },
      CloudTokenPath:   "",
   },
}
```

또는 YAML 형식의 `CredentialsRequest` 오브젝트(예: Operator 프로젝트 코드의 일부)에서 시작하는 경우 다르게 처리할 수 있습니다.

```plaintext
// CredentialsRequest is a struct that represents a request for credentials
type CredentialsRequest struct {
  APIVersion string `yaml:"apiVersion"`
  Kind       string `yaml:"kind"`
  Metadata   struct {
     Name      string `yaml:"name"`
     Namespace string `yaml:"namespace"`
  } `yaml:"metadata"`
  Spec struct {
     SecretRef struct {
        Name      string `yaml:"name"`
        Namespace string `yaml:"namespace"`
     } `yaml:"secretRef"`
     ProviderSpec struct {
        APIVersion     string `yaml:"apiVersion"`
        Kind           string `yaml:"kind"`
        StatementEntries []struct {
           Effect   string   `yaml:"effect"`
           Action   []string `yaml:"action"`
           Resource string   `yaml:"resource"`
        } `yaml:"statementEntries"`
        STSIAMRoleARN   string `yaml:"stsIAMRoleARN"`
     } `yaml:"providerSpec"`

     // added new field
      CloudTokenPath   string `yaml:"cloudTokenPath"`
  } `yaml:"spec"`
}

// ConsumeCredsRequestAddingTokenInfo is a function that takes a YAML filename and two strings as arguments
// It unmarshals the YAML file to a CredentialsRequest object and adds the token information.
func ConsumeCredsRequestAddingTokenInfo(fileName, tokenString, tokenPath string) (*CredentialsRequest, error) {
  // open a file containing YAML form of a CredentialsRequest
  file, err := os.Open(fileName)
  if err != nil {
     return nil, err
  }
  defer file.Close()

  // create a new CredentialsRequest object
  cr := &CredentialsRequest{}

  // decode the yaml file to the object
  decoder := yaml.NewDecoder(file)
  err = decoder.Decode(cr)
  if err != nil {
     return nil, err
  }

  // assign the string to the existing field in the object
  cr.Spec.CloudTokenPath = tokenPath

  // return the modified object
  return cr, nil
}
```

참고

Operator 번들에 `CredentialsRequest` 오브젝트를 추가하는 것은 현재 지원되지 않습니다.

인증 정보 요청에 ARN 및 웹 ID 토큰 경로를 추가하고 Operator 초기화 중에 적용합니다.

```plaintext
// apply CredentialsRequest on install
credReq := credreq.CredentialsRequestTemplate
credReq.Spec.CloudTokenPath = webIdentityTokenPath

c := mgr.GetClient()
if err := c.Create(context.TODO(), credReq); err != nil {
   if !errors.IsAlreadyExists(err) {
      setupLog.Error(err, "unable to create CredRequest")
      os.Exit(1)
   }
}
```

Operator에서 조정 중인 다른 항목과 함께 호출되는 다음 예와 같이 Operator가 CCO에서 `Secret` 오브젝트가 표시될 때까지 기다릴 수 있습니다.

```plaintext
// WaitForSecret is a function that takes a Kubernetes client, a namespace, and a v1 "k8s.io/api/core/v1" name as arguments
// It waits until the secret object with the given name exists in the given namespace
// It returns the secret object or an error if the timeout is exceeded
func WaitForSecret(client kubernetes.Interface, namespace, name string) (*v1.Secret, error) {
  // set a timeout of 10 minutes
  timeout := time.After(10 * time.Minute)
  // set a polling interval of 10 seconds
  ticker := time.NewTicker(10 * time.Second)

  // loop until the timeout or the secret is found
  for {
     select {
     case <-timeout:
        // timeout is exceeded, return an error
        return nil, fmt.Errorf("timed out waiting for secret %s in namespace %s", name, namespace)
           // add to this error with a pointer to instructions for following a manual path to a Secret that will work on STS
     case <-ticker.C:
        // polling interval is reached, try to get the secret
        secret, err := client.CoreV1().Secrets(namespace).Get(context.Background(), name, metav1.GetOptions{})
        if err != nil {
           if errors.IsNotFound(err) {
              // secret does not exist yet, continue waiting
              continue
           } else {
              // some other error occurred, return it
              return nil, err
           }
        } else {
           // secret is found, return it
           return secret, nil
        }
     }
  }
}
```

1. `시간 초과` 값은 CCO에서 추가된 `CredentialsRequest` 오브젝트를 감지하고 `Secret` 오브젝트를 생성하는 속도의 추정치를 기반으로 합니다. Operator가 아직 클라우드 리소스에 액세스하지 않는 이유를 확인할 수 있는 클러스터 관리자에게 시간을 낮추거나 사용자 정의 피드백을 생성하는 것을 고려할 수 있습니다.

인증 정보 요청에서 CCO에서 생성한 보안을 읽고 해당 시크릿의 데이터가 포함된 AWS 구성 파일을 생성하여 AWS 구성을 설정합니다.

```plaintext
func SharedCredentialsFileFromSecret(secret *corev1.Secret) (string, error) {
   var data []byte
   switch {
   case len(secret.Data["credentials"]) > 0:
       data = secret.Data["credentials"]
   default:
       return "", errors.New("invalid secret for aws credentials")
   }


   f, err := ioutil.TempFile("", "aws-shared-credentials")
   if err != nil {
       return "", errors.Wrap(err, "failed to create file for shared credentials")
   }
   defer f.Close()
   if _, err := f.Write(data); err != nil {
       return "", errors.Wrapf(err, "failed to write credentials to %s", f.Name())
   }
   return f.Name(), nil
}
```

중요

시크릿은 존재하는 것으로 가정되지만 Operator 코드는 이 시크릿을 사용할 때 대기하고 재시도하여 CCO에 시간을 할애하여 보안을 생성해야 합니다.

또한 대기 기간은 결국 OpenShift Container Platform 클러스터 버전 및 CCO가 STS 탐지를 사용하여 `CredentialsRequest` 오브젝트 워크플로를 지원하지 않는 이전 버전일 수 있음을 사용자에게 시간 초과하고 경고해야 합니다. 이러한 경우 다른 방법을 사용하여 시크릿을 추가해야 함을 사용자에게 지시합니다.

AWS SDK 세션을 구성합니다. 예를 들면 다음과 같습니다.

```plaintext
sharedCredentialsFile, err := SharedCredentialsFileFromSecret(secret)
if err != nil {
   // handle error
}
options := session.Options{
   SharedConfigState: session.SharedConfigEnable,
   SharedConfigFiles: []string{sharedCredentialsFile},
}
```

#### 5.1.2.2. 역할 사양

Operator 설명에는 설치 전에 생성하는 데 필요한 역할의 세부 정보가 포함되어야 합니다. 이는 관리자가 실행할 수 있는 스크립트 형태로 이상적입니다. 예를 들면 다음과 같습니다.

```bash
#!/bin/bash
set -x

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
OIDC_PROVIDER=$(oc get authentication cluster -ojson | jq -r .spec.serviceAccountIssuer | sed -e "s/^https:\/\///")
NAMESPACE=my-namespace
SERVICE_ACCOUNT_NAME="my-service-account"
POLICY_ARN_STRINGS="arn:aws:iam::aws:policy/AmazonS3FullAccess"


read -r -d '' TRUST_RELATIONSHIP <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Effect": "Allow",
     "Principal": {
       "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER}"
     },
     "Action": "sts:AssumeRoleWithWebIdentity",
     "Condition": {
       "StringEquals": {
         "${OIDC_PROVIDER}:sub": "system:serviceaccount:${NAMESPACE}:${SERVICE_ACCOUNT_NAME}"
       }
     }
   }
 ]
}
EOF

echo "${TRUST_RELATIONSHIP}" > trust.json

aws iam create-role --role-name "$SERVICE_ACCOUNT_NAME" --assume-role-policy-document file://trust.json --description "role for demo"

while IFS= read -r POLICY_ARN; do
   echo -n "Attaching $POLICY_ARN ... "
   aws iam attach-role-policy \
       --role-name "$SERVICE_ACCOUNT_NAME" \
       --policy-arn "${POLICY_ARN}"
   echo "ok."
done <<< "$POLICY_ARN_STRINGS"
```

#### 5.1.2.3.1. 인증 실패

인증이 실패하면 Operator에 제공된 토큰을 사용하여 웹 ID가 있는 역할을 가정할 수 있는지 확인합니다.

프로세스

Pod에서 토큰을 추출합니다.

```shell-session
$ oc exec operator-pod -n <namespace_name> \
    -- cat /var/run/secrets/openshift/serviceaccount/token
```

Pod에서 ARN 역할을 추출합니다.

```shell-session
$ oc exec operator-pod -n <namespace_name> \
    -- cat /<path>/<to>/<secret_name>
```

1. 경로에 root를 사용하지 마십시오.

웹 ID 토큰을 사용하여 역할을 가정합니다.

```shell-session
$ aws sts assume-role-with-web-identity \
    --role-arn $ROLEARN \
    --role-session-name <session_name> \
    --web-identity-token $TOKEN
```

#### 5.1.2.3.2. secret이 올바르게 마운트되지 않음

루트가 아닌 사용자로 실행되는 Pod는 기본적으로 AWS 공유 인증 정보 파일이 존재하는 `/root` 디렉토리에 쓸 수 없습니다. 보안이 AWS 인증 정보 파일 경로에 올바르게 마운트되지 않은 경우 시크릿을 다른 위치에 마운트하고 AWS SDK에서 공유 인증 정보 파일 옵션을 활성화하는 것이 좋습니다.

#### 5.1.2.4. 대체 방법

Operator 작성자의 대체 방법으로는 Operator를 설치하기 전에 사용자가 CCO(Cloud Credential Operator)에 대한 `CredentialsRequest` 오브젝트를 생성해야 함을 나타낼 수 있습니다.

Operator 명령은 다음을 사용자에게 표시해야 합니다.

지침에 YAML 인라인을 제공하거나 사용자를 다운로드 위치를 가리켜 `CredentialsRequest` 오브젝트의 YAML 버전을 제공합니다.

사용자에게 `CredentialsRequest` 오브젝트를 생성하도록 지시합니다.

OpenShift Container Platform 4.14 이상에서는 적절한 STS 정보가 추가된 클러스터에 `CredentialsRequest` 오브젝트가 표시된 후 Operator에서 CCO 생성 `시크릿` 을 읽거나 마운트하여 CSV(클러스터 서비스 버전)에서 마운트를 정의할 수 있습니다.

이전 버전의 OpenShift Container Platform의 경우 Operator 지침도 사용자에게 다음을 표시해야 합니다.

CCO 유틸리티(`ccoctl`)를 사용하여 `CredentialsRequest` 오브젝트에서 `Secret` YAML 오브젝트를 생성합니다.

적절한 네임스페이스의 클러스터에 `Secret` 오브젝트를 적용

Operator는 여전히 결과 시크릿을 사용하여 클라우드 API와 통신할 수 있어야 합니다. 이 경우 Operator가 설치되기 전에 사용자가 시크릿을 생성하므로 Operator는 다음 중 하나를 수행할 수 있습니다.

CSV 내의 `Deployment` 오브젝트에 명시적 마운트 정의

권장 "AWS STS를 사용하여 CCO 기반 워크플로우를 지원하도록 Operator 활성화" 메서드와 같이 API 서버에서 `Secret` 오브젝트를 프로그래밍 방식으로 읽습니다.

#### 5.1.3. Microsoft Entra Workload ID가 있는 OLM 관리 Operator의 CCO 기반 워크플로

Azure에서 실행되는 OpenShift Container Platform 클러스터가 Workload Identity / Federated Identity 모드에 있는 경우 클러스터가 Azure 및 OpenShift Container Platform의 기능을 활용하여 애플리케이션 수준에서 사용자가 할당한 관리 ID 또는 앱 등록을 적용합니다.

CCO(Cloud Credential Operator)는 기본적으로 클라우드 공급자에서 실행되는 OpenShift Container Platform 클러스터에 설치된 클러스터 Operator입니다. OpenShift Container Platform 4.14.8부터 CCO는 워크로드 ID가 있는 OLM 관리 Operator의 워크플로우를 지원합니다.

Workload ID의 목적을 위해 CCO는 다음 기능을 제공합니다.

워크로드 ID 지원 클러스터에서 실행 중인 시기 감지

Azure 리소스에 대한 Operator 액세스 권한을 부여하는 데 필요한 정보를 제공하는 필드가 있는지 `CredentialsRequest` 오브젝트를 확인합니다.

CCO는 워크로드 ID 워크플로에 필요한 정보가 포함된 `시크릿` 생성을 요청할 수 있는 `CredentialsRequest` 오브젝트의 확장된 사용을 통해 이 프로세스를 반자동화할 수 있습니다.

참고

업데이트에 대한 자동 승인이 있는 서브스크립션은 업데이트하기 전에 권한을 변경할 수 있으므로 권장되지 않습니다. 업데이트에 대한 수동 승인이 있는 서브스크립션을 통해 관리자는 최신 버전의 권한을 확인하고 필요한 단계를 수행한 다음 업데이트할 수 있습니다.

OpenShift Container Platform 4.14 이상에서 업데이트된 CCO와 함께 Operator를 사용할 수 있도록 Operator 작성자로서 Workload ID 토큰 인증(Operator가 아직 활성화되지 않은 경우)을 처리하는 것 외에도 사용자와 이전 CCO 버전의 차이점을 처리하도록 코드를 추가해야 합니다.

권장되는 방법은 올바르게 채워진 Workload ID 필드를 사용하여 `CredentialsRequest` 오브젝트를 제공하고 CCO가 `Secret` 오브젝트를 생성하도록 하는 것입니다.

중요

버전 4.14 이전의 OpenShift Container Platform 클러스터를 지원하려는 경우 CCO 유틸리티(`ccoctl`)를 사용하여 워크로드 ID를 사용하여 시크릿을 수동으로 생성하는 방법에 대한 지침을 사용자에게 제공하는 것이 좋습니다. 이전 CCO 버전은 클러스터에서 Workload ID 모드를 인식하지 못하며 시크릿을 생성할 수 없습니다.

코드는 나타나지 않는 시크릿을 확인하고 사용자가 제공한 대체 지침을 따르도록 경고해야 합니다.

Workload ID를 사용한 인증에는 다음 정보가 필요합니다.

`azure_client_id`

`azure_tenant_id`

`azure_region`

`azure_subscription_id`

`azure_federated_token_file`

클러스터 관리자는 웹 콘솔의 Operator 설치 페이지를 통해 설치 시 이 정보를 제공할 수 있습니다. 그런 다음 이 정보는 `Subscription` 오브젝트에 Operator Pod의 환경 변수로 전파됩니다.

추가 리소스

Microsoft Entra Workload ID를 사용한 인증에 대한 OLM 관리형 Operator 지원

웹 콘솔을 사용하여 OperatorHub에서 설치

CLI를 사용하여 OperatorHub에서 설치

#### 5.1.3.1. Microsoft Entra Workload ID를 사용하여 CCO 기반 워크플로우를 지원할 수 있도록 Operator 활성화

OLM(Operator Lifecycle Manager)에서 프로젝트를 실행하도록 프로젝트를 설계하는 Operator 작성자는 CCO(Cloud Credential Operator)를 지원하도록 프로젝트를 사용자 정의하여 Operator에서 Microsoft Entra Workload ID 지원 OpenShift Container Platform 클러스터에 대해 인증할 수 있습니다.

이 방법을 사용하면 Operator에서 `CredentialsRequest` 오브젝트를 생성하고 결과 `Secret` 오브젝트를 읽는 데 필요한 RBAC 권한이 필요합니다.

참고

기본적으로 Operator 배포와 관련된 Pod는 `serviceAccountToken` 볼륨을 마운트하여 결과 `Secret` 오브젝트에서 서비스 계정 토큰을 참조할 수 있습니다.

전제 조건

OpenShift Container Platform 4.14 이상

워크로드 ID 모드의 클러스터

OLM 기반 Operator 프로젝트

프로세스

Operator 프로젝트의 CSV(`ClusterServiceVersion`) 오브젝트를 업데이트합니다.

Operator에 `CredentialsRequests` 오브젝트를 생성할 수 있는 RBAC 권한이 있는지 확인합니다.

```yaml
# ...
install:
  spec:
    clusterPermissions:
    - rules:
      - apiGroups:
        - "cloudcredential.openshift.io"
        resources:
        - credentialsrequests
        verbs:
        - create
        - delete
        - get
        - list
        - patch
        - update
        - watch
```

Workload ID를 사용하여 CCO 기반 워크플로우 방법에 대한 지원을 요청하려면 다음 주석을 추가합니다.

```yaml
# ...
metadata:
 annotations:
   features.operators.openshift.io/token-auth-azure: "true"
```

Operator 프로젝트 코드를 업데이트합니다.

`Subscription` 오브젝트를 통해 포드에 설정된 환경 변수에서 클라이언트 ID, 테넌트 ID, 서브스크립션 ID를 가져옵니다. 예를 들면 다음과 같습니다.

```plaintext
// Get ENV var
clientID := os.Getenv("CLIENTID")
tenantID := os.Getenv("TENANTID")
subscriptionID := os.Getenv("SUBSCRIPTIONID")
azureFederatedTokenFile := "/var/run/secrets/openshift/serviceaccount/token"
```

`CredentialsRequest` 개체를 패치하고 적용할 준비가 되었는지 확인합니다.

참고

Operator 번들에 `CredentialsRequest` 오브젝트를 추가하는 것은 현재 지원되지 않습니다.

인증 정보 및 웹 ID 토큰 경로를 인증 정보 요청에 추가하고 Operator 초기화 중에 적용합니다.

```plaintext
// apply CredentialsRequest on install
credReqTemplate.Spec.AzureProviderSpec.AzureClientID = clientID
credReqTemplate.Spec.AzureProviderSpec.AzureTenantID = tenantID
credReqTemplate.Spec.AzureProviderSpec.AzureRegion = "centralus"
credReqTemplate.Spec.AzureProviderSpec.AzureSubscriptionID = subscriptionID
credReqTemplate.CloudTokenPath = azureFederatedTokenFile

c := mgr.GetClient()
if err := c.Create(context.TODO(), credReq); err != nil {
    if !errors.IsAlreadyExists(err) {
        setupLog.Error(err, "unable to create CredRequest")
        os.Exit(1)
    }
}
```

Operator에서 조정 중인 다른 항목과 함께 호출되는 다음 예와 같이 Operator가 CCO에서 `Secret` 오브젝트가 표시될 때까지 기다릴 수 있습니다.

```plaintext
// WaitForSecret is a function that takes a Kubernetes client, a namespace, and a v1 "k8s.io/api/core/v1" name as arguments
// It waits until the secret object with the given name exists in the given namespace
// It returns the secret object or an error if the timeout is exceeded
func WaitForSecret(client kubernetes.Interface, namespace, name string) (*v1.Secret, error) {
  // set a timeout of 10 minutes
  timeout := time.After(10 * time.Minute)
  // set a polling interval of 10 seconds
  ticker := time.NewTicker(10 * time.Second)

  // loop until the timeout or the secret is found
  for {
     select {
     case <-timeout:
        // timeout is exceeded, return an error
        return nil, fmt.Errorf("timed out waiting for secret %s in namespace %s", name, namespace)
           // add to this error with a pointer to instructions for following a manual path to a Secret that will work on STS
     case <-ticker.C:
        // polling interval is reached, try to get the secret
        secret, err := client.CoreV1().Secrets(namespace).Get(context.Background(), name, metav1.GetOptions{})
        if err != nil {
           if errors.IsNotFound(err) {
              // secret does not exist yet, continue waiting
              continue
           } else {
              // some other error occurred, return it
              return nil, err
           }
        } else {
           // secret is found, return it
           return secret, nil
        }
     }
  }
}
```

1. `시간 초과` 값은 CCO에서 추가된 `CredentialsRequest` 오브젝트를 감지하고 `Secret` 오브젝트를 생성하는 속도의 추정치를 기반으로 합니다. Operator가 아직 클라우드 리소스에 액세스하지 않는 이유를 확인할 수 있는 클러스터 관리자에게 시간을 낮추거나 사용자 정의 피드백을 생성하는 것을 고려할 수 있습니다.

Azure로 인증하고 필요한 인증 정보를 수신하기 위해 `CredentialsRequest` 오브젝트에서 CCO에서 생성한 시크릿을 읽습니다.

#### 5.1.4. GCP 워크로드 ID를 사용하는 OLM 관리 Operator의 CCO 기반 워크플로

Google Cloud에서 실행되는 OpenShift Container Platform 클러스터가 GCP Workload Identity / Federated Identity 모드에 있는 경우 클러스터가 Google Cloud 및 OpenShift Container Platform의 기능을 활용하여 애플리케이션 수준에서 GCP 워크로드 ID의 권한을 적용합니다.

CCO(Cloud Credential Operator)는 기본적으로 클라우드 공급자에서 실행되는 OpenShift Container Platform 클러스터에 설치된 클러스터 Operator입니다. OpenShift Container Platform 4.17부터 CCO는 GCP 워크로드 ID가 있는 OLM 관리 Operator의 워크플로우를 지원합니다.

GCP Workload Identity의 목적을 위해 CCO는 다음과 같은 기능을 제공합니다.

GCP 워크로드 ID 지원 클러스터에서 실행 중인 시기 감지

`CredentialsRequest` 오브젝트에서 Google Cloud 리소스에 대한 Operator 액세스 권한을 부여하는 데 필요한 정보를 제공하는 필드가 있는지 확인합니다.

CCO는 `CredentialsRequest` 오브젝트의 확장된 사용을 통해 이 프로세스를 반자동화할 수 있으며, 이는 GCP Workload Identity 워크플로에 필요한 정보가 포함된 `시크릿` 생성을 요청할 수 있습니다.

참고

업데이트에 대한 자동 승인이 있는 서브스크립션은 업데이트하기 전에 권한을 변경할 수 있으므로 권장되지 않습니다. 업데이트에 대한 수동 승인이 있는 서브스크립션을 통해 관리자는 최신 버전의 권한을 확인하고 필요한 단계를 수행한 다음 업데이트할 수 있습니다.

OpenShift Container Platform 4.17 이상에서 업데이트된 CCO와 함께 Operator를 사용할 수 있도록 Operator 작성자로서 GCP Workload Identity 토큰 인증(Operator가 아직 활성화되지 않은 경우)을 처리하는 것 외에도 사용자와 이전 CCO 버전의 차이점을 처리하도록 코드를 추가해야 합니다.

권장 방법은 올바르게 채워진 GCP Workload Identity 필드를 사용하여 `CredentialsRequest` 오브젝트를 제공하고 CCO가 `Secret` 오브젝트를 생성하도록 하는 것입니다.

중요

버전 4.17 이전의 OpenShift Container Platform 클러스터를 지원할 예정인 경우 CCO 유틸리티(`ccoctl`)를 사용하여 GCP Workload Identity-enabling 정보를 사용하여 시크릿을 수동으로 생성하는 방법에 대한 지침을 사용자에게 제공하는 것이 좋습니다.

이전 CCO 버전은 클러스터의 GCP Workload Identity 모드를 인식하지 않으며 시크릿을 생성할 수 없습니다.

코드는 나타나지 않는 시크릿을 확인하고 사용자가 제공한 대체 지침을 따르도록 경고해야 합니다.

Google Cloud Platform Workload Identity를 통해 짧은 토큰을 사용하여 Google Cloud로 인증하려면 Operator에서 다음 정보를 제공해야 합니다.

`대상`

GCP Workload Identity를 설정할 때 관리자가 Google Cloud에서 생성한 `AUDIENCE` 값은 다음 형식의 사전 형식의 URL이어야 합니다.

```plaintext
//iam.googleapis.com/projects/<project_number>/locations/global/workloadIdentityPools/<pool_id>/providers/<provider_id>
```

`SERVICE_ACCOUNT_EMAIL`

`SERVICE_ACCOUNT_EMAIL` 값은 Operator 작업 중에 가장하는 Google Cloud 서비스 계정 이메일입니다. 예를 들면 다음과 같습니다.

```plaintext
<service_account_name>@<project_id>.iam.gserviceaccount.com
```

클러스터 관리자는 웹 콘솔의 Operator 설치 페이지를 통해 설치 시 이 정보를 제공할 수 있습니다. 그런 다음 이 정보는 `Subscription` 오브젝트에 Operator Pod의 환경 변수로 전파됩니다.

추가 리소스

GCP 워크로드 ID를 통한 인증에 대한 OLM 관리형 Operator 지원

웹 콘솔을 사용하여 OperatorHub에서 설치

CLI를 사용하여 OperatorHub에서 설치

#### 5.1.4.1. Operator가 GCP 워크로드 ID를 사용하여 CCO 기반 워크플로우를 지원하도록 활성화

OLM(Operator Lifecycle Manager)에서 프로젝트를 실행하도록 프로젝트를 설계하는 Operator 작성자는 CCO(Cloud Credential Operator)를 지원하도록 프로젝트를 사용자 정의하여 Operator에서 OpenShift Container Platform 클러스터의 Google Cloud Platform 워크로드 ID에 대해 인증할 수 있습니다.

이 방법을 사용하면 Operator에서 `CredentialsRequest` 오브젝트를 생성하고 결과 `Secret` 오브젝트를 읽는 데 필요한 RBAC 권한이 필요합니다.

참고

기본적으로 Operator 배포와 관련된 Pod는 `serviceAccountToken` 볼륨을 마운트하여 결과 `Secret` 오브젝트에서 서비스 계정 토큰을 참조할 수 있습니다.

전제 조건

OpenShift Container Platform 4.17 이상

GCP 워크로드 ID/Federated Identity 모드의 클러스터

OLM 기반 Operator 프로젝트

프로세스

Operator 프로젝트의 CSV(`ClusterServiceVersion`) 오브젝트를 업데이트합니다.

Operator가 웹 ID로 역할을 가정할 수 있도록 CSV에서 Operator 배포에 다음과 같은 `volumeMounts` 및 `volumes` 필드가 있는지 확인합니다.

```yaml
# ...
      volumeMounts:

      - name: bound-sa-token
        mountPath: /var/run/secrets/openshift/serviceaccount
        readOnly: true
      volumes:
         # This service account token can be used to provide identity outside the cluster.
         - name: bound-sa-token
           projected:
             sources:
             - serviceAccountToken:
               path: token
               audience: openshift
```

Operator에 `CredentialsRequests` 오브젝트를 생성할 수 있는 RBAC 권한이 있는지 확인합니다.

```yaml
# ...
install:
  spec:
    clusterPermissions:
    - rules:
      - apiGroups:
        - "cloudcredential.openshift.io"
        resources:
        - credentialsrequests
        verbs:
        - create
        - delete
        - get
        - list
        - patch
        - update
        - watch
```

GCP Workload Identity를 사용하여 CCO 기반 워크플로우 방법에 대한 지원을 요청하려면 다음 주석을 추가합니다.

```yaml
# ...
metadata:
 annotations:
   features.operators.openshift.io/token-auth-gcp: "true"
```

Operator 프로젝트 코드를 업데이트합니다.

서브스크립션 구성에 설정된 환경 변수에서 `audience` 및 `serviceAccountEmail` 값을 가져옵니다.

```plaintext
// Get ENV var
   audience := os.Getenv("AUDIENCE")
   serviceAccountEmail := os.Getenv("SERVICE_ACCOUNT_EMAIL")
   gcpIdentityTokenFile := "/var/run/secrets/openshift/serviceaccount/token"
```

`CredentialsRequest` 개체를 패치하고 적용할 준비가 되었는지 확인합니다.

참고

Operator 번들에 `CredentialsRequest` 오브젝트를 추가하는 것은 현재 지원되지 않습니다.

인증 정보 요청에 GCP Workload Identity 변수를 추가하고 Operator 초기화 중에 적용합니다.

```plaintext
// apply CredentialsRequest on install
   credReqTemplate.Spec.GCPProviderSpec.Audience = audience
   credReqTemplate.Spec.GCPProviderSpec.ServiceAccountEmail = serviceAccountEmail
   credReqTemplate.CloudTokenPath = gcpIdentityTokenFile


   c := mgr.GetClient()
   if err := c.Create(context.TODO(), credReq); err != nil {
       if !errors.IsAlreadyExists(err) {
           setupLog.Error(err, "unable to create CredRequest")
           os.Exit(1)
       }
   }
```

Operator에서 조정 중인 다른 항목과 함께 호출되는 다음 예와 같이 Operator가 CCO에서 `Secret` 오브젝트가 표시될 때까지 기다릴 수 있습니다.

```plaintext
// WaitForSecret is a function that takes a Kubernetes client, a namespace, and a v1 "k8s.io/api/core/v1" name as arguments
// It waits until the secret object with the given name exists in the given namespace
// It returns the secret object or an error if the timeout is exceeded
func WaitForSecret(client kubernetes.Interface, namespace, name string) (*v1.Secret, error) {
  // set a timeout of 10 minutes
  timeout := time.After(10 * time.Minute)
  // set a polling interval of 10 seconds
  ticker := time.NewTicker(10 * time.Second)

  // loop until the timeout or the secret is found
  for {
     select {
     case <-timeout:
        // timeout is exceeded, return an error
        return nil, fmt.Errorf("timed out waiting for secret %s in namespace %s", name, namespace)
// add to this error with a pointer to instructions for following a manual path to a Secret that will work
     case <-ticker.C:
        // polling interval is reached, try to get the secret
        secret, err := client.CoreV1().Secrets(namespace).Get(context.Background(), name, metav1.GetOptions{})
        if err != nil {
           if errors.IsNotFound(err) {
              // secret does not exist yet, continue waiting
              continue
           } else {
              // some other error occurred, return it
              return nil, err
           }
        } else {
           // secret is found, return it
           return secret, nil
        }
     }
  }
}
```

1. `시간 초과` 값은 CCO에서 추가된 `CredentialsRequest` 오브젝트를 감지하고 `Secret` 오브젝트를 생성하는 속도의 추정치를 기반으로 합니다. Operator가 아직 클라우드 리소스에 액세스하지 않는 이유를 확인할 수 있는 클러스터 관리자에게 시간을 낮추거나 사용자 정의 피드백을 생성하는 것을 고려할 수 있습니다.

시크릿에서 `service_account.json` 필드를 읽고 이를 사용하여 Google Cloud 클라이언트를 인증합니다.

```plaintext
service_account_json := secret.StringData["service_account.json"]
```

## 6장. 클러스터 Operator 참조

이 참조 가이드에서는 OpenShift Container Platform의 아키텍처 기반 역할을 하는 Red Hat에서 제공하는 클러스터 Operator 를 인덱싱합니다. 클러스터 Operator는 달리 명시되지 않는 한 기본적으로 설치되고 CVO(Cluster Version Operator)에서 관리합니다.

컨트롤 플레인 아키텍처에 대한 자세한 내용은 OpenShift Container Platform의 Operator 를 참조하십시오.

클러스터 관리자는 관리 → 클러스터 설정 페이지에서 OpenShift Container Platform 웹 콘솔에서 클러스터 Operator를 볼 수 있습니다.

참고

클러스터 Operator는 OLM(Operator Lifecycle Manager) 및 소프트웨어 카탈로그에서 관리되지 않습니다. OLM 및 소프트웨어 카탈로그는 선택적 애드온 Operator를 설치하고 실행하는 데 OpenShift Container Platform에서 사용되는 Operator 프레임워크 의 일부입니다.

설치 전에 다음 클러스터 Operator를 비활성화할 수 있습니다. 자세한 내용은 클러스터 기능을 참조하십시오.

### 6.1. Cluster Baremetal Operator

참고

Cluster Baremetal Operator는 설치 중에 클러스터 관리자가 비활성화할 수 있는 선택적 클러스터 기능입니다. 선택적 클러스터 기능에 대한 자세한 내용은 설치 의 "클러스터 기능"을 참조하십시오.

CNO(Cluster Baremetal Operator)는 베어 메탈 서버를 사용하여 OpenShift Container Platform 컴퓨팅 노드를 실행할 준비가 된 작업자 노드에 모든 구성 요소를 배포합니다.

CBO를 사용하면 Bare Metal Operator(BMO) 및 Ironic 컨테이너로 구성된 metal3 배포가 OpenShift Container Platform 클러스터 내의 컨트롤 플레인 노드 중 하나에서 실행됩니다.

CBO는 또한 조사하여 적절한 조치를 취하는 리소스에 대한 OpenShift Container Platform 업데이트를 수신 대기합니다.

#### 6.1.1. 프로젝트

cluster-baremetal-operator

추가 리소스

베어 메탈 기능

### 6.2. Cloud Credential Operator

CCO(Cloud Credential Operator)는 클라우드 공급자 자격 증명을 Kubernetes CRD(사용자 지정 리소스 정의)로 관리합니다.

CCO는 `CredentialsRequest` CR(사용자 정의 리소스)에서 동기화되어 OpenShift Container Platform 구성 요소가 클러스터를 실행하는 데 필요한 특정 권한이 있는 클라우드 공급자 자격 증명을 요청할 수 있습니다.

`install-config.yaml` 파일에서 `credentialsMode` 매개변수에 다양한 값을 설정하면 CCO를 여러 모드에서 작동하도록 구성할 수 있습니다. 모드를 지정하지 않거나 `credentialsMode` 매개변수를 빈 문자열(`""`)로 설정하면 CCO가 기본 모드에서 작동합니다.

#### 6.2.1. 프로젝트

openshift-cloud-credential-operator

#### 6.2.2. CRD

`credentialsrequests.cloudcredential.openshift.io`

범위: 네임스페이스

CR: `CredentialsRequest`

검증: 예

#### 6.2.3. 구성 오브젝트

구성이 필요하지 않습니다.

#### 6.2.4. 추가 리소스

Cloud Credential Operator 정보

`CredentialsRequest` 사용자 정의 리소스

### 6.3. Cluster Authentication Operator

Cluster Authentication Operator는 클러스터에서 `Authentication` 사용자 정의 리소스를 설치 및 유지 관리하고 다음을 실행하여 확인할 수 있습니다.

```shell-session
$ oc get clusteroperator authentication -o yaml
```

#### 6.3.1. 프로젝트

cluster-authentication-operator

### 6.4. Cluster Autoscaler Operator

Cluster Autoscaler Operator는 `cluster-api` 공급자를 사용하여 OpenShift Cluster Autoscaler 배포를 관리합니다.

#### 6.4.1. 프로젝트

cluster-autoscaler-operator

#### 6.4.2. CRD

`ClusterAutoscaler`: 클러스터의 구성 자동 스케일러 인스턴스를 제어하는 단일 생성 리소스입니다. Operator는 관리형 네임스페이스에서 `WATCH_NAMESPACE` 환경 변수의 값인 `default` 라는 `ClusterAutoscaler` 리소스에만 응답합니다.

`MachineAutoscaler`: 이 리소스는 노드 그룹을 대상으로 하며 그룹, `min` 및 `max` 크기에 대해 자동 스케일링을 활성화하고 구성하는 주석을 관리합니다. 현재는 `MachineSet` 오브젝트만 대상으로 할 수 있습니다.

### 6.5. Cloud Controller Manager Operator

참고

이 Operator의 상태는 AWS(Amazon Web Services), Google Cloud, IBM Cloud®, 글로벌 Microsoft Azure, Microsoft Azure Stack Hub, Nutanix, RHOSP(Red Hat OpenStack Platform) 및 VMware vSphere의 일반 가용성입니다.

Operator는 IBM Power® Virtual Server용 기술 프리뷰로 사용할 수 있습니다.

Cloud Controller Manager Operator는 OpenShift Container Platform 상단에 배포된 클라우드 컨트롤러 관리자를 관리하고 업데이트합니다. Operator는 Kubebuilder 프레임워크 및 `controller-runtime` 라이브러리를 기반으로 합니다.

CVO(Cluster Version Operator)를 사용하여 Cloud Controller Manager Operator를 설치할 수 있습니다.

Cloud Controller Manager Operator에는 다음 구성 요소가 포함되어 있습니다.

Operator

클라우드 구성 관찰자

기본적으로 Operator는 `metrics` 서비스를 통해 Prometheus 지표를 표시합니다.

#### 6.5.1. 프로젝트

cluster-cloud-controller-manager-operator

### 6.6. Cluster CAPI Operator

Cluster CAPI Operator는 Cluster API 리소스의 라이프사이클을 유지 관리합니다. 이 Operator는 OpenShift Container Platform 클러스터 내에서 Cluster API 프로젝트 배포와 관련된 모든 관리 작업을 담당합니다.

참고

이 Operator는 AWS(Amazon Web Services), Google Cloud, Microsoft Azure, RHOSP(Red Hat OpenStack Platform) 및 VMware vSphere 클러스터용 기술 프리뷰로 사용할 수 있습니다.

#### 6.6.1. 프로젝트

cluster-capi-operator

#### 6.6.2. CRD

`awsmachines.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `awsmachine`

`gcpmachines.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `gcpmachine`

`azuremachines.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `azuremachine`

`openstackmachines.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `openstackmachine`

`vspheremachines.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `vspheremachine`

`metal3machines.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `metal3machine`

`awsmachinetemplates.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `awsmachinetemplate`

`gcpmachinetemplates.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `gcpmachinetemplate`

`azuremachinetemplates.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `azuremachinetemplate`

`openstackmachinetemplates.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `openstackmachinetemplate`

`vspheremachinetemplates.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `vspheremachinetemplate`

`metal3machinetemplates.infrastructure.cluster.x-k8s.io`

범위: 네임스페이스

CR: `metal3machinetemplate`

### 6.7. Cluster Config Operator

Cluster Config Operator는 `config.openshift.io` 와 관련된 다음 작업을 수행합니다.

CRD를 생성합니다.

초기 사용자 정의 리소스를 렌더링합니다.

마이그레이션을 처리합니다.

#### 6.7.1. 프로젝트

cluster-config-operator

### 6.8. Cluster CSI Snapshot Controller Operator

참고

Cluster CSI Snapshot Controller Operator는 설치 중에 클러스터 관리자가 비활성화할 수 있는 선택적 클러스터 기능입니다. 선택적 클러스터 기능에 대한 자세한 내용은 설치 의 "클러스터 기능"을 참조하십시오.

Cluster CSI Snapshot Controller Operator는 CSI Snapshot Controller를 설치하고 유지 관리합니다. CSI Snapshot Controller는 `VolumeSnapshot` CRD 오브젝트를 모니터링하고 볼륨 스냅샷의 생성 및 삭제 라이프사이클을 관리합니다.

#### 6.8.1. 프로젝트

cluster-csi-snapshot-controller-operator

추가 리소스

CSI 스냅샷 컨트롤러 기능

### 6.9. Cluster Image Registry Operator

Cluster Image Registry Operator는 OpenShift 이미지 레지스트리의 단일 인스턴스를 관리합니다. 스토리지 생성을 포함하여 레지스트리의 모든 구성을 관리합니다.

처음 시작 시 Operator는 클러스터에서 탐지된 구성에 따라 기본 `image-registry` 리소스 인스턴스를 생성합니다. 이는 클라우드 공급자를 기반으로 사용할 클라우드 스토리지 유형을 나타냅니다.

완전한 `image-registry` 리소스를 정의하는 데 사용할 수 있는 정보가 충분하지 않으면 불완전한 리소스가 정의되고 Operator는 누락된 항목에 대한 정보를 사용하여 리소스 상태를 업데이트합니다.

Cluster Image Registry Operator는 `openshift-image-registry` 네임스페이스에서 실행되며 해당 위치의 레지스트리 인스턴스도 관리합니다. 레지스트리의 모든 설정 및 워크로드 리소스는 해당 네임 스페이스에 있습니다.

#### 6.9.1. 프로젝트

cluster-image-registry-operator

### 6.10. Cluster Machine Approver Operator

Cluster Machine Approver Operator는 클러스터 설치 후 새 작업자 노드에 대해 요청된 CSR을 자동으로 승인합니다.

참고

컨트롤 플레인 노드의 경우 부트스트랩 노드의 `approve-csr` 서비스는 클러스터 부트스트랩 단계 중에 모든 CSR을 자동으로 승인합니다.

#### 6.10.1. 프로젝트

cluster-machine-approver-operator

### 6.11. Cluster Monitoring Operator

CCMO(Cluster Monitoring Operator)는 OpenShift Container Platform 상단에 배포된 Prometheus 기반 클러스터 모니터링 스택을 관리하고 업데이트합니다.

#### 프로젝트

openshift-monitoring

#### CRD

`alertmanagers.monitoring.coreos.com`

범위: 네임스페이스

CR: `alertmanager`

검증: 예

`prometheuses.monitoring.coreos.com`

범위: 네임스페이스

CR: `prometheus`

검증: 예

`prometheusrules.monitoring.coreos.com`

범위: 네임스페이스

CR: `prometheusrule`

검증: 예

`servicemonitors.monitoring.coreos.com`

범위: 네임스페이스

CR: `servicemonitor`

검증: 예

#### 구성 오브젝트

```shell-session
$ oc -n openshift-monitoring edit cm cluster-monitoring-config
```

### 6.12. CNO(Cluster Network Operator)

Cluster Network Operator는 OpenShift Container Platform 클러스터에 네트워킹 구성 요소를 설치 및 업그레이드합니다.

### 6.13. Cluster Samples Operator

참고

Cluster Samples Operator는 설치 중에 클러스터 관리자가 비활성화할 수 있는 선택적 클러스터 기능입니다. 선택적 클러스터 기능에 대한 자세한 내용은 설치 의 "클러스터 기능"을 참조하십시오.

Cluster Samples Operator는 `openshift` 네임스페이스에 저장된 샘플 이미지 스트림 및 템플릿을 관리합니다.

처음 시작 시 Operator는 기본 샘플 구성 리소스를 생성하여 이미지 스트림 및 템플릿을 생성하기 시작합니다. 구성 오브젝트는 키가 `cluster` 이고 유형이 `configs.samples` 인 클러스터 범위 지정 오브젝트입니다.

이미지 스트림은 `registry.redhat.io` 의 이미지를 가리키는 RHCOS(Red Hat Enterprise Linux CoreOS) 기반 OpenShift Container Platform 이미지 스트림입니다. 마찬가지로 템플릿은 OpenShift Container Platform 템플릿으로 분류된 템플릿입니다.

Cluster Samples Operator 배포는 `openshift-cluster-samples-operator` 네임스페이스에 포함됩니다. 시작 시 OpenShift 이미지 레지스트리 및 API 서버의 이미지 스트림 가져오기 논리에서 `registry.redhat.io` 로 인증하는 데 설치 가져오기 보안이 사용됩니다.

관리자는 샘플 이미지 스트림에 사용된 레지스트리를 변경하는 경우 `openshift` 네임스페이스에 추가 보안을 생성할 수 있습니다. 생성한 경우 이러한 보안에는 이미지를 손쉽게 가져오는 데 필요한 의 `config.json` 콘텐츠가 포함됩니다.

```shell
docker
```

Cluster Samples Operator 이미지에는 관련 OpenShift Container Platform 릴리스의 이미지 스트림 및 템플릿 정의가 포함되어 있습니다. Cluster Samples Operator는 샘플을 생성한 후 호환되는 OpenShift Container Platform 버전을 나타내는 주석을 추가합니다.

Operator는 이 주석을 사용하여 각 샘플이 호환되는 릴리스 버전과 일치하는지 확인합니다. 인벤토리 외부 샘플은 건너뛰기한 샘플과 마찬가지로 무시됩니다.

Operator에서 관리하는 모든 샘플에 대한 수정은 버전 주석을 수정하거나 삭제하지 않는 한 허용됩니다. 그러나 업그레이드 시 버전 주석이 변경되면 샘플이 최신 버전으로 업데이트되므로 이러한 수정 사항이 대체될 수 있습니다. Jenkins 이미지는 설치의 이미지 페이로드에 포함되어 있으며 이미지 스트림에 직접 태그가 지정됩니다.

샘플 리소스에는 삭제 시 다음을 정리하는 종료자가 포함됩니다.

Operator에서 관리하는 이미지 스트림

Operator에서 관리하는 템플릿

Operator에서 생성하는 구성 리소스

클러스터 상태 리소스

샘플 리소스를 삭제하면 Cluster Samples Operator에서 기본 구성을 사용하여 리소스를 다시 생성합니다.

#### 6.13.1. 프로젝트

cluster-samples-operator

추가 리소스

OpenShift 샘플 기능

### 6.14. Cluster Storage Operator

참고

Cluster Storage Operator는 설치 중에 클러스터 관리자가 비활성화할 수 있는 선택적 클러스터 기능입니다. 선택적 클러스터 기능에 대한 자세한 내용은 설치 의 "클러스터 기능"을 참조하십시오.

Cluster Storage Operator는 OpenShift Container Platform 클러스터 수준 스토리지 기본값을 설정합니다. 이는 OpenShift Container Platform 클러스터에 기본 `스토리지 클래스` 가 있는지 확인합니다.

또한 클러스터가 다양한 스토리지 백엔드를 사용할 수 있는 CSI(Container Storage Interface) 드라이버를 설치합니다.

#### 6.14.1. 프로젝트

cluster-storage-operator

#### 6.14.2. 설정

구성이 필요하지 않습니다.

#### 6.14.3. 참고

Operator에서 생성하는 스토리지 클래스는 주석을 편집하여 기본이 아닌 상태로 만들 수 있지만 Operator가 실행되는 동안 이 스토리지 클래스를 삭제할 수 없습니다.

추가 리소스

스토리지 기능

### 6.15. Cluster Version Operator

클러스터 Operator는 특정 클러스터 기능 영역을 관리합니다. CVO(Cluster Version Operator)는 기본적으로 OpenShift Container Platform에 설치된 클러스터 Operator의 라이프사이클을 관리합니다.

CVO는 OpenShift Update Service에서 클러스터 버전과 클러스터 Operator의 상태를 수집하여 현재 구성 요소 버전 및 그래프의 정보를 기반으로 유효한 업데이트 및 업데이트 경로를 확인합니다. 이 상태에는 OpenShift Container Platform 클러스터의 상태 및 현재 상태를 알려주는 조건 유형이 포함됩니다.

클러스터 버전 상태 유형에 대한 자세한 내용은 "클러스터 버전 상태 유형 이해"를 참조하십시오.

#### 6.15.1. 프로젝트

cluster-version-operator

추가 리소스

클러스터 버전 조건 유형 이해

### 6.16. Console Operator

참고

Console Operator는 설치 중에 클러스터 관리자가 비활성화할 수 있는 선택적 클러스터 기능입니다. 설치 시 Console Operator를 비활성화하면 클러스터가 계속 지원되며 업그레이드할 수 있습니다. 선택적 클러스터 기능에 대한 자세한 내용은 설치 의 "클러스터 기능"을 참조하십시오.

Console Operator에서 클러스터에 OpenShift Container Platform 웹 콘솔을 설치하고 유지 관리합니다. Console Operator는 기본적으로 설치되고 콘솔을 자동으로 유지 관리합니다.

#### 6.16.1. 프로젝트

console-operator

추가 리소스

웹 콘솔 기능

### 6.17. Control Plane Machine Set Operator

Control Plane Machine Set Operator는 OpenShift Container Platform 클러스터 내에서 컨트롤 플레인 머신 리소스 관리를 자동화합니다.

참고

이 Operator는 AWS(Amazon Web Services), Google Cloud, Microsoft Azure, Nutanix 및 VMware vSphere에서 사용할 수 있습니다.

#### 6.17.1. 프로젝트

cluster-control-plane-machine-set-operator

#### 6.17.2. CRD

`controlplanemachineset.machine.openshift.io`

범위: 네임스페이스

CR: `ControlPlaneMachineSet`

검증: 예

#### 6.17.3. 추가 리소스

컨트롤 플레인 머신 세트 정보

`ControlPlaneMachineSet` 사용자 정의 리소스

### 6.18. DNS Operator

DNS Operator는 CoreDNS를 배포 및 관리하고 Pod에 이름 확인 서비스를 제공하여 OpenShift Container Platform에서 DNS 기반 Kubernetes 서비스 검색을 사용할 수 있도록 합니다.

Operator는 클러스터 구성을 기반으로 작동하는 기본 배포를 생성합니다.

기본 클러스터 도메인은 `cluster.local` 입니다.

CoreDNS Corefile 또는 Kubernetes 플러그인 구성은 아직 지원되지 않습니다.

DNS Operator는 고정 IP를 사용하여 서비스로 노출되는 Kubernetes 데몬 세트로 CoreDNS를 관리합니다. CoreDNS는 클러스터의 모든 노드에서 실행됩니다.

#### 6.18.1. 프로젝트

cluster-dns-operator

### 6.19. etcd 클러스터 Operator

etcd 클러스터 Operator는 etcd 클러스터 스케일링을 자동화하고 etcd 모니터링 및 지표를 활성화하여 재해 복구 절차를 간소화합니다.

#### 6.19.1. 프로젝트

cluster-etcd-operator

#### 6.19.2. CRD

`etcds.operator.openshift.io`

범위: 클러스터

CR: `etcd`

검증: 예

#### 6.19.3. 구성 오브젝트

```shell-session
$ oc edit etcd cluster
```

### 6.20. Ingress Operator

Ingress Operator는 OpenShift Container Platform 라우터를 구성하고 관리합니다.

#### 6.20.1. 프로젝트

openshift-ingress-operator

#### 6.20.2. CRD

`clusteringresses.ingress.openshift.io`

범위: 네임스페이스

CR: `clusteringresses`

검증: 아니요

#### 6.20.3. 구성 오브젝트

클러스터 구성

유형 이름: `clusteringresses.ingress.openshift.io`

인스턴스 이름: `default`

```shell-session
$ oc get clusteringresses.ingress.openshift.io -n openshift-ingress-operator default -o yaml
```

#### 6.20.4. 참고

Ingress Operator는 `openshift-ingress` 프로젝트에서 라우터를 설정하고 라우터용 배포를 생성합니다.

```shell-session
$ oc get deployment -n openshift-ingress
```

Ingress Operator는 `network/cluster` 상태의 `clusterNetwork[].cidr` 을 사용하여 관리형 Ingress 컨트롤러(라우터)가 작동해야 하는 모드(IPv4, IPv6 또는 듀얼 스택)를 확인합니다.

예를 들어 `clusterNetwork` 에 v6 `cidr` 만 포함된 경우 Ingress 컨트롤러는 IPv6 전용 모드에서 작동합니다.

다음 예제에서는 클러스터 네트워크가 하나만 존재하고 네트워크가 IPv4 `cidr` 이므로 Ingress Operator에서 관리하는 Ingress 컨트롤러가 IPv4 전용 모드에서 실행됩니다.

```shell-session
$ oc get network/cluster -o jsonpath='{.status.clusterNetwork[*]}'
```

```shell-session
map[cidr:10.128.0.0/14 hostPrefix:23]
```

### 6.21. Insights Operator

참고

Insights Operator는 설치 중에 클러스터 관리자가 비활성화할 수 있는 선택적 클러스터 기능입니다. 선택적 클러스터 기능에 대한 자세한 내용은 설치 의 "클러스터 기능"을 참조하십시오.

Insights Operator는 OpenShift Container Platform 구성 데이터를 수집하여 Red Hat으로 보냅니다. 데이터는 클러스터가 노출될 수 있는 문제에 대한 사전 예방적 인사이트 권장 사항을 생성하는 데 사용됩니다.

이러한 통찰력은 console.redhat.com 의 Red Hat Lightspeed 권고 서비스를 통해 클러스터 관리자에게 전달됩니다.

#### 6.21.1. 프로젝트

insights-operator

#### 6.21.2. 설정

구성이 필요하지 않습니다.

#### 6.21.3. 참고

Insights Operator는 OpenShift Container Platform Telemetry를 보완합니다.

추가 리소스

Insights 기능

원격 상태 모니터링 정보

### 6.22. Kubernetes API Server Operator

Kubernetes API Server Operator는 OpenShift Container Platform 상단에 배포된 Kubernetes API 서버를 관리하고 업데이트합니다.

이 Operator는 OpenShift Container Platform `library-go` 프레임워크를 기반으로 하며 CVO(Cluster Version Operator)를 사용하여 설치됩니다.

#### 6.22.1. 프로젝트

openshift-kube-apiserver-operator

#### 6.22.2. CRD

`kubeapiservers.operator.openshift.io`

범위: 클러스터

CR: `kubeapiserver`

검증: 예

#### 6.22.3. 구성 오브젝트

```shell-session
$ oc edit kubeapiserver
```

### 6.23. Kubernetes Controller Manager Operator

Kubernetes Controller Manager Operator는 OpenShift Container Platform 상단에 배포된 Kubernetes Controller Manager를 관리하고 업데이트합니다.

이 Operator는 OpenShift Container Platform `library-go` 프레임워크를 기반으로 하며 CVO(Cluster Version Operator)를 사용하여 설치됩니다.

여기에는 다음 구성 요소가 포함됩니다.

Operator

부트스트랩 매니페스트 렌더러

정적 Pod 기반 설치

구성 관찰자

기본적으로 Operator는 `metrics` 서비스를 통해 Prometheus 지표를 표시합니다.

#### 6.23.1. 프로젝트

cluster-kube-controller-manager-operator

### 6.24. Kubernetes Scheduler Operator

Kubernetes Scheduler Operator는 OpenShift Container Platform 상단에 배포된 Kubernetes Scheduler를 관리하고 업데이트합니다.

이 Operator는 OpenShift Container Platform `library-go` 프레임워크를 기반으로 하며 CVO(Cluster Version Operator)를 사용하여 설치됩니다.

Kubernetes Scheduler Operator에는 다음 구성 요소가 포함됩니다.

Operator

부트스트랩 매니페스트 렌더러

정적 Pod 기반 설치

구성 관찰자

기본적으로 Operator는 metrics 서비스를 통해 Prometheus 지표를 표시합니다.

#### 6.24.1. 프로젝트

cluster-kube-scheduler-operator

#### 6.24.2. 설정

Kubernetes Scheduler의 구성은 다음을 병합한 결과입니다.

기본 구성.

사양 `schedulers.config.openshift.io` 에서 관찰된 구성

이러한 구성은 모두 스파스 구성으로, 마지막에 유효한 구성을 형성하기 위해 병합된, 무효화된 JSON 조각입니다.

### 6.25. Kubernetes Storage 버전 Migrator Operator

Kubernetes Storage Version Migrator Operator는 기본 스토리지 버전의 변경 사항을 감지하고, 스토리지 버전이 변경될 때 리소스 유형에 대한 마이그레이션 요청을 생성하며 마이그레이션 요청을 처리합니다.

#### 6.25.1. 프로젝트

cluster-kube-storage-version-migrator-operator

### 6.26. Machine API Operator

Machine API Operator는 Kubernetes API를 확장하는 특정 용도의 CRD(사용자 정의 리소스 정의), 컨트롤러, RBAC 오브젝트의 라이프사이클을 관리합니다. 이를 통해 클러스터에서 원하는 머신 상태를 선언합니다.

#### 6.26.1. 프로젝트

machine-api-operator

#### 6.26.2. CRD

`MachineSet`

`Machine`

`MachineHealthCheck`

### 6.27. Machine Config Operator

Machine Config Operator는 커널과 kubelet 사이의 모든 것을 포함하여 기본 운영 체제 및 컨테이너 런타임의 구성 및 업데이트를 관리하고 적용합니다.

다음의 네 가지 구성 요소가 있습니다.

`machine-config-server`: 클러스터에 가입하는 새 머신에 Ignition 설정을 제공합니다.

`machine-config-controller`: `MachineConfig` 객체에 의해 정의된 설정으로 머신 업그레이드를 조정합니다. 머신 세트의 업그레이드를 개별적으로 제어하는 옵션이 제공됩니다.

`machine-config-daemon`: 업데이트 중에 새로운 머신 설정을 적용합니다. 머신 상태를 요청한 머신 구성에 대해 검증하고 확인합니다.

`machine-config`: 처음으로 머신을 설치, 시작 및 업데이트하기위한 완전한 머신 구성 소스를 제공합니다.

중요

현재 머신 구성 서버 끝점을 차단하거나 제한하는 방법이 지원되지 않습니다. 기존 구성 또는 상태가 없는 새로 프로비저닝된 머신이 구성을 가져올 수 있도록 머신 구성 서버를 네트워크에 노출해야 합니다.

이 모델에서 trust의 루트는 CSR(인증서 서명 요청) 끝점입니다. 여기서 kubelet은 클러스터에 참여하도록 승인에 대한 인증서 서명 요청을 보냅니다.

이로 인해 시크릿 및 인증서와 같은 중요한 정보를 배포하는 데 머신 구성을 사용해서는 안 됩니다.

머신 구성 서버 엔드포인트, 포트 22623 및 22624가 베어 메탈 시나리오에서 보호되도록 고객은 적절한 네트워크 정책을 구성해야 합니다.

#### 6.27.1. 프로젝트

openshift-machine-config-operator

### 6.28. Marketplace Operator

참고

Marketplace Operator는 필요하지 않은 경우 클러스터 관리자가 비활성화할 수 있는 선택적 클러스터 기능입니다. 선택적 클러스터 기능에 대한 자세한 내용은 설치 의 "클러스터 기능"을 참조하십시오.

Marketplace Operator는 클러스터에서 기본 OLM(Operator Lifecycle Manager) 카탈로그 세트를 사용하여 클러스터 외부 Operator를 클러스터에 가져오는 프로세스를 간소화합니다. Marketplace Operator가 설치되면 `openshift-marketplace` 네임스페이스를 생성합니다.

OLM은 `openshift-marketplace` 네임스페이스에 설치된 카탈로그 소스를 클러스터의 모든 네임스페이스에 사용할 수 있도록 합니다.

#### 6.28.1. 프로젝트

operator-marketplace

추가 리소스

시장 기능

### 6.29. Node Tuning Operator

Node Tuning Operator는 TuneD 데몬을 오케스트레이션하여 노드 수준 튜닝을 관리하고 Performance Profile 컨트롤러를 사용하여 대기 시간이 짧은 성능을 달성하는 데 도움이 됩니다. 대부분의 고성능 애플리케이션에는 일정 수준의 커널 튜닝이 필요합니다.

Node Tuning Operator는 노드 수준 sysctls 사용자에게 통합 관리 인터페이스를 제공하며 사용자의 필요에 따라 지정되는 사용자 정의 튜닝을 추가할 수 있는 유연성을 제공합니다.

Operator는 OpenShift Container Platform의 컨테이너화된 TuneD 데몬을 Kubernetes 데몬 세트로 관리합니다. 클러스터에서 실행되는 모든 컨테이너화된 TuneD 데몬에 사용자 정의 튜닝 사양이 데몬이 이해할 수 있는 형식으로 전달되도록 합니다. 데몬은 클러스터의 모든 노드에서 노드당 하나씩 실행됩니다.

컨테이너화된 TuneD 데몬을 통해 적용되는 노드 수준 설정은 프로필 변경을 트리거하는 이벤트 시 또는 컨테이너화된 TuneD 데몬이 종료 신호를 수신하고 처리하여 정상적으로 종료될 때 롤백됩니다.

Node Tuning Operator는 Performance Profile 컨트롤러를 사용하여 OpenShift Container Platform 애플리케이션에 대한 짧은 대기 시간 성능을 달성하기 위해 자동 튜닝을 구현합니다.

클러스터 관리자는 다음과 같은 노드 수준 설정을 정의하도록 성능 프로필을 구성합니다.

커널을 kernel-rt로 업데이트합니다.

하우스키핑을 위한 CPU 선택.

실행 중인 워크로드를 위한 CPU 선택.

버전 4.1 이상에서는 Node Tuning Operator가 표준 OpenShift Container Platform 설치에 포함되어 있습니다.

참고

이전 버전의 OpenShift Container Platform에서는 Performance Addon Operator를 사용하여 OpenShift 애플리케이션에 대해 짧은 대기 시간 성능을 달성하기 위해 자동 튜닝을 구현했습니다. OpenShift Container Platform 4.11 이상에서 이 기능은 Node Tuning Operator의 일부입니다.

#### 6.29.1. 프로젝트

cluster-node-tuning-operator

#### 6.29.2. 추가 리소스

짧은 대기 시간 정보

### 6.30. OpenShift API Server Operator

OpenShift API Server Operator는 클러스터에서 `openshift-apiserver` 를 설치하고 유지 관리합니다.

#### 6.30.1. 프로젝트

openshift-apiserver-operator

#### 6.30.2. CRD

`openshiftapiservers.operator.openshift.io`

범위: 클러스터

CR: `openshiftapiserver`

검증: 예

### 6.31. OpenShift Controller Manager Operator

OpenShift Controller Manager Operator는 클러스터에서 `OpenShiftControllerManager` 사용자 정의 리소스를 설치하고 유지 관리하며 다음을 실행하여 확인할 수 있습니다.

```shell-session
$ oc get clusteroperator openshift-controller-manager -o yaml
```

CRD(사용자 정의 리소스 정의) `openshiftcontrollermanagers.operator.openshift.io` 는 다음을 사용하여 클러스터에서 볼 수 있습니다.

```shell-session
$ oc get crd openshiftcontrollermanagers.operator.openshift.io -o yaml
```

#### 6.31.1. 프로젝트

cluster-openshift-controller-manager-operator

### 6.32. OLM(Operator Lifecycle Manager) Classic Operator

참고

다음 섹션은 초기 릴리스 이후 OpenShift Container Platform 4에 포함된 OLM(Operator Lifecycle Manager) Classic과 관련이 있습니다. OLM v1의 경우 OLM(Operator Lifecycle Manager) v1 Operator 를 참조하십시오.

OLM(Operator Lifecycle Manager) Classic은 사용자가 OpenShift Container Platform 클러스터에서 실행되는 Kubernetes 네이티브 애플리케이션(Operator) 및 관련 서비스의 라이프사이클을 설치, 업데이트 및 관리하는 데 도움이 됩니다.

Operator 프레임워크 의 일부로, 효과적이고 자동화되었으며 확장 가능한 방식으로 Operator를 관리하도록 설계된 오픈 소스 툴킷입니다.

그림 6.1. OLM (Classic) 워크플로

OLM은 OpenShift Container Platform 4.20에서 기본적으로 실행되므로 클러스터 관리자가 클러스터에서 실행되는 Operator를 설치, 업그레이드 및 액세스 권한을 부여할 수 있습니다.

OpenShift Container Platform 웹 콘솔은 클러스터 관리자가 Operator를 설치할 수 있는 관리 화면을 제공하고, 클러스터에 제공되는 Operator 카탈로그를 사용할 수 있는 액세스 권한을 특정 프로젝트에 부여합니다.

개발자의 경우 분야별 전문가가 아니어도 셀프서비스 경험을 통해 데이터베이스, 모니터링, 빅 데이터 서비스의 인스턴스를 프로비저닝하고 구성할 수 있습니다. Operator에서 해당 지식을 제공하기 때문입니다.

#### 6.32.1. OLM Operator

CSV에 지정된 필수 리소스가 클러스터에 제공되면 OLM Operator는 CSV 리소스에서 정의하는 애플리케이션을 배포합니다.

OLM Operator는 필수 리소스 생성과는 관련이 없습니다. CLI 또는 Catalog Operator를 사용하여 이러한 리소스를 수동으로 생성하도록 선택할 수 있습니다. 이와 같은 분리를 통해 사용자는 애플리케이션에 활용하기 위해 선택하는 OLM 프레임워크의 양을 점차 늘리며 구매할 수 있습니다.

OLM Operator에서는 다음 워크플로를 사용합니다.

네임스페이스에서 CSV(클러스터 서비스 버전)를 조사하고 해당 요구 사항이 충족되는지 확인합니다.

요구사항이 충족되면 CSV에 대한 설치 전략을 실행합니다.

참고

설치 전략을 실행하기 위해서는 CSV가 Operator group의 활성 멤버여야 합니다.

#### 6.32.2. Catalog Operator

Catalog Operator는 CSV(클러스터 서비스 버전) 및 CSV에서 지정하는 필수 리소스를 확인하고 설치합니다. 또한 채널에서 패키지 업데이트에 대한 카탈로그 소스를 조사하고 원하는 경우 사용 가능한 최신 버전으로 자동으로 업그레이드합니다.

채널에서 패키지를 추적하려면 원하는 패키지를 구성하는 `Subscription` 오브젝트, 채널, 업데이트를 가져오는 데 사용할 `CatalogSource` 오브젝트를 생성하면 됩니다. 업데이트가 확인되면 사용자를 대신하여 네임스페이스에 적절한 `InstallPlan` 오브젝트를 기록합니다.

Catalog Operator에서는 다음 워크플로를 사용합니다.

클러스터의 각 카탈로그 소스에 연결합니다.

사용자가 생성한 설치 계획 중 확인되지 않은 계획이 있는지 조사하고 있는 경우 다음을 수행합니다.

요청한 이름과 일치하는 CSV를 찾아 확인된 리소스로 추가합니다.

각 관리 또는 필수 CRD의 경우 CRD를 확인된 리소스로 추가합니다.

각 필수 CRD에 대해 이를 관리하는 CSV를 확인합니다.

확인된 설치 계획을 조사하고 사용자의 승인에 따라 또는 자동으로 해당 계획에 대해 검색된 리소스를 모두 생성합니다.

카탈로그 소스 및 서브스크립션을 조사하고 이에 따라 설치 계획을 생성합니다.

#### 6.32.3. 카탈로그 레지스트리

Catalog 레지스트리는 클러스터에서 생성할 CSV 및 CRD를 저장하고 패키지 및 채널에 대한 메타데이터를 저장합니다.

패키지 매니페스트 는 패키지 ID를 CSV 세트와 연결하는 카탈로그 레지스트리의 항목입니다. 패키지 내에서 채널은 특정 CSV를 가리킵니다. CSV는 교체하는 CSV를 명시적으로 참조하므로 패키지 매니페스트는 Catalog Operator에 각 중간 버전을 거쳐 CSV를 최신 버전으로 업데이트하는 데 필요한 모든 정보를 제공합니다.

#### 6.32.4. CRD

OLM 및 Catalog Operator는 OLM 프레임워크의 기반인 CRD(사용자 정의 리소스 정의)를 관리합니다.

| 리소스 | 짧은 이름 | 소유자 | Description |
| --- | --- | --- | --- |
| `ClusterServiceVersion` (CSV) | `csv` | OLM | 애플리케이션 메타데이터: 이름, 버전, 아이콘, 필수 리소스, 설치 등입니다. |
| `InstallPlan` | `ip` | 카탈로그 | CSV를 자동으로 설치하거나 업그레이드하기 위해 생성하는 계산된 리소스 목록입니다. |
| `CatalogSource` | `catsrc` | 카탈로그 | 애플리케이션을 정의하는 CSV, CRD, 패키지의 리포지토리입니다. |
| `서브스크립션` | `sub` | 카탈로그 | 패키지의 채널을 추적하여 CSV를 최신 상태로 유지하는 데 사용됩니다. |
| `OperatorGroup` | `og` | OLM | 동일한 네임스페이스에 배포된 모든 Operator를 `OperatorGroup` 오브젝트로 구성하여 네임스페이스 목록 또는 클러스터 수준에서 CR(사용자 정의 리소스)을 조사합니다. |

또한 각 Operator는 다음 리소스를 생성합니다.

| 리소스 | 소유자 |
| --- | --- |
| `Deployments` | OLM |
| `ServiceAccounts` |
| `(Cluster)Roles` |
| `(Cluster)RoleBindings` |
| CRD( `CustomResourceDefinitions` ) | 카탈로그 |
| `ClusterServiceVersions` |

#### 6.32.5. 클러스터 Operator

OpenShift Container Platform에서 OLM 기능은 클러스터 Operator 세트에서 제공됩니다.

`operator-lifecycle-manager`

OLM Operator를 제공합니다. 또한 `olm.maxOpenShiftVersion` 속성에 따라 클러스터 업그레이드를 차단하는 설치된 Operator가 있는지 클러스터 관리자에게 알립니다. 자세한 내용은 "OpenShift Container Platform 버전과 Operator 호환성 제어"를 참조하십시오.

`operator-lifecycle-manager-catalog`

Catalog Operator를 제공합니다.

`operator-lifecycle-manager-packageserver`

클러스터의 모든 카탈로그에서 메타데이터를 수집하고 사용자용 `PackageManifest` API를 제공하는 API 확장 서버를 나타냅니다.

#### 6.32.6. 추가 리소스

OLM(Operator Lifecycle Manager) 이해

### 6.33. OLM(Operator Lifecycle Manager) v1 Operator

OpenShift Container Platform 4.18부터 OLM v1은 기본적으로 OLM(Classic)과 함께 활성화됩니다. 이 차세대 반복에서는 클러스터 관리자가 사용자의 기능을 확장할 수 있는 많은 OLM(Classic) 개념을 개발하는 업데이트된 프레임워크를 제공합니다.

OLM v1은 `registry+v1` 번들 형식을 통해 Operator를 포함하는 새 `ClusterExtension` 오브젝트의 라이프사이클을 관리하고 클러스터 내에서 확장의 설치, 업그레이드 및 역할 기반 액세스 제어(RBAC)를 제어합니다.

OpenShift Container Platform에서 OLM v1은 `olm` 클러스터 Operator에서 제공합니다.

참고

`olm` cluster Operator는 `olm.maxOpenShiftVersion` 속성에 따라 클러스터 업그레이드를 차단하는 설치된 확장이 있는지 클러스터 관리자에게 알립니다. 자세한 내용은 "OpenShift Container Platform 버전과의 호환성"을 참조하십시오.

#### 6.33.1. components

OLM(Operator Lifecycle Manager) v1은 다음과 같은 구성 요소 프로젝트로 구성됩니다.

Operator Controller

사용자가 Operator 및 확장의 라이프사이클을 설치하고 관리할 수 있는 API를 사용하여 Kubernetes를 확장하는 OLM v1의 중앙 구성 요소입니다. catalogd의 정보를 사용합니다.

Catalogd

클러스터 클라이언트의 사용을 위해 패키지화되고 컨테이너 이미지에 제공된 파일 기반 카탈로그(FBC) 콘텐츠의 압축을 풀는 Kubernetes 확장입니다. OLM v1 마이크로 서비스 아키텍처의 구성 요소로, 확장 작성자가 패키지한 Kubernetes 확장 기능에 대한 카탈로그 호스트 메타데이터를 호스트하므로 사용자가 설치 가능한 콘텐츠를 검색하는 데 도움이 됩니다.

#### 6.33.2. CRD

`clusterextension.olm.operatorframework.io`

범위: 클러스터

CR: `ClusterExtension`

`clustercatalog.olm.operatorframework.io`

범위: 클러스터

CR: `ClusterCatalog`

#### 6.33.3. 프로젝트

operator-framework/operator-controller

operator-framework/catalogd

#### 6.33.4. 추가 리소스

확장 개요

OpenShift Container Platform 버전과의 호환성

### 6.34. OpenShift Service CA Operator

OpenShift Service CA Operator는 Kubernetes 서비스에 대한 인증서를 검색하고 관리합니다.

#### 6.34.1. 프로젝트

openshift-service-ca-operator

### 6.35. vSphere Problem Detector Operator

vSphere Problem Detector Operator는 스토리지와 관련된 일반적인 설치 및 잘못된 구성 문제를 위해 vSphere에 배포된 클러스터를 확인합니다.

참고

vSphere Problem Detector Operator는 Cluster Storage Operator가 클러스터가 vSphere에 배포되었음을 탐지하는 경우에만 Cluster Storage Operator에 의해 시작됩니다.

#### 6.35.1. 설정

구성이 필요하지 않습니다.

#### 6.35.2. 참고

Operator는 vSphere에서 OpenShift Container Platform 설치를 지원합니다.

Operator는 `vsphere-cloud-credentials` 를 사용하여 vSphere와 통신합니다.

Operator는 스토리지와 관련된 검사를 수행합니다.

추가 리소스

vSphere Problem Detector Operator 사용

### 7.1. Operator Lifecycle Manager v1 정보

OLM(Operator Lifecycle Manager)은 최초 릴리스 이후 OpenShift Container Platform 4에 포함되어 있습니다. OpenShift Container Platform 4.18에는 이 단계에서 OLM v1 로 알려진 일반 사용 가능(GA) 기능으로 OLM의 차세대 반복을 위한 구성 요소가 포함되어 있습니다.

이 업데이트된 프레임워크는 이전 버전의 OLM에 포함된 여러 개념을 개발하고 새로운 기능을 추가합니다.

OpenShift Container Platform 4.17부터 OLM v1에 대한 문서가 다음 새 가이드로 이동되었습니다.

확장 (OLM v1)
