<!-- source: ocp-image-pull-troubleshooting-ko.md -->

# OCP/Kubernetes 이미지 풀(Pull) 에러 트러블슈팅 가이드

## 개요

컨테이너 배포 시 가장 자주 발생하는 에러 중 하나가 이미지 풀(Image Pull) 에러입니다. Pod가 `ImagePullBackOff` 또는 `ErrImagePull` 상태에 빠지면 컨테이너 이미지를 레지스트리에서 다운로드하지 못한 것입니다.

## 이미지 풀 에러 종류

| 에러 상태 | 설명 |
|---|---|
| ErrImagePull | 이미지 풀 시도 중 에러 발생 (첫 번째 시도) |
| ImagePullBackOff | 이미지 풀 반복 실패 후 대기 상태 (BackOff 간격이 점점 길어짐) |
| InvalidImageName | 이미지 이름/태그 형식이 잘못됨 |

## 원인별 진단 및 해결 방법

### 1. 이미지 이름 또는 태그 오류

가장 흔한 원인입니다. 이미지 경로나 태그에 오타가 있는 경우입니다.

**진단:**
```bash
# Pod 이벤트 확인
oc describe pod <pod-name> -n <namespace>
# 또는
kubectl describe pod <pod-name> -n <namespace>

# Events 섹션에서 다음과 같은 메시지 확인:
# Failed to pull image "nginx:latst": rpc error: manifest unknown
```

**해결:**
```bash
# Deployment에서 이미지 경로 확인
oc get deployment <deploy-name> -o yaml | grep image:

# 올바른 이미지로 수정
oc set image deployment/<deploy-name> <container-name>=nginx:latest
```

### 2. Private 레지스트리 인증 실패 (Pull Secret 미설정)

Private 레지스트리에서 이미지를 받으려면 인증 정보(Pull Secret)가 필요합니다.

**진단:**
```bash
# Pod 이벤트에서 인증 에러 확인
oc describe pod <pod-name>
# 메시지 예시: unauthorized: authentication required
# 또는: no basic auth credentials

# 현재 네임스페이스의 Pull Secret 확인
oc get secrets -n <namespace> | grep pull
```

**해결:**
```bash
# 1. Docker 레지스트리용 Secret 생성
oc create secret docker-registry my-pull-secret \
  --docker-server=registry.example.com \
  --docker-username=[REDACTED_ACCOUNT] \
  --docker-password=[REDACTED_SECRET] \
  --docker-email=[REDACTED_ACCOUNT] \
  -n <namespace>

# 2-A. Pod에 imagePullSecrets 추가 (Deployment YAML)
# spec:
#   template:
#     spec:
#       imagePullSecrets:
#       - name: my-pull-secret

# 2-B. 또는 ServiceAccount에 Secret 연결 (네임스페이스 전체 적용)
oc secrets link default my-pull-secret --for=pull -n <namespace>
oc secrets link builder my-pull-secret -n <namespace>
```

### 3. OCP 글로벌 Pull Secret 문제

OpenShift는 클러스터 전체에 적용되는 글로벌 Pull Secret이 있습니다. Red Hat 레지스트리(registry.redhat.io) 접근에 필요합니다.

**진단:**
```bash
# 글로벌 pull-secret 확인
oc get secret pull-secret -n openshift-config -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d | jq .
```

**해결:**
```bash
# 글로벌 Pull Secret 업데이트
oc set data secret/pull-secret -n openshift-config \
  --from-file=.dockerconfigjson=<new-pull-secret.json>
```

### 4. 이미지가 존재하지 않음

이미지 자체가 레지스트리에 없거나 삭제된 경우입니다.

**진단:**
```bash
# 이미지 존재 여부 확인 (Docker/Podman)
podman pull <image-name>:<tag>
# 또는
skopeo inspect docker://<image-name>:<tag>

# OCP 내부 레지스트리 이미지 확인
oc get imagestream -n <namespace>
oc get imagestreamtag -n <namespace>
```

**해결:**
- 올바른 이미지 태그 확인 (latest 대신 특정 버전 사용 권장)
- 이미지를 빌드하고 레지스트리에 Push
- ImageStream을 사용하는 경우 올바른 태그 확인

### 5. 네트워크 문제 (레지스트리 접근 불가)

노드에서 외부 레지스트리에 접근할 수 없는 경우입니다.

**진단:**
```bash
# 노드에서 레지스트리 접근 테스트
oc debug node/<node-name> -- chroot /host curl -v https://registry.redhat.io/v2/

# DNS 확인
oc debug node/<node-name> -- chroot /host nslookup registry.redhat.io

# 프록시 설정 확인
oc get proxy cluster -o yaml
```

**해결:**
- 방화벽에서 레지스트리 도메인 허용
- 프록시 설정 확인 및 수정
- Air-gapped 환경이면 미러 레지스트리 구성

### 6. ImagePullPolicy 설정 문제

`imagePullPolicy: Always`로 설정된 경우 매번 레지스트리에서 풀을 시도합니다.

**설정 옵션:**

| imagePullPolicy | 동작 |
|---|---|
| Always | 항상 레지스트리에서 풀 (latest 태그 기본값) |
| IfNotPresent | 로컬에 없을 때만 풀 (특정 태그 기본값) |
| Never | 로컬 이미지만 사용, 풀 안 함 |

```yaml
spec:
  containers:
  - name: myapp
    image: myapp:v1.2.3
    imagePullPolicy: IfNotPresent
```

## 일반적인 디버깅 순서

1. `oc get pods` 로 Pod 상태 확인 (ImagePullBackOff / ErrImagePull)
2. `oc describe pod <pod-name>` 으로 Events 섹션의 에러 메시지 확인
3. 에러 메시지에 따라 위 원인별 해결 방법 적용
4. 수정 후 Pod 재시작: `oc delete pod <pod-name>` (Deployment가 자동 재생성)

## 자주 사용하는 명령어 요약

```bash
# Pod 상태 확인
oc get pods -n <namespace>

# Pod 이벤트/에러 상세 확인
oc describe pod <pod-name> -n <namespace>

# Deployment 이미지 확인
oc get deployment <name> -o jsonpath='{.spec.template.spec.containers[*].image}'

# 이미지 변경
oc set image deployment/<name> <container>=<new-image>:<tag>

# Pull Secret 생성
oc create secret docker-registry <secret-name> \
  --docker-server=<registry> \
  --docker-username=[REDACTED_ACCOUNT] \
  --docker-password=[REDACTED_SECRET]

# Pull Secret을 ServiceAccount에 연결
oc secrets link default <secret-name> --for=pull

# Pod 강제 재시작
oc rollout restart deployment/<name>
```
