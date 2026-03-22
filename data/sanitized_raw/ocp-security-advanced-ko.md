<!-- source: ocp-security-advanced-ko.md -->

# OpenShift Container Platform (OCP) 보안 심화 가이드

## 1. 서론: OCP 보안 아키텍처의 중요성

OpenShift Container Platform 은 Kubernetes 의 기업용 분산 플랫폼으로, 클라우드 네이티브 애플리케이션의 생명주기 관리를 제공합니다. Kubernetes 는 자체적으로 강력한 보안 기능을 제공하지만, 다중 테넌트 (Multi-tenant) 환경이나 규제 준수 (Compliance) 가 필요한 기업 환경에서는 추가적인 보안 레이어가 필수적입니다. OCP 는 Kubernetes 의 기본 기능을 확장하여 **SCC (Security Context Constraints)**, **Pod Security Standards**, 그리고 통합된 네트워킹 및 이미지 관리 시스템을 제공함으로써, '보안 by Design' 접근 방식을 실현합니다. 본 가이드는 신입 엔지니어가 OCP 의 핵심 보안 메커니즘을 이해하고 실무에서 적용할 수 있도록 구성되었습니다.

---

## 2. SCC (Security Context Constraints)

### 개념 설명
Kubernetes 의 `SecurityContext` 는 컨테이너 실행 시 권한, 사용자, 그룹 등을 제어하는 기본적인 설정입니다. 그러나 다중 테넌트 환경에서 모든 사용자가 동일한 수준의 권한을 가질 수 없으므로, OCP 는 이를 강화한 **SCC**를 도입했습니다. SCC 는 클러스터 전체에 적용될 수 있는 보안 컨텍스트의 집합으로, 특정 사용자가 생성한 Pod 가 준수해야 할 보안 규칙을 강제합니다.

### 기본 SCC 종류
OCP 는 기본 제공되는 여러 SCC 를 포함하며, 각 SCC 는 허용되는 보안 컨텍스트를 정의합니다.

| SCC 이름 | 설명 | 주요 특징 |
| :--- | :--- | :--- |
| **privileged** | 가장 높은 권한을 부여 | 루트 권한 실행, 모든 장치 접근 허용. 개발 환경이나 특수한 디버깅 용도로만 사용. |
| **runasany** | 임의의 사용자/그룹 실행 | 특정 UID/GID 로 실행 가능하지만, 루트 권한은 제한됨. |
| **restricted** | **가장 엄격한 설정 (기본값)** | 루트 권한 불가, 특정 UID/GID 만 허용,Capabilities 제한, 비프리티 이미지만 허용. |
| **hostnetwork** | 호스트 네트워크 사용 | 호스트 네트워킹 스택 직접 사용 가능. |
| **hostpid** | 호스트 PID 네임스페이스 사용 | 호스트 프로세스 ID 공간 공유 가능. |
| **hostipc** | 호스트 IPC 네임스페이스 사용 | 호스트 인터프로세스 통신 공간 공유 가능. |
| **nonroot** | 비루트 실행 강제 | 루트로 실행하는 컨테이너를 차단. |

**주의사항:** `privileged` SCC 는 공격 표면적을 극대화하므로, 프로덕션 환경에서는 절대 사용하지 말아야 합니다.

---

## 3. Pod Security Standards (PSS)

### 개념 설명
PSS 는 SCC 보다 더 추상화된 개념으로, Pod 의 보안 설정에 대한 세 가지 표준을 정의합니다. OCP 는 이 표준을 SCC 와 연동하여 자동으로 적용합니다.

| 표준 (Standard) | 설명 | 적용 범위 및 목적 |
| :--- | :--- | :--- |
| **Privileged** | 가장 느슨한 보안 정책 | `privileged` SCC 와 유사. 특수한 워크로드 (예: 모니터링 에이전트, 디버깅) 에만 제한적으로 사용. |
| **Baseline** | 최소한의 보안 요구사항 충족 | `runasany` 및 `nonroot` SCC 와 유사. 호스트 리소스 접근은 금지하지만, 일부 유연성을 제공. |
| **Restricted** | **가장 엄격한 보안 정책** | `restricted` SCC 와 동등. 루트 실행, 호스트 네임스페이스 사용, Capability 확장 등 대부분의 위험 행위를 차단. |

### 실무 적용
OCP 클러스터의 모든 프로젝트 (Namespace) 는 기본적으로 `restricted` PSS 를 따르도록 설정되어 있습니다. 사용자가 `restricted` 기준에 맞지 않는 Pod 만을 생성하려면, 해당 프로젝트의 PSS 를 `baseline` 또는 `privileged` 로 변경하거나, 해당 Pod 에 대해 예외를 주는 SCC 를 할당해야 합니다.

