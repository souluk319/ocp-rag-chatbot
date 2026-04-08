"""원본 HTML을 가져와 fingerprint와 함께 캐시한다.

정규화 전에 코퍼스가 실제로 어디서 오는지 알고 싶다면 가장 먼저 볼 파일이다.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import requests

from .models import SourceManifestEntry
from play_book_studio.config.settings import Settings


def _decode_response_text(response: requests.Response) -> str:
    encoding = response.encoding
    if not encoding or encoding.lower() == "iso-8859-1":
        encoding = response.apparent_encoding or "utf-8"
    response.encoding = encoding
    return response.text


def _resolved_language_from_url(url: str, default: str) -> str:
    normalized = url.replace("\\", "/")
    if "/ko/" in normalized:
        return "ko"
    if "/en/" in normalized:
        return "en"
    return default


def fetch_html_response(url: str, settings: Settings) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, settings.request_retries + 1):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": settings.user_agent},
                timeout=settings.request_timeout_seconds,
            )
            response.raise_for_status()
            return response
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == settings.request_retries:
                break
            time.sleep(settings.request_backoff_seconds * attempt)
    assert last_error is not None
    raise last_error


def fetch_html_text(url: str, settings: Settings) -> str:
    return _decode_response_text(fetch_html_response(url, settings))


def raw_html_path(settings: Settings, book_slug: str) -> Path:
    return settings.raw_html_dir / f"{book_slug}.html"


def raw_html_metadata_path(settings: Settings, book_slug: str) -> Path:
    return settings.raw_html_dir / f"{book_slug}.meta.json"


def _html_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_raw_html_metadata(
    settings: Settings,
    entry: SourceManifestEntry,
    *,
    html: str,
) -> None:
    metadata = {
        "product_slug": entry.product_slug,
        "ocp_version": entry.ocp_version,
        "docs_language": entry.docs_language,
        "source_kind": entry.source_kind,
        "book_slug": entry.book_slug,
        "index_url": entry.index_url,
        "source_url": entry.source_url,
        "resolved_source_url": entry.resolved_source_url,
        "resolved_language": entry.resolved_language,
        "source_state": entry.source_state,
        "source_state_reason": entry.source_state_reason,
        "source_fingerprint": entry.source_fingerprint,
        "raw_html_sha256": _html_sha256(html),
        "fallback_detected": entry.fallback_detected,
        "content_length": len(html),
    }
    raw_html_metadata_path(settings, entry.book_slug).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _metadata_matches_entry(settings: Settings, entry: SourceManifestEntry) -> bool:
    metadata_path = raw_html_metadata_path(settings, entry.book_slug)
    html_path = raw_html_path(settings, entry.book_slug)
    if not metadata_path.exists() or not html_path.exists():
        return False
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return (
        payload.get("ocp_version") == entry.ocp_version
        and payload.get("docs_language") == entry.docs_language
        and payload.get("source_kind") == entry.source_kind
        and payload.get("source_url") == entry.source_url
        and payload.get("source_fingerprint") == entry.source_fingerprint
    )


def collect_entry(entry: SourceManifestEntry, settings: Settings, force: bool = False) -> Path:
    # source URL 또는 fingerprint가 바뀌었을 때만 다시 수집한다.
    # 강제 새로고침이 들어오면 예외적으로 무조건 다시 받는다.
    target = raw_html_path(settings, entry.book_slug)
    if target.exists() and not force and _metadata_matches_entry(settings, entry):
        return target
    response = fetch_html_response(entry.source_url, settings)
    html = _decode_response_text(response)
    resolved_source_url = response.url.rstrip("/")
    resolved_language = _resolved_language_from_url(resolved_source_url, entry.docs_language)
    entry = SourceManifestEntry(
        **{
            **entry.to_dict(),
            "resolved_source_url": resolved_source_url,
            "resolved_language": resolved_language,
            "fallback_detected": entry.docs_language == "ko" and resolved_language == "en",
        }
    )
    target.write_text(html, encoding="utf-8")
    _write_raw_html_metadata(settings, entry, html=html)
    return target
