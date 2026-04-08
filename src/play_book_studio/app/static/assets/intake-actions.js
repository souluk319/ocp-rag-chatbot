// 업로드 초안 생성, 수집, 정리 실행 흐름을 담당하는 프론트 helper다.
window.createIntakeActions = function createIntakeActions(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const callbacks = deps.callbacks;

  function fileAcceptForSourceType(sourceType) {
    return sourceType === "pdf" ? ".pdf,application/pdf" : ".html,.htm,.md,.txt,text/html,text/plain";
  }

  function syncIngestUploadHint() {
    const sourceType = refs.ingestSourceTypeEl.value || "web";
    refs.ingestFileInputEl.accept = fileAcceptForSourceType(sourceType);
    refs.ingestDropDetailEl.textContent = sourceType === "pdf"
      ? "PDF는 바로 올려 초안으로 만들고, 수집과 정리를 거쳐 참조 자료로 준비할 수 있습니다."
      : "웹 문서는 URL을 그대로 넣거나 저장한 HTML/Markdown 파일을 올려 초안으로 만들 수 있습니다.";
  }

  function setIngestSelectedFile(file) {
    state.activeIngestUpload = file || null;
    if (!file) {
      refs.ingestFilePillEl.textContent = "선택된 파일 없음";
      return;
    }
    refs.ingestFilePillEl.textContent = `${file.name} · ${helpers.formatByteSize(file.size)}`;
  }

  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(new Error("파일을 읽지 못했습니다."));
      reader.onload = () => {
        const result = typeof reader.result === "string" ? reader.result : "";
        const parts = result.split(",", 2);
        resolve(parts.length === 2 ? parts[1] : result);
      };
      reader.readAsDataURL(file);
    });
  }

  function getDocToBookRequestPayload() {
    const sourceType = refs.ingestSourceTypeEl.value;
    const uri = (refs.ingestUriEl.value || "").trim();
    const title = (refs.ingestTitleEl.value || "").trim();
    if (!uri) {
      throw new Error("웹 문서 URL 또는 PDF 경로를 입력해.");
    }
    return {
      source_type: sourceType,
      uri,
      title,
      language_hint: "ko",
    };
  }

  async function previewDocToBookPlan() {
    const requestPayload = getDocToBookRequestPayload();
    helpers.setIngestBusy(true, "정리 계획을 계산하는 중입니다.", refs.ingestPlanBtn);
    try {
      const response = await fetch("/api/doc-to-book/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestPayload),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "doc-to-book plan을 만들지 못했습니다.");
      }
      callbacks.renderDocToBookPreview(payload);
      callbacks.setIngestStatus(
        `계획 준비 완료 · ${payload.capture_strategy} · ${payload.canonical_model}`,
        "success",
      );
      return payload;
    } finally {
      helpers.setIngestBusy(false);
    }
  }

  async function loadDocToBookDrafts(activeDraftId = "") {
    const response = await fetch("/api/doc-to-book/drafts");
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "doc-to-book draft 목록을 불러오지 못했습니다.");
    }
    callbacks.renderDocToBookDrafts(payload, activeDraftId);
    return payload;
  }

  async function openDocToBookDraft(draftId) {
    const response = await fetch(`/api/doc-to-book/drafts?draft_id=${encodeURIComponent(draftId)}`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "doc-to-book draft를 불러오지 못했습니다.");
    }
    callbacks.populateDocToBookForm(payload);
    callbacks.renderDocToBookPreview(payload);
    callbacks.renderIngestCaptureMeta(payload);
    callbacks.setStudyTab("ingest");
    callbacks.setSourcePanelVisible(true);
    callbacks.setIngestStatus(
      `초안 불러옴 · ${payload.status} · ${payload.plan.capture_strategy}`,
      "success",
    );
    await loadDocToBookDrafts(payload.draft_id || "");
    return payload;
  }

  async function createDocToBookDraft(options = {}) {
    if (state.activeIngestUpload) {
      return uploadDocToBookFile(state.activeIngestUpload, options);
    }
    const requestPayload = getDocToBookRequestPayload();
    helpers.setIngestBusy(true, "초안을 저장하는 중입니다.", refs.ingestSaveBtn);
    try {
      const response = await fetch("/api/doc-to-book/drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestPayload),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "초안을 저장하지 못했습니다.");
      }
      callbacks.populateDocToBookForm(payload);
      callbacks.renderDocToBookPreview(payload);
      callbacks.renderIngestCaptureMeta(payload);
      callbacks.setStudyTab("ingest");
      callbacks.setSourcePanelVisible(true);
      callbacks.setIngestStatus(
        `초안 저장 완료 · ${payload.plan.capture_strategy} · ${payload.draft_id}`,
        "success",
      );
      await loadDocToBookDrafts(payload.draft_id || "");
      return payload;
    } finally {
      helpers.setIngestBusy(false);
    }
  }

  async function uploadDocToBookFile(file, options = {}) {
    const { focusStudyPanel = true, successMessage = "" } = options;
    if (!file) {
      throw new Error("올릴 파일을 먼저 선택해.");
    }
    const requestPayload = {
      source_type: refs.ingestSourceTypeEl.value || "web",
      uri: file.name,
      title: (refs.ingestTitleEl.value || "").trim(),
      language_hint: "ko",
      file_name: file.name,
      content_base64: await fileToBase64(file),
    };
    helpers.setIngestBusy(true, "파일을 올려 초안을 만드는 중입니다.", refs.ingestFileBtn);
    try {
      const response = await fetch("/api/doc-to-book/upload-draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestPayload),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "업로드 초안을 만들지 못했습니다.");
      }
      callbacks.populateDocToBookForm(payload);
      callbacks.renderDocToBookPreview(payload);
      callbacks.renderIngestCaptureMeta(payload);
      if (focusStudyPanel) {
        callbacks.setStudyTab("ingest");
        callbacks.setSourcePanelVisible(true);
      }
      callbacks.setIngestStatus(
        successMessage || `업로드 준비 완료 · ${payload.request.source_type} · ${payload.draft_id}`,
        "success",
      );
      state.activeIngestUpload = null;
      refs.ingestFilePillEl.textContent = `${payload.uploaded_file_name || payload.request.uri} · 업로드됨`;
      await loadDocToBookDrafts(payload.draft_id || "");
      return payload;
    } finally {
      helpers.setIngestBusy(false);
    }
  }

  async function handleIngestFileSelection(file) {
    if (!file) return;
    await prepareUploadedSource(file);
  }

  async function fetchDocToBookBook(draftId) {
    const response = await fetch(`/api/doc-to-book/book?draft_id=${encodeURIComponent(draftId)}`);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.error || "doc-to-book book을 불러오지 못했습니다.");
    }
    return response.json();
  }

  async function captureDocToBookDraft(options = {}) {
    const { focusStudyPanel = true, successMessage = "" } = options;
    const requestPayload = state.activeIngestDraftId
      ? { draft_id: state.activeIngestDraftId }
      : getDocToBookRequestPayload();
    helpers.setIngestBusy(true, "자료를 수집하는 중입니다.", refs.ingestCaptureBtn);
    try {
      const response = await fetch("/api/doc-to-book/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestPayload),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "자료 수집을 실행하지 못했습니다.");
      }
      callbacks.populateDocToBookForm(payload);
      callbacks.renderDocToBookPreview(payload);
      callbacks.renderIngestCaptureMeta(payload);
      if (focusStudyPanel) {
        callbacks.setStudyTab("ingest");
        callbacks.setSourcePanelVisible(true);
      }
      callbacks.setIngestStatus(
        successMessage || `수집 완료 · ${payload.status} · ${helpers.formatByteSize(payload.capture_byte_size)}`,
        "success",
      );
      await loadDocToBookDrafts(payload.draft_id || "");
      return payload;
    } finally {
      helpers.setIngestBusy(false);
    }
  }

  async function normalizeDocToBookDraft(options = {}) {
    const { focusStudyPanel = true, successMessage = "" } = options;
    if (!state.activeIngestDraftId) {
      throw new Error("먼저 초안을 저장하고 수집까지 끝내야 합니다.");
    }
    helpers.setIngestBusy(true, "자료를 정리하는 중입니다.", refs.ingestNormalizeBtn);
    try {
      const response = await fetch("/api/doc-to-book/normalize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ draft_id: state.activeIngestDraftId }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "자료 정리를 실행하지 못했습니다.");
      }
      callbacks.populateDocToBookForm(payload);
      callbacks.renderDocToBookPreview(payload);
      callbacks.renderIngestCaptureMeta(payload);
      if (focusStudyPanel) {
        callbacks.setStudyTab("ingest");
        callbacks.setSourcePanelVisible(true);
      }
      callbacks.setIngestStatus(
        successMessage || `정리 완료 · ${payload.status} · ${payload.normalized_section_count || 0}개 섹션`,
        "success",
      );
      await loadDocToBookDrafts(payload.draft_id || "");
      return payload;
    } finally {
      helpers.setIngestBusy(false);
    }
  }

  async function prepareUploadedSource(file) {
    if (!file) return null;
    const inferredSourceType = helpers.inferSourceTypeFromFile(file);
    refs.ingestSourceTypeEl.value = inferredSourceType;
    syncIngestUploadHint();
    setIngestSelectedFile(file);
    if (!refs.ingestTitleEl.value.trim()) {
      refs.ingestTitleEl.value = file.name.replace(/\.[^.]+$/, "");
    }
    refs.ingestUriEl.value = file.name;
    helpers.setRailUploadStatus(`${file.name} 업로드 중`, "busy");
    try {
      await uploadDocToBookFile(file, {
        focusStudyPanel: false,
        successMessage: `upload ready · ${file.name}`,
      });
      helpers.setRailUploadStatus(`${file.name} 수집 중`, "busy");
      await captureDocToBookDraft({
        focusStudyPanel: false,
        successMessage: `수집 완료 · ${file.name}`,
      });
      helpers.setRailUploadStatus(`${file.name} 정제 중`, "busy");
      const normalized = await normalizeDocToBookDraft({
        focusStudyPanel: false,
        successMessage: `정리 완료 · ${file.name}`,
      });
      callbacks.onDraftReady(normalized);
      helpers.setRailUploadStatus(
        `${normalized.title || file.name} 준비 완료 · ${normalized.normalized_section_count || 0}개 섹션`,
        "success",
      );
      return normalized;
    } catch (error) {
      helpers.setRailUploadStatus(error.message || "문서 업로드 처리 실패", "error");
      throw error;
    }
  }

  return {
    captureDocToBookDraft,
    createDocToBookDraft,
    fetchDocToBookBook,
    fileAcceptForSourceType,
    fileToBase64,
    getDocToBookRequestPayload,
    handleIngestFileSelection,
    loadDocToBookDrafts,
    normalizeDocToBookDraft,
    openDocToBookDraft,
    prepareUploadedSource,
    previewDocToBookPlan,
    setIngestSelectedFile,
    syncIngestUploadHint,
    uploadDocToBookFile,
  };
};
