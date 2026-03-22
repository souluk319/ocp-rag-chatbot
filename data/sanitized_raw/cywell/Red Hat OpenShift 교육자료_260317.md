<!-- source: Red Hat OpenShift 교육자료_260317.pptx -->

[슬라이드 2]
컨테이너와 Kubernetes로 여는 클라우드 네이티브 시대
Ⅰ.
Container
Kubernetes (K8s)

[슬라이드 3]
Resource 절감, dependency 해소
Container

[슬라이드 4]
Resource 절감, dependency 해소
Container
“ Build Once, Run Anywhere ”

[슬라이드 5]
Container
VM 간의 환경 불일치
느린 시작 시간
거대한 이미지 사이즈
VM은 템플릿 관리는 하지만 사이즈가 커서 재사용성을 높이기 어려움
부팅 시 Hypervisor – OS – 미들웨어 – 어플리케이션 순서로 실행
VM 생성 후 개별로 변경 사항을 관리하기 때문에 VM 간 구성이나 환경 불일치

[슬라이드 6]
Container
높은 이동성(Portability)
빠른 시작 시간
작은 이미지 사이즈
컨테이너는 레이어 개념으로 이미지에 파일을 추가/삭제하여 관리
컨테이너는 분리된 프로세스 형식으로 OS 부팅이 필요 없기 때문에 부팅 시간을 최소화
애플리케이션에 필요한 라이브러리나 의존 파일들을 이미지에 포함하기 때문에 환경에 의한 발행되는 문제가 거의 없음
Container = Process

[슬라이드 7]
Container
가상머신
컨테이너
OS
OS

[슬라이드 8]
Container
Linux
컨테이너 런타임

[슬라이드 9]
Container

[슬라이드 10]
Container
데모 영상 : 컨테이너의 빠른 시작
RHEL9 컨테이너 이미지(UBI9)를 다운로드
컨테이너 이미지(UBI9)가 있는지 확인
UBI9으로 컨테이너를 실행하여 컨테이너 내 쉘로 진입
/etc/os-release 파일을 통해 RHEL9 환경임을 확인
컨테이너로는 1분 안에 리눅스 환경 준비가 가능 확인

[슬라이드 11]
Container
데모 영상 : 컨테이너의 빠른 시작
RHEL9 컨테이너 이미지(UBI9)를 다운로드
컨테이너 이미지(UBI9)가 있는지 확인
UBI9으로 컨테이너를 실행하여 컨테이너 내 쉘로 진입
/etc/os-release 파일을 통해 RHEL9 환경임을 확인
컨테이너로는 1분 안에 리눅스 환경 준비가 가능 확인

[슬라이드 12]
Container
불변성 (Immutable)
동일한 컨테이너 이미지로 컨테이너를 생성되는 컨테이너도 매번 동일
휘발성 (Ephemeral)
컨테이너에서 변경한 부분은 컨테이너가 중지되면 사라짐 (컨테이너 자체에는 영속성 없음)
컨테이너를 변경하고 싶다면 컨테이너 이미지를 수정하고 새로운 컨테이너를 생성해야 함
(오래된 컨테이너는 폐기)

[슬라이드 13]
Container
데모 영상 : 컨테이너의 불변성 및 휘발성
RHEL9 컨테이너 이미지(UBI9)를 확인하고 실행하여 쉘에 진입
컨테이너의 루트 디렉토리 내용을 확인하고 변경
컨테이너를 종료하고 동일한 컨테이너를 다시 시작
변경하기 전의 상태로 되돌아갔으며, 앞서 변경한 내용은 없는 일이 된 것을 확인

[슬라이드 14]
Container
데모 영상 : 컨테이너의 불변성 및 휘발성
RHEL9 컨테이너 이미지(UBI9)를 확인하고 실행하여 쉘에 진입
컨테이너의 루트 디렉토리 내용을 확인하고 변경
컨테이너를 종료하고 동일한 컨테이너를 다시 시작
변경하기 전의 상태로 되돌아갔으며, 앞서 변경한 내용은 없는 일이 된 것을 확인

[슬라이드 15]
Container
컨테이너 이미지
컨테이너

[슬라이드 16]
Container
・・・

[슬라이드 17]
Container
컨테이너 이미지는 레이어 구조
컨테이너 이미지
Base Layer Image
Layer Image
Layer Image
컨테이너 이미지

