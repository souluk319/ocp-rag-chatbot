from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.embedding import EmbeddingClient
from play_book_studio.config.settings import Settings


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self) -> dict:
        return self._payload


class EmbeddingTests(unittest.TestCase):
    def test_embedding_client_uses_remote_endpoint_and_falls_back_to_short_model_name(self) -> None:
        calls: list[tuple[str, list[str]]] = []

        def fake_post(url, json, headers, timeout):  # noqa: ANN001
            self.assertEqual("http://embed.local/v1/embeddings", url)
            self.assertEqual(8.0, timeout)
            self.assertEqual({}, headers)
            calls.append((json["model"], list(json["input"])))
            if json["model"] == "dragonkue/bge-m3-ko":
                return _FakeResponse(404, {"error": "unknown model"})
            return _FakeResponse(
                200,
                {
                    "data": [
                        {"embedding": [float(index), float(index + 1)]}
                        for index, _ in enumerate(json["input"])
                    ]
                },
            )

        settings = Settings(root_dir=ROOT)
        settings.embedding_base_url = "http://embed.local/v1"
        settings.embedding_batch_size = 2
        settings.embedding_model = "dragonkue/bge-m3-ko"

        with patch("play_book_studio.ingestion.embedding.requests.post", side_effect=fake_post):
            client = EmbeddingClient(settings)
            vectors = client.embed_texts(["a", "b", "c"])

        self.assertEqual(
            [
                ("dragonkue/bge-m3-ko", ["a", "b"]),
                ("bge-m3-ko", ["a", "b"]),
                ("dragonkue/bge-m3-ko", ["c"]),
                ("bge-m3-ko", ["c"]),
            ],
            calls,
        )
        self.assertEqual([[0.0, 1.0], [1.0, 2.0], [0.0, 1.0]], vectors)

    def test_embedding_client_sends_bearer_authorization_when_api_key_is_set(self) -> None:
        captured_headers = None

        def fake_post(url, json, headers, timeout):  # noqa: ANN001
            nonlocal captured_headers
            captured_headers = headers
            return _FakeResponse(200, {"data": [{"embedding": [0.0, 1.0]}]})

        settings = Settings(root_dir=ROOT)
        settings.embedding_base_url = "http://embed.local/v1"
        settings.embedding_model = "dragonkue/bge-m3-ko"
        settings.embedding_api_key = "embed-secret"

        with patch("play_book_studio.ingestion.embedding.requests.post", side_effect=fake_post):
            client = EmbeddingClient(settings)
            vectors = client.embed_texts(["a"])

        self.assertEqual({"Authorization": "Bearer embed-secret"}, captured_headers)
        self.assertEqual([[0.0, 1.0]], vectors)

    def test_embedding_client_can_use_local_sentence_transformer_when_remote_is_missing(self) -> None:
        class _FakeSentenceModel:
            def encode(self, texts, batch_size, show_progress_bar, convert_to_numpy):  # noqa: ANN001
                self.called = {
                    "texts": list(texts),
                    "batch_size": batch_size,
                    "show_progress_bar": show_progress_bar,
                    "convert_to_numpy": convert_to_numpy,
                }
                return [[0.1, 0.2], [0.3, 0.4]]

        fake_model = _FakeSentenceModel()
        settings = Settings(root_dir=ROOT)
        settings.embedding_base_url = ""
        settings.embedding_model = "dragonkue/bge-m3-ko"
        settings.embedding_device = "cpu"

        with patch("play_book_studio.ingestion.embedding.load_sentence_model", return_value=fake_model) as loader:
            client = EmbeddingClient(settings)
            vectors = client.embed_texts(["a", "b"])

        loader.assert_called_once_with("dragonkue/bge-m3-ko", "cpu")
        self.assertEqual([[0.1, 0.2], [0.3, 0.4]], vectors)
