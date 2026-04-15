# Play Book Studio

> Test UI: [http://192.168.119.16:5173/](http://192.168.119.16:5173/)  
> Runtime API: [http://192.168.119.16:8765/](http://192.168.119.16:8765/)

Play Book Studio는 `기술 문서를 수집해 위키 대백과형 운영·학습 런타임으로 바꾸는 제품`이다.

이 저장소의 기준선은 더 이상 `markdown viewer` 나 `문서 정리 도구`가 아니다.

현재 기준선은 아래다.

`source-first figure-aware technical wiki runtime`

## What The Product Is

이 제품은 아래를 함께 제공한다.

- `source-first corpus`
- `structured technical books`
- `entity / section / figure relation graph`
- `grounded chat`
- `user overlay`

즉 사용자는

- 책처럼 읽고
- 위키처럼 이동하고
- 챗봇으로 묻고
- 개인화 overlay 로 다시 작업을 이어간다.

## Current Commercial Scope

- current stage: `paid_poc_candidate`
- validated pack: `OpenShift 4.20`
- commercial scope: `OpenShift 4.20 source-first validated pack + customer document PoC`

현재 단계에서 이 제품은 `full sale` 이 아니다.

## Canonical Runtime Shape

최종 제품 자산의 canonical form 은 markdown 파일이 아니다.

현재 canonical runtime 은 아래를 합친 것이다.

- `structured technical book`
  - paragraph
  - code
  - table
  - figure
  - diagram
  - xref
- `wiki relations`
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

markdown 은 export 와 review 용 중간 산출물로만 취급한다.

## Product Surfaces

### 1. Playbook Library

- corpus / runtime / candidate / signal 상태 확인
- gold candidate 와 active runtime 확인
- control tower 메트릭 확인

### 2. Wiki Runtime Viewer

- book reading
- entity hub 탐색
- related sections / figures 이동
- source trace 확인

### 3. Workspace

- grounded chat
- related navigation
- next plays
- overlay 기반 개인화 흐름

## Current Runtime Capabilities

- `source-first runtime build`
  - official repo 우선, html-single fallback
- `one-click runtime rebuild`
  - rebuild -> materialize -> relation refresh -> active switch -> smoke
- `figure-aware runtime`
  - figure asset materialization
  - figure page
  - related figure / related section
- `grounded chat`
  - citation
  - active runtime viewer path
  - related links
- `user overlay`
  - favorite / check / note / recent position
  - next plays
  - usage signals

## Shared Test Server

- Frontend: [http://192.168.119.16:5173/](http://192.168.119.16:5173/)
- Workspace: [http://192.168.119.16:5173/workspace](http://192.168.119.16:5173/workspace)
- Playbook Library: [http://192.168.119.16:5173/playbook-library](http://192.168.119.16:5173/playbook-library)
- Runtime API: [http://192.168.119.16:8765/](http://192.168.119.16:8765/)

## Local Run

### Backend

```powershell
play_book.cmd ui --host 0.0.0.0 --port 8765 --no-browser
```

### Frontend

```powershell
Set-Location presentation-ui
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### One-Click Runtime Rebuild

```powershell
& .\.venv\Scripts\python.exe scripts\run_ocp420_one_click_runtime.py
```

## Main Runtime Routes

- `POST /api/chat`
- `GET /api/data-control-room`
- `GET /api/wiki-overlay-signals`
- `GET /api/repositories/search`
- `GET /docs/*`
- `GET /playbooks/*`
- `GET /wiki/entities/*`
- `GET /wiki/figures/*`

## Repo Reading Order

현재 기준선을 가장 빨리 파악하려면 아래 순서로 읽는다.

1. [AGENTS.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/AGENTS.md:1)
2. [PROJECT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PROJECT.md:1)
3. [CODEX_OPERATING_CHARTER.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/CODEX_OPERATING_CHARTER.md:1)
4. [Q1_8_PRODUCT_CONTRACT.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/Q1_8_PRODUCT_CONTRACT.md:1)
5. [P0_ARCHITECTURE_FREEZE_ADDENDUM.md](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/P0_ARCHITECTURE_FREEZE_ADDENDUM.md:1)
6. [TASK_BOARD.yaml](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/TASK_BOARD.yaml:1)

## Rule Reminder

`README.md` 는 active rule owner 가 아니다.

현재 기준은 항상 루트의 active rule set 을 따른다.
