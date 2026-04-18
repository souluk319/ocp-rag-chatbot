# PlayBookStudio

PBS runtime repository입니다.

이 문서는 `reference README` 이다.  
현재 실행 계약은 아래 active root 문서를 우선한다.

- `AGENTS.md`
- `PROJECT.md`
- `RUNTIME_ARCHITECTURE_CONTRACT.md`
- `EXECUTION_HARNESS_CONTRACT.md`
- `SECURITY_BOUNDARY_CONTRACT.md`

제품 표면은 아래 3가지로 본다.

- `Playbook Library`
- `Wiki Runtime Viewer`
- `Chat Workspace`

공식 문서 lane 의 기준은 아래다.

- `repo/AsciiDoc first`
- `published HTML` 은 `reader benchmark / verification / fallback`
- `published PDF` 는 `reader verification / fallback`

`Playbook` 은 최신 고정 파이프라인을 통과한 문서 중,
`원문 충실도 + 챗봇 상호작용성` 을 동시에 만족하는 위키 단위다.

## Requirements

- `Docker Desktop` 또는 `Docker Engine + Compose plugin`
- `Python 3.11+`
- `Node.js` 최근 LTS

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -e .

cd presentation-ui
npm install
cd ..
```

## Run

### 1. 팀 공유용 서빙 주소

PBS 기본 주소는 `8765` 입니다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\pbs-up.ps1
```

- 같은 PC에서 확인: `http://127.0.0.1:8765`
- 같은 LAN의 다른 PC에서 확인: `http://<내-PC-LAN-IP>:8765`

`scripts\pbs-up.ps1` 는 아래를 한 번에 처리합니다.

- `docker compose up -d qdrant`
- `presentation-ui` build
- `0.0.0.0:8765` PBS shared serve 기동

중지:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\pbs-down.ps1
```

### 2. 빠른 UI 개발

UI를 빠르게 수정하면서 보려면 `5173` 개발 서버를 쓰고, 실제 데이터/API는 계속 `8765` 백엔드를 사용합니다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\pbs-dev-up.ps1
```

- 개발모드: `http://127.0.0.1:5173`
- 제품확인: `http://127.0.0.1:8765`
- 같은 LAN의 다른 PC에서 확인: `http://<내-PC-LAN-IP>:8765`
- `scripts\pbs-dev-up.ps1` 는 `qdrant + shared backend(8765) + vite(5173)` 를 함께 띄웁니다.
- Vite가 `/api`, `/docs`, `/playbooks`, `/wiki` 를 백엔드 `8765` 로 프록시합니다.

## Common Commands

### 단일 질의 실행

```powershell
.\play_book.cmd ask --query "etcd 백업 절차 알려줘"
```

### Runtime report 생성

```powershell
.\play_book.cmd runtime
```

### OCP 4.20 one-click runtime rebuild

```powershell
powershell -ExecutionPolicy Bypass -File scripts\codex_python.ps1 `
  -ScriptPath scripts\run_ocp420_one_click_runtime.py `
  -WriteScope reports/build_logs/ocp420_one_click_runtime_report.json `
  -VerifyCmd "ocp420 one-click runtime"
```

산출물:

- `reports/build_logs/ocp420_one_click_runtime_report.json`

## Test

백엔드:

```powershell
.\.venv\Scripts\python -m pytest tests/test_app_runtime_ui.py tests/test_app_data_control_room.py
```

프런트:

```powershell
cd presentation-ui
npm test
```
