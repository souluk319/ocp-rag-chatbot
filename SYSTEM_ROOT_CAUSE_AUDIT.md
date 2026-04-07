# System Root Cause Audit

## Incident

- Symptom: `.env`에 `LLM_ENDPOINT=http://10.0.1.201:8010/v1`를 적었는데도 실행 중 챗봇은 이전 서버를 계속 쥐고 있었다.
- Why this was severe: 사용자는 설정을 바꿨고, 시스템은 바뀐 척 보였지만 실제 런타임은 다른 값을 쓰고 있었다. 이건 단순 버그가 아니라 `설정 진실원천`, `런타임 상태`, `관측 가능성`이 동시에 깨진 사례다.

## Root Cause Classes

### 1. Config authority is broken

The system does not have one clean source of truth for runtime config.

- [settings.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part1/settings.py)
  `load_settings()`가 `.env`를 읽으면서 동시에 `os.environ`을 전역 변경한다.
- Same file:
  `Settings` dataclass fields are all populated from `os.getenv(...)`, so config resolution is indirectly coupled to mutable process environment.
- Before the fix, `.env` values were losing to stale process env values.
- Even after fixing precedence, this design is still fragile because config parsing and global env mutation are mixed together.

Why this class is dangerous:

- Process가 오래 살아 있으면 `.env`와 실제 런타임 값이 어긋날 수 있다.
- 테스트/스크립트/서버가 서로 환경을 오염시킬 수 있다.
- “설정 파일을 고쳤는데 왜 안 바뀌냐” 류 문제가 재발하기 쉽다.

What should replace it:

- `.env` -> parsed dict -> immutable `Settings`
- `load_settings()` should return settings, not rewrite global process env
- env reference expansion should happen inside parsed values only

### 2. Runtime is snapshotted too early

Large parts of the system capture config once at startup and keep running with that snapshot.

- [run_part4_ui.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/scripts/run_part4_ui.py)
  Builds `settings` and `Part3Answerer` once before serving requests.
- [answerer.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part3/answerer.py)
  `Part3Answerer.from_settings()` builds a retriever and LLM client once.
- [retriever.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part2/retriever.py)
  `Part2Retriever.from_settings()` snapshots BM25/vector runtime from current settings.
- [capture.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_doc_to_book/ingestion/capture.py)
  `DocToBookCaptureService.__init__` stores `self.settings = load_settings(...)`.
- [service.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_doc_to_book/normalization/service.py)
  `DocToBookNormalizeService.__init__` does the same.
- [store.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_doc_to_book/books/store.py)
  `DocToBookDraftStore.__init__` also snapshots settings.

Why this class is dangerous:

- LLM뿐 아니라 Qdrant, embedding, artifacts path, manifest path도 같은 방식으로 stale state가 될 수 있다.
- 지금 LLM만 갱신되게 패치했지만, 같은 계열 문제가 retriever/doc-to-book에도 남아 있다.

What should replace it:

- Long-lived services should receive an immutable config object from a central runtime config provider
- Or request-time operations should fetch a current config snapshot explicitly
- Config-sensitive components should expose a runtime fingerprint and be reconstructable in one place

### 3. Silent fallback hides real failures

The system often “keeps going” by silently degrading, which makes diagnosis much harder.

- [llm.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part3/llm.py)
  Automatically hops between OpenAI-compatible and Ollama-native providers based on model naming and error behavior.
- Same file:
  The provider fallback can make a broken endpoint look like a successful answer path.
- [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part4/server.py):245
  If `viewer_path` has no anchor, it returns the first section.
- [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part4/server.py):253
  If exact anchor recovery fails, it still falls back to the first section.
- [store.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_doc_to_book/books/store.py)
  Legacy draft metadata is auto-hydrated from a fresh planner fallback.
- [pdf.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_doc_to_book/normalization/pdf.py)
  PDF extraction falls back to string-scan recovery.

Why this class is dangerous:

- Wrong source can look like the right source.
- Wrong provider can look like the configured provider.
- Broken normalization can still appear “usable”.
- Observed success can be fake success.

What should replace it:

- Fallbacks must be explicit and observable
- user-visible payloads should carry `resolved_by`, `fallback_used`, `match_exact`
- provider fallback should be opt-in or at least reported in `/api/health` and traces
- source section fallback should be marked as degraded, not silently treated as normal

