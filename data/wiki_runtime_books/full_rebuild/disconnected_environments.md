# 연결이 끊긴 환경

## 연결이 끊긴 환경에서 OpenShift Container Platform 클러스터 관리

이 문서에서는 인터넷 액세스가 없는 환경에서 OpenShift Container Platform 클러스터를 설치, 관리 및 구성하는 방법에 대해 설명합니다.

## 1장. 연결이 끊긴 환경 정보

연결이 끊긴 환경은 인터넷에 대한 전체 액세스 권한이 없는 환경입니다.

OpenShift Container Platform은 레지스트리에서 릴리스 이미지 검색 또는 업데이트 경로 검색 및 클러스터 권장 사항과 같은 인터넷 연결을 사용하는 많은 자동 기능을 수행하도록 설계되었습니다. 인터넷에 직접 연결하지 않으면 연결이 끊긴 환경에서 전체 기능을 유지하기 위해 클러스터에 대한 추가 설정 및 구성을 수행해야 합니다.

### 1.1. 연결이 끊긴 환경 용어집

OpenShift Container Platform 설명서 전체에서 사용되지만 연결이 끊긴 환경은 다양한 수준의 인터넷 연결이 있는 환경을 참조할 수 있는 광범위한 용어입니다. 다른 용어는 특정 수준의 인터넷 연결을 참조하는 데 사용되는 경우가 있으며 이러한 환경에는 추가 고유 구성이 필요할 수 있습니다.

다음 표에서는 전체 인터넷 연결이 없는 환경을 참조하는 데 사용되는 다양한 용어를 설명합니다.

| 용어 | 설명 |
| --- | --- |
| Air-gapped 네트워크 | 외부 네트워크와 완전히 격리된 환경 또는 네트워크입니다. 이러한 격리는 내부 네트워크의 시스템과 외부 네트워크의 다른 부분 간의 물리적 분리 또는 "어두운"에 따라 달라집니다. Air-gapped 환경은 엄격한 보안 또는 규제 요구 사항이 있는 업계에서 자주 사용됩니다. |
| 연결이 끊긴 환경 | 외부 네트워크에서 어느 정도 격리할 수 있는 환경 또는 네트워크입니다. 이러한 격리는 내부 네트워크의 시스템과 외부 네트워크의 시스템을 물리적 또는 논리적 분리하여 활성화할 수 있습니다. 외부 네트워크와의 격리 수준에 관계없이 연결이 끊긴 환경의 클러스터는 Red Hat에서 호스팅하는 공용 서비스에 액세스할 수 없으며 전체 클러스터 기능을 유지하기 위해 추가 설정이 필요합니다. |
| 제한된 네트워크 | 외부 네트워크에 대한 연결이 제한된 환경 또는 네트워크입니다. 내부 네트워크와 외부 네트워크의 시스템 간에 물리적 연결이 존재할 수 있지만 네트워크 트래픽은 방화벽 및 프록시와 같은 추가 구성에 의해 제한됩니다. |

### 1.2. 연결이 끊긴 환경 작업을 위한 기본 방법

연결이 끊긴 환경에서 클러스터 관리의 대부분의 측면에 대해 여러 옵션 중에서 선택할 수 있습니다. 예를 들어 이미지를 미러링할 때 oc-mirror OpenShift CLI() 플러그인을 사용하거나 아래 명령을 사용하여 선택할 수 있습니다.

```shell
oc
```

```shell
oc adm
```

그러나 일부 옵션은 연결이 끊긴 환경에 대해 더 간단하고 편리한 사용자 환경을 제공하며 대안보다 선호되는 방법입니다.

조직에서 다른 옵션을 선택해야 하는 경우가 아니면 다음 방법을 사용하여 이미지를 미러링하고 클러스터를 설치하고 클러스터를 업데이트합니다.

oc-mirror 플러그인 v2 를 사용하여 이미지를 미러링합니다.

에이전트 기반 설치 관리자를 사용하여 클러스터를 설치합니다.

로컬 OpenShift Update Service 인스턴스를 사용하여 클러스터를 업데이트합니다.

## 2장. 연결된 클러스터를 연결이 끊긴 클러스터로 변환

OpenShift Container Platform 클러스터를 연결된 클러스터에서 연결이 끊긴 클러스터로 변환해야 하는 몇 가지 시나리오가 있을 수 있습니다.

제한된 클러스터라고도 하는 연결이 끊긴 클러스터에는 인터넷에 대한 활성 연결이 없습니다. 따라서 레지스트리 및 설치 미디어의 콘텐츠를 미러링해야 합니다. 인터넷과 폐쇄 네트워크에 모두 액세스할 수 있는 호스트에 이 미러 레지스트리를 생성하거나 네트워크 경계를 이동할 수 있는 장치에 이미지를 복사할 수 있습니다.

이 주제에서는 연결된 기존 클러스터를 연결이 끊긴 클러스터로 변환하는 일반적인 프로세스에 대해 설명합니다.

### 2.1. 미러 레지스트리 정보

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스해야 합니다. 대체 레지스트리를 사용하면 네트워크와 인터넷에 모두 액세스할 수 있는 미러 호스트에 미러 레지스트리를 배치합니다.

OpenShift Container Platform 설치 및 후속 제품 업데이트에 필요한 이미지를 Red Hat Quay, JFrog Artifactory, Sonatype Nexus Repository 또는 Harbor와 같은 컨테이너 미러 레지스트리에 미러링할 수 있습니다.

대규모 컨테이너 레지스트리에 액세스할 수 없는 경우 OpenShift Container Platform 서브스크립션에 포함된 소규모 컨테이너 레지스트리인 Red Hat OpenShift 에 미러 레지스트리를 사용할 수 있습니다.

Red Hat Quay, Red Hat OpenShift의 미러 레지스트리, Artifactory, Sonatype Nexus Repository 또는 Harbor와 같은 Docker v2-2 를 지원하는 컨테이너 레지스트리를 사용할 수 있습니다.

선택한 레지스트리에 관계없이 인터넷상의 Red Hat 호스팅 사이트의 콘텐츠를 격리된 이미지 레지스트리로 미러링하는 절차는 동일합니다. 콘텐츠를 미러링한 후 미러 레지스트리에서 이 콘텐츠를 검색하도록 각 클러스터를 설정합니다.

중요

OpenShift 이미지 레지스트리는 미러링 프로세스 중에 필요한 태그 없이 푸시를 지원하지 않으므로 대상 레지스트리로 사용할 수 없습니다.

Red Hat OpenShift의 미러 레지스트리가 아닌 컨테이너 레지스트리를 선택하는 경우 프로비저닝하는 클러스터의 모든 시스템에서 연결할 수 있어야 합니다. 레지스트리에 연결할 수 없는 경우 설치, 업데이트 또는 워크로드 재배치와 같은 일반 작업이 실패할 수 있습니다.

따라서 고가용성 방식으로 미러 레지스트리를 실행해야하며 미러 레지스트리는 최소한 OpenShift Container Platform 클러스터의 프로덕션 환경의 가용성조건에 일치해야 합니다.

미러 레지스트리를 OpenShift Container Platform 이미지로 채우면 다음 두 가지 시나리오를 수행할 수 있습니다. 호스트가 인터넷과 미러 레지스트리에 모두 액세스할 수 있지만 클러스터 노드에 액세스 할 수 없는 경우 해당 머신의 콘텐츠를 직접 미러링할 수 있습니다.

이 프로세스를 connected mirroring (미러링 연결)이라고 합니다. 그러한 호스트가 없는 경우 이미지를 파일 시스템에 미러링한 다음 해당 호스트 또는 이동식 미디어를 제한된 환경에 배치해야 합니다.

이 프로세스를 미러링 연결 해제 라고 합니다.

미러링된 레지스트리의 경우 가져온 이미지의 소스를 보려면 CRI-O 로그의 `Trying to access` 로그 항목을 검토해야 합니다. 노드에서 아래 명령을 사용하는 등의 이미지 가져오기 소스를 보는 다른 방법은 미러링되지 않은 이미지 이름을 표시합니다.

```shell
crictl images
```

참고

Red Hat은 OpenShift Container Platform에서 타사 레지스트리를 테스트하지 않습니다.

### 2.2. 사전 요구 사항

다음 명령클라이언트가 설치되어 있어야 합니다.

```shell
oc
```

실행 중인 클러스터가 있어야 합니다.

다음 레지스트리 중 하나와 같이 OpenShift Container Platform 클러스터를 호스팅할 위치에 Docker v2-2 를 지원하는 컨테이너 이미지 레지스트리인 설치된 미러 레지스트리입니다.

Red Hat Quay

JFrog Artifactory

Sonatype Nexus Repository

Harbor

Red Hat Quay에 대한 서브스크립션이 있는 경우 개념 증명 목적 으로 또는 Quay Operator 를 사용하여 Red Hat Quay 배포에 대한 설명서를 참조하십시오.

이미지를 공유하도록 미러 저장소를 구성해야 합니다. 예를 들어, Red Hat Quay 리포지토리에는 이미지를 공유하기 위해 조직이 필요합니다.

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스합니다.

### 2.3. 미러링을 위한 클러스터 준비

클러스터의 연결을 해제하기 전에 연결이 끊긴 클러스터의 모든 노드에서 연결할 수 있는 미러 레지스트리에 이미지를 미러링하거나 복사해야 합니다. 이미지를 미러링하려면 다음을 통해 클러스터를 준비해야 합니다.

호스트의 신뢰할 수 있는 CA 목록에 미러 레지스트리 인증서를 추가합니다.

`cloud.openshift.com` 토큰에서 이미지 가져오기 보안이 포함된 `.dockerconfigjson` 파일을 생성합니다.

프로세스

이미지 미러링을 허용하는 인증 정보 구성:

미러 레지스트리의 CA 인증서를 간단한 PEM 또는 DER 파일 형식으로 신뢰할 수 있는 CA 목록에 추가합니다. 예를 들면 다음과 같습니다.

```shell-session
$ cp </path/to/cert.crt> /usr/share/pki/ca-trust-source/anchors/
```

다음과 같습니다., `</path/to/cert.crt>`

로컬 파일 시스템의 인증서 경로를 지정합니다.

CA 신뢰를 업데이트합니다. 예를 들어 Linux에서는 다음과 같습니다.

```shell-session
$ update-ca-trust
```

글로벌 가져오기 보안에서 `.dockerconfigjson` 파일을 추출합니다.

```shell-session
$ oc extract secret/pull-secret -n openshift-config --confirm --to=.
```

```shell-session
.dockerconfigjson
```

`.dockerconfigjson` 파일을 편집하여 미러 레지스트리 및 인증 자격 증명을 추가하고 새 파일로 저장합니다.

```shell-session
{"auths":{"<local_registry>": {"auth": "<credentials>","email": "you@example.com"}}},"<registry>:<port>/<namespace>/":{"auth":"<token>"}}}
```

다음과 같습니다.

`<local_registry>`

미러 레지스트리가 콘텐츠를 제공하는 데 사용하는 레지스트리 도메인 이름과 포트(선택 사항)를 지정합니다.

`auth`

미러 레지스트리의 base64로 인코딩된 사용자 이름 및 암호를 지정합니다.

`<registry>:<port>/<namespace>`

미러 레지스트리 세부 정보를 지정합니다.

`<token>`

미러 레지스트리의 base64로 인코딩된 `username:password` 를 지정합니다.

예를 들면 다음과 같습니다.

```shell-session
$ {"auths":{"cloud.openshift.com":{"auth":"b3BlbnNoaWZ0Y3UjhGOVZPT0lOMEFaUjdPUzRGTA==","email":"user@example.com"},
"quay.io":{"auth":"b3BlbnNoaWZ0LXJlbGVhc2UtZGOVZPT0lOMEFaUGSTd4VGVGVUjdPUzRGTA==","email":"user@example.com"},
"registry.connect.redhat.com"{"auth":"NTE3MTMwNDB8dWhjLTFEZlN3VHkxOSTd4VGVGVU1MdTpleUpoYkdjaUailA==","email":"user@example.com"},
"registry.redhat.io":{"auth":"NTE3MTMwNDB8dWhjLTFEZlN3VH3BGSTd4VGVGVU1MdTpleUpoYkdjaU9fZw==","email":"user@example.com"},
"registry.svc.ci.openshift.org":{"auth":"dXNlcjpyWjAwWVFjSEJiT2RKVW1pSmg4dW92dGp1SXRxQ3RGN1pwajJhN1ZXeTRV"},"my-registry:5000/my-namespace/":{"auth":"dXNlcm5hbWU6cGFzc3dvcmQ="}}}
```

### 2.4. 이미지 미러링

클러스터가 올바르게 구성되면 외부 리포지토리의 이미지를 미러 저장소로 미러링할 수 있습니다.

프로세스

OLM(Operator Lifecycle Manager) 이미지를 미러링합니다.

```shell-session
$ oc adm catalog mirror registry.redhat.io/redhat/redhat-operator-index:v{product-version} <mirror_registry>:<port>/olm -a <reg_creds>
```

다음과 같습니다.

`product-version`

설치할 OpenShift Container Platform 버전에 해당하는 태그(예: `4.8`)를 지정합니다.

`mirror_registry`

Operator 콘텐츠를 미러링할 대상 레지스트리 및 네임스페이스에 대해 FQDN(정규화된 도메인 이름)을 지정합니다. 여기서 < `namespace` >는 레지스트리의 기존 네임스페이스입니다.

`reg_creds`

수정된 `.dockerconfigjson` 파일의 위치를 지정합니다.

예를 들면 다음과 같습니다.

```shell-session
$ oc adm catalog mirror registry.redhat.io/redhat/redhat-operator-index:v4.8 mirror.registry.com:443/olm -a ./.dockerconfigjson  --index-filter-by-os='.*'
```

다른 Red Hat 제공 Operator의 콘텐츠를 미러링합니다.

```shell-session
$ oc adm catalog mirror <index_image> <mirror_registry>:<port>/<namespace> -a <reg_creds>
```

다음과 같습니다.

`index_image`

미러링할 카탈로그의 인덱스 이미지를 지정합니다.

`mirror_registry`

Operator 콘텐츠를 미러링할 대상 레지스트리 및 네임스페이스의 FQDN을 지정합니다. 여기서 < `namespace` >는 레지스트리의 기존 네임스페이스입니다.

`reg_creds`

선택 사항: 필요한 경우 레지스트리 자격 증명 파일의 위치를 지정합니다.

예를 들면 다음과 같습니다.

```shell-session
$ oc adm catalog mirror registry.redhat.io/redhat/community-operator-index:v4.8 mirror.registry.com:443/olm -a ./.dockerconfigjson  --index-filter-by-os='.*'
```

OpenShift Container Platform 이미지 저장소를 미러링합니다.

```shell-session
$ oc adm release mirror -a .dockerconfigjson --from=quay.io/openshift-release-dev/ocp-release:v<product-version>-<architecture> --to=<local_registry>/<local_repository> --to-release-image=<local_registry>/<local_repository>:v<product-version>-<architecture>
```

다음과 같습니다.

`product-version`

설치할 OpenShift Container Platform 버전에 해당하는 태그를 지정합니다 (예: `4.8.15-x86_64`).

`architecture`

서버의 아키텍처 유형(예: `x86_64`)을 지정합니다.

`local_registry`

미러 저장소의 레지스트리 도메인 이름을 지정합니다.

`local_repository`

레지스트리에 작성할 저장소 이름 (예: `ocp4/openshift4`)을 지정합니다.

예를 들면 다음과 같습니다.

```shell-session
$ oc adm release mirror -a .dockerconfigjson --from=quay.io/openshift-release-dev/ocp-release:4.8.15-x86_64 --to=mirror.registry.com:443/ocp/release --to-release-image=mirror.registry.com:443/ocp/release:4.8.15-x86_64
```

```shell-session
info: Mirroring 109 images to mirror.registry.com/ocp/release ...
mirror.registry.com:443/
  ocp/release
    manifests:
    sha256:086224cadce475029065a0efc5244923f43fb9bb3bb47637e0aaf1f32b9cad47 -> 4.8.15-x86_64-thanos
    sha256:0a214f12737cb1cfbec473cc301aa2c289d4837224c9603e99d1e90fc00328db -> 4.8.15-x86_64-kuryr-controller
    sha256:0cf5fd36ac4b95f9de506623b902118a90ff17a07b663aad5d57c425ca44038c -> 4.8.15-x86_64-pod
    sha256:0d1c356c26d6e5945a488ab2b050b75a8b838fc948a75c0fa13a9084974680cb -> 4.8.15-x86_64-kube-client-agent

…..
sha256:66e37d2532607e6c91eedf23b9600b4db904ce68e92b43c43d5b417ca6c8e63c mirror.registry.com:443/ocp/release:4.5.41-multus-admission-controller
sha256:d36efdbf8d5b2cbc4dcdbd64297107d88a31ef6b0ec4a39695915c10db4973f1 mirror.registry.com:443/ocp/release:4.5.41-cluster-kube-scheduler-operator
sha256:bd1baa5c8239b23ecdf76819ddb63cd1cd6091119fecdbf1a0db1fb3760321a2 mirror.registry.com:443/ocp/release:4.5.41-aws-machine-controllers
info: Mirroring completed in 2.02s (0B/s)

Success
Update image:  mirror.registry.com:443/ocp/release:4.5.41-x86_64
Mirror prefix: mirror.registry.com:443/ocp/release
```

필요에 따라 다른 레지스트리를 미러링합니다.

```shell-session
$ oc image mirror <online_registry>/my/image:latest <mirror_registry>
```

추가 리소스

Operator 카탈로그 미러링에 대한 자세한 내용은 Operator 카탈로그 미러링을 참조하십시오.

아래 명령에 대한 자세한 내용은 OpenShift CLI 관리자 명령 참조를 참조하십시오.

```shell
oc adm catalog mirror
```

### 2.5. 미러 레지스트리에 대한 클러스터 구성

이미지를 생성하고 미러 레지스트리에 미러링한 후 Pod가 미러 레지스트리에서 이미지를 가져올 수 있도록 클러스터를 수정해야 합니다.

다음을 수행해야 합니다.

글로벌 풀 시크릿에 미러 레지스트리 인증 정보를 추가합니다.

미러 레지스트리 서버 인증서를 클러스터에 추가합니다.

미러 레지스트리를 소스 레지스트리와 연결하는 `ImageContentSourcePolicy` 사용자 정의 리소스(ICSP)를 생성합니다.

클러스터 글로벌 풀 시크릿에 미러 레지스트리 인증 정보를 추가합니다.

```shell-session
$ oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=<pull_secret_location>
```

1. 새 풀 시크릿 파일의 경로를 제공합니다.

예를 들면 다음과 같습니다.

```shell-session
$ oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=.mirrorsecretconfigjson
```

클러스터의 노드에 CA 서명 미러 레지스트리 서버 인증서를 추가합니다.

미러 레지스트리의 서버 인증서가 포함된 구성 맵을 생성합니다.

```shell-session
$ oc create configmap <config_map_name> --from-file=<mirror_address_host>..<port>=$path/ca.crt -n openshift-config
```

예를 들면 다음과 같습니다.

```shell-session
S oc create configmap registry-config --from-file=mirror.registry.com..443=/root/certs/ca-chain.cert.pem -n openshift-config
```

구성 맵을 사용하여 `image.config.openshift.io/cluster` 사용자 정의 리소스(CR)를 업데이트합니다. OpenShift Container Platform은 이 CR에 변경 사항을 클러스터의 모든 노드에 적용합니다.

```shell-session
$ oc patch image.config.openshift.io/cluster --patch '{"spec":{"additionalTrustedCA":{"name":"<config_map_name>"}}}' --type=merge
```

예를 들면 다음과 같습니다.

```shell-session
$ oc patch image.config.openshift.io/cluster --patch '{"spec":{"additionalTrustedCA":{"name":"registry-config"}}}' --type=merge
```

ICSP를 생성하여 온라인 레지스트리에서 미러 레지스트리로 컨테이너 가져오기 요청을 리디렉션합니다.

`ImageContentSourcePolicy` 사용자 정의 리소스를 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: mirror-ocp
spec:
  repositoryDigestMirrors:
  - mirrors:
    - mirror.registry.com:443/ocp/release
    source: quay.io/openshift-release-dev/ocp-release
  - mirrors:
    - mirror.registry.com:443/ocp/release
    source: quay.io/openshift-release-dev/ocp-v4.0-art-dev
```

1. 미러 이미지 레지스트리 및 저장소의 이름을 지정합니다.

2. 미러링된 콘텐츠가 포함된 온라인 레지스트리 및 저장소를 지정합니다.

ICSP 오브젝트를 생성합니다.

```shell-session
$ oc create -f registryrepomirror.yaml
```

```shell-session
imagecontentsourcepolicy.operator.openshift.io/mirror-ocp created
```

OpenShift Container Platform은 이 CR에 대한 변경 사항을 클러스터의 모든 노드에 적용합니다.

미러 레지스트리의 인증 정보, CA, ICSP가 추가되었는지 확인합니다.

노드에 로그인합니다.

```shell-session
$ oc debug node/<node_name>
```

디버그 쉘 내에서 `/host` 를 root 디렉터리로 설정합니다.

```shell-session
sh-4.4# chroot /host
```

인증 정보가 `config.json` 파일을 확인합니다.

```shell-session
sh-4.4# cat /var/lib/kubelet/config.json
```

```shell-session
{"auths":{"brew.registry.redhat.io":{"xx=="},"brewregistry.stage.redhat.io":{"auth":"xxx=="},"mirror.registry.com:443":{"auth":"xx="}}}
```

1. 미러 레지스트리 및 인증 정보가 있는지 확인합니다.

`certs.d` 디렉터리로 변경합니다.

```shell-session
sh-4.4# cd /etc/docker/certs.d/
```

`certs.d` 디렉터리에 인증서를 나열합니다.

```shell-session
sh-4.4# ls
```

```plaintext
image-registry.openshift-image-registry.svc.cluster.local:5000
image-registry.openshift-image-registry.svc:5000
mirror.registry.com:443
```

1. 미러 레지스트리가 목록에 있는지 확인합니다.

ICSP가 `registries.conf` 파일에 미러 레지스트리를 추가했는지 확인합니다.

```shell-session
sh-4.4# cat /etc/containers/registries.conf
```

```shell-session
unqualified-search-registries = ["registry.access.redhat.com", "docker.io"]

[[registry]]
  prefix = ""
  location = "quay.io/openshift-release-dev/ocp-release"
  mirror-by-digest-only = true

  [[registry.mirror]]
    location = "mirror.registry.com:443/ocp/release"

[[registry]]
  prefix = ""
  location = "quay.io/openshift-release-dev/ocp-v4.0-art-dev"
  mirror-by-digest-only = true

  [[registry.mirror]]
    location = "mirror.registry.com:443/ocp/release"
```

`registry.mirror` 매개변수는 미러 레지스트리가 원래 레지스트리보다 먼저 검색됨을 나타냅니다.

노드를 종료합니다.

```shell-session
sh-4.4# exit
```

### 2.6. 애플리케이션이 계속 작동하도록 보장

네트워크에서 클러스터를 분리하기 전에 클러스터가 예상대로 작동하고 모든 애플리케이션이 예상대로 작동하는지 확인합니다.

프로세스

다음 명령을 사용하여 클러스터 상태를 확인합니다.

Pod가 실행 중인지 확인합니다.

```shell-session
$ oc get pods --all-namespaces
```

```shell-session
NAMESPACE                                          NAME                                                          READY   STATUS      RESTARTS   AGE
kube-system                                        apiserver-watcher-ci-ln-47ltxtb-f76d1-mrffg-master-0          1/1     Running     0          39m
kube-system                                        apiserver-watcher-ci-ln-47ltxtb-f76d1-mrffg-master-1          1/1     Running     0          39m
kube-system                                        apiserver-watcher-ci-ln-47ltxtb-f76d1-mrffg-master-2          1/1     Running     0          39m
openshift-apiserver-operator                       openshift-apiserver-operator-79c7c646fd-5rvr5                 1/1     Running     3          45m
openshift-apiserver                                apiserver-b944c4645-q694g                                     2/2     Running     0          29m
openshift-apiserver                                apiserver-b944c4645-shdxb                                     2/2     Running     0          31m
openshift-apiserver                                apiserver-b944c4645-x7rf2                                     2/2     Running     0          33m
 ...
```

노드가 READY 상태에 있는지 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME                                       STATUS   ROLES    AGE   VERSION
ci-ln-47ltxtb-f76d1-mrffg-master-0         Ready    master   42m   v1.33.4
ci-ln-47ltxtb-f76d1-mrffg-master-1         Ready    master   42m   v1.33.4
ci-ln-47ltxtb-f76d1-mrffg-master-2         Ready    master   42m   v1.33.4
ci-ln-47ltxtb-f76d1-mrffg-worker-a-gsxbz   Ready    worker   35m   v1.33.4
ci-ln-47ltxtb-f76d1-mrffg-worker-b-5qqdx   Ready    worker   35m   v1.33.4
ci-ln-47ltxtb-f76d1-mrffg-worker-c-rjkpq   Ready    worker   34m   v1.33.4
```

### 2.7. 네트워크에서 클러스터 연결 해제

필요한 리포지토리를 모두 미러링하고 클러스터를 연결이 끊긴 클러스터로 구성한 후 네트워크에서 클러스터의 연결을 해제할 수 있습니다.

참고

클러스터가 인터넷 연결이 끊어지면 Insights Operator의 성능이 저하됩니다. 복원할 수 있을 때까지 Insights Operator를 일시적으로 비활성화하여 이 문제를 방지할 수 있습니다.

### 2.8. 성능 저하된 Insights Operator 복원

네트워크에서 클러스터를 분리하면 클러스터가 인터넷 연결이 끊어야 합니다. Insights Operator는 Red Hat Lightspeed 에 액세스해야 하므로 성능이 저하됩니다.

이 주제에서는 성능이 저하된 Insights Operator에서 복구하는 방법을 설명합니다.

프로세스

`.dockerconfigjson` 파일을 편집하여 `cloud.openshift.com` 항목을 제거합니다. 예를 들면 다음과 같습니다.

```shell-session
"cloud.openshift.com":{"auth":"<hash>","email":"user@example.com"}
```

파일을 저장합니다.

편집된 `.dockerconfigjson` 파일로 클러스터 시크릿을 업데이트합니다.

```shell-session
$ oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=./.dockerconfigjson
```

Insights Operator의 성능이 더 이상 저하되지 않았는지 확인합니다.

```shell-session
$ oc get co insights
```

```shell-session
NAME       VERSION   AVAILABLE   PROGRESSING   DEGRADED   SINCE
insights   4.5.41    True        False         False      3d
```

### 2.9. 네트워크 복원

연결이 끊긴 클러스터를 다시 연결하고 온라인 레지스트리에서 이미지를 가져오려면 클러스터의 ImageContentSourcePolicy (ICSP) 오브젝트를 삭제합니다. ICSP가 없으면 외부 레지스트리로 가져오기 요청이 더 이상 미러 레지스트리로 리디렉션되지 않습니다.

프로세스

클러스터의 ICSP 오브젝트를 확인합니다.

```shell-session
$ oc get imagecontentsourcepolicy
```

```shell-session
NAME                 AGE
mirror-ocp           6d20h
ocp4-index-0         6d18h
qe45-index-0         6d15h
```

클러스터의 연결을 해제할 때 생성한 모든 ICSP 오브젝트를 삭제합니다.

```shell-session
$ oc delete imagecontentsourcepolicy <icsp_name> <icsp_name> <icsp_name>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc delete imagecontentsourcepolicy mirror-ocp ocp4-index-0 qe45-index-0
```

```shell-session
imagecontentsourcepolicy.operator.openshift.io "mirror-ocp" deleted
imagecontentsourcepolicy.operator.openshift.io "ocp4-index-0" deleted
imagecontentsourcepolicy.operator.openshift.io "qe45-index-0" deleted
```

모든 노드가 다시 시작되고 READY 상태로 돌아갈 때까지 기다린 후 `registries.conf` 파일이 미러 레지스트리가 아닌 원래 레지스트리를 가리키고 있는지 확인합니다.

노드에 로그인합니다.

```shell-session
$ oc debug node/<node_name>
```

디버그 쉘 내에서 `/host` 를 root 디렉터리로 설정합니다.

```shell-session
sh-4.4# chroot /host
```

`registries.conf` 파일을 검사합니다.

```shell-session
sh-4.4# cat /etc/containers/registries.conf
```

```shell-session
unqualified-search-registries = ["registry.access.redhat.com", "docker.io"]
```

1. 삭제한 ICSP에서 생성한 `registry` 및 `registry.mirror` 항목이 제거됩니다.

## 3장. 연결 해제된 설치 미러링 정보

클러스터 관리자는 미러 레지스트리를 사용하여 클러스터가 외부 콘텐츠에 대한 조직의 제어를 충족하는 컨테이너 이미지만 사용하도록 할 수 있습니다.

### 3.1. 연결이 끊긴 환경에 클러스터를 설치하기 위한 미러 레지스트리

클러스터를 설치하고 프로비저닝하려면 필요한 컨테이너 이미지를 연결이 끊긴 환경에 미러링해야 합니다. 이러한 컨테이너 이미지를 미러링하려면 미러 레지스트리가 있어야 합니다. 미러 레지스트리를 생성하고 사용하려면 다음 옵션을 고려하십시오.

Red Hat Quay와 같은 컨테이너 이미지 레지스트리가 이미 있는 경우 이를 미러 레지스트리로 사용할 수 있습니다. 아직 레지스트리가 없는 경우 레지스트리를 생성해야 합니다.

레지스트리를 설정한 후에는 미러링 도구가 필요합니다. OpenShift Container Platform 이미지 저장소를 연결이 끊긴 환경의 미러 레지스트리에 미러링하려면 oc-mirror OpenShift CLI() 플러그인을 사용할 수 있습니다.

```shell
oc
```

oc-mirror 플러그인은 필요한 모든 OpenShift Container Platform 콘텐츠 및 기타 이미지를 미러 레지스트리에 미러링하는 단일 툴입니다. oc-mirror 플러그인은 미러링을 위한 기본 방법입니다.

또는 아래 명령을 사용하여 OpenShift Container Platform의 릴리스 및 카탈로그 이미지만 미러링할 수 있습니다.

```shell
oc adm
```

## 4장. Red Hat OpenShift용 미러 레지스트리를 사용하여 미러 레지스트리 생성

Red Hat OpenShift의 미러 레지스트리 는 연결이 끊긴 설치에 필요한 OpenShift Container Platform 컨테이너 이미지를 미러링하기 위해 대상으로 사용할 수 있는 작고 간소화된 컨테이너 레지스트리입니다.

Red Hat Quay 와 같은 컨테이너 이미지 레지스트리가 이미 있는 경우 이 섹션을 건너뛰고 OpenShift Container Platform 이미지 리포지토리 미러링 으로 바로 이동할 수 있습니다.

중요

Red Hat OpenShift의 미러 레지스트리 는 Red Hat Quay의 프로덕션 배포를 대체하기 위한 것이 아닙니다.

### 4.1. 사전 요구 사항

OpenShift Container Platform 서브스크립션

Podman 3.4.2 이상 및 OpenSSL이 설치된 RHEL(Red Hat Enterprise Linux) 8 및 9.

DNS 서버를 통해 확인해야 하는 Red Hat Quay 서비스의 정규화된 도메인 이름입니다.

대상 호스트의 키 기반 SSH 연결 로컬 설치를 위해 SSH 키가 자동으로 생성됩니다. 원격 호스트의 경우 자체 SSH 키를 생성해야 합니다.

2개 이상의 vCPU

8GB RAM.

OpenShift Container Platform 4.20 릴리스 이미지의 경우 약 12GB 또는 OpenShift Container Platform 4.20 릴리스 이미지 및 OpenShift Container Platform 4.20 Red Hat Operator 이미지의 경우 약 358GB입니다.

중요

스트림당 최대 1TB 또는 그 이상이 권장됩니다.

이러한 요구 사항은 릴리스 이미지 및 Operator 이미지만을 사용한 로컬 테스트 결과를 기반으로 합니다. 스토리지 요구 사항은 조직의 요구에 따라 다를 수 있습니다.

예를 들어 여러 z-streams를 미러링할 때 더 많은 공간이 필요할 수 있습니다. 표준 Red Hat Quay 기능 또는 적절한 API 호출 을 사용하여 불필요한 이미지를 제거하고 공간을 확보할 수 있습니다.

### 4.2. Red Hat OpenShift 배포를 위한 미러 레지스트리

OpenShift Container Platform의 연결이 끊긴 배포의 경우 클러스터 설치를 수행하려면 컨테이너 레지스트리가 필요합니다. 이러한 클러스터에서 프로덕션 레벨 레지스트리 서비스를 실행하려면 첫 번째 클러스터를 설치하기 위해 별도의 레지스트리 배포를 생성해야 합니다.

Red Hat OpenShift의 미러 레지스트리는 이러한 요구 사항을 충족하며 모든 OpenShift Container Platform 서브스크립션에 포함되어 있습니다. OpenShift 콘솔 다운로드 페이지에서 다운로드할 수 있습니다.

Red Hat OpenShift의 미러 레지스트리를 사용하면 `mirror-registry` CLI(명령줄 인터페이스) 툴을 사용하여 Red Hat Quay의 소규모 버전과 필요한 구성 요소를 설치할 수 있습니다. Red Hat OpenShift의 미러 레지스트리 는 사전 구성된 로컬 스토리지 및 로컬 데이터베이스와 함께 자동으로 배포됩니다.

또한 단일 입력 세트로 자동 생성된 사용자 자격 증명 및 액세스 권한이 포함되며, 추가 구성 옵션 없이 시작할 수 있습니다.

Red Hat OpenShift의 미러 레지스트리 는 사전 결정된 네트워크 구성을 제공하고 성공한 경우 배포된 구성 요소 인증 정보 및 액세스 URL을 보고합니다. FQDN(정규화된 도메인 이름) 서비스, 슈퍼유저 이름 및 암호, 사용자 지정 TLS 인증서와 같은 제한된 선택적 구성 입력 세트도 제공됩니다.

이를 통해 제한된 네트워크 환경에서 OpenShift Container Platform을 실행할 때 모든 OpenShift Container Platform 릴리스 콘텐츠의 오프라인 미러를 쉽게 생성할 수 있도록 컨테이너 레지스트리가 제공됩니다.

설치 환경에서 다른 컨테이너 레지스트리를 이미 사용할 수 있는 경우 Red Hat OpenShift에 미러 레지스트리를 사용하는 것이 선택 사항입니다.

#### 4.2.1. Red Hat OpenShift 제한 사항을 위한 미러 레지스트리

다음 제한 사항은 Red Hat OpenShift의 미러 레지스트리에 적용됩니다.

Red Hat OpenShift의 미러 레지스트리 는 고가용성 레지스트리가 아니며 로컬 파일 시스템 스토리지만 지원됩니다. Red Hat Quay 또는 OpenShift Container Platform의 내부 이미지 레지스트리를 대체하기 위한 것이 아닙니다.

Red Hat OpenShift의 미러 레지스트리 는 Red Hat Quay의 프로덕션 배포를 대체하기 위한 것이 아닙니다.

Red Hat OpenShift의 미러 레지스트리 는 릴리스 이미지 또는 Red Hat Operator 이미지와 같은 연결이 끊긴 OpenShift Container Platform 클러스터를 설치하는 데 필요한 이미지 호스팅에만 지원됩니다.

RHEL(Red Hat Enterprise Linux) 머신의 로컬 스토리지를 사용하고 RHEL에서 지원하는 스토리지는 Red Hat OpenShift의 미러 레지스트리에서 지원합니다.

참고

Red Hat OpenShift의 미러 레지스트리 는 로컬 스토리지를 사용하므로 이미지를 미러링하고 Red Hat Quay의 가비지 컬렉션 기능을 사용하여 잠재적인 문제를 완화할 때 사용되는 스토리지 사용량을 계속 알고 있어야 합니다. 이 기능에 대한 자세한 내용은 "Red Hat Quay 가비지 컬렉션"을 참조하십시오.

부트스트랩 목적으로 Red Hat OpenShift의 미러 레지스트리로 푸시된 Red Hat 제품 이미지에 대한 지원은 각 제품에 유효한 서브스크립션이 적용됩니다. 부트스트랩 환경을 추가로 활성화하는 예외 목록은 Self-managed Red Hat OpenShift 크기 조정 및 서브스크립션 가이드에서 확인할 수 있습니다.

고객이 빌드한 콘텐츠는 Red Hat OpenShift의 미러 레지스트리에서 호스팅해서는 안 됩니다.

클러스터 플릿을 업데이트할 때 여러 클러스터가 단일 장애 지점을 생성할 수 있으므로 클러스터가 두 개 이상 있는 Red Hat OpenShift의 미러 레지스트리 를 사용하는 것은 권장되지 않습니다.

대신 Red Hat OpenShift의 미러 레지스트리를 사용하여 OpenShift Container Platform 콘텐츠를 다른 클러스터에 제공할 수 있는 Red Hat Quay와 같은 프로덕션 수준의 고가용성 레지스트리를 호스팅할 수 있는 클러스터를 설치합니다.

### 4.3. Red Hat OpenShift의 미러 레지스트리를 사용하여 로컬 호스트에서 미러링

다음 절차에서는 `mirror-registry 설치 프로그램 도구를 사용하여 로컬 호스트에 Red Hat OpenShift` 의 미러 레지스트리를 설치하는 방법을 설명합니다. 이렇게 하면 OpenShift Container Platform 이미지의 미러를 저장하기 위해 포트 443에서 실행되는 로컬 호스트 레지스트리를 생성할 수 있습니다.

참고

`mirror-registry CLI 툴을 사용하여 Red Hat OpenShift` 의 미러 레지스트리를 설치하면 시스템에 몇 가지 변경 사항이 적용됩니다. 설치 후 설치 파일, 로컬 스토리지 및 구성 번들이 있는 `$HOME/quay-install` 디렉터리가 생성됩니다.

배포 대상이 로컬 호스트인 경우 신뢰할 수 있는 SSH 키가 생성되고, 컨테이너 런타임이 영구적인지 확인하기 위해 호스트 시스템의 systemd 파일이 설정됩니다. 또한 `init` 라는 초기 사용자는 자동으로 생성된 암호를 사용하여 생성됩니다.

모든 액세스 인증 정보는 설치 루틴이 끝나면 출력됩니다.

프로세스

OpenShift 콘솔 다운로드 페이지에 있는 Red Hat OpenShift의 미러 레지스트리 최신 버전의 `mirror-registry`.tar.gz 패키지를 다운로드합니다.

`mirror-registry 툴을 사용하여 현재 사용자 계정으로 로컬 호스트에 Red Hat OpenShift` 의 미러 레지스트리를 설치합니다. 사용 가능한 플래그의 전체 목록은 "Red Hat OpenShift 플래그의 미러 레지스트리"를 참조하십시오.

```shell-session
$ ./mirror-registry install \
  --quayHostname <host_example_com> \
  --quayRoot <example_directory_name>
```

설치 중에 생성된 사용자 이름과 암호를 사용하여 다음 명령을 실행하여 레지스트리에 로그인합니다.

```shell-session
$ podman login -u init \
  -p <password> \
  <host_example_com>:8443> \
  --tls-verify=false
```

1. 생성된 rootCA 인증서를 신뢰하도록 시스템을 구성하여 `--tls-verify=false` 실행을 방지할 수 있습니다. 자세한 내용은 "Red Hat Quay 확인" 및 "인증 기관을 신뢰하도록 시스템 구성"을 참조하십시오.

참고

설치 후 `https://<host.example.com>:8443` 에서 UI에 액세스하여 로그인할 수도 있습니다.

로그인 후 OpenShift Container Platform 이미지를 미러링할 수 있습니다. 필요에 따라 이 문서의 "OpenShift Container Platform 이미지 리포지토리 미러링" 또는 "연결이 끊긴 클러스터에 사용할 Operator 카탈로그 미러링" 섹션을 참조하십시오.

참고

스토리지 계층 문제로 인해 Red Hat OpenShift의 미러 레지스트리에 저장된 이미지에 문제가 있는 경우 OpenShift Container Platform 이미지를 다시 미러링하거나 더 안정적인 스토리지에 미러 레지스트리를 다시 설치할 수 있습니다.

### 4.4. 로컬 호스트에서 Red Hat OpenShift의 미러 레지스트리 업데이트

다음 절차에서는 `upgrade` 명령을 사용하여 로컬 호스트에서 Red Hat OpenShift의 미러 레지스트리 를 업데이트하는 방법을 설명합니다. 최신 버전으로 업데이트하면 새로운 기능, 버그 수정 및 보안 취약점 수정이 제공됩니다.

중요

버전 1에서 버전 2로 업그레이드할 때 다음 제약 조건을 유의하십시오.

SQLite에서 여러 쓰기가 허용되지 않기 때문에 작업자 수가 `1` 로 설정됩니다.

Red Hat OpenShift 사용자 인터페이스(UP)에는 미러 레지스트리를 사용해서는 안 됩니다.

업그레이드하는 동안 `sqlite-storage` Podman 볼륨에 액세스하지 마십시오.

업그레이드 프로세스 중에 다시 시작되므로 미러 레지스트리의 간헐적 다운 타임이 발생합니다.

PostgreSQL 데이터는 복구를 위해 `/$HOME/quay-install/quay-postgres-backup/` 디렉터리에 백업됩니다.

사전 요구 사항

로컬 호스트에 Red Hat OpenShift의 미러 레지스트리 가 설치되어 있습니다.

프로세스

Red Hat OpenShift의 미러 레지스트리를 1.3 → 2.y에서 업그레이드하는 중이며 설치 디렉터리가 `/etc/quay-install` 에서 기본값인 경우 다음 명령을 입력할 수 있습니다.

```shell-session
$ sudo ./mirror-registry upgrade -v
```

참고

Red Hat OpenShift의 미러 레지스트리 는 Red Hat Quay 스토리지, Postgres 데이터 및 `/etc/quay-install` 데이터를 새로운 `$HOME/quay-install` 위치에 대한 Podman 볼륨을 마이그레이션합니다.

이를 통해 향후 업그레이드 중에 `--quayRoot` 플래그 없이 Red Hat OpenShift에 미러 레지스트리 를 사용할 수 있습니다.

`./ mirror-registry upgrade -v 플래그를 사용하여 Red Hat OpenShift` 의 미러 레지스트리를 업그레이드하는 사용자는 미러 레지스트리를 생성할 때 사용되는 것과 동일한 인증 정보를 포함해야 합니다.

예를 들어 다음 명령을 사용하여 Red Hat OpenShift의 미러 레지스트리 를 설치한 경우 미러 레지스트리를 올바르게 업그레이드하려면 해당 문자열을 포함해야 합니다.

```shell
--quayHostname <host_example_com> 및 --quay Root <example_directory_name>
```

Red Hat OpenShift의 미러 레지스트리를 1.3 → 2.y에서 업그레이드하고 1.y 배포에서 사용자 지정 quay 구성 및 스토리지 디렉토리를 사용한 경우 `--quayRoot` 및 `--quayStorage` 플래그를 전달해야 합니다. 예를 들면 다음과 같습니다.

```shell-session
$ sudo ./mirror-registry upgrade --quayHostname <host_example_com> --quayRoot <example_directory_name>  --quayStorage <example_directory_name>/quay-storage -v
```

Red Hat OpenShift의 미러 레지스트리를 1.3 → 2.y에서 업그레이드하고 사용자 정의 SQLite 스토리지 경로를 지정하려면 `--sqliteStorage` 플래그를 전달해야 합니다. 예를 들면 다음과 같습니다.

```shell-session
$ sudo ./mirror-registry upgrade --sqliteStorage <example_directory_name>/sqlite-storage -v
```

검증

다음 명령을 실행하여 Red Hat OpenShift의 미러 레지스트리 가 업데이트되었는지 확인합니다.

```shell-session
$ podman ps
```

```shell-session
registry.redhat.io/quay/quay-rhel8:v3.12.10
```

### 4.5. Red Hat OpenShift의 미러 레지스트리를 사용하여 원격 호스트에서 미러링

다음 절차에서는 `mirror-registry 툴을 사용하여 원격 호스트에 Red Hat OpenShift` 의 미러 레지스트리를 설치하는 방법을 설명합니다. 이렇게 하면 사용자가 OpenShift Container Platform 이미지의 미러를 저장할 레지스트리를 생성할 수 있습니다.

참고

`mirror-registry CLI 툴을 사용하여 Red Hat OpenShift` 의 미러 레지스트리를 설치하면 시스템에 몇 가지 변경 사항이 적용됩니다. 설치 후 설치 파일, 로컬 스토리지 및 구성 번들이 있는 `$HOME/quay-install` 디렉터리가 생성됩니다.

배포 대상이 로컬 호스트인 경우 신뢰할 수 있는 SSH 키가 생성되고, 컨테이너 런타임이 영구적인지 확인하기 위해 호스트 시스템의 systemd 파일이 설정됩니다. 또한 `init` 라는 초기 사용자는 자동으로 생성된 암호를 사용하여 생성됩니다.

모든 액세스 인증 정보는 설치 루틴이 끝나면 출력됩니다.

프로세스

OpenShift 콘솔 다운로드 페이지에 있는 Red Hat OpenShift의 미러 레지스트리 최신 버전의 `mirror-registry`.tar.gz 패키지를 다운로드합니다.

`mirror-registry 툴을 사용하여 현재 사용자 계정으로 로컬 호스트에 Red Hat OpenShift` 의 미러 레지스트리를 설치합니다. 사용 가능한 플래그의 전체 목록은 "Red Hat OpenShift 플래그의 미러 레지스트리"를 참조하십시오.

```shell-session
$ ./mirror-registry install -v \
  --targetHostname <host_example_com> \
  --targetUsername <example_user> \
  -k ~/.ssh/my_ssh_key \
  --quayHostname <host_example_com> \
  --quayRoot <example_directory_name>
```

설치 중에 생성된 사용자 이름과 암호를 사용하여 다음 명령을 실행하여 미러 레지스트리에 로그인합니다.

```shell-session
$ podman login -u init \
  -p <password> \
  <host_example_com>:8443> \
  --tls-verify=false
```

1. 생성된 rootCA 인증서를 신뢰하도록 시스템을 구성하여 `--tls-verify=false` 실행을 방지할 수 있습니다. 자세한 내용은 "Red Hat Quay 확인" 및 "인증 기관을 신뢰하도록 시스템 구성"을 참조하십시오.

참고

설치 후 `https://<host.example.com>:8443` 에서 UI에 액세스하여 로그인할 수도 있습니다.

로그인 후 OpenShift Container Platform 이미지를 미러링할 수 있습니다. 필요에 따라 이 문서의 "OpenShift Container Platform 이미지 리포지토리 미러링" 또는 "연결이 끊긴 클러스터에 사용할 Operator 카탈로그 미러링" 섹션을 참조하십시오.

참고

스토리지 계층 문제로 인해 Red Hat OpenShift의 미러 레지스트리에 저장된 이미지에 문제가 있는 경우 OpenShift Container Platform 이미지를 다시 미러링하거나 더 안정적인 스토리지에 미러 레지스트리를 다시 설치할 수 있습니다.

### 4.6. 원격 호스트에서 Red Hat OpenShift의 미러 레지스트리 업데이트

다음 절차에서는 `upgrade` 명령을 사용하여 원격 호스트에서 Red Hat OpenShift의 미러 레지스트리 를 업데이트하는 방법을 설명합니다. 최신 버전으로 업데이트하면 버그 수정 및 보안 취약점 수정이 제공됩니다.

중요

버전 1에서 버전 2로 업그레이드할 때 다음 제약 조건을 유의하십시오.

SQLite에서 여러 쓰기가 허용되지 않기 때문에 작업자 수가 `1` 로 설정됩니다.

Red Hat OpenShift 사용자 인터페이스(UP)에는 미러 레지스트리를 사용해서는 안 됩니다.

업그레이드하는 동안 `sqlite-storage` Podman 볼륨에 액세스하지 마십시오.

업그레이드 프로세스 중에 다시 시작되므로 미러 레지스트리의 간헐적 다운 타임이 발생합니다.

PostgreSQL 데이터는 복구를 위해 `/$HOME/quay-install/quay-postgres-backup/` 디렉터리에 백업됩니다.

사전 요구 사항

원격 호스트에 Red Hat OpenShift의 미러 레지스트리 가 설치되어 있습니다.

프로세스

원격 호스트에서 Red Hat OpenShift의 미러 레지스트리를 업그레이드하려면 다음 명령을 입력합니다.

```shell-session
$ ./mirror-registry upgrade -v --targetHostname <remote_host_url> --targetUsername <user_name> -k ~/.ssh/my_ssh_key
```

참고

`./ mirror-registry upgrade -v 플래그를 사용하여 Red Hat OpenShift` 의 미러 레지스트리를 업그레이드하는 사용자는 미러 레지스트리를 생성할 때 사용되는 것과 동일한 인증 정보를 포함해야 합니다.

예를 들어 다음 명령을 사용하여 Red Hat OpenShift의 미러 레지스트리 를 설치한 경우 미러 레지스트리를 올바르게 업그레이드하려면 해당 문자열을 포함해야 합니다.

```shell
--quayHostname <host_example_com> 및 --quay Root <example_directory_name>
```

Red Hat OpenShift의 미러 레지스트리를 1.3 → 2.y에서 업그레이드하고 사용자 정의 SQLite 스토리지 경로를 지정하려면 `--sqliteStorage` 플래그를 전달해야 합니다. 예를 들면 다음과 같습니다.

```shell-session
$ ./mirror-registry upgrade -v --targetHostname <remote_host_url> --targetUsername <user_name> -k ~/.ssh/my_ssh_key --sqliteStorage <example_directory_name>/quay-storage
```

검증

다음 명령을 실행하여 Red Hat OpenShift의 미러 레지스트리 가 업데이트되었는지 확인합니다.

```shell-session
$ podman ps
```

```shell-session
registry.redhat.io/quay/quay-rhel8:v3.12.10
```

### 4.7. Red Hat OpenShift SSL/TLS 인증서의 미러 레지스트리 교체

경우에 따라 Red Hat OpenShift 의 미러 레지스트리에 대한 SSL/TLS 인증서를 업데이트할 수 있습니다. 이 기능은 다음 시나리오에서 유용합니다.

Red Hat OpenShift 인증서의 현재 미러 레지스트리를 교체하는 경우.

Red Hat OpenShift 설치를 위해 이전 미러 레지스트리와 동일한 인증서를 사용하는 경우

Red Hat OpenShift 인증서의 미러 레지스트리를 주기적으로 업데이트하는 경우.

Red Hat OpenShift SSL/TLS 인증서의 미러 레지스트리를 교체하려면 다음 절차를 사용하십시오.

사전 요구 사항

OpenShift 콘솔 다운로드 페이지에서 `./mirror-registry` 바이너리를 다운로드 하여 설치했습니다.

프로세스

다음 명령을 입력하여 Red Hat OpenShift의 미러 레지스트리를 설치합니다.

```shell-session
$ ./mirror-registry install \
--quayHostname <host_example_com> \
--quayRoot <example_directory_name>
```

이렇게 하면 Red Hat OpenShift의 미러 레지스트리 가 `$HOME/quay-install` 디렉터리에 설치됩니다.

새 CA(인증 기관) 번들을 준비하고 새 `ssl.key` 및 `ssl.crt` 키 파일을 생성합니다. 자세한 내용은 Red Hat Quay용 SSL 및 TLS 구성 을 참조하십시오.

다음 명령을 입력하여 `/$HOME/quay-install` 환경 변수(예: `QUAY`)를 할당합니다.

```shell-session
$ export QUAY=/$HOME/quay-install
```

다음 명령을 입력하여 새 `ssl.crt` 파일을 `/$HOME/quay-install` 디렉터리에 복사합니다.

```shell-session
$ cp ~/ssl.crt $QUAY/quay-config
```

다음 명령을 입력하여 새 `ssl.key` 파일을 `/$HOME/quay-install` 디렉터리에 복사합니다.

```shell-session
$ cp ~/ssl.key $QUAY/quay-config
```

다음 명령을 입력하여 `quay-app` 애플리케이션 포드를 다시 시작합니다.

```shell-session
$ systemctl --user restart quay-app
```

### 4.8. Red Hat OpenShift의 미러 레지스트리 설치 제거

로컬 호스트에서 Red Hat OpenShift의 미러 레지스트리를 제거하려면 다음 절차를 사용하십시오.

사전 요구 사항

로컬 호스트에 Red Hat OpenShift의 미러 레지스트리 가 설치되어 있습니다.

프로세스

다음 명령을 실행하여 로컬 호스트에서 Red Hat OpenShift의 미러 레지스트리 를 설치 제거합니다.

```shell-session
$ ./mirror-registry uninstall -v \
  --quayRoot <example_directory_name>
```

참고

Red Hat OpenShift의 미러 레지스트리를 삭제하면 삭제하기 전에 사용자에게 메시지를 표시합니다. `--autoApprove` 를 사용하여 이 프롬프트를 건너뛸 수 있습니다.

`--quayRoot` 플래그를 사용하여 Red Hat OpenShift의 미러 레지스트리 를 설치하는 사용자는 제거할 때 `--quayRoot` 플래그를 포함해야 합니다.

예를 들어 `--quayRoot example_directory_name` 을 사용하여 Red Hat OpenShift의 미러 레지스트리 를 설치한 경우 미러 레지스트리를 올바르게 제거하려면 해당 문자열을 포함해야 합니다.

### 4.9. Red Hat OpenShift 플래그의 미러 레지스트리

다음 플래그는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

| 플래그 | 설명 |
| --- | --- |
| `--autoApprove` | 대화형 프롬프트를 비활성화하는 부울 값입니다. `true` 로 설정하면 미러 레지스트리를 제거할 때 `quayRoot` 디렉터리가 자동으로 삭제됩니다. 지정되지 않은 경우 기본값은 `false` 입니다. |
| `--initPassword` | Quay 설치 중에 생성된 init 사용자의 암호입니다. 8자 이상이어야 하며 공백을 포함하지 않아야 합니다. |
| `--initUser string` | 초기 사용자의 사용자 이름을 표시합니다. 지정되지 않은 경우 기본값은 `init` 입니다. |
| `--no-color` , `-c` | 사용자는 색상 시퀀스를 비활성화하고 설치, 제거 및 업그레이드 명령을 실행할 때 Ansible에 이를 전파할 수 있습니다. |
| `--quayHostname` | 클라이언트가 레지스트리에 연결하는 데 사용할 미러 레지스트리의 정규화된 도메인 이름입니다. Quay `config.yaml` 의 `SERVER_HOSTNAME` 과 동일합니다. DNS로 확인해야 합니다. 지정되지 않은 경우 기본값은 `<targetHostname>:8443` 입니다. [1] |
| `--quayStorage` | Quay 영구 스토리지 데이터가 저장되는 폴더입니다. 기본값은 `quay-storage` Podman 볼륨입니다. 루트 권한을 제거해야 합니다. |
| `--quayRoot` , `-r` | `rootCA.key` , `rootCA.pem` , `rootCA.srl` 인증서를 포함하여 컨테이너 이미지 계층 및 구성 데이터가 저장되는 디렉터리입니다. 지정되지 않은 경우 기본값은 `$HOME/quay-install` 입니다. |
| `--sqliteStorage` | SQLite 데이터베이스 데이터가 저장되는 폴더입니다. 지정되지 않은 경우 기본값은 `sqlite-storage` Podman 볼륨입니다. 설치를 제거하려면 root가 필요합니다. |
| `--SSH-key` , `-k` | SSH ID 키의 경로입니다. 지정되지 않은 경우 기본값은 `~/.ssh/quay_installer` 입니다. |
| `--sslCert` | SSL/TLS 공개 키 / 인증서의 경로입니다. 기본값은 `{quayRoot}/quay-config` 이며 지정되지 않은 경우 자동으로 생성됩니다. |
| `--sslCheckSkip` | `config.yaml` 파일의 `SERVER_HOSTNAME` 에 대해 인증서 호스트 이름의 검사를 건너뜁니다. [2] |
| `--sslKey` | HTTPS 통신에 사용되는 SSL/TLS 개인 키의 경로입니다. 기본값은 `{quayRoot}/quay-config` 이며 지정되지 않은 경우 자동으로 생성됩니다. |
| `--targetHostname` , `-H` | Quay를 설치할 대상의 호스트 이름입니다. 지정되지 않은 경우 기본값은 `$HOST` (예: 로컬 호스트)입니다. |
| `--targetUsername` , `-u` | SSH에 사용할 대상 호스트의 사용자입니다. 기본값은 `$USER` 입니다. 예를 들어 지정되지 않은 경우 현재 사용자입니다. |
| `--verbose` , `-v` | 디버그 로그 및 Ansible 플레이북 출력을 표시합니다. |
| `--version` | Red Hat OpenShift의 미러 레지스트리 버전을 보여줍니다. |

시스템의 공용 DNS 이름이 로컬 호스트 이름과 다른 경우 `--quayHostname` 을 수정해야 합니다. 또한 `--quayHostname` 플래그는 IP 주소와 함께 설치를 지원하지 않습니다. 호스트 이름으로 설치해야 합니다.

`--sslCheckSkip` 은 미러 레지스트리가 프록시 뒤에 설정되고 노출된 호스트 이름이 내부 Quay 호스트 이름과 다른 경우 사용됩니다. 설치하는 동안 제공된 Quay 호스트 이름에 대해 인증서의 유효성을 검사하는 것을 원하지 않을 때 사용할 수도 있습니다.

### 4.10. Red Hat OpenShift 릴리스 노트의 미러 레지스트리

Red Hat OpenShift의 미러 레지스트리 는 연결이 끊긴 설치에 필요한 OpenShift Container Platform 컨테이너 이미지를 미러링하기 위해 대상으로 사용할 수 있는 작고 간소화된 컨테이너 레지스트리입니다.

이 릴리스 노트에서는 OpenShift Container Platform의 Red Hat OpenShift의 미러 레지스트리 개발을 추적합니다.

#### 4.10.1. Red Hat OpenShift 2.0 릴리스 노트의 미러 레지스트리

다음 섹션에서는 Red Hat OpenShift의 미러 레지스트리 각 2.0 릴리스에 대한 세부 정보를 제공합니다.

#### 4.10.1.1. Red Hat OpenShift 2.0.8의 미러 레지스트리

출시 날짜: 2025년 10월 16일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.12에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2025:17062 - Red Hat OpenShift 2.0.8의 미러 레지스트리

#### 4.10.1.2. Red Hat OpenShift 2.0.7의 미러 레지스트리

출시 날짜: 2025년 7월 14일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.10에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2025:9645 - Red Hat OpenShift 2.0.7의 미러 레지스트리

#### 4.10.1.3. Red Hat OpenShift 2.0.6의 미러 레지스트리

출시 날짜: 2025년 4월 28일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.8에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2025:4251 - Red Hat OpenShift 2.0.6의 미러 레지스트리

#### 4.10.1.4. Red Hat OpenShift 2.0.5의 미러 레지스트리

출시 날짜: 2025년 1월 13일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.5에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2025:0298 - Red Hat OpenShift 2.0.5의 미러 레지스트리

#### 4.10.1.5. Red Hat OpenShift 2.0.4의 미러 레지스트리

출시 날짜: 2025년 1월 06일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.4에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2025:0033 - Red Hat OpenShift 2.0.4의 미러 레지스트리

#### 4.10.1.6. Red Hat OpenShift 2.0.3의 미러 레지스트리

출시 날짜: 2024년 11월 25일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.3에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2024:10181 - Red Hat OpenShift 2.0.3의 미러 레지스트리

#### 4.10.1.7. Red Hat OpenShift 2.0.2의 미러 레지스트리

출시 날짜: 2024년 10월 31일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.2에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2024:8370 - Red Hat OpenShift 2.0.2의 미러 레지스트리

#### 4.10.1.8. Red Hat OpenShift 2.0.1의 미러 레지스트리

출시 날짜: 2024년 9월 26일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.1에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2024:7070 - Red Hat OpenShift 2.0.1의 미러 레지스트리

#### 4.10.1.9. Red Hat OpenShift 2.0.0의 미러 레지스트리

출시 날짜: 2024년 9월 3일

Red Hat OpenShift의 미러 레지스트리 는 이제 Red Hat Quay 3.12.0에서 사용할 수 있습니다.

다음 권고는 Red Hat OpenShift의 미러 레지스트리에 사용할 수 있습니다.

RHBA-2024:5277 - Red Hat OpenShift 2.0.0의 미러 레지스트리

Red Hat OpenShift 2.0.0의 미러 레지스트리와 함께 다음과 같은 새로운 기능을 사용할 수 있습니다.

Red Hat OpenShift 용 미러 레지스트리 가 릴리스되면서 내부 데이터베이스가 PostgreSQL에서 SQLite로 업그레이드되었습니다. 결과적으로 데이터가 기본적으로 `sqlite-storage` Podman 볼륨에 저장되고 전체 tarball 크기는 300MB로 줄어듭니다.

새 설치에서는 기본적으로 SQLite를 사용합니다. 버전 2.0으로 업그레이드하기 전에 환경에 따라 "로컬 호스트에서 Red Hat OpenShift의 미러 레지스트리 업그레이드" 또는 "원격 호스트에서 Red Hat OpenShift용 미러 레지스트리 업그레이드"를 참조하십시오.

새로운 기능 플래그 `--sqliteStorage` 가 추가되었습니다. 이 플래그를 사용하면 SQLite 데이터베이스 데이터가 저장되는 위치를 수동으로 설정할 수 있습니다.

Red Hat OpenShift의 미러 레지스트리 는 IBM Power 및 IBM Z 아키텍처(`s390x` 및 `ppc64le`)에서 사용할 수 있습니다.

#### 4.10.2. Red Hat OpenShift 1.3 릴리스 노트의 미러 레지스트리

Red Hat OpenShift 1.3 릴리스 노트의 미러 레지스트리를 보려면 Red Hat OpenShift 1.3 릴리스 노트의 미러 레지스트리 를 참조하십시오.

#### 4.10.3. Red Hat OpenShift 1.2 릴리스 노트의 미러 레지스트리

Red Hat OpenShift 1.2 릴리스 노트의 미러 레지스트리를 보려면 Red Hat OpenShift 1.2 릴리스 노트의 미러 레지스트리 를 참조하십시오.

#### 4.10.4. Red Hat OpenShift 1.1 릴리스 노트의 미러 레지스트리

Red Hat OpenShift 1.1 릴리스 노트의 미러 레지스트리를 보려면 Red Hat OpenShift 1.1 릴리스 노트의 미러 레지스트리 를 참조하십시오.

### 4.11. Red Hat OpenShift의 미러 레지스트리 문제 해결

Red Hat OpenShift의 미러 레지스트리 문제 해결을 지원하기 위해 미러 레지스트리에서 설치한 systemd 서비스의 로그를 수집할 수 있습니다. 다음 서비스가 설치됩니다.

quay-app.service

quay-redis.service

quay-pod.service

사전 요구 사항

Red Hat OpenShift용 미러 레지스트리 가 설치되어 있어야 합니다.

프로세스

루트 권한으로 Red Hat OpenShift의 미러 레지스트리를 설치한 경우 다음 명령을 입력하여 systemd 서비스의 상태 정보를 가져올 수 있습니다.

```shell-session
$ sudo systemctl status <service>
```

Red Hat OpenShift의 미러 레지스트리를 표준 사용자로 설치한 경우 다음 명령을 입력하여 systemd 서비스의 상태 정보를 가져올 수 있습니다.

```shell-session
$ systemctl --user status <service>
```

### 4.12. 추가 리소스

Red Hat Quay 가비지 컬렉션

Red Hat Quay 보안

인증 기관을 신뢰하도록 시스템 구성

OpenShift Container Platform 이미지 저장소 미러링

연결이 끊긴 클러스터와 함께 사용할 Operator 카탈로그 미러링

## 5장. oc-mirror 플러그인 v2를 사용하여 연결이 끊긴 설치의 이미지 미러링

프라이빗 레지스트리의 미러링된 OpenShift Container Platform 컨테이너 이미지에서 클러스터를 설치하는 경우 연결이 끊긴 환경에서 클러스터를 실행할 수 있습니다. 이 레지스트리는 클러스터가 실행될 때마다 실행되어야 합니다.

oc-mirror 플러그인 v2를 사용하여 완전히 또는 부분적으로 연결이 끊긴 환경의 미러 레지스트리에 이미지를 미러링할 수 있습니다. 공식 Red Hat 레지스트리에서 필요한 이미지를 다운로드하려면 인터넷 연결이 있는 시스템에서 oc-mirror 플러그인 v2를 실행해야 합니다.

### 5.1. oc-mirror 플러그인 v2 정보

oc-mirror OpenShift CLI() 플러그인은 필요한 모든 OpenShift Container Platform 콘텐츠 및 기타 이미지를 미러 레지스트리에 미러링하는 단일 툴입니다.

```shell
oc
```

새 버전의 oc-mirror를 사용하려면 oc-mirror 플러그인 v2 명령줄에 `--v2` 플래그를 추가합니다.

oc-mirror 플러그인 v2에는 다음과 같은 기능이 있습니다.

OpenShift Container Platform 릴리스, Operator, helm 차트 및 기타 이미지를 미러링하는 중앙 집중식 방법을 제공합니다.

이미지 세트 구성 파일에 지정된 전체 이미지 세트가 이전에 미러링되었는지 여부에 관계없이 미러링된 레지스트리에 미러링되었는지 확인합니다.

프로세스 단일 단계에서 오류가 발생하는 경우 미러링 프로세스를 시작할 필요가 없도록 메타데이터 대신 캐시 시스템을 사용합니다.

새 이미지만 아카이브에 통합하여 최소한의 아카이브 크기를 유지합니다.

미러링 날짜별로 선택한 콘텐츠로 미러링 아카이브를 생성합니다.

v1을 사용한 각 미러링 작업에 대한 이미지 세트만 적용되는 `ImageContentSourcePolicy` (ICSP) 리소스 대신 전체 이미지 세트를 포함하는 `ImageDigestMirrorSet` (IDMS) 및 `ImageTagMirrorSet` (ITMS) 리소스를 생성할 수 있습니다.

자동 정리를 수행하지 않습니다. v2에서는 이제 `Delete` 기능을 사용하여 사용자에게 이미지 삭제를 보다 효과적으로 제어할 수 있습니다.

`registries.conf` 파일을 지원합니다. 이 변경으로 동일한 캐시를 사용하는 동안 여러 개의 enclaves로 미러링할 수 있습니다.

#### 5.1.1. 고급 워크플로

다음 단계에서는 oc-mirror 플러그인 v2를 사용하여 이미지를 미러 레지스트리에 미러링하는 방법에 대한 고급 워크플로를 간략하게 설명합니다.

이미지 세트 구성 파일을 생성합니다.

다음 워크플로우 중 하나를 사용하여 대상 미러 레지스트리에 설정된 이미지를 미러링합니다.

대상 미러 레지스트리(mirror to mirror)에 직접 설정된 이미지를 미러링합니다.

이미지 세트를 디스크로 미러링하고, 파일을 대상 환경으로 전송한 다음, 대상 미러 레지스트리로 설정된 이미지를 미러링합니다(디스크를 미러링할 디스크).

```shell
tar
```

oc-mirror 플러그인 v2에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

필요에 따라 대상 미러 레지스트리를 업데이트하려면 다음 단계를 반복합니다.

#### 5.1.2. oc-mirror 플러그인 v2 호환성 및 지원

oc-mirror 플러그인 v2는 OpenShift Container Platform에서 지원됩니다.

참고

`aarch64`, `ppc64le` 및 `s390x` 아키텍처에서 oc-mirror 플러그인 v2는 OpenShift Container Platform 4.14 이상에서만 지원됩니다.

미러링해야 하는 OpenShift Container Platform 버전에 관계없이 사용 가능한 최신 oc-mirror 플러그인 v2 버전을 사용합니다.

### 5.2. 사전 요구 사항

Red Hat Quay와 같이 OpenShift Container Platform 클러스터를 호스팅하는 위치에 Docker V2-2 를 지원하는 컨테이너 이미지 레지스트리가 있어야 합니다.

참고

Red Hat Quay를 사용하는 경우 oc-mirror 플러그인과 함께 버전 3.6 이상을 사용하십시오. OpenShift Container Platform (Red Hat Quay 문서)에 Red Hat Quay Operator 배포를 참조하십시오. 레지스트리를 선택하고 설치하는 데 추가 지원이 필요한 경우 영업 담당자 또는 Red Hat 지원팀에 문의하십시오.

컨테이너 이미지 레지스트리에 대한 기존 솔루션이 없는 경우 OpenShift Container Platform 구독자에게 Red Hat OpenShift의 미러 레지스트리가 제공됩니다. 이 미러 레지스트리는 서브스크립션에 포함되어 있으며 소규모 컨테이너 레지스트리 역할을 합니다.

이 레지스트리를 사용하여 연결이 끊긴 설치에 필요한 OpenShift Container Platform 컨테이너 이미지를 미러링할 수 있습니다.

프로비저닝된 클러스터의 모든 시스템은 미러 레지스트리에 액세스할 수 있어야 합니다. 레지스트리에 연결할 수 없는 경우 설치, 업데이트 또는 워크로드 재배치와 같은 일상적인 작업과 같은 작업이 실패할 수 있습니다. 미러 레지스트리는 고가용성 방식으로 작동하여 OpenShift Container Platform 클러스터의 프로덕션 가용성과 일치하도록 해야 합니다.

### 5.3. 미러 호스트 준비

이미지 미러링에 oc-mirror 플러그인 v2를 사용하려면 플러그인을 설치하고 컨테이너 이미지에 대한 인증 정보가 있는 파일을 생성하여 Red Hat에서 미러로 미러링할 수 있어야 합니다.

#### 5.3.1. oc-mirror OpenShift CLI 플러그인 설치

oc-mirror OpenShift CLI 플러그인을 설치하여 연결이 끊긴 환경에서 이미지 세트를 관리합니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다. 완전히 연결이 끊긴 환경에서 이미지 세트를 미러링하는 경우 다음을 확인하십시오.

```shell
oc
```

인터넷에 액세스할 수 있는 호스트에 oc-mirror 플러그인을 설치했습니다.

연결이 끊긴 환경의 호스트는 대상 미러 레지스트리에 액세스할 수 있습니다.

oc-mirror `를` 사용하는 운영 체제에서 Cryostat 매개변수를 `0022` 로 설정해야 합니다.

사용 중인 RHEL 버전에 대해 올바른 바이너리를 설치했습니다.

프로세스

oc-mirror CLI 플러그인을 다운로드합니다.

Red Hat Hybrid Cloud Console의 다운로드 페이지로 이동합니다.

OpenShift 연결 설치 툴 섹션의 드롭다운 메뉴에서 OpenShift Client(oc) 미러 플러그인 의 OS 유형 및 아키텍처 유형을 선택합니다.

다운로드를 클릭하여 파일을 저장합니다.

다음 명령을 실행하여 아카이브의 압축을 풉니다.

```shell-session
$ tar xvzf oc-mirror.tar.gz
```

필요한 경우 다음 명령을 실행하여 플러그인 파일을 실행 가능하게 업데이트합니다.

```shell-session
$ chmod +x oc-mirror
```

참고

다음 명령파일의 이름을 바꾸지 마십시오.

```shell
oc-mirror
```

다음 명령을 실행하여 파일을 `PATH` (예: `/usr/local/bin`)에 배치하여 oc-mirror CLI 플러그인을 설치합니다.

```shell-session
$ sudo mv oc-mirror /usr/local/bin/.
```

검증

다음 명령을 실행하여 oc-mirror 플러그인 v2가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc mirror --v2 --help
```

#### 5.3.2. 이미지를 미러링할 수 있는 인증 정보 설정

Red Hat에서 미러로 이미지를 미러링할 수 있도록 컨테이너 이미지 레지스트리 인증 정보 파일을 생성합니다. 설치 호스트에서 다음 단계를 완료합니다.

주의

클러스터를 설치할 때 이 이미지 레지스트리 인증 정보 파일을 풀 시크릿(pull secret)으로 사용하지 마십시오. 클러스터를 설치할 때 이 파일을 지정하면 클러스터의 모든 시스템에 미러 레지스트리에 대한 쓰기 권한이 부여됩니다.

사전 요구 사항

연결이 끊긴 환경에서 사용할 미러 레지스트리를 구성했습니다.

미러 레지스트리에서 이미지를 미러링할 이미지 저장소 위치를 확인했습니다.

이미지를 해당 이미지 저장소에 업로드할 수 있는 미러 레지스트리 계정을 제공하고 있습니다.

미러 레지스트리에 대한 쓰기 권한이 있습니다.

프로세스

Red Hat OpenShift Cluster Manager 에서 `registry.redhat.io` 풀 시크릿을 다운로드합니다.

다음 명령을 실행하여 풀 시크릿을 JSON 형식으로 복사합니다.

```shell-session
$ cat ./pull-secret | jq . > <path>/<pull_secret_file_in_json>
```

풀 시크릿을 저장할 디렉터리의 경로와 생성한 JSON 파일의 이름을 지정합니다.

```plaintext
{
  "auths": {
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

`$XDG_RUNTIME_DIR/containers` 디렉터리가 없는 경우 다음 명령을 입력하여 만듭니다.

```shell-session
$ mkdir -p $XDG_RUNTIME_DIR/containers
```

풀 시크릿 파일을 `$XDG_RUNTIME_DIR/containers/auth.json` 로 저장합니다.

다음 명령을 실행하여 미러 레지스트리에 대한 base64로 인코딩된 사용자 이름 및 암호 또는 토큰을 생성합니다.

```shell-session
$ echo -n '<user_name>:<password>' | base64 -w0
```

`<user_name>` 및 `<password>` 의 경우 레지스트리에 설정한 사용자 이름 및 암호를 지정합니다.

```shell-session
BGVtbYk3ZHAtqXs=
```

JSON 파일을 편집하고 레지스트리를 설명하는 섹션을 추가합니다.

```plaintext
"auths": {
    "<mirror_registry>": {
      "auth": "<credentials>",
      "email": "you@example.com"
    }
  },
```

&lt `;mirror_registry` > 값의 경우 미러 레지스트리가 콘텐츠를 제공하는 데 사용하는 레지스트리 도메인 이름과 포트(선택 사항)를 지정합니다. 예: `registry.example.com` 또는 `registry.example.com:8443`.

&lt `;credentials&` gt; 값의 경우 미러 레지스트리의 base64 인코딩 사용자 이름과 암호를 지정합니다.

```plaintext
{
  "auths": {
    "registry.example.com": {
      "auth": "BGVtbYk3ZHAtqXs=",
      "email": "you@example.com"
    },
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

### 5.4. 미러 레지스트리로 이미지 세트 미러링

미러 레지스트리로 이미지를 미러링하면 안전하고 제어된 환경에서 필요한 이미지를 사용할 수 있으므로 더 원활한 배포, 업데이트 및 유지 관리 작업을 수행할 수 있습니다.

#### 5.4.1. 이미지 세트 구성 생성

oc-mirror 플러그인 v2를 사용하여 이미지를 미러링하려면 먼저 이미지 세트 구성 파일을 생성해야 합니다. 이 이미지 세트 구성 파일은 oc-mirror 플러그인 v2의 다른 구성 설정과 함께 미러링할 OpenShift Container Platform 릴리스, Operator 및 기타 이미지를 정의합니다.

사전 요구 사항

컨테이너 이미지 레지스트리 인증 정보 파일이 생성되어 있습니다. 자세한 내용은 이미지를 미러링할 수 있는 인증 정보 구성을 참조하십시오.

프로세스

`ImageSetConfiguration` YAML 파일을 생성하고 필요한 이미지를 포함하도록 수정합니다.

```yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v2alpha1
mirror:
  platform:
    channels:
    - name: stable-4.20
      minVersion: 4.20.2
      maxVersion: 4.20.2
    graph: true
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
      packages:
       - name: aws-load-balancer-operator
       - name: 3scale-operator
       - name: node-observability-operator
  additionalImages:
   - name: registry.redhat.io/ubi8/ubi:latest
   - name: registry.redhat.io/ubi9/ubi@sha256:20f695d2a91352d4eaa25107535126727b5945bff38ed36a3e59590f495046f0
```

1. 채널을 설정하여 OpenShift Container Platform 이미지를 검색합니다.

2. `graph: true` 를 추가하여 graph-data 이미지를 빌드 및 미러 레지스트리로 내보냅니다. OSUS(OpenShift Update Service)를 생성하려면 graph-data 이미지가 필요합니다.

`graph: true` 필드에서도 `UpdateService` 사용자 정의 리소스 매니페스트를 생성합니다. CLI(명령줄 인터페이스)는 `UpdateService` 사용자 정의 리소스 매니페스트를 사용하여 OSUS를 생성할 수 있습니다.

```shell
oc
```

자세한 내용은 OpenShift 업데이트 서비스 정보 를 참조하십시오.

3. Operator 카탈로그를 설정하여 OpenShift Container Platform 이미지를 검색합니다.

4. 이미지 세트에 포함할 특정 Operator 패키지만 지정합니다. 이 필드를 제거하여 카탈로그의 모든 패키지를 검색합니다.

5. 이미지 세트에 포함할 추가 이미지를 지정합니다.

참고

oc-mirror 플러그인 v2에서는 `additionalImages` 아래에 나열된 모든 이미지에 대해 명시적 레지스트리 호스트 이름을 사용해야 합니다. 그렇지 않으면 이미지가 잘못된 대상 경로로 미러링됩니다.

추가 리소스

OpenShift 업데이트 서비스 정보

#### 5.4.2. oc-mirror 워크플로우 비교

다음 표를 사용하여 mirror-to-disk(m2d), disk-to-mirror(d2m), mirror-to-mirror(m2m) 워크플로우에 대해 지원되는 사용 사례를 비교합니다.

| 사용 사례 | 미러 대상 디스크(m2d) 및 디스크 미러링(d2m) | 미러 대상 미러 (m2m) |
| --- | --- | --- |
| 대상 레지스트리는 인터넷 액세스가 없고 외부 액세스가 없는 환경에 있습니다. | ✓ |  |
| 대상 레지스트리는 인터넷에 액세스할 수 없지만 다른 시스템에서 액세스할 수 있는 환경에 있습니다. 예를 들어 대상 레지스트리는 bastion 호스트에 있습니다. |  | ✓ |
| USB 장치와 같은 물리적 방법을 사용하여 콘텐츠를 연결이 끊긴 환경으로 이동해야 합니다. | ✓ |  |
| 워크플로는 중간 tar 파일을 생성하지 않고 콘텐츠를 대상 레지스트리로 직접 이동합니다. |  | ✓ |
| 워크플로는 내부 캐시를 사용하여 실패 후 다시 시작되지만 추가 디스크 공간이 필요합니다. | ✓ |  |
| 워크플로는 캐시를 사용하지 않고 오류 발생 후 처음부터 다시 시작하며 추가 디스크 공간이 필요하지 않습니다. |  | ✓ |

#### 5.4.3. 부분적으로 연결이 끊긴 환경에서 이미지 세트 미러링

인터넷 액세스가 제한된 환경에서 oc-mirror 플러그인 v2를 사용하여 이미지 세트를 레지스트리에 미러링할 수 있습니다.

사전 요구 사항

oc-mirror 플러그인 v2를 실행하는 환경의 인터넷 및 미러 레지스트리에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 지정된 이미지 세트 구성의 이미지를 지정된 레지스트리로 미러링합니다.

```shell-session
$ oc mirror -c <image_set_configuration> --workspace file://<file_path> docker://<mirror_registry_url> --v2
```

다음과 같습니다.

<image_set_configuration>

이미지 세트 구성 파일의 이름을 지정합니다.

<file_path>

클러스터 리소스가 생성될 디렉터리를 지정합니다.

<mirror_registry_url>

이미지가 저장되고 삭제해야 하는 미러 레지스트리의 URL 또는 주소를 지정합니다.

검증

`<file_path>` 디렉터리에 생성된 `working-dir/cluster-resources` 디렉터리로 이동합니다.

`ImageDigestMirrorSet`, `ImageTagMirrorSet`, `CatalogSource` 리소스에 YAML 파일이 있는지 확인합니다.

다음 단계

oc-mirror 플러그인 v2에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

#### 5.4.4. 완전히 연결이 끊긴 환경에서 이미지 세트 미러링

OpenShift Container Platform 클러스터가 공용 인터넷에 액세스할 수 없는 완전히 연결이 끊긴 환경에서 이미지 세트를 미러링할 수 있습니다. 다음 고급 워크플로에서는 미러링 프로세스를 설명합니다.

mirror to disk: 이미지 세트를 아카이브로 미러링합니다.

디스크 전송: 압축 파일을 연결이 끊긴 미러 레지스트리의 네트워크로 수동으로 전송합니다.

Disk to mirror: 아카이브에서 대상 연결이 끊긴 레지스트리로 이미지 세트를 미러링합니다.

#### 5.4.4.1. 미러에서 디스크로 미러링

oc-mirror 플러그인 v2를 사용하여 이미지 세트를 생성하고 콘텐츠를 디스크에 저장할 수 있습니다. 이후 생성된 이미지 세트를 연결이 끊긴 환경으로 전송하고 대상 레지스트리에 미러링할 수 있습니다.

oc-mirror 플러그인 v2는 이미지 세트 구성 파일에 지정된 소스에서 컨테이너 이미지를 검색하고 로컬 디렉터리의 tar 아카이브에 추가합니다.

프로세스

다음 명령을 실행하여 지정된 이미지 세트 구성의 이미지를 디스크에 미러링합니다.

```shell-session
$ oc mirror -c <image_set_configuration> file://<file_path> --v2
```

다음과 같습니다.

<image_set_configuration>

이미지 세트 구성 파일의 이름을 지정합니다.

<file_path>

이미지 세트를 포함하는 아카이브가 생성될 디렉터리를 지정합니다.

검증

생성된 `<file_path>` 디렉터리로 이동합니다.

아카이브 파일이 생성되었는지 확인합니다.

다음 단계

디스크에서 미러로 미러링

#### 5.4.4.2. 디스크에서 미러로 미러링

oc-mirror 플러그인 v2를 사용하여 디스크에서 대상 미러 레지스트리로 이미지 세트를 미러링할 수 있습니다.

oc-mirror 플러그인 v2는 로컬 디스크에서 컨테이너 이미지를 검색하여 지정된 미러 레지스트리로 전송합니다.

프로세스

미러링된 이미지 세트가 포함된 디스크를 대상 미러 레지스트리가 포함된 환경으로 전송합니다.

디스크에서 이미지 세트 파일을 처리하고 다음 명령을 실행하여 콘텐츠를 대상 미러 레지스트리에 미러링합니다.

```shell-session
$ oc mirror -c <image_set_configuration> --from file://<file_path> docker://<mirror_registry_url> --v2
```

다음과 같습니다.

<image_set_configuration>

이미지 세트 구성 파일의 이름을 지정합니다.

<file_path>

아카이브를 포함하는 디스크의 디렉터리를 지정합니다. 이 폴더에는 클러스터에 적용할 수 있도록 생성된 클러스터 리소스도 포함됩니다(예: ImageDigestMirrorSet (IDMS) 또는 ImageTagMirrorSet (ITMS) 리소스).

<mirror_registry_url>

이미지가 저장되는 미러 레지스트리의 URL 또는 주소를 지정합니다.

검증

`<file_path>` 디렉터리에 생성된 `working-dir` 디렉터리 내에서 `cluster-resources` 디렉터리로 이동합니다.

`ImageDigestMirrorSet`, `ImageTagMirrorSet`, `CatalogSource` 리소스에 YAML 파일이 있는지 확인합니다.

다음 단계

oc-mirror 플러그인 v2에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

### 5.5. oc-mirror 플러그인 v2에서 생성한 사용자 정의 리소스 정보

oc-mirror 플러그인 v2는 다음 사용자 정의 리소스를 자동으로 생성합니다.

`ImageDigestMirrorSet` (IDMS)

이미지 다이제스트 가져오기 사양을 사용할 때 레지스트리 미러 규칙을 처리합니다. 다이제스트에 의해 이미지 세트의 이미지가 하나 이상 미러링되는 경우 생성됩니다.

`ImageTagMirrorSet` (ITMS)

이미지 태그 가져오기 사양을 사용할 때 레지스트리 미러 규칙을 처리합니다. 이미지 세트에서 하나 이상의 이미지가 태그로 미러링되는 경우 생성됩니다.

`CatalogSource`

미러 레지스트리에서 사용 가능한 Operator에 대한 정보를 검색합니다. OLM(Operator Lifecycle Manager) Classic에서 사용합니다.

`ClusterCatalog`

미러 레지스트리에서 사용 가능한 클러스터 확장(Operator 포함)에 대한 정보를 검색합니다. OLM v1에서 사용합니다.

`UpdateService`

연결이 끊긴 환경으로 그래프 데이터를 업데이트합니다. OpenShift 업데이트 서비스에서 사용합니다.

추가 리소스

CatalogSource

ImageDigestMirrorSet

ImageTagMirrorSet

OLM v1의 카탈로그 정보

#### 5.5.1. oc-mirror 플러그인에서 생성한 리소스 수정 제한

oc-mirror 플러그인 v2에서 생성한 리소스를 사용하여 클러스터를 구성하는 경우 특정 필드를 변경할 수 없습니다. 이러한 필드를 수정하면 오류가 발생할 수 있으며 지원되지 않습니다.

다음 표에는 변경되지 않은 상태로 유지해야 하는 리소스 및 해당 필드가 나열되어 있습니다.

| 리소스 | 변경할 수 없는 필드 |
| --- | --- |
| `CatalogSource` | `apiVersion` , `kind` , `spec.image` |
| `ClusterCatalog` | `apiVersion` , `kind` , `spec.source.image.ref` |
| `ImageDigestMirrorSet` | `apiVersion` , `kind` , `spec.imageDigestMirrors` |
| `ImageTagMirrorSet` | `apiVersion` , `kind` , `spec.imageTagMirrors` |
| 서명 `ConfigMap` | `apiVersion` , `kind` , `metadata.namespace` , `binaryData` |
| `UpdateService` | `apiVersion` , `kind` , `spec.graphDataImage` , `spec.releases` |

이러한 리소스에 대한 자세한 내용은 `CatalogSource`, `ImageDigestMirrorSet` 및 `ImageTagMirrorSet` 에 대한 OpenShift API 설명서를 참조하십시오.

#### 5.5.2. oc-mirror 플러그인 v2에서 생성한 리소스를 사용하도록 클러스터 구성

미러 레지스트리로 이미지를 미러링한 후 생성된 `ImageDigestMirrorSet` (IDMS), `ImageTagMirrorSet` (ITMS), `CatalogSource` 및 `UpdateService` 리소스를 클러스터에 적용해야 합니다.

중요

oc-mirror 플러그인 v2에서 IDMS 및 ITMS 파일은 oc-mirror 플러그인 v1의 `ImageContentSourcePolicy` (ICSP) 파일과 달리 전체 이미지 세트를 다룹니다. 따라서 IDMS 및 ITMS 파일에는 증분 미러링 중에 새 이미지만 추가하는 경우에도 세트의 모든 이미지가 포함됩니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`cluster-admin` 역할의 사용자로 OpenShift CLI에 로그인합니다.

다음 명령을 실행하여 결과 디렉터리의 YAML 파일을 클러스터에 적용합니다.

```shell-session
$ oc apply -f <path_to_oc_mirror_workspace>/working-dir/cluster-resources
```

미러링된 릴리스 이미지가 있는 경우 다음 명령을 실행하여 릴리스 이미지 서명을 클러스터에 적용합니다.

```shell-session
$ oc apply -f working-dir/cluster-resources/signature-configmap.json
```

중요

클러스터 대신 Operator를 미러링하는 경우 이전 명령을 실행하지 마십시오. 명령을 실행하면 적용할 릴리스 이미지 서명이 없기 때문에 오류가 발생합니다.

또한 YAML 파일은 동일한 디렉터리 `working-dir/cluster-resources/` 에서 사용할 수 있습니다. JSON 또는 YAML 형식을 사용할 수 있습니다.

검증

다음 명령을 실행하여 `ImageDigestMirrorSet` 리소스가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get imagedigestmirrorset
```

다음 명령에서 생성된 리소스만 보려면 다음 명령을 실행하세요.

```shell
oc-mirror
```

```shell-session
$ oc get imagedigestmirrorset -o jsonpath='{.items[?(@.metadata.annotations.createdBy=="oc-mirror v2")].metadata.name}'
```

다음 명령을 실행하여 `ImageTagMirrorSet` 리소스가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get imagetagmirrorset
```

다음 명령에서 생성된 리소스만 보려면 다음 명령을 실행하세요.

```shell
oc-mirror
```

```shell-session
$ oc get imagetagmirrorset -o jsonpath='{.items[?(@.metadata.annotations.createdBy=="oc-mirror v2")].metadata.name}'
```

다음 명령을 실행하여 `CatalogSource` 리소스가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get catalogsource -n openshift-marketplace
```

다음 명령에서 생성된 리소스만 보려면 다음 명령을 실행하세요.

```shell
oc-mirror
```

```shell-session
$ oc get catalogsource -o jsonpath='{.items[?(@.metadata.annotations.createdBy=="oc-mirror v2")].metadata.name}'
```

다음 명령을 실행하여 `ClusterCatalog` 리소스가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get clustercatalog
```

다음 명령에서 생성된 리소스만 보려면 다음 명령을 실행하세요.

```shell
oc-mirror
```

```shell-session
$ oc get clustercatalog -o jsonpath='{.items[?(@.metadata.annotations.createdBy=="oc-mirror v2")].metadata.name}'
```

oc-mirror 플러그인 v2에서 생성한 리소스를 사용하도록 클러스터를 구성한 후 미러링된 이미지를 사용하여 수행할 수 있는 작업에 대한 다음 단계를 참조하십시오.

추가 리소스

OLM v1에서 연결이 끊긴 환경 지원

### 5.6. 연결이 끊긴 환경에서 이미지 삭제

oc-mirror 플러그인 v2를 사용하여 이전에 이미지를 배포한 경우 이러한 이미지를 삭제하여 미러 레지스트리의 공간을 확보할 수 있습니다. oc-mirror 플러그인 v2는 `ImageSetConfiguration` 파일에 포함되지 않은 이미지를 자동으로 정리하지 않습니다.

이렇게 하면 `ImageSetConfig.yaml` 파일을 변경할 때 필요한 이미지 또는 배포된 이미지를 실수로 삭제하지 않습니다.

삭제할 이미지를 지정하려면 `DeleteImageSetConfiguration` 파일을 생성해야 합니다.

다음 예에서 `DeleteImageSetConfiguration` 파일은 다음 이미지를 제거합니다.

OpenShift Container Platform 4.13.3의 모든 릴리스 이미지

`aws-load-balancer-operator` v0.0.1 번들 및 모든 관련 이미지

해당 다이제스트에서 참조하는 `ubi` 및 `ubi-minimal` 의 추가 이미지입니다.

```yaml
apiVersion: mirror.openshift.io/v2alpha1
kind: DeleteImageSetConfiguration
delete:
  platform:
    channels:
      - name: stable-4.13
        minVersion: 4.13.3
        maxVersion: 4.13.3
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.12
      packages:
      - name: aws-load-balancer-operator
         minVersion: 0.0.1
         maxVersion: 0.0.1
  additionalImages:
    - name: registry.redhat.io/ubi8/ubi@sha256:bce7e9f69fb7d4533447232478fd825811c760288f87a35699f9c8f030f2c1a6
    - name: registry.redhat.io/ubi8/ubi-minimal@sha256:8bedbe742f140108897fb3532068e8316900d9814f399d676ac78b46e740e34e
```

중요

mirror-to-disk 및 disk-to-mirror 워크플로우를 사용하여 삭제 문제를 줄이는 것이 좋습니다.

oc-mirror 플러그인 v2에서는 `additionalImages` 아래에 나열된 모든 이미지에 대해 명시적 레지스트리 호스트 이름을 사용해야 합니다. 그렇지 않으면 이미지가 잘못된 대상 경로로 미러링됩니다.

oc-mirror 플러그인 v2는 이미지의 매니페스트만 삭제하여 레지스트리에 사용된 스토리지를 줄일 수 없습니다.

매니페스트가 삭제된 이미지와 같은 불필요한 이미지에서 스토리지 공간을 확보하려면 컨테이너 레지스트리에서 가비지 수집기를 활성화해야 합니다. 가비지 수집기가 활성화되면 레지스트리는 더 이상 매니페스트에 대한 참조가 없는 이미지 Blob을 삭제하여 이전에 삭제된 Blob에 의해 점유된 스토리지를 줄입니다.

가비지 수집기를 활성화하는 프로세스는 컨테이너 레지스트리에 따라 다릅니다.

자세한 내용은 "배포 레지스트리의 스토리지 정리 문제 복구"를 참조하십시오.

중요

Operator 이미지를 삭제하는 동안 Operator 카탈로그 이미지 삭제를 건너뛰려면 `DeleteImageSetConfiguration` 파일의 Operator 카탈로그 이미지에 특정 Operator를 나열해야 합니다. 이렇게 하면 카탈로그 이미지가 아닌 지정된 Operator만 삭제됩니다.

Operator 카탈로그 이미지만 지정하면 해당 카탈로그 내의 모든 Operator와 카탈로그 이미지 자체가 삭제됩니다.

oc-mirror 플러그인 v2는 다른 Operator를 계속 배포하고 이러한 이미지에 따라 달라질 수 있으므로 Operator 카탈로그 이미지를 자동으로 삭제하지 않습니다.

카탈로그의 Operator가 레지스트리 또는 클러스터에 남아 있지 않은 경우 `DeleteImageSetConfiguration` 의 `additionalImages` 에 카탈로그 이미지를 명시적으로 추가하여 제거할 수 있습니다.

가비지 컬렉션 동작은 레지스트리에 따라 다릅니다. 일부 레지스트리는 삭제된 이미지를 자동으로 제거하지 않으므로 시스템 관리자가 수동으로 가비지 컬렉션을 트리거하여 공간을 확보해야 합니다.

추가 리소스

배포 레지스트리에서 스토리지 정리 문제 해결

#### 5.6.1. 배포 레지스트리에서 스토리지 정리 문제 해결

배포 레지스트리에서 알려진 문제로 인해 가비지 수집기에서 예상대로 스토리지를 확보하지 못합니다. 이 문제는 Red Hat Quay를 사용할 때 발생하지 않습니다.

프로세스

배포 레지스트리에서 알려진 문제를 해결할 적절한 방법을 선택합니다.

컨테이너 레지스트리를 다시 시작하려면 다음 명령을 실행합니다.

```shell-session
$ podman restart <registry_container>
```

레지스트리 구성에서 캐싱을 비활성화하려면 다음 단계를 수행합니다.

`Blobdescriptor` 캐시를 비활성화하려면 `/etc/docker/registry/config.yml` 파일을 수정합니다.

```yaml
version: 0.1
log:
  fields:
    service: registry
storage:
  cache:
    blobdescriptor: ""
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: :5000
  headers:
    X-Content-Type-Options: [nosniff]
health:
  storagedriver:
    enabled: true
    interval: 10s
    threshold: 3
```

변경 사항을 적용하려면 다음 명령을 실행하여 컨테이너 레지스트리를 다시 시작합니다.

```shell-session
$ podman restart <registry_container>
```

#### 5.6.2. 연결이 끊긴 환경에서 이미지 삭제

oc-mirror 플러그인 v2를 사용하여 연결이 끊긴 환경에서 이미지를 삭제하려면 절차를 따르십시오.

사전 요구 사항

더 이상 매니페스트를 참조하지 않는 이미지를 삭제하도록 환경에서 가비지 컬렉션을 활성화했습니다.

프로세스

`delete-image-set-config.yaml` 파일을 생성하고 다음 콘텐츠를 포함합니다.

```yaml
apiVersion: mirror.openshift.io/v2alpha1
kind: DeleteImageSetConfiguration
delete:
  platform:
    channels:
      - name: <channel_name>
        minVersion: <channel_min_version>
        maxVersion: <channel_max_version>
  operators:
    - catalog: <operator_catalog_name>
      packages:
      - name: <operator_name>
         minVersion: <operator_max_version>
         maxVersion: <operator_min_version>
  additionalImages:
    - name: <additional_images>
```

1. 1

삭제할 OpenShift Container Platform 채널의 이름을 지정합니다(예: `stable-4.15`).

2. 3

채널 내에서 삭제할 이미지의 버전 범위를 지정합니다(예: 최소 버전의 경우 `4.15.0`, 최대 버전의 경우 `4.15.1`). 하나의 버전 이미지만 삭제하려면 `minVersion` 및 `maxVersion` 필드 모두에 해당 버전 번호를 사용합니다.

4. 삭제할 Operator가 포함된 Operator 카탈로그 이미지를 지정합니다(예: `registry.redhat.io/redhat/redhat-operator-index:v4.14`). Operator 카탈로그 이미지는 삭제되지 않습니다. 다른 Operator가 여전히 클러스터에 남아 있으면 레지스트리에 있어야 합니다.

5. 삭제할 특정 Operator를 지정합니다(예: `aws-load-balancer-operator`).

6. 7

Operator에 대해 삭제할 이미지의 버전 범위를 지정합니다(예: 최소 버전의 경우 `0.0.` 1, 최대 버전의 경우 0 `.` 0.2)입니다.

다음 명령을 실행하여 `delete-images.yaml` 파일을 생성합니다.

```shell-session
$ oc mirror delete --config delete-image-set-config.yaml --workspace file://<previously_mirrored_work_folder> --v2 --generate docker://<remote_registry>
```

다음과 같습니다.

<previously_mirrored_work_folder>

미러링 프로세스 중에 이미지가 이전에 미러링되었거나 저장된 디렉터리를 지정합니다.

<remote_registry>

이미지를 삭제할 원격 컨테이너 레지스트리의 URL 또는 주소를 지정합니다.

중요

이미지를 삭제할 때 올바른 작업 공간 디렉터리를 지정합니다. 새 클러스터 설정과 같이 미러링을 처음부터 시작할 때만 캐시 디렉터리를 수정하거나 삭제합니다. 캐시 디렉터리를 잘못 변경하면 추가 미러링 작업이 중단될 수 있습니다.

생성된 &lt `;previously_mirrored_work_folder>/delete` 디렉터리로 이동합니다.

`delete-images.yaml` 파일이 생성되었는지 확인합니다.

파일에 나열된 각 이미지가 더 이상 클러스터에 필요하지 않으며 레지스트리에서 안전하게 제거할 수 있는지 수동으로 확인합니다.

`delete-images` YAML 파일을 생성한 후 다음 명령을 실행하여 원격 레지스트리에서 이미지를 삭제합니다.

```shell-session
$ oc mirror delete --v2 --delete-yaml-file <previously_mirrored_work_folder>/working-dir/delete/delete-images.yaml docker://<remote_registry>
```

다음과 같습니다.

<previously_mirrored_work_folder>

미러링 프로세스 중에 이미지가 이전에 미러링되었거나 저장된 디렉터리를 지정합니다.

<remote_registry>

이미지를 삭제할 원격 컨테이너 레지스트리의 URL 또는 주소를 지정합니다.

중요

mirror-to-mirror 방법을 사용하여 이미지를 미러링할 때 이미지가 로컬에 캐시되지 않으므로 로컬 캐시에서 이미지를 삭제할 수 없습니다.

### 5.7. 미러링을 위해 선택한 이미지 확인

oc-mirror 플러그인 v2를 사용하여 실제로 이미지를 미러링하지 않는 테스트 실행(dry run)을 수행할 수 있습니다. 이를 통해 미러링할 이미지 목록을 검토할 수 있습니다.

예행 실행을 사용하여 이미지 세트 구성에서 오류를 조기에 파악할 수 있습니다. 미러-디스크 워크플로우에서 예행 실행을 실행하는 경우 oc-mirror 플러그인 v2는 이미지 세트 내의 모든 이미지를 캐시에서 사용할 수 있는지 확인합니다.

누락된 이미지는 `missing.txt` 파일에 나열됩니다. 미러링 전에 예행 실행이 수행되면 `missing.txt` 및 `mapping.txt` 파일에 동일한 이미지 목록이 포함됩니다.

#### 5.7.1. oc-mirror 플러그인 v2의 예행 실행 수행

이미지를 미러링하지 않고 시험 실행을 수행하여 이미지 세트 구성을 확인합니다. 이렇게 하면 설정이 올바르며 의도하지 않은 변경을 방지할 수 있습니다.

프로세스

테스트 실행을 수행하려면 아래 명령을 실행하고 `--dry-run` 인수를 명령에 추가합니다.

```shell
oc mirror
```

```shell-session
$ oc mirror -c <image_set_config_yaml> file://<oc_mirror_workspace_path> --dry-run --v2
```

다음과 같습니다.

`<image_set_config_yaml>`

생성한 이미지 세트 구성 파일을 지정합니다.

`<oc_mirror_workspace_path>`

작업 공간 경로의 주소를 삽입합니다.

`<mirror_registry_url>`

이미지가 미러링되거나 삭제될 원격 컨테이너 레지스트리의 URL 또는 주소를 삽입합니다.

```shell-session
[INFO]   : :wave: Hello, welcome to oc-mirror
[INFO]   : :gear:  setting up the environment for you...
[INFO]   : :twisted_rightwards_arrows: workflow mode: mirrorToDisk
[INFO]   : :sleuth_or_spy:  going to discover the necessary images...
[INFO]   : :mag: collecting release images...
[INFO]   : :mag: collecting operator images...
[INFO]   : :mag: collecting additional images...
[WARN]   : :warning:  54/54 images necessary for mirroring are not available in the cache.
[WARN]   : List of missing images in : CLID-19/working-dir/dry-run/missing.txt.
please re-run the mirror to disk process
[INFO]   : :page_facing_up: list of all images for mirroring in : CLID-19/working-dir/dry-run/mapping.txt
[INFO]   : mirror time     : 9.641091076s
[INFO]   : :wave: Goodbye, thank you for using oc-mirror
```

검증

생성된 작업 공간 디렉터리로 이동합니다.

```shell-session
$ cd <oc_mirror_workspace_path>
```

생성된 `mapping.txt` 및 `missing.txt` 파일을 검토합니다. 이러한 파일에는 미러링된 모든 이미지 목록이 포함되어 있습니다.

#### 5.7.2. oc-mirror 플러그인 v2 오류 문제 해결

oc-mirror 플러그인 v2는 이제 모든 이미지 미러링 오류를 별도의 파일에 기록하므로 오류를 더 쉽게 추적하고 진단할 수 있습니다.

중요

릴리스 또는 릴리스 구성 요소 이미지를 미러링하는 동안 오류가 발생하면 중요합니다. 이렇게 하면 미러링 프로세스가 즉시 중지됩니다.

Operator, Operator 관련 이미지 또는 추가 이미지 미러링 관련 오류로 인해 미러링 프로세스가 중지되지 않습니다. 미러링은 계속되고 oc-mirror 플러그인 v2는 미러링에 실패한 Operator를 설명하는 `working-dir/logs` 디렉터리에 파일을 저장합니다.

이미지가 미러링되지 않고 해당 이미지가 하나 이상의 Operator 번들의 일부로 미러링되는 경우 oc-mirror 플러그인 v2는 사용자에게 Operator가 불완전함을 알립니다. 그러면 오류의 영향을 받는 Operator 번들이 명확하게 표시됩니다.

프로세스

서버 관련 문제를 확인합니다.

```shell-session
[ERROR]  : [Worker] error mirroring image localhost:55000/openshift/graph-image:latest error: copying image 1/4 from manifest list: trying to reuse blob sha256:edab65b863aead24e3ed77cea194b6562143049a9307cd48f86b542db9eecb6e at destination: pinging container registry localhost:5000: Get "https://localhost:5000/v2/": http: server gave HTTP response to HTTPS client
```

oc-mirror 플러그인 v2 출력 디렉터리에 있는 `working-dir/logs` 폴더에서 `mirroring_error_date_time.log` 파일을 엽니다.

`HTTP 500` 오류, 만료된 토큰 또는 타임아웃과 같이 일반적으로 서버 측 문제를 나타내는 오류 메시지를 찾습니다.

문제가 지속되면 미러링 프로세스 다시 시도하거나 지원에 문의합니다.

Operator의 불완전한 미러링을 확인합니다.

```shell-session
error mirroring image docker://registry.redhat.io/3scale-amp2/zync-rhel9@sha256:8bb6b31e108d67476cc62622f20ff8db34efae5d58014de9502336fcc479d86d (Operator bundles: [3scale-operator.v0.11.12] - Operators: [3scale-operator]) error: initializing source docker://localhost:55000/3scale-amp2/zync-rhel9:8bb6b31e108d67476cc62622f20ff8db34efae5d58014de9502336fcc479d86d: reading manifest 8bb6b31e108d67476cc62622f20ff8db34efae5d58014de9502336fcc479d86d in localhost:55000/3scale-amp2/zync-rhel9: manifest unknown
error mirroring image docker://registry.redhat.io/3scale-amp2/3scale-rhel7-operator-metadata@sha256:de0a70d1263a6a596d28bf376158056631afd0b6159865008a7263a8e9bf0c7d error: skipping operator bundle docker://registry.redhat.io/3scale-amp2/3scale-rhel7-operator-metadata@sha256:de0a70d1263a6a596d28bf376158056631afd0b6159865008a7263a8e9bf0c7d because one of its related images failed to mirror
error mirroring image docker://registry.redhat.io/3scale-amp2/system-rhel7@sha256:fe77272021867cc6b6d5d0c9bd06c99d4024ad53f1ab94ec0ab69d0fda74588e (Operator bundles: [3scale-operator.v0.11.12] - Operators: [3scale-operator]) error: initializing source docker://localhost:55000/3scale-amp2/system-rhel7:fe77272021867cc6b6d5d0c9bd06c99d4024ad53f1ab94ec0ab69d0fda74588e: reading manifest fe77272021867cc6b6d5d0c9bd06c99d4024ad53f1ab94ec0ab69d0fda74588e in localhost:55000/3scale-amp2/system-rhel7: manifest unknown
```

콘솔 또는 로그 파일에서 불완전한 Operator를 나타내는 경고를 확인합니다.

Operator가 불완전한 것으로 표시되는 경우 해당 Operator와 관련된 이미지를 미러링하지 못할 수 있습니다.

누락된 이미지를 수동으로 미러링하거나 미러링 프로세스를 다시 시도합니다.

생성된 클러스터 리소스와 관련된 오류가 있는지 확인합니다. 일부 이미지가 미러링되지 않더라도 oc-mirror v2는 성공적으로 미러링된 이미지에 대한 `IDMS.yaml` 및 `ITMS.yaml` 파일과 같은 클러스터 리소스를 계속 생성합니다.

생성된 파일의 출력 디렉터리를 확인합니다.

이러한 파일이 특정 이미지에 대해 누락된 경우 미러링 프로세스 중에 해당 이미지에 대한 중요한 오류가 발생하지 않았는지 확인합니다.

이러한 단계를 수행하면 문제를 더 잘 진단하고 원활한 미러링을 보장할 수 있습니다.

### 5.8. enclave 지원의 이점

Enclave 지원은 네트워크의 특정 부분에 대한 내부 액세스를 제한합니다. 방화벽 경계를 통한 인바운드 및 아웃바운드 트래픽 액세스를 허용하는 DMZ(비밀화 영역) 네트워크와 달리 enclaves는 방화벽 경계를 통과하지 않습니다.

새로운 enclave 지원 기능은 하나 이상의 중간 연결이 끊긴 네트워크 뒤에서 보호되는 여러 enclav에 미러링이 필요한 시나리오에 적합합니다.

Enclave 지원에는 다음과 같은 이점이 있습니다.

여러 개의 enclaves의 콘텐츠를 미러링하고 단일 내부 레지스트리에 중앙 집중화할 수 있습니다. 일부 고객은 미러링된 컨텐츠에서 보안 검사를 실행하려고 하므로 이 설정을 사용하면 이러한 검사를 모두 한 번에 실행할 수 있습니다. 그런 다음 콘텐츠는 다운스트림으로 미러링되기 전에 비정형됩니다.

각 enclave에 대해 인터넷에서 미러링 프로세스를 다시 시작하지 않고 중앙 집중식 내부 레지스트리에서 직접 콘텐츠를 미러링할 수 있습니다.

네트워크 단계 간의 데이터 전송을 최소화하여 Blob 또는 이미지가 한 단계에서 다른 단계로만 전송되도록 할 수 있습니다.

#### 5.8.1. Enclave 미러링 워크플로

[FIGURE src="/playbooks/wiki-assets/full_rebuild/disconnected_environments/445_OpenShift_Enclave_support_0724.png" alt="Enclave 지원" kind="diagram" diagram_type="semantic_diagram"]
Enclave 지원
[/FIGURE]

_Source: `disconnected_environments.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Disconnected_environments-ko-KR/images/8cc1807490d35edf67c1f15ef8f62d1e/445_OpenShift_Enclave_support_0724.png`_


이전 이미지는 인터넷 연결이 있고 없이 환경을 포함하여 다양한 환경에서 oc-mirror 플러그인을 사용하는 흐름을 간략하게 설명합니다.

인터넷 연결이 있는 환경:

사용자는 oc-mirror 플러그인 v2를 실행하여 온라인 레지스트리의 콘텐츠를 로컬 디스크 디렉터리로 미러링합니다.

미러링된 콘텐츠는 오프라인 환경으로 전송하기 위해 디스크에 저장됩니다.

연결이 끊긴 엔터프라이즈 환경(인터넷 없음):

흐름 1:

사용자는 oc-mirror 플러그인 v2를 실행하여 온라인 환경에서 `enterprise-registry.in` 레지스트리로 전송된 디스크 디렉터리에서 미러링된 콘텐츠를 로드합니다.

흐름 2:

`registries.conf` 파일을 업데이트한 후 사용자는 oc-mirror 플러그인 v2를 실행하여 `enterprise-registry.in` 레지스트리의 콘텐츠를 enclave 환경으로 미러링합니다.

콘텐츠는 enclave로 전송하기 위해 디스크 디렉터리에 저장됩니다.

Enclave 환경 (인터넷 없음):

사용자는 oc-mirror 플러그인 v2를 실행하여 디스크 디렉터리의 콘텐츠를 `enclave-registry.in` 레지스트리로 로드합니다.

이미지는 이러한 환경에서 데이터 흐름을 시각적으로 나타내며 oc-mirror를 사용하여 인터넷 연결 없이 연결이 끊긴 환경을 처리합니다.

#### 5.8.2. enclave에 미러링

enclave에 미러링할 때는 먼저 필요한 이미지를 하나 이상의 enclav에서 엔터프라이즈 중앙 레지스트리로 전송해야 합니다.

중앙 레지스트리는 보안 네트워크, 특히 연결이 끊긴 환경 내에 있으며 공용 인터넷에 직접 연결되지 않습니다. 그러나 사용자는 공용 인터넷에 액세스할 수 있는 환경에서 다음 명령을 실행해야 합니다.

```shell
oc mirror
```

프로세스

연결이 끊긴 환경에서 oc-mirror 플러그인 v2를 실행하기 전에 `registries.conf` 파일을 생성합니다. 파일의 TOML 형식은 이 사양에 설명되어 있습니다.

참고

`$HOME/.config/containers/registries.conf` 또는 `/etc/containers/registries.conf` 아래에 파일을 저장하는 것이 좋습니다.

```plaintext
[[registry]]
location="registry.redhat.io"
[[registry.mirror]]
location="<enterprise-registry.in>"

[[registry]]
location="quay.io"
[[registry.mirror]]
location="<enterprise-registry.in>"
```

미러 아카이브를 생성합니다.

모든 OpenShift Container Platform 콘텐츠를 < `file_path>/enterprise-content` 아래의 아카이브로 수집하려면 다음 명령을 실행합니다.

```shell-session
$ oc mirror --v2 -c isc.yaml file://<file_path>/enterprise-content
```

```yaml
apiVersion: mirror.openshift.io/v2alpha1
kind: ImageSetConfiguration
mirror:
  platform:
    architectures:
      - "amd64"
    channels:
      - name: stable-4.15
        minVersion: 4.15.0
        maxVersion: 4.15.3
```

아카이브가 생성되면 연결이 끊긴 환경으로 전송됩니다. 전송 메커니즘은 oc-mirror 플러그인 v2의 일부가 아닙니다. 엔터프라이즈 네트워크 관리자는 전송 전략을 결정합니다.

경우에 따라 디스크가 물리적으로 한 위치에서 연결 해제되고 연결이 끊긴 환경의 다른 컴퓨터에 연결되어 있음을 전송이 수동으로 수행됩니다. 다른 경우에는 FTP(Secure File Transfer Protocol) 또는 기타 프로토콜이 사용됩니다.

아카이브 전송이 완료되면 다음 예에 설명된 대로 관련 아카이브 콘텐츠를 레지스트리(예의 `entrerpise_registry.in`)에 미러링하기 위해 oc-mirror 플러그인 v2를 다시 실행할 수 있습니다.

```shell-session
$ oc mirror --v2 -c isc.yaml --from file://<disconnected_environment_file_path>/enterprise-content docker://<enterprise_registry.in>/
```

다음과 같습니다.

`--from` 은 아카이브가 포함된 폴더를 가리킵니다. `file://` 로 시작합니다.

다음 명령는 미러링의 대상이 최종 인수입니다. 이는 docker 레지스트리이기 때문입니다.

```shell
docker://
```

`-c` (`--config`)는 필수 인수입니다. oc-mirror 플러그인 v2가 결국 아카이브의 하위 부분만 레지스트리에 미러링할 수 있습니다. 하나의 아카이브에는 여러 OpenShift Container Platform 릴리스가 포함될 수 있지만 연결이 끊긴 환경 또는 enclave는 몇 개만 미러링할 수 있습니다.

enclave에 미러링할 콘텐츠를 설명하는 `imageSetConfig` YAML 파일을 준비합니다.

```yaml
apiVersion: mirror.openshift.io/v2alpha1
kind: ImageSetConfiguration
mirror:
  platform:
    architectures:
      - "amd64"
    channels:
      - name: stable-4.15
        minVersion: 4.15.2
        maxVersion: 4.15.2
```

연결이 끊긴 레지스트리에 액세스할 수 있는 머신에서 oc-mirror 플러그인 v2를 실행해야 합니다. 이전 예에서 연결이 끊긴 환경 `enterprise-registry.in` 에 액세스할 수 있습니다.

그래프 URL 업데이트

`graph:true` 를 사용하는 경우 oc-mirror 플러그인 v2는 `cincinnati` API 끝점에 도달하려고 시도합니다. 이 환경의 연결이 끊어지면 `UPDATE_URL_OVERRIDE` 환경 변수 OSUS(OpenShift Update Service)의 URL을 참조하도록 환경 변수 UPDATE_URL_OVERRIDE를 내보내야 합니다.

```shell-session
$ export UPDATE_URL_OVERRIDE=https://<osus.enterprise.in>/graph
```

OpenShift 클러스터에서 OSUS를 설정하는 방법에 대한 자세한 내용은 "OpenShift Update Service를 사용하여 연결이 끊긴 환경에서 클러스터 업그레이드"를 참조하십시오.

참고

OpenShift Container Platform EUS (Extended Update Support) 버전 간에 업데이트할 때 현재 버전과 대상 버전 간의 중간 마이너 버전에 대한 이미지도 포함해야 합니다.

oc-mirror 플러그인 v2가 항상 이 요구 사항을 자동으로 감지하지는 않을 수 있으므로 Red Hat OpenShift Container Platform Update Graph 페이지를 확인하여 필요한 중간 버전을 확인합니다.

Update Graph 페이지를 사용하여 애플리케이션에서 제안된 중간 마이너 버전을 찾고 oc-mirror 플러그인 v2를 사용할 때 `ImageSetConfiguration` 파일에 이러한 버전을 포함합니다.

enclave의 엔터프라이즈 레지스트리에서 미러 아카이브를 생성합니다.

`enclave1` 용 아카이브를 준비하기 위해 사용자는 해당 enclave에 특정한 `imageSetConfiguration` 을 사용하여 엔터프라이즈 연결이 끊긴 환경에서 oc-mirror 플러그인 v2를 실행합니다. 이렇게 하면 enclave에 필요한 이미지만 미러링됩니다.

```shell-session
$ oc mirror --v2 -c isc-enclave.yaml
file:///disk-enc1/
```

이 작업은 모든 OpenShift Container Platform 콘텐츠를 아카이브로 수집하고 디스크에 아카이브를 생성합니다.

아카이브가 생성되면 `enclave1` 네트워크로 전송됩니다. 전송 메커니즘은 oc-mirror 플러그인 v2의 책임이 아닙니다.

enclave 레지스트리에 콘텐츠를 미러링

아카이브 전송이 완료되면 사용자는 관련 아카이브 콘텐츠를 레지스트리에 미러링하기 위해 oc-mirror 플러그인 v2를 다시 실행할 수 있습니다.

```shell-session
$ oc mirror --v2 -c isc-enclave.yaml --from file://local-disk docker://registry.enc1.in
```

`enclave1` 의 OpenShift Container Platform 클러스터 관리자는 이제 해당 클러스터를 설치하거나 업그레이드할 준비가 되었습니다.

### 5.9. oc-mirror 플러그인 v2 지원 프록시 설정

oc-mirror 플러그인 v2는 프록시가 구성된 환경에서 작동할 수 있습니다. 플러그인은 시스템 프록시 설정을 사용하여 OpenShift Container Platform, Operator 카탈로그 및 `additionalImages` 레지스트리의 이미지를 검색할 수 있습니다.

추가 리소스

OpenShift Update Service를 사용하여 연결이 끊긴 환경에서 클러스터 업데이트

배포 레지스트리에서 스토리지 정리 문제 해결

### 5.10. oc-mirror 플러그인 v2에서 이미지 시그니처 미러링 및 검증

OpenShift Container Platform 4.19부터 oc-mirror 플러그인 v2는 컨테이너 이미지의 상호 서명 미러링 및 확인 기능을 지원합니다.

#### 5.10.1. oc-mirror 플러그인 v2의 서명 미러링 활성화

기본적으로 서명 미러링은 비활성화되어 있습니다. 아래 명령에 `--remove-signatures=false` 플래그를 설정하여 모든 이미지에 서명 미러링을 활성화할 수 있습니다.

```shell
oc mirror
```

활성화하면 oc-mirror 플러그인 v2는 다음 이미지에 대해 `Sigstore` 태그 기반 서명을 미러링합니다.

OpenShift Container Platform 릴리스 이미지

Operator 이미지

추가 이미지

Helm 차트

참고

구성 파일을 제공하지 않으면 `--remove-signatures=false` 플래그가 사용될 때 oc-mirror 플러그인 v2는 기본적으로 모든 이미지에 대한 서명 미러링을 활성화합니다.

사용자 지정 구성 디렉터리를 지정하려면 `--registries.d` 플래그를 사용합니다.

자세한 내용은 `containers-registries.d(5)` 설명서를 참조하십시오.

프로세스

모든 이미지에 서명 미러링을 활성화하려면 다음 명령을 실행합니다.

```shell-session
$ oc mirror --remove-signatures=false
```

전송 프로토콜, 레지스트리, 네임스페이스 또는 이미지와 같은 특정 요소에 대한 서명 미러링을 활성화하거나 비활성화하려면 다음 단계를 사용하십시오.

`$HOME/.config/containers/registries.d/` 또는 `/etc/containers/registries.d/` 디렉터리에 YAML 파일을 생성합니다.

다음 예와 같이 `use-sigstore-attachments` 매개변수를 지정하고 제어하려는 특정 요소에서 `true` 또는 `false` 로 설정합니다.

```yaml
# ...
docker:
  quay.io:
    use-sigstore-attachments: false
# ...
```

```yaml
# ...
default-docker:
  use-sigstore-attachments: true
# ...
```

#### 5.10.2. oc-mirror 플러그인 v2에 대한 서명 확인 활성화

OpenShift Container Platform 4.19부터 oc-mirror 플러그인 v2는 기본적으로 비활성화된 서명 확인을 지원합니다. 활성화하면 플러그인은 컨테이너 이미지가 서명과 일치하는지 확인하여 해당 이미지가 변경되지 않았으며 신뢰할 수 있는 소스에서 가져옵니다. 서명 불일치가 감지되면 미러링 워크플로가 실패합니다.

프로세스

모든 이미지에 대한 서명 확인을 활성화하려면 다음 명령을 실행합니다.

```shell-session
$ oc mirror --secure-policy=true
```

전송 프로토콜, 레지스트리, 네임스페이스 또는 이미지와 같은 특정 요소에 대한 서명 확인을 활성화하거나 비활성화하려면 다음 단계를 따르십시오.

`$HOME/.config/containers/` 또는 `/etc/containers/` 디렉터리에 `policy.json` 파일을 생성합니다.

참고

정책 구성 파일이 기본 디렉터리 외부에 있는 경우 아래 명령과 함께 `--policy` 플래그를 사용하여 해당 경로를 지정할 수 있습니다.

```shell
oc mirror
```

자세한 내용은 `containers-policy.json(5)` 를 참조하십시오.

적절한 정책 구성을 사용하여 원하는 범위(예: 레지스트리 또는 이미지)에 대한 확인 규칙을 정의합니다. 각 요소에 원하는 규칙을 지정하여 확인 요구 사항을 설정할 수 있습니다.

예: 특정 이미지에 대해서만 확인을 활성화하고 다른 모든 이미지를 거부합니다.

```plaintext
{
  "default": [{"type": "reject"}],
  "transports": {
    "docker": {
      "hostname:5000/myns/sigstore-signed-image": [
        {
          "type": "sigstoreSigned",
          "keyPath": "/path/to/sigstore-pubkey.pub",
          "signedIdentity": {"type": "matchRepository"}
        }
      ]
    }
  }
}
```

### 5.11. Operator 카탈로그에서 필터링이 작동하는 방법

oc-mirror 플러그인 v2는 `imageSetConfig` 의 정보를 처리하여 미러링을 위한 번들 목록을 선택합니다.

oc-mirror 플러그인 v2는 미러링을 위한 번들을 선택할 때 GVK(그룹 버전 종류) 또는 번들 종속성을 유추하지 않고 미러링 세트에서 생략합니다. 대신 사용자 지침을 엄격하게 준수합니다. 필요한 종속 패키지 및 해당 버전을 명시적으로 지정해야 합니다.

| ImageSetConfig Operator 필터링 | 예상되는 번들 버전 |
| --- | --- |
| 시나리오 1 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.10 [/CODE] | 카탈로그의 각 패키지에 대해 해당 패키지의 각 채널의 헤드 버전에 해당하는 하나의 번들입니다. |
| 시나리오 2 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.10 full: true [/CODE] | 지정된 카탈로그의 모든 채널의 모든 번들입니다. |
| 시나리오 3 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.10 packages: - name: compliance-operator [/CODE] | 해당 패키지의 각 채널의 헤드 버전에 해당하는 하나의 번들입니다. |
| 시나리오 4 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.10 full: true - packages: - name: elasticsearch-operator [/CODE] | 지정된 패키지에 대한 모든 채널의 모든 번들입니다. |
| 시나리오 5 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator minVersion: 5.6.0 [/CODE] | `minVersion` 에서 해당 패키지의 채널 헤드까지 모든 채널의 모든 번들입니다. |
| 시나리오 6 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator maxVersion: 6.0.0 [/CODE] | 해당 패키지의 `maxVersion` 보다 낮은 모든 채널의 모든 번들입니다. |
| 시나리오 7 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator minVersion: 5.6.0 maxVersion: 6.0.0 [/CODE] | 해당 패키지의 `minVersion` 과 `maxVersion` 사이의 모든 채널의 모든 번들입니다. 여러 채널이 필터링에 포함되어 있어도 채널 헤드가 포함되지 않습니다. |
| 시나리오 8 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator channels - name: stable [/CODE] | 해당 패키지의 선택한 채널의 헤드 번들입니다. 필터링된 채널이 기본값이 아닌 경우 `defaultChannel` 필드를 사용해야 합니다. |
| 시나리오 9 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.10 full: true - packages: - name: elasticsearch-operator channels: - name: 'stable-v0' [/CODE] | 지정된 패키지 및 채널에 대한 모든 번들입니다. 필터링된 채널이 기본값이 아닌 경우 `defaultChannel` 을 사용해야 합니다. |
| 시나리오 10 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator channels - name: stable - name: stable-5.5 [/CODE] | 해당 패키지의 선택한 각 채널에 대한 헤드 번들입니다. |
| 시나리오 11 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator channels - name: stable minVersion: 5.6.0 [/CODE] | 해당 패키지의 선택한 채널 내에서 `minVersion` 부터 채널 헤드까지 모든 버전을 사용합니다. 필터링된 채널이 기본값이 아닌 경우 `defaultChannel` 필드를 사용해야 합니다. |
| 시나리오 12 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator channels - name: stable maxVersion: 6.0.0 [/CODE] | 해당 패키지의 선택한 채널 내에서 모든 버전 최대 `maxVersion` . 필터링에 여러 채널이 포함되어 있어도 채널 헤드는 포함되지 않습니다. 이 필터링이 여러 헤드가 있는 채널로 이어지는 경우 오류가 표시될 수 있습니다. 필터링된 채널이 기본값이 아닌 경우 `defaultChannel` 필드를 사용해야 합니다. |
| 시나리오 13 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator channels - name: stable minVersion: 5.6.0 maxVersion: 6.0.0 [/CODE] | 해당 패키지의 선택한 채널 내에서 `minVersion` 과 `maxVersion` 사이의 모든 버전 . 여러 채널이 필터링에 포함되어 있어도 채널 헤드는 포함되지 않습니다. 이 필터링이 여러 헤드가 있는 채널로 이어지는 경우 오류가 표시될 수 있습니다. 필터링된 채널이 기본값이 아닌 경우 `defaultChannel` 필드를 사용해야 합니다. |
| 시나리오 14 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator channels - name: stable minVersion: 5.6.0 maxVersion: 6.0.0 [/CODE] | 이 시나리오를 사용하지 마십시오. `minVersion` 또는 `maxVersion` 으로 패키지를 필터링하는 것은 허용되지 않습니다. |
| 시나리오 15 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 packages: - name: compliance-operator channels - name: stable minVersion: 5.6.0 maxVersion: 6.0.0 [/CODE] | 이 시나리오를 사용하지 마십시오. `full:true` 및 `minVersion` 또는 `maxVersion` 을 사용하여 필터링할 수 없습니다. |
| 시나리오 16 [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.15 full: true packages: - name: compliance-operator channels - name: stable minVersion: 5.6.0 maxVersion: 6.0.0 [/CODE] | 이 시나리오를 사용하지 마십시오. `full:true` 및 `minVersion` 또는 `maxVersion` 을 사용하여 필터링할 수 없습니다. |

### 5.12. oc-mirror 플러그인 v2의 이미지 세트 구성 매개변수

oc-mirror 플러그인 v2에는 미러링할 이미지를 정의하는 이미지 세트 구성 파일이 필요합니다. 다음 표에는 `ImageSetConfiguration` 리소스에 사용 가능한 매개변수가 나열되어 있습니다.

참고

미러링을 위한 번들을 선택할 때 oc-mirror 플러그인 v2는 GVK(그룹/버전/종류) 및 번들 종속성을 자동으로 감지하지 않습니다. `ImageSetConfiguration` 파일에서 필요한 Operator, 해당 채널 및 Operator 버전을 명시적으로 지정해야 합니다. 자세한 내용은 "opm CLI 참조"를 참조하십시오.

`minVersion` 및 `maxVersion` 속성을 사용하여 특정 Operator 버전 범위를 필터링하면 여러 채널 헤드 오류가 발생할 수 있습니다. 오류 메시지는 `여러 채널 헤드` 가 있음을 나타냅니다. 필터가 적용되면 Operator의 업데이트 그래프가 잘립니다.

OLM에는 모든 Operator 채널에 정확히 하나의 엔드 포인트, 즉 최신 버전의 Operator가 있는 업데이트 그래프를 형성하는 버전이 포함되어 있어야 합니다. 필터 범위가 적용되면 해당 그래프는 두 개 이상의 개별 그래프 또는 두 개 이상의 끝점이 있는 그래프로 전환할 수 있습니다.

이 오류를 방지하려면 최신 버전의 Operator를 필터링하지 마십시오. Operator에 따라 오류가 계속 실행되는 경우 `maxVersion` 속성을 늘리거나 `minVersion` 속성을 줄여야 합니다. 모든 Operator 그래프는 다를 수 있으므로 오류가 해결될 때까지 이러한 값을 조정해야 할 수 있습니다.

| 매개변수 | 설명 | 값 |
| --- | --- | --- |
| `apiVersion` | `ImageSetConfiguration` 콘텐츠의 API 버전입니다. | 문자열 예: `mirror.openshift.io/v2alpha1` |
| `archiveSize` | 이미지 세트 내의 각 아카이브 파일의 최대 크기(GiB)입니다. | 정수 예: `4` |
| `kubeVirtContainer` | `true` 로 설정하면 HyperShift KubeVirt CoreOS 컨테이너의 이미지를 포함합니다. | 부울 예 `ImageSetConfiguration` 파일: [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] apiVersion: mirror.openshift.io/v2alpha1 kind: ImageSetConfiguration mirror: platform: channels: - name: stable-4.16 minVersion: 4.16.0 maxVersion: 4.16.0 kubeVirtContainer: true [/CODE] |
| `mirror` | 이미지 세트의 구성입니다. | 개체 |
| `mirror.additionalImages` | 이미지 세트의 추가 이미지 구성입니다. | 개체 배열 예제: [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] additionalImages: - name: registry.redhat.io/ubi8/ubi:latest [/CODE] |
| `mirror.additionalImages.name` | 미러링할 이미지의 태그 또는 다이제스트입니다. | 문자열 예: `registry.redhat.io/ubi8/ubi:latest` |
| `mirror.blockedImages` | 미러링을 차단할 태그 또는 다이제스트(SHA)가 있는 이미지 목록입니다. | 문자열 배열 예: `docker.io/ Cryostat/alpine` |
| `mirror.helm` | 이미지 세트의 helm 구성입니다. oc-mirror 플러그인은 수동으로 수정된 `values.yaml` 파일이 있는 helm 차트를 지원하지 않습니다. | 개체 |
| `mirror.helm.local` | 미러링할 로컬 helm 차트입니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] local: - name: podinfo path: /test/podinfo-5.0.0.tar.gz [/CODE] |
| `mirror.helm.local.charts.imagePaths` | 로컬 helm 차트 내부의 컨테이너 이미지의 사용자 정의 경로입니다. + 참고 `oc-mirror` 는 잘 알려진 경로를 검색하여 helm 차트에서 컨테이너 이미지를 탐지하고 미러링합니다. 이 필드를 사용하여 사용자 정의 경로를 지정할 수도 있습니다. + 참고 런타임 시 Operator 컨트롤러에서 동적으로 배포하는 피연산자 이미지는 일반적으로 컨트롤러의 배포 템플릿 내의 환경 변수에서 참조합니다. `oc-mirror` 가 이러한 환경 변수에 액세스할 수 있는 동안 OpenShift Container Platform 4.20 이전에는 이미지 이외의 참조(예: 로그 수준)를 포함한 모든 값을 미러링하려고 시도하여 오류가 발생했습니다. 이번 업데이트를 통해 이러한 환경 변수에서 참조하는 컨테이너 이미지만 미러링할 수 있습니다. | 문자열 배열입니다. 예: `"- {.spec.template.spec.custom[*].image}"` . |
| `mirror.helm.local.name` | 미러링할 로컬 helm 차트의 이름입니다. | 문자열. 예: `podinfo` . |
| `mirror.helm.local.path` | 미러링할 로컬 helm 차트의 경로입니다. | 문자열. 예: `/test/podinfo-5.0.0.tar.gz` . |
| `mirror.helm.repositories` | 미러링할 원격 helm 리포지토리입니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] repositories: - name: podinfo url: https://example.github.io/podinfo charts: - name: podinfo version: 5.0.0 imagePaths: - "{.spec.template.spec.custom[*].image}" [/CODE] |
| `mirror.helm.repositories.name` | 미러링할 helm 저장소 이름입니다. | 문자열. 예: `podinfo` . |
| `mirror.helm.repositories.url` | 미러링할 helm 리포지토리의 URL입니다. | 문자열. 예: `https://example.github.io/podinfo` . |
| `mirror.helm.repositories.charts` | 미러링할 원격 helm 차트입니다. | 개체의 배열입니다. |
| `mirror.helm.repositories.charts.name` | 미러링할 helm 차트의 이름입니다. | 문자열. 예: `podinfo` . |
| `mirror.helm.repositories.charts.imagePaths` | helm 차트 내부의 컨테이너 이미지의 사용자 정의 경로입니다. + 참고 `oc-mirror` 는 잘 알려진 경로를 검색하여 helm 차트에서 컨테이너 이미지를 탐지하고 미러링합니다. 이 필드를 사용하여 사용자 정의 경로를 지정할 수도 있습니다. + 참고 런타임 시 Operator 컨트롤러에서 동적으로 배포하는 피연산자 이미지는 일반적으로 컨트롤러의 배포 템플릿 내의 환경 변수에서 참조합니다. `oc-mirror` 가 이러한 환경 변수에 액세스할 수 있는 동안 OpenShift Container Platform 4.20 이전에는 이미지 이외의 참조(예: 로그 수준)를 포함한 모든 값을 미러링하려고 시도하여 오류가 발생했습니다. 이번 업데이트를 통해 이러한 환경 변수에서 참조하는 컨테이너 이미지만 미러링할 수 있습니다. | 문자열 배열입니다. 예: `"- {.spec.template.spec.custom[*].image}"` . |
| `mirror.operators` | 이미지 세트의 Operator 구성 | 개체 배열 예제: [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:4.20 packages: - name: elasticsearch-operator minVersion: '2.4.0' [/CODE] |
| `mirror.operators.catalog` | 이미지 세트에 포함할 Operator 카탈로그입니다. | 문자열 예: `registry.redhat.io/redhat/redhat-operator-index:v4.15` |
| `mirror.operators.full` | `true` 인 경우 전체 카탈로그, Operator 패키지 또는 Operator 채널을 다운로드합니다. | 부울 값은 `false` 입니다. |
| `mirror.operators.packages` | Operator 패키지 구성입니다. | 개체 배열 예제: [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:4.20 packages: - name: elasticsearch-operator minVersion: '5.2.3-31' [/CODE] |
| `mirror.operators.packages.name` | 이미지 세트에 포함할 Operator 패키지 이름입니다. | 문자열 예: `elasticsearch-operator` |
| `mirror.operators.packages.channels` | Operator 패키지 채널 구성 | 개체 |
| `mirror.operators.packages.channels.name` | 이미지 세트에 포함할 Operator 채널 이름은 패키지 내에서 고유합니다. | 문자열 Eample: `fast` 또는 `stable-v4.15` |
| `mirror.operators.packages.channels.maxVersion` | Operator의 가장 높은 버전은 존재하는 모든 채널에서 미러링됩니다. | 문자열 예: `5.2.3-31` |
| `mirror.operators.packages.channels.minVersion` | 존재하는 모든 채널에 미러링할 가장 낮은 버전의 Operator | 문자열 예: `5.2.3-31` |
| `mirror.operators.packages.maxVersion` | 존재하는 모든 채널에 미러링할 Operator의 가장 높은 버전입니다. | 문자열 예: `5.2.3-31` |
| `mirror.operators.packages.minVersion` | 존재하는 모든 채널에 미러링할 Operator의 가장 낮은 버전입니다. | 문자열 예: `5.2.3-31` |
| `mirror.operators.targetCatalog` | 참조된 카탈로그를 미러링하는 대체 이름 및 선택적 네임스페이스 계층 구조 | 문자열 예: `my-namespace/my-operator-catalog` |
| `mirror.operators.targetCatalogSourceTemplate` | oc-mirror 플러그인 v2에서 생성한 catalogSource 사용자 정의 리소스를 완료하는 데 사용할 템플릿의 디스크 경로입니다. | 문자열 예: `/tmp/catalog-source_template.yaml` 템플릿 파일의 예: [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] apiVersion: operators.coreos.com/v1alpha1 kind: CatalogSource metadata: name: discarded namespace: openshift-marketplace spec: image: discarded sourceType: grpc updateStrategy: registryPoll: interval: 30m0s [/CODE] |
| `mirror.operators.targetTag` | `targetName` 또는 `targetCatalog` 에 추가할 대체 태그입니다. | 문자열 예: `v1` |
| `mirror.platform` | 이미지 세트의 플랫폼 구성입니다. | 개체 |
| `mirror.platform.architectures` | 미러링할 플랫폼 릴리스 페이로드의 아키텍처입니다. | 문자열 배열은 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] architectures: - amd64 - arm64 - multi - ppc64le - s390x [/CODE] 기본값은 `amd64` 입니다. 값 `multi` 를 사용하면 사용 가능한 모든 아키텍처에 대해 미러링이 지원되므로 개별 아키텍처를 지정할 필요가 없습니다. |
| `mirror.platform.channels` | 이미지 세트의 플랫폼 채널 구성입니다. | 오브젝트 배열은 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] channels: - name: stable-4.12 - name: stable-4.20 [/CODE] |
| `mirror.platform.channels.full` | `true` 인 경우 `minVersion` 을 채널의 첫 번째 릴리스로 설정하고 `maxVersion` 을 채널의 마지막 릴리스로 설정합니다. | 부울 값 기본값은 `false` 입니다. |
| `mirror.platform.channels.name` | 릴리스 채널의 이름 | 문자열 예: `stable-4.15` |
| `mirror.platform.channels.minVersion` | 미러링할 참조된 플랫폼의 최소 버전입니다. | 문자열 예: `4.12.6` |
| `mirror.platform.channels.maxVersion` | 참조된 플랫폼의 가장 높은 버전을 미러링합니다. | 문자열 예: `4.15.1` |
| `mirror.platform.channels.shortestPath` | 경로 미러링 또는 전체 범위 미러링을 전환합니다. | 부울 값 기본값은 `false` 입니다. |
| `mirror.platform.channels.type` | 미러링할 플랫폼의 유형 | 문자열 예: `ocp` 또는 `okd` . 기본값은 `ocp` 입니다. |
| `mirror.platform.graph` | OSUS 그래프가 이미지 세트에 추가되고 나중에 미러에 게시되는지 여부를 나타냅니다. | 부울 값 기본값은 `false` 입니다. |
| `mirror.operators.packages.defaultChannel` | 필터링에서 기본 채널을 제외할 때 정의해야 합니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] mirror: operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20 packages: - name: rhods-operator defaultChannel: fast channels: - name: fast [/CODE] |

#### 5.12.1. DeleteImageSetConfiguration 매개변수

oc-mirror 플러그인 v2와 함께 이미지 제거를 사용하려면 미러 레지스트리에서 삭제할 이미지를 정의하는 `DeleteImageSetConfiguration.yaml` 구성 파일을 사용해야 합니다. 다음 표에는 `DeleteImageSetConfiguration` 리소스에 사용 가능한 매개변수가 나열되어 있습니다.

| 매개변수 | 설명 | 값 |
| --- | --- | --- |
| `apiVersion` | `DeleteImageSetConfiguration` 콘텐츠의 API 버전입니다. | 문자열 예: `mirror.openshift.io/v2alpha1` |
| `삭제` | 삭제할 이미지 세트의 구성입니다. | 개체 |
| `delete.additionalImages` | 삭제 이미지 세트의 추가 이미지 구성입니다. | 오브젝트 배열은 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] additionalImages: - name: registry.redhat.io/ubi8/ubi:latest [/CODE] |
| `delete.additionalImages.name` | 삭제할 이미지의 태그 또는 다이제스트입니다. | 문자열 예: `registry.redhat.io/ubi8/ubi:latest` |
| `delete.operators` | 삭제 이미지 세트의 Operator 구성입니다. | 오브젝트 배열은 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:{product-version} packages: - name: elasticsearch-operator minVersion: '2.4.0' [/CODE] |
| `delete.operators.catalog` | 삭제 이미지 세트에 포함할 Operator 카탈로그입니다. | 문자열 예: `registry.redhat.io/redhat/redhat-operator-index:v4.15` |
| `delete.operators.full` | true인 경우 전체 카탈로그, Operator 패키지 또는 Operator 채널을 삭제합니다. | 부울 값 기본값은 `false` 입니다. |
| `delete.operators.packages` | Operator 패키지 구성 | 오브젝트 배열은 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:{product-version} packages: - name: elasticsearch-operator minVersion: '5.2.3-31' [/CODE] |
| `delete.operators.packages.name` | 삭제 이미지 세트에 포함할 Operator 패키지 이름입니다. | 문자열 예: `elasticsearch-operator` |
| `delete.operators.packages.channels` | Operator 패키지 채널 구성 | 개체 |
| `delete.operators.packages.channels.name` | 삭제 이미지 세트에 포함할 Operator 채널 이름(패키지 내에서 고유함)입니다. | 문자열 예: `fast` 또는 `stable-v4.15` |
| `delete.operators.packages.channels.maxVersion` | 선택한 채널 내에서 삭제할 Operator의 가장 높은 버전입니다. | 문자열 예: `5.2.3-31` |
| `delete.operators.packages.channels.minVersion` | 존재하는 선택 범위 내에서 삭제할 Operator의 가장 낮은 버전입니다. | 문자열 예: `5.2.3-31` |
| `delete.operators.packages.maxVersion` | 존재하는 모든 채널에서 삭제할 Operator의 가장 높은 버전입니다. | 문자열 예: `5.2.3-31` |
| `delete.operators.packages.minVersion` | 존재하는 모든 채널에서 삭제할 Operator의 가장 낮은 버전입니다. | 문자열 예: `5.2.3-31` |
| `delete.platform` | 이미지 세트의 플랫폼 구성 | 개체 |
| `delete.platform.architectures` | 삭제할 플랫폼 릴리스 페이로드의 아키텍처입니다. | 문자열 배열은 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] architectures: - amd64 - arm64 - multi - ppc64le - s390x [/CODE] 기본값은 `amd64` 입니다. |
| `delete.platform.channels` | 이미지 세트의 플랫폼 채널 구성입니다. | 개체 배열 예제: [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] channels: - name: stable-4.12 - name: stable-4.20 [/CODE] |
| `delete.platform.channels.full` | `true` 인 경우 `minVersion` 을 채널의 첫 번째 릴리스로 설정하고 `maxVersion` 을 채널의 마지막 릴리스로 설정합니다. | 부울 값 기본값은 `false` 입니다. |
| `delete.platform.channels.name` | 릴리스 채널의 이름 | 문자열 예: `stable-4.15` |
| `delete.platform.channels.minVersion` | 삭제할 참조 플랫폼의 최소 버전입니다. | 문자열 예: `4.12.6` |
| `delete.platform.channels.maxVersion` | 삭제할 가장 높은 버전의 참조 플랫폼입니다. | 문자열 예: `4.15.1` |
| `delete.platform.channels.shortestPath` | 가장 짧은 경로를 삭제하고 전체 범위를 삭제하는 사이를 전환합니다. | 부울 값 기본값은 `false` 입니다. |
| `delete.platform.channels.type` | 삭제할 플랫폼의 유형 | 문자열 예: `ocp` 또는 `okd` 기본값은 `ocp` 입니다. |
| `delete.platform.graph` | 미러 레지스트리에서도 OSUS 그래프가 삭제되었는지 여부를 확인합니다. | 부울 값 기본값은 `false` 입니다. |

추가 리소스

opm CLI 참조

### 5.13. oc-mirror 플러그인 v2에 대한 명령 참조

다음 표에서는 oc-mirror 플러그인 v2의 하위 명령 및 플래그를 설명합니다.

```shell
oc mirror
```

| 하위 명령 | 설명 |
| --- | --- |
| `help` | 모든 하위 명령에 대한 도움말 표시 |
| `version` | oc-mirror 버전을 출력합니다. |
| `삭제` | 원격 레지스트리 및 로컬 캐시의 이미지를 삭제합니다. |

| 플래그 | 설명 |
| --- | --- |
| `--authfile` | 인증 파일의 문자열 경로를 표시합니다. 기본값은 `${XDG_RUNTIME_DIR}/containers/auth.json` 입니다. |
| `-c` , `--config` `<string>` | 이미지 세트 구성 파일의 경로를 지정합니다. |
| `--cache-dir <string>` | 이 플래그를 사용하여 oc-mirror 플러그인이 미러링 작업 중에 사용할 이미지 Blob 및 매니페스트의 영구 캐시를 저장하는 디렉터리를 지정합니다. oc-mirror 플러그인은 `disk-to-mirror` 및 `mirror-to-disk` 워크플로의 캐시를 사용하지만 `mirror-to-mirror` 워크플로우에서 캐시를 사용하지 않습니다. 플러그인은 캐시를 사용하여 증분 미러링을 수행하고 변경되지 않은 이미지를 다시 미러링하지 않으므로 시간을 절약하고 네트워크 대역폭 사용량을 줄입니다. 기본 캐시 디렉터리는 `$HOME` 입니다. 자세한 내용은 "-cache-dir 및 --workspace 플래그 수락"을 참조하십시오. |
| `--dest-tls-verify` | HTTPS가 필요하며 컨테이너 레지스트리 또는 데몬에 액세스할 때 인증서를 확인합니다. 기본값은 `true` 입니다. |
| `--dry-run` | 이미지를 미러링하지 않고 작업을 출력합니다. |
| `--from <string>` | oc-mirror 플러그인 v2를 실행하여 대상 레지스트리를 로드하여 생성된 이미지 세트 아카이브의 경로를 지정합니다. |
| `-h` , `--help` | 도움말 표시 |
| `--image-timeout 기간` | 이미지 미러링에 대한 제한 시간입니다. 기본값은 10m0s입니다. 유효한 시간 단위는 `ns` , `us` 또는 `µs` , `ms` , `s` , `m` , `h` 입니다. |
| `--log-level <string>` | 문자열 로그 수준을 표시합니다. 지원되는 값에는 info, debug, trace, error가 포함됩니다. 기본값은 `info` 입니다. |
| `-p` , `--port` | oc-mirror 플러그인 v2 로컬 스토리지 인스턴스에서 사용하는 HTTP 포트를 결정합니다. 기본값은 `55000` 입니다. |
| `--parallel-images <unit>` | 병렬로 미러링된 이미지 수를 지정합니다. 값은 1-10의 범위에 있어야 합니다. 기본값은 `4` 입니다. |
| `--parallel-layers <unit>` | 병렬로 미러링된 이미지 계층 수를 지정합니다. 값은 1-10의 범위에 있어야 합니다. 기본값은 `5` 입니다. |
| `--max-nested-paths <int>` | 중첩된 경로를 제한하는 대상 레지스트리의 최대 중첩된 경로 수를 지정합니다. 기본값은 `0` 입니다. |
| `--secure-policy` | 기본값은 `false` 입니다. 기본값이 아닌 값을 설정하면 명령은 서명 확인을 위한 보안 정책인 서명 확인을 활성화합니다. |
| `--since` | 지정된 날짜 이후의 모든 새 콘텐츠를 포함합니다(format: `yyyy-mm-dd` ). 제공되지 않으면 이전 미러링 이후 새 콘텐츠가 미러링됩니다. |
| `--src-tls-verify` | HTTPS가 필요하며 컨테이너 레지스트리 또는 데몬에 액세스할 때 인증서를 확인합니다. |
| `--strict-archive` | 기본값은 `false` 입니다. 값을 설정하면 이 명령은 `imageSetConfig` CR(사용자 정의 리소스)에 설정된 `archiveSize` 보다 엄격하게 적은 아카이브를 생성합니다. 보관 중인 파일이 `archiveSize` (GB)를 초과하는 경우 미러링은 오류가 발생했습니다. |
| `-v` , `--version` | oc-mirror 플러그인 v2의 버전을 표시합니다. |
| `--workspace` | `--workspace` 플래그를 사용하여 oc-mirror 플러그인이 `ImageDigestMirrorSet` 및 `ImageTagMirrorSet` 매니페스트와 같이 미러링 작업 중에 생성하는 작업 파일을 저장하는 디렉터리를 지정할 수 있습니다. 이 디렉터리를 사용하여 생성된 구성을 클러스터에 적용하고 미러링 작업을 반복합니다. 자세한 내용은 "-cache-dir 및 --workspace 플래그 수락"을 참조하십시오. |
| `--retry-delay duration` | 두 번 재시도 사이의 지연 시간입니다. 기본값은 `1s` 입니다. |
| `--retry-times <int>` | 재시도 횟수입니다. 기본값은 `2` 입니다. |
| `--rootless-storage-path <string>` | 기본 컨테이너 루트리스 스토리지 경로(일반적으로 `etc/containers/storage.conf` )를 덮어씁니다. |
| `--remove-signatures` | 소스 이미지의 서명을 복사하지 않습니다. |
| `--registries.d` | 레지스트리 구성 파일이 포함된 디렉터리를 지정합니다. |
| `--secure-policy=true` | 모든 이미지에 대한 서명 확인을 활성화합니다. |
| `--policy` | 서명 확인 정책 파일의 경로를 지정합니다. |

#### 5.13.1. 이미지 삭제를 위한 명령 참조

다음 표에서는 이미지 삭제를 위한 하위 명령 및 플래그를 설명합니다.

```shell
oc mirror
```

| 하위 명령 | 설명 |
| --- | --- |
| `--authfile <string>` | 인증 파일의 경로입니다. 기본값은 `${XDG_RUNTIME_DIR}/containers/auth.json` 입니다. |
| `--cache-dir <string>` | 이 플래그를 사용하여 oc-mirror 플러그인이 미러링 작업 중에 사용할 이미지 Blob 및 매니페스트의 영구 캐시를 저장하는 디렉터리를 지정합니다. oc-mirror 플러그인은 `disk-to-mirror` 및 `mirror-to-disk` 워크플로의 캐시를 사용하지만 `mirror-to-mirror` 워크플로우에서 캐시를 사용하지 않습니다. 플러그인은 캐시를 사용하여 증분 미러링을 수행하고 변경되지 않은 이미지를 다시 미러링하지 않으므로 시간을 절약하고 네트워크 대역폭 사용량을 줄입니다. 기본 캐시 디렉터리는 `$HOME` 입니다. 자세한 내용은 "-cache-dir 및 --workspace 플래그 수락"을 참조하십시오. |
| `-c <string>` , `--config <string>` | 삭제 이미지 세트 구성 파일의 경로입니다. |
| `--delete-id <string>` | 삭제 기능으로 생성된 파일의 버전을 구분하는 데 사용됩니다. |
| `--delete-v1-images` | oc-mirror 플러그인 v1로 이전에 미러링된 이미지를 대상으로 하기 위해 `--generate` 와 함께 마이그레이션 중에 사용됩니다. |
| `--delete-yaml-file <string>` | 설정된 경우 생성된 yaml 또는 업데이트된 yaml 파일을 사용하여 콘텐츠를 삭제합니다. |
| `--dest-tls-verify` | HTTPS가 필요하며 컨테이너 레지스트리 또는 데몬과 통신할 때 인증서를 확인해야 합니다. 기본값은 `true` 입니다. |
| `--force-cache-delete` | 로컬 캐시 매니페스트 및 Blob을 강제로 삭제하는 데 사용됩니다. |
| `--generate` | 로컬 캐시 및 원격 레지스트리에서 삭제할 때 사용되는 매니페스트 및 Blob 목록에 대한 삭제 yaml을 생성하는 데 사용됩니다. |
| `-h` , `--help` | 도움말을 표시합니다. |
| `--log-level <string>` | 로그 수준 `정보` , `디버그` , `추적` 및 `오류` 중 하나입니다. 기본값은 `info` 입니다. |
| `--parallel-images <unit>` | 병렬로 삭제된 이미지 수를 나타냅니다. 값은 1-10의 범위에 있어야 합니다. 기본값은 `4` 입니다. |
| `--parallel-layers <unit>` | 병렬로 삭제된 이미지 계층 수를 나타냅니다. 값은 1-10의 범위에 있어야 합니다. 기본값은 `5` 입니다. |
| `-p <unit>` , `--port <unit>` | oc-mirror의 로컬 스토리지 인스턴스에서 사용하는 HTTP 포트입니다. 기본값은 `55000` 입니다. |
| `--retry-delay` | 2번 재시도 사이의 기간 지연. 기본값은 `1s` 입니다. |
| `--retry-times <int>` | 재시도 횟수입니다. 기본값은 `2` 입니다. |
| `--src-tls-verify` | HTTPS가 필요하며 컨테이너 레지스트리 또는 데몬과 통신할 때 인증서를 확인해야 합니다. 기본값은 `true` 입니다. |
| `--workspace <string>` | `--workspace` 플래그를 사용하여 oc-mirror 플러그인이 `ImageDigestMirrorSet` 및 `ImageTagMirrorSet` 매니페스트와 같이 미러링 작업 중에 생성하는 작업 파일을 저장하는 디렉터리를 지정할 수 있습니다. 이 디렉터리를 사용하여 생성된 구성을 클러스터에 적용하고 미러링 작업을 반복합니다. 자세한 내용은 "-cache-dir 및 --workspace 플래그 수락"을 참조하십시오. |

#### 5.13.2. --cache-dir 및 --workspace 플래그 정보

`--cache-dir` 플래그를 사용하여 oc-mirror 플러그인이 미러링 작업 중에 사용할 이미지 Blob 및 매니페스트의 영구 캐시를 저장하는 디렉터리를 지정할 수 있습니다.

oc-mirror 플러그인은 `mirror-to-disk` 및 `disk-to-mirror` 워크플로우에서 캐시를 사용하지만 `mirror-to-mirror` 워크플로우에서 캐시를 사용하지 않습니다. 플러그인은 캐시를 사용하여 증분 미러링을 수행하고 변경되지 않은 이미지를 다시 미러링하지 않으므로 시간을 절약하고 네트워크 대역폭 사용량을 줄입니다.

캐시 디렉터리에는 마지막으로 성공한 미러링 작업까지의 데이터만 포함됩니다. 캐시 디렉터리를 삭제하거나 손상시키는 경우 oc-mirror 플러그인은 이미지 Blob 및 매니페스트를 다시 가져오므로 전체 remirror를 강제 적용하고 네트워크 사용량을 늘릴 수 있습니다.

`--workspace` 플래그를 사용하여 oc-mirror 플러그인이 `ImageDigestMirrorSet` 및 `ImageTagMirrorSet` 매니페스트와 같이 미러링 작업 중에 생성하는 작업 파일을 저장하는 디렉터리를 지정할 수 있습니다. 작업 공간 디렉터리를 사용하여 다음 작업을 수행할 수도 있습니다.

릴리스 및 Operator 이미지에 대해 변경되지 않은 메타데이터를 저장합니다.

`disk-to-mirror` 워크플로우에 사용할 tar 아카이브를 생성합니다.

생성된 구성을 클러스터에 적용합니다.

이전 미러링 작업을 반복하거나 다시 시작합니다.

작업 공간 디렉터리를 제거하거나 수정하는 경우 향후 미러링 작업이 실패할 수 있거나 클러스터에서 일관되지 않은 이미지 소스를 사용할 수 있습니다.

주의

캐시 또는 작업 공간 디렉터리의 내용을 삭제하거나 수정하면 다음과 같은 문제가 발생할 수 있습니다.

미러링에 실패하거나 불완전한 미러링 작업입니다.

증분 미러링 데이터 손실.

전체 remirroring 요구 사항과 네트워크 오버헤드가 증가했습니다.

영향을 완전히 이해하지 않는 한 이러한 디렉터리를 수정, 재배치 또는 삭제하지 마십시오. 미러링 작업에 성공한 후 캐시 디렉터리를 정기적으로 백업해야 합니다. 각 미러링 주기 동안 내용이 다시 생성되므로 작업 공간 디렉터리를 백업할 필요가 없습니다.

캐시 및 작업 공간 디렉터리를 효과적으로 관리할 수 있도록 다음 모범 사례를 고려하십시오.

영구 스토리지 사용: 신뢰할 수 있는 백업 스토리지에 캐시 및 작업 공간 디렉터리를 배치합니다.

성공적인 작업 후 백업: 특히 미러링 주기를 완료한 후 캐시 디렉터리를 정기적으로 백업합니다.

필요한 경우 복원: 데이터가 손실되면 백업에서 캐시 및 작업 공간 디렉터리를 복원하여 전체 remirror를 수행하지 않고 미러링 작업을 재개합니다.

별도의 환경: 충돌을 방지하려면 다른 환경에 전용 디렉터리를 사용합니다.

다음 예제를 사용하여 oc-mirror 명령을 실행할 때 캐시 및 작업 공간 디렉터리를 지정합니다.

```shell-session
$ oc mirror --config=imageset-config.yaml \
    file://local_mirror \
    --workspace /mnt/mirror-data/workspace \
    --cache-dir /mnt/mirror-data/cache
    --v2
```

미러링 작업이 완료되면 디렉터리 구조는 다음과 같습니다.

```plaintext
/mnt/mirror-data/
├── cache/
│   ├── manifests/
│   ├── metadata.db
│   └── previous-mirror-state.json
└── workspace/
    ├── imageset-config-state.yaml
    ├── manifests/
    └── icsp/
```

미러링 작업이 성공할 때마다 `/mnt/mirror-data/cache` 디렉터리를 백업해야 합니다.

추가 리소스

oc-mirror에서 생성한 리소스를 사용하도록 클러스터 구성

### 5.14. 다음 단계

oc-mirror 플러그인 v2를 사용하여 연결이 끊긴 환경에 이미지를 미러링한 후 다음 작업을 수행할 수 있습니다.

연결이 끊긴 환경에서 클러스터 설치

연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

OpenShift Update Service를 사용하여 연결이 끊긴 환경에서 클러스터 업데이트

## 6장. oc-mirror 플러그인 v1에서 v2로 마이그레이션

oc-mirror v2 플러그인으로 인해 이미지 미러링 워크플로에 대한 주요 변경 사항이 추가되었습니다. 이 가이드에서는 oc-mirror 플러그인 v2과의 호환성을 보장하면서 마이그레이션에 대한 단계별 지침을 제공합니다.

중요

API 버전을 수정하고 더 이상 사용되지 않는 필드를 제거하여 구성을 수동으로 업데이트해야 합니다. 자세한 내용은 "oc-mirror 플러그인 v1에서 v2로 변경"을 참조하십시오.

### 6.1. oc-mirror 플러그인 v1에서 v2로 변경

oc-mirror 플러그인 v1에서 v2로 마이그레이션하기 전에 oc-mirror 플러그인 v1과 v2 간의 다음 차이점을 참조하십시오.

명시적 버전 선택: 다음 명령을 사용할 때 사용자가 `--v2` 를 명시적으로 지정해야 합니다. 버전을 지정하지 않으면 v1이 기본적으로 실행됩니다. 이 동작은 향후 릴리스에서 변경될 것으로 예상됩니다. 여기서 `--v2` 는 기본값입니다.

```shell
oc-mirror
```

업데이트된 명령: oc-mirror 플러그인 v2의 새 워크플로우에 맞게 워크플로우 미러링 명령이 변경되었습니다.

mirror-to-disk의 경우 다음 명령을 실행합니다.

```shell-session
$ oc-mirror --config isc.yaml file://<directory_name> --v2
```

disk-to-mirror의 경우 다음 명령을 실행합니다.

```shell-session
$ oc-mirror --config isc.yaml --from file://<directory_name> docker://<remote_registry> --v2
```

mirror-to-mirror의 경우 다음 명령을 실행합니다.

```shell-session
$ oc-mirror --config isc.yaml --workspace file://<directory_name> docker://<remote_registry> --v2
```

참고

mirror-to-mirror 작업에 `--workspace` 가 필요합니다.

API 버전 업데이트: `ImageSetConfiguration` API 버전이 `v1alpha2` (v1)에서 `v2alpha1` (v2)으로 변경됩니다. 마이그레이션 전에 구성 파일을 수동으로 업데이트해야 합니다.

구성 변경:

`storageConfig` 는 oc-mirror 플러그인 v2에서 제거해야 합니다.

증분 미러링은 이제 작업 디렉터리 또는 로컬 캐시를 통해 자동으로 처리됩니다.

결과 디렉터리: 연결이 끊긴 클러스터에 적용할 모든 사용자 정의 리소스는 마이그레이션 후 < `workspace_path>/working-dir/cluster-resources` 디렉터리에 생성됩니다.

oc-mirror 플러그인 v2의 출력은 oc-mirror 플러그인 v1과 동일한 위치에 저장되지 않습니다.

다음 리소스의 작업 디렉터리에서 `cluster-resources` 폴더를 확인해야 합니다.

`ImageDigestMirrorSet` (IDMS)

`ImageTagMirrorSet` (ITMS)

`CatalogSource`

`ClusterCatalog`

`UpdateService`

Workspace 및 디렉터리 이름 지정: 새 oc-mirror v2 규칙을 따르어 버전 간에 전환할 때 잠재적인 데이터 불일치를 방지합니다.

oc-mirror 플러그인 v1 디렉터리가 더 이상 필요하지 않습니다.

```shell
oc-mirror-workspace
```

충돌을 방지하려면 oc-mirror 플러그인 v2에 새 디렉터리를 사용합니다.

ICSP(`ImageContentSourcePolicy`) 리소스를 IDMS/ITMS로 교체:

중요

모든 ICSP(`ImageContentSourcePolicy`) 리소스를 삭제하면 oc-mirror와 관련이 없는 구성이 제거될 수 있습니다.

의도하지 않은 삭제를 방지하려면 제거하기 전에 oc-mirror에서 생성한 ICSP 리소스를 식별합니다. 확실하지 않은 경우 클러스터 관리자에게 확인하십시오. 자세한 내용은 "oc-mirror 플러그인 v2를 사용하여 연결이 끊긴 설치의 이미지 미러링"을 참조하십시오.

oc-mirror 플러그인 v2에서 ICSP 리소스는 `ImageDigestMirrorSet` (IDMS) 및 `ImageTagMirrorSet` (ITMS) 리소스로 교체됩니다.

### 6.2. oc-mirror 플러그인 v2로 마이그레이션

oc-mirror 플러그인 v1에서 v2로 마이그레이션하려면 `ImageSetConfiguration` 파일을 수동으로 업데이트하고 미러링 명령을 수정하고 v1 아티팩트를 정리해야 합니다. 다음 단계에 따라 마이그레이션을 완료합니다.

프로세스

API 버전을 수정하고 `ImageSetConfiguration` 에서 더 이상 사용되지 않는 필드를 제거합니다.

```yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v1alpha2
mirror:
  platform:
    channels:
      - name: stable-4.17
    graph: true
  helm:
    repositories:
      - name: sbo
        url: https://redhat-developer.github.io/service-binding-operator-helm-chart/
  additionalImages:
    - name: registry.redhat.io/ubi8/ubi:latest
    - name: quay.io/openshifttest/hello-openshift@sha256:example_hash
  operators:
    - catalog: oci:///test/redhat-operator-index
      packages:
        - name: aws-load-balancer-operator
storageConfig:  # REMOVE this field in v2
  local:
    path: /var/lib/oc-mirror
```

```yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v2alpha1
mirror:
  platform:
    channels:
      - name: stable-4.17
    graph: true
  helm:
    repositories:
      - name: sbo
        url: https://redhat-developer.github.io/service-binding-operator-helm-chart/
  additionalImages:
    - name: registry.redhat.io/ubi8/ubi:latest
    - name: quay.io/openshifttest/hello-openshift@sha256:example_hash
  operators:
    - catalog: oci:///test/redhat-operator-index
      packages:
        - name: aws-load-balancer-operator
```

참고

oc-mirror 플러그인 v1에서 v2로 마이그레이션하는 경우 `additionalImages` 아래에 나열된 모든 이미지에 대해 명시적 레지스트리 호스트 이름을 사용해야 합니다. 그렇지 않으면 이미지가 잘못된 대상 경로로 미러링됩니다.

다음 명령을 실행하여 IDMS, ITMS, `CatalogSource`, `ClusterCatalog` 리소스에 대한 작업 디렉터리 내부의 `cluster-resources` 디렉터리를 확인합니다.

```shell-session
$ ls <v2_workspace>/working-dir/cluster-resources/
```

마이그레이션이 완료되면 미러링된 이미지 및 카탈로그를 사용할 수 있는지 확인합니다.

미러링 중에 오류 또는 경고가 발생하지 않았는지 확인합니다.

오류 파일이 생성되지 않았는지 확인합니다(`working-dir/logs/mirroring_errors_YYYYMMdd_HHmmss.txt`).

다음 명령을 사용하여 미러링된 이미지 및 카탈로그를 사용할 수 있는지 확인합니다.

```shell-session
$ oc get catalogsource -n openshift-marketplace
```

```shell-session
$ oc get imagedigestmirrorset,imagetagmirrorset
```

자세한 내용은 "oc-mirror 플러그인 v2를 사용하여 연결이 끊긴 설치의 이미지 미러링"을 참조하십시오.

선택 사항: oc-mirror 플러그인 v1을 사용하여 미러링된 이미지를 제거합니다.

oc-mirror 플러그인 v1을 사용하여 이미지를 미러링합니다.

`ImageSetConfiguration` 파일에서 `v1alpha2` (v1)에서 `v2alpha1` (v2)으로 API 버전을 업데이트한 다음 다음 명령을 실행합니다.

```shell-session
$ oc-mirror -c isc.yaml file://some-dir --v2
```

참고

`StorageConfig` 는 `ImageSetConfiguration` 및 `DeleteImageSetConfiguration` 파일의 유효한 필드가 아닙니다. oc-mirror 플러그인 v2로 업데이트할 때 이 필드를 제거합니다.

다음 명령을 실행하여 삭제 매니페스트를 생성하고 v1 이미지를 삭제합니다.

```shell-session
$ oc-mirror delete --config=delete-isc.yaml --generate --delete-v1-images --workspace file://some-dir docker://registry.example:5000  --v2
```

중요

oc-mirror 플러그인 v2는 oc-mirror 플러그인 v1과 달리 대상 레지스트리를 자동으로 정리하지 않습니다. 더 이상 필요하지 않은 이미지를 정리하려면 `--delete-v1-images` 명령 플래그와 함께 v2의 삭제 기능을 사용합니다.

oc-mirror 플러그인 v1로 미러링된 모든 이미지가 제거되면 더 이상 이 플래그를 사용할 필요가 없습니다. oc-mirror 플러그인 v2로 미러링된 이미지를 삭제해야 하는 경우 `--delete-v1-images` 를 설정하지 마십시오.

이미지 삭제에 대한 자세한 내용은 "연결이 끊긴 환경에서 이미지 삭제"를 참조하십시오.

다음 명령을 실행하여 생성된 매니페스트를 기반으로 이미지를 삭제합니다.

```shell-session
$ oc-mirror delete --delete-yaml-file some-dir/working-dir/delete/delete-images.yaml docker://registry.example:5000 --v2
```

### 6.3. 추가 리소스

부분적으로 연결이 끊긴 환경에서 이미지 세트 미러링

완전히 연결이 끊긴 환경에서 이미지 세트 미러링

구성 변경에 대한 자세한 내용은 oc-mirror 플러그인 v1에서 v2로 변경 사항을 참조하십시오.

이미지 삭제에 대한 자세한 내용은 연결이 끊긴 환경에서 이미지 삭제를 참조하십시오.

## 7장. oc-mirror 플러그인을 사용하여 연결이 끊긴 설치의 이미지 미러링

직접 인터넷 연결이 없는 제한된 네트워크에서 클러스터를 실행하면 프라이빗 레지스트리의 미러링된 OpenShift Container Platform 컨테이너 이미지에서 클러스터를 설치할 수 있습니다. 클러스터를 실행하는 동안 이 레지스트리는 항상 실행되어야 합니다. 자세한 내용은 사전 요구 사항 섹션을 참조하십시오.

oc-mirror OpenShift CLI() 플러그인을 사용하여 완전히 또는 부분적으로 연결이 끊긴 환경의 미러 레지스트리에 이미지를 미러링할 수 있습니다. 공식 Red Hat 레지스트리에서 필요한 이미지를 다운로드하려면 인터넷 연결이 있는 시스템에서 oc-mirror를 실행해야 합니다.

```shell
oc
```

중요

oc-mirror v1 플러그인은 더 이상 사용되지 않습니다. 향후 릴리스에서 실패하지 않도록 하려면 v1 플러그인을 계속 사용하려면 `--v1` 플래그를 지정하거나 지원되는 v2 플러그인으로 마이그레이션하고 `--v2` 플래그를 사용합니다. 지속적인 지원 및 개선을 위해 oc-mirror v2 플러그인 으로 전환

### 7.1. oc-mirror 플러그인 정보

oc-mirror OpenShift CLI() 플러그인을 사용하여 필요한 모든 OpenShift Container Platform 콘텐츠 및 기타 이미지를 단일 툴을 사용하여 미러 레지스트리에 미러링할 수 있습니다. 다음과 같은 기능을 제공합니다.

```shell
oc
```

OpenShift Container Platform 릴리스, Operator, helm 차트 및 기타 이미지를 미러링하는 중앙 집중식 방법을 제공합니다.

OpenShift Container Platform 및 Operator의 업데이트 경로를 유지 관리합니다.

선언적 이미지 세트 구성 파일을 사용하여 클러스터에 필요한 OpenShift Container Platform 릴리스, Operator 및 이미지만 포함합니다.

증분 미러링을 수행하여 향후 이미지 세트의 크기를 줄입니다.

이전 실행 이후 이미지 세트 구성에서 제외된 대상 미러 레지스트리에서 이미지를 정리합니다.

선택적으로 OpenShift Update Service (OSUS) 사용에 대한 지원 아티팩트를 생성합니다.

oc-mirror 플러그인을 사용하는 경우 이미지 세트 구성 파일에서 미러링할 콘텐츠를 지정합니다. 이 YAML 파일에서는 클러스터에 필요한 OpenShift Container Platform 릴리스와 Operator만 포함하도록 구성을 미세 조정할 수 있습니다.

이렇게 하면 다운로드 및 전송에 필요한 데이터 양이 줄어듭니다. oc-mirror 플러그인은 임의의 helm 차트 및 추가 컨테이너 이미지를 미러링하여 사용자가 워크로드를 미러 레지스트리에 원활하게 동기화할 수 있도록 지원합니다.

oc-mirror 플러그인을 처음 실행하면 연결이 끊긴 클러스터 설치 또는 업데이트를 수행하는 데 필요한 콘텐츠로 미러 레지스트리를 채웁니다. 연결이 끊긴 클러스터가 업데이트를 계속 받으려면 미러 레지스트리를 계속 업데이트해야 합니다.

미러 레지스트리를 업데이트하려면 처음 실행할 때와 동일한 구성을 사용하여 oc-mirror 플러그인을 실행합니다. oc-mirror 플러그인은 스토리지 백엔드의 메타데이터를 참조하고 툴을 마지막으로 실행한 이후 릴리스된 항목만 다운로드합니다.

이는 OpenShift Container Platform 및 Operator의 업데이트 경로를 제공하고 필요에 따라 종속성 확인을 수행합니다.

#### 7.1.1. 고급 워크플로

다음 단계에서는 oc-mirror 플러그인을 사용하여 이미지를 미러 레지스트리에 미러링하는 방법에 대한 고급 워크플로를 간략하게 설명합니다.

이미지 세트 구성 파일을 생성합니다.

다음 방법 중 하나를 사용하여 대상 미러 레지스트리에 설정된 이미지를 미러링합니다.

대상 미러 레지스트리에 직접 설정된 이미지를 미러링합니다.

이미지를 디스크에 미러링하고 대상 환경으로 설정된 이미지를 전송한 다음 대상 미러 레지스트리에 설정된 이미지를 업로드합니다.

oc-mirror 플러그인에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

필요에 따라 대상 미러 레지스트리를 업데이트하려면 다음 단계를 반복합니다.

중요

oc-mirror CLI 플러그인을 사용하여 미러 레지스트리를 채우는 경우 oc-mirror 플러그인을 사용하여 대상 미러 레지스트리에 대한 추가 업데이트를 수행해야 합니다.

### 7.2. oc-mirror 플러그인 호환성 및 지원

oc-mirror 플러그인은 OpenShift Container Platform 버전 4.12 이상에서 OpenShift Container Platform 페이로드 이미지 및 Operator 카탈로그 미러링을 지원합니다.

참고

`aarch64`, `ppc64le` 및 `s390x` 아키텍처에서 oc-mirror 플러그인은 OpenShift Container Platform 버전 4.14 이상에서만 지원됩니다.

미러링해야 하는 OpenShift Container Platform 버전에 관계없이 사용 가능한 최신 버전의 oc-mirror 플러그인을 사용합니다.

추가 리소스

oc-mirror 업데이트에 대한 자세한 내용은 이미지 가져오기 소스 보기를 참조하십시오.

### 7.3. 미러 레지스트리 정보

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스해야 합니다. 대체 레지스트리를 사용하면 네트워크와 인터넷에 모두 액세스할 수 있는 미러 호스트에 미러 레지스트리를 배치합니다.

OpenShift Container Platform 설치 및 후속 제품 업데이트에 필요한 이미지를 Red Hat Quay와 같이 Docker v2-2 를 지원하는 컨테이너 미러 레지스트리에 미러링할 수 있습니다.

대규모 컨테이너 레지스트리에 액세스할 수 없는 경우 OpenShift Container Platform 서브스크립션에 포함된 소규모 컨테이너 레지스트리인 Red Hat OpenShift 에 미러 레지스트리를 사용할 수 있습니다.

선택한 레지스트리에 관계없이 인터넷상의 Red Hat 호스팅 사이트의 콘텐츠를 격리된 이미지 레지스트리로 미러링하는 절차는 동일합니다. 콘텐츠를 미러링한 후 미러 레지스트리에서 이 콘텐츠를 검색하도록 각 클러스터를 설정합니다.

중요

OpenShift 이미지 레지스트리는 미러링 프로세스 중에 필요한 태그 없이 푸시를 지원하지 않으므로 대상 레지스트리로 사용할 수 없습니다.

Red Hat OpenShift의 미러 레지스트리가 아닌 컨테이너 레지스트리를 선택하는 경우 프로비저닝하는 클러스터의 모든 시스템에서 연결할 수 있어야 합니다. 레지스트리에 연결할 수 없는 경우 설치, 업데이트 또는 워크로드 재배치와 같은 일반 작업이 실패할 수 있습니다.

따라서 고가용성 방식으로 미러 레지스트리를 실행해야하며 미러 레지스트리는 최소한 OpenShift Container Platform 클러스터의 프로덕션 환경의 가용성조건에 일치해야 합니다.

미러 레지스트리를 OpenShift Container Platform 이미지로 채우면 다음 두 가지 시나리오를 수행할 수 있습니다. 호스트가 인터넷과 미러 레지스트리에 모두 액세스할 수 있지만 클러스터 노드에 액세스 할 수 없는 경우 해당 머신의 콘텐츠를 직접 미러링할 수 있습니다.

이 프로세스를 connected mirroring (미러링 연결)이라고 합니다. 그러한 호스트가 없는 경우 이미지를 파일 시스템에 미러링한 다음 해당 호스트 또는 이동식 미디어를 제한된 환경에 배치해야 합니다.

이 프로세스를 미러링 연결 해제 라고 합니다.

미러링된 레지스트리의 경우 가져온 이미지의 소스를 보려면 CRI-O 로그의 `Trying to access` 로그 항목을 검토해야 합니다. 노드에서 아래 명령을 사용하는 등의 이미지 가져오기 소스를 보는 다른 방법은 미러링되지 않은 이미지 이름을 표시합니다.

```shell
crictl images
```

참고

Red Hat은 OpenShift Container Platform에서 타사 레지스트리를 테스트하지 않습니다.

추가 리소스

이미지 가져오기 소스 보기.

### 7.4. 사전 요구 사항

Red Hat Quay와 같은 OpenShift Container Platform 클러스터를 호스팅할 위치에 Docker v2-2 를 지원하는 컨테이너 이미지 레지스트리가 있어야 합니다.

참고

Red Hat Quay를 사용하는 경우 oc-mirror 플러그인에서 버전 3.6 이상을 사용해야 합니다. Red Hat Quay에 대한 인타이틀먼트가 있는 경우 개념 증명 목적으로 또는 Red Hat Quay Operator를 사용하여 Red Hat Quay 배포에 대한 설명서를 참조하십시오.

레지스트리를 선택 및 설치하는 데 추가 지원이 필요한 경우 영업 담당자 또는 Red Hat 지원팀에 문의하십시오.

컨테이너 이미지 레지스트리에 대한 기존 솔루션이 없는 경우 OpenShift Container Platform 구독자에게 Red Hat OpenShift의 미러 레지스트리 가 제공됩니다.

Red Hat OpenShift의 미러 레지스트리 는 서브스크립션에 포함되어 있으며 연결이 끊긴 설치에서 OpenShift Container Platform의 필요한 컨테이너 이미지를 미러링하는 데 사용할 수 있는 소규모 컨테이너 레지스트리입니다.

### 7.5. 미러 호스트 준비

oc-mirror 플러그인을 사용하여 이미지를 미러링하려면 먼저 플러그인을 설치하고 컨테이너 이미지 레지스트리 인증 정보 파일을 생성하여 Red Hat에서 미러로 미러링할 수 있습니다.

#### 7.5.1. oc-mirror OpenShift CLI 플러그인 설치

oc-mirror OpenShift CLI 플러그인을 설치하여 연결이 끊긴 환경에서 이미지 세트를 관리합니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다. 완전히 연결이 끊긴 환경에서 이미지 세트를 미러링하는 경우 다음을 확인하십시오.

```shell
oc
```

인터넷에 액세스할 수 있는 호스트에 oc-mirror 플러그인을 설치했습니다.

연결이 끊긴 환경의 호스트는 대상 미러 레지스트리에 액세스할 수 있습니다.

oc-mirror `를` 사용하는 운영 체제에서 Cryostat 매개변수를 `0022` 로 설정해야 합니다.

사용 중인 RHEL 버전에 대해 올바른 바이너리를 설치했습니다.

프로세스

oc-mirror CLI 플러그인을 다운로드합니다.

Red Hat Hybrid Cloud Console의 다운로드 페이지로 이동합니다.

OpenShift 연결 설치 툴 섹션의 드롭다운 메뉴에서 OpenShift Client(oc) 미러 플러그인 의 OS 유형 및 아키텍처 유형을 선택합니다.

다운로드를 클릭하여 파일을 저장합니다.

다음 명령을 실행하여 아카이브의 압축을 풉니다.

```shell-session
$ tar xvzf oc-mirror.tar.gz
```

필요한 경우 다음 명령을 실행하여 플러그인 파일을 실행 가능하게 업데이트합니다.

```shell-session
$ chmod +x oc-mirror
```

참고

다음 명령파일의 이름을 바꾸지 마십시오.

```shell
oc-mirror
```

다음 명령을 실행하여 파일을 `PATH` (예: `/usr/local/bin`)에 배치하여 oc-mirror CLI 플러그인을 설치합니다.

```shell-session
$ sudo mv oc-mirror /usr/local/bin/.
```

검증

다음 명령을 실행하여 oc-mirror 플러그인 v1이 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc mirror help
```

추가 리소스

CLI 플러그인 설치 및 사용

#### 7.5.2. 이미지를 미러링할 수 있는 인증 정보 설정

Red Hat에서 미러로 이미지를 미러링할 수 있도록 컨테이너 이미지 레지스트리 인증 정보 파일을 생성합니다. 설치 호스트에서 다음 단계를 완료합니다.

주의

클러스터를 설치할 때 이 이미지 레지스트리 인증 정보 파일을 풀 시크릿(pull secret)으로 사용하지 마십시오. 클러스터를 설치할 때 이 파일을 지정하면 클러스터의 모든 시스템에 미러 레지스트리에 대한 쓰기 권한이 부여됩니다.

사전 요구 사항

연결이 끊긴 환경에서 사용할 미러 레지스트리를 구성했습니다.

미러 레지스트리에서 이미지를 미러링할 이미지 저장소 위치를 확인했습니다.

이미지를 해당 이미지 저장소에 업로드할 수 있는 미러 레지스트리 계정을 제공하고 있습니다.

미러 레지스트리에 대한 쓰기 권한이 있습니다.

프로세스

Red Hat OpenShift Cluster Manager 에서 `registry.redhat.io` 풀 시크릿을 다운로드합니다.

다음 명령을 실행하여 풀 시크릿을 JSON 형식으로 복사합니다.

```shell-session
$ cat ./pull-secret | jq . > <path>/<pull_secret_file_in_json>
```

풀 시크릿을 저장할 디렉터리의 경로와 생성한 JSON 파일의 이름을 지정합니다.

```plaintext
{
  "auths": {
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

파일을 `~/.docker/config.json` 또는 `$XDG_RUNTIME_DIR/containers/auth.json` 으로 저장합니다.

`.docker` 또는 `$XDG_RUNTIME_DIR/containers` 디렉터리가 없는 경우 다음 명령을 입력하여 만듭니다.

```shell-session
$ mkdir -p <directory_name>
```

여기서 `<directory_name>` 은 `~/.docker` 또는 `$XDG_RUNTIME_DIR/containers` 입니다.

다음 명령을 입력하여 풀 시크릿을 적절한 디렉터리에 복사합니다.

```shell-session
$ cp <path>/<pull_secret_file_in_json> <directory_name>/<auth_file>
```

< `directory_name` >은 `~/.docker` 또는 `$XDG_RUNTIME_DIR/containers` 이며 < `auth_file` >은 `config.json` 또는 `auth.json` 입니다.

다음 명령을 실행하여 미러 레지스트리에 대한 base64로 인코딩된 사용자 이름 및 암호 또는 토큰을 생성합니다.

```shell-session
$ echo -n '<user_name>:<password>' | base64 -w0
```

`<user_name>` 및 `<password>` 의 경우 레지스트리에 설정한 사용자 이름 및 암호를 지정합니다.

```shell-session
BGVtbYk3ZHAtqXs=
```

JSON 파일을 편집하고 레지스트리를 설명하는 섹션을 추가합니다.

```plaintext
"auths": {
    "<mirror_registry>": {
      "auth": "<credentials>",
      "email": "you@example.com"
    }
  },
```

&lt `;mirror_registry` > 값의 경우 미러 레지스트리가 콘텐츠를 제공하는 데 사용하는 레지스트리 도메인 이름과 포트(선택 사항)를 지정합니다. 예: `registry.example.com` 또는 `registry.example.com:8443`.

&lt `;credentials&` gt; 값의 경우 미러 레지스트리의 base64 인코딩 사용자 이름과 암호를 지정합니다.

```plaintext
{
  "auths": {
    "registry.example.com": {
      "auth": "BGVtbYk3ZHAtqXs=",
      "email": "you@example.com"
    },
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

### 7.6. 이미지 세트 구성 생성

oc-mirror 플러그인을 사용하여 이미지 세트를 미러링하려면 먼저 이미지 세트 구성 파일을 생성해야 합니다. 이 이미지 세트 구성 파일은 oc-mirror 플러그인의 다른 구성 설정과 함께 미러링할 OpenShift Container Platform 릴리스, Operator 및 기타 이미지를 정의합니다.

이미지 세트 구성 파일에 스토리지 백엔드를 지정해야 합니다. 이 스토리지 백엔드는 로컬 디렉터리 또는 Docker v2-2 를 지원하는 레지스트리일 수 있습니다. oc-mirror 플러그인은 이미지 세트 생성 중에 이 스토리지 백엔드에 메타데이터를 저장합니다.

중요

oc-mirror 플러그인에서 생성한 메타데이터를 삭제하거나 수정하지 마십시오. 동일한 미러 레지스트리에 대해 oc-mirror 플러그인을 실행할 때마다 동일한 스토리지 백엔드를 사용해야 합니다.

사전 요구 사항

컨테이너 이미지 레지스트리 인증 정보 파일이 생성되어 있습니다. 자세한 내용은 "이미지 미러링을 허용하는 인증 정보 구성"을 참조하십시오.

프로세스

아래 명령을 사용하여 이미지 세트 구성에 대한 템플릿을 생성하고 `imageset-config.yaml` 이라는 파일에 저장합니다.

```shell
oc mirror init
```

```shell-session
$ oc mirror init --registry <storage_backend> > imageset-config.yaml
```

1. `example.com/mirror/oc-mirror-metadata` 와 같은 스토리지 백엔드의 위치를 지정합니다.

파일을 편집하고 필요에 따라 설정을 조정합니다.

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
    - name: serverless-operator
      channels:
      - name: stable
  additionalImages:
  - name: registry.redhat.io/ubi9/ubi:latest
  helm: {}
```

1. `archiveSize` 를 추가하여 이미지 세트 내에서 각 파일의 최대 크기를 GiB 단위로 설정합니다.

2. 이미지 세트 메타데이터를 저장할 백엔드 위치를 설정합니다. 이 위치는 레지스트리 또는 로컬 디렉터리일 수 있습니다. `storageConfig` 값을 지정해야 합니다.

3. 스토리지 백엔드의 레지스트리 URL을 설정합니다.

4. 채널을 설정하여 OpenShift Container Platform 이미지를 검색합니다.

5. `graph: true` 를 추가하여 graph-data 이미지를 빌드 및 미러 레지스트리로 내보냅니다. OSUS(OpenShift Update Service)를 생성하려면 graph-data 이미지가 필요합니다.

`graph: true` 필드에서도 `UpdateService` 사용자 정의 리소스 매니페스트를 생성합니다. CLI(명령줄 인터페이스)는 `UpdateService` 사용자 정의 리소스 매니페스트를 사용하여 OSUS를 생성할 수 있습니다.

```shell
oc
```

자세한 내용은 OpenShift 업데이트 서비스 정보 를 참조하십시오.

6. Operator 카탈로그를 설정하여 OpenShift Container Platform 이미지를 검색합니다.

7. 이미지 세트에 포함할 특정 Operator 패키지만 지정합니다. 이 필드를 제거하여 카탈로그의 모든 패키지를 검색합니다.

8. 이미지 세트에 포함할 Operator 패키지의 특정 채널만 지정합니다. 해당 채널에서 번들을 사용하지 않는 경우에도 Operator 패키지의 기본 채널을 항상 포함해야 합니다. 다음 명령을 실행하여 기본 채널을 찾을 수 있습니다. >.

```shell
oc mirror list operators --catalog=<catalog_name> --package=<package_name
```

9. 이미지 세트에 포함할 추가 이미지를 지정합니다.

참고

`graph: true` 필드도 다른 미러링된 이미지와 함께 `ubi-micro` 이미지를 미러링합니다.

OpenShift Container Platform EUS (Extended Update Support) 버전을 업그레이드할 때 현재 버전과 대상 버전 간에 중간 버전이 필요할 수 있습니다.

예를 들어 현재 버전이 `4.14` 이고 대상 버전이 `4.16` 인 경우 oc-mirror 플러그인 v1을 사용할 때 `ImageSetConfiguration` 에 `4.15.8` 과 같은 버전을 포함해야 할 수 있습니다.

oc-mirror 플러그인 v1이 항상 자동으로 감지되지 않을 수 있으므로 필요한 중간 버전을 확인하고 구성에 수동으로 추가하려면 Cincinnati 그래프 웹 페이지를 확인하십시오.

다양한 미러링 사용 사례에 대해서는 매개변수 전체 목록과 "Image set configuration examples"를 "Image set configuration parameters"를 참조하십시오.

업데이트된 파일을 저장합니다.

이 이미지 세트 구성 파일은 컨텐츠를 미러링할 때 아래 명령에 필요합니다.

```shell
oc mirror
```

추가 리소스

이미지 세트 구성 매개변수

이미지 세트 구성 예

연결이 끊긴 환경에서 OpenShift Update Service 사용

### 7.7. 미러 레지스트리로 이미지 세트 미러링

oc-mirror CLI 플러그인을 사용하여 부분적으로 연결이 끊긴 환경 또는 완전히 연결이 끊긴 환경에서 미러 레지스트리에 이미지를 미러링할 수 있습니다.

이 절차에서는 이미 미러 레지스트리가 설정되어 있다고 가정합니다.

#### 7.7.1. 부분적으로 연결이 끊긴 환경에서 이미지 세트 미러링

부분적으로 연결이 끊긴 환경에서는 대상 미러 레지스트리에 직접 설정된 이미지를 미러링할 수 있습니다.

#### 7.7.1.1. 미러에서 미러로 미러링

oc-mirror 플러그인을 사용하여 이미지 세트 생성 중에 액세스할 수 있는 대상 미러 레지스트리에 직접 설정된 이미지를 미러링할 수 있습니다.

이미지 세트 구성 파일에서 스토리지 백엔드를 지정해야 합니다. 이 스토리지 백엔드는 로컬 디렉터리 또는 Docker v2 레지스트리일 수 있습니다. oc-mirror 플러그인은 이미지 세트 생성 중에 이 스토리지 백엔드에 메타데이터를 저장합니다.

중요

oc-mirror 플러그인에서 생성한 메타데이터를 삭제하거나 수정하지 마십시오. 동일한 미러 레지스트리에 대해 oc-mirror 플러그인을 실행할 때마다 동일한 스토리지 백엔드를 사용해야 합니다.

사전 요구 사항

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스할 수 있습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

oc-mirror CLI 플러그인이 설치되어 있어야 합니다.

이미지 세트 구성 파일을 생성하셨습니다.

프로세스

아래 명령을 실행하여 지정된 이미지 세트 구성의 이미지를 지정된 레지스트리로 미러링합니다.

```shell
oc mirror
```

```shell-session
$ oc mirror --config=./<imageset-config.yaml> \
  docker://registry.example:5000
```

1. 생성한 이미지 세트 구성 파일을 지정합니다. 예를 들면 `imageset-config.yaml` 입니다.

2. 이미지 세트 파일을 미러링할 레지스트리를 지정합니다. 레지스트리는 다음 명령으로 시작해야 합니다. 미러 레지스트리에 최상위 네임스페이스를 지정하는 경우 후속 실행 시 동일한 네임스페이스를 사용해야 합니다.

```shell
docker://
```

검증

생성된 디렉터리로 이동합니다.

```shell
oc-mirror-workspace/
```

결과 디렉터리로 이동합니다 (예: `results-1639608409/`).

`ImageContentSourcePolicy` 및 `CatalogSource` 리소스에 YAML 파일이 있는지 확인합니다.

참고

`ImageContentSourcePolicy` YAML 파일의 `repositoryDigestMirrors` 섹션은 설치 중에 `install-config.yaml` 파일에 사용됩니다.

다음 단계

CRI-O를 수동으로 구성하는 데 사용할 `ImageContentSourcePolicy` YAML 콘텐츠를 변환합니다.

필요한 경우 연결이 끊긴 또는 오프라인 사용을 위해 미러의 이미지를 디스크로 미러링합니다.

oc-mirror에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

문제 해결

소스 이미지를 검색할 수 없습니다.

#### 7.7.2. 완전히 연결이 끊긴 환경에서 이미지 세트 미러링

완전히 연결이 끊긴 환경에서 이미지 세트를 미러링하려면 먼저 이미지 세트를 디스크로 미러링 한 다음 디스크의 이미지 세트 파일을 미러에 미러링 해야 합니다.

#### 7.7.2.1. 미러에서 디스크로 미러링

oc-mirror 플러그인을 사용하여 이미지 세트를 생성하고 내용을 디스크에 저장할 수 있습니다. 그런 다음 생성된 이미지 세트를 연결이 끊긴 환경으로 전송하고 대상 레지스트리에 미러링할 수 있습니다.

중요

이미지 세트 구성 파일에 지정된 구성에 따라 oc-mirror를 사용하여 이미지를 미러링하는 경우 수백 기가바이트의 데이터를 디스크에 다운로드할 수 있습니다.

미러 레지스트리를 채울 때 초기 이미지 세트 다운로드는 종종 가장 큰 것입니다. 명령을 마지막으로 실행한 이후 변경된 이미지만 다운로드하므로 oc-mirror 플러그인을 다시 실행하면 생성된 이미지 세트가 생성되는 경우가 많습니다.

이미지 세트 구성 파일에서 스토리지 백엔드를 지정해야 합니다. 이 스토리지 백엔드는 로컬 디렉터리 또는 docker v2 레지스트리일 수 있습니다. oc-mirror 플러그인은 이미지 세트 생성 중에 이 스토리지 백엔드에 메타데이터를 저장합니다.

중요

oc-mirror 플러그인에서 생성한 메타데이터를 삭제하거나 수정하지 마십시오. 동일한 미러 레지스트리에 대해 oc-mirror 플러그인을 실행할 때마다 동일한 스토리지 백엔드를 사용해야 합니다.

사전 요구 사항

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

oc-mirror CLI 플러그인을 설치했습니다.

이미지 세트 구성 파일을 생성했습니다.

프로세스

아래 명령을 실행하여 지정된 이미지 세트 구성의 이미지를 디스크로 미러링합니다.

```shell
oc mirror
```

```shell-session
$ oc mirror --config=./imageset-config.yaml \
  file://<path_to_output_directory>
```

1. 생성된 이미지 세트 구성 파일을 전달합니다. 이 절차에서는 `imageset-config.yaml` 이라는 이름을 가정합니다.

2. 이미지 세트 파일을 출력할 대상 디렉터리를 지정합니다. 대상 디렉터리 경로는 `file://` 로 시작해야 합니다.

검증

출력 디렉터리로 이동합니다.

```shell-session
$ cd <path_to_output_directory>
```

이미지 세트 `.tar` 파일이 생성되었는지 확인합니다.

```shell-session
$ ls
```

```plaintext
mirror_seq1_000000.tar
```

다음 단계

이미지 세트.tar 파일을 연결이 끊긴 환경으로 전송합니다.

문제 해결

소스 이미지를 검색할 수 없습니다.

#### 7.7.2.2. 디스크에서 미러로 미러링

oc-mirror 플러그인을 사용하여 생성된 이미지 세트의 콘텐츠를 대상 미러 레지스트리로 미러링할 수 있습니다.

사전 요구 사항

연결이 끊긴 환경에 OpenShift CLI ()를 설치했습니다.

```shell
oc
```

연결이 끊긴 환경에 oc-mirror CLI 플러그인을 설치했습니다.

아래 명령을 사용하여 이미지 세트 파일을 생성했습니다.

```shell
oc mirror
```

이미지 세트 파일을 연결이 끊긴 환경으로 전송했습니다.

프로세스

아래 명령을 실행하여 디스크에서 이미지 세트 파일을 처리하고 콘텐츠를 대상 미러 레지스트리에 미러링합니다.

```shell
oc mirror
```

```shell-session
$ oc mirror --from=./mirror_seq1_000000.tar \
  docker://registry.example:5000
```

1. 이 예제에서 `mirror_seq1_000000.tar` 라는 이미지 세트.tar 파일을 전달합니다. 이미지 세트 구성 파일에 `archiveSize` 값이 지정된 경우 이미지 세트가 여러.tar 파일로 분할될 수 있습니다. 이 경우 이미지 세트.tar 파일이 포함된 디렉토리에 전달할 수 있습니다.

2. 이미지 세트 파일을 미러링할 레지스트리를 지정합니다. 레지스트리는 다음 명령으로 시작해야 합니다. 미러 레지스트리에 최상위 네임스페이스를 지정하는 경우 후속 실행 시 동일한 네임스페이스를 사용해야 합니다.

```shell
docker://
```

이 명령은 이미지 세트로 미러 레지스트리를 업데이트하고 `ImageContentSourcePolicy` 및 `CatalogSource` 리소스를 생성합니다.

검증

생성된 디렉터리로 이동합니다.

```shell
oc-mirror-workspace/
```

결과 디렉터리로 이동합니다 (예: `results-1639608409/`).

`ImageContentSourcePolicy` 및 `CatalogSource` 리소스에 YAML 파일이 있는지 확인합니다.

다음 단계

oc-mirror에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

문제 해결

소스 이미지를 검색할 수 없습니다.

### 7.8. oc-mirror에서 생성한 리소스를 사용하도록 클러스터 구성

미러 레지스트리로 이미지를 미러링한 후 생성된 `ImageContentSourcePolicy`, `CatalogSource` 및 release 이미지 서명 리소스를 클러스터에 적용해야 합니다.

`ImageContentSourcePolicy` 리소스는 미러 레지스트리를 소스 레지스트리와 연결하고 온라인 레지스트리에서 미러 레지스트리로 이미지 가져오기 요청을 리디렉션합니다.

`CatalogSource` 리소스는 OLM(Operator Lifecycle Manager) Classic에서 미러 레지스트리에서 사용 가능한 Operator에 대한 정보를 검색하는 데 사용됩니다. 릴리스 이미지 서명은 미러링된 릴리스 이미지를 확인하는 데 사용됩니다.

참고

OLM v1은 `ClusterCatalog` 리소스를 사용하여 미러 레지스트리에서 사용 가능한 클러스터 확장에 대한 정보를 검색합니다.

oc-mirror 플러그인 v1은 `ClusterCatalog` 리소스를 자동으로 생성하지 않습니다. 수동으로 생성해야 합니다. `ClusterCatalog` 리소스 생성 및 적용에 대한 자세한 내용은 "Extensions"의 "클러스터에 카탈로그 추가"를 참조하십시오.

사전 요구 사항

연결이 끊긴 환경에서 레지스트리 미러로 이미지를 미러링했습니다.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

`cluster-admin` 역할의 사용자로 OpenShift CLI()에 로그인합니다.

```shell
oc
```

다음 명령을 실행하여 결과 디렉터리의 YAML 파일을 클러스터에 적용합니다.

```shell-session
$ oc apply -f ./oc-mirror-workspace/results-1639608409/
```

미러링된 릴리스 이미지가 있는 경우 다음 명령을 실행하여 릴리스 이미지 서명을 클러스터에 적용합니다.

```shell-session
$ oc apply -f ./oc-mirror-workspace/results-1639608409/release-signatures/
```

참고

클러스터 대신 Operator를 미러링하는 경우 다음 명령을 실행할 필요가 없습니다. 적용할 릴리스 이미지 서명이 없으므로 해당 명령을 실행하면 오류가 반환됩니다.

```shell
$ oc apply -f./oc-mirror-workspace/results-1639608409/release-signatures/
```

검증

다음 명령을 실행하여 `ImageContentSourcePolicy` 리소스가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get imagecontentsourcepolicy
```

다음 명령을 실행하여 `CatalogSource` 리소스가 성공적으로 설치되었는지 확인합니다.

```shell-session
$ oc get catalogsource -n openshift-marketplace
```

추가 리소스

"Extensions" 의 클러스터에 카탈로그 추가

### 7.9. 미러 레지스트리 콘텐츠 업데이트

이미지 세트 구성 파일을 업데이트하고 이미지 세트를 미러 레지스트리로 미러링하여 미러 레지스트리 콘텐츠를 업데이트할 수 있습니다. 다음에 oc-mirror 플러그인을 실행할 때 이전 실행 이후 신규 및 업데이트된 이미지만 포함하는 이미지 세트가 생성됩니다.

미러 레지스트리를 업데이트하는 동안 다음 고려 사항을 고려해야 합니다.

이미지가 생성되고 미러링된 최신 이미지 세트에 더 이상 포함되지 않는 경우 대상 미러 레지스트리에서 정리됩니다. 따라서 차등 이미지 세트만 생성되고 미러링되도록 다음 주요 구성 요소의 동일한 조합에 대한 이미지를 업데이트해야 합니다.

이미지 세트 구성

대상 레지스트리

스토리지 구성

미러링하거나 미러링할 디스크의 경우 이미지를 정리할 수 있습니다. 워크플로우를 미러링할 수 있습니다.

생성된 이미지 세트를 대상 미러 레지스트리로 순서대로 푸시해야 합니다. 생성된 이미지 세트 아카이브 파일의 파일 이름에서 시퀀스 번호를 파생할 수 있습니다.

oc-mirror 플러그인에서 생성한 메타데이터 이미지를 삭제하거나 수정하지 마십시오.

초기 이미지 세트 생성 중에 미러 레지스트리에 대한 최상위 네임스페이스를 지정한 경우 동일한 미러 레지스트리에 대해 oc-mirror 플러그인을 실행할 때마다 이 동일한 네임스페이스를 사용해야 합니다.

미러 레지스트리 콘텐츠를 업데이트하는 워크플로우에 대한 자세한 내용은 "High Level workflow" 섹션을 참조하십시오.

#### 7.9.1. 미러 레지스트리 업데이트 예

이 섹션에서는 미러 레지스트리를 디스크에서 미러 미러 레지스트리로 업데이트하는 사용 사례에 대해 설명합니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  platform:
    channels:
      - name: stable-4.12
        minVersion: 4.12.1
        maxVersion: 4.12.1
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.14
      packages:
        - name: rhacs-operator
          channels:
          - name: stable
```

#### 7.9.1.1. 기존 이미지를 정리하여 특정 OpenShift Container Platform 버전 미러링

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  platform:
    channels:
      - name: stable-4.13
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.14
      packages:
        - name: rhacs-operator
          channels:
          - name: stable
```

1. `stable-4.13` 으로 교체하면 `stable-4.12` 의 모든 이미지가 정리됩니다.

#### 7.9.1.2. 기존 이미지를 정리하여 Operator의 최신 버전으로 업데이트

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  platform:
    channels:
      - name: stable-4.12
        minVersion: 4.12.1
        maxVersion: 4.12.1
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.14
      packages:
        - name: rhacs-operator
          channels:
          - name: stable
```

1. 버전을 지정하지 않고 동일한 채널을 사용하면 기존 이미지 및 최신 버전의 이미지 업데이트가 정리됩니다.

#### 7.9.1.3. 기존 Operator를 정리하여 새 Operator 미러링

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  platform:
    channels:
      - name: stable-4.12
        minVersion: 4.12.1
        maxVersion: 4.12.1
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.14
      packages:
        - name: <new_operator_name>
          channels:
          - name: stable
```

1. `rhacs-operator` 를 `new_operator_name` 으로 교체하면 Kubernetes Operator의 Red Hat Advanced Cluster Security가 정리됩니다.

#### 7.9.1.4. 모든 OpenShift Container Platform 이미지 정리

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  platform:
    channels:
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.14
      packages:
```

추가 리소스

이미지 세트 구성 예

부분적으로 연결이 끊긴 환경에서 이미지 세트 미러링

완전히 연결이 끊긴 환경에서 이미지 세트 미러링

oc-mirror에서 생성한 리소스를 사용하도록 클러스터 구성

### 7.10. 시험 실행 수행

oc-mirror를 사용하여 실제로 이미지를 미러링하지 않고 시험 실행을 수행할 수 있습니다. 이를 통해 미러링된 이미지 목록과 미러 레지스트리에서 정리되는 이미지를 검토할 수 있습니다. 또한 예행 실행을 사용하면 이미지 세트 구성으로 오류를 조기에 발견하거나 다른 툴과 함께 생성된 이미지 목록을 사용하여 미러링 작업을 수행할 수 있습니다.

사전 요구 사항

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

oc-mirror CLI 플러그인을 설치했습니다.

이미지 세트 구성 파일을 생성했습니다.

프로세스

`--dry-run` 플래그와 함께 아래 명령을 실행하여 예행 실행을 수행합니다.

```shell
oc mirror
```

```shell-session
$ oc mirror --config=./imageset-config.yaml \
  docker://registry.example:5000            \
  --dry-run
```

1. 생성된 이미지 세트 구성 파일을 전달합니다. 이 절차에서는 `imageset-config.yaml` 이라는 이름을 가정합니다.

2. 미러 레지스트리를 지정합니다. `--dry-run` 플래그를 사용하는 한 이 레지스트리에 미러링된 것은 없습니다.

3. `--dry-run` 플래그를 사용하여 실제 이미지 세트 파일이 아닌 시험 실행 아티팩트를 생성합니다.

```shell-session
Checking push permissions for registry.example:5000
Creating directory: oc-mirror-workspace/src/publish
Creating directory: oc-mirror-workspace/src/v2
Creating directory: oc-mirror-workspace/src/charts
Creating directory: oc-mirror-workspace/src/release-signatures
No metadata detected, creating new workspace
wrote mirroring manifests to oc-mirror-workspace/operators.1658342351/manifests-redhat-operator-index

...

info: Planning completed in 31.48s
info: Dry run complete
Writing image mapping to oc-mirror-workspace/mapping.txt
```

생성된 작업 공간 디렉터리로 이동합니다.

```shell-session
$ cd oc-mirror-workspace/
```

생성된 `mapping.txt` 파일을 검토합니다.

이 파일에는 미러링된 모든 이미지 목록이 포함되어 있습니다.

생성된 `prune-plan.json` 파일을 검토합니다.

이 파일에는 이미지 세트가 게시될 때 미러 레지스트리에서 정리할 모든 이미지 목록이 포함되어 있습니다.

참고

cleanup `-plan.json 파일은 oc-mirror 명령이 미러 레지스트리를 가리키며 정리할` 이미지가 있는 경우에만 생성됩니다.

### 7.11. 로컬 OCI Operator 카탈로그 포함

OpenShift Container Platform 릴리스, Operator 카탈로그 및 추가 이미지를 레지스트리에서 부분적으로 연결이 끊긴 클러스터로 미러링하는 동안 디스크의 로컬 파일 기반 카탈로그의 Operator 카탈로그 이미지를 포함할 수 있습니다. 로컬 카탈로그는 OCI(Open Container Initiative) 형식이어야 합니다.

로컬 카탈로그 및 해당 콘텐츠는 이미지 세트 구성 파일의 필터링 정보를 기반으로 대상 미러 레지스트리에 미러링됩니다.

중요

로컬 OCI 카탈로그를 미러링할 때 OpenShift Container Platform 릴리스 또는 로컬 OCI 형식의 카탈로그와 함께 미러링하려는 추가 이미지를 레지스트리에서 가져와야 합니다.

디스크에 oc-mirror 이미지 세트 파일과 함께 OCI 카탈로그를 미러링할 수 없습니다.

OCI 기능을 사용하는 한 가지 사용 사례는 CI/CD 시스템이 디스크의 위치에 OCI 카탈로그를 빌드하는 경우이고, OpenShift Container Platform 릴리스와 함께 미러 레지스트리에 해당 OCI 카탈로그를 미러링하려는 경우입니다.

참고

OpenShift Container Platform 4.12용 oc-mirror 플러그인에 대한 기술 프리뷰 OCI 로컬 카탈로그 기능을 사용한 경우 oc-mirror 플러그인의 OCI 로컬 카탈로그 기능을 사용하여 카탈로그를 로컬로 복사하고 OCI 형식으로 변환하여 완전히 연결이 끊긴 클러스터로 미러링할 수 없습니다.

사전 요구 사항

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스할 수 있습니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

oc-mirror CLI 플러그인을 설치했습니다.

프로세스

이미지 세트 구성 파일을 생성하고 필요에 따라 설정을 조정합니다.

다음 예제 이미지 세트 구성은 OpenShift Container Platform 릴리스 및 `registry.redhat.io` 의 UBI 이미지와 함께 디스크에서 OCI 카탈로그를 미러링합니다.

```yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v1alpha2
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  platform:
    channels:
    - name: stable-4.20
      type: ocp
    graph: false
  operators:
  - catalog: oci:///home/user/oc-mirror/my-oci-catalog
    targetCatalog: my-namespace/redhat-operator-index
    packages:
    - name: aws-load-balancer-operator
  - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
    packages:
    - name: rhacs-operator
  additionalImages:
  - name: registry.redhat.io/ubi9/ubi:latest
```

1. 이미지 세트 메타데이터를 저장할 백엔드 위치를 설정합니다. 이 위치는 레지스트리 또는 로컬 디렉터리일 수 있습니다. `storageConfig` 값을 지정해야 합니다.

2. 선택적으로 `registry.redhat.io` 에서 미러링할 OpenShift Container Platform 릴리스를 포함합니다.

3. 디스크의 OCI 카탈로그 위치에 대한 절대 경로를 지정합니다. OCI 기능을 사용하는 경우 경로는 `oci://` 로 시작해야 합니다.

4. 필요한 경우 카탈로그를 미러링할 대체 네임스페이스와 이름을 지정합니다.

5. 필요한 경우 레지스트리에서 가져올 추가 Operator 카탈로그를 지정합니다.

6. 선택적으로 레지스트리에서 가져올 추가 이미지를 지정합니다.

참고

oc-mirror 플러그인 v2에서는 `additionalImages` 아래에 나열된 모든 이미지에 대해 명시적 레지스트리 호스트 이름을 사용해야 합니다. 그렇지 않으면 이미지가 잘못된 대상 경로로 미러링됩니다.

아래 명령을 실행하여 OCI 카탈로그를 대상 미러 레지스트리에 미러링합니다.

```shell
oc mirror
```

```shell-session
$ oc mirror --config=./imageset-config.yaml \
  docker://registry.example:5000
```

1. 이미지 세트 구성 파일을 전달합니다. 이 절차에서는 `imageset-config.yaml` 이라는 이름을 가정합니다.

2. 콘텐츠를 미러링할 레지스트리를 지정합니다. 레지스트리는 다음 명령으로 시작해야 합니다. 미러 레지스트리에 최상위 네임스페이스를 지정하는 경우 후속 실행 시 동일한 네임스페이스를 사용해야 합니다.

```shell
docker://
```

선택적으로 다른 플래그를 지정하여 OCI 기능의 동작을 조정할 수 있습니다.

`--oci-insecure-signature-policy`

서명을 대상 미러 레지스트리로 내보내지 마십시오.

`--oci-registries-config`

TOML 형식의 `registries.conf` 파일의 경로를 지정합니다. 이미지 세트 구성 파일을 변경하지 않고도 테스트를 위한 사전 프로덕션 위치와 같은 다른 레지스트리에서 미러링할 수 있습니다. 이 플래그는 다른 미러링된 콘텐츠가 아닌 로컬 OCI 카탈로그에만 영향을 미칩니다.

```plaintext
[[registry]]
 location = "registry.redhat.io:5000"
 insecure = false
 blocked = false
 mirror-by-digest-only = true
 prefix = ""
 [[registry.mirror]]
    location = "preprod-registry.example.com"
    insecure = false
```

다음 단계

oc-mirror에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

추가 리소스

oc-mirror에서 생성한 리소스를 사용하도록 클러스터 구성

### 7.12. 이미지 세트 구성 매개변수

oc-mirror 플러그인에는 미러링할 이미지를 정의하는 이미지 세트 구성 파일이 필요합니다. 다음 표에는 `ImageSetConfiguration` 리소스에 사용 가능한 매개변수가 나열되어 있습니다.

| 매개변수 | 설명 | 값 |
| --- | --- | --- |
| `apiVersion` | `ImageSetConfiguration` 콘텐츠의 API 버전입니다. | 문자열. 예: `mirror.openshift.io/v1alpha2` . |
| `archiveSize` | 이미지 세트 내의 각 아카이브 파일의 최대 크기(GiB)입니다. | 정수. 예: `4` |
| `mirror` | 이미지 세트의 구성입니다. | 개체 |
| `mirror.additionalImages` | 이미지 세트의 추가 이미지 구성입니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] additionalImages: - name: registry.redhat.io/ubi8/ubi:latest [/CODE] |
| `mirror.additionalImages.name` | 미러링할 이미지의 태그 또는 다이제스트입니다. | 문자열. 예: `registry.redhat.io/ubi8/ubi:latest` |
| `mirror.blockedImages` | 미러링을 차단할 이미지의 전체 태그, 다이제스트 또는 패턴입니다. | 문자열 배열입니다. 예: `docker.io/ Cryostat/alpine` |
| `mirror.helm` | 이미지 세트의 helm 구성입니다. oc-mirror 플러그인은 렌더링 시 사용자 입력이 필요하지 않은 helm 차트만 지원합니다. | 개체 |
| `mirror.helm.local` | 미러링할 로컬 helm 차트입니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] local: - name: podinfo path: /test/podinfo-5.0.0.tar.gz [/CODE] |
| `mirror.helm.local.name` | 미러링할 로컬 helm 차트의 이름입니다. | 문자열. 예: `podinfo` . |
| `mirror.helm.local.path` | 미러링할 로컬 helm 차트의 경로입니다. | 문자열. 예: `/test/podinfo-5.0.0.tar.gz` . |
| `mirror.helm.repositories` | 미러링할 원격 helm 리포지토리입니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] repositories: - name: podinfo url: https://example.github.io/podinfo charts: - name: podinfo version: 5.0.0 [/CODE] |
| `mirror.helm.repositories.name` | 미러링할 helm 저장소 이름입니다. | 문자열. 예: `podinfo` . |
| `mirror.helm.repositories.url` | 미러링할 helm 리포지토리의 URL입니다. | 문자열. 예: `https://example.github.io/podinfo` . |
| `mirror.helm.repositories.charts` | 미러링할 원격 helm 차트입니다. | 개체의 배열입니다. |
| `mirror.helm.repositories.charts.name` | 미러링할 helm 차트의 이름입니다. | 문자열. 예: `podinfo` . |
| `mirror.helm.repositories.charts.version` | 미러링할 이름이 helm 차트의 버전입니다. | 문자열. 예: `5.0.0` . |
| `mirror.operators` | 이미지 세트의 Operator 구성 | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20 packages: - name: elasticsearch-operator minVersion: '2.4.0' [/CODE] |
| `mirror.operators.catalog` | 이미지 세트에 포함할 Operator 카탈로그입니다. | 문자열. 예: `registry.redhat.io/redhat/redhat-operator-index:v4.20` . |
| `mirror.operators.full` | `true` 인 경우 전체 카탈로그, Operator 패키지 또는 Operator 채널을 다운로드합니다. | 부울. 기본값은 `false` 입니다. |
| `mirror.operators.packages` | Operator 패키지 구성입니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] operators: - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20 packages: - name: elasticsearch-operator minVersion: '5.2.3-31' [/CODE] |
| `mirror.operators.packages.name` | 이미지 세트에 포함할 Operator 패키지 이름 | 문자열. 예: `elasticsearch-operator` . |
| `mirror.operators.packages.channels` | Operator 패키지 채널 구성입니다. | 개체 |
| `mirror.operators.packages.channels.name` | 이미지 세트에 포함할 Operator 채널 이름은 패키지 내에서 고유합니다. | 문자열. 예: `fast` 또는 `stable-v4.20` . |
| `mirror.operators.packages.channels.maxVersion` | Operator의 가장 높은 버전은 존재하는 모든 채널에서 미러링됩니다. 자세한 내용은 다음 참고 사항을 참조하십시오. | 문자열. 예: `5.2.3-31` |
| `mirror.operators.packages.channels.minBundle` | 포함할 최소 번들의 이름과 업데이트 그래프의 모든 번들과 채널 헤드에 대한 모든 번들의 이름입니다. 이름이 지정된 번들에 의미 체계 버전 메타데이터가 없는 경우에만 이 필드를 설정합니다. | 문자열. 예: `bundleName` |
| `mirror.operators.packages.channels.minVersion` | 존재하는 모든 채널에 미러링할 Operator의 가장 낮은 버전입니다. 자세한 내용은 다음 참고 사항을 참조하십시오. | 문자열. 예: `5.2.3-31` |
| `mirror.operators.packages.maxVersion` | 존재하는 모든 채널에 미러링할 Operator의 가장 높은 버전입니다. 자세한 내용은 다음 참고 사항을 참조하십시오. | 문자열. 예: `5.2.3-31` . |
| `mirror.operators.packages.minVersion` | 존재하는 모든 채널에 미러링할 Operator의 가장 낮은 버전입니다. 자세한 내용은 다음 참고 사항을 참조하십시오. | 문자열. 예: `5.2.3-31` . |
| `mirror.operators.skipDependencies` | `true` 인 경우 번들의 종속 항목은 포함되지 않습니다. | 부울. 기본값은 `false` 입니다. |
| `mirror.operators.targetCatalog` | 참조된 카탈로그를 미러링하는 대체 이름 및 선택적 네임스페이스 계층 구조입니다. | 문자열. 예: `my-namespace/my-operator-catalog` |
| `mirror.operators.targetName` | 참조된 카탈로그를 미러링하는 대체 이름입니다. `targetName` 매개변수는 더 이상 사용되지 않습니다. 대신 `targetCatalog` 매개변수를 사용합니다. | 문자열. 예: `my-operator-catalog` |
| `mirror.operators.targetTag` | `targetName` 또는 `targetCatalog` 에 추가할 대체 태그입니다. | 문자열. 예: `v1` |
| `mirror.platform` | 이미지 세트의 플랫폼 구성입니다. | 개체 |
| `mirror.platform.architectures` | 미러링할 플랫폼 릴리스 페이로드의 아키텍처입니다. | 문자열 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] architectures: - amd64 - arm64 - multi - ppc64le - s390x [/CODE] 기본값은 `amd64` 입니다. 값 `multi` 를 사용하면 사용 가능한 모든 아키텍처에 대해 미러링이 지원되므로 개별 아키텍처를 지정할 필요가 없습니다. |
| `mirror.platform.channels` | 이미지 세트의 플랫폼 채널 구성입니다. | 개체의 배열입니다. 예를 들면 다음과 같습니다. [CODE language="yaml" wrap_hint="true" overflow_hint="toggle"] channels: - name: stable-4.10 - name: stable-4.20 [/CODE] |
| `mirror.platform.channels.full` | `true` 인 경우 `minVersion` 을 채널의 첫 번째 릴리스로 설정하고 `maxVersion` 을 채널의 마지막 릴리스로 설정합니다. | 부울. 기본값은 `false` 입니다. |
| `mirror.platform.channels.name` | 릴리스 채널의 이름입니다. | 문자열. 예: `stable-4.20` |
| `mirror.platform.channels.minVersion` | 미러링할 참조된 플랫폼의 최소 버전입니다. | 문자열. 예: `4.12.6` |
| `mirror.platform.channels.maxVersion` | 참조된 플랫폼의 가장 높은 버전을 미러링합니다. | 문자열. 예: `4.20.1` |
| `mirror.platform.channels.shortestPath` | 경로 미러링 또는 전체 범위 미러링을 전환합니다. | 부울. 기본값은 `false` 입니다. |
| `mirror.platform.channels.type` | 미러링할 플랫폼의 유형입니다. | 문자열. 예: `ocp` 또는 `okd` . 기본값은 `ocp` 입니다. |
| `mirror.platform.graph` | OSUS 그래프가 이미지 세트에 추가되고 나중에 미러에 게시되는지 여부를 나타냅니다. | 부울. 기본값은 `false` 입니다. |
| `storageConfig` | 이미지 세트의 백엔드 구성입니다. | 개체 |
| `storageConfig.local` | 이미지 세트의 로컬 백엔드 구성입니다. | 개체 |
| `storageConfig.local.path` | 이미지 세트 메타데이터를 포함할 디렉터리의 경로입니다. | 문자열. 예: `./path/to/dir/` . |
| `storageConfig.registry` | 이미지 세트의 레지스트리 백엔드 구성입니다. | 개체 |
| `storageConfig.registry.imageURL` | 백엔드 레지스트리 URI입니다. URI에 네임스페이스 참조를 선택적으로 포함할 수 있습니다. | 문자열. 예: `quay.io/myuser/imageset:metadata` . |
| `storageConfig.registry.skipTLS` | 필요한 경우 참조된 백엔드 레지스트리의 TLS 확인을 건너뜁니다. | 부울. 기본값은 `false` 입니다. |

참고

`minVersion` 및 `maxVersion` 속성을 사용하여 특정 Operator 버전 범위를 필터링하면 여러 채널 헤드 오류가 발생할 수 있습니다. 오류 메시지는 `여러 채널 헤드` 가 있음을 나타냅니다. 필터가 적용되면 Operator의 업데이트 그래프가 잘립니다.

Operator Lifecycle Manager를 사용하려면 모든 Operator 채널에 정확히 하나의 엔드 포인트, 즉 최신 버전의 Operator가 있는 업데이트 그래프를 구성하는 버전이 포함되어 있어야 합니다. 필터 범위가 적용되면 해당 그래프는 두 개 이상의 개별 그래프 또는 두 개 이상의 끝점이 있는 그래프로 전환할 수 있습니다.

이 오류를 방지하려면 최신 버전의 Operator를 필터링하지 마십시오. Operator에 따라 오류가 계속 실행되는 경우 `maxVersion` 속성을 늘리거나 `minVersion` 속성을 줄여야 합니다. 모든 Operator 그래프는 다를 수 있으므로 오류가 해결될 때까지 이러한 값을 조정해야 할 수 있습니다.

### 7.13. 이미지 세트 구성 예

다음 `ImageSetConfiguration` 파일 예제에서는 다양한 미러링 사용 사례에 대한 구성을 보여줍니다.

#### 7.13.1. 사용 사례: 최고 수준의 OpenShift Container Platform 업데이트 경로 포함

다음 `ImageSetConfiguration` 파일은 로컬 스토리지 백엔드를 사용하며 `4.11.37` 의 최소 버전에서 `4.12.15` 의 최대 버전으로 가장 짧은 업데이트 경로를 포함하여 모든 OpenShift Container Platform 버전을 포함합니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  platform:
    channels:
      - name: stable-4.12
        minVersion: 4.11.37
        maxVersion: 4.12.15
        shortestPath: true
```

#### 7.13.2. 사용 사례: 모든 OpenShift Container Platform 버전을 최소에서 다중 아키텍처 릴리스의 최신 버전으로 포함

다음 `ImageSetConfiguration` 파일은 레지스트리 스토리지 백엔드를 사용하며 최소 `4.13.4` 부터 채널의 최신 버전에 모든 OpenShift Container Platform 버전이 포함되어 있습니다.

이 이미지 세트 구성으로 oc-mirror를 호출할 때마다 `stable-4.13` 채널의 최신 릴리스가 평가되므로 정기적으로 oc-mirror를 실행하면 OpenShift Container Platform 이미지의 최신 릴리스를 자동으로 수신할 수 있습니다.

`platform.architectures` 값을 `multi` 로 설정하면 다중 아키텍처 릴리스에서 미러링이 지원되는지 확인할 수 있습니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  registry:
    imageURL: example.com/mirror/oc-mirror-metadata
    skipTLS: false
mirror:
  platform:
    architectures:
      - "multi"
    channels:
      - name: stable-4.13
        minVersion: 4.13.4
        maxVersion: 4.13.6
```

#### 7.13.3. 사용 사례: Operator 버전 최소에서 최신 버전 포함

다음 `ImageSetConfiguration` 파일은 로컬 스토리지 백엔드를 사용하며 `stable` 채널에서 4.0.1 이상 버전에서 실행되는 Kubernetes Operator용 Red Hat Advanced Cluster Security만 포함합니다.

참고

최소 또는 최대 버전 범위를 지정하면 해당 범위의 모든 Operator 버전이 제공되지 않을 수 있습니다.

기본적으로 oc-mirror는 OLM(Operator Lifecycle Manager) 사양에서 건너뛰거나 최신 버전으로 교체되는 버전을 제외합니다. 건너뛰는 Operator 버전은 CVE의 영향을 받거나 버그가 포함될 수 있습니다. 대신 최신 버전을 사용합니다. 건너뛰거나 교체된 버전에 대한 자세한 내용은 OLM을 사용하여 업데이트 그래프 생성을 참조하십시오.

지정된 범위의 모든 Operator 버전을 수신하려면 `mirror.operators.full` 필드를 `true` 로 설정할 수 있습니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  local:
    path: /home/user/metadata
mirror:
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
      packages:
        - name: rhacs-operator
          channels:
          - name: stable
            minVersion: 4.0.1
```

참고

latest 대신 최대 버전을 지정하려면 `mirror.operators.packages.channels.maxVersion` 필드를 설정합니다.

#### 7.13.4. 사용 사례: Nutanix CSI Operator 포함

다음 `ImageSetConfiguration` 파일은 로컬 스토리지 백엔드를 사용하며 Nutanix CSI Operator, OSUS(OpenShift Update Service) 그래프 이미지 및 추가 Red Hat UBI(Universal Base Image)를 포함합니다.

```yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v1alpha2
storageConfig:
  registry:
    imageURL: mylocalregistry/ocp-mirror/openshift4
    skipTLS: false
mirror:
  platform:
    channels:
    - name: stable-4.11
      type: ocp
    graph: true
  operators:
  - catalog: registry.redhat.io/redhat/certified-operator-index:v4.20
    packages:
    - name: nutanixcsioperator
      channels:
      - name: stable
  additionalImages:
  - name: registry.redhat.io/ubi9/ubi:latest
```

#### 7.13.5. 사용 사례: 기본 Operator 채널 포함

다음 `ImageSetConfiguration` 파일에는 OpenShift Elasticsearch Operator의 `stable-5.7` 및 `stable` 채널이 포함되어 있습니다.

`stable-5.7` 채널의 패키지만 필요한 경우에도 Operator의 기본 채널이므로 `stable` 채널도 `ImageSetConfiguration` 파일에 포함되어야 합니다. 해당 채널에서 번들을 사용하지 않는 경우에도 Operator 패키지의 기본 채널을 항상 포함해야 합니다.

작은 정보

다음 명령을 실행하여 기본 채널을 찾을 수 있습니다. >.

```shell
oc mirror list operators --catalog=<catalog_name> --package=<package_name
```

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  registry:
    imageURL: example.com/mirror/oc-mirror-metadata
    skipTLS: false
mirror:
  operators:
  - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
    packages:
    - name: elasticsearch-operator
      channels:
      - name: stable-5.7
      - name: stable
```

#### 7.13.6. 사용 사례: 전체 카탈로그 포함(모든 버전)

다음 `ImageSetConfiguration` 파일은 `mirror.operators.full` 필드를 `true` 로 설정하여 전체 Operator 카탈로그의 모든 버전을 포함합니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  registry:
    imageURL: example.com/mirror/oc-mirror-metadata
    skipTLS: false
mirror:
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
      full: true
```

#### 7.13.7. 사용 사례: 전체 카탈로그 포함(채널 헤드만 해당)

다음 `ImageSetConfiguration` 파일에는 전체 Operator 카탈로그의 채널 헤드가 포함되어 있습니다.

기본적으로 카탈로그의 각 Operator에 대해 oc-mirror에는 기본 채널의 최신 Operator 버전(채널 헤드)이 포함됩니다. 채널 헤드뿐만 아니라 모든 Operator 버전을 미러링하려면 `mirror.operators.full` 필드를 `true` 로 설정해야 합니다.

이 예제에서는 `targetCatalog` 필드를 사용하여 카탈로그를 미러링할 대체 네임스페이스와 이름을 지정합니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  registry:
    imageURL: example.com/mirror/oc-mirror-metadata
    skipTLS: false
mirror:
  operators:
  - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
    targetCatalog: my-namespace/my-operator-catalog
```

#### 7.13.8. 사용 사례: 임의의 이미지 및 helm 차트 포함

다음 `ImageSetConfiguration` 파일은 레지스트리 스토리지 백엔드를 사용하며 helm 차트 및 추가 Red Hat UBI(Universal Base Image)를 포함합니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
archiveSize: 4
storageConfig:
  registry:
    imageURL: example.com/mirror/oc-mirror-metadata
    skipTLS: false
mirror:
 platform:
   architectures:
     - "s390x"
   channels:
     - name: stable-4.20
 operators:
   - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
 helm:
   repositories:
     - name: redhat-helm-charts
       url: https://raw.githubusercontent.com/redhat-developer/redhat-helm-charts/master
       charts:
         - name: ibm-mongodb-enterprise-helm
           version: 0.2.0
 additionalImages:
   - name: registry.redhat.io/ubi9/ubi:latest
```

#### 7.13.9. 사용 사례: EUS 릴리스의 업그레이드 경로 포함

다음 `ImageSetConfiguration` 파일에는 `eus-<version` > 채널이 포함되어 있습니다. 여기서 `maxVersion` 값은 `minVersion` 값보다 두 개 이상의 마이너 버전입니다.

예를 들어 이 `ImageSetConfiguration` 파일에서 `minVersion` 은 `4.12.28` 로 설정되고 `eus-4.14` 채널의 `maxVersion` 은 `4.14.16` 입니다.

```yaml
kind: ImageSetConfiguration
apiVersion: mirror.openshift.io/v2alpha1
mirror:
  platform:
    graph: true # Required for the OSUS Operator
    architectures:
    - amd64
    channels:
    - name: stable-4.12
      minVersion: '4.12.28'
      maxVersion: '4.12.28'
      shortestPath: true
      type: ocp
    - name: eus-4.14
      minVersion: '4.12.28'
      maxVersion: '4.14.16'
      shortestPath: true
      type: ocp
```

#### 7.13.10. 사용 사례: 다중 클러스터 엔진 Operator에 대한 다중 아키텍처 OpenShift Container Platform 이미지 및 카탈로그 포함

다음 `ImageSetConfiguration` 파일에는 Kubernetes Operator용 멀티 클러스터 엔진 및 채널의 최소 `4.20.0` 버전에서 시작하는 모든 OpenShift Container Platform 버전이 포함되어 있습니다.

```yaml
apiVersion: mirror.openshift.io/v1alpha2
kind: ImageSetConfiguration
storageConfig:
  registry:
    imageURL: agent.agent.example.com:5000/openshift/release/metadata:latest/openshift/release/metadata:latest
mirror:
  platform:
    architectures:
      - "multi"
    channels:
    - name: stable-4.20
      minVersion: 4.20.0
      maxVersion: 4.20.1
      type: ocp
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.20
      packages:
        - name: multicluster-engine
```

### 7.14. oc-mirror에 대한 명령 참조

다음 표에서는 하위 명령 및 플래그를 설명합니다.

```shell
oc mirror
```

| 하위 명령 | 설명 |
| --- | --- |
| `완료` | 지정된 쉘에 대한 자동 완성 스크립트를 생성합니다. |
| `describe` | 이미지 세트의 내용을 출력합니다. |
| `help` | 하위 명령에 대한 도움말을 표시합니다. |
| `init` | 초기 이미지 세트 구성 템플릿을 출력합니다. |
| `list` | 사용 가능한 플랫폼 및 Operator 콘텐츠 및 해당 버전을 나열합니다. |
| `version` | oc-mirror 버전을 출력합니다. |

| 플래그 | 설명 |
| --- | --- |
| `-c` , `--config` `<string>` | 이미지 세트 구성 파일의 경로를 지정합니다. |
| `--continue-on-error` | 이미지 풀 관련 오류가 발생하면 계속 진행하고 가능한 한 많이 미러링하려고 합니다. |
| `--dest-skip-tls` | 대상 레지스트리에 대한 TLS 검증을 비활성화합니다. |
| `--dest-use-http` | 대상 레지스트리에 일반 HTTP를 사용합니다. |
| `--dry-run` | 이미지를 미러링하지 않고 작업을 출력합니다. `mapping.txt` 및 prune `-plan.json` 파일을 생성합니다. |
| `--from <string>` | 대상 레지스트리에 로드할 oc-mirror 실행으로 생성된 이미지 세트 아카이브의 경로를 지정합니다. |
| `-h` , `--help` | 도움말을 표시합니다. |
| `--ignore-history` | 이미지를 다운로드하고 레이어를 패키징할 때 이전 미러를 무시합니다. 증분 미러링을 비활성화하고 더 많은 데이터를 다운로드할 수 있습니다. |
| `--manifests-only` | mirror 레지스트리를 사용하지만 실제로 이미지를 미러링하지 않도록 `ImageContentSourcePolicy` 오브젝트에 대한 매니페스트를 생성합니다. 이 플래그를 사용하려면 `--from` 플래그를 사용하여 이미지 세트 아카이브를 전달해야 합니다. |
| `--max-nested-paths <int>` | 중첩된 경로를 제한하는 대상 레지스트리의 최대 중첩된 경로 수를 지정합니다. 기본값은 `0` 입니다. |
| `--max-per-registry <int>` | 레지스트리당 허용된 동시 요청 수를 지정합니다. 기본값은 `6` 입니다. |
| `--oci-insecure-signature-policy` | 로컬 OCI 카탈로그를 미러링할 때 서명을 내보내지 마십시오( `--include-local-oci-catalogs` ). |
| `--oci-registries-config` | 로컬 OCI 카탈로그를 미러링할 때 복사할 대체 레지스트리 위치를 지정할 레지스트리 구성 파일을 제공합니다( `--include-local-oci-catalogs` ). |
| `--skip-cleanup` | 아티팩트 디렉터리 제거를 건너뜁니다. |
| `--skip-image-pin` | Operator 카탈로그의 다이제스트 핀으로 이미지 태그를 교체하지 마십시오. |
| `--skip-metadata-check` | 이미지 세트를 게시할 때 메타데이터를 건너뜁니다. 참고 이미지 세트가 `--ignore-history` 플래그를 사용하여 생성된 경우에만 권장됩니다. |
| `--skip-missing` | 이미지를 찾을 수 없는 경우 오류를 보고하고 실행을 중단하는 대신 이미지를 건너뜁니다. 이미지 세트 구성에 명시적으로 지정된 사용자 지정 이미지에는 적용되지 않습니다. |
| `--skip-pruning` | 대상 미러 레지스트리에서 이미지 자동 정리를 비활성화합니다. |
| `--skip-verification` | 다이제스트 확인을 건너뜁니다. |
| `--source-skip-tls` | 소스 레지스트리에 대한 TLS 검증을 비활성화합니다. |
| `--source-use-http` | 소스 레지스트리에 일반 HTTP를 사용합니다. |
| `-v` , `--verbose` `<int>` | 로그 수준 상세 정보 표시의 번호를 지정합니다. 유효한 값은 `0` - `9` 입니다. 기본값은 `0` 입니다. |

### 7.15. 추가 리소스

연결이 끊긴 환경의 클러스터 업데이트 정보

## 8장. oc adm 명령을 사용하여 연결이 끊긴 설치의 이미지 미러링

클러스터가 외부 콘텐츠에 대한 조직의 제어를 충족하는 컨테이너 이미지만 사용하도록 할 수 있습니다. 제한된 네트워크에서 프로비저닝된 인프라에 클러스터를 설치하기 전에 필요한 컨테이너 이미지를 해당 환경에 미러링해야 합니다.

아래 명령을 사용하면 OpenShift에서 릴리스 및 카탈로그 이미지를 미러링할 수 있습니다. 컨테이너 이미지를 미러링하려면 미러링을 위한 레지스트리가 있어야 합니다.

```shell
oc adm
```

중요

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스해야 합니다. 이 절차에서는 네트워크와 인터넷에 모두 액세스할 수 있는 미러 호스트에 미러 레지스트리를 배치합니다. 미러 호스트에 액세스할 수 없는 경우 연결이 끊긴 클러스터에 사용할 Operator 카탈로그를 미러링 하여 네트워크 경계를 이동할 수 있는 장치에 이미지를 복사합니다.

### 8.1. 사전 요구 사항

다음 레지스트리 중 하나와 같이 OpenShift Container Platform 클러스터를 호스팅할 위치에 Docker v2-2 를 지원하는 컨테이너 이미지 레지스트리가 있어야 합니다.

Red Hat Quay

JFrog Artifactory

Sonatype Nexus Repository

Harbor

Red Hat Quay에 대한 인타이틀먼트가 있는 경우 개념 증명 목적으로 또는 Red Hat Quay Operator를 사용하여 Red Hat Quay 배포에 대한 설명서를 참조하십시오. 레지스트리를 선택 및 설치하는 데 추가 지원이 필요한 경우 영업 담당자 또는 Red Hat 지원팀에 문의하십시오.

컨테이너 이미지 레지스트리에 대한 기존 솔루션이 없는 경우 OpenShift Container Platform 구독자에게 Red Hat OpenShift의 미러 레지스트리 가 제공됩니다.

Red Hat OpenShift의 미러 레지스트리 는 서브스크립션에 포함되어 있으며 연결이 끊긴 설치에서 OpenShift Container Platform의 필요한 컨테이너 이미지를 미러링하는 데 사용할 수 있는 소규모 컨테이너 레지스트리입니다.

### 8.2. 미러 레지스트리 정보

필요한 컨테이너 이미지를 얻으려면 인터넷에 액세스해야 합니다. 대체 레지스트리를 사용하면 네트워크와 인터넷에 모두 액세스할 수 있는 미러 호스트에 미러 레지스트리를 배치합니다.

OpenShift Container Platform 설치 및 후속 제품 업데이트에 필요한 이미지를 Red Hat Quay, JFrog Artifactory, Sonatype Nexus Repository 또는 Harbor와 같은 컨테이너 미러 레지스트리에 미러링할 수 있습니다.

대규모 컨테이너 레지스트리에 액세스할 수 없는 경우 OpenShift Container Platform 서브스크립션에 포함된 소규모 컨테이너 레지스트리인 Red Hat OpenShift 에 미러 레지스트리를 사용할 수 있습니다.

Red Hat Quay, Red Hat OpenShift의 미러 레지스트리, Artifactory, Sonatype Nexus Repository 또는 Harbor와 같은 Docker v2-2 를 지원하는 컨테이너 레지스트리를 사용할 수 있습니다.

선택한 레지스트리에 관계없이 인터넷상의 Red Hat 호스팅 사이트의 콘텐츠를 격리된 이미지 레지스트리로 미러링하는 절차는 동일합니다. 콘텐츠를 미러링한 후 미러 레지스트리에서 이 콘텐츠를 검색하도록 각 클러스터를 설정합니다.

중요

OpenShift 이미지 레지스트리는 미러링 프로세스 중에 필요한 태그 없이 푸시를 지원하지 않으므로 대상 레지스트리로 사용할 수 없습니다.

Red Hat OpenShift의 미러 레지스트리가 아닌 컨테이너 레지스트리를 선택하는 경우 프로비저닝하는 클러스터의 모든 시스템에서 연결할 수 있어야 합니다. 레지스트리에 연결할 수 없는 경우 설치, 업데이트 또는 워크로드 재배치와 같은 일반 작업이 실패할 수 있습니다.

따라서 고가용성 방식으로 미러 레지스트리를 실행해야하며 미러 레지스트리는 최소한 OpenShift Container Platform 클러스터의 프로덕션 환경의 가용성조건에 일치해야 합니다.

미러 레지스트리를 OpenShift Container Platform 이미지로 채우면 다음 두 가지 시나리오를 수행할 수 있습니다. 호스트가 인터넷과 미러 레지스트리에 모두 액세스할 수 있지만 클러스터 노드에 액세스 할 수 없는 경우 해당 머신의 콘텐츠를 직접 미러링할 수 있습니다.

이 프로세스를 connected mirroring (미러링 연결)이라고 합니다. 그러한 호스트가 없는 경우 이미지를 파일 시스템에 미러링한 다음 해당 호스트 또는 이동식 미디어를 제한된 환경에 배치해야 합니다.

이 프로세스를 미러링 연결 해제 라고 합니다.

미러링된 레지스트리의 경우 가져온 이미지의 소스를 보려면 CRI-O 로그의 `Trying to access` 로그 항목을 검토해야 합니다. 노드에서 아래 명령을 사용하는 등의 이미지 가져오기 소스를 보는 다른 방법은 미러링되지 않은 이미지 이름을 표시합니다.

```shell
crictl images
```

참고

Red Hat은 OpenShift Container Platform에서 타사 레지스트리를 테스트하지 않습니다.

추가 정보

이미지 소스를 보려면 CRI-O 로그를 확인하는 방법에 대한 자세한 내용은 이미지 가져오기 소스 보기 를 참조하십시오.

### 8.3. 미러 호스트 준비

미러 단계를 수행하기 전에 호스트는 콘텐츠를 검색하고 원격 위치로 푸시할 준비가 되어 있어야 합니다.

#### 8.3.1. OpenShift CLI 설치

명령줄 인터페이스를 사용하여 OpenShift Container Platform과 상호 작용하기 위해 OpenShift CLI()를 설치할 수 있습니다. Linux, Windows 또는 macOS에 다음 명령을 설치할 수 있습니다.

```shell
oc
```

```shell
oc
```

중요

이전 버전의 다음 명령을 설치한 경우 OpenShift Container Platform의 모든 명령을 완료하는 데 해당 버전을 사용할 수 없습니다.

```shell
oc
```

새 버전의 다음 명령을 다운로드하여 설치합니다.

```shell
oc
```

#### 8.3.1.1. Linux에서 OpenShift CLI 설치

다음 절차를 사용하여 Linux에서 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

Red Hat 고객 포털에서 OpenShift Container Platform 다운로드 페이지로 이동합니다.

Product Variant 목록에서 아키텍처를 선택합니다.

버전 목록에서 적절한 버전을 선택합니다.

OpenShift v4.20 Linux Clients 항목 옆에 있는 지금 다운로드를 클릭하고 파일을 저장합니다.

아카이브의 압축을 풉니다.

```shell-session
$ tar xvf <file>
```

다음 명령바이너리를 `PATH` 에 있는 디렉터리에 배치합니다.

```shell
oc
```

`PATH` 를 확인하려면 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

검증

OpenShift CLI를 설치한 후 아래 명령을 사용할 수 있습니다.

```shell
oc
```

```shell-session
$ oc <command>
```

#### 8.3.1.2. Windows에서 OpenSfhit CLI 설치

다음 절차에 따라 Windows에 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

Red Hat 고객 포털에서 OpenShift Container Platform 다운로드 페이지로 이동합니다.

버전 목록에서 적절한 버전을 선택합니다.

OpenShift v4.20 Windows Client 항목 옆에 있는 지금 다운로드를 클릭하고 파일을 저장합니다.

ZIP 프로그램으로 아카이브의 압축을 풉니다.

다음 명령바이너리를 `PATH` 에 있는 디렉터리로 이동합니다.

```shell
oc
```

`PATH` 를 확인하려면 명령 프롬프트를 열고 다음 명령을 실행합니다.

```shell-session
C:\> path
```

검증

OpenShift CLI를 설치한 후 아래 명령을 사용할 수 있습니다.

```shell
oc
```

```shell-session
C:\> oc <command>
```

#### 8.3.1.3. macOS에 OpenShift CLI 설치

다음 절차에 따라 macOS에서 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

Red Hat 고객 포털에서 OpenShift Container Platform 다운로드 페이지로 이동합니다.

버전 드롭다운 목록에서 적절한 버전을 선택합니다.

OpenShift v4.20 macOS Clients 항목 옆에 있는 지금 다운로드를 클릭하고 파일을 저장합니다.

참고

macOS arm64의 경우 OpenShift v4.20 macOS arm64 Client 항목을 선택합니다.

아카이브의 압축을 해제하고 압축을 풉니다.

다음 명령바이너리 PATH의 디렉터리로 이동합니다.

```shell
oc
```

`PATH` 를 확인하려면 터미널을 열고 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

검증

아래 명령을 사용하여 설치를 확인합니다.

```shell
oc
```

```shell-session
$ oc <command>
```

### 8.4. 이미지를 미러링할 수 있는 인증 정보 설정

Red Hat에서 미러로 이미지를 미러링할 수 있도록 컨테이너 이미지 레지스트리 인증 정보 파일을 생성합니다. 설치 호스트에서 다음 단계를 완료합니다.

주의

클러스터를 설치할 때 이 이미지 레지스트리 인증 정보 파일을 풀 시크릿(pull secret)으로 사용하지 마십시오. 클러스터를 설치할 때 이 파일을 지정하면 클러스터의 모든 시스템에 미러 레지스트리에 대한 쓰기 권한이 부여됩니다.

사전 요구 사항

연결이 끊긴 환경에서 사용할 미러 레지스트리를 구성했습니다.

미러 레지스트리에서 이미지를 미러링할 이미지 저장소 위치를 확인했습니다.

이미지를 해당 이미지 저장소에 업로드할 수 있는 미러 레지스트리 계정을 제공하고 있습니다.

미러 레지스트리에 대한 쓰기 권한이 있습니다.

프로세스

Red Hat OpenShift Cluster Manager 에서 `registry.redhat.io` 풀 시크릿을 다운로드합니다.

다음 명령을 실행하여 풀 시크릿을 JSON 형식으로 복사합니다.

```shell-session
$ cat ./pull-secret | jq . > <path>/<pull_secret_file_in_json>
```

풀 시크릿을 저장할 디렉터리의 경로와 생성한 JSON 파일의 이름을 지정합니다.

```plaintext
{
  "auths": {
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

다음 명령을 실행하여 미러 레지스트리에 대한 base64로 인코딩된 사용자 이름 및 암호 또는 토큰을 생성합니다.

```shell-session
$ echo -n '<user_name>:<password>' | base64 -w0
```

`<user_name>` 및 `<password>` 의 경우 레지스트리에 설정한 사용자 이름 및 암호를 지정합니다.

```shell-session
BGVtbYk3ZHAtqXs=
```

JSON 파일을 편집하고 레지스트리를 설명하는 섹션을 추가합니다.

```plaintext
"auths": {
    "<mirror_registry>": {
      "auth": "<credentials>",
      "email": "you@example.com"
    }
  },
```

&lt `;mirror_registry` > 값의 경우 미러 레지스트리가 콘텐츠를 제공하는 데 사용하는 레지스트리 도메인 이름과 포트(선택 사항)를 지정합니다. 예: `registry.example.com` 또는 `registry.example.com:8443`.

&lt `;credentials&` gt; 값의 경우 미러 레지스트리의 base64 인코딩 사용자 이름과 암호를 지정합니다.

```plaintext
{
  "auths": {
    "registry.example.com": {
      "auth": "BGVtbYk3ZHAtqXs=",
      "email": "you@example.com"
    },
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

### 8.5. OpenShift Container Platform 이미지 저장소 미러링

클러스터 설치 또는 업그레이드 중에 사용할 OpenShift Container Platform 이미지 저장소를 레지스트리에 미러링합니다. 미러 호스트에서 다음 단계를 완료합니다.

사전 요구 사항

미러 호스트가 인터넷에 액세스할 수 있습니다.

네트워크가 제한된 환경에서 사용할 미러 레지스트리를 설정하고 설정한 인증서 및 인증 정보에 액세스할 수 있습니다.

Red Hat OpenShift Cluster Manager에서 풀 시크릿 을 다운로드하여 미러 저장소에 대한 인증을 포함하도록 수정했습니다.

자체 서명된 인증서를 사용하는 경우 인증서에 주체 대체 이름을 지정했습니다.

프로세스

OpenShift Container Platform 다운로드 페이지를 검토하여 설치할 OpenShift Container Platform 버전을 확인하고 리포지토리 태그 페이지에서 해당 태그를 확인합니다.

다음과 같은 필수 환경 변수를 설정합니다.

릴리스 버전을 내보냅니다.

```shell-session
$ OCP_RELEASE=<release_version>
```

& `lt;release_version` > 의 경우 설치할 OpenShift Container Platform 버전에 해당하는 태그를 지정합니다 (예: `4.20.1`).

로컬 레지스트리 이름 및 호스트 포트를 내보냅니다.

```shell-session
$ LOCAL_REGISTRY='<local_registry_host_name>:<local_registry_host_port>'
```

`<local_registry_host_name>` 의 경우 미러 저장소의 레지스트리 도메인 이름을 지정하고 `<local_registry_host_port>` 의 경우 콘텐츠를 제공하는데 사용되는 포트를 지정합니다.

로컬 저장소 이름을 내보냅니다.

```shell-session
$ LOCAL_REPOSITORY='<local_repository_name>'
```

`<local_repository_name>` 의 경우 레지스트리에 작성할 저장소 이름 (예: `ocp4/openshift4`)을 지정합니다.

미러링할 저장소 이름을 내보냅니다.

```shell-session
$ PRODUCT_REPO='openshift-release-dev'
```

프로덕션 환경의 릴리스의 경우 `openshift-release-dev` 를 지정해야 합니다.

레지스트리 풀 시크릿의 경로를 내보냅니다.

```shell-session
$ LOCAL_SECRET_JSON='<path_to_pull_secret>'
```

생성한 미러 레지스트리에 대한 풀 시크릿의 절대 경로 및 파일 이름을 `<path_to_pull_secret>` 에 지정합니다.

릴리스 미러를 내보냅니다.

```shell-session
$ RELEASE_NAME="ocp-release"
```

프로덕션 환경의 릴리스의 경우 `ocp-release` 를 지정해야 합니다.

클러스터의 아키텍처 유형을 내보냅니다.

```shell-session
$ ARCHITECTURE=<cluster_architecture>
```

`x86_64`, `aarch64`, `s390x` 또는 `ppc64le` 과 같은 클러스터의 아키텍처를 지정합니다.

미러링된 이미지를 호스트할 디렉터리의 경로를 내보냅니다.

```shell-session
$ REMOVABLE_MEDIA_PATH=<path>
```

초기 슬래시 (/) 문자를 포함하여 전체 경로를 지정합니다.

미러 레지스트리에 버전 이미지를 미러링합니다.

미러 호스트가 인터넷에 액세스할 수 없는 경우 다음 작업을 수행합니다.

이동식 미디어를 인터넷에 연결된 시스템에 연결합니다.

미러링할 이미지 및 설정 매니페스트를 확인합니다.

```shell-session
$ oc adm release mirror -a ${LOCAL_SECRET_JSON}  \
     --from=quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE}-${ARCHITECTURE} \
     --to=${LOCAL_REGISTRY}/${LOCAL_REPOSITORY} \
     --to-release-image=${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE} --dry-run
```

이전 명령의 출력에서 전체 `imageContentSources` 섹션을 기록합니다. 미러에 대한 정보는 미러링된 저장소에 고유하며 설치 중에 `imageContentSources` 섹션을 `install-config.yaml` 파일에 추가해야 합니다.

이동식 미디어의 디렉터리에 이미지를 미러링합니다.

```shell-session
$ oc adm release mirror -a ${LOCAL_SECRET_JSON} --to-dir=${REMOVABLE_MEDIA_PATH}/mirror quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE}-${ARCHITECTURE}
```

미디어를 네트워크가 제한된 환경으로 가져와서 이미지를 로컬 컨테이너 레지스트리에 업로드합니다.

```shell-session
$ oc image mirror -a ${LOCAL_SECRET_JSON} --from-dir=${REMOVABLE_MEDIA_PATH}/mirror "file://openshift/release:${OCP_RELEASE}*" ${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}
```

`REMOVABLE_MEDIA_PATH` 변수의 경우 이미지를 미러링할 때 지정한 것과 동일한 경로를 사용해야 합니다.

중요

아래 명령을 실행하면 다음과 같은 오류가 발생할 수 있습니다. `error: unable to retrieve source image`.

```shell
oc image mirror
```

이 오류는 이미지 인덱스에 이미지 레지스트리에 더 이상 존재하지 않는 이미지에 대한 참조가 포함된 경우 발생합니다. 이미지 인덱스에서는 이러한 이미지를 실행하는 사용자가 업그레이드 그래프의 최신 지점으로 업그레이드 경로를 실행할 수 있도록 이전 참조를 유지할 수 있습니다.

임시 해결 방법으로 `--skip-missing` 옵션을 사용하여 오류를 무시하고 이미지 인덱스를 계속 다운로드할 수 있습니다. 자세한 내용은 Service Mesh Operator 미러링 실패 에서 참조하십시오.

로컬 컨테이너 레지스트리가 미러 호스트에 연결된 경우 다음 작업을 수행합니다.

다음 명령을 사용하여 릴리스 이미지를 로컬 레지스트리에 직접 푸시합니다.

```shell-session
$ oc adm release mirror -a ${LOCAL_SECRET_JSON}  \
     --from=quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE}-${ARCHITECTURE} \
     --to=${LOCAL_REGISTRY}/${LOCAL_REPOSITORY} \
     --to-release-image=${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE}
```

이 명령은 요약된 릴리스 정보를 가져오며, 명령 출력에는 클러스터를 설치할 때 필요한 `imageContentSources` 데이터가 포함됩니다.

이전 명령의 출력에서 전체 `imageContentSources` 섹션을 기록합니다. 미러에 대한 정보는 미러링된 저장소에 고유하며 설치 중에 `imageContentSources` 섹션을 `install-config.yaml` 파일에 추가해야 합니다.

참고

미러링 프로세스 중에 이미지 이름이 Quay.io에 패치되고 Podman 이미지는 부트스트랩 가상 머신의 레지스트리에 Quay.io를 표시합니다.

미러링된 콘텐츠를 기반으로 설치 프로그램을 생성하려면 콘텐츠를 추출하여 릴리스 배포에 고정합니다.

미러 호스트가 인터넷에 액세스할 수 없는 경우 다음 명령을 실행합니다.

```shell-session
$ oc adm release extract -a ${LOCAL_SECRET_JSON} --icsp-file=<file> --command=openshift-install "${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE}" \
--insecure=true
```

선택 사항: 대상 레지스트리에 대한 신뢰를 구성하지 않으려면 `--insecure=true` 플래그를 추가합니다.

로컬 컨테이너 레지스트리가 미러 호스트에 연결된 경우 다음 명령을 실행합니다.

```shell-session
$ oc adm release extract -a ${LOCAL_SECRET_JSON} --command=openshift-install "${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE}"
```

중요

선택한 OpenShift Container Platform 버전에 올바른 이미지를 사용하려면 미러링된 콘텐츠에서 설치 프로그램을 배포해야 합니다.

인터넷이 연결된 컴퓨터에서 이 단계를 수행해야 합니다.

설치 프로그램에서 제공하는 인프라를 사용하는 클러스터의 경우 다음 명령을 실행합니다.

```shell-session
$ openshift-install
```

### 8.6. 연결이 끊긴 환경의 Cluster Samples Operator

연결이 끊긴 환경에서는 Cluster Samples Operator를 구성하기 위해 클러스터를 설치한 후 추가 단계를 수행해야 합니다. 준비 과정에서 다음 정보를 검토합니다.

#### 8.6.1. 미러링을 위한 Cluster Samples Operator 지원

설치 프로세스 중에 OpenShift Container Platform은 `openshift-cluster-samples-operator` 네임스페이스에 `imagestreamtag-to-image` 라는 구성 맵을 생성합니다.

`imagestreamtag-to-image` 구성 맵에는 각 이미지 스트림 태그에 대한 이미지 채우기 항목이 포함되어 있습니다.

구성 맵의 데이터 필드에 있는 각 항목의 키 형식은 `<image_stream_name>_<image_stream_tag_name>` 입니다.

OpenShift Container Platform의 연결이 끊긴 설치 프로세스 중에 Cluster Samples Operator의 상태가 `Removed` 로 설정됩니다. `Managed` 로 변경하려면 샘플이 설치됩니다.

참고

네트워크 제한 또는 중단된 환경에서 샘플을 사용하려면 네트워크 외부의 서비스에 액세스해야 할 수 있습니다. 일부 예제 서비스에는 GitHub, Maven Central, npm, RubyGems, PyPi 등이 있습니다. Cluster Samples Operator 오브젝트가 필요한 서비스에 도달할 수 있도록 하는 추가 단계가 있을 수 있습니다.

다음 원칙을 사용하여 이미지 스트림을 가져오려면 이미지 스트림을 미러링해야 하는 이미지를 결정합니다.

Cluster Samples Operator가 `Removed` 로 설정된 경우 미러링된 레지스트리를 생성하거나 사용할 기존 미러링된 레지스트리를 확인할 수 있습니다.

새 구성 맵을 가이드로 사용하여 미러링된 레지스트리에 샘플을 미러링합니다.

Cluster Samples Operator 구성 개체의 `skippedImagestreams` 필드에 미러링되지 않은 이미지 스트림을 추가합니다.

Cluster Samples Operator 구성 개체의 `samplesRegistry` 를 미러링된 레지스트리로 설정합니다.

그런 다음 Cluster Samples Operator를 `Managed` 로 설정하여 미러링된 이미지 스트림을 설치합니다.

### 8.7. 연결이 끊긴 클러스터와 함께 사용할 Operator 카탈로그 미러링

아래 명령을 사용하여 Red Hat 제공 카탈로그 또는 사용자 정의 카탈로그의 Operator 콘텐츠를 컨테이너 이미지 레지스트리에 미러링할 수 있습니다. 대상 레지스트리는 Docker v2-2 를 지원해야 합니다.

```shell
oc adm catalog mirror
```

제한된 네트워크에 있는 클러스터의 경우 이 레지스트리는 제한된 네트워크 클러스터 설치 중 생성된 미러 레지스트리와 같이 클러스터에 네트워크 액세스 권한이 있는 레지스트리일 수 있습니다.

중요

OpenShift 이미지 레지스트리는 미러링 프로세스 중에 필요한 태그 없이 푸시를 지원하지 않으므로 대상 레지스트리로 사용할 수 없습니다.

다음 명령을 실행하면 다음과 같은 오류가 발생할 수 있습니다. `error: unable to retrieve source image`.

```shell
oc adm catalog mirror
```

이 오류는 이미지 인덱스에 이미지 레지스트리에 더 이상 존재하지 않는 이미지에 대한 참조가 포함된 경우 발생합니다. 이미지 인덱스에서는 이러한 이미지를 실행하는 사용자가 업그레이드 그래프의 최신 지점으로 업그레이드 경로를 실행할 수 있도록 이전 참조를 유지할 수 있습니다.

임시 해결 방법으로 `--skip-missing` 옵션을 사용하여 오류를 무시하고 이미지 인덱스를 계속 다운로드할 수 있습니다. 자세한 내용은 Service Mesh Operator 미러링 실패 에서 참조하십시오.

아래 명령은 또한 Red Hat 제공 인덱스 이미지이든 자체 사용자 정의 빌드 인덱스 이미지이든 미러링 프로세스 중에 지정하는 인덱스 이미지를 대상 레지스트리에 자동으로 미러링합니다.

```shell
oc adm catalog mirror
```

그러면 미러링된 인덱스 이미지를 사용하여 OLM(Operator Lifecycle Manager)이 OpenShift Container Platform 클러스터에 미러링된 카탈로그를 로드할 수 있는 카탈로그 소스를 생성할 수 있습니다.

추가 리소스

연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

#### 8.7.1. 사전 요구 사항

연결이 끊긴 클러스터에 사용할 Operator 카탈로그를 미러링하려면 다음과 같은 사전 요구 사항이 있습니다.

워크스테이션에서 무제한 네트워크 액세스가 가능합니다.

다음 명령버전이 1.9.3 이상입니다.

```shell
podman
```

기존 카탈로그를 필터링 하거나 정리하고 선택적으로 Operator 서브 세트만 미러링하려면 다음 섹션을 참조하십시오.

opm CLI 설치

파일 기반 카탈로그 이미지 업데이트 또는 필터링

Red Hat 제공 카탈로그를 미러링하려면 무제한 네트워크 액세스 권한이 있는 워크스테이션에서 다음 명령을 실행하여 `registry.redhat.io` 로 인증합니다.

```shell-session
$ podman login registry.redhat.io
```

Docker v2-2 를 지원하는 미러 레지스트리에 액세스합니다.

미러 레지스트리에서 미러링된 Operator 콘텐츠를 저장하는 데 사용할 저장소 또는 네임스페이스를 결정합니다. 예를 들어 `olm-mirror` 리포지토리를 생성할 수 있습니다.

미러 레지스트리가 인터넷에 액세스할 수 없는 경우 이동식 미디어를 무제한 네트워크 액세스 권한이 있는 워크스테이션에 연결합니다.

`registry.redhat.io` 를 포함하여 프라이빗 레지스트리로 작업하는 경우 `REG_CREDS` 환경 변수를 이후 단계에서 사용할 레지스트리 자격 증명의 파일 경로로 설정합니다. 예를 들어 CLI의 경우:

```shell
podman
```

```shell-session
$ REG_CREDS=${XDG_RUNTIME_DIR}/containers/auth.json
```

#### 8.7.2. 카탈로그 콘텐츠 추출 및 미러링

아래 명령은 인덱스 이미지의 콘텐츠를 추출하여 미러링에 필요한 매니페스트를 생성합니다. 명령의 기본 동작은 매니페스트를 생성한 다음 인덱스 이미지 자체뿐만 아니라 인덱스 이미지의 모든 이미지 콘텐츠를 미러 레지스트리에 자동으로 미러링합니다.

```shell
oc adm catalog mirror
```

또는 미러 레지스트리가 완전히 연결이 끊긴 호스트 또는 에어갭(Airgap) 호스트에 있는 경우 먼저 콘텐츠를 이동식 미디어로 미러링하고 미디어를 연결이 끊긴 환경으로 이동한 다음 미디어에서 레지스트리로 해당 콘텐츠를 미러링할 수 있습니다.

#### 8.7.2.1. 동일한 네트워크의 레지스트리에 카탈로그 콘텐츠 미러링

미러 레지스트리가 무제한 네트워크 액세스 권한이 있는 워크스테이션과 동일한 네트워크에 배치된 경우 워크스테이션에서 다음 작업을 수행합니다.

프로세스

미러 레지스트리에 인증이 필요한 경우 다음 명령을 실행하여 레지스트리에 로그인합니다.

```shell-session
$ podman login <mirror_registry>
```

다음 명령을 실행하여 콘텐츠를 미러 레지스트리에 추출하고 미러링합니다.

```shell-session
$ oc adm catalog mirror \
    <index_image> \
    <mirror_registry>:<port>[/<repository>] \
    [-a ${REG_CREDS}] \
    [--insecure] \
    [--index-filter-by-os='<platform>/<arch>'] \
    [--manifests-only]
```

1. 미러링할 카탈로그의 인덱스 이미지를 지정합니다.

2. Operator 콘텐츠를 미러링할 대상 레지스트리의 FQDN(정규화된 도메인 이름)을 지정합니다. 미러 레지스트리 < `repository` >는 사전 요구 사항에 설명된 대로 레지스트리의 기존 저장소 또는 네임스페이스(예: `olm-mirror`)일 수 있습니다.

미러링 중에 기존 저장소가 발견되면 결과 이미지 이름에 저장소 이름이 추가됩니다. 이미지 이름에 리포지토리 이름을 포함하지 않으려면 이 행에서 `<repository>` 값을 생략합니다.

(예: `<mirror_registry>:<port>`)

3. 선택 사항: 필요한 경우 레지스트리 자격 증명 파일의 위치를 지정합니다. `registry.redhat.io` 에는 `{REG_CREDS}` 가 필요합니다.

4. 선택 사항: 대상 레지스트리에 대한 트러스트를 구성하지 않으려면 `--insecure` 플래그를 추가합니다.

5. 선택 사항: 여러 변형이 있을 때 선택할 수 있는 인덱스 이미지의 플랫폼 및 아키텍처를 지정합니다. 이미지는 `'<platform>/<arch>[/<variant>]’` 로 전달됩니다. 이는 인덱스에서 참조하는 이미지에는 적용되지 않습니다. 유효한 값은 `linux/amd64`, `linux/ppc64le`, `linux/s390x`, `linux/arm64` 입니다.

6. 선택 사항: 이미지 콘텐츠를 실제로 레지스트리에 미러링하지 않고 미러링에 필요한 매니페스트만 생성합니다. 이 옵션은 미러링할 항목을 검토하는 데 유용할 수 있으며 패키지의 서브 세트만 필요한 경우 매핑 목록을 변경할 수 있습니다.

그런 다음 아래 명령과 함께 `mapping.txt` 파일을 사용하여 이후 단계에서 수정된 이미지 목록을 미러링할 수 있습니다. 이 플래그는 카탈로그의 콘텐츠를 고급 선택 미러링을 위한 것입니다.

```shell
oc image mirror
```

```shell-session
src image has index label for database path: /database/index.db
using database path mapping: /database/index.db:/tmp/153048078
wrote database to /tmp/153048078
...
wrote mirroring manifests to manifests-redhat-operator-index-1614211642
```

1. 명령으로 생성된 임시 `index.db` 데이터베이스용 디렉터리입니다.

2. 생성된 매니페스트 디렉터리 이름을 기록합니다. 이 디렉터리는 후속 절차에서 참조됩니다.

참고

Red Hat Quay는 중첩된 리포지토리를 지원하지 않습니다. 결과적으로 아래 명령을 실행하면 `401` 무단 오류와 함께 실패합니다.

```shell
oc adm catalog mirror
```

이 문제를 해결하려면 아래 명령을 실행하여 중첩된 리포지토리 생성을 비활성화할 때 `--max-components=2` 옵션을 사용할 수 있습니다. 이 해결 방법에 대한 자세한 내용은 Quay 레지스트리 지식베이스 솔루션에서 catalog mirror 명령을 사용하는 동안 발생하는 무단 오류 를 참조하십시오.

```shell
oc adm catalog mirror
```

#### 8.7.2.2. Airgapped 레지스트리에 카탈로그 콘텐츠 미러링

미러 레지스트리가 완전히 연결이 끊겼거나 에어그래시된 호스트에 있는 경우 다음 작업을 수행합니다.

프로세스

무제한 네트워크 액세스 권한이 있는 워크스테이션에서 다음 명령을 실행하여 콘텐츠를 로컬 파일에 미러링합니다.

```shell-session
$ oc adm catalog mirror \
    <index_image> \
    file:///local/index \
    -a ${REG_CREDS} \
    --insecure \
    --index-filter-by-os='<platform>/<arch>'
```

1. 미러링할 카탈로그의 인덱스 이미지를 지정합니다.

2. 현재 디렉터리의 로컬 파일에 미러링할 내용을 지정합니다.

3. 선택 사항: 필요한 경우 레지스트리 자격 증명 파일의 위치를 지정합니다.

4. 선택 사항: 대상 레지스트리에 대한 트러스트를 구성하지 않으려면 `--insecure` 플래그를 추가합니다.

5. 선택 사항: 여러 변형이 있을 때 선택할 수 있는 인덱스 이미지의 플랫폼 및 아키텍처를 지정합니다. 이미지는 `'<platform>/<arch>[/<variant>]'` 로 지정됩니다.

이는 인덱스에서 참조하는 이미지에는 적용되지 않습니다. 유효한 값은 `linux/amd64`, `linux/ppc64le`, `linux/s390x`, `linux/arm64`, `.*` 입니다.

```shell-session
...
info: Mirroring completed in 5.93s (5.915MB/s)
wrote mirroring manifests to manifests-my-index-1614985528
To upload local images to a registry, run:

    oc adm catalog mirror file://local/index/myrepo/my-index:v1 REGISTRY/REPOSITORY
```

1. 생성된 매니페스트 디렉터리 이름을 기록합니다. 이 디렉터리는 후속 절차에서 참조됩니다.

2. 제공된 인덱스 이미지를 기반으로 확장된 `file://` 경로를 기록합니다. 이 경로는 후속 단계에서 참조됩니다.

이 명령은 현재 디렉터리에 `v2/` 디렉터리를 생성합니다.

`v2/` 디렉터리를 이동식 미디어에 복사합니다.

물리적으로 미디어를 제거하고 연결이 끊긴 환경의 호스트에 연결하여 미러 레지스트리에 액세스할 수 있습니다.

미러 레지스트리에 인증이 필요한 경우 연결이 끊긴 환경의 호스트에서 다음 명령을 실행하여 레지스트리에 로그인합니다.

```shell-session
$ podman login <mirror_registry>
```

`v2/` 디렉터리가 포함된 상위 디렉터리에서 다음 명령을 실행하여 로컬 파일에서 미러 레지스트리로 이미지를 업로드합니다.

```shell-session
$ oc adm catalog mirror \
    file://local/index/<repository>/<index_image>:<tag> \
    <mirror_registry>:<port>[/<repository>] \
    -a ${REG_CREDS} \
    --insecure \
    --index-filter-by-os='<platform>/<arch>'
```

1. 이전 명령 출력의 `file://` 경로를 지정합니다.

2. Operator 콘텐츠를 미러링할 대상 레지스트리의 FQDN(정규화된 도메인 이름)을 지정합니다. 미러 레지스트리 < `repository` >는 사전 요구 사항에 설명된 대로 레지스트리의 기존 저장소 또는 네임스페이스(예: `olm-mirror`)일 수 있습니다.

미러링 중에 기존 저장소가 발견되면 결과 이미지 이름에 저장소 이름이 추가됩니다. 이미지 이름에 리포지토리 이름을 포함하지 않으려면 이 행에서 `<repository>` 값을 생략합니다.

(예: `<mirror_registry>:<port>`)

3. 선택 사항: 필요한 경우 레지스트리 자격 증명 파일의 위치를 지정합니다.

4. 선택 사항: 대상 레지스트리에 대한 트러스트를 구성하지 않으려면 `--insecure` 플래그를 추가합니다.

5. 선택 사항: 여러 변형이 있을 때 선택할 수 있는 인덱스 이미지의 플랫폼 및 아키텍처를 지정합니다. 이미지는 `'<platform>/<arch>[/<variant>]'` 로 지정됩니다.

이는 인덱스에서 참조하는 이미지에는 적용되지 않습니다. 유효한 값은 `linux/amd64`, `linux/ppc64le`, `linux/s390x`, `linux/arm64`, `.*` 입니다.

참고

Red Hat Quay는 중첩된 리포지토리를 지원하지 않습니다. 결과적으로 아래 명령을 실행하면 `401` 무단 오류와 함께 실패합니다.

```shell
oc adm catalog mirror
```

이 문제를 해결하려면 아래 명령을 실행하여 중첩된 리포지토리 생성을 비활성화할 때 `--max-components=2` 옵션을 사용할 수 있습니다. 이 해결 방법에 대한 자세한 내용은 Quay 레지스트리 지식베이스 솔루션에서 catalog mirror 명령을 사용하는 동안 발생하는 무단 오류 를 참조하십시오.

```shell
oc adm catalog mirror
```

아래 명령을 다시 실행합니다. 새로 미러링된 인덱스 이미지를 소스로 사용하고 이전 단계에서 사용된 것과 동일한 미러 레지스트리 대상을 사용합니다.

```shell
oc adm catalog mirror
```

```shell-session
$ oc adm catalog mirror \
    <mirror_registry>:<port>/<index_image> \
    <mirror_registry>:<port>[/<repository>] \
    --manifests-only \
    [-a ${REG_CREDS}] \
    [--insecure]
```

1. 이 단계에서는 명령이 미러링된 모든 콘텐츠를 다시 복사하지 않도록 `--manifests-only` 플래그가 필요합니다.

중요

이전 단계에서 생성된 `imageContentSourcePolicy.yaml` 파일의 이미지 매핑은 로컬 경로에서 유효한 미러 위치로 업데이트해야 하므로 이 단계가 필요합니다. 이렇게 하지 않으면 이후 단계에서 `ImageContentSourcePolicy` 개체를 생성할 때 오류가 발생합니다.

카탈로그를 미러링한 후 나머지 클러스터 설치를 계속할 수 있습니다. 클러스터 설치가 성공적으로 완료되면 `ImageContentSourcePolicy` 및 `CatalogSource` 오브젝트를 생성하려면 이 절차의 매니페스트 디렉터리를 지정해야 합니다. 이러한 오브젝트는 소프트웨어 카탈로그에서 Operator를 설치하는 데 필요합니다.

#### 8.7.3. 생성된 매니페스트

Operator 카탈로그 콘텐츠를 미러 레지스트리에 미러링하면 현재 디렉터리에 매니페스트 디렉터리가 생성됩니다.

동일한 네트워크의 레지스트리에 콘텐츠를 미러링한 경우 디렉터리 이름은 다음 패턴을 사용합니다.

```plaintext
manifests-<index_image_name>-<random_number>
```

이전 섹션에서 연결이 끊긴 호스트의 레지스트리에 콘텐츠를 미러링한 경우 디렉터리 이름은 다음 패턴을 사용합니다.

```plaintext
manifests-index/<repository>/<index_image_name>-<random_number>
```

참고

매니페스트 디렉터리 이름은 후속 절차에서 참조됩니다.

매니페스트 디렉터리에는 다음 파일이 포함되어 있으며, 이 중 일부는 추가 수정이 필요할 수 있습니다.

`catalogSource.yaml` 파일은 인덱스 이미지 태그 및 기타 관련 메타데이터로 미리 채워진 `CatalogSource` 오브젝트에 대한 기본 정의입니다. 이 파일은 있는 그대로 사용하거나 카탈로그 소스를 클러스터에 추가하도록 수정할 수 있습니다.

중요

콘텐츠를 로컬 파일에 미러링한 경우 `metadata.name` 필드에서.name 필드에서 백슬래시(`/`) 문자를 제거하려면 `catalogSource.yaml` 파일을 수정해야 합니다. 그러지 않으면 오브젝트 생성을 시도할 때 "잘못된 리소스 이름" 오류로 인해 실패합니다.

`imageContentSourcePolicy.yaml` 파일은 Operator 매니페스트에 저장된 이미지 참조와 미러링된 레지스트리 간에 변환하도록 노드를 구성할 수 있는 `ImageContentSourcePolicy` 오브젝트를 정의합니다.

참고

클러스터에서 `ImageContentSourcePolicy` 오브젝트를 사용하여 저장소 미러링을 구성하는 경우 미러링된 레지스트리에 대한 글로벌 풀 시크릿만 사용할 수 있습니다. 프로젝트에 풀 시크릿을 추가할 수 없습니다.

`mapping.txt` 파일에는 모든 소스 이미지와 대상 레지스트리에서 매핑할 위치가 포함되어 있습니다. 이 파일은 아래 명령과 호환되며 미러링 구성을 추가로 사용자 정의하는 데 사용할 수 있습니다.

```shell
oc image mirror
```

중요

미러링 프로세스 중 `--manifests-only` 플래그를 사용한 후 미러링할 패키지의 서브 세트를 추가로 트리밍하려면 `mapping.txt` 파일을 수정하고 아래 명령으로 파일을 사용하는 데 대한 OpenShift Container Platform 4.7 설명서의 패키지 매니페스트 형식 카탈로그 이미지 미러링 절차에 있는 단계를 참조하십시오.

```shell
oc image mirror
```

#### 8.7.4. 설치 후 요구 사항

카탈로그를 미러링한 후 나머지 클러스터 설치를 계속할 수 있습니다. 클러스터 설치가 성공적으로 완료되면 `ImageContentSourcePolicy` 및 `CatalogSource` 오브젝트를 생성하려면 이 절차의 매니페스트 디렉터리를 지정해야 합니다. 이러한 오브젝트는 소프트웨어 카탈로그에서 Operator를 채우고 설치하는 데 필요합니다.

추가 리소스

미러링된 Operator 카탈로그에서 소프트웨어 카탈로그 채우기

파일 기반 카탈로그 이미지 업데이트 또는 필터링

### 8.8. 다음 단계

VMware vSphere, 베어 메탈 또는 Amazon Web Services 와 같이 네트워크가 제한된 환경에서 프로비저닝한 인프라에 클러스터를 설치합니다.

### 8.9. 추가 리소스

must-gather 사용에 대한 자세한 내용은 특정 기능에 대한 데이터 수집을 참조하십시오.

## 9장. 연결이 끊긴 환경에서 클러스터 설치

요구사항에 가장 적합한 설치 방법 및 인프라를 선택하여 연결이 끊긴 환경에 OpenShift Container Platform 클러스터를 설치할 수 있습니다. 여기에는 온프레미스 하드웨어 또는 AWS(Amazon Web Services)와 같은 클라우드 호스팅 서비스에 OpenShift Container Platform을 설치하는 작업이 포함됩니다.

다음 섹션에서는 연결이 끊긴 환경에 클러스터를 설치하는 데 지원되는 모든 방법을 간략하게 설명합니다.

참고

특정 방법을 사용하여 클러스터 설치의 다른 요구 사항에 대해 알아보려면 설명서의 절차 각 섹션에 있는 다른 콘텐츠를 검토하십시오.

예를 들어 설치 관리자 프로비저닝 인프라가 있는 AWS에 클러스터를 설치하려는 경우 AWS 계정 구성 및 AWS에 클러스터 설치 준비를 참조하십시오.

### 9.1. 에이전트 기반 설치 관리자를 사용하여 클러스터 설치

에이전트 기반 설치 프로그램을 사용하여 연결이 끊긴 환경에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 페이지를 참조하십시오.

연결 해제된 설치 미러링 이해

에이전트 기반 설치 관리자를 사용하여 OpenShift Container Platform 클러스터 설치

### 9.2. Amazon Web Services에 클러스터 설치

연결이 끊긴 환경의 AWS(Amazon Web Services)에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

설치 관리자 프로비저닝 인프라: 제한된 네트워크에서 AWS에 클러스터 설치

사용자 프로비저닝 인프라: 사용자 프로비저닝 인프라가 있는 제한된 네트워크에서 AWS에 클러스터 설치

### 9.3. Microsoft Azure에 클러스터 설치

연결이 끊긴 환경에서 Microsoft Azure에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

설치 관리자 프로비저닝 인프라: 네트워크가 제한된 환경에서 Azure에 클러스터 설치

사용자 프로비저닝 인프라: 사용자 프로비저닝 인프라가 있는 제한된 네트워크에서 Azure에 클러스터 설치

### 9.4. Google Cloud에 클러스터 설치

연결이 끊긴 환경에서 Google Cloud에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

설치 관리자 프로비저닝 인프라: 제한된 네트워크의 Google Cloud에 클러스터 설치

사용자 프로비저닝 인프라: 사용자 프로비저닝 인프라가 있는 제한된 네트워크에서 Google Cloud에 클러스터 설치

### 9.5. IBM Cloud에 클러스터 설치

연결이 끊긴 환경에서 IBM Cloud®에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

네트워크가 제한된 환경에서 IBM Cloud에 클러스터 설치

### 9.6. Nutanix에 클러스터 설치

연결이 끊긴 환경의 Nutanix에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

제한된 네트워크에서 Nutanix에 클러스터 설치

### 9.7. 베어 메탈 클러스터 설치

연결이 끊긴 환경에 베어 메탈 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

제한된 네트워크에서 사용자가 프로비저닝한 베어 메탈 클러스터를 설치

### 9.8. IBM Z(R) 또는 IBM(R) LinuxONE에 클러스터 설치

연결이 끊긴 환경에서 IBM Z® 또는 IBM® LinuxONE에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

네트워크가 제한된 환경에서 IBM Z 및 IBM LinuxONE에 z/VM으로 클러스터 설치

네트워크가 제한된 환경에서 IBM Z 및 IBM LinuxONE에 RHEL KVM으로 클러스터 설치

네트워크가 제한된 환경에서 IBM Z 및 IBM LinuxONE의 LPAR에 클러스터 설치

### 9.9. IBM Power에 클러스터 설치

연결이 끊긴 환경에서 IBM Power에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

네트워크가 제한된 환경에서 IBM Power에 클러스터 설치

### 9.10. OpenStack에 클러스터 설치

연결이 끊긴 환경의 RHOSP(Red Hat OpenStack Platform)에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

네트워크가 제한된 환경에서 OpenStack에 클러스터 설치

### 9.11. vSphere에 클러스터 설치

연결이 끊긴 환경에서 VMware vSphere에 클러스터를 설치하는 방법에 대한 자세한 내용은 다음 절차를 참조하십시오.

설치 관리자 프로비저닝 인프라: 제한된 네트워크의 vSphere에 클러스터 설치

사용자 프로비저닝 인프라: 사용자 프로비저닝 인프라가 있는 제한된 네트워크에서 vSphere에 클러스터 설치

## 10장. 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

연결이 끊긴 환경의 OpenShift Container Platform 클러스터의 경우 OLM(Operator Lifecycle Manager)은 기본적으로 원격 레지스트리에서 호스팅되는 Red Hat 제공 소프트웨어 카탈로그 소스에 액세스할 수 없습니다. 이러한 원격 소스에는 완전한 인터넷 연결이 필요하기 때문입니다.

그러나 클러스터 관리자는 워크스테이션에 완전한 인터넷 액세스 권한이 있는 경우 연결이 끊긴 환경에서 OLM을 사용하도록 클러스터를 활성화할 수 있습니다. 원격 소프트웨어 카탈로그 콘텐츠를 가져오는 데 완전한 인터넷 액세스가 필요한 워크스테이션은 원격 소스의 로컬 미러를 준비하고 콘텐츠를 미러 레지스트리로 내보내는 데 사용됩니다.

미러 레지스트리는 워크스테이션 및 연결이 끊긴 클러스터 모두에 연결해야 하는 베스천 호스트에 있거나 미러링된 콘텐츠를 연결이 끊긴 환경에 물리적으로 이동하기 위해 이동식 미디어가 필요한 완전히 연결이 끊긴 호스트 또는 에어갭(Airgap) 호스트에 있을 수 있습니다.

이 가이드에서는 연결이 끊긴 환경에서 OLM을 활성화하는 데 필요한 다음 프로세스를 설명합니다.

OLM의 기본 원격 소프트웨어 카탈로그 소스를 비활성화합니다.

전체 인터넷 액세스가 가능한 워크스테이션을 사용하여 소프트웨어 카탈로그 콘텐츠의 로컬 미러를 생성하고 미러 레지스트리로 내보냅니다.

기본 원격 소스가 아닌 미러 레지스트리의 로컬 소스에서 Operator를 설치하고 관리하도록 OLM을 구성합니다.

연결이 끊긴 환경에서 OLM을 활성화한 후에는 무제한 워크스테이션을 계속 사용하여 최신 버전의 Operator가 릴리스되면 로컬 소프트웨어 카탈로그 소스를 업데이트할 수 있습니다.

중요

OLM은 로컬 소스에서 Operator를 관리할 수 있지만 지정된 Operator가 연결이 끊긴 환경에서 성공적으로 실행되는 기능은 다음 기준을 충족하는 Operator 자체에 따라 다릅니다.

Operator에서 기능을 수행하는 데 필요할 수 있는 관련 이미지 또는 기타 컨테이너 이미지를 CSV(`ClusterServiceVersion`) 오브젝트의 `relatedImages` 매개변수에 나열합니다.

태그가 아닌 다이제스트(SHA)를 통해 지정된 모든 이미지를 참조합니다.

Red Hat Ecosystem Catalog 에서 다음 항목을 필터링하여 연결이 끊긴 모드에서 실행을 지원하는 Red Hat Operator 목록을 검색할 수 있습니다.

| 유형 | 컨테이너화된 애플리케이션 |
| --- | --- |
| 배포 방법 | Operator |
| 인프라 기능 | 연결 끊김 |

추가 리소스

Red Hat 제공 Operator 카탈로그

### 10.1. 사전 요구 사항

`cluster-admin` 권한이 있는 사용자로 OpenShift Container Platform 클러스터에 로그인되어 있습니다.

IBM Z®의 연결이 끊긴 환경에서 OLM을 사용하는 경우 레지스트리를 배치하는 디렉터리에 12GB 이상을 할당해야 합니다.

### 10.2. 기본 소프트웨어 카탈로그 소스 비활성화

Red Hat 및 커뮤니티 프로젝트에서 제공하는 콘텐츠를 소싱하는 Operator 카탈로그는 OpenShift Container Platform 설치 중에 기본적으로 소프트웨어 카탈로그용으로 구성됩니다. 제한된 네트워크 환경에서는 클러스터 관리자로서 기본 카탈로그를 비활성화해야 합니다.

그런 다음 소프트웨어 카탈로그에 로컬 카탈로그 소스를 사용하도록 OperatorHub CRD(사용자 정의 리소스 정의)를 구성할 수 있습니다.

프로세스

`OperatorHub` 오브젝트에 `disableAllDefaultSources: true` 를 추가하여 기본 카탈로그의 소스를 비활성화합니다.

```shell-session
$ oc patch OperatorHub cluster --type json \
    -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'
```

작은 정보

또는 웹 콘솔을 사용하여 카탈로그 소스를 관리할 수 있습니다. 관리 → 클러스터 설정 → 구성 → OperatorHub 페이지에서 개별 소스 를 생성, 업데이트, 삭제, 비활성화 및 활성화할 수 있는 소스 탭을 클릭합니다.

### 10.3. Operator 카탈로그 미러링

연결이 끊긴 클러스터에 사용할 Operator 카탈로그 미러링에 대한 자세한 내용은 연결이 끊긴 클러스터에 사용할 Operator 카탈로그 미러링을 참조하십시오.

중요

OpenShift Container Platform 4.11부터 파일 기반 카탈로그 형식의 기본 Red Hat 제공 Operator 카탈로그 릴리스입니다. 더 이상 사용되지 않는 SQLite 데이터베이스 형식으로 릴리스된 OpenShift Container Platform 4.6 through 4.10의 기본 Red Hat 제공 Operator 카탈로그입니다.

SQLite 데이터베이스 형식과 관련된 `opm` 하위 명령, 플래그 및 기능은 더 이상 사용되지 않으며 향후 릴리스에서 제거됩니다. 이 기능은 계속 지원되며 더 이상 사용되지 않는 SQLite 데이터베이스 형식을 사용하는 카탈로그에 사용해야 합니다.

`opm index prune` 와 같은 SQLite 데이터베이스 형식을 사용하기 위한 `opm` 하위 명령 및 플래그는 파일 기반 카탈로그 형식에서는 작동하지 않습니다.

파일 기반 카탈로그 작업에 대한 자세한 내용은 Operator 프레임워크 패키징 형식, 사용자 정의 카탈로그 관리, oc-mirror 플러그인 v2를 사용하여 연결이 끊긴 설치의 이미지 미러링 을 참조하십시오.

### 10.4. 클러스터에 카탈로그 소스 추가

OpenShift Container Platform 클러스터에 카탈로그 소스를 추가하면 사용자를 위한 Operator를 검색하고 설치할 수 있습니다. 클러스터 관리자는 인덱스 이미지를 참조하는 `CatalogSource` 오브젝트를 생성할 수 있습니다. 소프트웨어 카탈로그는 카탈로그 소스를 사용하여 사용자 인터페이스를 채웁니다.

작은 정보

또는 웹 콘솔을 사용하여 카탈로그 소스를 관리할 수 있습니다. 관리 → 클러스터 설정 → 구성 → OperatorHub 페이지에서 개별 소스 를 생성, 업데이트, 삭제, 비활성화 및 활성화할 수 있는 소스 탭을 클릭합니다.

사전 요구 사항

인덱스 이미지를 빌드하여 레지스트리로 내보냈습니다.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

인덱스 이미지를 참조하는 `CatalogSource` 오브젝트를 생성합니다. 아래 명령을 사용하여 카탈로그를 대상 레지스트리에 미러링한 경우 매니페스트 디렉터리에서 생성된 `catalogSource.yaml` 파일을 시작점으로 사용할 수 있습니다.

```shell
oc adm catalog mirror
```

다음을 사양에 맞게 수정하고 `catalogsource.yaml` 파일로 저장합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: my-operator-catalog
  namespace: openshift-marketplace
spec:
  sourceType: grpc
  grpcPodConfig:
    securityContextConfig: <security_mode>
  image: <registry>/<namespace>/redhat-operator-index:v4.20
  displayName: My Operator Catalog
  publisher: <publisher_name>
  updateStrategy:
    registryPoll:
      interval: 30m
```

1. 레지스트리에 업로드하기 전에 콘텐츠를 로컬 파일에 미러링한 경우 오브젝트를 생성할 때 "잘못된 리소스 이름" 오류가 발생하지 않도록 `metadata.name` 필드에서 백슬래시(`/`) 문자를 제거합니다.

2. 카탈로그 소스를 모든 네임스페이스의 사용자가 전역적으로 사용할 수 있도록 하려면 `openshift-marketplace` 네임스페이스를 지정합니다. 그러지 않으면 카탈로그의 범위가 지정되고 해당 네임스페이스에 대해서만 사용할 수 있도록 다른 네임스페이스를 지정할 수 있습니다.

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

프라이빗 레지스트리에서 Operator용 이미지에 액세스

사용자 정의 카탈로그 소스의 이미지 템플릿

이미지 가져오기 정책

### 10.5. 다음 단계

설치된 Operator 업데이트

### 11.1. 연결이 끊긴 환경의 클러스터 업데이트 정보

연결이 끊긴 환경은 클러스터 노드가 인터넷에 액세스할 수 없거나 정책 또는 성능을 위해 로컬로 업데이트 권장 사항을 관리하고 이미지를 릴리스하려는 위치입니다. 이 섹션에서는 OpenShift Container Platform 이미지 미러링, OpenShift Update Service 관리, 연결이 끊긴 환경에서 클러스터 업데이트를 수행하는 방법에 대해 설명합니다.

#### 11.1.1. OpenShift Container Platform 이미지 미러링

연결이 끊긴 환경에서 클러스터를 업데이트하려면 클러스터 환경에서 대상 업데이트에 필요한 이미지 및 리소스가 있는 미러 레지스트리에 액세스할 수 있어야 합니다. 단일 컨테이너 이미지 레지스트리는 연결이 끊긴 네트워크에서 여러 클러스터에 대해 미러링된 이미지를 호스팅하는 데 충분합니다. 다음 페이지에는 연결이 끊긴 클러스터의 저장소로 이미지를 미러링하는 방법이 있습니다.

OpenShift Container Platform 이미지 미러링

#### 11.1.2. 연결이 끊긴 환경에서 클러스터 업데이트 수행

다음 절차 중 하나를 사용하여 연결이 끊긴 OpenShift Container Platform 클러스터를 업데이트할 수 있습니다.

OpenShift Update Service를 사용하여 연결이 끊긴 환경에서 클러스터 업데이트

OpenShift Update Service 없이 연결이 끊긴 환경에서 클러스터 업데이트

#### 11.1.3. 클러스터에서 OpenShift Update Service 설치 제거

다음 절차에 따라 클러스터에서 OpenShift Update Service(OSUS)의 로컬 사본을 제거할 수 있습니다.

클러스터에서 OpenShift Update Service 설치 제거

### 11.2. OpenShift Container Platform 이미지 미러링

연결이 끊긴 환경에서 클러스터를 업데이트하려면 컨테이너 이미지를 미러 레지스트리에 미러링해야 합니다. 또한 연결된 환경에서 이 절차를 사용하여 클러스터가 외부 콘텐츠에 대한 조직의 제어 조건을 충족하는 승인된 컨테이너 이미지만 실행하도록 할 수 있습니다.

참고

미러 레지스트리는 클러스터가 실행되는 동안 항상 실행되어야 합니다.

다음 단계에서는 이미지를 미러 레지스트리에 미러링하는 방법에 대한 고급 워크플로를 간략하게 설명합니다.

릴리스 이미지를 검색하고 내보내는 데 사용되는 모든 장치에 OpenShift CLI()를 설치합니다.

```shell
oc
```

레지스트리 풀 시크릿을 다운로드하여 클러스터에 추가합니다.

```shell
oc
```

릴리스 이미지를 검색하고 내보내는 데 사용되는 모든 장치에 oc-mirror 플러그인을 설치합니다.

미러링할 릴리스 이미지를 결정할 때 사용할 플러그인의 이미지 세트 구성 파일을 생성합니다. 나중에 이 구성 파일을 편집하여 플러그인이 미러링하는 릴리스 이미지를 변경할 수 있습니다.

대상 릴리스 이미지를 미러 레지스트리 또는 이동식 미디어에 직접 미러링한 다음 미러 레지스트리에 미러링합니다.

oc-mirror 플러그인에서 생성한 리소스를 사용하도록 클러스터를 구성합니다.

필요에 따라 이러한 단계를 반복하여 미러 레지스트리를 업데이트합니다.

```shell
oc adm release mirror
```

사용자 환경과 미러링하려는 릴리스 이미지에 해당하는 환경 변수를 설정합니다.

대상 릴리스 이미지를 미러 레지스트리 또는 이동식 미디어에 직접 미러링한 다음 미러 레지스트리에 미러링합니다.

필요에 따라 이러한 단계를 반복하여 미러 레지스트리를 업데이트합니다.

아래 명령 사용과 비교하여 oc-mirror 플러그인은 다음과 같은 이점이 있습니다.

```shell
oc adm release mirror
```

컨테이너 이미지 이외의 콘텐츠를 미러링할 수 있습니다.

이미지를 처음 미러링하면 레지스트리의 이미지를 더 쉽게 업데이트할 수 있습니다.

oc-mirror 플러그인은 Quay의 릴리스 페이로드를 미러링하고 연결이 끊긴 환경에서 실행되는 OpenShift 업데이트 서비스에 대한 최신 그래프 데이터 이미지도 빌드하는 자동화된 방법을 제공합니다.

#### 11.2.1. oc-mirror 플러그인을 사용하여 리소스 미러링

oc-mirror OpenShift CLI() 플러그인을 사용하여 완전히 또는 부분적으로 연결이 끊긴 환경의 미러 레지스트리에 이미지를 미러링할 수 있습니다. 인터넷에 연결된 시스템에서 oc-mirror를 실행하여 공식 Red Hat 레지스트리에서 필요한 이미지를 다운로드해야 합니다.

```shell
oc
```

자세한 내용은 oc-mirror 플러그인 v2를 사용하여 연결이 끊긴 설치의 이미지 미러링 을 참조하십시오.

#### 11.2.2. oc adm release mirror 명령을 사용하여 이미지 미러링

아래 명령을 사용하여 이미지를 미러 레지스트리에 미러링할 수 있습니다.

```shell
oc adm release mirror
```

#### 11.2.2.1. 사전 요구 사항

Red Hat Quay와 같은 OpenShift Container Platform 클러스터를 호스팅할 위치에 Docker v2-2 를 지원하는 컨테이너 이미지 레지스트리가 있어야 합니다.

참고

Red Hat Quay를 사용하는 경우 oc-mirror 플러그인에서 버전 3.6 이상을 사용해야 합니다. Red Hat Quay에 대한 인타이틀먼트가 있는 경우 개념 증명 목적으로 또는 Quay Operator를 사용하여 Red Hat Quay 배포에 대한 설명서를 참조하십시오.

레지스트리를 선택 및 설치하는 데 추가 지원이 필요한 경우 영업 담당자 또는 Red Hat 지원팀에 문의하십시오.

컨테이너 이미지 레지스트리에 대한 기존 솔루션이 없는 경우 Red Hat OpenShift의 미러 레지스트리가 OpenShift Container Platform 서브스크립션에 포함되어 있습니다.

Red Hat OpenShift의 미러 레지스트리 는 연결이 끊긴 설치 및 업데이트에서 OpenShift Container Platform 컨테이너 이미지를 미러링하는 데 사용할 수 있는 소규모 컨테이너 레지스트리입니다.

#### 11.2.2.2. 미러 호스트 준비

미러 단계를 수행하기 전에 호스트는 콘텐츠를 검색하고 원격 위치로 푸시할 준비가 되어 있어야 합니다.

#### 11.2.2.2.1. OpenShift CLI 설치

명령줄 인터페이스를 사용하여 OpenShift Container Platform과 상호 작용하기 위해 OpenShift CLI()를 설치할 수 있습니다. Linux, Windows 또는 macOS에 다음 명령을 설치할 수 있습니다.

```shell
oc
```

```shell
oc
```

중요

이전 버전의 다음 명령을 설치한 경우 OpenShift Container Platform의 모든 명령을 완료하는 데 해당 버전을 사용할 수 없습니다.

```shell
oc
```

새 버전의 다음 명령을 다운로드하여 설치합니다. 연결이 끊긴 환경에서 클러스터를 업데이트하는 경우 업데이트할 버전을 설치합니다.

```shell
oc
```

```shell
oc
```

#### 11.2.2.2.1.1. Linux에서 OpenShift CLI 설치

다음 절차를 사용하여 Linux에서 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

Red Hat 고객 포털에서 OpenShift Container Platform 다운로드 페이지로 이동합니다.

Product Variant 목록에서 아키텍처를 선택합니다.

버전 목록에서 적절한 버전을 선택합니다.

OpenShift v4.20 Linux Clients 항목 옆에 있는 지금 다운로드를 클릭하고 파일을 저장합니다.

아카이브의 압축을 풉니다.

```shell-session
$ tar xvf <file>
```

다음 명령바이너리를 `PATH` 에 있는 디렉터리에 배치합니다.

```shell
oc
```

`PATH` 를 확인하려면 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

검증

OpenShift CLI를 설치한 후 아래 명령을 사용할 수 있습니다.

```shell
oc
```

```shell-session
$ oc <command>
```

#### 11.2.2.2.1.2. Windows에서 OpenSfhit CLI 설치

다음 절차에 따라 Windows에 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

Red Hat 고객 포털에서 OpenShift Container Platform 다운로드 페이지로 이동합니다.

버전 목록에서 적절한 버전을 선택합니다.

OpenShift v4.20 Windows Client 항목 옆에 있는 지금 다운로드를 클릭하고 파일을 저장합니다.

ZIP 프로그램으로 아카이브의 압축을 풉니다.

다음 명령바이너리를 `PATH` 에 있는 디렉터리로 이동합니다.

```shell
oc
```

`PATH` 를 확인하려면 명령 프롬프트를 열고 다음 명령을 실행합니다.

```shell-session
C:\> path
```

검증

OpenShift CLI를 설치한 후 아래 명령을 사용할 수 있습니다.

```shell
oc
```

```shell-session
C:\> oc <command>
```

#### 11.2.2.2.1.3. macOS에 OpenShift CLI 설치

다음 절차에 따라 macOS에서 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

Red Hat 고객 포털에서 OpenShift Container Platform 다운로드 페이지로 이동합니다.

버전 드롭다운 목록에서 적절한 버전을 선택합니다.

OpenShift v4.20 macOS Clients 항목 옆에 있는 지금 다운로드를 클릭하고 파일을 저장합니다.

참고

macOS arm64의 경우 OpenShift v4.20 macOS arm64 Client 항목을 선택합니다.

아카이브의 압축을 해제하고 압축을 풉니다.

다음 명령바이너리 PATH의 디렉터리로 이동합니다.

```shell
oc
```

`PATH` 를 확인하려면 터미널을 열고 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

검증

아래 명령을 사용하여 설치를 확인합니다.

```shell
oc
```

```shell-session
$ oc <command>
```

추가 리소스

CLI 플러그인 설치 및 사용

#### 11.2.2.2.2. 이미지를 미러링할 수 있는 인증 정보 설정

Red Hat에서 미러로 이미지를 미러링할 수 있도록 컨테이너 이미지 레지스트리 인증 정보 파일을 생성합니다. 설치 호스트에서 다음 단계를 완료합니다.

주의

클러스터를 설치할 때 이 이미지 레지스트리 인증 정보 파일을 풀 시크릿(pull secret)으로 사용하지 마십시오. 클러스터를 설치할 때 이 파일을 지정하면 클러스터의 모든 시스템에 미러 레지스트리에 대한 쓰기 권한이 부여됩니다.

사전 요구 사항

연결이 끊긴 환경에서 사용할 미러 레지스트리를 구성했습니다.

미러 레지스트리에서 이미지를 미러링할 이미지 저장소 위치를 확인했습니다.

이미지를 해당 이미지 저장소에 업로드할 수 있는 미러 레지스트리 계정을 제공하고 있습니다.

미러 레지스트리에 대한 쓰기 권한이 있습니다.

프로세스

Red Hat OpenShift Cluster Manager 에서 `registry.redhat.io` 풀 시크릿을 다운로드합니다.

다음 명령을 실행하여 풀 시크릿을 JSON 형식으로 복사합니다.

```shell-session
$ cat ./pull-secret | jq . > <path>/<pull_secret_file_in_json>
```

풀 시크릿을 저장할 디렉터리의 경로와 생성한 JSON 파일의 이름을 지정합니다.

```plaintext
{
  "auths": {
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

선택 사항: oc-mirror 플러그인을 사용하는 경우 파일을 `~/.docker/config.json` 또는 `$XDG_RUNTIME_DIR/containers/auth.json` 으로 저장합니다.

`.docker` 또는 `$XDG_RUNTIME_DIR/containers` 디렉터리가 없는 경우 다음 명령을 입력하여 만듭니다.

```shell-session
$ mkdir -p <directory_name>
```

여기서 `<directory_name>` 은 `~/.docker` 또는 `$XDG_RUNTIME_DIR/containers` 입니다.

다음 명령을 입력하여 풀 시크릿을 적절한 디렉터리에 복사합니다.

```shell-session
$ cp <path>/<pull_secret_file_in_json> <directory_name>/<auth_file>
```

여기서 `<directory_name>` 은 `~/.docker` 또는 `$XDG_RUNTIME_DIR/containers` 이며 `<auth_file>` 은 `config.json` 또는 `auth.json` 입니다.

다음 명령을 실행하여 미러 레지스트리에 대한 base64로 인코딩된 사용자 이름 및 암호 또는 토큰을 생성합니다.

```shell-session
$ echo -n '<user_name>:<password>' | base64 -w0
```

`<user_name>` 및 `<password>` 의 경우 레지스트리에 설정한 사용자 이름 및 암호를 지정합니다.

```shell-session
BGVtbYk3ZHAtqXs=
```

JSON 파일을 편집하고 레지스트리를 설명하는 섹션을 추가합니다.

```plaintext
"auths": {
    "<mirror_registry>": {
      "auth": "<credentials>",
      "email": "you@example.com"
    }
  },
```

&lt `;mirror_registry` > 값의 경우 미러 레지스트리가 콘텐츠를 제공하는 데 사용하는 레지스트리 도메인 이름과 포트(선택 사항)를 지정합니다. 예: `registry.example.com` 또는 `registry.example.com:8443`.

&lt `;credentials&` gt; 값의 경우 미러 레지스트리의 base64 인코딩 사용자 이름과 암호를 지정합니다.

```plaintext
{
  "auths": {
    "registry.example.com": {
      "auth": "BGVtbYk3ZHAtqXs=",
      "email": "you@example.com"
    },
    "cloud.openshift.com": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "quay.io": {
      "auth": "b3BlbnNo...",
      "email": "you@example.com"
    },
    "registry.connect.redhat.com": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    },
    "registry.redhat.io": {
      "auth": "NTE3Njg5Nj...",
      "email": "you@example.com"
    }
  }
}
```

#### 11.2.2.3. 미러 레지스트리에 이미지 미러링

중요

OpenShift Update Service 애플리케이션의 과도한 메모리 사용을 방지하려면 다음 절차에 설명된 대로 릴리스 이미지를 별도의 저장소에 미러링해야 합니다.

사전 요구 사항

연결이 끊긴 환경에서 사용할 미러 레지스트리를 구성하고 구성한 인증서 및 인증 정보에 액세스할 수 있습니다.

Red Hat OpenShift Cluster Manager에서 풀 시크릿 을 다운로드하여 미러 저장소에 대한 인증을 포함하도록 수정했습니다.

자체 서명된 인증서를 사용하는 경우 인증서에 주체 대체 이름을 지정했습니다.

프로세스

Red Hat OpenShift Container Platform Update Graph 시각화 프로그램 및 업데이트 플래너 를 사용하여 한 버전에서 다른 버전으로 업데이트를 계획합니다. OpenShift Update Graph는 채널 그래프와 현재 클러스터 버전과 의도한 클러스터 버전 간에 업데이트 경로가 있는지 확인하는 방법을 제공합니다.

필요한 환경 변수를 설정합니다.

릴리스 버전을 내보냅니다.

```shell-session
$ export OCP_RELEASE=<release_version>
```

`<release_version>` 에 대해 업데이트할 OpenShift Container Platform 버전에 해당하는 태그를 지정합니다 (예: `4.5.4`).

로컬 레지스트리 이름 및 호스트 포트를 내보냅니다.

```shell-session
$ LOCAL_REGISTRY='<local_registry_host_name>:<local_registry_host_port>'
```

`<local_registry_host_name>` 의 경우 미러 저장소의 레지스트리 도메인 이름을 지정하고 `<local_registry_host_port>` 의 경우 콘텐츠를 제공하는데 사용되는 포트를 지정합니다.

로컬 저장소 이름을 내보냅니다.

```shell-session
$ LOCAL_REPOSITORY='<local_repository_name>'
```

`<local_repository_name>` 의 경우 레지스트리에 작성할 저장소 이름 (예: `ocp4/openshift4`)을 지정합니다.

OpenShift Update Service를 사용하는 경우 릴리스 이미지를 포함하도록 추가 로컬 리포지토리 이름을 내보냅니다.

```shell-session
$ LOCAL_RELEASE_IMAGES_REPOSITORY='<local_release_images_repository_name>'
```

`<local_release_images_repository_name>` 의 경우 레지스트리에 작성할 저장소 이름 (예: `ocp4/openshift4-release-images`)을 지정합니다.

미러링할 저장소 이름을 내보냅니다.

```shell-session
$ PRODUCT_REPO='openshift-release-dev'
```

프로덕션 환경의 릴리스의 경우 `openshift-release-dev` 를 지정해야 합니다.

레지스트리 풀 시크릿의 경로를 내보냅니다.

```shell-session
$ LOCAL_SECRET_JSON='<path_to_pull_secret>'
```

생성한 미러 레지스트리에 대한 풀 시크릿의 절대 경로 및 파일 이름을 `<path_to_pull_secret>` 에 지정합니다.

참고

클러스터에서 `ImageContentSourcePolicy` 오브젝트를 사용하여 저장소 미러링을 구성하는 경우 미러링된 레지스트리에 대한 글로벌 풀 시크릿만 사용할 수 있습니다. 프로젝트에 풀 시크릿을 추가할 수 없습니다.

릴리스 미러를 내보냅니다.

```shell-session
$ RELEASE_NAME="ocp-release"
```

프로덕션 환경의 릴리스의 경우 `ocp-release` 를 지정해야 합니다.

클러스터의 아키텍처 유형을 내보냅니다.

```shell-session
$ ARCHITECTURE=<cluster_architecture>
```

1. `x86_64`, `aarch64`, `s390x` 또는 `ppc64le` 과 같은 클러스터의 아키텍처를 지정합니다.

미러링된 이미지를 호스트할 디렉터리의 경로를 내보냅니다.

```shell-session
$ REMOVABLE_MEDIA_PATH=<path>
```

1. 초기 슬래시 (/) 문자를 포함하여 전체 경로를 지정합니다.

미러링할 이미지 및 설정 매니페스트를 확인합니다.

```shell-session
$ oc adm release mirror -a ${LOCAL_SECRET_JSON} --to-dir=${REMOVABLE_MEDIA_PATH}/mirror quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE}-${ARCHITECTURE} --dry-run
```

미러 레지스트리에 버전 이미지를 미러링합니다.

미러 호스트가 인터넷에 액세스할 수 없는 경우 다음 작업을 수행합니다.

이동식 미디어를 인터넷에 연결된 시스템에 연결합니다.

이미지 및 설정 매니페스트를 이동식 미디어의 디렉토리에 미러링합니다.

```shell-session
$ oc adm release mirror -a ${LOCAL_SECRET_JSON} --to-dir=${REMOVABLE_MEDIA_PATH}/mirror quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE}-${ARCHITECTURE}
```

참고

이 명령은 미러링된 릴리스 이미지 서명 구성 맵을 생성하고 이동식 미디어에 저장합니다.

미디어를 연결이 끊긴 환경으로 가져와서 이미지를 로컬 컨테이너 레지스트리에 업로드합니다.

```shell-session
$ oc image mirror  -a ${LOCAL_SECRET_JSON} --from-dir=${REMOVABLE_MEDIA_PATH}/mirror "file://openshift/release:${OCP_RELEASE}*" ${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}
```

1. `REMOVABLE_MEDIA_PATH` 의 경우 이미지를 미러링 할 때 지정한 것과 동일한 경로를 사용해야 합니다.

다음 명령CLI(명령줄 인터페이스)를 사용하여 업데이트 중인 클러스터에 로그인합니다.

```shell
oc
```

미러링된 릴리스 이미지 서명 config map을 연결된 클러스터에 적용합니다.

```shell-session
$ oc apply -f ${REMOVABLE_MEDIA_PATH}/mirror/config/<image_signature_file>
```

1. < `image_signature_file` >의 경우 파일의 경로와 이름을 지정합니다(예: `signature-sha256-81154f5c03294534.yaml`).

OpenShift Update Service를 사용하는 경우 릴리스 이미지를 별도의 저장소에 미러링합니다.

```shell-session
$ oc image mirror -a ${LOCAL_SECRET_JSON} ${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE} ${LOCAL_REGISTRY}/${LOCAL_RELEASE_IMAGES_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE}
```

로컬 컨테이너 레지스트리와 클러스터가 미러 호스트에 연결된 경우 다음 작업을 수행합니다.

릴리스 이미지를 로컬 레지스트리로 직접 푸시하고 다음 명령을 사용하여 구성 맵을 클러스터에 적용합니다.

```shell-session
$ oc adm release mirror -a ${LOCAL_SECRET_JSON} --from=quay.io/${PRODUCT_REPO}/${RELEASE_NAME}:${OCP_RELEASE}-${ARCHITECTURE} \
  --to=${LOCAL_REGISTRY}/${LOCAL_REPOSITORY} --apply-release-image-signature
```

참고

`--apply-release-image-signature` 옵션이 포함된 경우 이미지 서명 확인을 위해 config map을 작성하지 않습니다.

OpenShift Update Service를 사용하는 경우 릴리스 이미지를 별도의 저장소에 미러링합니다.

```shell-session
$ oc image mirror -a ${LOCAL_SECRET_JSON} ${LOCAL_REGISTRY}/${LOCAL_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE} ${LOCAL_REGISTRY}/${LOCAL_RELEASE_IMAGES_REPOSITORY}:${OCP_RELEASE}-${ARCHITECTURE}
```

### 11.3. OpenShift Update Service를 사용하여 연결이 끊긴 환경에서 클러스터 업데이트

연결된 클러스터와 유사한 업데이트 환경을 얻으려면 다음 절차를 사용하여 연결이 끊긴 환경에서 OSUS(OpenShift Update Service)를 설치하고 구성할 수 있습니다.

다음 단계에서는 OSUS를 사용하여 연결이 끊긴 환경에서 클러스터를 업데이트하는 방법에 대한 고급 워크플로를 간략하게 설명합니다.

보안 레지스트리에 대한 액세스를 구성합니다.

미러 레지스트리에 액세스하려면 글로벌 클러스터 풀 시크릿을 업데이트합니다.

OSUS Operator를 설치합니다.

OpenShift 업데이트 서비스에 대한 그래프 데이터 컨테이너 이미지를 생성합니다.

OSUS 애플리케이션을 설치하고 사용자 환경에서 OpenShift Update Service를 사용하도록 클러스터를 구성합니다.

연결된 클러스터와 마찬가지로 문서에서 지원되는 업데이트 절차를 수행합니다.

#### 11.3.1. 연결이 끊긴 환경에서 OpenShift Update Service 사용

OSUS(OpenShift Update Service)는 OpenShift Container Platform 클러스터에 대한 업데이트 권장 사항을 제공합니다. Red Hat은 OpenShift Update Service를 공개적으로 호스팅하며 연결된 환경의 클러스터는 공용 API를 통해 서비스에 연결하여 업데이트 권장 사항을 검색할 수 있습니다.

그러나 연결이 끊긴 환경의 클러스터는 이러한 공용 API에 액세스하여 업데이트 정보를 검색할 수 없습니다. 연결이 끊긴 환경에서 유사한 업데이트 환경을 보유하려면 연결이 끊긴 환경에서 사용할 수 있도록 OpenShift 업데이트 서비스를 설치하고 구성할 수 있습니다.

단일 OSUS 인스턴스는 수천 개의 클러스터에 권장 사항을 제공할 수 있습니다. OSUS는 복제본 값을 변경하여 더 많은 클러스터를 수용하도록 수평으로 확장할 수 있습니다. 따라서 대부분의 연결이 끊긴 사용 사례의 경우 하나의 OSUS 인스턴스만으로도 충분합니다. 예를 들어, Red Hat은 연결된 클러스터의 전체 플릿에 대해 하나의 OSUS 인스턴스를 호스팅합니다.

다른 환경에서 업데이트 권장 사항을 별도로 유지하려면 각 환경에 대해 하나의 OSUS 인스턴스를 실행할 수 있습니다. 예를 들어 별도의 테스트 및 스테이징 환경이 있는 경우 스테이지 환경의 클러스터가 테스트 환경에서 테스트 환경에서 테스트되지 않은 경우 버전 A에 대한 업데이트 권장 사항을 수신하지 않도록 할 수 있습니다.

다음 섹션에서는 OSUS 인스턴스를 설치하고 클러스터에 업데이트 권장 사항을 제공하도록 구성하는 방법을 설명합니다.

추가 리소스

OpenShift 업데이트 서비스 정보

업데이트 채널 및 릴리스 이해

#### 11.3.2. 사전 요구 사항

아래 명령 줄 인터페이스 (CLI) 툴이 설치되어 있어야합니다.

```shell
oc
```

OpenShift Container Platform 이미지 미러링 에 설명된 대로 업데이트의 컨테이너 이미지를 사용하여 환경에 컨테이너 이미지 레지스트리를 프로비저닝해야 합니다.

#### 11.3.3. OpenShift Update Service의 보안 레지스트리에 대한 액세스 구성

릴리스 이미지가 사용자 정의 인증 기관에서 HTTPS X.509 인증서를 서명한 레지스트리에 포함된 경우 업데이트 서비스에 대한 다음 변경과 함께 이미지 레지스트리 액세스를 위한 추가 신뢰 저장소 구성 단계를 완료합니다.

OpenShift Update Service Operator는 레지스트리 CA 인증서에 구성 맵 키 이름 `updateservice-registry` 가 필요합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-registry-ca
data:
  updateservice-registry: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
  registry-with-port.example.com..5000: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
```

1. OpenShift Update Service Operator에는 레지스트리 CA 인증서에 구성 맵 키 이름 `updateservice-registry` 가 필요합니다.

2. 레지스트리에 `registry-with-port.example.com:5000` 같은 포트가 있는 경우 `:` 이 `..` 로 교체되어야 합니다.

#### 11.3.4. 글로벌 클러스터 풀 시크릿 업데이트

현재 풀 시크릿을 교체하거나 새 풀 시크릿을 추가하여 클러스터의 글로벌 풀 시크릿을 업데이트할 수 있습니다.

설치 중에 사용된 레지스트리보다 이미지를 저장하기 위해 별도의 레지스트리가 필요한 경우 절차를 사용하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

선택 사항: 기존 풀 시크릿에 새 풀 시크릿을 추가하려면 다음 단계를 완료합니다.

다음 명령을 입력하여 풀 시크릿을 다운로드합니다.

```shell-session
$ oc get secret/pull-secret -n openshift-config --template='{{index .data ".dockerconfigjson" | base64decode}}' > <pull_secret_location>
```

1. `<pull_secret_location` >: 풀 시크릿 파일의 경로를 포함합니다.

다음 명령을 입력하여 새 풀 시크릿을 추가합니다.

```shell-session
$ oc registry login --registry="<registry>" \
--auth-basic="<username>:<password>" \
--to=<pull_secret_location>
```

1. `<registry` >: 새 레지스트리를 포함합니다. 동일한 레지스트리에 여러 리포지토리를 포함할 수 있습니다(예: `--registry="<registry/my-namespace/my-repository>`).

2. `<username>:<password` >: 새 레지스트리의 인증 정보를 포함합니다.

3. `<pull_secret_location` >: 풀 시크릿 파일의 경로를 포함합니다.

풀 시크릿 파일에 대한 수동 업데이트를 수행할 수도 있습니다.

다음 명령을 입력하여 클러스터의 글로벌 풀 시크릿을 업데이트합니다.

```shell-session
$ oc set data secret/pull-secret -n openshift-config \
  --from-file=.dockerconfigjson=<pull_secret_location>
```

1. `<pull_secret_location` >: 새 풀 시크릿 파일의 경로를 추가합니다.

이번 업데이트에서는 모든 노드에 롤아웃되며 클러스터 크기에 따라 다소 시간이 걸릴 수 있습니다.

참고

OpenShift Container Platform 4.7.4부터 글로벌 풀 시크릿을 변경해도 더 이상 노드 드레이닝 또는 재부팅이 트리거되지 않습니다.

#### 11.3.5. OpenShift Update Service Operator 설치

OpenShift Update Service를 설치하려면 먼저 OpenShift Container Platform 웹 콘솔 또는 CLI를 사용하여 OpenShift Update Service Operator를 설치해야 합니다.

참고

연결이 끊긴 클러스터(연결이 끊긴 클러스터)에 설치된 클러스터의 경우 Operator Lifecycle Manager는 기본적으로 원격 레지스트리에서 호스팅되는 Red Hat 제공 소프트웨어 카탈로그 소스에 액세스할 수 없습니다. 이러한 원격 소스에는 완전한 인터넷 연결이 필요하기 때문입니다.

자세한 내용은 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용을 참조하십시오.

#### 11.3.5.1. 웹 콘솔을 사용하여 OpenShift Update Service Operator 설치

웹 콘솔을 사용하여 OpenShift Update Service Operator를 설치할 수 있습니다.

프로세스

웹 콘솔에서 Ecosystem → Software Catalog 를 클릭합니다.

참고

`Update Service` 를 키워드로 필터링…​ 필드에 입력하여 Operator를 더 빠르게 찾습니다.

사용 가능한 Operator 목록에서 OpenShift Update Service 를 선택한 다음 설치 를 클릭합니다.

업데이트 채널을 선택합니다.

버전을 선택합니다.

설치 모드 에서 클러스터의 특정 네임스페이스 를 선택합니다.

설치된 네임스페이스 의 네임스페이스를 선택하거나 권장 네임스페이스 `openshift-update-service` 를 수락합니다.

업데이트 승인 전략을 선택합니다.

자동 전략을 사용하면 Operator 새 버전이 준비될 때 OLM(Operator Lifecycle Manager)이 자동으로 Operator를 업데이트할 수 있습니다.

수동 전략을 사용하려면 클러스터 관리자가 Operator 업데이트를 승인해야 합니다.

설치 를 클릭합니다.

에코시스템 → 설치된 Operator 로 이동하여 OpenShift Update Service Operator가 설치되었는지 확인합니다.

OpenShift Update Service 가 올바른 네임스페이스에 성공

상태 로 나열되어 있는지 확인합니다.

#### 11.3.5.2. CLI를 사용하여 OpenShift Update Service Operator 설치

OpenShift CLI()를 사용하여 OpenShift Update Service Operator를 설치할 수 있습니다.

```shell
oc
```

프로세스

OpenShift OpenShift Update Service Operator의 네임스페이스를 생성합니다.

OpenShift Update Service Operator에 대해 `Namespace` 오브젝트 YAML 파일 (예: `update-service-namespace.yaml`)을 만듭니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-update-service
  annotations:
    openshift.io/node-selector: ""
  labels:
    openshift.io/cluster-monitoring: "true"
```

1. 이 네임스페이스에서 Operator가 권장하는 클러스터 모니터링을 사용하도록 하려면 `openshift.io/cluster-monitoring` 레이블을 설정합니다.

네임스페이스를 생성합니다.

```shell-session
$ oc create -f <filename>.yaml
```

예를 들면 다음과 같습니다.

```shell-session
$ oc create -f update-service-namespace.yaml
```

다음 오브젝트를 생성하여 OpenShift Update Service Operator를 설치합니다.

`OperatorGroup` 오브젝트 YAML 파일을 만듭니다 (예: `update-service-operator-group.yaml`).

```yaml
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: update-service-operator-group
  namespace: openshift-update-service
spec:
  targetNamespaces:
  - openshift-update-service
```

`OperatorGroup` 오브젝트를 생성합니다.

```shell-session
$ oc -n openshift-update-service create -f <filename>.yaml
```

예를 들면 다음과 같습니다.

```shell-session
$ oc -n openshift-update-service create -f update-service-operator-group.yaml
```

`Subscription` 오브젝트 YAML 파일(예: `update-service-subscription.yaml`)을 생성합니다.

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: update-service-subscription
  namespace: openshift-update-service
spec:
  channel: v1
  installPlanApproval: "Automatic"
  source: "redhat-operators"
  sourceNamespace: "openshift-marketplace"
  name: "cincinnati-operator"
```

1. Operator를 제공하는 카탈로그 소스의 이름을 지정합니다. 사용자 정의 OLM(Operator Lifecycle Manager)을 사용하지 않는 클러스터의 경우 `redhat-operators` 를 지정합니다.

OpenShift Container Platform 클러스터가 연결이 끊긴 환경에 설치된 경우 OLM(Operator Lifecycle Manager)을 구성할 때 생성된 `CatalogSource` 오브젝트의 이름을 지정합니다.

`Subscription` 오브젝트를 생성합니다.

```shell-session
$ oc create -f <filename>.yaml
```

예를 들면 다음과 같습니다.

```shell-session
$ oc -n openshift-update-service create -f update-service-subscription.yaml
```

OpenShift Update Service Operator는 `openshift-update-service` 네임스페이스에 설치되고 `openshift-update-service` 네임스페이스를 대상으로 합니다.

Operator 설치를 확인합니다.

```shell-session
$ oc -n openshift-update-service get clusterserviceversions
```

```shell-session
NAME                             DISPLAY                    VERSION   REPLACES   PHASE
update-service-operator.v4.6.0   OpenShift Update Service   4.6.0                Succeeded
...
```

OpenShift Update Service Operator가 나열된 경우 설치에 성공한 것입니다. 버전 번호가 표시된 것과 다를 수 있습니다.

추가 리소스

네임스페이스에 Operator 설치

#### 11.3.6. OpenShift Update Service 그래프 데이터 컨테이너 이미지 생성

OpenShift Update Service에는 그래프 데이터 컨테이너 이미지가 필요합니다. 여기서 OpenShift Update Service는 채널 멤버십 및 차단된 업데이트 에지에 대한 정보를 검색합니다.

일반적으로 그래프 데이터는 업데이트 그래프 데이터 리포지토리에서 직접 가져옵니다. 인터넷 연결이 불가능한 환경에서 init 컨테이너에서 이 정보를 로드하는 것도 OpenShift 업데이트 서비스에서 그래프 데이터를 사용할 수 있도록 하는 또 다른 방법입니다.

init 컨테이너의 역할은 그래프 데이터의 로컬 사본을 제공하는 것이며 pod 초기화 중에 init 컨테이너가 서비스에서 액세스할 수 있는 볼륨에 데이터를 복사하는 것입니다.

참고

oc-mirror OpenShift CLI() 플러그인은 릴리스 이미지 미러링 외에도 이 그래프 데이터 컨테이너 이미지를 생성합니다. oc-mirror 플러그인을 사용하여 릴리스 이미지를 미러링한 경우 이 절차를 건너뛸 수 있습니다.

```shell
oc
```

프로세스

다음을 포함하는 Dockerfile(예: `./Dockerfile`)을 생성합니다.

```shell-session
FROM registry.access.redhat.com/ubi9/ubi:latest

RUN curl -L -o cincinnati-graph-data.tar.gz https://api.openshift.com/api/upgrades_info/graph-data

RUN mkdir -p /var/lib/cincinnati-graph-data && tar xvzf cincinnati-graph-data.tar.gz -C /var/lib/cincinnati-graph-data/ --no-overwrite-dir --no-same-owner

CMD ["/bin/bash", "-c" ,"exec cp -rp /var/lib/cincinnati-graph-data/* /var/lib/cincinnati/graph-data"]
```

위 단계에서 생성된 Docker 파일을 사용하여 그래프 데이터 컨테이너 이미지(예: `registry.example.com/openshift/graph-data:latest`)를 빌드합니다.

```shell-session
$ podman build -f ./Dockerfile -t registry.example.com/openshift/graph-data:latest
```

이전 단계에서 생성한 그래프 데이터 컨테이너 이미지를 OpenShift Update Service에 액세스할 수 있는 리포지토리(예: `registry.example.com/openshift/graph-data:latest`)로 푸시합니다.

```shell-session
$ podman push registry.example.com/openshift/graph-data:latest
```

참고

그래프 데이터 이미지를 연결이 끊긴 환경의 레지스트리로 내보내려면 이전 단계에서 생성한 그래프 데이터 컨테이너 이미지를 OpenShift Update Service에서 액세스할 수 있는 리포지토리에 복사합니다. 사용 가능한 옵션에 대해 다음 명령을 실행합니다.

```shell
oc image mirror --help
```

#### 11.3.7. OpenShift Update Service 애플리케이션 생성

OpenShift Container Platform 웹 콘솔 또는 CLI를 사용하여 OpenShift Update Service 애플리케이션을 생성할 수 있습니다.

#### 11.3.7.1. 웹 콘솔을 사용하여 OpenShift Update Service 애플리케이션 생성

OpenShift Container Platform 웹 콘솔을 사용하여 OpenShift Update Service Operator를 사용하여 OpenShift Update Service 애플리케이션을 생성할 수 있습니다.

사전 요구 사항

OpenShift Update Service Operator가 설치되었습니다.

OpenShift Update Service 그래프 데이터 컨테이너 이미지가 생성되어 OpenShift Update Service에서 액세스할 수 있는 리포지토리로 푸시되었습니다.

현재 릴리스 및 업데이트 대상 릴리스는 연결이 끊긴 환경의 레지스트리에 미러링되었습니다.

프로세스

웹 콘솔에서 에코시스템 → 설치된 Operator

를 클릭합니다.

설치된 Operator 목록에서 OpenShift Update Service 를 선택합니다.

Update Service 탭을 클릭합니다.

Create UpdateService 를 클릭합니다.

Name 필드에 이름을 입력합니다. (예: `service`)

그래프 데이터 이미지 필드에 "OpenShift Update Service 그래프 데이터 컨테이너 이미지 생성"에서 생성된 그래프 데이터 컨테이너 이미지에 로컬 pullspec을 입력합니다(예: `registry.example.com/openshift/graph-data:latest`).

릴리스 필드에 "OpenShift Container Platform 이미지 리포지토리 미러링"의 릴리스 이미지를 포함하도록 생성된 레지스트리 및 리포지토리를 입력합니다(예: `registry.example.com/ocp4/openshift4-release-images`).

Replicas 필드에 `2` 를 입력합니다.

Create 를 클릭하여 OpenShift Update Service 애플리케이션을 생성합니다.

OpenShift Update Service 애플리케이션 확인

Update Service 탭의 UpdateServices 목록에서 방금 만든 업데이트 서비스 애플리케이션을 클릭합니다.

Resources 탭을 클릭합니다.

각 애플리케이션 리소스의 상태가 Created 인지 확인합니다.

#### 11.3.7.2. CLI를 사용하여 OpenShift Update Service 애플리케이션 생성

OpenShift CLI()를 사용하여 OpenShift Update Service 애플리케이션을 생성할 수 있습니다.

```shell
oc
```

사전 요구 사항

OpenShift Update Service Operator가 설치되었습니다.

OpenShift Update Service 그래프 데이터 컨테이너 이미지가 생성되어 OpenShift Update Service에서 액세스할 수 있는 리포지토리로 푸시되었습니다.

현재 릴리스 및 업데이트 대상 릴리스는 연결이 끊긴 환경의 레지스트리에 미러링되었습니다.

프로세스

OpenShift Update Service 대상 네임스페이스를 구성합니다(예: `openshift-update-service`).

```shell-session
$ NAMESPACE=openshift-update-service
```

네임스페이스는 Operator 그룹의 `targetNamespaces` 값과 일치해야 합니다.

OpenShift Update Service 애플리케이션의 이름을 구성합니다(예: `service`).

```shell-session
$ NAME=service
```

"OpenShift Container Platform 이미지 리포지토리 미러링"에 구성된 릴리스 이미지의 레지스트리 및 리포지토리를 구성합니다(예: `registry.example.com/ocp4/openshift4-release-images`).

```shell-session
$ RELEASE_IMAGES=registry.example.com/ocp4/openshift4-release-images
```

그래프 데이터 이미지의 로컬 pullspec을 "OpenShift Update Service 그래프 데이터 컨테이너 이미지 생성"에서 생성된 그래프 데이터 컨테이너 이미지로 설정합니다(예: `registry.example.com/openshift/graph-data:latest`).

```shell-session
$ GRAPH_DATA_IMAGE=registry.example.com/openshift/graph-data:latest
```

OpenShift Update Service 애플리케이션 오브젝트를 생성합니다.

```shell-session
$ oc -n "${NAMESPACE}" create -f - <<EOF
apiVersion: updateservice.operator.openshift.io/v1
kind: UpdateService
metadata:
  name: ${NAME}
spec:
  replicas: 2
  releases: ${RELEASE_IMAGES}
  graphDataImage: ${GRAPH_DATA_IMAGE}
EOF
```

OpenShift Update Service 애플리케이션 확인

다음 명령을 사용하여 정책 엔진 경로를 가져옵니다.

```shell-session
$ while sleep 1; do POLICY_ENGINE_GRAPH_URI="$(oc -n "${NAMESPACE}" get -o jsonpath='{.status.policyEngineURI}/api/upgrades_info/v1/graph{"\n"}' updateservice "${NAME}")"; SCHEME="${POLICY_ENGINE_GRAPH_URI%%:*}"; if test "${SCHEME}" = http -o "${SCHEME}" = https; then break; fi; done
```

명령이 성공할 때까지 폴링해야 할 수도 있습니다.

정책 엔진에서 그래프를 검색합니다. `channel` 에 유효한 버전을 지정해야 합니다. 예를 들어 OpenShift Container Platform 4.20에서 실행 중인 경우 `stable-4.20`:을 사용하십시오.

```shell-session
$ while sleep 10; do HTTP_CODE="$(curl --header Accept:application/json --output /dev/stderr --write-out "%{http_code}" "${POLICY_ENGINE_GRAPH_URI}?channel=stable-4.6")"; if test "${HTTP_CODE}" -eq 200; then break; fi; echo "${HTTP_CODE}"; done
```

이 경우 그래프 요청이 성공할 때까지 폴링되지만 미러링된 릴리스 이미지에 따라 결과 그래프가 비어 있을 수 있습니다.

참고

정책 엔진 경로 이름은 RFC-1123을 기반으로 63자 이하여야 합니다.

`host must conform to DNS 1123 naming convention and must be no more than 63 characters` 로 인해 `CreateRouteFailed` 이유와 함께 `ReconcileCompleted` 상태가 `false` 인 경우 더 짧은 이름으로 업데이트 서비스를 생성하십시오.

#### 11.3.8. Cluster Version Operator (CVO) 구성

OpenShift Update Service Operator가 설치되고 OpenShift Update Service 애플리케이션이 생성되면 CVO(Cluster Version Operator)를 업데이트하여 환경에 설치된 OpenShift Update Service에서 그래프 데이터를 가져올 수 있습니다.

사전 요구 사항

OpenShift Update Service Operator가 설치되었습니다.

OpenShift Update Service 그래프 데이터 컨테이너 이미지가 생성되어 OpenShift Update Service에서 액세스할 수 있는 리포지토리로 푸시되었습니다.

현재 릴리스 및 업데이트 대상 릴리스는 연결이 끊긴 환경의 레지스트리에 미러링되었습니다.

OpenShift Update Service 애플리케이션이 생성되었습니다.

프로세스

OpenShift Update Service 대상 네임스페이스를 설정합니다(예: `openshift-update-service`).

```shell-session
$ NAMESPACE=openshift-update-service
```

OpenShift Update Service 애플리케이션의 이름을 설정합니다(예: `service`).

```shell-session
$ NAME=service
```

정책 엔진 경로를 가져옵니다.

```shell-session
$ POLICY_ENGINE_GRAPH_URI="$(oc -n "${NAMESPACE}" get -o jsonpath='{.status.policyEngineURI}/api/upgrades_info/v1/graph{"\n"}' updateservice "${NAME}")"
```

풀 그래프 데이터의 패치를 설정합니다.

```shell-session
$ PATCH="{\"spec\":{\"upstream\":\"${POLICY_ENGINE_GRAPH_URI}\"}}"
```

CVO를 패치하여 사용자 환경에서 OpenShift Update Service를 사용합니다.

```shell-session
$ oc patch clusterversion version -p $PATCH --type merge
```

참고

업데이트 서버 를 신뢰하도록 CA를 구성하려면 클러스터 전체 프록시 구성 을 참조하십시오.

#### 11.3.9. 다음 단계

클러스터를 업데이트하기 전에 다음 조건이 충족되었는지 확인합니다.

CVO(Cluster Version Operator)는 설치된 OpenShift Update Service 애플리케이션을 사용하도록 구성되어 있습니다.

새 릴리스의 릴리스 이미지 서명 구성 맵이 클러스터에 적용됩니다.

참고

CVO(Cluster Version Operator)는 릴리스 이미지 서명을 사용하여 릴리스 이미지 서명이 예상되는 결과와 일치하는지 확인하여 릴리스 이미지가 수정되지 않았는지 확인합니다.

현재 릴리스 및 업데이트 대상 릴리스 이미지가 연결이 끊긴 환경의 레지스트리에 미러링됩니다.

최근 그래프 데이터 컨테이너 이미지가 레지스트리에 미러링되었습니다.

최신 버전의 OpenShift Update Service Operator가 설치되어 있습니다.

참고

OpenShift Update Service Operator를 최근에 설치하거나 업데이트하지 않은 경우 더 최신 버전이 있을 수 있습니다. 연결이 끊긴 환경에서 OLM 카탈로그를 업데이트하는 방법에 대한 자세한 내용은 연결이 끊긴 환경에서 Operator Lifecycle Manager 사용을 참조하십시오.

설치된 OpenShift Update Service 및 로컬 미러 레지스트리를 사용하도록 클러스터를 구성한 후 다음 업데이트 방법을 사용할 수 있습니다.

웹 콘솔을 사용하여 클러스터 업데이트

CLI를 사용하여 클러스터 업데이트

컨트롤 플레인만 업데이트 수행

카나리아 롤아웃 업데이트 수행

### 11.4. OpenShift Update Service 없이 연결이 끊긴 환경에서 클러스터 업데이트

다음 절차를 사용하여 OpenShift Update Service에 액세스하지 않고 연결이 끊긴 환경에서 클러스터를 업데이트합니다.

#### 11.4.1. 사전 요구 사항

아래 명령 줄 인터페이스 (CLI) 툴이 설치되어 있어야합니다.

```shell
oc
```

OpenShift Container Platform 이미지 미러링에 설명된 대로 업데이트의 컨테이너 이미지로 로컬 컨테이너 이미지 레지스트리를 프로비저닝해야 합니다.

`admin` 권한이 있는 사용자로 클러스터에 액세스할 수 있어야 합니다. RBAC를 사용하여 권한 정의 및 적용을 참조하십시오.

업데이트가 실패하는 경우 etcd 백업이 있어야 하며 클러스터를 이전 상태로 복원해야 합니다.

OLM(Operator Lifecycle Manager)을 통해 이전에 설치된 모든 Operator를 대상 릴리스와 호환되는 버전으로 업데이트했습니다. Operator를 업데이트하면 클러스터 업데이트 중에 기본 카탈로그 소스가 현재 마이너 버전에서 다음 버전으로 전환될 때 유효한 업데이트 경로가 있습니다.

호환성을 확인하고 필요한 경우 설치된 Operator를 업데이트하는 방법에 대한 자세한 내용은 설치된 Operator 업데이트를 참조하십시오.

모든 MCP(Machine config pool)가 실행 중이고 일시 중지되지 않았는지 확인해야 합니다. 업데이트 프로세스 중에 일시 중지된 MCP와 연결된 노드를 건너뜁니다. 카나리아 롤아웃 업데이트 전략을 수행하는 경우 MCP를 일시 중지할 수 있습니다.

클러스터에서 수동으로 유지 관리되는 인증 정보를 사용하는 경우 새 릴리스의 클라우드 공급자 리소스를 업데이트합니다. 클러스터의 요구 사항인지 확인하는 방법을 포함하여 자세한 내용은 수동으로 유지 관리되는 인증 정보를 사용하여 클러스터 업데이트 준비를 참조하십시오.

Operator를 실행하거나 Pod 중단 예산으로 애플리케이션을 구성한 경우 업데이트 프로세스 중에 중단이 발생할 수 있습니다. `PodDisruptionBudget` 에서 `minAvailable` 이 1로 설정된 경우 제거 프로세스를 차단할 수 있는 보류 중인 머신 구성을 적용하기 위해 노드가 드레인됩니다.

여러 노드가 재부팅되면 모든 Pod가 하나의 노드에서만 실행될 수 있으며 `PodDisruptionBudget` 필드에는 노드가 드레이닝되지 않을 수 있습니다.

참고

Operator를 실행하거나 Pod 중단 예산으로 애플리케이션을 구성한 경우 업데이트 프로세스 중에 중단이 발생할 수 있습니다. `PodDisruptionBudget` 에서 `minAvailable` 이 1로 설정된 경우 제거 프로세스를 차단할 수 있는 보류 중인 머신 구성을 적용하기 위해 노드가 드레인됩니다.

여러 노드가 재부팅되면 모든 Pod가 하나의 노드에서만 실행될 수 있으며 `PodDisruptionBudget` 필드에는 노드가 드레이닝되지 않을 수 있습니다.

#### 11.4.2. MachineHealthCheck 리소스 일시 중지

업데이트 프로세스 중에 클러스터의 노드를 일시적으로 사용할 수 없게 될 수 있습니다. 작업자 노드의 경우 `MachineHealthCheck` 리소스에서 이러한 노드를 비정상으로 식별하고 재부팅할 수 있습니다. 이러한 노드를 재부팅하지 않으려면 클러스터를 업데이트하기 전에 모든 `MachineHealthCheck` 리소스를 일시 중지합니다.

참고

일부 `MachineHealthCheck` 리소스를 일시 중지하지 않아도 될 수 있습니다. `MachineHealthCheck` 리소스가 복구할 수 없는 조건에 의존하는 경우 MHC가 필요하지 않은 상태를 일시 중지합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로세스

일시 중지하려는 사용 가능한 `MachineHealthCheck` 리소스를 모두 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc get machinehealthcheck -n openshift-machine-api
```

머신 상태 점검을 일시 중지하려면 `cluster.x-k8s.io/paused=""` 주석을 `MachineHealthCheck` 리소스에 추가합니다. 다음 명령을 실행합니다.

```shell-session
$ oc -n openshift-machine-api annotate mhc <mhc-name> cluster.x-k8s.io/paused=""
```

주석이 지정된 `MachineHealthCheck` 리소스는 다음 YAML 파일과 유사합니다.

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: example
  namespace: openshift-machine-api
  annotations:
    cluster.x-k8s.io/paused: ""
spec:
  selector:
    matchLabels:
      role: worker
  unhealthyConditions:
  - type:    "Ready"
    status:  "Unknown"
    timeout: "300s"
  - type:    "Ready"
    status:  "False"
    timeout: "300s"
  maxUnhealthy: "40%"
status:
  currentHealthy: 5
  expectedMachines: 5
```

중요

클러스터를 업데이트한 후 머신 상태 점검을 다시 시작합니다. 검사를 다시 시작하려면 다음 명령을 실행하여 `MachineHealthCheck` 리소스에서 일시 중지 주석을 제거합니다.

```shell-session
$ oc -n openshift-machine-api annotate mhc <mhc-name> cluster.x-k8s.io/paused-
```

#### 11.4.3. 릴리스 이미지 다이제스트 검색

아래 명령을 `--to-image` 옵션과 함께 사용하여 연결이 끊긴 환경에서 클러스터를 업데이트하려면 대상 릴리스 이미지에 해당하는 sha256 다이제스트를 참조해야 합니다.

```shell
oc adm upgrade
```

프로세스

인터넷에 연결된 장치에서 다음 명령을 실행합니다.

```shell-session
$ oc adm release info -o 'jsonpath={.digest}{"\n"}' quay.io/openshift-release-dev/ocp-release:${OCP_RELEASE_VERSION}-${ARCHITECTURE}
```

`{OCP_RELEASE_VERSION}` 의 경우 `4.10.16` 과 같이 업데이트할 OpenShift Container Platform 버전을 지정합니다.

`{ARCHITECTURE}` 의 경우 `x86_64`, `aarch64`, `s390x` 또는 `ppc64le` 과 같은 클러스터 아키텍처를 지정합니다.

```shell-session
sha256:a8bfba3b6dddd1a2fbbead7dac65fe4fb8335089e4e7cae327f3bad334add31d
```

클러스터를 업데이트할 때 사용할 sha256 다이제스트를 복사합니다.

#### 11.4.4. 연결이 끊긴 클러스터 업데이트

연결이 끊긴 클러스터를 다운로드한 릴리스 이미지를 OpenShift Container Platform 버전으로 업데이트합니다.

참고

로컬 OpenShift Update Service가 있는 경우 이 절차 대신 연결된 웹 콘솔 또는 CLI 지침을 사용하여 업데이트할 수 있습니다.

사전 요구 사항

새 릴리스의 이미지를 레지스트리에 미러링하고 있습니다.

새 릴리스의 릴리스 이미지 서명 ConfigMap을 클러스터에 적용하고 있습니다.

참고

릴리스 이미지 서명 구성 맵을 사용하면 CVO(Cluster Version Operator)에서 실제 이미지 서명이 예상 서명과 일치하는지 확인하여 릴리스 이미지의 무결성을 보장할 수 있습니다.

대상 릴리스 이미지에 대한 sha256 다이제스트를 가져옵니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

모든 `MachineHealthCheck` 리소스를 일시 중지했습니다.

프로세스

클러스터를 업데이트합니다.

```shell-session
$ oc adm upgrade --allow-explicit-upgrade --to-image <defined_registry>/<defined_repository>@<digest>
```

다음과 같습니다.

`<defined_registry>`

이미지를 미러링한 미러 레지스트리의 이름을 지정합니다.

`<defined_repository>`

미러 레지스트리에서 사용할 이미지 저장소의 이름을 지정합니다.

`<digest>`

대상 릴리스 이미지의 sha256 다이제스트(예: `sha256:81154f5c03294534e1eaf0319bef7a601134f891689ccede5d705ef659aa8c92`)를 지정합니다.

참고

미러 레지스트리 및 저장소 이름을 정의하는 방법은 "OpenShift Container Platform 이미지 미러링"을 참조하십시오.

`ImageContentSourcePolicy` 또는 `ImageDigestMirrorSet` 을 사용한 경우 정의한 이름 대신 정식 레지스트리 및 리포지토리 이름을 사용할 수 있습니다. 정식 레지스트리 이름은 `quay.io` 이고 표준 리포지토리 이름은 `openshift-release-dev/ocp-release` 입니다.

`ImageContentSourcePolicy`, `ImageDigestMirrorSet` 또는 `ImageTagMirrorSet` 오브젝트가 있는 클러스터에 대한 글로벌 풀 시크릿만 구성할 수 있습니다. 프로젝트에 풀 시크릿을 추가할 수 없습니다.

추가 리소스

OpenShift Container Platform 이미지 미러링

#### 11.4.5. 이미지 레지스트리 저장소 미러링 이해

컨테이너 레지스트리 저장소 미러링을 설정하면 다음 작업을 수행할 수 있습니다.

소스 이미지 레지스트리의 저장소에서 이미지를 가져오기 위해 요청을 리디렉션하고 미러링된 이미지 레지스트리의 저장소에서 이를 해석하도록 OpenShift Container Platform 클러스터를 설정합니다.

하나의 미러가 다운된 경우 다른 미러를 사용할 수 있도록 각 대상 저장소에 대해 여러 미러링된 저장소를 확인합니다.

OpenShift Container Platform의 저장소 미러링에는 다음 속성이 포함되어 있습니다.

이미지 풀은 레지스트리 다운타임에 탄력적으로 대처할 수 있습니다.

연결이 끊긴 환경의 클러스터는 중요한 위치(예: `quay.io`)에서 이미지를 가져오고 회사 방화벽 뒤의 레지스트리에서 요청된 이미지를 제공하도록 할 수 있습니다.

이미지 가져오기 요청이 있으면 특정한 레지스트리 순서로 가져오기를 시도하며 일반적으로 영구 레지스트리는 마지막으로 시도합니다.

입력한 미러링 정보는 OpenShift Container Platform 클러스터의 모든 노드에서 `/etc/containers/registries.conf` 파일에 추가됩니다.

노드가 소스 저장소에서 이미지를 요청하면 요청된 컨텐츠를 찾을 때 까지 미러링된 각 저장소를 차례로 시도합니다. 모든 미러가 실패하면 클러스터는 소스 저장소를 시도합니다. 성공하면 이미지를 노드로 가져올 수 있습니다.

다음과 같은 방법으로 저장소 미러링을 설정할 수 있습니다.

OpenShift Container Platform 설치 시

OpenShift Container Platform에 필요한 컨테이너 이미지를 가져온 다음 해당 이미지를 회사 방화벽 뒤에 배치하면 연결이 끊긴 환경에 있는 데이터 센터에 OpenShift Container Platform을 설치할 수 있습니다.

OpenShift Container Platform 설치 후

OpenShift Container Platform 설치 중에 미러링을 구성하지 않은 경우 다음 CR(사용자 정의 리소스) 오브젝트를 사용하여 설치 후 설치할 수 있습니다.

`ImageDigestMirrorSet` (IDMS). 이 오브젝트를 사용하면 다이제스트 사양을 사용하여 미러링된 레지스트리에서 이미지를 가져올 수 있습니다. IDMS CR을 사용하면 이미지 가져오기에 실패하는 경우 소스 레지스트리에서 지속적인 시도를 허용하거나 중지하는 fall back 정책을 설정할 수 있습니다.

`ImageTagMirrorSet` (ITMS). 이 오브젝트를 사용하면 이미지 태그를 사용하여 미러링된 레지스트리에서 이미지를 가져올 수 있습니다. ITMS CR을 사용하면 이미지 가져오기에 실패하는 경우 소스 레지스트리에서 지속적으로 시도하려는 시도를 허용하거나 중지하는 fall back 정책을 설정할 수 있습니다.

ICSP(`ImageContentSourcePolicy`). 이 오브젝트를 사용하면 다이제스트 사양을 사용하여 미러링된 레지스트리에서 이미지를 가져올 수 있습니다. 미러가 작동하지 않는 경우 ICSP CR은 항상 소스 레지스트리로 대체됩니다.

중요

ICSP(`ImageContentSourcePolicy`) 오브젝트를 사용하여 저장소 미러링을 구성하는 것은 더 이상 사용되지 않는 기능입니다. 더 이상 사용되지 않는 기능은 여전히 OpenShift Container Platform에 포함되어 있으며 계속 지원됩니다. 향후 릴리스에서 제거될 예정이므로 새 배포에는 사용하지 않는 것이 좋습니다.

`ImageContentSourcePolicy` 개체를 생성하는 데 사용한 기존 YAML 파일이 있는 경우 아래 명령을 사용하여 해당 파일을 `ImageDigestMirrorSet` YAML 파일로 변환할 수 있습니다.

```shell
oc adm migrate icsp
```

자세한 내용은 "이미지 레지스트리 저장소 미러링을 위한 ImageContentSourcePolicy (ICSP) 파일 변환"을 참조하십시오.

이러한 사용자 정의 리소스 오브젝트 각각 다음 정보를 식별합니다.

미러링하려는 컨테이너 이미지 저장소의 소스

콘텐츠를 제공하려는 각 미러 저장소에 대한 개별 항목

다음 동작 및 노드 드레이닝 동작에 어떤 영향을 미치는지에 유의하십시오.

IDMS 또는 ICSP CR 오브젝트를 생성하는 경우 MCO는 노드를 드레이닝하거나 재부팅하지 않습니다.

ITMS CR 오브젝트를 생성하면 MCO가 노드를 비우고 재부팅합니다.

ITMS, IDMS 또는 ICSP CR 오브젝트를 삭제하면 MCO가 노드를 비우고 재부팅합니다.

ITMS, IDMS 또는 ICSP CR 오브젝트를 수정하면 MCO가 노드를 비우고 재부팅합니다.

중요

MCO가 다음 변경 사항을 감지하면 노드를 드레이닝하거나 재부팅하지 않고 업데이트를 적용합니다.

머신 구성의 `spec.config.passwd.users.sshAuthorizedKeys` 매개변수에서 SSH 키 변경

`openshift-config` 네임 스페이스에서 글로벌 풀 시크릿 또는 풀 시크릿 관련 변경 사항

Kubernetes API Server Operator의 `/etc/kubernetes/kubelet-ca.crt` 인증 기관(CA) 자동 교체

MCO가 `ImageDigestMirrorSet`, `ImageTagMirrorSet` 또는 `ImageContentSourcePolicy` 개체 편집과 같은 `/etc/containers/registries.conf` 파일의 변경을 감지하면 해당 노드를 비우고 변경 사항을 적용한 다음 노드를 분리합니다. 다음 변경에는 노드 드레이닝이 발생하지 않습니다.

각 미러에 대해 설정된 `pull-from-mirror = "digest-only"` 매개변수를 사용하여 레지스트리를 추가합니다.

레지스트리에 설정된 `pull-from-mirror = "digest-only"` 매개변수를 사용하여 미러를 추가합니다.

`unqualified-search-registries` 목록에 항목이 추가되었습니다.

새 클러스터의 경우 필요에 따라 IDMS, ITMS 및 ICSP CRs 오브젝트를 사용할 수 있습니다. 그러나 IDMS 및 ITMS를 사용하는 것이 좋습니다.

클러스터를 업그레이드한 경우 기존 ICSP 오브젝트가 안정적으로 유지되며 IDMS 및 ICSP 오브젝트가 모두 지원됩니다. ICSP 오브젝트를 사용하는 워크로드는 예상대로 계속 작동합니다.

그러나 IDMS CR에 도입된 대체 정책을 활용하려면 다음 이미지 레지스트리 저장소 미러링 섹션에 대해 ICSP(Conversioning ImageContentSourcePolicy) 파일 에 표시된 대로 아래 명령을 사용하여 현재 워크로드를 IDMS 오브젝트로 마이그레이션할 수 있습니다.

```shell
oc adm migrate icsp
```

IDMS 오브젝트로 마이그레이션하려면 클러스터를 재부팅할 필요가 없습니다.

참고

클러스터에서 `ImageDigestMirrorSet`, `ImageTagMirrorSet` 또는 `ImageContentSourcePolicy` 개체를 사용하여 저장소 미러링을 구성하는 경우 미러링된 레지스트리에 대해 글로벌 풀 시크릿만 사용할 수 있습니다. 프로젝트에 풀 시크릿을 추가할 수 없습니다.

#### 11.4.5.1. 이미지 레지스트리 저장소 미러링 설정

설치 후 미러 구성 CR(사용자 정의 리소스)을 생성하여 소스 이미지 레지스트리에서 미러링된 이미지 레지스트리로 이미지 가져오기 요청을 리디렉션할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

미러링된 저장소를 설정합니다.

Red Hat Quay를 사용하여 미러링된 저장소를 설정합니다. Red Hat Quay를 사용하여 한 리포지토리에서 다른 리포지토리로 이미지를 복사하고 시간이 지남에 따라 해당 리포지토리를 반복적으로 동기화할 수도 있습니다.

Red Hat Quay Repository Mirroring

다음 명령과 같은 툴을 사용하여 소스 저장소에서 미러링된 저장소로 이미지를 수동으로 복사합니다.

```shell
skopeo
```

예를 들어 {op-system-base-full system}에 skopeo RPM 패키지를 설치한 후 다음 예와 같이 아래 명령을 사용합니다.

```shell
skopeo
```

```shell-session
$ skopeo copy --all \
docker://registry.access.redhat.com/ubi9/ubi-minimal:latest@sha256:5cf... \
docker://example.io/example/ubi-minimal
```

이 예제에는 `example.io` 라는 컨테이너 이미지 레지스트리와 `example` 이라는 이미지 리포지토리가 있습니다. `registry.access.redhat.com` 에서 `example.io` 로 `ubi9/ubi-minimal` 이미지를 복사하려고 합니다.

미러링된 레지스트리를 생성한 후 OpenShift Container Platform 클러스터를 구성하여 소스 저장소에 대한 요청을 미러링된 저장소로 리디렉션할 수 있습니다.

다음 예제 중 하나를 사용하여 설치 후 미러 구성 CR(사용자 정의 리소스)을 생성합니다.

필요에 따라 `ImageDigestMirrorSet` 또는 `ImageTagMirrorSet` CR을 생성하여 소스 및 미러를 자체 레지스트리 및 저장소 쌍과 이미지로 교체합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: ImageDigestMirrorSet
metadata:
  name: ubi9repo
spec:
  imageDigestMirrors:
  - mirrors:
    - example.io/example/ubi-minimal
    - example.com/example2/ubi-minimal
    source: registry.access.redhat.com/ubi9/ubi-minimal
    mirrorSourcePolicy: AllowContactingSource
  - mirrors:
    - mirror.example.com/redhat
    source: registry.example.com/redhat
    mirrorSourcePolicy: AllowContactingSource
  - mirrors:
    - mirror.example.com
    source: registry.example.com
    mirrorSourcePolicy: AllowContactingSource
  - mirrors:
    - mirror.example.net/image
    source: registry.example.com/example/myimage
    mirrorSourcePolicy: AllowContactingSource
  - mirrors:
    - mirror.example.net
    source: registry.example.com/example
    mirrorSourcePolicy: AllowContactingSource
  - mirrors:
    - mirror.example.net/registry-example-com
    source: registry.example.com
    mirrorSourcePolicy: AllowContactingSource
```

`ImageContentSourcePolicy` 사용자 정의 리소스를 생성하여 소스 및 미러를 고유한 레지스트리 및 저장소 쌍 및 이미지로 교체합니다.

```yaml
apiVersion: operator.openshift.io/v1alpha1
kind: ImageContentSourcePolicy
metadata:
  name: mirror-ocp
spec:
  repositoryDigestMirrors:
  - mirrors:
    - mirror.registry.com:443/ocp/release
    source: quay.io/openshift-release-dev/ocp-release
  - mirrors:
    - mirror.registry.com:443/ocp/release
    source: quay.io/openshift-release-dev/ocp-v4.0-art-dev
```

다음과 같습니다.

`- mirror.registry.com:443/ocp/release`

미러 이미지 레지스트리 및 저장소의 이름을 지정합니다.

`소스: quay.io/openshift-release-dev/ocp-release`

미러링된 콘텐츠가 포함된 온라인 레지스트리 및 저장소를 지정합니다.

다음 명령을 실행하여 새 오브젝트를 생성합니다.

```shell-session
$ oc create -f registryrepomirror.yaml
```

오브젝트가 생성되면 MCO(Machine Config Operator)는 `ImageTagMirrorSet` 오브젝트에 대해서만 노드를 드레이닝합니다. MCO는 `ImageDigestMirrorSet` 및 `ImageContentSourcePolicy` 개체에 대해 노드를 드레이닝하지 않습니다.

미러링된 구성 설정이 적용되었는지 확인하려면 노드 중 하나에서 다음을 수행하십시오.

노드를 나열합니다.

```shell-session
$ oc get node
```

```shell-session
NAME                           STATUS                     ROLES    AGE  VERSION
ip-10-0-137-44.ec2.internal    Ready                      worker   7m   v1.33.4
ip-10-0-138-148.ec2.internal   Ready                      master   11m  v1.33.4
ip-10-0-139-122.ec2.internal   Ready                      master   11m  v1.33.4
ip-10-0-147-35.ec2.internal    Ready                      worker   7m   v1.33.4
ip-10-0-153-12.ec2.internal    Ready                      worker   7m   v1.33.4
ip-10-0-154-10.ec2.internal    Ready                      master   11m  v1.33.4
```

디버깅 프로세스를 시작하고 노드에 액세스합니다.

```shell-session
$ oc debug node/ip-10-0-147-35.ec2.internal
```

```shell-session
Starting pod/ip-10-0-147-35ec2internal-debug ...
To use host binaries, run `chroot /host`
```

루트 디렉토리를 `/host` 로 변경합니다.

```shell-session
sh-4.2# chroot /host
```

`/etc/containers/registries.conf` 파일을 체크하여 변경 사항이 적용되었는지 확인합니다.

```shell-session
sh-4.2# cat /etc/containers/registries.conf
```

다음 출력은 설치 후 미러 구성 CR이 적용되는 `registries.conf` 파일을 나타냅니다.

```shell-session
unqualified-search-registries = ["registry.access.redhat.com", "docker.io"]
short-name-mode = ""

[[registry]]
  prefix = ""
  location = "registry.access.redhat.com/ubi9/ubi-minimal"

  [[registry.mirror]]
    location = "example.io/example/ubi-minimal"
    pull-from-mirror = "digest-only"

  [[registry.mirror]]
    location = "example.com/example/ubi-minimal"
    pull-from-mirror = "digest-only"

[[registry]]
  prefix = ""
  location = "registry.example.com"

  [[registry.mirror]]
    location = "mirror.example.net/registry-example-com"
    pull-from-mirror = "digest-only"

[[registry]]
  prefix = ""
  location = "registry.example.com/example"

  [[registry.mirror]]
    location = "mirror.example.net"
    pull-from-mirror = "digest-only"

[[registry]]
  prefix = ""
  location = "registry.example.com/example/myimage"

  [[registry.mirror]]
    location = "mirror.example.net/image"
    pull-from-mirror = "digest-only"

[[registry]]
  prefix = ""
  location = "registry.example.com"

  [[registry.mirror]]
    location = "mirror.example.com"
    pull-from-mirror = "digest-only"

[[registry]]
  prefix = ""
  location = "registry.example.com/redhat"

  [[registry.mirror]]
    location = "mirror.example.com/redhat"
    pull-from-mirror = "digest-only"
[[registry]]
  prefix = ""
  location = "registry.access.redhat.com/ubi9/ubi-minimal"
  blocked = true

  [[registry.mirror]]
    location = "example.io/example/ubi-minimal-tag"
    pull-from-mirror = "tag-only"
```

where: `[[registry]].location = "registry.access.redhat.com/ubi9/ubi-minimal"`:: 가져오기 사양에 나열된 리포지토리입니다. `[[registry.mirror]].location = "example.io/example/ubi-minimal"`:: 해당 저장소의 미러를 나타냅니다.

`[[registry.mirror]].pull-from-mirror = "digest-only"`:: 미러에서 이미지 가져오기는 다이제스트 참조 이미지입니다. `[[registry]].blocked = true`:: 이 리포지토리에 `NeverContactSource` 매개변수가 설정되어 있음을 나타냅니다.

`[[registry.mirror]].pull-from-mirror = "tag-only"`:: 미러에서 이미지 가져오기가 태그 참조 이미지임을 나타냅니다.

소스에서 이미지를 노드로 가져와 미러링에 의해 해결되는지 확인합니다.

```shell-session
sh-4.2# podman pull --log-level=debug registry.access.redhat.com/ubi9/ubi-minimal@sha256:5cf...
```

문제 해결

저장소 미러링 절차가 설명된 대로 작동하지 않는 경우 저장소 미러링 작동 방법에 대한 다음 정보를 사용하여 문제를 해결합니다.

가져온 이미지는 첫 번째 작동 미러를 사용하여 공급합니다.

주요 레지스트리는 다른 미러가 작동하지 않는 경우에만 사용됩니다.

시스템 컨텍스트에서 `Insecure` 플래그가 폴백으로 사용됩니다.

`/etc/containers/registries.conf` 파일 형식이 최근에 변경되었습니다. 현재 버전은 TOML 형식의 버전 2입니다.

#### 11.4.5.2. 이미지 레지스트리 저장소 미러링을 위한 ICP( ImageContentSourcePolicy) 파일 변환

ICSP(`ImageContentSourcePolicy`) 오브젝트를 사용하여 저장소 미러링을 구성하는 것은 더 이상 사용되지 않는 기능입니다.

이 기능은 여전히 OpenShift Container Platform에 포함되어 있으며 계속 지원됩니다. 그러나 이 기능은 향후 릴리스에서 제거될 예정이므로 새로운 배포에는 사용하지 않는 것이 좋습니다.

ICSP 오브젝트는 저장소 미러링을 구성하기 위해 `ImageDigestMirrorSet` 및 `ImageTagMirrorSet` 개체로 교체됩니다.

`ImageContentSourcePolicy` 개체를 생성하는 데 사용한 기존 YAML 파일이 있는 경우 아래 명령을 사용하여 해당 파일을 `ImageDigestMirrorSet` YAML 파일로 변환할 수 있습니다.

```shell
oc adm migrate icsp
```

명령은 현재 버전으로 API를 업데이트하고, `kind` 값을 `ImageDigestMirrorSet` 로 변경하고, `spec.repositoryDigestMirrors` 를 `spec.imageDigestMirrors` 로 변경합니다. 파일의 나머지 부분은 변경되지 않습니다.

마이그레이션은 `registries.conf` 파일을 변경하지 않으므로 클러스터를 재부팅할 필요가 없습니다.

`ImageDigestMirrorSet` 또는 `ImageTagMirrorSet` 오브젝트에 대한 자세한 내용은 이전 섹션의 "이미지 레지스트리 저장소 미러링 설정"을 참조하십시오.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

클러스터에 `ImageContentSourcePolicy` 개체가 있는지 확인합니다.

프로세스

다음 명령을 사용하여 하나 이상의 `ImageContentSourcePolicy` YAML 파일을 `ImageDigestMirrorSet` YAML 파일로 변환합니다.

```shell-session
$ oc adm migrate icsp <file_name>.yaml <file_name>.yaml <file_name>.yaml --dest-dir <path_to_the_directory>
```

다음과 같습니다.

`<file_name>`

소스 `ImageContentSourcePolicy` YAML의 이름을 지정합니다. 여러 파일 이름을 나열할 수 있습니다.

`--dest-dir`

선택 사항: 출력 `ImageDigestMirrorSet` YAML의 디렉터리를 지정합니다. 설정되지 않으면 파일이 현재 디렉터리에 기록됩니다.

예를 들어 다음 명령은 `icsp.yaml` 및 `icsp-2.yaml` 파일을 변환하고 새 YAML 파일을 `idms-files` 디렉터리에 저장합니다.

```shell-session
$ oc adm migrate icsp icsp.yaml icsp-2.yaml --dest-dir idms-files
```

```shell-session
wrote ImageDigestMirrorSet to idms-files/imagedigestmirrorset_ubi8repo.5911620242173376087.yaml
wrote ImageDigestMirrorSet to idms-files/imagedigestmirrorset_ubi9repo.6456931852378115011.yaml
```

다음 명령을 실행하여 CR 오브젝트를 생성합니다.

```shell-session
$ oc create -f <path_to_the_directory>/<file-name>.yaml
```

다음과 같습니다.

`<path_to_the_directory>`

`--dest-dir` 플래그를 사용한 경우 디렉터리의 경로를 지정합니다.

`<file_name>`

`ImageDigestMirrorSet` YAML의 이름을 지정합니다.

IDMS 오브젝트가 롤아웃된 후 ICSP 오브젝트를 제거합니다.

#### 11.4.6. 클러스터 노드 재부팅 빈도를 줄이기 위해 미러 이미지 카탈로그의 범위 확장

미러링된 이미지 카탈로그의 범위를 저장소 수준 또는 더 넓은 레지스트리 수준에서 지정할 수 있습니다. 광범위한 `ImageContentSourcePolicy` 리소스는 리소스 변경에 따라 노드를 재부팅해야 하는 횟수를 줄입니다.

`ImageContentSourcePolicy` 리소스에서 미러 이미지 카탈로그의 범위를 확장하려면 다음 절차를 수행합니다.

사전 요구 사항

OpenShift Container Platform CLI 다음 명령을 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

연결이 끊긴 클러스터에서 사용할 미러링된 이미지 카탈로그를 구성합니다.

프로세스

`<local_registry>`, `<pull_spec>`, 및 `<pull_secret_file>` 에 대한 값을 지정하여 다음 명령을 실행합니다.

```shell-session
$ oc adm catalog mirror <local_registry>/<pull_spec> <local_registry> -a <pull_secret_file> --icsp-scope=registry
```

다음과 같습니다.

<local_registry>

연결이 끊긴 클러스터에 대해 구성한 로컬 레지스트리입니다 (예: `local.registry:5000`).

<pull_spec>

연결이 끊긴 레지스트리에 구성된 풀 사양입니다(예: `redhat/redhat-operator-index:v4.20`).

<pull_secret_file>

`.json` 파일 형식의 `registry.redhat.io` 풀 시크릿입니다. Red Hat OpenShift Cluster Manager에서 풀 시크릿을 다운로드할 수 있습니다.

아래 명령은 `/redhat-operator-index-manifests` 디렉터리를 생성하고 `imageContentSourcePolicy.yaml`, `catalogSource.yaml` 및 `mapping.txt` 파일을 생성합니다.

```shell
oc adm catalog mirror
```

새 `ImageContentSourcePolicy` 리소스를 클러스터에 적용합니다.

```shell-session
$ oc apply -f imageContentSourcePolicy.yaml
```

검증

다음 명령가 `ImageContentSourcePolicy` 에 변경 사항을 성공적으로 적용했는지 확인합니다.

```shell
oc apply
```

```shell-session
$ oc get ImageContentSourcePolicy -o yaml
```

```yaml
apiVersion: v1
items:
- apiVersion: operator.openshift.io/v1alpha1
  kind: ImageContentSourcePolicy
  metadata:
    annotations:
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"operator.openshift.io/v1alpha1","kind":"ImageContentSourcePolicy","metadata":{"annotations":{},"name":"redhat-operator-index"},"spec":{"repositoryDigestMirrors":[{"mirrors":["local.registry:5000"],"source":"registry.redhat.io"}]}}
...
```

`ImageContentSourcePolicy` 리소스를 업데이트한 후 OpenShift Container Platform은 새 설정을 각 노드에 배포하고 클러스터는 소스 저장소에 대한 요청에 미러링된 저장소를 사용하기 시작합니다.

#### 11.4.7. 추가 리소스

연결이 끊긴 환경에서 Operator Lifecycle Manager 사용

머신 구성 개요

### 11.5. 클러스터에서 OpenShift Update Service 설치 제거

클러스터에서 OSUS(OpenShift Update Service)의 로컬 사본을 제거하려면 먼저 OSUS 애플리케이션을 삭제한 다음 OSUS Operator를 제거해야 합니다.

#### 11.5.1. OpenShift Update Service 애플리케이션 삭제

OpenShift Container Platform 웹 콘솔 또는 CLI를 사용하여 OpenShift Update Service 애플리케이션을 삭제할 수 있습니다.

#### 11.5.1.1. 웹 콘솔을 사용하여 OpenShift Update Service 애플리케이션 삭제

OpenShift Container Platform 웹 콘솔을 사용하여 OpenShift Update Service Operator로 OpenShift Update Service 애플리케이션을 삭제할 수 있습니다.

사전 요구 사항

OpenShift Update Service Operator가 설치되었습니다.

프로세스

웹 콘솔에서 에코시스템 → 설치된 Operator

를 클릭합니다.

설치된 Operator 목록에서 OpenShift Update Service 를 선택합니다.

Update Service 탭을 클릭합니다.

설치된 OpenShift Update Service 애플리케이션 목록에서 삭제할 애플리케이션을 선택한 다음 Delete UpdateService 를 클릭합니다.

Delete UpdateService? 확인 프롬프트에서 Delete 를 클릭하여 삭제를 확인합니다.

#### 11.5.1.2. CLI를 사용하여 OpenShift Update Service 애플리케이션 삭제

OpenShift CLI()를 사용하여 OpenShift Update Service 애플리케이션을 삭제할 수 있습니다.

```shell
oc
```

프로세스

OpenShift Update Service 애플리케이션이 생성된 네임스페이스(예: `openshift-update-service`)를 사용하여 OpenShift Update Service 애플리케이션 이름을 가져옵니다.

```shell-session
$ oc get updateservice -n openshift-update-service
```

```shell-session
NAME      AGE
service   6s
```

이전 단계의 `NAME` 값과 OpenShift Update Service 애플리케이션이 생성된 네임스페이스(예: `openshift-update-service`)를 사용하여 OpenShift Update Service 애플리케이션을 삭제합니다.

```shell-session
$ oc delete updateservice service -n openshift-update-service
```

```shell-session
updateservice.updateservice.operator.openshift.io "service" deleted
```

#### 11.5.2. OpenShift Update Service Operator 설치 제거

OpenShift Container Platform 웹 콘솔 또는 CLI를 사용하여 OpenShift Update Service Operator를 설치 제거할 수 있습니다.

#### 11.5.2.1. 웹 콘솔을 사용하여 OpenShift Update Service Operator 설치 제거

OpenShift Container Platform 웹 콘솔을 사용하여 OpenShift Update Service Operator를 설치 제거할 수 있습니다.

사전 요구 사항

모든 OpenShift Update Service 애플리케이션이 삭제되어 있어야 합니다.

프로세스

웹 콘솔에서 에코시스템 → 설치된 Operator

를 클릭합니다.

설치된 Operator 목록에서 OpenShift Update Service 을 선택하고 Uninstall Operator 를 클릭합니다.

Uninstall Operator? 확인 대화 상자에서 Uninstall 를 클릭하고 제거를 확인합니다.

#### 11.5.2.2. CLI를 사용하여 OpenShift Update Service Operator 설치 제거

OpenShift CLI()를 사용하여 OpenShift Update Service Operator를 제거할 수 있습니다.

```shell
oc
```

사전 요구 사항

모든 OpenShift Update Service 애플리케이션이 삭제되어 있어야 합니다.

프로세스

OpenShift Update Service Operator가 포함된 프로젝트로 변경합니다(예: `openshift-update-service`).

```shell-session
$ oc project openshift-update-service
```

```shell-session
Now using project "openshift-update-service" on server "https://example.com:6443".
```

OpenShift Update Service Operator Operator 그룹의 이름을 가져옵니다.

```shell-session
$ oc get operatorgroup
```

```shell-session
NAME                             AGE
openshift-update-service-fprx2   4m41s
```

operator 그룹을 삭제합니다(예: `openshift-update-service-fprx2`).

```shell-session
$ oc delete operatorgroup openshift-update-service-fprx2
```

```shell-session
operatorgroup.operators.coreos.com "openshift-update-service-fprx2" deleted
```

OpenShift Update Service Operator 서브스크립션의 이름을 가져옵니다.

```shell-session
$ oc get subscription
```

```shell-session
NAME                      PACKAGE                   SOURCE                        CHANNEL
update-service-operator   update-service-operator   updateservice-index-catalog   v1
```

이전 단계의 `Name` 값을 사용하여 `currentCSV` 필드에서 구독한 OpenShift Update Service Operator의 현재 버전을 확인합니다.

```shell-session
$ oc get subscription update-service-operator -o yaml | grep " currentCSV"
```

```shell-session
currentCSV: update-service-operator.v0.0.1
```

서브스크립션을 삭제합니다(예: `update-service-operator`).

```shell-session
$ oc delete subscription update-service-operator
```

```shell-session
subscription.operators.coreos.com "update-service-operator" deleted
```

이전 단계의 `currentCSV` 값을 사용하여 OpenShift Update Service Operator의 CSV를 삭제합니다.

```shell-session
$ oc delete clusterserviceversion update-service-operator.v0.0.1
```

```shell-session
clusterserviceversion.operators.coreos.com "update-service-operator.v0.0.1" deleted
```
