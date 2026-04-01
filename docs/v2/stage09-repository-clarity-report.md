# 2026-03-31 Stage 9 Report

## 목표

Stage 9의 목표는 이 저장소를 처음 보는 사람이 **v2 본체, 검증 자산, 생성물**을 바로 구분할 수 있게 만드는 것이다.

## 이번 단계에서 한 일

1. [README.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/README.md)를 제품 설명서 중심으로 다시 정리했다.
2. [repository-map.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/repository-map.md)를 추가해 v2 본체와 생성물을 구분했다.
3. Stage 9 전용 검사기 [check_stage09_repository_map.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage09_repository_map.py)를 추가했다.
4. 루트에 실행 코드가 흩어져 보이지 않도록, 핵심 코드는 `app/`, `ingest/`, `deployment/`, `eval/`, `configs/` 중심으로 설명을 고정했다.

## 저장소를 보는 기준

### v2 본체

- 제품 런타임: `app/`
- 문서 온보딩: `ingest/`
- 설정: `configs/`
- 실행/운영: `deployment/`
- 검증: `eval/`

### 설명 문서

- 제품 설명: [README.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/README.md)
- 저장소 지도: [repository-map.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/repository-map.md)
- 상태 요약: [project-plan-summary.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/project-plan-summary.md)
- 10단계 기준: [ten-stage-verification-plan.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/ten-stage-verification-plan.md)

### 실행 결과물

- generated evidence: `data/manifests/generated/`
- HTML citation views: `data/views/`
- staging / packages: `data/staging/`, `data/packages/`
- active pointers: `indexes/current.txt`, `indexes/previous.txt`
- runtime workspaces: `workspace/stage11/`, `workspace/stage12/`

## 검증

실행:

```powershell
python deployment/check_stage09_repository_map.py
```

결과:

- report: [stage09-repository-map-check.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage09-repository-map-check.json)
- `pass = true`
- `missing_core_paths = []`
- `missing_support_paths = []`
- `missing_directories = []`
- `root_python_files_present = false`

즉, 새로 보는 사람이 루트에서 곧바로 길을 잃게 만드는 stray Python entrypoint 는 현재 없다.

## 해석

Stage 9은 `pass` 이다.

이 pass 는 다음을 의미한다.

- v2 본체 경로가 README 와 repo map 에서 드러난다
- 생성물과 제품 코드의 경계가 문서로 고정됐다
- root 에서 혼란을 주는 임의 실행 파일이 보이지 않는다

Stage 9은 코드 품질이나 retrieval 품질을 승인하는 단계가 아니라, **저장소 가시성과 작업 진입 경로를 승인하는 단계**이다.
