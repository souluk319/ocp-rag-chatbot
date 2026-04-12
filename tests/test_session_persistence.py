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

from play_book_studio.answering.models import AnswerResult
from play_book_studio.app.chat_debug import append_chat_turn_log
from play_book_studio.app.sessions import ChatSession, SessionStore, Turn
from play_book_studio.retrieval.models import SessionContext


class SessionPersistenceTests(unittest.TestCase):
    def test_session_store_recovers_snapshots_after_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            store = SessionStore(root)
            session = ChatSession(
                session_id="session-abc",
                mode="chat",
                context=SessionContext(
                    mode="chat",
                    user_goal="etcd backup",
                    current_topic="backup_and_restore",
                    ocp_version="4.20",
                ),
                history=[
                    Turn(
                        turn_id="turn-1",
                        parent_turn_id="",
                        created_at="2026-04-12T18:00:00",
                        query="etcd 백업은?",
                        mode="chat",
                        answer="etcd 데이터 백업을 먼저 확인합니다.",
                        rewritten_query="etcd 백업",
                        response_kind="grounded",
                    )
                ],
                revision=1,
                updated_at="2026-04-12T18:00:00",
            )

            store.update(session)

            session_snapshot = root / "artifacts" / "runtime" / "sessions" / "session-abc.json"
            recent_snapshot = root / "artifacts" / "runtime" / "recent_chat_session.json"
            self.assertTrue(session_snapshot.exists())
            self.assertTrue(recent_snapshot.exists())

            reloaded = SessionStore(root)
            loaded = reloaded.peek("session-abc")
            self.assertIsNotNone(loaded)
            self.assertEqual("etcd backup", loaded.context.user_goal)
            self.assertEqual("backup_and_restore", loaded.context.current_topic)
            self.assertEqual("etcd 백업은?", loaded.history[0].query)
            self.assertEqual("turn-1", loaded.history[0].turn_id)
            self.assertEqual(1, loaded.revision)
            self.assertEqual("etcd 백업은?", loaded.last_query)

    def test_append_chat_turn_log_writes_audit_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            session = ChatSession(
                session_id="session-xyz",
                mode="chat",
                context=SessionContext(
                    mode="chat",
                    user_goal="replicas 조정",
                    ocp_version="4.20",
                ),
                history=[
                    Turn(
                        turn_id="turn-1",
                        parent_turn_id="",
                        created_at="2026-04-12T18:05:00",
                        query="Deployment replicas를 3에서 5로 바꾸려면?",
                        mode="chat",
                        answer="답변: `oc scale`을 사용하세요.",
                        rewritten_query="Deployment replicas 3 5",
                        response_kind="grounded",
                    )
                ],
                revision=1,
                updated_at="2026-04-12T18:05:00",
            )
            result = AnswerResult(
                query="Deployment replicas를 3에서 5로 바꾸려면?",
                mode="chat",
                answer="답변: `oc scale`을 사용하세요.",
                rewritten_query="Deployment replicas 3 5",
                response_kind="grounded",
                citations=[],
                retrieval_trace={"metrics": {"hybrid": {"count": 1}}},
                pipeline_trace={"llm": {"preferred_provider": "openai-compatible", "last_fallback_used": False}},
            )

            target = append_chat_turn_log(
                root,
                session=session,
                query=result.query,
                result=result,
                context_before=SessionContext(mode="chat", user_goal="replicas 조정", ocp_version="4.20"),
                context_after=session.context,
            )

            row = json.loads(target.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual("chat_turn_audit", row["record_kind"])
            envelope = row["audit_envelope"]
            self.assertEqual("session-xyz", envelope["session_id"])
            self.assertEqual(1, envelope["turn_index"])
            self.assertEqual("turn-1", envelope["turn_id"])
            self.assertEqual("", envelope["parent_turn_id"])
            self.assertTrue(envelope["snapshot_path"].endswith("session-xyz.json"))
            self.assertTrue(envelope["recent_session_path"].endswith("recent_chat_session.json"))
            self.assertEqual("replicas 조정", row["context_after"]["user_goal"])
            self.assertEqual("답변: `oc scale`을 사용하세요.", row["answer"])


if __name__ == "__main__":
    unittest.main()
