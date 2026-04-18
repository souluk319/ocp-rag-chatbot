# 검증 및 문제 해결

## OpenShift Container Platform 설치 검증 및 문제 해결

이 문서에서는 OpenShift Container Platform 설치의 유효성을 검사하고 문제를 해결하는 방법을 설명합니다.

## 1장. 설치 검증

이 문서의 절차에 따라 설치 후 OpenShift Container Platform 클러스터의 상태를 확인하거나 설치 전에 부팅 아티팩트를 검증할 수 있습니다.

### 1.1. RHCOS 라이브 미디어 검증

OpenShift Container Platform 설치 프로그램에는 고정된 RHCOS 부팅 이미지가 포함되어 있습니다. 완전 자동화된 설치에서는 기본적으로 이러한 고정 아티팩트를 사용합니다. 설치 프로그램을 다운로드한 미러 레지스트리에는 Red Hat 제품 키로 암호화된 `sha256sum` 이 포함되어 있습니다.

사용자가 프로비저닝한 인프라 설치의 경우 정보에 액세스하고 OpenShift Container Platform 설치 프로그램을 사용하여 SHA-256 체크섬을 사용하여 RHCOS bootimage 아티팩트를 간접적으로 검증할 수 있습니다.

프로세스

다음 명령을 실행하여 bootimage 아티팩트에 대한 메타데이터를 출력합니다.

```shell-session
$ openshift-install coreos print-stream-json | jq <bootimage>
```

1. 정보를 가져올 bootimage 쿼리입니다. 검증을 위해 bootimage 아티팩트에는 생성된 `sha256sum` 이 있어야 합니다.

여기에는 OVA, VHD, QCOW2 등이 포함될 수 있습니다. 예를 들어 베어 메탈 플랫폼의 `x86_64` 아키텍처 `iso` 파일에 대한 정보를 얻으려면 이 값은 `.architectures.x86_64.artifacts.metal.formats.iso` 입니다.

```plaintext
{
  "disk": {
    "location": "<url>/art/storage/prod/streams/<release>/builds/rhcos-<release>-live.<architecture>.<artifact>",
    "sha256": "abc2add9746eb7be82e6919ec13aad8e9eae8cf073d8da6126d7c95ea0dee962"
  }
}
```

### 1.2. 설치 로그 검토

OpenShift Container Platform 설치 로그에서 설치 요약을 검토할 수 있습니다. 설치에 성공하면 클러스터에 액세스하는 데 필요한 정보가 로그에 포함됩니다.

사전 요구 사항

설치 호스트에 대한 액세스 권한이 있어야 합니다.

프로세스

설치 호스트의 설치 디렉터리에서 `.openshift_install.log` 로그 파일을 검토합니다.

```shell-session
$ cat <install_dir>/.openshift_install.log
```

출력 예

다음 예에 설명된 대로 설치에 성공하면 클러스터 인증 정보가 로그 끝에 포함됩니다.

```shell-session
...
time="2020-12-03T09:50:47Z" level=info msg="Install complete!"
time="2020-12-03T09:50:47Z" level=info msg="To access the cluster as the system:admin user when using 'oc', run 'export KUBECONFIG=/home/myuser/install_dir/auth/kubeconfig'"
time="2020-12-03T09:50:47Z" level=info msg="Access the OpenShift web-console here: https://console-openshift-console.apps.mycluster.example.com"
time="2020-12-03T09:50:47Z" level=info msg="Login to the console with user: \"kubeadmin\", and password: \"password\""
time="2020-12-03T09:50:47Z" level=debug msg="Time elapsed per stage:"
time="2020-12-03T09:50:47Z" level=debug msg="    Infrastructure: 6m45s"
time="2020-12-03T09:50:47Z" level=debug msg="Bootstrap Complete: 11m30s"
time="2020-12-03T09:50:47Z" level=debug msg=" Bootstrap Destroy: 1m5s"
time="2020-12-03T09:50:47Z" level=debug msg=" Cluster Operators: 17m31s"
time="2020-12-03T09:50:47Z" level=info msg="Time elapsed: 37m26s"
```

### 1.3. 이미지 풀 소스 보기

무제한 네트워크 연결이 있는 클러스터의 경우 다음 명령과 같은 노드에서 명령을 사용하여 가져온 이미지의 소스를 볼 수 있습니다.

