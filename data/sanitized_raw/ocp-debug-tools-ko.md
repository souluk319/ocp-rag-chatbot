<!-- source: ocp-debug-tools-ko.md -->

# OCP 디버깅 도구 실무 가이드

안녕하세요, 신입 엔지니어 여러분. OpenShift Container Platform (OCP) 환경에서 장애 발생 시 신속하고 정확한 원인을 파악하는 것은 DevOps 엔지니어의 핵심 역량입니다. Kubernetes 와 OCP 는 강력한 기능을 제공하지만, 복잡한 아키텍처와 추상화 계층으로 인해 문제 진단이 어려울 수 있습니다. 본 가이드는 OCP 의 강력한 디버깅 도구들을 체계적으로 설명하여, 실제 운영 환경에서 즉시 활용하실 수 있도록 작성되었습니다.

---

## 1. oc debug: 실시간 디버깅의 핵심

`oc debug` 명령어는 현재 실행 중인 컨테이너 내부에 임시 디버깅 컨테이너를 붙여넣거나, 노드나 Pod 에서 쉘 세션을 시작할 수 있게 해줍니다. 이는 `kubectl exec` 과 유사하지만, OCP 의 보안 컨텍스트와 통합되어 더 안전하게 작동합니다.

### 노드 디버깅
노드 레벨의 문제 (예: 커널 패닉, 네트워크 스택 오류, 메모리 누수) 를 확인해야 할 때 사용됩니다. 노드 이름 대신 `node/<node-name>` 또는 노드 선택자로 접근할 수 있습니다.

```bash
# 노드 내부로 진입 (root 권한으로)
oc debug -it --hostname node-01

# 노드 내부로 진입 (일반 사용자 권한으로)
oc debug -it --hostname node-01 -- as root
```

### Pod 디버깅
특정 Pod 의 컨테이너 내부로 진입하여 로그를 확인하거나 명령어를 실행할 수 있습니다.

```bash
# 특정 Pod 에 진입
oc debug -it <pod-name> -n <namespace>

# 여러 컨테이너가 있는 Pod 에서 특정 컨테이너 선택
oc debug -it <pod-name> -n <namespace> --container=app-container
```

**실무 팁:** `-it` 플래그는 인터랙티브 (TTY) 모드를 활성화하여 터미널 연결을 유지합니다. 디버깅이 끝나면 `exit` 명령어를 입력하여 컨테이너를 종료하고 자동으로 노드로 돌아옵니다.

---

## 2. must-gather: 문제 상황 전체 수집

`oc adm must-gather` 는 장애 발생 시 시스템 상태, 로그, 설정 파일 등을 자동으로 수집하여 압축된 아카이브 파일로 생성하는 도구입니다. 이는 Support 팀에 티켓을 제출하거나 외부 전문가에게 상황을 공유할 때 필수적입니다.

### 기본 수집 (전 클러스터)
클러스터 전체의 정보를 수집합니다. 수집된 파일은 현재 디렉토리에 `must-gather-<timestamp>.tar.gz` 형태로 저장됩니다.

```bash
oc adm must-gather
```

### 특정 네임스페이스 수집
대규모 클러스터에서 특정 애플리케이션 네임스페이스만 집중적으로 분석할 필요가 있을 때 유용합니다.

```bash
oc adm must-gather --namespace=production-app
```

**주의사항:** 수집된 파일은 매우 크며 (수 GB 단위일 수 있음), 보안 정책상 민감한 정보가 포함될 수 있으므로 전송 전 필터링이나 암호화가 필요할 수 있습니다.

---

## 3. oc adm inspect: 객체 상세 분석

`oc adm inspect` 는 OCP 의 API 서버에서 특정 리소스 (Pod, Service, Node 등) 의 상세 구조와 상태 정보를 JSON 형식으로 출력합니다. 이는 `oc get -o yaml` 과 유사하지만, OCP 가 추가한 커스텀 리소스나 확장된 필드를 더 명확하게 보여줍니다.

```bash
# Pod 상세 정보 조회
oc adm inspect pod/<pod-name> -n <namespace>

# Service 상세 정보 조회
oc adm inspect service/<service-name> -n <namespace>
```

이 명령어는 Pod 의 시작 로그, 이벤트 히스토리, 컨테이너 상태 등 디버깅에 필요한 모든 메타데이터를 한눈에 볼 수 있게 합니다.

---

## 4. oc logs: 로그 조회의 정교한 활용

`oc logs` 는 컨테이너의 표준 출력 (stdout) 과 표준 오류 (stderr) 를 조회하는 기본 도구입니다. 다양한 플래그를 활용하여 원하는 시점의 로그를 필터링할 수 있습니다.

