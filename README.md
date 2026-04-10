# Play Book Studio

OpenShift 지식을 `검색 가능한 한국어 코퍼스`와 `직접 읽을 수 있는 한국어 매뉴얼북`으로 동시에 제련한 뒤, 그 위에 챗봇과 운영형 인터페이스를 올리는 플레이북 제품입니다.

## 요약: 세 문장으로 이해하기

Play Book Studio의 본체는 챗봇이 아니라 `Gold-Corpus`와 `Gold-Manualbook`입니다.  
공식 문서, 운영 근거, 트러블슈팅 데이터를 모아 한국어 기준의 고품질 지식 자산으로 승격시키고, 그 결과물을 검색과 매뉴얼 읽기 경험에 동시에 사용합니다.  
즉 이 프로젝트는 `문서 검색 챗봇`이 아니라, `OpenShift 지식 제련소 + 플레이북 실행 인터페이스`입니다.

## 1. Play Book Studio란 무엇인가

일반적인 챗봇은 질문이 들어오면 그때그때 답을 생성합니다.  
Play Book Studio는 그보다 앞단에서 먼저 지식을 정리합니다.

이 프로젝트가 만드는 것은 두 가지입니다.

1. `고품질 한국어 RAG 코퍼스`
2. `유저가 직접 읽고 클릭할 수 있는 한국어 매뉴얼북`

챗봇은 이 두 자산을 사용하는 표면입니다.  
그래서 목표는 답변을 예쁘게 꾸미는 것이 아니라, `근거가 있는 답변`, `클릭 가능한 매뉴얼북`, `버전이 고정된 운영 지식`을 만드는 데 있습니다.

## 2. 전체 구조를 한눈에 보기

Play Book Studio의 흐름은 크게 다섯 단계입니다.

```text
      +----------------------+
      |   Raw Source Input   |
      | official docs/issues |
      | repo/troubleshooting |
      +----------+-----------+
                 |
                 v
      +----------------------+
      |   Foundry Pipeline   |
      | Bronze -> Silver     |
      | -> Silver-KO         |
      | -> Gold-*            |
      +----------+-----------+
                 |
        +--------+--------+
        |                 |
        v                 v
 +---------------+  +------------------+
 | Gold-Corpus   |  | Gold-Manualbook  |
 | chunks/bm25   |  | books/anchors    |
 +-------+-------+  +---------+--------+
         |                    |
         +---------+----------+
                   |
                   v
         +--------------------+
         | Play Book Surfaces |
         | chat / viewer /    |
         | runtime / eval     |
         +--------------------+
```

핵심은 `데이터를 먼저 제련하고`, 그 다음에 `검색과 답변`이 올라간다는 점입니다.

## 3. 새로운 전략: 챗봇 우선이 아니라 골드데이터셋 우선

이 프로젝트는 더 이상 `챗봇부터 만드는 데모`가 아닙니다.

우선순위는 아래 순서로 고정합니다.

1. `Gold-Corpus`를 만든다.
2. `Gold-Manualbook`을 만든다.
3. 그 위에 챗봇, 뷰어, 운영형 UI를 올린다.

이 전략을 택한 이유는 단순합니다.

- 코퍼스가 약하면 검색이 흔들립니다.
- 매뉴얼북이 약하면 사용자가 근거를 직접 검증할 수 없습니다.
- 이 두 가지가 흔들리면 챗봇 품질도 결국 흔들립니다.

따라서 Play Book Studio의 경쟁력은 `모델 이름`보다 `골드데이터셋의 품질`에서 나옵니다.

## 4. 데이터 제련소

데이터 파이프라인은 아래 단계로 정리합니다.

```text
Bronze -> Silver -> Silver-KO -> Gold-Corpus -> Gold-Manualbook
```

### 4.1 Bronze

원문을 가능한 한 훼손하지 않고 모읍니다.

- Red Hat 공식 문서 HTML
- 공식 문서 원문 저장소
- 이슈, PR, 토론, 운영 근거
- 트러블슈팅 자료

### 4.2 Silver

문서를 문서 그래프로 정규화합니다.

- 문서 제목
- 버전
- 섹션 경로
- 앵커
- 출처 URL
- 명령어
- 에러 문자열
- Kubernetes / OpenShift 객체
- 운영 검증 힌트

이 단계부터 단순 텍스트 묶음이 아니라 `검색 가능한 구조화 지식`이 됩니다.

### 4.3 Silver-KO

한국어 승격 단계입니다.

