# 스토리지

## OpenShift Container Platform에서 스토리지 구성 및 사용

이 문서에서는 다양한 스토리지 백엔드에서 영구 볼륨을 구성하고 Pod의 동적 할당을 관리하는 방법을 설명합니다.

## 1장. OpenShift Container Platform 스토리지 개요

OpenShift Container Platform에서는 온프레미스 및 클라우드 공급자를 위해 여러 유형의 스토리지를 지원합니다. OpenShift Container Platform 클러스터에서 영구 및 비영구 데이터에 대한 컨테이너 스토리지를 관리할 수 있습니다.

### 1.1. OpenShift Container Platform 스토리지의 일반 용어집

이 용어집은 스토리지 콘텐츠에 사용되는 일반적인 용어를 정의합니다.

액세스 모드

볼륨 액세스 모드는 볼륨 기능을 설명합니다. 액세스 모드를 사용하여 PVC(영구 볼륨 클레임) 및 PV(영구 볼륨)와 일치시킬 수 있습니다. 다음은 액세스 모드의 예입니다.

ReadWriteOnce (RWO)

ReadOnlyMany (ROX)

ReadWriteMany (RWX)

ReadWriteOncePod (RWOP)

Cinder

모든 볼륨의 관리, 보안 및 스케줄링을 관리하는 RHOSP(Red Hat OpenStack Platform)용 블록 스토리지 서비스입니다.

구성 맵

구성 맵에서는 구성 데이터를 Pod에 삽입하는 방법을 제공합니다. 구성 맵에 저장된 데이터를 `ConfigMap` 유형의 볼륨에서 참조할 수 있습니다. Pod에서 실행되는 애플리케이션에서는 이 데이터를 사용할 수 있습니다.

CSI(Container Storage Interface)

다양한 컨테이너 오케스트레이션(CO) 시스템에서 컨테이너 스토리지를 관리하기 위한 API 사양입니다.

동적 프로비저닝

프레임워크를 사용하면 필요에 따라 스토리지 볼륨을 생성할 수 있으므로 클러스터 관리자가 영구 스토리지를 사전 프로비저닝할 필요가 없습니다.

임시 스토리지

Pod 및 컨테이너는 작업을 위해 임시 또는 일시적인 로컬 스토리지가 필요할 수 있습니다. 이러한 임시 스토리지의 수명은 개별 Pod의 수명 이상으로 연장되지 않으며 이 임시 스토리지는 여러 Pod 사이에서 공유할 수 없습니다.

파이버 채널

데이터 센터, 컴퓨터 서버, 스위치 및 스토리지 간에 데이터를 전송하는 데 사용되는 네트워킹 기술입니다.

FlexVolume

FlexVolume은 exec 기반 모델을 사용하여 스토리지 드라이버와 연결하는 out-of-tree 플러그인 인터페이스입니다. 각 노드의 사전 정의된 볼륨 플러그인 경로에 FlexVolume 드라이버 바이너리를 설치해야 하며 경우에 따라 컨트롤 플레인 노드를 설치해야 합니다.

fsGroup

fsGroup은 Pod의 파일 시스템 그룹 ID를 정의합니다.

iSCSI

iSCSI(Internet Small Computer Systems Interface)는 데이터 스토리지 기능을 연결하는 인터넷 프로토콜 기반 스토리지 네트워킹 표준입니다. iSCSI 볼륨을 사용하면 IP를 통한 기존 iSCSI(SCSI) 볼륨을 Pod에 마운트할 수 있습니다.

hostPath

OpenShift Container Platform 클러스터의 hostPath 볼륨은 호스트 노드 파일 시스템의 파일 또는 디렉터리를 Pod에 마운트합니다.

KMS key

KMS(Key Management Service)는 다양한 서비스에서 데이터의 필수 암호화 수준을 달성하는 데 도움이 됩니다. KMS 키를 사용하여 데이터를 암호화, 암호 해독 및 재암호화할 수 있습니다.

로컬 볼륨

로컬 볼륨은 디스크, 파티션 또는 디렉터리와 같은 마운트된 로컬 스토리지 장치를 나타냅니다.

중첩된 마운트 지점

중첩된 마운트 지점은 이전 볼륨에서 생성한 마운트 지점을 사용하려는 마운트 지점입니다.

```shell-session
kind: Pod
apiVersion: v1
metadata:
  name: webapp
  labels:
    name: webapp
spec:
  containers:
    - name: webapp
      image: nginx
      ports:
        - containerPort: 80
          name: "http-server"
      volumeMounts:
      - mountPath: /mnt/web
        name: web
      - mountPath: /mnt/web/redis
        name: redis
  volumes:
    - name: redis
      persistentVolumeClaim:
       claimName: "redis"
    - name: web
      persistentVolumeClaim:
        claimName: "web"
```

1. 중첩된 마운트 지점

OpenShift Container Platform에서 마운트 지점이 생성되는 순서를 보장하지 않으므로 중첩된 마운트 지점을 사용하지 마십시오. 이러한 사용은 조건과 정의되지 않은 동작을 경쟁하기 쉽습니다.

NFS

원격 호스트가 네트워크를 통해 파일 시스템을 마운트하고 로컬에 마운트된 것처럼 해당 파일 시스템과 상호 작용할 수 있는 NFS(네트워크 파일 시스템)입니다. 이를 통해 시스템 관리자는 네트워크의 중앙 집중식 서버에 리소스를 통합할 수 있습니다.

OpenShift Data Foundation

파일, 블록 및 오브젝트 스토리지를 지원하는 OpenShift Container Platform용 영구 스토리지 공급자(내부 또는 하이브리드 클라우드)

영구 스토리지

Pod 및 컨테이너는 작업을 위해 영구 스토리지가 필요할 수 있습니다. OpenShift Container Platform에서는 Kubernetes PV(영구 볼륨) 프레임워크를 사용하여 클러스터 관리자가 클러스터의 영구 스토리지를 프로비저닝할 수 있습니다. 개발자는 기본 스토리지 인프라에 대한 특정 지식 없이도 PVC를 사용하여 PV 리소스를 요청할 수 있습니다.

영구 볼륨(PV)

OpenShift Container Platform에서는 Kubernetes PV(영구 볼륨) 프레임워크를 사용하여 클러스터 관리자가 클러스터의 영구 스토리지를 프로비저닝할 수 있습니다. 개발자는 기본 스토리지 인프라에 대한 특정 지식 없이도 PVC를 사용하여 PV 리소스를 요청할 수 있습니다.

PVC(영구 볼륨 클레임)

PVC를 사용하여 PersistentVolume을 포드에 마운트할 수 있습니다. 클라우드 환경의 세부 사항을 모르는 상태에서 스토리지에 액세스할 수 있습니다.

Pod

OpenShift Container Platform 클러스터에서 실행되는 볼륨 및 IP 주소와 같은 공유 리소스가 있는 하나 이상의 컨테이너입니다. Pod는 정의, 배포 및 관리되는 최소 컴퓨팅 단위입니다.

회수 정책

해제 후 볼륨을 사용하여 클러스터에 수행할 작업을 알려주는 정책입니다. 볼륨 회수 정책은 `Retain`, `Recycle` 또는 `Delete` 일 수 있습니다.

RBAC(역할 기반 액세스 제어)

RBAC(역할 기반 액세스 제어)는 조직 내의 개별 사용자 역할에 따라 컴퓨터 또는 네트워크 리소스에 대한 액세스를 조정하는 방법입니다.

상태 비저장 애플리케이션

상태 비저장 애플리케이션은 해당 클라이언트와의 다음 세션에서 사용하기 위해 한 세션에서 생성된 클라이언트 데이터를 저장하지 않는 애플리케이션 프로그램입니다.

상태 저장 애플리케이션

상태 저장 애플리케이션은 데이터를 영구 디스크 스토리지에 저장하는 애플리케이션 프로그램입니다. 서버, 클라이언트 및 애플리케이션에서는 영구 디스크 스토리지를 사용할 수 있습니다. OpenShift Container Platform에서 `Statefulset` 오브젝트를 사용하여 Pod 세트의 배포 및 스케일링을 관리하고 이러한 Pod의 순서 및 고유성에 대해 보장할 수 있습니다.

정적 프로비저닝

클러스터 관리자는 여러 PV를 생성합니다. PV에는 스토리지 세부 정보가 포함됩니다. PV는 Kubernetes API에 있으며 사용할 수 있습니다.

스토리지

OpenShift Container Platform은 온프레미스 및 클라우드 공급자를 위해 다양한 유형의 스토리지를 지원합니다. OpenShift Container Platform 클러스터에서 영구 및 비영구 데이터에 대한 컨테이너 스토리지를 관리할 수 있습니다.

스토리지 클래스

스토리지 클래스는 관리자가 제공하는 스토리지 클래스를 설명할 수 있는 방법을 제공합니다. 다른 클래스는 서비스 수준, 백업 정책, 클러스터 관리자가 결정하는 임의의 정책에 매핑될 수 있습니다.

VMware vSphere의 VMI(가상 머신 디스크) 볼륨

VMI(가상 머신 디스크)는 가상 머신에 사용되는 가상 하드 디스크 드라이브의 컨테이너를 설명하는 파일 형식입니다.

### 1.2. 스토리지 유형

OpenShift Container Platform 스토리지는 일반적으로 임시 스토리지와 영구저장장치라는 두 가지 범주로 분류됩니다.

#### 1.2.1. 임시 스토리지

Pod 및 컨테이너는 임시 또는 일시적인 것이며 상태 비저장 애플리케이션을 위해 설계되었습니다. 임시 스토리지를 사용하면 관리자와 개발자가 일부 작업의 로컬 스토리지를 보다 효과적으로 관리할 수 있습니다. 임시 스토리지 개요, 유형 및 관리에 대한 자세한 내용은 임시 스토리지 이해 를 참조하십시오.

#### 1.2.2. 영구 스토리지

컨테이너에 배포된 상태 저장 애플리케이션에는 영구 스토리지가 필요합니다. OpenShift Container Platform에서는 PV(영구 볼륨)라는 사전 프로비저닝된 스토리지 프레임워크를 사용하여 클러스터 관리자가 영구 스토리지를 프로비저닝할 수 있습니다. 이러한 볼륨 내부의 데이터는 개별 Pod의 라이프사이클 이상으로 존재할 수 있습니다. 개발자는 PVC(영구 볼륨 클레임)를 사용하여 스토리지 요구 사항을 요청할 수 있습니다. 영구 스토리지 개요, 구성 및 라이프사이클에 대한 자세한 내용은 영구 스토리지 이해 를 참조하십시오.

### 1.3. CSI(Container Storage Interface)

CSI는 다양한 컨테이너 오케스트레이션(CO) 시스템에서 컨테이너 스토리지를 관리하기 위한 API 사양입니다. 기본 스토리지 인프라에 대한 구체적인 지식이 없어도 컨테이너 네이티브 환경에서 스토리지 볼륨을 관리할 수 있습니다. CSI를 사용하면 사용 중인 스토리지 벤더에 관계없이 스토리지가 다양한 컨테이너 오케스트레이션 시스템에서 균일하게 작동합니다. CSI에 대한 자세한 내용은 CSI(Container Storage Interface) 사용을 참조하십시오.

### 1.4. 동적 프로비저닝

동적 프로비저닝을 사용하면 필요에 따라 스토리지 볼륨을 생성할 수 있으므로 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없습니다. 동적 프로비저닝에 대한 자세한 내용은 동적 프로비저닝 을 참조하십시오.

### 2.1. 개요

Pod 및 컨테이너는 임시 또는 일시적인 것이며 상태 비저장 애플리케이션을 위해 설계되었습니다. 임시 스토리지를 사용하면 관리자와 개발자가 일부 작업의 로컬 스토리지를 보다 효과적으로 관리할 수 있습니다.

영구 스토리지 외에도 Pod 및 컨테이너는 작업을 위해 임시 또는 임시 로컬 스토리지가 필요할 수 있습니다. 이러한 임시 스토리지의 수명은 개별 Pod의 수명 이상으로 연장되지 않으며 이 임시 스토리지는 여러 Pod 사이에서 공유할 수 없습니다.

Pod는 스크래치 공간, 캐싱 및 로그를 위해 임시 로컬 스토리지를 사용합니다. 로컬 스토리지 회계 및 격리 부족과 관련한 문제는 다음과 같습니다.

Pod는 사용할 수 있는 로컬 스토리지 양을 감지할 수 없습니다.

Pod는 보장되는 로컬 스토리지를 요청할 수 없습니다.

로컬 스토리지는 최상의 리소스입니다.

Pod는 로컬 스토리지를 채우는 다른 Pod로 인해 제거할 수 있으며 충분한 스토리지를 회수할 때까지 새 Pod가 허용되지 않습니다.

영구 볼륨에 대해 임시 스토리지는 구조화되지 않으며 시스템에서 실행되는 모든 Pod와 시스템, 컨테이너 런타임 및 OpenShift Container Platform의 다른 사용에서 공간을 공유합니다. 임시 스토리지 프레임워크를 사용하면 Pod에서 일시적인 로컬 스토리지 요구를 지정할 수 있습니다. 또한, OpenShift Container Platform은 적절한 Pod를 예약하고 로컬 스토리지를 과도하게 사용하지 않도록 노드를 보호할 수 있습니다.

임시 스토리지 프레임워크를 사용하면 관리자와 개발자가 로컬 스토리지를 보다 효과적으로 관리할 수 있지만 I/O 처리량과 대기 시간은 직접적인 영향을 받지 않습니다.

### 2.2. 임시 스토리지 유형

임시 로컬 스토리지는 항상 기본 파티션에서 사용할 수 있습니다. 기본 파티션을 생성하는 방법에는 루트 및 런타임이라는 두 가지 기본적인 방법이 있습니다.

#### 2.2.1. 루트

이 파티션에는 기본적으로 kubelet 루트 디렉터리인 `/var/lib/kubelet/` 및 `/var/log/` 디렉터리가 있습니다. 이 파티션은 사용자 Pod, OS, Kubernetes 시스템 데몬 간에 공유할 수 있습니다. 이 파티션은 `EmptyDir` 볼륨, 컨테이너 로그, 이미지 계층 및 container-wriable 계층을 통해 Pod에서 사용할 수 있습니다. kubelet은 이 파티션의 공유 액세스 및 격리를 관리합니다. 이 파티션은 임시입니다. 애플리케이션은 이 파티션에서 디스크 IOPS와 같은 성능 SLA를 기대할 수 없습니다.

#### 2.2.2. 런타임

런타임에서 오버레이 파일 시스템에 사용할 수 있는 선택적 파티션입니다. OpenShift Container Platform에서는 이 파티션에 대한 격리와 함께 공유 액세스를 식별하고 제공합니다. 컨테이너 이미지 계층 및 쓰기 가능한 계층이 여기에 저장됩니다. 런타임 파티션이 있는 경우 `루트` 파티션은 이미지 계층 또는 기타 쓰기 가능한 스토리지를 유지하지 않습니다.

### 2.3. 임시 데이터 스토리지 관리

클러스터 관리자는 비종료 상태의 모든 Pod에서 임시 스토리지에 대한 제한 범위 및 요청 수를 정의하는 할당량을 설정하여 프로젝트 내에서 임시 스토리지를 관리할 수 있습니다. 개발자는 Pod 및 컨테이너 수준에서 이러한 컴퓨팅 리소스에 대한 요청 및 제한을 설정할 수도 있습니다.

요청 및 제한을 지정하여 로컬 임시 스토리지를 관리할 수 있습니다. Pod의 각 컨테이너는 다음을 지정할 수 있습니다.

`spec.containers[].resources.limits.ephemeral-storage`

`spec.containers[].resources.requests.ephemeral-storage`

#### 2.3.1. 임시 스토리지 제한 및 요청 단위

임시 스토리지의 제한 및 요청은 바이트 수로 측정됩니다. 스토리지를 일반 정수 또는 E, P, T, G, M, k 접미사 중 하나를 사용하여 고정 소수점 숫자로 나타낼 수 있습니다. Ei, Pi, Ti, Gi, Mi, Ki와 같은 Power-of-two를 사용할 수도 있습니다.

예를 들어 다음 양은 모두 1289748, 129e6, 129M 및 123Mi의 약 동일한 값을 나타냅니다.

중요

각 바이트 수의 접미사는 대소문자를 구분합니다. 올바른 케이스를 사용해야 합니다. "400M"에 사용된 것과 같이 대소문자를 구분하는 "M"을 사용하여 요청을 400 메가바이트로 설정합니다. 대소문자를 구분하는 "400Mi"를 사용하여 400 메비 바이트를 요청합니다. 임시 스토리지의 "400m"을 지정하는 경우 스토리지 요청은 0.4바이트에 불과합니다.

#### 2.3.2. 임시 스토리지 요청 및 제한 예

다음 예제 구성 파일은 두 개의 컨테이너가 있는 Pod를 보여줍니다.

각 컨테이너는 2GiB의 로컬 임시 스토리지를 요청합니다.

각 컨테이너에는 4GiB의 로컬 임시 스토리지 제한이 있습니다.

Pod 수준에서 kubelet은 해당 Pod의 모든 컨테이너 제한을 추가하여 전체 Pod 스토리지 제한을 제거합니다.

이 경우 Pod 수준의 총 스토리지 사용량은 모든 컨테이너의 디스크 사용량 합계와 Pod의 `emptyDir` 볼륨 합계입니다.

따라서 Pod에는 4GiB의 로컬 임시 스토리지 요청이 있고 로컬 임시 스토리지의 8GiB 제한이 있습니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: frontend
spec:
  containers:
  - name: app
    image: images.my-company.example/app:v4
    resources:
      requests:
        ephemeral-storage: "2Gi"
      limits:
        ephemeral-storage: "4Gi"
    volumeMounts:
    - name: ephemeral
      mountPath: "/tmp"
  - name: log-aggregator
    image: images.my-company.example/log-aggregator:v6
    resources:
      requests:
        ephemeral-storage: "2Gi"
      limits:
        ephemeral-storage: "4Gi"
    volumeMounts:
    - name: ephemeral
      mountPath: "/tmp"
  volumes:
    - name: ephemeral
      emptyDir: {}
```

1. 로컬 임시 스토리지에 대한 컨테이너 요청입니다.

2. 로컬 임시 스토리지에 대한 컨테이너 제한입니다.

#### 2.3.3. 임시 스토리지 구성 효과 Pod 예약 및 제거

Pod 사양의 설정은 스케줄러가 Pod 예약에 대한 결정을 내리는 방법과 kubelet이 Pod를 제거하는 경우 모두에 영향을 미칩니다.

먼저 스케줄러는 예약된 컨테이너의 리소스 요청 합계가 노드의 용량보다 적은지 확인합니다. 이 경우 노드의 사용 가능한 임시 스토리지(항상 리소스)가 4GiB를 초과하는 경우에만 Pod를 노드에 할당할 수 있습니다.

두 번째는 컨테이너 수준에서 첫 번째 컨테이너가 리소스 제한을 설정하기 때문에 kubelet 제거 관리자는 이 컨테이너의 디스크 사용량을 측정하고 컨테이너의 스토리지 사용량이 제한을 초과하는 경우 Pod를 제거합니다(4GiB). 또한 kubelet 제거 관리자는 총 사용량이 전체 Pod 스토리지 제한 (8GiB)을 초과하는 경우 제거 Pod를 표시합니다.

프로젝트의 할당량을 정의하는 방법에 대한 자세한 내용은 프로젝트당 할당량 설정을 참조하십시오.

### 2.4. 임시 스토리지 모니터링

`/bin/df` 를 임시 컨테이너 데이터가 위치하는 볼륨에서 임시 스토리지의 사용을 모니터링하는 도구를 사용할 수 있으며, 이는 `/var/lib/kubelet` 및 `/var/lib/containers` 입니다. 클러스터 관리자가 `/var/lib/containers` 를 별도의 디스크에 배치한 경우에는 `df` 명령을 사용하여 `/var/lib/kubelet` 에서 전용으로 사용할 수 있는 공간을 표시할 수 있습니다.

절차

`/var/lib` 에서 사용된 공간 및 사용할 수 있는 공간을 사람이 읽을 수 있는 값으로 표시하려면 다음 명령을 입력합니다.

```shell-session
$ df -h /var/lib
```

출력에는 `/var/lib` 에서의 임시 스토리지 사용량이 표시됩니다.

```shell-session
Filesystem  Size  Used Avail Use% Mounted on
/dev/disk/by-partuuid/4cd1448a-01    69G   32G   34G  49% /
```

### 3.1. 영구 스토리지 개요

컨테이너에 배포된 상태 저장 애플리케이션에는 영구 스토리지가 필요합니다. {microshift-short}은 PV(영구 볼륨)라는 사전 프로비저닝된 스토리지 프레임워크를 사용하여 노드 관리자가 영구 스토리지를 프로비저닝할 수 있도록 합니다. 이러한 볼륨 내부의 데이터는 개별 Pod의 라이프사이클 이상으로 존재할 수 있습니다. 개발자는 PVC(영구 볼륨 클레임)를 사용하여 스토리지 요구 사항을 요청할 수 있습니다.

스토리지 관리는 컴퓨팅 리소스 관리와 다릅니다. OpenShift Container Platform에서는 Kubernetes PV(영구 볼륨) 프레임워크를 사용하여 클러스터 관리자가 클러스터의 영구 스토리지를 프로비저닝할 수 있습니다. 개발자는 PVC(영구 볼륨 클레임)를 사용하여 기본 스토리지 인프라를 구체적으로 잘 몰라도 PV 리소스를 요청할 수 있습니다.

PVC는 프로젝트별로 고유하며 PV를 사용하는 방법과 같이 개발자가 생성 및 사용할 수 있습니다. 자체 PV 리소스는 단일 프로젝트로 범위가 지정되지 않으며 전체 OpenShift Container Platform 노드에서 공유되고 모든 프로젝트에서 요청할 수 있습니다. PV가 PVC에 바인딩된 후에는 해당 PV를 다른 PVC에 바인딩할 수 없습니다. 이는 바인딩 프로젝트인 단일 네임스페이스로 바인딩된 PV의 범위를 지정하는 효과가 있으며, 이는 바인딩된 프로젝트의 범위가 됩니다.

PV는 `PersistentVolume` API 오브젝트로 정의되면, 이는 클러스터 관리자가 정적으로 프로비저닝하거나 `StorageClass` 오브젝트를 사용하여 동적으로 프로비저닝한 클러스터에서의 기존 스토리지 조각을 나타냅니다. 그리고 노드가 클러스터 리소스인 것과 마찬가지로 클러스터의 리소스입니다.

PV는 `Volumes` 과 같은 볼륨 플러그인이지만 PV를 사용하는 개별 Pod와는 독립적인 라이프사이클이 있습니다. PV 오브젝트는 NFS, iSCSI 또는 클라우드 공급자별 스토리지 시스템에서 스토리지 구현의 세부 정보를 캡처합니다.

중요

인프라의 스토리지의 고가용성은 기본 스토리지 공급자가 담당합니다.

PVC는 `PersistentVolumeClaim` API 오브젝트에 의해 정의되며, 개발자의 스토리지 요청을 나타냅니다. Pod는 노드 리소스를 사용하고 PVC는 PV 리소스를 사용하는 점에서 Pod와 유사합니다. 예를 들어, Pod는 CPU 및 메모리와 같은 특정 리소스를 요청할 수 있지만 PVC는 특정 스토리지 용량 및 액세스 모드를 요청할 수 있습니다. 예를 들어, Pod는 1회 읽기-쓰기 또는 여러 번 읽기 전용으로 마운트될 수 있습니다.

### 3.2. 볼륨 및 클레임의 라이프사이클

PV는 클러스터의 리소스입니다. PVC는 그러한 리소스에 대한 요청이며, 리소스에 대한 클레임을 검사하는 역할을 합니다. PV와 PVC 간의 상호 작용에는 다음과 같은 라이프사이클이 있습니다.

#### 3.2.1. 스토리지 프로비저닝

PVC에 정의된 개발자의 요청에 대한 응답으로 클러스터 관리자는 스토리지 및 일치하는 PV를 프로비저닝하는 하나 이상의 동적 프로비저너를 구성합니다.

다른 방법으로 클러스터 관리자는 사용할 수 있는 실제 스토리지의 세부 정보를 전달하는 여러 PV를 사전에 생성할 수 있습니다. PV는 API에 위치하며 사용할 수 있습니다.

#### 3.2.2. 클레임 바인딩

PVC를 생성할 때 스토리지의 특정 용량을 요청하고, 필요한 액세스 모드를 지정하며, 스토리지를 설명 및 분류하는 스토리지 클래스를 만듭니다. 마스터의 제어 루프는 새 PVC를 감시하고 새 PVC를 적절한 PV에 바인딩합니다. 적절한 PV가 없으면 스토리지 클래스를 위한 프로비저너가 PV를 1개 생성합니다.

전체 PV의 크기는 PVC 크기를 초과할 수 있습니다. 이는 특히 수동으로 프로비저닝된 PV의 경우 더욱 그러합니다. 초과를 최소화하기 위해 OpenShift Container Platform은 기타 모든 조건과 일치하는 최소 PV로 바인딩됩니다.

일치하는 볼륨이 없거나 스토리지 클래스에 서비스를 제공하는 사용할 수 있는 프로비저너로 생성할 수 없는 경우 클레임은 영구적으로 바인딩되지 않습니다. 일치하는 볼륨을 사용할 수 있을 때 클레임이 바인딩됩니다. 예를 들어, 수동으로 프로비저닝된 50Gi 볼륨이 있는 클러스터는 100Gi 요청하는 PVC와 일치하지 않습니다. 100Gi PV가 클러스터에 추가되면 PVC를 바인딩할 수 있습니다.

#### 3.2.3. Pod 및 클레임된 PV 사용

Pod는 클레임을 볼륨으로 사용합니다. 클러스터는 클레임을 검사하여 바인딩된 볼륨을 찾고 Pod에 해당 볼륨을 마운트합니다. 여러 액세스 모드를 지원하는 그러한 볼륨의 경우 Pod에서 클레임을 볼륨으로 사용할 때 적용되는 모드를 지정해야 합니다.

클레임이 있고 해당 클레임이 바인딩되면, 바인딩된 PV는 필요한 동안 사용자의 소유가 됩니다. Pod의 볼륨 블록에 `persistentVolumeClaim` 을 포함하여 Pod를 예약하고 클레임된 PV에 액세스할 수 있습니다.

참고

파일 수가 많은 영구 볼륨을 Pod에 연결하면 해당 Pod가 실패하거나 시작하는 데 시간이 오래 걸릴 수 있습니다. 자세한 내용은 OpenShift에서 파일 수가 많은 영구 볼륨을 사용하는 경우 Pod를 시작하지 못하거나 "Ready" 상태를 달성하는 데 과도한 시간이 걸리는 이유를 참조하십시오.

#### 3.2.4. 사용 중 스토리지 오브젝트 보호

사용 중 스토리지 오브젝트 보호 기능은 Pod에서 사용 중인 PVC와 PVC에 바인딩된 PC가 시스템에서 제거되지 않도록 합니다. 제거되면 데이터가 손실될 수 있습니다.

사용 중 스토리지 오브젝트 보호는 기본적으로 활성화됩니다.

참고

PVC를 사용하는 `Pod` 오브젝트가 존재하는 경우 PVC는 Pod에 의해 활성 사용 중이 됩니다.

사용자가 Pod에서 활성 사용 중인 PVC를 삭제하면 PVC가 즉시 제거되지 않습니다. 모든 Pod에서 PVC를 더 이상 활성 사용하지 않을 때까지 PVC의 제거가 연기됩니다. 또한, 클러스터 관리자가 PVC에 바인딩된 PV를 삭제하는 경우에도 PV가 즉시 제거되지 않습니다. PV가 더 이상 PVC에 바인딩되지 않을 때까지 PV 제거가 연기됩니다.

#### 3.2.5. 영구 볼륨 해제

볼륨 사용 작업이 끝나면 API에서 PVC 오브젝트를 삭제하여 리소스를 회수할 수 있습니다. 클레임이 삭제되었지만 다른 클레임에서 아직 사용할 수 없을 때 볼륨은 해제된 것으로 간주됩니다. 이전 클레임의 데이터는 볼륨에 남아 있으며 정책에 따라 처리되어야 합니다.

#### 3.2.6. 영구 볼륨 회수 정책

영구 볼륨 회수 정책은 해제된 볼륨에서 수행할 작업을 클러스터에 명령합니다. 볼륨 회수 정책은 `Retain`, `Recycle` 또는 `Delete` 일 수 있습니다.

`Retain` 정책을 유지하면 이를 지원하는 해당 볼륨 플러그인에 대한 리소스를 수동으로 회수할 수 있습니다.

`Recycle` 회수 정책은 볼륨이 클레임에서 해제되면 바인딩되지 않은 영구 볼륨 풀로 다시 재활용합니다.

중요

OpenShift Container Platform 4에서는 `Recycle` 회수 정책이 사용되지 않습니다. 기능을 향상하기 위해 동적 프로비저닝이 권장됩니다.

`삭제` 회수 정책은 OpenShift Container Platform에서 `PersistentVolume` 오브젝트와 Amazon EBS(Amazon EBS) 또는 VMware vSphere와 같은 외부 인프라의 관련 스토리지 자산을 모두 삭제합니다.

참고

동적으로 프로비저닝된 볼륨은 항상 삭제됩니다.

#### 3.2.7. 수동으로 영구 볼륨 회수

PVC(영구 볼륨 클레임)가 삭제되어도 PV(영구 볼륨)는 계속 존재하며 "해제됨"으로 간주됩니다. 그러나 이전 클레임의 데이터가 볼륨에 남아 있으므로 다른 클레임에서 PV를 아직 사용할 수 없습니다.

절차

클러스터 관리자로 PV를 수동으로 회수하려면 다음을 수행합니다.

다음 명령을 실행하여 PV를 삭제합니다.

```shell-session
$ oc delete pv <pv_name>
```

AWS EBS, GCE PD, Azure Disk 또는 Cinder 볼륨과 같은 외부 인프라의 연결된 스토리지 자산은 PV가 삭제된 후에도 계속 존재합니다.

연결된 스토리지 자산에서 데이터를 정리합니다.

연결된 스토리지 자산을 삭제합니다. 대안으로, 동일한 스토리지 자산을 재사용하려면, 스토리지 자산 정의를 사용하여 새 PV를 생성합니다.

이제 회수된 PV를 다른 PVC에서 사용할 수 있습니다.

#### 3.2.8. 영구 볼륨의 회수 정책 변경

영구 볼륨의 회수 정책을 변경할 수 있습니다.

절차

클러스터의 영구 볼륨을 나열합니다.

```shell-session
$ oc get pv
```

```shell-session
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim3    manual                     3s
```

영구 볼륨 중 하나를 선택하고 다음과 같이 회수 정책을 변경합니다.

```shell-session
$ oc patch pv <your-pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

선택한 영구 볼륨에 올바른 정책이 있는지 확인합니다.

```shell-session
$ oc get pv
```

```shell-session
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Retain          Bound     default/claim3    manual                     3s
```

이전 출력에서 `default/claim3` 클레임에 바인딩된 볼륨이 이제 `Retain` 회수 정책을 갖습니다. 사용자가 `default/claim3` 클레임을 삭제할 때 볼륨이 자동으로 삭제되지 않습니다.

### 3.3. PV(영구 볼륨)

각 PV에는 `사양` 및 `상태` 가 포함됩니다. 이는 볼륨의 사양과 상태이고 예는 다음과 같습니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  ...
status:
  ...
```

1. 영구 볼륨의 이름입니다.

2. 볼륨에서 사용할 수 있는 스토리지의 용량입니다.

3. 읽기-쓰기 및 마운트 권한을 정의하는 액세스 모드입니다.

4. 해제된 후 리소스를 처리하는 방법을 나타내는 회수 정책입니다.

다음 명령을 실행하여 PV에 바인딩된 PVC의 이름을 볼 수 있습니다.

```shell-session
$ oc get pv <pv_name> -o jsonpath='{.spec.claimRef.name}'
```

#### 3.3.1. PV 유형

OpenShift Container Platform은 다음 영구 볼륨 플러그인을 지원합니다.

AWS EBS(Elastic Block Store)는 기본적으로 설치됩니다.

AWS EBS(Elastic File Store)

Azure Disk

Azure File

Cinder

파이버 채널

GCP 영구 디스크

GCP 파일 저장소

IBM Power Virtual Server Block

IBM Cloud® VPC Block

HostPath

iSCSI

로컬 볼륨

LVM 스토리지

NFS

OpenStack Manila

Red Hat OpenShift Data Foundation

CIFS/SMB

VMware vSphere

#### 3.3.2. 용량

일반적으로 PV(영구 볼륨)에는 특정 스토리지 용량이 있습니다. 이는 PV의 `용량` 속성을 사용하여 설정됩니다.

현재는 스토리지 용량이 설정 또는 요청할 수 있는 유일한 리소스뿐입니다. 향후 속성에는 IOPS, 처리량 등이 포함될 수 있습니다.

#### 3.3.3. 액세스 모드

영구 볼륨은 리소스 공급자가 지원하는 방식으로 호스트에 볼륨을 마운트될 수 있습니다. 공급자에 따라 기능이 다르며 각 PV의 액세스 모드는 해당 볼륨에서 지원하는 특정 모드로 설정됩니다. 예를 들어, NFS에서는 여러 읽기-쓰기 클라이언트를 지원할 수 있지만 특정 NFS PV는 서버에서 읽기 전용으로 내보낼 수 있습니다. 각 PV는 특정 PV의 기능을 설명하는 자체 액세스 모드 세트를 가져옵니다.

클레임은 액세스 모드가 유사한 볼륨과 매칭됩니다. 유일하게 일치하는 두 가지 기준은 액세스 모드와 크기입니다. 클레임의 액세스 모드는 요청을 나타냅니다. 따라서 더 많이 부여될 수 있지만 절대로 부족하게는 부여되지 않습니다. 예를 들어, 클레임 요청이 RWO이지만 사용 가능한 유일한 볼륨이 NFS PV(RWO+ROX+RWX)인 경우, RWO를 지원하므로 클레임이 NFS와 일치하게 됩니다.

항상 직접 일치가 먼저 시도됩니다. 볼륨의 모드는 사용자의 요청과 일치하거나 더 많은 모드를 포함해야 합니다. 크기는 예상되는 크기보다 크거나 같아야 합니다. NFS 및 iSCSI와 같은 두 개의 볼륨 유형에 동일한 액세스 모드 세트가 있는 경우 둘 중 하나를 해당 모드와 클레임과 일치시킬 수 있습니다. 볼륨 유형과 특정 유형을 선택할 수 있는 순서는 없습니다.

모드가 동일한 모든 볼륨이 그룹화된 후 크기 오름차순으로 크기가 정렬됩니다. 바인더는 모드가 일치하는 그룹을 가져온 후 크기가 일치하는 그룹을 찾을 때까지 크기 순서대로 각 그룹에 대해 반복합니다.

중요

볼륨 액세스 모드는 볼륨 기능을 설명합니다. 제한 조건이 적용되지 않습니다. 리소스를 잘못된 사용으로 인한 런타임 오류는 스토리지 공급자가 처리합니다. 공급자에서의 오류는 런타임 시 마운트 오류로 표시됩니다.

예를 들어, NFS는 `ReadWriteOnce` 액세스 모드를 제공합니다. 볼륨의 ROX 기능을 사용하려면 클레임을 `ReadOnlyMany` 로 표시합니다.

iSCSI 및 파이버 채널 볼륨은 현재 펜싱 메커니즘을 지원하지 않습니다. 볼륨을 한 번에 하나씩만 사용하는지 확인해야 합니다. 노드 드레이닝과 같은 특정 상황에서는 두 개의 노드에서 볼륨을 동시에 사용할 수 있습니다. 노드를 드레이닝하기 전에 볼륨을 사용하는 Pod를 삭제합니다.

다음 표에는 액세스 모드가 나열되어 있습니다.

| 액세스 모드 | CLI 약어 | 설명 |
| --- | --- | --- |
| ReadWriteOnce | `RWO` | 볼륨은 단일 노드에서 읽기-쓰기로 마운트할 수 있습니다. |
| ReadWriteOncePod | `RWOP` | 볼륨은 단일 노드의 단일 Pod에서 읽기-쓰기로 마운트할 수 있습니다. |
| ReadOnlyMany | `ROX` | 볼륨은 여러 노드에서 읽기 전용으로 마운트할 수 있습니다. |
| ReadWriteMany | `RWX` | 볼륨은 여러 노드에서 읽기-쓰기로 마운트할 수 있습니다. |

| 볼륨 플러그인 | ReadWriteOnce [1] | ReadWriteOncePod | ReadOnlyMany | ReadWriteMany |
| --- | --- | --- | --- | --- |
| AWS EBS [2] | ✅ | ✅ |  |  |
| AWS EFS | ✅ | ✅ | ✅ | ✅ |
| Azure File | ✅ | ✅ | ✅ | ✅ |
| Azure Disk | ✅ | ✅ |  |  |
| CIFS/SMB | ✅ | ✅ | ✅ | ✅ |
| Cinder | ✅ | ✅ |  |  |
| 파이버 채널 | ✅ | ✅ | ✅ | ✅ [3] |
| GCP 영구 디스크 | ✅ [4] | ✅ | ✅ | ✅ [4] |
| GCP 파일 저장소 | ✅ | ✅ | ✅ | ✅ |
| HostPath | ✅ | ✅ |  |  |
| IBM Power Virtual Server 디스크 | ✅ | ✅ | ✅ | ✅ |
| IBM Cloud® VPC 디스크 | ✅ | ✅ |  |  |
| iSCSI | ✅ | ✅ | ✅ | ✅ [3] |
| 로컬 볼륨 | ✅ | ✅ |  |  |
| LVM 스토리지 | ✅ | ✅ |  |  |
| NFS | ✅ | ✅ | ✅ | ✅ |
| OpenStack Manila |  | ✅ |  | ✅ |
| Red Hat OpenShift Data Foundation | ✅ | ✅ |  | ✅ |
| VMware vSphere | ✅ | ✅ |  | ✅ [5] |

ReadWriteOnce(RWO) 볼륨은 여러 노드에 마운트할 수 없습니다. 시스템이 이미 실패한 노드에 할당되어 있기 때문에, 노드가 실패하면 시스템은 연결된 RWO 볼륨을 새 노드에 마운트하는 것을 허용하지 않습니다. 이로 인해 다중 연결 오류 메시지가 표시되면 동적 영구 볼륨이 연결된 경우와 같이 중요한 워크로드에서의 데이터가 손실되는 것을 방지하기 위해 종료되거나 충돌이 발생한 노드에서 Pod를 삭제해야 합니다.

AWS EBS 기반 Pod에 재생성 배포 전략을 사용합니다.

원시 블록 볼륨만 파이버 채널 및 iSCSI에 대한 RWX(`ReadWriteMany`) 액세스 모드를 지원합니다. 자세한 내용은 "볼륨 지원 차단"을 참조하십시오.

GCP hyperdisk-balanced 디스크의 경우:

지원되는 액세스 모드는 다음과 같습니다.

`ReadWriteOnce`

`ReadWriteMany`

`ReadWriteMany` 액세스 모드가 활성화된 디스크에 대해 복제 및 스냅샷이 비활성화됩니다.

`ReadWriteMany` 의 단일 hyperdisk-balanced 디스크 볼륨을 최대 8개의 인스턴스에 연결할 수 있습니다.

모든 인스턴스에서 디스크를 분리한 경우에만 `ReadWriteMany` 의 디스크 크기를 조정할 수 있습니다.

추가 제한 사항.

기본 vSphere 환경에서 vSAN 파일 서비스를 지원하는 경우 OpenShift Container Platform에서 설치한 vSphere CSI(Container Storage Interface) Driver Operator는 RWX(ReadWriteMany) 볼륨의 프로비저닝을 지원합니다. vSAN 파일 서비스가 구성되어 있지 않고 RWX를 요청하면 볼륨이 생성되지 않고 오류가 기록됩니다. 자세한 내용은 "컨테이너 스토리지 인터페이스 사용" → "VMware vSphere CSI Driver Operator"를 참조하십시오.

#### 3.3.4. 단계

볼륨은 다음 단계 중 하나에서 찾을 수 있습니다.

| 단계 | 설명 |
| --- | --- |
| Available | 아직 클레임에 바인딩되지 않은 여유 리소스입니다. |
| Bound | 볼륨이 클레임에 바인딩됩니다. |
| 해제됨 | 클레임이 삭제되었지만, 리소스가 아직 클러스터에 의해 회수되지 않았습니다. |
| 실패 | 볼륨에서 자동 회수가 실패했습니다. |

#### 3.3.4.1. 마지막 단계 전환 시간

`LastPhaseTransitionTime` 필드에는 PV(영구 볼륨)가 다른 단계(`pv.Status.Phase`)로 전환될 때마다 업데이트하는 타임스탬프가 있습니다. PV의 마지막 단계 전환 시간을 찾으려면 다음 명령을 실행합니다.

```shell-session
$ oc get pv <pv_name> -o json | jq '.status.lastPhaseTransitionTime'
```

1. 마지막 단계 전환을 확인할 PV의 이름을 지정합니다.

#### 3.3.4.2. 마운트 옵션

`mountOptions` 속성을 사용하여 PV를 마운트하는 동안 마운트 옵션을 지정할 수 있습니다.

예를 들면 다음과 같습니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  mountOptions:
    - nfsvers=4.1
  nfs:
    path: /tmp
    server: 172.17.0.2
  persistentVolumeReclaimPolicy: Retain
  claimRef:
    name: claim1
    namespace: default
```

1. 지정된 마운트 옵션이 PV를 디스크에 마운트하는 동안 사용됩니다.

다음 PV 유형에서는 마운트 옵션을 지원합니다.

AWS Elastic Block Store (EBS)

AWS EBS(Elastic File Storage)

Azure Disk

Azure File

Cinder

GCE 영구 디스크

iSCSI

로컬 볼륨

NFS

Red Hat OpenShift Data Foundation (Ceph RBD 전용)

CIFS/SMB

VMware vSphere

참고

파이버 채널 및 HostPath PV는 마운트 옵션을 지원하지 않습니다.

추가 리소스

ReadWriteMany vSphere 볼륨 지원

### 3.4. 영구 볼륨 클레임

각 `PersistentVolumeClaim` 오브젝트에는 `spec` 및 `status` 가 포함되며, 이는 PVC(영구 볼륨 클레임)의 사양과 상태이고, 예를 들면 다음과 같습니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: myclaim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 8Gi
  storageClassName: gold
status:
  ...
```

1. PVC의 이름입니다.

2. 읽기-쓰기 및 마운트 권한을 정의하는 액세스 모드입니다.

3. PVC에서 사용할 수 있는 스토리지 용량입니다.

4. 클레임에 필요한 `StorageClass` 의 이름입니다.

#### 3.4.1. 스토리지 클래스

선택 사항으로 클레임은 `storageClassName` 속성에 스토리지 클래스의 이름을 지정하여 특정 스토리지 클래스를 요청할 수 있습니다. PVC와 `storageClassName` 이 동일하고 요청된 클래스의 PV만 PVC에 바인딩할 수 있습니다. 클러스터 관리자는 동적 프로비저너를 구성하여 하나 이상의 스토리지 클래스에 서비스를 제공할 수 있습니다. 클러스터 관리자는 PVC의 사양과 일치하는 PV를 생성할 수 있습니다.

중요

클러스터 스토리지 작업자는 사용 중인 플랫폼에 따라 기본 스토리지 클래스를 설치할 수 있습니다. 이 스토리지 클래스는 Operator가 소유하고 제어합니다. 주석 및 레이블 정의 외에는 삭제하거나 변경할 수 없습니다. 다른 동작이 필요한 경우 사용자 정의 스토리지 클래스를 정의해야 합니다.

클러스터 관리자는 모든 PVC의 기본 스토리지 클래스도 설정할 수도 있습니다. 기본 스토리지 클래스가 구성된 경우 PVC는 `""` 로 설정된 `StorageClass` 또는 `storageClassName` 주석이 스토리지 클래스를 제외하고 PV에 바인딩되도록 명시적으로 요청해야 합니다.

참고

두 개 이상의 스토리지 클래스가 기본값으로 표시되면 `storageClassName` 이 명시적으로 지정된 경우에만 PVC를 생성할 수 있습니다. 따라서 1개의 스토리지 클래스만 기본값으로 설정해야 합니다.

#### 3.4.2. 액세스 모드

클레임은 특정 액세스 모드로 스토리지를 요청할 때 볼륨과 동일한 규칙을 사용합니다.

#### 3.4.3. 리소스

Pod와 같은 클레임은 특정 리소스 수량을 요청할 수 있습니다. 이 경우 요청은 스토리지에 대한 요청입니다. 동일한 리소스 모델이 볼륨 및 클레임에 적용됩니다.

#### 3.4.4. 클레임을 볼륨으로

클레임을 볼륨으로 사용하여 Pod 액세스 스토리지 클레임은 클레임을 사용하는 Pod와 동일한 네임스페이스에 있어야 합니다. 클러스터는 Pod의 네임스페이스에서 클레임을 검색하고 이를 사용하여 클레임을 지원하는 `PersistentVolume` 을 가져옵니다. 볼륨은 호스트에 마운트되며, 예를 들면 다음과 같습니다.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: mypod
spec:
  containers:
    - name: myfrontend
      image: dockerfile/nginx
      volumeMounts:
      - mountPath: "/var/www/html"
        name: mypd
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: myclaim
```

1. Pod 내부에 볼륨을 마운트하는 경로입니다.

2. 마운트할 볼륨의 이름입니다. 컨테이너 루트, `/` 또는 호스트와 컨테이너에서 동일한 경로에 마운트하지 마십시오. 컨테이너가 호스트 `/dev/pts` 파일과 같이 충분한 권한이 있는 경우 호스트 시스템이 손상될 수 있습니다. `/host` 를 사용하여 호스트를 마운트하는 것이 안전합니다.

3. 동일한 네임스페이스에 있는 사용할 PVC의 이름입니다.

#### 3.4.5. PVC 사용량 통계 보기

PVC(영구 볼륨 클레임)에 대한 사용량 통계를 볼 수 있습니다.

중요

PVC usage statistics 명령은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

#### 3.4.5.1. PVC 사용 통계를 보는 데 필요한 사용자 권한

PVC 사용량 통계를 보려면 필요한 권한이 있어야 합니다.

필요한 권한으로 로그인하려면 다음을 수행합니다.

관리자 권한이 있는 경우 관리자로 로그인합니다.

관리자 권한이 없는 경우:

다음 명령을 실행하여 클러스터 역할을 생성하고 사용자에게 추가합니다.

```shell-session
$ oc create clusterrole routes-view --verb=get,list --resource=routes
$ oc adm policy add-cluster-role-to-user routes-view <user-name>
$ oc adm policy add-cluster-role-to-user cluster-monitoring-view <user-name>
```

1. 2

사용자 이름입니다.

#### 3.4.5.2. PVC 사용량 통계 보기

클러스터의 통계를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc adm top pvc -A
```

```shell-session
NAMESPACE     NAME         USAGE(%)
namespace-1   data-etcd-1  3.82%
namespace-1   data-etcd-0  3.81%
namespace-1   data-etcd-2  3.81%
namespace-2   mypvc-fs-gp3 0.00%
default       mypvc-fs     98.36%
```

지정된 네임스페이스의 PVC 사용량 통계를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc adm top pvc -n <namespace-name>
```

1. 여기서 `<namespace-name` >은 지정된 네임스페이스의 이름입니다.

```shell-session
NAMESPACE     NAME        USAGE(%)
namespace-1   data-etcd-2 3.81%
namespace-1   data-etcd-0 3.81%
namespace-1   data-etcd-1 3.82%
```

1. 이 예에서 지정된 네임스페이스는 `namespace-1` 입니다.

지정된 PVC 및 지정된 네임스페이스의 사용량 통계를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc adm top pvc <pvc-name> -n <namespace-name>
```

1. 여기서 `<pvc-name` >은 지정된 PVC의 이름이며 < `namespace-name` >은 지정된 네임스페이스의 이름입니다.

```shell-session
NAMESPACE   NAME        USAGE(%)
namespace-1 data-etcd-0 3.81%
```

1. 이 예에서 지정된 네임스페이스는 `namespace-1` 이고 지정된 PVC는 `data-etcd-0` 입니다.

#### 3.4.6. 볼륨 속성 클래스

볼륨 속성 클래스는 관리자가 제공하는 스토리지의 "클래스"를 설명하는 방법을 제공합니다. 서로 다른 수준의 서비스 수준에 따라 클래스가 다를 수 있습니다.

중요

볼륨 속성 클래스는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

OpenShift Container Platform의 볼륨 속성 클래스는 AWS EBS(Elastic Block Storage) 및 GCP(Google Cloud Platform) PD(영구 디스크) CSI(Container Storage Interface)에서만 사용할 수 있습니다.

볼륨 속성 클래스를 PVC(영구 볼륨 클레임)에 적용할 수 있습니다. 클러스터에서 새 Volume Attributes 클래스를 사용할 수 있게 되면 사용자는 필요한 경우 새 Volume Attributes Class로 PVC를 업데이트할 수 있습니다.

볼륨 속성 클래스에는 해당 클래스에 속한 볼륨을 설명하는 매개 변수가 있습니다. 매개변수를 생략하면 볼륨 프로비저닝에 기본값이 사용됩니다. 생략된 매개변수가 있는 다른 Volume Attributes Class로 PVC를 적용하면 CSI 드라이버 구현에 따라 매개변수의 기본값을 사용할 수 있습니다. 자세한 내용은 관련 CSI 드라이버 설명서를 참조하십시오.

#### 3.4.6.1. 제한

볼륨 속성 클래스에는 다음과 같은 제한 사항이 있습니다.

GCP PD를 사용하면 볼륨 속성 클래스를 사용한 볼륨 수정이 hyperdisk-balanced 디스크 유형에서만 가능합니다.

`VolumeAttributesClass` 에 대해 512 매개변수를 정의할 수 없습니다.

키와 값을 포함한 매개변수 오브젝트의 총 길이는 256KiB를 초과할 수 없습니다.

볼륨 속성 클래스를 PVC에 적용하는 경우 해당 PVC에 대해 적용된 볼륨 속성 클래스를 변경할 수 있지만 PVC에서 삭제할 수는 없습니다. PVC에서 Volume Attributes 클래스를 삭제하려면 PVC를 삭제한 다음 PVC를 다시 생성해야 합니다.

볼륨 속성 클래스 매개변수는 편집할 수 없습니다. Volume Attributes Class 매개변수를 변경해야 하는 경우 원하는 매개변수를 사용하여 새 Volume Attributes Class를 생성한 다음 PVC에 적용합니다.

#### 3.4.6.2. 볼륨 속성 클래스 활성화

볼륨 속성 클래스는 기본적으로 활성화되어 있지 않습니다.

볼륨 속성 클래스를 활성화하려면 FeatureGates를 사용하여 OpenShift Container Platform 기능 활성화 섹션의 절차를 따르십시오.

#### 3.4.6.3. 볼륨 속성 클래스 정의

다음은 AWS EBS의 Volume Attributes Class YAML 파일의 예입니다.

```yaml
apiVersion: storage.k8s.io/v1beta1
kind: VolumeAttributesClass
metadata:
  name: silver
driverName: ebs.csi.aws.com
parameters:
  iops: "300"
  throughput: "125"
  type: io2
  ...
```

1. 오브젝트를 Volumes 속성 클래스로 정의합니다.

2. `VolumeAttributesClass` 의 이름입니다. 이 예제에서는 "silver"입니다.

3. PV(영구 볼륨) 프로비저닝에 사용되는 볼륨 플러그인을 결정하는 프로비저너입니다. 이 예에서는 AWS EBS의 경우 "ebs.csi.aws.com"입니다.

4. 디스크 유형.

다음은 GPC PD용 Volume Attributes Class YAML 파일의 예입니다.

```yaml
apiVersion: storage.k8s.io/v1beta1
kind: VolumeAttributesClass
metadata:
  name: silver
driverName: pd.csi.storage.gke.io
parameters:
  iops: "3000"
  throughput: "150Mi"
  ...
```

1. 오브젝트를 Volumes 속성 클래스로 정의합니다.

2. `VolumeAttributesClass` 의 이름입니다. 이 예제에서는 "silver"입니다.

3. PV(영구 볼륨) 프로비저닝에 사용되는 볼륨 플러그인을 결정하는 프로비저너입니다. 이 예에서 GPC PD의 경우 "pd.csi.storage.gke.io"입니다.

#### 3.4.6.4. PVC에 볼륨 속성 클래스 적용

새로 생성된 PVC 외에도 볼륨 속성 클래스를 사용하여 기존 바인딩된 PVC를 업데이트할 수도 있습니다.

PVC에 볼륨 속성 클래스를 적용하려면 다음을 수행합니다.

PVC의 `volumeAttributesClassName` 매개변수를 Volume Attributes Class의 이름으로 설정합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pv-claim
spec:
  …
  volumeAttributesClassName: silver
```

1. 이 PVC에 볼륨 속성 클래스 "silver"를 사용하여 지정합니다.

#### 3.4.6.5. 볼륨 속성 클래스 삭제

PVC에서 사용하는 볼륨 속성 클래스를 삭제할 수 없습니다.

PVC에서 여전히 사용 중인 Volume Attributes 클래스를 삭제하려고 하면 볼륨 속성 클래스를 사용하는 모든 리소스가 업데이트되지 않을 때까지 명령이 완료되지 않습니다.

볼륨 속성 클래스를 삭제하려면 다음을 수행합니다.

다음 명령을 실행하여 볼륨 속성 클래스를 사용하는 PVC를 검색합니다.

```shell-session
$ oc get pvc -A -o jsonpath='{range .items[?(@.spec.volumeAttributesClassName=="<vac-name>")]}{.metadata.name}{"\n"}{end}'
```

1. <VAC-name> = 볼륨 속성 클래스 이름

```shell-session
$ mypvc
```

다음 중 하나를 수행합니다.

PVC의 `volumeAttributesClassName` 매개변수에 다른 Volume Attributes Class 이름을 지정합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
name: mypvc
spec:
…
volumeAttributesClassName: silver
```

1. 다른 볼륨 속성 클래스를 지정합니다. 이 예제에서는 "silver"입니다.

또는

다음 명령을 실행하여 Volume Attributes Class를 지정하는 모든 PVC를 삭제합니다.

```shell-session
$ oc delete pvc <pvc-name>
```

1. 삭제할 PVC의 이름입니다.

이제 Volume Attributes 클래스가 PVC에서 더 이상 사용되지 않기 때문에 다음 명령을 실행하여 Volume Attributes 클래스를 삭제합니다.

```shell-session
$ oc delete vac <vac-name>
```

1. 삭제할 Volume Attributes 클래스의 이름입니다.

추가 리소스

FeatureGates를 사용하여 OpenShift Container Platform 기능 활성화

### 3.5. 블록 볼륨 지원

OpenShift Container Platform은 원시 블록 볼륨을 정적으로 프로비저닝할 수 있습니다. 이러한 볼륨에는 파일 시스템이 없으며 디스크에 직접 쓰거나 자체 스토리지 서비스를 구현하는 애플리케이션에 성능 이점을 제공할 수 있습니다.

원시 블록 볼륨은 PV 및 PVC 사양에 `volumeMode:Block` 을 지정하여 프로비저닝됩니다.

중요

권한이 부여된 컨테이너를 허용하려면 원시 블록 볼륨을 사용하는 Pod를 구성해야 합니다.

다음 표에는 블록 볼륨을 지원하는 볼륨 플러그인이 표시되어 있습니다.

| 볼륨 플러그인 | 수동 프로비저닝 | 동적 프로비저닝 | 모두 지원됨 |
| --- | --- | --- | --- |
| Amazon Elastic Block Store(Amazon EBS) | ✅ | ✅ | ✅ |
| Amazon Elastic File Storage(Amazon EFS) |  |  |  |
| Azure Disk | ✅ | ✅ | ✅ |
| Azure File |  |  |  |
| Cinder | ✅ | ✅ | ✅ |
| 파이버 채널 | ✅ |  | ✅ |
| GCP | ✅ | ✅ | ✅ |
| HostPath |  |  |  |
| IBM Cloud Block Storage 볼륨 | ✅ | ✅ | ✅ |
| iSCSI | ✅ |  | ✅ |
| 로컬 볼륨 | ✅ |  | ✅ |
| LVM 스토리지 | ✅ | ✅ | ✅ |
| NFS |  |  |  |
| Red Hat OpenShift Data Foundation | ✅ | ✅ | ✅ |
| CIFS/SMB | ✅ | ✅ | ✅ |
| VMware vSphere | ✅ | ✅ | ✅ |

중요

수동으로 프로비저닝할 수 있지만 완전히 지원되지 않는 블록 볼륨을 사용하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

#### 3.5.1. 블록 볼륨 예

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: block-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  volumeMode: Block
  persistentVolumeReclaimPolicy: Retain
  fc:
    targetWWNs: ["50060e801049cfd1"]
    lun: 0
    readOnly: false
```

1. 이 PV가 원시 블록 볼륨임을 나타내려면 `volumeMode` 를 `Block` 으로 설정해야 합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: block-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Block
  resources:
    requests:
      storage: 10Gi
```

1. 원시 블록 PVC가 요청되었음을 나타내려면 `volumeMode` 를 `Block` 으로 설정해야 합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-block-volume
spec:
  containers:
    - name: fc-container
      image: fedora:26
      command: ["/bin/sh", "-c"]
      args: [ "tail -f /dev/null" ]
      volumeDevices:
        - name: data
          devicePath: /dev/xvda
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: block-pvc
```

1. 블록 장치에서는 `volumeMounts` 대신 `volumeDevices` 가 사용됩니다. `PersistentVolumeClaim` 소스만 원시 블록 볼륨과 함께 사용할 수 있습니다.

2. `mountPath` 대신 `devicePath` 가 원시 블록이 시스템에 매핑되는 물리 장치의 경로를 나타냅니다.

3. 볼륨 소스는 `persistentVolumeClaim` 유형이어야 하며 예상되는 PVC의 이름과 일치해야 합니다.

| 값 | 기본 |
| --- | --- |
| 파일 시스템 | 예 |
| 블록 | 아니요 |

| PV `volumeMode` | PVC `volumeMode` | 바인딩 결과 |
| --- | --- | --- |
| 파일 시스템 | 파일 시스템 | 바인딩 |
| 지정되지 않음 | 지정되지 않음 | 바인딩 |
| 파일 시스템 | 지정되지 않음 | 바인딩 |
| 지정되지 않음 | 파일 시스템 | 바인딩 |
| 블록 | 블록 | 바인딩 |
| 지정되지 않음 | 블록 | 바인딩되지 않음 |
| 블록 | 지정되지 않음 | 바인딩되지 않음 |
| 파일 시스템 | 블록 | 바인딩되지 않음 |
| 블록 | 파일 시스템 | 바인딩되지 않음 |

중요

값을 지정하지 않으면 `Filesystem` 의 기본값이 사용됩니다.

### 3.6. fsGroup을 사용하여 Pod 시간 초과 감소

스토리지 볼륨에 많은 파일(예: 100만 개 이상)이 포함된 경우 Pod 시간 초과가 발생할 수 있습니다.

기본적으로 OpenShift Container Platform은 볼륨이 마운트될 때 Pod의 `securityContext` 에 지정된 `fsGroup` 과 일치하도록 각 볼륨의 콘텐츠에 대한 소유권 및 권한을 반복적으로 변경하기 때문에 발생할 수 있습니다. 많은 파일이 있는 볼륨의 경우 소유권 및 권한을 확인하고 변경하는 데 시간이 오래 걸릴 수 있으므로 Pod 시작 속도가 느려질 수 있습니다. `securityContext` 내에서 `fsGroupChangePolicy` 필드를 사용하여 OpenShift Container Platform에서 볼륨에 대한 소유권 및 권한을 확인하고 관리하는 방법을 제어할 수 있습니다.

`fsGroupChangePolicy` 는 Pod 내에서 노출되기 전에 볼륨의 소유권 및 권한을 변경하는 동작을 정의합니다. 이 필드는 `fsGroup` - 제어된 소유권 및 권한을 지원하는 볼륨 유형에만 적용됩니다. 이 필드에는 두 가지 가능한 값이 있습니다.

`OnRootMismatch`: root 디렉터리의 권한 및 소유권이 볼륨의 예상 권한과 일치하지 않는 경우에만 권한 및 소유권을 변경합니다. 이를 통해 Pod 시간 초과를 줄이기 위해 볼륨의 소유권 및 권한을 변경하는 데 걸리는 시간을 단축할 수 있습니다.

`Always`: (기본값) 볼륨이 마운트될 때 볼륨의 권한 및 소유권을 항상 변경합니다.

참고

`fsGroupChangePolicy` 필드는 secret, configMap, emptydir과 같은 임시 볼륨 유형에는 영향을 미치지 않습니다.

네임스페이스 또는 Pod 수준에서 `fsGroupChangePolicy` 를 설정할 수 있습니다.

#### 3.6.1. 네임스페이스 수준에서 fsGroup 변경

네임스페이스 수준에서 `fsGroupChangePolicy` 에 원하는 설정을 적용한 후 해당 네임스페이스에서 나중에 생성된 모든 Pod가 해당 설정을 상속합니다. 그러나 필요한 경우 개별 Pod에 대해 상속된 `fsGroupChangePolicy` 설정을 덮어쓸 수 있습니다. Pod 수준에서 `fsGroupChangePolicy` 를 설정하면 해당 Pod의 네임스페이스 수준 설정에서 상속이 재정의됩니다.

사전 요구 사항

관리자 권한으로 실행 중인 OpenShift Container Platform 클러스터에 로그인합니다.

OpenShift Container Platform 콘솔에 액세스합니다.

프로세스

네임스페이스당 `fsGroupChangePolicy` 를 설정하려면 다음을 수행합니다.

원하는 네임스페이스를 선택합니다.

Administration > Namespaces 를 클릭합니다.

네임스페이스 페이지에서 원하는 네임스페이스를 클릭합니다. 네임스페이스 세부 정보 페이지가 표시됩니다.

네임스페이스에 `fsGroupChangePolicy` 레이블을 추가합니다.

라벨

옆에 있는 네임스페이스 세부 정보 페이지에서 편집을 클릭합니다.

레이블 편집 대화 상자에서 `storage.openshift.io/fsgroup-change-policy` 레이블을 추가하고 다음과 같이 설정합니다.

`OnRootMismatch`: 루트 디렉터리의 권한 및 소유권이 볼륨의 예상 권한과 일치하지 않는 경우에만 권한 및 소유권을 변경하여 Pod 시간 초과 문제를 방지합니다.

`Always`: (기본값) 볼륨이 마운트될 때 볼륨의 권한 및 소유권을 항상 변경하는 것을 지정합니다.

저장 을 클릭합니다.

검증

이전에 편집한 네임스페이스에서 Pod를 시작하고 `spec.securityContext.fsGroupChangePolicy` 매개변수에 네임스페이스에 설정한 값이 포함되어 있는지 확인합니다.

```yaml
securityContext:
  seLinuxOptions:
    level: 's0:c27,c24'
  runAsNonRoot: true
  fsGroup: 1000750000
  fsGroupChangePolicy: OnRootMismatch
  ...
```

1. 이 값은 네임스페이스에서 상속됩니다.

#### 3.6.2. Pod 수준에서 fsGroup 변경

새 배포 또는 기존 배포에서 `fsGroupChangePolicy` 매개변수를 설정한 다음 관리하는 Pod에 이 매개변수 값이 있습니다. 상태 저장 세트에서도 이 작업을 수행할 수 있습니다. 기존 Pod를 편집하여 `fsGroupChangePolicy` 를 설정할 수 없습니다. 그러나 새 Pod를 생성할 때 이 매개변수를 설정할 수 있습니다.

다음 절차에서는 기존 배포에서 `fsGroupChangePolicy` 매개변수를 설정하는 방법을 설명합니다.

사전 요구 사항

OpenShift Container Platform 콘솔에 액세스합니다.

프로세스

기존 배포에서 `fsGroupChangePolicy` 매개변수를 설정하려면 다음을 수행합니다.

워크로드 > 배포를 클릭합니다.

배포 페이지에서 원하는 배포를 클릭합니다.

Deployment details 페이지에서 YAML 탭을 클릭합니다.

다음 예제 파일을 사용하여 `spec.template.spec.securityContext` 에서 배포의 YAML 파일을 편집합니다.

```yaml
...
spec:
replicas: 3
selector:
matchLabels:
app: my-app
template:
metadata:
creationTimestamp: null
labels:
app: my-app
spec:
containers:
- name: container
image: 'image-registry.openshift-image-registry.svc:5000/openshift/httpd:latest'
ports:
- containerPort: 8080
protocol: TCP
resources: {}
terminationMessagePath: /dev/termination-log
terminationMessagePolicy: File
imagePullPolicy: Always
restartPolicy: Always
terminationGracePeriodSeconds: 30
dnsPolicy: ClusterFirst
securityContext:
  fsGroupChangePolicy: OnRootMismatch
...
```

1. `OnRootMismatch` 는 재귀 권한 변경을 건너뛰어 Pod 시간 초과 문제를 방지합니다. 기본값은 `Always` 이며, 볼륨이 마운트될 때 볼륨의 권한 및 소유권을 항상 변경합니다.

저장 을 클릭합니다.

### 3.7. seLinuxChangePolicy를 사용하여 Pod 시간 초과 감소

SELinux(Security-Enhanced Linux)는 시스템의 모든 오브젝트(파일, 프로세스, 네트워크 포트 등)에 보안 레이블(컨텍스트)을 할당하는 보안 메커니즘입니다. 이러한 레이블은 프로세스가 액세스할 수 있는 항목을 결정합니다. OpenShift Container Platform에서 SELinux는 컨테이너가 호스트 시스템 또는 기타 컨테이너를 피하고 액세스하지 못하도록 합니다.

Pod가 시작되면 컨테이너 런타임은 Pod의 SELinux 컨텍스트와 일치하도록 볼륨의 모든 파일의 레이블을 재귀적으로 다시 지정합니다. 여러 파일이 있는 볼륨의 경우 Pod 시작 시간이 크게 증가할 수 있습니다.

Mount 옵션은 -o 컨텍스트 마운트 옵션을 사용하여 올바른 SELinux 레이블로 볼륨을 직접 마운트하여 모든 파일의 재귀 레이블을 다시 지정하므로 Pod 시간 초과 문제를 방지할 수 있습니다.

RWOP 및 SELinux 마운트 옵션

RWOP(ReadWriteOncePod) 영구 볼륨은 기본적으로 SELinux 마운트 기능을 사용합니다.

마운트 옵션 기능은 드라이버에 따라 다르며 AWS EBS, Azure Disk, GCP PD, IBM Cloud Block Storage 볼륨, Cinder, vSphere 및 Red Hat OpenShift Data Foundation에서 기본적으로 활성화됩니다. 타사 드라이버의 경우 스토리지 벤더에 문의하십시오.

RWO 및 RWX 및 SELinux 마운트 옵션

ReadWriteOnce(RWO) 및 ReadWriteMany(RWX) 볼륨은 기본적으로 재귀 재레이블을 사용합니다.

중요

향후 OpenShift Container Platform 버전에서 RWO 및 RWX 볼륨은 기본적으로 마운트 옵션을 사용합니다.

다음 마운트 옵션 이동을 지원하기 위해 OpenShift Container Platform 4.20은 Pod를 생성하고 실행 중인 Pod에서 SELinux 관련 충돌을 보고하여 잠재적인 충돌을 파악하고 문제를 해결하는 데 도움이 됩니다. 이 보고에 대한 자세한 내용은 Kowledge Base 문서를 참조하십시오.

SELinux 관련 충돌을 확인할 수 없는 경우 선택한 Pod 또는 네임스페이스에 대해 기본적으로 마운트 옵션으로 자동 마운트 해제를 수행할 수 있습니다. 옵트아웃하려면 SELinux 마운트 옵션 비활성화를 참조하십시오.

#### 3.7.1. RWO 및 RWX 및 SELinux 마운트 옵션 테스트

OpenShift Container Platform 4.20에서는 RWO 및 RWX 볼륨의 마운트 옵션 기능을 기술 프리뷰 기능으로 평가할 수 있습니다.

중요

RWO/RWX SELinux 마운트는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

마운트 옵션 기능을 평가하려면 다음을 수행합니다.

기능 게이트를 활성화합니다. 기능 게이트 활성화에 대한 자세한 내용은 기능 게이트를 사용하여 기능 활성화 섹션을 참조하십시오.

이제 RWO 및 RWX 볼륨에는 기본 동작으로 마운트 옵션이 있습니다.

애플리케이션을 신중하게 테스트하고 스토리지 사용 방법을 관찰합니다. 이 기술 자료 문서를 참조하고 문제가 발생하는 경우 마운트 옵션 사용을 거부하는 것이 좋습니다. SELinux 마운트 옵션 기본값 비활성화 섹션을 참조하십시오.

#### 3.7.2. SELinux 마운트 옵션 비활성화

향후 마운트 옵션을 기본값으로 전환하려면 개별 Pod 또는 네임스페이스 수준에서 `seLinuxChangePolicy` 매개변수를 `Recursive` 로 설정할 수 있습니다.

#### 3.7.2.1. 네임스페이스 수준에서 seLinuxChangePolicy 변경

`seLinuxChangePolicy` 에 대해 원하는 설정을 네임스페이스 수준에서 적용한 후 해당 네임스페이스에서 나중에 생성된 모든 Pod는 설정을 상속합니다. 그러나 필요한 경우 개별 Pod에 대해 상속된 `seLinuxChangePolicy` 설정을 덮어쓸 수 있습니다. Pod 수준에서 `seLinuxChangePolicy` 를 설정하면 해당 Pod의 네임스페이스 수준 설정에서 상속이 재정의됩니다.

사전 요구 사항

관리자 권한으로 실행 중인 OpenShift Container Platform 클러스터에 로그인합니다.

OpenShift Container Platform 콘솔에 액세스합니다.

프로세스

네임스페이스당 `SELinuxChangePolicy` 를 설정하려면 다음을 수행합니다.

원하는 네임스페이스를 선택합니다.

Administration > Namespaces 를 클릭합니다.

네임스페이스 페이지에서 원하는 네임스페이스를 클릭합니다. 네임스페이스 세부 정보 페이지가 표시됩니다.

네임스페이스에 `seLinuxChangePolicy` 레이블을 추가합니다.

라벨

옆에 있는 네임스페이스 세부 정보 페이지에서 편집을 클릭합니다.

레이블 편집 대화 상자에서 `storage.openshift.io/selinux-change-policy=Recursive` 레이블을 추가합니다.

이는 Pod 볼륨의 모든 파일의 레이블을 적절한 SELinux 컨텍스트로 재귀적으로 다시 지정합니다.

저장 을 클릭합니다.

검증

이전에 편집한 네임스페이스에서 Pod를 시작하고 `spec.securityContext.seLinuxChangePolicy` 가 `Recursive` 로 설정되어 있는지 확인합니다.

```yaml
securityContext:
    seLinuxOptions:
      level: 's0:c27,c19'
    runAsNonRoot: true
    fsGroup: 1000740000
    seccompProfile:
      type: RuntimeDefault
    seLinuxChangePolicy: Recursive
  ...
```

1. 이 값은 네임스페이스에서 상속됩니다.

#### 3.7.2.2. Pod 수준에서 seLinuxChangePolicy 변경

새 배포 또는 기존 배포에서 `seLinuxChangePolicy` 매개변수 세트를 설정한 다음 관리하는 Pod에 이 매개변수 값이 있습니다. StatefulSet에서도 마찬가지로 이 작업을 수행할 수 있습니다. 기존 Pod를 편집하여 `seLinuxChangePolicy` 를 설정할 수 없습니다. 그러나 새 Pod를 생성할 때 이 매개변수를 설정할 수 있습니다.

다음 절차에서는 기존 배포에서 `seLinuxChangePolicy` 매개변수를 설정하는 방법을 설명합니다.

사전 요구 사항

OpenShift Container Platform 콘솔에 액세스합니다.

프로세스

기존 배포에서 `seLinuxChangePolicy` 매개변수를 설정하려면 다음을 수행합니다.

워크로드 > 배포를 클릭합니다.

배포 페이지에서 원하는 배포를 클릭합니다.

Deployment details 페이지에서 YAML 탭을 클릭합니다.

다음 예제 파일에 따라 `spec.template.spec.securityContext` 에서 배포의 YAML 파일을 편집합니다.

```yaml
...
securityContext:
  seLinuxChangePolicy: Recursive
  ...
```

1. 모든 Pod 볼륨의 모든 파일의 레이블을 적절한 SELinux 컨텍스트로 재귀적으로 다시 지정합니다.

저장 을 클릭합니다.

### 4.1. AWS Elastic Block Store를 사용하는 영구저장장치

OpenShift Container Platform은 Amazon EBS(Elastic Block Store) 볼륨을 지원합니다. Amazon EC2 를 사용하여 영구 스토리지로 OpenShift Container Platform 클러스터를 프로비저닝할 수 있습니다.

Kubernetes 영구 볼륨 프레임워크를 사용하면 관리자는 영구 스토리지로 클러스터를 프로비저닝하고 사용자가 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다. Amazon EBS 볼륨을 동적으로 프로비저닝할 수 있습니다. 영구 볼륨은 단일 프로젝트 또는 네임스페이스에 바인딩되지 않으며, OpenShift Container Platform 클러스터에서 공유할 수 있습니다. 영구 볼륨 클레임은 프로젝트 또는 네임스페이스에 고유하며 사용자가 요청할 수 있습니다. AWS에서 컨테이너-영구 볼륨을 암호화하기 위해 KMS 키를 정의할 수 있습니다. 기본적으로 OpenShift Container Platform 버전 4.10을 사용하여 새로 생성된 클러스터에서는 gp3 스토리지 및 AWS EBS CSI 드라이버 를 사용합니다.

중요

인프라의 스토리지의 고가용성은 기본 스토리지 공급자가 담당합니다.

중요

OpenShift Container Platform 4.12 이상에서는 동등한 CSI 드라이버로 AWS Block in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 제공합니다.

CSI 자동 마이그레이션이 원활해야 합니다. 마이그레이션은 영구 볼륨, 영구 볼륨 클레임 및 스토리지 클래스와 같은 기존 API 오브젝트를 사용하는 방법을 변경하지 않습니다. 마이그레이션에 대한 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

#### 4.1.1. EBS 스토리지 클래스 생성

스토리지 클래스는 스토리지 수준 및 사용량을 구분하고 조정하는 데 사용됩니다. 스토리지 클래스를 정의하면 사용자는 동적으로 프로비저닝된 영구 볼륨을 얻을 수 있습니다.

#### 4.1.2. 영구 볼륨 클레임 생성

사전 요구 사항

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 스토리지 → 영구 볼륨 클레임을 클릭합니다.

영구 볼륨 클레임 생성 개요에서 영구 볼륨 클레임 생성 을 클릭합니다.

표시되는 페이지에 원하는 옵션을 정의합니다.

드롭다운 메뉴에서 이전에 생성한 스토리지 클래스를 선택합니다.

스토리지 클레임의 고유한 이름을 입력합니다.

액세스 모드를 선택합니다. 이 선택에 따라 스토리지 클레임에 대한 읽기 및 쓰기 액세스가 결정됩니다.

스토리지 클레임의 크기를 정의합니다.

만들기 를 클릭하여 영구 볼륨 클레임을 생성하고 영구 볼륨을 생성합니다.

#### 4.1.3. 볼륨 형식

OpenShift Container Platform이 볼륨을 마운트하고 컨테이너에 전달하기 전에 영구 볼륨 정의의 `fsType` arameter에 지정된 파일 시스템이 볼륨에 포함되어 있는지 확인합니다. 장치가 파일 시스템으로 포맷되지 않으면 장치의 모든 데이터가 삭제되고 장치는 지정된 파일 시스템에서 자동으로 포맷됩니다.

이 확인을 사용하면 OpenShift Container Platform이 처음 사용하기 전에 포맷되므로 형식화되지 않은 AWS 볼륨을 영구 볼륨으로 사용할 수 있습니다.

#### 4.1.4. 노드의 최대 EBS 볼륨 수

기본적으로 OpenShift Container Platform은 노드 1개에 연결된 최대 39개의 EBS 볼륨을 지원합니다. 이 제한은 AWS 볼륨 제한 과 일치합니다. 볼륨 제한은 인스턴스 유형에 따라 다릅니다.

중요

클러스터 관리자는 in-tree 또는 CSI(Container Storage Interface) 볼륨과 해당 스토리지 클래스를 사용할 수 있지만, 두 볼륨을 동시에 사용하지 않아야 합니다. 연결된 최대 EBS 볼륨 수는 in-tree 및 CSI 볼륨에 대해 별도로 계산되므로 각 유형의 최대 39개의 EBS 볼륨이 있을 수 있습니다.

in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 추가 스토리지 옵션에 액세스하는 방법에 대한 자세한 내용은 AWS Elastic Block Store CSI Driver Operator 를 참조하십시오.

#### 4.1.5. KMS 키를 사용하여 AWS에서 컨테이너 영구 볼륨 암호화

AWS에서 컨테이너-영구 볼륨을 암호화할 KMS 키를 정의하는 것은 AWS에 배포할 때 명시적인 규정 준수 및 보안 지침이 있는 경우 유용합니다.

사전 요구 사항

기본 인프라에는 스토리지가 포함되어야 합니다.

AWS에서 고객 KMS 키를 생성해야 합니다.

프로세스

스토리지 클래스를 생성합니다.

```yaml
$ cat << EOF | oc create -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <storage-class-name>
parameters:
  fsType: ext4
  encrypted: "true"
  kmsKeyId: keyvalue
provisioner: ebs.csi.aws.com
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
```

1. 스토리지 클래스의 이름을 지정합니다.

2. 프로비저닝된 볼륨에서 생성된 파일 시스템입니다.

3. container-persistent 볼륨을 암호화할 때 사용할 키의 전체 Amazon 리소스 이름(ARN)을 지정합니다. 키를 제공하지 않지만 `암호화된` 필드가 `true` 로 설정된 경우 기본 KMS 키가 사용됩니다. AWS 문서의 AWS 문서의 키 ID 및 키 ARN 찾기를 참조하십시오.

KMS 키를 지정하는 스토리지 클래스를 사용하여 PVC(영구 볼륨 클레임)를 생성합니다.

```yaml
$ cat << EOF | oc create -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mypvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  storageClassName: <storage-class-name>
  resources:
    requests:
      storage: 1Gi
EOF
```

PVC를 사용할 워크로드 컨테이너를 생성합니다.

```yaml
$ cat << EOF | oc create -f -
kind: Pod
metadata:
  name: mypod
spec:
  containers:
    - name: httpd
      image: quay.io/centos7/httpd-24-centos7
      ports:
        - containerPort: 80
      volumeMounts:
        - mountPath: /mnt/storage
          name: data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: mypvc
EOF
```

#### 4.1.6. 추가 리소스

in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 추가 스토리지 옵션에 액세스하는 방법에 대한 정보는 AWS Elastic Block Store CSI Driver Operator 를 참조하십시오.

### 4.2. Azure를 사용하는 영구 스토리지

OpenShift Container Platform은 Microsoft Azure Disk 볼륨을 지원합니다. Azure를 사용하여 영구 스토리지로 OpenShift Container Platform 클러스터를 프로비저닝할 수 있습니다. Kubernetes 및 Azure에 대해 어느 정도 익숙한 것으로 가정합니다. Kubernetes 영구 볼륨 프레임워크를 사용하면 관리자는 영구 스토리지로 클러스터를 프로비저닝하고 사용자가 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다. Azure 디스크 볼륨은 동적으로 프로비저닝할 수 있습니다. 영구 볼륨은 단일 프로젝트 또는 네임스페이스에 바인딩되지 않으며, OpenShift Container Platform 클러스터에서 공유할 수 있습니다. 영구 볼륨 클레임은 프로젝트 또는 네임스페이스에 고유하며 사용자가 요청할 수 있습니다.

중요

OpenShift Container Platform 4.11 이상에서는 동등한 CSI 드라이버로 Azure Disk in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 제공합니다.

CSI 자동 마이그레이션이 원활해야 합니다. 마이그레이션은 영구 볼륨, 영구 볼륨 클레임 및 스토리지 클래스와 같은 기존 API 오브젝트를 사용하는 방법을 변경하지 않습니다. 마이그레이션에 대한 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

중요

인프라의 스토리지의 고가용성은 기본 스토리지 공급자가 담당합니다.

추가 리소스

Microsoft Azure Disk

#### 4.2.1. Azure 스토리지 클래스 생성

스토리지 클래스는 스토리지 수준 및 사용량을 구분하고 조정하는 데 사용됩니다. 스토리지 클래스를 정의하면 사용자는 동적으로 프로비저닝된 영구 볼륨을 얻을 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 스토리지 → 스토리지 클래스

를 클릭합니다.

스토리지 클래스 개요에서 스토리지 클래스 만들기 를 클릭합니다.

표시되는 페이지에 원하는 옵션을 정의합니다.

스토리지 클래스를 참조할 이름을 입력합니다.

선택적 설명을 입력합니다.

회수 정책을 선택합니다.

드롭다운 목록에서 `kubernetes.io/azure-disk` 를 선택합니다.

스토리지 계정 유형을 입력합니다. 이는 Azure 스토리지 계정 SKU 계층에 해당합니다. 유효한 옵션은 `Premium_LRS`, `PremiumV2_LRS`, `Standard_LRS`, `StandardSSD_LRS` 및 `UltraSSD_LRS` 입니다.

중요

skuname `PremiumV2_LRS` 는 일부 지역에서 지원되지 않으며 일부 지원되는 리전에서는 일부 가용성 영역이 지원되지 않습니다. 자세한 내용은 Azure 문서 를 참조하십시오.

계정 종류를 입력합니다. 유효한 옵션은 `shared`, `dedicated` 및 `managed` 입니다.

중요

Red Hat은 스토리지 클래스에서 `kind: Managed` 의 사용만 지원합니다.

`Shared` 및 `Dedicated` 를 사용하여 Azure는 관리되지 않은 디스크를 생성합니다. 반면 OpenShift Container Platform은 머신 OS(root) 디스크의 관리 디스크를 생성합니다. Azure Disk는 노드에서 관리 및 관리되지 않은 디스크를 모두 사용하도록 허용하지 않으므로 `Shared` 또는 `Dedicated` 로 생성된 관리되지 않은 디스크를 OpenShift Container Platform 노드에 연결할 수 없습니다.

원하는 대로 스토리지 클래스에 대한 추가 매개변수를 입력합니다.

생성 을 클릭하여 스토리지 클래스를 생성합니다.

추가 리소스

Azure Disk 스토리지 클래스

#### 4.2.2. 영구 볼륨 클레임 생성

사전 요구 사항

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 스토리지 → 영구 볼륨 클레임을 클릭합니다.

영구 볼륨 클레임 생성 개요에서 영구 볼륨 클레임 생성 을 클릭합니다.

표시되는 페이지에 원하는 옵션을 정의합니다.

드롭다운 메뉴에서 이전에 생성한 스토리지 클래스를 선택합니다.

스토리지 클레임의 고유한 이름을 입력합니다.

액세스 모드를 선택합니다. 이 선택에 따라 스토리지 클레임에 대한 읽기 및 쓰기 액세스가 결정됩니다.

스토리지 클레임의 크기를 정의합니다.

만들기 를 클릭하여 영구 볼륨 클레임을 생성하고 영구 볼륨을 생성합니다.

#### 4.2.3. 볼륨 형식

OpenShift Container Platform이 볼륨을 마운트하고 컨테이너에 전달하기 전에 영구 볼륨 정의에 `fsType` 매개변수에 의해 지정된 파일 시스템이 포함되어 있는지 확인합니다. 장치가 파일 시스템으로 포맷되지 않으면 장치의 모든 데이터가 삭제되고 장치는 지정된 파일 시스템에서 자동으로 포맷됩니다.

이를 통해 OpenShift Container Platform이 처음 사용하기 전에 포맷되기 때문에 형식화되지 않은 Azure 볼륨을 영구 볼륨으로 사용할 수 있습니다.

#### 4.2.4. PVC를 사용하여 울트라 디스크가 있는 머신을 배포하는 머신 세트

Azure에서 실행되는 머신 세트를 생성하여 울트라 디스크가 있는 머신을 배포할 수 있습니다. Ultra 디스크는 가장 까다로운 데이터 워크로드에 사용하기 위한 고성능 스토리지입니다.

in-tree 플러그인과 CSI 드라이버는 모두 PVC를 사용하여 울트라 디스크를 활성화합니다. PVC를 생성하지 않고 울트라 디스크가 있는 머신을 데이터 디스크로 배포할 수도 있습니다.

추가 리소스

Microsoft Azure Ultra 디스크 문서

CSI PVC를 사용하여 울트라 디스크에 머신을 배포하는 머신 세트

울트라 디스크에 머신을 데이터 디스크로 배포하는 머신 세트

#### 4.2.4.1. 머신 세트를 사용하여 울트라 디스크가 있는 머신 생성

머신 세트 YAML 파일을 편집하여 Azure에 울트라 디스크가 있는 머신을 배포할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

기존 Azure `MachineSet` CR(사용자 정의 리소스)을 복사하고 다음 명령을 실행하여 편집합니다.

```shell-session
$ oc edit machineset <machine_set_name>
```

여기서 `<machine_set_name` >은 울트라 디스크가 있는 머신을 프로비저닝하려는 머신 세트입니다.

표시된 위치에 다음 행을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
spec:
  template:
    spec:
      metadata:
        labels:
          disk: ultrassd
      providerSpec:
        value:
          ultraSSDCapability: Enabled
```

1. 이 머신 세트에서 생성한 노드를 선택하는 데 사용할 라벨을 지정합니다. 이 절차에서는 이 값에 `disk.ultrassd` 를 사용합니다.

2. 이 라인은 울트라 디스크를 사용할 수 있습니다.

다음 명령을 실행하여 업데이트된 구성을 사용하여 머신 세트를 생성합니다.

```shell-session
$ oc create -f <machine_set_name>.yaml
```

다음 YAML 정의가 포함된 스토리지 클래스를 생성합니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ultra-disk-sc
parameters:
  cachingMode: None
  diskIopsReadWrite: "2000"
  diskMbpsReadWrite: "320"
  kind: managed
  skuname: UltraSSD_LRS
provisioner: disk.csi.azure.com
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

1. 스토리지 클래스의 이름을 지정합니다. 이 절차에서는 이 값에 `Ultra-disk-sc` 를 사용합니다.

2. 스토리지 클래스의 IOPS 수를 지정합니다.

3. 스토리지 클래스의 처리량(MBps)을 지정합니다.

4. AKS(Azure Kubernetes Service) 버전 1.21 이상의 경우 `disk.csi.azure.com` 을 사용합니다. 이전 버전의 AKS의 경우 `kubernetes.io/azure-disk` 를 사용합니다.

5. 선택 사항: 디스크를 사용할 Pod 생성을 기다리려면 이 매개변수를 지정합니다.

다음 YAML 정의가 포함된 `Ultra-disk-sc` 스토리지 클래스를 참조하는 PVC(영구 볼륨 클레임)를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ultra-disk
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: ultra-disk-sc
  resources:
    requests:
      storage: 4Gi
```

1. PVC 이름을 지정합니다. 이 절차에서는 이 값에 `Ultra-disk` 를 사용합니다.

2. 이 PVC는 `Ultra-disk-sc` 스토리지 클래스를 참조합니다.

3. 스토리지 클래스의 크기를 지정합니다. 최소 값은 `4Gi` 입니다.

다음 YAML 정의가 포함된 Pod를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-ultra
spec:
  nodeSelector:
    disk: ultrassd
  containers:
  - name: nginx-ultra
    image: alpine:latest
    command:
      - "sleep"
      - "infinity"
    volumeMounts:
    - mountPath: "/mnt/azure"
      name: volume
  volumes:
    - name: volume
      persistentVolumeClaim:
        claimName: ultra-disk
```

1. 울트라 디스크를 사용할 수 있는 머신 세트의 레이블을 지정합니다. 이 절차에서는 이 값에 `disk.ultrassd` 를 사용합니다.

2. 이 Pod는 `Ultra-disk` PVC를 참조합니다.

검증

다음 명령을 실행하여 머신이 생성되었는지 확인합니다.

```shell-session
$ oc get machines
```

시스템은 `Running` 상태여야 합니다.

실행 중이고 노드가 연결된 시스템의 경우 다음 명령을 실행하여 파티션을 검증합니다.

```shell-session
$ oc debug node/<node_name> -- chroot /host lsblk
```

이 명령에서 >은 노드 < `node_name` >에서 디버깅 쉘을 시작하고 `--` --로 명령을 전달합니다. 전달된 명령 는 기본 호스트 OS 바이너리에 대한 액세스를 제공하며 `lsblk` 에는 호스트 OS 시스템에 연결된 블록 장치가 표시됩니다.

```shell
oc debug node/<node_name
```

```shell
chroot /host
```

다음 단계

Pod 내에서 울트라 디스크를 사용하려면 마운트 지점을 사용하는 워크로드를 생성합니다. 다음 예와 유사한 YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssd-benchmark1
spec:
  containers:
  - name: ssd-benchmark1
    image: nginx
    ports:
      - containerPort: 80
        name: "http-server"
    volumeMounts:
    - name: lun0p1
      mountPath: "/tmp"
  volumes:
    - name: lun0p1
      hostPath:
        path: /var/lib/lun0p1
        type: DirectoryOrCreate
  nodeSelector:
    disktype: ultrassd
```

#### 4.2.4.2. 울트라 디스크를 활성화하는 머신 세트의 리소스 문제 해결

이 섹션의 정보를 사용하여 발생할 수 있는 문제를 이해하고 복구하십시오.

#### 4.2.4.2.1. 울트라 디스크가 지원하는 영구 볼륨 클레임을 마운트할 수 없음

울트라 디스크가 지원하는 영구 볼륨 클레임을 마운트하는 데 문제가 있으면 Pod가 `ContainerCreating` 상태로 중단되고 경고가 트리거됩니다.

예를 들어, pod를 호스팅하는 노드를 백업하는 시스템에 `additionalCapabilities.ultraSSDEnabled` 매개변수가 설정되지 않은 경우 다음 오류 메시지가 표시됩니다.

```shell-session
StorageAccountType UltraSSD_LRS can be used only when additionalCapabilities.ultraSSDEnabled is set.
```

이 문제를 해결하려면 다음 명령을 실행하여 Pod를 설명합니다.

```shell-session
$ oc -n <stuck_pod_namespace> describe pod <stuck_pod_name>
```

### 4.3. Azure File을 사용하는 영구 스토리지

OpenShift Container Platform은 Microsoft Azure File 볼륨을 지원합니다. Azure를 사용하여 영구 스토리지로 OpenShift Container Platform 클러스터를 프로비저닝할 수 있습니다. Kubernetes 및 Azure에 대해 어느 정도 익숙한 것으로 가정합니다.

Kubernetes 영구 볼륨 프레임워크를 사용하면 관리자는 영구 스토리지로 클러스터를 프로비저닝하고 사용자가 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다. Azure File 볼륨을 동적으로 프로비저닝할 수 있습니다.

영구 볼륨은 단일 프로젝트 또는 네임스페이스에 바인딩되지 않으며 OpenShift Container Platform 클러스터에서 공유할 수 있습니다. 영구 볼륨 클레임은 프로젝트 또는 네임스페이스에 고유하며 사용자가 애플리케이션에서 사용하도록 요청할 수 있습니다.

중요

인프라의 스토리지의 고가용성은 기본 스토리지 공급자가 담당합니다.

중요

Azure File 볼륨은 서버 메시지 블록을 사용합니다.

중요

OpenShift Container Platform 4.13 이상에서는 동등한 CSI 드라이버로 Azure File in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 제공합니다.

CSI 자동 마이그레이션이 원활해야 합니다. 마이그레이션은 영구 볼륨, 영구 볼륨 클레임 및 스토리지 클래스와 같은 기존 API 오브젝트를 사용하는 방법을 변경하지 않습니다. 마이그레이션에 대한 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

추가 리소스

Azure File

#### 4.3.1. Azure File 공유 영구 볼륨 클레임 생성

영구 볼륨 클레임을 생성하려면 먼저 Azure 계정 및 키가 포함된 `Secret` 오브젝트를 정의해야 합니다. 이 시크릿은 `PersistentVolume` 정의에 사용되며 애플리케이션에서 사용하기 위해 영구 볼륨 클레임에 의해 참조됩니다.

사전 요구 사항

Azure File 공유가 있습니다.

이 공유에 액세스할 수 있는 인증 정보(특히 스토리지 계정 및 키)를 사용할 수 있습니다.

절차

Azure File 인증 정보가 포함된 `Secret` 오브젝트를 생성합니다.

```shell-session
$ oc create secret generic <secret-name> --from-literal=azurestorageaccountname=<storage-account> \
  --from-literal=azurestorageaccountkey=<storage-account-key>
```

1. Azure File 스토리지 계정 이름입니다.

2. Azure File 스토리지 계정 키입니다.

생성한 `Secret` 오브젝트를 참조하는 `PersistentVolume` 오브젝트를 생성합니다.

```yaml
apiVersion: "v1"
kind: "PersistentVolume"
metadata:
  name: "pv0001"
spec:
  capacity:
    storage: "5Gi"
  accessModes:
    - "ReadWriteOnce"
  storageClassName: azure-file-sc
  azureFile:
    secretName: <secret-name>
    shareName: share-1
    readOnly: false
```

1. 영구 볼륨의 이름입니다.

2. 이 영구 볼륨의 크기입니다.

3. Azure File에서 인증 정보를 공유하는 시크릿의 이름입니다.

4. Azure File 공유의 이름입니다.

생성한 영구 볼륨에 매핑되는 `PersistentVolumeClaim` 오브젝트를 생성합니다.

```yaml
apiVersion: "v1"
kind: "PersistentVolumeClaim"
metadata:
  name: "claim1"
spec:
  accessModes:
    - "ReadWriteOnce"
  resources:
    requests:
      storage: "5Gi"
  storageClassName: azure-file-sc
  volumeName: "pv0001"
```

1. 영구 볼륨 클레임의 이름입니다.

2. 이 영구 볼륨 클레임의 크기입니다.

3. 영구 볼륨을 프로비저닝하는 데 사용되는 스토리지 클래스의 이름입니다. `PersistentVolume` 정의에 사용되는 스토리지 클래스를 지정합니다.

4. Azure File 공유를 참조하는 기존 `PersistentVolume` 오브젝트의 이름입니다.

#### 4.3.2. Pod에서 Azure 파일 공유 마운트

영구 볼륨 클레임을 생성한 후 애플리케이션에 의해 내부에서 사용될 수 있습니다. 다음 예시는 Pod 내부에서 이 공유를 마운트하는 방법을 보여줍니다.

사전 요구 사항

기본 Azure File 공유에 매핑된 영구 볼륨 클레임이 있습니다.

절차

기존 영구 볼륨 클레임을 마운트하는 Pod를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-name
spec:
  containers:
    ...
    volumeMounts:
    - mountPath: "/data"
      name: azure-file-share
  volumes:
    - name: azure-file-share
      persistentVolumeClaim:
        claimName: claim1
```

1. Pod의 이름입니다.

2. Pod 내부에서 Azure 파일 공유를 마운트하기 위한 경로입니다. 컨테이너 루트, `/` 또는 호스트와 컨테이너에서 동일한 경로에 마운트하지 마십시오. 컨테이너가 호스트 `/dev/pts` 파일과 같이 충분한 권한이 있는 경우 호스트 시스템이 손상될 수 있습니다. `/host` 를 사용하여 호스트를 마운트하는 것이 안전합니다.

3. 이전에 생성된 `PersistentVolumeClaim` 오브젝트의 이름입니다.

### 4.4. Cinder를 사용하는 영구 스토리지

OpenShift Container Platform은 OpenStack Cinder를 지원합니다. Kubernetes 및 OpenStack에 대해 어느 정도 익숙한 것으로 가정합니다.

Cinder 볼륨은 동적으로 프로비저닝할 수 있습니다. 영구 볼륨은 단일 프로젝트 또는 네임스페이스에 바인딩되지 않으며, OpenShift Container Platform 클러스터에서 공유할 수 있습니다. 영구 볼륨 클레임은 프로젝트 또는 네임스페이스에 고유하며 사용자가 요청할 수 있습니다.

중요

OpenShift Container Platform 4.11 이상에서는 Cinder in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 동등한 CSI 드라이버로 제공합니다.

CSI 자동 마이그레이션이 원활해야 합니다. 마이그레이션은 영구 볼륨, 영구 볼륨 클레임 및 스토리지 클래스와 같은 기존 API 오브젝트를 사용하는 방법을 변경하지 않습니다. 마이그레이션에 대한 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

추가 리소스

OpenStack Block Storage가 가상 하드 드라이브의 영구 블록 스토리지 관리를 제공하는 방법에 대한 자세한 내용은 OpenStack Cinder 를 참조하십시오.

#### 4.4.1. Cinder를 사용한 수동 프로비저닝

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다.

사전 요구 사항

RHOSP(Red Hat OpenStack Platform)용으로 구성된 OpenShift Container Platform

Cinder 볼륨 ID

#### 4.4.1.1. 영구 볼륨 생성

OpenShift Container Platform에서 생성하기 전에 오브젝트 정의에서 PV(영구 볼륨)를 정의해야 합니다.

절차

오브젝트 정의를 파일에 저장합니다.

```yaml
apiVersion: "v1"
kind: "PersistentVolume"
metadata:
  name: "pv0001"
spec:
  capacity:
    storage: "5Gi"
  accessModes:
    - "ReadWriteOnce"
  cinder:
    fsType: "ext3"
    volumeID: "f37a03aa-6212-4c62-a805-9ce139fab180"
```

1. 영구 볼륨 클레임 또는 Pod에서 사용되는 볼륨의 이름입니다.

2. 이 볼륨에 할당된 스토리지의 용량입니다.

3. RHOSP(Red Hat OpenStack Platform) Cinder 볼륨의 `cinder` 를 나타냅니다.

4. 볼륨이 처음 마운트될 때 생성되는 파일 시스템입니다.

5. 사용할 Cinder 볼륨입니다.

중요

볼륨이 포맷되어 프로비저닝된 후에는 `fstype` 매개변수 값을 변경하지 마십시오. 이 값을 변경하면 데이터가 손실되고 Pod 오류가 발생할 수 있습니다.

이전 단계에서 저장한 오브젝트 정의 파일을 생성합니다.

```shell-session
$ oc create -f cinder-persistentvolume.yaml
```

#### 4.4.1.2. 영구 볼륨 포맷

OpenShift Container Platform은 처음 사용하기 전에 형식화되기 때문에 형식화되지 않은 Cinder 볼륨을 PV로 사용할 수 있습니다.

OpenShift Container Platform이 볼륨을 마운트하고 컨테이너에 전달하기 전, 시스템은 PV 정의에 `fsType` 매개변수에 의해 지정된 파일 시스템이 포함되어 있는지 확인합니다. 장치가 파일 시스템으로 포맷되지 않으면 장치의 모든 데이터가 삭제되고 장치는 지정된 파일 시스템에서 자동으로 포맷됩니다.

#### 4.4.1.3. Cinder 볼륨 보안

애플리케이션에서 Cinder PV를 사용하는 경우 배포 구성에 대한 보안을 구성합니다.

사전 요구 사항

적절한 `fsGroup` 전략을 사용하는 SCC를 생성해야 합니다.

절차

서비스 계정을 생성하고 SCC에 추가합니다.

```shell-session
$ oc create serviceaccount <service_account>
```

```shell-session
$ oc adm policy add-scc-to-user <new_scc> -z <service_account> -n <project>
```

애플리케이션 배포 구성에서 서비스 계정 이름과 `securityContext` 를 입력합니다.

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: frontend-1
spec:
  replicas: 1
  selector:
    name: frontend
  template:
    metadata:
      labels:
        name: frontend
    spec:
      containers:
      - image: openshift/hello-openshift
        name: helloworld
        ports:
        - containerPort: 8080
          protocol: TCP
      restartPolicy: Always
      serviceAccountName: <service_account>
      securityContext:
        fsGroup: 7777
```

1. 실행할 Pod의 사본 수입니다.

2. 실행할 Pod의 레이블 선택기입니다.

3. 컨트롤러가 생성하는 Pod용 템플릿입니다.

4. Pod의 레이블입니다. 선택기 레이블에서 제공되는 레이블이 포함되어야 합니다.

5. 매개변수를 확장한 후 최대 이름 길이는 63자입니다.

6. 생성한 서비스 계정을 지정합니다.

7. Pod에 대한 `fsGroup` 을 지정합니다.

### 4.5. 파이버 채널을 사용하는 영구 스토리지

OpenShift Container Platform은 파이버 채널을 지원하므로 파이버 채널 볼륨을 사용하여 영구 스토리지로 OpenShift Container Platform 클러스터를 프로비저닝할 수 있습니다. Kubernetes 및 Fibre 채널에 대해 어느 정도 익숙한 것으로 가정합니다.

중요

파이버 채널을 사용하는 영구 스토리지는 ARM 아키텍처 기반 인프라에서 지원되지 않습니다.

Kubernetes 영구 볼륨 프레임워크를 사용하면 관리자는 영구 스토리지로 클러스터를 프로비저닝하고 사용자가 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다. 영구 볼륨은 단일 프로젝트 또는 네임스페이스에 바인딩되지 않으며, OpenShift Container Platform 클러스터에서 공유할 수 있습니다. 영구 볼륨 클레임은 프로젝트 또는 네임스페이스에 고유하며 사용자가 요청할 수 있습니다.

중요

인프라의 스토리지의 고가용성은 기본 스토리지 공급자가 담당합니다.

추가 리소스

파이버 채널 장치 사용

#### 4.5.1. 프로비저닝

`PersistentVolume` API를 사용하여 파이버 채널 볼륨을 프로비저닝하려면 다음을 사용할 수 있어야 합니다.

`targetWWN` (파이버 채널 대상의 World Wide Names에 대한 배열).

유효한 LUN 번호입니다.

파일 시스템 유형입니다.

영구 볼륨과 LUN은 일대일 매핑됩니다.

사전 요구 사항

파이버 채널 LUN은 기본 인프라에 있어야 합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  fc:
    wwids: [scsi-3600508b400105e210000900000490000]
    targetWWNs: ['500a0981891b8dc5', '500a0981991b8dc5']
    lun: 2
    fsType: ext4
```

1. WWID(Global wide Identifier)입니다. FC `wwids` 또는 FC `targetWWNs` 및 `lun` 의 조합을 설정해야 하지만 동시에 설정할 수는 없습니다. FC WWID 식별자는 WWNs 대상에서 권장되며 모든 스토리지 장치에 대해 고유하고 장치에 액세스하는 데 사용되는 경로와 무관하게 보장되기 때문입니다. WWID 식별자는 장치 식별-제품 데이터(`페이지 0x83 페이지) 또는 단위 일련 번호(페이지 0x 80`)를 검색하기 위해 SCSI I request를 발행하여 얻을 수 있습니다. FC WWID는 장치의 경로가 변경되고 다른 시스템에서 장치에 액세스하는 경우에도 디스크의 데이터를 참조하기 위해 `/dev/disk/by-id/` 로 식별됩니다.

2. 3

파이버 채널 WWN은 `/dev/disk/by-path/pci-<IDENTIFIER>-fc-0x<WWN>-lun-<LUN#>` 로 식별되지만, 앞에 `0x` 를 포함한 `WWN` 이 오고 이후에 `-` (하이픈)이 포함된 다른 경로가 있는 경로의 일부를 입력할 필요가 없습니다.

중요

볼륨이 포맷되고 프로비저닝된 후 `fstype` 매개변수 값을 변경하면 데이터가 손실되고 Pod 오류가 발생할 수 있습니다.

#### 4.5.1.1. 디스크 할당량 강제 적용

LUN 파티션을 사용하여 디스크 할당량 및 크기 제약 조건을 강제 적용합니다. 각 LUN은 단일 영구 볼륨에 매핑되며 고유한 이름을 영구 볼륨에 사용해야 합니다.

이렇게 하면 최종 사용자가 10Gi와 같은 특정 용량에 의해 영구 스토리지를 요청하고 해당 볼륨과 동등한 용량과 일치시킬 수 있습니다.

#### 4.5.1.2. 파이버 채널 볼륨 보안

사용자는 영구 볼륨 클레임을 사용하여 스토리지를 요청합니다. 이 클레임은 사용자의 네임스페이스에만 존재하며, 동일한 네임스페이스 내의 Pod에서만 참조할 수 있습니다. 네임스페이스에서 영구 볼륨에 대한 액세스를 시도하면 Pod가 실패하게 됩니다.

각 파이버 채널 LUN은 클러스터의 모든 노드에서 액세스할 수 있어야 합니다.

### 4.6. FlexVolume을 사용하는 영구 스토리지

중요

FlexVolume은 더 이상 사용되지 않는 기능입니다. 더 이상 사용되지 않는 기능은 여전히 OpenShift Container Platform에 포함되어 있으며 계속 지원됩니다. 그러나 이 기능은 향후 릴리스에서 제거될 예정이므로 새로운 배포에는 사용하지 않는 것이 좋습니다.

CSI(Out-of-tree Container Storage Interface) 드라이버는 OpenShift Container Platform에서 볼륨 드라이버를 작성하는 것이 좋습니다. FlexVolume 드라이버 관리자는 CSI 드라이버를 구현하고 FlexVolume 사용자를 CSI로 이동해야 합니다. FlexVolume 사용자는 워크로드를 CSI 드라이버로 이동해야 합니다.

OpenShift Container Platform에서 더 이상 사용되지 않거나 삭제된 주요 기능의 최신 목록은 OpenShift Container Platform 릴리스 노트에서 더 이상 사용되지 않고 삭제된 기능 섹션을 참조하십시오.

OpenShift Container Platform은 실행 가능한 모델을 드라이버와 인터페이스에 사용하는 out-of-tree 플러그인인 FlexVolume을 지원합니다.

기본 플러그인이 없는 백엔드의 스토리지를 사용하려면 FlexVolume 드라이버를 통해 OpenShift Container Platform을 확장하고 애플리케이션에 영구 스토리지를 제공할 수 있습니다.

Pod는 `flexvolume` in-tree 플러그인을 통해 FlexVolume 드라이버와 상호 작용합니다.

추가 리소스

영구 볼륨 확장

#### 4.6.1. FlexVolume 드라이버 정보

FlexVolume 드라이버는 클러스터의 모든 노드의 올바르게 정의된 디렉터리에 위치하는 실행 파일입니다. `flexVolume` 을 갖는 `PersistentVolume` 오브젝트가 소스로 표시되는 볼륨을 마운트하거나 마운트 해제해야 할 때마다 OpenShift Container Platform이 FlexVolume 드라이버를 호출합니다.

중요

FlexVolume용 OpenShift Container Platform에서는 연결 및 분리 작업이 지원되지 않습니다.

#### 4.6.2. FlexVolume 드라이버 예

FlexVolume 드라이버의 첫 번째 명령줄 인수는 항상 작업 이름입니다. 다른 매개 변수는 각 작업에 따라 다릅니다. 대부분의 작업에서는 JSON(JavaScript Object Notation) 문자열을 매개변수로 사용합니다. 이 매개변수는 전체 JSON 문자열이며 JSON 데이터가 있는 파일 이름은 아닙니다.

FlexVolume 드라이버에는 다음이 포함됩니다.

모든 `flexVolume.options`.

`fsType` 및 `readwrite` 와 같은 `kubernetes.io/` 접두사가 붙은 `flexVolume` 의 일부 옵션.

설정된 경우, `kubernetes.io/secret/` 이 접두사로 사용되는 참조된 시크릿의 콘텐츠

```plaintext
{
    "fooServer": "192.168.0.1:1234",
        "fooVolumeName": "bar",
    "kubernetes.io/fsType": "ext4",
    "kubernetes.io/readwrite": "ro",
    "kubernetes.io/secret/<key name>": "<key value>",
    "kubernetes.io/secret/<another key name>": "<another key value>",
}
```

1. `flexVolume.options` 의 모든 옵션.

2. `flexVolume.fsType` 의 값.

3. `flexVolume.readOnly` 에 따른 `Ro` / `rw`.

4. `flexVolume.secretRef` 에서 참조하는 시크릿의 모든 키 및 해당 값.

OpenShift Container Platform은 드라이버의 표준 출력에서 JSON 데이터를 예상합니다. 지정하지 않으면, 출력이 작업 결과를 설명합니다.

```plaintext
{
    "status": "<Success/Failure/Not supported>",
    "message": "<Reason for success/failure>"
}
```

드라이버의 종료 코드는 성공의 경우 `0` 이고 오류의 경우 `1` 이어야 합니다.

작업은 idempotent여야 합니다. 즉, 이미 마운트된 볼륨의 마운트의 경우 작업이 성공적으로 수행되어야 합니다.

#### 4.6.3. FlexVolume 드라이버 설치

OpenShift Container Platform 확장에 사용되는 FlexVolume 드라이버는 노드에서만 실행됩니다. FlexVolumes를 구현하려면 호출할 작업 목록 및 설치 경로만 있으면 됩니다.

사전 요구 사항

FlexVolume 드라이버는 다음 작업을 구현해야 합니다.

`init`

드라이버를 초기화합니다. 이는 모든 노드를 초기화하는 동안 호출됩니다.

인수: 없음

실행 위치: 노드

예상 출력: 기본 JSON

`Mount`

디렉터리에 볼륨을 마운트합니다. 여기에는 장치를 검색한 다음 장치를 마운트하는 등 볼륨을 마운트하는 데 필요한 모든 항목이 포함됩니다.

인수: `<mount-dir>`

`<json>`

실행 위치: 노드

예상 출력: 기본 JSON

`unmount`

디렉터리에서 볼륨의 마운트를 해제합니다. 여기에는 마운트 해제 후 볼륨을 정리하는 데 필요한 모든 항목이 포함됩니다.

인수: `<mount-dir>`

실행 위치: 노드

예상 출력: 기본 JSON

`mountdevice`

개별 Pod가 마운트를 바인딩할 수 있는 디렉터리에 볼륨의 장치를 마운트합니다.

이 호출은 FlexVolume 사양에 지정된 "시크릿"을 전달하지 않습니다. 드라이버에 시크릿이 필요한 경우 이 호출을 구현하지 마십시오.

인수: `<mount-dir>`

`<json>`

실행 위치: 노드

예상 출력: 기본 JSON

`unmountdevice`

디렉터리에서 볼륨의 장치를 마운트 해제합니다.

인수: `<mount-dir>`

실행 위치: 노드

예상 출력: 기본 JSON

다른 모든 작업은 `{"status": "Not supported"}` 및 `1` 의 종료 코드와 함께 JSON을 반환해야 합니다.

절차

FlexVolume 드라이버를 설치하려면 다음을 수행합니다.

실행 가능한 파일이 클러스터의 모든 노드에 있는지 확인합니다.

볼륨 플러그인 경로에 실행 가능 파일을 `/etc/kubernetes/kubelet-plugins/volume/exec/<vendor>~<driver>/<driver` >.

예를 들어, `foo` 스토리지용 FlexVolume 드라이버를 설치하려면 실행 파일을 `/etc/kubernetes/kubelet-plugins/volume/exec/openshift.com~foo/foo` 에 배치합니다.

#### 4.6.4. FlexVolume 드라이버를 사용한 스토리지 사용

OpenShift Container Platform의 각 `PersistentVolume` 오브젝트는 볼륨과 같이 스토리지 백엔드에서 1개의 스토리지 자산을 나타냅니다.

절차

`PersistentVolume` 오브젝트를 사용하여 설치된 스토리지를 참조합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  flexVolume:
    driver: openshift.com/foo
    fsType: "ext4"
    secretRef: foo-secret
    readOnly: true
    options:
      fooServer: 192.168.0.1:1234
      fooVolumeName: bar
```

1. 볼륨의 이름입니다. 영구 볼륨 클레임을 통해 또는 Pod에서 식별되는 방법입니다. 이 이름은 백엔드 스토리지의 볼륨 이름과 다를 수 있습니다.

2. 이 볼륨에 할당된 스토리지의 용량입니다.

3. 드라이버의 이름입니다. 이 필드는 필수입니다.

4. 볼륨에 존재하는 파일 시스템입니다. 이 필드는 선택 사항입니다.

5. 시크릿에 대한 참조입니다. 이 시크릿의 키와 값은 호출 시 FlexVolume 드라이버에 제공됩니다. 이 필드는 선택 사항입니다.

6. 읽기 전용 플래그입니다. 이 필드는 선택 사항입니다.

7. FlexVolume 드라이버에 대한 추가 옵션입니다. `options` 필드에 있는 사용자가 지정한 플래그 외에도 다음 플래그도 실행 파일에 전달됩니다.

```plaintext
"fsType":"<FS type>",
"readwrite":"<rw>",
"secret/key1":"<secret1>"
...
"secret/keyN":"<secretN>"
```

참고

시크릿은 호출을 마운트하거나 마운트 해제하기 위해서만 전달됩니다.

### 4.7. GCE 영구 디스크를 사용하는 스토리지

OpenShift Container Platform은 gcePD(GCE 영구 디스크 볼륨)를 지원합니다. GCE를 사용하여 영구 스토리지로 OpenShift Container Platform 클러스터를 프로비저닝할 수 있습니다. Kubernetes 및 GCE에 대해 어느 정도 익숙한 것으로 가정합니다.

Kubernetes 영구 볼륨 프레임워크를 사용하면 관리자는 영구 스토리지로 클러스터를 프로비저닝하고 사용자가 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다.

GCE 영구 디스크 볼륨은 동적으로 프로비저닝할 수 있습니다.

영구 볼륨은 단일 프로젝트 또는 네임스페이스에 바인딩되지 않으며, OpenShift Container Platform 클러스터에서 공유할 수 있습니다. 영구 볼륨 클레임은 프로젝트 또는 네임스페이스에 고유하며 사용자가 요청할 수 있습니다.

중요

OpenShift Container Platform 4.12 이상에서는 동등한 CSI 드라이버로 GCE Persist Disk in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 제공합니다.

CSI 자동 마이그레이션이 원활해야 합니다. 마이그레이션은 영구 볼륨, 영구 볼륨 클레임 및 스토리지 클래스와 같은 기존 API 오브젝트를 사용하는 방법을 변경하지 않습니다.

마이그레이션에 대한 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

중요

인프라의 스토리지의 고가용성은 기본 스토리지 공급자가 담당합니다.

추가 리소스

GCE 영구 디스크

#### 4.7.1. GCE 스토리지 클래스 생성

스토리지 클래스는 스토리지 수준 및 사용량을 구분하고 조정하는 데 사용됩니다. 스토리지 클래스를 정의하면 사용자는 동적으로 프로비저닝된 영구 볼륨을 얻을 수 있습니다.

#### 4.7.2. 영구 볼륨 클레임 생성

사전 요구 사항

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔에서 스토리지 → 영구 볼륨 클레임을 클릭합니다.

영구 볼륨 클레임 생성 개요에서 영구 볼륨 클레임 생성 을 클릭합니다.

표시되는 페이지에 원하는 옵션을 정의합니다.

드롭다운 메뉴에서 이전에 생성한 스토리지 클래스를 선택합니다.

스토리지 클레임의 고유한 이름을 입력합니다.

액세스 모드를 선택합니다. 이 선택에 따라 스토리지 클레임에 대한 읽기 및 쓰기 액세스가 결정됩니다.

스토리지 클레임의 크기를 정의합니다.

만들기 를 클릭하여 영구 볼륨 클레임을 생성하고 영구 볼륨을 생성합니다.

#### 4.7.3. 볼륨 형식

OpenShift Container Platform이 볼륨을 마운트하고 컨테이너에 전달하기 전에 영구 볼륨 정의의 `fsType` arameter에 지정된 파일 시스템이 볼륨에 포함되어 있는지 확인합니다. 장치가 파일 시스템으로 포맷되지 않으면 장치의 모든 데이터가 삭제되고 장치는 지정된 파일 시스템에서 자동으로 포맷됩니다.

이 확인을 사용하면 OpenShift Container Platform이 처음 사용하기 전에 포맷되므로 포맷되지 않은 GCE 볼륨을 영구 볼륨으로 사용할 수 있습니다.

### 4.8. iSCSI를 사용하는 영구 스토리지

iSCSI 를 사용하여 영구 스토리지로 OpenShift Container Platform 클러스터를 프로비저닝할 수 있습니다. Kubernetes 및 iSCSI에 대해 어느 정도 익숙한 것으로 가정합니다.

Kubernetes 영구 볼륨 프레임워크를 사용하면 관리자는 영구 스토리지로 클러스터를 프로비저닝하고 사용자가 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다.

중요

인프라의 스토리지의 고가용성은 기본 스토리지 공급자가 담당합니다.

중요

Amazon Web Services에서 iSCSI를 사용하는 경우 iSCSI 포트의 노드 간 TCP 트래픽을 포함하도록 기본 보안 정책을 업데이트해야 합니다. 기본적으로 해당 포트는 `860` 및 `3260` 입니다.

중요

사용자는 `iscsi-initiator-utils` 패키지를 설치하고 `/etc/iscsi/initiatorname.iscsi` 에 이니시에이터 이름을 구성하여 iSCSI 이니시에이터가 모든 OpenShift Container Platform 노드에 이미 구성되어 있는지 확인해야 합니다. `iscsi-initiator-utils` 패키지는 RHCOS(Red Hat Enterprise Linux CoreOS)를 사용하는 배포에 이미 설치되어 있습니다.

자세한 내용은 스토리지 장치 관리를 참조하십시오.

#### 4.8.1. 프로비저닝

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있는지 확인할 수 있습니다. iSCSI에는 iSCSI 대상 포털, 유효한 IQN(iSCSI Qualified Name), 유효한 LUN 번호, 파일 시스템 유형 및 `PersistentVolume` API만 있으면 됩니다.

프로세스

다음. `PersistentVolume` 오브젝트 정의를 생성하여 OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있는지 확인합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: iscsi-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  iscsi:
     targetPortal: 10.16.154.81:3260
     iqn: iqn.2014-12.example.server:storage.target00
     lun: 0
     fsType: 'ext4'
```

#### 4.8.2. 디스크 할당량 적용

LUN 파티션을 사용하여 디스크 할당량 및 크기 제약 조건을 강제 적용합니다. 각 LUN은 1개의 영구 볼륨입니다. Kubernetes는 영구 볼륨에 고유 이름을 강제 적용합니다.

이렇게 하면 사용자가 특정 용량(예: `10Gi`)에 의해 영구 스토리지를 요청하고 해당 볼륨과 동등한 용량과 일치시킬 수 있습니다.

#### 4.8.3. iSCSI 볼륨 보안

사용자는 `PersistentVolumeClaim` 오브젝트를 사용하여 스토리지를 요청합니다. 이 클레임은 사용자의 네임스페이스에만 존재하며, 동일한 네임스페이스 내의 Pod에서만 참조할 수 있습니다. 네임스페이스에서 영구 볼륨 클레임에 대한 액세스를 시도하면 Pod가 실패하게 됩니다.

각 iSCSI LUN은 클러스터의 모든 노드에서 액세스할 수 있어야 합니다.

#### 4.8.3.1. CHAP(Challenge Handshake Authentication Protocol) 구성

선택적으로 OpenShift Container Platform은 CHAP을 사용하여 iSCSI 대상에 자신을 인증할 수 있습니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: iscsi-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  iscsi:
    targetPortal: 10.0.0.1:3260
    iqn: iqn.2016-04.test.com:storage.target00
    lun: 0
    fsType: ext4
    chapAuthDiscovery: true
    chapAuthSession: true
    secretRef:
      name: chap-secret
```

1. iSCSI 검색의 CHAP 인증을 활성화합니다.

2. iSCSI 세션의 CHAP 인증을 활성화합니다.

3. 사용자 이름 + 암호로 시크릿 오브젝트의 이름을 지정합니다. 이 `Secret` 오브젝트는 참조된 볼륨을 사용할 수 있는 모든 네임스페이스에서 사용할 수 있어야 합니다.

#### 4.8.4. iSCSI 다중 경로

iSCSI 기반 스토리지의 경우 두 개 이상의 대상 포털 IP 주소에 동일한 IQN을 사용하여 여러 경로를 구성할 수 있습니다. 경로의 구성 요소 중 하나 이상에 실패하면 다중 경로를 통해 영구 볼륨에 액세스할 수 있습니다.

절차

Pod 사양에 다중 경로를 지정하려면 `PersistentVolume` 정의 오브젝트의 `portals` 필드에 값을 지정합니다.

portals 필드에 지정된 값이 있는 PersistentVolume 오브젝트의 예.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: iscsi-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  iscsi:
    targetPortal: 10.0.0.1:3260
    portals: ['10.0.2.16:3260', '10.0.2.17:3260', '10.0.2.18:3260']
    iqn: iqn.2016-04.test.com:storage.target00
    lun: 0
    fsType: ext4
    readOnly: false
```

1. `portals` 필드를 사용하여 추가 대상 포털을 추가합니다.

#### 4.8.5. iSCSI 사용자 정의 이니시에이터 IQN

iSCSI 대상이 특정 IQN으로 제한되는 경우 사용자 정의 이니시에이터 IQN(iSCSI Qualified Name)을 구성하지만 iSCSI PV가 연결된 노드는 이러한 IQN을 갖는 것이 보장되지 않습니다.

절차

사용자 정의 이니시에이터 IQN을 지정하려면 `PersistentVolume` 정의 오브젝트에서 `initiatorName` 필드를 업데이트합니다.

initiatorName 필드에 지정된 값이 있는 PersistentVolume 오브젝트의 예.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: iscsi-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  iscsi:
    targetPortal: 10.0.0.1:3260
    portals: ['10.0.2.16:3260', '10.0.2.17:3260', '10.0.2.18:3260']
    iqn: iqn.2016-04.test.com:storage.target00
    lun: 0
    initiatorName: iqn.2016-04.test.com:custom.iqn
    fsType: ext4
    readOnly: false
```

1. 이니시에이터의 이름을 지정합니다.

### 4.9. NFS를 사용하는 영구저장장치

OpenShift Container Platform 클러스터는 NFS를 사용하는 영구 스토리지와 함께 프로비저닝될 수 있습니다. PV(영구 볼륨) 및 PVC(영구 볼륨 클레임)는 프로젝트 전체에서 볼륨을 공유하는 편리한 방법을 제공합니다. PV 정의에 포함된 NFS 관련 정보는 `Pod` 정의에서 직접 정의될 수 있지만, 이렇게 하면 볼륨이 별도의 클러스터 리소스로 생성되지 않아 볼륨에서 충돌이 발생할 수 있습니다.

추가 리소스

NFS 공유 마운트

#### 4.9.1. 프로비저닝

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다. NFS 볼륨을 프로비저닝하려면, NFS 서버 목록 및 내보내기 경로만 있으면 됩니다.

절차

PV에 대한 오브젝트 정의를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  nfs:
    path: /tmp
    server: 172.17.0.2
  persistentVolumeReclaimPolicy: Retain
```

1. 볼륨의 이름입니다. 이는 다양한 다음 명령에서 PV ID입니다.

```shell
oc <command> pod
```

2. 이 볼륨에 할당된 스토리지의 용량입니다.

3. 볼륨에 대한 액세스를 제어하는 것으로 표시되지만 실제로 레이블에 사용되며 PVC를 PV에 연결하는 데 사용됩니다. 현재는 `accessModes` 를 기반으로 하는 액세스 규칙이 적용되지 않습니다.

4. 사용 중인 볼륨 유형입니다(이 경우 `nfs` 플러그인).

5. NFS 서버에서 내보낸 경로입니다.

6. NFS 서버의 호스트 이름 또는 IP 주소입니다.

7. PV의 회수 정책입니다. 이는 릴리스될 때 볼륨에 발생하는 작업을 정의합니다.

참고

각 NFS 볼륨은 클러스터의 모든 스케줄링 가능한 노드에서 마운트할 수 있어야 합니다.

PV가 생성되었는지 확인합니다.

```shell-session
$ oc get pv
```

```shell-session
NAME     LABELS    CAPACITY     ACCESSMODES   STATUS      CLAIM  REASON    AGE
pv0001   <none>    5Gi          RWO           Available                    31s
```

새 PV에 바인딩하는 영구 볼륨 클레임을 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-claim1
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  volumeName: pv0001
  storageClassName: ""
```

1. 액세스 모드는 보안을 적용하지 않고 PV를 PVC에 일치시키기 위한 레이블 역할을 합니다.

2. 이 클레임에서는 5Gi 이상의 용량을 제공하는 PV를 찾습니다.

영구 볼륨 클레임이 생성되었는지 확인합니다.

```shell-session
$ oc get pvc
```

```shell-session
NAME         STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
nfs-claim1   Bound    pv0001   5Gi        RWO                           2m
```

#### 4.9.2. 디스크 할당량 적용

디스크 파티션을 사용하여 디스크 할당량 및 크기 제약 조건을 적용할 수 있습니다. 각 파티션은 자체 내보내기일 수 있습니다. 각 내보내기는 1개의 PV입니다. OpenShift Container Platform은 PV에 고유한 이름을 적용하지만 NFS 볼륨 서버와 경로의 고유성은 관리자에 따라 다릅니다.

이렇게 하면 개발자가 10Gi와 같은 특정 용량에 의해 영구 스토리지를 요청하고 해당 볼륨과 동등한 용량과 일치시킬 수 있습니다.

#### 4.9.3. NFS 볼륨 보안

이 섹션에서는 일치하는 권한 및 SELinux 고려 사항을 포함하여 NFS 볼륨 보안에 대해 설명합니다. 사용자는 POSIX 권한, 프로세스 UID, 추가 그룹 및 SELinux의 기본 사항을 이해하고 있어야 합니다.

개발자는 `Pod` 정의의 `volumes` 섹션에서 직접 PVC 또는 NFS 볼륨 플러그인을 참조하여 NFS 스토리지를 요청합니다.

NFS 서버의 `/etc/exports` 파일에 액세스할 수 있는 NFS 디렉터리가 있습니다. 대상 NFS 디렉터리에는 POSIX 소유자 및 그룹 ID가 있습니다. OpenShift Container Platform NFS 플러그인은 내보낸 NFS 디렉터리에 있는 것과 동일한 POSIX 소유권 및 권한으로 컨테이너의 NFS 디렉터리를 마운트합니다. 그러나 컨테이너는 원하는 동작인 NFS 마운트의 소유자와 동일한 유효 UID로 실행되지 않습니다.

```shell-session
$ ls -lZ /opt/nfs -d
```

```shell-session
drwxrws---. nfsnobody 5555 unconfined_u:object_r:usr_t:s0   /opt/nfs
```

```shell-session
$ id nfsnobody
```

```shell-session
uid=65534(nfsnobody) gid=65534(nfsnobody) groups=65534(nfsnobody)
```

그러면 컨테이너가 SELinux 레이블과 일치하고 `65534`, `nfsnobody` 소유자 또는 디렉터리에 액세스하려면 추가 그룹의 `5555` 와 함께 실행해야 합니다.

참고

`65534` 의 소유자 ID는 예시와 같이 사용됩니다. NFS의 `root_squash` 는 UID가 `0` 인 `루트` 를 UID가 `65534` 인 `nfsnobody` 로 매핑하지만, NFS 내보내기에는 임의의 소유자 ID가 있을 수 있습니다. NFS를 내보내려면 소유자 `65534` 가 필요하지 않습니다.

#### 4.9.3.1. 그룹 ID

NFS 내보내기 권한 변경 옵션이 아닐 경우 NFS 액세스를 처리하는 권장 방법은 추가 그룹을 사용하는 것입니다. OpenShift Container Platform의 추가 그룹은 공유 스토리지에 사용되며 NFS가 그 예입니다. 반면 iSCSI와 같은 블록 스토리지는 Pod의 `securityContext` 에 있는 `fsGroup` SCC 전략과 `fsGroup` 값을 사용합니다.

참고

영구 스토리지에 액세스하려면, 일반적으로 추가 그룹 ID vs 사용자 ID를 사용하는 것이 좋습니다.

예제 대상 NFS 디렉터리의 그룹 ID는 `5555` 이므로 Pod의 `securityContext` 정의에서 `supplementalGroups` 를 사용하여 해당 그룹 ID를 정의할 수 있습니다. 예를 들면 다음과 같습니다.

```yaml
spec:
  containers:
    - name:
    ...
  securityContext:
    supplementalGroups: [5555]
```

1. `SecurityContext` 는 특정 컨테이너의 하위가 아닌 Pod 수준에서 정의해야 합니다.

2. Pod에 정의된 GID 배열입니다. 이 경우 배열에는 1개의 요소가 있습니다. 추가 GID는 쉼표로 구분됩니다.

Pod 요구사항을 충족할 수 있는 사용자 지정 SCC가 없는 경우 Pod는 `restricted` SCC와 일치할 수 있습니다. 이 SCC에는 `supplementalGroups` 전략이 `RunAsAny` 로 설정되어 있으므로, 범위를 확인하지 않고 제공되는 그룹 ID가 승인됩니다.

그 결과 위의 Pod에서 승인이 전달 및 실행됩니다. 그러나 그룹 ID 범위 확인이 필요한 경우에는 사용자 지정 SCC를 사용하는 것이 좋습니다. 사용자 지정 SCC를 생성하면 최소 및 최대 그룹 ID가 정의되고, 그룹 ID 범위 확인이 적용되며, `5555` 그룹 ID가 허용될 수 있습니다.

참고

사용자 정의 SCC를 사용하려면 먼저 적절한 서비스 계정에 추가해야 합니다. 예를 들어, `Pod` 사양에 다른 값이 지정된 경우를 제외하고 지정된 프로젝트에서 `기본` 서비스 계정을 사용하십시오.

#### 4.9.3.2. 사용자 ID

사용자 ID는 컨테이너 이미지 또는 `Pod` 정의에 정의할 수 있습니다.

참고

일반적으로 사용자 ID를 사용하는 대신 추가 그룹 ID를 사용하여 영구 스토리지에 대한 액세스 권한을 얻는 것이 좋습니다.

위에 표시된 예시 NFS 디렉터리에서 컨테이너는 UID가 `65534` 로 설정되고, 현재 그룹 ID를 무시해야 하므로 다음을 `Pod` 정의에 추가할 수 있습니다.

```yaml
spec:
  containers:
  - name:
  ...
    securityContext:
      runAsUser: 65534
```

1. Pod에는 각 컨테이너에 특정 `securityContext` 정의와 Pod에 정의된 모든 컨테이너에 적용되는 Pod의 `securityContext` 정의가 포함됩니다.

2. `65534` 는 `nfsnobody` 사용자입니다.

프로젝트가 `default` 이고 SCC가 `restricted` 라고 가정하면 Pod에서 요청한 대로 `65534` 의 사용자 ID가 허용되지 않습니다. 따라서 Pod가 다음과 같은 이유로 실패합니다.

`65534` 가 사용자 ID로 요청되었습니다.

Pod에서 사용할 수 있는 모든 SCC를 검사하여 어떤 SCC에서 `65534` 의 사용자 ID를 허용하는지 확인합니다. SCC의 모든 정책을 확인하는 동안 여기에는 중요한 사항은 사용자 ID입니다.

사용 가능한 모든 SCC는 `runAsUser` 전략에서 `MustRunAsRange` 를 사용하므로 UID 범위 검사가 필요합니다.

`65534` 는 SCC 또는 프로젝트의 사용자 ID 범위에 포함되어 있지 않습니다.

일반적으로 사전 정의된 SCC를 수정하지 않는 것이 좋습니다. 이 상황을 해결하기 위해 선호되는 방법은 사용자 정의 SCC를 생성하는 것입니다. 따라서 최소 및 최대 사용자 ID가 정의되고 UID 범위 검사가 여전히 적용되며, `65534` 의 UID가 허용됩니다.

참고

사용자 정의 SCC를 사용하려면 먼저 적절한 서비스 계정에 추가해야 합니다. 예를 들어, `Pod` 사양에 다른 값이 지정된 경우를 제외하고 지정된 프로젝트에서 `기본` 서비스 계정을 사용하십시오.

#### 4.9.3.3. SELinux

RHEL(Red Hat Enterprise Linux) 및 RHCOS(Red Hat Enterprise Linux CoreOS) 시스템은 기본적으로 원격 NFS 서버에서 SELinux를 사용하도록 구성됩니다.

RHEL 이외 및 비RHCOS 시스템의 경우 SELinux는 Pod에서 원격 NFS 서버로 쓰기를 허용하지 않습니다. NFS 볼륨이 올바르게 마운트되지만 읽기 전용입니다. 다음 절차에 따라 올바른 SELinux 권한을 활성화해야 합니다.

사전 요구 사항

`container-selinux` 패키지가 설치되어 있어야 합니다. 이 패키지는 `virt_use_nfs` SELinux 부울을 제공합니다.

절차

다음 명령을 사용하여 `virt_use_nfs` 부울을 활성화합니다. `-P` 옵션을 사용하면 재부팅할 때 이 부울을 지속적으로 사용할 수 있습니다.

```shell-session
# setsebool -P virt_use_nfs 1
```

#### 4.9.3.4. 내보내기 설정

컨테이너 사용자가 볼륨을 읽고 쓸 수 있도록 하려면 NFS 서버의 내보낸 각 볼륨은 다음 조건을 준수해야 합니다.

모든 내보내는 다음 형식을 사용하여 내보내야 합니다.

```shell-session
/<example_fs> *(rw,root_squash)
```

마운트 옵션으로 트래픽을 허용하도록 방화벽을 구성해야 합니다.

NFSv4의 경우 기본 포트 `2049` (nfs)를 구성합니다.

```shell-session
# iptables -I INPUT 1 -p tcp --dport 2049 -j ACCEPT
```

NFSv3의 경우 `2049` (nfs), `20048` (mountd) 및 `111` (portmapper)의 포트 3개가 있습니다.

```shell-session
# iptables -I INPUT 1 -p tcp --dport 2049 -j ACCEPT
```

```shell-session
# iptables -I INPUT 1 -p tcp --dport 20048 -j ACCEPT
```

```shell-session
# iptables -I INPUT 1 -p tcp --dport 111 -j ACCEPT
```

대상 Pod에서 액세스할 수 있도록 NFS 내보내기 및 디렉터리를 설정해야 합니다. 컨테이너의 기본 UID에 표시된 대로 내보내기를 컨테이너의 기본 UID로 설정하거나 위 그룹 ID에 표시된 대로 `supplementalGroups` 를 사용하여 Pod 그룹 액세스 권한을 제공합니다.

#### 4.9.4. 리소스 회수

NFS는 OpenShift Container Platform `Recyclable` 플러그인 인터페이스를 구현합니다. 자동 프로세스는 각 영구 볼륨에 설정된 정책에 따라 복구 작업을 처리합니다.

기본적으로 PV는 `Retain` 으로 설정됩니다.

PVC에 대한 클레임이 삭제되고 PV가 해제되면 PV 오브젝트를 재사용해서는 안 됩니다. 대신 원래 볼륨과 동일한 기본 볼륨 세부 정보를 사용하여 새 PV를 생성해야 합니다.

예를 들어, 관리자가 이름이 `nfs1` 인 PV를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs1
spec:
  capacity:
    storage: 1Mi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.1.1
    path: "/"
```

사용자가 `PVC1` 을 생성하여 `nfs1` 에 바인딩합니다. 그리고 사용자가 `PVC1` 에서 `nfs1` 클레임을 해제합니다. 그러면 `nfs1` 이 `Released` 상태가 됩니다. 관리자가 동일한 NFS 공유를 사용하려면 동일한 NFS 서버 세부 정보를 사용하여 새 PV를 생성해야 하지만 다른 PV 이름을 사용해야 합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs2
spec:
  capacity:
    storage: 1Mi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.1.1
    path: "/"
```

원래 PV를 삭제하고 동일한 이름으로 다시 생성하는 것은 권장되지 않습니다. `Released` 에서 `Available` 로 PV의 상태를 수동으로 변경하면 오류가 발생하거나 데이터가 손실될 수 있습니다.

#### 4.9.5. 추가 구성 및 문제 해결

사용되는 NFS 버전과 구성 방법에 따라 적절한 내보내기 및 보안 매핑에 필요한 추가 구성 단계가 있을 수 있습니다. 다음은 적용되는 몇 가지입니다.

| NFSv4 마운트에서 소유권이 `nobody:nobody` 인 모든 파일이 올바르게 표시되지 않습니다. | 이는 NFS의 `/etc/idmapd.conf` 에 있는 ID 매핑 설정으로 인한 것일 수 있습니다. 이 Red Hat 해결책 을 참조하십시오. |
| --- | --- |
| NFSv4에서 ID 매핑 비활성화 | NFS 서버에서 다음 명령을 실행합니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] # echo 'Y' > /sys/module/nfsd/parameters/nfs4_disable_idmapping [/CODE] |

### 4.10. Red Hat OpenShift Data Foundation

Red Hat OpenShift Data Foundation은 사내 또는 하이브리드 클라우드에서 파일, 블록 및 개체 스토리지를 지원하는 OpenShift Container Platform용 영구 스토리지 공급자입니다. Red Hat 스토리지 솔루션인 Red Hat OpenShift Data Foundation은 배포, 관리 및 모니터링을 위해 OpenShift Container Platform과 완전히 통합되어 있습니다. 자세한 내용은 Red Hat OpenShift Data Foundation 설명서를 참조하십시오.

중요

OpenShift Container Platform과 함께 설치된 가상 머신을 호스팅하는 하이퍼컨버지드 노드를 사용하는 가상화용 RHHI(Red Hat Hyperconverged Infrastructure) 상단에 있는 OpenShift Data Foundation은 지원되는 구성이 아닙니다. 지원되는 플랫폼에 대한 자세한 내용은 Red Hat OpenShift Data Foundation 지원 및 상호 운용성 가이드를 참조하십시오.

### 4.11. VMware vSphere 볼륨을 사용하는 영구 스토리지

OpenShift Container Platform을 사용하면 VMware vSphere의 VMDK(가상 머신 디스크) 볼륨을 사용할 수 있습니다. VMware vSphere를 사용하여 영구 스토리지로 OpenShift Container Platform 클러스터를 프로비저닝할 수 있습니다. Kubernetes 및 VMware vSphere에 대해 어느 정도 익숙한 것으로 가정합니다.

VMware vSphere 볼륨은 동적으로 프로비저닝할 수 있습니다. OpenShift Container Platform은 vSphere에서 디스크를 생성하고 이 디스크를 올바른 이미지에 연결합니다.

참고

OpenShift Container Platform은 새 볼륨을 독립 영구 디스크로 프로비저닝하여 클러스터의 모든 노드에서 볼륨을 자유롭게 연결 및 분리합니다. 결과적으로 스냅샷을 사용하는 볼륨을 백업하거나 스냅샷에서 볼륨을 복원할 수 없습니다. 자세한 내용은 스냅 샷 제한 을 참조하십시오.

Kubernetes 영구 볼륨 프레임워크를 사용하면 관리자는 영구 스토리지로 클러스터를 프로비저닝하고 사용자가 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다.

영구 볼륨은 단일 프로젝트 또는 네임스페이스에 바인딩되지 않으며, OpenShift Container Platform 클러스터에서 공유할 수 있습니다. 영구 볼륨 클레임은 프로젝트 또는 네임스페이스에 고유하며 사용자가 요청할 수 있습니다.

중요

새로운 설치의 경우 OpenShift Container Platform 4.13 이상에서는 vSphere in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 동등한 CSI 드라이버로 제공합니다. OpenShift Container Platform 4.15 이상으로 업데이트하면 자동 마이그레이션도 제공됩니다. 업데이트 및 마이그레이션에 대한 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

CSI 자동 마이그레이션이 원활해야 합니다. 마이그레이션은 영구 볼륨, 영구 볼륨 클레임 및 스토리지 클래스와 같은 기존 API 오브젝트를 사용하는 방법을 변경하지 않습니다.

추가 리소스

VMware vSphere

#### 4.11.1. 동적으로 VMware vSphere 볼륨 프로비저닝

동적으로 VMware vSphere 볼륨 프로비저닝은 권장되는 방법입니다.

#### 4.11.2. 사전 요구 사항

사용하는 구성 요소의 요구사항을 충족하는 VMware vSphere 버전 6 인스턴스에 OpenShift Container Platform 클러스터가 설치되어 있어야 합니다. vSphere 버전 지원에 대한 자세한 내용은 vSphere에 클러스터 설치를 참조하십시오.

다음 절차 중 하나를 사용하여 기본 스토리지 클래스를 사용하여 이러한 볼륨을 동적으로 프로비저닝할 수 있습니다.

#### 4.11.2.1. UI를 사용하여 VMware vSphere 볼륨을 동적으로 프로비저닝

OpenShift Container Platform은 볼륨을 프로비저닝하기 위해 `thin` 디스크 형식을 사용하는 이름이 `thin` 인 기본 스토리지 클래스를 설치합니다.

사전 요구 사항

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다.

절차

OpenShift Container Platform 콘솔에서 스토리지 → 영구 볼륨 클레임 을 클릭합니다.

영구 볼륨 클레임 생성 개요에서 영구 볼륨 클레임 생성 을 클릭합니다.

결과 페이지에 필요한 옵션을 정의합니다.

`thin` 스토리지 클래스를 선택합니다.

스토리지 클레임의 고유한 이름을 입력합니다.

액세스 모드를 선택하여 생성된 스토리지 클레임에 대한 읽기 및 쓰기 액세스를 결정합니다.

스토리지 클레임의 크기를 정의합니다.

만들기 를 클릭하여 영구 볼륨 클레임을 생성하고 영구 볼륨을 생성합니다.

#### 4.11.2.2. CLI를 사용하여 VMware vSphere 볼륨을 동적으로 프로비저닝

OpenShift Container Platform은 볼륨 프로비저닝에 `thin` 디스크 형식을 사용하는 이름이 `thin` 인 기본 StorageClass를 설치합니다.

사전 요구 사항

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다.

절차(CLI)

다음 콘텐츠와 함께 `pvc.yaml` 파일을 생성하여 VMware vSphere PersistentVolumeClaim을 정의할 수 있습니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

1. 영구 볼륨 오브젝트를 표시하는 고유한 이름입니다.

2. 영구 볼륨 클레임의 액세스 모드입니다. `ReadWriteOnce` 를 사용하면 단일 노드에서 읽기 및 쓰기 권한으로 볼륨을 마운트할 수 있습니다.

3. 영구 볼륨 클레임의 크기입니다.

다음 명령을 입력하여 파일에서 `PersistentVolumeClaim` 오브젝트를 생성합니다.

```shell-session
$ oc create -f pvc.yaml
```

#### 4.11.3. 정적으로 프로비저닝 VMware vSphere 볼륨

VMware vSphere 볼륨을 정적으로 프로비저닝하려면 영구 볼륨 프레임워크를 참조하기 위해 가상 머신 디스크를 생성해야 합니다.

사전 요구 사항

OpenShift Container Platform에서 볼륨으로 마운트하기 전에 기본 인프라에 스토리지가 있어야 합니다.

절차

가상 머신 디스크를 생성합니다. VMDK(가상 머신 디스크)는 정적으로 VMware vSphere 볼륨을 프로비저닝하기 전에 수동으로 생성해야 합니다. 다음 방법 중 하나를 사용합니다.

`vmkfstools` 를 사용하여 생성합니다. SSH(Secure Shell)를 통해 ESX에 액세스한 후 다음 명령을 사용하여 VMDK 볼륨을 생성합니다.

```shell-session
$ vmkfstools -c <size> /vmfs/volumes/<datastore-name>/volumes/<disk-name>.vmdk
```

`vmware-diskmanager` 를 사용하여 생성합니다.

```shell-session
$ shell vmware-vdiskmanager -c -t 0 -s <size> -a lsilogic <disk-name>.vmdk
```

VMDK를 참조하는 영구 볼륨을 생성합니다. `PersistentVolume` 오브젝트 정의를 사용하여 `pv1.yaml` 파일을 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv1
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  vsphereVolume:
    volumePath: "[datastore1] volumes/myDisk"
    fsType: ext4
```

1. 볼륨의 이름입니다. 이 이름을 사용하여 영구 볼륨 클레임 또는 Pod에 의해 식별됩니다.

2. 이 볼륨에 할당된 스토리지의 용량입니다.

3. vSphere 볼륨을 위해 `vsphereVolume` 과 함께 사용되는 볼륨 유형입니다. 레이블은 vSphere VMDK 볼륨을 Pod에 마운트하는 데 사용됩니다. 볼륨의 내용은 마운트 해제 시 보존됩니다. 볼륨 유형은 VMFS 및 VSAN 데이터 저장소를 지원합니다.

4. 사용할 기존 VMDK 볼륨입니다. `vmkfstools` 를 사용하는 경우 이전에 설명된 대로 볼륨 정의에서 데이터 저장소의 이름을 대괄호 `[]` 로 감싸야 합니다.

5. 마운트할 파일 시스템 유형입니다. 예를 들어, ext4, xfs 또는 기타 파일 시스템이 이에 해당합니다.

중요

볼륨이 포맷 및 프로비저닝된 후 fsType 매개변수 값을 변경하면 데이터가 손실되거나 Pod 오류가 발생할 수 있습니다.

파일에서 `PersistentVolume` 오브젝트를 만듭니다.

```shell-session
$ oc create -f pv1.yaml
```

이전 단계에서 생성한 영구 볼륨 클레임에 매핑되는 영구 볼륨 클레임을 생성합니다. `PersistentVolumeClaim` 오브젝트 정의를 사용하여 `pvc1.yaml` 파일을 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc1
spec:
  accessModes:
    - ReadWriteOnce
  resources:
   requests:
     storage: "1Gi"
  volumeName: pv1
```

1. 영구 볼륨 오브젝트를 표시하는 고유한 이름입니다.

2. 영구 볼륨 클레임의 액세스 모드입니다. ReadWriteOnce를 사용하면 단일 노드에서 읽기 및 쓰기 권한으로 볼륨을 마운트할 수 있습니다.

3. 영구 볼륨 클레임의 크기입니다.

4. 기존 영구 볼륨의 이름입니다.

파일에서 `PersistentVolumeClaim` 오브젝트를 만듭니다.

```shell-session
$ oc create -f pvc1.yaml
```

#### 4.11.3.1. VMware vSphere 볼륨 포맷

OpenShift Container Platform이 볼륨을 마운트하고 컨테이너에 전달하기 전에 `PersistentVolume` (PV) 정의에 있는 `fsType` 매개변수 값에 의해 지정된 파일 시스템이 볼륨에 포함되어 있는지 확인합니다. 장치가 파일 시스템으로 포맷되지 않으면 장치의 모든 데이터가 삭제되고 장치는 지정된 파일 시스템에서 자동으로 포맷됩니다.

OpenShift Container Platform은 처음 사용하기 전에 포맷되므로 vSphere 볼륨을 PV로 사용할 수 있습니다.

### 5.1. 로컬 스토리지 개요

다음 솔루션을 사용하여 로컬 스토리지를 프로비저닝할 수 있습니다.

HostPath Provisioner (HPP)

LSO(Local Storage Operator)

LVM(Logical Volume Manager) 스토리지

주의

이러한 솔루션은 노드 로컬 스토리지 프로비저닝만 지원합니다. 워크로드는 스토리지를 제공하는 노드에 바인딩됩니다. 노드를 사용할 수 없게 되면 워크로드도 사용할 수 없게 됩니다. 노드 장애에도 불구하고 워크로드 가용성을 유지하려면 활성 또는 수동 복제 메커니즘을 통해 스토리지 데이터 복제를 확인해야 합니다.

#### 5.1.1. HostPath Provisioner 기능 개요

HPP(HostPath Provisioner)를 사용하여 다음 작업을 수행할 수 있습니다.

로컬 스토리지를 프로비저닝하기 위해 호스트 파일 시스템 경로를 스토리지 클래스에 매핑합니다.

스토리지 사용을 위해 노드에서 파일 시스템 경로를 구성하는 스토리지 클래스를 정적으로 생성합니다.

스토리지 클래스를 기반으로 영구 볼륨(PV)을 정적으로 프로비저닝합니다.

기본 스토리지 토폴로지를 인식하는 동안 워크로드 및 PVC(영구 볼륨)를 생성합니다.

참고

HPP는 업스트림 Kubernetes에서 사용할 수 있습니다. 그러나 업스트림 Kubernetes에서 HPP를 사용하지 않는 것이 좋습니다.

#### 5.1.2. Local Storage Operator 기능 개요

LSO(Local Storage Operator)를 사용하여 다음 작업을 수행할 수 있습니다.

장치 구성을 수정하지 않고 스토리지 장치(디스크 또는 파티션)를 스토리지 클래스에 할당합니다.

`LocalVolume` CR(사용자 정의 리소스)을 구성하여 PV 및 스토리지 클래스를 정적으로 프로비저닝합니다.

기본 스토리지 토폴로지를 인식하는 동안 워크로드 및 PVC를 생성합니다.

참고

LSO는 Red Hat에서 개발하고 제공합니다.

#### 5.1.3. LVM 스토리지 기능 개요

LVM(Logical Volume Manager) 스토리지를 사용하여 다음 작업을 수행할 수 있습니다.

스토리지 장치(디스크 또는 파티션)를 lvm2 볼륨 그룹으로 구성하고 볼륨 그룹을 스토리지 클래스로 노출합니다.

노드 토폴로지를 고려하지 않고 PVC를 사용하여 워크로드를 생성하고 스토리지를 요청합니다.

LVM 스토리지는 TopoLVM CSI 드라이버를 사용하여 토폴로지의 노드에 스토리지 공간을 동적으로 할당하고 PV를 프로비저닝합니다.

참고

LVM 스토리지는 Red Hat에서 개발하고 유지 관리합니다. LVM Storage와 함께 제공되는 CSI 드라이버는 업스트림 프로젝트 "topolvm"입니다.

#### 5.1.4. LVM 스토리지, LSO 및 HPP 비교

다음 섹션에서는 로컬 스토리지를 프로비저닝하는 LVM Storage, LSO(Local Storage Operator) 및 HPP(HostPath Provisioner)에서 제공하는 기능을 비교합니다.

#### 5.1.4.1. 스토리지 유형 및 파일 시스템에 대한 지원 비교

다음 표에서는 LVM 스토리지, LSO(Local Storage Operator) 및 HPP(HostPath Provisioner)에서 제공하는 스토리지 유형 및 파일 시스템에 대한 지원을 비교하여 로컬 스토리지를 프로비저닝합니다.

| 기능 | LVM 스토리지 | LSO | HPP |
| --- | --- | --- | --- |
| 블록 스토리지 지원 | 제공됨 | 제공됨 | 없음 |
| 파일 스토리지 지원 | 제공됨 | 제공됨 | 제공됨 |
| 오브젝트 스토리지 지원 [1] | 없음 | 없음 | 없음 |
| 사용 가능한 파일 시스템 | `ext4` , `xfs` | `ext4` , `xfs` | 노드에서 사용 가능한 마운트된 시스템이 지원됩니다. |

어떤 솔루션(LVM Storage, LSO 및 HPP)은 개체 스토리지를 지원하지 않습니다. 따라서 오브젝트 스토리지를 사용하려면 Red Hat OpenShift Data Foundation의 `MultiClusterGateway` 와 같은 S3 오브젝트 스토리지 솔루션이 필요합니다. 모든 솔루션은 S3 오브젝트 스토리지 솔루션의 기본 스토리지 공급자 역할을 할 수 있습니다.

#### 5.1.4.2. 핵심 기능에 대한 지원 비교

다음 표는 LVM 스토리지, LSO(Local Storage Operator) 및 HPP(HostPath Provisioner)가 로컬 스토리지 프로비저닝을 위한 핵심 기능을 지원하는 방법을 비교합니다.

| 기능 | LVM 스토리지 | LSO | HPP |
| --- | --- | --- | --- |
| 자동 파일 시스템 포맷 지원 | 제공됨 | 제공됨 | 해당 없음 |
| 동적 프로비저닝 지원 | 제공됨 | 없음 | 없음 |
| RAID(Redundant Array of Independent Disks) 어레이 사용 지원 | 제공됨 4.15 이상에서 지원됩니다. | 제공됨 | 제공됨 |
| 투명한 디스크 암호화 지원 | 제공됨 4.16 이상에서 지원됩니다. | 제공됨 | 제공됨 |
| 볼륨 기반 디스크 암호화 지원 | 없음 | 없음 | 없음 |
| 연결이 끊긴 설치 지원 | 제공됨 | 제공됨 | 제공됨 |
| PVC 확장 지원 | 제공됨 | 없음 | 없음 |
| 볼륨 스냅샷 및 볼륨 복제 지원 | 제공됨 | 없음 | 없음 |
| 씬 프로비저닝 지원 | 제공됨 장치는 기본적으로 씬 프로비저닝됩니다. | 제공됨 씬 프로비저닝된 볼륨을 가리키도록 장치를 구성할 수 있습니다. | 제공됨 씬 프로비저닝된 볼륨을 가리키도록 경로를 구성할 수 있습니다. |
| 자동 디스크 검색 및 설정 지원 | 제공됨 자동 디스크 검색은 설치 및 런타임 중에 사용할 수 있습니다. `LVMCluster` CR(사용자 정의 리소스)에 디스크를 동적으로 추가하여 기존 스토리지 클래스의 스토리지 용량을 늘릴 수도 있습니다. | 기술 프리뷰 자동 디스크 검색은 설치 중에 사용할 수 있습니다. | 없음 |

#### 5.1.4.3. 성능 및 격리 기능 비교

다음 표에서는 로컬 스토리지 프로비저닝의 LVM Storage, LSO(Local Storage Operator) 및 HPP(HostPath Provisioner)의 성능 및 격리 기능을 비교합니다.

| 기능 | LVM 스토리지 | LSO | HPP |
| --- | --- | --- | --- |
| 성능 | 동일한 스토리지 클래스를 사용하는 모든 워크로드에 대해 I/O 속도가 공유됩니다. 블록 스토리지를 사용하면 직접 I/O 작업을 수행할 수 있습니다. 씬 프로비저닝은 성능에 영향을 미칠 수 있습니다. | I/O는 LSO 구성에 따라 다릅니다. 블록 스토리지를 사용하면 직접 I/O 작업을 수행할 수 있습니다. | 동일한 스토리지 클래스를 사용하는 모든 워크로드에 대해 I/O 속도가 공유됩니다. 기본 파일 시스템에 의해 부과되는 제한 사항은 I/O 속도에 영향을 미칠 수 있습니다. |
| 격리 경계 [1] | LVM 논리 볼륨(LV) HPP에 비해 높은 수준의 격리를 제공합니다. | LVM 논리 볼륨(LV) HPP에 비해 높은 수준의 격리를 제공합니다. | 파일 시스템 경로 LSO 및 LVM 스토리지에 비해 낮은 수준의 격리를 제공합니다. |

격리 경계는 로컬 스토리지 리소스를 사용하는 다양한 워크로드 또는 애플리케이션 간의 분리 수준을 나타냅니다.

#### 5.1.4.4. 추가 기능에 대한 지원 비교

다음 표에서는 로컬 스토리지를 프로비저닝하기 위해 LVM Storage, LSO(Local Storage Operator) 및 HPP(HostPath Provisioner)에서 제공하는 추가 기능을 비교합니다.

| 기능 | LVM 스토리지 | LSO | HPP |
| --- | --- | --- | --- |
| 일반 임시 볼륨 지원 | 제공됨 | 없음 | 없음 |
| CSI 인라인 임시 볼륨 지원 | 없음 | 없음 | 없음 |
| 스토리지 토폴로지 지원 | 제공됨 CSI 노드 토폴로지 지원 | 제공됨 LSO는 노드 허용 오차를 통해 스토리지 토폴로지에 대한 부분적인 지원을 제공합니다. | 없음 |
| RWX( `ReadWriteMany` ) 액세스 모드 지원 [1] | 없음 | 없음 | 없음 |

모든 솔루션(LVM Storage, LSO 및 HPP)에는 RWO(`ReadWriteOnce`) 액세스 모드가 있습니다. RWO 액세스 모드를 사용하면 동일한 노드의 여러 Pod에서 액세스할 수 있습니다.

### 5.2. 로컬 블록을 사용하는 영구 스토리지

OpenShift Container Platform은 로컬 볼륨을 사용하여 영구 스토리지를 통해 프로비저닝될 수 있습니다. 로컬 영구 볼륨을 사용하면 표준 영구 볼륨 클레임 인터페이스를 사용하여 디스크 또는 파티션과 같은 로컬 스토리지 장치에 액세스할 수 있습니다.

시스템에서 볼륨 노드 제약 조건을 인식하고 있기 때문에 로컬 볼륨은 노드에 수동으로 Pod를 예약하지 않고 사용할 수 있습니다. 그러나 로컬 볼륨은 여전히 기본 노드의 가용성에 따라 달라지며 일부 애플리케이션에는 적합하지 않습니다.

참고

로컬 볼륨은 정적으로 생성된 영구 볼륨으로 사용할 수 있습니다.

#### 5.2.1. Local Storage Operator 설치

Local Storage Operator는 기본적으로 OpenShift Container Platform에 설치되지 않습니다. 다음 절차에 따라 이 Operator를 설치하고 구성하여 클러스터에서 로컬 볼륨을 활성화합니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔 또는 CLI(명령줄 인터페이스)에 액세스할 수 있습니다.

절차

`openshift-local-storage` 프로젝트를 생성합니다.

```shell-session
$ oc adm new-project openshift-local-storage
```

선택 사항: 인프라 노드에서 로컬 스토리지 생성을 허용합니다.

Local Storage Operator를 사용하여 로깅 및 모니터링과 같은 구성 요소를 지원하는 인프라 노드에 볼륨을 생성할 수 있습니다.

Local Storage Operator에 작업자 노드가 아닌 인프라 노드가 포함되도록 기본 노드 선택기를 조정해야 합니다.

Local Storage Operator가 클러스터 전체 기본 선택기를 상속하지 못하도록 하려면 다음 명령을 입력합니다.

```shell-session
$ oc annotate namespace openshift-local-storage openshift.io/node-selector=''
```

선택 사항: 단일 노드 배포의 CPU 관리 풀에서 로컬 스토리지를 실행할 수 있습니다.

단일 노드 배포에서 Local Storage Operator를 사용하고 `management` 풀에 속하는 CPU를 사용할 수 있습니다. 관리 워크로드 파티셔닝을 사용하는 단일 노드 설치에서 이 단계를 수행합니다.

Local Storage Operator가 관리 CPU 풀에서 실행되도록 하려면 다음 명령을 실행합니다.

```shell-session
$ oc annotate namespace openshift-local-storage workload.openshift.io/allowed='management'
```

UI에서

웹 콘솔에서 Local Storage Operator를 설치하려면 다음 단계를 따르십시오.

OpenShift Container Platform 웹 콘솔에 로그인합니다.

에코시스템 → 소프트웨어 카탈로그 로 이동합니다.

Local Storage 를 필터 상자에 입력하여 Local Storage Operator를 찾습니다.

설치 를 클릭합니다.

Operator 설치 페이지에서 클러스터의 특정 네임스페이스 를 선택합니다. 드롭다운 메뉴에서 openshift-local-storage 를 선택합니다.

업데이트 채널 및 승인 전략 값을 원하는 값으로 조정합니다.

설치 를 클릭합니다.

완료되면 Local Storage Operator가 웹 콘솔의 설치된 Operator 섹션에 나열됩니다.

CLI에서

CLI에서 Local Storage Operator를 설치합니다.

`openshift-local-storage.yaml` 과 같은 Local Storage Operator의 Operator 그룹 및 서브스크립션을 정의하는 오브젝트 YAML 파일을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: local-operator-group
  namespace: openshift-local-storage
spec:
  targetNamespaces:
    - openshift-local-storage
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: local-storage-operator
  namespace: openshift-local-storage
spec:
  channel: stable
  installPlanApproval: Automatic
  name: local-storage-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

1. 설치 계획에 대한 사용자 승인 정책입니다.

다음 명령을 입력하여 Local Storage Operator 오브젝트를 생성합니다.

```shell-session
$ oc apply -f openshift-local-storage.yaml
```

이 시점에서 OLM(Operator Lifecycle Manager)은 Local Storage Operator를 인식합니다. Operator의 ClusterServiceVersion (CSV)이 대상 네임스페이스에 표시되고 Operator가 제공한 API를 작성할 수 있어야 합니다.

모든 Pod 및 Local Storage Operator가 생성되었는지 확인하여 로컬 스토리지 설치를 확인합니다.

필요한 모든 Pod가 생성되었는지 확인합니다.

```shell-session
$ oc -n openshift-local-storage get pods
```

```shell-session
NAME                                      READY   STATUS    RESTARTS   AGE
local-storage-operator-746bf599c9-vlt5t   1/1     Running   0          19m
```

CSV(ClusterServiceVersion) YAML 매니페스트를 확인하여 `openshift-local-storage` 프로젝트에서 Local Storage Operator를 사용할 수 있는지 확인합니다.

```shell-session
$ oc get csvs -n openshift-local-storage
```

```shell-session
NAME                                         DISPLAY         VERSION               REPLACES   PHASE
local-storage-operator.4.2.26-202003230335   Local Storage   4.2.26-202003230335              Succeeded
```

모든 확인이 통과되면 Local Storage Operator가 성공적으로 설치됩니다.

#### 5.2.2. Local Storage Operator를 사용하여 로컬 볼륨을 프로비저닝

동적 프로비저닝을 통해 로컬 볼륨을 생성할 수 없습니다. 대신 Local Storage Operator에서 영구 볼륨을 생성할 수 있습니다. 로컬 볼륨 프로비저너는 정의된 리소스에 지정된 경로에서 모든 파일 시스템 또는 블록 볼륨 장치를 찾습니다.

사전 요구 사항

Local Storage Operator가 설치되어 있습니다.

다음 조건을 충족하는 로컬 디스크가 있습니다.

노드에 연결되어 있습니다.

마운트되지 않았습니다.

파티션이 포함되어 있지 않습니다.

프로세스

로컬 볼륨 리소스를 생성합니다. 이 리소스는 로컬 볼륨에 대한 노드 및 경로를 정의해야 합니다.

참고

동일한 장치에 다른 스토리지 클래스 이름을 사용하지 마십시오. 이렇게 하면 여러 영구 볼륨(PV)이 생성됩니다.

```yaml
apiVersion: "local.storage.openshift.io/v1"
kind: "LocalVolume"
metadata:
  name: "local-disks"
  namespace: "openshift-local-storage"
spec:
  nodeSelector:
    nodeSelectorTerms:
    - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - ip-10-0-140-183
          - ip-10-0-158-139
          - ip-10-0-164-33
  storageClassDevices:
    - storageClassName: "local-sc"
      forceWipeDevicesAndDestroyAllData: false
      volumeMode: Filesystem
      fsType: xfs
      devicePaths:
        - /path/to/device
```

1. Local Storage Operator가 설치된 네임스페이스입니다.

2. 선택 사항: 로컬 스토리지 볼륨이 연결된 노드 목록이 포함된 노드 선택기입니다. 이 예에서는 다음 명령에서 가져온 노드 호스트 이름을 사용합니다. 값을 정의하지 않으면 Local Storage Operator에서 사용 가능한 모든 노드에서 일치하는 디스크를 찾습니다.

```shell
oc get node
```

3. 영구 볼륨 오브젝트를 생성할 때 사용할 스토리지 클래스의 이름입니다. Local Storage Operator가 존재하지 않는 경우 스토리지 클래스를 자동으로 생성합니다. 이 로컬 볼륨 세트를 고유하게 식별하는 스토리지 클래스를 사용해야 합니다.

4. 이 설정은 `wipefs` 를 호출할지 여부를 정의합니다. 즉, 파티션 테이블 서명(마이크 문자열)을 제거하여 LSO(Local Storage Operator) 프로비저닝에 디스크를 사용할 준비가 되었습니다. 서명 이외의 다른 데이터는 삭제되지 않습니다. 기본값은 "false"입니다(`wipefs` 가 호출되지 않음). `forceWipeDevicesAndDestroyAllData` 를 "true"로 설정하면 이전 데이터를 다시 사용해야 하는 디스크에 남아 있을 수 있는 시나리오에서 유용할 수 있습니다. 이러한 시나리오에서는 이 필드를 true로 설정하면 관리자가 디스크를 수동으로 지울 필요가 없습니다. 이러한 경우는 단일 노드 OpenShift(SNO) 클러스터 환경이 포함될 수 있습니다. 노드를 여러 번 재배포할 수 있거나 OpenShift Data Foundation(ODF)을 사용할 때 이전 데이터가 개체 스토리지 장치(OSD)로 사용되는 디스크에 남아 있을 수 있습니다.

5. 로컬 볼륨의 유형을 정의하는 `Filesystem` 또는 `Block` 중 하나에 해당 볼륨 모드입니다.

참고

원시 블록 볼륨(`volumeMode: Block`)은 파일 시스템으로 포맷되지 않습니다. Pod에서 실행되는 모든 애플리케이션이 원시 블록 장치를 사용할 수 있는 경우에만 이 모드를 사용합니다.

6. 로컬 볼륨이 처음 마운트될 때 생성되는 파일 시스템입니다.

7. 선택할 로컬 스토리지 장치 목록이 포함된 경로입니다.

8. 이 값을 `LocalVolume` 리소스의 실제 로컬 디스크 파일 경로(예: `/dev/disk/ by-id /wwn`)로 바꿉니다. 프로비저너가 배포되면 이러한 로컬 디스크에 PV가 생성됩니다.

참고

RHEL KVM을 사용하여 OpenShift Container Platform을 실행하는 경우 VM 디스크에 일련 번호를 할당해야 합니다. 그렇지 않으면 재부팅 후 VM 디스크를 식별할 수 없습니다. > 명령을 사용하여 <serial> `mydisk</serial` > 정의를 추가할 수 있습니다.

```shell
virsh edit <VM
```

```yaml
apiVersion: "local.storage.openshift.io/v1"
kind: "LocalVolume"
metadata:
  name: "local-disks"
  namespace: "openshift-local-storage"
spec:
  nodeSelector:
    nodeSelectorTerms:
    - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - ip-10-0-136-143
          - ip-10-0-140-255
          - ip-10-0-144-180
  storageClassDevices:
    - storageClassName: "local-sc"
      forceWipeDevicesAndDestroyAllData: false
      volumeMode: Block
      devicePaths:
        - /path/to/device
```

1. Local Storage Operator가 설치된 네임스페이스입니다.

2. 선택 사항: 로컬 스토리지 볼륨이 연결된 노드 목록이 포함된 노드 선택기입니다. 이 예에서는 다음 명령에서 가져온 노드 호스트 이름을 사용합니다. 값을 정의하지 않으면 Local Storage Operator에서 사용 가능한 모든 노드에서 일치하는 디스크를 찾습니다.

```shell
oc get node
```

3. 영구 볼륨 오브젝트를 생성할 때 사용할 스토리지 클래스의 이름입니다.

4. 이 설정은 `wipefs` 를 호출할지 여부를 정의합니다. 즉, 파티션 테이블 서명(마이크 문자열)을 제거하여 LSO(Local Storage Operator) 프로비저닝에 디스크를 사용할 준비가 되었습니다. 서명 이외의 다른 데이터는 삭제되지 않습니다. 기본값은 "false"입니다(`wipefs` 가 호출되지 않음). `forceWipeDevicesAndDestroyAllData` 를 "true"로 설정하면 이전 데이터를 다시 사용해야 하는 디스크에 남아 있을 수 있는 시나리오에서 유용할 수 있습니다. 이러한 시나리오에서는 이 필드를 true로 설정하면 관리자가 디스크를 수동으로 지울 필요가 없습니다. 이러한 경우는 단일 노드 OpenShift(SNO) 클러스터 환경이 포함될 수 있습니다. 노드를 여러 번 재배포할 수 있거나 OpenShift Data Foundation(ODF)을 사용할 때 이전 데이터가 개체 스토리지 장치(OSD)로 사용되는 디스크에 남아 있을 수 있습니다.

5. 로컬 볼륨의 유형을 정의하는 `Filesystem` 또는 `Block` 중 하나에 해당 볼륨 모드입니다.

6. 선택할 로컬 스토리지 장치 목록이 포함된 경로입니다.

7. 이 값을 `LocalVolume` 리소스의 실제 로컬 디스크 파일 경로(예: `dev/disk/ by-id /wwn`)로 바꿉니다. 프로비저너가 배포되면 이러한 로컬 디스크에 PV가 생성됩니다.

참고

RHEL KVM을 사용하여 OpenShift Container Platform을 실행하는 경우 VM 디스크에 일련 번호를 할당해야 합니다. 그렇지 않으면 재부팅 후 VM 디스크를 식별할 수 없습니다. > 명령을 사용하여 <serial> `mydisk</serial` > 정의를 추가할 수 있습니다.

```shell
virsh edit <VM
```

OpenShift Container Platform 클러스터에 로컬 볼륨 리소스를 생성합니다. 방금 생성한 파일을 지정합니다.

```shell-session
$ oc create -f <local-volume>.yaml
```

프로비저너가 생성되었고 해당 데몬 세트가 생성되었는지 확인합니다.

```shell-session
$ oc get all -n openshift-local-storage
```

```shell-session
NAME                                          READY   STATUS    RESTARTS   AGE
pod/diskmaker-manager-9wzms                   1/1     Running   0          5m43s
pod/diskmaker-manager-jgvjp                   1/1     Running   0          5m43s
pod/diskmaker-manager-tbdsj                   1/1     Running   0          5m43s
pod/local-storage-operator-7db4bd9f79-t6k87   1/1     Running   0          14m

NAME                                     TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
service/local-storage-operator-metrics   ClusterIP   172.30.135.36   <none>        8383/TCP,8686/TCP   14m

NAME                               DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/diskmaker-manager   3         3         3       3            3           <none>          5m43s

NAME                                     READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/local-storage-operator   1/1     1            1           14m

NAME                                                DESIRED   CURRENT   READY   AGE
replicaset.apps/local-storage-operator-7db4bd9f79   1         1         1       14m
```

필요한 데몬 세트 프로세스 및 현재 개수를 기록해 둡니다. `0` 의 개수는 레이블 선택기가 유효하지 않음을 나타냅니다.

영구 볼륨이 생성되었는지 확인합니다.

```shell-session
$ oc get pv
```

```shell-session
NAME                CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
local-pv-1cec77cf   100Gi      RWO            Delete           Available           local-sc                88m
local-pv-2ef7cd2a   100Gi      RWO            Delete           Available           local-sc                82m
local-pv-3fa1c73    100Gi      RWO            Delete           Available           local-sc                48m
```

중요

`LocalVolume` 오브젝트 편집은 안전하지 않은 작업이므로 이를 수행하면 기존 영구 볼륨의 `fsType` 또는 `volumeMode` 가 변경되지 않습니다.

#### 5.2.3. Local Storage Operator없이 로컬 볼륨 프로비저닝

동적 프로비저닝을 통해 로컬 볼륨을 생성할 수 없습니다. 대신 개체 정의에서 영구 볼륨(PV)을 정의하여 영구 볼륨을 생성할 수 있습니다. 로컬 볼륨 프로비저너는 정의된 리소스에 지정된 경로에서 모든 파일 시스템 또는 블록 볼륨 장치를 찾습니다.

중요

PVC가 삭제될 때 PV를 수동으로 프로비저닝하면 PV를 재사용할 때 데이터 누출의 위험이 발생할 수 있습니다. Local Storage Operator는 로컬 PV를 프로비저닝할 때 장치의 라이프 사이클을 자동화하는 것이 좋습니다.

사전 요구 사항

로컬 디스크가 OpenShift Container Platform 노드에 연결되어 있습니다.

프로세스

PV를 정의합니다. `PersistentVolume` 오브젝트 정의로 `example-pv-filesystem.yaml` 또는 `example-pv-block.yaml` 과 같은 파일을 생성합니다. 이 리소스는 로컬 볼륨에 대한 노드 및 경로를 정의해야 합니다.

참고

동일한 장치에 다른 스토리지 클래스 이름을 사용하지 마십시오. 이렇게 하면 여러 PV가 생성됩니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: example-pv-filesystem
spec:
  capacity:
    storage: 100Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-sc
  local:
    path: /dev/xvdf
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - example-node
```

1. PV의 유형을 정의하는 `Filesystem` 또는 `Block` 중 하나에 해당 볼륨 모드입니다.

2. PV 리소스를 생성할 때 사용할 스토리지 클래스의 이름입니다. 이 PV 세트를 고유하게 식별하는 스토리지 클래스를 사용합니다.

3. 또는 디렉터리에서 선택할 로컬 스토리지 장치 목록이 포함된 경로입니다. `Filesystem`

`volumeMode` 가 있는 디렉터리만 지정할 수 있습니다.

참고

원시 블록 볼륨(`volumeMode: block`)은 파일 시스템과 함께 포맷되지 않습니다. Pod에서 실행되는 모든 애플리케이션이 원시 블록 장치를 사용할 수 있는 경우에만 이 모드를 사용합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: example-pv-block
spec:
  capacity:
    storage: 100Gi
  volumeMode: Block
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-sc
  local:
    path: /dev/xvdf
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - example-node
```

1. PV의 유형을 정의하는 `Filesystem` 또는 `Block` 중 하나에 해당 볼륨 모드입니다.

2. PV 리소스를 생성할 때 사용할 스토리지 클래스의 이름입니다. 이 PV 세트를 고유하게 식별하는 스토리지 클래스를 사용해야 합니다.

3. 선택할 로컬 스토리지 장치 목록이 포함된 경로입니다.

OpenShift Container Platform 클러스터에 PV 리소스를 생성합니다. 방금 생성한 파일을 지정합니다.

```shell-session
$ oc create -f <example-pv>.yaml
```

로컬 PV가 생성되었는지 확인합니다.

```shell-session
$ oc get pv
```

```shell-session
NAME                    CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                STORAGECLASS    REASON   AGE
example-pv-filesystem   100Gi      RWO            Delete           Available                        local-sc            3m47s
example-pv1             1Gi        RWO            Delete           Bound       local-storage/pvc1   local-sc            12h
example-pv2             1Gi        RWO            Delete           Bound       local-storage/pvc2   local-sc            12h
example-pv3             1Gi        RWO            Delete           Bound       local-storage/pvc3   local-sc            12h
```

#### 5.2.4. 로컬 볼륨 영구 볼륨 클레임 생성

로컬 볼륨은 Pod가 액세스할 수 있는 영구 볼륨 클레임(PVC)으로서 정적으로 생성되어야 합니다.

사전 요구 사항

영구 볼륨은 로컬 볼륨 프로비저너를 사용하여 생성됩니다.

절차

해당 스토리지 클래스를 사용하여 PVC를 생성합니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: local-pvc-name
spec:
  accessModes:
  - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 100Gi
  storageClassName: local-sc
```

1. PVC의 이름입니다.

2. PVC의 유형입니다. 기본값은 `Filesystem` 입니다.

3. PVC에서 사용할 수 있는 스토리지 용량입니다.

4. 클레임에 필요한 스토리지 클래스의 이름입니다.

방금 작성한 파일을 지정하여 OpenShift Container Platform 클러스터에서 PVC를 생성합니다.

```shell-session
$ oc create -f <local-pvc>.yaml
```

#### 5.2.5. 로컬 클레임 연결

로컬 볼륨이 영구 볼륨 클레임에 매핑된 후 리소스 내부에서 지정할 수 있습니다.

사전 요구 사항

동일한 네임스페이스에 영구 볼륨 클레임이 있어야 합니다.

절차

리소스 사양에 정의된 클레임을 포함합니다. 다음 예시는 Pod 내에서 영구 볼륨 클레임을 선언합니다.

```yaml
apiVersion: v1
kind: Pod
spec:
# ...
  containers:
    volumeMounts:
    - name: local-disks
      mountPath: /data
  volumes:
  - name: local-disks
    persistentVolumeClaim:
      claimName: local-pvc-name
# ...
```

1. 마운트할 볼륨의 이름입니다.

2. 볼륨이 마운트된 Pod 내부의 경로입니다. 컨테이너 루트, `/` 또는 호스트와 컨테이너에서 동일한 경로에 마운트하지 마십시오. 컨테이너가 호스트 `/dev/pts` 파일과 같이 충분한 권한이 있는 경우 호스트 시스템이 손상될 수 있습니다. `/host` 를 사용하여 호스트를 마운트하는 것이 안전합니다.

3. 사용할 기존 영구 볼륨 클레임의 이름입니다.

방금 생성한 파일을 지정하여 OpenShift Container Platform 클러스터에 리소스를 생성합니다.

```shell-session
$ oc create -f <local-pod>.yaml
```

#### 5.2.6. 로컬 스토리지 장치에 대한 검색 및 프로비저닝 자동화

로컬 스토리지 Operator는 로컬 스토리지 검색 및 프로비저닝을 자동화합니다. 이 기능을 사용하면 배포 중에 연결된 장치가 있는 베어 메탈, VMware 또는 AWS 스토어 인스턴스와 같이 동적 프로비저닝을 사용할 수 없는 경우 설치를 단순화할 수 있습니다.

중요

자동 검색 및 프로비저닝은 기술 프리뷰 기능 전용입니다. Technology Preview 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

중요

자동 검색 및 프로비저닝은 온프레미스 또는 플랫폼 관련 배포와 함께 Red Hat OpenShift Data Foundation을 배포하는 데 사용되는 경우 완전히 지원됩니다.

다음 절차에 따라 로컬 장치를 자동으로 검색하고 선택한 장치에 대한 로컬 볼륨을 자동으로 프로비저닝하십시오.

주의

`LocalVolumeSet` 오브젝트를 주의해서 사용합니다. 로컬 디스크에서 PV(영구 볼륨)를 자동으로 프로비저닝하면 로컬 PV에서 일치하는 모든 장치를 요청할 수 있습니다. `LocalVolumeSet` 오브젝트를 사용하는 경우 Local Storage Operator가 노드에서 로컬 장치를 관리하는 유일한 엔티티인지 확인합니다. 노드를 두 번 이상 대상으로 하는 `LocalVolumeSet` 의 여러 인스턴스를 생성할 수 없습니다.

사전 요구 사항

클러스터 관리자 권한이 있어야 합니다.

Local Storage Operator가 설치되어 있습니다.

OpenShift Container Platform 노드에 로컬 디스크가 연결되어 있습니다.

OpenShift Container Platform 웹 콘솔과 아래 명령줄 인터페이스(CLI)에 액세스할 수 있습니다.

```shell
oc
```

절차

웹 콘솔에서 로컬 장치를 자동으로 검색할 수 있도록 하려면 다음을 수행합니다.

Ecosystem → 설치된 Operators를 클릭합니다.

`openshift-local-storage` 네임스페이스에서 로컬 스토리지를 클릭합니다.

로컬 볼륨 검색 탭을 클릭합니다.

로컬 볼륨 검색 생성 을 클릭한 다음 양식 보기 또는 YAML 보기를 선택합니다.

`LocalVolumeDiscovery` 오브젝트 매개변수를 구성합니다.

생성 을 클릭합니다.

Local Storage Operator는 `auto-discover-devices` 라는 로컬 볼륨 검색 인스턴스를 생성합니다.

노드에 사용 가능한 장치 목록을 표시하려면 다음을 수행합니다.

OpenShift Container Platform 웹 콘솔에 로그인합니다.

컴퓨팅 → 노드 로 이동합니다.

열기를 원하는 노드 이름을 클릭합니다. "노드 세부 정보" 페이지가 표시됩니다.

선택한 장치 목록을 표시하려면 디스크 탭을 선택합니다.

로컬 디스크가 추가되거나 제거되면 장치 목록이 지속적으로 업데이트됩니다. 장치를 이름, 상태, 유형, 모델, 용량 및 모드로 필터링할 수 있습니다.

웹 콘솔에서 발견된 장치에 대한 로컬 볼륨을 자동으로 프로비저닝하려면 다음을 수행합니다.

에코시스템 → 설치된 Operator 로 이동하여 Operator 목록에서 로컬 스토리지를 선택합니다.

로컬 볼륨 세트 → 로컬 볼륨 세트 만들기 를 선택합니다.

볼륨 세트 이름과 스토리지 클래스 이름을 입력합니다.

그에 따라 필터를 적용하려면 모든 노드 또는 노드 선택 을 선택합니다.

참고

모든 노드 또는 노드 선택 을 사용하여 필터링하는지의 여부와 관계없이 작업자 노드만 사용할 수 있습니다.

로컬 볼륨 세트에 적용할 디스크 유형, 모드, 크기 및 제한을 선택하고 만들기 를 클릭합니다.

몇 분 후에 “Operator 조정됨”을 나타내는 메시지가 표시됩니다.

대신 CLI에서 검색된 장치에 대한 로컬 볼륨을 프로비저닝하려면 다음을 수행합니다.

다음 예와 같이 `local-volume-set.yaml` 과 같은 로컬 볼륨 세트를 정의하는 오브젝트 YAML 파일을 생성합니다.

```yaml
apiVersion: local.storage.openshift.io/v1alpha1
kind: LocalVolumeSet
metadata:
  name: example-autodetect
spec:
  nodeSelector:
    nodeSelectorTerms:
      - matchExpressions:
          - key: kubernetes.io/hostname
            operator: In
            values:
              - worker-0
              - worker-1
  storageClassName: local-sc
  volumeMode: Filesystem
  fsType: ext4
  maxDeviceCount: 10
  deviceInclusionSpec:
    deviceTypes:
      - disk
      - part
    deviceMechanicalProperties:
      - NonRotational
    minSize: 10G
    maxSize: 100G
    models:
      - SAMSUNG
      - Crucial_CT525MX3
    vendors:
      - ATA
      - ST2000LM
```

1. 검색된 장치에서 프로비저닝된 영구 볼륨에 대해 생성된 스토리지 클래스를 결정합니다. Local Storage Operator가 존재하지 않는 경우 스토리지 클래스를 자동으로 생성합니다. 이 로컬 볼륨 세트를 고유하게 식별하는 스토리지 클래스를 사용해야 합니다.

2. 로컬 볼륨 세트 기능을 사용할 때 Local Storage Operator는 논리 볼륨 관리(LVM) 장치 사용을 지원하지 않습니다.

로컬 볼륨 세트 오브젝트를 생성합니다.

```shell-session
$ oc apply -f local-volume-set.yaml
```

로컬 영구 볼륨이 스토리지 클래스를 기반으로 동적으로 프로비저닝되었는지 확인합니다.

```shell-session
$ oc get pv
```

```shell-session
NAME                CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS   REASON   AGE
local-pv-1cec77cf   100Gi      RWO            Delete           Available           local-sc                88m
local-pv-2ef7cd2a   100Gi      RWO            Delete           Available           local-sc                82m
local-pv-3fa1c73    100Gi      RWO            Delete           Available           local-sc                48m
```

참고

결과는 노드에서 제거된 후 삭제됩니다. 심볼릭 링크는 수동으로 제거해야 합니다.

#### 5.2.7. Local Storage Operator Pod에서 허용 오차 사용

테인트를 노드에 적용하여 일반 워크로드를 실행하지 못하도록 할 수 있습니다. Local Storage Operator가 테인트된 노드를 사용하도록 허용하려면 `Pod` 또는 `DaemonSet` 정의에 허용 오차를 추가해야 합니다. 그러면 생성된 리소스가 이러한 테인트된 노드에서 실행될 수 있습니다.

`LocalVolume` 리소스를 통해 Local Storage Operator Pod에 허용 오차를 적용하고 노드 사양을 통해 노드에 테인트를 적용합니다. 노드의 테인트는 해당 테인트를 허용하지 않는 모든 Pod를 거절하도록 노드에 지시합니다. 다른 Pod에 없는 특정 테인트를 사용하면 Local Storage Operator Pod가 해당 노드에서도 실행될 수 있습니다.

중요

테인트 및 허용 오차는 key, value 및 effect로 구성되어 있습니다. 인수로는 `key=value:effect` 로 표시됩니다. Operator는 이러한 매개 변수 중 하나를 비워두는 것을 허용합니다.

사전 요구 사항

Local Storage Operator가 설치되어 있습니다.

로컬 디스크는 테인트와 함께 OpenShift Container Platform 노드에 연결되어 있습니다.

테인트된 노드는 로컬 스토리지를 프로비저닝해야 합니다.

절차

테인트된 노드에서 스케줄링을 위해 로컬 볼륨을 구성하려면 다음을 수행하십시오.

다음 예와 같이 `Pod` 를 정의하는 YAML 파일을 수정하고 `LocalVolume` 사양을 추가합니다.

```yaml
apiVersion: "local.storage.openshift.io/v1"
  kind: "LocalVolume"
  metadata:
    name: "local-disks"
    namespace: "openshift-local-storage"
  spec:
    tolerations:
      - key: localstorage
        operator: Equal
        value: "localstorage"
    storageClassDevices:
        - storageClassName: "local-sc"
          volumeMode: Block
          devicePaths:
            - /dev/xvdg
```

1. 노드에 추가한 키를 지정합니다.

2. `키` / `값` 매개변수가 일치할 것을 요구하도록 `Equal` Operator를 지정합니다. Operator가 `Exists` 인 경우 시스템은 키가 존재하는지 확인하고 값을 무시합니다. Operator가 `Equal` 이면 키와 값이 일치해야 합니다.

3. 테인트된 노드의 `로컬` 값을 지정합니다.

4. 볼륨 모드(`파일 시스템` 또는 `블록`)는 로컬 볼륨의 유형을 정의합니다.

5. 선택할 로컬 스토리지 장치 목록이 포함된 경로입니다.

선택 사항: 테인트된 노드에만 로컬 영구 볼륨을 생성하려면 다음 예와 같이 YAML 파일을 수정하고 `LocalVolume` 사양을 추가합니다.

```yaml
spec:
  tolerations:
    - key: node-role.kubernetes.io/master
      operator: Exists
```

정의된 허용 오차가 결과 데몬 세트로 전달되어, 지정된 테인트를 포함하는 노드에 대해 디스크 제조 업체 및 프로비저너 Pod를 생성할 수 있습니다.

#### 5.2.8. Local Storage Operator 지표

OpenShift Container Platform은 Local Storage Operator에 대한 다음 지표를 제공합니다.

`lso_discovery_disk_count`: 각 노드에서 발견된 총 장치 수

`lso_lvset_provisioned_PV_count`: `LocalVolumeSet` 개체에서 생성한 총 PV 수

`lso_lvset_unmatched_disk_count`: 기준 불일치로 인해 Local Storage Operator가 프로비저닝을 위해 선택하지 않은 총 디스크 수

`lso_lvset_orphaned_symlink_count`: `LocalVolumeSet` 개체 기준과 더 이상 일치하지 않는 PV가 있는 장치 수

`lso_lv_orphaned_symlink_count`: `LocalVolume` 오브젝트 기준과 더 이상 일치하지 않는 PV가 있는 장치 수

`lso_lv_provisioned_PV_count`: `LocalVolume` 의 프로비저닝된 총 PV 수

이러한 메트릭을 사용하려면 다음 중 하나를 수행하여 활성화합니다.

웹 콘솔의 소프트웨어 카탈로그에서 Local Storage Operator를 설치할 때 이 네임스페이스에서 Operator 권장 클러스터 모니터링 활성화 확인란을 선택합니다.

다음 명령을 실행하여 Operator 네임스페이스에 `openshift.io/cluster-monitoring=true` 레이블을 수동으로 추가합니다.

```shell-session
$ oc label ns/openshift-local-storage openshift.io/cluster-monitoring=true
```

메트릭에 대한 자세한 내용은 관리자로 메트릭 액세스를 참조하십시오.

#### 5.2.9.1. 로컬 볼륨 또는 로컬 볼륨 세트 제거

경우에 따라 로컬 볼륨(LV) 및 로컬 볼륨 세트(LVS)를 삭제해야 합니다.

사전 요구 사항

PV(영구 볼륨)는 `릴리스` 또는 `사용 가능` 상태여야 합니다.

주의

아직 사용 중인 영구 볼륨을 삭제하면 데이터 손실 또는 손상이 발생할 수 있습니다.

프로세스

LV 또는 LVS를 삭제하려면 다음 단계를 완료합니다.

삭제 중인 LV 또는 LVS가 소유한 바인딩된 PV가 있는 경우 해당 PVC(영구 볼륨 클레임)를 삭제하여 PV를 해제합니다.

특정 LV 또는 LVS가 소유한 바인딩된 PV를 찾으려면 다음 명령을 실행합니다.

```shell-session
$ oc get pv --selector storage.openshift.com/owner-name=<LV_LVS_name>
```

1. `<LV_LVS_name` >은 LV 또는 LVS의 이름입니다.

```shell-session
NAME                CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                 STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
local-pv-3fa1c73    5Gi        RWO            Delete           Available                         slow           <unset>                          28s
local-pv-1cec77cf   30Gi       RWX            Retain           Bound       openshift/storage     my-sc          <unset>                          168d
```

바인딩된 PV의 상태는 `Bound` 이고 해당 PVC는 `CLAIM` 열에 표시됩니다. 이전 예에서 PV `local-pv-1cec77cf` 가 바인딩되고 PVC는 `openshift/storage` 입니다.

다음 명령을 실행하여 LV 또는 LVS가 소유한 바인딩된 PV의 해당 PVC를 삭제합니다.

```shell-session
$ oc delete pvc <name>
```

이 예에서는 PVC `openshift/storage` 를 삭제합니다.

다음 명령을 실행하여 LV 또는 LVS를 삭제합니다.

```shell-session
$ oc delete lv <name>
```

또는

```shell-session
$ oc delete lvs <name>
```

LV 또는 LVS가 소유한 PV에 `Retain` 회수 정책이 있는 경우 중요한 데이터를 백업한 다음 PV를 삭제합니다.

참고

LV 또는 LVS를 `삭제` 하면 삭제 정책이 있는 PV가 자동으로 삭제됩니다.

`Retain` 회수 정책을 사용하여 PV를 찾으려면 다음 명령을 실행합니다.

```shell-session
$ oc get pv
```

```shell-session
NAME                CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                STORAGECLASS   REASON   AGE
local-pv-1cec77cf   30Gi       RWX            Retain           Available                        my-sc                   168d
```

이 예에서 PV `local-pv-1cec77cf` 에는 `Retain` 회수 정책이 있으므로 수동으로 삭제해야 합니다.

이 볼륨의 중요한 데이터를 백업합니다.

다음 명령을 실행하여 PV를 삭제합니다.

```shell-session
$ oc delete pv <name>
```

이 예에서는 PV `local-pv-1cec77cf` 를 삭제합니다.

#### 5.2.9.2. Local Storage Operator 설치 제거

Local Storage Operator의 설치를 제거하려면 `openshift-local-storage` 프로젝트에서 Operator 및 모든 생성된 리소스를 제거해야 합니다.

주의

로컬 스토리지 PV를 아직 사용 중 일 때 Local Storage Operator의 설치를 제거하는 것은 권장되지 않습니다. Operator 제거 후 PV는 유지되지만, PV 및 로컬 스토리지 리소스를 제거하지 않고 Operator를 제거한 후 다시 설치하면 알 수 없는 동작이 발생할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

프로세스

다음 명령을 실행하여 프로젝트에 설치된 로컬 볼륨 리소스(예: `localvolume`, `localvolumeset`, `localvolumediscovery`)를 삭제합니다.

```shell-session
$ oc delete localvolume --all --all-namespaces
```

```shell-session
$ oc delete localvolumeset --all --all-namespaces
```

```shell-session
$ oc delete localvolumediscovery --all --all-namespaces
```

웹 콘솔에서 Local Storage Operator의 설치를 제거합니다.

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Ecosystem → 설치된 Operators 로 이동합니다.

Local Storage 를 필터 상자에 입력하여 Local Storage Operator를 찾습니다.

Local Storage Operator 끝에 있는 옵션 메뉴

를 클릭합니다.

Operator 제거 를 클릭합니다.

표시되는 창에서 제거 를 클릭합니다.

Local Storage Operator에서 생성한 PV는 삭제될 때까지 클러스터에 남아 있습니다. 이러한 볼륨이 더 이상 사용되지 않으면 다음 명령을 실행하여 해당 볼륨을 삭제합니다.

```shell-session
$ oc delete pv <pv-name>
```

다음 명령을 실행하여 `openshift-local-storage` 프로젝트를 삭제합니다.

```shell-session
$ oc delete project openshift-local-storage
```

### 5.3. hostPath를 사용하는 영구 스토리지

OpenShift Container Platform 클러스터의 hostPath 볼륨은 호스트 노드 파일 시스템의 파일 또는 디렉터리를 Pod에 마운트합니다. 대부분의 Pod에는 hostPath 볼륨이 필요하지 않지만 테스트에 필요한 빠른 옵션을 제공합니다.

중요

클러스터 관리자는 권한으로 실행되도록 Pod를 구성해야 합니다. 이를 통해 동일한 노드의 Pod에 액세스 권한이 부여됩니다.

#### 5.3.1. 개요

OpenShift Container Platform은 단일 노드 클러스터에서 개발 및 테스트를 위해 hostPath 마운트를 지원합니다.

프로덕션 클러스터에서는 hostPath를 사용할 수 없습니다. 대신, 클러스터 관리자는 GCE 영구 디스크 볼륨, NFS 공유 또는 Amazon EBS 볼륨과 같은 네트워크 리소스를 프로비저닝합니다. 네트워크 리소스는 스토리지 클래스 사용을 지원하여 동적 프로비저닝을 설정합니다.

hostPath 볼륨은 정적으로 프로비저닝해야 합니다.

중요

컨테이너 루트, `/` 또는 호스트와 컨테이너에서 동일한 경로에 마운트하지 마십시오. 컨테이너에 충분한 권한이 있는 경우 호스트 시스템이 손상될 수 있습니다. `/host` 를 사용하여 호스트를 마운트하는 것이 안전합니다. 다음 예는 `/host` 의 컨테이너에 마운트되는 호스트의 `/` 디렉터리를 보여줍니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-host-mount
spec:
  containers:
  - image: registry.access.redhat.com/ubi9/ubi
    name: test-container
    command: ['sh', '-c', 'sleep 3600']
    volumeMounts:
    - mountPath: /host
      name: host-slash
  volumes:
   - name: host-slash
     hostPath:
       path: /
       type: ''
```

#### 5.3.2. 정적으로 hostPath 볼륨을 프로비저닝

hostPath 볼륨을 사용하는 Pod는 수동(정적) 프로비저닝을 통해 참조해야 합니다.

프로세스

`PersistentVolume` 오브젝트 정의를 사용하여 `pv.yaml` 파일을 생성하여 PV(영구 볼륨)를 정의합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv-volume
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/mnt/data"
```

1. 볼륨의 이름입니다. 이 이름은 볼륨을 PV(영구 볼륨) 클레임 또는 Pod로 식별하는 방법입니다.

2. PVC(영구 볼륨 클레임) 요청을 PV에 바인딩하는 데 사용됩니다.

3. 볼륨은 단일 노드에서 `읽기-쓰기` 로 마운트할 수 있습니다.

4. 구성 파일은 볼륨이 클러스터 노드의 `/mnt/data` 에 있음을 지정합니다. 호스트 시스템이 손상되지 않도록 하려면 컨테이너 루트, `/` 또는 호스트와 컨테이너에서 동일한 경로에 마운트하지 마십시오. `/host` 를 사용하여 안전하게 호스트를 마운트할 수 있습니다.

파일에서 PV를 생성합니다.

```shell-session
$ oc create -f pv.yaml
```

`PersistentVolumeClaim` 오브젝트 정의를 사용하여 `pvc.yaml` 파일을 생성하여 PVC를 정의합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pvc-volume
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: manual
```

파일에서 PVC를 생성합니다.

```shell-session
$ oc create -f pvc.yaml
```

#### 5.3.3. 권한이 있는 Pod에서 hostPath 공유 마운트

영구 볼륨 클레임을 생성한 후 애플리케이션에 의해 내부에서 사용될 수 있습니다. 다음 예시는 Pod 내부에서 이 공유를 마운트하는 방법을 보여줍니다.

사전 요구 사항

기본 hostPath 공유에 매핑된 영구 볼륨 클레임이 있습니다.

절차

기존 영구 볼륨 클레임을 마운트하는 권한이 있는 Pod를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-name
spec:
  containers:
    ...
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /data
      name: hostpath-privileged
  ...
  securityContext: {}
  volumes:
    - name: hostpath-privileged
      persistentVolumeClaim:
        claimName: task-pvc-volume
```

1. Pod의 이름입니다.

2. 노드의 스토리지에 액세스하려면 Pod는 권한 있음으로 실행해야 합니다.

3. 권한이 있는 Pod 내부에서 호스트 경로 공유를 마운트하기 위한 경로입니다. 컨테이너 루트, `/` 또는 호스트와 컨테이너에서 동일한 경로에 마운트하지 마십시오. 컨테이너가 호스트 `/dev/pts` 파일과 같이 충분한 권한이 있는 경우 호스트 시스템이 손상될 수 있습니다. `/host` 를 사용하여 호스트를 마운트하는 것이 안전합니다.

4. 이전에 생성된 `PersistentVolumeClaim` 오브젝트의 이름입니다.

### 5.4. 논리 볼륨 관리자 스토리지를 사용하는 영구 스토리지

논리 볼륨 관리자(LVM) 스토리지는 TopoLVM CSI 드라이버를 통해 LVM2를 사용하여 제한된 리소스가 있는 클러스터에서 로컬 스토리지를 동적으로 프로비저닝합니다.

LVM 스토리지를 사용하여 볼륨 그룹, PVC(영구 볼륨 클레임), 볼륨 스냅샷 및 볼륨 복제를 생성할 수 있습니다.

#### 5.4.1. 논리 볼륨 관리자 스토리지 설치

OpenShift Container Platform 클러스터에 LVM(Logical Volume Manager) 스토리지를 설치하고 워크로드를 위한 스토리지를 동적으로 프로비저닝하도록 구성할 수 있습니다.

OpenShift Container Platform CLI(), OpenShift Container Platform 웹 콘솔 또는 RHACM(Red Hat Advanced Cluster Management)을 사용하여 LVM 스토리지를 설치할 수 있습니다.

```shell
oc
```

주의

다중 노드 클러스터에서 LVM 스토리지를 사용하는 경우 LVM 스토리지는 로컬 스토리지 프로비저닝만 지원합니다. LVM 스토리지는 노드 간에 스토리지 데이터 복제 메커니즘을 지원하지 않습니다. 단일 장애 지점을 방지하려면 활성 또는 수동 복제 메커니즘을 통해 스토리지 데이터 복제를 보장해야 합니다.

#### 5.4.1.1. LVM 스토리지를 설치하기 위한 사전 요구 사항

LVM 스토리지를 설치하기 위한 전제 조건은 다음과 같습니다.

최소 10밀리CPU 및 100MiB의 RAM이 있는지 확인합니다.

모든 관리 클러스터에 스토리지를 프로비저닝하는 데 사용되는 전용 디스크가 있는지 확인합니다. LVM 스토리지는 비어 있고 파일 시스템 서명이 포함되지 않은 디스크만 사용합니다. 디스크가 비어 있고 파일 시스템 서명을 포함하지 않도록 하려면 디스크를 사용하기 전에 초기화하십시오.

이전 LVM 스토리지 설치에서 구성한 스토리지 장치를 재사용할 수 있는 개인 CI 환경에 LVM 스토리지를 설치하기 전에 사용하지 않는 디스크를 지웁니다. LVM 스토리지를 설치하기 전에 디스크를 지우지 않으면 수동 조작 없이 디스크를 재사용할 수 없습니다.

참고

사용 중인 디스크를 초기화할 수 없습니다.

RHACM(Red Hat Advanced Cluster Management)을 사용하여 LVM 스토리지를 설치하려면 OpenShift Container Platform 클러스터에 RHACM을 설치해야 합니다. "RHACM을 사용하여 LVM 스토리지 설치" 섹션을 참조하십시오.

추가 리소스

Red Hat Advanced Cluster Management for Kubernetes: 온라인 연결된 동안 설치

#### 5.4.1.2. CLI를 사용하여 LVM 스토리지 설치

클러스터 관리자는 OpenShift CLI를 사용하여 LVM 스토리지를 설치할 수 있습니다.

참고

LVM Storage Operator의 기본 네임스페이스는 `openshift-lvm-storage` 입니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 및 Operator 설치 권한이 있는 사용자로 OpenShift Container Platform에 로그인했습니다.

프로세스

네임스페이스를 생성하기 위한 구성으로 YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    openshift.io/cluster-monitoring: "true"
    pod-security.kubernetes.io/enforce: privileged
    pod-security.kubernetes.io/audit: privileged
    pod-security.kubernetes.io/warn: privileged
  name: openshift-lvm-storage
```

다음 명령을 실행하여 네임스페이스를 생성합니다.

```shell-session
$ oc create -f <file_name>
```

`OperatorGroup` CR YAML 파일을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: openshift-storage-operatorgroup
  namespace: openshift-lvm-storage
spec:
  targetNamespaces:
  - openshift-storage
```

다음 명령을 실행하여 `OperatorGroup` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>
```

`서브스크립션` CR YAML 파일을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: lvms
  namespace: openshift-lvm-storage
spec:
  installPlanApproval: Automatic
  name: lvms-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

다음 명령을 실행하여 `서브스크립션` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>
```

검증

LVM 스토리지가 설치되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get csv -n openshift-lvm-storage -o custom-columns=Name:.metadata.name,Phase:.status.phase
```

```shell-session
Name                         Phase
4.13.0-202301261535          Succeeded
```

#### 5.4.1.3. 웹 콘솔을 사용하여 LVM 스토리지 설치

OpenShift Container Platform 웹 콘솔을 사용하여 LVM 스토리지를 설치할 수 있습니다.

참고

LVM Storage Operator의 기본 네임스페이스는 `openshift-lvm-storage` 입니다.

사전 요구 사항

클러스터에 액세스할 수 있습니다.

`cluster-admin` 및 Operator 설치 권한을 사용하여 OpenShift Container Platform에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Ecosystem → Software Catalog 를 클릭합니다.

소프트웨어 카탈로그 페이지에서 LVM Storage 를 클릭합니다.

Operator 설치 페이지에서 다음 옵션을 설정합니다.

Channel을 stable-4.20 으로 업데이트합니다.

설치 모드는

클러스터의 특정 네임스페이스 입니다.

설치된 네임스페이스 를 Operator 권장 네임스페이스 openshift-storage. `openshift-lvm-storage` 네임스페이스가 없는 경우 Operator 설치 중에 생성됩니다.

업데이트 승인 을 자동 또는 수동 으로 업데이트합니다.

참고

자동 업데이트를 선택하면 OLM(Operator Lifecycle Manager)이 개입 없이 실행 중인 LVM 스토리지 인스턴스를 자동으로 업데이트합니다.

수동 업데이트를 선택하면 OLM에서 업데이트 요청을 생성합니다. 클러스터 관리자는 LVM 스토리지를 최신 버전으로 업데이트하기 위해 업데이트 요청을 수동으로 승인해야 합니다.

선택 사항: 이 네임스페이스에서 Operator 권장 클러스터 모니터링 활성화 확인란을 선택합니다.

설치 를 클릭합니다.

검증 단계

LVM 스토리지에 성공적인 설치를 나타내는 녹색 눈금이 표시되는지 확인합니다.

#### 5.4.1.4. 연결이 끊긴 환경에 LVM 스토리지 설치

연결이 끊긴 환경의 OpenShift Container Platform에 LVM 스토리지를 설치할 수 있습니다. 이 절차에서 참조하는 모든 섹션은 "추가 리소스" 섹션에 연결되어 있습니다.

사전 요구 사항

"연결 해제된 설치 미러링 정보" 섹션을 읽습니다.

OpenShift Container Platform 이미지 리포지토리에 액세스할 수 있습니다.

미러 레지스트리를 생성하셨습니다.

프로세스

"이미지 세트 구성 생성" 절차의 단계를 따르십시오. LVM 스토리지에 대한 `ImageSetConfiguration` CR(사용자 정의 리소스)을 생성하려면 다음 예제 `ImageSetConfiguration` CR 구성을 사용하면 됩니다.

```yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v1alpha2
archiveSize: 4
storageConfig:
  registry:
    imageURL: example.com/mirror/oc-mirror-metadata
    skipTLS: false
mirror:
  platform:
    channels:
    - name: stable-4.20
      type: ocp
    graph: true
  operators:
  - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
    packages:
    - name: lvms-operator
      channels:
      - name: stable
  additionalImages:
  - name: registry.redhat.io/ubi9/ubi:latest
  helm: {}
```

1. 이미지 세트 내에서 각 파일의 최대 크기(GiB)를 설정합니다.

2. 이미지 세트를 저장할 위치를 지정합니다. 이 위치는 레지스트리 또는 로컬 디렉터리일 수 있습니다. 기술 프리뷰 OCI 기능을 사용하지 않는 한 `storageConfig` 필드를 구성해야 합니다.

3. 레지스트리를 사용할 때 이미지 스트림의 스토리지 URL을 지정합니다. 자세한 내용은 이미지 스트림을 사용하는 이유를 참조하십시오.

4. OpenShift Container Platform 이미지를 검색할 채널을 지정합니다.

5. OSUS(OpenShift Update Service) 그래프 이미지를 생성하려면 이 필드를 `true` 로 설정합니다. 자세한 내용은 OpenShift 업데이트 서비스 정보 를 참조하십시오.

6. OpenShift Container Platform 이미지를 검색할 Operator 카탈로그를 지정합니다.

7. 이미지 세트에 포함할 Operator 패키지를 지정합니다. 이 필드가 비어 있으면 카탈로그의 모든 패키지가 검색됩니다.

8. 이미지 세트에 포함할 Operator 패키지의 채널을 지정합니다. 해당 채널에서 번들을 사용하지 않는 경우에도 Operator 패키지의 기본 채널을 포함해야 합니다. 다음 명령을 실행하여 기본 채널을 찾을 수 있습니다. >.

```shell
$ oc mirror list operators --catalog=<catalog_name> --package=<package_name
```

9. 이미지 세트에 포함할 추가 이미지를 지정합니다.

" 미러 레지스트리로 설정된 이미지 미러링" 섹션의 절차를 따르십시오.

"이미지 레지스트리 저장소 미러링 구성" 섹션의 절차를 따르십시오.

추가 리소스

연결 해제된 설치 미러링 정보

Red Hat OpenShift용 미러 레지스트리를 사용하여 미러 레지스트리 생성

OpenShift Container Platform 이미지 저장소 미러링

이미지 세트 구성 생성

미러 레지스트리로 이미지 세트 미러링

이미지 레지스트리 저장소 미러링 설정

이미지 스트림을 사용하는 이유

#### 5.4.1.5. RHACM을 사용하여 LVM 스토리지 설치

RHACM(Red Hat Advanced Cluster Management)을 사용하여 클러스터에 LVM 스토리지를 설치하려면 `Policy` 사용자 정의 리소스(CR)를 생성해야 합니다. LVM 스토리지를 설치할 클러스터를 선택하도록 기준을 구성할 수도 있습니다.

참고

LVM 스토리지를 설치하기 위해 생성된 `Policy` CR은 `Policy` CR을 생성한 후 가져오거나 생성한 클러스터에도 적용됩니다.

사전 요구 사항

`cluster-admin` 및 Operator 설치 권한이 있는 계정을 사용하여 RHACM 클러스터에 액세스할 수 있습니다.

각 클러스터에서 LVM 스토리지를 사용할 수 있는 전용 디스크가 있습니다.

클러스터는 RHACM에서 관리해야 합니다.

프로세스

OpenShift Container Platform 인증 정보를 사용하여 RHACM CLI에 로그인합니다.

네임스페이스를 생성합니다.

```shell-session
$ oc create ns <namespace>
```

`Policy` CR YAML 파일을 생성합니다.

```yaml
apiVersion: apps.open-cluster-management.io/v1
kind: PlacementRule
metadata:
  name: placement-install-lvms
spec:
  clusterConditions:
  - status: "True"
    type: ManagedClusterConditionAvailable
  clusterSelector:
    matchExpressions:
    - key: mykey
      operator: In
      values:
      - myvalue
---
apiVersion: policy.open-cluster-management.io/v1
kind: PlacementBinding
metadata:
  name: binding-install-lvms
placementRef:
  apiGroup: apps.open-cluster-management.io
  kind: PlacementRule
  name: placement-install-lvms
subjects:
- apiGroup: policy.open-cluster-management.io
  kind: Policy
  name: install-lvms
---
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  annotations:
    policy.open-cluster-management.io/categories: CM Configuration Management
    policy.open-cluster-management.io/controls: CM-2 Baseline Configuration
    policy.open-cluster-management.io/standards: NIST SP 800-53
  name: install-lvms
spec:
  disabled: false
  remediationAction: enforce
  policy-templates:
  - objectDefinition:
      apiVersion: policy.open-cluster-management.io/v1
      kind: ConfigurationPolicy
      metadata:
        name: install-lvms
      spec:
        object-templates:
        - complianceType: musthave
          objectDefinition:
            apiVersion: v1
            kind: Namespace
            metadata:
              labels:
                openshift.io/cluster-monitoring: "true"
                pod-security.kubernetes.io/enforce: privileged
                pod-security.kubernetes.io/audit: privileged
                pod-security.kubernetes.io/warn: privileged
              name: openshift-lvm-storage
        - complianceType: musthave
          objectDefinition:
            apiVersion: operators.coreos.com/v1
            kind: OperatorGroup
            metadata:
              name: openshift-storage-operatorgroup
              namespace: openshift-lvm-storage
            spec:
              targetNamespaces:
              - openshift-lvm-storage
        - complianceType: musthave
          objectDefinition:
            apiVersion: operators.coreos.com/v1alpha1
            kind: Subscription
            metadata:
              name: lvms
              namespace: openshift-lvm-storage
            spec:
              installPlanApproval: Automatic
              name: lvms-operator
              source: redhat-operators
              sourceNamespace: openshift-marketplace
        remediationAction: enforce
        severity: low
```

1. LVM 스토리지를 설치하려는 클러스터에 구성된 라벨과 일치하도록 `PlacementRule.spec.clusterSelector` 의 `key` 필드 및 `values` 필드를 설정합니다.

2. 네임스페이스 구성.

3. `OperatorGroup` CR 구성입니다.

4. `서브스크립션` CR 구성입니다.

다음 명령을 실행하여 `Policy` CR을 생성합니다.

```shell-session
$ oc create -f <file_name> -n <namespace>
```

`Policy` CR을 생성할 때 `PlacementRule` CR에 구성된 선택 기준과 일치하는 클러스터에서 다음 사용자 정의 리소스가 생성됩니다.

`네임스페이스`

`OperatorGroup`

`서브스크립션`

참고

LVM Storage Operator의 기본 네임스페이스는 `openshift-lvm-storage` 입니다.

Red Hat Advanced Cluster Management for Kubernetes: 온라인 연결된 동안 설치

LVMCluster 사용자 정의 리소스 정보

#### 5.4.2. LVMCluster 사용자 정의 리소스 정보

다음 작업을 수행하도록 `LVMCluster` CR을 구성할 수 있습니다.

PVC(영구 볼륨 클레임)를 프로비저닝하는 데 사용할 수 있는 LVM 볼륨 그룹을 생성합니다.

LVM 볼륨 그룹에 추가할 장치 목록을 구성합니다.

LVM 볼륨 그룹을 생성할 노드와 볼륨 그룹에 대한 thin 풀 구성을 선택하도록 요구 사항을 구성합니다.

선택한 장치를 강제로 지웁니다.

LVM 스토리지를 설치한 후 `LVMCluster` CR(사용자 정의 리소스)을 생성해야 합니다.

```yaml
apiVersion: lvm.topolvm.io/v1alpha1
kind: LVMCluster
metadata:
  name: my-lvmcluster
spec:
  tolerations:
  - effect: NoSchedule
    key: xyz
    operator: Equal
    value: "true"
  storage:
    deviceClasses:
    - name: vg1
      fstype: ext4
      default: true
      nodeSelector:
        nodeSelectorTerms:
        - matchExpressions:
          - key: mykey
            operator: In
            values:
            - ssd
      deviceSelector:
        paths:
        - /dev/disk/by-path/pci-0000:87:00.0-nvme-1
        - /dev/disk/by-path/pci-0000:88:00.0-nvme-1
        optionalPaths:
        - /dev/disk/by-path/pci-0000:89:00.0-nvme-1
        - /dev/disk/by-path/pci-0000:90:00.0-nvme-1
        forceWipeDevicesAndDestroyAllData: true
      thinPoolConfig:
        name: thin-pool-1
        sizePercent: 90
        overprovisionRatio: 10
        chunkSize: 128Ki
        chunkSizeCalculationPolicy: Static
        metadataSize: 1Gi
        metadataSizeCalculationPolicy: Host
```

1. 2

3. 4

5. 6

7. 8

선택적 필드

#### 5.4.2.1. LVMCluster CR의 필드에 대한 설명

`LVMCluster` CR 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `spec.storage.deviceClasses` | `array` | 로컬 스토리지 장치를 LVM 볼륨 그룹에 할당하는 구성이 포함되어 있습니다. LVM Storage는 사용자가 생성하는 각 장치 클래스에 대한 스토리지 클래스 및 볼륨 스냅샷 클래스를 생성합니다. |
| `deviceClasses.name` | `string` | LVM 볼륨 그룹(VG)의 이름을 지정합니다. 이전 설치에서 생성한 볼륨 그룹을 재사용하도록 이 필드를 구성할 수도 있습니다. 자세한 내용은 "이전 LVM 스토리지 설치에서 볼륨 그룹 재사용"을 참조하십시오. |
| `deviceClasses.fstype` | `string` | 이 필드를 `ext4` 또는 `xfs` 로 설정합니다. 기본적으로 이 필드는 `xfs` 로 설정됩니다. |
| `deviceClasses.default` | `boolean` | 장치 클래스가 기본값임을 나타내려면 이 필드를 `true` 로 설정합니다. 그렇지 않으면 `false` 로 설정할 수 있습니다. 단일 기본 장치 클래스만 구성할 수 있습니다. |
| `deviceClasses.nodeSelector` | `object` | LVM 볼륨 그룹을 만들 노드를 선택하는 구성이 포함되어 있습니다. 이 필드가 비어 있으면 스케줄 테인트가 없는 모든 노드가 고려됩니다. control-plane 노드에서 LVM Storage는 클러스터에서 새 노드가 활성화될 때 추가 작업자 노드를 감지하고 사용합니다. |
| `nodeSelector.nodeSelectorTerms` | `array` | 노드를 선택하는 데 사용되는 요구 사항을 구성합니다. |
| `deviceClasses.deviceSelector` | `object` | 다음 작업을 수행할 구성이 포함되어 있습니다. LVM 볼륨 그룹에 추가할 장치의 경로를 지정합니다. LVM 볼륨 그룹에 추가된 장치를 강제로 지웁니다. 자세한 내용은 "볼륨 그룹에 장치 추가 정보"를 참조하십시오. |
| `deviceSelector.paths` | `array` | 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM Storage에서 장치가 지원되지 않는 경우 `LVMCluster` CR은 `Failed` 상태로 이동합니다. |
| `deviceSelector.optionalPaths` | `array` | 선택적 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM 스토리지에서 장치가 지원되지 않는 경우 LVM 스토리지는 오류가 발생하지 않고 장치를 무시합니다. |
| `deviceSelector. forceWipeDevicesAndDestroyAllData` | `boolean` | LVM 스토리지는 비어 있고 파일 시스템 서명이 포함되지 않은 디스크만 사용합니다. 디스크가 비어 있고 파일 시스템 서명을 포함하지 않도록 하려면 디스크를 사용하기 전에 초기화하십시오. 선택한 장치를 강제로 지우려면 이 필드를 `true` 로 설정합니다. 기본적으로 이 필드는 `false` 로 설정됩니다. 주의 이 필드가 `true` 로 설정되면 LVM 스토리지가 장치의 이전 데이터를 모두 지웁니다. 이 기능을 주의해서 사용하십시오. 장치를 제거하면 다음 조건이 충족되는 경우 데이터 무결성의 불일치가 발생할 수 있습니다. 장치가 스왑 공간으로 사용되고 있습니다. 장치는 RAID 배열의 일부입니다. 장치가 마운트됩니다. 이러한 조건 중 하나라도 true인 경우 디스크를 강제로 지우지 마십시오. 대신 디스크를 수동으로 초기화해야 합니다. |
| `deviceClasses.thinPoolConfig` | `object` | LVM 볼륨 그룹에 씬 풀을 만드는 구성이 포함되어 있습니다. 이 필드를 제외하면 논리 볼륨이 씩 프로비저닝됩니다. 씩 프로비저닝된 스토리지 사용에는 다음과 같은 제한 사항이 포함됩니다. 볼륨 복제에 대한 COW(Copy-On-Write) 지원이 없습니다. 스냅샷 클래스를 지원하지 않습니다. 과도한 프로비저닝을 지원하지 않습니다. 결과적으로 PVC( `PersistentVolumeClaims` )의 프로비저닝된 용량이 볼륨 그룹에서 즉시 줄어듭니다. thin 메트릭을 지원하지 않습니다. 씩 프로비저닝된 장치는 볼륨 그룹 지표만 지원합니다. |
| `thinPoolConfig.name` | `string` | thin 풀의 이름을 지정합니다. |
| `thinPoolConfig.sizePercent` | `integer` | thin 풀을 생성하기 위한 LVM 볼륨 그룹의 공간 백분율을 지정합니다. 기본적으로 이 필드는 90으로 설정됩니다. 설정할 수 있는 최소값은 10이며 최대값은 90입니다. |
| `thinPoolConfig.overprovisionRatio` | `integer` | 씬 풀에서 사용 가능한 스토리지를 기반으로 추가 스토리지를 프로비저닝할 수 있는 인수를 지정합니다. 예를 들어 이 필드가 10으로 설정된 경우 thin 풀에서 사용 가능한 스토리지 양을 최대 10배까지 프로비저닝할 수 있습니다. LVM 클러스터를 생성한 후 이 필드를 수정할 수 있습니다. 매개변수를 업데이트하려면 다음 작업을 수행합니다. LVM 클러스터를 편집하려면 다음 명령을 실행합니다. [CODE language="plaintext" wrap_hint="true" overflow_hint="toggle"] $ oc edit lvmcluster <lvmcluster_name> [/CODE] 패치를 적용하려면 다음 명령을 실행합니다. [CODE language="plaintext" wrap_hint="true" overflow_hint="toggle"] $ oc patch lvmcluster <lvmcluster_name> -p <patch_file.yaml> [/CODE] 오버 프로비저닝을 비활성화하려면 이 필드를 1로 설정합니다. |
| `thinPoolConfig.chunkSize` | `integer` | thin 풀에 대해 정적으로 계산된 청크 크기를 지정합니다. 이 필드는 `ChunkSizeCalculationPolicy` 필드가 `정적` 으로 설정된 경우에만 사용됩니다. 이 필드의 값은 `lvm2` 의 기본 제한 사항으로 인해 64KiB에서 1GiB 범위로 구성해야 합니다. 이 필드를 구성하지 않고 `ChunkSizeCalculationPolicy` 필드가 `Static` 으로 설정된 경우 기본 청크 크기는 128 KiB로 설정됩니다. 자세한 내용은 "Carge size 개요"를 참조하십시오. |
| `thinPoolConfig.chunkSizeCalculationPolicy` | `string` | 기본 볼륨 그룹의 청크 크기를 계산하는 정책을 지정합니다. 이 필드를 `정적` 또는 호스트로 설정할 수 `있습니다` . 기본적으로 이 필드는 `정적` 으로 설정됩니다. 이 필드가 `정적` 으로 설정된 경우 청크 크기는 `chunkSize` 필드 값으로 설정됩니다. `chunkSize` 필드가 구성되지 않은 경우 청크 크기는 128 KiB로 설정됩니다. 이 필드가 `Host` 로 설정되면 `lvm.conf` 파일의 구성에 따라 청크 크기가 계산됩니다. 자세한 내용은 "LVM Storage에서 사용되는 장치의 크기를 설정하기 위한 제한"을 참조하십시오. |
| `thinPoolConfig.metadataSize` | `integer` | thin 풀의 메타데이터 크기를 지정합니다. `MetadataSizeCalculationPolicy` 필드가 정적으로 설정된 경우에만 이 필드를 구성할 수 `있습니다` . 이 필드가 구성되지 않고 `MetadataSizeCalculationPolicy` 필드가 `정적` 으로 설정된 경우 기본 메타데이터 크기는 1GiB로 설정됩니다. 이 필드의 값은 `lvm2` 의 기본 제한 사항으로 인해 2MiB에서 16GiB 범위로 구성해야 합니다. 업데이트 중에 이 필드의 값을 늘릴 수 있습니다. |
| `thinPoolConfig.metadataSizeCalculationPolicy` | `string` | 기본 볼륨 그룹의 메타데이터 크기를 계산하는 정책을 지정합니다. 이 필드를 `정적` 또는 호스트로 설정할 수 `있습니다` . 기본적으로 이 필드는 호스트로 `설정됩니다` . 이 필드가 `Static` 으로 설정된 경우 `thinPoolConfig.metadataSize` 필드의 값에 따라 메타데이터 크기가 계산됩니다. 이 필드가 `Host` 로 설정된 경우 `lvm2` 설정을 기반으로 메타데이터 크기가 계산됩니다. |

추가 리소스

청크 크기 개요

LVM 스토리지에 사용되는 장치의 크기를 구성하는 제한 사항

이전 LVM 스토리지 설치에서 볼륨 그룹 재사용

볼륨 그룹에 장치 추가 정보

단일 노드 OpenShift 클러스터에 작업자 노드 추가

#### 5.4.2.2. LVM 스토리지에 사용되는 장치의 크기를 구성하는 제한 사항

LVM 스토리지를 사용하여 스토리지를 프로비저닝하는 데 사용할 수 있는 장치의 크기를 구성하는 제한 사항은 다음과 같습니다.

프로비저닝할 수 있는 총 스토리지 크기는 기본 LVM(Logical Volume Manager) 씬 풀의 크기와 초과 프로비저닝 요인으로 제한됩니다.

논리 볼륨의 크기는 물리 확장 영역(PE) 및 논리 확장 영역(LE)의 크기에 따라 다릅니다.

물리 및 논리 장치 생성 중에 PE 및 LE의 크기를 정의할 수 있습니다.

기본 PE 및 LE 크기는 4MB입니다.

PE의 크기가 증가하면 LVM의 최대 크기는 커널 제한과 디스크 공간에 따라 결정됩니다.

다음 표에서는 정적 및 호스트 구성에 대한 청크 크기 및 볼륨 크기 제한을 설명합니다.

| 매개변수 | 현재의 |
| --- | --- |
| 청크 크기 | 128KiB |
| 최대 볼륨 크기 | 32TiB |

| 매개변수 | 최소 값 | 최대값 |
| --- | --- | --- |
| 청크 크기 | 64KiB | 1GiB |
| 볼륨 크기 | 기본 RHCOS(Red Hat Enterprise Linux CoreOS) 시스템의 최소 크기입니다. | 기본 RHCOS 시스템의 최대 크기입니다. |

| 매개변수 | 현재의 |
| --- | --- |
| 청크 크기 | 이 값은 `lvm.conf` 파일의 구성을 기반으로 합니다. 기본적으로 이 값은 128KiB로 설정됩니다. |
| 최대 볼륨 크기 | 기본 RHCOS 시스템의 최대 볼륨 크기와 동일합니다. |
| 최소 볼륨 크기 | 기본 RHCOS 시스템의 최소 볼륨 크기와 동일합니다. |

#### 5.4.2.3. 볼륨 그룹에 장치 추가 정보

`LVMCluster` CR의 `deviceSelector` 필드에는 LVM(Logical Volume Manager) 볼륨 그룹에 추가할 장치의 경로를 지정하는 구성이 포함되어 있습니다.

`deviceSelector.paths` 필드, `deviceSelector.optionalPaths` 필드 또는 둘 다에서 장치 경로를 지정할 수 있습니다. `deviceSelector.paths` 필드와 `deviceSelector.optionalPaths` 필드 모두에서 장치 경로를 지정하지 않으면 LVM 스토리지에서 지원되는 사용되지 않는 장치를 볼륨 그룹(VG)에 추가합니다.

주의

RHCOS 내에서 재부팅 시 이러한 이름이 변경될 수 있으므로 `/dev/sdX` 와 같은 심볼릭 이름을 사용하여 디스크를 참조하는 것을 방지하는 것이 좋습니다. 대신 일관된 디스크 식별을 위해 `/dev/disk/by-path/` 또는 `/dev/disk/by-id/` 와 같은 안정적인 이름 지정 체계를 사용해야 합니다.

이 변경으로 모니터링에서 각 노드의 설치 장치에 대한 정보를 수집하는 경우 기존 자동화 워크플로를 조정해야 할 수 있습니다.

자세한 내용은 RHEL 설명서 를 참조하십시오.

`deviceSelector` 필드의 RAID(Redundant Array of Independent Disks) 배열의 경로를 추가하여 RAID 배열을 LVM 스토리지와 통합할 수 있습니다. `mdadm` 유틸리티를 사용하여 RAID 배열을 생성할 수 있습니다. LVM 스토리지는 소프트웨어 RAID 생성을 지원하지 않습니다.

참고

OpenShift Container Platform 설치 중에만 RAID 배열을 생성할 수 있습니다. RAID 배열 생성에 대한 자세한 내용은 다음 섹션을 참조하십시오.

"추가 리소스"에서 " RAID 사용 데이터 볼륨 구성".

설치된 시스템에서 소프트웨어 RAID 생성

RAID에서 실패한 디스크 교체

RAID 디스크 복구

암호화된 장치를 볼륨 그룹에 추가할 수도 있습니다. OpenShift Container Platform을 설치하는 동안 클러스터 노드에서 디스크 암호화를 활성화할 수 있습니다. 장치를 암호화한 후 `deviceSelector` 필드에서 LUKS 암호화된 장치의 경로를 지정할 수 있습니다. 디스크 암호화에 대한 자세한 내용은 "디스크 암호화 정보" 및 "디스크 암호화 및 미러링 구성"을 참조하십시오.

VG에 추가할 장치는 LVM 스토리지에서 지원해야 합니다. 지원되지 않는 장치에 대한 자세한 내용은 "LVM Storage에서 지원되지 않는 장치"를 참조하십시오.

LVM 스토리지는 다음 조건이 충족되는 경우에만 VG에 장치를 추가합니다.

장치 경로가 있습니다.

장치는 LVM 스토리지에서 지원합니다.

중요

장치를 VG에 추가한 후에는 장치를 제거할 수 없습니다.

LVM 스토리지는 동적 장치 검색을 지원합니다. `LVMCluster` CR에 `deviceSelector` 필드를 추가하지 않으면 장치를 사용할 수 있을 때 LVM 스토리지에서 새 장치를 VG에 자동으로 추가합니다.

주의

다음과 같은 이유로 동적 장치 검색을 통해 VG에 장치를 추가하지 않는 것이 좋습니다.

VG에 추가하려는 새 장치를 추가하면 LVM 스토리지에서 동적 장치 검색을 통해 이 장치를 VG에 자동으로 추가합니다.

LVM 스토리지가 동적 장치 검색을 통해 VG에 장치를 추가하는 경우 LVM 스토리지가 노드에서 장치를 제거하는 것을 제한하지 않습니다. VG에 이미 추가된 장치를 제거하거나 업데이트하면 VG가 중단될 수 있습니다. 이로 인해 데이터가 손실되고 수동 노드 수정이 필요할 수 있습니다.

추가 리소스

RAID 지원 데이터 볼륨 구성

디스크 암호화 정보

디스크 암호화 및 미러링 구성

LVM 스토리지에서 지원되지 않는 장치

#### 5.4.2.4. LVM 스토리지에서 지원되지 않는 장치

`LVMCluster` CR(사용자 정의 리소스)의 `deviceSelector` 필드에 장치 경로를 추가하는 경우 LVM Storage에서 장치를 지원하는지 확인합니다. 지원되지 않는 장치에 경로를 추가하는 경우 LVM Storage는 논리 볼륨 관리의 복잡성을 방지하기 위해 장치를 제외합니다.

`deviceSelector` 필드에 장치 경로를 지정하지 않으면 LVM 스토리지에서 지원하는 사용되지 않는 장치만 추가합니다.

참고

장치에 대한 정보를 얻으려면 다음 명령을 실행합니다.

```shell-session
$ lsblk --paths --json -o \
NAME,ROTA,TYPE,SIZE,MODEL,VENDOR,RO,STATE,KNAME,SERIAL,PARTLABEL,FSTYPE
```

LVM 스토리지는 다음 장치를 지원하지 않습니다.

읽기 전용 장치

`ro` 매개변수가 `true` 로 설정된 장치

일시 중지된 장치

`state` 매개 변수가 `suspended` 로 설정된 장치.

Romb 장치

`type` 매개변수가 `rom` 으로 설정된 장치.

LVM 파티션 장치

`type` 매개 변수가 `lvm` 으로 설정된 장치.

잘못된 파티션 레이블이 있는 장치

`partlabel` 매개변수가 `bios` 로 설정된 장치, `부팅` 또는 `reserved`.

잘못된 파일 시스템이 있는 장치

`fstype` 매개 변수가 `null` 또는 `LVM2_member` 이외의 값으로 설정된 장치입니다.

중요

LVM 스토리지는 장치에 하위 장치가 없는 경우에만 `fstype` 매개 변수가 `LVM2_member` 로 설정된 장치를 지원합니다.

다른 볼륨 그룹에 속하는 장치

장치의 볼륨 그룹에 대한 정보를 가져오려면 다음 명령을 실행합니다.

```shell-session
$ pvs <device-name>
```

1. &lt `;device-name&gt`;을 장치 이름으로 바꿉니다.

바인딩 마운트가 있는 장치

장치의 마운트 지점을 가져오려면 다음 명령을 실행합니다.

```shell-session
$ cat /proc/1/mountinfo | grep <device-name>
```

1. &lt `;device-name&gt`;을 장치 이름으로 바꿉니다.

하위 장치가 포함된 장치 참고

예기치 않은 동작을 방지하기 위해 LVM 스토리지에서 장치를 사용하기 전에 장치를 초기화하는 것이 좋습니다.

#### 5.4.3. LVMCluster 사용자 정의 리소스를 생성하는 방법

OpenShift CLI() 또는 OpenShift Container Platform 웹 콘솔을 사용하여 `LVMCluster` CR(사용자 정의 리소스)을 생성할 수 있습니다. RHACM(Red Hat Advanced Cluster Management)을 사용하여 LVM Storage를 설치한 경우 RHACM을 사용하여 `LVMCluster` CR을 생성할 수도 있습니다.

```shell
oc
```

중요

기본적으로 `openshift-storage` 인 LVM Storage Operator를 설치한 동일한 네임스페이스에 `LVMCluster` CR을 생성해야 합니다.

`LVMCluster` CR을 생성할 때 LVM 스토리지에서 다음 시스템 관리 CR을 생성합니다.

각 장치 클래스에 대한 `storageClass` 및 `volumeSnapshotClass` 입니다.

참고

LVM 스토리지는 구성합니다. 여기서 < `device_class_name` >은 `LVMCluster` CR의 `deviceClasses.name` 필드의 값입니다. 예를 들어 `deviceClasses.name` 필드가 Cryostat1로 설정된 경우 스토리지 클래스의 이름과 볼륨 스냅샷 클래스가 `lvms-vg1` 입니다.

```shell
lvms-<device_class_name> 형식으로 스토리지 클래스 및 볼륨 스냅샷 클래스의 이름을
```

`LVMVolumeGroup`: 이 CR은 LVM 볼륨 그룹에서 지원하는 특정 유형의 PV(영구 볼륨)입니다. 여러 노드에서 개별 볼륨 그룹을 추적합니다.

`LVMVolumeGroupNodeStatus`: 이 CR은 노드에서 볼륨 그룹의 상태를 추적합니다.

#### 5.4.3.1. 이전 LVM 스토리지 설치에서 볼륨 그룹 재사용

새 VG를 만드는 대신 이전 LVM 스토리지 설치의 기존 볼륨 그룹(VG)을 재사용할 수 있습니다.

VG만 재사용할 수 있지만 VG와 연결된 논리 볼륨은 재사용할 수 없습니다.

중요

`LVMCluster` CR(사용자 정의 리소스)을 생성하는 경우에만 이 절차를 수행할 수 있습니다.

사전 요구 사항

재사용할 VG가 손상되지 않아야 합니다.

재사용할 VG에 `lvms` 태그가 있어야 합니다. LVM 개체에 태그를 추가하는 방법에 대한 자세한 내용은 태그가 있는 LVM 개체 그룹화를 참조하십시오.

프로세스

`LVMCluster` CR YAML 파일을 엽니다.

다음 예에 설명된 대로 `LVMCluster` CR 매개변수를 구성합니다.

```yaml
apiVersion: lvm.topolvm.io/v1alpha1
kind: LVMCluster
metadata:
  name: my-lvmcluster
spec:
# ...
  storage:
    deviceClasses:
    - name: vg1
      fstype: ext4
      default: true
      deviceSelector:
# ...
        forceWipeDevicesAndDestroyAllData: false
      thinPoolConfig:
# ...
      nodeSelector:
# ...
```

1. 이 필드를 이전 LVM 스토리지 설치의 VG 이름으로 설정합니다.

2. 이 필드를 `ext4` 또는 `xfs` 로 설정합니다. 기본적으로 이 필드는 `xfs` 로 설정됩니다.

3. `deviceSelector` 필드에 새 장치 경로를 지정하여 재사용할 VG에 새 장치를 추가할 수 있습니다. 새 장치를 VG에 추가하지 않으려면 현재 LVM 스토리지 설치의 `deviceSelector` 구성이 이전 LVM Storage 설치와 동일한지 확인합니다.

4. 이 필드가 `true` 로 설정되면 LVM 스토리지가 VG에 추가되는 장치의 모든 데이터를 지웁니다.

5. 재사용할 VG의 `thinPoolConfig` 구성을 유지하려면 현재 LVM 스토리지 설치의 `thinPoolConfig` 구성이 이전 LVM 스토리지 설치와 동일한지 확인하십시오. 또는 필요에 따라 `thinPoolConfig` 필드를 구성할 수 있습니다.

6. LVM 볼륨 그룹을 생성할 노드를 선택하도록 요구 사항을 구성합니다. 이 필드가 비어 있으면 스케줄 테인트가 없는 모든 노드가 고려됩니다.

`LVMCluster` CR YAML 파일을 저장합니다.

참고

볼륨 그룹에 속하는 장치를 보려면 다음 명령을 실행합니다.

```shell-session
$ pvs -S vgname=<vg_name>
```

1. & `lt;vg_name` >을 볼륨 그룹의 이름으로 바꿉니다.

#### 5.4.3.2. CLI를 사용하여 LVMCluster CR 생성

OpenShift CLI()를 사용하여 작업자 노드에 `LVMCluster` CR(사용자 정의 리소스)을 생성할 수 있습니다.

```shell
oc
```

중요

OpenShift Container Platform 클러스터에서 `LVMCluster` CR(사용자 정의 리소스)의 단일 인스턴스만 생성할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 로그인했습니다.

LVM 스토리지를 설치했습니다.

클러스터에 작업자 노드가 설치되어 있습니다.

"LVMCluster 사용자 정의 리소스 정보" 섹션을 읽습니다.

프로세스

`LVMCluster` CR(사용자 정의 리소스) YAML 파일을 생성합니다.

```yaml
apiVersion: lvm.topolvm.io/v1alpha1
kind: LVMCluster
metadata:
  name: my-lvmcluster
  namespace: openshift-lvm-storage
spec:
# ...
  storage:
    deviceClasses:
# ...
      nodeSelector:
# ...
      deviceSelector:
# ...
      thinPoolConfig:
# ...
```

1. 로컬 스토리지 장치를 LVM 볼륨 그룹에 할당하는 구성이 포함되어 있습니다.

2. LVM 볼륨 그룹을 만들 노드를 선택하는 구성이 포함되어 있습니다. 이 필드가 비어 있으면 스케줄 테인트가 없는 모든 노드가 고려됩니다.

3. LVM 볼륨 그룹에 추가할 장치의 경로를 지정하고 LVM 볼륨 그룹에 추가된 장치를 강제로 지우는 구성이 포함되어 있습니다.

4. LVM 볼륨 그룹에 씬 풀을 만드는 구성이 포함되어 있습니다. 이 필드를 제외하면 논리 볼륨이 씩 프로비저닝됩니다.

다음 명령을 실행하여 `LVMCluster` CR을 생성합니다.

```shell-session
$ oc create -f <file_name>
```

```shell-session
lvmcluster/lvmcluster created
```

검증

`LVMCluster` CR이 `Ready` 상태인지 확인합니다.

```shell-session
$ oc get lvmclusters.lvm.topolvm.io -o jsonpath='{.items[*].status}' -n <namespace>
```

```plaintext
{"deviceClassStatuses":
[
  {
    "name": "vg1",
    "nodeStatus": [
        {
            "devices": [
                "/dev/nvme0n1",
                "/dev/nvme1n1",
                "/dev/nvme2n1"
            ],
            "node": "kube-node",
            "status": "Ready"
        }
    ]
  }
]
"state":"Ready"}
```

1. 장치 클래스의 상태입니다.

2. 각 노드의 LVM 볼륨 그룹의 상태입니다.

3. LVM 볼륨 그룹을 만드는 데 사용되는 장치 목록입니다.

4. 장치 클래스가 생성되는 노드입니다.

5. 노드의 LVM 볼륨 그룹의 상태입니다.

6. `LVMCluster` CR의 상태.

참고

`LVMCluster` CR이 `Failed` 상태인 경우 `status` 필드에서 실패 이유를 볼 수 있습니다.

```yaml
status:
  deviceClassStatuses:
    - name: vg1
      nodeStatus:
        - node: my-node-1.example.com
          reason: no available devices found for volume group
          status: Failed
  state: Failed
```

선택 사항: 각 장치 클래스에 대해 LVM 스토리지에서 생성한 스토리지 클래스를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get storageclass
```

```shell-session
NAME          PROVISIONER          RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
lvms-vg1      topolvm.io           Delete          WaitForFirstConsumer   true                   31m
```

선택 사항: 각 장치 클래스에 대해 LVM 스토리지에서 생성한 볼륨 스냅샷 클래스를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get volumesnapshotclass
```

```shell-session
NAME          DRIVER               DELETIONPOLICY   AGE
lvms-vg1      topolvm.io           Delete           24h
```

추가 리소스

LVMCluster 사용자 정의 리소스 정보

#### 5.4.3.3. 웹 콘솔을 사용하여 LVMCluster CR 생성

OpenShift Container Platform 웹 콘솔을 사용하여 작업자 노드에 `LVMCluster` CR을 생성할 수 있습니다.

중요

OpenShift Container Platform 클러스터에서 `LVMCluster` CR(사용자 정의 리소스)의 단일 인스턴스만 생성할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 OpenShift Container Platform 클러스터에 액세스할 수 있습니다.

LVM 스토리지를 설치했습니다.

클러스터에 작업자 노드가 설치되어 있습니다.

"LVMCluster 사용자 정의 리소스 정보" 섹션을 읽습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Ecosystem → 설치된 Operators를 클릭합니다.

`openshift-lvm-storage` 네임스페이스에서 LVM Storage 를 클릭합니다.

LVMCluster 생성 을 클릭하고 양식 보기 또는 YAML 보기를 선택합니다.

필요한 `LVMCluster` CR 매개변수를 구성합니다.

Create 를 클릭합니다.

선택 사항: `LVMCLuster` CR을 편집하려면 다음 작업을 수행합니다.

LVMCluster 탭을 클릭합니다.

Actions 메뉴에서 Edit LVMCluster 를 선택합니다.

YAML 을 클릭하고 필요한 `LVMCLuster` CR 매개변수를 편집합니다.

저장 을 클릭합니다.

검증

LVMCLuster 페이지에서 `LVMCluster` CR이 `Ready` 상태인지 확인합니다.

선택 사항: 각 장치 클래스에 대해 LVM Storage에서 생성한 사용 가능한 스토리지 클래스를 보려면 스토리지 → StorageClasses 를 클릭합니다.

선택 사항: 각 장치 클래스에 대해 LVM Storage에서 생성한 사용 가능한 볼륨 스냅샷 클래스를 보려면 스토리지 → VolumeSnapshotClasses 를 클릭합니다.

추가 리소스

LVMCluster 사용자 정의 리소스 정보

#### 5.4.3.4. RHACM을 사용하여 LVMCluster CR 생성

RHACM을 사용하여 LVM 스토리지를 설치한 후 `LVMCluster` CR(사용자 정의 리소스)을 생성해야 합니다.

사전 요구 사항

RHACM을 사용하여 LVM 스토리지를 설치했습니다.

`cluster-admin` 권한이 있는 계정을 사용하여 RHACM 클러스터에 액세스할 수 있습니다.

"LVMCluster 사용자 정의 리소스 정보" 섹션을 읽습니다.

프로세스

OpenShift Container Platform 인증 정보를 사용하여 RHACM CLI에 로그인합니다.

`LVMCluster` CR을 생성하려면 구성으로 `ConfigurationPolicy` CR YAML 파일을 생성합니다.

```yaml
apiVersion: policy.open-cluster-management.io/v1
kind: ConfigurationPolicy
metadata:
  name: lvms
  namespace: openshift-lvm-storage
spec:
  object-templates:
  - complianceType: musthave
    objectDefinition:
      apiVersion: lvm.topolvm.io/v1alpha1
      kind: LVMCluster
      metadata:
        name: my-lvmcluster
        namespace: openshift-lvm-storage
      spec:
        storage:
          deviceClasses:
# ...
            deviceSelector:
# ...
            thinPoolConfig:
# ...
            nodeSelector:
# ...
  remediationAction: enforce
  severity: low
```

1. 로컬 스토리지 장치를 LVM 볼륨 그룹에 할당하는 구성이 포함되어 있습니다.

2. LVM 볼륨 그룹에 추가할 장치의 경로를 지정하고 LVM 볼륨 그룹에 추가된 장치를 강제로 지우는 구성이 포함되어 있습니다.

3. LVM 볼륨 그룹에 씬 풀을 만드는 구성이 포함되어 있습니다. 이 필드를 제외하면 논리 볼륨이 씩 프로비저닝됩니다.

4. LVM 볼륨 그룹을 만들 노드를 선택하는 구성이 포함되어 있습니다. 이 필드가 비어 있으면 스케줄 테인트가 없는 모든 노드가 고려됩니다.

다음 명령을 실행하여 `ConfigurationPolicy` CR을 생성합니다.

```shell-session
$ oc create -f <file_name> -n <cluster_namespace>
```

1. LVM 스토리지가 설치된 OpenShift Container Platform 클러스터의 네임스페이스입니다.

추가 리소스

Red Hat Advanced Cluster Management for Kubernetes: 온라인 연결된 동안 설치

LVMCluster 사용자 정의 리소스 정보

#### 5.4.4. LVMCluster 사용자 정의 리소스를 삭제하는 방법

OpenShift CLI() 또는 OpenShift Container Platform 웹 콘솔을 사용하여 `LVMCluster` CR(사용자 정의 리소스)을 삭제할 수 있습니다. RHACM(Red Hat Advanced Cluster Management)을 사용하여 LVM Storage를 설치한 경우 RHACM을 사용하여 `LVMCluster` CR을 삭제할 수도 있습니다.

```shell
oc
```

`LVMCluster` CR을 삭제하면 LVM 스토리지에서 다음 CR을 삭제합니다.

`storageClass`

`volumeSnapshotClass`

`LVMVolumeGroup`

`LVMVolumeGroupNodeStatus`

#### 5.4.4.1. CLI를 사용하여 LVMCluster CR 삭제

OpenShift CLI()를 사용하여 `LVMCluster` CR(사용자 정의 리소스)을 삭제할 수 있습니다.

```shell
oc
```

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

LVM 스토리지에서 프로비저닝한 PVC(영구 볼륨 클레임), 볼륨 스냅샷 및 볼륨 복제를 삭제했습니다. 이러한 리소스를 사용하는 애플리케이션도 삭제했습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 실행하여 `LVMCluster` CR을 삭제합니다.

```shell-session
$ oc delete lvmcluster <lvm_cluster_name> -n <namespace>
```

검증

`LVMCluster` CR이 삭제되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get lvmcluster -n <namespace>
```

```shell-session
No resources found in openshift-lvm-storage namespace.
```

#### 5.4.4.2. 웹 콘솔을 사용하여 LVMCluster CR 삭제

OpenShift Container Platform 웹 콘솔을 사용하여 `LVMCluster` CR(사용자 정의 리소스)을 삭제할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

LVM 스토리지에서 프로비저닝한 PVC(영구 볼륨 클레임), 볼륨 스냅샷 및 볼륨 복제를 삭제했습니다. 이러한 리소스를 사용하는 애플리케이션도 삭제했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Ecosystem → 설치된 Operators 를 클릭하여 설치된 모든 Operator를 확인합니다.

`openshift-lvm-storage` 네임스페이스에서 LVM Storage 를 클릭합니다.

LVMCluster 탭을 클릭합니다.

작업 에서 LVMCluster 삭제 를 선택합니다.

삭제 를 클릭합니다.

검증

`LVMCLuster` 페이지에서 `LVMCluster` CR이 삭제되었는지 확인합니다.

#### 5.4.4.3. RHACM을 사용하여 LVMCluster CR 삭제

RHACM(Red Hat Advanced Cluster Management)을 사용하여 LVM Storage를 설치한 경우 RHACM을 사용하여 `LVMCluster` CR을 삭제할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 RHACM 클러스터에 액세스할 수 있습니다.

LVM 스토리지에서 프로비저닝한 PVC(영구 볼륨 클레임), 볼륨 스냅샷 및 볼륨 복제를 삭제했습니다. 이러한 리소스를 사용하는 애플리케이션도 삭제했습니다.

프로세스

OpenShift Container Platform 인증 정보를 사용하여 RHACM CLI에 로그인합니다.

`LVMCluster` CR용으로 생성된 `ConfigurationPolicy` CR YAML 파일을 삭제합니다.

```shell-session
$ oc delete -f <file_name> -n <cluster_namespace>
```

1. LVM 스토리지가 설치된 OpenShift Container Platform 클러스터의 네임스페이스입니다.

`Policy` CR YAML 파일을 생성하여 `LVMCluster` CR을 삭제합니다.

```yaml
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  name: policy-lvmcluster-delete
  annotations:
    policy.open-cluster-management.io/standards: NIST SP 800-53
    policy.open-cluster-management.io/categories: CM Configuration Management
    policy.open-cluster-management.io/controls: CM-2 Baseline Configuration
spec:
  remediationAction: enforce
  disabled: false
  policy-templates:
    - objectDefinition:
        apiVersion: policy.open-cluster-management.io/v1
        kind: ConfigurationPolicy
        metadata:
          name: policy-lvmcluster-removal
        spec:
          remediationAction: enforce
          severity: low
          object-templates:
            - complianceType: mustnothave
              objectDefinition:
                kind: LVMCluster
                apiVersion: lvm.topolvm.io/v1alpha1
                metadata:
                  name: my-lvmcluster
                  namespace: openshift-lvm-storage
---
apiVersion: policy.open-cluster-management.io/v1
kind: PlacementBinding
metadata:
  name: binding-policy-lvmcluster-delete
placementRef:
  apiGroup: apps.open-cluster-management.io
  kind: PlacementRule
  name: placement-policy-lvmcluster-delete
subjects:
  - apiGroup: policy.open-cluster-management.io
    kind: Policy
    name: policy-lvmcluster-delete
---
apiVersion: apps.open-cluster-management.io/v1
kind: PlacementRule
metadata:
  name: placement-policy-lvmcluster-delete
spec:
  clusterConditions:
    - status: "True"
      type: ManagedClusterConditionAvailable
  clusterSelector:
    matchExpressions:
      - key: mykey
        operator: In
        values:
          - myvalue
```

1. `policy-template` 의 `spec.remediationAction` 은 `spec.remediationAction` 에 대한 이전 매개변수 값으로 재정의됩니다.

2. 이 `namespace` 필드에는 `openshift-lvm-storage` 값이 있어야 합니다.

3. 클러스터를 선택하도록 요구 사항을 구성합니다. 선택 기준과 일치하는 클러스터에서 LVM 스토리지가 제거됩니다.

다음 명령을 실행하여 `Policy` CR을 생성합니다.

```shell-session
$ oc create -f <file_name> -n <namespace>
```

`Policy` CR YAML 파일을 생성하여 `LVMCluster` CR이 삭제되었는지 확인합니다.

```yaml
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  name: policy-lvmcluster-inform
  annotations:
    policy.open-cluster-management.io/standards: NIST SP 800-53
    policy.open-cluster-management.io/categories: CM Configuration Management
    policy.open-cluster-management.io/controls: CM-2 Baseline Configuration
spec:
  remediationAction: inform
  disabled: false
  policy-templates:
    - objectDefinition:
        apiVersion: policy.open-cluster-management.io/v1
        kind: ConfigurationPolicy
        metadata:
          name: policy-lvmcluster-removal-inform
        spec:
          remediationAction: inform
          severity: low
          object-templates:
            - complianceType: mustnothave
              objectDefinition:
                kind: LVMCluster
                apiVersion: lvm.topolvm.io/v1alpha1
                metadata:
                  name: my-lvmcluster
                  namespace: openshift-lvm-storage
---
apiVersion: policy.open-cluster-management.io/v1
kind: PlacementBinding
metadata:
  name: binding-policy-lvmcluster-check
placementRef:
  apiGroup: apps.open-cluster-management.io
  kind: PlacementRule
  name: placement-policy-lvmcluster-check
subjects:
  - apiGroup: policy.open-cluster-management.io
    kind: Policy
    name: policy-lvmcluster-inform
---
apiVersion: apps.open-cluster-management.io/v1
kind: PlacementRule
metadata:
  name: placement-policy-lvmcluster-check
spec:
  clusterConditions:
    - status: "True"
      type: ManagedClusterConditionAvailable
  clusterSelector:
    matchExpressions:
      - key: mykey
        operator: In
        values:
          - myvalue
```

1. `policy-template`

`spec.remediationAction` 은 `spec.remediationAction` 의 이전 매개변수 값으로 재정의됩니다.

2. `namespace` 필드에는 `openshift-lvm-storage` 값이 있어야 합니다.

다음 명령을 실행하여 `Policy` CR을 생성합니다.

```shell-session
$ oc create -f <file_name> -n <namespace>
```

검증

다음 명령을 실행하여 `Policy` CR의 상태를 확인합니다.

```shell-session
$ oc get policy -n <namespace>
```

```shell-session
NAME                       REMEDIATION ACTION   COMPLIANCE STATE   AGE
policy-lvmcluster-delete   enforce              Compliant          15m
policy-lvmcluster-inform   inform               Compliant          15m
```

중요

`Policy` CR은 `Compliant` 상태에 있어야 합니다.

#### 5.4.5. 스토리지 프로비저닝

`LVMCluster` CR(사용자 정의 리소스)을 사용하여 LVM 볼륨 그룹을 생성한 후 PVC(영구 볼륨 클레임)를 생성하여 스토리지를 프로비저닝할 수 있습니다.

다음은 각 파일 시스템 유형에 요청할 수 있는 최소 스토리지 크기입니다.

`블록`: 8MiB

`XFS`: 300MiB

`ext4`: 32 MiB

PVC를 생성하려면 `PersistentVolumeClaim` 오브젝트를 생성해야 합니다.

사전 요구 사항

`LVMCluster` CR을 생성했습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

`PersistentVolumeClaim` 오브젝트를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: lvm-block-1
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 10Gi
    limits:
      storage: 20Gi
  storageClassName: lvms-vg1
```

1. PVC의 이름을 지정합니다.

2. 파일 PVC를 생성하려면 이 필드를 `Filesystem` 으로 설정합니다. 블록 PVC를 생성하려면 이 필드를 `Block` 으로 설정합니다.

3. 스토리지 크기를 지정합니다. 값이 최소 스토리지 크기보다 작으면 요청된 스토리지 크기가 최소 스토리지 크기로 반올림됩니다. 프로비저닝할 수 있는 총 스토리지 크기는 LVM(Logical Volume Manager) 씬 풀의 크기와 초과 프로비저닝 요인으로 제한됩니다.

4. 선택 사항: 스토리지 제한을 지정합니다. 이 필드를 최소 스토리지 크기보다 크거나 같은 값으로 설정합니다. 그러지 않으면 오류와 함께 PVC 생성이 실패합니다.

5. `storageClassName` 필드의 값은 `lvms-<device_class_name` > 형식이어야 합니다. 여기서 < `device_class_name` >은 `LVMCluster` CR의 `deviceClasses.name` 필드의 값입니다. 예를 들어 `deviceClasses.name` 필드가 Cryostat1로 설정된 경우 `storageClassName` 필드를 `lvms- vg1` 로 설정해야 합니다.

참고

스토리지 클래스의 `volumeBindingMode` 필드는 `WaitForFirstConsumer` 로 설정됩니다.

다음 명령을 실행하여 PVC를 생성합니다.

```shell-session
# oc create -f <file_name> -n <application_namespace>
```

참고

생성된 PVC는 해당 PVC를 사용하는 Pod를 배포할 때까지 `Pending` 상태로 유지됩니다.

검증

PVC가 생성되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pvc -n <namespace>
```

```shell-session
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
lvm-block-1   Bound    pvc-e90169a8-fd71-4eea-93b8-817155f60e47   1Gi        RWO            lvms-vg1       5s
```

#### 5.4.6. 클러스터 스토리지를 확장하는 방법

OpenShift Container Platform은 베어 메탈 사용자 프로비저닝 인프라에서 클러스터에 대한 추가 작업자 노드를 지원합니다. 사용 가능한 스토리지가 있는 새 작업자 노드를 추가하거나 기존 작업자 노드에 새 장치를 추가하여 클러스터의 스토리지를 확장할 수 있습니다.

LVM(Logical Volume Manager) 스토리지는 노드가 활성화되면 추가 작업자 노드를 감지하고 사용합니다.

클러스터의 기존 작업자 노드에 새 장치를 추가하려면 `LVMCluster` CR(사용자 정의 리소스)의 `deviceSelector` 필드에 있는 새 장치에 경로를 추가해야 합니다.

중요

`LVMCluster` CR을 생성하는 경우에만 `LVMCluster` CR에 `deviceSelector` 필드를 추가할 수 있습니다. `LVMCluster` CR을 생성하는 동안 `deviceSelector` 필드를 추가하지 않은 경우 `LVMCluster` CR을 삭제하고 `deviceSelector` 필드가 포함된 새 `LVMCluster` CR을 생성해야 합니다.

`LVMCluster` CR에 `deviceSelector` 필드를 추가하지 않으면 LVM 스토리지에서 장치를 사용할 수 있을 때 새 장치를 자동으로 추가합니다.

참고

LVM 스토리지는 지원되는 장치만 추가합니다. 지원되지 않는 장치에 대한 자세한 내용은 "LVM Storage에서 지원되지 않는 장치"를 참조하십시오.

추가 리소스

단일 노드 OpenShift 클러스터에 작업자 노드 추가

LVM 스토리지에서 지원되지 않는 장치

#### 5.4.6.1. CLI를 사용하여 클러스터 스토리지 확장

OpenShift CLI()를 사용하여 클러스터에서 작업자 노드의 스토리지 용량을 확장할 수 있습니다.

```shell
oc
```

사전 요구 사항

각 클러스터에 LVM(Logical Volume Manager) 스토리지에서 사용할 추가 사용되지 않는 장치가 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`LVMCluster` CR(사용자 정의 리소스)을 생성했습니다.

프로세스

다음 명령을 실행하여 `LVMCluster` CR을 편집합니다.

```shell-session
$ oc edit <lvmcluster_file_name> -n <namespace>
```

`deviceSelector` 필드에 새 장치의 경로를 추가합니다.

```yaml
apiVersion: lvm.topolvm.io/v1alpha1
kind: LVMCluster
metadata:
  name: my-lvmcluster
spec:
  storage:
    deviceClasses:
# ...
      deviceSelector:
        paths:
        - /dev/disk/by-path/pci-0000:87:00.0-nvme-1
        - /dev/disk/by-path/pci-0000:88:00.0-nvme-1
        optionalPaths:
        - /dev/disk/by-path/pci-0000:89:00.0-nvme-1
        - /dev/disk/by-path/pci-0000:90:00.0-nvme-1
# ...
```

1. LVM 볼륨 그룹에 추가할 장치의 경로를 지정하는 구성이 포함되어 있습니다. `paths` 필드, `optionalPaths` 필드 또는 둘 다에서 장치 경로를 지정할 수 있습니다. 경로와 `optionalPaths` 모두에 장치 `경로를` 지정하지 않으면 LVM(Logical Volume Manager) 스토리지에서 지원되는 사용되지 않는 장치가 LVM 볼륨 그룹에 추가됩니다. LVM 스토리지는 다음 조건이 충족되는 경우에만 LVM 볼륨 그룹에 장치를 추가합니다.

장치 경로가 있습니다.

장치는 LVM 스토리지에서 지원합니다. 지원되지 않는 장치에 대한 자세한 내용은 "LVM Storage에서 지원되지 않는 장치"를 참조하십시오.

2. 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM Storage에서 장치가 지원되지 않는 경우 `LVMCluster` CR은 `Failed` 상태로 이동합니다.

3. 선택적 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM 스토리지에서 장치가 지원되지 않는 경우 LVM 스토리지는 오류가 발생하지 않고 장치를 무시합니다.

중요

장치를 LVM 볼륨 그룹에 추가한 후에는 제거할 수 없습니다.

`LVMCluster` CR을 저장합니다.

추가 리소스

LVMCluster 사용자 정의 리소스 정보

LVM 스토리지에서 지원되지 않는 장치

볼륨 그룹에 장치 추가 정보

#### 5.4.6.2. 웹 콘솔을 사용하여 클러스터 스토리지 확장

OpenShift Container Platform 웹 콘솔을 사용하여 클러스터에서 작업자 노드의 스토리지 용량을 확장할 수 있습니다.

사전 요구 사항

각 클러스터에 LVM(Logical Volume Manager) 스토리지에서 사용할 추가 사용되지 않는 장치가 있습니다.

`LVMCluster` CR(사용자 정의 리소스)을 생성했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Ecosystem → 설치된 Operators를 클릭합니다.

`openshift-lvm-storage` 네임스페이스에서 LVM Storage 를 클릭합니다.

LVMCluster 탭을 클릭하여 클러스터에서 생성된 `LVMCluster` CR을 확인합니다.

Actions 메뉴에서 Edit LVMCluster 를 선택합니다.

YAML 탭을 클릭합니다.

`LVMCluster` CR을 편집하여 `deviceSelector` 필드에 새 장치 경로를 추가합니다.

```yaml
apiVersion: lvm.topolvm.io/v1alpha1
kind: LVMCluster
metadata:
  name: my-lvmcluster
spec:
  storage:
    deviceClasses:
# ...
      deviceSelector:
        paths:
        - /dev/disk/by-path/pci-0000:87:00.0-nvme-1
        - /dev/disk/by-path/pci-0000:88:00.0-nvme-1
        optionalPaths:
        - /dev/disk/by-path/pci-0000:89:00.0-nvme-1
        - /dev/disk/by-path/pci-0000:90:00.0-nvme-1
# ...
```

1. LVM 볼륨 그룹에 추가할 장치의 경로를 지정하는 구성이 포함되어 있습니다. `paths` 필드, `optionalPaths` 필드 또는 둘 다에서 장치 경로를 지정할 수 있습니다. 경로와 `optionalPaths` 모두에 장치 `경로를` 지정하지 않으면 LVM(Logical Volume Manager) 스토리지에서 지원되는 사용되지 않는 장치가 LVM 볼륨 그룹에 추가됩니다. LVM 스토리지는 다음 조건이 충족되는 경우에만 LVM 볼륨 그룹에 장치를 추가합니다.

장치 경로가 있습니다.

장치는 LVM 스토리지에서 지원합니다. 지원되지 않는 장치에 대한 자세한 내용은 "LVM Storage에서 지원되지 않는 장치"를 참조하십시오.

2. 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM Storage에서 장치가 지원되지 않는 경우 `LVMCluster` CR은 `Failed` 상태로 이동합니다.

3. 선택적 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM 스토리지에서 장치가 지원되지 않는 경우 LVM 스토리지는 오류가 발생하지 않고 장치를 무시합니다.

중요

장치를 LVM 볼륨 그룹에 추가한 후에는 제거할 수 없습니다.

저장 을 클릭합니다.

추가 리소스

LVMCluster 사용자 정의 리소스 정보

LVM 스토리지에서 지원되지 않는 장치

볼륨 그룹에 장치 추가 정보

#### 5.4.6.3. RHACM을 사용하여 클러스터 스토리지 확장

RHACM을 사용하여 클러스터에서 작업자 노드의 스토리지 용량을 확장할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 계정을 사용하여 RHACM 클러스터에 액세스할 수 있습니다.

RHACM을 사용하여 `LVMCluster` CR(사용자 정의 리소스)을 생성했습니다.

각 클러스터에 LVM(Logical Volume Manager) 스토리지에서 사용할 추가 사용되지 않는 장치가 있습니다.

프로세스

OpenShift Container Platform 인증 정보를 사용하여 RHACM CLI에 로그인합니다.

다음 명령을 실행하여 RHACM을 사용하여 생성한 `LVMCluster` CR을 편집합니다.

```shell-session
$ oc edit -f <file_name> -n <namespace>
```

1. & `lt;file_name&` gt;을 `LVMCluster` CR의 이름으로 바꿉니다.

`LVMCluster` CR에서 `deviceSelector` 필드의 새 장치에 경로를 추가합니다.

```yaml
apiVersion: policy.open-cluster-management.io/v1
kind: ConfigurationPolicy
metadata:
  name: lvms
spec:
  object-templates:
     - complianceType: musthave
       objectDefinition:
         apiVersion: lvm.topolvm.io/v1alpha1
         kind: LVMCluster
         metadata:
           name: my-lvmcluster
           namespace: openshift-lvm-storage
         spec:
           storage:
             deviceClasses:
# ...
               deviceSelector:
                 paths:
                 - /dev/disk/by-path/pci-0000:87:00.0-nvme-1
                 optionalPaths:
                 - /dev/disk/by-path/pci-0000:89:00.0-nvme-1
# ...
```

1. LVM 볼륨 그룹에 추가할 장치의 경로를 지정하는 구성이 포함되어 있습니다. `paths` 필드, `optionalPaths` 필드 또는 둘 다에서 장치 경로를 지정할 수 있습니다. 경로와 `optionalPaths` 모두에 장치 `경로를` 지정하지 않으면 LVM(Logical Volume Manager) 스토리지에서 지원되는 사용되지 않는 장치가 LVM 볼륨 그룹에 추가됩니다. LVM 스토리지는 다음 조건이 충족되는 경우에만 LVM 볼륨 그룹에 장치를 추가합니다.

장치 경로가 있습니다.

장치는 LVM 스토리지에서 지원합니다. 지원되지 않는 장치에 대한 자세한 내용은 "LVM Storage에서 지원되지 않는 장치"를 참조하십시오.

2. 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM Storage에서 장치가 지원되지 않는 경우 `LVMCluster` CR은 `Failed` 상태로 이동합니다.

3. 선택적 장치 경로를 지정합니다. 이 필드에 지정된 장치 경로가 없거나 LVM 스토리지에서 장치가 지원되지 않는 경우 LVM 스토리지는 오류가 발생하지 않고 장치를 무시합니다.

중요

장치를 LVM 볼륨 그룹에 추가한 후에는 제거할 수 없습니다.

`LVMCluster` CR을 저장합니다.

추가 리소스

Red Hat Advanced Cluster Management for Kubernetes: 온라인 연결된 동안 설치

LVMCluster 사용자 정의 리소스 정보

LVM 스토리지에서 지원되지 않는 장치

볼륨 그룹에 장치 추가 정보

#### 5.4.7. 영구 볼륨 클레임 확장

클러스터 스토리지를 확장한 후 기존 PVC(영구 볼륨 클레임)를 확장할 수 있습니다.

PVC를 확장하려면 PVC의 `storage` 필드를 업데이트해야 합니다.

사전 요구 사항

동적 프로비저닝이 사용됩니다.

PVC와 연결된 `StorageClass` 오브젝트에는 `allowVolumeExpansion` 필드가 `true` 로 설정되어 있습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 실행하여 `spec.resources.requests.storage` 필드의 값을 현재 값보다 큰 값으로 업데이트합니다.

```shell-session
$ oc patch pvc <pvc_name> -n <application_namespace> \
  --type=merge -p \ '{ "spec": { "resources": { "requests": { "storage": "<desired_size>" }}}}'
```

1. & `lt;pvc_name` >을 확장하려는 PVC 이름으로 바꿉니다.

2. & `lt;desired_size&` gt;를 새 크기로 교체하여 PVC를 확장합니다.

검증

크기 조정이 완료되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pvc <pvc_name> -n <application_namespace> -o=jsonpath={.status.capacity.storage}
```

LVM 스토리지는 확장 중에 PVC에 `Resizing` 조건을 추가합니다. PVC 확장 후 `Resizing` 조건을 삭제합니다.

추가 리소스

클러스터 스토리지를 확장하는 방법

볼륨 확장 지원 활성화

#### 5.4.8. 영구 볼륨 클레임 삭제

OpenShift CLI()를 사용하여 PVC(영구 볼륨 클레임)를 삭제할 수 있습니다.

```shell
oc
```

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 실행하여 PVC를 삭제합니다.

```shell-session
$ oc delete pvc <pvc_name> -n <namespace>
```

검증

PVC가 삭제되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pvc -n <namespace>
```

삭제된 PVC는 이 명령의 출력에 표시되지 않아야 합니다.

#### 5.4.9. 볼륨 스냅샷 정보

LVM 스토리지에서 프로비저닝하는 PVC(영구 볼륨 클레임)의 스냅샷을 생성할 수 있습니다.

볼륨 스냅샷을 사용하여 다음 작업을 수행할 수 있습니다.

애플리케이션 데이터를 백업합니다.

중요

볼륨 스냅샷은 원래 데이터와 동일한 장치에 있습니다. 볼륨 스냅샷을 백업으로 사용하려면 스냅샷을 안전한 위치로 이동해야 합니다. OADP(OpenShift API for Data Protection) 백업 및 복원 솔루션을 사용할 수 있습니다. OADP에 대한 자세한 내용은 "OADP 기능"을 참조하십시오.

볼륨 스냅샷을 만든 상태로 되돌립니다.

참고

볼륨 복제의 볼륨 스냅샷을 생성할 수도 있습니다.

#### 5.4.9.1. 다중 노드 토폴로지에서 볼륨 스냅샷을 생성하기 위한 제한 사항

LVM 스토리지에는 다중 노드 토폴로지에서 볼륨 스냅샷을 생성하기 위한 다음과 같은 제한 사항이 있습니다.

볼륨 스냅샷 생성은 LVM 씬 풀 기능을 기반으로 합니다.

볼륨 스냅샷을 생성한 후 노드에 원래 데이터 소스를 추가로 업데이트하기 위한 추가 스토리지 공간이 있어야 합니다.

원래 데이터 소스를 배포한 노드에서만 볼륨 스냅샷을 생성할 수 있습니다.

스냅샷 데이터를 사용하는 PVC를 사용하는 Pod는 원래 데이터 소스를 배포한 노드에서만 예약할 수 있습니다.

추가 리소스

OADP 기능

#### 5.4.9.2. 볼륨 스냅샷 생성

씬 풀의 사용 가능한 용량 및 초과 프로비저닝 제한을 기반으로 볼륨 스냅샷을 생성할 수 있습니다. 볼륨 스냅샷을 생성하려면 `VolumeSnapshotClass` 오브젝트를 생성해야 합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

PVC(영구 볼륨 클레임)가 `Bound` 상태인지 확인합니다. 이는 일관된 스냅샷에 필요합니다.

PVC에 대한 모든 I/O를 중지했습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

`VolumeSnapshot` 오브젝트를 생성합니다.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: lvm-block-1-snap
spec:
  source:
    persistentVolumeClaimName: lvm-block-1
  volumeSnapshotClassName: lvms-vg1
```

1. 볼륨 스냅샷의 이름을 지정합니다.

2. 소스 PVC의 이름을 지정합니다. LVM 스토리지는 이 PVC의 스냅샷을 생성합니다.

3. 이 필드를 볼륨 스냅샷 클래스의 이름으로 설정합니다.

참고

사용 가능한 볼륨 스냅샷 클래스 목록을 가져오려면 다음 명령을 실행합니다.

```shell-session
$ oc get volumesnapshotclass
```

다음 명령을 실행하여 소스 PVC를 생성한 네임스페이스에 볼륨 스냅샷을 생성합니다.

```shell-session
$ oc create -f <file_name> -n <namespace>
```

LVM 스토리지는 볼륨 스냅샷으로 PVC의 읽기 전용 사본을 생성합니다.

검증

볼륨 스냅샷이 생성되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get volumesnapshot -n <namespace>
```

```shell-session
NAME               READYTOUSE   SOURCEPVC     SOURCESNAPSHOTCONTENT   RESTORESIZE   SNAPSHOTCLASS   SNAPSHOTCONTENT                                    CREATIONTIME   AGE
lvm-block-1-snap   true         lvms-test-1                           1Gi           lvms-vg1        snapcontent-af409f97-55fc-40cf-975f-71e44fa2ca91   19s            19s
```

생성한 볼륨 스냅샷의 `READYTOUSE` 필드 값은 `true` 여야 합니다.

#### 5.4.9.3. 볼륨 스냅샷 복원

볼륨 스냅샷을 복원하려면 `dataSource.name` 필드가 볼륨 스냅샷 이름으로 설정된 PVC(영구 볼륨 클레임)를 생성해야 합니다.

복원된 PVC는 볼륨 스냅샷 및 소스 PVC와 독립적입니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

볼륨 스냅샷을 생성했습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

볼륨 스냅샷을 복원하려면 구성으로 `PersistentVolumeClaim` 오브젝트를 생성합니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: lvm-block-1-restore
spec:
  accessModes:
  - ReadWriteOnce
  volumeMode: Block
  Resources:
    Requests:
      storage: 2Gi
  storageClassName: lvms-vg1
  dataSource:
    name: lvm-block-1-snap
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

1. 복원된 PVC의 스토리지 크기를 지정합니다. 요청된 PVC의 스토리지 크기는 복원하려는 볼륨 스냅샷의 stoage 크기보다 크거나 같아야 합니다. 더 큰 PVC가 필요한 경우 볼륨 스냅샷을 복원한 후 PVC의 크기를 조정할 수도 있습니다.

2. 복원하려는 볼륨 스냅샷의 소스 PVC에 있는 `storageClassName` 필드 값으로 이 필드를 설정합니다.

3. 이 필드를 복원할 볼륨 스냅샷의 이름으로 설정합니다.

다음 명령을 실행하여 볼륨 스냅샷을 생성한 네임스페이스에 PVC를 생성합니다.

```shell-session
$ oc create -f <file_name> -n <namespace>
```

검증

볼륨 스냅샷이 복원되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pvc -n <namespace>
```

```shell-session
NAME                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
lvm-block-1-restore   Bound    pvc-e90169a8-fd71-4eea-93b8-817155f60e47   1Gi        RWO            lvms-vg1       5s
```

#### 5.4.9.4. 볼륨 스냅샷 삭제

PVC(영구 볼륨 클레임)의 볼륨 스냅샷을 삭제할 수 있습니다.

중요

PVC(영구 볼륨 클레임)를 삭제하면 LVM 스토리지가 PVC의 스냅샷이 아닌 PVC만 삭제합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

삭제할 볼륨 snpashot이 사용되지 않는지 확인했습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 실행하여 볼륨 스냅샷을 삭제합니다.

```shell-session
$ oc delete volumesnapshot <volume_snapshot_name> -n <namespace>
```

검증

볼륨 스냅샷이 삭제되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get volumesnapshot -n <namespace>
```

삭제된 볼륨 스냅샷은 이 명령의 출력에 표시되지 않아야 합니다.

#### 5.4.10. 볼륨 복제 정보

볼륨 복제는 기존 PVC(영구 볼륨 클레임)와 중복됩니다. 볼륨 복제를 생성하여 특정 시점의 데이터를 복사할 수 있습니다.

#### 5.4.10.1. 다중 노드 토폴로지에서 볼륨 복제 생성에 대한 제한 사항

LVM 스토리지에는 다중 노드 토폴로지에서 볼륨 복제를 생성하기 위한 다음과 같은 제한 사항이 있습니다.

볼륨 복제 생성은 LVM 씬 풀 기능을 기반으로 합니다.

원래 데이터 소스를 추가로 업데이트하려면 볼륨 복제를 생성한 후 노드에 추가 스토리지가 있어야 합니다.

원래 데이터 소스를 배포한 노드에서만 볼륨 복제를 생성할 수 있습니다.

복제 데이터를 사용하는 PVC를 사용하는 Pod는 원래 데이터 소스를 배포한 노드에서만 예약할 수 있습니다.

#### 5.4.10.2. 볼륨 복제 생성

PVC(영구 볼륨 클레임) 복제본을 생성하려면 소스 PVC를 생성한 네임스페이스에 `PersistentVolumeClaim` 오브젝트를 생성해야 합니다.

중요

복제된 PVC에는 쓰기 액세스 권한이 있습니다.

사전 요구 사항

소스 PVC가 `Bound` 상태인지 확인합니다. 이는 일관된 복제에 필요합니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

`PersistentVolumeClaim` 오브젝트를 생성합니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: lvm-pvc-clone
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: lvms-vg1
  volumeMode: Filesystem
  dataSource:
    kind: PersistentVolumeClaim
    name: lvm-pvc
  resources:
    requests:
      storage: 1Gi
```

1. 이 필드를 소스 PVC의 `storageClassName` 필드 값으로 설정합니다.

2. 이 필드를 소스 PVC의 `volumeMode` 필드로 설정합니다.

3. 소스 PVC의 이름을 지정합니다.

4. 복제된 PVC의 스토리지 크기를 지정합니다. 복제된 PVC의 스토리지 크기는 소스 PVC의 스토리지 크기보다 크거나 같아야 합니다.

다음 명령을 실행하여 소스 PVC를 생성한 네임스페이스에 PVC를 생성합니다.

```shell-session
$ oc create -f <file_name> -n <namespace>
```

검증

볼륨 복제가 생성되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pvc -n <namespace>
```

```shell-session
NAME                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
lvm-block-1-clone   Bound    pvc-e90169a8-fd71-4eea-93b8-817155f60e47   1Gi        RWO            lvms-vg1       5s
```

#### 5.4.10.3. 볼륨 복제 삭제

볼륨 복제를 삭제할 수 있습니다.

중요

PVC(영구 볼륨 클레임)를 삭제하면 LVM 스토리지가 소스 PVC(영구 볼륨 클레임)만 삭제하지만 PVC의 복제본은 삭제하지 않습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 실행하여 복제된 PVC를 삭제합니다.

```shell-session
# oc delete pvc <clone_pvc_name> -n <namespace>
```

검증

볼륨 복제가 삭제되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pvc -n <namespace>
```

삭제된 볼륨 복제는 이 명령의 출력에 표시되지 않아야 합니다.

#### 5.4.11. LVM 스토리지 업데이트

OpenShift Container Platform 버전과의 호환성을 보장하기 위해 LVM 스토리지를 업데이트할 수 있습니다.

참고

LVM Storage Operator의 기본 네임스페이스는 `openshift-lvm-storage` 입니다.

사전 요구 사항

OpenShift Container Platform 클러스터를 업데이트했습니다.

이전 버전의 LVM Storage를 설치했습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 계정을 사용하여 클러스터에 액세스할 수 있습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 실행하여 LVM 스토리지를 설치하는 동안 생성한 `Subscription` CR(사용자 정의 리소스)을 업데이트합니다.

```shell-session
$ oc patch subscription lvms-operator -n openshift-lvm-storage --type merge --patch '{"spec":{"channel":"<update_channel>"}}'
```

1. & `lt;update_channel` >을 설치하려는 LVM 스토리지 버전으로 바꿉니다. 예를 들면 `stable-4.20` 입니다.

업데이트 이벤트를 보고 다음 명령을 실행하여 설치가 완료되었는지 확인합니다.

```shell-session
$ oc get events -n openshift-lvm-storage
```

```shell-session
...
8m13s       Normal    RequirementsUnknown   clusterserviceversion/lvms-operator.v4.20   requirements not yet checked
8m11s       Normal    RequirementsNotMet    clusterserviceversion/lvms-operator.v4.20   one or more requirements couldn't be found
7m50s       Normal    AllRequirementsMet    clusterserviceversion/lvms-operator.v4.20   all requirements found, attempting install
7m50s       Normal    InstallSucceeded      clusterserviceversion/lvms-operator.v4.20   waiting for install components to report healthy
7m49s       Normal    InstallWaiting        clusterserviceversion/lvms-operator.v4.20   installing: waiting for deployment lvms-operator to become ready: deployment "lvms-operator" waiting for 1 outdated replica(s) to be terminated
7m39s       Normal    InstallSucceeded      clusterserviceversion/lvms-operator.v4.20   install strategy completed with no errors
...
```

검증

다음 명령을 실행하여 LVM 스토리지 버전을 확인합니다.

```shell-session
$ oc get subscription lvms-operator -n openshift-lvm-storage -o jsonpath='{.status.installedCSV}'
```

```shell-session
lvms-operator.v4.20
```

#### 5.4.12. LVM 스토리지 모니터링

클러스터 모니터링을 활성화하려면 LVM 스토리지를 설치한 네임스페이스에 다음 레이블을 추가해야 합니다.

```plaintext
openshift.io/cluster-monitoring=true
```

중요

RHACM에서 클러스터 모니터링 활성화에 대한 자세한 내용은 Observability 및 사용자 정의 지표 추가 를 참조하십시오.

#### 5.4.12.1. 지표

메트릭을 확인하여 LVM 스토리지를 모니터링할 수 있습니다.

다음 표에서는 `topolvm` 메트릭을 설명합니다.

| 경고 | 설명 |
| --- | --- |
| `topolvm_thinpool_data_percent` | LVM thinpool에 사용된 데이터 공간의 백분율을 나타냅니다. |
| `topolvm_thinpool_metadata_percent` | LVM thinpool에 사용된 메타데이터 공간의 백분율을 나타냅니다. |
| `topolvm_thinpool_size_bytes` | LVM 씬 풀의 크기를 바이트 단위로 나타냅니다. |
| `topolvm_volumegroup_available_bytes` | LVM 볼륨 그룹의 사용 가능한 공간을 바이트 단위로 나타냅니다. |
| `topolvm_volumegroup_size_bytes` | LVM 볼륨 그룹의 크기를 바이트 단위로 나타냅니다. |
| `topolvm_thinpool_overprovisioned_available` | LVM 씬 풀의 사용 가능한 초과 프로비저닝 크기를 바이트 단위로 나타냅니다. |

참고

지표는 10분마다 업데이트되거나 씬 풀에서 새 논리 볼륨 생성과 같은 변경이 있을 때 업데이트됩니다.

#### 5.4.12.2. 경고

thin 풀 및 볼륨 그룹이 최대 스토리지 용량에 도달하면 추가 작업이 실패합니다. 이는 데이터 손실을 초래할 수 있습니다.

LVM 스토리지는 thin 풀 및 볼륨 그룹 사용이 특정 값을 초과하면 다음 경고를 보냅니다.

| 경고 | 설명 |
| --- | --- |
| `VolumeGroupUsageAtThresholdNearFull` | 이 경고는 볼륨 그룹과 씬 풀 사용량이 노드에서 75%를 초과하면 트리거됩니다. 데이터 삭제 또는 볼륨 그룹 확장이 필요합니다. |
| `VolumeGroupUsageAtThresholdCritical` | 이 경고는 볼륨 그룹과 씬 풀 사용량이 노드에서 85%를 초과하면 트리거됩니다. 이 경우 볼륨 그룹이 매우 가득 차 있습니다. 데이터 삭제 또는 볼륨 그룹 확장이 필요합니다. |
| `ThinPoolDataUsageAtThresholdNearFull` | 이 경고는 볼륨 그룹의 thin pool data uusage가 노드에서 75%를 초과하면 트리거됩니다. 데이터 삭제 또는 씬 풀 확장이 필요합니다. |
| `ThinPoolDataUsageAtThresholdCritical` | 이 경고는 볼륨 그룹의 씬 풀 데이터 사용량이 노드에서 85%를 초과하면 트리거됩니다. 데이터 삭제 또는 씬 풀 확장이 필요합니다. |
| `ThinPoolMetaDataUsageAtThresholdNearFull` | 이 경고는 볼륨 그룹의 씬 풀 메타데이터 사용량이 노드에서 75%를 초과하면 트리거됩니다. 데이터 삭제 또는 씬 풀 확장이 필요합니다. |
| `ThinPoolMetaDataUsageAtThresholdCritical` | 이 경고는 볼륨 그룹의 씬 풀 메타데이터 사용량이 노드에서 85%를 초과하면 트리거됩니다. 데이터 삭제 또는 씬 풀 확장이 필요합니다. |

#### 5.4.13. CLI를 사용하여 LVM 스토리지 설치 제거

OpenShift CLI()를 사용하여 LVM 스토리지를 설치 제거할 수 있습니다.

```shell
oc
```

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 다음 명령에 로그인했습니다.

```shell
oc
```

LVM 스토리지에서 프로비저닝한 PVC(영구 볼륨 클레임), 볼륨 스냅샷 및 볼륨 복제를 삭제했습니다. 이러한 리소스를 사용하는 애플리케이션도 삭제했습니다.

`LVMCluster` CR(사용자 정의 리소스)을 삭제했습니다.

프로세스

다음 명령을 실행하여 LVM Storage Operator의 `currentCSV` 값을 가져옵니다.

```shell-session
$ oc get subscription.operators.coreos.com lvms-operator -n <namespace> -o yaml | grep currentCSV
```

```shell-session
currentCSV: lvms-operator.v4.15.3
```

다음 명령을 실행하여 서브스크립션을 삭제합니다.

```shell-session
$ oc delete subscription.operators.coreos.com lvms-operator -n <namespace>
```

```shell-session
subscription.operators.coreos.com "lvms-operator" deleted
```

다음 명령을 실행하여 대상 네임스페이스에서 LVM Storage Operator의 CSV를 삭제합니다.

```shell-session
$ oc delete clusterserviceversion <currentCSV> -n <namespace>
```

1. & `lt;currentCSV&` gt;를 LVM Storage Operator의 `currentCSV` 값으로 바꿉니다.

```shell-session
clusterserviceversion.operators.coreos.com "lvms-operator.v4.15.3" deleted
```

검증

LVM Storage Operator가 제거되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get csv -n <namespace>
```

LVM Storage Operator가 성공적으로 설치 제거되면 이 명령의 출력에 표시되지 않습니다.

#### 5.4.14. 웹 콘솔을 사용하여 LVM 스토리지 설치 제거

OpenShift Container Platform 웹 콘솔을 사용하여 LVM 스토리지를 설치 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform에 액세스할 수 있습니다.

LVM 스토리지에서 프로비저닝한 PVC(영구 볼륨 클레임), 볼륨 스냅샷 및 볼륨 복제를 삭제했습니다. 이러한 리소스를 사용하는 애플리케이션도 삭제했습니다.

`LVMCluster` CR(사용자 정의 리소스)을 삭제했습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Ecosystem → 설치된 Operators를 클릭합니다.

`openshift-lvm-storage` 네임스페이스에서 LVM Storage 를 클릭합니다.

세부 정보 탭을 클릭합니다.

작업 메뉴에서 Operator 설치 제거를 선택합니다.

선택 사항: 메시지가 표시되면 이 operator의 모든 피연산자 인스턴스 삭제 확인란을 선택하여 LVM Storage의 피연산자 인스턴스를 삭제합니다.

제거 를 클릭합니다.

#### 5.4.15. RHACM을 사용하여 설치된 LVM 스토리지 설치 제거

RHACM을 사용하여 설치한 LVM 스토리지를 설치 제거하려면 LVM 스토리지를 설치 및 구성하기 위해 생성한 RHACM `정책` CR(사용자 정의 리소스)을 삭제해야 합니다.

사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 RHACM 클러스터에 액세스할 수 있습니다.

LVM 스토리지에서 프로비저닝한 PVC(영구 볼륨 클레임), 볼륨 스냅샷 및 볼륨 복제를 삭제했습니다. 이러한 리소스를 사용하는 애플리케이션도 삭제했습니다.

RHACM을 사용하여 생성한 `LVMCluster` CR을 삭제했습니다.

프로세스

OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 사용하여 LVM 스토리지를 설치 및 구성하기 위해 생성한 RHACM `정책` CR을 삭제합니다.

```shell-session
$ oc delete -f <policy> -n <namespace>
```

1. & `lt;policy&` gt;를 `Policy` CR YAML 파일의 이름으로 바꿉니다.

LVM 스토리지를 설치 제거하려면 구성으로 `Policy` CR YAML 파일을 생성합니다.

```yaml
apiVersion: apps.open-cluster-management.io/v1
kind: PlacementRule
metadata:
  name: placement-uninstall-lvms
spec:
  clusterConditions:
  - status: "True"
    type: ManagedClusterConditionAvailable
  clusterSelector:
    matchExpressions:
    - key: mykey
      operator: In
      values:
      - myvalue
---
apiVersion: policy.open-cluster-management.io/v1
kind: PlacementBinding
metadata:
  name: binding-uninstall-lvms
placementRef:
  apiGroup: apps.open-cluster-management.io
  kind: PlacementRule
  name: placement-uninstall-lvms
subjects:
- apiGroup: policy.open-cluster-management.io
  kind: Policy
  name: uninstall-lvms
---
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  annotations:
    policy.open-cluster-management.io/categories: CM Configuration Management
    policy.open-cluster-management.io/controls: CM-2 Baseline Configuration
    policy.open-cluster-management.io/standards: NIST SP 800-53
  name: uninstall-lvms
spec:
  disabled: false
  policy-templates:
  - objectDefinition:
      apiVersion: policy.open-cluster-management.io/v1
      kind: ConfigurationPolicy
      metadata:
        name: uninstall-lvms
      spec:
        object-templates:
        - complianceType: mustnothave
          objectDefinition:
            apiVersion: v1
            kind: Namespace
            metadata:
              name: openshift-lvm-storage
        - complianceType: mustnothave
          objectDefinition:
            apiVersion: operators.coreos.com/v1
            kind: OperatorGroup
            metadata:
              name: openshift-storage-operatorgroup
              namespace: openshift-lvm-storage
            spec:
              targetNamespaces:
              - openshift-lvm-storage
        - complianceType: mustnothave
          objectDefinition:
            apiVersion: operators.coreos.com/v1alpha1
            kind: Subscription
            metadata:
              name: lvms-operator
              namespace: openshift-lvm-storage
        remediationAction: enforce
        severity: low
  - objectDefinition:
      apiVersion: policy.open-cluster-management.io/v1
      kind: ConfigurationPolicy
      metadata:
        name: policy-remove-lvms-crds
      spec:
        object-templates:
        - complianceType: mustnothave
          objectDefinition:
            apiVersion: apiextensions.k8s.io/v1
            kind: CustomResourceDefinition
            metadata:
              name: logicalvolumes.topolvm.io
        - complianceType: mustnothave
          objectDefinition:
            apiVersion: apiextensions.k8s.io/v1
            kind: CustomResourceDefinition
            metadata:
              name: lvmclusters.lvm.topolvm.io
        - complianceType: mustnothave
          objectDefinition:
            apiVersion: apiextensions.k8s.io/v1
            kind: CustomResourceDefinition
            metadata:
              name: lvmvolumegroupnodestatuses.lvm.topolvm.io
        - complianceType: mustnothave
          objectDefinition:
            apiVersion: apiextensions.k8s.io/v1
            kind: CustomResourceDefinition
            metadata:
              name: lvmvolumegroups.lvm.topolvm.io
        remediationAction: enforce
        severity: high
```

다음 명령을 실행하여 `Policy` CR을 생성합니다.

```shell-session
$ oc create -f <policy> -ns <namespace>
```

#### 5.4.16. must-gather를 사용하여 로그 파일 및 진단 정보 다운로드

LVM 스토리지에서 문제를 자동으로 해결할 수 없는 경우 must-gather 툴을 사용하여 로그 파일 및 진단 정보를 수집하여 귀하 또는 Red Hat 지원팀이 문제를 검토하고 솔루션을 결정할 수 있도록 합니다.

프로세스

LVM 스토리지 클러스터에 연결된 클라이언트에서 `must-gather` 명령을 실행합니다.

```shell-session
$ oc adm must-gather --image=registry.redhat.io/lvms4/lvms-must-gather-rhel9:v4.20 --dest-dir=<directory_name>
```

추가 리소스

must-gather 툴 정보

#### 5.4.17. 영구 스토리지 문제 해결

LVM(Logical Volume Manager) 스토리지를 사용하여 영구 스토리지를 구성하는 동안 문제 해결이 필요한 몇 가지 문제가 발생할 수 있습니다.

#### 5.4.17.1. Pending 상태에 있는 PVC 조사

PVC(영구 볼륨 클레임)는 다음과 같은 이유로 `Pending` 상태로 고정될 수 있습니다.

컴퓨팅 리소스가 충분하지 않습니다.

네트워크 문제.

일치하지 않는 스토리지 클래스 또는 노드 선택기입니다.

사용 가능한 PV(영구 볼륨)가 없습니다.

PV가 있는 노드는 `Not Ready` 상태입니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 OpenShift CLI()에 로그인했습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 PVC 목록을 검색합니다.

```shell-session
$ oc get pvc
```

```shell-session
NAME        STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
lvms-test   Pending                                      lvms-vg1       11s
```

다음 명령을 실행하여 PVC와 관련된 이벤트를 `Pending` 상태로 유지합니다.

```shell-session
$ oc describe pvc <pvc_name>
```

1. `<pvc_name>` 을 PVC 이름으로 바꿉니다. 예를 들면 `lvms-vg1` 입니다.

```shell-session
Type     Reason              Age               From                         Message
----     ------              ----              ----                         -------
Warning  ProvisioningFailed  4s (x2 over 17s)  persistentvolume-controller  storageclass.storage.k8s.io "lvms-vg1" not found
```

#### 5.4.17.2. 누락된 스토리지 클래스에서 복구

`스토리지 클래스를 찾을 수 없는` 경우 `LVMCluster` CR(사용자 정의 리소스)을 확인하고 모든 LVM(Logical Volume Manager) 스토리지 Pod가 `Running` 상태인지 확인합니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 OpenShift CLI()에 로그인했습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 `LVMCluster` CR이 있는지 확인합니다.

```shell-session
$ oc get lvmcluster -n <namespace>
```

```shell-session
NAME            AGE
my-lvmcluster   65m
```

`LVMCluster` CR이 없으면 `LVMCluster` CR을 생성합니다. 자세한 내용은 "Ways to create an LVMCluster custom resource"를 참조하십시오.

Operator가 설치된 네임스페이스에서 다음 명령을 실행하여 모든 LVM 스토리지 Pod가 `Running` 상태에 있는지 확인합니다.

```shell-session
$ oc get pods -n <namespace>
```

```shell-session
NAME                                  READY   STATUS    RESTARTS      AGE
lvms-operator-7b9fb858cb-6nsml        3/3     Running   0             70m
topolvm-controller-5dd9cf78b5-7wwr2   5/5     Running   0             66m
topolvm-node-dr26h                    4/4     Running   0             66m
vg-manager-r6zdv                      1/1     Running   0             66m
```

이 명령의 출력에는 다음 Pod의 실행 중인 인스턴스가 포함되어야 합니다.

`lvms-operator`

`vg-manager`

구성 파일을 로드하는 동안 Cryostat `-manager` pod가 중단된 경우 LVM Storage에서 사용할 사용 가능한 디스크를 찾지 못하기 때문입니다. 이 문제를 해결하기 위해 필요한 정보를 검색하려면 다음 명령을 실행하여 Cryostat `-manager` Pod의 로그를 검토합니다.

```shell-session
$ oc logs -l app.kubernetes.io/component=vg-manager -n <namespace>
```

추가 리소스

LVMCluster 사용자 정의 리소스 정보

LVMCluster 사용자 정의 리소스를 생성하는 방법

#### 5.4.17.3. 노드 장애로 복구

PVC(영구 볼륨 클레임)는 클러스터의 노드 오류로 인해 `Pending` 상태가 될 수 있습니다.

실패한 노드를 식별하기 위해 `topolvm-node` Pod의 재시작 횟수를 검사할 수 있습니다. 재시작 횟수가 증가하면 기본 노드의 잠재적인 문제가 발생하므로 추가 조사 및 문제 해결이 필요할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 OpenShift CLI()에 로그인했습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 `topolvm-node` Pod 인스턴스의 재시작 횟수를 검사합니다.

```shell-session
$ oc get pods -n <namespace>
```

```shell-session
NAME                                  READY   STATUS    RESTARTS      AGE
lvms-operator-7b9fb858cb-6nsml        3/3     Running   0             70m
topolvm-controller-5dd9cf78b5-7wwr2   5/5     Running   0             66m
topolvm-node-dr26h                    4/4     Running   0             66m
topolvm-node-54as8                    4/4     Running   0             66m
topolvm-node-78fft                    4/4     Running   17 (8s ago)   66m
vg-manager-r6zdv                      1/1     Running   0             66m
vg-manager-990ut                      1/1     Running   0             66m
vg-manager-an118                      1/1     Running   0             66m
```

다음 단계

노드 문제를 해결한 후에도 PVC가 `Pending` 상태에 있는 경우 강제 정리를 수행해야 합니다. 자세한 내용은 "Performing a forced clean-up"을 참조하십시오.

추가 리소스

강제 정리 수행

#### 5.4.17.4. 디스크 장애에서 복구

PVC(영구 볼륨 클레임)와 연결된 이벤트를 검사하는 동안 실패 메시지가 표시되면 기본 볼륨 또는 디스크에 문제가 있을 수 있습니다.

디스크 및 볼륨 프로비저닝 문제로 인해 스토리지 클래스 <. 일반 오류 메시지에는 특정 볼륨 실패 오류 메시지가 표시됩니다.

```shell
storage_class_name>을 사용하여 볼륨을 프로비저닝하지 못했습니다
```

다음 표에서는 볼륨 실패 오류 메시지를 설명합니다.

| 오류 메시지 | 설명 |
| --- | --- |
| `볼륨 존재를 확인하지 못했습니다` | 볼륨이 이미 있는지 확인하는 데 문제가 있음을 나타냅니다. 볼륨 확인 오류는 네트워크 연결 문제 또는 기타 오류로 인해 발생할 수 있습니다. |
| `볼륨을 바인딩하지 못했습니다` | 사용 가능한 PV(영구 볼륨)가 PVC의 요구 사항과 일치하지 않으면 볼륨을 바인딩하지 못할 수 있습니다. |
| `FailedMount` 또는 `FailedAttachVolume` | 이 오류는 볼륨을 노드에 마운트하려고 할 때 문제가 있음을 나타냅니다. 디스크가 실패한 경우 Pod에서 PVC 사용을 시도할 때 이 오류가 표시될 수 있습니다. |
| `FailedUnMount` | 이 오류는 노드에서 볼륨을 마운트 해제하려고 할 때 문제가 있음을 나타냅니다. 디스크가 실패한 경우 Pod에서 PVC 사용을 시도할 때 이 오류가 표시될 수 있습니다. |
| `볼륨은 이미 하나의 노드에만 연결되어 있으며 다른 노드에 연결할 수 없습니다.` | 이 오류는 `ReadWriteMany` 액세스 모드를 지원하지 않는 스토리지 솔루션에 표시될 수 있습니다. |

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 OpenShift CLI()에 로그인했습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 PVC와 관련된 이벤트를 검사합니다.

```shell-session
$ oc describe pvc <pvc_name>
```

1. `<pvc_name>` 을 PVC 이름으로 바꿉니다.

문제가 발생하는 호스트에 대한 직접 연결을 설정합니다.

디스크 문제를 해결합니다.

다음 단계

디스크 문제를 해결한 후에도 볼륨 오류 메시지가 유지되거나 재귀되는 경우 강제 정리를 수행해야 합니다. 자세한 내용은 "Performing a forced clean-up"을 참조하십시오.

추가 리소스

강제 정리 수행

#### 5.4.17.5. 강제 정리 수행

문제 해결 절차를 완료한 후에도 디스크 또는 노드 관련 문제가 지속되는 경우 강제 정리를 수행해야 합니다. 강제 정리는 영구 문제를 해결하고 LVM(Logical Volume Manager) 스토리지의 적절한 기능을 확인하는 데 사용됩니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 OpenShift CLI()에 로그인했습니다.

```shell
oc
```

LVM 스토리지를 사용하여 생성된 모든 PVC(영구 볼륨 클레임)를 삭제했습니다.

LVM 스토리지를 사용하여 생성된 PVC를 사용하는 Pod를 중지했습니다.

프로세스

다음 명령을 실행하여 LVM Storage Operator를 설치한 네임스페이스로 전환합니다.

```shell-session
$ oc project <namespace>
```

다음 명령을 실행하여 `LogicalVolume` CR(사용자 정의 리소스)이 있는지 확인합니다.

```shell-session
$ oc get logicalvolume
```

`LogicalVolume` CR이 있는 경우 다음 명령을 실행하여 해당 CR을 삭제합니다.

```shell-session
$ oc delete logicalvolume <name>
```

1. & `lt;name&` gt;을 `LogicalVolume` CR의 이름으로 바꿉니다.

`LogicalVolume` CR을 삭제한 후 다음 명령을 실행하여 종료자를 제거합니다.

```shell-session
$ oc patch logicalvolume <name> -p '{"metadata":{"finalizers":[]}}' --type=merge
```

1. & `lt;name&` gt;을 `LogicalVolume` CR의 이름으로 바꿉니다.

다음 명령을 실행하여 `LVMVolumeGroup` CR이 있는지 확인합니다.

```shell-session
$ oc get lvmvolumegroup
```

`LVMVolumeGroup` CR이 있는 경우 다음 명령을 실행하여 해당 CR을 삭제합니다.

```shell-session
$ oc delete lvmvolumegroup <name>
```

1. & `lt;name&` gt;을 `LVMVolumeGroup` CR의 이름으로 바꿉니다.

`LVMVolumeGroup` CR을 삭제한 후 다음 명령을 실행하여 종료자를 제거합니다.

```shell-session
$ oc patch lvmvolumegroup <name> -p '{"metadata":{"finalizers":[]}}' --type=merge
```

1. & `lt;name&` gt;을 `LVMVolumeGroup` CR의 이름으로 바꿉니다.

다음 명령을 실행하여 `LVMVolumeGroupNodeStatus` CR을 삭제합니다.

```shell-session
$ oc delete lvmvolumegroupnodestatus --all
```

다음 명령을 실행하여 `LVMCluster` CR을 삭제합니다.

```shell-session
$ oc delete lvmcluster --all
```

`LVMCluster` CR을 삭제한 후 다음 명령을 실행하여 종료자를 제거합니다.

```shell-session
$ oc patch lvmcluster <name> -p '{"metadata":{"finalizers":[]}}' --type=merge
```

1. & `lt;name&` gt;을 `LVMCluster` CR의 이름으로 바꿉니다.

### 6.1. CSI 볼륨 구성

CSI(Container Storage Interface)를 사용하면 OpenShift Container Platform이 CSI 인터페이스 를 영구 스토리지로 구현하는 스토리지 백엔드에서 스토리지를 사용할 수 있습니다.

참고

OpenShift Container Platform 4.20은 CSI 사양 의 버전 1.6.0을 지원합니다.

#### 6.1.1. CSI 아키텍처

[FIGURE src="/playbooks/wiki-assets/full_rebuild/storage/csi-arch-rev1.png" alt="CSI 구성 요소의 아키텍처" kind="diagram" diagram_type="semantic_diagram"]
CSI 구성 요소의 아키텍처
[/FIGURE]

_Source: `storage.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Storage-ko-KR/images/8984f70396bee6fae4a769322f541eab/csi-arch-rev1.png`_


CSI 드라이버는 일반적으로 컨테이너 이미지로 제공됩니다. 이러한 컨테이너는 OpenShift Container Platform이 실행되는 위치를 인식하지 못합니다. OpenShift Container Platform에서 CSI 호환 스토리지 백엔드를 사용하려면 클러스터 관리자가 OpenShift Container Platform과 스토리지 드라이버 간의 브리지 역할을 하는 여러 구성 요소를 배포해야 합니다.

다음 다이어그램에서는 OpenShift Container Platform 클러스터의 Pod에서 실행되는 구성 요소에 대한 상위 수준 개요를 설명합니다.

다른 스토리지 백엔드에 대해 여러 CSI 드라이버를 실행할 수 있습니다. 각 드라이버에는 드라이버 및 CSI 등록 기관과 함께 자체 외부 컨트롤러 배포 및 데몬 세트가 필요합니다.

#### 6.1.1.1. 외부 CSI 컨트롤러

외부 CSI 컨트롤러는 5개의 컨테이너가 있는 하나 이상의 Pod를 배포하는 배포입니다.

snapshotter 컨테이너는 `VolumeSnapshot` 및 `VolumeSnapshotContent` 오브젝트를 감시하고 `VolumeSnapshotContent` 오브젝트를 생성 및 삭제해야 합니다.

resizer 컨테이너는 `PersistentVolumeClaim` 업데이트를 감시하고 `PersistentVolumeClaim` 오브젝트에 더 많은 스토리지를 요청하는 경우 CSI 끝점에 대해 `ControllerExpandVolume` 작업을 트리거하는 사이드카 컨테이너입니다.

외부 CSI 연결 컨테이너는 OpenShift Container Platform의 `attach` 및 `detach` 호출을 CSI 드라이버에 대한 각 `ControllerPublish` 및 `ControllerUnpublish` 호출로 변환합니다.

OpenShift Container Platform으로부터의 `provision` 및 `delete` 호출을 CSI 드라이버의 해당 `CreateVolume` 및 `DeleteVolume` 호출로 변환하는 외부 CSI 프로비저너 컨테이너입니다.

CSI 드라이버 컨테이너입니다.

CSI 연결 및 CSI 프로비저너 컨테이너는 UNIX 도메인 소켓을 사용해 CSI 드라이버 컨테이너와 통신하여 CSI 통신이 Pod를 종료하지 않도록 합니다. Pod 외부에서 CSI 드라이버에 액세스할 수 없습니다.

참고

`attach`, `detach`, `provision`, `delete` 작업에는 일반적으로 스토리지 백엔드에 인증 정보를 사용하려면 CSI 드라이버가 필요합니다. 컴퓨팅 노드의 심각한 보안 위반 시 인증 정보가 사용자 프로세스에 유출되지 않도록 인프라 노드에서 CSI 컨트롤러 Pod를 실행합니다.

참고

외부 연결에서는 타사 `attach` 또는 `detach` 작업을 지원하지 않는 CSI 드라이버에서도 실행해야 합니다. 외부 연결은 CSI 드라이버에 `ControllerPublish` 또는 `ControllerUnpublish` 작업을 발행하지 않습니다. 그러나 필요한 OpenShift Container Platform 연결 API를 구현하려면 실행해야 합니다.

#### 6.1.1.2. CSI 드라이버 데몬 세트

CSI 드라이버 데몬 세트는 OpenShift Container Platform이 CSI 드라이버에서 제공한 스토리지를 노드에 마운트하고 사용자 워크로드(Pod)에서 PV(영구 볼륨)로 사용할 수 있는 모든 노드에서 Pod를 실행합니다. CSI 드라이버가 설치된 Pod에는 다음 컨테이너가 포함되어 있습니다.

CSI 드라이버 등록 기관. CSI 드라이버를 노드에서 실행 중인 `openshift-node` 서비스에 등록합니다. 노드에서 실행되는 `openshift-node` 프로세스는 노드에서 사용 가능한 UNIX 도메인 소켓을 사용하여 CSI 드라이버와 직접 연결합니다.

CSI 드라이버.

노드에 배포된 CSI 드라이버는 스토리지 백엔드에 최대한 적은 수의 인증 정보가 있어야 합니다. 이러한 호출이 구현된 경우 OpenShift Container Platform은 `NodePublish` / `NodeUnpublish` 및 `NodeStage` / `NodeUnstage` 와 같은 CSI 호출의 노드 플러그인 세트만 사용합니다.

#### 6.1.2. OpenShift Container Platform에서 지원되는 CSI 드라이버

OpenShift Container Platform은 기본적으로 특정 CSI 드라이버를 설치하여 in-tree 볼륨 플러그인에서 사용할 수 없는 사용자 스토리지 옵션을 제공합니다.

지원되는 스토리지 자산에 마운트된 CSI 프로비저닝 영구 볼륨을 생성하기 위해 OpenShift Container Platform은 기본적으로 필요한 CSI 드라이버 Operator, CSI 드라이버 및 필요한 스토리지 클래스를 설치합니다. Operator 및 드라이버의 기본 네임스페이스에 대한 자세한 내용은 특정 CSI Driver Operator 설명서를 참조하십시오.

중요

AWS EFS 및 GCP Filestore CSI 드라이버는 기본적으로 설치되지 않으며 수동으로 설치해야 합니다. AWS EFS CSI 드라이버 설치에 대한 자세한 내용은 AWS Elastic File Service CSI Driver Operator 설정을 참조하십시오. GCP Filestore CSI 드라이버 설치에 대한 자세한 내용은 Google Compute Platform Filestore CSI Driver Operator 를 참조하십시오.

다음 표에서는 OpenShift Container Platform에서 지원하는 OpenShift Container Platform과 함께 설치된 CSI 드라이버와 볼륨 스냅샷 및 크기와 같은 CSI 기능을 설명합니다.

중요

다음 표에 CSI 드라이버가 나열되지 않은 경우 지원되는 CSI 기능을 사용하려면 CSI 스토리지 벤더가 제공한 설치 지침을 따라야 합니다.

타사 인증 CSI 드라이버 목록은 추가 리소스 에서 Red Hat 에코시스템 포털 을 참조하십시오.

| CSI 드라이버 | CSI 볼륨 스냅샷 | CSI 볼륨 그룹 스냅샷 [1] | CSI 복제 | CSI 크기 조정 | 인라인 임시 볼륨 |
| --- | --- | --- | --- | --- | --- |
| AWS EBS | ✅ |  |  | ✅ |  |
| AWS EFS |  |  |  |  |  |
| GCP(Google Compute Platform) PD(영구 디스크) | ✅ |  | ✅ [2] | ✅ |  |
| GCP 파일 저장소 | ✅ |  |  | ✅ |  |
| IBM Power® Virtual Server Block |  |  |  | ✅ |  |
| IBM Cloud® Block | ✅ [3] |  |  | ✅ [3] |  |
| LVM 스토리지 | ✅ |  | ✅ | ✅ |  |
| Microsoft Azure Disk | ✅ |  | ✅ | ✅ |  |
| Microsoft Azure Stack Hub | ✅ |  | ✅ | ✅ |  |
| Microsoft Azure File | ✅ [4] |  | ✅ [4] | ✅ | ✅ |
| OpenStack Cinder | ✅ |  | ✅ | ✅ |  |
| OpenShift Data Foundation | ✅ | ✅ | ✅ | ✅ |  |
| OpenStack Manila | ✅ |  |  | ✅ |  |
| 공유 리소스 |  |  |  |  | ✅ |
| CIFS/SMB |  |  | ✅ |  |  |
| VMware vSphere | ✅ [5] |  |  | ✅ [6] |  |

1.

중요

CSI 볼륨 그룹 스냅샷은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

2.

스토리지 풀이 있는 하이퍼 디스크 분산 디스크에서 복제가 지원되지 않습니다.

3.

오프라인 스냅샷 또는 크기 조정을 지원하지 않습니다. 볼륨은 실행 중인 Pod에 연결해야 합니다.

4.

Azure 파일 복제는 NFS 프로토콜을 지원하지 않습니다. SMB 프로토콜을 사용하는 `azurefile-csi` 스토리지 클래스를 지원합니다.

Azure File 복제 및 스냅샷은 기술 프리뷰 기능입니다.

중요

Azure File CSI 복제 및 스냅샷은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

5.

vCenter Server 및 ESXi 모두에 vSphere 버전 8.0 업데이트 1 이상이 필요합니다.

fileshare 볼륨을 지원하지 않습니다.

6.

온라인 확장은 vSphere 버전 8.0 업데이트 1 이상에서 지원됩니다.

추가 리소스

Red Hat 에코시스템 포털

타사 지원 정책

#### 6.1.3. 동적 프로비저닝

영구 스토리지의 동적 프로비저닝은 CSI 드라이버 및 기본 스토리지 백엔드의 기능에 따라 달라집니다. CSI 드라이버 공급자는 OpenShift Container Platform에서 스토리지 클래스와 구성에 사용 가능한 매개변수를 생성하는 방법을 설명해야 합니다.

동적 프로비저닝을 사용하도록 생성된 스토리지 클래스를 구성할 수 있습니다.

절차

설치된 CSI 드라이버에서 특수 스토리지 클래스가 필요하지 않은 모든 PVC를 프로비저닝하는 기본 스토리지 클래스를 생성합니다.

```plaintext
# oc create -f - << EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <storage-class>
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: <provisioner-name>
parameters:
  csi.storage.k8s.io/fstype: xfs
EOF
```

1. 생성할 스토리지 클래스의 이름입니다.

2. 설치된 CSI 드라이버의 이름입니다.

3. vSphere CSI 드라이버는 XFS 및 Ext4를 포함하여 기본 Red Hat Core 운영 체제 릴리스에서 지원하는 모든 파일 시스템을 지원합니다.

#### 6.1.4. CSI 드라이버 사용 예

다음 예시는 템플릿을 변경하지 않고 기본 MySQL 템플릿을 설치합니다.

사전 요구 사항

CSI 드라이버가 배포되었습니다.

동적 프로비저닝을 위해 스토리지 클래스가 생성되었습니다.

절차

MySQL 템플릿을 생성합니다.

```shell-session
# oc new-app mysql-persistent
```

```shell-session
--> Deploying template "openshift/mysql-persistent" to project default
...
```

```shell-session
# oc get pvc
```

```shell-session
NAME              STATUS    VOLUME                                   CAPACITY
ACCESS MODES   STORAGECLASS   AGE
mysql             Bound     kubernetes-dynamic-pv-3271ffcb4e1811e8   1Gi
RWO            cinder         3s
```

### 6.2. CSI 인라인 임시 볼륨

CSI(Container Storage Interface) 인라인 임시 볼륨을 사용하여 `Pod` 가 배포되고 Pod가 제거될 때 인라인 임시 볼륨을 생성하는 Pod 사양을 정의할 수 있습니다.

이 기능은 지원되는 CSI(Container Storage Interface) 드라이버에서만 사용할 수 있습니다.

Azure File CSI 드라이버

보안 저장소 CSI 드라이버

#### 6.2.1. CSI 인라인 임시 볼륨 개요

일반적으로 CSI(Container Storage Interface) 드라이버에서 지원하는 볼륨은 `PersistentVolume` 및 `PersistentVolumeClaim` 오브젝트 조합에서만 사용할 수 있습니다.

이 기능을 사용하면 `PersistentVolume` 오브젝트가 아닌 `Pod` 사양에 직접 CSI 볼륨을 지정할 수 있습니다. 인라인 볼륨은 임시 볼륨이며 Pod를 다시 시작하면 유지되지 않습니다.

#### 6.2.1.1. 지원 제한

중요

이제 Red Hat OpenShift 1.1 빌드 에서 공유 리소스 CSI 드라이버 기능을 사용할 수 있습니다. 이 기능은 이제 OpenShift Container Platform 4.18 이상에서 제거되었습니다. 이 기능을 사용하려면 Red Hat OpenShift 1.1 이상에서 빌드를 사용하고 있는지 확인합니다.

기본적으로 OpenShift Container Platform에서는 다음과 같은 제한이 있는 CSI 인라인 임시 볼륨을 지원합니다.

CSI 드라이버에서만 지원을 사용할 수 있습니다. In-tree 및 FlexVolumes는 지원되지 않습니다.

커뮤니티 또는 스토리지 벤더는 이러한 볼륨을 지원하는 다른 CSI 드라이버를 제공합니다. CSI 드라이버 공급자가 제공하는 설치 지침을 따르십시오.

CSI 드라이버는 `임시` 용량을 포함하여 인라인 볼륨 기능을 구현하지 못할 수 있습니다. 자세한 내용은 CSI 드라이버 설명서를 참조하십시오.

#### 6.2.2. CSI 볼륨 Admission 플러그인

CSI(Container Storage Interface) 볼륨 Admission 플러그인을 사용하면 Pod 승인 시 CSI 볼륨을 프로비저닝할 수 있는 개별 CSI 드라이버 사용을 제한할 수 있습니다. 관리자는 `csi-ephemeral-volume-profile` 레이블을 추가할 수 있으며 이 레이블은 Admission 플러그인에서 검사하고 시행, 경고 및 감사 결정에 사용됩니다.

#### 6.2.2.1. 개요

관리자는 CSI 볼륨 Admission 플러그인을 사용하기 위해 다음 예와 같이 CSI 드라이버의 유효 Pod 보안 프로필을 선언하는 `CSIDriver` 오브젝트에 `security.openshift.io/csi-ephemeral-volume-profile` 라벨을 추가합니다.

```yaml
kind: CSIDriver
metadata:
  name: csi.mydriver.company.org
  labels:
    security.openshift.io/csi-ephemeral-volume-profile: restricted
```

1. `csi-ephemeral-volume-profile` 라벨을 "제한된"으로 설정된 CSI 드라이버 오브젝트 YAML 파일

이 "효율 프로파일"은 Pod의 네임스페이스가 Pod 보안 표준에 의해 관리될 때 Pod에서 CSI 드라이버를 사용하여 CSI 임시 볼륨을 마운트할 수 있다고 통신합니다.

CSI 볼륨 Admission 플러그인은 Pod가 생성되면 Pod 볼륨을 검사합니다. CSI 볼륨을 사용하는 기존 Pod는 영향을 받지 않습니다. Pod에서 CSI(Container Storage Interface) 볼륨을 사용하는 경우 플러그인은 `CSIDriver` 오브젝트를 조회하고 `csi-ephemeral-volume-profile` 라벨을 검사한 다음 적용, 경고 및 감사 결정에 레이블의 값을 사용합니다.

#### 6.2.2.2. Pod 보안 프로필 적용

CSI 드라이버에 `csi-ephemeral-volume-profile` 레이블이 있는 경우 CSI 드라이버를 사용하여 CSI 드라이버를 사용하여 CSI 임시 볼륨을 마운트하는 Pod는 Pod 보안 표준을 동일한 권한 이상으로 적용하는 네임스페이스에서 실행해야 합니다. 네임스페이스가 보다 제한적인 표준을 적용하는 경우 CSI 볼륨 Admission 플러그인에서 허용을 거부합니다. 다음 표에서는 지정된 라벨 값에 대한 다양한 Pod 보안 프로필에 대한 적용 동작을 설명합니다.

| Pod 보안 프로필 | 드라이버 레이블: restricted | 드라이버 레이블: baseline | 드라이버 레이블: privileged |
| --- | --- | --- | --- |
| restricted | Allowed | Denied | Denied |
| 기준 | Allowed | Allowed | Denied |
| privileged | Allowed | Allowed | Allowed |

#### 6.2.2.3. Pod 보안 프로필 경고

CSI 볼륨 Admission 플러그인은 CSI 드라이버의 유효 프로필이 Pod 네임스페이스에 대한 Pod 보안 경고 프로필보다 더 허용되는 경우 경고할 수 있습니다. 다음 표는 지정된 라벨 값에 대해 다양한 Pod 보안 프로필에 대한 경고가 발생하는 경우를 보여줍니다.

| Pod 보안 프로필 | 드라이버 레이블: restricted | 드라이버 레이블: baseline | 드라이버 레이블: privileged |
| --- | --- | --- | --- |
| restricted | No warning | Warning | Warning |
| 기준 | No warning | No warning | Warning |
| privileged | No warning | No warning | No warning |

#### 6.2.2.4. Pod 보안 프로필 감사

CSI 드라이버의 유효 프로필이 Pod 네임스페이스의 Pod 보안 감사 프로필보다 더 많은 경우 CSI 볼륨 Admission 플러그인은 Pod에 감사 주석을 적용할 수 있습니다. 다음 표는 지정된 라벨 값에 대해 다양한 Pod 보안 프로필에 적용되는 audit 주석을 보여줍니다.

| Pod 보안 프로필 | 드라이버 레이블: restricted | 드라이버 레이블: baseline | 드라이버 레이블: privileged |
| --- | --- | --- | --- |
| restricted | No audit | Audit | Audit |
| 기준 | No audit | No audit | Audit |
| privileged | No audit | No audit | No audit |

#### 6.2.2.5. CSI 볼륨 Admission 플러그인의 기본 동작

CSI 임시 볼륨에 대해 참조된 CSI 드라이버에 `csi-ephemeral-volume-profile` 레이블이 없는 경우 CSI 볼륨 Admission 플러그인은 드라이버에 적용, 경고 및 감사 동작을 위한 권한 있는 프로필이 있는 것으로 간주합니다. 마찬가지로 Pod의 네임스페이스에 Pod 보안 승인 라벨이 설정되지 않은 경우 Admission 플러그인은 restricted 프로필이 적용, 경고 및 감사 결정에 허용되는 것으로 간주합니다. 따라서 라벨이 설정되지 않은 경우 기본적으로 해당 CSI 드라이버를 사용하는 CSI 임시 볼륨은 권한 있는 네임스페이스에서만 사용할 수 있습니다.

OpenShift Container Platform과 함께 제공되고 임시 볼륨을 지원하는 CSI 드라이버에는 `csi-ephemeral-volume-profile` 라벨에 적절한 기본값이 설정되어 있습니다.

Azure File CSI 드라이버: privileged

필요한 경우 관리자는 레이블의 기본값을 변경할 수 있습니다.

#### 6.2.3. Pod 사양에 CSI 인라인 임시 볼륨 포함

OpenShift Container Platform의 `Pod` 사양에 CSI 인라인 임시 볼륨을 포함할 수 있습니다. 런타임 시 중첩된 인라인 볼륨은 관련 Pod의 임시 라이프사이클을 따라 CSI 드라이버가 Pod를 생성 및 삭제할 때 볼륨 작업의 모든 단계를 처리합니다.

절차

`Pod` 오브젝트 정의를 생성하여 파일에 저장합니다.

파일에 CSI 인라인 임시 볼륨을 삽입합니다.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: my-csi-app
spec:
  containers:
    - name: my-frontend
      image: busybox
      volumeMounts:
      - mountPath: "/data"
        name: my-csi-inline-vol
      command: [ "sleep", "1000000" ]
  volumes:
    - name: my-csi-inline-vol
      csi:
        driver: inline.storage.kubernetes.io
        volumeAttributes:
          foo: bar
```

1. 풀에서 사용되는 볼륨의 이름입니다.

이전 단계에서 저장한 오브젝트 정의 파일을 생성합니다.

```shell-session
$ oc create -f my-csi-app.yaml
```

#### 6.2.4. 추가 리소스

Pod 보안 표준

### 6.3. CSI 볼륨 스냅샷

이 문서에서는 지원되는 CSI(Container Storage Interface) 드라이버로 볼륨 스냅샷을 사용하여 OpenShift Container Platform의 데이터 손실을 보호하는 방법을 설명합니다. 영구 볼륨에 대해 숙지하는 것이 좋습니다.

#### 6.3.1. CSI 볼륨 스냅샷 개요

스냅샷 은 특정 시점에서 클러스터의 스토리지 볼륨 상태를 나타냅니다. 볼륨 스냅샷을 사용하여 새 볼륨을 프로비저닝할 수 있습니다.

OpenShift Container Platform은 기본적으로 CSI(Container Storage Interface) 볼륨 스냅샷을 지원합니다. 그러나 특정 CSI 드라이버가 필요합니다.

CSI 볼륨 스냅샷을 사용하면 클러스터 관리자가 다음을 수행할 수 있습니다.

스냅샷을 지원하는 타사 CSI 드라이버를 배포합니다.

기존 볼륨 스냅샷에서 새 PVC(영구 볼륨 클레임)를 생성합니다.

기존 PVC의 스냅샷을 가져옵니다.

스냅샷을 다른 PVC로 복원합니다.

기존 VM 스냅샷을 삭제합니다.

CSI 볼륨 스냅샷을 사용하면 앱 개발자가 다음을 수행할 수 있습니다.

애플리케이션 또는 클러스터 수준의 스토리지 백업 솔루션을 개발하기 위한 볼륨 스냅샷을 빌드 블록으로 사용할 수 있습니다.

빠르게 이전 개발 버전으로 롤백할 수 있습니다.

시간마다 전체 복사를 하지 않고 스토리지를 보다 효율적으로 사용할 수 있습니다.

볼륨 스냅샷을 사용할 때는 다음에 유의하십시오.

CSI 드라이버에서만 지원을 사용할 수 있습니다. In-tree 및 FlexVolumes는 지원되지 않습니다.

OpenShift Container Platform은 일부 CSI 드라이버만 제공됩니다. OpenShift Container Platform Driver Operator가 제공하지 않는 CSI 드라이버의 경우 커뮤니티 또는 스토리지 공급 업체에서 제공하는 CSI 드라이버를 사용하는 것이 좋습니다. CSI 드라이버 공급자가 제공하는 설치 지침을 따릅니다.

CSI 드라이버는 볼륨 스냅샷 기능을 구현하거나 사용하지 않을 수 있습니다. 볼륨 스냅샷을 지원하는 CSI 드라이버는 `csi-external-snapshotter` 사이드카를 사용할 수 있습니다. 자세한 내용은 CSI 드라이버에서 제공하는 설명서를 참조하십시오.

#### 6.3.2. CSI 스냅샷 컨트롤러 및 사이드카

OpenShift Container Platform은 컨트롤 플레인에 배포된 스냅샷 컨트롤러를 제공합니다. 또한, CSI 드라이버 벤더는 CSI 드라이버 설치 중에 설치된 Helper 컨테이너로 CSI 스냅샷 사이드카를 제공합니다.

CSI 스냅샷 컨트롤러 및 사이드카는 OpenShift Container Platform API를 통해 볼륨 스냅샷을 제공합니다. 이러한 외부 구성 요소는 클러스터에서 실행됩니다.

외부 컨트롤러는 CSI Snapshot Controller Operator에 의해 배포됩니다.

#### 6.3.2.1. 외부 컨트롤러

CSI 스냅샷 컨트롤러는 `VolumeSnapshot` 및 `VolumeSnapshotContent` 오브젝트를 바인딩합니다. 컨트롤러는 `VolumeSnapshotContent` 오브젝트를 생성 및 삭제하여 동적 프로비저닝을 관리합니다.

#### 6.3.2.2. 외부 사이드카

CSI 드라이버 벤더는 `csi-external-snapshotter` 사이드카를 제공합니다. 이 컨테이너는 CSI 드라이버와 함께 배포된 별도의 Helper 컨테이너입니다. 사이드카는 `CreateSnapshot` 및 `DeleteSnapshot` 작업을 트리거하여 스냅샷을 관리합니다. 벤더가 제공하는 설치 지침을 따르십시오.

#### 6.3.3. CSI Snapshot Controller Operator 정보

CSI Snapshot Controller Operator는 `openshift-cluster-storage-operator` 네임스페이스에서 실행됩니다. 기본적으로 모든 클러스터에 CVO(Cluster Version Operator)에 의해 설치됩니다.

CSI Snapshot Controller Operator는 `openshift-cluster-storage-operator` 네임스페이스에서 실행되는 CSI 스냅샷 컨트롤러를 설치합니다.

#### 6.3.3.1. 볼륨 스냅샷 CRD

OpenShift Container Platform을 설치하는 동안 CSI Snapshot Controller Operator는 `snapshot.storage.k8s.io/v1` API 그룹에 다음 스냅샷 CRD(사용자 정의 리소스 정의)를 생성합니다.

`VolumeSnapshotContent`

클러스터 관리자가 프로비저닝한 클러스터의 볼륨으로 가져온 스냅샷입니다.

`PersistentVolume` 오브젝트와 유사하게 `VolumeSnapshotContent` CRD는 스토리지 백엔드의 실제 스냅샷을 가리키는 클러스터 리소스입니다.

수동으로 프로비저닝된 스냅샷의 경우 클러스터 관리자는 여러 `VolumeSnapshotContent` CRD를 생성합니다. 이는 스토리지 시스템의 실제 볼륨 스냅샷에 대한 세부 정보를 제공합니다.

`VolumeSnapshotContent` CRD는 네임스페이스가 제공되지 않으며 클러스터 관리자가 사용합니다.

`VolumeSnapshot`

`PersistentVolumeClaim` 오브젝트와 유사하게 `VolumeSnapshot CRD는` 스냅샷에 대한 개발자 요청을 정의합니다. CSI Snapshot Controller Operator는 CSI 스냅샷 컨트롤러를 실행하여 `VolumeSnapshot` CRD의 바인딩을 적절한 `VolumeSnapshotContent` CRD로 처리합니다. 바인딩은 일대일 매핑입니다.

`VolumeSnapshot CRD` 에는 네임스페이스가 지정됩니다. 개발자는 CRD를 스냅샷에 대한 개별 요청으로 사용합니다.

`VolumeSnapshotClass`

클러스터 관리자는 `VolumeSnapshot` 오브젝트에 속한 다른 속성을 지정할 수 있습니다. 이러한 속성은 스토리지 시스템에서 동일한 볼륨에서 가져온 스냅샷과 다를 수 있으며, 이 경우 영구 볼륨 클레임의 동일한 스토리지 클래스를 사용하여 표시하지 않을 수 있습니다.

`VolumeSnapshotClass CRD` 는 스냅샷을 생성할 때 사용할 `csi-external-snapshotter` 사이드카에 대한 매개변수를 정의합니다. 이를 통해 여러 옵션이 지원되는 경우 스토리지 백엔드가 어떤 종류의 스냅샷을 동적으로 생성할지 알 수 있습니다.

동적으로 프로비저닝된 스냅샷은 `VolumeSnapshotClass` CRD를 사용하여 스냅샷을 생성할 때 사용할 스토리지에서 제공되는 특정 매개변수를 지정합니다.

`VolumeSnapshotContentClass` CRD에는 네임스페이스가 지정되지 않으며, 클러스터 관리자가 사용하여 스토리지 백엔드에 대한 글로벌 구성 옵션을 활성화하기 위한 용도입니다.

#### 6.3.4. 볼륨 스냅샷 프로비저닝

스냅샷을 프로비저닝하는 방법은 동적으로 수동의 두 가지가 있습니다.

#### 6.3.4.1. 동적 프로비저닝

기존 스냅샷을 사용하는 대신 영구 볼륨 클레임에서 스냅샷을 동적으로 수락하도록 요청할 수 있습니다. 매개변수는 `VolumeSnapshotClass` CRD를 사용하여 지정됩니다.

#### 6.3.4.2. 수동 프로비저닝

클러스터 관리자는 여러 `VolumeSnapshotContent` 오브젝트를 수동으로 사전 프로비저닝할 수 있습니다. 이를 통해 클러스터 사용자가 사용할 수 있는 실제 볼륨 스냅샷 세부 정보가 제공됩니다.

#### 6.3.5. 볼륨 스냅샷 생성

`VolumeSnapshot` 오브젝트를 생성할 때 OpenShift Container Platform은 볼륨 스냅샷을 생성합니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인합니다.

`VolumeSnapshot` 오브젝트를 지원하는 CSI 드라이버를 사용하여 생성된 PVC입니다.

스토리지 백엔드를 프로비저닝하는 스토리지 클래스입니다.

스냅샷을 사용하려는 PVC(영구 볼륨 클레임)를 사용하는 Pod가 없습니다.

주의

Pod에서 사용 중인 PVC의 볼륨 스냅샷을 생성하면 기록되지 않은 데이터와 캐시된 데이터가 스냅샷에서 제외될 수 있습니다. 모든 데이터가 디스크에 기록되도록 하려면 스냅샷을 생성하기 전에 PVC를 사용하는 Pod를 삭제합니다.

프로세스

볼륨 스냅샷을 동적으로 생성하려면 다음을 수행합니다.

다음 YAML로 설명된 `VolumeSnapshotClass` 오브젝트로 파일을 생성합니다.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-hostpath-snap
driver: hostpath.csi.k8s.io
deletionPolicy: Delete
```

1. 이 `VolumeSnapshotClass` 오브젝트의 스냅샷을 생성하는 데 사용되는 CSI 드라이버의 이름입니다. 이름은 스냅샷을 수행 중인 PVC를 담당하는 스토리지 클래스의 `Provisioner` 필드와 동일해야 합니다.

참고

영구 스토리지를 구성하는 데 사용한 드라이버에 따라 추가 매개변수가 필요할 수 있습니다. 기존 `VolumeSnapshotClass` 오브젝트를 사용할 수도 있습니다.

다음 명령을 입력하여 이전 단계에서 저장한 오브젝트를 생성합니다.

```shell-session
$ oc create -f volumesnapshotclass.yaml
```

`VolumeSnapshot` 오브젝트를 생성합니다.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysnap
spec:
  volumeSnapshotClassName: csi-hostpath-snap
  source:
    persistentVolumeClaimName: myclaim
```

1. 볼륨 스냅샷의 특정 클래스에 대한 요청입니다. `volumeSnapshotClassName` 설정이 없으며 기본 볼륨 스냅샷 클래스가 있는 경우 기본 볼륨 스냅샷 클래스 이름을 사용하여 스냅샷이 생성됩니다. 그러나 필드가 없으며 기본 볼륨 스냅샷 클래스가 없는 경우에는 스냅샷이 생성되지 않습니다.

2. 영구 볼륨에 바인딩된 `PersistentVolumeClaim` 오브젝트의 이름입니다. 이 명령은 스냅샷을 생성할 대상을 정의합니다. 스냅샷을 동적으로 프로비저닝하는 데 필요합니다.

다음 명령을 입력하여 이전 단계에서 저장한 오브젝트를 생성합니다.

```shell-session
$ oc create -f volumesnapshot-dynamic.yaml
```

스냅샷을 수동으로 프로비저닝하려면 다음을 수행합니다.

위에서 설명한 볼륨 스냅샷 클래스를 정의하는 것 외에도 `volumeSnapshotContentName` 매개변수 값을 스냅샷의 소스로 제공해야 합니다.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: snapshot-demo
spec:
  source:
    volumeSnapshotContentName: mycontent
```

1. 사전 프로비저닝된 스냅샷에는 `volumeSnapshotContentName` 매개변수가 필요합니다.

다음 명령을 입력하여 이전 단계에서 저장한 오브젝트를 생성합니다.

```shell-session
$ oc create -f volumesnapshot-manual.yaml
```

검증

클러스터에서 스냅샷을 생성한 후 스냅샷에 대한 추가 세부 정보를 사용할 수 있습니다.

생성된 볼륨 스냅샷에 대한 세부 정보를 표시하려면 다음 명령을 입력합니다.

```shell-session
$ oc describe volumesnapshot mysnap
```

다음 예시는 `mysnap` 볼륨 스냅샷에 대한 세부 정보를 표시합니다.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: mysnap
spec:
  source:
    persistentVolumeClaimName: myclaim
  volumeSnapshotClassName: csi-hostpath-snap
status:
  boundVolumeSnapshotContentName: snapcontent-1af4989e-a365-4286-96f8-d5dcd65d78d6
  creationTime: "2020-01-29T12:24:30Z"
  readyToUse: true
  restoreSize: 500Mi
```

1. 컨트롤러가 생성한 실제 스토리지 콘텐츠의 포인터입니다.

2. 스냅샷이 생성된 시간입니다. 스냅샷에는 이 표시된 시점에서 사용 가능한 볼륨 내용이 포함되어 있습니다.

3. 값을 `true` 로 설정하면 스냅샷을 사용하여 새 PVC로 복원할 수 있습니다. 값을 `false` 로 설정하면 스냅샷이 생성됩니다. 하지만 스토리지 백엔드는 스냅샷을 사용할 수 있도록 추가 작업을 수행하여 새 볼륨으로 복원해야 합니다. 예를 들어, Amazon Elastic Block Store 데이터를 다른 저렴한 위치로 이동할 수 있으며, 이 작업에는 몇 분이 걸릴 수 있습니다.

볼륨 스냅샷이 생성되었는지 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get volumesnapshotcontent
```

실제 컨텐츠에 대한 포인터가 표시됩니다. `boundVolumeSnapshotContentName` 필드가 입력된 경우 `VolumeSnapshotContent` 오브젝트가 존재하고 스냅샷이 생성된 것입니다.

스냅샷이 준비되었는지 확인하려면 `VolumeSnapshot` 오브젝트에 `readyToUse: true` 가 있는지 확인합니다.

#### 6.3.6. 볼륨 스냅샷 삭제

OpenShift Container Platform이 볼륨 스냅샷을 삭제하는 방법을 구성할 수 있습니다.

절차

다음 예와 같이 `VolumeSnapshotClass` 오브젝트에 필요한 삭제 정책을 지정합니다.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-hostpath-snap
driver: hostpath.csi.k8s.io
deletionPolicy: Delete
```

1. 볼륨 스냅샷을 삭제할 때 `Delete` 값이 설정되면 `VolumeSnapshotContent` 오브젝트와 함께 기본 스냅샷이 삭제됩니다. `Retain` 값이 설정된 경우 기본 스냅샷 및 `VolumeSnapshotContent` 오브젝트다 모두 유지됩니다.

`Retain` 값이 설정되고 해당 `VolumeSnapshotContent` 오브젝트를 삭제하지 않고 `VolumeSnapshot` 오브젝트가 삭제되면 해당 콘텐츠는 그대로 유지됩니다. 스냅샷 자체는 스토리지 백엔드에서도 유지됩니다.

다음 명령을 입력하여 볼륨 스냅샷을 삭제합니다.

```shell-session
$ oc delete volumesnapshot <volumesnapshot_name>
```

1. & lt;volumesnapshot_name >을 삭제하려는 볼륨 스냅샷의 이름으로 바꿉니다.

```shell-session
volumesnapshot.snapshot.storage.k8s.io "mysnapshot" deleted
```

삭제 정책이 `Retain` 으로 설정된 경우 다음 명령을 입력하여 볼륨 스냅샷 콘텐츠를 삭제합니다.

```shell-session
$ oc delete volumesnapshotcontent <volumesnapshotcontent_name>
```

1. & lt;volumesnapshotcontent_name& gt;을 삭제하려는 콘텐츠로 바꿉니다.

선택 사항: `VolumeSnapshot` 오브젝트가 성공적으로 삭제되지 않으면 삭제 작업이 계속될 수 있도록 다음 명령을 입력하여 남은 리소스의 종료자를 제거합니다.

중요

`VolumeSnapshot` 오브젝트에 대한 영구 볼륨 클레임 또는 볼륨 스냅샷 콘텐츠에서 기존 참조가 없음을 확신할 수 있는 경우에만 종료자를 제거하십시오. `--force` 옵션을 사용하면 모든 종료자가 제거될 때까지 삭제 작업에서 스냅샷 오브젝트를 삭제하지 않습니다.

```shell-session
$ oc patch -n $PROJECT volumesnapshot/$NAME --type=merge -p '{"metadata": {"finalizers":null}}'
```

```shell-session
volumesnapshotclass.snapshot.storage.k8s.io "csi-ocs-rbd-snapclass" deleted
```

종료자가 제거되고 볼륨 스냅샷이 삭제됩니다.

#### 6.3.7. 볼륨 스냅샷 복원

`VolumeSnapshot` CRD 콘텐츠를 사용하여 기존 볼륨을 이전 상태로 복원할 수 있습니다.

`VolumeSnapshot` CRD가 바인딩되고 `readyToUse` 값이 `true` 로 설정된 후 해당 리소스를 사용하여 스냅샷의 데이터로 미리 채워진 새 볼륨을 프로비저닝할 수 있습니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인합니다.

볼륨 스냅샷을 지원하는 CSI(Container Storage Interface) 드라이버를 사용하여 생성된 PVC(영구 볼륨 클레임)입니다.

스토리지 백엔드를 프로비저닝하는 스토리지 클래스입니다.

볼륨 스냅샷이 생성되어 사용할 준비가 되었습니다.

프로세스

다음과 같이 PVC에서 `VolumeSnapshot` 데이터 소스를 지정합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myclaim-restore
spec:
  storageClassName: csi-hostpath-sc
  dataSource:
    name: mysnap
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

1. 소스로 사용할 스냅샷을 나타내는 `VolumeSnapshot` 오브젝트의 이름입니다.

2. `VolumeSnapshot` 값으로 설정해야 합니다.

3. `snapshot.storage.k8s.io` 값으로 설정해야 합니다.

다음 명령을 입력하여 PVC를 생성합니다.

```shell-session
$ oc create -f pvc-restore.yaml
```

다음 명령을 입력하여 복원된 PVC가 생성되었는지 확인합니다.

```shell-session
$ oc get pvc
```

`myclaim-restore` 와 같은 새 PVC가 표시됩니다.

#### 6.3.8. vSphere의 최대 스냅샷 수 변경

vSphere CSI(Container Storage Interface)의 볼륨당 기본 최대 스냅샷 수는 3입니다. 볼륨당 최대 32개까지 변경할 수 있습니다.

그러나 스냅샷 최대값을 늘리려면 성능 장단점이 필요하므로 볼륨당 2~3개의 스냅샷만 사용할 수 있습니다.

자세한 VMware 스냅샷 성능 권장 사항은 추가 리소스를 참조하십시오.

사전 요구 사항

관리자 권한으로 클러스터에 액세스합니다.

프로세스

다음 명령을 실행하여 현재 시크릿을 확인합니다.

```shell-session
$ oc -n openshift-cluster-csi-drivers get secret/vsphere-csi-config-secret -o jsonpath='{.data.cloud\.conf}' | base64 -d
```

```shell-session
# Labels with topology values are added dynamically via operator
[Global]
cluster-id = vsphere-01-cwv8p

# Populate VCenters (multi) after here
[VirtualCenter "vcenter.openshift.com"]
insecure-flag           = true
datacenters             = DEVQEdatacenter
password                = "xxxxxxxx"
user                    = "xxxxxxxx@devcluster.openshift.com"
migration-datastore-url = ds:///vmfs/volumes/vsan:52c842f232751e0d-3253aadeac21ca82/
```

이 예에서는 글로벌 최대 스냅샷 수가 구성되지 않았으므로 기본값 3이 적용됩니다.

다음 명령을 실행하여 스냅샷 제한을 변경합니다.

글로벌 스냅샷 제한을 설정합니다.

```shell-session
$ oc patch clustercsidriver/csi.vsphere.vmware.com --type=merge -p '{"spec":{"driverConfig":{"vSphere":{"globalMaxSnapshotsPerBlockVolume": 10}}}}'

clustercsidriver.operator.openshift.io/csi.vsphere.vmware.com patched
```

이 예에서 글로벌 제한이 10(`globalMaxSnapshotsPerBlockVolume` 으로 설정)으로 변경됩니다.

가상 볼륨 스냅샷 제한을 설정합니다.

이 매개변수는 가상 볼륨 데이터 저장소에만 제한을 설정합니다. 가상 볼륨 최대 스냅샷 제한은 전역 제약 조건을 재정의하지만 설정되지 않은 경우 기본값은 글로벌 제한입니다.

```shell-session
$ oc patch clustercsidriver/csi.vsphere.vmware.com --type=merge -p '{"spec":{"driverConfig":{"vSphere":{"granularMaxSnapshotsPerBlockVolumeInVVOL": 5}}}}'
clustercsidriver.operator.openshift.io/csi.vsphere.vmware.com patched
```

이 예에서는 가상 볼륨 제한이 5로 변경되고 있습니다(`granularMaxSnapshotsPerBlockVolumeInVVOL` 을 5)로 설정합니다.

vSAN 스냅샷 제한을 설정합니다.

이 매개변수는 vSAN 데이터 저장소에만 제한을 설정합니다. 설정된 경우 vSAN 최대 스냅샷 제한이 전역 제약 조건을 덮어씁니다. 그러나 설정되지 않은 경우 기본값은 글로벌 제한입니다. vSAN ESA 설정에서 최대 32 값을 설정할 수 있습니다.

```shell-session
$ oc patch clustercsidriver/csi.vsphere.vmware.com --type=merge -p '{"spec":{"driverConfig":{"vSphere":{"granularMaxSnapshotsPerBlockVolumeInVSAN": 7}}}}'
clustercsidriver.operator.openshift.io/csi.vsphere.vmware.com patched
```

이 예에서 vSAN 제한이 7로 변경되었습니다 (`granularMaxSnapshotsPerBlockVolumeInVSAN` 을 7로 설정).

검증

다음 명령을 실행하여 구성 맵에 변경 사항이 반영되었는지 확인합니다.

```shell-session
$ oc -n openshift-cluster-csi-drivers get secret/vsphere-csi-config-secret -o jsonpath='{.data.cloud\.conf}' | base64 -d
```

```shell-session
# Labels with topology values are added dynamically via operator
[Global]
cluster-id = vsphere-01-cwv8p

# Populate VCenters (multi) after here
[VirtualCenter "vcenter.openshift.com"]
insecure-flag           = true
datacenters             = DEVQEdatacenter
password                = "xxxxxxxx"
user                    = "xxxxxxxx@devcluster.openshift.com"
migration-datastore-url = ds:///vmfs/volumes/vsan:52c842f232751e0d-3253aadeac21ca82/

[Snapshot]
global-max-snapshots-per-block-volume = 10
```

1. `global-max-snapshots-per-block-volume` 이 이제 10으로 설정됩니다.

#### 6.3.9. 추가 리소스

vSphere 환경에서 VMware 스냅샷을 사용하기 위한 모범 사례

### 6.4. CSI 볼륨 그룹 스냅샷

이 문서에서는 지원되는 CSI(Container Storage Interface) 드라이버와 함께 볼륨 그룹 스냅샷을 사용하여 OpenShift Container Platform의 데이터 손실을 보호하는 방법을 설명합니다. 영구 볼륨에 대해 숙지하는 것이 좋습니다.

중요

CSI 볼륨 그룹 스냅샷은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

이 기술 프리뷰 기능을 사용하려면 기능 게이트를 사용하여 활성화해야 합니다.

#### 6.4.1. CSI 볼륨 그룹 스냅샷 개요

스냅샷 은 특정 시점에서 클러스터의 스토리지 볼륨 상태를 나타냅니다. 볼륨 스냅샷을 사용하여 새 볼륨을 프로비저닝할 수 있습니다.

볼륨 그룹 스냅샷은 레이블 선택기를 사용하여 스냅샷 을 생성하기 위해 여러 영구 볼륨 클레임을 그룹화합니다. 볼륨 그룹 스냅샷은 동일한 시점으로 가져온 여러 볼륨에서 복사본을 나타냅니다. 이 기능은 여러 볼륨이 포함된 애플리케이션에 유용할 수 있습니다.

CSI(Container Storage Interface) 볼륨 그룹 스냅샷을 CSI 드라이버에서 지원해야 합니다. OpenShift Data Foundation은 볼륨 그룹 스냅샷을 지원합니다.

볼륨 그룹 스냅샷은 스냅샷을 관리하기 위한 세 가지 새로운 API 오브젝트를 제공합니다.

`VolumeGroupSnapshot`

여러 영구 볼륨 클레임에 대한 볼륨 그룹 스냅샷 생성을 요청합니다. 볼륨 그룹 스냅샷을 만들 때 타임스탬프 및 사용할 준비가 되었는지와 같은 볼륨 그룹 스냅샷 작업에 대한 정보가 포함되어 있습니다.

`VolumeGroupSnapshotContent`

동적으로 생성된 volumeGroupSnapshot에 대해 스냅샷 컨트롤러에서 생성합니다. 볼륨 그룹 스냅샷 ID를 포함하여 볼륨 그룹 스냅샷에 대한 정보가 포함되어 있습니다. 이 오브젝트는 클러스터의 프로비저닝된 리소스(그룹 스냅샷)를 나타냅니다. `VolumeGroupSnapshotContent` 오브젝트는 일대일 매핑으로 생성된 볼륨 그룹 스냅샷에 바인딩됩니다.

`VolumeGroupSnapshotClass`

드라이버 정보, 삭제 정책 등 볼륨 그룹 스냅샷을 생성하는 방법을 설명하기 위해 클러스터 관리자가 생성합니다.

이 세 가지 API 종류는 CRD(`CustomResourceDefinitions`)로 정의됩니다. 볼륨 그룹 스냅샷을 지원하려면 CSI 드라이버의 OpenShift Container Platform 클러스터에 이러한 CRD를 설치해야 합니다.

#### 6.4.2. CSI 볼륨 그룹 스냅샷 제한 사항

볼륨 그룹 스냅샷에는 다음과 같은 제한 사항이 있습니다.

기존 PVC(영구 볼륨 클레임)를 스냅샷에 표시된 이전 상태로 되돌리는 것은 스냅샷의 새 볼륨 프로비저닝만 지원합니다.

애플리케이션 일관성(예: 충돌 일관성)은 스토리지 시스템에서 제공하는 것 이상으로 제공되지 않습니다. 애플리케이션 일관성에 대한 자세한 내용은 Quiesce and Unquiesce Hooks 를 참조하십시오.

#### 6.4.3. 볼륨 그룹 스냅샷 클래스 생성

볼륨 그룹 스냅샷을 생성하려면 클러스터 관리자가 `VolumeGroupSnapshotClass` 를 생성해야 합니다.

이 오브젝트는 드라이버 정보, 삭제 정책 등을 포함하여 볼륨 그룹 스냅샷을 생성하는 방법을 설명합니다.

사전 요구 사항

관리자 권한으로 실행 중인 OpenShift Container Platform 클러스터에 로그인합니다.

기능 게이트를 사용하여 이 기능을 활성화했습니다. 기능 게이트를 사용하는 방법에 대한 자세한 내용은 기능 게이트 를 사용하여 기능 세트 활성화를 참조하십시오.

프로세스

`VolumeGroupSnapshotClass` 를 생성하려면 다음을 수행합니다.

다음 예제 파일을 사용하여 `VolumeGroupSnapshotClass` YAML 파일을 생성합니다.

```yaml
apiVersion: groupsnapshot.storage.k8s.io/v1beta1
kind: VolumeGroupSnapshotClass
metadata:
  name: csi-hostpath-groupsnapclass
deletionPolicy: Delete
driver: hostpath.csi.k8s.io
     …...
```

1. `VolumeGroupSnapshotClass` 오브젝트를 지정합니다.

2. `VolumeGroupSnapshotClass` 의 이름입니다.

다음 명령을 실행하여 'VolumeGroupSnapshotClass' 오브젝트를 생성합니다.

```shell-session
$ oc create -f <volume-group-snapshot-class-filename>.yaml
```

#### 6.4.4. 볼륨 그룹 스냅샷 생성

`VolumeGroupSnapshot` 오브젝트를 생성할 때 OpenShift Container Platform은 볼륨 그룹 스냅샷을 생성합니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인합니다.

기능 게이트를 사용하여 이 기능을 활성화했습니다. 기능 게이트를 사용하는 방법에 대한 자세한 내용은 기능 게이트 를 사용하여 기능 세트 활성화를 참조하십시오.

스냅샷에 대해 그룹화하려는 PVC(영구 볼륨 클레임)는 `VolumeGroupSnapshot` 오브젝트를 지원하는 CSI 드라이버를 사용하여 생성되었습니다.

스토리지 백엔드를 프로비저닝하는 스토리지 클래스입니다.

관리자가 `VolumeGroupSnapshotClass` 오브젝트를 생성했습니다.

프로세스

볼륨 그룹 스냅샷을 생성하려면 다음을 수행합니다.

볼륨 그룹 스냅샷에 포함할 PVC를 찾습니다(또는 생성).

```shell-session
$ oc get pvc
```

```shell-session
NAME        STATUS    VOLUME                                     CAPACITY   ACCESSMODES   AGE
pvc-0       Bound     pvc-a42d7ea2-e3df-11ed-b5ea-0242ac120002   1Gi        RWO           48s
pvc-1       Bound     pvc-a42d81b8-e3df-11ed-b5ea-0242ac120002   1Gi        RWO           48S
```

이 예에서는 두 개의 PVC를 사용합니다.

스냅샷 그룹에 속할 PVC에 레이블을 지정합니다.

다음 명령을 실행하여 PVC pvc-0에 레이블을 지정합니다.

```shell-session
$ oc label pvc pvc-0 group=myGroup
```

```shell-session
persistentvolumeclaim/pvc-0 labeled
```

다음 명령을 실행하여 PVC pvc-1에 레이블을 지정합니다.

```shell-session
$ oc label pvc pvc-1 group=myGroup
```

```shell-session
persistentvolumeclaim/pvc-1 labeled
```

이 예에서는 PVC "pvc-0" 및 "pvc-1"이라는 레이블이 지정되어 "myGroup" 그룹에 속합니다.

`VolumeGroupSnapshot` 오브젝트를 생성하여 볼륨 그룹 스냅샷을 지정합니다.

다음 예제 파일을 사용하여 `VolumeGroupSnapshot` 오브젝트 YAML 파일을 생성합니다.

```yaml
apiVersion: groupsnapshot.storage.k8s.io/v1beta1
kind: VolumeGroupSnapshot
metadata:
  name: <volume-group-snapshot-name>
  namespace: <namespace>
spec:
  volumeGroupSnapshotClassName: <volume-group-snapshot-class-name>
  source:
    selector:
      matchLabels:
        group: myGroup
```

1. `VolumeGroupSnapshot` 오브젝트는 여러 PVC에 대한 볼륨 그룹 스냅샷 생성을 요청합니다.

2. 볼륨 그룹 스냅샷의 이름입니다.

3. 볼륨 그룹 스냅샷의 네임스페이스입니다.

4. `VolumeGroupSnapshotClass` 이름입니다. 이 오브젝트는 관리자가 생성하며 볼륨 그룹 스냅샷을 생성하는 방법을 설명합니다.

5. 스냅샷에 원하는 PVC를 그룹화하는 데 사용되는 라벨의 이름입니다. 이 예제에서는 "myGroup"입니다.

다음 명령을 실행하여 `VolumeGroupSnapshot` 오브젝트를 생성합니다.

```shell-session
$ oc create -f <volume-group-snapshot-filename>.yaml
```

결과

볼륨 그룹 스냅샷의 일부로 지정된 PVC 수에 따라 개별 볼륨 스냅샷이 생성됩니다.

이러한 개별 볼륨 스냅샷의 이름은 다음과 같은 형식으로 지정됩니다. <hash of VolumeGroupSnaphotContentUUID+volumeHandle>:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: snapshot-4dc1c53a29538b36e85003503a4bcac5dbde4cff59e81f1e3bb80b6c18c3fd03
  namespace: default
  ownerReferences:
  - apiVersion: groupsnapshot.storage.k8s.io/v1beta1
    kind: VolumeGroupSnapshot
    name: my-groupsnapshot
    uid: ba2d60c5-5082-4279-80c2-daa85f0af354
  resourceVersion: "124503"
  uid: c0137282-f161-4e86-92c1-c41d36c6d04c
spec:
  source:
    persistentVolumeClaimName:pvc-1
status:
  volumeGroupSnapshotName: volume-group-snapshot-name
```

이전 예에서는 볼륨 그룹 스냅샷의 일부로 두 개의 개별 볼륨 스냅샷이 생성됩니다.

```shell-session
snapshot-4dc1c53a29538b36e85003503a4bcac5dbde4cff59e81f1e3bb80b6c18c3fd03
snapshot-fbfe59eff570171765df664280910c3bf1a4d56e233a5364cd8cb0152a35965b
```

#### 6.4.5. 볼륨 그룹 스냅샷 복원

`VolumeGroupSnapshot` CRD(사용자 정의 리소스 정의) 콘텐츠를 사용하여 기존 볼륨을 이전 상태로 복원할 수 있습니다.

기존 볼륨을 복원하려면 `VolumeGroupSnapshot` 의 일부인 `VolumeSnapshot` 오브젝트에서 생성할 새 PVC(영구 볼륨 클레임)를 요청할 수 있습니다. 이렇게 하면 지정된 스냅샷의 데이터로 채워진 새 볼륨의 프로비저닝이 트리거됩니다. 볼륨 그룹 스냅샷의 일부인 모든 스냅샷에서 모든 볼륨이 생성될 때까지 이 프로세스를 반복합니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인합니다.

PVC는 볼륨 그룹 스냅샷을 지원하는 CSI(Container Storage Interface) 드라이버를 사용하여 생성되었습니다.

스토리지 백엔드를 프로비저닝하는 스토리지 클래스입니다.

볼륨 그룹 스냅샷이 생성되어 사용할 준비가 되었습니다.

프로세스

볼륨 그룹 스냅샷에서 기존 볼륨을 이전 상태로 복원하려면 다음을 수행합니다.

다음 예와 같이 PVC의 볼륨 그룹 스냅샷에서 `VolumeSnapshot` 데이터 소스를 지정합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <pvc-restore-name>
  namespace: <namespace>
spec:
  storageClassName: csi-hostpath-sc
  dataSource:
    name: snapshot-fbfe59eff570171765df664280910c3bf1a4d56e233a5364cd8cb0152a35965b
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

1. 복원 PVC의 이름입니다.

2. 네임스페이스의 이름입니다.

3. 소스로 사용할 볼륨 그룹 스냅샷의 일부인 개별 볼륨 스냅샷의 이름입니다.

4. `VolumeSnapshot` 값으로 설정해야 합니다.

5. `snapshot.storage.k8s.io` 값으로 설정해야 합니다.

다음 명령을 실행하여 PVC를 생성합니다.

```shell-session
$ oc create -f <pvc-restore-filename>.yaml
```

1. 이전 단계에서 지정된 PVC 복원 파일의 이름입니다.

다음 명령을 실행하여 복원된 PVC가 생성되었는지 확인합니다.

```shell-session
$ oc get pvc
```

첫 번째 단계에서 지정한 이름이 있는 새 PVC가 표시됩니다.

볼륨 그룹 스냅샷의 일부인 모든 스냅샷에서 모든 볼륨을 생성할 때까지 필요에 따라 절차를 반복합니다.

#### 6.4.6. 추가 리소스

CSI 볼륨 스냅샷

### 6.5. CSI 볼륨 복제

볼륨 복제는 OpenShift Container Platform의 데이터 손실을 방지하기 위해 기존 영구 볼륨을 중복합니다. 이 기능은 지원되는 CSI(Container Storage Interface) 드라이버에서만 사용할 수 있습니다. CSI 볼륨 복제를 프로비저닝하기 전에 영구 볼륨에 대해 잘 알고 있어야 합니다.

#### 6.5.1. CSI 볼륨 복제 개요

CSI(Container Storage Interface) 볼륨 복제는 특정 시점에서 기존 영구 볼륨이 복제됩니다.

볼륨 복제는 볼륨 스냅샷과 유사하지만 더 효율적으로 사용할 수 있습니다. 예를 들어, 클러스터 관리자는 기존 클러스터 볼륨의 다른 인스턴스를 생성하여 클러스터 볼륨을 복제할 수 있습니다.

복제는 새 빈 볼륨을 생성하지 않고 백엔드 장치에서 지정된 볼륨을 정확하게 복제합니다. 동적 프로비저닝 후 모든 표준 볼륨을 사용하는 것처럼 볼륨 복제를 사용할 수 있습니다.

복제에는 새 API 오브젝트가 필요하지 않습니다. `PersistentVolumeClaim` 오브젝트의 기존 `dataSource` 필드가 동일한 네임스페이스에서 기존 PersistentVolumeClaim의 이름을 허용하도록 확장됩니다.

#### 6.5.1.1. 지원 제한

기본적으로 OpenShift Container Platform은 이러한 제한이 있는 CSI 볼륨 복제를 지원합니다.

대상 PVC(영구 볼륨 클레임)는 소스 PVC와 동일한 네임스페이스에 있어야 합니다.

복제는 다른 스토리지 클래스에서 지원됩니다.

대상 볼륨은 소스와 다른 스토리지 클래스에 대해 같을 수 있습니다.

기본 스토리지 클래스를 사용하고 `spec` 에서 `storageClassName` 을 생략할 수 있습니다.

CSI 드라이버에서만 지원을 사용할 수 있습니다. In-tree 및 FlexVolumes는 지원되지 않습니다.

CSI 드라이버가 볼륨 복제 기능을 구현하지 못할 수 있습니다. 자세한 내용은 CSI 드라이버 설명서를 참조하십시오.

#### 6.5.2. CSI 볼륨 복제 프로비저닝

복제된 PVC(영구 볼륨 클레임) API 오브젝트를 생성할 때 CSI 볼륨 복제 프로비저닝을 트리거합니다. 복제본은 다른 PVC 콘텐츠로 미리 채워져 다른 영구 볼륨과 동일한 규칙으로 구성됩니다. 한 가지 예외는 동일한 네임스페이스에서 기존 PVC를 참조하는 `dataSource` 를 추가해야 한다는 것입니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인되어 있습니다.

볼륨 복제를 지원하는 CSI 드라이버를 사용하여 PVC가 생성되었습니다.

동적 프로비저닝을 위해 스토리지 백엔드가 구성되어 있습니다. 정적 프로비저너에서는 복제 지원을 사용할 수 없습니다.

절차

기존 PVC에서 PVC를 복제하려면 다음을 수행합니다.

다음 YAML로 설명된 `PersistentVolumeClaim` 오브젝트를 사용하여 파일을 생성하고 저장합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-1-clone
  namespace: mynamespace
spec:
  storageClassName: csi-cloning
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  dataSource:
    kind: PersistentVolumeClaim
    name: pvc-1
```

1. 스토리지 백엔드를 프로비저닝하는 스토리지 클래스의 이름입니다. 기본 스토리지 클래스를 사용할 수 있으며 `storageClassName` 은 사양에서 생략할 수 있습니다.

다음 명령을 실행하여 이전 단계에서 저장한 오브젝트를 생성합니다.

```shell-session
$ oc create -f pvc-clone.yaml
```

새 PVC `pvc-1-clone` 이 생성됩니다.

볼륨 복제가 생성되어 다음 명령을 실행하여 준비되었는지 확인합니다.

```shell-session
$ oc get pvc pvc-1-clone
```

`pvc-1-clone` 에 `Bound` 로 표시됩니다.

이제 새로 복제된 PVC를 사용하여 Pod를 구성할 준비가 되었습니다.

YAML로 설명된 `Pod` 오브젝트로 파일을 생성하고 저장합니다. 예를 들면 다음과 같습니다.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: mypod
spec:
  containers:
    - name: myfrontend
      image: dockerfile/nginx
      volumeMounts:
      - mountPath: "/var/www/html"
        name: mypd
  volumes:
    - name: mypd
      persistentVolumeClaim:
        claimName: pvc-1-clone
```

1. CSI 볼륨 복제 작업 중에 생성된 복제 PVC입니다.

생성된 `Pod` 오브젝트가 원래 `dataSource` PVC와 독립적으로 복제된 PVC를 사용, 복제, 삭제하거나 그 스냅샷을 생성할 준비가 되었습니다.

### 6.6. 볼륨 팝업기

볼륨 채우기를 사용하면 빈 볼륨을 프로비저닝하는 대신 동적 프로비저닝 중에 데이터를 볼륨에 사전 로드할 수 있습니다.

#### 6.6.1. 볼륨 팝업 개요

OpenShift Container Platform 버전 4.12에서 4.19까지의 PVC(영구 볼륨 클레임) 사양의 `dataSource` 필드는 볼륨 팝업 기능을 제공합니다. 그러나 볼륨 채우기를 위해 PVC 및 스냅샷만 데이터 소스로 사용하는 것으로 제한됩니다.

OpenShift Container Platform 버전 4.20부터 `dataSourceRef` 필드가 대신 사용됩니다. `dataSourceRef` 필드를 사용하여 적절한 CR(사용자 정의 리소스)을 데이터 소스로 사용하여 새 볼륨을 사전 채울 수 있습니다.

참고

`dataSource` 필드를 사용하는 볼륨 팝업 기능은 향후 버전에서 더 이상 사용되지 않습니다. 이 필드를 사용하여 볼륨 팝업기를 생성한 경우 향후 문제를 방지하기 위해 `dataSourceRef` 필드를 사용하도록 볼륨 팝업기를 다시 생성하는 것이 좋습니다.

볼륨 채우기는 기본적으로 활성화되어 있으며 OpenShift Container Platform에는 설치된 `volume-data-source-validator` 컨트롤러가 포함되어 있습니다. 그러나 OpenShift Container Platform에는 볼륨 팝업기가 제공되지 않습니다.

#### 6.6.2. 볼륨 팝업기 생성

볼륨 팝업기를 생성하고 사용하려면 다음을 수행합니다.

볼륨 팝업을 위한 CRD(사용자 정의 리소스 정의)를 생성합니다.

볼륨 팝업기를 사용하여 미리 채워진 볼륨을 만듭니다.

#### 6.6.2.1. 볼륨 팝업기를 위한 CRD 생성

다음 절차에서는 볼륨 팝업기에 대한 예제 "hello, world" CRD(사용자 정의 리소스 정의)를 생성하는 방법을 설명합니다.

그런 다음 사용자는 이 CRD의 인스턴스를 생성하여 PVC(영구 볼륨 클레임)를 채울 수 있습니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

cluster-admin 권한으로 클러스터에 액세스합니다.

프로세스

다음 예제 YAML 파일을 사용하여 팝업기 및 관련 리소스의 논리 그룹화 및 작업에 대한 네임스페이스를 생성합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: hello
```

다음 예제 YAML 파일을 사용하여 데이터 소스에 대한 CRD를 생성합니다.

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: hellos.hello.example.com
spec:
  group: hello.example.com
  names:
    kind: Hello
    listKind: HelloList
    plural: hellos
    singular: hello
  scope: Namespaced
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        description: Hello is a specification for a Hello resource
        properties:
          apiVersion:
            description: 'APIVersion defines the versioned schema of this representation
              of an object. Servers should convert recognized schemas to the latest
              internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
            type: string
          kind:
            description: 'Kind is a string value representing the REST resource this
              object represents. Servers may infer this from the endpoint the client
              submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
            type: string
          spec:
            description: HelloSpec is the spec for a Hello resource
            properties:
              fileContents:
                type: string
              fileName:
                type: string
            required:
            - fileContents
            - fileName
            type: object
        required:
        - spec
        type: object
    served: true
    storage: true
```

`ServiceAccount`, ClusterRole, `ClusterRole Bindering`, `Deployment` 를 생성하여 컨트롤러를 배포하여 채우기를 구현하는 논리를 실행합니다.

다음 예제 YAML 파일을 사용하여 팝업기에 대한 서비스 계정을 생성합니다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: hello-account
  namespace: hello
```

1. 이전에 생성한 네임스페이스를 참조합니다.

다음 예제 YAML 파일을 사용하여 팝업기에 대한 클러스터 역할을 생성합니다.

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: hello-role
rules:
  - apiGroups: [hello.example.com]
    resources: [hellos]
    verbs: [get, list, watch]
```

다음 예제 YAML 파일을 사용하여 클러스터 역할 바인딩을 생성합니다.

```yaml
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: hello-binding
subjects:
  - kind: ServiceAccount
    name: hello-account
    namespace: hello
roleRef:
  kind: ClusterRole
  name: hello-role
  apiGroup: rbac.authorization.k8s.io
```

1. 역할 바인딩 이름입니다.

2. 이전에 생성한 서비스 계정의 이름을 참조합니다.

3. 이전에 생성한 서비스 계정의 네임스페이스 이름을 참조합니다.

4. 이전에 생성한 클러스터 역할을 참조합니다.

다음 예제 YAML 파일을 사용하여 팝업기에 대한 배포를 생성합니다.

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-populator
  namespace: hello
spec:
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      serviceAccount: hello-account
      containers:
        - name: hello
          image: registry.k8s.io/sig-storage/hello-populator:v1.0.1
          imagePullPolicy: IfNotPresent
          args:
            - --mode=controller
            - --image-name=registry.k8s.io/sig-storage/hello-populator:v1.0.1
            - --http-endpoint=:8080
          ports:
            - containerPort: 8080
              name: http-endpoint
              protocol: TCP
```

1. 이전에 생성한 네임스페이스를 참조합니다.

2. 이전에 생성한 서비스 계정을 참조합니다.

다음 예제 YAML 파일을 사용하여 `kind:Hello` 리소스를 볼륨의 유효한 데이터 소스로 등록할 볼륨 채우기를 생성합니다.

```yaml
kind: VolumePopulator
apiVersion: populator.storage.k8s.io/v1beta1
metadata:
  name: hello-populator
sourceKind:
  group: hello.example.com
  kind: Hello
```

1. 볼륨 팝업 이름.

등록되지 않은 팝업을 사용하는 PVC는 "이 PVC의 데이터 소스가 알 수 없음(등록되지 않은) 팝업기를 사용하므로 PVC가 프로비저닝되지 않을 수 있음을 나타내는 등록된 VolumePopulator와 일치하지 않습니다.

다음 단계

이제 이 CRD의 CR 인스턴스를 생성하여 PVC를 채울 수 있습니다.

볼륨 채우기기를 사용하여 볼륨을 미리 채우는 방법에 대한 자세한 내용은 볼륨 채우기가 포함된 사전 예약된 볼륨 생성을 참조하십시오.

#### 6.6.2.2. 볼륨 팝업기를 사용하여 미리 채워진 볼륨 생성

다음 절차에서는 이전에 생성한 `hellos.hello.example.com` CRD(Custom Resource Definition) 예제를 사용하여 미리 채워진 PVC(영구 볼륨 클레임)를 생성하는 방법을 설명합니다.

이 예제에서는 실제 데이터 소스를 사용하는 대신 볼륨의 루트 디렉터리에 "Hello, world!" 문자열이 포함된 "example.txt"라는 파일을 생성합니다. 실제 구현을 위해서는 자체 볼륨 팝업기를 생성해야 합니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인되어 있습니다.

볼륨 팝업을 위한 기존 CRD(사용자 정의 리소스 정의)가 있습니다.

OpenShift Container Platform은 볼륨 팝업과 함께 제공되지 않습니다. 자체 볼륨 팝업기를 생성해야 합니다.

프로세스

다음 명령을 실행하여 `fileContents` 매개변수로 전달된 텍스트 " `Hello`, World!"를 사용하여 Hello CRD의 CR(사용자 정의 리소스) 인스턴스를 생성합니다.

```shell-session
$ oc apply -f  - <<EOF
apiVersion: hello.example.com/v1alpha1
kind: Hello
metadata:
  name: example-hello
spec:
  fileName: example.txt
  fileContents: Hello, world!
EOF
```

다음 예제 파일과 유사한 Hello CR을 참조하는 PVC를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: example-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Mi
  dataSourceRef:
    apiGroup: hello.example.com
    kind: Hello
    name: example-hello
  volumeMode: Filesystem
```

1. `dataSourceRef` 필드는 PVC의 데이터 소스를 지정합니다.

2. 데이터 소스로 사용하는 CR의 이름입니다. 예에서는 'example-hello'입니다.

검증

몇 분 후에 다음 명령을 실행하여 PVC가 생성되고 `Bound` 상태에서 있는지 확인합니다.

```shell-session
$ oc get pvc example-pvc -n hello
```

1. 이 예에서 PVC 이름은 `example-pvc` 입니다.

```shell-session
NAME          STATUS    VOLUME        CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
example-pvc   Bound     my-pv         10Mi       ReadWriteOnce  gp3-csi        <unset>                 14s
```

PVC에서 읽는 작업을 생성하여 다음 예제 파일을 사용하여 데이터 소스 정보가 적용되었는지 확인합니다.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: example-job
spec:
  template:
    spec:
      containers:
        - name: example-container
          image: busybox:latest
          command:
            - cat
            - /mnt/example.txt
          volumeMounts:
            - name: vol
              mountPath: /mnt
      restartPolicy: Never
      volumes:
        - name: vol
          persistentVolumeClaim:
            claimName: example-pvc
```

1. "Hello, world!" 텍스트가 포함된 파일의 위치와 이름입니다.

2. 2단계에서 생성한 PVC의 이름입니다. 예에서는 `example-pvc`.

다음 명령을 실행하여 작업을 시작합니다.

```shell-session
$ oc run example-job --image=busybox --command -- sleep 30 --restart=OnFailure
```

```shell-session
pod/example-job created
```

다음 명령을 실행하여 작업 및 모든 종속 항목이 완료될 때까지 기다립니다.

```shell-session
$ oc wait --for=condition=Complete pod/example-job
```

다음 명령을 실행하여 작업에서 수집한 콘텐츠를 확인합니다.

```shell-session
$ oc logs job/example-job
```

```shell-session
Hello, world!
```

#### 6.6.2.3. 볼륨 팝업 설치 제거

다음 절차에서는 볼륨 팝업을 제거하는 방법을 설명합니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

cluster-admin 권한으로 클러스터에 액세스합니다.

프로세스

볼륨 팝업기를 제거하려면 아래 절차에 설치된 모든 오브젝트를 역순으로 삭제합니다.

섹션 볼륨 팝업기를 사용하여 미리 채워진 볼륨 생성.

섹션 볼륨 팝업을 위한 CRD 생성.

`VolumePopulator` 인스턴스를 제거해야 합니다.

#### 6.7.1. 개요

기본 스토리지 클래스를 관리하면 다음과 같은 몇 가지 다른 목표를 달성할 수 있습니다.

동적 프로비저닝을 비활성화하여 정적 프로비저닝을 강제 적용합니다.

다른 기본 스토리지 클래스가 있는 경우 스토리지 Operator가 초기 기본 스토리지 클래스를 다시 생성하지 못하도록 합니다.

기본 스토리지 클래스 이름 변경 또는 변경

이러한 목표를 달성하려면 `ClusterCSIDriver` 오브젝트의 `spec.storageClassState` 필드에 대한 설정을 변경합니다. 이 필드에 가능한 설정은 다음과 같습니다.

Managed: (기본값) CSI(Container Storage Interface) Operator는 기본 스토리지 클래스를 적극적으로 관리하므로 클러스터 관리자가 기본 스토리지 클래스에 대한 대부분의 수동 변경 사항이 제거되고 수동으로 삭제하려고 하면 기본 스토리지 클래스가 지속적으로 다시 생성됩니다.

Unmanaged: 기본 스토리지 클래스를 수정할 수 있습니다. CSI Operator는 스토리지 클래스를 적극적으로 관리하지 않으므로 자동으로 생성하는 기본 스토리지 클래스를 조정하지 않습니다.

Removed: CSI Operator가 기본 스토리지 클래스를 삭제합니다.

기본 스토리지 클래스 관리는 다음 CSI(Container Storage Interface) 드라이버 Operator에서 지원합니다.

AWS(Amazon Web Services) EBS(Elastic Block Storage)

Azure Disk

Azure File

GCP(Google Cloud Platform) PD(영구 디스크)

IBM Cloud® VPC Block

OpenStack Cinder

VMware vSphere

#### 6.7.2. 웹 콘솔을 사용하여 기본 스토리지 클래스 관리

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

cluster-admin 권한으로 클러스터에 액세스합니다.

프로세스

웹 콘솔을 사용하여 기본 스토리지 클래스를 관리하려면 다음을 수행합니다.

웹 콘솔에 로그인합니다.

Administration > CustomResourceDefinitions 를 클릭합니다.

CustomResourceDefinitions 페이지에서 `clustercsidrivers를 입력하여`

`ClusterCSIDriver` 오브젝트를 찾습니다.

ClusterCSIDriver 를 클릭한 다음 Instances 탭을 클릭합니다.

원하는 인스턴스의 이름을 클릭한 다음 YAML 탭을 클릭합니다.

`Managed`, `Unmanaged` 또는 `Removed` 의 값을 사용하여 `spec.storageClassState` 필드를 추가합니다.

```yaml
...
spec:
  driverConfig:
    driverType: ''
  logLevel: Normal
  managementState: Managed
  observedConfig: null
  operatorLogLevel: Normal
  storageClassState: Unmanaged
...
```

1. `spec.storageClassState` 필드가 "Unmanaged"로 설정

저장 을 클릭합니다.

#### 6.7.3. CLI를 사용하여 기본 스토리지 클래스 관리

사전 요구 사항

cluster-admin 권한으로 클러스터에 액세스합니다.

프로세스

CLI를 사용하여 스토리지 클래스를 관리하려면 다음 명령을 실행합니다.

```shell-session
$ oc patch clustercsidriver $DRIVERNAME --type=merge -p "{\"spec\":{\"storageClassState\":\"${STATE}\"}}"
```

1. 여기서 `${STATE}` 는 "제거" 또는 "관리되지 않음" 또는 "관리되지 않음"입니다.

여기서 `$DRIVERNAME` 은 프로비저너 이름입니다. 아래 명령을 실행하여 프로비저너 이름을 찾을 수 있습니다.

```shell
oc get sc
```

#### 6.7.4.1. 여러 기본 스토리지 클래스

기본이 아닌 스토리지 클래스를 기본값으로 표시하고 기존 기본 스토리지 클래스를 설정하지 않거나 기본 스토리지 클래스가 이미 있을 때 기본 스토리지 클래스를 생성하는 경우 여러 기본 스토리지 클래스가 발생할 수 있습니다. 여러 기본 스토리지 클래스가 있는 경우 기본 스토리지 클래스 `pvc.spec.storageClassName` =nil)를 요청하는 모든 영구 볼륨 클레임(PVC)은 해당 스토리지 클래스의 기본 상태와 관계없이 가장 최근에 생성된 기본 스토리지 클래스를 가져옵니다. 경고 대시보드에서 여러 기본 스토리지 클래스인 `MultipleDefaultStorageClasses` 가 있다는 경고를 받습니다.

#### 6.7.4.2. 기본 스토리지 클래스가 없음

PVC에서 존재하지 않는 기본 스토리지 클래스를 사용하려는 두 가지 시나리오가 있습니다.

관리자는 기본 스토리지 클래스를 제거하거나 기본이 아닌 것으로 표시한 다음 사용자가 기본 스토리지 클래스를 요청하는 PVC를 생성합니다.

설치 중에 설치 프로그램은 아직 생성되지 않은 기본 스토리지 클래스를 요청하는 PVC를 생성합니다.

이전 시나리오에서는 PVC가 보류 중인 상태로 무기한 유지됩니다. 이 상황을 해결하려면 기본 스토리지 클래스를 생성하거나 기존 스토리지 클래스 중 하나를 기본값으로 선언합니다. 기본 스토리지 클래스가 생성되거나 선언되면 PVC에 새 기본 스토리지 클래스가 제공됩니다. 가능한 경우 PVC는 결국 정적 또는 동적으로 프로비저닝된 PV에 바인딩하고 보류 중 상태로 이동합니다.

#### 6.7.5. 기본 스토리지 클래스 변경

다음 절차에 따라 기본 스토리지 클래스를 변경합니다.

예를 들어 두 개의 스토리지 클래스인 `gp3` 및 `standard` 가 있고 기본 스토리지 클래스를 `gp3` 에서 `standard` 로 변경하려는 경우.

사전 요구 사항

cluster-admin 권한으로 클러스터에 액세스합니다.

프로세스

기본 스토리지 클래스를 변경하려면 다음을 수행합니다.

스토리지 클래스를 나열합니다.

```shell-session
$ oc get storageclass
```

```shell-session
NAME                 TYPE
gp3 (default)        ebs.csi.aws.com
standard             ebs.csi.aws.com
```

1. `(default)` 는 기본 스토리지 클래스를 나타냅니다.

원하는 스토리지 클래스를 기본값으로 설정합니다.

원하는 스토리지 클래스의 경우 다음 명령을 실행하여 `storageclass.kubernetes.io/is-default-class` 주석을 `true` 로 설정합니다.

```shell-session
$ oc patch storageclass standard -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'
```

참고

짧은 시간 동안 여러 기본 스토리지 클래스를 사용할 수 있습니다. 그러나 결국 하나의 기본 스토리지 클래스만 존재하는지 확인해야 합니다.

여러 기본 스토리지 클래스가 있는 경우 기본 스토리지 클래스 `pvc.spec.storageClassName` =nil)를 요청하는 모든 영구 볼륨 클레임(PVC)은 해당 스토리지 클래스의 기본 상태와 관계없이 가장 최근에 생성된 기본 스토리지 클래스를 가져옵니다. 경고 대시보드에서 여러 기본 스토리지 클래스인 `MultipleDefaultStorageClasses` 가 있다는 경고를 받습니다.

이전 기본 스토리지 클래스에서 기본 스토리지 클래스 설정을 제거합니다.

이전 기본 스토리지 클래스의 경우 다음 명령을 실행하여 `storageclass.kubernetes.io/is-default-class` 주석의 값을 `false` 로 변경합니다.

```shell-session
$ oc patch storageclass gp3 -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "false"}}}'
```

변경 사항을 확인합니다.

```shell-session
$ oc get storageclass
```

```shell-session
NAME                 TYPE
gp3                  ebs.csi.aws.com
standard (default)   ebs.csi.aws.com
```

### 6.8. CSI 자동 마이그레이션

일반적으로 OpenShift Container Platform과 함께 제공되는 in-tree 스토리지 드라이버는 더 이상 사용되지 않으며 동등한 CSI(Container Storage Interface) 드라이버로 교체됩니다. OpenShift Container Platform은 동등한 CSI 드라이버에 인트리 볼륨 플러그인에 대한 자동 마이그레이션을 제공합니다.

#### 6.8.1. 개요

이 기능은 in-tree 스토리지 플러그인을 사용하여 프로비저닝된 볼륨을 CSI(Container Storage Interface) 드라이버에 자동으로 마이그레이션합니다.

이 프로세스는 데이터 마이그레이션을 수행하지 않습니다. OpenShift Container Platform은 메모리의 영구 볼륨 오브젝트만 변환합니다. 결과적으로 변환된 영구 볼륨 오브젝트는 디스크에 저장되지 않으며 내용이 변경되지도 않습니다. CSI 자동 마이그레이션이 원활해야 합니다. 이 기능은 기존 API 오브젝트(예: `PersistentVolumes`, `PersistentVolumeClaims`, `StorageClasses`)를 사용하는 방법을 변경하지 않습니다.

CSI 드라이버로 다음 인트리가 자동으로 마이그레이션됩니다.

Azure Disk

OpenStack Cinder

AWS(Amazon Web Services) EBS(Elastic Block Storage)

GCP PD(Google Compute Engine Persistent Disk)

Azure File

VMware vSphere

이러한 볼륨 유형의 CSI 마이그레이션은 일반적으로 사용 가능한 것으로 간주되며 수동 개입이 필요하지 않습니다.

CSI(In-tree 영구 볼륨) 또는 PVC(영구 볼륨 클레임)의 자동 마이그레이션은 원래의 in-tree 스토리지 플러그인에서 지원하지 않는 경우 스냅샷 또는 확장과 같은 새로운 CSI 드라이버 기능을 활성화하지 않습니다.

#### 6.8.2. 스토리지 클래스의 영향

새로운 OpenShift Container Platform 4.13 이상의 경우 기본 스토리지 클래스는 CSI 스토리지 클래스입니다. 이 스토리지 클래스를 사용하여 프로비저닝된 모든 볼륨은 CSI PV(영구 볼륨)입니다.

4.12 및 이전 버전에서 4.13 이상으로 업그레이드된 클러스터의 경우 CSI 스토리지 클래스가 생성되며 업그레이드 전에 기본 스토리지 클래스가 설정되지 않은 경우 기본값으로 설정됩니다. 이름이 동일한 스토리지 클래스가 있는 경우 기존 스토리지 클래스는 변경되지 않은 상태로 유지됩니다. 기존 in-tree 스토리지 클래스는 그대로 유지되며 기존 in-tree PV의 볼륨 확장과 같은 특정 기능에 필요할 수 있습니다. in-tree 스토리지 플러그인을 참조하는 스토리지 클래스는 계속 작동하지만 기본 스토리지 클래스를 CSI 스토리지 클래스로 전환하는 것이 좋습니다.

기본 스토리지 클래스 를 변경하려면 기본 스토리지 클래스 변경을 참조하십시오.

#### 6.9.1. 개요

OpenShift Container Platform은 AWS EBS CSI 드라이버 를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI(Container Storage Interface) Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

AWS EBS 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 AWS EBS CSI Driver Operator (Red Hat Operator) 및 AWS EBS CSI 드라이버를 설치합니다.

AWS EBS CSI Driver Operator 는 기본적으로 PVC를 생성하는 데 사용할 수 있는 StorageClass를 제공합니다. 필요한 경우 이 기본 스토리지 클래스를 비활성화할 수 있습니다(기본 스토리지 클래스 관리 참조). Amazon Elastic Block Store를 사용하는 영구 스토리지에 설명된 대로 AWS EBS StorageClass를 생성하는 옵션도 있습니다.

AWS EBS CSI 드라이버 를 사용하면 AWS EBS PV를 생성 및 마운트할 수 있습니다.

참고

OpenShift Container Platform 4.5 클러스터에 AWS EBS CSI Operator 및 드라이버를 설치하는 경우 OpenShift Container Platform 4.20으로 업데이트하기 전에 4.5 Operator 및 드라이버를 제거해야 합니다.

#### 6.9.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

중요

OpenShift Container Platform은 기본적으로 CSI 플러그인을 사용하여 Amazon EBS(Elastic Block Store) 스토리지를 프로비저닝합니다.

OpenShift Container Platform에서 AWS EBS 영구 볼륨을 동적으로 프로비저닝하는 방법에 대한 자세한 내용은 Amazon Elastic Block Store를 사용한 영구 스토리지를 참조하십시오.

#### 6.9.3. 사용자 관리 암호화

사용자 관리 암호화 기능을 사용하면 OpenShift Container Platform 노드 루트 볼륨을 암호화하는 설치 중에 키를 제공하고 모든 관리 스토리지 클래스가 이러한 키를 사용하여 프로비저닝된 스토리지 볼륨을 암호화할 수 있습니다. install-config YAML 파일의 `platform.<cloud_type>.defaultMachinePlatform` 필드에 사용자 지정 키를 지정해야 합니다.

이 기능은 다음 스토리지 유형을 지원합니다.

AWS(Amazon Web Services) EBS(Elastic Block Storage)

Microsoft Azure Disk 스토리지

GCP(Google Cloud Platform) PD(영구 디스크) 스토리지

IBM Virtual Private Cloud (VPC) 블록 스토리지

참고

스토리지 클래스에 암호화된 키가 정의되어 있지 않은 경우 스토리지 클래스에 `encrypted: "true"` 만 설정합니다. AWS EBS CSI 드라이버는 기본적으로 프로비저닝된 스토리지 볼륨을 암호화하기 위해 각 리전에서 Amazon EBS에 의해 자동으로 생성되는 AWS 관리 alias/aws/ebs를 사용합니다. 또한 관리 스토리지 클래스에는 모두 `encrypted: "true"` 설정이 있습니다.

Amazon EBS용 사용자 관리 암호화를 사용하여 설치하는 방법에 대한 자세한 내용은 설치 구성 매개변수를 참조하십시오.

추가 리소스

Amazon Elastic Block Store를 사용하는 영구 스토리지

CSI 볼륨 구성

#### 6.10.1. 개요

OpenShift Container Platform은 AWS EFS(Elastic File Service)용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

AWS EFS CSI Driver Operator를 설치한 후 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 AWS EFS CSI Operator 및 AWS EFS CSI 드라이버를 설치합니다. 이렇게 하면 AWS EFS CSI Driver Operator에서 AWS EFS 자산에 마운트되는 CSI 프로비저닝 PV를 생성할 수 있습니다.

AWS EFS CSI Driver Operator 는 설치 후 PVC(영구 볼륨 클레임)를 생성하는 데 사용할 스토리지 클래스를 기본적으로 생성하지 않습니다. 그러나 AWS EFS `StorageClass` 를 수동으로 생성할 수 있습니다. AWS EFS CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있도록 하여 동적 볼륨 프로비저닝을 지원합니다. 이렇게 하면 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없습니다.

AWS EFS CSI 드라이버 를 사용하면 AWS EFS PV를 생성하고 마운트할 수 있습니다.

#### 6.10.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.10.3. AWS EFS CSI Driver Operator 설정

AWS STS(Secure Token Service)와 함께 AWS EFS를 사용하는 경우 STS에 대한 역할 ARM(Amazon Resource Name)을 가져옵니다. 이는 AWS EFS CSI Driver Operator를 설치하는 데 필요합니다.

AWS EFS CSI Driver Operator를 설치합니다.

AWS EFS CSI 드라이버를 설치합니다.

#### 6.10.3.1. 보안 토큰 서비스의 Amazon 리소스 이름 가져오기

다음 절차에서는 AWS Security Token Service(STS)에서 OpenShift Container Platform을 사용하여 AWS EFS CSI Driver Operator를 구성하기 위해 역할 ARM(Amazon Resource Name)을 가져오는 방법을 설명합니다.

중요

AWS EFS CSI Driver Operator를 설치하기 전에 다음 절차 를 수행합니다(AWS EFS CSI Driver Operator 설치 참조).

사전 요구 사항

cluster-admin 역할을 가진 사용자로 클러스터에 액세스합니다.

AWS 계정 인증 정보

프로세스

ARN 역할은 여러 가지 방법으로 얻을 수 있습니다. 다음 절차에서는 클러스터 설치와 동일한 개념 및 CCO 유틸리티(`ccoctl`) 바이너리 툴을 사용하는 하나의 방법을 보여줍니다.

참고

하나의 영역 파일 시스템을 사용하는 경우 두 개의 `CredentialRequests` (컨트롤러용 및 드라이버 노드용)를 생성해야 합니다. 자세한 내용은 STS를 사용하여 하나의 영역 파일 시스템 설정 섹션을 참조하십시오.

STS를 사용하여 AWS EFS CSI Driver Operator 구성에 대한 역할 ARN을 가져오려면 다음을 수행합니다.

STS를 사용하여 클러스터를 설치하는 데 사용한 OpenShift Container Platform 릴리스 이미지에서 `ccoctl` 을 추출합니다. 자세한 내용은 "Cloud Credential Operator 유틸리티 구성"을 참조하십시오.

다음 예와 같이 EFS `CredentialsRequest` YAML 파일을 생성하고 저장한 다음 `credrequests` 디렉터리에 배치합니다.

```yaml
apiVersion: cloudcredential.openshift.io/v1
kind: CredentialsRequest
metadata:
  name: openshift-aws-efs-csi-driver
  namespace: openshift-cloud-credential-operator
spec:
  providerSpec:
    apiVersion: cloudcredential.openshift.io/v1
    kind: AWSProviderSpec
    statementEntries:
    - action:
      - elasticfilesystem:*
      effect: Allow
      resource: '*'
  secretRef:
    name: aws-efs-cloud-credentials
    namespace: openshift-cluster-csi-drivers
  serviceAccountNames:
  - aws-efs-csi-driver-operator
  - aws-efs-csi-driver-controller-sa
```

`ccoctl` 툴을 실행하여 AWS에서 새 IAM 역할을 생성하고 로컬 파일 시스템에서 YAML 파일을 생성합니다(< `path_to_ccoctl_output_dir>/manifests/openshift-cluster-csi-drivers-aws-efs-cloud-credentials.yaml`).

```shell-session
$ ccoctl aws create-iam-roles --name=<name> --region=<aws_region> --credentials-requests-dir=<path_to_directory_with_list_of_credentials_requests>/credrequests --identity-provider-arn=arn:aws:iam::<aws_account_id>:oidc-provider/<name>-oidc.s3.<aws_region>.amazonaws.com
```

`name=<name>` 은 추적을 위해 생성된 클라우드 리소스에 태그를 지정하는 데 사용되는 이름입니다.

`region=<aws_region` >은 클라우드 리소스가 생성되는 AWS 리전입니다.

`dir=<path_to_directory_with_list_of_credentials_requests>/credrequests` 는 이전 단계에서 EFS CredentialsRequest 파일을 포함하는 디렉터리입니다.

`<aws_account_id&` gt;는 AWS 계정 ID입니다.

```shell-session
$ ccoctl aws create-iam-roles --name my-aws-efs --credentials-requests-dir credrequests --identity-provider-arn arn:aws:iam::123456789012:oidc-provider/my-aws-efs-oidc.s3.us-east-2.amazonaws.com
```

```shell-session
2022/03/21 06:24:44 Role arn:aws:iam::123456789012:role/my-aws-efs -openshift-cluster-csi-drivers-aws-efs-cloud- created
2022/03/21 06:24:44 Saved credentials configuration to: /manifests/openshift-cluster-csi-drivers-aws-efs-cloud-credentials-credentials.yaml
2022/03/21 06:24:45 Updated Role policy for Role my-aws-efs-openshift-cluster-csi-drivers-aws-efs-cloud-
```

이전 단계에서 예제 출력 의 첫 번째 줄에서 ARN 역할을 복사합니다. 역할 ARN은 "Role"과 "created" 사이의 역할입니다. 이 예에서 ARN 역할은 "arn:aws:iam::123456789012:role/my-aws-efs -openshift-cluster-csi-drivers-aws-efs-cloud"입니다.

AWS EFS CSI Driver Operator를 설치할 때 ARN 역할이 필요합니다.

다음 단계

AWS EFS CSI Driver Operator를 설치합니다.

추가 리소스

AWS EFS CSI Driver Operator 설치

Cloud Credential Operator 유틸리티 구성

AWS EFS CSI 드라이버 설치

#### 6.10.3.2. AWS EFS CSI Driver Operator 설치

AWS EFS CSI Driver Operator(Red Hat Operator)는 기본적으로 OpenShift Container Platform에 설치되지 않습니다. 다음 절차에 따라 클러스터에서 AWS EFS CSI Driver Operator를 설치하고 구성합니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

프로세스

웹 콘솔에서 AWS EFS CSI Driver Operator를 설치하려면 다음을 수행합니다.

웹 콘솔에 로그인합니다.

AWS EFS CSI Operator를 설치합니다.

Ecosystem → Software Catalog 를 클릭합니다.

필터 상자에 AWS EFS CSI를 입력하여 AWS EFS CSI Operator를 찾습니다.

AWS EFS CSI Driver Operator 버튼을 클릭합니다.

중요

AWS EFS Operator 가 아닌 AWS EFS CSI Driver Operator 를 선택해야 합니다. AWS EFS Operator 는 커뮤니티 Operator이며 Red Hat에서 지원하지 않습니다.

AWS EFS CSI Driver Operator 페이지에서 설치 를 클릭합니다.

Operator 설치 페이지에서 다음을 확인합니다.

역할 ARN 필드에 AWS EFS(Secure Token Service)를 사용하는 경우 보안 토큰 서비스 프로세스의 Amazon Resource Name(보안 토큰 서비스) 절차의 마지막 단계에서 복사한 ARN 역할을 입력합니다.

클러스터의 모든 네임스페이스(기본값) 가 선택됩니다.

설치된 네임스페이스 는 openshift-cluster-csi-drivers 로 설정됩니다.

설치 를 클릭합니다.

설치가 완료되면 AWS EFS CSI Operator가 웹 콘솔의 설치된 Operators 섹션에 나열됩니다.

다음 단계

AWS EFS CSI 드라이버를 설치합니다.

#### 6.10.3.3. AWS EFS CSI 드라이버 설치

AWS EFS CSI Driver Operator (Red Hat Operator)를 설치한 후 AWS EFS CSI 드라이버 를 설치합니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

프로세스

Administration → CustomResourceDefinitions → ClusterCSIDriver 를 클릭합니다.

Instances 탭에서 Create ClusterCSIDriver 를 클릭합니다.

다음 YAML 파일을 사용합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: ClusterCSIDriver
metadata:
    name: efs.csi.aws.com
spec:
  managementState: Managed
```

생성 을 클릭합니다.

다음 조건이 "True" 상태로 변경될 때까지 기다립니다.

AWSEFSDriverNodeServiceControllerAvailable

AWSEFSDriverControllerServiceControllerAvailable

#### 6.10.4. AWS EFS 스토리지 클래스 생성

스토리지 클래스는 스토리지 수준 및 사용량을 구분하고 조정하는 데 사용됩니다. 스토리지 클래스를 정의하면 사용자는 동적으로 프로비저닝된 영구 볼륨을 얻을 수 있습니다.

AWS EFS CSI Driver Operator (Red Hat Operator) 는 설치 후 기본적으로 스토리지 클래스를 생성하지 않습니다. 그러나 AWS EFS 스토리지 클래스를 수동으로 생성할 수 있습니다.

#### 6.10.4.1. 콘솔을 사용하여 AWS EFS 스토리지 클래스 생성

프로세스

OpenShift Container Platform 웹 콘솔에서 스토리지 → StorageClasses 를 클릭합니다.

StorageClasses 페이지에서 StorageClass 만들기 를 클릭합니다.

StorageClass 페이지에서 다음 단계를 수행합니다.

스토리지 클래스를 참조할 이름을 입력합니다.

선택 사항: 설명을 입력합니다.

회수 정책을 선택합니다.

Provisioner 드롭다운 목록에서 `efs.csi.aws.com` 을 선택합니다.

선택 사항: 선택한 프로비저너의 구성 매개변수를 설정합니다.

생성 을 클릭합니다.

#### 6.10.4.2. CLI를 사용하여 AWS EFS 스토리지 클래스 생성

프로세스

`StorageClass` 오브젝트를 생성합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: efs-sc
provisioner: efs.csi.aws.com
parameters:
  provisioningMode: efs-ap
  fileSystemId: fs-a5324911
  directoryPerms: "700"
  gidRangeStart: "1000"
  gidRangeEnd: "2000"
  basePath: "/dynamic_provisioning"
```

1. 동적 프로비저닝을 사용하려면 `provisioningMode` 가 `efs-ap` 이어야 합니다.

2. `fileSystemId` 는 수동으로 생성된 EFS 볼륨의 ID여야 합니다.

3. `directoryPerms` 는 볼륨의 루트 디렉터리에 대한 기본 권한입니다. 이 예에서는 소유자만 볼륨에 액세스할 수 있습니다.

4. 5

`gidRangeStart` 및 `gidRangeEnd` 는 AWS 액세스 지점의 GID를 설정하는 데 사용되는 POSIX 그룹 ID(GID) 범위를 설정합니다. 지정하지 않으면 기본 범위는 50000-7000000입니다. 각 프로비저닝 볼륨이므로 AWS 액세스 지점에는 이 범위의 고유한 GID가 할당됩니다.

6. `basePath` 는 동적으로 프로비저닝된 볼륨을 생성하는 데 사용되는 EFS 볼륨의 디렉터리입니다. 이 경우 PV는 EFS 볼륨에서 "/dynamic_provisioning/<random uuid>"로 프로비저닝됩니다. 하위 디렉터리만 PV를 사용하는 pod에 마운트됩니다.

참고

클러스터 관리자는 각각 다른 EFS 볼륨을 사용하여 여러 `StorageClass` 오브젝트를 생성할 수 있습니다.

#### 6.10.5. AWS EFS CSI 간 계정 지원

계정 간 지원을 통해 AWS EBS(Elastic File System) CSI(Container Storage Interface) 드라이버를 사용하여 하나의 AWS 계정에 OpenShift Container Platform 클러스터를 마운트하고 다른 AWS 계정에 파일 시스템을 마운트할 수 있습니다.

사전 요구 사항

관리자 권한을 사용하여 OpenShift Container Platform 클러스터에 액세스

두 개의 유효한 AWS 계정

EFS CSI Operator가 설치되었습니다. EFS CSI Operator 설치에 대한 자세한 내용은 AWS EFS CSI Driver Operator 설치 섹션을 참조하십시오.

OpenShift Container Platform 클러스터 및 EFS 파일 시스템은 모두 동일한 AWS 리전에 있어야 합니다.

다음 절차에서 사용되는 두 개의 가상 프라이빗 클라우드(VPC)가 다른 네트워크 CIDR(Classless Inter-Domain Routing) 범위를 사용하는지 확인합니다.

OpenShift Container Platform CLI()에 액세스합니다.

```shell
oc
```

AWS CLI에 액세스합니다.

아래 명령줄 JSON 프로세서에 액세스합니다.

```shell
jq
```

프로세스

다음 절차에서는 설정 방법을 설명합니다.

OpenShift Container Platform AWS 계정 A: VPC 내에 배포된 Red Hat OpenShift Container Platform 클러스터 v4.16 이상을 포함합니다.

AWS 계정 B: VPC(네트워크, 라우팅 테이블, 네트워크 연결 포함)를 포함합니다. EFS 파일 시스템은 이 VPC에서 생성됩니다.

계정에서 AWS EFS를 사용하려면 다음을 수행합니다.

환경을 설정합니다.

다음 명령을 실행하여 환경 변수를 구성합니다.

```shell-session
export CLUSTER_NAME="<CLUSTER_NAME>"
export AWS_REGION="<AWS_REGION>"
export AWS_ACCOUNT_A_ID="<ACCOUNT_A_ID>"
export AWS_ACCOUNT_B_ID="<ACCOUNT_B_ID>"
export AWS_ACCOUNT_A_VPC_CIDR="<VPC_A_CIDR>"
export AWS_ACCOUNT_B_VPC_CIDR="<VPC_B_CIDR>"
export AWS_ACCOUNT_A_VPC_ID="<VPC_A_ID>"
export AWS_ACCOUNT_B_VPC_ID="<VPC_B_ID>"
export SCRATCH_DIR="<WORKING_DIRECTORY>"
export CSI_DRIVER_NAMESPACE="openshift-cluster-csi-drivers"
export AWS_PAGER=""
```

1. 선택한 클러스터 이름입니다.

2. AWS 리전을 선택합니다.

3. AWS 계정 A ID.

4. AWS 계정 B ID.

5. 계정 A의 VPC의 CIDR 범위.

6. 계정 B의 VPC의 CIDR 범위.

7. 계정 A(클러스터)의 VPC ID

8. 계정 B의 VPC ID (EFS 크로스 계정)

9. 임시 파일을 저장하는 데 사용할 쓰기 가능한 쓰기 가능한 디렉터리입니다.

10. 드라이버가 기본이 아닌 네임스페이스에 설치된 경우 이 값을 변경합니다.

11. AWS CLI를 사용하면 모든 것이 stdout에 직접 출력됩니다.

다음 명령을 실행하여 작업 디렉터리를 생성합니다.

```shell-session
mkdir -p $SCRATCH_DIR
```

OpenShift Container Platform CLI에서 다음 명령을 실행하여 클러스터 연결을 확인합니다.

```shell-session
$ oc whoami
```

OpenShift Container Platform 클러스터 유형을 확인하고 노드 선택기를 설정합니다.

EFS 교차 계정 기능을 사용하려면 EFS CSI 컨트롤러 Pod를 실행하는 노드에 AWS IAM 정책을 할당해야 합니다. 그러나 모든 OpenShift Container Platform 유형에서 이 문제가 일치하지는 않습니다.

클러스터가 HyperShift(Hosted Control Plane)로 배포된 경우 다음 명령을 실행하여 `NODE_SELECTOR` 환경 변수를 설정하여 작업자 노드 레이블을 유지합니다.

```shell-session
export NODE_SELECTOR=node-role.kubernetes.io/worker
```

다른 모든 OpenShift Container Platform 유형의 경우 다음 명령을 실행하여 마스터 노드 레이블을 유지하도록 `NODE_SELECTOR` 환경 변수를 설정합니다.

```shell-session
export NODE_SELECTOR=node-role.kubernetes.io/master
```

다음 명령을 실행하여 AWS CLI 프로필을 계정 전환의 환경 변수로 구성합니다.

```shell-session
export AWS_ACCOUNT_A="<ACCOUNT_A_NAME>"
export AWS_ACCOUNT_B="<ACCOUNT_B_NAME>"
```

다음 명령을 실행하여 AWS CLI가 두 계정의 기본값으로 JSON 출력 형식으로 구성되어 있는지 확인합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_A}
aws configure get output
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_B}
aws configure get output
```

이전 명령이 반환되는 경우:

no value: 기본 출력 형식은 이미 JSON으로 설정되어 있으며 변경 사항이 필요하지 않습니다.

모든 값: JSON 형식을 사용하도록 AWS CLI를 재구성하십시오. 출력 형식 변경에 대한 자세한 내용은 AWS 문서 의 AWS CLI의 출력 형식 설정을 참조하십시오.

다음 명령을 실행하여 `AWS_DEFAULT_PROFILE` 과의 충돌을 방지하기 위해 쉘에서 `AWS_PROFILE` 을 설정 해제합니다.

```shell-session
unset AWS_PROFILE
```

AWS 계정 B IAM 역할 및 정책을 구성합니다.

다음 명령을 실행하여 계정 B 프로필로 전환합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_B}
```

다음 명령을 실행하여 EFS CSI Driver Operator의 IAM 역할 이름을 정의합니다.

```shell-session
export ACCOUNT_B_ROLE_NAME=${CLUSTER_NAME}-cross-account-aws-efs-csi-operator
```

다음 명령을 실행하여 IAM 신뢰 정책 파일을 생성합니다.

```shell-session
cat <<EOF > $SCRATCH_DIR/AssumeRolePolicyInAccountB.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${AWS_ACCOUNT_A_ID}:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {}
        }
    ]
}
EOF
```

다음 명령을 실행하여 EFS CSI Driver Operator에 대한 IAM 역할을 생성합니다.

```shell-session
ACCOUNT_B_ROLE_ARN=$(aws iam create-role \
  --role-name "${ACCOUNT_B_ROLE_NAME}" \
  --assume-role-policy-document file://$SCRATCH_DIR/AssumeRolePolicyInAccountB.json \
  --query "Role.Arn" --output text) \
&& echo $ACCOUNT_B_ROLE_ARN
```

다음 명령을 실행하여 IAM 정책 파일을 생성합니다.

```shell-session
cat << EOF > $SCRATCH_DIR/EfsPolicyInAccountB.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeSubnets"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "elasticfilesystem:DescribeMountTargets",
                "elasticfilesystem:DeleteAccessPoint",
                "elasticfilesystem:ClientMount",
                "elasticfilesystem:DescribeAccessPoints",
                "elasticfilesystem:ClientWrite",
                "elasticfilesystem:ClientRootAccess",
                "elasticfilesystem:DescribeFileSystems",
                "elasticfilesystem:CreateAccessPoint",
                "elasticfilesystem:TagResource"
            ],
            "Resource": "*"
        }
    ]
}
EOF
```

다음 명령을 실행하여 IAM 정책을 생성합니다.

```shell-session
ACCOUNT_B_POLICY_ARN=$(aws iam create-policy --policy-name "${CLUSTER_NAME}-efs-csi-policy" \
   --policy-document file://$SCRATCH_DIR/EfsPolicyInAccountB.json \
   --query 'Policy.Arn' --output text) \
&& echo ${ACCOUNT_B_POLICY_ARN}
```

다음 명령을 실행하여 역할에 정책을 연결합니다.

```shell-session
aws iam attach-role-policy \
   --role-name "${ACCOUNT_B_ROLE_NAME}" \
   --policy-arn "${ACCOUNT_B_POLICY_ARN}"
```

AWS 계정 A IAM 역할 및 정책을 구성합니다.

다음 명령을 실행하여 계정 A 프로필로 전환합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_A}
```

다음 명령을 실행하여 IAM 정책 문서를 생성합니다.

```shell-session
cat << EOF > $SCRATCH_DIR/AssumeRoleInlinePolicyPolicyInAccountA.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "${ACCOUNT_B_ROLE_ARN}"
    }
  ]
}
EOF
```

AWS 계정 A에서 다음 명령을 실행하여 AWS 관리 정책 "AmazonElasticFileSystemSystemClientFullAccess"를 OpenShift Container Platform 클러스터 마스터 역할에 연결합니다.

```shell-session
EFS_CLIENT_FULL_ACCESS_BUILTIN_POLICY_ARN=arn:aws:iam::aws:policy/AmazonElasticFileSystemClientFullAccess
declare -A ROLE_SEEN
for NODE in $(oc get nodes --selector="${NODE_SELECTOR}" -o jsonpath='{.items[*].metadata.name}'); do
    INSTANCE_PROFILE=$(aws ec2 describe-instances \
        --filters "Name=private-dns-name,Values=${NODE}" \
        --query 'Reservations[].Instances[].IamInstanceProfile.Arn' \
        --output text | awk -F'/' '{print $NF}' | xargs)
    MASTER_ROLE_ARN=$(aws iam get-instance-profile \
        --instance-profile-name "${INSTANCE_PROFILE}" \
        --query 'InstanceProfile.Roles[0].Arn' \
        --output text | xargs)
    MASTER_ROLE_NAME=$(echo "${MASTER_ROLE_ARN}" | awk -F'/' '{print $NF}' | xargs)
    echo "Checking role: '${MASTER_ROLE_NAME}'"
    if [[ -n "${ROLE_SEEN[$MASTER_ROLE_NAME]:-}" ]]; then
        echo "Already processed role: '${MASTER_ROLE_NAME}', skipping."
        continue
    fi
    ROLE_SEEN["$MASTER_ROLE_NAME"]=1
    echo "Assigning policy ${EFS_CLIENT_FULL_ACCESS_BUILTIN_POLICY_ARN} to role ${MASTER_ROLE_NAME}"
    aws iam attach-role-policy --role-name "${MASTER_ROLE_NAME}" --policy-arn "${EEFS_CLIENT_FULL_ACCESS_BUILTIN_POLICY_ARN}"
done
```

역할을 가정할 수 있도록 IAM 엔터티에 정책을 연결합니다.

이 단계는 클러스터 구성에 따라 다릅니다. 다음 두 시나리오 모두에서 EFS CSI Driver Operator는 엔터티를 사용하여 AWS에 인증하며 이 엔티티에는 계정 B에서 역할을 가정할 수 있는 권한이 부여되어야 합니다.

클러스터가 있는 경우:

STS가 활성화되지 않음: EFS CSI Driver Operator는 AWS 인증을 위해 IAM 사용자 엔터티를 사용합니다. 역할 가정을 허용하기 위해 IAM 사용자에게 정책 연결을 진행합니다.

STS가 활성화되어 있습니다. EFS CSI Driver Operator는 AWS 인증을 위해 IAM 역할 엔터티를 사용합니다. 역할 가정을 허용하려면 " IAM 역할에 연결 정책 적용" 단계를 진행합니다.

역할 가정 허용을 위해 IAM 사용자에게 정책 연결

다음 명령을 실행하여 EFS CSI Driver Operator에서 사용하는 IAM 사용자를 식별합니다.

```shell-session
EFS_CSI_DRIVER_OPERATOR_USER=$(oc -n openshift-cloud-credential-operator get credentialsrequest/openshift-aws-efs-csi-driver -o json | jq -r '.status.providerStatus.user')
```

다음 명령을 실행하여 IAM 사용자에게 정책을 연결합니다.

```shell-session
aws iam put-user-policy \
    --user-name "${EFS_CSI_DRIVER_OPERATOR_USER}"  \
    --policy-name efs-cross-account-inline-policy \
    --policy-document file://$SCRATCH_DIR/AssumeRoleInlinePolicyPolicyInAccountA.json
```

역할을 가정할 수 있도록 IAM 역할에 정책을 연결합니다.

다음 명령을 실행하여 현재 EFS CSI Driver Operator에서 사용하는 IAM 역할 이름을 식별합니다.

```shell-session
EFS_CSI_DRIVER_OPERATOR_ROLE=$(oc -n ${CSI_DRIVER_NAMESPACE} get secret/aws-efs-cloud-credentials -o jsonpath='{.data.credentials}' | base64 -d | grep role_arn | cut -d'/' -f2) && echo ${EFS_CSI_DRIVER_OPERATOR_ROLE}
```

다음 명령을 실행하여 EFS CSI Driver Operator에서 사용하는 IAM 역할에 정책을 연결합니다.

```shell-session
aws iam put-role-policy \
    --role-name "${EFS_CSI_DRIVER_OPERATOR_ROLE}"  \
    --policy-name efs-cross-account-inline-policy \
    --policy-document file://$SCRATCH_DIR/AssumeRoleInlinePolicyPolicyInAccountA.json
```

VPC 피어링을 구성합니다.

다음 명령을 실행하여 계정 A에서 계정 B로의 피어링 요청을 시작합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_A}
PEER_REQUEST_ID=$(aws ec2 create-vpc-peering-connection --vpc-id "${AWS_ACCOUNT_A_VPC_ID}" --peer-vpc-id "${AWS_ACCOUNT_B_VPC_ID}" --peer-owner-id "${AWS_ACCOUNT_B_ID}" --query VpcPeeringConnection.VpcPeeringConnectionId --output text)
```

다음 명령을 실행하여 계정 B에서 피어링 요청을 수락합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_B}
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id "${PEER_REQUEST_ID}"
```

다음 명령을 실행하여 계정 A의 경로 테이블 ID를 검색하고 계정 B VPC에 경로를 추가합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_A}
for NODE in $(oc get nodes --selector=node-role.kubernetes.io/worker | tail -n +2 | awk '{print $1}')
do
    SUBNET=$(aws ec2 describe-instances --filters "Name=private-dns-name,Values=$NODE" --query 'Reservations[*].Instances[*].NetworkInterfaces[*].SubnetId' | jq -r '.[0][0][0]')
    echo SUBNET is ${SUBNET}
    ROUTE_TABLE_ID=$(aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=${SUBNET}" --query 'RouteTables[*].RouteTableId' | jq -r '.[0]')
    echo Route table ID is $ROUTE_TABLE_ID
    aws ec2 create-route --route-table-id ${ROUTE_TABLE_ID} --destination-cidr-block ${AWS_ACCOUNT_B_VPC_CIDR} --vpc-peering-connection-id ${PEER_REQUEST_ID}
done
```

계정 B의 경로 테이블 ID를 검색하고 다음 명령을 실행하여 계정 A VPC에 경로를 추가합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_B}
for ROUTE_TABLE_ID in $(aws ec2 describe-route-tables   --filters "Name=vpc-id,Values=${AWS_ACCOUNT_B_VPC_ID}"   --query "RouteTables[].RouteTableId" | jq -r '.[]')
do
    echo Route table ID is $ROUTE_TABLE_ID
    aws ec2 create-route --route-table-id ${ROUTE_TABLE_ID} --destination-cidr-block ${AWS_ACCOUNT_A_VPC_CIDR} --vpc-peering-connection-id ${PEER_REQUEST_ID}
done
```

계정 A에서 EFS로 NFS 트래픽을 허용하도록 계정 B에서 보안 그룹을 구성합니다.

다음 명령을 실행하여 계정 B 프로필로 전환합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_B}
```

다음 명령을 실행하여 EFS 액세스를 위해 VPC 보안 그룹을 구성합니다.

```shell-session
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters Name=vpc-id,Values="${AWS_ACCOUNT_B_VPC_ID}" | jq -r '.SecurityGroups[].GroupId')
aws ec2 authorize-security-group-ingress \
 --group-id "${SECURITY_GROUP_ID}" \
 --protocol tcp \
 --port 2049 \
 --cidr "${AWS_ACCOUNT_A_VPC_CIDR}" | jq .
```

계정 B에서 지역 전체 EFS 파일 시스템을 생성합니다.

다음 명령을 실행하여 계정 B 프로필로 전환합니다.

```shell-session
export AWS_DEFAULT_PROFILE=${AWS_ACCOUNT_B}
```

다음 명령을 실행하여 지역 전체 EFS 파일 시스템을 생성합니다.

```shell-session
CROSS_ACCOUNT_FS_ID=$(aws efs create-file-system --creation-token efs-token-1 \
--region ${AWS_REGION} \
--encrypted | jq -r '.FileSystemId') \
&& echo $CROSS_ACCOUNT_FS_ID
```

다음 명령을 실행하여 EFS의 지역 전체 마운트 대상을 구성합니다.

```shell-session
for SUBNET in $(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=${AWS_ACCOUNT_B_VPC_ID}" \
  --region ${AWS_REGION} \
  | jq -r '.Subnets.[].SubnetId'); do \
    MOUNT_TARGET=$(aws efs create-mount-target --file-system-id ${CROSS_ACCOUNT_FS_ID} \
    --subnet-id ${SUBNET} \
    --region ${AWS_REGION} \
    | jq -r '.MountTargetId'); \
    echo ${MOUNT_TARGET}; \
done
```

그러면 VPC의 각 서브넷에 마운트 지점이 생성됩니다.

계정 간 액세스를 위해 EFS Operator를 구성합니다.

다음 명령을 실행하여 후속 단계에서 생성할 시크릿 및 스토리지 클래스에 대한 사용자 정의 이름을 정의합니다.

```shell-session
export SECRET_NAME=my-efs-cross-account
export STORAGE_CLASS_NAME=efs-sc-cross
```

OpenShift Container Platform CLI에서 다음 명령을 실행하여 계정 B에서 ARN 역할을 참조하는 시크릿을 생성합니다.

```shell-session
oc create secret generic ${SECRET_NAME} -n ${CSI_DRIVER_NAMESPACE} --from-literal=awsRoleArn="${ACCOUNT_B_ROLE_ARN}"
```

OpenShift Container Platform CLI에서 다음 명령을 실행하여 새로 생성된 보안에 대한 CSI 드라이버 컨트롤러 액세스 권한을 부여합니다.

```shell-session
oc -n ${CSI_DRIVER_NAMESPACE} create role access-secrets --verb=get,list,watch --resource=secrets
oc -n ${CSI_DRIVER_NAMESPACE} create rolebinding --role=access-secrets default-to-secrets --serviceaccount=${CSI_DRIVER_NAMESPACE}:aws-efs-csi-driver-controller-sa
```

OpenShift Container Platform CLI에서 다음 명령을 실행하여 계정 B의 EFS ID와 이전에 생성된 시크릿을 참조하는 새 스토리지 클래스를 생성합니다.

```shell-session
cat << EOF | oc apply -f -
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: ${STORAGE_CLASS_NAME}
provisioner: efs.csi.aws.com
parameters:
  provisioningMode: efs-ap
  fileSystemId: ${CROSS_ACCOUNT_FS_ID}
  directoryPerms: "700"
  gidRangeStart: "1000"
  gidRangeEnd: "2000"
  basePath: "/dynamic_provisioning"
  csi.storage.k8s.io/provisioner-secret-name: ${SECRET_NAME}
  csi.storage.k8s.io/provisioner-secret-namespace: ${CSI_DRIVER_NAMESPACE}
EOF
```

추가 리소스

AWS CLI에서 출력 형식 설정

#### 6.10.6.1. 영역 파일 시스템 개요

OpenShift Container Platform은 AWS EFS(Elastic File System) One Zone File System (EFS) One Zone File System (EFS) One Zone File System (EFS) 단일 가용성 영역 (AZ)에 중복 데이터를 저장하는 EFS 스토리지 옵션임을 지원합니다. 이는 리전 내의 여러 AZ에 중복된 데이터를 저장하는 기본 EFS 스토리지 옵션과 대조됩니다.

OpenShift Container Platform 4.19에서 업그레이드된 클러스터는 지역 EFS 볼륨과 호환됩니다.

참고

하나의 영역 볼륨의 동적 프로비저닝은 단일 영역 클러스터에서만 지원됩니다. 클러스터의 모든 노드는 동적 프로비저닝에 사용되는 EFS 볼륨과 동일한 AZ에 있어야 합니다.

영구 볼륨(PV)에 볼륨이 있는 영역을 나타내는 올바른 `spec.nodeAffinity` 가 있다고 가정하면 지역 클러스터에서 수동으로 프로비저닝된 하나의 영역 볼륨이 지원됩니다.

CCO(Cloud Credential Operator) Mint 모드 또는 Passthrough의 경우 추가 구성이 필요하지 않습니다. 그러나 STS(보안 토큰 서비스)의 경우 STS를 사용하여 하나의 영역 파일 시스템 설정 섹션의 절차를 사용하십시오.

#### 6.10.6.2. STS를 사용하여 하나의 영역 파일 시스템 설정

다음 절차에서는 STS(Security Token Service)를 사용하여 AWS One 영역 파일 시스템을 설정하는 방법을 설명합니다.

사전 요구 사항

cluster-admin 역할을 가진 사용자로 클러스터에 액세스합니다.

AWS 계정 인증 정보

프로세스

STS를 사용하여 하나의 영역 파일 시스템을 구성하려면 다음을 수행합니다.

보안 토큰 서비스의 Amazon 리소스 이름 얻기 섹션 아래의 절차에 따라 `credrequests` 디렉터리에 두 개의

`CredentialsRequests` 를 생성합니다.

컨트롤러

`CredentialsRequest` 의 경우 변경없이 절차를 따르십시오.

드라이버 노드

`CredentialsRequest` 의 경우 다음 예제 파일을 사용합니다.

```yaml
apiVersion: cloudcredential.openshift.io/v1
kind: CredentialsRequest
metadata:
  annotations:
    credentials.openshift.io/role-arns-vars: NODE_ROLEARN
  name: openshift-aws-efs-csi-driver-node
  namespace: openshift-cloud-credential-operator
spec:
  providerSpec:
    apiVersion: cloudcredential.openshift.io/v1
    kind: AWSProviderSpec
    statementEntries:
    - action:
      - elasticfilesystem:DescribeMountTargets
      - ec2:DescribeAvailabilityZones
      effect: Allow
      resource: '*'
  secretRef:
    name: node-aws-efs-cloud-credentials
    namespace: openshift-cluster-csi-drivers
  serviceAccountNames:
  - aws-efs-csi-driver-node-sa
```

1. `metadata.annotations.credentials.openshift.io/role-arns-vars` 를 `NODE_ROLEARN` 로 설정합니다.

```shell-session
2025/08/26 14:05:24 Role arn:aws:iam::269733383066:role/my-arn-1-blll6-openshift-cluster-csi-drivers-aws-efs-cloud-cre created
2025/08/26 14:05:24 Saved credentials configuration to: /home/my-arn/project/go/src/github.com/openshift/myinst/aws-sts-compact-1/manifests/openshift-cluster-csi-drivers-aws-efs-cloud-credentials-credentials.yaml
2025/08/26 14:05:24 Updated Role policy for Role my-arn-1-blll6-openshift-cluster-csi-drivers-aws-efs-cloud-cre
2025/08/26 14:05:24 Role arn:aws:iam::269733383066:role/my-arn-1-blll6-openshift-cluster-csi-drivers-node-aws-efs-clou created
2025/08/26 14:05:24 Saved credentials configuration to: manifests/openshift-cluster-csi-drivers-node-aws-efs-cloud-credentials-credentials.yaml
2025/08/26 14:05:24 Updated Role policy for Role my-arn-1-blll6-openshift-cluster-csi-drivers-node-aws-efs-clou
```

1. 컨트롤러 Amazon 리소스 이름(ARN)

2. 드라이버 노드 ARN

이 절차의 앞부분에서 생성된 컨트롤러 ARN을 사용하여 AWS EFS CSI 드라이버를 설치합니다.

다음과 유사한 명령을 실행하여 Operator의 서브스크립션을 편집하고 드라이버 노드의 ARN으로 `NODE_ROLEARN` 을 추가합니다.

```shell-session
$ oc -n openshift-cluster-csi-drivers edit subscription aws-efs-csi-driver-operator
...
  config:
    env:
    - name: ROLEARN
      value: arn:aws:iam::269733383066:role/my-arn-1-blll6-openshift-cluster-csi-drivers-aws-efs-cloud-cre
    - name: NODE_ROLEARN
      value: arn:aws:iam::269733383066:role/my-arn-1-blll6-openshift-cluster-csi-drivers-node-aws-efs-clou
...
```

1. 컨트롤러 ARN. 이미 존재합니다.

2. 드라이버 노드 ARN

#### 6.10.7. Amazon Elastic File Storage에 대한 동적 프로비저닝

AWS EFS CSI 드라이버는 다른 CSI 드라이버와 다른 형태의 동적 프로비저닝을 지원합니다. 새 PV를 기존 EFS 볼륨의 하위 디렉터리로 프로비저닝합니다. PV는 서로 독립적입니다. 그러나 모두 동일한 EFS 볼륨을 공유합니다. 볼륨이 삭제되면 프로비저닝된 모든 PV도 삭제됩니다. EFS CSI 드라이버는 이러한 각 하위 디렉터리에 대한 AWS 액세스 지점을 생성합니다. AWS AccessPoint 제한으로 인해 단일 `StorageClass` /EFS 볼륨에서 1000 PV만 동적으로 프로비저닝할 수 있습니다.

중요

`PVC.spec.resources` 는 EFS에 의해 적용되지 않습니다.

아래 예제에서는 5GiB의 공간을 요청합니다. 그러나 생성된 PV는 제한적이며 페타바이트와 같이 원하는 양의 데이터를 저장할 수 있습니다. 손상된 애플리케이션이나 불량 애플리케이션도 볼륨에 너무 많은 데이터를 저장할 경우 상당한 비용이 발생할 수 있습니다.

AWS에서 EFS 볼륨 크기를 모니터링하는 것이 좋습니다.

사전 요구 사항

Amazon EFS(Elastic File Storage) 볼륨을 생성했습니다.

AWS EFS 스토리지 클래스를 생성했습니다.

프로세스

동적 프로비저닝을 활성화하려면 다음을 수행합니다.

이전에 만든 `StorageClass` 를 참조하여 PVC(또는 StatefulSet 또는 Template)를 만듭니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test
spec:
  storageClassName: efs-sc
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```

동적 프로비저닝을 설정하는 데 문제가 있는 경우 AWS EFS 문제 해결을 참조하십시오.

추가 리소스

AWS EFS 스토리지 클래스 생성

#### 6.10.8. Amazon Elastic File Storage를 사용하여 정적 PV 생성

동적 프로비저닝 없이 Amazon EFS(Elastic File Storage) 볼륨을 단일 PV로 사용할 수 있습니다. 전체 볼륨이 pod에 마운트됩니다.

사전 요구 사항

Amazon EFS 볼륨을 생성했습니다.

프로세스

다음 YAML 파일을 사용하여 PV를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: efs-pv
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  csi:
    driver: efs.csi.aws.com
    volumeHandle: fs-ae66151a
    volumeAttributes:
      encryptInTransit: "false"
```

1. `spec.capacity` 에는 의미가 없으며 CSI 드라이버에서 무시합니다. PVC에 바인딩할 때만 사용됩니다. 애플리케이션은 볼륨에 원하는 양의 데이터를 저장할 수 있습니다.

2. `volumeHandle` 은 AWS에서 생성한 EFS 볼륨과 동일해야 합니다. 자체 액세스 지점을 제공하는 경우 `volumeHandle` 은 여야 합니다. 예: `fs-6e633ada::fsap-081a1d293f0004630`.

```shell
<EFS volume ID>::<access point ID>
```

3. 필요한 경우 전송 시 암호화를 비활성화할 수 있습니다. 암호화는 기본적으로 활성화되어 있습니다.

정적 PV를 설정하는 데 문제가 있는 경우 AWS EFS 문제 해결을 참조하십시오.

#### 6.10.9. Amazon Elastic File Storage 보안

다음 정보는 Amazon Elastic File Storage(Amazon EFS) 보안에 중요합니다.

예를 들어 앞에서 설명한 대로 동적 프로비저닝을 사용하여 액세스 지점을 사용하는 경우 Amazon은 파일의 GID를 액세스 지점의 GID로 자동으로 대체합니다. 또한 EFS는 파일 시스템 권한을 평가할 때 액세스 지점의 사용자 ID, 그룹 ID 및 보조 그룹 ID를 고려합니다. EFS는 NFS 클라이언트의 ID를 무시합니다. 액세스 지점에 대한 자세한 내용은 https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html 을 참조하십시오.

결과적으로 EFS 볼륨은 FSGroup을 자동으로 무시합니다. OpenShift Container Platform은 볼륨의 파일 GID를 FSGroup으로 대체할 수 없습니다. 마운트된 EFS 액세스 지점에 액세스할 수 있는 모든 Pod는 해당 노드의 모든 파일에 액세스할 수 있습니다.

이와 무관하게 전송 중 암호화는 기본적으로 활성화되어 있습니다. 자세한 내용은 https://docs.aws.amazon.com/efs/latest/ug/encryption-in-transit.html 을 참조하십시오.

#### 6.10.10.1. 사용량 지표 개요

AWS(Amazon Web Services) EBS(Elastic File Service) 스토리지 CSI(Container Storage Interface) 사용량 메트릭을 사용하면 동적으로 또는 정적으로 프로비저닝된 EFS 볼륨에서 사용하는 공간을 모니터링할 수 있습니다.

중요

이 기능은 메트릭을 켜면 성능이 저하될 수 있으므로 기본적으로 비활성화되어 있습니다.

AWS EFS 사용량 메트릭 기능은 볼륨의 파일을 재귀적으로 진행하여 AWS EFS CSI 드라이버에서 볼륨 지표를 수집합니다. 이 노력으로 성능이 저하될 수 있으므로 관리자는 이 기능을 명시적으로 활성화해야 합니다.

#### 6.10.10.2. 웹 콘솔을 사용하여 사용량 메트릭 활성화

웹 콘솔을 사용하여 AWS(Amazon Web Services) EBS(Elastic File Service) CSI(Container Storage Interface) 사용 지표를 활성화하려면 다음을 수행합니다.

Administration > CustomResourceDefinitions 를 클릭합니다.

Name 드롭다운 옆에 있는 CustomResourceDefinitions 페이지에서 `clustercsidriver` 를 입력합니다.

CRD ClusterCSIDriver 를 클릭합니다.

YAML 탭을 클릭합니다.

`spec.aws.efsVolumeMetrics.state` 에서 값을 `RecursiveWalk` 로 설정합니다.

`RecursiveWalk` 는 볼륨의 파일을 재귀적으로 진행하여 AWS EFS CSI 드라이버의 볼륨 메트릭 컬렉션이 수행됨을 나타냅니다.

```yaml
spec:
    driverConfig:
        driverType: AWS
        aws:
            efsVolumeMetrics:
              state: RecursiveWalk
              recursiveWalk:
                refreshPeriodMinutes: 100
                fsRateLimit: 10
```

선택 사항: 재귀우가 작동하는 방법을 정의하려면 다음 필드를 설정할 수도 있습니다.

`refreshPeriodMinutes`: 볼륨 메트릭의 새로 고침 빈도를 분 단위로 지정합니다. 이 필드를 비워 두면 적절한 기본값이 선택되며, 이는 시간이 지남에 따라 변경될 수 있습니다. 현재 기본값은 240분입니다. 유효한 범위는 1 ~ 43,200 분입니다.

`fsRateLimit`: 파일 시스템당 goroutines에서 볼륨 메트릭을 처리하기 위한 속도 제한을 정의합니다. 이 필드를 비워 두면 적절한 기본값이 선택되며, 이는 시간이 지남에 따라 변경될 수 있습니다. 현재 기본값은 5 goroutines입니다. 유효한 범위는 1에서 100 goroutines입니다.

저장 을 클릭합니다.

참고

AWS EFS CSI 사용 지표를 비활성화하려면 이전 절차를 사용하지만 `spec.aws.efsVolumeMetrics.state` 의 경우 값을 `RecursiveWalk` 에서 `Disabled` 로 변경합니다.

#### 6.10.10.3. CLI를 사용하여 사용량 메트릭 활성화

CLI를 사용하여 AWS(Amazon Web Services) EBS(Elastic File Service) 스토리지 CSI(Container Storage Interface) 사용 지표를 활성화하려면 다음을 수행합니다.

다음 명령을 실행하여 ClusterCSIDriver를 편집합니다.

```shell-session
$ oc edit clustercsidriver efs.csi.aws.com
```

`spec.aws.efsVolumeMetrics.state` 에서 값을 `RecursiveWalk` 로 설정합니다.

`RecursiveWalk` 는 볼륨의 파일을 재귀적으로 진행하여 AWS EFS CSI 드라이버의 볼륨 메트릭 컬렉션이 수행됨을 나타냅니다.

```yaml
spec:
    driverConfig:
        driverType: AWS
        aws:
            efsVolumeMetrics:
              state: RecursiveWalk
              recursiveWalk:
                refreshPeriodMinutes: 100
                fsRateLimit: 10
```

선택 사항: 재귀우가 작동하는 방법을 정의하려면 다음 필드를 설정할 수도 있습니다.

`refreshPeriodMinutes`: 볼륨 메트릭의 새로 고침 빈도를 분 단위로 지정합니다. 이 필드를 비워 두면 적절한 기본값이 선택되며, 이는 시간이 지남에 따라 변경될 수 있습니다. 현재 기본값은 240분입니다. 유효한 범위는 1 ~ 43,200 분입니다.

`fsRateLimit`: 파일 시스템당 goroutines에서 볼륨 메트릭을 처리하기 위한 속도 제한을 정의합니다. 이 필드를 비워 두면 적절한 기본값이 선택되며, 이는 시간이 지남에 따라 변경될 수 있습니다. 현재 기본값은 5 goroutines입니다. 유효한 범위는 1에서 100 goroutines입니다.

`efs.csi.aws.com` 오브젝트에 변경 사항을 저장합니다.

참고

AWS EFS CSI 사용 지표를 비활성화하려면 이전 절차를 사용하지만 `spec.aws.efsVolumeMetrics.state` 의 경우 값을 `RecursiveWalk` 에서 `Disabled` 로 변경합니다.

#### 6.10.11. Amazon Elastic File Storage 문제 해결

다음 정보는 Amazon EFS(Elastic File Storage) 문제 해결 방법에 대한 지침을 제공합니다.

AWS EFS Operator 및 CSI 드라이버는 `openshift-cluster-csi-drivers` 에서 실행됩니다.

AWS EFS Operator 및 CSI 드라이버의 로그 수집을 시작하려면 다음 명령을 실행합니다.

```shell-session
$ oc adm must-gather
[must-gather      ] OUT Using must-gather plugin-in image: quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:125f183d13601537ff15b3239df95d47f0a604da2847b561151fedd699f5e3a5
[must-gather      ] OUT namespace/openshift-must-gather-xm4wq created
[must-gather      ] OUT clusterrolebinding.rbac.authorization.k8s.io/must-gather-2bd8x created
[must-gather      ] OUT pod for plug-in image quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:125f183d13601537ff15b3239df95d47f0a604da2847b561151fedd699f5e3a5 created
```

AWS EFS Operator 오류를 표시하려면 `ClusterCSIDriver` 상태를 확인합니다.

```shell-session
$ oc get clustercsidriver efs.csi.aws.com -o yaml
```

```shell-session
$ oc describe pod
...
  Type     Reason       Age    From               Message
  ----     ------       ----   ----               -------
  Normal   Scheduled    2m13s  default-scheduler  Successfully assigned default/efs-app to ip-10-0-135-94.ec2.internal
  Warning  FailedMount  13s    kubelet            MountVolume.SetUp failed for volume "pvc-d7c097e6-67ec-4fae-b968-7e7056796449" : rpc error: code = DeadlineExceeded desc = context deadline exceeded
  Warning  FailedMount  10s    kubelet            Unable to attach or mount volumes: unmounted volumes=[persistent-storage], unattached volumes=[persistent-storage kube-api-access-9j477]: timed out waiting for the condition
```

1. 볼륨이 마운트되지 않았음을 나타내는 경고 메시지입니다.

이 오류는 AWS가 OpenShift Container Platform 노드와 Amazon EFS 간에 패킷을 삭제하기 때문에 발생하는 경우가 많습니다.

다음 사항이 올바른지 확인합니다.

AWS 방화벽 및 보안 그룹

네트워킹: 포트 번호 및 IP 주소

#### 6.10.12. AWS EFS CSI Driver Operator 설치 제거

모든 EFS PV는 AWS EFS CSI Driver Operator (Red Hat Operator)를 설치 제거한 후 액세스할 수 없습니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

프로세스

웹 콘솔에서 AWS EFS CSI Driver Operator를 설치 제거하려면 다음을 수행합니다.

웹 콘솔에 로그인합니다.

AWS EFS PV를 사용하는 모든 애플리케이션을 중지합니다.

모든 AWS EFS PV를 삭제합니다.

스토리지 → 영구 볼륨 클레임 을 클릭합니다.

AWS EFS CSI Driver Operator에서 사용 중인 각 PVC를 선택하고 PVC 오른쪽에 있는 드롭다운 메뉴를 클릭한 다음 영구 볼륨 클레임 삭제 를 클릭합니다.

AWS EFS CSI 드라이버를 설치 제거합니다.

참고

Operator를 설치 제거하려면 CSI 드라이버를 먼저 제거해야 합니다.

Administration → CustomResourceDefinitions → ClusterCSIDriver 를 클릭합니다.

인스턴스 탭에서 efs.csi.aws.com 의 맨 왼쪽에 있는 드롭다운 메뉴를 클릭한 다음 ClusterCSIDriver 삭제 를 클릭합니다.

메시지가 표시되면 삭제 를 클릭합니다.

AWS EFS CSI Operator를 설치 제거합니다.

Ecosystem → 설치된 Operators를 클릭합니다.

설치된 Operators 페이지에서 스크롤하거나 AWS EFS CSI를 이름으로 검색 상자에 입력하여 Operator를 찾은 다음 클릭합니다.

설치된 Operator > Operator 세부 정보 페이지 오른쪽 상단에서 작업 → Operator 설치 제거 를 클릭합니다.

Operator 설치 제거 창이 표시되면 제거 버튼을 클릭하여 네임스페이스에서 Operator를 제거합니다. 클러스터에 Operator가 배포한 애플리케이션을 수동으로 정리해야 합니다.

설치 제거 후 AWS EFS CSI Driver Operator는 더 이상 웹 콘솔의 설치된 Operator 섹션에 나열되지 않습니다.

참고

클러스터(`openshift-install destroy cluster`)를 제거하려면 먼저 AWS에서 EFS 볼륨을 삭제해야 합니다. 클러스터의 VPC를 사용하는 EFS 볼륨이 있는 경우 OpenShift Container Platform 클러스터를 삭제할 수 없습니다. Amazon에서는 이러한 VPC를 삭제할 수 없습니다.

#### 6.10.13. 추가 리소스

CSI 볼륨 구성

#### 6.11.1. 개요

OpenShift Container Platform은 Microsoft Azure Disk Storage용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

Azure Disk 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 Azure Disk CSI Driver Operator 및 Azure Disk CSI 드라이버를 설치합니다.

Azure Disk CSI Driver Operator 는 PVC(영구 볼륨 클레임)를 생성하는 데 사용할 수 있는 `managed-csi` 라는 스토리지 클래스를 제공합니다. Azure Disk CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있도록 하여 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없어 동적 볼륨 프로비저닝을 지원합니다. 필요한 경우 이 기본 스토리지 클래스를 비활성화할 수 있습니다(기본 스토리지 클래스 관리 참조).

Azure Disk CSI 드라이버 를 사용하면 Azure Disk PV를 생성 및 마운트할 수 있습니다.

#### 6.11.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

참고

OpenShift Container Platform은 동등한 CSI 드라이버로 Azure Disk in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 제공합니다. 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

#### 6.11.3. 스토리지 계정 유형을 사용하여 스토리지 클래스 생성

스토리지 클래스는 스토리지 수준 및 사용량을 구분하고 조정하는 데 사용됩니다. 스토리지 클래스를 정의하면 동적으로 프로비저닝된 영구 볼륨을 얻을 수 있습니다.

스토리지 클래스를 생성할 때 스토리지 계정 유형을 지정할 수 있습니다. 이는 Azure 스토리지 계정 SKU 계층에 해당합니다. 유효한 옵션은 `Standard_LRS`, `Premium_LRS`, `StandardSSD_LRS`, `UltraSSD_LRS`, UltraSSD_LRS, `Premium_ZRS`, `StandardSSD_ZRS`, `PremiumV2_LRS` 입니다. Azure SKU 계층을 찾는 방법에 대한 자세한 내용은 SKU 유형을 참조하십시오.

ZRS 및 PremiumV2_LRS 모두 일부 지역 제한이 있습니다. 이러한 제한 사항에 대한 자세한 내용은 ZRS 제한 사항 및 Premium_LRS 제한을 참조하십시오.

사전 요구 사항

관리자 권한을 사용하여 OpenShift Container Platform 클러스터에 액세스

프로세스

다음 단계를 사용하여 스토리지 계정 유형의 스토리지 클래스를 생성합니다.

다음과 유사한 YAML 파일을 사용하여 스토리지 계정 유형을 지정하는 스토리지 클래스를 생성합니다.

```shell-session
$ oc create -f - << EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <storage-class>
provisioner: disk.csi.azure.com
parameters:
  skuName: <storage-class-account-type>
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
EOF
```

1. 스토리지 클래스 이름입니다.

2. 스토리지 계정 유형. 이는 Azure 스토리지 계정 SKU 계층('Standard_LRS', `Premium_LRS`, `StandardSSD_LRS`, `UltraSSD_LRS`, `Premium_ZRS`, `StandardSSD_ZRS`, `PremiumV2_LRS`)에 해당합니다.

참고

PremiumV2_LRS의 경우 `storageclass.parameters` 에서 `cachingMode: None` 을 지정합니다.

스토리지 클래스를 나열하여 스토리지 클래스가 생성되었는지 확인합니다.

```shell-session
$ oc get storageclass
```

```shell-session
$ oc get storageclass
NAME                    PROVISIONER          RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
azurefile-csi           file.csi.azure.com   Delete          Immediate              true                   68m
managed-csi (default)   disk.csi.azure.com   Delete          WaitForFirstConsumer   true                   68m
sc-prem-zrs             disk.csi.azure.com   Delete          WaitForFirstConsumer   true                   4m25s
```

1. 스토리지 계정 유형의 새 스토리지 클래스입니다.

#### 6.11.4.1. 개요

성능 +를 활성화하면 513GiB 이상의 다음과 같은 디스크 유형에 대해 IOPS(초당 입력/출력 작업) 및 처리량 제한을 늘릴 수 있습니다.

Azure 프리미엄 SSD(Solid-State Drive)

표준 SSD

표준 하드 디스크 드라이브(HDD)

IOPS 및 처리량에 대한 제한 증가를 보려면 VM 디스크의 확장 기능 및 성능 대상 에서 Expanded 로 시작하는 열을 참조하십시오.

#### 6.11.4.2. 제한

Azure Disk의 성능 추가에는 다음과 같은 제한 사항이 있습니다.

513GiB 이상의 표준 HDD, 표준 SSD 및 프리미엄 SSD 관리 디스크에서만 활성화할 수 있습니다.

중요

더 작은 값을 요청하면 디스크 크기가 513GiB까지 반올림됩니다.

새 디스크에서만 활성화할 수 있습니다. 해결 방법은 스냅 샷 또는 복제를 통해 성능 활성화 섹션(Enabling performance plus by snapshot or cloning)을 참조하십시오.

#### 6.11.4.3. 성능 및 향상된 디스크를 사용하는 스토리지 클래스 생성

다음 절차에서는 성능 및 향상된 Azure 디스크를 사용하기 위해 스토리지 클래스를 생성하는 방법을 설명합니다.

사전 요구 사항

cluster-admin 권한이 있는 Microsoft Azure 클러스터에 액세스할 수 있습니다.

성능 및 기능이 활성화된 Azure 디스크에 액세스할 수 있습니다.

디스크에서 성능 및 성능을 활성화하는 방법에 대한 자세한 내용은 Microsoft Azure 스토리지 설명서를 참조하십시오.

프로세스

성능 및 향상된 디스크를 사용하는 스토리지 클래스를 생성하려면 다음을 수행합니다.

다음 예제 YAML 파일을 사용하여 스토리지 클래스를 생성합니다.

```plaintext
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <azure-disk-performance-plus-sc>
provisioner: disk.csi.azure.com
parameters:
  skuName: Premium_LRS
  cachingMode: ReadOnly
  enablePerformancePlus: "true"
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

1. StorageClass의 이름입니다.

2. CSI(Azure Disk Container Storage Interface) 드라이버 프로비저너를 지정합니다.

3. Azure 디스크 유형 SKU를 지정합니다. 이 예에서는 Premium SSD 로컬 중복 스토리지의 `Premium_LRS` 입니다.

4. Azure Disk 성능 및 기능을 활성화합니다.

다음 예제 YAML 파일을 사용하여 이 스토리지 클래스를 사용하는 PVC(영구 볼륨 클레임)를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <my-azure-pvc>
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: <azure-disk-performance-plus-sc>
  resources:
    requests:
      storage: 513Gi
```

1. PVC 이름입니다.

2. 성능 및 스토리지 클래스를 참조합니다.

3. 513GiB보다 작은 디스크 크기는 자동으로 반올림됩니다.

#### 6.11.4.4. 스냅샷 또는 복제로 성능 추가 활성화

일반적으로 성능 추가는 새 디스크에서만 활성화할 수 있습니다. 해결방법은 다음 절차를 사용할 수 있습니다.

사전 요구 사항

cluster-admin 권한이 있는 Microsoft Azure 클러스터에 액세스할 수 있습니다.

성능 및 기능이 활성화된 Azure 디스크에 액세스할 수 있습니다.

성능 및 향상된 Azure 디스크를 사용하는 스토리지 클래스를 생성했습니다.

스토리지 클래스 생성에 대한 자세한 내용은 성능 및 향상된 디스크를 사용할 스토리지 클래스 생성 섹션을 참조하십시오.

프로세스

스냅샷 또는 복제를 통해 성능을 추가하려면 다음을 수행합니다.

성능 및 성능이 활성화되어 있지 않은 기존 볼륨의 스냅샷을 생성합니다.

`enablePerformance` Cryostat가 "true"로 설정된 스토리지 클래스를 사용하여 해당 스냅샷에서 새 디스크를 프로비저닝합니다.

또는

`enablePerformance` Cryostat를 "true"로 설정하여 새 디스크 복제본을 생성하는 스토리지 클래스를 사용하여 PVC(영구 볼륨 클레임)를 복제합니다.

#### 6.11.5. 사용자 관리 암호화

사용자 관리 암호화 기능을 사용하면 OpenShift Container Platform 노드 루트 볼륨을 암호화하는 설치 중에 키를 제공하고 모든 관리 스토리지 클래스가 이러한 키를 사용하여 프로비저닝된 스토리지 볼륨을 암호화할 수 있습니다. install-config YAML 파일의 `platform.<cloud_type>.defaultMachinePlatform` 필드에 사용자 지정 키를 지정해야 합니다.

이 기능은 다음 스토리지 유형을 지원합니다.

AWS(Amazon Web Services) EBS(Elastic Block Storage)

Microsoft Azure Disk 스토리지

GCP(Google Cloud Platform) PD(영구 디스크) 스토리지

IBM Virtual Private Cloud (VPC) 블록 스토리지

참고

OS(root) 디스크가 암호화되고 스토리지 클래스에 정의된 암호화된 키가 없는 경우 Azure Disk CSI 드라이버는 기본적으로 OS 디스크 암호화 키를 사용하여 프로비저닝된 스토리지 볼륨을 암호화합니다.

Azure의 사용자 관리 암호화를 사용하여 설치하는 방법에 대한 자세한 내용은 Azure에 대한 사용자 관리 암호화 활성화를 참조하십시오.

#### 6.11.6. PVC를 사용하여 울트라 디스크가 있는 머신을 배포하는 머신 세트

Azure에서 실행되는 머신 세트를 생성하여 울트라 디스크가 있는 머신을 배포할 수 있습니다. Ultra 디스크는 가장 까다로운 데이터 워크로드에 사용하기 위한 고성능 스토리지입니다.

in-tree 플러그인과 CSI 드라이버는 모두 PVC를 사용하여 울트라 디스크를 활성화합니다. PVC를 생성하지 않고 울트라 디스크가 있는 머신을 데이터 디스크로 배포할 수도 있습니다.

추가 리소스

Microsoft Azure Ultra 디스크 문서

트리 내 PVC를 사용하여 울트라 디스크에 머신을 배포하는 머신 세트

울트라 디스크에 머신을 데이터 디스크로 배포하는 머신 세트

#### 6.11.6.1. 머신 세트를 사용하여 울트라 디스크가 있는 머신 생성

머신 세트 YAML 파일을 편집하여 Azure에 울트라 디스크가 있는 머신을 배포할 수 있습니다.

사전 요구 사항

기존 Microsoft Azure 클러스터가 있어야 합니다.

프로세스

기존 Azure `MachineSet` CR(사용자 정의 리소스)을 복사하고 다음 명령을 실행하여 편집합니다.

```shell-session
$ oc edit machineset <machine_set_name>
```

여기서 `<machine_set_name` >은 울트라 디스크가 있는 머신을 프로비저닝하려는 머신 세트입니다.

표시된 위치에 다음 행을 추가합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
spec:
  template:
    spec:
      metadata:
        labels:
          disk: ultrassd
      providerSpec:
        value:
          ultraSSDCapability: Enabled
```

1. 이 머신 세트에서 생성한 노드를 선택하는 데 사용할 라벨을 지정합니다. 이 절차에서는 이 값에 `disk.ultrassd` 를 사용합니다.

2. 이 라인은 울트라 디스크를 사용할 수 있습니다.

다음 명령을 실행하여 업데이트된 구성을 사용하여 머신 세트를 생성합니다.

```shell-session
$ oc create -f <machine_set_name>.yaml
```

다음 YAML 정의가 포함된 스토리지 클래스를 생성합니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ultra-disk-sc
parameters:
  cachingMode: None
  diskIopsReadWrite: "2000"
  diskMbpsReadWrite: "320"
  kind: managed
  skuname: UltraSSD_LRS
provisioner: disk.csi.azure.com
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

1. 스토리지 클래스의 이름을 지정합니다. 이 절차에서는 이 값에 `Ultra-disk-sc` 를 사용합니다.

2. 스토리지 클래스의 IOPS 수를 지정합니다.

3. 스토리지 클래스의 처리량(MBps)을 지정합니다.

4. AKS(Azure Kubernetes Service) 버전 1.21 이상의 경우 `disk.csi.azure.com` 을 사용합니다. 이전 버전의 AKS의 경우 `kubernetes.io/azure-disk` 를 사용합니다.

5. 선택 사항: 디스크를 사용할 Pod 생성을 기다리려면 이 매개변수를 지정합니다.

다음 YAML 정의가 포함된 `Ultra-disk-sc` 스토리지 클래스를 참조하는 PVC(영구 볼륨 클레임)를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ultra-disk
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: ultra-disk-sc
  resources:
    requests:
      storage: 4Gi
```

1. PVC 이름을 지정합니다. 이 절차에서는 이 값에 `Ultra-disk` 를 사용합니다.

2. 이 PVC는 `Ultra-disk-sc` 스토리지 클래스를 참조합니다.

3. 스토리지 클래스의 크기를 지정합니다. 최소 값은 `4Gi` 입니다.

다음 YAML 정의가 포함된 Pod를 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-ultra
spec:
  nodeSelector:
    disk: ultrassd
  containers:
  - name: nginx-ultra
    image: alpine:latest
    command:
      - "sleep"
      - "infinity"
    volumeMounts:
    - mountPath: "/mnt/azure"
      name: volume
  volumes:
    - name: volume
      persistentVolumeClaim:
        claimName: ultra-disk
```

1. 울트라 디스크를 사용할 수 있는 머신 세트의 레이블을 지정합니다. 이 절차에서는 이 값에 `disk.ultrassd` 를 사용합니다.

2. 이 Pod는 `Ultra-disk` PVC를 참조합니다.

검증

다음 명령을 실행하여 머신이 생성되었는지 확인합니다.

```shell-session
$ oc get machines
```

시스템은 `Running` 상태여야 합니다.

실행 중이고 노드가 연결된 시스템의 경우 다음 명령을 실행하여 파티션을 검증합니다.

```shell-session
$ oc debug node/<node_name> -- chroot /host lsblk
```

이 명령에서 >은 노드 < `node_name` >에서 디버깅 쉘을 시작하고 `--` --로 명령을 전달합니다. 전달된 명령 는 기본 호스트 OS 바이너리에 대한 액세스를 제공하며 `lsblk` 에는 호스트 OS 시스템에 연결된 블록 장치가 표시됩니다.

```shell
oc debug node/<node_name
```

```shell
chroot /host
```

다음 단계

Pod 내에서 울트라 디스크를 사용하려면 마운트 지점을 사용하는 워크로드를 생성합니다. 다음 예와 유사한 YAML 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssd-benchmark1
spec:
  containers:
  - name: ssd-benchmark1
    image: nginx
    ports:
      - containerPort: 80
        name: "http-server"
    volumeMounts:
    - name: lun0p1
      mountPath: "/tmp"
  volumes:
    - name: lun0p1
      hostPath:
        path: /var/lib/lun0p1
        type: DirectoryOrCreate
  nodeSelector:
    disktype: ultrassd
```

#### 6.11.6.2. 울트라 디스크를 활성화하는 머신 세트의 리소스 문제 해결

이 섹션의 정보를 사용하여 발생할 수 있는 문제를 이해하고 복구하십시오.

#### 6.11.6.2.1. 울트라 디스크가 지원하는 영구 볼륨 클레임을 마운트할 수 없음

울트라 디스크가 지원하는 영구 볼륨 클레임을 마운트하는 데 문제가 있으면 Pod가 `ContainerCreating` 상태로 중단되고 경고가 트리거됩니다.

예를 들어, pod를 호스팅하는 노드를 백업하는 시스템에 `additionalCapabilities.ultraSSDEnabled` 매개변수가 설정되지 않은 경우 다음 오류 메시지가 표시됩니다.

```shell-session
StorageAccountType UltraSSD_LRS can be used only when additionalCapabilities.ultraSSDEnabled is set.
```

이 문제를 해결하려면 다음 명령을 실행하여 Pod를 설명합니다.

```shell-session
$ oc -n <stuck_pod_namespace> describe pod <stuck_pod_name>
```

#### 6.11.7. 추가 리소스

Azure Disk를 사용하는 영구 스토리지

CSI 볼륨 구성

Microsoft Azure 스토리지 문서

#### 6.12.1. 개요

OpenShift Container Platform은 Microsoft Azure File Storage용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

Azure File 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 Azure File CSI Driver Operator 및 Azure File CSI 드라이버를 설치합니다.

Azure File CSI Driver Operator 는 PVC(영구 볼륨 클레임)를 생성하는 데 사용할 수 있는 `azurefile-csi` 라는 스토리지 클래스를 제공합니다. 필요한 경우 이 기본 스토리지 클래스를 비활성화할 수 있습니다(기본 스토리지 클래스 관리 참조).

Azure File CSI 드라이버 를 사용하면 Azure File PV를 생성하고 마운트할 수 있습니다. Azure File CSI 드라이버는 필요에 따라 스토리지 볼륨을 생성할 수 있으므로 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없어 동적 볼륨 프로비저닝을 지원합니다.

Azure File CSI Driver Operator는 다음을 지원하지 않습니다.

가상 하드 디스크(VHD)

FIPS(Federal Information Processing Standard) 모드가 있는 노드에서는 SMB(Server Message Block) 파일 공유에 대해 활성화됩니다. 그러나 NFS(네트워크 파일 시스템)는 FIPS 모드를 지원합니다.

지원되는 기능에 대한 자세한 내용은 지원되는 CSI 드라이버 및 기능을 참조하십시오.

#### 6.12.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.12.3. NFS 지원

OpenShift Container Platform 4.14 이상에서는 다음 주의 사항과 함께 NFS(Network File System) Driver Operator를 지원합니다.

컨트롤 플레인 노드에 예약된 Azure File NFS 볼륨을 사용하여 Pod를 생성하면 마운트가 거부됩니다.

이 문제를 해결하려면 컨트롤 플레인 노드를 예약할 수 있고 작업자 노드에서 Pod를 실행할 수 있는 경우 `nodeSelector` 또는 Affinity를 사용하여 작업자 노드에서 Pod를 예약합니다.

FS 그룹 정책 동작:

중요

NFS를 사용하는 Azure File CSI는 Pod에서 요청한 fsGroupChangePolicy를 준수하지 않습니다. NFS를 사용하는 Azure File CSI는 Pod에서 요청한 정책에 관계없이 기본 OnRootMismatch FS 그룹 정책을 적용합니다.

Azure File CSI Operator는 NFS의 스토리지 클래스를 자동으로 생성하지 않습니다. 수동으로 생성해야 합니다. 다음과 유사한 파일을 사용합니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <storage-class-name>
provisioner: file.csi.azure.com
parameters:
  protocol: nfs
  skuName: Premium_LRS  # available values: Premium_LRS, Premium_ZRS
mountOptions:
  - nconnect=4
```

1. 스토리지 클래스 이름입니다.

2. Azure File CSI 공급자를 지정합니다.

3. NFS를 스토리지 백엔드 프로토콜로 지정합니다.

#### 6.12.4. Azure 파일 간 서브스크립션 지원

서브스크립션 간 지원을 통해 하나의 Azure 서브스크립션에 OpenShift Container Platform 클러스터를 보유하고 CSI(Azure File Container Storage Interface) 드라이버를 사용하여 다른 Azure 서브스크립션에 Azure 파일 공유를 마운트할 수 있습니다.

중요

OpenShift Container Platform 클러스터와 Azure File 공유(사전 프로비저닝 또는 프로비저닝) 둘 다 동일한 테넌트 내에 있어야 합니다.

#### 6.12.4.1. Azure File 서브스크립션 간 동적 프로비저닝

사전 요구 사항

서비스 주체 또는 관리 ID를 하나의 서브스크립션에서 Azure ID로 사용하여 Azure에 설치된 OpenShift Container Platform 클러스터(서브스크립션 A라고 함)

클러스터와 동일한 테넌트에 있는 스토리지를 사용하여 다른 서브스크립션(서브스크립션 B라고 함)에 액세스

Azure CLI에 로그인

프로세스

서브스크립션 간에 Azure File 동적 프로비저닝을 사용하려면 다음을 수행합니다.

다음 적용 가능한 명령을 실행하여 Azure ID(서비스 주체 또는 관리 ID)를 기록합니다. Azure ID는 이후 단계에서 필요합니다.

```shell-session
$ sp_id=$(oc -n openshift-cluster-csi-drivers get secret azure-file-credentials -o jsonpath='{.data.azure_client_id}' | base64 --decode)
```

```shell-session
$ az ad sp show --id ${sp_id} --query displayName --output tsv
```

```shell-session
$ mi_id=$(oc -n openshift-cluster-csi-drivers get secret azure-file-credentials -o jsonpath='{.data.azure_client_id}' | base64 --decode)
```

```shell-session
$ az identity list --query "[?clientId=='${mi_id}'].{Name:name}" --output tsv
```

다음 중 하나를 수행하여 Azure File 공유를 프로비저닝하려는 다른 서브스크립션 B의 리소스 그룹에 액세스할 수 있는 Azure ID(서비스 주체 또는 관리 ID) 권한을 부여합니다.

다음 Azure CLI 명령을 실행합니다.

```shell-session
az role assignment create \
  --assignee <object-id-or-app-id> \
  --role <role-name> \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>
```

다음과 같습니다.

`<object-id-or-app-id` >: `sp_id` 또는 `mi_id` 와 같이 이전 단계에서 얻은 서비스 주체 또는 관리 ID입니다.

`<role-name&` gt;: 역할 이름입니다. 필요한 권한으로 기여자 또는 자체 역할.

`<subscription-id&` gt;: 서브스크립션 B ID.

`<resource-group-name&` gt;: 서브스크립션 B 리소스 그룹 이름입니다.

또는

Azure 포털에 로그인하여 왼쪽 메뉴에서 리소스 그룹을 클릭합니다.

리소스 그룹 → 액세스 제어(IAM) → 역할 할당 탭을 클릭하여 역할을 할당할 서브스크립션 B에서 리소스 그룹을 선택한 다음, 추가 > 역할 할당 추가

를 클릭합니다.

역할 탭에서 할당할 기여자 역할을 선택한 다음 다음을 클릭합니다. 필요한 권한으로 자체 역할을 생성하고 선택할 수도 있습니다.

멤버 탭에서 다음을 수행합니다.

할당자 유형: 사용자, 그룹 또는 서비스 주체(또는 관리 ID)를 선택하여 할당자를 선택합니다.

멤버 선택을 클릭합니다.

이전 단계에서 기록된 원하는 서비스 주체 또는 관리 ID를 검색한 다음 선택합니다.

Select 를 클릭하여 확인합니다.

Review + assign 탭에서 설정을 검토합니다.

역할 할당을 완료하려면 검토 + 할당 을 클릭합니다.

참고

특정 스토리지 계정을 사용하여 Azure File 공유를 프로비저닝하려면 유사한 단계를 사용하여 스토리지 계정에 액세스할 수 있는 Azure ID(서비스 주체 또는 관리 ID) 권한을 얻을 수도 있습니다.

다음과 유사한 구성을 사용하여 Azure File 스토리지 클래스를 생성합니다.

```yaml
allowVolumeExpansion: true
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <sc-name>
mount options:
  - mfsymlinks
  - cache=strict
  - nosharesock
  - actimeo=30
parameters:
  subscriptionID: <xxxx-xxxx-xxxx-xxxx-xxxx>
  resourceGroup: <resource group name>
  storageAccount: <storage account>
  skuName: <skuName>
provisioner: file.csi.azure.com
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

1. 스토리지 클래스의 이름

2. 서브스크립션 B ID

3. 서브스크립션 B 리소스 그룹 이름

4. 자체 지정하려는 경우 스토리지 계정 이름입니다.

5. SKU 유형의 이름

다음과 유사한 구성을 사용하여 이전 단계에서 생성한 Azure File 스토리지 클래스를 지정하는 PVC(영구 볼륨 클레임)를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <pvc-name>
spec:
  storageClassName: <sc-name-cross-sub>
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```

1. PVC의 이름입니다.

2. 이전 단계에서 생성한 스토리지 클래스의 이름입니다.

#### 6.12.4.2. PV 및 PVC를 생성하여 Azure File 서브스크립션 간 정적 프로비저닝

사전 요구 사항

서비스 주체 또는 관리 ID를 하나의 서브스크립션에서 Azure ID로 사용하여 Azure에 설치된 OpenShift Container Platform 클러스터(서브스크립션 A라고 함)

클러스터와 동일한 테넌트에 있는 스토리지를 사용하여 다른 서브스크립션(서브스크립션 B라고 함)에 액세스

Azure CLI에 로그인

프로세스

Azure File 공유의 경우 리소스 그룹, 스토리지 계정, 스토리지 계정 키 및 Azure File 이름을 기록합니다. 이러한 값은 다음 단계에 사용됩니다.

다음 명령을 실행하여 영구 볼륨 매개변수 `spec.csi.nodeStageSecretRef.name` 의 시크릿을 생성합니다.

```shell-session
$ oc create secret generic azure-storage-account-<storageaccount-name>-secret --from-literal=azurestorageaccountname="<azure-storage-account-name>" --from-literal azurestorageaccountkey="<azure-storage-account-key>" --type=Opaque
```

여기서 < `azure-storage-account-name` > 및 < `azure-storage-account-key` >는 1단계에서 각각 기록한 Azure 스토리지 계정 이름과 키입니다.

다음 예제 파일과 유사한 구성을 사용하여 PV(영구 볼륨)를 생성합니다.

```shell-session
apiVersion: v1
kind: PersistentVolume
metadata:
  annotations:
    pv.kubernetes.io/provisioned-by: file.csi.azure.com
  name: <pv-name>
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: <sc-name>
  mountOptions:
    - cache=strict
    - nosharesock
    - actimeo=30
    - nobrl
  csi:
    driver: file.csi.azure.com
    volumeHandle: "{resource-group-name}#{storage-account-name}#{file-share-name}"
    volumeAttributes:
      shareName: <existing-file-share-name>
    nodeStageSecretRef:
      name: <secret-name>
      namespace: <secret-namespace>
```

1. PV의 이름입니다.

2. PV의 크기입니다.

3. 스토리지 클래스 이름입니다.

4. `volumeHandle` 이 클러스터의 모든 동일한 공유에 대해 고유한지 확인합니다.

5. 의<existing-file-share-name> 경우 전체 경로가 아닌 파일 공유 이름만 사용합니다.

6. 이전 단계에서 생성한 시크릿 이름입니다.

7. 시크릿이 있는 네임스페이스입니다.

다음과 유사한 구성을 사용하여 1단계에서 참조하는 기존 Azure File 공유를 지정하는 PVC(영구 값 클레임)를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <pvc-name>
spec:
  storageClassName: <sc-name>
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```

1. PVC의 이름입니다.

2. 이전 단계에서 PV에 지정한 스토리지 클래스의 이름입니다.

스토리지 클래스 사용 권장 사항

서브스크립션 간 정적 프로비저닝 예에서는 정적 프로비저닝을 수행하는 데 스토리지 클래스가 필요하지 않으므로 PV 및 PVC에서 참조하는 스토리지 클래스는 엄격하게 필요하지 않습니다. 그러나 스토리지 클래스를 사용하여 수동으로 생성된 PVC가 실수로 생성된 PV와 일치하지 않는 경우가 발생하지 않으므로 새 PV의 동적 프로비저닝을 트리거할 수 있습니다. 이 문제를 방지하는 다른 방법은 `provisioner: kubernetes.io/no-provisioner` 를 사용하여 스토리지 클래스를 생성하거나 존재하지 않는 스토리지 클래스를 참조하는 것입니다. 이 경우 두 경우 모두 동적 프로비저닝이 발생하지 않습니다. 이러한 전략 중 하나를 사용하는 경우 잘못 일치하는 PV 및 PVC가 발생하면 PVC가 보류 중 상태로 유지되며 오류를 수정할 수 있습니다.

#### 6.12.5. Azure File의 정적 프로비저닝

정적 프로비저닝을 위해 클러스터 관리자는 실제 스토리지의 세부 정보를 정의하는 PV(영구 볼륨)를 생성합니다. 그런 다음 클러스터 사용자는 이러한 PV를 사용하는 PVC(영구 볼륨 클레임)를 생성할 수 있습니다.

사전 요구 사항

관리자 권한을 사용하여 OpenShift Container Platform 클러스터에 액세스

프로세스

Azure 파일에 정적 프로비저닝을 사용하려면 다음을 수행합니다.

Azure 스토리지 계정에 대한 시크릿을 아직 생성하지 않은 경우 지금 생성합니다.

이 시크릿에는 다음과 같은 매우 구체적인 형식의 Azure 스토리지 계정 이름과 키가 두 개의 키-값 쌍을 포함해야 합니다.

`azurestorageaccountname`: <storage_account_name>

`azurestorageaccountkey`: <account_key>

azure-secret 이라는 보안을 생성하려면 다음 명령을 실행합니다.

```shell-session
oc create secret generic azure-secret  -n <namespace_name> --type=Opaque --from-literal=azurestorageaccountname="<storage_account_name>" --from-literal=azurestorageaccountkey="<account_key>"
```

1. & `lt;namespace_name&` gt;을 PV가 사용되는 네임스페이스로 설정합니다.

2. <.

```shell
storage_account_name> 및 < account_ key>에 대한 값을 제공합니다
```

다음 예제 YAML 파일을 사용하여 PV를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  annotations:
    pv.kubernetes.io/provisioned-by: file.csi.azure.com
  name: pv-azurefile
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: <sc-name>
  mountOptions:
    - dir_mode=0777
    - file_mode=0777
    - uid=0
    - gid=0
    - cache=strict
    - nosharesock
    - actimeo=30
    - nobrl
  csi:
    driver: file.csi.azure.com
    volumeHandle: "{resource-group-name}#{account-name}#{file-share-name}"
    volumeAttributes:
      shareName: EXISTING_FILE_SHARE_NAME
    nodeStageSecretRef:
      name: azure-secret
      namespace: <my-namespace>
```

1. 볼륨 크기.

2. 액세스 모드. 읽기-쓰기 및 마운트 권한을 정의합니다. 자세한 내용은 추가 리소스 에서 액세스 모드를 참조하십시오.

3. 회수 정책. 해제 후 볼륨을 사용하여 클러스터에 수행할 작업을 지시합니다. 허용되는 값은 `Retain`, `Recycle` 또는 `Delete` 입니다.

4. 스토리지 클래스 이름입니다. 이 이름은 PVC에서 이 특정 PV에 바인딩하는 데 사용됩니다. 정적 프로비저닝의 경우 `StorageClass` 오브젝트가 존재할 필요는 없지만 PV 및 PVC의 이름이 일치해야 합니다.

5. 보안을 강화하려면 이 권한을 수정합니다.

6. 캐시 모드. 허용되는 값은 `none`, `strict` 및 `loose` 입니다. 기본값은 `strict` 입니다.

7. 재연결 레이스 가능성을 줄이기 위해 를 사용합니다.

8. CIFS 클라이언트가 서버에서 속성 정보를 요청하기 전에 파일 또는 디렉터리의 속성을 캐시하는 시간(초)입니다.

9. 서버에 대한 바이트 범위 잠금 요청 및 POSIX 잠금에 문제가 있는 애플리케이션에 대해 전송을 비활성화합니다.

10. `volumeHandle` 이 클러스터 전체에서 고유해야 합니다. `resource-group-name` 은 스토리지 계정이 있는 Azure 리소스 그룹입니다.

11. 파일 공유 이름. 파일 공유 이름만 사용합니다. 전체 경로를 사용하지 마십시오.

12. 이 절차의 1단계에서 생성된 시크릿 이름을 제공합니다. 이 예에서는 azure-secret 입니다.

13. 시크릿이 생성된 네임스페이스입니다. PV를 사용하는 네임스페이스여야 합니다.

다음 예제 파일을 사용하여 PV를 참조하는 PVC를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <pvc-name>
  namespace: <my-namespace>
spec:
  volumeName: pv-azurefile
  storageClassName: <sc-name>
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```

1. PVC 이름입니다.

2. PVC의 네임스페이스입니다.

3. 이전 단계에서 생성한 PV의 이름입니다.

4. 스토리지 클래스 이름입니다. 이 이름은 PVC에서 이 특정 PV에 바인딩하는 데 사용됩니다. 정적 프로비저닝의 경우 `StorageClass` 오브젝트가 존재할 필요는 없지만 PV 및 PVC의 이름이 일치해야 합니다.

5. 액세스 모드. PVC에 대해 요청된 읽기-쓰기 액세스를 정의합니다. 클레임은 특정 액세스 모드로 스토리지를 요청할 때 볼륨과 동일한 규칙을 사용합니다. 자세한 내용은 추가 리소스 에서 액세스 모드를 참조하십시오.

6. PVC 크기.

다음 명령을 실행하여 PVC가 생성되고 `Bound` 상태에 있는지 확인합니다.

```shell-session
$ oc get pvc <pvc-name>
```

1. PVC의 이름입니다.

```shell-session
NAME       STATUS    VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS   AGE
pvc-name   Bound     pv-azurefile   5Gi        ReadWriteMany  my-sc          7m2s
```

추가 리소스

Azure File을 사용하는 영구 스토리지

CSI 볼륨 구성

액세스 모드

#### 6.13.1. 개요

OpenShift Container Platform은 Azure Stack Hub 스토리지용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다. Azure Stack 포트폴리오의 일부인 Azure Stack Hub를 사용하면 온프레미스 환경에서 앱을 실행하고 데이터 센터에 Azure 서비스를 제공할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

Azure Stack Hub 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 Azure Stack Hub CSI 드라이버 및 Azure Stack Hub CSI 드라이버를 설치합니다.

Azure Stack Hub CSI Driver Operator 는 스토리지 클래스(`managed-csi`)에 기본 스토리지 계정 유형으로 "Standard_LRS"를 제공하여 PVC(영구 볼륨 클레임)를 생성할 수 있습니다. Azure Stack Hub CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있도록 하여 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없어 동적 볼륨 프로비저닝을 지원합니다.

Azure Stack Hub CSI 드라이버 를 사용하면 Azure Stack Hub PV를 생성하고 마운트할 수 있습니다.

#### 6.13.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.13.3. 추가 리소스

CSI 볼륨 구성

#### 6.14.1. 개요

OpenShift Container Platform은 GCP(Google Cloud Platform) PD(영구 디스크) 스토리지용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI(Container Storage Interface) Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

GCP PD 스토리지 자산에 마운트하는 CSI(영구 볼륨)를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에서 기본적으로 GCP PD CSI Driver Operator 및 GCP PD CSI 드라이버를 설치합니다.

GCP PD CSI Driver Operator: 기본적으로 Operator는 PVC를 생성하는 데 사용할 수 있는 스토리지 클래스를 제공합니다. 필요한 경우 이 기본 스토리지 클래스를 비활성화할 수 있습니다(기본 스토리지 클래스 관리 참조). GCE 영구 디스크를 사용하는 영구 스토리지에 설명된 대로 GCP PD 스토리지 클래스를 생성하는 옵션도 있습니다.

GCP PD 드라이버: 이 드라이버를 사용하면 GCP PD PV를 생성 및 마운트할 수 있습니다.

GCP PD CSI 드라이버는 베어 메탈 및 N4 머신 시리즈의 C3 인스턴스 유형을 지원합니다. C3 인스턴스 유형 및 N4 시스템 시리즈는 hyperdisk-balanced 디스크를 지원합니다.

OpenShift Container Platform은 동등한 CSI 드라이버로 GCE 영구 디스크 in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 제공합니다. 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

#### 6.14.2.1. C3 및 N4 인스턴스 유형 제한 사항

베어 메탈 및 N4 머신 시리즈의 C3 인스턴스 유형에 대한 GCP PD CSI 드라이버 지원에는 다음과 같은 제한 사항이 있습니다.

hyperdisk-balanced 디스크를 생성할 때 볼륨 크기를 4Gi 이상으로 설정해야 합니다. OpenShift Container Platform은 최소 크기까지 반올림하지 않으므로 올바른 크기를 직접 지정해야 합니다.

스토리지 풀을 사용할 때는 볼륨 복제가 지원되지 않습니다.

복제 또는 크기 조정을 위해 원래 볼륨 크기는 6Gi 이상이어야 합니다.

기본 스토리지 클래스는 standard-csi입니다.

중요

스토리지 클래스를 수동으로 생성해야 합니다.

스토리지 클래스 생성에 대한 자세한 내용은 hyperdisk-balanced 디스크 설정 섹션의 2단계를 참조하십시오.

다양한 스토리지 유형을 사용하는 혼합 VM(가상 머신)이 있는 클러스터는 지원되지 않습니다. 이는 대부분의 기존 VM에서 하이퍼 디스크 분산 디스크를 사용할 수 없기 때문입니다. 마찬가지로 일반 영구 디스크는 N4/C3 VM에서 사용할 수 없습니다.

c3-standard-2, c3-standard-4, n4-standard-2, n4-standard-4 노드가 있는 GCP 클러스터는 연결할 수 있는 최대 디스크 번호(JIRA 링크)를 잘못 초과할 수 있습니다.

추가 제한 사항.

#### 6.14.2.2. hyperdisk-balanced 디스크용 스토리지 풀 개요

대규모 스토리지를 위해 Compute Engine과 함께 Hyperdisk 스토리지 풀을 사용할 수 있습니다. 하이퍼 디스크 스토리지 풀은 구매한 용량, 처리량 및 IOPS 컬렉션으로, 필요에 따라 애플리케이션을 프로비저닝할 수 있습니다. 하이퍼 디스크 스토리지 풀을 사용하여 풀에서 디스크를 생성 및 관리하고 여러 워크로드의 디스크를 사용할 수 있습니다. 디스크를 집계하여 관리하면 예상 용량 및 성능 증가를 달성하면서 비용을 절감할 수 있습니다. 하이퍼 디스크 스토리지 풀에서 필요한 스토리지만 사용하면 예측 용량의 복잡성을 줄이고 수백 개의 디스크를 관리에서 단일 스토리지 풀 관리로 이동하여 관리를 줄일 수 있습니다.

스토리지 풀을 설정하려면 hyperdisk-balanced 디스크 설정을 참조하십시오.

#### 6.14.2.3. hyperdisk-balanced 디스크 설정

사전 요구 사항

관리 권한이 있는 클러스터에 액세스

프로세스

hyperdisk-balanced 디스크를 설정하려면 다음 단계를 완료합니다.

하이퍼 디스크 분산 디스크를 사용하여 프로비저닝된 연결된 디스크를 사용하여 GCP 클러스터를 생성합니다.

설치 중에 hyperdisk-balanced 디스크를 지정하는 스토리지 클래스를 생성합니다.

사용자 지정 섹션을 사용하여 GCP에 클러스터 설치 섹션의 절차를 따르십시오.

install-config.yaml 파일의 경우 다음 예제 파일을 사용합니다.

```yaml
apiVersion: v1
metadata:
  name: ci-op-9976b7t2-8aa6b

sshKey: |
  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
baseDomain: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
platform:
  gcp:
    projectID: XXXXXXXXXXXXXXXXXXXXXX
    region: us-central1
controlPlane:
  architecture: amd64
  name: master
  platform:
    gcp:
      type: n4-standard-4
      osDisk:
        diskType: hyperdisk-balanced
        diskSizeGB: 200
  replicas: 3
compute:
- architecture: amd64
  name: worker
  replicas: 3
  platform:
    gcp:
      type: n4-standard-4
      osDisk:
        diskType: hyperdisk-balanced
```

1. 3

노드 유형을 n4-standard-4로 지정합니다.

2. 4

노드의 root 디스크가 hyperdisk-balanced 디스크 유형으로 지원됩니다. 클러스터의 모든 노드는 hyperdisks-balanced 또는 pd-*인 동일한 디스크 유형을 사용해야 합니다.

참고

클러스터의 모든 노드는 hyperdisk-balanced 볼륨을 지원해야 합니다. 혼합 노드가 있는 클러스터는 지원되지 않습니다(예: hyperdisk-balanced 디스크를 사용하는 N2 및 N3).

Cloud Credential Operator 유틸리티 매니페스트 섹션을 통합한 3단계 후 다음 매니페스트를 설치 프로그램에서 생성한 매니페스트 디렉터리에 복사합니다.

cluster_csi_driver.yaml - 기본 스토리지 클래스 생성 옵트아웃을 지정합니다.

StorageClass.yaml - 하이퍼 디스크별 스토리지 클래스를 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: "ClusterCSIDriver"
metadata:
  name: "pd.csi.storage.gke.io"
spec:
  logLevel: Normal
  managementState: Managed
  operatorLogLevel: Normal
  storageClassState: Unmanaged
```

1. 기본 OpenShift Container Platform 스토리지 클래스 생성 비활성화를 지정합니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: hyperdisk-sc
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: pd.csi.storage.gke.io
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
parameters:
  type: hyperdisk-balanced
  replication-type: none
  provisioned-throughput-on-create: "140Mi"
  provisioned-iops-on-create: "3000"
  storage-pools: projects/my-project/zones/us-east4-c/storagePools/pool-us-east4-c
allowedTopologies:
- matchLabelExpressions:
  - key: topology.kubernetes.io/zone
    values:
    - us-east4-c
...
```

1. 스토리지 클래스의 이름을 지정합니다. 이 예에서는 `hyperdisk-sc` 입니다.

2. `PD.csi.storage.gke.io` 는 GCP CSI 프로비저너를 지정합니다.

3. hyperdisk-balanced 디스크를 사용하도록 지정합니다.

4. "Mi" 한정자를 사용하여 throughput 값을 MiBps로 지정합니다. 예를 들어 필요한 처리량이 250MiBps인 경우 "250Mi"를 지정합니다. 값을 지정하지 않으면 용량은 디스크 유형 기본값을 기반으로 합니다.

5. 한정자 없이 IOPS 값을 지정합니다. 예를 들어 Cryostat IOPS가 필요한 경우 "7000"을 지정합니다. 값을 지정하지 않으면 용량은 디스크 유형 기본값을 기반으로 합니다.

6. 스토리지 풀을 사용하는 경우 project/PROJECT_ID/zones/ZONE/storagePools/STORAGE_POOL_NAME 형식으로 사용할 특정 스토리지 풀 목록을 지정합니다.

7. 스토리지 풀을 사용하는 경우 프로비저닝된 볼륨의 토폴로지를 스토리지 풀이 존재하는 위치로 제한하도록 `allowedTopologies` 를 설정합니다. 이 예에서 `us-east4-c`.

다음 예제 YAML 파일을 사용하여 하이퍼 디스크별 스토리지 클래스를 사용하는 PVC(영구 볼륨 클레임)를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  storageClassName: hyperdisk-sc
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 2048Gi
```

1. PVC는 스토리지 풀별 스토리지 클래스를 참조합니다. 예에서는 `hyperdisk-sc` 입니다.

2. hyperdisk-balanced 볼륨의 대상 스토리지 용량입니다. 예에서는 `2048Gi` 입니다.

방금 생성한 PVC를 사용하는 배포를 생성합니다. 배포를 사용하면 Pod를 재시작하고 일정을 변경한 후에도 애플리케이션이 영구 스토리지에 액세스할 수 있도록 합니다.

배포를 생성하기 전에 지정된 머신 시리즈가 있는 노드 풀이 실행 중인지 확인합니다. 그러지 않으면 Pod를 예약하지 못합니다.

다음 예제 YAML 파일을 사용하여 배포를 생성합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      nodeSelector:
        cloud.google.com/machine-family: n4
      containers:
      - name: postgres
        image: postgres:14-alpine
        args: [ "sleep", "3600" ]
        volumeMounts:
        - name: sdk-volume
          mountPath: /usr/share/data/
      volumes:
      - name: sdk-volume
        persistentVolumeClaim:
          claimName: my-pvc
```

1. 머신 제품군을 지정합니다. 이 예에서 `n4` 입니다.

2. 이전 단계에서 생성한 PVC의 이름을 지정합니다. 이 예에서는 `my-pfc` 입니다.

다음 명령을 실행하여 배포가 성공적으로 생성되었는지 확인합니다.

```shell-session
$ oc get deployment
```

```shell-session
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
postgres   0/1     1            0           42s
```

하이퍼 디스크 인스턴스가 프로비저닝을 완료하고 READY 상태를 표시하는 데 몇 분이 걸릴 수 있습니다.

다음 명령을 실행하여 PVC `my-pvc` 가 PV(영구 볼륨)에 성공적으로 바인딩되었는지 확인합니다.

```shell-session
$ oc get pvc my-pvc
```

```shell-session
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS       VOLUMEATTRIBUTESCLASS  AGE
my-pvc        Bound    pvc-1ff52479-4c81-4481-aa1d-b21c8f8860c6   2Ti        RWO            hyperdisk-sc       <unset>                2m24s
```

hyperdisk-balanced 디스크의 예상 구성을 확인합니다.

```shell-session
$ gcloud compute disks list
```

```shell-session
NAME                                        LOCATION        LOCATION_SCOPE  SIZE_GB  TYPE                STATUS
instance-20240914-173145-boot               us-central1-a   zone            150      pd-standard         READY
instance-20240914-173145-data-workspace     us-central1-a   zone            100      pd-balanced         READY
c4a-rhel-vm                                 us-central1-a   zone            50       hyperdisk-balanced  READY
```

1. Hyperdisk-balanced 디스크.

스토리지 풀을 사용하는 경우 다음 명령을 실행하여 스토리지 클래스 및 PVC에 지정된 대로 볼륨이 프로비저닝되었는지 확인합니다.

```shell-session
$ gcloud compute storage-pools list-disks pool-us-east4-c --zone=us-east4-c
```

```shell-session
NAME                                      STATUS  PROVISIONED_IOPS  PROVISIONED_THROUGHPUT  SIZE_GB
pvc-1ff52479-4c81-4481-aa1d-b21c8f8860c6  READY   3000              140                     2048
```

#### 6.14.2.4. 추가 리소스

사용자 지정 설정의 GCP에 클러스터 설치

#### 6.14.3. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.14.4. GCP PD CSI 드라이버 스토리지 클래스 매개변수

GCP(Google Cloud Platform) PD(영구 디스크) CSI(Container Storage Interface) 드라이버는 CSI `외부 프로비저너` 사이드카를 컨트롤러로 사용합니다. 이 컨테이너는 CSI 드라이버와 함께 배포된 별도의 Helper 컨테이너입니다. 사이드카는 `CreateVolume` 작업을 트리거하여 PV(영구 볼륨)를 관리합니다.

GCP PD CSI 드라이버는 `csi.storage.k8s.io/fstype` 매개변수 키를 사용하여 동적 프로비저닝을 지원합니다. 다음 표에는 OpenShift Container Platform에서 지원하는 모든 GCP PD CSI 스토리지 클래스 매개변수를 설명합니다.

| 매개변수 | 값 | 기본 | 설명 |
| --- | --- | --- | --- |
| `type` | `PD-ssd` , `pd-standard` 또는 `pd-balanced` | `pd-standard` | 표준 PV 또는 솔리드 스테이트 드라이브 PV 중 하나를 선택할 수 있습니다. 드라이버는 값을 확인하지 않으므로 가능한 모든 값이 허용됩니다. |
| `replication-type` | `none` 또는 `regional-pd` | `none` | 존 또는 지역 PV 중 하나를 선택할 수 있습니다. |
| `disk-encryption-kms-key` | 새 디스크를 암호화하는 데 사용할 키가 정규화된 리소스 식별자입니다. | 빈 문자열 | CMEK(고객 관리 암호화 키)를 사용하여 새 디스크를 암호화합니다. |

#### 6.14.5. 사용자 정의 암호화 영구 볼륨 생성

`PersistentVolumeClaim` 오브젝트를 생성할 때 OpenShift Container Platform은 새 PV(영구 볼륨)를 프로비저닝하고 `PersistentVolume` 오브젝트를 생성합니다. 새로 생성된 PV를 암호화하여 클러스터에서 PV를 보호하기 위해 GCP(Google Cloud Platform)에 사용자 지정 암호화 키를 추가할 수 있습니다.

암호화를 위해 새로 연결된 PV는 신규 또는 기존 Google Cloud KMS(키 관리 서비스) 키를 사용하여 클러스터에서 CMEK(고객 관리 암호화 키)를 사용합니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인되어 있습니다.

Cloud KMS 키 링 및 키 버전이 생성되어 있습니다.

CMEK 및 Cloud KMS 리소스에 대한 자세한 내용은 CMEK(고객 관리 암호화 키) 사용 을 참조하십시오.

절차

사용자 정의 PV를 생성하려면 다음 단계를 완료합니다.

Cloud KMS 키를 사용하여 스토리지 클래스를 생성합니다. 다음 예시에서는 암호화된 볼륨의 동적 프로비저닝을 활성화합니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-gce-pd-cmek
provisioner: pd.csi.storage.gke.io
volumeBindingMode: "WaitForFirstConsumer"
allowVolumeExpansion: true
parameters:
  type: pd-standard
  disk-encryption-kms-key: projects/<key-project-id>/locations/<location>/keyRings/<key-ring>/cryptoKeys/<key>
```

1. 이 필드는 새 디스크를 암호화하는 데 사용할 키의 리소스 식별자여야 합니다. 값은 대소문자를 구분합니다. 키 ID 값을 제공하는 방법에 대한 자세한 내용은 리소스의 ID 검색 및 Cloud KMS 리소스 ID 가져오기 를 참조하십시오.

참고

`disk-encryption-✓s-key` 매개변수를 기존 스토리지 클래스에 추가할 수 없습니다. 그러나 스토리지 클래스를 삭제하고 동일한 이름과 다른 매개변수 세트로 다시 생성할 수 있습니다. 이렇게 하는 경우 기존 클래스의 프로비저너가 `pd.csi.storage.gke.io` 여야 합니다.

아래 명령을 사용하여 OpenShift Container Platform 클러스터에 스토리지 클래스를 배포합니다.

```shell
oc
```

```shell-session
$ oc describe storageclass csi-gce-pd-cmek
```

```shell-session
Name:                  csi-gce-pd-cmek
IsDefaultClass:        No
Annotations:           None
Provisioner:           pd.csi.storage.gke.io
Parameters:            disk-encryption-kms-key=projects/key-project-id/locations/location/keyRings/ring-name/cryptoKeys/key-name,type=pd-standard
AllowVolumeExpansion:  true
MountOptions:          none
ReclaimPolicy:         Delete
VolumeBindingMode:     WaitForFirstConsumer
Events:                none
```

이전 단계에서 생성한 스토리지 클래스 오브젝트의 이름과 일치하는 `pvc.yaml` 파일을 생성합니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: podpvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: csi-gce-pd-cmek
  resources:
    requests:
      storage: 6Gi
```

참고

새 스토리지 클래스를 기본값으로 표시한 경우 `storageClassName` 필드를 생략할 수 있습니다.

클러스터에 PVC를 적용합니다.

```shell-session
$ oc apply -f pvc.yaml
```

PVC 상태를 가져온 후 새로 프로비저닝된 PV에 바인딩되었는지 확인합니다.

```shell-session
$ oc get pvc
```

```shell-session
NAME      STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS     AGE
podpvc    Bound     pvc-e36abf50-84f3-11e8-8538-42010a800002   10Gi       RWO            csi-gce-pd-cmek  9s
```

참고

스토리지 클래스에 `WaitForFirstConsumer` 로 설정된 `volumeBindingMode` 필드가 있는 경우 이를 확인하기 전에 PVC를 사용하도록 Pod를 생성해야 합니다.

이제 CMEK가 지원하는 PV를 OpenShift Container Platform 클러스터와 함께 사용할 준비가 되었습니다.

#### 6.14.6. 사용자 관리 암호화

사용자 관리 암호화 기능을 사용하면 OpenShift Container Platform 노드 루트 볼륨을 암호화하는 설치 중에 키를 제공하고 모든 관리 스토리지 클래스가 이러한 키를 사용하여 프로비저닝된 스토리지 볼륨을 암호화할 수 있습니다. install-config YAML 파일의 `platform.<cloud_type>.defaultMachinePlatform` 필드에 사용자 지정 키를 지정해야 합니다.

이 기능은 다음 스토리지 유형을 지원합니다.

AWS(Amazon Web Services) EBS(Elastic Block Storage)

Microsoft Azure Disk 스토리지

GCP(Google Cloud Platform) PD(영구 디스크) 스토리지

IBM Virtual Private Cloud (VPC) 블록 스토리지

GCP PD의 사용자 관리 암호화로 설치하는 방법에 대한 자세한 내용은 설치 구성 매개변수를 참조하십시오.

#### 6.14.7. 추가 리소스

GCE 영구 디스크를 사용하는 스토리지

CSI 볼륨 구성

#### 6.15.1. 개요

OpenShift Container Platform은 GCP(Google Compute Platform) 파일 저장소 스토리지용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

Google Cloud Filestore 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하려면 `openshift-cluster-csi-drivers` 네임스페이스에 Google Cloud Filestore CSI 드라이버와 Google Cloud Filestore CSI 드라이버를 설치합니다.

Google Cloud Filestore CSI Driver Operator 는 기본적으로 스토리지 클래스를 제공하지 않지만 필요한 경우 스토리지 클래스를 생성할 수 있습니다. Google Cloud Filestore CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있으므로 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없어 동적 볼륨 프로비저닝을 지원합니다.

Google Cloud Filestore CSI 드라이버 를 사용하면 Google Cloud Filestore PV를 생성하고 마운트할 수 있습니다.

OpenShift Container Platform Google Cloud Filestore는 워크로드 ID를 지원합니다. 이를 통해 사용자는 서비스 계정 키 대신 페더레이션 ID를 사용하여 Google Cloud 리소스에 액세스할 수 있습니다. GCP Workload Identity는 설치 중에 전역적으로 활성화되어야 하며 Google Cloud Filestore CSI Driver Operator에 대해 구성해야 합니다.

#### 6.15.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.15.3.1. Workload Identity를 사용하여 Google Cloud Filestore CSI Driver Operator 설치 준비

Google Compute Platform Filestore와 함께 GCP 워크로드 ID를 사용하려면 Google Cloud Filestore CSI(Container Storage Interface) Driver Operator를 설치하는 동안 사용할 특정 매개변수를 가져와야 합니다.

사전 요구 사항

cluster-admin 역할을 가진 사용자로 클러스터에 액세스합니다.

프로세스

Workload Identity를 사용하여 Google Cloud Filestore CSI Driver Operator 설치를 준비하려면 다음을 수행합니다.

프로젝트 번호를 가져옵니다.

다음 명령을 실행하여 프로젝트 ID를 가져옵니다.

```shell-session
$ export PROJECT_ID=$(oc get infrastructure/cluster -o jsonpath='{.status.platformStatus.gcp.projectID}')
```

다음 명령을 실행하여 프로젝트 ID를 사용하여 프로젝트 번호를 가져옵니다.

```shell-session
$ gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
```

ID 풀 ID와 공급자 ID를 찾습니다.

클러스터 설치 중에 이러한 리소스의 이름은 `--name 매개변수를` 사용하여 Cloud Credential Operator 유틸리티(`ccoctl`)에 제공됩니다. "Cloud Credential Operator 유틸리티를 사용하여 Google Cloud 리소스 생성"을 참조하십시오.

Google Cloud Filestore Operator의 Workload Identity 리소스를 생성합니다.

다음 예제 파일을 사용하여 `CredentialsRequest` 파일을 생성합니다.

```yaml
apiVersion: cloudcredential.openshift.io/v1
kind: CredentialsRequest
metadata:
  name: openshift-gcp-filestore-csi-driver-operator
  namespace: openshift-cloud-credential-operator
  annotations:
    include.release.openshift.io/self-managed-high-availability: "true"
    include.release.openshift.io/single-node-developer: "true"
spec:
  serviceAccountNames:
  - gcp-filestore-csi-driver-operator
  - gcp-filestore-csi-driver-controller-sa
  secretRef:
    name: gcp-filestore-cloud-credentials
    namespace: openshift-cluster-csi-drivers
  providerSpec:
    apiVersion: cloudcredential.openshift.io/v1
    kind: GCPProviderSpec
    predefinedRoles:
    - roles/file.editor
    - roles/resourcemanager.tagUser
    skipServiceCheck: true
```

`CredentialsRequest` 파일을 사용하여 다음 명령을 실행하여 Google Cloud 서비스 계정을 생성합니다.

```shell-session
$ ./ccoctl gcp create-service-accounts --name=<filestore-service-account> \
  --workload-identity-pool=<workload-identity-pool> \
  --workload-identity-provider=<workload-identity-provider> \
  --project=<project-id> \
  --credentials-requests-dir=/tmp/credreq
```

1. <filestore-service-account>는 사용자 선택 이름입니다.

2. <workload-identity-pool>은 위의 2단계에서 제공합니다.

3. <workload-identity-provider>는 위의 2단계에서 제공합니다.

4. <project-id>는 위의 1.a 단계에서 제공됩니다.

5. `CredentialsRequest` 파일이 있는 디렉터리의 이름입니다.

```shell-session
2025/02/10 17:47:39 Credentials loaded from gcloud CLI defaults
2025/02/10 17:47:42 IAM service account filestore-service-account-openshift-gcp-filestore-csi-driver-operator created
2025/02/10 17:47:44 Unable to add predefined roles to IAM service account, retrying...
2025/02/10 17:47:59 Updated policy bindings for IAM service account filestore-service-account-openshift-gcp-filestore-csi-driver-operator
2025/02/10 17:47:59 Saved credentials configuration to: /tmp/install-dir/
openshift-cluster-csi-drivers-gcp-filestore-cloud-credentials-credentials.yaml
```

1. 현재 디렉터리입니다.

다음 명령을 실행하여 새로 생성된 서비스 계정의 서비스 계정 이메일을 찾습니다.

```shell-session
$ cat /tmp/install-dir/manifests/openshift-cluster-csi-drivers-gcp-filestore-cloud-credentials-credentials.yaml | yq '.data["service_account.json"]' | base64 -d | jq '.service_account_impersonation_url'
```

```shell-session
https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/filestore-se-openshift-g-ch8cm@openshift-gce-devel.iam.gserviceaccount.com:generateAccessToken
```

이 예제 출력에서 서비스 계정 이메일은 `filestore-se-openshift-g-ch8cm@openshift-gce-devel.iam.gserviceaccount.com` 입니다.

결과

이제 Google Cloud Filestore CSI Driver Operator를 설치해야 하는 매개변수가 다음과 같습니다.

프로젝트 번호 - 1.b 단계

Pool ID - 단계 2에서

공급자 ID - 2단계에서

서비스 계정 이메일 - 단계 3.c

추가 리소스

Cloud Credential Operator 유틸리티를 사용하여 Google Cloud 리소스 생성

#### 6.15.3.2. Google Cloud Filestore CSI Driver Operator 설치

Google Compute Platform (Google Cloud) Filestore CSI(Container Storage Interface) Driver Operator는 기본적으로 OpenShift Container Platform에 설치되지 않습니다. 다음 절차에 따라 클러스터에 Google Cloud Filestore CSI Driver Operator를 설치합니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

GCP 워크로드 ID를 사용하는 경우 특정 GCP 워크로드 ID 매개변수가 필요합니다. Workload Identity를 사용하여 Google Cloud Filestore CSI Driver Operator 설치 준비 섹션을 참조하십시오.

프로세스

웹 콘솔에서 Google Cloud Filestore CSI Driver Operator를 설치하려면 다음을 수행합니다.

웹 콘솔에 로그인합니다.

다음 명령을 실행하여 GCE 프로젝트에서 Filestore API를 활성화합니다.

```plaintext
$ gcloud services enable file.googleapis.com  --project <my_gce_project>
```

1. `<my_gce_project>` 를 Google Cloud 프로젝트로 바꿉니다.

Google Cloud 웹 콘솔을 사용하여 이 작업을 수행할 수도 있습니다.

Google Cloud Filestore CSI Operator를 설치합니다.

Ecosystem → Software Catalog 를 클릭합니다.

Google Cloud Filestore CSI Operator를 필터 상자에 입력합니다.

Google Cloud Filestore CSI Driver Operator 버튼을 클릭합니다.

Google Cloud Filestore CSI Driver Operator 페이지에서 설치를 클릭합니다.

Operator 설치 페이지에서 다음을 확인합니다.

클러스터의 모든 네임스페이스(기본값) 가 선택됩니다.

설치된 네임스페이스 는 openshift-cluster-csi-drivers 로 설정됩니다.

GCP 워크로드 ID를 사용하는 경우 워크로드 ID를 사용하여 Google Cloud Filestore CSI Driver Operator 설치 준비 섹션 섹션의 다음 필드에 대한 값을 입력합니다.

Google Cloud 프로젝트 번호

Google 클라우드 풀 ID

Google 클라우드 공급자 ID

Google Cloud 서비스 계정 이메일

설치 를 클릭합니다.

설치가 완료되면 Google Cloud Filestore CSI Operator가 웹 콘솔의 설치된 Operator 섹션에 나열됩니다.

Google Cloud Filestore CSI 드라이버를 설치합니다.

관리 → CustomResourceDefinitions → ClusterCSIDriver 를 클릭합니다.

Instances 탭에서 Create ClusterCSIDriver 를 클릭합니다.

다음 YAML 파일을 사용합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: ClusterCSIDriver
metadata:
    name: filestore.csi.storage.gke.io
spec:
  managementState: Managed
```

생성 을 클릭합니다.

다음 조건이 "true" 상태로 변경될 때까지 기다립니다.

GCPFilestoreDriverCredentialsRequestControllerAvailable

GCPFilestoreDriverNodeServiceControllerAvailable

GCPFilestoreDriverControllerServiceControllerAvailable

추가 리소스

Google 클라우드에서 API 활성화.

Google Cloud 웹 콘솔을 사용하여 API 활성화.

#### 6.15.4. GCP Filestore 스토리지용 스토리지 클래스 생성

Operator를 설치한 후 GCP(Google Compute Platform) Filestore 볼륨의 동적 프로비저닝을 위한 스토리지 클래스를 생성해야 합니다.

사전 요구 사항

실행 중인 OpenShift Container Platform 클러스터에 로그인되어 있습니다.

프로세스

스토리지 클래스를 생성하려면 다음을 수행합니다.

다음 예제 YAML 파일을 사용하여 스토리지 클래스를 생성합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: filestore-csi
provisioner: filestore.csi.storage.gke.io
parameters:
  connect-mode: DIRECT_PEERING
  network: network-name
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

1. 공유 VPC의 경우 `PRIVATE_SERVICE_ACCESS` 로 설정된 `connect-mode` 매개변수를 사용합니다. 비공유 VPC의 경우 값은 기본 설정인 `DIRECT_PEERING` 입니다.

2. Filestore 인스턴스를 생성해야 하는 GCP 가상 프라이빗 클라우드(VPC) 네트워크의 이름을 지정합니다.

Filestore 인스턴스를 생성해야 하는 VPC 네트워크의 이름을 지정합니다.

Filestore 인스턴스를 생성해야 하는 VPC 네트워크를 지정하는 것이 좋습니다. VPC 네트워크가 지정되지 않은 경우 CSI(Container Storage Interface) 드라이버는 프로젝트의 기본 VPC 네트워크에 인스턴스를 생성하려고 합니다.

IPI 설치 시 VPC 네트워크 이름은 일반적으로 접미사 "-network"가 있는 클러스터 이름입니다. 그러나 UPI 설치 시 VPC 네트워크 이름은 사용자가 선택한 모든 값이 될 수 있습니다.

공유 VPC(`connect-mode` = `PRIVATE_SERVICE_ACCESS`)의 경우 네트워크가 전체 VPC 이름이어야 합니다. 예: `projects/shared-vpc-name/global/networks/gcp-filestore-network`.

다음 명령을 사용하여 `MachineSets` 오브젝트를 검사하여 VPC 네트워크 이름을 확인할 수 있습니다.

```plaintext
$ oc -n openshift-machine-api get machinesets -o yaml | grep "network:"
            - network: gcp-filestore-network
(...)
```

이 예에서 이 클러스터의 VPC 네트워크 이름은 "gcp-filestore-network"입니다.

#### 6.15.5. NFS 내보내기 옵션

기본적으로 Filestore 인스턴스는 동일한 Google Cloud 프로젝트 및 VPC(가상 프라이빗 클라우드) 네트워크를 공유하는 모든 클라이언트에 루트 수준 읽기/쓰기 액세스 권한을 부여합니다. NFS(Network File System) 내보내기 옵션은 Filestore 인스턴스의 특정 IP 범위 및 특정 사용자/그룹 ID에 대한 이 액세스를 제한할 수 있습니다. 스토리지 클래스를 생성할 때 `nfs-export-options-on-create` 매개변수를 사용하여 이러한 옵션을 설정할 수 있습니다.

사전 요구 사항

cluster-admin 역할을 가진 사용자로 클러스터에 액세스합니다.

Google Cloud Filestore CSI Driver Operator 및 Google Cloud Filestore CSI 드라이버가 설치되어 있어야 합니다.

프로세스

다음 샘플 YAML 파일과 유사한 파일을 사용하여 스토리지 클래스를 생성합니다.

참고

스토리지 클래스 생성에 대한 자세한 내용은 GCP Filestore Operator용 스토리지 클래스 생성 섹션을 참조하십시오.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
 name: SC-name
provisioner: filestore.csi.storage.gke.io
parameters:
 connect-mode: DIRECT_PEERING
 network: project-network
 nfs-export-options-on-create: '[
   {
     "accessMode": "READ_WRITE",
     "squashMode": "NO_ROOT_SQUASH",
     "anonUid": 65534
     "anonGid": 65534
     "ipRanges": [
       "10.0.0.0/16"
     ]
   }]'
allowVolumeExpansion: true
```

1. NFS 내보내기 옵션 매개변수

2. 액세스 모드: 내보낸 디렉터리에 대한 읽기 요청만 허용하는 `READ_ONLY` 또는 읽기 및 쓰기 요청을 모두 허용하는 `READ_WRITE`. 기본값은 `READ_WRITE` 입니다.

3. squash 모드: 내보낸 디렉터리에 대한 루트 액세스를 허용하는 `NO_ROOT_SQUASH`; 또는 루트 액세스를 허용하지 않는 ROOT_SQUASH입니다. 기본값은 `NO_ROOT_SQUASH` 입니다.

4. AnonUid: 기본값이 65534인 익명 사용자 ID를 나타내는 정수입니다. `AnonUid` 는 `ROOT_SQUASH` 로 설정된 `squashMode` 만 설정할 수 있습니다. 그렇지 않으면 오류가 발생합니다.

5. AnonGid: 기본값이 65534인 익명 그룹 ID를 나타내는 정수입니다. `AnonGid` 는 `ROOT_SQUASH` 로 설정된 `squashMode` 에서만 설정할 수 있습니다. 그렇지 않으면 오류가 발생합니다.

6. IP 범위: {octet1}.{octet2}.{octet3}.{octet4} 형식의 IPv4 주소 목록 또는 {octet1}.{octet2}.{octet3}.{octet3}/{octet4}/{mask size} 형식의 CIDR 범위입니다. 그렇지 않으면 내부 및 NfsExportOptions 모두에서 겹치는 IP 범위가 허용되지 않습니다. 제한은 모든 NFS 내보내기 옵션 중 각 `FileShareConfig` 의 64 IP 범위 또는 주소입니다.

#### 6.15.6. 클러스터 및 GCP 파일 저장소 삭제

일반적으로 클러스터를 삭제하면 OpenShift Container Platform 설치 프로그램이 해당 클러스터에 속하는 모든 클라우드 리소스를 삭제합니다. 그러나 GCP(Google Compute Platform) Filestore 리소스의 특수 특성으로 인해 자동화된 정리 프로세스가 드문 경우 모두 제거되지 않을 수 있습니다.

따라서 제거 프로세스에서 모든 클러스터 소유 Filestore 리소스가 삭제되었는지 확인하는 것이 좋습니다.

프로세스

모든 GCP Filestore PVC가 삭제되었는지 확인하려면 다음을 수행하십시오.

GUI 또는 CLI를 사용하여 Google Cloud 계정에 액세스합니다.

`kubernetes-io-cluster-${CLUSTER_ID}=owned` 라벨을 사용하여 모든 리소스를 검색합니다.

클러스터 ID는 삭제된 클러스터에 고유하므로 해당 클러스터 ID가 있는 나머지 리소스가 없어야 합니다.

예기치 않은 경우 나머지 리소스가 있으며 삭제합니다.

#### 6.15.7. 추가 리소스

CSI 볼륨 구성

Google Cloud Workload Identity를 사용하는 OLM 관리 Operator의 CCO 기반 워크플로 입니다.

#### 6.16.1. 개요

OpenShift Container Platform은 IBM® VPC(Virtual Private Cloud) 블록 스토리지용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

IBM Cloud® VPC Block 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 IBM Cloud® VPC Block CSI Driver Operator 및 IBM Cloud® VPC Block CSI 드라이버를 설치합니다.

IBM Cloud® VPC Block CSI Driver Operator 는 `ibmc-vpc-block-10iops-tier` (default), `ibmc-vpc-block-5iops-tier`, ibmc-vpc-block-custom, 영구 볼륨 클레임(PVC)을 생성하는 데 사용할 수 있는 다른 계층에 대해 `ibmc-vpc-block-custom` 이라는 세 가지 스토리지 클래스를 제공합니다. IBM Cloud® VPC Block CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있으므로 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없어 동적 볼륨 프로비저닝을 지원합니다. 필요한 경우 이 기본 스토리지 클래스를 비활성화할 수 있습니다(기본 스토리지 클래스 관리 참조).

IBM Cloud® VPC Block CSI 드라이버 를 사용하면 IBM Cloud® VPC Block PV를 생성하고 마운트할 수 있습니다.

#### 6.16.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.16.3. 사용자 관리 암호화

사용자 관리 암호화 기능을 사용하면 OpenShift Container Platform 노드 루트 볼륨을 암호화하는 설치 중에 키를 제공하고 모든 관리 스토리지 클래스가 이러한 키를 사용하여 프로비저닝된 스토리지 볼륨을 암호화할 수 있습니다. install-config YAML 파일의 `platform.<cloud_type>.defaultMachinePlatform` 필드에 사용자 지정 키를 지정해야 합니다.

이 기능은 다음 스토리지 유형을 지원합니다.

AWS(Amazon Web Services) EBS(Elastic Block Storage)

Microsoft Azure Disk 스토리지

GCP(Google Cloud Platform) PD(영구 디스크) 스토리지

IBM Virtual Private Cloud (VPC) 블록 스토리지

IBM Cloud용 사용자 관리 암호화로 설치하는 방법에 대한 자세한 내용은 IBM Cloud의 사용자 관리 암호화 및 IBM Cloud

에 설치 준비를 참조하십시오.

추가 리소스

CSI 볼륨 구성

#### 6.17.1. 소개

IBM Power® Virtual Server Block CSI 드라이버는 IBM Power® Virtual Server Block CSI Driver Operator를 통해 설치되고 Operator는 `library-go` 를 기반으로 합니다. OpenShift Container Platform `library-go` 프레임워크는 사용자가 OpenShift Operator를 쉽게 빌드할 수 있는 함수 컬렉션입니다. CSI Driver Operator의 대부분의 기능은 이미 사용 가능합니다. IBM Power® Virtual Server Block CSI Driver Operator는 Cluster Storage Operator에 의해 설치됩니다. 플랫폼 유형이 Power Virtual Servers인 경우 Cluster Storage Operator는 IBM Power® Virtual Server Block CSI Driver Operator를 설치합니다.

#### 6.17.2. 개요

OpenShift Container Platform은 IBM Power® Virtual Server Block Storage용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하면 CSI Operator 및 드라이버를 사용할 때 유용합니다.

IBM Power® Virtual Server Block 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 IBM Power® Virtual Server Block CSI Driver Operator 및 IBM Power® Virtual Server Block CSI 드라이버를 설치합니다.

IBM Power® Virtual Server Block CSI Driver Operator 는 PVC(영구 볼륨 클레임)를 생성하는 데 사용할 수 있는 다른 계층에 대해 `ibm-powervs-tier1` (기본값) 및 `ibm-powervs-tier3` 이라는 두 가지 스토리지 클래스를 제공합니다. IBM Power® Virtual Server Block CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있으므로 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없어 동적 볼륨 프로비저닝을 지원합니다.

IBM Power® Virtual Server Block CSI 드라이버 를 사용하면 IBM Power® Virtual Server Block PV를 생성하고 마운트할 수 있습니다.

#### 6.17.3. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

추가 리소스

CSI 볼륨 구성

#### 6.18.1. 개요

OpenShift Container Platform은 OpenStack Cinder 용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI(Container Storage Interface) Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

OpenStack Cinder 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 OpenStack Cinder CSI 드라이버와 OpenStack Cinder CSI 드라이버를 설치합니다.

OpenStack Cinder CSI Driver Operator는 PVC를 생성하는 데 사용할 수 있는 CSI 스토리지 클래스를 제공합니다. 필요한 경우 이 기본 스토리지 클래스를 비활성화할 수 있습니다(기본 스토리지 클래스 관리 참조).

OpenStack Cinder CSI 드라이버 를 사용하면 OpenStack Cinder PV를 생성 및 마운트할 수 있습니다.

참고

OpenShift Container Platform은 Cinder in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 동등한 CSI 드라이버로 제공합니다. 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

#### 6.18.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

중요

OpenShift Container Platform은 기본적으로 CSI 플러그인을 사용하여 Cinder 스토리지를 프로비저닝합니다.

#### 6.18.3. OpenStack Cinder CSI를 기본 스토리지 클래스로 설정

OpenStack Cinder CSI 드라이버는 `cinder.csi.openstack.org` 매개변수 키를 사용한 동적 프로비저닝을 지원합니다.

OpenShift Container Platform에서 OpenStack Cinder CSI 프로비저닝을 활성화하려면 기본 in-tree 스토리지 클래스를 `standard-csi` 로 덮어쓰는 것이 좋습니다. 다른 방법으로 PVC(영구 볼륨 클레임)를 생성하고 스토리지 클래스를 "standard-csi"로 지정할 수 있습니다.

OpenShift Container Platform에서 기본 스토리지 클래스는 in-tree Cinder 드라이버를 참조합니다. 그러나 CSI 자동 마이그레이션이 활성화된 경우 기본 스토리지 클래스를 사용하여 생성된 볼륨은 실제로 CSI 드라이버를 사용합니다.

프로세스

기본 in-tree 스토리지 클래스를 작성하여 `standard-csi` 스토리지 클래스를 적용하려면 다음 단계를 사용합니다.

스토리지 클래스를 나열합니다.

```shell-session
$ oc get storageclass
```

```shell-session
NAME                   PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard(default)      cinder.csi.openstack.org   Delete          WaitForFirstConsumer   true                   46h
standard-csi           kubernetes.io/cinder       Delete          WaitForFirstConsumer   true                   46h
```

기본 StorageClass에 대해 주석 `storageclass.kubernetes.io/is-default-class` 의 값을 `false` 로 변경합니다.

```shell-session
$ oc patch storageclass standard -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "false"}}}'
```

주석을 `storageclass.kubernetes.io/is-default-class=true` 로 추가하거나 수정하여 다른 스토리지 클래스를 기본값으로 설정합니다.

```shell-session
$ oc patch storageclass standard-csi -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'
```

PVC가 기본적으로 CSI 스토리지 클래스를 참조하는지 확인합니다.

```shell-session
$ oc get storageclass
```

```shell-session
NAME                   PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
standard               kubernetes.io/cinder       Delete          WaitForFirstConsumer   true                   46h
standard-csi(default)  cinder.csi.openstack.org   Delete          WaitForFirstConsumer   true                   46h
```

선택 사항: 스토리지 클래스를 지정하지 않고도 새 PVC를 정의할 수 있습니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cinder-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

특정 스토리지 클래스를 지정하지 않는 PVC는 기본 스토리지 클래스를 사용하여 자동으로 프로비저닝됩니다.

선택 사항: 새 파일을 구성한 후 클러스터에서 파일을 생성합니다.

```shell-session
$ oc create -f cinder-claim.yaml
```

추가 리소스

CSI 볼륨 구성

#### 6.19.1. 개요

OpenShift Container Platform은 OpenStack Manila 공유 파일 시스템 서비스의 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI(Container Storage Interface) Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

Manila 스토리지 자산에 마운트되는 CSI 프로비저닝 PV를 생성하기 위해 OpenShift Container Platform은 Manila 서비스가 활성화된 모든 OpenStack 클러스터에 Manila CSI Driver Operator 및 Manila CSI 드라이버를 설치합니다.

Manila CSI Driver Operator 는 사용 가능한 모든 Manila 공유 유형에 대해 PVC를 생성하는 데 필요한 스토리지 클래스를 생성합니다. Operator는 `openshift-cluster-csi-drivers` 네임스페이스에 설치됩니다.

Manila CSI 드라이버 를 사용하면 Manila PV를 생성 및 마운트할 수 있습니다. 드라이버는 `openshift-manila-csi-driver` 네임스페이스에 설치됩니다.

#### 6.19.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.19.3. Manila CSI Driver Operator 제한 사항

Manila CSI(Container Storage Interface) Driver Operator에 다음과 같은 제한 사항이 적용됩니다.

NFS만 지원됨

OpenStack Manila는 NFS, CIFS, CEPHFS와 같은 많은 네트워크 연결 스토리지 프로토콜을 지원하며 OpenStack 클라우드에서 선택적으로 활성화할 수 있습니다. OpenShift Container Platform의 Manila CSI Driver Operator는 NFS 프로토콜 사용만 지원합니다. 기본 OpenStack 클라우드에서 NFS를 사용할 수 없고 활성화된 경우 Manila CSI Driver Operator를 사용하여 OpenShift Container Platform용 스토리지를 프로비저닝할 수 없습니다.

백엔드가 CephFS-NFS인 경우 스냅샷은 지원되지 않습니다.

PV(영구 볼륨)의 스냅샷을 작성하고 볼륨을 스냅샷으로 되돌리려면 사용 중인 Manila 공유 유형이 이러한 기능을 지원하는지 확인해야 합니다. Red Hat OpenStack 관리자는 사용하려는 스토리지 클래스와 연결된 `share type extra-spec snapshot_support`)과 스냅샷에서 공유를 생성해야 합니다(`share type extra-spec create_share_from_snapshot_support`).

FSGroups는 지원되지 않습니다.

Manila CSI는 여러 리더 및 여러 작성자가 액세스할 수 있는 공유 파일 시스템을 제공하므로 FSGroups 사용을 지원하지 않습니다. ReadWriteOnce 액세스 모드를 사용하여 생성된 영구 볼륨에도 적용됩니다. 따라서 Manila CSI 드라이버에서 사용하기 위해 수동으로 생성하는 스토리지 클래스에 `fsType` 속성을 지정하지 않는 것이 중요합니다.

중요

Red Hat OpenStack Platform 16.x 및 17.x에서 NFS를 통해 CephFS의 공유 파일 시스템 서비스(Manila)는 Manila CSI를 통해 OpenShift Container Platform에 공유를 완전히 지원합니다. 그러나 이 솔루션은 대규모 확장을 위한 것은 아닙니다. Red Hat OpenStack Platform 용 CephFS NFS Manila-CSI 워크로드 권장 사항 에서 중요한 권장 사항을 검토하십시오.

#### 6.19.4. 동적으로 Manila CSI 볼륨 프로비저닝

OpenShift Container Platform은 사용 가능한 Manila 공유 유형마다 스토리지 클래스를 설치합니다.

생성된 YAML 파일은 Manila 및 해당 CSI(Container Storage Interface) 플러그인에서 완전히 분리됩니다. 애플리케이션 개발자는 RWX(ReadWriteMany) 스토리지를 동적으로 프로비저닝하고 YAML 매니페스트를 사용하여 스토리지를 안전하게 사용하는 애플리케이션에 Pod를 배포할 수 있습니다.

PVC 정의의 스토리지 클래스 참조를 제외하고 AWS, Google Cloud, Azure 및 기타 플랫폼에서 OpenShift Container Platform과 함께 사용하는 것과 동일한 Pod 및 PVC(영구 볼륨 클레임) 정의를 사용할 수 있습니다.

중요

기본적으로 볼륨에 할당된 액세스 규칙은 `0.0.0.0/0` 이며 모든 IPv4 클라이언트에서 액세스할 수 있습니다. 클라이언트 액세스를 제한하려면 특정 클라이언트 IP 주소 또는 서브넷을 사용하는 사용자 지정 스토리지 클래스를 생성합니다. 자세한 내용은 Manila 공유 액세스 규칙 사용자 지정을 참조하십시오.

참고

Manila 서비스는 선택 사항입니다. RHOSP(Red Hat OpenStack Platform)에서 서비스가 활성화되지 않으면 Manila CSI 드라이버가 설치되지 않고 Manila용 스토리지 클래스가 생성되지 않습니다.

사전 요구 사항

RHOSP는 적절한 Manila와 함께 배포되어 OpenShift Container Platform에서 볼륨을 동적으로 프로비저닝 및 마운트하는 데 사용할 수 있습니다.

절차(UI)

웹 콘솔을 사용하여 Manila CSI 볼륨을 동적으로 생성하려면 다음을 수행합니다.

OpenShift Container Platform 콘솔에서 스토리지 → 영구 볼륨 클레임 을 클릭합니다.

영구 볼륨 클레임 생성 개요에서 영구 볼륨 클레임 생성 을 클릭합니다.

결과 페이지에 필요한 옵션을 정의합니다.

적절한 스토리지 클래스를 선택합니다.

스토리지 클레임의 고유한 이름을 입력합니다.

생성 중인 PVC에 대한 읽기 및 쓰기 권한을 지정하려면 액세스 모드를 선택합니다.

중요

이 PVC를 수행하는 PV가 클러스터의 여러 노드의 여러 Pod에 마운트되도록 하려면 RWX를 사용합니다.

스토리지 클레임의 크기를 정의합니다.

생성 을 클릭하여 PVC를 생성하고 PV를 생성합니다.

프로세스(CLI)

CLI(명령줄 인터페이스)를 사용하여 Manila CSI 볼륨을 동적으로 생성하려면 다음을 수행합니다.

다음 YAML로 설명된 `PersistentVolumeClaim` 오브젝트를 사용하여 파일을 생성하고 저장합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-manila
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: csi-manila-gold
```

1. 이 PVC를 수행하는 PV가 클러스터의 여러 노드의 여러 Pod에 마운트되도록 하려면 RWX를 사용합니다.

2. 스토리지 백엔드를 프로비저닝하는 스토리지 클래스의 이름입니다. Manila 스토리지 클래스는 Operator에 의해 프로비저닝되며 `csi-manila-` 접두사가 적용됩니다.

다음 명령을 실행하여 이전 단계에서 저장한 오브젝트를 생성합니다.

```shell-session
$ oc create -f pvc-manila.yaml
```

새 PVC가 생성됩니다.

볼륨이 생성되고 준비되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get pvc pvc-manila
```

`pvc-manila` 에 `Bound` 가 표시됩니다.

이제 새 PVC를 사용하여 Pod를 구성할 수 있습니다.

#### 6.19.5. Manila 공유 액세스 규칙 사용자 정의

기본적으로 OpenShift Container Platform은 모든 IPv4 클라이언트에 대한 액세스를 제공하는 Manila 스토리지 클래스를 생성합니다. 클라이언트 액세스를 제한하려면 `nfs-ShareClient` 매개변수를 사용하여 특정 클라이언트 IP 주소 또는 서브넷을 사용하는 사용자 지정 스토리지 클래스를 정의할 수 있습니다.

중요

액세스 규칙이 제한된 사용자 정의 스토리지 클래스를 사용하는 경우 다음 조건을 충족해야 합니다.

지정된 IP 주소 또는 서브넷에는 스토리지에 액세스해야 하는 모든 OpenShift Container Platform 노드가 포함됩니다.

RHOSP의 Manila 서비스는 스토리지 클래스에 지정된 공유 유형을 지원합니다.

허용된 클라이언트와 Manila 공유 서버 간에 네트워크 연결이 존재합니다.

사전 요구 사항

RHOSP(Red Hat OpenStack Platform)는 적절한 Manila 공유 인프라와 함께 배포됩니다.

관리자 권한으로 클러스터에 액세스합니다.

프로세스

다음 예제를 기반으로 사용자 정의 스토리지 클래스에 대한 YAML 파일을 생성합니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: csi-manila-gold-restricted
provisioner: manila.csi.openstack.org
parameters:
  type: gold
  nfs-ShareClient: "10.0.0.0/24,192.168.1.100"
  csi.storage.k8s.io/provisioner-secret-name: manila-csi-secret
  csi.storage.k8s.io/provisioner-secret-namespace: openshift-manila-csi-driver
  csi.storage.k8s.io/controller-expand-secret-name: manila-csi-secret
  csi.storage.k8s.io/controller-expand-secret-namespace: openshift-manila-csi-driver
  csi.storage.k8s.io/node-stage-secret-name: manila-csi-secret
  csi.storage.k8s.io/node-stage-secret-namespace: openshift-manila-csi-driver
  csi.storage.k8s.io/node-publish-secret-name: manila-csi-secret
  csi.storage.k8s.io/node-publish-secret-namespace: openshift-manila-csi-driver
allowVolumeExpansion: true
```

1. 사용자 정의 스토리지 클래스에 대한 설명이 포함된 이름입니다.

2. Manila 공유 유형입니다. 이 유형은 RHOSP 환경의 기존 공유 유형과 일치해야 합니다.

3. NFS 공유에 액세스할 수 있는 IP 주소 또는 CIDR 서브넷의 쉼표로 구분된 목록입니다. `nfs-ShareClient` 매개변수는 다양한 형식을 허용합니다.

단일 IP 주소: `192.168.1.100`

CIDR 서브넷: `10.0.0.0/24`

여러 항목: `10.0.0.0/24,192.168.1.100,172.16.0.0/16`

지정된 IP 주소 또는 서브넷에 영구 볼륨을 올바르게 마운트할 수 있도록 OpenShift Container Platform 클러스터 노드가 포함되어 있는지 확인합니다.

이 예에서 액세스는 `10.0.0.0/24` 서브넷으로 제한되며 특정 IP 주소는 `192.168.1.100` 입니다.

다음 명령을 실행하여 파일에서 스토리지 클래스를 적용합니다.

```shell-session
$ oc apply -f custom-manila-storageclass.yaml
```

다음 명령을 실행하여 스토리지 클래스가 생성되었는지 확인합니다.

```shell-session
$ oc get storageclass csi-manila-gold-restricted
```

```shell-session
NAME                            PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
csi-manila-gold-restricted  manila.csi.openstack.org   Delete          Immediate           true                   43m
```

다음 예제를 기반으로 사용자 정의 스토리지 클래스를 사용하는 PVC(영구 볼륨 클레임)를 생성합니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-manila-restricted
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: csi-manila-gold-restricted
```

1. 액세스 권한이 제한된 사용자 정의 스토리지 클래스의 이름입니다. 이 예에서 이름은 `csi-manila-gold-restricted` 입니다.

다음 명령을 실행하여 파일에서 PVC를 적용합니다.

```shell-session
$ oc apply -f pvc-manila-restricted.yaml
```

추가 리소스

CSI 볼륨 구성

#### 6.20.1. 개요

Kubernetes 시크릿은 Base64 인코딩으로 저장됩니다. etcd는 이러한 시크릿을 위해 미사용 암호화를 제공하지만 시크릿이 검색되면 암호 해독되어 사용자에게 제공됩니다. 클러스터에서 역할 기반 액세스 제어가 제대로 구성되지 않은 경우 API 또는 etcd 액세스 권한이 있는 모든 사용자가 시크릿을 검색하거나 수정할 수 있습니다. 또한 네임스페이스에서 Pod를 생성할 권한이 있는 사용자는 해당 액세스 권한을 사용하여 해당 네임스페이스의 보안을 읽을 수 있습니다.

보안을 안전하게 저장하고 관리하려면 공급자 플러그인을 사용하여 OpenShift Container Platform Store Container Storage Interface (CSI) Driver Operator를 구성하여 Azure Key Vault와 같은 외부 시크릿 관리 시스템에서 시크릿을 마운트할 수 있습니다. 그러면 애플리케이션에서 시크릿을 사용할 수 있지만 애플리케이션 pod를 삭제한 후에는 시스템에서 시크릿이 유지되지 않습니다.

Secrets Store CSI Driver Operator, `secrets-store.csi.k8s.io` 를 사용하면 OpenShift Container Platform에서 엔터프라이즈급 외부 시크릿 저장소에 저장된 여러 시크릿, 키 및 인증서를 볼륨으로 마운트할 수 있습니다. Secrets Store CSI Driver Operator는 gRPC를 사용하여 공급자와 통신하여 지정된 외부 시크릿 저장소에서 마운트 콘텐츠를 가져옵니다. 볼륨이 연결되면 해당 데이터가 컨테이너의 파일 시스템에 마운트됩니다. 시크릿 저장소 볼륨은 인라인으로 마운트됩니다.

CSI 인라인 볼륨에 대한 자세한 내용은 CSI 인라인 임시 볼륨을 참조하십시오.

CSI 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

#### 6.20.1.1. 보안 저장소 공급자

Secrets Store CSI Driver Operator는 다음 보안 저장소 공급자로 테스트되었습니다.

AWS Secrets Manager

AWS Systems Manager 매개변수 저장소

Azure Key Vault

Google Secret Manager

HashiCorp Vault

참고

Red Hat은 타사 보안 저장소 공급자 기능과 관련된 모든 요소를 테스트하지 않습니다. 타사 지원에 대한 자세한 내용은 Red Hat 타사 지원 정책을 참조하십시오.

#### 6.20.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.20.3. 연결이 끊긴 환경 지원

다음 보안 저장소 공급자는 연결이 끊긴 클러스터에서 Secrets Store CSI 드라이버 사용을 지원합니다.

AWS Secrets Manager

Azure Key Vault

Google Secret Manager

HashiCorp Vault

Secrets Store CSI 드라이버와 시크릿 저장소 공급자 간의 통신을 활성화하려면 VPC(Virtual Private Cloud) 끝점 또는 해당 시크릿 저장소 공급자, OpenID Connect(OIDC) 발행자 및 STS(Secure Token Service)와 동일한 연결을 구성합니다. 정확한 구성은 시크릿 저장소 공급자, 인증 방법 및 연결이 끊긴 클러스터 유형에 따라 다릅니다.

참고

연결이 끊긴 환경에 대한 자세한 내용은 연결이 끊긴 환경 정보를 참조하십시오.

#### 6.20.4. 네트워크 정책 지원

Secrets Store CSI Driver Operator에는 보안을 강화하기 위해 사전 정의된 `NetworkPolicies` 리소스가 포함되어 있습니다. 이러한 정책은 SS-CSI Operator와 관련 드라이버 모두에 대한 수신 및 송신 트래픽을 제어합니다.

다음 표에는 기본 수신 및 송신 규칙이 요약되어 있습니다.

| Component | Ingress 포트 | 송신 포트 | 설명 |
| --- | --- | --- | --- |
| secrets Store CSI Driver Operator | `8443` | `6443` | 메트릭에 액세스하고 API 서버와 통신 |
| 보안 저장소 CSI 드라이버 | `8095` | `6443` | 메트릭에 액세스하고 API 서버와 통신 |

#### 6.20.5. Secrets Store CSI 드라이버 설치

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

클러스터에 대한 관리자 액세스 권한

프로세스

Secrets Store CSI 드라이버를 설치하려면 다음을 수행합니다.

Secrets Store CSI Driver Operator를 설치합니다.

웹 콘솔에 로그인합니다.

Ecosystem → Software Catalog 를 클릭합니다.

필터 상자에 "Secrets Store CSI"를 입력하여 Secrets Store CSI 드라이버 Operator를 찾습니다.

Secrets Store CSI Driver Operator 버튼을 클릭합니다.

Secrets Store CSI Driver Operator 페이지에서 설치를 클릭합니다.

Operator 설치 페이지에서 다음을 확인합니다.

클러스터의 모든 네임스페이스(기본값) 가 선택됩니다.

설치된 네임스페이스 는 openshift-cluster-csi-drivers 로 설정됩니다.

설치 를 클릭합니다.

설치가 완료되면 Secrets Store CSI Driver Operator가 웹 콘솔의 설치된 Operator 섹션에 나열됩니다.

드라이버에 대한 `ClusterCSIDriver` 인스턴스를 생성합니다(`secret-store.csi.k8s.io`).

Administration → CustomResourceDefinitions → ClusterCSIDriver 를 클릭합니다.

Instances 탭에서 Create ClusterCSIDriver 를 클릭합니다.

다음 YAML 파일을 사용합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: ClusterCSIDriver
metadata:
    name: secrets-store.csi.k8s.io
spec:
  managementState: Managed
```

생성 을 클릭합니다.

다음 단계

외부 시크릿 저장소에서 CSI 볼륨으로 보안 마운트

#### 6.20.6. Secrets Store CSI Driver Operator 설치 제거

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

클러스터에 대한 관리자 액세스 권한

프로세스

Secrets Store CSI Driver Operator를 설치 제거하려면 다음을 수행합니다.

`secrets-store.csi.k8s.io` 공급자를 사용하는 모든 애플리케이션 Pod를 중지합니다.

선택한 시크릿 저장소에 대한 타사 공급자 플러그인을 제거합니다.

CSI(Container Storage Interface) 드라이버 및 관련 매니페스트를 제거합니다.

Administration → CustomResourceDefinitions → ClusterCSIDriver 를 클릭합니다.

인스턴스 탭에서 secrets-store.csi.k8s.io 의 경우 맨 왼쪽에 있는 드롭다운 메뉴를 클릭한 다음 ClusterCSIDriver 삭제 를 클릭합니다.

메시지가 표시되면 삭제 를 클릭합니다.

CSI 드라이버 Pod가 더 이상 실행되지 않는지 확인합니다.

Secrets Store CSI Driver Operator를 설치 제거합니다.

참고

Operator를 설치 제거하려면 CSI 드라이버를 먼저 제거해야 합니다.

Ecosystem → 설치된 Operators를 클릭합니다.

설치된 Operator 페이지에서 스크롤하거나 "Secrets Store CSI"를 이름으로 검색 상자에 입력하여 Operator를 찾은 다음 클릭합니다.

설치된 Operator > Operator 세부 정보 페이지 오른쪽 상단에서 작업 → Operator 설치 제거를 클릭합니다.

Operator 설치 제거 창이 표시되면 제거 버튼을 클릭하여 네임스페이스에서 Operator를 제거합니다. 클러스터에 Operator가 배포한 애플리케이션을 수동으로 정리해야 합니다.

설치 제거 후 Secrets Store CSI Driver Operator는 더 이상 웹 콘솔의 설치된 Operator 섹션에 나열되지 않습니다.

#### 6.20.7. 추가 리소스

CSI 볼륨 구성

### 6.21. CIFS/SMB CSI Driver Operator

OpenShift Container Platform은 CIFS(Common Internet File System)alect/SMB(Server Message Block) 프로토콜용 CSI(Container Storage Interface) 드라이버를 사용하여 PV(영구 볼륨)를 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

CIFS/SMB CSI Driver Operator를 설치한 후 OpenShift Container Platform은 기본적으로 `openshift-cluster-csi-drivers` 네임스페이스에 Operator 및 드라이버에 대한 해당 Pod를 설치합니다. 이를 통해 CIFS/SMB CSI 드라이버는 CIFS/SMB 공유에 마운트되는 CSI(영구 볼륨)를 생성할 수 있습니다.

CIFS/SMB CSI Driver Operator 는 설치 후 PVC(영구 볼륨 클레임)를 생성하는 데 사용할 스토리지 클래스를 생성하지 않습니다. 그러나 동적 프로비저닝을 위해 CIFS/SMB `StorageClass` 를 수동으로 만들 수 있습니다. CIFS/SMB CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있도록 하여 동적 볼륨 프로비저닝을 지원합니다. 이렇게 하면 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없습니다.

CIFS/SMB CSI 드라이버 를 사용하면 CIFS/SMB PV를 생성하고 마운트할 수 있습니다.

#### 6.21.1. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.21.2. 제한

다음 제한 사항은 CIFS(Common Internet File System)/SMB(Server Message Block) CSI(Container Storage Interface) Driver Operator에 적용됩니다.

FIPS 모드는 지원되지 않습니다.

연방 정보 처리 표준(FIPS) 모드가 활성화되면 md4 및 md5의 사용이 비활성화되어 사용자가 ntlm, ntlmv2 또는 ntlmssp 인증을 사용할 수 없습니다. 또한 서명은 md5를 사용하므로 사용할 수 없습니다. FIPS 모드가 활성화되면 이러한 방법을 사용하는 CIFS 마운트가 실패합니다.

HTTP 프록시 구성을 사용하여 클러스터 SMB 서버 외부에 연결하는 것은 CSI 드라이버에서 지원되지 않습니다.

CIFS/SMB는 LAN 프로토콜이며 서브넷으로 라우팅할 수 있지만 WAN을 통해 확장하도록 설계되지 않으며 HTTP 프록시 설정을 지원하지 않습니다.

CIFS/SMB CSI Driver Operator는 Windows DFS(Distributed File System)를 지원하지 않습니다.

Kerberos 인증은 지원되지 않습니다.

SMB CSI는 Samba v4.21.2 및 Windows Server 2019 및 Windows Server 2022에서 테스트되었습니다.

#### 6.21.3. CIFS/SMB CSI Driver Operator 설치

CIFS/SMB CSI Driver Operator(Red Hat Operator)는 기본적으로 OpenShift Container Platform에 설치되지 않습니다. 다음 절차에 따라 클러스터에서 CIFS/SMB CSI Driver Operator를 설치하고 구성합니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

프로세스

웹 콘솔에서 CIFS/SMB CSI Driver Operator를 설치하려면 다음을 수행합니다.

웹 콘솔에 로그인합니다.

CIFS/SMB CSI Operator를 설치합니다.

Ecosystem → Software Catalog 를 클릭합니다.

필터 상자에 CIFS/SMB CSI를 입력하여 CIFS/SMB CSI Operator를 찾습니다.

CIFS/SMB CSI Driver Operator 버튼을 클릭합니다.

CIFS/SMB CSI Driver Operator 페이지에서 설치를 클릭합니다.

Operator 설치 페이지에서 다음을 확인합니다.

클러스터의 모든 네임스페이스(기본값) 가 선택됩니다.

설치된 네임스페이스 는 openshift-cluster-csi-drivers 로 설정됩니다.

설치 를 클릭합니다.

설치가 완료되면 웹 콘솔의 Installed Operators 섹션에 CIFS/SMB CSI Operator가 나열됩니다.

#### 6.21.4. CIFS/SMB CSI 드라이버 설치

CIFS/SMB CSI(Container Storage Interface) Driver Operator를 설치한 후 CIFS/SMB CSI 드라이버를 설치합니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

CIFS/SMB CSI Driver Operator가 설치되었습니다.

프로세스

Administration → CustomResourceDefinitions → ClusterCSIDriver 를 클릭합니다.

Instances 탭에서 Create ClusterCSIDriver 를 클릭합니다.

다음 YAML 파일을 사용합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: ClusterCSIDriver
metadata:
    name: smb.csi.k8s.io
spec:
  managementState: Managed
```

생성 을 클릭합니다.

다음 조건이 "True" 상태로 변경될 때까지 기다립니다.

`SambaDriverControllerServiceControllerAvailable`

`SambaDriverNodeServiceControllerAvailable`

#### 6.21.5. 동적 프로비저닝

CIFS(Common Internet File System) 모음/SMB(Server Message Block) 프로토콜 볼륨의 동적 프로비저닝을 위한 스토리지 클래스를 생성할 수 있습니다. 프로비저닝 볼륨은 스토리지 클래스에 정의된 `소스에` PV(영구 볼륨) 이름이 있는 하위 디렉터리를 생성합니다.

사전 요구 사항

CIFS/SMB CSI Driver Operator 및 드라이버 설치

실행 중인 OpenShift Container Platform 클러스터에 로그인되어 있습니다.

SMB 서버를 설치하고 서버에 대한 다음 정보를 알고 있습니다.

호스트 이름

공유 이름

사용자 이름 및 암호

프로세스

동적 프로비저닝을 설정하려면 다음을 수행합니다.

다음 예제 YAML 파일과 함께 다음 명령을 사용하여 Samba 서버에 액세스할 수 있는 보안을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: smbcreds
  namespace: samba-server
stringData:
  username: <username>
  password: <password>
```

1. Samba 서버의 시크릿 이름입니다.

2. Samba 서버의 시크릿 네임스페이스입니다.

3. Samba 서버의 시크릿 사용자 이름입니다.

4. Samba 서버의 시크릿 암호입니다.

다음 예제 YAML 파일로 다음 명령을 실행하여 스토리지 클래스를 생성합니다.

```shell-session
$ oc create -f <sc_file_name>.yaml
```

1. 스토리지 클래스 YAML 파일의 이름입니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <sc_name>
provisioner: smb.csi.k8s.io
parameters:
  source: //<hostname>/<shares>
  csi.storage.k8s.io/provisioner-secret-name: smbcreds
  csi.storage.k8s.io/provisioner-secret-namespace: samba-server
  csi.storage.k8s.io/node-stage-secret-name: smbcreds
  csi.storage.k8s.io/node-stage-secret-namespace: samba-server
reclaimPolicy: Delete
volumeBindingMode: Immediate
mountOptions:
  - dir_mode=0777
  - file_mode=0777
  - uid=1001
  - gid=1001
```

1. 스토리지 클래스의 이름입니다.

2. Samba 서버는 어디에나 설치되고 <'hostname>'이 Samba 서버의 호스트 이름이고 서버가 내보낸 `공유` 사이에 있도록 구성된 경로인 클러스터에서 연결할 수 있어야 합니다.

3. 5

이전 단계에서 설정한 Samba 서버의 시크릿 이름입니다. `csi.storage.k8s.io/provisioner-secret` 이 제공되면 `소스` 아래에 PV 이름이 포함된 하위 디렉터리가 생성됩니다.

4. 6

이전 단계에서 설정한 Samba 서버의 Secret의 네임스페이스입니다.

PVC를 생성합니다.

다음 예제 YAML 파일로 다음 명령을 실행하여 PVC를 생성합니다.

```shell-session
$ oc create -f <pv_file_name>.yaml
```

1. PVC YAML 파일의 이름입니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: <pvc_name>
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: <storage_amount>
  storageClassName: <sc_name>
```

1. PVC의 이름입니다.

2. 스토리지 요청 양.

3. 이전 단계에서 만든 CIFS/SMB 스토리지 클래스의 이름입니다.

다음 명령을 실행하여 PVC가 생성되었고 "Bound" 상태에 있는지 확인합니다.

```shell-session
$ oc describe pvc <pvc_name>
```

1. 이전 단계에서 생성한 PVC의 이름입니다.

```shell-session
Name:          pvc-test
Namespace:     default
StorageClass:  samba
Status:        Bound
...
```

1. PVC는 Bound 상태입니다.

#### 6.21.6. 정적 프로비저닝

정적 프로비저닝을 사용하여 기존 SMB(Server Message Block Protocol) 공유를 사용하기 위해 PV(영구 볼륨) 및 PVC(영구 볼륨 클레임)를 생성할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

CIFS/SMB CSI Driver Operator 및 드라이버 설치

SMB 서버를 설치하고 서버에 대한 다음 정보를 알고 있습니다.

호스트 이름

공유 이름

사용자 이름 및 암호

프로세스

정적 프로비저닝을 설정하려면 다음을 수행합니다.

다음 예제 YAML 파일과 함께 다음 명령을 사용하여 Samba 서버에 액세스할 수 있는 보안을 생성합니다.

```shell-session
$ oc create -f <file_name>.yaml
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: smbcreds
  namespace: samba-server
stringData:
  username: <username>
  password: <password>
```

1. Samba 서버의 시크릿 이름입니다.

2. Samba 서버의 시크릿 네임스페이스입니다.

3. Samba 서버의 시크릿 사용자 이름입니다.

4. Samba 서버의 시크릿 암호입니다.

다음 예제 YAML 파일로 다음 명령을 실행하여 PV를 생성합니다.

```shell-session
$ oc create -f <pv_file_name>.yaml
```

1. PV YAML 파일의 이름입니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  annotations:
    pv.kubernetes.io/provisioned-by: smb.csi.k8s.io
  name: <pv_name>
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
  mountOptions:
    - dir_mode=0777
    - file_mode=0777
  csi:
    driver: smb.csi.k8s.io
    volumeHandle: smb-server.default.svc.cluster.local/share#
    volumeAttributes:
      source: //<hostname>/<shares>
    nodeStageSecretRef:
      name: <secret_name_shares>
      namespace: <namespace>
```

1. PV의 이름입니다.

2. `volumeHandle` 형식: {smb-server-address}#{sub-dir-name}#{share-name}. 이 값이 클러스터의 모든 공유에 대해 고유한지 확인합니다.

3. Samba 서버는 어디에나 설치되고 <hostname>이 Samba 서버의 호스트 이름이고 서버가 내보낸 공유 사이에 있도록 구성된 경로인 클러스터에서 연결할 수 있어야 합니다.

4. 공유의 시크릿 이름입니다.

5. 해당 네임스페이스입니다.

PVC를 생성합니다.

다음 예제 YAML 파일로 다음 명령을 실행하여 PVC를 생성합니다.

```shell-session
$ oc create -f <pv_file_name>.yaml
```

1. PVC YAML 파일의 이름입니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: <pvc_name>
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: <storage_amount>
  storageClassName: ""
  volumeName: <pv_name>
```

1. PVC의 이름입니다.

2. 스토리지 요청 양.

3. 첫 번째 단계에서 PV의 이름입니다.

다음 명령을 실행하여 PVC가 생성되었고 "Bound" 상태에 있는지 확인합니다.

```shell-session
$ oc describe pvc <pvc_name>
```

1. 이전 단계에서 생성한 PVC의 이름입니다.

```shell-session
Name:          pvc-test
Namespace:     default
StorageClass:
Status:        Bound
...
```

1. PVC는 Bound 상태입니다.

다음 예제 YAML 파일로 다음 명령을 실행하여 Linux에 배포를 생성합니다.

참고

다음 배포는 이전 단계에서 생성된 PV 및 PVC를 사용하는 데 필요하지 않습니다. 이는 사용할 수 있는 방법의 예입니다.

```shell-session
$ oc create -f <deployment_file_name>.yaml
```

1. 배포 YAML 파일의 이름입니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx
  name: <deployment_name>
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
      name: <deployment_name>
    spec:
      nodeSelector:
        "kubernetes.io/os": linux
      containers:
        - name: <deployment_name>
          image: quay.io/centos/centos:stream8
          command:
            - "/bin/bash"
            - "-c"
            - set -euo pipefail; while true; do echo $(date) >> <mount_path>/outfile; sleep 1; done
          volumeMounts:
            - name: <vol_mount_name>
              mountPath: <mount_path>
              readOnly: false
      volumes:
        - name: <vol_mount_name>
          persistentVolumeClaim:
            claimName: <pvc_name>
  strategy:
    rollingUpdate:
      maxSurge: 0
      maxUnavailable: 1
    type: RollingUpdate
```

1. 2

3. 배포 이름입니다.

4. 6

볼륨 마운트 경로입니다.

5. 7

볼륨 마운트의 이름입니다.

8. 이전 단계에서 생성된 PVC의 이름입니다.

컨테이너에서 `df -h` 명령을 실행하여 설정을 확인합니다.

```shell-session
$ oc exec -it <pod_name> -- df -h
```

1. Pod의 이름입니다.

```shell-session
Filesystem            Size  Used Avail Use% Mounted on
...
/dev/sda1              97G   21G   77G  22% /etc/hosts
//20.43.191.64/share   97G   21G   77G  22% /mnt/smb
...
```

이 예제에는 CIFS(Common Internet File System) 파일 시스템으로 마운트된 `/mnt/smb` 디렉터리가 있습니다.

#### 6.21.7. 추가 리소스

CSI 볼륨 구성

#### 6.22.1. 개요

OpenShift Container Platform은 VMDK(Virtual Machine Disk) 볼륨용 CSI(Container Storage Interface) VMware vSphere 드라이버를 사용하여 영구 볼륨(PV)을 프로비저닝할 수 있습니다.

CSI Operator 및 드라이버를 사용할 때는 영구 스토리지 및 CSI 볼륨 구성에 대해 숙지하는 것이 좋습니다.

vSphere 스토리지 자산에 마운트되는 CSI(영구 볼륨)를 생성하기 위해 OpenShift Container Platform은 `openshift-cluster-csi-drivers` 네임스페이스에 기본적으로 vSphere CSI Driver Operator 및 vSphere CSI 드라이버를 설치합니다.

vSphere CSI Driver Operator: Operator는 PVC(영구 볼륨 클레임)를 생성하는 데 사용할 수 있는 `thin-csi` 라는 스토리지 클래스를 제공합니다. vSphere CSI Driver Operator는 필요에 따라 스토리지 볼륨을 생성할 수 있어 클러스터 관리자가 스토리지를 사전 프로비저닝할 필요가 없어 동적 볼륨 프로비저닝을 지원합니다. 필요한 경우 이 기본 스토리지 클래스를 비활성화할 수 있습니다(기본 스토리지 클래스 관리 참조).

vSphere CSI 드라이버: 이 드라이버를 사용하면 vSphere PV를 생성 및 마운트할 수 있습니다. OpenShift Container Platform 4.20에서 드라이버 버전은 3.5.0입니다. vSphere CSI 드라이버는 XFS 및 Ext4를 포함하여 기본 Red Hat Core 운영 체제 릴리스에서 지원하는 모든 파일 시스템을 지원합니다. 지원되는 파일 시스템에 대한 자세한 내용은 사용 가능한 파일 시스템 개요 를 참조하십시오.

참고

새로운 설치의 경우 OpenShift Container Platform 4.13 이상에서는 vSphere in-tree 볼륨 플러그인에 대한 자동 마이그레이션을 동등한 CSI 드라이버로 제공합니다. OpenShift Container Platform 4.15 이상으로 업데이트하면 자동 마이그레이션도 제공됩니다. 업데이트 및 마이그레이션에 대한 자세한 내용은 CSI 자동 마이그레이션 을 참조하십시오.

CSI 자동 마이그레이션이 원활해야 합니다. 마이그레이션은 영구 볼륨, 영구 볼륨 클레임 및 스토리지 클래스와 같은 기존 API 오브젝트를 사용하는 방법을 변경하지 않습니다.

#### 6.22.2. CSI 정보

스토리지 벤더는 일반적으로 Kubernetes의 일부로 스토리지 드라이버를 제공합니다. CSI(Container Storage Interface) 구현을 통해 타사 공급자는 코어 Kubernetes 코드를 변경하지 않고도 표준 인터페이스를 사용하여 스토리지 플러그인을 제공할 수 있습니다.

CSI Operator는 in-tree 볼륨 플러그인에서 사용할 수 없는 볼륨 스냅샷과 같은 OpenShift Container Platform 사용자 스토리지 옵션을 제공합니다.

#### 6.22.3. vSphere CSI 제한 사항

다음 제한 사항은 vSphere CSI(Container Storage Interface) Driver Operator에 적용됩니다.

vSphere CSI 드라이버는 동적 및 정적 프로비저닝을 지원합니다. 그러나 PV 사양에서 정적 프로비저닝을 사용하는 경우 이 키가 동적으로 프로비저닝된 PV를 나타내므로 `csi.volumeAttributes` 에서 키 `storage.kubernetes.io/csiProvisionerIdentity` 를 사용하지 마십시오.

vSphere 클라이언트 인터페이스를 사용하여 데이터 저장소 간에 영구 컨테이너 볼륨을 마이그레이션하는 것은 OpenShift Container Platform에서 지원되지 않습니다.

#### 6.22.4. vSphere 스토리지 정책

vSphere CSI Driver Operator 스토리지 클래스는 vSphere의 스토리지 정책을 사용합니다. OpenShift Container Platform은 클라우드 구성에 구성된 데이터 저장소를 대상으로 하는 스토리지 정책을 자동으로 생성합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: thin-csi
provisioner: csi.vsphere.vmware.com
parameters:
  StoragePolicyName: "$openshift-storage-policy-xxxx"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: false
reclaimPolicy: Delete
```

#### 6.22.5. ReadWriteMany vSphere 볼륨 지원

기본 vSphere 환경에서 vSAN 파일 서비스를 지원하는 경우 OpenShift Container Platform에서 설치한 vSphere CSI(Container Storage Interface) Driver Operator는 RWX(ReadWriteMany) 볼륨의 프로비저닝을 지원합니다. vSAN 파일 서비스가 구성되지 않은 경우 RWO(ReadWriteOnce)가 사용 가능한 유일한 액세스 모드입니다. vSAN 파일 서비스가 구성되어 있지 않고 RWX를 요청하면 볼륨이 생성되지 않고 오류가 기록됩니다.

사용자 환경에서 vSAN 파일 서비스를 구성하는 방법에 대한 자세한 내용은 vSAN 파일 서비스를 참조하십시오.

다음과 같은 PVC(영구 볼륨 클레임)를 수행하여 RWX 볼륨을 요청할 수 있습니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: myclaim
spec:
  resources:
    requests:
      storage: 1Gi
  accessModes:
     - ReadWriteMany
  storageClassName: thin-csi
```

RWX 볼륨 유형의 PVC를 요청하면 vSAN 파일 서비스에서 지원하는 PV(영구 볼륨)가 프로비저닝됩니다.

#### 6.22.6. VMware vSphere CSI Driver Operator 요구 사항

vSphere CSI(Container Storage Interface) Driver Operator를 설치하려면 다음 요구 사항을 충족해야 합니다.

VMware vSphere 버전: 8.0 업데이트 1 이상 또는 VMware Cloud Foundation 5.0 이상

vCenter 버전: 8.0 업데이트 1 이상 또는 VMware Cloud Foundation 5.0 이상

하드웨어 버전 15 이상의 가상 머신

클러스터에 이미 설치된 타사 vSphere CSI 드라이버가 없습니다

타사 vSphere CSI 드라이버가 클러스터에 있는 경우 OpenShift Container Platform은 이를 덮어쓰지 않습니다. 타사 vSphere CSI 드라이버가 있으면 OpenShift Container Platform이 OpenShift Container Platform 4.13 이상으로 업데이트되지 않습니다.

참고

VMware vSphere CSI Driver Operator는 설치 매니페스트에서 `platform: vsphere` 와 함께 배포된 클러스터에서만 지원됩니다.

CSI(Container Storage Interface) 드라이버, vSphere CSI Driver Operator 및 vSphere Problem Detector Operator에 대한 사용자 정의 역할을 생성할 수 있습니다. 사용자 지정 역할에는 각 vSphere 오브젝트에 최소 권한 세트를 할당하는 권한 세트가 포함될 수 있습니다. 즉 CSI 드라이버, vSphere CSI Driver Operator 및 vSphere Problem Detector Operator가 이러한 오브젝트와의 기본 상호 작용을 설정할 수 있습니다.

중요

vCenter에 OpenShift Container Platform 클러스터를 설치하는 것은 "필수 vCenter 계정 권한" 섹션에 설명된 대로 전체 권한 목록에 대해 테스트됩니다. 전체 권한 목록을 준수하면 제한된 권한 세트를 사용하여 사용자 지정 역할을 생성할 때 발생할 수 있는 예기치 않고 지원되지 않는 동작의 가능성을 줄일 수 있습니다.

타사 CSI 드라이버를 제거하려면 타사 vSphere CSI 드라이버 제거를 참조하십시오.

#### 6.22.7. 타사 vSphere CSI Driver Operator 제거

OpenShift Container Platform 4.10 이상에는 Red Hat에서 지원하는 vSphere CSI(Container Storage Interface) Operator 드라이버 기본 제공 버전이 포함되어 있습니다. 커뮤니티 또는 다른 공급 업체가 제공하는 vSphere CSI 드라이버를 설치한 경우 클러스터에 대해 4.13 이상과 같은 OpenShift Container Platform의 다음 주요 버전으로 업데이트를 비활성화할 수 있습니다.

OpenShift Container Platform 4.12 이상에서는 클러스터가 완전히 지원되며 4.12.z와 같은 z-stream 릴리스의 업데이트는 차단되지 않지만 OpenShift Container Platform의 다음 주요 버전으로 업데이트하기 전에 타사 vSphere CSI 드라이버를 제거하여 이 상태를 수정해야 합니다. 타사 vSphere CSI 드라이버를 제거해도 연결된 PV(영구 볼륨) 오브젝트를 삭제할 필요가 없으며 데이터 손실이 발생하지 않습니다.

참고

이러한 지침은 완료되지 않을 수 있으므로 공급 업체 또는 커뮤니티 공급자 제거 가이드를 참조하여 드라이버 및 구성 요소를 제거하십시오.

타사 vSphere CSI 드라이버를 설치 제거하려면 다음을 수행합니다.

타사 vSphere CSI 드라이버(VMware vSphere Container Storage 플러그인) Deployment 및 Daemonset 오브젝트를 삭제합니다.

타사 vSphere CSI 드라이버와 함께 이전에 설치된 configmap 및 secret 오브젝트를 삭제합니다.

타사 vSphere CSI 드라이버 `CSIDriver` 오브젝트를 삭제합니다.

```shell-session
$ oc delete CSIDriver csi.vsphere.vmware.com
```

```shell-session
csidriver.storage.k8s.io "csi.vsphere.vmware.com" deleted
```

OpenShift Container Platform 클러스터에서 타사 vSphere CSI 드라이버를 제거한 후 Red Hat vSphere CSI Driver Operator를 자동으로 다시 시작하며 OpenShift Container Platform 4.11 이상으로의 업그레이드를 차단할 수 있는 모든 조건이 자동으로 제거됩니다. 기존 vSphere CSI PV 오브젝트가 있는 경우 이제 Red Hat의 vSphere CSI Driver Operator에서 라이프사이클을 관리합니다.

#### 6.22.8. vSphere 영구 디스크 암호화

vSphere에서 실행 중인 OpenShift Container Platform에서 VM(가상 머신)과 동적으로 프로비저닝된 PV(영구 볼륨)를 암호화할 수 있습니다.

참고

OpenShift Container Platform은 RWX 암호화 PV를 지원하지 않습니다. 암호화된 스토리지 정책을 사용하는 스토리지 클래스 중 RWX PV를 요청할 수 없습니다.

설치 중 또는 설치 후 수행할 수 있는 PV를 암호화하기 전에 VM을 암호화해야 합니다.

VM 암호화에 대한 자세한 내용은 다음을 참조하십시오.

가상 머신 암호화 요구사항

설치 중: RHCOS 설치의 7 단계 및 OpenShift Container Platform 부트스트랩 프로세스 시작

vSphere 클러스터에서 암호화 활성화

VM을 암호화한 후 vSphere CSI(Container Storage Interface) 드라이버를 사용하여 동적 암호화 볼륨 프로비저닝을 지원하는 스토리지 클래스를 구성할 수 있습니다. 이 작업은 다음 두 가지 방법 중 하나로 수행할 수 있습니다.

Datastore URL:이 방법은 매우 유연하지 않으며 단일 데이터 저장소를 사용하도록 강제합니다. 토폴로지 인식 프로비저닝도 지원하지 않습니다.

태그 기반 배치: 프로비저닝된 볼륨을 암호화하고 태그 기반 배치를 사용하여 특정 데이터 저장소를 대상으로 합니다.

#### 6.22.8.1. 데이터 저장소 URL 사용

프로세스

데이터 저장소 URL을 사용하여 암호화하려면 다음을 수행합니다.

암호화를 지원하는 데이터 저장소의 기본 스토리지 정책 이름을 확인합니다.

이 정책은 VM을 암호화하는 데 사용된 정책과 동일합니다.

이 스토리지 정책을 사용하는 스토리지 클래스를 생성합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
 name: encryption
provisioner: csi.vsphere.vmware.com
parameters:
 storagePolicyName: <storage-policy-name>
 datastoreurl: "ds:///vmfs/volumes/vsan:522e875627d-b090c96b526bb79c/"
```

1. 암호화를 지원하는 데이터 저장소의 기본 스토리지 정책 이름

#### 6.22.8.2. 태그 기반 배치 사용

프로세스

태그 기반 배치를 사용하여 암호화하려면 다음을 수행합니다.

vCenter에서 이 스토리지 클래스에서 사용할 수 있는 데이터 저장소를 태그하는 카테고리를 생성합니다. 또한 StoragePod(Datastore 클러스터), Datastore (데이터 저장소) 및 폴더 가 생성된 카테고리에 대해 Associable Entities로 선택되어 있는지 확인합니다.

vCenter에서 이전에 만든 카테고리를 사용하는 태그를 생성합니다.

스토리지 클래스에서 사용할 수 있는 각 데이터 저장소에 이전에 생성된 태그를 할당합니다. 데이터 저장소가 OpenShift Container Platform 클러스터에 참여하는 호스트와 공유되는지 확인합니다.

vCenter의 주 메뉴에서 정책 및 프로필을 클릭합니다.

정책 및 프로필 페이지의 탐색 창에서 VM Storage Policies 를 클릭합니다.

만들기를 클릭합니다.

스토리지 정책의 이름을 입력합니다.

호스트 기반 규칙 사용을 선택하고 태그 기반 배치 규칙 사용을 선택합니다.

다음 탭에서 다음을 수행합니다.

암호화 및 기본 암호화 속성을 선택합니다.

이전에 만든 태그 범주를 선택하고 선택한 태그를 선택합니다. 정책이 일치하는 데이터 저장소를 선택 중인지 확인합니다.

스토리지 정책을 생성합니다.

스토리지 정책을 사용하는 스토리지 클래스를 생성합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
 name:  csi-encrypted
provisioner: csi.vsphere.vmware.com
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
parameters:
 storagePolicyName: <storage-policy-name>
```

1. 암호화를 위해 생성한 스토리지 정책의 이름

#### 6.22.9. vSphere CSI에 대한 여러 vCenter 지원

고가용성을 위해 공유 스토리지 없이 여러 vSphere vCenter 클러스터에 OpenShift Container Platform을 배포하는 것이 유용할 수 있습니다. OpenShift Container Platform v4.17 이상에서는 이 기능을 지원합니다.

참고

여러 vCenter는 설치 중에 만 구성할 수 있습니다. 설치 후에는 여러 vCenter를 구성할 수 없습니다.

지원되는 최대 vCenter 클러스터 수는 3개입니다.

#### 6.22.9.1. 설치 중 여러 vCenter 구성

설치 중에 여러 vCenter를 구성하려면 다음을 수행합니다.

설치 중에 여러 vSphere 클러스터를 지정합니다. 자세한 내용은 "Installation configuration parameters for vSphere"를 참조하십시오.

추가 리소스

vSphere에 대한 설치 구성 매개변수입니다.

#### 6.22.10. vSphere CSI 토폴로지 개요

OpenShift Container Platform은 다양한 영역과 지역에 vSphere용 OpenShift Container Platform을 배포할 수 있으므로 여러 컴퓨팅 클러스터 및 데이터 센터에 배포할 수 있으므로 단일 장애 지점을 방지할 수 있습니다.

이는 vCenter에서 영역 및 지역 카테고리를 정의한 다음 이러한 범주를 컴퓨팅 클러스터와 같은 다양한 장애 도메인에 할당하여 이러한 영역 및 지역 카테고리에 대한 태그를 생성하여 수행됩니다. 적절한 카테고리를 생성하고 vCenter 오브젝트에 태그를 할당하면 해당 실패 도메인에서 Pod를 예약하는 VM(가상 머신)을 생성하는 추가 머신 세트를 생성할 수 있습니다.

다음 예제에서는 하나의 리전과 두 개의 영역이 있는 두 개의 실패 도메인을 정의합니다.

| 컴퓨팅 클러스터 | 실패 도메인 | 설명 |
| --- | --- | --- |
| 컴퓨팅 클러스터: ocp1, 데이터 센터: Atlanta | openshift-region: us-east-1 (태그), openshift-zone: us-east-1a (태그) | 이는 us-east-1a 영역과 함께 us-east-1 리전에서 실패 도메인을 정의합니다. |
| 컴퓨터 클러스터: ocp2, 데이터 센터: Atlanta | openshift-region: us-east-1(태그), openshift-zone: us-east-1b(태그) | 이는 us-east-1b라는 동일한 리전 내에서 다른 실패 도메인을 정의합니다. |

#### 6.22.10.1. vSphere CSI 토폴로지 요구사항

vSphere CSI 토폴로지에 다음 지침이 권장됩니다.

호스트가 아닌 데이터 센터 및 컴퓨팅 클러스터에 토폴로지 태그를 추가하는 것이 좋습니다.

vSphere `-problem-detector` 는 `openshift-region` 또는 `openshift-zone` 태그가 데이터 센터 또는 컴퓨팅 클러스터 수준에서 정의되지 않은 경우 경고를 제공합니다. 각 토폴로지 태그(`openshift-region` 또는 `openshift-zone`)가 계층 구조에서 한 번만 발생해야 합니다.

참고

이 권장 사항을 무시하면 CSI 드라이버에서 로그 경고가 표시되고 계층 구조에서 낮은 계층 구조(예: 호스트)가 무시됩니다. VMware는 이 구성을 고려하므로 사용하지 않아야 하는 문제를 방지할 수 있습니다.

토폴로지 인식 환경의 볼륨 프로비저닝 요청은 지정된 토폴로지 세그먼트의 모든 호스트에 액세스할 수 있는 데이터 저장소에 볼륨을 생성하려고 합니다. 여기에는 Kubernetes 노드 VM이 실행되고 있지 않은 호스트가 포함됩니다. 예를 들어 vSphere Container Storage 플러그인 드라이버가 데이터 센터 `dc-1` 에 적용된 `zone-a` 에서 볼륨을 프로비저닝하라는 요청을 수신하는 경우 `dc-1` 아래의 모든 호스트에서 볼륨 프로비저닝을 위해 선택한 데이터 저장소에 액세스할 수 있어야 합니다. 호스트에는 `dc-1` 아래에 직접 있는 것과 `dc-1` 내부의 클러스터의 일부인 호스트가 포함됩니다.

추가 권장 사항은 VMware 지침 및 토폴로지를 사용한 배포 모범 사례 섹션을 참조하십시오.

#### 6.22.10.2.1. 프로세스

설치 중에 토폴로지를 지정합니다. VMware vCenter 섹션의 지역 및 영역 구성 섹션을 참조하십시오.

추가 작업이 필요하지 않으며 OpenShift Container Platform에서 생성한 기본 스토리지 클래스는 토폴로지를 인식하고 다른 장애 도메인에서 볼륨을 프로비저닝할 수 있어야 합니다.

추가 리소스

VMware vCenter의 지역 및 영역 구성

#### 6.22.10.3.1. 프로세스

VMware vCenter vSphere 클라이언트 GUI에서 적절한 영역 및 지역 분류 및 태그를 정의합니다.

vSphere를 사용하면 임의의 이름으로 카테고리를 생성할 수 있지만 OpenShift Container Platform은 토폴로지 카테고리를 정의하는 데 `openshift-region` 및 `openshift-zone` 이름을 사용하는 것이 좋습니다.

vSphere 카테고리 및 태그에 대한 자세한 내용은 VMware vSphere 설명서를 참조하십시오.

OpenShift Container Platform에서 실패 도메인을 생성합니다. vSphere에서 클러스터의 여러 리전 및 영역 지정 섹션을 참조하십시오.

장애 도메인에서 데이터 저장소에 할당할 태그를 생성합니다.

OpenShift Container Platform이 두 개 이상의 장애 도메인을 확장하면 데이터 저장소가 해당 장애 도메인에서 공유되지 않을 수 있습니다. 여기서 PV(영구 볼륨)의 토폴로지 인식 프로비저닝이 유용합니다.

vCenter에서 데이터 저장소 태그를 지정하는 카테고리를 생성합니다. 예를 들면 `openshift-zonal-datastore-cat` 입니다. 카테고리가 OpenShift Container Platform 클러스터에 참여하는 데이터 저장소에 태그를 지정하는 데 고유하게 사용되는 경우 다른 카테고리 이름을 사용할 수 있습니다. 또한 `StoragePod`, `Datastore`, `Folder` 가 생성된 카테고리의 연관 가능한 엔티티로 선택되어 있는지 확인합니다.

vCenter에서 이전에 생성된 카테고리를 사용하는 태그를 생성합니다. 이 예에서는 태그 이름 `openshift-zonal-datastore` 를 사용합니다.

이전에 생성된 태그(이 예에서는 `openshift-zonal-datastore`)를 동적 프로비저닝으로 간주하는 실패 도메인의 각 데이터 저장소에 할당합니다.

참고

데이터 저장소 카테고리 및 태그에 원하는 모든 이름을 사용할 수 있습니다. 이 예제에서 사용되는 이름은 권장 사항으로 제공됩니다. OpenShift Container Platform 클러스터의 모든 호스트와 공유되는 데이터 저장소만 고유하게 정의하는 태그 및 카테고리가 있는지 확인합니다.

필요에 따라 각 실패 도메인의 태그 기반 데이터 저장소를 대상으로 하는 스토리지 정책을 생성합니다.

vCenter의 주 메뉴에서 정책 및 프로필을 클릭합니다.

정책 및 프로필 페이지의 탐색 창에서 VM Storage Policies 를 클릭합니다.

만들기를 클릭합니다.

스토리지 정책의 이름을 입력합니다.

규칙의 경우 태그 배치 규칙을 선택하고 원하는 데이터 저장소를 대상으로 하는 태그 및 카테고리(이 예에서는 `openshift-zonal-datastore` 태그)를 선택합니다.

데이터 저장소는 스토리지 호환성 테이블에 나열됩니다.

새 영역 스토리지 정책을 사용하는 새 스토리지 클래스를 생성합니다.

스토리지 > StorageClass 를 클릭합니다.

StorageClasses 페이지에서 StorageClass 만들기 를 클릭합니다.

이름에 새 스토리지 클래스의 이름을 입력합니다.

Provisioner 에서 csi.vsphere.vmware.com 을 선택합니다.

추가 매개변수 에서 StoragePolicyName 매개변수의 경우 Value 를 이전에 생성한 새 영역 스토리지 정책의 이름으로 설정합니다.

생성 을 클릭합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: zoned-sc
provisioner: csi.vsphere.vmware.com
parameters:
  StoragePolicyName: zoned-storage-policy
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

1. 새 토폴로지 인식 스토리지 클래스 이름입니다.

2. 영역화된 스토리지 정책을 지정합니다.

참고

이전 YAML 파일을 편집하고 아래 명령을 실행하여 스토리지 클래스를 생성할 수도 있습니다.

```shell
oc create -f $FILE
```

추가 리소스

vSphere에서 클러스터의 여러 리전 및 영역 지정

VMware vSphere 태그 문서

#### 6.22.10.4. 인프라 토폴로지 없이 vSphere 스토리지 토폴로지 생성

참고

OpenShift Container Platform은 토폴로지 인식 설정에서 실패 도메인을 지정하는 데 인프라 오브젝트를 사용하는 것이 좋습니다. 인프라 오브젝트에 실패 도메인을 지정하고 `ClusterCSIDriver` 오브젝트에 topology-categories를 지정하는 것은 지원되지 않는 작업입니다.

#### 6.22.10.4.1. 프로세스

VMware vCenter vSphere 클라이언트 GUI에서 적절한 영역 및 지역 분류 및 태그를 정의합니다.

vSphere를 사용하면 임의의 이름으로 카테고리를 생성할 수 있지만 OpenShift Container Platform은 토폴로지를 정의하는 데 `openshift-region` 및 `openshift-zone` 이름을 사용하는 것이 좋습니다.

vSphere 카테고리 및 태그에 대한 자세한 내용은 VMware vSphere 설명서를 참조하십시오.

CSI(컨테이너 스토리지 인터페이스) 드라이버가 이 토폴로지를 감지할 수 있도록 하려면 `clusterCSIDriver` 오브젝트 YAML 파일 `driverConfig` 섹션을 편집합니다.

이전에 생성한 `openshift-zone` 및 `openshift-region` 카테고리를 지정합니다.

`driverType` 을 `vSphere` 로 설정합니다.

```shell-session
~ $ oc edit clustercsidriver csi.vsphere.vmware.com -o yaml
```

```shell-session
apiVersion: operator.openshift.io/v1
kind: ClusterCSIDriver
metadata:
  name: csi.vsphere.vmware.com
spec:
  logLevel: Normal
  managementState: Managed
  observedConfig: null
  operatorLogLevel: Normal
  unsupportedConfigOverrides: null
  driverConfig:
    driverType: vSphere
      vSphere:
        topologyCategories:
        - openshift-zone
        - openshift-region
```

1. `driverType` 이 `vSphere` 로 설정되어 있는지 확인합니다.

2. vCenter에서 이전에 생성된 OpenShift `-zone` 및 `openshift-region` 카테고리입니다.

다음 명령을 실행하여 `CSINode` 오브젝트에 토폴로지 키가 있는지 확인합니다.

```shell-session
~ $ oc get csinode
```

```shell-session
NAME DRIVERS AGE
co8-4s88d-infra-2m5vd 1 27m
co8-4s88d-master-0 1 70m
co8-4s88d-master-1 1 70m
co8-4s88d-master-2 1 70m
co8-4s88d-worker-j2hmg 1 47m
co8-4s88d-worker-mbb46 1 47m
co8-4s88d-worker-zlk7d 1 47m
```

```shell-session
~ $ oc get csinode co8-4s88d-worker-j2hmg -o yaml
```

```shell-session
...
spec:
  drivers:
  - allocatable:
      count: 59
  name: csi-vsphere.vmware.com
  nodeID: co8-4s88d-worker-j2hmg
  topologyKeys:
  - topology.csi.vmware.com/openshift-zone
  - topology.csi.vmware.com/openshift-region
```

1. vSphere `openshift-zone` 및 `openshift-region` catagories의 토폴로지 키입니다.

참고

`CSINode` 오브젝트는 업데이트된 토폴로지 정보를 수신하는 데 약간의 시간이 걸릴 수 있습니다. 드라이버가 업데이트되면 `CSINode` 오브젝트에 토폴로지 키가 있어야 합니다.

장애 도메인에서 데이터 저장소에 할당할 태그를 생성합니다.

OpenShift Container Platform이 두 개 이상의 장애 도메인을 확장하면 데이터 저장소가 해당 장애 도메인에서 공유되지 않을 수 있습니다. 여기서 PV(영구 볼륨)의 토폴로지 인식 프로비저닝이 유용합니다.

vCenter에서 데이터 저장소 태그를 지정하는 카테고리를 생성합니다. 예를 들면 `openshift-zonal-datastore-cat` 입니다. 카테고리가 OpenShift Container Platform 클러스터에 참여하는 데이터 저장소에 태그를 지정하는 데 고유하게 사용되는 경우 다른 카테고리 이름을 사용할 수 있습니다. 또한 `StoragePod`, `Datastore`, `Folder` 가 생성된 카테고리의 연관 가능한 엔티티로 선택되어 있는지 확인합니다.

vCenter에서 이전에 생성된 카테고리를 사용하는 태그를 생성합니다. 이 예에서는 태그 이름 `openshift-zonal-datastore` 를 사용합니다.

이전에 생성된 태그(이 예에서는 `openshift-zonal-datastore`)를 동적 프로비저닝으로 간주하는 실패 도메인의 각 데이터 저장소에 할당합니다.

참고

카테고리 및 태그에 대해 원하는 모든 이름을 사용할 수 있습니다. 이 예제에서 사용되는 이름은 권장 사항으로 제공됩니다. OpenShift Container Platform 클러스터의 모든 호스트와 공유되는 데이터 저장소만 고유하게 정의하는 태그 및 카테고리가 있는지 확인합니다.

각 실패 도메인의 태그 기반 데이터 저장소를 대상으로 하는 스토리지 정책을 생성합니다.

vCenter의 주 메뉴에서 정책 및 프로필을 클릭합니다.

정책 및 프로필 페이지의 탐색 창에서 VM Storage Policies 를 클릭합니다.

만들기를 클릭합니다.

스토리지 정책의 이름을 입력합니다.

규칙의 경우 태그 배치 규칙을 선택하고 원하는 데이터 저장소를 대상으로 하는 태그 및 카테고리(이 예에서는 `openshift-zonal-datastore` 태그)를 선택합니다.

데이터 저장소는 스토리지 호환성 테이블에 나열됩니다.

새 영역 스토리지 정책을 사용하는 새 스토리지 클래스를 생성합니다.

스토리지 > StorageClass 를 클릭합니다.

StorageClasses 페이지에서 StorageClass 만들기 를 클릭합니다.

이름에 새 스토리지 클래스의 이름을 입력합니다.

Provisioner 에서 csi.vsphere.vmware.com 을 선택합니다.

추가 매개변수 에서 StoragePolicyName 매개변수의 경우 Value 를 이전에 생성한 새 영역 스토리지 정책의 이름으로 설정합니다.

생성 을 클릭합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: zoned-sc
provisioner: csi.vsphere.vmware.com
parameters:
  StoragePolicyName: zoned-storage-policy
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

1. 새 토폴로지 인식 스토리지 클래스 이름입니다.

2. 영역화된 스토리지 정책을 지정합니다.

참고

이전 YAML 파일을 편집하고 아래 명령을 실행하여 스토리지 클래스를 생성할 수도 있습니다.

```shell
oc create -f $FILE
```

추가 리소스

VMware vSphere 태그 문서

#### 6.22.10.5. 결과

토폴로지 인식 스토리지 클래스의 PVC(영구 볼륨 클레임) 및 PV를 생성하는 것은 실제로 영역이므로 Pod 예약 방법에 따라 각 영역에 데이터 저장소를 사용해야 합니다.

```shell-session
$ oc get pv <pv_name> -o yaml
```

```shell-session
...
nodeAffinity:
  required:
    nodeSelectorTerms:
    - matchExpressions:
      - key: topology.csi.vmware.com/openshift-zone
        operator: In
        values:
        - <openshift_zone>
      - key: topology.csi.vmware.com/openshift-region
        operator: In
        values:
        - <openshift_region>
...
peristentVolumeclaimPolicy: Delete
storageClassName: <zoned_storage_class_name>
volumeMode: Filesystem
...
```

1. 2

PV에는 영역 키가 있습니다.

3. PV에서 zoned 스토리지 클래스를 사용하고 있습니다.

#### 6.22.11. vSphere의 최대 스냅샷 수 변경

vSphere CSI(Container Storage Interface)의 볼륨당 기본 최대 스냅샷 수는 3입니다. 볼륨당 최대 32개까지 변경할 수 있습니다.

그러나 스냅샷 최대값을 늘리려면 성능 장단점이 필요하므로 볼륨당 2~3개의 스냅샷만 사용할 수 있습니다.

자세한 VMware 스냅샷 성능 권장 사항은 추가 리소스를 참조하십시오.

사전 요구 사항

관리자 권한으로 클러스터에 액세스합니다.

프로세스

다음 명령을 실행하여 현재 시크릿을 확인합니다.

```shell-session
$ oc -n openshift-cluster-csi-drivers get secret/vsphere-csi-config-secret -o jsonpath='{.data.cloud\.conf}' | base64 -d
```

```shell-session
# Labels with topology values are added dynamically via operator
[Global]
cluster-id = vsphere-01-cwv8p

# Populate VCenters (multi) after here
[VirtualCenter "vcenter.openshift.com"]
insecure-flag           = true
datacenters             = DEVQEdatacenter
password                = "xxxxxxxx"
user                    = "xxxxxxxx@devcluster.openshift.com"
migration-datastore-url = ds:///vmfs/volumes/vsan:52c842f232751e0d-3253aadeac21ca82/
```

이 예에서는 글로벌 최대 스냅샷 수가 구성되지 않았으므로 기본값 3이 적용됩니다.

다음 명령을 실행하여 스냅샷 제한을 변경합니다.

글로벌 스냅샷 제한을 설정합니다.

```shell-session
$ oc patch clustercsidriver/csi.vsphere.vmware.com --type=merge -p '{"spec":{"driverConfig":{"vSphere":{"globalMaxSnapshotsPerBlockVolume": 10}}}}'

clustercsidriver.operator.openshift.io/csi.vsphere.vmware.com patched
```

이 예에서 글로벌 제한이 10(`globalMaxSnapshotsPerBlockVolume` 으로 설정)으로 변경됩니다.

가상 볼륨 스냅샷 제한을 설정합니다.

이 매개변수는 가상 볼륨 데이터 저장소에만 제한을 설정합니다. 가상 볼륨 최대 스냅샷 제한은 전역 제약 조건을 재정의하지만 설정되지 않은 경우 기본값은 글로벌 제한입니다.

```shell-session
$ oc patch clustercsidriver/csi.vsphere.vmware.com --type=merge -p '{"spec":{"driverConfig":{"vSphere":{"granularMaxSnapshotsPerBlockVolumeInVVOL": 5}}}}'
clustercsidriver.operator.openshift.io/csi.vsphere.vmware.com patched
```

이 예에서는 가상 볼륨 제한이 5로 변경되고 있습니다(`granularMaxSnapshotsPerBlockVolumeInVVOL` 을 5)로 설정합니다.

vSAN 스냅샷 제한을 설정합니다.

이 매개변수는 vSAN 데이터 저장소에만 제한을 설정합니다. 설정된 경우 vSAN 최대 스냅샷 제한이 전역 제약 조건을 덮어씁니다. 그러나 설정되지 않은 경우 기본값은 글로벌 제한입니다. vSAN ESA 설정에서 최대 32 값을 설정할 수 있습니다.

```shell-session
$ oc patch clustercsidriver/csi.vsphere.vmware.com --type=merge -p '{"spec":{"driverConfig":{"vSphere":{"granularMaxSnapshotsPerBlockVolumeInVSAN": 7}}}}'
clustercsidriver.operator.openshift.io/csi.vsphere.vmware.com patched
```

이 예에서 vSAN 제한이 7로 변경되었습니다 (`granularMaxSnapshotsPerBlockVolumeInVSAN` 을 7로 설정).

검증

다음 명령을 실행하여 구성 맵에 변경 사항이 반영되었는지 확인합니다.

```shell-session
$ oc -n openshift-cluster-csi-drivers get secret/vsphere-csi-config-secret -o jsonpath='{.data.cloud\.conf}' | base64 -d
```

```shell-session
# Labels with topology values are added dynamically via operator
[Global]
cluster-id = vsphere-01-cwv8p

# Populate VCenters (multi) after here
[VirtualCenter "vcenter.openshift.com"]
insecure-flag           = true
datacenters             = DEVQEdatacenter
password                = "xxxxxxxx"
user                    = "xxxxxxxx@devcluster.openshift.com"
migration-datastore-url = ds:///vmfs/volumes/vsan:52c842f232751e0d-3253aadeac21ca82/

[Snapshot]
global-max-snapshots-per-block-volume = 10
```

1. `global-max-snapshots-per-block-volume` 이 이제 10으로 설정됩니다.

#### 6.22.12. vSphere의 데이터 저장소 간에 CNS 볼륨 마이그레이션

현재 데이터 저장소에서 공간이 부족하거나 고성능 데이터 저장소로 이동하려는 경우 데이터 저장소 간에 VMware vSphere vSphere Cloud Native Storage(CNS) 볼륨을 마이그레이션할 수 있습니다. 이는 첨부된 볼륨과 분리된 볼륨 모두에 적용됩니다.

제한

VMware vSphere 8.0.2 이상이 필요합니다.

한 번에 하나의 볼륨만 마이그레이션할 수 있습니다.

RWX 볼륨은 지원되지 않습니다.

CNS 볼륨은 OpenShift Container Platform 클러스터를 구성하는 모든 호스트와 공유되는 데이터 저장소로만 마이그레이션해야 합니다.

다른 데이터 센터의 다른 데이터 저장소 간에 볼륨을 마이그레이션하는 것은 지원되지 않습니다.

추가 제한 사항

vSphere 8의 경우

데이터 저장소 간에 CNS 볼륨을 마이그레이션하는 방법에 대한 자세한 내용은 vSphere v8.0 설명서를 참조하십시오.

#### 6.22.13. vSphere에서 스토리지 비활성화 및 활성화

클러스터 관리자는 VMware vSphere CSI(Container Storage Interface) 드라이버를 Day 2 작업으로 비활성화하여 vSphere CSI 드라이버가 vSphere 설정과 상호 작용하지 않도록 할 수 있습니다.

#### 6.22.13.1. vSphere에서 스토리지를 비활성화하고 활성화한 결과

vSphere에서 스토리지를 비활성화하고 활성화한 결과는 다음 표에 설명되어 있습니다.

| 비활성화 | 활성화 |
| --- | --- |
| vSphere CSI Driver Operator는 CSI 드라이버를 설치 해제합니다. 스토리지 컨테이너 오케스트레이션(CO)은 정상이어야 합니다. vSphere-problem-detector는 계속 실행 중이지만 경고 또는 이벤트를 내보내지 않고 덜 자주(24시간마다) 검사를 받지 않습니다. 기존 PV(영구 볼륨), PVC(영구 볼륨 클레임) 및 vSphere 스토리지 정책은 모두 변경되지 않습니다. vSphere PV는 새 Pod에서 사용할 수 없습니다. vSphere PV는 기존 Pod의 기존 노드에 영구적으로 마운트되어 연결되어 있습니다. 이러한 Pod는 삭제 후 무기한 유지됩니다. 스토리지 클래스가 제거됨 | * vSphere CSI Driver Operator는 CSI 드라이버를 다시 설치합니다. * 필요한 경우 vSphere CSI Driver Operator는 vSphere 스토리지 정책을 생성합니다. |

#### 6.22.13.2. vSphere에서 스토리지 비활성화 및 활성화

중요

이 절차를 실행하기 전에 이전 " vSphere에서 스토리지 비활성화 및 활성화" 테이블 및 환경에 미치는 영향을 주의 깊게 검토하십시오.

프로세스

vSphere에서 스토리지를 비활성화하거나 활성화하려면 다음을 수행합니다.

Administration > CustomResourceDefinitions 를 클릭합니다.

Name 드롭다운 옆에 있는 CustomResourceDefinitions 페이지에서 "clustercsidriver"를 입력합니다.

CRD ClusterCSIDriver 를 클릭합니다.

Instances 탭을 클릭합니다.

csi.vsphere.vmware.com 을 클릭합니다.

YAML 탭을 클릭합니다.

`spec.managementState` 의 경우 값을 `Removed` 또는 `Managed` 로 변경합니다.

`Removed`: 스토리지가 비활성화됨

`Managed`: 스토리지가 활성화됨

저장 을 클릭합니다.

스토리지를 비활성화하는 경우 드라이버가 제거되었는지 확인합니다.

워크로드 > 포드 를 클릭합니다.

포드 페이지의 이름 필터 상자에 "vmware-vsphere-csi-driver"를 입력합니다.

표시되는 유일한 항목은 Operator입니다. 예: " vmware-vsphere-csi-driver-operator-559b97ffc5-w99fm"

#### 6.22.14. vSphere의 노드당 최대 볼륨 증가

vSphere 버전 8 이상의 경우 노드당 허용된 볼륨 수를 최대 255개로 늘릴 수 있습니다. 그렇지 않으면 기본값은 59로 유지됩니다.

중요

ESXi 8 하이퍼바이저만 포함하는 동종 vSphere 8 환경이 있어야 합니다. 8 이외의 ESXi 버전이 혼합된 이기종 환경은 허용되지 않습니다. 이러한 이기종 환경에서 값을 59보다 크게 설정하면 클러스터가 성능이 저하됩니다.

제한

VMware vSphere 버전 8 이상을 실행 중이어야 합니다.

충분한 노드에서 노드당 최대 볼륨 수를 늘리면 호스트당 2048개의 가상 디스크 제한을 초과할 수 있습니다. 이는 이 제한을 초과하지 않도록 vSphere에 대한 DCRS(Distributed Resource scheduler) 검증이 없기 때문에 발생할 수 있습니다.

중요

노드당 볼륨 증가는 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 기술 프리뷰 기능 지원 범위 를 참조하십시오.

#### 6.22.14.1. vSphere의 노드당 허용되는 최대 볼륨 증가

사전 요구 사항

OpenShift Container Platform 웹 콘솔에 액세스합니다.

cluster-admin 역할을 가진 사용자로 클러스터에 액세스합니다.

VMware vSphere vCenter에 액세스할 수 있습니다.

vCenter에서 `pvscsi Cryostatr256DiskSupportEnabled` 매개변수가 'True'로 설정되어 있는지 확인합니다.

중요

`pvscsi Cryostatr256DiskSupportEnabled` 매개변수를 변경하는 것은 VMware에서 완전히 지원되지 않습니다. 또한 매개변수는 클러스터 전체 옵션입니다.

프로세스

vSphere의 노드당 최대 볼륨 수를 늘리려면 다음 절차를 사용하십시오.

Administration > CustomResourceDefinitions 를 클릭합니다.

Name 드롭다운 옆에 있는 CustomResourceDefinitions 페이지에서 "clustercsidriver"를 입력합니다.

CRD ClusterCSIDriver 를 클릭합니다.

Instances 탭을 클릭합니다.

csi.vsphere.vmware.com 을 클릭합니다.

YAML 탭을 클릭합니다.

`spec.driverConfig.driverType` 매개변수를 `vSphere` 로 설정합니다.

`spec.driverConfig.vSphere.maxAllowedBlockVolumesPerNode` 매개변수를 YAML 파일에 추가하고 다음 샘플 YAML 파일과 같이 노드당 원하는 최대 볼륨 수의 값을 제공합니다.

```yaml
...
spec:
  driverConfig:
    driverType: vSphere
    vSphere:
      maxAllowedBlockVolumesPerNode:
...
```

1. 노드당 최대 볼륨 수에 대해 원하는 값을 입력합니다. 기본값은 59입니다. 최소값은 1이고 최대값은 255입니다.

저장 을 클릭합니다.

#### 6.22.15. 추가 리소스

CSI 볼륨 구성

vSphere 환경에서 VMware 스냅샷을 사용하기 위한 모범 사례

VMware vCenter 문서

### 7.1. 개요

일반 임시 볼륨은 영구 볼륨 및 동적 프로비저닝을 지원하는 모든 스토리지 드라이버에서 제공할 수 있는 임시 볼륨 유형입니다. 일반 임시 볼륨은 스크래치 데이터에 대한 Pod별 디렉터리를 제공하는 `emptyDir` 볼륨과 유사합니다. 일반적으로 프로비저닝 후 비어 있습니다.

일반 임시 볼륨은 Pod 사양에 인라인으로 지정되며 Pod의 라이프사이클을 따릅니다. Pod와 함께 생성 및 삭제됩니다.

일반 임시 볼륨에는 다음과 같은 기능이 있습니다.

스토리지는 로컬 또는 네트워크 연결일 수 있습니다.

볼륨은 Pod를 초과할 수 없는 고정된 크기를 가질 수 있습니다.

드라이버 및 매개변수에 따라 볼륨에 일부 초기 데이터가 있을 수 있습니다.

스냅샷, 복제, 크기 조정, 스토리지 용량 추적을 포함하여 드라이버가 지원하는 경우 볼륨상의 일반적인 작업이 지원됩니다.

참고

일반 임시 볼륨은 오프라인 스냅샷 및 크기 조정을 지원하지 않습니다.

이러한 제한으로 인해 다음 CSI(Container Storage Interface) 드라이버는 일반 임시 볼륨에 대해 다음 기능을 지원하지 않습니다.

Azure Disk CSI 드라이버는 크기 조정을 지원하지 않습니다.

Cinder CSI 드라이버는 스냅샷을 지원하지 않습니다.

### 7.2. 라이프사이클 및 영구 볼륨 클레임

볼륨 클레임의 매개변수는 Pod의 볼륨 소스 내에 허용됩니다. 레이블, 주석 및 PVC(영구 볼륨 클레임)의 전체 필드 세트가 지원됩니다. 이러한 Pod가 생성되면 임시 볼륨 컨트롤러에서 Pod와 동일한 네임스페이스에 있는 일반 임시 볼륨 생성 절차에 표시된 템플릿에서 실제 PVC 오브젝트를 생성하고 Pod가 삭제될 때 PVC가 삭제됩니다. 이렇게 하면 다음 두 가지 방법 중 하나로 볼륨 바인딩 및 프로비저닝이 트리거됩니다.

스토리지 클래스가 즉시 볼륨 바인딩을 사용하는 경우 즉시 실행됩니다.

즉시 바인딩을 사용하면 스케줄러에서 사용 가능한 후 볼륨에 액세스할 수 있는 노드를 선택해야 합니다.

Pod가 노드에 임시로 예약되는 경우(`WaitForFirstConsumervolume` 바인딩 모드).

스케줄러에서 Pod에 적합한 노드를 선택할 수 있으므로 이 볼륨 바인딩 옵션은 일반 임시 볼륨에 권장됩니다.

리소스 소유권 측면에서 일반 임시 스토리지가 있는 Pod는 해당 임시 스토리지를 제공하는 PVC의 소유자입니다. Pod가 삭제되면 Kubernetes 가비지 수집기는 PVC를 삭제합니다. 그러면 스토리지 클래스의 기본 회수 정책은 볼륨을 삭제하는 것이므로 일반적으로 볼륨 삭제를 트리거합니다. retain의 회수 정책과 함께 스토리지 클래스를 사용하여 quasi-ephemeral 로컬 스토리지를 생성할 수 있습니다. 즉, 스토리지가 Pod를 초과하는 경우 볼륨 정리가 별도로 수행되도록 해야 합니다. 이러한 PVC가 존재하는 동안 다른 PVC처럼 사용할 수 있습니다. 특히 볼륨 복제 또는 스냅샷에서 데이터 소스로 참조할 수 있습니다. PVC 오브젝트에는 볼륨의 현재 상태도 있습니다.

추가 리소스

일반 임시 볼륨 생성

### 7.3. 보안

일반 임시 볼륨 기능을 활성화하면 Pod를 생성할 수 있는 사용자가 PVC(영구 볼륨 클레임)도 간접적으로 생성할 수 있습니다. 이 기능은 이러한 사용자에게 직접 PVC를 생성할 수 있는 권한이 없는 경우에도 작동합니다. 클러스터 관리자는 이를 알고 있어야 합니다. 보안 모델에 맞지 않는 경우 일반 임시 볼륨이 있는 Pod와 같은 오브젝트를 거부하는 승인 Webhook를 사용합니다.

PVC에 대한 일반 네임스페이스 할당량은 계속 적용되므로 사용자가 이 새 메커니즘을 사용할 수 있더라도 다른 정책을 우회하는 데 사용할 수 없습니다.

### 7.4. 영구 볼륨 클레임 이름 지정

자동으로 생성된 PVC(영구 볼륨 클레임)는 Pod 이름과 볼륨 이름을 조합하여 중간에서 하이픈(-)으로 이름이 지정됩니다. 이 이름 지정 규칙은 다른 Pod와 Pod 간 및 수동으로 생성된 PVC 간에 충돌이 발생할 수 있습니다.

예를 들어, 볼륨 `scratch` 가 있는 `pod-a` 와 볼륨 `a-scratch` 가 있는 `pod` 는 모두 동일한 PVC 이름인 `pod-a-scratch` 로 끝납니다.

이러한 충돌이 감지되고 PVC는 Pod용으로 생성된 경우에만 임시 볼륨에 사용됩니다. 이 검사는 소유권 관계를 기반으로 합니다. 기존 PVC는 덮어쓰거나 수정되지 않지만 충돌을 해결하지는 않습니다. 올바른 PVC가 없으면 Pod를 시작할 수 없습니다.

중요

이름 충돌이 발생하지 않도록 동일한 네임스페이스 내에서 Pod 및 볼륨 이름을 지정할 때는 주의하십시오.

### 7.5. 일반 임시 볼륨 생성

프로세스

`Pod` 오브젝트 정의를 생성하여 파일에 저장합니다.

파일에 일반 임시 볼륨 정보를 포함합니다.

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: my-app
spec:
  containers:
    - name: my-frontend
      image: busybox:1.28
      volumeMounts:
      - mountPath: "/mnt/storage"
        name: data
      command: [ "sleep", "1000000" ]
  volumes:
    - name: data
      ephemeral:
        volumeClaimTemplate:
          metadata:
            labels:
              type: my-app-ephvol
          spec:
            accessModes: [ "ReadWriteOnce" ]
            storageClassName: "gp2-csi"
            resources:
              requests:
                storage: 1Gi
```

1. 일반 임시 볼륨 클레임.

### 8.1. 볼륨 확장 지원 활성화

영구 볼륨을 확장하려면 `StorageClass` 오브젝트에서 `allowVolumeExpansion` 필드가 `true` 로 설정되어 있어야 합니다.

프로세스

`StorageClass` 오브젝트를 편집하고 다음 명령을 실행하여 `allowVolumeExpansion` 속성을 추가합니다.

```shell-session
$ oc edit storageclass <storage_class_name>
```

1. 스토리지 클래스의 이름을 지정합니다.

다음 예시는 스토리지 클래스 구성 하단에 이 행을 추가하는 방법을 보여줍니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
...
parameters:
  type: gp2
reclaimPolicy: Delete
allowVolumeExpansion: true
```

1. 이 속성을 `true` 로 설정하면 생성 후 PVC가 확장됩니다.

### 8.2. CSI 볼륨 확장

CSI(Container Storage Interface)를 사용하여 이미 생성된 스토리지 볼륨을 확장할 수 있습니다.

PV(영구 볼륨) 축소는 지원되지 않습니다.

사전 요구 사항

기본 CSI 드라이버는 크기 조정을 지원합니다. "추가 리소스" 섹션의 "OpenShift Container Platform에서 지원하는 CSI 드라이버"를 참조하십시오.

동적 프로비저닝이 사용됩니다.

제어 `StorageClass` 오브젝트에 `allowVolumeExpansion` 이 `true` 로 설정되어 있습니다. 자세한 내용은 " 볼륨 확장 지원 활성화"를 참조하십시오.

프로세스

PVC(영구 볼륨 클레임)의 경우 `.spec.resources.requests.storage` 를 원하는 새 크기로 설정합니다.

PVC의 `status.conditions` 필드를 확인하여 크기 조정이 완료되었는지 확인합니다. OpenShift Container Platform은 확장 중에 PVC에 `Resizing` 조건을 추가합니다. 확장이 완료된 후 제거됩니다.

### 8.3. 지원되는 드라이버를 사용한 FlexVolume 확장

FlexVolume을 사용하여 백엔드 스토리지 시스템에 연결할 때 이미 생성된 후 영구 스토리지 볼륨을 확장할 수 있습니다. OpenShift Container Platform에서 PVC(영구 볼륨 클레임)를 수동으로 업데이트하여 수행합니다.

FlexVolume은 `RequiresFSResize` 가 `true` 로 설정된 경우 확장을 허용합니다. Pod를 다시 시작할 때 FlexVolume을 확장할 수 있습니다.

다른 볼륨 유형과 유사하게 Pod에서 사용할 때 FlexVolume 볼륨도 확장할 수 있습니다.

사전 요구 사항

기본 볼륨 드라이버는 크기 조정을 지원합니다.

드라이버에서는 `RequiresFSResize` 기능이 `true` 로 설정됩니다.

동적 프로비저닝이 사용됩니다.

제어 `StorageClass` 오브젝트에 `allowVolumeExpansion` 이 `true` 로 설정되어 있습니다.

절차

FlexVolume 플러그인에서 크기 조정을 사용하려면 다음 방법을 사용하여 `ExpandableVolumePlugin` 인터페이스를 구현해야 합니다.

`RequiresFSResize`

`true` 인 경우 용량을 직접 업데이트합니다. `false` 인 경우 `ExpandFS` 메서드를 호출하여 파일 시스템의 크기 조정을 완료합니다.

`ExpandFS`

`true` 인 경우 `ExpandFS` 를 호출하여 물리 볼륨 확장을 수행한 후 파일 시스템의 크기를 조정합니다. 볼륨 드라이버는 파일 시스템의 크기 조정과 함께 물리 볼륨 크기 조정을 수행할 수도 있습니다.

중요

OpenShift Container Platform은 컨트롤 플레인 노드에 FlexVolume 플러그인 설치를 지원하지 않으므로 FlexVolume의 컨트롤 플레인 확장을 지원하지 않습니다.

### 8.4. 로컬 볼륨 확장

로컬 스토리지 Operator(LSO)를 사용하여 생성된 PV(영구 볼륨) 및 PVC(영구 볼륨 클레임)를 수동으로 확장할 수 있습니다.

프로세스

기본 장치를 확장합니다. 이러한 장치에서 적절한 용량을 사용할 수 있는지 확인합니다.

PV의 `.spec.capacity` 필드를 편집하여 새 장치 크기와 일치하도록 해당 PV 오브젝트를 업데이트합니다.

PVC를 PVet에 바인딩하는 데 사용되는 스토리지 클래스의 경우 `allowVolumeExpansion:true` 를 설정합니다.

PVC의 경우 새 크기와 일치하도록 `.spec.resources.requests.storage` 를 설정합니다.

kubelet은 필요한 경우 볼륨에서 기본 파일 시스템을 자동으로 확장하고 새 크기를 반영하도록 PVC의 상태 필드를 업데이트해야 합니다.

### 8.5. 파일 시스템을 사용한 PVC(영구 볼륨 클레임) 처리

GCE, EBS 및 Cinder와 같이 파일 시스템 크기 조정이 필요한 볼륨 유형에 따라 PVC를 확장하는 것은 2단계 프로세스입니다. 먼저 클라우드 공급자의 볼륨 오브젝트를 확장합니다. 두 번째는 노드의 파일 시스템을 확장합니다.

노드의 파일 시스템을 배양하는 것은 볼륨으로 새 Pod가 시작될 때만 수행됩니다.

사전 요구 사항

제어 `StorageClass` 오브젝트에서 `allowVolumeExpansion` 이 `true` 로 설정되어야 합니다.

절차

PVC를 편집하고 `spec.resources.requests` 를 편집하여 새 크기를 요청합니다. 예를 들어 다음은 `ebs` PVC를 8Gi로 확장합니다.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: ebs
spec:
  storageClass: "storageClassWithFlagSet"
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 8Gi
```

1. `spec.resources.requests` 를 더 큰 용량으로 업데이트하면 PVC가 확장됩니다.

클라우드 공급자 오브젝트 크기 조정이 완료되면 PVC가 `FileSystemResizePending` 로 설정됩니다. 다음 명령을 입력하여 조건을 확인합니다.

```shell-session
$ oc describe pvc <pvc_name>
```

클라우드 공급자 오브젝트 크기 조정이 완료되면 `PersistentVolume` 오브젝트가 `PersistentVolume.Spec.Capacity` 의 새로 요청된 크기를 반영합니다. 이 시점에서 PVC에서 새 Pod를 생성하거나 재생성하여 파일 시스템 크기 조정을 완료할 수 있습니다. Pod가 실행되면 새로 요청된 크기를 사용할 수 있으며, `FileSystemResizePending` 조건이 PVC에서 제거됩니다.

### 8.6. 볼륨을 분리할 때 실패에서 복구

크기 조정 요청이 실패하거나 보류 중인 상태로 남아 있는 경우 PVC(영구 볼륨 클레임)에 대해 `.spec.resources.requests.storage` 에 다른 크기 조정 값을 입력하여 다시 시도할 수 있습니다. 새 값은 원래 볼륨 크기보다 커야 합니다.

여전히 문제가 있는 경우 다음 절차를 사용하여 복구하십시오.

프로세스

PVC에 대해 `.spec.resources.requests.storage` 에 작은 크기 조정 값을 입력하는 경우 다음을 수행합니다.

PVC에 바인딩된 PV(영구 볼륨)를 `Retain` 회수 정책으로 표시합니다. `persistentVolumeReclaimPolicy` 를 `Retain` 으로 변경합니다.

PVC를 삭제합니다.

PV를 수동으로 편집하고 PV 사양에서 `claimRef` 항목을 삭제하여 새로 생성된 PVC가 `Retain` 이라는 PV에 바인딩할 수 있는지 확인합니다. PV가 `Available` 로 표시됩니다.

PVC를 작은 크기로 다시 생성하거나 기본 스토리지 공급자가 할당할 수 있는 크기입니다.

PVC의 `volumeName` 필드를 PV 이름으로 설정합니다. 이렇게 하면 PVC가 프로비저닝된 PV에만 바인딩됩니다.

PV에서 회수 정책을 복구합니다.

### 8.7. 추가 리소스

볼륨 확장 지원 활성화

OpenShift Container Platform에서 지원되는 CSI 드라이버

### 9.1. 동적 프로비저닝 소개

`StorageClass` 리소스 객체는 요청 가능한 스토리지를 설명하고 분류할 뿐 만 아니라 필요에 따라 동적으로 프로비저닝된 스토리지에 대한 매개 변수를 전달하는 수단을 제공합니다. `StorageClass` 객체는 다른 수준의 스토리지 및 스토리지에 대한 액세스를 제어하기 위한 관리 메커니즘으로 사용될 수 있습니다. 클러스터 관리자 (`cluster-admin`) 또는 스토리지 관리자 (`storage-admin`)는 사용자가 기본 스토리지 볼륨 소스에 대한 자세한 지식이 없어도 요청할 수 있는 `StorageClass` 오브젝트를 정의하고 생성할 수 있습니다.

OpenShift Container Platform 영구 볼륨 프레임 워크를 사용하면이 기능을 사용할 수 있으며 관리자는 영구 스토리지로 클러스터를 프로비저닝할 수 있습니다. 또한 이 프레임 워크를 통해 사용자는 기본 인프라에 대한 지식이 없어도 해당 리소스를 요청할 수 있습니다.

OpenShift Container Platform에서 많은 스토리지 유형을 영구 볼륨으로 사용할 수 있습니다. 관리자가 정적으로 프로비저닝할 수 있지만 일부 스토리지 유형은 기본 제공 공급자 및 플러그인 API를 사용하여 동적으로 생성됩니다.

### 9.2. 사용 가능한 동적 프로비저닝 플러그인

OpenShift Container Platform은 다음 프로비저너 플러그인을 제공합니다. 이 플러그인에는 클러스터의 구성된 공급자의 API를 사용하여 새 스토리지 리소스를 생성하는 동적 프로비저닝을 위한 일반적인 구현이 있습니다.

| 스토리지 유형 | 프로비저너 플러그인 이름 | 참고 |
| --- | --- | --- |
| Red Hat OpenStack Platform (RHOSP) Cinder | `kubernetes.io/cinder` |  |
| RHOSP Manila Container Storage Interface (CSI) | `manila.csi.openstack.org` | 설치 완료되면 OpenStack Manila CSI Driver Operator 및 ManilaDriver가 동적 프로비저닝에 필요한 모든 사용 가능한 Manila 공유 유형에 필요한 스토리지 클래스를 자동으로 생성합니다. |
| Amazon Elastic Block Store(Amazon EBS) | `ebs.csi.aws.com` | 다른 영역에서 여러 클러스터를 사용할 때 동적 프로비저닝의 경우 각 노드에 `Key=kubernetes.io/cluster/<cluster_name>,Value=<cluster_id>` 로 태그를 지정합니다. 여기서 `<cluster_name>` 및 `<cluster_id>` 는 클러스터마다 고유합니다. |
| Azure Disk | `kubernetes.io/azure-disk` |  |
| Azure File | `kubernetes.io/azure-file` | `persistent-volume-binder` 서비스 계정에는 Azure 스토리지 계정 및 키를 저장할 시크릿을 생성하고 검색할 수 있는 권한이 필요합니다. |
| GCE Persistent Disk (gcePD) | `kubernetes.io/gce-pd` | 멀티 존 설정에서는 현재 클러스터에 노드가 없는 영역에서 PV가 생성되지 않도록 GCE 프로젝트 당 하나의 OpenShift Container Platform 클러스터를 실행하는 것이 좋습니다. |
| IBM Power® Virtual Server Block | `powervs.csi.ibm.com` | 설치 후 IBM Power® Virtual Server Block CSI Driver Operator 및 IBM Power® Virtual Server Block CSI Driver가 동적 프로비저닝에 필요한 스토리지 클래스를 자동으로 생성합니다. |
| VMware vSphere | `kubernetes.io/vsphere-volume` |  |

중요

선택한 프로비저너 플러그인에는 관련 문서에 따라 클라우드, 호스트 또는 타사 공급자를 구성해야 합니다.

### 9.3. 스토리지 클래스 정의

`StorageClass` 객체는 현재 전역 범위 객체이며 `cluster-admin` 또는 `storage-admin` 사용자가 만들어야 합니다.

중요

클러스터 스토리지 작업자는 사용 중인 플랫폼에 따라 기본 스토리지 클래스를 설치할 수 있습니다. 이 스토리지 클래스는 Operator가 소유하고 제어합니다. 주석 및 레이블 정의 외에는 삭제하거나 변경할 수 없습니다. 다른 동작이 필요한 경우 사용자 정의 스토리지 클래스를 정의해야 합니다.

다음 섹션에서는 `StorageClass` 오브젝트의 기본 정의 및 지원되는 각 플러그인 유형에 대한 구체적인 예를 설명합니다.

#### 9.3.1. 기본 StorageClass 개체 정의

다음 리소스는 스토리지 클래스를 구성하는 데 사용되는 매개변수 및 기본값을 보여줍니다. 이 예에서는 AWS ElasticBlockStore (EBS) 객체 정의를 사용합니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: <storage-class-name>
  annotations:
    storageclass.kubernetes.io/is-default-class: 'true'
    ...
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
...
```

1. (필수) API 객체 유형입니다.

2. (필수) 현재 apiVersion입니다.

3. (필수) 스토리지 클래스의 이름입니다.

4. (선택 사항) 스토리지 클래스의 주석입니다.

5. (필수) 이 스토리지 클래스에 연결된 프로비저너의 유형입니다.

6. (선택 사항) 특정 프로비저너에 필요한 매개 변수로, 플러그인에 따라 변경됩니다.

#### 9.3.2. 스토리지 클래스 주석

스토리지 클래스를 클러스터 전체 기본값으로 설정하려면 스토리지 클래스의 메타데이터에 다음 주석을 추가합니다.

```yaml
storageclass.kubernetes.io/is-default-class: "true"
```

예를 들면 다음과 같습니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
...
```

이렇게 하면 특정 스토리지 클래스를 지정하지 않은 모든 PVC(영구 볼륨 클레임)가 기본 스토리지 클래스를 통해 자동으로 프로비저닝됩니다. 그러나 클러스터에는 두 개 이상의 스토리지 클래스가 있을 수 있지만, 이 중 하나만 기본 스토리지 클래스일 수 있습니다.

참고

베타 주석 `storageclass.beta.kubernetes.io/is-default-class` 는 여전히 작동하지만 향후 릴리스에서는 제거될 예정입니다.

스토리지 클래스 설명을 설정하려면 스토리지 클래스의 메타데이터에 다음 주석을 추가합니다.

```yaml
kubernetes.io/description: My Storage Class Description
```

예를 들면 다음과 같습니다.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  annotations:
    kubernetes.io/description: My Storage Class Description
...
```

#### 9.3.3. RHOSP Cinder 오브젝트 정의

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: <storage-class-name>
provisioner: kubernetes.io/cinder
parameters:
  type: fast
  availability: nova
  fsType: ext4
```

1. StorageClass의 이름입니다. 영구 볼륨 클래임은 이 스토리지 클래스를 사용하여 관련 영구 볼륨을 프로비저닝합니다.

2. Cinder에서 생성 된 볼륨 유형입니다. 기본값은 비어 있습니다.

3. 가용성 영역입니다. 지정하지 않으면 일반적으로 OpenShift Container Platform 클러스터에 노드가 있는 모든 활성 영역에서 볼륨이 라운드 로빈됩니다.

4. 동적으로 프로비저닝된 볼륨에서 생성된 파일 시스템입니다. 이 값은 동적으로 프로비저닝된 영구 볼륨의 `fsType` 필드에 복사되며 볼륨이 처음 마운트될 때 파일 시스템이 작성됩니다. 기본값은 `ext4` 입니다.

#### 9.3.4. RHOSP Manila CSI(Container Storage Interface) 오브젝트 정의

설치 완료되면 OpenStack Manila CSI Driver Operator 및 ManilaDriver가 동적 프로비저닝에 필요한 모든 사용 가능한 Manila 공유 유형에 필요한 스토리지 클래스를 자동으로 생성합니다.

#### 9.3.5. AWS Elastic Block Store (EBS) 객체 정의

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: <storage-class-name>
provisioner: ebs.csi.aws.com
parameters:
  type: io1
  iopsPerGB: "10"
  encrypted: "true"
  kmsKeyId: keyvalue
  fsType: ext4
```

1. (필수) 스토리지 클래스의 이름입니다. 영구 볼륨 클래임은 이 스토리지 클래스를 사용하여 관련 영구 볼륨을 프로비저닝합니다.

2. (필수) `io1`, `gp3`, `sc1`, `st1` 에서 선택합니다. 기본값은 `gp3` 입니다. 유효한 Amazon Resource Name (ARN) 값은 AWS 설명서 를 참조하십시오.

3. 선택 사항: io1 볼륨만 해당합니다. GiB마다 초당 I/O 작업 수입니다. AWS 볼륨 플러그인은 요청된 볼륨 크기와 멀티플로우하여 볼륨의 IOPS를 계산합니다. 값의 상한은 AWS가 지원하는 최대치인 20,000 IOPS입니다. 자세한 내용은 AWS 설명서 를 참조하십시오.

4. 선택 사항: EBS 볼륨을 암호화할지 여부를 나타냅니다. 유효한 값은 `true` 또는 `false` 입니다.

5. 선택 사항: 볼륨을 암호화할 때 사용할 키의 전체 ARN입니다. 값을 지정하지 않는 경우에도 `encypted` 가 `true` 로 설정되어 있는 경우 AWS가 키를 생성합니다. 유효한 ARN 값은 AWS 설명서 를 참조하십시오.

6. 선택 사항: 동적으로 프로비저닝된 볼륨에서 생성된 파일 시스템입니다. 이 값은 동적으로 프로비저닝된 영구 볼륨의 `fsType` 필드에 복사되며 볼륨이 처음 마운트될 때 파일 시스템이 작성됩니다. 기본값은 `ext4` 입니다.

#### 9.3.6. Azure Disk 오브젝트 정의

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <storage-class-name>
provisioner: kubernetes.io/azure-disk
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
parameters:
  kind: Managed
  storageaccounttype: Premium_LRS
reclaimPolicy: Delete
```

1. StorageClass의 이름입니다. 영구 볼륨 클래임은 이 스토리지 클래스를 사용하여 관련 영구 볼륨을 프로비저닝합니다.

2. `WaitForFirstConsumer` 를 사용하는 것이 좋습니다. 이렇게 하면 볼륨을 프로비저닝하고 사용 가능한 영역에서 사용 가능한 작업자 노드의 Pod를 예약할 수 있는 충분한 스토리지를 허용합니다.

3. 가능한 값은 `Shared` (기본값), `Managed`, `Dedicated` 입니다.

중요

Red Hat은 스토리지 클래스에서 `kind: Managed` 의 사용만 지원합니다.

`Shared` 및 `Dedicated` 를 사용하여 Azure는 관리되지 않은 디스크를 생성합니다. 반면 OpenShift Container Platform은 머신 OS(root) 디스크의 관리 디스크를 생성합니다. Azure Disk는 노드에서 관리 및 관리되지 않은 디스크를 모두 사용하도록 허용하지 않으므로 `Shared` 또는 `Dedicated` 로 생성된 관리되지 않은 디스크를 OpenShift Container Platform 노드에 연결할 수 없습니다.

4. Azure 스토리지 계정 SKU층입니다. 기본값은 비어 있습니다. 프리미엄 VM은 `Standard_LRS` 및 `Premium_LRS` 디스크를 모두 연결할 수 있으며 표준 VM은 `Standard_LRS` 디스크만 연결할 수 있습니다. 관리형 VM은 관리 디스크만 연결할 수 있으며 관리되지 않는 VM은 관리되지 않는 디스크만 연결할 수 있습니다.

`kind` 가 `Shared` 로 설정된 경우 Azure는 클러스터와 동일한 리소스 그룹에 있는 일부 공유 스토리지 계정에서 관리되지 않는 디스크를 만듭니다.

`kind` 가 `Managed` 로 설정된 경우 Azure는 새 관리 디스크를 만듭니다.

`kind` 가 `Dedicated` 로 설정되고 `storageAccount` 가 지정된 경우 Azure는 클러스터와 동일한 리소스 그룹에서 새로운 관리되지 않는 디스크에 대해 지정된 스토리지 계정을 사용합니다. 이 기능이 작동하려면 다음 사항이 전제가 되어야 합니다.

지정된 스토리지 계정이 같은 지역에 있어야 합니다.

Azure Cloud Provider는 스토리지 계정에 대한 쓰기 권한이 있어야 합니다.

`kind` 가 `Dedicated` 로 설정되어 있고 `storageAccount` 가 지정되지 않은 경우 Azure는 클러스터와 동일한 리소스 그룹에 새로운 관리되지 않는 디스크에 대한 새로운 전용 스토리지 계정을 만듭니다.

#### 9.3.7. Azure File 객체 정의

Azure File 스토리지 클래스는 시크릿을 사용하여 Azure 파일 공유를 만드는 데 필요한 Azure 스토리지 계정 이름과 스토리지 계정 키를 저장합니다. 이러한 권한은 다음 절차의 일부로 생성됩니다.

절차

시크릿을 작성하고 볼 수 있는 액세스를 허용하는 `ClusterRole` 오브젝트를 정의합니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
#  name: system:azure-cloud-provider
  name: <persistent-volume-binder-role>
rules:
- apiGroups: ['']
  resources: ['secrets']
  verbs:     ['get','create']
```

1. 시크릿을 표시하고 작성하는 클러스터 역할의 이름입니다.

서비스 계정에 클러스터 역할을 추가합니다.

```shell-session
$ oc adm policy add-cluster-role-to-user <persistent-volume-binder-role> system:serviceaccount:kube-system:persistent-volume-binder
```

Azure File `StorageClass` 오브젝트를 만듭니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: <azure-file>
provisioner: kubernetes.io/azure-file
parameters:
  location: eastus
  skuName: Standard_LRS
  storageAccount: <storage-account>
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

1. StorageClass의 이름입니다. 영구 볼륨 클래임은 이 스토리지 클래스를 사용하여 관련 영구 볼륨을 프로비저닝합니다.

2. `eastus` 와 같은 Azure 스토리지 계정의 위치입니다. 기본값은 비어 있습니다. 즉, OpenShift Container Platform 클러스터 위치에 새 Azure 스토리지 계정이 만들어집니다.

3. Azure 스토리지 계정의 SKU 계층입니다 (예: `Standard_LRS)`. 기본값은 비어 있습니다. 즉, `Standard_LRS` SKU를 사용하여 새 Azure 스토리지 계정이 만들어집니다.

4. Azure 스토리지 계정 이름입니다. 스토리지 계정이 제공되면 `skuName` 및 `location` 이 무시됩니다. 스토리지 계정이 제공되지 않으면 스토리지 클래스는 정의된 `skuName` 및 `location` 과 일치하는 계정의 리소스 그룹과 연관된 스토리지 계정을 검색합니다.

#### 9.3.7.1. Azure File 사용시 고려 사항

기본 Azure File 스토리지 클래스는 다음 파일 시스템 기능을 지원하지 않습니다.

심볼릭 링크

하드 링크

확장 속성

스파스 파일

명명된 파이프

또한 Azure File이 마운트되는 디렉터리의 소유자 ID (UID)는 컨테이너의 프로세스 UID와 다릅니다. 마운트된 디렉터리에 사용할 특정 사용자 ID를 정의하기 위해 `StorageClass` 오브젝트에서 `uid` 마운트 옵션을 지정할 수 있습니다.

다음 `StorageClass` 오브젝트는 마운트된 디렉터리의 심볼릭 링크를 활성화한 상태에서 사용자 및 그룹 ID를 변경하는 방법을 보여줍니다.

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: azure-file
mountOptions:
  - uid=1500
  - gid=1500
  - mfsymlinks
provisioner: kubernetes.io/azure-file
parameters:
  location: eastus
  skuName: Standard_LRS
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

1. 마운트된 디렉터리에 사용할 사용자 ID를 지정합니다.

2. 마운트된 디렉터리에 사용할 그룹 ID를 지정합니다.

3. 심볼릭 링크를 활성화합니다.

#### 9.3.8. GCE PersistentDisk (gcePD) 오브젝트 정의

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: <storage-class-name>
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: none
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
```

1. StorageClass의 이름입니다. 영구 볼륨 클래임은 이 스토리지 클래스를 사용하여 관련 영구 볼륨을 프로비저닝합니다.

2. `pd-ssd`, `pd-standard` 또는 `hyperdisk-balanced` 를 선택합니다. 기본값은 `pd-ssd` 입니다.

#### 9.3.9. VMware vSphere 개체 정의

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: <storage-class-name>
provisioner: csi.vsphere.vmware.com
```

1. StorageClass의 이름입니다. 영구 볼륨 클래임은 이 스토리지 클래스를 사용하여 관련 영구 볼륨을 프로비저닝합니다.

2. OpenShift Container Platform에서 VMware vSphere CSI를 사용하는 방법에 대한 자세한 내용은 Kubernetes 설명서 를 참조하십시오.

### 9.4. 기본 스토리지 클래스 변경

다음 절차에 따라 기본 스토리지 클래스를 변경합니다.

예를 들어 두 개의 스토리지 클래스인 `gp3` 및 `standard` 가 있고 기본 스토리지 클래스를 `gp3` 에서 `standard` 로 변경하려는 경우.

사전 요구 사항

cluster-admin 권한으로 클러스터에 액세스합니다.

프로세스

기본 스토리지 클래스를 변경하려면 다음을 수행합니다.

스토리지 클래스를 나열합니다.

```shell-session
$ oc get storageclass
```

```shell-session
NAME                 TYPE
gp3 (default)        ebs.csi.aws.com
standard             ebs.csi.aws.com
```

1. `(default)` 는 기본 스토리지 클래스를 나타냅니다.

원하는 스토리지 클래스를 기본값으로 설정합니다.

원하는 스토리지 클래스의 경우 다음 명령을 실행하여 `storageclass.kubernetes.io/is-default-class` 주석을 `true` 로 설정합니다.

```shell-session
$ oc patch storageclass standard -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'
```

참고

짧은 시간 동안 여러 기본 스토리지 클래스를 사용할 수 있습니다. 그러나 결국 하나의 기본 스토리지 클래스만 존재하는지 확인해야 합니다.

여러 기본 스토리지 클래스가 있는 경우 기본 스토리지 클래스 `pvc.spec.storageClassName` =nil)를 요청하는 모든 영구 볼륨 클레임(PVC)은 해당 스토리지 클래스의 기본 상태와 관계없이 가장 최근에 생성된 기본 스토리지 클래스를 가져옵니다. 경고 대시보드에서 여러 기본 스토리지 클래스인 `MultipleDefaultStorageClasses` 가 있다는 경고를 받습니다.

이전 기본 스토리지 클래스에서 기본 스토리지 클래스 설정을 제거합니다.

이전 기본 스토리지 클래스의 경우 다음 명령을 실행하여 `storageclass.kubernetes.io/is-default-class` 주석의 값을 `false` 로 변경합니다.

```shell-session
$ oc patch storageclass gp3 -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "false"}}}'
```

변경 사항을 확인합니다.

```shell-session
$ oc get storageclass
```

```shell-session
NAME                 TYPE
gp3                  ebs.csi.aws.com
standard (default)   ebs.csi.aws.com
```

## 10장. 비정상적인 노드 종료 후 볼륨 분리

이 기능을 사용하면 노드가 비정상적으로 중단될 때 드라이버가 볼륨을 자동으로 분리할 수 있습니다.

### 10.1. 개요

kubelet의 노드 종료 관리자가 예정된 노드 종료 작업을 감지하면 정상 노드 종료가 발생합니다. 비정상적인 종료는 kubelet에서 노드 종료 작업을 감지하지 못하면 시스템 또는 하드웨어 오류로 인해 발생할 수 있습니다. 또한 shutdown 명령이 Linux에서 kubelet에서 사용하는 Inhibitor Locks 메커니즘을 트리거하지 않거나 예를 들어 shutdownGracePerioiod 및 shutdownGracePeriodCriticalPods 세부 정보가 올바르게 구성되지 않은 경우 kubelet에서 노드 종료 작업을 감지하지 못할 수 있습니다.

이 기능을 사용하면 비정상적인 노드 종료가 발생하면 노드에서 볼륨이 자동으로 분리될 수 있도록 노드에 `out-of-service` 테인트를 수동으로 추가할 수 있습니다.

### 10.2. 자동 볼륨 분리를 위해 서비스 외부 테인트 추가

사전 요구 사항

cluster-admin 권한으로 클러스터에 액세스합니다.

프로세스

비정상적인 노드 종료 후 노드에서 볼륨을 자동으로 분리할 수 있도록 하려면 다음을 수행합니다.

노드가 비정상으로 감지되면 작업자 노드를 종료합니다.

다음 명령을 실행하고 상태를 확인하여 노드가 종료되었는지 확인합니다.

```shell-session
$ oc get node <node_name>
```

1. <NODE_NAME> = 무중하게 종료되는 노드의 이름

중요

노드가 완전히 종료되지 않으면 노드에 테인트를 진행하지 마십시오. 노드가 계속 작동 중이고 테인트가 적용되면 파일 시스템 손상이 발생할 수 있습니다.

다음 명령을 실행하여 해당 노드 오브젝트를 테인트합니다.

중요

이렇게 하면 노드를 테인트하면 해당 노드의 모든 Pod가 삭제됩니다. 이로 인해 상태 저장 세트에서 지원하는 모든 Pod가 제거되고 다른 노드에서 Pod 교체도 생성됩니다.

```shell-session
$ oc adm taint node <node_name> node.kubernetes.io/out-of-service=nodeshutdown:NoExecute
```

1. <NODE_NAME> = 무중하게 종료되는 노드의 이름

테인트를 적용한 후 볼륨이 종료 노드에서 분리되므로 디스크를 다른 노드에 연결할 수 있습니다.

예제

결과 YAML 파일은 다음과 유사합니다.

```yaml
spec:
  taints:
  - effect: NoExecute
    key: node.kubernetes.io/out-of-service
    value: nodeshutdown
```

노드를 재시작합니다.

다음 명령을 실행하여 해당 노드 오브젝트에서 테인트를 제거합니다.

```shell-session
$ oc adm taint node <node_name> node.kubernetes.io/out-of-service=nodeshutdown:NoExecute-
```

1. <NODE_NAME> = 무중하게 종료되는 노드의 이름