[슬라이드 18]
Container
데모 영상 : 컨테이너 이미지 빌드
Dockerfile의 내용을 확인
Dockerfile로 컨테이너 이미지 빌드
새로운 컨테이너 이미지가 생성되었는지 확인
생성한 이미지로 컨테이너를 실행하면, Dockerfile에 작성한 대로 newdir과 messagefile이 생성된 것을 확인
RHEL9 이미지(UBI9)를 베이스로 함
루트 디렉토리에 새로운 디렉토리 (newdir)와 파일(messagefile)을 생성

[슬라이드 19]
Container
데모 영상 : 컨테이너 이미지 빌드
Dockerfile의 내용을 확인
Dockerfile로 컨테이너 이미지 빌드
새로운 컨테이너 이미지가 생성되었는지 확인
생성한 이미지로 컨테이너를 실행하면, Dockerfile에 작성한 대로 newdir과 messagefile이 생성된 것을 확인
RHEL9 이미지(UBI9)를 베이스로 함
루트 디렉토리에 새로운 디렉토리 (newdir)와 파일(messagefile)을 생성

[슬라이드 20]
컨테이너 기반 WAS
java_agent_install
├── Dockerfile
├── jennifer-agent-java-x.x.x.x.zip
├── jennifer.conf
└── setenv.sh
작업 디렉터리 구조
이미지 생성 절차 정의
Agent 설치 패키지
Jennifer Agent 설정 파일
Tomcat JVM 옵션 설정

[슬라이드 21]
컨테이너 기반 WAS

[슬라이드 22]
컨테이너 기반 WAS

[슬라이드 23]
컨테이너 기반 WAS

[슬라이드 24]
컨테이너 기반 WAS

[슬라이드 25]
Container
컨테이너 런타임은 컨테이너를 구동하는데 필수적인 요소
컨테이너를 운영/관리하기 위한 SW
컨테이너의 생성, 실행, 정지, 삭제 등
컨테이너의 라이프 사이클 관리
런타임이 없으면 컨테이너는 작동하지 않음
런타임 종류
로컬 환경에서 사용할 때
- Docker, Podman
컨테이너 기반 플랫폼에서 사용할 때
- Containerd, cri-o

[슬라이드 26]
클라우드 혁신:
컨테이너 오케스트레이션
Ⅱ.
Kubernetes/OpenShift

[슬라이드 27]
Kubernetes
오케스트라(Orchestra) = 지휘자 에서 파생된 단어로 다수의 컨테이너를 자동으로 배치, 관리, 확장, 복구하는 시스템.
사람이 직접 관리하기 힘든 작업(스케일링, 로드밸런싱, 장애복구 등)을 자동화한다.
Kubernetes (K8s)
OpenShift (OCP)

[슬라이드 28]
Kubernetes
컨테이너 런타임만 사용
컨테이너 오케스트레이터 사용
특정 개인에 의존적인 장애 복구 작업
수동으로 컨테이너 변경 작업
애플리케이션별 설정 관리
정기적인 모니터링 작업
비즈니스 변화에 따른 적절한 리소스 조정
전부 사람이 관리해야 함
많은 작업이 자동으로 실행됨

[슬라이드 29]
Kubernetes

[슬라이드 30]
Kubernetes

[슬라이드 31]
Kubernetes

[슬라이드 32]
Kubernetes

[슬라이드 33]
Kubernetes
Node
Node
Auto Scale

[슬라이드 34]
Kubernetes
Node
Node

[슬라이드 35]
Kubernetes
Namespace
Namespace

[슬라이드 36]
Kubernetes
“ Kubernetes에서 제공하지 않는 기능”

[슬라이드 37]
Kubernetes

[슬라이드 38]
Kubernetes
Kubernetes  아키텍처(Bastion)

[슬라이드 39]
Kubernetes
Kubernetes 아키텍처(Master Node)

[슬라이드 40]
Kubernetes
Kubernetes 아키텍처(Worker Node)

[슬라이드 41]
Kubernetes
Kubernetes 아키텍처(Infra/Router Node)

[슬라이드 42]
Kubernetes

[슬라이드 43]
Kubernetes
파드(Pod) - 쿠버네티스에서 생성하고 관리할 수 있는 배포 가능한 가장 작은 컴퓨팅 단위

[슬라이드 44]
Kubernetes
Pod
역할
테스트용
단일 컨테이너 실행
특징
장애가 나면 스스로 복구 불가 → 상위 리소스 필요

[슬라이드 45]
Kubernetes

[슬라이드 46]
Kubernetes
ReplicaSet
역할
Pod의 개수를 보장
특징
장애 발생 시 지정된 개수를 유지하지만 버전 관리 등 업데이트 전략 없음 → Deployment가 대신 관리

[슬라이드 47]
Kubernetes

