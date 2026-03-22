<!-- source: ocp-cicd-ko.md -->

# OpenShift CI/CD 및 GitOps 실무 가이드

## 1. CI/CD 개요: 왜 필요한가?

현대 소프트웨어 개발에서 **CI/CD (Continuous Integration / Continuous Delivery or Deployment)** 는 개발 주기를 단축하고 배포 위험을 최소화하기 위한 핵심 실천 방법입니다.

*   **지속적 통합 (CI)**: 개발자가 코드를 자주 브랜치에 병합할 때, 자동화된 빌드 및 테스트 프로세스가 실행되어 통합 오류를 즉시 발견합니다. 이는 "작은 변경, 자주 통합" 원칙을 통해 대형 배포 시 발생할 수 있는 충돌을 방지합니다.
*   **지속적 배포 (CD)**: 검증된 코드를 자동으로 프로덕션 환경으로 배포하는 과정입니다. 수동 개입을 줄여 배포 속도를 높이고, 롤백 (Rollback) 을 신속하게 수행할 수 있게 합니다.

OpenShift는 Kubernetes 기반의 PaaS 플랫폼으로, 내장된 **OpenShift Pipelines (Tekton 기반)** 와 **OpenShift GitOps Operator**를 통해 엔터프라이즈급의 CI/CD 및 GitOps 워크플로우를 제공합니다. 이는 복잡한 마이크로서비스 아키텍처에서 신뢰할 수 있는 소프트웨어 공급망 (Software Supply Chain) 을 구축하는 데 필수적입니다.

---

## 2. OCP 빌드 전략 비교

OpenShift 는 애플리케이션 소스를 이미지로 변환하는 다양한 빌드 전략을 제공합니다. 각 전략은 사용 사례와 복잡도에 따라 선택되어야 합니다.

| 전략명 | 설명 | 주요 특징 | 적합한 시나리오 |
| :--- | :--- | :--- | :--- |
| **Source-to-Image (S2I)** | 소스 코드를 받아 기본 이미지 (Base Image) 에 의존성을 설치하고 애플리케이션을 실행 가능한 이미지로 만듦. | - 개발 환경과 실행 환경 격리<br>- 빌드 컨테이너가 애플리케이션 컨테이너와 분리됨<br>- `.dockerfile` 또는 `.s2i` 스크립트 사용 | - 표준 프레임워크 (Java, Node.js 등) 기반 애플리케이션<br>- 보안 요구사항이 높은 환경 |
| **Docker Build** | Dockerfile 을 직접 사용하여 이미지를 빌드하는 전통적인 방식. | - Dockerfile 에 대한 완전한 제어권<br>- S2I 보다 유연하지만, 빌드 컨테이너가 애플리케이션 컨테이너와 공유될 수 있음 | - S2I 로 지원되지 않는 특수한 애플리케이션<br>- Dockerfile 이 이미 최적화된 경우 |
| **Pipeline Build** | OpenShift Pipeline (Tekton) 을 사용하여 복잡한 의존성 해결, 다단계 빌드, 테스트를 포함한 파이프라인 실행. | - 외부 레지스트리 연동 가능<br>- 빌드 단계와 테스트 단계를 명확히 분리<br>- CI/CD 파이프라인과 통합 용이 | - 복잡한 다단계 빌드 필요<br>- 빌드 결과물을 즉시 다른 파이프라인으로 전달해야 할 때 |

---

## 3. Tekton: 클라우드 네이티브 CI/CD 파이프라인

OpenShift 의 CI/CD 엔진인 **Tekton**은 Kubernetes 네이티브인 Go 언어로 작성된 오픈소스 프로젝트입니다. Tekton 은 작업을 세분화된 단위로 나누어 유연한 파이프라인을 구성할 수 있게 합니다.

### 핵심 개념
*   **Task (작업)**: CI/CD 파이프라인의 최소 단위로, 특정 작업을 수행하는 코드 블록입니다 (예: 소스 클론, 빌드 실행, 단위 테스트). Task 는 입력 (Inputs) 과 출력 (Outputs) 을 가지며, 다른 Task 와 독립적으로 실행될 수 있습니다.
*   **Pipeline (파이프라인)**: 여러 Task 를 순차적 또는 병렬적으로 연결하여 하나의 워크플로우를 정의합니다. 파이프라인은 Task 를 실행할 수 있는 환경 (Pod 템플릿) 을 정의합니다.
*   **PipelineRun (파이프라인 실행)**: 정의된 파이프라인을 실제로 실행하는 인스턴스입니다. 파라미터를 변경하여 동일한 파이프라인을 여러 번 실행할 수 있으며, 실행 결과를 추적할 수 있습니다.

