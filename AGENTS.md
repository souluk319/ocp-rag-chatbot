# 프로젝트 지식 베이스

**생성일:** 2026-04-01
**커밋:** `b590d0c`
**브랜치:** `feat/OCP_v2_planB`

## 개요
이 저장소는 OpenDocuments를 중심으로 구성된 폐쇄망 OCP 운영용 RAG 제품 레이어다. OCP 전용 수집 파이프라인, 정책, 런타임 연결부, 평가 게이트, 에어갭 배포 흐름은 이 저장소가 책임지며, 상위 OpenDocuments 본체나 원천 미러 저장소 자체는 여기서 소유하지 않는다.

## 구조
```text
ocp-rag-chatbot/
├── app/          런타임 게이트웨이, 브리지, 정책, 소스 인덱싱
├── configs/      소스 프로필, 메타데이터 스키마, 검색/응답 정책
├── data/         매니페스트와 플레이스홀더; 생성 산출물은 Git 비추적
├── deployment/   준비 상태 점검, 번들, 스테이징, 활성화, 롤백, 스모크 흐름
├── docs/v2/      권위 문서, 설계, 단계별 검증 기록
├── eval/         벤치마크 러너, 하니스, 픽스처, 릴리즈 게이트
├── indexes/      current/previous/archive 포인터와 생성 인덱스 출력
└── ingest/       openshift-docs 정규화 파이프라인
```

## 어디를 봐야 하나
| 작업 | 위치 | 메모 |
|------|------|------|
| 제품 개요와 런타임 구조 파악 | `README.md`, `docs/v2/repository-map.md` | 깊은 수정 전 가장 먼저 볼 곳 |
| 런타임 요청 흐름 | `app/ocp_runtime_gateway.py`, `app/opendocuments_openai_bridge.py` | 사용자 HTTP 경로와 브리지 |
| 검색/응답 정책 | `app/ocp_policy.py`, `configs/rag-policy.yaml` | 정책 변경 시 평가 후속 작업 필요 |
| 런타임 설정/환경변수 로딩 | `app/runtime_config.py` | 환경변수 기반 모델/런타임 설정 |
| 소스 범위와 승인된 미러 | `configs/source-profiles.yaml`, `configs/active-source-profile.yaml` | 공식 OCP 범위는 여기서 관리 |
| 문서 정규화 | `ingest/normalize_openshift_docs.py` | `.adoc` → 텍스트/뷰/메타데이터 파이프라인 |
| Stage 11/12/14 운영 흐름 | `deployment/README.md`, `docs/v2/stage11-readiness.md`, `docs/v2/stage12-live-runtime-report.md`, `docs/v2/stage14-runtime-launch.md` | 배포 흐름은 증거 중심 |
| 평가/릴리즈 게이트 | `eval/README.md`, `eval/run_stage10_release_gate.py`, `docs/v2/evaluation-spec.md` | 임의 추정보다 평가 문서가 우선 |
| 현재 상태와 마일스톤 | `docs/v2/project-plan-summary.md` | 브랜치 의도와 검증 완료 단계 |

## 규칙
- `docs/v2/`를 단계 상태, 계약, 흐름 존재 이유를 설명하는 권위 계층으로 취급한다.
- 런타임 엔드포인트/모델 설정은 반드시 환경변수 기반으로 유지하고, 비밀값과 구체 엔드포인트는 코드나 커밋 문서에 남기지 않는다.
- 소스 신뢰도는 명시적이다. 공식 OCP 자료를 우선하고, OKD/ROSA/OSD/MicroShift 같은 차단 제품은 정책/프로필 데이터에 반영한다.
- 이 저장소에는 추적 대상 매니페스트, 스키마, 플레이스홀더만 둔다. 생성 코퍼스와 빌드된 인덱스는 저장하지 않는다.
- 상위 OpenDocuments 가정을 이 저장소 안에서 비틀기보다, 얇은 제품 레이어 연결부를 선호한다.

## 안티패턴 (이 프로젝트)
- 코드나 권위 문서가 있는데도 `data/`, `indexes/`, 생성 JSON 보고서를 제품의 진실 원천처럼 다루지 않는다.
- 생성 코퍼스, 렌더된 뷰, 스테이징 번들, 빌드된 인덱스를 커밋하지 않는다.
- `docs/v2/` 또는 `data/manifests/generated/` 아래 대응 보고서/증거 없이 어떤 단계가 끝났다고 주장하지 않는다.
- 소스 범위를 가볍게 넓히지 않는다. source-profile과 정책 변경은 공식 OCP 경계를 분명히 유지해야 한다.
- 배포 흐름에서 승인, 검증, 스테이징, 스모크, 활성화, 롤백 순서를 건너뛰지 않는다.

## 이 저장소만의 스타일
- 문서는 직설적이고 운영 중심이다. 제품 설명은 `README.md`, 구현 지도는 `docs/v2/repository-map.md`, 단계별 증거는 전용 보고서에 둔다.
- 검증은 단계 단위로 나뉜다. 많은 스크립트와 문서가 stage 번호를 이름에 포함하므로, 워크플로를 확장할 때 그 naming을 유지한다.
- 원문 문서는 영어여도, 운영자에게 보이는 기본 응답과 스모크 질문은 한국어 맥락을 반영한다.

## 주요 명령어
```bash
python deployment/start_runtime_stack.py
python deployment/check_stage11_readiness.py
python deployment/run_live_runtime_smoke.py
python eval/run_stage10_release_gate.py
python ingest/normalize_openshift_docs.py --help
```

## 메모
- 이 워크스페이스에는 Python LSP(`basedpyright-langserver`)가 아직 없어서, 심볼 추적은 직접 읽기/검색 위주로 해야 한다.
- `docs/v2/2026-04-01/`는 날짜 기준 증거 묶음이다. 새 권위 문서는 날짜 폴더가 아니라 `docs/v2/` 아래에 두는 편이 맞다.
- 로컬 가이드는 각 도메인에 자체 워크플로가 있을 때만 만든다. 현재 분리는 `app`, `deployment`, `eval`, `ingest`, `docs/v2`다.
