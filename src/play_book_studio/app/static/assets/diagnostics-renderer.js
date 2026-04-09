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
    if (!refs.sessionContextEl) return;
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

  function formatMetricScore(value, digits = 4) {
    if (value === undefined || value === null || value === "") return "-";
    const numeric = Number(value);
    if (Number.isNaN(numeric)) return String(value);
    return numeric.toFixed(digits);
  }

  function summarizeMetricEvent(step, event) {
    const summary = event && event.meta && event.meta.summary ? event.meta.summary : null;
    const topHit = summary && Array.isArray(summary.top_hits) ? summary.top_hits[0] : null;
    const count = summary && typeof summary.count === "number" ? summary.count : null;
    const topScore = summary ? summary.top_score : null;
    const section = topHit && topHit.section ? topHit.section : "";

    if (step === "bm25_search") {
      return {
        label: "BM25",
        value: formatMetricScore(topScore),
        detail: [
          "키워드 일치 강도",
          count !== null ? `후보 ${count}개` : "",
          section ? `상위 근거: ${section}` : "",
        ].filter(Boolean).join("\n"),
      };
    }

    if (step === "vector_search") {
      return {
        label: "Vector",
        value: formatMetricScore(topScore),
        detail: [
          "문맥 의미 유사도",
          count !== null ? `후보 ${count}개` : "",
          section ? `상위 근거: ${section}` : "",
        ].filter(Boolean).join("\n"),
      };
    }

    const hybridParts = [];
    if (topHit && topHit.bm25_rank !== undefined) {
      hybridParts.push(`BM25 ${Math.round(Number(topHit.bm25_rank))}위`);
    }
    if (topHit && topHit.vector_rank !== undefined) {
      hybridParts.push(`Vector ${Math.round(Number(topHit.vector_rank))}위`);
    }

    return {
      label: "Hybrid",
      value: formatMetricScore(topScore),
      detail: [
        "BM25와 Vector를 함께 반영한 최종 결합 점수",
        hybridParts.length ? `결합 근거: ${hybridParts.join(" + ")}` : "",
        count !== null ? `후보 ${count}개` : "",
        section ? `상위 근거: ${section}` : "",
      ].filter(Boolean).join("\n"),
    };
  }

  function buildMetricCardsHtml(traceEvents) {
    const metricEvents = new Map();
    (traceEvents || []).forEach((event) => {
      if (!event || !event.step) return;
      if (["bm25_search", "vector_search", "fusion"].includes(event.step)) {
        metricEvents.set(event.step, event);
      }
    });
    if (!metricEvents.size) return "";

    const nodes = [];
    [
      ["bm25_search", "metric-selected"],
      ["vector_search", "metric-selected"],
      ["fusion", "metric-hybrid"],
    ].forEach(([step, klass]) => {
      const event = metricEvents.get(step);
      if (!event) return;
      const summary = summarizeMetricEvent(step, event);
      nodes.push(`
        <div class="metric-card ${klass}">
          <div class="metric-label">${summary.label}</div>
          <div class="metric-value">${summary.value}</div>
          <div class="metric-detail">${summary.detail}</div>
        </div>
      `);
    });
    if (!nodes.length) return "";
    return `<div class="metric-grid">${nodes.join("")}</div>`;
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
    if (refs.pipelineLiveEl) {
      refs.pipelineLiveEl.innerHTML = '<div class="trace-empty">질문을 보내면 현재 단계와 진행 상황이 여기에 표시됩니다.</div>';
    }
    if (refs.searchMetricsEl) {
      refs.searchMetricsEl.innerHTML = '<div class="trace-empty">질문을 보내면 BM25, Vector, Hybrid 점수가 표시됩니다.</div>';
    }
    if (refs.pipelineSummaryEl) {
      refs.pipelineSummaryEl.innerHTML = '<div class="trace-empty">아직 실행 기록이 없습니다.</div>';
    }
    if (refs.pipelineTraceEl) {
      refs.pipelineTraceEl.innerHTML = '<div class="trace-empty">아직 실행 기록이 없습니다.</div>';
    }
  }

  function renderSearchMetrics() {
    if (!refs.searchMetricsEl) return;
    const html = buildMetricCardsHtml(state.traceEvents || []);
    if (!html) {
      refs.searchMetricsEl.innerHTML = state.generating
        ? '<div class="trace-empty">검색 지표를 계산하는 중입니다.</div>'
        : '<div class="trace-empty">질문을 보내면 BM25, Vector, Hybrid 점수가 표시됩니다.</div>';
      return;
    }
    refs.searchMetricsEl.innerHTML = html;
  }

  function renderPipelineLive() {
    if (!refs.pipelineLiveEl) return;
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
    if (!refs.pipelineSummaryEl) return;
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
    if (!refs.pipelineTraceEl) {
      renderPipelineLive();
      renderSearchMetrics();
      return;
    }
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
    state.latestRetrievalTrace = payload.retrieval_trace || {};
    if (refs.rewrittenQueryEl) {
      refs.rewrittenQueryEl.textContent = payload.rewritten_query || "-";
    }
    updateSessionContextDisplay(payload.context || {});
    if (refs.warningsEl) {
      refs.warningsEl.textContent = payload.warnings && payload.warnings.length
        ? payload.warnings.join("\n")
        : "없음";
    }
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


// Friendly Trace logic injected for Left Rail
document.addEventListener("DOMContentLoaded", () => {
    // Right panel (if any remnants, just clear tabs)
    document.querySelectorAll('.trace-tab').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.trace-tab').forEach(b => {
                b.classList.remove('active');
                b.style.background = 'transparent';
                b.style.color = 'var(--muted)';
                b.style.boxShadow = 'none';
            });
            e.target.classList.add('active');
            e.target.style.background = 'white';
            e.target.style.color = 'var(--ink)';
            e.target.style.boxShadow = '0 1px 2px rgba(0,0,0,0.05)';
        });
    });

    // Left panel tabs
    const leftTabs = document.querySelectorAll('.trace-tab-left');
    leftTabs.forEach(btn => {
      btn.addEventListener('click', (e) => {
        leftTabs.forEach(b => {
           b.classList.remove('active');
           b.style.background = 'transparent';
           b.style.color = 'var(--muted)';
           b.style.boxShadow = 'none';
        });
        e.target.classList.add('active');
        e.target.style.background = 'white';
        e.target.style.color = 'var(--ink)';
        e.target.style.boxShadow = '0 1px 2px rgba(0,0,0,0.05)';
        
        const targetId = e.target.dataset.target;
        document.querySelectorAll('.left-rail-page').forEach(page => {
           if(page.dataset.railPage === targetId) {
               page.classList.add('active');
               page.style.display = targetId === 'library' ? 'flex' : 'block';
           } else {
               page.classList.remove('active');
               page.style.display = 'none';
           }
        });
      });
    });
});

