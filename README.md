# PlayBookStudio

이 저장소는 `다른 프로젝트에 편입시키기 위한 minimal incorporation payload` 이다.

핵심 원칙은 단순하다.

- `main` 은 편입에 필요한 코드와 최소 runtime 표면만 남긴다.
- 대용량 데이터, 생성 산출물, ops/task board, 대규모 스크립트 묶음은 Git 밖으로 뺀다.
- 정리 담당자는 이 저장소를 `합치기용 기준선`으로만 보고, 추가 데이터는 필요할 때만 외부에서 받는다.

## 이 브랜치에 남긴 것

- PBS 앱 코드
- backend/runtime 핵심 Python 패키지
- shared landing + partner namespace shell
- schemas / manifests
- 최소 active runtime data
  - `data/wiki_runtime_books`
  - `data/wiki_assets`
  - `data/wiki_relations`
  - `data/gold_candidate_books`
- 핵심 handoff 테스트 subset

## 이 브랜치에서 뺀 것

- `data/quarantine/**`
- `scripts/**`
- `pipelines/**`
- `reports/execution_harness/**`
- `reports/multiturn/**`
- `reports/technical_notes/**`
- `reports/build_logs/**`
- `reports/demo_simulator/**`
- `docs/playbook_wiki/**`
- `TASK_BOARD.yaml`
- `PRODUCT_GATE_SCORECARD.yaml`
- `play_book.cmd`
- `docker-compose.dev.yml`
- 대규모 회귀/실험 테스트 세트
- 임시 audit residue

## 외부 대용량 데이터

Git 에서 제외된 대용량 데이터와 개인 보관 데이터는 아래 Drive 폴더를 기준으로 본다.

- [PBS external data folder](https://drive.google.com/drive/folders/136wfeJbcpst7iO3ZwBbwhzpbwMo_WiSh?usp=sharing)

정리 담당자는 아래 원칙으로 처리하면 된다.

- `코드 merge` 만 필요하면 Drive 데이터 없이 먼저 편입한다.
- `재현 / 검증 / 데이터 재구성` 이 필요할 때만 필요한 폴더만 내려받는다.
- 내려받은 데이터는 `로컬 전용` 으로 두고, 편입 저장소 main 에 다시 커밋하지 않는다.

## 사용자가 따로 챙겨야 하는 것

이 브랜치에 없는 아래 자료는 Git에 합치지 말고 별도로 보관한다.

- 골드데이터 원본
  - `data/gold_corpus_ko`
  - `data/gold_manualbook_ko`
  - `data/silver_ko`
- raw source / rebuild 계열
  - `data/bronze/raw_html`
  - `data/bronze/source_bundles`
  - `artifacts/official_lane/repo_wide_official_source`
- 실행 산출물 / 평가 산출물
  - `artifacts/runtime`
  - `artifacts/retrieval`
  - `artifacts/answering`
  - `artifacts/customer_packs`
- customer/private 문서 원본
- 개인 분석 메모
- 로컬 캐시
- `.venv`
- `node_modules`
- 재생성 가능한 하네스/실험 산출물

공유가 필요하면 별도 저장소나 드라이브로 관리하고, 편입 main 의 진실 소스는 이 브랜치의 코드와 manifest 로 본다.

## 절대 다시 Git 에 넣지 말 것

- `.env`
- `artifacts/**`
- `data/bronze/raw_html/**`
- `data/bronze/source_bundles/**`
- 대용량 gold data 원본
- 개인/customer 원본 문서
- 실험 리포트와 execution harness 재생성본
- task board / scorecard / local launcher 재생성본

## 제품 표면

- `/` shared landing shell
- `/studio`
- `/workspace`
- `/llmwikibook`
- `/playbook-library`
- `/partner/*`

기존 PBS direct entry 는 유지하고, partner 기능은 sibling namespace 로 분리한다.

## 빠른 실행

```powershell
docker compose up -d --build backend frontend qdrant
```

## 최소 검증

```powershell
npm --prefix presentation-ui run build
npm --prefix presentation-ui exec vitest run src/app/handoff.test.ts
.\.venv\Scripts\python.exe -m pytest tests/test_app_server.py tests/test_customer_pack_direct_viewer_route.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_app_viewers_routes.py -q -k "canonicalize_viewer_path or viewer_document_route_supports_entity_and_figure_paths or viewer_document_route_falls_back_to_normalized_sections_for_known_book or viewer_path_local_raw_html_fallback"
```

## 참고

- 편입 후 확장 작업은 이 clean payload 위에서만 진행한다.
- 데이터가 필요하면 먼저 Drive 를 보고, 정말 필요한 것만 로컬로 가져와서 쓰는 방식이 기본이다.
- 이 저장소는 `PBS 전체 작업 레포`가 아니라 `편입용 최소 payload` 이다.
