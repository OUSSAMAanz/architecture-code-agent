"""Turn the supplied Markdown architecture documents into structured JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
FENCE_RE = re.compile(r"```([\w+-]*)\s*\n(.*?)```", re.DOTALL)
REQ_RE = re.compile(r"\b(?:FR|NFR|ASR)-\d+\b")
COMPONENT_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*Component\b")
PLANTUML_RE = re.compile(
    r"```plantuml\s*\n\s*@startuml(?:\s+([^\s]+))?\s*\n(.*?)@enduml\s*\n```",
    re.DOTALL | re.IGNORECASE,
)


class ArchitectureParser:
    """Parse the two assignment inputs without relying on an LLM."""

    def parse_files(self, architecture_path: Path, views_path: Path) -> dict[str, Any]:
        architecture_text = architecture_path.read_text(encoding="utf-8")
        views_text = views_path.read_text(encoding="utf-8")
        return self.parse(architecture_text, views_text)

    def parse(self, architecture_text: str, views_text: str) -> dict[str, Any]:
        architecture_sections = self._sections(architecture_text)
        views_sections = self._sections(views_text)
        requirements = sorted(set(REQ_RE.findall(architecture_text)))
        components = sorted(set(COMPONENT_RE.findall(architecture_text + "\n" + views_text)))
        diagrams = self._diagrams(views_text)

        return {
            "schema_version": "1.0",
            "system": self._system_name(architecture_text),
            "requirements": requirements,
            "components": components,
            "architecture": {
                "sections": architecture_sections,
                "code_blocks": self._code_blocks(architecture_text),
            },
            "views": {
                "sections": views_sections,
                "diagrams": diagrams,
            },
            "statistics": {
                "requirement_count": len(requirements),
                "component_count": len(components),
                "diagram_count": len(diagrams),
            },
        }

    @staticmethod
    def to_json(data: dict[str, Any]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    @staticmethod
    def _system_name(text: str) -> str:
        match = re.search(r"\bThe\s+([A-Z][A-Za-z0-9 ]+?)\s+system\b", text)
        return match.group(1).strip() if match else "Generated Project"

    @staticmethod
    def _sections(text: str) -> list[dict[str, Any]]:
        matches = list(HEADING_RE.finditer(text))
        sections: list[dict[str, Any]] = []
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            sections.append(
                {
                    "level": len(match.group(1)),
                    "title": match.group(2).strip(),
                    "content": content,
                }
            )
        return sections

    @staticmethod
    def _code_blocks(text: str) -> list[dict[str, str]]:
        return [
            {"language": match.group(1) or "text", "content": match.group(2).strip()}
            for match in FENCE_RE.finditer(text)
        ]

    def _diagrams(self, text: str) -> list[dict[str, str]]:
        headings = list(HEADING_RE.finditer(text))
        diagrams: list[dict[str, str]] = []
        for match in PLANTUML_RE.finditer(text):
            preceding = [heading for heading in headings if heading.start() < match.start()]
            view = "Unclassified"
            title = "Untitled Diagram"
            if preceding:
                title = preceding[-1].group(2).strip()
                view_heading = next(
                    (heading for heading in reversed(preceding) if heading.group(2).endswith("View")),
                    None,
                )
                if view_heading:
                    view = view_heading.group(2).strip()
            diagrams.append(
                {
                    "name": match.group(1) or title.replace(" ", ""),
                    "title": title,
                    "view": view,
                    "syntax": match.group(2).strip(),
                }
            )
        return diagrams
