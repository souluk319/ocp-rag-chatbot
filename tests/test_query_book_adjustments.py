from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.retrieval.models import SessionContext
from play_book_studio.retrieval.query import query_book_adjustments


class QueryBookAdjustmentsTests(unittest.TestCase):
    def test_rbac_follow_up_uses_session_context_for_security_boosts(self) -> None:
        boosts, penalties = query_book_adjustments(
            "권한이 잘 들어갔는지 확인하는 명령도 알려줘",
            context=SessionContext(
                current_topic="RBAC",
                open_entities=["RBAC"],
                user_goal="특정 namespace에 admin 권한 주는 법 알려줘",
            ),
        )

        self.assertGreaterEqual(boosts.get("authentication_and_authorization", 0.0), 1.42)
        self.assertGreaterEqual(boosts.get("postinstallation_configuration", 0.0), 1.14)
        self.assertLessEqual(penalties.get("role_apis", 1.0), 0.72)


if __name__ == "__main__":
    unittest.main()