---

## 4. RBAC 심화: 최소 권한 원칙

### 개념 설명
Role-Based Access Control (RBAC) 은 OCP 의 핵심 인증 및 권한 부여 메커니즘입니다. 역할 (Role) 기반 접근 제어는 사용자에게 필요한 최소한의 권한만 부여하여, 권한 남용이나 사고 발생 시 피해를 최소화합니다.

### Role vs ClusterRole
*   **Role**: 특정 **Namespace** 내에서만 유효한 권한을 정의합니다.
*   **ClusterRole**: 클러스터 전체 (**All Namespaces**) 에서 유효한 권한을 정의합니다.

### ServiceAccount 보안
Pod 이 클러스터 리소스에 접근하려면 `ServiceAccount` 가 필요합니다. 개발자는 기본 `default` 계정을 사용해서는 안 되며, 전용 ServiceAccount 를 생성하고 최소 권한의 Role 을 바인딩해야 합니다.

### 명령어 예시
```bash
# 1. 최소 권한의 Role 생성 (Namespace level)
cat <<EOF | oc create -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: my-project
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
EOF

# 2. ServiceAccount 생성 및 RoleBinding
cat <<EOF | oc create -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-project
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-sa-binding
  namespace: my-project
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: my-project
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
EOF
```

---

## 5. 네트워크 보안: NetworkPolicy

### 개념 설명
Kubernetes 의 기본 네트워크 모델은 'Allow All' (모든 Pod 간 통신 허용) 입니다. OCP 는 **NetworkPolicy** 를 통해 마이크로세그멘테이션 (Micro-segmentation) 을 구현하여, Pod 간 통신을 명시적으로 제어할 수 있습니다.

### 동작 원리
NetworkPolicy 는 'Default Deny' (기본 차단) 전략과 'Allow List' (허용 목록) 전략을 결합하여 사용합니다. 먼저 모든 Pod 간 통신을 차단한 뒤, 필요한 트래픽만 허용합니다.

### YAML 예시
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

---

## 6. 이미지 보안: 신뢰성 확보

### 개념 설명
공격자는 취약점을 가진 이미지나 악성 코드가 포함된 이미지를 배포하여 클러스터를 침투할 수 있습니다. OCP 는 이미지 스캐닝과 서명 검증을 통해 이미지 출처를 검증하고 취약점을 사전에 차단합니다.

### 주요 기능
1.  **Image Digest**: 이미지 태그 대신 Digest 를 사용하여 이미지 무결성을 보장합니다.
2.  **Image Verification**: GPG 서명을 통해 이미지 제작자가 인증되었는지 확인합니다.
3.  **Allowlist**: 승인된 레지스트리 및 이미지만 다운로드하도록 제한합니다.

### 명령어 예시
```bash
# 1. 이미지 스캐닝 (Trivy 또는 Clair 연동 시)
oc adm policy add-cluster-role-to-user image-puller --user=[REDACTED_ACCOUNT]

# 2. 허용된 레지스트리 확인 및 설정
oc get configmap.imageregistry.operator.openshift.io/cluster -o yaml | grep -A 10 "imageContentSources"
```

---

## 7. Secret 관리: 암호화된 데이터 처리

### 개념 설명
비밀번호, API 키, 인증서 등 민감한 정보는 Secret 으로 관리합니다. OCP 는 Secret 을 암호화하여 저장소 (etcd) 에 저장하며, Sealed Secrets 나 HashiCorp Vault 와 연동하여 더 강력한 관리를 제공합니다.

### Sealed Secrets
외부에서 생성된 Secret 을 Base64 로 인코딩하고 서명하여, 클러스터 내부에서만 복호화할 수 있게 합니다. 이는 Git 저장소에 Secret 을 안전하게 푸시할 수 있게 해줍니다.

### Vault 연동 개요
HashiCorp Vault 와 연동하면 Secret 이 etcd 에 영구 저장되지 않고, Vault 에서 동적으로 발급 및 회전 (Rotation) 됩니다.

---

## 8. 감사 (Audit) 로그

### 개념 설명
API 서버의 모든 요청과 응답을 기록하여, 누가 어떤 작업을 수행했는지 추적할 수 있습니다. 이는 보안 사고 조사 및 규정 준수에 필수적입니다.

### 설정 및 분석
1.  **Audit Policy 설정**: `audit-policy.yaml` 파일을 생성하여 감사할 리소스와 동작을 정의합니다.
2.  **Audit Policy 적용**: `oc adm policy` 명령어를 통해 적용합니다.
