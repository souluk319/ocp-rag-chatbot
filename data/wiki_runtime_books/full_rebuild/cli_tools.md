# CLI 툴

## OpenShift Container Platform 명령줄 툴 사용 방법 알아보기

이 문서는 OpenShift Container Platform 명령줄 툴 설치, 구성 및 사용에 대해 자세히 설명합니다. CLI 명령에 대한 참조와 사용 방법에 대한 예도 포함되어 있습니다.

## 1장. OpenShift Container Platform CLI 툴 개요

사용자는 다음과 같은 OpenShift Container Platform에서 작업하는 동안 다양한 작업을 수행합니다.

클러스터 관리

애플리케이션 빌드, 배포 및 관리

배포 프로세스 관리

Operator 카탈로그 생성 및 유지 관리

OpenShift Container Platform은 사용자가 터미널에서 다양한 관리 및 개발 작업을 수행할 수 있도록 하여 이러한 작업을 단순화하는 CLI(명령줄 인터페이스) 툴 세트를 제공합니다. 이러한 툴은 간단한 명령을 사용하여 애플리케이션을 관리하고 시스템의 각 구성 요소와 상호 작용합니다.

### 1.1. CLI 툴 목록

OpenShift Container Platform에서 다음 CLI 툴 세트를 사용할 수 있습니다.

OpenShift CLI(): OpenShift Container Platform 사용자가 가장 일반적으로 사용하는 CLI 툴입니다. 클러스터 관리자와 개발자가 터미널을 사용하여 OpenShift Container Platform에서 엔드 투 엔드 작업을 수행할 수 있도록 지원합니다. 웹 콘솔과 달리 사용자는 명령 스크립트를 사용하여 프로젝트 소스 코드로 직접 작업할 수 있습니다.

```shell
oc
```

Knative CLI(kn): Knative(`kn`) CLI 툴은 Knative Serving 및 Eventing과 같은 OpenShift Serverless 구성 요소와 상호 작용하는 데 사용할 수 있는 단순하고 직관적인 터미널 명령을 제공합니다.

Pipeline CLI(tkn): OpenShift Pipelines는 내부적으로 Tekton을 사용하는 OpenShift Container Platform의 CI/CD(지속적 통합 및 연속 제공) 솔루션입니다. `tkn` CLI 툴은 터미널을 사용하여 OpenShift Pipelines와 상호 작용할 수 있는 간단하고 직관적인 명령을 제공합니다.

opm CLI: `opm` CLI 툴을 사용하면 Operator 개발자와 클러스터 관리자가 터미널에서 Operator 카탈로그를 생성하고 유지 관리할 수 있습니다.

#### 2.1.1. OpenShift CLI 정보

OpenShift CLI ()를 사용하면 터미널에서 애플리케이션을 생성하고 OpenShift Container Platform 프로젝트를 관리할 수 있습니다. OpenShift CLI를 사용하기에 적합한 경우는 다음과 같습니다.

```shell
oc
```

프로젝트 소스 코드로 직접 작업.

OpenShift Container Platform 작업 스크립트를 작성하는 경우

대역폭 리소스로 제한되고 웹 콘솔을 사용할 수 없는 동안 프로젝트를 관리할 수 없습니다.

#### 2.1.2. OpenShift CLI 설치

OpenShift CLI()는 바이너리를 다운로드하거나 RPM을 사용하여 설치할 수 있습니다.

```shell
oc
```

#### 2.1.2.1. OpenShift CLI 설치

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

#### 2.1.2.1.1. Linux에서 OpenShift CLI 설치

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

#### 2.1.2.1.2. Windows에서 OpenSfhit CLI 설치

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

#### 2.1.2.1.3. macOS에 OpenShift CLI 설치

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

#### 2.1.2.2. 웹 콘솔을 사용하여 OpenShift CLI 설치

웹 콘솔에서 OpenShift Container Platform 클러스터와 상호 작용하기 위해 CLI(OpenShift CLI)를 설치할 수 있습니다. Linux, Windows 또는 macOS에 다음 명령을 설치할 수 있습니다.

```shell
oc
```

```shell
oc
```

중요

이전 버전의 다음 명령을 설치한 경우 OpenShift Container Platform 4.20의 모든 명령을 완료하는 데 해당 버전을 사용할 수 없습니다. 새 버전의 다음 명령을 다운로드하여 설치합니다.

```shell
oc
```

```shell
oc
```

#### 2.1.2.2.1. 웹 콘솔을 사용하여 Linux에 OpenShift CLI 설치

[FIGURE src="/playbooks/wiki-assets/full_rebuild/cli_tools/click-question-mark.png" alt="물음표를 클릭합니다." kind="figure" diagram_type="image_figure"]
물음표를 클릭합니다.
[/FIGURE]

_Source: `cli_tools.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-CLI_tools-ko-KR/images/f0c1646f62eeee179a9093cf3d794ab3/click-question-mark.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/cli_tools/CLI-list.png" alt="CLI 목록" kind="figure" diagram_type="image_figure"]
CLI 목록
[/FIGURE]

_Source: `cli_tools.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-CLI_tools-ko-KR/images/af5ebcca8d086078c0ea2821b491e9b3/CLI-list.png`_


다음 절차를 사용하여 Linux에서 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

웹 콘솔에서? 를 클릭합니다.

명령줄 툴 을 클릭합니다.

Linux 플랫폼에 적합한 바이너리를 선택한 다음 Linux용 oc 용으로 다운로드를 클릭합니다.

```shell
oc
```

파일을 저장합니다.

아카이브의 압축을 풉니다.

```shell-session
$ tar xvf <file>
```

다음 명령바이너리를 `PATH` 에 있는 디렉터리로 이동합니다.

```shell
oc
```

`PATH` 를 확인하려면 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

OpenShift CLI를 설치한 후 아래 명령을 사용할 수 있습니다.

```shell
oc
```

```shell-session
$ oc <command>
```

#### 2.1.2.2.2. 웹 콘솔을 사용하여 Windows에 OpenShift CLI 설치

다음 절차에 따라 Windows에 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

웹 콘솔에서? 를 클릭합니다.

명령줄 툴 을 클릭합니다.

다음 명령바이너리 for Windows 플랫폼을 선택한 다음 Download oc for Windows for x86_64 를 클릭합니다.

```shell
oc
```

파일을 저장합니다.

ZIP 프로그램으로 아카이브의 압축을 풉니다.

다음 명령바이너리를 `PATH` 에 있는 디렉터리로 이동합니다.

```shell
oc
```

`PATH` 를 확인하려면 명령 프롬프트를 열고 다음 명령을 실행합니다.

```shell-session
C:\> path
```

OpenShift CLI를 설치한 후 아래 명령을 사용할 수 있습니다.

```shell
oc
```

```shell-session
C:\> oc <command>
```

#### 2.1.2.2.3. 웹 콘솔을 사용하여 macOS에 OpenShift CLI 설치

다음 절차에 따라 macOS에서 OpenShift CLI() 바이너리를 설치할 수 있습니다.

```shell
oc
```

프로세스

웹 콘솔에서? 를 클릭합니다.

명령줄 툴 을 클릭합니다.

macOS 플랫폼용 바이너리를 선택한 다음 x86_64용 oc for Mac 다운로드를 클릭합니다.

```shell
oc
```

참고

macOS arm64의 경우 Mac용 oc for ARM 64 다운로드를 클릭합니다.

파일을 저장합니다.

아카이브의 압축을 해제하고 압축을 풉니다.

다음 명령바이너리 PATH의 디렉터리로 이동합니다.

```shell
oc
```

`PATH` 를 확인하려면 터미널을 열고 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

OpenShift CLI를 설치한 후 아래 명령을 사용할 수 있습니다.

```shell
oc
```

```shell-session
$ oc <command>
```

#### 2.1.2.3. RPM을 사용하여 OpenShift CLI 설치

RHEL(Red Hat Enterprise Linux)의 경우 Red Hat 계정에 활성 OpenShift Container Platform 서브스크립션이 있는 경우 OpenShift CLI()를 RPM으로 설치할 수 있습니다.

```shell
oc
```

중요

바이너리를 다운로드하여 RHEL 9용 다음 명령을 설치해야 합니다. RPM 패키지를 사용하여 다음 명령을 설치하는 것은 RHEL(Red Hat Enterprise Linux) 9에서 지원되지 않습니다.

```shell
oc
```

```shell
oc
```

사전 요구 사항

root 또는 sudo 권한이 있어야 합니다.

프로세스

Red Hat Subscription Manager에 등록합니다.

```shell-session
# subscription-manager register
```

최신 서브스크립션 데이터를 가져옵니다.

```shell-session
# subscription-manager refresh
```

사용 가능한 서브스크립션을 나열하십시오.

```shell-session
# subscription-manager list --available --matches '*OpenShift*'
```

이전 명령의 출력에서 OpenShift Container Platform 서브스크립션의 풀 ID를 찾아서 이 서브스크립션을 등록된 시스템에 연결합니다.

```shell-session
# subscription-manager attach --pool=<pool_id>
```

OpenShift Container Platform 4.20에 필요한 리포지토리를 활성화합니다.

```shell-session
# subscription-manager repos --enable="rhocp-4.20-for-rhel-8-x86_64-rpms"
```

`openshift-clients` 패키지를 설치합니다.

```shell-session
# yum install openshift-clients
```

검증

아래 명령을 사용하여 설치를 확인합니다.

```shell
oc
```

```shell-session
$ oc <command>
```

#### 2.1.2.4. Homebrew를 사용하여 OpenShift CLI 설치

macOS의 경우 Homebrew 패키지 관리자를 사용하여 OpenShift CLI()를 설치할 수 있습니다.

```shell
oc
```

사전 요구 사항

Homebrew(`brew`)가 설치되어 있어야 합니다.

프로세스

다음 명령을 실행하여 openshift-cli 패키지를 설치합니다.

```shell-session
$ brew install openshift-cli
```

검증

아래 명령을 사용하여 설치를 확인합니다.

```shell
oc
```

```shell-session
$ oc <command>
```

#### 2.1.3. OpenShift CLI에 로그인

OpenShift CLI () 에 로그인하면 클러스터에 액세스하여 관리할 수 있습니다.

```shell
oc
```

사전 요구 사항

OpenShift Container Platform 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있어야 합니다.

```shell
oc
```

참고

HTTP 프록시 서버를 통해서만 액세스할 수 있는 클러스터에 액세스하려면 `HTTP_PROXY`, `HTTPS_PROXY` 및 `NO_PROXY` 변수를 설정할 수 있습니다. CLI에서는 이러한 환경 변수를 준수하므로 클러스터와의 모든 통신이 HTTP 프록시를 통해 이루어집니다.

```shell
oc
```

인증 헤더는 HTTPS 전송을 사용하는 경우에만 전송됩니다.

프로세스

아래 명령을 입력하고 사용자 이름을 전달합니다.

```shell
oc login
```

```shell-session
$ oc login -u user1
```

프롬프트가 표시되면 필요한 정보를 입력합니다.

```shell-session
Server [https://localhost:8443]: https://openshift.example.com:6443
The server uses a certificate signed by an unknown authority.
You can bypass the certificate check, but any data you send to the server could be intercepted by others.
Use insecure connections? (y/n): y
Authentication required for https://openshift.example.com:6443 (openshift)
Username: user1
Password:
Login successful.

You don't have any projects. You can try to create a new project, by running

    oc new-project <projectname>

Welcome! See 'oc help' to get started.
```

1. OpenShift Container Platform 서버 URL을 입력합니다.

2. 비보안 연결 사용 여부를 입력합니다.

3. 사용자 암호를 입력합니다.

참고

웹 콘솔에 로그인한 경우 토큰 및 서버 정보를 포함하는 아래 명령을 생성할 수 있습니다. 명령을 사용하여 대화형 프롬프트 없이 (OpenShift CLI)에 로그인할 수 있습니다. 명령을 생성하려면 웹 콘솔의 오른쪽 상단에 있는 사용자 이름 드롭다운 메뉴에서 로그인 복사 명령 을 선택합니다.

```shell
oc login
```

```shell
oc
```

이제 클러스터를 관리하기 위한 프로젝트를 생성하거나 다른 명령을 실행할 수 있습니다.

#### 2.1.4. 웹 브라우저를 사용하여 OpenShift CLI에 로그인

웹 브라우저의 도움말을 사용하여 OpenShift CLI()에 로그인하여 클러스터에 액세스하고 관리할 수 있습니다. 이를 통해 사용자는 액세스 토큰을 명령줄에 삽입하지 않을 수 있습니다.

```shell
oc
```

주의

웹 브라우저를 통해 CLI에 로그인하면 HTTPS가 아닌 localhost에서 서버를 실행합니다. 다중 사용자 워크스테이션에서 주의해서 사용합니다.

사전 요구 사항

OpenShift Container Platform 클러스터에 대한 액세스 권한이 있어야 합니다.

OpenShift CLI()가 설치되어 있어야 합니다.

```shell
oc
```

브라우저가 설치되어 있어야 합니다.

프로세스

`--web` 플래그를 사용하여 아래 명령을 입력합니다.

```shell
oc login
```

```shell-session
$ oc login <cluster_url> --web
```

1. 선택적으로 서버 URL 및 콜백 포트를 지정할 수 있습니다. 예:.

```shell
oc login <cluster_url> --web --callback-port 8280 localhost:8443
```

웹 브라우저가 자동으로 열립니다. 그렇지 않은 경우 명령 출력의 링크를 클릭합니다. OpenShift Container Platform 서버를 지정하지 않으면 는 현재 구성 파일에 지정된 클러스터의 웹 콘솔을 엽니다. 구성이 없는 경우 다음 명령에서 서버 URL을 대화형으로 입력하라는 메시지를 표시합니다.

```shell
oc
```

```shell
oc
```

```shell
oc
```

```shell
oc
```

```shell-session
Opening login URL in the default browser: https://openshift.example.com
Opening in existing browser session.
```

둘 이상의 ID 공급자를 사용할 수 있는 경우 제공된 옵션에서 선택한 항목을 선택합니다.

해당 브라우저 필드에 사용자 이름과 암호를 입력합니다. 로그인한 후 브라우저에 `access token received successfully; please return to your terminal` 라는 텍스트가 표시됩니다.

CLI에서 로그인 확인을 확인합니다.

```shell-session
Login successful.

You don't have any projects. You can try to create a new project, by running

    oc new-project <projectname>
```

참고

웹 콘솔은 기본적으로 이전 세션에서 사용된 프로필로 설정됩니다. 관리자와 개발자 프로필 간에 전환하려면 OpenShift Container Platform 웹 콘솔에서 로그아웃하고 캐시를 지웁니다.

이제 클러스터를 관리하기 위한 프로젝트를 생성하거나 다른 명령을 실행할 수 있습니다.

#### 2.1.5. OpenShift CLI 사용

다음 섹션을 검토하여 CLI로 일반적인 작업을 완료하는 방법을 알아봅니다.

#### 2.1.5.1. 프로젝트 생성

아래 명령을 사용하여 새 프로젝트를 생성합니다.

```shell
oc new-project
```

```shell-session
$ oc new-project my-project
```

```shell-session
Now using project "my-project" on server "https://openshift.example.com:6443".
```

#### 2.1.5.2. 새 애플리케이션 생성

아래 명령을 사용하여 새 애플리케이션을 생성합니다.

```shell
oc new-app
```

```shell-session
$ oc new-app https://github.com/sclorg/cakephp-ex
```

```shell-session
--> Found image 40de956 (9 days old) in imagestream "openshift/php" under tag "7.2" for "php"

...

    Run 'oc status' to view your app.
```

#### 2.1.5.3. Pod 보기

아래 명령을 사용하여 현재 프로젝트의 Pod를 봅니다.

```shell
oc get pods
```

참고

Pod 내부에서 다음 명령을 실행하고 네임스페이스를 지정하지 않으면 기본적으로 Pod의 네임스페이스가 사용됩니다.

```shell
oc
```

```shell-session
$ oc get pods -o wide
```

```shell-session
NAME                  READY   STATUS      RESTARTS   AGE     IP            NODE                           NOMINATED NODE
cakephp-ex-1-build    0/1     Completed   0          5m45s   10.131.0.10   ip-10-0-141-74.ec2.internal    <none>
cakephp-ex-1-deploy   0/1     Completed   0          3m44s   10.129.2.9    ip-10-0-147-65.ec2.internal    <none>
cakephp-ex-1-ktz97    1/1     Running     0          3m33s   10.128.2.11   ip-10-0-168-105.ec2.internal   <none>
```

#### 2.1.5.4. Pod 로그 보기

아래 명령을 사용하여 특정 Pod의 로그를 봅니다.

```shell
oc logs
```

```shell-session
$ oc logs cakephp-ex-1-deploy
```

```shell-session
--> Scaling cakephp-ex-1 to 1
--> Success
```

#### 2.1.5.5. 현재 프로젝트 보기

아래 명령을 사용하여 현재 프로젝트를 봅니다.

```shell
oc project
```

```shell-session
$ oc project
```

```shell-session
Using project "my-project" on server "https://openshift.example.com:6443".
```

#### 2.1.5.6. 현재 프로젝트의 상태 보기

아래 명령을 사용하여 서비스, 배포, 빌드 구성 등 현재 프로젝트에 대한 정보를 봅니다.

```shell
oc status
```

```shell-session
$ oc status
```

```shell-session
In project my-project on server https://openshift.example.com:6443

svc/cakephp-ex - 172.30.236.80 ports 8080, 8443
  dc/cakephp-ex deploys istag/cakephp-ex:latest <-
    bc/cakephp-ex source builds https://github.com/sclorg/cakephp-ex on openshift/php:7.2
    deployment #1 deployed 2 minutes ago - 1 pod

3 infos identified, use 'oc status --suggest' to see details.
```

#### 2.1.5.7. 지원되는 API 리소스 나열

아래 명령을 사용하여 서버에서 지원되는 API 리소스 목록을 봅니다.

```shell
oc api-resources
```

```shell-session
$ oc api-resources
```

```shell-session
NAME                                  SHORTNAMES       APIGROUP                              NAMESPACED   KIND
bindings                                                                                     true         Binding
componentstatuses                     cs                                                     false        ComponentStatus
configmaps                            cm                                                     true         ConfigMap
...
```

#### 2.1.6. 도움말 가져오기

다음과 같은 방법으로 CLI 명령 및 OpenShift Container Platform 리소스에 대한 도움말을 얻을 수 있습니다.

다음 명령을 사용하여 모든 사용 가능한 CLI 명령 목록 및 설명을 가져옵니다.

```shell
oc help
```

```shell-session
$ oc help
```

```shell-session
OpenShift Client

This client helps you develop, build, deploy, and run your applications on any OpenShift or Kubernetes compatible
platform. It also includes the administrative commands for managing a cluster under the 'adm' subcommand.

Usage:
  oc [flags]

Basic Commands:
  login           Log in to a server
  new-project     Request a new project
  new-app         Create a new application

...
```

`--help` 플래그를 사용하여 특정 CLI 명령에 대한 도움말을 가져옵니다.

```shell
oc create
```

```shell-session
$ oc create --help
```

```shell-session
Create a resource by filename or stdin

JSON and YAML formats are accepted.

Usage:
  oc create -f FILENAME [flags]

...
```

아래 명령을 사용하여 특정 리소스에 대한 설명 및 필드를 봅니다.

```shell
oc explain
```

```shell-session
$ oc explain pods
```

```shell-session
KIND:     Pod
VERSION:  v1

DESCRIPTION:
     Pod is a collection of containers that can run on a host. This resource is
     created by clients and scheduled onto hosts.

FIELDS:
   apiVersion   <string>
     APIVersion defines the versioned schema of this representation of an
     object. Servers should convert recognized schemas to the latest internal
     value, and may reject unrecognized values. More info:
     https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

...
```

#### 2.1.7. OpenShift CLI에서 로그아웃

OpenShift CLI에서 로그아웃하여 현재 세션을 종료할 수 있습니다.

아래 명령을 사용합니다.

```shell
oc logout
```

```shell-session
$ oc logout
```

```shell-session
Logged "user1" out on "https://openshift.example.com"
```

이렇게 하면 저장된 인증 토큰이 서버에서 삭제되고 구성 파일에서 제거됩니다.

#### 2.2.1. 탭 완료 활성화

Bash 또는 Zsh 쉘에 탭 완료를 활성화할 수 있습니다.

#### 2.2.1.1. Bash 탭 완료 활성화

OpenShift CLI()를 설치한 후 탭 완료를 활성화하여 자동으로 아래 명령을 완료하거나 탭을 누를 때 옵션을 제안할 수 있습니다. Bash 쉘에 대한 탭 완료를 활성화하는 절차는 다음과 같습니다.

```shell
oc
```

```shell
oc
```

사전 요구 사항

OpenShift CLI()가 설치되어 있어야 합니다.

```shell
oc
```

`bash-completion` 패키지가 설치되어 있어야 합니다.

프로세스

Bash 완료 코드를 파일에 저장합니다.

```shell-session
$ oc completion bash > oc_bash_completion
```

파일을 `/etc/bash_completion.d/` 에 복사합니다.

```shell-session
$ sudo cp oc_bash_completion /etc/bash_completion.d/
```

파일을 로컬 디렉터리에 저장하고 `.bashrc` 파일에서 소싱할 수도 있습니다.

새 터미널을 열면 탭 완료가 활성화됩니다.

#### 2.2.1.2. Zsh 탭 완료 활성화

OpenShift CLI()를 설치한 후 탭 완료를 활성화하여 자동으로 아래 명령을 완료하거나 탭을 누를 때 옵션을 제안할 수 있습니다. 다음 절차에서는 Zsh 쉘에 대한 탭 완료를 활성화합니다.

```shell
oc
```

```shell
oc
```

사전 요구 사항

OpenShift CLI()가 설치되어 있어야 합니다.

```shell
oc
```

프로세스

다음 명령의 탭 완료를 `.zshrc` 파일에 추가하려면 다음 명령을 실행합니다.

```shell
oc
```

```shell-session
$ cat >>~/.zshrc<<EOF
autoload -Uz compinit
compinit
if [ $commands[oc] ]; then
  source <(oc completion zsh)
  compdef _oc oc
fi
EOF
```

새 터미널을 열면 탭 완료가 활성화됩니다.

#### 2.2.2. oc CLI를 사용하여 kubeconfig에 액세스

다음 명령CLI를 사용하여 OpenShift 클러스터에 로그인하고 명령줄에서 클러스터에 액세스하기 위해 kubeconfig 파일을 검색할 수 있습니다.

```shell
oc
```

사전 요구 사항

OpenShift Container Platform 웹 콘솔 또는 API 서버 끝점에 액세스할 수 있습니다.

프로세스

다음 명령을 실행하여 OpenShift 클러스터에 로그인합니다.

```shell-session
$ oc login <api-server-url> -u <username> -p <password>
```

1. 전체 API 서버 URL을 지정합니다. 예: `https://api.my-cluster.example.com:6443`.

2. 유효한 사용자 이름을 지정합니다. 예: `kubeadmin`.

3. 지정된 사용자의 암호를 입력합니다. 예를 들어 클러스터 설치 중에 생성된 `kubeadmin` 암호입니다.

다음 명령을 실행하여 클러스터 구성을 로컬 파일에 저장합니다.

```shell-session
$ oc config view --raw > kubeconfig
```

다음 명령을 실행하여 내보낸 파일을 가리키도록 `KUBECONFIG` 환경 변수를 설정합니다.

```shell-session
$ export KUBECONFIG=./kubeconfig
```

다음 명령을 실행하여 OpenShift 클러스터와 상호 작용하려면 다음 명령을 사용합니다.

```shell
oc
```

```shell-session
$ oc get nodes
```

참고

세션 또는 시스템에서 내보낸 `kubeconfig` 파일을 재사용하려면 안전하게 저장하고 소스 제어에 커밋하지 마십시오.

### 2.3. oc 및 kubectl 명령 사용

Kubernetes CLI(명령줄 인터페이스), 은 Kubernetes 클러스터에 대해 명령을 실행하는 데 사용할 수 있습니다. OpenShift Container Platform은 인증된 Kubernetes 배포판이므로 OpenShift Container Platform과 함께 제공된 지원되는 바이너리를 사용할 수도 있고 바이너리를 사용하여 확장 기능을 받을 수도 있습니다.

```shell
kubectl
```

```shell
kubectl
```

```shell
oc
```

#### 2.3.1. oc 바이너리

[FIGURE src="/playbooks/wiki-assets/full_rebuild/cli_tools/redcircle-1.png" alt="redcircle 1" kind="figure" diagram_type="image_figure"]
redcircle 1
[/FIGURE]

_Source: `cli_tools.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-CLI_tools-ko-KR/images/e6e80b7e9c4b03038c3528b5a02c6c87/redcircle-1.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/cli_tools/redcircle-3.png" alt="redcircle 3" kind="figure" diagram_type="image_figure"]
redcircle 3
[/FIGURE]

_Source: `cli_tools.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-CLI_tools-ko-KR/images/303956f5d0c12798adfa653218555f12/redcircle-3.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/cli_tools/redcircle-2.png" alt="redcircle 2" kind="figure" diagram_type="image_figure"]
redcircle 2
[/FIGURE]

_Source: `cli_tools.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-CLI_tools-ko-KR/images/fe0c835a883b665da7d112e7e6d32d8c/redcircle-2.png`_


다음 명령바이너리는 바이너리와 동일한 기능을 제공하지만 다음을 비롯하여 추가 OpenShift Container Platform 기능을 지원하도록 기본적으로 확장됩니다.

```shell
oc
```

```shell
kubectl
```

OpenShift Container Platform 리소스 전체 지원

`DeploymentConfig`, `BuildConfig`, `Route`, `ImageStream` 및 `ImageStreamTag` 오브젝트와 같은 리소스는 OpenShift Container Platform 배포판에 고유하며 표준 Kubernetes 프리미티브에 빌드됩니다.

인증

다음 명령바이너리는 인증을 위해 기본 제공 `로그인` 명령을 제공하며 Kubernetes 네임스페이스를 인증된 사용자에게 매핑하는 프로젝트 작업을 수행할 수 있습니다. 자세한 내용은 인증 이해 를 참조하십시오.

```shell
oc
```

추가 명령

예를 들어 추가 명령 다음 명령을 사용하면 기존 소스 코드 또는 미리 빌드된 이미지를 사용하여 새 애플리케이션을 보다 쉽게 시작할 수 있습니다. 마찬가지로, 추가 명령 다음 명령을 사용하면 기본값으로 전환할 수 있는 프로젝트를 보다 쉽게 시작할 수 있습니다.

```shell
oc new-app
```

```shell
oc new-project
```

중요

이전 버전의 바이너리를 설치한 경우 OpenShift Container Platform 4.20의 모든 명령을 완료하는 데 사용할 수 없습니다. 최신 기능을 사용하려면 OpenShift Container Platform 서버 버전에 해당하는 최신 버전의 바이너리를 다운로드하여 설치해야 합니다.

```shell
oc
```

```shell
oc
```

비보안 API 변경에는 이전 바이너리를 업데이트할 수 있도록 최소 두 개의 마이너 릴리스(예: 4.2에서 4.3으로)가 포함됩니다. 새 기능을 사용하려면 최신 바이너리가 필요할 수 있습니다. 4.3 서버에는 4.2 바이너리가 사용할 수 없는 추가 기능이 있을 수 있으며 4.3 바이너리에는 4.2 서버에서 지원되지 않는 추가 기능이 있을 수 있습니다.

```shell
oc
```

```shell
oc
```

```shell
oc
```

```shell
oc
```

| XY ( `oc` 클라이언트) | X.Y+N footnote:versionpolicyn[여기서 N 은 1보다 크거나 같은 숫자입니다. ( `oc` Client) |
| --- | --- |
| X.Y (서버) |  |  |
| X.Y+N footnote:versionpolicyn[](Server) |  |  |

완전하게 호환됩니다.

다음 명령클라이언트에서 서버 기능에 액세스하지 못할 수 있습니다.

```shell
oc
```

다음 명령클라이언트에서 액세스한 서버와 호환되지 않는 옵션 및 기능을 제공할 수 있습니다.

```shell
oc
```

#### 2.3.2. kubectl 바이너리

다음 명령바이너리는 표준 Kubernetes 환경의 새로운 OpenShift Container Platform 사용자 또는 CLI 사용을 선호하는 사용자를 위해 기존 워크플로우 및 스크립트를 지원하는 수단으로 제공됩니다. 의 기존 사용자는 OpenShift Container Platform 클러스터를 변경할 필요 없이 이 바이너리를 사용하여 Kubernetes 프리미티브와 계속 상호 작용할 수 있습니다.

```shell
kubectl
```

```shell
kubectl
```

```shell
kubectl
```

OpenShift CLI 설치 단계에 따라 지원되는 바이너리를 설치할 수 있습니다. 바이너리는 바이너리를 다운로드한 경우 아카이브에 포함되어 있습니다. RPM을 사용하여 CLI를 설치할 때 이 바이너리가 설치됩니다.

```shell
kubectl
```

```shell
kubectl
```

자세한 내용은 kubectl 문서 를 참조하십시오.

### 2.4. CLI 프로필 관리

CLI 구성 파일을 사용하면 CLI 툴 개요 와 함께 사용할 수 있도록 다양한 프로필 또는 컨텍스트를 구성할 수 있습니다. 컨텍스트는 닉네임 과 연결된 OpenShift Container Platform 서버 정보로 구성됩니다. https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/authentication_and_authorization/#understanding-authentication

#### 2.4.1. CLI 프로필 간 전환 정보

컨텍스트를 사용하면 CLI 작업을 사용할 때 여러 OpenShift Container Platform 서버 또는 클러스터에서 여러 사용자 간에 쉽게 전환할 수 있습니다. 닉네임을 사용하면 컨텍스트, 사용자 자격 증명 및 클러스터 세부 정보에 대한 간단한 참조를 제공하여 CLI 구성을 보다 쉽게 관리할 수 있습니다. 사용자가 CLI로 처음 로그인한 후 OpenShift Container Platform은 아직 존재하지 않는 경우 `~/.kube/config` 파일을 생성합니다. 작업 중에 자동으로 또는 CLI 프로필을 수동으로 구성하여 CLI에 인증 및 연결 세부 정보가 제공되면 업데이트된 정보는 구성 파일에 저장됩니다.

```shell
oc
```

```shell
oc login
```

```yaml
apiVersion: v1
clusters:
- cluster:
    insecure-skip-tls-verify: true
    server: https://openshift1.example.com:8443
  name: openshift1.example.com:8443
- cluster:
    insecure-skip-tls-verify: true
    server: https://openshift2.example.com:8443
  name: openshift2.example.com:8443
contexts:
- context:
    cluster: openshift1.example.com:8443
    namespace: alice-project
    user: alice/openshift1.example.com:8443
  name: alice-project/openshift1.example.com:8443/alice
- context:
    cluster: openshift1.example.com:8443
    namespace: joe-project
    user: alice/openshift1.example.com:8443
  name: joe-project/openshift1/alice
current-context: joe-project/openshift1.example.com:8443/alice
kind: Config
preferences: {}
users:
- name: alice/openshift1.example.com:8443
  user:
    token: xZHd2piv5_9vQrg-SKXRJ2Dsl9SceNJdhNTljEKTb8k
```

1. `clusters` 섹션에서는 마스터 서버의 주소를 포함하여 OpenShift Container Platform 클러스터에 대한 연결 세부 정보를 정의합니다. 이 예에서 한 클러스터는 닉네임이 `openshift1.example.com:8443` 이고 다른 클러스터는 닉네임이 `openshift2.example.com:8443` 입니다.

2. 이 `contexts` 섹션은 두 개의 컨텍스트를 정의합니다. 하나는 `alice-project` 프로젝트, `openshift1.example.com:8443` 클러스터 및 `alice` 사용자를 사용하여 별명이 `alice-project/openshift1.example.com:8443/alice` 이고, 다른 하나는 `joe-project` 프로젝트, `openshift1.example.com:8443` 클러스터 및 `alice` 사용자를 사용하여 별명이 `joe-project/openshift1.example.com:8443/alice` 입니다.

3. `current-context` 매개변수는 `joe-project/openshift1.example.com:8443/alice` 컨텍스트가 현재 사용 중임을 표시하므로 `alice` 사용자가 `openshift1.example.com:8443` 클러스터의 `joe-project` 프로젝트에서 작업할 수 있습니다.

4. `users` 섹션에서는 사용자 자격 증명을 정의합니다. 이 예에서 사용자 nickname `alice/openshift1.example.com:8443` 은 액세스 토큰을 사용합니다.

CLI는 런타임 시 로드되고 명령줄에서 지정된 재정의 옵션과 함께 병합되는 여러 구성 파일을 지원할 수 있습니다. 로그인한 후 또는 아래 명령을 사용하여 현재 작업 환경을 확인할 수 있습니다.

```shell
oc status
```

```shell
oc project
```

```shell-session
$ oc status
```

```shell-session
oc status
In project Joe's Project (joe-project)

service database (172.30.43.12:5434 -> 3306)
  database deploys docker.io/openshift/mysql-55-centos7:latest
    #1 deployed 25 minutes ago - 1 pod

service frontend (172.30.159.137:5432 -> 8080)
  frontend deploys origin-ruby-sample:latest <-
    builds https://github.com/openshift/ruby-hello-world with joe-project/ruby-20-centos7:latest
    #1 deployed 22 minutes ago - 2 pods

To see more information about a service or deployment, use 'oc describe service <name>' or 'oc describe dc <name>'.
You can use 'oc get all' to see lists of each of the types described in this example.
```

현재 프로젝트를 나열합니다.

```shell-session
$ oc project
```

```shell-session
Using project "joe-project" from context named "joe-project/openshift1.example.com:8443/alice" on server "https://openshift1.example.com:8443".
```

아래 명령을 다시 실행하고 대화형 프로세스 중에 필요한 정보를 제공하여 사용자 인증 정보 및 클러스터 세부 정보를 다른 조합으로 로그인할 수 있습니다. 컨텍스트는 아직 존재하지 않는 경우 제공된 정보를 기반으로 구성됩니다. 이미 로그인한 후 현재 사용자가 이미 액세스할 수 있는 다른 프로젝트로 전환하려면 아래 명령을 사용하여 프로젝트 이름을 입력합니다.

```shell
oc login
```

```shell
oc project
```

```shell-session
$ oc project alice-project
```

```shell-session
Now using project "alice-project" on server "https://openshift1.example.com:8443".
```

언제든지 아래 명령을 사용하여 출력에 표시된 대로 현재 CLI 구성을 볼 수 있습니다. 고급 사용을 위해 추가 CLI 구성 명령도 사용할 수 있습니다.

```shell
oc config view
```

참고

관리자 자격 증명에 액세스할 수 있지만 기본 시스템 사용자 `system:admin` 으로 더 이상 로그인하지 않은 경우 CLI 구성 파일에 인증 정보가 계속 존재하는 한 언제든지 이 사용자로 다시 로그인할 수 있습니다. 다음 명령은 로그인하고 기본 프로젝트로 전환합니다.

```shell-session
$ oc login -u system:admin -n default
```

#### 2.4.2. CLI 프로필 수동 구성

참고

이 섹션에서는 CLI 구성의 고급 사용에 대해 설명합니다. 대부분의 경우 및 아래 명령을 사용하여 로그인하고 컨텍스트와 프로젝트 간에 전환할 수 있습니다.

```shell
oc login
```

```shell
oc project
```

CLI 구성 파일을 수동으로 구성하려면 파일을 직접 수정하는 대신 아래 명령을 사용할 수 있습니다. 아래 명령에는 다음과 같은 목적으로 여러 유용한 하위 명령이 포함되어 있습니다.

```shell
oc config
```

```shell
oc config
```

| 하위 명령 | 사용법 |
| --- | --- |
| `set-cluster` | CLI 구성 파일에 클러스터 항목을 설정합니다. 참조된 클러스터 닉네임이 이미 존재하는 경우 지정된 정보가 병합됩니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] $ oc config set-cluster <cluster_nickname> [--server=<master_ip_or_fqdn>] [--certificate-authority=<path/to/certificate/authority>] [--api-version=<apiversion>] [--insecure-skip-tls-verify=true] [/CODE] |
| `set-context` | CLI 구성 파일에서 컨텍스트 항목을 설정합니다. 참조된 컨텍스트 닉네임이 이미 존재하는 경우 지정된 정보가 병합됩니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] $ oc config set-context <context_nickname> [--cluster=<cluster_nickname>] [--user=<user_nickname>] [--namespace=<namespace>] [/CODE] |
| `use-context` | 지정된 컨텍스트 닉네임을 사용하여 현재 컨텍스트를 설정합니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] $ oc config use-context <context_nickname> [/CODE] |
| `set` | CLI 구성 파일에서 개별 값을 설정합니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] $ oc config set <property_name> <property_value> [/CODE] `<property_name>` 은 각 토큰이 특성 이름 또는 맵 키를 나타내는 점으로 구분된 이름입니다. `<property_value>` 는 설정되는 새 값입니다. |
| `unset` | CLI 구성 파일에서 개별 값을 설정 해제합니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] $ oc config unset <property_name> [/CODE] `<property_name>` 은 각 토큰이 특성 이름 또는 맵 키를 나타내는 점으로 구분된 이름입니다. |
| `view` | 현재 사용 중인 병합된 CLI 구성을 표시합니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] $ oc config view [/CODE] 지정된 CLI 구성 파일의 결과를 표시합니다. [CODE language="shell-session" wrap_hint="true" overflow_hint="toggle"] $ oc config view --config=<specific_filename> [/CODE] |

