# PlayBookStudio

## 이 문서는 누구를 위한 것인가

이 README는 `다음 편입 담당자`를 위한 안내서입니다.

이 저장소를 처음 받는 사람이 아래 네 가지를 빠르게 이해할 수 있도록 작성했습니다.

1. 이 저장소가 원래 PBS 전체 저장소와 무엇이 다른가
2. 지금 여기 남아 있는 파일은 무엇을 위한 것인가
3. 합칠 때 어떤 순서로 진행하면 안전한가
4. 어떤 데이터는 Git 밖에서 따로 다뤄야 하는가

이 문서는 작업 메모가 아니라 `편입 기준선 설명서`로 보면 됩니다.

## 먼저 한 줄로 요약하면

이 저장소는 `PlayBookStudio(PBS)`를 다른 프로젝트에 편입하기 위해 정리한 `최소 handoff payload`입니다.

즉, 이 `main` 브랜치는 아래 성격을 갖습니다.

- `전체 개발 이력 보관소`가 아닙니다.
- `실험 산출물까지 포함한 원본 작업 트리`도 아닙니다.
- `다음 담당자가 바로 합치기 시작할 수 있는 최소 기준선`입니다.

쉽게 말해, `합치는 데 필요한 것만 남기고`, `잡음이 되는 것은 최대한 걷어낸 저장소`입니다.

## 왜 이렇게 정리했는가

원래 PBS 작업 저장소에는 아래 성격의 자료가 많이 섞여 있었습니다.

- 실험 중간 산출물
- 대용량 데이터
- 개인 보관용 자료
- 재생성 가능한 보고물
- 운영 중 누적된 보조 문서와 도구

그 상태 그대로 편입하면 아래 문제가 생깁니다.

- 저장소가 너무 크고 무거워집니다.
- 다음 담당자가 무엇이 핵심 코드인지 판단하기 어려워집니다.
- 다른 프로젝트와 합칠 때 충돌면이 불필요하게 넓어집니다.
- 다시 Git에 올리면 안 되는 데이터까지 섞일 위험이 커집니다.

그래서 이번 브랜치는 `제품 기능을 보전하면서도`, `편입에 직접 필요하지 않은 것`은 의도적으로 걷어낸 상태입니다.

## 지금 이 저장소에 남겨둔 것

현재 이 저장소에는 아래 항목만 남겨두었습니다.

### 1. 프론트엔드 진입면

- `presentation-ui/`
- shared landing shell
- PBS 주요 화면
- partner namespace shell

즉, 사용자가 실제로 보게 되는 entry surface와 route shell은 유지했습니다.

### 2. 백엔드 및 runtime 코드

- `src/`
- backend/runtime 코드
- viewer 처리 코드
- workspace 처리 코드
- customer-pack / server route 처리 코드

즉, 화면만 남긴 것이 아니라 `실제로 동작하는 핵심 로직`도 함께 남겼습니다.

### 3. 최소 runtime 데이터 및 편입용 데이터셋

- `data/`
- `wiki_runtime_books`
- `wiki_assets`
- `wiki_relations`
- `gold_candidate_books`
- `gold_manualbook_ko`
- `silver_ko`
- `gold_corpus_ko`

이 데이터는 두 부류로 보면 됩니다.

- 앱이 깨지지 않고 도는 데 필요한 `tracked runtime truth`
- 편입 후 바로 이어서 작업하기 쉽게 함께 싣는 `핵심 한국어 데이터셋`

즉, 이번 편입 브랜치에서는 `gold_manualbook_ko`, `silver_ko`, `gold_corpus_ko` 세 폴더를 의도적으로 함께 가져갑니다.

### 4. 계약과 구조 파일

- `manifests/`
- `schemas/`

이 폴더들은 코드가 runtime 구조를 이해하는 데 필요한 기준선 역할을 합니다.

### 5. 최소 검증 세트

- `tests/`

전체 테스트를 다 들고 온 것은 아니고, `편입 직전 sanity check`에 필요한 최소 회귀만 남겼습니다.

### 6. 루트 실행 파일