```shell
crictl images
```

그러나 연결이 끊긴 설치의 경우 가져온 이미지 소스를 보려면 CRI-O 로그를 검토하여 다음 절차에 표시된 대로 로그 항목에 `Trying to access` 를 찾아야 합니다. 아래 명령과 같은 이미지 가져오기 소스를 보는 다른 방법은 미러링된 위치에서 이미지를 가져오는 경우에도 미러링되지 않은 이미지 이름을 표시합니다.

```shell
crictl images
```

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

마스터 또는 작업자 노드의 CRI-O 로그를 확인합니다.

```shell-session
$  oc adm node-logs <node_name> -u crio
```

출력 예

`Trying to access` 로그 항목은 이미지를 가져오는 위치를 나타냅니다.

```shell-session
...
Mar 17 02:52:50 ip-10-0-138-140.ec2.internal crio[1366]: time="2021-08-05 10:33:21.594930907Z" level=info msg="Pulling image: quay.io/openshift-release-dev/ocp-release:4.10.0-ppc64le" id=abcd713b-d0e1-4844-ac1c-474c5b60c07c name=/runtime.v1alpha2.ImageService/PullImage
Mar 17 02:52:50 ip-10-0-138-140.ec2.internal crio[1484]: time="2021-03-17 02:52:50.194341109Z" level=info msg="Trying to access \"li0317gcp1.mirror-registry.qe.gcp.devcluster.openshift.com:5000/ocp/release@sha256:1926eae7cacb9c00f142ec98b00628970e974284b6ddaf9a6a086cb9af7a6c31\""
Mar 17 02:52:50 ip-10-0-138-140.ec2.internal crio[1484]: time="2021-03-17 02:52:50.226788351Z" level=info msg="Trying to access \"li0317gcp1.mirror-registry.qe.gcp.devcluster.openshift.com:5000/ocp/release@sha256:1926eae7cacb9c00f142ec98b00628970e974284b6ddaf9a6a086cb9af7a6c31\""
...
```

위 예제와 같이 로그에 이미지 가져오기 소스가 두 번 표시될 수 있습니다.

`ImageContentSourcePolicy` 오브젝트가 여러 미러를 나열하는 경우 OpenShift Container Platform은 구성에 나열된 순서대로 이미지를 가져오려고 시도합니다. 예를 들면 다음과 같습니다.

```plaintext
Trying to access \"li0317gcp1.mirror-registry.qe.gcp.devcluster.openshift.com:5000/ocp/release@sha256:1926eae7cacb9c00f142ec98b00628970e974284b6ddaf9a6a086cb9af7a6c31\"
Trying to access \"li0317gcp2.mirror-registry.qe.gcp.devcluster.openshift.com:5000/ocp/release@sha256:1926eae7cacb9c00f142ec98b00628970e974284b6ddaf9a6a086cb9af7a6c31\"
```

### 1.4. 클러스터 버전, 상태 및 업데이트 세부 정보 가져오기

아래 명령을 실행하여 클러스터 버전 및 상태를 검토할 수 있습니다. 설치가 여전히 진행 중임을 표시하는 경우 자세한 내용은 Operator의 상태를 검토할 수 있습니다.

```shell
oc get clusterversion
```

현재 업데이트 채널을 나열하고 사용 가능한 클러스터 업데이트를 검토할 수도 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

클러스터 버전 및 전체 상태를 가져옵니다.

```shell-session
$ oc get clusterversion
```

```shell-session
NAME      VERSION   AVAILABLE   PROGRESSING   SINCE   STATUS
version   4.6.4     True        False         6m25s   Cluster version is 4.6.4
```

예제 출력은 클러스터가 성공적으로 설치되었음을 나타냅니다.

클러스터 상태가 설치가 여전히 진행 중임을 나타내는 경우 Operator 상태를 확인하여 더 자세한 진행 정보를 얻을 수 있습니다.

```shell-session
$ oc get clusteroperators.config.openshift.io
```

클러스터 사양, 업데이트 가용성 및 업데이트 기록에 대한 자세한 요약을 확인합니다.

```shell-session
$ oc describe clusterversion
```

현재 업데이트 채널을 나열합니다.

```shell-session
$ oc get clusterversion -o jsonpath='{.items[0].spec}{"\n"}'
```