사용 예

액세스 토큰을 사용하는 사용자로 로그인합니다. 이 토큰은 `alice` 사용자가 사용합니다.

```shell-session
$ oc login https://openshift1.example.com --token=ns7yVhuRNpDM9cgzfhhxQ7bM5s7N2ZVrkZepSRf4LC0
```

생성된 클러스터 항목을 자동으로 확인합니다.

```shell-session
$ oc config view
```

```shell-session
apiVersion: v1
clusters:
- cluster:
    insecure-skip-tls-verify: true
    server: https://openshift1.example.com
  name: openshift1-example-com
contexts:
- context:
    cluster: openshift1-example-com
    namespace: default
    user: alice/openshift1-example-com
  name: default/openshift1-example-com/alice
current-context: default/openshift1-example-com/alice
kind: Config
preferences: {}
users:
- name: alice/openshift1.example.com
  user:
    token: ns7yVhuRNpDM9cgzfhhxQ7bM5s7N2ZVrkZepSRf4LC0
```

사용자가 원하는 네임스페이스에 로그인하도록 현재 컨텍스트를 업데이트합니다.

```shell-session
$ oc config set-context `oc config current-context` --namespace=<project_name>
```

현재 컨텍스트를 검사하여 변경 사항이 구현되었는지 확인합니다.

```shell-session
$ oc whoami -c
```

이후의 모든 CLI 작업에서는 CLI 옵션을 덮어쓰거나 컨텍스트가 전환될 때까지 달리 지정하지 않는 한 새 컨텍스트를 사용합니다.

#### 2.4.3. 로드 및 병합 규칙

CLI 구성의 로드 및 병합 순서를 위한 CLI 작업을 실행할 때 다음 규칙을 따를 수 있습니다.

CLI 구성 파일은 다음 계층 및 병합 규칙을 사용하여 워크스테이션에서 검색됩니다.

`--config` 옵션이 설정된 경우 해당 파일만 로드됩니다. 플래그는 한 번만 설정되며 병합이 발생하지 않습니다.

`$KUBECONFIG` 환경 변수가 설정된 경우 사용됩니다. 변수는 경로 목록일 수 있으므로 경로가 병합될 수 있습니다. 값이 수정되면 스탠자를 정의하는 파일에서 수정됩니다. 값이 생성되면 첫 번째 파일이 존재하는 파일에 생성됩니다. 체인에 있는 파일이 없으면 목록에 마지막 파일이 생성됩니다.

그렇지 않으면 `~/.kube/config` 파일이 사용되고 병합이 수행되지 않습니다.

사용할 컨텍스트는 다음 흐름의 첫 번째 일치 항목에 따라 결정됩니다.

`--context` 옵션의 값입니다.

CLI 구성 파일의 `current-context` 값입니다.

이 단계에서 빈 값이 허용됩니다.

사용할 사용자 및 클러스터가 결정됩니다. 이 시점에서 컨텍스트가 있거나 없을 수 있습니다. 이러한 컨텍스트는 사용자 및 클러스터에 대해 한 번 실행되는 다음 흐름의 첫 번째 일치 항목에 따라 빌드됩니다.

사용자 이름용 `--user` 및 클러스터 이름에 대한 `--cluster` 옵션의 값입니다.

`--context` 옵션이 있는 경우 컨텍스트의 값을 사용합니다.

이 단계에서 빈 값이 허용됩니다.

사용할 실제 클러스터 정보가 결정됩니다. 이 시점에서 클러스터 정보가 있거나 없을 수 있습니다. 클러스터 정보의 각 조각은 다음 흐름의 첫 번째 일치 항목을 기반으로 빌드됩니다.

다음 명령줄 옵션 중 하나의 값입니다.

`--server`,

`--api-version`

`--certificate-authority`

`--insecure-skip-tls-verify`

클러스터 정보와 속성 값이 있는 경우 해당 정보를 사용합니다.

서버 위치가 없는 경우 오류가 발생합니다.

실제 사용할 사용자 정보가 결정됩니다. 사용자는 사용자당 하나의 인증 기술만 가질 수 있다는 점을 제외하고 클러스터와 동일한 규칙을 사용하여 빌드됩니다. 충돌하는 기술로 인해 작업이 실패합니다. 명령줄 옵션이 구성 파일 값보다 우선합니다. 유효한 명령줄 옵션은 다음과 같습니다.

`--auth-path`

`--client-certificate`

`--client-key`

`--token`

아직 누락된 정보에 대해 기본값이 사용되고 추가 정보에 대한 프롬프트가 제공됩니다.

### 2.5. 플러그인을 사용하여 OpenShift CLI 확장

기본 아래 명령에 빌드할 플러그인을 작성하고 설치하여 OpenShift Container Platform CLI에서 새롭고 더 복잡한 작업을 수행할 수 있습니다.

```shell
oc
```

#### 2.5.1. CLI 플러그인 작성

명령줄 명령을 작성할 수 있는 모든 프로그래밍 언어 또는 스크립트로 OpenShift Container Platform CLI용 플러그인을 작성할 수 있습니다. 플러그인을 사용하여 기존 아래 명령을 덮어쓸 수 없습니다.

```shell
oc
```

프로세스

이 절차에서는 아래 명령을 실행할 때 메시지를 터미널에 출력하는 간단한 Bash 플러그인을 생성합니다.

```shell
oc foo
```

다음 명령라는 파일을 생성합니다.

```shell
oc-foo
```

플러그인 파일의 이름을 지정할 때 다음 사항에 유의하십시오.

파일이 플러그인으로 인식되려면 다음 명령으로 시작되어야 합니다.

```shell
oc-
```

```shell
kubectl-
```

파일 이름에 따라 플러그인을 호출하는 명령이 결정됩니다. 예를 들어 파일 이름이 인 플러그인은 아래 명령으로 호출할 수 있습니다. 명령에 대시를 포함하기 위해 밑줄을 사용할 수도 있습니다. 예를 들어 파일 이름이 인 플러그인은 아래 명령으로 호출할 수 있습니다.

```shell
oc-foo-bar
```

```shell
oc foo bar
```

```shell
oc-foo_bar
```

```shell
oc foo-bar
```

파일에 다음 콘텐츠를 추가합니다.

```bash
#!/bin/bash

# optional argument handling
if [[ "$1" == "version" ]]
then
    echo "1.0.0"
    exit 0
fi

# optional argument handling
if [[ "$1" == "config" ]]
then
    echo $KUBECONFIG
    exit 0
fi

echo "I am a plugin named kubectl-foo"
```

OpenShift Container Platform CLI용으로 이 플러그인을 설치한 후에는 아래 명령을 사용하여 호출할 수 있습니다.

```shell
oc foo
```

추가 리소스

Go에서 작성된 플러그인의 예를 보려면 샘플 플러그인 리포지토리 를 검토합니다.

Go에서 플러그인을 작성하는 데 도움이 되는 유틸리티 세트는 CLI 런타임 리포지터리 를 검토하십시오.

#### 2.5.2. CLI 플러그인 설치 및 사용

OpenShift Container Platform CLI에 대한 사용자 정의 플러그인을 작성한 후 사용하기 전에 플러그인을 설치해야 합니다.

사전 요구 사항

다음 명령CLI 툴이 설치되어 있어야 합니다.

```shell
oc
```

다음 명령또는 다음 명령으로 시작하는 CLI 플러그인 파일이 있어야 합니다.

```shell
oc-
```

```shell
kubectl-
```

프로세스

필요한 경우 플러그인 파일을 실행 가능하게 업데이트합니다.

```shell-session
$ chmod +x <plugin_file>
```

파일을 `PATH` 에 있는 임의의 위치(예: `/usr/local/bin/`)에 배치합니다.

```shell-session
$ sudo mv <plugin_file> /usr/local/bin/.
```

다음 명령을 실행하여 플러그인이 나열되었는지 확인합니다.

```shell
oc plugin list
```

```shell-session
$ oc plugin list
```

```shell-session
The following compatible plugins are available:

/usr/local/bin/<plugin_file>
```

여기에 플러그인이 나열되지 않은 경우 파일이 다음 명령으로 시작하고 실행 가능하며 `PATH` 에 있는지 확인합니다.

```shell
oc-
```

```shell
kubectl-
```

플러그인에서 도입한 새 명령 또는 옵션을 호출합니다.

예를 들어 샘플 플러그인 리포지토리 에서 플러그인을 빌드하고 설치한 경우 다음 명령을 사용하여 현재 네임스페이스를 볼 수 있습니다.

```shell
kubectl-ns
```

```shell-session
$ oc ns
```

플러그인을 호출하는 명령은 플러그인 파일 이름에 따라 다릅니다. 예를 들어 파일 이름이 인 플러그인은 아래 명령으로 호출합니다.

```shell
oc-foo-bar
```

```shell
oc foo bar
```

### 2.6. OpenShift CLI 개발자 명령 참조

이 참조는 OpenShift CLI () developer 명령에 대한 설명 및 예제 명령을 제공합니다. 관리자 명령의 경우 OpenShift CLI 관리자 명령 참조 를 참조하십시오.

```shell
oc
```

다음 명령을 실행하여 모든 명령을 나열하거나 다음 명령을 실행하여 특정 명령에 대한 추가 세부 정보를 가져옵니다.

```shell
oc help
```

```shell
oc <command> --help
```

#### 2.6.1.1. oc annotate

리소스에서 주석을 업데이트

```bash
# Update pod 'foo' with the annotation 'description' and the value 'my frontend'
  # If the same annotation is set multiple times, only the last value will be applied
  oc annotate pods foo description='my frontend'

  # Update a pod identified by type and name in "pod.json"
  oc annotate -f pod.json description='my frontend'

  # Update pod 'foo' with the annotation 'description' and the value 'my frontend running nginx', overwriting any existing value
  oc annotate --overwrite pods foo description='my frontend running nginx'

  # Update all pods in the namespace
  oc annotate pods --all description='my frontend running nginx'

  # Update pod 'foo' only if the resource is unchanged from version 1
  oc annotate pods foo description='my frontend running nginx' --resource-version=1

  # Update pod 'foo' by removing an annotation named 'description' if it exists
  # Does not require the --overwrite flag
  oc annotate pods foo description-
```

#### 2.6.1.2. oc api-resources

서버에서 지원되는 API 리소스를 인쇄

```bash
# Print the supported API resources
  oc api-resources

  # Print the supported API resources with more information
  oc api-resources -o wide

  # Print the supported API resources sorted by a column
  oc api-resources --sort-by=name

  # Print the supported namespaced resources
  oc api-resources --namespaced=true

  # Print the supported non-namespaced resources
  oc api-resources --namespaced=false

  # Print the supported API resources with a specific APIGroup
  oc api-resources --api-group=rbac.authorization.k8s.io
```

#### 2.6.1.3. oc api-versions

"group/version" 형식으로 서버에서 지원되는 API 버전을 인쇄

```bash
# Print the supported API versions
  oc api-versions
```

#### 2.6.1.4. oc apply

파일 이름 또는 stdin으로 리소스에 구성 적용

```bash
# Apply the configuration in pod.json to a pod
  oc apply -f ./pod.json

  # Apply resources from a directory containing kustomization.yaml - e.g. dir/kustomization.yaml
  oc apply -k dir/

  # Apply the JSON passed into stdin to a pod
  cat pod.json | oc apply -f -

  # Apply the configuration from all files that end with '.json'
  oc apply -f '*.json'

  # Note: --prune is still in Alpha
  # Apply the configuration in manifest.yaml that matches label app=nginx and delete all other resources that are not in the file and match label app=nginx
  oc apply --prune -f manifest.yaml -l app=nginx

  # Apply the configuration in manifest.yaml and delete all the other config maps that are not in the file
  oc apply --prune -f manifest.yaml --all --prune-allowlist=core/v1/ConfigMap
```

#### 2.6.1.5. oc apply edit-last-applied

리소스/오브젝트의 최신 last-applied-configuration 주석을 편집

```bash
# Edit the last-applied-configuration annotations by type/name in YAML
  oc apply edit-last-applied deployment/nginx

  # Edit the last-applied-configuration annotations by file in JSON
  oc apply edit-last-applied -f deploy.yaml -o json
```

#### 2.6.1.6. oc apply set-last-applied

파일의 내용과 일치하도록 라이브 오브젝트에 last-applied-configuration 주석을 설정

```bash
# Set the last-applied-configuration of a resource to match the contents of a file
  oc apply set-last-applied -f deploy.yaml

  # Execute set-last-applied against each configuration file in a directory
  oc apply set-last-applied -f path/

  # Set the last-applied-configuration of a resource to match the contents of a file; will create the annotation if it does not already exist
  oc apply set-last-applied -f deploy.yaml --create-annotation=true
```

#### 2.6.1.7. oc apply view-last-applied

리소스/오브젝트의 최신 last-applied-configuration 주석을 표시

```bash
# View the last-applied-configuration annotations by type/name in YAML
  oc apply view-last-applied deployment/nginx

  # View the last-applied-configuration annotations by file in JSON
  oc apply view-last-applied -f deploy.yaml -o json
```

#### 2.6.1.8. oc attach

실행 중인 컨테이너에 연결

```bash
# Get output from running pod mypod; use the 'oc.kubernetes.io/default-container' annotation
  # for selecting the container to be attached or the first container in the pod will be chosen
  oc attach mypod

  # Get output from ruby-container from pod mypod
  oc attach mypod -c ruby-container

  # Switch to raw terminal mode; sends stdin to 'bash' in ruby-container from pod mypod
  # and sends stdout/stderr from 'bash' back to the client
  oc attach mypod -c ruby-container -i -t

  # Get output from the first pod of a replica set named nginx
  oc attach rs/nginx
```

#### 2.6.1.9. oc auth can-i

작업이 허용되는지 확인

```bash
# Check to see if I can create pods in any namespace
  oc auth can-i create pods --all-namespaces

  # Check to see if I can list deployments in my current namespace
  oc auth can-i list deployments.apps

  # Check to see if service account "foo" of namespace "dev" can list pods in the namespace "prod"
  # You must be allowed to use impersonation for the global option "--as"
  oc auth can-i list pods --as=system:serviceaccount:dev:foo -n prod

  # Check to see if I can do everything in my current namespace ("*" means all)
  oc auth can-i '*' '*'

  # Check to see if I can get the job named "bar" in namespace "foo"
  oc auth can-i list jobs.batch/bar -n foo

  # Check to see if I can read pod logs
  oc auth can-i get pods --subresource=log

  # Check to see if I can access the URL /logs/
  oc auth can-i get /logs/

  # Check to see if I can approve certificates.k8s.io
  oc auth can-i approve certificates.k8s.io

  # List all allowed actions in namespace "foo"
  oc auth can-i --list --namespace=foo
```

#### 2.6.1.10. oc auth reconcile

RBAC 역할, 역할 바인딩, 클러스터 역할 및 클러스터 역할 바인딩 오브젝트에 대한 규칙 조정

```bash
# Reconcile RBAC resources from a file
  oc auth reconcile -f my-rbac-rules.yaml
```

#### 2.6.1.11. oc auth whoami

실험: 자체 주제 속성 확인

```bash
# Get your subject attributes
  oc auth whoami

  # Get your subject attributes in JSON format
  oc auth whoami -o json
```

#### 2.6.1.12. oc autoscale

배포 구성, 배포, 복제본 세트, 상태 저장 세트 또는 복제 컨트롤러를 자동 스케일링

```bash
# Auto scale a deployment "foo", with the number of pods between 2 and 10, no target CPU utilization specified so a default autoscaling policy will be used
  oc autoscale deployment foo --min=2 --max=10

  # Auto scale a replication controller "foo", with the number of pods between 1 and 5, target CPU utilization at 80%
  oc autoscale rc foo --max=5 --cpu-percent=80
```

#### 2.6.1.13. oc cancel-build

실행 중이거나 보류 중인 빌드 또는 새 빌드를 취소

```bash
# Cancel the build with the given name
  oc cancel-build ruby-build-2

  # Cancel the named build and print the build logs
  oc cancel-build ruby-build-2 --dump-logs

  # Cancel the named build and create a new one with the same parameters
  oc cancel-build ruby-build-2 --restart

  # Cancel multiple builds
  oc cancel-build ruby-build-1 ruby-build-2 ruby-build-3

  # Cancel all builds created from the 'ruby-build' build config that are in the 'new' state
  oc cancel-build bc/ruby-build --state=new
```

