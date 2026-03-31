# Stage 2 완료 보고서

## 단계명

런타임 경로 진위 검증

## 목표

`bridge -> OpenDocuments -> gateway` 경로가 실제로 **회사 LLM + `BAAI/bge-m3` + active Stage 11 index** 를 사용하고 있는지 증명하는 것이다.

이 단계는 retrieval 품질을 평가하지 않는다.  
오직 런타임 경로가 **의도한 모델/브리지/플러그인/게이트웨이 체인**을 타는지만 본다.

## 적용 범위

- [opendocuments_openai_bridge.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/app/opendocuments_openai_bridge.py)
- [run_activation_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_activation_smoke.py)
- [run_live_runtime_smoke.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/run_live_runtime_smoke.py)
- [start_runtime_stack.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/start_runtime_stack.py)
- [run_opendocuments_stage6.mjs](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/run_opendocuments_stage6.mjs)
- [check_stage02_runtime_path.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage02_runtime_path.py)

## 6인 역할

- `Creative-A`: live smoke 시나리오가 런타임 진위 검증에 맞는지 검토
- `Creative-B`: false positive 위험과 우회 경로 탐지 포인트 검토
- `Expert-A`: bridge ready, embedding model/dimension, upstream chat path 기술 검토
- `Expert-B`: runner가 stub/ollama를 우회하고 stale workspace 재사용을 막는지 검토
- `Inspector-A`: Stage 2 필수 증거 필드와 로그 체크리스트 정리
- `Inspector-B`: Stage 2 완료 경계와 남은 리스크 정리

## 수행 내용

- bridge `/ready` 경로를 추가하고 런타임이 embedder preload까지 통과하는지 확인하도록 보강했다.
- `start_runtime_stack.py` 와 `run_live_runtime_smoke.py` 가 `/ready` 결과를 함께 기록하도록 맞췄다.
- `run_activation_smoke.py` 도 bridge `/ready` 통과 후에만 retrieval smoke를 시작하도록 보강했다.
- `run_opendocuments_stage6.mjs` 에 OpenAI override, retrieval-only 모드, data-dir reset을 추가해 stub/old vector 재사용 가능성을 낮췄다.
- Stage 2 전용 진위 검증기 [check_stage02_runtime_path.py](/C:/Users/soulu/cywell/ocp-rag-chatbot/deployment/check_stage02_runtime_path.py) 를 추가했다.
- Stage 2 전용 검증기는 live smoke를 **별도 포트**로 실행해서 기존 프로세스와 섞이지 않게 했다.

## 테스트

### 문법 검증

- `python -m py_compile app\opendocuments_openai_bridge.py deployment\run_activation_smoke.py deployment\run_live_runtime_smoke.py deployment\start_runtime_stack.py deployment\check_stage02_runtime_path.py`

### Stage 2 전용 진위 검증

- `python deployment\check_stage02_runtime_path.py --index s15c-core --output data\manifests\generated\stage02-runtime-path-authenticity-report.json`

생성 리포트:

- [stage02-runtime-path-authenticity-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage02-runtime-path-authenticity-report.json)
- [stage02-live-runtime-smoke.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage02-live-runtime-smoke.json)

## 검증 결과

Stage 2는 완료로 판정한다.

핵심 pass 조건:

- `bridge_health_ok = true`
- `bridge_ready_ok = true`
- `runtime_mode_company_only = true`
- `local_chat_fallback_disabled = true`
- `bridge_ready_model_matches_config = true`
- `bridge_ready_dimensions_match_config = true`
- `bridge_ready_dimensions_match_active_index = true`
- `bridge_models_include_configured_chat_model = true`
- `opendocuments_openai_plugin_loaded = true`
- `opendocuments_no_embed_probe_failure = true`
- `opendocuments_no_ollama_reference = true`
- `bridge_embedding_requests_seen = true`
- `bridge_chat_requests_seen = true`
- `bridge_evidence_ok = true`
- `bridge_evidence_runtime_mode_company_only = true`
- `bridge_evidence_embedding_requests_seen = true`
- `bridge_evidence_chat_requests_seen = true`
- `bridge_evidence_upstream_chat_success_seen = true`
- `bridge_evidence_fallback_chat_absent = true`
- `bridge_evidence_last_chat_target_path_valid = true`
- `bridge_evidence_last_embedding_model_matches_config = true`
- `bridge_evidence_last_embedding_dimensions_match_active_index = true`
- `gateway_health_ok = true`
- `gateway_port_conflict_absent = true`
- `gateway_stream_requests_seen = true`
- `smoke_turns_executed = true`

관찰 사항:

- nested live smoke 자체는 retrieval 품질 기준으로는 여전히 실패할 수 있다.
- 하지만 Stage 2는 retrieval 품질을 묻는 단계가 아니므로, 이 실패 때문에 Stage 2를 fail 처리하지 않는다.
- Stage 2의 결론은 **“telemetry 기준으로도 경로는 진짜다. 품질은 다음 단계에서 본다.”** 이다.

## 정리 메모

- Stage 2는 **경로 진위**만 닫았다.
- widened corpus retrieval 품질, source alignment, citation 정확도, multiturn 품질은 다음 단계에서 다룬다.

## 다음 단계

다음 활성 단계는 **3단계. widened corpus retrieval 실패 원인 해부**다.
