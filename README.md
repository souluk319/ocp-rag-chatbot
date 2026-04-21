# PlayBookStudio

## 이 저장소는 무엇인가

이 저장소는 `PlayBookStudio(PBS)`를 다른 프로젝트에 편입하기 위해 정리한 `최소 handoff payload`입니다.

원래 작업 저장소 전체를 넘기는 대신, 실제 편입과 초기 통합에 필요한 것만 남겼습니다.
즉, 이 `main` 브랜치는 `전체 개발 히스토리 보관용`이 아니라 `다음 담당자가 바로 합치기 시작할 수 있는 기준선`입니다.

이 저장소의 목적은 아래 네 가지입니다.

1. PBS의 핵심 기능을 보전한다.
2. 다른 프로젝트와 합칠 때 불필요한 잡음과 대용량 산출물을 제거한다.
3. 정리 담당자가 저장소 구조를 빠르게 이해할 수 있게 한다.
4. 외부 데이터와 로컬 전용 자료의 경계를 분명하게 한다.

## 지금 이 저장소에 남겨둔 것

이 저장소에는 아래 항목만 남겨두었습니다.

- `presentation-ui/`
  - shared landing shell
  - PBS 주요 프론트엔드 화면
  - partner namespace shell
- `src/`
  - backend/runtime 코드
  - viewer, workspace, customer-pack, server route 처리 코드
- `data/`
  - 현재 payload가 동작하는 데 필요한 최소 tracked runtime 데이터
  - `wiki_runtime_books`
  - `wiki_assets`
  - `wiki_relations`
  - `gold_candidate_books`
- `manifests/`
  - 현재 코드 경로에서 참조하는 manifest 세트
- `schemas/`
  - 핵심 schema 파일
- `tests/`
  - 편입 직전 sanity check에 필요한 축소된 회귀 테스트만 남김
- 루트 실행 파일
  - `docker-compose.yml`
  - `Dockerfile.backend`
  - `pyproject.toml`
  - `.gitignore`
  - `README.md`

쉽게 말하면, `앱 코드`, `백엔드 코드`, `최소 runtime 데이터`, `핵심 manifest/schema`, `최소 검증 세트`만 남긴 상태입니다.

## 의도적으로 제거한 것

이 저장소에는 아래 항목이 없습니다.

- root의 다른 `.md` 문서들
  - handoff 혼선을 막기 위해 루트 문서는 `README.md` 하나만 남겼습니다.
- task board / scorecard / ops 문서
- scripts 전체
- pipelines 전체
- execution harness 결과물
- build logs
- multiturn/debug/demo residue
- quarantine 데이터
- 대규모 회귀 테스트, 실험 테스트, 분석용 테스트
- 로컬 전용 실행기와 launcher 잔재

즉, `운영 중 쌓이던 실험 흔적`과 `개발 편의용 보조 구조`는 모두 뺐고, `편입에 직접 필요한 표면`만 남겼습니다.

## 다음 담당자가 이 저장소를 어떻게 보면 되는가

이 저장소는 아래 관점으로 보면 됩니다.

- `merge baseline`
  - 다른 프로젝트와 합칠 때 기준이 되는 최소 PBS 표면
- `clean payload`
  - 내부 작업 흔적을 최대한 걷어낸 전달용 트리
- `not full historical repo`
  - 원래 PBS의 모든 실험, 리포트, 대용량 데이터, 보조 스크립트를 담은 저장소는 아님

따라서 이 저장소를 보고 “원래 있던 문서나 스크립트가 왜 없지?”라고 느껴질 수 있는데, 그건 누락이 아니라 의도된 정리 결과입니다.

## 현재 남아 있는 제품 표면

이 payload에서 유지하는 주요 진입 경로는 아래와 같습니다.

- `/`
  - shared landing shell
- `/studio`
- `/workspace`
- `/llmwikibook`
- `/playbook-library`
- `/partner/*`

정리 의도는 단순합니다.

- PBS 고유 경로는 그대로 유지한다.
- partner 기능은 sibling namespace로 분리한다.
- 공유 랜딩만 함께 쓰고, 기능 본체는 뒤섞지 않는다.

## 외부 대용량 데이터

대용량 데이터와 개인 보관 데이터는 Git에 넣지 않았습니다.

필요한 경우 아래 Drive 폴더를 사용하면 됩니다.