#### 2.6.1.14. oc cluster-info

클러스터 정보 표시

```bash
# Print the address of the control plane and cluster services
  oc cluster-info
```

#### 2.6.1.15. oc cluster-info dump

디버깅 및 진단을 위한 관련 정보 덤프

```bash
# Dump current cluster state to stdout
  oc cluster-info dump

  # Dump current cluster state to /path/to/cluster-state
  oc cluster-info dump --output-directory=/path/to/cluster-state

  # Dump all namespaces to stdout
  oc cluster-info dump --all-namespaces

  # Dump a set of namespaces to /path/to/cluster-state
  oc cluster-info dump --namespaces default,kube-system --output-directory=/path/to/cluster-state
```

#### 2.6.1.16. oc completion

지정된 쉘에 대한 쉘 완료 코드 출력(bash, zsh, fish 또는 powershell)

```bash
# Installing bash completion on macOS using homebrew
  ## If running Bash 3.2 included with macOS
  brew install bash-completion
  ## or, if running Bash 4.1+
  brew install bash-completion@2
  ## If oc is installed via homebrew, this should start working immediately
  ## If you've installed via other means, you may need add the completion to your completion directory
  oc completion bash > $(brew --prefix)/etc/bash_completion.d/oc


  # Installing bash completion on Linux
  ## If bash-completion is not installed on Linux, install the 'bash-completion' package
  ## via your distribution's package manager.
  ## Load the oc completion code for bash into the current shell
  source <(oc completion bash)
  ## Write bash completion code to a file and source it from .bash_profile
  oc completion bash > ~/.kube/completion.bash.inc
  printf "
  # oc shell completion
  source '$HOME/.kube/completion.bash.inc'
  " >> $HOME/.bash_profile
  source $HOME/.bash_profile

  # Load the oc completion code for zsh[1] into the current shell
  source <(oc completion zsh)
  # Set the oc completion code for zsh[1] to autoload on startup
  oc completion zsh > "${fpath[1]}/_oc"


  # Load the oc completion code for fish[2] into the current shell
  oc completion fish | source
  # To load completions for each session, execute once:
  oc completion fish > ~/.config/fish/completions/oc.fish

  # Load the oc completion code for powershell into the current shell
  oc completion powershell | Out-String | Invoke-Expression
  # Set oc completion code for powershell to run on startup
  ## Save completion code to a script and execute in the profile
  oc completion powershell > $HOME\.kube\completion.ps1
  Add-Content $PROFILE "$HOME\.kube\completion.ps1"
  ## Execute completion code in the profile
  Add-Content $PROFILE "if (Get-Command oc -ErrorAction SilentlyContinue) {
  oc completion powershell | Out-String | Invoke-Expression
  }"
  ## Add completion code directly to the $PROFILE script
  oc completion powershell >> $PROFILE
```

#### 2.6.1.17. oc config current-context

current-context 표시

```bash
# Display the current-context
  oc config current-context
```

#### 2.6.1.18. oc config delete-cluster

kubeconfig에서 지정된 클러스터를 삭제

```bash
# Delete the minikube cluster
  oc config delete-cluster minikube
```

#### 2.6.1.19. oc config delete-context

kubeconfig에서 지정된 컨텍스트를 삭제

```bash
# Delete the context for the minikube cluster
  oc config delete-context minikube
```

#### 2.6.1.20. oc config delete-user

kubeconfig에서 지정된 사용자를 삭제

```bash
# Delete the minikube user
  oc config delete-user minikube
```

#### 2.6.1.21. oc config get-clusters

kubeconfig에 정의된 클러스터를 표시

```bash
# List the clusters that oc knows about
  oc config get-clusters
```

#### 2.6.1.22. oc config get-contexts

하나 또는 여러 컨텍스트를 설명

```bash
# List all the contexts in your kubeconfig file
  oc config get-contexts

  # Describe one context in your kubeconfig file
  oc config get-contexts my-context
```

#### 2.6.1.23. oc config get-users

kubeconfig에 정의된 사용자를 표시

```bash
# List the users that oc knows about
  oc config get-users
```

#### 2.6.1.24. oc config new-admin-kubeconfig

서버를 생성하고, 신뢰하고, 새 admin.kubeconfig를 표시합니다.

```bash
# Generate a new admin kubeconfig
  oc config new-admin-kubeconfig
```

#### 2.6.1.25. oc config new-kubelet-bootstrap-kubeconfig

서버를 생성하고, 신뢰하고, 새 kubelet /etc/kubernetes/kubeconfig를 표시합니다.

```bash
# Generate a new kubelet bootstrap kubeconfig
  oc config new-kubelet-bootstrap-kubeconfig
```

#### 2.6.1.26. oc config refresh-ca-bundle

API 서버에 연결하여 OpenShift CA 번들 업데이트

```bash
# Refresh the CA bundle for the current context's cluster
  oc config refresh-ca-bundle

  # Refresh the CA bundle for the cluster named e2e in your kubeconfig
  oc config refresh-ca-bundle e2e

  # Print the CA bundle from the current OpenShift cluster's API server
  oc config refresh-ca-bundle --dry-run
```

#### 2.6.1.27. oc config rename-context

kubeconfig 파일에서 컨텍스트의 이름 변경

```bash
# Rename the context 'old-name' to 'new-name' in your kubeconfig file
  oc config rename-context old-name new-name
```

#### 2.6.1.28. oc config set

kubeconfig 파일에서 개별 값 설정

```bash
# Set the server field on the my-cluster cluster to https://1.2.3.4
  oc config set clusters.my-cluster.server https://1.2.3.4

  # Set the certificate-authority-data field on the my-cluster cluster
  oc config set clusters.my-cluster.certificate-authority-data $(echo "cert_data_here" | base64 -i -)

  # Set the cluster field in the my-context context to my-cluster
  oc config set contexts.my-context.cluster my-cluster

  # Set the client-key-data field in the cluster-admin user using --set-raw-bytes option
  oc config set users.cluster-admin.client-key-data cert_data_here --set-raw-bytes=true
```

#### 2.6.1.29. oc config set-cluster

kubeconfig에서 클러스터 항목 설정

```bash
# Set only the server field on the e2e cluster entry without touching other values
  oc config set-cluster e2e --server=https://1.2.3.4

  # Embed certificate authority data for the e2e cluster entry
  oc config set-cluster e2e --embed-certs --certificate-authority=~/.kube/e2e/kubernetes.ca.crt

  # Disable cert checking for the e2e cluster entry
  oc config set-cluster e2e --insecure-skip-tls-verify=true

  # Set the custom TLS server name to use for validation for the e2e cluster entry
  oc config set-cluster e2e --tls-server-name=my-cluster-name

  # Set the proxy URL for the e2e cluster entry
  oc config set-cluster e2e --proxy-url=https://1.2.3.4
```

#### 2.6.1.30. oc config set-context

kubeconfig에서 컨텍스트 항목 설정

```bash
# Set the user field on the gce context entry without touching other values
  oc config set-context gce --user=cluster-admin
```

#### 2.6.1.31. oc config set-credentials

kubeconfig에서 사용자 항목 설정

```bash
# Set only the "client-key" field on the "cluster-admin"
  # entry, without touching other values
  oc config set-credentials cluster-admin --client-key=~/.kube/admin.key

  # Set basic auth for the "cluster-admin" entry
  oc config set-credentials cluster-admin --username=admin --password=uXFGweU9l35qcif

  # Embed client certificate data in the "cluster-admin" entry
  oc config set-credentials cluster-admin --client-certificate=~/.kube/admin.crt --embed-certs=true

  # Enable the Google Compute Platform auth provider for the "cluster-admin" entry
  oc config set-credentials cluster-admin --auth-provider=gcp

  # Enable the OpenID Connect auth provider for the "cluster-admin" entry with additional arguments
  oc config set-credentials cluster-admin --auth-provider=oidc --auth-provider-arg=client-id=foo --auth-provider-arg=client-secret=bar

  # Remove the "client-secret" config value for the OpenID Connect auth provider for the "cluster-admin" entry
  oc config set-credentials cluster-admin --auth-provider=oidc --auth-provider-arg=client-secret-

  # Enable new exec auth plugin for the "cluster-admin" entry
  oc config set-credentials cluster-admin --exec-command=/path/to/the/executable --exec-api-version=client.authentication.k8s.io/v1beta1

  # Enable new exec auth plugin for the "cluster-admin" entry with interactive mode
  oc config set-credentials cluster-admin --exec-command=/path/to/the/executable --exec-api-version=client.authentication.k8s.io/v1beta1 --exec-interactive-mode=Never

  # Define new exec auth plugin arguments for the "cluster-admin" entry
  oc config set-credentials cluster-admin --exec-arg=arg1 --exec-arg=arg2

  # Create or update exec auth plugin environment variables for the "cluster-admin" entry
  oc config set-credentials cluster-admin --exec-env=key1=val1 --exec-env=key2=val2

  # Remove exec auth plugin environment variables for the "cluster-admin" entry
  oc config set-credentials cluster-admin --exec-env=var-to-remove-
```

#### 2.6.1.32. oc config unset

kubeconfig 파일에서 개별 값 설정 해제

```bash
# Unset the current-context
  oc config unset current-context

  # Unset namespace in foo context
  oc config unset contexts.foo.namespace
```

#### 2.6.1.33. oc config use-context

kubeconfig 파일에서 current-context 설정

```bash
# Use the context for the minikube cluster
  oc config use-context minikube
```

#### 2.6.1.34. oc config view

병합된 kubeconfig 설정 또는 지정된 kubeconfig 파일을 표시

```bash
# Show merged kubeconfig settings
  oc config view

  # Show merged kubeconfig settings, raw certificate data, and exposed secrets
  oc config view --raw

  # Get the password for the e2e user
  oc config view -o jsonpath='{.users[?(@.name == "e2e")].user.password}'
```

#### 2.6.1.35. oc cp

컨테이너 간에 파일 및 디렉터리를 복사

```bash
# !!!Important Note!!!
  # Requires that the 'tar' binary is present in your container
  # image.  If 'tar' is not present, 'oc cp' will fail.
  #
  # For advanced use cases, such as symlinks, wildcard expansion or
  # file mode preservation, consider using 'oc exec'.

  # Copy /tmp/foo local file to /tmp/bar in a remote pod in namespace <some-namespace>
  tar cf - /tmp/foo | oc exec -i -n <some-namespace> <some-pod> -- tar xf - -C /tmp/bar

  # Copy /tmp/foo from a remote pod to /tmp/bar locally
  oc exec -n <some-namespace> <some-pod> -- tar cf - /tmp/foo | tar xf - -C /tmp/bar

  # Copy /tmp/foo_dir local directory to /tmp/bar_dir in a remote pod in the default namespace
  oc cp /tmp/foo_dir <some-pod>:/tmp/bar_dir

  # Copy /tmp/foo local file to /tmp/bar in a remote pod in a specific container
  oc cp /tmp/foo <some-pod>:/tmp/bar -c <specific-container>

  # Copy /tmp/foo local file to /tmp/bar in a remote pod in namespace <some-namespace>
  oc cp /tmp/foo <some-namespace>/<some-pod>:/tmp/bar

  # Copy /tmp/foo from a remote pod to /tmp/bar locally
  oc cp <some-namespace>/<some-pod>:/tmp/foo /tmp/bar
```

#### 2.6.1.36. oc create

파일 또는 stdin에서 리소스를 생성

```bash
# Create a pod using the data in pod.json
  oc create -f ./pod.json

  # Create a pod based on the JSON passed into stdin
  cat pod.json | oc create -f -

  # Edit the data in registry.yaml in JSON then create the resource using the edited data
  oc create -f registry.yaml --edit -o json
```

#### 2.6.1.37. oc create build

새 빌드를 생성

```bash
# Create a new build
  oc create build myapp
```

#### 2.6.1.38. oc create clusterresourcequota

클러스터 리소스 쿼터를 생성

```bash
# Create a cluster resource quota limited to 10 pods
  oc create clusterresourcequota limit-bob --project-annotation-selector=openshift.io/requester=user-bob --hard=pods=10
```

#### 2.6.1.39. oc create clusterrole

클러스터 역할 생성

```bash
# Create a cluster role named "pod-reader" that allows user to perform "get", "watch" and "list" on pods
  oc create clusterrole pod-reader --verb=get,list,watch --resource=pods

  # Create a cluster role named "pod-reader" with ResourceName specified
  oc create clusterrole pod-reader --verb=get --resource=pods --resource-name=readablepod --resource-name=anotherpod

  # Create a cluster role named "foo" with API Group specified
  oc create clusterrole foo --verb=get,list,watch --resource=rs.apps

  # Create a cluster role named "foo" with SubResource specified
  oc create clusterrole foo --verb=get,list,watch --resource=pods,pods/status

  # Create a cluster role name "foo" with NonResourceURL specified
  oc create clusterrole "foo" --verb=get --non-resource-url=/logs/*

  # Create a cluster role name "monitoring" with AggregationRule specified
  oc create clusterrole monitoring --aggregation-rule="rbac.example.com/aggregate-to-monitoring=true"
```

#### 2.6.1.40. oc create clusterrolebinding

특정 클러스터 역할에 대한 클러스터 역할 바인딩 생성

```bash
# Create a cluster role binding for user1, user2, and group1 using the cluster-admin cluster role
  oc create clusterrolebinding cluster-admin --clusterrole=cluster-admin --user=user1 --user=user2 --group=group1
```

#### 2.6.1.41. oc create configmap

로컬 파일, 디렉터리 또는 리터럴 값에서 구성 맵 생성

```bash
# Create a new config map named my-config based on folder bar
  oc create configmap my-config --from-file=path/to/bar

  # Create a new config map named my-config with specified keys instead of file basenames on disk
  oc create configmap my-config --from-file=key1=/path/to/bar/file1.txt --from-file=key2=/path/to/bar/file2.txt

  # Create a new config map named my-config with key1=config1 and key2=config2
  oc create configmap my-config --from-literal=key1=config1 --from-literal=key2=config2

  # Create a new config map named my-config from the key=value pairs in the file
  oc create configmap my-config --from-file=path/to/bar

  # Create a new config map named my-config from an env file
  oc create configmap my-config --from-env-file=path/to/foo.env --from-env-file=path/to/bar.env
```

#### 2.6.1.42. oc create cronjob

지정된 이름으로 cron 작업 생성

```bash
# Create a cron job
  oc create cronjob my-job --image=busybox --schedule="*/1 * * * *"

  # Create a cron job with a command
  oc create cronjob my-job --image=busybox --schedule="*/1 * * * *" -- date
```

#### 2.6.1.43. oc create deployment

지정된 이름으로 배포 생성

```bash
# Create a deployment named my-dep that runs the busybox image
  oc create deployment my-dep --image=busybox

  # Create a deployment with a command
  oc create deployment my-dep --image=busybox -- date

  # Create a deployment named my-dep that runs the nginx image with 3 replicas
  oc create deployment my-dep --image=nginx --replicas=3

  # Create a deployment named my-dep that runs the busybox image and expose port 5701
  oc create deployment my-dep --image=busybox --port=5701

  # Create a deployment named my-dep that runs multiple containers
  oc create deployment my-dep --image=busybox:latest --image=ubuntu:latest --image=nginx
```

#### 2.6.1.44. oc create deploymentconfig

지정된 이미지를 사용하는 기본 옵션으로 배포 구성을 생성

```bash
# Create an nginx deployment config named my-nginx
  oc create deploymentconfig my-nginx --image=nginx
```

#### 2.6.1.45. oc create identity

수동으로 ID를 생성 (자동 생성이 비활성화된 경우에만 필요)

```bash
# Create an identity with identity provider "acme_ldap" and the identity provider username "adamjones"
  oc create identity acme_ldap:adamjones
```

#### 2.6.1.46. oc create imagestream

비어 있는 새 이미지 스트림을 생성

```bash
# Create a new image stream
  oc create imagestream mysql
```

#### 2.6.1.47. oc create imagestreamtag

새 이미지 스트림 태그를 생성

```bash
# Create a new image stream tag based on an image in a remote registry
  oc create imagestreamtag mysql:latest --from-image=myregistry.local/mysql/mysql:5.0
```

#### 2.6.1.48. oc create ingress

지정된 이름으로 수신 생성

```bash
# Create a single ingress called 'simple' that directs requests to foo.com/bar to svc
  # svc1:8080 with a TLS secret "my-cert"
  oc create ingress simple --rule="foo.com/bar=svc1:8080,tls=my-cert"

  # Create a catch all ingress of "/path" pointing to service svc:port and Ingress Class as "otheringress"
  oc create ingress catch-all --class=otheringress --rule="/path=svc:port"

  # Create an ingress with two annotations: ingress.annotation1 and ingress.annotations2
  oc create ingress annotated --class=default --rule="foo.com/bar=svc:port" \
  --annotation ingress.annotation1=foo \
  --annotation ingress.annotation2=bla

  # Create an ingress with the same host and multiple paths
  oc create ingress multipath --class=default \
  --rule="foo.com/=svc:port" \
  --rule="foo.com/admin/=svcadmin:portadmin"

  # Create an ingress with multiple hosts and the pathType as Prefix
  oc create ingress ingress1 --class=default \
  --rule="foo.com/path*=svc:8080" \
  --rule="bar.com/admin*=svc2:http"

  # Create an ingress with TLS enabled using the default ingress certificate and different path types
  oc create ingress ingtls --class=default \
  --rule="foo.com/=svc:https,tls" \
  --rule="foo.com/path/subpath*=othersvc:8080"

  # Create an ingress with TLS enabled using a specific secret and pathType as Prefix
  oc create ingress ingsecret --class=default \
  --rule="foo.com/*=svc:8080,tls=secret1"

  # Create an ingress with a default backend
  oc create ingress ingdefault --class=default \
  --default-backend=defaultsvc:http \
  --rule="foo.com/*=svc:8080,tls=secret1"
```

#### 2.6.1.49. oc create job

지정된 이름으로 작업 생성

```bash
# Create a job
  oc create job my-job --image=busybox

  # Create a job with a command
  oc create job my-job --image=busybox -- date

  # Create a job from a cron job named "a-cronjob"
  oc create job test-job --from=cronjob/a-cronjob
```

#### 2.6.1.50. oc create namespace

지정된 이름으로 네임 스페이스를 생성

```bash
# Create a new namespace named my-namespace
  oc create namespace my-namespace
```

#### 2.6.1.51. oc create poddisruptionbudget

지정된 이름으로 Pod 중단 예산 생성

```bash
# Create a pod disruption budget named my-pdb that will select all pods with the app=rails label
  # and require at least one of them being available at any point in time
  oc create poddisruptionbudget my-pdb --selector=app=rails --min-available=1

  # Create a pod disruption budget named my-pdb that will select all pods with the app=nginx label
  # and require at least half of the pods selected to be available at any point in time
  oc create pdb my-pdb --selector=app=nginx --min-available=50%
```

#### 2.6.1.52. oc create priorityclass

지정된 이름으로 우선순위 클래스 생성

```bash
# Create a priority class named high-priority
  oc create priorityclass high-priority --value=1000 --description="high priority"

  # Create a priority class named default-priority that is considered as the global default priority
  oc create priorityclass default-priority --value=1000 --global-default=true --description="default priority"

  # Create a priority class named high-priority that cannot preempt pods with lower priority
  oc create priorityclass high-priority --value=1000 --description="high priority" --preemption-policy="Never"
```

#### 2.6.1.53. oc create quota

지정된 이름으로 할당량 생성

```bash
# Create a new resource quota named my-quota
  oc create quota my-quota --hard=cpu=1,memory=1G,pods=2,services=3,replicationcontrollers=2,resourcequotas=1,secrets=5,persistentvolumeclaims=10

  # Create a new resource quota named best-effort
  oc create quota best-effort --hard=pods=100 --scopes=BestEffort
```

#### 2.6.1.54. oc create role

단일 규칙을 사용하여 역할 생성

```bash
# Create a role named "pod-reader" that allows user to perform "get", "watch" and "list" on pods
  oc create role pod-reader --verb=get --verb=list --verb=watch --resource=pods

  # Create a role named "pod-reader" with ResourceName specified
  oc create role pod-reader --verb=get --resource=pods --resource-name=readablepod --resource-name=anotherpod

  # Create a role named "foo" with API Group specified
  oc create role foo --verb=get,list,watch --resource=rs.apps

  # Create a role named "foo" with SubResource specified
  oc create role foo --verb=get,list,watch --resource=pods,pods/status
```

#### 2.6.1.55. oc create rolebinding

특정 역할 또는 클러스터 역할에 대한 역할 바인딩 생성

```bash
# Create a role binding for user1, user2, and group1 using the admin cluster role
  oc create rolebinding admin --clusterrole=admin --user=user1 --user=user2 --group=group1

  # Create a role binding for service account monitoring:sa-dev using the admin role
  oc create rolebinding admin-binding --role=admin --serviceaccount=monitoring:sa-dev
```

#### 2.6.1.56. oc create route edge

엣지 TLS 종료를 사용하는 경로를 생성

```bash
# Create an edge route named "my-route" that exposes the frontend service
  oc create route edge my-route --service=frontend

  # Create an edge route that exposes the frontend service and specify a path
  # If the route name is omitted, the service name will be used
  oc create route edge --service=frontend --path /assets
```

#### 2.6.1.57. oc create route passthrough

패스스루 TLS 종료를 사용하는 경로를 생성

```bash
# Create a passthrough route named "my-route" that exposes the frontend service
  oc create route passthrough my-route --service=frontend

  # Create a passthrough route that exposes the frontend service and specify
  # a host name. If the route name is omitted, the service name will be used
  oc create route passthrough --service=frontend --hostname=www.example.com
```

#### 2.6.1.58. oc create route reencrypt

재암호화 TLS 종료를 사용하는 경로를 생성

```bash
# Create a route named "my-route" that exposes the frontend service
  oc create route reencrypt my-route --service=frontend --dest-ca-cert cert.cert

  # Create a reencrypt route that exposes the frontend service, letting the
  # route name default to the service name and the destination CA certificate
  # default to the service CA
  oc create route reencrypt --service=frontend
```

#### 2.6.1.59. oc create secret docker-registry

Docker 레지스트리와 함께 사용할 시크릿을 생성

```bash
# If you do not already have a .dockercfg file, create a dockercfg secret directly
  oc create secret docker-registry my-secret --docker-server=DOCKER_REGISTRY_SERVER --docker-username=DOCKER_USER --docker-password=DOCKER_PASSWORD --docker-email=DOCKER_EMAIL

  # Create a new secret named my-secret from ~/.docker/config.json
  oc create secret docker-registry my-secret --from-file=path/to/.docker/config.json
```

#### 2.6.1.60. oc create secret generic

로컬 파일, 디렉터리 또는 리터럴 값에서 시크릿을 생성

```bash
# Create a new secret named my-secret with keys for each file in folder bar
  oc create secret generic my-secret --from-file=path/to/bar

  # Create a new secret named my-secret with specified keys instead of names on disk
  oc create secret generic my-secret --from-file=ssh-privatekey=path/to/id_rsa --from-file=ssh-publickey=path/to/id_rsa.pub

  # Create a new secret named my-secret with key1=supersecret and key2=topsecret
  oc create secret generic my-secret --from-literal=key1=supersecret --from-literal=key2=topsecret

  # Create a new secret named my-secret using a combination of a file and a literal
  oc create secret generic my-secret --from-file=ssh-privatekey=path/to/id_rsa --from-literal=passphrase=topsecret

  # Create a new secret named my-secret from env files
  oc create secret generic my-secret --from-env-file=path/to/foo.env --from-env-file=path/to/bar.env
```

#### 2.6.1.61. oc create secret tls

TLS 시크릿을 생성

```bash
# Create a new TLS secret named tls-secret with the given key pair
  oc create secret tls tls-secret --cert=path/to/tls.crt --key=path/to/tls.key
```

#### 2.6.1.62. oc create service clusterip

ClusterIP 서비스 생성

```bash
# Create a new ClusterIP service named my-cs
  oc create service clusterip my-cs --tcp=5678:8080

  # Create a new ClusterIP service named my-cs (in headless mode)
  oc create service clusterip my-cs --clusterip="None"
```

#### 2.6.1.63. oc create service externalname

ExternalName 서비스 생성

```bash
# Create a new ExternalName service named my-ns
  oc create service externalname my-ns --external-name bar.com
```

#### 2.6.1.64. oc create service loadbalancer

LoadBalancer 서비스 생성

```bash
# Create a new LoadBalancer service named my-lbs
  oc create service loadbalancer my-lbs --tcp=5678:8080
```

#### 2.6.1.65. oc create service nodeport

NodePort 서비스 생성

```bash
# Create a new NodePort service named my-ns
  oc create service nodeport my-ns --tcp=5678:8080
```

#### 2.6.1.66. oc create serviceaccount

지정된 이름으로 서비스 계정을 생성

```bash
# Create a new service account named my-service-account
  oc create serviceaccount my-service-account
```

#### 2.6.1.67. oc create token

서비스 계정 토큰 요청

```bash
# Request a token to authenticate to the kube-apiserver as the service account "myapp" in the current namespace
  oc create token myapp

  # Request a token for a service account in a custom namespace
  oc create token myapp --namespace myns

  # Request a token with a custom expiration
  oc create token myapp --duration 10m

  # Request a token with a custom audience
  oc create token myapp --audience https://example.com

  # Request a token bound to an instance of a Secret object
  oc create token myapp --bound-object-kind Secret --bound-object-name mysecret

  # Request a token bound to an instance of a Secret object with a specific UID
  oc create token myapp --bound-object-kind Secret --bound-object-name mysecret --bound-object-uid 0d4691ed-659b-4935-a832-355f77ee47cc
```

#### 2.6.1.68. oc create user

사용자를 수동으로 생성 (자동 생성이 비활성화된 경우에만 필요)

```bash
# Create a user with the username "ajones" and the display name "Adam Jones"
  oc create user ajones --full-name="Adam Jones"
```

#### 2.6.1.69. oc create useridentitymapping

ID를 사용자에게 수동으로 매핑

```bash
# Map the identity "acme_ldap:adamjones" to the user "ajones"
  oc create useridentitymapping acme_ldap:adamjones ajones
```

#### 2.6.1.70. oc debug

디버깅을 위해 Pod의 새 인스턴스를 시작