### 주요 옵션 활용
*   **`--tail`**: 마지막 N 개의 로그 줄만 표시합니다.
*   **`-f` (또는 `--follow`)**: 로그가 생성되는 대로 실시간으로 스트리밍합니다.
*   **`--previous`**: 컨테이너가 종료된 후에도 마지막 로그를 확인합니다.
*   **멀티컨테이너**: 하나의 Pod 에 여러 컨테이너가 있다면 `--container` 옵션으로 지정해야 합니다.

```bash
# 마지막 50 줄만 표시
oc logs <pod-name> -n <namespace> --tail=50

# 실시간 로그 스트리밍
oc logs -f <pod-name> -n <namespace>

# 종료된 컨테이너의 마지막 로그 확인
oc logs <pod-name> -n <namespace> --previous

# 특정 컨테이너의 로그 (멀티컨테이너 Pod)
oc logs <pod-name> -n <namespace> --container=sidecar
```

**실무 팁:** `--previous` 옵션은 Pod 가 `CrashLoopBackOff` 상태로 반복 실패했을 때 가장 유용합니다. 현재 실행 중인 컨테이너는 없으므로, 이전 실행 기록을 확인해야 원인을 파악할 수 있습니다.

---

## 5. oc login: 안전한 인증 방법

OCP 클러스터에 접속하기 위해서는 올바른 인증 정보가 필요합니다. `oc login` 은 토큰 기반 인증과 인증서 기반 인증을 지원합니다.

### 토큰 기반 로그인 (권장)
OAuth2 토큰을 사용하여 로그인합니다. 클라이언트 ID 와 클라이언트 시크릿이 필요하며, 보통 CI/CD 파이프라인이나 스크립트에서 사용됩니다.

```bash
oc login --token=[REDACTED_SECRET] --server=https://<cluster-api>:6443
```

### 인증서 기반 로그인
서버의 CA 인증서를 사용하여 인증합니다. 이는 브라우저에서 로그인이 완료된 후 얻은 인증서를 `.kube/config` 에 저장하는 방식과 유사합니다.

```bash
oc login -u developer -p <password> https://<cluster-api>:6443
```

**주의사항:** 로그인 후 토큰은 만료될 수 있습니다. 만료 시에는 다시 `oc login` 명령어를 실행해야 합니다. 또한, `.kube/config` 파일에 토큰이 저장될 경우 보안상 주의가 필요합니다.

---

## 6. Pod 생성 기본 절차

디버깅을 위해 테스트 Pod 를 생성하거나, 실제 애플리케이션을 배포하는 첫 단계입니다.

### kubectl run 을 이용한 빠른 생성
YAML 파일을 작성하지 않고 빠르게 테스트용 Pod 를 생성할 수 있습니다.

```bash
kubectl run debug-pod --image=busybox --restart=Never --rm -it -- sh
```

### YAML 적용을 통한 생성 (권장)
실무에서는 상태 관리와 재현성을 위해 YAML 파일을 작성하여 적용합니다.

```yaml
# debug-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: debug-pod
  namespace: default
spec:
  containers:
  - name: debug-container
    image: centos:latest
    command: ["sleep", "3600"]
```

```bash
oc apply -f debug-pod.yaml
```

---

## 7. 감사 (Audit) 로그 확인 방법

OCP 는 클러스터 내 모든 API 요청에 대한 감사 로그를 기록합니다. 이는 보안 감사나 이상한 접근 패턴 감지에 필수적입니다.

### 감사 로그 위치 확인
일반적으로 감사 로그는 클러스터 내의 `openshift-audit` 프로젝트에 있는 `audit` 이름공간에 저장된 Elasticsearch 또는 Filebeat 로 수집됩니다.

```bash
# 감사 로그가 저장된 위치 확인 (클러스터 설정에 따라 다름)
oc get projects -A | grep audit

# 감사 로그 조회 (예시: Elasticsearch 와 연동된 경우)
oc logs -f -n openshift-audit <audit-logging-pod-name>
```

**주의사항:** 감사 로그는 민감한 정보 (패스워드, 토큰 등) 를 포함할 수 있으므로, 조회 시에는 필터링을 적용하거나 보안 정책에 따라 접근 권한을 제한해야 합니다.

---

## 8. sosreport: 시스템 상태 포착

`sosreport` 는 리눅스 시스템의 디버깅을 위해 설계된 강력한 도구로, OCP 의 노드에서 시스템 상태 (내부 설정, 네트워크, 메모리, 디스크 등) 를 포착합니다.

### 사용 방법
```bash
# 기본 리포트 생성
sosreport

# 특정 디렉토리에 저장
sosreport -d /tmp/sosreport-$(date +%F)

# 특정 패키지 정보 포함
sosreport --collect-pkgs
```

생성된 리포트는 압축 파일이며, Support 팀이나 외부 전문가에게 전달하여 심층 분석을 요청할 때 사용됩니다.

---

## 요약 및 주의사항

| 도구 | 주요 용도 | 주의사항 |
| :--- | :--- | :--- |
| **oc debug** | 노드/Pod 내부 진입 | `-
