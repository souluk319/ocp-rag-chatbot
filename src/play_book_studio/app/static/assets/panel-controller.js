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

  function setSourceLink(anchor, href) {
    if (!href) {
      anchor.hidden = true;
      anchor.removeAttribute("href");
      return;
    }
    anchor.hidden = false;
    anchor.href = href;
  }

  function resetSourcePanel() {
    state.activeSourceKey = "";
    refs.sourceTitleEl.textContent = "근거 문서를 선택하세요";
    refs.sourcePathEl.textContent = "답변 속 번호를 누르면 여기서 바로 확인합니다.";
    refs.sourceNoteEl.textContent = "핵심 구간과 원문 링크를 함께 보여줍니다.";
    refs.sourceSummaryStripEl.innerHTML = "";
    refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">문서를 열면 핵심 구간이 여기에 표시됩니다.</div>';
    setSourceLink(refs.sourceOpenDocEl, "");
    setSourceLink(refs.sourceOpenOriginEl, "");
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

  async function fetchSourceBook(viewerPath) {
    const response = await fetch(`/api/source-book?viewer_path=${encodeURIComponent(viewerPath)}`);
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.error || "source book을 불러오지 못했습니다.");
    }
    return response.json();
  }

  function renderSourceBook(book, targetAnchor = "") {
    const sections = Array.isArray(book && book.sections) ? book.sections : [];
    refs.sourceSummaryStripEl.innerHTML = "";

    [
      book && book.source_collection ? helpers.humanizeSourceCollection(book.source_collection) : "자료군 미확인",
      book && book.pack_label ? book.pack_label : "묶음 미확인",
      helpers.formatInferredScope(book),
      `${sections.length}개 섹션`,
      book && book.canonical_model ? helpers.humanizeDraftValue(book.canonical_model) : "정리본",
      book && book.source_view_strategy ? helpers.humanizeDraftValue(book.source_view_strategy) : "정리 보기",
    ].forEach((label) => {
      refs.sourceSummaryStripEl.appendChild(helpers.createSummaryChip(label));
    });

    if (!sections.length) {
      refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">핵심 구간을 아직 만들지 못했습니다.</div>';
      return;
    }

    const outline = sections.slice(0, 5);
    refs.sourceOutlineEl.innerHTML = "";
    outline.forEach((section, index) => {
      const item = document.createElement("section");
      item.className = `source-outline-item ${section.anchor === targetAnchor ? "active" : ""}`.trim();

      const kicker = document.createElement("div");
      kicker.className = "source-outline-kicker";
      kicker.textContent = `섹션 ${index + 1}`;

      const label = document.createElement("div");
      label.className = "source-outline-label";
      label.textContent = section.section_path_label || section.heading || section.section_key || "이름 없는 섹션";

      item.append(kicker, label);
      refs.sourceOutlineEl.appendChild(item);
    });
  }

  function applySourcePanelState(citation, meta = null) {
    const bookTitle = meta && meta.book_title
      ? meta.book_title
      : citation.book_title || citation.book_slug || "근거 문서";
    const sectionLabel = meta && meta.section_path_label
      ? meta.section_path_label
      : citation.section_path_label || citation.section || citation.anchor || "문서 전체";
    const excerpt = (citation.excerpt || "").trim();
    const packLine = [
      meta && meta.source_collection ? helpers.humanizeSourceCollection(meta.source_collection) : "",
      meta && meta.pack_label ? meta.pack_label : "",
      helpers.formatInferredScope(meta || citation),
    ].filter(Boolean).join(" · ");
    const qualityLine = meta && helpers.qualityStatusLabel(meta)
      ? `${helpers.qualityStatusLabel(meta)}${helpers.qualitySummaryText(meta) ? ` · ${helpers.qualitySummaryText(meta)}` : ""}`
      : "";
    const sectionMatchLine = meta && meta.section_match_exact === false
      ? "정확한 섹션 anchor를 찾지 못해 문서 첫 section 기준으로 열었습니다."
      : "";

    refs.sourceTitleEl.textContent = bookTitle;
    refs.sourcePathEl.textContent = sectionLabel;
    refs.sourceNoteEl.textContent = excerpt
      ? ([packLine, qualityLine, sectionMatchLine, excerpt].filter(Boolean).join("\n"))
      : ([packLine, qualityLine, sectionMatchLine].filter(Boolean).join("\n") || "선택한 참조의 관련 구간을 이 패널에서 확인할 수 있습니다.");
    setSourceLink(
      refs.sourceOpenDocEl,
      (meta && meta.viewer_path) || citation.viewer_path || citation.href || "",
    );
    setSourceLink(refs.sourceOpenOriginEl, (meta && meta.source_url) || citation.source_url || "");
  }

  async function openSourcePanel(citation) {
    if (!citation) return;

    state.activeSourceKey = sourceKeyFor(citation);
    syncActiveSourceTags();
    setSourcePanelVisible(true);
    callbacks.setStudyTab("source");
    applySourcePanelState(citation);

    const href = citation.href || "";
    const viewerPath = citation.viewer_path
      || ((href.startsWith("/docs/") || (!href.startsWith("http") && href.length > 0)) ? href : "");
    const viewerHref = viewerPath
      ? (viewerPath.startsWith("/docs/") ? viewerPath : `/docs/${viewerPath}`)
      : "";

    if (viewerHref) {
      refs.sourceFrameShellEl.hidden = false;
      refs.sourceViewerFrameEl.hidden = false;
      callbacks.setSourceFrameLoading(true);
      refs.sourceViewerFrameEl.src = viewerHref;
    } else {
      refs.sourcePathEl.textContent = "뷰어를 바로 열 수 없습니다.";
      refs.sourceNoteEl.textContent = "이 항목은 원문 링크만 제공합니다.";
      refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">문서 뷰어가 없는 항목이라 원문 링크로만 확인할 수 있습니다.</div>';
      setSourceEmptyState();
    }

    if (!viewerPath) return;

    try {
      const meta = await fetchSourceMeta(viewerPath);
      if (state.activeSourceKey !== sourceKeyFor(citation)) return;
      applySourcePanelState(citation, meta);
      if (helpers.isReviewNeeded(meta)) {
        setSourceLink(refs.sourceOpenDocEl, "");
        refs.sourcePathEl.textContent = "정규화 검토 필요";
        refs.sourceNoteEl.textContent = helpers.qualitySummaryText(meta) || "이 자료는 아직 원문 기준으로 먼저 확인해야 합니다.";
        refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">검토가 끝나면 핵심 구간이 열립니다.</div>';
        setSourceEmptyState();
        return;
      }
    } catch (error) {
      if (state.activeSourceKey !== sourceKeyFor(citation)) return;
      refs.sourceNoteEl.textContent = citation.excerpt || (error.message || "source metadata를 불러오지 못했습니다.");
    }

    try {
      const book = await fetchSourceBook(viewerPath);
      if (state.activeSourceKey !== sourceKeyFor(citation)) return;
      renderSourceBook(book, book.target_anchor || citation.anchor || "");
    } catch (error) {
      if (state.activeSourceKey !== sourceKeyFor(citation)) return;
      refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">핵심 구간을 불러오지 못했습니다.</div>';
    }
  }

  return {
    citationMapByIndex,
    fetchSourceBook,
    fetchSourceMeta,
    inlineCitationLabel,
    openSourcePanel,
    renderSourceBook,
    resetSourcePanel,
    setLeftPanelVisible,
    setSourceEmptyState,
    setSourceLink,
    setSourcePanelVisible,
    sourceKeyFor,
    syncActiveSourceTags,
  };
};
