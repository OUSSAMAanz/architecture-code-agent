# Suggested 3-Minute Demonstration

## 0:00–0:25 — Introduce the goal

“This project studies Claude Code's agent mechanisms but implements an independent
Code Agent powered by OpenAI Codex. It accepts architecture documentation and
PlantUML views, converts them to structured JSON, and uses a model/tool loop to
generate and test a project repository.”

Show `inputs/Architecture_Documentation.md` and `inputs/Architecture_View.md`.

## 0:25–0:55 — Show the implementation

Open these three files:

1. `code_agent/parser.py` — deterministic architecture extraction.
2. `code_agent/agent.py` — the model/tool/result loop.
3. `code_agent/tools.py` — safe tools and workspace boundary.

Mention that there is no unrestricted shell tool and that path traversal is tested.

## 0:55–1:25 — Run the tests

```bash
python -m unittest discover -s tests -v
```

Point out the parser, safety, CLI, and end-to-end agent tests.

## 1:25–2:15 — Run the agent

Use a new output directory:

```bash
python -m code_agent generate \
  --architecture inputs/Architecture_Documentation.md \
  --views inputs/Architecture_View.md \
  --output demo-output \
  --provider scripted
```

Explain that scripted mode is deterministic and requires no API key. Live Codex
mode uses the same loop through the OpenAI Responses API provider.

## 2:15–2:45 — Inspect the result

Show:

- `demo-output/src/`
- `demo-output/tests/`
- `demo-output/openapi.yaml`
- `demo-output/sql/game_ddl.sql`
- `demo-output/k8s/deployment.yaml`
- `demo-output/.agent/transcript.jsonl`

Run:

```bash
cd demo-output
npm test
```

## 2:45–3:00 — Close

“The result demonstrates structured input, autonomous file generation, controlled
tools, test execution, final validation, and an auditable transcript. The design
is deliberately small, safe, and appropriate for the assignment scope.”
