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
        trace_panel_tsx = self._read("presentation-ui/src/components/WorkspaceTracePanel.tsx")
        explain_helper_ts = self._read("presentation-ui/src/components/workspaceExplain.ts")
        vite_config = self._read("presentation-ui/vite.config.ts")

        self.assertIn('path="/studio"', app_tsx)
        self.assertIn('path="/workspace"', app_tsx)
        self.assertIn('Navigate to="/studio"', app_tsx)
        self.assertIn("Playbook Library", library_tsx)
        self.assertIn("User Library", library_tsx)
        self.assertIn("Studio", self._read("presentation-ui/src/components/ProductSurfaces.tsx"))
        self.assertIn("Playbot", workspace_tsx)
        self.assertIn("Release Gate Surface", library_tsx)
        self.assertIn("Product Rehearsal", library_tsx)
        self.assertIn("setBookViewer({", library_tsx)
        self.assertIn("CUSTOMER_PACK_UPLOAD_ACCEPT", runtime_api)
        self.assertIn("CUSTOMER_PACK_UPLOAD_ACCEPT", library_tsx)
        self.assertIn("accept={CUSTOMER_PACK_UPLOAD_ACCEPT}", library_tsx)
        self.assertIn("CUSTOMER_PACK_UPLOAD_ACCEPT", workspace_tsx)
        self.assertIn("accept={CUSTOMER_PACK_UPLOAD_ACCEPT}", workspace_tsx)
        self.assertIn("loadBuyerPacket", runtime_api)
        self.assertIn("sendChatStream", runtime_api)
        self.assertIn("loadViewerDocument", runtime_api)
        self.assertIn("loadCustomerPackCapturedPreview", runtime_api)
        self.assertIn("BuyerPacketPreview", runtime_api)
        self.assertIn("product_gate?:", runtime_api)
        self.assertIn("product_rehearsal?:", runtime_api)
        self.assertIn("user_library_book_count?:", runtime_api)
        self.assertIn("user_library_books?:", runtime_api)
        self.assertNotIn("content_base64", runtime_api)
        self.assertNotIn("toRuntimeUrl(`/api/customer-packs/captured?", library_tsx)
        self.assertIn("TruthBadgeBlock", workspace_tsx)
        self.assertIn("WorkspaceTracePanel", workspace_tsx)
        self.assertIn("testMode", workspace_tsx)
        self.assertIn("activeTestTrace", workspace_tsx)
        self.assertIn("RelatedLinkCard", workspace_tsx)
        self.assertIn("Explain", trace_panel_tsx)
        self.assertIn("Overview", trace_panel_tsx)
        self.assertIn("Forensic", trace_panel_tsx)
        self.assertIn("질문 해석", explain_helper_ts)
        self.assertIn("assistant-truth-chip", workspace_css)
        self.assertIn("session-truth-chip", workspace_css)
        self.assertIn("related-link-card", workspace_css)
        self.assertIn("related-link-badge", workspace_css)
        self.assertIn("workspace-trace-panel", workspace_css)
        self.assertIn("test-mode-btn", workspace_css)
        self.assertIn("'/api': 'http://127.0.0.1:8765'", vite_config)
        self.assertIn("'/docs': 'http://127.0.0.1:8765'", vite_config)
        self.assertIn("'/playbooks': 'http://127.0.0.1:8765'", vite_config)
        self.assertIn("'/wiki': 'http://127.0.0.1:8765'", vite_config)
        self.assertNotIn("/buyer-packets", vite_config)

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

        self.assertIn('to="/studio"', hero_tsx)
        self.assertIn("Launch Studio", hero_tsx)
        self.assertNotIn('to="/workspace"', hero_tsx)
        self.assertIn('to="/playbook-library"', surface_tsx)
        self.assertNotIn('href={`${RUNTIME_EXTERNAL_ORIGIN}/data-situation-room`}', surface_tsx)
        self.assertNotIn("Back to Presentation", details_tsx)
        self.assertIn("TEST", workspace_tsx)

    def test_server_keeps_backend_boundary_clean(self) -> None:
        server_source = self._read("src/play_book_studio/app/server.py")

        self.assertIn("FRONTEND_DIST_DIRNAME", server_source)
        self.assertIn("presentation-ui/dist", server_source)
        self.assertIn("webbrowser.open(backend_url)", server_source)
        self.assertIn('"/studio"', server_source)
        self.assertIn('/playbooks/wiki-assets/', server_source)
        self.assertIn('/api/viewer-document', server_source)
        self.assertNotIn("LEGACY_UI_ROUTE_REDIRECTS", server_source)
        self.assertNotIn("BLOCKED_LEGACY_VIEWER_PREFIXES", server_source)
        self.assertNotIn("_viewer_path_to_local_html", server_source)
        self.assertNotIn("internal_active_runtime_markdown_viewer_html", server_source)
        self.assertNotIn("internal_entity_hub_viewer_html", server_source)
        self.assertNotIn("internal_figure_viewer_html", server_source)
        self.assertNotIn("workspace.html", server_source)
