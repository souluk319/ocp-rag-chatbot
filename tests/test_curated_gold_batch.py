from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import Settings
from play_book_studio.ingestion.curated_gold_batch import (
    CURATED_GOLD_PROMOTION_STRATEGY,
    promote_curated_source_bundle,
)
from play_book_studio.ingestion.models import SourceManifestEntry


class CuratedGoldBatchTests(unittest.TestCase):
    def test_promote_curated_source_bundle_marks_dossier_as_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(root_dir=Path(tmpdir))
            dossier_path = settings.bronze_dir / "source_bundles" / "etcd" / "dossier.json"
            dossier_path.parent.mkdir(parents=True, exist_ok=True)
            dossier_path.write_text(
                json.dumps(
                    {
                        "slug": "etcd",
                        "current_status": {
                            "content_status": "blocked",
                            "gap_lane": "manual_review_first",
                            "title": "etcd",
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            entry = SourceManifestEntry(
                book_slug="etcd",
                title="etcd 백업 및 복구 플레이북",
                source_url="https://docs.redhat.com/ko/documentation/openshift_container_platform/4.20/html-single/etcd/index",
                source_id="openshift_container_platform:4.20:ko:etcd:curated_gold_v1",
                source_lane="applied_playbook",
                source_type="manual_synthesis",
                updated_at="2026-04-10T00:00:00Z",
                translation_source_url="https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html-single/etcd/index",
            )

            payload = promote_curated_source_bundle(settings, entry)

            self.assertIsNotNone(payload)
            refreshed = json.loads(dossier_path.read_text(encoding="utf-8"))
            current_status = refreshed["current_status"]
            self.assertEqual("approved_ko", current_status["content_status"])
            self.assertEqual("approved", current_status["gap_lane"])
            self.assertEqual(CURATED_GOLD_PROMOTION_STRATEGY, current_status["promotion_strategy"])
            self.assertEqual("approved", current_status["review_status"])
            self.assertEqual("approved_ko", refreshed["promotion"]["status"])


if __name__ == "__main__":
    unittest.main()
