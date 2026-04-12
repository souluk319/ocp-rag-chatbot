from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.repository_registry import (
    list_repository_favorites,
    remove_repository_favorite,
    save_repository_favorites,
    search_github_repositories,
)
from play_book_studio.app.server_routes import (
    handle_repository_favorites,
    handle_repository_favorites_remove,
    handle_repository_favorites_save,
    handle_repository_search,
)


class _FakeResponse:
    def __init__(self, payload, *, status_code: int = 200, headers: dict[str, str] | None = None):
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):  # noqa: ANN001
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


class _Handler:
    def __init__(self) -> None:
        self.payload = None
        self.status = None

    def _send_json(self, payload, status=None):  # noqa: ANN001
        self.payload = payload
        self.status = status


class TestAppRepositorySearch(unittest.TestCase):
    def _root(self) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        root = Path(tmpdir.name)
        (root / ".env").write_text("ARTIFACTS_DIR=artifacts\nGITHUB_TOKEN=test-token\n", encoding="utf-8")
        return root

    def test_search_github_repositories_reranks_docs_heavy_repo_first(self) -> None:
        root = self._root()

        def fake_get(url, *, headers=None, params=None, timeout=None):  # noqa: ANN001
            del headers, timeout
            if url.endswith("/search/repositories"):
                self.assertIn("openshift", str((params or {}).get("q") or ""))
                return _FakeResponse(
                    {
                        "items": [
                            {
                                "id": 1,
                                "name": "openshift-docs",
                                "full_name": "redhat/openshift-docs",
                                "owner": {"login": "redhat"},
                                "html_url": "https://github.com/redhat/openshift-docs",
                                "description": "Official OpenShift documentation and runbooks",
                                "stargazers_count": 1200,
                                "updated_at": "2026-04-13T00:00:00Z",
                                "language": "AsciiDoc",
                                "default_branch": "main",
                                "topics": ["openshift", "documentation", "runbook"],
                                "archived": False,
                            },
                            {
                                "id": 2,
                                "name": "platform-demo",
                                "full_name": "acme/platform-demo",
                                "owner": {"login": "acme"},
                                "html_url": "https://github.com/acme/platform-demo",
                                "description": "Demo deployment assets",
                                "stargazers_count": 1800,
                                "updated_at": "2026-04-12T00:00:00Z",
                                "language": "TypeScript",
                                "default_branch": "main",
                                "topics": ["demo", "samples"],
                                "archived": False,
                            },
                        ]
                    }
                )
            if url.endswith("/repos/redhat/openshift-docs/contents"):
                return _FakeResponse(
                    [
                        {"name": "README.md", "type": "file"},
                        {"name": "docs", "type": "dir"},
                        {"name": "troubleshooting", "type": "dir"},
                    ]
                )
            if url.endswith("/repos/acme/platform-demo/contents"):
                return _FakeResponse(
                    [
                        {"name": "README.md", "type": "file"},
                        {"name": "examples", "type": "dir"},
                    ]
                )
            raise AssertionError(f"unexpected URL {url}")

        with patch("play_book_studio.app.repository_registry.requests.get", side_effect=fake_get):
            payload = search_github_repositories(root, query="openshift", limit=10)

        self.assertEqual("token", payload["auth_mode"])
        self.assertIn("in:name,description,readme", payload["rewritten_query"])
        self.assertEqual(2, payload["count"])
        self.assertEqual("redhat/openshift-docs", payload["results"][0]["full_name"])
        self.assertTrue(payload["results"][0]["docs_signals"]["has_docs_dir"])
        self.assertEqual("Official Docs", payload["results"][0]["suggested_category"])

    def test_save_and_remove_repository_favorites_persist_category(self) -> None:
        root = self._root()

        saved = save_repository_favorites(
            root,
            {
                "category": "Operations Demo",
                "repositories": [
                    {
                        "id": 10,
                        "name": "platform-demo",
                        "full_name": "acme/platform-demo",
                        "owner_login": "acme",
                        "html_url": "https://github.com/acme/platform-demo",
                        "description": "Demo deployment assets",
                        "stargazers_count": 1800,
                        "updated_at": "2026-04-12T00:00:00Z",
                        "language": "TypeScript",
                        "default_branch": "main",
                        "topics": ["demo", "samples"],
                        "docs_signals": {
                            "score": 5,
                            "inspection_status": "ok",
                            "has_readme": True,
                            "has_docs_dir": False,
                            "has_demo_assets": True,
                            "doc_keyword_hits": 0,
                            "troubleshooting_hits": 0,
                            "demo_hits": 2,
                            "entry_names": ["README.md", "examples"],
                            "summary": "README, demo/example assets",
                        },
                        "suggested_category": "Operations Demo",
                    }
                ],
            },
        )

        self.assertEqual(1, saved["count"])
        self.assertEqual("Operations Demo", saved["items"][0]["favorite_category"])
        listed = list_repository_favorites(root)
        self.assertEqual("acme/platform-demo", listed["items"][0]["full_name"])

        removed = remove_repository_favorite(root, {"full_name": "acme/platform-demo"})
        self.assertEqual(0, removed["count"])

    def test_repository_route_handlers_return_search_and_favorite_payloads(self) -> None:
        root = self._root()
        search_handler = _Handler()
        favorites_handler = _Handler()
        save_handler = _Handler()
        remove_handler = _Handler()

        with patch(
            "play_book_studio.app.server_routes._search_github_repositories",
            return_value={"count": 1, "results": [{"full_name": "redhat/openshift-docs"}]},
        ):
            handle_repository_search(search_handler, "query=openshift&limit=5", root_dir=root)

        self.assertEqual(1, search_handler.payload["count"])
        self.assertEqual("redhat/openshift-docs", search_handler.payload["results"][0]["full_name"])

        handle_repository_favorites_save(
            save_handler,
            {
                "category": "Official Docs",
                "repositories": [{"full_name": "redhat/openshift-docs"}],
            },
            root_dir=root,
        )
        self.assertEqual(1, save_handler.payload["count"])

        handle_repository_favorites(favorites_handler, "", root_dir=root)
        self.assertEqual(1, favorites_handler.payload["count"])

        handle_repository_favorites_remove(
            remove_handler,
            {"full_name": "redhat/openshift-docs"},
            root_dir=root,
        )
        self.assertEqual(0, remove_handler.payload["count"])
