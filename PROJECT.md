# Project

## Product Charter

Play Book Studio 는 `기술 문서를 위키 대백과형 운영·학습 플랫폼으로 바꾸고, buyer/demo/release packet surface 까지 연결하는 제품`이다.

제품의 핵심은 문서를 저장하는 것이 아니라 아래를 자동으로 만드는 것이다.

- `structured technical book`
- `entity hub`
- `section relation`
- `figure / diagram asset`
- `chat navigation`
- `user overlay`

현재 첫 상업 범위는 `OpenShift 4.20 source-first validated pack + customer document PoC` 다.

## Canonical Product Form

최종 자산의 canonical form 은 `markdown 파일`이 아니다.

최종 자산은 아래를 합친 `structured technical wiki runtime` 이다.

- `book blocks`
  - paragraph
  - code
  - table
  - figure
  - diagram
  - admonition
  - xref
- `relation assets`
  - entity hubs
  - related books
  - related sections
  - related figures
  - backlinks
- `user overlay`
  - favorites
  - checks
  - private notes
  - recent positions

`markdown` 은 diff, export, review 를 위한 파생 형식일 뿐이다.

## Product Promise

이 제품은 아래를 약속한다.

1. 공식 source 와 fallback source 를 수집해 재현 가능한 코퍼스를 만든다.
2. raw 문서를 reader-grade 실행형 북으로 변환한다.
3. 문서 / 엔터티 / 절차 / 그림이 연결된 위키 탐색면을 제공한다.
4. 챗봇이 위키 런타임과 같은 근거 집합 위에서 동작한다.
5. 사용자의 overlay 행동을 개인화 next play 와 운영 backlog 신호로 되먹인다.
6. customer/private 문서를 같은 위키 아키텍처 안에서 `pack boundary labeled runtime` 으로 수용한다.

## Non-Promise

이 제품은 아직 아래를 약속하지 않는다.

- 모든 포맷 완벽 지원
- 모든 diagram semantic parsing 완성
- full-sale 단계
- 임의의 고객 문서를 zero-touch 로 자동 product-grade 승격

현재 정직한 단계는 `paid_poc_candidate` 다.

## Source Authority

권위 계층은 아래로 고정한다.

1. `Vendor Official Source`
2. `Reviewed Translation`
3. `Verified Operational Evidence`
4. `Playbook Synthesis`
5. `Model Prose`

하위 tier 는 상위 tier 를 보강할 수는 있어도 뒤집을 수 없다.

## Runtime Doctrine

현재 기본선은 아래 자동화 경로다.

`official source repo or html-single fallback -> parse -> structured book -> reader-grade shaping -> wiki relations -> figure-aware runtime -> user overlay -> chatbot/runtime integration`

customer lane 은 아래를 기본선으로 추가한다.

`customer source -> parsed artifact -> structured book candidate -> reviewed pack candidate -> pack runtime`

즉 제품의 본질은 `문서를 예쁘게 렌더`하는 것이 아니라, `운영과 학습이 가능한 connected technical wiki` 를 만드는 것이다.

## Current Product Focus

현재 우선순위는 아래다.

1. `위키 정보 구조 정리`
2. `full runtime relation quality`
3. `figure/diagram coverage`
4. `overlay 를 개인화 플레이와 운영 신호로 연결`
5. `buyer/demo/release packet surface 정리`
6. `customer document lane 계약 고정`

## Customer Pack Lane

customer document PoC 는 별도 실험 레인이 아니라 제품 안의 공식 lane 이다.

이 lane 은 아래로 고정한다.

`customer source -> parsed artifact -> structured book candidate -> reviewed pack candidate -> pack runtime`

공식 runtime 과 customer runtime 은 같은 viewer, 같은 chat surface 를 공유할 수 있지만, 같은 security boundary 를 공유하지 않는다.

## Working Style

이 프로젝트의 기본 일 방식은 아래다.

`archive -> contract rewrite -> source-first build -> runtime evidence -> promotion`

모든 execution milestone 은 아래 하네스를 먼저 만든 뒤 시작한다.

`prepare_execution_harness -> manifest -> local worklog -> code and evidence -> final report`

실질 milestone 은 기본적으로 병렬 lane 으로 진행한다.

- `Main lane`
- `Explorer lane`
- `Worker 또는 Reviewer lane`

lane 마다 worktree 와 write scope 를 분리하고, Main lane 이 최종 통합과 closeout packet 을 맡는다.

trial 방식이 필요할 때만 아래를 쓴다.

`reference -> trials -> hybrid -> winner -> promotion`

## Rule Ownership And Precedence

우선순위는 아래다.

1. `AGENTS.md`
2. `CODEX_OPERATING_CHARTER.md`
3. `PROJECT.md`
4. `P0_ARCHITECTURE_FREEZE_ADDENDUM.md`
5. `PARSED_ARTIFACT_CONTRACT.md`
6. `SECURITY_BOUNDARY_CONTRACT.md`
7. `Q1_8_PRODUCT_CONTRACT.md`
8. `OWNER_SCENARIO_SCORECARD.yaml`
9. `TASK_BOARD.yaml`

`README.md` 와 `archive/` 아래 문서는 active owner 가 아니다.