```bash
# Start a shell session into a pod using the OpenShift tools image
  oc debug

  # Debug a currently running deployment by creating a new pod
  oc debug deploy/test

  # Debug a node as an administrator
  oc debug node/master-1

  # Debug a Windows node
  # Note: the chosen image must match the Windows Server version (2019, 2022) of the node
  oc debug node/win-worker-1 --image=mcr.microsoft.com/powershell:lts-nanoserver-ltsc2022

  # Launch a shell in a pod using the provided image stream tag
  oc debug istag/mysql:latest -n openshift

  # Test running a job as a non-root user
  oc debug job/test --as-user=1000000

  # Debug a specific failing container by running the env command in the 'second' container
  oc debug daemonset/test -c second -- /bin/env

  # See the pod that would be created to debug
  oc debug mypod-9xbc -o yaml

  # Debug a resource but launch the debug pod in another namespace
  # Note: Not all resources can be debugged using --to-namespace without modification. For example,
  # volumes and service accounts are namespace-dependent. Add '-o yaml' to output the debug pod definition
  # to disk.  If necessary, edit the definition then run 'oc debug -f -' or run without --to-namespace
  oc debug mypod-9xbc --to-namespace testns
```

#### 2.6.1.71. oc delete

파일 이름, stdin, 리소스 및 이름별 또는 리소스 및 라벨 선택기별 리소스 삭제

```bash
# Delete a pod using the type and name specified in pod.json
  oc delete -f ./pod.json

  # Delete resources from a directory containing kustomization.yaml - e.g. dir/kustomization.yaml
  oc delete -k dir

  # Delete resources from all files that end with '.json'
  oc delete -f '*.json'

  # Delete a pod based on the type and name in the JSON passed into stdin
  cat pod.json | oc delete -f -

  # Delete pods and services with same names "baz" and "foo"
  oc delete pod,service baz foo

  # Delete pods and services with label name=myLabel
  oc delete pods,services -l name=myLabel

  # Delete a pod with minimal delay
  oc delete pod foo --now

  # Force delete a pod on a dead node
  oc delete pod foo --force

  # Delete all pods
  oc delete pods --all

  # Delete all pods only if the user confirms the deletion
  oc delete pods --all --interactive
```

#### 2.6.1.72. oc describe

특정 리소스 또는 리소스 그룹의 세부 정보를 표시

```bash
# Describe a node
  oc describe nodes kubernetes-node-emt8.c.myproject.internal

  # Describe a pod
  oc describe pods/nginx

  # Describe a pod identified by type and name in "pod.json"
  oc describe -f pod.json

  # Describe all pods
  oc describe pods

  # Describe pods by label name=myLabel
  oc describe pods -l name=myLabel

  # Describe all pods managed by the 'frontend' replication controller
  # (rc-created pods get the name of the rc as a prefix in the pod name)
  oc describe pods frontend
```

#### 2.6.1.73. oc diff

적용될 버전에 대한 Diff 라이브 버전

```bash
# Diff resources included in pod.json
  oc diff -f pod.json

  # Diff file read from stdin
  cat service.yaml | oc diff -f -
```

#### 2.6.1.74. oc edit

서버에서 리소스를 편집

```bash
# Edit the service named 'registry'
  oc edit svc/registry

  # Use an alternative editor
  KUBE_EDITOR="nano" oc edit svc/registry

  # Edit the job 'myjob' in JSON using the v1 API format
  oc edit job.v1.batch/myjob -o json

  # Edit the deployment 'mydeployment' in YAML and save the modified config in its annotation
  oc edit deployment/mydeployment -o yaml --save-config

  # Edit the 'status' subresource for the 'mydeployment' deployment
  oc edit deployment mydeployment --subresource='status'
```

#### 2.6.1.75. oc events

이벤트 나열

```bash
# List recent events in the default namespace
  oc events

  # List recent events in all namespaces
  oc events --all-namespaces

  # List recent events for the specified pod, then wait for more events and list them as they arrive
  oc events --for pod/web-pod-13je7 --watch

  # List recent events in YAML format
  oc events -oyaml

  # List recent only events of type 'Warning' or 'Normal'
  oc events --types=Warning,Normal
```

#### 2.6.1.76. oc exec

컨테이너에서 명령을 실행

```bash
# Get output from running the 'date' command from pod mypod, using the first container by default
  oc exec mypod -- date

  # Get output from running the 'date' command in ruby-container from pod mypod
  oc exec mypod -c ruby-container -- date

  # Switch to raw terminal mode; sends stdin to 'bash' in ruby-container from pod mypod
  # and sends stdout/stderr from 'bash' back to the client
  oc exec mypod -c ruby-container -i -t -- bash -il

  # List contents of /usr from the first container of pod mypod and sort by modification time
  # If the command you want to execute in the pod has any flags in common (e.g. -i),
  # you must use two dashes (--) to separate your command's flags/arguments
  # Also note, do not surround your command and its flags/arguments with quotes
  # unless that is how you would execute it normally (i.e., do ls -t /usr, not "ls -t /usr")
  oc exec mypod -i -t -- ls -t /usr

  # Get output from running 'date' command from the first pod of the deployment mydeployment, using the first container by default
  oc exec deploy/mydeployment -- date

  # Get output from running 'date' command from the first pod of the service myservice, using the first container by default
  oc exec svc/myservice -- date
```

#### 2.6.1.77. oc explain

리소스에 대한 문서 가져오기

```bash
# Get the documentation of the resource and its fields
  oc explain pods

  # Get all the fields in the resource
  oc explain pods --recursive

  # Get the explanation for deployment in supported api versions
  oc explain deployments --api-version=apps/v1

  # Get the documentation of a specific field of a resource
  oc explain pods.spec.containers

  # Get the documentation of resources in different format
  oc explain deployment --output=plaintext-openapiv2
```

#### 2.6.1.78. oc expose

복제된 애플리케이션을 서비스 또는 경로로 노출

```bash
# Create a route based on service nginx. The new route will reuse nginx's labels
  oc expose service nginx

  # Create a route and specify your own label and route name
  oc expose service nginx -l name=myroute --name=fromdowntown

  # Create a route and specify a host name
  oc expose service nginx --hostname=www.example.com

  # Create a route with a wildcard
  oc expose service nginx --hostname=x.example.com --wildcard-policy=Subdomain
  # This would be equivalent to *.example.com. NOTE: only hosts are matched by the wildcard; subdomains would not be included

  # Expose a deployment configuration as a service and use the specified port
  oc expose dc ruby-hello-world --port=8080

  # Expose a service as a route in the specified path
  oc expose service nginx --path=/nginx
```

#### 2.6.1.79. oc extract

시크릿 또는 구성 맵을 디스크에 추출

```bash
# Extract the secret "test" to the current directory
  oc extract secret/test

  # Extract the config map "nginx" to the /tmp directory
  oc extract configmap/nginx --to=/tmp

  # Extract the config map "nginx" to STDOUT
  oc extract configmap/nginx --to=-

  # Extract only the key "nginx.conf" from config map "nginx" to the /tmp directory
  oc extract configmap/nginx --to=/tmp --keys=nginx.conf
```

#### 2.6.1.80. oc get

리소스를 하나 이상 표시

```bash
# List all pods in ps output format
  oc get pods

  # List all pods in ps output format with more information (such as node name)
  oc get pods -o wide

  # List a single replication controller with specified NAME in ps output format
  oc get replicationcontroller web

  # List deployments in JSON output format, in the "v1" version of the "apps" API group
  oc get deployments.v1.apps -o json

  # List a single pod in JSON output format
  oc get -o json pod web-pod-13je7

  # List a pod identified by type and name specified in "pod.yaml" in JSON output format
  oc get -f pod.yaml -o json

  # List resources from a directory with kustomization.yaml - e.g. dir/kustomization.yaml
  oc get -k dir/

  # Return only the phase value of the specified pod
  oc get -o template pod/web-pod-13je7 --template={{.status.phase}}

  # List resource information in custom columns
  oc get pod test-pod -o custom-columns=CONTAINER:.spec.containers[0].name,IMAGE:.spec.containers[0].image

  # List all replication controllers and services together in ps output format
  oc get rc,services

  # List one or more resources by their type and names
  oc get rc/web service/frontend pods/web-pod-13je7

  # List the 'status' subresource for a single pod
  oc get pod web-pod-13je7 --subresource status

  # List all deployments in namespace 'backend'
  oc get deployments.apps --namespace backend

  # List all pods existing in all namespaces
  oc get pods --all-namespaces
```

#### 2.6.1.81. oc get-token

실험: credentials exec 플러그인으로 외부 OIDC 발행자에서 토큰 가져오기

```bash
# Starts an auth code flow to the issuer URL with the client ID and the given extra scopes
  oc get-token --client-id=client-id --issuer-url=test.issuer.url --extra-scopes=email,profile

  # Starts an auth code flow to the issuer URL with a different callback address
  oc get-token --client-id=client-id --issuer-url=test.issuer.url --callback-address=127.0.0.1:8343
```

#### 2.6.1.82. oc idle

확장 가능한 리소스를 유휴 상태로 설정

```bash
# Idle the scalable controllers associated with the services listed in to-idle.txt
  $ oc idle --resource-names-file to-idle.txt
```

#### 2.6.1.83. oc image append

이미지에 레이어를 추가하고 레지스트리에 푸시

```bash
# Remove the entrypoint on the mysql:latest image
  oc image append --from mysql:latest --to myregistry.com/myimage:latest --image '{"Entrypoint":null}'

  # Add a new layer to the image
  oc image append --from mysql:latest --to myregistry.com/myimage:latest layer.tar.gz

  # Add a new layer to the image and store the result on disk
  # This results in $(pwd)/v2/mysql/blobs,manifests
  oc image append --from mysql:latest --to file://mysql:local layer.tar.gz

  # Add a new layer to the image and store the result on disk in a designated directory
  # This will result in $(pwd)/mysql-local/v2/mysql/blobs,manifests
  oc image append --from mysql:latest --to file://mysql:local --dir mysql-local layer.tar.gz

  # Add a new layer to an image that is stored on disk (~/mysql-local/v2/image exists)
  oc image append --from-dir ~/mysql-local --to myregistry.com/myimage:latest layer.tar.gz

  # Add a new layer to an image that was mirrored to the current directory on disk ($(pwd)/v2/image exists)
  oc image append --from-dir v2 --to myregistry.com/myimage:latest layer.tar.gz

  # Add a new layer to a multi-architecture image for an os/arch that is different from the system's os/arch
  # Note: The first image in the manifest list that matches the filter will be returned when --keep-manifest-list is not specified
  oc image append --from docker.io/library/busybox:latest --filter-by-os=linux/s390x --to myregistry.com/myimage:latest layer.tar.gz

  # Add a new layer to a multi-architecture image for all the os/arch manifests when keep-manifest-list is specified
  oc image append --from docker.io/library/busybox:latest --keep-manifest-list --to myregistry.com/myimage:latest layer.tar.gz

  # Add a new layer to a multi-architecture image for all the os/arch manifests that is specified by the filter, while preserving the manifestlist
  oc image append --from docker.io/library/busybox:latest --filter-by-os=linux/s390x --keep-manifest-list --to myregistry.com/myimage:latest layer.tar.gz
```

#### 2.6.1.84. oc image extract

이미지에서 파일 시스템으로 파일을 복사

```bash
# Extract the busybox image into the current directory
  oc image extract docker.io/library/busybox:latest

  # Extract the busybox image into a designated directory (must exist)
  oc image extract docker.io/library/busybox:latest --path /:/tmp/busybox

  # Extract the busybox image into the current directory for linux/s390x platform
  # Note: Wildcard filter is not supported with extract; pass a single os/arch to extract
  oc image extract docker.io/library/busybox:latest --filter-by-os=linux/s390x

  # Extract a single file from the image into the current directory
  oc image extract docker.io/library/centos:7 --path /bin/bash:.

  # Extract all .repo files from the image's /etc/yum.repos.d/ folder into the current directory
  oc image extract docker.io/library/centos:7 --path /etc/yum.repos.d/*.repo:.

  # Extract all .repo files from the image's /etc/yum.repos.d/ folder into a designated directory (must exist)
  # This results in /tmp/yum.repos.d/*.repo on local system
  oc image extract docker.io/library/centos:7 --path /etc/yum.repos.d/*.repo:/tmp/yum.repos.d

  # Extract an image stored on disk into the current directory ($(pwd)/v2/busybox/blobs,manifests exists)
  # --confirm is required because the current directory is not empty
  oc image extract file://busybox:local --confirm

  # Extract an image stored on disk in a directory other than $(pwd)/v2 into the current directory
  # --confirm is required because the current directory is not empty ($(pwd)/busybox-mirror-dir/v2/busybox exists)
  oc image extract file://busybox:local --dir busybox-mirror-dir --confirm

  # Extract an image stored on disk in a directory other than $(pwd)/v2 into a designated directory (must exist)
  oc image extract file://busybox:local --dir busybox-mirror-dir --path /:/tmp/busybox

  # Extract the last layer in the image
  oc image extract docker.io/library/centos:7[-1]

  # Extract the first three layers of the image
  oc image extract docker.io/library/centos:7[:3]

  # Extract the last three layers of the image
  oc image extract docker.io/library/centos:7[-3:]
```

#### 2.6.1.85. oc image info

이미지에 대한 정보 표시

```bash
# Show information about an image
  oc image info quay.io/openshift/cli:latest

  # Show information about images matching a wildcard
  oc image info quay.io/openshift/cli:4.*

  # Show information about a file mirrored to disk under DIR
  oc image info --dir=DIR file://library/busybox:latest

  # Select which image from a multi-OS image to show
  oc image info library/busybox:latest --filter-by-os=linux/arm64
```

#### 2.6.1.86. oc image mirror

한 저장소에서 다른 저장소로 이미지를 미러링

```bash
# Copy image to another tag
  oc image mirror myregistry.com/myimage:latest myregistry.com/myimage:stable

  # Copy image to another registry
  oc image mirror myregistry.com/myimage:latest docker.io/myrepository/myimage:stable

  # Copy all tags starting with mysql to the destination repository
  oc image mirror myregistry.com/myimage:mysql* docker.io/myrepository/myimage

  # Copy image to disk, creating a directory structure that can be served as a registry
  oc image mirror myregistry.com/myimage:latest file://myrepository/myimage:latest

  # Copy image to S3 (pull from <bucket>.s3.amazonaws.com/image:latest)
  oc image mirror myregistry.com/myimage:latest s3://s3.amazonaws.com/<region>/<bucket>/image:latest

  # Copy image to S3 without setting a tag (pull via @<digest>)
  oc image mirror myregistry.com/myimage:latest s3://s3.amazonaws.com/<region>/<bucket>/image

  # Copy image to multiple locations
  oc image mirror myregistry.com/myimage:latest docker.io/myrepository/myimage:stable \
  docker.io/myrepository/myimage:dev

  # Copy multiple images
  oc image mirror myregistry.com/myimage:latest=myregistry.com/other:test \
  myregistry.com/myimage:new=myregistry.com/other:target

  # Copy manifest list of a multi-architecture image, even if only a single image is found
  oc image mirror myregistry.com/myimage:latest=myregistry.com/other:test \
  --keep-manifest-list=true

  # Copy specific os/arch manifest of a multi-architecture image
  # Run 'oc image info myregistry.com/myimage:latest' to see available os/arch for multi-arch images
  # Note that with multi-arch images, this results in a new manifest list digest that includes only the filtered manifests
  oc image mirror myregistry.com/myimage:latest=myregistry.com/other:test \
  --filter-by-os=os/arch

  # Copy all os/arch manifests of a multi-architecture image
  # Run 'oc image info myregistry.com/myimage:latest' to see list of os/arch manifests that will be mirrored
  oc image mirror myregistry.com/myimage:latest=myregistry.com/other:test \
  --keep-manifest-list=true

  # Note the above command is equivalent to
  oc image mirror myregistry.com/myimage:latest=myregistry.com/other:test \
  --filter-by-os=.*

  # Copy specific os/arch manifest of a multi-architecture image
  # Run 'oc image info myregistry.com/myimage:latest' to see available os/arch for multi-arch images
  # Note that the target registry may reject a manifest list if the platform specific images do not all exist
  # You must use a registry with sparse registry support enabled
  oc image mirror myregistry.com/myimage:latest=myregistry.com/other:test \
  --filter-by-os=linux/386 \
  --keep-manifest-list=true
```

#### 2.6.1.87. oc import-image

컨테이너 이미지 레지스트리에서 이미지를 가져옵니다

```bash
# Import tag latest into a new image stream
  oc import-image mystream --from=registry.io/repo/image:latest --confirm

  # Update imported data for tag latest in an already existing image stream
  oc import-image mystream

  # Update imported data for tag stable in an already existing image stream
  oc import-image mystream:stable

  # Update imported data for all tags in an existing image stream
  oc import-image mystream --all

  # Update imported data for a tag that points to a manifest list to include the full manifest list
  oc import-image mystream --import-mode=PreserveOriginal

  # Import all tags into a new image stream
  oc import-image mystream --from=registry.io/repo/image --all --confirm

  # Import all tags into a new image stream using a custom timeout
  oc --request-timeout=5m import-image mystream --from=registry.io/repo/image --all --confirm
```

#### 2.6.1.88. oc kustomize

디렉터리 또는 URL에서 kustomization 대상을 빌드합니다.

```bash
# Build the current working directory
  oc kustomize

  # Build some shared configuration directory
  oc kustomize /home/config/production

  # Build from github
  oc kustomize https://github.com/kubernetes-sigs/kustomize.git/examples/helloWorld?ref=v1.0.6
```

#### 2.6.1.89. oc label

리소스에서 레이블을 업데이트

```bash
# Update pod 'foo' with the label 'unhealthy' and the value 'true'
  oc label pods foo unhealthy=true

  # Update pod 'foo' with the label 'status' and the value 'unhealthy', overwriting any existing value
  oc label --overwrite pods foo status=unhealthy

  # Update all pods in the namespace
  oc label pods --all status=unhealthy

  # Update a pod identified by the type and name in "pod.json"
  oc label -f pod.json status=unhealthy

  # Update pod 'foo' only if the resource is unchanged from version 1
  oc label pods foo status=unhealthy --resource-version=1

  # Update pod 'foo' by removing a label named 'bar' if it exists
  # Does not require the --overwrite flag
  oc label pods foo bar-
```

#### 2.6.1.90. oc login

서버에 로그인

```bash
# Log in interactively
  oc login --username=myuser

  # Log in to the given server with the given certificate authority file
  oc login localhost:8443 --certificate-authority=/path/to/cert.crt

  # Log in to the given server with the given credentials (will not prompt interactively)
  oc login localhost:8443 --username=myuser --password=mypass

  # Log in to the given server through a browser
  oc login localhost:8443 --web --callback-port 8280

  # Log in to the external OIDC issuer through Auth Code + PKCE by starting a local server listening on port 8080
  oc login localhost:8443 --exec-plugin=oc-oidc --client-id=client-id --extra-scopes=email,profile --callback-port=8080
```

#### 2.6.1.91. oc logout

현재 서버 세션을 종료

```bash
# Log out
  oc logout
```

#### 2.6.1.92. oc logs

Pod에서 컨테이너의 로그를 출력

```bash
# Start streaming the logs of the most recent build of the openldap build config
  oc logs -f bc/openldap

  # Start streaming the logs of the latest deployment of the mysql deployment config
  oc logs -f dc/mysql

  # Get the logs of the first deployment for the mysql deployment config. Note that logs
  # from older deployments may not exist either because the deployment was successful
  # or due to deployment pruning or manual deletion of the deployment
  oc logs --version=1 dc/mysql

  # Return a snapshot of ruby-container logs from pod backend
  oc logs backend -c ruby-container

  # Start streaming of ruby-container logs from pod backend
  oc logs -f pod/backend -c ruby-container
```

#### 2.6.1.93. oc new-app

새 애플리케이션을 생성

```bash
# List all local templates and image streams that can be used to create an app
  oc new-app --list

  # Create an application based on the source code in the current git repository (with a public remote) and a container image
  oc new-app . --image=registry/repo/langimage

  # Create an application myapp with Docker based build strategy expecting binary input
  oc new-app  --strategy=docker --binary --name myapp

  # Create a Ruby application based on the provided [image]~[source code] combination
  oc new-app centos/ruby-25-centos7~https://github.com/sclorg/ruby-ex.git

  # Use the public container registry MySQL image to create an app. Generated artifacts will be labeled with db=mysql
  oc new-app mysql MYSQL_USER=user MYSQL_PASSWORD=pass MYSQL_DATABASE=testdb -l db=mysql

  # Use a MySQL image in a private registry to create an app and override application artifacts' names
  oc new-app --image=myregistry.com/mycompany/mysql --name=private

  # Use an image with the full manifest list to create an app and override application artifacts' names
  oc new-app --image=myregistry.com/mycompany/image --name=private --import-mode=PreserveOriginal

  # Create an application from a remote repository using its beta4 branch
  oc new-app https://github.com/openshift/ruby-hello-world#beta4

  # Create an application based on a stored template, explicitly setting a parameter value
  oc new-app --template=ruby-helloworld-sample --param=MYSQL_USER=admin

  # Create an application from a remote repository and specify a context directory
  oc new-app https://github.com/youruser/yourgitrepo --context-dir=src/build

  # Create an application from a remote private repository and specify which existing secret to use
  oc new-app https://github.com/youruser/yourgitrepo --source-secret=yoursecret

  # Create an application based on a template file, explicitly setting a parameter value
  oc new-app --file=./example/myapp/template.json --param=MYSQL_USER=admin

  # Search all templates, image streams, and container images for the ones that match "ruby"
  oc new-app --search ruby

  # Search for "ruby", but only in stored templates (--template, --image-stream and --image
  # can be used to filter search results)
  oc new-app --search --template=ruby

  # Search for "ruby" in stored templates and print the output as YAML
  oc new-app --search --template=ruby --output=yaml
```

#### 2.6.1.94. oc new-build

새 빌드 구성을 생성

```bash
# Create a build config based on the source code in the current git repository (with a public
  # remote) and a container image
  oc new-build . --image=repo/langimage

  # Create a NodeJS build config based on the provided [image]~[source code] combination
  oc new-build centos/nodejs-8-centos7~https://github.com/sclorg/nodejs-ex.git

  # Create a build config from a remote repository using its beta2 branch
  oc new-build https://github.com/openshift/ruby-hello-world#beta2

  # Create a build config using a Dockerfile specified as an argument
  oc new-build -D $'FROM centos:7\nRUN yum install -y httpd'

  # Create a build config from a remote repository and add custom environment variables
  oc new-build https://github.com/openshift/ruby-hello-world -e RACK_ENV=development

  # Create a build config from a remote private repository and specify which existing secret to use
  oc new-build https://github.com/youruser/yourgitrepo --source-secret=yoursecret

  # Create a build config using  an image with the full manifest list to create an app and override application artifacts' names
  oc new-build --image=myregistry.com/mycompany/image --name=private --import-mode=PreserveOriginal

  # Create a build config from a remote repository and inject the npmrc into a build
  oc new-build https://github.com/openshift/ruby-hello-world --build-secret npmrc:.npmrc

  # Create a build config from a remote repository and inject environment data into a build
  oc new-build https://github.com/openshift/ruby-hello-world --build-config-map env:config

  # Create a build config that gets its input from a remote repository and another container image
  oc new-build https://github.com/openshift/ruby-hello-world --source-image=openshift/jenkins-1-centos7 --source-image-path=/var/lib/jenkins:tmp
```

#### 2.6.1.95. oc new-project

새 프로젝트를 요청

```bash
# Create a new project with minimal information
  oc new-project web-team-dev

  # Create a new project with a display name and description
  oc new-project web-team-dev --display-name="Web Team Development" --description="Development project for the web team."
```

#### 2.6.1.96. oc observe

리소스에 대한 변경 사항을 관찰하고 이에 대응합니다(시험적)

```bash
# Observe changes to services
  oc observe services

  # Observe changes to services, including the clusterIP and invoke a script for each
  oc observe services --template '{ .spec.clusterIP }' -- register_dns.sh

  # Observe changes to services filtered by a label selector
  oc observe services -l regist-dns=true --template '{ .spec.clusterIP }' -- register_dns.sh
```

#### 2.6.1.97. oc patch

리소스 필드를 업데이트

```bash
# Partially update a node using a strategic merge patch, specifying the patch as JSON
  oc patch node k8s-node-1 -p '{"spec":{"unschedulable":true}}'

  # Partially update a node using a strategic merge patch, specifying the patch as YAML
  oc patch node k8s-node-1 -p $'spec:\n unschedulable: true'

  # Partially update a node identified by the type and name specified in "node.json" using strategic merge patch
  oc patch -f node.json -p '{"spec":{"unschedulable":true}}'

  # Update a container's image; spec.containers[*].name is required because it's a merge key
  oc patch pod valid-pod -p '{"spec":{"containers":[{"name":"kubernetes-serve-hostname","image":"new image"}]}}'

  # Update a container's image using a JSON patch with positional arrays
  oc patch pod valid-pod --type='json' -p='[{"op": "replace", "path": "/spec/containers/0/image", "value":"new image"}]'

  # Update a deployment's replicas through the 'scale' subresource using a merge patch
  oc patch deployment nginx-deployment --subresource='scale' --type='merge' -p '{"spec":{"replicas":2}}'
```

#### 2.6.1.98. oc plugin

플러그인과 상호 작용하기 위한 유틸리티 제공

```bash
# List all available plugins
  oc plugin list

  # List only binary names of available plugins without paths
  oc plugin list --name-only
```

#### 2.6.1.99. oc plugin list

사용자의 PATH에 표시되는 모든 플러그인 실행 파일 나열

```bash
# List all available plugins
  oc plugin list

  # List only binary names of available plugins without paths
  oc plugin list --name-only
```

#### 2.6.1.100. oc policy add-role-to-user

현재 프로젝트의 사용자 또는 서비스 계정에 역할을 추가

```bash
# Add the 'view' role to user1 for the current project
  oc policy add-role-to-user view user1

  # Add the 'edit' role to serviceaccount1 for the current project
  oc policy add-role-to-user edit -z serviceaccount1
```

#### 2.6.1.101. oc policy scc-review

Pod를 생성할 수 있는 서비스 계정을 확인

```bash
# Check whether service accounts sa1 and sa2 can admit a pod with a template pod spec specified in my_resource.yaml
  # Service Account specified in myresource.yaml file is ignored
  oc policy scc-review -z sa1,sa2 -f my_resource.yaml

  # Check whether service accounts system:serviceaccount:bob:default can admit a pod with a template pod spec specified in my_resource.yaml
  oc policy scc-review -z system:serviceaccount:bob:default -f my_resource.yaml

  # Check whether the service account specified in my_resource_with_sa.yaml can admit the pod
  oc policy scc-review -f my_resource_with_sa.yaml

  # Check whether the default service account can admit the pod; default is taken since no service account is defined in myresource_with_no_sa.yaml
  oc policy scc-review -f myresource_with_no_sa.yaml
```

#### 2.6.1.102. oc policy scc-subject-review

사용자 또는 서비스 계정의 Pod 생성 가능 여부 확인

```bash
# Check whether user bob can create a pod specified in myresource.yaml
  oc policy scc-subject-review -u bob -f myresource.yaml

  # Check whether user bob who belongs to projectAdmin group can create a pod specified in myresource.yaml
  oc policy scc-subject-review -u bob -g projectAdmin -f myresource.yaml

  # Check whether a service account specified in the pod template spec in myresourcewithsa.yaml can create the pod
  oc policy scc-subject-review -f myresourcewithsa.yaml
```

