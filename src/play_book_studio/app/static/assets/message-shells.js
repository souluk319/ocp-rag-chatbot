// 채팅 empty state, pending panel, citation chip, 메시지 wrapper 같은 공통 shell 조립을 맡는 helper다.
window.createMessageShells = function createMessageShells(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const constants = deps.constants;

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function shuffledEmptyStateSamples(limit = 4) {
    const items = [...constants.emptyStateSamples];
    for (let index = items.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [items[index], items[swapIndex]] = [items[swapIndex], items[index]];
    }
    return items.slice(0, limit);
  }

  function renderEmptyState() {
    const sampleMarkup = shuffledEmptyStateSamples()
      .map(
        (sample) => `
            <button type="button" class="sample-chip" data-sample-query="${escapeHtml(sample.query)}">${escapeHtml(sample.label)}</button>
          `,
      )
      .join("");

    refs.messagesEl.innerHTML = `
        <section class="empty-state">
          <div class="empty-state-header">
            <div class="eyebrow">Play Book Studio</div>
            <h3>바로 질문해보세요</h3>
            <p>문서를 붙이고 바로 물어보면 됩니다.</p>
          </div>
          <div class="sample-grid">
            ${sampleMarkup}
          </div>
        </section>
      `;
    refs.messagesEl.querySelectorAll(".sample-chip").forEach((button) => {
      button.addEventListener("click", () => {
        refs.composerEl.value = button.dataset.sampleQuery || "";
        helpers.resizeComposer();
        refs.composerEl.focus();
      });
    });
    helpers.syncChatPanelState();
  }

  function clearEmptyState() {
    const emptyState = refs.messagesEl.querySelector(".empty-state");
    if (emptyState && refs.messagesEl.children.length === 1) {
      refs.messagesEl.innerHTML = "";
      helpers.syncChatPanelState();
    }
  }

  function appendMessage(role, text) {
    clearEmptyState();
    const wrapper = document.createElement("article");
    wrapper.className = `message ${role}`;
    const body = document.createElement("div");
    body.className = "body";
    helpers.renderMessageBody(role, body, text);
    wrapper.appendChild(body);
    refs.messagesEl.appendChild(wrapper);
    helpers.syncChatPanelState();
    refs.messagesEl.scrollTop = refs.messagesEl.scrollHeight;
    return { wrapper, body };
  }

  function renderAssistantMeta(wrapper, payload) {
    const meta = document.createElement("div");
    meta.className = "assistant-footer";

    if (payload.citations.length) {
      const citationChip = document.createElement("span");
      citationChip.className = "meta-chip";
      citationChip.textContent = `참조 ${payload.citations.length}`;
      meta.append(citationChip);
    }

    if (payload.warnings && payload.warnings.length) {
      const warningChip = document.createElement("span");
      warningChip.className = "meta-chip";
      warningChip.textContent = `경고 ${payload.warnings.length}개`;
      meta.appendChild(warningChip);
    }

    if (meta.children.length) {
      wrapper.appendChild(meta);
    }

    const suggestedQueries = Array.isArray(payload.suggested_queries)
      ? payload.suggested_queries.filter(Boolean)
      : [];
    if (suggestedQueries.length) {
      const title = document.createElement("div");
      title.className = "suggestion-list-title";
      title.textContent = "추천 질문";

      const followupGrid = document.createElement("div");
      followupGrid.className = "followup-grid";

      suggestedQueries.forEach((suggestedQuery) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "followup-chip";
        button.textContent = suggestedQuery;
        button.addEventListener("click", () => {
          if (state.currentController) return;
          void deps.sendMessage({ query: suggestedQuery });
        });
        followupGrid.appendChild(button);
      });

      wrapper.append(title, followupGrid);
    }

    if (payload.citations.length) {
      const title = document.createElement("div");
      title.className = "citation-list-title";
      title.textContent = "참조";

      const citations = document.createElement("div");
      citations.className = "source-tag-group";
      payload.citations.forEach((citation) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "source-tag";
        chip.dataset.sourceKey = helpers.sourceKeyFor(citation);

        const index = document.createElement("span");
        index.className = "source-tag-index";
        index.textContent = `참조 ${citation.index}`;

        const main = document.createElement("span");
        main.className = "source-tag-main";
        main.textContent = citation.book_title || citation.book_slug;

        const sub = document.createElement("span");
        sub.className = "source-tag-sub";
        sub.textContent = citation.section_path_label || citation.section || citation.anchor || "관련 섹션";

        chip.addEventListener("click", () => {
          void helpers.openSourcePanel(citation);
        });

        chip.append(index, main, sub);
        citations.appendChild(chip);
      });
      wrapper.append(title, citations);
      helpers.syncActiveSourceTags();
    }
  }

  function renderPendingStage(element, event) {
    element.innerHTML = "";
    const panel = document.createElement("div");
    panel.className = "pending-panel";

    const kicker = document.createElement("div");
    kicker.className = "pending-kicker";
    kicker.textContent = "답변 생성 중";

    const stage = document.createElement("div");
    stage.className = "pending-stage live";
    stage.textContent = event.label || helpers.humanizePipelineKey(event.step) || "처리 중";

    const detail = document.createElement("div");
    detail.className = "pending-detail";
    detail.textContent = event.detail
      || helpers.summarizeTraceMeta(event.meta)
      || "질문을 정리하고 관련 문서를 찾은 뒤 답을 만들고 있습니다.";

    panel.append(kicker, stage, detail);
    element.appendChild(panel);
    refs.messagesEl.scrollTop = refs.messagesEl.scrollHeight;
  }

  return {
    appendMessage,
    clearEmptyState,
    renderAssistantMeta,
    renderEmptyState,
    renderPendingStage,
  };
};
