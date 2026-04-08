// 업로드 초안/보관함 화면 렌더링을 담당하는 프론트 helper다.
window.createIntakeRenderer = function createIntakeRenderer(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const callbacks = deps.callbacks;

  function setIngestStatus(message, tone = "muted") {
    refs.ingestStatusEl.textContent = message || " ";
    refs.ingestStatusEl.dataset.tone = tone;
  }

  function populateDocToBookForm(payload) {
    refs.ingestSourceTypeEl.value = payload && payload.request && payload.request.source_type
      ? payload.request.source_type
      : "web";
    refs.ingestUriEl.value = payload && payload.request && payload.request.uri ? payload.request.uri : "";
    refs.ingestTitleEl.value = payload && payload.request && payload.request.title ? payload.request.title : "";
    if (payload && payload.uploaded_file_name) {
      refs.ingestFilePillEl.textContent = `${payload.uploaded_file_name} · ${helpers.formatByteSize(payload.uploaded_byte_size)}`;
    } else if (!(payload && payload.request && payload.request.uri)) {
      helpers.setIngestSelectedFile(null);
    }
    helpers.syncIngestUploadHint();
  }

  function createPreviewStep(title, body) {
    const card = document.createElement("section");
    card.className = "draft-preview-step";

    const kicker = document.createElement("div");
    kicker.className = "draft-preview-step-title";
    kicker.textContent = title;

    const content = document.createElement("div");
    content.className = "draft-preview-step-body";
    content.textContent = body;

    card.append(kicker, content);
    return card;
  }

  function createAssetTraceCard(title, value, detail = "") {
    const card = document.createElement("article");
    card.className = "asset-trace-card";

    const strong = document.createElement("strong");
    strong.textContent = title;

    const valueEl = document.createElement("span");
    valueEl.textContent = value;

    card.append(strong, valueEl);
    if (detail) {
      const detailEl = document.createElement("span");
      detailEl.textContent = detail;
      card.appendChild(detailEl);
    }
    return card;
  }

  function createAssetTraceStep(kicker, body) {
    const step = document.createElement("section");
    step.className = "asset-trace-step";

    const kickerEl = document.createElement("div");
    kickerEl.className = "asset-trace-step-kicker";
    kickerEl.textContent = kicker;

    const bodyEl = document.createElement("div");
    bodyEl.className = "asset-trace-step-body";
    bodyEl.textContent = body;

    step.append(kickerEl, bodyEl);
    return step;
  }

  function renderIngestCaptureMeta(payload) {
    state.activeIngestDraft = payload && payload.draft_id ? payload : null;
    state.activeIngestDraftId = state.activeIngestDraft && state.activeIngestDraft.draft_id ? state.activeIngestDraft.draft_id : "";

    if (!state.activeIngestDraft) {
      refs.ingestCaptureMetaEl.innerHTML = '<div class="draft-preview-empty">아직 수집 결과가 없습니다.</div>';
      refs.ingestOpenCaptureBtn.disabled = true;
      return;
    }

    refs.ingestCaptureMetaEl.innerHTML = "";
    const summaryGrid = document.createElement("div");
    summaryGrid.className = "summary-grid";

    const captureReady = Boolean(state.activeIngestDraft.capture_artifact_path);
    const normalizedReady = Boolean(state.activeIngestDraft.canonical_book_path);
    [
      {
        label: "초안",
        value: state.activeIngestDraft.status || "planned",
        detail: state.activeIngestDraft.draft_id || "-",
      },
      {
        label: "상태",
        value: normalizedReady ? "정리 완료" : (captureReady ? "수집 완료" : "대기 중"),
        detail: normalizedReady
          ? `${state.activeIngestDraft.normalized_section_count || 0}개 섹션`
          : (state.activeIngestDraft.capture_content_type || "아직 수집 전"),
      },
      {
        label: "크기",
        value: helpers.formatByteSize(state.activeIngestDraft.capture_byte_size),
        detail: state.activeIngestDraft.plan && state.activeIngestDraft.plan.capture_strategy
          ? helpers.humanizeDraftValue(state.activeIngestDraft.plan.capture_strategy)
          : "-",
      },
      {
        label: "자료",
        value: state.activeIngestDraft.request && state.activeIngestDraft.request.source_type
          ? state.activeIngestDraft.request.source_type
          : "-",
        detail: state.activeIngestDraft.plan && state.activeIngestDraft.plan.acquisition_uri
          ? state.activeIngestDraft.plan.acquisition_uri
          : (state.activeIngestDraft.request && state.activeIngestDraft.request.uri) || "-",
      },
    ].forEach((item) => {
      const card = document.createElement("div");
      card.className = "summary-card";
      const kicker = document.createElement("div");
      kicker.className = "summary-kicker";
      kicker.textContent = item.label;
      const value = document.createElement("div");
      value.className = "summary-value";
      value.textContent = item.value;
      const detail = document.createElement("div");
      detail.className = "summary-detail";
      detail.textContent = item.detail;
      card.append(kicker, value, detail);
      summaryGrid.appendChild(card);
    });

    refs.ingestCaptureMetaEl.appendChild(summaryGrid);

    if (state.activeIngestDraft.capture_error) {
      refs.ingestCaptureMetaEl.appendChild(createPreviewStep("수집 오류", state.activeIngestDraft.capture_error));
    } else if (state.activeIngestDraft.normalize_error) {
      refs.ingestCaptureMetaEl.appendChild(createPreviewStep("정리 오류", state.activeIngestDraft.normalize_error));
    } else if (normalizedReady) {
      refs.ingestCaptureMetaEl.appendChild(createPreviewStep("정리본", state.activeIngestDraft.canonical_book_path));
    } else if (captureReady) {
      refs.ingestCaptureMetaEl.appendChild(createPreviewStep("수집 파일", state.activeIngestDraft.capture_artifact_path));
    } else {
      refs.ingestCaptureMetaEl.appendChild(
        createPreviewStep(
          "다음 단계",
          "지금은 초안만 저장된 상태입니다. 먼저 수집을 실행하고, 그다음 정리를 실행하면 섹션 구조가 만들어집니다.",
        ),
      );
    }

    refs.ingestOpenCaptureBtn.disabled = !(captureReady || normalizedReady);
  }

  function resetLibraryDetail() {
    state.activeLibraryDraftId = "";
    refs.libraryDetailEl.innerHTML = '<div class="asset-trace-empty">문서 자산을 선택하면 원문, 수집, 정리, 파생 과정을 여기서 확인할 수 있습니다.</div>';
  }

  function renderLibraryDetail(draft, book = null) {
    state.activeLibraryDraftId = draft && draft.draft_id ? draft.draft_id : "";
    if (!draft) {
      resetLibraryDetail();
      return;
    }

    refs.libraryDetailEl.innerHTML = "";

    const summary = document.createElement("div");
    summary.className = "asset-trace-grid";
    summary.append(
      createAssetTraceCard("자료군", helpers.humanizeSourceCollection(draft.source_collection), `${draft.pack_label || "업로드 묶음"} · ${helpers.formatInferredScope(draft)}`),
      createAssetTraceCard("수집", helpers.humanizeDraftValue(draft.capture_strategy), draft.capture_content_type || draft.acquisition_uri || "-"),
      createAssetTraceCard("정리", helpers.humanizeDraftValue(draft.canonical_model || (draft.plan && draft.plan.canonical_model)), `${draft.normalized_section_count || 0}개 섹션`),
      createAssetTraceCard("품질", helpers.qualityStatusLabel(draft) || "검토 전", helpers.qualitySummaryText(draft) || "정리 품질 판정 전"),
      createAssetTraceCard("원본", draft.source_uri || "-", draft.book_slug || "-"),
    );

    const actions = document.createElement("div");
    actions.className = "asset-trace-actions";

    const studyButton = document.createElement("button");
    studyButton.type = "button";
    studyButton.className = "ghost-btn";
    studyButton.textContent = helpers.isReviewNeeded(draft) ? "정규 문서 보류" : "정규 문서 열기";
    studyButton.disabled = helpers.isReviewNeeded(draft);
    studyButton.addEventListener("click", () => {
      void callbacks.openLibraryAsset(draft.draft_id);
    });
    actions.appendChild(studyButton);

    if (draft.capture_artifact_path) {
      const capturedLink = document.createElement("a");
      capturedLink.className = "source-link";
      capturedLink.href = `/api/doc-to-book/captured?draft_id=${encodeURIComponent(draft.draft_id)}`;
      capturedLink.target = "_blank";
      capturedLink.rel = "noreferrer";
      capturedLink.textContent = "수집본 보기";
      actions.appendChild(capturedLink);
    }

    const steps = document.createElement("div");
    steps.className = "asset-trace-steps";
    steps.append(
      createAssetTraceStep("원문", [
        `사용자 입력: ${draft.source_uri || "-"}`,
        draft.uploaded_file_path ? `업로드 파일: ${draft.uploaded_file_path}` : "",
        `자료군: ${helpers.humanizeSourceCollection(draft.source_collection)}`,
        `묶음: ${draft.pack_label || "업로드 묶음"}`,
        `범위: ${helpers.formatInferredScope(draft)}`,
      ].filter(Boolean).join("\n")),
      createAssetTraceStep("수집", [
        draft.acquisition_uri ? `수집 주소: ${draft.acquisition_uri}` : "",
        draft.plan && draft.plan.acquisition_step ? draft.plan.acquisition_step : "",
      ].filter(Boolean).join("\n")),
      createAssetTraceStep("정리", [
        draft.plan && draft.plan.normalization_step ? draft.plan.normalization_step : "",
        `정리 방식: ${draft.plan && draft.plan.canonical_model ? draft.plan.canonical_model : draft.canonical_model || "-"}`,
        `섹션 수: ${draft.normalized_section_count || 0}`,
      ].join("\n")),
      createAssetTraceStep("파생", [
        draft.plan && draft.plan.derivation_step ? draft.plan.derivation_step : "",
        draft.plan && draft.plan.retrieval_derivation ? `검색 파생: ${draft.plan.retrieval_derivation}` : "",
      ].filter(Boolean).join("\n")),
    );

    const notes = Array.isArray(draft.plan && draft.plan.notes) ? draft.plan.notes.filter(Boolean) : [];
    if (notes.length) {
      steps.appendChild(createAssetTraceStep("전처리 메모", notes.join("\n")));
    }
    if (helpers.qualitySummaryText(draft)) {
      steps.appendChild(
        createAssetTraceStep(
          "품질 점검",
          [
            helpers.qualityStatusLabel(draft) || "검토 전",
            helpers.qualitySummaryText(draft),
            Array.isArray(draft.quality_flags) && draft.quality_flags.length
              ? `플래그: ${draft.quality_flags.join(", ")}`
              : "",
          ].filter(Boolean).join("\n"),
        ),
      );
    }
    if (book && Array.isArray(book.sections) && book.sections.length) {
      steps.appendChild(
        createAssetTraceStep(
          "섹션 미리보기",
          book.sections
            .slice(0, 4)
            .map((section) => section.section_path_label || section.heading || section.anchor)
            .filter(Boolean)
            .join("\n"),
        ),
      );
    }

    refs.libraryDetailEl.append(summary, actions, steps);
  }

  function renderDocToBookPreview(payload) {
    const draft = payload && payload.plan ? payload.plan : payload;
    if (!draft || typeof draft !== "object") {
      refs.ingestPlanOutputEl.innerHTML = '<div class="draft-preview-empty">아직 정리본이 없습니다.</div>';
      return;
    }

    refs.ingestPlanOutputEl.innerHTML = "";
    const summaryGrid = document.createElement("div");
    summaryGrid.className = "summary-grid";

    [
      { label: "제목", value: draft.title || "-", detail: draft.book_slug || "-" },
      { label: "수집", value: helpers.humanizeDraftValue(draft.capture_strategy), detail: `${draft.source_type || "-"} · ${draft.capture_strategy || "-"}` },
      { label: "묶음", value: draft.pack_label || "업로드 묶음", detail: `${helpers.humanizeSourceCollection(draft.source_collection)} · ${helpers.formatInferredScope(draft)}` },
      { label: "정리", value: helpers.humanizeDraftValue(draft.canonical_model), detail: payload && payload.draft_id ? `초안 ${payload.draft_id}` : helpers.humanizeDraftValue(draft.source_view_strategy) },
    ].forEach((item) => {
      const card = document.createElement("div");
      card.className = "summary-card";
      const kicker = document.createElement("div");
      kicker.className = "summary-kicker";
      kicker.textContent = item.label;
      const value = document.createElement("div");
      value.className = "summary-value";
      value.textContent = item.value;
      const detail = document.createElement("div");
      detail.className = "summary-detail";
      detail.textContent = item.detail;
      card.append(kicker, value, detail);
      summaryGrid.appendChild(card);
    });

    const steps = document.createElement("div");
    steps.className = "draft-preview-steps";
    steps.append(
      createPreviewStep("수집 주소", draft.acquisition_uri || draft.source_uri || "-"),
      createPreviewStep("수집 단계", draft.acquisition_step || "-"),
      createPreviewStep("정리 단계", draft.normalization_step || "-"),
      createPreviewStep("파생 단계", draft.derivation_step || "-"),
    );

    refs.ingestPlanOutputEl.append(summaryGrid, steps);

    const notes = Array.isArray(draft.notes) ? draft.notes.filter(Boolean) : [];
    if (notes.length) {
      const noteWrap = document.createElement("div");
      noteWrap.className = "draft-preview-notes";
      notes.forEach((note, index) => {
        noteWrap.appendChild(createPreviewStep(`메모 ${index + 1}`, note));
      });
      refs.ingestPlanOutputEl.appendChild(noteWrap);
    }
  }

  return {
    populateDocToBookForm,
    renderDocToBookPreview,
    renderIngestCaptureMeta,
    renderLibraryDetail,
    resetLibraryDetail,
    setIngestStatus,
  };
};
