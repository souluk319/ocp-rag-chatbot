# Structure Refactor Backlog

이 문서는 현재 기준 `Play Book Studio`에서 남아 있는 구조개편 후보를 한 곳에 모아 두는 문서다.

목적은 세 가지다.

1. 큰 파일과 책임 덩어리를 숫자로 본다.
2. “왜 다음에 이걸 뜯는가”를 감이 아니라 근거로 남긴다.
3. 구조개편 순서를 고정해서, 버그 수정 중에도 기준점을 잃지 않게 한다.

## 1. 현재 남은 큰 덩어리

2026-04-08 기준 대형 파일은 아래 순서다.

| 우선순위 | 파일 | 현재 줄 수 | 왜 큰 문제인가 | 다음 안전한 분리 단위 |
|---|---|---:|---|---|
| 1 | [index.html](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/index.html) | 3464 | 채팅/자료 렌더링 핫스팟은 빠졌지만 최종 shell과 DOM helper가 아직 크다 | DOM ref polish, final startup trim |
| 2 | [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/server.py) | 797 | 많이 줄였지만 route wiring, HTTP 처리, 일부 runtime glue가 아직 남아 있다 | route table, response writer, runtime refresh |
| 3 | [answerer.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/answerer.py) | 547 | 핵심 spine 역할은 맞지만 pipeline orchestration 외 보조 규칙이 아직 있다 | deterministic answer path, trace emission helper |
| 4 | [data_quality.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/data_quality.py) | 241 | 제목/본문/경로 품질 리포트 조립이 한 파일에 모여 있어 다음 audit 튜닝 지점이 된다 | title audit, path audit, text audit |
| 5 | [pdf_cleanup.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_cleanup.py) | 221 | PDF page/docling cleanup 규칙이 한 파일에 모여 있어 다음 PDF 품질 튜닝 지점이 된다 | page cleanup, docling cleanup |
| 6 | [book_adjustment_discovery.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/book_adjustment_discovery.py) | 196 | 개념/문서 탐색 조정 규칙이 많아 다음 retrieval 튜닝 때 다시 커질 수 있다 | intro/locator, platform concept |
| 7 | [book_adjustment_operations.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/book_adjustment_operations.py) | 188 | 운영/트러블슈팅 규칙이 한 덩어리라 증상별 조정이 늘수록 읽기 비용이 커진다 | node/project, pod/rbac |
| 8 | [approval_report.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/approval_report.py) | 174 | 승인 리포트와 runtime manifest 조립이 한 파일에 모여 있다 | report summary, manifest assembly |
| 9 | [query_terms_operations.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query_terms_operations.py) | 158 | 운영형 질의 확장 용어가 모여 있어 alias 보강이 계속 누적될 수 있다 | rbac/project, node/pod |
| 10 | [query_terms_core.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query_terms_core.py) | 89 | 공통 개념/문서 탐색 용어가 쌓이면 이후 intro/locator tuning이 다시 어려워질 수 있다 | platform aliases, locator aliases |

## 2. 프론트 현재 상태

프론트는 이미 아래 모듈까지 분리됐다.

- [panel-controller.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/panel-controller.js)
- [app-shell-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-shell-state.js)
- [app-bootstrap.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-bootstrap.js)
- [shell-helpers.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/shell-helpers.js)
- [message-shells.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/message-shells.js)
- [chat-renderer.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/chat-renderer.js)
- [chat-session.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/chat-session.js)
- [workspace-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/workspace-state.js)
- [intake-renderer.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/intake-renderer.js)
- [diagnostics-renderer.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/diagnostics-renderer.js)
- [source-workflows.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/source-workflows.js)
- [intake-actions.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/intake-actions.js)

즉 지금 `index.html`에 남은 진짜 덩어리는 “렌더링 로직”보다 “최상위 shell/DOM helper” 쪽이다.
앱 shell 기본 DOM ref와 mutable state는 [app-shell-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-shell-state.js)에서 보고, bootstrap과 module wiring은 [app-bootstrap.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-bootstrap.js)에서 본다. 공통 DOM helper와 shell 상태 동기화는 [shell-helpers.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/shell-helpers.js)에서 본다. empty state, pending panel, citation chip, 메시지 wrapper 조립은 [message-shells.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/message-shells.js)에서 본다. 채팅 송수신/스트리밍 응답/세션 리셋은 [chat-session.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/chat-session.js), 팩 선택/자료 선택 집합/보관함 렌더링은 [workspace-state.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/workspace-state.js)에서 본다.

그래서 프론트 다음 후보는 아래 둘이다.

1. `message shell`
- 최상위 message/card 조립
- 공통 DOM helper
- 빈 상태/알림 shell

2. `DOM ref collection`
- 긴 ref 수집 구간
- bootstrap deps packing
- 상수/헬퍼 전달 정리

