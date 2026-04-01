# APP 도메인 가이드

## 개요
`app/`은 사용자와 맞닿는 런타임 레이어를 책임진다. 게이트웨이, OpenDocuments 브리지, 검색 정책 연결, 세션 연속성, 소스/뷰어 정규화가 여기에 들어간다.

## 어디를 봐야 하나
| 작업 | 위치 | 메모 |
|------|------|------|
| 메인 사용자 HTTP 경로 | `ocp_runtime_gateway.py` | 게이트웨이 동작, 뷰어 서빙, 채팅 흐름 |
| 모델/런타임 브리지 | `opendocuments_openai_bridge.py` | OpenAI 호환 브리지와 대체 경로 처리 |
| 검색/질의 보정 | `ocp_policy.py` | `configs/rag-policy.yaml`과 의미를 맞춘다 |
| 세션/후속질문 메모리 | `multiturn_memory.py` | 후속 질문 재작성 동작 |
| 런타임 보조 유틸 | `runtime_gateway_support.py`, `runtime_source_index.py` | 인용/소스 정규화 보조 |
| 환경변수 로딩 | `runtime_config.py` | 저장소 `.env`와 프로세스 환경변수를 읽음 |

## 로컬 규칙
- 이 디렉터리는 OpenDocuments 위에 얇게 얹는 제품 레이어로 유지한다. 상위 저장소 내부를 사실상 포크하는 방향으로 가지 않는다.
- 런타임 설정은 반드시 환경변수 중심이어야 한다. 새 키가 필요하면 `os.getenv`를 흩뿌리기보다 `runtime_config.py`를 통해 추가한다.
- `viewer`/인용 동작은 단순 UI 부가요소가 아니라 런타임 정합성의 일부다.
- 정책 로직은 명시적 보조 함수와 설정 기반 규칙에 둔다. 요청 처리 함수 안에 불투명한 휴리스틱을 숨기지 않는다.

## 안티패턴
- 회사 엔드포인트, 베어러 토큰, 모델 값을 하드코딩하지 않는다.
- 기본값으로 로컬 채팅 대체 경로를 켜지 않는다. 현재 검증된 모드는 회사 경로 우선이며 대체 경로는 명시적이어야 한다.
- 정책 점수 계산 변경을 게이트웨이 전송 코드에 섞지 않는다.
- 인용 링크나 `viewer` 링크를 만들 때 소스 정규화 메타데이터를 우회하지 않는다.

## 변경 체크리스트
- 요청 흐름을 바꾼다면 `docs/v2/live-runtime-gateway.md`, `docs/v2/stage08-live-runtime-quality-report.md`, `docs/v2/stage12-live-runtime-report.md`를 먼저 본다.
- 정책/검색 동작을 바꾼다면 관련 `eval/` 게이트를 갱신하거나 다시 돌린다.
- 설정 키를 바꾼다면 상태 확인 출력과 `.env` 기대값까지 함께 반영한다.
