# INGEST 도메인 가이드

## 개요
`ingest/`는 승인된 원천 자료를 인덱싱 가능한 정규화 텍스트, 메타데이터, `viewer`용 산출물로 바꾸는 역할을 한다.

## 어디를 봐야 하나
| 작업 | 위치 | 메모 |
|------|------|------|
| 범위 요약 | `README.md` | 온보딩 책임 범위 |
| 메인 파이프라인 | `normalize_openshift_docs.py` | 핵심 정규화 로직 |
| 소스 경계 | `../configs/source-profiles.yaml`, `../configs/source-manifest.yaml` | 승인된 소스 범위와 메타데이터 |
| 출력 계약 | `../configs/chunk-schema.yaml`, `../configs/metadata-schema.yaml`, `../docs/v2/chunking-contract.md` | 청크/메타데이터 정합성 |

## 로컬 규칙
- 1급 원천은 공식 `openshift-docs`다. 더 넓은 소스 확장은 프로필/매니페스트에 명시적으로 드러나야 한다.
- 정규화는 청크에서 섹션/`viewer` 경로까지 인용 추적 가능성을 보존해야 한다.
- 신뢰도/제품/버전 메타데이터는 선택 장식이 아니라 파이프라인 출력의 일부다.

## 안티패턴
- 차단된 제품 스트림을 실수로 수집하지 않는다. source profile의 제외 규칙은 의도된 것이다.
- 섹션 일관성이나 인용 검토 가능성을 깨는 청크를 만들지 않는다.
- 프로필 기반 변환을 관련 없는 보조 함수 코드 속에 숨기지 않는다.

## 변경 체크리스트
- 정규화 출력 구조를 바꾼다면 대응 스키마와 chunking/metadata 문서도 함께 갱신한다.
- 소스 범위를 바꾼다면 `source-profiles.yaml`과 하위 검색 정책 가정까지 같이 검토한다.
- 재현 가능성을 지킨다. 같은 source/profile이면 안정적인 manifest 메타데이터가 나와야 한다.
