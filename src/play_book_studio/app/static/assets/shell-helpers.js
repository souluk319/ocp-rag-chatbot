// index.html에 남아 있는 공통 DOM/helper 함수를 묶어 두는 프론트 shell helper다.
window.createShellHelpers = function createShellHelpers(deps) {
  const refs = deps.refs;
  const state = deps.state;

  let setIngestStatusHandler = () => {};

  function bindIngestStatus(handler) {
    setIngestStatusHandler = typeof handler === "function" ? handler : () => {};
  }

  function resizeComposer() {
    refs.composerEl.style.height = "22px";
    refs.composerEl.style.height = `${Math.min(refs.composerEl.scrollHeight, 88)}px`;
  }

  function syncChatPanelState() {
    if (!refs.chatPanelEl) return;
    const hasOnlyEmptyState =
      refs.messagesEl.children.length === 1 && refs.messagesEl.querySelector(".empty-state");
    refs.chatPanelEl.classList.toggle("has-messages", refs.messagesEl.children.length > 0 && !hasOnlyEmptyState);
  }

  function syncViewportLayout() {
    const topbarHeight = refs.topbarEl ? Math.ceil(refs.topbarEl.getBoundingClientRect().height) : 0;
    const shellStyle = getComputedStyle(refs.shellEl);
    const shellPadTop = parseFloat(shellStyle.paddingTop || "0");
    const topbarMarginBottom = refs.topbarEl
      ? parseFloat(getComputedStyle(refs.topbarEl).marginBottom || "0")
      : 0;
    const chromeOffset = Math.max(shellPadTop, shellPadTop + topbarHeight + topbarMarginBottom);
    refs.shellEl.style.setProperty("--chrome-offset", `${chromeOffset}px`);
  }

  function setButtonBusy(button, busy) {
      if (!button) return;
      button.classList.add("button-busy");
      button.classList.toggle("is-busy", Boolean(busy));
      button.setAttribute("aria-busy", busy ? "true" : "false");
    }

    function renderSendButtonState(generating) {
      if (!refs.sendBtn) return;
      refs.sendBtn.classList.toggle("is-stop", generating);
      refs.sendBtn.classList.toggle("is-stop-icon", generating);
      refs.sendBtn.classList.remove("button-busy", "is-busy");
      refs.sendBtn.setAttribute("aria-busy", "false");
      if (generating) {
        refs.sendBtn.innerHTML = '<span class="send-btn-stop-icon" aria-hidden="true"></span>';
        refs.sendBtn.setAttribute("aria-label", "생성 중지");
        refs.sendBtn.setAttribute("title", "생성 중지");
        return;
      }
      refs.sendBtn.textContent = "전송";
      refs.sendBtn.setAttribute("aria-label", "전송");
      refs.sendBtn.setAttribute("title", "전송");
    }

  function setIngestBusy(busy, message = "", activeButton = null) {
    refs.ingestStatusEl.dataset.busy = busy ? "true" : "false";
    [
      refs.ingestFileBtn,
      refs.ingestPlanBtn,
      refs.ingestSaveBtn,
      refs.ingestCaptureBtn,
      refs.ingestNormalizeBtn,
      refs.ingestOpenCaptureBtn,
    ].forEach((button) => {
      setButtonBusy(button, busy && button === activeButton);
    });
    if (message) {
      setIngestStatusHandler(message, "muted");
    }
  }

  function setSourceFrameLoading(loading) {
    if (!refs.sourceFrameShellEl) return;
    refs.sourceFrameShellEl.classList.toggle("loading", Boolean(loading));
  }

  function formatDuration(value) {
    if (typeof value !== "number" || !Number.isFinite(value)) return "";
    if (value >= 1000) {
      return `${(value / 1000).toFixed(2)}s`;
    }
    return `${Math.round(value)}ms`;
  }

  function formatByteSize(value) {
    if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) return "-";
    if (value >= 1024 * 1024) {
      return `${(value / (1024 * 1024)).toFixed(1)} MB`;
    }
    if (value >= 1024) {
      return `${Math.round(value / 1024)} KB`;
    }
    return `${Math.round(value)} B`;
  }

  function inferSourceTypeFromFile(file) {
    const name = String(file && file.name ? file.name : "").toLowerCase();
    return name.endsWith(".pdf") ? "pdf" : "web";
  }

  function setGenerating(next) {
      state.generating = next;
      refs.sendBtn.disabled = false;
      renderSendButtonState(next);
      refs.resetBtn.disabled = next;
      refs.newSessionBtn.disabled = next;
    }

  function humanizeDraftValue(value) {
    const token = String(value || "").trim();
    if (!token) return "-";
    if (token === "docs_redhat_html_single_v1") return "HTML single";
    if (token === "pdf_text_extract_v1") return "PDF text";
    if (token === "canonical_book_v1") return "정리본 v1";
    if (token === "source_view_first") return "Source-first";
    if (token === "chunks_from_canonical_sections") return "검색 파생";
    return token.replace(/_/g, " ");
  }

  function humanizeSourceCollection(value) {
    const token = String(value || "").trim().toLowerCase();
    if (!token) return "자료군 미확인";
    if (token === "core") return "기본 문서";
    if (token === "uploaded") return "업로드 자료";
    return token;
  }

  function humanizeInferredProduct(value) {
    const token = String(value || "").trim().toLowerCase();
    if (!token || token === "unknown") return "";
    if (token === "openshift") return "OpenShift";
    if (token === "kubernetes") return "Kubernetes";
    return token;
  }

  function formatInferredScope(entity) {
    if (!entity || typeof entity !== "object") return "Version unknown";
    const product = humanizeInferredProduct(entity.inferred_product);
    const version = String(entity.inferred_version || "").trim();
    if (product && version && version !== "unknown") return `${product} ${version}`;
    if (product) return `${product} version unknown`;
    if (version && version !== "unknown") return `Version ${version}`;
    return "Version unknown";
  }

  function qualityStatusLabel(entity) {
    const status = String((entity && entity.quality_status) || "").trim().toLowerCase();
    if (!status) return "";
    if (status === "ready") return "품질 검증 통과";
    if (status === "review") return "정규화 검토 필요";
    return status;
  }

  function qualitySummaryText(entity) {
    return String((entity && entity.quality_summary) || "").trim();
  }

  function isReviewNeeded(entity) {
    return String((entity && entity.quality_status) || "").trim().toLowerCase() === "review";
  }

  function createSummaryChip(label) {
    const chip = document.createElement("span");
    chip.className = "source-summary-chip";
    chip.textContent = label;
    return chip;
  }

  return {
    bindIngestStatus,
    createSummaryChip,
    formatByteSize,
    formatDuration,
    formatInferredScope,
    humanizeDraftValue,
    humanizeSourceCollection,
    inferSourceTypeFromFile,
    isReviewNeeded,
    qualityStatusLabel,
    qualitySummaryText,
    resizeComposer,
    setButtonBusy,
    setGenerating,
    setIngestBusy,
    setSourceFrameLoading,
    syncChatPanelState,
    syncViewportLayout,
  };
};
