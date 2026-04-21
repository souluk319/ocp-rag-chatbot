---
status: reference
doc_type: strategy
audience:
  - codex
  - engineer
  - operator
last_updated: 2026-04-21
---

# Goal-First Upgrade Operation v1

이 문서는 PBS 업그레이드의 기준점을 `현재 코드`가 아니라 `고정된 제품 목표`에 다시 맞추기 위해 작성한다.

핵심 선언은 하나다.

`PBS의 다음 단계는 RAG 챗봇 고도화가 아니라, 문서를 reader-grade wiki/playbook과 chat-grade knowledge base로 승급시키는 지식 제조 시스템의 정립이다.`

## 1. 왜 이 문서가 필요한가

지금까지 저장소에는 이미 많은 자산이 쌓여 있다.

- viewer shell
- playbook runtime
- corpus/retrieval
- user upload lane
- control tower style surface
- knowledge object 초안
- promotion gate 초안

문제는 자산의 양이 아니다.

문제는 아래 판단 축이 아직 완전히 잠기지 않았다는 점이다.

- 무엇이 `고정 목표` 인가
- 무엇이 `교체 가능한 구현물` 인가
- 무엇이 `껍데기` 이고 무엇이 `내실` 인가
- 무엇을 유지하고 무엇을 과감히 다시 세워야 하는가

따라서 이번 업그레이드는 `기존 코어를 어떻게 보존할까`로 시작하지 않는다.

이번 업그레이드는 아래 질문으로 시작한다.

`새 딥리서치 전략이 PBS의 고정 목표와 얼마나 정확히 맞닿아 있으며, 그 목표에 더 빨리 도달하기 위해 현재 시스템의 어느 부분을 유지/대체/신설해야 하는가`

## 2. 고정 불변 목표

이 문서에서 불변인 것은 코드가 아니라 아래 목표다.

1. 어떤 원천 문서가 들어와도 사람이 읽을 수 있는 `reader-grade technical wiki/playbook` 으로 승급시킨다.
2. 같은 기준선에서 LLM이 신뢰할 수 있는 `chat-grade corpus` 를 만든다.
3. viewer와 chat은 반드시 `shared truth` 를 사용한다.
4. 출처, anchor, figure, table, procedure fidelity를 잃지 않는다.
5. 품질이 부족한 산출물은 무리하게 승격하지 않고 `repair + grade + promote` 루프를 거친다.

즉 PBS의 본질은 아래다.

`문서를 넣으면 답하는 챗봇`

이 아니라,

`문서를 읽고, 해석하고, 수리하고, 등급화하고, 출판하고, 검색 가능한 지식으로 제조하는 시스템`

이다.

## 3. 이번 판단

이번 업그레이드에서 가장 중요한 판단은 아래다.

### 3.1 유지해야 하는 것

- PBS의 최종 제품 목표
- source-first / shared-truth 원칙
- playbook library / wiki runtime viewer / chat workspace 표면 체계
- citation landing, figure awareness, boundary discipline
- viewer shell, landing page, book factory surface 같은 외형 자산

### 3.2 교체 가능하다고 보는 것

- 현재 parser 구성
- 현재 canonical AST의 범위와 세부 필드
- 현재 one-shot normalize 흐름
- 현재 quality score의 계산 방식
- 현재 user upload lane의 승격 기준
- 현재 corpus 생성과 citation trace 방식의 결합도

### 3.3 새 기준점

앞으로 구현 우선순위는 `기존 구조를 최대한 재사용`이 아니라 아래 순서로 정한다.

1. 제품 목표에 직접 닿는가
2. 품질 게이트를 자동화할 수 있는가
3. 사람이 읽는 결과와 챗봇 결과가 같은 truth에서 파생되는가
4. low-quality source를 repair/promotion loop 안에서 다룰 수 있는가
5. 그 다음에야 현재 코드 재사용 여부를 판단한다

즉 기존 코드는 `보존 대상` 이 아니라 `평가 대상` 이다.

## 4. 딥리서치 전략과 PBS 목표의 접점

새 딥리서치 전략은 PBS의 목표와 아래 지점에서 강하게 맞닿아 있다.

