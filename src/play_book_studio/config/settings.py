"""모든 파이프라인 단계가 공유하는 런타임 설정 계약.

`cli.py` 다음으로 이 파일을 보면, 나머지 시스템이 어떤 path, endpoint,
pack 메타데이터, artifact 위치를 바라보는지 빠르게 잡을 수 있다.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from .packs import (
    APP_ID,
    APP_LABEL,
    DEFAULT_DOCS_LANGUAGE,
    DEFAULT_OCP_VERSION,
    GLOBAL_SOURCE_CATALOG_NAME,
    SUPPORTED_SOURCE_CRAWLER_KINDS,
    SUPPORTED_SOURCE_CRAWLER_LANGUAGES,
    SUPPORTED_SOURCE_CRAWLER_VERSIONS,
    default_core_pack,
    resolve_ocp_core_pack,
    source_crawler_packs,
)
from .settings_paths import SettingsPathMixin


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
DEFAULT_CORE_PACK = default_core_pack()
DEFAULT_BOOK_URL_TEMPLATE = DEFAULT_CORE_PACK.book_url_template
DEFAULT_VIEWER_PATH_TEMPLATE = DEFAULT_CORE_PACK.viewer_path_template


def _parse_csv_tuple(value: str, default: tuple[str, ...]) -> tuple[str, ...]:
    parts = tuple(item.strip() for item in value.split(",") if item.strip())
    return parts or default


@dataclass(slots=True)
class Settings(SettingsPathMixin):
    """프로세스 한 번의 시작 기준으로 해석된 불변 런타임 설정."""

    root_dir: Path
    artifacts_dir_override: str = field(
        default_factory=lambda: os.getenv("ARTIFACTS_DIR", "").strip()
    )
    raw_html_dir_override: str = field(
        default_factory=lambda: os.getenv("RAW_HTML_DIR", "").strip()
    )
    source_catalog_path_override: str = field(
        default_factory=lambda: os.getenv("SOURCE_CATALOG_PATH", "").strip()
    )
    source_manifest_path_override: str = field(
        default_factory=lambda: os.getenv("SOURCE_MANIFEST_PATH", "").strip()
    )
    source_catalog_versions_override: str = field(
        default_factory=lambda: os.getenv("SOURCE_CATALOG_VERSIONS", "").strip()
    )
    source_catalog_languages_override: str = field(
        default_factory=lambda: os.getenv("SOURCE_CATALOG_LANGUAGES", "").strip()
    )
    source_catalog_kinds_override: str = field(
        default_factory=lambda: os.getenv("SOURCE_CATALOG_KINDS", "").strip()
    )
    ocp_version: str = field(
        default_factory=lambda: os.getenv("OCP_VERSION", DEFAULT_OCP_VERSION).strip()
    )
    docs_language: str = field(
        default_factory=lambda: os.getenv("DOCS_LANGUAGE", DEFAULT_DOCS_LANGUAGE).strip()
    )
    docs_index_url_template: str = field(
        default_factory=lambda: DEFAULT_CORE_PACK.docs_index_url_template
    )
    book_url_template_str: str = field(
        default_factory=lambda: os.getenv("BOOK_URL_TEMPLATE", DEFAULT_BOOK_URL_TEMPLATE)
    )
    viewer_path_template_str: str = field(
        default_factory=lambda: os.getenv("VIEWER_PATH_TEMPLATE", DEFAULT_VIEWER_PATH_TEMPLATE)
    )
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
        default_factory=lambda: os.getenv("QDRANT_COLLECTION", DEFAULT_CORE_PACK.qdrant_collection)
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
    reranker_enabled: bool = field(
        default_factory=lambda: os.getenv("RERANKER_ENABLED", "false").lower()
        in {"1", "true", "yes", "on"}
    )
    reranker_model: str = field(
        default_factory=lambda: os.getenv(
            "RERANKER_MODEL",
            "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
        ).strip()
    )
    reranker_top_n: int = field(
        default_factory=lambda: int(os.getenv("RERANKER_TOP_N", "12"))
    )
    reranker_batch_size: int = field(
        default_factory=lambda: int(os.getenv("RERANKER_BATCH_SIZE", "8"))
    )
    reranker_device: str = field(
        default_factory=lambda: os.getenv("RERANKER_DEVICE", "auto").strip()
    )

    @property
    def app_id(self) -> str:
        return APP_ID

    @property
    def app_label(self) -> str:
        return APP_LABEL

    @property
    def active_pack(self):
        return resolve_ocp_core_pack(version=self.ocp_version, language=self.docs_language)

    @property
    def active_pack_id(self) -> str:
        return self.active_pack.pack_id

    @property
    def active_pack_label(self) -> str:
        return self.active_pack.pack_label

    @property
    def viewer_path_prefix(self) -> str:
        return self.active_pack.viewer_path_prefix

    @property
    def supported_ocp_versions(self) -> tuple[str, ...]:
        return _parse_csv_tuple(
            self.source_catalog_versions_override,
            SUPPORTED_SOURCE_CRAWLER_VERSIONS,
        )

    @property
    def supported_docs_languages(self) -> tuple[str, ...]:
        return _parse_csv_tuple(
            self.source_catalog_languages_override,
            SUPPORTED_SOURCE_CRAWLER_LANGUAGES,
        )

    @property
    def supported_source_kinds(self) -> tuple[str, ...]:
        return _parse_csv_tuple(
            self.source_catalog_kinds_override,
            SUPPORTED_SOURCE_CRAWLER_KINDS,
        )

    @property
    def source_catalog_scope(self):
        return source_crawler_packs(
            versions=self.supported_ocp_versions,
            languages=self.supported_docs_languages,
        )

    @property
    def docs_index_url(self) -> str:
        return self.docs_index_url_template.format(
            version=self.ocp_version,
            lang=self.docs_language
        )

    @property
    def book_url_template(self) -> str:
        return self.book_url_template_str.format(
            version=self.ocp_version,
            lang=self.docs_language,
            slug="{slug}"
        )

    @property
    def viewer_path_template(self) -> str:
        return self.viewer_path_template_str.format(
            version=self.ocp_version,
            lang=self.docs_language,
            slug="{slug}"
        )

def load_effective_env(root_dir: str | Path) -> dict[str, str]:
    """`.env` overlay를 반영한 환경 맵을 반환한다.

    전역 `os.environ`은 건드리지 않고, 호출자가 필요한 곳에만 같은 해석 결과를
    재사용할 수 있게 만든다.
    """

    root_path = Path(root_dir)
    env_path = root_path / ".env"
    effective_env: dict[str, str] = dict(os.environ)
    if not env_path.exists():
        return effective_env

    raw_values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        raw_values[key.strip()] = value.strip().strip('"').strip("'")

    resolved_values: dict[str, str] = {}

    def resolve_value(key: str, stack: set[str]) -> str:
        cached = resolved_values.get(key)
        if cached is not None:
            return cached
        raw_value = raw_values.get(key, "")
        if key in stack:
            return raw_value

        def replace_reference(match: re.Match[str]) -> str:
            reference = match.group(1) or match.group(2) or ""
            if reference in raw_values:
                return resolve_value(reference, stack | {key})
            return effective_env.get(reference, "")

        resolved = ENV_REFERENCE_RE.sub(replace_reference, raw_value)
        resolved_values[key] = resolved
        return resolved

    for key in raw_values:
        effective_env[key] = resolve_value(key, set())
    return effective_env


def load_settings(root_dir: str | Path) -> Settings:
    # `.env`를 읽어 별도 overlay로 해석하고, `os.environ` 자체는 건드리지 않는다.
    # 그래야 endpoint 변경이 재현 가능하고 숨은 전역 부작용을 막을 수 있다.
    root_path = Path(root_dir)
    effective_env = load_effective_env(root_path)

    return Settings(
        root_dir=root_path,
        artifacts_dir_override=effective_env.get("ARTIFACTS_DIR", "").strip(),
        raw_html_dir_override=effective_env.get("RAW_HTML_DIR", "").strip(),
        source_catalog_path_override=effective_env.get("SOURCE_CATALOG_PATH", "").strip(),
        source_manifest_path_override=effective_env.get("SOURCE_MANIFEST_PATH", "").strip(),
        source_catalog_versions_override=effective_env.get("SOURCE_CATALOG_VERSIONS", "").strip(),
        source_catalog_languages_override=effective_env.get("SOURCE_CATALOG_LANGUAGES", "").strip(),
        source_catalog_kinds_override=effective_env.get("SOURCE_CATALOG_KINDS", "").strip(),
        ocp_version=effective_env.get("OCP_VERSION", DEFAULT_OCP_VERSION).strip(),
        docs_language=effective_env.get("DOCS_LANGUAGE", DEFAULT_DOCS_LANGUAGE).strip(),
        book_url_template_str=effective_env.get("BOOK_URL_TEMPLATE", DEFAULT_BOOK_URL_TEMPLATE),
        viewer_path_template_str=effective_env.get("VIEWER_PATH_TEMPLATE", DEFAULT_VIEWER_PATH_TEMPLATE),
        embedding_base_url=effective_env.get("EMBEDDING_BASE_URL", "").strip().rstrip("/"),
        embedding_model=effective_env.get("EMBEDDING_MODEL", "dragonkue/bge-m3-ko"),
        embedding_device=effective_env.get("EMBEDDING_DEVICE", "auto").strip(),
        embedding_api_key=effective_env.get("EMBEDDING_API_KEY", "").strip(),
        embedding_batch_size=int(effective_env.get("EMBEDDING_BATCH_SIZE", "32")),
        embedding_timeout_seconds=float(effective_env.get("EMBEDDING_TIMEOUT_SECONDS", "8")),
        qdrant_url=effective_env.get("QDRANT_URL", "http://localhost:6333").rstrip("/"),
        qdrant_collection=effective_env.get("QDRANT_COLLECTION", DEFAULT_CORE_PACK.qdrant_collection),
        qdrant_vector_size=int(effective_env.get("QDRANT_VECTOR_SIZE", "1024")),
        qdrant_distance=effective_env.get("QDRANT_DISTANCE", "Cosine"),
        qdrant_upsert_batch_size=int(effective_env.get("QDRANT_UPSERT_BATCH_SIZE", "128")),
        qdrant_recreate_collection=effective_env.get("QDRANT_RECREATE_COLLECTION", "false").lower()
        in {"1", "true", "yes", "on"},
        llm_endpoint=effective_env.get("LLM_ENDPOINT", "").strip().rstrip("/"),
        llm_api_key=effective_env.get("LLM_API_KEY", "").strip(),
        llm_model=effective_env.get("LLM_MODEL", "").strip(),
        llm_temperature=float(effective_env.get("LLM_TEMPERATURE", "0.2")),
        llm_max_tokens=int(effective_env.get("LLM_MAX_TOKENS", "1100")),
        reranker_enabled=effective_env.get("RERANKER_ENABLED", "false").lower()
        in {"1", "true", "yes", "on"},
        reranker_model=effective_env.get(
            "RERANKER_MODEL",
            "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
        ).strip(),
        reranker_top_n=int(effective_env.get("RERANKER_TOP_N", "12")),
        reranker_batch_size=int(effective_env.get("RERANKER_BATCH_SIZE", "8")),
        reranker_device=effective_env.get("RERANKER_DEVICE", "auto").strip(),
    )
