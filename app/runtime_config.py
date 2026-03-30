from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        cleaned = value.strip().strip("'").strip('"')
        values[key.strip()] = cleaned
    return values


@lru_cache(maxsize=1)
def _repo_env() -> dict[str, str]:
    return _parse_env_file(_repo_root() / ".env")


def _get_env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip()

    file_values = _repo_env()
    for name in names:
        value = file_values.get(name, "")
        if value:
            return value.strip()

    return default.strip()


def _get_bool(*names: str, default: bool = False) -> bool:
    raw = _get_env(*names, default="1" if default else "0")
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class RuntimeConfig:
    company_base_url: str
    chat_model: str
    embedding_model: str
    company_bearer_token: str
    request_timeout_seconds: float
    allow_local_chat_fallback: bool

    def runtime_mode(self) -> str:
        if self.allow_local_chat_fallback:
            return "company-plus-explicit-local-fallback"
        return "company-only"

    def missing_required_keys(self) -> list[str]:
        missing: list[str] = []
        if not self.company_base_url:
            missing.append("LLM_EP_COMPANY_URL")
        if not self.chat_model:
            missing.append("LLM_EP_COMPANY_MODEL")
        if not self.embedding_model:
            missing.append("EMBEDDING_MODEL")
        return missing

    def to_health_dict(self) -> dict[str, object]:
        return {
            "company_base_url_configured": bool(self.company_base_url),
            "chat_model_configured": bool(self.chat_model),
            "embedding_model_configured": bool(self.embedding_model),
            "company_token_configured": bool(self.company_bearer_token),
            "local_chat_fallback": self.allow_local_chat_fallback,
            "runtime_mode": self.runtime_mode(),
            "missing_required_keys": self.missing_required_keys(),
        }


def load_runtime_config() -> RuntimeConfig:
    timeout_raw = _get_env("OD_BRIDGE_TIMEOUT_SECONDS", default="120")
    try:
        timeout_value = float(timeout_raw)
    except ValueError:
        timeout_value = 120.0

    return RuntimeConfig(
        company_base_url=_get_env("OD_COMPANY_BASE_URL", "LLM_EP_COMPANY_URL", "LLM_ENDPOINT"),
        chat_model=_get_env("OD_CHAT_MODEL", "LLM_EP_COMPANY_MODEL", "LLM_MODEL"),
        embedding_model=_get_env("OD_EMBEDDING_MODEL", "EMBEDDING_MODEL"),
        company_bearer_token=_get_env("OD_COMPANY_BEARER_TOKEN", "LLM_EP_COMPANY_BEARER_TOKEN"),
        request_timeout_seconds=timeout_value,
        allow_local_chat_fallback=_get_bool("OD_ALLOW_LOCAL_CHAT_FALLBACK", default=False),
    )
