<!-- source: ocp-troubleshooting.md -->

# OCP 트러블슈팅 가이드

## Pod 상태 이상

### CrashLoopBackOff
Pod가 반복적으로 시작 후 즉시 종료되는 상태입니다.

**원인:**
- 애플리케이션 코드 오류 (시작 시 예외 발생)
- 잘못된 컨테이너 설정 (command, args)
- 필요한 환경변수 또는 ConfigMap/Secret 누락
- 리소스 부족 (OOMKilled)

**해결 방법:**
1. `oc logs <pod-name> --previous` 로 이전 실행 로그 확인
2. `oc describe pod <pod-name>` 으로 이벤트와 상태 확인
3. Exit Code 확인:
   - Exit Code 1: 애플리케이션 에러
   - Exit Code 137: OOMKilled (메모리 부족)
   - Exit Code 143: SIGTERM으로 종료됨
4. 리소스 limits 확인 및 조정

### ImagePullBackOff
컨테이너 이미지를 가져오지 못하는 상태입니다.

**원인:**
- 이미지 이름 또는 태그 오타
- Private 레지스트리 인증 실패
- 네트워크 문제로 레지스트리 접근 불가
- 이미지가 존재하지 않음

**해결 방법:**
1. `oc describe pod <pod-name>` 에서 이미지 URL 확인
2. 레지스트리에 이미지 존재 여부 확인
3. ImagePullSecret 설정 확인: `oc get secrets`
4. 네트워크 연결 테스트

### Pending 상태
Pod가 스케줄링되지 않고 대기 중인 상태입니다.

**원인:**
- 리소스(CPU, 메모리) 부족
- NodeSelector 또는 Node Affinity 조건 미충족
- PVC가 바인딩되지 않음
- Taint/Toleration 불일치

**해결 방법:**
1. `oc describe pod <pod-name>` 에서 Events 확인
2. `oc adm top nodes` 로 노드 리소스 확인
3. `oc get pvc` 로 PVC 상태 확인
4. 노드 label과 taint 확인

### Evicted
노드의 리소스 압박으로 Pod가 축출된 상태입니다.

**원인:**
- 디스크 공간 부족 (DiskPressure)
- 메모리 부족 (MemoryPressure)
- PID 부족

**해결 방법:**
1. `oc describe node <node-name>` 에서 Conditions 확인
2. 노드의 디스크 공간 확보
3. 불필요한 이미지/컨테이너 정리
4. Resource Requests/Limits 적절히 설정

## 네트워크 문제

### Service 접근 불가
**확인 사항:**
1. `oc get endpoints <service-name>` - Endpoint가 존재하는지 확인
2. Pod의 label과 Service의 selector가 일치하는지 확인
3. Pod가 정상 Running 상태인지 확인
4. targetPort가 컨테이너의 실제 리스닝 포트와 일치하는지 확인

### Route 접근 불가
**확인 사항:**
1. `oc get route` 로 Route 상태 확인
2. Router Pod가 정상 동작 중인지 확인
3. DNS 해석이 올바른지 확인
4. TLS 인증서 유효성 확인 (HTTPS Route인 경우)

## 스토리지 문제

### PVC Pending
**원인:**
- 사용 가능한 PV가 없음
- StorageClass가 존재하지 않음
- 요청한 용량을 만족하는 PV가 없음

**해결 방법:**
1. `oc get pv` 로 사용 가능한 PV 확인
2. `oc get storageclass` 로 StorageClass 확인
3. Dynamic Provisioning 설정 확인
4. 요청 용량 조정

## 인증/권한 문제

### 403 Forbidden
**확인 사항:**
1. `oc auth can-i <verb> <resource>` 로 권한 확인
2. Role/ClusterRole 바인딩 확인
3. ServiceAccount 권한 확인
4. SCC(Security Context Constraints) 확인

### SCC 관련 오류
OCP에서는 보안을 위해 SCC를 통해 Pod의 보안 컨텍스트를 제한합니다.

**일반적인 오류:**
- "unable to validate against any security context constraint"
- root 권한 실행 거부

**해결 방법:**
1. `oc get scc` 로 사용 가능한 SCC 확인
2. `oc adm policy add-scc-to-user anyuid -z <sa-name>` (주의: 보안 위험)
3. Dockerfile에서 non-root 사용자로 변경하는 것을 권장
