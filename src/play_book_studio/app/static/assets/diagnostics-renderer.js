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
          <div class="metric-label">${label}</div>
          <div class="metric-value">${formatMetricScore(summary ? summary.top_score : null)}</div>
          <div class="metric-detail">${detailParts.join("<br>")}</div>
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
      container.innerHTML = '<div class="trace-empty" style="text-align: center; color: var(--muted); padding-top: 40px; font-size: 14px;">질문을 보내거나 말풍선을 클릭하면<br>상황실 모니터가 켜집니다.</div>';
      return;
    }

    const friendlyMap = {
      route_query: { title: "요청 접수", desc: "질문의 종류를 판별하고 있습니다." },
      rewrite_query: { title: "질문 분석", desc: "질문의 숨은 의도와 핵심 키워드를 파악합니다." },
      bm25_search: { title: "키워드 매칭", desc: "단어 단위로 흩어진 관련 문서를 긁어옵니다." },
      vector_search: { title: "의미 탐색", desc: "문맥상 비슷한 의미를 가진 공식 문서를 찾습니다." },
      fusion: { title: "하이브리드 병합", desc: "BM25와 Vector 결과를 수학적으로 결합합니다." },
      rerank: { title: "문맥 재정렬 (AI 리랭킹)", desc: "AI 모델이 문서 문맥을 분석해 정답 우선순위를 조정합니다." },
      query_reranking: { title: "문맥 재정렬 (AI 리랭킹)", desc: "AI 모델이 문서 문맥을 분석해 정답 우선순위를 조정합니다." },
      llm_generate: { title: "답변 작성 중", desc: "선정된 근거를 바탕으로 답변을 구성합니다." },
      pipeline_complete: { title: "임무 완료", desc: "검색과 답변 생성을 마쳤습니다." },
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

      let detail = event.detail || friendlyMap[key].desc;
      if (metaParts.length) {
        detail += `<br><span class="stepper-meta-chip">📊 ${metaParts.join(" | ")}</span>`;
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
