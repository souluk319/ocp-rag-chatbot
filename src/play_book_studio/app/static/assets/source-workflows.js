// 업로드 자료/보관함에서 참조 패널을 여는 특수 워크플로를 담당하는 프론트 helper다.
window.createSourceWorkflows = function createSourceWorkflows(deps) {
  const state = deps.state;
  const refs = deps.refs;
  const helpers = deps.helpers;
  const callbacks = deps.callbacks;

  async function openLibraryTrace(draftId) {
    const payload = await callbacks.openDocToBookDraft(draftId);
    let book = null;
    if (payload.status === "normalized" && payload.canonical_book_path) {
      try {
        book = await callbacks.fetchDocToBookBook(draftId);
      } catch (error) {
        book = null;
      }
    }
    callbacks.renderLibraryDetail(payload, book);
    callbacks.setStudyTab("library");
    callbacks.setSourcePanelVisible(true);
    await callbacks.loadDocToBookDrafts(draftId);
    return payload;
  }

  async function openLibraryAsset(draftId) {
    const payload = await openLibraryTrace(draftId);
    if (helpers.isReviewNeeded(payload)) {
      callbacks.setStudyTab("library");
      callbacks.setSourcePanelVisible(true);
      callbacks.setSourceLink(refs.sourceOpenDocEl, "");
      callbacks.setSourceLink(
        refs.sourceOpenOriginEl,
        `/api/doc-to-book/captured?draft_id=${encodeURIComponent(payload.draft_id)}`,
      );
      if (refs.sourceTitleEl) {
        refs.sourceTitleEl.textContent = payload.plan && payload.plan.title
          ? payload.plan.title
          : "정규화 검토 필요";
      }
      if (refs.sourcePathEl) {
        refs.sourcePathEl.textContent = "정규화 검토 필요";
      }
      if (refs.sourceNoteEl) {
        refs.sourceNoteEl.textContent = helpers.qualitySummaryText(payload) || "이 자료는 아직 바로 열기용 자산으로 쓰기엔 구조가 불안정합니다. 처리 과정과 원문을 먼저 확인해 주세요.";
      }
      callbacks.setSourceEmptyState();
      if (refs.sourceSummaryStripEl) {
        refs.sourceSummaryStripEl.innerHTML = "";
        [
          helpers.humanizeSourceCollection(payload.source_collection),
          payload.pack_label || "업로드 묶음",
          helpers.formatInferredScope(payload),
          helpers.qualityStatusLabel(payload) || "검토 전",
        ].forEach((label) => {
          refs.sourceSummaryStripEl.appendChild(helpers.createSummaryChip(label));
        });
      }
      return;
    }
    if (payload.status === "normalized" || payload.capture_artifact_path) {
      await openCapturedDocToBookDraft();
    }
  }

  async function openCapturedDocToBookDraft() {
    const activeIngestDraft = state.activeIngestDraft;
    if (!activeIngestDraft || !activeIngestDraft.draft_id) {
      return;
    }

    let normalizedBook = null;
    const normalizedReady = Boolean(activeIngestDraft.canonical_book_path);
    if (normalizedReady) {
      try {
        normalizedBook = await callbacks.fetchDocToBookBook(activeIngestDraft.draft_id);
      } catch (error) {
        normalizedBook = null;
      }
    }
    const reviewNeeded = helpers.isReviewNeeded(normalizedBook);
    const href = normalizedReady && !reviewNeeded
      ? `/docs/intake/${encodeURIComponent(activeIngestDraft.draft_id)}/index.html`
      : `/api/doc-to-book/captured?draft_id=${encodeURIComponent(activeIngestDraft.draft_id)}`;
    if (refs.sourceTitleEl) {
      refs.sourceTitleEl.textContent = activeIngestDraft.plan && activeIngestDraft.plan.title
        ? activeIngestDraft.plan.title
        : "수집 결과";
    }
    if (refs.sourcePathEl) {
      refs.sourcePathEl.textContent = [
        activeIngestDraft.request && activeIngestDraft.request.source_type
          ? activeIngestDraft.request.source_type.toUpperCase()
          : "-",
        activeIngestDraft.plan && activeIngestDraft.plan.capture_strategy
          ? helpers.humanizeDraftValue(activeIngestDraft.plan.capture_strategy)
          : "-",
      ].join(" · ");
    }
    if (refs.sourceNoteEl) {
      refs.sourceNoteEl.textContent = activeIngestDraft.normalize_error
        ? activeIngestDraft.normalize_error
        : activeIngestDraft.capture_error
          ? activeIngestDraft.capture_error
          : reviewNeeded
            ? (helpers.qualitySummaryText(normalizedBook) || "정리 결과가 아직 불안정해서 원문만 먼저 보여줍니다.")
            : normalizedReady
              ? "수집한 자료를 섹션 단위로 정리한 보기입니다."
              : "수집 결과를 먼저 확인하는 단계입니다. 다음은 자료를 섹션별로 정리하는 단계입니다.";
    }
    callbacks.setSourceLink(refs.sourceOpenDocEl, href);
    callbacks.setSourceLink(
      refs.sourceOpenOriginEl,
      `/api/doc-to-book/captured?draft_id=${encodeURIComponent(activeIngestDraft.draft_id)}`,
    );
    if (refs.sourceSummaryStripEl) {
      refs.sourceSummaryStripEl.innerHTML = "";
      [
        helpers.humanizeSourceCollection(activeIngestDraft.source_collection),
        activeIngestDraft.pack_label || "업로드 묶음",
        helpers.formatInferredScope(activeIngestDraft),
        reviewNeeded ? "정규화 검토 필요" : "",
        activeIngestDraft.status || "captured",
        normalizedReady
          ? `${activeIngestDraft.normalized_section_count || 0}개 섹션`
          : (activeIngestDraft.capture_content_type || "수집 파일"),
        helpers.formatByteSize(activeIngestDraft.capture_byte_size),
      ].forEach((label) => {
        refs.sourceSummaryStripEl.appendChild(helpers.createSummaryChip(label));
      });
    }
    callbacks.setStudyTab("source");
    callbacks.setSourcePanelVisible(true);

    if (!normalizedReady) {
      refs.sourceFrameShellEl.hidden = false;
      refs.sourceViewerFrameEl.hidden = false;
      callbacks.setSourceFrameLoading(true);
      refs.sourceViewerFrameEl.src = href;
      if (refs.sourceOutlineEl) {
        refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">이 자료는 아직 수집 단계라 섹션 목록이 없습니다. 정리 후에 목록이 생깁니다.</div>';
      }
      return;
    }

    if (reviewNeeded) {
      if (refs.sourcePathEl) {
        refs.sourcePathEl.textContent = "정규화 검토 필요";
      }
      if (refs.sourceNoteEl) {
        refs.sourceNoteEl.textContent = helpers.qualitySummaryText(normalizedBook) || "이 자료는 아직 바로 열지 않습니다. 원문과 처리 과정을 먼저 확인해 주세요.";
      }
      if (refs.sourceOutlineEl) {
        refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">검토가 끝난 뒤 section outline이 열립니다.</div>';
      }
      callbacks.setSourceEmptyState();
      return;
    }

    refs.sourceFrameShellEl.hidden = false;
    refs.sourceViewerFrameEl.hidden = false;
    callbacks.setSourceFrameLoading(true);
    refs.sourceViewerFrameEl.src = href;

    if (refs.sourceOutlineEl) {
      refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">섹션 목록을 불러오는 중입니다.</div>';
    }
    try {
      const book = normalizedBook || await callbacks.fetchDocToBookBook(activeIngestDraft.draft_id);
      if (!state.activeIngestDraft || state.activeIngestDraft.draft_id !== book.draft_id) return;
      callbacks.renderSourceBook(book, "");
    } catch (error) {
      if (refs.sourceOutlineEl) {
        refs.sourceOutlineEl.innerHTML = '<div class="trace-empty">섹션 목록을 불러오지 못했습니다.</div>';
      }
    }
  }

  return {
    openCapturedDocToBookDraft,
    openLibraryAsset,
    openLibraryTrace,
  };
};
