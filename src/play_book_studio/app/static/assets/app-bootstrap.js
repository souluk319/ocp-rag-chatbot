// 앱 bootstrap과 active runtime wiring만 남긴 최소 helper다.
window.createAppBootstrap = function createAppBootstrap(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const constants = deps.constants;

  function ensureDataControlRoomTrigger() {
    const topbarSideEl = document.querySelector(".topbar-side");
    if (!topbarSideEl) {
      return null;
    }
    return topbarSideEl.querySelector(".data-control-room-launch-btn[href]");
  }

  async function fetchWorkspaceCatalog() {
    const response = await fetch("/api/data-control-room", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`workspace catalog failed: ${response.status}`);
    }
    return response.json();
  }

  function initialize() {
    let updateSessionContextDisplay = () => {};

    const workspaceState = window.createWorkspaceState({
      state: {
        get currentOcpVersion() { return state.currentOcpVersion; },
        set currentOcpVersion(value) { state.currentOcpVersion = value; },
        get packButtons() { return state.packButtons; },
        set packButtons(value) { state.packButtons = value; },
      },
      refs: {
        activePackTitleEl: refs.activePackTitleEl,
        coreSourceSummaryEl: refs.coreSourceSummaryEl,
        coreVersionPickerEl: refs.coreVersionPickerEl,
        packStackEl: refs.packStackEl,
        topicPlaybookListEl: refs.topicPlaybookListEl,
        topicPlaybookSummaryEl: refs.topicPlaybookSummaryEl,
        versionChipEl: refs.versionChipEl,
      },
      constants: {
        corePacks: constants.corePacks,
      },
      callbacks: {
        updateSessionContextDisplay: () => updateSessionContextDisplay(),
      },
    });
    const {
      hydrateFromDataControlRoom,
      initialize: initializeWorkspaceState,
      setCorePack,
    } = workspaceState;

    const panelController = window.createPanelController({
      state: {
        get layoutMotionTimer() { return state.layoutMotionTimer; },
        set layoutMotionTimer(value) { state.layoutMotionTimer = value; },
        get leftPanelVisible() { return state.leftPanelVisible; },
        set leftPanelVisible(value) { state.leftPanelVisible = value; },
        get sourcePanelVisible() { return state.sourcePanelVisible; },
        set sourcePanelVisible(value) { state.sourcePanelVisible = value; },
        get activeSourceKey() { return state.activeSourceKey; },
        set activeSourceKey(value) { state.activeSourceKey = value; },
      },
      refs: {
        leftPanelToggleBtn: refs.leftPanelToggleBtn,
        leftRailToggleBtn: refs.leftRailToggleBtn,
        shellEl: refs.shellEl,
        sourceFrameShellEl: refs.sourceFrameShellEl,
        sourcePanelEdgeBtn: refs.sourcePanelEdgeBtn,
        sourcePanelToggleBtn: refs.sourcePanelToggleBtn,
        sourceViewerFrameEl: refs.sourceViewerFrameEl,
      },
      helpers: {
        isReviewNeeded: helpers.isReviewNeeded,
      },
      callbacks: {
        setSourceFrameLoading: helpers.setSourceFrameLoading,
      },
    });
    const {
      citationMapByIndex,
      inlineCitationLabel,
      openSourcePanel,
      resetSourcePanel,
      setLeftPanelVisible,
      setSourcePanelVisible,
      sourceKeyFor,
      syncActiveSourceTags,
    } = panelController;

    const chatRenderer = window.createChatRenderer({
      refs: {
        messagesEl: refs.messagesEl,
      },
      helpers: {
        citationMapByIndex,
        inlineCitationLabel,
        openSourcePanel,
        sourceKeyFor,
      },
    });
    const {
      renderAssistantBody,
      renderMessageBody,
    } = chatRenderer;

    const diagnosticsRenderer = window.createDiagnosticsRenderer({
      state: {
        get currentMode() { return state.currentMode; },
        get currentOcpVersion() { return state.currentOcpVersion; },
        get generating() { return state.generating; },
        get latestRetrievalTrace() { return state.latestRetrievalTrace; },
        set latestRetrievalTrace(value) { state.latestRetrievalTrace = value; },
        get traceEvents() { return state.traceEvents; },
        set traceEvents(value) { state.traceEvents = value; },
      },
      refs: {
        friendlyStepperContainerEl: refs.friendlyStepperContainerEl,
        leftRailPages: refs.leftRailPages,
        leftTraceTabButtons: refs.leftTraceTabButtons,
        statusDotEl: refs.statusDotEl,
        statusTextEl: refs.statusTextEl,
      },
      helpers: {
        formatDuration: helpers.formatDuration,
        pipelineLabels: constants.pipelineLabels,
        pipelineStageOrder: constants.pipelineStageOrder,
      },
    });
    const {
      appendTraceEvent,
      humanizePipelineKey,
      renderPipelineLive,
      resetPipelineTrace,
      setStatus,
      summarizeTraceMeta,
      updateSessionContextDisplay: nextUpdateSessionContextDisplay,
      updateSidePanel,
    } = diagnosticsRenderer;
    updateSessionContextDisplay = nextUpdateSessionContextDisplay;

    const chatSession = window.createChatSession({
      state: {
        get currentController() { return state.currentController; },
        set currentController(value) { state.currentController = value; },
        get currentMode() { return state.currentMode; },
        get currentOcpVersion() { return state.currentOcpVersion; },
        get currentTyper() { return state.currentTyper; },
        set currentTyper(value) { state.currentTyper = value; },
        get generating() { return state.generating; },
        get isComposing() { return state.isComposing; },
        set isComposing(value) { state.isComposing = value; },
        get lastQuery() { return state.lastQuery; },
        set lastQuery(value) { state.lastQuery = value; },
        get sessionId() { return state.sessionId; },
        set sessionId(value) { state.sessionId = value; },
      },
      refs: {
        chatPanelEl: refs.chatPanelEl,
        composerSamplesEl: refs.composerSamplesEl,
        composerEl: refs.composerEl,
        messagesEl: refs.messagesEl,
        newSessionBtn: refs.newSessionBtn,
        resetBtn: refs.resetBtn,
        sendBtn: refs.sendBtn,
        sessionIdEl: refs.sessionIdEl,
      },
      constants: {
        emptyStateSamples: constants.emptyStateSamples,
      },
      helpers: {
        appendTraceEvent,
        formatDuration: helpers.formatDuration,
        humanizePipelineKey,
        openSourcePanel,
        renderAssistantBody,
        renderMessageBody,
        renderPipelineLive,
        resetPipelineTrace,
        resetSourcePanel,
        resizeComposer: helpers.resizeComposer,
        setGenerating: helpers.setGenerating,
        setStatus,
        sourceKeyFor,
        summarizeTraceMeta,
        syncActiveSourceTags,
        syncChatPanelState: helpers.syncChatPanelState,
        updateSessionContextDisplay,
        updateSidePanel,
      },
    });
    const {
      bindEvents: bindChatSessionEvents,
      initialize: initializeChatSession,
    } = chatSession;

    initializeWorkspaceState();
    bindChatSessionEvents();
    ensureDataControlRoomTrigger();
    fetchWorkspaceCatalog()
      .then((payload) => {
        hydrateFromDataControlRoom(payload);
      })
      .catch(() => {
        hydrateFromDataControlRoom({ topic_playbooks: { books: [] } });
      });
    window.bindAppBootstrapEvents({
      state,
      refs,
      helpers,
      callbacks: {
        initializeChatSession,
        resetPipelineTrace,
        resetSourcePanel,
        setCorePack,
        setLeftPanelVisible,
        setSourcePanelVisible,
      },
    });
  }

  return { initialize };
};
