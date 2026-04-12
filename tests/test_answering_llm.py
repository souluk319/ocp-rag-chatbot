from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from _support_answering import LLMClient, Settings, _FakeResponse

class TestAnsweringLlm(unittest.TestCase):
    def test_llm_client_parses_chat_completions_response(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local/v1"
        settings.llm_model = "demo-model"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        with patch.object(
            requests,
            "post",
            return_value=_FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "답변: 테스트입니다. [1]",
                            }
                        }
                    ]
                }
            ),
        ) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("답변: 테스트입니다. [1]", content)
        self.assertEqual(
            "http://llm.local/v1/chat/completions",
            mocked_post.call_args.args[0],
        )
        self.assertEqual({}, mocked_post.call_args.kwargs["headers"])
        self.assertFalse(mocked_post.call_args.kwargs["json"]["reasoning"])
        self.assertFalse(
            mocked_post.call_args.kwargs["json"]["chat_template_kwargs"]["enable_thinking"]
        )

    def test_llm_client_retries_without_reasoning_controls(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local:8080/v1"
        settings.llm_model = "demo-model"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        responses = [
            _FakeResponse(
                {"error": {"message": "json: cannot unmarshal bool into Go struct field ChatCompletionRequest.reasoning of type openai.Reasoning"}},
                status_code=400,
                text="json: cannot unmarshal bool into Go struct field ChatCompletionRequest.reasoning of type openai.Reasoning",
            ),
            _FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "답변: 테스트입니다. [1]",
                            }
                        }
                    ]
                }
            ),
        ]

        with patch.object(requests, "post", side_effect=responses) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("답변: 테스트입니다. [1]", content)
        self.assertIn("reasoning", mocked_post.call_args_list[0].kwargs["json"])
        self.assertNotIn("reasoning", mocked_post.call_args_list[1].kwargs["json"])
        self.assertNotIn("chat_template_kwargs", mocked_post.call_args_list[1].kwargs["json"])

    def test_llm_client_sends_bearer_authorization_when_api_key_is_set(self) -> None:
        settings = Settings(root_dir=ROOT)
        settings.llm_endpoint = "http://llm.local/v1"
        settings.llm_model = "demo-model"
        settings.llm_api_key = "llm-secret"

        client = LLMClient(settings)

        import requests
        from unittest.mock import patch

        with patch.object(
            requests,
            "post",
            return_value=_FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": "답변: 테스트입니다. [1]",
                            }
                        }
                    ]
                }
            ),
        ) as mocked_post:
            content = client.generate([{"role": "user", "content": "질문"}])

        self.assertEqual("답변: 테스트입니다. [1]", content)
        self.assertEqual(
            {"Authorization": "Bearer llm-secret"},
            mocked_post.call_args.kwargs["headers"],
        )
