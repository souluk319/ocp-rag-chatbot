from __future__ import annotations

import time
from pathlib import Path

import requests

from .models import SourceManifestEntry
from .settings import Settings


def _decode_response_text(response: requests.Response) -> str:
    encoding = response.encoding
    if not encoding or encoding.lower() == "iso-8859-1":
        encoding = response.apparent_encoding or "utf-8"
    response.encoding = encoding
    return response.text


def fetch_html_text(url: str, settings: Settings) -> str:
    last_error: Exception | None = None
    for attempt in range(1, settings.request_retries + 1):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": settings.user_agent},
                timeout=settings.request_timeout_seconds,
            )
            response.raise_for_status()
            return _decode_response_text(response)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == settings.request_retries:
                break
            time.sleep(settings.request_backoff_seconds * attempt)
    assert last_error is not None
    raise last_error


def raw_html_path(settings: Settings, book_slug: str) -> Path:
    return settings.raw_html_dir / f"{book_slug}.html"


def collect_entry(entry: SourceManifestEntry, settings: Settings, force: bool = False) -> Path:
    target = raw_html_path(settings, entry.book_slug)
    if target.exists() and not force:
        return target
    html = fetch_html_text(entry.source_url, settings)
    target.write_text(html, encoding="utf-8")
    return target
