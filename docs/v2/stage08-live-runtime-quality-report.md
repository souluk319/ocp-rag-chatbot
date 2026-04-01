# 2026-03-31 Stage 8 Report

## 목표

Stage 8의 목표는 widened corpus 활성 인덱스 기준으로 실제 HTTP serving path 에서 아래 조건이 모두 유지되는지 재검증하는 것이다.

- 한국어 질문
- 스트리밍 응답
- 세션 연속성
- follow-up rewrite
- citation 존재
- citation click-through
- HTML viewer 경로

이 단계는 retrieval 품질을 새로 승인하는 단계가 아니다. retrieval-quality authority 는 계속 Stage 5 / Stage 6 에 둔다.

## 사용한 6인 역할

- `Creative-A`: 운영자 질문 문구 현실성 점검
- `Creative-B`: citation 클릭 시 사용자 신뢰 관점 점검
- `Expert-A`: bridge evidence 기반 진짜 serving path 게이트 제안
- `Expert-B`: 세션 / follow-up continuity 게이트 점검
- `Inspector-A`: strict reviewer 가 기대하는 evidence 정리
- `Inspector-B`: Stage 8 pass/fail framing 정리

## 이번 단계에서 보강한 것

1. live smoke 질문을 더 운영자다운 한국어 표현으로 수정했다.
   - `CNF 드라이버 업데이트` -> `OpenShift CNF 클러스터 업데이트`
2. bridge evidence 를 pass 조건으로 올렸다.
   - embedding request 발생
   - chat request 발생
   - upstream chat success 존재
   - fallback chat 없음
   - last chat target path 일치
   - embedding model / dimensions 일치
3. citation viewer 검증을 강화했다.
   - 문서가 열리는지만 보지 않고
   - citation 의 `section_title` 이 HTML 본문에 실제로 존재하는지 확인한다.
4. 세션 continuity 검증을 강화했다.
   - cookie presence 뿐 아니라
   - 동일 cookie value 유지까지 확인한다.

## 핵심 증거

- Stage 8 live report: [stage08-live-runtime-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage08-live-runtime-report.json)
- smoke input: [live_runtime_smoke_cases.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/live_runtime_smoke_cases.json)
- live runner: [run_live_runtime_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_live_runtime_smoke.py)

## 결과

- `overall_pass = true`
- `first_turn_pass = true`
- `second_turn_pass = true`
- `same_conversation_id = true`
- `same_session_cookie_value = true`
- `follow_up_rewrite_contains_last_document = true`
- `viewer_click_through_pass = true`
- `bridge_embedding_requests_present = true`
- `bridge_chat_requests_present = true`
- `bridge_upstream_chat_success_present = true`
- `bridge_no_fallback_chat = true`
- `bridge_last_chat_target_ok = true`
- `bridge_embedding_model_match = true`
- `bridge_embedding_dimensions_match = true`

bridge telemetry 요약:

- runtime mode: `company-chat-plus-local-embeddings`
- embedding model: `BAAI/bge-m3`
- embedding dimensions: `1024`
- embedding requests: `8`
- chat requests: `2`
- upstream chat success: `2`
- fallback chat: `0`

viewer 검증 요약:

- 두 턴 모두 top sources 에 대해 HTML 문서 열림 확인
- `section_title_present = true`
- 즉 citation 이 단순히 파일만 여는 것이 아니라, 인용된 섹션 제목과 실제 HTML 본문이 맞는다

## 해석

Stage 8은 `pass` 이다.

이 pass 는 다음 의미로 제한된다.

- widened corpus live serving path 가 실제로 동작한다
- bridge -> OpenDocuments -> gateway -> viewer 경로가 유지된다
- 한국어 질문, 스트리밍, 세션 연속성, citation click-through 가 유지된다

이 pass 는 다음을 의미하지 않는다.

- retrieval 품질의 신규 승인
- Stage 5 / Stage 6 결과 대체

즉 Stage 8은 serving-path integrity 와 citation-viewer behavior 의 pass 이고, retrieval-quality authority 는 계속 Stage 5 / Stage 6 이다.

## 결론

이제 widened corpus 기준으로도 실제 사용자 관점의 최소 경로는 닫혔다.

- 질문 가능
- 한국어 응답 가능
- 스트리밍 가능
- follow-up 유지
- citation 표기
- citation click-through
- section-level viewer 확인

다음 단계는 이 serving path 를 유지한 채 source profile 운영 전환 또는 corpus / release policy 보강으로 넘어가면 된다.
