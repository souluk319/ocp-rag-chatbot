(function () {
  function esc(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function count(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed.toLocaleString("ko-KR") : "-";
  }

  function pct(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? `${(parsed * 100).toFixed(1)}%` : "-";
  }

  function dateText(value) {
    const text = String(value || "").trim();
    if (!text) return "-";
    const date = new Date(text);
    if (Number.isNaN(date.getTime())) return text;
    return new Intl.DateTimeFormat("ko-KR", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = String(value ?? "");
  }

  function setHTML(id, html) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = html;
  }

  function tone(value) {
    const normalized = String(value || "").trim().toLowerCase();
    if (["release_ready", "approved_ko", "approved", "gold", "ready", "ok", "materialized"].includes(normalized)) {
      return "approved";
    }
    if (["needs_promotion", "translated_ko_draft", "silver draft", "needs_review", "review", "mixed"].includes(normalized)) {
      return "review";
    }
    if (["blocked", "error", "failed", "missing", "not_emitted"].includes(normalized)) {
      return "blocked";
    }
    return "neutral";
  }

  function statusChip(label, value, chipTone) {
    if (value === undefined || value === null || value === "") return "";
    const resolvedTone = chipTone || tone(value);
    return `<span class="status-chip ${esc(resolvedTone)}">${esc(label)} ${esc(value)}</span>`;
  }

  function chooseLink(item) {
    return String(item.viewer_path || item.source_url || "").trim();
  }

  function emptyState(message) {
    return `<div class="room-empty">${esc(message)}</div>`;
  }

  function rowCard(item) {
    const link = chooseLink(item);
    const title = String(item.title || item.book_slug || "-").trim();
    const meta = [
      item.book_slug,
      item.library_group_label || item.family_label || "",
      item.source_lane || "",
      item.source_type || "",
      item.updated_at ? `갱신 ${dateText(item.updated_at)}` : "",
    ].filter(Boolean).join(" · ");
    const metrics = [
      item.section_count !== undefined ? `섹션 ${count(item.section_count)}` : "",
      item.anchor_count !== undefined ? `앵커 ${count(item.anchor_count)}` : "",
      item.code_block_count !== undefined ? `코드 ${count(item.code_block_count)}` : "",
      item.paragraph_block_count !== undefined ? `문단 ${count(item.paragraph_block_count)}` : "",
      item.chunk_count !== undefined ? `청크 ${count(item.chunk_count)}` : "",
    ].filter(Boolean).join(" · ");
    return `
      <article class="room-row">
        <div class="room-row-top">
          <div class="room-row-title">
            ${link ? `<a href="${esc(link)}" target="_blank" rel="noreferrer">${esc(title)}</a>` : esc(title)}
          </div>
          ${statusChip("상태", item.grade || item.content_status || item.review_status || "-", item.grade === "Gold" ? "gold" : null)}
        </div>
        <p class="room-row-copy">${esc(meta || "메타데이터 없음")}</p>
        <p class="room-row-copy">${esc(metrics || "상세 카운트 없음")}</p>
        <div class="tag-row">
          ${statusChip("검수", item.review_status || "-")}
          ${statusChip("번역", item.content_status || item.translation_status || "-")}
          ${typeof item.materialized === "boolean" ? statusChip("산출", item.materialized ? "materialized" : "missing", item.materialized ? "approved" : "blocked") : ""}
        </div>
      </article>
    `;
  }

  function renderList(id, items, emptyMessage) {
    if (!Array.isArray(items) || !items.length) {
      setHTML(id, emptyState(emptyMessage));
      return;
    }
    setHTML(id, items.map((item) => rowCard(item)).join(""));
  }

  function renderSummary(payload) {
    const summary = payload.summary || {};
    const manualLibrary = payload.manual_book_library || {};
    const playbookLibrary = payload.playbook_library || {};
    const activePack = payload.active_pack || {};

    setText(
      "data-situation-room-version-chip",
      `${activePack.pack_label || "OpenShift 4.20"} · ${summary.canonical_grade_source || "source_approval_report"}`
    );
    setText("data-situation-room-live-status", summary.gate_status || "unknown");
    setText("data-situation-room-summary-raw-manuals", count(summary.raw_manual_count));
    setText("data-situation-room-summary-manual-books", count(manualLibrary.total_count));
    setText("data-situation-room-summary-playbooks", count(playbookLibrary.total_count));
    setText("data-situation-room-summary-gate", summary.gate_status || "-");

    setText("data-situation-room-manual-total-pill", count(manualLibrary.total_count));
    setText("data-situation-room-manual-core-pill", count(manualLibrary.core_count));
    setText("data-situation-room-manual-extra-pill", count(manualLibrary.extra_count));
    setText("data-situation-room-manual-core-chip", `${count(manualLibrary.core_count)}권`);
    setText("data-situation-room-manual-extra-chip", `${count(manualLibrary.extra_count)}권`);

    setText("data-situation-room-playbook-total-pill", count(playbookLibrary.total_count));
    setText("data-situation-room-playbook-family-pill", count(playbookLibrary.family_count));
  }

  function renderManualLibrary(payload) {
    const library = payload.manual_book_library || {};
    const books = Array.isArray(library.books) ? library.books : [];
    const coreBooks = books.filter((book) => book.library_group === "core");
    const extraBooks = books.filter((book) => book.library_group === "extra");

    renderList(
      "data-situation-room-manual-core-list",
      coreBooks,
      "런타임 팩 매뉴얼북이 없습니다."
    );
    renderList(
      "data-situation-room-manual-extra-list",
      extraBooks,
      "확장 매뉴얼북이 없습니다."
    );
  }

  function familyCard(family) {
    return `
      <article class="family-card">
        <span>${esc(family.family_label || family.family || "-")}</span>
        <strong>${count(family.count)}</strong>
      </article>
    `;
  }

  function familySection(family) {
    const books = Array.isArray(family.books) ? family.books : [];
    return `
      <details class="family-section" ${books.length ? "" : ""}>
        <summary>
          <span class="summary-title">${esc(family.family_label || family.family || "-")}</span>
          <span class="tag-row">
            ${statusChip("수량", count(family.count), "neutral")}
            ${statusChip("상태", family.status || "-", family.status === "materialized" ? "approved" : null)}
          </span>
        </summary>
        <div class="family-section-body">
          ${books.length ? books.map((book) => rowCard(book)).join("") : emptyState("이 family에 아직 책이 없습니다.")}
        </div>
      </details>
    `;
  }

  function renderPlaybookLibrary(payload) {
    const library = payload.playbook_library || {};
    const families = Array.isArray(library.families) ? library.families : [];

    if (!families.length) {
      setHTML("data-situation-room-family-grid", emptyState("플레이북 family 데이터가 없습니다."));
      setHTML("data-situation-room-family-sections", emptyState("플레이북 라이브러리가 아직 비어 있습니다."));
      return;
    }

    setHTML(
      "data-situation-room-family-grid",
      families.map((family) => familyCard(family)).join("")
    );
    setHTML(
      "data-situation-room-family-sections",
      families.map((family) => familySection(family)).join("")
    );
  }

  function renderOpsSnapshot(payload) {
    const summary = payload.summary || {};
    const evaluations = payload.evaluations || {};
    const retrieval = evaluations.retrieval || {};
    const answer = evaluations.answer || {};
    const reportPaths = payload.recent_report_paths || {};
    const materialization = payload.materialization || {};
    const multiplication = materialization.playable_asset_multiplication || {};

    setText("data-situation-room-ops-retrieval", pct(retrieval.book_hit_at_1));
    setText("data-situation-room-ops-answer", pct(answer.pass_rate));
    setText("data-situation-room-ops-runtime-count", count(summary.approved_runtime_count || summary.gold_book_count));
    setText(
      "data-situation-room-ops-runtime-report",
      dateText(reportPaths.runtime_report && reportPaths.runtime_report.mtime)
    );

    setText(
      "data-situation-room-footnote",
      `raw ${count(multiplication.raw_manual_count)}권에서 playable ${count(multiplication.playable_asset_count)}권으로 증식됐다. 배수 ${count(multiplication.ratio_vs_raw_manual_count)} · gate ${summary.gate_status || "-"}`
    );
  }

  function render(payload) {
    renderSummary(payload);
    renderManualLibrary(payload);
    renderPlaybookLibrary(payload);
    renderOpsSnapshot(payload);
  }

  function renderErrorState(message) {
    setText("data-situation-room-live-status", "error");
    setText("data-situation-room-version-chip", "OpenShift 4.20 · data-control-room");
    setText("data-situation-room-summary-raw-manuals", "-");
    setText("data-situation-room-summary-manual-books", "-");
    setText("data-situation-room-summary-playbooks", "-");
    setText("data-situation-room-summary-gate", "error");
    setText("data-situation-room-manual-total-pill", "-");
    setText("data-situation-room-manual-core-pill", "-");
    setText("data-situation-room-manual-extra-pill", "-");
    setText("data-situation-room-manual-core-chip", "-");
    setText("data-situation-room-manual-extra-chip", "-");
    setText("data-situation-room-playbook-total-pill", "-");
    setText("data-situation-room-playbook-family-pill", "-");
    setText("data-situation-room-ops-retrieval", "-");
    setText("data-situation-room-ops-answer", "-");
    setText("data-situation-room-ops-runtime-count", "-");
    setText("data-situation-room-ops-runtime-report", "-");
    setText("data-situation-room-footnote", "데이터상황실을 불러오지 못했다.");
    setHTML("data-situation-room-manual-core-list", emptyState(message));
    setHTML("data-situation-room-manual-extra-list", emptyState(message));
    setHTML("data-situation-room-family-grid", emptyState(message));
    setHTML("data-situation-room-family-sections", emptyState(message));
  }

  async function loadPayload() {
    const response = await fetch("/api/data-control-room", {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || `데이터상황실 요청 실패 (${response.status})`);
    }
    return payload;
  }

  async function refresh() {
    setText("data-situation-room-live-status", "refreshing");
    try {
      const payload = await loadPayload();
      render(payload);
    } catch (error) {
      const message = error && error.message ? error.message : "데이터상황실을 불러오지 못했습니다.";
      renderErrorState(message);
    }
  }

  function bindEvents() {
    const refreshButton = document.getElementById("data-situation-room-refresh-btn");
    if (!refreshButton) return;
    refreshButton.addEventListener("click", () => {
      void refresh();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    void refresh();
  });
})();
