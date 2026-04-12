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
    el.textContent = value;
  }

  function tone(value) {
    const normalized = String(value || "").trim().toLowerCase();
    if (["release_ready", "approved_ko", "approved", "gold", "ready", "ok"].includes(normalized)) {
      return "approved";
    }
    if (["needs_promotion", "translated_ko_draft", "silver draft", "needs_review", "review"].includes(normalized)) {
      return "review";
    }
    if (["blocked", "error", "failed"].includes(normalized)) {
      return "blocked";
    }
    return "neutral";
  }

  function statusChip(label, value, extraTone) {
    if (value === undefined || value === null || value === "") return "";
    const chipTone = extraTone || tone(value);
    return `<span class="status-chip ${esc(chipTone)}">${esc(label)} ${esc(value)}</span>`;
  }

  function chooseLink(item, options) {
    if (options && options.linkKind === "source") {
      return String(item.source_url || item.viewer_path || "").trim();
    }
    return String(item.viewer_path || item.source_url || "").trim();
  }

  function rowCard(item, options) {
    const link = chooseLink(item, options);
    const title = String(item.title || item.book_slug || "-").trim();
    const meta = [
      item.book_slug,
      item.source_lane,
      item.source_type,
      item.updated_at ? `갱신 ${dateText(item.updated_at)}` : "",
    ].filter(Boolean).join(" · ");
    const metrics = [
      item.chunk_count !== undefined ? `청크 ${count(item.chunk_count)}` : "",
      item.section_count !== undefined ? `섹션 ${count(item.section_count)}` : "",
      item.anchor_count !== undefined ? `앵커 ${count(item.anchor_count)}` : "",
      item.code_block_count !== undefined ? `코드 ${count(item.code_block_count)}` : "",
      item.command_chunk_count !== undefined ? `명령 ${count(item.command_chunk_count)}` : "",
    ].filter(Boolean).join(" · ");
    return `
      <div class="room-row">
        <div class="room-row-top">
          <div class="room-row-title">${link ? `<a href="${esc(link)}" target="_blank" rel="noreferrer">${esc(title)}</a>` : esc(title)}</div>
          ${statusChip(options.badgeLabel || "상태", item.grade || item.content_status || item.review_status || "-", options.badgeTone)}
        </div>
        <p class="room-row-copy">${esc(meta || "메타데이터 없음")}</p>
        <p class="room-row-copy">${esc(metrics || "상세 카운트 없음")}</p>
        <div class="tag-row">
          ${statusChip("검수", item.review_status)}
          ${statusChip("번역", item.content_status || item.translation_status)}
          ${typeof item.materialized === "boolean" ? statusChip("산출", item.materialized ? "materialized" : "missing", item.materialized ? "approved" : "blocked") : ""}
          ${item.high_value ? statusChip("중요", "high-value", "gold") : ""}
          ${item.fallback_detected ? statusChip("Fallback", "EN→KO", "review") : ""}
        </div>
      </div>
    `;
  }

  function corpusRowCard(item) {
    const link = chooseLink(item, { linkKind: "source" });
    const title = String(item.title || item.book_slug || "-").trim();
    const meta = [
      `slug ${item.book_slug || "-"}`,
      item.source_lane || "",
      item.source_type || "",
      item.updated_at ? `갱신 ${dateText(item.updated_at)}` : "",
    ].filter(Boolean).join(" · ");
    const metrics = [
      `청크 ${count(item.chunk_count)}`,
      `토큰 ${count(item.token_total)}`,
      `명령 ${count(item.command_chunk_count)}`,
      `에러 ${count(item.error_chunk_count)}`,
      `앵커 ${count(item.anchor_count)}`,
    ].join(" · ");
    const chunkKinds = item.chunk_type_breakdown && Object.keys(item.chunk_type_breakdown).length
      ? Object.entries(item.chunk_type_breakdown)
        .slice(0, 4)
        .map(([key, value]) => statusChip(key, count(value), "neutral"))
        .join("")
      : "";
    return `
      <div class="room-row">
        <div class="room-row-top">
          <div class="room-row-title">${link ? `<a href="${esc(link)}" target="_blank" rel="noreferrer">${esc(title)}</a>` : esc(title)}</div>
          ${statusChip("코퍼스", item.grade || "-", "approved")}
        </div>
        <p class="room-row-copy">${esc(meta || "코퍼스 메타데이터 없음")}</p>
        <p class="room-row-copy">${esc(metrics)}</p>
        <div class="tag-row">
          ${statusChip("산출", item.materialized ? "materialized" : "missing", item.materialized ? "approved" : "blocked")}
          ${statusChip("검수", item.review_status || "-", tone(item.review_status))}
          ${statusChip("링크", item.source_url ? "source" : "viewer", item.source_url ? "approved" : "review")}
          ${chunkKinds}
        </div>
      </div>
    `;
  }

  function manualbookRowCard(item) {
    const link = chooseLink(item, { linkKind: "viewer" });
    const title = String(item.title || item.book_slug || "-").trim();
    const meta = [
      `slug ${item.book_slug || "-"}`,
      item.source_lane || "",
      item.source_type || "",
      item.updated_at ? `갱신 ${dateText(item.updated_at)}` : "",
    ].filter(Boolean).join(" · ");
    const metrics = [
      `섹션 ${count(item.section_count)}`,
      `코드 ${count(item.code_block_count)}`,
      `문단 ${count(item.paragraph_block_count)}`,
      `앵커 ${count(item.anchor_count)}`,
    ].join(" · ");
    const sectionRoles = item.semantic_role_breakdown && Object.keys(item.semantic_role_breakdown).length
      ? Object.entries(item.semantic_role_breakdown)
        .slice(0, 4)
        .map(([key, value]) => statusChip(key, count(value), "neutral"))
        .join("")
      : "";
    return `
      <div class="room-row">
        <div class="room-row-top">
          <div class="room-row-title">${link ? `<a href="${esc(link)}" target="_blank" rel="noreferrer">${esc(title)}</a>` : esc(title)}</div>
          ${statusChip("매뉴얼북", item.grade || "-", "neutral")}
        </div>
        <p class="room-row-copy">${esc(meta || "매뉴얼북 메타데이터 없음")}</p>
        <p class="room-row-copy">${esc(metrics)}</p>
        <div class="tag-row">
          ${statusChip("검수", item.review_status || "-", tone(item.review_status))}
          ${statusChip("번역", item.translation_status || "-", tone(item.translation_status))}
          ${statusChip("산출", item.materialized ? "materialized" : "missing", item.materialized ? "approved" : "blocked")}
          ${sectionRoles}
        </div>
      </div>
    `;
  }

  function listInto(id, items, options) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!Array.isArray(items) || !items.length) {
      el.innerHTML = `<div class="room-row"><p class="room-row-copy">${esc(options.empty || "표시할 항목이 없습니다.")}</p></div>`;
      return;
    }
    const renderer = options && typeof options.renderItem === "function"
      ? options.renderItem
      : (item) => rowCard(item, options);
    el.innerHTML = items.slice(0, options.limit || 12).map((item) => renderer(item)).join("");
  }

  function renderKnownBooksTable(books) {
    const table = document.getElementById("data-situation-room-known-books-table");
    if (!table) return;
    const tbody = table.querySelector("tbody");
    if (!tbody) return;
    if (!Array.isArray(books) || !books.length) {
      tbody.innerHTML = `<tr><td colspan="7">표시할 책이 없습니다.</td></tr>`;
      return;
    }
    tbody.innerHTML = books.map((book) => {
      const link = chooseLink(book);
      return `
        <tr>
          <td>${link ? `<a href="${esc(link)}" target="_blank" rel="noreferrer">${esc(book.title || book.book_slug || "-")}</a>` : esc(book.title || book.book_slug || "-")}<br><span style="color:#627084">${esc(book.book_slug || "")}</span></td>
          <td>${esc(book.grade || "-")}</td>
          <td>${esc(book.content_status || book.review_status || "-")}</td>
          <td>${esc([book.source_lane, book.source_type].filter(Boolean).join(" / ") || "-")}</td>
          <td>${count(book.chunk_count)}</td>
          <td>${count(book.section_count)}</td>
          <td>${book.high_value ? "Y" : "-"}</td>
        </tr>
      `;
    }).join("");
  }

  function renderDrift(payload) {
    const el = document.getElementById("data-situation-room-drift-list");
    if (!el) return;
    const drift = payload.source_of_truth_drift || {};
    const storage = drift.storage_drift || {};
    const alignment = drift.status_alignment || {};
    const gradeSource = payload.canonical_grade_source || drift.canonical_grade_source || {};
    const materialization = payload.materialization || {};
    const items = [
      {
        title: "등급 기준 보고서",
        copy: `${gradeSource.name || "-"} · ${gradeSource.rule || ""}`,
        tags: [
          statusChip("exists", gradeSource.exists ? "yes" : "no", gradeSource.exists ? "approved" : "blocked"),
          statusChip("approved", alignment.approved_ko_count, "gold"),
          statusChip("runtime", alignment.approved_runtime_count, "approved"),
        ],
      },
      {
        title: "Storage drift",
        copy: `chunks drift ${storage.chunks && storage.chunks.drift_detected ? "있음" : "없음"} · playbooks drift ${storage.playbooks && storage.playbooks.drift_detected ? "있음" : "없음"}`,
        tags: [
          statusChip("manifest", storage.manifest && storage.manifest.exists ? "ready" : "missing", storage.manifest && storage.manifest.exists ? "approved" : "blocked"),
          statusChip("chunks", storage.chunks && storage.chunks.drift_detected ? "drift" : "aligned", storage.chunks && storage.chunks.drift_detected ? "review" : "approved"),
          statusChip("playbooks", storage.playbooks && storage.playbooks.drift_detected ? "drift" : "aligned", storage.playbooks && storage.playbooks.drift_detected ? "review" : "approved"),
        ],
      },
      {
        title: "Status alignment",
        copy: alignment.mismatches && alignment.mismatches.length ? alignment.mismatches.join(", ") : "gate/source approval/queue alignment ok",
        tags: [
          statusChip("gate", alignment.gate_status || "-", tone(alignment.gate_status)),
          statusChip("queue", alignment.active_queue_count, "review"),
          statusChip("mismatch", alignment.mismatches && alignment.mismatches.length ? alignment.mismatches.length : 0, alignment.mismatches && alignment.mismatches.length ? "blocked" : "approved"),
        ],
      },
      {
        title: "Materialization",
        copy: `runtime ${count(materialization.manifest_book_count)} · corpus ${count(materialization.materialized_corpus_book_count)} · manual book ${count(materialization.materialized_manualbook_book_count)} · extra ${count(materialization.extra_manualbook_book_count)} · topic ${count(materialization.materialized_topic_playbook_count)}`,
        tags: [
          statusChip("physical", materialization.counts_match ? "aligned" : "mismatch", materialization.counts_match ? "approved" : "blocked"),
          statusChip("logical", materialization.logical_counts_match ? "aligned" : "mismatch", materialization.logical_counts_match ? "approved" : "review"),
          statusChip("missing", (materialization.missing_corpus_books || []).length + (materialization.missing_manualbook_books || []).length, ((materialization.missing_corpus_books || []).length + (materialization.missing_manualbook_books || []).length) > 0 ? "blocked" : "approved"),
          statusChip("extra", (materialization.extra_corpus_book_count || 0) + (materialization.extra_manualbook_book_count || 0), ((materialization.extra_corpus_book_count || 0) + (materialization.extra_manualbook_book_count || 0)) > 0 ? "review" : "approved"),
        ],
      },
    ];
    el.innerHTML = items.map((item) => `
      <div class="room-row">
        <div class="room-row-top">
          <div class="room-row-title">${esc(item.title)}</div>
        </div>
        <p class="room-row-copy">${esc(item.copy)}</p>
        <div class="tag-row">${item.tags.join("")}</div>
      </div>
    `).join("");
  }

  function renderAudit(payload) {
    const el = document.getElementById("data-situation-room-audit-log");
    if (!el) return;
    const reportPaths = payload.recent_report_paths || {};
    const materialization = payload.materialization || {};
    const feed = [
      `Morning gate ${payload.summary && payload.summary.gate_status ? payload.summary.gate_status : "-"} · approved runtime ${count(payload.summary && payload.summary.gold_book_count)}권`,
      `Known books ${count(payload.summary && payload.summary.known_books_count)}권 · active queue ${count(payload.summary && payload.summary.active_queue_count)}권`,
      `Materialization ${materialization.counts_match ? "정합" : "불일치"} · runtime ${count(materialization.manifest_book_count)} / corpus ${count(materialization.materialized_corpus_book_count)} / manual book ${count(materialization.materialized_manualbook_book_count)} / extra ${count(materialization.extra_manualbook_book_count)} / topic ${count(materialization.materialized_topic_playbook_count)}`,
      `Retrieval hit@1 ${pct(payload.evaluations && payload.evaluations.retrieval && payload.evaluations.retrieval.book_hit_at_1)} · answer pass ${pct(payload.evaluations && payload.evaluations.answer && payload.evaluations.answer.pass_rate)}`,
      `Source approval report ${dateText(reportPaths.source_approval && reportPaths.source_approval.mtime)}`,
      `Translation lane report ${dateText(reportPaths.translation_lane && reportPaths.translation_lane.mtime)}`,
      `Runtime report ${dateText(reportPaths.runtime_report && reportPaths.runtime_report.mtime)}`,
    ];
    el.innerHTML = feed.map((item) => `<div class="feed-item">${esc(item)}</div>`).join("");
  }

  function renderFootnote(payload) {
    const el = document.getElementById("data-situation-room-footnote");
    if (!el) return;
    const canonical = payload.canonical_grade_source || {};
    const materialization = payload.materialization || {};
    const missingCorpus = (materialization.missing_corpus_books || []).length;
    const missingManualbooks = (materialization.missing_manualbook_books || []).length;
    const extraCorpus = materialization.extra_corpus_book_count || 0;
    const extraManualbooks = materialization.extra_manualbook_book_count || 0;
    const topicPlaybooks = materialization.materialized_topic_playbook_count || 0;
    el.textContent = `등급 기준은 ${canonical.name || "source_approval_report"}이고, queue 기준은 translation_lane_report다. runtime materialization은 ${materialization.counts_match ? "일치" : "불일치"} 상태이며, 누락 corpus ${missingCorpus}권 · 누락 manual book ${missingManualbooks}권 · extra corpus ${count(extraCorpus)}권 · extra manual book ${count(extraManualbooks)}권 · topic playbook ${count(topicPlaybooks)}권이다.`;
  }

  function renderOpsNotes(payload) {
    const retrieval = payload.evaluations && payload.evaluations.retrieval ? payload.evaluations.retrieval : {};
    const answer = payload.evaluations && payload.evaluations.answer ? payload.evaluations.answer : {};
    const runtime = payload.evaluations && payload.evaluations.runtime ? payload.evaluations.runtime : {};
    const probes = runtime.probes || {};
    const embedding = probes.embedding || {};
    const llmModel = runtime.runtime && runtime.runtime.llm_model ? runtime.runtime.llm_model : "-";
    const embeddingHealth = embedding.health_status !== undefined ? String(embedding.health_status) : "-";
    const sampleEmbeddingOk = embedding.sample_embedding_ok === true ? "ok" : embedding.sample_embedding_ok === false ? "fail" : "-";
    setText(
      "data-situation-room-eval-note",
      `retrieval hit@1 ${pct(retrieval.book_hit_at_1)} · answer pass ${pct(answer.pass_rate)} · citation precision ${pct(answer.avg_citation_precision)}`
    );
    setText(
      "data-situation-room-runtime-note",
      `LLM ${llmModel} · embedding health ${embeddingHealth} · sample embedding ${sampleEmbeddingOk}`
    );
  }

  function renderSummary(payload) {
    const summary = payload.summary || {};
    const activePack = payload.active_pack || {};
    const versionChip = document.getElementById("data-situation-room-version-chip");
    const liveStatus = document.getElementById("data-situation-room-live-status");
    const goldPill = document.getElementById("data-situation-room-gold-count-pill");
    const queuePill = document.getElementById("data-situation-room-queue-count-pill");
    const chunkPill = document.getElementById("data-situation-room-chunk-count-pill");
    const summaryGold = document.getElementById("data-situation-room-summary-gold-books");
    const summaryKnown = document.getElementById("data-situation-room-summary-known-books");
    const summaryQueue = document.getElementById("data-situation-room-summary-active-queue");
    const summaryGate = document.getElementById("data-situation-room-summary-gate");

    if (versionChip) versionChip.textContent = `${activePack.pack_label || "OpenShift 4.20"} · Grade Source ${summary.canonical_grade_source || "source_approval_report"}`;
    if (liveStatus) liveStatus.textContent = summary.gate_status || "unknown";
    if (goldPill) goldPill.textContent = count(summary.gold_book_count);
    if (queuePill) queuePill.textContent = count(summary.active_queue_count || summary.queue_count);
    if (chunkPill) chunkPill.textContent = count(summary.chunk_count);
    if (summaryGold) summaryGold.textContent = count(summary.gold_book_count);
    if (summaryKnown) summaryKnown.textContent = count(summary.known_books_count || summary.known_book_count);
    if (summaryQueue) summaryQueue.textContent = count(summary.active_queue_count || summary.queue_count);
    if (summaryGate) summaryGate.textContent = summary.gate_status || "-";
  }

  function renderErrorState(message) {
    setText("data-situation-room-live-status", "error");
    setText("data-situation-room-gold-count-pill", "-");
    setText("data-situation-room-queue-count-pill", "-");
    setText("data-situation-room-chunk-count-pill", "-");
    setText("data-situation-room-summary-gold-books", "-");
    setText("data-situation-room-summary-known-books", "-");
    setText("data-situation-room-summary-active-queue", "-");
    setText("data-situation-room-summary-gate", "error");
    setText("data-situation-room-version-chip", "OCP 4.20 Control Room");
    setText("data-situation-room-eval-note", "평가 리포트를 불러오지 못했다.");
    setText("data-situation-room-runtime-note", "런타임 프로브를 불러오지 못했다.");
    listInto("data-situation-room-gold-books-list", [], { empty: message });
    listInto("data-situation-room-active-queue-list", [], { empty: message });
    listInto("data-situation-room-high-value-list", [], { empty: message });
    listInto("data-situation-room-corpus-chunks-list", [], { empty: message });
    listInto("data-situation-room-manualbooks-list", [], { empty: message });
    renderKnownBooksTable([]);
    const drift = document.getElementById("data-situation-room-drift-list");
    if (drift) {
      drift.innerHTML = `<div class="room-row"><p class="room-row-copy">${esc(message)}</p></div>`;
    }
    const audit = document.getElementById("data-situation-room-audit-log");
    if (audit) {
      audit.innerHTML = `<div class="feed-item">${esc(message)}</div>`;
    }
    setText("data-situation-room-footnote", "데이터상황실을 불러오지 못했다. 현재 숫자는 비어 있는 상태다.");
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

  function render(payload) {
    renderSummary(payload);
    listInto("data-situation-room-gold-books-list", payload.gold_books || [], { badgeLabel: "등급", badgeTone: "gold", empty: "Gold 책이 없습니다." });
    listInto("data-situation-room-active-queue-list", payload.active_queue || [], { badgeLabel: "큐", badgeTone: "review", empty: "현재 활성 큐가 없습니다." });
    listInto("data-situation-room-high-value-list", (payload.high_value_focus && payload.high_value_focus.books) || [], { badgeLabel: "중요", badgeTone: "neutral", empty: "High-value focus 데이터가 없습니다." });
    listInto("data-situation-room-corpus-chunks-list", payload.corpus_book_status || [], { limit: 10, empty: "코퍼스 상태가 없습니다.", renderItem: corpusRowCard });
    listInto("data-situation-room-manualbooks-list", payload.manualbook_status || [], { limit: 10, empty: "매뉴얼북 상태가 없습니다.", renderItem: manualbookRowCard });
    renderKnownBooksTable(payload.known_books || []);
    renderDrift(payload);
    renderAudit(payload);
    renderOpsNotes(payload);
    renderFootnote(payload);
  }

  async function refresh() {
    const liveStatus = document.getElementById("data-situation-room-live-status");
    if (liveStatus) liveStatus.textContent = "refreshing";
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
    if (refreshButton) {
      refreshButton.addEventListener("click", () => {
        void refresh();
      });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    void refresh();
  });
})();
