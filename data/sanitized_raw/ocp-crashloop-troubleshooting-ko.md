<!-- source: ocp-crashloop-troubleshooting-ko.md -->

# OCP/Kubernetes CrashLoopBackOff 트러블슈팅 가이드

## 개요

Pod가 `CrashLoopBackOff` 상태에 빠지면 컨테이너가 시작 직후 반복적으로 종료되고 있는 것입니다. Kubernetes는 재시작 간격을 점점 늘리며(BackOff) 계속 재시도합니다.

## CrashLoopBackOff 관련 에러 상태

| 에러 상태 | 설명 |
|---|---|
| CrashLoopBackOff | 컨테이너가 반복 크래시 → 대기 간격이 점점 길어짐 (10s, 20s, 40s, ..., 최대 5분) |
| Error | 컨테이너가 비정상 종료 (exit code != 0) |
| OOMKilled | 메모리 부족으로 컨테이너가 강제 종료됨 |

## 원인별 진단 및 해결 방법

### 1. 애플리케이션 에러 (가장 흔한 원인)

애플리케이션 코드에 버그가 있거나 설정이 잘못되어 시작 직후 종료되는 경우입니다.

**진단:**
```bash
# Pod 로그 확인 (현재 컨테이너)
oc logs <pod-name> -n <namespace>

# 이전 크래시된 컨테이너 로그 (--previous 플래그)
oc logs <pod-name> --previous -n <namespace>

# Pod 이벤트 확인
oc describe pod <pod-name> -n <namespace>
# Last State 섹션에서 Exit Code 확인
```

**해결:**
- Exit Code 1: 애플리케이션 에러 → 로그에서 에러 메시지 확인 후 코드/설정 수정
- Exit Code 137: SIGKILL (OOMKilled 가능성) → 메모리 리소스 확인
- Exit Code 0: 정상 종료인데 반복 → 컨테이너가 데몬 프로세스가 아닌 경우 (foreground 실행 필요)

### 2. OOMKilled (메모리 부족)

컨테이너가 설정된 메모리 제한을 초과하여 강제 종료된 경우입니다.

**진단:**
```bash
# Pod 상태에서 OOMKilled 확인
oc get pod <pod-name> -o jsonpath='{.status.containerStatuses[*].lastState}'

# describe에서 Reason: OOMKilled 확인
oc describe pod <pod-name>
# Last State:
#   Reason: OOMKilled
#   Exit Code: 137
```

**해결:**
```bash
# 현재 메모리 제한 확인
oc get deployment <deploy-name> -o jsonpath='{.spec.template.spec.containers[*].resources}'

# 메모리 제한 늘리기
oc set resources deployment/<deploy-name> --limits=memory=512Mi --requests=memory=256Mi

# 또는 YAML 직접 수정
oc edit deployment <deploy-name>
# spec.template.spec.containers[].resources.limits.memory 수정
```

### 3. 설정 파일/환경 변수 누락

필수 ConfigMap, Secret, 환경 변수가 없어서 애플리케이션이 시작에 실패하는 경우입니다.

**진단:**
```bash
# Pod 로그에서 설정 관련 에러 확인
oc logs <pod-name> --previous

# ConfigMap/Secret 존재 여부 확인
oc get configmap -n <namespace>
oc get secret -n <namespace>

# Pod에 마운트된 볼륨 확인
oc get pod <pod-name> -o jsonpath='{.spec.volumes}'
```

**해결:**
- 누락된 ConfigMap/Secret 생성
- 환경 변수 설정 확인 (`oc set env deployment/<name> KEY=VALUE`)
- 볼륨 마운트 경로 확인

### 4. Liveness Probe 실패

Liveness Probe가 너무 엄격하게 설정되어 애플리케이션이 초기화되기 전에 컨테이너를 죽이는 경우입니다.

**진단:**
```bash
# Pod 이벤트에서 Liveness probe failed 메시지 확인
oc describe pod <pod-name>
# Events:
#   Liveness probe failed: HTTP probe failed with statuscode: 503
```

**해결:**
```yaml
# initialDelaySeconds를 늘리거나 startupProbe 추가
spec:
  containers:
  - name: myapp
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 30    # 시작 대기 시간 늘림
      periodSeconds: 10
      failureThreshold: 5        # 실패 허용 횟수 늘림
    startupProbe:                # 시작 시에만 적용되는 프로브
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
```

### 5. 컨테이너 명령어 오류

Dockerfile의 ENTRYPOINT/CMD가 잘못되었거나 Deployment의 command/args가 틀린 경우입니다.

**진단:**
```bash
# 컨테이너 명령어 확인
oc get deployment <deploy-name> -o jsonpath='{.spec.template.spec.containers[*].command}'
oc get deployment <deploy-name> -o jsonpath='{.spec.template.spec.containers[*].args}'
```

**해결:**
- 올바른 실행 명령어로 수정
- Shell form vs Exec form 확인 (`["sh", "-c", "..."]` vs 직접 실행)

## 일반적인 디버깅 순서

1. `oc get pods` 로 CrashLoopBackOff 상태 확인
2. `oc logs <pod> --previous` 로 이전 크래시 로그 확인
3. `oc describe pod <pod>` 로 Exit Code, Events 확인
4. Exit Code에 따라 원인 분류:
   - 137 → OOMKilled → 메모리 늘림
   - 1 → 애플리케이션 에러 → 로그 분석
   - 0 → 정상 종료 반복 → foreground 실행 확인
5. 수정 후 재배포: `oc rollout restart deployment/<name>`

## 자주 사용하는 명령어 요약

```bash
# 이전 크래시 로그 확인 (가장 중요!)
oc logs <pod-name> --previous -n <namespace>

# Pod 상태 상세 (Exit Code, 이벤트)
oc describe pod <pod-name> -n <namespace>

# 메모리 리소스 확인
oc get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'

# 메모리 제한 변경
oc set resources deployment/<name> --limits=memory=512Mi

# Pod 재시작
oc rollout restart deployment/<name>
```
