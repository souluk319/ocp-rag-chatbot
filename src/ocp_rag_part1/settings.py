from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


HIGH_VALUE_SLUGS = (
    "overview",
    "architecture",
    "installation_overview",
    "installing_on_any_platform",
    "disconnected_environments",
    "postinstallation_configuration",
    "updating_clusters",
    "release_notes",
    "nodes",
    "etcd",
    "operators",
    "authentication_and_authorization",
    "security_and_compliance",
    "cli_tools",
    "networking_overview",
    "advanced_networking",
    "ingress_and_load_balancing",
    "storage",
    "monitoring",
    "logging",
    "support",
    "validation_and_troubleshooting",
    "backup_and_restore",
    "machine_management",
    "machine_configuration",
    "images",
    "registry",
    "web_console",
    "observability_overview",
)
ENV_REFERENCE_RE = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")


@dataclass(slots=True)
class Settings:
    root_dir: Path
    artifacts_dir_override: str = field(
        default_factory=lambda: os.getenv("ARTIFACTS_DIR", "").strip()
    )
    raw_html_dir_override: str = field(
        default_factory=lambda: os.getenv("RAW_HTML_DIR", "").strip()
    )
    source_manifest_path_override: str = field(
        default_factory=lambda: os.getenv("SOURCE_MANIFEST_PATH", "").strip()
    )
    docs_index_url: str = (
        "https://docs.redhat.com/ko/documentation/"
        "openshift_container_platform/4.20/"
    )
    book_url_template: str = (
        "https://docs.redhat.com/ko/documentation/"
        "openshift_container_platform/4.20/html-single/{slug}/index"
    )
    viewer_path_template: str = "/docs/ocp/4.20/ko/{slug}/index.html"
    user_agent: str = "Mozilla/5.0 (compatible; OCPRAGPart1/1.0)"
    request_timeout_seconds: int = 30
    request_retries: int = 3
    request_backoff_seconds: int = 2
    chunk_size: int = 160
    chunk_overlap: int = 32
    embedding_base_url: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_BASE_URL", "").strip().rstrip("/")
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "dragonkue/bge-m3-ko")
    )
    embedding_device: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_DEVICE", "auto").strip()
    )
    embedding_api_key: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_API_KEY", "").strip()
    )
    embedding_batch_size: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    )
    embedding_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("EMBEDDING_TIMEOUT_SECONDS", "8"))
    )
    qdrant_url: str = field(
        default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333").rstrip("/")
    )
    qdrant_collection: str = field(
        default_factory=lambda: os.getenv("QDRANT_COLLECTION", "openshift_docs")
    )
    qdrant_vector_size: int = field(
        default_factory=lambda: int(os.getenv("QDRANT_VECTOR_SIZE", "1024"))
    )
    qdrant_distance: str = field(
        default_factory=lambda: os.getenv("QDRANT_DISTANCE", "Cosine")
    )
    qdrant_upsert_batch_size: int = field(
        default_factory=lambda: int(os.getenv("QDRANT_UPSERT_BATCH_SIZE", "128"))
    )
    qdrant_recreate_collection: bool = field(
        default_factory=lambda: os.getenv("QDRANT_RECREATE_COLLECTION", "false").lower()
        in {"1", "true", "yes", "on"}
    )
    llm_endpoint: str = field(
        default_factory=lambda: os.getenv("LLM_ENDPOINT", "").strip().rstrip("/")
    )
    llm_api_key: str = field(
        default_factory=lambda: os.getenv("LLM_API_KEY", "").strip()
    )
    llm_model: str = field(
        default_factory=lambda: os.getenv("LLM_MODEL", "").strip()
    )
    llm_temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2"))
    )
    llm_max_tokens: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "1100"))
    )

    def __post_init__(self) -> None:
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        self.part1_dir.mkdir(parents=True, exist_ok=True)
        self.part2_dir.mkdir(parents=True, exist_ok=True)
        self.part3_dir.mkdir(parents=True, exist_ok=True)
        self.part4_dir.mkdir(parents=True, exist_ok=True)
        self.doc_to_book_drafts_dir.mkdir(parents=True, exist_ok=True)
        self.doc_to_book_capture_dir.mkdir(parents=True, exist_ok=True)
        self.doc_to_book_books_dir.mkdir(parents=True, exist_ok=True)
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

    @property
    def manifest_dir(self) -> Path:
        return self.root_dir / "manifests"

    @property
    def source_manifest_path(self) -> Path:
        return self._resolve_optional_path(
            self.source_manifest_path_override,
            self.manifest_dir / "ocp_ko_4_20_html_single.json",
        )

    @property
    def artifacts_dir(self) -> Path:
        return self._resolve_optional_dir(
            self.artifacts_dir_override,
            self.root_dir / "artifacts",
        )

    @property
    def part1_dir(self) -> Path:
        return self.artifacts_dir / "part1"

    @property
    def part2_dir(self) -> Path:
        return self.artifacts_dir / "part2"

    @property
    def raw_html_dir(self) -> Path:
        return self._resolve_optional_dir(
            self.raw_html_dir_override,
            self.part1_dir / "raw_html",
        )

    @property
    def part3_dir(self) -> Path:
        return self.artifacts_dir / "part3"

    @property
    def part4_dir(self) -> Path:
        return self.artifacts_dir / "part4"

    @property
    def doc_to_book_dir(self) -> Path:
        return self.artifacts_dir / "doc_to_book"

    @property
    def doc_to_book_drafts_dir(self) -> Path:
        return self.doc_to_book_dir / "drafts"

    @property
    def doc_to_book_capture_dir(self) -> Path:
        return self.doc_to_book_dir / "captures"

    @property
    def doc_to_book_books_dir(self) -> Path:
        return self.doc_to_book_dir / "books"

    @property
    def normalized_docs_path(self) -> Path:
        return self.part1_dir / "normalized_docs.jsonl"

    @property
    def chunks_path(self) -> Path:
        return self.part1_dir / "chunks.jsonl"

    @property
    def bm25_corpus_path(self) -> Path:
        return self.part1_dir / "bm25_corpus.jsonl"

    @property
    def preprocessing_log_path(self) -> Path:
        return self.part1_dir / "preprocessing_log.json"

    @property
    def retrieval_log_path(self) -> Path:
        return self.part2_dir / "retrieval_log.jsonl"

    @property
    def part2_smoke_report_path(self) -> Path:
        return self.part2_dir / "smoke_report.json"

    @property
    def part3_answer_log_path(self) -> Path:
        return self.part3_dir / "answer_log.jsonl"

    @property
    def part4_chat_log_path(self) -> Path:
        return self.part4_dir / "chat_turns.jsonl"


def load_settings(root_dir: str | Path) -> Settings:
    env_path = Path(root_dir) / ".env"
    if env_path.exists():
        raw_values: dict[str, str] = {}
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            raw_values[key.strip()] = value.strip().strip('"').strip("'")

        resolved_values: dict[str, str] = {}

        def resolve_value(key: str, stack: set[str]) -> str:
            if key in os.environ:
                return os.environ[key]
            cached = resolved_values.get(key)
            if cached is not None:
                return cached
            raw_value = raw_values.get(key, "")
            if key in stack:
                return raw_value

            def replace_reference(match: re.Match[str]) -> str:
                reference = match.group(1) or match.group(2) or ""
                if reference in os.environ:
                    return os.environ[reference]
                if reference not in raw_values:
                    return ""
                return resolve_value(reference, stack | {key})

            resolved = ENV_REFERENCE_RE.sub(replace_reference, raw_value)
            resolved_values[key] = resolved
            return resolved

        for key in raw_values:
            os.environ.setdefault(key, resolve_value(key, set()))
    return Settings(root_dir=Path(root_dir))
