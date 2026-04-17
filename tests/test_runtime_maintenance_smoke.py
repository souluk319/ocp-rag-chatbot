from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from play_book_studio.app.runtime_maintenance_smoke import (
    build_runtime_maintenance_smoke,
    write_runtime_maintenance_smoke,
)


class RuntimeMaintenanceSmokeTests(unittest.TestCase):
    def test_build_runtime_maintenance_smoke_refreshes_graph_and_probes_health_and_chat(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            health_response = MagicMock()
            health_response.status_code = 200
            health_response.json.return_value = {
                "runtime": {
                    "graph_compact_artifact": {
                        "state": "fresh",
                        "ready": True,
                    }
                }
            }
            chat_response = MagicMock()
            chat_response.status_code = 200
            chat_response.json.return_value = {
                "response_kind": "rag",
                "warnings": [],
                "runtime": {
                    "graph_compact_artifact": {
                        "state": "fresh",
                        "ready": True,
                    }
                },
                "retrieval_trace": {
                    "graph": {
                        "summary": {
                            "adapter_mode": "local_sidecar",
                            "sidecar_relation_count": 1,
                        }
                    }
                },
            }

            with (
                patch(
                    "play_book_studio.app.runtime_maintenance_smoke.refresh_active_runtime_graph_artifacts",
                    return_value={
                        "status": "ok",
                        "compact_sidecar": {
                            "status": "ok",
                            "book_count": 10,
                            "relation_count": 25,
                        },
                    },
                ) as refresh_mock,
                patch(
                    "play_book_studio.app.runtime_maintenance_smoke.graph_sidecar_compact_artifact_status",
                    return_value={
                        "state": "fresh",
                        "ready": True,
                        "relation_count": 25,
                    },
                ),
                patch(
                    "play_book_studio.app.runtime_maintenance_smoke.requests.get",
                    return_value=health_response,
                ) as get_mock,
                patch(
                    "play_book_studio.app.runtime_maintenance_smoke.requests.post",
                    return_value=chat_response,
                ) as post_mock,
            ):
                payload = build_runtime_maintenance_smoke(
                    root,
                    ui_base_url="http://127.0.0.1:8765",
                    query="OpenShift architecture overview",
                )

            refresh_mock.assert_called_once()
            get_mock.assert_called_once_with("http://127.0.0.1:8765/api/health", timeout=10)
            post_mock.assert_called_once()
            self.assertTrue(payload["summary"]["compact_ready"])
            self.assertTrue(payload["summary"]["health_ok"])
            self.assertTrue(payload["summary"]["chat_ok"])
            self.assertTrue(payload["summary"]["ok"])
            self.assertTrue(payload["summary"]["runtime_uses_compact_artifact"])
            self.assertTrue(payload["summary"]["chat_graph_summary_present"])

    def test_write_runtime_maintenance_smoke_persists_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            report_path = root / "reports" / "build_logs" / "runtime_maintenance_smoke.json"
            with patch(
                "play_book_studio.app.runtime_maintenance_smoke.build_runtime_maintenance_smoke",
                return_value={"summary": {"ok": True, "compact_ready": True}},
            ):
                output_path, payload = write_runtime_maintenance_smoke(root)

            self.assertEqual(report_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(True, payload["summary"]["compact_ready"])


if __name__ == "__main__":
    unittest.main()