| 딥리서치 관점 | PBS 고정 목표와의 접점 | 이번 업그레이드 판단 |
| --- | --- | --- |
| RAG 챗봇보다 문서 승급 시스템이 핵심 | Playbook의 자격 조건이 source fidelity + chat interaction quality 이기 때문 | 채택 |
| 파서 하나가 아니라 parser router + fallback + repair loop 가 필요 | source-first official lane과 user upload lane 모두 형식별 실패 양상이 다르기 때문 | 채택 |
| 중간에 Wiki AST가 있어야 한다 | markdown 단독 truth 금지, structured runtime core 유지 계약과 정합 | 채택 |
| Bronze/Silver/Gold가 예쁜 이름이 아니라 품질 게이트여야 한다 | blocked artifact, corpus quality gate, playbook publish rule과 정합 | 채택 |
| PPT는 복원 대상이 아니라 해석 대상이다 | partner/private lane의 현실 검증대가 PPT/slide 계열이기 때문 | 채택 |
| quality dashboard가 제품 기능이어야 한다 | enterprise 신뢰 형성에 필요하고 control tower와 자연스럽게 연결됨 | 채택 |
| annotation과 citation이 block 단위로 묶여야 한다 | viewer jump, chat landing, overlay discipline과 직결 | 채택 |
| 기존 코드 우선이 아니라 목표 우선으로 기준점을 재설정해야 한다 | 현재 renewal의 핵심이 refinement/hardening/validation이며 목표 미달 구조는 교체되어야 하기 때문 | 채택 |

채택하지 않는 것은 하나뿐이다.

- `제품 목표 자체를 새로 정의하는 것`

이번 업그레이드는 목표 재정의가 아니라 `목표 도달 경로의 재설계` 다.

## 5. 새 아키텍처 기준선

앞으로 PBS 코어는 아래 제조 흐름으로 본다.

`Source Intake -> Document Inspector -> Parser Router -> Canonical Wiki AST / Knowledge Layer -> Quality Gate -> Repair Planner -> Publish -> Viewer/Corpus/Annotation/Dashboard`

### 5.1 Source Intake

역할:

- official repo / html / pdf / customer / upload source 수집
- hash, lane, tenant, workspace, provenance 고정

### 5.2 Document Inspector

역할:

- 파일 형식 판별
- OCR 필요성
- table / image / slide / layout complexity
- 예상 cost level
- parser route candidate 선정

### 5.3 Parser Router

역할:

- 문서 난이도에 따라 route 선택
- 성공/실패 기록
- parser backend 비교 가능화

### 5.4 Canonical Wiki AST / Knowledge Layer

역할:

- source별 파싱 결과를 공통 truth 구조로 정규화
- viewer, corpus, repair, dashboard가 같은 truth를 참조하게 만듦

중요:

- 현재 `canonical AST v1`은 폐기 대상이 아니라 seed다
- 현재 `knowledge object schema v1`은 대체재가 아니라 상위 semantic layer 후보다
- 최종 구조는 `page/section/block 기반 Wiki AST` 와 `knowledge object graph` 가 결합된 2층 구조로 보는 것이 적절하다

### 5.5 Quality Gate

역할:

- parse-grade
- reader-grade
- chat-grade
- governance-grade
- promotion fail gate

### 5.6 Repair Planner

역할:

- 실패 원인 taxonomy 기록
- 재시도 전략 선택
- 기대 개선폭 / 비용 / 재처리 횟수 관리

### 5.7 Publish

역할:

- grade 확정
- playbook render
- corpus build
- citation map
- annotation-ready target surface 생성

### 5.8 Product Surfaces

역할:

- Playbook Library
- Wiki Runtime Viewer
- Chat Workspace
- Knowledge Grade Dashboard

## 6. 기존 자산 재배치

현재 저장소 자산은 버릴 것과 다시 쓸 것을 아래처럼 재배치한다.

### 6.1 그대로 유지할 자산

- `presentation-ui`의 shell, landing, playbook viewer 계열 외형
- `PRODUCT_GATE_SCORECARD.yaml` 의 release/product gate 골격
- `TASK_BOARD.yaml` 의 harness discipline
- `RUNTIME_ARCHITECTURE_CONTRACT.md` 의 shared truth / source-first / runtime core 원칙

### 6.2 승격해서 코어로 삼을 자산

