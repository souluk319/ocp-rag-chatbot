// index.html에 남아 있는 공통 DOM/helper 함수를 묶어 두는 프론트 shell helper다.
window.createShellHelpers = function createShellHelpers(deps) {
  const refs = deps.refs;
  const state = deps.state;

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

  function setGenerating(next) {
    state.generating = next;
    refs.sendBtn.disabled = false;
    renderSendButtonState(next);
    refs.resetBtn.disabled = next;
    refs.newSessionBtn.disabled = next;
  }

  function isReviewNeeded(entity) {
    return String((entity && entity.quality_status) || "").trim().toLowerCase() === "review";
  }

  return {
    formatDuration,
    isReviewNeeded,
    resizeComposer,
    setGenerating,
    setSourceFrameLoading,
    syncChatPanelState,
    syncViewportLayout,
  };
};
