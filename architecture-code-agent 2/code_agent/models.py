"""Small provider-neutral data models used by the agent loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ModelResponse:
    text: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    raw_content: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ToolResult:
    tool_call_id: str
    name: str
    content: str
    is_error: bool = False


@dataclass(frozen=True)
class AgentResult:
    completed: bool
    iterations: int
    summary: str
    validation_errors: tuple[str, ...] = ()
