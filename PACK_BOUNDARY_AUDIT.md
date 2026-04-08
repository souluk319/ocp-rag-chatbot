# Pack Boundary Audit

이 문서는 `Play Book Studio`라는 앱 정체성과 현재 선택된 OCP 코퍼스 정체성을 어디서 나눴는지 기록한다.

## 현재 기준선

- 앱 정체성: `Play Book Studio`
- 현재 운영 범위: `OpenShift` 코퍼스만 사용
- 현재 기본 pack: `OpenShift 4.20`
- 현재 source of truth: `docs.redhat.com`의 published Korean `html-single`

즉 지금은 범용 NotebookLM이 아니라 `OCP Playbook Studio`가 맞다.  
다만 OCP literal이 core runtime 곳곳에 흩어지지 않도록, pack identity는 한 군데로 몰아두는 상태를 목표로 한다.

## 경계가 생긴 곳

현재 pack 정체성의 기준 파일은 아래다.

- [packs.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/packs.py)

여기서 관리하는 값:

- `pack_id`
- `pack_label`
- `product_label`
- `version`
- `language`
- `source_collection`
- `docs index / book url / viewer path template`
- `runtime manifest 파일명`
- `qdrant collection 기본값`

현재 core runtime은 아래 경로를 통해 pack 정보를 받는다.

- [settings.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/settings.py)
- [presenters.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/presenters.py)
- [sessions.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/sessions.py)
- [viewers.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/viewers.py)
- [manifest.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/manifest.py)
- [audit.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/audit.py)

## 지금도 OCP-specific 인 곳

이건 기술 부채라기보다 현재 제품 범위상 의도된 부분이다.

- [query.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query.py)
  OCP 용어, 버전, operator, MCO, update locator 같은 질문 해석 규칙
- [router.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/router.py)
  OCP 범위 밖 질문을 막는 문구
- [index.html](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/index.html)
  OCP 예시 질문, OCP pack 선택 UI
- [app-config.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-config.js)
  현재 core pack 목록이 OCP 버전 선택기 기준
- [play_book_studio/intake](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake)
  업로드 문서 intake는 제품 네임스페이스 아래로 흡수되기 시작했지만, draft/plan 기본 pack label은 아직 OCP 컨텍스트를 전제

## 나중에 범용화할 때 뜯을 순서

1. `packs.py`에 OCP 외 pack 타입 추가
2. `app-config.js` 또는 server bootstrap payload를 pack registry 기반으로 교체
3. `retrieval/query.py`의 OCP 전용 규칙을 product-specific query policy로 분리
4. `router.py`의 no-answer / unsupported-product 문구를 pack-aware copy로 교체
5. `play_book_studio/intake`의 plan 기본값을 OCP 고정 대신 active pack 기반으로 전환

## 지금 단계의 결론

지금은 OCP-only로 가는 게 맞다.  
다만 `Play Book Studio`와 `OpenShift 4.20 core pack`을 같은 개념으로 취급하지 않도록, core runtime 기준의 pack identity는 `packs.py`와 `Settings.active_pack`으로 몰아둔 상태가 현재 기준선이다.
