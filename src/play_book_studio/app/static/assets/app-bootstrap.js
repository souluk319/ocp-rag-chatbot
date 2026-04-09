// 앱 bootstrap, 모듈 wiring, 초기 startup 순서를 담당하는 프론트 helper다.
window.createAppBootstrap = function createAppBootstrap(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const constants = deps.constants;

  function initialize() {
    let updateSessionContextDisplay = () => {};
    let openLibraryAsset = () => Promise.resolve();
    let openLibraryTrace = () => Promise.resolve();
    let openDocToBookDraft = () => Promise.resolve();
    let setIngestSelectedFile = () => {};
    let syncIngestUploadHint = () => {};

    const workspaceState = window.createWorkspaceState({
      state: {
        get currentOcpVersion() { return state.currentOcpVersion; },
        set currentOcpVersion(value) { state.currentOcpVersion = value; },
        get activeIngestDraftId() { return state.activeIngestDraftId; },
        set activeIngestDraftId(value) { state.activeIngestDraftId = value; },
        get activeLibraryDraftId() { return state.activeLibraryDraftId; },
        set activeLibraryDraftId(value) { state.activeLibraryDraftId = value; },
        get docToBookDraftCache() { return state.docToBookDraftCache; },
        set docToBookDraftCache(value) { state.docToBookDraftCache = value; },
        get knownSelectableDraftIds() { return state.knownSelectableDraftIds; },
        set knownSelectableDraftIds(value) { state.knownSelectableDraftIds = value; },
        get packButtons() { return state.packButtons; },
        set packButtons(value) { state.packButtons = value; },
        get selectedDraftIds() { return state.selectedDraftIds; },
      },
      refs: {
        activePackTitleEl: refs.activePackTitleEl,
        coreSourceSummaryEl: refs.coreSourceSummaryEl,
        coreVersionPickerEl: refs.coreVersionPickerEl,
        ingestDraftListEl: refs.ingestDraftListEl,
        libraryListEl: refs.libraryListEl,
        librarySummaryEl: refs.librarySummaryEl,
        packStackEl: refs.packStackEl,
        railLibraryListEl: refs.railLibraryListEl,
        railUploadStatusEl: refs.railUploadStatusEl,
        selectedSourceCountEl: refs.selectedSourceCountEl,
        studyPages: refs.studyPages,
        studyTabButtons: refs.studyTabButtons,
        versionChipEl: refs.versionChipEl,
      },
      constants: {
        corePacks: constants.corePacks,
      },
      helpers: {
        formatInferredScope: helpers.formatInferredScope,
        humanizeSourceCollection: helpers.humanizeSourceCollection,
        isReviewNeeded: helpers.isReviewNeeded,
        qualityStatusLabel: helpers.qualityStatusLabel,
        qualitySummaryText: helpers.qualitySummaryText,
      },
      callbacks: {
        openDocToBookDraft: (draftId) => openDocToBookDraft(draftId),
        openLibraryAsset: (draftId) => openLibraryAsset(draftId),
        openLibraryTrace: (draftId) => openLibraryTrace(draftId),
        updateSessionContextDisplay: () => updateSessionContextDisplay(),
      },
    });
    const {
      initialize: initializeWorkspaceState,
      registerReadyDraft,
      renderDocToBookDrafts,
      selectedDraftIdList,
      setCorePack,
      setRailUploadStatus,
      setStudyTab,
      setUploadedDraftSelected,
      syncSelectableDraftIds,
      syncSourceSelectionSummary,
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
        sourceNoteEl: refs.sourceNoteEl,
        sourceOpenDocEl: refs.sourceOpenDocEl,
        sourceOpenOriginEl: refs.sourceOpenOriginEl,
        sourceOutlineEl: refs.sourceOutlineEl,
        sourcePanelEdgeBtn: refs.sourcePanelEdgeBtn,
        sourcePanelToggleBtn: refs.sourcePanelToggleBtn,
        sourcePathEl: refs.sourcePathEl,
        sourceSummaryStripEl: refs.sourceSummaryStripEl,
        sourceTitleEl: refs.sourceTitleEl,
        sourceViewerFrameEl: refs.sourceViewerFrameEl,
      },
      helpers: {
        createSummaryChip: helpers.createSummaryChip,
        formatInferredScope: helpers.formatInferredScope,
        humanizeDraftValue: helpers.humanizeDraftValue,
        humanizeSourceCollection: helpers.humanizeSourceCollection,
        isReviewNeeded: helpers.isReviewNeeded,
        qualityStatusLabel: helpers.qualityStatusLabel,
        qualitySummaryText: helpers.qualitySummaryText,
      },
      callbacks: {
        setSourceFrameLoading: helpers.setSourceFrameLoading,
        setStudyTab,
      },
    });
    const {
      citationMapByIndex,
      fetchSourceBook,
      fetchSourceMeta,
      inlineCitationLabel,
      openSourcePanel,
      renderSourceBook,
      resetSourcePanel,
      setLeftPanelVisible,
      setSourceEmptyState,
      setSourceLink,
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
      normalizeAssistantAnswer,
      renderAssistantBody,
      renderMarkdownInto,
      renderMessageBody,
    } = chatRenderer;

    const intakeRenderer = window.createIntakeRenderer({
      state: {
        get activeIngestDraftId() { return state.activeIngestDraftId; },
        set activeIngestDraftId(value) { state.activeIngestDraftId = value; },
        get activeIngestDraft() { return state.activeIngestDraft; },
        set activeIngestDraft(value) { state.activeIngestDraft = value; },
        get activeLibraryDraftId() { return state.activeLibraryDraftId; },
        set activeLibraryDraftId(value) { state.activeLibraryDraftId = value; },
      },
      refs: {
        ingestCaptureMetaEl: refs.ingestCaptureMetaEl,
        ingestFilePillEl: refs.ingestFilePillEl,
        ingestOpenCaptureBtn: refs.ingestOpenCaptureBtn,
        ingestPlanOutputEl: refs.ingestPlanOutputEl,
        ingestSourceTypeEl: refs.ingestSourceTypeEl,
        ingestStatusEl: refs.ingestStatusEl,
        ingestTitleEl: refs.ingestTitleEl,
        ingestUriEl: refs.ingestUriEl,
        libraryDetailEl: refs.libraryDetailEl,
      },
      helpers: {
        formatByteSize: helpers.formatByteSize,
        formatInferredScope: helpers.formatInferredScope,
        humanizeDraftValue: helpers.humanizeDraftValue,
        humanizeSourceCollection: helpers.humanizeSourceCollection,
        isReviewNeeded: helpers.isReviewNeeded,
        qualityStatusLabel: helpers.qualityStatusLabel,
        qualitySummaryText: helpers.qualitySummaryText,
        setIngestSelectedFile: (...args) => setIngestSelectedFile(...args),
        syncIngestUploadHint: (...args) => syncIngestUploadHint(...args),
      },
      callbacks: {
        openLibraryAsset: (draftId) => openLibraryAsset(draftId),
      },
    });
    const {
      populateDocToBookForm,
      renderDocToBookPreview,
      renderIngestCaptureMeta,
      renderLibraryDetail,
      resetLibraryDetail,
      setIngestStatus,
    } = intakeRenderer;
    if (helpers.bindIngestStatus) {
      helpers.bindIngestStatus(setIngestStatus);
    }

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
        statusDotEl: refs.statusDotEl,
        statusTextEl: refs.statusTextEl,
      },
      helpers: {
        formatDuration: helpers.formatDuration,
        pipelineLabels: constants.pipelineLabels,
        pipelineStageOrder: constants.pipelineStageOrder,
        selectedDraftIdList,
      },
    });
    const {
      appendTraceEvent,
      humanizePipelineKey,
      renderPipelineLive,
      renderPipelineSummary,
      resetPipelineTrace,
      setStatus,
      summarizeTraceMeta,
      updateSessionContextDisplay: nextUpdateSessionContextDisplay,
      updateSidePanel,
    } = diagnosticsRenderer;
    updateSessionContextDisplay = nextUpdateSessionContextDisplay;

    const intakeActions = window.createIntakeActions({
      state: {
        get activeIngestDraftId() { return state.activeIngestDraftId; },
        get activeIngestUpload() { return state.activeIngestUpload; },
        set activeIngestUpload(value) { state.activeIngestUpload = value; },
      },
      refs: {
        ingestCaptureBtn: refs.ingestCaptureBtn,
        ingestDropDetailEl: refs.ingestDropDetailEl,
        ingestFileBtn: refs.ingestFileBtn,
        ingestFileInputEl: refs.ingestFileInputEl,
        ingestFilePillEl: refs.ingestFilePillEl,
        ingestNormalizeBtn: refs.ingestNormalizeBtn,
        ingestPlanBtn: refs.ingestPlanBtn,
        ingestSaveBtn: refs.ingestSaveBtn,
        ingestSourceTypeEl: refs.ingestSourceTypeEl,
        ingestTitleEl: refs.ingestTitleEl,
        ingestUriEl: refs.ingestUriEl,
      },
      helpers: {
        formatByteSize: helpers.formatByteSize,
        inferSourceTypeFromFile: helpers.inferSourceTypeFromFile,
        setIngestBusy: helpers.setIngestBusy,
        setRailUploadStatus,
      },
      callbacks: {
        onDraftReady: (normalized) => {
          registerReadyDraft(normalized.draft_id);
        },
        populateDocToBookForm,
        renderDocToBookDrafts,
        renderDocToBookPreview,
        renderIngestCaptureMeta,
        setIngestStatus,
        setSourcePanelVisible,
        setStudyTab,
      },
    });
    const {
      captureDocToBookDraft,
      createDocToBookDraft,
      fetchDocToBookBook,
      handleIngestFileSelection,
      loadDocToBookDrafts,
      normalizeDocToBookDraft,
      openDocToBookDraft: nextOpenDocToBookDraft,
      previewDocToBookPlan,
      setIngestSelectedFile: nextSetIngestSelectedFile,
      syncIngestUploadHint: nextSyncIngestUploadHint,
    } = intakeActions;
    openDocToBookDraft = nextOpenDocToBookDraft;
    setIngestSelectedFile = nextSetIngestSelectedFile;
    syncIngestUploadHint = nextSyncIngestUploadHint;

    const sourceWorkflows = window.createSourceWorkflows({
      state: {
        get activeIngestDraft() { return state.activeIngestDraft; },
      },
      refs: {
        sourceFrameShellEl: refs.sourceFrameShellEl,
        sourceNoteEl: refs.sourceNoteEl,
        sourceOpenDocEl: refs.sourceOpenDocEl,
        sourceOpenOriginEl: refs.sourceOpenOriginEl,
        sourceOutlineEl: refs.sourceOutlineEl,
        sourcePathEl: refs.sourcePathEl,
        sourceSummaryStripEl: refs.sourceSummaryStripEl,
        sourceTitleEl: refs.sourceTitleEl,
        sourceViewerFrameEl: refs.sourceViewerFrameEl,
      },
      helpers: {
        createSummaryChip: helpers.createSummaryChip,
        formatByteSize: helpers.formatByteSize,
        formatInferredScope: helpers.formatInferredScope,
        humanizeDraftValue: helpers.humanizeDraftValue,
        humanizeSourceCollection: helpers.humanizeSourceCollection,
        isReviewNeeded: helpers.isReviewNeeded,
        qualityStatusLabel: helpers.qualityStatusLabel,
        qualitySummaryText: helpers.qualitySummaryText,
      },
      callbacks: {
        fetchDocToBookBook,
        loadDocToBookDrafts,
        openDocToBookDraft,
        renderLibraryDetail,
        renderSourceBook,
        setSourceEmptyState,
        setSourceFrameLoading: helpers.setSourceFrameLoading,
        setSourceLink,
        setSourcePanelVisible,
        setStudyTab,
      },
    });
    let openCapturedDocToBookDraft = () => Promise.resolve();
    const {
      openCapturedDocToBookDraft: nextOpenCapturedDocToBookDraft,
      openLibraryAsset: nextOpenLibraryAsset,
      openLibraryTrace: nextOpenLibraryTrace,
    } = sourceWorkflows;
    openCapturedDocToBookDraft = nextOpenCapturedDocToBookDraft;
    openLibraryAsset = nextOpenLibraryAsset;
    openLibraryTrace = nextOpenLibraryTrace;

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
        selectedDraftIdList,
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
    window.bindAppBootstrapEvents({
      state,
      refs,
      helpers,
      callbacks: {
        captureDocToBookDraft,
        createDocToBookDraft,
        handleIngestFileSelection,
        initializeChatSession,
        loadDocToBookDrafts,
        normalizeDocToBookDraft,
        openCapturedDocToBookDraft,
        previewDocToBookPlan,
        renderIngestCaptureMeta,
        resetLibraryDetail,
        resetPipelineTrace,
        resetSourcePanel,
        setCorePack,
        setIngestSelectedFile,
        setIngestStatus,
        setLeftPanelVisible,
        setRailUploadStatus,
        setSourcePanelVisible,
        setStudyTab,
        syncIngestUploadHint,
      },
    });
  }

  return { initialize };
};