## 3. 백엔드 현재 상태

백엔드는 이미 아래 축이 밖으로 빠졌다.

- [chat_debug.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/chat_debug.py)
- [intake_api.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/intake_api.py)
- [source_books.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/source_books.py)
- [session_flow.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/session_flow.py)
- [answer_text.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/answer_text.py)
- [citations.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/answering/citations.py)

즉 다음부터는 `audit.py` 자체를 더 쪼개는 일은 끝났고, 이제 남은 ingestion/retrieval 하위 파일을 정리하는 단계다.

## 4. 추천 순서

다음 구조개편은 이 순서를 추천한다.

1. [index.html](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/index.html) shell/helper
2. [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/server.py) runtime glue
3. [data_quality.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/data_quality.py)
4. [pdf_cleanup.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_cleanup.py)
5. [query_terms_operations.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/retrieval/query_terms_operations.py)
6. 문서/가이드의 현재 구조 기준선 유지

이 순서인 이유:

- 현재 프론트는 큰 핫스팟이 잘게 나뉘었고, bootstrap 자체는 [app-bootstrap.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-bootstrap.js)로 빠졌다.
- ingestion audit는 [audit.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/audit.py) facade, [audit_rules.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/audit_rules.py), [data_quality.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/data_quality.py), [approval_report.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/approval_report.py)로 나뉘었다.
- intake PDF 정규화는 [pdf_helpers.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_helpers.py) facade, [pdf_outline.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_outline.py), [pdf_cleanup.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/intake/normalization/pdf_cleanup.py)로 나뉘었다.
- retrieval은 façade 분리가 끝났고, `book_adjustments.py`, `query_terms.py` 모두 façade가 됐다. 다음부턴 남은 cluster 파일을 필요할 때 더 쪼개는 단계다.
- 프론트는 이제 마지막 shell/helper 정리만 남은 상태다.

## 5. `src` 구조개편 순서표

`src/play_book_studio`를 최종 단일 패키지로 굳히기 위한 순서표는 아래처럼 잡는다.

| 단계 | 목표 | 끝나야 하는 조건 | 메모 |
|---|---|---|---|
| 1 | retrieval query 축 정리 | `query.py`는 facade로 남고, `intents.py` / `rewrite.py`로 실제 구현이 갈라짐 | ambiguity/decompose 분리 완료, facade/intents/rewrite 분리 완료 |
| 2 | retrieval runtime 축 정리 | `retriever.py`에서 fusion/scoring 본체와 runtime glue가 분리됨 | scoring 분리 완료 |
| 3 | intake normalization 축 정리 | `service.py`는 service로, `builders.py`는 canonical assembly로, `pdf_rows.py`는 row assembly로, `pdf_helpers.py`는 outline/cleanup helper로 나뉨 | service/builders 분리 완료, pdf_rows 2차 분리 완료 |
| 4 | app bootstrap/state 정리 | bootstrap/wiring은 [app-bootstrap.js](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/static/assets/app-bootstrap.js)로 빠지고, `index.html`는 shell/helper 위주로 줄어듦 | bootstrap 분리 완료 |
| 5 | ingestion audit 정리 | `audit.py`는 facade, `audit_rules.py` / `data_quality.py` / `approval_report.py`로 역할이 분리됨 | 완료 |
| 6 | intake shim/legacy 참조 전수 점검 | 구 intake 경로 의존이 더 이상 남지 않음 | 완료 |
| 7 | 구 shim 제거 | `src/play_book_studio/intake`만 남고, `src` 하위 패키지가 사실상 하나로 정리됨 | 완료 |
| 8 | 문서 최종 동기화 | README, CODE_READING_GUIDE, FILE_ROLE_GUIDE, RESTRUCTURE_DRAFT, VENDOR_NOTES가 새 구조만 설명 | 완료 |

핵심은 이거다.

- `src` 두 갈래로 보이던 이행기는 끝났다.
- 이제 `src` 하위의 주 패키지는 `play_book_studio` 하나다.
- 남은 일은 shim 제거가 아니라, 새 구조 기준 문서 유지와 잔여 대형 파일 정리다.

## 6. 하지 말아야 할 것

- 큰 파일 여러 개를 한 턴에 동시에 뜯지 않기
- 이름 변경과 책임 이동과 동작 수정까지 한 번에 섞지 않기
- 구조개편 중 회귀 테스트 범위를 줄이지 않기

## 7. 한 줄 결론

현재 구조개편은 “아직 시작도 못 한 상태”가 아니라,
`server/app/frontend hot spot`은 이미 많이 줄였고,
이제 남은 제일 큰 산은 `retrieval/query`, `intake normalization`, 그리고 최종 문서 동기화다.
