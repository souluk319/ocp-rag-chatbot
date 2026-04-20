from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from play_book_studio.app import server


class _FakeReranker:
    def __init__(self) -> None:
        self.model_name = "fake-reranker"
        self.warmup_calls = 0

    def warmup(self) -> bool:
        self.warmup_calls += 1
        return True


class _FakeThread:
    def __init__(self, *, target, args, name, daemon) -> None:
        self.target = target
        self.args = args
        self.name = name
        self.daemon = daemon
        self.start_calls = 0

    def start(self) -> None:
        self.start_calls += 1


def test_start_runtime_warmup_skips_when_reranker_missing() -> None:
    answerer = SimpleNamespace(retriever=SimpleNamespace(reranker=None))

    with patch("play_book_studio.app.server.threading.Thread") as thread_mock:
        thread = server._start_runtime_warmup(answerer)

    assert thread is None
    thread_mock.assert_not_called()


def test_start_runtime_warmup_starts_daemon_thread_when_reranker_present() -> None:
    answerer = SimpleNamespace(retriever=SimpleNamespace(reranker=_FakeReranker()))
    created_threads: list[_FakeThread] = []

    def _build_thread(*, target, args, name, daemon):
        thread = _FakeThread(target=target, args=args, name=name, daemon=daemon)
        created_threads.append(thread)
        return thread

    with patch("play_book_studio.app.server.threading.Thread", side_effect=_build_thread):
        thread = server._start_runtime_warmup(answerer)

    assert thread is created_threads[0]
    assert thread.target is server._warmup_runtime_components
    assert thread.args == (answerer,)
    assert thread.name == "pbs-runtime-warmup"
    assert thread.daemon is True
    assert thread.start_calls == 1