```shell-session
{"channel":"stable-4.6","clusterID":"245539c1-72a3-41aa-9cec-72ed8cf25c5c"}
```

사용 가능한 클러스터 업데이트를 검토합니다.

```shell-session
$ oc adm upgrade
```

```shell-session
Cluster version is 4.6.4

Updates:

VERSION IMAGE
4.6.6   quay.io/openshift-release-dev/ocp-release@sha256:c7e8f18e8116356701bd23ae3a23fb9892dd5ea66c8300662ef30563d7104f39
```

추가 리소스

설치가 계속 진행 중인 경우 Operator 상태를 쿼리하는 방법에 대한 자세한 내용은 설치 후 Operator 상태 쿼리를 참조하십시오.

Operator 문제 조사에 대한 정보는 Operator 문제 해결을 참조하십시오.

클러스터 업데이트에 대한 자세한 내용은 웹 콘솔을 사용하여 클러스터 업데이트를 참조하십시오.

업데이트 릴리스 채널에 대한 개요는 업데이트 채널 및 릴리스 이해 를 참조하십시오.

### 1.5. 클러스터가 단기 인증 정보를 사용하는지 확인

CCO(Cloud Credential Operator) 구성 및 클러스터의 기타 값을 확인하여 클러스터가 개별 구성 요소에 대해 단기 보안 인증 정보를 사용하는지 확인할 수 있습니다.

사전 요구 사항

단기 인증 정보를 구현하기 위해 Cloud Credential Operator 유틸리티(`ccoctl`)를 사용하여 OpenShift Container Platform 클러스터를 배포했습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

다음 명령을 실행하여 CCO가 수동 모드에서 작동하도록 구성되었는지 확인합니다.

```shell-session
$ oc get cloudcredentials cluster \
  -o=jsonpath={.spec.credentialsMode}
```

다음 출력은 CCO가 수동 모드에서 작동하는지 확인합니다.

```plaintext
Manual
```

다음 명령을 실행하여 클러스터에 `root` 인증 정보가 없는지 확인합니다.

```shell-session
$ oc get secrets \
  -n kube-system <secret_name>
```

여기서 `<secret_name` >은 클라우드 공급자의 루트 시크릿 이름입니다.

| 플랫폼 | 시크릿 이름 |
| --- | --- |
| AWS(Amazon Web Services) | `aws-creds` |
| Microsoft Azure | `azure-credentials` |
| Google Cloud | `gcp-credentials` |

오류가 발생하면 루트 시크릿이 클러스터에 존재하지 않음을 확인할 수 있습니다.

```plaintext
Error from server (NotFound): secrets "aws-creds" not found
```

다음 명령을 실행하여 구성 요소가 개별 구성 요소에 대해 단기 보안 인증 정보를 사용하고 있는지 확인합니다.

```shell-session
$ oc get authentication cluster \
  -o jsonpath \
  --template='{ .spec.serviceAccountIssuer }'
```

이 명령은 클러스터 `Authentication` 오브젝트에서 `.spec.serviceAccountIssuer` 매개변수 값을 표시합니다. 클라우드 공급자와 연결된 URL의 출력은 클러스터가 클러스터 외부에서 생성 및 관리되는 단기 자격 증명과 함께 수동 모드를 사용하고 있음을 나타냅니다.

Azure 클러스터: 구성 요소가 다음 명령을 실행하여 시크릿 매니페스트에 지정된 Azure 클라이언트 ID를 가정하는지 확인합니다.

```shell-session
$ oc get secrets \
  -n openshift-image-registry installer-cloud-credentials \
  -o jsonpath='{.data}'
```

`azure_client_id` 및 `azure_federated_token_file` 가 포함된 출력은 구성 요소가 Azure 클라이언트 ID를 가정하고 있음을 확인합니다.

Azure 클러스터: 다음 명령을 실행하여 Pod ID Webhook가 실행 중인지 확인합니다.

```shell-session
$ oc get pods \
  -n openshift-cloud-credential-operator
```

```plaintext
NAME                                         READY   STATUS    RESTARTS   AGE
cloud-credential-operator-59cf744f78-r8pbq   2/2     Running   2          71m
pod-identity-webhook-548f977b4c-859lz        1/1     Running   1          70m
```

### 1.6. CLI를 사용하여 클러스터 노드의 상태 쿼리

설치 후 클러스터 노드의 상태를 확인할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

