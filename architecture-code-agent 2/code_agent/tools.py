"""Constrained filesystem and test tools exposed to the language model."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


MAX_FILE_BYTES = 200_000


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "list_files",
        "description": "List files already present in the generated repository.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Relative directory path."}},
            "additionalProperties": False,
        },
    },
    {
        "name": "read_file",
        "description": "Read a UTF-8 text file in the generated repository.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "write_file",
        "description": "Create or replace a UTF-8 text file in the generated repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_tests",
        "description": "Run the repository's recognized test command with a timeout.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "finish",
        "description": "Mark generation complete and provide a short summary.",
        "input_schema": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
            "additionalProperties": False,
        },
    },
]


class ToolError(RuntimeError):
    pass


class SafeWorkspace:
    """A workspace boundary that prevents path traversal and arbitrary shell access."""

    def __init__(self, root: Path, timeout_seconds: int = 30) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.finished = False
        self.finish_summary = ""
        self.tests_ran = False
        self.last_test_exit_code: int | None = None

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        handlers: dict[str, Callable[..., str]] = {
            "list_files": self.list_files,
            "read_file": self.read_file,
            "write_file": self.write_file,
            "run_tests": self.run_tests,
            "finish": self.finish,
        }
        if name not in handlers:
            raise ToolError(f"Unknown tool: {name}")
        try:
            return handlers[name](**arguments)
        except TypeError as exc:
            raise ToolError(f"Invalid arguments for {name}: {exc}") from exc

    def _resolve(self, relative_path: str) -> Path:
        path = Path(relative_path)
        if path.is_absolute():
            raise ToolError("Absolute paths are not allowed")
        candidate = (self.root / path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ToolError("Path traversal outside the workspace is not allowed") from exc
        if any(part in {".git", ".env", "secrets"} for part in path.parts):
            raise ToolError("Sensitive or repository-internal paths are not writable")
        return candidate

    def list_files(self, path: str = ".") -> str:
        target = self._resolve(path)
        if not target.exists():
            raise ToolError(f"Path does not exist: {path}")
        if not target.is_dir():
            raise ToolError(f"Not a directory: {path}")
        files = sorted(
            str(item.relative_to(self.root)) + ("/" if item.is_dir() else "")
            for item in target.rglob("*")
            if ".agent" not in item.parts
        )
        return json.dumps(files[:500])

    def read_file(self, path: str) -> str:
        target = self._resolve(path)
        if not target.is_file():
            raise ToolError(f"File does not exist: {path}")
        if target.stat().st_size > MAX_FILE_BYTES:
            raise ToolError(f"File is larger than {MAX_FILE_BYTES} bytes")
        return target.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> str:
        if len(content.encode("utf-8")) > MAX_FILE_BYTES:
            raise ToolError(f"Content is larger than {MAX_FILE_BYTES} bytes")
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {path} ({len(content.encode('utf-8'))} bytes)"

    def run_tests(self) -> str:
        if (self.root / "package.json").is_file():
            # Do not trust and execute an arbitrary model-generated npm script.
            command = ["node", "--test"]
        elif (self.root / "pyproject.toml").is_file() or (self.root / "requirements.txt").is_file():
            command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        else:
            raise ToolError("No supported Python or Node dependency manifest was found")

        try:
            completed = subprocess.run(
                command,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ToolError(f"Could not run tests: {exc}") from exc
        output = (completed.stdout + "\n" + completed.stderr).strip()
        self.tests_ran = True
        self.last_test_exit_code = completed.returncode
        return f"exit_code={completed.returncode}\n{output[-12_000:]}"

    def finish(self, summary: str) -> str:
        self.finished = True
        self.finish_summary = summary
        return "Generation marked complete; final validation will run."
