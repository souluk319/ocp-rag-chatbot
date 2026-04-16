from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestAppRuntimeUi(unittest.TestCase):
    def _read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_playbook_ui_is_the_main_surface(self) -> None:
        app_tsx = self._read("presentation-ui/src/App.tsx")
        library_tsx = self._read("presentation-ui/src/pages/PlaybookLibraryPage.tsx")
        runtime_api = self._read("presentation-ui/src/lib/runtimeApi.ts")
        workspace_tsx = self._read("presentation-ui/src/pages/WorkspacePage.tsx")
        workspace_css = self._read("presentation-ui/src/pages/WorkspacePage.css")

        self.assertIn('path="/workspace"', app_tsx)
        self.assertIn('path="/studio"', app_tsx)
        self.assertIn('Navigate to="/workspace"', app_tsx)
        self.assertIn("Playbook Library", library_tsx)
        self.assertIn("Release Gate Surface", library_tsx)
        self.assertIn("Owner Demo Rehearsal", library_tsx)
        self.assertIn("setBookViewer({", library_tsx)
        self.assertIn("loadBuyerPacket", runtime_api)
        self.assertIn("sendChatStream", runtime_api)
        self.assertIn("BuyerPacketPreview", runtime_api)
        self.assertIn("buyer_demo_gate?:", runtime_api)
        self.assertIn("owner_demo_rehearsal?:", runtime_api)
        self.assertNotIn("content_base64", runtime_api)
        self.assertIn("TruthBadgeBlock", workspace_tsx)
        self.assertIn("WorkspaceTracePanel", workspace_tsx)
        self.assertIn("testMode", workspace_tsx)
        self.assertIn("activeTestTrace", workspace_tsx)
        self.assertIn("RelatedLinkCard", workspace_tsx)
        self.assertIn("assistant-truth-chip", workspace_css)
        self.assertIn("session-truth-chip", workspace_css)
        self.assertIn("related-link-card", workspace_css)
        self.assertIn("related-link-badge", workspace_css)
        self.assertIn("workspace-trace-panel", workspace_css)
        self.assertIn("test-mode-btn", workspace_css)

    def test_legacy_static_shell_strings_are_not_the_main_ui_contract(self) -> None:
        app_tsx = self._read("presentation-ui/src/App.tsx")
        hero_tsx = self._read("presentation-ui/src/components/Hero.tsx")
        surface_tsx = self._read("presentation-ui/src/components/ProductSurfaces.tsx")
        library_tsx = self._read("presentation-ui/src/pages/PlaybookLibraryPage.tsx")
        workspace_tsx = self._read("presentation-ui/src/pages/WorkspacePage.tsx")
        details_tsx = self._read("presentation-ui/src/pages/ProjectDetailsPage.tsx")

        for legacy_string in [
            "data-situation-room",
            "app-shell",
            "support-surface",
        ]:
            self.assertNotIn(legacy_string, app_tsx)
            self.assertNotIn(legacy_string, hero_tsx)
            self.assertNotIn(legacy_string, surface_tsx)
            self.assertNotIn(legacy_string, library_tsx)
            self.assertNotIn(legacy_string, workspace_tsx)
            self.assertNotIn(legacy_string, details_tsx)

        self.assertIn('to="/workspace"', hero_tsx)
        self.assertIn("Open Workspace", hero_tsx)
        self.assertNotIn('to="/studio"', hero_tsx)
        self.assertIn('to="/playbook-library"', surface_tsx)
        self.assertNotIn('href={`${RUNTIME_EXTERNAL_ORIGIN}/data-situation-room`}', surface_tsx)
        self.assertNotIn("Back to Presentation", details_tsx)
        self.assertIn("TEST", workspace_tsx)

    def test_server_points_legacy_routes_to_the_playbook_ui_origin(self) -> None:
        server_source = self._read("src/play_book_studio/app/server.py")
        cli_source = self._read("src/play_book_studio/cli.py")
        runtime_report_source = self._read("src/play_book_studio/app/runtime_report.py")

        self.assertIn("LEGACY_UI_ROUTE_REDIRECTS", server_source)
        self.assertIn("DEFAULT_PLAYBOOK_UI_ORIGIN", server_source)
        self.assertIn('"/studio": "/workspace"', server_source)
        self.assertIn('"/data-situation-room": "/playbook-library"', server_source)
        self.assertIn("DEFAULT_PLAYBOOK_UI_BASE_URL", cli_source)
        self.assertIn('DEFAULT_PLAYBOOK_UI_BASE_URL = "http://127.0.0.1:5173"', runtime_report_source)
        self.assertNotIn("workspace.html", server_source)
