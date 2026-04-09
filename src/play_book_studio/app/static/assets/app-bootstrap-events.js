// 앱 bootstrap의 이벤트 wiring과 startup sequence를 분리한다.
window.bindAppBootstrapEvents = function bindAppBootstrapEvents(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const callbacks = deps.callbacks;

  refs.sourceViewerFrameEl.addEventListener("load", () => {
    helpers.setSourceFrameLoading(false);
  });
  refs.sourcePanelToggleBtn.addEventListener("click", () => {
    callbacks.setSourcePanelVisible(!state.sourcePanelVisible);
  });
  refs.sourcePanelEdgeBtn.addEventListener("click", () => {
    callbacks.setSourcePanelVisible(!state.sourcePanelVisible);
  });
  refs.leftRailToggleBtn.addEventListener("click", () => {
    callbacks.setLeftPanelVisible(!state.leftPanelVisible);
  });
  refs.leftPanelToggleBtn.addEventListener("click", () => {
    callbacks.setLeftPanelVisible(!state.leftPanelVisible);
  });
  refs.railOpenIntakeBtn.addEventListener("click", () => {
    refs.ingestFileInputEl.accept = ".pdf,.html,.htm,.md,.txt,application/pdf,text/html,text/plain";
    refs.ingestFileInputEl.click();
  });
  refs.ingestPlanBtn.addEventListener("click", () => {
    void callbacks.previewDocToBookPlan().catch((error) => {
      callbacks.setIngestStatus(error.message || "doc-to-book plan 실패", "error");
    });
  });
  refs.ingestSaveBtn.addEventListener("click", () => {
    void callbacks.createDocToBookDraft().catch((error) => {
      callbacks.setIngestStatus(error.message || "doc-to-book draft 저장 실패", "error");
    });
  });
  refs.ingestCaptureBtn.addEventListener("click", () => {
    void callbacks.captureDocToBookDraft().catch((error) => {
      callbacks.setIngestStatus(error.message || "doc-to-book capture 실패", "error");
    });
  });
  refs.ingestNormalizeBtn.addEventListener("click", () => {
    void callbacks.normalizeDocToBookDraft().catch((error) => {
      callbacks.setIngestStatus(error.message || "doc-to-book normalize 실패", "error");
    });
  });
  refs.ingestFileBtn.addEventListener("click", () => {
    refs.ingestFileInputEl.click();
  });
  refs.ingestFileInputEl.addEventListener("change", () => {
    const file = refs.ingestFileInputEl.files && refs.ingestFileInputEl.files[0];
    void callbacks.handleIngestFileSelection(file).catch((error) => {
      callbacks.setIngestStatus(error.message || "파일 업로드 실패", "error");
    }).finally(() => {
      refs.ingestFileInputEl.value = "";
    });
  });
  refs.ingestDropzoneEl.addEventListener("dragover", (event) => {
    event.preventDefault();
    refs.ingestDropzoneEl.classList.add("is-dragover");
  });
  refs.ingestDropzoneEl.addEventListener("dragleave", () => {
    refs.ingestDropzoneEl.classList.remove("is-dragover");
  });
  refs.ingestDropzoneEl.addEventListener("drop", (event) => {
    event.preventDefault();
    refs.ingestDropzoneEl.classList.remove("is-dragover");
    const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
    void callbacks.handleIngestFileSelection(file).catch((error) => {
      callbacks.setIngestStatus(error.message || "파일 업로드 실패", "error");
    });
  });
  refs.ingestSourceTypeEl.addEventListener("change", () => {
    callbacks.syncIngestUploadHint();
    callbacks.setIngestSelectedFile(null);
    if (refs.ingestSourceTypeEl.value === "pdf") {
      refs.ingestUriEl.placeholder = "PDF는 파일 업로드를 권장해. 필요하면 서버 경로를 직접 넣어도 돼";
    } else {
      refs.ingestUriEl.placeholder = "웹 문서 URL 또는 업로드된 HTML 파일 경로가 여기에 표시돼";
    }
  });
  refs.ingestOpenCaptureBtn.addEventListener("click", () => {
    void callbacks.openCapturedDocToBookDraft();
  });
  window.addEventListener("resize", helpers.syncViewportLayout);
  if (typeof ResizeObserver !== "undefined" && refs.topbarEl) {
    const topbarObserver = new ResizeObserver(() => helpers.syncViewportLayout());
    topbarObserver.observe(refs.topbarEl);
  }

  helpers.syncViewportLayout();
  callbacks.initializeChatSession();
  helpers.setIngestBusy(false);
  callbacks.setRailUploadStatus("자료 추가 대기");
  callbacks.setLeftPanelVisible(true);
  callbacks.setSourcePanelVisible(true);
  callbacks.setStudyTab("source");
  callbacks.syncIngestUploadHint();
  callbacks.setIngestSelectedFile(null);
  callbacks.setCorePack(state.currentOcpVersion);
  callbacks.resetPipelineTrace();
  callbacks.resetSourcePanel();
  callbacks.resetLibraryDetail();
  callbacks.renderIngestCaptureMeta(null);
  void callbacks.loadDocToBookDrafts().catch((error) => {
    callbacks.setIngestStatus(error.message || "doc-to-book draft 목록 로드 실패", "error");
  });
};
