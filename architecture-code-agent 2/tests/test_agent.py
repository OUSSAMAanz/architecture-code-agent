import tempfile
import unittest
from pathlib import Path

from code_agent.agent import CodeAgent
from code_agent.models import ModelResponse, ToolCall
from code_agent.providers import ScriptedDemoProvider
from code_agent.validator import validate_repository


class SilentProvider:
    def respond(self, **kwargs):
        return ModelResponse(text="I stopped early")


class FinishesWithoutTestingProvider:
    def respond(self, **kwargs):
        calls = (
            ToolCall("1", "write_file", {"path": "README.md", "content": "# Demo\n"}),
            ToolCall("2", "write_file", {"path": "requirements.txt", "content": "# none\n"}),
            ToolCall("3", "write_file", {"path": "src/app.py", "content": "VALUE = 1\n"}),
            ToolCall("4", "write_file", {"path": "tests/test_app.py", "content": "# test\n"}),
            ToolCall("5", "finish", {"summary": "done"}),
        )
        return ModelResponse(tool_calls=calls)


class AgentLoopTests(unittest.TestCase):
    def test_scripted_provider_generates_and_validates_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = CodeAgent(ScriptedDemoProvider(), root, max_iterations=6).run(
                {"system": "Space Fractions", "requirements": ["FR-1"]}
            )
            self.assertTrue(result.completed, result.validation_errors)
            self.assertEqual(result.iterations, 4)
            self.assertTrue((root / "src" / "server.js").is_file())
            self.assertTrue((root / ".agent" / "transcript.jsonl").is_file())
            self.assertEqual(validate_repository(root), [])

    def test_model_stopping_without_tools_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            result = CodeAgent(SilentProvider(), Path(directory)).run({"system": "Demo"})
            self.assertFalse(result.completed)

    def test_finish_without_running_tests_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            result = CodeAgent(FinishesWithoutTestingProvider(), Path(directory)).run(
                {"system": "Demo"}
            )
            self.assertFalse(result.completed)
            self.assertIn("Tests were not run", result.validation_errors)


if __name__ == "__main__":
    unittest.main()
