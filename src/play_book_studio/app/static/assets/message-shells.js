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
            <h3>질문을 시작하세요</h3>
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

  function stripTopicPrefix(value) {
    const text = String(value || "").trim();
    if (!text) return "";
    const lastSegment = text.split(">").pop().trim();
    const cleaned = lastSegment.replace(/^\d+(?:\.\d+)*\.?\s*/, "").trim();
    return cleaned || lastSegment;
  }

  function inferSuggestionSubject(payload) {
    const rewritten = String(payload?.rewritten_query || "").trim();
    const answer = String(payload?.answer || "").trim();
    const topic = String(payload?.context?.current_topic || "").trim();
    const citations = Array.isArray(payload?.citations) ? payload.citations : [];
    const primary = citations[0] || null;
    const primarySection = stripTopicPrefix(primary?.section || "");

    if (/route/i.test(rewritten) && /ingress/i.test(rewritten)) return "Route와 Ingress";
    if (/etcd/i.test(rewritten) || /etcd/i.test(answer)) return "etcd";
    if (/machine config operator|mco/i.test(rewritten) || /machine config operator|mco/i.test(answer)) {
      return "Machine Config Operator";
    }
    if (/operator/i.test(rewritten) || /operator/i.test(answer) || /operator/i.test(primarySection)) {
      return "Operator";
    }
    if (topic) return stripTopicPrefix(topic);
    if (primarySection) return primarySection;
    return "";
  }

  function contextualizeSuggestedQuery(suggestedQuery, payload) {
    const cleaned = String(suggestedQuery || "").trim();
    if (!cleaned) return cleaned;
    const subject = inferSuggestionSubject(payload);
    if (!subject) return cleaned;

    const replacements = {
      "실행 예시도 같이 보여줘": `${subject} 관련 실행 예시도 같이 보여줘`,
      "주의사항도 함께 정리해줘": `${subject} 관련 주의사항도 함께 정리해줘`,
      "운영 중 주의사항도 함께 정리해줘": `${subject} 운영 시 주의사항도 함께 정리해줘`,
      "상태 확인 방법도 같이 알려줘": `${subject} 상태 확인 방법도 같이 알려줘`,
      "실무에서 언제 쓰는지 알려줘": `${subject}를 실무에서 언제 쓰는지 알려줘`,
      "초보자 기준으로 단계별로 설명해줘": `${subject}를 초보자 기준으로 단계별로 설명해줘`,
      "실무에서 왜 중요한지도 설명해줘": `${subject}가 실무에서 왜 중요한지도 설명해줘`,
    };
    return replacements[cleaned] || cleaned;
  }

  function renderAssistantMeta(wrapper, payload) {
    const meta = document.createElement("div");
    meta.className = "assistant-footer";

    if (meta.children.length) {
      wrapper.appendChild(meta);
    }

    const suggestedQueries = Array.isArray(payload.suggested_queries)
      ? payload.suggested_queries.filter(Boolean)
      : [];
    const canRenderSuggestedQueries = (
      payload.response_kind === "rag"
      && Array.isArray(payload.citations)
      && payload.citations.length > 0
      && Array.isArray(payload.cited_indices)
      && payload.cited_indices.length > 0
      && (!Array.isArray(payload.warnings) || payload.warnings.length === 0)
    );
    if (suggestedQueries.length && canRenderSuggestedQueries) {
      const title = document.createElement("div");
      title.className = "suggestion-list-title";
      title.textContent = "Follow-ups";

      const followupGrid = document.createElement("div");
      followupGrid.className = "followup-grid";

      suggestedQueries.forEach((suggestedQuery) => {
        const effectiveQuery = contextualizeSuggestedQuery(suggestedQuery, payload);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "followup-chip";
        button.textContent = effectiveQuery;
        button.addEventListener("click", () => {
          if (state.currentController) return;
          void deps.sendMessage({ query: effectiveQuery });
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
    const stageBlueprint = [
      { label: "질문 분석", steps: ["route_query", "normalize_query", "rewrite_query"] },
      { label: "키워드 검색", steps: ["bm25_search"] },
      { label: "의미 검색", steps: ["vector_search"] },
      { label: "결과 결합", steps: ["fusion"] },
      { label: "리랭킹", steps: ["rerank", "query_reranking"] },
      { label: "근거 조립", steps: ["context_assembly", "prompt_build"] },
      { label: "답변 생성", steps: ["llm_generate"] },
      { label: "참조 정리", steps: ["citation_finalize"] },
    ];
    const eventByStep = new Map();
    (state.traceEvents || []).forEach((traceEvent) => {
      if (!traceEvent || !traceEvent.step) return;
      eventByStep.set(traceEvent.step, traceEvent);
    });

    function chipStatus(steps) {
      const matches = steps
        .map((step) => eventByStep.get(step))
        .filter(Boolean);
      if (!matches.length) return "pending";
      if (matches.some((item) => item.status === "error")) return "warning";
      if (matches.some((item) => item.status === "running")) return "running";
      if (matches.some((item) => item.status === "done")) return "done";
      return "pending";
    }

    element.innerHTML = "";
    const panel = document.createElement("div");
    panel.className = "pending-panel";

    const kicker = document.createElement("div");
    kicker.className = "pending-kicker";
    kicker.textContent = "답변 생성 중";

    const stage = document.createElement("div");
    stage.className = "pending-stage live";
    stage.textContent = event.label || helpers.humanizePipelineKey(event.step) || "처리 중";

    const stageStrip = document.createElement("div");
    stageStrip.className = "stage-strip";
    stageBlueprint.forEach((item) => {
      const chip = document.createElement("div");
      chip.className = `stage-chip ${chipStatus(item.steps)}`;
      chip.textContent = item.label;
      stageStrip.appendChild(chip);
    });

    const detail = document.createElement("div");
    detail.className = "pending-detail";
    detail.textContent = event.detail
      || helpers.summarizeTraceMeta(event.meta)
      || "";

    panel.append(kicker, stage, stageStrip, detail);
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