- [PBS external data folder](https://drive.google.com/drive/folders/136wfeJbcpst7iO3ZwBbwhzpbwMo_WiSh?usp=sharing)

이 링크는 다음 상황에서만 사용하면 됩니다.

- 코드 merge는 끝났는데 실제 데이터 재현이 필요할 때
- runtime 동작을 더 깊게 검증해야 할 때
- gold data나 source mirror를 다시 받아야 할 때
- customer/private 문서 관련 자료를 로컬에 복원해야 할 때

권장 순서는 아래와 같습니다.

1. 먼저 이 저장소 코드만으로 편입 작업을 진행합니다.
2. 코드 merge와 라우트 통합이 끝난 뒤, 정말 필요한 데이터만 Drive에서 받습니다.
3. 받은 데이터는 로컬에만 두고 사용합니다.
4. 받은 데이터를 편입 저장소 `main`에 다시 넣지 않습니다.

## Git 밖에서 따로 관리해야 하는 것

아래 자료는 이 저장소에 intentionally 포함하지 않았습니다.

- 골드데이터 원본
  - `data/gold_corpus_ko`
  - `data/gold_manualbook_ko`
  - `data/silver_ko`
- raw source / rebuild 계열
  - `data/bronze/raw_html`
  - `data/bronze/source_bundles`
  - `artifacts/official_lane/repo_wide_official_source`
- 실행/평가 산출물
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

정리하면, `다시 만들 수 있는 것`, `너무 큰 것`, `개인/민감한 것`, `현재 편입과 직접 관계없는 것`은 모두 Git 밖으로 분리한 상태입니다.

## 절대 다시 Git에 넣지 말 것

다음 항목은 편입 저장소 `main`에 다시 넣지 않는 것을 기본 규칙으로 삼는 것이 좋습니다.

- `.env`
- `artifacts/**`
- `data/bronze/raw_html/**`
- `data/bronze/source_bundles/**`
- 대용량 gold data 원본
- 개인/customer 원본 문서
- 실험 리포트
- execution harness 재생성본
- task board / scorecard / local launcher 재생성본

이 규칙을 지켜야 `main`이 다시 무거워지거나 지저분해지는 것을 막을 수 있습니다.

## 합칠 때 추천 순서

다음 담당자가 실제로 편입 작업을 할 때는 이 순서를 추천합니다.

1. 이 저장소의 `main`을 기준선으로 받습니다.
2. 상대 프로젝트 쪽 shared landing 진입 구조와 route namespace를 먼저 확인합니다.
3. PBS 쪽 경로(`/studio`, `/workspace`, `/llmwikibook`, `/playbook-library`)가 유지되는지 먼저 맞춥니다.
4. partner 기능은 `/partner/*` namespace 아래에서 분리된 상태로 편입합니다.
5. 코드 편입이 끝난 뒤에만 필요한 외부 데이터를 Drive에서 선택적으로 가져옵니다.
6. 마지막에 build와 최소 route regression만 다시 확인합니다.

핵심은 `코드 먼저`, `데이터는 나중`, `기능은 namespace 분리`, `main은 계속 얇게 유지`입니다.

## 빠른 실행

로컬에서 기본 실행을 확인하려면 아래 명령을 사용하면 됩니다.

```powershell
docker compose up -d --build backend frontend qdrant
```

## 최소 검증

편입 직후 sanity check는 아래 정도면 충분합니다.

```powershell
npm --prefix presentation-ui run build
npm --prefix presentation-ui exec vitest run src/app/handoff.test.ts
.\.venv\Scripts\python.exe -m pytest tests/test_app_server.py tests/test_customer_pack_direct_viewer_route.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_app_viewers_routes.py -q -k "canonicalize_viewer_path or viewer_document_route_supports_entity_and_figure_paths or viewer_document_route_falls_back_to_normalized_sections_for_known_book or viewer_path_local_raw_html_fallback"
```

이 검증은 다음을 확인합니다.

- 프론트엔드가 빌드되는가
- shared landing handoff가 유지되는가
- 서버 route가 PBS surface를 제대로 내보내는가
- viewer route의 최소 핵심 경로가 깨지지 않았는가

## 마지막 메모

이 저장소는 `PBS 전체 개발 저장소`가 아니라 `편입용 최소 전달판`입니다.

따라서 이후에 더 많은 데이터나 툴링이 필요해지면,
이 저장소를 다시 비대하게 만들기보다는
필요한 항목만 외부 데이터 폴더나 후속 브랜치에서 선택적으로 추가하는 방식이 더 안전합니다.