#### 2.6.1.103. oc port-forward

Pod에 하나 이상의 로컬 포트를 전달

```bash
# Listen on ports 5000 and 6000 locally, forwarding data to/from ports 5000 and 6000 in the pod
  oc port-forward pod/mypod 5000 6000

  # Listen on ports 5000 and 6000 locally, forwarding data to/from ports 5000 and 6000 in a pod selected by the deployment
  oc port-forward deployment/mydeployment 5000 6000

  # Listen on port 8443 locally, forwarding to the targetPort of the service's port named "https" in a pod selected by the service
  oc port-forward service/myservice 8443:https

  # Listen on port 8888 locally, forwarding to 5000 in the pod
  oc port-forward pod/mypod 8888:5000

  # Listen on port 8888 on all addresses, forwarding to 5000 in the pod
  oc port-forward --address 0.0.0.0 pod/mypod 8888:5000

  # Listen on port 8888 on localhost and selected IP, forwarding to 5000 in the pod
  oc port-forward --address localhost,10.19.21.23 pod/mypod 8888:5000

  # Listen on a random port locally, forwarding to 5000 in the pod
  oc port-forward pod/mypod :5000
```

#### 2.6.1.104. oc process

템플릿을 리소스 목록으로 처리

```bash
# Convert the template.json file into a resource list and pass to create
  oc process -f template.json | oc create -f -

  # Process a file locally instead of contacting the server
  oc process -f template.json --local -o yaml

  # Process template while passing a user-defined label
  oc process -f template.json -l name=mytemplate

  # Convert a stored template into a resource list
  oc process foo

  # Convert a stored template into a resource list by setting/overriding parameter values
  oc process foo PARM1=VALUE1 PARM2=VALUE2

  # Convert a template stored in different namespace into a resource list
  oc process openshift//foo

  # Convert template.json into a resource list
  cat template.json | oc process -f -
```

#### 2.6.1.105. oc project

다른 프로젝트로 전환

```bash
# Switch to the 'myapp' project
  oc project myapp

  # Display the project currently in use
  oc project
```

#### 2.6.1.106. oc projects

기존 프로젝트를 표시

```bash
# List all projects
  oc projects
```

#### 2.6.1.107. oc proxy

Kubernetes API 서버에 대해 프록시를 실행

```bash
# To proxy all of the Kubernetes API and nothing else
  oc proxy --api-prefix=/

  # To proxy only part of the Kubernetes API and also some static files
  # You can get pods info with 'curl localhost:8001/api/v1/pods'
  oc proxy --www=/my/files --www-prefix=/static/ --api-prefix=/api/

  # To proxy the entire Kubernetes API at a different root
  # You can get pods info with 'curl localhost:8001/custom/api/v1/pods'
  oc proxy --api-prefix=/custom/

  # Run a proxy to the Kubernetes API server on port 8011, serving static content from ./local/www/
  oc proxy --port=8011 --www=./local/www/

  # Run a proxy to the Kubernetes API server on an arbitrary local port
  # The chosen port for the server will be output to stdout
  oc proxy --port=0

  # Run a proxy to the Kubernetes API server, changing the API prefix to k8s-api
  # This makes e.g. the pods API available at localhost:8001/k8s-api/v1/pods/
  oc proxy --api-prefix=/k8s-api
```

#### 2.6.1.108. oc registry login

통합 레지스트리에 로그인

```bash
# Log in to the integrated registry
  oc registry login

  # Log in to different registry using BASIC auth credentials
  oc registry login --registry quay.io/myregistry --auth-basic=USER:PASS
```

#### 2.6.1.109. oc replace

리소스를 파일 이름 또는 stdin으로 교체

```bash
# Replace a pod using the data in pod.json
  oc replace -f ./pod.json

  # Replace a pod based on the JSON passed into stdin
  cat pod.json | oc replace -f -

  # Update a single-container pod's image version (tag) to v4
  oc get pod mypod -o yaml | sed 's/\(image: myimage\):.*$/\1:v4/' | oc replace -f -

  # Force replace, delete and then re-create the resource
  oc replace --force -f ./pod.json
```

#### 2.6.1.110. oc rollback

애플리케이션의 일부를 이전 배포로 되돌립니다

```bash
# Perform a rollback to the last successfully completed deployment for a deployment config
  oc rollback frontend

  # See what a rollback to version 3 will look like, but do not perform the rollback
  oc rollback frontend --to-version=3 --dry-run

  # Perform a rollback to a specific deployment
  oc rollback frontend-2

  # Perform the rollback manually by piping the JSON of the new config back to oc
  oc rollback frontend -o json | oc replace dc/frontend -f -

  # Print the updated deployment configuration in JSON format instead of performing the rollback
  oc rollback frontend -o json
```

#### 2.6.1.111. oc rollout

리소스 롤아웃 관리

```bash
# Roll back to the previous deployment
  oc rollout undo deployment/abc

  # Check the rollout status of a daemonset
  oc rollout status daemonset/foo

  # Restart a deployment
  oc rollout restart deployment/abc

  # Restart deployments with the 'app=nginx' label
  oc rollout restart deployment --selector=app=nginx
```

#### 2.6.1.112. oc rollout cancel

진행 중인 배포를 취소

```bash
# Cancel the in-progress deployment based on 'nginx'
  oc rollout cancel dc/nginx
```

#### 2.6.1.113. oc rollout history

롤아웃 내역 보기

```bash
# View the rollout history of a deployment
  oc rollout history deployment/abc

  # View the details of daemonset revision 3
  oc rollout history daemonset/abc --revision=3
```

#### 2.6.1.114. oc rollout latest

트리거의 최신 상태로 배포 구성에 대한 새 롤아웃 시작

```bash
# Start a new rollout based on the latest images defined in the image change triggers
  oc rollout latest dc/nginx

  # Print the rolled out deployment config
  oc rollout latest dc/nginx -o json
```

#### 2.6.1.115. oc rollout pause

제공된 리소스를 일시 중지됨으로 표시

```bash
# Mark the nginx deployment as paused
  # Any current state of the deployment will continue its function; new updates
  # to the deployment will not have an effect as long as the deployment is paused
  oc rollout pause deployment/nginx
```

#### 2.6.1.116. oc rollout restart

리소스를 다시 시작

```bash
# Restart all deployments in the test-namespace namespace
  oc rollout restart deployment -n test-namespace

  # Restart a deployment
  oc rollout restart deployment/nginx

  # Restart a daemon set
  oc rollout restart daemonset/abc

  # Restart deployments with the app=nginx label
  oc rollout restart deployment --selector=app=nginx
```

#### 2.6.1.117. oc rollout resume

일시 중지된 리소스 재개

```bash
# Resume an already paused deployment
  oc rollout resume deployment/nginx
```

#### 2.6.1.118. oc rollout retry

가장 최근에 실패한 롤아웃 재시도

```bash
# Retry the latest failed deployment based on 'frontend'
  # The deployer pod and any hook pods are deleted for the latest failed deployment
  oc rollout retry dc/frontend
```

#### 2.6.1.119. oc rollout status

롤아웃 상태를 표시

```bash
# Watch the rollout status of a deployment
  oc rollout status deployment/nginx
```

#### 2.6.1.120. oc rollout undo

이전 롤아웃 실행 취소

```bash
# Roll back to the previous deployment
  oc rollout undo deployment/abc

  # Roll back to daemonset revision 3
  oc rollout undo daemonset/abc --to-revision=3

  # Roll back to the previous deployment with dry-run
  oc rollout undo --dry-run=server deployment/abc
```

#### 2.6.1.121. oc rsh

컨테이너에서 쉘 세션 시작

```bash
# Open a shell session on the first container in pod 'foo'
  oc rsh foo

  # Open a shell session on the first container in pod 'foo' and namespace 'bar'
  # (Note that oc client specific arguments must come before the resource name and its arguments)
  oc rsh -n bar foo

  # Run the command 'cat /etc/resolv.conf' inside pod 'foo'
  oc rsh foo cat /etc/resolv.conf

  # See the configuration of your internal registry
  oc rsh dc/docker-registry cat config.yml

  # Open a shell session on the container named 'index' inside a pod of your job
  oc rsh -c index job/scheduled
```

#### 2.6.1.122. oc rsync

로컬 파일 시스템과 Pod 간 파일 복사

```bash
# Synchronize a local directory with a pod directory
  oc rsync ./local/dir/ POD:/remote/dir

  # Synchronize a pod directory with a local directory
  oc rsync POD:/remote/dir/ ./local/dir
```

#### 2.6.1.123. oc run

클러스터에서 특정 이미지 실행

```bash
# Start a nginx pod
  oc run nginx --image=nginx

  # Start a hazelcast pod and let the container expose port 5701
  oc run hazelcast --image=hazelcast/hazelcast --port=5701

  # Start a hazelcast pod and set environment variables "DNS_DOMAIN=cluster" and "POD_NAMESPACE=default" in the container
  oc run hazelcast --image=hazelcast/hazelcast --env="DNS_DOMAIN=cluster" --env="POD_NAMESPACE=default"

  # Start a hazelcast pod and set labels "app=hazelcast" and "env=prod" in the container
  oc run hazelcast --image=hazelcast/hazelcast --labels="app=hazelcast,env=prod"

  # Dry run; print the corresponding API objects without creating them
  oc run nginx --image=nginx --dry-run=client

  # Start a nginx pod, but overload the spec with a partial set of values parsed from JSON
  oc run nginx --image=nginx --overrides='{ "apiVersion": "v1", "spec": { ... } }'

  # Start a busybox pod and keep it in the foreground, don't restart it if it exits
  oc run -i -t busybox --image=busybox --restart=Never

  # Start the nginx pod using the default command, but use custom arguments (arg1 .. argN) for that command
  oc run nginx --image=nginx -- <arg1> <arg2> ... <argN>

  # Start the nginx pod using a different command and custom arguments
  oc run nginx --image=nginx --command -- <cmd> <arg1> ... <argN>
```

#### 2.6.1.124. oc scale

배포, 복제본 세트 또는 복제 컨트롤러의 새 크기 설정

```bash
# Scale a replica set named 'foo' to 3
  oc scale --replicas=3 rs/foo

  # Scale a resource identified by type and name specified in "foo.yaml" to 3
  oc scale --replicas=3 -f foo.yaml

  # If the deployment named mysql's current size is 2, scale mysql to 3
  oc scale --current-replicas=2 --replicas=3 deployment/mysql

  # Scale multiple replication controllers
  oc scale --replicas=5 rc/example1 rc/example2 rc/example3

  # Scale stateful set named 'web' to 3
  oc scale --replicas=3 statefulset/web
```

#### 2.6.1.125. oc secrets link

서비스 계정에 시크릿 연결

```bash
# Add an image pull secret to a service account to automatically use it for pulling pod images
  oc secrets link serviceaccount-name pull-secret --for=pull

  # Add an image pull secret to a service account to automatically use it for both pulling and pushing build images
  oc secrets link builder builder-image-secret --for=pull,mount
```

#### 2.6.1.126. oc secrets unlink

서비스 계정에서 시크릿 분리

```bash
# Unlink a secret currently associated with a service account
  oc secrets unlink serviceaccount-name secret-name another-secret-name ...
```

#### 2.6.1.127. oc set build-hook

빌드 구성에서 빌드 후크를 업데이트

```bash
# Clear post-commit hook on a build config
  oc set build-hook bc/mybuild --post-commit --remove

  # Set the post-commit hook to execute a test suite using a new entrypoint
  oc set build-hook bc/mybuild --post-commit --command -- /bin/bash -c /var/lib/test-image.sh

  # Set the post-commit hook to execute a shell script
  oc set build-hook bc/mybuild --post-commit --script="/var/lib/test-image.sh param1 param2 && /var/lib/done.sh"
```

#### 2.6.1.128. oc set build-secret

빌드 구성에서 빌드 보안을 업데이트

```bash
# Clear the push secret on a build config
  oc set build-secret --push --remove bc/mybuild

  # Set the pull secret on a build config
  oc set build-secret --pull bc/mybuild mysecret

  # Set the push and pull secret on a build config
  oc set build-secret --push --pull bc/mybuild mysecret

  # Set the source secret on a set of build configs matching a selector
  oc set build-secret --source -l app=myapp gitsecret
```

#### 2.6.1.129. oc set data

구성 맵 또는 시크릿 내의 데이터를 업데이트

```bash
# Set the 'password' key of a secret
  oc set data secret/foo password=this_is_secret

  # Remove the 'password' key from a secret
  oc set data secret/foo password-

  # Update the 'haproxy.conf' key of a config map from a file on disk
  oc set data configmap/bar --from-file=../haproxy.conf

  # Update a secret with the contents of a directory, one key per file
  oc set data secret/foo --from-file=secret-dir
```

#### 2.6.1.130. oc set deployment-hook

배포 구성에서 배포 후크를 업데이트

```bash
# Clear pre and post hooks on a deployment config
  oc set deployment-hook dc/myapp --remove --pre --post

  # Set the pre deployment hook to execute a db migration command for an application
  # using the data volume from the application
  oc set deployment-hook dc/myapp --pre --volumes=data -- /var/lib/migrate-db.sh

  # Set a mid deployment hook along with additional environment variables
  oc set deployment-hook dc/myapp --mid --volumes=data -e VAR1=value1 -e VAR2=value2 -- /var/lib/prepare-deploy.sh
```

#### 2.6.1.131. oc set env

Pod 템플릿에서 환경 변수를 업데이트

```bash
# Update deployment config 'myapp' with a new environment variable
  oc set env dc/myapp STORAGE_DIR=/local

  # List the environment variables defined on a build config 'sample-build'
  oc set env bc/sample-build --list

  # List the environment variables defined on all pods
  oc set env pods --all --list

  # Output modified build config in YAML
  oc set env bc/sample-build STORAGE_DIR=/data -o yaml

  # Update all containers in all replication controllers in the project to have ENV=prod
  oc set env rc --all ENV=prod

  # Import environment from a secret
  oc set env --from=secret/mysecret dc/myapp

  # Import environment from a config map with a prefix
  oc set env --from=configmap/myconfigmap --prefix=MYSQL_ dc/myapp

  # Remove the environment variable ENV from container 'c1' in all deployment configs
  oc set env dc --all --containers="c1" ENV-

  # Remove the environment variable ENV from a deployment config definition on disk and
  # update the deployment config on the server
  oc set env -f dc.json ENV-

  # Set some of the local shell environment into a deployment config on the server
  oc set env | grep RAILS_ | oc env -e - dc/myapp
```

#### 2.6.1.132. oc set image

Pod 템플릿 이미지 업데이트

```bash
# Set a deployment config's nginx container image to 'nginx:1.9.1', and its busybox container image to 'busybox'.
  oc set image dc/nginx busybox=busybox nginx=nginx:1.9.1

  # Set a deployment config's app container image to the image referenced by the imagestream tag 'openshift/ruby:2.3'.
  oc set image dc/myapp app=openshift/ruby:2.3 --source=imagestreamtag

  # Update all deployments' and rc's nginx container's image to 'nginx:1.9.1'
  oc set image deployments,rc nginx=nginx:1.9.1 --all

  # Update image of all containers of daemonset abc to 'nginx:1.9.1'
  oc set image daemonset abc *=nginx:1.9.1

  # Print result (in YAML format) of updating nginx container image from local file, without hitting the server
  oc set image -f path/to/file.yaml nginx=nginx:1.9.1 --local -o yaml
```

#### 2.6.1.133. oc set image-lookup

애플리케이션을 배포할 때 이미지가 해결되는 방법 변경

```bash
# Print all of the image streams and whether they resolve local names
  oc set image-lookup

  # Use local name lookup on image stream mysql
  oc set image-lookup mysql

  # Force a deployment to use local name lookup
  oc set image-lookup deploy/mysql

  # Show the current status of the deployment lookup
  oc set image-lookup deploy/mysql --list

  # Disable local name lookup on image stream mysql
  oc set image-lookup mysql --enabled=false

  # Set local name lookup on all image streams
  oc set image-lookup --all
```

#### 2.6.1.134. oc set probe

Pod 템플릿에서 프로브 업데이트

```bash
# Clear both readiness and liveness probes off all containers
  oc set probe dc/myapp --remove --readiness --liveness

  # Set an exec action as a liveness probe to run 'echo ok'
  oc set probe dc/myapp --liveness -- echo ok

  # Set a readiness probe to try to open a TCP socket on 3306
  oc set probe rc/mysql --readiness --open-tcp=3306

  # Set an HTTP startup probe for port 8080 and path /healthz over HTTP on the pod IP
  oc set probe dc/webapp --startup --get-url=http://:8080/healthz

  # Set an HTTP readiness probe for port 8080 and path /healthz over HTTP on the pod IP
  oc set probe dc/webapp --readiness --get-url=http://:8080/healthz

  # Set an HTTP readiness probe over HTTPS on 127.0.0.1 for a hostNetwork pod
  oc set probe dc/router --readiness --get-url=https://127.0.0.1:1936/stats

  # Set only the initial-delay-seconds field on all deployments
  oc set probe dc --all --readiness --initial-delay-seconds=30
```

#### 2.6.1.135. oc set resources

Pod 템플릿을 사용하여 오브젝트에서 리소스 요청/제한 업데이트

```bash
# Set a deployments nginx container CPU limits to "200m and memory to 512Mi"
  oc set resources deployment nginx -c=nginx --limits=cpu=200m,memory=512Mi

  # Set the resource request and limits for all containers in nginx
  oc set resources deployment nginx --limits=cpu=200m,memory=512Mi --requests=cpu=100m,memory=256Mi

  # Remove the resource requests for resources on containers in nginx
  oc set resources deployment nginx --limits=cpu=0,memory=0 --requests=cpu=0,memory=0

  # Print the result (in YAML format) of updating nginx container limits locally, without hitting the server
  oc set resources -f path/to/file.yaml --limits=cpu=200m,memory=512Mi --local -o yaml
```

#### 2.6.1.136. oc set route-backends

경로의 백엔드 업데이트

```bash
# Print the backends on the route 'web'
  oc set route-backends web

  # Set two backend services on route 'web' with 2/3rds of traffic going to 'a'
  oc set route-backends web a=2 b=1

  # Increase the traffic percentage going to b by 10%% relative to a
  oc set route-backends web --adjust b=+10%%

  # Set traffic percentage going to b to 10%% of the traffic going to a
  oc set route-backends web --adjust b=10%%

  # Set weight of b to 10
  oc set route-backends web --adjust b=10

  # Set the weight to all backends to zero
  oc set route-backends web --zero
```

#### 2.6.1.137. oc set selector

리소스에 선택기 설정

```bash
# Set the labels and selector before creating a deployment/service pair.
  oc create service clusterip my-svc --clusterip="None" -o yaml --dry-run | oc set selector --local -f - 'environment=qa' -o yaml | oc create -f -
  oc create deployment my-dep -o yaml --dry-run | oc label --local -f - environment=qa -o yaml | oc create -f -
```

#### 2.6.1.138. oc set serviceaccount

리소스의 서비스 계정을 업데이트

```bash
# Set deployment nginx-deployment's service account to serviceaccount1
  oc set serviceaccount deployment nginx-deployment serviceaccount1

  # Print the result (in YAML format) of updated nginx deployment with service account from a local file, without hitting the API server
  oc set sa -f nginx-deployment.yaml serviceaccount1 --local --dry-run -o yaml
```

#### 2.6.1.139. oc set subject

역할 바인딩 또는 클러스터 역할 바인딩에서 사용자, 그룹 또는 서비스 계정을 업데이트

```bash
# Update a cluster role binding for serviceaccount1
  oc set subject clusterrolebinding admin --serviceaccount=namespace:serviceaccount1

  # Update a role binding for user1, user2, and group1
  oc set subject rolebinding admin --user=user1 --user=user2 --group=group1

  # Print the result (in YAML format) of updating role binding subjects locally, without hitting the server
  oc create rolebinding admin --role=admin --user=admin -o yaml --dry-run | oc set subject --local -f - --user=foo -o yaml
```

#### 2.6.1.140. oc set triggers

하나 이상의 오브젝트에서 트리거 업데이트

```bash
# Print the triggers on the deployment config 'myapp'
  oc set triggers dc/myapp

  # Set all triggers to manual
  oc set triggers dc/myapp --manual

  # Enable all automatic triggers
  oc set triggers dc/myapp --auto

  # Reset the GitHub webhook on a build to a new, generated secret
  oc set triggers bc/webapp --from-github
  oc set triggers bc/webapp --from-webhook

  # Remove all triggers
  oc set triggers bc/webapp --remove-all

  # Stop triggering on config change
  oc set triggers dc/myapp --from-config --remove

  # Add an image trigger to a build config
  oc set triggers bc/webapp --from-image=namespace1/image:latest

  # Add an image trigger to a stateful set on the main container
  oc set triggers statefulset/db --from-image=namespace1/image:latest -c main
```

#### 2.6.1.141. oc set volumes

Pod 템플릿에서 볼륨 업데이트

```bash
# List volumes defined on all deployment configs in the current project
  oc set volume dc --all

  # Add a new empty dir volume to deployment config (dc) 'myapp' mounted under
  # /var/lib/myapp
  oc set volume dc/myapp --add --mount-path=/var/lib/myapp

  # Use an existing persistent volume claim (PVC) to overwrite an existing volume 'v1'
  oc set volume dc/myapp --add --name=v1 -t pvc --claim-name=pvc1 --overwrite

  # Remove volume 'v1' from deployment config 'myapp'
  oc set volume dc/myapp --remove --name=v1

  # Create a new persistent volume claim that overwrites an existing volume 'v1'
  oc set volume dc/myapp --add --name=v1 -t pvc --claim-size=1G --overwrite

  # Change the mount point for volume 'v1' to /data
  oc set volume dc/myapp --add --name=v1 -m /data --overwrite

  # Modify the deployment config by removing volume mount "v1" from container "c1"
  # (and by removing the volume "v1" if no other containers have volume mounts that reference it)
  oc set volume dc/myapp --remove --name=v1 --containers=c1

  # Add new volume based on a more complex volume source (AWS EBS, GCE PD,
  # Ceph, Gluster, NFS, ISCSI, ...)
  oc set volume dc/myapp --add -m /data --source=<json-string>
```

#### 2.6.1.142. oc start-build

새 빌드를 시작

```bash
# Starts build from build config "hello-world"
  oc start-build hello-world

  # Starts build from a previous build "hello-world-1"
  oc start-build --from-build=hello-world-1

  # Use the contents of a directory as build input
  oc start-build hello-world --from-dir=src/

  # Send the contents of a Git repository to the server from tag 'v2'
  oc start-build hello-world --from-repo=../hello-world --commit=v2

  # Start a new build for build config "hello-world" and watch the logs until the build
  # completes or fails
  oc start-build hello-world --follow

  # Start a new build for build config "hello-world" and wait until the build completes. It
  # exits with a non-zero return code if the build fails
  oc start-build hello-world --wait
```

#### 2.6.1.143. oc status

현재 프로젝트의 개요를 표시

```bash
# See an overview of the current project
  oc status

  # Export the overview of the current project in an svg file
  oc status -o dot | dot -T svg -o project.svg

  # See an overview of the current project including details for any identified issues
  oc status --suggest
```

#### 2.6.1.144. oc tag

기존 이미지를 이미지 스트림에 태깅

```bash
# Tag the current image for the image stream 'openshift/ruby' and tag '2.0' into the image stream 'yourproject/ruby with tag 'tip'
  oc tag openshift/ruby:2.0 yourproject/ruby:tip

  # Tag a specific image
  oc tag openshift/ruby@sha256:6b646fa6bf5e5e4c7fa41056c27910e679c03ebe7f93e361e6515a9da7e258cc yourproject/ruby:tip

  # Tag an external container image
  oc tag --source=docker openshift/origin-control-plane:latest yourproject/ruby:tip

  # Tag an external container image and request pullthrough for it
  oc tag --source=docker openshift/origin-control-plane:latest yourproject/ruby:tip --reference-policy=local

  # Tag an external container image and include the full manifest list
  oc tag --source=docker openshift/origin-control-plane:latest yourproject/ruby:tip --import-mode=PreserveOriginal

  # Remove the specified spec tag from an image stream
  oc tag openshift/origin-control-plane:latest -d
```

#### 2.6.1.145. oc version

클라이언트 및 서버 버전 정보를 인쇄

```bash
# Print the OpenShift client, kube-apiserver, and openshift-apiserver version information for the current context
  oc version

  # Print the OpenShift client, kube-apiserver, and openshift-apiserver version numbers for the current context in JSON format
  oc version --output json

  # Print the OpenShift client version information for the current context
  oc version --client
```

#### 2.6.1.146. oc wait

실험적: 하나 이상의 리소스에서 특정 조건을 대기합니다.

```bash
# Wait for the pod "busybox1" to contain the status condition of type "Ready"
  oc wait --for=condition=Ready pod/busybox1

  # The default value of status condition is true; you can wait for other targets after an equal delimiter (compared after Unicode simple case folding, which is a more general form of case-insensitivity)
  oc wait --for=condition=Ready=false pod/busybox1

  # Wait for the pod "busybox1" to contain the status phase to be "Running"
  oc wait --for=jsonpath='{.status.phase}'=Running pod/busybox1

  # Wait for pod "busybox1" to be Ready
  oc wait --for='jsonpath={.status.conditions[?(@.type=="Ready")].status}=True' pod/busybox1

  # Wait for the service "loadbalancer" to have ingress
  oc wait --for=jsonpath='{.status.loadBalancer.ingress}' service/loadbalancer

  # Wait for the secret "busybox1" to be created, with a timeout of 30s
  oc create secret generic busybox1
  oc wait --for=create secret/busybox1 --timeout=30s

  # Wait for the pod "busybox1" to be deleted, with a timeout of 60s, after having issued the "delete" command
  oc delete pod/busybox1
  oc wait --for=delete pod/busybox1 --timeout=60s
```

#### 2.6.1.147. oc whoami

현재 세션에 대한 정보를 반환

```bash
# Display the currently authenticated user
  oc whoami
```

#### 2.6.2. 추가 리소스

OpenShift CLI 관리자 명령 참조

### 2.7. OpenShift CLI 관리자 명령 참조

이 참조는 OpenShift CLI () 관리자 명령에 대한 설명 및 예제 명령을 제공합니다. 이러한 명령을 사용하려면 `cluster-admin` 또는 동등한 권한이 있어야 합니다.

```shell
oc
```

개발자 명령의 경우 OpenShift CLI 개발자 명령 참조를 참조하십시오.

다음 명령을 실행하여 모든 관리자 명령을 나열하거나 다음 명령을 실행하여 특정 명령에 대한 추가 세부 정보를 가져옵니다.

```shell
oc adm -h
```

```shell
oc <command> --help
```

