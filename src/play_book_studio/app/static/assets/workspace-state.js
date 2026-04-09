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
    initialize,
    setCorePack,
  };
};
