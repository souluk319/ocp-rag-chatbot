# 보안 및 컴플라이언스

## OpenShift Container Platform의 보안 학습 및 관리

이 문서에서는 컨테이너 보안, 인증서 구성 및 암호화를 사용하여 클러스터를 보호하는 방법을 설명합니다.

### 1.1. 보안 개요

OpenShift Container Platform 클러스터의 다양한 측면을 적절하게 보호하는 방법을 이해하는 것이 중요합니다.

#### 1.1.1. 컨테이너 보안

OpenShift Container Platform 보안을 이해하기 위한 좋은 시작점은 컨테이너 보안 이해 의 개념을 검토하는 것입니다. 이 섹션에서는 호스트 계층, 컨테이너 및 오케스트레이션 계층, 빌드 및 애플리케이션 계층에 대한 솔루션을 포함하여 OpenShift Container Platform에서 사용할 수 있는 컨테이너 보안 조치의 수준 높은 검토 단계를 제공합니다. 이 섹션에는 다음 주제에 대한 정보도 포함되어 있습니다.

컨테이너 보안이 중요한 이유 및 기존 보안 표준과의 비교

호스트(RHCOS 및 RHEL) 계층에서 제공하는 컨테이너 보안 조치와 OpenShift Container Platform에서 제공하는 컨테이너 보안 조치

컨테이너 콘텐츠 및 취약점의 소스를 평가하는 방법

컨테이너 콘텐츠를 사전 예방식으로 확인하기 위해 빌드 및 배포 프로세스를 디자인하는 방법

인증 및 권한 부여를 통해 컨테이너에 대한 액세스를 제어하는 방법

OpenShift Container Platform에서 네트워킹 및 연결된 스토리지를 보호하는 방법

API 관리 및 SSO에 사용하는 컨테이너화된 솔루션

#### 1.1.2. 감사

OpenShift Container Platform 감사에서는 시스템의 개별 사용자, 관리자 또는 기타 구성 요소가 시스템에 영향을 준 활동 시퀀스를 설명하는 보안 관련 레코드 집합을 제공합니다. 관리자는 감사 로그 정책을 구성하고 감사 로그

를 볼 수 있습니다.

#### 1.1.3. 인증서

인증서는 다양한 구성 요소에서 클러스터에 대한 액세스 권한을 검증하는 데 사용됩니다. 관리자는 기본 수신 인증서를 교체 하거나 API 서버 인증서를 추가하거나

서비스 인증서를 추가할 수 있습니다.

클러스터에서 사용하는 인증서 유형에 대한 세부 정보를 검토할 수도 있습니다.

API 서버의 사용자 제공 인증서

프록시 인증서

서비스 CA 인증서

노드 인증서

부트스트랩 인증서

etcd 인증서

OLM 인증서

집계된 API 클라이언트 인증서

Machine Config Operator 인증서

기본 수신을 위한 사용자 제공 인증서

수신 인증서

모니터링 및 클러스터 로깅 Operator 구성요소 인증서

컨트롤 플레인 인증서

#### 1.1.4. 데이터 암호화

클러스터에 etcd 암호화를 활성화하여 추가 데이터 보안 계층을 제공할 수 있습니다. 예를 들어 etcd 백업이 잘못된 당사자에게 노출되는 경우 중요한 데이터의 손실을 방지할 수 있습니다.

#### 1.1.5. 취약점 검사

관리자는 Red Hat Quay Container Security Operator를 사용하여 취약점 검사를 실행하고 탐지된 취약점 에 대한 정보를 검토할 수 있습니다.

### 1.2. 컴플라이언스 개요

많은 OpenShift Container Platform 고객은 시스템을 프로덕션 환경에 도입하기 전에 일정 수준의 규제 준비 또는 컴플라이언스를 갖춰야 합니다. 이러한 규제 준비는 국가 표준, 산업 표준 또는 조직의 기업 거버넌스 프레임워크에 의해 부과될 수 있습니다.

#### 1.2.1. 컴플라이언스 확인

관리자는 Compliance Operator 를 사용하여 규정 준수 검사를 실행하고 발견된 문제에 대한 수정을 권장할 수 있습니다. 플러그인 은 Compliance Operator와 쉽게 상호 작용할 수 있는 유틸리티 세트를 제공하는 OpenShift CLI() 플러그인입니다.

```shell
oc-compliance
```

```shell
oc
```

#### 1.2.2. 파일 무결성 검사

관리자는 File Integrity Operator 를 사용하여 클러스터 노드에서 파일 무결성 검사를 지속적으로 실행하고 수정된 파일의 로그를 제공할 수 있습니다.

### 1.3. 추가 리소스

인증 이해

내부 OAuth 서버 구성

ID 공급자 구성 이해

RBAC를 사용하여 권한 정의 및 적용

보안 컨텍스트 제약 조건 관리

### 2.1. 컨테이너 보안 이해

컨테이너화된 애플리케이션은 여러 수준의 보안에 의존합니다.

컨테이너 보안은 신뢰할 수 있는 기본 컨테이너 이미지로 시작하며 CI/CD 파이프라인에 따라 진행하면서 컨테이너 빌드 프로세스를 계속합니다.

중요

기본적으로 이미지 스트림은 자동으로 업데이트되지 않습니다. 이 기본 동작은 이미지 스트림에서 참조하는 이미지에 대한 보안 업데이트가 자동으로 발생하지 않기 때문에 보안 문제가 발생할 수 있습니다. 이 기본 동작을 재정의하는 방법에 대한 자세한 내용은 주기적으로 imagestreamtag 가져오기 구성을 참조하십시오.

배포된 컨테이너의 보안은 컨테이너가 보안 운영 체제 및 네트워크에서 실행 중이며 컨테이너와 상호 작용하는 사용자 및 호스트와 컨테이너 자체 사이에 확실한 경계가 설정되어 있는지에 따라 결정됩니다.

컨테이너 이미지에서 취약점을 스캔하고 취약한 이미지를 효율적으로 수정 및 교체하는 기능이 있어야 지속적인 보안이 가능합니다.

OpenShift Container Platform과 같은 플랫폼이 기본적으로 제공하는 보안 외에도 조직에는 자체 보안 요구 사항이 있습니다. OpenShift Container Platform을 데이터 센터로 가져오려면 일정 수준의 컴플라이언스 확인이 필요할 수 있습니다.

마찬가지로 조직의 보안 표준을 충족하기 위해 자체 에이전트, 특수 하드웨어 드라이버 또는 암호화 기능을 OpenShift Container Platform에 추가해야 할 수도 있습니다.

이 가이드에서는 호스트 계층, 컨테이너 및 오케스트레이션 계층, 빌드 및 애플리케이션 계층의 솔루션을 포함하여 OpenShift Container Platform에서 사용 가능한 컨테이너 보안 조치의 수준 높은 검토 단계를 제공합니다. 그런 다음 보안 조치를 달성하는 데 도움이 되는 특정 OpenShift Container Platform 설명서를 표시합니다.

이 안내서에는 다음 정보가 포함되어 있습니다.

컨테이너 보안이 중요한 이유 및 기존 보안 표준과의 비교

호스트(RHCOS 및 RHEL) 계층에서 제공하는 컨테이너 보안 조치와 OpenShift Container Platform에서 제공하는 컨테이너 보안 조치

컨테이너 콘텐츠 및 취약점의 소스를 평가하는 방법

컨테이너 콘텐츠를 사전 예방식으로 확인하기 위해 빌드 및 배포 프로세스를 디자인하는 방법

인증 및 권한 부여를 통해 컨테이너에 대한 액세스를 제어하는 방법

OpenShift Container Platform에서 네트워킹 및 연결된 스토리지를 보호하는 방법

API 관리 및 SSO에 사용하는 컨테이너화된 솔루션

이 가이드의 목표는 컨테이너화된 워크로드에 OpenShift Container Platform을 사용하여 얻을 수 있는 뛰어난 보안 이점과 Red Hat 에코시스템을 통해 컨테이너를 안전하게 만들고 유지하는 방법을 이해하는 것입니다. 또한 조직의 보안 목표를 달성하기 위해 OpenShift Container Platform에 참여하는 방법을 이해하는 데 도움이 됩니다.

#### 2.1.1. 컨테이너 정의

컨테이너에서는 애플리케이션과 모든 종속 항목을 변경하지 않고 개발에서 테스트 및 프로덕션으로 승격할 수 있는 단일 이미지로 패키징합니다. 컨테이너는 다른 컨테이너와 밀접하게 작동하는 더 큰 애플리케이션의 일부일 수 있습니다.

컨테이너에서는 물리 서버, 가상 머신(VM) 및 프라이빗 또는 퍼블릭 클라우드와 같은 환경 및 여러 배치 대상 사이에 일관성을 제공합니다.

컨테이너를 사용하면 다음과 같은 이점이 있습니다.

| 인프라 | 애플리케이션 |
| --- | --- |
| 공유 Linux 운영 체제 커널의 샌드박스 애플리케이션 프로세스 | 내 애플리케이션 및 모든 종속 항목 패키징 |
| 가상 머신보다 단순하고 가벼우며 밀도가 높음 | 몇 초 안에 모든 환경에 배포하고 CI/CD 활성화 |
| 다양한 환경에 이식 가능 | 컨테이너화된 구성요소에 쉽게 액세스 및 공유 |

Linux 컨테이너에 관한 자세한 내용은 Red Hat Customer Portal의 Linux 컨테이너 이해 를 참조하십시오. RHEL 컨테이너 툴에 관해 알아보려면 RHEL 제품 설명서의 컨테이너 빌드, 실행 및 관리 를 참조하십시오.

#### 2.1.2. OpenShift Container Platform의 정의

컨테이너화된 애플리케이션이 배포, 실행 및 관리되는 방식을 자동화하는 것이 OpenShift Container Platform과 같은 플랫폼의 역할입니다. OpenShift Container Platform의 핵심은 쿠버네티스 프로젝트를 사용하여 확장 가능한 데이터 센터의 여러 노드에서 컨테이너를 조정하는 엔진을 제공하는 것입니다.

쿠버네티스는 프로젝트에서 지원 가능성을 보장하지 않는 여러 다른 운영 체제 및 애드온 구성요소를 사용하여 실행할 수 있는 프로젝트입니다. 결과적으로 쿠버네티스 플랫폼마다 보안이 다를 수 있습니다.

OpenShift Container Platform은 쿠버네티스 보안을 잠그고 다양한 확장 구성요소와 플랫폼을 통합하도록 설계되었습니다. 이를 위해 OpenShift Container Platform에서는 운영 체제, 인증, 스토리지, 네트워킹, 개발 툴, 기본 컨테이너 이미지 및 기타 여러 구성요소를 포함하는 광범위한 오픈소스 기술의 Red Hat 에코 시스템을 활용합니다.

OpenShift Container Platform은 플랫폼에서 실행 중인 컨테이너화된 애플리케이션 외에도 플랫폼 자체의 취약점을 발견하고 신속하게 수정 사항을 배포하는 Red Hat의 환경을 활용할 수 있습니다. Red Hat 환경에서는 새로운 구성요소가 사용 가능하게 되면 OpenShift Container Platform과 효율적으로 통합하고 개별 고객 요구 사항에 맞게 기술을 조정하는 범위까지 기능이 확장됩니다.

추가 리소스

OpenShift Container Platform 아키텍처

OpenShift 보안 가이드

### 2.2. 호스트 및 VM 보안 이해

컨테이너와 가상 머신 모두 호스트에서 실행 중인 애플리케이션을 운영 체제 자체에서 분리하는 방법을 제공합니다. OpenShift Container Platform에서 사용하는 운영 체제인 RHCOS를 이해하면 호스트 시스템이 컨테이너와 호스트를 서로 보호하는 방법을 알 수 있습니다.

#### 2.2.1. RHCOS(Red Hat Enterprise Linux CoreOS)에서 컨테이너 보안

컨테이너를 사용하면 동일한 커널 및 컨테이너 런타임을 통해 각 컨테이너를 가동하여 동일한 호스트에서 실행되도록 많은 애플리케이션을 배포하는 작업이 단순화됩니다. 애플리케이션은 많은 사용자가 소유할 수 있으며, 개별적으로 유지되기 때문에 서로 다르거나 호환되지 않는 버전의 애플리케이션도 문제없이 동시에 실행될 수 있습니다.

Linux에서 컨테이너는 특별한 유형의 프로세스이므로 컨테이너 보안은 여러 가지 면에서 기타 실행 중인 프로세스를 보호하는 것과 비슷합니다. 컨테이너를 실행하는 환경은 컨테이너를 서로 보호할 뿐만 아니라 호스트에서 실행 중인 다른 프로세스 및 컨테이너로부터 호스트 커널을 보호할 수 있는 운영 체제로 시작합니다.

OpenShift Container Platform 4.20은 RHEL(Red Hat Enterprise Linux)을 작업자 노드로 사용하는 옵션과 함께 RHCOS 호스트에서 실행되므로 다음 개념이 배포된 모든 OpenShift Container Platform 클러스터에 기본적으로 적용됩니다. 이러한 RHEL 보안 기능은 OpenShift Container Platform에서 컨테이너를 더 안전하게 실행할 수 있게 하는 핵심 요소입니다.

Linux 네임스페이스 를 사용하면 특정 글로벌 시스템 리소스를 추상화하여 네임스페이스에서 처리할 별도의 인스턴스로 표시할 수 있습니다. 따라서 여러 컨테이너가 충돌없이 동일한 컴퓨팅 리소스를 동시에 사용할 수 있습니다. 기본적으로 호스트와 분리된 컨테이너 네임스페이스에는 마운트 테이블, 프로세스 테이블, 네트워크 인터페이스, 사용자, 제어 그룹, UTS 및 IPC 네임스페이스가 있습니다. 호스트 네임스페이스에 직접 액세스해야 하는 컨테이너에는 높은 권한이 있어야 해당 액세스를 요청할 수 있습니다. 네임스페이스 유형에 대한 자세한 내용은 RHEL 9 컨테이너 설명서에서 컨테이너 빌드, 실행 및 관리를 참조하십시오.

SELinux 에서는 컨테이너 간에 서로 격리하고 컨테이너를 호스트에서 격리된 상태로 유지하는 추가 보안 계층을 제공합니다. 관리자는 SELinux를 사용하여 모든 사용자, 애플리케이션, 프로세스 및 파일에 MAC(필수 액세스 제어)를 적용할 수 있습니다.

주의

RHCOS에서 SELinux를 비활성화하는 것은 지원되지 않습니다.

CGroup (제어 그룹)은 프로세스 컬렉션의 리소스 사용량(CPU, 메모리, 디스크 I/O, 네트워크 등)을 제한, 설명 및 격리합니다. CGroup을 사용하면 동일한 호스트의 컨테이너가 서로 영향을 주지 않습니다.

보안 컴퓨팅 모드(seccomp) 프로파일은 사용 가능한 시스템 호출을 제한하기 위해 컨테이너와 연관될 수 있습니다. seccomp에 대한 자세한 내용은 Red Hat OpenShift 보안 가이드 의 94페이지를 참조하십시오.

RHCOS 를 사용하여 컨테이너를 배포하면 호스트 환경을 최소화하고 컨테이너에 맞게 조정하여 공격 면적을 줄입니다. CRI-O 컨테이너 엔진 은 데스크톱 지향 독립 실행형 기능을 구현하는 다른 컨테이너 엔진과 달리 컨테이너를 실행하고 관리하기 위해 쿠버네티스 및 OpenShift Container Platform에 필요한 기능만 구현하여 공격 면적을 더 줄입니다.

RHCOS는 OpenShift Container Platform 클러스터에서 컨트롤 플레인 (마스터) 및 작업자 노드로 작동하도록 특별히 구성된 RHEL (Red Hat Enterprise Linux) 버전입니다. 따라서 RHCOS는 쿠버네티스 및 OpenShift Container Platform 서비스와 함께 컨테이너 워크로드를 효율적으로 실행하도록 조정됩니다.

참고

OpenShift Container Platform 클러스터에서 RHCOS 시스템을 추가로 보호하려면 호스트 시스템 자체를 관리하거나 모니터링하는 컨테이너를 제외한 대부분의 컨테이너는 루트가 아닌 사용자로 실행해야 합니다. 고유한 OpenShift Container Platform 클러스터를 보호하는 데 권장되는 모범 사례는 권한 수준을 낮추거나 가능한 최소 권한으로 컨테이너를 생성하는 것입니다.

추가 리소스

노드에서 리소스 제약 조건을 적용하는 방법

보안 컨텍스트 제약 조건 관리

OpenShift 클러스터에서 지원되는 플랫폼

사용자 프로비저닝 인프라를 포함한 클러스터의 시스템 요구사항

RHCOS 구성 방법 선택

Ignition

커널 인수

커널 모듈

디스크 암호화

Chrony 타임 서비스

OpenShift 업데이트 서비스 정보

FIPS 암호화

#### 2.2.2. 가상화 및 컨테이너 비교

기존 가상화에서는 동일한 물리적 호스트에서 애플리케이션 환경을 분리한 상태로 유지할 수 있는 또 다른 방법을 제공합니다. 그러나 가상 머신은 컨테이너와 다른 방식으로 작동합니다. 가상화는 게스트 가상 머신(VM)을 가동시키는 하이퍼바이저를 사용하며, 각 가상 머신에는 실행 중인 커널로 표시되는 자체 운영 체제(OS)와 실행 중인 애플리케이션 및 해당 종속 항목이 있습니다.

VM을 사용하면 하이퍼바이저에서 게스트 간에 서로 분리하고 호스트 커널에서 게스트를 분리합니다. 하이퍼바이저에 액세스하는 개인과 프로세스 수가 적어지므로 물리 서버의 공격 면적을 줄입니다. 보안은 여전히 모니터링해야 하지만, 하나의 게스트 VM은 하이퍼바이저 버그를 사용하여 다른 VM 또는 호스트 커널에 액세스할 수 있습니다. 또한 OS에 패치가 필요한 경우 해당 OS를 사용하는 모든 게스트 VM에서 패치를 적용해야 합니다.

컨테이너는 게스트 VM 내부에서 실행될 수 있으며 이와 같은 조치 바람직한 경우가 있을 수 있습니다. 예를 들어, 애플리케이션을 클라우드로 수정 없이 그대로 리프트 앤 시프트(lift-and-shift) 방식으로 배포하고 이동하기 위해 컨테이너에 기존 애플리케이션을 배포할 수 있습니다.

그러나 단일 호스트에서 컨테이너를 분리하면 더 가볍고 유연하며 쉽게 확장되는 배포 솔루션이 제공됩니다. 이 배포 모델은 특히 클라우드 네이티브 애플리케이션에 적합합니다. 컨테이너는 일반적으로 VM보다 훨씬 작으며 메모리와 CPU 사용량이 적습니다.

컨테이너와 VM의 차이점에 관해 알아보려면 RHEL 7 컨테이너 설명서의 Linux 컨테이너와 KVM 가상화 비교 를 참조하십시오.

#### 2.2.3. OpenShift Container Platform 보호

OpenShift Container Platform을 배포할 때 설치 프로그램 프로비저닝 인프라(사용 가능한 플랫폼이 여러 개) 또는 사용자가 프로비저닝한 자체 인프라 중에서 선택할 수 있습니다. FIPS 모드 활성화 또는 처음 부팅 시 필요한 커널 모듈 추가와 같은 일부 낮은 수준의 보안 관련 구성은 사용자 프로비저닝 인프라를 활용할 수 있습니다. 마찬가지로 사용자 프로비저닝 인프라는 연결 해제된 OpenShift Container Platform 배포에 적합합니다.

OpenShift Container Platform의 보안 향상 및 기타 구성 변경과 관련된 목표는 다음과 같습니다.

기본 노드를 최대한 일반적으로 유지합니다. 비슷한 노드를 신속하고 규범에 맞는 방식으로 쉽게 제거하고 구동할 수 있어야 합니다.

노드를 일회성으로 직접 변경하지 말고 최대한 OpenShift Container Platform에서 노드 수정을 관리합니다.

이러한 목표를 달성하기 위해 대부분의 노드 변경은 설치 중 Ignition을 사용하거나 나중에 Machine Config Operator가 노드 세트에 적용하는 MachineConfig를 사용하여 수행해야 합니다. 이러한 방식으로 수행할 수 있는 보안 관련 구성 변경의 예는 다음과 같습니다.

커널 인수 추가

커널 모듈 추가

FIPS 암호화 지원 활성화

디스크 암호화 구성

chrony 타임 서비스 구성

Machine Config Operator 외에도 CVO(Cluster Version Operator)에서 관리하며 OpenShift Container Platform 인프라를 구성하는 데 사용할 수 있는 Operator는 여러 가지가 있습니다. CVO를 사용하면 OpenShift Container Platform 클러스터 업데이트의 여러 요소를 자동화할 수 있습니다.

추가 리소스

FIPS 암호화

### 2.3. RHCOS 강화

RHCOS는 RHCOS 노드에 필요한 변경이 거의 없이 OpenShift Container Platform에 배포되도록 생성되고 조정되었습니다. OpenShift Container Platform을 채택한 모든 조직에는 시스템 강화를 위한 고유 요구 사항이 있습니다. OpenShift 고유 수정 사항 및 기능(예: 제한된 불변성을 제공하는 Ignition, ostree 및 읽기 전용 `/usr` 등)이 추가된 RHEL 시스템으로 RHCOS는 다른 RHEL 시스템과 마찬가지로 강화될 수 있습니다. 차이점은 강화 관리 방법에 있습니다.

OpenShift Container Platform과 쿠버네티스 엔진의 주요 기능은 필요에 따라 애플리케이션과 인프라를 빠르게 확장하고 축소할 수 있다는 것입니다. 불가피한 경우가 아니라면 호스트에 로그인하고 소프트웨어를 추가하거나 설정을 변경하여 RHCOS를 직접 변경하지 않게 합니다. OpenShift Container Platform 설치 프로그램 및 컨트롤 플레인에서 RHCOS의 변경 사항을 관리하여 수동 조작없이 새 노드를 구동할 수 있습니다.

따라서 보안 요구 사항을 충족하기 위해 OpenShift Container Platform에서 RHCOS 노드를 강화하려는 경우 강화할 대상과 강화를 수행하는 방법을 모두 고려해야 합니다.

#### 2.3.1. RHCOS에서 강화할 대상 선택

RHEL 시스템의 보안에 액세스하는 방법에 대한 자세한 내용은 RHEL 9 Security Hardening 가이드를 참조하십시오.

이 가이드를 사용하여 암호화에 접근하고 취약점을 평가하며 다양한 서비스에 대한 위협을 평가하는 방법을 알아봅니다. 마찬가지로 컴플라이언스 표준을 스캔하고, 파일 무결성을 확인하며, 감사를 수행하고, 스토리지 장치를 암호화하는 방법을 배울 수 있습니다.

강화하려는 기능에 관한 지식을 통해 RHCOS에서 강화할 방법을 결정할 수 있습니다.

#### 2.3.2. RHCOS 강화 방법 선택

OpenShift Container Platform에서 RHCOS 시스템을 직접 수정하지 않는 것이 좋습니다. 대신 작업자 노드 및 컨트롤 플레인 노드와 같은 노드 풀의 시스템 수정을 고려해야 합니다. 베어 메탈이 아닌 설치에서 새 노드가 필요한 경우 원하는 유형의 새 노드를 요청할 수 있으며 RHCOS 이미지와 이전에 수정한 사항으로 노드를 생성합니다.

설치 전, 설치 중 및 클러스터가 가동되어 실행된 후에 RHCOS를 수정할 기회가 있습니다.

#### 2.3.2.1. 설치 전 강화

베어 메탈 설치의 경우 OpenShift Container Platform 설치를 시작하기 전에 RHCOS에 강화 기능을 추가할 수 있습니다. 예를 들어 RHCOS 설치 프로그램을 부팅할 때 커널 옵션을 추가하여 다양한 SELinux 부울 또는 대칭 멀티스레딩과 같은 다양한 SELinux 부울 또는 하위 수준 설정과 같은 보안 기능을 켜거나 끌 수 있습니다.

주의

RHCOS 노드에서 SELinux를 비활성화하는 것은 지원되지 않습니다.

베어 메탈 RHCOS 설치는 더 어렵지만 OpenShift Container Platform 설치를 시작하기 전에 운영 체제를 변경할 수 있는 기회를 제공합니다. 디스크 암호화 또는 특수 네트워킹 설정과 같은 특정 기능을 가능한 빨리 설정해야 할 때 중요할 수 있습니다.

#### 2.3.2.2. 설치 중 강화

OpenShift Container Platform 설치 프로세스를 중단하고 Ignition 구성을 변경할 수 있습니다. Ignition 구성을 통해 자체 파일 및 systemd 서비스를 RHCOS 노드에 추가할 수 있습니다. 또한 설치에 사용되는 `install-config.yaml` 파일에서 기본 보안 관련 사항을 변경할 수 있습니다. 이 방식으로 추가된 콘텐츠는 각 노드의 첫 부팅 시 사용할 수 있습니다.

#### 2.3.2.3. 클러스터가 실행된 후 강화

OpenShift Container Platform 클러스터가 가동되어 실행된 후 RHCOS에 강화 기능을 적용하는 방법은 몇 가지가 있습니다.

데몬 세트: 모든 노드에서 서비스를 실행해야 하는 경우 Kubernetes `DaemonSet` 오브젝트 로 해당 서비스를 추가할 수 있습니다.

머신 구성: `MachineConfig` 오브젝트에는 동일한 형식의 Ignition 구성 서브 세트가 있습니다. 머신 구성을 모든 작업자 또는 컨트롤 플레인 노드에 적용하면 클러스터에 추가된 동일한 유형의 다음 노드에 동일한 변경 사항이 적용될 수 있습니다.

여기에 언급된 모든 기능은 OpenShift Container Platform 제품 설명서에 설명되어 있습니다.

추가 리소스

OpenShift 보안 가이드

RHCOS 구성 방법 선택

노드 수정

수동으로 설치 구성 파일 생성

Kubernetes 매니페스트 및 Ignition 설정 파일 생성

ISO 이미지를 사용하여 RHCOS 설치

노드의 사용자 정의

노드에 커널 인수 추가

선택적 구성 매개변수

FIPS 암호화 지원

RHEL 핵심 암호화 구성요소

### 2.4. 컨테이너 이미지 서명

Red Hat은 Red Hat Container Registries에 있는 이미지에 대한 서명을 제공합니다. 이러한 서명은 MCO(Machine Config Operator)를 사용하여 OpenShift Container Platform 4 클러스터로 가져올 때 자동으로 확인할 수 있습니다.

Quay.io 는 OpenShift Container Platform을 구성하는 대부분의 이미지를 제공하며 릴리스 이미지만 서명됩니다. 릴리스 이미지는 승인된 OpenShift Container Platform 이미지를 참조하여 공급 체인 공격에 대한 보안 수준을 제공합니다. 그러나 로깅, 모니터링 및 서비스 메시와 같은 OpenShift Container Platform에 대한 일부 확장 기능은 OLM(Operator Lifecycle Manager)에서 Operator로 제공됩니다. 이러한 이미지는 Red Hat Ecosystem Catalog 컨테이너 이미지 레지스트리에서 제공됩니다.

Red Hat 레지스트리와 인프라 간의 이미지의 무결성을 확인하려면 서명 확인을 활성화하십시오.

#### 2.4.1. Red Hat Container Registries에 대한 서명 확인 활성화

Red Hat Container Registries에 대한 컨테이너 서명 검증을 활성화하려면 이러한 레지스트리의 이미지를 확인하는 키를 지정하는 서명 확인 정책 파일을 작성해야 합니다. RHEL8 노드의 경우 레지스트리는 기본적으로 `/etc/containers/registries.d` 에 이미 정의되어 있습니다.

프로세스

작업자 노드에 필요한 구성이 포함된 Butane 구성 파일 `51-worker-rh-registry-trust.bu` 를 만듭니다.

참고

구성 파일에 지정하는 Butane 버전이 OpenShift Container Platform 버전과 일치해야 하며 항상 `0` 으로 끝나야 합니다. 예: `4.20.0`. Butane에 대한 자세한 내용은 “Butane 을 사용하여 머신 구성 생성”을 참조하십시오.

```yaml
variant: openshift
version: 4.20.0
metadata:
  name: 51-worker-rh-registry-trust
  labels:
    machineconfiguration.openshift.io/role: worker
storage:
  files:
  - path: /etc/containers/policy.json
    mode: 0644
    overwrite: true
    contents:
      inline: |
        {
          "default": [
            {
              "type": "insecureAcceptAnything"
            }
          ],
          "transports": {
            "docker": {
              "registry.access.redhat.com": [
                {
                  "type": "signedBy",
                  "keyType": "GPGKeys",
                  "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
                }
              ],
              "registry.redhat.io": [
                {
                  "type": "signedBy",
                  "keyType": "GPGKeys",
                  "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
                }
              ]
            },
            "docker-daemon": {
              "": [
                {
                  "type": "insecureAcceptAnything"
                }
              ]
            }
          }
        }
```

Butane을 사용하여 작업자 노드의 디스크에 작성할 파일이 포함된 머신 구성 YAML 파일 `51-worker-rh-registry-trust.yaml` 을 생성합니다.

```shell-session
$ butane 51-worker-rh-registry-trust.bu -o 51-worker-rh-registry-trust.yaml
```

생성된 머신 구성을 적용합니다.

```shell-session
$ oc apply -f 51-worker-rh-registry-trust.yaml
```

작업자 머신 구성 풀이 새 머신 구성을 사용하여 롤아웃되었는지 확인합니다.

새 머신 구성이 생성되었는지 확인합니다.

```shell-session
$ oc get mc
```

```shell-session
NAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
00-worker                                          a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
01-master-container-runtime                        a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
01-master-kubelet                                  a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
01-worker-container-runtime                        a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
01-worker-kubelet                                  a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
51-master-rh-registry-trust                                                                   3.5.0             13s
51-worker-rh-registry-trust                                                                   3.5.0             53s
99-master-generated-crio-seccomp-use-default                                                  3.5.0             25m
99-master-generated-registries                     a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
99-master-ssh                                                                                 3.2.0             28m
99-worker-generated-crio-seccomp-use-default                                                  3.5.0             25m
99-worker-generated-registries                     a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             25m
99-worker-ssh                                                                                 3.2.0             28m
rendered-master-af1e7ff78da0a9c851bab4be2777773b   a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             8s
rendered-master-cd51fd0c47e91812bfef2765c52ec7e6   a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             24m
rendered-worker-2b52f75684fbc711bd1652dd86fd0b82   a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             24m
rendered-worker-be3b3bce4f4aa52a62902304bac9da3c   a2178ad522c49ee330b0033bb5cb5ea132060b0a   3.5.0             48s
```

1. 새 머신 구성

2. 새로 렌더링된 머신 구성

작업자 머신 구성 풀이 새 머신 구성을 사용하여 업데이트되었는지 확인합니다.

```shell-session
$ oc get mcp
```

```shell-session
NAME     CONFIG                                             UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
master   rendered-master-af1e7ff78da0a9c851bab4be2777773b   True      False      False      3              3                   3                     0                      30m
worker   rendered-worker-be3b3bce4f4aa52a62902304bac9da3c   False     True       False      3              0                   0                     0                      30m
```

1. `UPDATING` 필드가 `True` 이면 머신 구성 풀이 새 머신 구성으로 업데이트됩니다. 필드가 `False` 가 되면 작업자 머신 구성 풀이 새 머신 구성에 롤아웃됩니다.

클러스터에서 RHEL7 작업자 노드를 사용하는 경우 작업자 머신 구성 풀이 업데이트되면 `/etc/containers/registries.d` 디렉터리의 해당 노드에 YAML 파일을 생성하여 지정된 레지스트리 서버의 분리된 서명 위치를 지정합니다. 다음 예제는 `registry.access.redhat.com` 및 `registry.redhat.io` 에서 호스팅되는 이미지에 대해서만 작동합니다.

각 RHEL7 작업자 노드에 대한 디버그 세션을 시작합니다.

```shell-session
$ oc debug node/<node_name>
```

루트 디렉토리를 `/host` 로 변경합니다.

```shell-session
sh-4.2# chroot /host
```

다음을 포함하는 `/etc/containers/registries.d/registry.redhat.io.yaml` 파일을 만듭니다.

```shell-session
docker:
     registry.redhat.io:
         sigstore: https://registry.redhat.io/containers/sigstore
```

다음을 포함하는 `/etc/containers/registries.d/registry.access.redhat.com.yaml` 파일을 만듭니다.

```shell-session
docker:
     registry.access.redhat.com:
         sigstore: https://access.redhat.com/webassets/docker/content/sigstore
```

디버그 세션을 종료합니다.

#### 2.4.2. 서명 확인 구성 확인

머신 구성을 클러스터에 적용한 후 머신 구성 컨트롤러에서 새 `MachineConfig` 오브젝트를 감지하고 새로운 `rendered-worker-<hash>` 버전을 생성합니다.

사전 요구 사항

머신 구성 파일을 사용하여 서명 확인 활성화로 설정해야 합니다.

프로세스

명령줄에서 다음 명령을 실행하여 원하는 작업자에 대한 정보를 표시합니다.

```shell-session
$ oc describe machineconfigpool/worker
```

```shell-session
Name:         worker
Namespace:
Labels:       machineconfiguration.openshift.io/mco-built-in=
Annotations:  <none>
API Version:  machineconfiguration.openshift.io/v1
Kind:         MachineConfigPool
Metadata:
  Creation Timestamp:  2019-12-19T02:02:12Z
  Generation:          3
  Resource Version:    16229
  Self Link:           /apis/machineconfiguration.openshift.io/v1/machineconfigpools/worker
  UID:                 92697796-2203-11ea-b48c-fa163e3940e5
Spec:
  Configuration:
    Name:  rendered-worker-f6819366eb455a401c42f8d96ab25c02
    Source:
      API Version:  machineconfiguration.openshift.io/v1
      Kind:         MachineConfig
      Name:         00-worker
      API Version:  machineconfiguration.openshift.io/v1
      Kind:         MachineConfig
      Name:         01-worker-container-runtime
      API Version:  machineconfiguration.openshift.io/v1
      Kind:         MachineConfig
      Name:         01-worker-kubelet
      API Version:  machineconfiguration.openshift.io/v1
      Kind:         MachineConfig
      Name:         51-worker-rh-registry-trust
      API Version:  machineconfiguration.openshift.io/v1
      Kind:         MachineConfig
      Name:         99-worker-92697796-2203-11ea-b48c-fa163e3940e5-registries
      API Version:  machineconfiguration.openshift.io/v1
      Kind:         MachineConfig
      Name:         99-worker-ssh
  Machine Config Selector:
    Match Labels:
      machineconfiguration.openshift.io/role:  worker
  Node Selector:
    Match Labels:
      node-role.kubernetes.io/worker:
  Paused:                              false
Status:
  Conditions:
    Last Transition Time:  2019-12-19T02:03:27Z
    Message:
    Reason:
    Status:                False
    Type:                  RenderDegraded
    Last Transition Time:  2019-12-19T02:03:43Z
    Message:
    Reason:
    Status:                False
    Type:                  NodeDegraded
    Last Transition Time:  2019-12-19T02:03:43Z
    Message:
    Reason:
    Status:                False
    Type:                  Degraded
    Last Transition Time:  2019-12-19T02:28:23Z
    Message:
    Reason:
    Status:                False
    Type:                  Updated
    Last Transition Time:  2019-12-19T02:28:23Z
    Message:               All nodes are updating to rendered-worker-f6819366eb455a401c42f8d96ab25c02
    Reason:
    Status:                True
    Type:                  Updating
  Configuration:
    Name:  rendered-worker-d9b3f4ffcfd65c30dcf591a0e8cf9b2e
    Source:
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   00-worker
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   01-worker-container-runtime
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   01-worker-kubelet
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   99-worker-92697796-2203-11ea-b48c-fa163e3940e5-registries
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   99-worker-ssh
  Degraded Machine Count:     0
  Machine Count:              1
  Observed Generation:        3
  Ready Machine Count:        0
  Unavailable Machine Count:  1
  Updated Machine Count:      0
Events:                       <none>
```

아래 명령을 다시 실행합니다.

```shell
oc describe
```

```shell-session
$ oc describe machineconfigpool/worker
```

```shell-session
...
    Last Transition Time:  2019-12-19T04:53:09Z
    Message:               All nodes are updated with rendered-worker-f6819366eb455a401c42f8d96ab25c02
    Reason:
    Status:                True
    Type:                  Updated
    Last Transition Time:  2019-12-19T04:53:09Z
    Message:
    Reason:
    Status:                False
    Type:                  Updating
  Configuration:
    Name:  rendered-worker-f6819366eb455a401c42f8d96ab25c02
    Source:
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   00-worker
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   01-worker-container-runtime
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   01-worker-kubelet
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   51-worker-rh-registry-trust
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   99-worker-92697796-2203-11ea-b48c-fa163e3940e5-registries
      API Version:            machineconfiguration.openshift.io/v1
      Kind:                   MachineConfig
      Name:                   99-worker-ssh
  Degraded Machine Count:     0
  Machine Count:              3
  Observed Generation:        4
  Ready Machine Count:        3
  Unavailable Machine Count:  0
  Updated Machine Count:      3
...
```

참고

`Observed Generation` 매개변수는 컨트롤러에서 생성된 구성의 생성에 따라 증가된 개수를 보여줍니다. 이 컨트롤러는 사양을 처리하고 수정본을 생성하지 못하더라도 이 값을 업데이트합니다. `Configuration Source` 값은 `51-worker-rh-registry-trust` 구성을 나타냅니다.

다음 명령을 사용하여 `policy.json` 파일이 있는지 확인합니다.

```shell-session
$ oc debug node/<node> -- chroot /host cat /etc/containers/policy.json
```

```shell-session
Starting pod/<node>-debug ...
To use host binaries, run `chroot /host`
{
  "default": [
    {
      "type": "insecureAcceptAnything"
    }
  ],
  "transports": {
    "docker": {
      "registry.access.redhat.com": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
        }
      ],
      "registry.redhat.io": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
        }
      ]
    },
    "docker-daemon": {
      "": [
        {
          "type": "insecureAcceptAnything"
        }
      ]
    }
  }
}
```

다음 명령을 사용하여 `registry.redhat.io.yaml` 파일이 있는지 확인합니다.

```shell-session
$ oc debug node/<node> -- chroot /host cat /etc/containers/registries.d/registry.redhat.io.yaml
```

```shell-session
Starting pod/<node>-debug ...
To use host binaries, run `chroot /host`
docker:
     registry.redhat.io:
         sigstore: https://registry.redhat.io/containers/sigstore
```

다음 명령을 사용하여 `registry.access.redhat.yaml` 파일이 있는지 확인합니다.

```shell-session
$ oc debug node/<node> -- chroot /host cat /etc/containers/registries.d/registry.access.redhat.com.yaml
```

```shell-session
Starting pod/<node>-debug ...
To use host binaries, run `chroot /host`
docker:
     registry.access.redhat.com:
         sigstore: https://access.redhat.com/webassets/docker/content/sigstore
```

#### 2.4.3. 검증 가능한 서명이 없는 컨테이너 이미지의 확인 이해

각 OpenShift Container Platform 릴리스 이미지는 변경할 수 없으며 Red Hat 프로덕션 키를 사용하여 서명됩니다. OpenShift Container Platform 업데이트 또는 설치 중에 릴리스 이미지에서 확인 가능한 서명이 없는 컨테이너 이미지를 배포할 수 있습니다. 서명된 각 릴리스 이미지 다이제스트는 변경할 수 없습니다. 릴리스 이미지의 각 참조는 다른 이미지의 변경 불가능한 다이제스트이므로 콘텐츠를 전송하여 신뢰할 수 있습니다. 즉, 릴리스 이미지의 서명은 모든 릴리스 콘텐츠의 유효성을 검사합니다.

예를 들어 검증 가능한 서명이 없는 이미지 참조는 서명된 OpenShift Container Platform 릴리스 이미지에 포함되어 있습니다.

```shell-session
$ oc adm release info quay.io/openshift-release-dev/ocp-release@sha256:2309578b68c5666dad62aed696f1f9d778ae1a089ee461060ba7b9514b7ca417 -o pullspec
quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:9aafb914d5d7d0dec4edd800d02f811d7383a7d49e500af548eab5d00c1bffdb
```

1. 서명된 릴리스 이미지 SHA.

2. 릴리스에는 확인 가능한 서명이 없는 컨테이너 이미지입니다.

#### 2.4.3.1. 업데이트 중 자동 확인

서명 확인은 자동입니다. CVO(OpenShift Cluster Version Operator)는 OpenShift Container Platform 업데이트 중에 릴리스 이미지의 서명을 확인합니다. 이는 내부 프로세스입니다. 자동 확인에 실패하면 OpenShift Container Platform 설치 또는 업데이트가 실패합니다.

서명 확인은 아래 명령줄 유틸리티를 사용하여 수동으로 수행할 수도 있습니다.

```shell
skopeo
```

추가 리소스

OpenShift 업데이트 소개

#### 2.4.3.2. skopeo를 사용하여 Red Hat 컨테이너 이미지의 서명 확인

OCP 릴리스 미러 사이트에서 해당 서명을 가져와서 OpenShift Container Platform 릴리스 이미지에 포함된 컨테이너 이미지의 서명을 확인할 수 있습니다. 미러 사이트의 서명은 Podman 또는 CRI-O에서 쉽게 이해할 수 있는 형식이 아니므로 아래 명령을 사용하여 Red Hat에서 릴리스 이미지에 서명했는지 확인할 수 있습니다.

```shell
skopeo standalone-verify
```

사전 요구 사항

아래 명령줄 유틸리티를 설치했습니다.

```shell
skopeo
```

프로세스

다음 명령을 실행하여 릴리스의 전체 SHA를 가져옵니다.

```shell-session
$ oc adm release info <release_version>  \
```

1. <release_version>을 릴리스 번호로 바꿉니다(예: `4.14.3`).

```shell-session
---
Pull From: quay.io/openshift-release-dev/ocp-release@sha256:e73ab4b33a9c3ff00c9f800a38d69853ca0c4dfa5a88e3df331f66df8f18ec55
---
```

다음 명령을 실행하여 Red Hat 릴리스 키를 가져옵니다.

```shell-session
$ curl -o pub.key https://access.redhat.com/security/data/fd431d51.txt
```

다음 명령을 실행하여 확인할 특정 릴리스의 서명 파일을 가져옵니다.

```shell-session
$ curl -o signature-1 https://mirror.openshift.com/pub/openshift-v4/signatures/openshift-release-dev/ocp-release/sha256=<sha_from_version>/signature-1 \
```

1. & `lt;sha_from_version` >을 릴리스의 SHA와 일치하는 미러 사이트에 대한 전체 링크의 SHA 값으로 바꿉니다. 예를 들어 4.12.23 릴리스의 서명 링크는 `https://mirror.openshift.com/pub/openshift-v4/signatures/openshift-release-dev/ocp-release/sha256=e73ab4b33a9c3ff00c9f800a38d69853ca0c4dfa5a88e3df331f66df8f18ec55/signature-1` 이며 SHA 값은 `e73ab4b33a9c3ff00c9f800a38d69853ca0c4dfa5a88e3df331f18f18ec55` 입니다.

다음 명령을 실행하여 릴리스 이미지에 대한 매니페스트를 가져옵니다.

```shell-session
$ skopeo inspect --raw docker://<quay_link_to_release> > manifest.json \
```

1. & `lt;quay_link_to_release` >를 아래 명령의 출력으로 바꿉니다. 예를 들어 `quay.io/openshift-release-dev/ocp-release@sha256:e73ab4b33a9c3ff00c9f800a38d69853ca0c4dfa5a88e3df331f66df8f18ec55`.

```shell
oc adm release info
```

skopeo를 사용하여 서명을 확인합니다.

```shell-session
$ skopeo standalone-verify manifest.json quay.io/openshift-release-dev/ocp-release:<release_number>-<arch> any signature-1 --public-key-file pub.key
```

다음과 같습니다.

`<release_number>`

릴리스 번호를 지정합니다(예: `4.14.3`).

`<arch>`

아키텍처를 지정합니다(예: `x86_64`).

```shell-session
Signature verified using fingerprint 567E347AD0044ADE55BA8A5F199E2F91FD431D51, digest sha256:e73ab4b33a9c3ff00c9f800a38d69853ca0c4dfa5a88e3df331f66df8f18ec55
```

#### 2.4.4. 추가 리소스

머신 구성 개요

### 2.5. 컴플라이언스 이해

많은 OpenShift Container Platform 고객은 시스템을 프로덕션 환경에 도입하기 전에 일정 수준의 규제 준비 또는 컴플라이언스를 갖춰야 합니다. 이러한 규정 준비는 국가 표준, 산업 표준 또는 조직의 기업 거버넌스 프레임워크에 따라 규정될 수 있습니다.

#### 2.5.1. 컴플라이언스 및 위험 관리 이해

FIPS 컴플라이언스는 보안 수준이 높은 환경에서 요구되는 가장 중요한 구성요소 중 하나로, 지원되는 암호화 기술만 노드에서 허용합니다.

중요

클러스터의 FIPS 모드를 활성화하려면 FIPS 모드에서 작동하도록 구성된 RHEL(Red Hat Enterprise Linux) 컴퓨터에서 설치 프로그램을 실행해야 합니다. RHEL에서 FIPS 모드를 구성하는 방법에 대한 자세한 내용은 RHEL을 FIPS 모드로 전환 을 참조하십시오.

FIPS 모드로 부팅된 Red Hat Enterprise Linux(RHEL) 또는 Red Hat Enterprise Linux CoreOS(RHCOS)를 실행할 때 OpenShift Container Platform 핵심 구성 요소는 x86_64, ppc64le 및 s390x 아키텍처에서만 FIPS 140-2/140-3 검증을 위해 NIST에 제출된 RHEL 암호화 라이브러리를 사용합니다.

OpenShift Container Platform 컴플라이언스 프레임워크에 대한 Red Hat의 관점을 이해하려면 OpenShift 보안 가이드 의 위험 관리 및 규제 준비 장을 참조하십시오.

추가 리소스

FIPS 모드에서 클러스터 설치

### 2.6. 컨테이너 콘텐츠 보안

컨테이너 내부 콘텐츠의 보안을 유지하려면 Red Hat Universal Base Image와 같은 신뢰할 수 있는 기본 이미지로 시작하고 신뢰할 수 있는 소프트웨어를 추가해야 합니다. 컨테이너 이미지의 지속적인 보안을 확인하기 위해 이미지를 스캔하는 Red Hat 도구와 타사 도구가 있습니다.

#### 2.6.1. 컨테이너 내부 보안

애플리케이션 및 인프라는 쉽게 사용할 수 있는 구성요소로 구성되며, 대부분은 Linux 운영 체제, JBoss Web Server, PostgreSQL 및 Node.js와 같은 오픈소스 패키지입니다.

이러한 패키지의 컨테이너화된 버전도 제공됩니다. 그러나 패키지의 원래 위치, 사용된 버전, 빌드한 사람 및 악성 코드가 있는지 여부를 알아야 합니다.

답변해야 할 몇 가지 질문은 다음과 같습니다.

컨테이너 내부의 구성요소 때문에 인프라가 손상됩니까?

애플리케이션 계층에 알려진 취약점이 있습니까?

런타임 및 운영 체제 계층이 최신입니까?

Red Hat UBI(Universal Base Images)의 컨테이너를 빌드하여 컨테이너 이미지의 기초가 Red Hat Enterprise Linux에 포함된 동일한 RPM 패키지 소프트웨어로 구성되게 합니다. UBI 이미지를 사용하거나 재배포하는 데 서브스크립션이 필요하지 않습니다.

컨테이너 자체의 지속적인 보안을 보장하기 위해 RHEL에서 직접 사용되거나 OpenShift Container Platform에 추가된 보안 스캔 기능을 통해 사용 중인 이미지에 취약점이 있을 때 경고할 수 있습니다. OpenSCAP 이미지 스캔은 RHEL에서 사용할 수 있으며 Red Hat Quay Container Security Operator 를 추가하여 OpenShift Container Platform에서 사용하는 컨테이너 이미지를 확인할 수 있습니다.

#### 2.6.2. UBI를 사용하여 재배포 가능한 이미지 생성

컨테이너화된 애플리케이션을 생성하려면 일반적으로 운영 체제에서 제공하는 구성요소를 제공하는 신뢰할 수 있는 기본 이미지로 시작합니다. 여기에는 라이브러리, 유틸리티 및 운영 체제의 파일 시스템에서 애플리케이션에 표시될 것으로 예상되는 기타 기능이 포함됩니다.

Red Hat UBI(Universal Base Images)는 자체 컨테이너를 빌드하는 모든 사용자가 Red Hat Enterprise Linux rpm 패키지 및 기타 컨텐츠로 완전히 구성된 컨테이너로 시작할 수 있도록 설계되었습니다. 이 UBI 이미지는 보안 패치로 최신 상태를 유지하고 고유 소프트웨어를 포함하도록 빌드된 컨테이너 이미지를 자유롭게 사용하고 재배포하도록 정기적으로 업데이트됩니다.

다른 UBI 이미지의 상태를 찾고 확인하려면 Red Hat Ecosystem Catalog 를 검색하십시오. 보안 컨테이너 이미지의 생성자는 다음과 같은 일반적인 두 가지 유형의 UBI 이미지에 관심이 있을 수 있습니다.

UBI: RHEL 7, 8 및 9의 표준 UBI 이미지(`ubi7/ubi`, `ubi8/ubi` 및 `ubi9/ubi`)와 해당 시스템 기반 최소 이미지(`ubi7/ubi-minimal`, `ubi8/ubi-mimimal`, ubi9/ubi-imimal, ubi9/ubi-minimal)가 있습니다. 이러한 이미지는 모두 표준 `yum` 및 `dnf` 명령을 사용하여 빌드한 컨테이너 이미지에 추가할 수 있는 RHEL 소프트웨어의 무료 리포지토리를 가리키도록 미리 구성되어 있습니다.

참고

Red Hat은 Fedora 및 Ubuntu와 같은 다른 배포판에서 이러한 이미지를 사용하도록 권장합니다.

Red Hat Software Collections: 특정 유형의 애플리케이션에 대한 기본 이미지로 사용하기 위해 생성된 이미지를 찾으려면 Red Hat Ecosystem Catalog에서 `rhscl/` 을 검색하십시오. 예를 들어, Apache httpd(`rhscl/httpd-*`), Python(`rhscl/python-*`), Ruby(`rhscl/ruby-*`), Node.js(`rhscl/nodejs-*`) 및 Perl(`rhscl/perl-*`) rhscl 이미지가 있습니다.

UBI 이미지는 자유롭게 재배포할 수 있지만 이러한 이미지에 대한 Red Hat 지원은 Red Hat 제품 서브스크립션을 통해서만 제공됩니다.

표준, 최소 및 init UBI 이미지에서 사용 및 빌드하는 방법에 대한 정보는 Red Hat Enterprise Linux 설명서에서 Red Hat Universal Base Images 를 참조하십시오.

#### 2.6.3. RHEL의 보안 스캔

RHEL(Red Hat Enterprise Linux) 시스템의 경우 OpenSCAP 스캔은 `openscap-utils` 패키지에서 사용할 수 있습니다. RHEL에서 `openscap-podman` 명령을 사용하여 이미지의 취약점을 스캔할 수 있습니다. Red Hat Enterprise Linux 설명서에서 컨테이너 및 컨테이너 이미지에서 취약점 스캔 을 참조하십시오.

OpenShift Container Platform을 사용하면 CI/CD 프로세스에서 RHEL 스캐너를 활용할 수 있습니다. 예를 들어 소스 코드의 보안 결함을 테스트하는 정적 코드 분석 툴과 오픈소스 라이브러리에서 알려진 취약점과 같은 메타데이터를 제공하기 위해 해당 라이브러리르 식별하는 소프트웨어 구성 분석 툴을 통합할 수 있습니다.

#### 2.6.3.1. OpenShift 이미지 스캔

OpenShift Container Platform에서 실행 중이고 Red Hat Quay 레지스트리에서 가져온 컨테이너 이미지의 경우 Operator를 사용하여 해당 이미지의 취약점을 나열할 수 있습니다. Red Hat Quay Container Security Operator 를 OpenShift Container Platform에 추가하여 선택한 네임스페이스에 추가된 이미지에 대한 취약점 보고를 제공할 수 있습니다.

Red Hat Quay의 컨테이너 이미지 스캔은 Clair 에서 수행합니다. Red Hat Quay에서 Clair는 RHEL, CentOS, Oracle, Alpine, Debian 및 Ubuntu 운영 체제 소프트웨어에서 빌드된 이미지의 취약점을 검색하고 보고할 수 있습니다.

#### 2.6.4. 외부 스캔 통합

OpenShift Container Platform은 오브젝트 주석 을 사용하여 기능을 확장합니다. 취약점 스캐너와 같은 외부 툴에서는 메타데이터로 이미지 오브젝트에 주석을 달아 결과를 요약하고 Pod 실행을 제어할 수 있습니다. 이 섹션에서는 이 주석의 인식된 형식을 설명하므로 유용한 데이터를 사용자에게 표시하기 위해 콘솔에서 안정적으로 사용할 수 있습니다.

#### 2.6.4.1. 이미지 메타데이터

패키지 취약점 및 오픈소스 소프트웨어(OSS) 라이센스 컴플라이언스를 포함하여 다양한 유형의 이미지 품질 데이터가 있습니다. 또한 이 메타데이터를 제공하는 공급자가 둘 이상일 수 있습니다. 이를 위해 다음 주석 형식이 예약되어 있습니다.

```plaintext
quality.images.openshift.io/<qualityType>.<providerId>: {}
```

| 구성요소 | 설명 | 허용 가능한 값 |
| --- | --- | --- |
| `qualityType` | 메타데이터 유형 | `vulnerability` `license` `operations` `policy` |
| `providerId` | 공급자 ID 문자열 | `openscap` `redhatcatalog` `redhatinsights` `blackduck` `jfrog` |

#### 2.6.4.1.1. 주석 키 예

```plaintext
quality.images.openshift.io/vulnerability.blackduck: {}
quality.images.openshift.io/vulnerability.jfrog: {}
quality.images.openshift.io/license.blackduck: {}
quality.images.openshift.io/vulnerability.openscap: {}
```

이미지 품질 주석의 값은 다음 형식을 준수해야 하는 구조화된 데이터입니다.

| 필드 | 필수 여부 | 설명 | 유형 |
| --- | --- | --- | --- |
| `name` | 예 | 공급자 표시 이름 | 문자열 |
| `timestamp` | 예 | 스캔 타임스탬프 | 문자열 |
| `description` | 아니요 | 짧은 설명 | 문자열 |
| `reference` | 예 | 정보 소스 또는 자세한 내용의 URL. 사용자가 데이터를 검증하려면 필수 | 문자열 |
| `scannerVersion` | 아니요 | 스캐너 버전 | 문자열 |
| `compliant` | 아니요 | 컴플라이언스 합격 또는 불합격 | 부울 |
| `summary` | 아니요 | 발견된 문제 요약 | 목록(아래 표 참조) |

`summary` 필드는 다음 형식을 준수해야 합니다.

| 필드 | 설명 | 유형 |
| --- | --- | --- |
| `label` | 구성요소의 표시 레이블(예: "심각", "중요", "중간", "낮음" 또는 "상태") | 문자열 |
| `data` | 이 구성요소의 데이터(예: 발견된 취약점 수 또는 점수) | 문자열 |
| `severityIndex` | 그래픽 표시의 순서를 지정하고 할당할 수 있는 구성요소 색인입니다. 값은 `0..3` 범위입니다. 여기서 `0` = 낮음입니다. | 정수 |
| `reference` | 정보 소스 또는 자세한 내용의 URL. 선택 사항입니다. | 문자열 |

#### 2.6.4.1.2. 주석 값 예

이 예에서는 취약성 요약 데이터 및 컴플라이언스 부울이 있는 이미지의 OpenSCAP 주석을 표시합니다.

```plaintext
{
  "name": "OpenSCAP",
  "description": "OpenSCAP vulnerability score",
  "timestamp": "2016-09-08T05:04:46Z",
  "reference": "https://www.open-scap.org/930492",
  "compliant": true,
  "scannerVersion": "1.2",
  "summary": [
    { "label": "critical", "data": "4", "severityIndex": 3, "reference": null },
    { "label": "important", "data": "12", "severityIndex": 2, "reference": null },
    { "label": "moderate", "data": "8", "severityIndex": 1, "reference": null },
    { "label": "low", "data": "26", "severityIndex": 0, "reference": null }
  ]
}
```

이 예에서는 추가 세부 사항의 외부 URL이 있는 상태 인덱스 데이터가 있는 이미지의 Red Hat Ecosystem Catalog의 컨테이너 이미지 섹션 주석을 표시합니다.

```plaintext
{
  "name": "Red Hat Ecosystem Catalog",
  "description": "Container health index",
  "timestamp": "2016-09-08T05:04:46Z",
  "reference": "https://access.redhat.com/errata/RHBA-2016:1566",
  "compliant": null,
  "scannerVersion": "1.2",
  "summary": [
    { "label": "Health index", "data": "B", "severityIndex": 1, "reference": null }
  ]
}
```

#### 2.6.4.2. 이미지 오브젝트에 주석 달기

이미지 스트림 오브젝트는 OpenShift Container Platform의 최종 사용자가 작동하는 대상인 반면, 이미지 오브젝트는 보안 메타데이터로 주석을 답니다. 이미지 오브젝트는 클러스터 범위에 있으며, 여러 이미지 스트림 및 태그에서 참조할 수 있는 단일 이미지를 가리킵니다.

#### 2.6.4.2.1. 주석 CLI 명령 예

`<image>` 를 이미지 다이제스트로 교체합니다(예: `sha256:401e359e0f45bfdcf004e258b72e253fd07fba8cc5c6f2ed4f4608fb119ecc2`).

```shell-session
$ oc annotate image <image> \
    quality.images.openshift.io/vulnerability.redhatcatalog='{ \
    "name": "Red Hat Ecosystem Catalog", \
    "description": "Container health index", \
    "timestamp": "2020-06-01T05:04:46Z", \
    "compliant": null, \
    "scannerVersion": "1.2", \
    "reference": "https://access.redhat.com/errata/RHBA-2020:2347", \
    "summary": "[ \
      { "label": "Health index", "data": "B", "severityIndex": 1, "reference": null } ]" }'
```

#### 2.6.4.3. Pod 실행 제어

`images.openshift.io/deny-execution` 이미지 정책을 사용하여 이미지 실행 가능 여부를 프로그래밍 방식으로 제어합니다.

#### 2.6.4.3.1. 주석 예

```yaml
annotations:
  images.openshift.io/deny-execution: true
```

#### 2.6.4.4. 통합 참조

대부분의 경우 취약점 스캐너와 같은 외부 툴은 이미지 업데이트를 감시하고 스캔을 수행하며 결과를 사용하여 관련 이미지 오브젝트에 주석을 추가하는 스크립트 또는 플러그인을 개발합니다. 일반적으로 이 자동화에서는 OpenShift Container Platform 4.20 REST API를 호출하여 주석을 작성합니다. REST API에 관한 일반 정보는 OpenShift Container Platform REST API를 참조하십시오.

#### 2.6.4.4.1. REST API 호출 예

다음 명령을 사용하는 다음 예제 호출은 주석의 값을 덮어씁니다. `<token>`, `<openshift_server>`, `<image_id>` 및 `<image_annotation>` 의 값을 교체하십시오.

```shell
curl
```

```shell-session
$ curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/merge-patch+json" \
  https://<openshift_server>:6443/apis/image.openshift.io/v1/images/<image_id> \
  --data '{ <image_annotation> }'
```

다음은 `PATCH` 페이로드 데이터의 예입니다.

```shell-session
{
"metadata": {
  "annotations": {
    "quality.images.openshift.io/vulnerability.redhatcatalog":
       "{ 'name': 'Red Hat Ecosystem Catalog', 'description': 'Container health index', 'timestamp': '2020-06-01T05:04:46Z', 'compliant': null, 'reference': 'https://access.redhat.com/errata/RHBA-2020:2347', 'summary': [{'label': 'Health index', 'data': '4', 'severityIndex': 1, 'reference': null}] }"
    }
  }
}
```

추가 리소스

이미지 스트림 오브젝트

### 2.7. 안전하게 컨테이너 레지스트리 사용

컨테이너 레지스트리는 컨테이너 이미지를 다음에 저장합니다.

다른 사용자가 이미지에 액세스하도록 허용

이미지를 여러 버전의 이미지를 포함할 수 있는 리포지토리로 구성

선택적으로 다른 인증 방법을 기반으로 이미지에 대한 액세스를 제한하거나 공개적으로 사용 가능하게 합니다.

많은 사람과 조직이 이미지를 공유하는 Quay.io 및 Docker Hub와 같은 공용 컨테이너 레지스트리가 있습니다. Red Hat Registry에서는 지원되는 Red Hat 및 파트너 이미지를 제공하는 반면, Red Hat Ecosystem Catalog에서는 해당 이미지에 관한 자세한 설명 및 상태 점검을 제공합니다. 자체 레지스트리를 관리하려면 Red Hat Quay 와 같은 컨테이너 레지스트리를 구매할 수 있습니다.

보안 관점에서 일부 레지스트리는 컨테이너의 상태를 확인하고 향상시키는 특수 기능을 제공합니다. 예를 들어 Red Hat Quay는 Clair 보안 스캐너를 사용하여 컨테이너 취약점 스캔, GitHub 및 기타 위치에서 소스 코드가 변경될 때 이미지를 자동으로 다시 빌드하는 빌드 트리거, 역할 기반 액세스 제어(RBAC)를 사용하여 이미지에 대한 액세스를 보호하는 기능을 제공합니다.

#### 2.7.1. 컨테이너의 출처를 알고 있습니까?

다운로드 및 배포된 컨테이너 이미지의 콘텐츠를 스캔하고 추적하는 데 사용할 수 있는 툴이 있습니다. 그러나 컨테이너 이미지의 공용 소스가 많이 있습니다. 공용 컨테이너 레지스트리를 사용하는 경우 신뢰할 수 있는 소스를 사용하여 보호 계층을 추가할 수 있습니다.

#### 2.7.2. 불변의 인증된 컨테이너

불변 컨테이너 를 관리할 때는 보안 업데이트를 사용하는 것이 특히 중요합니다. 불변 컨테이너는 실행 중에 변경되지 않는 컨테이너입니다. 불변 컨테이너를 배포할 때 하나 이상의 바이너리를 대체하기 위해 실행 중인 컨테이너로 들어가지 않습니다. 운영 관점에서 컨테이너를 변경하는 대신 업데이트된 컨테이너 이미지를 재빌드하고 재배포하여 컨테이너를 교체합니다.

Red Hat 인증 이미지는 다음과 같습니다.

플랫폼 구성 요소 또는 계층에 알려진 취약점이 없음

베어 메탈에서 클라우드까지 전체 RHEL 플랫폼에서 호환 가능

Red Hat에서 지원

알려진 취약점 목록은 지속적으로 늘어나므로 시간 경과에 따라 배포된 컨테이너 이미지의 콘텐츠와 새로 다운로드한 이미지의 콘텐츠를 추적해야 합니다. RHSA(Red Hat Security Advisories) 를 사용하여 Red Hat 인증 컨테이너 이미지에서 새로 발견된 문제를 경고하고 업데이트된 이미지로 안내할 수 있습니다. 또는 Red Hat Ecosystem Catalog로 이동하여 각 Red Hat 이미지에 관한 기타 보안 관련 문제를 조회할 수 있습니다.

#### 2.7.3. Red Hat Registry 및 Ecosystem Catalog에서 컨테이너 가져오기

Red Hat에서는 Red Hat Ecosystem Catalog의 컨테이너 이미지 섹션에서 Red Hat 제품 및 파트너 제품의 인증된 컨테이너 이미지를 나열합니다. 해당 카탈로그에서 CVE, 소프트웨어 패키지 목록 및 상태 점수를 포함하여 각 이미지의 세부 정보를 볼 수 있습니다.

Red Hat 이미지는 실제로 공개 컨테이너 레지스트리(`registry.access.redhat.com`) 및 인증된 레지스트리(`registry.redhat.io`)로 표시되는 Red Hat Registry 에 저장됩니다. 둘 다 기본적으로 동일한 컨테이너 이미지 세트를 포함하며 `registry.redhat.io` 에는 Red Hat 서브스크립션 인증서로 인증해야 하는 추가 이미지가 포함됩니다.

Red Hat에서 컨테이너 콘텐츠에 취약점이 있는지 모니터링하고 정기적으로 업데이트합니다. Red Hat에서 glibc, DROWN 또는 Dirty Cow 에 대한 수정 사항과 같은 보안 업데이트를 릴리스하면 영향을 받는 컨테이너 이미지도 다시 빌드되어 Red Hat Registry에 푸시됩니다.

Red Hat에서는 `상태 색인` 을 사용하여 Red Hat Ecosystem Catalog를 통해 제공되는 각 컨테이너의 보안 위험을 반영합니다. 컨테이너에서는 Red Hat과 에라타 프로세스에서 제공하는 소프트웨어를 사용하므로 오래되어 해지된 컨테이너는 안전하지 않은 반면 새로운 컨테이너는 더 안전합니다.

컨테이너의 수명을 설명하기 위해 Red Hat Ecosystem Catalog에서는 평가 시스템을 사용합니다. 최신 등급은 이미지에 사용 가능한 가장 오래되고 가장 심각한 보안 정오표 수치입니다. "A"는 "F"보다 최신입니다. 이 평가 시스템에 관한 자세한 내용은 Red Hat Ecosystem Catalog 내부에서 사용되는 컨테이너 상태 색인 등급 을 참조하십시오.

Red Hat 소프트웨어와 관련된 보안 업데이트 및 취약점에 관한 자세한 내용은 Red Hat 제품 보안 센터 를 확인하십시오. Red Hat Security Advisories 를 확인하여 특정 권고와 CVE를 검색하십시오.

#### 2.7.4. OpenShift Container Registry

OpenShift Container Platform에는 컨테이너 이미지를 관리하는 데 사용할 수 있는 플랫폼의 통합 구성요소로 실행되는 프라이빗 레지스트리인 OpenShift Container Registry 가 포함되어 있습니다. OpenShift Container Registry에서는 누가 어떤 컨테이너 이미지를 가져오고 푸시하는지 관리할 수 있는 역할 기반 액세스 제어를 제공합니다.

OpenShift Container Platform은 Red Hat Quay와 같이 이미 사용 중인 다른 프라이빗 레지스트리와의 통합도 지원합니다.

추가 리소스

통합된 OpenShift 이미지 레지스트리

#### 2.7.5. Red Hat Quay를 사용하여 컨테이너 저장

Red Hat Quay 는 Red Hat의 엔터프라이즈급 컨테이너 레지스트리 제품입니다. Red Hat Quay의 개발은 업스트림 프로젝트 Quay 를 통해 수행됩니다. Red Hat Quay는 온프레미스 또는 Quay.io 에서 호스팅된 Red Hat Quay 버전을 통해 배포할 수 있습니다.

Red Hat Quay의 보안 관련 기능은 다음과 같습니다.

타임 머신: 오래된 태그가 있는 이미지가 설정된 기간이 지난 후 만료되거나 사용자가 선택한 만료 시간에 따라 만료될 수 있습니다.

저장소 미러링: 회사 방화벽 뒤에서 Red Hat Quay의 공용 리포지토리를 호스트하거나 성능상의 이유로 다른 레지스트리를 미러링하여 레지스트리를 사용하는 위치에 더 가깝게 유지할 수 있습니다.

작업 로그 스토리지: Red Hat Quay 로깅 출력을 Elasticsearch 스토리지 또는 Splunk 에 저장하여 나중에 검색하고 분석할 수 있습니다.

Clair: 각 컨테이너 이미지의 출처를 기반으로 다양한 Linux 취약점 데이터베이스에 대해 이미지를 스캔합니다.

내부 인증: 기본 로컬 데이터베이스를 사용하여 Red Hat Quay에 대한 RBAC 인증을 처리하거나 LDAP, Keystone(OpenStack), JWT 사용자 정의 인증 또는 외부 애플리케이션 토큰 인증 중에서 선택합니다.

외부 인증(OAuth): GitHub, GitHub Enterprise 또는 Google 인증에서 Red Hat Quay에 대한 인증을 허용합니다.

액세스 설정: docker, rkt, anonymous 액세스, 사용자 생성 계정, 암호화된 클라이언트 암호 또는 접두사 사용자 이름 자동 완성에서 Red Hat Quay에 액세스할 수 있도록 토큰을 생성합니다.

OpenShift Container Platform과 Red Hat Quay의 지속적인 통합은 특히 관심이 있는 여러 OpenShift Container Platform Operator와 계속 통합됩니다. Quay Bridge Operator 를 사용하면 내부 OpenShift 이미지 레지스트리를 Red Hat Quay로 교체할 수 있습니다. Red Hat Quay Container Security Operator 를 사용하면 Red Hat Quay 레지스트리에서 가져온 OpenShift Container Platform에서 실행되는 이미지의 취약점을 확인할 수 있습니다.

### 2.8. 빌드 프로세스 보안

컨테이너 환경에서 소프트웨어 빌드 프로세스는 애플리케이션 코드가 필수 런타임 라이브러리와 통합되는 라이프사이클의 단계입니다. 이 빌드 프로세스 관리는 소프트웨어 스택을 보호하는 데 핵심입니다.

#### 2.8.1. 한 번 빌드하여 어디에나 배포

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/trustedsupplychain.png" alt="trustedsupplychain" kind="figure" diagram_type="image_figure"]
trustedsupplychain
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/fb24f4bab3af9ca7be8bfa0c17e69e1a/trustedsupplychain.png`_


컨테이너 빌드를 위한 표준 플랫폼으로 OpenShift Container Platform을 사용하면 빌드 환경의 보안을 보장할 수 있습니다. "한 번만 빌드하여 어디에나 배포" 철학을 준수하면 빌드 프로세스의 제품을 프로덕션에 정확히 배포할 수 있습니다.

컨테이너의 불변성을 유지 관리하는 것도 중요합니다. 실행 중인 컨테이너에 패치를 적용하지 말고 다시 빌드하여 재배치해야 합니다.

소프트웨어가 빌드, 테스트 및 프로덕션 단계를 진행해 갈 때 소프트웨어 공급망을 구성하는 툴을 신뢰하는 것이 중요합니다. 다음 그림에서는 컨테이너화된 소프트웨어를 위한 신뢰할 수 있는 소프트웨어 공급망에 통합될 수 있는 프로세스와 툴을 보여줍니다.

OpenShift Container Platform은 신뢰할 수 있는 코드 리포지토리(예: GitHub) 및 개발 플랫폼(예: Che)과 통합되어 보안 코드를 생성하고 관리할 수 있습니다. 단위 테스트에서는 Cucumber 및 JUnit 을 사용합니다.

Red Hat Advanced Cluster Security for Kubernetes 를 사용하여 빌드, 배포 또는 런타임에 컨테이너의 취약점 및 구성 문제를 검사할 수 있습니다. Quay에 저장된 이미지의 경우 Clair 스캐너 를 사용하여 미사용 이미지를 검사할 수 있습니다. 또한 Red Hat 에코시스템 카탈로그에는 인증된 취약점 스캐너 를 사용할 수 있습니다.

Sysdig 와 같은 툴은 컨테이너화된 애플리케이션을 지속적으로 모니터링할 수 있습니다.

#### 2.8.2. 빌드 관리

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/build_process1.png" alt="소스-이미지 빌드" kind="figure" diagram_type="image_figure"]
소스-이미지 빌드
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/e0638ed7f3db92b8ace1aaa85ef6acd8/build_process1.png`_


S2I(Source-to-Image)를 사용하여 소스 코드와 기본 이미지를 결합할 수 있습니다. 빌더 이미지 는 S2I를 사용하므로 개발 및 운영 팀이 재현 가능한 빌드 환경에서 협업할 수 있습니다. UBI(Universal Base Image) 이미지로 사용 가능한 Red Hat S2I 이미지를 사용하면 실제 RHEL RPM 패키지에서 빌드된 기본 이미지로 소프트웨어를 자유롭게 재배포할 수 있습니다. Red Hat에서는 이를 허용하기 위해 서브스크립션 제한 사항을 제거했습니다.

개발자가 빌드 이미지를 사용하여 애플리케이션용 Git로 코드를 커밋하면 OpenShift Container Platform에서는 다음 기능을 수행할 수 있습니다.

사용 가능한 아티팩트, S2I 빌더 이미지 및 새로 커밋된 코드에서 자동으로 새 이미지를 어셈블링하기 위해 코드 리포지토리의 웹 후크를 사용하거나 기타 자동 연속 통합(CI) 프로세스를 사용하여 트리거합니다.

테스트를 위해 새로 빌드된 이미지를 자동으로 배포합니다.

테스트된 이미지를 CI 프로세스를 사용하여 자동으로 배포할 수 있는 프로덕션으로 승격합니다.

통합 OpenShift Container Registry를 사용하여 최종 이미지에 대한 액세스를 관리할 수 있습니다. S2I 및 기본 빌드 이미지가 자동으로 OpenShift Container Registry로 푸시됩니다.

포함된 Jenkins for CI 외에도 RESTful API를 사용하여 자체 빌드 및 CI 환경을 OpenShift Container Platform과 통합하고 API 호환 이미지 레지스트리를 사용할 수 있습니다.

#### 2.8.3. 빌드 중 입력 보안

일부 시나리오에서는 빌드 작업을 할 때 종속 리소스에 액세스하기 위한 인증서가 필요하지만 빌드에서 생성한 최종 애플리케이션 이미지에서 해당 인증서가 사용 가능한 것은 바람직하지 않습니다. 이 목적을 위해 입력 보안을 정의할 수 있습니다.

예를 들어 Node.js 애플리케이션을 빌드할 때 Node.js 모듈에 맞게 개인용 미러를 설정할 수 있습니다. 이 개인용 미러에서 모듈을 다운로드하려면 URL, 사용자 이름 및 암호가 포함된 빌드에 사용할 사용자 정의 `.npmrc` 파일을 제공해야 합니다. 보안상의 이유로 애플리케이션 이미지에 자격 증명을 노출해서는 안 됩니다.

이 예제 시나리오를 사용하여 새 `BuildConfig` 오브젝트에 입력 보안을 추가할 수 있습니다.

프로세스

보안이 없으면 다음과 같이 생성합니다.

```shell-session
$ oc create secret generic secret-npmrc --from-file=.npmrc=~/.npmrc
```

그러면 `~/.npmrc` 파일의 base64 인코딩 콘텐츠를 포함하는 `secret-npmrc` 라는 새 보안이 생성됩니다.

다음과 같이 기존 `BuildConfig` 오브젝트의 `source` 섹션에 보안을 추가합니다.

```yaml
source:
  git:
    uri: https://github.com/sclorg/nodejs-ex.git
  secrets:
  - destinationDir: .
    secret:
      name: secret-npmrc
```

새 `BuildConfig` 오브젝트에 보안을 포함하려면 다음 명령을 실행합니다.

```shell-session
$ oc new-build \
    openshift/nodejs-010-centos7~https://github.com/sclorg/nodejs-ex.git \
    --build-secret secret-npmrc
```

#### 2.8.4. 빌드 프로세스 설계

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/build_process2.png" alt="빌드 프로세스 설계" kind="figure" diagram_type="image_figure"]
빌드 프로세스 설계
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/02f7a10ce12e6eda9fdb2b08ff589754/build_process2.png`_


개별적으로 제어할 수 있도록 컨테이너 이미지 관리를 설계하고 컨테이너 계층을 사용하도록 프로세스를 구축할 수 있습니다.

예를 들어, 운영 팀은 기본 이미지를 관리하는 반면 아키텍트는 미들웨어, 런타임, 데이터베이스 및 기타 솔루션을 관리합니다. 그런 다음 개발자는 애플리케이션 계층과 코드 작성에 중점을 둘 수 있습니다.

매일 새로운 취약점이 식별되므로 시간 경과에 따라 컨테이너 콘텐츠를 사전 대응식으로 확인해야 합니다. 이를 위해서는 자동화된 보안 테스트를 빌드 또는 CI 프로세스에 통합해야 합니다. 예를 들면 다음과 같습니다.

SAST/DAST – 정적 및 동적 보안 테스트 도구.

알려진 취약점과 비교하여 실시간 검사를 위한 스캐너. 이러한 툴을 통해서는 컨테이너의 오픈소스 패키지를 카탈로그화하고 알려진 취약점을 사용자에게 알리며 이전에 스캔한 패키지에서 새로운 취약점이 발견되면 사용자에게 이 내용을 업데이트합니다.

CI 프로세스에는 보안 스캔에서 발견된 문제로 빌드에 플래그를 표시하는 정책이 포함되어 있으므로, 팀이 해당 문제를 해결하기 위해 적절한 조치를 취할 수 있습니다. 빌드와 배포 사이에 아무것도 변경되지 않도록 사용자 정의 빌드 컨테이너에 서명해야 합니다.

GitOps 방법론을 사용하면 동일한 CI/CD 메커니즘을 사용하여 애플리케이션 구성뿐만 아니라 OpenShift Container Platform 인프라를 관리할 수 있습니다.

#### 2.8.5. Knative 서버리스 애플리케이션 빌드

Kubernetes 및 Kourier를 사용하면 OpenShift Container Platform에서 OpenShift Serverless를 사용하여 서버리스 애플리케이션을 빌드, 배포 및 관리할 수 있습니다.

다른 빌드와 마찬가지로 S2I 이미지를 사용하여 컨테이너를 빌드한 다음 Knative 서비스를 사용하여 컨테이너를 제공할 수 있습니다. OpenShift Container Platform 웹 콘솔의 토폴로지 보기를 통해 Knative 애플리케이션 빌드를 봅니다.

#### 2.8.6. 추가 리소스

이미지 빌드 이해

빌드 트리거 및 수정

빌드 입력 생성

입력 보안 및 구성 맵

OpenShift Serverless 개요

토폴로지 보기를 사용하여 애플리케이션 구성 보기

### 2.9. 컨테이너 배포

사용자가 배포한 컨테이너가 최신 프로덕션 품질의 콘텐츠를 보유하고 있으며 변경되지 않았는지 다양한 기술을 사용하여 확인할 수 있습니다. 이러한 기술에는 최신 코드를 통합하도록 빌드 트리거를 설정하는 것과 서명을 사용하여 컨테이너가 신뢰할 수 있는 소스에서 제공되었으며 수정되지 않았는지 확인하는 것이 포함됩니다.

#### 2.9.1. 트리거를 사용하여 컨테이너 배포 제어

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/secure_deployments.png" alt="안전한 배포" kind="figure" diagram_type="image_figure"]
안전한 배포
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/58398ce097ac705459624130e73c1082/secure_deployments.png`_


빌드 프로세스 중에 문제가 발생하거나 이미지가 배포된 후 취약점이 발견되면 자동화된 정책 기반 배포 도구를 사용하여 문제를 해결할 수 있습니다. 실행 중인 컨테이너에 패치를 적용하는 것이 아니라, 트리거를 사용하여 이미지를 다시 빌드하고 교체함으로써 컨테이너 프로세스가 변경되지 않게 할 수 있습니다.

예를 들어 코어, 미들웨어 및 애플리케이션의 세 가지 컨테이너 이미지 계층을 사용하여 애플리케이션을 빌드합니다. 핵심 이미지에서 문제가 발견되고 해당 이미지가 다시 빌드됩니다. 빌드가 완료되면 이미지가 OpenShift Container Registry로 푸시됩니다. OpenShift Container Platform에서 이미지가 변경되었음을 감지하고 정의된 트리거를 기반으로 애플리케이션 이미지를 자동으로 재빌드하고 배포합니다. 이 변경은 고정 라이브러리를 통합하고 프로덕션 코드가 최신 이미지와 동일하게 합니다.

아래 명령을 사용하여 배포 트리거를 설정할 수 있습니다. 예를 들어 deployment-example이라는 배포용 트리거를 설정하려면 다음을 수행합니다.

```shell
oc set triggers
```

```shell-session
$ oc set triggers deploy/deployment-example \
    --from-image=example:latest \
    --containers=web
```

#### 2.9.2. 배포할 수 있는 이미지 소스 제어

원하는 이미지가 실제로 배포되고 포함된 콘텐츠를 포함하는 이미지가 신뢰할 수 있는 소스의 이미지이며 변경되지 않은 것이 중요합니다. 암호화 서명을 사용하면 이를 보장할 수 있습니다. OpenShift Container Platform을 사용하면 클러스터 관리자는 배포 환경 및 보안 요구 사항을 반영하여 광범위하거나 한정된 보안 정책을 적용할 수 있습니다. 이 정책을 정의하는 매개변수는 다음 두 가지입니다.

선택적 프로젝트 네임스페이스가 있는 레지스트리 하나 이상

공개 키 수락, 거부 또는 필수와 같은 신뢰 유형

이러한 정책 매개변수를 사용하여 전체 레지스트리, 레지스트리 일부 또는 개별 이미지의 신뢰 관계를 허용, 거부 또는 필수로 지정할 수 있습니다. 신뢰할 수 있는 공개 키를 사용하면 암호화 방식으로 소스를 확인할 수 있습니다. 정책 규칙은 노드에 적용됩니다. 정책은 모든 노드에 균일하게 적용되거나 다른 노드 워크로드(예: 빌드, 영역 또는 환경)를 대상으로 할 수 있습니다.

```plaintext
{
    "default": [{"type": "reject"}],
    "transports": {
        "docker": {
            "access.redhat.com": [
                {
                    "type": "signedBy",
                    "keyType": "GPGKeys",
                    "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
                }
            ]
        },
        "atomic": {
            "172.30.1.1:5000/openshift": [
                {
                    "type": "signedBy",
                    "keyType": "GPGKeys",
                    "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
                }
            ],
            "172.30.1.1:5000/production": [
                {
                    "type": "signedBy",
                    "keyType": "GPGKeys",
                    "keyPath": "/etc/pki/example.com/pubkey"
                }
            ],
            "172.30.1.1:5000": [{"type": "reject"}]
        }
    }
}
```

정책은 `/etc/containers/policy.json` 으로 노드에 저장될 수 있습니다. 이 파일을 노드에 저장할 때는 새로운 `MachineConfig` 오브젝트를 사용하는 것이 가장 좋습니다. 이 예에서는 다음 규칙을 적용합니다.

Red Hat 공개 키로 Red Hat Registry(`registry.access.redhat.com`)의 이미지에 서명해야 합니다.

`openshift` 네임스페이스에 있는 OpenShift Container Registry의 이미지에 Red Hat 공개 키로 서명해야 합니다.

`production` 네임스페이스에 있는 OpenShift Container Registry의 이미지에 `example.com` 의 공개 키로 서명해야 합니다.

글로벌 `default` 정의로 지정되지 않은 다른 모든 레지스트리는 거부됩니다.

#### 2.9.3. 서명 전송 사용

서명 전송은 바이너리 서명 Blob을 저장하고 검색하는 방법입니다. 서명 전송의 유형은 다음 두 가지입니다.

`atomic`: OpenShift Container Platform API에서 관리합니다.

다음 명령: 로컬 파일로 제공되거나 웹 서버를 통해 제공됩니다.

```shell
docker
```

OpenShift Container Platform API는 `atomic` 전송 유형을 사용하는 서명을 관리합니다. 이 서명 유형을 사용하는 이미지를 OpenShift 컨테이너 레지스트리에 저장해야 합니다. docker/distribution `extensions` API에서 이미지 서명 끝점을 자동 검색하므로 추가 구성이 필요하지 않습니다.

다음 명령전송 유형을 사용하는 서명은 로컬 파일 또는 웹 서버에서 제공합니다. 이 서명은 더 유연합니다. 컨테이너 이미지 레지스트리에서 이미지를 제공하고 독립 서버를 사용하여 바이너리 서명을 제공할 수 있습니다.

```shell
docker
```

그러나 전송 유형에는 추가 구성이 필요합니다. 임의로 이름이 지정된 YAML 파일을 기본적으로 호스트 시스템의 디렉터리인 `/etc/containers/registries.d` 에 배치하여 서명 서버의 URI로 노드를 구성해야 합니다. YAML 구성 파일에는 레지스트리 URI 및 서명 서버 URI 또는 sigstore 가 포함되어 있습니다.

```shell
docker
```

```yaml
docker:
    access.redhat.com:
        sigstore: https://access.redhat.com/webassets/docker/content/sigstore
```

이 예에서 Red Hat Registry, `access.redhat.com` 은 전송 유형의 서명을 제공하는 서명 서버입니다. 해당 URI는 `sigstore` 매개변수에 정의되어 있습니다. 이 파일의 이름을 `/etc/containers/registries.d/redhat.com.yam` 로 지정하고 Machine Config Operator를 사용하여 파일을 클러스터의 각 노드에 자동으로 배치합니다. 정책 및 `registries.d` 파일은 컨테이너 런타임을 통해 동적으로 로드되므로 서비스를 다시 시작할 필요가 없습니다.

```shell
docker
```

#### 2.9.4. 보안 및 구성 맵 생성

`Secret` 오브젝트 유형에서는 암호, OpenShift Container Platform 클라이언트 구성 파일, `dockercfg` 파일, 개인 소스 리포지토리 인증서와 같은 중요한 정보를 보유하는 메커니즘을 제공합니다. 보안은 Pod에서 민감한 콘텐츠를 분리합니다. 볼륨 플러그인을 사용하여 컨테이너에 보안을 마운트하거나 시스템에서 시크릿을 사용하여 Pod 대신 작업을 수행할 수 있습니다.

예를 들어 개인 이미지 리포지토리에 액세스할 수 있도록 배치 구성에 보안을 추가하려면 다음을 수행하십시오.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

새 프로젝트를 생성합니다.

리소스 → 보안 으로 이동하여 새 보안을 생성합니다. `보안 유형` 을 `이미지 보안` 으로 설정하고 `인증 유형` 을 `이미지 레지스트리 인증서` 로 설정하여 개인 이미지 리포지토리에 액세스하는 데 사용할 인증서를 입력합니다.

배포 구성을 생성할 때(예: 프로젝트에 추가 → 이미지 배포 페이지) `가져오기 보안` 을 새 보안으로 설정합니다.

구성 맵은 보안과 유사하지만 민감한 정보가 포함되지 않은 문자열 작업을 지원하도록 설계되었습니다. `ConfigMap` 오브젝트에는 Pod에서 사용하거나 컨트롤러와 같은 시스템 구성 요소의 구성 데이터를 저장하는 데 사용할 수 있는 구성 데이터의 키-값 쌍이 있습니다.

#### 2.9.5. 지속적인 배포 자동화

OpenShift Container Platform과 연속 배포(CD) 툴링을 통합할 수 있습니다.

CI/CD 및 OpenShift Container Platform을 활용하면 최신 수정 사항을 통합하기 위해 애플리케이션을 재빌드하고 테스트한 다음 환경 내 모든 위치에 배포되었는지 확인하는 프로세스를 자동화할 수 있습니다.

추가 리소스

입력 보안 및 구성 맵

### 2.10. 컨테이너 플랫폼 보안

OpenShift Container Platform 및 쿠버네티스 API는 대규모 컨테이너 관리 자동화의 핵심입니다. API는 다음을 수행하는 데 사용됩니다.

Pod, 서비스 및 복제 컨트롤러의 데이터를 검증하고 구성합니다.

수신 요청에서 프로젝트의 유효성을 확인하고 다른 주요 시스템 구성요소에서 트리거를 호출합니다.

쿠버네티스를 기반으로 하는 OpenShift Container Platform의 보안 관련 기능은 다음과 같습니다.

역할 기반 액세스 제어 및 네트워크 정책을 결합하여 컨테이너를 여러 수준으로 격리하는 멀티 테넌시.

API와 API에 요청하는 규칙 사이의 경계를 형성하는 승인 플러그인입니다.

OpenShift Container Platform에서는 Operator를 사용하여 쿠버네티스 수준 보안 기능 관리를 자동화하고 단순화합니다.

#### 2.10.1. 멀티 테넌시로 컨테이너 격리

다중 테넌트를 사용하면 여러 사용자가 소유하고 여러 호스트와 네임스페이스에서 실행되는 OpenShift Container Platform 클러스터의 애플리케이션을 서로 분리하고 외부 공격으로부터 격리된 상태로 유지할 수 있습니다. 쿠버네티스 네임스페이스에 역할 기반 액세스 제어(RBAC)를 적용하여 멀티 테넌시를 확보합니다.

쿠버네티스에서 네임스페이스 는 다른 애플리케이션과 분리된 방식으로 애플리케이션을 실행할 수 있는 영역입니다. OpenShift Container Platform에서는 SELinux에서 MCS 레이블링을 포함하여 주석을 추가하고 이러한 확장 네임스페이스를 프로젝트 로 식별하여 네임스페이스를 사용하고 확장합니다. 프로젝트 범위 내에서 서비스 계정, 정책, 제약 조건 및 기타 다양한 오브젝트를 포함하여 자체 클러스터 리소스를 유지 관리할 수 있습니다.

선택된 사용자가 프로젝트에 액세스할 수 있도록 RBAC 오브젝트가 해당 프로젝트에 할당됩니다. 이 인증에서는 규칙, 역할 및 바인딩 양식을 사용합니다.

규칙을 통해서는 사용자가 프로젝트에서 생성하거나 액세스할 수 있는 대상을 정의합니다.

역할은 선택한 사용자 또는 그룹에 바인딩할 수 있는 규칙 컬렉션입니다.

바인딩을 통해서는 사용자 또는 그룹과 역할 간의 연결을 정의합니다.

로컬 RBAC 역할 및 바인딩은 사용자 또는 그룹을 특정 프로젝트에 연결합니다. 클러스터 RBAC는 클러스터 전체 역할 및 바인딩을 클러스터의 모든 프로젝트에 연결할 수 있습니다. `admin`, `basic-user`, `cluster-admin` 및 `cluster-status` 액세스를 제공하기 위해 지정할 수 있는 기본 클러스터 역할이 있습니다.

#### 2.10.2. 승인 플러그인으로 컨트롤 플레인 보호

RBAC는 사용자와 그룹 간의 액세스 규칙을 제어하지만 승인 플러그인 은 OpenShift Container Platform 마스터 API에 대한 액세스를 정의합니다. 승인 플러그인은 다음으로 구성된 규칙 체인을 형성합니다.

기본 승인 플러그인: OpenShift Container Platform 컨트롤 플레인의 구성 요소에 적용되는 기본 정책 및 리소스 제한 세트를 구현합니다.

변경 승인 플러그인: 이 플러그인은 승인 체인을 동적으로 확장합니다. 이 플러그인은 웹 후크 서버를 호출하고 요청을 인증하며 선택된 리소스를 수정할 수 있습니다.

승인 플러그인 검증: 선택한 리소스에 대한 요청을 검증하고 요청을 검증하고 리소스가 다시 변경되지 않는지 확인할 수 있습니다.

API 요청은 체인의 승인 플러그인을 통과하며 실패로 인해 요청이 거부됩니다. 각 승인 플러그인은 특정 리소스와 연결되어 있으며 해당 리소스에 대한 요청에만 응답합니다.

#### 2.10.2.1. SCC(보안 컨텍스트 제약 조건)

SCC(보안 컨텍스트 제약 조건)를 사용하여 시스템에 적용하기 위해 Pod를 실행해야 하는 조건 집합을 정의할 수 있습니다.

SCC에서 관리할 수 있는 몇 가지 요소는 다음과 같습니다.

권한이 있는 컨테이너 실행

컨테이너가 추가하도록 요청할 수 있는 기능

호스트 디렉터리를 볼륨으로 사용

컨테이너의 SELinux 컨텍스트

컨테이너 사용자 ID

필수 권한이 있으면 필요한 경우 기본 SCC 정책의 허용 범위를 넓게 조정할 수 있습니다.

#### 2.10.2.2. 서비스 계정에 역할 부여

사용자에게 역할 기반 액세스 권한이 할당된 방식과 동일하게 서비스 계정에 역할을 할당할 수 있습니다. 프로젝트마다 3개의 기본 서비스 계정이 생성됩니다. 서비스 계정:

특정 프로젝트로 범위가 제한됨

프로젝트에서 이름 파생

OpenShift Container Registry에 액세스하기 위해 API 토큰 및 인증서가 자동으로 할당됨

플랫폼 구성요소와 관련된 서비스 계정의 키는 자동으로 순환됩니다.

#### 2.10.3.1. OAuth를 사용하여 액세스 제어

컨테이너 플랫폼 보안을 위해 인증 및 권한 부여를 통해 API 액세스 제어를 사용할 수 있습니다. OpenShift Container Platform 마스터에는 내장 OAuth 서버가 포함되어 있습니다. 사용자가 API에 자신을 인증하기 위해 OAuth 액세스 토큰을 가져올 수 있습니다.

관리자는 LDAP, GitHub 또는 Google과 같은 ID 공급자 를 사용하여 인증할 OAuth를 구성할 수 있습니다. ID 공급자는 기본적으로 새 OpenShift Container Platform 배포에 사용되지만 초기 설치 시 또는 설치 후 이 공급자를 구성할 수 있습니다.

#### 2.10.3.2. API 액세스 제어 및 관리

애플리케이션에는 관리가 필요한 끝점이 서로 다른 여러 개의 독립적인 API 서비스가 있을 수 있습니다. OpenShift Container Platform에는 3scale API 게이트웨이의 컨테이너화된 버전이 포함되어 있으므로 API를 관리하고 액세스를 제어할 수 있습니다.

3scale에서는 API 인증 및 보안을 위한 다양한 표준 옵션을 제공합니다. 이 옵션은 표준 API 키, 애플리케이션 ID와 키 쌍 및 OAuth 2.0과 함께 인증서를 발행하고 액세스를 제어하기 위해 조합하여 사용하거나 단독으로 사용할 수 있습니다.

특정 끝점, 방법 및 서비스에 대한 액세스를 제한하고 사용자 그룹의 액세스 정책을 적용할 수 있습니다. 애플리케이션 계획을 통해 API 사용에 대한 속도 제한을 설정하고 개발자 그룹의 트래픽 흐름을 제어할 수 있습니다.

컨테이너화된 3scale API 게이트웨이인 APIcast v2를 사용하는 방법에 관한 자습서는 3scale 설명서의 Red Hat OpenShift에서 APIcast 실행 을 참조하십시오.

#### 2.10.3.3. Red Hat Single Sign-On

Red Hat Single Sign-On 서버를 사용하면 SAML 2.0, OpenID Connect 및 OAuth 2.0을 포함한 표준을 기반으로 웹 싱글 사인온 기능을 제공하여 애플리케이션을 보호할 수 있습니다. 서버는 SAML 또는 OpenID Connect 기반 ID 공급자(IdP)의 역할을 하며 엔터프라이즈 사용자 디렉터리 또는 타사 ID 공급자와 함께 표준 기반 토큰을 사용하여 ID 정보 및 애플리케이션을 중재할 수 있습니다. Red Hat Single Sign-On을 Microsoft Active Directory 및 Red Hat Enterprise Linux Identity Management를 포함한 LDAP 기반 디렉터리 서비스와 통합할 수 있습니다.

#### 2.10.3.4. 보안 셀프 서비스 웹 콘솔

OpenShift Container Platform에서는 팀이 권한없이 다른 환경에 액세스하지 못하도록 셀프 서비스 웹 콘솔을 제공합니다. OpenShift Container Platform에서는 다음을 제공하여 보안 멀티 테넌트 마스터를 보장합니다.

마스터에 액세스하는 데 TLS(Transport Layer Security)를 사용합니다.

API 서버에 액세스하는 데 X.509 인증서 또는 OAuth 액세스 토큰을 사용합니다.

프로젝트에 할당량을 지정하면 불량 토큰으로 인한 피해가 제한됩니다

etcd 서비스는 클러스터에 직접 노출되지 않습니다

#### 2.10.4. 플랫폼의 인증서 관리

OpenShift Container Platform의 프레임워크에는 TLS 인증서를 통한 암호화를 활용하는 REST 기반 HTTPS 통신을 사용하는 여러 구성요소가 있습니다. OpenShift Container Platform의 설치 관리자는 설치 중에 이러한 인증서를 구성합니다. 이 트래픽을 생성하는 몇 가지 기본 구성요소가 있습니다.

마스터(API 서버 및 컨트롤러)

etcd

노드

레지스트리

라우터

#### 2.10.4.1. 사용자 정의 인증서 구성

초기 설치 중 또는 인증서를 재배포할 때 API 서버와 웹 콘솔의 공개 호스트 이름에 맞게 사용자 정의 제공 인증서를 구성할 수 있습니다. 사용자 정의 CA도 사용할 수 있습니다.

추가 리소스

OpenShift Container Platform 소개

RBAC를 사용하여 권한 정의 및 적용

승인 플러그인 정보

보안 컨텍스트 제약 조건 관리

SCC 참조 명령

서비스 계정에 역할을 부여하는 예

내부 OAuth 서버 구성

ID 공급자 구성 이해

인증서 유형 및 설명

프록시 인증서

### 2.11. 네트워크 보안

네트워크 보안은 여러 수준에서 관리할 수 있습니다. Pod 수준에서 네트워크 네임스페이스는 네트워크 액세스를 제한하여 컨테이너에 다른 Pod 또는 호스트 시스템이 표시되지 않게 할 수 있습니다. 네트워크 정책을 통해 연결을 허용하거나 거부할 수 있습니다. 컨테이너화된 애플리케이션으로 수신 및 송신되는 트래픽을 관리할 수 있습니다.

#### 2.11.1. 네트워크 네임스페이스 사용

OpenShift Container Platform에서는 소프트웨어 정의 네트워킹(SDN)을 사용하여 클러스터 전체의 컨테이너 간 통신이 가능한 통합 클러스터 네트워크를 제공합니다.

기본적으로 네트워크 정책 모드에서는 다른 Pod 및 네트워크 끝점에서 프로젝트의 모든 Pod에 액세스 할 수 있습니다. 프로젝트에서 하나 이상의 Pod를 분리하기 위해 해당 프로젝트에서 `NetworkPolicy` 오브젝트를 생성하여 수신되는 연결을 표시할 수 있습니다. 다중 테넌트 모드를 사용하면 Pod 및 서비스에 대한 프로젝트 수준 격리를 제공할 수 있습니다.

#### 2.11.2. 네트워크 정책으로 Pod 분리

네트워크 정책 을 사용하면 동일한 프로젝트에서 Pod를 서로 분리할 수 있습니다. 네트워크 정책은 Pod에 대한 모든 네트워크 액세스를 거부하거나 Ingress 컨트롤러의 연결만 허용하거나, 다른 프로젝트의 Pod의 연결을 거부하거나, 네트워크 작동 방식에 대한 유사한 규칙을 설정할 수 있습니다.

추가 리소스

네트워크 정책 정의

#### 2.11.3. 여러 Pod 네트워크 사용

실행 중인 각 컨테이너에는 기본적으로 하나의 네트워크 인터페이스만 있습니다. Multus CNI 플러그인을 사용하면 여러 CNI 네트워크를 생성한 다음 해당 네트워크를 Pod에 연결할 수 있습니다. 이렇게 하면 개인 데이터를 더 제한된 네트워크로 분리할 수 있으며 노드마다 네트워크 인터페이스가 여러 개일 수 있습니다.

추가 리소스

여러 네트워크 사용

#### 2.11.4. 애플리케이션 격리

OpenShift Container Platform을 사용하면 단일 클러스터에서 네트워크 트래픽을 세그먼트화하여 사용자, 팀, 애플리케이션 및 환경을 글로벌이 아닌 리소스와 분리하는 다중 테넌트 클러스터를 만들 수 있습니다.

#### 2.11.5. 수신 트래픽 보안

OpenShift Container Platform 클러스터 외부에서 쿠버네티스 서비스에 대한 액세스를 구성하는 방법과 관련하여 보안에 미치는 영향이 많이 있습니다. HTTP 및 HTTPS 경로를 노출하는 외에도 수신 라우팅을 사용하면 NodePort 또는 LoadBalancer 수신 유형을 설정할 수 있습니다. NodePort에서는 각 클러스터 작업자의 애플리케이션 서비스 API 오브젝트를 노출합니다. LoadBalancer를 사용하면 OpenShift Container Platform 클러스터의 관련 서비스 API 오브젝트에 외부 로드 밸런서를 할당할 수 있습니다.

추가 리소스

수신 클러스터 트래픽 구성

#### 2.11.6. 송신 트래픽 보안

OpenShift Container Platform에서는 라우터 또는 방화벽 방법을 사용하여 송신 트래픽을 제어하는 기능을 제공합니다. 예를 들어 IP 허용 목록을 사용하여 데이터베이스 액세스를 제어할 수 있습니다. 클러스터 관리자는 송신 IP 주소를 구성하여 프로젝트에 하나 이상의 송신 IP 주소를 할당할 수 있습니다. 마찬가지로 클러스터 관리자는 송신 방화벽을 사용하여 송신 트래픽이 OpenShift Container Platform 클러스터 외부로 나가는 것을 방지할 수 있습니다.

고정 송신 IP 주소를 할당하면 특정 프로젝트용으로 나가는 모든 트래픽을 해당 IP 주소에 할당할 수 있습니다. 송신 방화벽을 사용하면 Pod가 외부 네트워크에 연결 또는 Pod가 내부 네트워크에 연결하는 것을 방지하거나 특정 내부 서브넷에 대한 Pod의 액세스를 제한할 수 있습니다.

추가 리소스

프로젝트에 대한 송신 방화벽 구성

IPsec 암호화 구성

### 2.12. 연결된 스토리지 보안

OpenShift Container Platform에서는 온프레미스 및 클라우드 공급자를 위해 여러 유형의 스토리지를 지원합니다. 특히 OpenShift Container Platform에서는 컨테이너 스토리지 인터페이스를 지원하는 스토리지 유형을 사용할 수 있습니다.

#### 2.12.1. 영구 볼륨 플러그인

컨테이너는 스테이트리스(stateless) 및 스테이트풀(stateful) 애플리케이션 둘 다에 유용합니다. 연결된 스토리지를 보호하는 것이 상태 저장 서비스 보안의 핵심 요소입니다. CSI(Container Storage Interface)를 사용하여 OpenShift Container Platform에서는 CSI 인터페이스를 지원하는 모든 스토리지 백엔드의 스토리지를 통합할 수 있습니다.

OpenShift Container Platform은 다음을 포함하여 여러 유형의 스토리지에 대한 플러그인을 제공합니다.

Red Hat OpenShift Data Foundation*

AWS EBS(Elastic Block Stores)*

AWS EFS(Elastic File System)*

Azure 디스크*

Azure 파일*

OpenStack Cinder*

GCE 영구 디스크*

VMware vSphere*

네트워크 파일 시스템(NFS)

FlexVolume

파이버 채널

iSCSI

동적 프로비저닝이 있는 스토리지 유형의 플러그인은 별표(*)로 표시됩니다. 서로 통신 중인 모든 OpenShift Container Platform 구성요소에서 전송 중인 데이터는 HTTPS를 통해 암호화됩니다.

스토리지 유형에서 지원하는 방식으로 호스트에 영구 볼륨(PV)을 마운트할 수 있습니다. 스토리지 유형에 따라 기능이 다르며 각 PV의 액세스 모드는 해당 볼륨에서 지원하는 특정 모드로 설정됩니다.

예를 들어 NFS에서는 여러 읽기/쓰기 클라이언트를 지원할 수 있지만 특정 NFS PV는 서버에서 읽기 전용으로 내보낼 수 있습니다. 각 PV에는 `ReadWriteOnce`, `ReadOnlyMany` 및 `ReadWriteMany` 와 같은 특정 PV 기능을 설명하는 자체 액세스 모드 세트가 있습니다.

#### 2.12.2. 공유 스토리지

NFS와 같은 공유 스토리지 공급자의 경우 PV는 그룹 ID(GID)를 PV 리소스에 대한 주석으로 등록합니다. 그런 다음 Pod에서 PV를 요청하면 주석이 달린 GID가 Pod의 보충 그룹에 추가되므로, 해당 Pod가 공유 스토리지의 콘텐츠에 액세스할 수 있습니다.

#### 2.12.3. 블록 스토리지

AWS EBS(Elastic Block Store), GCE 영구 디스크 및 iSCSI와 같은 블록 스토리지 공급자의 경우 OpenShift Container Platform에서는 SELinux 기능을 사용하여 권한이 없는 Pod용으로 마운트된 볼륨의 루트를 보호함으로써, 연관된 컨테이너에서만 마운트된 볼륨을 소유하고 볼 수 있게 합니다.

추가 리소스

영구저장장치 이해

CSI 볼륨 구성

동적 프로비저닝

NFS를 사용하는 영구저장장치

AWS Elastic Block Store를 사용하는 영구저장장치

GCE 영구 디스크를 사용한 영구저장장치

### 2.13. 클러스터 이벤트 및 로그 모니터링

OpenShift Container Platform 클러스터를 모니터링하고 감사하는 기능은 부적절한 사용으로부터 클러스터와 사용자를 보호하는 데 중요한 부분입니다.

이 용도에 유용한 클러스터 수준 정보의 두 가지 주요 소스, 즉 이벤트와 로깅이 있습니다.

#### 2.13.1. 클러스터 이벤트 감시

클러스터 관리자는 `Event` 리소스 유형을 익히고 시스템 이벤트 목록을 검토하여 관심있는 이벤트를 결정하는 것이 좋습니다. 이벤트는 네임스페이스, 즉 관련 리소스의 네임스페이스 또는 클러스터 이벤트의 경우에는 `default` 네임스페이스와 연결됩니다. 기본 네임스페이스에는 인프라 구성요소와 관련된 노드 이벤트 및 리소스 이벤트와 같은 클러스터 모니터링 또는 감사 관련 이벤트가 있습니다.

마스터 API 및 아래 명령은 이벤트 목록의 범위를 노드 관련 항목으로만 지정하는 매개변수는 제공하지 않습니다. 간단한 접근 방식은 다음 명령을 사용하는 것입니다.

```shell
oc
```

```shell
grep
```

```shell-session
$ oc get event -n default | grep Node
```

```shell-session
1h         20h         3         origin-node-1.example.local   Node      Normal    NodeHasDiskPressure   ...
```

더 유연한 접근 방식은 다른 툴에서 처리할 수 있는 양식으로 이벤트를 출력하는 것입니다. 예를 들어 다음 예에서는 JSON 출력을 대상으로 툴을 사용하여 `NodeHasDiskPressure` 이벤트만 추출합니다.

```shell
jq
```

```shell-session
$ oc get events -n default -o json \
  | jq '.items[] | select(.involvedObject.kind == "Node" and .reason == "NodeHasDiskPressure")'
```

```shell-session
{
  "apiVersion": "v1",
  "count": 3,
  "involvedObject": {
    "kind": "Node",
    "name": "origin-node-1.example.local",
    "uid": "origin-node-1.example.local"
  },
  "kind": "Event",
  "reason": "NodeHasDiskPressure",
  ...
}
```

리소스 생성, 수정 또는 삭제와 관련된 이벤트도 클러스터의 오용을 탐지하는 데 적합할 수 있습니다. 예를 들어 다음과 같은 쿼리를 사용하면 과도한 이미지 가져오기를 찾을 수 있습니다.

```shell-session
$ oc get events --all-namespaces -o json \
  | jq '[.items[] | select(.involvedObject.kind == "Pod" and .reason == "Pulling")] | length'
```

```shell-session
4
```

참고

네임스페이스가 삭제되면 해당 이벤트도 삭제됩니다. 이벤트도 만료될 수 있으며 etcd 스토리지가 가득 차지 않도록 삭제됩니다. 이벤트는 영구 레코드로 저장되지 않으며 시간 경과에 따른 통계를 캡처하려면 자주 폴링해야 합니다.

#### 2.13.2. 로깅

아래 명령을 사용하면 컨테이너 로그, 빌드 구성, 배포를 실시간으로 볼 수 있습니다. 다른 사용자는 다른 로그에 액세스할 수 있습니다.

```shell
oc log
```

프로젝트에 액세스할 수 있는 사용자는 기본적으로 해당 프로젝트의 로그를 볼 수 있습니다.

관리자 역할이 있는 사용자는 모든 컨테이너 로그에 액세스할 수 있습니다.

추가 감사 및 분석을 위해 로그를 저장하려면 `cluster-logging` 애드온 기능을 사용하여 시스템, 컨테이너 및 감사 로그를 수집, 관리 및 볼 수 있습니다. OpenShift Elasticsearch Operator 및 Red Hat OpenShift Logging Operator를 통해 OpenShift Logging을 배포, 관리 및 업그레이드할 수 있습니다.

#### 2.13.3. 감사 로그

감사 로그 를 사용하면 사용자, 관리자 또는 기타 OpenShift Container Platform 구성요소의 동작과 관련된 일련의 활동을 따를 수 있습니다. API 감사 로깅은 각 서버에서 수행됩니다.

추가 리소스

시스템 이벤트 목록

감사 로그 보기

#### 3.1.1. 기본 수신 인증서 이해

기본적으로 OpenShift Container Platform에서는 Ingress Operator를 사용하여 내부 CA를 생성하고 `.apps` 하위 도메인의 애플리케이션에 유효한 와일드카드 인증서를 발급합니다. 웹 콘솔과 CLI도 모두 이 인증서를 사용합니다.

내부 인프라 CA 인증서는 자체 서명됩니다. 이 프로세스는 일부 보안 또는 PKI 팀에서는 나쁜 습관으로 인식할 수 있지만 위험이 거의 없습니다. 이러한 인증서를 암시적으로 신뢰하는 유일한 클라이언트는 클러스터 내의 다른 구성요소입니다. 기본 와일드카드 인증서를 컨테이너 사용자 공간에서 제공한 대로 이미 CA 번들에 포함된 공용 CA에서 발행한 인증서로 교체하면 외부 클라이언트가 `.apps` 하위 도메인에서 실행되는 애플리케이션에 안전하게 연결할 수 있습니다.

#### 3.1.2. 기본 수신 인증서 교체

`.apps` 하위 도메인에 있는 애플리케이션의 기본 수신 인증서를 교체할 수 있습니다. 인증서를 교체한 후 웹 콘솔 및 CLI를 포함한 모든 애플리케이션에는 지정된 인증서에서 제공하는 암호화가 있습니다.

사전 요구 사항

정규화된 `.apps` 하위 도메인 및 해당 개인 키에 맞는 와일드카드 인증서가 있어야 합니다. 각각은 별도의 PEM 형식 파일이어야 합니다.

개인 키는 암호화되지 않아야 합니다. 키가 암호화된 경우 OpenShift Container Platform으로 가져오기 전에 키의 암호를 해독합니다.

인증서에는 `*.apps.<clustername>.<domain>` 을 표시하는 `subjectAltName` 확장자가 포함되어야 합니다.

인증서 파일은 체인에 하나 이상의 인증서를 포함할 수 있습니다. 파일은 와일드카드 인증서를 첫 번째 인증서로 나열한 다음 다른 중간 인증서가 있는 다음 root CA 인증서로 끝나야 합니다.

루트 CA 인증서를 추가 PEM 형식 파일로 복사합니다.

---- `END CERTIFICATE-----를` 포함하는 모든 인증서가 해당 행 뒤에 하나의 반환으로도 종료되는지 확인합니다.

프로세스

와일드카드 인증서에 서명하는 데 사용되는 루트 CA 인증서만 포함하는 구성 맵을 생성합니다.

```shell-session
$ oc create configmap custom-ca \
     --from-file=ca-bundle.crt=</path/to/example-ca.crt> \
     -n openshift-config
```

1. `</path/to/example-ca.crt>` 는 로컬 파일 시스템에서 루트 CA 인증서 파일의 경로입니다. 예를 들어 `/etc/pki/ca-trust/source/anchors`.

새로 생성된 구성 맵으로 클러스터 전체 프록시 구성을 업데이트합니다.

```shell-session
$ oc patch proxy/cluster \
     --type=merge \
     --patch='{"spec":{"trustedCA":{"name":"custom-ca"}}}'
```

참고

클러스터에 대해 신뢰할 수 있는 CA만 업데이트하면 MCO는 `/etc/pki/ca-trust/source/anchors/openshift-config-user-ca-bundle.crt` 파일을 업데이트하고 노드를 재부팅할 필요가 없도록 신뢰할 수 있는 CA 업데이트를 각 노드에 적용합니다. 그러나 이러한 변경으로 인해 MCP(Machine Config Daemon)가 kubelet 및 CRI-O와 같은 각 노드에서 중요한 서비스를 다시 시작합니다. 이러한 서비스를 다시 시작하면 서비스가 완전히 다시 시작될 때까지 각 노드가 `NotReady` 상태를 간략하게 입력합니다.

`openshift-config-user-ca-bundle.crt` 파일(예: `noproxy`)에서 다른 매개변수를 변경하면 MCO가 클러스터의 각 노드를 재부팅합니다.

와일드카드 인증서 체인과 키를 포함하는 보안을 생성합니다.

```shell-session
$ oc create secret tls <secret> \
     --cert=</path/to/cert.crt> \
     --key=</path/to/cert.key> \
     -n openshift-ingress
```

1. `<secret>` 은 인증서 체인과 개인 키를 포함할 보안의 이름입니다.

2. `</path/to/cert.crt>` 는 로컬 파일 시스템의 인증서 체인 경로입니다.

3. `</path/to/cert.key>` 는 이 인증서와 관련된 개인 키의 경로입니다.

새로 생성된 보안으로 Ingress Controller 구성을 업데이트합니다.

```shell-session
$ oc patch ingresscontroller.operator default \
     --type=merge -p \
     '{"spec":{"defaultCertificate": {"name": "<secret>"}}}' \
     -n openshift-ingress-operator
```

1. `<secret>` 을 이전 단계에서 보안에 사용된 이름으로 교체합니다.

중요

롤링 업데이트를 수행하기 위해 Ingress Operator를 트리거하려면 보안 이름을 업데이트해야 합니다. kubelet은 볼륨 마운트의 시크릿에 변경 사항을 자동으로 전파하므로 시크릿 콘텐츠를 업데이트해도 롤링 업데이트가 트리거되지 않습니다. 자세한 내용은 Red Hat 지식베이스 솔루션을 참조하십시오.

#### 3.1.3. 추가 리소스

CA 번들 인증서 교체

프록시 인증서 사용자 정의

### 3.2. API 서버 인증서 추가

기본 API 서버 인증서는 내부 OpenShift Container Platform 클러스터 CA에서 발급합니다. 클러스터 외부의 클라이언트는 기본적으로 API 서버의 인증서를 확인할 수 없습니다. 이 인증서는 클라이언트가 신뢰하는 CA에서 발급한 인증서로 교체할 수 있습니다.

참고

호스팅된 컨트롤 플레인 클러스터에서 필요한 만큼 Kubernetes API 서버에 사용자 지정 인증서를 추가할 수 있습니다. 그러나 작업자 노드가 컨트롤 플레인과 통신하는 데 사용하는 끝점의 인증서를 추가하지 마십시오. 자세한 내용은 호스팅된 클러스터에서 사용자 정의 API 서버 인증서 구성을 참조하십시오.

#### 3.2.1. certificate이라는 API 서버 추가

기본 API 서버 인증서는 내부 OpenShift Container Platform 클러스터 CA에서 발급합니다. 리버스 프록시 또는 로드 밸런서가 사용되는 경우와 같이 클라이언트가 요청한 정규화된 도메인 이름(FQDN)을 기반으로 API 서버가 반환할 대체 인증서를 하나 이상 추가할 수 있습니다.

사전 요구 사항

FQDN의 인증서와 해당 개인 키가 있어야 합니다. 각각은 별도의 PEM 형식 파일이어야 합니다.

개인 키는 암호화되지 않아야 합니다. 키가 암호화된 경우 OpenShift Container Platform으로 가져오기 전에 키의 암호를 해독합니다.

인증서에는 FQDN을 표시하는 `subjectAltName` 확장자가 포함되어야 합니다.

인증서 파일은 체인에 하나 이상의 인증서를 포함할 수 있습니다. API 서버 FQDN의 인증서는 파일의 첫 번째 인증서여야 합니다. 그런 다음 중간 인증서가 올 수 있으며 파일은 루트 CA 인증서로 끝나야 합니다.

주의

내부 로드 밸런서용으로 이름 지정된 인증서를 제공하지 마십시오(host name `api-int.<cluster_name>.<base_domain>`). 그렇지 않으면 클러스터 성능이 저하됩니다.

프로세스

`kubeadmin` 사용자로 새 API에 로그인합니다.

```shell-session
$ oc login -u kubeadmin -p <password> https://FQDN:6443
```

`kubeconfig` 파일을 가져옵니다.

```shell-session
$ oc config view --flatten > kubeconfig-newapi
```

`openshift-config` 네임스페이스에 인증서 체인과 개인 키가 포함된 보안을 생성합니다.

```shell-session
$ oc create secret tls <secret> \
     --cert=</path/to/cert.crt> \
     --key=</path/to/cert.key> \
     -n openshift-config
```

1. `<secret>` 은 인증서 체인과 개인 키를 포함할 보안의 이름입니다.

2. `</path/to/cert.crt>` 는 로컬 파일 시스템의 인증서 체인 경로입니다.

3. `</path/to/cert.key>` 는 이 인증서와 관련된 개인 키의 경로입니다.

생성된 보안을 참조하도록 API 서버를 업데이트합니다.

```shell-session
$ oc patch apiserver cluster \
     --type=merge -p \
     '{"spec":{"servingCerts": {"namedCertificates": \
     [{"names": ["<FQDN>"], \
     "servingCertificate": {"name": "<secret>"}}]}}}'
```

1. `<FQDN>` 을 API 서버가 인증서를 제공해야 하는 FQDN으로 바꿉니다. 포트 번호를 포함하지 마십시오.

2. `<secret>` 을 이전 단계에서 보안에 사용된 이름으로 교체합니다.

`apiserver/cluster` 오브젝트를 조사하고 보안이 이제 참조되는지 확인합니다.

```shell-session
$ oc get apiserver cluster -o yaml
```

```shell-session
...
spec:
  servingCerts:
    namedCertificates:
    - names:
      - <FQDN>
      servingCertificate:
        name: <secret>
...
```

`kube-apiserver` 운영자를 확인하고 Kubernetes API 서버의 새 버전이 롤아웃되는지 확인합니다. 운영자가 구성 변경 사항을 탐지하고 새 배포를 트리거하는 데 1분 정도 걸릴 수 있습니다. 새 버전이 롤아웃되는 동안 `PROGRESSING` 은 `True` 를 보고합니다.

```shell-session
$ oc get clusteroperators kube-apiserver
```

다음 출력에 표시된 것처럼 `PROGRESSING` 이 `False` 로 표시될 때까지 다음 단계를 진행하지 마십시오.

```shell-session
NAME             VERSION   AVAILABLE   PROGRESSING   DEGRADED   SINCE
kube-apiserver   4.20.0     True        False         False      145m
```

`PROGRESSING` 에 `True` 가 표시되면 몇 분 기다렸다가 다시 시도하십시오.

참고

Kubernetes API 서버의 새 버전은 certificate라는 API 서버가 처음으로 추가된 경우에만 롤아웃합니다. certificate라는 API 서버가 업데이트되면 `kube-apiserver` Pod가 업데이트된 인증서를 동적으로 다시 로드하기 때문에 Kubernetes API 서버의 새 버전이 롤아웃되지 않습니다.

### 3.3. 서비스 제공 인증서 보안을 사용하여 서비스 트래픽 보안

서비스 제공 인증서는 서비스 간 통신을 위한 자동 TLS 암호화를 제공합니다. 내부 클러스터 트래픽을 보호하도록 서비스, ConfigMaps, APIServices, CRD 및 Webhook에 대한 인증서를 구성합니다.

#### 3.3.1. 서비스 제공 인증서 이해

서비스 제공 인증서는 암호화가 필요한 복잡한 미들웨어 애플리케이션을 지원하기 위한 것입니다. 이러한 인증서는 TLS 웹 서버 인증서로 발급됩니다.

`service-ca` 컨트롤러에서는 `x509.SHA256WithRSA` 서명 알고리즘을 사용하여 서비스 인증서를 생성합니다.

생성된 인증서 및 키는 PEM 형식이며, 생성된 보안의 `tls.crt` 및 `tls.key` 에 각각 저장됩니다. 인증서와 키는 만료 시기가 다가오면 자동으로 교체됩니다.

서비스 인증서를 발급하는 서비스 CA 인증서는 26개월 동안 유효하며 유효 기간이 13개월 미만으로 남아 있으면 자동으로 순환됩니다. 교체 후에도 이전 서비스 CA 구성은 만료될 때까지 계속 신뢰 상태가 유지됩니다. 그러면 만료되기 전에 유예 기간 동안 영향을 받는 모든 서비스의 주요 자료를 새로 고칠 수 있습니다. 서비스를 다시 시작하고 키 자료를 새로 고치는 이 유예 기간 동안 클러스터를 업그레이드하지 않으면 이전 서비스 CA가 만료된 후 실패하지 않도록 서비스를 직접 다시 시작해야 할 수도 있습니다.

참고

다음 명령을 사용하여 클러스터의 모든 Pod를 직접 다시 시작할 수 있습니다. 이 명령을 실행하면 모든 네임스페이스에서 실행 중인 모든 Pod가 삭제되므로 서비스가 중단됩니다. 이 Pod는 삭제 후 자동으로 다시 시작됩니다.

```shell-session
$ for I in $(oc get ns -o jsonpath='{range .items[*]} {.metadata.name}{"\n"} {end}'); \
      do oc delete pods --all -n $I; \
      sleep 1; \
      done
```

#### 3.3.2. 서비스 인증서 추가

서비스와의 통신을 보호하려면 서명된 제공 인증서와 키 쌍을 서비스와 동일한 네임스페이스의 보안에 생성합니다.

생성된 인증서는 내부 서비스 DNS 이름 `<service.name>.<service.namespace>.svc` 에만 유효하고 내부 통신에만 유효합니다. 서비스가 헤드리스 서비스(`clusterIP` 값이 설정되지 않음)인 경우 생성된 인증서에는 `*.<service.name>.<service.namespace>.svc` 형식의 와일드카드 제목도 포함됩니다.

중요

생성된 인증서에는 헤드리스 서비스에 대한 와일드카드 제목이 포함되어 있으므로 클라이언트가 개별 Pod를 구분해야 하는 경우 서비스 CA를 사용하지 않아야 합니다. 이 경우 다음을 수행합니다.

다른 CA를 사용하여 개별 TLS 인증서를 생성합니다.

개별 Pod로 전달되며 다른 Pod로 가장해서는 안 되는 연결에 대해 서비스 CA를 신뢰할 수 있는 CA로 수락하지 마십시오. 이러한 연결은 개별 TLS 인증서를 생성하는 데 사용된 CA를 신뢰하도록 구성해야 합니다.

사전 요구 사항

서비스가 정의되어 있어야 합니다.

프로세스

`service.beta.openshift.io/serving-cert-secret-name` 으로 서비스에 주석을 답니다.

```shell-session
$ oc annotate service <service_name> \
     service.beta.openshift.io/serving-cert-secret-name=<secret_name>
```

1. `<service_name>` 을 보호할 서비스 이름으로 교체합니다.

2. `<secret_name>` 은 인증서와 키 쌍이 포함되어 생성된 보안의 이름입니다.

참고

편의를 위해 이 값은 <.

```shell
service_name>과 동일하게 사용하는 것이 좋습니다
```

예를 들어 서비스 `test1` 에 주석을 달려면 다음 명령을 사용합니다.

```shell-session
$ oc annotate service test1 service.beta.openshift.io/serving-cert-secret-name=test1
```

서비스를 검사하여 주석이 있는지 확인합니다.

```shell-session
$ oc describe service <service_name>
```

```shell-session
...
Annotations:              service.beta.openshift.io/serving-cert-secret-name: <service_name>
                          service.beta.openshift.io/serving-cert-signed-by: openshift-service-serving-signer@1556850837
...
```

클러스터에서 서비스 보안을 생성하면 `Pod` 사양에서 보안을 마운트하고, 사용 가능 상태가 되면 Pod에서 실행합니다.

추가 리소스

서비스 인증서를 사용하여 재암호화 TLS 종료를 사용하여 보안 경로를 구성할 수 있습니다. 자세한 내용은 사용자 정의 인증서를 사용하여 재암호화 경로 생성을 참조하십시오.

#### 3.3.3. 구성 맵에 서비스 CA 번들 추가

Pod는 `service.beta.openshift.io/inject-cabundle=true` 주석이 있는 `ConfigMap` 오브젝트를 마운트하여 CA(서비스 인증 기관) 인증서에 액세스할 수 있습니다. 구성 맵에 주석을 달면 클러스터에서 서비스 CA 인증서를 구성 맵의 `service-ca.crt` 키에 자동으로 삽입합니다. 이 CA 인증서에 액세스하면 TLS 클라이언트가 서비스 제공 인증서를 사용하여 서비스에 대한 연결을 확인할 수 있습니다.

중요

구성 맵에 이 주석을 추가하면 OpenShift Service CA Operator가 구성 맵의 모든 데이터를 삭제합니다. Pod 구성을 저장하는 것과 동일한 구성 맵을 사용하는 대신 별도의 구성 맵을 사용하여 `service-ca.crt` 를 포함하는 것이 좋습니다.

프로세스

다음 명령을 입력하여 `service.beta.openshift.io/inject-cabundle=true` 주석으로 구성 맵에 주석을 답니다.

```shell-session
$ oc annotate configmap <config_map_name> \
     service.beta.openshift.io/inject-cabundle=true
```

1. `<config_map_name>` 을 주석을 달 구성 맵 이름으로 교체합니다.

참고

볼륨 마운트에서 명시적으로 `service-ca.crt` 키를 참조하면 CA 번들로 구성 맵을 삽입할 때까지 Pod가 시작되지 않습니다. 볼륨의 제공 인증서 구성에서 `optional` 매개변수를 `true` 로 설정하여 이 동작을 덮어쓸 수 있습니다.

구성 맵을 보고 서비스 CA 번들이 삽입되었는지 확인합니다.

```shell-session
$ oc get configmap <config_map_name> -o yaml
```

CA 번들은 YAML 출력에서 `service-ca.crt` 키 값으로 표시됩니다.

```shell-session
apiVersion: v1
data:
  service-ca.crt: |
    -----BEGIN CERTIFICATE-----
...
```

`Deployment` 오브젝트를 구성하여 Pod에 존재하는 각 컨테이너에 구성 맵을 볼륨으로 마운트합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-example-custom-ca-deployment
  namespace: my-example-custom-ca-ns
spec:
  ...
    spec:
      ...
      containers:
        - name: my-container-that-needs-custom-ca
          volumeMounts:
          - name: trusted-ca
            mountPath: /etc/pki/ca-trust/extracted/pem
            readOnly: true
      volumes:
      - name: trusted-ca
        configMap:
          name: <config_map_name>
          items:
            - key: ca-bundle.crt
              path: tls-ca-bundle.pem
# ...
```

1. 절차의 이전 단계에서 주석을 지정한 구성 맵의 이름을 지정합니다.

2. `ca-bundle.crt` 는 ConfigMap 키로 필요합니다.

3. `tls-ca-bundle.pem` 은 ConfigMap 경로로 필요합니다.

#### 3.3.4. API 서비스에 서비스 CA 번들 추가

`spec.caBundle` 필드에 서비스 CA 번들이 입력되도록 `service.beta.openshift.io/inject-cabundle=true` 로 `APIService` 오브젝트에 주석을 답니다. 그러면 쿠버네티스 API 서버가 대상 끝점을 보호하는 데 사용되는 서비스 CA 인증서의 유효성을 확인할 수 있습니다.

프로세스

`service.beta.openshift.io/inject-cabundle=true` 로 API 서비스에 주석을 답니다.

```shell-session
$ oc annotate apiservice <api_service_name> \
     service.beta.openshift.io/inject-cabundle=true
```

1. `<api_service_name>` 을 주석을 달 API 서비스 이름으로 교체합니다.

예를 들어 API 서비스 `test1` 에 주석을 달려면 다음 명령을 사용합니다.

```shell-session
$ oc annotate apiservice test1 service.beta.openshift.io/inject-cabundle=true
```

API 서비스를 보고 서비스 CA 번들이 삽입되었는지 확인합니다.

```shell-session
$ oc get apiservice <api_service_name> -o yaml
```

CA 번들은 YAML 출력의 `spec.caBundle` 필드에 표시됩니다.

```shell-session
apiVersion: apiregistration.k8s.io/v1
kind: APIService
metadata:
  annotations:
    service.beta.openshift.io/inject-cabundle: "true"
...
spec:
  caBundle: <CA_BUNDLE>
...
```

#### 3.3.5. 사용자 정의 리소스 정의에 서비스 CA 번들 추가

`spec.conversion.webhook.clientConfig.caBundle` 필드에 서비스 CA 번들이 입력되도록 `CustomResourceDefinition` (CRD) 오브젝트에 `service.beta.openshift.io/inject-cabundle=true` 로 주석을 답니다. 그러면 쿠버네티스 API 서버가 대상 끝점을 보호하는 데 사용되는 서비스 CA 인증서의 유효성을 확인할 수 있습니다.

참고

CRD가 변환에 웹 후크를 사용하도록 구성된 경우 서비스 CA 번들은 CRD에만 삽입됩니다. CRD의 웹 후크가 서비스 CA 인증서로 보안된 경우에만 서비스 CA 번들을 삽입하는 것이 유용합니다.

프로세스

`service.beta.openshift.io/inject-cabundle=true` 로 CRD에 주석을 답니다.

```shell-session
$ oc annotate crd <crd_name> \
     service.beta.openshift.io/inject-cabundle=true
```

1. `<crd_name>` 을 주석을 달 CRD 이름으로 교체합니다.

예를 들어 CRD `test1` 에 주석을 달려면 다음 명령을 사용합니다.

```shell-session
$ oc annotate crd test1 service.beta.openshift.io/inject-cabundle=true
```

CRD를 보고 서비스 CA 번들이 삽입되었는지 확인합니다.

```shell-session
$ oc get crd <crd_name> -o yaml
```

CA 번들은 YAML 출력의 `spec.conversion.webhook.clientConfig.caBundle` 필드에 표시됩니다.

```shell-session
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  annotations:
    service.beta.openshift.io/inject-cabundle: "true"
...
spec:
  conversion:
    strategy: Webhook
    webhook:
      clientConfig:
        caBundle: <CA_BUNDLE>
...
```

#### 3.3.6. 변경 웹 후크 구성에 서비스 CA 번들 추가

각 웹 후크의 `clientConfig.caBundle` 필드에 서비스 CA 번들이 입력되도록 `service.beta.openshift.io/inject-cabundle=true` 로 `MutatingWebhookConfiguration` 오브젝트에 주석을 달 수 있습니다. 그러면 쿠버네티스 API 서버가 대상 끝점을 보호하는 데 사용되는 서비스 CA 인증서의 유효성을 확인할 수 있습니다.

참고

웹 후크마다 다른 CA 번들을 지정해야 하는 승인 웹 후크 구성에는 이 주석을 설정하지 마십시오. 그러면 모든 웹 후크에 서비스 CA 번들이 삽입됩니다.

프로세스

`service.beta.openshift.io/inject-cabundle=true` 로 변경 웹 후크 구성에 주석을 답니다.

```shell-session
$ oc annotate mutatingwebhookconfigurations <mutating_webhook_name> \
     service.beta.openshift.io/inject-cabundle=true
```

1. `<mutating_webhook_name>` 을 주석을 달 변경 웹 후크 구성 이름으로 교체합니다.

예를 들어 변경 웹 후크 구성 `test1` 에 주석을 달려면 다음 명령을 사용합니다.

```shell-session
$ oc annotate mutatingwebhookconfigurations test1 service.beta.openshift.io/inject-cabundle=true
```

변경 웹 후크 구성을 보고 서비스 CA 번들이 삽입되었는지 확인합니다.

```shell-session
$ oc get mutatingwebhookconfigurations <mutating_webhook_name> -o yaml
```

CA 번들은 YAML 출력에 있는 모든 웹 후크의 `clientConfig.caBundle` 필드에 표시됩니다.

```shell-session
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  annotations:
    service.beta.openshift.io/inject-cabundle: "true"
...
webhooks:
- myWebhook:
  - v1beta1
  clientConfig:
    caBundle: <CA_BUNDLE>
...
```

#### 3.3.7. 검증 웹 후크 구성에 서비스 CA 번들 추가

각 웹 후크의 `clientConfig.caBundle` 필드에 서비스 CA 번들이 입력되도록 `service.beta.openshift.io/inject-cabundle=true` 로 `ValidatingWebhookConfiguration` 오브젝트에 주석을 달 수 있습니다. 그러면 쿠버네티스 API 서버가 대상 끝점을 보호하는 데 사용되는 서비스 CA 인증서의 유효성을 확인할 수 있습니다.

참고

웹 후크마다 다른 CA 번들을 지정해야 하는 승인 웹 후크 구성에는 이 주석을 설정하지 마십시오. 그러면 모든 웹 후크에 서비스 CA 번들이 삽입됩니다.

프로세스

`service.beta.openshift.io/inject-cabundle=true` 로 검증 웹 후크 구성에 주석을 답니다.

```shell-session
$ oc annotate validatingwebhookconfigurations <validating_webhook_name> \
     service.beta.openshift.io/inject-cabundle=true
```

1. `<validating_webhook_name>` 을 주석을 달 검증 웹 후크 구성 이름으로 교체합니다.

예를 들어 검증 웹 후크 구성 `test1` 에 주석을 달려면 다음 명령을 사용합니다.

```shell-session
$ oc annotate validatingwebhookconfigurations test1 service.beta.openshift.io/inject-cabundle=true
```

검증 웹 후크 구성을 보고 서비스 CA 번들이 삽입되었는지 확인합니다.

```shell-session
$ oc get validatingwebhookconfigurations <validating_webhook_name> -o yaml
```

CA 번들은 YAML 출력에 있는 모든 웹 후크의 `clientConfig.caBundle` 필드에 표시됩니다.

```shell-session
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  annotations:
    service.beta.openshift.io/inject-cabundle: "true"
...
webhooks:
- myWebhook:
  - v1beta1
  clientConfig:
    caBundle: <CA_BUNDLE>
...
```

#### 3.3.8. 생성된 서비스 인증서를 직접 순환

관련 보안을 삭제하여 서비스 인증서를 순환할 수 있습니다. 보안을 삭제하면 새로운 보안이 자동으로 생성되어 새 인증서가 생성됩니다.

사전 요구 사항

인증서 및 키 쌍을 포함하는 보안이 서비스용으로 생성되어야 합니다.

프로세스

서비스를 검사하여 인증서가 포함된 보안을 판별합니다. 아래 표시된 대로 `serving-cert-secret-name` 주석에 있습니다.

```shell-session
$ oc describe service <service_name>
```

```shell-session
...
service.beta.openshift.io/serving-cert-secret-name: <secret>
...
```

서비스용으로 생성된 보안을 삭제합니다. 이 프로세스는 자동으로 보안을 재생성합니다.

```shell-session
$ oc delete secret <secret>
```

1. `<secret>` 을 이전 단계의 보안 이름으로 교체합니다.

새 보안을 확보하고 `AGE` 를 검사하여 인증서가 다시 생성되었는지 확인합니다.

```shell-session
$ oc get secret <service_name>
```

```shell-session
NAME              TYPE                DATA   AGE
<service.name>    kubernetes.io/tls   2      1s
```

#### 3.3.9. 서비스 CA 인증서를 직접 순환

서비스 CA는 26개월 동안 유효하며 유효 기간이 13개월 미만으로 남아 있으면 자동으로 새로 고쳐집니다.

필요하면 다음 절차에 따라 서비스 CA를 직접 새로 고칠 수 있습니다.

주의

수동으로 순환된 서비스 CA는 이전 서비스 CA와의 신뢰를 유지 관리하지 않습니다. 클러스터의 Pod가 다시 시작되어 Pod가 새 서비스 CA에서 발급한 서비스 제공 인증서를 사용하고 있는지 확인할 때까지 일시적으로 서비스 중단이 발생할 수 있습니다.

사전 요구 사항

클러스터 관리자로 로그인해야 합니다.

프로세스

다음 명령을 사용하여 현재 서비스 CA 인증서의 만료 날짜를 봅니다.

```shell-session
$ oc get secrets/signing-key -n openshift-service-ca \
     -o template='{{index .data "tls.crt"}}' \
     | base64 --decode \
     | openssl x509 -noout -enddate
```

서비스 CA를 직접 순환합니다. 이 프로세스는 새로운 서비스 인증서에 서명하는 데 사용될 새로운 서비스 CA를 생성합니다.

```shell-session
$ oc delete secret/signing-key -n openshift-service-ca
```

새 인증서를 모든 서비스에 적용하도록 클러스터의 모든 Pod를 다시 시작합니다. 이 명령을 실행하면 모든 서비스가 업데이트된 인증서를 사용합니다.

```shell-session
$ for I in $(oc get ns -o jsonpath='{range .items[*]} {.metadata.name}{"\n"} {end}'); \
      do oc delete pods --all -n $I; \
      sleep 1; \
      done
```

주의

이 명령은 모든 네임스페이스에서 실행 중인 모든 Pod를 대상으로 진행하고 삭제하므로 서비스가 중단됩니다. 이 Pod는 삭제 후 자동으로 다시 시작됩니다.

#### 3.4.1. CA 번들 인증서 이해

프록시 인증서를 사용하면 송신 연결을 수행할 때 플랫폼 구성 요소에서 사용하는 하나 이상의 사용자 정의 인증 기관(CA)을 지정할 수 있습니다.

Proxy 오브젝트의 `trustedCA` 필드는 사용자 제공 신뢰할 수 있는 인증 기관(CA) 번들을 포함하는 구성 맵에 대한 참조입니다. 이 번들은 RHCOS(Red Hat Enterprise Linux CoreOS) 신뢰 번들과 병합되어 송신 HTTPS 호출을 수행하는 플랫폼 구성 요소의 신뢰 저장소에 삽입됩니다. 예를 들어 `image-registry-operator` 에서 이미지를 다운로드하도록 외부 이미지 레지스트리를 호출합니다. `trustedCA` 를 지정하지 않으면 프록시 HTTPS 연결에 RHCOS 신뢰 번들만 사용됩니다. 자체 인증서 인프라를 사용하려면 RHCOS 신뢰 번들에 사용자 정의 CA 인증서를 제공합니다.

`trustedCA` 필드는 프록시 유효성 검증기만 사용해야 합니다. 유효성 검증기를 통해서는 필수 키 `ca-bundle.crt` 에서 인증서 번들을 읽고 `openshift-config-managed` 네임스페이스의 `trusted-ca-bundle` 이라는 구성 맵에 복사해야 합니다. `trustedCA` 에서 참조하는 구성 맵의 네임스페이스는 `openshift-config` 입니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-ca-bundle
  namespace: openshift-config
data:
  ca-bundle.crt: |
    -----BEGIN CERTIFICATE-----
    Custom CA certificate bundle.
    -----END CERTIFICATE-----
```

#### 3.4.2. CA 번들 인증서 교체

프로세스

와일드카드 인증서에 서명하는 데 사용되는 루트 CA 인증서가 포함된 구성 맵을 생성합니다.

```shell-session
$ oc create configmap custom-ca \
     --from-file=ca-bundle.crt=</path/to/example-ca.crt> \
     -n openshift-config
```

1. `</path/to/example-ca.crt` >는 로컬 파일 시스템의 CA 인증서 번들 경로입니다.

새로 생성된 구성 맵으로 클러스터 전체 프록시 구성을 업데이트합니다.

```shell-session
$ oc patch proxy/cluster \
     --type=merge \
     --patch='{"spec":{"trustedCA":{"name":"custom-ca"}}}'
```

#### 3.4.3. 추가 리소스

기본 수신 인증서 교체

클러스터 전체 프록시 사용

프록시 인증서 사용자 정의

#### 4.1.1. 목적

API 서버는 `api.<cluster_name>.<base_domain>` 에서 클러스터 외부의 클라이언트가 액세스할 수 있습니다. 클라이언트가 다른 호스트 이름으로 또는 클러스터 관리 인증 기관(CA) 인증서를 클라이언트에 배포하지 않고 API 서버에 액세스하게 합니다. 관리자는 콘텐츠를 제공할 때 API 서버가 사용할 사용자 정의 기본 인증서를 설정해야 합니다.

#### 4.1.2. 위치

사용자 제공 인증서는 `openshift-config` 네임스페이스에 `kubernetes.io/tls` 유형 `Secret` 으로 제공되어야 합니다. API 서버 클러스터 구성인 `apiserver/cluster` 리소스를 업데이트하여 사용자 제공 인증서를 사용할 수 있게 합니다.

#### 4.1.3. 관리

사용자 제공 인증서는 사용자가 관리합니다.

#### 4.1.4. 만료

API 서버 클라이언트 인증서가 5분 내에 만료됩니다.

사용자 제공 인증서는 사용자가 관리합니다.

#### 4.1.5. 사용자 정의

필요에 따라 사용자 관리 인증서가 포함된 보안을 업데이트합니다.

#### 4.1.6. 추가 리소스

API 서버 인증서 추가

#### 4.2.1. 목적

프록시 인증서를 사용하면 송신 연결을 만들 때 플랫폼 구성요소에서 사용하는 하나 이상의 사용자 정의 인증 기관(CA) 인증서를 지정할 수 있습니다.

Proxy 오브젝트의 `trustedCA` 필드는 사용자 제공 신뢰할 수 있는 인증 기관(CA) 번들을 포함하는 구성 맵에 대한 참조입니다. 이 번들은 RHCOS(Red Hat Enterprise Linux CoreOS) 신뢰 번들과 병합되어 송신 HTTPS 호출을 수행하는 플랫폼 구성 요소의 신뢰 저장소에 삽입됩니다. 예를 들어 `image-registry-operator` 에서 이미지를 다운로드하도록 외부 이미지 레지스트리를 호출합니다. `trustedCA` 를 지정하지 않으면 프록시 HTTPS 연결에 RHCOS 신뢰 번들만 사용됩니다. 자체 인증서 인프라를 사용하려면 RHCOS 신뢰 번들에 사용자 정의 CA 인증서를 제공합니다.

`trustedCA` 필드는 프록시 유효성 검증기만 사용해야 합니다. 유효성 검증기를 통해서는 필수 키 `ca-bundle.crt` 에서 인증서 번들을 읽고 `openshift-config-managed` 네임스페이스의 `trusted-ca-bundle` 이라는 구성 맵에 복사해야 합니다. `trustedCA` 에서 참조하는 구성 맵의 네임스페이스는 `openshift-config` 입니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-ca-bundle
  namespace: openshift-config
data:
  ca-bundle.crt: |
    -----BEGIN CERTIFICATE-----
    Custom CA certificate bundle.
    -----END CERTIFICATE-----
```

#### 4.2.1.1. 추가 리소스

클러스터 전체 프록시 구성

#### 4.2.2. 설치 중 프록시 인증서 관리

설치 프로그램 구성의 `additionalTrustBundle` 값은 설치 중 프록시 신뢰 CA 인증서를 지정하는 데 사용됩니다. 예를 들면 다음과 같습니다.

```shell-session
$ cat install-config.yaml
```

```shell-session
...
proxy:
  httpProxy: http://<username:password@proxy.example.com:123/>
  httpsProxy: http://<username:password@proxy.example.com:123/>
  noProxy: <123.example.com,10.88.0.0/16>
additionalTrustBundle: |
    -----BEGIN CERTIFICATE-----
   <MY_HTTPS_PROXY_TRUSTED_CA_CERT>
    -----END CERTIFICATE-----
...
```

#### 4.2.3. 위치

사용자 제공 신뢰 번들은 구성 맵으로 표시됩니다. 구성 맵은 송신 HTTPS 호출을 수행하는 플랫폼 구성 요소의 파일 시스템에 마운트됩니다. 일반적으로 Operator는 구성 맵을 `/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem` 에 마운트하지만 프록시에는 필요하지 않습니다. 프록시는 HTTPS 연결을 수정하거나 검사할 수 있습니다. 두 경우 모두 프록시는 연결을 위해 새 인증서를 생성하고 서명해야 합니다.

완전한 프록시 지원이란 지정된 프록시에 연결하고 생성된 서명을 신뢰한다는 의미입니다. 따라서 사용자가 신뢰할 수 있는 루트를 지정하고 이 신뢰할 수 있는 루트에 연결된 인증서 체인도 신뢰할 수 있게 해야 합니다.

RHCOS 신뢰 번들을 사용하는 경우 `/etc/pki/ca-trust/source/anchors` 에 CA 인증서를 배치합니다. 자세한 내용은 RHEL(Red Hat Enterprise Linux) 보안 네트워크 문서에서 공유 시스템 인증서 사용을 참조하십시오.

#### 4.2.4. 만료

사용자가 사용자 제공 신뢰 번들의 만료 기간을 설정합니다.

기본 만료 기간은 CA 인증서 자체를 통해 정의됩니다. OpenShift Container Platform 또는 RHCOS에서 사용하기 전에 인증서에 맞게 기본 만료 기간을 구성하는 것은 CA 관리자의 책임입니다.

참고

Red Hat에서는 CA 만료 시점을 모니터링하지 않습니다. 그러나 CA의 수명이 길기 때문에 일반적으로 문제가 되지 않습니다. 그러나 신뢰 번들을 정기적으로 업데이트해야 할 수도 있습니다.

#### 4.2.5. 서비스

기본적으로 송신 HTTPS 호출을 수행하는 모든 플랫폼 구성요소에서는 RHCOS 신뢰 번들을 사용합니다. `trustedCA` 가 정의된 경우에도 사용됩니다.

RHCOS 노드에서 실행 중인 모든 서비스는 노드의 신뢰 번들을 사용할 수 있습니다.

#### 4.2.6. 관리

이러한 인증서는 사용자가 아닌 시스템에서 관리합니다.

#### 4.2.7. 사용자 정의

사용자 제공 신뢰 번들 업데이트는 다음 중 하나로 구성됩니다.

`trustedCA` 에서 참조하는 구성 맵에서 PEM 인코딩 인증서 업데이트

새 신뢰 번들이 포함된 네임스페이스 `openshift-config` 에 구성 맵을 생성하고 새 구성 맵 이름을 참조하도록 `trustedCA` 업데이트

RHCOS 신뢰 번들에 CA 인증서를 작성하는 메커니즘은 다른 파일을 RHCOS에 작성하는 방법과 같습니다. 이 방법은 머신 구성을 사용하여 수행됩니다. MCO(Machine Config Operator)에서 새 CA 인증서가 포함된 새 머신 구성을 적용하면 나중에 프로그램 `update-ca-trust` 를 실행하고 RHCOS 노드에서 CRI-O 서비스를 다시 시작합니다. 이번 업데이트에서는 노드를 재부팅할 필요가 없습니다. CRI-O 서비스를 다시 시작하면 새 CA 인증서로 신뢰 번들이 자동으로 업데이트됩니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 50-examplecorp-ca-cert
spec:
  config:
    ignition:
      version: 3.1.0
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUVORENDQXh5Z0F3SUJBZ0lKQU51bkkwRDY2MmNuTUEwR0NTcUdTSWIzRFFFQkN3VUFNSUdsTVFzd0NRWUQKV1FRR0V3SlZVekVYTUJVR0ExVUVDQXdPVG05eWRHZ2dRMkZ5YjJ4cGJtRXhFREFPQmdOVkJBY01CMUpoYkdWcApBMmd4RmpBVUJnTlZCQW9NRFZKbFpDQklZWFFzSUVsdVl5NHhFekFSQmdOVkJBc01DbEpsWkNCSVlYUWdTVlF4Ckh6QVpCZ05WQkFNTUVsSmxaQ0JJWVhRZ1NWUWdVbTl2ZENCRFFURWhNQjhHQ1NxR1NJYjNEUUVKQVJZU2FXNW0KWGpDQnBURUxNQWtHQTFVRUJoTUNWVk14RnpBVkJnTlZCQWdNRGs1dmNuUm9JRU5oY205c2FXNWhNUkF3RGdZRApXUVFIREFkU1lXeGxhV2RvTVJZd0ZBWURWUVFLREExU1pXUWdTR0YwTENCSmJtTXVNUk13RVFZRFZRUUxEQXBTCkFXUWdTR0YwSUVsVU1Sc3dHUVlEVlFRRERCSlNaV1FnU0dGMElFbFVJRkp2YjNRZ1EwRXhJVEFmQmdrcWhraUcKMHcwQkNRRVdFbWx1Wm05elpXTkFjbVZrYUdGMExtTnZiVENDQVNJd0RRWUpLb1pJaHZjTkFRRUJCUUFEZ2dFUApCRENDQVFvQ2dnRUJBTFF0OU9KUWg2R0M1TFQxZzgwcU5oMHU1MEJRNHNaL3laOGFFVHh0KzVsblBWWDZNSEt6CmQvaTdsRHFUZlRjZkxMMm55VUJkMmZRRGsxQjBmeHJza2hHSUlaM2lmUDFQczRsdFRrdjhoUlNvYjNWdE5xU28KSHhrS2Z2RDJQS2pUUHhEUFdZeXJ1eTlpckxaaW9NZmZpM2kvZ0N1dDBaV3RBeU8zTVZINXFXRi9lbkt3Z1BFUwpZOXBvK1RkQ3ZSQi9SVU9iQmFNNzYxRWNyTFNNMUdxSE51ZVNmcW5obzNBakxRNmRCblBXbG82MzhabTFWZWJLCkNFTHloa0xXTVNGa0t3RG1uZTBqUTAyWTRnMDc1dkNLdkNzQ0F3RUFBYU5qTUdFd0hRWURWUjBPQkJZRUZIN1IKNXlDK1VlaElJUGV1TDhacXczUHpiZ2NaTUI4R0ExVWRJd1FZTUJhQUZIN1I0eUMrVWVoSUlQZXVMOFpxdzNQegpjZ2NaTUE4R0ExVWRFd0VCL3dRRk1BTUJBZjh3RGdZRFZSMFBBUUgvQkFRREFnR0dNQTBHQ1NxR1NJYjNEUUVCCkR3VUFBNElCQVFCRE52RDJWbTlzQTVBOUFsT0pSOCtlbjVYejloWGN4SkI1cGh4Y1pROGpGb0cwNFZzaHZkMGUKTUVuVXJNY2ZGZ0laNG5qTUtUUUNNNFpGVVBBaWV5THg0ZjUySHVEb3BwM2U1SnlJTWZXK0tGY05JcEt3Q3NhawpwU29LdElVT3NVSks3cUJWWnhjckl5ZVFWMnFjWU9lWmh0UzV3QnFJd09BaEZ3bENFVDdaZTU4UUhtUzQ4c2xqCjVlVGtSaml2QWxFeHJGektjbGpDNGF4S1Fsbk92VkF6eitHbTMyVTB4UEJGNEJ5ZVBWeENKVUh3MVRzeVRtZWwKU3hORXA3eUhvWGN3bitmWG5hK3Q1SldoMWd4VVp0eTMKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=
        mode: 0644
        overwrite: true
        path: /etc/pki/ca-trust/source/anchors/examplecorp-ca.crt
```

머신의 신뢰 저장소는 노드의 신뢰 저장소 업데이트도 지원해야 합니다.

#### 4.2.8. 갱신

RHCOS 노드에서 인증서를 자동 갱신할 수 있는 Operator가 없습니다.

참고

Red Hat에서는 CA 만료 시점을 모니터링하지 않습니다. 그러나 CA의 수명이 길기 때문에 일반적으로 문제가 되지 않습니다. 그러나 신뢰 번들을 정기적으로 업데이트해야 할 수도 있습니다.

#### 4.3.1. 목적

`service-ca` 는 OpenShift Container Platform 클러스터가 배포될 때 자체 서명된 CA를 만드는 Operator입니다.

#### 4.3.2. 만료

사용자 정의 기간은 지원되지 않습니다. 자체 서명된 CA는 `tls.crt` (인증서), `tls.key` (개인 키) 및 `ca-bundle.crt` (CA 번들)의 규정된 이름 `service-ca/signing-key` 로 보안에 저장됩니다.

다른 서비스에서는 다음 명령으로 서비스 리소스에 주석을 달아 서비스 제공 인증서를 요청할 수 있습니다. 이에 응답하여 Operator는 이름 지정된 보안에 대한 `tls.crt` 로 새 인증서를, `tls.key` 로 개인 키를 생성합니다. 이 인증서는 2년간 유효합니다.

```shell
service.beta.openshift.io/serving-cert-secret-name: <secret name>
```

다른 서비스에서는 서비스 CA에서 생성된 인증서의 검증을 지원하기 위해 `service.beta.openshift.io/inject-cabundle: true` 로 주석을 달아 서비스 CA의 CA 번들을 API 서비스 또는 구성 맵 리소스에 삽입하도록 요청할 수 있습니다. 이에 응답하여 Operator는 현재 CA 번들을 API 서비스의 `CABundle` 필드에 쓰거나 `service-ca.crt` 로 구성 맵에 씁니다.

OpenShift Container Platform 4.3.5부터 자동 순환이 지원되며 일부 4.2.z 및 4.3.z 릴리스로 백포트됩니다. 자동 순환을 지원하는 모든 릴리스에서 서비스 CA는 26개월 동안 유효하며 유효 기간이 13개월 미만으로 남아 있으면 자동으로 새로 고칩니다. 필요하면 서비스 CA를 직접 새로 고칠 수 있습니다.

26개월의 서비스 CA 만료 기간은 지원되는 OpenShift Container Platform 클러스터에 대한 업그레이드 예상 간격보다 길기 때문에 서비스 CA 인증서의 비컨트롤 플레인 소비자의 CA는 CA 순환 후와 순환 전 CA 만료 전에 새로 고칩니다.

주의

수동으로 순환된 서비스 CA는 이전 서비스 CA와의 신뢰를 유지 관리하지 않습니다. 클러스터의 Pod가 다시 시작되어 Pod가 새 서비스 CA에서 발급한 서비스 제공 인증서를 사용하고 있는지 확인할 때까지 일시적으로 서비스 중단이 발생할 수 있습니다.

#### 4.3.3. 관리

이러한 인증서는 사용자가 아닌 시스템에서 관리합니다.

#### 4.3.4. 서비스

서비스 CA 인증서를 사용하는 서비스는 다음과 같습니다.

cluster-autoscaler-operator

cluster-monitoring-operator

cluster-authentication-operator

cluster-image-registry-operator

cluster-ingress-operator

cluster-kube-apiserver-operator

cluster-kube-controller-manager-operator

cluster-kube-scheduler-operator

cluster-networking-operator

cluster-openshift-apiserver-operator

cluster-openshift-controller-manager-operator

cluster-samples-operator

cluster-storage-operator

machine-config-operator

console-operator

insights-operator

machine-api-operator

operator-lifecycle-manager

CSI 드라이버 Operator

이것은 포괄적인 목록이 아닙니다.

#### 4.3.5. 추가 리소스

서비스 제공 인증서를 직접 순환

서비스 제공 인증서 보안을 사용하여 서비스 트래픽 보안

#### 4.4.1. 목적

노드 인증서는 클러스터에서 서명하고 kubelet이 Kubernetes API 서버와 통신할 수 있도록 합니다. 이러한 인증서는 부트스트랩 프로세스에서 생성되는 kubelet CA 인증서에서 가져옵니다.

#### 4.4.2. 위치

kubelet CA 인증서는 `openshift-kube-apiserver-operator` 네임스페이스의 `kube-apiserver-to-kubelet-signer` 시크릿에 있습니다.

#### 4.4.3. 관리

이러한 인증서는 사용자가 아닌 시스템에서 관리합니다.

#### 4.4.4. 만료

30일 후에 노드 인증서가 자동으로 순환됩니다.

#### 4.4.5. 갱신

Kubernetes API Server Operator는 292일 내에 새 `kube-apiserver-to-kubelet-signer` CA 인증서를 자동으로 생성합니다. 이전 CA 인증서는 365일 후에 제거됩니다. kubelet CA 인증서가 업데이트되거나 제거되면 노드가 재부팅되지 않습니다.

클러스터 관리자는 다음 명령을 실행하여 kubelet CA 인증서를 수동으로 갱신할 수 있습니다.

```shell-session
$ oc annotate -n openshift-kube-apiserver-operator secret kube-apiserver-to-kubelet-signer auth.openshift.io/certificate-not-after-
```

#### 4.4.6. 추가 리소스

노드 작업

#### 4.5.1. 목적

OpenShift Container Platform 4 이상에서 kubelet은 `/etc/kubernetes/kubeconfig` 에 있는 부트스트랩 인증서를 사용하여 처음에 부트스트랩합니다. 그런 다음 부트스트랩 초기화 프로세스 및 CSR을 생성하기 위한 kubelet 권한 부여가 이어집니다.

이 과정에서 kubelet은 부트스트랩 채널을 통해 통신하면서 CSR을 생성합니다. 컨트롤러 관리자는 CSR에 서명하여 kubelet을 통해 관리하는 인증서를 생성합니다.

#### 4.5.2. 관리

이러한 인증서는 사용자가 아닌 시스템에서 관리합니다.

#### 4.5.3. 만료

이 부트스트랩 인증서는 10년 동안 유효합니다.

kubelet 관리형 인증서는 1년 동안 유효하며 1년 중 80% 정도되는 시점에 자동으로 순환됩니다.

참고

OLM(OpenShift Lifecycle Manager)은 부트스트랩 인증서를 업데이트하지 않습니다.

#### 4.5.4. 사용자 정의

부트스트랩 인증서를 사용자 정의할 수 없습니다.

#### 4.6.1. 목적

etcd 인증서는 etcd-signer를 통해 서명합니다. 노드 인증서는 부트스트랩 프로세스를 통해 생성된 인증 기관(CA)에서 제공합니다.

#### 4.6.2. 만료

CA 인증서는 10년 동안 유효합니다. 피어, 클라이언트 및 서버 인증서는 3년간 유효합니다.

#### 4.6.3. etcd 인증서 교체

`etcd` 인증서는 etcd 클러스터 Operator를 사용하여 자동으로 순환됩니다. 그러나 인증서가 자동으로 교체되기 전에 순환해야 하는 경우 수동으로 교체할 수 있습니다.

프로세스

다음 명령을 실행하여 현재 서명자 인증서의 백업 사본을 만듭니다.

```shell-session
$ oc get secret -n openshift-etcd etcd-signer -oyaml > signer_backup_secret.yaml
```

다음 명령을 실행하여 기존 서명자 인증서를 삭제합니다.

```shell-session
$ oc delete secret -n openshift-etcd etcd-signer
```

다음 명령을 실행하여 정적 포드가 롤아웃될 때까지 기다립니다. 정적 pod 롤아웃을 완료하는 데 몇 분이 걸릴 수 있습니다.

```shell-session
$ oc wait --for=condition=Progressing=False --timeout=15m clusteroperator/etcd
```

#### 4.6.4. 번들에서 사용되지 않는 인증 기관 제거

수동 교체는 이전 서명자 인증서의 공개 키를 제거하기 위해 신뢰 번들을 즉시 업데이트하지 않습니다.

서명자 인증서의 공개 키는 만료 날짜에 제거되지만 공개 키가 만료되기 전에 제거해야 하는 경우 삭제할 수 있습니다.

프로세스

다음 명령을 실행하여 키를 삭제합니다.

```shell-session
$ oc delete configmap -n openshift-etcd etcd-ca-bundle
```

다음 명령을 실행하여 정적 포드 롤아웃을 기다립니다. 번들은 현재 서명자 인증서로 다시 생성되고 알 수 없거나 사용되지 않는 모든 키가 삭제됩니다.

```shell-session
$ oc adm wait-for-stable-cluster --minimum-stable-period 2m
```

#### 4.6.5. etcd 인증서 교체 경고 및 메트릭 서명자 인증서

보류 중인 `etcd` 인증서 만료에 대해 사용자에게 알리는 두 가지 경고:

`etcdSignerCAExpirationWarning`

서명자가 만료될 때까지 730일이 걸립니다.

`etcdSignerCAExpirationCritical`

서명자가 만료될 때까지 365일이 걸립니다.

이러한 경고는 `openshift-etcd` 네임스페이스에 있는 서명자 인증 기관의 만료 날짜를 추적합니다.

다음과 같은 이유로 인증서를 순환할 수 있습니다.

만료 경고가 표시됩니다.

개인 키가 유출됩니다.

중요

개인 키가 유출되면 모든 인증서를 교체해야 합니다.

OpenShift Container Platform 메트릭 시스템에는 `etcd` 서명자가 있습니다. etcd 인증서를 Rotating할 때 다음 지표 매개변수를 대체합니다.

`etcd-signer` 대신 `etcd-metric-signer`

`etcd-ca-bundle` 대신 `etcd-metrics-ca-bundle`

#### 4.6.6. 관리

이러한 인증서는 시스템에서만 관리되며 자동으로 교체됩니다.

#### 4.6.7. 서비스

etcd 인증서는 etcd 멤버 피어와 암호화된 클라이언트 트래픽 간의 암호화된 통신에 사용됩니다. 다음 인증서는 etcd 및 etcd와 통신하는 다른 프로세스를 통해 생성되고 사용됩니다.

피어 인증서: etcd 멤버 간의 통신에 사용됩니다.

클라이언트 인증서: 암호화된 서버-클라이언트 통신에 사용됩니다. 클라이언트 인증서는 현재 API 서버에서만 사용되며 프록시를 제외한 다른 서비스는 etcd에 직접 연결하지 않아야 합니다. 클라이언트 보안(`etcd-client`, `etcd-metric-client`, `etcd-metric-signer`, `etcd-signer`)이 `openshift-config`, `openshift-etcd`, `openshift-etcd-operator`, `openshift-kube-apiserver` 네임스페이스에 추가됩니다.

서버 인증서: etcd 서버가 클라이언트 요청을 인증하는 데 사용합니다.

지표 인증서: 모든 지표 소비자는 지표 클라이언트 인증서를 사용하여 프록시에 연결합니다.

#### 4.6.8. 추가 리소스

이전 클러스터 상태로 복원

#### 4.7.1. 관리

OLM(Operator Lifecycle Manager) 구성 요소(`olm-operator`, `catalog-operator`, `packageserver`, `marketplace-operator`)에 대한 모든 인증서는 시스템에서 관리합니다.

CSV(`ClusterServiceVersion`) 개체에 Webhook 또는 API 서비스가 포함된 Operator를 설치하면 OLM이 이러한 리소스의 인증서를 생성하고 회전합니다. `openshift-operator-lifecycle-manager` 네임스페이스의 리소스의 인증서는 OLM에서 관리합니다.

OLM은 프록시 환경에서 관리하는 Operator의 인증서를 업데이트하지 않습니다. 이러한 인증서는 서브스크립션 구성을 통해 사용자가 관리해야 합니다.

다음 단계

Operator Lifecycle Manager에서 프록시 지원 구성

#### 4.7.2. 추가 리소스

프록시 인증서

기본 수신 인증서 교체

CA 번들 업데이트

#### 4.8.1. 목적

집계된 API 클라이언트 인증서는 집계된 API 서버에 연결할 때 KubeAPIServer를 인증하는 데 사용됩니다.

#### 4.8.2. 관리

이러한 인증서는 사용자가 아닌 시스템에서 관리합니다.

#### 4.8.3. 만료

이 CA는 30일 동안 유효합니다.

관리형 클라이언트 인증서는 30일 동안 유효합니다.

CA 및 클라이언트 인증서는 컨트롤러를 사용하여 자동으로 순환됩니다.

#### 4.8.4. 사용자 정의

집계된 API 서버 인증서를 사용자 지정할 수 없습니다.

#### 4.9.1. 목적

이 인증 기관은 초기 프로비저닝 중에 노드에서 MCS(Machine Config Server)로의 연결을 보호하는 데 사용됩니다.

두 개의 인증서가 있습니다.

자체 서명된 CA, `machine-config-server-ca` 구성 맵(MCS CA)

파생 인증서, `machine-config-server-tls` 시크릿(MCS 인증서)

#### 4.9.1.1. 프로비저닝 세부 정보

RHCOS(Red Hat Enterprise Linux CoreOS)를 사용하는 OpenShift Container Platform 설치는 Ignition을 사용하여 설치됩니다. 이 프로세스는 두 부분으로 나뉩니다.

MCS에서 제공하는 전체 구성의 URL을 참조하는 Ignition 구성이 생성됩니다.

사용자 프로비저닝 infrastucture 설치 방법의 경우 `openshift-install` 명령으로 생성된 `worker.ign` 파일로 Ignition 구성 매니페스트입니다. Machine API Operator를 사용하는 설치 관리자 프로비저닝 인프라 설치 방법의 경우 이 구성이 `worker-user-data` 시크릿으로 표시됩니다.

중요

현재 머신 구성 서버 끝점을 차단하거나 제한하는 방법이 지원되지 않습니다. 기존 구성 또는 상태가 없는 새로 프로비저닝된 머신이 구성을 가져올 수 있도록 머신 구성 서버를 네트워크에 노출해야 합니다. 이 모델에서 trust의 루트는 CSR(인증서 서명 요청) 끝점입니다. 여기서 kubelet은 클러스터에 참여하도록 승인에 대한 인증서 서명 요청을 보냅니다. 이로 인해 시크릿 및 인증서와 같은 중요한 정보를 배포하는 데 머신 구성을 사용해서는 안 됩니다.

머신 구성 서버 엔드포인트, 포트 22623 및 22624가 베어 메탈 시나리오에서 보호되도록 고객은 적절한 네트워크 정책을 구성해야 합니다.

추가 리소스

Machine Config Operator.

OVN-Kubernetes 네트워크 플러그인 정보

#### 4.9.1.2. 신뢰 체인 프로비저닝

MCS CA는 `security.tls.certificateAuthorities` 구성 필드 아래에 Ignition 구성에 삽입됩니다. 그런 다음 MCS는 웹 서버에서 제공하는 MCS 인증서를 사용하여 전체 구성을 제공합니다.

클라이언트는 서버에서 제공하는 MCS 인증서에 해당 인증 기관에 대한 신뢰 체인이 있는지 확인합니다. 이 경우 MCS CA는 해당 권한이며 MCS 인증서에 서명합니다. 이렇게 하면 클라이언트가 올바른 서버에 액세스합니다. 이 경우 클라이언트는 initramfs의 머신에서 실행되는 Ignition입니다.

#### 4.9.1.3. 클러스터 내부의 주요 자료

다음 오브젝트는 `openshift-machine-config-operator` 네임스페이스에 저장됩니다.

MCS CA 번들은 `machine-config-server-ca` 구성 맵으로 저장됩니다. MCS CA 번들은 `MachineConfigServer` TLS 인증서에 대한 모든 유효한 CA를 저장합니다.

MCS CA 서명 키는 `machine-config-server-ca` 시크릿으로 저장됩니다. MCS CA 서명 키는 `MachineConfigServer` TLS 인증서에 서명하는 데 사용됩니다.

MCS 인증서는 `MachineConfigServer` TLS 인증서 및 키를 포함하는 `machine-config-server-tls` 시크릿으로 저장됩니다.

`machine-config-server-ca` 구성 맵은 다음과 같은 방식으로 사용됩니다.

인증서 컨트롤러는 `machine-config-server-ca` configmap이 업데이트될 때마다 `openshift-machine-api` 네임스페이스에서 `*-user-data` 시크릿을 업데이트합니다.

Machine Config Operator는 `machine-config-server-ca` configmap에서 `master-user-data-managed` 및 `worker-user-data-managed` 시크릿을 렌더링합니다.

#### 4.9.2. 관리

현재 이러한 인증서 중 하나를 직접 수정하는 것은 지원되지 않습니다.

#### 4.9.3. 만료

MCS CA 및 MCS 인증서는 10년 동안 유효하며 8년 후에 MCO에 의해 자동으로 순환됩니다.

발급된 제공 인증서는 10년 동안 유효합니다.

#### 4.9.4. 사용자 정의

Machine Config Operator 인증서를 사용자 지정할 수 없습니다.

#### 4.10.1. 목적

애플리케이션은 일반적으로 `<route_name>.apps.<cluster_name>.<base_domain>` 에서 노출됩니다. `<cluster_name>` 및 `<base_domain>` 은 설치 구성 파일에서 가져옵니다. `<route_name>` 은 경로가 지정된 경우 경로의 호스트 필드이거나 경로 이름입니다. 예를 들면 `hello-openshift-default.apps.username.devcluster.openshift.com` 입니다. `hello-openshift` 는 경로의 이름이고 경로는 기본 네임스페이스에 있습니다. 클러스터 관리 CA 인증서를 클라이언트에 배포할 필요없이 클라이언트가 애플리케이션에 액세스하게 합니다. 애플리케이션 콘텐츠를 제공할 때 관리자는 사용자 정의 기본 인증서를 설정해야 합니다.

주의

사용자가 사용자 정의 기본 인증서를 구성할 때까지 Ingress Operator가 자리 표시자로 사용될 Ingress Controller의 기본 인증서를 생성합니다. 프로덕션 클러스터에서는 operator가 생성한 기본 인증서를 사용하지 마십시오.

#### 4.10.2. 위치

사용자 제공 인증서는 `openshift-ingress` 네임스페이스에 `tls` 유형 `Secret` 리소스로 제공되어야 합니다. 사용자 제공 인증서를 사용할 수 있도록 `openshift-ingress-operator` 네임스페이스에서 `IngressController` CR을 업데이트합니다. 이 프로세스에 대한 자세한 내용은 사용자 정의 기본 인증서 설정을 참조하십시오.

#### 4.10.3. 관리

사용자 제공 인증서는 사용자가 관리합니다.

#### 4.10.4. 만료

사용자 제공 인증서는 사용자가 관리합니다.

#### 4.10.5. 서비스

클러스터에 배포된 애플리케이션에서는 기본 수신에 사용자 제공 인증서를 사용합니다.

#### 4.10.6. 사용자 정의

필요에 따라 사용자 관리 인증서가 포함된 보안을 업데이트합니다.

#### 4.10.7. 추가 리소스

기본 수신 인증서 교체

#### 4.11.1. 목적

Ingress Operator에서는 다음을 위해 인증서를 사용합니다.

Prometheus의 지표에 대한 액세스 보안

경로에 대한 액세스 보안

#### 4.11.2. 위치

Ingress Operator 및 Ingress Controller 지표에 대한 액세스를 보호하기 위해 Ingress Operator에서는 서비스 제공 인증서를 사용합니다. Operator가 `service-ca` 컨트롤러에서 고유 지표에 맞는 인증서를 요청하고, `service-ca` 컨트롤러가 `metrics-tls` 라는 보안의 인증서를 `openshift-ingress-operator` 네임스페이스에 둡니다. 또한 Ingress Operator에서 각 Ingress Controller의 인증서를 요청하고 `service-ca` 컨트롤러에서 `router-metrics-certs-<name>` 라는 보안에 인증서를 넣습니다. 여기서 `<name>` 은 `openshift-ingress` 네임스페이스의 Ingress Controller의 이름입니다.

각 Ingress Controller에는 고유 인증서를 지정하지 않는 보안 경로에 사용하는 기본 인증서가 있습니다. 사용자 정의 인증서를 지정하지 않으면 Operator에서 기본적으로 자체 서명된 인증서를 사용합니다. Operator는 자체 서명된 서명 인증서를 사용하여 생성하는 기본 인증서에 서명합니다. Operator는 이 서명 인증서를 생성하여 `openshift-ingress-operator` 네임스페이스의 `router-ca` 라는 보안에 둡니다. Operator가 기본 인증서를 생성하고 `openshift-ingress` 네임스페이스의 `router-certs-<name>` 라는 보안에 기본 인증서를 둡니다(여기서 `<name>` 은 Ingress Controller의 이름임).

주의

사용자가 사용자 정의 기본 인증서를 구성할 때까지 Ingress Operator가 자리 표시자로 사용될 Ingress Controller의 기본 인증서를 생성합니다. 프로덕션 클러스터에서는 operator가 생성한 기본 인증서를 사용하지 마십시오.

#### 4.11.3. 워크플로

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-0.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/1f6a7d5c77035f587ab16d2072b67d80/darkcircle-0.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-1.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/066d390945eb233d66d1b10310fec9e7/darkcircle-1.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-2.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/dffcf5a2ed44061a19f38d92a8a3d1bb/darkcircle-2.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-3.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/e4171dd0f615beb50be5dc701259f444/darkcircle-3.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-4.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/dd170f3f40e17838a75352ca1962f9bb/darkcircle-4.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-5.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/b86066dfcdf40a6c7ce19b770a9d3868/darkcircle-5.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-6.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/3355b6bb1a911bd888724ef147bddf81/darkcircle-6.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-7.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/c375237f874aa152901afcfc636b49aa/darkcircle-7.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-8.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/a6d6413c1aa40b05d8373cb664db1913/darkcircle-8.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-9.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/03e302a74ada37da40eee80ede633c6e/darkcircle-9.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-10.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/df532c957f233ffca7c47f1341e1e491/darkcircle-10.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/darkcircle-11.png" alt="20" kind="diagram" diagram_type="semantic_diagram"]
20
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/a31e8b5875a5bdeae5cad6dd5f4d261f/darkcircle-11.png`_


그림 4.1. 사용자 정의 인증서 워크플로 그림 4.2. 기본 인증서 워크플로

`defaultCertificate` 필드가 비어 있으면 Ingress Operator에서 자체 서명된 CA를 사용하여 지정된 도메인의 제공 인증서를 생성합니다.

Ingress Operator에서 생성한 기본 CA 인증서 및 키. Operator 생성 기본 제공 인증서에 서명하는 데 사용합니다.

기본 워크플로에서는 Ingress Operator가 작성하고 생성된 기본 CA 인증서를 사용하여 서명한 와일드카드 기본 제공 인증서입니다. 사용자 정의 워크플로에서 이 인증서는 사용자 제공 인증서입니다.

라우터 배포. `secrets/router-certs-default` 의 인증서를 기본 프론트 엔드 서버 인증서로 사용합니다.

기본 워크플로에서 와일드카드 기본 제공 인증서(공용 및 개인용 부분)의 콘텐츠가 여기에 복사되므로 OAuth 통합이 가능합니다. 사용자 정의 워크플로에서 이 인증서는 사용자 제공 인증서입니다.

기본 제공 인증서의 공용(인증서) 부분입니다. `configmaps/router-ca` 리소스를 교체합니다.

사용자는 `ingresscontroller` 제공 인증서에 서명한 CA 인증서로 클러스터 프록시 구성을 업데이트합니다. 그러면 `auth`, `console` 및 레지스트리와 같은 구성요소가 제공 인증서를 신뢰할 수 있습니다.

사용자 번들이 제공되지 않는 경우 RHCOS(Red Hat Enterprise Linux CoreOS) 및 사용자 제공 CA 번들 또는 RHCOS 전용 번들을 포함하는 클러스터 전체의 신뢰할 수 있는 CA 번들입니다.

사용자 정의 인증서로 구성된 `ingresscontroller` 를 신뢰하도록 다르 구성요소(예: `auth` 및 `console`)에 지시하는 사용자 정의 CA 인증서 번들입니다.

`trustedCA` 필드는 사용자 제공 CA 번들을 참조하는 데 사용됩니다.

Cluster Network Operator에서 신뢰할 수 있는 CA 번들을 `proxy-ca` 구성 맵에 삽입합니다.

OpenShift Container Platform 4.20 이상에서는 `default-ingress-cert` 를 사용합니다.

#### 4.11.4. 만료

Ingress Operator 인증서의 만료 기간은 다음과 같습니다.

`service-ca` 컨트롤러가 생성하는 메트릭 인증서의 만료 날짜는 생성일로부터 2년입니다.

Operator 서명 인증서의 만료 날짜는 생성일로부터 2년입니다.

Operator가 생성하는 기본 인증서의 만료 날짜는 생성일로부터 2년입니다.

Ingress Operator 또는 `service-ca` 컨트롤러에서 생성하는 인증서에 사용자 정의 만료 기간을 지정할 수 없습니다.

Ingress Operator 또는 `Service-CA` 컨트롤러가 생성하는 인증서에 맞게 OpenShift Container Platform을 설치하면 만료 조건을 지정할 수 없습니다.

#### 4.11.5. 서비스

Prometheus에서는 메트릭을 보호하는 인증서를 사용합니다.

Ingress Operator에서는 서명 인증서를 사용하여 사용자 정의 기본 인증서를 설정하지 않은 Ingress Controller용으로 생성한 기본 인증서에 서명합니다.

보안 경로를 사용하는 클러스터 구성요소는 기본 Ingress Controller의 기본 인증서를 사용할 수 있습니다.

보안 경로를 통해 클러스터로 수신할 때는 경로에서 고유 인증서를 지정하지 않는 한 경로에 액세스하는 Ingress Controller의 기본 인증서를 사용합니다.

#### 4.11.6. 관리

수신 인증서는 사용자가 관리합니다. 자세한 내용은 기본 수신 인증서 교체를 참조하십시오.

#### 4.11.7. 갱신

`service-ca` 컨트롤러에서는 발급한 인증서가 자동으로 순환됩니다. 그러나 다음 명령을 사용하여 서비스 제공 인증서를 직접 순환할 수 있습니다.

```shell
oc delete secret <secret>
```

Ingress Operator에서는 자체 서명 인증서 또는 생성된 기본 인증서가 순환되지 않습니다. Operator가 생성한 기본 인증서는 구성하는 사용자 정의 기본 인증서의 자리 표시자로 사용됩니다.

#### 4.12.1. 만료

모니터링 구성요소는 서비스 CA 인증서로 트래픽을 보호합니다. 이 인증서는 2년 동안 유효하며 서비스 CA 순환 시 13개월마다 자동으로 교체됩니다.

`openshift-monitoring` 또는 `openshift-logging` 네임스페이스에 인증서가 있는 경우 시스템 관리 및 순환이 자동으로 수행됩니다.

#### 4.12.2. 관리

이러한 인증서는 사용자가 아닌 시스템에서 관리합니다.

#### 4.13.1. 위치

컨트롤 플레인 인증서는 다음 네임스페이스에 포함되어 있습니다.

openshift-config-managed

openshift-kube-apiserver

openshift-kube-apiserver-operator

openshift-kube-controller-manager

openshift-kube-controller-manager-operator

openshift-kube-scheduler

#### 4.13.2. 관리

컨트롤 플레인 인증서는 시스템에서 관리하고 자동으로 순환됩니다.

드문 경우지만 컨트롤 플레인 인증서가 만료된 경우 만료된 컨트롤 플레인 인증서에서 복구를 참조하십시오.

### 5.1. Compliance Operator 개요

OpenShift Container Platform Compliance Operator는 다양한 기술 구현을 자동화하고 업계 표준, 벤치마크 및 기준선의 특정 측면과 비교하여 사용자를 지원합니다. Compliance Operator는 감사자가 아닙니다. 이러한 다양한 표준을 준수하거나 인증하려면 QSA(Qualified Security Assessor), 공동 인증 기관(JAB) 또는 기타 업계가 귀하의 환경을 평가할 수 있는 규제 당국을 고용해야 합니다.

Compliance Operator는 이러한 표준에 대한 일반적으로 사용 가능한 정보 및 관행을 기반으로 권장 사항을 제시하고 수정에 도움이 될 수 있지만 실제 규정 준수는 귀하의 책임이 있습니다. 표준을 준수하기 위해 권한 있는 감사자와 협력해야 합니다. 최신 업데이트는 Compliance Operator 릴리스 노트 를 참조하십시오. 모든 Red Hat 제품의 규정 준수 지원에 대한 자세한 내용은 제품 규정 준수 를 참조하십시오.

#### 5.1.1. Compliance Operator 개념

Compliance Operator 이해

사용자 정의 리소스 정의 이해

#### 5.1.2. Compliance Operator 관리

Compliance Operator 설치

Compliance Operator 업데이트

Compliance Operator 관리

Compliance Operator 설치 제거

#### 5.1.3. Compliance Operator 검사 관리

지원되는 규정 준수 프로필

Compliance Operator 검사

Compliance Operator 조정

Compliance Operator 원시 결과 검색

Compliance Operator 수정 관리

고급 Compliance Operator 작업 수행

Compliance Operator 문제 해결

oc-compliance 플러그인 사용

### 5.2. Compliance Operator 릴리스 정보

OpenShift Container Platform 관리자는 Compliance Operator를 통해 클러스터의 필수 규정 준수 상태를 설명하고 격차에 대한 개요와 문제를 해결하는 방법을 제공할 수 있습니다.

이 릴리스 노트는 OpenShift Container Platform의 Compliance Operator 개발을 추적합니다.

Compliance Operator에 대한 개요는 Compliance Operator 이해를 참조하십시오.

최신 릴리스에 액세스하려면 Compliance Operator 업데이트를 참조하십시오.

모든 Red Hat 제품의 규정 준수 지원에 대한 자세한 내용은 제품 규정 준수 를 참조하십시오.

#### 5.2.1. OpenShift Compliance Operator 1.8.0

OpenShift Compliance Operator 1.8.0에 대해 다음 권고를 사용할 수 있습니다.

RHSA-2025:21885 - OpenShift Compliance Operator 1.8.0 버그 수정 및 개선 사항 업데이트

#### 5.2.1.1. 새로운 기능 및 개선 사항

이번 업데이트를 통해 Compliance Operator는 CEL(Common Expression Language) 스캐너를 Cryostat PREVIEW 상태로 제공합니다. CEL 스캐너는 관리자가 CEL 표현식을 사용하여 사용자 정의 보안 정책을 정의하고 적용할 수 있는 새로운 `CustomRule` CRD(Custom Resource Definition)를 구현합니다. 이 새 콘텐츠 형식은 기존 XCCDF(Extensible Configuration Checklist Description Format) 프로필을 대체하지 않지만 사용자 지정 보안 정책을 준수하는 기능을 확장합니다. 자세한 내용은 (CMP-3118)을 참조하십시오.

이전에는 Compliance Operator에서 원시 검사 결과를 저장하기 위해 영구 스토리지가 필요했습니다. 이로 인해 스토리지 인프라가 없는 에지 배포 및 환경에 문제가 발생했습니다. 이번 릴리스에서는 Compliance Operator에서 영구 스토리지 없이 검사 실행을 지원합니다. 관리자는 `ScanSetting` 리소스에서 `rawResultStorage.enabled: false` 를 설정하여 검사 결과 파일의 스토리지를 비활성화하여 규정 준수 검사를 에지 배포 및 단일 노드 OpenShift와 같은 스토리지 제한 환경에서 실행할 수 있습니다. 컴플라이언스 검사 결과는 `ComplianceCheckResult` 리소스를 통해 완전히 사용할 수 있습니다. 이전 버전과의 호환성을 위해 원시 결과 스토리지는 기본적으로 활성화되어 있습니다. 자세한 내용은 (CMP-1225)를 참조하십시오.

이전에는 Compliance Operator에서 `ocp4-bsi` 및 `ocp4-bsi-node` 프로필을 제공했습니다. 이번 릴리스에서는 `rhcos4-bsi` 프로필을 사용할 수 있으므로 Cryostat 표준 적용 범위를 RHCOS 시스템에 확장합니다. 자세한 내용은 (CMP-3720)을 참조하십시오.

이 릴리스에서는 더 이상 사용되지 않는 CIS 1.4.0, CIS 1.5.0, DISA STIG V1R1 및 DISA STIG V2R1 프로필을 제거합니다. 최신 버전은 고객을 위해 더 이상 사용되지 않는 프로필을 교체했습니다. 자세한 내용은 (CMP-3712)을 참조하십시오.

이번 릴리스에서는 ARM 아키텍처 시스템에서 PCI-DSS 프로필 3.2.1 및 4.0.0이 지원됩니다. 자세한 내용은 (CMP-3723)을 참조하십시오.

#### 5.2.1.2. 버그 수정

이번 릴리스에서는 API 서버 암호화에 대한 자동 수정이 이제 OpenShift 버전인 AES-GCM for OpenShift 4.13.0 이상 버전 AES-CBC를 기반으로 하는 적절한 암호화 모드를 적용합니다. 두 암호화 모드는 모든 OpenShift 버전에서 계속 호환됩니다. 자세한 내용은 (CMP-3248)을 참조하십시오.

이번 릴리스 이전에는 Compliance Operator에서 모든 SSH 강화 설정이 포함된 고정 sshd_config 파일을 배포하여 RHCOS 호스트에서 SSH 설정을 수정했습니다. 해당 규칙에 대한 검사에 실패한 경우 의도하지 않은 구성이 SSH로 변경될 수 있습니다. 이번 릴리스에서는 Compliance Operator가 https://github.com/ComplianceAsCode/content/blob/master/shared/macros/10-kubernetes.jinja#L1-L154 에 표시된 규칙에 따라 SSH에 매우 구체적인 수정을 적용합니다. 자세한 내용은 (CMP-3553)을 참조하십시오.

이전 버전의 Compliance Operator의 경우 로그 순환 기능은 `/etc/cron.daily` 폴더에서 `logrotate` 파일을 찾는 데 의존했습니다. 이번 릴리스에서는 Compliance Operator가 `logrotate.timer` 서비스와 함께 작동합니다. 이렇게 하면 Compliance Operator의 안정적인 로그 순환 동작을 제공합니다.

이전 버전의 Compliance Operator의 경우 규정 준수 보고서에서 `STIG ID` 를 생략할 수 있습니다. 이러한 누락은 누락된 `stigref` 및 `stigid` 값으로 인해 발생했습니다. 이번 릴리스에서는 누락이 수정되었으며 이제 `STIG ID` 가 규정 준수 보고서에 안정적으로 표시됩니다.

이번 릴리스 이전에는 Compliance Operator STIG에서 CNTR-OS-000720 규칙을 선택한 규칙 `rhcos4-audit-rules-suid-privilege-function` 이지만 Compliance Operator에서 규칙을 사용할 수 없으므로 출력이 생성되지 않았습니다. 이번 릴리스에서는 Compliance Operator에서 `rhcos4-audit-rules-suid-privilege-function` 규칙을 사용할 수 있으며 검사 출력에 나열됩니다. 자세한 내용은 (CMP-3558)을 참조하십시오.

이전 버전의 Compliance Operator에서는 TLS가 올바르게 활성화되어 있어도 `ocp4-stig -modified-audit-log-forwarding-uses-tls` 규칙에 대해 ocp4-stig 프로필로 스캔할 수 없었습니다. 이는 `ClusterLogForwarder` 리소스에서 `tls://` 필드가 더 이상 필요하지 않기 때문에 검사 출력에 잘못된 `FAIL` 결과가 표시되었습니다. 이번 릴리스에서는 프로토콜 접두사가 필요하지 않으며 검사 출력에서 올바른 결과를 생성합니다. 자세한 내용은 ODF 4.11을 설치하면 route-protected-by-tls 컴플라이언스 검사를 참조하십시오.

이전에는 CIS Benchmark 제어 1.2.31 또는 1.2.33에서 권장하는 대로 API 서버가 지원되지 않는 구성 덮어쓰기를 사용하는지 확인하는 자동화된 방법이 없었습니다. 이 릴리스에서는 지원되지 않는 구성 덮어쓰기를 확인하기 위한 전용 규칙을 제공합니다.

이전 버전의 Compliance Operator의 경우 일부 규칙에 규칙 `resource-requests-limits` 와 같은 주석에서 변수 참조가 누락되었습니다. 이번 릴리스에서는 규칙에 변수 참조를 사용할 수 있으며 잘못된 출력이 제거됩니다. 자세한 내용은 (CMP-3582)을 참조하십시오.

이전에는 `ocp4-routes-rate-limit` 규칙에서 `openshift` 및 `kube` 네임스페이스 외부의 모든 경로에 대한 설정 속도 제한이 필요했습니다. 그러나 중요한 Operator에서 관리하는 다른 네임스페이스는 수정되지 않고 Compliance Operator에서 수정할 수 없기 때문에 기능을 사용하고 검사하면 문제가 발생했습니다. 이번 릴리스에서는 중요한 Operator에서 관리하는 경로에 Compliance Operator의 오류로 플래그가 표시되지 않습니다.

이전 버전의 Compliance Operator에서 `openshift-sdn` 네트워킹 공급자를 `찾을 수 없는 경우 ComplianceScan 에서 경고 SDN` 을 찾을 수 없었습니다. 이번 릴리스에서는 OpenShift-SDN이 활성 네트워킹 공급자가 아닌 경우 Compliance Operator에서 경고를 표시하지 않습니다. 자세한 내용은 (CMP-3591)을 참조하십시오.

이전에는 `TailoredProfile` 에서 중복 변수가 실수로 생성되어 Compliance Operator에서 올바르게 감지하지 못했습니다. 이번 릴리스에서는 `TailoredProfile` 의 중복 `setValues` 가 확인되고 규정 준수 검사에서 경고 이벤트를 트리거합니다.

이전 버전의 Compliance Operator에서는 `clusterlogforwarder` 출력 구성에 URL 키가 없는 맵이 포함된 경우 ocp4-audit-log-forwarding-uses-tls 규칙이 실패했습니다. 이번 릴리스에서는 URL 필드가 있는 출력에 대한 규칙이 올바르게 필터링되어 `clusterlogforwarder` 에 대해 TLS가 올바르게 활성화될 때 `PASS` 가 표시됩니다. 자세한 내용은 (CMP-3597)을 참조하십시오.

이전 버전의 Compliance Operator에서는 `rhcos4-service-systemd-coredump-disabled` 규칙에 대해 클러스터를 검사한 후 수정이 생성되지 않았습니다. 이번 릴리스에서는 `rhcos4-service-systemd-coredump-disabled` 에 대한 수정이 제공됩니다.

이전 버전의 Compliance Operator에서는 구성이 올바른 경우에도 `imagestream.spec.tags.importPolicy.scheduled` 설정을 확인하는 규칙입니다. 이번 릴리스에서는 규칙에서 샘플 Operator가 관리하는 이미지 스트림과 ClusterVersion이 소유한 이미지 스트림을 올바르게 제외하여 정확한 규정 준수 상태 보고를 생성합니다.

이전 릴리스에서 Compliance Operator에는 지원되지 않는 구성 덮어쓰기를 사용한 오래된 TLS 암호화 제품군 규칙이 포함되어 있습니다. 이번 릴리스에서는 이러한 오래된 규칙이 기본 프로필에서 제거되었습니다. 또한 `ocp4-kubelet-configure-cipher-suites-ingresscontroller` 규칙의 이름이 `ocp4-ingress-controller-tls-cipher-suites` 로 변경되었습니다. 자세한 내용은 (CMP-3606)을 참조하십시오.

이전 버전의 Compliance Operator에서는 프로필 사용 중단 확인 중에 사용자 정의 콘텐츠 이미지로 직접 `ComplianceScan` 을 생성할 수 없습니다. 이번 릴리스에서는 Compliance Operator에서 `ProfileBundle` 을 확인할 수 없는 케이스를 정상적으로 처리하고 검사 실패 대신 정보 메시지를 기록합니다. 자세한 내용은 (CMP-3613)을 참조하십시오.

이전에는 Compliance Operator에서 `ocp4-routes-protected-by-tls` 규칙을 사용하여 NON-COMPLIANT로 패스스루가 잘못 플래그를 지정했습니다. 이번 릴리스에서는 TLS 종료를 백엔드 애플리케이션에 위임하기 때문에 통과 경로가 이 규칙에서 올바르게 제외됩니다.

#### 5.2.2. OpenShift Compliance Operator 1.7.1

OpenShift Compliance Operator 1.7.1에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2025:14639 - OpenShift Compliance Operator 1.7.1 버그 수정 업데이트

참고

OpenShift Compliance Operator 1.7.1은 IBM Z® (`s390x`) 아키텍처에서 PCI-DSS 버전 3.2.1 및 4.0.0을 지원합니다.

#### 5.2.2.1. 버그 수정

이전에는 메모리 부족으로 인해 Compliance Operator의 `일시 중지` 컨테이너를 종료하여 `OOMKilled 상태가 표시될 수 있었습니다. 이번 업데이트를 통해 오류를 방지하고 전체 안정성을 개선하기 위해 'pauser` 컨테이너의 메모리 제한이 증가합니다. (OCPBUGS-50924)

#### 5.2.3. OpenShift Compliance Operator 1.7.0

OpenShift Compliance Operator 1.7.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2025:3728 - OpenShift Compliance Operator 1.7.0 버그 수정 및 개선 사항 업데이트

#### 5.2.3.1. 새로운 기능 및 개선 사항

이제 `aarch64`, `x86, ppc64le 및 s390x` 아키텍처에 설치된 Compliance Operator에 `must-gather` 확장을 사용할 수 있습니다. `must-gather` 툴에서는 Red Hat 고객 지원 및 엔지니어링에 중요한 구성 세부 정보를 제공합니다. 자세한 내용은 Compliance Operator의 must-gather 툴 사용을 참조하십시오.

Compliance Operator 1.7.0에 CIS 벤치마크 지원이 추가되었습니다. 지원되는 프로필은 CIS OpenShift Benchmark 1.7.0입니다. 자세한 내용은 (CMP-3081)를 참조하십시오.

Compliance Operator는 CIS OpenShift Benchmark 1.7.0 및 FedRAMP Moderate Revision 4의 `aarch64` 아키텍처에서 지원됩니다. 자세한 내용은 (CMP-2960)를 참조하십시오.

Compliance Operator 1.7.0에서는 OpenShift 및 RHCOS에 대해 OpenShift DISA STIG V2R2 프로필을 지원합니다. 자세한 내용은 (CMP-3142)를 참조하십시오.

Compliance Operator 1.7.0에서는 CIS 1.4 프로필 사용 중단, CIS 1.5 프로필, DISA STIG V1R1 프로필 및 DISA STIG V2R1 프로필과 같은 이전 버전의 지원되지 않는 프로필 버전 사용 중단을 지원합니다. 자세한 내용은 (CMP-3149)를 참조하십시오.

이 Compliance Operator 1.7.0 릴리스에서는 이전 CIS 및 DISA STIG 프로파일의 사용 중단은 Compliance Operator 1.8.0이 표시된 상태에서 이전 프로필이 더 이상 지원되지 않음을 의미합니다. 자세한 내용은 (CMP-3284)를 참조하십시오.

이번 Compliance Operator 1.7.0 릴리스와 함께 OpenShift에 Cryostat 프로파일 지원이 추가되었습니다. 자세한 내용은 KCS 문서 Cryostat Quick Check 및 Cryostat

규정 준수 요약 을 참조하십시오.

#### 5.2.3.2. 버그 수정

이번 릴리스 이전에는 Compliance Operator에서 `s390x` 아키텍처의 파일 시스템 구조 차이로 인해 불필요한 수정 권장 사항을 제공합니다. 이번 릴리스에서는 Compliance Operator에서 파일 시스템 구조의 차이점을 인식하고 잘못된 수정을 제공하지 않습니다. 이번 업데이트를 통해 이제 규칙이 더 명확하게 정의됩니다. (OCPBUGS-33194)

이전에는 `ocp4-etcd-unique-ca` 규칙에 대한 지침이 OpenShift 4.17 이상에서 작동하지 않았습니다. 이번 업데이트를 통해 지침 및 실행 가능한 단계가 수정되었습니다. (OCPBUGS-42350)

Compliance Operator를CLO(Cluster Logging Operator) 버전 6.0과 함께 사용하면 다양한 규칙이 실패했습니다. 이는 CLO가 사용하는 CRD에 대한 이전 버전과 호환되지 않는 변경 때문입니다. Compliance Operator는 해당 CRD를 사용하여 로깅 기능을 확인합니다. CLO에서 PCI-DSS 프로필을 지원하도록 CRD가 수정되었습니다. (OCPBUGS-43229)

CLO(Cluster Logging Operator) 6.0을 설치한 후 `clusterlogforwarder` 리소스의 API 버전이 변경되어 ComplianceCheckResult `ocp4-cis-audit-log-forwarding-enabled` 가 실패했습니다. 이제 observability.openshift.io API 그룹의 일부인 새 API에서 로그 수집 및 전달 구성이 지정됩니다. (OCPBUGS-43585)

이전 버전의 Compliance Operator의 경우 검사에서 Operator Pod의 조정 루프에 대한 오류 로그를 생성합니다. 이번 릴리스에서는 Compliance Operator 컨트롤러 논리가 더 안정적입니다. (OCPBUGS-51267)

이전에는 `file-integrity-exists` 규칙 또는 `file-integrity-notification-enabled` 가 `aarch64` OpenShift 클러스터에서 실패했습니다. 이번 업데이트를 통해 이러한 규칙은 `arch64` 시스템에서 `NOT-APPLICABLE` 으로 평가됩니다. (OCPBUGS-52884)

이번 릴리스 이전에는 Compliance Operator 규칙 `kubelet-configure-tls-cipher-suites` 가 API 서버 암호에 실패했습니다. 이로 인해 `E2E-FAILURE` 상태가 발생합니다. OpenShift 4.18에 포함된 RFC 8446의 새 암호를 확인하도록 규칙이 업데이트되었습니다. 이제 규칙이 올바르게 평가되고 있습니다. (OCPBUGS-54212)

이전에는 Compliance Operator 플랫폼 검사에 실패하고 `Ignition 구성을 구문 분석하지 못했습니다`. 이번 릴리스에서는 해당 OpenShift 버전을 사용할 수 있는 경우 4.19 클러스터에서 Compliance Operator를 실행할 수 있습니다. (OCPBUGS-54403)

이번 Compliance Operator 릴리스 이전에는 플랫폼을 인식하지 못하여 불필요한 오류가 발생했습니다. 이제 규칙이 다른 아키텍처에 올바르게 이식되었으므로 이러한 규칙이 올바르게 실행되고 사용자는 사용 중인 아키텍처에 따라 일부 Compliance Check Results 보고를 적절하게 확인할 수 있습니다. (OCPBUGS-53041)

이전에는 `file-groupowner-ovs-conf-db-hugetlbf` 규칙에서 예기치 않게 실패했습니다. 이번 릴리스에서는 필요한 결과인 경우에만 규칙이 실패합니다. (OCPBUGS-55190)

#### 5.2.4. OpenShift Compliance Operator 1.6.2

OpenShift Compliance Operator 1.6.2에서 다음 권고를 사용할 수 있습니다.

RHBA-2025:2659 - OpenShift Compliance Operator 1.6.2 업데이트

CVE-2024-45338은 Compliance Operator 1.6.2 릴리스에서 해결되었습니다. (CVE-2024-45338)

#### 5.2.5. OpenShift Compliance Operator 1.6.1

OpenShift Compliance Operator 1.6.1에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2024:10367 - OpenShift Compliance Operator 1.6.1 update

이번 업데이트에서는 기본 기본 이미지의 업그레이드된 종속 항목이 포함되어 있습니다.

#### 5.2.6. OpenShift Compliance Operator 1.6.0

OpenShift Compliance Operator 1.6.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2024:6761 - OpenShift Compliance Operator 1.6.0 버그 수정 및 개선 사항 업데이트

#### 5.2.6.1. 새로운 기능 및 개선 사항

Compliance Operator에는 이제 PCI-DSS(Payment Card Industry Data Security Standard) 버전 4에 대해 지원되는 프로필이 포함되어 있습니다. 자세한 내용은 지원되는 규정 준수 프로필을 참조하십시오.

Compliance Operator에는 이제 DISA STIG(Security Technical Implementation Guide) V2R1에 대해 지원되는 프로필이 포함되어 있습니다. 자세한 내용은 지원되는 규정 준수 프로필을 참조하십시오.

x86, `ppc64le`, `s390 x` 아키텍처에 설치된 Compliance Operator에 `must-gather` 확장을 사용할 수 있습니다. `must-gather` 툴에서는 Red Hat 고객 지원 및 엔지니어링에 중요한 구성 세부 정보를 제공합니다. 자세한 내용은 Compliance Operator의 must-gather 툴 사용을 참조하십시오.

#### 5.2.6.2. 버그 수정

이번 릴리스 이전에는 `ocp4-route-ip-whitelist` 규칙에 대한 잘못된 설명으로 인해 잘못된 오류가 발생하여 잘못된 구성이 발생할 수 있었습니다. 이번 업데이트를 통해 이제 규칙이 더 명확하게 정의됩니다. (CMP-2485)

이전에는 `DONE` 상태 `ComplianceScan` 의 모든 `ComplianceCheckResults` 보고가 불완전했습니다. 이번 업데이트를 통해 `DONE` 상태로 `ComplianceScan` 의 총 `ComplianceCheckResult` 수를 보고하기 위해 주석이 추가되었습니다. (CMP-2615)

이전 버전에서는 `ocp4-cis-scc-limit-container-allowed-capabilities` 규칙 설명에 모호한 지침이 포함되어 사용자 간에 혼동이 발생했습니다. 이번 업데이트를 통해 규칙 설명 및 실행 가능한 단계가 명확하게 표시됩니다. (OCPBUGS-17828)

이번 업데이트 이전에는 sysctl 구성으로 RHCOS4 규칙에 대한 특정 자동 수정으로 영향을 받는 클러스터의 검사에 실패했습니다. 이번 업데이트를 통해 올바른 sysctl 설정이 적용되고 FedRAMP High 프로파일의 RHCOS4 규칙이 올바르게 검사를 전달합니다. (OCPBUGS-19690)

이번 업데이트 이전에는 필터와 관련된 문제로 인해 규정 준수 확인 중에 `rhacs-operator-controller-manager` 배포에 오류가 발생했습니다. 이번 업데이트를 통해 필터 표현식이 업데이트되고 `rhacs-operator-controller-manager` 배포는 컨테이너 리소스 제한과 관련된 규정 준수 검사에서 제외되어 잘못된 잘못된 결과가 제거됩니다. (OCPBUGS-19690)

```shell
jq
```

```shell
jq
```

이번 업데이트 이전에는 `rhcos4-high` 및 `rhcos4-moderate` 프로필이 잘못 지정된 구성 파일의 값을 확인했습니다. 이로 인해 일부 검사에 실패할 수 있었습니다. 이번 업데이트를 통해 `rhcos4` 프로필에서 올바른 구성 파일을 확인하고 검사가 올바르게 통과합니다. (OCPBUGS-31674)

이전에는 `oauthclient-inactivity-timeout` 규칙에 사용된 `accessokenInactivityTimeoutSeconds` 변수로 인해 DISA STIG 스캔을 수행할 때 `FAIL` 상태가 발생했습니다. 이번 업데이트를 통해 `accessTokenInactivityTimeoutSeconds` 변수가 올바르게 작동하고 `PASS` 상태를 올바르게 적용할 수 있습니다. (OCPBUGS-32551)

이번 업데이트 이전에는 규칙에 대한 일부 주석이 업데이트되지 않아 잘못된 제어 표준이 표시되었습니다. 이번 업데이트를 통해 규칙에 대한 주석이 올바르게 업데이트되어 올바른 제어 표준이 표시됩니다. (OCPBUGS-34982)

이전 버전에서는 ServiceMonitor 구성에서 Compliance Operator 1.5.1로 업그레이드할 때 `ServiceMonitor` 구성에서 잘못 참조된 시크릿으로 인해 Prometheus Operator와의 통합 문제가 발생했습니다. 이번 업데이트를 통해 Compliance Operator는 `ServiceMonitor` 메트릭에 대한 토큰이 포함된 시크릿을 정확하게 참조합니다. (OCPBUGS-39417)

#### 5.2.7. OpenShift Compliance Operator 1.5.1

OpenShift Compliance Operator 1.5.1에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2024:5956 - OpenShift Compliance Operator 1.5.1 버그 수정 및 개선 사항 업데이트

#### 5.2.8. OpenShift Compliance Operator 1.5.0

OpenShift Compliance Operator 1.5.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2024:3533 - OpenShift Compliance Operator 1.5.0 버그 수정 및 개선 사항 업데이트

#### 5.2.8.1. 새로운 기능 및 개선 사항

이번 업데이트를 통해 Compliance Operator는 더 쉽게 프로그래밍할 수 있도록 고유한 프로필 ID를 제공합니다. (CMP-2450)

이번 릴리스에서는 Compliance Operator가 ROSA HCP 환경에서 테스트 및 지원됩니다. Compliance Operator는 ROSA HCP에서 실행할 때 노드 프로필만 로드합니다. 이는 Red Hat 관리 플랫폼이 컨트롤 플레인에 대한 액세스를 제한하기 때문에 플랫폼 프로필이 운영자의 기능에 무관하게 됩니다. (CMP-2581)

#### 5.2.8.2. 버그 수정

CVE-2024-2961은 Compliance Operator 1.5.0 릴리스에서 해결되었습니다. (CVE-2024-2961)

이전에는 ROSA HCP 시스템의 경우 프로필 목록이 올바르지 않았습니다. 이번 업데이트를 통해 Compliance Operator에서 올바른 프로필 출력을 제공할 수 있습니다. (OCPBUGS-34535)

이번 릴리스에서는 맞춤형 프로필의 `ocp4-var-network-policies-namespaces-exempt-regex` 변수를 설정하여 `ocp4-configure-network-policies-namespaces` 검사에서 네임스페이스를 제외할 수 있습니다. (CMP-2543)

#### 5.2.9. OpenShift Compliance Operator 1.4.1

OpenShift Compliance Operator 1.4.1에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2024:1830 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.9.1. 새로운 기능 및 개선 사항

이번 릴리스에서는 Compliance Operator에서 CIS OpenShift 1.5.0 프로필 규칙을 제공합니다. (CMP-2447)

이번 업데이트를 통해 Compliance Operator는 이제 `OCP4 STIG ID` 및 `SRG` 에 프로필 규칙을 제공합니다. (CMP-2401)

이번 업데이트를 통해 `s390x` 에 더 이상 사용되지 않는 규칙이 제거되었습니다. (CMP-2471)

#### 5.2.9.2. 버그 수정

이전에는 RHEL(Red Hat Enterprise Linux) 9를 사용하는 RHCOS(Red Hat Enterprise Linux CoreOS) 시스템의 경우 `ocp4-kubelet-enable-protect-kernel-sysctl-file-exist` 규칙의 애플리케이션이 실패했습니다. 이번 업데이트에서는 규칙을 `ocp4-kubelet-enable-protect-kernel-sysctl` 로 대체합니다. 이제 자동 수정이 적용되면 이 규칙의 적용 시 RHEL 9 기반 RHCOS 시스템에 `PASS` 가 표시됩니다. (OCPBUGS-13589)

이전에는 프로필 `rhcos4-e8` 을 사용하여 규정 준수 수정을 적용한 후 코어 사용자 계정에 SSH를 사용하여 노드에 더 이상 액세스할 수 없었습니다. 이번 업데이트를 통해 'sshkey1 옵션을 사용하여 SSH를 통해 노드에 액세스할 수 있습니다. (OCPBUGS-18331)

이전에는 OpenShift Container Platform의 게시된 `STIG` 에 대한 요구 사항을 충족하는 CaC에서 `STIG` 프로필에 누락된 규칙이 누락되었습니다. 이번 업데이트를 통해 수정 시 클러스터는 Compliance Operator를 사용하여 수정할 수 있는 `STIG` 요구 사항을 충족합니다. (OCPBUGS-26193)

이전 버전에서는 여러 제품에 대해 다양한 유형의 프로필을 사용하여 `ScanSettingBinding` 오브젝트를 생성하면 바인딩의 여러 제품 유형에 대한 제한이 무시되었습니다. 이번 업데이트를 통해 이제 `ScanSettingBinding` 오브젝트의 프로필 유형에 관계없이 제품 검증에서 여러 제품을 사용할 수 있습니다. (OCPBUGS-26229)

이전 버전에서는 `rhcos4-service-debug-shell-disabled` 규칙을 실행하면 auto-remediation이 적용된 후에도 `FAIL` 로 표시되었습니다. 이번 업데이트를 통해 `rhcos4-service-debug-shell-disabled` 규칙을 실행하면 자동 복구가 적용된 후 `PASS` 가 표시됩니다. (OCPBUGS-28242)

이번 업데이트를 통해 `rhcos4-banner-etc-issue` 규칙 사용에 대한 지침이 개선되었습니다. (OCPBUGS-28797)

이전에는 `api_server_api_priority_flowschema_catch_all` 규칙에서 OpenShift Container Platform 4.16 클러스터에서 `FAIL` 상태를 제공했습니다. 이번 업데이트를 통해 `api_server_api_priority_flowschema_catch_all` 규칙은 OpenShift Container Platform 4.16 클러스터에서 `PASS` 상태를 제공합니다. (OCPBUGS-28918)

이전에는 `ScanSettingBinding` (SSB) 오브젝트에 표시된 완료된 검사에서 프로필이 제거되면 Compliance Operator에서 이전 검사를 제거하지 않았습니다. 나중에 삭제된 프로필을 사용하여 새 SSB를 시작할 때 Compliance Operator에서 결과를 업데이트하지 못했습니다. 이번 Compliance Operator 릴리스에서 새로운 SSB에 새로운 규정 준수 검사 결과가 표시됩니다. (OCPBUGS-29272)

이전에는 `ppc64le` 아키텍처에서 지표 서비스가 생성되지 않았습니다. 이번 업데이트를 통해 `ppc64le` 아키텍처에 Compliance Operator v1.4.1을 배포할 때 메트릭 서비스가 올바르게 생성됩니다. (OCPBUGS-32797)

이전 버전에서는 HyperShift 호스트 클러스터에서 `ocp4-pci-dss 프로필이` 있는 검사에서 `필터로 인해 복구할 수 없는 오류로 인해 문제가 반복될 수` 없었습니다. 이번 릴리스에서는 `ocp4-pci-dss` 프로파일에 대한 검사가 `완료된` 상태에 도달하고 `규정 준수` 또는 `비준수` 테스트 결과를 반환합니다. (OCPBUGS-33067)

#### 5.2.10. OpenShift Compliance Operator 1.4.0

OpenShift Compliance Operator 1.4.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:7658 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.10.1. 새로운 기능 및 개선 사항

이번 업데이트를 통해 기본 `작업자` 및 `마스터` 노드 풀 외부에서 사용자 정의 노드 풀을 사용하는 클러스터는 더 이상 Compliance Operator가 해당 노드 풀에 대한 구성 파일을 집계하도록 추가 변수를 제공할 필요가 없습니다.

이제 `ScanSetting.suspend` 속성을 `True` 로 설정하여 검사 일정을 일시 중지할 수 있습니다. 이를 통해 사용자는 `ScanSettingBinding` 을 삭제하고 다시 생성할 필요 없이 검사 일정을 일시 중지하고 다시 활성화할 수 있습니다. 이렇게 하면 유지 관리 기간 동안 검사 일정을 일시 중지하는 작업이 간소화됩니다. (CMP-2123)

Compliance Operator는 이제 `Profile` 사용자 정의 리소스에서 선택적 `버전` 속성을 지원합니다. (CMP-2125)

Compliance Operator에서 `ComplianceRules` 에서 프로필 이름을 지원합니다. (CMP-2126)

이번 릴리스에서는 Compliance Operator 호환성과 `cronjob` API 개선 사항이 개선되었습니다. (CMP-2310)

#### 5.2.10.2. 버그 수정

이전 버전에서는 Windows 노드가 있는 클러스터에서 규정 준수 검사에서 Windows 노드를 건너뛰지 않았기 때문에 자동 수정이 적용된 후 일부 규칙이 실패합니다. 이번 릴리스에서는 스캔 시 Windows 노드를 올바르게 건너뜁니다. (OCPBUGS-7355)

이번 업데이트를 통해 다중 경로를 사용하는 Pod의 루트 볼륨 마운트에 대해 `rprivate` 기본 마운트 전파가 올바르게 처리됩니다. (OCPBUGS-17494)

이전에는 Compliance Operator에서 수정을 적용하는 동안 규칙을 조정하지 않고 `coreos_vsyscall_kernel_argument` 에 대한 수정을 생성했습니다. 릴리스 1.4.0을 사용하면 `coreos_vsyscall_kernel_argument` 규칙이 커널 인수를 적절하게 평가하고 적절한 수정을 생성합니다.(OCPBUGS-8041)

이번 업데이트 이전에는 auto-remediation이 적용된 후에도 `rhcos4-audit-rules-login-events-faillock` 이 실패했습니다. 이번 업데이트를 통해 auto-remediation 후 `rhcos4-audit-rules-login-events-faillock` 실패 잠금이 올바르게 적용됩니다. (OCPBUGS-24594)

이전에는 Compliance Operator 1.3.1에서 Compliance Operator 1.4.0으로 업그레이드하면 OVS 규칙 검사 결과가 `PASS` 에서 `NOT-APPLICABLE` 로 전환되었습니다. 이번 업데이트를 통해 OVS 규칙 검사 결과에 `PASS` 가 표시됩니다(OCPBUGS-25323)

#### 5.2.11. OpenShift Compliance Operator 1.3.1

OpenShift Compliance Operator 1.3.1에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:5669 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

이번 업데이트에서는 기본 종속성의 CVE를 해결합니다.

#### 5.2.11.1. 새로운 기능 및 개선 사항

FIPS 모드에서 실행되는 OpenShift Container Platform 클러스터에서 Compliance Operator를 설치하고 사용할 수 있습니다.

중요

클러스터의 FIPS 모드를 활성화하려면 FIPS 모드에서 작동하도록 구성된 RHEL(Red Hat Enterprise Linux) 컴퓨터에서 설치 프로그램을 실행해야 합니다. RHEL에서 FIPS 모드를 구성하는 방법에 대한 자세한 내용은 RHEL을 FIPS 모드로 전환 을 참조하십시오.

FIPS 모드로 부팅된 Red Hat Enterprise Linux(RHEL) 또는 Red Hat Enterprise Linux CoreOS(RHCOS)를 실행할 때 OpenShift Container Platform 핵심 구성 요소는 x86_64, ppc64le 및 s390x 아키텍처에서만 FIPS 140-2/140-3 검증을 위해 NIST에 제출된 RHEL 암호화 라이브러리를 사용합니다.

#### 5.2.11.2. 알려진 문제

Windows 노드가 있는 클러스터에서 규정 준수 검사로 Windows 노드를 건너뛰지 않기 때문에 자동 수정이 적용된 후 일부 규칙이 실패합니다. 스캔할 때 Windows 노드를 건너뛰어야 하므로 예상된 결과와 다릅니다. (OCPBUGS-7355)

#### 5.2.12. OpenShift Compliance Operator 1.3.0

OpenShift Compliance Operator 1.3.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:5102 - OpenShift Compliance Operator 개선 사항 업데이트

#### 5.2.12.1. 새로운 기능 및 개선 사항

OpenShift Container Platform용 DISA-STIG(DISA-STIG)는 Compliance Operator 1.3.0에서 사용할 수 있습니다. 자세한 내용은 지원되는 규정 준수 프로필을 참조하십시오.

Compliance Operator 1.3.0은 이제 OpenShift Container Platform 플랫폼 및 노드 프로필에 대해 NIST 800-53 Moderate-Impact Baseline용 IBM Power® 및 IBM Z®를 지원합니다.

#### 5.2.13. OpenShift Compliance Operator 1.2.0

OpenShift Compliance Operator 1.2.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:4245 - OpenShift Compliance Operator enhancement update

#### 5.2.13.1. 새로운 기능 및 개선 사항

이제 플랫폼 및 노드 애플리케이션에서 CIS OpenShift Container Platform 4 Benchmark v1.4.0 프로필을 사용할 수 있습니다. CIS OpenShift Container Platform v4 벤치마크를 찾으려면 CIS 벤치마크로 이동하여 최신 CIS 벤치마크 다운로드를 클릭합니다. 여기에서 등록하여 벤치마크를 다운로드할 수 있습니다.

중요

Compliance Operator 1.2.0으로 업그레이드하면 CIS OpenShift Container Platform 4 벤치마크 1.1.0 프로필을 덮어씁니다.

OpenShift Container Platform 환경에 기존 `cis` 및 `cis-node` 수정이 포함된 경우 Compliance Operator 1.2.0으로 업그레이드한 후 검사 결과에 몇 가지 차이점이 있을 수 있습니다.

`scc-limit-container-allowed-capabilities` 규칙에 대해 SCC(보안 컨텍스트 제약 조건) 감사에 대한 추가 명확성을 사용할 수 있습니다.

#### 5.2.14. OpenShift Compliance Operator 1.1.0

OpenShift Compliance Operator 1.1.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:3630 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.14.1. 새로운 기능 및 개선 사항

이제 `ComplianceScan` CRD(사용자 정의 리소스 정의) 상태에서 시작 및 종료 타임스탬프를 사용할 수 있습니다.

Compliance Operator는 `서브스크립션` 파일을 생성하여 소프트웨어 카탈로그를 사용하여 호스팅된 컨트롤 플레인에 배포할 수 있습니다. 자세한 내용은 호스팅된 컨트롤 플레인에 Compliance Operator 설치를 참조하십시오.

#### 5.2.14.2. 버그 수정

이번 업데이트 이전에는 일부 Compliance Operator 규칙 지침이 표시되지 않았습니다. 이번 업데이트 후 다음 규칙에 대한 지침이 개선되었습니다.

`classification_banner`

`oauth_login_template_set`

`oauth_logout_url_set`

`oauth_provider_selection_set`

`ocp_allowed_registries`

`ocp_allowed_registries_for_import`

(OCPBUGS-10473)

이번 업데이트 이전에는 정확성 및 규칙 지침이 명확하지 않았습니다. 이번 업데이트 후 다음 `sysctl` 규칙에 대해 검사 정확도와 지침이 개선되었습니다.

`kubelet-enable-protect-kernel-sysctl`

`kubelet-enable-protect-kernel-sysctl-kernel-keys-root-maxbytes`

`kubelet-enable-protect-kernel-sysctl-kernel-keys-root-maxkeys`

`kubelet-enable-protect-kernel-sysctl-kernel-panic`

`kubelet-enable-protect-kernel-sysctl-kernel-panic-on-oops`

`kubelet-enable-protect-kernel-sysctl-vm-overcommit-memory`

`kubelet-enable-protect-kernel-sysctl-vm-panic-on-oom`

(OCPBUGS-11334)

이번 업데이트 이전에는 `ocp4-alert-receiver-configured` 규칙에 지침이 포함되어 있지 않았습니다. 이번 업데이트를 통해 이제 `ocp4-alert-receiver 구성` 규칙에 향상된 지침이 포함되어 있습니다. (OCPBUGS-7307)

이번 업데이트 이전에는 `rhcos4-sshd-set-loglevel-info` 규칙이 `rhcos4-e8` 프로필에 대해 실패했습니다. 이번 업데이트를 통해 `sshd-set-loglevel-info` 규칙에 대한 수정이 올바른 구성 변경 사항을 적용하도록 업데이트되어 수정을 적용한 후 후속 검사가 통과할 수 있습니다. (OCPBUGS-7816)

이번 업데이트 이전에는 최신 Compliance Operator 설치가 포함된 OpenShift Container Platform의 새 설치가 `scheduler-no-bind-address` 규칙에서 실패했습니다. 이번 업데이트를 통해 매개변수가 제거된 이후 최신 버전의 OpenShift Container Platform에서 `scheduler-no-bind-address` 규칙이 비활성화되어 있습니다. (OCPBUGS-8347)

#### 5.2.15. OpenShift Compliance Operator 1.0.0

OpenShift Compliance Operator 1.0.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:1682 - OpenShift Compliance Operator 버그 수정 업데이트

#### 5.2.15.1. 새로운 기능 및 개선 사항

Compliance Operator가 안정되어 릴리스 채널이 `stable` 로 업그레이드되었습니다. 향후 릴리스에서는 Semantic Versioning 을 따릅니다. 최신 릴리스에 액세스하려면 Compliance Operator 업데이트를 참조하십시오.

#### 5.2.15.2. 버그 수정

이번 업데이트 이전에는 compliance_operator_compliance_scan_error_total 지표에 오류 메시지마다 다른 값이 있는 ERROR 라벨이 있었습니다. 이번 업데이트를 통해 compliance_operator_compliance_scan_error_total 메트릭이 값이 증가하지 않습니다. (OCPBUGS-1803)

이번 업데이트 이전에는 `ocp4-api-server-audit-log-maxsize` 규칙이 `FAIL` 상태가 되었습니다. 이번 업데이트를 통해 오류 메시지가 메트릭에서 제거되어 모범 사례에 따라 메트릭의 카디널리티가 줄어듭니다. (OCPBUGS-7520)

이번 업데이트 이전에는 설치 후 FIPS를 활성화하도록 `rhcos4-enable-fips-mode` 규칙 설명이 잘못 표시될 수 있었습니다. 이번 업데이트를 통해 `rhcos4-enable-fips-mode` 규칙 설명은 설치 시 FIPS를 활성화해야 함을 명확히 합니다. (OCPBUGS-8358)

#### 5.2.16. OpenShift Compliance Operator 0.1.61

OpenShift Compliance Operator 0.1.61에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:0557 - OpenShift Compliance Operator 버그 수정 업데이트

#### 5.2.16.1. 새로운 기능 및 개선 사항

Compliance Operator에서 스캐너 Pod의 시간 초과 구성을 지원합니다. 시간 초과는 `ScanSetting` 오브젝트에 지정됩니다. 제한 시간 내에 검사가 완료되지 않으면 최대 재시도 횟수에 도달할 때까지 검사를 다시 시도합니다. 자세한 내용은 ScanSetting 시간 초과 구성 을 참조하십시오.

#### 5.2.16.2. 버그 수정

이번 업데이트 이전에는 Compliance Operator에서 필요한 변수를 입력으로 수정합니다. 변수 세트가 없는 수정이 클러스터 전체로 적용되고 수정 사항이 올바르게 적용된 경우에도 노드가 중단되었습니다. 이번 업데이트를 통해 Compliance Operator는 수정을 위해 `TailoredProfile` 을 사용하여 변수를 제공해야 하는지 확인합니다. (OCPBUGS-3864)

이번 업데이트 이전에는 `ocp4-kubelet-configure-tls-cipher-suites` 에 대한 지침이 불완전하여 사용자가 쿼리를 수동으로 개선해야 했습니다. 이번 업데이트를 통해 `ocp4-kubelet-configure-tls-cipher-suites` 에 제공된 쿼리에서 실제 결과를 반환하여 감사 단계를 수행합니다. (OCPBUGS-3017)

이번 업데이트 이전에는 kubelet 구성 파일에 시스템 예약된 매개변수가 생성되지 않아 Compliance Operator에서 머신 구성 풀의 일시 중지를 해제하지 못했습니다. 이번 업데이트를 통해 Compliance Operator는 머신 구성 풀 평가 중에 시스템 예약된 매개변수를 생략합니다. (OCPBUGS-4445)

이번 업데이트 이전에는 `ComplianceCheckResult` 오브젝트에 올바른 설명이 없었습니다. 이번 업데이트를 통해 Compliance Operator는 규칙 설명에서 `ComplianceCheckResult` 정보를 소싱합니다. (OCPBUGS-4615)

이번 업데이트 이전에는 머신 구성을 구문 분석할 때 Compliance Operator에서 빈 kubelet 구성 파일을 확인하지 않았습니다. 그 결과 Compliance Operator가 패닉 상태가 되고 충돌했습니다. 이번 업데이트를 통해 Compliance Operator는 kubelet 구성 데이터 구조의 향상된 검사를 구현하고 완전히 렌더링되는 경우에만 계속됩니다. (OCPBUGS-4621)

이번 업데이트 이전에는 Compliance Operator에서 머신 구성 풀 이름과 유예 기간을 기반으로 kubelet 제거에 대한 수정이 생성되어 단일 제거 규칙에 대해 여러 번 수정이 생성되었습니다. 이번 업데이트를 통해 Compliance Operator는 단일 규칙에 대한 모든 수정을 적용합니다. (OCPBUGS-4338)

이번 업데이트 이전에는 기본이 아닌 `MachineConfigPool` 이 `ScanSettingBinding` 을 `Failed` 로 표시한 `TailoredProfile` 을 사용하여 `ScanSettingBinding` 을 생성하려고 할 때 회귀 문제가 발생했습니다. 이번 업데이트를 통해 기능이 복원되고 `TailoredProfile` 을 사용하여 사용자 정의 `ScanSettingBinding` 이 올바르게 수행됩니다. (OCPBUGS-6827)

이번 업데이트 이전에는 일부 kubelet 구성 매개변수에 기본값이 없었습니다. 이번 업데이트를 통해 다음 매개변수에 기본값 (OCPBUGS-6708)이 포함되어 있습니다.

`ocp4-cis-kubelet-enable-streaming-connections`

`ocp4-cis-kubelet-eviction-thresholds-set-hard-imagefs-available`

`ocp4-cis-kubelet-eviction-thresholds-set-hard-imagefs-inodesfree`

`ocp4-cis-kubelet-eviction-thresholds-set-hard-memory-available`

`ocp4-cis-kubelet-eviction-thresholds-set-hard-nodefs-available`

이번 업데이트 이전에는 kubelet을 실행하는 데 필요한 권한으로 인해 `selinux_confinement_of_daemons` 규칙이 kubelet에서 실행되지 않았습니다. 이번 업데이트를 통해 `selinux_confinement_of_daemons` 규칙이 비활성화됩니다. (OCPBUGS-6968)

#### 5.2.17. OpenShift Compliance Operator 0.1.59

OpenShift Compliance Operator 0.1.59에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:8538 - OpenShift Compliance Operator 버그 수정 업데이트

#### 5.2.17.1. 새로운 기능 및 개선 사항

Compliance Operator는 이제 `ppc64le` 아키텍처에서 PCI-DSS(Payment Card Industry Data Security Standard) `ocp4-pci-dss` 및 `ocp4-pci-dss-node` 프로필을 지원합니다.

#### 5.2.17.2. 버그 수정

이전에는 Compliance Operator에서 `ppc64le` 과 같은 다른 아키텍처의 PCI DSS(Payment Card Industry Data Security Standard) `ocp4-pci-dss` 및 `ocp4-pci-dss-node` 프로필을 지원하지 않았습니다. 이제 Compliance Operator에서 `ppc64le` 아키텍처에서 `ocp4-pci-dss` 및 `ocp4-pci-dss-node` 프로필을 지원합니다. (OCPBUGS-3252)

이전 버전에서는 최근 버전 0.1.57로 업데이트한 후SA(`rerunner` 서비스 계정)가 더 이상 CSV(클러스터 서비스 버전)에 속하지 않아 Operator 업그레이드 중에 SA가 제거되었습니다. 이제 CSV는 0.1.59에 `rerunner` SA를 소유하고 있으며 이전 버전에서 업그레이드하면 SA가 누락되지 않습니다. (OCPBUGS-3452)

#### 5.2.18. OpenShift Compliance Operator 0.1.57

OpenShift Compliance Operator 0.1.57에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:6657 - OpenShift Compliance Operator 버그 수정 업데이트

#### 5.2.18.1. 새로운 기능 및 개선 사항

`KubeletConfig` 검사가 `Node` 에서 `Platform` 유형으로 변경되었습니다. `KubeletConfig` 는 `KubeletConfig` 의 기본 구성을 확인합니다. 구성 파일은 모든 노드에서 노드 풀당 단일 위치로 집계됩니다. 기본 구성 값에 대한 `KubeletConfig` 규칙 평가를 참조하십시오.

이제 `ScanSetting` 사용자 정의 리소스를 사용하면 `scanLimits` 특성을 통해 스캐너 Pod의 기본 CPU 및 메모리 제한을 덮어쓸 수 있습니다. 자세한 내용은 Compliance Operator 리소스 제한 증가를 참조하십시오.

`PriorityClass` 오브젝트는 `ScanSetting` 을 통해 설정할 수 있습니다. 이렇게 하면 Compliance Operator에 우선순위가 지정되고 클러스터가 준수하지 않을 가능성을 최소화합니다. 자세한 내용은

`ScanSetting` 검사를 위한 `PriorityClass` 설정을 참조하십시오.

#### 5.2.18.2. 버그 수정

이전에는 Compliance Operator에서 기본 `openshift-compliance` 네임스페이스에 대한 알림을 하드 코딩했습니다. Operator가 기본이 아닌 네임스페이스에 설치된 경우 알림이 예상대로 작동하지 않습니다. 이제 기본이 아닌 `openshift-compliance` 네임스페이스에서 알림이 작동합니다. (BZ#2060726)

이전에는 Compliance Operator에서 kubelet 오브젝트에서 사용하는 기본 구성을 평가할 수 없어 부정확한 결과 및 잘못된 긍정이 발생했습니다. 이 새로운 기능은 kubelet 구성을 평가하고 이제 정확하게 보고합니다. (BZ#2075041)

이전에는 `eventRecordQPS` 값이 기본값보다 높기 때문에 자동 수정을 적용한 후 Compliance Operator에서 `FAIL` 상태에서 `ocp4-kubelet-configure-event-creation` 규칙을 보고했습니다. 이제 `ocp4-kubelet-configure-event-creation` 규칙 수정이 기본값을 설정하고 규칙이 올바르게 적용됩니다. (BZ#2082416)

`ocp4-configure-network-policies` 규칙은 효과적으로 수행하기 위해 수동 개입이 필요합니다. 새로운 설명 지침 및 규칙 업데이트는 Calico CNI를 사용하는 클러스터의 `ocp4-configure-network-policies` 규칙의 적용 가능성을 향상시킵니다. (BZ#2091794)

이전에는 Compliance Operator에서 검사 설정에서 `debug=true` 옵션을 사용할 때 인프라를 검사하는 데 사용되는 Pod를 정리하지 않았습니다. 이로 인해 `ScanSettingBinding` 을 삭제한 후에도 Pod가 클러스터에 남아 있었습니다. 이제 `ScanSettingBinding` 이 삭제될 때 Pod가 항상 삭제됩니다. (BZ#2092913)

이전에는 Compliance Operator에서 더 이상 사용되지 않는 기능에 대한 경고로 인해 이전 버전의 `operator-sdk` 명령을 사용했습니다. 이제 `operator-sdk` 명령의 업데이트된 버전이 포함되어 더 이상 사용되지 않는 기능에 대한 경고가 없습니다. (BZ#2098581)

이전에는 kubelet과 머신 구성 간의 관계를 확인할 수 없는 경우 Compliance Operator에서 수정을 적용하지 못했습니다. 이제 Compliance Operator에서 머신 구성 처리가 개선되어 kubelet 구성이 머신 구성의 서브 세트인지 확인할 수 있습니다. (BZ#2102511)

이전에는 `ocp4-cis-node-master-kubelet-enable-cert-rotation` 규칙이 성공 기준을 올바르게 설명하지 않았습니다. 그 결과 `RotateKubeletClientCertificate` 의 요구 사항은 명확하지 않았습니다. 이제 kubelet 구성 파일에 있는 구성에 관계없이 `ocp4-cis-node-master-kubelet-cert-rotation` 에 대한 규칙이 정확하게 보고됩니다. (BZ#2105153)

이전에는 유휴 스트리밍 시간 초과를 확인하는 규칙에서 기본 값을 고려하지 않아 잘못된 규칙 보고가 발생했습니다. 이제 더 강력한 검사를 통해 기본 구성 값에 따라 결과 정확도가 향상됩니다. (BZ#2105878)

이전에는 Ignition 사양 없이 머신 구성을 구문 분석할 때 Compliance Operator에서 API 리소스를 가져오지 못했습니다. 이로 인해 `api-check-pods` 프로세스가 크래시 루프가 발생했습니다. 이제 Compliance Operator에서 Ignition 사양이 올바르게 없는 Machine Config Pool을 처리합니다. (BZ#2117268)

이전에는 `modprobe` 구성의 값이 일치하지 않아 수정 사항을 적용한 후에도 `modprobe` 구성을 평가하는 규칙이 실패했습니다. 이제 검사 및 수정에서 `modprobe` 구성에 동일한 값이 사용되어 일관된 결과를 보장합니다. (BZ#2117747)

#### 5.2.18.3. deprecations

클러스터의 모든 네임스페이스에 설치 를 지정하거나 `WATCH_NAMESPACES` 환경 변수를 `""` 로 설정하면 더 이상 모든 네임스페이스에 영향을 미치지 않습니다. Compliance Operator 설치 시 지정되지 않은 네임스페이스에 설치된 모든 API 리소스가 더 이상 작동하지 않습니다. API 리소스에는 기본적으로 선택한 네임스페이스 또는 `openshift-compliance` 네임스페이스를 생성해야 할 수 있습니다. 이번 변경으로 Compliance Operator의 메모리 사용량이 향상됩니다.

#### 5.2.19. OpenShift Compliance Operator 0.1.53

OpenShift Compliance Operator 0.1.53에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:5537 - OpenShift Compliance Operator 버그 수정 업데이트

#### 5.2.19.1. 버그 수정

이전에는 `ocp4-kubelet-enable-streaming-connections` 규칙에 잘못된 변수 비교가 포함되어 있어 잘못된 검색 결과가 발생했습니다. 이제 `streamingConnectionIdleTimeout` 을 설정할 때 Compliance Operator에서 정확한 검사 결과를 제공합니다. (BZ#2069891)

이전 버전에서는 `/etc/openvswitch/conf.db` 에 대한 그룹 소유권이 IBM Z® 아키텍처에서 올바르지 않아 `ocp4-cis-node-worker-file-ovs-conf-db` 검사 실패가 발생했습니다. 이제 이 검사에 IBM Z® `아키텍처 시스템에서 AppLICABLE이 표시되지 않습니다`. (BZ#2072597)

이전 버전에서는 배포의 SCC(보안 컨텍스트 제약 조건) 규칙에 대한 불완전한 데이터로 인해 `FAIL` 상태에서 보고된 `ocp4-cis-scc-scc-container-allowed-capabilities` 규칙입니다. 이제 결과는 많은 `것으로`, 사람의 개입이 필요한 다른 검사와 일치합니다. (BZ#2077916)

이전에는 다음 규칙이 API 서버 및 TLS 인증서 및 키에 대한 추가 구성 경로를 고려하지 않아 인증서 및 키가 올바르게 설정된 경우에도 오류가 보고되었습니다.

`ocp4-cis-api-server-kubelet-client-cert`

`ocp4-cis-api-server-kubelet-client-key`

`ocp4-cis-kubelet-configure-tls-cert`

`ocp4-cis-kubelet-configure-tls-key`

이제 규칙에서 정확하게 보고하고 kubelet 구성 파일에 지정된 레거시 파일 경로를 관찰합니다. (BZ#2079813)

이전에는 `content_rule_oauth_or_oauthclient_inactivity_timeout` 규칙이 시간 초과에 대한 규정 준수를 평가할 때 배포에 의해 설정된 구성 가능한 타임아웃을 고려하지 않았습니다. 이로 인해 시간 초과가 유효한 경우에도 규칙이 실패했습니다. 이제 Compliance Operator에서 `var_oauth_inactivity_timeout` 변수를 사용하여 유효한 시간 초과 길이를 설정합니다. (BZ#2081952)

이전에는 Compliance Operator에서 권한 있는 사용을 위해 적절하게 레이블이 지정되지 않은 네임스페이스에서 관리 권한을 사용했기 때문에 Pod 보안 수준 위반에 대한 경고 메시지가 표시되었습니다. 이제 Compliance Operator에 권한을 위반하지 않고 적절한 네임스페이스 라벨과 액세스 권한을 조정할 수 있습니다. (BZ#2088202)

이전 버전에서는 `rhcos4-high-master-sysctl-kernel-yama-ptrace-scope` 및 `rhcos4-sysctl-kernel-core-pattern` 에 대한 자동 수정을 적용하면 수정된 경우에도 해당 규칙이 후속으로 실패했습니다. 이제 규칙이 수정 사항이 적용된 후에도 `PASS` 를 정확하게 보고합니다. (BZ#2094382)

이전에는 메모리 부족 예외로 인해 Compliance Operator가 `CrashLoopBackoff` 상태에서 실패했습니다. 이제 메모리의 대규모 머신 구성 데이터 세트를 처리하고 올바르게 작동하도록 Compliance Operator가 개선되었습니다. (BZ#2094854)

#### 5.2.19.2. 알려진 문제

`"debug":true` 가 `ScanSettingBinding` 오브젝트 내에서 설정된 경우 `ScanSettingBinding` 오브젝트에서 생성한 Pod는 해당 바인딩이 삭제될 때 제거되지 않습니다. 이 문제를 해결하려면 다음 명령을 실행하여 나머지 Pod를 삭제합니다.

```shell-session
$ oc delete pods -l compliance.openshift.io/scan-name=ocp4-cis
```

(BZ#2092913)

#### 5.2.20. OpenShift Compliance Operator 0.1.52

OpenShift Compliance Operator 0.1.52에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:4657 - OpenShift Compliance Operator 버그 수정 업데이트

#### 5.2.20.1. 새로운 기능 및 개선 사항

OpenShift Container Platform 환경에서 FedRAMP High SCAP 프로필을 사용할 수 있습니다. 자세한 내용은 지원되는 규정 준수 프로필을 참조하십시오.

#### 5.2.20.2. 버그 수정

이전에는 `DAC_OVERRIDE` 기능이 삭제되는 보안 환경에서 마운트 권한 문제로 인해 `OpenScap` 컨테이너가 충돌했습니다. 이제 실행 가능한 마운트 권한이 모든 사용자에게 적용됩니다. (BZ#2082151)

이전에는 규정 준수 규칙 `ocp4-configure-network-policies` 를 `MANUAL` 로 구성할 수 있었습니다. 이제 규정 준수 규칙 `ocp4-configure-network-policies` 가 `AUTOMATIC` 로 설정됩니다. (BZ#2072431)

이전에는 Compliance Operator 검사 Pod가 검사 후 제거되지 않았기 때문에 클러스터 자동 스케일러가 축소되지 않았습니다. 이제 디버깅을 위해 명시적으로 저장하지 않는 한 기본적으로 Pod가 각 노드에서 제거됩니다. (BZ#2075029)

이전 버전에서는 `KubeletConfig` 에 Compliance Operator를 적용하면 Machine Config Pools을 너무 빨리 일시 중지 해제하여 노드가 `NotReady` 상태가 되었습니다. 이제 머신 구성 풀이 제대로 일시 중지되지 않고 노드가 올바르게 작동합니다. (BZ#2071854)

이전에는 Machine Config Operator에서 최신 릴리스의 `URL 인코딩` 코드 대신 `base64` 를 사용하여 Compliance Operator 수정에 실패했습니다. 이제 Compliance Operator 검사 인코딩에서 `base64` 및 `url로 인코딩된` Machine Config 코드를 모두 처리하고 수정이 올바르게 적용됩니다. (BZ#2082431)

#### 5.2.20.3. 알려진 문제

`"debug":true` 가 `ScanSettingBinding` 오브젝트 내에서 설정된 경우 `ScanSettingBinding` 오브젝트에서 생성한 Pod는 해당 바인딩이 삭제될 때 제거되지 않습니다. 이 문제를 해결하려면 다음 명령을 실행하여 나머지 Pod를 삭제합니다.

```shell-session
$ oc delete pods -l compliance.openshift.io/scan-name=ocp4-cis
```

(BZ#2092913)

#### 5.2.21. OpenShift Compliance Operator 0.1.49

OpenShift Compliance Operator 0.1.49에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:1148 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.21.1. 새로운 기능 및 개선 사항

이제 Compliance Operator가 다음 아키텍처에서 지원됩니다.

IBM Power®

IBM Z®

IBM® LinuxONE

#### 5.2.21.2. 버그 수정

이전에는 `openshift-compliance` 콘텐츠에 네트워크 유형에 대한 플랫폼별 검사가 포함되지 않았습니다. 그 결과 네트워크 구성에 따라 `not-applicable` 대신 OVN 및 SDN 관련 검사가 `failed` 표시되었습니다. 이제 새로운 규칙에는 네트워킹 규칙에 대한 플랫폼 검사가 포함되어 있어 네트워크별 검사를 보다 정확하게 평가할 수 있습니다. (BZ#1994609)

이전 버전에서는 `ocp4-moderate-routes-protected-by-tls` 규칙에서 연결 보안 SSL/TLS 프로토콜이 있어도 규칙에서 검사에 실패하는 TLS 설정을 잘못 확인했습니다. 이제 검사에서 네트워킹 지침 및 프로필 권장 사항과 일치하는 TLS 설정을 올바르게 평가합니다. (BZ#2002695)

이전 버전에서는 `ocp-cis-configure-network-policies-namespace` 에서 네임스페이스를 요청할 때 pagination을 사용했습니다. 이로 인해 배포가 500개 이상의 네임스페이스 목록을 잘린 때문에 규칙이 실패했습니다. 이제 전체 네임스페이스 목록이 요청되고 구성된 네트워크 정책을 확인하는 규칙이 500개 이상의 네임스페이스가 있는 배포에 적용됩니다. (BZ#2038909)

이전에는 `sshd jinja` 매크로를 사용하는 수정 사항이 특정 sshd 구성에 하드 코딩되었습니다. 결과적으로 해당 구성이 규칙에서 검사한 내용과 일치하지 않아 검사에 실패했습니다. 이제 sshd 구성이 매개 변수화되고 규칙이 성공적으로 적용됩니다. (BZ#2049141)

이전에는 `ocp4-cluster-version-operator-verify-integrity` 에서 항상 Cluter Version Operator (CVO) 기록의 첫 번째 항목을 확인했습니다. 결과적으로 후속 버전의 OpenShift Container Platform을 확인하는 경우 업그레이드가 실패했습니다. 이제 `ocp4-cluster-version-operator-verify-integrity` 의 규정 준수 점검 결과는 확인된 버전을 탐지하고 CVO 기록을 통해 정확합니다. (BZ#2053602)

이전에는 `ocp4-api-server-no-adm-ctrl-plugins-disabled` 규칙에서 빈 승인 컨트롤러 플러그인 목록을 확인하지 않았습니다. 결과적으로 모든 승인 플러그인이 활성화되어 있어도 규칙은 항상 실패합니다. 이제 `ocp4-api-server-no-adm-ctrl-plugins-disabled` 규칙을 보다 강력하게 확인하는 것이 모든 승인 컨트롤러 플러그인과 정확하게 전달됩니다. (BZ#2058631)

이전에는 검사에 Linux 작업자 노드에 대해 실행 중인 플랫폼 검사가 포함되지 않았습니다. 결과적으로 Linux 기반이 아닌 작업자 노드에 대해 검사를 실행하면 검사 루프가 종료되지 않았습니다. 이제 플랫폼 유형 및 라벨에 따라 스캔 일정이 성공적으로 완료됩니다. (BZ#2056911)

#### 5.2.22. OpenShift Compliance Operator 0.1.48

OpenShift Compliance Operator 0.1.48에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:0416 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.22.1. 버그 수정

이전에는 확장된 OVAL(Open Vulnerability and Assessment Language) 정의와 관련된 일부 규칙에는 `None` 이라는 `checkType` 이 있었습니다. 이는 Compliance Operator가 규칙을 구문 분석할 때 확장된 OVAL 정의를 처리하지 않았기 때문입니다. 이번 업데이트를 통해 확장된 OVAL 정의의 콘텐츠를 구문 분석하므로 이러한 규칙에 `Node` 또는 `Platform` 의 `checkType` 이 있습니다. (BZ#2040282)

이전에는 `KubeletConfig` 에 대해 수동으로 생성한 `MachineConfig` 오브젝트로 인해 수정으로 인해 `KubeletConfig` 오브젝트가 생성되지 않아 수정 사항이 `Pending` 상태로 유지되었습니다. 이번 릴리스에서는 `KubeletConfig` 에 대해 수동으로 생성된 `MachineConfig` 오브젝트가 있는지와 관계없이 수정으로 `KubeletConfig` 오브젝트가 생성됩니다. 결과적으로 `KubeletConfig` 수정이 예상대로 작동합니다. (BZ#2040401)

#### 5.2.23. OpenShift Compliance Operator 0.1.47

OpenShift Compliance Operator 0.1.47에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:0014 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.23.1. 새로운 기능 및 개선 사항

Compliance Operator는 이제 PCI DSS(Payment Card Industry Data Security Standard)에 대해 다음 규정 준수 벤치마크를 지원합니다.

ocp4-pci-dss

ocp4-pci-dss-node

FedRAMP 중간 수준의 영향을 미치는 수준에 대한 추가 규칙 및 수정이 OCP4-moderate, OCP4-moderate-node 및 rhcos4-moderate 프로필에 추가됩니다.

KubeletConfig에 대한 수정을 노드 수준 프로필에서 사용할 수 있습니다.

#### 5.2.23.2. 버그 수정

이전 버전에서는 클러스터가 OpenShift Container Platform 4.6 또는 이전 버전을 실행 중인 경우 보통 프로필에 대해 USBGuard 관련 규칙에 대한 수정이 실패했습니다. Compliance Operator에서 생성한 수정은 드롭인 디렉터리를 지원하지 않는 이전 버전의 USBGuard를 기반으로하기 때문입니다. 이제 OpenShift Container Platform 4.6을 실행하는 클러스터에 대해 USBGuard 관련 규칙에 대한 잘못된 수정이 생성되지 않습니다. 클러스터가 OpenShift Container Platform 4.6을 사용하는 경우 USBGuard 관련 규칙에 대한 수정을 수동으로 생성해야 합니다.

또한 최소 버전 요구 사항을 충족하는 규칙에 대해서만 수정이 생성됩니다. (BZ#1965511)

이전 버전에서는 수정을 렌더링할 때 규정 준수 Operator에서 너무 엄격한 정규식을 사용하여 수정 사항이 제대로 작성되었는지 확인했습니다. 결과적으로 `sshd_config` 를 렌더링하는 것과 같은 일부 수정이 정규식 검사를 통과하지 않아 생성되지 않았습니다. 정규 표현식은 불필요하고 제거되는 것으로 확인되었습니다. 이제 수정이 올바르게 렌더링됩니다. (BZ#2033009)

#### 5.2.24. OpenShift Compliance Operator 0.1.44

OpenShift Compliance Operator 0.1.44에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2021:4530 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.24.1. 새로운 기능 및 개선 사항

이번 릴리스에서는 `ComplianceScan`, `ComplianceSuite` 및 `ScanSetting` CR에 `strictNodeScan` 옵션이 추가되었습니다. 이 옵션은 노드에서 검색을 예약할 수 없는 경우 오류가 발생한 이전 동작과 일치하는 `true` 로 기본 설정됩니다. 옵션을 `false` 로 설정하면 Compliance Operator가 스케줄링 검사에 대해 더 관대해질 수 있습니다. 임시 노드가 있는 환경에서는 `strictNodeScan` 값을 false로 설정할 수 있으므로 클러스터의 일부 노드를 예약할 수 없는 경우에도 규정 준수 검사를 진행할 수 있습니다.

이제 `ScanSetting` 오브젝트의 `nodeSelector` 및 `tolerations` 속성을 구성하여 결과 서버 워크로드를 예약하는 데 사용되는 노드를 사용자 지정할 수 있습니다. 이러한 속성은 PV 스토리지 볼륨을 마운트하고 원시 자산 보고 형식(ARF) 결과를 저장하는 데 사용되는 Pod인 `ResultServer` Pod를 배치하는 데 사용됩니다. 이전에는 `nodeSelector` 및 `tolerations` 매개변수가 컨트롤 플레인 노드 중 하나를 선택하고 `node-role.kubernetes.io/master taint` 를 허용하는 것으로 기본 설정되었습니다. 이는 컨트롤 플레인 노드가 PV를 마운트할 수 없는 환경에서는 작동하지 않았습니다. 이 기능을 사용하면 해당 환경에서 노드를 선택하고 다른 테인트를 허용할 수 있습니다.

Compliance Operator에서 `KubeletConfig` 오브젝트를 수정할 수 있습니다.

이제 오류 메시지가 포함된 주석이 추가되어 콘텐츠 개발자가 클러스터에 없는 오브젝트와 가져올 수 없는 오브젝트를 구분할 수 있습니다.

이제 rule 오브젝트에 `checkType` 및 `description` 이라는 두 개의 새 속성이 포함됩니다. 이러한 속성을 사용하면 규칙과 노드 점검 또는 플랫폼 점검이 적용되는지 확인하고 규칙의 기능을 검토할 수도 있습니다.

이번 개선된 기능을 통해 기존 프로필을 확장하여 맞춤형 프로필을 생성해야 합니다. 즉 `TailoredProfile` CRD의 `extends` 필드가 더 이상 필수가 아닙니다. 이제 규칙 오브젝트 목록을 선택하여 맞춤형 프로필을 생성할 수 있습니다. `compliance.openshift.io/product-type:` 주석을 설정하거나 `TailoredProfile` CR에 `-node` 접미사를 설정하여 프로필이 노드 또는 플랫폼에 적용되는지 여부를 선택해야 합니다.

이번 릴리스에서 Compliance Operator는 테인트와 관계없이 모든 노드에서 검사를 예약할 수 있습니다. 이전에는 검사 Pod에서 `node-role.kubernetes.io/master taint` 만 허용했습니다. 즉, 테인트가 없는 노드에서나 `node-role.kubernetes.io/master` 테인트가 있는 노드에서만 실행되었습니다. 노드에 사용자 정의 테인트를 사용하는 배포에서는 해당 노드에 검사가 예약되지 않았습니다. 이제 검사 Pod에서 모든 노드 테인트를 허용합니다.

이번 릴리스에서 Compliance Operator는 다음과 같은 NERC(North American Electric Reliability Corporation) 보안 프로필을 지원합니다.

ocp4-nerc-cip

ocp4-nerc-cip-node

rhcos4-nerc-cip

이번 릴리스에서 Compliance Operator는 Red Hat OpenShift - 노드 수준, ocp4-moderate-node, 보안 프로필에 대해 NIST 800-53 Moderate-Impact Baseline을 지원합니다.

#### 5.2.24.2. 템플릿 및 변수 사용

이번 릴리스에서는 해결 템플릿에서 다중 값 변수를 허용합니다.

이번 업데이트를 통해 Compliance Operator는 규정 준수 프로필에 설정된 변수를 기반으로 수정을 변경할 수 있습니다. 이는 시간 제한, NTP 서버 호스트 이름 또는 유사한 배포별 값을 포함하는 수정에 유용합니다. 또한 `ComplianceCheckResult` 오브젝트에서 검사에서 사용한 변수를 나열하는 `compliance.openshift.io/check-has-value` 레이블을 사용합니다.

#### 5.2.24.3. 버그 수정

이전에는 검사를 수행하는 동안 Pod의 스캐너 컨테이너 중 하나에서 예기치 않은 종료가 발생했습니다. 이번 릴리스에서 Compliance Operator는 최신 OpenSCAP 버전 1.3.5를 사용하여 충돌을 방지합니다.

이전 버전에서는 `autoReplyRemediations` 를 사용하여 수정을 적용하면 클러스터 노드 업데이트가 트리거되었습니다. 일부 수정에 필요한 입력 변수가 모두 포함되지 않은 경우 이로 인해 중단되었습니다. 이제 수정에 필요한 입력 변수가 하나 이상 누락된 경우 `NeedsReview` 상태가 할당됩니다. 하나 이상의 수정이 `needsReview` 상태에 있는 경우 머신 구성 풀은 일시 중지된 상태로 남아 있으며 모든 필수 변수가 설정될 때까지 수정이 적용되지 않습니다. 이렇게 하면 노드 중단을 최소화할 수 있습니다.

Prometheus 지표에 사용되는 RBAC 역할 및 역할 바인딩이 'ClusterRole' 및 'ClusterRoleBinding'으로 변경되어 사용자 지정 없이 모니터링이 작동하는지 확인합니다.

이전에는 프로필을 구문 분석하는 중에 오류가 발생하면 규칙 또는 변수 오브젝트가 프로필에서 제거되고 삭제되었습니다. 이제 구문 분석 중에 오류가 발생하면 `profileparser` 는 구문 분석이 완료될 때까지 오브젝트가 삭제되지 않도록 임시 주석으로 오브젝트에 주석을 추가합니다. (BZ#1988259)

이전에는 맞춤형 프로필에서 제목 또는 설명이 누락된 경우 오류가 발생했습니다. XCCDF 표준에는 맞춤형 프로필에 대한 제목과 설명이 필요하므로 이제 `TailoredProfile` CR에 제목 및 설명을 설정해야 합니다.

이전에는 맞춤형 프로필을 사용할 때 특정 선택 세트만 사용하여 `TailoredProfile` 변수 값을 설정할 수 있었습니다. 이제 이 제한이 제거되고 `TailoredProfile` 변수를 임의의 값으로 설정할 수 있습니다.

#### 5.2.25. Compliance Operator 0.1.39의 릴리스 정보

OpenShift Compliance Operator 0.1.39에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2021:3214 - OpenShift Compliance Operator 버그 수정 및 개선 사항 업데이트

#### 5.2.25.1. 새로운 기능 및 개선 사항

이전에는 Compliance Operator에서 PCI DSS(Payment Card Industry Data Security Standard) 참조를 구문 분석할 수 없었습니다. 이제 Operator에서 PCI DSS 프로필과 함께 제공되는 규정 준수 콘텐츠를 구문 분석할 수 있습니다.

이전에는 Compliance Operator에서 보통 프로필에서 AU-5 제어 규칙을 실행할 수 없었습니다. 이제 Prometheusrules.monitoring.coreos.com 오브젝트를 읽고 보통 프로필에서 AU-5 제어를 포함하는 규칙을 실행할 수 있도록 Operator에 권한이 추가됩니다.

#### 5.2.26. 추가 리소스

Compliance Operator 이해

#### 5.3.1. Compliance Operator 라이프사이클

Compliance Operator는 "Rolling Stream" Operator입니다. 즉, OpenShift Container Platform 릴리스의 비동기식으로 업데이트를 사용할 수 있습니다. 자세한 내용은 Red Hat Customer Portal의 OpenShift Operator 라이프 사이클 을 참조하십시오.

#### 5.3.2. 지원 요청

이 문서에 설명된 절차 또는 일반적으로 OpenShift Container Platform에 문제가 발생하는 경우 Red Hat 고객 포털 에 액세스하십시오.

고객 포털에서 다음을 수행할 수 있습니다.

Red Hat 제품과 관련된 기사 및 솔루션에 대한 Red Hat 지식베이스를 검색하거나 살펴볼 수 있습니다.

Red Hat 지원에 대한 지원 케이스 제출할 수 있습니다.

다른 제품 설명서에 액세스 가능합니다.

클러스터 문제를 식별하기 위해 OpenShift Cluster Manager 에서 Red Hat Lightspeed를 사용할 수 있습니다. Red Hat Lightspeed는 문제에 대한 세부 정보와 가능한 경우 문제 해결 방법에 대한 정보를 제공합니다.

이 문서를 개선하기 위한 제안이 있거나 오류를 발견한 경우 가장 관련 문서 구성 요소에 대해 Jira 문제를 제출합니다. 섹션 이름 및 OpenShift Container Platform 버전과 같은 구체적인 정보를 제공합니다.

#### 5.3.3. Compliance Operator에 must-gather 툴 사용

Compliance Operator v1.6.0부터 Compliance Operator 이미지로 `must-gather` 명령을 실행하여 Compliance Operator 리소스에 대한 데이터를 수집할 수 있습니다.

참고

Operator 구성 및 로그에 대한 추가 세부 정보를 제공하므로 지원 케이스를 열거나 버그 보고서를 작성할 때 `must-gather` 툴을 사용하는 것이 좋습니다.

프로세스

다음 명령을 실행하여 Compliance Operator에 대한 데이터를 수집합니다.

```shell-session
$ oc adm must-gather --image=$(oc get csv compliance-operator.v1.6.0 -o=jsonpath='{.spec.relatedImages[?(@.name=="must-gather")].image}')
```

#### 5.3.4. 추가 리소스

must-gather 툴 정보

제품 규정 준수

#### 5.4.1. Compliance Operator 이해

OpenShift Container Platform 관리자는 Compliance Operator를 통해 클러스터의 필수 규정 준수 상태를 설명하고 격차에 대한 개요와 문제를 해결하는 방법을 제공할 수 있습니다. Compliance Operator는 OpenShift Container Platform의 Kubernetes API 리소스와 클러스터를 실행하는 노드 모두의 규정 준수를 평가합니다. Compliance Operator는 NIST 인증 툴인 OpenSCAP을 사용하여 콘텐츠에서 제공하는 보안 정책을 검사하고 시행합니다.

중요

Compliance Operator는 RHCOS(Red Hat Enterprise Linux CoreOS) 배포에서만 사용할 수 있습니다.

#### 5.4.1.1. Compliance Operator 프로필

Compliance Operator 설치의 일부로 다양한 프로필을 사용할 수 있습니다. 아래 명령을 사용하여 사용 가능한 프로필, 프로필 세부 정보 및 특정 규칙을 볼 수 있습니다.

```shell
oc get
```

```shell-session
$ oc get profile.compliance -n openshift-compliance
```

```shell-session
NAME                       AGE     VERSION
ocp4-cis                   3h49m   1.5.0
ocp4-cis-1-4               3h49m   1.4.0
ocp4-cis-1-5               3h49m   1.5.0
ocp4-cis-node              3h49m   1.5.0
ocp4-cis-node-1-4          3h49m   1.4.0
ocp4-cis-node-1-5          3h49m   1.5.0
ocp4-e8                    3h49m
ocp4-high                  3h49m   Revision 4
ocp4-high-node             3h49m   Revision 4
ocp4-high-node-rev-4       3h49m   Revision 4
ocp4-high-rev-4            3h49m   Revision 4
ocp4-moderate              3h49m   Revision 4
ocp4-moderate-node         3h49m   Revision 4
ocp4-moderate-node-rev-4   3h49m   Revision 4
ocp4-moderate-rev-4        3h49m   Revision 4
ocp4-nerc-cip              3h49m
ocp4-nerc-cip-node         3h49m
ocp4-pci-dss               3h49m   3.2.1
ocp4-pci-dss-3-2           3h49m   3.2.1
ocp4-pci-dss-4-0           3h49m   4.0.0
ocp4-pci-dss-node          3h49m   3.2.1
ocp4-pci-dss-node-3-2      3h49m   3.2.1
ocp4-pci-dss-node-4-0      3h49m   4.0.0
ocp4-stig                  3h49m   V2R1
ocp4-stig-node             3h49m   V2R1
ocp4-stig-node-v1r1        3h49m   V1R1
ocp4-stig-node-v2r1        3h49m   V2R1
ocp4-stig-v1r1             3h49m   V1R1
ocp4-stig-v2r1             3h49m   V2R1
rhcos4-e8                  3h49m
rhcos4-high                3h49m   Revision 4
rhcos4-high-rev-4          3h49m   Revision 4
rhcos4-moderate            3h49m   Revision 4
rhcos4-moderate-rev-4      3h49m   Revision 4
rhcos4-nerc-cip            3h49m
rhcos4-stig                3h49m   V2R1
rhcos4-stig-v1r1           3h49m   V1R1
rhcos4-stig-v2r1           3h49m   V2R1
```

이러한 프로필은 다양한 규정 준수 벤치마크를 나타냅니다. 각 프로필에는 적용되는 제품 이름이 프로필 이름에 접두사로 추가됩니다. `ocp4-e8` 은 Essential 8 벤치마크를 OpenShift Container Platform 제품에 적용하고 `rhcos4-e8` 은 Essential 8 벤치마크를 RHCOS(Red Hat Enterprise Linux CoreOS) 제품에 적용합니다.

다음 명령을 실행하여 `rhcos4-e8` 프로필의 세부 정보를 확인합니다.

```shell-session
$ oc get -n openshift-compliance -oyaml profiles.compliance rhcos4-e8
```

```yaml
apiVersion: compliance.openshift.io/v1alpha1
description: 'This profile contains configuration checks for Red Hat Enterprise Linux
  CoreOS that align to the Australian Cyber Security Centre (ACSC) Essential Eight.
  A copy of the Essential Eight in Linux Environments guide can be found at the ACSC
  website: https://www.cyber.gov.au/acsc/view-all-content/publications/hardening-linux-workstations-and-servers'
id: xccdf_org.ssgproject.content_profile_e8
kind: Profile
metadata:
  annotations:
    compliance.openshift.io/image-digest: pb-rhcos4hrdkm
    compliance.openshift.io/product: redhat_enterprise_linux_coreos_4
    compliance.openshift.io/product-type: Node
  creationTimestamp: "2022-10-19T12:06:49Z"
  generation: 1
  labels:
    compliance.openshift.io/profile-bundle: rhcos4
  name: rhcos4-e8
  namespace: openshift-compliance
  ownerReferences:
  - apiVersion: compliance.openshift.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: ProfileBundle
    name: rhcos4
    uid: 22350850-af4a-4f5c-9a42-5e7b68b82d7d
  resourceVersion: "43699"
  uid: 86353f70-28f7-40b4-bf0e-6289ec33675b
rules:
- rhcos4-accounts-no-uid-except-zero
- rhcos4-audit-rules-dac-modification-chmod
- rhcos4-audit-rules-dac-modification-chown
- rhcos4-audit-rules-execution-chcon
- rhcos4-audit-rules-execution-restorecon
- rhcos4-audit-rules-execution-semanage
- rhcos4-audit-rules-execution-setfiles
- rhcos4-audit-rules-execution-setsebool
- rhcos4-audit-rules-execution-seunshare
- rhcos4-audit-rules-kernel-module-loading-delete
- rhcos4-audit-rules-kernel-module-loading-finit
- rhcos4-audit-rules-kernel-module-loading-init
- rhcos4-audit-rules-login-events
- rhcos4-audit-rules-login-events-faillock
- rhcos4-audit-rules-login-events-lastlog
- rhcos4-audit-rules-login-events-tallylog
- rhcos4-audit-rules-networkconfig-modification
- rhcos4-audit-rules-sysadmin-actions
- rhcos4-audit-rules-time-adjtimex
- rhcos4-audit-rules-time-clock-settime
- rhcos4-audit-rules-time-settimeofday
- rhcos4-audit-rules-time-stime
- rhcos4-audit-rules-time-watch-localtime
- rhcos4-audit-rules-usergroup-modification
- rhcos4-auditd-data-retention-flush
- rhcos4-auditd-freq
- rhcos4-auditd-local-events
- rhcos4-auditd-log-format
- rhcos4-auditd-name-format
- rhcos4-auditd-write-logs
- rhcos4-configure-crypto-policy
- rhcos4-configure-ssh-crypto-policy
- rhcos4-no-empty-passwords
- rhcos4-selinux-policytype
- rhcos4-selinux-state
- rhcos4-service-auditd-enabled
- rhcos4-sshd-disable-empty-passwords
- rhcos4-sshd-disable-gssapi-auth
- rhcos4-sshd-disable-rhosts
- rhcos4-sshd-disable-root-login
- rhcos4-sshd-disable-user-known-hosts
- rhcos4-sshd-do-not-permit-user-env
- rhcos4-sshd-enable-strictmodes
- rhcos4-sshd-print-last-log
- rhcos4-sshd-set-loglevel-info
- rhcos4-sysctl-kernel-dmesg-restrict
- rhcos4-sysctl-kernel-kptr-restrict
- rhcos4-sysctl-kernel-randomize-va-space
- rhcos4-sysctl-kernel-unprivileged-bpf-disabled
- rhcos4-sysctl-kernel-yama-ptrace-scope
- rhcos4-sysctl-net-core-bpf-jit-harden
title: Australian Cyber Security Centre (ACSC) Essential Eight
```

다음 명령을 실행하여 `rhcos4-audit-rules-login-events` 규칙의 세부 정보를 확인합니다.

```shell-session
$ oc get -n openshift-compliance -oyaml rules rhcos4-audit-rules-login-events
```

```yaml
apiVersion: compliance.openshift.io/v1alpha1
checkType: Node
description: |-
  The audit system already collects login information for all users and root. If the auditd daemon is configured to use the augenrules program to read audit rules during daemon startup (the default), add the following lines to a file with suffix.rules in the directory /etc/audit/rules.d in order to watch for attempted manual edits of files involved in storing logon events:

  -w /var/log/tallylog -p wa -k logins
  -w /var/run/faillock -p wa -k logins
  -w /var/log/lastlog -p wa -k logins

  If the auditd daemon is configured to use the auditctl utility to read audit rules during daemon startup, add the following lines to /etc/audit/audit.rules file in order to watch for unattempted manual edits of files involved in storing logon events:

  -w /var/log/tallylog -p wa -k logins
  -w /var/run/faillock -p wa -k logins
  -w /var/log/lastlog -p wa -k logins
id: xccdf_org.ssgproject.content_rule_audit_rules_login_events
kind: Rule
metadata:
  annotations:
    compliance.openshift.io/image-digest: pb-rhcos4hrdkm
    compliance.openshift.io/rule: audit-rules-login-events
    control.compliance.openshift.io/NIST-800-53: AU-2(d);AU-12(c);AC-6(9);CM-6(a)
    control.compliance.openshift.io/PCI-DSS: Req-10.2.3
    policies.open-cluster-management.io/controls: AU-2(d),AU-12(c),AC-6(9),CM-6(a),Req-10.2.3
    policies.open-cluster-management.io/standards: NIST-800-53,PCI-DSS
  creationTimestamp: "2022-10-19T12:07:08Z"
  generation: 1
  labels:
    compliance.openshift.io/profile-bundle: rhcos4
  name: rhcos4-audit-rules-login-events
  namespace: openshift-compliance
  ownerReferences:
  - apiVersion: compliance.openshift.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: ProfileBundle
    name: rhcos4
    uid: 22350850-af4a-4f5c-9a42-5e7b68b82d7d
  resourceVersion: "44819"
  uid: 75872f1f-3c93-40ca-a69d-44e5438824a4
rationale: Manual editing of these files may indicate nefarious activity, such as
  an attacker attempting to remove evidence of an intrusion.
severity: medium
title: Record Attempts to Alter Logon and Logout Events
warning: Manual editing of these files may indicate nefarious activity, such as an
  attacker attempting to remove evidence of an intrusion.
```

#### 5.4.1.1.1. Compliance Operator 프로필 유형

Compliance Operator 규칙은 프로필로 구성됩니다. 프로필은 OpenShift Container Platform의 플랫폼 또는 노드를 대상으로 지정할 수 있으며 일부 벤치마크에는 `rhcos4` 노드 프로필이 포함됩니다.

플랫폼

플랫폼 프로필은 OpenShift Container Platform 클러스터 구성 요소를 평가합니다. 예를 들어 플랫폼 수준 규칙은 APIServer 구성이 강력한 암호화 Ccyphers를 사용하는지 여부를 확인할 수 있습니다.

노드

노드 프로필은 각 호스트의 OpenShift 또는 RHCOS 구성을 평가합니다. 두 개의 노드 프로필 `ocp4` 노드 프로필 및 `rhcos4` 노드 프로필을 사용할 수 있습니다. `ocp4` 노드 프로필은 각 호스트의 OpenShift 구성을 평가합니다. 예를 들어 `kubeconfig` 파일에 규정 준수 표준을 충족할 수 있는 올바른 권한이 있는지 확인할 수 있습니다. `rhcos4` 노드 프로필은 각 호스트의 RHCOS(Red Hat Enterprise Linux CoreOS) 구성을 평가합니다. 예를 들어 SSHD 서비스가 암호 로그인을 비활성화하도록 구성되어 있는지 확인할 수 있습니다.

중요

PCI-DSS와 같은 Node 및 Platform 프로필이 있는 벤치마크의 경우 OpenShift Container Platform 환경에서 두 프로필을 모두 실행해야 합니다.

`ocp4` Platform, `ocp4` Node 및 `rhcos4` Node 프로필이 있는 벤치마크의 경우 OpenShift Container Platform 환경에서 세 개의 프로필을 모두 실행해야 합니다.

참고

노드가 많은 클러스터에서 `ocp4` Node 및 `rhcos4` 노드 검사를 완료하는 데 시간이 오래 걸릴 수 있습니다.

#### 5.4.2. 사용자 정의 리소스 정의 이해

OpenShift Container Platform의 Compliance Operator는 규정 준수 검사를 수행할 수 있도록 여러 CRD(Custom Resource Definitions)를 제공합니다. 규정 준수 검사를 실행하기 위해 ComplianceAsCode 커뮤니티 프로젝트에서 파생되는 사전 정의된 보안 정책을 활용합니다. Compliance Operator는 이러한 보안 정책을 CRD로 변환하여 규정 준수 검사를 실행하고 발견된 문제에 대한 수정을 받을 수 있습니다.

#### 5.4.2.1. CRD 워크플로

CRD는 다음 워크플로우를 제공하여 규정 준수 검사를 완료합니다.

규정 준수 검사 요구 사항 정의

규정 준수 검사 설정 구성

규정 준수 검사 설정을 사용하여 규정 준수 요구 사항 처리

규정 준수 검사 모니터링

컴플라이언스 검사 결과 확인

#### 5.4.2.2. 규정 준수 검사 요구 사항 정의

기본적으로 Compliance Operator CRD에는 `ProfileBundle` 및 `Profile` 오브젝트가 포함되어 있으며 규정 준수 검사 요구 사항에 대한 규칙을 정의하고 설정할 수 있습니다. `TailoredProfile` 오브젝트를 사용하여 기본 프로필을 사용자 지정할 수도 있습니다.

#### 5.4.2.2.1. ProfileBundle 오브젝트

Compliance Operator를 설치하면 즉시 실행 가능한 `ProfileBundle` 오브젝트가 포함됩니다. Compliance Operator는 `ProfileBundle` 오브젝트를 구문 분석하고 번들의 각 프로필에 대해 `Profile` 오브젝트를 생성합니다. 또한 `Profile` 오브젝트에서 사용하는 `Rule` 및 `Variable` 오브젝트를 구문 분석합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ProfileBundle
  name: <profile bundle name>
  namespace: openshift-compliance
status:
  dataStreamStatus: VALID
```

1. Compliance Operator에서 콘텐츠 파일을 구문 분석할 수 있는지 여부를 나타냅니다.

참고

`contentFile` 이 실패하면 발생한 오류에 대한 세부 정보를 제공하는 `errorMessage` 속성이 표시됩니다.

문제 해결

유효하지 않은 이미지의 알려진 콘텐츠 이미지로 롤백하면 `ProfileBundle` 오브젝트가 응답을 중지하고 `PENDING` 상태를 표시합니다. 이 문제를 해결하려면 이전 이미지와 다른 이미지로 이동할 수 있습니다. 또는 `ProfileBundle` 오브젝트를 삭제하고 다시 생성하여 작동 상태로 돌아갈 수 있습니다.

#### 5.4.2.2.2. Profile 오브젝트

`Profile` 오브젝트는 특정 규정 준수 표준에 대해 평가할 수 있는 규칙과 변수를 정의합니다. XCCDF 식별자 및 프로파일 검사와 같이 OpenSCAP 프로필에 대한 세부 정보를 구문 분석했습니다(예: `노드` 또는 `플랫폼` 유형 확인). `Profile` 오브젝트를 직접 사용하거나 `Tailor Profile` 오브젝트를 사용하여 추가로 사용자 지정할 수 있습니다.

참고

`Profile` 오브젝트는 단일 `ProfileBundle` 오브젝트에서 파생되므로 수동으로 생성하거나 수정할 수 없습니다. 일반적으로 단일 `ProfileBundle` 오브젝트에는 여러 `Profile` 오브젝트를 포함할 수 있습니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
description: <description of the profile>
id: xccdf_org.ssgproject.content_profile_moderate
kind: Profile
metadata:
  annotations:
    compliance.openshift.io/product: <product name>
    compliance.openshift.io/product-type: Node
  creationTimestamp: "YYYY-MM-DDTMM:HH:SSZ"
  generation: 1
  labels:
    compliance.openshift.io/profile-bundle: <profile bundle name>
  name: rhcos4-moderate
  namespace: openshift-compliance
  ownerReferences:
  - apiVersion: compliance.openshift.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: ProfileBundle
    name: <profile bundle name>
    uid: <uid string>
  resourceVersion: "<version number>"
  selfLink: /apis/compliance.openshift.io/v1alpha1/namespaces/openshift-compliance/profiles/rhcos4-moderate
  uid: <uid string>
rules:
- rhcos4-account-disable-post-pw-expiration
- rhcos4-accounts-no-uid-except-zero
- rhcos4-audit-rules-dac-modification-chmod
- rhcos4-audit-rules-dac-modification-chown
title: <title of the profile>
```

1. 프로필의 XCCDF 이름을 지정합니다. `ComplianceScan` 오브젝트를 검사의 profile 속성 값으로 정의할 때 이 식별자를 사용합니다.

2. `노드 또는 플랫폼을`

`지정합니다`. 노드 프로필은 클러스터 노드 및 플랫폼 프로필을 스캔하여 Kubernetes 플랫폼을 검사합니다.

3. 프로필의 규칙 목록을 지정합니다. 각 규칙은 단일 점검에 해당합니다.

#### 5.4.2.2.3. 규칙 오브젝트

프로필을 형성하는 `Rule` 오브젝트도 오브젝트로 노출됩니다. `Rule` 오브젝트를 사용하여 규정 준수 확인 요구 사항을 정의하고 수정 가능한 방법을 지정합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
    checkType: Platform
    description: <description of the rule>
    id: xccdf_org.ssgproject.content_rule_configure_network_policies_namespaces
    instructions: <manual instructions for the scan>
    kind: Rule
    metadata:
      annotations:
        compliance.openshift.io/rule: configure-network-policies-namespaces
        control.compliance.openshift.io/CIS-OCP: 5.3.2
        control.compliance.openshift.io/NERC-CIP: CIP-003-3 R4;CIP-003-3 R4.2;CIP-003-3
          R5;CIP-003-3 R6;CIP-004-3 R2.2.4;CIP-004-3 R3;CIP-007-3 R2;CIP-007-3 R2.1;CIP-007-3
          R2.2;CIP-007-3 R2.3;CIP-007-3 R5.1;CIP-007-3 R6.1
        control.compliance.openshift.io/NIST-800-53: AC-4;AC-4(21);CA-3(5);CM-6;CM-6(1);CM-7;CM-7(1);SC-7;SC-7(3);SC-7(5);SC-7(8);SC-7(12);SC-7(13);SC-7(18)
      labels:
        compliance.openshift.io/profile-bundle: ocp4
      name: ocp4-configure-network-policies-namespaces
      namespace: openshift-compliance
    rationale: <description of why this rule is checked>
    severity: high
    title: <summary of the rule>
```

1. 이 규칙이 실행되는 검사 유형을 지정합니다. `노드` 프로필은 클러스터 노드 및 `플랫폼` 프로필을 스캔하여 Kubernetes 플랫폼을 검사합니다. 빈 값은 자동 검사가 없음을 나타냅니다.

2. datastream에서 직접 구문 분석되는 규칙의 XCCDF 이름을 지정합니다.

3. 실패하는 경우 규칙의 심각도를 지정합니다.

참고

`Rule` 오브젝트는 연결된 `ProfileBundle` 오브젝트를 쉽게 식별할 수 있는 적절한 레이블을 가져옵니다. `ProfileBundle` 은 이 오브젝트 `의 OwnerReference` 에도 지정됩니다.

#### 5.4.2.2.4. TailoredProfile 오브젝트

`TailoredProfile` 오브젝트를 사용하여 조직 요구 사항에 따라 기본 `Profile` 오브젝트를 수정합니다. 규칙을 활성화하거나 비활성화하고 변수 값을 설정하며 사용자 지정에 대한 정당성을 제공할 수 있습니다. 검증 후 `TailoredProfile` 오브젝트는 `ComplianceScan` 오브젝트에서 참조할 수 있는 `ConfigMap` 을 생성합니다.

작은 정보

`ScanSettingBinding` 오브젝트에서 `TailoredProfile` 오브젝트를 참조할 수 있습니다. ScanSettingBinding에 대한 자세한 내용은 `ScanSettingBinding` 오브젝트를 참조하십시오.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: TailoredProfile
metadata:
  name: rhcos4-with-usb
spec:
  extends: rhcos4-moderate
  title: <title of the tailored profile>
  disableRules:
    - name: <name of a rule object to be disabled>
      rationale: <description of why this rule is checked>
status:
  id: xccdf_compliance.openshift.io_profile_rhcos4-with-usb
  outputRef:
    name: rhcos4-with-usb-tp
    namespace: openshift-compliance
  state: READY
```

1. 이는 선택 사항입니다. `TailoredProfile` 이 빌드된 `Profile` 오브젝트의 이름입니다. 값을 설정하지 않으면 `enableRules` 목록에서 새 프로필이 생성됩니다.

2. 맞춤형 프로필의 XCCDF 이름을 지정합니다.

3. `ComplianceScan` 의 `tailoringConfigMap.name` 속성 값으로 사용할 수 있는 `ConfigMap` 이름을 지정합니다.

4. `READY`, `PENDING` 및 `FAILURE` 와 같은 오브젝트의 상태를 표시합니다. 오브젝트 상태가 `ERROR` 인 경우 `status.errorMessage` 속성은 실패 이유를 제공합니다.

`TailoredProfile` 오브젝트를 사용하면 `TailoredProfile` 구문을 사용하여 새 `Profile` 오브젝트를 생성할 수 있습니다. 새 `프로필` 을 생성하려면 다음 구성 매개변수를 설정합니다.

적절한 제목

`확장` 값은 비어 있어야 합니다.

`TailoredProfile` 오브젝트에서 유형 주석을 스캔합니다.

```yaml
compliance.openshift.io/product-type: Platform/Node
```

참고

`product-type` 주석을 설정하지 않은 경우 Compliance Operator는 기본적으로 `Platform` 검사 유형으로 설정됩니다. `TailoredProfile` 오브젝트의 이름에 `-node` 접미사를 추가하면 `노드` 검사 유형이 생성됩니다.

#### 5.4.2.3. 규정 준수 검사 설정 구성

규정 준수 검사의 요구 사항을 정의한 후 검사 유형, 검사 발생, 검사 위치를 지정하여 구성할 수 있습니다. 이렇게 하려면 Compliance Operator에서 `ScanSetting` 오브젝트를 제공합니다.

#### 5.4.2.3.1. ScanSetting 오브젝트

`ScanSetting` 오브젝트를 사용하여 작업 정책을 정의하고 재사용하여 스캔을 실행합니다. 기본적으로 Compliance Operator는 다음 `ScanSetting` 오브젝트를 생성합니다.

Default - PV(영구 볼륨)를 사용하여 마스터 노드와 작업자 노드 모두에서 매일 검사를 실행하고 마지막 세 가지 결과를 유지합니다. 수정은 자동으로 적용되거나 업데이트되지 않습니다.

default-auto-apply - PV(영구 볼륨)를 사용하여 컨트롤 플레인 및 작업자 노드에서 매일 1AM에서 검사를 실행하고 마지막 세 가지 결과를 유지합니다. `autoApplyRemediations` 및 `autoUpdateRemediations` 가 모두 true로 설정됩니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
autoApplyRemediations: true
autoUpdateRemediations: true
kind: ScanSetting
maxRetryOnTimeout: 3
metadata:
  creationTimestamp: "2022-10-18T20:21:00Z"
  generation: 1
  name: default-auto-apply
  namespace: openshift-compliance
  resourceVersion: "38840"
  uid: 8cb0967d-05e0-4d7a-ac1c-08a7f7e89e84
rawResultStorage:
  nodeSelector:
    node-role.kubernetes.io/master: ""
  pvAccessModes:
  - ReadWriteOnce
  rotation: 3
  size: 1Gi
  tolerations:
  - effect: NoSchedule
    key: node-role.kubernetes.io/master
    operator: Exists
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  - effect: NoSchedule
    key: node.kubernetes.io/memory-pressure
    operator: Exists
roles:
- master
- worker
scanTolerations:
- operator: Exists
schedule: 0 1 * * *
showNotApplicable: false
strictNodeScan: true
timeout: 30m
```

1. 자동 수정을 활성화하려면 `true` 로 설정합니다. 자동 수정을 비활성화하려면 `false` 로 설정합니다.

2. 콘텐츠 업데이트에 대한 자동 수정을 활성화하려면 `true` 로 설정합니다. 콘텐츠 업데이트에 대한 자동 수정을 비활성화하려면 `false` 로 설정합니다.

3. 원시 결과 형식으로 저장된 검사 수를 지정합니다. 기본값은 `3` 입니다. 이전 결과가 순환되면 관리자는 교체를 수행하기 전에 결과를 다른 위치에 저장해야 합니다.

4. 원시 결과를 저장하기 위해 검사에 생성해야 하는 스토리지 크기를 지정합니다. 기본값은 `1Gi` 입니다.

6. cron 형식으로 검사를 실행하는 빈도를 지정합니다.

참고

회전 정책을 비활성화하려면 값을 `0` 으로 설정합니다.

5. `Node` 유형에 대한 검사를 예약하려면 `node-role.kubernetes.io` 레이블 값을 지정합니다. 이 값은 `MachineConfigPool` 의 이름과 일치해야 합니다.

#### 5.4.2.4. 규정 준수 검사 설정을 사용하여 규정 준수 검사 요구 사항 처리

규정 준수 검사 요구 사항을 정의하고 검사를 실행하도록 설정을 구성한 경우 Compliance Operator는 `ScanSettingBinding` 오브젝트를 사용하여 처리합니다.

#### 5.4.2.4.1. ScanSettingBinding 오브젝트

`ScanSettingBinding` 오브젝트를 사용하여 `Profile` 또는 `TailoredProfile` 오브젝트에 대한 참조로 규정 준수 요구 사항을 지정합니다. 그런 다음 검사에 대한 운영 제약 조건을 제공하는 `ScanSetting` 오브젝트에 연결됩니다. 그런 다음 Compliance Operator는 `ScanSetting` 및 `ScanSettingBinding` 오브젝트를 기반으로 `ComplianceSuite` 오브젝트를 생성합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSettingBinding
metadata:
  name: <name of the scan>
profiles:
  # Node checks
  - name: rhcos4-with-usb
    kind: TailoredProfile
    apiGroup: compliance.openshift.io/v1alpha1
  # Cluster checks
  - name: ocp4-moderate
    kind: Profile
    apiGroup: compliance.openshift.io/v1alpha1
settingsRef:
  name: my-companys-constraints
  kind: ScanSetting
  apiGroup: compliance.openshift.io/v1alpha1
```

1. 환경을 검사할 `Profile` 또는 `TailoredProfile` 오브젝트의 세부 정보를 지정합니다.

2. 일정 및 스토리지 크기와 같은 작동 제약 조건을 지정합니다.

`ScanSetting` 및 `ScanSettingBinding` 오브젝트를 생성하면 규정 준수 제품군이 생성됩니다. 규정 준수 제품군 목록을 가져오려면 다음 명령을 실행합니다.

```shell-session
$ oc get compliancesuites
```

중요

`ScanSettingBinding` 을 삭제하면 규정 준수 제품군도 삭제됩니다.

#### 5.4.2.5. 컴플라이언스 검사 추적

규정 준수 제품군 생성 후 `ComplianceSuite` 오브젝트를 사용하여 배포된 검사의 상태를 모니터링할 수 있습니다.

#### 5.4.2.5.1. ComplianceSuite 오브젝트

`ComplianceSuite` 오브젝트를 사용하면 검사 상태를 추적할 수 있습니다. 검사 및 전체 결과를 생성하는 원시 설정이 포함되어 있습니다.

`노드` 유형 검사의 경우 문제에 대한 수정이 포함되어 있으므로 `MachineConfigPool` 에 검사를 매핑해야 합니다. 라벨을 지정하는 경우 풀에 직접 적용되었는지 확인합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ComplianceSuite
metadata:
  name: <name_of_the_suite>
spec:
  autoApplyRemediations: false
  schedule: "0 1 * * *"
  scans:
    - name: workers-scan
      scanType: Node
      profile: xccdf_org.ssgproject.content_profile_moderate
      content: ssg-rhcos4-ds.xml
      contentImage: registry.redhat.io/compliance/openshift-compliance-content-rhel8@sha256:45dc...
      rule: "xccdf_org.ssgproject.content_rule_no_netrc_files"
      nodeSelector:
        node-role.kubernetes.io/worker: ""
status:
  Phase: DONE
  Result: NON-COMPLIANT
  scanStatuses:
  - name: workers-scan
    phase: DONE
    result: NON-COMPLIANT
```

1. 자동 수정을 활성화하려면 `true` 로 설정합니다. 자동 수정을 비활성화하려면 `false` 로 설정합니다.

2. cron 형식으로 검사를 실행하는 빈도를 지정합니다.

3. 클러스터에서 실행할 검사 사양 목록을 지정합니다.

4. 검사 진행 상황을 나타냅니다.

5. 제품군의 전체 평결을 나타냅니다.

백그라운드에서 모음은 `scans` 매개변수를 기반으로 `ComplianceScan` 오브젝트를 생성합니다. `ComplianceSuites` 이벤트를 프로그래밍 방식으로 가져올 수 있습니다. 모음의 이벤트를 가져오려면 다음 명령을 실행합니다.

```shell-session
$ oc get events --field-selector involvedObject.kind=ComplianceSuite,involvedObject.name=<name of the suite>
```

중요

XCCDF 속성이 포함되어 있으므로 `ComplianceSuite` 를 수동으로 정의할 때 오류가 발생할 수 있습니다.

#### 5.4.2.5.2. 고급 ComplianceScan 오브젝트

Compliance Operator에는 고급 사용자가 기존 툴링을 디버깅하거나 통합할 수 있는 옵션이 포함되어 있습니다. `ComplianceScan` 오브젝트를 직접 생성하지 않는 것이 좋지만 대신 `ComplianceSuite` 오브젝트를 사용하여 관리할 수 있습니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ComplianceScan
metadata:
  name: <name_of_the_compliance_scan>
spec:
  scanType: Node
  profile: xccdf_org.ssgproject.content_profile_moderate
  content: ssg-ocp4-ds.xml
  contentImage: registry.redhat.io/compliance/openshift-compliance-content-rhel8@sha256:45dc...
  rule: "xccdf_org.ssgproject.content_rule_no_netrc_files"
  nodeSelector:
    node-role.kubernetes.io/worker: ""
status:
  phase: DONE
  result: NON-COMPLIANT
```

1. `노드` 또는 플랫폼을 `지정합니다`. 노드 프로필은 클러스터 노드 및 플랫폼 프로필을 스캔하여 Kubernetes 플랫폼을 검사합니다.

2. 실행할 프로필의 XCCDF 식별자를 지정합니다.

3. 프로필 파일을 캡슐화하는 컨테이너 이미지를 지정합니다.

4. 이는 선택 사항입니다. 단일 규칙을 실행하려면 검사를 지정합니다. 이 규칙은 XCCDF ID로 식별되어야 하며 지정된 프로필에 속해야 합니다.

참고

`rule` 매개변수를 건너뛰면 지정된 프로필의 사용 가능한 모든 규칙에 대해 검사를 실행합니다.

5. OpenShift Container Platform에 있고 수정을 생성하려면 nodeSelector 레이블이 `MachineConfigPool` 레이블과 일치해야 합니다.

참고

`nodeSelector` 매개변수를 지정하지 않거나 `MachineConfig` 레이블과 일치하지 않으면 검사가 계속 실행되지만 수정이 생성되지 않습니다.

6. 검사의 현재 단계를 나타냅니다.

7. 검사 확인 상태를 나타냅니다.

중요

`ComplianceSuite` 오브젝트를 삭제하면 연결된 모든 검사가 삭제됩니다.

검사가 완료되면 결과를 `ComplianceCheckResult` 오브젝트의 Custom Resources로 생성합니다. 그러나 원시 결과는 ARF 형식으로 제공됩니다. 이러한 결과는 검사 이름과 연결된 PVC(영구 볼륨 클레임)가 있는 PV(영구 볼륨)에 저장됩니다. `ComplianceScans` 이벤트를 프로그래밍 방식으로 가져올 수 있습니다. 모음에 대한 이벤트를 생성하려면 다음 명령을 실행합니다.

```shell-session
oc get events --field-selector involvedObject.kind=ComplianceScan,involvedObject.name=<name_of_the_compliance_scan>
```

#### 5.4.2.6. 규정 준수 결과 보기

규정 준수 제품군이 `DONE` 단계에 도달하면 검사 결과 및 가능한 수정을 볼 수 있습니다.

#### 5.4.2.6.1. ComplianceCheckResult 오브젝트

특정 프로필로 검사를 실행하면 프로필의 여러 규칙이 확인됩니다. 이러한 각 규칙에 대해 특정 규칙에 대한 클러스터 상태를 제공하는 `ComplianceCheckResult` 오브젝트가 생성됩니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ComplianceCheckResult
metadata:
  labels:
    compliance.openshift.io/check-severity: medium
    compliance.openshift.io/check-status: FAIL
    compliance.openshift.io/suite: example-compliancesuite
    compliance.openshift.io/scan-name: workers-scan
  name: workers-scan-no-direct-root-logins
  namespace: openshift-compliance
  ownerReferences:
  - apiVersion: compliance.openshift.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: ComplianceScan
    name: workers-scan
description: <description of scan check>
instructions: <manual instructions for the scan>
id: xccdf_org.ssgproject.content_rule_no_direct_root_logins
severity: medium
status: FAIL
```

1. 검사 검사의 심각도를 설명합니다.

2. 검사 결과를 설명합니다. 가능한 값은 다음과 같습니다.

PASS: 확인에 성공했습니다.

FAIL: 확인에 실패했습니다.

INFO: 확인이 성공했으며 오류로 간주될 만큼 심각하지 않은 것을 발견했습니다.

MANUAL: 검사가 자동으로 상태를 평가할 수 없으며 수동 점검이 필요합니다.

INCONSISTENT: 다른 노드에서 다른 결과를 보고합니다.

ERROR: 성공적으로 실행되지만 완료할 수 없습니다.

NOTAPPLICABLE: 적용되지 않으므로 검사가 실행되지 않았습니다.

제품군에서 모든 점검 결과를 가져오려면 다음 명령을 실행합니다.

```shell-session
oc get compliancecheckresults \
-l compliance.openshift.io/suite=workers-compliancesuite
```

#### 5.4.2.6.2. ComplianceRemediation 오브젝트

특정 검사의 경우 datastream 지정 수정 사항이 있을 수 있습니다. 그러나 Kubernetes 수정 사항을 사용할 수 있는 경우 Compliance Operator는 `ComplianceRemediation` 오브젝트를 생성합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ComplianceRemediation
metadata:
  labels:
    compliance.openshift.io/suite: example-compliancesuite
    compliance.openshift.io/scan-name: workers-scan
    machineconfiguration.openshift.io/role: worker
  name: workers-scan-disable-users-coredumps
  namespace: openshift-compliance
  ownerReferences:
  - apiVersion: compliance.openshift.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: ComplianceCheckResult
    name: workers-scan-disable-users-coredumps
    uid: <UID>
spec:
  apply: false
  object:
    current:
       apiVersion: machineconfiguration.openshift.io/v1
       kind: MachineConfig
       spec:
         config:
           ignition:
             version: 2.2.0
           storage:
             files:
             - contents:
                 source: data:,%2A%20%20%20%20%20hard%20%20%20core%20%20%20%200
               filesystem: root
               mode: 420
               path: /etc/security/limits.d/75-disable_users_coredumps.conf
    outdated: {}
```

1. `true` 는 수정이 적용되었음을 나타냅니다. `false` 는 수정이 적용되지 않았음을 나타냅니다.

2. 수정에 대한 정의가 포함됩니다.

3. 이전 버전의 콘텐츠에서 이전에 구문 분석된 수정을 나타냅니다. Compliance Operator는 오래된 오브젝트를 유지하여 관리자가 새 수정을 적용하기 전에 검토할 수 있는 기회를 제공합니다.

제품군에서 모든 수정을 가져오려면 다음 명령을 실행합니다.

```shell-session
oc get complianceremediations \
-l compliance.openshift.io/suite=workers-compliancesuite
```

자동으로 수정될 수 있는 실패한 검사를 모두 나열하려면 다음 명령을 실행합니다.

```shell-session
oc get compliancecheckresults \
-l 'compliance.openshift.io/check-status in (FAIL),compliance.openshift.io/automated-remediation'
```

수동으로 수정할 수 있는 실패한 검사를 모두 나열하려면 다음 명령을 실행합니다.

```shell-session
oc get compliancecheckresults \
-l 'compliance.openshift.io/check-status in (FAIL),!compliance.openshift.io/automated-remediation'
```

#### 5.5.1. Compliance Operator 설치

Compliance Operator를 사용하려면 먼저 클러스터에 배포되었는지 확인해야 합니다.

중요

이 Operator가 제대로 작동하려면 모든 클러스터 노드에 동일한 릴리스 버전이 있어야 합니다. 예를 들어 RHCOS를 실행하는 노드의 경우 모든 노드에 동일한 RHCOS 버전이 있어야합니다.

중요

Compliance Operator는 OpenShift Dedicated, AWS Classic의 Red Hat OpenShift Service, Microsoft Azure Red Hat OpenShift와 같은 관리형 플랫폼에서 잘못된 결과를 보고할 수 있습니다. 자세한 내용은 Knowledgebase 문서 Compliance Operator에서 Managed Services에서 잘못된 결과를 보고합니다.

중요

Compliance Operator를 배포하기 전에 원시 결과 출력을 저장하기 위해 클러스터에 영구 스토리지를 정의해야 합니다. 자세한 내용은 영구 스토리지 개요 및 기본 스토리지 클래스 관리를 참조하십시오.

#### 5.5.1.1. 웹 콘솔을 통해 Compliance Operator 설치

사전 요구 사항

`admin` 권한이 있어야 합니다.

`StorageClass` 리소스가 구성되어 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 Ecosystem → Software Catalog 로 이동합니다.

Compliance Operator를 검색한 다음 설치 를 클릭합니다.

기본 설치 모드 및 네임스페이스 를 계속 선택하여 Operator가 `openshift-compliance` 네임스페이스에 설치되도록 합니다.

설치 를 클릭합니다.

검증

설치에 성공했는지 확인하려면 다음을 수행하십시오.

에코시스템 → 설치된 Operator 페이지로 이동합니다.

Compliance Operator가 `openshift-compliance` 네임스페이스에 설치되어 있고 해당 상태는 `Succeeded` 인지 확인합니다.

Operator가 성공적으로 설치되지 않은 경우 다음을 수행하십시오.

Ecosystem → Installed Operators 페이지로 이동하여 `Status` 열에 오류 또는 실패가 있는지 검사합니다.

워크로드 → Pod 페이지로 이동하고 `openshift-compliance` 프로젝트에서 문제를 보고하는 Pod의 로그를 확인합니다.

중요

`restricted` SCC(보안 컨텍스트 제약 조건)가 `system:authenticated` 그룹을 포함하도록 수정되었거나 `requiredDropCapabilities` 를 추가한 경우 Compliance Operator 가 권한 문제로 인해 제대로 작동하지 않을 수 있습니다.

Compliance Operator 스캐너 Pod 서비스 계정에 대한 사용자 정의 SCC를 생성할 수 있습니다. 자세한 내용은 Compliance Operator에 대한 사용자 정의 SCC 생성을 참조하십시오.

#### 5.5.1.2. CLI를 사용하여 Compliance Operator 설치

사전 요구 사항

`admin` 권한이 있어야 합니다.

`StorageClass` 리소스가 구성되어 있어야 합니다.

프로세스

`Namespace` 오브젝트를 정의합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    openshift.io/cluster-monitoring: "true"
    pod-security.kubernetes.io/enforce: privileged
  name: openshift-compliance
```

1. OpenShift Container Platform 4.20에서 Pod 보안 레이블을 네임스페이스 수준에서 `privileged` 로 설정해야 합니다.

`Namespace` 오브젝트를 생성합니다.

```shell-session
$ oc create -f namespace-object.yaml
```

`OperatorGroup` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: compliance-operator
  namespace: openshift-compliance
spec:
  targetNamespaces:
  - openshift-compliance
```

`OperatorGroup` 개체를 생성합니다.

```shell-session
$ oc create -f operator-group-object.yaml
```

`Subscription` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: compliance-operator-sub
  namespace: openshift-compliance
spec:
  channel: "stable"
  installPlanApproval: Automatic
  name: compliance-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

`Subscription` 오브젝트를 생성합니다.

```shell-session
$ oc create -f subscription-object.yaml
```

참고

글로벌 스케줄러 기능을 설정하고 `defaultNodeSelector` 를 활성화하는 경우 네임스페이스를 수동으로 생성하고 `openshift-compliance` 네임스페이스의 주석 또는 Compliance Operator가 설치된 네임스페이스를 `openshift.io/node-selector: “”` 로 업데이트해야 합니다. 이렇게 하면 기본 노드 선택기가 제거되고 배포 실패가 발생하지 않습니다.

검증

CSV 파일을 검사하여 설치에 성공했는지 확인합니다.

```shell-session
$ oc get csv -n openshift-compliance
```

Compliance Operator가 실행 중인지 확인합니다.

```shell-session
$ oc get deploy -n openshift-compliance
```

#### 5.5.1.3. ROSA 호스트 컨트롤 플레인 (HCP)에 Compliance Operator 설치

Compliance Operator 1.5.0 릴리스에서 Operator는 호스팅된 컨트롤 플레인을 사용하여 AWS의 Red Hat OpenShift Service에 대해 테스트됩니다.

AWS 호스팅 컨트롤 플레인 클러스터의 Red Hat OpenShift Service는 Red Hat에서 관리하는 컨트롤 플레인에 대한 액세스 권한을 제한합니다. 기본적으로 Compliance Operator는 `마스터` 노드 풀 내의 노드에 스케줄링합니다. 이 풀은 AWS 호스팅 컨트롤 플레인 설치의 Red Hat OpenShift Service에서 사용할 수 없습니다. 이를 위해서는 Operator가 사용 가능한 노드 풀에서 예약할 수 있는 방식으로 `Subscription` 오브젝트를 구성해야 합니다. 이 단계는 AWS 호스팅 컨트롤 플레인 클러스터의 Red Hat OpenShift Service에 성공적으로 설치하기 위해 필요합니다.

사전 요구 사항

`admin` 권한이 있어야 합니다.

`StorageClass` 리소스가 구성되어 있어야 합니다.

프로세스

`Namespace` 오브젝트를 정의합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    openshift.io/cluster-monitoring: "true"
    pod-security.kubernetes.io/enforce: privileged
  name: openshift-compliance
```

1. OpenShift Container Platform 4.20에서 Pod 보안 레이블을 네임스페이스 수준에서 `privileged` 로 설정해야 합니다.

다음 명령을 실행하여 `Namespace` 오브젝트를 생성합니다.

```shell-session
$ oc create -f namespace-object.yaml
```

`OperatorGroup` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: compliance-operator
  namespace: openshift-compliance
spec:
  targetNamespaces:
  - openshift-compliance
```

다음 명령을 실행하여 `OperatorGroup` 오브젝트를 생성합니다.

```shell-session
$ oc create -f operator-group-object.yaml
```

`Subscription` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: compliance-operator-sub
  namespace: openshift-compliance
spec:
  channel: "stable"
  installPlanApproval: Automatic
  name: compliance-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  config:
    nodeSelector:
      node-role.kubernetes.io/worker: ""
```

1. `작업자` 노드에 배포하도록 Operator 배포를 업데이트합니다.

다음 명령을 실행하여 서브스크립션 오브젝트를 생성합니다.

```shell-session
$ oc create -f subscription-object.yaml
```

검증

CSV(클러스터 서비스 버전) 파일을 검사하도록 다음 명령을 실행하여 설치에 성공했는지 확인합니다.

```shell-session
$ oc get csv -n openshift-compliance
```

다음 명령을 사용하여 Compliance Operator가 실행 중인지 확인합니다.

```shell-session
$ oc get deploy -n openshift-compliance
```

중요

`restricted` SCC(보안 컨텍스트 제약 조건)가 `system:authenticated` 그룹을 포함하도록 수정되었거나 `requiredDropCapabilities` 를 추가한 경우 Compliance Operator 가 권한 문제로 인해 제대로 작동하지 않을 수 있습니다.

Compliance Operator 스캐너 Pod 서비스 계정에 대한 사용자 정의 SCC를 생성할 수 있습니다. 자세한 내용은 Compliance Operator에 대한 사용자 정의 SCC 생성을 참조하십시오.

#### 5.5.1.4. Hypershift 호스팅 컨트롤 플레인에 Compliance Operator 설치

Compliance Operator는 `서브스크립션` 파일을 생성하여 소프트웨어 카탈로그를 사용하여 호스팅되는 컨트롤 플레인에 설치할 수 있습니다.

중요

호스팅된 컨트롤 플레인은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

사전 요구 사항

`admin` 권한이 있어야 합니다.

프로세스

다음과 유사한 `Namespace` 오브젝트를 정의합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    openshift.io/cluster-monitoring: "true"
    pod-security.kubernetes.io/enforce: privileged
  name: openshift-compliance
```

1. OpenShift Container Platform 4.20에서 Pod 보안 레이블을 네임스페이스 수준에서 `privileged` 로 설정해야 합니다.

다음 명령을 실행하여 `Namespace` 오브젝트를 생성합니다.

```shell-session
$ oc create -f namespace-object.yaml
```

`OperatorGroup` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: compliance-operator
  namespace: openshift-compliance
spec:
  targetNamespaces:
  - openshift-compliance
```

다음 명령을 실행하여 `OperatorGroup` 오브젝트를 생성합니다.

```shell-session
$ oc create -f operator-group-object.yaml
```

`Subscription` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: compliance-operator-sub
  namespace: openshift-compliance
spec:
  channel: "stable"
  installPlanApproval: Automatic
  name: compliance-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  config:
    nodeSelector:
      node-role.kubernetes.io/worker: ""
    env:
    - name: PLATFORM
      value: "HyperShift"
```

다음 명령을 실행하여 서브스크립션 오브젝트를 생성합니다.

```shell-session
$ oc create -f subscription-object.yaml
```

검증

다음 명령을 실행하여 CSV 파일을 검사하여 설치에 성공했는지 확인합니다.

```shell-session
$ oc get csv -n openshift-compliance
```

다음 명령을 실행하여 Compliance Operator가 실행 중인지 확인합니다.

```shell-session
$ oc get deploy -n openshift-compliance
```

추가 리소스

호스팅된 컨트롤 플레인 개요

#### 5.5.1.5. 추가 리소스

Compliance Operator는 제한된 네트워크 환경에서 지원됩니다. 자세한 내용은 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용을 참조하십시오.

#### 5.5.2. Compliance Operator 업데이트

클러스터 관리자는 OpenShift Container Platform 클러스터에서 Compliance Operator를 업데이트할 수 있습니다.

중요

OpenShift Container Platform 클러스터를 버전 4.14로 업데이트하면 Compliance Operator가 예상대로 작동하지 않을 수 있습니다. 이는 지속적으로 알려진 문제 때문입니다. 자세한 내용은 OCPBUGS-18025 에서 참조하십시오.

#### 5.5.2.1. Operator 업데이트 준비

설치된 Operator의 서브스크립션은 Operator를 추적하고 업데이트를 수신하는 업데이트 채널을 지정합니다. 업데이트 채널을 변경하여 추적을 시작하고 최신 채널에서 업데이트를 수신할 수 있습니다.

서브스크립션의 업데이트 채널 이름은 Operator마다 다를 수 있지만 이름 지정 체계는 일반적으로 지정된 Operator 내의 공통 규칙을 따릅니다. 예를 들어 채널 이름은 Operator(`1.2`, `1.3`) 또는 릴리스 빈도(`stable`, `fast`)에서 제공하는 애플리케이션의 마이너 릴리스 업데이트 스트림을 따를 수 있습니다.

참고

설치된 Operator는 현재 채널보다 오래된 채널로 변경할 수 없습니다.

Red Hat Customer Portal 랩에는 관리자가 Operator 업데이트를 준비하는 데 도움이 되는 다음 애플리케이션이 포함되어 있습니다.

Red Hat OpenShift Container Platform Operator 업데이트 정보 확인기

애플리케이션을 사용하여 Operator Lifecycle Manager 기반 Operator를 검색하고 다양한 OpenShift Container Platform 버전에서 업데이트 채널별로 사용 가능한 Operator 버전을 확인할 수 있습니다. Cluster Version Operator 기반 Operator는 포함되어 있지 않습니다.

#### 5.5.2.2. Operator의 업데이트 채널 변경

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

#### 5.5.2.3. 보류 중인 Operator 업데이트 수동 승인

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

#### 5.5.3. Compliance Operator 관리

이 섹션에서는 업데이트된 버전의 규정 준수 콘텐츠를 사용하는 방법과 사용자 정의 `ProfileBundle` 오브젝트를 만드는 방법을 포함하여 보안 콘텐츠의 라이프사이클에 대해 설명합니다.

#### 5.5.3.1. ProfileBundle CR의 예

`ProfileBundle` 오브젝트에는 `contentImage` 가 포함된 컨테이너 이미지의 URL과 규정 준수 콘텐츠가 포함된 파일의 URL이 필요합니다. `contentFile` 매개변수는 파일 시스템의 루트와 상대적입니다. 다음 예와 같이 내장된 `rhcos4`

`ProfileBundle` 오브젝트를 정의할 수 있습니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ProfileBundle
metadata:
  creationTimestamp: "2022-10-19T12:06:30Z"
  finalizers:
  - profilebundle.finalizers.compliance.openshift.io
  generation: 1
  name: rhcos4
  namespace: openshift-compliance
  resourceVersion: "46741"
  uid: 22350850-af4a-4f5c-9a42-5e7b68b82d7d
spec:
  contentFile: ssg-rhcos4-ds.xml
  contentImage: registry.redhat.io/compliance/openshift-compliance-content-rhel8@sha256:900e...
status:
  conditions:
  - lastTransitionTime: "2022-10-19T12:07:51Z"
    message: Profile bundle successfully parsed
    reason: Valid
    status: "True"
    type: Ready
  dataStreamStatus: VALID
```

1. 규정 준수 콘텐츠가 포함된 파일의 위치입니다.

2. 콘텐츠 이미지 위치입니다.

중요

콘텐츠 이미지에 사용되는 기본 이미지에는 `coreutils` 가 포함되어야 합니다.

#### 5.5.3.2. 보안 콘텐츠 업데이트

보안 콘텐츠는 `ProfileBundle` 오브젝트가 참조하는 컨테이너 이미지로 포함됩니다. `ProfileBundles` 및 규칙 또는 프로필과 같은 번들에서 구문 분석한 사용자 정의 리소스에 대한 업데이트를 정확하게 추적하려면 태그 대신 다이제스트를 사용하여 규정 준수 콘텐츠가 있는 컨테이너 이미지를 확인하십시오.

```shell-session
$ oc -n openshift-compliance get profilebundles rhcos4 -oyaml
```

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ProfileBundle
metadata:
  creationTimestamp: "2022-10-19T12:06:30Z"
  finalizers:
  - profilebundle.finalizers.compliance.openshift.io
  generation: 1
  name: rhcos4
  namespace: openshift-compliance
  resourceVersion: "46741"
  uid: 22350850-af4a-4f5c-9a42-5e7b68b82d7d
spec:
  contentFile: ssg-rhcos4-ds.xml
  contentImage: registry.redhat.io/compliance/openshift-compliance-content-rhel8@sha256:900e...
status:
  conditions:
  - lastTransitionTime: "2022-10-19T12:07:51Z"
    message: Profile bundle successfully parsed
    reason: Valid
    status: "True"
    type: Ready
  dataStreamStatus: VALID
```

1. 보안 컨테이너 이미지입니다.

각 `ProfileBundle` 은 배포를 통해 지원됩니다. Compliance Operator에서 컨테이너 이미지 다이제스트가 변경되었음을 감지하면 배포가 업데이트되어 변경 사항을 반영하고 콘텐츠를 다시 구문 분석합니다. 태그 대신 다이제스트를 사용하면 안정적이고 예측 가능한 프로필 세트를 사용할 수 있습니다.

#### 5.5.3.3. 추가 리소스

Compliance Operator는 제한된 네트워크 환경에서 지원됩니다. 자세한 내용은 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용을 참조하십시오.

#### 5.5.4. Compliance Operator 설치 제거

OpenShift Container Platform 웹 콘솔 또는 CLI를 사용하여 클러스터에서 OpenShift Compliance Operator를 제거할 수 있습니다.

#### 5.5.4.1. 웹 콘솔을 사용하여 OpenShift Container Platform에서 OpenShift Compliance Operator 설치 제거

Compliance Operator를 제거하려면 먼저 네임스페이스에서 오브젝트를 삭제해야 합니다. 오브젝트가 제거되면 openshift-compliance 프로젝트를 삭제하여 Operator 및 해당 네임스페이스를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

OpenShift Compliance Operator가 설치되어 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔을 사용하여 Compliance Operator를 제거하려면 다음을 수행합니다.

에코시스템 → 설치된 Operator →

Compliance Operator 페이지로 이동합니다.

모든 인스턴스를 클릭합니다.

모든 네임스페이스 에서 옵션 메뉴

를 클릭하고 all ScanSettingBinding, ComplainceSuite, ComplianceScan 및 ProfileBundle 오브젝트를 삭제합니다.

관리 → 에코시스템 → 설치된 Operator 페이지로 전환합니다.

Compliance Operator 항목에서 옵션 메뉴

를 클릭하고 Operator 설치 제거를 선택합니다.

홈 → 프로젝트 페이지로 전환합니다.

'compliance'를 검색합니다.

openshift-compliance 프로젝트 옆에 있는 옵션 메뉴

를 클릭하고 프로젝트 삭제 를 선택합니다.

대화 상자에 `openshift-compliance` 를 입력하여 삭제를 확인하고 삭제 를 클릭합니다.

#### 5.5.4.2. CLI를 사용하여 OpenShift Container Platform에서 OpenShift Compliance Operator 설치 제거

Compliance Operator를 제거하려면 먼저 네임스페이스에서 오브젝트를 삭제해야 합니다. 오브젝트가 제거되면 openshift-compliance 프로젝트를 삭제하여 Operator 및 해당 네임스페이스를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

OpenShift Compliance Operator가 설치되어 있어야 합니다.

프로세스

네임스페이스의 모든 오브젝트를 삭제합니다.

`ScanSettingBinding` 오브젝트를 삭제합니다.

```shell-session
$ oc delete ssb --all -n openshift-compliance
```

`ScanSetting` 오브젝트를 삭제합니다.

```shell-session
$ oc delete ss --all -n openshift-compliance
```

`ComplianceSuite` 오브젝트를 삭제합니다.

```shell-session
$ oc delete suite --all -n openshift-compliance
```

`ComplianceScan` 오브젝트를 삭제합니다.

```shell-session
$ oc delete scan --all -n openshift-compliance
```

`ProfileBundle` 오브젝트를 삭제합니다.

```shell-session
$ oc delete profilebundle.compliance --all -n openshift-compliance
```

Subscription 오브젝트를 삭제합니다.

```shell-session
$ oc delete sub --all -n openshift-compliance
```

CSV 오브젝트를 삭제합니다.

```shell-session
$ oc delete csv --all -n openshift-compliance
```

프로젝트를 삭제합니다.

```shell-session
$ oc delete project openshift-compliance
```

```shell-session
project.project.openshift.io "openshift-compliance" deleted
```

검증

네임스페이스가 삭제되었는지 확인합니다.

```shell-session
$ oc get project/openshift-compliance
```

```shell-session
Error from server (NotFound): namespaces "openshift-compliance" not found
```

#### 5.6.1. 지원되는 규정 준수 프로필

Compliance Operator (CO) 설치의 일부로 사용할 수 있는 여러 프로필이 있습니다. 다음 프로필을 사용하여 클러스터의 격차를 평가할 수는 있지만 사용만으로는 특정 프로필의 준수를 유추하거나 보장하지 않으며 감사자가 아닙니다.

이러한 다양한 표준을 준수하거나 인증하려면 QSA(Qualified Security Assessor), 공동 인증 기관(JAB) 또는 기타 업계가 귀하의 환경을 평가할 수 있는 규제 당국을 고용해야 합니다. 표준을 준수하기 위해 권한 있는 감사자와 협력해야 합니다.

모든 Red Hat 제품의 규정 준수 지원에 대한 자세한 내용은 제품 규정 준수 를 참조하십시오.

중요

Compliance Operator는 OpenShift Dedicated 및 Azure Red Hat OpenShift와 같은 일부 관리형 플랫폼에서 잘못된 결과를 보고할 수 있습니다. 자세한 내용은 Red Hat 지식베이스 솔루션 #6983418 을 참조하십시오.

#### 5.6.1.1. 규정 준수 프로필

Compliance Operator는 업계 표준 벤치마크를 충족하기 위한 프로필을 제공합니다.

참고

다음 표에는 Compliance Operator에서 사용 가능한 최신 프로필이 반영되어 있습니다.

#### 5.6.1.1.1. CIS 규정 준수 프로필

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-cis [1] | CIS Red Hat OpenShift Container Platform Benchmark v1.7.0 | 플랫폼 | CIS 벤치마크 ™ [4] | `x86_64` `ppc64le` `s390x` `aarch64` |  |
| ocp4-cis-1-7 [3] | CIS Red Hat OpenShift Container Platform Benchmark v1.7.0 | 플랫폼 | CIS 벤치마크 ™ [4] | `x86_64` `ppc64le` `s390x` `aarch64` |  |
| ocp4-cis-node [1] | CIS Red Hat OpenShift Container Platform Benchmark v1.7.0 | 노드 [2] | CIS 벤치마크 ™ [4] | `x86_64` `ppc64le` `s390x` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-cis-node-1-7 [3] | CIS Red Hat OpenShift Container Platform Benchmark v1.7.0 | 노드 [2] | CIS 벤치마크 ™ [4] | `x86_64` `ppc64le` `s390x` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |

`ocp4-cis` 및 `ocp4-cis-node` 프로필은 Compliance Operator에서 사용 가능하게 되면 CIS 벤치마크의 최신 버전을 유지합니다. CIS v1.7.0과 같은 특정 버전을 준수하려면 `ocp4-cis-1-7` 및 `ocp4-cis-node-1-7` 프로필을 사용합니다.

노드 프로필은 관련 플랫폼 프로필과 함께 사용해야 합니다. 자세한 내용은 Compliance Operator 프로필 유형을 참조하십시오.

이전의 모든 CIS 프로필은 CIS v1.7.0에서 우선합니다. 최신 프로필을 환경에 적용하는 것이 좋습니다.

CIS OpenShift Container Platform v4 벤치마크를 찾으려면 CIS 벤치마크로 이동하여 최신 CIS 벤치마크 다운로드를 클릭합니다. 여기에서 등록하여 벤치마크를 다운로드할 수 있습니다.

#### 5.6.1.1.2. Cryostat 프로파일 지원

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-bsi [1] | Cryostat IT-Grundschutz (Basic Protection) 빌딩 블록 SYS.1.6 및 APP.4.4 | 플랫폼 | Cryostat Basic Protection Compendium | `x86_64` |  |
| ocp4-bsi-node [1] | Cryostat IT-Grundschutz (Basic Protection) 빌딩 블록 SYS.1.6 및 APP.4.4 | 노드 [2] | Cryostat Basic Protection Compendium | `x86_64` |  |
| ocp4-bsi-2022 [3] | Cryostat IT-Grundschutz (Basic Protection) 빌딩 블록 SYS.1.6 및 APP.4.4 | 플랫폼 | Cryostat Basic Protection Compendium | `x86_64` |  |
| ocp4-bsi-node-2022 [3] | Cryostat IT-Grundschutz (Basic Protection) 빌딩 블록 SYS.1.6 및 APP.4.4 | 노드 [2] | Cryostat Basic Protection Compendium | `x86_64` |  |
| rhcos4-bsi [3] | Cryostat IT-Grundschutz (Basic Protection) 빌딩 블록 SYS.1.6 및 APP.4.4 | 노드 [2] | Cryostat Basic Protection Compendium | `x86_64` |  |
| ocp4-bsi-2022 [3] | Cryostat IT-Grundschutz (Basic Protection) 빌딩 블록 SYS.1.6 및 APP.4.4 | 노드 [2] | Cryostat Basic Protection Compendium | `x86_64` |  |

`ocp4-bsi` 및 `ocp4-bsi-node` 프로필은 Compliance Operator에서 사용할 수 있게 되면 ocp4-bsi-node 프로필의 최신 버전을 유지 관리합니다. Cryostat 2022와 같은 특정 버전을 준수하려면 `ocp4-bsi-2022` 및 `ocp4-bsi-node-2022` 프로필을 사용합니다.

노드 프로필은 관련 플랫폼 프로필과 함께 사용해야 합니다. 자세한 내용은 Compliance Operator 프로필 유형을 참조하십시오.

버전 2022는 Cryostat IT-Grundschutz (Basic Protection) 개정판의 최신 영어 버전입니다. 최근 공개된 독일 규정 준수(2023년)에는 Building Blocks SYS.1.6 및 APP.4.4에 대한 변경 사항이 없었습니다.

자세한 내용은 Cryostat Quick Check 를 참조하십시오.

#### 5.6.1.1.3. 필수 Eight 컴플라이언스 프로필

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-e8 | Australian Cyber Security Centre (ACSC) Essential Eight | 플랫폼 | ACSC Hardening Linux Workstations and Servers | `x86_64` |  |
| rhcos4-e8 | Australian Cyber Security Centre (ACSC) Essential Eight | 노드 | ACSC Hardening Linux Workstations and Servers | `x86_64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |

#### 5.6.1.1.4. FedRAMP High Compliance Profile

중요

`service-sshd-disabled` 규칙을 사용하는 `rhcos4-stig` 와 같은 프로필에 자동 수정 사항을 적용하면 `sshd` 서비스가 자동으로 비활성화됩니다. 이 경우 컨트롤 플레인 노드 및 컴퓨팅 노드에 대한 SSH 액세스를 차단합니다. SSH 액세스를 계속 활성화하려면 `TailoredProfile` 오브젝트를 생성하고 `disableRules` 매개변수에 대해 `rhcos4-service-sshd-disabled` 규칙 값을 설정합니다.

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-high [1] | NIST 800-53 High-Impact Baseline for Red Hat OpenShift - 플랫폼 수준 | 플랫폼 | NIST SP-800-53 릴리스 검색 | `x86_64` |  |
| ocp4-high-node [1] | NIST 800-53 High-Impact Baseline for Red Hat OpenShift - 노드 수준 | 노드 [2] | NIST SP-800-53 릴리스 검색 | `x86_64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-high-node-rev-4 | NIST 800-53 High-Impact Baseline for Red Hat OpenShift - 노드 수준 | 노드 [2] | NIST SP-800-53 릴리스 검색 | `x86_64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-high-rev-4 | NIST 800-53 High-Impact Baseline for Red Hat OpenShift - 플랫폼 수준 | 플랫폼 | NIST SP-800-53 릴리스 검색 | `x86_64` |  |
| rhcos4-high [1] | NIST 800-53 High-Impact Baseline for Red Hat Enterprise Linux CoreOS | 노드 | NIST SP-800-53 릴리스 검색 | `x86_64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| rhcos4-high-rev-4 | NIST 800-53 High-Impact Baseline for Red Hat Enterprise Linux CoreOS | 노드 | NIST SP-800-53 릴리스 검색 | `x86_64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |

`ocp4-high`, `ocp4-high-node` 및 `rhcos4-high` 프로필은 Compliance Operator에서 사용할 수 있게 되면 FedRAMP High 표준의 최신 버전을 유지합니다. FedRAMP high R4와 같은 특정 버전을 준수하려면 `ocp4-high-rev-4` 및 `ocp4-high-node-rev-4` 프로필을 사용하십시오.

노드 프로필은 관련 플랫폼 프로필과 함께 사용해야 합니다. 자세한 내용은 Compliance Operator 프로필 유형을 참조하십시오.

#### 5.6.1.1.5. FedRAMP Moderate 규정 준수 프로필

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-moderate [1] | NIST 800-53 Moderate-Impact Baseline for Red Hat OpenShift - 플랫폼 수준 | 플랫폼 | NIST SP-800-53 릴리스 검색 | `x86_64` `ppc64le` `s390x` `aarch64` |  |
| ocp4-moderate-node [1] | NIST 800-53 Moderate-Impact Baseline for Red Hat OpenShift - 노드 수준 | 노드 [2] | NIST SP-800-53 릴리스 검색 | `x86_64` `ppc64le` `s390x` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-moderate-node-rev-4 | NIST 800-53 Moderate-Impact Baseline for Red Hat OpenShift - 노드 수준 | 노드 [2] | NIST SP-800-53 릴리스 검색 | `x86_64` `ppc64le` `s390x` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-moderate-rev-4 | NIST 800-53 Moderate-Impact Baseline for Red Hat OpenShift - 플랫폼 수준 | 플랫폼 | NIST SP-800-53 릴리스 검색 | `x86_64` `ppc64le` `s390x` `aarch64` |  |
| rhcos4-moderate [1] | NIST 800-53 Moderate-Impact Baseline for Red Hat Enterprise Linux CoreOS | 노드 | NIST SP-800-53 릴리스 검색 | `x86_64` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| rhcos4-moderate-rev-4 | NIST 800-53 Moderate-Impact Baseline for Red Hat Enterprise Linux CoreOS | 노드 | NIST SP-800-53 릴리스 검색 | `x86_64` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |

`ocp4-moderate`, `ocp4-moderate-node` 및 `rhcos4-moderate` 프로필은 Compliance Operator에서 사용 가능하게 되면 FedRAMP Moderate 표준의 최신 버전을 유지합니다. FedRAMP Moderate R4와 같은 특정 버전을 준수하려면 `ocp4-moderate-rev-4` 및 `ocp4-moderate-node-rev-4` 프로필을 사용하십시오.

노드 프로필은 관련 플랫폼 프로필과 함께 사용해야 합니다. 자세한 내용은 Compliance Operator 프로필 유형을 참조하십시오.

#### 5.6.1.1.6. NERC-CIP 준수 프로필

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-nerc-cip | OpenShift Container Platform - 플랫폼 수준에 대한 North American Electric Reliability Corporation (NERC) Critical Infrastructure Protection (CIP) insecure standard profile for the OpenShift Container Platform - Platform level | 플랫폼 | NERC CIP 표준 | `x86_64` |  |
| ocp4-nerc-cip-node | OpenShift Container Platform - 노드 수준에 대한 North American Electric Reliability Corporation (NERC) Critical Infrastructure Protection (CIP) insecure standard profile for the OpenShift Container Platform | 노드 [1] | NERC CIP 표준 | `x86_64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| rhcos4-nerc-cip | Red Hat Enterprise Linux CoreOS에 대한 North American Electric Reliability Corporation (NERC) Critical Infrastructure Protection (CIP) securing standards profile for Red Hat Enterprise Linux CoreOS | 노드 | NERC CIP 표준 | `x86_64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |

노드 프로필은 관련 플랫폼 프로필과 함께 사용해야 합니다. 자세한 내용은 Compliance Operator 프로필 유형을 참조하십시오.

#### 5.6.1.1.7. PCI-DSS 규정 준수 프로필

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-pci-dss [1] | OpenShift Container Platform 4의 PCI-DSS v4 Control Baseline | 플랫폼 | PCI 보안 표준 ®pub 문서 라이브러리 | `x86_64` `ppc64le` `aarch64` |  |
| ocp4-pci-dss-3-2 [3] | PCI-DSS v3.2.1 Control Baseline for OpenShift Container Platform 4 | 플랫폼 | PCI 보안 표준 ®pub 문서 라이브러리 | `x86_64` `ppc64le` `s390x` `aarch64` |  |
| ocp4-pci-dss-4-0 | OpenShift Container Platform 4의 PCI-DSS v4 Control Baseline | 플랫폼 | PCI 보안 표준 ®pub 문서 라이브러리 | `x86_64` `ppc64le` `aarch64` |  |
| ocp4-pci-dss-node [1] | OpenShift Container Platform 4의 PCI-DSS v4 Control Baseline | 노드 [2] | PCI 보안 표준 ®pub 문서 라이브러리 | `x86_64` `ppc64le` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-pci-dss-node-3-2 [3] | PCI-DSS v3.2.1 Control Baseline for OpenShift Container Platform 4 | 노드 [2] | PCI 보안 표준 ®pub 문서 라이브러리 | `x86_64` `ppc64le` `s390x` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-pci-dss-node-4-0 | OpenShift Container Platform 4의 PCI-DSS v4 Control Baseline | 노드 [2] | PCI 보안 표준 ®pub 문서 라이브러리 | `x86_64` `ppc64le` `aarch64` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |

`ocp4-pci-dss` 및 `ocp4-pci-dss-node` 프로필은 Compliance Operator에서 사용할 수 있게 되면 PCI-DSS 표준의 최신 버전을 유지합니다. PCI-DSS v3.2.1과 같은 특정 버전을 준수하려면 `ocp4-pci-dss-3-2` 및 `ocp4-pci-dss-node-3-2` 프로필을 사용합니다.

노드 프로필은 관련 플랫폼 프로필과 함께 사용해야 합니다. 자세한 내용은 Compliance Operator 프로필 유형을 참조하십시오.

PCI-DSS v3.2.1은 PCI-DSS v4에 의해 구동됩니다. 최신 프로필을 환경에 적용하는 것이 좋습니다.

#### 5.6.1.1.8. STIG 준수 프로필

중요

`service-sshd-disabled` 규칙을 사용하는 `rhcos4-stig` 와 같은 프로필에 자동 수정 사항을 적용하면 `sshd` 서비스가 자동으로 비활성화됩니다. 이 경우 컨트롤 플레인 노드 및 컴퓨팅 노드에 대한 SSH 액세스를 차단합니다. SSH 액세스를 계속 활성화하려면 `TailoredProfile` 오브젝트를 생성하고 `disableRules` 매개변수에 대해 `rhcos4-service-sshd-disabled` 규칙 값을 설정합니다.

| 프로필 | 프로필 제목 | 애플리케이션 | 업계 컴플라이언스 벤치마크 | 지원되는 아키텍처 | 지원되는 플랫폼 |
| --- | --- | --- | --- | --- | --- |
| ocp4-stig [1] | Red Hat Openshift용 DISA STIG(Security Technical Implementation Guide) | 플랫폼 | DISA-STIG | `x86_64` `ppc64le` |  |
| ocp4-stig-node [1] | Red Hat Openshift용 DISA STIG(Security Technical Implementation Guide) | 노드 [2] | DISA-STIG | `x86_64` `ppc64le` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| ocp4-stig-v2r3 | Red Hat Openshift V2R3용 DISA STIG(Security Agency Security Technical Implementation Guide) | 플랫폼 | DISA-STIG | `x86_64` `ppc64le` |  |
| ocp4-stig-node-v2r3 [1] | Red Hat Openshift V2R3용 DISA STIG(Security Agency Security Technical Implementation Guide) | 노드 | DISA-STIG | `x86_64` `ppc64le` |  |
| rhcos4-stig [1] | Red Hat Openshift용 DISA STIG(Security Technical Implementation Guide) | 노드 | DISA-STIG | `x86_64` `ppc64le` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |
| rhcos4-stig-v2r3 | Red Hat Openshift V2R3용 DISA STIG(Security Agency Security Technical Implementation Guide) | 노드 | DISA-STIG | `x86_64` `ppc64le` | 호스팅된 컨트롤 플레인(ROSA HCP)을 사용하는 AWS의 Red Hat OpenShift Service |

`ocp4-stig`, `ocp4-stig-node` 및 `rhcos4-stig` 프로필은 Compliance Operator에서 사용할 수 있게 되면 DISA-STIG 벤치마크의 최신 버전을 유지합니다. DISA-STIG V2R3과 같은 특정 버전을 준수하려면 `ocp4-stig-v2r3` 및 `ocp4-stig-node-v2r3` 프로필을 사용하십시오.

노드 프로필은 관련 플랫폼 프로필과 함께 사용해야 합니다. 자세한 내용은 Compliance Operator 프로필 유형을 참조하십시오.

DISA-STIG V1R2는 DISA-STIG V2R3에 의해 중첩됩니다. 최신 프로필을 환경에 적용하는 것이 좋습니다.

#### 5.6.1.1.9. 확장된 규정 준수 프로필 정보

일부 규정 준수 프로필에는 다음과 같은 업계 모범 사례를 필요로 하는 제어가 있어 일부 프로필이 다른 프로필을 확장할 수 있습니다. CIS(Center for Internet Security) 모범 사례를 NIST(National Institute of Standards and Technology) 보안 프레임워크와 결합하면 안전하고 호환되는 환경을 위한 경로가 설정됩니다.

예를 들어 NIST High-Impact 및 Moderate-Impact 프로필은 CIS 프로필을 확장하여 규정 준수를 달성합니다. 결과적으로 확장된 규정 준수 프로필을 사용하면 단일 클러스터에서 두 프로필을 모두 실행할 필요가 없습니다.

| 프로필 | 확장 |
| --- | --- |
| ocp4-pci-dss | ocp4-cis |
| ocp4-pci-dss-node | ocp4-cis-node |
| ocp4-high | ocp4-cis |
| ocp4-high-node | ocp4-cis-node |
| ocp4-moderate | ocp4-cis |
| ocp4-moderate-node | ocp4-cis-node |
| ocp4-nerc-cip | ocp4-moderate |
| ocp4-nerc-cip-node | ocp4-moderate-node |

#### 5.6.1.1.10. Compliance Operator 프로필 유형

Compliance Operator 규칙은 프로필로 구성됩니다. 프로필은 OpenShift Container Platform의 플랫폼 또는 노드를 대상으로 지정할 수 있으며 일부 벤치마크에는 `rhcos4` 노드 프로필이 포함됩니다.

플랫폼

플랫폼 프로필은 OpenShift Container Platform 클러스터 구성 요소를 평가합니다. 예를 들어 플랫폼 수준 규칙은 APIServer 구성이 강력한 암호화 Ccyphers를 사용하는지 여부를 확인할 수 있습니다.

노드

노드 프로필은 각 호스트의 OpenShift 또는 RHCOS 구성을 평가합니다. 두 개의 노드 프로필 `ocp4` 노드 프로필 및 `rhcos4` 노드 프로필을 사용할 수 있습니다. `ocp4` 노드 프로필은 각 호스트의 OpenShift 구성을 평가합니다. 예를 들어 `kubeconfig` 파일에 규정 준수 표준을 충족할 수 있는 올바른 권한이 있는지 확인할 수 있습니다. `rhcos4` 노드 프로필은 각 호스트의 RHCOS(Red Hat Enterprise Linux CoreOS) 구성을 평가합니다. 예를 들어 SSHD 서비스가 암호 로그인을 비활성화하도록 구성되어 있는지 확인할 수 있습니다.

중요

PCI-DSS와 같은 Node 및 Platform 프로필이 있는 벤치마크의 경우 OpenShift Container Platform 환경에서 두 프로필을 모두 실행해야 합니다.

`ocp4` Platform, `ocp4` Node 및 `rhcos4` Node 프로필이 있는 벤치마크의 경우 OpenShift Container Platform 환경에서 세 개의 프로필을 모두 실행해야 합니다.

참고

노드가 많은 클러스터에서 `ocp4` Node 및 `rhcos4` 노드 검사를 완료하는 데 시간이 오래 걸릴 수 있습니다.

#### 5.6.2. Compliance Operator 검사

Compliance Operator를 사용하여 규정 준수 검사를 실행하도록 `ScanSetting` 및 `ScanSettingBinding` API를 사용하는 것이 좋습니다. 이러한 API 오브젝트에 대한 자세한 내용을 보려면 다음을 실행합니다.

```shell-session
$ oc explain scansettings
```

```shell-session
$ oc explain scansettingbindings
```

#### 5.6.2.1. 규정 준수 검사 실행

CIS(Center for Internet Security) 프로필을 사용하여 검사를 실행할 수 있습니다. 편의를 위해 Compliance Operator는 시작 시 적절한 기본값을 사용하여 `ScanSetting` 오브젝트를 생성합니다. 이 `ScanSetting` 오브젝트의 이름은 `default` 입니다.

참고

올인원 컨트롤 플레인 및 작업자 노드의 경우 규정 준수 검사가 작업자 및 컨트롤 플레인 노드에서 두 번 실행됩니다. 규정 준수 검사에서 일관성 없는 검사 결과가 생성될 수 있습니다. `ScanSetting` 오브젝트에서 단일 역할만 정의하여 일관성 없는 결과를 방지할 수 있습니다.

중요

Compliance Operator는 컨트롤 플레인에서 `aarch64` 또는 `x86` CPU를 사용하는지 여부에 관계없이 다중 아키텍처 컴퓨팅 머신이 있는 클러스터에서 `INCONSISTENT` 를 보고합니다. 이는 다른 아키텍처에서 다르게 작동하는 것과 동일한 규칙 때문입니다. Compliance Operator가 여러 노드의 결과를 단일 결과로 집계하는 노드 검사에만 적용 가능해야 합니다.

일관성 없는 검사 결과에 대한 자세한 내용은 Compliance Operator에 INCONSISTENT 검사 결과가 작업자 노드와 함께 표시됩니다.

프로세스

다음 명령을 실행하여 `ScanSetting` 오브젝트를 검사합니다.

```shell-session
$ oc describe scansettings default -n openshift-compliance
```

```yaml
Name:                  default
Namespace:             openshift-compliance
Labels:                <none>
Annotations:           <none>
API Version:           compliance.openshift.io/v1alpha1
Kind:                  ScanSetting
Max Retry On Timeout:  3
Metadata:
  Creation Timestamp:  2024-07-16T14:56:42Z
  Generation:          2
  Resource Version:    91655682
  UID:                 50358cf1-57a8-4f69-ac50-5c7a5938e402
Raw Result Storage:
  Node Selector:
    node-role.kubernetes.io/master:
  Pv Access Modes:
    ReadWriteOnce
  Rotation:            3
  Size:                1Gi
  Storage Class Name:  standard
  Tolerations:
    Effect:              NoSchedule
    Key:                 node-role.kubernetes.io/master
    Operator:            Exists
    Effect:              NoExecute
    Key:                 node.kubernetes.io/not-ready
    Operator:            Exists
    Toleration Seconds:  300
    Effect:              NoExecute
    Key:                 node.kubernetes.io/unreachable
    Operator:            Exists
    Toleration Seconds:  300
    Effect:              NoSchedule
    Key:                 node.kubernetes.io/memory-pressure
    Operator:            Exists
Roles:
  master
  worker
Scan Tolerations:
  Operator:           Exists
Schedule:             0 1 * * *
Show Not Applicable:  false
Strict Node Scan:     true
Suspend:              false
Timeout:              30m
Events:               <none>
```

1. Compliance Operator는 검사 결과가 포함된 PV(영구 볼륨)를 생성합니다. 기본적으로 PV는 Compliance Operator에서 클러스터에 구성된 스토리지 클래스에 대한 가정을 할 수 없기 때문에 액세스 모드 `ReadWriteOnce` 를 사용합니다. 대부분의 클러스터에서 `ReadWriteOnce` 액세스 모드를 사용할 수 있습니다. 검사 결과를 가져오려면 볼륨을 바인딩하는 도우미 Pod를 사용하여 이를 수행할 수 있습니다. `ReadWriteOnce` 액세스 모드를 사용하는 볼륨은 한 번에 하나의 Pod에서만 마운트할 수 있으므로 도우미 Pod를 삭제해야 합니다. 그러지 않으면 Compliance Operator가 후속 검사에 볼륨을 재사용할 수 없습니다.

2. Compliance Operator는 세 번의 후속 검사 결과를 볼륨에 보관합니다. 이전 검사는 순환됩니다.

3. Compliance Operator는 검사 결과에 대해 1GB의 스토리지를 할당합니다.

4. `scansetting.rawResultStorage.storageClassName` 필드는 원시 결과를 저장하기 위해 `PersistentVolumeClaim` 오브젝트를 생성할 때 사용할 `storageClassName` 값을 지정합니다. 기본값은 null이며 클러스터에 구성된 기본 스토리지 클래스를 사용하려고 합니다. 기본 클래스가 지정되지 않은 경우 기본 클래스를 설정해야 합니다.

5. 6

검사 설정에서 클러스터 노드를 검사하는 프로필을 사용하는 경우 이러한 노드 역할을 검사합니다.

7. 기본 검사 설정 오브젝트는 모든 노드를 검사합니다.

8. 기본 검사 설정 오브젝트는 매일 01:00에 검사를 실행합니다.

기본 검사 설정 대신 다음과 같은 설정이 있는 `default-auto-apply` 를 사용할 수 있습니다.

```yaml
Name:                      default-auto-apply
Namespace:                 openshift-compliance
Labels:                    <none>
Annotations:               <none>
API Version:               compliance.openshift.io/v1alpha1
Auto Apply Remediations:   true
Auto Update Remediations:  true
Kind:                      ScanSetting
Metadata:
  Creation Timestamp:  2022-10-18T20:21:00Z
  Generation:          1
  Managed Fields:
    API Version:  compliance.openshift.io/v1alpha1
    Fields Type:  FieldsV1
    fieldsV1:
      f:autoApplyRemediations:
      f:autoUpdateRemediations:
      f:rawResultStorage:
        .:
        f:nodeSelector:
          .:
          f:node-role.kubernetes.io/master:
        f:pvAccessModes:
        f:rotation:
        f:size:
        f:tolerations:
      f:roles:
      f:scanTolerations:
      f:schedule:
      f:showNotApplicable:
      f:strictNodeScan:
    Manager:         compliance-operator
    Operation:       Update
    Time:            2022-10-18T20:21:00Z
  Resource Version:  38840
  UID:               8cb0967d-05e0-4d7a-ac1c-08a7f7e89e84
Raw Result Storage:
  Node Selector:
    node-role.kubernetes.io/master:
  Pv Access Modes:
    ReadWriteOnce
  Rotation:  3
  Size:      1Gi
  Tolerations:
    Effect:              NoSchedule
    Key:                 node-role.kubernetes.io/master
    Operator:            Exists
    Effect:              NoExecute
    Key:                 node.kubernetes.io/not-ready
    Operator:            Exists
    Toleration Seconds:  300
    Effect:              NoExecute
    Key:                 node.kubernetes.io/unreachable
    Operator:            Exists
    Toleration Seconds:  300
    Effect:              NoSchedule
    Key:                 node.kubernetes.io/memory-pressure
    Operator:            Exists
Roles:
  master
  worker
Scan Tolerations:
  Operator:           Exists
Schedule:             0 1 * * *
Show Not Applicable:  false
Strict Node Scan:     true
Events:               <none>
```

1. 2

`autoUpdateRemediations` 및 `autoApplyRemediations` 플래그를 `true` 로 설정하면 추가 단계 없이 자동으로 조정되는 `ScanSetting` 오브젝트를 쉽게 생성할 수 있습니다.

기본 `ScanSetting` 오브젝트에 바인딩하는 `ScanSettingBinding` 오브젝트를 생성하고 `cis` 및 `cis-node` 프로파일을 사용하여 클러스터를 검사합니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSettingBinding
metadata:
  name: cis-compliance
  namespace: openshift-compliance
profiles:
  - name: ocp4-cis-node
    kind: Profile
    apiGroup: compliance.openshift.io/v1alpha1
  - name: ocp4-cis
    kind: Profile
    apiGroup: compliance.openshift.io/v1alpha1
settingsRef:
  name: default
  kind: ScanSetting
  apiGroup: compliance.openshift.io/v1alpha1
```

다음을 실행하여 `ScanSettingBinding` 오브젝트를 생성합니다.

```shell-session
$ oc create -f <file-name>.yaml -n openshift-compliance
```

프로세스의 이 시점에서 `ScanSettingBinding` 오브젝트는 `Binding` 및 `Bound` 설정을 기반으로 조정됩니다. Compliance Operator는 `ComplianceSuite` 오브젝트 및 관련 `ComplianceScan` 오브젝트를 생성합니다.

다음을 실행하여 컴플라이언스 검사 진행 상황을 따르십시오.

```shell-session
$ oc get compliancescan -w -n openshift-compliance
```

검사는 스캔 단계를 통해 진행되며 완료되면 `DONE` 단계에 도달합니다. 대부분의 경우 검사 결과는 `NON-COMPLIANT` 입니다. 검사 결과를 검토하고 업데이트 적용 작업을 시작하여 클러스터를 준수하도록 할 수 있습니다. 자세한 내용은 Compliance Operator 수정 관리를 참조하십시오.

#### 5.6.2.2. 결과에 대한 사용자 정의 스토리지 크기 설정

`ComplianceCheckResult` 와 같은 사용자 정의 리소스는 검사한 모든 노드에서 집계한 한 번의 점검 결과를 나타내지만 스캐너에서 생성한 원시 결과를 검토하는 것이 유용할 수 있습니다. 원시 결과는 ARF 형식으로 생성되며 크기가 클 수 있습니다(노드당 수십 메가바이트). 따라서 `etcd` 키-값 저장소에서 지원하는 Kubernetes 리소스에 저장하는 것은 비현실적입니다. 대신 검사할 때마다 기본 크기가 1GB인 영구 볼륨(PV)이 생성됩니다. 환경에 따라 적절하게 PV 크기를 늘릴 수 있습니다. 크기를 늘리려면 `ScanSetting` 및 `ComplianceScan` 리소스 모두에 노출되는 `rawResultStorage.size` 특성을 사용하면 됩니다.

관련 매개변수는 `rawResultStorage.rotation` 으로, 이전 검사가 되풀이되기 전에 PV에 유지되는 검사 수를 조절합니다. 기본값은 3이며 되풀이 정책을 0으로 설정하면 되풀이가 비활성화됩니다. 기본 되풀이 정책과 원시 ARF 검사 보고서당 100MB의 추정치가 지정되면 환경에 적합한 PV 크기를 계산할 수 있습니다.

#### 5.6.2.2.1. 사용자 정의 결과 스토리지 값 사용

OpenShift Container Platform은 다양한 퍼블릭 클라우드 또는 베어 메탈에 배포할 수 있으므로 Compliance Operator에서는 사용 가능한 스토리지 구성을 결정할 수 없습니다. 기본적으로 Compliance Operator는 클러스터의 기본 스토리지 클래스를 사용하여 결과를 저장하는 PV를 생성하지만 사용자 정의 스토리지 클래스는 `rawResultStorage.StorageClassName` 특성을 사용하여 구성할 수 있습니다.

중요

클러스터에서 기본 스토리지 클래스를 지정하지 않는 경우 이 특성을 설정해야 합니다.

표준 스토리지 클래스를 사용하고 마지막 결과 10개를 유지하는 10GB 크기의 영구 볼륨을 만들도록 `ScanSetting` 사용자 정의 리소스를 구성합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  name: default
  namespace: openshift-compliance
rawResultStorage:
  storageClassName: standard
  rotation: 10
  size: 10Gi
roles:
- worker
- master
scanTolerations:
- effect: NoSchedule
  key: node-role.kubernetes.io/master
  operator: Exists
schedule: '0 1 * * *'
```

#### 5.6.2.3. 작업자 노드에서 결과 서버 Pod 예약

결과 서버 Pod는 원시 자산 보고 형식(ARF) 검사 결과를 저장하는 PV(영구 볼륨)를 마운트합니다. `nodeSelector` 및 `허용 오차` 속성을 사용하면 결과 서버 Pod의 위치를 구성할 수 있습니다.

이는 컨트롤 플레인 노드가 영구 볼륨을 마운트할 수 없는 환경에 유용합니다.

프로세스

Compliance Operator에 대한 `ScanSetting` CR(사용자 정의 리소스)을 생성합니다.

`ScanSetting` CR을 정의하고 YAML 파일(예: `rs-workers.yaml`)을 저장합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  name: rs-on-workers
  namespace: openshift-compliance
rawResultStorage:
  nodeSelector:
    node-role.kubernetes.io/worker: ""
  pvAccessModes:
  - ReadWriteOnce
  rotation: 3
  size: 1Gi
  tolerations:
  - operator: Exists
roles:
- worker
- master
scanTolerations:
  - operator: Exists
schedule: 0 1 * * *
```

1. Compliance Operator는 이 노드를 사용하여 검사 결과를 ARF 형식으로 저장합니다.

2. 결과 서버 Pod는 모든 테인트를 허용합니다.

`ScanSetting` CR을 생성하려면 다음 명령을 실행합니다.

```shell-session
$ oc create -f rs-workers.yaml
```

검증

`ScanSetting` 오브젝트가 생성되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get scansettings rs-on-workers -n openshift-compliance -o yaml
```

```shell-session
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  creationTimestamp: "2021-11-19T19:36:36Z"
  generation: 1
  name: rs-on-workers
  namespace: openshift-compliance
  resourceVersion: "48305"
  uid: 43fdfc5f-15a7-445a-8bbc-0e4a160cd46e
rawResultStorage:
  nodeSelector:
    node-role.kubernetes.io/worker: ""
  pvAccessModes:
  - ReadWriteOnce
  rotation: 3
  size: 1Gi
  tolerations:
  - operator: Exists
roles:
- worker
- master
scanTolerations:
- operator: Exists
schedule: 0 1 * * *
strictNodeScan: true
```

#### 5.6.2.4. ScanSetting 사용자 정의 리소스

`ScanSetting` 사용자 정의 리소스를 사용하면 검사 제한 속성을 통해 스캐너 Pod의 기본 CPU 및 메모리 제한을 덮어쓸 수 있습니다. Compliance Operator는 500Mi 메모리, 스캐너 컨테이너의 경우 100m CPU, `api-resource-collector` 컨테이너의 100m CPU가 있는 200Mi 메모리를 사용합니다. Operator의 메모리 제한을 설정하려면 OLM 또는 Operator 배포 자체를 통해 설치된 경우 `Subscription` 오브젝트를 수정합니다.

Compliance Operator의 기본 CPU 및 메모리 제한을 늘리려면 Compliance Operator 리소스 제한 증가를 참조하십시오.

중요

기본 제한이 충분하지 않고 OOM(Out Of Memory) 프로세스에서 Operator 또는 스캐너 Pod를 종료하는 경우 Compliance Operator 또는 스캐너 Pod의 메모리 제한을 늘려야 합니다. 자세한 내용은 Compliance Operator 리소스 제한 증가를 참조하십시오.

#### 5.6.2.5. 호스트된 컨트롤 플레인 관리 클러스터 구성

자체 호스팅 컨트롤 플레인 또는 Hypershift 환경을 호스팅하고 관리 클러스터에서 호스팅된 클러스터를 검사하려면 대상 호스팅 클러스터의 이름 및 접두사 네임스페이스를 설정해야 합니다. `TailoredProfile` 을 생성하여 이를 수행할 수 있습니다.

중요

이 절차는 자체 호스팅 컨트롤 플레인 환경을 관리하는 사용자에게만 적용됩니다.

참고

호스트된 컨트롤 플레인 관리 클러스터에서 `ocp4-cis` 및 `ocp4-pci-dss` 프로필만 지원됩니다.

사전 요구 사항

Compliance Operator는 관리 클러스터에 설치됩니다.

프로세스

다음 명령을 실행하여 검사할 호스팅 클러스터의 `이름과`

`네임스페이스` 를 가져옵니다.

```shell-session
$ oc get hostedcluster -A
```

```shell-session
NAMESPACE       NAME                   VERSION   KUBECONFIG                              PROGRESS    AVAILABLE   PROGRESSING   MESSAGE
local-cluster   79136a1bdb84b3c13217   4.13.5    79136a1bdb84b3c13217-admin-kubeconfig   Completed   True        False         The hosted control plane is available
```

관리 클러스터에서 검사 프로필을 확장한 `TailoredProfile` 을 생성하고 스캔할 Hosted Cluster의 이름과 네임스페이스를 정의합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: TailoredProfile
metadata:
  name: hypershift-cisk57aw88gry
  namespace: openshift-compliance
spec:
  description: This profile test required rules
  extends: ocp4-cis
  title: Management namespace profile
  setValues:
  - name: ocp4-hypershift-cluster
    rationale: This value is used for HyperShift version detection
    value: 79136a1bdb84b3c13217
  - name: ocp4-hypershift-namespace-prefix
    rationale: This value is used for HyperShift control plane namespace detection
    value: local-cluster
```

1. 변수. 호스트된 컨트롤 플레인 관리 클러스터에서 `ocp4-cis` 및 `ocp4-pci-dss` 프로필만 지원됩니다.

2. `값은` 이전 단계의 출력에서 `NAME` 입니다.

3. `값은` 이전 단계의 출력에서 `NAMESPACE` 입니다.

`TailoredProfile` 을 생성합니다.

```shell-session
$ oc create -n openshift-compliance -f mgmt-tp.yaml
```

#### 5.6.2.6. 리소스 요청 및 제한 적용

kubelet은 컨테이너를 Pod의 일부로 시작하면 kubelet은 해당 컨테이너의 메모리 및 CPU에 대한 요청 및 제한을 컨테이너 런타임으로 전달합니다. Linux에서 컨테이너 런타임은 사용자가 정의한 제한을 적용하고 적용하는 커널 cgroup을 구성합니다.

CPU 제한은 컨테이너에서 사용할 수 있는 CPU 시간을 정의합니다. 각 스케줄링 간격 동안 Linux 커널은 이 제한이 초과되었는지 확인합니다. 이 경우 커널은 cgroup 실행이 다시 시작될 때까지 기다립니다.

일련의 시스템에서 여러 다른 컨테이너(cgroups)를 실행하려는 경우 더 큰 CPU 요청이 있는 워크로드가 작은 요청이 있는 워크로드보다 더 많은 CPU 시간이 할당됩니다. 메모리 요청은 Pod 예약 중에 사용됩니다. cgroups v2를 사용하는 노드에서 컨테이너 런타임은 메모리 요청을 힌트로 사용하여 `memory.min` 및 `memory.low` 값을 설정할 수 있습니다.

컨테이너가 이 제한보다 많은 메모리를 할당하려고 하면 Linux 커널 메모리 부족 하위 시스템이 활성화되고 메모리를 할당하려는 컨테이너의 프로세스 중 하나를 중지하여 개입합니다. Pod 또는 컨테이너의 메모리 제한은 emptyDir과 같이 메모리 지원 볼륨의 페이지에도 적용할 수 있습니다.

kubelet은 로컬 임시 스토리지 대신 컨테이너 메모리가 사용되므로 `tmpfs`

`emptyDir` 볼륨을 추적합니다. 컨테이너가 메모리 요청을 초과하고 실행 중인 노드가 전체 메모리가 되면 Pod의 컨테이너가 제거될 수 있습니다.

중요

컨테이너는 연장된 기간 동안 CPU 제한을 초과할 수 없습니다. 컨테이너 실행 시간은 과도한 CPU 사용을 위해 Pod 또는 컨테이너를 중지하지 않습니다. 리소스 제한으로 인해 컨테이너를 예약할 수 없거나 종료되는지 확인하려면 Compliance Operator 문제 해결을 참조하십시오.

#### 5.6.2.7. 컨테이너 리소스 요청을 사용하여 Pod 예약

Pod가 생성되면 스케줄러에서 Pod를 실행할 노드를 선택합니다. 각 노드에는 Pod에 제공할 수 있는 CPU 및 메모리 양의 각 리소스 유형에 대한 최대 용량이 있습니다. 스케줄러는 예약된 컨테이너의 리소스 요청 합계가 각 리소스 유형의 용량 노드보다 작은지 확인합니다.

노드의 메모리 또는 CPU 리소스 사용량이 매우 낮지만 용량 검사에서 노드의 리소스 부족으로부터 보호하지 못하는 경우에도 스케줄러에서 노드에 Pod를 배치하지 못할 수 있습니다.

각 컨테이너에 대해 다음 리소스 제한 및 요청을 지정할 수 있습니다.

```shell-session
spec.containers[].resources.limits.cpu
spec.containers[].resources.limits.memory
spec.containers[].resources.limits.hugepages-<size>
spec.containers[].resources.requests.cpu
spec.containers[].resources.requests.memory
spec.containers[].resources.requests.hugepages-<size>
```

개별 컨테이너에 대한 요청 및 제한을 지정할 수 있지만 Pod에 대한 전체 리소스 요청 및 제한을 고려하는 것도 유용합니다. 특정 리소스의 경우 컨테이너 리소스 요청 또는 제한은 Pod의 각 컨테이너에 대한 리소스 요청 또는 제한의 합계입니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: frontend
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: images.my-company.example/app:v4
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: [ALL]
  - name: log-aggregator
    image: images.my-company.example/log-aggregator:v6
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: [ALL]
```

1. 컨테이너는 64Mi의 메모리와 250 m CPU를 요청하고 있습니다.

2. 컨테이너의 제한은 128 Mi의 메모리 및 500 m CPU입니다.

#### 5.6.3. Compliance Operator 조정

Compliance Operator는 즉시 사용할 수 있는 프로필과 함께 제공되지만 조직의 필요 및 요구 사항에 맞게 수정해야 합니다. 프로필을 수정하는 프로세스를 조정 이라고 합니다.

Compliance Operator는 프로필을 조정하는 데 도움이 되도록 `TailoredProfile` 오브젝트를 제공합니다.

#### 5.6.3.1. 새 맞춤형 프로파일 생성

`TailoredProfile` 오브젝트를 사용하여 처음부터 맞춤형 프로필을 작성할 수 있습니다. 적절한 `title` 및 `description` 을 설정하고 `extends` 필드를 비워 둡니다. Compliance Operator에 이 사용자 정의 프로파일에서 생성할 검사 유형을 나타냅니다.

노드 검사: 운영 체제를 검사합니다.

플랫폼 검사: OpenShift Container Platform 구성을 검사합니다.

프로세스

`TailoredProfile` 오브젝트에 다음 주석을 설정합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: TailoredProfile
metadata:
  name: new-profile
  annotations:
    compliance.openshift.io/product-type: Node
spec:
  extends: ocp4-cis-node
  description: My custom profile
  title: Custom profile
  enableRules:
    - name: ocp4-etcd-unique-ca
      rationale: We really need to enable this
  disableRules:
    - name: ocp4-file-groupowner-cni-conf
      rationale: This does not apply to the cluster
```

1. 그에 따라 `노드` 또는 `플랫폼을` 설정합니다.

2. `extends` 필드는 선택 사항입니다.

3. `description` 필드를 사용하여 새 `TailoredProfile` 오브젝트의 기능을 설명합니다.

4. `TailoredProfile` 오브젝트에 `제목을 지정합니다`.

참고

`TailoredProfile` 오브젝트의 `name` 필드에 `-node` 접미사를 추가하는 것은 `Node` 제품 유형 주석을 추가하고 운영 체제 검사를 생성하는 것과 유사합니다.

#### 5.6.3.2. 맞춤형 프로필을 사용하여 기존 ProfileBundles 확장

`TailoredProfile` CR에서는 가장 일반적인 맞춤 작업을 수행할 수 있지만 XCCDF 표준을 사용하면 OpenSCAP 프로필 맞춤 시 유연성이 훨씬 더 향상됩니다. 또한 조직에서 이전에 OpenScap을 사용한 적이 있는 경우 기존 XCCDF 맞춤 파일이 있을 수 있으며 이 파일을 다시 사용할 수 있습니다.

`ComplianceSuite` 오브젝트에는 사용자 정의 맞춤 파일을 가리킬 수 있는 선택적 `TailoringConfigMap` 특성이 포함되어 있습니다. `TailoringConfigMap` 특성 값은 구성 맵의 이름으로, 이 맵에는 `tailoring.xml` 이라는 키가 포함되어야 하며 이 키의 값은 맞춤 콘텐츠입니다.

프로세스

RHCOS(Red Hat Enterprise Linux CoreOS) `ProfileBundle` 에 사용 가능한 규칙을 찾습니다.

```shell-session
$ oc get rules.compliance -n openshift-compliance -l compliance.openshift.io/profile-bundle=rhcos4
```

해당 `ProfileBundle` 에서 사용 가능한 변수를 찾습니다.

```shell-session
$ oc get variables.compliance -n openshift-compliance -l compliance.openshift.io/profile-bundle=rhcos4
```

`nist-moderate-modified` 라는 맞춤형 프로필을 만듭니다.

`nist-moderate-modified` 맞춤형 프로필에 추가할 규칙을 선택합니다. 이 예제에서는 두 개의 규칙을 비활성화하고 하나의 값을 변경하여 `rhcos4-moderate` 프로필을 확장합니다. `rationale` 값을 사용하여 이러한 변경이 이루어진 이유를 설명합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: TailoredProfile
metadata:
  name: nist-moderate-modified
spec:
  extends: rhcos4-moderate
  description: NIST moderate profile
  title: My modified NIST moderate profile
  disableRules:
  - name: rhcos4-file-permissions-var-log-messages
    rationale: The file contains logs of error messages in the system
  - name: rhcos4-account-disable-post-pw-expiration
    rationale: No need to check this as it comes from the IdP
  setValues:
  - name: rhcos4-var-selinux-state
    rationale: Organizational requirements
    value: permissive
```

| 속성 | 설명 |
| --- | --- |
| `extends` | 이 `TailoredProfile` 이 빌드되는 `Profile` 오브젝트의 이름입니다. |
| `title` | `TailoredProfile` 의 사람이 읽을 수 있는 제목입니다. |
| `disableRules` | 이름 및 이유 쌍 목록입니다. 각 이름은 비활성화할 규칙 오브젝트의 이름을 나타냅니다. 이유 값은 규칙이 비활성화된 이유를 설명하는 사람이 읽을 수 있는 텍스트입니다. |
| `manualRules` | 이름 및 이유 쌍 목록입니다. 수동 규칙이 추가되면 검사 결과 상태가 항상 `수동` 이 되고 수정 사항이 생성되지 않습니다. 이 속성은 자동이며 기본적으로 수동 규칙으로 설정할 때 값이 없습니다. |
| `enableRules` | 이름 및 이유 쌍 목록입니다. 각 이름은 활성화할 규칙 오브젝트의 이름을 나타냅니다. 이유 값은 규칙이 활성화된 이유를 설명하는 사람이 읽을 수 있는 텍스트입니다. |
| `description` | `TailoredProfile` 을 설명하는 사람이 읽을 수 있는 텍스트입니다. |
| `setValues` | 이름, 이유 및 값 그룹화 목록입니다. 각 이름은 설정된 값의 이름을 나타냅니다. 이유는 집합을 설명하는 사람이 읽을 수 있는 텍스트입니다. 값은 실제 설정입니다. |

`tailoredProfile.spec.manualRules` 속성을 추가합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: TailoredProfile
metadata:
  name: ocp4-manual-scc-check
spec:
  extends: ocp4-cis
  description: This profile extends ocp4-cis by forcing the SCC check to always return MANUAL
  title: OCP4 CIS profile with manual SCC check
  manualRules:
    - name: ocp4-scc-limit-container-allowed-capabilities
      rationale: We use third party software that installs its own SCC with extra privileges
```

`TailoredProfile` 오브젝트를 생성합니다.

```shell-session
$ oc create -n openshift-compliance -f new-profile-node.yaml
```

1. `TailoredProfile` 오브젝트는 기본 `openshift-compliance` 네임스페이스에 생성됩니다.

```shell-session
tailoredprofile.compliance.openshift.io/nist-moderate-modified created
```

새 `nist-moderate-modified` 맞춤형 프로필을 기본 `ScanSetting` 오브젝트에 바인딩하도록 `ScanSettingBinding` 오브젝트를 정의합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSettingBinding
metadata:
  name: nist-moderate-modified
profiles:
  - apiGroup: compliance.openshift.io/v1alpha1
    kind: Profile
    name: ocp4-moderate
  - apiGroup: compliance.openshift.io/v1alpha1
    kind: TailoredProfile
    name: nist-moderate-modified
settingsRef:
  apiGroup: compliance.openshift.io/v1alpha1
  kind: ScanSetting
  name: default
```

`ScanSettingBinding` 오브젝트를 생성합니다.

```shell-session
$ oc create -n openshift-compliance -f new-scansettingbinding.yaml
```

```shell-session
scansettingbinding.compliance.openshift.io/nist-moderate-modified created
```

#### 5.6.4. Compliance Operator 원시 결과 검색

OpenShift Container Platform 클러스터의 규정 준수를 입증할 때 감사 목적으로 검사 결과를 제공해야 할 수 있습니다.

#### 5.6.4.1. 영구 볼륨에서 Compliance Operator 원시 결과 가져오기

프로세스

Compliance Operator는 원시 결과를 생성하여 영구 볼륨에 저장합니다. 이러한 결과는 자산 보고 형식(ARF)으로 되어 있습니다.

`ComplianceSuite` 오브젝트를 살펴봅니다.

```shell-session
$ oc get compliancesuites nist-moderate-modified \
-o json -n openshift-compliance | jq '.status.scanStatuses[].resultsStorage'
```

```plaintext
{
     "name": "ocp4-moderate",
     "namespace": "openshift-compliance"
}
{
     "name": "nist-moderate-modified-master",
     "namespace": "openshift-compliance"
}
{
     "name": "nist-moderate-modified-worker",
     "namespace": "openshift-compliance"
}
```

원시 결과에 액세스할 수 있는 영구 볼륨 클레임이 표시됩니다.

결과 중 하나의 이름과 네임스페이스를 사용하여 원시 데이터 위치를 확인합니다.

```shell-session
$ oc get pvc -n openshift-compliance rhcos4-moderate-worker
```

```shell-session
NAME                    STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
rhcos4-moderate-worker   Bound  pvc-548f6cfe-164b-42fe-ba13-a07cfbc77f3a   1Gi      RWO         gp2         92m
```

볼륨을 마운트하는 Pod를 생성하고 결과를 복사하여 원시 결과를 가져옵니다.

```shell-session
$ oc create -n openshift-compliance -f pod.yaml
```

```yaml
apiVersion: "v1"
kind: Pod
metadata:
  name: pv-extract
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: pv-extract-pod
      image: registry.access.redhat.com/ubi9/ubi
      command: ["sleep", "3000"]
      volumeMounts:
      - mountPath: "/workers-scan-results"
        name: workers-scan-vol
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
  volumes:
    - name: workers-scan-vol
      persistentVolumeClaim:
        claimName: rhcos4-moderate-worker
```

Pod가 실행되면 결과를 다운로드합니다.

```shell-session
$ oc cp pv-extract:/workers-scan-results -n openshift-compliance .
```

중요

영구 볼륨을 마운트하는 Pod를 생성하면 클레임이 `Bound` 로 유지됩니다. 사용 중인 볼륨의 스토리지 클래스에 `ReadWriteOnce` 로 설정된 권한이 있는 경우 한 번에 하나의 Pod에서만 볼륨을 마운트할 수 있습니다. 완료 시 Pod를 삭제해야 합니다. 그러지 않으면 Operator에서 Pod를 예약하고 이 위치에 결과를 계속 저장할 수 없습니다.

추출이 완료되면 Pod를 삭제할 수 있습니다.

```shell-session
$ oc delete pod pv-extract -n openshift-compliance
```

#### 5.6.5. Compliance Operator 결과 및 수정 관리

각 `ComplianceCheckResult` 는 하나의 규정 준수 규칙 검사 결과를 나타냅니다. 규칙을 자동으로 수정할 수 있는 경우 `ComplianceCheckResult` 가 소유한 동일한 이름의 `ComplianceRemediation` 오브젝트가 생성됩니다. 요청하지 않는 경우 수정은 자동으로 적용되지 않으므로 OpenShift Container Platform 관리자는 수정을 통해 수행되는 작업을 검토하고 확인한 후에만 수정을 적용할 수 있습니다.

중요

FIPS(Federal Information Processing Standards) 준수를 완전히 해결하려면 클러스터에 FIPS 모드를 활성화해야 합니다. FIPS 모드를 활성화하려면 FIPS 모드에서 작동하도록 구성된 RHEL(Red Hat Enterprise Linux) 컴퓨터에서 설치 프로그램을 실행해야 합니다. RHEL에서 FIPS 모드 구성에 대한 자세한 내용은 FIPS 모드에서 시스템 설치를 참조하십시오.

FIPS 모드는 다음 아키텍처에서 지원됩니다.

`x86_64`

`ppc64le`

`s390x`

#### 5.6.5.1. 규정 준수 검사 결과에 대한 필터

기본적으로 `ComplianceCheckResult` 오브젝트에는 검사를 쿼리하고 결과가 생성된 후 다음 단계를 결정할 수 있는 몇 가지 유용한 레이블이 지정됩니다.

특정 제품군에 속하는 검사를 나열합니다.

```shell-session
$ oc get -n openshift-compliance compliancecheckresults \
  -l compliance.openshift.io/suite=workers-compliancesuite
```

특정 검사에 속하는 검사를 나열합니다.

```shell-session
$ oc get -n openshift-compliance compliancecheckresults \
-l compliance.openshift.io/scan=workers-scan
```

일부 `ComplianceCheckResult` 오브젝트가 `ComplianceRemediation` 오브젝트를 생성하는 것은 아닙니다. 자동으로 업데이트를 적용할 수 있는 `ComplianceCheckResult` 오브젝트만 해당합니다. `ComplianceCheckResult` 오브젝트에 `compliance.openshift.io/automated-remediation` 레이블이 지정된 경우 관련된 업데이트 적용이 있습니다. 업데이트 적용의 이름은 검사 이름과 동일합니다.

자동으로 업데이트를 적용할 수 있는 모든 실패한 검사를 나열합니다.

```shell-session
$ oc get -n openshift-compliance compliancecheckresults \
-l 'compliance.openshift.io/check-status=FAIL,compliance.openshift.io/automated-remediation'
```

심각도별로 정렬된 실패한 모든 검사를 나열합니다.

```shell-session
$ oc get compliancecheckresults -n openshift-compliance \
-l 'compliance.openshift.io/check-status=FAIL,compliance.openshift.io/check-severity=high'
```

```shell-session
NAME                                                           STATUS   SEVERITY
nist-moderate-modified-master-configure-crypto-policy          FAIL     high
nist-moderate-modified-master-coreos-pti-kernel-argument       FAIL     high
nist-moderate-modified-master-disable-ctrlaltdel-burstaction   FAIL     high
nist-moderate-modified-master-disable-ctrlaltdel-reboot        FAIL     high
nist-moderate-modified-master-enable-fips-mode                 FAIL     high
nist-moderate-modified-master-no-empty-passwords               FAIL     high
nist-moderate-modified-master-selinux-state                    FAIL     high
nist-moderate-modified-worker-configure-crypto-policy          FAIL     high
nist-moderate-modified-worker-coreos-pti-kernel-argument       FAIL     high
nist-moderate-modified-worker-disable-ctrlaltdel-burstaction   FAIL     high
nist-moderate-modified-worker-disable-ctrlaltdel-reboot        FAIL     high
nist-moderate-modified-worker-enable-fips-mode                 FAIL     high
nist-moderate-modified-worker-no-empty-passwords               FAIL     high
nist-moderate-modified-worker-selinux-state                    FAIL     high
ocp4-moderate-configure-network-policies-namespaces            FAIL     high
ocp4-moderate-fips-mode-enabled-on-all-nodes                   FAIL     high
```

수동으로 업데이트를 적용해야 하는 모든 실패한 검사를 나열합니다.

```shell-session
$ oc get -n openshift-compliance compliancecheckresults \
-l 'compliance.openshift.io/check-status=FAIL,!compliance.openshift.io/automated-remediation'
```

수동 업데이트 적용 단계는 일반적으로 `ComplianceCheckResult` 오브젝트의 `description` 속성에 저장됩니다.

| ComplianceCheckResult Status | 설명 |
| --- | --- |
| PASS | 규정 준수 검사가 완료된 후 통과되었습니다. |
| FAIL | 규정 준수 검사가 완료되도록 실행되었으며 실패했습니다. |
| INFO | 컴플라이언스 검사가 완료되기 위해 실행되었으며 오류로 간주할 만큼 심각하지 않은 것을 발견했습니다. |
| MANUAL | 규정 준수 확인에는 성공 또는 실패를 자동으로 평가할 방법이 없으며 수동으로 확인해야 합니다. |
| 일관성 없음 | 규정 준수 검사에서는 일반적으로 클러스터 노드와 다른 소스와 다른 결과를 보고합니다. |
| 오류 | 컴플라이언스 검사가 실행되었지만 제대로 완료되지 못했습니다. |
| NOT-APPLICABLE | 규정 준수 검사가 적용되지 않거나 선택되지 않았기 때문에 실행되지 않았습니다. |

#### 5.6.5.2. 수정 검토

수정이 포함된 `ComplianceRemediation` 오브젝트 및 `ComplianceCheckResult` 오브젝트를 모두 검토합니다. `ComplianceCheckResult` 오브젝트에는 검사에서 수행하는 작업과 방지를 위한 강화 작업에 관해 사람이 있을 수 있는 설명과 심각도 및 관련 보안 제어와 같은 기타 `메타데이터` 가 포함되어 있습니다. `ComplianceRemediation` 오브젝트는 `ComplianceCheckResult` 에서 설명하는 문제를 해결하는 방법을 나타냅니다. 첫 번째 검사 후 `MissingDependencies` 상태로 수정을 확인합니다.

다음은 `sysctl-net-ipv4-conf-all-accept-redirects` 라는 검사와 수정의 예입니다. 이 예는 `spec` 및 `status` 만 표시하고 `metadata` 는 생략하도록 수정되었습니다.

```yaml
spec:
  apply: false
  current:
  object:
    apiVersion: machineconfiguration.openshift.io/v1
    kind: MachineConfig
    spec:
      config:
        ignition:
          version: 3.2.0
        storage:
          files:
            - path: /etc/sysctl.d/75-sysctl_net_ipv4_conf_all_accept_redirects.conf
              mode: 0644
              contents:
                source: data:,net.ipv4.conf.all.accept_redirects%3D0
  outdated: {}
status:
  applicationState: NotApplied
```

수정 페이로드는 `spec.current` 특성에 저장됩니다. 페이로드는 임의의 Kubernetes 오브젝트일 수 있지만 이 수정은 노드 검사를 통해 생성되었기 때문에 위 예의 수정 페이로드는 `MachineConfig` 오브젝트입니다. 플랫폼 검사의 경우 수정 페이로드는 종종 다른 종류의 오브젝트(예: `ConfigMap` 또는 `Secret` 오브젝트)에 해당하지만 일반적으로 이러한 수정을 적용하는 것은 관리자의 몫입니다. 그러지 않으면 일반 Kubernetes 오브젝트를 조작하기 위해 Compliance Operator에 매우 광범위한 권한이 있어야 하기 때문입니다. 플랫폼 검사를 수정하는 예는 본문 뒷부분에 있습니다.

수정 적용 시 수행되는 작업을 정확히 확인하기 위해 `MachineConfig` 오브젝트 콘텐츠에서는 구성에 Ignition 오브젝트를 사용합니다. 형식에 대한 자세한 내용은 Ignition 사양 을 참조하십시오. 이 예에서 `spec.config.storage.files[0].path` 특성은 이 수정(`/etc/sysctl.d/75-sysctl_net_ipv4_conf_all_accept_redirects.conf`)으로 생성되는 파일을 지정하고, `spec.config.storage.files[0].contents.source` 특성은 해당 파일의 콘텐츠를 지정합니다.

참고

파일 내용은 URL로 인코딩됩니다.

콘텐츠를 보려면 다음 Python 스크립트를 사용합니다.

```shell-session
$ echo "net.ipv4.conf.all.accept_redirects%3D0" | python3 -c "import sys, urllib.parse; print(urllib.parse.unquote(''.join(sys.stdin.readlines())))"
```

```shell-session
net.ipv4.conf.all.accept_redirects=0
```

중요

Compliance Operator는 수정 사이에 발생할 수 있는 종속성 문제를 자동으로 해결하지 않습니다. 정확한 결과를 보장하기 위해 수정을 적용한 후 다시 스캔해야 합니다.

#### 5.6.5.3. 사용자 지정 머신 구성 풀을 사용할 때 수정 적용

사용자 지정 `MachineConfigPool` 을 생성할 때 `KubeletConfig` 에 있는 `machineConfigPoolSelector` 가 `MachineConfigPool` 과 함께 레이블을 일치시킬 수 있도록 `MachineConfigPool` 에 레이블을 추가합니다.

중요

Compliance Operator가 수정 적용을 완료한 후 `MachineConfigPool` 오브젝트가 예기치 않게 일시 중지 해제될 수 있으므로 `KubeletConfig` 파일에 `protectKernelDefaults: false` 를 설정하지 마십시오.

프로세스

노드를 나열합니다.

```shell-session
$ oc get nodes -n openshift-compliance
```

```shell-session
NAME                                       STATUS  ROLES  AGE    VERSION
ip-10-0-128-92.us-east-2.compute.internal  Ready   master 5h21m  v1.33.4
ip-10-0-158-32.us-east-2.compute.internal  Ready   worker 5h17m  v1.33.4
ip-10-0-166-81.us-east-2.compute.internal  Ready   worker 5h17m  v1.33.4
ip-10-0-171-170.us-east-2.compute.internal Ready   master 5h21m  v1.33.4
ip-10-0-197-35.us-east-2.compute.internal  Ready   master 5h22m  v1.33.4
```

노드에 레이블을 추가합니다.

```shell-session
$ oc -n openshift-compliance \
label node ip-10-0-166-81.us-east-2.compute.internal \
node-role.kubernetes.io/<machine_config_pool_name>=
```

```shell-session
node/ip-10-0-166-81.us-east-2.compute.internal labeled
```

사용자 지정 `MachineConfigPool` CR을 생성합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  name: <machine_config_pool_name>
  labels:
    pools.operator.machineconfiguration.openshift.io/<machine_config_pool_name>: ''
spec:
  machineConfigSelector:
  matchExpressions:
  - {key: machineconfiguration.openshift.io/role, operator: In, values: [worker,<machine_config_pool_name>]}
  nodeSelector:
  matchLabels:
    node-role.kubernetes.io/<machine_config_pool_name>: ""
```

1. `labels` 필드는 MCP(Machine config pool)에 추가할 레이블 이름을 정의합니다.

MCP가 성공적으로 생성되었는지 확인합니다.

```shell-session
$ oc get mcp -w
```

#### 5.6.5.4. 기본 구성 값에 대해 KubeletConfig 규칙 평가

OpenShift Container Platform 인프라에는 런타임에 불완전한 구성 파일이 포함될 수 있으며 노드는 누락된 구성 옵션에 대한 기본 구성 값을 가정합니다. 일부 구성 옵션은 명령줄 인수로 전달할 수 있습니다. 결과적으로 Compliance Operator는 규칙 검사에 사용되는 옵션이 누락될 수 있으므로 노드의 구성 파일이 완료되었는지 확인할 수 없습니다.

기본 구성 값이 검사를 전달하는 잘못된 결과를 방지하기 위해 Compliance Operator는 Node/Proxy API를 사용하여 노드 풀의 각 노드에 대한 구성을 가져온 다음 노드 풀의 노드 간에 일관된 모든 구성 옵션이 해당 노드 풀 내의 모든 노드에 대한 구성을 나타내는 파일에 저장됩니다. 이렇게 하면 검사 결과의 정확성이 높아집니다.

기본 `마스터` 및 `작업자` 노드 풀 구성과 함께 이 기능을 사용하려면 추가 구성 변경이 필요하지 않습니다.

#### 5.6.5.5. 사용자 정의 노드 풀 스캔

Compliance Operator는 각 노드 풀 구성의 사본을 유지 관리하지 않습니다. Compliance Operator는 단일 노드 풀 내의 모든 노드에 대한 일관된 구성 옵션을 구성 파일의 하나의 사본으로 집계합니다. 그런 다음 Compliance Operator는 특정 노드 풀의 구성 파일을 사용하여 해당 풀 내의 노드에 대한 규칙을 평가합니다.

프로세스

`ScanSettingBinding` CR에 저장될 `ScanSetting` 오브젝트에 `예제` 역할을 추가합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  name: default
  namespace: openshift-compliance
rawResultStorage:
  rotation: 3
  size: 1Gi
roles:
- worker
- master
- example
scanTolerations:
- effect: NoSchedule
  key: node-role.kubernetes.io/master
  operator: Exists
schedule: '0 1 * * *'
```

`ScanSettingBinding` CR을 사용하는 검사를 생성합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSettingBinding
metadata:
  name: cis
  namespace: openshift-compliance
profiles:
- apiGroup: compliance.openshift.io/v1alpha1
  kind: Profile
  name: ocp4-cis
- apiGroup: compliance.openshift.io/v1alpha1
  kind: Profile
  name: ocp4-cis-node
settingsRef:
  apiGroup: compliance.openshift.io/v1alpha1
  kind: ScanSetting
  name: default
```

검증

Platform KubeletConfig 규칙은 `Node/Proxy` 오브젝트를 통해 확인합니다. 다음 명령을 실행하여 해당 규칙을 찾을 수 있습니다.

```shell-session
$ oc get rules -o json | jq '.items[] | select(.checkType == "Platform") | select(.metadata.name | contains("ocp4-kubelet-")) | .metadata.name'
```

#### 5.6.5.6. KubeletConfig 하위 풀 수정

`KubeletConfig` 수정 레이블은 `MachineConfigPool` 하위 풀에 적용할 수 있습니다.

프로세스

하위 풀 `MachineConfigPool` CR에 라벨을 추가합니다.

```shell-session
$ oc label mcp <sub-pool-name> pools.operator.machineconfiguration.openshift.io/<sub-pool-name>=
```

#### 5.6.5.7. 수정 적용

부울 특성 `spec.apply` 는 Compliance Operator에서 수정을 적용해야 하는지를 제어합니다. 특성을 `true` 로 설정하면 수정을 적용할 수 있습니다.

```shell-session
$ oc -n openshift-compliance \
patch complianceremediations/<scan-name>-sysctl-net-ipv4-conf-all-accept-redirects \
--patch '{"spec":{"apply":true}}' --type=merge
```

Compliance Operator에서 적용된 수정을 처리하면 `status.ApplicationState` 특성이 Applied 로 변경되거나 잘못된 경우 Error 로 변경됩니다. 시스템 구성 수정이 적용되면 적용된 기타 모든 수정과 함께 해당 수정이 `75-$scan-name-$suite-name` 이라는 `MachineConfig` 오브젝트로 렌더링됩니다. 이후 Machine Config Operator에서 `MachineConfig` 오브젝트를 렌더링하고 마지막으로 각 노드에서 실행되는 머신 제어 데몬 인스턴스에서 머신 구성 풀의 모든 노드에 이 오브젝트를 적용합니다.

Machine Config Operator에서 새 `MachineConfig` 오브젝트를 풀의 노드에 적용하면 풀에 속하는 모든 노드가 재부팅됩니다. 이러한 방법은 복합적인 `75-$scan-name-$suite-name`

`MachineConfig` 오브젝트를 각각 다시 렌더링하는 수정을 여러 번 적용할 때 불편할 수 있습니다. 수정을 즉시 적용하지 않으려면 `MachineConfigPool` 오브젝트의 `.spec.paused` 특성을 `true` 로 설정하여 머신 구성 풀을 일시 중지하면 됩니다.

Compliance Operator는 수정을 자동으로 적용할 수 있습니다. `ScanSetting` 최상위 오브젝트에 `autoApplyRemediations: true` 를 설정합니다.

주의

수정 사항 자동 적용은 신중하게 고려해야 합니다.

중요

Compliance Operator는 수정 사이에 발생할 수 있는 종속성 문제를 자동으로 해결하지 않습니다. 정확한 결과를 보장하기 위해 수정을 적용한 후 다시 스캔해야 합니다.

#### 5.6.5.8. 플랫폼 점검 수동 수정

플랫폼 검사에 대한 점검은 일반적으로 다음 두 가지 이유로 관리자가 수동으로 수정해야 합니다.

설정해야 하는 값을 자동으로 결정할 수 없는 경우가 있습니다. 검사 중 하나를 통해 허용된 레지스트리 목록을 제공해야 하지만 스캐너에서는 조직이 허용하려는 레지스트리를 알 수 없습니다.

다양한 점검에서 여러 API 오브젝트를 수정하므로 클러스터의 오브젝트를 수정하려면 `root` 또는 슈퍼 유저 액세스 권한을 가져오기 위해 자동 수정이 필요합니다. 이 방법은 바람직하지 않습니다.

프로세스

아래 예제에서는 `ocp4-ocp-allowed-registries-for-import` 규칙을 사용하며 기본 OpenShift Container Platform 설치에서 실패합니다. 규칙을 검사합니다. 이 규칙은 `allowedRegistriesForImport` 특성을 설정하여 사용자가 이미지를 가져올 수 있는 레지스트리를 제한합니다. 규칙의 warning 특성에는 점검된 API 오브젝트도 표시되므로 이를 수정하고 문제를 해결할 수 있습니다.

```shell
oc get rule.compliance/ocp4-ocp-allowed-registries-for-import -oyaml
```

```shell-session
$ oc edit image.config.openshift.io/cluster
```

```yaml
apiVersion: config.openshift.io/v1
kind: Image
metadata:
  annotations:
    release.openshift.io/create-only: "true"
  creationTimestamp: "2020-09-10T10:12:54Z"
  generation: 2
  name: cluster
  resourceVersion: "363096"
  selfLink: /apis/config.openshift.io/v1/images/cluster
  uid: 2dcb614e-2f8a-4a23-ba9a-8e33cd0ff77e
spec:
  allowedRegistriesForImport:
  - domainName: registry.redhat.io
status:
  externalRegistryHostnames:
  - default-route-openshift-image-registry.apps.user-cluster-09-10-12-07.devcluster.openshift.com
  internalRegistryHostname: image-registry.openshift-image-registry.svc:5000
```

검사를 다시 실행합니다.

```shell-session
$ oc -n openshift-compliance \
annotate compliancescans/rhcos4-e8-worker compliance.openshift.io/rescan=
```

#### 5.6.5.9. 수정 업데이트

새 버전의 규정 준수 콘텐츠를 사용하는 경우 이전 버전과 다른 새 버전의 수정을 제공할 수 있습니다. Compliance Operator는 이전 버전의 수정을 적용한 상태로 유지됩니다. OpenShift Container Platform 관리자에게는 검토하고 적용할 새 버전에 대한 알림이 제공됩니다. 이전에 적용되었지만 업데이트된 ComplianceRemediation 오브젝트는 상태가 Outdated 로 변경됩니다. 오래된 오브젝트는 쉽게 검색할 수 있도록 레이블이 지정됩니다.

이전에 적용된 수정 내용은 `ComplianceRemediation` 오브젝트의 `spec.outdated` 특성에 저장되고 새로 업데이트된 내용은 `spec.current` 특성에 저장됩니다. 콘텐츠가 최신 버전으로 업데이트되면 관리자는 수정을 검토해야 합니다. `spec.outdated` 특성이 존재하는 동안에는 결과 `MachineConfig` 오브젝트를 렌더링하는 데 사용됩니다. `spec.outdated` 특성이 제거되면 Compliance Operator에서 결과 `MachineConfig` 오브젝트를 다시 렌더링하고 이로 인해 Operator에서 구성을 노드로 푸시합니다.

프로세스

오래된 수정을 검색합니다.

```shell-session
$ oc -n openshift-compliance get complianceremediations \
-l complianceoperator.openshift.io/outdated-remediation=
```

```shell-session
NAME                              STATE
workers-scan-no-empty-passwords   Outdated
```

현재 적용된 수정은 `Outdated` 특성에 저장되고 적용되지 않은 새 수정은 `Current` 특성에 저장됩니다. 새 버전에 만족한다면 `Outdated` 필드를 제거하십시오. 업데이트된 콘텐츠를 유지하려면 `Current` 및 `Outdated` 특성을 제거하십시오.

최신 버전의 수정을 적용합니다.

```shell-session
$ oc -n openshift-compliance patch complianceremediations workers-scan-no-empty-passwords \
--type json -p '[{"op":"remove", "path":/spec/outdated}]'
```

수정 상태가 `Outdated` 에서 `Applied` 로 전환됩니다.

```shell-session
$ oc get -n openshift-compliance complianceremediations workers-scan-no-empty-passwords
```

```shell-session
NAME                              STATE
workers-scan-no-empty-passwords   Applied
```

노드에 최신 수정 버전이 적용되고 노드가 재부팅됩니다.

중요

Compliance Operator는 수정 사이에 발생할 수 있는 종속성 문제를 자동으로 해결하지 않습니다. 정확한 결과를 보장하기 위해 수정을 적용한 후 다시 스캔해야 합니다.

#### 5.6.5.10. 수정 적용 취소

이전에 적용한 수정을 적용 취소해야 할 수 있습니다.

프로세스

`apply` 플래그를 `false` 로 설정합니다.

```shell-session
$ oc -n openshift-compliance \
patch complianceremediations/rhcos4-moderate-worker-sysctl-net-ipv4-conf-all-accept-redirects \
--patch '{"spec":{"apply":false}}' --type=merge
```

수정 상태가 `NotApplied` 로 변경되고 복합 `MachineConfig` 오브젝트가 수정을 포함하지 않도록 다시 렌더링됩니다.

중요

수정으로 영향을 받는 모든 노드가 재부팅됩니다.

중요

Compliance Operator는 수정 사이에 발생할 수 있는 종속성 문제를 자동으로 해결하지 않습니다. 정확한 결과를 보장하기 위해 수정을 적용한 후 다시 스캔해야 합니다.

#### 5.6.5.11. KubeletConfig 수정 제거

`KubeletConfig` 수정은 노드 수준 프로필에 포함되어 있습니다. KubeletConfig 수정을 제거하려면 `KubeletConfig` 오브젝트에서 수동으로 제거해야 합니다. 이 예에서는 `one-rule-tp-node-kubelet-eviction-thresholds-set-hard-imagefs-available` 수정의 규정 준수 검사를 제거하는 방법을 보여줍니다.

프로세스

`one-rule-tp-node-master-kubelet-eviction-thresholds-set-hard-imagefs-available` 수정의 `scan-name` 및 컴플라이언스 검사를 찾습니다.

```shell-session
$ oc -n openshift-compliance get remediation \ one-rule-tp-node-master-kubelet-eviction-thresholds-set-hard-imagefs-available -o yaml
```

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ComplianceRemediation
metadata:
  annotations:
    compliance.openshift.io/xccdf-value-used: var-kubelet-evictionhard-imagefs-available
  creationTimestamp: "2022-01-05T19:52:27Z"
  generation: 1
  labels:
    compliance.openshift.io/scan-name: one-rule-tp-node-master
    compliance.openshift.io/suite: one-rule-ssb-node
  name: one-rule-tp-node-master-kubelet-eviction-thresholds-set-hard-imagefs-available
  namespace: openshift-compliance
  ownerReferences:
  - apiVersion: compliance.openshift.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: ComplianceCheckResult
    name: one-rule-tp-node-master-kubelet-eviction-thresholds-set-hard-imagefs-available
    uid: fe8e1577-9060-4c59-95b2-3e2c51709adc
  resourceVersion: "84820"
  uid: 5339d21a-24d7-40cb-84d2-7a2ebb015355
spec:
  apply: true
  current:
    object:
      apiVersion: machineconfiguration.openshift.io/v1
      kind: KubeletConfig
      spec:
        kubeletConfig:
          evictionHard:
            imagefs.available: 10%
  outdated: {}
  type: Configuration
status:
  applicationState: Applied
```

1. 수정의 검사 이름입니다.

2. `KubeletConfig` 오브젝트에 추가된 수정입니다.

참고

수정을 통해 `evictionHard` kubelet 구성을 호출하는 경우 모든 `evictionHard` 매개변수: `memory.available`, `nodefs.available`, `nodefs.inodesFree`, `imagefs.available`, `imagefs.inodesFree` 를 지정해야 합니다. 모든 매개변수를 지정하지 않으면 지정된 매개변수만 적용되고 수정이 제대로 작동하지 않습니다.

수정을 제거합니다.

수정 오브젝트에 대해 `apply` to false로 설정합니다.

```shell-session
$ oc -n openshift-compliance patch \
complianceremediations/one-rule-tp-node-master-kubelet-eviction-thresholds-set-hard-imagefs-available \
-p '{"spec":{"apply":false}}' --type=merge
```

`scan-name` 을 사용하여 수정 사항이 적용된 `KubeletConfig` 오브젝트를 찾습니다.

```shell-session
$ oc -n openshift-compliance get kubeletconfig \
--selector compliance.openshift.io/scan-name=one-rule-tp-node-master
```

```shell-session
NAME                                 AGE
compliance-operator-kubelet-master   2m34s
```

`KubeletConfig` 오브젝트에서 수동으로 수정 `imagefs.available: 10%` 를 제거합니다.

```shell-session
$ oc edit -n openshift-compliance KubeletConfig compliance-operator-kubelet-master
```

중요

수정으로 영향을 받는 모든 노드가 재부팅됩니다.

참고

또한 수정을 자동으로 적용하는 맞춤형 프로필의 예약된 검사에서 규칙을 제외해야 합니다. 그러지 않으면 다음 스케줄링된 검사 중에 수정이 다시 적용됩니다.

#### 5.6.5.12. Inconsistent ComplianceScan

`ScanSetting` 오브젝트는 `ScanSetting` 또는 `ScanSettingBinding` 오브젝트에서 생성한 규정 준수 검사에서 검사할 노드 역할을 나열합니다. 각 노드 역할은 일반적으로 머신 구성 풀에 매핑됩니다.

중요

머신 구성 풀의 모든 머신이 동일하고 풀에 있는 노드의 모든 검사 결과가 동일해야 합니다.

일부 결과가 다른 결과와 다른 경우 Compliance Operator는 일부 노드에서 `INCONSISTENT` 로 보고하는 `ComplianceCheckResult` 오브젝트에 플래그를 지정합니다. 또한 모든 `ComplianceCheckResult` 오브젝트에는 `compliance.openshift.io/inconsistent-check` 레이블이 지정됩니다.

풀의 머신 수가 상당히 많을 수 있기 때문에 Compliance Operator는 가장 일반적인 상태를 찾고 일반적인 상태와 다른 노드를 나열하려고 합니다. 가장 일반적인 상태는 `compliance.openshift.io/most-common-status` 주석에 저장되고 주석 `compliance.openshift.io/inconsistent-source` 에는 가장 일반적인 상태와 다른 점검 상태의 `hostname:status` 쌍이 포함됩니다. 일반적인 상태를 찾을 수 없는 경우 모든 `hostname:status` 쌍이 `compliance.openshift.io/inconsistent-source annotation` 에 나열됩니다.

가능한 경우 클러스터가 규정 준수 상태에 통합될 수 있도록 수정이 계속 생성됩니다. 그러나 이러한 통합이 항상 가능한 것은 아니며 노드 간 차이를 수동으로 수정해야 합니다. `compliance.openshift.io/rescan=` 옵션으로 검사에 주석을 달아 일관된 결과를 가져오도록 규정 준수 검사를 다시 실행해야 합니다.

```shell-session
$ oc -n openshift-compliance \
annotate compliancescans/rhcos4-e8-worker compliance.openshift.io/rescan=
```

#### 5.6.5.13. 추가 리소스

노드 수정.

#### 5.6.6. 고급 Compliance Operator 작업 수행

Compliance Operator에는 디버깅 또는 기존 툴과의 통합에 필요한 고급 사용자용 옵션이 포함되어 있습니다.

#### 5.6.6.1. ComplianceSuite 및 ComplianceScan 오브젝트 직접 사용

사용자가 `ScanSetting` 및 `ScanSettingBinding` 오브젝트를 활용하여 모음과 검사를 정의하는 것이 바람직하지만 `ComplianceSuite` 오브젝트를 직접 정의하는 유효한 사용 사례가 있습니다.

검사할 단일 규칙만 지정합니다. 그러지 않으면 디버그 모드가 매우 상세하게 표시되는 경향이 있으므로 이 방법은 OpenSCAP 스캐너의 상세 수준을 높이는 `debug: true` 특성과 함께 디버깅하는 데 유용할 수 있습니다. 테스트를 하나의 규칙으로 제한하면 디버그 정보의 양을 줄이는 데 도움이 됩니다.

사용자 정의 nodeSelector를 제공합니다. 수정을 적용하려면 nodeSelector가 풀과 일치해야 합니다.

맞춤 파일을 사용하여 맞춤형 구성 맵을 검사합니다.

번들의 프로파일을 구문 분석하는 오버헤드가 필요하지 않은 경우의 테스트 또는 개발에 해당합니다.

다음 예제에서는 단일 규칙으로만 작업자 머신을 검사하는 `ComplianceSuite` 를 보여줍니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ComplianceSuite
metadata:
  name: workers-compliancesuite
spec:
  scans:
    - name: workers-scan
      profile: xccdf_org.ssgproject.content_profile_moderate
      content: ssg-rhcos4-ds.xml
      contentImage: registry.redhat.io/compliance/openshift-compliance-content-rhel8@sha256:45dc...
      debug: true
      rule: xccdf_org.ssgproject.content_rule_no_direct_root_logins
      nodeSelector:
      node-role.kubernetes.io/worker: ""
```

위에서 언급한 `ComplianceSuite` 오브젝트 및 `ComplianceScan` 오브젝트는 여러 특성을 OpenSCAP에서 예상하는 형식으로 지정합니다.

프로필, 콘텐츠 또는 규칙 값을 찾으려면 `ScanSetting` 및 `ScanSettingBinding` 에서 유사한 모음을 생성하여 시작하거나 규칙 또는 프로필과 같이 `ProfileBundle` 오브젝트에서 구문 분석한 오브젝트를 검사하면 됩니다. 이러한 오브젝트에는 `ComplianceSuite` 에서 참조하는 데 사용할 수 있는 `xccdf_org` 식별자가 포함되어 있습니다.

#### 5.6.6.2. ScanSetting 검사의 PriorityClass 설정

대규모 환경에서는 기본 `PriorityClass` 오브젝트가 너무 낮아 Pod가 시간 내에 검사를 실행할 수 있도록 할 수 있습니다. 컴플라이언스를 유지 관리하거나 자동화된 검사를 보장해야 하는 클러스터의 경우 Compliance Operator가 리소스 제한 상황에서 항상 우선 순위를 지정하도록 `PriorityClass` 변수를 설정하는 것이 좋습니다.

사전 요구 사항

선택 사항: `PriorityClass` 오브젝트를 생성했습니다. 자세한 내용은 추가 리소스 의 "우선 순위 및 선점 구성"을 참조하십시오.

프로세스

`PriorityClass` 변수를 설정합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
strictNodeScan: true
metadata:
  name: default
  namespace: openshift-compliance
priorityClass: compliance-high-priority
kind: ScanSetting
showNotApplicable: false
rawResultStorage:
  nodeSelector:
    node-role.kubernetes.io/master: ''
  pvAccessModes:
    - ReadWriteOnce
  rotation: 3
  size: 1Gi
  tolerations:
    - effect: NoSchedule
      key: node-role.kubernetes.io/master
      operator: Exists
    - effect: NoExecute
      key: node.kubernetes.io/not-ready
      operator: Exists
      tolerationSeconds: 300
    - effect: NoExecute
      key: node.kubernetes.io/unreachable
      operator: Exists
      tolerationSeconds: 300
    - effect: NoSchedule
      key: node.kubernetes.io/memory-pressure
      operator: Exists
schedule: 0 1 * * *
roles:
  - master
  - worker
scanTolerations:
  - operator: Exists
```

1. `ScanSetting` 에서 참조하는 `PriorityClass` 를 찾을 수 없는 경우 Operator는 `PriorityClass` 를 비워 두고 경고를 발행하며 `PriorityClass` 없이 계속 스케줄링 검사를 수행합니다.

추가 리소스

우선순위 및 선점 구성

#### 5.6.6.3. 원시 맞춤형 프로필 사용

`TailoredProfile` CR에서는 가장 일반적인 맞춤 작업을 수행할 수 있지만 XCCDF 표준을 사용하면 OpenSCAP 프로필 맞춤 시 유연성이 훨씬 더 향상됩니다. 또한 조직에서 이전에 OpenScap을 사용한 적이 있는 경우 기존 XCCDF 맞춤 파일이 있을 수 있으며 이 파일을 다시 사용할 수 있습니다.

`ComplianceSuite` 오브젝트에는 사용자 정의 맞춤 파일을 가리킬 수 있는 선택적 `TailoringConfigMap` 특성이 포함되어 있습니다. `TailoringConfigMap` 특성 값은 구성 맵의 이름으로, 이 맵에는 `tailoring.xml` 이라는 키가 포함되어야 하며 이 키의 값은 맞춤 콘텐츠입니다.

프로세스

파일에서 `ConfigMap` 오브젝트를 만듭니다.

```shell-session
$ oc -n openshift-compliance \
create configmap nist-moderate-modified \
--from-file=tailoring.xml=/path/to/the/tailoringFile.xml
```

모음에 속하는 검사의 맞춤 파일을 참조합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ComplianceSuite
metadata:
  name: workers-compliancesuite
spec:
  debug: true
  scans:
    - name: workers-scan
      profile: xccdf_org.ssgproject.content_profile_moderate
      content: ssg-rhcos4-ds.xml
      contentImage: registry.redhat.io/compliance/openshift-compliance-content-rhel8@sha256:45dc...
      debug: true
  tailoringConfigMap:
      name: nist-moderate-modified
  nodeSelector:
    node-role.kubernetes.io/worker: ""
```

#### 5.6.6.4. 재검사 수행

일반적으로 매주 월요일 또는 매일 등 정의된 일정에 따라 검사를 다시 실행하려고 할 것입니다. 노드 문제를 해결한 후 다시 한 번 검사를 실행하는 것도 유용할 수 있습니다. 단일 검사를 수행하려면 `compliance.openshift.io/rescan=` 옵션을 사용하여 검사에 주석을 답니다.

```shell-session
$ oc -n openshift-compliance \
annotate compliancescans/rhcos4-e8-worker compliance.openshift.io/rescan=
```

rescan은 `rhcos-moderate` 프로필에 대해 4개의 추가 `mc` 를 생성합니다.

```shell-session
$ oc get mc
```

```shell-session
75-worker-scan-chronyd-or-ntpd-specify-remote-server
75-worker-scan-configure-usbguard-auditbackend
75-worker-scan-service-usbguard-enabled
75-worker-scan-usbguard-allow-hid-and-hub
```

중요

검사 설정 `default-auto-apply` 레이블이 적용되면 수정 사항이 자동으로 적용되고 오래된 수정 사항이 자동으로 업데이트됩니다. 종속 항목 또는 오래된 수정 사항으로 인해 적용되지 않은 업데이트 적용이 있는 경우 다시 검사하면 업데이트가 적용되고 재부팅이 트리거될 수 있습니다. `MachineConfig` 오브젝트를 사용하는 업데이트 적용만 재부팅을 트리거합니다. 적용할 업데이트 또는 종속 항목이 없는 경우 재부팅이 수행되지 않습니다.

#### 5.6.6.5. 결과에 대한 사용자 정의 스토리지 크기 설정

`ComplianceCheckResult` 와 같은 사용자 정의 리소스는 검사한 모든 노드에서 집계한 한 번의 점검 결과를 나타내지만 스캐너에서 생성한 원시 결과를 검토하는 것이 유용할 수 있습니다. 원시 결과는 ARF 형식으로 생성되며 크기가 클 수 있습니다(노드당 수십 메가바이트). 따라서 `etcd` 키-값 저장소에서 지원하는 Kubernetes 리소스에 저장하는 것은 비현실적입니다. 대신 검사할 때마다 기본 크기가 1GB인 영구 볼륨(PV)이 생성됩니다. 환경에 따라 적절하게 PV 크기를 늘릴 수 있습니다. 크기를 늘리려면 `ScanSetting` 및 `ComplianceScan` 리소스 모두에 노출되는 `rawResultStorage.size` 특성을 사용하면 됩니다.

관련 매개변수는 `rawResultStorage.rotation` 으로, 이전 검사가 되풀이되기 전에 PV에 유지되는 검사 수를 조절합니다. 기본값은 3이며 되풀이 정책을 0으로 설정하면 되풀이가 비활성화됩니다. 기본 되풀이 정책과 원시 ARF 검사 보고서당 100MB의 추정치가 지정되면 환경에 적합한 PV 크기를 계산할 수 있습니다.

#### 5.6.6.5.1. 사용자 정의 결과 스토리지 값 사용

OpenShift Container Platform은 다양한 퍼블릭 클라우드 또는 베어 메탈에 배포할 수 있으므로 Compliance Operator에서는 사용 가능한 스토리지 구성을 결정할 수 없습니다. 기본적으로 Compliance Operator는 클러스터의 기본 스토리지 클래스를 사용하여 결과를 저장하는 PV를 생성하지만 사용자 정의 스토리지 클래스는 `rawResultStorage.StorageClassName` 특성을 사용하여 구성할 수 있습니다.

중요

클러스터에서 기본 스토리지 클래스를 지정하지 않는 경우 이 특성을 설정해야 합니다.

표준 스토리지 클래스를 사용하고 마지막 결과 10개를 유지하는 10GB 크기의 영구 볼륨을 만들도록 `ScanSetting` 사용자 정의 리소스를 구성합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  name: default
  namespace: openshift-compliance
rawResultStorage:
  storageClassName: standard
  rotation: 10
  size: 10Gi
roles:
- worker
- master
scanTolerations:
- effect: NoSchedule
  key: node-role.kubernetes.io/master
  operator: Exists
schedule: '0 1 * * *'
```

#### 5.6.6.6. 제품군 검사에서 생성된 수정 사항 적용

`ComplianceSuite` 오브젝트에서 `autoApplyRemediations` 부울 매개 변수를 사용할 수 있지만, 대신 `compliance.openshift.io/apply-remediations` 로 오브젝트에 주석을 달 수 있습니다. 이를 통해 Operator는 생성된 모든 수정 사항을 적용할 수 있습니다.

프로세스

다음을 실행하여 `compliance.openshift.io/apply-remediations` 주석을 적용합니다.

```shell-session
$ oc -n openshift-compliance \
annotate compliancesuites/workers-compliancesuite compliance.openshift.io/apply-remediations=
```

#### 5.6.6.7. 수정 사항 자동 업데이트

경우에 따라 최신 콘텐츠가 있는 검사에서 `OUTDATED` 로 업데이트 적용을 표시할 수 있습니다. 관리자는 `compliance.openshift.io/remove-outdated` 주석을 적용하여 새 업데이트를 적용하고 오래된 항목을 제거할 수 있습니다.

프로세스

`compliance.openshift.io/remove-outdated` 주석을 적용합니다.

```shell-session
$ oc -n openshift-compliance \
annotate compliancesuites/workers-compliancesuite compliance.openshift.io/remove-outdated=
```

또는 `ScanSetting` 또는 `ComplianceSuite` 오브젝트에 `autoUpdateRemediations` 플래그를 설정하여 수정 사항을 자동으로 업데이트합니다.

#### 5.6.6.8. Compliance Operator에 대한 사용자 정의 SCC 생성

일부 환경에서는 Compliance Operator `api-resource-collector` 에서 올바른 권한을 사용할 수 있도록 사용자 정의 SCC(보안 컨텍스트 제약 조건) 파일을 생성해야 합니다.

사전 요구 사항

`admin` 권한이 있어야 합니다.

프로세스

이름이 `restricted-adjusted-compliance.yaml` 인 YAML 파일에 SCC를 정의합니다.

```yaml
allowHostDirVolumePlugin: false
  allowHostIPC: false
  allowHostNetwork: false
  allowHostPID: false
  allowHostPorts: false
  allowPrivilegeEscalation: true
  allowPrivilegedContainer: false
  allowedCapabilities: null
  apiVersion: security.openshift.io/v1
  defaultAddCapabilities: null
  fsGroup:
    type: MustRunAs
  kind: SecurityContextConstraints
  metadata:
    name: restricted-adjusted-compliance
  priority: 30
  readOnlyRootFilesystem: false
  requiredDropCapabilities:
  - KILL
  - SETUID
  - SETGID
  - MKNOD
  runAsUser:
    type: MustRunAsRange
  seLinuxContext:
    type: MustRunAs
  supplementalGroups:
    type: RunAsAny
  users:
  - system:serviceaccount:openshift-compliance:api-resource-collector
  volumes:
  - configMap
  - downwardAPI
  - emptyDir
  - persistentVolumeClaim
  - projected
  - secret
```

1. 이 SCC의 우선순위는 `system:authenticated` 그룹에 적용되는 다른 SCC보다 커야 합니다.

2. Compliance Operator 스캐너 Pod에서 사용하는 서비스 계정입니다.

SCC를 생성합니다.

```shell-session
$ oc create -n openshift-compliance  -f restricted-adjusted-compliance.yaml
```

```shell-session
securitycontextconstraints.security.openshift.io/restricted-adjusted-compliance created
```

검증

SCC가 생성되었는지 확인합니다.

```shell-session
$ oc get -n openshift-compliance scc restricted-adjusted-compliance
```

```shell-session
NAME                             PRIV    CAPS         SELINUX     RUNASUSER        FSGROUP     SUPGROUP   PRIORITY   READONLYROOTFS   VOLUMES
restricted-adjusted-compliance   false   <no value>   MustRunAs   MustRunAsRange   MustRunAs   RunAsAny   30         false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
```

#### 5.6.6.9. 추가 리소스

보안 컨텍스트 제약 조건 관리

#### 5.6.7. Compliance Operator 검사 문제 해결

이 섹션에서는 Compliance Operator 문제 해결 방법에 대해 설명합니다. 이 정보는 문제를 진단하거나 버그 보고서에 정보를 제공하는 데 유용할 수 있습니다. 몇 가지 일반적인 정보:

Compliance Operator는 중요한 일이 발생할 때 Kubernetes 이벤트를 생성합니다. 다음 명령을 사용하여 클러스터의 모든 이벤트를 볼 수 있습니다.

```shell-session
$ oc get events -n openshift-compliance
```

또는 다음 명령을 사용하여 검사와 같은 오브젝트 이벤트를 볼 수 있습니다.

```shell-session
$ oc describe -n openshift-compliance compliancescan/cis-compliance
```

Compliance Operator는 대략 API 오브젝트당 하나씩 여러 개의 컨트롤러로 구성됩니다. 문제가 있는 API 오브젝트에 해당하는 컨트롤러만 필터링하는 것이 유용할 수 있습니다. `ComplianceRemediation` 을 적용할 수 없는 경우 `remediationctrl` 컨트롤러의 메시지를 확인하십시오. 다음 명령을 사용하여 구문 분석하면 단일 컨트롤러의 메시지를 필터링할 수 있습니다.

```shell
jq
```

```shell-session
$ oc -n openshift-compliance logs compliance-operator-775d7bddbd-gj58f \
    | jq -c 'select(.logger == "profilebundlectrl")'
```

타임스탬프는 UTC의 UNIX epoch 이후의 초로 기록됩니다. 사람이 읽을 수 있는 날짜로 변환하려면 `date -d @timestamp --utc` 를 사용하십시오. 예를 들면 다음과 같습니다.

```shell-session
$ date -d @1596184628.955853 --utc
```

많은 사용자 정의 리소스 중에서도 가장 중요한 `ComplianceSuite` 및 `ScanSetting` 에서는 `debug` 옵션을 설정할 수 있습니다. 이 옵션을 활성화하면 OpenSCAP 스캐너 Pod 및 기타 도우미 Pod의 상세 수준이 높아집니다.

단일 규칙이 예기치 않게 통과 또는 실패하는 경우 해당 규칙만 사용하여 단일 스캔 또는 모음을 실행하고 해당 `ComplianceCheckResult` 오브젝트에서 규칙 ID를 찾은 후 이를 `Scan` CR에서 `rule` 특성 값으로 사용하는 것이 도움이 될 수 있습니다. 그러면 `debug` 옵션이 활성화된 상태에서 스캐너 Pod의 `scanner` 컨테이너 로그에 원시 OpenSCAP 로그가 표시됩니다.

#### 5.6.7.1. 검사 구조

다음 섹션에서는 Compliance Operator 검사의 구성 요소 및 단계를 간략하게 설명합니다.

#### 5.6.7.1.1. 규정 준수 소스

규정 준수 콘텐츠는 `ProfileBundle` 오브젝트에서 생성되는 `Profile` 오브젝트에 저장됩니다. Compliance Operator는 클러스터와 클러스터 노드에 대해 각각 하나의 `ProfileBundle` 오브젝트를 생성합니다.

```shell-session
$ oc get -n openshift-compliance profilebundle.compliance
```

```shell-session
$ oc get -n openshift-compliance profile.compliance
```

`ProfileBundle` 오브젝트는 `Bundle` 이라는 이름으로 레이블이 지정된 배포에서 처리합니다. `Bundle` 문제를 해결하려면 배포를 찾은 후 해당 배포에서 Pod 로그를 보면 됩니다.

```shell-session
$ oc logs -n openshift-compliance -lprofile-bundle=ocp4 -c profileparser
```

```shell-session
$ oc get -n openshift-compliance deployments,pods -lprofile-bundle=ocp4
```

```shell-session
$ oc logs -n openshift-compliance pods/<pod-name>
```

```shell-session
$ oc describe -n openshift-compliance pod/<pod-name> -c profileparser
```

#### 5.6.7.1.2. ScanSetting 및 ScanSettingBinding 오브젝트 라이프사이클 및 디버깅

유효한 준수 콘텐츠 소스를 사용하면 높은 수준의 `ScanSetting` 및 `ScanSettingBinding` 오브젝트를 사용하여 `ComplianceSuite` 및 `ComplianceScan` 오브젝트를 생성할 수 있습니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  name: my-companys-constraints
debug: true
# For each role, a separate scan will be created pointing
# to a node-role specified in roles
roles:
  - worker
---
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSettingBinding
metadata:
  name: my-companys-compliance-requirements
profiles:
  # Node checks
  - name: rhcos4-e8
    kind: Profile
    apiGroup: compliance.openshift.io/v1alpha1
  # Cluster checks
  - name: ocp4-e8
    kind: Profile
    apiGroup: compliance.openshift.io/v1alpha1
settingsRef:
  name: my-companys-constraints
  kind: ScanSetting
  apiGroup: compliance.openshift.io/v1alpha1
```

`ScanSetting` 및 `ScanSettingBinding` 오브젝트는 모두 `logger=scansettingbindingctrl` 태그가 지정된 동일한 컨트롤러에서 처리합니다. 이러한 오브젝트에는 상태가 없습니다. 모든 문제는 이벤트 형식으로 전달됩니다.

```shell-session
Events:
  Type     Reason        Age    From                    Message
  ----     ------        ----   ----                    -------
  Normal   SuiteCreated  9m52s  scansettingbindingctrl  ComplianceSuite openshift-compliance/my-companys-compliance-requirements created
```

이제 `ComplianceSuite` 오브젝트가 생성되었습니다. flow는 새로 생성된 `ComplianceSuite` 를 계속 조정합니다.

#### 5.6.7.1.3. ComplianceSuite 사용자 정의 리소스 라이프사이클 및 디버깅

`ComplianceSuite` CR은 `ComplianceScan` 관련 래퍼입니다. `ComplianceSuite` CR은 `logger=suitectrl` 태그가 지정된 컨트롤러에서 처리합니다. 이 컨트롤러는 모음의 검사 생성을 처리하고 개별 검사 상태를 단일 모음 상태로 조정 및 집계합니다. 모음이 주기적으로 실행되도록 설정된 경우에는 초기 실행이 완료된 후 `suitectrl` 에서도 `CronJob` CR 생성을 처리합니다.

```shell-session
$ oc get cronjobs
```

```shell-session
NAME                                           SCHEDULE    SUSPEND   ACTIVE   LAST SCHEDULE   AGE
<cron_name>                                    0 1 * * *   False     0        <none>          151m
```

가장 중요한 문제의 경우 이벤트가 생성됩니다. 다음 명령으로 문제를 확인하십시오. `Suite` 오브젝트에는 이 모음에 속한 `Scan` 오브젝트에서 `Status` 하위 리소스를 업데이트할 때 업데이트되는 `Status` 하위 리소스도 있습니다. 예상되는 모든 검사가 생성되면 제어가 검사 컨트롤러로 전달됩니다.

```shell
oc describe compliancesuites/<name>
```

#### 5.6.7.1.4. ComplianceScan 사용자 정의 리소스 라이프사이클 및 디버깅

`ComplianceScan` CR은 `scanctrl` 컨트롤러에 의해 처리됩니다. 여기에서 실제 검사가 발생하고 검사 결과가 생성됩니다. 각 검사는 여러 단계를 거칩니다.

#### 5.6.7.1.4.1. 보류 단계

이 단계에서는 검사의 정확성을 확인합니다. 스토리지 크기와 같은 일부 매개변수가 잘못된 경우 검사가 ‘오류와 함께 완료’ 결과로 전환되고, 그러지 않으면 시작 단계가 진행됩니다.

#### 5.6.7.1.4.2. 시작 단계

이 단계에서는 스캐너 Pod에 대한 환경이나 스캐너 Pod를 평가할 스크립트를 직접 포함하는 여러 구성 맵이 있습니다. 구성 맵을 나열합니다.

```shell-session
$ oc -n openshift-compliance get cm \
-l compliance.openshift.io/scan-name=rhcos4-e8-worker,complianceoperator.openshift.io/scan-script=
```

이러한 구성 맵은 스캐너 Pod에서 사용합니다. 스캐너 동작을 수정하거나 스캐너 디버그 수준을 변경하거나 원시 결과를 출력해야 하는 경우 구성 맵을 수정하는 것이 좋습니다. 이후 원시 ARF 결과를 저장하기 위해 검사별 영구 볼륨 클레임이 생성됩니다.

```shell-session
$ oc get pvc -n openshift-compliance -lcompliance.openshift.io/scan-name=rhcos4-e8-worker
```

PVC는 검사별 `ResultServer` 배포로 마운트됩니다. `ResultServer` 는 개별 스캐너 Pod에서 전체 ARF 결과를 업로드하는 간단한 HTTP 서버입니다. 각 서버는 다른 노드에서 실행될 수 있습니다. 전체 ARF 결과는 매우 클 수 있으며 동시에 여러 노드에서 마운트할 수 있는 볼륨을 생성할 수 있다고 가정해서는 안 됩니다. 검사가 완료되면 `ResultServer` 배포가 축소됩니다. 원시 결과가 있는 PVC는 다른 사용자 정의 Pod에서 마운트할 수 있으며 결과를 가져오거나 검사할 수 있습니다. 스캐너 Pod와 `ResultServer` 간 트래픽은 상호 TLS 프로토콜로 보호됩니다.

마지막으로 이 단계에서는 스캐너 Pod가 시작되는데, `Platform` 검사 인스턴스용 스캐너 Pod 1개와 `node` 검사 인스턴스에 일치하는 노드당 스캐너 Pod 1개입니다. 노드별 Pod는 노드 이름으로 레이블이 지정됩니다. 각 Pod는 항상 `ComplianceScan` 이라는 이름으로 레이블이 지정됩니다.

```shell-session
$ oc get pods -lcompliance.openshift.io/scan-name=rhcos4-e8-worker,workload=scanner --show-labels
```

```shell-session
NAME                                                              READY   STATUS      RESTARTS   AGE   LABELS
rhcos4-e8-worker-ip-10-0-169-90.eu-north-1.compute.internal-pod   0/2     Completed   0          39m   compliance.openshift.io/scan-name=rhcos4-e8-worker,targetNode=ip-10-0-169-90.eu-north-1.compute.internal,workload=scanner
```

그런 다음 검사가 실행 중 단계로 진행됩니다.

#### 5.6.7.1.4.3. 실행 단계

실행 단계는 스캐너 Pod가 종료될 때까지 대기합니다. 다음은 실행 단계에서 사용되는 용어 및 프로세스입니다.

init container: `content-container` 라는 하나의 init 컨테이너가 있습니다. contentImage 컨테이너를 실행하고 이 Pod의 다른 컨테이너와 공유하는 `/content` 디렉터리에 contentFile 을 복사하는 단일 명령을 실행합니다.

scanner: 이 컨테이너는 검사를 실행합니다. 노드 검사의 경우 컨테이너는 노드 파일 시스템을 `/host` 로 마운트하고 init 컨테이너에서 제공하는 콘텐츠를 마운트합니다. 컨테이너는 또한 시작 단계에서 생성된 `entrypoint`

`ConfigMap` 을 마운트하고 실행합니다. 진입점 `ConfigMap` 의 기본 스크립트는 OpenSCAP을 실행하고 Pod 컨테이너 간 공유하는 `/results` 디렉터리에 결과 파일을 저장합니다. 이 Pod의 로그를 보고 OpenSCAP 스캐너에서 점검한 사항을 확인할 수 있습니다. 더 자세한 출력 내용은 `debug` 플래그를 사용하여 볼 수 있습니다.

logcollector: logcollector 컨테이너는 스캐너 컨테이너가 종료될 때까지 대기합니다. 그런 다음 전체 ARF 결과를 `ResultServer` 에 업로드하고 XCCDF 결과를 검사 결과 및 OpenSCAP 결과 코드와 함께 `ConfigMap` 으로 별도로 업로드합니다. 이러한 결과 구성 맵은 검사 이름(`compliance.openshift.io/scan-name=rhcos4-e8-worker`)으로 레이블이 지정됩니다.

```shell-session
$ oc describe cm/rhcos4-e8-worker-ip-10-0-169-90.eu-north-1.compute.internal-pod
```

```shell-session
Name:         rhcos4-e8-worker-ip-10-0-169-90.eu-north-1.compute.internal-pod
      Namespace:    openshift-compliance
      Labels:       compliance.openshift.io/scan-name-scan=rhcos4-e8-worker
                    complianceoperator.openshift.io/scan-result=
      Annotations:  compliance-remediations/processed:
                    compliance.openshift.io/scan-error-msg:
                    compliance.openshift.io/scan-result: NON-COMPLIANT
                    OpenSCAP-scan-result/node: ip-10-0-169-90.eu-north-1.compute.internal

      Data
      ====
      exit-code:
      ----
      2
      results:
      ----
      <?xml version="1.0" encoding="UTF-8"?>
      ...
```

`Platform` 검사를 위한 스캐너 Pod는 다음을 제외하고 비슷합니다.

`api-resource-collector` 라는 하나의 추가 init 컨테이너가 있습니다. 이 컨테이너는 content-container init 컨테이너에서 제공하는 OpenSCAP 콘텐츠를 읽고, 해당 콘텐츠에서 검사해야 하는 API 리소스를 파악한 후 `scanner` 컨테이너에서 이러한 API 리소스를 읽는 공유 디렉터리에 저장합니다.

`scanner` 컨테이너는 호스트 파일 시스템을 마운트할 필요가 없습니다.

스캐너 Pod가 완료되면 검사가 집계 단계로 이동합니다.

#### 5.6.7.1.4.4. 집계 단계

검사 컨트롤러는 집계 단계에서 집계기 Pod라는 또 다른 Pod를 생성합니다. 그 목적은 결과 `ConfigMap` 오브젝트를 가져와서 결과를 읽고 각 점검 결과에 해당하는 Kubernetes 오브젝트를 만드는 것입니다. 점검 실패를 자동으로 수정할 수 있는 경우 `ComplianceRemediation` 오브젝트가 생성됩니다. 또한 집계기 Pod는 사람이 읽을 수 있는 점검 및 수정용 메타데이터를 제공하기 위해 init 컨테이너를 사용하여 OpenSCAP 콘텐츠도 마운트합니다.

집계기 Pod에서 구성 맵을 처리하면 구성 맵에 `compliance-remediations/processed` 라는 레이블이 지정됩니다. 이 단계의 결과는 `ComplianceCheckResult` 오브젝트

```shell-session
$ oc get compliancecheckresults -lcompliance.openshift.io/scan-name=rhcos4-e8-worker
```

```shell-session
NAME                                                       STATUS   SEVERITY
rhcos4-e8-worker-accounts-no-uid-except-zero               PASS     high
rhcos4-e8-worker-audit-rules-dac-modification-chmod        FAIL     medium
```

및 `ComplianceRemediation` 오브젝트입니다.

```shell-session
$ oc get complianceremediations -lcompliance.openshift.io/scan-name=rhcos4-e8-worker
```

```shell-session
NAME                                                       STATE
rhcos4-e8-worker-audit-rules-dac-modification-chmod        NotApplied
rhcos4-e8-worker-audit-rules-dac-modification-chown        NotApplied
rhcos4-e8-worker-audit-rules-execution-chcon               NotApplied
rhcos4-e8-worker-audit-rules-execution-restorecon          NotApplied
rhcos4-e8-worker-audit-rules-execution-semanage            NotApplied
rhcos4-e8-worker-audit-rules-execution-setfiles            NotApplied
```

이러한 CR이 생성되면 집계기 Pod가 종료되고 검사가 완료 단계로 전환됩니다.

#### 5.6.7.1.4.5. 완료 단계

최종 검사 단계에서는 필요한 경우 검사 리소스가 정리되고 `ResultServer` 배포가 축소되거나(검사가 1회인 경우) 삭제됩니다(검사가 계속되는 경우). 삭제하는 경우 다음 검사 인스턴스에서 배포를 다시 생성합니다.

또한 주석을 달아 완료 단계에서 검사 재실행을 트리거할 수도 있습니다.

```shell-session
$ oc -n openshift-compliance \
annotate compliancescans/rhcos4-e8-worker compliance.openshift.io/rescan=
```

`autoApplyRemediations: true` 를 사용하여 수정을 자동 적용하도록 설정하지 않으면 검사가 완료 단계에 도달한 후 자체적으로 수행되는 작업이 없습니다. OpenShift Container Platform 관리자가 수정 사항을 검토하고 필요에 따라 적용합니다. 수정을 자동 적용하도록 설정하면 완료 단계에서 `ComplianceSuite` 컨트롤러에 설정이 전달되고, 이 컨트롤러에서 검사가 매핑되는 머신 구성 풀을 일시 중지한 후 모든 수정을 한 번에 적용합니다. 수정은 `ComplianceRemediation` 컨트롤러에서 대신 적용합니다.

#### 5.6.7.1.5. ComplianceRemediation 컨트롤러 라이프사이클 및 디버깅

예제 검사에서 몇 가지 결과가 보고되었습니다. `apply` 특성을 `true` 로 전환하여 수정 중 하나를 활성화할 수 있습니다.

```shell-session
$ oc patch complianceremediations/rhcos4-e8-worker-audit-rules-dac-modification-chmod --patch '{"spec":{"apply":true}}' --type=merge
```

`ComplianceRemediation` 컨트롤러(`logger=remediationctrl`)는 수정된 오브젝트를 조정합니다. 조정으로 인해 조정된 수정 오브젝트의 상태가 변경될 뿐만 아니라 적용된 모든 수정이 포함되는 렌더링된 모음별 `MachineConfig` 오브젝트도 변경됩니다.

`MachineConfig` 오브젝트는 항상 `75-` 로 시작하며 검사 및 모음 이름을 따서 이름이 지정됩니다.

```shell-session
$ oc get mc | grep 75-
```

```shell-session
75-rhcos4-e8-worker-my-companys-compliance-requirements                                                3.2.0             2m46s
```

현재 `mc` 가 구성되어 있는 수정이 머신 구성의 주석에 나열됩니다.

```shell-session
$ oc describe mc/75-rhcos4-e8-worker-my-companys-compliance-requirements
```

```shell-session
Name:         75-rhcos4-e8-worker-my-companys-compliance-requirements
Labels:       machineconfiguration.openshift.io/role=worker
Annotations:  remediation/rhcos4-e8-worker-audit-rules-dac-modification-chmod:
```

`ComplianceRemediation` 컨트롤러 알고리즘은 다음과 같이 작동합니다.

현재 적용된 모든 수정은 초기 수정 세트로 해석됩니다.

조정된 수정을 적용해야 하는 경우 이 세트에 추가됩니다.

`MachineConfig` 오브젝트는 해당 세트에서 렌더링되고 세트의 수정 이름으로 주석이 달립니다. 세트가 비어 있는 경우(마지막 수정이 적용되지 않음) 렌더링된 `MachineConfig` 오브젝트가 제거됩니다.

렌더링된 머신 구성이 클러스터에 이미 적용된 구성과 다른 경우에만 적용된 MC가 업데이트되거나 생성 또는 삭제됩니다.

`MachineConfig` 오브젝트를 생성하거나 수정하면 `machineconfiguration.openshift.io/role` 레이블과 일치하는 노드의 재부팅이 트리거됩니다. 자세한 내용은 Machine Config Operator 설명서를 참조하십시오.

필요한 경우 렌더링된 머신 구성을 업데이트하고 조정된 수정 오브젝트 상태를 업데이트하면 수정 루프가 종료됩니다. 예제의 경우 수정을 적용하면 재부팅이 트리거됩니다. 재부팅 후 검사에 주석을 달아 다시 실행합니다.

```shell-session
$ oc -n openshift-compliance \
annotate compliancescans/rhcos4-e8-worker compliance.openshift.io/rescan=
```

검사가 실행되고 완료됩니다. 전달할 수정을 확인합니다.

```shell-session
$ oc -n openshift-compliance \
get compliancecheckresults/rhcos4-e8-worker-audit-rules-dac-modification-chmod
```

```shell-session
NAME                                                  STATUS   SEVERITY
rhcos4-e8-worker-audit-rules-dac-modification-chmod   PASS     medium
```

#### 5.6.7.1.6. 유용한 레이블

Compliance Operator에서 생성하는 각 Pod는 특별히 해당 Pod가 속하는 검사와 수행하는 작업을 사용하여 레이블이 지정됩니다. 검사 식별자는 `compliance.openshift.io/scan-name` 으로 레이블이 지정됩니다. 워크로드 식별자는 `workload` 로 레이블이 지정됩니다.

Compliance Operator는 다음 워크로드를 예약합니다.

scanner: 적합성 검사를 수행합니다.

resultserver: 준수 검사에 대한 원시 결과를 저장합니다.

aggregator: 결과를 집계하고, 불일치를 감지하고, 결과 오브젝트를 출력합니다(검사 결과 및 수정).

suitererunner: 재실행할 모음에 태그를 지정합니다(일정이 설정된 경우).

profileparser: 데이터 스트림을 구문 분석하고 적절한 프로필, 규칙, 변수를 만듭니다.

특정 워크로드에 디버깅 및 로그가 필요한 경우 다음을 실행합니다.

```shell-session
$ oc logs -l workload=<workload_name> -c <container_name>
```

#### 5.6.7.2. Compliance Operator 리소스 제한 증가

경우에 따라 Compliance Operator에 기본 제한에서 허용하는 것보다 더 많은 메모리가 필요할 수 있습니다. 이 문제를 완화하는 가장 좋은 방법은 사용자 정의 리소스 제한을 설정하는 것입니다.

스캐너 Pod의 기본 메모리 및 CPU 제한을 늘리려면 'ScanSetting' 사용자 정의 리소스 를 참조하십시오.

프로세스

Operator의 메모리 제한을 500Mi로 늘리려면 `co-memlimit-patch.yaml` 이라는 다음 패치 파일을 생성합니다.

```yaml
spec:
  config:
    resources:
      limits:
        memory: 500Mi
```

패치 파일을 적용합니다.

```shell-session
$ oc patch sub compliance-operator -nopenshift-compliance --patch-file co-memlimit-patch.yaml --type=merge
```

#### 5.6.7.3. Operator 리소스 제약 조건 구성

`resources` 필드는 OLM(Operator Lifecycle Manager)에서 생성한 Pod의 모든 컨테이너에 대한 리소스 제약 조건을 정의합니다.

참고

이 프로세스에 적용된 리소스 제약 조건은 기존 리소스 제약 조건을 덮어씁니다.

프로세스

`Subscription` 오브젝트를 편집하여 0.25 cpu 및 64 Mi의 메모리 요청을 삽입하고 각 컨테이너에 0.5 cpu 및 128 Mi의 메모리 제한을 삽입합니다.

```yaml
kind: Subscription
metadata:
  name: compliance-operator
  namespace: openshift-compliance
spec:
  package: package-name
  channel: stable
  config:
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

#### 5.6.7.4. ScanSetting 리소스 구성

500개 이상의 MachineConfig가 포함된 클러스터에서 Compliance Operator를 사용하는 경우 `플랫폼` 검사를 수행할 때 `ocp4-pci-dss-api-checks-pod` Pod가 `init` 단계에서 일시 중지될 수 있습니다.

참고

이 프로세스에 적용된 리소스 제약 조건은 기존 리소스 제약 조건을 덮어씁니다.

프로세스

`ocp4-pci-dss-api-checks-pod` Pod가 `Init:OOMKilled` 상태에 있는지 확인합니다.

```shell-session
$ oc get pod ocp4-pci-dss-api-checks-pod -w
```

```shell-session
NAME                          READY   STATUS     RESTARTS        AGE
ocp4-pci-dss-api-checks-pod   0/2     Init:1/2   8 (5m56s ago)   25m
ocp4-pci-dss-api-checks-pod   0/2     Init:OOMKilled   8 (6m19s ago)   26m
```

`ScanSetting` CR에서 `scanLimits` 속성을 편집하여 `ocp4-pci-dss-api-checks-pod` Pod에 사용 가능한 메모리를 늘립니다.

```yaml
timeout: 30m
strictNodeScan: true
metadata:
  name: default
  namespace: openshift-compliance
kind: ScanSetting
showNotApplicable: false
rawResultStorage:
  nodeSelector:
    node-role.kubernetes.io/master: ''
  pvAccessModes:
    - ReadWriteOnce
  rotation: 3
  size: 1Gi
  tolerations:
    - effect: NoSchedule
      key: node-role.kubernetes.io/master
      operator: Exists
    - effect: NoExecute
      key: node.kubernetes.io/not-ready
      operator: Exists
      tolerationSeconds: 300
    - effect: NoExecute
      key: node.kubernetes.io/unreachable
      operator: Exists
      tolerationSeconds: 300
    - effect: NoSchedule
      key: node.kubernetes.io/memory-pressure
      operator: Exists
schedule: 0 1 * * *
roles:
  - master
  - worker
apiVersion: compliance.openshift.io/v1alpha1
maxRetryOnTimeout: 3
scanTolerations:
  - operator: Exists
scanLimits:
  memory: 1024Mi
```

1. 기본 설정은 `500Mi` 입니다.

`ScanSetting` CR을 클러스터에 적용합니다.

```shell-session
$ oc apply -f scansetting.yaml
```

#### 5.6.7.5. ScanSetting 시간 초과 구성

`ScanSetting` 오브젝트에는 `1h30m` 과 같은 기간 문자열로 `ComplianceScanSetting` 오브젝트에 지정할 수 있는 시간 초과 옵션이 있습니다. 지정된 시간 초과 내에 검사가 완료되지 않으면 `maxRetryOnTimeout` 제한에 도달할 때까지 검사 다시 시도합니다.

프로세스

ScanSetting에서 `시간 초과` 및 `maxRetryOnTimeout` 을 설정하려면 기존 `ScanSetting` 오브젝트를 수정합니다.

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  name: default
  namespace: openshift-compliance
rawResultStorage:
  rotation: 3
  size: 1Gi
roles:
- worker
- master
scanTolerations:
- effect: NoSchedule
  key: node-role.kubernetes.io/master
  operator: Exists
schedule: '0 1 * * *'
timeout: '10m0s'
maxRetryOnTimeout: 3
```

1. `timeout` 변수는 `1h30m` 과 같은 기간 문자열로 정의됩니다. 기본값은 `30m` 입니다. 시간 초과를 비활성화하려면 값을 `0s` 로 설정합니다.

2. `maxRetryOnTimeout` 변수는 재시도 횟수를 정의합니다. 기본값은 `3` 입니다.

#### 5.6.7.6. 지원 요청

이 문서에 설명된 절차 또는 일반적으로 OpenShift Container Platform에 문제가 발생하는 경우 Red Hat 고객 포털 에 액세스하십시오.

고객 포털에서 다음을 수행할 수 있습니다.

Red Hat 제품과 관련된 기사 및 솔루션에 대한 Red Hat 지식베이스를 검색하거나 살펴볼 수 있습니다.

Red Hat 지원에 대한 지원 케이스 제출할 수 있습니다.

다른 제품 설명서에 액세스 가능합니다.

클러스터 문제를 식별하기 위해 OpenShift Cluster Manager 에서 Red Hat Lightspeed를 사용할 수 있습니다. Red Hat Lightspeed는 문제에 대한 세부 정보와 가능한 경우 문제 해결 방법에 대한 정보를 제공합니다.

이 문서를 개선하기 위한 제안이 있거나 오류를 발견한 경우 가장 관련 문서 구성 요소에 대해 Jira 문제를 제출합니다. 섹션 이름 및 OpenShift Container Platform 버전과 같은 구체적인 정보를 제공합니다.

#### 5.6.8. oc-compliance 플러그인 사용

Compliance Operator 는 클러스터에 대한 많은 검사 및 수정을 자동화하지만 클러스터를 규정 준수 상태로 전환하려면 관리자가 Compliance Operator API 및 기타 구성 요소와 상호 작용해야 하는 경우가 많습니다. 플러그인을 사용하면 프로세스를 더 쉽게 수행할 수 있습니다.

```shell
oc-compliance
```

#### 5.6.8.1. oc-compliance 플러그인 설치

프로세스

다음 명령이미지를 추출하여 바이너리를 가져옵니다.

```shell
oc-compliance
```

```shell
oc-compliance
```

```shell-session
$ podman run --rm -v ~/.local/bin:/mnt/out:Z registry.redhat.io/compliance/oc-compliance-rhel8:stable /bin/cp /usr/bin/oc-compliance /mnt/out/
```

```shell-session
W0611 20:35:46.486903   11354 manifest.go:440] Chose linux/amd64 manifest from the manifest list.
```

이제 다음 명령을 실행할 수 있습니다.

```shell
oc-compliance
```

#### 5.6.8.2. 원시 결과 가져오기

규정 준수 검사가 완료되면 결과 `ComplianceCheckResult` CR(사용자 정의 리소스)에 개별 검사 결과가 나열됩니다. 그러나 관리자 또는 감사자는 검사에 대한 전체 세부 정보가 필요할 수 있습니다. OpenSCAP 툴은 자세한 결과를 사용하여 AMQP(Advanced Recording Format) 포맷 파일을 생성합니다. 이 ARF 파일은 구성 맵 또는 기타 표준 Kubernetes 리소스에 저장하기에 너무 크므로 이를 포함할 영구 볼륨(PV)이 생성됩니다.

프로세스

Compliance Operator를 사용하여 PV에서 결과를 가져오는 작업은 4단계 프로세스입니다. 그러나 플러그인을 사용하면 단일 명령을 사용할 수 있습니다.

```shell
oc-compliance
```

```shell-session
$ oc compliance fetch-raw <object-type> <object-name> -o <output-path>
```

`<object-type>` 은 검사가 시작된 오브젝트에 따라 `scansettingbinding`, `compliancescan` 또는 `compliancesuite` 일 수 있습니다.

`<object-name>` 은 ARF 파일을 수집할 바인딩, 제품군 또는 검사 오브젝트의 이름이고 `<output-path>` 는 결과를 배치할 로컬 디렉터리입니다.

예를 들면 다음과 같습니다.

```shell-session
$ oc compliance fetch-raw scansettingbindings my-binding -o /tmp/
```

```shell-session
Fetching results for my-binding scans: ocp4-cis, ocp4-cis-node-worker, ocp4-cis-node-master
Fetching raw compliance results for scan 'ocp4-cis'.......
The raw compliance results are available in the following directory: /tmp/ocp4-cis
Fetching raw compliance results for scan 'ocp4-cis-node-worker'...........
The raw compliance results are available in the following directory: /tmp/ocp4-cis-node-worker
Fetching raw compliance results for scan 'ocp4-cis-node-master'......
The raw compliance results are available in the following directory: /tmp/ocp4-cis-node-master
```

디렉터리에서 파일 목록을 확인합니다.

```shell-session
$ ls /tmp/ocp4-cis-node-master/
```

```shell-session
ocp4-cis-node-master-ip-10-0-128-89.ec2.internal-pod.xml.bzip2  ocp4-cis-node-master-ip-10-0-150-5.ec2.internal-pod.xml.bzip2  ocp4-cis-node-master-ip-10-0-163-32.ec2.internal-pod.xml.bzip2
```

결과를 추출합니다.

```shell-session
$ bunzip2 -c resultsdir/worker-scan/worker-scan-stage-459-tqkg7-compute-0-pod.xml.bzip2 > resultsdir/worker-scan/worker-scan-ip-10-0-170-231.us-east-2.compute.internal-pod.xml
```

결과를 확인합니다.

```shell-session
$ ls resultsdir/worker-scan/
```

```shell-session
worker-scan-ip-10-0-170-231.us-east-2.compute.internal-pod.xml
worker-scan-stage-459-tqkg7-compute-0-pod.xml.bzip2
worker-scan-stage-459-tqkg7-compute-1-pod.xml.bzip2
```

#### 5.6.8.3. 검사 재실행

예약된 작업으로 스캔을 실행할 수 있지만 수정을 적용한 후 또는 클러스터에 대한 기타 변경이 이루어진 경우 필요에 따라 검사를 다시 실행해야 합니다.

프로세스

Compliance Operator를 사용하여 검사를 다시 실행하려면 검사 오브젝트에서 주석을 사용해야 합니다. 그러나 플러그인을 사용하면 단일 명령으로 검사를 재실행할 수 있습니다. `my-binding`:이라는 `ScanSettingBinding` 오브젝트에 대한 검사를 재실행하려면 다음 명령을 입력합니다.

```shell
oc-compliance
```

```shell-session
$ oc compliance rerun-now scansettingbindings my-binding
```

```shell-session
Rerunning scans from 'my-binding': ocp4-cis
Re-running scan 'openshift-compliance/ocp4-cis'
```

#### 5.6.8.4. ScanSettingBinding 사용자 정의 리소스 사용

Compliance Operator에서 제공하는 `ScanSetting` 및 `ScanSettingBinding` CR(사용자 정의 리소스)을 사용하는 경우 `schedule`, `machine roles`, `tolerations` 등과 같은 공통 검사 옵션 세트를 사용하는 동안 여러 프로필 검사를 실행할 수 있습니다. 여러 `ComplianceSuite` 또는 `ComplianceScan` 오브젝트로 작업하는 것보다 쉽지만 새로운 사용자를 혼란스럽게 할 수 있습니다.

다음 명령하위 명령은 `ScanSettingBinding` CR을 생성하는 데 도움이 됩니다.

```shell
oc compliance bind
```

프로세스

다음을 실행합니다.

```shell-session
$ oc compliance bind [--dry-run] -N <binding name> [-S <scansetting name>] <objtype/objname> [..<objtype/objname>]
```

`-S` 플래그를 생략하면 Compliance Operator에서 제공하는 `default` 검사 설정이 사용됩니다.

오브젝트 유형은 Kubernetes 오브젝트 유형으로 `profile` 또는 `tailoredprofile` 일 수 있습니다. 두 개 이상의 오브젝트를 제공할 수 있습니다.

오브젝트 이름은 Kubernetes 리소스의 이름입니다 (예: `.metadata.name`).

`--dry-run` 옵션을 추가하여 생성된 오브젝트의 YAML 파일을 표시합니다.

예를 들어 다음 프로필 및 검사 설정이 제공됩니다.

```shell-session
$ oc get profile.compliance -n openshift-compliance
```

```shell-session
NAME                       AGE     VERSION
ocp4-cis                   3h49m   1.5.0
ocp4-cis-1-4               3h49m   1.4.0
ocp4-cis-1-5               3h49m   1.5.0
ocp4-cis-node              3h49m   1.5.0
ocp4-cis-node-1-4          3h49m   1.4.0
ocp4-cis-node-1-5          3h49m   1.5.0
ocp4-e8                    3h49m
ocp4-high                  3h49m   Revision 4
ocp4-high-node             3h49m   Revision 4
ocp4-high-node-rev-4       3h49m   Revision 4
ocp4-high-rev-4            3h49m   Revision 4
ocp4-moderate              3h49m   Revision 4
ocp4-moderate-node         3h49m   Revision 4
ocp4-moderate-node-rev-4   3h49m   Revision 4
ocp4-moderate-rev-4        3h49m   Revision 4
ocp4-nerc-cip              3h49m
ocp4-nerc-cip-node         3h49m
ocp4-pci-dss               3h49m   3.2.1
ocp4-pci-dss-3-2           3h49m   3.2.1
ocp4-pci-dss-4-0           3h49m   4.0.0
ocp4-pci-dss-node          3h49m   3.2.1
ocp4-pci-dss-node-3-2      3h49m   3.2.1
ocp4-pci-dss-node-4-0      3h49m   4.0.0
ocp4-stig                  3h49m   V2R1
ocp4-stig-node             3h49m   V2R1
ocp4-stig-node-v1r1        3h49m   V1R1
ocp4-stig-node-v2r1        3h49m   V2R1
ocp4-stig-v1r1             3h49m   V1R1
ocp4-stig-v2r1             3h49m   V2R1
rhcos4-e8                  3h49m
rhcos4-high                3h49m   Revision 4
rhcos4-high-rev-4          3h49m   Revision 4
rhcos4-moderate            3h49m   Revision 4
rhcos4-moderate-rev-4      3h49m   Revision 4
rhcos4-nerc-cip            3h49m
rhcos4-stig                3h49m   V2R1
rhcos4-stig-v1r1           3h49m   V1R1
rhcos4-stig-v2r1           3h49m   V2R1
```

```shell-session
$ oc get scansettings -n openshift-compliance
```

```shell-session
NAME                 AGE
default              10m
default-auto-apply   10m
```

`default` 설정을 `ocp4-cis` 및 `ocp4-cis-node` 프로필에 적용하려면 다음을 실행합니다.

```shell-session
$ oc compliance bind -N my-binding profile/ocp4-cis profile/ocp4-cis-node
```

```shell-session
Creating ScanSettingBinding my-binding
```

`ScanSettingBinding` CR이 생성되면 바인딩된 프로파일은 관련 설정으로 두 프로필의 스캔을 시작합니다. 전반적으로 이것은 Compliance Operator로 스캔을 시작하는 가장 빠른 방법입니다.

#### 5.6.8.5. 인쇄 제어

컴플라이언스 표준은 일반적으로 다음과 같이 계층 구조로 구성됩니다.

벤치마크는 특정 표준에 대한 제어 집합의 최상위 정의입니다. 예를 들어 FedRAMP Moderate 또는 Center for Internet Security (CIS) v.1.6.0입니다.

제어는 벤치마크를 준수하기 위해 충족되어야 하는 일련의 요구 사항을 설명합니다. 예: FedRAMP AC-01(액세스 제어 정책 및 절차)

규칙은 규정을 준수하는 시스템에 특정한 단일 검사이며 이러한 규칙 중 하나 이상이 제어에 매핑됩니다.

Compliance Operator는 단일 벤치마크의 프로필로 규칙 그룹화를 처리합니다. 프로필의 규칙 집합이 충족되도록 제어하는 것을 결정하기 어려울 수 있습니다.

프로세스

```shell
oc compliance
```

`control` 하위 명령은 표준에 대한 보고서를 제공하고 지정된 프로필이 충족되도록 제어합니다.

```shell-session
$ oc compliance controls profile ocp4-cis-node
```

```shell-session
+-----------+----------+
| FRAMEWORK | CONTROLS |
+-----------+----------+
| CIS-OCP   | 1.1.1    |
+           +----------+
|           | 1.1.10   |
+           +----------+
|           | 1.1.11   |
+           +----------+
...
```

#### 5.6.8.6. 컴플라이언스 수정 세부 정보 가져오기

Compliance Operator는 클러스터를 준수하는 데 필요한 변경 사항을 자동화하는 데 사용되는 수정 오브젝트를 제공합니다. `fetch-fixes` 하위 명령은 어떤 구성 수정이 사용되는지 정확하게 이해하는 데 도움이 될 수 있습니다. `fetch-fixes` 하위 명령을 사용하여 프로필, 규칙 또는 `ComplianceRemediation` 오브젝트에서 검사할 디렉터리로 수정 오브젝트를 추출합니다.

프로세스

프로필의 수정을 확인합니다.

```shell-session
$ oc compliance fetch-fixes profile ocp4-cis -o /tmp
```

```shell-session
No fixes to persist for rule 'ocp4-api-server-api-priority-flowschema-catch-all'
No fixes to persist for rule 'ocp4-api-server-api-priority-gate-enabled'
No fixes to persist for rule 'ocp4-api-server-audit-log-maxbackup'
Persisted rule fix to /tmp/ocp4-api-server-audit-log-maxsize.yaml
No fixes to persist for rule 'ocp4-api-server-audit-log-path'
No fixes to persist for rule 'ocp4-api-server-auth-mode-no-aa'
No fixes to persist for rule 'ocp4-api-server-auth-mode-node'
No fixes to persist for rule 'ocp4-api-server-auth-mode-rbac'
No fixes to persist for rule 'ocp4-api-server-basic-auth'
No fixes to persist for rule 'ocp4-api-server-bind-address'
No fixes to persist for rule 'ocp4-api-server-client-ca'
Persisted rule fix to /tmp/ocp4-api-server-encryption-provider-cipher.yaml
Persisted rule fix to /tmp/ocp4-api-server-encryption-provider-config.yaml
```

1. 규칙을 자동으로 수정할 수 없거나 수정이 제공되지 않았기 때문에 프로필에 해당 수정 조치가 없는 규칙이 있을 때마다 `No fixes to persist` 경고가 예상됩니다.

YAML 파일의 샘플을 볼 수 있습니다. `head` 명령은 처음 10행을 표시합니다.

```shell-session
$ head /tmp/ocp4-api-server-audit-log-maxsize.yaml
```

```shell-session
apiVersion: config.openshift.io/v1
kind: APIServer
metadata:
  name: cluster
spec:
  maximumFileSizeMegabytes: 100
```

검사 후 생성된 `ComplianceRemediation` 오브젝트에서 수정을 확인합니다.

```shell-session
$ oc get complianceremediations -n openshift-compliance
```

```shell-session
NAME                                             STATE
ocp4-cis-api-server-encryption-provider-cipher   NotApplied
ocp4-cis-api-server-encryption-provider-config   NotApplied
```

```shell-session
$ oc compliance fetch-fixes complianceremediations ocp4-cis-api-server-encryption-provider-cipher -o /tmp
```

```shell-session
Persisted compliance remediation fix to /tmp/ocp4-cis-api-server-encryption-provider-cipher.yaml
```

YAML 파일의 샘플을 볼 수 있습니다. `head` 명령은 처음 10행을 표시합니다.

```shell-session
$ head /tmp/ocp4-cis-api-server-encryption-provider-cipher.yaml
```

```shell-session
apiVersion: config.openshift.io/v1
kind: APIServer
metadata:
  name: cluster
spec:
  encryption:
    type: aescbc
```

주의

수정을 직접 적용하기 전에 주의하십시오. 중간 프로파일의 usbguard 규칙과 같은 일부 수정 사항은 일괄적으로 적용되지 않을 수 있습니다. 이 경우 종속성을 해결하고 클러스터가 정상 상태로 유지되도록 Compliance Operator가 규칙을 적용하도록 허용합니다.

#### 5.6.8.7. ComplianceCheckResult 오브젝트 세부 정보 보기

검사 실행이 완료되면 개별 검사 규칙에 대해 `ComplianceCheckResult` 오브젝트가 생성됩니다. `view-result` 하위 명령은 사용자가 읽을 수 있는 `ComplianceCheckResult` 오브젝트 세부 정보 출력을 제공합니다.

프로세스

다음을 실행합니다.

```shell-session
$ oc compliance view-result ocp4-cis-scheduler-no-bind-address
```

### 6.1. File Integrity Operator 개요

File Integrity Operator는 클러스터 노드에서 파일 무결성 검사를 지속적으로 실행합니다. 각 노드에서 권한 있는 AIDE(Advanced Intrusion Detection Environment) 컨테이너를 초기화하고 실행하는 DaemonSet을 배포하여 DaemonSet Pod의 초기 실행 이후 수정된 파일의 로그를 제공합니다.

참고

File Integrity Operator는 HCP 클러스터에서 지원되지 않습니다.

최신 업데이트는 File Integrity Operator 릴리스 노트 를 참조하십시오.

File Integrity Operator 설치

File Integrity Operator 업데이트

File Integrity Operator 이해

Custom File Integrity Operator 구성

고급 Custom File Integrity Operator 작업 수행

File Integrity Operator 문제 해결

File Integrity Operator 설치 제거

### 6.2. File Integrity Operator 릴리스 정보

OpenShift Container Platform용 File Integrity Operator는 RHCOS 노드에서 파일 무결성 검사를 지속적으로 실행합니다.

이 릴리스 노트에서는 OpenShift Container Platform의 File Integrity Operator 개발을 추적합니다.

File Integrity Operator에 대한 개요는 File Integrity Operator 이해를 참조하십시오.

최신 릴리스에 액세스하려면 File Integrity Operator 업데이트를 참조하십시오.

#### 6.2.1. OpenShift File Integrity Operator 1.3.7

OpenShift File Integrity Operator 1.3.7에서 다음 권고를 사용할 수 있습니다.

RHSA-2025:21913 OpenShift File Integrity Operator 업데이트

이번 업데이트에서는 기본 기본 이미지의 업그레이드된 종속 항목이 포함되어 있습니다.

#### 6.2.2. OpenShift File Integrity Operator 1.3.6

OpenShift File Integrity Operator 1.3.6에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2025:11535 OpenShift File Integrity Operator 버그 수정 업데이트

#### 6.2.2.1. 버그 수정

이전 버전에서는 아래 명령을 실행하면 모든 노드에서 다시 초기화가 트리거되었습니다. 이제 오류가 발생한 노드만 다시 초기화합니다. (OCPBUGS-18933)

```shell
oc annotate fileintegrities/<fileintegrity-name> file-integrity.openshift.io/re-init-on-failed=
```

이전에는 FIO 재설정에서 `NodeHasIntegrityFailure` 경고가 삭제되었습니다. 이는 `지표 file_integrity_operator_node_failed` 설정도 재설정되었기 때문에 발생했습니다. 이번 릴리스에서는 FIO를 다시 시작하면 `NodeHasIntegrityFailure` 경고에 영향을 미치지 않습니다. (OCPBUGS-42807)

이전 버전에서는 `머신 세트` 오브젝트를 확장하여 새 노드가 클러스터에 추가되면 FIO에서 노드가 준비되기 전에 새 노드를 `Failed` 로 표시했습니다. 이번 릴리스에서는 FIO가 새 노드가 준비될 때까지 대기합니다. (OCPBUGS-36483)

이전에는 AIDE(Advanced Intrusion Detection Environment) 데몬 세트 Pod가 AIDE 데이터베이스를 지속적으로 강제로 초기화했습니다. 이번 릴리스에서는 FIO에서 AIDE 데이터베이스를 한 번만 초기화합니다. (OCPBUGS-37300)

이전에는 MCO(Machine Config Operator) 구성의 일부 링크 경로(예: `/hostroot/etc/ipsec.d/openshift.conf` 및 `hostroot/mco/internal-registry-pull-secret.json`)가 MCO 업데이트 중에 수정되었습니다. 이로 인해 업데이트 후 노드에서 파일 무결성 검사에 실패하여 사용자 환경이 중단되었습니다. 이번 업데이트를 통해 MCO 구성에서 수정된 파일 링크 경로가 업데이트되었습니다. 이제 업데이트 후 파일 무결성 검사가 전달되어 안정적인 클러스터를 보장합니다. (OCPBUGS-41628)

#### 6.2.3. OpenShift File Integrity Operator 1.3.5

OpenShift File Integrity Operator 1.3.5에서 다음 권고를 사용할 수 있습니다.

RHBA-2024:10366 OpenShift File Integrity Operator 업데이트

이번 업데이트에서는 기본 기본 이미지의 업그레이드된 종속 항목이 포함되어 있습니다.

#### 6.2.4. OpenShift File Integrity Operator 1.3.4

OpenShift File Integrity Operator 1.3.4에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2024:2946 OpenShift File Integrity Operator 버그 수정 및 개선 사항 업데이트

#### 6.2.4.1. 버그 수정

이전에는 multus 인증서 교체로 인해 File Integrity Operator에서 `NodeHasIntegrityFailure` 경고를 발행했습니다. 이번 릴리스에서는 경고 및 실패 상태가 올바르게 트리거됩니다. (OCPBUGS-31257)

#### 6.2.5. OpenShift File Integrity Operator 1.3.3

OpenShift File Integrity Operator 1.3.3에서 다음 권고를 사용할 수 있습니다.

RHBA-2023:5652 OpenShift File Integrity Operator 버그 수정 및 개선 사항 업데이트

이번 업데이트에서는 기본 종속성의 CVE를 해결합니다.

#### 6.2.5.1. 새로운 기능 및 개선 사항

FIPS 모드에서 실행되는 OpenShift Container Platform 클러스터에서 File Integrity Operator를 설치하고 사용할 수 있습니다.

중요

클러스터의 FIPS 모드를 활성화하려면 FIPS 모드에서 작동하도록 구성된 RHEL(Red Hat Enterprise Linux) 컴퓨터에서 설치 프로그램을 실행해야 합니다. RHEL에서 FIPS 모드를 구성하는 방법에 대한 자세한 내용은 RHEL을 FIPS 모드로 전환 을 참조하십시오.

FIPS 모드로 부팅된 Red Hat Enterprise Linux(RHEL) 또는 Red Hat Enterprise Linux CoreOS(RHCOS)를 실행할 때 OpenShift Container Platform 핵심 구성 요소는 x86_64, ppc64le 및 s390x 아키텍처에서만 FIPS 140-2/140-3 검증을 위해 NIST에 제출된 RHEL 암호화 라이브러리를 사용합니다.

#### 6.2.5.2. 버그 수정

이전에는 `hostPath: path: /` 볼륨 마운트와 함께 개인 기본 마운트 전파가 있는 일부 FIO Pod에서 다중 경로를 사용하는 CSI 드라이버가 손상되었습니다. 이 문제가 해결되어 CSI 드라이버가 올바르게 작동합니다. (다중자가 사용 중인 경우 CSI 볼륨 마운트 해제를 차단하는 일부 OpenShift Operator Pod

이번 업데이트에서는 CVE-2023-39325가 해결되었습니다. (CVE-2023-39325)

#### 6.2.6. OpenShift File Integrity Operator 1.3.2

OpenShift File Integrity Operator 1.3.2에서 다음 권고를 사용할 수 있습니다.

RHBA-2023:5107 OpenShift File Integrity Operator 버그 수정 업데이트

이번 업데이트에서는 기본 종속성의 CVE를 해결합니다.

#### 6.2.7. OpenShift File Integrity Operator 1.3.1

OpenShift File Integrity Operator 1.3.1에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:3600 OpenShift File Integrity Operator 버그 수정 업데이트

#### 6.2.7.1. 새로운 기능 및 개선 사항

FIO에는 이제 OpenShift Container Platform에서 관리할 때 경고 발행을 제외하고 kubelet 인증서가 기본 파일로 포함됩니다. (OCPBUGS-14348)

FIO는 이제 Red Hat 기술 지원 주소로 이메일을 올바르게 전달합니다. (OCPBUGS-5023)

#### 6.2.7.2. 버그 수정

이전에는 노드가 클러스터에서 제거될 때 FIO에서 `FileIntegrityNodeStatus` CRD를 정리하지 않았습니다. FIO가 노드 제거 시 노드 상태 CRD를 올바르게 정리하도록 업데이트되었습니다. (OCPBUGS-4321)

이전에는 FIO도 새 노드가 무결성 검사에 실패했음을 잘못 표시했습니다. FIO가 클러스터에 새 노드를 추가할 때 노드 상태 CRD를 올바르게 표시하도록 업데이트되었습니다. 올바른 노드 상태 알림을 제공합니다. (OCPBUGS-8502)

이전에는 FIO가 `FileIntegrity` CRD를 조정할 때 조정이 완료될 때까지 검사가 일시 중지되었습니다. 이로 인해 조정의 영향을 받지 않는 노드에 대한 지나치게 공격적인 재 시작 프로세스가 발생했습니다. 이 문제로 인해 머신 구성 풀에 대한 불필요한 데몬 세트로 인해 `FileIntegrity` 와 관련이 없습니다. FIO는 이러한 사례를 올바르게 처리하고 파일 무결성 변경의 영향을 받는 노드의 AIDE 스캔을 일시 중지합니다. (CMP-1097)

#### 6.2.7.3. 확인된 문제

FIO 1.3.1에서 IBM Z® 클러스터의 노드를 늘리면 파일 무결성 노드 상태가 `실패` 할 수 있습니다. 자세한 내용은 IBM Power® 클러스터에 노드 추가로 인해 파일 무결성 노드 상태가 실패할 수 있습니다.

#### 6.2.8. OpenShift File Integrity Operator 1.2.1

OpenShift File Integrity Operator 1.2.1에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:1684 OpenShift File Integrity Operator 버그 수정 업데이트

이 릴리스에는 업데이트된 컨테이너 종속 항목이 포함되어 있습니다.

#### 6.2.9. OpenShift File Integrity Operator 1.2.0

OpenShift File Integrity Operator 1.2.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:1273 OpenShift File Integrity Operator 기능 개선 업데이트

#### 6.2.9.1. 새로운 기능 및 개선 사항

이제 File Integrity Operator CR(사용자 정의 리소스)에 첫 번째 AIDE 무결성 검사를 시작하기 전에 대기할 시간(초)을 지정하는 `initialDelay` 기능이 포함되어 있습니다. 자세한 내용은 FileIntegrity 사용자 정의 리소스 생성을 참조하십시오.

File Integrity Operator가 안정되어 릴리스 채널이 `stable` 로 업그레이드되었습니다. 향후 릴리스에서는 Semantic Versioning 을 따릅니다. 최신 릴리스에 액세스하려면 File Integrity Operator 업데이트를 참조하십시오.

#### 6.2.10. OpenShift File Integrity Operator 1.0.0

OpenShift File Integrity Operator 1.0.0에 다음 권고를 사용할 수 있습니다.

RHBA-2023:0037 OpenShift File Integrity Operator 버그 수정 업데이트

#### 6.2.11. OpenShift File Integrity Operator 0.1.32

OpenShift File Integrity Operator 0.1.32에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:7095 OpenShift File Integrity Operator 버그 수정 업데이트

#### 6.2.11.1. 버그 수정

이전에는 File Integrity Operator에서 발행한 경고가 네임스페이스를 설정하지 않아 경고가 시작된 네임스페이스를 이해하기 어려웠습니다. 이제 Operator에서 적절한 네임스페이스를 설정하여 경고에 대한 자세한 정보를 제공합니다. (BZ#2112394)

이전에는 File Integrity Operator가 Operator 시작 시 메트릭 서비스를 업데이트하지 않아 지표 대상에 연결할 수 없었습니다. 이번 릴리스에서는 File Integrity Operator가 Operator 시작 시 지표 서비스가 업데이트되도록 합니다. (BZ#2115821)

#### 6.2.12. OpenShift File Integrity Operator 0.1.30

OpenShift File Integrity Operator 0.1.30에서 다음 권고를 사용할 수 있습니다.

RHBA-2022:5538 OpenShift File Integrity Operator 버그 수정 및 개선 사항 업데이트

#### 6.2.12.1. 새로운 기능 및 개선 사항

File Integrity Operator는 다음 아키텍처에서 지원됩니다.

IBM Power®

IBM Z® 및 IBM® LinuxONE

#### 6.2.12.2. 버그 수정

이전에는 File Integrity Operator에서 발행한 경고가 네임스페이스를 설정하지 않아 경고가 시작된 위치를 이해하기 어려웠습니다. 이제 Operator에서 적절한 네임스페이스를 설정하여 경고에 대한 이해가 증가합니다. (BZ#2101393)

#### 6.2.13. OpenShift File Integrity Operator 0.1.24

OpenShift File Integrity Operator 0.1.24에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:1331 OpenShift File Integrity Operator Bug Fix

#### 6.2.13.1. 새로운 기능 및 개선 사항

이제 `config.maxBackups` 특성을 사용하여 `FileIntegrity` CR(사용자 정의 리소스)에 저장된 최대 백업 수를 구성할 수 있습니다. 이 속성은 노드에서 유지할 `re-init` 프로세스에서 남아 있는 AIDE 데이터베이스 및 로그 백업의 수를 지정합니다. 구성된 번호 이외의 이전 백업이 자동으로 정리됩니다. 기본값은 5개의 백업으로 설정됩니다.

#### 6.2.13.2. 버그 수정

이전에는 0.1.21 이전 버전에서 0.1.22 이전 버전에서 Operator를 업그레이드하면 `다시 초기화` 기능이 실패할 수 있었습니다. 이로 인해 Operator가 `configMap` 리소스 레이블을 업데이트하지 못했습니다. 이제 최신 버전으로 업그레이드하면 리소스 레이블이 수정되었습니다. (BZ#2049206)

이전 버전에서는 기본 `configMap` 스크립트 콘텐츠를 실행할 때 잘못된 데이터 키가 비교되었습니다. 이로 인해 Operator 업그레이드 후 `aide-reinit` 스크립트가 제대로 업데이트되지 않아 `다시` 초기화 프로세스가 실패했습니다. 이제 `daemonSets` 가 완료될 때까지 실행되고 AIDE 데이터베이스 `다시 초기화` 프로세스가 성공적으로 실행됩니다. (BZ#2072058)

#### 6.2.14. OpenShift File Integrity Operator 0.1.22

OpenShift File Integrity Operator 0.1.22에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:0142 OpenShift File Integrity Operator Bug Fix

#### 6.2.14.1. 버그 수정

이전에는 File Integrity Operator가 설치된 시스템이 `/etc/kubernetes/aide.reinit` 파일로 인해 OpenShift Container Platform 업데이트를 중단할 수 있었습니다. 이는 `/etc/kubernetes/aide.reinit` 파일이 있지만 나중에 `ostree` 검증 전에 제거된 경우 발생했습니다. 이번 업데이트를 통해 `/etc/kubernetes/aide.reinit` 가 `/run` 디렉터리로 이동되어 OpenShift Container Platform 업데이트와 충돌하지 않습니다. (BZ#2033311)

#### 6.2.15. OpenShift File Integrity Operator 0.1.21

OpenShift File Integrity Operator 0.1.21에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2021:4631 OpenShift File Integrity Operator 버그 수정 및 개선 사항 업데이트

#### 6.2.15.1. 새로운 기능 및 개선 사항

`FileIntegrity` 검사 결과 및 처리 메트릭과 관련된 지표는 웹 콘솔의 모니터링 대시보드에 표시됩니다. 결과는 `file_integrity_operator_` 접두사로 레이블이 지정됩니다.

노드에 1초 이상 무결성 오류가 있는 경우 경고와 함께 Operator 네임스페이스 경고에 기본 `PrometheusRule` 이 제공됩니다.

다음 동적 Machine Config Operator 및 Cluster Version Operator 관련 파일 경로는 노드 업데이트 중 잘못된 긍정을 방지하기 위해 기본 AIDE 정책에서 제외됩니다.

/etc/machine-config-daemon/currentconfig

/etc/pki/ca-trust/extracted/java/cacerts

/etc/cvo/updatepayloads

/root/.kube

AIDE 데몬 프로세스는 v0.1.16보다 안정성이 향상되었으며 AIDE 데이터베이스가 초기화될 때 발생할 수 있는 오류에 더 탄력적입니다.

#### 6.2.15.2. 버그 수정

이전에는 Operator가 자동으로 업그레이드되면 오래된 데몬 세트가 제거되지 않았습니다. 이번 릴리스에서는 자동 업그레이드 중에 오래된 데몬 세트가 제거됩니다.

#### 6.2.16. 추가 리소스

File Integrity Operator 이해

#### 6.3.1. File Integrity Operator 라이프사이클

File Integrity Operator는 "Rolling Stream" Operator입니다. 즉, OpenShift Container Platform 릴리스의 비동기식으로 업데이트를 사용할 수 있습니다. 자세한 내용은 Red Hat Customer Portal의 OpenShift Operator 라이프 사이클 을 참조하십시오.

#### 6.3.2. 지원 요청

이 문서에 설명된 절차 또는 일반적으로 OpenShift Container Platform에 문제가 발생하는 경우 Red Hat 고객 포털 에 액세스하십시오.

고객 포털에서 다음을 수행할 수 있습니다.

Red Hat 제품과 관련된 기사 및 솔루션에 대한 Red Hat 지식베이스를 검색하거나 살펴볼 수 있습니다.

Red Hat 지원에 대한 지원 케이스 제출할 수 있습니다.

다른 제품 설명서에 액세스 가능합니다.

클러스터 문제를 식별하기 위해 OpenShift Cluster Manager 에서 Red Hat Lightspeed를 사용할 수 있습니다. Red Hat Lightspeed는 문제에 대한 세부 정보와 가능한 경우 문제 해결 방법에 대한 정보를 제공합니다.

이 문서를 개선하기 위한 제안이 있거나 오류를 발견한 경우 가장 관련 문서 구성 요소에 대해 Jira 문제를 제출합니다. 섹션 이름 및 OpenShift Container Platform 버전과 같은 구체적인 정보를 제공합니다.

### 6.4. File Integrity Operator 설치

중요

이 Operator가 제대로 작동하려면 모든 클러스터 노드에 동일한 릴리스 버전이 있어야 합니다. 예를 들어 RHCOS를 실행하는 노드의 경우 모든 노드에 동일한 RHCOS 버전이 있어야합니다.

#### 6.4.1. 웹 콘솔을 사용하여 File Integrity Operator 설치

사전 요구 사항

`admin` 권한이 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 Ecosystem → Software Catalog 로 이동합니다.

File Integrity Operator 를 검색한 다음 설치 를 클릭합니다.

기본 설치 모드 및 네임스페이스를 계속 선택하여 Operator가 `openshift-file-integrity` 네임스페이스에 설치되도록 합니다.

설치 를 클릭합니다.

검증

설치에 성공했는지 확인하려면 다음을 수행하십시오.

에코시스템 → 설치된 Operator 페이지로 이동합니다.

Operator가 `openshift-file-integrity` 네임스페이스에 설치되어 있고 해당 상태는 `Succeeded` 인지 확인합니다.

Operator가 성공적으로 설치되지 않은 경우 다음을 수행하십시오.

Ecosystem → Installed Operators 페이지로 이동하여 `Status` 열에 오류 또는 실패가 있는지 검사합니다.

워크로드 → Pod 페이지로 전환하고 `openshift-file-integrity` 프로젝트에서 문제를 보고하는 Pod의 로그를 확인합니다.

#### 6.4.2. CLI를 사용하여 File Integrity Operator 설치

사전 요구 사항

`admin` 권한이 있어야 합니다.

프로세스

다음을 실행하여 `Namespace` 오브젝트 YAML 파일을 생성합니다.

```shell-session
$ oc create -f <file-name>.yaml
```

```yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    openshift.io/cluster-monitoring: "true"
    pod-security.kubernetes.io/enforce: privileged
  name: openshift-file-integrity
```

1. OpenShift Container Platform 4.20에서 Pod 보안 레이블을 네임스페이스 수준에서 `privileged` 로 설정해야 합니다.

`OperatorGroup` 오브젝트 YAML 파일을 생성합니다.

```shell-session
$ oc create -f <file-name>.yaml
```

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: file-integrity-operator
  namespace: openshift-file-integrity
spec:
  targetNamespaces:
  - openshift-file-integrity
```

`Subscription` 오브젝트 YAML 파일을 생성합니다.

```shell-session
$ oc create -f <file-name>.yaml
```

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: file-integrity-operator
  namespace: openshift-file-integrity
spec:
  channel: "stable"
  installPlanApproval: Automatic
  name: file-integrity-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

검증

CSV 파일을 검사하여 설치에 성공했는지 확인합니다.

```shell-session
$ oc get csv -n openshift-file-integrity
```

File Integrity Operator가 실행 중인지 확인합니다.

```shell-session
$ oc get deploy -n openshift-file-integrity
```

#### 6.4.3. 추가 리소스

File Integrity Operator는 제한된 네트워크 환경에서 지원됩니다. 자세한 내용은 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용을 참조하십시오.

### 6.5. File Integrity Operator 업데이트

클러스터 관리자는 OpenShift Container Platform 클러스터에서 File Integrity Operator를 업데이트할 수 있습니다.

#### 6.5.1. Operator 업데이트 준비

설치된 Operator의 서브스크립션은 Operator를 추적하고 업데이트를 수신하는 업데이트 채널을 지정합니다. 업데이트 채널을 변경하여 추적을 시작하고 최신 채널에서 업데이트를 수신할 수 있습니다.

서브스크립션의 업데이트 채널 이름은 Operator마다 다를 수 있지만 이름 지정 체계는 일반적으로 지정된 Operator 내의 공통 규칙을 따릅니다. 예를 들어 채널 이름은 Operator(`1.2`, `1.3`) 또는 릴리스 빈도(`stable`, `fast`)에서 제공하는 애플리케이션의 마이너 릴리스 업데이트 스트림을 따를 수 있습니다.

참고

설치된 Operator는 현재 채널보다 오래된 채널로 변경할 수 없습니다.

Red Hat Customer Portal 랩에는 관리자가 Operator 업데이트를 준비하는 데 도움이 되는 다음 애플리케이션이 포함되어 있습니다.

Red Hat OpenShift Container Platform Operator 업데이트 정보 확인기

애플리케이션을 사용하여 Operator Lifecycle Manager 기반 Operator를 검색하고 다양한 OpenShift Container Platform 버전에서 업데이트 채널별로 사용 가능한 Operator 버전을 확인할 수 있습니다. Cluster Version Operator 기반 Operator는 포함되어 있지 않습니다.

#### 6.5.2. Operator의 업데이트 채널 변경

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

#### 6.5.3. 보류 중인 Operator 업데이트 수동 승인

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

### 6.6. File Integrity Operator 이해

File Integrity Operator는 클러스터 노드에서 파일 무결성 검사를 지속적으로 실행하는 OpenShift Container Platform Operator입니다. 이 Operator는 각 노드에서 권한 있는 AIDE(고급 침입 탐지 환경) 컨테이너를 초기화 및 실행하는 데몬 세트를 배포하여 데몬 세트 Pod 초기 실행 중 수정된 파일의 로그를 상태 오브젝트에 제공합니다.

중요

현재 RHCOS(Red Hat Enterprise Linux CoreOS) 노드만 지원됩니다.

#### 6.6.1. FileIntegrity 사용자 정의 리소스 생성

`FileIntegrity` 사용자 정의 리소스(CR) 인스턴스는 하나 이상의 노드에 대한 연속적인 파일 무결성 검사 세트를 나타냅니다.

각 `FileIntegrity` CR은 `FileIntegrity` CR 사양과 일치하는 노드에서 AIDE를 실행하는 데몬 세트에서 지원합니다.

프로세스

`worker-fileintegrity.yaml` 이라는 다음 예제 `FileIntegrity` CR을 생성하여 작업자 노드에서 검사를 활성화합니다.

```yaml
apiVersion: fileintegrity.openshift.io/v1alpha1
kind: FileIntegrity
metadata:
  name: worker-fileintegrity
  namespace: openshift-file-integrity
spec:
  nodeSelector:
      node-role.kubernetes.io/worker: ""
  tolerations:
  - key: "myNode"
    operator: "Exists"
    effect: "NoSchedule"
  config:
    name: "myconfig"
    namespace: "openshift-file-integrity"
    key: "config"
    gracePeriod: 20
    maxBackups: 5
    initialDelay: 60
  debug: false
status:
  phase: Active
```

1. 노드 검사 예약에 필요한 선택기를 정의합니다.

2. 사용자 정의 테인트가 있는 노드에 예약할 `tolerations` 를 지정합니다. 지정하지 않으면 기본 및 인프라 노드에서 실행되도록 허용하는 기본 허용 오차가 적용됩니다.

3. 사용할 AIDE 구성이 포함된 `ConfigMap` 을 정의합니다.

4. AIDE 무결성 검사 사이에 일시 중지하는 시간(초)입니다. 노드에 대한 빈번한 AIDE 검사는 리소스 집약적일 수 있으므로 간격을 더 길게 지정하는 것이 유용할 수 있습니다. 기본값은 900초(15분)입니다.

5. 노드에 유지할 최대 AIDE 데이터베이스 및 로그 백업(초기 프로세스에서 왼쪽) 수입니다. 이 번호를 초과하는 이전 백업은 데몬에 의해 자동으로 정리됩니다. 기본값은 5로 설정됩니다.

6. 첫 번째 AIDE 무결성 검사를 시작하기 전에 대기하는 시간(초)입니다. 기본값은 0입니다.

7. `FileIntegrity` 인스턴스의 실행 상태입니다. 상태가 `초기화` 됨, `보류 중` 또는 `활성 상태입니다`.

| `초기화` | `FileIntegrity` 오브젝트는 현재 AIDE 데이터베이스를 초기화하거나 다시 초기화하고 있습니다. |
| --- | --- |
| `보류 중` | `FileIntegrity` 배포가 계속 생성되고 있습니다. |
| `활성` | 검사가 활성 상태이며 진행 중입니다. |

YAML 파일을 `openshift-file-integrity` 네임스페이스에 적용합니다.

```shell-session
$ oc apply -f worker-fileintegrity.yaml -n openshift-file-integrity
```

검증

다음 명령을 실행하여 `FileIntegrity` 오브젝트가 성공적으로 생성되었는지 확인합니다.

```shell-session
$ oc get fileintegrities -n openshift-file-integrity
```

```shell-session
NAME                   AGE
worker-fileintegrity   14s
```

#### 6.6.2. FileIntegrity 사용자 정의 리소스 상태 확인

`FileIntegrity` 사용자 정의 리소스(CR)는. `status.phase` 하위 리소스를 통해 해당 상태를 보고합니다.

프로세스

`FileIntegrity` CR 상태를 쿼리하려면 다음을 실행합니다.

```shell-session
$ oc get fileintegrities/worker-fileintegrity  -o jsonpath="{ .status.phase }"
```

```shell-session
Active
```

#### 6.6.3. FileIntegrity 사용자 정의 리소스 단계

`Pending` - 사용자 정의 리소스(CR)가 생성된 후 단계입니다.

`Active` - 백업 데몬 세트가 설정되어 실행되는 단계입니다.

`Initializing` - AIDE 데이터베이스가 다시 초기화되는 단계입니다.

#### 6.6.4. FileIntegrityNodeStatuses 오브젝트 이해

`FileIntegrity` CR의 검사 결과는 `FileIntegrityNodeStatuses` 라는 다른 오브젝트에 보고됩니다.

```shell-session
$ oc get fileintegritynodestatuses
```

```shell-session
NAME                                                AGE
worker-fileintegrity-ip-10-0-130-192.ec2.internal   101s
worker-fileintegrity-ip-10-0-147-133.ec2.internal   109s
worker-fileintegrity-ip-10-0-165-160.ec2.internal   102s
```

참고

`FileIntegrityNodeStatus` 오브젝트 결과를 사용할 수 있는 데 시간이 걸릴 수 있습니다.

노드당 하나의 결과 오브젝트가 있습니다. 각 `FileIntegrityNodeStatus` 오브젝트의 `nodeName` 특성은 검사 중인 노드에 해당합니다. 파일 무결성 검사의 상태는 `results` 배열에 표시되며 여기에는 검사 조건이 포함됩니다.

```shell-session
$ oc get fileintegritynodestatuses.fileintegrity.openshift.io -ojsonpath='{.items[*].results}' | jq
```

`fileintegritynodestatus` 오브젝트는 AIDE 실행의 최신 상태를 보고하고 `status` 필드에 `Failed`, `Succeeded`, `Errored` 로 표시합니다.

```shell-session
$ oc get fileintegritynodestatuses -w
```

```shell-session
NAME                                                               NODE                                         STATUS
example-fileintegrity-ip-10-0-134-186.us-east-2.compute.internal   ip-10-0-134-186.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-150-230.us-east-2.compute.internal   ip-10-0-150-230.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-169-137.us-east-2.compute.internal   ip-10-0-169-137.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-180-200.us-east-2.compute.internal   ip-10-0-180-200.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-194-66.us-east-2.compute.internal    ip-10-0-194-66.us-east-2.compute.internal    Failed
example-fileintegrity-ip-10-0-222-188.us-east-2.compute.internal   ip-10-0-222-188.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-134-186.us-east-2.compute.internal   ip-10-0-134-186.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-222-188.us-east-2.compute.internal   ip-10-0-222-188.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-194-66.us-east-2.compute.internal    ip-10-0-194-66.us-east-2.compute.internal    Failed
example-fileintegrity-ip-10-0-150-230.us-east-2.compute.internal   ip-10-0-150-230.us-east-2.compute.internal   Succeeded
example-fileintegrity-ip-10-0-180-200.us-east-2.compute.internal   ip-10-0-180-200.us-east-2.compute.internal   Succeeded
```

#### 6.6.5. FileIntegrityNodeStatus CR 상태 유형

이러한 조건은 해당 `FileIntegrityNodeStatus` CR 상태의 결과 배열에 보고됩니다.

`Succeeded` - 무결성 검사를 통과했습니다. 데이터베이스가 마지막으로 초기화된 이후 AIDE 검사에 포함된 파일과 디렉터리가 수정되지 않았습니다.

`Failed` - 무결성 검사에 실패했습니다. 데이터베이스가 마지막으로 초기화된 이후 AIDE 검사에 포함된 일부 파일 또는 디렉터리가 수정되었습니다.

`Errored` - AIDE 스캐너에 내부 오류가 발생했습니다.

#### 6.6.5.1. FileIntegrityNodeStatus CR 성공 상태의 예

```shell-session
[
  {
    "condition": "Succeeded",
    "lastProbeTime": "2020-09-15T12:45:57Z"
  }
]
[
  {
    "condition": "Succeeded",
    "lastProbeTime": "2020-09-15T12:46:03Z"
  }
]
[
  {
    "condition": "Succeeded",
    "lastProbeTime": "2020-09-15T12:45:48Z"
  }
]
```

이 경우 세 가지 검사가 모두 성공했으며 지금까지 다른 조건이 없습니다.

#### 6.6.5.2. FileIntegrityNodeStatus CR 실패 상태의 예

실패 조건을 시뮬레이션하려면 AIDE가 추적하는 파일 중 하나를 수정하십시오. 예를 들어 작업자 노드 중 하나에서 `/etc/resolv.conf` 를 수정합니다.

```shell-session
$ oc debug node/ip-10-0-130-192.ec2.internal
```

```shell-session
Creating debug namespace/openshift-debug-node-ldfbj ...
Starting pod/ip-10-0-130-192ec2internal-debug ...
To use host binaries, run `chroot /host`
Pod IP: 10.0.130.192
If you don't see a command prompt, try pressing enter.
sh-4.2# echo "# integrity test" >> /host/etc/resolv.conf
sh-4.2# exit

Removing debug pod ...
Removing debug namespace/openshift-debug-node-ldfbj ...
```

잠시 후 해당 `FileIntegrityNodeStatus` 오브젝트의 결과 배열에 `Failed` 조건이 보고되었습니다. 이전의 `Succeeded` 조건이 유지되므로 검사가 실패한 시간을 정확히 찾을 수 있습니다.

```shell-session
$ oc get fileintegritynodestatuses.fileintegrity.openshift.io/worker-fileintegrity-ip-10-0-130-192.ec2.internal -ojsonpath='{.results}' | jq -r
```

또는 오브젝트 이름을 언급하지 않는 경우 다음을 실행합니다.

```shell-session
$ oc get fileintegritynodestatuses.fileintegrity.openshift.io -ojsonpath='{.items[*].results}' | jq
```

```shell-session
[
  {
    "condition": "Succeeded",
    "lastProbeTime": "2020-09-15T12:54:14Z"
  },
  {
    "condition": "Failed",
    "filesChanged": 1,
    "lastProbeTime": "2020-09-15T12:57:20Z",
    "resultConfigMapName": "aide-ds-worker-fileintegrity-ip-10-0-130-192.ec2.internal-failed",
    "resultConfigMapNamespace": "openshift-file-integrity"
  }
]
```

`Failed` 조건은 정확히 무엇이 실패하고 왜 실패했는지에 대한 자세한 정보를 제공하는 구성 맵을 가리킵니다.

```shell-session
$ oc describe cm aide-ds-worker-fileintegrity-ip-10-0-130-192.ec2.internal-failed
```

```shell-session
Name:         aide-ds-worker-fileintegrity-ip-10-0-130-192.ec2.internal-failed
Namespace:    openshift-file-integrity
Labels:       file-integrity.openshift.io/node=ip-10-0-130-192.ec2.internal
              file-integrity.openshift.io/owner=worker-fileintegrity
              file-integrity.openshift.io/result-log=
Annotations:  file-integrity.openshift.io/files-added: 0
              file-integrity.openshift.io/files-changed: 1
              file-integrity.openshift.io/files-removed: 0

Data

integritylog:
------
AIDE 0.15.1 found differences between database and filesystem!!
Start timestamp: 2020-09-15 12:58:15

Summary:
  Total number of files:  31553
  Added files:                0
  Removed files:            0
  Changed files:            1


---------------------------------------------------
Changed files:
---------------------------------------------------

changed: /hostroot/etc/resolv.conf

---------------------------------------------------
Detailed information about changes:
---------------------------------------------------


File: /hostroot/etc/resolv.conf
 SHA512   : sTQYpB/AL7FeoGtu/1g7opv6C+KT1CBJ , qAeM+a8yTgHPnIHMaRlS+so61EN8VOpg

Events:  <none>
```

구성 맵 데이터 크기 제한으로 인해 1MB 이상의 AIDE 로그가 실패 구성 맵에 base64로 인코딩된 gzip 아카이브로 추가됩니다. 다음 명령을 사용하여 로그를 추출합니다.

```shell-session
$ oc get cm <failure-cm-name> -o json | jq -r '.data.integritylog' | base64 -d | gunzip
```

참고

압축 로그는 구성 맵에 `file-integrity.openshift.io/compressed` 주석 키가 있는 것으로 표시됩니다.

#### 6.6.6. 이벤트 이해

`FileIntegrity` 및 `FileIntegrityNodeStatus` 오브젝트의 상태의 전환은 이벤트 에서 기록됩니다. 이벤트 생성 시간은 `Active` 로 `Initializing` 과 같은 최신 전환을 반영하며 반드시 최신 검사 결과가 반영되는 것은 아닙니다. 그러나 최신 이벤트는 항상 최근 상태를 반영합니다.

```shell-session
$ oc get events --field-selector reason=FileIntegrityStatus
```

```shell-session
LAST SEEN   TYPE     REASON                OBJECT                                MESSAGE
97s         Normal   FileIntegrityStatus   fileintegrity/example-fileintegrity   Pending
67s         Normal   FileIntegrityStatus   fileintegrity/example-fileintegrity   Initializing
37s         Normal   FileIntegrityStatus   fileintegrity/example-fileintegrity   Active
```

노드 검사에 실패하면 `add/changed/removed` 및 config map 정보를 사용하여 이벤트가 생성됩니다.

```shell-session
$ oc get events --field-selector reason=NodeIntegrityStatus
```

```shell-session
LAST SEEN   TYPE      REASON                OBJECT                                MESSAGE
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-134-173.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-168-238.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-169-175.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-152-92.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-158-144.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-131-30.ec2.internal
87m         Warning   NodeIntegrityStatus   fileintegrity/example-fileintegrity   node ip-10-0-152-92.ec2.internal has changed! a:1,c:1,r:0 \ log:openshift-file-integrity/aide-ds-example-fileintegrity-ip-10-0-152-92.ec2.internal-failed
```

추가, 변경 또는 제거된 파일의 수를 변경하면 노드 상태가 전환되지 않은 경우에도 새 이벤트가 생성됩니다.

```shell-session
$ oc get events --field-selector reason=NodeIntegrityStatus
```

```shell-session
LAST SEEN   TYPE      REASON                OBJECT                                MESSAGE
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-134-173.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-168-238.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-169-175.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-152-92.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-158-144.ec2.internal
114m        Normal    NodeIntegrityStatus   fileintegrity/example-fileintegrity   no changes to node ip-10-0-131-30.ec2.internal
87m         Warning   NodeIntegrityStatus   fileintegrity/example-fileintegrity   node ip-10-0-152-92.ec2.internal has changed! a:1,c:1,r:0 \ log:openshift-file-integrity/aide-ds-example-fileintegrity-ip-10-0-152-92.ec2.internal-failed
40m         Warning   NodeIntegrityStatus   fileintegrity/example-fileintegrity   node ip-10-0-152-92.ec2.internal has changed! a:3,c:1,r:0 \ log:openshift-file-integrity/aide-ds-example-fileintegrity-ip-10-0-152-92.ec2.internal-failed
```

#### 6.7.1. FileIntegrity 오브젝트 특성 보기

모든 Kubernetes 사용자 정의 리소스(CR)와 마찬가지로 다음 명령을 실행하면 다음을 사용하여 개별 특성을 볼 수 있습니다.

```shell
oc explain fileintegrity
```

```shell-session
$ oc explain fileintegrity.spec
```

```shell-session
$ oc explain fileintegrity.spec.config
```

#### 6.7.2. 중요한 특성

| 속성 | 설명 |
| --- | --- |
| `spec.nodeSelector` | 해당 노드에 AIDE Pod를 예약하기 위해서는 노드의 레이블과 일치해야 하는 키-값 쌍에 대한 맵입니다. 일반적인 용도는 `node-role.kubernetes.io/worker: ""` 가 모든 작업자 노드에 AIDE를 예약하고 `node.openshift.io/os_id: "rhcos"` 는 모든 RHCOS(Red Hat Enterprise Linux CoreOS) 노드에서 예약하는 단일 키-값 쌍만 설정하는 것입니다. |
| `spec.debug` | 부울 특성입니다. `true` 로 설정하면 AIDE 데몬 세트의 Pod에서 실행 중인 데몬에서 추가 정보를 출력합니다. |
| `spec.tolerations` | 사용자 정의 테인트가 있는 노드에 예약할 허용 오차를 지정합니다. 지정하지 않으면 기본 허용 오차가 적용되므로 컨트롤 플레인 노드에서 허용 오차가 실행될 수 있습니다. |
| `spec.config.gracePeriod` | AIDE 무결성 검사 사이에 일시 중지하는 시간(초)입니다. 노드에 대한 빈번한 AIDE 검사는 리소스 집약적일 수 있으므로 간격을 길게 지정하는 것이 유용할 수 있습니다. 기본값은 `900` 또는 15분입니다. |
| `maxBackups` | 노드에 보관하기 위해 `재` 초기 프로세스에서 남은 최대 AIDE 데이터베이스 및 로그 백업 수입니다. 이 번호를 초과하는 이전 백업은 데몬에 의해 자동으로 정리됩니다. |
| `spec.config.name` | 사용자 지정 AIDE 구성이 포함된 configMap의 이름입니다. 생략하면 기본 구성이 생성됩니다. |
| `spec.config.namespace` | 사용자 지정 AIDE 구성이 포함된 configMap의 네임스페이스입니다. 설정되지 않은 경우 FIO는 RHCOS 시스템에 적합한 기본 구성을 생성합니다. |
| `spec.config.key` | `이름` 및 `네임스페이스` 로 지정된 구성 맵에 실제 AIDE 구성이 포함된 키입니다. 기본값은 `aide.conf` 입니다. |
| `spec.config.initialDelay` | 첫 번째 AIDE 무결성 검사를 시작하기 전에 대기하는 시간(초)입니다. 기본값은 0입니다. 이 속성은 선택 사항입니다. |

#### 6.7.3. 기본 구성 검사

기본 File Integrity Operator 구성은 `FileIntegrity` CR과 동일한 이름으로 구성 맵에 저장됩니다.

프로세스

기본 구성을 검토하려면 다음을 실행합니다.

```shell-session
$ oc describe cm/worker-fileintegrity
```

#### 6.7.4. 기본 File Integrity Operator 구성 이해

다음은 구성 맵의 `aide.conf` 키에서 발췌한 것입니다.

```bash
@@define DBDIR /hostroot/etc/kubernetes
@@define LOGDIR /hostroot/etc/kubernetes
database=file:@@{DBDIR}/aide.db.gz
database_out=file:@@{DBDIR}/aide.db.gz
gzip_dbout=yes
verbose=5
report_url=file:@@{LOGDIR}/aide.log
report_url=stdout
PERMS = p+u+g+acl+selinux+xattrs
CONTENT_EX = sha512+ftype+p+u+g+n+acl+selinux+xattrs

/hostroot/boot/     CONTENT_EX
/hostroot/root/\..* PERMS
/hostroot/root/   CONTENT_EX
```

`FileIntegrity` 인스턴스의 기본 구성은 다음 디렉터리의 파일에 대한 적용 범위를 제공합니다.

`/root`

`/boot`

`/usr`

`/etc`

다음 디렉터리에는 적용되지 않습니다.

`/var`

`/opt`

`/etc/` 아래의 일부 OpenShift Container Platform 관련 디렉터리는 제외됩니다.

#### 6.7.5. 사용자 정의 AIDE 구성 제공

`DBDIR`, `LOGDIR`, `database`, `database_out` 과 같은 AIDE 내부 동작을 구성하는 모든 항목을 Operator에서 덮어씁니다. Operator는 무결성 변경을 확인할 모든 경로 앞에 `/hostroot/` 접두사를 추가합니다. 그러면 대부분 컨테이너화된 환경에 맞게 조정되지 않고 루트 디렉터리에서 더 쉽게 시작할 수 있는 기존 AIDE 구성이 재사용됩니다.

참고

`/hostroot` 는 AIDE를 실행하는 Pod에서 호스트의 파일 시스템을 마운트하는 디렉터리입니다. 구성을 변경하면 데이터베이스가 다시 초기화됩니다.

#### 6.7.6. 사용자 정의 File Integrity Operator 구성 정의

이 예제에서는 `worker-fileintegrity` CR에 제공된 기본 구성을 기반으로 컨트롤 플레인 노드에서 실행되는 스캐너의 사용자 정의 구성을 정의하는 데 중점을 둡니다. 이 워크플로는 데몬 세트로 실행되는 사용자 정의 소프트웨어를 배포하고 컨트롤 플레인 노드의 `/opt/mydaemon` 에 데이터를 저장하려는 경우 유용할 수 있습니다.

프로세스

기본 구성을 복사합니다.

확인 또는 제외해야 하는 파일을 사용하여 기본 구성을 편집합니다.

편집한 내용을 새 구성 맵에 저장합니다.

`spec.config` 의 특성을 통해 `FileIntegrity` 오브젝트를 새 구성 맵으로 지정합니다.

기본 구성을 추출합니다.

```shell-session
$ oc extract cm/worker-fileintegrity --keys=aide.conf
```

그러면 편집할 수 있는 `aide.conf` 라는 파일이 생성됩니다. Operator에서 경로를 후처리하는 방법을 설명하기 위해 이 예제에서는 접두사 없이 제외 디렉터리를 추가합니다.

```shell-session
$ vim aide.conf
```

```shell-session
/hostroot/etc/kubernetes/static-pod-resources
!/hostroot/etc/kubernetes/aide.*
!/hostroot/etc/kubernetes/manifests
!/hostroot/etc/docker/certs.d
!/hostroot/etc/selinux/targeted
!/hostroot/etc/openvswitch/conf.db
```

컨트롤 플레인 노드 관련 경로를 제외합니다.

```shell-session
!/opt/mydaemon/
```

다른 내용은 `/etc` 에 저장합니다.

```shell-session
/hostroot/etc/  CONTENT_EX
```

이 파일을 기반으로 구성 맵을 생성합니다.

```shell-session
$ oc create cm master-aide-conf --from-file=aide.conf
```

구성 맵을 참조하는 `FileIntegrity` CR 매니페스트를 정의합니다.

```yaml
apiVersion: fileintegrity.openshift.io/v1alpha1
kind: FileIntegrity
metadata:
  name: master-fileintegrity
  namespace: openshift-file-integrity
spec:
  nodeSelector:
      node-role.kubernetes.io/master: ""
  config:
      name: master-aide-conf
      namespace: openshift-file-integrity
```

Operator는 제공된 구성 맵 파일을 처리하고 결과를 `FileIntegrity` 오브젝트와 동일한 이름의 구성 맵에 저장합니다.

```shell-session
$ oc describe cm/master-fileintegrity | grep /opt/mydaemon
```

```shell-session
!/hostroot/opt/mydaemon
```

#### 6.7.7. 사용자 정의 파일 무결성 구성 변경

파일 무결성 구성을 변경하려면 생성된 구성 맵을 변경하지 마십시오. 대신 `spec.name`, `namespace`, `key` 특성을 통해 `FileIntegrity` 오브젝트에 연결된 구성 맵을 변경하십시오.

#### 6.8.1. 데이터베이스 다시 초기화

File Integrity Operator에서 계획된 변경을 감지하면 데이터베이스를 다시 초기화해야 할 수 있습니다.

프로세스

`file-integrity.openshift.io/re-init` 로 `FileIntegrity` 사용자 정의 리소스(CR)에 주석을 답니다.

```shell-session
$ oc annotate fileintegrities/worker-fileintegrity file-integrity.openshift.io/re-init=
```

이전 데이터베이스 및 로그 파일이 백업되고 새 데이터베이스가 초기화됩니다. 다음 명령을 사용하여 생성된 Pod의 다음 출력에서 볼 수 있듯이 이전 데이터베이스 및 로그는 `/ etc/kubernetes` 아래의 노드에 보관됩니다.

```shell
oc debug
```

```shell-session
ls -lR /host/etc/kubernetes/aide.*
-rw-------. 1 root root 1839782 Sep 17 15:08 /host/etc/kubernetes/aide.db.gz
-rw-------. 1 root root 1839783 Sep 17 14:30 /host/etc/kubernetes/aide.db.gz.backup-20200917T15_07_38
-rw-------. 1 root root   73728 Sep 17 15:07 /host/etc/kubernetes/aide.db.gz.backup-20200917T15_07_55
-rw-r--r--. 1 root root       0 Sep 17 15:08 /host/etc/kubernetes/aide.log
-rw-------. 1 root root     613 Sep 17 15:07 /host/etc/kubernetes/aide.log.backup-20200917T15_07_38
-rw-r--r--. 1 root root       0 Sep 17 15:07 /host/etc/kubernetes/aide.log.backup-20200917T15_07_55
```

일부 레코드 영구성을 제공하기 위해 결과 구성 맵은 `FileIntegrity` 오브젝트에 속하지 않으므로 수동 정리가 필요합니다. 그 결과 `FileIntegrityNodeStatus` 오브젝트에 이전의 무결성 실패가 계속 표시됩니다.

#### 6.8.2. 머신 구성 통합

OpenShift Container Platform 4에서 클러스터 노드 구성은 `MachineConfig` 오브젝트를 통해 제공됩니다. `MachineConfig` 오브젝트로 인해 파일 변경이 예상되며 이러한 변경으로 파일 무결성 검사가 실패하지 않아야 합니다. `MachineConfig` 오브젝트 업데이트로 인한 파일 변경을 억제하기 위해 File Integrity Operator에서 노드 오브젝트를 감시합니다. 노드가 업데이트될 때 업데이트 기간 동안 AIDE 검사가 일시 중단됩니다. 업데이트가 완료되면 데이터베이스가 다시 초기화되고 검사가 다시 시작됩니다.

이러한 일시 중지 및 재개 논리는 노드 오브젝트 주석에 반영되므로 `MachineConfig` API를 통한 업데이트에만 적용됩니다.

#### 6.8.3. 데몬 세트 탐색

각 `FileIntegrity` 오브젝트는 여러 노드에 대한 검사를 나타냅니다. 검사 자체는 데몬 세트에서 관리하는 Pod에서 수행합니다.

`FileIntegrity` 오브젝트를 나타내는 데몬 세트를 찾으려면 다음을 실행하십시오.

```shell-session
$ oc -n openshift-file-integrity get ds/aide-worker-fileintegrity
```

해당 데몬 세트의 Pod를 나열하려면 다음을 실행합니다.

```shell-session
$ oc -n openshift-file-integrity get pods -lapp=aide-worker-fileintegrity
```

단일 AIDE Pod의 로그를 보려면 Pod 중 하나에서 다음 명령을 호출합니다.

```shell
oc logs
```

```shell-session
$ oc -n openshift-file-integrity logs pod/aide-worker-fileintegrity-mr8x6
```

```shell-session
Starting the AIDE runner daemon
initializing AIDE db
initialization finished
running aide check
...
```

AIDE 데몬에서 생성한 구성 맵은 보관되지 않으며 File Integrity Operator에서 처리한 후 삭제됩니다. 그러나 실패 및 오류 시에는 이러한 구성 맵의 내용이 `FileIntegrityNodeStatus` 오브젝트가 가리키는 구성 맵에 복사됩니다.

#### 6.9.1. 일반 문제 해결

문제

File Integrity Operator의 일반적인 문제를 해결하려고 합니다.

해결

`FileIntegrity` 오브젝트에서 디버그 플래그를 활성화합니다. `debug` 플래그를 사용하면 `DaemonSet` Pod에서 실행되며 AIDE 검사를 실행하는 데몬의 상세 수준이 높아집니다.

#### 6.9.2. AIDE 구성 확인

문제

AIDE 구성을 확인하려고 합니다.

해결

AIDE 구성은 `FileIntegrity` 오브젝트와 동일한 이름으로 구성 맵에 저장됩니다. 모든 AIDE 구성의 구성 맵에는 `file-integrity.openshift.io/aide-conf` 레이블이 지정됩니다.

#### 6.9.3. FileIntegrity 오브젝트의 단계 확인

문제

`FileIntegrity` 오브젝트가 있는지 파악하고 현재 상태를 확인하려고 합니다.

해결

`FileIntegrity` 오브젝트의 현재 상태를 보려면 다음을 실행합니다.

```shell-session
$ oc get fileintegrities/worker-fileintegrity  -o jsonpath="{ .status }"
```

`FileIntegrity` 오브젝트와 백업 데몬 세트가 생성되면 상태가 `Active` 로 전환되어야 합니다. 그러지 않으면 Operator Pod 로그를 확인하십시오.

#### 6.9.4. 데몬 세트의 Pod가 예상 노드에서 실행 중인지 확인

문제

데몬 세트가 존재하고 해당 Pod가 실행되어야 하는 노드에서 실행되고 있는지 확인하려고 합니다.

해결

다음을 실행합니다.

```shell-session
$ oc -n openshift-file-integrity get pods -lapp=aide-worker-fileintegrity
```

참고

`-owide` 추가에는 Pod가 실행 중인 노드의 IP 주소가 포함됩니다.

데몬 Pod의 로그를 확인하려면 다음 명령을 실행합니다.

```shell
oc logs
```

AIDE 명령의 반환 값을 확인하여 검사가 통과 또는 실패했는지 확인하십시오.

### 6.10. File Integrity Operator 설치 제거

OpenShift Container Platform 웹 콘솔을 사용하여 클러스터에서 File Integrity Operator를 제거할 수 있습니다.

#### 6.10.1. 웹 콘솔을 사용하여 File Integrity Operator 설치 제거

File Integrity Operator를 제거하려면 먼저 모든 네임스페이스에서 `FileIntegrity` 오브젝트를 삭제해야 합니다. 오브젝트가 제거된 후 Operator 및 해당 네임스페이스를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하는 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

File Integrity Operator가 설치되어 있습니다.

프로세스

Ecosystem → 설치된 Operators → File Integrity Operator 페이지로 이동합니다.

File Integrity 탭에서 Show operands in: All namespaces default option is selected to list all `FileIntegrity` objects in all namespaces.

옵션 메뉴

를 클릭한 다음 FileIntegrity 삭제를 클릭하여 `FileIntegrity 오브젝트를 삭제합니다`. 모든 `FileIntegrity` 오브젝트가 삭제되었는지 확인합니다.

관리 → 에코시스템 → 설치된 Operator 페이지로 이동합니다.

File Integrity Operator 항목에서 옵션 메뉴

를 클릭하고 Operator 설치 제거를 선택합니다.

홈 → 프로젝트 페이지로 이동합니다.

`openshift-file-integrity` 를 검색합니다.

openshift-file-integrity 프로젝트 항목의 옵션 메뉴

를 클릭한 다음 프로젝트 삭제 를 클릭합니다. 웹 콘솔에서 프로젝트 삭제 대화 상자가 열립니다.

검증

프로젝트 삭제 대화 상자에 `openshift-file-integrity` 를 입력한 다음 삭제 버튼을 클릭합니다.

### 7.1. Security Profiles Operator 개요

OpenShift Container Platform Security Profiles Operator(SPO)는 보안 컴퓨팅(seccomp) 프로필 및 SELinux 프로필을 사용자 지정 리소스로 정의하여 지정된 네임스페이스의 모든 노드에 프로필을 동기화하는 방법을 제공합니다. 최신 업데이트는 릴리스 노트 를 참조하십시오.

SPO는 조정 루프를 통해 프로필을 최신 상태로 유지하는 동안 각 노드에 사용자 정의 리소스를 배포할 수 있습니다. Security Profiles Operator 이해를 참조하십시오.

SPO는 네임스페이스가 지정된 워크로드에 대한 SELinux 정책 및 seccomp 프로필을 관리합니다. 자세한 내용은 Security Profiles Operator 활성화를 참조하십시오.

seccomp 및 SELinux 프로필을 생성하고, 정책을 Pod에 바인딩하고, 워크로드를 기록하며, 네임스페이스의 모든 작업자 노드를 동기화할 수 있습니다.

Advanced Security Profile Operator 작업을 사용하여 로그 강화를 활성화하거나 Webhook 및 메트릭을 구성하거나 프로필을 단일 네임스페이스로 제한합니다.

필요에 따라 Security Profiles Operator 의 문제를 해결하거나 Red Hat 지원에 참여하십시오.

Operator 를 제거하기 전에 프로필을 제거하여 Security Profiles Operator 를 설치 제거할 수 있습니다.

### 7.2. Security Profiles Operator 릴리스 노트

Security Profiles Operator는 보안 컴퓨팅(seccomp) 및 SELinux 프로필을 사용자 정의 리소스로 정의하여 지정된 네임스페이스의 모든 노드에 프로필을 동기화하는 방법을 제공합니다.

이 릴리스 노트에서는 OpenShift Container Platform의 Security Profiles Operator 개발을 추적합니다.

Security Profiles Operator 개요는 Security Profiles Operator 개요 를 참조하십시오.

#### 7.2.1. Security Profiles Operator 0.9.0

Security Profiles Operator 0.9.0에 대해 다음 권고를 사용할 수 있습니다. RHBA-2025:15655 - OpenShift Security Profiles Operator 업데이트

이번 업데이트에서는 보안 프로필을 네임스페이스 리소스가 아닌 클러스터 전체 리소스로 관리합니다. Security Profiles Operator를 0.8.6 이후 버전으로 업데이트하려면 수동 마이그레이션이 필요합니다. 마이그레이션 지침은 Security Profiles Operator 0.9.0 업데이트 마이그레이션 가이드를 참조하십시오.

#### 7.2.1.1. 버그 수정

이번 업데이트 이전에는 semanage 구성 파일을 구문 분석하는 동안 오류로 인해 spod Pod가 시작되고 `CrashLoopBackOff` 상태가 될 수 있었습니다. 이 문제는 OpenShift Container Platform 4.19부터 RHEL 9 이미지 이름 지정 규칙을 변경했기 때문에 발생합니다. (OCPBUGS-55829)

이번 업데이트 이전에는 조정기 유형 불일치 오류로 인해 Security Profiles Operator가 새 추가된 노드에 `RawSelinuxProfile` 을 적용하지 못했습니다. 이번 업데이트를 통해 이제 Operator에서 `RawSelinuxProfile` 오브젝트를 올바르게 처리하고 정책이 모든 노드에 예상대로 적용됩니다. (OCPBUGS-33718)

#### 7.2.2. Security Profiles Operator 0.8.6

Security Profiles Operator 0.8.6에 대한 다음 권고를 사용할 수 있습니다.

RHBA-2024:10380 - OpenShift Security Profiles Operator 업데이트

이번 업데이트에서는 기본 기본 이미지의 업그레이드된 종속 항목이 포함되어 있습니다.

#### 7.2.3. Security Profiles Operator 0.8.5

Security Profiles Operator 0.8.5에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2024:5016 - OpenShift Security Profiles Operator 버그 수정 업데이트

#### 7.2.3.1. 버그 수정

웹 콘솔에서 Security Profile Operator를 설치하려고 할 때 네임스페이스에 Operator 권장 클러스터 모니터링을 활성화하는 옵션을 사용할 수 없었습니다. 이번 업데이트를 통해 네임스페이스에서 Operator-recommend 클러스터 모니터링을 활성화할 수 있습니다. (OCPBUGS-37794)

이전에는 OperatorHub에 Security Profiles Operator가 간헐적으로 표시되지 않아 웹 콘솔을 통해 Operator를 설치할 수 있는 제한된 액세스 권한이 있었습니다. 이번 업데이트를 통해 OperatorHub에 Security Profiles Operator가 표시됩니다.

#### 7.2.4. Security Profiles Operator 0.8.4

Security Profiles Operator 0.8.4에 대한 다음 권고를 사용할 수 있습니다.

RHBA-2024:4781 - OpenShift Security Profiles Operator 버그 수정 업데이트

이번 업데이트에서는 기본 종속 항목의 CVE를 해결합니다.

#### 7.2.4.1. 새로운 기능 및 개선 사항

와일드카드를 설정하여 `ProfileBinding` 오브젝트의 `image` 속성에 기본 보안 프로필을 지정할 수 있습니다. 자세한 내용은 SELinux(ProfileBindings)를 사용하여 프로필로 워크로드를 프로필로 바인딩하고 워크로드를 ProfileBindings(Seccomp)를 사용하여 프로필에 바인딩합니다.

#### 7.2.5. Security Profiles Operator 0.8.2

Security Profiles Operator 0.8.2에 대한 다음 권고를 사용할 수 있습니다.

RHBA-2023:5958 - OpenShift Security Profiles Operator 버그 수정 업데이트

#### 7.2.5.1. 버그 수정

이전에는 `SELinuxProfile` 오브젝트가 동일한 네임스페이스의 사용자 지정 속성을 상속하지 않았습니다. 이번 업데이트를 통해 문제가 해결되었으며 `SELinuxProfile` 오브젝트 속성이 예상대로 동일한 네임스페이스에서 상속됩니다. (OCPBUGS-17164)

이전에는 RawSELinuxProfiles가 생성 프로세스 중에 중단되었으며 `설치된` 상태에 도달하지 못했습니다. 이번 업데이트를 통해 문제가 해결되었으며 RawSELinuxProfiles가 성공적으로 생성됩니다. (OCPBUGS-19744)

이전 버전에서는 `enableLogEnricher` 를 `true` 로 패치하면 `seccompProfile`

`log-enricher-trace` Pod가 `Pending` 상태가 되었습니다. 이번 업데이트를 통해 `log-enricher-trace` Pod가 예상대로 `설치된` 상태에 도달합니다. (OCPBUGS-22182)

이전에는 Security Profiles Operator에서 높은 카디널리티 메트릭을 생성했기 때문에 많은 양의 메모리를 사용하는 Prometheus Pod가 발생했습니다. 이번 업데이트를 통해 Security Profiles Operator 네임스페이스에 다음 메트릭이 더 이상 적용되지 않습니다.

`rest_client_request_duration_seconds`

`rest_client_request_size_bytes`

`rest_client_response_size_bytes`

(OCPBUGS-22406)

#### 7.2.6. Security Profiles Operator 0.8.0

Security Profiles Operator 0.8.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:4689 - OpenShift Security Profiles Operator 버그 수정 업데이트

#### 7.2.6.1. 버그 수정

이전에는 연결이 끊긴 클러스터에 Security Profiles Operator를 설치하는 동안 SHA 재레이블 문제로 인해 제공된 보안 해시가 올바르지 않았습니다. 이번 업데이트를 통해 SHA는 연결이 끊긴 환경에서 일관되게 작동합니다. (OCPBUGS-14404)

#### 7.2.7. Security Profiles Operator Cryostat.1

Security Profiles Operator Cryostat.1에 대해 다음 권고를 사용할 수 있습니다.

RHSA-2023:2029 - OpenShift Security Profiles Operator 버그 수정 업데이트

#### 7.2.7.1. 새로운 기능 및 개선 사항

SPO(Security Profiles Operator)는 RHEL 8 및 9 기반 RHCOS 시스템에 적합한 `selinuxd` 이미지를 자동으로 선택합니다.

중요

연결이 끊긴 환경의 이미지를 미러링하는 사용자는 Security Profiles Operator에서 제공하는 `selinuxd` 이미지를 모두 미러링해야 합니다.

이제 `spod` 데몬 내부에서 메모리 최적화를 활성화할 수 있습니다. 자세한 내용은 spod 데몬에서 메모리 최적화 활성화를 참조하십시오.

참고

SPO 메모리 최적화는 기본적으로 활성화되어 있지 않습니다.

이제 데몬 리소스 요구 사항을 구성할 수 있습니다. 자세한 내용은 데몬 리소스 요구 사항 사용자 지정을 참조하십시오.

이제 `spod` 구성에서 우선순위 클래스 이름을 구성할 수 있습니다. 자세한 내용은 spod 데몬 Pod의 사용자 정의 우선순위 클래스 이름 설정을 참조하십시오.

#### 7.2.7.2. 사용되지 않거나 삭제된 기능

기본 `nginx-1.19.1` seccomp 프로필이 이제 Security Profiles Operator 배포에서 제거됩니다.

#### 7.2.7.3. 버그 수정

이전에는 SPO(Security Profiles Operator) SELinux 정책이 컨테이너 템플릿의 하위 수준 정책 정의를 상속하지 않았습니다. net_container와 같은 다른 템플릿을 선택한 경우 컨테이너 템플릿에만 존재하는 하위 수준 정책 정의가 필요하기 때문에 정책이 작동하지 않습니다. 이 문제는 SPO SELinux 정책이 SPO 사용자 지정 형식에서 CIL(Common Intermediate Language) 형식으로 SELinux 정책을 변환하려고 할 때 발생했습니다. 이번 업데이트를 통해 컨테이너 템플릿은 SPO에서 CIL로의 변환이 필요한 모든 SELinux 정책에 추가됩니다. 또한 SPO SELinux 정책은 지원되는 모든 정책 템플릿에서 하위 수준 정책 정의를 상속할 수 있습니다. (OCPBUGS-12879)

#### 7.2.7.4. 알려진 문제

Security Profiles Operator를 설치 제거할 때 `MutatingWebhookConfiguration` 오브젝트는 삭제되지 않으며 수동으로 제거해야 합니다. 이 문제를 해결하려면 Security Profiles Operator를 설치 제거한 후 `MutatingWebhookConfiguration` 오브젝트를 삭제합니다. 이러한 단계는 Security Profiles Operator 설치 제거에서 정의됩니다. (OCPBUGS-4687)

#### 7.2.8. Security Profiles Operator 0.5.2

Security Profiles Operator 0.5.2에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2023:0788 - OpenShift Security Profiles Operator 버그 수정 업데이트

이번 업데이트에서는 기본 종속성의 CVE를 해결합니다.

#### 7.2.8.1. 알려진 문제

Security Profiles Operator를 설치 제거할 때 `MutatingWebhookConfiguration` 오브젝트는 삭제되지 않으며 수동으로 제거해야 합니다. 이 문제를 해결하려면 Security Profiles Operator를 설치 제거한 후 `MutatingWebhookConfiguration` 오브젝트를 삭제합니다. 이러한 단계는 Security Profiles Operator 설치 제거에서 정의됩니다. (OCPBUGS-4687)

#### 7.2.9. Security Profiles Operator 0.5.0

Security Profiles Operator 0.5.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2022:8762 - OpenShift Security Profiles Operator 버그 수정 업데이트

#### 7.2.9.1. 알려진 문제

Security Profiles Operator를 설치 제거할 때 `MutatingWebhookConfiguration` 오브젝트는 삭제되지 않으며 수동으로 제거해야 합니다. 이 문제를 해결하려면 Security Profiles Operator를 설치 제거한 후 `MutatingWebhookConfiguration` 오브젝트를 삭제합니다. 이러한 단계는 Security Profiles Operator 설치 제거에서 정의됩니다. (OCPBUGS-4687)

#### 7.3.1. Security Profiles Operator 라이프사이클

Security Profiles Operator는 "Rolling Stream" Operator입니다. 즉, OpenShift Container Platform 릴리스의 비동기식으로 업데이트를 사용할 수 있습니다. 자세한 내용은 Red Hat Customer Portal의 OpenShift Operator 라이프 사이클 을 참조하십시오.

#### 7.3.2. 지원 요청

이 문서에 설명된 절차 또는 일반적으로 OpenShift Container Platform에 문제가 발생하는 경우 Red Hat 고객 포털 에 액세스하십시오.

고객 포털에서 다음을 수행할 수 있습니다.

Red Hat 제품과 관련된 기사 및 솔루션에 대한 Red Hat 지식베이스를 검색하거나 살펴볼 수 있습니다.

Red Hat 지원에 대한 지원 케이스 제출할 수 있습니다.

다른 제품 설명서에 액세스 가능합니다.

클러스터 문제를 식별하기 위해 OpenShift Cluster Manager 에서 Red Hat Lightspeed를 사용할 수 있습니다. Red Hat Lightspeed는 문제에 대한 세부 정보와 가능한 경우 문제 해결 방법에 대한 정보를 제공합니다.

이 문서를 개선하기 위한 제안이 있거나 오류를 발견한 경우 가장 관련 문서 구성 요소에 대해 Jira 문제를 제출합니다. 섹션 이름 및 OpenShift Container Platform 버전과 같은 구체적인 정보를 제공합니다.

### 7.4. Security Profiles Operator 이해

OpenShift Container Platform 관리자는 Security Profiles Operator를 사용하여 클러스터에서 향상된 보안 조치를 정의할 수 있습니다.

중요

Security Profiles Operator는 RHCOS(Red Hat Enterprise Linux CoreOS) 작업자 노드만 지원합니다. RHEL(Red Hat Enterprise Linux) 노드는 지원되지 않습니다.

#### 7.4.1. 보안 프로필 정보

보안 프로필은 클러스터의 컨테이너 수준에서 보안을 강화할 수 있습니다.

seccomp 보안 프로필은 프로세스에서 수행할 수 있는 syscall을 나열합니다. 권한은 SELinux보다 광범위하므로 사용자는 `쓰기` 와 같은 운영 체제 전체에서 작업을 제한할 수 있습니다.

SELinux 보안 프로필은 시스템의 프로세스, 애플리케이션 또는 파일의 액세스 및 사용을 제한하는 레이블 기반 시스템을 제공합니다. 환경의 모든 파일에는 권한을 정의하는 레이블이 있습니다. SELinux 프로필은 디렉터리와 같은 지정된 구조 내에서 액세스를 정의할 수 있습니다.

### 7.5. Security Profiles Operator 활성화

Security Profiles Operator를 사용하려면 먼저 Operator가 클러스터에 배포되었는지 확인해야 합니다.

중요

이 Operator가 제대로 작동하려면 모든 클러스터 노드에 동일한 릴리스 버전이 있어야 합니다. 예를 들어 RHCOS를 실행하는 노드의 경우 모든 노드에 동일한 RHCOS 버전이 있어야합니다.

중요

Security Profiles Operator는 RHCOS(Red Hat Enterprise Linux CoreOS) 작업자 노드만 지원합니다. RHEL(Red Hat Enterprise Linux) 노드는 지원되지 않습니다.

중요

Security Profiles Operator는 `x86_64` 및 `ppc64le` 아키텍처를 지원합니다.

#### 7.5.1. Security Profiles Operator 설치

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 웹 콘솔에 액세스할 수 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 Ecosystem → Software Catalog 로 이동합니다.

Security Profiles Operator를 검색한 다음 설치를 클릭합니다.

기본 설치 모드 및 네임스페이스 를 계속 선택하여 Operator가 `openshift-security-profiles` 네임스페이스에 설치되도록 합니다.

설치 를 클릭합니다.

검증

설치에 성공했는지 확인하려면 다음을 수행하십시오.

에코시스템 → 설치된 Operator 페이지로 이동합니다.

Security Profiles Operator가 `openshift-security-profiles` 네임스페이스에 설치되어 있고 해당 상태가 `Succeeded` 인지 확인합니다.

Operator가 성공적으로 설치되지 않은 경우 다음을 수행하십시오.

Ecosystem → Installed Operators 페이지로 이동하여 `Status` 열에 오류 또는 실패가 있는지 검사합니다.

워크로드 → Pod 페이지로 이동하여 `openshift-security-profiles` 프로젝트에서 문제를 보고하는 Pod의 로그를 확인합니다.

#### 7.5.2. CLI를 사용하여 Security Profiles Operator 설치

사전 요구 사항

`cluster-admin` 권한이 있어야 합니다.

프로세스

`Namespace` 오브젝트를 정의합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
    name: openshift-security-profiles
labels:
  openshift.io/cluster-monitoring: "true"
```

`Namespace` 오브젝트를 생성합니다.

```shell-session
$ oc create -f namespace-object.yaml
```

`OperatorGroup` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: security-profiles-operator
  namespace: openshift-security-profiles
```

`OperatorGroup` 개체를 생성합니다.

```shell-session
$ oc create -f operator-group-object.yaml
```

`Subscription` 오브젝트를 정의합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: security-profiles-operator-sub
  namespace: openshift-security-profiles
spec:
  channel: release-alpha-rhel-8
  installPlanApproval: Automatic
  name: security-profiles-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

`Subscription` 오브젝트를 생성합니다.

```shell-session
$ oc create -f subscription-object.yaml
```

참고

글로벌 스케줄러 기능을 설정하고 `defaultNodeSelector` 를 활성화하는 경우 네임스페이스를 수동으로 생성하고 `openshift-security-profiles` 네임스페이스의 주석을 업데이트하거나 `openshift.io/node-selector: ""` 를 사용하여 Security Profiles Operator가 설치된 네임스페이스를 업데이트해야 합니다. 이렇게 하면 기본 노드 선택기가 제거되고 배포 실패가 발생하지 않습니다.

검증

다음 CSV 파일을 검사하여 설치에 성공했는지 확인합니다.

```shell-session
$ oc get csv -n openshift-security-profiles
```

다음 명령을 실행하여 Security Profiles Operator가 작동하는지 확인합니다.

```shell-session
$ oc get deploy -n openshift-security-profiles
```

#### 7.5.3. 로깅 상세 정보 표시 구성

Security Profiles Operator는 기본 로깅 상세 정보 표시 수준을 `0` 으로 지원하며 `1` 의 향상된 상세 정보 표시 수준을 지원합니다.

프로세스

향상된 로깅 상세 정보를 활성화하려면 다음 명령을 실행하여 `spod` 구성을 패치하고 값을 조정합니다.

```shell-session
$ oc -n openshift-security-profiles patch spod \
    spod --type=merge -p '{"spec":{"verbosity":1}}'
```

```shell-session
securityprofilesoperatordaemon.security-profiles-operator.x-k8s.io/spod patched
```

### 7.6. seccomp 프로필 관리

seccomp 프로필을 생성 및 관리하고 워크로드에 바인딩합니다.

중요

Security Profiles Operator는 RHCOS(Red Hat Enterprise Linux CoreOS) 작업자 노드만 지원합니다. RHEL(Red Hat Enterprise Linux) 노드는 지원되지 않습니다.

#### 7.6.1. seccomp 프로필 생성

`SeccompProfile` 오브젝트를 사용하여 프로필을 생성합니다.

`seccompProfile` 오브젝트는 컨테이너 내에서 syscall을 제한하여 애플리케이션 액세스를 제한할 수 있습니다.

프로세스

다음 명령을 실행하여 프로젝트를 생성합니다.

```shell-session
$ oc new-project my-namespace
```

`SeccompProfile` 오브젝트를 생성합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1beta1
kind: SeccompProfile
metadata:
  name: profile1
spec:
  defaultAction: SCMP_ACT_LOG
```

seccomp 프로필은 `/var/lib/kubelet/seccomp/operator/<namespace>/<name>.json` 에 저장됩니다.

`init` 컨테이너는 Security Profiles Operator의 루트 디렉터리를 생성하여 `root` 그룹 또는 사용자 ID 권한 없이 Operator를 실행합니다. rootless 프로필 스토리지 `/var/lib/openshift-security-profiles` 에서 kubelet 루트 루트 `/var/lib/kubelet/seccomp/operator` 내부의 기본 `seccomp` 루트 경로에 대한 심볼릭 링크가 생성됩니다.

#### 7.6.2. Pod에 seccomp 프로필 적용

생성된 프로필 중 하나를 적용할 Pod를 생성합니다.

프로세스

`securityContext` 를 정의하는 Pod 오브젝트를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: Localhost
      localhostProfile: operator/profile1.json
  containers:
    - name: test-container
      image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
```

다음 명령을 실행하여 `seccompProfile.localhostProfile` 속성의 프로필 경로를 확인합니다.

```shell-session
$ oc get seccompprofile profile1 --output wide
```

```shell-session
NAME       STATUS     AGE   SECCOMPPROFILE.LOCALHOSTPROFILE
profile1   Installed  14s   operator/profile1.json
```

다음 명령을 실행하여 localhost 프로필의 경로를 확인합니다.

```shell-session
$ oc get sp profile1 --output=jsonpath='{.status.localhostProfile}'
```

```shell-session
operator/profile1.json
```

`localhostProfile` 출력을 패치 파일에 적용합니다.

```yaml
spec:
  template:
    spec:
      securityContext:
        seccompProfile:
          type: Localhost
          localhostProfile: operator/profile1.json
```

다음 명령을 실행하여 `Deployment` 오브젝트와 같은 다른 워크로드에 프로필을 적용합니다.

```shell-session
$ oc -n my-namespace patch deployment myapp --patch-file patch.yaml --type=merge
```

```shell-session
deployment.apps/myapp patched
```

검증

다음 명령을 실행하여 프로필이 올바르게 적용되었는지 확인합니다.

```shell-session
$ oc -n my-namespace get deployment myapp --output=jsonpath='{.spec.template.spec.securityContext}' | jq .
```

```plaintext
{
  "seccompProfile": {
    "localhostProfile": "operator/profile1.json",
    "type": "localhost"
  }
}
```

#### 7.6.2.1. ProfileBindings를 사용하여 프로필에 워크로드 바인딩

`ProfileBinding` 리소스를 사용하여 보안 프로필을 컨테이너의 `SecurityContext` 에 바인딩할 수 있습니다.

프로세스

`quay.io/security-profiles-operator/test-nginx-unprivileged:1.21` 이미지를 사용하는 Pod를 `SeccompProfile` 프로필 예제에 바인딩하려면 Pod 및 `SeccompProfile` 오브젝트를 사용하여 동일한 네임스페이스에 `ProfileBinding` 오브젝트를 생성합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha1
kind: ProfileBinding
metadata:
  namespace: my-namespace
  name: nginx-binding
spec:
  profileRef:
    kind: SeccompProfile
    name: profile
  image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
```

1. `kind:` 변수는 프로필의 종류를 나타냅니다.

2. `name:` 변수는 프로필의 이름을 나타냅니다.

3. 이미지 특성에서 와일드카드를 사용하여 기본 보안 프로필을 활성화할 수 있습니다. `image: "*"`

중요

`image: "*"` 와일드카드 속성을 사용하면 모든 새 Pod가 지정된 네임스페이스의 기본 보안 프로필로 바인딩됩니다.

다음 명령을 실행하여 `enable-binding=true` 로 네임스페이스에 레이블을 지정합니다.

```shell-session
$ oc label ns my-namespace spo.x-k8s.io/enable-binding=true
```

`test-pod.yaml` 이라는 Pod를 정의합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: test-container
    image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
```

Pod를 생성합니다.

```shell-session
$ oc create -f test-pod.yaml
```

참고

Pod가 이미 존재하는 경우 바인딩이 제대로 작동하려면 Pod를 다시 생성해야 합니다.

검증

다음 명령을 실행하여 Pod가 `ProfileBinding` 을 상속하는지 확인합니다.

```shell-session
$ oc get pod test-pod -o jsonpath='{.spec.containers[*].securityContext.seccompProfile}'
```

```shell-session
{"localhostProfile":"operator/profile.json","type":"Localhost"}
```

#### 7.6.3. 워크로드의 프로필 기록

Security Profiles Operator는 `ProfileRecording` 오브젝트를 사용하여 시스템 호출을 기록할 수 있으므로 애플리케이션에 대한 기본 프로필을 더 쉽게 생성할 수 있습니다.

seccomp 프로필 기록에 로그 강화기를 사용하는 경우 로그 강화 기능이 활성화되었는지 확인합니다. 자세한 내용은 추가 리소스 를 참조하십시오.

참고

`privileged: true` security context restraints가 있는 컨테이너는 로그 기반 기록을 방지합니다. 권한 있는 컨테이너는 seccomp 정책의 영향을 받지 않으며 로그 기반 레코딩은 특수 seccomp 프로필을 사용하여 이벤트를 기록합니다.

프로세스

다음 명령을 실행하여 프로젝트를 생성합니다.

```shell-session
$ oc new-project my-namespace
```

다음 명령을 실행하여 `enable-recording=true` 로 네임스페이스에 레이블을 지정합니다.

```shell-session
$ oc label ns my-namespace spo.x-k8s.io/enable-recording=true
```

`recorder: logs` 변수를 포함하는 `ProfileRecording` 오브젝트를 생성합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha1
kind: ProfileRecording
metadata:
  namespace: my-namespace
  name: test-recording
spec:
  kind: SeccompProfile
  recorder: logs
  podSelector:
    matchLabels:
      app: my-app
```

기록할 워크로드를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  namespace: my-namespace
  name: my-pod
  labels:
    app: my-app
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: nginx
      image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
      ports:
        - containerPort: 8080
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
    - name: redis
      image: quay.io/security-profiles-operator/redis:6.2.1
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
```

다음 명령을 입력하여 Pod가 `Running` 상태인지 확인합니다.

```shell-session
$ oc -n my-namespace get pods
```

```shell-session
NAME     READY   STATUS    RESTARTS   AGE
my-pod   2/2     Running   0          18s
```

강화자가 해당 컨테이너에 대한 감사 로그를 수신하는지 확인합니다.

```shell-session
$ oc -n openshift-security-profiles logs --since=1m --selector name=spod -c log-enricher
```

```shell-session
I0523 14:19:08.747313  430694 enricher.go:445] log-enricher "msg"="audit" "container"="redis" "executable"="/usr/local/bin/redis-server" "namespace"="my-namespace" "node"="xiyuan-23-5g2q9-worker-eastus2-6rpgf" "pid"=656802 "pod"="my-pod" "syscallID"=0 "syscallName"="read" "timestamp"="1684851548.745:207179" "type"="seccomp"
```

검증

Pod를 제거합니다.

```shell-session
$ oc -n my-namespace delete pod my-pod
```

Security Profiles Operator가 두 seccomp 프로필을 조정하는지 확인합니다.

```shell-session
$ oc get seccompprofiles -lspo.x-k8s.io/recording-id=test-recording
```

```shell-session
NAME                   STATUS      AGE
test-recording-nginx   Installed   2m48s
test-recording-redis   Installed   2m48s
```

#### 7.6.3.1. 컨테이너당 프로필 인스턴스 병합

기본적으로 각 컨테이너 인스턴스는 별도의 프로필에 저장됩니다. Security Profiles Operator는 컨테이너별 프로필을 단일 프로필에 병합할 수 있습니다. 프로필 병합은 `ReplicaSet` 또는 `Deployment` 오브젝트를 사용하여 애플리케이션을 배포할 때 유용합니다.

프로세스

`mergeStrategy: containers` 변수를 포함하도록 `ProfileRecording` 오브젝트를 편집합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha1
kind: ProfileRecording
metadata:
  # The name of the Recording is the same as the resulting SeccompProfile CRD
  # after reconciliation.
  name: test-recording
  namespace: my-namespace
spec:
  kind: SeccompProfile
  recorder: logs
  mergeStrategy: containers
  podSelector:
    matchLabels:
      app: sp-record
```

다음 명령을 실행하여 네임스페이스에 레이블을 지정합니다.

```shell-session
$ oc label ns my-namespace security.openshift.io/scc.podSecurityLabelSync=false pod-security.kubernetes.io/enforce=privileged pod-security.kubernetes.io/audit=privileged pod-security.kubernetes.io/warn=privileged --overwrite=true
```

다음 YAML을 사용하여 워크로드를 생성합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
  namespace: my-namespace
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sp-record
  template:
    metadata:
      labels:
        app: sp-record
    spec:
      serviceAccountName: spo-record-sa
      containers:
      - name: nginx-record
        image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
        ports:
        - containerPort: 8080
```

개별 프로필을 기록하려면 다음 명령을 실행하여 배포를 삭제합니다.

```shell-session
$ oc delete deployment nginx-deploy -n my-namespace
```

프로필을 병합하려면 다음 명령을 실행하여 프로필 레코딩을 삭제합니다.

```shell-session
$ oc delete profilerecording test-recording -n my-namespace
```

병합 작업을 시작하고 결과 프로필을 생성하려면 다음 명령을 실행합니다.

```shell-session
$ oc get seccompprofiles -lspo.x-k8s.io/recording-id=test-recording -n my-namespace
```

```shell-session
NAME                          STATUS       AGE
test-recording-nginx-record   Installed    55s
```

컨테이너에서 사용하는 권한을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get seccompprofiles test-recording-nginx-record -o yaml
```

#### 7.6.4. 추가 리소스

보안 컨텍스트 제약 조건 관리

OpenShift에서 SCC 관리

로그 강화기 사용

보안 프로필 정보

### 7.7. SELinux 프로필 관리

SELinux 프로필을 생성 및 관리하고 워크로드에 바인딩합니다.

중요

Security Profiles Operator는 RHCOS(Red Hat Enterprise Linux CoreOS) 작업자 노드만 지원합니다. RHEL(Red Hat Enterprise Linux) 노드는 지원되지 않습니다.

#### 7.7.1. SELinux 프로필 생성

`SelinuxProfile` 오브젝트를 사용하여 프로필을 생성합니다.

`SelinuxProfile` 오브젝트에는 보안 강화 및 가독성을 개선할 수 있는 몇 가지 기능이 있습니다.

현재 네임스페이스 또는 시스템 전체 프로필로 상속할 프로필을 제한합니다. 일반적으로 시스템에 설치된 프로필이 많이 있지만 클러스터 워크로드에서 하위 집합만 사용해야 하므로 상속 가능한 시스템 프로필은 `spec.selinuxOptions.allowedSystemProfiles` 의 `spod` 인스턴스에 나열됩니다.

권한, 클래스 및 라벨에 대한 기본 검증을 수행합니다.

정책을 사용하여 프로세스를 설명하는 새 키워드 `@self` 를 추가합니다. 이를 통해 정책 사용이 이름과 네임스페이스를 기반으로 하므로 워크로드와 네임스페이스 간에 정책을 쉽게 재사용할 수 있습니다.

SELinux CIL 언어로 직접 프로필을 작성하는 것과 비교하여 보안 강화 및 가독성 향상을 위한 기능을 추가합니다.

프로세스

다음 명령을 실행하여 프로젝트를 생성합니다.

```shell-session
$ oc new-project nginx-deploy
```

다음 `SelinuxProfile` 오브젝트를 생성하여 권한이 없는 워크로드에 사용할 수 있는 정책을 생성합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha2
kind: SelinuxProfile
metadata:
  name: nginx-secure
spec:
  allow:
    '@self':
      tcp_socket:
      - listen
    http_cache_port_t:
      tcp_socket:
      - name_bind
    node_t:
      tcp_socket:
      - node_bind
  inherit:
  - kind: System
    name: container
```

다음 명령을 실행하여 `selinuxd` 가 정책을 설치할 때까지 기다립니다.

```shell-session
$ oc wait --for=condition=ready selinuxprofile nginx-secure
```

```shell-session
selinuxprofile.security-profiles-operator.x-k8s.io/nginx-secure condition met
```

정책은 Security Profiles Operator가 소유한 컨테이너의 `emptyDir` 에 배치됩니다. 정책은 `/etc/selinux.d/<name>_<namespace>.cil` 의 CIL(Common Intermediate Language) 형식으로 저장됩니다.

다음 명령을 실행하여 Pod에 액세스합니다.

```shell-session
$ oc -n openshift-security-profiles rsh -c selinuxd ds/spod
```

검증

다음 명령을 실행하여 다음 명령으로 파일 내용을 확인합니다.

```shell
cat
```

```shell-session
$ cat /etc/selinux.d/nginx-secure_.cil
```

```shell-session
(block nginx-secure_
(blockinherit container)
(allow process nginx-secure_.process ( tcp_socket ( listen )))
(allow process http_cache_port_t ( tcp_socket ( name_bind )))
(allow process node_t ( tcp_socket ( node_bind )))
)
```

다음 명령을 실행하여 정책이 설치되었는지 확인합니다.

```shell-session
$ semodule -l | grep nginx-secure
```

```shell-session
nginx-secure_
```

#### 7.7.2. Pod에 SELinux 프로필 적용

생성된 프로필 중 하나를 적용할 Pod를 생성합니다.

SELinux 프로필의 경우 권한 있는 워크로드를 허용하려면 네임스페이스에 레이블을 지정해야 합니다.

프로세스

다음 명령을 실행하여 `scc.podSecurityLabelSync=false` 레이블을 `nginx-deploy` 네임스페이스에 적용합니다.

```shell-session
$ oc label ns nginx-deploy security.openshift.io/scc.podSecurityLabelSync=false
```

다음 명령을 실행하여 `nginx-deploy` 네임스페이스에 `privileged` 레이블을 적용합니다.

```shell-session
$ oc label ns nginx-deploy --overwrite=true pod-security.kubernetes.io/enforce=privileged
```

다음 명령을 실행하여 SELinux 프로필 사용 문자열을 가져옵니다.

```shell-session
$ oc get selinuxprofile.security-profiles-operator.x-k8s.io/nginx-secure -ojsonpath='{.status.usage}'
```

```shell-session
nginx-secure_.process
```

`.spec.containers[].securityContext.seLinuxOptions` 속성의 워크로드 매니페스트에 출력 문자열을 적용합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-secure
  namespace: nginx-deploy
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - image: nginxinc/nginx-unprivileged:1.21
      name: nginx
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
        seLinuxOptions:
          # NOTE: This uses an appropriate SELinux type
          type: nginx-secure_.process
```

중요

워크로드를 생성하기 전에 SELinux `유형이` 있어야 합니다.

#### 7.7.2.1. SELinux 로그 정책 적용

정책 위반 또는 AVC 거부를 로깅하려면 `SElinuxProfile` 프로필을 `허용` 으로 설정합니다.

중요

이 절차에서는 로깅 정책을 정의합니다. 시행 정책을 설정하지 않습니다.

프로세스

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha2
kind: SelinuxProfile
metadata:
  name: nginx-secure
spec:
  permissive: true
```

#### 7.7.2.2. ProfileBindings를 사용하여 프로필에 워크로드 바인딩

`ProfileBinding` 리소스를 사용하여 보안 프로필을 컨테이너의 `SecurityContext` 에 바인딩할 수 있습니다.

프로세스

`quay.io/security-profiles-operator/test-nginx-unprivileged:1.21` 이미지를 사용하는 Pod를 `SelinuxProfile` 프로필 예제에 바인딩하려면 Pod 및 `SelinuxProfile` 오브젝트를 사용하여 동일한 네임스페이스에 `ProfileBinding` 오브젝트를 생성합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha1
kind: ProfileBinding
metadata:
  namespace: my-namespace
  name: nginx-binding
spec:
  profileRef:
    kind: SelinuxProfile
    name: profile
  image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
```

1. `kind:` 변수는 프로필의 종류를 나타냅니다.

2. `name:` 변수는 프로필의 이름을 나타냅니다.

3. 이미지 특성에서 와일드카드를 사용하여 기본 보안 프로필을 활성화할 수 있습니다. `image: "*"`

중요

`image: "*"` 와일드카드 속성을 사용하면 모든 새 Pod가 지정된 네임스페이스의 기본 보안 프로필로 바인딩됩니다.

다음 명령을 실행하여 `enable-binding=true` 로 네임스페이스에 레이블을 지정합니다.

```shell-session
$ oc label ns my-namespace spo.x-k8s.io/enable-binding=true
```

`test-pod.yaml` 이라는 Pod를 정의합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: test-container
    image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
```

Pod를 생성합니다.

```shell-session
$ oc create -f test-pod.yaml
```

참고

Pod가 이미 존재하는 경우 바인딩이 제대로 작동하려면 Pod를 다시 생성해야 합니다.

검증

다음 명령을 실행하여 Pod가 `ProfileBinding` 을 상속하는지 확인합니다.

```shell-session
$ oc get pod test-pod -o jsonpath='{.spec.containers[*].securityContext.seLinuxOptions.type}'
```

```shell-session
profile_.process
```

#### 7.7.2.3. 컨트롤러 및 SecurityContextConstraints 복제

배포 또는 데몬 세트와 같은 컨트롤러를 복제하기 위한 SELinux 정책을 배포할 때 컨트롤러에서 생성한 `Pod` 오브젝트는 워크로드를 생성하는 사용자의 ID로 실행되지 않습니다. `ServiceAccount` 를 선택하지 않으면 사용자 정의 보안 정책 사용을 허용하지 않는 restricted SCC(`SecurityContextConstraints`)를 사용하여 Pod가 되돌릴 수 있습니다.

프로세스

다음 명령을 실행하여 프로젝트를 생성합니다.

```shell-session
$ oc new-project nginx-secure
```

다음 `RoleBinding` 오브젝트를 생성하여 `nginx-secure` 네임스페이스에서 SELinux 정책을 사용할 수 있습니다.

```yaml
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: spo-nginx
  namespace: nginx-secure
subjects:
- kind: ServiceAccount
  name: spo-deploy-test
roleRef:
  kind: Role
  name: spo-nginx
  apiGroup: rbac.authorization.k8s.io
```

`Role` 오브젝트를 생성합니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  creationTimestamp: null
  name: spo-nginx
  namespace: nginx-secure
rules:
- apiGroups:
  - security.openshift.io
  resources:
  - securitycontextconstraints
  resourceNames:
  - privileged
  verbs:
  - use
```

`ServiceAccount` 오브젝트를 생성합니다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  creationTimestamp: null
  name: spo-deploy-test
  namespace: nginx-secure
```

`Deployment` 오브젝트를 생성합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: selinux-test
  namespace: nginx-secure
  metadata:
    labels:
      app: selinux-test
spec:
  replicas: 3
  selector:
    matchLabels:
      app: selinux-test
  template:
    metadata:
      labels:
        app: selinux-test
    spec:
      serviceAccountName: spo-deploy-test
      securityContext:
        seLinuxOptions:
          type: nginx-secure_.process
      containers:
      - name: nginx-unpriv
        image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
        ports:
        - containerPort: 8080
```

1. 배포가 생성되기 전에 `.seLinuxOptions.type` 이 있어야 합니다.

참고

SELinux 유형은 워크로드에 지정되지 않으며 SCC에서 처리합니다. 배포 및 `ReplicaSet` 을 통해 Pod를 생성하면 Pod가 적절한 프로필과 함께 실행됩니다.

올바른 서비스 계정에서만 SCC를 사용할 수 있는지 확인합니다. 자세한 내용은 추가 리소스를 참조하십시오.

#### 7.7.3. 워크로드의 프로필 기록

Security Profiles Operator는 `ProfileRecording` 오브젝트를 사용하여 시스템 호출을 기록할 수 있으므로 애플리케이션에 대한 기본 프로필을 더 쉽게 생성할 수 있습니다.

SELinux 프로필을 기록하는 데 로그 강화기를 사용하는 경우 로그 강화 기능이 활성화되었는지 확인합니다. 자세한 내용은 추가 리소스 를 참조하십시오.

참고

`privileged: true` security context restraints가 있는 컨테이너는 로그 기반 기록을 방지합니다. 권한 있는 컨테이너는 SELinux 정책의 영향을 받지 않으며 로그 기반 기록에서는 특수 SELinux 프로필을 사용하여 이벤트를 기록합니다.

프로세스

다음 명령을 실행하여 프로젝트를 생성합니다.

```shell-session
$ oc new-project my-namespace
```

다음 명령을 실행하여 `enable-recording=true` 로 네임스페이스에 레이블을 지정합니다.

```shell-session
$ oc label ns my-namespace spo.x-k8s.io/enable-recording=true
```

`recorder: logs` 변수를 포함하는 `ProfileRecording` 오브젝트를 생성합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha1
kind: ProfileRecording
metadata:
  namespace: my-namespace
  name: test-recording
spec:
  kind: SelinuxProfile
  recorder: logs
  podSelector:
    matchLabels:
      app: my-app
```

기록할 워크로드를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  namespace: my-namespace
  name: my-pod
  labels:
    app: my-app
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: nginx
      image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
      ports:
        - containerPort: 8080
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
    - name: redis
      image: quay.io/security-profiles-operator/redis:6.2.1
      securityContext:
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
```

다음 명령을 입력하여 Pod가 `Running` 상태인지 확인합니다.

```shell-session
$ oc -n my-namespace get pods
```

```shell-session
NAME     READY   STATUS    RESTARTS   AGE
my-pod   2/2     Running   0          18s
```

강화자가 해당 컨테이너에 대한 감사 로그를 수신하는지 확인합니다.

```shell-session
$ oc -n openshift-security-profiles logs --since=1m --selector name=spod -c log-enricher
```

```shell-session
I0517 13:55:36.383187  348295 enricher.go:376] log-enricher "msg"="audit" "container"="redis" "namespace"="my-namespace" "node"="ip-10-0-189-53.us-east-2.compute.internal" "perm"="name_bind" "pod"="my-pod" "profile"="test-recording_redis_6kmrb_1684331729" "scontext"="system_u:system_r:selinuxrecording.process:s0:c4,c27" "tclass"="tcp_socket" "tcontext"="system_u:object_r:redis_port_t:s0" "timestamp"="1684331735.105:273965" "type"="selinux"
```

검증

Pod를 제거합니다.

```shell-session
$ oc -n my-namespace delete pod my-pod
```

Security Profiles Operator가 다음 두 SELinux 프로필을 조정하는지 확인합니다.

```shell-session
$ oc get selinuxprofiles -lspo.x-k8s.io/recording-id=test-recording
```

```shell-session
NAME                   USAGE                                       STATE
test-recording-nginx   test-recording-nginx_.process   Installed
test-recording-redis   test-recording-redis_.process   Installed
```

#### 7.7.3.1. 컨테이너당 프로필 인스턴스 병합

기본적으로 각 컨테이너 인스턴스는 별도의 프로필에 저장됩니다. Security Profiles Operator는 컨테이너별 프로필을 단일 프로필에 병합할 수 있습니다. 프로필 병합은 `ReplicaSet` 또는 `Deployment` 오브젝트를 사용하여 애플리케이션을 배포할 때 유용합니다.

프로세스

`mergeStrategy: containers` 변수를 포함하도록 `ProfileRecording` 오브젝트를 편집합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1alpha1
kind: ProfileRecording
metadata:
  # The name of the Recording is the same as the resulting SelinuxProfile CRD
  # after reconciliation.
  name: test-recording
  namespace: my-namespace
spec:
  kind: SelinuxProfile
  recorder: logs
  mergeStrategy: containers
  podSelector:
    matchLabels:
      app: sp-record
```

다음 명령을 실행하여 네임스페이스에 레이블을 지정합니다.

```shell-session
$ oc label ns my-namespace security.openshift.io/scc.podSecurityLabelSync=false pod-security.kubernetes.io/enforce=privileged pod-security.kubernetes.io/audit=privileged pod-security.kubernetes.io/warn=privileged --overwrite=true
```

다음 YAML을 사용하여 워크로드를 생성합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
  namespace: my-namespace
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sp-record
  template:
    metadata:
      labels:
        app: sp-record
    spec:
      serviceAccountName: spo-record-sa
      containers:
      - name: nginx-record
        image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
        ports:
        - containerPort: 8080
```

개별 프로필을 기록하려면 다음 명령을 실행하여 배포를 삭제합니다.

```shell-session
$ oc delete deployment nginx-deploy -n my-namespace
```

프로필을 병합하려면 다음 명령을 실행하여 프로필 레코딩을 삭제합니다.

```shell-session
$ oc delete profilerecording test-recording -n my-namespace
```

병합 작업을 시작하고 결과 프로필을 생성하려면 다음 명령을 실행합니다.

```shell-session
$ oc get selinuxprofiles -lspo.x-k8s.io/recording-id=test-recording -n my-namespace
```

```shell-session
NAME                          USAGE                                  STATE
test-recording-nginx-record   test-recording-nginx-record_.process   Installed
```

컨테이너에서 사용하는 권한을 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get selinuxprofiles test-recording-nginx-record -o yaml
```

#### 7.7.3.2. seLinuxContext 정보: RunAsAny

SELinux 정책 기록은 기록 중인 포드에 특수 SELinux 유형을 삽입하는 Webhook를 사용하여 구현됩니다. SELinux 유형은 pod를 `허용` 모드로 실행하고 모든 AVC 거부를 `audit.log` 에 기록합니다. 기본적으로 워크로드는 사용자 지정 SELinux 정책으로 실행할 수 없지만 자동 생성 유형을 사용합니다.

워크로드를 기록하려면 Webhook에서 허용 SELinux 유형을 삽입할 수 있는 SCC를 사용할 수 있는 권한이 있는 서비스 계정을 사용해야 합니다. `권한 있는` SCC에는 `seLinuxContext: RunAsAny` 가 포함되어 있습니다.

또한 `privileged` Pod 보안 표준 에서만 사용자 정의 SELinux 정책을 사용할 수 있으므로 클러스터가 Pod Security Admission 을 활성화하는 경우 `pod-security.kubernetes.io/enforce: privileged` 로 네임스페이스에 라벨을 지정해야 합니다.

#### 7.7.4. 추가 리소스

보안 컨텍스트 제약 조건 관리

OpenShift에서 SCC 관리

로그 강화기 사용

보안 프로필 정보

### 7.8. Advanced Security Profiles Operator 작업

고급 작업을 사용하여 메트릭을 활성화하거나 Webhook를 구성하거나 syscall을 제한합니다.

#### 7.8.1. seccomp 프로필에서 허용되는 syscalls 제한

Security Profiles Operator는 기본적으로 `seccomp` 프로필 `의 syscall` 을 제한하지 않습니다. `spod` 구성에서 허용된 `syscall` 목록을 정의할 수 있습니다.

프로세스

`allowedSyscalls` 목록을 정의하려면 다음 명령을 실행하여 `spec` 매개변수를 조정합니다.

```shell-session
$ oc -n openshift-security-profiles patch spod spod --type merge \
    -p '{"spec":{"allowedSyscalls": ["exit", "exit_group", "futex", "nanosleep"]}}'
```

중요

Operator는 허용된 목록에 정의된 `syscall의` 하위 집합이 있는 `seccomp` 프로필만 설치합니다. 이 규칙 세트를 준수하지 않는 모든 프로필이 거부됩니다.

`spod` 구성에서 허용되는 `syscall` 목록이 수정되면 Operator는 준수하지 않는 이미 설치된 프로필을 확인하고 자동으로 제거합니다.

#### 7.8.2. 컨테이너 런타임의 기본 syscall

`baseProfileName` 속성을 사용하여 지정된 런타임에서 컨테이너를 시작하는 데 필요한 최소 `syscall` 을 설정할 수 있습니다.

프로세스

`SeccompProfile` kind 오브젝트를 편집하고 `baseProfileName: runc-v1.0.0` 을 `spec` 필드에 추가합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1beta1
kind: SeccompProfile
metadata:
  name: example-name
spec:
  defaultAction: SCMP_ACT_ERRNO
  baseProfileName: runc-v1.0.0
  syscalls:
    - action: SCMP_ACT_ALLOW
      names:
        - exit_group
```

#### 7.8.3. spod 데몬에서 메모리 최적화 활성화

`spod` 데몬 프로세스 내에서 실행 중인 컨트롤러는 프로파일 레코딩이 활성화된 경우 클러스터에서 사용 가능한 모든 Pod를 감시합니다. 이로 인해 대규모 클러스터에서 메모리 사용량이 매우 높아져 `spod` 데몬이 메모리가 부족하거나 충돌할 수 있습니다.

충돌을 방지하기 위해 `spod` 데몬은 프로파일 레코딩용으로 레이블이 지정된 Pod만 캐시 메모리에 로드하도록 구성할 수 있습니다.

참고

SPO 메모리 최적화는 기본적으로 활성화되어 있지 않습니다.

프로세스

다음 명령을 실행하여 메모리 최적화를 활성화합니다.

```shell-session
$ oc -n openshift-security-profiles patch spod spod --type=merge -p '{"spec":{"enableMemoryOptimization":true}}'
```

Pod의 보안 프로필을 기록하려면 Pod에 `spo.x-k8s.io/enable-recording: "true"` 로 레이블이 지정되어야 합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-recording-pod
  labels:
    spo.x-k8s.io/enable-recording: "true"
# ...
```

#### 7.8.4. 데몬 리소스 요구 사항 사용자 정의

데몬 컨테이너의 기본 리소스 요구 사항은 `spod` 구성의 `daemonResourceRequirements` 필드를 사용하여 조정할 수 있습니다.

프로세스

데몬 컨테이너의 메모리 및 cpu 요청 및 제한을 지정하려면 다음 명령을 실행합니다.

```shell-session
$ oc -n openshift-security-profiles patch spod spod --type merge -p \
    '{"spec":{"daemonResourceRequirements": { \
    "requests": {"memory": "256Mi", "cpu": "250m"}, \
    "limits": {"memory": "512Mi", "cpu": "500m"}}}}'
```

#### 7.8.5. spod 데몬 Pod의 사용자 정의 우선순위 클래스 이름 설정

`spod` 데몬 Pod의 기본 우선순위 클래스 이름은 `system-node-critical` 로 설정됩니다. `priorityClassName` 필드에 값을 설정하여 사용자 정의 우선순위 클래스 이름을 `spod` 구성에 구성할 수 있습니다.

프로세스

다음 명령을 실행하여 우선순위 클래스 이름을 구성합니다.

```shell-session
$ oc -n openshift-security-profiles patch spod spod --type=merge -p '{"spec":{"priorityClassName":"my-priority-class"}}'
```

```shell-session
securityprofilesoperatordaemon.openshift-security-profiles.x-k8s.io/spod patched
```

#### 7.8.6. 메트릭 사용

`openshift-security-profiles` 네임스페이스는 kube-rbac-proxy 컨테이너에서 보안되는 메트릭 끝점을 제공합니다. 모든 메트릭은 `openshift-security-profiles` 네임스페이스 내에서 `메트릭` 서비스에 의해 노출됩니다.

Security Profiles Operator에는 클러스터 역할 및 해당 바인딩 `spo-metrics-client` 가 포함되어 클러스터 내에서 지표를 검색합니다. 다음 두 가지 메트릭 경로를 사용할 수 있습니다.

`metrics.openshift-security-profiles/metrics`: 컨트롤러 런타임 지표의 경우

`metrics.openshift-security-profiles/metrics-spod`: Operator 데몬 지표의 경우

프로세스

메트릭 서비스의 상태를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get svc/metrics -n openshift-security-profiles
```

```shell-session
NAME      TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
metrics   ClusterIP   10.0.0.228   <none>        443/TCP   43s
```

지표를 검색하려면 다음 명령을 실행하여 `openshift-security-profiles` 네임스페이스에서 기본 `ServiceAccount` 토큰을 사용하여 서비스 끝점을 쿼리합니다.

```shell-session
$ oc run --rm -i --restart=Never --image=registry.fedoraproject.org/fedora-minimal:latest \
    -n openshift-security-profiles metrics-test -- bash -c \
    'curl -ks -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" https://metrics.openshift-security-profiles/metrics-spod'
```

```shell-session
# HELP security_profiles_operator_seccomp_profile_total Counter about seccomp profile operations.
# TYPE security_profiles_operator_seccomp_profile_total counter
security_profiles_operator_seccomp_profile_total{operation="delete"} 1
security_profiles_operator_seccomp_profile_total{operation="update"} 2
```

다른 네임스페이스에서 지표를 검색하려면 다음 명령을 실행하여 `ServiceAccount` 를 `spo-metrics-client`

`ClusterRoleBinding` 에 연결합니다.

```shell-session
$ oc get clusterrolebinding spo-metrics-client -o wide
```

```shell-session
NAME                 ROLE                             AGE   USERS   GROUPS   SERVICEACCOUNTS
spo-metrics-client   ClusterRole/spo-metrics-client   35m                    openshift-security-profiles/default
```

#### 7.8.6.1. controller-runtime 메트릭

controller-runtime `메트릭` 및 DaemonSet 끝점 `metrics-spod` 는 기본 지표 세트를 제공합니다. 추가 메트릭은 데몬에서 제공하며 항상 `security_profiles_operator_` 접두사가 붙습니다.

| 메트릭 키 | 가능한 레이블 | 유형 | 목적 |
| --- | --- | --- | --- |
| `seccomp_profile_total` | `operation={delete,update}` | 카운터 | seccomp 프로필 작업의 양입니다. |
| `seccomp_profile_audit_total` | `노드` , `네임스페이스` , `Pod` , `컨테이너` , `실행 가능` , `syscall` | 카운터 | seccomp 프로필 감사 작업의 양입니다. 로그를 더 강화해야 합니다. |
| `seccomp_profile_bpf_total` | `node` , `mount_namespace` , `profile` | 카운터 | seccomp 프로필 bpf 작업의 양입니다. bpf 레코더를 활성화해야 합니다. |
| `seccomp_profile_error_total` | `reason={` `SeccompSupportedOnNode,` `InvalidSeccompProfile,` `CannotSaveSeccompProfile,` CannotRemoveSeccompProfile, `CannotRemoveSeccompProfile,` `CannotUpdateSeccompProfile,` `CannotUpdateNodeStatus` `}` | 카운터 | seccomp 프로필 오류의 양입니다. |
| `selinux_profile_total` | `operation={delete,update}` | 카운터 | SELinux 프로필 작업의 양입니다. |
| `selinux_profile_audit_total` | `노드` , `네임스페이스` , `Pod` , `컨테이너` , `실행 가능` , `scontext` , `tcontext` | 카운터 | SELinux 프로필 감사 작업의 양입니다. 로그를 더 강화해야 합니다. |
| `selinux_profile_error_total` | `reason={` `CannotSaveSelinuxPolicy,` `CannotUpdatePolicyStatus,` `CannotRemoveSelinuxPolicy,` `CannotContactSelinuxd,` `CannotWritePolicyFile,` `CannotGetPolicyStatus` `}` | 카운터 | SELinux 프로필 오류 수입니다. |

#### 7.8.7. 로그 강화기 사용

Security Profiles Operator에는 기본적으로 비활성화되어 있는 로그 보강 기능이 포함되어 있습니다. 로그 강화 컨테이너는 로컬 노드에서 감사 로그를 읽을 수 `있는` 권한과 함께 실행됩니다. 로그 강화는 호스트 PID 네임스페이스 `hostPID` 내에서 실행됩니다.

중요

로그 보강자는 호스트 프로세스를 읽을 수 있는 권한이 있어야 합니다.

프로세스

다음 명령을 실행하여 `spod` 구성을 패치하여 로그 강화를 활성화합니다.

```shell-session
$ oc -n openshift-security-profiles patch spod spod \
    --type=merge -p '{"spec":{"enableLogEnricher":true}}'
```

```shell-session
securityprofilesoperatordaemon.security-profiles-operator.x-k8s.io/spod patched
```

참고

Security Profiles Operator는 `spod` 데몬 세트를 자동으로 다시 배포합니다.

다음 명령을 실행하여 감사 로그를 확인합니다.

```shell-session
$ oc -n openshift-security-profiles logs -f ds/spod log-enricher
```

```shell-session
I0623 12:51:04.257814 1854764 deleg.go:130] setup "msg"="starting component: log-enricher"  "buildDate"="1980-01-01T00:00:00Z" "compiler"="gc" "gitCommit"="unknown" "gitTreeState"="clean" "goVersion"="go1.16.2" "platform"="linux/amd64" "version"="0.4.0-dev"
I0623 12:51:04.257890 1854764 enricher.go:44] log-enricher "msg"="Starting log-enricher on node: 127.0.0.1"
I0623 12:51:04.257898 1854764 enricher.go:46] log-enricher "msg"="Connecting to local GRPC server"
I0623 12:51:04.258061 1854764 enricher.go:69] log-enricher "msg"="Reading from file /var/log/audit/audit.log"
2021/06/23 12:51:04 Seeked /var/log/audit/audit.log - &{Offset:0 Whence:2}
```

#### 7.8.7.1. 로그를 보강하여 애플리케이션 추적

Security Profiles Operator 로그를 사용하여 애플리케이션을 추적할 수 있습니다.

프로세스

애플리케이션을 추적하려면 `SeccompProfile` 로깅 프로필을 생성합니다.

```yaml
apiVersion: security-profiles-operator.x-k8s.io/v1beta1
kind: SeccompProfile
metadata:
  name: log
spec:
  defaultAction: SCMP_ACT_LOG
```

프로필을 사용할 Pod 오브젝트를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: log-pod
  namespace: default
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: Localhost
      localhostProfile: operator/log.json
  containers:
  - name: log-container
    image: quay.io/security-profiles-operator/test-nginx-unprivileged:1.21
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: [ALL]
```

다음 명령을 실행하여 로그 강화 출력을 검사합니다.

```shell-session
$ oc -n openshift-security-profiles logs -f ds/spod log-enricher
```

```shell-session
…
I0623 12:59:11.479869 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=3 "syscallName"="close" "timestamp"="1624453150.205:1061" "type"="seccomp"
I0623 12:59:11.487323 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=157 "syscallName"="prctl" "timestamp"="1624453150.205:1062" "type"="seccomp"
I0623 12:59:11.492157 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=157 "syscallName"="prctl" "timestamp"="1624453150.205:1063" "type"="seccomp"
…
I0623 12:59:20.258523 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/usr/sbin/nginx" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=12 "syscallName"="brk" "timestamp"="1624453150.235:2873" "type"="seccomp"
I0623 12:59:20.263349 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/usr/sbin/nginx" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=21 "syscallName"="access" "timestamp"="1624453150.235:2874" "type"="seccomp"
I0623 12:59:20.354091 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/usr/sbin/nginx" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=257 "syscallName"="openat" "timestamp"="1624453150.235:2875" "type"="seccomp"
I0623 12:59:20.358844 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/usr/sbin/nginx" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=5 "syscallName"="fstat" "timestamp"="1624453150.235:2876" "type"="seccomp"
I0623 12:59:20.363510 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/usr/sbin/nginx" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=9 "syscallName"="mmap" "timestamp"="1624453150.235:2877" "type"="seccomp"
I0623 12:59:20.454127 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/usr/sbin/nginx" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=3 "syscallName"="close" "timestamp"="1624453150.235:2878" "type"="seccomp"
I0623 12:59:20.458654 1854764 enricher.go:111] log-enricher "msg"="audit"  "container"="log-container" "executable"="/usr/sbin/nginx" "namespace"="default" "node"="127.0.0.1" "pid"=1905792 "pod"="log-pod" "syscallID"=257 "syscallName"="openat" "timestamp"="1624453150.235:2879" "type"="seccomp"
…
```

#### 7.8.8. Webhook 구성

프로파일 바인딩 및 프로파일 레코딩 오브젝트는 Webhook를 사용할 수 있습니다. 프로필 바인딩 및 레코딩 오브젝트 구성은 `MutatingWebhookConfiguration` CR이며 Security Profiles Operator에서 관리합니다.

Webhook 구성을 변경하기 위해 `spod` CR은 `failurePolicy`, `namespaceSelector` 및 `objectSelector` 변수를 수정할 수 있는 `webhookOptions` 필드를 노출합니다. 이를 통해 Webhook를 "soft-fail"로 설정하거나 Webhook가 실패하더라도 다른 네임스페이스 또는 리소스가 영향을 받지 않도록 네임스페이스의 하위 집합으로 제한할 수 있습니다.

프로세스

다음 패치 파일을 생성하여 `spo-record=true` 로 레이블이 지정된 Pod만 기록하도록 `recording.spo.io` 웹 후크 구성을 설정합니다.

```yaml
spec:
  webhookOptions:
    - name: recording.spo.io
      objectSelector:
        matchExpressions:
          - key: spo-record
            operator: In
            values:
              - "true"
```

다음 명령을 실행하여 `spod/spod` 인스턴스를 패치합니다.

```shell-session
$ oc -n openshift-security-profiles patch spod \
    spod -p $(cat /tmp/spod-wh.patch) --type=merge
```

결과 `MutatingWebhookConfiguration` 오브젝트를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get MutatingWebhookConfiguration \
    spo-mutating-webhook-configuration -oyaml
```

### 7.9. Security Profiles Operator 문제 해결

Security Profiles Operator의 문제를 해결하여 문제를 진단하거나 버그 보고서에 정보를 제공합니다.

#### 7.9.1. seccomp 프로필 검사

손상된 `seccomp` 프로필로 인해 워크로드가 손상될 수 있습니다. 다른 워크로드가 경로 `/var/lib/kubelet/seccomp/operator` 의 일부를 매핑할 수 없으므로 사용자가 시스템을 악용할 수 없는지 확인합니다.

프로세스

다음 명령을 실행하여 프로필이 조정되었는지 확인합니다.

```shell-session
$ oc -n openshift-security-profiles logs openshift-security-profiles-<id>
```

```shell-session
I1019 19:34:14.942464       1 main.go:90] setup "msg"="starting openshift-security-profiles"  "buildDate"="2020-10-19T19:31:24Z" "compiler"="gc" "gitCommit"="a3ef0e1ea6405092268c18f240b62015c247dd9d" "gitTreeState"="dirty" "goVersion"="go1.15.1" "platform"="linux/amd64" "version"="0.2.0-dev"
I1019 19:34:15.348389       1 listener.go:44] controller-runtime/metrics "msg"="metrics server is starting to listen"  "addr"=":8080"
I1019 19:34:15.349076       1 main.go:126] setup "msg"="starting manager"
I1019 19:34:15.349449       1 internal.go:391] controller-runtime/manager "msg"="starting metrics server"  "path"="/metrics"
I1019 19:34:15.350201       1 controller.go:142] controller "msg"="Starting EventSource" "controller"="profile" "reconcilerGroup"="security-profiles-operator.x-k8s.io" "reconcilerKind"="SeccompProfile" "source"={"Type":{"metadata":{"creationTimestamp":null},"spec":{"defaultAction":""}}}
I1019 19:34:15.450674       1 controller.go:149] controller "msg"="Starting Controller" "controller"="profile" "reconcilerGroup"="security-profiles-operator.x-k8s.io" "reconcilerKind"="SeccompProfile"
I1019 19:34:15.450757       1 controller.go:176] controller "msg"="Starting workers" "controller"="profile" "reconcilerGroup"="security-profiles-operator.x-k8s.io" "reconcilerKind"="SeccompProfile" "worker count"=1
I1019 19:34:15.453102       1 profile.go:148] profile "msg"="Reconciled profile from SeccompProfile" "namespace"="openshift-security-profiles" "profile"="nginx-1.19.1" "name"="nginx-1.19.1" "resource version"="728"
I1019 19:34:15.453618       1 profile.go:148] profile "msg"="Reconciled profile from SeccompProfile" "namespace"="openshift-security-profiles" "profile"="openshift-security-profiles" "name"="openshift-security-profiles" "resource version"="729"
```

다음 명령을 실행하여 `seccomp` 프로필이 올바른 경로에 저장되었는지 확인합니다.

```shell-session
$ oc exec -t -n openshift-security-profiles openshift-security-profiles-<id> \
    -- ls /var/lib/kubelet/seccomp/operator/my-namespace/my-workload
```

```shell-session
profile-block.json
profile-complain.json
```

### 7.10. Security Profiles Operator 설치 제거

OpenShift Container Platform 웹 콘솔을 사용하여 클러스터에서 Security Profiles Operator를 제거할 수 있습니다.

#### 7.10.1. 웹 콘솔을 사용하여 Security Profiles Operator 설치 제거

Security Profiles Operator를 제거하려면 먼저 `seccomp` 및 SELinux 프로필을 삭제해야 합니다. 프로필이 제거되면 openshift-security-profiles 프로젝트를 삭제하여 Operator 및 해당 네임스페이스를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 웹 콘솔에 액세스할 수 있습니다.

Security Profiles Operator가 설치되어 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔을 사용하여 Security Profiles Operator를 제거하려면 다음을 수행합니다.

에코시스템 → 설치된 Operator 페이지로 이동합니다.

모든 `seccomp` 프로필, SELinux 프로필 및 Webhook 구성을 삭제합니다.

관리 → 에코시스템 → 설치된 Operator 페이지로 전환합니다.

Security Profiles Operator 항목에서 옵션 메뉴

를 클릭하고 Operator 설치 제거를 선택합니다.

홈 → 프로젝트 페이지로 전환합니다.

`security profiles` 을 검색합니다.

openshift-security-profiles 프로젝트 옆에 있는 옵션 메뉴

를 클릭하고 프로젝트 삭제 를 선택합니다.

대화 상자에 `openshift-security-profiles` 를 입력하여 삭제를 확인하고 삭제 를 클릭합니다.

다음 명령을 실행하여 `MutatingWebhookConfiguration` 오브젝트를 삭제합니다.

```shell-session
$ oc delete MutatingWebhookConfiguration spo-mutating-webhook-configuration
```

### 8.1. NBDE Tang Server Operator 개요

NBDE(Network-bound Disk Encryption)는 하나 이상의 전용 네트워크 바인딩 서버를 사용하여 LUKS 암호화 볼륨의 자동 잠금 해제를 제공합니다. Clevis의 클라이언트 측은 Clevis 암호 해독 정책 프레임워크라고 하며 서버 쪽은 Tang으로 표시됩니다.

NBDE Tang Server Operator를 사용하면 OCP(OpenShift Container Platform) 환경에서 하나 이상의 Tang 서버 배포를 자동화할 수 있습니다.

### 8.2. NBDE Tang Server Operator 릴리스 노트

다음 릴리스 노트에서는 OpenShift Container Platform에서 NBDE Tang Server Operator의 개발을 추적합니다.

RHEA-2023:7491

NBDE Tang Server Operator 1.0은 Red Hat OpenShift Enterprise 4 카탈로그에서 릴리스되었습니다.

RHEA-2024:0854

NBDE Tang Server Operator 1.0.1이 `알파` 채널에서 `stable` 채널로 이동되었습니다.

RHBA-2024:8681

1.0.2 업데이트에는 NBDE Tang 서버 Operator와 함께 배포된 컨테이너의 Container Health Index를 최고 등급으로 늘리는 수정 사항이 포함되어 있습니다.

RHEA-2024:10970

1.0.3 업데이트에는 Container Health Index를 가장 높은 등급으로 다시 만드는 변경 사항이 포함되어 있습니다.

RHBA-2025:0663

NBDE Tang Server Operator 1.1에는 `golang` 패키지 버전 1.23.2와 `golang.org/x/net/html` 패키지 버전 0.33.0이 포함되어 있습니다. 업데이트는 컨테이너 상태 지수를 개선합니다.

RHBA-2025:4453

1.1.1 업데이트는 CVE-2025-22866 에 대한 수정 사항을 제공합니다.

### 8.3. NBDE Tang Server Operator 이해

NBDE Tang Server Operator를 사용하여 OpenShift Container Platform에서 이 자동화를 수행하기 위해 OpenShift Container Platform에서 제공하는 툴을 활용하여 내부적으로 NBDE(Network Bound Disk Encryption)가 필요한 Tang 서버 배포를 자동화할 수 있습니다.

NBDE Tang Server Operator는 설치 프로세스를 단순화하고 다중 복제 배포, 스케일링, 트래픽 로드 밸런싱 등과 같은 OpenShift Container Platform 환경에서 제공하는 기본 기능을 사용합니다. 또한 Operator는 수동으로 수행할 때 오류가 발생하기 쉬운 특정 작업의 자동화도 제공합니다. 예를 들면 다음과 같습니다.

서버 배포 및 구성

키 교체

숨겨진 키 삭제

NBDE Tang Server Operator는 Operator SDK를 사용하여 구현되며 CRD(사용자 정의 리소스 정의)를 통해 OpenShift에서 하나 이상의 Tang 서버를 배포할 수 있습니다.

#### 8.3.1. 추가 리소스

Tang-Operator: OpenShift Red Hat Hybrid Cloud에서 NBDE 제공 블로그 문서

Tang-operator Github 프로젝트

RHEL 9 보안 강화 문서에서 정책 기반 암호 해독 장을 사용하여 암호화된 볼륨의 자동 잠금 해제 구성

### 8.4. NBDE Tang Server Operator 설치

웹 콘솔을 사용하거나 CLI에서 아래 명령을 통해 NBDE Tang Operator를 설치할 수 있습니다.

```shell
oc
```

#### 8.4.1. 웹 콘솔을 사용하여 NBDE Tang Server Operator 설치

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-01-operatorhub.png" alt="소프트웨어 카탈로그의 NBDE Tang Server Operator" kind="figure" diagram_type="image_figure"]
소프트웨어 카탈로그의 NBDE Tang Server Operator
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/83c00746ec22ba3d557d58787e60f06d/nbde-tang-server-operator-01-operatorhub.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-03-confirmation.png" alt="NBDE Tang Server Operator 설치 확인" kind="figure" diagram_type="image_figure"]
NBDE Tang Server Operator 설치 확인
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/99b80a9d09455aeb0362604c65210ff6/nbde-tang-server-operator-03-confirmation.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-05-succeeded.png" alt="NBDE Tang Server Operator 상태" kind="figure" diagram_type="image_figure"]
NBDE Tang Server Operator 상태
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/89689feb45b48b9e83f858f6198bddd0/nbde-tang-server-operator-05-succeeded.png`_


웹 콘솔을 사용하여 소프트웨어 카탈로그에서 NBDE Tang Server Operator를 설치할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 `cluster-admin` 권한이 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 Ecosystem → Software Catalog 로 이동합니다.

NBDE Tang Server Operator를 검색합니다.

설치 를 클릭합니다.

Operator 설치 화면에서 업데이트 채널, 버전, 설치 모드, 설치된 네임스페이스 및 업데이트 승인 필드를 기본값에 유지합니다.

Install 을 클릭하여 설치 옵션을 확인한 후 콘솔에 설치 확인이 표시됩니다.

검증

에코시스템 → 설치된 Operator 페이지로 이동합니다.

NBDE Tang Server Operator가 설치되고 해당 상태가 `Succeeded` 인지 확인합니다.

#### 8.4.2. CLI를 사용하여 NBDE Tang Server Operator 설치

CLI를 사용하여 소프트웨어 카탈로그에서 NBDE Tang Server Operator를 설치할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 `cluster-admin` 권한이 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 명령을 사용하여 소프트웨어 카탈로그에서 사용 가능한 Operator를 나열하고 출력을 Tang 관련 결과로 제한합니다.

```shell-session
$ oc get packagemanifests -n openshift-marketplace | grep tang
```

```shell-session
tang-operator           Red Hat
```

이 경우 해당 packagemanifest 이름은 `tang-operator` 입니다.

`Subscription` 오브젝트 YAML 파일을 생성하여 NBDE Tang Server Operator에 네임스페이스를 서브스크립션합니다(예: `tang-operator.yaml`).

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: tang-operator
  namespace: openshift-operators
spec:
  channel: stable
  installPlanApproval: Automatic
  name: tang-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

1. Operator를 서브스크립션할 채널 이름을 지정합니다.

2. 등록할 Operator의 이름을 지정합니다.

3. Operator를 제공하는 CatalogSource의 이름을 지정합니다.

4. CatalogSource의 네임스페이스입니다. 기본 소프트웨어 카탈로그 소스에는 `openshift-marketplace` 를 사용합니다.

클러스터에 `서브스크립션` 을 적용합니다.

```shell-session
$ oc apply -f tang-operator.yaml
```

검증

NBDE Tang Server Operator 컨트롤러가 `openshift-operators` 네임스페이스에서 실행되는지 확인합니다.

```shell-session
$ oc -n openshift-operators get pods
```

```shell-session
NAME                                                READY   STATUS    RESTARTS   AGE
tang-operator-controller-manager-694b754bd6-4zk7x   2/2     Running   0          12s
```

### 8.5. NBDE Tang Server Operator를 사용하여 Tang 서버 구성 및 관리

NBDE Tang Server Operator를 사용하면 Tang 서버를 배포하고 빠르게 구성할 수 있습니다. 배포된 Tang 서버에서 기존 키를 나열하고 회전할 수 있습니다.

#### 8.5.1. NBDE Tang Server Operator를 사용하여 Tang 서버 배포

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-07-create-project.png" alt="웹 콘솔에서 프로젝트 생성" kind="figure" diagram_type="image_figure"]
웹 콘솔에서 프로젝트 생성
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/5c18fe4af4c5278bc84520eac6149577/nbde-tang-server-operator-07-create-project.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-09-project-values.png" alt="프로젝트 생성 페이지의 값 예" kind="figure" diagram_type="image_figure"]
프로젝트 생성 페이지의 값 예
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/a6a880d64a79dbb996b12c5ce2ae8dcd/nbde-tang-server-operator-09-project-values.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-11-pvc.png" alt="Storage 메뉴의 PersistentVolumeClaims" kind="figure" diagram_type="image_figure"]
Storage 메뉴의 PersistentVolumeClaims
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/eb00c8f14a19d006efe6eb61428cd9de/nbde-tang-server-operator-11-pvc.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-13-create-pvc.png" alt="PersistentVolumeClaims 페이지 생성" kind="figure" diagram_type="image_figure"]
PersistentVolumeClaims 페이지 생성
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/e544d77f4bdf708ec1f341a795ae555c/nbde-tang-server-operator-13-create-pvc.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-15-create-instance.png" alt="NBDE Tang 서버 인스턴스 생성" kind="figure" diagram_type="image_figure"]
NBDE Tang 서버 인스턴스 생성
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/6960212ac71f6abf259abab7278d8802/nbde-tang-server-operator-15-create-instance.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-17-create-tangserver.png" alt="TangServer 페이지 생성" kind="figure" diagram_type="image_figure"]
TangServer 페이지 생성
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/f106d49f37570ba038a7875195f8752d/nbde-tang-server-operator-17-create-tangserver.png`_


웹 콘솔에서 NBDE Tang Server Operator를 사용하여 하나 이상의 Tang 서버를 배포하고 빠르게 구성할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 `cluster-admin` 권한이 있어야 합니다.

OCP 클러스터에 NBDE Tang Server Operator를 설치했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 Ecosystem → Software Catalog 로 이동합니다.

프로젝트 를 선택하고 프로젝트 생성 을 클릭합니다.

`프로젝트 생성` 페이지에서 필요한 정보를 입력합니다. 예를 들면 다음과 같습니다.

생성 을 클릭합니다.

NBDE Tang 서버 복제본에는 암호화 키를 저장하기 위한 영구 볼륨 클레임(PVC)이 필요합니다. 웹 콘솔에서 스토리지 → PersistentVolumeClaims 로 이동합니다.

다음 `PersistentVolumeClaims` 화면에서 PersistentVolumeClaim 생성을 클릭합니다.

`PersistentVolumeClaim 생성` 페이지에서 배포 시나리오에 맞는 스토리지를 선택합니다. 암호화 키를 교체하는 빈도를 고려하십시오. PVC의 이름을 지정하고 클레임된 스토리지 용량을 선택합니다. 예를 들면 다음과 같습니다.

Ecosystem → 설치된 Operators 로 이동하여 NBDE Tang Server 를 클릭합니다.

인스턴스 만들기 를 클릭합니다.

`TangServer 생성 페이지에서 Tang Server` 인스턴스의 이름, 복제본 크기, 이전에 생성된 영구 볼륨 클레임의 이름을 지정합니다. 예를 들면 다음과 같습니다.

필요한 값을 입력한 후 시나리오의 기본값과 다른 변경 설정을 클릭하여 만들기 를 클릭합니다.

#### 8.5.2. NBDE Tang Server Operator를 사용하여 키 교체

NBDE Tang Server Operator를 사용하면 Tang 서버 키를 교체할 수도 있습니다. 교체해야하는 정확한 간격은 애플리케이션, 키 크기 및 기관 정책에 따라 다릅니다.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 `cluster-admin` 권한이 있어야 합니다.

OpenShift 클러스터에서 NBDE Tang Server Operator를 사용하여 Tang 서버를 배포했습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

Tang 서버의 기존 키를 나열합니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc -n nbde describe tangserver
```

```shell-session
…
Status:
  Active Keys:
    File Name:      QS82aXnPKA4XpfHr3umbA0r2iTbRcpWQ0VI2Qdhi6xg
    Generated:      2022-02-08 15:44:17.030090484 +0000
    sha1:           PvYQKtrTuYsMV2AomUeHrUWkCGg
    sha256:         QS82aXnPKA4XpfHr3umbA0r2iTbRcpWQ0VI2Qdhi6xg
…
```

활성 키를 숨겨진 키로 이동하기 위한 YAML 파일을 만듭니다(예: `minimal-keyretrieve-rotate-tangserver.yaml`).

```yaml
apiVersion: daemons.redhat.com/v1alpha1
kind: TangServer
metadata:
  name: tangserver
  namespace: nbde
  finalizers:
    - finalizer.daemons.tangserver.redhat.com
spec:
  replicas: 1
  hiddenKeys:
    - sha1: "PvYQKtrTuYsMV2AomUeHrUWkCGg"
```

1. 회전할 활성 키의 SHA-1 지문을 지정합니다.

YAML 파일을 적용합니다.

```shell-session
$ oc apply -f minimal-keyretrieve-rotate-tangserver.yaml
```

검증

구성에 따라 일정 시간이 지나면 이전 `activeKey` 값이 새 `hiddenKey` 값이고 `activeKey` 키 파일이 새로 생성되었는지 확인합니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc -n nbde describe tangserver
```

```shell-session
…
Spec:
  Hidden Keys:
    sha1:    PvYQKtrTuYsMV2AomUeHrUWkCGg
  Replicas:  1
Status:
  Active Keys:
    File Name:  T-0wx1HusMeWx4WMOk4eK97Q5u4dY5tamdDs7_ughnY.jwk
    Generated:  2023-10-25 15:38:18.134939752 +0000
    sha1:       vVxkNCNq7gygeeA9zrHrbc3_NZ4
    sha256:     T-0wx1HusMeWx4WMOk4eK97Q5u4dY5tamdDs7_ughnY
  Hidden Keys:
    File Name:           .QS82aXnPKA4XpfHr3umbA0r2iTbRcpWQ0VI2Qdhi6xg.jwk
    Generated:           2023-10-25 15:37:29.126928965 +0000
    Hidden:              2023-10-25 15:38:13.515467436 +0000
    sha1:                PvYQKtrTuYsMV2AomUeHrUWkCGg
    sha256:              QS82aXnPKA4XpfHr3umbA0r2iTbRcpWQ0VI2Qdhi6xg
…
```

#### 8.5.3. NBDE Tang Server Operator를 사용하여 숨겨진 키 삭제

Tang 서버 키를 순환하면 이전 활성 키가 숨겨지고 Tang 인스턴스에서 더 이상 광고하지 않습니다. NBDE Tang Server Operator를 사용하여 더 이상 사용되지 않는 암호화 키를 제거할 수 있습니다.

경고

바인딩된 모든 Clevis 클라이언트가 이미 새 키를 사용하는지 확인하지 않는 한 숨겨진 키를 제거하지 마십시오.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 `cluster-admin` 권한이 있어야 합니다.

OpenShift 클러스터에서 NBDE Tang Server Operator를 사용하여 Tang 서버를 배포했습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

Tang 서버의 기존 키를 나열합니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc -n nbde describe tangserver
```

```shell-session
…
Status:
  Active Keys:
    File Name:      PvYQKtrTuYsMV2AomUeHrUWkCGg.jwk
    Generated:      2022-02-08 15:44:17.030090484 +0000
    sha1:           PvYQKtrTuYsMV2AomUeHrUWkCGg
    sha256:         QS82aXnPKA4XpfHr3umbA0r2iTbRcpWQ0VI2Qdhi6xg
…
```

숨겨진 키를 제거하기 위한 YAML 파일을 만듭니다(예: `hidden-keys-deletion-tangserver.yaml`):

```yaml
apiVersion: daemons.redhat.com/v1alpha1
kind: TangServer
metadata:
  name: tangserver
  namespace: nbde
  finalizers:
    - finalizer.daemons.tangserver.redhat.com
spec:
  replicas: 1
  hiddenKeys: []
```

1. `hiddenKeys` 항목의 값으로 빈 배열은 Tang 서버에서 숨겨진 키를 유지하지 않으려는 것을 나타냅니다.

YAML 파일을 적용합니다.

```shell-session
$ oc apply -f hidden-keys-deletion-tangserver.yaml
```

검증

구성에 따라 일정 시간이 지나면 이전 활성 키가 계속 존재하지만 숨겨진 키를 사용할 수 있는지 확인합니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc -n nbde describe tangserver
```

```shell-session
…
Spec:
  Hidden Keys:
    sha1:    PvYQKtrTuYsMV2AomUeHrUWkCGg
  Replicas:  1
Status:
  Active Keys:
    File Name:  T-0wx1HusMeWx4WMOk4eK97Q5u4dY5tamdDs7_ughnY.jwk
    Generated:  2023-10-25 15:38:18.134939752 +0000
    sha1:       vVxkNCNq7gygeeA9zrHrbc3_NZ4
    sha256:     T-0wx1HusMeWx4WMOk4eK97Q5u4dY5tamdDs7_ughnY
Status:
  Ready:                 1
  Running:               1
  Service External URL:  http://35.222.247.84:7500/adv
  Tang Server Error:     No
Events:
…
```

### 8.6. NBDE Tang Server Operator로 배포된 Tang 서버의 URL 확인

Tang 서버에서 알리는 암호화 키를 사용하도록 Clevis 클라이언트를 구성하려면 서버의 URL을 식별해야 합니다.

#### 8.6.1. 웹 콘솔을 사용하여 NBDE Tang Server Operator의 URL 확인

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-19-tangserver-details.png" alt="NBDE Tang Server Operator 세부 정보" kind="figure" diagram_type="image_figure"]
NBDE Tang Server Operator 세부 정보
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/f7764b939f8d836f58a5e48f6c2ae10e/nbde-tang-server-operator-19-tangserver-details.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/nbde-tang-server-operator-21-tangserver-overview.png" alt="Tang 서버의 NBDE Tang Server Operator 개요" kind="diagram" diagram_type="semantic_diagram"]
Tang 서버의 NBDE Tang Server Operator 개요
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/4e68b22420a623d8fe0ff5b7e2fd056b/nbde-tang-server-operator-21-tangserver-overview.png`_


OpenShift Container Platform 웹 콘솔을 사용하여 소프트웨어 카탈로그에서 NBDE Tang Server Operator와 함께 배포된 Tang 서버의 URL을 확인할 수 있습니다. URL을 확인한 후 Tang 서버에서 알리는 키를 사용하여 자동으로 잠금 해제하려는 LUKS 암호화 볼륨이 포함된 클라이언트에서 `clevis luks bind` 명령을 사용합니다. Clevis를 사용한 클라이언트 구성을 설명하는 자세한 단계는 RHEL 9 보안 강화 문서의 LUKS 암호화 볼륨 수동 등록 구성 섹션을 참조하십시오.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 `cluster-admin` 권한이 있어야 합니다.

OpenShift 클러스터에서 NBDE Tang Server Operator를 사용하여 Tang 서버를 배포했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 Ecosystem → Installed Operators → Tang Server 로 이동합니다.

NBDE Tang Server Operator 세부 정보 페이지에서 Tang Server 를 선택합니다.

배포된 Tang 서버 목록이 클러스터에 표시됩니다. Clevis 클라이언트와 바인딩할 Tang 서버의 이름을 클릭합니다.

웹 콘솔에는 선택한 Tang 서버의 개요가 표시됩니다. 화면의 Tang `서버 외부 Url 섹션에서 Tang` 서버의 URL을 찾을 수 있습니다.

이 예에서 Tang 서버의 URL은 `http://34.28.173.205:7500` 입니다.

검증

다음 명령, `wget` 또는 유사한 툴을 사용하여 Tang 서버가 광고하고 있는지 확인할 수 있습니다. 예를 들면 다음과 같습니다.

```shell
curl
```

```shell-session
$ curl 2> /dev/null http://34.28.173.205:7500/adv  | jq
```

```shell-session
{
  "payload": "eyJrZXlzIj…eSJdfV19",
  "protected": "eyJhbGciOiJFUzUxMiIsImN0eSI6Imp3ay1zZXQranNvbiJ9",
  "signature": "AUB0qSFx0FJLeTU…aV_GYWlDx50vCXKNyMMCRx"
}
```

#### 8.6.2. CLI를 사용하여 NBDE Tang Server Operator의 URL 확인

CLI를 사용하여 소프트웨어 카탈로그에서 NBDE Tang Server Operator와 함께 배포된 Tang 서버의 URL을 확인할 수 있습니다. URL을 확인한 후 Tang 서버에서 알리는 키를 사용하여 자동으로 잠금 해제하려는 LUKS 암호화 볼륨이 포함된 클라이언트에서 `clevis luks bind` 명령을 사용합니다. Clevis를 사용한 클라이언트 구성을 설명하는 자세한 단계는 RHEL 9 보안 강화 문서의 LUKS 암호화 볼륨 수동 등록 구성 섹션을 참조하십시오.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 `cluster-admin` 권한이 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

OpenShift 클러스터에서 NBDE Tang Server Operator를 사용하여 Tang 서버를 배포했습니다.

프로세스

Tang 서버에 대한 세부 정보를 나열합니다. 예를 들면 다음과 같습니다.

```shell-session
$ oc -n nbde describe tangserver
```

```shell-session
…
Spec:
…
Status:
  Ready:                 1
  Running:               1
  Service External URL:  http://34.28.173.205:7500/adv
  Tang Server Error:     No
Events:
…
```

`/adv` 부분이 없는 `Service External URL:` 항목의 값을 사용합니다. 이 예에서 Tang 서버의 URL은 `http://34.28.173.205:7500` 입니다.

검증

다음 명령, `wget` 또는 유사한 툴을 사용하여 Tang 서버가 광고하고 있는지 확인할 수 있습니다. 예를 들면 다음과 같습니다.

```shell
curl
```

```shell-session
$ curl 2> /dev/null http://34.28.173.205:7500/adv  | jq
```

```shell-session
{
  "payload": "eyJrZXlzIj…eSJdfV19",
  "protected": "eyJhbGciOiJFUzUxMiIsImN0eSI6Imp3ay1zZXQranNvbiJ9",
  "signature": "AUB0qSFx0FJLeTU…aV_GYWlDx50vCXKNyMMCRx"
}
```

#### 8.6.3. 추가 리소스

RHEL 9 보안 강화 문서에서 LUKS 암호화 볼륨 수동 등록 섹션 구성.

### 9.1. cert-manager Operator for Red Hat OpenShift 개요

cert-manager Operator for Red Hat OpenShift는 애플리케이션 인증서 라이프사이클 관리를 제공하는 클러스터 전체 서비스입니다. cert-manager Operator for Red Hat OpenShift를 사용하면 외부 인증 기관과 통합하고 인증서 프로비저닝, 갱신 및 폐기를 제공할 수 있습니다.

#### 9.1.1. cert-manager Operator for Red Hat OpenShift 정보

cert-manager 프로젝트는 인증 기관 및 인증서를 Kubernetes API의 리소스 유형으로 도입하므로 클러스터 내에서 작업하는 개발자에게 필요에 따라 인증서를 제공할 수 있습니다. cert-manager Operator for Red Hat OpenShift는 cert-manager를 OpenShift Container Platform 클러스터에 통합하는 데 지원되는 방법을 제공합니다.

cert-manager Operator for Red Hat OpenShift는 다음과 같은 기능을 제공합니다.

외부 인증 기관과 통합 지원

인증서를 관리하는 툴

개발자가 인증서를 자체 예약할 수 있는 기능

인증서 갱신 자동

중요

OpenShift Container Platform용 Red Hat OpenShift용 cert-manager Operator와 클러스터에서 동시에 커뮤니티 cert-manager Operator를 모두 사용하지 마십시오.

또한 단일 OpenShift 클러스터 내의 여러 네임스페이스에 OpenShift Container Platform용 cert-manager Operator를 설치하지 않아야 합니다.

#### 9.1.2. cert-manager Operator for Red Hat OpenShift issuer 공급자

cert-manager Operator for Red Hat OpenShift는 다음과 같은 발행자 유형으로 테스트되었습니다.

ACME(Automated Certificate Management Environment)

인증 기관(CA)

자체 서명

Vault

Venafi

Nokia NetGuard Certificate Manager (NCM)

Google 클라우드 인증 기관 서비스 (Google CAS)

#### 9.1.2.1. 발행자 유형 테스트

다음 표에서는 테스트된 각 발행자 유형에 대한 테스트 범위를 간략하게 설명합니다.

| 발행자 유형 | 테스트 상태 | 참고 |
| --- | --- | --- |
| ACME | 완전히 테스트됨 | 표준 ACME 구현으로 검증되었습니다. |
| CA | 완전히 테스트됨 | 기본 CA 기능을 보장합니다. |
| 자체 서명 | 완전히 테스트됨 | 자체 서명된 기본 기능을 보장합니다. |
| Vault | 완전히 테스트됨 | 인프라 액세스 제약 조건으로 인해 표준 Vault 설정으로 제한됩니다. |
| Venafi | 부분적으로 테스트됨 | 공급자별 제한에 따라 다릅니다. |
| NCM | 부분적으로 테스트됨 | 공급자별 제한에 따라 다릅니다. |
| Google CAS | 부분적으로 테스트됨 | 일반적인 CA 구성과 호환됩니다. |

참고

OpenShift Container Platform은 Red Hat OpenShift 공급자 기능용 타사 cert-manager Operator와 관련된 모든 요소를 테스트하지 않습니다. 타사 지원에 대한 자세한 내용은 OpenShift Container Platform 타사 지원 정책을 참조하십시오.

#### 9.1.3. 인증서 요청 방법

cert-manager Operator for Red Hat OpenShift를 사용하여 인증서를 요청하는 방법은 다음 두 가지가 있습니다.

`cert-manager.io/CertificateRequest` 오브젝트 사용

이 방법을 사용하면 서비스 개발자가 구성된 발행자(서비스 인프라 관리자가 구성)를 가리키는 유효한 `issuerRef` 를 사용하여 `CertificateRequest` 오브젝트를 생성합니다. 그러면 서비스 인프라 관리자가 인증서 요청을 수락하거나 거부합니다. 허용되는 인증서 요청만 해당 인증서를 생성합니다.

`cert-manager.io/Certificate` 오브젝트 사용

이 방법을 사용하면 서비스 개발자가 유효한 `issuerRef` 를 사용하여 `Certificate` 오브젝트를 생성하고 `Certificate` 오브젝트를 가리키는 보안에서 인증서를 가져옵니다.

#### 9.1.4. Red Hat OpenShift 버전에 지원되는 cert-manager Operator

다른 OpenShift Container Platform 릴리스에서 Red Hat OpenShift용 cert-manager Operator의 지원되는 버전 목록은 OpenShift Container Platform 업데이트 및 지원 정책의 "플랫폼 Agnostic Operator" 섹션을 참조하십시오.

#### 9.1.5. cert-manager Operator for Red Hat OpenShift에 대한 FIPS 컴플라이언스 정보

버전 1.14.0부터 cert-manager Operator for Red Hat OpenShift는 FIPS 준수를 위해 설계되었습니다. FIPS 모드에서 OpenShift Container Platform을 실행하는 경우 x86_64, ppc64le 및 s390X 아키텍처에서 FIPS 검증을 위해 NIST에 제출된 RHEL 암호화 라이브러리를 사용합니다. NIST 검증 프로그램에 대한 자세한 내용은 암호화 모듈 검증 프로그램을 참조하십시오. 검증을 위해 제출된 개별 RHEL 암호화 라이브러리의 최신 NIST 상태는 규정 준수 활동 및 정부 표준을 참조하십시오.

FIPS 모드를 활성화하려면 FIPS 모드에서 작동하도록 구성된 OpenShift Container Platform 클러스터에 cert-manager Operator for Red Hat OpenShift를 설치해야 합니다. 자세한 내용은 "클러스터에 추가 보안이 필요합니까?"를 참조하십시오.

#### 9.1.6. 추가 리소스

cert-manager 프로젝트 문서

컴플라이언스 이해

FIPS 모드에서 클러스터 설치

클러스터에 추가 보안이 필요하십니까?

### 9.2. cert-manager Operator for Red Hat OpenShift 릴리스 정보

cert-manager Operator for Red Hat OpenShift는 애플리케이션 인증서 라이프사이클 관리를 제공하는 클러스터 전체 서비스입니다.

이 릴리스 노트에서는 cert-manager Operator for Red Hat OpenShift의 개발을 추적합니다.

자세한 내용은 cert-manager Operator for Red Hat OpenShift 에서 참조하십시오.

#### 9.2.1. cert-manager Operator for Red Hat OpenShift 1.18.0

출시 날짜: 2025-11-12

cert-manager Operator for Red Hat OpenShift 1.18.0에 다음 권고를 사용할 수 있습니다.

RHBA-2025:21087

RHBA-2025:21086

RHBA-2025:21088

RHBA-2025:21114

Red Hat OpenShift용 cert-manager Operator의 버전 `1.18.0` 은 업스트림 cert-manager 버전 `v1.18.3` 을 기반으로 합니다. 자세한 내용은 v1.18.3의 cert-manager 프로젝트 릴리스 노트를 참조하십시오.

#### 9.2.1.1. 새로운 기능 및 개선 사항

Red Hat OpenShift 용 cert-manager Operator와 Istio-CSR 통합 (일반 사용 가능)

이번 릴리스에서는 이전에 기술 프리뷰 기능으로 제공된 Istio-CSR과 cert-manager Operator for Red Hat OpenShift의 통합이 완전히 지원됩니다. 이 기능은 Red Hat OpenShift Service Mesh 또는 Istio 환경 내의 워크로드 및 컨트롤 플레인 구성 요소를 보호하기 위한 향상된 지원을 제공합니다. Red Hat OpenShift 관리 Istio-CSR 에이전트를 위한 cert-manager Operator를 사용하면 Istio는 상호 TLS(mTLS)에 필요한 인증서를 취득, 서명, 제공 및 갱신할 수 있습니다. 자세한 내용은 cert-manager Operator with Istio-CSR 의 통합을 참조하십시오.

cert-manager Operator for Red Hat OpenShift 피연산자의 복제본 수 구성

이번 릴리스에서는 Red Hat OpenShift `컨트롤러`, `웹 후크` 및 `cainjector` 피연산자에 대한 cert-manager Operator의 기본 복제본 수를 덮어쓸 수 있습니다. 이러한 값을 구성하려면 `CertManager` 사용자 정의 리소스에서 새 `overrideReplicas` 필드를 지정합니다. 이번 개선된 기능을 통해 특정 운영 요구 사항에 따라 HA(고가용성) 및 스케일 피연산자를 구성할 수 있습니다. 자세한 내용은 cert-manager 구성 요소에 대한 CertManager CR의 공통 구성 가능한 필드를 참조하십시오.

루트 파일 시스템은 Red Hat OpenShift 컨테이너용 cert-manager Operator에 대해 읽기 전용입니다.

이번 릴리스에서는 보안을 개선하기 위해 cert-manager Operator for Red Hat OpenShift 및 모든 피연산자에는 기본적으로 `readOnlyRootFilesystem` 보안 컨텍스트가 `true` 로 설정되어 있습니다. 이번 개선된 기능을 통해 컨테이너가 강화되고 잠재적인 공격자가 컨테이너 루트 파일 시스템의 내용을 수정하지 못하도록 합니다.

cert-manager Operator for Red Hat OpenShift 구성 요소에 네트워크 정책 강화 가능

이번 릴리스에서는 Red Hat OpenShift용 cert-manager Operator에 사전 정의된 `NetworkPolicy` 리소스가 포함되어 구성 요소에 대한 수신 및 송신 트래픽을 제어하여 보안을 강화합니다. 이러한 정책은 메트릭 및 웹 후크 서버에 대한 수신과 같은 내부 트래픽을 처리하고 OpenShift API 및 DNS 서버로의 송신을 포함합니다.

기본적으로 이 기능은 업그레이드 중에 연결 문제가 발생하지 않도록 비활성화되어 있습니다. `CertManager` 사용자 정의 리소스에서 명시적으로 활성화해야 합니다. 자세한 내용은 cert-manager Operator for Red Hat OpenShift에 대한 네트워크 정책 구성 을 참조하십시오.

#### 9.2.1.2. 확인된 문제

업스트림 cert-manager `v1.18` 릴리스에서는 ACME HTTP-01 챌린지 인그레스 경로 유형이 `ImplementationSpecific` 에서 `Exact` 로 업데이트되었습니다. OpenShift Route API에는 `Exact` 경로 유형과 동일한 기능이 없으므로 Ingress-to-route 컨트롤러가 이를 지원하지 않습니다. 결과적으로 HTTP-01 챌린지에 대해 생성된 수신 리소스는 트래픽을 솔버 Pod로 라우팅할 수 없으므로 503 오류와 함께 문제가 발생하지 않습니다. 이 문제를 완화하기 위해 이 릴리스에서는 `ACMEHTTP01IngressPathTypeExact` 기능 게이트가 기본적으로 비활성화되어 있습니다.

#### 9.2.2. cert-manager Operator for Red Hat OpenShift 1.17.0

출시 날짜: 2025-08-06

cert-manager Operator for Red Hat OpenShift 1.17.0에 다음 권고를 사용할 수 있습니다.

RHBA-2025:13182

RHBA-2025:13134

RHBA-2025:13133

Red Hat OpenShift 용 cert-manager Operator의 버전 `1.17.0` 은 업스트림 cert-manager 버전 `v1.17.4` 를 기반으로 합니다. 자세한 내용은 v1.17.4의 cert-manager 프로젝트 릴리스 노트를 참조하십시오.

#### 9.2.2.1. 버그 수정

이전에는 Istio-CSR을 성공적으로 배포한 후에도 `IstioCSR` CR(사용자 정의 리소스)의 `status` 필드가 `Ready` 로 설정되지 않았습니다. 이번 수정을 통해 `status` 필드가 `Ready` 로 올바르게 설정되어 일관성 있고 안정적인 상태 보고가 보장됩니다. (CM-546)

#### 9.2.2.2. 새로운 기능 및 개선 사항

ACME HTTP-01 솔버 Pod에 대한 리소스 요청 및 제한 구성 지원

이번 릴리스에서는 cert-manager Operator for Red Hat OpenShift에서 ACME HTTP-01 솔버 Pod에 대한 CPU 및 메모리 리소스 요청 및 제한 구성을 지원합니다. `CertManager` CR(사용자 정의 리소스)에서 다음과 같이 덮어쓸 수 있는 인수를 사용하여 CPU 및 메모리 리소스 요청 및 제한을 구성할 수 있습니다.

`--acme-http01-solver-resource-limits-cpu`

`--acme-http01-solver-resource-limits-memory`

`--acme-http01-solver-resource-request-cpu`

`--acme-http01-solver-resource-request-memory`

자세한 내용은 cert-manager 구성 요소에 대한 덮어쓰기 가능 인수를 참조하십시오.

#### 9.2.2.3. CVE

CVE-2025-22866

CVE-2025-22868

CVE-2025-22872

CVE-2025-22870

CVE-2025-27144

CVE-2025-22871

### 9.3. cert-manager Operator for Red Hat OpenShift 설치

중요

cert-manager Operator for Red Hat OpenShift 버전 1.15 이상에서는 `AllNamespaces`, `SingleNamespace` s 및 `OwnNamespace` 설치 모드를 지원합니다. 1.14와 같은 이전 버전은 `SingleNamespace` 및 `OwnNamespace` 설치 모드만 지원합니다.

cert-manager Operator for Red Hat OpenShift는 기본적으로 OpenShift Container Platform에 설치되지 않습니다. 웹 콘솔을 사용하여 cert-manager Operator for Red Hat OpenShift를 설치할 수 있습니다.

#### 9.3.1.1. 웹 콘솔을 사용하여 cert-manager Operator for Red Hat OpenShift 설치

웹 콘솔을 사용하여 cert-manager Operator for Red Hat OpenShift를 설치할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

에코시스템 → 소프트웨어 카탈로그 로 이동합니다.

cert-manager Operator for Red Hat OpenShift 를 필터 상자에 입력합니다.

cert-manager Operator for Red Hat OpenShift 선택

cert-manager Operator for Red Hat OpenShift 버전을 버전 드롭다운 목록에서 선택하고 설치를 클릭합니다.

참고

다음 "추가 리소스" 섹션에서 지원되는 cert-manager Operator for Red Hat OpenShift 버전을 참조하십시오.

Operator 설치 페이지에서 다음을 수행합니다.

필요한 경우 업데이트 채널을 업데이트합니다. 채널은 기본적으로 stable-v1 로, cert-manager Operator for Red Hat OpenShift의 안정적인 최신 릴리스를 설치합니다.

Operator의 설치된 네임스페이스 를 선택합니다. 기본 Operator 네임스페이스는 `cert-manager-operator` 입니다.

`cert-manager-operator` 네임스페이스가 없으면 해당 네임스페이스가 생성됩니다.

참고

설치 중에 OpenShift Container Platform 웹 콘솔을 사용하면 `AllNamespaces` 와 `SingleNamespace` 설치 모드 중에서 선택할 수 있습니다. cert-manager Operator for Red Hat OpenShift 버전 1.15.0 이상을 사용하는 경우 `AllNamespaces` 설치 모드를 선택하는 것이 좋습니다. `SingleNamespace` 및 `OwnNamespace` 지원은 이전 버전에서 유지되지만 향후 버전에서는 더 이상 사용되지 않습니다.

업데이트 승인 전략을 선택합니다.

자동 전략을 사용하면 Operator 새 버전이 준비될 때 OLM(Operator Lifecycle Manager)이 자동으로 Operator를 업데이트할 수 있습니다.

수동 전략을 사용하려면 적절한 자격 증명을 가진 사용자가 Operator 업데이트를 승인해야 합니다.

설치 를 클릭합니다.

검증

Ecosystem → 설치된 Operators 로 이동합니다.

cert-manager Operator for Red Hat OpenShift 가 `cert-manager-operator` 네임스페이스에 Succeeded

상태 로 나열되어 있는지 확인합니다.

다음 명령을 입력하여 cert-manager Pod가 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n cert-manager
```

```shell-session
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-bd7fbb9fc-wvbbt               1/1     Running   0          3m39s
cert-manager-cainjector-56cc5f9868-7g9z7   1/1     Running   0          4m5s
cert-manager-webhook-d4f79d7f7-9dg9w       1/1     Running   0          4m9s
```

cert-manager Pod가 가동되어 실행된 경우에만 cert-manager Operator를 Red Hat OpenShift에 사용할 수 있습니다.

#### 9.3.1.2. CLI를 사용하여 Red Hat OpenShift용 cert-manager Operator 설치

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 `cert-manager-operator` 라는 새 프로젝트를 생성합니다.

```shell-session
$ oc new-project cert-manager-operator
```

`OperatorGroup` 오브젝트를 생성합니다.

다음 콘텐츠를 사용하여 YAML 파일(예: `operatorGroup.yaml`)을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-cert-manager-operator
  namespace: cert-manager-operator
spec:
  targetNamespaces:
  - "cert-manager-operator"
```

cert-manager Operator for Red Hat OpenShift v1.15.0 이상의 경우 다음 콘텐츠를 사용하여 YAML 파일을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-cert-manager-operator
  namespace: cert-manager-operator
spec:
  targetNamespaces: []
  spec: {}
```

참고

cert-manager Operator for Red Hat OpenShift 버전 1.15.0부터 `AllNamespaces` OLM `installMode` 를 사용하여 Operator를 설치하는 것이 좋습니다. 이전 버전에서는 `SingleNamespace` 또는 `OwnNamespace` OLM `installMode` 를 계속 사용할 수 있습니다. `SingleNamespace` 및 `OwnNamespace` 에 대한 지원은 향후 버전에서 더 이상 사용되지 않습니다.

다음 명령을 실행하여 `OperatorGroup` 오브젝트를 생성합니다.

```shell-session
$ oc create -f operatorGroup.yaml
```

`Subscription` 오브젝트를 생성합니다.

`Subscription` 오브젝트를 정의하는 YAML 파일(예: `subscription.yaml`)을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-cert-manager-operator
  namespace: cert-manager-operator
spec:
  channel: stable-v1
  name: openshift-cert-manager-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
```

다음 명령을 실행하여 서브스크립션 오브젝트를 생성합니다.

```shell-session
$ oc create -f subscription.yaml
```

검증

다음 명령을 실행하여 OLM 서브스크립션이 생성되었는지 확인합니다.

```shell-session
$ oc get subscription -n cert-manager-operator
```

```shell-session
NAME                              PACKAGE                           SOURCE             CHANNEL
openshift-cert-manager-operator   openshift-cert-manager-operator   redhat-operators   stable-v1
```

다음 명령을 실행하여 Operator가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get csv -n cert-manager-operator
```

```shell-session
NAME                            DISPLAY                                       VERSION   REPLACES                        PHASE
cert-manager-operator.v1.13.0   cert-manager Operator for Red Hat OpenShift   1.13.0    cert-manager-operator.v1.12.1   Succeeded
```

다음 명령을 실행하여 Red Hat OpenShift용 cert-manager Operator 상태가 `Running` 인지 확인합니다.

```shell-session
$ oc get pods -n cert-manager-operator
```

```shell-session
NAME                                                        READY   STATUS    RESTARTS   AGE
cert-manager-operator-controller-manager-695b4d46cb-r4hld   2/2     Running   0          7m4s
```

다음 명령을 실행하여 cert-manager pod의 상태가 `Running` 인지 확인합니다.

```shell-session
$ oc get pods -n cert-manager
```

```shell-session
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-58b7f649c4-dp6l4              1/1     Running   0          7m1s
cert-manager-cainjector-5565b8f897-gx25h   1/1     Running   0          7m37s
cert-manager-webhook-9bc98cbdd-f972x       1/1     Running   0          7m40s
```

추가 리소스

Red Hat OpenShift 버전에 지원되는 cert-manager Operator

#### 9.3.2. cert-manager Operator for Red Hat OpenShift의 업데이트 채널 이해

업데이트 채널은 클러스터에서 Red Hat OpenShift용 cert-manager Operator 버전을 선언할 수 있는 메커니즘입니다. cert-manager Operator for Red Hat OpenShift는 다음과 같은 업데이트 채널을 제공합니다.

`stable-v1`

`stable-v1.y`

#### 9.3.2.1. stable-v1 채널

`stable-v1` 채널에서는 Red Hat OpenShift용 cert-manager Operator의 최신 릴리스 버전을 설치하고 업데이트합니다. Red Hat OpenShift용 cert-manager Operator의 안정적인 최신 릴리스를 사용하려면 `stable-v1` 채널을 선택합니다.

참고

`stable-v1` 채널은 cert-manager Operator for Red Hat OpenShift를 설치하는 동안 기본 및 제안된 채널입니다.

`stable-v1` 채널에서는 다음과 같은 업데이트 승인 전략을 제공합니다.

자동

설치된 cert-manager Operator for Red Hat OpenShift에 대한 자동 업데이트를 선택하면 새 버전의 cert-manager Operator for Red Hat OpenShift를 `stable-v1` 채널에서 사용할 수 있습니다. OLM(Operator Lifecycle Manager)은 개입 없이 Operator의 실행 중인 인스턴스를 자동으로 업그레이드합니다.

수동

수동 업데이트를 선택하면 최신 버전의 cert-manager Operator for Red Hat OpenShift를 사용할 수 있으면 OLM에서 업데이트 요청을 생성합니다. 그런 다음 클러스터 관리자는 cert-manager Operator for Red Hat OpenShift가 새 버전으로 업데이트되도록 해당 업데이트 요청을 수동으로 승인해야 합니다.

#### 9.3.2.2. stable-v1.y channel

Red Hat OpenShift용 cert-manager Operator의 y-stream 버전에서는 `stable-v1.y` 채널(예: `stable-v1.10`, `stable-v1.11`, `stable-v1.12`)에서 업데이트를 설치합니다. y-stream 버전을 사용하려면 `stable-v1.y` 채널을 선택하고 Red Hat OpenShift용 cert-manager Operator의 z-stream 버전으로 계속 업데이트하십시오.

`stable-v1.y` 채널에서는 다음과 같은 업데이트 승인 전략을 제공합니다.

자동

설치된 cert-manager Operator for Red Hat OpenShift에 대한 자동 업데이트를 선택하는 경우 `stable-v1.y` 채널에서 cert-manager Operator for Red Hat OpenShift의 새로운 z-stream 버전을 사용할 수 있습니다. OLM은 개입 없이 Operator의 실행 중인 인스턴스를 자동으로 업그레이드합니다.

수동

수동 업데이트를 선택하면 최신 버전의 cert-manager Operator for Red Hat OpenShift를 사용할 수 있으면 OLM에서 업데이트 요청을 생성합니다. 그런 다음 클러스터 관리자는 cert-manager Operator for Red Hat OpenShift가 새 버전의 z-stream 릴리스로 업데이트되도록 해당 업데이트 요청을 수동으로 승인해야 합니다.

#### 9.3.3. 추가 리소스

클러스터에 Operator 추가

설치된 Operator 업데이트

### 9.4. cert-manager Operator for Red Hat OpenShift에 대한 송신 프록시 구성

클러스터 전체 송신 프록시가 OpenShift Container Platform에 구성된 경우 OLM(Operator Lifecycle Manager)은 클러스터 전체 프록시로 관리하는 Operator를 자동으로 구성합니다. OLM은 `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` 환경 변수를 사용하여 모든 Operator의 배포를 자동으로 업데이트합니다.

cert-manager Operator for Red Hat OpenShift에 HTTPS 연결을 프록시하는 데 필요한 모든 CA 인증서를 삽입할 수 있습니다.

#### 9.4.1. cert-manager Operator for Red Hat OpenShift용 사용자 정의 CA 인증서 삽입

OpenShift Container Platform 클러스터에 클러스터 전체 프록시가 활성화된 경우 cert-manager Operator for Red Hat OpenShift에 HTTPS 연결을 프록시하는 데 필요한 CA 인증서를 삽입할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift Container Platform에 대해 클러스터 전체 프록시를 활성화했습니다.

프로세스

다음 명령을 실행하여 `cert-manager` 네임스페이스에 구성 맵을 생성합니다.

```shell-session
$ oc create configmap trusted-ca -n cert-manager
```

다음 명령을 실행하여 OpenShift Container Platform에서 신뢰하는 CA 번들을 구성 맵에 삽입합니다.

```shell-session
$ oc label cm trusted-ca config.openshift.io/inject-trusted-cabundle=true -n cert-manager
```

다음 명령을 실행하여 Red Hat OpenShift용 cert-manager Operator 배포를 업데이트하여 구성 맵을 사용합니다.

```shell-session
$ oc -n cert-manager-operator patch subscription openshift-cert-manager-operator --type='merge' -p '{"spec":{"config":{"env":[{"name":"TRUSTED_CA_CONFIGMAP_NAME","value":"trusted-ca"}]}}}'
```

검증

다음 명령을 실행하여 배포 롤아웃이 완료되었는지 확인합니다.

```shell-session
$ oc rollout status deployment/cert-manager-operator-controller-manager -n cert-manager-operator && \
oc rollout status deployment/cert-manager -n cert-manager && \
oc rollout status deployment/cert-manager-webhook -n cert-manager && \
oc rollout status deployment/cert-manager-cainjector -n cert-manager
```

```shell-session
deployment "cert-manager-operator-controller-manager" successfully rolled out
deployment "cert-manager" successfully rolled out
deployment "cert-manager-webhook" successfully rolled out
deployment "cert-manager-cainjector" successfully rolled out
```

다음 명령을 실행하여 CA 번들이 볼륨으로 마운트되었는지 확인합니다.

```shell-session
$ oc get deployment cert-manager -n cert-manager -o=jsonpath={.spec.template.spec.'containers[0].volumeMounts'}
```

```shell-session
[{"mountPath":"/etc/pki/tls/certs/cert-manager-tls-ca-bundle.crt","name":"trusted-ca","subPath":"ca-bundle.crt"}]
```

다음 명령을 실행하여 CA 번들의 소스가 `trusted-ca` 구성 맵인지 확인합니다.

```shell-session
$ oc get deployment cert-manager -n cert-manager -o=jsonpath={.spec.template.spec.volumes}
```

```shell-session
[{"configMap":{"defaultMode":420,"name":"trusted-ca"},"name":"trusted-ca"}]
```

#### 9.4.2. 추가 리소스

Operator Lifecycle Manager에서 프록시 지원 구성

### 9.5. CertManager 사용자 정의 리소스를 사용하여 cert-manager Operator 사용자 정의

Red Hat OpenShift용 cert-manager Operator를 설치한 후 `CertManager` CR(사용자 정의 리소스)을 구성하여 다음 작업을 수행할 수 있습니다.

cert-manager 컨트롤러, CA 인젝터, Webhook와 같은 cert-manager 구성 요소의 동작을 수정하도록 인수를 구성합니다.

컨트롤러 Pod의 환경 변수를 설정합니다.

CPU 및 메모리 사용량을 관리하기 위해 리소스 요청 및 제한을 정의합니다.

클러스터에서 Pod가 실행되는 위치를 제어하도록 스케줄링 규칙을 구성합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
spec:
  controllerConfig:
    overrideArgs:
      - "--dns01-recursive-nameservers=8.8.8.8:53,1.1.1.1:53"
    overrideEnv:
      - name: HTTP_PROXY
        value: http://proxy.example.com:8080
    overrideResources:
      limits:
        cpu: "200m"
        memory: "512Mi"
      requests:
        cpu: "100m"
        memory: "256Mi"
    overrideScheduling:
      nodeSelector:
        custom: "label"
      tolerations:
        - key: "key1"
          operator: "Equal"
          value: "value1"
          effect: "NoSchedule"
    overrideReplicas: 2
#...

  webhookConfig:
    overrideArgs:
#...
    overrideResources:
#...
    overrideScheduling:
#...
    overrideReplicas:
#...

  cainjectorConfig:
    overrideArgs:
#...
    overrideResources:
#...
    overrideScheduling:
#...
    overrideReplicas:
#...
```

주의

지원되지 않는 인수를 재정의하려면 `CertManager` 리소스에 `spec.unsupportedConfigOverrides` 섹션을 추가할 수 있지만 `spec.unsupportedConfigOverrides` 를 사용하는 것은 지원되지 않습니다.

#### 9.5.1. CertManager 사용자 정의 리소스의 필드에 대한 설명

`CertManager` CR(사용자 정의 리소스)을 사용하여 cert-manager Operator for Red Hat OpenShift의 다음 핵심 구성 요소를 구성할 수 있습니다.

cert-manager 컨트롤러: `spec.controllerConfig` 필드를 사용하여 cert-manager 컨트롤러 Pod를 구성할 수 있습니다.

Webhook: `spec.webhookConfig` 필드를 사용하여 검증 및 변경 요청을 처리하는 Webhook Pod를 구성할 수 있습니다.

CA injector: `spec.cainjectorConfig` 필드를 사용하여 CA 인젝터 Pod를 구성할 수 있습니다.

#### 9.5.1.1. cert-manager 구성 요소에 대한 CertManager CR의 구성 가능한 일반적인 필드

다음 표에는 `CertManager` CR의 `spec.controllerConfig`, `spec.webhookConfig` 및 `spec.cainjectorConfig` 섹션에서 구성할 수 있는 일반 필드가 나열되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `overrideArgs` | `string` | cert-manager 구성 요소에 대해 지원되는 인수를 덮어쓸 수 있습니다. |
| `overrideEnv` | `dict` | cert-manager 컨트롤러에 대해 지원되는 환경 변수를 덮어쓸 수 있습니다. 이 필드는 cert-manager 컨트롤러 구성 요소에 대해서만 지원됩니다. |
| `overrideReplicas` | `int` | cert-manager 구성 요소에 대한 복제본을 구성할 수 있습니다. 기본값은 `1` 입니다. 프로덕션 환경의 경우 다음 복제본 수를 사용하는 것이 좋습니다. controller: 2 cainjector: 2 Webhook: 최소 3개 자세한 내용은 고가용성 을 참조하십시오. |
| `overrideResources` | `object` | cert-manager 구성 요소에 대한 CPU 및 메모리 제한을 구성할 수 있습니다. |
| `overrideScheduling` | `object` | cert-manager 구성 요소에 대한 Pod 예약 제약 조건을 구성할 수 있습니다. |

#### 9.5.1.2. cert-manager 구성 요소에 대한 덮어쓰기 가능 인수

`CertManager` CR의 `spec.controllerConfig`, `spec.webhookConfig` 및 `spec.cainjectorConfig` 섹션에서 cert-manager 구성 요소에 대해 덮어쓸 수 있는 인수를 구성할 수 있습니다.

다음 표에서는 cert-manager 구성 요소에 대해 덮어쓸 수 있는 인수를 설명합니다.

| 인수 | Component | 설명 |
| --- | --- | --- |
| `--dns01-recursive-nameservers=<server_address>` | 컨트롤러 | DNS-01 자체 검사를 쿼리할 쉼표로 구분된 이름 서버 목록을 제공합니다. 네임서버는 < `host>:<port` > (예: `1.1.1.1:53` )로 지정하거나 HTTPS(DoH)를 통해 DNS를 사용할 수 있습니다(예: `https://1.1.1.1/dns-query` ). 참고 DoH(DNS over HTTPS)는 cert-manager Operator for Red Hat OpenShift 버전 1.13.0 이상에서만 지원됩니다. |
| `--dns01-recursive-nameservers-only` | 컨트롤러 | 해당 도메인과 연결된 권한 있는 이름 서버를 확인하는 대신 재귀 이름 서버만 사용하도록 지정합니다. |
| `--acme-http01-solver-nameservers=<host>:<port>` | 컨트롤러 | 쉼표로 구분된 < `host>:<port` > 네임서버 목록을 제공하여 ACME(Automated Certificate Management Environment) HTTP01 자체 검사를 쿼리합니다. 예를 들면 `--acme-http01-solver-nameservers=1.1.1.1:53` 입니다. |
| `--metrics-listen-address=<host>:<port>` | 컨트롤러 | 지표 끝점의 호스트 및 포트를 지정합니다. 기본값은 `--metrics-listen-address=0.0.0.0:9402` 입니다. |
| `--issuer-ambient-credentials` | 컨트롤러 | 이 인수를 사용하여 앰비언트 인증 정보를 사용하여 DNS-01 문제를 해결하기 위해 ACME 발행자를 구성할 수 있습니다. |
| `--enable-certificate-owner-ref` | 컨트롤러 | 이 인수는 인증서 리소스를 TLS 인증서가 저장된 보안의 소유자로 설정합니다. 자세한 내용은 "인증서 제거 시 자동으로 TLS 시크릿 삭제"를 참조하십시오. |
| `--acme-http01-solver-resource-limits-cpu` | 컨트롤러 | ACME HTTP-01 솔버 Pod의 최대 CPU 제한을 정의합니다. 기본값은 `100m` 입니다. |
| `--acme-http01-solver-resource-limits-memory` | 컨트롤러 | ACME HTTP-01 솔버 Pod의 최대 메모리 제한을 정의합니다. 기본값은 `64Mi` 입니다. |
| `--acme-http01-solver-resource-request-cpu` | 컨트롤러 | ACME HTTP-01 솔버 Pod의 최소 CPU 요청을 정의합니다. 기본값은 `10m` 입니다. |
| `--acme-http01-solver-resource-request-memory` | 컨트롤러 | ACME HTTP-01 솔버 Pod에 대한 최소 메모리 요청을 정의합니다. 기본값은 `64Mi` 입니다. |
| `--v=<verbosity_level>` | 컨트롤러, Webhook, CA 인젝터 | 로그 수준 상세 수준을 지정하여 로그 메시지의 상세 수준을 확인합니다. |

#### 9.5.1.3. cert-manager 컨트롤러에 대한 Overridable 환경 변수

`CertManager` CR의 `spec.controllerConfig.overrideEnv` 필드에서 cert-manager 컨트롤러에 대해 덮어쓸 수 있는 환경 변수를 구성할 수 있습니다.

다음 표에서는 cert-manager 컨트롤러에 대해 덮어쓸 수 있는 환경 변수를 설명합니다.

| 환경 변수 | 설명 |
| --- | --- |
| `HTTP_PROXY` | 발신 HTTP 요청에 대한 프록시 서버입니다. |
| `HTTPS_PROXY` | 발신 HTTPS 요청을 위한 프록시 서버입니다. |
| `NO_PROXY` | 프록시를 바이패스하는 쉼표로 구분된 호스트 목록입니다. |

#### 9.5.1.4. cert-manager 구성 요소에 대한 Overridable 리소스 매개변수

`CertManager` CR의 `spec.controllerConfig`, `spec.webhookConfig` 및 `spec.cainjectorConfig` 섹션에서 cert-manager 구성 요소에 대한 CPU 및 메모리 제한을 구성할 수 있습니다.

다음 표에서는 cert-manager 구성 요소에 대해 덮어쓸 수 있는 리소스 매개변수를 설명합니다.

| 필드 | 설명 |
| --- | --- |
| `overrideResources.limits.cpu` | 구성 요소 Pod에서 사용할 수 있는 최대 CPU 양을 정의합니다. |
| `overrideResources.limits.memory` | 구성 요소 Pod에서 사용할 수 있는 최대 메모리 양을 정의합니다. |
| `overrideResources.requests.cpu` | 구성 요소 Pod에 대해 스케줄러에서 요청하는 최소 CPU 양을 정의합니다. |
| `overrideResources.requests.memory` | 스케줄러에서 구성 요소 Pod에 대해 요청하는 최소 메모리 양을 정의합니다. |

#### 9.5.1.5. cert-manager 구성 요소에 대한 Overridable 스케줄링 매개변수

`CertManager` CR의 `spec.controllerConfig`, `spec.webhookConfig` 및 `spec.cainjectorConfig` 섹션에서 cert-manager 구성 요소에 대한 Pod 예약 제한을 구성할 수 있습니다.

다음 표에서는 cert-manager 구성 요소에 대한 Pod 예약 매개변수를 설명합니다.

| 필드 | 설명 |
| --- | --- |
| `overrideScheduling.nodeSelector` | Pod를 특정 노드로 제한하는 키-값 쌍입니다. |
| `overrideScheduling.tolerations` | 테인트된 노드에서 Pod를 예약하기 위한 허용 오차 목록입니다. |

추가 리소스

인증서 제거 시 자동으로 TLS 시크릿 삭제

#### 9.5.2. cert-manager Operator API에서 환경 변수를 재정의하여 cert-manager 사용자 정의

`CertManager` 리소스에 `spec.controllerConfig` 섹션을 추가하여 cert-manager Operator for Red Hat OpenShift에 대해 지원되는 환경 변수를 덮어쓸 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
  ...
spec:
  ...
  controllerConfig:
    overrideEnv:
      - name: HTTP_PROXY
        value: http://<proxy_url>
      - name: HTTPS_PROXY
        value: https://<proxy_url>
      - name: NO_PROXY
        value: <ignore_proxy_domains>
```

1. 2

&lt `;proxy_url&gt`;을 프록시 서버 URL로 바꿉니다.

3. & `lt;ignore_proxy_domains&gt`;를 쉼표로 구분된 도메인 목록으로 바꿉니다. 이러한 도메인은 프록시 서버에서 무시합니다.

참고

덮어쓸 수 있는 환경 변수에 대한 자세한 내용은 CertManager 사용자 정의 리소스의 "CertManager 사용자 정의 리소스의 필드 설명"의 "인증 관리자 구성 요소에 대한 개요 가능 환경 변수"를 참조하십시오.

변경 사항을 저장하고 텍스트 편집기를 종료하여 변경 사항을 적용합니다.

검증

다음 명령을 실행하여 cert-manager 컨트롤러 Pod가 재배포되었는지 확인합니다.

```shell-session
$ oc get pods -l app.kubernetes.io/name=cert-manager -n cert-manager
```

```shell-session
NAME                          READY   STATUS    RESTARTS   AGE
cert-manager-bd7fbb9fc-wvbbt  1/1     Running   0          39s
```

다음 명령을 실행하여 cert-manager Pod에 대한 환경 변수가 업데이트되었는지 확인합니다.

```shell-session
$ oc get pod <redeployed_cert-manager_controller_pod> -n cert-manager -o yaml
```

```yaml
env:
    ...
    - name: HTTP_PROXY
      value: http://<PROXY_URL>
    - name: HTTPS_PROXY
      value: https://<PROXY_URL>
    - name: NO_PROXY
      value: <IGNORE_PROXY_DOMAINS>
```

추가 리소스

CertManager 사용자 정의 리소스의 필드에 대한 설명

#### 9.5.3. cert-manager Operator API에서 인수를 재정의하여 cert-manager 사용자 정의

`CertManager` 리소스에 `spec.controllerConfig` 섹션을 추가하여 cert-manager Operator에 대해 지원되는 인수를 덮어쓸 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
  ...
spec:
  ...
  controllerConfig:
    overrideArgs:
      - '--dns01-recursive-nameservers=<server_address>'
      - '--dns01-recursive-nameservers-only'
      - '--acme-http01-solver-nameservers=<host>:<port>'
      - '--v=<verbosity_level>'
      - '--metrics-listen-address=<host>:<port>'
      - '--issuer-ambient-credentials'
      - '--acme-http01-solver-resource-limits-cpu=<quantity>'
      - '--acme-http01-solver-resource-limits-memory=<quantity>'
      - '--acme-http01-solver-resource-request-cpu=<quantity>'
      - '--acme-http01-solver-resource-request-memory=<quantity>'
  webhookConfig:
    overrideArgs:
      - '--v=<verbosity_level>'
  cainjectorConfig:
    overrideArgs:
      - '--v=<verbosity_level>'
```

1. 신뢰할 수 있는 문제에 대한 자세한 내용은 CertManager 사용자 정의 리소스의 "인증 관리자 구성 요소 설명"의 "인증 관리자 구성 요소에 대한 설명"을 참조하십시오.

변경 사항을 저장하고 텍스트 편집기를 종료하여 변경 사항을 적용합니다.

검증

다음 명령을 실행하여 cert-manager Pod에 대한 인수가 업데이트되었는지 확인합니다.

```shell-session
$ oc get pods -n cert-manager -o yaml
```

```yaml
...
  metadata:
    name: cert-manager-6d4b5d4c97-kldwl
    namespace: cert-manager
...
  spec:
    containers:
    - args:
      - --acme-http01-solver-nameservers=1.1.1.1:53
      - --cluster-resource-namespace=$(POD_NAMESPACE)
      - --dns01-recursive-nameservers=1.1.1.1:53
      - --dns01-recursive-nameservers-only
      - --leader-election-namespace=kube-system
      - --max-concurrent-challenges=60
      - --metrics-listen-address=0.0.0.0:9042
      - --v=6
...
  metadata:
    name: cert-manager-cainjector-866c4fd758-ltxxj
    namespace: cert-manager
...
  spec:
    containers:
    - args:
      - --leader-election-namespace=kube-system
      - --v=2
...
  metadata:
    name: cert-manager-webhook-6d48f88495-c88gd
    namespace: cert-manager
...
  spec:
    containers:
    - args:
      ...
      - --v=4
```

추가 리소스

CertManager 사용자 정의 리소스의 필드에 대한 설명

#### 9.5.4. 인증서 제거 시 자동으로 TLS 시크릿 삭제

`CertManager` 리소스에 `spec.controllerConfig` 섹션을 추가하여 cert-manager Operator for Red Hat OpenShift에 대해 `--enable-certificate-owner-ref` 플래그를 활성화할 수 있습니다. `--enable-certificate-owner-ref` 플래그는 인증서 리소스를 TLS 인증서가 저장된 보안의 소유자로 설정합니다.

주의

cert-manager Operator for Red Hat OpenShift를 설치 제거하거나 클러스터에서 인증서 리소스를 삭제하면 보안이 자동으로 삭제됩니다. 이로 인해 인증서 TLS 보안이 사용되는 위치에 따라 네트워크 연결 문제가 발생할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.12.0 이상이 설치되어 있어야 합니다.

프로세스

다음 명령을 실행하여 `Certificate` 오브젝트 및 해당 시크릿을 사용할 수 있는지 확인합니다.

```shell-session
$ oc get certificate
```

```shell-session
NAME                                             READY   SECRET                                           AGE
certificate-from-clusterissuer-route53-ambient   True    certificate-from-clusterissuer-route53-ambient   8h
```

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
# ...
spec:
# ...
  controllerConfig:
    overrideArgs:
      - '--enable-certificate-owner-ref'
```

변경 사항을 저장하고 텍스트 편집기를 종료하여 변경 사항을 적용합니다.

검증

다음 명령을 실행하여 cert-manager 컨트롤러 Pod에 대해 `--enable-certificate-owner-ref` 플래그가 업데이트되었는지 확인합니다.

```shell-session
$ oc get pods -l app.kubernetes.io/name=cert-manager -n cert-manager -o yaml
```

```yaml
# ...
  metadata:
    name: cert-manager-6e4b4d7d97-zmdnb
    namespace: cert-manager
# ...
  spec:
    containers:
    - args:
      - --enable-certificate-owner-ref
```

#### 9.5.5. cert-manager 구성 요소에 대한 CPU 및 메모리 제한 덮어쓰기

Red Hat OpenShift용 cert-manager Operator를 설치한 후 cert-manager 컨트롤러, CA 인젝터 및 Webhook와 같은 cert-manager 구성 요소에 대한 cert-manager Operator for Red Hat OpenShift API에서 CPU 및 메모리 제한을 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.12.0 이상이 설치되어 있어야 합니다.

프로세스

다음 명령을 입력하여 cert-manager 컨트롤러, CA 인젝터 및 Webhook의 배포를 사용할 수 있는지 확인합니다.

```shell-session
$ oc get deployment -n cert-manager
```

```shell-session
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager              1/1     1            1           53m
cert-manager-cainjector   1/1     1            1           53m
cert-manager-webhook      1/1     1            1           53m
```

CPU 및 메모리 제한을 설정하기 전에 다음 명령을 입력하여 cert-manager 컨트롤러, CA 인젝터 및 Webhook의 기존 구성을 확인합니다.

```shell-session
$ oc get deployment -n cert-manager -o yaml
```

```yaml
# ...
  metadata:
    name: cert-manager
    namespace: cert-manager
# ...
  spec:
    template:
      spec:
        containers:
        - name: cert-manager-controller
          resources: {}
# ...
  metadata:
    name: cert-manager-cainjector
    namespace: cert-manager
# ...
  spec:
    template:
      spec:
        containers:
        - name: cert-manager-cainjector
          resources: {}
# ...
  metadata:
    name: cert-manager-webhook
    namespace: cert-manager
# ...
  spec:
    template:
      spec:
        containers:
        - name: cert-manager-webhook
          resources: {}
# ...
```

1. 2

3. `spec.resources` 필드는 기본적으로 비어 있습니다. cert-manager 구성 요소에는 CPU 및 메모리 제한이 없습니다.

cert-manager 컨트롤러, CA 인젝터 및 Webhook에 대한 CPU 및 메모리 제한을 구성하려면 다음 명령을 입력합니다.

```shell-session
$ oc patch certmanager.operator cluster --type=merge -p="
spec:
  controllerConfig:
    overrideResources:
      limits:
        cpu: 200m
        memory: 64Mi
      requests:
        cpu: 10m
        memory: 16Mi
  webhookConfig:
    overrideResources:
      limits:
        cpu: 200m
        memory: 64Mi
      requests:
        cpu: 10m
        memory: 16Mi
  cainjectorConfig:
    overrideResources:
      limits:
        cpu: 200m
        memory: 64Mi
      requests:
        cpu: 10m
        memory: 16Mi
"
```

1. 덮어쓸 수 있는 리소스 매개변수에 대한 자세한 내용은 CertManager 사용자 정의 리소스의 "CertManager 사용자 정의 리소스의 필드 설명"의 "인증 관리자 구성 요소에 대한 리소스 매개변수"를 참조하십시오.

```shell-session
certmanager.operator.openshift.io/cluster patched
```

검증

cert-manager 구성 요소에 대해 CPU 및 메모리 제한이 업데이트되었는지 확인합니다.

```shell-session
$ oc get deployment -n cert-manager -o yaml
```

```yaml
# ...
  metadata:
    name: cert-manager
    namespace: cert-manager
# ...
  spec:
    template:
      spec:
        containers:
        - name: cert-manager-controller
          resources:
            limits:
              cpu: 200m
              memory: 64Mi
            requests:
              cpu: 10m
              memory: 16Mi
# ...
  metadata:
    name: cert-manager-cainjector
    namespace: cert-manager
# ...
  spec:
    template:
      spec:
        containers:
        - name: cert-manager-cainjector
          resources:
            limits:
              cpu: 200m
              memory: 64Mi
            requests:
              cpu: 10m
              memory: 16Mi
# ...
  metadata:
    name: cert-manager-webhook
    namespace: cert-manager
# ...
  spec:
    template:
      spec:
        containers:
        - name: cert-manager-webhook
          resources:
            limits:
              cpu: 200m
              memory: 64Mi
            requests:
              cpu: 10m
              memory: 16Mi
# ...
```

추가 리소스

CertManager 사용자 정의 리소스의 필드에 대한 설명

#### 9.5.6. cert-manager 구성 요소에 대한 스케줄링 덮어쓰기 구성

cert-manager 컨트롤러, CA 인젝터, Webhook와 같은 cert-manager Operator for Red Hat OpenShift 구성 요소에 대해 cert-manager Operator for Red Hat OpenShift API에서 Pod 예약을 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.15.0 이상을 설치했습니다.

프로세스

다음 명령을 실행하여 `certmanager.operator` 사용자 정의 리소스를 업데이트하여 원하는 구성 요소에 대한 Pod 예약 덮어쓰기를 구성합니다. `controllerConfig`, `webhookConfig` 또는 `cainjectorConfig` 섹션 아래의 `overrideScheduling` 필드를 사용하여 `nodeSelector` 및 `허용 오차` 설정을 정의합니다.

```shell-session
$ oc patch certmanager.operator cluster --type=merge -p="
spec:
  controllerConfig:
    overrideScheduling:
      nodeSelector:
        node-role.kubernetes.io/control-plane: ''
      tolerations:
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
  webhookConfig:
    overrideScheduling:
      nodeSelector:
        node-role.kubernetes.io/control-plane: ''
      tolerations:
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
  cainjectorConfig:
    overrideScheduling:
      nodeSelector:
        node-role.kubernetes.io/control-plane: ''
      tolerations:
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule"
"
```

1. 덮어쓸 수 있는 스케줄링 매개변수에 대한 자세한 내용은 CertManager 사용자 정의 리소스의 "CertManager 사용자 정의 리소스의 필드 설명"에서 "인증 관리자 구성 요소에 대한 일반 예약 매개변수"를 참조하십시오.

검증

`cert-manager` Pod의 Pod 예약 설정을 확인합니다.

다음 명령을 실행하여 `cert-manager` 네임스페이스의 배포를 확인하여 올바른 `nodeSelector` 및 `허용 오차` 가 있는지 확인합니다.

```shell-session
$ oc get pods -n cert-manager -o wide
```

```shell-session
NAME                                       READY   STATUS    RESTARTS   AGE   IP            NODE                         NOMINATED NODE   READINESS GATES
cert-manager-58d9c69db4-78mzp              1/1     Running   0          10m   10.129.0.36   ip-10-0-1-106.ec2.internal   <none>           <none>
cert-manager-cainjector-85b6987c66-rhzf7   1/1     Running   0          11m   10.128.0.39   ip-10-0-1-136.ec2.internal   <none>           <none>
cert-manager-webhook-7f54b4b858-29bsp      1/1     Running   0          11m   10.129.0.35   ip-10-0-1-106.ec2.internal   <none>           <none>
```

다음 명령을 실행하여 배포에 적용되는 `nodeSelector` 및 `허용 오차` 설정을 확인합니다.

```shell-session
$ oc get deployments -n cert-manager -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{.spec.template.spec.nodeSelector}{"\n"}{.spec.template.spec.tolerations}{"\n\n"}{end}'
```

```shell-session
cert-manager
{"kubernetes.io/os":"linux","node-role.kubernetes.io/control-plane":""}
[{"effect":"NoSchedule","key":"node-role.kubernetes.io/master","operator":"Exists"}]

cert-manager-cainjector
{"kubernetes.io/os":"linux","node-role.kubernetes.io/control-plane":""}
[{"effect":"NoSchedule","key":"node-role.kubernetes.io/master","operator":"Exists"}]

cert-manager-webhook
{"kubernetes.io/os":"linux","node-role.kubernetes.io/control-plane":""}
[{"effect":"NoSchedule","key":"node-role.kubernetes.io/master","operator":"Exists"}]
```

다음 명령을 실행하여 `cert-manager` 네임스페이스에서 Pod 예약 이벤트를 확인합니다.

```shell-session
$ oc get events -n cert-manager --field-selector reason=Scheduled
```

추가 리소스

CertManager 사용자 정의 리소스의 필드에 대한 설명

### 9.6. cert-manager Operator for Red Hat OpenShift 인증

클라우드 인증 정보를 구성하여 클러스터에서 cert-manager Operator for Red Hat OpenShift를 인증할 수 있습니다.

#### 9.6.1. AWS에서 인증

사전 요구 사항

Red Hat OpenShift용 cert-manager Operator 버전 1.11.1 이상이 설치되어 있어야 합니다.

mint 또는 passthrough 모드에서 작동하도록 Cloud Credential Operator를 구성했습니다.

프로세스

다음과 같이 `CredentialsRequest` 리소스 YAML 파일을 생성합니다(예: `sample-credential-request.yaml`).

```yaml
apiVersion: cloudcredential.openshift.io/v1
kind: CredentialsRequest
metadata:
  name: cert-manager
  namespace: openshift-cloud-credential-operator
spec:
  providerSpec:
    apiVersion: cloudcredential.openshift.io/v1
    kind: AWSProviderSpec
    statementEntries:
    - action:
      - "route53:GetChange"
      effect: Allow
      resource: "arn:aws:route53:::change/*"
    - action:
      - "route53:ChangeResourceRecordSets"
      - "route53:ListResourceRecordSets"
      effect: Allow
      resource: "arn:aws:route53:::hostedzone/*"
    - action:
      - "route53:ListHostedZonesByName"
      effect: Allow
      resource: "*"
  secretRef:
    name: aws-creds
    namespace: cert-manager
  serviceAccountNames:
  - cert-manager
```

다음 명령을 실행하여 `CredentialsRequest` 리소스를 생성합니다.

```shell-session
$ oc create -f sample-credential-request.yaml
```

다음 명령을 실행하여 cert-manager Operator for Red Hat OpenShift의 서브스크립션 오브젝트를 업데이트합니다.

```shell-session
$ oc -n cert-manager-operator patch subscription openshift-cert-manager-operator --type=merge -p '{"spec":{"config":{"env":[{"name":"CLOUD_CREDENTIALS_SECRET_NAME","value":"aws-creds"}]}}}'
```

검증

다음 명령을 실행하여 재배포된 cert-manager 컨트롤러 Pod의 이름을 가져옵니다.

```shell-session
$ oc get pods -l app.kubernetes.io/name=cert-manager -n cert-manager
```

```shell-session
NAME                          READY   STATUS    RESTARTS   AGE
cert-manager-bd7fbb9fc-wvbbt  1/1     Running   0          15m39s
```

다음 명령을 실행하여 cert-manager 컨트롤러 Pod가 `mountPath` 에 지정된 경로에 마운트된 AWS 인증 정보 볼륨으로 업데이트되었는지 확인합니다.

```shell-session
$ oc get -n cert-manager pod/<cert-manager_controller_pod_name> -o yaml
```

```shell-session
...
spec:
  containers:
  - args:
    ...
    - mountPath: /.aws
      name: cloud-credentials
  ...
  volumes:
  ...
  - name: cloud-credentials
    secret:
      ...
      secretName: aws-creds
```

#### 9.6.2. AWS 보안 토큰 서비스로 인증

사전 요구 사항

`ccoctl` 바이너리를 추출하여 준비했습니다.

수동 모드에서 Cloud Credential Operator를 사용하여 AWS STS를 사용하여 OpenShift Container Platform 클러스터를 구성했습니다.

프로세스

다음 명령을 실행하여 `CredentialsRequest` 리소스 YAML 파일을 저장할 디렉터리를 생성합니다.

```shell-session
$ mkdir credentials-request
```

다음 yaml을 적용하여 `credentials-request` 디렉터리(예: `sample-credential-request.yaml`)에 `CredentialsRequest` 리소스 YAML 파일을 생성합니다.

```yaml
apiVersion: cloudcredential.openshift.io/v1
kind: CredentialsRequest
metadata:
  name: cert-manager
  namespace: openshift-cloud-credential-operator
spec:
  providerSpec:
    apiVersion: cloudcredential.openshift.io/v1
    kind: AWSProviderSpec
    statementEntries:
    - action:
      - "route53:GetChange"
      effect: Allow
      resource: "arn:aws:route53:::change/*"
    - action:
      - "route53:ChangeResourceRecordSets"
      - "route53:ListResourceRecordSets"
      effect: Allow
      resource: "arn:aws:route53:::hostedzone/*"
    - action:
      - "route53:ListHostedZonesByName"
      effect: Allow
      resource: "*"
  secretRef:
    name: aws-creds
    namespace: cert-manager
  serviceAccountNames:
  - cert-manager
```

`ccoctl` 툴을 사용하여 다음 명령을 실행하여 `CredentialsRequest` 오브젝트를 처리합니다.

```shell-session
$ ccoctl aws create-iam-roles \
    --name <user_defined_name> --region=<aws_region> \
    --credentials-requests-dir=<path_to_credrequests_dir> \
    --identity-provider-arn <oidc_provider_arn> --output-dir=<path_to_output_dir>
```

```shell-session
2023/05/15 18:10:34 Role arn:aws:iam::XXXXXXXXXXXX:role/<user_defined_name>-cert-manager-aws-creds created
2023/05/15 18:10:34 Saved credentials configuration to: <path_to_output_dir>/manifests/cert-manager-aws-creds-credentials.yaml
2023/05/15 18:10:35 Updated Role policy for Role <user_defined_name>-cert-manager-aws-creds
```

다음 단계에서 사용할 출력에서 < `aws_role_arn` >을 복사합니다. For example, `"arn:aws:iam::XXXXXXXXXXXX:role/<user_defined_name>-cert-manager-aws-creds"`

다음 명령을 실행하여 `eks.amazonaws.com/role-arn="<aws_role_arn>"` 주석을 서비스 계정에 추가합니다.

```shell-session
$ oc -n cert-manager annotate serviceaccount cert-manager eks.amazonaws.com/role-arn="<aws_role_arn>"
```

새 Pod를 생성하려면 다음 명령을 실행하여 기존 cert-manager 컨트롤러 Pod를 삭제합니다.

```shell-session
$ oc delete pods -l app.kubernetes.io/name=cert-manager -n cert-manager
```

AWS 인증 정보는 1분 이내에 새 cert-manager 컨트롤러 Pod에 적용됩니다.

검증

다음 명령을 실행하여 업데이트된 cert-manager 컨트롤러 Pod의 이름을 가져옵니다.

```shell-session
$ oc get pods -l app.kubernetes.io/name=cert-manager -n cert-manager
```

```shell-session
NAME                          READY   STATUS    RESTARTS   AGE
cert-manager-bd7fbb9fc-wvbbt  1/1     Running   0          39s
```

다음 명령을 실행하여 AWS 인증 정보가 업데이트되었는지 확인합니다.

```shell-session
$ oc set env -n cert-manager po/<cert_manager_controller_pod_name> --list
```

```shell-session
# pods/cert-manager-57f9555c54-vbcpg, container cert-manager-controller
# POD_NAMESPACE from field path metadata.namespace
AWS_ROLE_ARN=XXXXXXXXXXXX
AWS_WEB_IDENTITY_TOKEN_FILE=/var/run/secrets/eks.amazonaws.com/serviceaccount/token
```

추가 리소스

Cloud Credential Operator 유틸리티 구성

#### 9.6.3. Google Cloud에서 인증

사전 요구 사항

Red Hat OpenShift용 cert-manager Operator 버전 1.11.1 이상이 설치되어 있어야 합니다.

mint 또는 passthrough 모드에서 작동하도록 Cloud Credential Operator를 구성했습니다.

프로세스

다음 yaml을 적용하여 `sample-credential-request.yaml` 과 같은 `CredentialsRequest` 리소스 YAML 파일을 생성합니다.

```yaml
apiVersion: cloudcredential.openshift.io/v1
kind: CredentialsRequest
metadata:
  name: cert-manager
  namespace: openshift-cloud-credential-operator
spec:
  providerSpec:
    apiVersion: cloudcredential.openshift.io/v1
    kind: GCPProviderSpec
    predefinedRoles:
    - roles/dns.admin
  secretRef:
    name: gcp-credentials
    namespace: cert-manager
  serviceAccountNames:
  - cert-manager
```

참고

`dns.admin` 역할은 Google Cloud DNS 리소스를 관리하기 위해 서비스 계정에 대한 관리자 권한을 제공합니다. cert-manager가 최소 권한이 있는 서비스 계정으로 실행되도록 다음 권한을 사용하여 사용자 지정 역할을 생성할 수 있습니다.

`dns.resourceRecordSets.*`

`dns.changes.*`

`dns.managedZones.list`

다음 명령을 실행하여 `CredentialsRequest` 리소스를 생성합니다.

```shell-session
$ oc create -f sample-credential-request.yaml
```

다음 명령을 실행하여 cert-manager Operator for Red Hat OpenShift의 서브스크립션 오브젝트를 업데이트합니다.

```shell-session
$ oc -n cert-manager-operator patch subscription openshift-cert-manager-operator --type=merge -p '{"spec":{"config":{"env":[{"name":"CLOUD_CREDENTIALS_SECRET_NAME","value":"gcp-credentials"}]}}}'
```

검증

다음 명령을 실행하여 재배포된 cert-manager 컨트롤러 Pod의 이름을 가져옵니다.

```shell-session
$ oc get pods -l app.kubernetes.io/name=cert-manager -n cert-manager
```

```shell-session
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-bd7fbb9fc-wvbbt               1/1     Running   0          15m39s
```

다음 명령을 실행하여 cert-manager 컨트롤러 Pod가 `mountPath` 에 지정된 경로에 마운트된 Google Cloud 인증 정보 볼륨으로 업데이트되었는지 확인합니다.

```shell-session
$ oc get -n cert-manager pod/<cert-manager_controller_pod_name> -o yaml
```

```shell-session
spec:
  containers:
  - args:
    ...
    volumeMounts:
    ...
    - mountPath: /.config/gcloud
      name: cloud-credentials
    ....
  volumes:
  ...
  - name: cloud-credentials
    secret:
      ...
      items:
      - key: service_account.json
        path: application_default_credentials.json
      secretName: gcp-credentials
```

#### 9.6.4. Google Cloud Workload Identity로 인증

사전 요구 사항

`ccoctl` 바이너리를 추출하여 준비합니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.11.1 이상이 설치되어 있어야 합니다.

수동 모드에서 Cloud Credential Operator를 사용하여 Google Cloud Workload Identity로 OpenShift Container Platform 클러스터를 구성했습니다.

프로세스

다음 명령을 실행하여 `CredentialsRequest` 리소스 YAML 파일을 저장할 디렉터리를 생성합니다.

```shell-session
$ mkdir credentials-request
```

`credentials-request` 디렉터리에서 다음 `CredentialsRequest` 매니페스트가 포함된 YAML 파일을 생성합니다.

```yaml
apiVersion: cloudcredential.openshift.io/v1
kind: CredentialsRequest
metadata:
  name: cert-manager
  namespace: openshift-cloud-credential-operator
spec:
  providerSpec:
    apiVersion: cloudcredential.openshift.io/v1
    kind: GCPProviderSpec
    predefinedRoles:
    - roles/dns.admin
  secretRef:
    name: gcp-credentials
    namespace: cert-manager
  serviceAccountNames:
  - cert-manager
```

참고

`dns.admin` 역할은 Google Cloud DNS 리소스를 관리하기 위해 서비스 계정에 대한 관리자 권한을 제공합니다. cert-manager가 최소 권한이 있는 서비스 계정으로 실행되도록 다음 권한을 사용하여 사용자 지정 역할을 생성할 수 있습니다.

`dns.resourceRecordSets.*`

`dns.changes.*`

`dns.managedZones.list`

`ccoctl` 툴을 사용하여 다음 명령을 실행하여 `CredentialsRequest` 오브젝트를 처리합니다.

```shell-session
$ ccoctl gcp create-service-accounts \
    --name <user_defined_name> --output-dir=<path_to_output_dir> \
    --credentials-requests-dir=<path_to_credrequests_dir> \
    --workload-identity-pool <workload_identity_pool> \
    --workload-identity-provider <workload_identity_provider> \
    --project <gcp_project_id>
```

```shell-session
$ ccoctl gcp create-service-accounts \
    --name abcde-20230525-4bac2781 --output-dir=/home/outputdir \
    --credentials-requests-dir=/home/credentials-requests \
    --workload-identity-pool abcde-20230525-4bac2781 \
    --workload-identity-provider abcde-20230525-4bac2781 \
    --project openshift-gcp-devel
```

다음 명령을 실행하여 클러스터의 매니페스트 디렉터리에 생성된 보안을 적용합니다.

```shell-session
$ ls <path_to_output_dir>/manifests/*-credentials.yaml | xargs -I{} oc apply -f {}
```

다음 명령을 실행하여 cert-manager Operator for Red Hat OpenShift의 서브스크립션 오브젝트를 업데이트합니다.

```shell-session
$ oc -n cert-manager-operator patch subscription openshift-cert-manager-operator --type=merge -p '{"spec":{"config":{"env":[{"name":"CLOUD_CREDENTIALS_SECRET_NAME","value":"gcp-credentials"}]}}}'
```

검증

다음 명령을 실행하여 재배포된 cert-manager 컨트롤러 Pod의 이름을 가져옵니다.

```shell-session
$ oc get pods -l app.kubernetes.io/name=cert-manager -n cert-manager
```

```shell-session
NAME                          READY   STATUS    RESTARTS   AGE
cert-manager-bd7fbb9fc-wvbbt  1/1     Running   0          15m39s
```

다음 명령을 실행하여 cert-manager 컨트롤러 Pod가 `mountPath` 에 지정된 경로에 마운트된 Google Cloud 워크로드 ID 인증 정보 볼륨을 사용하여 업데이트되었는지 확인합니다.

```shell-session
$ oc get -n cert-manager pod/<cert-manager_controller_pod_name> -o yaml
```

```shell-session
spec:
  containers:
  - args:
    ...
    volumeMounts:
    - mountPath: /var/run/secrets/openshift/serviceaccount
      name: bound-sa-token
      ...
    - mountPath: /.config/gcloud
      name: cloud-credentials
  ...
  volumes:
  - name: bound-sa-token
    projected:
      ...
      sources:
      - serviceAccountToken:
          audience: openshift
          ...
          path: token
  - name: cloud-credentials
    secret:
      ...
      items:
      - key: service_account.json
        path: application_default_credentials.json
      secretName: gcp-credentials
```

추가 리소스

Cloud Credential Operator 유틸리티 구성

구성 요소에 대한 단기 인증 정보가 있는 수동 모드

Cloud Credential Operator의 기본 동작

### 9.7. ACME 발행자 구성

cert-manager Operator for Red Hat OpenShift는 Let's Encrypt 와 같은 ACME(Automated Certificate Management Environment) CA 서버 사용을 지원하여 인증서를 발행합니다. `발행자` API 오브젝트에 시크릿 세부 정보를 지정하여 명시적 인증 정보를 구성합니다. 앰비언트 자격 증명은 `Issuer` API 개체에서 명시적으로 구성되지 않은 환경, 메타데이터 서비스 또는 로컬 파일에서 추출됩니다.

참고

`Issuer` 오브젝트는 namespace 범위입니다. 동일한 네임스페이스에서만 인증서를 발행할 수 있습니다. `ClusterIssuer` 오브젝트를 사용하여 클러스터의 모든 네임스페이스에서 인증서를 발행할 수도 있습니다.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: acme-cluster-issuer
spec:
  acme:
    ...
```

참고

기본적으로 앰비언트 자격 증명과 함께 `ClusterIssuer` 개체를 사용할 수 있습니다. 앰비언트 자격 증명과 함께 `Issuer` 오브젝트를 사용하려면 cert-manager 컨트롤러에 대해 `--issuer-ambient-credentials` 설정을 활성화해야 합니다.

#### 9.7.1. ACME 발행자 정보

cert-manager Operator for Red Hat OpenShift의 ACME 발행자 유형은 ACME(Automated Certificate Management Environment) 인증 기관(CA) 서버를 나타냅니다. ACME CA 서버는 클라이언트가 인증서가 요청되는 도메인 이름을 소유하고 있는지 확인하는 챌린지에 의존합니다. 문제가 발생하면 cert-manager Operator for Red Hat OpenShift에서 인증서를 발행할 수 있습니다. 챌린지가 실패하면 cert-manager Operator for Red Hat OpenShift에서 인증서를 발행하지 않습니다.

참고

Let's Encrypt 및 Internet ACME 서버에서는 프라이빗 DNS 영역이 지원되지 않습니다.

#### 9.7.1.1. 지원되는 ACME 챌린지 유형

cert-manager Operator for Red Hat OpenShift는 ACME 발행자를 위해 다음과 같은 챌린지 유형을 지원합니다.

HTTP-01

HTTP-01 챌린지 유형을 사용하면 도메인의 HTTP URL 끝점에 계산된 키를 제공합니다. ACME CA 서버가 URL에서 키를 가져올 수 있는 경우 도메인 소유자로 유효성을 검사할 수 있습니다.

자세한 내용은 업스트림 cert-manager 설명서의 HTTP01 을 참조하십시오.

참고

HTTP-01을 사용하려면 Let's Encrypt 서버가 클러스터 경로에 액세스할 수 있어야 합니다. 내부 또는 프라이빗 클러스터가 프록시 뒤에 있는 경우 인증서 발행을 위한 HTTP-01 검증에 실패합니다.

HTTP-01 챌린지는 포트 80으로 제한됩니다. 자세한 내용은 HTTP-01 챌린지 (Let's Encrypt)를 참조하십시오.

DNS-01

DNS-01 챌린지 유형을 사용하면 DNS TXT 레코드에서 계산된 키를 제공합니다. ACME CA 서버가 DNS 조회로 키를 가져올 수 있는 경우 도메인 소유자로 유효성을 검사할 수 있습니다.

자세한 내용은 업스트림 cert-manager 문서의 DNS01 을 참조하십시오.

#### 9.7.1.2. 지원되는 DNS-01 공급자

cert-manager Operator for Red Hat OpenShift는 ACME 발행자를 위한 다음 DNS-01 공급자를 지원합니다.

Amazon Route 53

Azure DNS

참고

cert-manager Operator for Red Hat OpenShift는 Microsoft Entra ID Pod ID를 사용하여 pod에 관리 ID를 할당하도록 지원하지 않습니다.

Google Cloud DNS

Webhook

Red Hat은 OpenShift Container Platform에서 cert-manager가 있는 외부 Webhook를 사용하여 DNS 공급자를 테스트하고 지원합니다. 다음 DNS 공급자는 OpenShift Container Platform에서 테스트 및 지원됩니다.

cert-manager-webhook-ibmcis

참고

나열되지 않은 DNS 공급자를 사용하면 OpenShift Container Platform에서 작동할 수 있지만 Red Hat에서 이 공급자를 테스트하지 않았기 때문에 Red Hat에서 지원하지 않습니다.

#### 9.7.2. HTTP-01 문제를 해결하기 위해 ACME 발행자 구성

cert-manager Operator for Red Hat OpenShift를 사용하여 ACME 발행자를 설정하여 HTTP-01 문제를 해결할 수 있습니다. 이 절차에서는 Let's Encrypt 를 ACME CA 서버로 사용합니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

노출하려는 서비스가 있습니다. 이 절차에서 서비스의 이름은 `sample-workload` 입니다.

프로세스

ACME 클러스터 발행자를 생성합니다.

`ClusterIssuer` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    preferredChain: ""
    privateKeySecretRef:
      name: <secret_for_private_key>
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    solvers:
    - http01:
        ingress:
          ingressClassName: openshift-default
```

1. 클러스터 발행자의 이름을 제공합니다.

2. & `lt;secret_private_key` >를 ACME 계정 개인 키를 저장할 시크릿 이름으로 바꿉니다.

3. ACME 서버의 `디렉터리` 끝점에 액세스할 URL을 지정합니다. 이 예에서는 Let's Encrypt 스테이징 환경을 사용합니다.

4. Ingress 클래스를 지정합니다.

선택 사항: `ingressClassName` 을 지정하지 않고 오브젝트를 생성하는 경우 다음 명령을 사용하여 기존 수신을 패치합니다.

```shell-session
$ oc patch ingress/<ingress-name> --type=merge --patch '{"spec":{"ingressClassName":"openshift-default"}}' -n <namespace>
```

다음 명령을 실행하여 `ClusterIssuer` 오브젝트를 생성합니다.

```shell-session
$ oc create -f acme-cluster-issuer.yaml
```

Ingress를 생성하여 사용자 워크로드의 서비스를 노출합니다.

`Namespace` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-ingress-namespace
```

1. Ingress의 네임스페이스를 지정합니다.

다음 명령을 실행하여 `Namespace` 오브젝트를 생성합니다.

```shell-session
$ oc create -f namespace.yaml
```

`Ingress` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sample-ingress
  namespace: my-ingress-namespace
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
spec:
  ingressClassName: openshift-default
  tls:
  - hosts:
    - <hostname>
    secretName: sample-tls
  rules:
  - host: <hostname>
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sample-workload
            port:
              number: 80
```

1. Ingress의 이름을 지정합니다.

2. Ingress에 대해 생성한 네임스페이스를 지정합니다.

3. 생성한 클러스터 발행자를 지정합니다.

4. Ingress 클래스를 지정합니다.

5. & `lt;hostname` >을 인증서와 연결할 주체 대체 이름(SAN)으로 바꿉니다. 이 이름은 인증서에 DNS 이름을 추가하는 데 사용됩니다.

6. 인증서를 저장하는 보안을 지정합니다.

7. &lt `;hostname&gt`;을 호스트 이름으로 바꿉니다. < `host_name>.<cluster_ingress_domain` > 구문을 사용하여 `*.<cluster_ingress_domain` > 와일드카드 DNS 레코드 및 클러스터의 인증서를 제공할 수 있습니다. 예를 들어. 그렇지 않으면 선택한 호스트 이름에 대한 DNS 레코드가 있는지 확인해야 합니다.

```shell
apps.<cluster_base_domain>을 사용할 수 있습니다
```

8. 노출할 서비스 이름을 지정합니다. 이 예에서는 `sample-workload` 라는 서비스를 사용합니다.

다음 명령을 실행하여 `Ingress` 오브젝트를 생성합니다.

```shell-session
$ oc create -f ingress.yaml
```

#### 9.7.3. AWS Route53에 대한 명시적 인증 정보를 사용하여 ACME 발행자 구성

cert-manager Operator for Red Hat OpenShift를 사용하여 AWS에서 명시적 인증 정보를 사용하여 ACME(Automated Certificate Management Environment) 발행자를 설정하여 DNS-01 문제를 해결할 수 있습니다. 이 절차에서는 Let's Encrypt 를 ACME 인증 기관(CA) 서버로 사용하고 Amazon Route 53을 사용하여 DNS-01 문제를 해결하는 방법을 보여줍니다.

사전 요구 사항

명시적 `accessKeyID` 및 `secretAccessKey` 인증 정보를 제공해야 합니다. 자세한 내용은 업스트림 cert-manager 문서의 Route53 을 참조하십시오.

참고

AWS에서 실행되지 않는 OpenShift Container Platform 클러스터의 명시적 인증 정보와 함께 Amazon Route 53을 사용할 수 있습니다.

프로세스

선택 사항: DNS-01 자체 검사의 네임서버 설정을 재정의합니다.

이 단계는 대상 퍼블릭 호스팅 영역이 클러스터의 기본 개인 호스팅 영역과 겹치는 경우에만 필요합니다.

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
  ...
spec:
  ...
  controllerConfig:
    overrideArgs:
      - '--dns01-recursive-nameservers-only'
      - '--dns01-recursive-nameservers=1.1.1.1:53'
```

1. `spec.controllerConfig` 섹션을 추가합니다.

2. 해당 도메인과 연결된 권한 있는 이름 서버를 확인하는 대신 재귀 이름 서버만 사용하도록 지정합니다.

3. DNS-01 자체 검사를 쿼리하려면 쉼표로 구분된 < `host>:<port` > 네임서버 목록을 제공합니다. 공개 영역과 프라이빗 영역이 겹치지 않도록 `1.1.1.1:53` 값을 사용해야 합니다.

파일을 저장하여 변경 사항을 적용합니다.

선택 사항: 발행자의 네임스페이스를 생성합니다.

```shell-session
$ oc new-project <issuer_namespace>
```

다음 명령을 실행하여 AWS 인증 정보를 저장할 시크릿을 생성합니다.

```shell-session
$ oc create secret generic aws-secret --from-literal=awsSecretAccessKey=<aws_secret_access_key> \
    -n my-issuer-namespace
```

1. & `lt;aws_secret_access_key&gt`;를 AWS 시크릿 액세스 키로 바꿉니다.

발행자를 생성합니다.

`Issuer` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: <letsencrypt_staging>
  namespace: <issuer_namespace>
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: "<email_address>"
    privateKeySecretRef:
      name: <secret_private_key>
    solvers:
    - dns01:
        route53:
          accessKeyID: <aws_key_id>
          hostedZoneID: <hosted_zone_id>
          region: <region_name>
          secretAccessKeySecretRef:
            name: "aws-secret"
            key: "awsSecretAccessKey"
```

1. 발행자의 이름을 입력합니다.

2. 발행자에 대해 생성한 네임스페이스를 지정합니다.

3. ACME 서버의 `디렉터리` 끝점에 액세스할 URL을 지정합니다. 이 예에서는 Let's Encrypt 스테이징 환경을 사용합니다.

4. &lt `;email_address&gt`;를 이메일 주소로 바꿉니다.

5. & `lt;secret_private_key` >를 ACME 계정 개인 키를 저장할 시크릿 이름으로 바꿉니다.

6. &lt `;aws_key_id&gt`;를 AWS 키 ID로 바꿉니다.

7. &lt `;hosted_zone_id&gt`;를 호스팅 영역 ID로 바꿉니다.

8. & `lt;region_name&` gt;을 AWS 리전 이름으로 바꿉니다. 예를 들면 `us-east-1` 입니다.

9. 생성한 시크릿의 이름을 지정합니다.

10. AWS 시크릿 액세스 키를 저장하는 생성한 시크릿에 키를 지정합니다.

다음 명령을 실행하여 `Issuer` 오브젝트를 생성합니다.

```shell-session
$ oc create -f issuer.yaml
```

#### 9.7.4. AWS에서 앰비언트 인증 정보를 사용하여 ACME 발행자 구성

cert-manager Operator for Red Hat OpenShift를 사용하여 AWS에서 앰비언트 인증 정보를 사용하여 ACME 발행자를 설정하여 DNS-01 문제를 해결할 수 있습니다. 이 절차에서는 Let's Encrypt 를 ACME CA 서버로 사용하고 Amazon Route 53을 사용하여 DNS-01 문제를 해결하는 방법을 보여줍니다.

사전 요구 사항

클러스터가 AWS STS(보안 토큰 서비스)를 사용하도록 구성된 경우 AWS Security Token Service 클러스터용 cert-manager Operator에 대한 클라우드 인증 정보 구성 섹션의 지침을 따르십시오.

클러스터가 AWS STS를 사용하지 않는 경우, AWS의 cert-manager Operator for Red Hat OpenShift에 대한 클라우드 인증 정보 구성 섹션의 지침을 따르십시오.

프로세스

선택 사항: DNS-01 자체 검사의 네임서버 설정을 재정의합니다.

이 단계는 대상 퍼블릭 호스팅 영역이 클러스터의 기본 개인 호스팅 영역과 겹치는 경우에만 필요합니다.

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
  ...
spec:
  ...
  controllerConfig:
    overrideArgs:
      - '--dns01-recursive-nameservers-only'
      - '--dns01-recursive-nameservers=1.1.1.1:53'
```

1. `spec.controllerConfig` 섹션을 추가합니다.

2. 해당 도메인과 연결된 권한 있는 이름 서버를 확인하는 대신 재귀 이름 서버만 사용하도록 지정합니다.

3. DNS-01 자체 검사를 쿼리하려면 쉼표로 구분된 < `host>:<port` > 네임서버 목록을 제공합니다. 공개 영역과 프라이빗 영역이 겹치지 않도록 `1.1.1.1:53` 값을 사용해야 합니다.

파일을 저장하여 변경 사항을 적용합니다.

선택 사항: 발행자의 네임스페이스를 생성합니다.

```shell-session
$ oc new-project <issuer_namespace>
```

`CertManager` 리소스를 수정하여 `--issuer-ambient-credentials` 인수를 추가합니다.

```shell-session
$ oc patch certmanager/cluster \
  --type=merge \
  -p='{"spec":{"controllerConfig":{"overrideArgs":["--issuer-ambient-credentials"]}}}'
```

발행자를 생성합니다.

`Issuer` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: <letsencrypt_staging>
  namespace: <issuer_namespace>
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: "<email_address>"
    privateKeySecretRef:
      name: <secret_private_key>
    solvers:
    - dns01:
        route53:
          hostedZoneID: <hosted_zone_id>
          region: us-east-1
```

1. 발행자의 이름을 입력합니다.

2. 발행자에 대해 생성한 네임스페이스를 지정합니다.

3. ACME 서버의 `디렉터리` 끝점에 액세스할 URL을 지정합니다. 이 예에서는 Let's Encrypt 스테이징 환경을 사용합니다.

4. &lt `;email_address&gt`;를 이메일 주소로 바꿉니다.

5. & `lt;secret_private_key` >를 ACME 계정 개인 키를 저장할 시크릿 이름으로 바꿉니다.

6. &lt `;hosted_zone_id&gt`;를 호스팅 영역 ID로 바꿉니다.

다음 명령을 실행하여 `Issuer` 오브젝트를 생성합니다.

```shell-session
$ oc create -f issuer.yaml
```

#### 9.7.5. Google Cloud DNS에 대한 명시적 인증 정보를 사용하여 ACME 발행자 구성

cert-manager Operator for Red Hat OpenShift를 사용하여 Google Cloud에서 명시적 인증 정보를 사용하여 DNS-01 문제를 해결하기 위해 ACME 발행자를 설정할 수 있습니다. 이 절차에서는 Let's Encrypt 를 ACME CA 서버로 사용하고 Google Cloud DNS를 사용하여 DNS-01 문제를 해결하는 방법을 보여줍니다.

사전 요구 사항

Google Cloud DNS에 대해 원하는 역할을 가진 Google Cloud 서비스 계정을 설정했습니다. 자세한 내용은 업스트림 cert-manager 설명서의 Google Cloud DNS 를 참조하십시오.

참고

Google Cloud DNS는 Google Cloud에서 실행되지 않는 OpenShift Container Platform 클러스터에서 명시적 인증 정보와 함께 사용할 수 있습니다.

프로세스

선택 사항: DNS-01 자체 검사의 네임서버 설정을 재정의합니다.

이 단계는 대상 퍼블릭 호스팅 영역이 클러스터의 기본 개인 호스팅 영역과 겹치는 경우에만 필요합니다.

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
  ...
spec:
  ...
  controllerConfig:
    overrideArgs:
      - '--dns01-recursive-nameservers-only'
      - '--dns01-recursive-nameservers=1.1.1.1:53'
```

1. `spec.controllerConfig` 섹션을 추가합니다.

2. 해당 도메인과 연결된 권한 있는 이름 서버를 확인하는 대신 재귀 이름 서버만 사용하도록 지정합니다.

3. DNS-01 자체 검사를 쿼리하려면 쉼표로 구분된 < `host>:<port` > 네임서버 목록을 제공합니다. 공개 영역과 프라이빗 영역이 겹치지 않도록 `1.1.1.1:53` 값을 사용해야 합니다.

파일을 저장하여 변경 사항을 적용합니다.

선택 사항: 발행자의 네임스페이스를 생성합니다.

```shell-session
$ oc new-project my-issuer-namespace
```

다음 명령을 실행하여 Google Cloud 인증 정보를 저장할 시크릿을 생성합니다.

```shell-session
$ oc create secret generic clouddns-dns01-solver-svc-acct --from-file=service_account.json=<path/to/gcp_service_account.json> -n my-issuer-namespace
```

발행자를 생성합니다.

`Issuer` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: <acme_dns01_clouddns_issuer>
  namespace: <issuer_namespace>
spec:
  acme:
    preferredChain: ""
    privateKeySecretRef:
      name: <secret_private_key>
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    solvers:
    - dns01:
        cloudDNS:
          project: <project_id>
          serviceAccountSecretRef:
            name: clouddns-dns01-solver-svc-acct
            key: service_account.json
```

1. 발행자의 이름을 입력합니다.

2. &lt `;issuer_namespace&gt`;를 issuer 네임스페이스로 바꿉니다.

3. & `lt;secret_private_key` >를 ACME 계정 개인 키를 저장할 시크릿 이름으로 바꿉니다.

4. ACME 서버의 `디렉터리` 끝점에 액세스할 URL을 지정합니다. 이 예에서는 Let's Encrypt 스테이징 환경을 사용합니다.

5. & `lt;project_id` >를 Cloud DNS 영역이 포함된 Google Cloud 프로젝트의 이름으로 바꿉니다.

6. 생성한 시크릿의 이름을 지정합니다.

7. Google Cloud 시크릿 액세스 키를 저장하는 생성한 시크릿에 키를 지정합니다.

다음 명령을 실행하여 `Issuer` 오브젝트를 생성합니다.

```shell-session
$ oc create -f issuer.yaml
```

#### 9.7.6. Google Cloud에서 앰비언트 인증 정보를 사용하여 ACME 발행자 구성

cert-manager Operator for Red Hat OpenShift를 사용하여 Google Cloud에서 앰비언트 인증 정보를 사용하여 DNS-01 문제를 해결하기 위해 ACME 발행자를 설정할 수 있습니다. 이 절차에서는 Let's Encrypt 를 ACME CA 서버로 사용하고 Google Cloud DNS를 사용하여 DNS-01 문제를 해결하는 방법을 보여줍니다.

사전 요구 사항

클러스터가 Google Cloud Workload Identity를 사용하도록 구성된 경우 Google Cloud Workload Identity 섹션을 사용하여 cert-manager Operator for Red Hat OpenShift에 대한 클라우드 인증 정보 구성 의 지침을 따르십시오.

클러스터에서 Google Cloud Workload Identity를 사용하지 않는 경우 Google Cloud의 cert-manager Operator for Red Hat OpenShift에 대한 클라우드 인증 정보 구성 섹션의 지침을 따르십시오.

프로세스

선택 사항: DNS-01 자체 검사의 네임서버 설정을 재정의합니다.

이 단계는 대상 퍼블릭 호스팅 영역이 클러스터의 기본 개인 호스팅 영역과 겹치는 경우에만 필요합니다.

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
  ...
spec:
  ...
  controllerConfig:
    overrideArgs:
      - '--dns01-recursive-nameservers-only'
      - '--dns01-recursive-nameservers=1.1.1.1:53'
```

1. `spec.controllerConfig` 섹션을 추가합니다.

2. 해당 도메인과 연결된 권한 있는 이름 서버를 확인하는 대신 재귀 이름 서버만 사용하도록 지정합니다.

3. DNS-01 자체 검사를 쿼리하려면 쉼표로 구분된 < `host>:<port` > 네임서버 목록을 제공합니다. 공개 영역과 프라이빗 영역이 겹치지 않도록 `1.1.1.1:53` 값을 사용해야 합니다.

파일을 저장하여 변경 사항을 적용합니다.

선택 사항: 발행자의 네임스페이스를 생성합니다.

```shell-session
$ oc new-project <issuer_namespace>
```

`CertManager` 리소스를 수정하여 `--issuer-ambient-credentials` 인수를 추가합니다.

```shell-session
$ oc patch certmanager/cluster \
  --type=merge \
  -p='{"spec":{"controllerConfig":{"overrideArgs":["--issuer-ambient-credentials"]}}}'
```

발행자를 생성합니다.

`Issuer` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: <acme_dns01_clouddns_issuer>
  namespace: <issuer_namespace>
spec:
  acme:
    preferredChain: ""
    privateKeySecretRef:
      name: <secret_private_key>
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    solvers:
    - dns01:
        cloudDNS:
          project: <gcp_project_id>
```

1. 발행자의 이름을 입력합니다.

2. & `lt;secret_private_key` >를 ACME 계정 개인 키를 저장할 시크릿 이름으로 바꿉니다.

3. ACME 서버의 `디렉터리` 끝점에 액세스할 URL을 지정합니다. 이 예에서는 Let's Encrypt 스테이징 환경을 사용합니다.

4. Cloud DNS 영역이 포함된 Google Cloud 프로젝트의 이름으로 바꿉니다.

다음 명령을 실행하여 `Issuer` 오브젝트를 생성합니다.

```shell-session
$ oc create -f issuer.yaml
```

#### 9.7.7. Microsoft Azure DNS에 대한 명시적 인증 정보를 사용하여 ACME 발행자 구성

cert-manager Operator for Red Hat OpenShift를 사용하여 Microsoft Azure에서 명시적 인증 정보를 사용하여 ACME 발행자를 설정하여 DNS-01 문제를 해결할 수 있습니다. 이 절차에서는 Let's Encrypt 를 ACME CA 서버로 사용하고 Azure DNS를 사용하여 DNS-01 문제를 해결하는 방법을 보여줍니다.

사전 요구 사항

Azure DNS에 대해 원하는 역할을 가진 서비스 주체를 설정했습니다. 자세한 내용은 업스트림 cert-manager 설명서의 Azure DNS 를 참조하십시오.

참고

Microsoft Azure에서 실행되지 않는 OpenShift Container Platform 클러스터에 대해 다음 절차를 수행할 수 있습니다.

프로세스

선택 사항: DNS-01 자체 검사의 네임서버 설정을 재정의합니다.

이 단계는 대상 퍼블릭 호스팅 영역이 클러스터의 기본 개인 호스팅 영역과 겹치는 경우에만 필요합니다.

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager cluster
```

다음 덮어쓰기 인수가 포함된 `spec.controllerConfig` 섹션을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
  ...
spec:
  ...
  controllerConfig:
    overrideArgs:
      - '--dns01-recursive-nameservers-only'
      - '--dns01-recursive-nameservers=1.1.1.1:53'
```

1. `spec.controllerConfig` 섹션을 추가합니다.

2. 해당 도메인과 연결된 권한 있는 이름 서버를 확인하는 대신 재귀 이름 서버만 사용하도록 지정합니다.

3. DNS-01 자체 검사를 쿼리하려면 쉼표로 구분된 < `host>:<port` > 네임서버 목록을 제공합니다. 공개 영역과 프라이빗 영역이 겹치지 않도록 `1.1.1.1:53` 값을 사용해야 합니다.

파일을 저장하여 변경 사항을 적용합니다.

선택 사항: 발행자의 네임스페이스를 생성합니다.

```shell-session
$ oc new-project my-issuer-namespace
```

다음 명령을 실행하여 Azure 인증 정보를 저장할 시크릿을 생성합니다.

```shell-session
$ oc create secret generic <secret_name> --from-literal=<azure_secret_access_key_name>=<azure_secret_access_key_value> \
    -n my-issuer-namespace
```

1. &lt `;secret_name&gt`;을 시크릿 이름으로 바꿉니다.

2. & `lt;azure_secret_access_key_name` >을 Azure 시크릿 액세스 키 이름으로 바꿉니다.

3. & `lt;azure_secret_access_key_value&gt`;를 Azure 시크릿 키로 바꿉니다.

발행자를 생성합니다.

`Issuer` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: <acme-dns01-azuredns-issuer>
  namespace: <issuer_namespace>
spec:
  acme:
    preferredChain: ""
    privateKeySecretRef:
      name: <secret_private_key>
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    solvers:
    - dns01:
        azureDNS:
          clientID: <azure_client_id>
          clientSecretSecretRef:
            name: <secret_name>
            key: <azure_secret_access_key_name>
          subscriptionID: <azure_subscription_id>
          tenantID: <azure_tenant_id>
          resourceGroupName: <azure_dns_zone_resource_group>
          hostedZoneName: <azure_dns_zone>
          environment: AzurePublicCloud
```

1. 발행자의 이름을 입력합니다.

2. &lt `;issuer_namespace&gt`;를 issuer 네임스페이스로 바꿉니다.

3. & `lt;secret_private_key` >를 ACME 계정 개인 키를 저장할 시크릿 이름으로 바꿉니다.

4. ACME 서버의 `디렉터리` 끝점에 액세스할 URL을 지정합니다. 이 예에서는 Let's Encrypt 스테이징 환경을 사용합니다.

5. &lt `;azure_client_id&gt`;를 Azure 클라이언트 ID로 바꿉니다.

6. & `lt;secret_name` >을 클라이언트 시크릿 이름으로 바꿉니다.

7. & `lt;azure_secret_access_key_name&gt`;을 클라이언트 시크릿 키 이름으로 바꿉니다.

8. &lt `;azure_subscription_id&gt`;를 Azure 서브스크립션 ID로 바꿉니다.

9. &lt `;azure_tenant_id&gt`;를 Azure 테넌트 ID로 바꿉니다.

10. & `lt;azure_dns_zone_resource_group` >을 Azure DNS 영역 리소스 그룹의 이름으로 바꿉니다.

11. & `lt;azure_dns_zone&` gt;을 Azure DNS 영역 이름으로 바꿉니다.

다음 명령을 실행하여 `Issuer` 오브젝트를 생성합니다.

```shell-session
$ oc create -f issuer.yaml
```

#### 9.7.8. 추가 리소스

AWS 보안 토큰 서비스 클러스터용 Red Hat OpenShift용 cert-manager Operator에 대한 클라우드 인증 정보 구성

AWS에서 Red Hat OpenShift용 cert-manager Operator에 대한 클라우드 인증 정보 구성

Google Cloud Workload Identity를 사용하여 Red Hat OpenShift용 cert-manager Operator에 대한 클라우드 인증 정보 구성

Google Cloud에서 Red Hat OpenShift용 cert-manager Operator에 대한 클라우드 인증 정보 구성

### 9.8. 발급자를 사용하여 인증서 구성

cert-manager Operator for Red Hat OpenShift를 사용하면 인증서와 인증서를 관리하고 갱신 및 발급과 같은 작업을 처리하며 클러스터 내 워크로드에 대해 클러스터 내부 및 클러스터 외부에서 상호 작용하는 구성 요소를 관리할 수 있습니다.

#### 9.8.1. 사용자 워크로드에 대한 인증서 생성

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다.

프로세스

발행자를 생성합니다. 자세한 내용은 "추가 리소스" 섹션의 "문제 구성"을 참조하십시오.

인증서를 생성합니다.

`Certificate` 오브젝트를 정의하는 YAML 파일(예: `certificate.yaml`)을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: <tls_cert>
  namespace: <issuer_namespace>
spec:
  isCA: false
  commonName: '<common_name>'
  secretName: <secret_name>
  dnsNames:
  - "<domain_name>"
  issuerRef:
    name: <issuer_name>
    kind: Issuer
```

1. 인증서의 이름을 입력합니다.

2. 발급자의 네임스페이스를 지정합니다.

3. CN(일반 이름)을 지정합니다.

4. 인증서가 포함된 생성하는 시크릿의 이름을 지정합니다.

5. 도메인 이름을 지정합니다.

6. 발행자의 이름을 지정합니다.

다음 명령을 실행하여 `Certificate` 오브젝트를 생성합니다.

```shell-session
$ oc create -f certificate.yaml
```

검증

다음 명령을 실행하여 인증서가 생성되고 사용할 준비가 되었는지 확인합니다.

```shell-session
$ oc get certificate -w -n <issuer_namespace>
```

인증서가 `Ready` 상태가 되면 클러스터의 워크로드가 생성된 인증서 시크릿을 사용할 수 있습니다.

#### 9.8.2. API 서버에 대한 인증서 생성

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.13.0 이상이 설치되어 있어야 합니다.

프로세스

발행자를 생성합니다. 자세한 내용은 "추가 리소스" 섹션의 "문제 구성"을 참조하십시오.

인증서를 생성합니다.

`Certificate` 오브젝트를 정의하는 YAML 파일(예: `certificate.yaml`)을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: <tls_cert>
  namespace: openshift-config
spec:
  isCA: false
  commonName: "api.<cluster_base_domain>"
  secretName: <secret_name>
  dnsNames:
  - "api.<cluster_base_domain>"
  issuerRef:
    name: <issuer_name>
    kind: Issuer
```

1. 인증서의 이름을 입력합니다.

2. CN(일반 이름)을 지정합니다.

3. 인증서가 포함된 생성하는 시크릿의 이름을 지정합니다.

4. API 서버의 DNS 이름을 지정합니다.

5. 발행자의 이름을 지정합니다.

다음 명령을 실행하여 `Certificate` 오브젝트를 생성합니다.

```shell-session
$ oc create -f certificate.yaml
```

certificate라는 API 서버를 추가합니다. 자세한 내용은 "추가 리소스" 섹션의 "인증서라는 API 서버 추가" 섹션을 참조하십시오.

참고

인증서가 업데이트되었는지 확인하려면 인증서가 생성된 후 아래 명령을 다시 실행합니다.

```shell
oc login
```

검증

다음 명령을 실행하여 인증서가 생성되고 사용할 준비가 되었는지 확인합니다.

```shell-session
$ oc get certificate -w -n openshift-config
```

인증서가 `Ready` 상태가 되면 클러스터의 API 서버가 생성된 인증서 보안을 사용할 수 있습니다.

#### 9.8.3. Ingress 컨트롤러의 인증서 생성

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.13.0 이상이 설치되어 있어야 합니다.

프로세스

발행자를 생성합니다. 자세한 내용은 "추가 리소스" 섹션의 "문제 구성"을 참조하십시오.

인증서를 생성합니다.

`Certificate` 오브젝트를 정의하는 YAML 파일(예: `certificate.yaml`)을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: <tls_cert>
  namespace: openshift-ingress
spec:
  isCA: false
  commonName: "apps.<cluster_base_domain>"
  secretName: <secret_name>
  dnsNames:
  - "apps.<cluster_base_domain>"
  - "*.apps.<cluster_base_domain>"
  issuerRef:
    name: <issuer_name>
    kind: Issuer
```

1. 인증서의 이름을 입력합니다.

2. CN(일반 이름)을 지정합니다.

3. 인증서가 포함된 생성하는 시크릿의 이름을 지정합니다.

4. 5

인그레스의 DNS 이름을 지정합니다.

6. 발행자의 이름을 지정합니다.

다음 명령을 실행하여 `Certificate` 오브젝트를 생성합니다.

```shell-session
$ oc create -f certificate.yaml
```

기본 수신 인증서를 교체합니다. 자세한 내용은 "추가 리소스" 섹션의 "기본 수신 인증서 교체" 섹션을 참조하십시오.

검증

다음 명령을 실행하여 인증서가 생성되고 사용할 준비가 되었는지 확인합니다.

```shell-session
$ oc get certificate -w -n openshift-ingress
```

인증서가 `Ready` 상태가 되면 클러스터의 Ingress 컨트롤러가 생성된 인증서 보안을 사용할 수 있습니다.

#### 9.8.4. 추가 리소스

발행자 구성

지원되는 발급자 유형

ACME 발행자 구성

certificate라는 API 서버 추가

기본 수신 인증서 교체

### 9.9. cert-manager Operator for Red Hat OpenShift를 사용하여 경로 보안

OpenShift Container Platform에서 경로 API는 시크릿을 통해 TLS 인증서를 참조하는 구성 가능한 옵션을 제공하도록 확장됩니다. 외부 관리형 인증서 를 활성화하면 수동 조작으로 인한 오류를 최소화하고 인증서 관리 프로세스를 간소화하며 OpenShift Container Platform 라우터에서 참조된 인증서를 즉시 제공할 수 있습니다.

#### 9.9.1. 클러스터의 경로를 보호하도록 인증서 구성

다음 단계에서는 Let's Encrypt ACME HTTP-01 챌린지 유형과 함께 cert-manager Operator for Red Hat OpenShift를 사용하여 OpenShift Container Platform 클러스터의 경로 리소스를 보호하는 프로세스를 보여줍니다.

사전 요구 사항

Red Hat OpenShift용 cert-manager Operator 버전 1.14.0 이상을 설치했습니다.

경로 `생성` 및 업데이트 모두에 사용되는 `routes/custom-host` 하위 리소스에 대한 생성 권한이 있습니다.

노출하려는 `서비스` 리소스가 있습니다.

프로세스

다음 명령을 실행하여 HTTP-01 솔러를 구성할 `Issuer` 를 만듭니다. 다른 ACME 발행자 유형의 경우 "ACME an issuer 구성"을 참조하십시오.

```yaml
$ oc create -f - << EOF
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: letsencrypt-acme
  namespace: <namespace>
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-acme-account-key
    solvers:
      - http01:
          ingress:
            ingressClassName: openshift-default
EOF
```

1. `Issuer` 가 있는 네임스페이스를 지정합니다. 경로의 네임스페이스와 동일해야 합니다.

다음 명령을 실행하여 경로에 대한 `인증서` 오브젝트를 생성합니다. `secretName` 은 cert-manager에서 발행하고 관리할 TLS 시크릿을 지정하고 다음 단계에서 경로에서도 참조합니다.

```yaml
$ oc create -f - << EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-route-cert
  namespace: <namespace>
spec:
  commonName: <hostname>
  dnsNames:
    - <hostname>
  usages:
    - server auth
  issuerRef:
    kind: Issuer
    name: letsencrypt-acme
  secretName: <secret_name>
EOF
```

1. `인증서`

`리소스가 있는 네임스페이스` 를 지정합니다. 경로의 네임스페이스와 동일해야 합니다.

2. 경로의 호스트 이름을 사용하여 인증서의 일반 이름을 지정합니다.

3. 경로의 호스트 이름을 인증서의 DNS 이름에 추가합니다.

4. 인증서가 포함된 보안의 이름을 지정합니다.

다음 명령을 사용하여 참조된 시크릿을 읽을 수 있는 라우터 서비스 계정 권한을 제공하는 `역할` 을 생성합니다.

```shell-session
$ oc create role secret-reader \
  --verb=get,list,watch \
  --resource=secrets \
  --resource-name=<secret_name> \
  --namespace=<namespace>
```

1. 액세스 권한을 부여할 시크릿 이름을 지정합니다. `인증서` 리소스에 지정된 `secretName` 과 일치해야 합니다.

2. 시크릿과 경로가 모두 있는 네임스페이스를 지정합니다.

다음 명령을 사용하여 새로 생성된 `Role` 리소스와 라우터 서비스 계정을 바인딩할 `RoleBinding` 리소스를 생성합니다.

```shell-session
$ oc create rolebinding secret-reader-binding \
  --role=secret-reader \
  --serviceaccount=openshift-ingress:router \
  --namespace=<namespace>
```

1. 시크릿과 경로가 모두 있는 네임스페이스를 지정합니다.

다음 명령을 실행하여 엣지 TLS 종료 및 사용자 지정 호스트 이름을 사용하는 서비스 리소스의 경로를 생성합니다. 호스트 이름은 다음 단계에서 `인증서` 리소스를 생성할 때 사용됩니다.

```shell-session
$ oc create route edge <route_name> \
  --service=<service_name> \
  --hostname=<hostname> \
  --namespace=<namespace>
```

1. 경로 이름을 지정합니다.

2. 노출하려는 서비스를 지정합니다.

3. 경로의 호스트 이름을 지정합니다.

4. 경로가 있는 네임스페이스를 지정합니다.

경로의 `.spec.tls.externalCertificate` 필드를 업데이트하여 이전에 생성된 보안을 참조하고 다음 명령을 사용하여 cert-manager에서 발급한 인증서를 사용합니다.

```shell-session
$ oc patch route <route_name> \
  -n <namespace> \
  --type=merge \
  -p '{"spec":{"tls":{"externalCertificate":{"name":"<secret_name>"}}}}'
```

1. 경로 이름을 지정합니다.

2. 시크릿과 경로가 모두 있는 네임스페이스를 지정합니다.

3. 인증서가 포함된 보안의 이름을 지정합니다.

검증

다음 명령을 실행하여 인증서가 생성되고 사용할 준비가 되었는지 확인합니다.

```shell-session
$ oc get certificate -n <namespace>
$ oc get secret -n <namespace>
```

1. 2

시크릿과 경로가 모두 있는 네임스페이스를 지정합니다.

다음 명령을 실행하여 라우터에서 참조된 외부 인증서를 사용하고 있는지 확인합니다. 명령은 상태 코드 `200 OK` 와 함께 반환되어야 합니다.

```shell-session
$ curl -IsS https://<hostname>
```

1. 경로의 호스트 이름을 지정합니다.

다음 명령을 실행하여 서버 인증서의 `subject`, `subjectAltName`, `issuer` 가 모두 curl verbose 출력에서 예상대로 표시되는지 확인합니다.

```shell-session
$ curl -v https://<hostname>
```

1. 경로의 호스트 이름을 지정합니다.

이제 경로는 cert-manager가 발행한 참조 시크릿의 인증서로 성공적으로 보호됩니다. cert-manager는 인증서의 라이프 사이클을 자동으로 관리합니다.

#### 9.9.2. 추가 리소스

외부 관리 인증서를 사용하여 경로 생성

ACME 발행자 구성

### 9.10. Red Hat OpenShift용 cert-manager Operator와 Istio-CSR 통합

cert-manager Operator for Red Hat OpenShift는 Red Hat OpenShift Service Mesh 또는 Istio에서 워크로드 및 컨트롤 플레인 구성 요소를 보호하기 위한 향상된 지원을 제공합니다. 여기에는 cert-manager 발행자를 사용하여 서명, 전달 및 갱신되는 상호 TLS(mTLS)를 활성화하는 인증서 지원이 포함됩니다. cert-manager Operator for Red Hat OpenShift 관리 Istio-CSR 에이전트를 사용하여 Istio 워크로드 및 컨트롤 플레인 구성 요소를 보호할 수 있습니다.

이 Istio-CSR 통합을 통해 Istio는 이제 Red Hat OpenShift용 cert-manager Operator에서 인증서를 가져와 보안 및 인증서 관리를 단순화할 수 있습니다.

#### 9.10.1.1. Istio-CSR 에이전트에 대한 루트 CA 발행자 생성

이 절차를 사용하여 Istio-CSR 에이전트에 대한 루트 CA 발행자를 생성합니다.

참고

지원되지 않는 ACME 발행자를 제외하고 지원되는 다른 발급자를 사용할 수 있습니다. 자세한 내용은 "cert-manager Operator for Red Hat OpenShift issuer providers"를 참조하십시오.

프로세스

`Issuer` 및 `Certificate` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: selfsigned
  namespace: <istio_project_name>
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: istio-ca
  namespace: <istio_project_name>
spec:
  isCA: true
  duration: 87600h # 10 years
  secretName: istio-ca
  commonName: istio-ca
  privateKey:
    algorithm: ECDSA
    size: 256
  subject:
    organizations:
      - cluster.local
      - cert-manager
  issuerRef:
    name: selfsigned
    kind: Issuer
    group: cert-manager.io
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: istio-ca
  namespace: <istio_project_name>
spec:
  ca:
    secretName: istio-ca
```

1. 3

4. 발급자 또는 `Cluster Issuer` 를 지정합니다.

2. 5

Istio 프로젝트의 이름을 지정합니다.

검증

다음 명령을 실행하여 Issuer가 생성되고 사용할 준비가 되었는지 확인합니다.

```shell-session
$ oc get issuer istio-ca -n <istio_project_name>
```

```shell-session
NAME       READY   AGE
istio-ca   True    3m
```

추가 리소스

cert-manager Operator for Red Hat OpenShift issuer 공급자

#### 9.10.1.2. IstioCSR 사용자 정의 리소스 생성

cert-manager Operator for Red Hat OpenShift를 통해 Istio-CSR 에이전트를 설치하려면 다음 절차를 사용하십시오.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

Istio-CSR 기능을 활성화했습니다.

Istio-CSR 에이전트의 인증서를 생성하는 데 필요한 발급자 또는 `Cluster Issuer` 리소스를 생성했습니다.

참고

`Issuer` 리소스를 사용하는 경우 Red Hat OpenShift Service Mesh 또는 `Istiod` 네임스페이스에서 발급자 및 `인증서` 리소스를 생성합니다. 인증서 요청은 동일한 네임스페이스에 생성되고 이에 따라 RBAC(역할 기반 액세스 제어)가 구성됩니다.

프로세스

다음 명령을 실행하여 Istio-CSR을 설치하기 위한 새 프로젝트를 생성합니다. Istio-CSR을 설치하기 위한 기존 프로젝트가 있는 경우 이 단계를 건너뜁니다.

```shell-session
$ oc new-project <istio_csr_project_name>
```

`IstioCSR` 사용자 정의 리소스를 생성하여 Istio 워크로드 및 컨트롤 플레인 인증서 서명 요청을 처리하기 위해 cert-manager Operator for Red Hat OpenShift에서 관리하는 Istio-CSR 에이전트를 활성화합니다.

참고

한 번에 하나의 `IstioCSR` CR(사용자 정의 리소스)만 지원됩니다. 여러 `IstioCSR` CR이 생성되면 하나만 활성화됩니다. `IstioCSR` 의 `status` 하위 리소스를 사용하여 리소스가 처리되지 않았는지 확인합니다.

여러 `IstioCSR` CR이 동시에 생성되는 경우 처리되지 않습니다.

여러 `IstioCSR` CR이 순차적으로 생성되는 경우 첫 번째 CSR CR만 처리됩니다.

새 요청이 거부되지 않도록 하려면 처리되지 않은 `IstioCSR` CR을 삭제합니다.

Operator는 `IstioCSR` 용으로 생성된 오브젝트를 자동으로 제거하지 않습니다. 활성 `IstioCSR` 리소스가 삭제되고 이전 배포를 제거하지 않고 다른 네임스페이스에서 새 리소스가 생성되면 여러 `istio-csr` 배포가 활성 상태로 유지될 수 있습니다. 이 동작은 권장되지 않으며 지원되지 않습니다.

`IstioCSR` 오브젝트를 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: IstioCSR
metadata:
  name: default
  namespace: <istio_csr_project_name>
spec:
  istioCSRConfig:
    certManager:
      issuerRef:
        name: istio-ca
        kind: Issuer
        group: cert-manager.io
    istiodTLSConfig:
      trustDomain: cluster.local
    istio:
      namespace: <istio_project_name>
```

1. 발급자 또는 `Cluster Issuer` 이름을 지정합니다. `issuer.yaml` 파일에 정의된 CA 발행자와 동일해야 합니다.

2. 발급자 또는 `Cluster Issuer 유형을` 지정합니다. `issuer.yaml` 파일에 정의된 CA 발행자와 동일해야 합니다.

다음 명령을 실행하여 `IstioCSR` 사용자 지정 리소스를 생성합니다.

```shell-session
$ oc create -f IstioCSR.yaml
```

검증

다음 명령을 실행하여 Istio-CSR 배포가 준비되었는지 확인합니다.

```shell-session
$ oc get deployment -n <istio_csr_project_name>
```

```shell-session
NAME                     READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager-istio-csr   1/1     1            1           24s
```

다음 명령을 실행하여 Istio-CSR 포드가 실행 중인지 확인합니다.

```shell-session
$ oc get pod -n <istio_csr_project_name>
```

```shell-session
NAME                                     READY   STATUS   RESTARTS    AGE
cert-manager-istio-csr-5c979f9b7c-bv57w  1/1     Running  0           45s
```

다음 명령을 실행하여 Istio-CSR Pod에서 로그에 오류를 보고하지 않는지 확인합니다.

```shell-session
$ oc -n <istio_csr_project_name> logs <istio_csr_pod_name>
```

다음 명령을 실행하여 cert-manager Operator for Red Hat OpenShift Pod가 오류를 보고하지 않는지 확인합니다.

```shell-session
$ oc -n cert-manager-operator logs <cert_manager_operator_pod_name>
```

#### 9.10.2. IstioCSR 사용자 정의 리소스 사용자 정의

`IstioCSR` CR(사용자 정의 리소스)을 수정하여 Istio 워크로드가 cert-manager Operator와 상호 작용하는 방식을 정의할 수 있습니다.

#### 9.10.2.1. istio-csr 구성 요소의 로그 수준 설정

istio-csr 구성 요소의 로그 수준을 설정하여 로그 메시지의 상세 정보 표시 및 형식을 제어할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

`IstioCSR` CR(사용자 정의 리소스)을 생성했습니다.

프로세스

다음 명령을 실행하여 `IstioCSR` CR을 편집합니다.

```shell-session
oc edit istiocsrs.operator.openshift.io default -n <istio_csr_project_name>
```

1. & `lt;istio_csr_project_name` >을 `IstioCSR` CR을 생성한 네임스페이스로 바꿉니다.

`spec.istioCSRConfig` 섹션에서 로그 수준 및 형식을 구성합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: IstioCSR
...
spec:
  istioCSRConfig:
    logFormat: text
    logLevel: 2
# ...
```

1. 로그 출력 형식을 지정합니다. 이 필드를 `text` 또는 `json` 으로 설정할 수 있습니다.

2. 로그 수준을 설정합니다. 지원되는 값은 Kubernetes 로깅 지침에 정의된 대로 `1~5` 범위에 있습니다. 기본값은 `1` 입니다.

편집기를 저장하고 종료하여 변경 사항을 적용합니다. 변경 사항이 적용되면 cert-manager Operator에서 istio-csr 피연산자의 로그 구성을 업데이트합니다.

#### 9.10.2.2. CA 번들 배포를 위한 네임스페이스 선택기 구성

Istio-CSR 에이전트는 CA 번들이 포함된 `istio-ca-root-cert`

`ConfigMap` 을 생성하고 업데이트합니다. 서비스 메시의 워크로드는 이 CA 번들을 사용하여 Istio 컨트롤 플레인에 대한 연결을 검증합니다. Istio-CSR 에이전트가 이 `ConfigMap` 을 생성하는 네임스페이스를 지정하도록 네임스페이스 선택기를 구성할 수 있습니다. 선택기를 구성하지 않으면 Istio-CSR 에이전트가 모든 네임스페이스에 `ConfigMap` 을 생성합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

`IstioCSR` CR(사용자 정의 리소스)을 생성했습니다.

프로세스

다음 명령을 실행하여 `IstioCSR` CR을 편집합니다.

```shell-session
oc edit istiocsrs.operator.openshift.io default -n <istio_csr_project_name>
```

1. & `lt;istio_csr_project_name` >을 `IstioCSR` CR을 생성한 네임스페이스로 바꿉니다.

`spec.istioCSRConfig.istioDataPlaneNamespaceSelector` 섹션을 구성하여 네임스페이스 선택기를 설정합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: IstioCSR
...
spec:
  istioCSRConfig:
    istioDataPlaneNamespaceSelector: maistra.io/member-of=istio-system
# ...
```

1. `maistra.io/member-of=istio-system` 을 서비스 메시의 네임스페이스를 식별하는 라벨 키와 값으로 교체합니다. < `key>=<value&` gt; 형식을 사용합니다.

참고

istio-csr 구성 요소는 구성된 선택기와 일치하지 않는 네임스페이스에서 `ConfigMap` 오브젝트를 삭제하거나 관리하지 않습니다. `IstioCSR` CR을 배포한 후 선택기를 생성하거나 업데이트하거나 네임스페이스에서 레이블을 제거하는 경우 충돌을 방지하기 위해 이러한 `ConfigMap` 오브젝트를 수동으로 삭제해야 합니다.

다음 명령을 실행하여 선택기와 일치하는 네임스페이스에 없는 `ConfigMap` 오브젝트를 나열할 수 있습니다. 이 예에서 선택기는 `maistra.io/member-of=istio-system`:입니다.

```shell-session
printf "%-25s %10s\n" "ConfigMap" "Namespace"; \
for ns in $(oc get namespaces -l "maistra.io/member-of!=istio-system" -o=jsonpath='{.items[*].metadata.name}'); do \
  oc get configmaps -l "istio.io/config=true" -n $ns --no-headers -o jsonpath='{.items[*].metadata.name}{"\t"}{.items[*].metadata.namespace}{"\n"}' --ignore-not-found; \
done
```

편집기를 저장하고 종료하여 변경 사항을 적용합니다. 변경 사항을 적용한 후 cert-manager Operator for Red Hat OpenShift는 istio-csr 피연산자의 네임스페이스 선택기 구성을 업데이트합니다.

#### 9.10.2.3. Istio 서버의 CA 인증서 구성

Istio 워크로드에서 Istio 서버 인증서를 확인하는 데 사용하는 CA 번들이 포함된 `ConfigMap` 을 구성할 수 있습니다. 구성되지 않은 경우 cert-manager Operator for Red Hat OpenShift는 구성된 발행자 및 Istio 인증서가 포함된 Kubernetes Secret에서 CA 인증서를 찾습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

`IstioCSR` CR(사용자 정의 리소스)을 생성했습니다.

프로세스

다음 명령을 실행하여 `IstioCSR` CR을 편집합니다.

```shell-session
oc edit istiocsrs.operator.openshift.io default -n <istio_csr_project_name>
```

1. & `lt;istio_csr_project_name` >을 `IstioCSR` CR을 생성한 네임스페이스로 바꿉니다.

`spec.istioCSRConfig.certManager` 섹션을 편집하여 CA 번들을 구성합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: IstioCSR
...
spec:
  istioCSRConfig:
    certManager:
      istioCACertificate:
        key: <key_in_the_configmap>
        name: <configmap_name>
        namespace: <configmap_namespace>
```

1. CA 번들이 포함된 `ConfigMap` 에 키 이름을 지정합니다.

2. `ConfigMap` 의 이름을 지정합니다. 이 필드를 업데이트하기 전에 참조된 `ConfigMap` 및 키가 있는지 확인합니다.

3. 선택 사항: `ConfigMap` 이 존재하는 네임스페이스를 지정합니다. 이 필드를 설정하지 않으면 cert-manager Operator for Red Hat OpenShift는 `IstioCSR` CR을 설치한 네임스페이스에서 `ConfigMap` 을 검색합니다.

참고

CA 인증서가 교체될 때마다 최신 인증서로 `ConfigMap` 을 수동으로 업데이트해야 합니다.

편집기를 저장하고 종료하여 변경 사항을 적용합니다. 변경 사항이 적용되면 cert-manager Operator에서 `istio-csr` 피연산자의 CA 번들을 업데이트합니다.

#### 9.10.3. cert-manager Operator for Red Hat OpenShift에서 관리하는 Istio-CSR 에이전트 설치 제거

cert-manager Operator for Red Hat OpenShift에서 관리하는 Istio-CSR 에이전트를 제거하려면 다음 절차를 사용하십시오.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

Istio-CSR 기능을 활성화했습니다.

`IstioCSR` 사용자 정의 리소스를 생성했습니다.

프로세스

다음 명령을 실행하여 `IstioCSR` 사용자 정의 리소스를 제거합니다.

```shell-session
$ oc -n <istio_csr_project_name> delete istiocsrs.operator.openshift.io default
```

관련 리소스를 제거합니다.

중요

Red Hat OpenShift Service Mesh 또는 Istio 구성 요소가 중단되지 않도록 하려면 다음 리소스를 제거하기 전에 Istio-CSR 서비스 또는 Istio에 발행된 인증서를 참조하는 구성 요소가 없는지 확인합니다.

다음 명령을 실행하여 클러스터 scoped-resources를 나열하고 나중에 참조할 수 있도록 나열된 리소스의 이름을 저장합니다.

```shell-session
$ oc get clusterrolebindings,clusterroles -l "app=cert-manager-istio-csr,app.kubernetes.io/name=cert-manager-istio-csr"
```

다음 명령을 실행하여 Istio-csr 배포된 네임스페이스의 리소스를 나열하고 나중에 참조할 수 있도록 나열된 리소스의 이름을 저장합니다.

```shell-session
$ oc get certificate,deployments,services,serviceaccounts -l "app=cert-manager-istio-csr,app.kubernetes.io/name=cert-manager-istio-csr" -n <istio_csr_project_name>
```

다음 명령을 실행하고 나중에 참조할 수 있도록 나열된 리소스의 이름을 저장하여 Red Hat OpenShift Service Mesh 또는 Istio 배포된 네임스페이스의 리소스를 나열합니다.

```shell-session
$ oc get roles,rolebindings -l "app=cert-manager-istio-csr,app.kubernetes.io/name=cert-manager-istio-csr" -n <istio_csr_project_name>
```

이전 단계에서 나열된 각 리소스에 대해 다음 명령을 실행하여 리소스를 삭제합니다.

```shell-session
$ oc -n <istio_csr_project_name> delete <resource_type>/<resource_name>
```

관련 리소스가 모두 삭제될 때까지 이 프로세스를 반복합니다.

### 9.11. cert-manager Operator의 네트워크 정책 구성

cert-manager Operator for Red Hat OpenShift는 구성 요소에 대한 수신 및 송신 트래픽을 제어하여 보안을 강화하기 위해 사전 정의된 `NetworkPolicy` 리소스를 제공합니다. 기본적으로 이 기능은 업그레이드 중에 연결 문제 또는 변경 사항을 손상시키지 않도록 비활성화되어 있습니다. 이 기능을 사용하려면 `CertManager` CR(사용자 정의 리소스)에서 활성화해야 합니다.

기본 정책을 활성화한 후 아웃바운드 트래픽을 허용하도록 추가 송신 규칙을 수동으로 구성해야 합니다. cert-manager Operator for Red Hat OpenShift가 API 서버 및 내부 DNS 이외의 외부 서비스와 통신하려면 이러한 규칙이 필요합니다.

사용자 정의 송신 규칙이 필요한 서비스의 예는 다음과 같습니다.

ACME 서버, 예를 들어, Let's Encrypt

DNS-01 챌린지 공급자(예: AWS Route53 또는 Cryostat)

HashiCorp Vault와 같은 외부 CA

참고

네트워크 정책은 향후 릴리스에서 기본적으로 활성화되어야 하므로 업그레이드 중에 연결 오류가 발생할 수 있습니다. 이 변경 사항을 준비하려면 필요한 송신 정책을 구성합니다.

#### 9.11.1. 기본 수신 및 송신 규칙

기본 네트워크 정책은 다음 수신 및 송신 규칙을 각 구성 요소에 적용합니다.

| Component | Ingress 포트 | 송신 포트 | 설명 |
| --- | --- | --- | --- |
| `cert-manager` | 9402 | 6443, 5353 | 메트릭 서버로의 수신 트래픽 및 OpenShift API 서버로의 송신 트래픽을 허용합니다. |
| `cert-manager-webhook` | 9402, 10250 | 6443 | 메트릭 및 웹 후크 서버에 대한 수신 트래픽과 OpenShift API 서버 및 내부 DNS 서버로의 송신 트래픽을 허용합니다. |
| `cert-manager-cainjector` | 9402 | 6443 | 메트릭 서버로의 수신 트래픽 및 OpenShift API 서버로의 송신 트래픽을 허용합니다. |
| `istio-csr` | 6443, 9402 | 6443 | gRPC Istio 인증서 요청 API, 지표 서버 및 OpenShift API 서버로의 송신 트래픽에 대한 수신 트래픽을 허용합니다. |

#### 9.11.2. 네트워크 정책 구성 매개변수

`CertManager` CR(사용자 정의 리소스)을 업데이트하여 cert-manager Operator 구성 요소에 대한 네트워크 정책을 활성화하고 구성할 수 있습니다. CR에는 기본 네트워크 정책을 활성화하고 사용자 정의 송신 규칙을 정의하는 데 필요한 다음 매개변수가 포함되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `spec.defaultNetworkPolicy` | `boolean` | cert-manager Operator 구성 요소에 대한 기본 네트워크 정책을 활성화할지 여부를 지정합니다. 중요 기본 네트워크 정책을 활성화하면 비활성화할 수 없습니다. 이러한 제한은 실수로 보안 저하를 방지합니다. 이 설정을 활성화하기 전에 네트워크 정책 요구 사항을 계획해야 합니다. |
| `spec.networkPolicies` | `object` | 사용자 지정 네트워크 정책 구성 목록을 정의합니다. 구성을 적용하려면 `spec.defaultNetworkPolicy` 를 `true` 로 설정해야 합니다. |
| `spec.networkPolicies.componentName` | `string` | 이 네트워크 정책의 대상으로 하는 구성 요소를 지정합니다. 유일한 유효한 값은 `CoreController` 입니다. |
| `spec.networkPolicies.egress` | `object` | 지정된 구성 요소에 대한 송신 규칙을 정의합니다. 모든 외부 공급자에 대한 연결을 허용하려면 `{}` 로 설정합니다. |
| `spec.networkPolicies.egress.ports` | `object` | 지정된 공급자에 대한 네트워크 포트 및 프로토콜 목록을 정의합니다. |
| `spec.networkPolicies.name` | `string` | `NetworkPolicy` 리소스 이름을 생성하는 데 사용되는 사용자 지정 네트워크 정책의 고유한 이름을 지정합니다. |

#### 9.11.3. 네트워크 정책 구성 예

다음 예제에서는 네트워크 정책 및 사용자 지정 규칙 활성화와 관련된 다양한 시나리오를 다룹니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
spec:
  defaultNetworkPolicy: "true"
```

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
spec:
  defaultNetworkPolicy: "true"
  networkPolicies:
  - name: allow-egress-to-all
    componentName: CoreController
    egress:
     - {}
```

특정 발행자 공급자에 대한 송신 허용 예

다음 구성을 사용하면 cert-manager Operator 컨트롤러에서 ACME 챌린지 자체 확인을 수행할 수 있습니다. 이 프로세스에서는 ACME 공급자, DNS API 엔드포인트 및 재귀 DNS 서버에 대한 연결이 필요합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
metadata:
  name: cluster
spec:
  defaultNetworkPolicy: "true"
  networkPolicies:
  - name: allow-egress-to-acme-server
    componentName: CoreController
    egress:
    - ports:
      - port: 80
        protocol: TCP
      - port: 443
        protocol: TCP
  - name: allow-egress-to-dns-service
    componentName: CoreController
    egress:
    - ports:
      - port: 53
        protocol: UDP
      - port: 53
        protocol: TCP
```

#### 9.11.4. 네트워크 정책 생성 확인

기본 및 사용자 지정 `NetworkPolicy` 리소스가 생성되었는지 확인할 수 있습니다.

사전 요구 사항

`CertManager` 사용자 정의 리소스에서 cert-manager Operator for Red Hat OpenShift에 대한 네트워크 정책을 활성화했습니다.

프로세스

다음 명령을 실행하여 `cert-manager` 네임스페이스에서 `NetworkPolicy` 리소스 목록을 확인합니다.

```shell-session
$ oc get networkpolicy -n cert-manager
```

```shell-session
NAME                                             POD-SELECTOR                              AGE
cert-manager-allow-egress-to-api-server          app.kubernetes.io/instance=cert-manager   7s
cert-manager-allow-egress-to-dns                 app=cert-manager                          6s
cert-manager-allow-ingress-to-metrics            app.kubernetes.io/instance=cert-manager   7s
cert-manager-allow-ingress-to-webhook            app=webhook                               6s
cert-manager-deny-all                            app.kubernetes.io/instance=cert-manager   8s
cert-manager-user-allow-egress-to-acme-server    app=cert-manager                          8s
cert-manager-user-allow-egress-to-dns-service    app=cert-manager                          7s
```

출력에 기본 정책 및 사용자가 생성한 모든 사용자 지정 정책이 나열됩니다.

### 9.12. Monitoring cert-manager Operator for Red Hat OpenShift

기본적으로 cert-manager Operator for Red Hat OpenShift는 세 가지 핵심 구성 요소(controller, cainjector, webhook)에 대한 지표를 표시합니다. Prometheus Operator 형식을 사용하여 이러한 지표를 수집하도록 OpenShift 모니터링을 구성할 수 있습니다.

#### 9.12.1. 사용자 워크로드 모니터링 활성화

클러스터에서 사용자 워크로드 모니터링을 구성하여 사용자 정의 프로젝트에 대한 모니터링을 활성화할 수 있습니다. 자세한 내용은 "사용자 정의 프로젝트에 대한 메트릭 컬렉션 설정"을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`cluster-monitoring-config.yaml` YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |
    enableUserWorkload: true
```

다음 명령을 실행하여 `ConfigMap` 을 적용합니다.

```shell-session
$ oc apply -f cluster-monitoring-config.yaml
```

검증

다음 명령을 실행하여 사용자 워크로드에 대한 모니터링 구성 요소가 `openshift-user-workload-monitoring` 네임스페이스에서 실행되고 있는지 확인합니다.

```shell-session
$ oc -n openshift-user-workload-monitoring get pod
```

```shell-session
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-6cb6bd9588-dtzxq   2/2     Running   0          50s
prometheus-user-workload-0             6/6     Running   0          48s
prometheus-user-workload-1             6/6     Running   0          48s
thanos-ruler-user-workload-0           4/4     Running   0          42s
thanos-ruler-user-workload-1           4/4     Running   0          42s
```

`prometheus-operator`, `prometheus-user-workload`, `thanos-ruler-user-workload` 와 같은 Pod의 상태는 `Running` 이어야 합니다.

추가 리소스

사용자 정의 프로젝트에 대한 메트릭 컬렉션 설정

#### 9.12.2. ServiceMonitor를 사용하여 Red Hat OpenShift 피연산자에 대한 cert-manager Operator의 메트릭 컬렉션 구성

cert-manager Operator for Red Hat OpenShift 피연산자s는 기본적으로 `/metrics` 서비스 끝점의 포트 `9402` 에 메트릭을 노출합니다. Prometheus Operator가 사용자 정의 메트릭을 수집할 수 있는 `ServiceMonitor` CR(사용자 정의 리소스)을 생성하여 cert-manager 피연산자에 대한 메트릭 컬렉션을 구성할 수 있습니다. 자세한 내용은 "사용자 워크로드 모니터링 구성"을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다.

사용자 워크로드 모니터링을 활성화했습니다.

프로세스

`ServiceMonitor` CR을 생성합니다.

`ServiceMonitor` CR을 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    app: cert-manager
    app.kubernetes.io/instance: cert-manager
    app.kubernetes.io/name: cert-manager
  name: cert-manager
  namespace: cert-manager
spec:
  endpoints:
    - honorLabels: false
      interval: 60s
      path: /metrics
      scrapeTimeout: 30s
      targetPort: 9402
  selector:
    matchExpressions:
      - key: app.kubernetes.io/name
        operator: In
        values:
          - cainjector
          - cert-manager
          - webhook
      - key: app.kubernetes.io/instance
        operator: In
        values:
          - cert-manager
      - key: app.kubernetes.io/component
        operator: In
        values:
          - cainjector
          - controller
          - webhook
```

다음 명령을 실행하여 `ServiceMonitor` CR을 생성합니다.

```shell-session
$ oc apply -f servicemonitor-cert-manager.yaml
```

`ServiceMonitor` CR이 생성되면 사용자 워크로드 Prometheus 인스턴스는 Red Hat OpenShift 피연산자용 cert-manager Operator에서 메트릭 수집을 시작합니다. 수집된 지표는 `job="cert-manager"`, `job="cert-manager-cainjector"` 및 `job="cert-manager-webhook"` 로 레이블이 지정됩니다.

검증

OpenShift Container Platform 웹 콘솔에서 모니터링 → 대상으로

이동합니다.

라벨 필터 필드에 다음 레이블을 입력하여 각 피연산자의 메트릭 대상을 필터링합니다.

```shell-session
$ service=cert-manager
```

```shell-session
$ service=cert-manager-webhook
```

```shell-session
$ service=cert-manager-cainjector
```

Status (상태) 열에 cert-manager, `cert-manager -webhook`, `cert-manager-cainjector` 항목에 대한 `Up` 이 표시되는지 확인합니다.

추가 리소스

사용자 워크로드 모니터링 구성

#### 9.12.3. Red Hat OpenShift 피연산자용 cert-manager Operator의 메트릭 쿼리

클러스터 관리자 또는 모든 네임스페이스에 대한 보기 액세스 권한이 있는 사용자는 OpenShift Container Platform 웹 콘솔 또는 CLI(명령줄 인터페이스)를 사용하여 Red Hat OpenShift 피연산자 메트릭에 대해 cert-manager Operator를 쿼리할 수 있습니다. 자세한 내용은 " metrics 액세스"를 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다.

`ServiceMonitor` 오브젝트를 생성하여 모니터링 및 메트릭 컬렉션을 활성화했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 모니터링 → 메트릭 으로 이동합니다.

쿼리 필드에 다음 PromQL 표현식을 입력하여 각 피연산자에 대한 cert-manager Operator for Red Hat OpenShift 피연산자 메트릭을 쿼리합니다.

```plaintext
{job="cert-manager"}
```

```plaintext
{job="cert-manager-webhook"}
```

```plaintext
{job="cert-manager-cainjector"}
```

추가 리소스

메트릭 액세스

#### 9.12.4. istio-csr 피연산자에 대한 메트릭 컬렉션 구성

istio-csr 피연산자는 기본적으로 `/metrics` 서비스 끝점의 포트 `9402` 에 지표를 노출합니다. `ServiceMonitor` CR(사용자 정의 리소스)을 생성하여 피연산자에 대한 메트릭 컬렉션을 구성하여 Prometheus Operator에서 사용자 정의 지표를 수집할 수 있습니다. 자세한 내용은 "사용자 워크로드 모니터링 구성"을 참조하십시오.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다.

사용자 워크로드 모니터링을 활성화했습니다.

프로세스

`ServiceMonitor` CR 정의 파일을 생성합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    app: cert-manager-istio-csr
    app.kubernetes.io/instance: cert-manager-istio-csr
    app.kubernetes.io/name: cert-manager-istio-csr
  name: cert-manager-istio-csr
  namespace: <istio_csr_project_name>
spec:
  endpoints:
    - honorLabels: false
      interval: 60s
      path: /metrics
      scrapeTimeout: 30s
      targetPort: 9402
  namespaceSelector:
    matchNames:
      - <istio_csr_project_name>
  selector:
    matchLabels:
      app: cert-manager-istio-csr
      app.kubernetes.io/instance: cert-manager-istio-csr
      app.kubernetes.io/name: cert-manager-istio-csr
```

1. 2

& `lt;istio_csr_project_name` >을 `IstioCSR` CR을 생성한 네임스페이스로 바꿉니다.

다음 명령을 실행하여 `ServiceMonitor` CR을 생성합니다.

```shell-session
$ oc apply -f servicemonitor-istio-csr.yaml
```

`ServiceMonitor` CR이 생성되면 사용자 워크로드 Prometheus 인스턴스가 istio-csr 피연산자에서 메트릭 수집을 시작합니다. 수집된 지표는 `job="cert-manager-istio-csr"` 로 레이블이 지정됩니다.

검증

OpenShift Container Platform 웹 콘솔에 로그인합니다.

모니터링 → 대상 을 클릭합니다.

라벨 필터 필드에 `service=cert-manager-istio-csr` 레이블을 입력하여 지표 대상을 필터링합니다.

`cert-manager-istio-csr` 대상에 대한 상태 열에 Up 이 표시되는지 확인합니다.

추가 리소스

사용자 워크로드 모니터링 구성

#### 9.12.5. istio-csr 피연산자의 메트릭 쿼리

클러스터 관리자 또는 모든 네임스페이스에 대한 보기 액세스 권한이 있는 사용자는 OpenShift Container Platform 웹 콘솔을 사용하여 istio-csr 피연산자에 대한 메트릭을 쿼리할 수 있습니다. 자세한 내용은 " metrics 액세스"를 참조하십시오.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다.

istio-csr 피연산자에 대한 `ServiceMonitor` 오브젝트를 생성하여 모니터링 및 메트릭 컬렉션을 활성화했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

모니터링 → 메트릭 을 클릭합니다.

쿼리 필드에 다음 PromQL 표현식을 입력하여 `istio-csr` 피연산자 메트릭을 쿼리합니다.

`{job="cert-manager-istio-csr"}`

results에는 istio-csr 피연산자에 대해 수집된 지표가 표시되어 성능 및 동작을 모니터링하는 데 도움이 될 수 있습니다.

추가 리소스

관리자로 메트릭에 액세스

### 9.13. cert-manager 및 cert-manager Operator for Red Hat OpenShift의 로그 수준 구성

cert-manager 구성 요소 및 cert-manager Operator for Red Hat OpenShift 관련 문제를 해결하려면 로그 수준 세부 정보 표시를 구성할 수 있습니다.

참고

다른 cert-manager 구성 요소에 대해 다른 로그 수준을 사용하려면 cert-manager Operator API 필드 사용자 지정을 참조하십시오.

#### 9.13.1. cert-manager의 로그 수준 설정

cert-manager의 로그 수준을 설정하여 로그 메시지의 상세 수준을 확인할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.11.1 이상이 설치되어 있어야 합니다.

프로세스

다음 명령을 실행하여 `CertManager` 리소스를 편집합니다.

```shell-session
$ oc edit certmanager.operator cluster
```

`spec.logLevel` 섹션을 편집하여 로그 수준 값을 설정합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: CertManager
...
spec:
  logLevel: <log_level>
```

1. `CertManager` 리소스에 유효한 로그 수준 값은 `Normal`, `Debug`, `Trace`, `TraceAll` 입니다. 로그 감사 및 문제가 없을 때 일반적인 작업을 수행하려면 `logLevel` 을 `Normal` 으로 설정합니다. 자세한 로그를 확인하여 마이너 문제를 해결하려면 `logLevel` 을 `Debug` 로 설정합니다. 더 자세한 로그를 확인하여 주요 문제를 해결하려면 `logLevel` 을 `Trace` 로 설정할 수 있습니다. 심각한 문제를 해결하려면 `logLevel` 을 `TraceAll` 로 설정합니다. 기본 `logLevel` 은 `Normal` 입니다.

참고

`TraceAll` 은 대량의 로그를 생성합니다. `logLevel` 을 `TraceAll` 로 설정한 후 성능 문제가 발생할 수 있습니다.

변경 사항을 저장하고 텍스트 편집기를 종료하여 변경 사항을 적용합니다.

변경 사항을 적용하면 cert-manager 구성 요소 컨트롤러, CA 인젝터 및 Webhook의 상세 정보 표시 수준이 업데이트됩니다.

#### 9.13.2. cert-manager Operator for Red Hat OpenShift의 로그 수준 설정

cert-manager Operator for Red Hat OpenShift의 로그 수준을 설정하여 Operator 로그 메시지의 상세 수준을 확인할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

Red Hat OpenShift용 cert-manager Operator 버전 1.11.1 이상이 설치되어 있어야 합니다.

프로세스

다음 명령을 실행하여 operator 로그에 대한 상세 정보 표시 수준을 제공하도록 cert-manager Operator for Red Hat OpenShift의 서브스크립션 오브젝트를 업데이트합니다.

```shell-session
$ oc -n cert-manager-operator patch subscription openshift-cert-manager-operator --type='merge' -p '{"spec":{"config":{"env":[{"name":"OPERATOR_LOG_LEVEL","value":"v"}]}}}'
```

1. `v` 를 원하는 로그 수준 번호로 바꿉니다. `v` 에 유효한 값은 `1'에서 '10 까지의 범위를 지정할` 수 있습니다. 기본값은 `2` 입니다.

검증

cert-manager Operator Pod가 재배포됩니다. 다음 명령을 실행하여 Red Hat OpenShift용 cert-manager Operator의 로그 수준이 업데이트되었는지 확인합니다.

```shell-session
$ oc set env deploy/cert-manager-operator-controller-manager -n cert-manager-operator --list | grep -e OPERATOR_LOG_LEVEL -e container
```

```shell-session
# deployments/cert-manager-operator-controller-manager, container kube-rbac-proxy
OPERATOR_LOG_LEVEL=9
# deployments/cert-manager-operator-controller-manager, container cert-manager-operator
OPERATOR_LOG_LEVEL=9
```

아래 명령을 실행하여 Red Hat OpenShift용 cert-manager Operator의 로그 수준이 업데이트되었는지 확인합니다.

```shell
oc logs
```

```shell-session
$ oc logs deploy/cert-manager-operator-controller-manager -n cert-manager-operator
```

#### 9.13.3. 추가 리소스

cert-manager Operator API 필드 사용자 정의

### 9.14. cert-manager Operator for Red Hat OpenShift 설치 제거

Operator를 제거하고 관련 리소스를 제거하여 OpenShift Container Platform에서 cert-manager Operator를 제거할 수 있습니다.

#### 9.14.1. cert-manager Operator for Red Hat OpenShift 설치 제거

웹 콘솔을 사용하여 cert-manager Operator for Red Hat OpenShift를 설치 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

cert-manager Operator for Red Hat OpenShift Operator를 설치 제거합니다.

Ecosystem → 설치된 Operators 로 이동합니다.

cert-manager Operator for Red Hat OpenShift 항목 옆에 있는 옵션 메뉴

를 클릭하고 Operator 설치 제거를 클릭합니다.

확인 대화 상자에서 설치 제거 를 클릭합니다.

#### 9.14.2. cert-manager Operator for Red Hat OpenShift 리소스 제거

cert-manager Operator for Red Hat OpenShift를 설치 제거한 후 클러스터에서 관련 리소스를 제거하는 옵션이 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

`cert-manager` 네임스페이스에 있는 cert-manager, `cainjector`, `webhook` 와 같은 `cert-manager` 구성 요소의 배포를 제거합니다.

프로젝트 드롭다운 메뉴를 클릭하여 사용 가능한 모든 프로젝트 목록을 확인하고 cert-manager 프로젝트를 선택합니다.

워크로드 → 배포로 이동합니다.

삭제할 배포를 선택합니다.

작업 드롭다운 메뉴를 클릭하고 배포 삭제 를 선택하여 확인 대화 상자를 확인합니다.

삭제 를 클릭하여 배포를 삭제합니다.

또는 CLI(명령줄 인터페이스)를 사용하여 `cert-manager`, `cainjector` 및 `webhook` 와 같은 `cert-manager` 구성 요소의 배포를 삭제합니다.

```shell-session
$ oc delete deployment -n cert-manager -l app.kubernetes.io/instance=cert-manager
```

선택사항: cert-manager Operator for Red Hat OpenShift에서 설치한 CRD(사용자 정의 리소스 정의)를 제거합니다.

다음 명령을 실행하여 `CertManager` CR(사용자 정의 리소스)에서 종료자를 제거합니다.

```shell-session
$ oc patch certmanagers.operator cluster --type=merge -p='{"metadata":{"finalizers":null}}'
```

관리 → 클러스터 리소스 정의 로 이동합니다.

Name 필드에 `certmanager` 를 입력하여 CRD를 필터링합니다.

다음 각 CRD 옆에 있는 옵션 메뉴

를 클릭하고 사용자 정의 리소스 정의 삭제 를 선택합니다.

`certificate`

`CertificateRequest`

`CertManager` (`operator.openshift.io`)

`과제`

`ClusterIssuer`

`issuer`

`주문`

선택사항: `cert-manager-operator` 네임스페이스를 제거합니다.

관리 → 네임스페이스 로 이동합니다.

cert-manager-operator 옆에 있는 옵션 메뉴

를 클릭하고 네임스페이스 삭제 를 선택합니다.

확인 대화 상자에서 필드에 `cert-manager-operator` 를 입력하고 삭제 를 클릭합니다.

### 10.1. Zero Trust Workload Identity Manager 개요

중요

Zero Trust Workload Identity Manager는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

Zero Trust Workload Identity Manager는 SPIFFE(Secure Production Identity Framework for Everyone) 및 SPIFFE 런타임 환경(SPIRE)을 활용하여 분산 시스템에 대한 포괄적인 ID 관리 솔루션을 제공합니다. SPIFFE 및 SPIRE는 워크로드 ID에 대한 표준화된 접근 방식을 제공하여 워크로드가 동일한 클러스터 또는 다른 환경에서 다른 서비스와 통신할 수 있습니다.

Zero Trust Workload Identity Manager는 수명이 오래되고 수동으로 관리되는 보안을 암호화 방식으로 확인할 수 있는 ID로 대체합니다. 워크로드가 서로 통신할 수 있도록 하는 강력한 인증을 제공합니다. SPIRE는 SPIFFE SVID(확인 가능한 ID 문서)의 발행, 회전 및 취소를 자동화하여 시크릿을 관리하는 개발자 및 관리자의 워크로드를 줄입니다.

SPIFFE는 온프레미스, 클라우드 및 하이브리드 환경을 포함한 다양한 인프라에서 작동할 수 있습니다. SPIFFE ID는 암호화 방식으로 활성화되며 감사 및 규정 준수의 기반이 됩니다.

다음은 Zero Trust Workload Identity Manager 아키텍처의 구성 요소입니다.

#### 10.1.1. SPIFFE

SPIFFE(Secure Production Identity Framework for Everyone)는 분산 시스템에서 소프트웨어 워크로드 간 신뢰를 구축하기 위한 표준화된 방법을 제공합니다. SPIFFE는 SPIFFE ID라는 고유한 ID를 할당합니다. 이러한 ID는 신뢰 도메인과 워크로드 식별자를 포함하는 URI(Uniform Resource Identifier)입니다.

SPIFFE ID는 SPIFFE Verifiable Identity Document (SVID)에 포함되어 있습니다. SVID는 워크로드가 서로 통신할 수 있도록 다른 워크로드에 대한 ID를 확인하는 데 사용됩니다. 두 가지 주요 SVID 형식은 다음과 같습니다.

X.509-SVIDs: SPIFFE ID가 SAN(주체 대체 이름) 필드에 포함된 X.509 인증서입니다.

JWT-SVIDs: SPIFFE ID가 `하위` 클레임으로 포함된 JWT(JSON Web Tokens)입니다.

자세한 내용은 SPIFFE 개요 를 참조하십시오.

#### 10.1.2. SPIRE 서버

SPIRE 서버는 신뢰 도메인 내에서 SPIFFE ID를 관리하고 발행하는 역할을 담당합니다. SPIFFE ID를 발행해야 하는 조건 하에서 결정하는 등록 항목(selector) 및 서명 키를 저장합니다. SPIRE 서버는 SPIRE 에이전트와 함께 작동하여 노드 플러그인을 통해 노드 테스트를 수행합니다. 자세한 내용은 SPIRE Server 정보를 참조하십시오.

#### 10.1.3. SPIRE 에이전트

SPIRE 에이전트는 워크로드 검증을 담당하여 SPIFFE Workload API를 통해 인증을 요청할 때 워크로드가 확인된 ID를 수신하도록 합니다. 구성된 워크로드 attestor 플러그인을 사용하여 이를 수행합니다. Kubernetes 환경에서는 Kubernetes 워크로드 attestor 플러그인이 사용됩니다.

SPIRE 및 SPIRE Agent는 노드 플러그인을 통해 노드 검증을 수행합니다. 플러그인은 에이전트가 실행 중인 노드의 ID를 확인하는 데 사용됩니다. 자세한 내용은 SPIRE 에이전트 정보를 참조하십시오.

#### 10.1.4. 인증

인증은 SPIFFE ID 및 SVID가 발행되기 전에 노드 및 워크로드의 ID를 확인하는 프로세스입니다. SPIRE Server는 SPIRE 에이전트가 실행하는 워크로드와 노드의 속성을 수집한 다음, 워크로드가 등록될 때 정의된 선택기 세트와 비교합니다. 비교가 성공하면 엔터티에 자격 증명이 제공됩니다. 이렇게 하면 신뢰 도메인 내의 합법적이고 예상되는 엔티티만 암호화 ID를 수신할 수 있습니다. SPIFFE/SPIRE의 두 가지 주요 인증 유형은 다음과 같습니다.

노드 인증: 해당 노드에서 실행 중인 SPIRE 에이전트를 신뢰하여 워크로드에 대한 ID를 요청할 수 있기 전에 시스템의 머신 또는 노드의 ID를 확인합니다.

워크로드 인증: 해당 노드의 SPIRE 에이전트가 SPIFFE ID 및 SVID를 제공하기 전에 테스트된 노드에서 실행 중인 애플리케이션 또는 서비스의 ID를 확인합니다.

자세한 내용은 인증을 참조하십시오.

#### 10.1.5. Zero Trust Workload Identity Manager 구성 요소

다음 구성 요소는 Zero Trust Workload Identity Manager의 초기 릴리스의 일부로 제공됩니다.

#### 10.1.5.1. SPIFFE CSI 드라이버

SPIFFE CSI(Container Storage Interface)는 Pod에서 Workload API 소켓을 Pod에 전달하여 SPIFFE 확인 가능한 ID 문서(SVID)를 안전하게 얻을 수 있도록 지원하는 플러그인입니다. SPIFFE CSI 드라이버는 클러스터에 데몬 세트로 배포되어 각 노드에서 드라이버 인스턴스가 실행됩니다. 드라이버는 Kubernetes의 임시 인라인 볼륨 기능을 사용하여 Pod가 SPIFFE CSI 드라이버에서 직접 제공하는 볼륨을 요청할 수 있습니다. 이렇게 하면 임시 스토리지가 필요한 애플리케이션에서 사용이 간소화됩니다.

Pod가 시작되면 Kubelet은 SPIFFE CSI 드라이버를 호출하여 볼륨을 Pod의 컨테이너에 프로비저닝하고 마운트합니다. SPIFFE CSI 드라이버는 SPIFFE Workload API를 포함하는 디렉터리를 Pod에 마운트합니다. 그런 다음 Pod의 애플리케이션은 Workload API와 통신하여 SVID를 가져옵니다. 드라이버는 각 SVID가 고유한 것을 보장합니다.

#### 10.1.5.2. SPIRE OpenID Connect 검색 공급자

SPIRE OpenID Connect Discovery Provider는 공개 ID 구성 끝점 및 토큰 확인을 위한 JWKS URI를 노출하여 표준 OpenID Connect(OIDC) 사용자와 호환되는 SPIRE-issued JWT-SVID를 만드는 독립형 구성 요소입니다. 특히 외부 API를 OIDC 호환 토큰이 필요한 시스템과 SPIRE 기반 워크로드 ID를 통합하는 것이 중요합니다. SPIRE는 주로 워크로드에 대한 ID를 발행하지만, 추가 워크로드 관련 클레임은 SPIRE 구성을 통해 JWT-SVID에 포함될 수 있습니다. 이 클레임은 토큰에 포함되어 OIDC 호환 클라이언트가 확인합니다.

#### 10.1.5.3. SPIRE 컨트롤러 관리자

SPIRE 컨트롤러 관리자는 CRD(사용자 정의 리소스 정의)를 사용하여 워크로드를 쉽게 등록할 수 있습니다. 워크로드 등록을 용이하게 하기 위해 SPIRE 컨트롤러 관리자는 Pod 및 CRD에 대한 컨트롤러를 등록합니다. 이러한 리소스에서 변경 사항이 감지되면 워크로드 조정 프로세스가 트리거됩니다. 이 프로세스에서는 기존 Pod 및 CRD를 기반으로 해야 하는 SPIRE 항목이 결정됩니다. 조정 프로세스는 필요에 따라 SPIRE 서버에서 항목을 생성, 업데이트 및 삭제합니다.

SPIRE 컨트롤러 관리자는 SPIRE 서버와 동일한 Pod에 배포되도록 설계되었습니다. 관리자는 공유 볼륨 내의 프라이빗 UNIX 도메인 소켓을 사용하여 SPIRE 서버 API와 통신합니다.

#### 10.1.6.1. SPIRE 서버 및 에이전트 Telemetry

SPIRE Server 및 Agent Telemetry에서는 SPIRE 배포 상태에 대한 통찰력을 제공합니다. 지표는 Prometheus Operator에서 제공하는 형식으로 되어 있습니다. 서버 상태 및 라이프사이클, SPIRE 구성 요소 성능, 테스트 및 SVID 발급 및 플러그인 통계를 이해하는 데 도움이 되는 메트릭입니다.

#### 10.1.7. Zero Trust Workload Identity Manager 워크플로 정보

다음은 Red Hat OpenShift 클러스터 내 Zero Trust Workload Identity Manager의 고급 워크플로입니다.

SPIRE, SPIRE Agent, SPIFFE CSI Driver 및 SPIRE OIDC 검색 공급자 피연산자는 연결된 CRD(고객 리소스 정의)를 통해 Zero Trust Workload Identity Manager에서 배포 및 관리합니다.

그런 다음 관련 Kubernetes 리소스에 대해 감시를 등록하고 필요한 SPIRE CRD가 클러스터에 적용됩니다.

`cluster` 라는 ZeroTrustWorkloadIdentityManager 리소스의 CR은 컨트롤러에서 배포 및 관리합니다.

SPIRE Server, SPIRE Agent, SPIFFE CSI Driver 및 SPIRE OIDC 검색 공급자를 배포하려면 각 특정 유형의 사용자 지정 리소스를 생성하고 `클러스터` 이름을 지정해야 합니다. 사용자 정의 리소스 유형은 다음과 같습니다.

SPIRE 서버 - `SpireServer`

SPIRE Agent - `SpireAgent`

SPIFFE CSI 드라이버 - `SpiffeCSIDriver`

SPIRE OIDC 검색 공급자 - `SpireOIDCDiscoveryProvider`

노드가 시작되면 SPIRE 에이전트가 초기화되고 SPIRE 서버에 연결됩니다.

SPIRE 에이전트는 노드 인증 프로세스를 시작합니다. 에이전트는 라벨 이름 및 네임스페이스와 같은 노드의 ID에 대한 정보를 수집합니다. 에이전트는 SPIRE Server의 인증을 통해 수집된 정보를 안전하게 제공합니다.

그런 다음 SPIRE 서버는 구성된 인증 정책 및 등록 항목에 대해 이 정보를 평가합니다. 성공하면 서버는 에이전트 SVID 및 CA 인증서(Trust Bundle)를 생성하고 이를 SPIRE 에이전트로 안전하게 전송합니다.

워크로드는 노드에서 시작되고 보안 ID가 필요합니다. 워크로드는 에이전트의 Workload API에 연결하고 SVID를 요청합니다.

SPIRE 에이전트는 요청을 수신하고 워크로드에 대한 정보를 수집하기 위해 워크로드 인증을 시작합니다.

SPIRE 에이전트가 정보를 수집한 후, 정보가 SPIRE 서버로 전송되고 서버는 구성된 등록 항목을 확인합니다.

SPIRE 에이전트는 워크로드 SVID 및 Trust Bundle을 수신하고 이를 워크로드에 전달합니다. 워크로드는 이제 SVID를 다른 SPIFFE 인식 장치에 표시하여 통신할 수 있습니다.

추가 리소스

워크로드 등록

SPIFFE 개념

추가 사용 사례

### 10.2. Zero Trust Workload Identity Manager 릴리스 노트

Zero Trust Workload Identity Manager는 SPIFFE(Secure Production Identity Framework for Everyone) 및 SPIFFE 런타임 환경(SPIRE)을 활용하여 분산 시스템에 대한 포괄적인 ID 관리 솔루션을 제공합니다. Zero Trust Workload Identity Manager는 피연산자로 실행되는 SPIRE 버전 1.12.4를 지원합니다.

이 릴리스 노트는 Zero Trust Workload Identity Manager의 개발을 추적합니다.

중요

Zero Trust Workload Identity Manager는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 10.2.1. Zero Trust Workload Identity Manager 0.2.0 (기술 프리뷰)

출시 날짜: 2025-09-08

다음 권고는 Zero Trust Workload Identity Manager에 사용할 수 있습니다.

RHBA-2025:15425

RHBA-2025:15426

RHBA-2025:15427

RHBA-2025:15428

이번 Zero Trust Workload Identity Manager 릴리스는 기술 프리뷰입니다.

#### 10.2.1.1.1. 관리되는 OIDC 검색 공급자 경로 지원

Operator는 선택한 기본 설치에 대해 도메인 `*.apps.<cluster_domain` >의 OpenShift 경로를 통해 `SPIREOIDCDiscoveryProvider` 사양을 노출합니다.

`managedRoute` 및 `externalSecretRef` 필드가 `spireOidcDiscoveryProvider` 사양에 추가되었습니다.

`managedRoute` 필드는 부울이며 기본적으로 `true` 로 설정됩니다. `false` 로 설정하면 Operator가 경로 관리를 중지하고 기존 경로가 자동으로 삭제되지 않습니다. `true` 로 다시 설정하면 Operator가 경로 관리를 다시 시작합니다. 경로가 없으면 Operator에서 새 경로를 생성합니다. 경로가 이미 존재하는 경우 충돌이 있는 경우 Operator에서 사용자 구성을 재정의합니다.

`externalSecretRef` 는 `oidc-discovery-provider` 경로 호스트에 대한 TLS 인증서가 있는 외부 관리형 보안을 참조합니다. 제공된 경우 경로의 `.Spec.TLS.ExternalCertificate` 필드가 채워집니다. 자세한 내용은 외부 관리 인증서를 사용하여 경로 생성 을 참조하십시오.

#### 10.2.1.1.2. SPIRE 번들용 사용자 정의 인증 기관 Time-To-Live 활성화

SPIRE 서버 인증서 관리를 위해 다음 TTL(Time-To-Live) 필드가 `SpireServer` CRD(사용자 정의 리소스 정의) API에 추가되었습니다.

`CAValidity` (기본값: 24h)

`DefaultX509Validity` (기본값: 1h)

`DefaultJWTValidity` (기본값: 5m)

서버 구성에서 기본값은 보안 요구 사항에 따라 인증서를 사용자 지정할 수 있는 유연성을 제공하는 사용자 구성 가능한 옵션으로 교체될 수 있으며, 이는 보안 요구 사항에 따라 인증서 및 SVID(확인 가능한 ID 문서) 수명을 사용자 지정할 수 있습니다.

#### 10.2.1.1.3. 수동 사용자 구성 활성화

Operator의 API에 `ztwim.openshift.io/ create-only =true` 주석이 있으면 Operator 컨트롤러에서 생성 전용 모드로 전환합니다. 그러면 업데이트를 건너뛰는 동안 리소스를 생성할 수 있습니다. 사용자는 리소스를 수동으로 업데이트하여 구성을 테스트할 수 있습니다. 이 주석은 `SpireServer`, `SpireAgents`, `SpiffeCSIDriver`, `SpireOIDCDiscoveryProvider`, 그리고 `ZeroTrustWorkloadIdentityManager` 와 같은 API를 지원합니다.

주석이 적용되면 Operator에서 생성 및 관리하는 리소스를 포함하여 파생된 모든 리소스가 적용됩니다.

주석이 제거되고 Pod가 재시작되면 Operator는 필수 상태로 돌아가려고 합니다. 주석은 시작 중 또는 재시작 중에 한 번만 적용됩니다.

#### 10.2.1.2. 버그 수정

이번 업데이트 이전에는 `SpireServer` 및 `SpireOidcDiscoveryProvider` 모두에 대한 `JwtIssuer` 필드가 구성 오류를 유발하는 URL일 필요가 없었습니다. 이번 릴리스에서는 두 사용자 정의 리소스의 `JwtIssuer` 필드에 발행자 URL을 수동으로 입력해야 합니다. (SPIRE-117)

#### 10.2.2. Zero Trust Workload Identity Manager 0.1.0 (기술 프리뷰)

출시 날짜: 2025-06-16

다음 권고는 Zero Trust Workload Identity Manager에 사용할 수 있습니다.

RHBA-2025:9088

RHBA-2025:9085

RHBA-2025:9090

RHBA-2025:9084

RHBA-2025:9089

RHBA-2025:9087

RHBA-2025:9101

RHBA-2025:9104

이 Zero Trust Workload Identity Manager의 초기 릴리스는 기술 프리뷰입니다. 이 버전에는 다음과 같은 알려진 제한 사항이 있습니다.

SPIRE 페더레이션 지원은 사용할 수 없습니다.

키 관리자는 `디스크` 스토리지 유형만 지원합니다.

Telemetry는 Prometheus를 통해서만 지원됩니다.

SPIRE Servers의 HA(고가용성) 구성 또는 OpenID Connect(OIDC) 검색 공급자는 지원되지 않습니다.

외부 데이터 저장소는 지원되지 않습니다. 이 버전은 SPIRE에서 배포한 내부 `sqlite` 데이터 저장소를 사용합니다.

이 버전은 고정된 구성을 사용하여 작동합니다. 사용자 정의 구성은 허용되지 않습니다.

피연산자의 로그 수준은 구성할 수 없습니다. 기본값은 `DEBUG` 입니다.

### 10.3. Zero Trust Workload Identity Manager 설치

중요

Zero Trust Workload Identity Manager for Red Hat OpenShift는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

Zero Trust Workload Identity Manager는 기본적으로 OpenShift Container Platform에 설치되지 않습니다. 웹 콘솔 또는 CLI를 사용하여 Zero Trust Workload Identity Manager를 설치할 수 있습니다.

#### 10.3.1.1. 웹 콘솔을 사용하여 Zero Trust Workload Identity Manager 설치

웹 콘솔을 사용하여 Zero Trust Workload Identity Manager를 설치할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

에코시스템 → 소프트웨어 카탈로그 로 이동합니다.

필터 상자에 Zero Trust Workload Identity Manager 를 입력합니다.

Zero Trust Workload Identity Manager 를 선택합니다.

버전 드롭다운 목록에서 Zero Trust Workload Identity Manager 버전을 선택하고 설치를 클릭합니다.

Operator 설치 페이지에서 다음을 수행합니다.

필요한 경우 업데이트 채널을 업데이트합니다. 채널은 기본적으로 Zero Trust Workload Identity Manager의 최신 기술 프리뷰 v0.1 릴리스를 설치하는 tech-preview-v0.1 입니다.

Operator의 설치된 네임스페이스 를 선택합니다. 기본 Operator 네임스페이스는 `zero-trust-workload-identity-manager` 입니다.

`zero-trust-workload-identity-manager` 네임스페이스가 없으면 이를 위해 생성됩니다.

업데이트 승인 전략을 선택합니다.

자동 전략을 사용하면 Operator 새 버전이 준비될 때 OLM(Operator Lifecycle Manager)이 자동으로 Operator를 업데이트할 수 있습니다.

수동 전략을 사용하려면 적절한 자격 증명을 가진 사용자가 Operator 업데이트를 승인해야 합니다.

설치 를 클릭합니다.

검증

Ecosystem → 설치된 Operators 로 이동합니다.

Zero Trust Workload Identity Manager 가 `zero-trust-workload-identity-manager` 네임스페이스에 Succeeded 상태로 나열되어 있는지 확인합니다.

다음 명령을 실행하여 Zero Trust Workload Identity Manager 컨트롤러 관리자 배포가 준비되었는지 확인합니다.

```shell-session
$ oc get deployment -l name=zero-trust-workload-identity-manager -n zero-trust-workload-identity-manager
```

```shell-session
NAME                                                            READY   UP-TO-DATE    AVAILABLE  AGE
zero-trust-workload-identity-manager-controller-manager-6c4djb  1/1     1             1          43m
```

#### 10.3.1.2. CLI를 사용하여 Zero Trust Workload Identity Manager 설치

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 `zero-trust-workload-identity-manager` 라는 새 프로젝트를 생성합니다.

```shell-session
$ oc new-project zero-trust-workload-identity-manager
```

`OperatorGroup` 오브젝트를 생성합니다.

다음 콘텐츠를 사용하여 YAML 파일(예: `operatorGroup.yaml`)을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-zero-trust-workload-identity-manager
  namespace: zero-trust-workload-identity-manager
spec:
  upgradeStrategy: Default
```

다음 명령을 실행하여 `OperatorGroup` 오브젝트를 생성합니다.

```shell-session
$ oc create -f operatorGroup.yaml
```

`Subscription` 오브젝트를 생성합니다.

`Subscription` 오브젝트를 정의하는 YAML 파일(예: `subscription.yaml`)을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-zero-trust-workload-identity-manager
  namespace: zero-trust-workload-identity-manager
spec:
  channel: tech-preview-v0.1
  name: openshift-zero-trust-workload-identity-manager
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
```

다음 명령을 실행하여 서브스크립션 오브젝트를 생성합니다.

```shell-session
$ oc create -f subscription.yaml
```

검증

다음 명령을 실행하여 OLM 서브스크립션이 생성되었는지 확인합니다.

```shell-session
$ oc get subscription -n zero-trust-workload-identity-manager
```

```shell-session
NAME                                             PACKAGE                                SOURCE             CHANNEL
openshift-zero-trust-workload-identity-manager   zero-trust-workload-identity-manager   redhat-operators   tech-preview-v0.1
```

다음 명령을 실행하여 Operator가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get csv -n zero-trust-workload-identity-manager
```

```shell-session
NAME                                         DISPLAY                                VERSION  PHASE
zero-trust-workload-identity-manager.v0.1.0   Zero Trust Workload Identity Manager   0.1.0    Succeeded
```

다음 명령을 실행하여 Zero Trust Workload Identity Manager 컨트롤러 관리자가 준비되었는지 확인합니다.

```shell-session
$ oc get deployment -l name=zero-trust-workload-identity-manager -n zero-trust-workload-identity-manager
```

```shell-session
NAME                                                      READY   UP-TO-DATE   AVAILABLE   AGE
zero-trust-workload-identity-manager-controller-manager   1/1     1            1           43m
```

### 10.4. Zero Trust Workload Identity Manager 피연산자 배포

중요

Zero Trust Workload Identity Manager는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

각 CR(사용자 정의 리소스)을 생성하여 다음 피연산자를 배포할 수 있습니다. 설치에 성공하려면 다음 순서로 피연산자를 배포해야 합니다.

SPIRE 서버

SPIRE 에이전트

SPIFFE CSI 드라이버

SPIRE OIDC 검색 공급자

#### 10.4.1. SPIRE 서버 배포

SPIRE 서버를 배포하고 구성하도록 `SpireServer` CR(사용자 정의 리소스)을 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

클러스터에 Zero Trust Workload Identity Manager를 설치했습니다.

프로세스

`SpireServer` CR을 생성합니다.

`SpireServer` CR을 정의하는 YAML 파일을 생성합니다(예: `SpireServer.yaml`).

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: SpireServer
metadata:
  name: cluster
spec:
  trustDomain: <trust_domain>
  clusterName: <cluster_name>
  caSubject:
    commonName: example.org
    country: "US"
    organization: "RH"
  persistence:
    type: pvc
    size: "5Gi"
    accessMode: ReadWriteOnce
  datastore:
    databaseType: sqlite3
    connectionString: "/run/spire/data/datastore.sqlite3"
    maxOpenConns: 100
    maxIdleConns: 2
    connMaxLifetime: 3600
  jwtIssuer: <jwt_issuer_domain>
```

1. SPIFFE 식별자에 사용할 신뢰 도메인입니다.

2. 클러스터 이름입니다.

3. SPIRE 서버 CA의 일반 이름입니다.

4. SPIRE 서버 CA 국가입니다.

5. SPIRE 서버 CA 조직입니다.

6. 지속성에 사용할 볼륨 유형입니다. 유효한 옵션은 `pvc` 및 `hostPath` 입니다.

7. 지속성에 사용할 볼륨 크기

8. 지속성에 사용할 액세스 모드입니다. 유효한 옵션은 `ReadWriteOnce`, `ReadWriteOncePod` 및 `ReadWriteMany` 입니다.

9. 열려 있는 데이터베이스 연결의 최대 수입니다.

10. 풀의 최대 유휴 연결 수입니다.

11. 연결을 재사용할 수 있는 최대 시간입니다. 무제한 시간을 지정하려면 값을 `0` 으로 설정할 수 있습니다.

12. JSON 웹 토큰(JWT) 발행자 도메인입니다. 값은 유효한 URL이어야 합니다.

다음 명령을 실행하여 구성을 적용합니다.

```shell-session
$ oc apply -f SpireServer.yaml
```

검증

다음 명령을 실행하여 SPIRE Server의 상태 저장 세트가 준비되었으며 사용 가능한지 확인합니다.

```shell-session
$ oc get statefulset -l app.kubernetes.io/name=server -n zero-trust-workload-identity-manager
```

```shell-session
NAME            READY   AGE
spire-server    1/1     65s
```

다음 명령을 실행하여 SPIRE 서버 포드의 상태가 `Running` 인지 확인합니다.

```shell-session
$ oc get po -l app.kubernetes.io/name=server -n zero-trust-workload-identity-manager
```

```shell-session
NAME               READY   STATUS    RESTARTS        AGE
spire-server-0     2/2     Running   1 (108s ago)    111s
```

다음 명령을 실행하여 PVC(영구 볼륨 클레임)가 바인딩되었는지 확인합니다.

```shell-session
$ oc get pvc -l app.kubernetes.io/name=server -n zero-trust-workload-identity-manager
```

```shell-session
NAME                        STATUS    VOLUME                                     CAPACITY   ACCESS MODES  STORAGECLASS  VOLUMEATTRIBUTECLASS  AGE
spire-data-spire-server-0   Bound     pvc-27a36535-18a1-4fde-ab6d-e7ee7d3c2744   5Gi        RW0           gp3-csi       <unset>               22m
```

#### 10.4.2. SPIRE 에이전트 배포

SPIRE 에이전트를 배포하고 구성하도록 `SpireAgent` CR(사용자 정의 리소스)을 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

클러스터에 Zero Trust Workload Identity Manager를 설치했습니다.

프로세스

`SpireAgent` CR을 생성합니다.

`SpireAgent` CR을 정의하는 YAML 파일을 생성합니다(예: `SpireAgent.yaml`).

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: SpireAgent
metadata:
  name: cluster
spec:
  trustDomain: <trust_domain>
  clusterName: <cluster_name>
  nodeAttestor:
    k8sPSATEnabled: "true"
  workloadAttestors:
    k8sEnabled: "true"
    workloadAttestorsVerification:
      type: "auto"
```

1. SPIFFE 식별자에 사용할 신뢰 도메인입니다.

2. 클러스터 이름입니다.

3. PSAT(projected service account token) Kubernetes 노드를 활성화하거나 비활성화합니다. 유효한 옵션은 `true` 및 `false` 입니다.

4. Kubernetes 워크로드 attestor를 활성화하거나 비활성화합니다. 유효한 옵션은 `true` 및 `false` 입니다.

5. kubelet에 대해 수행할 확인 유형입니다. 유효한 옵션은 `auto`, `hostCert`, `apiServerCA`, `skip` 입니다. `auto` 옵션은 처음에 `hostCert` 를 사용하려고 시도한 다음 `apiServerCA` 로 대체됩니다.

다음 명령을 실행하여 구성을 적용합니다.

```shell-session
$ oc apply -f SpireAgent.yaml
```

검증

다음 명령을 실행하여 SPIRE 에이전트의 데몬 세트가 준비되고 사용 가능한지 확인합니다.

```shell-session
$ oc get daemonset -l app.kubernetes.io/name=agent -n zero-trust-workload-identity-manager
```

```shell-session
NAME          DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
spire-agent   3         3         3       3            3           <none>          10m
```

다음 명령을 실행하여 SPIRE 에이전트 Pod의 상태가 `Running` 인지 확인합니다.

```shell-session
$ oc get po -l app.kubernetes.io/name=agent -n zero-trust-workload-identity-manager
```

```shell-session
NAME                READY   STATUS    RESTARTS   AGE
spire-agent-dp4jb   1/1     Running   0          12m
spire-agent-nvwjm   1/1     Running   0          12m
spire-agent-vtvlk   1/1     Running   0          12m
```

#### 10.4.3. SPIFFE 컨테이너 스토리지 인터페이스 드라이버 배포

SPIFFE CSI(Container Storage Interface) 드라이버를 배포하고 구성하도록 `SpiffeCSIDriver` 사용자 정의 리소스(CR)를 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

클러스터에 Zero Trust Workload Identity Manager를 설치했습니다.

프로세스

`SpiffeCSIDriver` CR을 생성합니다.

`SpiffeCSIDriver` CR 오브젝트를 정의하는 YAML 파일을 생성합니다(예: `SpiffeCSIDriver.yaml`).

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: SpiffeCSIDriver
metadata:
  name: cluster
spec:
  agentSocketPath: '/run/spire/agent-sockets/spire-agent.sock'
```

1. SPIRE 에이전트의 UNIX 소켓 경로입니다.

다음 명령을 실행하여 구성을 적용합니다.

```shell-session
$ oc apply -f SpiffeCSIDriver.yaml
```

검증

다음 명령을 실행하여 SPIFFE CSI 드라이버의 데몬 세트가 준비되고 사용 가능한지 확인합니다.

```shell-session
$ oc get daemonset -l app.kubernetes.io/name=spiffe-csi-driver -n zero-trust-workload-identity-manager
```

```shell-session
NAME                      DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
spire-spiffe-csi-driver   3         3         3       3            3           <none>          114s
```

다음 명령을 실행하여 SPIFFE CSI(Container Storage Interface) 드라이버 Pod의 상태가 실행 중인지 확인합니다.

```shell-session
$ oc get po -l app.kubernetes.io/name=spiffe-csi-driver -n zero-trust-workload-identity-manager
```

```shell-session
NAME                            READY   STATUS    RESTARTS   AGE
spire-spiffe-csi-driver-gpwcp   2/2     Running   0          2m37s
spire-spiffe-csi-driver-rrbrd   2/2     Running   0          2m37s
spire-spiffe-csi-driver-w6s6q   2/2     Running   0          2m37s
```

#### 10.4.4. SPIRE OpenID Connect 검색 공급자 배포

`OIDCDiscoveryProvider` CR(사용자 정의 리소스)을 구성하고 OIDC(OpenID Connect) 검색 공급자를 구성하고 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

클러스터에 Zero Trust Workload Identity Manager를 설치했습니다.

프로세스

`SpireOIDCDiscoveryProvider` CR을 생성합니다.

`SpireOIDCDiscoveryProvider` CR을 정의하는 YAML 파일을 생성합니다(예: `SpireOIDCDiscoveryProvider.yaml`).

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: SpireOIDCDiscoveryProvider
metadata:
  name: cluster
spec:
  trustDomain: <trust_domain>
  agentSocketName: 'spire-agent.sock'
  jwtIssuer: <jwt_issuer_domain>
```

1. SPIFFE 식별자에 사용할 신뢰 도메인입니다.

2. SPIRE 에이전트 UNIX 소켓의 이름입니다.

3. JSON 웹 토큰(JWT) 발행자 도메인입니다. 값은 유효한 URL이어야 합니다.

다음 명령을 실행하여 구성을 적용합니다.

```shell-session
$ oc apply -f SpireOIDCDiscoveryProvider.yaml
```

검증

다음 명령을 실행하여 OIDC 검색 공급자의 배포가 준비되고 사용 가능한지 확인합니다.

```shell-session
$ oc get deployment -l app.kubernetes.io/name=spiffe-oidc-discovery-provider -n zero-trust-workload-identity-manager
```

```shell-session
NAME                                    READY  UP-TO-DATE  AVAILABLE  AGE
spire-spiffe-oidc-discovery-provider    1/1    1           1          2m58s
```

다음 명령을 실행하여 OIDC 검색 공급자 Pod의 상태가 `Running` 인지 확인합니다.

```shell-session
$ oc get po -l app.kubernetes.io/name=spiffe-oidc-discovery-provider -n zero-trust-workload-identity-manager
```

```shell-session
NAME                                                    READY   STATUS    RESTARTS   AGE
spire-spiffe-oidc-discovery-provider-64586d599f-lcc94   2/2     Running   0          7m15s
```

### 10.5. 제로 트러스트 워크로드 ID 관리자 OIDC 페더레이션

Zero Trust Workload Identity Manager는 SPIRE 서버가 OIDC 공급자 역할을 할 수 있도록 하여 OpenID Connect(OIDC)와 통합됩니다. 이를 통해 워크로드는 로컬 SPIRE 에이전트에서 확인할 수 있는 JSON 웹 토큰 - SPIFFE 확인 가능한 ID 문서(JWT-SVID)를 요청하고 수신할 수 있습니다. 클라우드 공급자와 같은 외부 시스템은 SPIRE 서버에서 노출하는 OIDC 검색 끝점을 사용하여 공개 키를 검색할 수 있습니다.

중요

Zero Trust Workload Identity Manager for Red Hat OpenShift는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

다음 공급자는 SPIRE OIDC 페더레이션과 함께 작동하는 것으로 확인됩니다.

Azure Entra ID

Vault

#### 10.5.1. Entra ID OpenID Connect 정보

Entra ID는 사용자 관리 및 액세스 제어를 중앙 집중화하는 클라우드 기반 ID 및 액세스 관리 서비스입니다. Entra ID는 ID 공급자 역할을 하며, 애플리케이션에 대한 사용자 ID 및 발행 및 ID 토큰을 확인합니다. 이 토큰에는 필수 사용자 정보가 있어 애플리케이션이 사용자 자격 증명을 관리하지 않고 사용자를 확인할 수 있습니다.

OIDC(Entra ID OpenID Connect)를 SPIRE와 통합하면 워크로드에서 수명이 짧은 자동 암호화 ID를 제공합니다. SPIRE-issued ID는 정적 보안 없이 서비스를 안전하게 인증하기 위해 Entra ID로 전송됩니다.

#### 10.5.1.1. 관리형 OIDC 검색 공급자 경로에 대한 외부 인증서 구성

관리형 경로는 외부 경로 인증서 기능을 사용하여 `tls.externalCertificate` 필드를 외부적으로 관리되는 TLS(전송 계층 보안) 보안 이름으로 설정합니다.

사전 요구 사항

Zero Trust Workload Identity Manager 0.2.0 이상을 설치했습니다.

클러스터에 SPIRE 에이전트, SPIFFEE CSI Driver 및 SPIRE OIDC 검색 공급자 피연산자를 배포했습니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다. 자세한 내용은 cert-manager Operator for Red Hat OpenShift를 설치합니다.

공개적으로 신뢰할 수 있는 CA 서비스로 구성된 `Cluster Issuer` 또는 Issuer를 생성했습니다. 예를 들어 자동화된 인증서 관리 환경(ACME)은 "Let's Encrypt ACME" 서비스가 있는 `발급` 자를 입력합니다. 자세한 내용은 ACME 발행자 구성을 참조하십시오.

프로세스

다음 명령을 실행하여 참조된 시크릿을 읽을 수 있는 라우터 서비스 계정 권한을 제공하는 `역할을` 생성합니다.

```shell-session
$ oc create role secret-reader \
  --verb=get,list,watch \
  --resource=secrets \
  --resource-name=$TLS_SECRET_NAME \
  -n zero-trust-workload-identity-manager
```

다음 명령을 실행하여 라우터 서비스 계정을 새로 생성된 Role 리소스와 바인딩할 `RoleBinding` 리소스를 생성합니다.

```shell-session
$ oc create rolebinding secret-reader-binding \
  --role=secret-reader \
  --serviceaccount=openshift-ingress:router \
  -n zero-trust-workload-identity-manager
```

다음 명령을 실행하여 이전 단계에서 생성된 보안을 참조하도록 `SpireOIDCDIscoveryProvider` CR(사용자 정의 리소스) 오브젝트를 구성합니다.

```shell-session
$ oc patch SpireOIDCDiscoveryProvider cluster --type=merge -p='
spec:
  externalSecretRef: ${TLS_SECRET_NAME}
'
```

검증

`SpireOIDCDiscoveryProvider` CR에서 다음 명령을 실행하여 `ManageRouteReady` 조건이 `True` 로 설정되어 있는지 확인합니다.

```shell-session
$ oc wait --for=jsonpath='{.status.conditions[?(@.type=="ManagedRouteReady")].status}'=True SpireOIDCDiscoveryProvider/cluster --timeout=120s
```

다음 명령을 실행하여 HTTPS를 통해 OIDC 엔드포인트에 안전하게 액세스할 수 있는지 확인합니다.

```shell-session
$ curl https://$JWT_ISSUER_ENDPOINT/.well-known/openid-configuration

{
  "issuer": "https://$JWT_ISSUER_ENDPOINT",
  "jwks_uri": "https://$JWT_ISSUER_ENDPOINT/keys",
  "authorization_endpoint": "",
  "response_types_supported": [
    "id_token"
  ],
  "subject_types_supported": [],
  "id_token_signing_alg_values_supported": [
    "RS256",
    "ES256",
    "ES384"
  ]
}%
```

#### 10.5.1.2. 관리형 경로 비활성화

OIDC 검색 공급자 서비스 노출 동작을 완전히 제어하려면 요구 사항에 따라 관리 경로를 비활성화할 수 있습니다.

프로세스

OIDC 검색 공급자를 수동으로 구성하려면 다음 명령을 실행하여 `managedRoute` 를 `false` 로 설정합니다.

```shell-session
$ oc patch SpireOIDCDiscoveryProvider cluster --type=merge -p='
spec:
  managedRoute: "false"
```

#### 10.5.1.3. Microsoft Azure에서 Entra ID 사용

Entra ID 구성이 완료되면 Azure에서 작동하도록 Entra ID를 설정할 수 있습니다.

사전 요구 사항

공개적으로 신뢰할 수 있는 CA에서 TLS 인증서를 제공하도록 SPIRE OIDC 검색 공급자 경로를 구성했습니다.

프로세스

다음 명령을 실행하여 Azure에 로그인합니다.

```shell-session
$ az login
```

다음 명령을 실행하여 Azure 서브스크립션 및 테넌트의 변수를 구성합니다.

```shell-session
$ export SUBSCRIPTION_ID=$(az account list --query "[?isDefault].id" -o tsv)
```

```shell-session
$ export TENANT_ID=$(az account list --query "[?isDefault].tenantId" -o tsv)
```

```shell-session
$ export LOCATION=centralus
```

1. 고유 서브스크립션 식별자입니다.

1. Azure Active Directory 인스턴스의 ID입니다.

1. 리소스가 생성된 Azure 리전입니다.

다음 명령을 실행하여 리소스 변수 이름을 정의합니다.

```shell-session
$ export NAME=ztwim
```

```shell-session
$ export RESOURCE_GROUP="${NAME}-rg"
```

```shell-session
$ export STORAGE_ACCOUNT="${NAME}storage"
```

```shell-session
$ export STORAGE_CONTAINER="${NAME}storagecontainer"
```

```shell-session
$ export USER_ASSIGNED_IDENTITY_NAME="${NAME}-identity"
```

1. 모든 리소스의 기본 이름입니다.

1. 리소스 그룹의 이름입니다.

1. 스토리지 계정의 이름입니다.

1. 스토리지 컨테이너의 이름입니다.

1. 관리 ID의 이름입니다.

다음 명령을 실행하여 리소스 그룹을 생성합니다.

```shell-session
$ az group create \
  --name "${RESOURCE_GROUP}" \
  --location "${LOCATION}"
```

#### 10.5.1.4. Azure Blob 스토리지 구성

콘텐츠를 저장하는 데 사용할 새 스토리지 계정을 생성해야 합니다.

프로세스

다음 명령을 실행하여 콘텐츠를 저장하는 데 사용되는 새 스토리지 계정을 생성합니다.

```shell-session
$ az storage account create \
  --name ${STORAGE_ACCOUNT} \
  --resource-group ${RESOURCE_GROUP} \
  --location ${LOCATION} \
  --encryption-services blob
```

다음 명령을 실행하여 새로 생성된 스토리지 계정의 스토리지 ID를 가져옵니다.

```shell-session
$ export STORAGE_ACCOUNT_ID=$(az storage account show -n ${STORAGE_ACCOUNT} -g ${RESOURCE_GROUP} --query id --out tsv)
```

다음 명령을 실행하여 Blob 스토리지를 지원할 위치를 제공하기 위해 새로 생성된 스토리지 계정 내에 스토리지 컨테이너를 생성합니다.

```shell-session
$ az storage container create \
  --account-name ${STORAGE_ACCOUNT} \
  --name ${STORAGE_CONTAINER} \
  --auth-mode login
```

#### 10.5.1.5. Azure 사용자 관리 ID 구성

새 사용자 관리 ID를 만든 다음 사용자 관리 ID와 연결된 관련 서비스 주체의 클라이언트 ID를 가져와야 합니다.

프로세스

새 사용자 관리 ID를 만든 다음 다음 명령을 실행하여 사용자 관리 ID와 연결된 관련 서비스 주체의 클라이언트 ID를 가져옵니다.

```shell-session
$ az identity create \
  --name ${USER_ASSIGNED_IDENTITY_NAME} \
  --resource-group ${RESOURCE_GROUP}
```

```shell-session
$ export IDENTITY_CLIENT_ID=$(az identity show --resource-group "${RESOURCE_GROUP}" --name "${USER_ASSIGNED_IDENTITY_NAME}" --query 'clientId' -otsv)
```

다음 명령을 실행하여 Azure 사용자가 할당한 관리 ID의 `CLIENT_ID` 를 검색하고 환경 변수로 저장합니다.

```shell-session
$ export IDENTITY_CLIENT_ID=$(az identity show --resource-group "${RESOURCE_GROUP}" --name "${USER_ASSIGNED_IDENTITY_NAME}" --query 'clientId' -otsv)
```

다음 명령을 실행하여 역할을 사용자 관리 ID와 연결된 서비스 주체와 연결합니다.

```shell-session
$ az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee "${IDENTITY_CLIENT_ID}" \
  --scope ${STORAGE_ACCOUNT_ID}
```

#### 10.5.1.6. 데모 애플리케이션 생성

데모 애플리케이션은 전체 시스템이 작동하는지 확인하는 방법을 제공합니다.

프로세스

데모 애플리케이션을 생성하려면 다음 단계를 완료합니다.

다음 명령을 실행하여 애플리케이션 이름과 네임스페이스를 설정합니다.

```shell-session
$ export APP_NAME=workload-app
```

```shell-session
$ export APP_NAMESPACE=demo
```

다음 명령을 실행하여 네임스페이스를 생성합니다.

```shell-session
$ oc create namespace $APP_NAMESPACE
```

다음 명령을 실행하여 애플리케이션 시크릿을 생성합니다.

```shell-session
$ oc apply -f - << EOF
apiVersion: v1
kind: Secret
metadata:
  name: $APP_NAME
  namespace: $APP_NAMESPACE
stringData:
  AAD_AUTHORITY: https://login.microsoftonline.com/
  AZURE_AUDIENCE: "api://AzureADTokenExchange"
  AZURE_TENANT_ID: "${TENANT_ID}"
  AZURE_CLIENT_ID: "${IDENTITY_CLIENT_ID}"
  BLOB_STORE_ACCOUNT: "${STORAGE_ACCOUNT}"
  BLOB_STORE_CONTAINER: "${STORAGE_CONTAINER}"
EOF
```

#### 10.5.1.7. 워크로드 애플리케이션 배포

데모 애플리케이션이 생성되면.

사전 요구 사항

데모 애플리케이션이 생성되어 배포되었습니다.

프로세스

애플리케이션을 배포하려면 제공된 전체 명령 블록을 복사하여 터미널에 직접 붙여넣습니다. Enter 를 누릅니다.

```shell-session
$ oc apply -f - << EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: $APP_NAME
  namespace: $APP_NAMESPACE
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: $APP_NAME
  namespace: $APP_NAMESPACE
spec:
  selector:
    matchLabels:
      app: $APP_NAME
  template:
    metadata:
      labels:
        app: $APP_NAME
        deployment: $APP_NAME
    spec:
      serviceAccountName: $APP_NAME
      containers:
        - name: $APP_NAME
          image: "registry.redhat.io/ubi9/python-311:latest"
          command:
            - /bin/bash
            - "-c"
            - |
              #!/bin/bash
              pip install spiffe azure-cli

              cat << EOF > /opt/app-root/src/get-spiffe-token.py
              #!/opt/app-root/bin/python
              from spiffe import JwtSource
              import argparse
              parser = argparse.ArgumentParser(description='Retrieve SPIFFE Token.')
              parser.add_argument("-a", "--audience", help="The audience to include in the token", required=True)
              args = parser.parse_args()
              with JwtSource() as source:
                jwt_svid = source.fetch_svid(audience={args.audience})
                print(jwt_svid.token)
              EOF

              chmod +x /opt/app-root/src/get-spiffe-token.py
              while true; do sleep 10; done
          envFrom:
          - secretRef:
              name: $APP_NAME
          env:
            - name: SPIFFE_ENDPOINT_SOCKET
              value: unix:///run/spire/sockets/spire-agent.sock
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
            readOnlyRootFilesystem: false
            runAsNonRoot: true
            seccompProfile:
              type: RuntimeDefault
          ports:
            - containerPort: 8080
              protocol: TCP
          volumeMounts:
            - name: spiffe-workload-api
              mountPath: /run/spire/sockets
              readOnly: true
      volumes:
        - name: spiffe-workload-api
          csi:
            driver: csi.spiffe.io
            readOnly: true
EOF
```

검증

다음 명령을 실행하여 `workload-app` Pod가 성공적으로 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n $APP_NAMESPACE
```

```shell-session
NAME                             READY     STATUS      RESTARTS      AGE
workload-app-5f8b9d685b-abcde    1/1       Running     0             60s
```

SPIFFE JWT 토큰(SVID-JWT)을 검색합니다.

다음 명령을 실행하여 Pod 이름을 동적으로 가져옵니다.

```shell-session
$ POD_NAME=$(oc get pods -n $APP_NAMESPACE -l app=$APP_NAME -o jsonpath='{.items[0].metadata.name}')
```

다음 명령을 실행하여 Pod 내에서 스크립트를 실행합니다.

```shell-session
$ oc exec -it $POD_NAME -n $APP_NAMESPACE -- \
  /opt/app-root/src/get-spiffe-token.py -a "api://AzureADTokenExchange"
```

#### 10.5.1.8. SPIFFE ID 페더레이션을 사용하여 Azure 구성

SPIFFE ID 페더레이션을 사용하여 Azure를 구성하여 데모 애플리케이션에 대한 암호 없이 자동화된 인증을 활성화할 수 있습니다.

프로세스

다음 명령을 실행하여 사용자 관리 ID와 워크로드 애플리케이션과 관련된 SPIFFE ID 간의 ID를 통합합니다.

```shell-session
$ az identity federated-credential create \
 --name ${NAME} \
 --identity-name ${USER_ASSIGNED_IDENTITY_NAME} \
 --resource-group ${RESOURCE_GROUP} \
 --issuer https://$JWT_ISSUER_ENDPOINT \
 --subject spiffe://$APP_DOMAIN/ns/$APP_NAMESPACE/sa/$APP_NAME \
 --audience api://AzureADTokenExchange
```

#### 10.5.1.9. 애플리케이션 워크로드가 Azure Blob Storage의 콘텐츠에 액세스할 수 있는지 확인

애플리케이션 워크로드가 Azure Blob Storage에 액세스할 수 있는지 확인할 수 있습니다.

사전 요구 사항

Azure Blob 스토리지가 생성되었습니다.

프로세스

다음 명령을 실행하여 SPIFFE Workload API에서 JWT 토큰을 검색합니다.

```shell-session
$ oc rsh -n $APP_NAMESPACE deployment/$APP_NAME
```

다음 명령을 실행하여 `TOKEN` 이라는 환경 변수를 생성하고 내보냅니다.

```shell-session
$ export TOKEN=$(/opt/app-root/src/get-spiffe-token.py --audience=$AZURE_AUDIENCE)
```

다음 명령을 실행하여 Pod에 포함된 Azure CLI에 로그인합니다.

```shell-session
$ az login --service-principal \
  -t ${AZURE_TENANT_ID} \
  -u ${AZURE_CLIENT_ID} \
  --federated-token ${TOKEN}
```

다음 명령을 실행하여 애플리케이션 워크로드 Pod를 사용하여 새 파일을 생성하고 Blob Storage에 파일을 업로드합니다.

```shell-session
$ echo “Hello from OpenShift” > openshift-spire-federated-identities.txt
```

다음 명령을 실행하여 Azure 블로그 스토리지에 파일을 업로드합니다.

```shell-session
$ az storage blob upload \
  --account-name ${BLOB_STORE_ACCOUNT} \
  --container-name ${BLOB_STORE_CONTAINER} \
  --name openshift-spire-federated-identities.txt \
  --file openshift-spire-federated-identities.txt \
  --auth-mode login
```

검증

다음 명령을 실행하여 포함된 파일을 나열하여 파일이 업로드되었는지 확인합니다.

```shell-session
$ az storage blob list \
  --account-name ${BLOB_STORE_ACCOUNT} \
  --container-name ${BLOB_STORE_CONTAINER} \
  --auth-mode login \
  -o table
```

#### 10.5.2. Vault OpenID Connect 정보

SPIRE를 사용하는 Vault OpenID Connect(OIDC)는 Vault에서 신뢰할 수 있는 OIDC 공급자로 SPIRE를 사용하는 보안 인증 방법을 생성합니다. 워크로드는 고유한 SPIFFE ID가 있는 로컬 SPIRE 에이전트에서 JWT-SVID를 요청합니다. 그러면 워크로드가 이 토큰을 Vault에 표시하고 Vault는 SPIRE 서버의 공개 키에 대해 유효성을 검사합니다. 모든 조건이 충족되면 Vault는 워크로드에서 시크릿에 액세스하고 Vault 내에서 작업을 수행하는 데 사용할 수 있는 워크로드에 수명이 짧은 Vault 토큰을 발행합니다.

#### 10.5.2.1. Vault 설치

Vault를 OIDC로 사용하려면 Vault를 설치해야 합니다.

사전 요구 사항

경로를 구성합니다. 자세한 내용은 경로 구성 을 참조하십시오.

Helm이 설치되어 있어야 합니다.

Vault API에서 출력을 쉽게 읽을 수 있는 명령줄 JSON 프로세서입니다.

HashiCorp Helm 리포지토리가 추가되었습니다.

프로세스

`vault-helm-value.yaml` 파일을 생성합니다.

```yaml
global:
  enabled: true
  openshift: true
  tlsDisable: true
injector:
  enabled: false
server:
  ui:
    enabled: true
  image:
    repository: docker.io/hashicorp/vault
    tag: "1.19.0"
  dataStorage:
    enabled: true
    size: 1Gi
  standalone:
    enabled: true
    config: |
      listener "tcp" {
        tls_disable = 1
        address = "[::]:8200"
        cluster_address = "[::]:8201"
      }
      storage "file" {
        path = "/vault/data"
      }
  extraEnvironmentVars: {}
```

1. OpenShift 관련 보안 컨텍스트에 대한 배포를 최적화합니다.

2. 차트로 생성된 Kubernetes 오브젝트의 TLS를 비활성화합니다.

3. Vault 데이터를 저장할 1Gi 영구 볼륨을 생성합니다.

4. 단일 Vault Pod를 배포합니다.

5. Vault 서버에 TLS를 사용하지 않도록 지시합니다.

아래 명령을 실행합니다.

```shell
helm install
```

```shell-session
$ helm install vault hashicorp/vault \
  --create-namespace -n vault \
  --values ./vault-helm-value.yaml
```

다음 명령을 실행하여 Vault 서비스를 노출합니다.

```shell-session
$ oc expose service vault -n vault
```

`VAULT_ADDR` 환경 변수를 설정하여 새 경로에서 호스트 이름을 검색한 다음 다음 명령을 실행하여 내보냅니다.

```shell-session
$ export VAULT_ADDR="http://$(oc get route vault -n vault -o jsonpath='{.spec.host}')"
```

참고

TLS가 비활성화되어 있기 때문에 HTTP `://` 가 앞에 추가됩니다.

검증

Vault 인스턴스가 실행 중인지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ curl -s $VAULT_ADDR/v1/sys/health | jq
```

```plaintext
{
  "initialized": true,
  "sealed": true,
  "standby": true,
  "performance_standby": false,
  "replication_performance_mode": "disabled",
  "replication_dr_mode": "disabled",
  "server_time_utc": 1663786574,
  "version": "1.19.0",
  "cluster_name": "vault-cluster-a1b2c3d4",
  "cluster_id": "5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b"
}
```

#### 10.5.2.2. Vault 초기화 및 삭제

새로 설치된 Vault가 봉인됩니다. 즉, 다른 모든 암호화 키를 보호하는 기본 암호화 키가 시작 시 서버 메모리에 로드되지 않습니다. 자격 증명을 해제하려면 Vault를 초기화해야 합니다.

Vault 서버를 초기화하는 단계는 다음과 같습니다.

Vault 초기화 및 해제

KV(key-value) 시크릿 엔진을 활성화하고 테스트 시크릿을 저장합니다.

SPIRE를 사용하여 JSON 웹 토큰(JWT) 인증 구성

데모 애플리케이션 배포

시크릿 인증 및 검색

사전 요구 사항

Vault가 실행 중인지 확인합니다.

Vault가 초기화되지 않았는지 확인합니다. Vault 서버를 한 번만 초기화할 수 있습니다.

프로세스

다음 명령을 실행하여 `vault` Pod에 대한 원격 쉘을 엽니다.

```shell-session
$ oc rsh -n vault statefulset/vault
```

다음 명령을 실행하여 Vault를 초기화하여 unseal 키 및 root 토큰을 가져옵니다.

```shell-session
$ vault operator init -key-shares=1 -key-threshold=1 -format=json
```

다음 명령을 실행하여 이전 명령에서 받은 unseal 키 및 root 토큰을 내보냅니다.

```shell-session
$ export UNSEAL_KEY=<Your-Unseal-Key>
```

```shell-session
$ export ROOT_TOKEN=<Your-Root-Token>
```

다음 명령을 실행하여 unseal 키를 사용하여 Vault를 봉인 해제합니다.

```shell-session
$ vault operator unseal -format=json $UNSEAL_KEY
```

`exit` 를 입력하여 Pod를 종료합니다.

검증

Vault Pod가 준비되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pod -n vault
```

```shell-session
NAME        READY        STATUS      RESTARTS     AGE
vault-0     1/1          Running     0            65d
```

#### 10.5.2.3. 키-값 시크릿 엔진 활성화 및 테스트 시크릿 저장

키-값 시크릿 엔진을 활성화하여 인증 정보를 관리하기 위한 안전하고 중앙 집중식 위치를 설정할 수 있습니다.

사전 요구 사항

Vault가 초기화되고 봉인 해제되었는지 확인합니다.

프로세스

다음 명령을 실행하여 `Vault` Pod에서 다른 쉘 세션을 엽니다.

```shell-session
$ oc rsh -n vault statefulset/vault
```

이 새 세션 내에서 root 토큰을 다시 내보내고 다음 명령을 실행하여 로그인합니다.

```shell-session
$ export ROOT_TOKEN=<Your-Root-Token>
```

```shell-session
$ vault login "${ROOT_TOKEN}"
```

시크릿 `/ 경로에서 KV 시크릿` 엔진을 활성화하고 다음 명령을 실행하여 테스트 시크릿을 생성합니다.

```shell-session
$ export NAME=ztwim
```

```shell-session
$ vault secrets enable -path=secret kv
```

```shell-session
$ vault kv put secret/$NAME version=v0.1.0
```

검증

보안이 올바르게 저장되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ vault kv get secret/$NAME
```

#### 10.5.2.4. SPIRE를 사용하여 JSON 웹 토큰 인증 구성

애플리케이션이 SPIFFE ID를 사용하여 Vault에 안전하게 로그인할 수 있도록 JSON 웹 토큰(JWT) 인증을 설정해야 합니다.

사전 요구 사항

Vault가 초기화되고 봉인 해제되었는지 확인합니다.

테스트 보안이 키-값 시크릿 엔진에 저장되어 있는지 확인합니다.

프로세스

로컬 시스템에서 SPIRE 인증 기관(CA) 번들을 검색하여 다음 명령을 실행하여 파일에 저장합니다.

```shell-session
$ oc get cm -n zero-trust-workload-identity-manager spire-bundle -o jsonpath='{ .data.bundle\.crt }' > oidc_provider_ca.pem
```

Vault Pod 쉘로 돌아가 임시 파일을 생성하고 다음 명령을 실행하여 `oidc_provider_ca.pem` 의 내용을 붙여 넣습니다.

```shell-session
$ cat << EOF > /tmp/oidc_provider_ca.pem
-----BEGIN CERTIFICATE-----
<Paste-Your-Certificate-Content-Here>
-----END CERTIFICATE-----
EOF
```

다음 명령을 실행하여 JWT 구성에 필요한 환경 변수를 설정합니다.

```shell-session
$ export APP_DOMAIN=<Your-App-Domain>
```

```shell-session
$ export JWT_ISSUER_ENDPOINT="oidc-discovery.$APP_DOMAIN"
```

```shell-session
$ export OIDC_URL="https://$JWT_ISSUER_ENDPOINT"
```

```shell-session
$ export OIDC_CA_PEM="$(cat /tmp/oidc_provider_ca.pem)"
```

다음 명령을 실행하여 새 환경 변수를 인용합니다.

```shell-session
$ export ROLE="${NAME}-role"
```

다음 명령을 실행하여 JWT 인증 방법을 활성화합니다.

```shell-session
$ vault auth enable jwt
```

다음 명령을 실행하여 ODIC 인증 방법을 구성합니다.

```shell-session
$ vault write auth/jwt/config \
  oidc_discovery_url=$OIDC_URL \
  oidc_discovery_ca_pem="$OIDC_CA_PEM" \
  default_role=$ROLE
```

다음 명령을 실행하여 `ztwim-policy` 라는 정책을 생성합니다.

```shell-session
$ export POLICY="${NAME}-policy"
```

다음 명령을 실행하여 이전에 생성한 시크릿에 대한 읽기 액세스 권한을 부여합니다.

```shell-session
$ vault policy write $POLICY -<<EOF
path "secret/$NAME" {
    capabilities = ["read"]
}
EOF
```

다음 명령을 실행하여 다음 환경 변수를 생성합니다.

```shell-session
$ export APP_NAME=client
```

```shell-session
$ export APP_NAMESPACE=demo
```

```shell-session
$ export AUDIENCE=$APP_NAME
```

다음 명령을 실행하여 특정 SPIFFE ID를 사용하여 정책을 워크로드에 바인딩하는 JWT 역할을 생성합니다.

```shell-session
$ vault write auth/jwt/role/$ROLE -<<EOF
{
  "role_type": "jwt",
  "user_claim": "sub",
  "bound_audiences": "$AUDIENCE",
  "bound_claims_type": "glob",
  "bound_claims": {
    "sub": "spiffe://$APP_DOMAIN/ns/$APP_NAMESPACE/sa/$APP_NAME"
  },
  "token_ttl": "24h",
  "token_policies": "$POLICY"
}
EOF
```

#### 10.5.2.5. 데모 애플리케이션 배포

데모 애플리케이션을 배포할 때 SPIFFE ID를 사용하여 Vault로 인증하는 간단한 클라이언트 애플리케이션을 생성합니다.

프로세스

로컬 시스템에서 다음 명령을 실행하여 애플리케이션의 환경 변수를 설정합니다.

```shell-session
$ export APP_NAME=client
```

```shell-session
$ export APP_NAMESPACE=demo
```

```shell-session
$ export AUDIENCE=$APP_NAME
```

다음 명령을 실행하여 데모 앱에 대한 네임스페이스, 서비스 계정 및 배포를 생성하려면 Kubernetes 매니페스트를 적용합니다. 이 배포는 SPIFFE CSI 드라이버 소켓을 마운트합니다.

```shell-session
$ oc apply -f - <<EOF
# ... (paste the full YAML from your provided code here) ...
EOF
```

검증

다음 명령을 실행하여 클라이언트 배포가 준비되었는지 확인합니다.

```shell-session
$ oc get deploy -n $APP_NAMESPACE
```

```shell-session
NAME             READY        UP-TO-DATE      AVAILABLE     AGE
frontend-app     2/2          2               2             120d
backend-api      3/3          3               3             120d
```

#### 10.5.2.6. 보안 인증 및 검색

데모 애플리케이션을 사용하여 SPIFFE Workload API에서 JWT 토큰을 가져와서 이를 사용하여 Vault에 로그인하고 시크릿을 검색합니다.

프로세스

실행 중인 클라이언트 Pod 내에서 다음 명령을 실행하여 JWT-SVID를 가져옵니다.

```shell-session
$ oc -n $APP_NAMESPACE exec -it $(oc get pod -o=jsonpath='{.items[*].metadata.name}' -l app=$APP_NAME -n $APP_NAMESPACE) \
  -- /opt/spire/bin/spire-agent api fetch jwt \
  -socketPath /run/spire/sockets/spire-agent.sock \
  -audience $AUDIENCE
```

출력에서 토큰을 복사하고 다음 명령을 실행하여 로컬 머신의 환경 변수로 내보냅니다.

```shell-session
$ export IDENTITY_TOKEN=<Your-JWT-Token>
```

다음 명령을 실행하여 새 환경 변수를 인용합니다.

```shell-session
$ export ROLE="${NAME}-role"
```

다음 명령을 실행하여 Vault 클라이언트 토큰을 가져오려면 다음 명령을 사용하여 JWT 토큰을 Vault 로그인 엔드포인트로 보냅니다.

```shell
curl
```

```shell-session
$ VAULT_TOKEN=$(curl -s --request POST --data '{ "jwt": "'"${IDENTITY_TOKEN}"'", "role": "'"${ROLE}"'"}' "${VAULT_ADDR}"/v1/auth/jwt/login | jq -r '.auth.client_token')
```

검증

다음 명령을 실행하여 새로 구입한 Vault 토큰을 사용하여 KV 저장소에서 시크릿을 읽습니다.

```shell-session
$ curl -s -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/$NAME | jq
```

출력에 시크릿의 콘텐츠(`"version": "v0.1.0"`)가 표시되어 전체 워크플로우가 성공했는지 확인해야 합니다.

### 10.6. Zero Trust Workload Identity Manager에 대해 create-only 모드 활성화

`생성 전용` 모드를 활성화하면 Operator 조정을 일시 중지하여 컨트롤러에서 변경 사항을 덮어쓰지 않고 수동 구성 또는 디버그를 수행할 수 있습니다. 이 작업은 Operator에서 관리하는 API 리소스에 주석을 달아 수행됩니다. 다음 시나리오는 `create-only` 모드가 사용 가능한 경우의 예입니다.

수동 사용자 지정 필수: Operator의 기본값과 다른 특정 구성으로 operator 관리 리소스(ConfigMaps, Deployments, DaemonSet 등)를 사용자 지정해야 합니다.

2일 차 작업: 초기 배포 후 Operator가 후속 조정 주기 동안 수동 변경 사항을 덮어쓰지 않도록 하려는 경우

Configuration Drift Prevention: Operator의 라이프사이클 관리의 이점을 계속 활용하면서 특정 리소스 구성을 제어하려는 경우

#### 10.6.1. 주석별 Operator 조정 일시 중지

주석 조정은 `SpireServer`, `SpireAgent`, `SpiffeCSIDriver`, `SpireOIDCDiscoveryProvider`, `ZeroTrustWorkloadIdentityManager` 사용자 정의 리소스를 지원합니다. 주석을 추가하여 조정 프로세스를 일시 중지할 수 있습니다.

사전 요구 사항

시스템에 Zero Trust Workload Identity Manager를 설치했습니다.

SPIRE 서버, 에이전트, SPIFFE CSI(Container Storage Interface) 및 OpenID Connect(OIDC) 검색 공급자를 설치했으며 실행 중입니다.

프로세스

`SpireServer` 사용자 정의 리소스 조정을 일시 중지하려면 다음 명령을 실행하여 이름이 지정된 `클러스터에`

`create-only` 주석을 추가합니다.

```shell-session
$ oc annotate SpireServer cluster -n zero-trust-workload-identity-manager ztwim.openshift.io/create-only=true
```

검증

`SpireServer` 리소스의 상태를 확인하여 `create-only` 모드가 활성 상태인지 확인합니다. `상태는`

`true` 여야 하며 `이유는`

`CreateOnlyModeEnabled` 여야 합니다.

```shell-session
$ oc get SpireServer cluster -o yaml
```

```yaml
status:
  conditions:
  - lastTransitionTime: "2025-09-03T12:13:39Z"
    message: Create-only mode is enabled via ztwim.openshift.io/create-only annotation
    reason: CreateOnlyModeEnabled
    status: "True"
    type: CreateOnlyMode
```

#### 10.6.2. 주석으로 Operator 조정 재시작

프로세스

조정 프로세스를 다시 시작하려면 다음 단계를 따르십시오.

아래 명령을 실행하고 주석 이름 끝에 하이픈(`-`)을 추가합니다. 이렇게 하면 클러스터 리소스에서 주석이 제거됩니다.

```shell
oc annotate
```

```shell-session
$ oc annotate SpireServer cluster -n zero-trust-workload-identity-manager ztwim.openshift.io/create-only-
```

다음 명령을 실행하여 컨트롤러를 다시 시작합니다.

```shell-session
$ oc rollout restart deploy/zero-trust-workload-identity-manager-controller-manager -n zero-trust-workload-identity-manager
```

검증

`SpireServer` 리소스의 상태를 확인하여 `생성 전용` 모드가 비활성화되었는지 확인합니다. `상태는`

`false` 여야 하며 `이유는`

`CreateOnlyModeDisabled` 여야 합니다.

```shell-session
$ oc get SpireServer cluster -o yaml
```

```yaml
status:
  conditions:
  - lastTransitionTime: "2025-09-03T12:13:39Z"
    message: Create-only mode is enabled via ztwim.openshift.io/create-only annotation
    reason: CreateOnlyModeDisabled
    status: "False"
    type: CreateOnlyMode
```

`create-only` 모드가 활성화되면 주석이 제거되더라도 Operator Pod가 재시작될 때까지 지속됩니다. 이 모드를 종료하려면 주석을 제거하거나 설정 해제하고 Operator Pod를 다시 시작해야 할 수 있습니다.

### 10.7. Zero Trust Workload Identity Manager 모니터링

기본적으로 Zero Trust Workload Identity Manager의 SPIRE Server 및 SPIRE 에이전트 구성 요소는 메트릭을 내보냅니다. Prometheus Operator 형식을 사용하여 이러한 지표를 수집하도록 OpenShift 모니터링을 구성할 수 있습니다.

#### 10.7.1. 사용자 워크로드 모니터링 활성화

클러스터에서 사용자 워크로드 모니터링을 구성하여 사용자 정의 프로젝트에 대한 모니터링을 활성화할 수 있습니다.

사전 요구 사항

`cluster-admin` 클러스터 역할의 사용자로 클러스터에 액세스할 수 있습니다.

프로세스

`cluster-monitoring-config.yaml` 파일을 생성하여 `ConfigMap` 을 정의하고 구성합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |
    enableUserWorkload: true
```

다음 명령을 실행하여 `ConfigMap` 을 적용합니다.

```shell-session
$ oc apply -f cluster-monitoring-config.yaml
```

검증

사용자 워크로드에 대한 모니터링 구성 요소가 `openshift-user-workload-monitoring` 네임스페이스에서 실행되고 있는지 확인합니다.

```shell-session
$ oc -n openshift-user-workload-monitoring get pod
```

```plaintext
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-6cb6bd9588-dtzxq   2/2     Running   0          50s
prometheus-user-workload-0             6/6     Running   0          48s
prometheus-user-workload-1             6/6     Running   0          48s
thanos-ruler-user-workload-0           4/4     Running   0          42s
thanos-ruler-user-workload-1           4/4     Running   0          42s
```

`prometheus-operator`, `prometheus-user-workload`, `thanos-ruler-user-workload` 와 같은 Pod의 상태는 `Running` 이어야 합니다.

추가 리소스

사용자 정의 프로젝트에 대한 메트릭 컬렉션 설정

#### 10.7.2. 서비스 모니터를 사용하여 SPIRE 서버에 대한 메트릭 컬렉션 구성

SPIRE Server 피연산자는 기본적으로 `/metrics` 엔드포인트의 포트 `9402` 에 지표를 노출합니다. `ServiceMonitor` CR(사용자 정의 리소스)을 생성하여 Prometheus Operator가 사용자 정의 메트릭을 수집할 수 있도록 SPIRE Server에 대한 메트릭 컬렉션을 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 클러스터 역할의 사용자로 클러스터에 액세스할 수 있습니다.

Zero Trust Workload Identity Manager를 설치했습니다.

클러스터에 SPIRE 서버 피연산자를 배포했습니다.

사용자 워크로드 모니터링을 활성화했습니다.

프로세스

`ServiceMonitor` CR을 생성합니다.

`ServiceMonitor` CR을 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    app.kubernetes.io/name: server
    app.kubernetes.io/instance: spire
  name: spire-server-metrics
  namespace: zero-trust-workload-identity-manager
spec:
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
  selector:
    matchLabels:
      app.kubernetes.io/name: server
      app.kubernetes.io/instance: spire
  namespaceSelector:
    matchNames:
    - zero-trust-workload-identity-manager
```

다음 명령을 실행하여 `ServiceMonitor` CR을 생성합니다.

```shell-session
$ oc create -f servicemonitor-spire-server.yaml
```

`ServiceMonitor` CR이 생성되면 사용자 워크로드 Prometheus 인스턴스가 SPIRE 서버에서 지표 컬렉션을 시작합니다. 수집된 지표는 `job="spire-server"` 로 레이블이 지정됩니다.

검증

OpenShift Container Platform 웹 콘솔에서 모니터링 → 대상으로

이동합니다.

라벨 필터 필드에 다음 레이블을 입력하여 메트릭 대상을 필터링합니다.

```shell-session
$ service=spire-server
```

Status (상태) 열에 `spire-server-metrics` 항목에 대해 `Up` 이 표시되는지 확인합니다.

추가 리소스

사용자 워크로드 모니터링 구성

#### 10.7.3. 서비스 모니터를 사용하여 SPIRE 에이전트의 메트릭 컬렉션 구성

SPIRE 에이전트 피연산자는 기본적으로 `/metrics` 엔드포인트의 포트 `9402` 에 지표를 노출합니다. `ServiceMonitor` CR(사용자 정의 리소스)을 생성하여 SPIRE 에이전트에 대한 메트릭 컬렉션을 구성하여 Prometheus Operator가 사용자 정의 지표를 수집할 수 있습니다.

사전 요구 사항

`cluster-admin` 클러스터 역할의 사용자로 클러스터에 액세스할 수 있습니다.

Zero Trust Workload Identity Manager를 설치했습니다.

클러스터에 SPIRE 에이전트 피연산자를 배포했습니다.

사용자 워크로드 모니터링을 활성화했습니다.

프로세스

`ServiceMonitor` CR을 생성합니다.

`ServiceMonitor` CR을 정의하는 YAML 파일을 생성합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    app.kubernetes.io/name: agent
    app.kubernetes.io/instance: spire
  name: spire-agent-metrics
  namespace: zero-trust-workload-identity-manager
spec:
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
  selector:
    matchLabels:
      app.kubernetes.io/name: agent
      app.kubernetes.io/instance: spire
  namespaceSelector:
    matchNames:
    - zero-trust-workload-identity-manager
```

다음 명령을 실행하여 `ServiceMonitor` CR을 생성합니다.

```shell-session
$ oc create -f servicemonitor-spire-agent.yaml
```

`ServiceMonitor` CR이 생성되면 사용자 워크로드 Prometheus 인스턴스는 SPIRE 에이전트에서 메트릭 컬렉션을 시작합니다. 수집된 지표는 `job="spire-agent"` 로 레이블이 지정됩니다.

검증

OpenShift Container Platform 웹 콘솔에서 모니터링 → 대상으로

이동합니다.

라벨 필터 필드에 다음 레이블을 입력하여 메트릭 대상을 필터링합니다.

```shell-session
$ service=spire-agent
```

Status (상태) 열에 `spire-agent-metrics` 항목에 대해 `Up` 이 표시되는지 확인합니다.

추가 리소스

사용자 워크로드 모니터링 구성

#### 10.7.4. Zero Trust Workload Identity Manager의 메트릭 쿼리

클러스터 관리자는 또는 모든 네임스페이스에 대한 보기 액세스 권한이 있는 사용자로 OpenShift Container Platform 웹 콘솔 또는 명령줄을 사용하여 SPIRE 에이전트 및 SPIRE 서버 메트릭을 쿼리할 수 있습니다. 쿼리는 지정된 작업 레이블과 일치하는 SPIRE 구성 요소에서 수집된 모든 메트릭을 검색합니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

Zero Trust Workload Identity Manager를 설치했습니다.

클러스터에 SPIRE 서버 및 SPIRE 에이전트 피연산자를 배포했습니다.

`ServiceMonitor` 오브젝트를 생성하여 모니터링 및 메트릭 컬렉션을 활성화했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 모니터링 → 메트릭 으로 이동합니다.

쿼리 필드에 다음 PromQL 표현식을 입력하여 SPIRE 서버 메트릭을 쿼리합니다.

```plaintext
{job="spire-server"}
```

쿼리 필드에 다음 PromQL 표현식을 입력하여 SPIRE 에이전트 메트릭을 쿼리합니다.

```plaintext
{job="spire-agent"}
```

추가 리소스

메트릭 액세스

### 10.8. Zero Trust Workload Identity Manager 설치 제거

중요

Zero Trust Workload Identity Manager는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

Operator를 제거하고 관련 리소스를 제거하여 OpenShift Container Platform에서 Zero Trust Workload Identity Manager를 제거할 수 있습니다.

#### 10.8.1. Zero Trust Workload Identity Manager 설치 제거

웹 콘솔을 사용하여 Zero Trust Workload Identity Manager를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

Zero Trust Workload Identity Manager가 설치되어 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Zero Trust Workload Identity Manager를 제거합니다.

에코시스템 → 설치된 Operator 로 이동합니다.

Zero Trust Workload Identity Manager 항목 옆에 있는 옵션 메뉴를 클릭한 다음 Operator 설치 제거를 클릭합니다.

확인 대화 상자에서 설치 제거 를 클릭합니다.

#### 10.8.2. CLI를 사용하여 Zero Trust Workload Identity Manager 리소스 설치 제거

Zero Trust Workload Identity Manager를 설치 제거한 후 클러스터에서 연결된 리소스를 삭제하는 옵션이 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

프로세스

다음 명령을 각각 실행하여 피연산자를 설치 제거합니다.

다음 명령을 실행하여 `ZeroTrustWorkloadIdentityManager` 클러스터를 삭제합니다.

```shell-session
$ oc delete ZeroTrustWorkloadIdentityManager cluster
```

다음 명령을 실행하여 `SpireOIDCDiscoveryProvider` 클러스터를 삭제합니다.

```shell-session
$ oc delete SpireOIDCDiscoveryProvider cluster
```

다음 명령을 실행하여 `SpiffeCSIDriver` 클러스터를 삭제합니다.

```shell-session
$ oc delete SpiffeCSIDriver cluster
```

다음 명령을 실행하여 `SpireAgent` 클러스터를 삭제합니다.

```shell-session
$ oc delete SpireAgent cluster
```

다음 명령을 실행하여 `SpireServer` 클러스터를 삭제합니다.

```shell-session
$ oc delete SpireServer cluster
```

다음 명령을 실행하여 PVC(영구 볼륨 클레임)를 삭제합니다.

```shell-session
$ oc delete pvc -l=app.kubernetes.io/managed-by=zero-trust-workload-identity-manager
```

다음 명령을 실행하여 CSI 드라이버를 삭제합니다.

```shell-session
$ oc delete csidriver -l=app.kubernetes.io/managed-by=zero-trust-workload-identity-manager
```

다음 명령을 실행하여 서비스를 삭제합니다.

```shell-session
$ oc delete service -l=app.kubernetes.io/managed-by=zero-trust-workload-identity-manager
```

다음 명령을 실행하여 네임스페이스를 삭제합니다.

```shell-session
$ oc delete ns zero-trust-workload-identity-manager
```

다음 명령을 실행하여 클러스터 역할 바인딩을 삭제합니다.

```shell-session
$ oc delete clusterrolebinding -l=app.kubernetes.io/managed-by=zero-trust-workload-identity-manager
```

다음 명령을 실행하여 클러스터 역할을 삭제합니다.

```shell-session
$ oc delete clusterrole -l=app.kubernetes.io/managed-by=zero-trust-workload-identity-manager
```

다음 명령을 실행하여 승인 wehhook 구성을 삭제합니다.

```shell-session
$ oc delete validatingwebhookconfigurations -l=app.kubernetes.io/managed-by=zero-trust-workload-identity-manager
```

다음 명령을 각각 실행하여 CRD(사용자 정의 리소스 정의)를 삭제합니다.

다음 명령을 실행하여 SPIRE Server CRD를 삭제합니다.

```shell-session
$ oc delete crd spireservers.operator.openshift.io
```

다음 명령을 실행하여 SPIRE 에이전트 CRD를 삭제합니다.

```shell-session
$ oc delete crd spireagents.operator.openshift.io
```

다음 명령을 실행하여 SPIFFEE CSI 드라이버 CRD를 삭제합니다.

```shell-session
$ oc delete crd spiffecsidrivers.operator.openshift.io
```

다음 명령을 실행하여 SPIRE OIDC 검색 공급자 CRD를 삭제합니다.

```shell-session
$ oc delete crd spireoidcdiscoveryproviders.operator.openshift.io
```

다음 명령을 실행하여 SPIRE 및 SPIFFE 클러스터 통합 신뢰 도메인 CRD를 삭제합니다.

```shell-session
$ oc delete crd clusterfederatedtrustdomains.spire.spiffe.io
```

다음 명령을 실행하여 클러스터 SPIFFE ID CRD를 삭제합니다.

```shell-session
$ oc delete crd clusterspiffeids.spire.spiffe.io
```

다음 명령을 실행하여 SPIRE 및 SPIFFE 클러스터 정적 항목 CRD를 삭제합니다.

```shell-session
$ oc delete crd clusterstaticentries.spire.spiffe.io
```

다음 명령을 실행하여 Zero Trust Workload Identity Manager CRD를 삭제합니다.

```shell-session
$ oc delete crd zerotrustworkloadidentitymanagers.operator.openshift.io
```

검증

리소스가 삭제되었는지 확인하려면 각 아래 명령을 다음 명령으로 교체한 다음 명령을 실행합니다. 리소스가 반환되지 않으면 삭제에 성공했습니다.

```shell
oc delete
```

```shell
oc get
```

### 11.1. External Secrets Operator for Red Hat OpenShift 개요

Red Hat OpenShift용 External Secrets Operator는 `external-secrets` 애플리케이션을 배포 및 관리하기 위해 클러스터 전체 서비스로 작동합니다. `external-secrets` 애플리케이션은 외부 시크릿 관리 시스템과 통합되며 클러스터 내에서 시크릿 가져오기, 새로 고침 및 프로비저닝을 수행합니다.

#### 11.1.1. Red Hat OpenShift용 External Secrets Operator 정보

Red Hat OpenShift에 External Secrets Operator를 사용하여 external-secrets 애플리케이션을 OpenShift Container Platform 클러스터와 통합합니다. `external-secrets` 애플리케이션은 AWS Secrets Manager, HashiCorp Vault, Google Secret Manager, Azure Key Vault, IBM Cloud Secrets Manager, AWS Systems Manager Parameter Store 와 같은 외부 공급자에 저장된 시크릿을 가져와서 안전한 방식으로 Kubernetes와 통합합니다.

외부 보안 Operator를 사용하면 다음을 수행할 수 있습니다.

시크릿 라이프사이클 관리에서 애플리케이션을 분리합니다.

규정 준수 요구 사항을 지원하기 위해 시크릿 스토리지를 중앙 집중화합니다.

안전하고 자동화된 보안 교체를 활성화합니다.

세분화된 액세스 제어를 사용하여 다중 클라우드 시크릿 소싱 지원.

액세스 제어 중앙 집중화 및 감사.

중요

클러스터에서 두 개 이상의 외부 Secrets Operator를 사용하지 마십시오. 커뮤니티 외부 Secrets Operator가 클러스터에 설치된 경우 이를 제거한 후 Red Hat OpenShift용 외부 Secrets Operator를 설치해야 합니다.

`external-secrets` 애플리케이션에 대한 자세한 내용은 external-secrets 를 참조하십시오.

외부 Secrets Operator를 사용하여 외부 보안 저장소로 인증하고 시크릿을 검색하고 검색된 보안을 네이티브 Kubernetes 보안에 삽입합니다. 이 방법을 사용하면 애플리케이션에서 외부 시크릿에 직접 액세스하거나 관리할 필요가 없습니다.

#### 11.1.2. External Secrets Operator for Red Hat OpenShift의 외부 시크릿 공급자

External Secrets Operator for Red Hat OpenShift는 다음과 같은 외부 시크릿 공급자 유형으로 테스트합니다.

AWS Secrets Manager

HashiCorp Vault

Google Secret Manager

Azure Key Vault

IBM Cloud Secrets Manager

참고

Red Hat은 타사 보안 저장소 공급자 기능과 관련된 모든 요소를 테스트하지 않습니다. 타사 지원에 대한 자세한 내용은 Red Hat 타사 지원 정책을 참조하십시오.

#### 11.1.3. 외부 보안 공급자 유형 테스트

다음 표에서는 테스트된 각 외부 보안 공급자 유형에 대한 테스트 범위를 보여줍니다.

| 보안 공급자 | 테스트 상태 | 참고 |
| --- | --- | --- |
| AWS Secrets Manager | 부분적으로 테스트됨 | 기본 기능을 보장합니다. |
| AWS Systems Manager 매개변수 저장소 | 부분적으로 테스트됨 | 기본 기능을 보장합니다. |
| HashiCorp Vault | 부분적으로 테스트됨 |  |
| Google Secrets Manager | 부분적으로 테스트됨 |  |

#### 11.1.4. Red Hat OpenShift용 외부 보안 Operator에 대한 FIPS 컴플라이언스 정보

External Secrets Operator for Red Hat OpenShift는 FIPS 규정 준수를 지원합니다. FIPS 모드에서 OpenShift Container Platform을 실행하는 경우 External Secrets Operator는 x86_64, ppc64le 및 s390X 아키텍처에서 FIPS 검증을 위해 NIST에 제출된 RHEL 암호화 라이브러리를 사용합니다. NIST 검증 프로그램에 대한 자세한 내용은 암호화 모듈 검증 프로그램을 참조하십시오. 검증을 위해 제출된 개별 RHEL 암호화 라이브러리의 최신 NIST 상태에 대한 자세한 내용은 규정 준수 활동 및 정부 표준을 참조하십시오.

FIPS 모드를 활성화하려면 FIPS 모드에서 실행되는 OpenShift Container Platform 클러스터에 외부 Secrets Operator를 설치합니다. 자세한 내용은 "클러스터에 추가 보안이 필요합니까?"를 참조하십시오.

#### 11.1.5. 보안 고려 사항

Red Hat OpenShift에 External Secrets Operator를 사용하는 경우 다음과 같은 몇 가지 보안 문제를 고려해야 합니다.

`external-secrets` 피연산자는 구성된 외부 공급자에서 시크릿을 가져와서 Kubernetes 네이티브 `Secrets` 리소스에 저장합니다. 이로 인해 시크릿 제로 문제가 발생합니다. 추가 암호화를 사용하여 보안 오브젝트를 보호하는 것이 좋습니다. 자세한 내용은 데이터 암호화 옵션을 참조하십시오.

`SecretStore` 및 `ClusterSecretStore` 리소스를 구성할 때 단기 인증 정보 기반 권한 부여를 사용하는 것이 좋습니다. 이 접근 방식은 인증 정보가 손상된 경우에도 무단 액세스 권한 창을 제한하여 보안을 강화합니다.

Red Hat OpenShift용 외부 보안 Operator의 보안을 강화하려면 역할 기반 액세스 제어(RBAC)를 구현하는 것이 중요합니다. 이러한 RBAC는 외부 Secrets Operator에서 제공하는 사용자 정의 리소스에 대한 액세스를 정의하고 제한해야 합니다.

#### 11.1.6. 추가 리소스

external-secrets 애플리케이션

컴플라이언스 이해

FIPS 모드에서 클러스터 설치

클러스터에 추가 보안이 필요하십니까?

보안 고려 사항

보안 모범 사례

### 11.2. External Secrets Operator for Red Hat OpenShift 릴리스 정보

External Secrets Operator for Red Hat OpenShift는 외부 보안 관리 시스템에서 가져온 보안에 대한 라이프사이클 관리를 제공하는 클러스터 전체 서비스입니다.

이 릴리스 노트에서는 외부 Secrets Operator의 개발을 추적합니다.

자세한 내용은 External Secrets Operator 개요 를 참조하십시오.

#### 11.2.1. Red Hat OpenShift 1.0.0(일반 가용성)용 External Secrets Operator 릴리스 노트

출시 날짜: 2025-11-03

다음 권고는 Red Hat OpenShift 1.0.0용 외부 Secrets Operator에 사용할 수 있습니다.

RHBA-2025:19416

RHBA-2025:19417

RHBA-2025:19418

RHBA-2025:19463

Red Hat OpenShift용 외부 시크릿 Operator의 버전 1.0.0은 업스트림 external-secrets 프로젝트 버전 v0.19.0을 기반으로 합니다. 자세한 내용은 v0.19.0의 external-secrets 프로젝트 릴리스 노트를 참조하십시오.

#### 11.2.1.1. 버그 수정

이번 릴리스 이전에는 외부 Secrets Operator for Red Hat OpenShift의 콘솔에 나열된 많은 API가 누락되었습니다. 이번 릴리스에서는 API 설명이 추가되었습니다. (OCPBUGS-61081)

#### 11.2.1.2. 새로운 기능 및 개선 사항

Operator API의 이름 변경 및 개선 사항

이번 릴리스에서는 Operator API의 `externalsecrets.operator.openshift.io` 가 `externalsecretsconfigs.operator.openshift.io` 로 이름이 변경되어 이름이 동일하지만 다른 용도인 external-secrets가 제공된 API와 혼동을 방지합니다. 제공된 external-secrets도 재구성되어 새로운 기능이 추가되었습니다.

자세한 내용은 External Secrets Operator for Red Hat OpenShift API 를 참조하십시오.

외부 Secrets Operator의 메트릭 수집 지원

이번 릴리스에서는 Red Hat OpenShift용 External Secrets Operator가 Operator와 피연산자 모두에 대한 메트릭 수집을 지원합니다. 이는 선택 사항이며 활성화해야 합니다.

자세한 내용은 Monitoring the External Secrets Operator for Red Hat OpenShift 에서 참조하십시오.

외부 Secrets Operator에 대한 프록시 구성 지원

이번 릴리스에서는 Red Hat OpenShift용 External Secrets Operator가 Operator와 피연산자 모두에 대한 프록시 구성을 지원합니다.

자세한 내용은 External Secrets Operator for Red Hat OpenShift의 송신 프록시 정보를 참조하십시오.

루트 파일 시스템은 Red Hat OpenShift 컨테이너용 외부 Secrets Operator에 대해 읽기 전용입니다.

이번 릴리스에서는 보안을 개선하기 위해 Red Hat OpenShift 및 모든 피연산자의 외부 Secrets Operator에는 기본적으로 `readOnlyRootFilesystem` 보안 컨텍스트가 true로 설정되어 있습니다. 이번 개선된 기능을 통해 컨테이너가 강화되고 잠재적인 공격자가 컨테이너 루트 파일 시스템의 내용을 수정하지 못하도록 합니다.

외부 Secrets Operator 구성 요소에 네트워크 정책 강화 가능

이번 릴리스에서는 Red Hat OpenShift용 External Secrets Operator에 피연산자 구성 요소에 대한 수신 및 송신 트래픽을 관리하여 향상된 보안을 위해 설계된 사전 정의된 `NetworkPolicy` 리소스가 포함되어 있습니다. 이러한 정책은 메트릭 및 웹 후크 서버로의 수신과 같은 필수 내부 트래픽을 처리하고 OpenShift API 서버 및 DNS 서버로의 송신을 포함합니다. `NetworkPolicy` 배포는 기본적으로 활성화되어 있으며 송신 허용 정책은 외부 공급자에서 시크릿을 가져오려면 `external-secrets` 구성 요소의 `ExternalSecretsConfig` 사용자 정의 리소스에 명시적으로 정의해야 합니다.

자세한 내용은 피연산자의 네트워크 정책 구성을 참조하십시오.

#### 11.2.2. Red Hat OpenShift 0.1.0용 External Secrets Operator 릴리스 노트 (기술 프리뷰)

출시 날짜: 2025-06-26

다음 권고는 Red Hat OpenShift 0.1.0용 외부 Secrets Operator에 사용할 수 있습니다.

RHBA-2025:9747

RHBA-2025:9746

RHBA-2025:9757

RHBA-2025:9763

Red Hat OpenShift용 외부 시크릿 Operator 버전 `0.1.0` 은 업스트림 external-secrets 버전 `0.14.3` 을 기반으로 합니다. 자세한 내용은 v0.14.3의 external-secrets 프로젝트 릴리스 노트를 참조하십시오.

#### 11.2.2.1. 새로운 기능 및 개선 사항

이는 Red Hat OpenShift용 External Secrets Operator의 초기 기술 프리뷰 릴리스입니다.

### 11.3. Red Hat OpenShift용 외부 Secrets Operator 설치

Red Hat OpenShift용 External Secrets Operator는 기본적으로 OpenShift Container Platform에 설치되지 않습니다. 웹 콘솔 또는 CLI(명령줄 인터페이스)를 사용하여 External Secrets Operator를 설치합니다.

#### 11.3.1. Red Hat OpenShift용 외부 보안 Operator의 제한 사항

다음은 `external-secrets` 애플리케이션을 설치 및 제거하는 동안 Red Hat OpenShift용 외부 Secrets Operator의 제한 사항입니다.

Red Hat OpenShift용 External Secrets Operator를 설치 제거해도 `external-secrets` 애플리케이션에 대해 생성된 리소스가 삭제되지 않습니다. 리소스를 수동으로 정리해야 합니다.

생성 후 `externalsecrets.operator.openshift.io` 오브젝트에 `cert-manager` Operator 구성을 추가하면 `external-secrets-cert-controller` 배포 리소스를 수동으로 삭제하여 `external-secrets` 애플리케이션의 저하를 방지합니다.

x86_64 및 arm64 아키텍처에서 실행되는 OpenShift 클러스터에 설치된 경우에만 `externalsecrets.operator.openshift.io` 오브젝트에서 `BitwardenSecretManagerProvider` 필드를 활성화합니다.

원활한 기능을 위해 Red Hat OpenShift용 외부 Secrets Operator를 배포하기 전에 `cert-manager` Operator가 설치되어 작동하는지 확인합니다. 나중에 `cert-manager` Operator를 설치하는 경우 `external-secrets-operator` Pod를 수동으로 다시 시작하여 `externalsecrets.operator.openshift.io` 오브젝트에 cert-manager 구성을 적용합니다.

#### 11.3.2. 웹 콘솔을 사용하여 Red Hat OpenShift용 External Secrets Operator 설치

웹 콘솔을 사용하여 Red Hat OpenShift용 외부 Secrets Operator를 설치할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

에코시스템 → 소프트웨어 카탈로그 로 이동합니다.

검색 상자에 External Secrets Operator 를 입력합니다.

생성된 목록에서 External Secrets Operator for Red Hat OpenShift 를 선택하고 설치를 클릭합니다.

Operator 설치 페이지에서 다음을 수행합니다.

필요한 경우 업데이트 채널을 업데이트합니다. 채널은 기본적으로 External Secrets Operator의 안정적인 최신 릴리스를 설치하는 tech-preview-v0.1 입니다.

버전 드롭다운 목록에서 버전을 선택합니다.

Operator의 설치된 네임스페이스 를 선택합니다.

기본 Operator 네임스페이스를 사용하려면 Operator 권장 네임스페이스 옵션을 선택합니다.

생성한 네임스페이스를 사용하려면 네임스페이스 선택 옵션을 선택한 다음 드롭다운 목록에서 네임스페이스를 선택합니다.

기본 `external-secrets-operator` 네임스페이스가 없는 경우 OLM(Operator Lifecycle Manager)에서 생성됩니다.

업데이트 승인 전략을 선택합니다.

자동 전략을 사용하면 새 버전이 사용 가능할 때 OLM에서 Operator를 자동으로 업데이트할 수 있습니다.

수동 전략을 사용하려면 적절한 자격 증명을 가진 사용자가 Operator 업데이트를 승인해야 합니다.

설치 를 클릭합니다.

검증

Ecosystem → 설치된 Operators 로 이동합니다.

External Secrets Operator 가 `external-secrets-operator` 네임스페이스에 Succeeded 상태로 나열되어 있는지 확인합니다.

#### 11.3.3. CLI를 사용하여 Red Hat OpenShift용 External Secrets Operator 설치

CLI(명령줄 인터페이스)를 사용하여 Red Hat OpenShift용 외부 Secrets Operator를 설치할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 `external-secrets-operator` 라는 새 프로젝트를 생성합니다.

```shell-session
$ oc new-project external-secrets-operator
```

다음 콘텐츠로 YAML 파일을 정의하여 `OperatorGroup` 오브젝트를 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-external-secrets-operator
  namespace: external-secrets-operator
spec:
  targetNamespaces: []
```

다음 명령을 실행하여 `OperatorGroup` 오브젝트를 생성합니다.

```shell-session
$ oc create -f operatorGroup.yaml
```

다음 콘텐츠로 YAML 파일을 정의하여 `Subscription` 오브젝트를 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-external-secrets-operator
  namespace: external-secrets-operator
spec:
  channel: tech-preview-v0.1
  name: openshift-external-secrets-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
```

다음 명령을 실행하여 서브스크립션 오브젝트를 생성합니다.

```shell-session
$ oc create -f subscription.yaml
```

검증

다음 명령을 실행하여 OLM 서브스크립션이 생성되었는지 확인합니다.

```shell-session
$ oc get subscription -n external-secrets-operator
```

```shell-session
NAME                                  PACKAGE                               SOURCE          CHANNEL
openshift-external-secrets-operator   openshift-external-secrets-operator   eso-010-index   tech-preview-v0.1
```

다음 명령을 실행하여 Operator가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get csv -n external-secrets-operator
```

```shell-session
NAME                               DISPLAY                                           VERSION   REPLACES   PHASE
external-secrets-operator.v0.1.0   External Secrets Operator for Red Hat OpenShift   0.1.0                Succeeded
```

다음 명령을 입력하여 외부 Secrets Operator의 상태가 Running인지 확인합니다.

```shell-session
$ oc get pods -n external-secrets-operator
```

```shell-session
NAME                                                            READY   STATUS    RESTARTS   AGE
external-secrets-operator-controller-manager-5699f4bc54-kbsmn   1/1     Running   0          25h
```

#### 11.3.4. 추가 리소스

클러스터에 Operator 추가

#### 11.3.5. CLI를 사용하여 Red Hat OpenShift의 외부 시크릿 피연산자 설치

CLI(명령줄 인터페이스)를 사용하여 외부 시크릿 피연산자를 설치할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

프로세스

다음 내용으로 YAML 파일을 정의하여 `externalsecrets.openshift.operator.io` 오브젝트를 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecrets
metadata:
  labels:
    app.kubernetes.io/name: external-secrets-operator
  name: cluster
spec: {}
```

사양 구성에 대한 자세한 내용은 "외부 시크릿 Operator for Red Hat OpenShift API"를 참조하십시오.

다음 명령을 실행하여 `externalsecrets.openshift.operator.io` 오브젝트를 생성합니다.

```shell-session
$ oc create -f externalsecrets.yaml
```

검증

다음 명령을 입력하여 `external-secrets` Pod가 실행 중인지 확인합니다.

```shell-session
$ oc get pods -n external-secrets
```

```shell-session
NAME                                                READY   STATUS    RESTARTS   AGE
external-secrets-75d47cb9c8-6p4n2                   1/1     Running   0          4h5m
external-secrets-cert-controller-676444b897-qb6ft   1/1     Running   0          4h5m
external-secrets-webhook-b566658ff-7m4d5            1/1     Running   0          4h5m
```

다음 명령을 실행하여 `external-secrets-operator` 배포 오브젝트가 성공적인 상태를 보고하는지 확인합니다.

```shell-session
$ oc get externalsecrets.operator.openshift.io cluster -n external-secrets-operator -o jsonpath='{.status.conditions}' | jq .
```

```shell-session
[
  {
    "lastTransitionTime": "2025-06-17T14:57:04Z",
    "message": "",
    "observedGeneration": 1,
    "reason": "Ready",
    "status": "False",
    "type": "Degraded"
  },
  {
    "lastTransitionTime": "2025-06-17T14:57:04Z",
    "message": "reconciliation successful",
    "observedGeneration": 1,
    "reason": "Ready",
    "status": "True",
    "type": "Ready"
  }
]
```

### 11.4. 피연산자의 네트워크 정책 구성

Red Hat OpenShift용 External Secrets Operator에는 보안에 대한 사전 정의된 `NetworkPolicies` 가 포함되어 있지만 외부 공급자와 통신할 수 있도록 `ExternalSecretsConfig` 사용자 정의 리소스를 통해 additonal 정책을 구성해야 합니다. 이러한 구성 가능 정책은 `ExternalSecretsConfig` 사용자 정의 리소스를 통해 설정하여 송신 허용 정책을 설정합니다.

#### 11.4.1. 모든 외부 공급자로의 송신을 허용하는 사용자 정의 네트워크 정책 추가

모든 외부 공급자로 모든 송신을 허용하도록 `ExternalSecretsConfig` 사용자 정의 리소스를 통해 사용자 지정 정책을 구성해야 합니다.

사전 요구 사항

`ExternalSecretsConfig` 가 사전 정의되어 있어야 합니다.

대상 포트 및 프로토콜을 포함하여 특정 송신 규칙을 정의할 수 있어야 합니다.

프로세스

다음 명령을 실행하여 `ExternalSecretsConfig` CR을 편집합니다.

```shell-session
$ oc edit externalsecretsconfigs.operator.openshift.io cluster
```

`networkPolicies` 섹션을 편집하여 정책을 설정합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsConfig
metadata:
  name: cluster
spec:
  controllerConfig:
    networkPolicies:
      - name: allow-external-secrets-egress
        componentName: CoreController
        egress: # Allow all egress traffic
```

#### 11.4.2. 특정 공급자로의 송신을 허용하는 사용자 정의 네트워크 정책 추가

특정 공급자로 모든 송신을 허용하도록 `ExternalSecretsConfig` 사용자 정의 리소스를 통해 사용자 지정 정책을 구성해야 합니다.

사전 요구 사항

`ExternalSecretsConfig` 가 사전 정의되어 있어야 합니다.

대상 포트 및 프로토콜을 포함하여 특정 송신 규칙을 정의할 수 있어야 합니다.

프로세스

다음 명령을 실행하여 `ExternalSecretsConfig` CR을 편집합니다.

```shell-session
$ oc edit externalsecretsconfigs.operator.openshift.io cluster
```

`networkPolicies` 섹션을 편집하여 정책을 설정합니다. 다음 예제에서는 AWS(Amazon Web Services) 끝점으로의 송신을 허용하는 방법을 보여줍니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsConfig
metadata:
  name: cluster
spec:
  controllerConfig:
    networkPolicies:
      - componentName: ExternalSecretsCoreController
        egress:
          # Allow egress to Kubernetes API server, AWS endpoints, and DNS
          - ports:
              - port: 443   # HTTPS (AWS Secrets Manager)
                protocol: TCP
      - name: allow-external-secrets-egress
```

다음과 같습니다.

componentName

`ExternalSecretsCoreController` 인 코어 컨트롤러의 이름을 지정합니다. 송신 규칙은 AWS Secrets Manager와 같은 서비스에 대해 TCP(Transmission Control Protocol) 포트 443과 같은 필수 포트를 지정해야 합니다.

#### 11.4.3. 기본 수신 및 송신 규칙

다음 표에는 기본 수신 및 송신 규칙이 요약되어 있습니다.

| Component | Ingress 포트 | 송신 포트 | 설명 |
| --- | --- | --- | --- |
| `external-secrets` | 8080 | 6443 | 메트릭 검색 및 API 서버와 상호 작용 가능 |
| `external-secrets-webhook` | 8080/10250 | 6443 | 메트릭 검색, 웹 후크 요청 처리, API 서버와 상호 작용 가능 |
| `external-secrets-cert-controller` | 8080 | 6443 | 메트릭 검색 및 API 서버와 상호 작용 가능 |
| `external-secrets-bitwarden-server` | 9998 | 6443 | Bitwarden 서버 연결을 처리하고 API 서버와 상호 작용합니다. |
| `external-secrets-allow-dns` |  | 5353 | DNS 조회를 활성화하여 외부 시크릿 공급자를 찾습니다. |

### 11.5. Red Hat OpenShift용 외부 Secrets Operator의 송신 프록시 정보

클러스터 전체 송신 프록시가 OpenShift Container Platform에 구성된 경우 OLM(Operator Lifecycle Manager)은 클러스터 전체 프록시로 관리하는 Operator를 자동으로 구성합니다. OLM은 `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` 환경 변수를 사용하여 모든 Operator의 배포를 자동으로 업데이트합니다.

#### 11.5.1. Red Hat OpenShift용 외부 Secrets Operator에 대한 송신 프록시 구성

송신 프록시는 `ExternalSecretsConfig` 또는 `ExternalSecretsManager` CR(사용자 정의 리소스)에서 구성할 수 있습니다. Operator 및 피연산자는 프록시 검증에 OpenShift Container Platform 지원 CA(인증 기관) 번들을 사용합니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

`ExternalSecretsConfig` 사용자 지정 CR을 생성했습니다.

프로세스

`ExternalSecretsConfig` 리소스에서 프록시를 설정하려면 다음 단계를 수행합니다.

다음 명령을 실행하여 `ExternalSecretsConfig` 리소스를 편집합니다.

```shell-session
$ oc edit externalsecretsconfigs.operator.openshift.io cluster
```

`spec.appConfig.proxy` 섹션을 편집하여 다음과 같이 프록시 값을 설정합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsConfig
...
spec:
  appConfig:
    proxy:
      httpProxy: <http_proxy>
      httpsProxy: <https_proxy>
      noProxy: <no_proxy>
```

다음과 같습니다.

<http_proxy>

http 요청에 대한 프록시 URL을 지정합니다.

<https_proxy>

https 요청의 프록시 URL을 지정합니다.

<no_proxy>

프록시를 사용하지 않아야 하는 쉼표로 구분된 호스트 이름, CIDR, IP 또는 조합을 지정합니다.

`ExternalSecretsManager` CR에서 프록시를 설정하려면 다음 단계를 수행합니다.

다음 명령을 실행하여 `ExternalSecretsManager` CR을 편집합니다.

```shell-session
$ oc edit externalsecretsmanagers.operator.openshift.io cluster
```

`spec.globalConfig.proxy` 섹션을 편집하여 다음과 같이 프록시 값을 설정합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsManager
...
spec:
  globalConfig:
    proxy:
      httpProxy: <http_proxy>
      httpsProxy: <https_proxy>
      noProxy: <no_proxy>
```

다음과 같습니다.

<http_proxy>

http 요청에 대한 프록시 URL을 지정합니다.

<https_proxy>

https 요청에 대한 프록시 URL입니다.

<no_proxy>

쉼표로 구분된 호스트 이름, CIDR, IP 또는 프록시를 사용하지 않아야 하는 호스트 이름, CIDR, IP의 조합 목록입니다.

#### 11.5.2. 추가 리소스

Operator Lifecycle Manager에서 프록시 지원 구성

### 11.6. Red Hat OpenShift용 외부 시크릿 Operator 모니터링

기본적으로 Red Hat OpenShift의 External Secrets Operator는 Operator 및 피연산자에 대한 지표를 표시합니다. Prometheus Operator 형식을 사용하여 이러한 지표를 수집하도록 OpenShift 모니터링을 구성할 수 있습니다.

#### 11.6.1. 사용자 워크로드 모니터링 활성화

클러스터에서 사용자 워크로드 모니터링을 구성하여 사용자 정의 프로젝트에 대한 모니터링을 활성화할 수 있습니다. 자세한 내용은 "사용자 정의 프로젝트에 대한 메트릭 컬렉션 설정"을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`cluster-monitoring-config.yaml` YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |
    enableUserWorkload: true
```

다음 명령을 실행하여 `ConfigMap` 을 적용합니다.

```shell-session
$ oc apply -f cluster-monitoring-config.yaml
```

검증

다음 명령을 실행하여 사용자 워크로드에 대한 모니터링 구성 요소가 `openshift-user-workload-monitoring` 네임스페이스에서 실행되고 있는지 확인합니다.

```shell-session
$ oc -n openshift-user-workload-monitoring get pod
```

```shell-session
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-5f79cff9c9-67pjb   2/2     Running   0          25h
prometheus-user-workload-0             6/6     Running   0          25h
thanos-ruler-user-workload-0           4/4     Running   0          25h
```

`prometheus-operator`, `prometheus-user-workload`, `thanos-ruler-user-workload` 와 같은 Pod의 상태는 `Running` 이어야 합니다.

추가 리소스

사용자 정의 프로젝트에 대한 메트릭 컬렉션 설정

#### 11.6.2. ServiceMonitor를 사용하여 Red Hat OpenShift용 외부 시크릿 Operator에 대한 메트릭 컬렉션 구성

Red Hat OpenShift용 External Secrets Operator는 기본적으로 `/metrics` 서비스 끝점의 포트 `8443` 에 지표를 노출합니다. `ServiceMonitor` CR(사용자 정의 리소스)을 생성하여 Prometheus Operator가 사용자 정의 지표를 수집할 수 있도록 Operator에 대한 메트릭 컬렉션을 구성할 수 있습니다. 자세한 내용은 "사용자 워크로드 모니터링 구성"을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

Red Hat OpenShift용 External Secrets Operator가 설치되어 있습니다.

사용자 워크로드 모니터링을 활성화했습니다.

프로세스

메트릭 서버에 `HTTP` 를 사용하도록 Operator를 구성합니다. `HTTPS` 는 기본적으로 활성화되어 있습니다.

다음 명령을 실행하여 Red Hat OpenShift용 외부 Secrets Operator에 대한 서브스크립션 오브젝트를 업데이트하여 `HTTP` 프로토콜을 구성합니다.

```shell-session
$ oc -n external-secrets-operator patch subscription openshift-external-secrets-operator --type='merge' -p '{"spec":{"config":{"env":[{"name":"METRICS_BIND_ADDRESS","value":":8080"}, {"name": "METRICS_SECURE", "value": "false"}]}}}'
```

External Secrets Operator Pod가 재배포되고 `METRICS_BIND_ADDRESS` 및 `METRICS_SECURE` 에 대해 구성된 값이 업데이트되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc set env --list deployment/external-secrets-operator-controller-manager -n external-secrets-operator | grep -e METRICS_BIND_ADDRESS -e METRICS_SECURE -e container
```

다음 예제에서는 `METRICS_BIND_ADDRESS` 및 `METRICS_SECURE` 가 업데이트되었음을 보여줍니다.

```shell-session
# deployments/external-secrets-operator-controller-manager, container manager
METRICS_BIND_ADDRESS=:8080
METRICS_SECURE=false
```

`kubernetes.io/service-account.name` 주석을 사용하여 `Secret` 리소스를 생성하여 지표 서버로 인증하는 데 필요한 토큰을 삽입합니다.

`secret-external-secrets-operator.yaml` YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  labels:
    app: external-secrets-operator
  name: external-secrets-operator-metrics-auth
  namespace: external-secrets-operator
  annotations:
    kubernetes.io/service-account.name: external-secrets-operator-controller-manager
type: kubernetes.io/service-account-token
```

다음 명령을 실행하여 `Secret` 리소스를 생성합니다.

```shell-session
$ oc apply -f secret-external-secrets-operator.yaml
```

메트릭에 액세스 권한을 부여하는 데 필요한 `ClusterRoleBinding` 리소스를 생성합니다.

`clusterrolebinding-external-secrets.yaml` YAML 파일을 생성합니다.

다음 예제에서는 `cluserrolebinding-external-secrets.yaml` 파일을 보여줍니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    app: external-secrets-operator
  name: external-secrets-allow-metrics-access
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-secrets-operator-metrics-reader
subjects:
  - kind: ServiceAccount
    name: external-secrets-operator-controller-manager
    namespace: external-secrets-operator
```

다음 명령을 실행하여 `ClusterRoldeBinding` 사용자 정의 리소스를 생성합니다.

```shell-session
$ oc apply -f clusterrolebinding-external-secrets.yaml
```

기본 `HTTPS` 를 사용하는 경우 `ServiceMonitor` CR을 생성합니다.

`servicemonitor-external-secrets-operator-https.yaml` YAML 파일을 생성합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    app: external-secrets-operator
  name: external-secrets-operator-metrics-monitor
  namespace: external-secrets-operator
spec:
  endpoints:
    - authorization:
        credentials:
          name: external-secrets-operator-metrics-auth
          key: token
        type: Bearer
      interval: 60s
      path: /metrics
      port: metrics-https
      scheme: https
      scrapeTimeout: 30s
      tlsConfig:
        ca:
          configMap:
            name: openshift-service-ca.crt
            key: service-ca.crt
        serverName: external-secrets-operator-controller-manager-metrics-service.external-secrets-operator.svc.cluster.local
  namespaceSelector:
    matchNames:
      - external-secrets-operator
  selector:
    matchLabels:
      app: external-secrets-operator
      svc: external-secrets-operator-controller-manager-metrics-service
```

다음 명령을 실행하여 `ServiceMonitor` CR을 생성합니다.

```shell-session
$ oc apply -f servicemonitor-external-secrets-operator-https.yaml
```

`HTTP` 를 사용하도록 구성된 경우 `ServiceMonitor` CR을 생성합니다.

`servicemonitor-external-secrets-operator-http.yaml` YAML 파일을 생성합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    app: external-secrets-operator
  name: external-secrets-operator-metrics-monitor
  namespace: external-secrets-operator
spec:
  endpoints:
    - authorization:
        credentials:
          name: external-secrets-operator-metrics-auth
          key: token
        type: Bearer
      interval: 60s
      path: /metrics
      port: metrics-http
      scheme: http
      scrapeTimeout: 30s
  namespaceSelector:
    matchNames:
      - external-secrets-operator
  selector:
    matchLabels:
      app: external-secrets-operator
      svc: external-secrets-operator-controller-manager-metrics-service
```

다음 명령을 실행하여 `ServiceMonitor` CR을 생성합니다.

```shell-session
$ oc apply -f servicemonitor-external-secrets-operator-http.yaml
```

`ServiceMonitor` CR이 생성되면 사용자 워크로드 Prometheus 인스턴스는 Operator에서 메트릭 수집을 시작합니다. 수집된 지표는 `job="external-secrets-operator-controller-manager-metrics-service"` 로 레이블이 지정됩니다.

검증

OpenShift Container Platform 웹 콘솔에서 모니터링 → 대상으로

이동합니다.

라벨 필터 필드에 다음 레이블을 입력하여 각 피연산자의 메트릭 대상을 필터링합니다.

```shell-session
$ service=external-secrets-operator-controller-manager-metrics-service
```

`external-secrets-operator` 의 Status 열에 `Up` 이 표시되는지 확인합니다.

추가 리소스

구성 가능한 모니터링 구성 요소

#### 11.6.3. Red Hat OpenShift용 External Secrets Operator의 메트릭 쿼리

클러스터 관리자 또는 모든 네임스페이스에 대한 보기 액세스 권한이 있는 사용자는 OpenShift Container Platform 웹 콘솔 또는 CLI(명령줄 인터페이스)를 사용하여 Operator 지표를 쿼리할 수 있습니다. 자세한 내용은 " metrics 액세스"를 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

Red Hat OpenShift용 External Secrets Operator가 설치되어 있습니다.

`ServiceMonitor` 오브젝트를 생성하여 모니터링 및 메트릭 컬렉션을 활성화했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 모니터링 → 메트릭 으로 이동합니다.

쿼리 필드에 다음 PromQL 표현식을 입력하여 External Secrets Operator for Red Hat OpenShift 메트릭을 쿼리합니다.

```plaintext
{job="external-secrets-operator-controller-manager-metrics-service"}
```

추가 리소스

메트릭 액세스

#### 11.6.4. ServiceMonitor를 사용하여 Red Hat OpenShift 피연산자에 대한 외부 시크릿 Operator에 대한 메트릭 컬렉션 구성

Red Hat OpenShift 피연산자용 External Secrets Operator는 세 가지 구성 요소(external-secrets, `external-secrets-cert-controll`, `external- secrets -webhook`)에 대해 `/metrics` 서비스 끝점의 포트 `8080` 에 기본적으로 지표를 노출합니다. `ServiceMonitor` CR(사용자 정의 리소스)을 생성하여 external-secrets 피연산자에 대한 메트릭 컬렉션을 구성하여 Prometheus Operator에서 사용자 정의 지표를 수집할 수 있습니다. 자세한 내용은 "사용자 워크로드 모니터링 구성"을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

Red Hat OpenShift용 External Secrets Operator가 설치되어 있습니다.

사용자 워크로드 모니터링을 활성화했습니다.

프로세스

메트릭에 액세스 권한을 부여하는 데 필요한 `ClusterRoleBinding` 리소스를 생성합니다.

`clusterrolebinding-external-secrets.yaml` YAML 파일을 생성합니다.

다음 예제에서는 `cluserrolebinding-external-secrets.yaml` 파일을 보여줍니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    app: external-secrets
  name: external-secrets-allow-metrics-access
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-secrets-operator-metrics-reader
subjects:
  - kind: ServiceAccount
    name: external-secrets
    namespace: external-secrets
  - kind: ServiceAccount
    name: external-secrets-cert-controller
    namespace: external-secrets
  - kind: ServiceAccount
    name: external-secrets-webhook
    namespace: external-secrets
```

다음 명령을 실행하여 `ClusterRoldeBinding` 사용자 정의 리소스를 생성합니다.

```shell-session
$ oc apply -f clusterrolebinding-external-secrets.yaml
```

`ServiceMonitor` CR을 생성합니다.

`servicemonitor-external-secrets.yaml` YAML 파일을 생성합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    app: external-secrets
  name: external-secrets-metrics-monitor
  namespace: external-secrets
spec:
  endpoints:
    - interval: 60s
      path: /metrics
      port: metrics
      scheme: http
      scrapeTimeout: 30s
  namespaceSelector:
    matchNames:
      - external-secrets
  selector:
    matchExpressions:
      - key: app.kubernetes.io/name
        operator: In
        values:
          - external-secrets
          - external-secrets-cert-controller
          - external-secrets-webhook
      - key: app.kubernetes.io/instance
        operator: In
        values:
          - external-secrets
      - key: app.kubernetes.io/managed-by
        operator: In
        values:
          - external-secrets-operator
```

다음 명령을 실행하여 `ServiceMonitor` CR을 생성합니다.

```shell-session
$ oc apply -f servicemonitor-external-secrets.yaml
```

`ServiceMonitor` CR이 생성되면 사용자 워크로드 Prometheus 인스턴스는 Red Hat OpenShift 피연산자용 External Secrets Operator에서 메트릭 수집을 시작합니다. 수집된 지표는 `job="external-secrets"`, `job="external-secrets-cainjector"` 및 `job="external-secrets-webhook"` 로 레이블이 지정됩니다.

검증

OpenShift Container Platform 웹 콘솔에서 모니터링 → 대상으로

이동합니다.

라벨 필터 필드에 다음 레이블을 입력하여 각 피연산자의 메트릭 대상을 필터링합니다.

```shell-session
$ service=external-secrets
```

```shell-session
$ service=external-secrets-cert-controller-metrics
```

```shell-session
$ service=external-secrets-webhook
```

Status 열에 external-secrets, `external-secrets` - `cert-controller 및 external-secrets- webhook` 에 대한 `Up` 이 표시되는지 확인합니다.

추가 리소스

사용자 워크로드 모니터링 구성

#### 11.6.5. external-secrets 피연산자의 메트릭 쿼리

클러스터 관리자는 또는 모든 네임스페이스에 대한 보기 액세스 권한이 있는 사용자로 OpenShift Container Platform 웹 콘솔 또는 CLI(명령줄 인터페이스)를 사용하여 `external-secrets` 피연산자 메트릭을 쿼리할 수 있습니다. 자세한 내용은 " metrics 액세스"를 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

Red Hat OpenShift용 External Secrets Operator가 설치되어 있습니다.

`ServiceMonitor` 오브젝트를 생성하여 모니터링 및 메트릭 컬렉션을 활성화했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 모니터링 → 메트릭 으로 이동합니다.

쿼리 필드에 다음 PromQL 표현식을 입력하여 각 피연산자의 외부 Secrets Operator를 쿼리합니다.

```plaintext
{job="external-secrets"}
```

```plaintext
{job="external-secrets-webhook"}
```

```plaintext
{job="external-secrets-cert-controller-metrics"}
```

추가 리소스

메트릭 액세스

### 11.7. Red Hat OpenShift용 외부 보안 Operator 사용자 정의

Red Hat OpenShift용 External Secrets Operator가 설치된 후 `ExternalSecretsConfig` CR(사용자 정의 리소스)을 편집하여 동작을 사용자 지정할 수 있습니다. 이를 통해 external-secrets 컨트롤러, cert-controller, webhook, `bitwardenSecretManagerProvider` 플러그인과 같은 구성 요소를 수정할 수 있으며 Operator Pod의 환경 변수도 설정할 수 있습니다.

추가 리소스

External Secrets Operator for Red hat OpenShift API

#### 11.7.1. Red Hat OpenShift용 외부 Secrets Operator의 로그 수준 설정

Red Hat OpenShift의 External Secrets Operator의 로그 수준을 설정하여 Operator 로그 메시지의 상세 정보를 확인할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

`ExternalSecretsConfig` 사용자 정의 리소스를 생성했습니다.

프로세스

다음 명령을 실행하여 Red Hat OpenShift용 외부 Secrets Operator의 서브스크립션 오브젝트를 업데이트하여 Operator 로그에 대한 상세 정보 표시 수준을 제공합니다.

```shell-session
$ oc -n <external_secrets_operator_namespace> patch subscription openshift-external-secrets-operator --type='merge' -p '{"spec":{"config":{"env":[{"name":"OPERATOR_LOG_LEVEL","value":"<log_level>"}]}}}'
```

다음과 같습니다.

external_secrets_operator_namespace

Operator가 설치된 네임스페이스를 지정합니다.

log_level

로그 세부 정보 수준을 지정합니다. 값 범위는 1-5입니다. 기본값은 2입니다.

검증

External Secrets Operator Pod가 재배포됩니다. 다음 명령을 실행하여 Red Hat OpenShift용 외부 시크릿 Operator의 로그 수준이 업데이트되었는지 확인합니다.

```shell-session
$ oc set env deploy/external-secrets-operator-controller-manager -n external-secrets-operator --list | grep -e OPERATOR_LOG_LEVEL -e container
```

다음 예제에서는 Red Hat OpenShift용 External Secrets Operator의 로그 수준이 업데이트되었는지 확인합니다.

```shell-session
# deployments/external-secrets-operator-controller-manager, container manager
OPERATOR_LOG_LEVEL=2
```

아래 명령을 실행하여 Red Hat OpenShift용 외부 Secrets Operator의 로그 수준이 업데이트되었는지 확인합니다.

```shell
oc logs
```

```shell-session
$ oc logs -n external-secrets-operator -f deployments/external-secrets-operator-controller-manager -c manager
```

#### 11.7.2. Red Hat OpenShift 피연산자용 External Secrets Operator의 로그 수준 설정

Red Hat OpenShift의 외부 Secrets Operator의 로그 수준을 설정하여 로그 메시지의 상세 수준을 확인할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

`ExternalSecretsConfig` 사용자 정의 리소스를 생성했습니다.

프로세스

다음 명령을 실행하여 `ExternalSecretsConfig` CR을 편집합니다.

```shell-session
$ oc edit externalsecretsconfigs.operator.openshift.io cluster
```

`spec.appConfig.logLevel` 섹션을 편집하여 로그 수준 값을 설정합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsConfig
...
spec:
  appConfig:
    logLevel: <log_level>
```

1. 1-5의 값 범위를 지원합니다. 로그 수준은 다음 피연산자 지원 수준에 매핑됩니다.

1 - 경고

2 - 오류 로그

3 - 정보 로그

4 및 5 - 디버그 로그

변경 사항을 저장하고 편집기를 종료합니다.

#### 11.7.3. external-secrets 인증서 요구 사항에 맞게 cert-manager 구성

`external-secrets` 웹 후크 및 플러그인은 인증서 관리를 위해 `cert-manager` 에 할당할 수 있습니다. 이 구성은 선택 사항입니다.

`cert-manager` 를 사용하지 않으면 `external-secrets` 의 기본값은 자체 인증서 관리입니다. 이 모드에서는 플러그인에 대한 인증서를 수동으로 구성하는 동안 Webhook에 필요한 인증서를 자동으로 생성합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

`ExternalSecretsConfig` 사용자 정의 리소스를 생성했습니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다. 자세한 내용은 "Cert-manager Operator for Red Hat OpenShift 설치"를 참조하십시오.

프로세스

다음 명령을 실행하여 `ExternalSecretsConfig` 사용자 정의 리소스를 편집합니다.

```shell-session
$  oc edit externalsecretsconfigs.operator.openshift.io cluster
```

`spec.controllerConfig.certProvider.certManager` 섹션을 다음과 같이 편집하여 `cert-manager` 를 구성합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsConfig
...
spec:
  controllerConfig:
    certProvider:
      certManager:
        injectAnnotations: "true"
        issuerRef:
          name: <issuer_name>
          kind: <issuer_kind>
          group: <issuer_group>
        mode: Enabled
```

다음과 같습니다.

injectAnnotation

활성화된 경우 `true` 로 설정해야 합니다.

name

`ExternalSecretsConfig` 에서 참조하는 발급자 오브젝트의 이름을 지정합니다.

kind

API 발행자를 지정합니다. `Issuer` 또는 `ClusterIssuer` 로 설정할 수 있습니다.

group

API 발행자 그룹을 지정합니다. 그룹 이름은 `cert-manager.io` 여야 합니다.

mode

`enabled` 로 설정해야 합니다. 이는 변경할 수 없는 필드이며 구성 후에는 수정할 수 없습니다.

변경 사항을 저장하십시오.

`externalsecretsconfig.operator.openshift.io` 오브젝트에서 `cert-manager` 구성을 업데이트한 후 다음 명령을 실행하여 `external-secrets-cert-controller` 배포를 수동으로 삭제해야 합니다. 이렇게 하면 `external-secrets` 애플리케이션의 성능 저하가 방지됩니다.

```shell-session
$ oc delete deployments.apps external-secrets-cert-controller -n external-secrets
```

선택적으로 다음 명령을 실행하여 `cert-controller` 에 대해 생성된 다른 리소스를 삭제할 수 있습니다.

```shell-session
$ oc delete clusterrolebindings.rbac.authorization.k8s.io external-secrets-cert-controller
```

```shell-session
$ oc delete clusterroles.rbac.authorization.k8s.io external-secrets-cert-controller
```

```shell-session
$ oc delete serviceaccounts external-secrets-cert-controller -n external-secrets
```

```shell-session
$ oc delete secrets external-secrets-webhook -n external-secrets
```

추가 리소스

Cert-manager Operator for Red Hat Openshift

Red Hat Openshift용 cert-manager-Operator 설치

#### 11.7.4. bitwardenSecretManagerProvider 플러그인 구성

Bit `wardenSecretManagerProvider` 가 Bitwarden Secrets Manager 공급자를 보안 소스로 사용하도록 활성화할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

`ExternalSecretsConfig` 사용자 정의 리소스를 생성했습니다.

프로세스

다음 명령을 실행하여 `ExternalSecretsConfig` 사용자 정의 리소스를 편집합니다.

```shell-session
$  oc edit externalsecretsconfigs.operator.openshift.io cluster
```

다음과 같이 `spec.plugins.bitwardenSecretManagerProvider` 섹션을 편집하여 Bitwarden Secrets Manager를 활성화합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsConfig
...
spec:
  plugins:
    bitwardenSecretManagerProvider:
      mode: Enabled
      secretRef:
        name: <secret_object_name>
```

다음과 같습니다.

name

플러그인의 인증서 키 쌍을 포함하는 보안의 이름입니다. 인증서의 시크릿의 키 이름은 `tls.crt` 여야 합니다. 개인 키의 키 이름은 `tls.key` 여야 합니다. CA(인증 기관) 인증서 키 이름의 키 이름은 `ca.crt` 여야 합니다. cert-manager 인증서 공급자가 구성된 경우 보안을 구성하는 것은 선택 사항입니다.

변경 사항을 저장하고 편집기를 종료합니다.

플러그인을 비활성화하는 경우 다음 명령을 실행하여 다음 리소스를 수동으로 삭제해야 합니다.

```shell-session
$ oc delete deployments.apps bitwarden-sdk-server -n external-secrets
```

```shell-session
$ oc delete certificates.cert-manager.io bitwarden-tls-certs -n external-secrets
```

```shell-session
$ oc delete service bitwarden-sdk-server -n external-secrets
```

```shell-session
$ oc delete serviceaccounts bitwarden-sdk-server -n external-secrets
```

### 11.8. Red Hat OpenShift용 외부 시크릿 Operator 설치 제거

Operator를 제거하고 관련 리소스를 제거하여 OpenShift Container Platform에서 Red Hat OpenShift용 External Secrets Operator를 제거할 수 있습니다.

#### 11.8.1. 웹 콘솔을 사용하여 Red Hat OpenShift용 External Secrets Operator 설치 제거

웹 콘솔을 사용하여 Red Hat OpenShift용 External Secrets Operator를 설치 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

External Secrets Operator가 설치되어 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

다음 단계를 사용하여 Red Hat OpenShift용 External Secrets Operator를 설치 제거합니다.

Ecosystem → 설치된 Operators 로 이동합니다.

외부 Secrets Operator for Red Hat OpenShift 항목 옆에 있는 옵션 메뉴

를 클릭하고 Operator 설치 제거를 클릭합니다.

확인 대화 상자에서 설치 제거 를 클릭합니다.

#### 11.8.2. 웹 콘솔을 사용하여 Red Hat OpenShift 리소스에 대한 외부 Secrets Operator 제거

Red Hat OpenShift용 외부 Secrets Operator를 설치 제거한 후 클러스터에서 연결된 리소스를 선택적으로 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

`external-secrets` 네임스페이스에서 `external-secrets` 애플리케이션 구성 요소의 배포를 제거합니다.

프로젝트 드롭다운 메뉴를 클릭하여 사용 가능한 모든 프로젝트 목록을 확인하고 external-secrets 프로젝트를 선택합니다.

워크로드 → 배포로 이동합니다.

삭제할 배포를 선택합니다.

작업 드롭다운 메뉴를 클릭하고 배포 삭제 를 선택하여 확인 대화 상자를 확인합니다.

삭제 를 클릭하여 배포를 삭제합니다.

다음 단계를 사용하여 외부 Secrets Operator에서 설치한 CRD(사용자 정의 리소스 정의)를 제거합니다.

관리 → 클러스터 리소스 정의 로 이동합니다.

Label 필드의 제안에서 `external-secrets.io/component: controller` 를 선택하여 CRD를 필터링합니다.

다음 각 CRD 옆에 있는 옵션 메뉴

를 클릭하고 사용자 정의 리소스 정의 삭제 를 선택합니다.

ACRAccessToken

ClusterExternalSecret

ClusterGenerator

ClusterSecretStore

ECRAuthorizationToken

ExternalSecret

GCRAccessToken

GeneratorState

GithubAccessToken

Grafana

암호

PushSecret

QuayAccessToken

SecretStore

STSSessionToken

UUID

VaultDynamicSecret

Webhook

다음 단계를 사용하여 `external-secrets-operator` 네임스페이스를 제거합니다.

관리 → 네임스페이스 로 이동합니다.

외부 시크릿 Operator 옆에 있는 옵션 메뉴

를 클릭하고 네임스페이스 삭제 를 선택합니다.

확인 대화 상자에서 필드에 `external-secrets-operator` 를 입력하고 삭제 를 클릭합니다.

#### 11.8.3. CLI를 사용하여 Red Hat OpenShift 리소스에 대한 외부 Secrets Operator 제거

Red Hat OpenShift용 외부 Secrets Operator를 설치 제거한 후 선택적으로 CLI(명령줄 인터페이스)를 사용하여 클러스터에서 연결된 리소스를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 `external-secrets` 네임스페이스에서 `external-secrets` 애플리케이션 구성 요소의 배포를 삭제합니다.

```shell-session
$ oc delete deployment -n external-secrets -l app=external-secrets
```

다음 명령을 실행하여 외부 Secrets Operator에서 설치한 CRD(사용자 정의 리소스 정의)를 삭제합니다.

```shell-session
$ oc delete customresourcedefinitions.apiextensions.k8s.io -l external-secrets.io/component=controller
```

다음 명령을 실행하여 `external-secrets-operator` 네임스페이스를 삭제합니다.

```shell-session
$ oc delete project external-secrets-operator
```

### 11.9. External Secrets Operator for Red Hat OpenShift API

External Secrets Operator for Red Hat OpenShift는 다음 두 API를 사용하여 `external-secrets` 애플리케이션 배포를 구성합니다.

| 그룹 | 버전 | 유형 |
| --- | --- | --- |
| `operator.openshift.io` | `v1alpha1` | `externalsecretsConfig` |
| `operator.openshift.io` | `v1alpha1` | `externalsecretsmanager` |

다음 목록에는 Red Hat OpenShift API용 외부 Secrets Operator가 포함되어 있습니다.

ExternalSecretsConfig

ExternalSecretsManager

#### 11.9.1. externalSecretsManagerList

`externalSecretsManagerList` 오브젝트는 `externalSecretsManager` 오브젝트 목록을 가져옵니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `apiVersion` | string | `apiVersion` 은 사용 중인 스키마 버전, 즉 `operator.openshift.io/v1alpha1` 을 지정합니다. |  |  |
| `kind` | string | `kind` 는 이 API의 `externalSecretsManagerList` 인 오브젝트 유형을 지정합니다. |  |  |
| `메타데이터` | ListMeta | `메타데이터` 필드에 대한 자세한 내용은 Kubernetes API 설명서를 참조하십시오. |  |  |
| `items` | array |  |  |  |

#### 11.9.2. externalSecretsManager

`externalSecretsManager` 오브젝트는 External Secrets Operator에서 관리하는 배포의 구성 및 정보를 정의합니다. 이름을 `cluster` 로 설정하면 클러스터당 `externalSecretsManager` 인스턴스가 하나만 허용됩니다.

`externalSecretsManager` 를 사용하여 글로벌 옵션을 구성할 수 있습니다. 이는 Operator의 여러 컨트롤러를 관리하기 위한 중앙 집중식 구성 역할을 합니다. Operator는 설치 중에 `externalSecretsManager` 오브젝트를 자동으로 생성합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `apiVersion` | string | `apiVersion` 은 사용 중인 스키마 버전, 즉 `operator.openshift.io/v1alpha1` 을 지정합니다. |  |  |
| `kind` | string | `kind` 는 이 오브젝트에 대한 `externalSecretsManager` 인 오브젝트 유형을 지정합니다. |  |  |
| `메타데이터` | ObjectMeta | `메타데이터` 필드에 대한 자세한 내용은 Kubernetes API 설명서를 참조하십시오. |  |  |
| `spec` | object | `spec` 에는 원하는 동작의 사양이 포함되어 있습니다. |  |  |
| `status` | object | `상태에` 는 외부 Secrets Operator에 가장 최근에 관찰된 컨트롤러 상태가 표시됩니다. |  |  |

#### 11.9.3. externalSecretsConfigList

`externalSecretsConfigList` 오브젝트는 `externalSecretsConfig` 오브젝트 목록을 가져옵니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `apiVersion` | string | `apiVersion` 은 사용 중인 스키마 버전을 지정합니다. `operator.openshift.io/v1alpha1` |  |  |
| `kind` | string | `kind` 는 이 API의 `externalSecretsList` 인 오브젝트 유형을 지정합니다. |  |  |
| `메타데이터` | ListMeta | `메타데이터` 필드에 대한 자세한 내용은 Kubernetes API 설명서를 참조하십시오. |  |  |
| `items` | array | `항목에` 는 `externalSecrets` 오브젝트 목록이 포함되어 있습니다. |  |  |

#### 11.9.4. externalSecretsConfig

`externalSecretsConfig` 오브젝트는 관리되는 `external-secrets` 피연산자 배포에 대한 구성 및 정보를 정의합니다. 이름을 `cluster` 로 설정합니다. `externalSecretsConfig` 오브젝트로 설정하면 클러스터당 하나의 인스턴스만 허용됩니다.

`externalSecretsConfig` 오브젝트를 생성하면 `external-secrets` 피연산자의 배포가 트리거되고 원하는 상태가 유지됩니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `apiVersion` | string | `apiVersion` 은 사용 중인 스키마 버전, 즉 `operator.openshift.io/v1alpha1` 을 지정합니다. |  |  |
| `kind` | string | `kind` 는 이 오브젝트의 `externalSecrets` 인 오브젝트 유형을 지정합니다. |  |  |
| `메타데이터` | ObjectMeta | `메타데이터` 필드에 대한 자세한 내용은 Kubernetes API 설명서를 참조하십시오. |  |  |
| `spec` | object | `spec` 에는 `externalSecrets` 오브젝트의 원하는 동작의 사양이 포함되어 있습니다. |  |  |
| `status` | object | `status` 에는 최근에 관찰된 `externalSecrets` 오브젝트의 상태가 표시됩니다. |  |  |

#### 11.9.5. Red Hat OpenShift API용 External Secrets Operator에 필드 나열

다음 필드는 Red Hat OpenShift API용 외부 Secrets Operator에 적용됩니다.

#### 11.9.6. externalSecretsManagerSpec

`externalSecretsManagerSpec` 필드는 `externalSecretsManager` 오브젝트의 원하는 동작을 정의합니다.

| 필드 | type | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `globalConfig` | object | `globalConfig` 는 External Secrets Operator가 관리하는 배포의 동작을 설정합니다. |  | 선택 사항 |

#### 11.9.7. externalSecretsManagerStatus

`externalSecretsManagerStatus` 필드에는 최근에 관찰된 `externalSecretsManager` 오브젝트의 상태가 표시됩니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `controllerStatuses` | array | `controllerStatuses` 에는 Operator에서 사용하는 컨트롤러의 관찰된 조건이 있습니다. |  |  |
| `lastTransitionTime` | 시간 | `lastTransitionTime` 은 조건의 상태가 변경된 가장 최근의 시간을 기록합니다. |  | 형식: 날짜-시간 유형: 문자열 |

#### 11.9.8. externalSecretsConfigSpec

`externalSecretsConfigSpec` 필드는 `externalSecrets` 오브젝트의 원하는 동작을 정의합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `appConfig` | object | `appconfig` 는 `external-secrets` 피연산자의 동작을 구성합니다. |  | 선택 사항 |
| `plugins` | object | `플러그인` 은 선택적 공급자 플러그인을 구성합니다. |  | 선택 사항 |
| `controllerConfig` | object | `controllerConfig` 는 `external-secrets` 피연산자를 활성화하는 기본값을 설정하도록 컨트롤러를 구성합니다. |  | 선택 사항 |

#### 11.9.9. externalSecretsConfigStatus

`externalSecretsConfigStatus` 필드에는 최근에 관찰된 `externalSecretsConfig` 오브젝트의 상태가 표시됩니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `conditions` | 조건 배열 | `조건에` 는 현재 배포 상태에 대한 정보가 포함되어 있습니다. |  |  |
| `externalSecretsImage` | string | `externalSecretsImage` 는 `external-secrets` 피연산자 배포에 사용되는 이미지 이름과 태그를 지정합니다. |  |  |
| `bitwardenSDKServerImage` | string | `bitwardenSDKServerImage` 는 `bitwarden-sdk-server` 를 배포하는 데 사용되는 이미지 및 태그 이름을 지정합니다. |  |  |

#### 11.9.10. globalConfig

`globalConfig` 필드는 외부 Secrets Operator의 동작을 구성합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `labels` | integer | `레이블` 은 Operator가 생성한 모든 리소스에 적용됩니다. 이 필드에는 최대 20개의 항목이 있을 수 있습니다. | 1 | 최대 속성 수는 20개입니다. 최소 속성 수는 0입니다. 선택 사항 |
| `logLevel` | integer | `loglevel` 은 kubernetes 로깅 지침에 정의된 대로 다양한 값을 지원합니다. | 1 | 최대 범위 값은 5입니다. 최소 범위 값은 1입니다. 선택 사항 |
| `resources` | resourceRequirements | `resources` 는 리소스 요구 사항을 정의합니다. 처음에 설정한 후에는 이 필드의 값을 변경할 수 없습니다. 자세한 내용은 https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ 에서 참조하십시오. |  | 선택 사항 |
| `유사성` | 유사성 | `유사성` 은 스케줄링 선호도 규칙을 설정합니다. 자세한 내용은 https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ 에서 참조하십시오. |  | 선택 사항 |
| `허용 오차` | 톨러레이션 어레이 | `허용 오차` 는 Pod 허용 오차를 설정합니다. 자세한 내용은 https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ 에서 참조하십시오. |  | 최대 항목 수는 50개입니다. 최소 항목 수는 0입니다. 선택 사항 |
| `nodeSelector` | object(keys:string, values:string) | `nodeSelector` 는 노드 레이블을 사용하여 예약 기준을 정의합니다. 자세한 내용은 https://kubernetes.io/docs/concepts/configuration/assign-pod-node/ 에서 참조하십시오. |  | 최대 속성 수는 50입니다. 최소 속성 수는 0입니다. 선택 사항 |
| `proxy` | object | `프록시는` Operator에서 관리하는 피연산자 컨테이너에서 사용할 수 있는 프록시 구성을 환경 변수로 설정합니다. |  | 선택 사항 |

#### 11.9.11. controllerConfig

`controllerConfig` 는 `external-secrets` 피연산자 및 플러그인을 설치할 때 컨트롤러에서 사용하는 구성을 지정합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `certProvider` | string | `certProvider` 는 Webhook 및 플러그인의 TLS 인증서를 관리하는 데 사용되는 인증서 공급자에 대한 구성을 정의합니다. |  | 선택 사항 |
| `labels` | object(keys:string, values:string) | `labels` 필드는 `external-secrets` 피연산자 배포를 위해 생성된 모든 리소스에 레이블을 적용합니다. |  | 최대 속성 수는 20개입니다. 최소 속성 수는 0입니다. 선택 사항 |

#### 11.9.12. controllerStatus

`controllerStatus` 필드에는 Operator에서 사용하는 컨트롤러의 관찰된 조건이 포함됩니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `name` | string | `name` 은 관찰된 조건이 기록되는 컨트롤러의 이름을 지정합니다. |  | 필수 항목 |
| `conditions` | array | `상태에` 는 외부 Secrets Operator 컨트롤러의 현재 상태에 대한 정보가 포함되어 있습니다. |  |  |
| `observedGeneration` | integer | `observedGeneration` 은 관찰된 리소스의 `.metadata.generation` 을 나타냅니다. |  | 관찰된 최소 리소스 수는 0입니다. |

#### 11.9.13. applicationConfig

`applicationConfig` 는 `external-secrets` 피연산자에 대한 구성을 지정합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `logLevel` | integer | `loglevel` 은 kubernetes 로깅 지침에 정의된 대로 다양한 값을 지원합니다. | 1 | 최대 범위 값은 5입니다. 최소 범위 값은 1입니다. 선택 사항 |
| `operatingNamespace` | string | `operatingNamespace` 는 `external-secrets` 피연산자 작업을 제공된 네임스페이스로 제한합니다. 이 필드를 활성화하면 `ClusterSecretStore` 및 `ClusterExternalSecret` 이 비활성화됩니다. |  | 최대 길이는 63입니다. 최소 길이는 1입니다. 선택 사항 |
| `webhookConfig` | object | `webhookConfig` 는 `external-secrets` 피연산자의 Webhook 관련 정보를 구성합니다. |  |  |
| `resources` | resourceRequirements | `resources` 는 리소스 요구 사항을 정의합니다. 처음에 설정한 후에는 이 필드의 값을 변경할 수 없습니다. 자세한 내용은 https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ 에서 참조하십시오. |  | 선택 사항 |
| `유사성` | 유사성 | `유사성` 은 스케줄링 선호도 규칙을 설정합니다. 자세한 내용은 https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ 에서 참조하십시오. |  | 선택 사항 |
| `허용 오차` | 톨러레이션 어레이 | `허용 오차` 는 Pod 허용 오차를 설정합니다. 자세한 내용은 https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ 에서 참조하십시오. |  | 최대 항목 수는 50개입니다. 최소 항목 수는 0입니다. 선택 사항 |
| `nodeSelector` | object(keys:string, values:string) | `nodeSelector` 는 노드 레이블을 사용하여 예약 기준을 정의합니다. 자세한 내용은 https://kubernetes.io/docs/concepts/configuration/assign-pod-node/ 에서 참조하십시오. |  | 최대 속성 수는 50입니다. 최소 속성 수는 0입니다. 선택 사항 |
| `proxy` | object(keys:string, values:string) | `프록시는` Operator에서 관리하는 피연산자 컨테이너에서 사용할 수 있는 프록시 구성을 환경 변수로 설정합니다. |  | 선택 사항 |

#### 11.9.14. bitwardenSecretManagerProvider

`bitwardenSecretManagerProvider` 필드는 Bitwarden 시크릿 관리자 공급자를 활성화하고 Bitwarden 서버에 연결하는 데 필요한 추가 서비스를 설정합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `mode` | string | `mode` 필드는 `enabled` 또는 `Disabled` 로 설정할 수 있는 `bitwardenSecretManagerProvider` 공급자 상태를 활성화합니다. `Enabled` 로 설정하면 Operator에서 플러그인이 배포되고 동기화됩니다. `Disabled` 로 설정하면 Bitwarden 공급자 플러그인 조정이 비활성화됩니다. 플러그인 및 리소스는 현재 상태로 유지되며 Operator에서 관리하지 않습니다. | `비활성화됨` | enum: [Enabled Disabled] 선택 사항 |
| `secretRef` | SecretReference | secret `Ref` 는 Bitwarden 서버의 TLS 키 쌍을 포함하는 Kubernetes 시크릿을 지정합니다. 이 참조가 제공되지 않고 `certManagerConfig` 필드가 구성된 경우 `certManagerConfig` 에 정의된 발급자가 필요한 인증서를 생성합니다. 시크릿은 인증서에 `tls.crt` , 개인 키에는 `tls.key` , CA 인증서에 `ca.crt` 를 사용해야 합니다. |  | 선택 사항 |

#### 11.9.15. webhookConfig

`webhookConfig` 필드는 `external-secrets` 애플리케이션 Webhook의 세부 사항을 구성합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `certificateCheckInterval` | duration | `certificateCheckInterval` 은 인증서의 유효성을 확인하도록 폴링 간격을 구성합니다. | 5m | 선택 사항 |

#### 11.9.16. certManagerConfig

`certManagerConfig` 필드는 `cert-manager` Operator 설정을 구성합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `mode` | string | `mode` 는 `Enabled` 또는 `Disabled` 로 표시할 수 있는 기본 제공 `cert-controller` 대신 인증서 관리에 cert-manager를 사용할지 여부를 지정합니다. `Enabled` 로 설정된 경우 Webhook 서버 및 기타 구성 요소의 인증서를 가져오는 데 `cert-manager` 를 사용합니다. `Disabled` 로 설정된 경우 `cert-controller` 를 사용하여 웹 후크 서버의 인증서를 가져옵니다. `비활성화` 는 기본 동작입니다. | false | enum: [true false] 필수 항목 |
| `injectAnnotations` | string | `injectAnnotations` 는 `cert-manager.io/inject-ca-from` 주석을 Webhook 및 CRD(사용자 정의 리소스 정의)에 추가하여 `cert-manager` Operator 인증 기관(CA)을 사용하여 Webhook를 자동으로 구성합니다. 이를 위해서는 `cert-manager` Operator에서 CA Injector를 활성화해야 합니다. 이 필드를 `true` 또는 `false` 로 설정합니다. 이 필드를 설정하면 이 필드를 변경할 수 없습니다. | false | enum: [true false] 선택 사항 |
| `issuerRef` | ObjectReference | `issuerRef` 에는 인증서를 가져오는 데 사용되는 참조된 오브젝트의 세부 정보가 포함되어 있습니다. 클러스터 범위 `cert-manager` Operator 발행자를 사용하지 않는 한 `external-secrets` 네임스페이스에 오브젝트가 있어야 합니다. |  | 필수 항목 |
| `certificateDuration` | duration | `certificateDuration` 은 Webhook 인증서의 유효 기간을 설정합니다. | 8760h | 선택 사항 |
| `certificateRenewBefore` | duration | `certificateRenewBefore` 는 만료 전에 Webhook 인증서를 갱신할 시간을 설정합니다. | 30m | 선택 사항 |

#### 11.9.17. certProvidersConfig

`certProvidersConfig` 는 Webhook 및 플러그인의 TLS 인증서를 관리하는 데 사용되는 인증서 공급자에 대한 구성을 정의합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `certManager` | object | `certManager` 는 `cert-manager` 공급자 관련 구성을 정의합니다. |  | 선택 사항 |

#### 11.9.18. objectReference

`ObjectReference` 필드는 이름, 종류 및 그룹으로 오브젝트를 참조합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `name` | string | `name` 은 참조되는 리소스의 이름을 지정합니다. |  | 최대 길이는 253자입니다. 최소 길이는 1자입니다. 필수 항목 |
| `kind` | string | `kind` 는 참조되는 리소스의 종류를 지정합니다. |  | 최대 길이는 253자입니다. 최소 길이는 1자입니다. 선택 사항 |
| `group` | string | `group` 은 참조되는 리소스 그룹을 지정합니다. |  | 최대 길이는 253자입니다. 최소 길이는 1자입니다. 선택 사항 |

#### 11.9.19. secretReference

`secretReference` 필드는 사용된 동일한 네임스페이스에 지정된 이름이 있는 보안을 나타냅니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `name` | string | `name` 은 참조되는 시크릿 리소스의 이름을 지정합니다. |  | 최대 길이는 253입니다. 최소 길이는 1입니다. 필수 항목 |

#### 11.9.20. condition

`condition` 필드에는 `external-secrets` 배포 상태에 대한 정보가 있습니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `type` | string | `type` 에는 배포 조건이 포함됩니다. |  | 필수 항목 |
| `status` | ConditionStatus | `status` 에는 배포 조건의 상태가 포함됩니다. |  |  |
| `message` | string | `message` 는 배포 상태에 대한 세부 정보를 제공합니다. |  |  |

#### 11.9.21. conditionalStatus

`conditionalStatus` 필드에는 `external-secrets` 배포의 현재 상태에 대한 정보가 있습니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `conditions` | array | `조건에` 는 배포 현재 상태에 대한 정보가 포함되어 있습니다. |  |  |

#### 11.9.22. mode

`mode` 필드는 선택적 기능의 작동 상태를 나타냅니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `활성화됨` |  | enabled는 선택적 구성이 `활성화` 되었음을 나타냅니다. |  |  |
| `비활성화됨` |  | `disabled` 는 선택적 구성이 비활성화되었음을 나타냅니다. |  |  |

#### 11.9.23. pluginsConfig

`pluginsConfig` 는 선택적 플러그인을 구성합니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `bitwardenSecretManagerProvider` | object | `bitwardenSecretManagerProvider` 는 ' `bitwarden-secrets-manager` '로 연결하기 위한 bitwarden-secrets-manager 공급자 플러그인을 활성화합니다. |  | 선택 사항 |

#### 11.9.24. proxyConfig

`proxyConfig` 에는 피연산자 컨테이너에서 사용할 수 있고 Operator에서 환경 변수로 관리하는 프록시 구성이 있습니다.

| 필드 | 유형 | 설명 | 기본 | 검증 |
| --- | --- | --- | --- | --- |
| `httpProxy` | string | `httpProxy` 필드에는 HTTP 요청에 대한 프록시 URL이 포함되어 있습니다. 이 필드는 최대 2048자를 가질 수 있습니다. |  | 최대 길이는 2048자입니다. 최소 길이는 0자입니다. 선택 사항 |
| `httpsProxy` | string | `httpsProxy` 필드에는 HTTPS 요청을 위한 프록시 URL이 포함되어 있습니다. 이 필드는 최대 2048자를 가질 수 있습니다. |  | 최대 길이는 2048자입니다. 최소 길이는 0자입니다. 선택 사항 |
| `noProxy` | string | `noProxy` 필드는 쉼표로 구분된 호스트 이름, CIDR(Classless inter-domain routings) 및 IP 주소 또는 프록시를 사용하지 않아야 하는 세 가지 주소의 조합입니다. 이 필드는 최대 4096자를 포함할 수 있습니다. |  | 최대 길이는 4096자입니다. 최소 길이는 0자입니다. 선택 사항 |

### 11.10. 커뮤니티 External Secrets Operator에서 Red Hat OpenShift용 외부 Secrets Operator로 마이그레이션

커뮤니티 External Secrets Operator에서 Red Hat OpenShift 지원 버전의 External Secrets Operator로 마이그레이션합니다. 이 변환은 엔터프라이즈급 지원과 외부 시크릿 관리를 위한 원활한 통합을 제공합니다.

다음 마이그레이션 버전이 완전히 테스트되었습니다.

| 업스트림 버전 | 설치 방법 | 다운스트림 버전 |
| --- | --- | --- |
| 0.11.0 | OLM | v1.0.0 GA |
| 0.19.0 | Helm | v1.0.0 GA |

참고

마이그레이션은 롤백을 지원하지 않습니다.

참고

External Secrets Operator for Red Hat OpenShift는 업스트림 버전 0.19.0을 기반으로 합니다. 상위 버전의 External Secrets Operator에서 마이그레이션하지 마십시오.

#### 11.10.1. 커뮤니티 외부 시크릿 Operator 삭제

기존 애플리케이션이 완전히 제거되도록 커뮤니티 Operator의 구성 리소스를 삭제합니다. 이 작업을 수행하면 Red Hat OpenShift용 외부 Secrets Operator를 설치하기 전에 충돌이 발생하지 않습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 로그인해야 합니다.

아래 명령줄 툴이 설치되어 구성되어 있어야 합니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 커뮤니티 Operator의 `네임스페이스` 를 찾습니다.

```shell-session
$ oc get operatorconfigs.operator.external-secrets.io -A
```

다음은 `네임스페이스` 를 찾는 예입니다.

```shell-session
NAMESPACE             NAME        AGE
external-secrets      cluster     9m18s
```

다음 명령을 실행하여 `operatorconfig` CR(사용자 정의 resrouce)을 삭제합니다.

```shell-session
$ oc delete operatorconfig <config_name> -n <operator_namespace>
```

검증

`operatorconfig` CR이 삭제되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get operatorconfig -n <operator_namespace>
```

명령에서 `리소스를 찾을 수 없습니다`.

이전 Webhook가 삭제되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get validatingwebhookconfigurations | grep external-secrets
```

```shell-session
$ oc get mutatingwebhookconfigurations | grep external-secrets
```

명령에서 결과를 반환하지 않아야 합니다.

#### 11.10.2. 커뮤니티 외부 시크릿 Operator 설치 제거

Red Hat OpenShift용 외부 Secret Operator로 마이그레이션한 후 충돌 또는 실수로 재생성하지 않도록 커뮤니티 외부 시크릿 Operator를 설치 제거합니다.

다시 생성되거나 새 보안과 충돌하지 않도록 커뮤니티 외부 시크릿 Operator를 설치 제거해야 합니다. 설치 제거 단계는 커뮤니티 외부 시크릿 Operator 설치 방법에 따라 다르지만 사전 요구 사항은 각각에 대해 동일합니다.

#### 11.10.2.1. helm installed community External Secrets Operator 설치 제거

Helm을 사용하여 설치된 커뮤니티 외부 Secrets Operator를 제거합니다. 이를 통해 리소스를 확보하고 클러스터에 대한 클린 환경을 유지 관리할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 로그인해야 합니다.

`operatorconfig` CR(사용자 정의 리소스)을 삭제해야 합니다.

프로세스

Red Hat OpenShift용 외부 Secrets Operator를 설치합니다. `external-secrets-operator` 네임스페이스는 null이어야 합니다.

다음 명령을 실행하여 외부 Secrets Operator를 삭제합니다.

```shell-session
$ oc helm delete <release_name> -n <operator_namespace>
```

참고

다음 명령을 사용하면 모든 CRD(Custom Resource Definitions) 및 CR을 삭제할 수 있습니다. 네임스페이스 `external-secrets-operator` 가 비어 있으면 먼저 다운스트림 Operator를 설치하는 것이 좋습니다.

```shell
helm delete
```

#### 11.10.2.2. Operator Lifecylce Manager 설치 제거 커뮤니티 External Secrets Operator

OLM(Operator Lifecycle Manager) 서브스크립션을 통해 설치한 커뮤니티 외부 시크릿 Operator를 제거합니다. 이를 통해 리소스를 확보하고 클러스터에 대한 클린 환경을 유지 관리할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 로그인해야 합니다.

`operatorconfig` CR을 삭제해야 합니다.

프로세스

다음 명령을 실행하여 서브스크립션 이름을 찾습니다.

```shell-session
$ oc get subscription -n <operator_namespace> | grep external-secrets
```

다음 명령을 실행하여 서브스크립션을 삭제합니다.

```shell-session
$ oc delete subscription <subscription_name> -n <operator_namespace>
```

다음 명령을 실행하여 `ClusterServiceVersion` 을 삭제합니다.

```shell-session
$ oc delete csv <csv_name> -n <operator_namespace>
```

#### 11.10.2.3. 원시 매니페스트가 설치된 커뮤니티 외부 시크릿 Operator 설치 제거

원시 매니페스트에서 설치한 커뮤니티 외부 Secrets Operator를 제거합니다. 이를 통해 리소스를 확보하고 클러스터에 대한 클린 환경을 유지 관리할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 로그인해야 합니다.

`operatorconfig` CR을 삭제해야 합니다.

프로세스

원시 매니페스트에서 설치한 communiity External Secrets Operator를 제거하려면 다음 명령을 실행합니다.

```shell-session
$ oc delete -f /path/to/your/old/manifests.yaml -n <operator_namespace>
```

#### 11.10.3. Red Hat OpenShift용 외부 Secrets Operator 설치

커뮤니티 버전을 정리한 후 Red Hat OpenShift용 External Secrets Operator를 설치합니다. 이렇게 하면 클러스터에서 시크릿을 관리하기 위해 공식적으로 지원되는 서비스가 설정됩니다. 자세한 내용은 외부 Secrets Operator for Red Hat OpenShift 설치를 참조하십시오.

#### 11.10.4. ExternalSecretsConfig Operator 생성

코어 `external-secrets` 구성 요소를 설치하고 구성할 `ExternalSecretsConfig` 리소스를 생성합니다. 이 설정은 Bitwarden 및 cert-manager 지원과 같은 기능이 올바르게 활성화되도록 하는 데 도움이 됩니다.

사전 요구 사항

External Secrets Operator for Red Hat OpenShift가 설치되어 있습니다.

cert-manager Operator for Red Hat OpenShift가 설치되어 있습니다.

`cluster-admin` 권한이 있는 클러스터에 액세스할 수 있습니다.

프로세스

다음 내용으로 YAML 파일을 정의하여 `externalsecretsconfig` 파일을 생성합니다.

```plaintext
apiVersion: operator.openshift.io/v1alpha1
kind: ExternalSecretsConfig
metadata:
  labels:
    app.kubernetes.io/name: cluster
  name: cluster
spec:
  appConfig:
    logLevel: 3
  webhookConfig:
    certificateCheckInterval: 5m0s
  controllerConfig:
    certProvider:
      certManager:
        certificateDuration: 8760h0m0s
        certificateRenewBefore: 30m0s
        injectAnnotations: "true"
        issuerRef:
          group: cert-manager.io
          kind: Issuer
          name: _<created_issuer_name>_
    mode: Enabled
    networkPolicies:
    - componentName: ExternalSecretsCoreController
      egress:
      - ports:
        - port: 443
          protocol: TCP
        - port: 9998
          protocol: TCP
        name: allow-external-secrets-egress
    plugins:
      bitwardenSecretManagerProvider:
        mode: Enabled
```

다음 명령을 실행하여 `ExternalSecretsConfig` 오브젝트를 생성합니다.

```shell-session
$ oc create -f externalsecretsconfig.yaml
```

검증

모든 CR(사용자 정의 리소스)이 있고 API가 `v1beta1` 대신 `v1` 을 사용하고 있는지 확인합니다. CR은 유지되며 새 Operator에 의해 자동으로 변환됩니다.

`external-secrets` Pod가 `실행 중인지` 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pods -n external-secret
```

다음은 `external-secrets` Pod가 `실행 중인` 상태인 예제 출력입니다.

```shell-session
NAME                                          READY        STATUS        RESTARTS     AGE
bitwarden-sdk-server-5b4cf48766-w7zp7         1/1          Running       0            5m
external-secrets-5854b85dd5-m6zf9             1/1          Running       0            5m
external-secrets-webhook-5cb85b8fdb-6jtqb     1/1          Running       0            5m
```

`SecretStore` CR이 있는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get secretstores.external-secrets.io -A
```

다음은 `SecretStore` 가 있는지 확인하는 출력의 예입니다.

```shell-session
NAMESPACE               NAME                         AGE         STATUS      CAPABILITIES    READY
external-secrets-1      gcp-store                    18min       Valid       ReadWrite       True
external-secrets-2      aws-secretstore              11min       Valid       ReadWrite       True
external-secrets        bitwarden-secretsmanager     20min       Valid       Readwrite       True
```

`ExternalSecret` CR이 있는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get externalsecrets.external-secrets.io -A
```

다음은 `SecretStore` 가 있는지 확인하는 출력의 예입니다.

```shell-session
NAMESPACE             NAME                    STORE                      REFRESH INTERVAL    STATUS          READY
external-secrets-1    gcp-externalsecret      gcp-store                  1hr                 SecretSynced    True
external-secrets-2    aws-external-secret     aws-secret-store           1hr                 SecretSynced    True
external-secrets      bitwarden               bitwarden-secretsmanager   1hr                 SecretSynced    True
```

`SecretStore` 가 `apiVersion: external-secrets.io/v1` 인지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get secretstores.external-secrets.io -n external-secrets-1 gcp-store -o yaml
```

다음은 `SecretStore` 가 `apiVersion: external-secrets.io/v1` 인 예제 출력입니다.

```plaintext
apiVersion: external-secrets.io/v1
kind: SecretStore
metadata:
  creationTimestamp: "2025-10-27T11:38:19Z"
  generation: 1
  name: gcp-store
  namespace: external-secrets-1
  resourceVersion: "104519"
  uid: 7bccb0cc-2557-4f4a-9caa-1577f0108f4b
spec:
.
.
.
status:
  capabilities: ReadWrite
  conditions:
  - lastTransitionTime: "2025-10-27T11:38:19Z"
    message: store validated
    reason: Valid
    status: "True"
    type: Ready
```

`ExternalSecret` 이 `apiVersion: external-secrets.io/v1` 인지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get externalsecrets.external-secrets.io -n external-secrets-1 gcp-externalsecret -o yaml
```

`ExternalSecret` 이 `apiVersion: external-secrets.io/v1` 인 예제 출력은 다음과 같습니다.

```plaintext
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  creationTimestamp: "2025-10-27T11:39:03Z"
  generation: 1
  name: gcp-externalsecret
  namespace: external-secrets-1
  resourceVersion: "104532"
  uid: 93a3295a-a3ad-4304-90e1-1328d951e5fb
spec:
.
.
.
status:
  binding:
    name: k8s-secret-gcp
  conditions:
  - lastTransitionTime: "2025-10-27T11:39:03Z"
    message: secret synced
    reason: SecretSynced
    status: "True"
    type: Ready
  refreshTime: "2025-10-27T12:13:15Z"
  syncedResourceVersion: 1-f47fe3c0b255b6dd8047cdffa772587bb829efe7a1cb70febeda2eb2
```

## 12장. 감사 로그 보기

OpenShift Container Platform 감사에서는 시스템의 개별 사용자, 관리자 또는 기타 구성 요소가 시스템에 영향을 준 활동 시퀀스를 설명하는 보안 관련 레코드 집합을 제공합니다.

### 12.1. API 감사 로그 정보

감사는 API 서버 수준에서 작동하며 서버로 들어오는 모든 요청을 기록합니다. 각 감사 로그에는 다음 정보가 포함됩니다.

| 필드 | 설명 |
| --- | --- |
| `level` | 이벤트가 생성된 감사 수준입니다. |
| `auditID` | 각 요청에 생성되는 고유 감사 ID입니다. |
| `stage` | 이 이벤트 인스턴스가 생성되었을 때의 요청 처리 단계입니다. |
| `requestURI` | 클라이언트에서 서버로 보낸 요청 URI입니다. |
| `verb` | 요청과 관련된 Kubernetes 동사입니다. 리소스가 아닌 요청의 경우 소문자 HTTP 메서드입니다. |
| `user` | 인증된 사용자 정보입니다. |
| `impersonatedUser` | 선택 사항: 요청에서 다른 사용자를 가장하는 경우 가장된 사용자 정보입니다. |
| `sourceIPs` | 선택 사항: 요청이 발생한 소스 IP 및 중간 프록시입니다. |
| `userAgent` | 선택 사항: 클라이언트에서 보고한 사용자 에이전트 문자열입니다. 사용자 에이전트는 클라이언트에서 제공하며 신뢰할 수 없습니다. |
| `objectRef` | 선택 사항: 이 요청의 대상이 되는 오브젝트 참조입니다. 이는 `List` 유형의 요청 또는 리소스가 아닌 요청에는 적용되지 않습니다. |
| `responseStatus` | 선택 사항: `ResponseObject` 가 `Status` 유형이 아닌 경우에도 채워지는 응답 상태입니다. 성공적인 응답을 위해 여기에는 코드만 포함됩니다. 상태 유형이 아닌 오류 응답의 경우 오류 메시지가 자동으로 채워집니다. |
| `requestObject` | 선택 사항: 요청의 API 오브젝트로, JSON 형식으로 되어 있습니다. `RequestObject` 는 버전 변환, 기본값 설정, 승인 또는 병합 전에 요청에 있는 그대로(JSON으로 다시 인코딩될 수 있음) 기록됩니다. 외부 버전이 지정된 오브젝트 유형이며 그 자체로는 유효한 오브젝트가 아닐 수 있습니다. 리소스가 아닌 요청의 경우 생략되며 요청 수준 이상에서만 기록됩니다. |
| `responseObject` | 선택 사항: 응답에서 반환된 API 오브젝트로, JSON 형식으로 되어 있습니다. `ResponseObject` 는 외부 유형으로 변환된 후 기록되고 JSON으로 직렬화됩니다. 리소스가 아닌 요청의 경우 생략되며 응답 수준에서만 기록됩니다. |
| `requestReceivedTimestamp` | 요청이 API 서버에 도달한 시간입니다. |
| `stageTimestamp` | 요청이 현재 감사 단계에 도달한 시간입니다. |
| `annotations` | 선택 사항: 인증, 권한 부여 및 승인 플러그인을 포함하여 요청 서비스 체인에서 호출한 플러그인에 의해 설정될 수 있는 감사 이벤트와 함께 저장되는 구조화되지 않은 키 값 맵입니다. 이러한 주석은 감사 이벤트용이며 제출된 오브젝트의 `metadata.annotations` 와 일치하지 않습니다. 키는 이름 충돌을 방지하기 위해 알림 구성 요소를 고유하게 식별해야 합니다(예: `podsecuritypolicy.admission.k8s.io/policy)` . 값은 짧아야 합니다. 주석은 메타데이터 수준에 포함됩니다. |

```plaintext
{"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"Metadata","auditID":"ad209ce1-fec7-4130-8192-c4cc63f1d8cd","stage":"ResponseComplete","requestURI":"/api/v1/namespaces/openshift-kube-controller-manager/configmaps/cert-recovery-controller-lock?timeout=35s","verb":"update","user":{"username":"system:serviceaccount:openshift-kube-controller-manager:localhost-recovery-client","uid":"dd4997e3-d565-4e37-80f8-7fc122ccd785","groups":["system:serviceaccounts","system:serviceaccounts:openshift-kube-controller-manager","system:authenticated"]},"sourceIPs":["::1"],"userAgent":"cluster-kube-controller-manager-operator/v0.0.0 (linux/amd64) kubernetes/$Format","objectRef":{"resource":"configmaps","namespace":"openshift-kube-controller-manager","name":"cert-recovery-controller-lock","uid":"5c57190b-6993-425d-8101-8337e48c7548","apiVersion":"v1","resourceVersion":"574307"},"responseStatus":{"metadata":{},"code":200},"requestReceivedTimestamp":"2020-04-02T08:27:20.200962Z","stageTimestamp":"2020-04-02T08:27:20.206710Z","annotations":{"authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":"RBAC: allowed by ClusterRoleBinding \"system:openshift:operator:kube-controller-manager-recovery\" of ClusterRole \"cluster-admin\" to ServiceAccount \"localhost-recovery-client/openshift-kube-controller-manager\""}}
```

### 12.2. 감사 로그 보기

각 컨트롤 플레인 노드에 대한 OpenShift API 서버, Kubernetes API 서버, OpenShift OAuth API 서버 및 OpenShift OAuth 서버의 로그를 볼 수 있습니다.

프로세스

감사 로그를 보려면 다음을 수행합니다.

OpenShift API 서버 감사 로그를 확인합니다.

각 컨트롤 플레인 노드에 사용할 수 있는 OpenShift API 서버 감사 로그를 나열합니다.

```shell-session
$ oc adm node-logs --role=master --path=openshift-apiserver/
```

```shell-session
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit-2021-03-09T00-12-19.834.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit-2021-03-09T00-11-49.835.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit-2021-03-09T00-13-00.128.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit.log
```

노드 이름과 로그 이름을 제공하여 특정 OpenShift API 서버 감사 로그를 확인합니다.

```shell-session
$ oc adm node-logs <node_name> --path=openshift-apiserver/<log_name>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc adm node-logs ci-ln-m0wpfjb-f76d1-vnb5x-master-0 --path=openshift-apiserver/audit-2021-03-09T00-12-19.834.log
```

```shell-session
{"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"Metadata","auditID":"381acf6d-5f30-4c7d-8175-c9c317ae5893","stage":"ResponseComplete","requestURI":"/metrics","verb":"get","user":{"username":"system:serviceaccount:openshift-monitoring:prometheus-k8s","uid":"825b60a0-3976-4861-a342-3b2b561e8f82","groups":["system:serviceaccounts","system:serviceaccounts:openshift-monitoring","system:authenticated"]},"sourceIPs":["10.129.2.6"],"userAgent":"Prometheus/2.23.0","responseStatus":{"metadata":{},"code":200},"requestReceivedTimestamp":"2021-03-08T18:02:04.086545Z","stageTimestamp":"2021-03-08T18:02:04.107102Z","annotations":{"authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":"RBAC: allowed by ClusterRoleBinding \"prometheus-k8s\" of ClusterRole \"prometheus-k8s\" to ServiceAccount \"prometheus-k8s/openshift-monitoring\""}}
```

Kubernetes API 서버 감사 로그를 확인합니다.

각 컨트롤 플레인 노드에 사용할 수 있는 Kubernetes API 서버 감사 로그를 나열합니다.

```shell-session
$ oc adm node-logs --role=master --path=kube-apiserver/
```

```shell-session
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit-2021-03-09T14-07-27.129.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit-2021-03-09T19-24-22.620.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit-2021-03-09T18-37-07.511.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit.log
```

노드 이름과 로그 이름을 제공하여 특정 Kubernetes API 서버 감사 로그를 확인합니다.

```shell-session
$ oc adm node-logs <node_name> --path=kube-apiserver/<log_name>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc adm node-logs ci-ln-m0wpfjb-f76d1-vnb5x-master-0 --path=kube-apiserver/audit-2021-03-09T14-07-27.129.log
```

```shell-session
{"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"Metadata","auditID":"cfce8a0b-b5f5-4365-8c9f-79c1227d10f9","stage":"ResponseComplete","requestURI":"/api/v1/namespaces/openshift-kube-scheduler/serviceaccounts/openshift-kube-scheduler-sa","verb":"get","user":{"username":"system:serviceaccount:openshift-kube-scheduler-operator:openshift-kube-scheduler-operator","uid":"2574b041-f3c8-44e6-a057-baef7aa81516","groups":["system:serviceaccounts","system:serviceaccounts:openshift-kube-scheduler-operator","system:authenticated"]},"sourceIPs":["10.128.0.8"],"userAgent":"cluster-kube-scheduler-operator/v0.0.0 (linux/amd64) kubernetes/$Format","objectRef":{"resource":"serviceaccounts","namespace":"openshift-kube-scheduler","name":"openshift-kube-scheduler-sa","apiVersion":"v1"},"responseStatus":{"metadata":{},"code":200},"requestReceivedTimestamp":"2021-03-08T18:06:42.512619Z","stageTimestamp":"2021-03-08T18:06:42.516145Z","annotations":{"authentication.k8s.io/legacy-token":"system:serviceaccount:openshift-kube-scheduler-operator:openshift-kube-scheduler-operator","authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":"RBAC: allowed by ClusterRoleBinding \"system:openshift:operator:cluster-kube-scheduler-operator\" of ClusterRole \"cluster-admin\" to ServiceAccount \"openshift-kube-scheduler-operator/openshift-kube-scheduler-operator\""}}
```

OpenShift OAuth API 서버 감사 로그를 확인합니다.

각 컨트롤 플레인 노드에 사용할 수 있는 OpenShift OAuth API 서버 감사 로그를 나열합니다.

```shell-session
$ oc adm node-logs --role=master --path=oauth-apiserver/
```

```shell-session
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit-2021-03-09T13-06-26.128.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit-2021-03-09T18-23-21.619.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit-2021-03-09T17-36-06.510.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit.log
```

노드 이름과 로그 이름을 제공하여 특정 OpenShift OAuth API 서버 감사 로그를 확인합니다.

```shell-session
$ oc adm node-logs <node_name> --path=oauth-apiserver/<log_name>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc adm node-logs ci-ln-m0wpfjb-f76d1-vnb5x-master-0 --path=oauth-apiserver/audit-2021-03-09T13-06-26.128.log
```

```shell-session
{"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"Metadata","auditID":"dd4c44e2-3ea1-4830-9ab7-c91a5f1388d6","stage":"ResponseComplete","requestURI":"/apis/user.openshift.io/v1/users/~","verb":"get","user":{"username":"system:serviceaccount:openshift-monitoring:prometheus-k8s","groups":["system:serviceaccounts","system:serviceaccounts:openshift-monitoring","system:authenticated"]},"sourceIPs":["10.0.32.4","10.128.0.1"],"userAgent":"dockerregistry/v0.0.0 (linux/amd64) kubernetes/$Format","objectRef":{"resource":"users","name":"~","apiGroup":"user.openshift.io","apiVersion":"v1"},"responseStatus":{"metadata":{},"code":200},"requestReceivedTimestamp":"2021-03-08T17:47:43.653187Z","stageTimestamp":"2021-03-08T17:47:43.660187Z","annotations":{"authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":"RBAC: allowed by ClusterRoleBinding \"basic-users\" of ClusterRole \"basic-user\" to Group \"system:authenticated\""}}
```

OpenShift OAuth 서버 감사 로그를 확인합니다.

각 컨트롤 플레인 노드에 사용할 수 있는 OpenShift OAuth 서버 감사 로그를 나열합니다.

```shell-session
$ oc adm node-logs --role=master --path=oauth-server/
```

```shell-session
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit-2022-05-11T18-57-32.395.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-0 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit-2022-05-11T19-07-07.021.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-1 audit.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit-2022-05-11T19-06-51.844.log
ci-ln-m0wpfjb-f76d1-vnb5x-master-2 audit.log
```

노드 이름과 로그 이름을 지정하여 특정 OpenShift OAuth 서버 감사 로그를 확인합니다.

```shell-session
$ oc adm node-logs <node_name> --path=oauth-server/<log_name>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc adm node-logs ci-ln-m0wpfjb-f76d1-vnb5x-master-0 --path=oauth-server/audit-2022-05-11T18-57-32.395.log
```

```shell-session
{"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"Metadata","auditID":"13c20345-f33b-4b7d-b3b6-e7793f805621","stage":"ResponseComplete","requestURI":"/login","verb":"post","user":{"username":"system:anonymous","groups":["system:unauthenticated"]},"sourceIPs":["10.128.2.6"],"userAgent":"Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0","responseStatus":{"metadata":{},"code":302},"requestReceivedTimestamp":"2022-05-11T17:31:16.280155Z","stageTimestamp":"2022-05-11T17:31:16.297083Z","annotations":{"authentication.openshift.io/decision":"error","authentication.openshift.io/username":"kubeadmin","authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":""}}
```

`authentication.openshift.io/decision` 주석에 사용 가능한 값은 `allow`, `deny` 또는 `error` 입니다.

### 12.3. 감사 로그 필터링

다음 명령또는 다른 JSON 구문 분석 툴을 사용하여 API 서버 감사 로그를 필터링할 수 있습니다.

```shell
jq
```

참고

설정된 감사 로그 정책에 의해 API 서버 감사 로그에 기록되는 정보의 양을 제어할 수 있습니다.

다음 절차에서는 다음 명령을 사용하여 컨트롤 플레인 노드 `node-1.example.com` 에서 감사 로그를 필터링하는 예를 제공합니다. 다음 명령을 사용하는 방법에 대한 자세한 내요ㅇ은 jq 설명서 를 참조하십시오.

```shell
jq
```

```shell
jq
```

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

다음 명령을 설치했습니다.

```shell
jq
```

프로세스

사용자가 OpenShift API 서버 감사 로그를 필터링합니다.

```shell-session
$ oc adm node-logs node-1.example.com  \
  --path=openshift-apiserver/audit.log \
  | jq 'select(.user.username == "myusername")'
```

사용자 에이전트가 OpenShift API 서버 감사 로그를 필터링합니다.

```shell-session
$ oc adm node-logs node-1.example.com  \
  --path=openshift-apiserver/audit.log \
  | jq 'select(.userAgent == "cluster-version-operator/v0.0.0 (linux/amd64) kubernetes/$Format")'
```

특정 API 버전 별로 Kubernetes API 서버 감사 로그를 필터링하고 사용자 에이전트만 출력합니다.

```shell-session
$ oc adm node-logs node-1.example.com  \
  --path=kube-apiserver/audit.log \
  | jq 'select(.requestURI | startswith("/apis/apiextensions.k8s.io/v1beta1")) | .userAgent'
```

동사 제외하여 OpenShift OAuth API 서버 감사 로그를 필터링합니다.

```shell-session
$ oc adm node-logs node-1.example.com  \
  --path=oauth-apiserver/audit.log \
  | jq 'select(.verb != "get")'
```

사용자 이름을 식별하고 오류와 함께 실패한 이벤트로 OpenShift OAuth 서버 감사 로그를 필터링합니다.

```shell-session
$ oc adm node-logs node-1.example.com  \
  --path=oauth-server/audit.log \
  | jq 'select(.annotations["authentication.openshift.io/username"] != null and .annotations["authentication.openshift.io/decision"] == "error")'
```

### 12.4. 감사 로그 수집

must-gather 툴을 사용하여 Red Hat Support를 검토하거나 보낼 수 있는 클러스터 디버깅을 위한 감사 로그를 수집할 수 있습니다.

프로세스

`-- /usr/bin/gather_audit_logs`:를 사용하여 아래 명령을 실행합니다.

```shell
oc adm must-gather
```

```shell-session
$ oc adm must-gather -- /usr/bin/gather_audit_logs
```

작업 디렉토리에서 생성된 `must-gather` 디렉토리에서 압축 파일을 만듭니다. 예를 들어 Linux 운영 체제를 사용하는 컴퓨터에서 다음 명령을 실행합니다.

```shell-session
$ tar cvaf must-gather.tar.gz must-gather.local.472290403699006248
```

1. `must-gather-local.472290403699006248` 을 실제 디렉터리 이름으로 교체합니다.

압축 파일을 Red Hat 고객 포털 의 고객 지원 페이지의 지원

케이스에 첨부합니다.

### 12.5. 추가 리소스

must-gather 툴

API 감사 로그 이벤트 구조

감사 로그 정책 구성

## 13장. 감사 로그 정책 구성

이제 사용할 감사 로그 정책 프로필을 선택하여 API 서버 감사 로그에 기록되는 정보의 양을 제어할 수 있습니다.

### 13.1. 감사 로그 정책 프로필 정보

감사 로그 프로필은 OpenShift API 서버, Kubernetes API 서버, OpenShift OAuth API 서버 및 OpenShift OAuth 서버로 들어오는 요청을 기록하는 방법을 정의합니다.

OpenShift Container Platform에서는 다음과 같이 사전 정의된 감사 정책 프로필을 제공합니다.

| Profile | 설명 |
| --- | --- |
| `Default` | 읽기 및 쓰기 요청에 대한 메타데이터만 기록합니다. OAuth 액세스 토큰 요청을 제외하고 요청 본문을 기록하지 않습니다. 이는 기본 정책입니다. |
| `WriteRequestBodies` | 모든 요청에 대한 메타데이터를 기록하는 것 외에도 API 서버에 대한 모든 쓰기 요청에 대한 요청 본문을 기록합니다( `생성` , `업데이트` , `패치` , `삭제` , `삭제` ). 이 프로필은 `Default` 프로필보다 리소스 오버헤드가 많습니다. [1] |
| `AllRequestBodies` | 모든 요청에 대한 메타데이터 기록 외에도 API 서버에 대한 모든 읽기 및 쓰기 요청( `get` , `list` , `create` , `update` , `patch` )의 요청 본문을 기록합니다. 이 프로필은 리소스 오버헤드가 가장 많습니다. [1] |
| `없음` | OAuth 액세스 토큰 요청 및 OAuth 인증 토큰 요청을 포함하여 요청이 기록되지 않습니다. 이 프로필이 설정되면 사용자 정의 규칙은 무시됩니다. 주의 문제를 해결할 때 유용할 수 있는 데이터를 로깅하지 않는 한 `None` 프로필을 사용하여 감사 로깅을 비활성화하지 마십시오. 감사 로깅을 비활성화하고 지원 상황이 발생하는 경우 감사 로깅을 활성화하고 문제를 재현하여 적절하게 해결해야 할 수 있습니다. |

`Secret`, `Route`, `OAuthClient` 오브젝트와 같은 중요한 리소스는 메타데이터 수준에서만 기록됩니다. OpenShift OAuth 서버 이벤트는 메타데이터 수준에서만 기록됩니다.

기본적으로 OpenShift Container Platform에서는 `Default` 감사 로그 프로필을 사용합니다. 요청 본문도 기록하는 다른 감사 정책 프로필을 사용할 수 있지만 CPU, 메모리, I/O와 같은 증가된 리소스 사용량을 알고 있어야 합니다.

### 13.2. 감사 로그 정책 구성

API 서버로 들어오는 요청을 기록할 때 사용할 감사 로그 정책을 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`APIServer` 리소스를 편집합니다.

```shell-session
$ oc edit apiserver cluster
```

`spec.audit.profile` 필드를 업데이트합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: APIServer
metadata:
...
spec:
  audit:
    profile: WriteRequestBodies
```

1. `Default`, `WriteRequestBodies`, `AllRequestBodies` 또는 `None` 으로 설정합니다. 기본 프로필은 `Default` 입니다.

주의

문제를 해결할 때 유용할 수 있는 데이터를 로깅하지 않는 한 `None` 프로필을 사용하여 감사 로깅을 비활성화하지 않는 것이 좋습니다. 감사 로깅을 비활성화하고 지원 상황이 발생하는 경우 적절하게 해결하려면 감사 로깅을 활성화하고 문제를 재현해야 할 수 있습니다.

파일을 저장하여 변경 사항을 적용합니다.

검증

Kubernetes API 서버 Pod의 새 버전이 출시되었는지 확인합니다. 모든 노드가 새 버전으로 업데이트되는 데 몇 분이 걸릴 수 있습니다.

```shell-session
$ oc get kubeapiserver -o=jsonpath='{range .items[0].status.conditions[?(@.type=="NodeInstallerProgressing")]}{.reason}{"\n"}{.message}{"\n"}'
```

Kubernetes API 서버의 `NodeInstallerProgressing` 상태 조건을 검토하여 모든 노드가 최신 버전인지 확인합니다. 업데이트가 성공적으로 실행되면 출력에 `AllNodesAtLatestRevision` 이 표시됩니다.

```shell-session
AllNodesAtLatestRevision
3 nodes are at revision 12
```

1. 이 예에서 최신 버전 번호는 `12` 입니다.

출력에 다음 메시지 중 하나와 유사한 메시지가 표시되면 업데이트가 계속 진행 중입니다. 몇 분 기다린 후 다시 시도합니다.

`3 nodes are at revision 11; 0 nodes have achieved new revision 12`

`2 nodes are at revision 11; 1 nodes are at revision 12`

### 13.3. 사용자 정의 규칙을 사용하여 감사 로그 정책 구성

사용자 정의 규칙을 정의하는 감사 로그 정책을 구성할 수 있습니다. 여러 그룹을 지정하고 해당 그룹에 사용할 프로필을 정의할 수 있습니다.

이러한 사용자 정의 규칙은 최상위 프로필 필드보다 우선합니다. 사용자 지정 규칙은 위에서 아래로 평가되고 일치하는 첫 번째 규칙이 적용됩니다.

중요

최상위 프로필 필드를 `None` 으로 설정하면 Kubernetes API 서버와 같은 API 서버는 사용자 정의 규칙을 무시하고 감사 로깅을 비활성화합니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`APIServer` 리소스를 편집합니다.

```shell-session
$ oc edit apiserver cluster
```

`spec.audit.customRules` 필드를 추가합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: APIServer
metadata:
...
spec:
  audit:
    customRules:
    - group: system:authenticated:oauth
      profile: WriteRequestBodies
    - group: system:authenticated
      profile: AllRequestBodies
    profile: Default
```

1. 하나 이상의 그룹을 추가하고 해당 그룹에 사용할 프로필을 지정합니다. 이러한 사용자 정의 규칙은 최상위 프로필 필드보다 우선합니다. 사용자 지정 규칙은 위에서 아래로 평가되고 일치하는 첫 번째 규칙이 적용됩니다.

2. `Default`, `WriteRequestBodies` 또는 `AllRequestBodies` 로 설정합니다. 이 최상위 프로필 필드를 설정하지 않으면 기본값은 `Default` 프로필입니다.

파일을 저장하여 변경 사항을 적용합니다.

검증

Kubernetes API 서버 Pod의 새 버전이 출시되었는지 확인합니다. 모든 노드가 새 버전으로 업데이트되는 데 몇 분이 걸릴 수 있습니다.

```shell-session
$ oc get kubeapiserver -o=jsonpath='{range .items[0].status.conditions[?(@.type=="NodeInstallerProgressing")]}{.reason}{"\n"}{.message}{"\n"}'
```

Kubernetes API 서버의 `NodeInstallerProgressing` 상태 조건을 검토하여 모든 노드가 최신 버전인지 확인합니다. 업데이트가 성공적으로 실행되면 출력에 `AllNodesAtLatestRevision` 이 표시됩니다.

```shell-session
AllNodesAtLatestRevision
3 nodes are at revision 12
```

1. 이 예에서 최신 버전 번호는 `12` 입니다.

출력에 다음 메시지 중 하나와 유사한 메시지가 표시되면 업데이트가 계속 진행 중입니다. 몇 분 기다린 후 다시 시도합니다.

`3 nodes are at revision 11; 0 nodes have achieved new revision 12`

`2 nodes are at revision 11; 1 nodes are at revision 12`

### 13.4. 감사 로깅 비활성화

OpenShift Container Platform에 대한 감사 로깅을 비활성화할 수 있습니다. 감사 로깅을 비활성화하면 OAuth 액세스 토큰 요청 및 OAuth 인증 토큰 요청도 기록되지 않습니다.

주의

문제를 해결할 때 유용할 수 있는 데이터를 로깅하지 않는 한 `None` 프로필을 사용하여 감사 로깅을 비활성화하지 않는 것이 좋습니다. 감사 로깅을 비활성화하고 지원 상황이 발생하는 경우 적절하게 해결하려면 감사 로깅을 활성화하고 문제를 재현해야 할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`APIServer` 리소스를 편집합니다.

```shell-session
$ oc edit apiserver cluster
```

`spec.audit.profile` 필드를 `None` 으로 설정합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: APIServer
metadata:
...
spec:
  audit:
    profile: None
```

참고

`spec.audit.customRules` 필드에 사용자 정의 규칙을 지정하여 특정 그룹에 대한 감사 로깅만 비활성화할 수도 있습니다.

파일을 저장하여 변경 사항을 적용합니다.

검증

Kubernetes API 서버 Pod의 새 버전이 출시되었는지 확인합니다. 모든 노드가 새 버전으로 업데이트되는 데 몇 분이 걸릴 수 있습니다.

```shell-session
$ oc get kubeapiserver -o=jsonpath='{range .items[0].status.conditions[?(@.type=="NodeInstallerProgressing")]}{.reason}{"\n"}{.message}{"\n"}'
```

Kubernetes API 서버의 `NodeInstallerProgressing` 상태 조건을 검토하여 모든 노드가 최신 버전인지 확인합니다. 업데이트가 성공적으로 실행되면 출력에 `AllNodesAtLatestRevision` 이 표시됩니다.

```shell-session
AllNodesAtLatestRevision
3 nodes are at revision 12
```

1. 이 예에서 최신 버전 번호는 `12` 입니다.

출력에 다음 메시지 중 하나와 유사한 메시지가 표시되면 업데이트가 계속 진행 중입니다. 몇 분 기다린 후 다시 시도합니다.

`3 nodes are at revision 11; 0 nodes have achieved new revision 12`

`2 nodes are at revision 11; 1 nodes are at revision 12`

## 14장. TLS 보안 프로필 설정

TLS 보안 프로필은 서버가 서버에 연결할 때 클라이언트가 사용할 수 있는 암호를 규제하는 방법을 제공합니다. 이렇게 하면 OpenShift Container Platform 구성 요소에서 알려진 비보안 프로토콜, 암호 또는 알고리즘을 허용하지 않는 암호화 라이브러리를 사용할 수 있습니다.

클러스터 관리자는 다음 구성 요소 각각에 사용할 TLS 보안 프로필을 선택할 수 있습니다.

Ingress 컨트롤러

컨트롤 플레인

여기에는 Kubernetes API 서버, Kubernetes 컨트롤러 관리자, Kubernetes 스케줄러, OpenShift API 서버, OpenShift OAuth API 서버, OpenShift OAuth 서버, etcd, Machine Config Operator 및 Machine Config Server가 포함됩니다.

Kubernetes API 서버의 HTTP 서버 역할을 하는 kubelet

### 14.1. TLS 보안 프로필 이해

TLS(Transport Layer Security) 보안 프로필을 사용하여 다양한 OpenShift Container Platform 구성 요소에 필요한 TLS 암호를 정의할 수 있습니다. OpenShift Container Platform TLS 보안 프로필은 Mozilla 권장 구성 을 기반으로 합니다.

각 구성 요소에 대해 다음 TLS 보안 프로필 중 하나를 지정할 수 있습니다.

| Profile | 설명 |
| --- | --- |
| `Old` | 이 프로필은 레거시 클라이언트 또는 라이브러리와 함께 사용하기 위한 것입니다. 프로필은 이전 버전과의 호환성 권장 구성을 기반으로 합니다. `Old` 프로파일에는 최소 TLS 버전 1.0이 필요합니다. 참고 Ingress 컨트롤러의 경우 최소 TLS 버전이 1.0에서 1.1로 변환됩니다. |
| `Intermediate` | 이 프로필은 Ingress 컨트롤러, kubelet 및 컨트롤 플레인의 기본 TLS 보안 프로필입니다. 프로필은 중간 호환성 권장 구성을 기반으로 합니다. `Intermediate` 프로필에는 최소 TLS 버전이 1.2가 필요합니다. 참고 이 프로필은 대부분의 클라이언트에서 권장되는 구성입니다. |
| `Modern` | 이 프로필은 이전 버전과의 호환성이 필요하지 않은 최신 클라이언트와 사용하기 위한 것입니다. 이 프로필은 최신 호환성 권장 구성을 기반으로 합니다. `Modern` 프로필에는 최소 TLS 버전 1.3이 필요합니다. |
| `사용자 지정` | 이 프로필을 사용하면 사용할 TLS 버전과 암호를 정의할 수 있습니다. 주의 `Custom` 프로파일을 사용할 때는 잘못된 구성으로 인해 문제가 발생할 수 있으므로 주의해야 합니다. |

참고

미리 정의된 프로파일 유형 중 하나를 사용하는 경우 유효한 프로파일 구성은 릴리스마다 변경될 수 있습니다. 예를 들어 릴리스 X.Y.Z에 배포된 중간 프로필을 사용하는 사양이 있는 경우 릴리스 X.Y.Z+1로 업그레이드하면 새 프로필 구성이 적용되어 롤아웃이 발생할 수 있습니다.

### 14.2. TLS 보안 프로필 세부 정보 보기

Ingress 컨트롤러, 컨트롤 플레인, kubelet 등 다음 각 구성 요소에 대해 사전 정의된 TLS 보안 프로필의 최소 TLS 버전 및 암호를 볼 수 있습니다.

중요

프로필에 대한 최소 TLS 버전 및 암호 목록의 효과적인 구성은 구성 요소마다 다를 수 있습니다.

프로세스

특정 TLS 보안 프로필의 세부 정보를 확인합니다.

```shell-session
$ oc explain <component>.spec.tlsSecurityProfile.<profile>
```

1. `<component>` 에 대해 `ingresscontroller`, `apiserver` 또는 `kubeletconfig` 를 지정합니다. `<profile>` 에 대해 `old`, `intermediate`, `custom` 을 지정합니다.

예를 들어 컨트롤 플레인의 `intermediate` 프로필에 포함된 암호를 확인하려면 다음을 수행합니다.

```shell-session
$ oc explain apiserver.spec.tlsSecurityProfile.intermediate
```

```shell-session
KIND:     APIServer
VERSION:  config.openshift.io/v1

DESCRIPTION:
    intermediate is a TLS security profile based on:
    https://wiki.mozilla.org/Security/Server_Side_TLS#Intermediate_compatibility_.28recommended.29
    and looks like this (yaml):
    ciphers: - TLS_AES_128_GCM_SHA256 - TLS_AES_256_GCM_SHA384 -
    TLS_CHACHA20_POLY1305_SHA256 - ECDHE-ECDSA-AES128-GCM-SHA256 -
    ECDHE-RSA-AES128-GCM-SHA256 - ECDHE-ECDSA-AES256-GCM-SHA384 -
    ECDHE-RSA-AES256-GCM-SHA384 - ECDHE-ECDSA-CHACHA20-POLY1305 -
    ECDHE-RSA-CHACHA20-POLY1305 - DHE-RSA-AES128-GCM-SHA256 -
    DHE-RSA-AES256-GCM-SHA384 minTLSVersion: TLSv1.2
```

구성 요소의 `tlsSecurityProfile` 필드에 대한 모든 세부 정보를 확인합니다.

```shell-session
$ oc explain <component>.spec.tlsSecurityProfile
```

1. `<component>` 에 대해 `ingresscontroller`, `apiserver` 또는 `kubeletconfig` 를 지정합니다.

예를 들어 Ingress 컨트롤러의 `tlsSecurityProfile` 필드의 모든 세부 정보를 확인하려면 다음을 수행합니다.

```shell-session
$ oc explain ingresscontroller.spec.tlsSecurityProfile
```

```shell-session
KIND:     IngressController
VERSION:  operator.openshift.io/v1

RESOURCE: tlsSecurityProfile <Object>

DESCRIPTION:
     ...

FIELDS:
   custom   <>
     custom is a user-defined TLS security profile. Be extremely careful using a
     custom profile as invalid configurations can be catastrophic. An example
     custom profile looks like this:
     ciphers: - ECDHE-ECDSA-CHACHA20-POLY1305 - ECDHE-RSA-CHACHA20-POLY1305 -
     ECDHE-RSA-AES128-GCM-SHA256 - ECDHE-ECDSA-AES128-GCM-SHA256 minTLSVersion:
     TLSv1.1

   intermediate <>
     intermediate is a TLS security profile based on:
     https://wiki.mozilla.org/Security/Server_Side_TLS#Intermediate_compatibility_.28recommended.29
     and looks like this (yaml):
     ...
   modern   <>
     modern is a TLS security profile based on:
     https://wiki.mozilla.org/Security/Server_Side_TLS#Modern_compatibility and
     looks like this (yaml):
     ...
     NOTE: Currently unsupported.

   old  <>
     old is a TLS security profile based on:
     https://wiki.mozilla.org/Security/Server_Side_TLS#Old_backward_compatibility
     and looks like this (yaml):
     ...
   type <string>
     ...
```

1. 여기에서는 `intermediate` 프로필의 암호 및 최소 버전을 나열합니다.

2. `modern` 프로필의 암호 및 최소 버전을 나열합니다.

3. `old` 프로필의 암호 및 최소 버전을 여기에서 나열합니다.

### 14.3. Ingress 컨트롤러의 TLS 보안 프로필 구성

Ingress 컨트롤러에 대한 TLS 보안 프로필을 구성하려면 `IngressController` CR(사용자 정의 리소스)을 편집하여 사전 정의된 또는 사용자 지정 TLS 보안 프로필을 지정합니다. TLS 보안 프로필이 구성되지 않은 경우 기본값은 API 서버에 설정된 TLS 보안 프로필을 기반으로 합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
 ...
spec:
  tlsSecurityProfile:
    old: {}
    type: Old
 ...
```

TLS 보안 프로필은 Ingress 컨트롤러의 TLS 연결에 대한 최소 TLS 버전과 TLS 암호를 정의합니다.

`Status.Tls Profile` 아래의 `IngressController` CR(사용자 정의 리소스) 및 `Spec.Tls Security Profile` 아래 구성된 TLS 보안 프로필에서 구성된 TLS 보안 프로필의 암호 및 최소 TLS 버전을 확인할 수 있습니다. `Custom` TLS 보안 프로필의 경우 특정 암호 및 최소 TLS 버전이 두 매개변수 아래에 나열됩니다.

참고

HAProxy Ingress 컨트롤러 이미지는 TLS `1.3` 및 `Modern` 프로필을 지원합니다.

Ingress Operator는 `Old` 또는 `Custom` 프로파일의 TLS `1.0` 을 `1.1` 로 변환합니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`openshift-ingress-operator` 프로젝트에서 `IngressController` CR을 편집하여 TLS 보안 프로필을 구성합니다.

```shell-session
$ oc edit IngressController default -n openshift-ingress-operator
```

`spec.tlsSecurityProfile` 필드를 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
 ...
spec:
  tlsSecurityProfile:
    type: Custom
    custom:
      ciphers:
      - ECDHE-ECDSA-CHACHA20-POLY1305
      - ECDHE-RSA-CHACHA20-POLY1305
      - ECDHE-RSA-AES128-GCM-SHA256
      - ECDHE-ECDSA-AES128-GCM-SHA256
      minTLSVersion: VersionTLS11
 ...
```

1. TLS 보안 프로필 유형(`Old`, `Intermediate` 또는 `Custom`)을 지정합니다. 기본값은 `Intermediate` 입니다.

2. 선택한 유형의 적절한 필드를 지정합니다.

`old: {}`

`intermediate: {}`

`Modern: {}`

`custom:`

3. `custom` 유형의 경우 TLS 암호화 목록 및 최소 허용된 TLS 버전을 지정합니다.

파일을 저장하여 변경 사항을 적용합니다.

검증

`IngressController` CR에 프로파일이 설정되어 있는지 확인합니다.

```shell-session
$ oc describe IngressController default -n openshift-ingress-operator
```

```shell-session
Name:         default
Namespace:    openshift-ingress-operator
Labels:       <none>
Annotations:  <none>
API Version:  operator.openshift.io/v1
Kind:         IngressController
 ...
Spec:
 ...
  Tls Security Profile:
    Custom:
      Ciphers:
        ECDHE-ECDSA-CHACHA20-POLY1305
        ECDHE-RSA-CHACHA20-POLY1305
        ECDHE-RSA-AES128-GCM-SHA256
        ECDHE-ECDSA-AES128-GCM-SHA256
      Min TLS Version:  VersionTLS11
    Type:               Custom
 ...
```

### 14.4. 컨트롤 플레인의 TLS 보안 프로필 구성

컨트롤 플레인에 대한 TLS 보안 프로필을 구성하려면 `APIServer` CR(사용자 정의 리소스)을 편집하여 사전 정의된 또는 사용자 지정 TLS 보안 프로필을 지정합니다. `APIServer` CR에서 TLS 보안 프로필을 설정하면 다음 컨트롤 플레인 구성 요소로 설정이 전파됩니다.

Kubernetes API 서버

Kubernetes 컨트롤러 관리자

Kubernetes 스케줄러

OpenShift API 서버

OpenShift OAuth API 서버

OpenShift OAuth 서버

etcd

Machine Config Operator

머신 구성 서버

TLS 보안 프로필이 구성되지 않은 경우 기본 TLS 보안 프로필은 `Intermediate` 입니다.

참고

Ingress 컨트롤러의 기본 TLS 보안 프로필은 API 서버에 설정된 TLS 보안 프로필을 기반으로 합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: APIServer
 ...
spec:
  tlsSecurityProfile:
    old: {}
    type: Old
 ...
```

TLS 보안 프로필은 컨트롤 플레인 구성 요소와 통신하는 데 필요한 최소 TLS 버전 및 TLS 암호를 정의합니다.

`Spec.Tls Security Profile` 의 `APIServer` CR(사용자 정의 리소스)에서 구성된 TLS 보안 프로필을 확인할 수 있습니다. `Custom` TLS 보안 프로필의 경우 특정 암호 및 최소 TLS 버전이 나열됩니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

기본 `APIServer` CR을 편집하여 TLS 보안 프로필을 구성합니다.

```shell-session
$ oc edit APIServer cluster
```

`spec.tlsSecurityProfile` 필드를 추가합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: APIServer
metadata:
  name: cluster
spec:
  tlsSecurityProfile:
    type: Custom
    custom:
      ciphers:
      - ECDHE-ECDSA-CHACHA20-POLY1305
      - ECDHE-RSA-CHACHA20-POLY1305
      - ECDHE-RSA-AES128-GCM-SHA256
      - ECDHE-ECDSA-AES128-GCM-SHA256
      minTLSVersion: VersionTLS11
```

1. TLS 보안 프로필 유형(`Old`, `Intermediate` 또는 `Custom`)을 지정합니다. 기본값은 `Intermediate` 입니다.

2. 선택한 유형의 적절한 필드를 지정합니다.

`old: {}`

`intermediate: {}`

`Modern: {}`

`custom:`

3. `custom` 유형의 경우 TLS 암호화 목록 및 최소 허용된 TLS 버전을 지정합니다.

파일을 저장하여 변경 사항을 적용합니다.

검증

TLS 보안 프로필이 `APIServer` CR에 설정되어 있는지 확인합니다.

```shell-session
$ oc describe apiserver cluster
```

```shell-session
Name:         cluster
Namespace:
 ...
API Version:  config.openshift.io/v1
Kind:         APIServer
 ...
Spec:
  Audit:
    Profile:  Default
  Tls Security Profile:
    Custom:
      Ciphers:
        ECDHE-ECDSA-CHACHA20-POLY1305
        ECDHE-RSA-CHACHA20-POLY1305
        ECDHE-RSA-AES128-GCM-SHA256
        ECDHE-ECDSA-AES128-GCM-SHA256
      Min TLS Version:  VersionTLS11
    Type:               Custom
 ...
```

TLS 보안 프로필이 `etcd` CR에 설정되어 있는지 확인합니다.

```shell-session
$ oc describe etcd cluster
```

```shell-session
Name:         cluster
Namespace:
 ...
API Version:  operator.openshift.io/v1
Kind:         Etcd
 ...
Spec:
  Log Level:         Normal
  Management State:  Managed
  Observed Config:
    Serving Info:
      Cipher Suites:
        TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
        TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
      Min TLS Version:           VersionTLS12
 ...
```

TLS 보안 프로필이 Machine Config Server Pod에 설정되어 있는지 확인합니다.

```shell-session
$ oc logs machine-config-server-5msdv -n openshift-machine-config-operator
```

```shell-session
# ...
I0905 13:48:36.968688       1 start.go:51] Launching server with tls min version: VersionTLS12 & cipher suites [TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256]
# ...
```

### 14.5. kubelet의 TLS 보안 프로필 구성

HTTP 서버 역할을 할 때 kubelet에 대한 TLS 보안 프로필을 구성하려면 `KubeletConfig` CR(사용자 정의 리소스)을 생성하여 특정 노드에 대해 사전 정의 또는 사용자 지정 TLS 보안 프로필을 지정합니다. TLS 보안 프로필이 구성되지 않은 경우 기본 TLS 보안 프로필은 `Intermediate` 입니다.

kubelet은 HTTP/GRPC 서버를 사용하여 명령을 Pod에 전송하고 로그를 수집하며 kubelet을 통해 Pod에서 exec 명령을 실행하는 Kubernetes API 서버와 통신합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
# ...
spec:
  tlsSecurityProfile:
    old: {}
    type: Old
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
# ...
```

구성된 노드의 `kubelet.conf` 파일에서 구성된 TLS 보안 프로필의 암호 및 최소 TLS 버전을 확인할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform에 로그인되어 있습니다.

프로세스

`KubeletConfig` CR을 생성하여 TLS 보안 프로필을 구성합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-kubelet-tls-security-profile
spec:
  tlsSecurityProfile:
    type: Custom
    custom:
      ciphers:
      - ECDHE-ECDSA-CHACHA20-POLY1305
      - ECDHE-RSA-CHACHA20-POLY1305
      - ECDHE-RSA-AES128-GCM-SHA256
      - ECDHE-ECDSA-AES128-GCM-SHA256
      minTLSVersion: VersionTLS11
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...
```

1. TLS 보안 프로필 유형(`Old`, `Intermediate` 또는 `Custom`)을 지정합니다. 기본값은 `Intermediate` 입니다.

2. 선택한 유형의 적절한 필드를 지정합니다.

`old: {}`

`intermediate: {}`

`Modern: {}`

`custom:`

3. `custom` 유형의 경우 TLS 암호화 목록 및 최소 허용된 TLS 버전을 지정합니다.

4. 선택 사항: TLS 보안 프로필을 적용하려는 노드의 머신 구성 풀 레이블을 지정합니다.

`KubeletConfig` 오브젝트를 생성합니다.

```shell-session
$ oc create -f <filename>
```

클러스터의 작업자 노드 수에 따라 구성된 노드가 하나씩 재부팅될 때까지 기다립니다.

검증

프로필이 설정되었는지 확인하려면 노드가 `Ready` 상태가 된 후 다음 단계를 수행합니다.

구성된 노드의 디버그 세션을 시작합니다.

```shell-session
$ oc debug node/<node_name>
```

디버그 쉘 내에서 `/host` 를 root 디렉터리로 설정합니다.

```shell-session
sh-4.4# chroot /host
```

`kubelet.conf` 파일을 확인합니다.

```shell-session
sh-4.4# cat /etc/kubernetes/kubelet.conf
```

```shell-session
"kind": "KubeletConfiguration",
  "apiVersion": "kubelet.config.k8s.io/v1beta1",
#...
  "tlsCipherSuites": [
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
  ],
  "tlsMinVersion": "VersionTLS12",
#...
```

## 15장. seccomp 프로필 구성

OpenShift Container Platform 컨테이너 또는 Pod는 하나 이상의 잘 정의된 작업을 수행하는 단일 애플리케이션을 실행합니다. 애플리케이션에는 일반적으로 기본 운영 체제 커널 API의 작은 하위 집합만 필요합니다. 보안 컴퓨팅 모드 seccomp는 사용 가능한 시스템 호출의 하위 집합만 사용하여 컨테이너에서 실행되는 프로세스를 제한하기 위해 사용할 수 있는 Linux 커널 기능입니다.

`restricted-v2` SCC는 4.20에서 새로 생성된 모든 Pod에 적용됩니다. 기본 seccomp 프로필 `runtime/default` 는 이러한 Pod에 적용됩니다.

seccomp 프로필은 디스크에 JSON 파일로 저장됩니다.

중요

seccomp 프로필은 권한 있는 컨테이너에 적용할 수 없습니다.

### 15.1. Pod에 적용되는 기본 seccomp 프로필 확인

OpenShift Container Platform에는 `runtime/default` 로 참조되는 기본 seccomp 프로필이 포함되어 있습니다. 4.20에서 새로 생성된 Pod에는 SCC(Security Context Constraint)가 `restricted-v2` 로 설정되어 있고 기본 seccomp 프로필이 Pod에 적용됩니다.

프로세스

다음 명령을 실행하여 Pod에 설정된 SCC(보안 컨텍스트 제약 조건) 및 기본 seccomp 프로필을 확인할 수 있습니다.

네임스페이스에서 실행 중인 Pod를 확인합니다.

```shell-session
$ oc get pods -n <namespace>
```

예를 들어, `workshop` 네임스페이스에서 실행 중인 Pod를 확인하려면 다음을 실행합니다.

```shell-session
$ oc get pods -n workshop
```

```shell-session
NAME                READY   STATUS      RESTARTS   AGE
parksmap-1-4xkwf    1/1     Running     0          2m17s
parksmap-1-deploy   0/1     Completed   0          2m22s
```

Pod를 검사합니다.

```shell-session
$ oc get pod parksmap-1-4xkwf -n workshop -o yaml
```

```shell-session
apiVersion: v1
kind: Pod
metadata:
  annotations:
    k8s.v1.cni.cncf.io/network-status: |-
      [{
          "name": "ovn-kubernetes",
          "interface": "eth0",
          "ips": [
              "10.131.0.18"
          ],
          "default": true,
          "dns": {}
      }]
    k8s.v1.cni.cncf.io/network-status: |-
      [{
          "name": "ovn-kubernetes",
          "interface": "eth0",
          "ips": [
              "10.131.0.18"
          ],
          "default": true,
          "dns": {}
      }]
    openshift.io/deployment-config.latest-version: "1"
    openshift.io/deployment-config.name: parksmap
    openshift.io/deployment.name: parksmap-1
    openshift.io/generated-by: OpenShiftWebConsole
    openshift.io/scc: restricted-v2
    seccomp.security.alpha.kubernetes.io/pod: runtime/default
```

1. 워크로드가 다른 SCC에 액세스할 수 없는 경우 `restricted-v2` SCC가 기본적으로 추가됩니다.

2. 4.20에서 새로 생성된 Pod에는 SCC에서 요구하는 대로 `runtime/default` 로 seccomp 프로필이 구성됩니다.

#### 15.1.1. 업그레이드된 클러스터

클러스터에서 4.20으로 업그레이드된 모든 인증된 사용자는 `restricted` 및 `restricted-v2` SCC에 액세스할 수 있습니다.

예를 들어 업그레이드 시 OpenShift Container Platform v4.10 클러스터에서 `restricted` SCC에 의해 허용된 워크로드는 `restricted-v2` 에 의해 허용될 수 있습니다. `restricted-v2` 는 `restricted` 및 `restricted-v2` 간에 더 제한적인 SCC이기 때문입니다.

참고

워크로드는 `re complexted-v2` 를 사용하여 실행할 수 있어야 합니다.

반대로 `privilegeEscalation` 이 필요한 워크로드와는 반대로 이 워크로드에서는 인증된 모든 사용자에 대해 `제한된` SCC를 계속 사용할 수 있습니다. `restricted-v2` 에서는 `privilegeEscalation` 을 허용하지 않기 때문입니다.

#### 15.1.2. 새로 설치된 클러스터

새로 설치된 OpenShift Container Platform 4.11 이상의 클러스터의 경우 `restricted-v2` 는 인증된 사용자가 사용할 수 있는 SCC로 `restricted` SCC를 대체합니다. `restricted-v2` 는 기본적으로 인증된 사용자에게 사용 가능한 유일한 SCC이므로 `privilegeEscalation: true` 가 클러스터에 허용되지 않습니다.

`privilegeEscalation` 기능은 `restricted` 으로 허용되지만 `restricted-v2` 로는 허용되지 않습니다. `restricted` SCC에서 허용하는 것보다 `restricted-v2` 에서는 더 많은 기능이 거부됩니다.

`privilegeEscalation: true` 가 있는 워크로드는 새로 설치된 OpenShift Container Platform 4.11 이상 클러스터에 허용될 수 있습니다. RoleBinding을 사용하여 워크로드를 실행하는 ServiceAccount(또는 이 워크로드를 허용할 수 있는 기타 SCC)에 `제한된` SCC에 대한 액세스 권한을 부여하려면 다음 명령을 실행합니다.

```shell-session
$ oc -n <workload-namespace> adm policy add-scc-to-user <scc-name> -z <serviceaccount_name>
```

OpenShift Container Platform 4.20에서 Pod 주석 `seccomp.security.alpha.kubernetes.io/pod: runtime/default` 및 가 더 이상 사용되지 않습니다.

```shell
container.seccomp.security.alpha.io/<container_name>: runtime/default
```

### 15.2. 사용자 정의 seccomp 프로필 구성

애플리케이션 요구 사항에 따라 필터를 업데이트할 수 있는 사용자 지정 seccomp 프로필을 구성할 수 있습니다. 이를 통해 클러스터 관리자는 OpenShift Container Platform에서 실행되는 워크로드의 보안을 보다 효과적으로 제어할 수 있습니다.

seccomp 보안 프로필은 프로세스에서 수행할 수 있는 시스템 호출(syscall)을 나열합니다. 권한은 SELinux보다 광범위하며, 시스템 전체 `쓰기` 와 같은 작업을 제한합니다.

#### 15.2.1. seccomp 프로필 생성

`MachineConfig` 오브젝트를 사용하여 프로필을 생성할 수 있습니다.

seccomp는 컨테이너 내에서 시스템 호출(syscall)을 제한하여 애플리케이션 액세스를 제한할 수 있습니다.

사전 요구 사항

클러스터 관리자 권한이 있습니다.

사용자 정의 SCC(보안 컨텍스트 제약 조건)를 생성했습니다. 자세한 내용은 추가 리소스를 참조하십시오.

프로세스

`MachineConfig` 오브젝트를 생성합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: custom-seccomp
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,<hash>
        filesystem: root
        mode: 0644
        path: /var/lib/kubelet/seccomp/seccomp-nostat.json
```

#### 15.2.2. 사용자 정의 seccomp 프로필 설정

사전 요구 사항

클러스터 관리자 권한이 있어야 합니다.

사용자 정의 SCC(보안 컨텍스트 제약 조건)를 생성했습니다. 자세한 내용은 "추가 리소스"를 참조하십시오.

사용자 지정 seccomp 프로필을 생성했습니다.

프로세스

Machine Config를 사용하여 사용자 정의 seccomp 프로필을 `/var/lib/kubelet/seccomp/<custom-name>.json` 에 업로드합니다. 자세한 단계는 "추가 리소스"를 참조하십시오.

생성된 사용자 지정 seccomp 프로필에 대한 참조를 제공하여 사용자 정의 SCC를 업데이트합니다.

```yaml
seccompProfiles:
- localhost/<custom-name>.json
```

1. 사용자 지정 seccomp 프로필의 이름을 제공합니다.

#### 15.2.3. 워크로드에 사용자 정의 seccomp 프로필 적용

사전 요구 사항

클러스터 관리자가 사용자 지정 seccomp 프로필을 설정했습니다. 자세한 내용은 "사용자 지정 seccomp 프로필 설정"을 참조하십시오.

프로세스

`securityContext.seccompProfile.type` 필드를 다음과 같이 설정하여 워크로드에 seccomp 프로필을 적용합니다.

```yaml
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: <custom-name>.json
```

1. 사용자 지정 seccomp 프로필의 이름을 제공합니다.

또는 Pod 주석 다음 명령을 사용할 수 있습니다. 그러나 이 방법은 OpenShift Container Platform 4.20에서 더 이상 사용되지 않습니다.

```shell
seccomp.security.alpha.kubernetes.io/pod: localhost/<custom-name>.json
```

배포하는 동안 승인 컨트롤러는 다음을 확인합니다.

사용자 역할에서 허용하는 현재 SCC에 대한 주석입니다.

seccomp 프로필을 포함하는 SCC를 pod에 사용할 수 있습니다.

Pod에 SCC가 허용되면 kubelet은 지정된 seccomp 프로필을 사용하여 Pod를 실행합니다.

중요

seccomp 프로필이 모든 작업자 노드에 배포되었는지 확인합니다.

참고

사용자 정의 SCC에는 CAP_NET_ADMIN 허용과 같은 Pod에 필요한 다른 조건을 충족하거나 Pod에 자동으로 할당되는 적절한 우선순위가 있어야 합니다.

### 15.3. 추가 리소스

보안 컨텍스트 제약 조건 관리

머신 구성 개요

### 16.1. 추가 호스트에서 JavaScript를 기반으로 API 서버에 액세스하도록 허용

기본 OpenShift Container Platform 구성에서는 웹 콘솔에서만 요청을 API 서버로 보낼 수 있습니다.

다른 호스트 이름을 사용하여 JavaScript 애플리케이션에서 API 서버 또는 OAuth 서버에 액세스해야 하는 경우 허용할 추가 호스트 이름을 구성할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`APIServer` 리소스를 편집합니다.

```shell-session
$ oc edit apiserver.config.openshift.io cluster
```

`spec` 섹션 아래에 `additionalCORSAllowedOrigins` 필드를 추가하고 하나 이상의 추가 호스트 이름을 지정합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: APIServer
metadata:
  annotations:
    release.openshift.io/create-only: "true"
  creationTimestamp: "2019-07-11T17:35:37Z"
  generation: 1
  name: cluster
  resourceVersion: "907"
  selfLink: /apis/config.openshift.io/v1/apiservers/cluster
  uid: 4b45a8dd-a402-11e9-91ec-0219944e0696
spec:
  additionalCORSAllowedOrigins:
  - (?i)//my\.subdomain\.domain\.com(:|\z)
```

1. 호스트 이름은 API 서버 및 OAuth 서버에 대한 HTTP 요청의 CORS 헤더와 일치하는 Golang 정규식 으로 지정됩니다.

참고

이 예에서는 다음 구문을 사용합니다.

`(?i)` 는 대소문자를 구분하지 않습니다.

`//` 는 도메인 시작 부분에 고정되고 `http:` 또는 `https:` 다음의 이중 슬래시와 일치합니다.

`\.` 은 도메인 이름에서 점을 이스케이프합니다.

`(:|\z)` 는 도메인 이름 `(\z)` 의 끝 또는 포트 구분 기호 `(:)` 과 일치하는지 확인합니다.

파일을 저장하여 변경 사항을 적용합니다.

## 17장. Pod에서 취약점 스캔

중요

Red Hat Quay Container Security Operator는 더 이상 사용되지 않으며 향후 OpenShift Container Platform 릴리스에서 제거될 예정입니다. Red Hat Quay Container Security Operator의 공식 교체 제품은 Red Hat Advanced Cluster Security for Kubernetes입니다.

Red Hat Quay Container Security Operator를 사용하면 OpenShift Container Platform 웹 콘솔에서 클러스터의 활성 Pod에 사용되는 컨테이너 이미지의 취약점 검사 결과에 액세스할 수 있습니다. Red Hat Quay Container Security Operator:

모든 네임스페이스 또는 지정된 네임스페이스에서 Pod와 관련된 컨테이너 감시

이미지의 레지스트리(예: Clair 스캔을 사용하는 Quay.io 또는 Red Hat Quay 레지스트리)를 실행 중인 경우 컨테이너가 취약점 정보를 통해 가져온 컨테이너 레지스트리를 쿼리합니다.

Kubernetes API의 `ImageManifestVuln` 오브젝트를 통해 취약점 노출

여기 지침을 사용하여 Red Hat Quay Container Security Operator는 `openshift-operators` 네임스페이스에 설치되므로 OpenShift Container Platform 클러스터의 모든 네임스페이스에서 사용할 수 있습니다.

### 17.1. Red Hat Quay Container Security Operator 설치

OpenShift Container Platform 웹 콘솔 Operator Hub에서 또는 CLI를 사용하여 Red Hat Quay Container Security Operator를 설치할 수 있습니다.

사전 요구 사항

다음 명령CLI를 설치했습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 웹 콘솔에 액세스할 수 있습니다.

클러스터에서 실행되는 Red Hat Quay 또는 Quay.io 레지스트리에서 제공되는 컨테이너가 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔을 사용하여 Red Hat Quay Container Security Operator를 설치할 수 있습니다.

웹 콘솔에서 Ecosystem → Software Catalog 로 이동하여 보안 을 선택합니다.

Red Hat Quay Container Security Operator 를 선택한 다음 설치를 선택합니다.

Red Hat Quay Container Security Operator 페이지에서 설치를 선택합니다. 업데이트 채널, 설치 모드 및 업데이트 승인이 자동으로 선택됩니다. 설치된 네임스페이스 필드의 기본값은 `openshift-operators` 입니다. 필요에 따라 이러한 설정을 조정할 수 있습니다.

설치 를 선택합니다. Red Hat Quay Container Security Operator 는 설치된 Operator 페이지에 잠시 후에 표시됩니다.

선택 사항: Red Hat Quay Container Security Operator에 사용자 정의 인증서를 추가할 수 있습니다. 예를 들어 현재 디렉터리에 `quay.crt` 라는 인증서를 생성합니다. 그런 다음 다음 명령을 실행하여 Red Hat Quay Container Security Operator에 사용자 정의 인증서를 추가합니다.

```shell-session
$ oc create secret generic container-security-operator-extra-certs --from-file=quay.crt -n openshift-operators
```

선택 사항: 사용자 정의 인증서를 추가한 경우 새 인증서를 적용하기 위해 Red Hat Quay Container Security Operator Pod를 다시 시작합니다.

또는 CLI를 사용하여 Red Hat Quay Container Security Operator를 설치할 수 있습니다.

다음 명령을 입력하여 Container Security Operator의 최신 버전 및 해당 채널을 검색합니다.

```shell-session
$ oc get packagemanifests container-security-operator \
  -o jsonpath='{range .status.channels[*]}{@.currentCSV} {@.name}{"\n"}{end}' \
  | awk '{print "STARTING_CSV=" $1 " CHANNEL=" $2 }' \
  | sort -Vr \
  | head -1
```

```shell-session
STARTING_CSV=container-security-operator.v3.8.9 CHANNEL=stable-3.8
```

이전 명령의 출력을 사용하여 Red Hat Quay Container Security Operator에 대한 `Subscription` 사용자 정의 리소스를 생성하여 `container-security-operator.yaml` 로 저장합니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: container-security-operator
  namespace: openshift-operators
spec:
  channel: ${CHANNEL}
  installPlanApproval: Automatic
  name: container-security-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  startingCSV: ${STARTING_CSV}
```

1. `spec.channel` 매개변수에 대해 이전 단계에서 얻은 값을 지정합니다.

2. `spec.startingCSV` 매개변수에 대해 이전 단계에서 얻은 값을 지정합니다.

다음 명령을 입력하여 구성을 적용합니다.

```shell-session
$ oc apply -f container-security-operator.yaml
```

```shell-session
subscription.operators.coreos.com/container-security-operator created
```

### 17.2. Red Hat Quay Container Security Operator 사용

다음 절차에서는 Red Hat Quay Container Security Operator를 사용하는 방법을 보여줍니다.

사전 요구 사항

Red Hat Quay Container Security Operator를 설치했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 홈 → 개요 로 이동합니다. Status (상태) 섹션에서 Image Vulnerabilities (이미지 취약점)에서 발견된 취약점 수를 제공합니다.

이미지 취약점 을 클릭하여 취약점의 심각도, 취약점을 수정할 수 있는지, 총 취약점 수를 자세히 설명하는 이미지 취약점 분석 탭을 표시합니다.

탐지된 취약점은 다음 두 가지 방법 중 하나로 해결할 수 있습니다.

취약점 섹션에서 링크를 선택합니다. 이렇게 하면 컨테이너가 제공된 컨테이너 레지스트리로 이동하여 취약점에 대한 정보를 볼 수 있습니다.

네임스페이스 링크를 선택합니다. 이렇게 하면 이미지 매니페스트 취약점 페이지로 이동합니다. 여기서 선택한 이미지의 이름과 해당 이미지가 실행 중인 모든 네임스페이스를 볼 수 있습니다.

취약한 이미지, 해당 취약점을 수정하는 방법, 이미지가 실행되는 네임스페이스를 학습한 후 다음 작업을 수행하여 보안을 개선할 수 있습니다.

이미지를 실행 중인 조직의 모든 사용자에게 경고하고 취약점을 수정하도록 요청합니다.

이미지가 있는 Pod를 시작한 배포 또는 기타 오브젝트를 삭제하여 이미지 실행을 중지합니다.

참고

Pod를 삭제하면 대시보드에서 취약점 정보가 재설정되는 데 몇 분이 걸릴 수 있습니다.

### 17.3. CLI에서 이미지 취약점 쿼리

아래 명령을 사용하면 Red Hat Quay Container Security Operator에서 탐지한 취약점에 대한 정보를 표시할 수 있습니다.

```shell
oc
```

사전 요구 사항

OpenShift Container Platform 인스턴스에 Red Hat Quay Container Security Operator를 설치했습니다.

프로세스

다음 명령을 입력하여 감지된 컨테이너 이미지 취약점을 쿼리합니다.

```shell-session
$ oc get vuln --all-namespaces
```

```shell-session
NAMESPACE     NAME              AGE
default       sha256.ca90...    6m56s
skynet        sha256.ca90...    9m37s
```

특정 취약점에 대한 세부 정보를 표시하려면 취약점 이름과 해당 네임스페이스를 아래 명령에 추가합니다. 다음 예제에서는 이미지에 취약점이 있는 RPM 패키지가 포함된 활성 컨테이너를 보여줍니다.

```shell
oc describe
```

```shell-session
$ oc describe vuln --namespace mynamespace sha256.ac50e3752...
```

```shell-session
Name:         sha256.ac50e3752...
Namespace:    quay-enterprise
...
Spec:
  Features:
    Name:            nss-util
    Namespace Name:  centos:7
    Version:         3.44.0-3.el7
    Versionformat:   rpm
    Vulnerabilities:
      Description: Network Security Services (NSS) is a set of libraries...
```

### 17.4. Red Hat Quay Container Security Operator 설치 제거

Container Security Operator를 설치 제거하려면 Operator를 설치 제거하고 `imagemanifestvulns.secscan.quay.redhat.com` 사용자 정의 리소스 정의(CRD)를 삭제해야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 에코시스템 → 설치된 Operator

를 클릭합니다.

Container Security Operator의 옵션 메뉴

를 클릭합니다.

Operator 제거 를 클릭합니다.

팝업 창에서 설치 제거를 클릭하여 결정을 확인합니다.

CLI를 사용하여 `imagemanifestvulns.secscan.quay.redhat.com` CRD를 삭제합니다.

다음 명령을 입력하여 `imagemanifestvulns.secscan.quay.redhat.com` 사용자 정의 리소스 정의를 제거합니다.

```shell-session
$ oc delete customresourcedefinition imagemanifestvulns.secscan.quay.redhat.com
```

```shell-session
customresourcedefinition.apiextensions.k8s.io "imagemanifestvulns.secscan.quay.redhat.com" deleted
```

### 18.1. 디스크 암호화 기술 정보

NBDE(Network-Bound Disk Encryption)를 사용하면 시스템을 다시 시작할 때 암호를 수동으로 입력하지 않고도 실제 및 가상 시스템에서 하드 드라이브의 root 볼륨을 암호화할 수 있습니다.

#### 18.1.1. 디스크 암호화 기술 비교

에지 서버에서 미사용 데이터를 보호하기 위한 NBDE(Network-Bound Disk Encryption)의 장점을 이해하려면 Clevis 없이 키 에스크로 및 TPM 디스크 암호화를 RHEL(Red Hat Enterprise Linux)을 실행하는 시스템의 NBDE와 비교합니다.

다음 표에는 위협 모델과 각 암호화 솔루션의 복잡성과 관련된 몇 가지 장단점이 표시되어 있습니다.

| 시나리오 | 키 에스크로 | TPM 디스크 암호화 (Clevis 제외) | NBDE |
| --- | --- | --- | --- |
| 단일 디스크 도난으로부터 보호 | X | X | X |
| 전체 서버 도난으로부터 보호 | X |  | X |
| 시스템은 네트워크와 독립적으로 재부팅 가능 |  | X |  |
| 주기적인 키 재입력 없음 |  | X |  |
| 키가 네트워크를 통해 전송되지 않음 |  | X | X |
| OpenShift에서 지원 |  | X | X |

#### 18.1.1.1. 키 에스크로

키 에스크로는 암호화 키를 저장하는 기존 시스템입니다. 네트워크의 키 서버는 암호화된 부팅 디스크가 있는 노드의 암호화 키를 저장하고 쿼리할 때 이를 반환합니다. 키 관리, 전송 암호화 및 인증에 대한 복잡성으로 인해 부팅 디스크 암호화를 위한 합리적인 선택이 아닙니다.

RHEL(Red Hat Enterprise Linux)에서 사용할 수 있지만 키 에스크로 기반 디스크 암호화 설정 및 관리는 수동 프로세스이며 노드 자동 추가를 포함하여 OpenShift Container Platform 자동화 작업에 적합하지 않으며 현재 OpenShift Container Platform에서 지원하지 않습니다.

#### 18.1.1.2. TPM 암호화

신뢰할 수 있는 TPM(Platform Module) 디스크 암호화는 데이터 센터나 원격 보호 위치에 설치하는 데 가장 적합합니다. dm-crypt 및 BitLocker와 같은 전체 디스크 암호화 유틸리티는 TPM 바인드 키를 사용하여 디스크를 암호화한 다음 노드의 마더보드에 연결된 TPM에 TPM 바인드 키를 저장합니다. 이 방법의 주요 이점은 외부 종속성이 없으며 노드는 외부 상호 작용 없이 부팅 시 자체 디스크를 암호 해독할 수 있다는 것입니다.

디스크가 노드에서 도난되어 외부에서 분석되는 경우 TPM 디스크 암호화는 데이터의 암호 해독을 방지합니다. 그러나 안전하지 않은 위치의 경우 이것으로 충분하지 않을 수 있습니다. 예를 들어 공격자가 전체 노드를 압축하는 경우 노드가 자체 디스크를 암호 해독하므로 공격자는 노드의 전원을 켤 때 데이터를 가로챌 수 있습니다. 물리적 TPM2 칩이 있는 노드와 VPM(Virtual Trusted Platform Module) 액세스 권한이 있는 가상 머신에 적용됩니다.

#### 18.1.1.3. NBDE(Network-Bound Disk Encryption)

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/179_OpenShift_NBDE_implementation_0821_1.png" alt="NBDE 배포 모델" kind="figure" diagram_type="image_figure"]
NBDE 배포 모델
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/6730655fe574055b7907c92ba2b6dea4/179_OpenShift_NBDE_implementation_0821_1.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/179_OpenShift_NBDE_implementation_0821_2.png" alt="NBDE 재부팅 동작" kind="figure" diagram_type="image_figure"]
NBDE 재부팅 동작
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/0c98a4380aa04f7838df462a51a2c266/179_OpenShift_NBDE_implementation_0821_2.png`_


NBDE(Network-Bound Disk Encryption)는 네트워크 전체에서 안전하고 익명의 방식으로 암호화 키를 외부 서버 또는 서버 집합에 효과적으로 연결합니다. 노드가 암호화 키를 저장하지 않거나 네트워크를 통해 전송하지 않지만 유사한 방식으로 작동한다는 점에서 키 에스크로가 아닙니다.

Clevis 및 Tang은 네트워크 바인딩 암호화를 제공하는 일반 클라이언트 및 서버 구성 요소입니다. RHCOS(Red Hat Enterprise Linux CoreOS)는 Linux Unified Key Setup-on-disk-format(LUKS)과 함께 이러한 구성 요소를 사용하여 루트 및 루트가 아닌 스토리지 볼륨을 암호화하고 암호 해독하여 네트워크 바인딩 디스크 암호화를 수행합니다.

노드가 시작되면 암호화 핸드셰이크를 수행하여 미리 정의된 Tang 서버 집합에 연결을 시도합니다. 필요한 수의 Tang 서버 수에 도달할 수 있는 경우 노드는 디스크 암호 해독 키를 구성하고 디스크를 잠금 해제하여 계속 부팅할 수 있습니다. 네트워크 중단 또는 서버를 사용할 수 없으므로 노드가 Tang 서버에 액세스할 수 없는 경우 노드는 부팅할 수 없으며 Tang 서버를 다시 사용할 수 있을 때까지 무기한 다시 시도합니다. 키가 네트워크에 있는 노드에 효과적으로 연결되기 때문에, 공격자가 미사용 데이터에 액세스하려고 하면 노드의 디스크와 Tang 서버에 대한 네트워크 액세스도 가져와야 합니다.

다음 그림은 NBDE의 배포 모델을 보여줍니다.

다음 그림은 재부팅 중에 NBDE 동작을 보여줍니다.

#### 18.1.1.4. 보안 공유 암호화

Shamir의 비밀 공유(sss)는 안전하게 키를 분할, 배포 및 재조정하기 위한 암호화 알고리즘입니다. OpenShift Container Platform은 이 알고리즘을 사용하여 더 복잡한 키 보안 조합을 지원할 수 있습니다.

여러 Tang 서버를 사용하도록 클러스터 노드를 구성하면 OpenShift Container Platform은 sss를 사용하여 지정된 서버 중 하나를 사용할 수 있는 경우 성공하는 암호 해독 정책을 설정합니다. 추가 보안을 위해 계층을 만들 수 있습니다. 예를 들어 OpenShift Container Platform에 디스크 암호 해독을 위해 지정된 Tang 서버 목록 중 하나와 TPM이 모두 필요한 정책을 정의할 수 있습니다.

#### 18.1.2. Tang 서버 디스크 암호화

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/179_OpenShift_NBDE_implementation_0821_3.png" alt="NBDE(Network-Bound Disk Encryption)" kind="figure" diagram_type="image_figure"]
NBDE(Network-Bound Disk Encryption)
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/ac88796341834a81c9a37f80ce6dd121/179_OpenShift_NBDE_implementation_0821_3.png`_


다음 구성 요소와 기술은 NBDE(Network-Bound Disk Encryption)를 구현합니다.

그림 18.1. LUKS1 암호화 볼륨을 사용할 때의 NBDE 스키마입니다 luksmeta 패키지는 LUKS2 볼륨에 사용되지 않습니다.

Tang 은 데이터를 네트워크 상에 바인딩하는 서버입니다. 그러면 노드가 특정 보안 네트워크에 바인딩될 때 데이터를 포함하는 노드를 사용할 수 있습니다. Tang은 상태 비저장이며 TLS(전송 계층 보안) 또는 인증이 필요하지 않습니다. 키 서버가 모든 암호화 키를 저장하고 모든 암호화 키에 대한 지식이 있는 에스크로 기반 솔루션과 달리 Tang은 노드 키와 상호 작용하지 않으므로 노드에서 식별 정보를 얻을 수 없습니다.

Clevis 는 Linux Unified Key Setup-on-disk-format(LUKS) 볼륨의 자동 잠금 해제를 제공하는 자동화된 암호 해독을 위한 플러그형 프레임워크입니다. Clevis 패키지는 노드에서 실행되며 기능의 클라이언트 측면을 제공합니다.

Clevis 핀 은 Clevis 프레임워크에 대한 플러그인입니다. 다음 세 가지 고정 유형이 있습니다.

TPM2

디스크 암호화를 TPM2에 바인딩합니다.

Tang

디스크 암호화를 Tang 서버에 바인딩하여 NBDE를 활성화합니다.

Shamir의 시크릿 공유 (sss)

다른 핀의 더 복잡한 조합을 허용합니다. 다음과 같은 더 미묘한 정책을 허용합니다.

이 세 개의 Tang 서버 중 하나에 연결할 수 있어야합니다.

이 5 개의 Tang 서버 중 세 개에 연결할 수 있어야합니다.

TPM2 및 이 세 Tang 서버 중 하나 이상에 연결할 수 있어야합니다.

#### 18.1.3. Tang 서버 위치 계획

Tang 서버 환경을 계획할 때 Tang 서버의 실제 및 네트워크 위치를 고려하십시오.

물리적 위치

Tang 서버의 지리적 위치는 무단 액세스 또는 도난으로부터 적절하게 보호되고 중요한 서비스를 실행하는 데 필요한 가용성과 접근성을 제공하는 한 비교적 중요하지 않습니다.

항상 Tang 서버를 사용할 수 있는 한 Clevis 클라이언트가 있는 노드에는 로컬 Tang 서버가 필요하지 않습니다. 재해 복구에는 위치에 관계없이 Tang 서버에 대한 중복 전원 및 중복 네트워크 연결이 필요합니다.

네트워크 위치

Tang 서버에 대한 네트워크 액세스 권한이 있는 노드는 고유한 디스크 파티션 또는 동일한 Tang 서버에서 암호화된 다른 디스크를 해독할 수 있습니다.

지정된 호스트에서 네트워크 연결 여부가 있는지 확인하는 Tang 서버의 네트워크 위치를 선택하여 암호 해독 권한을 허용합니다. 예를 들어 방화벽 보호는 모든 유형의 게스트 또는 공용 네트워크에서 액세스하지 못하거나, 보안이 유지되지 않은 모든 네트워크 파이크에서 액세스하지 못하도록 할 수 있습니다.

또한 프로덕션 네트워크와 개발 네트워크 간의 네트워크 분리를 유지 관리합니다. 이를 통해 적절한 네트워크 위치를 정의하고 추가 보안 계층을 추가할 수 있습니다.

동일한 리소스(예: 동일한 `rolebindings.rbac.authorization.k8s.io` 클러스터)에 Tang 서버를 배포하지 마십시오. 그러나 Tang 서버 및 기타 보안 리소스의 클러스터는 여러 추가 클러스터 및 클러스터 리소스를 지원하는 데 유용한 구성일 수 있습니다.

#### 18.1.4. Tang 서버 크기 조정 요구사항

가용성, 네트워크 및 물리적 위치에 대한 요구 사항은 서버 용량에 대해 우려하지 않고 사용할 Tang 서버 수를 결정하는 데 영향을 미칩니다.

Tang 서버는 Tang 리소스를 사용하여 암호화된 데이터 상태를 유지 관리하지 않습니다. Tang 서버는 완전히 독립적이거나 중요한 자료만 공유하므로 확장이 용이합니다.

Tang 서버는 핵심 자료를 처리하는 두 가지 방법이 있습니다.

여러 Tang 서버는 주요 자료를 공유합니다.

동일한 URL 뒤에서 키를 공유하는 Tang 서버를 로드 밸런싱해야 합니다. 구성은 라운드 로빈 DNS만큼 간단하거나 물리적 로드 밸런서를 사용할 수 있습니다.

단일 Tang 서버에서 여러 Tang 서버로 확장할 수 있습니다. Tang 서버가 주요 자료와 동일한 URL을 공유하는 경우 Tang 서버 확장은 노드에서 다시 키 또는 클라이언트 재구성을 필요로 하지 않습니다.

클라이언트 노드 설정 및 키 순환에는 Tang 서버 한 개만 필요합니다.

여러 Tang 서버는 자체 주요 자료를 생성합니다.

설치 시 여러 Tang 서버를 구성할 수 있습니다.

로드 밸런서 백그라운드에서 개별 Tang 서버를 확장할 수 있습니다.

모든 Tang 서버는 클라이언트 노드 설정 또는 키 교체 중에 사용할 수 있어야 합니다.

클라이언트 노드가 기본 구성을 사용하여 부팅되면 Clevis 클라이언트는 모든 Tang 서버에 연결합니다. 해독을 진행하려면 n 개의 Tang 서버만 온라인 상태 여야합니다. n 의 기본값은 1입니다.

Red Hat은 Tang 서버의 동작을 변경하는 설치 후 구성을 지원하지 않습니다.

#### 18.1.5. 로깅 고려 사항

Tang 트래픽의 중앙 집중식 로깅은 예기치 않은 암호 해독 요청과 같은 항목을 탐지할 수 있기 때문에 유용합니다. 예를 들면 다음과 같습니다.

부팅 시퀀스에 해당하지 않는 암호의 암호 해독을 요청하는 노드

알려진 유지 관리 활동 외부에서 암호 해독을 요청하는 노드(예:암호 키)

### 18.2. Tang 서버 설치 시 고려 사항

클러스터 노드를 설치할 때 NBDE(Network-Bound Disk Encryption)를 활성화해야 합니다. 그러나 설치 시 초기화된 후 언제든지 디스크 암호화 정책을 변경할 수 있습니다.

#### 18.2.1. 설치 시나리오

Tang 서버 설치를 계획할 때 다음 권장 사항을 고려하십시오.

소규모 환경은 여러 Tang 서버를 사용하는 경우에도 하나의 핵심 자료 세트를 사용할 수 있습니다.

키 교체가 더 쉽습니다.

Tang 서버는 고가용성을 허용하도록 쉽게 확장할 수 있습니다.

대규모 환경은 다음과 같은 여러 주요 자료 세트의 혜택을 누릴 수 있습니다.

물리적으로 다양한 설치를 통해 지리적 지역 간 주요 자료를 복사하고 동기화할 필요가 없습니다.

키 교체는 대규모 환경에서 더 복잡합니다.

노드 설치 및 다시 키를 지정하려면 모든 Tang 서버에 대한 네트워크 연결이 필요합니다.

암호 해독 중에 모든 Tang 서버를 쿼리하는 부팅 노드로 인해 네트워크 트래픽이 약간 증가할 수 있습니다. 하나의 Clevis 클라이언트 쿼리만 성공해야 하지만 Clevis는 모든 Tang 서버를 쿼리합니다.

추가 복잡성:

추가 수동 재구성을 통해 디스크 파티션의 암호를 해독하기 위해 `any N of M servers online` 의 Shamir의 시크릿 공유(sss)를 허용할 수 있습니다. 이 시나리오에서 디스크를 해독하려면 여러 주요 자료 집합과 초기 설치 후 Clevis 클라이언트를 사용하여 Tang 서버 및 노드를 수동으로 관리해야 합니다.

높은 수준의 권장 사항:

단일 RAN 배포의 경우 제한된 Tang 서버 집합은 해당 도메인 컨트롤러(DC)에서 실행할 수 있습니다.

여러 RAN 배포의 경우 각 해당 DC에서 Tang 서버를 실행할지 또는 글로벌 Tang 환경이 시스템의 다른 요구 사항 및 요구 사항에 더 적합한지 여부를 결정해야 합니다.

#### 18.2.2. Tang 서버 설치

하나 이상의 Tang 서버를 배포하려면 시나리오에 따라 다음 옵션에서 선택할 수 있습니다.

NBDE Tang Server Operator를 사용하여 Tang 서버 배포

RHEL 시스템에서 강제 모드로 SELinux로 Tang 서버 배포

RHEL 웹 콘솔에서 Tang 서버 구성

Tang을 컨테이너로 배포

nbde_server 시스템 역할을 사용하여 여러 Tang 서버를 설정

#### 18.2.2.1. 컴퓨팅 요구 사항

Tang 서버의 컴퓨팅 요구 사항은 매우 낮습니다. 서버를 프로덕션에 배포하는 데 사용하는 일반적인 서버 평가 구성은 충분한 컴퓨팅 용량을 프로비저닝할 수 있습니다.

고가용성 고려 사항은 고객 요구를 충족하기 위한 추가 컴퓨팅 성능은 가용성에만 해당하지 않습니다.

#### 18.2.2.2. 부팅 시 자동 시작

Tang 서버가 사용하는 주요 자료의 중요한 특성으로 인해 Tang 서버의 부팅 시퀀스 중 수동 개입 오버헤드가 유용할 수 있습니다.

기본적으로 Tang 서버가 시작되고 예상되는 로컬 볼륨에 주요 자료가 없으면 새로운 자료를 만들고 제공합니다. 기존 주요 자료로 시작하거나 시작을 중단하고 수동 개입을 기다리면 이 기본 동작을 방지할 수 있습니다.

#### 18.2.2.3. HTTP와 HTTPS 비교

Tang 서버에 대한 트래픽은 암호화(HTTPS) 또는 일반 텍스트(HTTP)일 수 있습니다. 이 트래픽을 암호화할 때 큰 보안 이점이 없으며 암호를 해독하면 Clevis 클라이언트를 실행하는 노드에서 TLS(Transport Layer Security) 인증서 검사와 관련된 복잡성 또는 실패 조건이 제거됩니다.

노드의 Clevis 클라이언트와 Tang 서버 간에 암호화되지 않은 트래픽을 수동 모니터링할 수 있지만, 이 트래픽을 사용하여 주요 자료를 확인하는 기능은 향후 이론적인 문제가 될 수 있습니다. 이러한 트래픽 분석에는 대량의 캡처된 데이터가 필요합니다. 키 교체는 즉시 무효화됩니다. 마지막으로 수동 모니터링을 수행할 수 있는 모든 위협 행위자는 Tang 서버에 대한 수동 연결을 수행하는 데 필요한 네트워크 액세스 권한을 이미 획득했으며 캡처된 Clevis 헤더의 수동 암호 해독을 수행할 수 있습니다.

그러나 설치 사이트에 있는 다른 네트워크 정책에는 애플리케이션과 관계없이 트래픽 암호화가 필요할 수 있으므로 이 결정을 클러스터 관리자에게 맡기는 것이 좋습니다.

추가 리소스

RHEL 8 보안 강화 문서에서 정책 기반 암호 해독을 사용하여 암호화된 볼륨의 자동 잠금 해제 구성

공식 Tang 서버 컨테이너

설치하는 동안 디스크 암호화 및 미러링

### 18.3. Tang 서버 암호화 키 관리

암호화 키를 다시 생성하는 암호화 메커니즘은 노드에 저장된 인식되지 않은 키와 관련 Tang 서버의 개인 키를 기반으로 합니다.

참고

Tang 서버 개인 키와 노드의 암호화된 디스크를 모두 취득한 공격자의 가능성을 보호하기 위해 주기적으로 다시 키를 변경하는 것이 좋습니다.

Tang 서버에서 이전 키를 삭제하려면 모든 노드에 대해 키 다시 입력 작업을 수행해야 합니다.

다음 섹션에서는 이전 키를 다시 키우고 삭제하는 절차를 제공합니다.

#### 18.3.1. Tang 서버의 키 백업

Tang 서버는 `/usr/libexec/tangd-keygen` 을 사용하여 새 키를 생성하고 기본적으로 `/var/db/tang` 디렉터리에 저장합니다. 오류가 발생할 경우 Tang 서버를 복구하려면 이 디렉터리를 백업하십시오. 키는 민감하며 키를 사용하는 모든 호스트의 부팅 디스크 암호 해독을 수행할 수 있으므로 적절하게 키를 보호해야 합니다.

프로세스

`/var/db/tang` 디렉토리에서 키를 복원할 수 있는 temp 디렉토리로 백업 키를 복사합니다.

#### 18.3.2. Tang 서버의 키 복구

백업에서 키에 액세스하여 Tang 서버의 키를 복구할 수 있습니다.

프로세스

백업 폴더에서 `/var/db/tang/` 디렉터리로 키를 복원합니다.

Tang 서버가 시작되면 이 복원된 키를 알리고 사용합니다.

#### 18.3.3. Tang 서버 키 다시 지정

[FIGURE src="/playbooks/wiki-assets/full_rebuild/security_and_compliance/179_OpenShift_NBDE_implementation_0821_4.png" alt="Tang 서버 키 다시 지정" kind="figure" diagram_type="image_figure"]
Tang 서버 키 다시 지정
[/FIGURE]

_Source: `security_and_compliance.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Security_and_compliance-ko-KR/images/7ca99379d14d14d75c8d2f49f6cf0d5c/179_OpenShift_NBDE_implementation_0821_4.png`_


이 절차에서는 각각 고유한 키가 있는 세 개의 Tang 서버 세트를 예제로 사용합니다.

중복된 Tang 서버를 사용하면 노드가 자동으로 부팅되지 않을 가능성이 줄어듭니다.

Tang 서버 및 연결된 모든 NBDE 암호화 노드를 다시 입력하는 것은 3단계 절차입니다.

사전 요구 사항

하나 이상의 노드에 작동하는 NBDE(Network-Bound Disk Encryption)를 설치합니다.

프로세스

새 Tang 서버 키를 생성합니다.

새 키를 사용하도록 모든 NBDE 암호화 노드를 다시 입력합니다.

이전 Tang 서버 키를 삭제합니다.

참고

모든 NBDE 암호화 노드가 키 변경을 완료하기 전에 이전 키를 삭제하면 해당 노드가 다른 구성된 Tang 서버에 지나치게 의존하게 됩니다.

그림 18.2. Tang 서버 재키핑을 위한 워크플로우 예

#### 18.3.3.1. 새 Tang 서버 키 생성

사전 요구 사항

Tang 서버를 실행하는 Linux 시스템의 root 쉘입니다.

Tang 서버 키 교체를 쉽게 확인하려면 이전 키를 사용하여 작은 테스트 파일을 암호화합니다.

```shell-session
# echo plaintext | clevis encrypt tang '{"url":"http://localhost:7500”}' -y >/tmp/encrypted.oldkey
```

암호화에 성공하고 파일을 해독하여 동일한 문자열 `plaintext` 를 생성할 수 있는지 확인합니다.

```shell-session
# clevis decrypt </tmp/encrypted.oldkey
```

프로세스

Tang 서버 키를 저장하는 디렉터리를 찾아 액세스합니다. 일반적으로 `/var/db/tang` 디렉토리입니다. 현재 공개된 키 지문을 확인합니다.

```shell-session
# tang-show-keys 7500
```

```shell-session
36AHjNH3NZDSnlONLz1-V4ie6t8
```

Tang 서버 키 디렉토리를 입력합니다.

```shell-session
# cd /var/db/tang/
```

현재 Tang 서버 키를 나열합니다.

```shell-session
# ls -A1
```

```shell-session
36AHjNH3NZDSnlONLz1-V4ie6t8.jwk
gJZiNPMLRBnyo_ZKfK4_5SrnHYo.jwk
```

일반적인 Tang 서버 작업 중에는 이 디렉터리에 두 개의 `.jwk` 파일이 있습니다. 하나는 서명 및 확인용이고 다른 하나는 키 파생을 위한 것입니다.

이전 키의 알림을 비활성화합니다.

```shell-session
# for key in *.jwk; do \
  mv -- "$key" ".$key"; \
done
```

새 클라이언트는 NBDE(Network-Bound Disk Encryption) 또는 요청 키를 설정해도 더 이상 이전 키가 표시되지 않습니다. 기존 클라이언트는 삭제될 때까지 이전 키에 계속 액세스하고 사용할 수 있습니다. Tang 서버는 UNIX 숨겨진 파일에 저장된 키를 읽지만 알림은 하지 않으며 `.` 문자로 시작합니다.

새 키를 생성합니다.

```shell-session
# /usr/libexec/tangd-keygen /var/db/tang
```

현재 Tang 서버 키를 나열하여 이전 키가 현재 숨겨진 파일이고 새 키가 있는지 확인합니다.

```shell-session
# ls -A1
```

```shell-session
.36AHjNH3NZDSnlONLz1-V4ie6t8.jwk
.gJZiNPMLRBnyo_ZKfK4_5SrnHYo.jwk
Bp8XjITceWSN_7XFfW7WfJDTomE.jwk
WOjQYkyK7DxY_T5pMncMO5w0f6E.jwk
```

Tang은 새 키를 자동으로 알립니다.

참고

보다 최근 Tang 서버 설치에는 광고 비활성화 및 새 키를 동시에 생성하는 도우미 `/usr/libexec/tangd-rotate-keys` 디렉토리가 있습니다.

동일한 주요 자료를 공유하는 로드 밸런서 장치에서 여러 Tang 서버를 실행하는 경우, 계속하기 전에 여기서 변경한 사항이 전체 서버 집합에서 올바르게 동기화되는지 확인하십시오.

검증

Tang 서버가 새 키를 알리고 이전 키를 알리지 않는지 확인합니다.

```shell-session
# tang-show-keys 7500
```

```shell-session
WOjQYkyK7DxY_T5pMncMO5w0f6E
```

이전 키가 보급되지는 않았지만 암호 해독 요청에 계속 사용할 수 있는지 확인합니다.

```shell-session
# clevis decrypt </tmp/encrypted.oldkey
```

#### 18.3.3.2. 모든 NBDE 노드 키 다시 지정

원격 클러스터에 다운타임을 발생시키지 않고 `DaemonSet` 오브젝트를 사용하여 원격 클러스터의 모든 노드를 다시 입력할 수 있습니다.

참고

노드를 다시 시작하는 동안 전원이 손실되는 경우 부팅할 수 없게 될 수 있으며 RHACM(Red Hat Advanced Cluster Management) 또는 GitOps 파이프라인을 통해 재배포해야 합니다.

사전 요구 사항

NBDE(Network-Bound Disk Encryption) 노드가 있는 모든 클러스터에 대한 `cluster-admin` 액세스가 있어야 합니다.

모든 Tang 서버는 Tang 서버의 키가 변경되지 않은 경우에도 키 재지정 중인 모든 NBDE 노드에서 액세스할 수 있어야 합니다.

Tang 서버 URL과 모든 Tang 서버의 키 지문을 가져옵니다.

프로세스

다음 템플릿을 기반으로 `DaemonSet` 오브젝트를 생성합니다. 이 템플릿은 3개의 중복 Tang 서버를 설정하지만 다른 상황에 맞게 쉽게 조정할 수 있습니다. `NEW_TANG_PIN` 환경의 Tang 서버 URL과 지문을 사용자 환경에 맞게 변경합니다.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: tang-rekey
  namespace: openshift-machine-config-operator
spec:
  selector:
    matchLabels:
      name: tang-rekey
  template:
    metadata:
      labels:
        name: tang-rekey
    spec:
      containers:
      - name: tang-rekey
        image: registry.access.redhat.com/ubi9/ubi-minimal:latest
        imagePullPolicy: IfNotPresent
        command:
        - "/sbin/chroot"
        - "/host"
        - "/bin/bash"
        - "-ec"
        args:
        - |
          rm -f /tmp/rekey-complete || true
          echo "Current tang pin:"
          clevis-luks-list -d $ROOT_DEV -s 1
          echo "Applying new tang pin: $NEW_TANG_PIN"
          clevis-luks-edit -f -d $ROOT_DEV -s 1 -c "$NEW_TANG_PIN"
          echo "Pin applied successfully"
          touch /tmp/rekey-complete
          sleep infinity
        readinessProbe:
          exec:
            command:
            - cat
            - /host/tmp/rekey-complete
          initialDelaySeconds: 30
          periodSeconds: 10
        env:
        - name: ROOT_DEV
          value: /dev/disk/by-partlabel/root
        - name: NEW_TANG_PIN
          value: >-
            {"t":1,"pins":{"tang":[
              {"url":"http://tangserver01:7500","thp":"WOjQYkyK7DxY_T5pMncMO5w0f6E"},
              {"url":"http://tangserver02:7500","thp":"I5Ynh2JefoAO3tNH9TgI4obIaXI"},
              {"url":"http://tangserver03:7500","thp":"38qWZVeDKzCPG9pHLqKzs6k1ons"}
            ]}}
        volumeMounts:
        - name: hostroot
          mountPath: /host
        securityContext:
          privileged: true
      volumes:
      - name: hostroot
        hostPath:
          path: /
      nodeSelector:
        kubernetes.io/os: linux
      priorityClassName: system-node-critical
      restartPolicy: Always
      serviceAccount: machine-config-daemon
      serviceAccountName: machine-config-daemon
```

이 경우 `tangserver01` 을 다시 입력하더라도 `tangserver01` 의 새 지문뿐만 아니라 다른 모든 Tang 서버의 현재 지문도 지정해야 합니다. 키 재지정 작업의 모든 지문을 지정하지 않으면 메시지 가로채기 공격의 기회가 열립니다.

다시 키를 지정해야 하는 모든 클러스터에 데몬 세트를 배포하려면 다음 명령을 실행합니다.

```shell-session
$ oc apply -f tang-rekey.yaml
```

그러나 대규모로 실행하려면 ACM 정책에서 데몬 세트를 래핑합니다. 이 ACM 구성에는 데몬 세트를 배포하기 위한 하나의 정책, 모든 데몬 세트 pod가 준비되었는지 확인하는 두 번째 정책 및 적절한 클러스터 세트에 적용하는 배치 규칙이 포함되어야 합니다.

참고

데몬 세트가 모든 서버를 성공적으로 다시 시작했는지 확인한 후 데몬 세트를 삭제합니다. 데몬 세트를 삭제하지 않으면 다음 키 재지정 작업을 수행하기 전에 삭제해야 합니다.

검증

데몬 세트를 배포한 후 데몬 세트를 모니터링하여 키 지정 작업이 성공적으로 완료되었는지 확인합니다. 예제 데몬 세트의 스크립트는 키 재지정에 실패한 경우 오류와 함께 종료되고 성공한 경우 `CURRENT` 상태로 유지됩니다. 키 재지정이 성공적으로 완료되면 Pod를 `READY` 로 표시하는 준비 프로브도 있습니다.

다음은 키 재지정이 완료되기 전에 데몬 세트의 출력 목록의 예입니다.

```shell-session
$ oc get -n openshift-machine-config-operator ds tang-rekey
```

```shell-session
NAME         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
tang-rekey   1         1         0       1            0           kubernetes.io/os=linux   11s
```

다음은 키 재지정을 성공적으로 완료한 후 데몬 세트의 출력 목록의 예입니다.

```shell-session
$ oc get -n openshift-machine-config-operator ds tang-rekey
```

```shell-session
NAME         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
tang-rekey   1         1         1       1            1           kubernetes.io/os=linux   13h
```

키를 다시 입력하는 데는 일반적으로 몇 분이 소요됩니다.

참고

ACM 정책을 사용하여 데몬 세트를 여러 클러스터에 배포하는 경우 모든 데몬 세트의 준비 수가 DESIRED 수인지 확인하는 규정 준수 정책을 포함해야 합니다. 이러한 방식으로 이러한 정책에 대한 규정 준수는 모든 데몬 세트 Pod가 READY이고 키 재지정이 성공적으로 완료되었음을 보여줍니다. ACM 검색을 사용하여 모든 데몬 세트 상태를 쿼리할 수도 있습니다.

#### 18.3.3.3. Tang 서버의 임시 키 재지정 오류 문제 해결

Tang 서버를 다시 입력하는 오류 조건이 일시적인지 확인하려면 다음 절차를 수행합니다. 임시 오류 상태에는 다음이 포함될 수 있습니다.

임시 네트워크 중단

Tang 서버 유지 관리

일반적으로 이러한 유형의 임시 오류 조건이 발생하면 데몬 세트가 오류를 성공적으로 해결하거나 데몬 세트를 삭제하고 임시 오류 조건이 해결될 때까지 다시 시도할 수 없습니다.

프로세스

일반적인 Kubernetes pod 재시작 정책을 사용하여 키 재지정 작업을 수행하는 Pod를 다시 시작합니다.

연결된 Tang 서버를 사용할 수 없는 경우 모든 서버가 다시 온라인 상태가 될 때까지 다시 키를 입력합니다.

#### 18.3.3.4. Tang 서버의 영구적인 키 재지정 오류 문제 해결

Tang 서버를 다시 시작한 후 `READY` 수는 연장된 기간이 지나면 `DESIRED` 개수와 동일하지 않으므로 영구적인 오류 상태를 나타낼 수 있습니다. 이 경우 다음 조건이 적용될 수 있습니다.

`NEW_TANG_PIN` 정의의 Tang 서버 URL 또는 지문의 오타 오류입니다.

Tang 서버가 해제되거나 키가 영구적으로 손실됩니다.

사전 요구 사항

이 절차에 표시된 명령은 Tang 서버 또는 Tang 서버에 대한 네트워크 액세스 권한이 있는 Linux 시스템에서 실행할 수 있습니다.

프로세스

데몬 세트에 정의된 대로 각 Tang 서버의 구성에 대해 간단한 암호화 및 암호 해독 작업을 수행하여 Tang 서버 구성을 확인합니다.

이는 잘못된 지문이 있는 암호화 및 암호 해독 시도의 예입니다.

```shell-session
$ echo "okay" | clevis encrypt tang \
  '{"url":"http://tangserver02:7500","thp":"badthumbprint"}' | \
  clevis decrypt
```

```shell-session
Unable to fetch advertisement: 'http://tangserver02:7500/adv/badthumbprint'!
```

올바른 지문이 있는 암호화 및 암호 해독 시도의 예입니다.

```shell-session
$ echo "okay" | clevis encrypt tang \
  '{"url":"http://tangserver03:7500","thp":"goodthumbprint"}' | \
  clevis decrypt
```

```shell-session
okay
```

근본 원인을 확인한 후 기본 상황을 해결합니다.

작동하지 않는 데몬 세트를 삭제합니다.

데몬 세트 정의를 편집하여 기본 문제를 해결합니다. 여기에는 다음 작업이 포함될 수 있습니다.

Tang 서버 항목을 편집하여 URL과 지문을 수정합니다.

더 이상 서비스 중이 아닌 Tang 서버를 제거합니다.

해제된 서버를 대체하는 새 Tang 서버를 추가합니다.

업데이트된 데몬 세트를 다시 배포합니다.

참고

구성에서 Tang 서버를 교체, 제거 또는 추가할 때 현재 서버를 포함하여 하나 이상의 원본 서버가 계속 작동하는 한 키 재지정 작업이 성공적으로 수행됩니다. 원래 Tang 서버가 작동하지 않거나 복구할 수 없는 경우 시스템을 복구할 수 없으며 영향을 받는 노드를 다시 배포해야 합니다.

검증

데몬 세트의 각 pod에서 로그를 확인하여 키 재지정이 성공적으로 완료되었는지 확인합니다. 키 재지정에 성공하지 못하면 로그에 실패 조건이 표시될 수 있습니다.

데몬 세트에서 생성한 컨테이너의 이름을 찾습니다.

```shell-session
$ oc get pods -A | grep tang-rekey
```

```shell-session
openshift-machine-config-operator  tang-rekey-7ks6h  1/1  Running   20 (8m39s ago)  89m
```

컨테이너에서 로그를 출력합니다. 다음 로그는 성공적인 키 재지정 작업에서 가져온 것입니다.

```shell-session
$ oc logs tang-rekey-7ks6h
```

```shell-session
Current tang pin:
1: sss '{"t":1,"pins":{"tang":[{"url":"http://10.46.55.192:7500"},{"url":"http://10.46.55.192:7501"},{"url":"http://10.46.55.192:7502"}]}}'
Applying new tang pin: {"t":1,"pins":{"tang":[
  {"url":"http://tangserver01:7500","thp":"WOjQYkyK7DxY_T5pMncMO5w0f6E"},
  {"url":"http://tangserver02:7500","thp":"I5Ynh2JefoAO3tNH9TgI4obIaXI"},
  {"url":"http://tangserver03:7500","thp":"38qWZVeDKzCPG9pHLqKzs6k1ons"}
]}}
Updating binding...
Binding edited successfully
Pin applied successfully
```

#### 18.3.4. 이전 Tang 서버 키 삭제

사전 요구 사항

Tang 서버를 실행하는 Linux 시스템의 root 쉘입니다.

프로세스

Tang 서버 키가 저장된 디렉터리를 찾아 액세스합니다. 일반적으로 `/var/db/tang` 디렉토리입니다.

```shell-session
# cd /var/db/tang/
```

공개된 키와 의도하지 않은 키를 표시하여 현재 Tang 서버 키를 나열합니다.

```shell-session
# ls -A1
```

```shell-session
.36AHjNH3NZDSnlONLz1-V4ie6t8.jwk
.gJZiNPMLRBnyo_ZKfK4_5SrnHYo.jwk
Bp8XjITceWSN_7XFfW7WfJDTomE.jwk
WOjQYkyK7DxY_T5pMncMO5w0f6E.jwk
```

이전 키를 삭제합니다.

```shell-session
# rm .*.jwk
```

현재 Tang 서버 키를 나열하여 의도하지 않은 키가 더 이상 존재하지 않는지 확인합니다.

```shell-session
# ls -A1
```

```shell-session
Bp8XjITceWSN_7XFfW7WfJDTomE.jwk
WOjQYkyK7DxY_T5pMncMO5w0f6E.jwk
```

검증

이 시점에서 서버는 새 키를 계속 알립니다. 그러나 이전 키를 기반으로 암호를 해독하려는 시도는 실패합니다.

현재 공개된 키 지문을 위해 Tang 서버를 쿼리합니다.

```shell-session
# tang-show-keys 7500
```

```shell-session
WOjQYkyK7DxY_T5pMncMO5w0f6E
```

이전에 만든 테스트 파일을 해독하여 이전 키에 대한 암호 해독이 실패하는지 확인합니다.

```shell-session
# clevis decrypt </tmp/encryptValidation
```

```shell-session
Error communicating with the server!
```

동일한 주요 자료를 공유하는 로드 밸런서 장치에서 여러 Tang 서버를 실행하는 경우 계속하기 전에 변경 사항이 전체 서버 세트에서 올바르게 동기화되는지 확인하십시오.

### 18.4. 재해 복구 고려 사항

이 섹션에서는 몇 가지 잠재적 재해 상황과 각 상황에 대응하는 절차에 대해 설명합니다. 추가 상황이 발견되거나 가능할 것으로 추정되면 여기에 추가됩니다.

#### 18.4.1. 클라이언트 시스템 손실

Tang 서버를 사용하여 디스크 파티션을 해독하는 클러스터 노드가 손실되는 것은 재해가 아닙니다. 시스템이 도난되었는지, 하드웨어 장애 발생 또는 다른 손실 시나리오는 중요하지 않습니다. 디스크는 암호화되어 복구할 수 없는 것으로 간주됩니다.

그러나 도난이 발생하는 경우 Tang 서버의 키를 미리 교체하고 나머지 모든 노드의 키를 다시 입력하여 공격자가 Tang 서버에 액세스할 수 있는 경우에도 디스크를 복구할 수 없게 됩니다.

이 상황에서 복구하려면 노드를 다시 설치하거나 교체합니다.

#### 18.4.2. 클라이언트 네트워크 연결 손실에 대한 계획

개별 노드에 대한 네트워크 연결이 끊어지면 자동으로 부팅할 수 없게 됩니다.

네트워크 연결이 끊어질 수 있는 작업을 계획하는 경우 현장 기술자가 수동으로 사용할 암호를 표시한 다음 나중에 키를 교체하여 무효화할 수 있습니다.

프로세스

네트워크를 사용할 수 없게 되기 전에 다음 명령을 사용하여 `/dev/vda2` 장치의 첫 번째 `-s 1` 슬롯에 사용된 암호를 표시하십시오.

```shell-session
$ sudo clevis luks pass -d /dev/vda2 -s 1
```

이 값을 무효화하고 다음 명령을 사용하여 임의의 부팅 시간 암호를 다시 생성합니다.

```shell-session
$ sudo clevis luks regen -d /dev/vda2 -s 1
```

#### 18.4.3. 예기치 않은 네트워크 연결 손실

네트워크 중단이 예기치 않고 노드가 재부팅되면 다음 시나리오를 고려하십시오.

노드가 여전히 온라인 상태인 경우 네트워크 연결이 복원될 때까지 재부팅하지 않아야 합니다. 이는 단일 노드 클러스터에는 적용되지 않습니다.

노드는 네트워크 연결이 복원되거나 사전 설정된 암호가 콘솔에 수동으로 입력될 때까지 오프라인 상태로 유지됩니다. 예외적으로 네트워크 관리자는 액세스를 다시 설정하기 위해 네트워크 세그먼트를 재구성할 수 있지만, NBDE의 의도에 어긋나는 것으로 네트워크 액세스 권한이 부족하다는 것은 부팅 기능이 없다는 것을 의미합니다.

노드에서 네트워크 액세스 권한이 부족하면 노드의 기능 및 부팅 기능에 영향을 줄 것으로 예상할 수 있습니다. 노드가 수동 조작을 통해 부팅되는 경우에도 네트워크 액세스 부족으로 인해 거의 사용되지 않습니다.

#### 18.4.4. 수동으로 네트워크 연결 복구

네트워크 복구를 위해 현장 기술자도 다소 복잡하고 수동 집약적인 프로세스를 사용할 수 있습니다.

프로세스

현장 기술자는 하드 디스크에서 Clevis 헤더를 추출합니다. BIOS 잠금에 따라 이 작업을 수행하려면 디스크를 제거하고 랩 시스템에 설치해야 할 수 있습니다.

현장 기술자는 Tang 네트워크에 대한 합법적 액세스 권한이 있는 Clevis 헤더를 동료에게 전송합니다. 그런 다음 암호 해독을 수행합니다.

Tang 네트워크에 대한 제한된 액세스의 필요성으로 인해 기술자는 VPN 또는 기타 원격 연결을 통해 해당 네트워크에 액세스할 수 없어야 합니다. 마찬가지로 기술자는 디스크의 암호를 자동으로 해독하기 위해 원격 서버를 이 네트워크에 패치할 수 없습니다.

기술자는 디스크를 다시 설치하고 동료가 제공한 일반 텍스트 암호를 수동으로 입력합니다.

Tang 서버에 직접 액세스하지 않아도 시스템이 성공적으로 시작됩니다. 설치 사이트에서 네트워크 액세스가 가능한 다른 사이트로 주요 자료의 전송은 신중하게 수행해야 합니다.

네트워크 연결이 복원되면 기술자는 암호화 키를 교체합니다.

#### 18.4.5. 네트워크 연결의 긴급 복구

네트워크 연결을 수동으로 복구할 수 없는 경우 다음 단계를 고려하십시오. 네트워크 연결을 복구하는 다른 방법을 사용할 수 있는 경우 이러한 단계는 권장되지 않습니다.

이 방법은 매우 신뢰할 수 있는 기술자만 수행해야 합니다.

Tang 서버의 핵심 자료를 원격 사이트로 가져오는 것은 주요 자료의 위반으로 간주되며 모든 서버를 재암호화하고 다시 암호화해야 합니다.

이 방법은 극단적 사례에서만 사용하거나 실효성을 입증하기 위해 개념 증명 복구 방법으로 사용해야 합니다.

마찬가지로 극단적이지만 이론적으로 가능한 것은 무중단 전력 공급 장치(UPS)로 서버에 전원을 공급하고, 서버를 네트워크 연결이 있는 위치로 전송하여 디스크를 부팅하고 암호를 해독한 다음, 계속 작업을 계속하기 위해 원래 위치에 서버를 복원하는 것입니다.

백업 수동 암호를 사용하려면 오류 상황이 발생하기 전에 생성해야 합니다.

공격 시나리오가 독립 실행형 Tang 설치에 비해 TPM 및 Tang에서 더 복잡해지므로 동일한 방법을 활용하는 경우 긴급 재해 복구 프로세스도 더 복잡해집니다.

#### 18.4.6. 네트워크 세그먼트 손실

네트워크 세그먼트가 손실되어 Tang 서버를 일시적으로 사용할 수 없게 되므로 다음과 같은 결과가 발생합니다.

다른 서버를 사용할 수 있는 경우 OpenShift Container Platform 노드는 정상적으로 계속 부팅됩니다.

새 노드는 네트워크 세그먼트가 복원될 때까지 암호화 키를 설정할 수 없습니다. 이 경우 고가용성 및 중복성을 위해 원격 지리적 위치에 대한 연결을 확인하십시오. 새 노드를 설치하거나 기존 노드를 다시 시작하는 경우 해당 작업에서 참조하는 모든 Tang 서버를 사용할 수 있어야 하기 때문입니다.

각 클라이언트가 가장 가까운 세 클라이언트에 연결되어 있는 5개 지역과 같이 매우 다양한 네트워크를 위한 하이브리드 모델은 조사할 만한 가치가 있습니다.

이 시나리오에서 새 클라이언트는 연결할 수 있는 서버의 하위 집합을 사용하여 암호화 키를 설정할 수 있습니다. 예를 들어 `tang1`, `tang2` 및 `tang3` 서버 세트에서 `tang2` 에 연결할 수 없는 클라이언트가 여전히 `tang1` 및 `tang3` 을 사용하여 암호화 키를 설정할 수 있고 나중에 전체 세트로 다시 설정될 수 있습니다. 이로 인해 수동 조작이나 사용 가능한 더 복잡한 자동화가 포함될 수 있습니다.

#### 18.4.7. Tang 서버 손실

주요 자료가 동일한 서버 세트 내에서 부하 분산된 서버 집합 내에서 개별 Tang 서버가 손실되는 것은 클라이언트에 완전히 투명합니다.

동일한 URL(즉, 전체 부하 분산 집합)과 연결된 모든 Tang 서버의 일시적인 오류는 네트워크 세그먼트 손실과 동일하게 간주될 수 있습니다. 미리 구성된 다른 Tang 서버를 사용할 수 있는 한 기존 클라이언트는 디스크 파티션을 암호 해독할 수 있습니다. 새 클라이언트는 이러한 서버 중 하나 이상이 온라인 상태가 될 때까지 등록할 수 없습니다.

서버를 다시 설치하거나 백업에서 서버를 복원하여 Tang 서버의 물리적 손실을 완화할 수 있습니다. 주요 자료의 백업 및 복원 프로세스가 무단 액세스로부터 적절히 보호되는지 확인합니다.

#### 18.4.8. 손상된 주요 자료 키 재지정

Tang 서버 또는 관련 데이터의 물리적 도난을 통해 키 자료가 권한 없는 타사에 노출되는 경우 키를 즉시 교체합니다.

프로세스

영향을 받는 자료를 보관하는 모든 Tang 서버에 키를 다시 입력합니다.

Tang 서버를 사용하여 모든 클라이언트를 다시 입력합니다.

원래의 주요 자료를 삭제합니다.

마스터 암호화 키의 의도하지 않은 노출을 초리해는 모든 경우를 확인합니다. 가능한 경우 손상된 노드를 오프라인으로 사용하여 디스크를 다시 암호화합니다.

작은 정보

속도가 느리지만 동일한 물리적 하드웨어에 다시 포맷하고 다시 설치하면 자동화 및 테스트가 쉽습니다.