#### 2.7.1.1. oc adm build-chain

빌드의 입력 및 종속 항목을 출력

```bash
# Build the dependency tree for the 'latest' tag in <image-stream>
  oc adm build-chain <image-stream>

  # Build the dependency tree for the 'v2' tag in dot format and visualize it via the dot utility
  oc adm build-chain <image-stream>:v2 -o dot | dot -T svg -o deps.svg

  # Build the dependency tree across all namespaces for the specified image stream tag found in the 'test' namespace
  oc adm build-chain <image-stream> -n test --all
```

#### 2.7.1.2. oc adm catalog mirror

operator-registry 카탈로그 미러링

```bash
# Mirror an operator-registry image and its contents to a registry
  oc adm catalog mirror quay.io/my/image:latest myregistry.com

  # Mirror an operator-registry image and its contents to a particular namespace in a registry
  oc adm catalog mirror quay.io/my/image:latest myregistry.com/my-namespace

  # Mirror to an airgapped registry by first mirroring to files
  oc adm catalog mirror quay.io/my/image:latest file:///local/index
  oc adm catalog mirror file:///local/index/my/image:latest my-airgapped-registry.com

  # Configure a cluster to use a mirrored registry
  oc apply -f manifests/imageDigestMirrorSet.yaml

  # Edit the mirroring mappings and mirror with "oc image mirror" manually
  oc adm catalog mirror --manifests-only quay.io/my/image:latest myregistry.com
  oc image mirror -f manifests/mapping.txt

  # Delete all ImageDigestMirrorSets generated by oc adm catalog mirror
  oc delete imagedigestmirrorset -l operators.openshift.org/catalog=true
```

#### 2.7.1.3. oc adm certificate approve

인증서 서명 요청 승인

```bash
# Approve CSR 'csr-sqgzp'
  oc adm certificate approve csr-sqgzp
```

#### 2.7.1.4. oc adm certificate deny

인증서 서명 요청 거부

```bash
# Deny CSR 'csr-sqgzp'
  oc adm certificate deny csr-sqgzp
```

#### 2.7.1.5. oc adm copy-to-node

지정된 파일을 노드에 복사

```bash
# Copy a new bootstrap kubeconfig file to node-0
  oc adm copy-to-node --copy=new-bootstrap-kubeconfig=/etc/kubernetes/kubeconfig node/node-0
```

#### 2.7.1.6. oc adm cordon

노드를 예약 불가로 표시

```bash
# Mark node "foo" as unschedulable
  oc adm cordon foo
```

#### 2.7.1.7. oc adm create-bootstrap-project-template

부트스트랩 프로젝트 템플릿을 생성

```bash
# Output a bootstrap project template in YAML format to stdout
  oc adm create-bootstrap-project-template -o yaml
```

#### 2.7.1.8. oc adm create-error-template

오류 페이지 템플릿 생성

```bash
# Output a template for the error page to stdout
  oc adm create-error-template
```

#### 2.7.1.9. oc adm create-login-template

로그인 템플릿 생성

```bash
# Output a template for the login page to stdout
  oc adm create-login-template
```

#### 2.7.1.10. oc adm create-provider-selection-template

공급자 선택 템플릿 생성

```bash
# Output a template for the provider selection page to stdout
  oc adm create-provider-selection-template
```

#### 2.7.1.11. oc adm drain

유지 관리를 위해 노드를 드레이닝

```bash
# Drain node "foo", even if there are pods not managed by a replication controller, replica set, job, daemon set, or stateful set on it
  oc adm drain foo --force

  # As above, but abort if there are pods not managed by a replication controller, replica set, job, daemon set, or stateful set, and use a grace period of 15 minutes
  oc adm drain foo --grace-period=900
```

#### 2.7.1.12. oc adm groups add-users

그룹에 사용자 추가

```bash
# Add user1 and user2 to my-group
  oc adm groups add-users my-group user1 user2
```

#### 2.7.1.13. oc adm groups new

새 그룹 생성

```bash
# Add a group with no users
  oc adm groups new my-group

  # Add a group with two users
  oc adm groups new my-group user1 user2

  # Add a group with one user and shorter output
  oc adm groups new my-group user1 -o name
```

#### 2.7.1.14. oc adm groups prune

외부 공급자에서 누락된 레코드를 참조하는 이전 OpenShift 그룹 제거

```bash
# Prune all orphaned groups
  oc adm groups prune --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Prune all orphaned groups except the ones from the denylist file
  oc adm groups prune --blacklist=/path/to/denylist.txt --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Prune all orphaned groups from a list of specific groups specified in an allowlist file
  oc adm groups prune --whitelist=/path/to/allowlist.txt --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Prune all orphaned groups from a list of specific groups specified in a list
  oc adm groups prune groups/group_name groups/other_name --sync-config=/path/to/ldap-sync-config.yaml --confirm
```

#### 2.7.1.15. oc adm groups remove-users

그룹에서 사용자 제거

```bash
# Remove user1 and user2 from my-group
  oc adm groups remove-users my-group user1 user2
```

#### 2.7.1.16. oc adm groups sync

외부 공급자에서 레코드와 OpenShift 그룹 동기화

```bash
# Sync all groups with an LDAP server
  oc adm groups sync --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Sync all groups except the ones from the blacklist file with an LDAP server
  oc adm groups sync --blacklist=/path/to/blacklist.txt --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Sync specific groups specified in an allowlist file with an LDAP server
  oc adm groups sync --whitelist=/path/to/allowlist.txt --sync-config=/path/to/sync-config.yaml --confirm

  # Sync all OpenShift groups that have been synced previously with an LDAP server
  oc adm groups sync --type=openshift --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Sync specific OpenShift groups if they have been synced previously with an LDAP server
  oc adm groups sync groups/group1 groups/group2 groups/group3 --sync-config=/path/to/sync-config.yaml --confirm
```

#### 2.7.1.17. oc adm inspect

지정된 리소스에 대한 디버깅 데이터 수집

```bash
# Collect debugging data for the "openshift-apiserver" clusteroperator
  oc adm inspect clusteroperator/openshift-apiserver

  # Collect debugging data for the "openshift-apiserver" and "kube-apiserver" clusteroperators
  oc adm inspect clusteroperator/openshift-apiserver clusteroperator/kube-apiserver

  # Collect debugging data for all clusteroperators
  oc adm inspect clusteroperator

  # Collect debugging data for all clusteroperators and clusterversions
  oc adm inspect clusteroperators,clusterversions
```

#### 2.7.1.18. oc adm migrate icsp

imagecontentsourcepolicy 파일을 imagedigestmirrorset 파일로 업데이트

```bash
# Update the imagecontentsourcepolicy.yaml file to a new imagedigestmirrorset file under the mydir directory
  oc adm migrate icsp imagecontentsourcepolicy.yaml --dest-dir mydir
```

#### 2.7.1.19. oc adm migrate template-instances

최신 group-version-kinds를 가리키도록 템플릿 인스턴스를 업데이트

```bash
# Perform a dry-run of updating all objects
  oc adm migrate template-instances

  # To actually perform the update, the confirm flag must be appended
  oc adm migrate template-instances --confirm
```

#### 2.7.1.20. oc adm must-gather

디버그 정보 수집을 위해 Pod의 새 인스턴스를 시작

```bash
# Gather information using the default plug-in image and command, writing into ./must-gather.local.<rand>
  oc adm must-gather

  # Gather information with a specific local folder to copy to
  oc adm must-gather --dest-dir=/local/directory

  # Gather audit information
  oc adm must-gather -- /usr/bin/gather_audit_logs

  # Gather information using multiple plug-in images
  oc adm must-gather --image=quay.io/kubevirt/must-gather --image=quay.io/openshift/origin-must-gather

  # Gather information using a specific image stream plug-in
  oc adm must-gather --image-stream=openshift/must-gather:latest

  # Gather information using a specific image, command, and pod directory
  oc adm must-gather --image=my/image:tag --source-dir=/pod/directory -- myspecial-command.sh
```

#### 2.7.1.21. oc adm new-project

새 프로젝트 생성

```bash
# Create a new project using a node selector
  oc adm new-project myproject --node-selector='type=user-node,region=east'
```

#### 2.7.1.22. oc adm node-image create

대상 클러스터에 추가할 노드를 부팅하기 위한 ISO 이미지 생성

```bash
# Create the ISO image and download it in the current folder
  oc adm node-image create

  # Use a different assets folder
  oc adm node-image create --dir=/tmp/assets

  # Specify a custom image name
  oc adm node-image create -o=my-node.iso

  # In place of an ISO, creates files that can be used for PXE boot
  oc adm node-image create --pxe

  # Create an ISO to add a single node without using the configuration file
  oc adm node-image create --mac-address=00:d8:e7:c7:4b:bb

  # Create an ISO to add a single node with a root device hint and without
  # using the configuration file
  oc adm node-image create --mac-address=00:d8:e7:c7:4b:bb --root-device-hint=deviceName:/dev/sda
```

#### 2.7.1.23. oc adm node-image 모니터

OpenShift 클러스터에 추가되는 새 노드 모니터링

```bash
# Monitor a single node being added to a cluster
  oc adm node-image monitor --ip-addresses 192.168.111.83

  # Monitor multiple nodes being added to a cluster by separating each
  # IP address with a comma
  oc adm node-image monitor --ip-addresses 192.168.111.83,192.168.111.84
```

#### 2.7.1.24. oc adm node-logs

노드 로그를 표시하고 필터링

```bash
# Show kubelet logs from all control plane nodes
  oc adm node-logs --role master -u kubelet

  # See what logs are available in control plane nodes in /var/log
  oc adm node-logs --role master --path=/

  # Display cron log file from all control plane nodes
  oc adm node-logs --role master --path=cron
```

#### 2.7.1.25. oc adm ocp-certificates monitor-certificates

플랫폼 인증서 감시

```bash
# Watch platform certificates
  oc adm ocp-certificates monitor-certificates
```

#### 2.7.1.26. oc adm ocp-certificates regenerate-leaf

클라이언트 다시 생성 및 OpenShift 클러스터의 인증서 제공

```bash
# Regenerate a leaf certificate contained in a particular secret
  oc adm ocp-certificates regenerate-leaf -n openshift-config-managed secret/kube-controller-manager-client-cert-key
```

#### 2.7.1.27. oc adm ocp-certificates recreate-machine-config-server-serving-cert

OpenShift 클러스터에서 머신 구성 Operator 인증서 다시 생성

```bash
# Regenerate the MCO certs without modifying user-data secrets
  oc adm ocp-certificates regenerate-machine-config-server-serving-cert --update-ignition=false

  # Update the user-data secrets to use new MCS certs
  oc adm ocp-certificates update-ignition-ca-bundle-for-machine-config-server
```

#### 2.7.1.28. oc adm ocp-certificates recreate-top-level

OpenShift 클러스터에서 최상위 인증서 다시 생성

```bash
# Regenerate the signing certificate contained in a particular secret
  oc adm ocp-certificates regenerate-top-level -n openshift-kube-apiserver-operator secret/loadbalancer-serving-signer-key
```

#### 2.7.1.29. oc adm ocp-certificates remove-old-trust

OpenShift 클러스터에서 플랫폼 신뢰 번들을 나타내는 ConfigMap에서 이전 CA 제거

```bash
# Remove a trust bundled contained in a particular config map
  oc adm ocp-certificates remove-old-trust -n openshift-config-managed configmaps/kube-apiserver-aggregator-client-ca --created-before 2023-06-05T14:44:06Z

  #  Remove only CA certificates created before a certain date from all trust bundles
  oc adm ocp-certificates remove-old-trust configmaps -A --all --created-before 2023-06-05T14:44:06Z
```

#### 2.7.1.30. oc adm ocp-certificates update-ignition-ca-bundle-for-machine-config-server

업데이트된 MCO certfs를 사용하도록 OpenShift 클러스터에서 user-data 시크릿 업데이트

```bash
# Regenerate the MCO certs without modifying user-data secrets
  oc adm ocp-certificates regenerate-machine-config-server-serving-cert --update-ignition=false

  # Update the user-data secrets to use new MCS certs
  oc adm ocp-certificates update-ignition-ca-bundle-for-machine-config-server
```

#### 2.7.1.31. oc adm policy add-cluster-role-to-group

클러스터의 모든 프로젝트에 대한 그룹에 역할을 추가

```bash
# Add the 'cluster-admin' cluster role to the 'cluster-admins' group
  oc adm policy add-cluster-role-to-group cluster-admin cluster-admins
```

#### 2.7.1.32. oc adm policy add-cluster-role-to-user

클러스터의 모든 프로젝트에 대한 사용자에게 역할 추가

```bash
# Add the 'system:build-strategy-docker' cluster role to the 'devuser' user
  oc adm policy add-cluster-role-to-user system:build-strategy-docker devuser
```

#### 2.7.1.33. oc adm policy add-role-to-user

현재 프로젝트의 사용자 또는 서비스 계정에 역할을 추가

```bash
# Add the 'view' role to user1 for the current project
  oc adm policy add-role-to-user view user1

  # Add the 'edit' role to serviceaccount1 for the current project
  oc adm policy add-role-to-user edit -z serviceaccount1
```

#### 2.7.1.34. oc adm policy add-scc-to-group

그룹에 보안 컨텍스트 제한 조건 추가

```bash
# Add the 'restricted' security context constraint to group1 and group2
  oc adm policy add-scc-to-group restricted group1 group2
```

#### 2.7.1.35. oc adm policy add-scc-to-user

사용자 또는 서비스 계정에 보안 컨텍스트 제약 조건 추가

```bash
# Add the 'restricted' security context constraint to user1 and user2
  oc adm policy add-scc-to-user restricted user1 user2

  # Add the 'privileged' security context constraint to serviceaccount1 in the current namespace
  oc adm policy add-scc-to-user privileged -z serviceaccount1
```

#### 2.7.1.36. oc adm policy remove-cluster-role-from-group

클러스터의 모든 프로젝트에 대한 그룹에서 역할 제거

```bash
# Remove the 'cluster-admin' cluster role from the 'cluster-admins' group
  oc adm policy remove-cluster-role-from-group cluster-admin cluster-admins
```

#### 2.7.1.37. oc adm policy remove-cluster-role-from-user

클러스터의 모든 프로젝트에 대한 사용자에서 역할 제거

```bash
# Remove the 'system:build-strategy-docker' cluster role from the 'devuser' user
  oc adm policy remove-cluster-role-from-user system:build-strategy-docker devuser
```

#### 2.7.1.38. oc adm policy scc-review

Pod를 생성할 수 있는 서비스 계정을 확인

```bash
# Check whether service accounts sa1 and sa2 can admit a pod with a template pod spec specified in my_resource.yaml
  # Service Account specified in myresource.yaml file is ignored
  oc adm policy scc-review -z sa1,sa2 -f my_resource.yaml

  # Check whether service accounts system:serviceaccount:bob:default can admit a pod with a template pod spec specified in my_resource.yaml
  oc adm policy scc-review -z system:serviceaccount:bob:default -f my_resource.yaml

  # Check whether the service account specified in my_resource_with_sa.yaml can admit the pod
  oc adm policy scc-review -f my_resource_with_sa.yaml

  # Check whether the default service account can admit the pod; default is taken since no service account is defined in myresource_with_no_sa.yaml
  oc adm policy scc-review -f myresource_with_no_sa.yaml
```

#### 2.7.1.39. oc adm policy scc-subject-review

사용자 또는 서비스 계정의 Pod 생성 가능 여부 확인

```bash
# Check whether user bob can create a pod specified in myresource.yaml
  oc adm policy scc-subject-review -u bob -f myresource.yaml

  # Check whether user bob who belongs to projectAdmin group can create a pod specified in myresource.yaml
  oc adm policy scc-subject-review -u bob -g projectAdmin -f myresource.yaml

  # Check whether a service account specified in the pod template spec in myresourcewithsa.yaml can create the pod
  oc adm policy scc-subject-review -f myresourcewithsa.yaml
```

#### 2.7.1.40. oc adm prune 빌드

이전 빌드 및 실패한 빌드 삭제

```bash
# Dry run deleting older completed and failed builds and also including
  # all builds whose associated build config no longer exists
  oc adm prune builds --orphans

  # To actually perform the prune operation, the confirm flag must be appended
  oc adm prune builds --orphans --confirm
```

#### 2.7.1.41. oc adm prune deployment

이전 완료 및 실패한 배포 구성 제거

```bash
# Dry run deleting all but the last complete deployment for every deployment config
  oc adm prune deployments --keep-complete=1

  # To actually perform the prune operation, the confirm flag must be appended
  oc adm prune deployments --keep-complete=1 --confirm
```

#### 2.7.1.42. oc adm prune groups

외부 공급자에서 누락된 레코드를 참조하는 이전 OpenShift 그룹 제거

```bash
# Prune all orphaned groups
  oc adm prune groups --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Prune all orphaned groups except the ones from the denylist file
  oc adm prune groups --blacklist=/path/to/denylist.txt --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Prune all orphaned groups from a list of specific groups specified in an allowlist file
  oc adm prune groups --whitelist=/path/to/allowlist.txt --sync-config=/path/to/ldap-sync-config.yaml --confirm

  # Prune all orphaned groups from a list of specific groups specified in a list
  oc adm prune groups groups/group_name groups/other_name --sync-config=/path/to/ldap-sync-config.yaml --confirm
```

#### 2.7.1.43. oc adm prune images

권장되지 않은 이미지 제거

```bash
# See what the prune command would delete if only images and their referrers were more than an hour old
  # and obsoleted by 3 newer revisions under the same tag were considered
  oc adm prune images --keep-tag-revisions=3 --keep-younger-than=60m

  # To actually perform the prune operation, the confirm flag must be appended
  oc adm prune images --keep-tag-revisions=3 --keep-younger-than=60m --confirm

  # See what the prune command would delete if we are interested in removing images
  # exceeding currently set limit ranges ('openshift.io/Image')
  oc adm prune images --prune-over-size-limit

  # To actually perform the prune operation, the confirm flag must be appended
  oc adm prune images --prune-over-size-limit --confirm

  # Force the insecure HTTP protocol with the particular registry host name
  oc adm prune images --registry-url=http://registry.example.org --confirm

  # Force a secure connection with a custom certificate authority to the particular registry host name
  oc adm prune images --registry-url=registry.example.org --certificate-authority=/path/to/custom/ca.crt --confirm
```

#### 2.7.1.44. oc adm prune renderedmachineconfigs

OpenShift 클러스터에서 렌더링된 MachineConfigs 정리

```bash
# See what the prune command would delete if run with no options
  oc adm prune renderedmachineconfigs

  # To actually perform the prune operation, the confirm flag must be appended
  oc adm prune renderedmachineconfigs --confirm

  # See what the prune command would delete if run on the worker MachineConfigPool
  oc adm prune renderedmachineconfigs --pool-name=worker

  # Prunes 10 oldest rendered MachineConfigs in the cluster
  oc adm prune renderedmachineconfigs --count=10 --confirm

  # Prunes 10 oldest rendered MachineConfigs in the cluster for the worker MachineConfigPool
  oc adm prune renderedmachineconfigs --count=10 --pool-name=worker --confirm
```

#### 2.7.1.45. oc adm prune renderedmachineconfigs list

OpenShift 클러스터에서 렌더링된 MachineConfig 나열

```bash
# List all rendered MachineConfigs for the worker MachineConfigPool in the cluster
  oc adm prune renderedmachineconfigs list --pool-name=worker

  # List all rendered MachineConfigs in use by the cluster's MachineConfigPools
  oc adm prune renderedmachineconfigs list --in-use
```

#### 2.7.1.46. oc adm reboot-machine-config-pool

지정된 MachineConfigPool의 재부팅을 시작합니다.

```bash
# Reboot all MachineConfigPools
  oc adm reboot-machine-config-pool mcp/worker mcp/master

  # Reboot all MachineConfigPools that inherit from worker.  This include all custom MachineConfigPools and infra.
  oc adm reboot-machine-config-pool mcp/worker

  # Reboot masters
  oc adm reboot-machine-config-pool mcp/master
```

#### 2.7.1.47. oc adm release extract

업데이트 페이로드 내용을 디스크에 추출

```bash
# Use git to check out the source code for the current cluster release to DIR
  oc adm release extract --git=DIR

  # Extract cloud credential requests for AWS
  oc adm release extract --credentials-requests --cloud=aws

  # Use git to check out the source code for the current cluster release to DIR from linux/s390x image
  # Note: Wildcard filter is not supported; pass a single os/arch to extract
  oc adm release extract --git=DIR quay.io/openshift-release-dev/ocp-release:4.11.2 --filter-by-os=linux/s390x
```

#### 2.7.1.48. oc adm release info

릴리스에 대한 정보 표시

```bash
# Show information about the cluster's current release
  oc adm release info

  # Show the source code that comprises a release
  oc adm release info 4.11.2 --commit-urls

  # Show the source code difference between two releases
  oc adm release info 4.11.0 4.11.2 --commits

  # Show where the images referenced by the release are located
  oc adm release info quay.io/openshift-release-dev/ocp-release:4.11.2 --pullspecs

  # Show information about linux/s390x image
  # Note: Wildcard filter is not supported; pass a single os/arch to extract
  oc adm release info quay.io/openshift-release-dev/ocp-release:4.11.2 --filter-by-os=linux/s390x
```

#### 2.7.1.49. oc adm release mirror

다른 이미지 레지스트리 위치에 릴리스 미러링

```bash
# Perform a dry run showing what would be mirrored, including the mirror objects
  oc adm release mirror 4.11.0 --to myregistry.local/openshift/release \
  --release-image-signature-to-dir /tmp/releases --dry-run

  # Mirror a release into the current directory
  oc adm release mirror 4.11.0 --to file://openshift/release \
  --release-image-signature-to-dir /tmp/releases

  # Mirror a release to another directory in the default location
  oc adm release mirror 4.11.0 --to-dir /tmp/releases

  # Upload a release from the current directory to another server
  oc adm release mirror --from file://openshift/release --to myregistry.com/openshift/release \
  --release-image-signature-to-dir /tmp/releases

  # Mirror the 4.11.0 release to repository registry.example.com and apply signatures to connected cluster
  oc adm release mirror --from=quay.io/openshift-release-dev/ocp-release:4.11.0-x86_64 \
  --to=registry.example.com/your/repository --apply-release-image-signature
```

#### 2.7.1.50. oc adm release new

새 OpenShift 릴리스 생성

```bash
# Create a release from the latest origin images and push to a DockerHub repository
  oc adm release new --from-image-stream=4.11 -n origin --to-image docker.io/mycompany/myrepo:latest

  # Create a new release with updated metadata from a previous release
  oc adm release new --from-release registry.ci.openshift.org/origin/release:v4.11 --name 4.11.1 \
  --previous 4.11.0 --metadata ... --to-image docker.io/mycompany/myrepo:latest

  # Create a new release and override a single image
  oc adm release new --from-release registry.ci.openshift.org/origin/release:v4.11 \
  cli=docker.io/mycompany/cli:latest --to-image docker.io/mycompany/myrepo:latest

  # Run a verification pass to ensure the release can be reproduced
  oc adm release new --from-release registry.ci.openshift.org/origin/release:v4.11
```

#### 2.7.1.51. oc adm restart-kubelet

지정된 노드에서 kubelet 재시작

```bash
# Restart all the nodes, 10% at a time
  oc adm restart-kubelet nodes --all --directive=RemoveKubeletKubeconfig

  # Restart all the nodes, 20 nodes at a time
  oc adm restart-kubelet nodes --all --parallelism=20 --directive=RemoveKubeletKubeconfig

  # Restart all the nodes, 15% at a time
  oc adm restart-kubelet nodes --all --parallelism=15% --directive=RemoveKubeletKubeconfig

  # Restart all the masters at the same time
  oc adm restart-kubelet nodes -l node-role.kubernetes.io/master --parallelism=100% --directive=RemoveKubeletKubeconfig
```

#### 2.7.1.52. oc adm taint

하나 이상의 노드에서 테인트를 업데이트

```bash
# Update node 'foo' with a taint with key 'dedicated' and value 'special-user' and effect 'NoSchedule'
  # If a taint with that key and effect already exists, its value is replaced as specified
  oc adm taint nodes foo dedicated=special-user:NoSchedule

  # Remove from node 'foo' the taint with key 'dedicated' and effect 'NoSchedule' if one exists
  oc adm taint nodes foo dedicated:NoSchedule-

  # Remove from node 'foo' all the taints with key 'dedicated'
  oc adm taint nodes foo dedicated-

  # Add a taint with key 'dedicated' on nodes having label myLabel=X
  oc adm taint node -l myLabel=X  dedicated=foo:PreferNoSchedule

  # Add to node 'foo' a taint with key 'bar' and no value
  oc adm taint nodes foo bar:NoSchedule
```

#### 2.7.1.53. oc adm top images

이미지에 대한 사용량 통계 표시

```bash
# Show usage statistics for images
  oc adm top images
```

#### 2.7.1.54. oc adm top imagestreams

이미지 스트림에 대한 사용량 통계 표시

```bash
# Show usage statistics for image streams
  oc adm top imagestreams
```

#### 2.7.1.55. oc adm top node

노드의 리소스 (CPU/memory) 사용 표시

```bash
# Show metrics for all nodes
  oc adm top node

  # Show metrics for a given node
  oc adm top node NODE_NAME
```

#### 2.7.1.56. oc adm top persistentvolumeclaims

실험적: 바인딩된 persistentvolumeclaims에 대한 사용량 통계 표시

```bash
# Show usage statistics for all the bound persistentvolumeclaims across the cluster
  oc adm top persistentvolumeclaims -A

  # Show usage statistics for all the bound persistentvolumeclaims in a specific namespace
  oc adm top persistentvolumeclaims -n default

  # Show usage statistics for specific bound persistentvolumeclaims
  oc adm top persistentvolumeclaims database-pvc app-pvc -n default
```

#### 2.7.1.57. oc adm top pod

Pod의 리소스(CPU/메모리) 사용 표시

```bash
# Show metrics for all pods in the default namespace
  oc adm top pod

  # Show metrics for all pods in the given namespace
  oc adm top pod --namespace=NAMESPACE

  # Show metrics for a given pod and its containers
  oc adm top pod POD_NAME --containers

  # Show metrics for the pods defined by label name=myLabel
  oc adm top pod -l name=myLabel
```

#### 2.7.1.58. oc adm uncordon

노드를 예약 가능으로 표시

```bash
# Mark node "foo" as schedulable
  oc adm uncordon foo
```

#### 2.7.1.59. oc adm upgrade

클러스터 업그레이드 또는 업그레이드 채널 조정

```bash
# View the update status and available cluster updates
  oc adm upgrade

  # Update to the latest version
  oc adm upgrade --to-latest=true
```

#### 2.7.1.60. oc adm verify-image-signature

이미지 서명에 포함된 이미지 ID 확인