- `docker-compose.yml`
- `Dockerfile.backend`
- `pyproject.toml`
- `.gitignore`
- `README.md`

정리하면, 지금 이 저장소는 `앱 코드`, `백엔드 코드`, `최소 runtime truth`, `manifest/schema`, `최소 회귀 검증`만 담고 있습니다.

## 의도적으로 제거한 것

이 저장소에는 아래 항목이 없습니다.

- root의 다른 `.md` 문서
- nested markdown payload
- task board / scorecard
- scripts 전체
- pipelines 전체
- execution harness 결과물
- build logs
- multiturn/debug/demo residue
- quarantine 데이터
- 대규모 실험 테스트
- 분석용 테스트
- 로컬 launcher 잔재

특히 문서 쪽은 혼선을 막기 위해 `README.md` 하나만 남겼습니다.

따라서 "원래 있던 문서가 왜 없지?"라는 느낌이 들 수 있는데, 그건 누락이 아니라 `전달 효율을 높이기 위한 의도된 컷`입니다.

## 다음 담당자는 이 저장소를 어떻게 이해하면 되는가

이 저장소는 아래 세 가지 관점으로 보면 가장 정확합니다.

### merge baseline

다른 프로젝트와 합칠 때 기준이 되는 최소 PBS 표면입니다.

### clean payload

내부 작업 흔적을 최대한 걷어낸 전달용 트리입니다.

### not full historical repo

PBS의 모든 실험, 리포트, 대용량 데이터, 보조 스크립트를 담아둔 완전한 이력 저장소는 아닙니다.

즉, `없어서 이상한 것`이 아니라 `없어야 정상인 것`이 많습니다.

## 현재 유지하는 제품 표면

이 payload에서 유지하는 주요 진입 경로는 아래와 같습니다.

- `/`
- `/studio`
- `/workspace`
- `/llmwikibook`
- `/playbook-library`
- `/partner/*`

이 구조에서 중요한 원칙은 세 가지입니다.

1. PBS 고유 경로는 최대한 유지합니다.
2. partner 기능은 sibling namespace로 분리합니다.
3. 공유 랜딩만 함께 쓰고, 기능 본체는 무리하게 한 덩어리로 섞지 않습니다.

즉, 합칠 때도 `겉표면은 공유`, `기능 본체는 분리`, `기존 PBS route truth는 보전`이 기준입니다.

## 외부 대용량 데이터는 어디에 있는가

대용량 데이터 대부분과 개인 보관 데이터는 Git에 넣지 않았습니다.

필요한 경우 아래 Drive 폴더를 사용하면 됩니다.