- `docs/playbook_wiki/knowledge_object_schema_v1.md`
- `docs/playbook_wiki/user_upload_repair_promotion_plan_v1.md`
- `docs/playbook_wiki/pbs_playbook_wiki_plan.md`
- `src/play_book_studio/canonical/models.py`
- `src/play_book_studio/intake/models.py`

이 자산들은 완성본이 아니라, 새 제조 시스템의 씨앗이다.

### 6.3 대체가 필요한 자산

- 현재 canonical model의 block 범위 부족
- format별 inspector/route 부재 또는 약함
- quality score와 fail gate 분리 부족
- repair planner 부재
- parser benchmark / route decision evidence 부재
- PPT 전용 dual path 부재
- dashboard에서 grade/issue/retry/cost가 1급 시민이 아닌 점

## 7. 코어 설계 결론

### 7.1 Wiki AST는 반드시 v2로 확장한다

기존 canonical AST v1은 section/block 중심 구조로 출발점 역할은 한다.
하지만 새 기준선에서는 아래가 더 필요하다.

- page_id / slide_id
- bbox / layout / z-order / reading order
- figure-caption relation
- source block trace
- parser confidence / OCR confidence
- validation issue attachment
- chunk group / citation anchor metadata

즉 `문단만 가진 AST` 에서 `문서 해석과 승급을 위한 AST` 로 올라가야 한다.

### 7.2 knowledge object layer는 AST 위에 놓는다

지금 시점에서 object graph만으로 바로 가면 문서 fidelity가 먼저 무너질 수 있다.

따라서 순서는 아래가 맞다.

1. `Wiki AST v2` 로 문서 충실도를 확보
2. 그 위에서 entity/concept/procedure/claim 객체를 누적

즉 object graph는 목표지만, 구현 착수점은 AST다.

### 7.3 Bronze/Silver/Gold는 gate engine으로 고정한다

등급은 라벨이 아니라 verdict여야 한다.

최소 verdict는 아래 네 가지로 나눈다.

- `blocked_artifact`
- `bronze`
- `silver`
- `gold`

그리고 별도 축으로 아래를 유지한다.

- `parse_grade`
- `reader_grade`
- `chat_grade`
- `governance_grade`

### 7.4 PPT는 별도 lane으로 처리한다

PPTX는 일반 문서 normalize의 하위 케이스가 아니다.

PPT lane 최소 구성:

- OOXML 구조 추출
- slide render image 추출
- OCR/vision 보조
- slide intent / narrative reconstruction
- original thumbnail 연결

즉 `pptx -> markdown` 이 아니라 `pptx -> interpreted wiki page candidate` 가 기준이다.

## 8. 새 우선순위

이번 작전의 우선순위는 아래로 잠근다.

1. `Goal-first quality model`
2. `Wiki AST v2`
3. `Quality Gate Engine`
4. `Parser Router + Document Inspector`
5. `PPT dual path`
6. `Repair Planner`
7. `Knowledge Grade Dashboard`
8. `Renderer/Corpus/Annotation rebinding`

이 순서를 뒤집으면 다시 껍데기 강화가 된다.

## 9. Phase Plan

## Phase 0. Goal Lock and Scoring Reset

목표:

- 현재 구현 우선주의를 중단하고 목표 우선 평가 체계를 잠근다

산출물:

- goal-first strategy
- grade rubric
- fail gate taxonomy
- representative fixture set

acceptance criteria:

- pass: 같은 문서를 보고 왜 blocked / bronze / silver / gold 인지 설명할 수 있다
- fail: 여전히 좋아 보이는 UI나 기존 구조를 이유로 품질 판정을 덮는다

## Phase 1. Wiki AST v2

목표:

- 모든 문서형식을 공통 truth 구조로 정규화한다

산출물:

- wiki_ast_v2 schema
- parser adapter contract
- block/source/layout/citation 모델

acceptance criteria:

- pass: html, pdf, pptx가 동일 truth family로 들어온다
- pass: viewer와 corpus가 AST만 보고 파생 가능하다
- fail: markdown이나 temporary html가 사실상 canonical truth 역할을 한다

## Phase 2. Quality Gate Engine

목표:

- 등급을 시스템 verdict로 바꾼다