클러스터 노드의 상태를 나열합니다. 출력에 모든 예상 컨트롤 플레인 및 컴퓨팅 노드가 나열되고 각 노드에 `Ready` 상태가 있는지 확인합니다.

```shell-session
$ oc get nodes
```

```shell-session
NAME                          STATUS   ROLES    AGE   VERSION
compute-1.example.com         Ready    worker   33m   v1.33.4
control-plane-1.example.com   Ready    master   41m   v1.33.4
control-plane-2.example.com   Ready    master   45m   v1.33.4
compute-2.example.com         Ready    worker   38m   v1.33.4
compute-3.example.com         Ready    worker   33m   v1.33.4
control-plane-3.example.com   Ready    master   41m   v1.33.4
```

각 클러스터 노드의 CPU 및 메모리 리소스 가용성을 검토합니다.

```shell-session
$ oc adm top nodes
```

```shell-session
NAME                          CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
compute-1.example.com         128m         8%     1132Mi          16%
control-plane-1.example.com   801m         22%    3471Mi          23%
control-plane-2.example.com   1718m        49%    6085Mi          40%
compute-2.example.com         935m         62%    5178Mi          75%
compute-3.example.com         111m         7%     1131Mi          16%
control-plane-3.example.com   942m         26%    4100Mi          27%
```

추가 리소스

노드 상태 검토 및 노드 문제 조사에 대한 자세한 내용은 노드 상태 확인을 참조하십시오.

### 1.7. OpenShift Container Platform 웹 콘솔에서 클러스터 상태 검토

OpenShift Container Platform 웹 콘솔의 개요 페이지에서 다음 정보를 검토할 수 있습니다.

클러스터의 일반 상태

컨트롤 플레인, 클러스터 Operator 및 스토리지의 상태

CPU, 메모리, 파일 시스템, 네트워크 전송, Pod 가용성

클러스터의 API 주소, 클러스터 ID 및 공급자의 이름

클러스터 버전 정보

현재 업데이트 채널 및 사용 가능한 업데이트를 포함하여 클러스터 업데이트 상태

노드, 포드, 스토리지 클래스 및 PVC(영구 볼륨 클레임) 정보를 설명하는 클러스터 인벤토리

진행 중인 클러스터 활동 및 최근 이벤트 목록

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

홈 → 개요 로 이동합니다.

### 1.8. Red Hat OpenShift Cluster Manager에서 클러스터 상태 검토

OpenShift Container Platform 웹 콘솔에서 OpenShift Cluster Manager의 클러스터 상태에 대한 자세한 정보를 확인할 수 있습니다.

사전 요구 사항

OpenShift Cluster Manager 에 로그인되어 있습니다.

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

OpenShift Cluster Manager 의 클러스터 목록으로 이동하여 OpenShift Container Platform 클러스터를 찾습니다.

클러스터의 개요 탭을 클릭합니다.

클러스터에 대한 다음 정보를 검토합니다.

vCPU 및 메모리 가용성 및 리소스 사용

클러스터 ID, 상태, 유형, 리전 및 공급자 이름

노드 유형별 노드 수

클러스터 버전 세부 정보, 클러스터 생성 날짜, 클러스터 소유자의 이름

클러스터의 라이프사이클 지원 상태

SLA(서비스 수준 계약) 상태, 서브스크립션 단위 유형, 클러스터의 프로덕션 상태, 서브스크립션을 포함한 서브스크립션 정보

작은 정보

클러스터 기록을 보려면 클러스터 기록 탭을 클릭합니다.

모니터링 페이지로 이동하여 다음 정보를 검토합니다.

감지된 모든 문제 목록

실행 중인 경고 목록

클러스터 Operator 상태 및 버전

클러스터의 리소스 사용량

선택 사항: 개요 메뉴로 이동하여 Red Hat Lightspeed가 수집하는 클러스터에 대한 정보를 볼 수 있습니다. 이 메뉴에서 다음 정보를 볼 수 있습니다.

위험 수준별로 분류된, 클러스터가 노출될 수 있는 잠재적인 문제

카테고리별 상태 검사 상태

추가 리소스

클러스터의 잠재적인 문제 검토에 대한 자세한 내용은 Red Hat Lightspeed를 사용하여 클러스터 문제 식별 을 참조하십시오.

