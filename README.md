# Architecture Code Agent

An educational Code Agent that turns Markdown architecture specifications into a
runnable software repository. The project studies the model/tool/result loop,
permission boundaries, iteration, and validation mechanisms described in the
Claude Code research material supplied with the assignment, while providing an
independent OpenAI Codex runtime implementation.

Claude Code is not installed or used at runtime.

## Assignment objective

The agent accepts two inputs:

- `Architecture_Documentation.md`, containing system requirements and contracts.
- `Architecture_View.md`, containing PlantUML architectural views.

It parses those documents into structured JSON, lets a model choose constrained
tools, writes a project inside a protected workspace, runs tests, and validates
the final repository before reporting success.

```text
Architecture documents
        |
        v
Structured architecture JSON
        |
        v
Model <-> tool execution loop
        |
        v
Source code + tests + documentation + deployment artifacts
        |
        v
Deterministic validation
```

## What is included

- A readable Python agent loop and command-line interface.
- Markdown and PlantUML parsing.
- Workspace-scoped file tools with traversal and sensitive-path protection.
- A deterministic offline provider for tests and classroom demonstrations.
- An OpenAI Responses API provider for live Codex generation.
- Unit and end-to-end tests.
- A verified generated Space Fractions API example.
- Research notes and a short video-demonstration script.

The project source is located in
[`architecture-code-agent 2/`](architecture-code-agent%202/).

## Requirements

- Python 3.10 or newer.
- Node.js 18 or newer to test the generated example.
- An OpenAI API key only for the optional live provider.

The offline demonstration does not require network access or an API key.

## Quick start

Clone the repository and enter the project directory:

```bash
git clone https://github.com/OUSSAMAanz/architecture-code-agent.git
cd architecture-code-agent/"architecture-code-agent 2"
```

Run the agent tests:

```bash
python3 -m unittest discover -s tests -v
```

Generate a project using the deterministic offline demonstration:

```bash
python3 -m code_agent generate \
  --architecture inputs/Architecture_Documentation.md \
  --views inputs/Architecture_View.md \
  --output generated-project \
  --provider scripted
```

Test and run the generated project:

```bash
cd generated-project
npm test
npm start
```

The service health check is then available at
[`http://localhost:3000/health`](http://localhost:3000/health).

## Live OpenAI Codex mode

Create a virtual environment, install the official OpenAI SDK, and provide your
API key through the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"

python3 -m code_agent generate \
  --architecture inputs/Architecture_Documentation.md \
  --views inputs/Architecture_View.md \
  --output live-generated-project \
  --provider openai \
  --model gpt-5.3-codex
```

Never commit a real API key or `.env` file.

## Agent safety model

The model does not receive an unrestricted shell. It can request only five
constrained tools:

| Tool | Purpose |
| --- | --- |
| `list_files` | Inspect generated files |
| `read_file` | Read workspace text files |
| `write_file` | Create or update workspace files |
| `run_tests` | Execute a fixed Python or Node test command |
| `finish` | Request final deterministic validation |

Paths are resolved inside the selected output workspace, sensitive paths are
blocked, and the loop has a configurable iteration limit.

## Example output

The committed
[`examples/generated-space-fractions/`](architecture-code-agent%202/examples/generated-space-fractions/)
directory demonstrates the expected output. It includes source code, tests, a
dependency manifest, README, Dockerfile, OpenAPI specification, protocol contract,
database definition, Kubernetes configuration, and an agent audit trail.

## Documentation

- [Full project documentation](architecture-code-agent%202/README.md)
- [Implementation mechanisms](architecture-code-agent%202/docs/IMPLEMENTATION_MECHANISMS.md)
- [Video demonstration script](architecture-code-agent%202/docs/DEMO_SCRIPT.md)
- [Submission checklist](architecture-code-agent%202/SUBMISSION_CHECKLIST.md)
- [Security policy](architecture-code-agent%202/SECURITY.md)

## Scope

This is a focused educational implementation, not a production replacement for
Claude Code or Codex. The scripted provider is a deterministic demonstration
fixture rather than an AI model; live generation is available through the OpenAI
provider.

## License

MIT. See [`LICENSE`](architecture-code-agent%202/LICENSE).