- 공식 한국어가 있으면 우선 채택
- 한국어가 비어 있으면 EN fallback 기반 draft 생성
- review 전에는 gold로 올리지 않음

즉 `번역됨`과 `승인됨`은 같은 말이 아닙니다.

### 4.4 Gold-Corpus

검색용 산출물입니다.

- chunks
- BM25 corpus
- retrieval metadata
- citation용 provenance

목표는 `정확하게 찾는 것`입니다.

### 4.5 Gold-Manualbook

읽기용 산출물입니다.

- 장/절/소절 구조 유지
- anchor 유지
- viewer 연결
- citation 클릭 시 정확한 섹션으로 이동

목표는 `직접 읽고 검증할 수 있게 만드는 것`입니다.

## 5. 현재 범위

현재 기준 제품 범위는 `OpenShift 4.20` 입니다.

핵심 산출물 상태:

- active gold 문서: `23권`
- 번역 승격 대기: `4권`

현재 active gold 문서:

- `advanced_networking`
- `architecture`
- `authentication_and_authorization`
- `cli_tools`
- `disconnected_environments`
- `images`
- `ingress_and_load_balancing`
- `installation_overview`
- `logging`
- `machine_management`
- `networking_overview`
- `nodes`
- `observability_overview`
- `overview`
- `postinstallation_configuration`
- `registry`
- `release_notes`
- `security_and_compliance`
- `storage`
- `support`
- `updating_clusters`
- `validation_and_troubleshooting`
- `web_console`

현재 번역 승격 대기 문서:

- `backup_and_restore`
- `installing_on_any_platform`
- `machine_configuration`
- `monitoring`

이 네 권은 `translated_ko_draft / needs_review` 상태이며, 아직 active gold에는 포함되지 않았습니다.

## 6. 사용자에게 보이는 표면

사용자는 주로 아래 세 표면을 보게 됩니다.

### 6.1 Chat UI

질문을 입력하면 검색, 리랭킹, 근거 선택을 거쳐 답을 만듭니다.  
답변은 가능하면 문서 근거와 citation을 함께 제공합니다.

### 6.2 Manualbook Viewer

citation을 누르면 해당 문서의 정확한 섹션으로 이동합니다.  
이 덕분에 사용자는 챗봇 답을 그대로 믿는 대신, 원문과 구조화된 매뉴얼북을 직접 확인할 수 있습니다.

### 6.3 Runtime / Eval

현재 런타임 상태와 평가 결과를 점검합니다.  
즉 제품을 “보여주는 화면”만이 아니라, “재현성과 품질을 검증하는 표면”도 함께 가집니다.

## 7. 실행

기준 진입점은 `play_book.cmd` 하나입니다.

```powershell
play_book.cmd ui
play_book.cmd ask --query "etcd 백업은 어떻게 하나?"
play_book.cmd eval
play_book.cmd runtime
```

발표나 시연에서 가장 많이 쓰는 실행은 아래 하나입니다.

```powershell
play_book.cmd ui --host 127.0.0.1 --port 8765 --no-browser
```

런타임 점검:

```powershell
play_book.cmd runtime
```

## 8. 저장소 구조

```text
.
├─ data/
│  ├─ bronze/
│  ├─ silver/
│  ├─ silver_ko/
│  ├─ gold_corpus_ko/
│  └─ gold_manualbook_ko/
├─ manifests/
├─ reports/
├─ schemas/
├─ scripts/
├─ src/
│  └─ play_book_studio/
├─ tests/
├─ PROJECT.md
├─ SYSTEM_RULES.md
├─ TASK_BOARD.yaml
└─ play_book.cmd
```

의미는 간단합니다.

- `data/`는 제련 결과물
- `manifests/`는 문서 범위와 승인 상태
- `schemas/`는 데이터 계약
- `src/`는 실제 제품 코드
- `tests/`는 회귀 검증

## 9. 같이 보는 문서

루트 기준으로 아래 문서를 함께 봅니다.

- `PROJECT.md`
- `SYSTEM_RULES.md`
- `TASK_BOARD.yaml`
- `PRODUCT_BRIEF.md`
- `PRODUCT_ROADMAP.md`
- `QUICKSTART.md`
- `FILE_ROLE_GUIDE.md`

## 한 문장 요약

Play Book Studio는 OpenShift 공식 지식과 운영 근거를 `골드 코퍼스`와 `골드 매뉴얼북`으로 동시에 제련하고, 그 위에 검색·답변·읽기 경험을 올리는 지식 제품입니다.
