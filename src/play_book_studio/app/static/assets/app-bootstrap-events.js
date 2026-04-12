// 앱 bootstrap의 shell-level 이벤트 wiring만 남긴다.
window.bindAppBootstrapEvents = function bindAppBootstrapEvents(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const callbacks = deps.callbacks;

  refs.sourceViewerFrameEl.addEventListener("load", () => {
    helpers.setSourceFrameLoading(false);
  });
  refs.sourcePanelToggleBtn.addEventListener("click", () => {
    callbacks.setSourcePanelVisible(!state.sourcePanelVisible);
  });
  refs.sourcePanelEdgeBtn.addEventListener("click", () => {
    callbacks.setSourcePanelVisible(!state.sourcePanelVisible);
  });
  refs.leftRailToggleBtn.addEventListener("click", () => {
    callbacks.setLeftPanelVisible(!state.leftPanelVisible);
  });
  refs.leftPanelToggleBtn.addEventListener("click", () => {
    callbacks.setLeftPanelVisible(!state.leftPanelVisible);
  });

  window.addEventListener("resize", helpers.syncViewportLayout);
  if (typeof ResizeObserver !== "undefined" && refs.topbarEl) {
    const topbarObserver = new ResizeObserver(() => helpers.syncViewportLayout());
    topbarObserver.observe(refs.topbarEl);
  }

  helpers.syncViewportLayout();
  callbacks.initializeChatSession();
  callbacks.setLeftPanelVisible(true);
  callbacks.setSourcePanelVisible(true);
  callbacks.setCorePack(state.currentOcpVersion);
  callbacks.resetPipelineTrace();
  callbacks.resetSourcePanel();
};