window.renderFriendlyTrace = function(traceEvents, isLive, retrievalTrace) {
    const container = document.getElementById('friendly-stepper-container');
    if(!container) return;
    
    if(!traceEvents || traceEvents.length === 0) {
        container.innerHTML = '<div class="trace-empty" style="text-align: center; color: var(--muted); padding-top: 40px; font-size: 14px;">질문을 보내거나 말풍선을 클릭하면<br>상황실 모니터가 켜집니다.</div>';
        return;
    }
    
    // 친절한 매핑 사전에 있는 것만 유저에게 보여줌 (개발자용 자잘한 로그는 병합/무시)
    const friendlyMap = {
        'route_query': { title: '요청 접수', desc: '질문의 종류를 판별하고 있습니다.' },
        'rewrite_query': { title: '질문 분석', desc: '질문의 숨은 의도와 핵심 키워드를 파악합니다.' },
        'bm25_search': { title: '키워드 매칭', desc: '단어 단위로 흩어진 관련 문서를 긁어옵니다.' },
        'vector_search': { title: '의미 탐색', desc: '문맥상 비슷한 의미를 가진 공식 문서를 찾습니다.' },
        'fusion': { title: '하이브리드 병합', desc: 'BM25와 Vector 결과를 수학적으로 결합합니다.' },
        'rerank': { title: '문맥 재정렬 (AI 리랭킹)', desc: 'AI 모델이 문서의 문맥을 깊이 분석하여 진짜 정답을 최상위로 끌어올립니다.' },
        'query_reranking': { title: '문맥 재정렬 (AI 리랭킹)', desc: 'AI 모델이 문서의 문맥을 깊이 분석하여 진짜 정답을 최상위로 끌어올립니다.' },
        'llm_generate': { title: '답변 작성 중', desc: '최상위 문서들을 바탕으로 답변을 서술합니다.' },
        'pipeline_complete': { title: '임무 완료', desc: '모든 분석과 답변 작성을 무사히 마쳤습니다.' }
    };
    
    const formatMetricScore = (value, digits = 4) => {
        if (value === undefined || value === null || value === "") return "-";
        const numeric = Number(value);
        if (Number.isNaN(numeric)) return String(value);
        return numeric.toFixed(digits);
    };

    const metricEvents = new Map();
    traceEvents.forEach(ev => {
        if (ev && ["bm25_search", "vector_search", "fusion"].includes(ev.step)) {
            metricEvents.set(ev.step, ev);
        }
    });

    let html = '';
    const rerankerEnabled = Boolean(retrievalTrace && retrievalTrace.reranker && retrievalTrace.reranker.enabled);
    const customBm25Count = retrievalTrace && retrievalTrace.metrics && retrievalTrace.metrics.custom_bm25
        ? Number(retrievalTrace.metrics.custom_bm25.count || 0)
        : 0;
    html += `
        <div class="trace-runtime-status">
            BM25 <strong>on</strong>
            <span>·</span>
            Vector <strong>${metricEvents.has("vector_search") ? "on" : "off"}</strong>
            <span>·</span>
            Hybrid <strong>${metricEvents.has("fusion") ? "on" : "off"}</strong>
            <span>·</span>
            Reranker <strong>${rerankerEnabled ? "on" : "off"}</strong>
            <span>·</span>
            Custom BM25 <strong>${customBm25Count > 0 ? "on" : "off"}</strong>
        </div>
    `;

    if (metricEvents.size) {
        const metricHtml = [];
        [
            ["bm25_search", "BM25", "키워드 일치 강도", "metric-selected"],
            ["vector_search", "Vector", "문맥 의미 유사도", "metric-selected"],
            ["fusion", "Hybrid", "BM25와 Vector를 결합한 최종 점수", "metric-hybrid"],
        ].forEach(([step, label, meaning, klass]) => {
            const ev = metricEvents.get(step);
            if (!ev) return;
            const summary = ev.meta && ev.meta.summary ? ev.meta.summary : null;
            const topHit = summary && Array.isArray(summary.top_hits) ? summary.top_hits[0] : null;
            const detailParts = [meaning];
            if (summary && typeof summary.count === "number") detailParts.push(`후보 ${summary.count}개`);
            if (step === "fusion" && topHit) {
                const fusedFrom = [];
                if (topHit.bm25_rank !== undefined) fusedFrom.push(`BM25 ${Math.round(Number(topHit.bm25_rank))}위`);
                if (topHit.vector_rank !== undefined) fusedFrom.push(`Vector ${Math.round(Number(topHit.vector_rank))}위`);
                if (fusedFrom.length) detailParts.push(`결합 근거: ${fusedFrom.join(" + ")}`);
            }
            if (topHit && topHit.section) detailParts.push(`상위 근거: ${String(topHit.section).slice(0, 46)}${String(topHit.section).length > 46 ? "…" : ""}`);
            metricHtml.push(`
                <div class="metric-card ${klass} metric-card-compact">
                    <div class="metric-label">${label}</div>
                    <div class="metric-value">${formatMetricScore(summary ? summary.top_score : null)}</div>
                    <div class="metric-detail">${detailParts.join("<br>")}</div>
                </div>
            `);
        });
        if (metricHtml.length) {
            html += `<div class="metric-grid" style="margin-bottom: 14px;">${metricHtml.join("")}</div>`;
        }
    }

    html += '<div class="friendly-stepper">';
    
    // 중복 제거 및 최신 상태 갱신을 위한 Map
    const stepMap = new Map();
    
    // 원본 이벤트들을 순회하면서 우리가 보여줄 굵직한 단계만 솎아냄
    traceEvents.forEach(ev => {
        let key = ev.step || '';
        
        // 특정 마이크로 스텝을 메인 스텝으로 병합 처리
        if (key === 'normalize_query') key = 'rewrite_query';
        if (key === 'context_assembly' || key === 'prompt_build') key = 'llm_generate';
        if (key === 'citation_finalize') key = 'pipeline_complete';
        
        // 매핑 사전에 없는 잡다한 기술적 스텝은 무시
        if (!friendlyMap[key]) return;
        
        let status = ev.status === 'running' ? 'running' : (ev.status === 'error' ? 'error' : 'done');
        let detail = ev.detail ? ev.detail : friendlyMap[key].desc;
        
        // 메타데이터(가중치/비율 등)가 있으면 추가로 표시
        if (ev.meta) {
            let metaArr = [];
            // 하이브리드 단계의 주요 메타데이터만 간단히 보여준다.
            if (ev.meta.hits) metaArr.push(`가져온 문단: ${ev.meta.hits}개`);
            if (ev.meta.selected) metaArr.push(`최종 선정: ${ev.meta.selected}개`);
            if (ev.meta.provider) metaArr.push(`AI 모델: ${ev.meta.model}`);
            
            // 그 외 잡다한 메타데이터 (보여줄 필요 없는 것 제외)
            for (let k in ev.meta) {
                if (!['alpha', 'hits', 'selected', 'provider', 'model', 'summary'].includes(k) && typeof ev.meta[k] !== 'object') {
                    metaArr.push(`${k}: ${ev.meta[k]}`);
                }
            }
            
            if (metaArr.length > 0) {
                detail += `<br><span class="stepper-meta-chip">📊 ${metaArr.join(' | ')}</span>`;
            }
        }
        
        // 기존 상태 업데이트 (최신 상태로 덮어쓰기)
        stepMap.set(key, {
            title: friendlyMap[key].title,
            desc: detail,
            status: status
        });
    });
    
    // Map을 배열로 변환해서 HTML 구성
    Array.from(stepMap.values()).forEach((step) => {
        let iconHtml = step.status === 'done' ? '✓' : (step.status === 'error' ? '!' : '⋯');
        html += `
            <div class="stepper-item ${step.status}">
                <div class="stepper-icon">${iconHtml}</div>
                <div class="stepper-title">${step.title}</div>
                <div class="stepper-detail">${step.desc}</div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
};

// Check if monkey patch already done
if (!window._origCreateDiagnosticsRenderer) {
    window._origCreateDiagnosticsRenderer = window.createDiagnosticsRenderer;
    window.createDiagnosticsRenderer = function(deps) {
        const inst = window._origCreateDiagnosticsRenderer(deps);
        const origAppend = inst.appendTraceEvent;
        inst.appendTraceEvent = function(event) {
            origAppend(event);
            window.renderFriendlyTrace(deps.state.traceEvents, true, deps.state.latestRetrievalTrace);
        };
        const origUpdateSidePanel = inst.updateSidePanel;
        inst.updateSidePanel = function(payload) {
            origUpdateSidePanel(payload);
            if(payload.pipeline_trace && payload.pipeline_trace.events) {
                window.renderFriendlyTrace(payload.pipeline_trace.events, false, payload.retrieval_trace || deps.state.latestRetrievalTrace);
            }
        };
        return inst;
    };
}
