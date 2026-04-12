// index.html DOM ref와 초기 shell 상태를 모으는 state 모듈이다.
window.createAppShellState = function createAppShellState(deps) {
  const corePacks = Array.isArray(deps && deps.corePacks) ? deps.corePacks : [];
  const defaultPack = corePacks.find((pack) => pack.default) || corePacks[0] || { version: "4.20" };

  const refs = {
    shellEl: document.querySelector(".shell"),
    topbarEl: document.querySelector(".topbar"),
    packStackEl: document.getElementById("pack-stack"),
    versionChipEl: document.getElementById("version-chip"),
    coreVersionPickerEl: document.getElementById("core-version-picker"),
    activePackTitleEl: document.getElementById("active-pack-title"),
    coreSourceSummaryEl: document.getElementById("core-source-summary"),
    topicPlaybookListEl: document.getElementById("topic-playbook-list"),
    topicPlaybookSummaryEl: document.getElementById("topic-playbook-summary"),
    chatPanelEl: document.querySelector(".chat-panel"),
    messagesEl: document.getElementById("messages"),
    composerSamplesEl: document.getElementById("composer-samples"),
    composerEl: document.getElementById("composer"),
    sendBtn: document.getElementById("send-btn"),
    resetBtn: document.getElementById("reset-btn"),
    newSessionBtn: document.getElementById("new-session-btn"),
    statusDotEl: document.getElementById("status-dot"),
    statusTextEl: document.getElementById("status-text"),
    sessionIdEl: document.getElementById("session-id"),
    leftRailToggleBtn: document.getElementById("left-rail-toggle-btn"),
    leftPanelToggleBtn: document.getElementById("left-panel-toggle-btn"),
    sourcePanelToggleBtn: document.getElementById("source-panel-toggle-btn"),
    sourcePanelEdgeBtn: document.getElementById("source-panel-edge-btn"),
    sourceFrameShellEl: document.querySelector(".source-frame-shell"),
    sourceViewerFrameEl: document.getElementById("source-viewer-frame"),
    leftTraceTabButtons: Array.from(document.querySelectorAll(".trace-tab-left")),
    leftRailPages: Array.from(document.querySelectorAll(".left-rail-page")),
    friendlyStepperContainerEl: document.getElementById("friendly-stepper-container"),
  };

  const state = {
    sessionId: crypto.randomUUID(),
    currentMode: "chat",
    currentController: null,
    currentTyper: null,
    layoutMotionTimer: null,
    traceEvents: [],
    latestRetrievalTrace: {},
    generating: false,
    lastQuery: "",
    isComposing: false,
    currentOcpVersion: defaultPack.version,
    packButtons: [],
    leftPanelVisible: true,
    sourcePanelVisible: true,
    activeSourceKey: "",
  };

  const constants = {
    pipelineStageOrder: [
      "normalize_query",
      "rewrite_query",
      "bm25_search",
      "vector_search",
      "fusion",
      "retrieval_total",
      "context_assembly",
      "prompt_build",
      "llm_generate_total",
      "citation_finalize",
      "total",
    ],
    pipelineLabels: {
      normalize_query: "질문 정리",
      rewrite_query: "질문 재구성",
      bm25_search: "키워드 검색",
      vector_search: "벡터 검색",
      fusion: "결과 합치기",
      retrieval_total: "검색 전체",
      context_assembly: "근거 조립",
      prompt_build: "프롬프트 구성",
      llm_generate_total: "LLM 답변 생성",
      citation_finalize: "참조 정리",
      total: "총 응답 시간",
    },
  };

  return { refs, state, constants };
};
