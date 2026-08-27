"""The provider-neutral model/tool/result loop at the center of the assignment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AgentResult, ToolResult
from .prompts import SYSTEM_PROMPT, initial_prompt
from .providers import Provider
from .tools import TOOL_SCHEMAS, SafeWorkspace, ToolError
from .validator import validate_repository


class CodeAgent:
    def __init__(self, provider: Provider, output_dir: Path, max_iterations: int = 12) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be positive")
        self.provider = provider
        self.workspace = SafeWorkspace(output_dir)
        self.max_iterations = max_iterations
        self.events: list[dict[str, Any]] = []

    def run(self, specification: dict[str, Any]) -> AgentResult:
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": initial_prompt(specification)}
        ]
        self._write_agent_artifact("architecture.json", json.dumps(specification, indent=2) + "\n")

        for iteration in range(1, self.max_iterations + 1):
            response = self.provider.respond(
                system=SYSTEM_PROMPT,
                messages=messages,
                tools=TOOL_SCHEMAS,
            )
            self._record(
                "model_response",
                iteration=iteration,
                text=response.text,
                tool_names=[call.name for call in response.tool_calls],
            )
            if response.raw_content:
                messages.extend(response.raw_content)
            elif response.text:
                messages.append({"role": "assistant", "content": response.text})

            if not response.tool_calls:
                errors = validate_repository(self.workspace.root)
                return self._result(False, iteration, response.text or "Model stopped without finishing", errors)

            tool_results: list[ToolResult] = []
            for call in response.tool_calls:
                try:
                    content = self.workspace.execute(call.name, call.arguments)
                    result = ToolResult(call.id, call.name, content)
                except (ToolError, OSError, ValueError) as exc:
                    result = ToolResult(call.id, call.name, str(exc), is_error=True)
                tool_results.append(result)
                self._record(
                    "tool_result",
                    iteration=iteration,
                    tool=result.name,
                    is_error=result.is_error,
                    content=result.content,
                )

            messages.extend(
                {
                    "type": "function_call_output",
                    "call_id": result.tool_call_id,
                    "output": (
                        f"ERROR: {result.content}" if result.is_error else result.content
                    ),
                }
                for result in tool_results
            )

            if self.workspace.finished:
                errors = validate_repository(self.workspace.root)
                if not self.workspace.tests_ran:
                    errors.append("Tests were not run")
                elif self.workspace.last_test_exit_code != 0:
                    errors.append(
                        f"Tests failed with exit code {self.workspace.last_test_exit_code}"
                    )
                return self._result(
                    not errors,
                    iteration,
                    self.workspace.finish_summary,
                    errors,
                )

        errors = validate_repository(self.workspace.root)
        return self._result(False, self.max_iterations, "Maximum iterations reached", errors)

    def _record(self, event: str, **payload: Any) -> None:
        self.events.append({"event": event, **payload})
        rendered = "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in self.events)
        self._write_agent_artifact("transcript.jsonl", rendered)

    def _write_agent_artifact(self, name: str, content: str) -> None:
        directory = self.workspace.root / ".agent"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(content, encoding="utf-8")

    def _result(
        self,
        completed: bool,
        iterations: int,
        summary: str,
        errors: list[str],
    ) -> AgentResult:
        result = AgentResult(completed, iterations, summary, tuple(errors))
        self._write_agent_artifact(
            "result.json",
            json.dumps(
                {
                    "completed": result.completed,
                    "iterations": result.iterations,
                    "summary": result.summary,
                    "validation_errors": list(result.validation_errors),
                },
                indent=2,
            )
            + "\n",
        )
        return result