- [PBS external data folder](https://drive.google.com/drive/folders/136wfeJbcpst7iO3ZwBbwhzpbwMo_WiSh?usp=sharing)

이 링크는 아래 상황에서만 보는 것을 권장합니다.

- 코드 merge는 끝났는데 실제 데이터 재현이 필요할 때
- runtime 동작을 더 깊게 검증해야 할 때
- gold data나 source mirror를 다시 받아야 할 때
- customer/private 자료를 로컬에 복원해야 할 때

중요한 점은 이번 브랜치에서 아래 세 폴더는 이미 함께 싣는다는 것입니다.

- `data/gold_manualbook_ko`
- `data/silver_ko`
- `data/gold_corpus_ko`

따라서 Drive는 `이 세 폴더의 대체 source`가 아니라, 나머지 대용량 자료나 보조 복원 자료를 위한 외부 보관소로 이해하면 됩니다.

## Git 밖에서 따로 관리해야 하는 것

아래 자료는 이 저장소에 포함하지 않았고, 앞으로도 기본적으로 Git 밖에서 다루는 것이 맞습니다.

### raw source / rebuild 계열

- `data/bronze/raw_html`
- `data/bronze/source_bundles`
- `artifacts/official_lane/repo_wide_official_source`

### 실행/평가 산출물

- `artifacts/runtime`
- `artifacts/retrieval`
- `artifacts/answering`
- `artifacts/customer_packs`

### 그 외 로컬 전용 자료

- customer/private 문서 원본
- 개인 분석 메모
- 로컬 캐시
- `.venv`
- `node_modules`
- 재생성 가능한 하네스/실험 산출물

정리하면, 아래 네 가지는 Git 밖으로 빼는 것이 원칙입니다.

- 다시 만들 수 있는 것
- 너무 큰 것
- 개인/민감한 것
- 현재 편입과 직접 관련 없는 것

## 절대 다시 Git에 넣지 말 것

편입 저장소 `main`을 계속 얇고 깨끗하게 유지하려면, 아래 항목은 다시 넣지 않는 것을 기본 규칙으로 삼는 것이 좋습니다.

- `.env`
- `artifacts/**`
- `data/bronze/raw_html/**`
- `data/bronze/source_bundles/**`
- 개인/customer 원본 문서
- 실험 리포트
- execution harness 재생성본
- task board / scorecard / local launcher 재생성본

이 규칙을 지켜야 `main`이 다시 커지거나, 전달용 브랜치가 다시 혼탁해지는 것을 막을 수 있습니다.

## 실제 편입 작업은 어떤 순서가 좋은가

다음 담당자가 실제로 합칠 때는 아래 순서를 추천합니다.

1. 이 저장소의 `main`을 편입 기준선으로 받습니다.
2. 상대 프로젝트의 shared landing 구조와 route namespace를 먼저 확인합니다.
3. PBS 쪽 경로(`/studio`, `/workspace`, `/llmwikibook`, `/playbook-library`)가 유지되는지 먼저 맞춥니다.
4. partner 기능은 `/partner/*` 아래에서 분리된 상태로 편입합니다.
5. `gold_manualbook_ko`, `silver_ko`, `gold_corpus_ko`는 이미 포함되어 있으므로, 그 외 데이터만 필요할 때 Drive에서 선택적으로 가져옵니다.
6. 마지막에 build와 최소 route regression만 다시 확인합니다.

핵심만 줄이면 아래 네 줄입니다.

- 코드 먼저
- 핵심 3종 데이터는 같이 간다
- 그 외 큰 데이터는 나중
- 기능은 namespace 분리
- `main`은 계속 얇게 유지

## 빠르게 실행해보고 싶다면

로컬에서 기본 구동을 확인하려면 아래 명령을 사용하면 됩니다.

```powershell
docker compose up -d --build backend frontend qdrant
```

## 편입 직후 최소 검증

편입 직후 sanity check는 아래 정도면 충분합니다.

```powershell
npm --prefix presentation-ui run build
npm --prefix presentation-ui exec vitest run src/app/handoff.test.ts
.\.venv\Scripts\python.exe -m pytest tests/test_app_server.py tests/test_customer_pack_direct_viewer_route.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_app_viewers_routes.py -q -k "canonicalize_viewer_path or viewer_document_route_supports_entity_and_figure_paths or viewer_document_route_falls_back_to_normalized_sections_for_known_book or viewer_path_local_raw_html_fallback"
```

이 검증은 아래를 확인합니다.

- 프론트엔드가 빌드되는가
- shared landing handoff가 유지되는가
- 서버 route가 PBS surface를 제대로 내보내는가
- viewer route 핵심 경로가 깨지지 않았는가

## 마지막 안내

이 저장소는 `PBS 전체 개발 저장소`가 아니라 `편입용 최소 전달판`입니다.

따라서 이후 더 많은 데이터나 툴링이 필요해지면,
이 브랜치를 다시 비대하게 만들기보다
필요한 항목만 외부 데이터 폴더나 후속 브랜치에서 선택적으로 추가하는 방식이 더 안전합니다.

이 README만 읽고도 다음 담당자가 아래 판단을 바로 할 수 있으면 이 저장소의 목적은 달성된 것입니다.

- 무엇이 남아 있는가
- 무엇이 빠져 있는가
- 왜 이렇게 잘랐는가
- 무엇부터 합치면 되는가
- 어떤 데이터는 이미 포함되었고, 어떤 데이터는 Git 밖에서 다뤄야 하는가
