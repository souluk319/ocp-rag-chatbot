from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest.embedding import EmbeddingClient
from ocp_rag.shared.settings import Settings


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self) -> dict:
        return self._payload


class _FakeSentenceModel:
    def encode(self, texts, normalize_embeddings=False, show_progress_bar=False):  # noqa: ANN001
        self.last_call = {
            "texts": list(texts),
            "normalize_embeddings": normalize_embeddings,
            "show_progress_bar": show_progress_bar,
        }
        return [[0.1, 0.2] for _ in texts]


class LocalQueryEmbeddingTests(unittest.TestCase):
    def test_embedding_client_prefers_local_for_single_query_embedding(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.embedding_base_url = "http://embed.local/v1"
        settings.embedding_model = "dragonkue/bge-m3-ko"
        fake_model = _FakeSentenceModel()

        with (
            patch(
                "ocp_rag.ingest.embedding.requests.post",
                side_effect=AssertionError("remote should not be called for single-query embeddings"),
            ),
            patch("ocp_rag.ingest.embedding.load_sentence_model", return_value=fake_model),
        ):
            client = EmbeddingClient(settings)
            vectors = client.embed_texts(["query text"])

        self.assertEqual([[0.1, 0.2]], vectors)
        self.assertEqual(["query text"], fake_model.last_call["texts"])

    def test_embedding_client_falls_back_to_local_model_when_remote_fails(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.embedding_base_url = "http://embed.local/v1"
        settings.embedding_model = "dragonkue/bge-m3-ko"
        fake_model = _FakeSentenceModel()

        with (
            patch(
                "ocp_rag.ingest.embedding.requests.post",
                return_value=_FakeResponse(500, {"error": "down"}),
            ),
            patch("ocp_rag.ingest.embedding.load_sentence_model", return_value=fake_model),
        ):
            client = EmbeddingClient(settings)
            vectors = client.embed_texts(["a", "b"])

        self.assertEqual([[0.1, 0.2], [0.1, 0.2]], vectors)
        self.assertEqual(["a", "b"], fake_model.last_call["texts"])
        self.assertFalse(fake_model.last_call["normalize_embeddings"])

    def test_embedding_client_uses_local_model_when_remote_base_url_is_empty(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.embedding_base_url = ""
        settings.embedding_model = "dragonkue/bge-m3-ko"
        fake_model = _FakeSentenceModel()

        with patch("ocp_rag.ingest.embedding.load_sentence_model", return_value=fake_model):
            client = EmbeddingClient(settings)
            vectors = client.embed_texts(["query text"])

        self.assertEqual([[0.1, 0.2]], vectors)
        self.assertEqual(["query text"], fake_model.last_call["texts"])


if __name__ == "__main__":
    unittest.main()