```bash
# Verify the image signature and identity using the local GPG keychain
  oc adm verify-image-signature sha256:c841e9b64e4579bd56c794bdd7c36e1c257110fd2404bebbb8b613e4935228c4 \
  --expected-identity=registry.local:5000/foo/bar:v1

  # Verify the image signature and identity using the local GPG keychain and save the status
  oc adm verify-image-signature sha256:c841e9b64e4579bd56c794bdd7c36e1c257110fd2404bebbb8b613e4935228c4 \
  --expected-identity=registry.local:5000/foo/bar:v1 --save

  # Verify the image signature and identity via exposed registry route
  oc adm verify-image-signature sha256:c841e9b64e4579bd56c794bdd7c36e1c257110fd2404bebbb8b613e4935228c4 \
  --expected-identity=registry.local:5000/foo/bar:v1 \
  --registry-url=docker-registry.foo.com

  # Remove all signature verifications from the image
  oc adm verify-image-signature sha256:c841e9b64e4579bd56c794bdd7c36e1c257110fd2404bebbb8b613e4935228c4 --remove-all
```

#### 2.7.1.61. oc adm wait-for-node-reboot

다음 명령을 실행한 후 노드가 재부팅될 때까지 기다립니다.

```shell
oc adm reboot-machine-config-pool
```

```bash
# Wait for all nodes to complete a requested reboot from 'oc adm reboot-machine-config-pool mcp/worker mcp/master'
  oc adm wait-for-node-reboot nodes --all

  # Wait for masters to complete a requested reboot from 'oc adm reboot-machine-config-pool mcp/master'
  oc adm wait-for-node-reboot nodes -l node-role.kubernetes.io/master

  # Wait for masters to complete a specific reboot
  oc adm wait-for-node-reboot nodes -l node-role.kubernetes.io/master --reboot-number=4
```

#### 2.7.1.62. oc adm wait-for-stable-cluster

플랫폼 운영자가 안정될 때까지 기다립니다.

```bash
# Wait for all cluster operators to become stable
  oc adm wait-for-stable-cluster

  # Consider operators to be stable if they report as such for 5 minutes straight
  oc adm wait-for-stable-cluster --minimum-stable-period 5m
```

#### 2.7.2. 추가 리소스

OpenShift CLI 개발자 명령 참조

### 3.1. CLI Manager Operator 개요

중요

CLI Manager Operator를 사용하여 OpenShift CLI용 플러그인을 설치 및 관리하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 3.1.1. CLI Manager Operator 정보

CLI Manager Operator를 사용하면 CLI 플러그인을 더 쉽게 설치하고 업데이트할 수 있습니다. 연결 및 연결이 끊긴 환경 모두에서 실행되며 연결이 끊긴 환경에서 특히 유용합니다. 클러스터 관리자는 CLI Manager Operator에 CLI 플러그인 및 플러그인 업데이트를 추가할 수 있으며 사용자는 환경 연결이 끊어졌는지 여부에 관계없이 필요한 경우 CLI 플러그인을 설치 및 업데이트할 수 있습니다.

### 3.2. CLI Manager Operator 릴리스 노트

CLI Manager Operator를 사용하면 연결된 환경 및 연결이 끊긴 환경 모두에 CLI 플러그인을 설치할 수 있습니다.

중요

CLI Manager Operator를 사용하여 OpenShift CLI용 플러그인을 설치 및 관리하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

이 릴리스 노트에서는 OpenShift Container Platform용 CLI Manager Operator의 개발을 추적합니다.

CLI Manager Operator에 대한 자세한 내용은 CLI Manager Operator 정보를 참조하십시오.

#### 3.2.1. CLI Manager Operator 0.2.0 (기술 프리뷰)

출시 날짜: 2025년 12월 9일

CLI Manager Operator 0.2.0에 대해 다음 권고를 사용할 수 있습니다.

RHBA-2025:22803

#### 3.2.1.1. 새로운 기능 및 개선 사항

이번 CLI Manager Operator 릴리스는 Kubernetes 버전을 1.34로 업데이트합니다.

OpenShift Container Platform Pod를 추가로 강화하기 위해 `readOnlyRootFilesystem` 플래그가 `true` 로 설정됩니다.

#### 3.2.2. CLI Manager Operator 0.1.1 (기술 프리뷰)

출시 날짜: 2025년 3월 12일

CLI Manager Operator 0.1.1에 대해 다음 권고를 사용할 수 있습니다.

RHEA-2025:2680

#### 3.2.2.1. 새로운 기능 및 개선 사항

이번 CLI Manager 릴리스는 Kubernetes 버전을 1.32로 업데이트합니다.

#### 3.2.3. CLI Manager Operator 0.1.0 (기술 프리뷰)

출시 날짜: 2024년 11월 19일

CLI Manager Operator 0.1.0에 대해 다음 권고를 사용할 수 있습니다.

RHEA-2024:8303

#### 3.2.3.1. 새로운 기능 및 개선 사항

이 버전은 CLI Manager Operator의 초기 기술 프리뷰 릴리스입니다. 설치 정보는 CLI Manager Operator 설치를 참조하십시오.

### 3.3. CLI Manager Operator 설치

참고

Krew는 CLI Manager Operator를 설치하지 않고 항상 OpenShift CLI()에서 작동합니다. 이 문서에 설명된 것과 동일한 명령을 사용하여 다음 명령과 함께 Krew를 사용할 수 있습니다. 자세한 내용은 Krew 설명서를 참조하십시오.

```shell
oc
```

```shell
oc
```

연결된 환경과 연결이 끊긴 환경 모두에서 CLI Manager Operator를 실행할 수 있습니다. 특히 연결이 끊긴 환경에서 CLI 플러그인을 쉽게 설치하고 관리할 수 있습니다. CLI Manager Operator를 사용하면 Krew가 CLI와 호환됩니다. 클러스터 관리자는 CLI Manager Operator를 사용하여 연결된 환경 및 연결이 끊긴 환경에서 액세스할 수 있는 CLI 플러그인 사용자 정의 리소스를 추가할 수 있습니다. 클러스터 관리자는 CLI Manager Operator를 설치하고 구성한 다음 사용자는 사용자 정의 인덱스를 Krew에 추가하고 CLI Manager Operator에 CLI 플러그인을 추가합니다.

```shell
oc
```

중요

CLI Manager Operator를 사용하여 OpenShift CLI용 플러그인을 설치 및 관리하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 3.3.1. CLI Manager Operator 설치

CLI Manager Operator를 설치하여 연결된 환경 및 연결이 끊긴 환경 모두에 CLI 플러그인을 쉽게 추가할 수 있습니다.

사전 요구 사항

Krew가 설치되어 있습니다.

`cluster-admin` 역할의 사용자로 OpenShift Container Platform에 로그인되어 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

CLI Manager Operator에 필요한 네임스페이스를 생성합니다.

관리 → 네임스페이스 로 이동하여 네임스페이스 생성 을 클릭합니다.

이름 필드에 `openshift-cli-manager-operator` 를 입력하고 생성 을 클릭합니다.

CLI Manager Operator를 설치합니다.

에코시스템 → 소프트웨어 카탈로그 로 이동합니다.

필터 상자에 CLI Manager Operator 를 입력합니다.

CLI Manager Operator 를 선택하고 설치를 클릭합니다.

Operator 설치 페이지에서 다음 단계를 완료합니다.

Update 채널이 CLI Manager Operator의 최신 기술 프리뷰 릴리스를 설치하는 기술 프리뷰로 설정되어 있는지 확인합니다.

드롭다운 메뉴에서 클러스터의 특정 네임스페이스를 선택하고 openshift-cli-manager-operator 를 선택합니다.

설치 를 클릭합니다.

다음 단계를 완료하여 `CliManager` 리소스를 생성합니다.

설치된 Operator로 이동합니다.

CLI Manager Operator 를 선택합니다.

CLI Manager 탭을 선택합니다.

CliManager 생성을 클릭합니다.

기본 이름을 사용합니다.

생성 을 클릭합니다.

새로운 `CliManager` 리소스는 CLI Manager 탭에 나열됩니다.

검증

Ecosystem → 설치된 Operators 로 이동합니다.

CLI Manager Operator 가 성공

상태 로 나열되어 있는지 확인합니다.

#### 3.3.2. Krew에 CLI Manager Operator 사용자 정의 인덱스 추가

터미널을 사용하여 CLI 관리자 사용자 정의 인덱스를 Krew에 추가할 수 있습니다. CLI Manager Operator가 제대로 작동하려면 다음 절차가 필요하며 한 번만 수행해야 합니다.

사용자 정의 인덱스는 Krew를 CLI Manager Operator 바이너리에 연결하고 CLI Manager Operator가 연결이 끊긴 환경에서 작업할 수 있도록 합니다.

참고

자체 서명된 인증서를 사용하는 경우 인증서를 로컬 운영 체제에서 신뢰할 수 있는 것으로 표시하여 Krew를 사용합니다.

사전 요구 사항

Krew가 설치되어 있습니다.

CLI Manager Operator가 설치되어 있습니다.

프로세스

`ROUTE` 변수를 설정하려면 다음 명령을 입력합니다.

```shell-session
$ ROUTE=$(oc get route/openshift-cli-manager -n openshift-cli-manager-operator -o=jsonpath='{.spec.host}')
```

Krew에 사용자 정의 인덱스를 추가하려면 다음 명령을 입력합니다.

```shell-session
$ oc krew index add <custom_index_name> https://$ROUTE/cli-manager
```

Krew를 업데이트하려면 다음 명령을 입력하고 오류를 확인합니다.

```shell-session
$ oc krew update
```

```shell-session
Updated the local copy of plugin index.
Updated the local copy of plugin index <custom_index_name>.
New plugins available:
* ocp/<plugin_name>
```

#### 3.3.3. CLI Manager Operator에 플러그인 추가

YAML 보기를 사용하여 CLI Manager Operator에 CLI 플러그인을 추가할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform에 로그인되어 있습니다.

CLI Manager Operator가 설치되어 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

Ecosystem → 설치된 Operators 로 이동합니다.

목록에서 CLI Manager Operator 를 선택합니다.

CLI 플러그인 탭을 선택합니다.

플러그인 생성 을 클릭합니다.

텍스트 상자에 설치 중인 플러그인에 대한 정보를 입력합니다. 다음 예제 YAML 파일을 참조하십시오.

```yaml
apiVersion: config.openshift.io/v1alpha1
kind: Plugin
metadata:
  name: <plugin_name>
spec:
  description: <description_of_plugin>
  homepage: <plugin_homepage>
  platforms:
  - bin:
    files:
    - from: <plugin_file_path>
      to: .
    image: <plugin_image>
    imagePullSecret:
    platform: <platform>
  shortDescription: <short_description_of_plugin>
  version: <version>
```

1. 명령에서 사용할 플러그인의 이름입니다.

2. `bin` 은 플러그인 실행 파일의 경로를 지정합니다.

3. 선택 사항: 레지스트리가 공용이 아닌 경우 플러그인 이미지에 액세스할 수 있는 풀 시크릿을 추가합니다.

4. 시스템의 아키텍처(예: `linux/amd64`, `darwin/arm64`, `windows/amd64`) 또는 다른 아키텍처를 추가합니다.

5. 버전은 v0.0.0 형식이어야 합니다.

저장 을 클릭합니다.

검증

다음 명령을 입력하여 플러그인이 나열되었으며 성공적으로 추가되었는지 확인합니다.

```shell-session
$ oc get plugin/<plugin_name> -o yaml
```

```shell-session
<plugin_name> ready to be served.
```

### 3.4. CLI Manager Operator 사용

클러스터 관리자가 CLI Manager Operator를 설정하고 구성한 후 사용자는 CLI 플러그인을 설치, 업데이트 및 제거할 수 있습니다.

중요

CLI Manager Operator를 사용하여 OpenShift CLI용 플러그인을 설치 및 관리하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 3.4.1. CLI Manager Operator를 사용하여 CLI 플러그인 설치

CLI Manager Operator를 사용하여 CLI 플러그인을 설치할 수 있습니다.

사전 요구 사항

Krew 문서의 설치 절차 에 따라 Krew를 설치했습니다.

CLI Manager가 설치되어 있어야 합니다.

CLI Manager 사용자 정의 인덱스가 Krew에 추가되었습니다.

OpenShift Container Platform 4.17 이상을 사용하고 있습니다.

프로세스

사용 가능한 모든 플러그인을 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc krew search
```

플러그인에 대한 정보를 얻으려면 다음 명령을 실행합니다.

```shell-session
$ oc krew info <plugin_name>
```

플러그인을 설치하려면 다음 명령을 실행합니다.

```shell-session
$ oc krew install <plugin_name>
```

Krew가 설치한 모든 플러그인을 나열하려면 다음 명령을 실행합니다.

```shell-session
$ oc krew list
```

#### 3.4.2. CLI Manager Operator를 사용하여 플러그인 업그레이드

CLI Manager Operator를 사용하여 CLI 플러그인을 최신 버전으로 업그레이드할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform에 로그인되어 있습니다.

CLI Manager Operator가 설치되어 있습니다.

업그레이드 중인 플러그인이 설치되어 있습니다.

프로세스

CLI를 사용하여 다음 명령을 입력합니다.

```shell-session
oc edit plugin/<plugin_name>
```

플러그인의 새 사양을 포함하도록 YAML 파일을 편집합니다.

```yaml
apiVersion: config.openshift.io/v1alpha1
kind: Plugin
metadata:
  name: <plugin_name>
spec:
  description: <description_of_plugin>
  homepage: <plugin_homepage>
  platforms:
  - bin:
    files:
    - from: <plugin_file_path>
      to: .
    image: <plugin_image>
    imagePullSecret:
    platform: <platform>
  shortDescription: <short_description_of_plugin>
  version: <version>