---

## 4. Tekton 파이프라인 YAML 예시

다음은 소스 코드 클론 → 빌드 → 이미지 푸시 및 배포를 수행하는 간단한 Tekton 파이프라인 예시입니다.

```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: simple-app-pipeline
spec:
  workspaces:
    - name: source
  tasks:
    - name: clone-source
      taskRef:
        name: git-clone
      params:
        - name: url
          value: https://github.com/example/my-app.git
        - name: revision
          value: main
      workspaces:
        - name: output
          workspace: source
    - name: build-image
      runAfter: [clone-source]
      taskRef:
        name: docker-build
      params:
        - name: IMAGE
          value: quay.io/myorg/my-app:latest
        - name: DOCKERFILE
          value: Dockerfile
      workspaces:
        - name: source
          workspace: source
    - name: push-image
      runAfter: [build-image]
      taskRef:
        name: docker-push
      params:
        - name: IMAGE
          value: quay.io/myorg/my-app:latest
      workspaces:
        - name: source
          workspace: source
    - name: deploy
      runAfter: [push-image]
      taskRef:
        name: deploy-app
      params:
        - name: IMAGE
          value: quay.io/myorg/my-app:latest
      workspaces:
        - name: source
          workspace: source
```

이 파이프라인을 실행하려면 `PipelineRun` 리소스를 생성합니다:
```bash
oc create pr simple-app-pipeline --param IMAGE=quay.io/myorg/my-app:latest
```

---

## 5. GitOps 개념: 선언적 인프라 관리

**GitOps**는 Git 저장소를 인프라 및 애플리케이션의 **Single Source of Truth (단일 진실 공급원)** 으로 삼는 운영 방법론입니다.

*   **선언적 관리**: "시스템이 어떤 상태여야 하는가"를 Git 의 파일 (YAML 등) 로 정의합니다. 시스템의 실제 상태가 Git 의 정의와 다르면, GitOps 도구 (ArgoCD 등) 가 자동으로 상태를 동기화하여 일치시킵니다.
*   **이점**:
    *   **검증 가능성**: 모든 변경 사항이 Git 커밋으로 남기 때문에 누가, 언제, 무엇을 변경했는지 감사 로그가 완벽하게 확보됩니다.
    *   **재현성**: Git 저장소를 복제하는 것만으로 환경 (Dev, Stage, Prod) 을 즉시 재현할 수 있습니다.
    *   **자동 복구**: 의도치 않은 변경 사항이 발생하면 이전 버전으로 Git 을 되돌리기만 하면 시스템이 자동으로 복구됩니다.

---

## 6. ArgoCD: 개념 및 OCP 통합

**ArgoCD**는 Kubernetes 네이티브인 GitOps 오토메이션 도구로, OpenShift 에서 널리 사용됩니다.

*   **작동 원리**: ArgoCD 는 Git 저장소를 지속적으로 스캔하여 `Application` CRD (Custom Resource Definition) 로 정의된 Desired State 와 클러스터의 Actual State 를 비교합니다. 불일치가 감지되면 자동으로 수정 작업을 수행합니다.
*   **Application CRD**: ArgoCD 는 `Application`이라는 리소스를 통해 관리 대상 (Target Cluster) 과 소스 (Git Repo, Path, Revision) 를 정의합니다.
    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Application
    metadata:
      name: my-app
      namespace: argocd
    spec:
      project: default
      source:
        repoURL: https://github.com/example/my-app.git
        targetRevision: HEAD
        path: k8s
      destination:
        server: https://kubernetes.default.svc
        namespace: production
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
    ```

---

## 7. OpenShift GitOps Operator 설치 및 기본 사용법

OpenShift 는 ArgoCD 를 쉽게 설치하고 관리하기 위해 **OpenShift GitOps Operator**를 제공합니다. 이는 ArgoCD 를 Helm 차트 대신 Operator Lifecycle Manager (OLM) 을 통해 설치합니다.

### 설치 방법
1.  OpenShift CLI (`oc`) 로 GitOps Operator 구독을 활성화합니다.
2.  `openshift-gitops-operator` 라는 이름으로 구독을 생성합니다.
    ```bash
    oc apply -f https://github.com/openshift/openshift-gitops-operator/releases/download/v1.2.0/openshift-gitops-operator.yaml
    ```
3.  설치 상태를 확인합니다.
    ```bash
    oc get subscription openshift-gitops-operator -n openshift-gitops
    ```

### 기본 사용법
1.  **ArgoCD UI 접속**: 설치 완료 후 `argocd` 서비스의 라우팅 규칙을 확인하여 UI URL 을 얻습니다.
2.  **CLI 토큰 생성**:
    ```bash
