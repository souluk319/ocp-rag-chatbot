from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.app.source_books import build_chat_navigation_links, build_chat_section_links


class ChatNavigationLinkTests(unittest.TestCase):
    def test_navigation_links_prefer_direct_citation_books(self) -> None:
        citations = [
            {
                "book_slug": "authentication_and_authorization",
                "book_title": "인증 및 권한 부여",
                "href": "/playbooks/wiki-runtime/active/authentication_and_authorization/index.html#user-role",
                "section": "사용자 역할 추가",
                "section_path_label": "인증 및 권한 부여 > 사용자 역할 추가",
                "source_label": "인증 및 권한 부여 · 인증 및 권한 부여 > 사용자 역할 추가",
            }
        ]

        links = build_chat_navigation_links(ROOT, citations)

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["label"], "인증 및 권한 부여")
        self.assertTrue(links[0]["href"].startswith("/playbooks/wiki-runtime/active/authentication_and_authorization/index.html"))

    def test_section_links_prefer_direct_citation_sections(self) -> None:
        citations = [
            {
                "book_slug": "authentication_and_authorization",
                "book_title": "인증 및 권한 부여",
                "href": "/playbooks/wiki-runtime/active/authentication_and_authorization/index.html#user-role",
                "section": "사용자 역할 추가",
                "section_path_label": "인증 및 권한 부여 > 사용자 역할 추가",
                "source_label": "인증 및 권한 부여 · 인증 및 권한 부여 > 사용자 역할 추가",
            }
        ]

        links = build_chat_section_links(ROOT, citations)

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["label"], "사용자 역할 추가")
        self.assertEqual(
            links[0]["href"],
            "/playbooks/wiki-runtime/active/authentication_and_authorization/index.html#user-role",
        )


if __name__ == "__main__":
    unittest.main()
