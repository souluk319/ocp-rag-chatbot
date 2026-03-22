<!-- source: ocp-commands.md -->

# OCP oc CLI 명령어 가이드

## 기본 명령어

### 로그인/로그아웃
```bash
# 클러스터 로그인
oc login https://api.cluster.example.com:6443 -u admin -p password

# 토큰으로 로그인
oc login --token=[REDACTED_SECRET] --server=https://api.cluster.example.com:6443

# 현재 사용자 확인
oc whoami

# 로그아웃
oc logout
```

### 프로젝트 관리
```bash
# 프로젝트 목록
oc projects

# 프로젝트 전환
oc project my-project

# 새 프로젝트 생성
oc new-project my-app --description="My Application"

# 프로젝트 삭제
oc delete project my-project
```

### Pod 관리
```bash
# Pod 목록 조회
oc get pods
oc get pods -o wide  # 상세 정보
oc get pods --all-namespaces  # 전체 네임스페이스

# Pod 상세 정보
oc describe pod <pod-name>

# Pod 로그 확인
oc logs <pod-name>
oc logs -f <pod-name>  # 실시간 로그
oc logs <pod-name> -c <container-name>  # 특정 컨테이너

# Pod 접속
oc rsh <pod-name>
oc exec -it <pod-name> -- /bin/bash

# Pod 삭제
oc delete pod <pod-name>
```

### Deployment 관리
```bash
# Deployment 목록
oc get deployments

# Deployment 생성
oc create deployment nginx --image=nginx:latest

# 스케일링
oc scale deployment nginx --replicas=3

# 롤아웃 상태 확인
oc rollout status deployment/nginx

# 롤백
oc rollout undo deployment/nginx
```

### Service & Route
```bash
# Service 목록
oc get services

# Service 생성 (Pod 노출)
oc expose deployment nginx --port=80

# Route 생성 (외부 노출)
oc expose service nginx

# Route에 TLS 설정
oc create route edge nginx-tls --service=nginx --cert=cert.pem --key=key.pem
```

### 리소스 관리
```bash
# YAML 적용
oc apply -f deployment.yaml

# 리소스 편집
oc edit deployment nginx

# 리소스 삭제
oc delete -f deployment.yaml

# 리소스 내보내기
oc get deployment nginx -o yaml > deployment.yaml
```

### 디버깅
```bash
# 이벤트 확인
oc get events --sort-by=.lastTimestamp

# 노드 상태 확인
oc get nodes
oc describe node <node-name>

# 리소스 사용량 확인
oc adm top pods
oc adm top nodes

# Debug 컨테이너
oc debug deployment/nginx
```

## 주요 팁
1. `-o json` 또는 `-o yaml`으로 상세 출력 가능
2. `--dry-run=client -o yaml`으로 YAML 생성 가능
3. `oc explain <resource>`로 리소스 스펙 확인 가능
4. `oc api-resources`로 사용 가능한 리소스 타입 목록 확인
