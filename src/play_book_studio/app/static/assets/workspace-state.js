// 코어 팩 선택과 기본 runtime 컨텍스트만 다루는 최소 workspace 상태 모듈이다.
window.createWorkspaceState = function createWorkspaceState(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const constants = deps.constants;
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

  function renderTopicPlaybooks(playbooks) {
    if (!refs.topicPlaybookListEl) return;
    const rows = Array.isArray(playbooks) ? playbooks.filter((item) => item && typeof item === "object") : [];
    if (!rows.length) {
      refs.topicPlaybookListEl.innerHTML = '<div class="trace-empty rail-inline-empty">토픽 플레이북이 아직 없습니다.</div>';
      if (refs.topicPlaybookSummaryEl) {
        refs.topicPlaybookSummaryEl.textContent = "토픽 플레이북 0개";
      }
      return;
    }
    refs.topicPlaybookListEl.innerHTML = rows.map((book) => {
      const title = String(book.title || book.book_slug || "Untitled");
      const sectionCount = Number(book.section_count || 0);
      const sourceLane = String(book.source_lane || "").trim();
      const meta = [sourceLane, sectionCount ? `섹션 ${sectionCount}` : ""].filter(Boolean).join(" · ");
      return `
        <article class="rail-metric-card">
          <span>Topic Playbook</span>
          <strong>${title}</strong>
          <p>${meta || "실행형 토픽 플레이북"}</p>
        </article>
      `;
    }).join("");
    if (refs.topicPlaybookSummaryEl) {
      refs.topicPlaybookSummaryEl.textContent = `토픽 플레이북 ${rows.length}개`;
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

  function hydrateFromDataControlRoom(payload) {
    const activePack = payload && typeof payload === "object" ? payload.active_pack || {} : {};
    const summary = payload && typeof payload === "object" ? payload.summary || {} : {};
    const topicSection = payload && typeof payload === "object" ? payload.topic_playbooks || {} : {};
    const nextVersion = String(activePack.ocp_version || state.currentOcpVersion || "4.20");
    const nextLabel = String(activePack.pack_label || activePack.ocp_version || nextVersion);
    setCorePack(nextVersion, nextLabel);
    if (refs.coreSourceSummaryEl) {
      const manualCount = Number(summary.manualbook_count || summary.gold_book_count || 0);
      const topicCount = Number(summary.topic_playbook_count || 0);
      const parts = [nextVersion];
      if (manualCount) {
        parts.push(`manual ${manualCount}`);
      }
      parts.push(`topic ${topicCount}`);
      refs.coreSourceSummaryEl.textContent = parts.join(" · ");
    }
    renderTopicPlaybooks(topicSection.books || []);
  }

  function bindEvents() {
    state.packButtons.forEach((button) => {
      button.addEventListener("click", () => {
        setCorePack(button.dataset.packVersion || "4.20", button.dataset.packLabel || "");
      });
    });
  }

  function initialize() {
    renderCorePackOptions();
    bindEvents();
  }

  return {
    hydrateFromDataControlRoom,
    initialize,
    setCorePack,
  };
};
