# Gold Corpus Priority For OCP Operations

## 목적

이 문서는 OpenShift 운영 가이드를 위한 골드 코퍼스를 어떤 순서로 쌓을지 고정한다.

핵심 목표는 단순하다.

- 많이 모으는 것보다
- 운영 질문에 바로 답할 수 있는 자료를 먼저 넣는다

즉, `공식 제품 설명서 -> 운영 절차 -> 장애 대응 -> 배경 지식` 순으로 우선순위를 잠근다.

## 현재 판단

OpenShift 챗봇이 실제 운영 가이드로 쓰이려면 OCP 버전 매뉴얼만으로는 부족하다.

필수 코퍼스는 아래 네 층으로 쌓아야 한다.

1. `공식 제품 문서 source`
2. `운영 절차 / 복구 / 검증 문서`
3. `트러블슈팅 / known failure 문서`
4. `Linux baseline / host-level 운영 지식`

## 우선순위 계층

### Priority 0. Official Source Repos

가장 먼저 확보해야 하는 기준 본문이다.

- `openshift/openshift-docs`
  - AsciiDoc source-first 입력
  - `enterprise-4.20` 같은 버전 브랜치 기준
- vendor 공식 저장소에서 AsciiDoc/Markdown 원문을 제공하는 경우
  - HTML single보다 먼저 사용

이 계층의 역할:

- 가장 깨끗한 원문 구조 확보
- 코드 블록, admonition, section hierarchy 보존
- reader-grade book shaping의 기준 입력 제공

### Priority 1. Official Operations Manuals

설명서가 아니라 실제 작업을 닫는 데 필요한 문서다.

- backup / restore
- install / upgrade / migrate
- machine configuration
- certificate rotation
- cluster health / verification
- node recovery
- network validation
- storage recovery

이 계층의 역할:

- `Procedure / Verify / Failure Signals` 중심 북 생성
- buyer가 바로 제품 가치를 느끼는 첫 표면

### Priority 2. Official Troubleshooting And Failure Manuals

장애가 났을 때 어디부터 봐야 하는지를 정리하는 문서다.

- etcd 장애
- API server 접근 불가
- node not ready / degraded
- machine config rollout stuck
- ingress / route 장애
- storage attach / mount 장애
- monitoring / alert 해석
- upgrade blocked / cert expiry / operator degraded

이 계층의 역할:

- 추천질문이 가리키는 진짜 수요를 메운다
- 챗봇이 "개요 설명기"가 아니라 "운영 안내자"로 바뀌게 만든다

### Priority 3. Linux Baseline For OCP Operations

OpenShift 운영 답변의 구멍을 메우는 배경 지식 계층이다.

우선 확보 축:

- `systemd`
- `journald`
- `DNS / dig / resolution`
- `network / routing / interfaces`
- `storage / filesystem / mount`
- `certificate / openssl / trust`
- `process / podman / host shell`

이 계층의 역할:

- host-level 조치가 필요한 질문에 답변 공백을 없앤다
- OpenShift 문서가 전제하는 운영 배경을 챗봇이 같이 이해하게 만든다

### Priority 4. Official Build / Validation Tooling

문서 본문은 아니지만 source-first 파이프라인을 검증하는 데 도움이 되는 자료다.

- `redhat-documentation/openshift-docs-build-tools`
- vendor build / lint / validation repo

이 계층의 역할:

- source 문서 구조 이해
- AsciiDoc include / build context / validation 규칙 참고
- parsing / shaping 보조 근거

### Priority 5. Verified Community Or Operational Repos

공식 문서를 보강하는 계층이다.

- operator maintainer repo
- 운영 예시 repo
- 실전 구성 예시
- policy overlay 후보

주의:

- 메인 본문으로 쓰지 않는다
- 공식 source를 대체하지 않는다
- authority badge와 review 상태를 반드시 분리한다

## 소스 전략

### 1. Source-First

가능하면 아래 순서를 따른다.

1. 공식 AsciiDoc / Markdown repo
2. official html-single
3. 공식 API / reference page
4. verified operational repo

### 2. html-single 는 버리지 않는다

html-single 는 fallback 이 아니라 coverage safety net 이다.

아래 상황에서 여전히 필요하다.

- 공식 repo 원문을 바로 찾기 어려운 경우
- include chain 이 너무 복잡한 경우
- 버전별 single-page reference 가 더 안정적인 경우
- repo source와 최종 문서 표면을 같이 검증해야 하는 경우

### 3. GitHub Surface 는 두 분기로 나눈다

- `Official Source Repos`
- `Official Build Tooling`

그 외 community / ops repo 는 별도 보강 분기로 둔다.

## Gold 승격 기준

### Data Gold

아래를 만족해야 한다.

- source provenance 추적 가능
- version / branch / source path 보존
- citation source trace 가능
- review 상태와 authority badge 분리

### Reader-Grade Gold Book

아래를 만족해야 한다.

- 제목이 사람이 읽기 좋다
- 번호 찌꺼기가 독해를 방해하지 않는다
- 절차 / 코드 / 검증 / 실패 신호가 분리된다
- 중요한 명령어와 옵션이 빠지지 않는다
- 운영자가 first reading path 를 바로 잡을 수 있다

즉, `approved source` 와 `reader-grade gold book` 은 같은 말이 아니다.

## 문서 타입별 우선 북 family

### Manual Book

- 기준 본문
- 긴 공식 문서를 읽는 용도
- 좌측 목차와 현재 섹션 하이라이트가 중요

### Operation Book

- 실제 절차를 빠르게 수행하는 용도
- prerequisite / procedure / verify / failure signal 중심

### Troubleshooting Book

- 장애 대응용
- symptom / likely cause / first checks / commands / recovery path 중심

### Environment Book

- Linux baseline 지식용
- systemd, journal, DNS, network, cert, storage를 운영 맥락에 맞춰 정리

## 첫 적재 순서

### Wave 1. 반드시 먼저 넣을 것

- `openshift/openshift-docs`
- backup and restore
- installing on any platform
- machine configuration
- monitoring

### Wave 2. 운영형으로 바로 가치가 큰 것

- certificate rotation / expiry
- update / upgrade troubleshooting
- ingress / route operations
- storage operations
- node / machine health

### Wave 3. 환경 지식 보강

- systemd
- journald
- DNS
- network
- certificate
- storage / filesystem

## 추천질문 활용 규칙

추천질문은 UX 부가 기능이 아니라 `다음 골드 코퍼스 후보 탐지기`로 본다.

반복해서 등장하는 추천질문은 아래로 분류한다.

- 운영 절차 부족
- 장애 대응 부족
- 검증 기준 부족
- Linux baseline 부족
- policy / authority 분리 부족

이 분류 결과를 다음 적재 backlog 로 사용한다.

## 현재 결론

우리가 쌓아야 할 골드 코퍼스는 단순한 OCP 버전 매뉴얼 묶음이 아니다.

우리가 쌓아야 할 것은 아래다.

- `공식 source 문서`
- `운영 절차 북`
- `트러블슈팅 북`
- `Linux baseline 북`

이 우선순위를 기준으로 중요한 자료부터 reader-grade gold 자산으로 승격한다.
