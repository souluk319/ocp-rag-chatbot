<!-- source: ocp-build-deploy-ko.md -->

# OCP 빌드 & 배포 전략 가이드

안녕하세요, 신규 엔지니어 여러분.
오늘은 OpenShift Container Platform (OCP) 에서 애플리케이션을 효율적으로 빌드하고 배포하는 핵심 전략에 대해 알아보겠습니다. Kubernetes 기반의 OCP 는 단순한 컨테이너 오케스트레이션을 넘어, 애플리케이션의 수명 주기를 관리하는 강력한 도구들을 제공합니다.

---

## 1. Source-to-Image (S2I): 컨테이너 빌드의 혁신

### 개념과 동작 원리
Source-to-Image (S2I) 는 OpenShift 의 핵심 빌드 전략 중 하나로, 소스 코드와 빌드 스크립트를 기반으로 컨테이너 이미지를 생성하는 프로세스입니다. S2I 는 "이미지 대신 빌드"하는 철학을 따릅니다. 개발자가 직접 `Dockerfile` 을 작성하여 베이스 이미지를 수정할 필요가 없으며, 오히려 **Builder Image**(빌더 이미지) 에 포함된 표준화된 빌드 스크립트를 활용하여 애플리케이션 소스를 가져와서 컴파일하고 설치한 뒤, 결과물을 새로운 애플리케이션 이미지로 추출합니다.

이는 다음과 같은 문제를 해결합니다:
- **베이스 이미지 오염 방지**: 애플리케이션 소스 코드에 빌드 도구 (gcc, maven 등) 가 섞이지 않습니다.
- **재현성 보장**: 동일한 Builder Image 와 소스 코드는 항상 동일한 이미지를 생성합니다.
- **보안 강화**: 불필요한 빌드 환경이 최종 런타임 이미지에 포함되지 않습니다.

### 동작 흐름
1. 소스 코드와 `.dockerfile` (S2I 스크립트) 가 BuildConfig 로 정의됨.
2. BuildPod 가 생성되어 Builder Image 로 시작.
3. 소스 코드를 가져오고, 스크립트 실행, 결과 이미지 추출.
4. 생성된 이미지가 ImageStream 으로 저장됨.

### S2I 빌드 예시
S2I 는 주로 Node.js, Java, Python 등 언어별 공식 Builder Image 를 사용합니다.

```yaml
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: nodejs-app-build
  labels:
    app: my-app
spec:
  source:
    type: Git
    git:
      uri: https://github.com/example/my-app.git
      revision: main
  strategy:
    type: Source
    sourceStrategy:
      from:
        kind: ImageStreamTag
        name: nodejs-18-bookworm-s2i:latest
        namespace: default
  output:
    to:
      kind: ImageStreamTag
      name: nodejs-app:latest
  triggers:
    - type: ImageChange
    - type: ConfigChange
```

---

## 2. Docker Build: 커스터마이징을 위한 빌드 전략

Docker Build 전략은 전통적인 `Dockerfile` 을 기반으로 이미지를 빌드하는 방식입니다. S2I 가 표준화된 스크립트를 사용하는 반면, Docker Build 는 개발자가 직접 모든 빌드 단계 (COPY, RUN, EXPOSE 등) 를 제어할 수 있어 복잡한 빌드 파이프라인이 필요한 경우에 유용합니다.

### BuildConfig YAML 예시
Dockerfile 기반 빌드는 `dockerfile` 속성을 통해 참조합니다.

```yaml
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: custom-java-build
spec:
  source:
    type: Docker
    dockerfile: |
      FROM eclipse-temurin:17-jre-alpine
      WORKDIR /app
      COPY . .
      RUN mvn clean package -DskipTests
      EXPOSE 8080
  strategy:
    type: Docker
    dockerStrategy:
      from:
        kind: ImageStreamTag
        name: docker-remote:latest
  output:
    to:
      kind: ImageStreamTag
      name: java-app:latest
```

---

## 3. BuildConfig: 빌드 트리거 메커니즘

`BuildConfig` 는 애플리케이션의 소스 변경 사항을 감지하여 자동으로 재빌드를 수행하는 트리거를 설정할 수 있습니다.

| 트리거 유형 | 설명 | 사용 시나리오 |
| :--- | :--- | :--- |
| **ConfigChange** | BuildConfig 객체 자체가 변경될 때 (예: 소스 URI 수정, 전략 변경) | 초기 빌드 설정 변경 시 자동 재시작 |
| **ImageChange** | 소스 이미지 (Git, Docker 등) 가 업데이트될 때 | Git 레포지토리에 푸시 시 자동 빌드 |
| **Webhook** | 외부 시스템 (GitHub, Jenkins 등) 에서 HTTP 요청을 보낼 때 | CI/CD 파이프라인 연동 시 수동 또는 자동 트리거 |

