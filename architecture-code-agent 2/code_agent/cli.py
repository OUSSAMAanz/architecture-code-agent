"""Command-line entry point for parsing specifications and generating projects."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Sequence

from .agent import CodeAgent
from .parser import ArchitectureParser
from .providers import create_provider


DEFAULT_MODEL = "gpt-5.3-codex"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="architecture-code-agent",
        description="Generate a small repository from Markdown architecture specifications.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_command = subparsers.add_parser("parse", help="Convert the inputs to structured JSON")
    _add_input_arguments(parse_command)
    parse_command.add_argument("--json-out", type=Path, required=True)

    generate = subparsers.add_parser("generate", help="Run the model/tool coding-agent loop")
    _add_input_arguments(generate)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--provider", choices=("scripted", "openai"), default="scripted")
    generate.add_argument("--model", default=DEFAULT_MODEL)
    generate.add_argument("--max-iterations", type=int, default=12)
    generate.add_argument(
        "--clean",
        action="store_true",
        help="Delete the selected output directory before generation (never implied).",
    )
    return parser


def _add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--architecture", type=Path, required=True)
    parser.add_argument("--views", type=Path, required=True)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    architecture = args.architecture.resolve()
    views = args.views.resolve()
    for path in (architecture, views):
        if not path.is_file():
            raise SystemExit(f"Input file does not exist: {path}")

    structured = ArchitectureParser().parse_files(architecture, views)
    if args.command == "parse":
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(ArchitectureParser.to_json(structured), encoding="utf-8")
        print(f"Wrote structured specification to {args.json_out}")
        return 0

    output = args.output.resolve()
    if args.clean and output.exists():
        protected = (Path.cwd().resolve(), architecture, views)
        if output == Path(output.anchor) or any(_contains(output, path) for path in protected):
            raise SystemExit(
                "Refusing to clean a workspace, input-containing, or filesystem-root directory"
            )
        shutil.rmtree(output)
    if output.exists() and any(output.iterdir()):
        raise SystemExit("Output directory is not empty; select another path or pass --clean")

    provider = create_provider(args.provider, args.model)
    result = CodeAgent(provider, output, max_iterations=args.max_iterations).run(structured)
    print(json.dumps(
        {
            "completed": result.completed,
            "iterations": result.iterations,
            "summary": result.summary,
            "validation_errors": list(result.validation_errors),
            "output": str(output),
        },
        indent=2,
    ))
    return 0 if result.completed else 1


def _contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