[슬라이드 48]
Kubernetes
Deployment
역할
서비스 운영의 기본 단위
특징
롤링 업데이트
롤백
오토 스케일링 지원

[슬라이드 49]
Kubernetes

[슬라이드 50]
Kubernetes
Control plane
Compute plane
[ Kubernetes 동작원리 ]

[슬라이드 51]
Kubernetes
Sys admin

[슬라이드 52]
Kubernetes
Namespace

[슬라이드 53]
Kubernetes
Service/INGRESS

[슬라이드 54]
Kubernetes

[슬라이드 55]
Kubernetes

[슬라이드 56]
Kubernetes

[슬라이드 57]
Kubernetes

[슬라이드 58]
Kubernetes

[슬라이드 59]
Kubernetes

[슬라이드 60]
Kubernetes
Persistent
Storage

[슬라이드 61]
Kubernetes

[슬라이드 62]
Kubernetes

[슬라이드 63]
Kubernetes

[슬라이드 64]
Kubernetes

[슬라이드 65]
Kubernetes

[슬라이드 66]
Kubernetes

[슬라이드 67]
클라우드 혁신: OpenShift 이해
Ⅱ.
OpenShift

[슬라이드 68]
OpenShift
통합된 개발자 워크플로
관찰 가능성
서버 관리

[슬라이드 69]
OpenShift
요구사항에 맞는 다양한 에디션을 사용 가능

[슬라이드 70]
OpenShift
“ OpenShift의 5가지 특징 ”

[슬라이드 71]
OpenShift
Source to Image 빌드
애플리케이션 소스 코드와 베이스 이미지를 동적으로 빌드하는 기능(S2I)이 있어 개발자는 소스 코드 개발에 집중

[슬라이드 72]
OpenShift
업데이트
승인

[슬라이드 73]
OpenShift
Operator는 Kubernetes에서 미들웨어와 애플리케이션을 동적으로 배포하고 관리하기 위한 수단
Kubernetes 리소스와 컨트롤러를 기반으로 하며, 운영자를 대신하여 미들웨어의 복잡한 설치, 설정, 운영, 관리 작업을 실행

[슬라이드 74]
OpenShift
OperatorHub
OperatorHub를 통해 다양한 미들웨어가 제공되며, Operator를 이용하면 각 미들웨어의 설치, 설정, 모니터링, 업그레이드 등 운영 작업을 자동화할 수 있습니다.

[슬라이드 75]
OpenShift
Operator의 종류
Red Hat이 패키징하고 딜리버리하는 Red Hat 제품
Red Hat이 지원
주요 독립 소프트웨어 벤더(ISV)가 제공하는 제품
Red Hat은 ISV와의 파트너쉽을 통해 패키징 및 딜리버리를 담당
ISV에서 지원
GitHub 리포지토리에 있는 각 프로젝트에서 유지보수하는 소프트웨어
공식적으로 지원은 제공되지 않음

[슬라이드 76]
OpenShift
Cluster Monitoring
OpenShift를 설치하면, 클러스터에 대한 모니터링은 Cluster Monitoring(Prometheus)을 통해 이미 설치 및 설정되어 있습니다. (초기 설정 및 업데이트 작업은 자동으로 설정 됩니다.)

[슬라이드 77]
OpenShift
Cluster Logging
Cluster Logging을 활성화하면 각 Pod, Cluster에서 출력되는 로그를 Loki에 저장할 수 있습니다.
저장된 로그는 App, Infra, Audit 단위로 분류되어 콘솔에서 확인할 수 있습니다.

[슬라이드 78]
OpenShift
컨테이너 기반을 지원하는 RHCOS
컨테이너 이용에 최적화된 RHCOS (Red Hat Enterprise Linux CoreOS)를 활용하여 보다 안전하고 안정적인 컨테이너 환경을 제공합니다.
OpenShift와 연동해서, 동적 업그레이드를 One-Click으로 실현
라이브러리가 적기 때문에 보안 취약점 발생 가능성이 매우 낮음
라이브러리가 적기 때문에 많은 프로그램이 OS내에서 구동되지 않음

[슬라이드 79]
OpenShift
베이스 이미지 제공
컨테이너 베이스 이미지를 Red Hat Ecosystem Catalog에서 제공하고 있으며, 보안 취약점 진단 내용도 바로 확인할 수 있어 안심하고 컨테이너 이미지를 사용할 수 있습니다.

[슬라이드 80]
OpenShift
OpenShift의 버전 업그레이드
클릭 한 번으로 OpenShift 클러스터를 업데이트하는 ‘OTA(Over-the-Air) 업데이트’ 기능을 제공 및 구성 요소별로 관리
“ One-click Upgrade ”
