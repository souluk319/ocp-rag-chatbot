# Priority Wiki Targets

현재 navigation backlog 기준 다음 위키 확장 타깃 3개입니다.

## P1. etcd Hub Densification

- why_now: 추천질문과 관련 탐색에서 가장 강한 허브 재진입 신호가 etcd 축으로 모인다.
- expansion_goal: etcd 허브를 backup, restore, control plane recovery, monitoring signal 확인 경로까지 확장한다.
- deliverables:
  - etcd 허브 related books 확장
  - etcd 관련 troubleshooting book 연결
  - etcd 허브 backlink 보강
- primary_signal: `entity:etcd` · count=`40`

## P2. Machine Configuration Recovery Bridge

- why_now: 복원 이후 Machine Configuration을 같이 봐야 한다는 신호가 반복적으로 등장한다.
- expansion_goal: Backup and Restore와 Machine Configuration 사이의 운영 분기와 후속 확인 경로를 별도 bridge book 또는 relation으로 고정한다.
- deliverables:
  - 복원 후 MCO 확인 경로 정리
  - machine_configuration 허브/문서 backlink 강화
  - chat related links에 복구 후속 점검 경로 고정
- primary_signal: `query:복원-후-machine-configuration은-왜-같이-봐야-하는지-알려줘` · count=`45`
- supporting_signal: `book:machine-configuration` · count=`7`

## P3. Post-Action Verification Path

- why_now: 실행 이후 무엇을 먼저 검증해야 하는지에 대한 후속 질문이 반복되고 있다.
- expansion_goal: 복구/설치/프록시 변경 이후 Monitoring과 검증 문서를 묶는 후속 점검 위키 경로를 만든다.
- deliverables:
  - Monitoring verification path relation 추가
  - post-action verify 중심 북 후보 정의
  - 추천질문을 verification path로 재고정
- primary_signal: `query:백업-후-monitoring에서는-어떤-신호를-먼저-확인해야-해?` · count=`45`
- supporting_signal: `entity:cluster-wide-proxy` · count=`38`