산출물:

- parse/reader/chat/governance metric set
- blocked fail gate
- score report schema

acceptance criteria:

- pass: 각 문서가 왜 승격/보류/차단됐는지 issue list가 남는다
- fail: 점수는 있지만 fail reason taxonomy가 없다

## Phase 3. Parser Router + PPT Dual Path

목표:

- 문서 타입별 라우팅과 PPT 해석 전략을 고정한다

산출물:

- document inspector
- parser router
- route benchmark report
- ppt dual path prototype

acceptance criteria:

- pass: parser 선택 근거와 fallback 이유가 기록된다
- pass: ppt slide별 품질 이슈와 narrative candidate가 나온다
- fail: ppt가 일반 md 변환 경로에 눌린다

## Phase 4. Repair Planner

목표:

- 실패한 산출물을 다시 승급시키는 자동 수리 루프를 만든다

산출물:

- issue taxonomy
- repair strategy catalog
- rerun history
- plateau detection

acceptance criteria:

- pass: repair 전/후 점수와 issue 차이를 설명할 수 있다
- fail: 다시 돌렸다 수준에서 멈추고 개선 증거가 없다

## Phase 5. Publish and Bind

목표:

- viewer, corpus, annotation, dashboard를 새 truth에 다시 묶는다

산출물:

- renderer binding
- chunk binding
- citation map binding
- annotation target model
- grade dashboard

acceptance criteria:

- pass: viewer와 chat이 같은 block/source anchor로 수렴한다
- pass: dashboard가 등급, 이슈, 비용, retry history를 보여준다
- fail: 표면은 좋아졌는데 source trace가 약해진다

## 10. 첫 실행 packet 순서

아래 packet 순서를 권장한다.

1. `goal_first_grade_rubric_packet`
2. `wiki_ast_v2_packet`
3. `quality_gate_engine_packet`
4. `parser_router_packet`
5. `ppt_dual_path_packet`
6. `repair_planner_packet`
7. `grade_dashboard_packet`
8. `renderer_corpus_rebind_packet`

## 11. Keep / Replace / Build Matrix

### Keep

- current product goal
- current product surfaces
- source-first / shared truth / pack boundary doctrine
- viewer shell and landing assets

### Replace

- implementation-first decision rule
- weak canonical model coverage
- parser-as-single-path assumption
- score-only quality judgment

### Build

- document inspector
- parser router
- wiki ast v2
- quality gate engine
- repair planner
- ppt dual path
- knowledge grade dashboard

## 12. 하지 않을 것

- 기존 코드라는 이유만으로 우선권을 주지 않는다
- viewer shell 개선을 코어 재정립보다 먼저 하지 않는다
- low-quality source를 corpus에 서둘러 흘려보내지 않는다
- markdown/html export를 canonical truth로 승격하지 않는다
- ppt를 원본 시각 레이아웃 복제 문제로만 취급하지 않는다
- gold 승격을 full-auto magic처럼 과장하지 않는다

## 13. 구현 packet 운영 규칙

이 계획은 구현 단계에서 `major task` 로 다뤄야 한다.

필수 companion lane:

- `main`
- `explorer`
- `worker` 또는 `reviewer`

현재 세션에서는 사용자 명시 없이 병렬 agent를 바로 띄울 수 없으므로,
이번 문서는 구현 packet의 병렬 필요성을 먼저 잠그는 용도로 사용한다.

## 14. 최종 결론

PBS는 지금 `챗봇이 있는 문서 시스템`에서 멈추면 안 된다.

이번 업그레이드의 목표는 아래로 잠근다.

`껍데기로서의 위키/북팩토리 표면은 유지하되, 내부 코어를 문서 해석 -> 품질 판정 -> 자동 수리 -> 승격 출판의 지식 제조 시스템으로 재편한다.`

기존 코어는 기준점이 아니다.
기존 코어는 이 목표에 얼마나 기여하는지 평가받는 대상이다.

## 15. Ref Stamp

- `branch`: `feat/pbs-v3`
- `head_sha`: `f71719898cd6e8e85fa192a0c0008ecd6d241632`
- `base_ref`: `origin/main`
- `base_sha`: `e87fa0c562c5e277305617e1eea36c112aa01b27`