```

1. 명령에서 사용할 플러그인의 이름입니다.

2. `bin` 은 플러그인 실행 파일의 경로를 지정합니다.

3. 선택 사항: 레지스트리가 공용이 아닌 경우 플러그인 이미지에 액세스할 수 있는 풀 시크릿을 추가합니다.

4. 시스템 플랫폼의 아키텍처를 추가합니다(예: `linux/amd64`, `darwin/arm64`, `windows/amd64`) 또는 다른 아키텍처.

5. v0.0.0 형식의 플러그인 버전입니다.

파일을 저장합니다.

#### 3.4.3. CLI Manager Operator를 사용하여 CLI 플러그인 업데이트

CLI Manager Operator를 사용하여 OpenShift CLI()용으로 설치된 플러그인을 업데이트할 수 있습니다.

```shell
oc
```

사전 요구 사항

Krew 문서의 설치 절차 에 따라 Krew를 설치했습니다.

CLI Manager Operator가 설치되어 있습니다.

클러스터 관리자가 Krew에 사용자 지정 인덱스가 추가되었습니다.

클러스터 관리자가 CLI Manager Operator에 플러그인 업데이트가 추가되었습니다.

업데이트 중인 플러그인이 이미 설치되어 있습니다.

프로세스

단일 플러그인을 업데이트하려면 다음 명령을 실행합니다.

```shell-session
$ oc krew upgrade <plugin_name>
```

Krew가 설치한 모든 플러그인을 업데이트하려면 다음 명령을 실행합니다.

```shell-session
$ oc krew upgrade
```

#### 3.4.4. CLI Manager Operator를 사용하여 CLI 플러그인 설치 제거

CLI Manager Operator를 사용하여 OpenShift CLI()용으로 설치된 플러그인을 설치 제거할 수 있습니다.

```shell
oc
```

사전 요구 사항

Krew 문서의 설치 절차 에 따라 Krew를 설치했습니다.

CLI Manager Operator를 사용하여 OpenShift CLI용 플러그인을 설치했습니다.

프로세스

플러그인을 설치 제거하려면 다음 명령을 실행합니다.

```shell-session
$ oc krew uninstall <plugin_name>
```

### 3.5. CLI Manager Operator 설치 제거

CLI Manager Operator를 설치 제거하고 관련 리소스를 제거하여 OpenShift Container Platform에서 CLI Manager Operator를 제거할 수 있습니다.

중요

CLI Manager Operator를 사용하여 OpenShift CLI용 플러그인을 설치 및 관리하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 3.5.1. CLI Manager Operator 설치 제거

웹 콘솔을 사용하여 CLI Manager Operator를 설치 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform에 로그인되어 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

CLI Manager Operator가 설치되어 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

다음 단계를 완료하여 CLI Manager Operator를 설치 제거합니다.

Ecosystem → 설치된 Operators 로 이동합니다.

CLI Manager Operator 항목 옆에 있는 옵션 메뉴

를 클릭하고 Operator 설치 제거를 클릭합니다.

확인 대화 상자에서 설치 제거 를 클릭합니다.

#### 3.5.2. CLI Manager Operator 리소스 제거

CLI Manager Operator를 설치 제거한 후 선택적으로 클러스터에서 관련 리소스를 제거할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 OpenShift Container Platform에 로그인되어 있습니다.

OpenShift Container Platform 웹 콘솔에 액세스할 수 있습니다.

프로세스

OpenShift Container Platform 웹 콘솔에 로그인합니다.

`openshift-cli-manager-operator` 네임스페이스를 제거합니다.

관리 → 네임스페이스 로 이동합니다.

openshift-cli-manager-operator 항목 옆에 있는 옵션 메뉴

를 클릭하고 네임스페이스 삭제 를 선택합니다.

확인 대화 상자에서 필드에 `openshift-cli-manager-operator` 를 입력하고 삭제 를 클릭합니다.

## 4장. odo에서 중요한 업데이트

Red Hat은 OpenShift Container Platform 설명서 사이트에서 `odo` 에 대한 정보를 제공하지 않습니다. `odo` 와 관련된 문서 정보는 Red Hat에서 유지 관리하는 문서 및 업스트림 커뮤니티에서 참조하십시오.

중요

업스트림 커뮤니티에서 유지 관리하는 자료의 경우 Red Hat은 협력 커뮤니티 지원에 따라 지원을 제공합니다.

## 5장. OpenShift Serverless와 함께 사용할 Knative CLI

Knative(`kn`) CLI를 사용하면 OpenShift Container Platform에서 Knative 구성 요소와 간단한 상호 작용을 수행할 수 있습니다.

### 5.1. 주요 기능

Knative(`kn`) CLI는 서버리스 컴퓨팅 작업을 간단하고 간결하게 제공하도록 설계되었습니다. Knative CLI의 주요 기능은 다음과 같습니다.

명령줄에서 서버리스 애플리케이션을 배포합니다.

서비스, 개정, 트래픽 분할 등 Knative Serving 기능을 관리합니다.

이벤트 소스 및 트리거와 같은 Knative 이벤트 구성 요소를 생성하고 관리합니다.

기존 Kubernetes 애플리케이션 및 Knative 서비스를 연결하는 싱크 바인딩을 생성합니다.

다음 명령CLI와 유사하게 유연한 플러그인 아키텍처를 사용하여 Knative CLI를 확장합니다.

```shell
kubectl
```

Knative 서비스에 대한 자동 스케일링 매개변수를 구성합니다.

작업 결과 대기나 사용자 정의 롤아웃 및 롤백 전략 배포와 같은 사용법을 스크립팅합니다.

### 5.2. Knative CLI 설치

Knative CLI 설치를 참조하십시오.

### 6.1. tkn 설치

CLI 툴을 사용하여 터미널에서 Red Hat OpenShift Pipelines를 관리합니다. 다음 섹션에서는 다른 플랫폼에 CLI 툴을 설치하는 방법을 설명합니다.

오른쪽 상단에 있는? 아이콘을 클릭하고 명령줄 툴 을 선택하여 OpenShift Container Platform 웹 콘솔의 최신 바이너리 URL을 찾을 수도 있습니다.

참고

아카이브와 RPM 모두에 다음과 같은 실행 파일이 포함되어 있습니다.

`tkn`

`tkn-pac`

`opc`

중요

`opc` CLI 툴을 사용하여 Red Hat OpenShift Pipelines를 실행하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 6.1.1. Linux에서 Red Hat OpenShift Pipelines CLI 설치

Linux 배포판의 경우 CLI를 아카이브로 다운로드할 수 있습니다.

```shell
tar.gz
```

프로세스

관련 CLI 툴을 다운로드합니다.

Linux (x86_64, amd64)

Linux on IBM Z® and IBM® LinuxONE (s390x)

Linux on IBM Power® (ppc64le)

Linux on ARM (aarch64, arm64)

아카이브의 압축을 풉니다.

```shell-session
$ tar xvzf <file>
```

tkn, `tkn -pac`, `opc` 파일의 위치를 `PATH` 환경 변수에 추가합니다.

`PATH` 를 확인하려면 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

#### 6.1.2. RPM을 사용하여 Linux에 Red Hat OpenShift Pipelines CLI 설치

RHEL(Red Hat Enterprise Linux) 버전 8의 경우 Red Hat OpenShift Pipelines CLI를 RPM으로 설치할 수 있습니다.

사전 요구 사항

Red Hat 계정에 활성 OpenShift Container Platform 서브스크립션이 있어야 합니다.

로컬 시스템에 root 또는 sudo 권한이 있어야 합니다.

프로세스

Red Hat Subscription Manager에 등록합니다.

```shell-session
# subscription-manager register
```

최신 서브스크립션 데이터를 가져옵니다.

```shell-session
# subscription-manager refresh
```

사용 가능한 서브스크립션을 나열하십시오.

```shell-session
# subscription-manager list --available --matches '*pipelines*'
```

이전 명령의 출력에서 OpenShift Container Platform 서브스크립션의 풀 ID를 찾아서 이 서브스크립션을 등록된 시스템에 연결합니다.

```shell-session
# subscription-manager attach --pool=<pool_id>
```

Red Hat OpenShift Pipelines에 필요한 리포지토리를 활성화합니다.

```shell-session
# subscription-manager repos --enable="pipelines-1.18-for-rhel-8-x86_64-rpms"
```

```shell-session
# subscription-manager repos --enable="pipelines-1.18-for-rhel-8-s390x-rpms"
```

```shell-session
# subscription-manager repos --enable="pipelines-1.18-for-rhel-8-ppc64le-rpms"
```

```shell-session
# subscription-manager repos --enable="pipelines-1.18-for-rhel-8-aarch64-rpms"
```

`openshift-pipelines-client` 패키지를 설치합니다.

```shell-session
# yum install openshift-pipelines-client
```

CLI를 설치한 후 `tkn` 명령을 사용할 수 있습니다.

```shell-session
$ tkn version
```

#### 6.1.3. Windows에서 Red Hat OpenShift Pipelines CLI 설치

Windows의 경우 CLI를 `zip` 아카이브로 다운로드할 수 있습니다.

프로세스

CLI 툴 을 다운로드합니다.

ZIP 프로그램으로 아카이브의 압축을 풉니다.

tkn, `tkn -pac`, `opc` 파일의 위치를 `PATH` 환경 변수에 추가합니다.

`PATH` 를 확인하려면 다음 명령을 실행합니다.

```shell-session
C:\> path
```

#### 6.1.4. macOS에서 Red Hat OpenShift Pipelines CLI 설치

macOS의 경우 CLI를 아카이브로 다운로드할 수 있습니다.

```shell
tar.gz
```

프로세스

관련 CLI 툴을 다운로드합니다.

macOS

macOS on ARM

아카이브의 압축을 해제하고 압축을 풉니다.

tkn, `tkn -pac`, `opc` 파일의 위치를 `PATH` 환경 변수에 추가합니다.

`PATH` 를 확인하려면 다음 명령을 실행합니다.

```shell-session
$ echo $PATH
```

### 6.2. OpenShift Pipelines tkn CLI 구성

탭 완료를 활성화하도록 Red Hat OpenShift Pipelines `tkn` CLI를 구성합니다.

#### 6.2.1. 탭 완료 활성화

`tkn` CLI를 설치한 후에는 탭 완료를 활성화하여 자동으로 `tkn` 명령을 완료하거나 탭을 누를 때 옵션을 제안하도록 할 수 있습니다.

사전 요구 사항

`tkn` CLI 툴이 설치되어 있어야 합니다.

로컬 시스템에 `bash-completion` 이 설치되어 있어야 합니다.

프로세스

Bash 탭 완료를 활성화하는 절차는 다음과 같습니다.

Bash 완료 코드를 파일에 저장합니다.

```shell-session
$ tkn completion bash > tkn_bash_completion
```

파일을 `/etc/bash_completion.d/` 에 복사합니다.

```shell-session
$ sudo cp tkn_bash_completion /etc/bash_completion.d/
```

또는 파일을 로컬 디렉터리에 저장하여 `.bashrc` 파일에서 소싱할 수도 있습니다.

새 터미널을 열면 탭 완료가 활성화됩니다.

### 6.3. OpenShift Pipelines tkn 참조

이 섹션에는 기본 `tkn` CLI 명령이 나열됩니다.

#### 6.3.1. 기본 구문

`tkn [command or options] [arguments…​]`

#### 6.3.2. 글로벌 옵션

`--help, -h`

#### 6.3.3.1. tkn

`tkn` CLI의 상위 명령입니다.

```shell-session
$ tkn
```

#### 6.3.3.2. completion [shell]

대화형 완료를 제공하려면 평가해야 하는 쉘 완료 코드를 출력합니다. 지원되는 쉘은 `bash` 및 `zsh` 입니다.

```shell-session
$ tkn completion bash
```

#### 6.3.3.3. version

`tkn` CLI의 버전 정보를 출력합니다.

```shell-session
$ tkn version
```

#### 6.3.4.1. pipeline

파이프라인을 관리합니다.

```shell-session
$ tkn pipeline --help
```

#### 6.3.4.2. pipeline delete

파이프라인을 삭제합니다.

```shell-session
$ tkn pipeline delete mypipeline -n myspace
```

#### 6.3.4.3. pipeline describe

파이프라인을 설명합니다.

```shell-session
$ tkn pipeline describe mypipeline
```

#### 6.3.4.4. pipeline list

파이프라인 목록을 표시합니다.

```shell-session
$ tkn pipeline list
```

#### 6.3.4.5. pipeline logs

특정 파이프라인의 로그를 표시합니다.

```shell-session
$ tkn pipeline logs -f mypipeline
```

#### 6.3.4.6. pipeline start

파이프라인을 시작합니다.

```shell-session
$ tkn pipeline start mypipeline
```

#### 6.3.5.1. pipelinerun

파이프라인 실행을 관리합니다.

```shell-session
$ tkn pipelinerun -h
```

#### 6.3.5.2. pipelinerun cancel

파이프라인 실행을 취소합니다.

```shell-session
$ tkn pipelinerun cancel mypipelinerun -n myspace
```

#### 6.3.5.3. pipelinerun delete

파이프라인 실행을 삭제합니다.

```shell-session
$ tkn pipelinerun delete mypipelinerun1 mypipelinerun2 -n myspace
```

```shell-session
$ tkn pipelinerun delete -n myspace --keep 5
```

1. `5` 를 유지하려는 가장 최근에 실행된 파이프라인 실행 수로 바꿉니다.

```shell-session
$ tkn pipelinerun delete --all
```

참고

Red Hat OpenShift Pipelines 1.6부터 `tkn pipelinerun delete --all` 명령은 running 상태인 리소스를 삭제하지 않습니다.

#### 6.3.5.4. pipelinerun describe

파이프라인 실행을 설명합니다.

```shell-session
$ tkn pipelinerun describe mypipelinerun -n myspace
```

#### 6.3.5.5. pipelinerun list

파이프라인 실행을 나열합니다.

```shell-session
$ tkn pipelinerun list -n myspace
```

#### 6.3.5.6. pipelinerun logs

파이프라인 실행 로그를 표시합니다.

```shell-session
$ tkn pipelinerun logs mypipelinerun -a -n myspace
```

#### 6.3.6.1. task

작업을 관리합니다.

```shell-session
$ tkn task -h
```

#### 6.3.6.2. task delete

작업을 삭제합니다.

```shell-session
$ tkn task delete mytask1 mytask2 -n myspace
```

#### 6.3.6.3. task describe

작업을 설명합니다.

```shell-session
$ tkn task describe mytask -n myspace
```

#### 6.3.6.4. task list

작업을 나열합니다.

```shell-session
$ tkn task list -n myspace
```

#### 6.3.6.5. task logs

작업 로그를 표시합니다.

```shell-session
$ tkn task logs mytask mytaskrun -n myspace
```

#### 6.3.6.6. task start

작업을 시작합니다.

```shell-session
$ tkn task start mytask -s <ServiceAccountName> -n myspace
```

#### 6.3.7.1. taskrun

작업 실행을 관리합니다.

```shell-session
$ tkn taskrun -h
```

#### 6.3.7.2. taskrun cancel

작업 실행을 취소합니다.

```shell-session
$ tkn taskrun cancel mytaskrun -n myspace
```

#### 6.3.7.3. taskrun delete

TaskRun을 삭제합니다.

```shell-session
$ tkn taskrun delete mytaskrun1 mytaskrun2 -n myspace
```

예: 네임스페이스에서 가장 최근에 실행한 5개의 작업을 모두 삭제합니다.

```shell-session
$ tkn taskrun delete -n myspace --keep 5
```

1. `5` 를 유지하려는 가장 최근에 실행된 작업 실행 수로 바꿉니다.

#### 6.3.7.4. taskrun describe

작업 실행을 설명합니다.

```shell-session
$ tkn taskrun describe mytaskrun -n myspace
```

#### 6.3.7.5. taskrun list

작업 실행을 나열합니다.

```shell-session
$ tkn taskrun list -n myspace
```

#### 6.3.7.6. taskrun logs

작업 실행 로그를 표시합니다.

```shell-session
$ tkn taskrun logs -f mytaskrun -n myspace
```

#### 6.3.8.1. condition

상태를 관리합니다.

```shell-session
$ tkn condition --help
```

#### 6.3.8.2. condition delete

상태를 삭제합니다.

```shell-session
$ tkn condition delete mycondition1 -n myspace
```

#### 6.3.8.3. condition describe

상태를 설명합니다.

```shell-session
$ tkn condition describe mycondition1 -n myspace
```

#### 6.3.8.4. condition list

상태를 나열합니다.

```shell-session
$ tkn condition list -n myspace
```

#### 6.3.9.1. resource

파이프라인 리소스를 관리합니다.

```shell-session
$ tkn resource -h
```

#### 6.3.9.2. resource create

파이프라인 리소스를 생성합니다.

```shell-session
$ tkn resource create -n myspace
```

이 명령은 리소스 이름, 리소스 유형, 리소스 유형 기반 값 입력을 요청하는 대화형 명령입니다.

#### 6.3.9.3. resource delete

파이프라인 리소스를 삭제합니다.

```shell-session
$ tkn resource delete myresource -n myspace
```

#### 6.3.9.4. resource describe

파이프라인 리소스를 설명합니다.

```shell-session
$ tkn resource describe myresource -n myspace
```

#### 6.3.9.5. resource list

파이프라인 리소스를 나열합니다.

```shell-session
$ tkn resource list -n myspace
```

#### 6.3.10. ClusterTask 관리 명령

중요

Red Hat OpenShift Pipelines 1.10, `tkn` 명령줄 유틸리티의 ClusterTask 기능은 더 이상 사용되지 않으며 향후 릴리스에서 제거될 예정입니다.

#### 6.3.10.1. clustertask

ClusterTask를 관리합니다.

```shell-session
$ tkn clustertask --help
```

#### 6.3.10.2. clustertask delete

클러스터의 ClusterTask 리소스를 삭제합니다.

```shell-session
$ tkn clustertask delete mytask1 mytask2
```

#### 6.3.10.3. clustertask describe

ClusterTask를 설명합니다.

```shell-session
$ tkn clustertask describe mytask1
```

#### 6.3.10.4. clustertask list

ClusterTask를 나열합니다.

```shell-session
$ tkn clustertask list
```

#### 6.3.10.5. clustertask start

ClusterTask를 시작합니다.

```shell-session
$ tkn clustertask start mytask
```

#### 6.3.11.1. eventlistener

EventListener를 관리합니다.

```shell-session
$ tkn eventlistener -h
```

#### 6.3.11.2. eventlistener delete

EventListener를 삭제합니다.

```shell-session
$ tkn eventlistener delete mylistener1 mylistener2 -n myspace
```

#### 6.3.11.3. eventlistener describe

EventListener를 설명합니다.

```shell-session
$ tkn eventlistener describe mylistener -n myspace
```

#### 6.3.11.4. eventlistener list

EventListener를 나열합니다.

```shell-session
$ tkn eventlistener list -n myspace
```

#### 6.3.11.5. eventlistener logs

EventListener 로그 표시

```shell-session
$ tkn eventlistener logs mylistener -n myspace
```

#### 6.3.11.6. triggerbinding

TriggerBinding을 관리합니다.

```shell-session
$ tkn triggerbinding -h
```

#### 6.3.11.7. triggerbinding delete

TriggerBinding을 삭제합니다.

```shell-session
$ tkn triggerbinding delete mybinding1 mybinding2 -n myspace
```

#### 6.3.11.8. triggerbinding describe

TriggerBinding을 설명합니다.

```shell-session
$ tkn triggerbinding describe mybinding -n myspace
```

#### 6.3.11.9. triggerbinding list

TriggerBinding을 나열합니다.

```shell-session
$ tkn triggerbinding list -n myspace
```

#### 6.3.11.10. triggertemplate

TriggerTemplate을 관리합니다.

```shell-session
$ tkn triggertemplate -h
```

#### 6.3.11.11. triggertemplate delete

TriggerTemplate을 삭제합니다.

```shell-session
$ tkn triggertemplate delete mytemplate1 mytemplate2 -n `myspace`
```

#### 6.3.11.12. triggertemplate describe

TriggerTemplate을 설명합니다.

```shell-session
$ tkn triggertemplate describe mytemplate -n `myspace`
```

#### 6.3.11.13. triggertemplate list

TriggerTemplate을 나열합니다.

```shell-session
$ tkn triggertemplate list -n myspace
```

#### 6.3.11.14. clustertriggerbinding

Manage ClusterTriggerBindings.

```shell-session
$ tkn clustertriggerbinding -h
```

#### 6.3.11.15. clustertriggerbinding delete

ClusterTriggerBinding을 삭제합니다.

```shell-session
$ tkn clustertriggerbinding delete myclusterbinding1 myclusterbinding2
```

#### 6.3.11.16. clustertriggerbinding describe

ClusterTriggerBinding을 설명합니다.

```shell-session
$ tkn clustertriggerbinding describe myclusterbinding
```

#### 6.3.11.17. clustertriggerbinding list

ClusterTriggerBinding을 나열합니다.

```shell-session
$ tkn clustertriggerbinding list
```

#### 6.3.12. Hub 상호 작용 명령

작업 및 파이프라인과 같은 리소스에 대해 Tekton Hub와 상호 작용합니다.

#### 6.3.12.1. hub

hub와 상호 작용.

```shell-session
$ tkn hub -h
```

```shell-session
$ tkn hub --api-server https://api.hub.tekton.dev
```

참고

각 예에서는 해당 하위 명령 및 플래그를 가져오려면 다음 명령을 실행합니다.

```shell
tkn hub <command> --help
```

#### 6.3.12.2. hub downgrade

설치된 리소스를 다운그레이드합니다.

```shell-session
$ tkn hub downgrade task mytask --to version -n mynamespace
```

#### 6.3.12.3. hub get

이름, 종류, 카탈로그, 버전 별로 리소스 매니페스트를 가져옵니다.

```shell-session
$ tkn hub get [pipeline | task] myresource --from tekton --version version
```

#### 6.3.12.4. hub info

이름, 종류, 카탈로그, 버전으로 리소스에 대한 정보를 표시합니다.

```shell-session
$ tkn hub info task mytask --from tekton --version version
```

#### 6.3.12.5. hub install

종류, 이름 및 버전으로 카탈로그에서 리소스를 설치합니다.

```shell-session
$ tkn hub install task mytask --from tekton --version version -n mynamespace
```

#### 6.3.12.6. hub reinstall

리소스 종류와 이름을 사용하여 리소스를 다시 설치합니다.

```shell-session
$ tkn hub reinstall task mytask --from tekton --version version -n mynamespace
```

#### 6.3.12.7. hub search

이름, 종류 및 태그의 조합으로 리소스를 검색합니다.

```shell-session
$ tkn hub search --tags cli
```

#### 6.3.12.8. hub upgrade

설치된 리소스를 업그레이드합니다.

```shell-session
$ tkn hub upgrade task mytask --to version -n mynamespace
```

## 7장. Red Hat OpenShift GitOps와 함께 사용할 GitOps CLI

GitOps `argocd` CLI는 터미널에서 Red Hat OpenShift GitOps 및 Argo CD 리소스를 구성하고 관리하는 툴입니다.

GitOps CLI를 사용하면 GitOps 컴퓨팅 작업을 간단하고 간결하게 만들 수 있습니다. 다른 플랫폼에 이 CLI 툴을 설치할 수 있습니다.

### 7.1. GitOps CLI 설치

GitOps CLI 설치를 참조하십시오.

### 7.2. 추가 리소스

GitOps란 무엇입니까?

#### 8.1.1. opm CLI 정보

`opm` CLI 툴은 Operator 번들 형식과 함께 사용할 수 있도록 Operator 프레임워크에서 제공합니다. 이 툴을 사용하면 소프트웨어 리포지토리와 유사한 Operator 번들 목록에서 Operator 카탈로그를 생성하고 유지 관리할 수 있습니다. 결과적으로 컨테이너 레지스트리에 저장한 다음 클러스터에 설치할 수 있는 컨테이너 이미지가 생성됩니다.

카탈로그에는 컨테이너 이미지가 실행될 때 제공되는 포함된 API를 통해 쿼리할 수 있는 Operator 매니페스트 콘텐츠에 대한 포인터 데이터베이스가 포함되어 있습니다. OpenShift Container Platform에서 OLM(Operator Lifecycle Manager)은 `CatalogSource` 오브젝트에서 정의한 카탈로그 소스의 이미지를 참조할 수 있으며 주기적으로 이미지를 폴링하여 클러스터에 설치된 Operator를 자주 업데이트할 수 있습니다.

추가 리소스

번들 형식에 대한 자세한 내용은 Operator 프레임워크 패키지 형식을 참조하십시오.

#### 8.1.2. opm CLI 설치

Linux, macOS 또는 Windows 워크스테이션에 `opm` CLI 툴을 설치할 수 있습니다.

사전 요구 사항

RHEL(Red Hat Enterprise Linux) 9.0 이상의 경우 다음 패키지를 제공해야 합니다.

```shell
podman
```

`glibc` 버전 2.28 이상

프로세스

OpenShift 미러 사이트로 이동하여 운영 체제와 일치하는 최신 버전의 tarball을 다운로드합니다.

아카이브의 압축을 풉니다.

```shell-session
$ tar xvf <file>
```

Windows의 경우 ZIP 프로그램으로 아카이브의 압축을 풉니다.

`PATH` 에 있는 임의의 위치에 파일을 배치합니다.

Linux 또는 macOS의 경우:

`PATH` 를 확인합니다.

```shell-session
$ echo $PATH
```

파일을 이동합니다. 예를 들면 다음과 같습니다.

```shell-session
$ sudo mv ./opm /usr/local/bin/
```

Windows의 경우:

`PATH` 를 확인합니다.

```shell-session
C:\> path
```

파일을 이동합니다.

```shell-session
C:\> move opm.exe <directory>
```

검증

`opm` CLI를 설치한 후 사용할 수 있는지 확인합니다.

```shell-session
$ opm version
```

#### 8.1.3. 추가 리소스

카탈로그 생성, 업데이트 및 정리를 포함한 `opm` 프로시저는 사용자 정의 카탈로그 관리를 참조하십시오.

### 8.2. opm CLI 참조

`opm` CLI(명령줄 인터페이스)는 Operator 카탈로그를 생성하고 유지 관리하는 툴입니다.

```shell-session
$ opm <command> [<subcommand>] [<argument>] [<flags>]
```

주의

`opm` CLI는 향후 버전과 호환되지 않습니다. 카탈로그 콘텐츠를 생성하는 데 사용되는 `opm` CLI 버전은 클러스터의 콘텐츠를 제공하는 데 사용되는 버전보다 작거나 같아야 합니다.

| 플래그 | 설명 |
| --- | --- |
| `-skip-tls-verify` | 번들 또는 인덱스를 가져오는 동안 컨테이너 이미지 레지스트리의 TLS 인증서 확인을 건너뜁니다. |
| `--use-http` | 번들을 가져올 때 컨테이너 이미지 레지스트리에 일반 HTTP를 사용합니다. |

중요

관련 CLI 명령을 포함한 SQLite 기반 카탈로그 형식은 더 이상 사용되지 않는 기능입니다. 더 이상 사용되지 않는 기능은 여전히 OpenShift Container Platform에 포함되어 있으며 계속 지원됩니다. 그러나 이 기능은 향후 릴리스에서 제거될 예정이므로 새로운 배포에는 사용하지 않는 것이 좋습니다.

OpenShift Container Platform에서 더 이상 사용되지 않거나 삭제된 주요 기능의 최신 목록은 OpenShift Container Platform 릴리스 노트에서 더 이상 사용되지 않고 삭제된 기능 섹션을 참조하십시오.

#### 8.2.1. generate

선언적 구성 인덱스에 대한 다양한 아티팩트를 생성합니다.

```shell-session
$ opm generate <subcommand> [<flags>]
```

| 하위 명령 | 설명 |
| --- | --- |
| `dockerfile` | 선언적 구성 인덱스에 대한 Dockerfile을 생성합니다. |

| 플래그 | 설명 |
| --- | --- |
| `-h` , `--help` | generate에 대한 도움말입니다. |

#### 8.2.1.1. dockerfile

선언적 구성 인덱스에 대한 Dockerfile을 생성합니다.

중요

이 명령은 인덱스를 빌드하는 데 사용되는 < `<dcRootDir>` (`<dcDirName>.Dockerfile` 로 이름 지정됨)과 동일한 디렉터리에 Dockerfile을 생성합니다. 동일한 이름의 Dockerfile이 이미 있는 경우 이 명령이 실패합니다.

추가 레이블을 지정할 때 중복 키가 있는 경우 각 중복 키의 마지막 값만 생성된 Dockerfile에 추가됩니다.

```shell-session
$ opm generate dockerfile <dcRootDir> [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-i,` `--binary-image` (문자열) | 카탈로그를 빌드할 이미지입니다. 기본값은 `quay.io/operator-framework/opm:latest` 입니다. |
| `-l` , `--extra-labels` (문자열) | 생성된 Dockerfile에 포함할 추가 레이블입니다. 레이블에는 `key=value` 형식이 있습니다. |
| `-h` , `--help` | Dockerfile에 대한 도움말입니다. |

참고

공식 Red Hat 이미지로 빌드하려면 `-i` 플래그와 함께 `registry.redhat.io/openshift4/ose-operator-registry-rhel9:v4.20` 값을 사용합니다.

#### 8.2.2. 인덱스

기존 Operator 번들에서 SQLite 데이터베이스 형식 컨테이너 이미지에 대한 Operator 인덱스를 생성합니다.

중요

OpenShift Container Platform 4.11부터 파일 기반 카탈로그 형식으로 기본 Red Hat 제공 Operator 카탈로그 릴리스입니다. 더 이상 사용되지 않는 SQLite 데이터베이스 형식으로 릴리스된 OpenShift Container Platform 4.6에 대한 기본 Red Hat 제공 Operator 카탈로그입니다.

SQLite 데이터베이스 형식과 관련된 `opm` 하위 명령, 플래그 및 기능은 더 이상 사용되지 않으며 향후 릴리스에서 제거됩니다. 이 기능은 계속 지원되며 더 이상 사용되지 않는 SQLite 데이터베이스 형식을 사용하는 카탈로그에 사용해야 합니다.

`opm index prune` 와 같은 SQLite 데이터베이스 형식을 사용하기 위한 `opm` 하위 명령 및 플래그는 파일 기반 카탈로그 형식에서는 작동하지 않습니다.

파일 기반 카탈로그 사용에 대한 자세한 내용은 "ECDHE 리소스"를 참조하십시오.

```shell-session
$ opm index <subcommand> [<flags>]
```

| 하위 명령 | 설명 |
| --- | --- |
| `add` | Operator 번들을 인덱스에 추가합니다. |
| `prune` | 지정된 패키지의 인덱스를 모두 정리합니다. |
| `prune-stranded` | 특정 이미지와 연결되지 않은 번들로 구성된 인덱스를 정리합니다. |
| `rm` | 인덱스에서 전체 Operator를 삭제합니다. |

#### 8.2.2.1. add

Operator 번들을 인덱스에 추가합니다.

```shell-session
$ opm index add [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-i` , `--binary-image` | on-image `opm` 명령의 컨테이너 이미지 |
| `-u` , `--build-tool` (문자열) | 컨테이너 이미지를 빌드하는 툴: `podman` (기본값) 또는 `docker` . `--container-tool` 플래그의 일부를 덮어씁니다. |
| `-b` , `--bundles` (문자열) | 쉼표로 구분된 추가할 번들 목록입니다. |
| `-c` , `--container-tool` (문자열) | 저장 및 빌드(예: `docker` 또는 `podman` )와 같은 컨테이너 이미지와 상호 작용하는 툴입니다. |
| `-f` , `--from-index` (문자열) | 추가할 이전 인덱스입니다. |
| `--generate` | 활성화된 경우 Dockerfile만 생성하여 로컬 디스크에 저장합니다. |
| `--mode` (문자열) | 채널 그래프 업데이트 방법을 정의하는 그래프 업데이트 모드 `replaces` (기본값), `semver` , 또는 `semver-skippatch` . |
| `-d` , `--out-dockerfile` (문자열) | 선택 사항: Dockerfile을 생성하는 경우 파일 이름을 지정합니다. |
| `--permissive` | 레지스트리 로드 오류를 허용합니다. |
| `-p` , `--pull-tool` (문자열) | 컨테이너 이미지를 가져오는 툴: `none` (기본값), `docker` 또는 `podman` . `--container-tool` 플래그의 일부를 덮어씁니다. |
| `-t` , `--tag` (문자열) | 빌드 중인 컨테이너 이미지에 대한 사용자 정의 태그입니다. |

#### 8.2.2.2. prune

지정된 패키지의 인덱스를 모두 정리합니다.

```shell-session
$ opm index prune [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-i` , `--binary-image` | on-image `opm` 명령의 컨테이너 이미지 |
| `-c` , `--container-tool` (문자열) | 저장 및 빌드(예: `docker` 또는 `podman` )와 같은 컨테이너 이미지와 상호 작용하는 툴입니다. |
| `-f` , `--from-index` (문자열) | 정리할 인덱스입니다. |
| `--generate` | 활성화된 경우 Dockerfile만 생성하여 로컬 디스크에 저장합니다. |
| `-d` , `--out-dockerfile` (문자열) | 선택 사항: Dockerfile을 생성하는 경우 파일 이름을 지정합니다. |
| `-p` , `--packages` (문자열) | 쉼표로 구분된 보관할 패키지 목록입니다. |
| `--permissive` | 레지스트리 로드 오류를 허용합니다. |
| `-t` , `--tag` (문자열) | 빌드 중인 컨테이너 이미지에 대한 사용자 정의 태그입니다. |

#### 8.2.2.3. prune-stranded

특정 이미지와 연결되지 않은 번들로 구성된 인덱스를 정리합니다.

```shell-session
$ opm index prune-stranded [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-i` , `--binary-image` | on-image `opm` 명령의 컨테이너 이미지 |
| `-c` , `--container-tool` (문자열) | 저장 및 빌드(예: `docker` 또는 `podman` )와 같은 컨테이너 이미지와 상호 작용하는 툴입니다. |
| `-f` , `--from-index` (문자열) | 정리할 인덱스입니다. |
| `--generate` | 활성화된 경우 Dockerfile만 생성하여 로컬 디스크에 저장합니다. |
| `-d` , `--out-dockerfile` (문자열) | 선택 사항: Dockerfile을 생성하는 경우 파일 이름을 지정합니다. |
| `-p` , `--packages` (문자열) | 쉼표로 구분된 보관할 패키지 목록입니다. |
| `--permissive` | 레지스트리 로드 오류를 허용합니다. |
| `-t` , `--tag` (문자열) | 빌드 중인 컨테이너 이미지에 대한 사용자 정의 태그입니다. |

#### 8.2.2.4. rm

인덱스에서 전체 Operator를 삭제합니다.

```shell-session
$ opm index rm [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-i` , `--binary-image` | on-image `opm` 명령의 컨테이너 이미지 |
| `-u` , `--build-tool` (문자열) | 컨테이너 이미지를 빌드하는 툴: `podman` (기본값) 또는 `docker` . `--container-tool` 플래그의 일부를 덮어씁니다. |
| `-c` , `--container-tool` (문자열) | 저장 및 빌드(예: `docker` 또는 `podman` )와 같은 컨테이너 이미지와 상호 작용하는 툴입니다. |
| `-f` , `--from-index` (문자열) | 삭제할 이전 인덱스입니다. |
| `--generate` | 활성화된 경우 Dockerfile만 생성하여 로컬 디스크에 저장합니다. |
| `-o` , `--operators` (문자열) | 삭제할 Operator의 쉼표로 구분된 목록입니다. |
| `-d` , `--out-dockerfile` (문자열) | 선택 사항: Dockerfile을 생성하는 경우 파일 이름을 지정합니다. |
| `-p` , `--packages` (문자열) | 쉼표로 구분된 보관할 패키지 목록입니다. |
| `--permissive` | 레지스트리 로드 오류를 허용합니다. |
| `-p` , `--pull-tool` (문자열) | 컨테이너 이미지를 가져오는 툴: `none` (기본값), `docker` 또는 `podman` . `--container-tool` 플래그의 일부를 덮어씁니다. |
| `-t` , `--tag` (문자열) | 빌드 중인 컨테이너 이미지에 대한 사용자 정의 태그입니다. |

추가 리소스

Operator 프레임워크 패키지 형식

사용자 정의 카탈로그 관리

oc-mirror 플러그인을 사용하여 연결이 끊긴 설치의 이미지 미러링

#### 8.2.3. init

`olm.package` 선언적 구성 Blob을 생성합니다.

```shell-session
$ opm init <package_name> [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-c` , `--default-channel` (문자열) | 서브스크립션이 지정되지 않은 경우 기본적으로 서브스크립션할 채널입니다. |
| `-d` , `--description` (문자열) | Operator의 `README.md` 또는 기타 문서 경로입니다. |
| `-i` , `--icon` (문자열) | 패키지의 아이콘 경로입니다. |
| `-o` , `--output` (문자열) | 출력 형식: `json` (기본값) 또는 `yaml` . |

#### 8.2.4. migrate

VMDK 데이터베이스 형식 인덱스 이미지 또는 데이터베이스 파일을 파일 기반 카탈로그로 마이그레이션합니다.

중요

관련 CLI 명령을 포함한 SQLite 기반 카탈로그 형식은 더 이상 사용되지 않는 기능입니다. 더 이상 사용되지 않는 기능은 여전히 OpenShift Container Platform에 포함되어 있으며 계속 지원됩니다. 그러나 이 기능은 향후 릴리스에서 제거될 예정이므로 새로운 배포에는 사용하지 않는 것이 좋습니다.

OpenShift Container Platform에서 더 이상 사용되지 않거나 삭제된 주요 기능의 최신 목록은 OpenShift Container Platform 릴리스 노트에서 더 이상 사용되지 않고 삭제된 기능 섹션을 참조하십시오.

```shell-session
$ opm migrate <index_ref> <output_dir> [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-o` , `--output` (문자열) | 출력 형식: `json` (기본값) 또는 `yaml` . |

#### 8.2.5. render

제공된 인덱스 이미지, 번들 이미지 및 SQLite 데이터베이스 파일에서 선언적 구성 Blob을 생성합니다.

```shell-session
$ opm render <index_image | bundle_image | sqlite_file> [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `-o` , `--output` (문자열) | 출력 형식: `json` (기본값) 또는 `yaml` . |

#### 8.2.6. serve

GRPC 서버를 통해 선언적 구성을 제공합니다.

참고

선언적 구성 디렉터리는 시작 시 `serve` 명령에 의해 로드됩니다. 이 명령을 시작한 후 선언적 구성에 대한 변경 사항은 제공된 콘텐츠에 반영되지 않습니다.

```shell-session
$ opm serve <source_path> [<flags>]
```

| 플래그 | 설명 |
| --- | --- |
| `--cache-dir` (문자열) | 이 플래그를 설정하면 서버 캐시 디렉터리를 동기화하고 유지합니다. |
| `--cache-enforce-integrity` | 캐시가 없거나 유효하지 않은 경우 오류와 함께 종료합니다. `--cache-dir` 플래그가 설정되어 있고 `--cache-only` 플래그가 `false` 인 경우 기본값은 `true` 입니다. 그렇지 않으면 기본값은 `false` 입니다. |
| `--cache-only` | 서비스 캐시를 동기화하고 서비스하지 않고 종료됩니다. |
| `--debug` | 디버그 로깅을 활성화합니다. |
| `h` , `--help` | serve에 대한 도움말입니다. |
| `-p` , `--port` (문자열) | 서비스의 포트 번호입니다. 기본값은 `50051` 입니다. |
| `--pprof-addr` (문자열) | 시작 프로파일링 끝점의 주소입니다. 형식은 `Addr:Port` 입니다. |
| `-t` , `--termination-log` (문자열) | 컨테이너 종료 로그 파일의 경로입니다. 기본값은 `/dev/termination-log` 입니다. |

#### 8.2.7. 검증

지정된 디렉터리에서 선언적 구성 JSON 파일을 검증합니다.

```shell-session
$ opm validate <directory> [<flags>]
```
