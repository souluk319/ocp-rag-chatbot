// 세션 상태와 왼쪽 상황실 렌더링을 담당하는 active-path diagnostics helper다.
window.createDiagnosticsRenderer = function createDiagnosticsRenderer(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;

  let statusPulseTimer = null;
  let statusBaseText = "준비됨";

  function stopStatusPulse() {
    if (statusPulseTimer) {
      clearInterval(statusPulseTimer);
      statusPulseTimer = null;
    }
    refs.statusDotEl.classList.remove("live");
    refs.statusTextEl.textContent = statusBaseText;
  }

  function startStatusPulse() {
    stopStatusPulse();
    let dots = 0;
    refs.statusDotEl.classList.add("live");
    statusPulseTimer = setInterval(() => {
      dots = (dots + 1) % 4;
      refs.statusTextEl.textContent = `${statusBaseText}${".".repeat(dots)}`;
    }, 420);
  }

  function setStatus(text, { live = false, detail = "" } = {}) {
    statusBaseText = text || "준비됨";
    refs.statusTextEl.dataset.detail = detail || "";
    if (live) {
      startStatusPulse();
    } else {
      stopStatusPulse();
    }
  }

  function updateSessionContextDisplay() {
    return undefined;
  }

  function humanizePipelineKey(key) {
    return helpers.pipelineLabels[key] || key;
  }

  function summarizeTraceMeta(meta) {
    if (!meta || !Object.keys(meta).length) return "";
    const preferred = ["provider", "model", "top_k", "selected", "hits", "citation_count"];
    const lines = [];
    preferred.forEach((key) => {
      if (!(key in meta)) return;
      const value = meta[key];
      lines.push(`${key}: ${Array.isArray(value) ? value.join(", ") : String(value)}`);
    });
    Object.keys(meta).forEach((key) => {
      if (preferred.includes(key)) return;
      const value = meta[key];
      if (typeof value === "object") return;
      lines.push(`${key}: ${String(value)}`);
    });
    return lines.join("\n");
  }

  function formatMetricScore(value, digits = 4) {
    if (value === undefined || value === null || value === "") return "-";
    const numeric = Number(value);
    if (Number.isNaN(numeric)) return String(value);
    return numeric.toFixed(digits);
  }

  function activateLeftRailPage(targetId) {
    (refs.leftTraceTabButtons || []).forEach((button) => {
      const active = button.dataset.target === targetId;
      button.classList.toggle("active", active);
      button.style.background = active ? "white" : "transparent";
      button.style.color = active ? "var(--ink)" : "var(--muted)";
      button.style.boxShadow = active ? "0 1px 2px rgba(0,0,0,0.05)" : "none";
    });

    (refs.leftRailPages || []).forEach((page) => {
      const active = page.dataset.railPage === targetId;
      page.classList.toggle("active", active);
      page.style.display = active ? (targetId === "library" ? "flex" : "block") : "none";
    });
  }

  function bindLeftRailTabs() {
    (refs.leftTraceTabButtons || []).forEach((button) => {
      button.addEventListener("click", () => {
        activateLeftRailPage(button.dataset.target || "library");
      });
    });
  }

  function summarizeMetricCards(traceEvents) {
    const metricEvents = new Map();
    (traceEvents || []).forEach((event) => {
      if (!event || !event.step) return;
      if (["bm25_search", "vector_search", "fusion"].includes(event.step)) {
        metricEvents.set(event.step, event);
      }
    });
    if (!metricEvents.size) return "";

    const cards = [];
    [
      ["bm25_search", "BM25", "키워드 일치 강도", "metric-selected"],
      ["vector_search", "Vector", "문맥 의미 유사도", "metric-selected"],
      ["fusion", "Hybrid", "BM25와 Vector를 결합한 최종 점수", "metric-hybrid"],
    ].forEach(([step, label, meaning, klass]) => {
      const event = metricEvents.get(step);
      if (!event) return;
      const summary = event.meta && event.meta.summary ? event.meta.summary : null;
      const topHit = summary && Array.isArray(summary.top_hits) ? summary.top_hits[0] : null;
      const detailParts = [meaning];
      if (summary && typeof summary.count === "number") {
        detailParts.push(`후보 ${summary.count}개`);
      }
      if (step === "fusion" && topHit) {
        const fusedFrom = [];
        if (topHit.bm25_rank !== undefined) {
          fusedFrom.push(`BM25 ${Math.round(Number(topHit.bm25_rank))}위`);
        }
        if (topHit.vector_rank !== undefined) {
          fusedFrom.push(`Vector ${Math.round(Number(topHit.vector_rank))}위`);
        }
        if (fusedFrom.length) {
          detailParts.push(`결합 근거: ${fusedFrom.join(" + ")}`);
        }
      }
      if (topHit && topHit.section) {
        const section = String(topHit.section);
        detailParts.push(`상위 근거: ${section.slice(0, 46)}${section.length > 46 ? "…" : ""}`);
      }
      cards.push(`
        <div class="metric-card ${klass} metric-card-compact">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.04); padding-bottom: 4px; margin-bottom: 2px;">
            <div class="metric-label" style="font-size: 10px;">${label}</div>
            <div class="metric-value" style="font-size: 13px;">${formatMetricScore(summary ? summary.top_score : null)}</div>
          </div>
          <div class="metric-detail" style="font-size: 9px; line-height: 1.35;">${detailParts.join(" <span style='opacity:0.4'>|</span> ")}</div>
        </div>
      `);
    });

    if (!cards.length) return "";
    return `<div class="metric-grid" style="margin-bottom: 14px;">${cards.join("")}</div>`;
  }

  function renderFriendlyTrace(traceEvents, retrievalTrace) {
    const container = refs.friendlyStepperContainerEl;
    if (!container) return;

    if (!traceEvents || !traceEvents.length) {
      container.innerHTML = '<div class="trace-empty" style="text-align: center; color: var(--muted); padding-top: 40px; font-size: 14px;">대기 중</div>';
      return;
    }

    const friendlyMap = {
      route_query: { title: "Request", desc: "" },
      rewrite_query: { title: "Query", desc: "" },
      bm25_search: { title: "BM25", desc: "" },
      vector_search: { title: "Vector", desc: "" },
      fusion: { title: "Hybrid", desc: "" },
      rerank: { title: "Rerank", desc: "" },
      query_reranking: { title: "Rerank", desc: "" },
      llm_generate: { title: "Answer", desc: "" },
      pipeline_complete: { title: "Complete", desc: "" },
    };

    let html = "";
    const rerankerEnabled = Boolean(retrievalTrace && retrievalTrace.reranker && retrievalTrace.reranker.enabled);
    html += `
      <div class="trace-runtime-status">
        BM25 <strong>on</strong>
        <span>·</span>
        Vector <strong>${traceEvents.some((event) => event && event.step === "vector_search") ? "on" : "off"}</strong>
        <span>·</span>
        Hybrid <strong>${traceEvents.some((event) => event && event.step === "fusion") ? "on" : "off"}</strong>
        <span>·</span>
        Reranker <strong>${rerankerEnabled ? "on" : "off"}</strong>
      </div>
    `;
    html += summarizeMetricCards(traceEvents);
    html += '<div class="friendly-stepper">';

    const stepMap = new Map();
    traceEvents.forEach((event) => {
      let key = event.step || "";
      if (key === "normalize_query") key = "rewrite_query";
      if (key === "context_assembly" || key === "prompt_build") key = "llm_generate";
      if (key === "citation_finalize") key = "pipeline_complete";
      if (!friendlyMap[key]) return;

      const metaParts = [];
      if (event.meta) {
        if (event.meta.hits) metaParts.push(`가져온 문단: ${event.meta.hits}개`);
        if (event.meta.selected) metaParts.push(`최종 선정: ${event.meta.selected}개`);
        if (event.meta.provider && event.meta.model) metaParts.push(`AI 모델: ${event.meta.model}`);
        Object.keys(event.meta).forEach((metaKey) => {
          if (["alpha", "hits", "selected", "provider", "model", "summary"].includes(metaKey)) return;
          if (typeof event.meta[metaKey] === "object") return;
          metaParts.push(`${metaKey}: ${event.meta[metaKey]}`);
        });
      }

      let detail = "";
      if (event.detail) {
        detail = event.detail;
      } else if (friendlyMap[key].desc) {
        detail = friendlyMap[key].desc;
      }
      if (metaParts.length) {
        detail += `${detail ? "<br>" : ""}<span class="stepper-meta-chip">📊 ${metaParts.join(" | ")}</span>`;
      }

      stepMap.set(key, {
        title: friendlyMap[key].title,
        desc: detail,
        status: event.status === "running" ? "running" : (event.status === "error" ? "error" : "done"),
      });
    });

    Array.from(stepMap.values()).forEach((step) => {
      const iconHtml = step.status === "done" ? "✓" : (step.status === "error" ? "!" : "⋯");
      html += `
        <div class="stepper-item ${step.status}">
          <div class="stepper-icon">${iconHtml}</div>
          <div class="stepper-title">${step.title}</div>
          <div class="stepper-detail">${step.desc}</div>
        </div>
      `;
    });

    html += "</div>";
    container.innerHTML = html;
  }

  function resetPipelineTrace() {
    state.traceEvents = [];
    renderFriendlyTrace([], state.latestRetrievalTrace || {});
  }

  function renderPipelineLive() {
    renderFriendlyTrace(state.traceEvents || [], state.latestRetrievalTrace || {});
  }

  function renderSearchMetrics() {
    renderFriendlyTrace(state.traceEvents || [], state.latestRetrievalTrace || {});
  }

  function renderPipelineSummary() {
    renderFriendlyTrace(state.traceEvents || [], state.latestRetrievalTrace || {});
  }

  function renderPipelineTrace() {
    renderFriendlyTrace(state.traceEvents || [], state.latestRetrievalTrace || {});
  }

  function appendTraceEvent(event) {
    state.traceEvents = [...(state.traceEvents || []), event];
    renderFriendlyTrace(state.traceEvents, state.latestRetrievalTrace || {});
    const detailParts = [];
    if (event.detail) detailParts.push(event.detail);
    if (event.duration_ms) detailParts.push(helpers.formatDuration(event.duration_ms));
    setStatus(event.label || "처리 중", {
      live: event.status === "running",
      detail: detailParts.join(" · "),
    });
  }

  function updateSidePanel(payload) {
    state.latestRetrievalTrace = payload.retrieval_trace || {};
    if (payload.pipeline_trace && Array.isArray(payload.pipeline_trace.events)) {
      state.traceEvents = payload.pipeline_trace.events;
    }
    renderFriendlyTrace(state.traceEvents || [], state.latestRetrievalTrace);
  }

  bindLeftRailTabs();
  activateLeftRailPage("library");

  return {
    appendTraceEvent,
    humanizePipelineKey,
    renderPipelineLive,
    renderPipelineSummary,
    renderPipelineTrace,
    renderSearchMetrics,
    resetPipelineTrace,
    setStatus,
    startStatusPulse,
    stopStatusPulse,
    summarizeTraceMeta,
    updateSessionContextDisplay,
    updateSidePanel,
  };
};
