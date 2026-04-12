window.createPanelController = function createPanelController(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const callbacks = deps.callbacks;

  function chevronIcon(direction) {
    const path = direction === "left"
      ? "M10 3.5 5.5 8 10 12.5"
      : "M6 3.5 10.5 8 6 12.5";
    return `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="${path}"></path></svg>`;
  }

  function nudgeWorkspace(direction) {
    if (state.layoutMotionTimer) {
      clearTimeout(state.layoutMotionTimer);
    }
    refs.shellEl.classList.remove("motion-nudge-left", "motion-nudge-right");
    if (direction !== "left" && direction !== "right") {
      return;
    }
    refs.shellEl.classList.add(direction === "left" ? "motion-nudge-left" : "motion-nudge-right");
    state.layoutMotionTimer = window.setTimeout(() => {
      refs.shellEl.classList.remove("motion-nudge-left", "motion-nudge-right");
      state.layoutMotionTimer = null;
    }, 320);
  }

  function setSourcePanelVisible(nextVisible) {
    nudgeWorkspace(nextVisible ? "left" : "right");
    state.sourcePanelVisible = nextVisible;
    refs.shellEl.classList.toggle("source-hidden", !nextVisible);
    refs.sourcePanelToggleBtn.innerHTML = chevronIcon("right");
    refs.sourcePanelToggleBtn.setAttribute("aria-label", nextVisible ? "참조 패널 닫기" : "참조 패널 열기");
    refs.sourcePanelToggleBtn.setAttribute("title", nextVisible ? "참조 패널 닫기" : "참조 패널 열기");
    refs.sourcePanelEdgeBtn.innerHTML = chevronIcon("left");
    refs.sourcePanelEdgeBtn.setAttribute("aria-label", nextVisible ? "참조 패널 닫기" : "참조 패널 열기");
    refs.sourcePanelEdgeBtn.setAttribute("title", nextVisible ? "참조 패널 닫기" : "참조 패널 열기");
  }

  function setLeftPanelVisible(nextVisible) {
    nudgeWorkspace(nextVisible ? "right" : "left");
    state.leftPanelVisible = nextVisible;
    refs.shellEl.classList.toggle("left-hidden", !nextVisible);
    refs.leftRailToggleBtn.innerHTML = chevronIcon("left");
    refs.leftRailToggleBtn.setAttribute("aria-label", nextVisible ? "왼쪽 패널 닫기" : "왼쪽 패널 열기");
    refs.leftRailToggleBtn.setAttribute("title", nextVisible ? "왼쪽 패널 닫기" : "왼쪽 패널 열기");
    refs.leftPanelToggleBtn.innerHTML = chevronIcon("right");
    refs.leftPanelToggleBtn.setAttribute("aria-label", nextVisible ? "왼쪽 패널 닫기" : "왼쪽 패널 열기");
    refs.leftPanelToggleBtn.setAttribute("title", nextVisible ? "왼쪽 패널 닫기" : "왼쪽 패널 열기");
  }

  function sourceKeyFor(citation) {
    return citation.viewer_path || citation.href || citation.source_url || `${citation.book_slug}-${citation.anchor}`;
  }

  function inlineCitationLabel(index) {
    const circled = ["", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩", "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳"];
    return circled[index] || `근${index}`;
  }

  function syncActiveSourceTags() {
    document.querySelectorAll(".source-tag, .inline-citation").forEach((button) => {
      button.classList.toggle("active", button.dataset.sourceKey === state.activeSourceKey);
    });
  }

  function citationMapByIndex(citations = []) {
    const mapped = new Map();
    citations.forEach((citation) => {
      if (citation && Number.isFinite(Number(citation.index))) {
        mapped.set(String(citation.index), citation);
      }
    });
    return mapped;
  }

  function setSourceEmptyState() {
    callbacks.setSourceFrameLoading(false);
    refs.sourceFrameShellEl.hidden = true;
    refs.sourceViewerFrameEl.hidden = true;
    refs.sourceViewerFrameEl.removeAttribute("src");
  }

  function buildEmbeddedViewerHref(viewerPath) {
    if (!viewerPath) {
      return "";
    }
    const basePath = viewerPath.startsWith("/docs/") ? viewerPath : `/docs/${viewerPath}`;
    const hashIndex = basePath.indexOf("#");
    const pathWithoutHash = hashIndex >= 0 ? basePath.slice(0, hashIndex) : basePath;
    const hash = hashIndex >= 0 ? basePath.slice(hashIndex) : "";
    const separator = pathWithoutHash.includes("?") ? "&" : "?";
    return `${pathWithoutHash}${separator}embed=1&_ts=${Date.now()}${hash}`;
  }

  function resetSourcePanel() {
    state.activeSourceKey = "";
    setSourceEmptyState();
    syncActiveSourceTags();
  }

  async function fetchSourceMeta(viewerPath) {
    const response = await fetch(`/api/source-meta?viewer_path=${encodeURIComponent(viewerPath)}`);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.error || "source metadata를 불러오지 못했습니다.");
    }
    return response.json();
  }

  async function openSourcePanel(citation) {
    if (!citation) return;

    state.activeSourceKey = sourceKeyFor(citation);
    syncActiveSourceTags();
    setSourcePanelVisible(true);

    const href = citation.href || "";
    const viewerPath = citation.viewer_path
      || ((href.startsWith("/docs/") || (!href.startsWith("http") && href.length > 0)) ? href : "");
    const viewerHref = buildEmbeddedViewerHref(viewerPath);

    if (viewerHref) {
      refs.sourceFrameShellEl.hidden = false;
      refs.sourceViewerFrameEl.hidden = false;
      callbacks.setSourceFrameLoading(true);
      refs.sourceViewerFrameEl.removeAttribute("src");
      refs.sourceViewerFrameEl.src = viewerHref;
    } else {
      setSourceEmptyState();
    }

    if (!viewerPath) return;

    try {
      const meta = await fetchSourceMeta(viewerPath);
      if (state.activeSourceKey !== sourceKeyFor(citation)) return;
      if (helpers.isReviewNeeded(meta)) {
        setSourceEmptyState();
        return;
      }
    } catch (error) {
      if (state.activeSourceKey !== sourceKeyFor(citation)) return;
    }
  }

  return {
    citationMapByIndex,
    fetchSourceMeta,
    inlineCitationLabel,
    openSourcePanel,
    resetSourcePanel,
    setLeftPanelVisible,
    setSourceEmptyState,
    setSourcePanelVisible,
    sourceKeyFor,
    syncActiveSourceTags,
  };
};
