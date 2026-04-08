// 질문 전송, 스트리밍 응답, 세션 리셋처럼 채팅 흐름 자체를 담당하는 프론트 helper다.
window.createChatSession = function createChatSession(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const constants = deps.constants;

  const messageShells = window.createMessageShells({
    state,
    refs,
    constants,
    helpers,
    sendMessage: (payload) => sendMessage(payload),
  });
  const {
    appendMessage,
    renderAssistantMeta,
    renderEmptyState,
    renderPendingStage,
  } = messageShells;

  function shuffledComposerSamples(limit = 4) {
    const items = Array.isArray(constants.emptyStateSamples) ? [...constants.emptyStateSamples] : [];
    for (let index = items.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [items[index], items[swapIndex]] = [items[swapIndex], items[index]];
    }
    return items.slice(0, limit);
  }

  function escapeComposerSample(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function renderComposerSamples() {
    if (!refs.composerSamplesEl) return;
    const sampleMarkup = shuffledComposerSamples()
      .map(
        (sample) => `
            <button type="button" class="sample-chip" data-sample-query="${escapeComposerSample(sample.query)}">${escapeComposerSample(sample.label)}</button>
          `,
      )
      .join("");
    refs.composerSamplesEl.innerHTML = `
        <div class="composer-samples-title">예시 질문</div>
        <div class="composer-samples-list">
          ${sampleMarkup}
        </div>
      `;
    refs.composerSamplesEl.querySelectorAll(".sample-chip").forEach((button) => {
      button.addEventListener("click", () => {
        refs.composerEl.value = button.dataset.sampleQuery || "";
        helpers.resizeComposer();
        refs.composerEl.focus();
      });
    });
  }

  async function typeText(element, text, role = "assistant") {
    if (state.currentTyper) {
      clearInterval(state.currentTyper);
      state.currentTyper = null;
    }
    element.textContent = "";
    let index = 0;
    await new Promise((resolve) => {
      state.currentTyper = setInterval(() => {
        index += 4;
        element.textContent = text.slice(0, index);
        refs.messagesEl.scrollTop = refs.messagesEl.scrollHeight;
        if (index >= text.length) {
          clearInterval(state.currentTyper);
          state.currentTyper = null;
          helpers.renderMessageBody(role, element, text);
          resolve();
        }
      }, 12);
    });
  }

  async function consumeChatStream(response, onEvent) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) continue;
        onEvent(JSON.parse(line));
      }

      if (done) break;
    }

    if (buffer.trim()) {
      onEvent(JSON.parse(buffer));
    }
  }

  async function sendMessage({ query, regenerate = false } = {}) {
    const trimmed = (query ?? refs.composerEl.value).trim();
    if (!trimmed && !regenerate) return;

    if (!regenerate) {
      appendMessage("user", trimmed);
      refs.composerEl.value = "";
      helpers.resizeComposer();
      state.lastQuery = trimmed;
    }

    const { wrapper, body } = appendMessage("assistant", "생성 중...");
    wrapper.classList.add("streaming");
    helpers.resetPipelineTrace();
    helpers.setGenerating(true);
    helpers.renderPipelineLive();
    helpers.setStatus("파이프라인 시작", { live: true, detail: "질문을 분석하고 있습니다" });
    state.currentController = new AbortController();

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: state.sessionId,
          query: trimmed,
          mode: state.currentMode,
          ocp_version: state.currentOcpVersion,
          selected_draft_ids: helpers.selectedDraftIdList(),
          restrict_uploaded_sources: true,
          regenerate,
        }),
        signal: state.currentController.signal,
      });
      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.error || "응답 생성 실패");
      }

      let payload = null;
      let streamedError = null;
      await consumeChatStream(response, (event) => {
        if (event.type === "trace") {
          helpers.appendTraceEvent(event);
          renderPendingStage(body, event);
          return;
        }
        if (event.type === "error") {
          streamedError = event.error || "응답 생성 실패";
          return;
        }
        if (event.type === "result") {
          payload = event.payload || null;
        }
      });
      if (streamedError) {
        throw new Error(streamedError);
      }
      if (!payload) {
        throw new Error("스트리밍 응답이 비어 있습니다.");
      }

      state.sessionId = payload.session_id;
      refs.sessionIdEl.textContent = state.sessionId.slice(0, 8);
      await typeText(body, payload.answer || "답변이 비어 있습니다.", "assistant");
      helpers.renderAssistantBody(body, payload.answer || "답변이 비어 있습니다.", payload.citations || []);
      wrapper.classList.remove("streaming");
      renderAssistantMeta(wrapper, payload);
      helpers.updateSidePanel(payload);
      helpers.setStatus("완료", {
        detail: payload.pipeline_trace && payload.pipeline_trace.timings_ms
          ? `총 ${helpers.formatDuration(payload.pipeline_trace.timings_ms.total || 0)}`
          : "응답 생성이 끝났습니다",
      });
    } catch (error) {
      wrapper.classList.remove("streaming");
      if (error.name === "AbortError") {
        helpers.renderMessageBody("assistant", body, "응답 표시를 중단했습니다.");
        helpers.setStatus("중단됨", { detail: "클라이언트에서 응답 표시를 멈췄습니다" });
      } else {
        helpers.renderMessageBody("assistant", body, error.message || "오류가 발생했습니다.");
        helpers.setStatus("오류", { detail: error.message || "오류가 발생했습니다." });
      }
    } finally {
      state.currentController = null;
      helpers.setGenerating(false);
      helpers.renderPipelineLive();
    }
  }

  async function resetSession() {
    const response = await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: state.sessionId }),
    });
    const payload = await response.json();
    state.sessionId = payload.session_id;
    refs.sessionIdEl.textContent = state.sessionId.slice(0, 8);
    refs.messagesEl.innerHTML = "";
    renderEmptyState();
    renderComposerSamples();
    refs.rewrittenQueryEl.textContent = "-";
    helpers.updateSessionContextDisplay(payload.context || {});
    refs.warningsEl.textContent = "없음";
    helpers.resetPipelineTrace();
    state.lastQuery = "";
    helpers.resetSourcePanel();
    helpers.setStatus("리셋됨", { detail: "새 세션으로 다시 시작합니다" });
  }

  async function startNewSession() {
    const response = await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: crypto.randomUUID() }),
    });
    const payload = await response.json();
    state.sessionId = payload.session_id;
    refs.sessionIdEl.textContent = state.sessionId.slice(0, 8);
    refs.messagesEl.innerHTML = "";
    renderEmptyState();
    renderComposerSamples();
    refs.rewrittenQueryEl.textContent = "-";
    helpers.updateSessionContextDisplay(payload.context || {});
    refs.warningsEl.textContent = "없음";
    helpers.resetPipelineTrace();
    state.lastQuery = "";
    helpers.resetSourcePanel();
    helpers.setStatus("새 세션", { detail: "새 대화를 시작합니다" });
  }

  function bindEvents() {
    refs.composerEl.addEventListener("keydown", (event) => {
      if (event.isComposing || event.keyCode === 229 || state.isComposing) {
        return;
      }
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        void sendMessage();
      }
    });

    refs.composerEl.addEventListener("input", () => {
      helpers.resizeComposer();
    });

    refs.composerEl.addEventListener("compositionstart", () => {
      state.isComposing = true;
    });

    refs.composerEl.addEventListener("compositionend", () => {
      state.isComposing = false;
    });

    refs.composerEl.addEventListener("blur", () => {
      state.isComposing = false;
    });

    refs.sendBtn.addEventListener("click", () => {
      if (!state.generating) {
        void sendMessage();
        return;
      }
      if (state.currentController) state.currentController.abort();
      if (state.currentTyper) {
        clearInterval(state.currentTyper);
        state.currentTyper = null;
      }
    });

    refs.resetBtn.addEventListener("click", resetSession);
    refs.newSessionBtn.addEventListener("click", startNewSession);
  }

  function initialize() {
    refs.sessionIdEl.textContent = state.sessionId.slice(0, 8);
    helpers.resizeComposer();
    helpers.setGenerating(false);
    renderEmptyState();
    renderComposerSamples();
  }

  return {
    bindEvents,
    initialize,
    renderEmptyState,
    resetSession,
    sendMessage,
    startNewSession,
  };
};