### 1.9. 클러스터 리소스 가용성 및 사용 여부 확인

[FIGURE src="/playbooks/wiki-assets/full_rebuild/validation_and_troubleshooting/monitoring-dashboard-compute-resources.png" alt="대시보드 컴퓨팅 리소스 모니터링" kind="figure" diagram_type="image_figure"]
대시보드 컴퓨팅 리소스 모니터링
[/FIGURE]

_Source: `validation_and_troubleshooting.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Validation_and_troubleshooting-ko-KR/images/b2d5f6ce1d0581d56b0bf88e26721b63/monitoring-dashboard-compute-resources.png`_


OpenShift Container Platform은 클러스터 구성 요소의 상태를 이해하는 데 도움이 되는 포괄적인 모니터링 대시보드 세트를 제공합니다.

관리자는 다음을 포함하여 핵심 OpenShift Container Platform 구성 요소의 대시보드에 액세스할 수 있습니다.

etcd

Kubernetes 컴퓨팅 리소스

Kubernetes 네트워크 리소스

Prometheus

클러스터 및 노드 성능과 관련된 대시보드

그림 1.1. 컴퓨팅 리소스 대시보드 예

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

OpenShift Container Platform 웹 콘솔의 클러스터 관리자로 모니터링 → 대시보드 로 이동합니다.

대시보드 목록에서 대시보드를 선택합니다. etcd 대시보드와 같은 일부 대시보드를 선택하면 추가 하위 메뉴가 생성됩니다.

선택 사항: 시간 범위 목록에서 그래프의 시간 범위를 선택합니다.

미리 정의된 기간을 선택합니다.

시간 범위 목록 에서 사용자 지정 시간 범위 를 선택하여 사용자 지정 시간 범위를 설정합니다.

시작 및 종료 날짜 및 시간을 입력하거나 선택합니다.

저장 을 클릭하여 사용자 지정 시간 범위를 저장합니다.

선택 사항: 새로 고침 간격 을 선택합니다.

대시보드 내에서 각각의 그래프로 마우스를 이동하여 특정 항목에 대한 세부 정보를 표시합니다.

추가 리소스

OpenShift Container Platform 모니터링 스택에 대한 자세한 내용은 OpenShift Container Platform 모니터링 정보를 참조하십시오.

### 1.10. 실행 중인 경고 나열

경고는 OpenShift Container Platform 클러스터에서 정의된 조건 집합이 적용되는 경우 알림을 제공합니다. OpenShift Container Platform 웹 콘솔에서 경고 UI를 사용하여 클러스터에서 실행되는 경고를 확인할 수 있습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

관리자 화면에서 모니터링 → 경고 → 경고 규칙 페이지로 이동합니다.

심각도, 상태 및 소스 를 포함하여 실행 중인 경고를 검토합니다.

경고 세부 정보 페이지에서 자세한 정보를 보려면 경고를 선택합니다.

추가 리소스

OpenShift Container Platform 의 경고에 대한 자세한 내용은 관리자로 경고 관리를 참조하십시오.

### 1.11. 다음 단계

클러스터를 설치할 때 문제가 발생하면 설치 문제 해결을 참조하십시오.

OpenShift Container Platform을 설치한 후 클러스터를 추가로 확장하고 사용자 정의할 수 있습니다.

## 2장. 설치 문제 해결

OpenShift Container Platform 설치 실패 문제를 해결하기 위해 부트스트랩 및 컨트롤 플레인 시스템에서 로그를 수집할 수 있습니다. 설치 프로그램에서 디버그 정보를 얻을 수도 있습니다. 로그 및 디버그 정보를 사용하여 문제를 해결할 수 없는 경우 구성 요소별 문제 해결에 대해 설치 문제가 발생하는 위치 지정을 참조하십시오.

참고

OpenShift Container Platform 설치에 실패하고 디버그 출력 또는 로그에 네트워크 시간 초과 또는 기타 연결 오류가 포함된 경우 방화벽 구성 지침을 검토하십시오. 방화벽 및 로드 밸런서에서 로그를 수집하면 네트워크 관련 오류를 진단하는 데 도움이 될 수 있습니다.

### 2.1. 사전 요구 사항

OpenShift Container Platform 클러스터를 설치하려고했으나 설치에 실패했습니다.

### 2.2. 실패한 설치에서 로그 수집

