# Suggested 4-Minute Demonstration

## 0:00–0:25 — Introduce the goal

“This project studies Claude Code's agent mechanisms and implements an independent
Code Agent with OpenAI Codex support. It accepts architecture documentation and
PlantUML views, converts them to structured JSON, and uses a model/tool loop to
generate and test a complete project.”

Show `inputs/Architecture_Documentation.md` and `inputs/Architecture_View.md`.

## 0:25–0:55 — Show the implementation

Open these files:

1. `code_agent/parser.py` — deterministic architecture extraction.
2. `code_agent/agent.py` — the model/tool/result loop.
3. `code_agent/tools.py` — safe tools and workspace boundary.
4. `code_agent/providers.py` — offline demonstration and live OpenAI adapters.

Mention that there is no unrestricted shell tool and path traversal is tested.

## 0:55–1:20 — Run the agent tests

```bash
python3 -m unittest discover -s tests -v
```

Point out the parser, safety, CLI, provider, and end-to-end agent tests.

## 1:20–2:05 — Generate the project

Use a new output directory:

```bash
python3 -m code_agent generate \
  --architecture inputs/Architecture_Documentation.md \
  --views inputs/Architecture_View.md \
  --output video-demo-ui \
  --provider scripted
```

Explain that scripted mode is deterministic and requires no API key. Live Codex
mode uses the same loop through the OpenAI Responses API provider. Show that the
result says `completed: true` and has no validation errors.

## 2:05–2:35 — Inspect and test the result

Show:

- `video-demo-ui/public/` — generated browser interface.
- `video-demo-ui/src/` — game service and HTTP server.
- `video-demo-ui/tests/` — game logic and UI/API integration tests.
- `video-demo-ui/openapi.yaml` — API contract.
- `video-demo-ui/.agent/transcript.jsonl` — auditable tool transcript.

Then run:

```bash
cd video-demo-ui
npm test
```

## 2:35–3:40 — Play the generated game UI

Run:

```bash
npm start
```

Open `http://localhost:3000/`—not only `/health`. Show the main menu, click
**Launch mission**, answer at least two fraction questions, display the immediate
feedback and score, and briefly show the ending screen if time permits.

Explain that the browser submits a selected answer to the generated API and that
the server checks correctness before returning feedback and the next question.

## 3:40–4:00 — Close

“The result demonstrates structured input, controlled autonomous file generation,
a playable responsive user interface, server-side game logic, automated tests,
final validation, and an auditable transcript.”

Stop the server with `Control+C`. Never display a real API key or `.env` file.
