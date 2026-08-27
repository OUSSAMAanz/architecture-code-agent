import unittest
import json
from types import SimpleNamespace

from code_agent.providers import OpenAIProvider, ScriptedDemoProvider, create_provider
from code_agent.tools import TOOL_SCHEMAS


class FakeOutputItem:
    type = "function_call"
    call_id = "call-1"
    name = "list_files"
    arguments = json.dumps({"path": "."})

    def model_dump(self, exclude_none=True):
        return {
            "type": self.type,
            "call_id": self.call_id,
            "name": self.name,
            "arguments": self.arguments,
        }


class FakeResponses:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            output=[FakeOutputItem()],
            output_text="I will inspect the repository.",
        )


class OpenAIProviderAdapterTests(unittest.TestCase):
    def test_converts_responses_function_calls_to_provider_neutral_response(self):
        provider = object.__new__(OpenAIProvider)
        provider.client = SimpleNamespace(responses=FakeResponses())
        provider.model = "test-model"
        provider.max_tokens = 100

        response = provider.respond(
            system="system",
            messages=[{"role": "user", "content": "hello"}],
            tools=TOOL_SCHEMAS[:1],
        )

        self.assertEqual(response.text, "I will inspect the repository.")
        self.assertEqual(response.tool_calls[0].name, "list_files")
        self.assertEqual(response.tool_calls[0].arguments, {"path": "."})
        request = provider.client.responses.kwargs
        self.assertEqual(request["model"], "test-model")
        self.assertEqual(request["tools"][0]["type"], "function")
        self.assertEqual(request["tools"][0]["name"], "list_files")
        self.assertEqual(request["include"], ["reasoning.encrypted_content"])
        self.assertFalse(request["store"])

    def test_factory_returns_offline_provider(self):
        self.assertIsInstance(create_provider("scripted", "unused"), ScriptedDemoProvider)


if __name__ == "__main__":
    unittest.main()
