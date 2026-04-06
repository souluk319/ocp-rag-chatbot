from __future__ import annotations

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .models import SourceManifestEntry
from ocp_rag.shared.settings import HIGH_VALUE_SLUGS, Settings


BOOK_HREF_RE = re.compile(
    r"^/ko/documentation/openshift_container_platform/4\.20/html/([^/]+)$"
)


def _normalize_space(text: str) -> str:
    return " ".join(text.split())


def _decode_response_text(response: requests.Response) -> str:
    encoding = response.encoding
    if not encoding or encoding.lower() == "iso-8859-1":
        encoding = response.apparent_encoding or "utf-8"
    response.encoding = encoding
    return response.text


def fetch_docs_index(settings: Settings) -> str:
    response = requests.get(
        settings.docs_index_url,
        headers={"User-Agent": settings.user_agent},
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    return _decode_response_text(response)


def parse_manifest_entries(index_html: str, settings: Settings) -> list[SourceManifestEntry]:
    soup = BeautifulSoup(index_html, "html.parser")
    books: dict[str, str] = {}

    for link in soup.find_all("a", href=True):
        href = link["href"].rstrip("/")
        match = BOOK_HREF_RE.match(href)
        if not match:
            continue
        slug = match.group(1)
        title = _normalize_space(link.get_text(" ", strip=True)) or slug
        books.setdefault(slug, title)

    return [
        SourceManifestEntry(
            book_slug=slug,
            title=books[slug],
            source_url=settings.book_url_template.format(slug=slug),
            viewer_path=settings.viewer_path_template.format(slug=slug),
            high_value=slug in HIGH_VALUE_SLUGS,
        )
        for slug in sorted(books)
    ]


def write_manifest(path: Path, entries: list[SourceManifestEntry]) -> None:
    payload = {
        "version": 1,
        "source": "docs.redhat.com Korean OCP 4.20 html-single",
        "count": len(entries),
        "entries": [entry.to_dict() for entry in entries],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_manifest(path: Path) -> list[SourceManifestEntry]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [SourceManifestEntry(**item) for item in payload["entries"]]
