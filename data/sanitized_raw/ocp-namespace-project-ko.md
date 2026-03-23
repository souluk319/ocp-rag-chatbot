<!-- source: ocp-namespace-project-ko.md -->

# OpenShift Container Platform Namespace & Project 관리 가이드

## 1. Namespace 와 Project 개념: 차이점 이해하기

Kubernetes 생태계에서 리소스를 논리적으로 분리하는 핵심 개념은 **Namespace**입니다. 그러나 Red Hat OpenShift Container Platform (OCP) 은 이 개념을 확장하여 **Project**를 도입했습니다. 두 용어는 밀접하게 연관되어 있지만, OCP 환경에서는 Project 가 Namespace 보다 더 풍부한 기능을 제공합니다.

**Namespace**는 Kubernetes 의 기본 단위로, 같은 클러스터 내에서 리소스 이름 충돌을 방지하고 리소스를 논리적으로 그룹화합니다. 반면, **Project**는 OCP 에서 Namespace 와 1:1 매핑되지만, 단순한 이름 공간 이상의 기능을 포함합니다. Project 는 Namespaces 가 가진 기본 기능 (리소스 격리) 에 더해, OCP 의 고유한 보안 및 운영 기능들을 자동으로 적용합니다.

### 핵심 특징 비교

| 기능 | Kubernetes Namespace | OpenShift Project |
| :--- | :--- | :--- |
| **기본 격리** | 리소스 이름 충돌 방지, 스토리지 격리 | ✅ 제공 |
| **기본 RBAC** | 없음 (사용자가 직접 정의 필요) | ✅ 제공 (admin, edit, view 등) |
| **ServiceAccount** | 없음 (수동 생성 필요) | ✅ 제공 (default, build, deploy 등) |
| **Image Streams** | 수동 설정 필요 | ✅ 자동 생성 및 관리 |
| **Build Configs** | 수동 설정 필요 | ✅ 기본 템플릿 포함 |
| **Network Policies** | 수동 설정 필요 | ✅ 기본 정책 포함 (Default Deny 등) |
| **ResourceQuota** | 수동 설정 필요 | ✅ 권장 설정 템플릿 포함 |
| **사용자 인터페이스** | kubectl 기반 | Web Console + oc/cli |

즉, **Project 는 Namespace 를 기반으로 하되, OCP 의 보안 모델 (RBAC), 빌드/배포 워크플로우, 그리고 기본 리소스 제한 설정이 미리 적용된 '엔비러닝된 Namespace'**라고 할 수 있습니다.

---

## 2. Project 생성, 삭제 및 전환 방법

OCP 에서 작업을 수행할 때는 대부분 Project 단위로 접근합니다. `oc` CLI 는 Project 관리에 최적화되어 있습니다.

### Project 생성
새로운 개발 환경을 위해 Project 를 생성합니다.
```bash
# 기본 설정으로 생성 (default namespace 사용)
oc new-project my-development-env

# 특정 이름으로 생성 (옵션: --display-name)
oc new-project production-db --display-name="Production Database Cluster"
```

### Project 전환
현재 컨텍스트를 다른 Project 로 변경합니다. 모든 후속 명령어가 해당 Project 에 적용됩니다.
```bash
# Project 로 전환
oc project my-development-env

# 현재 Project 확인
oc who am i
# 또는
oc get projects
```

### Project 삭제
프로젝트를 완전히 삭제합니다. 주의: 이 작업은 해당 Project 내의 모든 리소스 (Pod, PVC, ConfigMap 등) 를 영구적으로 제거합니다.
```bash
# Project 삭제 (강제 삭제 옵션 --delete-full=true 포함 시 모든 관련 리소스 제거)
oc delete project my-development-env --delete-full=true
```

---

## 3. Namespace 생성: kubectl vs oc 비교

Kubernetes 클러스터에 직접 접근하거나 OCP 의 Namespace 기능만 필요한 경우 `kubectl` 을 사용할 수 있습니다. 하지만 OCP 환경에서는 `oc new-project` 가 권장됩니다.

### 비교 분석

1.  **기능의 완전성**:
    *   `kubectl create namespace my-ns`: 빈 Namespace 만 생성합니다. RBAC, ServiceAccount, ImageStream 이 없습니다.
    *   `oc new-project my-ns`: Namespace 생성과 동시에 OCP 의 기본 템플릿 (RBAC, SA, ImageStreams 등) 을 적용합니다.

2.  **권장 사항**:
    *   OCP 클러스터라면 **반드시 `oc new-project`**를 사용해야 합니다. `kubectl` 로 생성된 Namespace 는 OCP 의 보안 정책 (예: Default Deny Network Policy) 이 적용되지 않을 수 있어 보안 취약점이 될 수 있습니다.

