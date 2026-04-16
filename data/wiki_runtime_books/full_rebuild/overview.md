# 개요

[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/247-OpenShift-Kubernetes-Overview.png" alt="247 OpenShift Kubernetes 개요" kind="diagram" diagram_type="semantic_diagram"]
247 OpenShift Kubernetes 개요
[/FIGURE]

_Source: `overview.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Overview-ko-KR/images/57e7cf27848f5d30a70a61ea778c1101/247-OpenShift-Kubernetes-Overview.png`_


## OpenShift Container Platform 소개

이 문서에서는 OpenShift Container Platform 기능에 대한 개요를 설명합니다.

## 1장. OpenShift Container Platform 4.20 문서

목차

OpenShift Container Platform 4.20 공식 문서에 오신 것을 환영합니다. 여기에서 OpenShift Container Platform에 대해 알아보고 해당 기능을 살펴볼 수 있습니다.

OpenShift Container Platform 4.20 문서를 탐색하려면 다음 방법 중 하나를 사용할 수 있습니다.

탐색 모음을 사용하여 문서를 찾습니다.

OpenShift Container Platform에 대해 자세히 알아보기 에서 관심 있는 작업을 선택합니다.

OpenShift Container Platform에는 추가 기능을 추가하고 클러스터의 기능을 확장할 수 있는 다양한 계층 서비스가 있습니다. 자세한 내용은 OpenShift Container Platform Operator 라이프 사이클 을 참조하십시오.

## 2장. OpenShift Container Platform 소개

OpenShift Container Platform은 클라우드 기반 Kubernetes 컨테이너 플랫폼입니다. OpenShift Container Platform의 기초는 Kubernetes를 기반으로 하므로 동일한 기술을 공유합니다.

애플리케이션 및 애플리케이션을 지원하는 데이터센터를 몇 대의 머신 및 애플리케이션에서 수백만 클라이언트에 서비스를 제공하는 수천 대의 컴퓨터로 확장 가능하도록 설계되었습니다.

OpenShift Container Platform을 사용하면 다음을 수행할 수 있습니다.

개발자와 IT 조직에 안전하고 확장 가능한 리소스에 애플리케이션을 배포하는 데 사용할 수 있는 클라우드 애플리케이션 플랫폼을 제공합니다.

최소한의 구성 및 관리 오버헤드가 필요합니다.

Kubernetes 플랫폼을 고객 데이터 센터 및 클라우드에 가져옵니다.

보안, 개인 정보 보호, 컴플라이언스 및 거버넌스 요구 사항을 충족합니다.

Kubernetes에 기반을 둔 OpenShift Container Platform은 대규모 통신, 스트리밍 비디오, 게임, 뱅킹 및 기타 애플리케이션의 엔진 역할을 하는 동일한 기술을 통합합니다. Red Hat의 오픈 기술로 구현하면 컨테이너화된 애플리케이션을 단일 클라우드에서 온프레미스 및 다중 클라우드 환경으로 확장할 수 있습니다.

OpenShift Container Platform은 컨테이너화된 애플리케이션을 개발하고 실행하기 위한 플랫폼입니다. 애플리케이션 및 애플리케이션을 지원하는 데이터센터를 몇 대의 머신 및 애플리케이션에서 수백만 클라이언트에 서비스를 제공하는 수천 대의 컴퓨터로 확장 가능하도록 설계되었습니다.

### 2.1. OpenShift Container Platform 이해

[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/oke-about-ocp-stack-image.png" alt="Red Hat OpenShift Kubernetes Engine" kind="figure" diagram_type="image_figure"]
Red Hat OpenShift Kubernetes Engine
[/FIGURE]

_Source: `overview.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Overview-ko-KR/images/785227c5bdddf26566a9c43c0ddfcab6/oke-about-ocp-stack-image.png`_


OpenShift Container Platform은 베어 메탈, 가상화, 온프레미스, 클라우드와 같은 다양한 컴퓨팅 플랫폼에 대한 컨테이너 기반 애플리케이션의 라이프사이클과 종속 항목을 관리하는 Kubernetes 환경입니다. OpenShift Container Platform은 컨테이너를 배포, 구성 및 관리합니다.

OpenShift Container Platform은 구성 요소의 사용성, 안정성 및 사용자 지정 기능을 제공합니다.

OpenShift Container Platform은 노드라고 하는 여러 컴퓨팅 리소스를 사용합니다. 노드에는 RHCOS(Red Hat Enterprise Linux CoreOS)라는 RHEL(Red Hat Enterprise Linux CoreOS)을 기반으로 하는 경량의 보안 운영 체제가 있습니다.

노드가 부팅 및 구성되면 예약된 컨테이너 워크로드의 이미지를 관리하고 실행하기 위해 CRI-O 또는 Docker와 같은 컨테이너 런타임을 가져옵니다. Kubernetes 에이전트 또는 kubelet은 노드에서 컨테이너 워크로드를 예약합니다. kubelet은 클러스터에 노드를 등록하고 컨테이너 워크로드의 세부 정보를 수신해야 합니다.

OpenShift Container Platform은 클러스터의 네트워킹, 로드 밸런싱 및 라우팅을 구성하고 관리합니다. OpenShift Container Platform은 클러스터 상태 및 성능, 로깅 및 업그레이드 관리를 위한 클러스터 서비스를 추가합니다.

컨테이너 이미지 레지스트리 및 소프트웨어 카탈로그는 클러스터 내에서 다양한 애플리케이션 서비스를 제공하기 위한 Red Hat 인증 제품 및 커뮤니티 빌드 소프트웨어를 제공합니다.

이러한 애플리케이션 및 서비스는 클러스터, 데이터베이스, 프런트 엔드 및 사용자 인터페이스, 애플리케이션 런타임 및 비즈니스 자동화, 컨테이너 애플리케이션 개발 및 테스트를 위한 개발자 서비스에 배포된 애플리케이션을 관리합니다.

사전 빌드된 이미지 또는 Operator라는 리소스를 통해 실행되는 컨테이너 배포를 구성하여 클러스터 내에서 애플리케이션을 수동으로 관리할 수 있습니다. 사전 빌드 이미지 및 소스 코드에서 사용자 정의 이미지를 빌드하고 이러한 사용자 지정 이미지를 내부, 개인 또는 퍼블릭 레지스트리에 로컬로 저장할 수 있습니다.

멀티클러스터 관리 계층은 단일 콘솔에서 워크로드 배포, 구성, 규정 준수 및 배포를 포함하여 여러 클러스터를 관리할 수 있습니다.

#### 2.1.1. 사용 사례

Red Hat OpenShift는 다양한 사용 사례를 지원하기 위해 업계에서 널리 채택되어 조직이 애플리케이션을 현대화하고 인프라를 최적화하며 운영 효율성을 향상시킬 수 있습니다.

OpenShift Virtualization

VM(가상 머신)과 컨테이너를 병렬로 관리할 수 있는 통합 플랫폼을 제공하여 작업을 간소화하고 복잡성을 줄입니다.

VM 워크로드를 효율적으로 확장할 수 있는 강력한 인프라를 제공합니다.

VM 환경을 보호하기 위해 향상된 보안 기능을 제공하여 규정 준수 및 데이터 무결성을 보장합니다.

자세한 구현 지침 및 샘플 아키텍처는 OpenShift Virtualization - 참조 구현 가이드를 참조하십시오.

이 문서에서는 VMware Cloud Foundation, VMware vSphere Foundation, Red Hat Virtualization 및 OpenStack과 같은 플랫폼에서 OpenShift를 OpenShift Virtualization으로 전환하는 환경을 위해 설계된 가상화 워크로드를 위한 호스팅 솔루션으로 OpenShift를 배포하는 모범 사례를 설명합니다.

인공 지능 및 머신 러닝(AI/ML) 작업을 포함한 애플리케이션 현대화

레거시 애플리케이션의 컨테이너화 및 리팩토링을 활성화합니다.

비즈니스 로직을 보존하는 동시에 애플리케이션을 클라우드에 적합하고 유지 관리 가능하게 만듭니다.

표준화된 ML 인프라를 사용하여 모델 교육 및 추론 워크로드를 지원합니다.

데이터 사이언스 워크플로우와 완벽하게 통합됩니다.

멀티클라우드 및 하이브리드 클라우드 배포

온프레미스 데이터 센터와 여러 퍼블릭 클라우드에 일관된 플랫폼을 제공합니다.

벤더 종속을 방지하고 워크로드 배치를 최적화할 수 있습니다.

DevOps 사용

CI/CD(Continuous Delivery and continuous integration) 파이프라인 및 GitOps 워크플로는 소프트웨어 개발을 간소화합니다.

소프트웨어 제공을 가속화하기 위한 개발자 셀프 서비스 기능을 제공합니다.

엣지 컴퓨팅

통신, 소매 및 제조와 같은 산업의 데이터 소스에 분산 컴퓨팅을 더 가깝게 수행할 수 있습니다.

3노드 클러스터, 단일 노드 클러스터, Red Hat Device Edge 또는 MicroShift를 포함한 가벼운 배포 패턴을 지원합니다.

온-프레미스 배포를 지원합니다.

규정 준수

금융 서비스, 의료 및 정부 기관의 규정 준수 요구 사항을 충족할 수 있는 강력한 보안 기능을 제공합니다.

마이크로 서비스 아키텍처

서비스 메시, API 관리 및 서버리스 기능을 사용하여 클라우드 네이티브 애플리케이션 개발을 지원합니다.

Enterprise SaaS 제공

일관된 작업으로 멀티 테넌트 SaaS 애플리케이션 배포를 지원합니다.

Advanced Cluster Management (ACM) 및 Advanced Cluster Security (ACS)를 사용한 호스트 컨트롤 플레인, cluster-as-a-service 및 플릿 수준 관리와 같은 기능이 포함되어 있습니다.

자세한 사용 사례를 보려면 사용 사례를 참조하십시오.

다양한 사용 사례에 맞는 추가 권장 솔루션은 Red Hat의 솔루션 패턴 을 참조하십시오.

추가 리소스

단일 노드에 설치할 준비

## 3장. OpenShift Container Platform에 대해 자세히 알아보기

다음 섹션을 사용하여 OpenShift Container Platform 기능에 대해 알아보고 더 잘 이해할 수 있도록 콘텐츠를 찾습니다.

### 3.1. 학습 및 지원

| OpenShift Container Platform에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| OpenShift Container Platform의 새로운 기능 | OpenShift 블로그 |
| OpenShift Container Platform 라이프 사이클 정책 | OpenShift Container Platform 라이프 사이클 |
| OpenShift Interactive Learning Portal | OpenShift 지식베이스 문서 |
| 지원 요청 | 클러스터에 대한 데이터 수집 |

### 3.2. 아키텍처

| OpenShift Container Platform에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| OpenShift를 사용한 Enterprise Kubernetes | 테스트된 플랫폼 |
| 아키텍처 | 보안 및 컴플라이언스 |
| 네트워킹 | OVN-Kubernetes 아키텍처 |
| 백업 및 복원 | 이전 클러스터 상태로 복원 |

### 3.3. 설치

다음 OpenShift Container Platform 설치 작업을 살펴봅니다.

| OpenShift Container Platform의 설치에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| OpenShift Container Platform 설치 프로그램 개요 | 클러스터 설치 방법 선택 및 사용자를 위한 준비 |
| FIPS 모드에서 클러스터 설치 | FIPS 컴플라이언스 정보 |

### 3.4. 기타 클러스터 설치 프로그램 작업

| OpenShift Container Platform의 다른 설치 프로그램 작업에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| 설치 문제 해결 | 설치 검증 |
| Red Hat OpenShift Data Foundation 설치 | OpenShift의 이미지 모드 |

#### 3.4.1. 네트워크가 제한된 환경에서 클러스터 설치

| 제한된 네트워크에 설치하는 방법 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| 연결 해제된 설치 미러링 정보 | 클러스터가 사용자 프로비저닝 인프라를 사용하고 클러스터가 인터넷에 대한 전체 액세스 권한이 없는 경우 OpenShift Container Platform 설치 이미지를 미러링해야 합니다. AWS(Amazon Web Services) Google Cloud vSphere IBM Cloud® IBM Z® 및 IBM® LinuxONE IBM Power® 베어 메탈 |

#### 3.4.2. 기존 네트워크에 클러스터 설치

| 제한된 네트워크에 설치하는 방법 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| AWS(Amazon Web Services) 또는 Google Cloud 에서 기존 VPC(Virtual Private Cloud) 를 사용하거나 Microsoft Azure에 기존 VNet 을 사용하는 경우 클러스터를 설치할 수 있습니다. | Google Cloud의 클러스터를 공유 VPC에 설치 |

### 3.5. 클러스터 관리자

| OpenShift Container Platform 클러스터 활동에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| OpenShift Container Platform 관리 이해 | 머신 API Operator * etcd |
| 클러스터 기능 활성화 | OpenShift Container Platform 4.20의 선택적 클러스터 기능 |

#### 3.5.1.1. 클러스터 구성 요소 관리

| 클러스터 구성 요소 관리에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| 머신 세트를 사용하여 컴퓨팅 및 컨트롤 플레인 시스템 관리 | 머신 상태 점검 배포 |
| OpenShift Container Platform 클러스터에 자동 스케일링 적용 | Pod 예약 결정에 Pod 우선순위 포함 |
| 컨테이너 레지스트리 관리 | Red Hat Quay |
| 사용자 및 그룹 관리 | system:admin 사용자 가장 |
| 인증 관리 | 여러 ID 공급자 |
| Ingress , API 서버 및 서비스 인증서 관리 | 네트워크 보안 |
| 네트워킹 관리 | CNO(Cluster Network Operator) 다중 네트워크 인터페이스 네트워크 정책 |
| Operator 관리 | 설치된 Operator에서 애플리케이션 생성 |

#### 3.5.1.2. 클러스터 구성 요소 변경

| 클러스터 구성 요소 변경에 대해 자세히 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| OpenShift 업데이트 소개 | 웹 콘솔을 사용하여 클러스터 업데이트 CLI를 사용하여 업데이트 연결이 끊긴 환경에서 OpenShift Update Service 사용 |
| CRD(사용자 정의 리소스 정의)를 사용하여 클러스터 수정 | CRD 생성 CRD에서 리소스 관리 |
| 리소스 할당량 설정 | 다중 프로젝트의 리소스 할당량 |
| 리소스 정리 및 회수 | 고급 빌드 수행 |
| 클러스터 확장 및 조정 | OpenShift Container Platform 확장성 및 성능 |

### 3.6. 클러스터 모니터링

| OpenShift Container Platform에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| Red Hat OpenShift Distributed Tracing Platform 릴리스 노트 | Red Hat OpenShift Distributed Tracing Platform |
| Red Hat build of OpenTelemetry | 여러 클러스터에서 Telemetry 데이터 수신 |
| 네트워크 Observability 정보 | 대시보드 및 경고로 메트릭 사용 트래픽 흐름 보기의 네트워크 트래픽 예약 |
| OpenShift Container Platform 모니터링 정보 | 원격 상태 모니터링 Red Hat OpenShift의 전원 모니터링 (기술 프리뷰) |

### 3.7. 스토리지 활동

| OpenShift Container Platform에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| 스토리지 유형 | 영구 스토리지 임시 스토리지 |

### 3.8. 애플리케이션 사이트 안정성 엔지니어 (App SRE)

| OpenShift Container Platform에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| 애플리케이션 빌드 개요 | 프로젝트 |
| Operator | Cluster Operator 참조 |

### 3.9. 개발자

OpenShift Container Platform은 컨테이너화된 애플리케이션을 개발하고 배포하기 위한 플랫폼입니다. OpenShift Container Platform 기능을 더 잘 이해할 수 있도록 다음 OpenShift Container Platform 설명서를 읽으십시오.

| OpenShift Container Platform의 애플리케이션 개발에 대해 알아보기 | 선택적 추가 리소스 |
| --- | --- |
| 개발자를 위한 OpenShift 시작하기(대화형 튜토리얼) | OpenShift Container Platform 개발 이해 노드 작업 배포 생성 |
| Red Hat 개발자 사이트 | 이미지 빌드 이해 |
| Red Hat OpenShift Dev Spaces (이전 Red Hat CodeReady Workspaces) | Operator |
| 컨테이너 이미지 생성 | 이미지 관리 개요 |
| `odo` | 개발자 중심 CLI |
| 토폴로지 보기를 사용하여 애플리케이션 구성 보기 | 애플리케이션 내보내기 |
| OpenShift Pipelines 이해 | CI/CD 파이프라인 생성 |
| 클러스터 구성으로 애플리케이션을 배포하여 OpenShift 클러스터 구성 | 노드 테인트를 사용하여 Pod 배치 제어 인프라 머신 세트 생성 |

## 4장. Kubernetes 개요

Kubernetes는 Google에서 개발한 오픈 소스 컨테이너 오케스트레이션 툴입니다. Kubernetes를 사용하여 컨테이너 기반 워크로드를 실행하고 관리할 수 있습니다.

가장 일반적인 Kubernetes 사용 사례는 상호 연결된 마이크로 서비스 배열을 배포하여 클라우드 네이티브 방식으로 애플리케이션을 구축하는 것입니다. 온프레미스, 퍼블릭, 프라이빗 또는 하이브리드 클라우드에 걸쳐 호스트를 확장할 수 있는 Kubernetes 클러스터를 생성할 수 있습니다.

일반적으로 애플리케이션은 단일 운영 체제 위에 배포되었습니다. 가상화를 사용하면 물리적 호스트를 여러 가상 호스트로 분할할 수 있습니다.

공유 리소스의 가상 인스턴스에서 작업하는 것은 효율성 및 확장성에 적합하지 않습니다. VM(가상 머신)은 실제 머신만큼 많은 리소스를 사용하므로 CPU, RAM, 스토리지와 같은 VM에 리소스를 제공하면 비용이 많이 듭니다.

또한 공유 리소스에서 가상 인스턴스 사용량으로 인해 애플리케이션이 성능이 저하될 수 있습니다.

그림 4.1. 클래식 배포를 위한 컨테이너 기술의 진화

이 문제를 해결하려면 컨테이너화된 환경에서 애플리케이션을 분리하는 컨테이너화 기술을 사용할 수 있습니다. VM과 유사하게 컨테이너에는 자체 파일 시스템, vCPU, 메모리, 프로세스 공간, 종속성 등이 있습니다.

컨테이너는 기본 인프라와 분리되며 클라우드 및 OS 배포 전반에서 이식 가능합니다. 컨테이너는 완전한 기능을 갖춘 OS보다 훨씬 가벼우며 운영 체제 커널에서 실행되는 경량의 격리된 프로세스입니다.

VM은 부팅 속도가 느리고 물리적 하드웨어에 대한 추상화입니다. 하이퍼바이저를 통해 단일 시스템에서 VM을 실행합니다.

Kubernetes를 사용하여 다음 작업을 수행할 수 있습니다.

리소스 공유

여러 호스트에서 컨테이너 오케스트레이션

새 하드웨어 구성 설치

상태 점검 실행 및 자동 복구 애플리케이션 실행

컨테이너화된 애플리케이션 스케일링

### 4.1. Kubernetes 구성 요소

| Component | 목적 |
| --- | --- |
| `kube-proxy` | 클러스터의 모든 노드에서 실행되며 Kubernetes 리소스 간의 네트워크 트래픽을 유지 관리합니다. |
| `kube-controller-manager` | 클러스터 상태를 관리합니다. |
| `kube-scheduler` | 노드에 pod를 할당합니다. |
| `etcd` | 클러스터 데이터를 저장합니다. |
| `kube-apiserver` | API 오브젝트의 데이터를 검증하고 구성합니다. |
| `kubelet` | 노드에서 실행되며 컨테이너 매니페스트를 읽습니다. 정의된 컨테이너가 시작되어 실행 중인지 확인합니다. |
| `kubectl` | 워크로드를 실행하려는 방법을 정의할 수 있습니다. `kubectl` 명령을 사용하여 `kube-apiserver` 와 상호 작용합니다. |
| 노드 | 노드는 Kubernetes 클러스터의 물리적 시스템 또는 VM입니다. 컨트롤 플레인은 모든 노드를 관리하고 Kubernetes 클러스터의 노드에서 Pod를 예약합니다. |
| 컨테이너 런타임 | 컨테이너 런타임은 호스트 운영 체제에서 컨테이너를 실행합니다. Pod를 노드에서 실행할 수 있도록 각 노드에 컨테이너 런타임을 설치해야 합니다. |
| 영구 스토리지 | 장치가 종료된 후에도 데이터를 저장합니다. Kubernetes는 영구 볼륨을 사용하여 애플리케이션 데이터를 저장합니다. |
| `container-registry` | 컨테이너 이미지를 저장하고 액세스합니다. |
| Pod | Pod는 Kubernetes에서 가장 작은 논리 단위입니다. Pod에는 작업자 노드에서 실행할 하나 이상의 컨테이너가 포함되어 있습니다. |

### 4.2. Kubernetes 리소스

[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/247_OpenShift_Kubernetes_Overview-1.png" alt="247 OpenShift Kubernetes 개요 1" kind="diagram" diagram_type="semantic_diagram"]
247 OpenShift Kubernetes 개요 1
[/FIGURE]

_Source: `overview.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Overview-ko-KR/images/16b84090439adc71ef80265d0ed0ef48/247_OpenShift_Kubernetes_Overview-1.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/247_OpenShift_Kubernetes_Overview-2.png" alt="247 OpenShift Kubernetes 개요 2" kind="diagram" diagram_type="semantic_diagram"]
247 OpenShift Kubernetes 개요 2
[/FIGURE]

_Source: `overview.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Overview-ko-KR/images/c8d00fda77932b65f092760ad269d15c/247_OpenShift_Kubernetes_Overview-2.png`_


사용자 정의 리소스는 Kubernetes API의 확장입니다. 사용자 정의 리소스를 사용하여 Kubernetes 클러스터를 사용자 지정할 수 있습니다.

Operator는 사용자 정의 리소스를 사용하여 애플리케이션 및 해당 구성 요소를 관리하는 소프트웨어 확장입니다. Kubernetes는 클러스터 리소스를 처리하는 동안 고정된 결과를 원하는 경우 선언적 모델을 사용합니다.

Operator를 사용하여 Kubernetes는 선언적 방식으로 상태를 정의합니다. 필수 명령을 사용하여 Kubernetes 클러스터 리소스를 수정할 수 있습니다.

Operator는 원하는 리소스 상태를 리소스의 실제 상태와 지속적으로 비교하고 원하는 상태와 일치하도록 현실을 구현하기 위한 조치를 취하는 제어 루프 역할을 합니다.

그림 4.2. Kubernetes 클러스터 개요

| 리소스 | 목적 |
| --- | --- |
| Service | Kubernetes는 서비스를 사용하여 pod 세트에 실행 중인 애플리케이션을 노출합니다. |
| `ReplicaSets` | Kubernetes는 `ReplicaSets` 를 사용하여 일정한 pod 번호를 유지합니다. |
| Deployment | 애플리케이션의 라이프사이클을 유지보수하는 리소스 오브젝트입니다. |

Kubernetes는 OpenShift Container Platform의 핵심 구성 요소입니다. OpenShift Container Platform을 사용하여 컨테이너화된 애플리케이션을 개발하고 실행할 수 있습니다.

Kubernetes에 기반을 둔 OpenShift Container Platform은 대규모 통신, 스트리밍 비디오, 게임, 뱅킹 및 기타 애플리케이션의 엔진 역할을 하는 동일한 기술을 통합합니다.

OpenShift Container Platform을 사용하여 컨테이너화된 애플리케이션을 단일 클라우드 이상으로 온프레미스 및 다중 클라우드 환경으로 확장할 수 있습니다.

그림 4.3. Kubernetes 아키텍처

클러스터는 클라우드 환경에서 여러 노드로 구성된 단일 계산 단위입니다. Kubernetes 클러스터에는 컨트롤 플레인 및 작업자 노드가 포함됩니다.

다양한 머신 및 환경에서 Kubernetes 컨테이너를 실행할 수 있습니다. 컨트롤 플레인 노드는 클러스터 상태를 제어하고 유지보수합니다.

작업자 노드를 사용하여 Kubernetes 애플리케이션을 실행할 수 있습니다. Kubernetes 네임스페이스를 사용하여 클러스터의 클러스터 리소스를 구분할 수 있습니다.

네임스페이스 범위는 배포, 서비스 및 Pod와 같은 리소스 오브젝트에 적용할 수 있습니다. 스토리지 클래스, 노드, 영구 볼륨과 같은 클러스터 전체 리소스 오브젝트에는 네임스페이스를 사용할 수 없습니다.

### 4.3. Kubernetes 개념 가이드라인

OpenShift Container Platform을 시작하기 전에 Kubernetes의 개념적 가이드라인을 고려하십시오.

하나 이상의 작업자 노드에서 시작하여 컨테이너 워크로드를 실행합니다.

하나 이상의 컨트롤 플레인 노드에서 해당 워크로드의 배포를 관리합니다.

컨테이너를 포드라는 배포 단위로 래핑합니다. Pod를 사용하면 컨테이너에 추가 메타데이터를 제공하고 단일 배포 엔티티에서 여러 컨테이너를 그룹화할 수 있습니다.

특별한 종류의 자산을 생성합니다. 예를 들어 서비스는 pod 세트와 Pod에 액세스하는 방법을 정의하는 정책으로 표시됩니다.

이 정책을 통해 컨테이너는 서비스에 대한 특정 IP 주소가 없어도 필요한 서비스에 연결할 수 있습니다. 복제 컨트롤러는 한 번에 실행하는 데 필요한 포드 복제본 수를 나타내는 또 다른 특수 자산입니다.

이 기능을 사용하여 현재 수요에 맞게 애플리케이션을 자동으로 확장할 수 있습니다.

OpenShift Container Platform 클러스터로의 API는 100% Kubernetes입니다. 다른 Kubernetes에서 실행되고 OpenShift Container Platform에서 실행되는 컨테이너 간에는 변경되지 않습니다.

애플리케이션에 대한 변경 사항이 없습니다. OpenShift Container Platform은 Kubernetes에 엔터프라이즈급 개선사항을 제공하기 위해 추가 값 기능을 제공합니다.

OpenShift Container Platform CLI 툴()은 다음 명령과 호환됩니다. Kubernetes API는 OpenShift Container Platform 내에서 100% 액세스할 수 있지만 아래 명령줄에는 사용자 친화적인 기능이 많이 없습니다.

```shell
oc
```

```shell
kubectl
```

```shell
kubectl
```

OpenShift Container Platform에서는 다음 명령과 같은 기능 명령줄 툴 세트를 제공합니다. Kubernetes는 애플리케이션 관리에 뛰어나지만 플랫폼 수준 요구사항 또는 배포 프로세스를 지정하거나 관리하지는 않습니다.

```shell
oc
```

강력하고 유연한 플랫폼 관리 툴 및 프로세스는 OpenShift Container Platform에서 제공하는 중요한 이점입니다. 컨테이너화 플랫폼에 인증, 네트워킹, 보안, 모니터링 및 로그 관리를 추가해야 합니다.

## 5장. Red Hat OpenShift 버전

Red Hat OpenShift는 다양한 배포 모델 및 운영 기본 설정을 지원하기 위해 여러 버전으로 제공됩니다. 각 버전은 통합된 툴, 보안 기능 및 개발자 경험을 통해 일관된 Kubernetes 플랫폼을 제공합니다. OpenShift는 클라우드 서비스 및 자체 관리 버전에서 사용할 수 있습니다.

### 5.1. 클라우드 서비스 버전

Red Hat OpenShift는 다양한 조직의 요구 사항을 충족하기 위해 다양한 클라우드 서비스 버전을 제공합니다. 이러한 장치는 주요 클라우드 공급자의 완전 관리형 애플리케이션 플랫폼을 제공합니다.

Red Hat OpenShift Service on AWS(ROSA)

조직이 네이티브 AWS 환경에서 애플리케이션을 빌드, 배포 및 확장할 수 있도록 지원하는 완전 관리형 애플리케이션 플랫폼입니다. 자세한 내용은 AWS의 Red Hat OpenShift Service를 참조하십시오.

Microsoft Azure Red Hat OpenShift

조직이 Azure에서 애플리케이션을 빌드, 배포 및 확장할 수 있도록 지원하는 완전 관리형 애플리케이션 플랫폼입니다. 자세한 내용은 Microsoft Azure Red Hat OpenShift 를 참조하십시오.

Red Hat OpenShift Dedicated

Google Cloud에서 관리형 Red Hat OpenShift 제품을 사용할 수 있습니다. 자세한 내용은 Red Hat OpenShift Dedicated 를 참조하십시오.

Red Hat OpenShift on IBM Cloud

운영의 복잡성을 줄이고 개발자가 IBM Cloud에서 애플리케이션을 빌드하고 확장하는 데 도움이 되는 관리형 OpenShift 클라우드 서비스입니다. 자세한 내용은 IBM Cloud의 Red Hat OpenShift를 참조하십시오.

### 5.2. 자체 관리 대상

Red Hat OpenShift는 자체 인프라에서 OpenShift를 배포, 구성 및 관리하는 것을 선호하는 조직을 위해 자체 관리 버전을 제공합니다. 이러한 판은 OpenShift의 기능을 활용하는 동시에 플랫폼에 대한 유연성과 제어 기능을 제공합니다.

Red Hat OpenShift Container Platform (OCP)

컨테이너화된 애플리케이션을 빌드하고 스케일링하기 위한 완전한 작업 및 개발자 서비스 및 툴 세트를 제공합니다. 자세한 내용은 Red Hat OpenShift Container Platform 을 참조하십시오.

Red Hat OpenShift Platform Plus

OpenShift Container Platform의 기능을 기반으로 합니다. 자세한 내용은 Red Hat OpenShift Platform Plus 를 참조하십시오.

Red Hat OpenShift Kubernetes Engine

Red Hat Enterprise Linux CoreOS (RHCOS)에서 엔터프라이즈 Kubernetes의 기본 보안 중심 기능을 제공하여 하이브리드 클라우드 환경에서 컨테이너를 실행합니다. 자세한 내용은 Red Hat OpenShift Kubernetes Engine 을 참조하십시오.

Red Hat OpenShift Virtualization Engine

Red Hat OpenShift의 가상화 기능을 간소화하고 비용 효율적인 솔루션으로 VM을 독점적으로 배포, 관리 및 확장할 수 있습니다. 자세한 내용은 Red Hat OpenShift Virtualization Engine 을 참조하십시오.

## 6장. OpenShift Container Platform의 일반 용어집

이 용어집은 일반적인 Kubernetes 및 OpenShift Container Platform 용어를 정의합니다.

액세스 정책

클러스터 내의 사용자, 애플리케이션 및 엔터티가 서로 상호 작용하는 방식을 지정하는 일련의 역할입니다. 액세스 정책은 클러스터 보안을 강화합니다.

승인 플러그인

승인 플러그인은 보안 정책, 리소스 제한 또는 구성 요구 사항을 적용합니다.

인증

OpenShift Container Platform 클러스터에 대한 액세스를 제어하기 위해 클러스터 관리자는 승인된 사용자만 클러스터에 액세스할 수 있도록 사용자 인증을 구성할 수 있습니다. OpenShift Container Platform 클러스터와 상호 작용하려면 OpenShift Container Platform API로 인증해야 합니다.

OpenShift Container Platform API에 대한 요청에 OAuth 액세스 토큰 또는 X.509 클라이언트 인증서를 제공하여 인증할 수 있습니다.

부트스트랩

최소한의 Kubernetes를 실행하고 OpenShift Container Platform 컨트롤 플레인을 배포하는 임시 시스템입니다.

Build

빌드는 소스 코드와 같은 입력 매개 변수를 실행 가능한 컨테이너 이미지로 변환하는 프로세스입니다. 이 프로세스는 전체 빌드 워크플로를 지정하는 BuildConfig 오브젝트로 정의됩니다. OpenShift Container Platform은 Kubernetes를 사용하여 빌드 이미지에서 컨테이너를 생성하고 이를 통합 컨테이너 레지스트리로 내보냅니다.

CSR(인증서 서명 요청)

리소스는 표시된 서명자가 인증서에 서명하도록 요청합니다. 이 요청은 승인되거나 거부될 수 있습니다.

Cluster Version Operator (CVO)

OpenShift Container Platform Update Service를 사용하여 현재 구성 요소 버전 및 그래프의 정보를 기반으로 유효한 업데이트 및 업데이트 경로를 확인하는 Operator입니다.

컴퓨팅 노드

클러스터 사용자에 대한 워크로드를 실행하는 노드입니다.

구성 드리프트

노드의 구성이 머신 구성에서 지정하는 것과 일치하지 않는 경우입니다.

container

컨테이너는 컴퓨팅 노드의 OCI 호환 환경에서 실행되는 경량의 이식 가능한 애플리케이션 인스턴스입니다. 각 컨테이너는 애플리케이션 및 해당 종속 항목이 포함된 바이너리 패키지인 OCI(Open Container Initiative) 호환 이미지의 런타임 인스턴스입니다.

단일 컴퓨팅 노드는 클라우드 인프라, 물리적 하드웨어 또는 가상화된 환경에서 사용 가능한 메모리 및 CPU 리소스에 따라 용량이 결정되어 여러 컨테이너를 호스팅할 수 있습니다.

컨테이너 오케스트레이션 엔진

컨테이너의 배포, 관리, 확장 및 네트워킹을 자동화하는 소프트웨어입니다.

컨테이너 워크로드

컨테이너에 패키지 및 배포되는 애플리케이션입니다.

컨트롤그룹(cgroups)

프로세스의 소비를 관리하고 제한하기 위해 프로세스의 파티션 세트를 그룹으로 분할합니다.

컨트롤 플레인

컨테이너의 라이프사이클을 정의, 배포, 관리하기 위해 API 및 인터페이스를 노출하는 컨테이너 오케스트레이션 계층입니다. 컨트롤 플레인은 컨트롤 플레인 시스템이라고도 합니다.

CRI-O

운영 체제와 통합되는 Kubernetes 네이티브 컨테이너 런타임 구현으로 효율적인 Kubernetes 환경을 제공합니다.

배포 및 배포 구성

OpenShift Container Platform은 애플리케이션 롤아웃 및 스케일링을 관리하기 위해 Kubernetes Deployment 오브젝트와 OpenShift Container Platform DeploymentConfig 오브젝트를 모두 지원합니다.

Deployment 오브젝트는 애플리케이션이 Pod로 배포되는 방법을 정의합니다. 레지스트리에서 가져올 컨테이너 이미지, 유지할 복제본 수, 컴퓨팅 노드에 스케줄링을 안내하는 레이블을 지정합니다.

Deployment는 지정된 수의 Pod가 실행 중인지 확인하는 ReplicaSet을 생성하고 관리합니다. 또한 Deployment 오브젝트는 애플리케이션 가용성을 유지하면서 Pod를 업데이트하는 다양한 롤아웃 전략을 지원합니다.

DeploymentConfig 오브젝트는 변경 트리거를 도입하여 배포 기능을 확장하므로 새 컨테이너 이미지 버전을 사용할 수 있게 되거나 기타 정의된 변경 사항이 발생할 때 새 배포 버전이 자동으로 생성됩니다. 이를 통해 OpenShift Container Platform 내에서 자동 롤아웃 관리가 가능합니다.

Dockerfile

터미널에서 이미지를 어셈블하기 위해 수행할 사용자 명령이 포함된 텍스트 파일입니다.

호스트 컨트롤 플레인

데이터 플레인 및 작업자의 OpenShift Container Platform 클러스터에서 컨트롤 플레인을 호스팅할 수 있는 OpenShift Container Platform 기능입니다. 이 모델은 다음 작업을 수행합니다.

컨트롤 플레인에 필요한 인프라 비용을 최적화합니다.

클러스터 생성 시간을 개선합니다.

Kubernetes 기본 상위 수준 프리미티브를 사용하여 컨트롤 플레인 호스팅을 활성화합니다. 예를 들어 배포 및 상태 저장 세트가 있습니다.

컨트롤 플레인과 워크로드 간 강력한 네트워크 분할을 허용합니다.

하이브리드 클라우드 배포

베어 메탈, 가상, 프라이빗 및 퍼블릭 클라우드 환경 전체에 일관된 플랫폼을 제공하는 배포. 이를 통해 속도, 민첩성 및 이식성을 제공합니다.

Ignition

초기 구성 중에 RHCOS가 디스크를 조작하는 데 사용하는 유틸리티입니다. 디스크 파티셔닝, 파티션 포맷, 파일 작성 및 사용자 구성을 포함한 일반적인 디스크 작업을 완료합니다.

설치 프로그램에서 제공하는 인프라

설치 프로그램은 클러스터가 실행되는 인프라를 배포하고 구성합니다.

kubelet

Pod에서 컨테이너가 실행 중인지 확인하기 위해 클러스터의 각 노드에서 실행되는 기본 노드 에이전트입니다.

Kubernetes

Kubernetes는 컨테이너화된 애플리케이션의 배포, 확장 및 관리를 자동화하기 위한 오픈 소스 컨테이너 오케스트레이션 엔진입니다.

Kubernetes 매니페스트

JSON 또는 YAML 형식의 Kubernetes API 오브젝트의 사양입니다. 구성 파일에는 배포, 구성 맵, 시크릿, 데몬 세트가 포함될 수 있습니다.

MCD(Machine Config Daemon)

노드에서 구성 드리프트가 있는지 정기적으로 확인하는 데몬입니다.

Machine Config Operator (MCO)

클러스터 머신에 새 구성을 적용하는 Operator입니다.

머신 구성 풀(MCP)

컨트롤 플레인 구성 요소 또는 사용자 워크로드와 같은 머신 그룹은 처리하는 리소스를 기반으로 합니다.

메타데이터

클러스터 배포 아티팩트에 대한 추가 정보입니다.

마이크로 서비스

소프트웨어 작성을 위한 접근 방식. 애플리케이션은 마이크로 서비스를 사용하여 서로 독립적으로 가장 작은 구성 요소로 분리할 수 있습니다.

미러 레지스트리

OpenShift Container Platform 이미지의 미러가 있는 레지스트리입니다.

모놀리식 애플리케이션

자체 포함, 빌드 및 패키지된 애플리케이션입니다.

네임스페이스

네임스페이스는 모든 프로세스에 표시되는 특정 시스템 리소스를 격리합니다. 네임스페이스 내에서 해당 네임스페이스의 멤버인 프로세스만 해당 리소스를 볼 수 있습니다.

네트워킹

OpenShift Container Platform 클러스터의 네트워크 정보입니다.

노드

OpenShift Container Platform 클러스터의 컴퓨팅 머신. 노드는 VM(가상 머신) 또는 물리적 머신입니다.

```shell
oc
```

터미널에서 OpenShift Container Platform 명령을 실행하는 명령줄 도구입니다.

OpenShift Dedicated

AWS(Amazon Web Services) 및 Google Cloud에서 관리형 RHEL OpenShift Container Platform. OpenShift Dedicated는 애플리케이션 빌드 및 확장에 중점을 둡니다.

OSUS(OpenShift Update Service)

인터넷에 액세스할 수 있는 클러스터의 경우 RHEL(Red Hat Enterprise Linux)은 공용 API 뒤에 있는 호스팅 서비스로 OpenShift 업데이트 서비스를 사용하여 무선 업데이트를 제공합니다.

OpenShift 이미지 레지스트리

이미지를 관리하기 위해 OpenShift Container Platform에서 제공하는 레지스트리입니다.

Operator

OpenShift Container Platform 클러스터에서 Kubernetes 애플리케이션을 패키징, 배포 및 관리하는 기본 방법입니다. Operator는 운영 지식을 패키지화하고 고객과 공유하는 소프트웨어로 변환하도록 설계된 Kubernetes 네이티브 애플리케이션입니다.

일반적으로 설치, 구성, 확장, 업데이트 및 장애 조치와 같은 작업은 Ansible과 같은 스크립트 또는 자동화 툴을 사용하여 관리자가 수동으로 관리했습니다. Operator는 이러한 기능을 Kubernetes로 가져와 기본적으로 클러스터 내에서 통합 및 자동화합니다.

Operator는 설치 및 구성과 같은 Day 1 작업 및 스케일링, 업데이트, 백업, 페일오버 및 복원과 같은 Day 2 작업을 모두 관리합니다. Operator는 Kubernetes API 및 개념을 활용하여 복잡한 애플리케이션을 관리하는 자동화된 일관된 방법을 제공합니다.

OperatorHub

설치할 다양한 OpenShift Container Platform Operator가 포함된 플랫폼입니다.

OLM(Operator Lifecycle Manager)

OLM은 Kubernetes 네이티브 애플리케이션의 라이프사이클을 설치, 업데이트 및 관리할 수 있도록 지원합니다. OLM은 효과적이고 자동화되고 확장 가능한 방식으로 Operator를 관리하도록 설계된 오픈 소스 툴킷입니다.

ostree

전체 파일 시스템 트리 트리의 원자 업그레이드를 수행하는 Linux 기반 운영 체제의 업그레이드 시스템입니다. ostree는 주소 지정 가능 오브젝트 저장소를 사용하여 파일 시스템 트리에 대한 의미 있는 변경을 추적하고 기존 패키지 관리 시스템을 보완하도록 설계되었습니다.

OTA(Over-the-Air) 업데이트

OSUS(OpenShift Container Platform Update Service)는 RHCOS(Red Hat Enterprise Linux CoreOS)를 포함하여 OpenShift Container Platform에 대한 무선 업데이트를 제공합니다.

Pod

Pod는 하나의 호스트에 함께 배포되는 하나 이상의 컨테이너입니다. 볼륨 및 IP 주소와 같은 공유 리소스가 있는 배치된 컨테이너 그룹으로 구성됩니다.

Pod는 정의, 배포 및 관리되는 최소 컴퓨팅 단위이기도 합니다. OpenShift Container Platform에서 Pod는 개별 애플리케이션 컨테이너를 배포 가능한 가장 작은 단위로 교체합니다.

Pod는 OpenShift Container Platform의 오케스트레이션된 단위입니다. OpenShift Container Platform은 동일한 노드의 Pod에 있는 모든 컨테이너를 예약하고 실행합니다.

복잡한 애플리케이션은 각각 자체 컨테이너가 있는 여러 Pod로 구성됩니다. 외부적으로 상호 작용하고 OpenShift Container Platform 환경 내부와도 상호 작용합니다.

프라이빗 레지스트리

OpenShift Container Platform은 컨테이너 이미지 레지스트리 API를 구현하는 모든 서버를 이미지 소스로 사용할 수 있으므로 개발자가 개인 컨테이너 이미지를 푸시하고 가져올 수 있습니다.

project

OpenShift Container Platform에서는 프로젝트를 사용하여 사용자 또는 개발자 그룹이 함께 작업할 수 있습니다. 프로젝트는 리소스 범위를 정의하고 사용자 액세스를 관리하며 리소스 할당량 및 제한을 적용합니다.

프로젝트는 역할 기반 액세스 제어(RBAC) 및 관리 기능을 제공하는 추가 주석이 있는 Kubernetes 네임스페이스입니다. 리소스를 구성하여 서로 다른 사용자 그룹 간의 격리를 보장하는 중앙 메커니즘 역할을 합니다.

퍼블릭 레지스트리

OpenShift Container Platform은 컨테이너 이미지 레지스트리 API를 구현하는 모든 서버를 이미지의 소스로 사용하여 개발자가 공용 컨테이너 이미지를 푸시하고 가져올 수 있습니다.

RHEL OpenShift Container Platform Cluster Manager

OpenShift Container Platform 클러스터를 설치, 수정, 운영 및 업그레이드할 수 있는 관리형 서비스입니다.

RHEL Quay 컨테이너 레지스트리

대부분의 컨테이너 이미지 및 Operator를 OpenShift Container Platform 클러스터에 제공하는 Quay.io 컨테이너 레지스트리입니다.

복제 컨트롤러

한 번에 실행하는 데 필요한 Pod 복제본 수를 나타내는 자산입니다.

ReplicaSet 및 ReplicationController

Kubernetes `ReplicaSet` 및 `ReplicationController` 오브젝트를 사용하면 항상 원하는 수의 Pod 복제본이 실행됩니다. Pod가 실패, 종료 또는 삭제되면 이러한 컨트롤러는 지정된 복제본 수를 유지하기 위해 새 Pod를 자동으로 생성합니다.

반대로 필요한 것보다 많은 Pod가 있는 경우 ReplicaSet 또는 ReplicationController는 정의된 복제본 수와 일치하도록 초과 Pod를 종료하여 축소합니다.

RBAC(역할 기반 액세스 제어)

클러스터 사용자와 워크로드가 역할을 실행하는 데 필요한 리소스에만 액세스할 수 있도록 하는 주요 보안 제어입니다.

라우트

경로는 www.example.com과 같이 외부에 연결할 수 있는 호스트 이름을 지정하여 서비스를 노출하는 방법입니다. 각 경로는 경로 이름, 서비스 선택기, 선택적으로 보안 구성으로 구성됩니다.

라우터

라우터는 정의된 경로 및 관련 서비스 엔드포인트를 처리하여 외부 클라이언트가 애플리케이션에 액세스할 수 있도록 합니다. OpenShift Container Platform에 다중 계층 애플리케이션을 배포하는 것은 간단하지만 외부 트래픽은 라우팅 계층 없이 애플리케이션에 연결할 수 없습니다.

스케일링

리소스 용량이 증가하거나 감소합니다.

서비스

OpenShift Container Platform의 서비스는 논리적 Pod 세트와 해당 Pod에 도달하기 위한 액세스 정책을 정의합니다. 안정적인 내부 IP 주소와 호스트 이름을 제공하여 포드를 생성하고 삭제할 때 애플리케이션 구성 요소 간에 원활한 통신을 보장합니다.

S2I(Source-to-Image) 이미지

애플리케이션을 배포하기 위해 OpenShift Container Platform의 애플리케이션 소스 코드의 프로그래밍 언어를 기반으로 생성된 이미지입니다.

스토리지

OpenShift Container Platform은 온프레미스 및 클라우드 공급자를 위해 다양한 유형의 스토리지를 지원합니다. OpenShift Container Platform 클러스터에서 영구 및 비영구 데이터에 대한 컨테이너 스토리지를 관리할 수 있습니다.

telemetry

OpenShift Container Platform의 크기, 상태 및 상태와 같은 정보를 수집하는 구성 요소입니다.

템플릿

템플릿은 오브젝트 세트를 설명합니다. 이러한 오브젝트를 매개변수화하고 처리하여 OpenShift Container Platform에서 생성할 오브젝트 목록을 만들 수 있습니다.

사용자 프로비저닝 인프라

사용자가 제공하는 인프라에 OpenShift Container Platform을 설치할 수 있습니다. 설치 프로그램을 사용하여 클러스터 인프라를 프로비저닝하고 클러스터 인프라를 생성한 다음 제공한 인프라에 클러스터를 배포하는 데 필요한 자산을 생성할 수 있습니다.

웹 콘솔

OpenShift Container Platform을 관리할 UI(사용자 인터페이스)입니다.

## 7장. About OpenShift Kubernetes Engine

2020년 4월 27일 현재 Red Hat은 Red Hat OpenShift Container Engine의 이름을 Red Hat OpenShift Kubernetes Engine으로 교체하여 제품이 제공하는 가치를 보다 효과적으로 전달할 수 있도록 했습니다.

Red Hat OpenShift Kubernetes Engine은 컨테이너를 시작하기 위한 프로덕션 플랫폼으로 엔터프라이즈급 Kubernetes 플랫폼을 사용할 수 있는 Red Hat의 제품입니다.

OpenShift Container Platform과 동일한 방식으로 OpenShift Kubernetes Engine을 다운로드하여 설치할 수 있지만 OpenShift Kubernetes Engine은 OpenShift Container Platform에서 제공하는 기능의 하위 집합을 제공합니다.

### 7.1. 유사점 및 차이점

다음 표에서 OpenShift Kubernetes Engine과 OpenShift Container Platform의 유사점과 차이점을 확인할 수 있습니다.

| OpenShift Kubernetes Engine | OpenShift Container Platform |
| --- | --- |
| 완전히 자동화된 설치 프로그램 | 제공됨 | 제공됨 |
| Air Smart Upgrades를 통해 | 제공됨 | 제공됨 |
| Enterprise Secured Kubernetes | 제공됨 | 제공됨 |
| kubectl 및 oc 자동화된 명령줄 | 제공됨 | 제공됨 |
| OLM(Operator Lifecycle Manager) | 제공됨 | 제공됨 |
| 관리자 웹 콘솔 | 제공됨 | 제공됨 |
| OpenShift Virtualization | 제공됨 | 제공됨 |
| 사용자 워크로드 모니터링 |  | 제공됨 |
| 클러스터 모니터링 | 제공됨 | 제공됨 |
| Cost Management SaaS Service | 제공됨 | 제공됨 |
| 플랫폼 로깅 |  | 제공됨 |
| 개발자 웹 콘솔 |  | 제공됨 |
| 개발자 애플리케이션 카탈로그 |  | 제공됨 |
| Source to Image and Builder Automation (Tekton) |  | 제공됨 |
| OpenShift Service Mesh(Maistra 및 Kiali) |  | 제공됨 |
| 분산 추적 플랫폼 |  | 제공됨 |
| OpenShift Serverless(Knative) |  | 제공됨 |
| OpenShift Pipelines(Jenkins 및 Tekton) |  | 제공됨 |
| IBM Cloud® Pak 및 RHT MW Bundles의 임베디드 구성 요소 |  | 제공됨 |
| OpenShift 샌드박스 컨테이너 |  | 제공됨 |

#### 7.1.1. 코어 Kubernetes 및 컨테이너 오케스트레이션

OpenShift Kubernetes Engine은 설치가 쉽고 데이터 센터에서 사용할 수 있는 많은 소프트웨어 요소가 있는 광범위한 호환성 테스트 매트릭스를 제공하는 엔터프라이즈급 Kubernetes 환경에 대한 전체 액세스 권한을 제공합니다.

OpenShift Kubernetes Engine은 OpenShift Container Platform과 동일한 서비스 수준 계약, 버그 수정 및 일반적인 취약점 및 오류 보호를 제공합니다.

OpenShift Kubernetes Engine에는 동일한 기술 공급자의 컨테이너 런타임과 통합 Linux 운영 체제를 사용할 수 있는 RHEL(Red Hat Enterprise Linux) 가상 데이터센터 및 RHCOS(Red Hat Enterprise Linux CoreOS) 인타이틀먼트가 포함되어 있습니다.

OpenShift Kubernetes Engine 서브스크립션은 Red Hat OpenShift support for Windows Containers 서브스크립션과 호환됩니다.

#### 7.1.2. 엔터프라이즈급 구성

OpenShift Kubernetes Engine은 OpenShift Container Platform과 동일한 보안 옵션 및 기본 설정을 사용합니다.

기본 보안 컨텍스트 제약 조건, Pod 보안 정책, 모범 사례 네트워크 및 스토리지 설정, 서비스 계정 구성, SELinux 통합, HAproxy 에지 라우팅 구성 및 OpenShift Container Platform에서 제공하는 기타 모든 표준 보호 기능을 OpenShift Kubernetes Engine에서 사용할 수 있습니다.

OpenShift Kubernetes Engine은 Prometheus를 기반으로 하는 OpenShift Container Platform에서 사용하는 통합 모니터링 솔루션에 대한 전체 액세스 권한을 제공하며 일반적인 Kubernetes 문제에 대한 심층적인 적용 범위 및 경고를 제공합니다.

OpenShift Kubernetes Engine은 OpenShift Container Platform과 동일한 설치 및 업그레이드 자동화를 사용합니다.

#### 7.1.3. 표준 인프라 서비스

OpenShift Kubernetes Engine 서브스크립션을 사용하면 OpenShift Container Platform에서 지원하는 모든 스토리지 플러그인에 대한 지원이 제공됩니다.

네트워킹 측면에서 OpenShift Kubernetes Engine은 Kubernetes CNI(Container Network Interface)에 대한 완전하고 지원되는 액세스를 제공하므로 OpenShift Container Platform을 지원하는 타사 SDN을 사용할 수 있습니다.

또한 포함된 Open vSwitch 소프트웨어 정의 네트워크를 최대한 활용할 수 있습니다. OpenShift Kubernetes Engine을 사용하면 OpenShift Container Platform에서 지원되는 OVN Kubernetes 오버레이, Multus 및 Multus 플러그인을 최대한 활용할 수 있습니다.

OpenShift Kubernetes Engine을 사용하면 고객은 Kubernetes 네트워크 정책을 사용하여 클러스터에 배포된 애플리케이션 서비스 간에 마이크로 세분화를 생성할 수 있습니다.

HAproxy 에지 라우팅 계층과의 정교한 통합을 포함하여 OpenShift Container Platform에 있는 `Route` API 오브젝트를 즉시 Kubernetes Ingress 컨트롤러로 사용할 수도 있습니다.

#### 7.1.4. 핵심 사용자 경험

OpenShift Kubernetes Engine 사용자는 Kubernetes Operator, Pod 배포 전략, Helm 및 OpenShift Container Platform 템플릿에 대한 전체 액세스 권한이 있습니다.

OpenShift Kubernetes Engine 사용자는 및 아래 명령줄 인터페이스를 모두 사용할 수 있습니다. OpenShift Kubernetes Engine은 배포된 컨테이너 서비스의 모든 측면을 보여주고 서비스 환경을 제공하는 관리자 웹 기반 콘솔도 제공합니다.

```shell
oc
```

```shell
kubectl
```

OpenShift Kubernetes Engine은 사용하는 클러스터 및 라이프 사이클 Operator 지원 서비스의 콘텐츠에 대한 액세스를 제어하는 데 도움이 되는 Operator 라이프 사이클 관리자에 대한 액세스 권한을 부여합니다.

OpenShift Kubernetes Engine 서브스크립션을 사용하면 Kubernetes 네임스페이스, OpenShift `Project` API 오브젝트, 클러스터 수준 Prometheus 모니터링 지표 및 이벤트에 액세스할 수 있습니다.

#### 7.1.5. 유지 관리 및 큐레이션된 콘텐츠

OpenShift Kubernetes Engine 서브스크립션을 사용하면 Red Hat Ecosystem Catalog 및 Red Hat Connect ISV 마켓플레이스에서 OpenShift Container Platform 콘텐츠에 액세스할 수 있습니다.

OpenShift Container Platform eco-system에서 제공하는 모든 유지 관리 및 큐레이션된 콘텐츠에 액세스할 수 있습니다.

#### 7.1.6. OpenShift Data Foundation 호환 가능

OpenShift Kubernetes Engine은 OpenShift Data Foundation 구매와 호환 및 지원됩니다.

#### 7.1.7. Red Hat Middleware 호환 가능

OpenShift Kubernetes Engine은 개별 Red Hat Middleware 제품 솔루션과 호환 및 지원됩니다. OpenShift가 포함된 Red Hat Middleware 번들에는 OpenShift Container Platform만 포함됩니다.

#### 7.1.8. OpenShift Serverless

OpenShift Kubernetes Engine에는 OpenShift Serverless 지원이 포함되어 있지 않습니다. 이러한 지원을 위해 OpenShift Container Platform을 사용하십시오.

#### 7.1.9. Quay 통합 호환 가능

OpenShift Kubernetes Engine은 Red Hat Quay 구매와 호환 및 지원됩니다.

#### 7.1.10. OpenShift Virtualization

OpenShift Kubernetes Engine에는 kubevirt.io 오픈 소스 프로젝트에서 파생된 Red Hat 제품 제품에 대한 지원이 포함되어 있습니다.

#### 7.1.11. 고급 클러스터 관리

OpenShift Kubernetes Engine은 Kubernetes용 RHACM(Red Hat Advanced Cluster Management) 추가 구매와 호환됩니다. OpenShift Kubernetes Engine 서브스크립션은 클러스터 전체 로그 집계 솔루션을 제공하거나 Fluentd 또는 Kibana 기반 로깅 솔루션을 지원하지 않습니다.

OpenShift Container Platform의 컨테이너화된 서비스에 대한 OpenTracing 관찰 기능을 제공하는 오픈 소스 istio.io 및 kiali.io 프로젝트에서 파생된 Red Hat OpenShift Service Mesh 기능은 OpenShift Kubernetes Engine에서 지원되지 않습니다.

#### 7.1.12. 고급 네트워킹

OpenShift Container Platform의 표준 네트워킹 솔루션은 OpenShift Kubernetes Engine 서브스크립션에서 지원됩니다.

OpenShift Container Platform Kubernetes CNI 플러그인은 OpenShift Kubernetes Engine과 함께 사용할 수 있는 OpenShift Container Platform 프로젝트 간 다중 테넌트 네트워크 분할을 자동화할 수 있습니다.

OpenShift Kubernetes Engine은 클러스터의 애플리케이션 서비스에서 사용하는 소스 IP 주소에 대한 모든 세분화된 제어를 제공합니다. 이러한 송신 IP 주소 제어는 OpenShift Kubernetes Engine에서 사용할 수 있습니다.

OpenShift Container Platform은 OpenShift Container Platform에 있는 VIP Pod를 통해 퍼블릭 클라우드 공급자를 사용하지 않는 경우 비표준 포트를 사용하는 클러스터 서비스에서 수신 라우팅을 제공합니다. 해당 수신 솔루션은 OpenShift Kubernetes Engine에서 지원됩니다.

OpenShift Kubernetes Engine 사용자는 퍼블릭 클라우드 공급자와의 통합을 제공하는 Kubernetes 수신 제어 오브젝트에 대해 지원됩니다. istio.io 오픈 소스 프로젝트에서 파생되는 Red Hat Service Mesh는 OpenShift Kubernetes Engine에서 지원되지 않습니다.

또한 OpenShift Serverless에 있는 Kourier Ingress 컨트롤러는 OpenShift Kubernetes Engine에서 지원되지 않습니다.

#### 7.1.13. OpenShift 샌드박스 컨테이너

OpenShift Kubernetes Engine에는 OpenShift 샌드박스 컨테이너가 포함되어 있지 않습니다. 이러한 지원을 위해 OpenShift Container Platform을 사용하십시오.

#### 7.1.14. 개발자 경험

OpenShift Kubernetes Engine에서는 다음 기능이 지원되지 않습니다.

OpenShift Container Platform 개발자 경험 유틸리티 및 Red Hat OpenShift Dev Spaces와 같은 툴.

사용자의 프로젝트 공간에 간소화된 Kubernetes 지원 Jenkins 및 Tekton 환경을 통합하는 OpenShift Container Platform 파이프라인 기능입니다.

OpenShift Container Platform source-to-image 기능을 사용하면 클러스터 전체에서 소스 코드, dockerfiles 또는 컨테이너 이미지를 쉽게 배포할 수 있습니다.

최종 사용자 컨테이너 배포를 위한 빌드 전략, 빌더 Pod 또는 Tekton입니다.

`odo` 개발자 명령줄입니다.

OpenShift Container Platform 웹 콘솔의 개발자 가상 사용자입니다.

#### 7.1.15. 기능 요약

다음 표는 OpenShift Kubernetes Engine 및 OpenShift Container Platform의 기능 가용성에 대한 요약입니다. 해당하는 경우 기능을 활성화하는 Operator의 이름이 포함됩니다.

| 기능 | OpenShift Kubernetes Engine | OpenShift Container Platform | Operator 이름 |
| --- | --- | --- | --- |
| 완전 자동화된 설치 프로그램(IPI) | 포함됨 | 포함됨 | 해당 없음 |
| 사용자 지정할 수 있는 설치 프로그램 (UPI) | 포함됨 | 포함됨 | 해당 없음 |
| 연결이 끊긴 설치 | 포함됨 | 포함됨 | 해당 없음 |
| RHEL(Red Hat Enterprise Linux) 또는 RHCOS(Red Hat Enterprise Linux CoreOS) 인타이틀먼트 | 포함됨 | 포함됨 | 해당 없음 |
| 기존 RHEL 수동으로 클러스터(BYO)에 연결 | 포함됨 | 포함됨 | 해당 없음 |
| CRIO 런타임 | 포함됨 | 포함됨 | 해당 없음 |
| Air Smart Upgrades and Operating System (RHCOS) Management를 통해 | 포함됨 | 포함됨 | 해당 없음 |
| Enterprise Secured Kubernetes | 포함됨 | 포함됨 | 해당 없음 |
| kubectl 및 `oc` 자동화된 명령줄 | 포함됨 | 포함됨 | 해당 없음 |
| 인증 통합, RBAC, SCC, Multi-Tenancy Admission Controller | 포함됨 | 포함됨 | 해당 없음 |
| OLM(Operator Lifecycle Manager) | 포함됨 | 포함됨 | 해당 없음 |
| 관리자 웹 콘솔 | 포함됨 | 포함됨 | 해당 없음 |
| OpenShift Virtualization | 포함됨 | 포함됨 | OpenShift Virtualization Operator |
| Red Hat에서 제공하는 Compliance Operator | 포함됨 | 포함됨 | Compliance Operator |
| File Integrity Operator | 포함됨 | 포함됨 | File Integrity Operator |
| Gatekeeper Operator | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Gatekeeper Operator |
| Klusterlet | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | 해당 없음 |
| Red Hat에서 제공하는 kube Descheduler Operator | 포함됨 | 포함됨 | kube Descheduler Operator |
| Red Hat에서 제공하는 로컬 스토리지 | 포함됨 | 포함됨 | Local Storage Operator |
| Red Hat에서 제공하는 Node Feature Discovery | 포함됨 | 포함됨 | Node Feature Discovery Operator |
| 성능 프로필 컨트롤러 | 포함됨 | 포함됨 | 해당 없음 |
| Red Hat에서 제공하는 PTP Operator | 포함됨 | 포함됨 | PTP Operator |
| Red Hat에서 제공하는 Service Telemetry Operator | 포함되지 않음 | 포함됨 | Service Telemetry Operator |
| SR-IOV 네트워크 Operator | 포함됨 | 포함됨 | SR-IOV 네트워크 Operator |
| Vertical Pod Autoscaler | 포함됨 | 포함됨 | Vertical Pod Autoscaler |
| 클러스터 모니터링(Prometheus) | 포함됨 | 포함됨 | 클러스터 모니터링 |
| 장치 관리자(예: GPU) | 포함됨 | 포함됨 | 해당 없음 |
| 로그 전달 | 포함됨 | 포함됨 | Red Hat OpenShift Logging Operator |
| Telemeter 및 Insights Connected Experience | 포함됨 | 포함됨 | 해당 없음 |
| 기능 | OpenShift Kubernetes Engine | OpenShift Container Platform | Operator 이름 |
| OpenShift Cloud Manager SaaS Service | 포함됨 | 포함됨 | 해당 없음 |
| OVS 및 OVN SDN | 포함됨 | 포함됨 | 해당 없음 |
| MetalLB | 포함됨 | 포함됨 | MetalLB Operator |
| HAProxy Ingress 컨트롤러 | 포함됨 | 포함됨 | 해당 없음 |
| Ingress 클러스터 전체 방화벽 | 포함됨 | 포함됨 | 해당 없음 |
| 송신 Pod 및 네임스페이스 Granular Control | 포함됨 | 포함됨 | 해당 없음 |
| Ingress 비 표준 포트 | 포함됨 | 포함됨 | 해당 없음 |
| Multus 및 사용 가능한 Multus 플러그인 | 포함됨 | 포함됨 | 해당 없음 |
| 네트워크 정책 | 포함됨 | 포함됨 | 해당 없음 |
| IPv6 단일 및 듀얼 스택 | 포함됨 | 포함됨 | 해당 없음 |
| CNI 플러그인 ISV 호환성 | 포함됨 | 포함됨 | 해당 없음 |
| CSI 플러그인 ISV 호환성 | 포함됨 | 포함됨 | 해당 없음 |
| RHT 및 IBM® 미들웨어 (OpenShift Container Platform 또는 OpenShift Kubernetes Engine에 포함되지 않음) | 포함됨 | 포함됨 | 해당 없음 |
| ISV 또는 파트너 Operator 및 컨테이너 호환성 (OpenShift Container Platform 또는 OpenShift Kubernetes Engine에는 포함되지 않음) | 포함됨 | 포함됨 | 해당 없음 |
| 임베디드 소프트웨어 카탈로그 | 포함됨 | 포함됨 | 해당 없음 |
| 임베디드 Marketplace | 포함됨 | 포함됨 | 해당 없음 |
| Quay 호환성(포함되지 않음) | 포함됨 | 포함됨 | 해당 없음 |
| OADP(OpenShift API for Data Protection) | 포함됨 | 포함됨 | OADP Operator |
| RHEL Software Collections 및 RHT SSO 공통 서비스(포함) | 포함됨 | 포함됨 | 해당 없음 |
| 포함된 레지스트리 | 포함됨 | 포함됨 | 해당 없음 |
| Helm | 포함됨 | 포함됨 | 해당 없음 |
| 사용자 워크로드 모니터링 | 포함되지 않음 | 포함됨 | 해당 없음 |
| Cost Management SaaS Service | 포함됨 | 포함됨 | Cost Management Metrics Operator |
| 플랫폼 로깅 | 포함되지 않음 | 포함됨 | Red Hat OpenShift Logging Operator |
| 개발자 웹 콘솔 | 포함되지 않음 | 포함됨 | 해당 없음 |
| 개발자 애플리케이션 카탈로그 | 포함되지 않음 | 포함됨 | 해당 없음 |
| Source to Image and Builder Automation (Tekton) | 포함되지 않음 | 포함됨 | 해당 없음 |
| OpenShift Service Mesh | 포함되지 않음 | 포함됨 | OpenShift Service Mesh Operator |
| 기능 | OpenShift Kubernetes Engine | OpenShift Container Platform | Operator 이름 |
| Red Hat OpenShift Serverless | 포함되지 않음 | 포함됨 | OpenShift Serverless Operator |
| Red Hat에서 제공하는 웹 터미널 | 포함되지 않음 | 포함됨 | Web Terminal Operator |
| Red Hat OpenShift Pipelines Operator | 포함되지 않음 | 포함됨 | OpenShift Pipelines Operator |
| IBM Cloud® Pak 및 RHT MW Bundles의 임베디드 구성 요소 | 포함되지 않음 | 포함됨 | 해당 없음 |
| Red Hat OpenShift GitOps | 포함되지 않음 | 포함됨 | OpenShift GitOps |
| Red Hat OpenShift Dev Spaces | 포함되지 않음 | 포함됨 | Red Hat OpenShift Dev Spaces |
| Red Hat OpenShift Local | 포함되지 않음 | 포함됨 | 해당 없음 |
| Red Hat에서 제공하는 Quay Bridge Operator | 포함되지 않음 | 포함됨 | Quay Bridge Operator |
| Red Hat에서 제공하는 Quay 컨테이너 보안 | 포함되지 않음 | 포함됨 | Quay Operator |
| Red Hat OpenShift 분산 추적 platform | 포함되지 않음 | 포함됨 | Red Hat OpenShift distributed tracing Platform Operator |
| Red Hat OpenShift Kiali | 포함되지 않음 | 포함됨 | Kiali Operator |
| Red Hat에서 제공하는 미터링 (더 이상 사용되지 않음) | 포함되지 않음 | 포함됨 | 해당 없음 |
| Migration Toolkit for Containers Operator | 포함되지 않음 | 포함됨 | Migration Toolkit for Containers Operator |
| OpenShift의 비용 관리 | 포함되지 않음 | 포함됨 | 해당 없음 |
| Red Hat에서 제공하는 JBoss Web Server | 포함되지 않음 | 포함됨 | JWS Operator |
| Red Hat Build of Quarkus | 포함되지 않음 | 포함됨 | 해당 없음 |
| Kourier Ingress 컨트롤러 | 포함되지 않음 | 포함됨 | 해당 없음 |
| RHT Middleware 번들 하위 호환성 (OpenShift Container Platform에 포함되지 않음) | 포함되지 않음 | 포함됨 | 해당 없음 |
| IBM Cloud® Pak 하위 호환성 (OpenShift Container Platform에 포함되지 않음) | 포함되지 않음 | 포함됨 | 해당 없음 |
| OpenShift Do ( `odo` ) | 포함되지 않음 | 포함됨 | 해당 없음 |
| 이미지 및 Tekton 빌더로 소스 | 포함되지 않음 | 포함됨 | 해당 없음 |
| OpenShift Serverless FaaS | 포함되지 않음 | 포함됨 | 해당 없음 |
| IDE 통합 | 포함되지 않음 | 포함됨 | 해당 없음 |
| OpenShift 샌드박스 컨테이너 | 포함되지 않음 | 포함되지 않음 | OpenShift 샌드박스 컨테이너 Operator |
| Windows Machine Config Operator | 커뮤니티 Windows Machine Config Operator 포함 - 서브스크립션이 필요하지 않음 | Red Hat Windows Machine Config Operator 포함 - 별도의 서브스크립션 필요 | Windows Machine Config Operator |
| Red Hat Quay | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Quay Operator |
| Red Hat Advanced Cluster Management | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Kubernetes용 고급 클러스터 관리 |
| Red Hat Advanced Cluster Security | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | 해당 없음 |
| OpenShift Data Foundation | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | OpenShift Data Foundation |
| 기능 | OpenShift Kubernetes Engine | OpenShift Container Platform | Operator 이름 |
| Ansible Automation Platform Resource Operator | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Ansible Automation Platform Resource Operator |
| Red Hat에서 제공하는 비즈니스 자동화 | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Business Automation Operator |
| Red Hat에서 제공하는 Data Grid | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Data Grid Operator |
| Red Hat에서 제공하는 Red Hat Integration | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Red Hat Integration Operator |
| Red Hat Integration - Red Hat에서 제공하는 3Scale | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | 3scale |
| Red Hat Integration - Red Hat에서 제공하는 3Scale APICast 게이트웨이 | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | 3scale APIcast |
| Red Hat Integration - AMQ Broker | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | AMQ Broker |
| Red Hat Integration - AMQ Broker LTS | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 |  |
| Red Hat Integration - AMQ Interconnect | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | AMQ Interconnect |
| Red Hat Integration - AMQ Online | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 |  |
| Red Hat Integration - AMQ Streams | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | AMQ Streams |
| Red Hat Integration - Camel K | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Camel K |
| Red Hat Integration - Fuse Console | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Fuse 콘솔 |
| Red Hat Integration - Fuse Online | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Fuse Online |
| Red Hat Integration - Service Registry Operator | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | 서비스 레지스트리 |
| Red Hat에서 제공하는 API Cryostat | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | API Cryostat |
| Red Hat에서 제공하는 JBoss EAP | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | JBoss EAP |
| Smart Gateway Operator | 포함되지 않음 - 별도의 서브스크립션 필요 | 포함되지 않음 - 별도의 서브스크립션 필요 | Smart Gateway Operator |
| Kubernetes NMState Operator | 포함됨 | 포함됨 | 해당 없음 |

### 7.2. 서브스크립션 제한 사항

OpenShift Kubernetes Engine은 OpenShift Container Platform에 지원되는 제한된 기능 세트를 저렴한 가격으로 제공하는 서브스크립션 서비스입니다. OpenShift Kubernetes Engine 및 OpenShift Container Platform은 동일한 제품이므로 모든 소프트웨어와 기능이 모두 제공됩니다.

OpenShift Container Platform은 하나의 다운로드만 있습니다. OpenShift Kubernetes Engine은 이러한 이유로 OpenShift Container Platform 문서 및 지원 서비스 및 버그 에라타를 사용합니다.

## 8장. OpenShift Container Platform 문서에 대한 피드백 제공

오류를 보고하거나 문서를 개선하기 위해 Red Hat Jira 계정에 로그인하여 문제를 제출하십시오. Red Hat Jira 계정이 없는 경우 계정을 생성하라는 메시지가 표시됩니다.

프로세스

다음 링크 중 하나를 클릭합니다.

OpenShift Container Platform에 대한 Jira 문제를 생성하려면 다음을 수행합니다.

OpenShift Virtualization에 대한 Jira 문제를 생성하려면 다음을 수행합니다.

요약 에 문제에 대한 간략한 설명을 입력합니다.

설명 에 문제점이나 개선 사항에 대한 자세한 설명을 제공하세요. 문서에서 문제가 발생한 위치에 URL을 포함합니다.

생성 을 클릭하여 문제를 생성합니다.
