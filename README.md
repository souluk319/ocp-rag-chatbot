# OCP Operations Assistant v2

폐쇄망 환경에서 사용할 수 있는 OCP 운영도우미 RAG 챗봇입니다.

이 프로젝트는 OpenShift 공식 문서와 승인된 내부 문서를 수집해 검색 가능한 형태로 정규화하고, OpenDocuments 기반 RAG 흐름 위에 OCP 전용 정책과 멀티턴 문맥 관리, 출처 클릭 기능을 얹어 운영형 챗봇으로 제공하는 것을 목표로 합니다.

## 프로젝트 개요

이 챗봇은 단순 문서 검색기가 아니라, 다음 조건을 만족하는 운영 보조 시스템을 지향합니다.

- 한국어 질문에 답변할 수 있어야 함
- 답변은 근거 문서에 기반해야 함
- 답변에 표시된 출처를 누르면 실제 문서가 열려야 함
- 멀티턴 질문에서도 이전 맥락과 버전을 유지해야 함
- 폐쇄망 환경에서 문서 업데이트와 재인덱싱이 가능해야 함

## 핵심 기능

- OCP 공식 문서 원본인 `.adoc` 를 정규화해 검색용 텍스트와 HTML 출처 문서를 동시에 생성
- OpenDocuments 기반 인덱싱 및 질의 흐름
- 한국어 질의와 영어 원문 문서를 함께 다루기 위한 다국어 임베더 baseline
  `BAAI/bge-m3`
- OCP 전용 retrieval policy
  공식 문서 우선, 버전 연속성 유지, 보수적 답변 규칙
- 멀티턴 메모리와 follow-up rewrite
- 답변 하단 출처 표기와 HTML 클릭 연동
- 폐쇄망 반입을 위한 승인형 bundle, reindex, activation, rollback 흐름

## 시스템 구성

```text
openshift-docs / internal docs
  -> normalization pipeline
  -> normalized text + HTML citation views + metadata manifests
  -> OpenDocuments indexing / retrieval
  -> product runtime gateway
  -> Korean grounded answer + clickable citations
```

현재 제품 런타임은 다음 역할로 분리되어 있습니다.

- `openshift-docs`: 공식 문서 원천
- `OpenDocuments`: RAG 플랫폼 기준 구현
- `ocp-rag-chatbot`: 제품 전용 파이프라인, 정책, 게이트웨이, 평가, 폐쇄망 배포 흐름

## 데이터 소스 방식

현재 기본 공식 소스는 아래 저장소입니다.

- `https://github.com/openshift/openshift-docs`

이 저장소의 `.adoc` 문서는 공식 문서 작성 원본으로 취급합니다. 다만 챗봇은 저장소 전체를 그대로 읽지 않고, 소스 프로파일 기반으로 필요한 범위만 선택합니다.

현재 파이프라인은 다음 개념을 지원합니다.

- `source mirror`
  신뢰할 수 있는 원천 저장소와 로컬 mirror 위치
- `source profile`
  어떤 브랜치와 어떤 디렉터리 범위를 수집할지 정하는 규칙
- `active target release`
  아직 확정되지 않은 운영 대상 minor 버전이 정해졌을 때, `main` 에서 특정 `enterprise-4.x` 계열로 자연스럽게 전환할 수 있는 상태값

즉 지금은 validation 용으로 `main` 기반 프로파일을 사용할 수 있고, 나중에 운영 대상 minor가 정해지면 설정만 바꿔 `enterprise-4.17` 같은 버전 고정 프로파일로 전환할 수 있습니다.

## 답변과 출처 방식

이 프로젝트에서 출처는 보조 정보가 아니라 핵심 요구사항입니다.

- 검색용 텍스트와 별도로 HTML 문서 뷰를 생성함
- 각 section 은 anchor 와 metadata 를 가짐
- 답변에 붙는 citation 은 `viewer_url` 로 연결됨
- 사용자가 citation 을 누르면 raw `.adoc` 가 아니라 읽기 쉬운 HTML 문서가 열림

이 구조 덕분에 “왜 이런 답을 했는지”를 운영자가 바로 검증할 수 있습니다.

## 폐쇄망 운영 방식

문서 업데이트는 자동 즉시 반영이 아니라, 승인형 refresh loop를 기준으로 설계되어 있습니다.

1. 외부망에서 source mirror 갱신
2. 정규화 결과와 baseline diff 계산
3. outbound bundle 생성
4. 승인
5. 폐쇄망 inbound 반입
6. staging / reindex
7. smoke test
8. activate
9. 필요 시 rollback

이 흐름 덕분에 최신성보다 운영 안정성과 추적성을 우선할 수 있습니다.

## 저장소 구조

```text
app/           제품 전용 런타임 게이트웨이와 연동 코드
configs/       source profile, manifest, metadata, retrieval policy
data/          manifests, packages, staging, generated views
deployment/    폐쇄망 반입, bundle, activation, rollback 절차와 스크립트
docs/v2/       설계 문서, 단계별 계획, 검증 보고서
eval/          retrieval benchmark, red-team, multiturn 평가 자산
indexes/       활성/이전 index 포인터와 로컬 index 산출물
ingest/        문서 정규화 파이프라인
```

## 현재 구현 상태

현재 v2 브랜치에서는 아래가 구현되어 있습니다.

- validation slice 기준 공식 문서 정규화
- HTML citation view 생성
- retrieval benchmark / red-team / multiturn baseline
- Stage 11 refresh loop
  build -> approve -> validate -> stage -> reindex -> activate -> rollback
- Stage 12 live runtime baseline
  bridge -> OpenDocuments -> gateway -> viewer
- Stage 13 source profile / git lineage abstraction

즉 지금 상태는 “파이프라인의 큰 뼈대”가 돌아가는 단계이고, 이후에는 target minor 고정과 corpus 확대, UI polish 를 순차적으로 진행하면 됩니다.

## 관련 문서

설계와 진행계획은 별도 문서로 분리했습니다.

- 프로젝트 계획/현황: `docs/v2/project-plan-summary.md`
- 아키텍처 기준서: `docs/v2/architecture-blueprint.md`
- 단계별 로드맵: `docs/v2/execution-roadmap.md`
- 소스 범위 기준: `docs/v2/source-scope.md`
- 소스 프로파일 계층: `docs/v2/source-profile-layer.md`
- 평가 기준: `docs/v2/evaluation-spec.md`

## 브랜치 기준

- `main`: 안정 기준선
- `release/v1`: 이전 구현 보존
- `rewrite/opendoc-v2`: 현재 v2 개발 브랜치