### 4. Product/domain values are hardcoded deeply

The system still assumes OCP 4.20 in many core paths.

- [settings.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part1/settings.py)
  `docs_index_url`, `book_url_template`, `viewer_path_template`, `QDRANT_COLLECTION=openshift_docs`
- [manifest.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part1/manifest.py)
  Manifest regex and metadata are pinned to `openshift_container_platform/4.20`
- [audit.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part1/audit.py)
  Viewer-path validation assumes `/docs/ocp/4.20/ko/...`
- [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part4/server.py)
  `ChatSession` defaults `ocp_version="4.20"`, core pack payload is OpenShift-specific, viewer parsing hardcodes `/docs/ocp/4.20/ko/`
- [index.html](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part4/static/index.html)
  Branding, active pack title, default version, corpus labels still pinned to OCP 4.20/OCP Play Studio

Why this class is dangerous:

- `Play Book Studio`로 갈수록 core behavior와 content pack behavior가 충돌한다.
- 새 문서군을 넣어도 engine이 아니라 OCP assumption이 먼저 개입한다.

What should replace it:

- `App identity` and `content pack identity` must be separate
- viewer path/schema, pack label, inferred product/version should be data-driven
- OCP should be one pack, not the base system’s hidden default

### 5. Operational observability is too weak

The system does not expose enough runtime truth to prove what it is actually doing.

- [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part4/server.py):1466
  `/api/health` only returns `{ "ok": true }`
- There is no active config fingerprint in health payload
- There is no direct runtime statement of active `llm_endpoint`, `llm_model`, `qdrant_url`, `embedding mode`

Why this class is dangerous:

- A wrong backend can stay hidden until someone manually tests failure modes.
- Debugging becomes guesswork.

What should replace it:

- `/api/health` should return a safe runtime snapshot:
  - active llm endpoint
  - active llm model
  - provider mode
  - qdrant url/collection
  - embedding mode local/remote
  - config fingerprint hash

### 6. Hidden destructive or lossy defaults exist

Some defaults are too risky for a productizing system.

- [qdrant_store.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part1/qdrant_store.py)
  `ensure_collection()` can delete and recreate a collection if configured to do so
- Current `.env` has `QDRANT_RECREATE_COLLECTION=true`
- [server.py](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/ocp_rag_part4/server.py)
  Session state is memory-only via `SessionStore`

Why this class is dangerous:

- Wrong config can wipe vector data during normal pipeline execution.
- Server restart loses conversation state and hides reproducibility of test sessions.

## What Was Fixed In This Incident

Already fixed:

- `.env` now overrides stale process env for loaded keys
- chat requests now refresh LLM runtime settings instead of pinning the first endpoint forever
- tests were added for env override and runtime LLM refresh

This addresses the specific incident but **does not solve the whole class**.

## Immediate Audit Findings To Treat As High Priority

1. Replace global env mutation with explicit immutable config loading
2. Extend runtime refresh logic beyond LLM to all config-sensitive services or rebuild app components cleanly
3. Remove or expose silent provider fallback in `LLMClient`
4. Mark citation/source fallback as degraded instead of silently exact-enough
5. Add real `/api/health` runtime snapshot
6. Turn OCP/version literals into pack config, not core app assumptions
7. Change dangerous operational defaults like `QDRANT_RECREATE_COLLECTION=true`

## Fix Order

### Phase 1: Config integrity

- Refactor `load_settings()` so it does not mutate `os.environ`
- Add a single runtime config loader/provider
- Add health payload with runtime config fingerprint
- Add regression tests for `.env` switching while server is alive

### Phase 2: Fallback integrity

- Audit every fallback and classify it:
  - allowed and explicit
  - allowed but must emit warning
  - forbidden in product mode
- Remove silent LLM provider switching unless explicitly enabled
- Mark source-section fallback with a visible degraded flag

### Phase 3: Pack separation

- Extract OCP-specific values into pack config
- Rename product shell toward `Play Book Studio`
- Keep OCP as selected pack/context, not base identity

### Phase 4: State and reproducibility

- Persist session/debug state
- Add startup/runtime report that captures active config, build, artifacts path, corpus identity

## Working Rule Going Forward

When asked to review or improve the system, the task is not:

- “patch the visible symptom”

The task is:

- identify which systemic class produced the symptom
- find all code paths in that class
- rank by blast radius
- fix the class at its root or document why not

