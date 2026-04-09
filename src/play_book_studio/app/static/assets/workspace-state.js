// 코어 팩 선택, 자료 선택 상태, 보관함/최근 초안 목록 렌더링을 담당하는 프론트 helper다.
window.createWorkspaceState = function createWorkspaceState(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const constants = deps.constants;
  const helpers = deps.helpers;
  const callbacks = deps.callbacks;

  function renderCorePackOptions() {
    if (!refs.packStackEl) return [];
    refs.packStackEl.innerHTML = constants.corePacks.map((pack) => `
        <button type="button" class="core-pack-tab" data-pack-version="${pack.version}" data-pack-label="${pack.label || pack.version}">
          <span class="core-pack-tab-dot" aria-hidden="true"></span>
          <span class="core-pack-tab-copy">
            <strong>${pack.label || pack.version}</strong>
          </span>
          <span class="core-pack-tab-state">${pack.inactiveState || "선택"}</span>
        </button>
      `).join("");
    const nextButtons = Array.from(refs.packStackEl.querySelectorAll("[data-pack-version]"));
    state.packButtons = nextButtons;
    return nextButtons;
  }

  function selectedDraftIdList() {
    return Array.from(state.selectedDraftIds).sort();
  }

  function setRailUploadStatus(message, tone = "muted") {
    if (!refs.railUploadStatusEl) return;
    refs.railUploadStatusEl.textContent = message || "자료 추가 대기";
    refs.railUploadStatusEl.dataset.tone = tone;
  }

  function syncSelectableDraftIds(drafts) {
    const nextIds = new Set(
      (Array.isArray(drafts) ? drafts : [])
        .map((draft) => String(draft && draft.draft_id ? draft.draft_id : "").trim())
        .filter(Boolean),
    );
    Array.from(state.selectedDraftIds).forEach((draftId) => {
      if (!nextIds.has(draftId)) {
        state.selectedDraftIds.delete(draftId);
      }
    });
    state.knownSelectableDraftIds = nextIds;
  }

  function syncSourceSelectionSummary(totalReady = state.knownSelectableDraftIds.size) {
    if (!refs.selectedSourceCountEl) return;
    const selectedCount = state.selectedDraftIds.size;
    if (!totalReady) {
      refs.selectedSourceCountEl.textContent = "기본만";
      return;
    }
    refs.selectedSourceCountEl.textContent = selectedCount ? `기본 + ${selectedCount}` : "기본만";
  }

  function createSummaryCard(label, value, detail) {
    const card = document.createElement("div");
    card.className = "summary-card";

    const kicker = document.createElement("div");
    kicker.className = "summary-kicker";
    kicker.textContent = label;

    const valueEl = document.createElement("div");
    valueEl.className = "summary-value";
    valueEl.textContent = value;

    const detailEl = document.createElement("div");
    detailEl.className = "summary-detail";
    detailEl.textContent = detail;

    card.append(kicker, valueEl, detailEl);
    return card;
  }

  function draftStateLabel(draft) {
    if (draft.normalize_error) return "정리 오류";
    if (draft.capture_error) return "수집 오류";
    if (Number(draft.normalized_section_count || 0) > 0) return "준비됨";
    if (draft.canonical_book_path) return "정리 완료";
    if (draft.capture_artifact_path) return "수집 완료";
    return draft.status || "초안";
  }

  function draftMetaText(draft) {
    const parts = [
      draft.pack_label || "업로드 묶음",
      helpers.humanizeSourceCollection(draft.source_collection),
      draft.source_type || "-",
      Number(draft.normalized_section_count || 0) > 0
        ? `${draft.normalized_section_count}개 섹션`
        : helpers.qualityStatusLabel(draft) || draftStateLabel(draft),
    ].filter(Boolean);
    return parts.join(" · ");
  }

  function draftDetailText(draft) {
    const qualitySummary = helpers.qualitySummaryText(draft);
    if (qualitySummary) return qualitySummary;
    if (draft.source_uri) return draft.source_uri;
    return draft.book_slug || "-";
  }

  function createActionButton(label, onClick, className = "ghost-btn", disabled = false) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = label;
    button.disabled = disabled;
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      void onClick();
    });
    return button;
  }

  function createDraftCard(draft, options = {}) {
    const {
      active = false,
      compact = false,
      inspectLabel = "보기",
    } = options;

    const article = document.createElement("article");
    article.className = "draft-card";
    if (active) article.classList.add("active");

    const head = document.createElement("div");
    head.className = "draft-card-head";

    const copy = document.createElement("div");
    const title = document.createElement("div");
    title.className = "draft-card-title";
    title.textContent = draft.title || draft.book_slug || draft.draft_id;

    const meta = document.createElement("div");
    meta.className = "draft-card-meta";
    meta.textContent = `${draftMetaText(draft)}\n${draftDetailText(draft)}`;
    copy.append(title, meta);

    const selectionButton = createActionButton(
      state.selectedDraftIds.has(draft.draft_id) ? "해제" : "추가",
      () => {
        setUploadedDraftSelected(draft.draft_id, !state.selectedDraftIds.has(draft.draft_id));
      },
      "ghost-btn",
      !state.knownSelectableDraftIds.has(draft.draft_id),
    );
    head.append(copy, selectionButton);

    const actions = document.createElement("div");
    actions.className = "draft-card-actions";
    actions.appendChild(
      createActionButton(inspectLabel, () => callbacks.openLibraryTrace(draft.draft_id)),
    );

    const canOpenAsset = !helpers.isReviewNeeded(draft) && Number(draft.normalized_section_count || 0) > 0;
    actions.appendChild(
      createActionButton(
        "참조",
        () => callbacks.openLibraryAsset(draft.draft_id),
        "ghost-btn",
        !canOpenAsset,
      ),
    );

    if (!compact) {
      actions.appendChild(
        createActionButton(
          "불러오기",
          () => callbacks.openDocToBookDraft(draft.draft_id),
        ),
      );
    }

    article.append(head, actions);
    article.addEventListener("click", () => {
      void callbacks.openLibraryTrace(draft.draft_id);
    });
    return article;
  }

  function renderDraftCollection(container, drafts, options = {}) {
    if (!container) return;
    const {
      activeId = "",
      compact = false,
      emptyText = "표시할 자료가 없습니다.",
    } = options;

    container.innerHTML = "";
    if (!Array.isArray(drafts) || !drafts.length) {
      const empty = document.createElement("div");
      empty.className = "trace-empty";
      empty.textContent = emptyText;
      container.appendChild(empty);
      return;
    }

    drafts.forEach((draft) => {
      container.appendChild(
        createDraftCard(draft, {
          active: draft.draft_id === activeId,
          compact,
          inspectLabel: compact ? "보기" : "흐름",
        }),
      );
    });
  }

  function renderLibrarySummary(drafts) {
    if (!refs.librarySummaryEl) return;
    refs.librarySummaryEl.innerHTML = "";
    if (!Array.isArray(drafts) || !drafts.length) {
      const empty = document.createElement("div");
      empty.className = "trace-empty";
      empty.textContent = "아직 정리된 문서 자산이 없습니다.";
      refs.librarySummaryEl.appendChild(empty);
      return;
    }

    const readyCount = drafts.filter((draft) => Number(draft.normalized_section_count || 0) > 0).length;
    const selectedCount = state.selectedDraftIds.size;
    const reviewCount = drafts.filter((draft) => helpers.isReviewNeeded(draft)).length;

    refs.librarySummaryEl.append(
      createSummaryCard("자료 수", `${drafts.length}개`, "업로드 후 정리된 자산 포함"),
      createSummaryCard("선택됨", `${selectedCount}개`, "기본 팩 외 추가 자료"),
      createSummaryCard("준비 완료", `${readyCount}개`, "참조로 바로 열 수 있는 문서"),
      createSummaryCard("검토 필요", `${reviewCount}개`, "정규 문서 검토가 남은 자산"),
    );
  }

  function renderDocToBookDrafts(payload, activeDraftId = "") {
    const drafts = Array.isArray(payload && payload.drafts) ? payload.drafts : [];
    state.docToBookDraftCache = drafts;
    if (activeDraftId) {
      state.activeLibraryDraftId = activeDraftId;
    }

    syncSelectableDraftIds(drafts);
    syncSourceSelectionSummary(drafts.length);
    renderLibrarySummary(drafts);

    const activeLibraryId = state.activeLibraryDraftId || state.activeIngestDraftId || activeDraftId;
    renderDraftCollection(refs.railLibraryListEl, drafts, {
      activeId: activeLibraryId,
      compact: true,
      emptyText: "정리된 자료가 여기에 표시됩니다.",
    });
    renderDraftCollection(refs.libraryListEl, drafts, {
      activeId: activeLibraryId,
      emptyText: "정리가 끝난 문서가 여기에 표시됩니다.",
    });
    renderDraftCollection(refs.ingestDraftListEl, drafts, {
      activeId: state.activeIngestDraftId || activeDraftId,
      emptyText: "아직 저장된 초안이 없습니다.",
    });
  }

  function setUploadedDraftSelected(draftId, checked) {
    const normalizedId = String(draftId || "").trim();
    if (!normalizedId) return;
    if (checked) {
      state.selectedDraftIds.add(normalizedId);
    } else {
      state.selectedDraftIds.delete(normalizedId);
    }
    syncSourceSelectionSummary();
    renderDocToBookDrafts({ drafts: state.docToBookDraftCache }, state.activeLibraryDraftId || state.activeIngestDraftId);
    if (callbacks.updateSessionContextDisplay) {
      callbacks.updateSessionContextDisplay();
    }
  }

  function registerReadyDraft(draftId) {
    const normalizedId = String(draftId || "").trim();
    if (!normalizedId) return;
    state.knownSelectableDraftIds.add(normalizedId);
    syncSourceSelectionSummary();
    if (callbacks.updateSessionContextDisplay) {
      callbacks.updateSessionContextDisplay();
    }
  }

  function setCorePack(version, label = "") {
    state.currentOcpVersion = version || state.currentOcpVersion || "4.20";
    state.packButtons.forEach((button) => {
      const isActive = button.dataset.packVersion === state.currentOcpVersion;
      button.classList.toggle("active", isActive);
    });
    const activeButton = state.packButtons.find((button) => button.dataset.packVersion === state.currentOcpVersion) || state.packButtons[0];
    const activePack = constants.corePacks.find((pack) => pack.version === state.currentOcpVersion) || constants.corePacks[0] || null;
    const activeLabel = label || (activeButton ? activeButton.dataset.packLabel : activePack?.label || state.currentOcpVersion);
    if (refs.versionChipEl) {
      refs.versionChipEl.textContent = `Pack · ${activeLabel}`;
    }
    if (refs.activePackTitleEl) {
      refs.activePackTitleEl.textContent = activeLabel;
    }
    if (refs.coreSourceSummaryEl) {
      refs.coreSourceSummaryEl.textContent = `${state.currentOcpVersion} · 기본 포함`;
    }
    state.packButtons.forEach((button) => {
      const stateEl = button.querySelector(".core-pack-tab-state");
      if (!stateEl) return;
      const pack = constants.corePacks.find((item) => item.version === button.dataset.packVersion);
      stateEl.textContent = button.dataset.packVersion === state.currentOcpVersion
        ? (pack?.activeState || "사용 중")
        : (pack?.inactiveState || "선택");
    });
    if (refs.coreVersionPickerEl) {
      refs.coreVersionPickerEl.open = false;
    }
    if (callbacks.updateSessionContextDisplay) {
      callbacks.updateSessionContextDisplay();
    }
  }

  function setStudyTab(tab) {
    const effectiveTab = "source";
    refs.studyTabButtons.forEach((button) => {
      button.classList.toggle("active", button.dataset.studyTab === effectiveTab);
    });
    refs.studyPages.forEach((page) => {
      page.classList.toggle("active", page.dataset.studyPage === effectiveTab);
    });
  }

  function bindEvents() {
    refs.studyTabButtons.forEach((button) => {
      button.addEventListener("click", () => setStudyTab(button.dataset.studyTab));
    });

    state.packButtons.forEach((button) => {
      button.addEventListener("click", () => {
        setCorePack(button.dataset.packVersion || "4.20", button.dataset.packLabel || "");
      });
    });
  }

  function initialize() {
    renderCorePackOptions();
    bindEvents();
    renderLibrarySummary([]);
    renderDraftCollection(refs.railLibraryListEl, [], {
      compact: true,
      emptyText: "정리된 자료가 여기에 표시됩니다.",
    });
    renderDraftCollection(refs.libraryListEl, [], {
      emptyText: "정리가 끝난 문서가 여기에 표시됩니다.",
    });
    renderDraftCollection(refs.ingestDraftListEl, [], {
      emptyText: "아직 저장된 초안이 없습니다.",
    });
  }

  return {
    initialize,
    registerReadyDraft,
    renderDocToBookDrafts,
    selectedDraftIdList,
    setCorePack,
    setRailUploadStatus,
    setStudyTab,
    setUploadedDraftSelected,
    syncSelectableDraftIds,
    syncSourceSelectionSummary,
  };
};
