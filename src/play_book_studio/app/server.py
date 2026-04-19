"""Play Book Studio HTTP runtime entrypoint."""

from __future__ import annotations

from http.server import ThreadingHTTPServer
from pathlib import Path

from play_book_studio.answering.answerer import ChatAnswerer

from .server_handler_factory import _build_handler
from .sessions import ChatSession, SessionStore


def serve(
    *,
    answerer: ChatAnswerer,
    root_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    store = SessionStore(root_dir)
    handler = _build_handler(answerer=answerer, store=store, root_dir=root_dir)
    server = ThreadingHTTPServer((host, port), handler)
    backend_url = f"http://{host}:{port}"
    print(f"Play Book Studio runtime/API server running at {backend_url}")
    if open_browser:
        import webbrowser

        webbrowser.open(backend_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


__all__ = [
    "ChatSession",
    "SessionStore",
    "serve",
]
