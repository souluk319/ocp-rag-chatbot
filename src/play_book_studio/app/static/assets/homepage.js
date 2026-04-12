(function () {
  const slides = Array.from(document.querySelectorAll(".hero-slide"));
  const backgrounds = Array.from(document.querySelectorAll(".hero-bg"));
  const progressItems = Array.from(document.querySelectorAll(".hero-progress-item"));
  const prevBtn = document.getElementById("hero-prev-btn");
  const nextBtn = document.getElementById("hero-next-btn");
  const approvedRuntimeEl = document.getElementById("metric-approved-runtime");
  const topicPlaybooksEl = document.getElementById("metric-topic-playbooks");
  const answerPassRateEl = document.getElementById("metric-answer-pass-rate");
  const evidenceReadyEl = document.getElementById("metric-evidence-ready");
  const revealNodes = Array.from(document.querySelectorAll(".reveal-up"));

  if (!slides.length) {
    return;
  }

  let currentIndex = 0;
  let timer = null;

  function activate(index) {
    currentIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      slide.classList.toggle("active", slideIndex === currentIndex);
    });
    backgrounds.forEach((background, backgroundIndex) => {
      background.classList.toggle("active", backgroundIndex === currentIndex);
    });
    progressItems.forEach((item, itemIndex) => {
      item.classList.toggle("active", itemIndex === currentIndex);
    });
  }

  function queueNext() {
    if (timer) {
      window.clearInterval(timer);
    }
    timer = window.setInterval(() => {
      activate(currentIndex + 1);
    }, 6500);
  }

  function formatRate(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return "-";
    }
    return `${Math.round(value * 100)}%`;
  }

  function setMetric(node, value) {
    if (!node) {
      return;
    }
    node.textContent = value;
  }

  async function loadMetrics() {
    try {
      const response = await fetch("/api/data-control-room", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`status ${response.status}`);
      }
      const payload = await response.json();
      const summary = payload && typeof payload.summary === "object" ? payload.summary : {};
      const drift = payload && typeof payload.source_of_truth_drift === "object"
        ? payload.source_of_truth_drift
        : {};
      const storageDrift = drift && typeof drift.storage_drift === "object" ? drift.storage_drift : {};
      const evidenceReady = storageDrift.drift_detected === false ? "Ready" : "Review";

      setMetric(approvedRuntimeEl, String(summary.approved_runtime_count ?? "-"));
      setMetric(topicPlaybooksEl, String(summary.topic_playbook_count ?? "-"));
      setMetric(answerPassRateEl, formatRate(summary.answer_pass_rate));
      setMetric(evidenceReadyEl, evidenceReady);
    } catch (_error) {
      setMetric(approvedRuntimeEl, "-");
      setMetric(topicPlaybooksEl, "-");
      setMetric(answerPassRateEl, "-");
      setMetric(evidenceReadyEl, "Review");
    }
  }

  function bindReveal() {
    if (!("IntersectionObserver" in window)) {
      revealNodes.forEach((node) => node.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.16 });

    revealNodes.forEach((node) => observer.observe(node));
  }

  prevBtn?.addEventListener("click", () => {
    activate(currentIndex - 1);
    queueNext();
  });

  nextBtn?.addEventListener("click", () => {
    activate(currentIndex + 1);
    queueNext();
  });

  progressItems.forEach((item) => {
    item.addEventListener("click", () => {
      const target = Number(item.dataset.slideTarget || "0");
      activate(target);
      queueNext();
    });
  });

  activate(0);
  queueNext();
  bindReveal();
  void loadMetrics();
})();
