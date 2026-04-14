# Reader-Grade Book Reference

## Purpose

이 문서는 `reader-grade book`의 기준 형태를 고정한다.

여기서 말하는 `book`은 단순히 원문을 markdown 으로 변환해 viewer 에 띄운 산출물이 아니다.
사용자가 실제로 읽고, 형광펜을 긋고, 밑줄을 긋고, 다시 찾아볼 수 있을 만큼 구조와 밀도가 정리된 문서를 뜻한다.

현재 첫 shadow sample 은 아래 두 권으로 고정한다.

- `backup_and_restore`
- `installing_on_any_platform`

## Reference Direction

구조 기준은 아래 조합을 따른다.

- `Material for MkDocs`
  - heading hierarchy
  - admonition / note / warning block
  - code block readability
  - table readability
- `Runbook structure`
  - prerequisites
  - procedure
  - verify
  - failure signals
  - source trace

즉, `예쁜 문서`가 아니라 `빠르게 읽히는 실행형 문서`를 목표로 한다.

## Reader-Grade Definition

아래를 모두 만족해야 `reader-grade book`으로 본다.

1. 제목만 읽어도 목적이 바로 이해된다.
2. 긴 장문이 목적별 섹션으로 분해돼 있다.
3. 코드, 표, 주의, 검증이 서로 섞이지 않는다.
4. `1.5.3` 같은 원문 구조 찌꺼기가 독해를 방해하지 않는다.
5. 설명 밀도가 과하지 않고, 실행과 직접 관련 없는 TMI 가 억제돼 있다.
6. 사용자 annotation 이 자연스럽게 붙을 만한 단위로 section 이 나뉘어 있다.

## Global Book Rules

### 1. Title Cleanup

- heading 앞의 기계적 번호는 기본적으로 제거한다.
- 번호가 의미를 가질 때만 보조 메타로 남기고 제목 본문에는 넣지 않는다.
- 제목은 `사람이 한 번에 읽는 길이`로 다시 쓴다.

예시:

- `1.5.3 Backing up etcd data`
  -> `Back Up etcd Data`
- `3.2.4 Installing on any platform`
  -> `Install on Any Platform`

### 2. Section Shaping

모든 section 은 아래 역할 중 하나로 귀속돼야 한다.

- `Overview`
- `When To Use`
- `Prerequisites`
- `Procedure`
- `Commands / YAML`
- `Verify`
- `Failure Signals`
- `Related Decisions`
- `Source Trace`

역할이 불명확한 문단은 그대로 두지 않는다.

### 3. Density Control

- 한 section 에 너무 많은 목적을 담지 않는다.
- 배경 설명은 `Overview` 로 밀어 넣고, 실행 절차는 `Procedure` 에 집중시킨다.
- 반복 설명은 제거한다.
- 실행과 검증이 이어지는 문서는 `설명 -> 명령 -> 검증` 리듬을 유지한다.

### 4. Code And Table Rules

- 코드 블록은 항상 문맥 제목을 가진다.
- YAML, shell, JSON 은 언어 태그와 함께 분리한다.
- 표는 가능한 경우 의미 단위 표로 유지하되, 너무 넓으면 요약 설명 + 원문 링크로 전환한다.
- 코드 블록 뒤에는 바로 `왜 이 명령을 쓰는지` 또는 `무엇을 확인해야 하는지`가 따라와야 한다.

### 5. Admonition Rules

아래 블록은 본문과 분리한다.

- `Important`
- `Warning`
- `Unsupported / Do Not`
- `Verification Tip`

경고 문장이 본문 중간에 묻히지 않게 한다.

## Sample A: Backup And Restore

### Book Role

- `operations_runbook`

### Reader Goal

- 운영자가 etcd 백업/복구를 빠르게 이해하고 실행한다.
- 단순 설명보다 `사전조건 -> 절차 -> 검증 -> 실패 신호`가 먼저 보여야 한다.

### Target Table Of Contents

1. `Backup and Restore Overview`
2. `When to Back Up the Cluster`
3. `Before You Begin`
4. `Back Up etcd Data`
5. `Verify the Backup Files`
6. `Restore etcd from a Backup`
7. `Verify Cluster Recovery`
8. `Common Failure Signals`
9. `Related Operations`
10. `Source Trace`

### Required Block Shape

- `Before You Begin`
  - cluster state assumptions
  - required node access
  - required file paths
- `Back Up etcd Data`
  - one step per action
  - shell block directly below step
  - short explanation only
- `Verify the Backup Files`
  - expected output
  - what success looks like
- `Common Failure Signals`
  - symptom
  - likely cause
  - next check

### Forbidden Shape

- backup and restore 개념 설명과 실제 명령을 같은 장문 안에 섞기
- 명령어 없이 개념 설명만 길게 이어가기
- warning 을 본문 중간 문장으로 흘려보내기
- 문단 하나에 여러 절차를 몰아넣기

## Sample B: Installing On Any Platform

### Book Role

- `installation_manual`

### Reader Goal

- 설치 담당자가 플랫폼 독립 설치의 전체 흐름과 분기점을 빠르게 파악한다.
- 긴 설치 문서를 처음부터 끝까지 읽게 만들지 않고, 단계별로 접근하게 한다.

### Target Table Of Contents

1. `Install on Any Platform Overview`
2. `Choose This Installation Path`
3. `Architecture and Prerequisites`
4. `Prepare the Install Configuration`
5. `Generate Cluster Assets`
6. `Create the Cluster`
7. `Complete Post-Install Tasks`
8. `Verify Installation Health`
9. `Common Installation Failures`
10. `Source Trace`

### Required Block Shape

- `Choose This Installation Path`
  - 언제 이 문서를 써야 하는지
  - 다른 설치 문서와 어떻게 다른지
- `Architecture and Prerequisites`
  - infra assumptions
  - required credentials
  - required network/DNS/base domain
- `Prepare the Install Configuration`
  - 입력값 목록
  - config 예시
  - common mistakes
- `Verify Installation Health`
  - cluster operators
  - node readiness
  - console / API checks

### Forbidden Shape

- 설치 전제조건이 문서 여러 곳에 흩어져 있는 형태
- 긴 reference 설명이 절차보다 먼저 문서를 점령하는 형태
- `1.2.3` 류의 번호가 heading 독해를 방해하는 형태
- verify 없이 create step 만 보여주는 형태

## Viewer Expectations

reader-grade book 이 viewer 에서는 아래처럼 보여야 한다.

- heading hierarchy 가 눈에 바로 들어온다.
- `Overview / Procedure / Verify / Warning` 블록이 시각적으로 구분된다.
- 코드 블록은 복사 가능한 독립 영역으로 보인다.
- section 하나가 너무 길면 anchor 기준으로 더 잘게 쪼개진다.
- 하이라이트/밑줄/메모를 붙여도 어색하지 않다.

## Pass / Fail

### Pass

- 목차만 읽어도 문서 목적이 보인다.
- 실행자가 어디부터 읽어야 하는지 알 수 있다.
- 긴 원문이 `읽기 -> 실행 -> 검증` 흐름으로 바뀐다.
- viewer 에서 block 유형이 구분된다.

### Fail

- 원문 section 번호가 그대로 독해를 지배한다.
- 본문이 장문 위주라 annotation 을 얹고 싶지 않다.
- 절차와 검증이 분리되지 않는다.
- source trace 는 남았지만 reader 경험은 raw manual 에 가깝다.