### 예시: kubectl 로 Namespace 생성 (비추천)
```bash
kubectl create namespace legacy-ns
```
이렇게 생성된 Namespace 에서는 `default` ServiceAccount 만 존재하며, 이미지 스트림이나 빌드 구성을 바로 사용할 수 없습니다.

---

## 4. ResourceQuota 와 LimitRange 연동

Project 는 리소스 오버컨슈머를 방지하기 위해 ResourceQuota 와 LimitRange 를 기본으로 지원합니다.

### ResourceQuota
Project 전체의 리소스 사용량을 제한합니다.
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-template
  namespace: my-project
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    persistentvolumeclaims: "5"
```

### LimitRange
Namespace 내의 Pod 인스턴스당 최소/최대 리소스 한도를 설정합니다.
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: my-project
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: 512Mi
      defaultRequest:
        cpu: "100m"
        memory: 128Mi
      max:
        cpu: "2"
        memory: 4Gi
      min:
        cpu: "50m"
        memory: 64Mi
```
**팁**: `oc new-project` 명령어를 실행할 때 `--resource-quota` 플래그를 사용하여 즉시 커스텀 쿼otas 를 적용할 수 있습니다.

---

## 5. RBAC 연동 및 역할 관리

OCP Project 는 세 가지 기본 역할 (Role) 을 제공합니다.

1.  **admin**: Project 내 모든 리소스에 대한 완전한 제어 권한.
2.  **edit**: 리소스 수정, 삭제, 생성 가능 (Read-only 제외).
3.  **view**: 리소스 조회 및 모니터링만 가능 (수정 불가).

### RoleBinding 예시
사용자나 그룹에 특정 역할을 부여합니다.
```bash
# admin 역할 부여
oc adm policy add-role-to-user admin developer@dev-group

# view 역할 부여
oc adm policy add-role-to-user view developer@dev-group

# ServiceAccount 에 역할 부여 (예: CI/CD 파이프라인용)
oc adm policy add-scc-to-user anyuid -z build
```
**주의**: OCP 의 `oc adm policy` 명령어는 Project 레벨의 RBAC 를 관리하는 데 필수적입니다.

---

## 6. Project 템플릿 커스터마이징

OCP 는 Project 생성 시 기본 템플릿을 제공합니다. 이 템플릿을 수정하여 조직별 표준을 만들 수 있습니다.

### 기본 템플릿 위치
기본 템플릿은 `openshift/template` 프로젝트에 정의되어 있습니다.
```bash
oc get templates -n openshift/template
```

### 커스터마이징 방법
1.  템플릿 파일을 복사합니다 (`template.yaml`).
2.  `spec.parameters` 또는 `metadata.labels` 를 수정하여 기본값을 변경합니다.
3.  수정된 템플릿을 `openshift/template` 프로젝트의 `templates` 디렉토리에 업로드합니다.
    ```bash
    # 예시: 수정된 템플릿 적용
    oc apply -f ./custom-app-template.yaml -n openshift/template
    ```
이후 `oc new-project` 시 이 커스터마이징된 템플릿이 기본값으로 적용됩니다.

---

## 7. 멀티테넌시: 팀/환경 분리 전략

Project 는 멀티테넌시 구현의 핵심 도구입니다.

*   **팀 기반 분리**: 개발팀, QA 팀, 운영팀별로 별도의 Project 를 생성하여 코드와 설정을 격리합니다.
*   **환경 기반 분리**: Dev, Staging, Production 환경별로 Project 를 분리하여 데이터 격리와 보안 정책을 다르게 적용합니다.
*   **전략적 이점**:
    *   **보안**: 한 팀의 실수가 다른 팀의 Production 환경으로 확산되는 것을 방지.
    *   **관리**: 각 팀의 ResourceQuota 를 독립적으로 관리하여 특정 팀이 리소스를 독점하는 것을 방지.
    *   **네트워크**: Project 레벨에서 NetworkPolicy 를 적용하여 팀 간 트래픽을 차단 가능.

---

## 8. 실무 팁 및 주의사항

### 네이밍 컨벤션
*   프로젝트 이름은 소문자, 하이픈 (`-`) 만 사용하세요 (예: `team-a-dev`, `prod-db-cluster`).
*   대문자나 특수문자 (`_`, `.`) 는 일부 OCP 기능과 호환성이 떨어질 수 있습니다.

### 라벨 전략 (Label Strategy)
Project 내 리소스 관리에 라벨을 체계적으로 사용하세요.
*   `team`: 담당 팀명 (`app-team-a`)
*   `environment`: 환경 (`dev`, `staging`, `prod`)
*   `cost-center`: 비용 중심 (`cc-100`)
