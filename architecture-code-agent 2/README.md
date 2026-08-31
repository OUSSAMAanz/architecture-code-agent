# Architecture Code Agent

A small educational coding agent that studies Claude Code's published mechanisms
but implements an independent agent using OpenAI Codex. The model chooses
constrained tools, receives their results, and continues until it has produced and
verified a repository. Claude Code is not installed or used at runtime.

The assignment inputs are parsed into structured JSON before generation. The
repository supports two providers:

- `scripted`: deterministic, offline, free, and ideal for tests or a classroom demo.
- `openai`: a live OpenAI Codex model that can generalize to other architecture inputs.

## What it demonstrates

1. Deterministic Markdown and PlantUML parsing.
2. An explicit model/tool/result loop with an isolated OpenAI provider adapter.
3. JSON Schema tool definitions.
4. Workspace-scoped file operations and path-traversal prevention.
5. Controlled test execution rather than unrestricted shell access.
6. Iteration limits, transcripts, and deterministic final validation.
7. A complete generated Space Fractions game with a responsive browser UI.

## Architecture

```text
Architecture_Documentation.md ─┐
                               ├─> ArchitectureParser ─> architecture.json
Architecture_View.md ──────────┘                              │
                                                              v
User goal ─> CodeAgent ─> ModelProvider ─> tool calls ─> SafeWorkspace
                ^                                  │              │
                └──────────── tool results ────────┘              v
                                                        generated repository
                                                              │
                                                     tests + validation
```

The central loop is intentionally small and readable in `code_agent/agent.py`.
Provider-specific API code stays in `code_agent/providers.py`, while all model
actions pass through the boundary in `code_agent/tools.py`.

## Requirements

- Python 3.10 or newer.
- Node.js 18 or newer only for running the generated Space Fractions example.
- An OpenAI API key and API access only when using the optional live provider.

The offline parser, tests, and scripted demonstration use the Python standard
library and do not require network access.

## Quick start: offline demonstration

```bash
python -m unittest discover -s tests -v

python -m code_agent parse \
  --architecture inputs/Architecture_Documentation.md \
  --views inputs/Architecture_View.md \
  --json-out architecture.json

python -m code_agent generate \
  --architecture inputs/Architecture_Documentation.md \
  --views inputs/Architecture_View.md \
  --output generated-project \
  --provider scripted

cd generated-project
npm test
npm start
```

The committed `examples/generated-space-fractions/` directory is the result of
that same generation command. After `npm start`, open `http://localhost:3000/`
to play six fraction challenges, receive answer explanations, track progress and
score, and view the final mission feedback screen.

## Live OpenAI Codex mode

Install the official SDK and export the key in your shell:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"

python -m code_agent generate \
  --architecture inputs/Architecture_Documentation.md \
  --views inputs/Architecture_View.md \
  --output generated-project \
  --provider openai \
  --model gpt-5.3-codex
```

Model names change over time, so `--model` is configurable. The application
never reads a key from source code and never writes the key to the generated
repository.

## CLI reference

### Parse

```bash
python -m code_agent parse \
  --architecture PATH \
  --views PATH \
  --json-out PATH
```

The JSON contains headings, code blocks, requirement IDs, component names, and
each PlantUML diagram with its view and syntax.

### Generate

```bash
python -m code_agent generate \
  --architecture PATH \
  --views PATH \
  --output DIRECTORY \
  [--provider scripted|openai] \
  [--model MODEL] \
  [--max-iterations 12]
```

Generation refuses to write into a non-empty directory. `--clean` is available
for deliberate reruns and explicitly deletes only the selected output directory;
it refuses filesystem roots, the current workspace, and directories containing
either input file.

## Agent tools

| Tool | Purpose | Safety property |
| --- | --- | --- |
| `list_files` | Inspect the output tree | Workspace-relative paths only |
| `read_file` | Read generated text files | Size limit and workspace boundary |
| `write_file` | Create project files | Blocks traversal, `.env`, `.git`, and secrets paths |
| `run_tests` | Verify the repository | Chooses a fixed Python or Node test command |
| `finish` | Request completion | Deterministic validation still runs afterward |

The model receives no general-purpose shell tool. This is a deliberate scope and
safety decision for a one-week educational project.

## Output and audit trail

Every generated repository includes an internal `.agent/` directory:

- `architecture.json`: structured input given to the model.
- `transcript.jsonl`: model steps and tool results.
- `result.json`: completion status and validation errors.

Final validation checks for a README, dependency manifest, source directory,
tests, and empty files. A model saying “finished” is therefore not automatically
treated as success.

## Tests

The test suite covers:

- architecture and PlantUML parsing;
- JSON serialization;
- safe file reading and writing;
- absolute-path and traversal attacks;
- sensitive-path blocking;
- unknown tool rejection;
- a complete four-iteration offline agent run;
- early model termination;
- CLI parsing.

Run all tests with:

```bash
python -m unittest discover -s tests -v
```

## Repository map

```text
code_agent/                 Agent implementation
inputs/                     Teacher-provided architecture fixtures
tests/                      Unit and end-to-end tests
docs/                       Research notes and video demo script
examples/generated-space-fractions/
                            Verified output produced by the agent
Dockerfile                  Optional container for the agent CLI
requirements.txt            Optional live-provider dependency
```

## Scope and limitations

- The Markdown parser recognizes the structure used in the supplied assignment;
  it is not a complete CommonMark parser.
- The scripted provider is a deterministic demonstration fixture, not an AI model.
- Live output quality depends on the selected model and specification quality.
- Tests run in a subprocess with a timeout, but production deployment should add
  operating-system sandboxing or container isolation.
- The generated Space Fractions game is an educational vertical slice with a
  complete playable UI and API, not the full cloud microservices platform
  suggested by the architecture document.

## Research basis

The design is based on the model/tool/result loop, context construction, unified
tool interface, permissions, and validation patterns described in the assignment's
references. See [docs/IMPLEMENTATION_MECHANISMS.md](docs/IMPLEMENTATION_MECHANISMS.md)
for the mapping between research and this implementation.

## License

MIT. See [LICENSE](LICENSE).
