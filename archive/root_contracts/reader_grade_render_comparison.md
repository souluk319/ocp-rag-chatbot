# Reader-Grade Render Comparison

## Purpose

이 문서는 같은 원문 기준으로 `현재 자동 viewer 출력`과 `reader-grade reference book`을 비교한다.

비교 대상은 JSON AST 가 아니다.
실제 사용자가 읽게 되는 viewer 결과와 reference book 문서를 나란히 본다.

---

## 1. Backup and Restore

### Automatic Viewer Output

- source: `data/gold_manualbook_ko/playbooks/backup_and_restore.json`
- viewer path: `/docs/ocp/4.20/ko/backup_and_restore/index.html?embed=1`
- rendered sections: `450`
- numbered headings in source sections: `449`

자동 viewer 는 문서처럼 렌더되지만, 첫 독해 경로가 너무 넓다.
앞부분만 봐도 아래 제목이 그대로 이어진다.

- `Backing up and restoring your OpenShift Container Platform cluster`
- `Control plane backup and restore operations`
- `Application backup and restore operations`
- `OADP requirements`
- `Backing up and restoring applications`
- `Shutting down the cluster gracefully`
- `Restarting the cluster gracefully`
- `Hibernating an OpenShift Container Platform cluster`

핵심 운영 절차인 `Backing up etcd data`, `Restoring a cluster manually from an etcd backup`, `verify` 계열 내용은 자동 viewer 안에 존재한다.
문제는 이 절차들이 manual 전체 흐름 안에 깊게 묻혀 있다는 점이다.

### Reader-Grade Reference

- source: `archive/root_contracts/backup_and_restore_reader_grade_shadow.md`

reference 는 다음 순서로 재구성한다.

- `Overview`
- `When To Use`
- `Before You Begin`
- `Back Up etcd Data`
- `Verify the Backup Artifacts`
- `Restore etcd from a Backup`
- `Verify Cluster Recovery`
- `Common Failure Signals`
- `Source Trace`

### Render Gap

자동 viewer 와 reference 의 차이는 세 가지다.

1. `entry path`
   - 자동본은 broad manual entry 이고, reference 는 운영자용 slim entry 다.
2. `section density`
   - 자동본은 450 section 을 그대로 보여주고, reference 는 핵심 경로만 남긴다.
3. `reader intent`
   - 자동본은 설명/범주/부가 문서가 앞에 오고, reference 는 `backup -> restore -> verify`를 먼저 드러낸다.

### Current Verdict

`backup_and_restore`는 자동화 라인이 정보를 잃은 상태는 아니다.
하지만 지금 출력은 `reader-grade book` 이 아니라 `읽을 수 있는 raw manual viewer` 에 가깝다.

---

## 2. Installing on Any Platform

### Automatic Viewer Output

- source: `data/gold_manualbook_ko/playbooks/installing_on_any_platform.json`
- viewer path: `/docs/ocp/4.20/ko/installing_on_any_platform/index.html?embed=1`
- rendered sections: `54`

자동 viewer 첫 heading 은 아래처럼 이어진다.

- `Installing OpenShift Container Platform on any platform`
- `Installing a cluster on any platform`
- `Prerequisites`
- `Internet access for OpenShift Container Platform`
- `Requirements for a cluster with user-provisioned infrastructure`
- `Required machines for cluster installation`
- `Minimum resource requirements for cluster installation`
- `Certificate signing requests management`
- `Networking requirements for user-provisioned infrastructure`

설치 핵심 명령인 `./openshift-install create manifests`, `./openshift-install create ignition-configs` 는 자동 viewer 안에 존재한다.
그러나 prerequisite 와 세부 조건이 길게 앞을 차지해 설치 경로가 immediately visible 하지는 않다.

### Reader-Grade Reference

- source: `archive/root_contracts/installing_on_any_platform_reader_grade_shadow.md`

reference 는 다음 순서로 재구성한다.

- `Overview`
- `When To Use`
- `Choose This Installation Path`
- `Before You Begin`
- `Prepare the Installation Configuration`
- `Generate Cluster Assets`
- `Start RHCOS Installation and Bootstrap`
- `Verify Installation Readiness`
- `Verify Installation Health`
- `Common Installation Failures`
- `Source Trace`

### Render Gap

자동 viewer 와 reference 의 차이는 세 가지다.

1. `installation path visibility`
   - 자동본은 prerequisite 와 환경 조건을 먼저 길게 보여주고, reference 는 실제 설치 순서를 먼저 세운다.
2. `decision support`
   - reference 는 `언제 이 문서를 쓰는지` 와 `왜 이 경로를 택하는지`를 먼저 말한다.
3. `operational readability`
   - 자동본은 full manual, reference 는 install runbook 에 가깝다.

### Current Verdict

`installing_on_any_platform`도 자동화 라인이 정보를 잃지는 않았다.
하지만 현재 표면은 `설치용 reference manual` 이고, reference book 은 `설치용 guided manual` 에 더 가깝다.

---

## Fixed Conclusion

현재 자동화 파이프라인은 문서를 `볼 수 있게` 만들 수 있다.
하지만 아직 문서를 `읽기 좋은 북`으로 만들지는 못한다.

다음 단계는 새 정보를 추가하는 것이 아니다.
이미 있는 정보를 아래 기준으로 다시 shape 하는 것이다.

- first reading path 가 바로 보여야 한다
- broad manual 범주보다 실행 경로가 먼저 보여야 한다
- tone 은 내부 메모가 아니라 기술 가이드 / runbook 톤이어야 한다
- manual book 과 derived playbook 은 서로 다른 viewer 목표를 가져야 한다