설치 프로그램에 SSH 키를 지정한 경우 실패한 설치에 대한 데이터를 수집할 수 있습니다.

참고

실패한 설치에 대한 로그를 수집하는데 사용되는 명령은 실행중인 클러스터에서 로그를 수집할 때 사용되는 명령과 다릅니다. 실행중인 클러스터에서 로그를 수집해야하는 경우 아래 명령을 사용하십시오.

```shell
oc adm must-gather
```

사전 요구 사항

부트스트랩 프로세스가 완료되기 전에 OpenShift Container Platform 설치에 실패합니다. 부트스트랩 노드가 실행 중이며 SSH를 통해 액세스할 수 있습니다.

다음 명령프로세스는 컴퓨터에서 활성화되어 있으며 프로세스 및 설치 프로그램에 동일한 SSH 키를 제공하고 있습니다.

```shell
ssh-agent
```

```shell
ssh-agent
```

프로비저닝하는 인프라에 클러스터를 설치하려는 경우 부트스트랩 및 컨트롤 플레인 노드의 정규화된 도메인 이름이 있어야 합니다.

프로세스

부트스트랩 및 컨트롤 플레인 시스템에서 설치 로그를 가져오는데 필요한 명령을 생성합니다.

설치 관리자 프로비저닝 인프라를 사용한 경우 설치 프로그램이 포함된 디렉터리로 변경하고 다음 명령을 실행합니다.

```shell-session
$ ./openshift-install gather bootstrap --dir <installation_directory>
```

1. `installation_directory` 는 `./openshift-install create cluster` 를 실행할 때 지정한 디렉터리입니다. 이 디렉터리에는 설치 프로그램이 생성한 OpenShift Container Platform 정의 파일이 포함되어 있습니다.

설치 프로그램이 프로비저닝한 인프라의 경우 설치 프로그램은 클러스터에 대한 정보를 저장하므로 호스트 이름 또는 IP 주소를 지정할 필요가 없습니다.

자체적으로 프로비저닝한 인프라를 사용한 경우 설치 프로그램이 포함된 디렉터리로 변경하고 다음 명령을 실행합니다.

```shell-session
$ ./openshift-install gather bootstrap --dir <installation_directory> \
    --bootstrap <bootstrap_address> \
    --master <master_1_address> \
    --master <master_2_address> \
    --master <master_3_address>
```

1. `installation_directory` 의 경우 `./openshift-install create cluster` 를 실행할 때 지정한 것과 동일한 디렉터리를 지정합니다. 이 디렉터리에는 설치 프로그램이 생성한 OpenShift Container Platform 정의 파일이 포함되어 있습니다.

2. `<bootstrap_address>` 는 클러스터 부트스트랩 시스템의 정규화된 도메인 이름 또는 IP 주소입니다.

3. 4

5. 클러스터의 각 컨트롤 플레인 또는 마스터 시스템에 대해 `<master_*_address>` 를 정규화된 도메인 이름 또는 IP 주소로 변경합니다.

참고

기본 클러스터에는 세 개의 컨트롤 플레인 시스템이 있습니다. 클러스터가 사용하는 수에 관계없이 표시된대로 모든 컨트롤 플레인 시스템을 나열합니다.

```shell-session
INFO Pulling debug logs from the bootstrap machine
INFO Bootstrap gather logs captured here "<installation_directory>/log-bundle-<timestamp>.tar.gz"
```

설치 실패에 대한 Red Hat 지원 케이스를 만들 경우 압축된 로그를 케이스에 포함해야 합니다.

### 2.3. 호스트에 SSH 액세스를 통해 수동으로 로그 수집

`must-gather` 또는 자동화된 수집 방법이 작동하지 않는 경우 로그를 수동으로 수집합니다.

중요

기본적으로 OpenShift Container Platform 노드에 대한 SSH 액세스는 RHOSP(Red Hat OpenStack Platform) 기반 설치에서 비활성화되어 있습니다.

사전 요구 사항

호스트에 대한 SSH 액세스 권한이 있어야합니다.

프로세스

다음을 실행하여 아래 명령을 사용하여 부트스트랩 호스트에서 `bootkube.service` 서비스 로그를 수집합니다.

```shell
journalctl
```

```shell-session
$ journalctl -b -f -u bootkube.service
```

