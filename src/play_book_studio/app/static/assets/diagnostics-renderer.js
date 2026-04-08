// 세션 문맥, 상태 표시, 파이프라인 추적 패널 렌더링을 담당하는 프론트 helper다.
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

  function updateSessionContextDisplay(context = null) {
    const baseContext = context && typeof context === "object" ? { ...context } : {};
    baseContext.mode = state.currentMode;
    baseContext.ocp_version = state.currentOcpVersion;
    baseContext.selected_draft_ids = helpers.selectedDraftIdList();
    baseContext.restrict_uploaded_sources = true;
    refs.sessionContextEl.textContent = JSON.stringify(baseContext, null, 2);
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
      lines.push(`${key}: ${Array.isArray(value) ? value.join(", ") : String(value)}`);
    });
    return lines.join("\n");
  }

  function pipelineProgressPercent() {
    const traceEvents = state.traceEvents || [];
    if (!traceEvents.length) {
      return state.generating ? 8 : 0;
    }
    const seenSteps = new Set(traceEvents.map((event) => event.step).filter(Boolean));
    const completed = helpers.pipelineStageOrder.filter((step) => seenSteps.has(step)).length;
    const percent = Math.round((completed / helpers.pipelineStageOrder.length) * 100);
    if (state.generating) {
      return Math.max(12, Math.min(94, percent || 16));
    }
    return Math.max(0, Math.min(100, percent || 100));
  }

  function resetPipelineTrace() {
    state.traceEvents = [];
    refs.pipelineLiveEl.innerHTML = '<div class="trace-empty">질문을 보내면 현재 단계와 진행 상황이 여기에 표시됩니다.</div>';
    refs.searchMetricsEl.innerHTML = '<div class="trace-empty">질문을 보내면 BM25, Vector, Hybrid 점수가 표시됩니다.</div>';
    refs.pipelineSummaryEl.innerHTML = '<div class="trace-empty">아직 실행 기록이 없습니다.</div>';
    refs.pipelineTraceEl.innerHTML = '<div class="trace-empty">아직 실행 기록이 없습니다.</div>';
  }

  function renderSearchMetrics() {
    const metricEvents = new Map();
    (state.traceEvents || []).forEach((event) => {
      if (!event || !event.step) return;
      if (["bm25_search", "vector_search", "fusion"].includes(event.step)) {
        metricEvents.set(event.step, event);
      }
    });

    if (!metricEvents.size) {
      refs.searchMetricsEl.innerHTML = state.generating
        ? '<div class="trace-empty">검색 지표를 계산하는 중입니다.</div>'
        : '<div class="trace-empty">질문을 보내면 BM25, Vector, Hybrid 점수가 표시됩니다.</div>';
      return;
    }

    refs.searchMetricsEl.innerHTML = "";
    [
      ["bm25_search", "BM25"],
      ["vector_search", "Vector"],
      ["fusion", "Hybrid"],
    ].forEach(([step, label]) => {
      const event = metricEvents.get(step);
      if (!event) return;
      const card = document.createElement("div");
      card.className = `metric-card ${step === "fusion" ? "metric-hybrid" : "metric-selected"}`.trim();

      const kicker = document.createElement("div");
      kicker.className = "metric-label";
      kicker.textContent = label;

      const value = document.createElement("div");
      value.className = "metric-value";
      value.textContent = event.duration_ms
        ? helpers.formatDuration(event.duration_ms)
        : (event.status === "running" ? "..." : "-");

      const detail = document.createElement("div");
      detail.className = "metric-detail";
      detail.textContent = event.detail || summarizeTraceMeta(event.meta) || humanizePipelineKey(step);

      card.append(kicker, value, detail);
      refs.searchMetricsEl.appendChild(card);
    });
  }

  function renderPipelineLive() {
    const traceEvents = state.traceEvents || [];
    if (!traceEvents.length) {
      refs.pipelineLiveEl.innerHTML = state.generating
        ? '<div class="trace-empty">질문을 받아 파이프라인을 준비하는 중입니다.</div>'
        : '<div class="trace-empty">질문을 보내면 현재 단계와 진행 상황이 여기에 표시됩니다.</div>';
      return;
    }

    const latestEvent = traceEvents[traceEvents.length - 1];
    const runningEvent = [...traceEvents].reverse().find((event) => event.status === "running") || latestEvent;
    const liveStage = runningEvent || latestEvent;
    const seenSteps = new Set(traceEvents.map((event) => event.step).filter(Boolean));
    const currentStep = liveStage && liveStage.step ? liveStage.step : "";
    const progress = pipelineProgressPercent();

    const panel = document.createElement("div");
    panel.className = "pending-panel";

    const kicker = document.createElement("div");
    kicker.className = "pending-kicker";
    kicker.textContent = state.generating ? "Live Pipeline" : "최근 파이프라인";

    const stage = document.createElement("div");
    stage.className = `pending-stage ${state.generating ? "live" : ""}`.trim();
    stage.textContent = liveStage && (liveStage.label || humanizePipelineKey(liveStage.step))
      ? (liveStage.label || humanizePipelineKey(liveStage.step))
      : (state.generating ? "응답을 준비하는 중" : "파이프라인 완료");

    const detail = document.createElement("div");
    detail.className = "pending-detail";
    detail.textContent = liveStage && liveStage.detail
      ? liveStage.detail
      : (state.generating
        ? "질문 정리, 검색, context 조립, 답변 생성 흐름을 순서대로 진행하고 있습니다."
        : "가장 최근 실행된 단계 기록입니다.");

    const rail = document.createElement("div");
    rail.className = "progress-rail";

    const fill = document.createElement("div");
    fill.className = `progress-fill ${state.generating ? "live" : ""}`.trim();
    fill.style.width = `${progress}%`;
    rail.appendChild(fill);

    const strip = document.createElement("div");
    strip.className = "stage-strip";
    helpers.pipelineStageOrder.forEach((stepKey) => {
      const chip = document.createElement("span");
      chip.className = "stage-chip pending";
      chip.textContent = humanizePipelineKey(stepKey);
      if (seenSteps.has(stepKey)) {
        chip.classList.remove("pending");
        chip.classList.add(stepKey === currentStep && state.generating ? "running" : "done");
      } else if (stepKey === currentStep && state.generating) {
        chip.classList.remove("pending");
        chip.classList.add("running");
      }
      strip.appendChild(chip);
    });

    panel.append(kicker, stage, detail, rail, strip);
    refs.pipelineLiveEl.innerHTML = "";
    refs.pipelineLiveEl.appendChild(panel);
  }

  function renderPipelineSummary(trace) {
    const timings = trace && trace.timings_ms ? trace.timings_ms : null;
    if (!timings || !Object.keys(timings).length) {
      refs.pipelineSummaryEl.innerHTML = '<div class="trace-empty">아직 실행 기록이 없습니다.</div>';
      return;
    }

    const bottleneckEntry = Object.entries(timings)
      .filter(([key]) => key !== "total")
      .sort((a, b) => (b[1] || 0) - (a[1] || 0))[0];

    const cards = [
      {
        label: "총 응답",
        value: helpers.formatDuration(timings.total || 0),
        detail: "질문 입력부터 답변 완료까지",
      },
      {
        label: "검색",
        value: helpers.formatDuration(timings.retrieval_total || 0),
        detail: `BM25 ${helpers.formatDuration(timings.bm25_search || 0)} · Vector ${helpers.formatDuration(timings.vector_search || 0)}`,
      },
      {
        label: "LLM 생성",
        value: helpers.formatDuration(timings.llm_generate_total || 0),
        detail: "모델 응답 생성 시간",
      },
      {
        label: "병목",
        value: bottleneckEntry ? helpers.formatDuration(bottleneckEntry[1] || 0) : "-",
        detail: bottleneckEntry ? humanizePipelineKey(bottleneckEntry[0]) : "아직 계산 전",
        className: "bottleneck",
      },
    ];

    refs.pipelineSummaryEl.innerHTML = "";
    cards.forEach((card) => {
      const node = document.createElement("div");
      node.className = `summary-card ${card.className || ""}`.trim();

      const kicker = document.createElement("div");
      kicker.className = "summary-kicker";
      kicker.textContent = card.label;

      const value = document.createElement("div");
      value.className = "summary-value";
      value.textContent = card.value;

      const detail = document.createElement("div");
      detail.className = "summary-detail";
      detail.textContent = card.detail;

      node.append(kicker, value, detail);
      refs.pipelineSummaryEl.appendChild(node);
    });
  }

  function renderPipelineTrace() {
    const traceEvents = state.traceEvents || [];
    if (!traceEvents.length) {
      refs.pipelineTraceEl.innerHTML = '<div class="trace-empty">아직 실행 기록이 없습니다.</div>';
      return;
    }

    refs.pipelineTraceEl.innerHTML = "";
    traceEvents.forEach((event, index) => {
      const card = document.createElement("div");
      card.className = `trace-item ${event.status || "info"}`;

      const headline = document.createElement("div");
      headline.className = "trace-headline";

      const step = document.createElement("div");
      step.className = "trace-step";
      step.textContent = String(index + 1).padStart(2, "0");

      const title = document.createElement("div");
      title.className = "trace-title";

      const label = document.createElement("span");
      label.textContent = event.label || humanizePipelineKey(event.step) || "trace";

      const duration = document.createElement("span");
      duration.className = "trace-duration";
      duration.textContent = event.duration_ms ? helpers.formatDuration(event.duration_ms) : "";

      title.append(label, duration);
      headline.append(step, title);
      card.appendChild(headline);

      if (event.detail) {
        const detail = document.createElement("div");
        detail.className = "trace-detail";
        detail.textContent = event.detail;
        card.appendChild(detail);
      }

      const metaParts = [];
      if (typeof event.timestamp_ms === "number") {
        metaParts.push(`t+${helpers.formatDuration(event.timestamp_ms)}`);
      }
      if (event.meta && Object.keys(event.meta).length) {
        metaParts.push(summarizeTraceMeta(event.meta));
      }
      if (metaParts.length) {
        const meta = document.createElement("div");
        meta.className = "trace-meta";
        meta.textContent = metaParts.join(" · ");
        card.appendChild(meta);
      }

      refs.pipelineTraceEl.appendChild(card);
    });
    refs.pipelineTraceEl.scrollTop = refs.pipelineTraceEl.scrollHeight;
    renderPipelineLive();
    renderSearchMetrics();
  }

  function appendTraceEvent(event) {
    state.traceEvents = [...(state.traceEvents || []), event];
    renderPipelineTrace();
    const detailParts = [];
    if (event.detail) detailParts.push(event.detail);
    if (event.duration_ms) detailParts.push(helpers.formatDuration(event.duration_ms));
    setStatus(event.label || "처리 중", {
      live: event.status === "running",
      detail: detailParts.join(" · "),
    });
  }

  function updateSidePanel(payload) {
    refs.rewrittenQueryEl.textContent = payload.rewritten_query || "-";
    updateSessionContextDisplay(payload.context || {});
    refs.warningsEl.textContent = payload.warnings && payload.warnings.length
      ? payload.warnings.join("\n")
      : "없음";
    renderPipelineSummary(payload.pipeline_trace || {});
  }

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
