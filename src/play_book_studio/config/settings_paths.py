"""Settings의 artifact/path 계약만 분리해 둔 mixin."""

from __future__ import annotations

from pathlib import Path
import re

from .packs import GLOBAL_SOURCE_CATALOG_NAME


class SettingsPathMixin:
    def __post_init__(self) -> None:
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bronze_dir.mkdir(parents=True, exist_ok=True)
        self.silver_dir.mkdir(parents=True, exist_ok=True)
        self.silver_ko_dir.mkdir(parents=True, exist_ok=True)
        self.gold_corpus_ko_dir.mkdir(parents=True, exist_ok=True)
        self.gold_manualbook_ko_dir.mkdir(parents=True, exist_ok=True)
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        self.retrieval_dir.mkdir(parents=True, exist_ok=True)
        self.answering_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_sessions_dir.mkdir(parents=True, exist_ok=True)
        self.customer_pack_drafts_dir.mkdir(parents=True, exist_ok=True)
        self.customer_pack_capture_dir.mkdir(parents=True, exist_ok=True)
        self.customer_pack_books_dir.mkdir(parents=True, exist_ok=True)
        self.customer_pack_corpus_dir.mkdir(parents=True, exist_ok=True)
        self.playbook_books_dir.mkdir(parents=True, exist_ok=True)
        self.raw_html_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_optional_dir(self, value: str, default: Path) -> Path:
        if not value:
            return default
        normalized = value.strip().replace("\\", "/")
        candidate = Path(normalized).expanduser()
        if not candidate.is_absolute():
            candidate = self.root_dir / candidate
        return candidate.resolve()

    def _resolve_optional_path(self, value: str, default: Path) -> Path:
        if not value:
            return default
        normalized = value.strip().replace("\\", "/")
        candidate = Path(normalized).expanduser()
        if not candidate.is_absolute():
            candidate = self.root_dir / candidate
        return candidate.resolve()

    def _artifact_scope_dir(self, preferred_name: str) -> Path:
        return self.artifacts_dir / preferred_name

    def _unique_paths(self, *paths: Path) -> tuple[Path, ...]:
        unique: list[Path] = []
        seen: set[Path] = set()
        for path in paths:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            unique.append(resolved)
        return tuple(unique)

    @property
    def manifest_dir(self) -> Path:
        return self.root_dir / "manifests"

    @property
    def data_dir(self) -> Path:
        return self.root_dir / "data"

    @property
    def bronze_dir(self) -> Path:
        return self.data_dir / "bronze"

    @property
    def silver_dir(self) -> Path:
        return self.data_dir / "silver"

    @property
    def silver_ko_dir(self) -> Path:
        return self.data_dir / "silver_ko"

    @property
    def gold_corpus_ko_dir(self) -> Path:
        return self.data_dir / "gold_corpus_ko"

    @property
    def gold_manualbook_ko_dir(self) -> Path:
        return self.data_dir / "gold_manualbook_ko"

    @property
    def source_manifest_path(self) -> Path:
        return self._resolve_optional_path(
            self.source_manifest_path_override,
            self.manifest_dir / self.active_pack.approved_manifest_name,
        )

    @property
    def source_catalog_path(self) -> Path:
        return self._resolve_optional_path(
            self.source_catalog_path_override,
            self.manifest_dir / GLOBAL_SOURCE_CATALOG_NAME,
        )

    @property
    def translation_draft_manifest_path(self) -> Path:
        return self.manifest_dir / self.active_pack.translated_manifest_name

    @property
    def corpus_working_manifest_path(self) -> Path:
        return self.manifest_dir / self.active_pack.corpus_working_manifest_name

    @property
    def artifacts_dir(self) -> Path:
        return self._resolve_optional_dir(
            self.artifacts_dir_override,
            self.root_dir / "artifacts",
        )

    @property
    def corpus_dir(self) -> Path:
        return self._artifact_scope_dir("corpus")

    @property
    def retrieval_dir(self) -> Path:
        return self._artifact_scope_dir("retrieval")

    @property
    def raw_html_dir(self) -> Path:
        return self._resolve_optional_dir(
            self.raw_html_dir_override,
            self.bronze_dir / "raw_html",
        )

    @property
    def answering_dir(self) -> Path:
        return self._artifact_scope_dir("answering")

    @property
    def runtime_dir(self) -> Path:
        return self._artifact_scope_dir("runtime")

    @property
    def customer_packs_dir(self) -> Path:
        return self.artifacts_dir / "customer_packs"

    @property
    def customer_pack_drafts_dir(self) -> Path:
        return self.customer_packs_dir / "drafts"

    @property
    def customer_pack_capture_dir(self) -> Path:
        return self.customer_packs_dir / "captures"

    @property
    def customer_pack_books_dir(self) -> Path:
        return self.customer_packs_dir / "books"

    @property
    def customer_pack_corpus_dir(self) -> Path:
        return self.customer_packs_dir / "corpus"

    @property
    def normalized_docs_path(self) -> Path:
        return self.silver_dir / "normalized_docs.jsonl"

    @property
    def normalized_docs_candidates(self) -> tuple[Path, ...]:
        return (self.normalized_docs_path.resolve(),)

    @property
    def chunks_path(self) -> Path:
        return self.gold_corpus_ko_dir / "chunks.jsonl"

    @property
    def bm25_corpus_path(self) -> Path:
        return self.gold_corpus_ko_dir / "bm25_corpus.jsonl"

    @property
    def playbook_documents_path(self) -> Path:
        return self.gold_manualbook_ko_dir / "playbook_documents.jsonl"

    @property
    def playbook_books_dir(self) -> Path:
        return self.gold_manualbook_ko_dir / "playbooks"

    @property
    def playbook_book_dirs(self) -> tuple[Path, ...]:
        return (self.playbook_books_dir.resolve(),)

    @property
    def preprocessing_log_path(self) -> Path:
        return self.corpus_dir / "preprocessing_log.json"

    @property
    def source_manifest_update_report_path(self) -> Path:
        return self.corpus_dir / "source_manifest_update_report.json"

    @property
    def source_approval_report_path(self) -> Path:
        return self.corpus_dir / "source_approval_report.json"

    @property
    def corpus_gap_report_path(self) -> Path:
        return self.corpus_dir / "corpus_gap_report.json"

    @property
    def translation_lane_report_path(self) -> Path:
        return self.corpus_dir / "translation_lane_report.json"

    @property
    def retrieval_log_path(self) -> Path:
        return self.retrieval_dir / "retrieval_log.jsonl"

    @property
    def retrieval_smoke_report_path(self) -> Path:
        return self.retrieval_dir / "smoke_report.json"

    @property
    def retrieval_sanity_report_path(self) -> Path:
        return self.retrieval_dir / "sanity_report.json"

    @property
    def retrieval_eval_report_path(self) -> Path:
        return self.retrieval_dir / "retrieval_eval_report.json"

    @property
    def graph_sidecar_path(self) -> Path:
        return self.retrieval_dir / "graph_sidecar.json"

    @property
    def graph_sidecar_compact_path(self) -> Path:
        return self.retrieval_dir / "graph_sidecar_compact.json"

    @property
    def benchmark_report_path(self) -> Path:
        return self.retrieval_dir / "benchmark_report.json"

    @property
    def answer_log_path(self) -> Path:
        return self.answering_dir / "answer_log.jsonl"

    @property
    def answer_eval_report_path(self) -> Path:
        return self.answering_dir / "answer_eval_report.json"

    @property
    def ragas_dataset_preview_path(self) -> Path:
        return self.answering_dir / "ragas_eval_dataset_preview.json"

    @property
    def ragas_eval_report_path(self) -> Path:
        return self.answering_dir / "ragas_eval_report.json"

    @property
    def chat_log_path(self) -> Path:
        return self.runtime_dir / "chat_turns.jsonl"

    @property
    def chat_markdown_log_path(self) -> Path:
        return self.runtime_dir / "chat_turns.md"

    @property
    def runtime_sessions_dir(self) -> Path:
        return self.runtime_dir / "sessions"

    def session_snapshot_path(self, session_id: str) -> Path:
        normalized = self.session_snapshot_stem(session_id)
        return self.runtime_sessions_dir / f"{normalized}.json"

    def session_snapshot_stem(self, session_id: str) -> str:
        normalized = (session_id or "").strip() or "unknown-session"
        if re.fullmatch(r"[0-9a-f]{8,}", normalized, flags=re.IGNORECASE):
            return normalized[:8]
        if re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            normalized,
            flags=re.IGNORECASE,
        ):
            return normalized[:8]
        return normalized

    @property
    def recent_chat_session_path(self) -> Path:
        return self.runtime_dir / "recent_chat_session.json"

    @property
    def unanswered_questions_path(self) -> Path:
        return self.runtime_dir / "unanswered_questions.jsonl"

    @property
    def runtime_report_path(self) -> Path:
        return self.runtime_dir / "runtime_report.json"

    @property
    def runtime_endpoint_report_path(self) -> Path:
        return self.runtime_dir / "runtime_endpoint_report.json"