---

## 4. 빌드 로그 확인 및 수동 빌드

빌드 과정에서 오류가 발생하거나 로그를 확인해야 할 때는 `oc` 명령어가 필수적입니다.

### 수동 빌드 시작
빌드 트리거 없이 즉시 빌드를 시작하려면 `start-build` 명령어를 사용합니다.

```bash
# 빌드 시작
oc start-build nodejs-app-build --from-context-dir=./local-code

# 빌드 상태 확인
oc get build nodejs-app-build -w
```

### 빌드 로그 확인
빌드 실행 중 발생한 에러 메시지나 진행 상황을 확인합니다.

```bash
# 빌드 로그 출력
oc logs build/nodejs-app-build
```

---

## 5. Rolling 배포: 기본 및 고급 설정

Rolling Update 는 가장 일반적인 배포 전략으로, 기존 Pod 을 점진적으로 종료하고 새로운 Pod 을 시작합니다. 이는 서비스 가용성을 유지하면서 업데이트를 적용합니다.

### maxSurge 와 maxUnavailable 설정
`Deployment` 또는 `DeploymentConfig` 의 `spec.strategy.rollingUpdate` 섹션에서 설정합니다.

- **maxSurge**: 업데이트 중 추가적으로 생성될 Pod 의 최대 개수 (또는 비율).
- **maxUnavailable**: 업데이트 중 일시적으로 서비스를 제공할 수 없는 Pod 의 최대 개수 (또는 비율).

**예시**: 10 개 Pod 이 있는 Deployment 에서 `maxSurge: 25%`, `maxUnavailable: 0` 을 설정하면, 2 개의 새 Pod 을 먼저 생성한 후 기존 Pod 을 하나씩 끕니다.

```yaml
spec:
  strategy:
    type: Rolling
    rollingParams:
      updatePeriodSeconds: 1
      intervalSeconds: 1
      timeoutSeconds: 300
      maxSurge: 25%
      maxUnavailable: 0
```

---

## 6. Blue-Green 배포: 무중단 배포의 정석

Blue-Green 배포는 두 개의 동일한 환경 (Blue 와 Green) 을 준비하는 전략입니다. 현재 운영 중인 버전 (예: Blue) 과 새로운 버전 (예: Green) 이 동시에 존재하며, 트래픽을 완전히 한쪽으로만 전환합니다.

### 동작 방식
1. **Blue 버전 운영**: 기존 트래픽 처리.
2. **Green 버전 배포**: 새로운 코드로 Green Deployment 생성 및 테스트.
3. **Route 전환**: Ingress 또는 Service 의 엔드포인트를 Blue 에서 Green 으로 즉시 변경.
4. **Blue 정리**: Green 이 안정적으로 작동하면 Blue 리소스 삭제.

**장점**: 배포 중 다운타임이 거의 없으며, 롤백 시 원상복구가 매우 빠릅니다.
**단점**: 리소스 사용량이 두 배로 증가할 수 있음.

---

## 7. Canary 배포: 위험 분산 전략

Canary 배포는 새로운 버전의 애플리케이션을 전체 트래픽이 아닌, 소량의 트래픽 (예: 5%) 만에게 먼저 제공하여 안정성을 검증하는 방식입니다.

### Route Weight 활용
OpenShift Route 는 `weight` 속성을 통해 트래픽 분배를 제어할 수 있습니다.

```yaml
spec:
  host: myapp.example.com
  to:
    kind: Service
    name: myapp-service
  port:
    targetPort: 8080
  traffic:
    - kind: Weighted
      weight: 90
      trafficTarget:
        kind: Route
        name: myapp-blue
    - kind: Weighted
      weight: 10
      trafficTarget:
        kind: Route
        name: myapp-green
```

**장점**: 실제 사용자의 피드백을 통해 새로운 버그를 사전에 발견 가능.
**단점**: 설정이 복잡하고, 모니터링이 필수적임.

---

## 8. Rollback: 배포 실패 시 대응

배포 중 문제가 발생하면 즉시 이전 버전으로 되돌려야 합니다. OCP 는 이를 매우 간편하게 지원합니다.

### 명령어 예시
```bash
# DeploymentConfig 기반 롤백 (가장 일반적)
oc rollout undo deploymentconfig/my-app-deploy

# Deployment 기반 롤백
oc rollout undo deployment/my-app-deploy

# 특정 Revision 으로 복원
oc rollout undo deployment/my-app-deploy --to-revision=3
```

---

## 9. 실무 팁 및 주의사항

1. **빌드 캐시 활용**: 동일한 소스 코드로 반복 빌드 시 시간을 단축하기 위해 BuildConfig 에 `build` 속성의 캐시 설정을 활용하거나, `.s2i_cache` 디렉토