podman 로그를 사용하여 부트스트랩 호스트의 컨테이너 로그를 수집합니다. 이는 호스트에서 모든 컨테이너 로그를 가져오기 위해 루프로 표시됩니다.

```shell-session
$ for pod in $(sudo podman ps -a -q); do sudo podman logs $pod; done
```

또는 다음을 실행하여 `tail` 명령을 사용하여 호스트 컨테이너 로그를 수집합니다.

```shell-session
# tail -f /var/lib/containers/storage/overlay-containers/*/userdata/ctr.log
```

다음과 같이 아래 명령을 사용하여 마스터 및 작업자 호스트에서 `kubelet.service` 및 `crio.service` 서비스 로그를 수집합니다.

```shell
journalctl
```

```shell-session
$ journalctl -b -f -u kubelet.service -u crio.service
```

다음과 같이 `tail` 명령을 사용하여 마스터 및 작업자 호스트 컨테이너 로그를 수집합니다.

```shell-session
$ sudo tail -f /var/log/containers/*
```

### 2.4. 호스트에 SSH 액세스없이 수동으로 로그 수집

`must-gather` 또는 자동화된 수집 방법이 작동하지 않는 경우 로그를 수동으로 수집합니다.

노드에 대한 SSH 액세스 권한이 없는 경우 시스템 저널에 액세스하여 호스트에서 발생하는 상황을 조사할 수 있습니다.

사전 요구 사항

OpenShift Container Platform 설치가 완료되어야 합니다.

API 서비스가 작동하고 있어야 합니다.

시스템 관리자 권한이 있어야 합니다.

프로세스

다음을 실행하여 `/var/log` 아래의 `journald` 유닛 로그에 액세스합니다.

```shell-session
$ oc adm node-logs --role=master -u kubelet
```

다음을 실행하여 `/var/log` 아래의 호스트 파일 경로에 액세스합니다.

```shell-session
$ oc adm node-logs --role=master --path=openshift-apiserver
```

### 2.5. 설치 프로그램에서 디버그 정보 검색

다음 조치 중 하나를 사용하여 설치 프로그램에서 디버그 정보를 얻을 수 있습니다.

숨겨진 `.openshift_install.log` 파일에서 이전 설치의 디버그 정보를 확인합니다. 예를 들면 다음과 같습니다.

```shell-session
$ cat ~/<installation_directory>/.openshift_install.log
```

1. `installation_directory` 의 경우 `./openshift-install create cluster` 를 실행할 때 지정한 것과 동일한 디렉터리를 지정합니다.

설치 프로그램이 포함된 디렉터리로 변경하고 `--log-level=debug` 로 다시 실행합니다.

```shell-session
$ ./openshift-install create cluster --dir <installation_directory> --log-level debug
```

1. `installation_directory` 의 경우 `./openshift-install create cluster` 를 실행할 때 지정한 것과 동일한 디렉터리를 지정합니다.

### 2.6. OpenShift Container Platform 클러스터 다시 설치

실패한 OpenShift Container Platform 설치에서 문제를 디버그하고 해결할 수 없는 경우 새 OpenShift Container Platform 클러스터를 설치하는 것이 좋습니다. 설치 프로세스를 다시 시작하기 전에 철저하게 정리해야 합니다.

사용자가 프로비저닝한 인프라(UPI) 설치의 경우 클러스터를 수동으로 제거하고 모든 관련 리소스를 삭제해야 합니다. 다음 절차는 설치 관리자 프로비저닝 인프라(IPI) 설치를 위한 것입니다.

프로세스

클러스터를 삭제하고 설치 디렉터리의 숨겨진 설치 프로그램 상태 파일을 포함하여 클러스터와 관련된 모든 리소스를 제거합니다.

```shell-session
$ ./openshift-install destroy cluster --dir <installation_directory>
```

1. `installation_directory` 는 `./openshift-install create cluster` 를 실행할 때 지정한 디렉터리입니다. 이 디렉터리에는 설치 프로그램이 생성한 OpenShift Container Platform 정의 파일이 포함되어 있습니다.

클러스터를 다시 설치하기 전에 설치 디렉터리를 삭제합니다.

```shell-session
$ rm -rf <installation_directory>
```

새 OpenShift Container Platform 클러스터를 설치하는 절차를 따르십시오.

추가 리소스

OpenShift Container Platform 클러스터 설치
