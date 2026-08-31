"""Model providers: live OpenAI Codex plus a deterministic offline demonstration."""

from __future__ import annotations

import itertools
import json
import os
from pathlib import Path
from typing import Any, Protocol

from .models import ModelResponse, ToolCall


class Provider(Protocol):
    def respond(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse: ...


class OpenAIProvider:
    """Thin adapter around OpenAI's Responses API and function calling."""

    def __init__(self, model: str, max_tokens: int = 8192) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the optional dependency with: pip install openai") from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for --provider openai")
        self.client = OpenAI()
        self.model = model
        self.max_tokens = max_tokens

    def respond(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        function_tools = [
            {
                "type": "function",
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            }
            for tool in tools
        ]
        response = self.client.responses.create(
            model=self.model,
            max_output_tokens=self.max_tokens,
            instructions=system,
            input=messages,
            tools=function_tools,
            include=["reasoning.encrypted_content"],
            parallel_tool_calls=True,
            store=False,
        )
        calls: list[ToolCall] = []
        raw_content: list[dict[str, Any]] = []
        for item in response.output:
            if item.type == "function_call":
                call = ToolCall(
                    id=item.call_id,
                    name=item.name,
                    arguments=json.loads(item.arguments),
                )
                calls.append(call)
            raw_content.append(item.model_dump(exclude_none=True))
        return ModelResponse(
            text=response.output_text,
            tool_calls=tuple(calls),
            raw_content=raw_content,
        )


class ScriptedDemoProvider:
    """Offline provider that demonstrates the same tool loop deterministically.

    It intentionally generates a small Space Fractions service because that is the
    supplied assignment fixture. It is useful for tests, marking, and video demos;
    live architecture generalization is provided by ``OpenAIProvider``.
    """

    def __init__(self) -> None:
        self.step = 0
        self._ids = itertools.count(1)

    def _call(self, name: str, **arguments: Any) -> ToolCall:
        return ToolCall(f"demo-{next(self._ids)}", name, arguments)

    def respond(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        del system, messages, tools
        batches = self._batches()
        index = min(self.step, len(batches) - 1)
        text, calls = batches[index]
        self.step += 1
        raw = [
            {
                "type": "function_call",
                "call_id": call.id,
                "name": call.name,
                "arguments": json.dumps(call.arguments),
            }
            for call in calls
        ]
        if text:
            raw.insert(
                0,
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": text}],
                },
            )
        return ModelResponse(text=text, tool_calls=tuple(calls), raw_content=raw)

    def _repository_template_batches(self) -> list[tuple[str, list[ToolCall]]] | None:
        """Load the verified example as the offline provider's canonical template.

        Keeping the classroom fixture and the committed example aligned prevents
        the demonstration from silently drifting away from what reviewers see in
        the repository. The embedded service below remains a small fallback for
        source distributions that omit the example directory.
        """

        root = Path(__file__).resolve().parent.parent / "examples" / "generated-space-fractions"
        implementation_files = [
            "package.json",
            "README.md",
            "src/game-service.js",
            "src/server.js",
            "public/index.html",
            "public/styles.css",
            "public/app.js",
            "tests/game-service.test.js",
            "tests/server.test.js",
        ]
        architecture_files = [
            "openapi.yaml",
            "internal.proto",
            "sql/game_ddl.sql",
            "k8s/deployment.yaml",
            "Dockerfile",
            "traceability_matrix.csv",
        ]
        all_files = implementation_files + architecture_files
        if not all((root / relative).is_file() for relative in all_files):
            return None

        def write_calls(paths: list[str]) -> list[ToolCall]:
            return [
                self._call(
                    "write_file",
                    path=relative,
                    content=(root / relative).read_text(encoding="utf-8"),
                )
                for relative in paths
            ]

        return [
            (
                "I will generate a playable Space Fractions web game with a responsive user interface and server-owned answer checking.",
                write_calls(implementation_files),
            ),
            (
                "Now I will add the architecture, API, data, and deployment artifacts.",
                write_calls(architecture_files),
            ),
            ("The playable implementation is ready for verification.", [self._call("run_tests")]),
            (
                "The UI and API tests have passed, so I will finish.",
                [
                    self._call(
                        "finish",
                        summary="Generated a playable Space Fractions web game, responsive UI, API, tests, and architecture artifacts.",
                    )
                ],
            ),
        ]

    def _batches(self) -> list[tuple[str, list[ToolCall]]]:
        repository_batches = self._repository_template_batches()
        if repository_batches is not None:
            return repository_batches

        package_json = """{
  "name": "space-fractions",
  "version": "1.0.0",
  "private": true,
  "description": "Small service generated from the Space Fractions architecture",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "test": "node --test"
  },
  "engines": {"node": ">=18"}
}
"""
        readme = """# Space Fractions

Generated example for the Architecture Code Agent assignment. The service keeps
game sessions in memory and exposes a small HTTP API using only Node.js built-ins.

## Run

```bash
npm test
npm start
curl -X POST http://localhost:3000/games
```

## API

- `GET /health` returns service status.
- `POST /games` starts a game.
- `GET /games/:id` returns the game state.
- `POST /games/:id/answers` submits `{\"correct\": true|false}`.

The included OpenAPI, SQL, Kubernetes, and traceability artifacts preserve the
architecture contracts while the educational runtime stays intentionally small.
"""
        game_service = """'use strict';

const { randomUUID } = require('node:crypto');

class GameService {
  constructor() {
    this.games = new Map();
  }

  start() {
    const game = { id: randomUUID(), score: 0, answered: 0, status: 'playing' };
    this.games.set(game.id, game);
    return { ...game };
  }

  get(id) {
    const game = this.games.get(id);
    return game ? { ...game } : null;
  }

  answer(id, correct) {
    const game = this.games.get(id);
    if (!game) return null;
    game.answered += 1;
    if (correct) game.score += 1;
    return { ...game };
  }
}

module.exports = { GameService };
"""
        server = """'use strict';

const http = require('node:http');
const { GameService } = require('./game-service');

const games = new GameService();

function send(response, status, body) {
  response.writeHead(status, { 'content-type': 'application/json' });
  response.end(JSON.stringify(body));
}

function createServer() {
  return http.createServer((request, response) => {
    const url = new URL(request.url, 'http://localhost');
    if (request.method === 'GET' && url.pathname === '/health') {
      return send(response, 200, { status: 'ok' });
    }
    if (request.method === 'POST' && url.pathname === '/games') {
      return send(response, 201, games.start());
    }
    const gameMatch = url.pathname.match(/^\/games\/([^/]+)$/);
    if (request.method === 'GET' && gameMatch) {
      const game = games.get(gameMatch[1]);
      return send(response, game ? 200 : 404, game || { error: 'not found' });
    }
    const answerMatch = url.pathname.match(/^\/games\/([^/]+)\/answers$/);
    if (request.method === 'POST' && answerMatch) {
      let raw = '';
      request.on('data', chunk => { raw += chunk; });
      request.on('end', () => {
        try {
          const payload = JSON.parse(raw || '{}');
          const game = games.answer(answerMatch[1], payload.correct === true);
          send(response, game ? 200 : 404, game || { error: 'not found' });
        } catch {
          send(response, 400, { error: 'invalid JSON' });
        }
      });
      return;
    }
    send(response, 404, { error: 'not found' });
  });
}

if (require.main === module) {
  createServer().listen(process.env.PORT || 3000);
}

module.exports = { createServer };
"""
        test_file = """'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { GameService } = require('../src/game-service');

test('starts a game with zero score', () => {
  const service = new GameService();
  const game = service.start();
  assert.equal(game.score, 0);
  assert.equal(game.status, 'playing');
});

test('records correct and incorrect answers', () => {
  const service = new GameService();
  const game = service.start();
  service.answer(game.id, true);
  const updated = service.answer(game.id, false);
  assert.equal(updated.score, 1);
  assert.equal(updated.answered, 2);
});

test('returns null for unknown games', () => {
  assert.equal(new GameService().get('missing'), null);
});
"""
        openapi = """openapi: 3.0.3
info:
  title: Space Fractions API
  version: 1.0.0
paths:
  /health:
    get:
      responses:
        '200': {description: Service is healthy}
  /games:
    post:
      summary: Start a game
      responses:
        '201': {description: Game created}
  /games/{id}:
    get:
      parameters:
        - in: path
          name: id
          required: true
          schema: {type: string}
      responses:
        '200': {description: Game state}
        '404': {description: Game not found}
"""
        ddl = """CREATE TABLE games (
    id UUID PRIMARY KEY,
    score INTEGER NOT NULL DEFAULT 0 CHECK (score >= 0),
    answered INTEGER NOT NULL DEFAULT 0 CHECK (answered >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'playing',
    game_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
        deployment = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: space-fractions
spec:
  replicas: 3
  selector:
    matchLabels: {app: space-fractions}
  template:
    metadata:
      labels: {app: space-fractions}
    spec:
      containers:
        - name: app
          image: space-fractions:latest
          ports:
            - containerPort: 3000
          readinessProbe:
            httpGet: {path: /health, port: 3000}
"""
        dockerfile = """FROM node:20-alpine
WORKDIR /app
COPY package.json ./
COPY src ./src
USER node
EXPOSE 3000
CMD ["node", "src/server.js"]
"""
        traceability = """Requirement ID,Short Text,Artifact,Rationale
FR-1,Play game,src/game-service.js,Creates and updates game sessions
NFR-1,Performance,src/game-service.js,Uses constant-time in-memory lookup for the demo
ASR-1,Data durability,sql/game_ddl.sql,Defines a durable PostgreSQL representation
"""
        proto = """syntax = \"proto3\";
package spacefractions;
service GameService {
  rpc Play(PlayRequest) returns (PlayResponse);
}
message PlayRequest {}
message PlayResponse { string game_id = 1; }
"""
        return [
            (
                "I will create a compact Node.js implementation and preserve the supplied contracts.",
                [
                    self._call("write_file", path="package.json", content=package_json),
                    self._call("write_file", path="README.md", content=readme),
                    self._call("write_file", path="src/game-service.js", content=game_service),
                    self._call("write_file", path="src/server.js", content=server),
                    self._call("write_file", path="tests/game-service.test.js", content=test_file),
                ],
            ),
            (
                "Now I will add the architecture and deployment artifacts.",
                [
                    self._call("write_file", path="openapi.yaml", content=openapi),
                    self._call("write_file", path="internal.proto", content=proto),
                    self._call("write_file", path="sql/game_ddl.sql", content=ddl),
                    self._call("write_file", path="k8s/deployment.yaml", content=deployment),
                    self._call("write_file", path="Dockerfile", content=dockerfile),
                    self._call("write_file", path="traceability_matrix.csv", content=traceability),
                ],
            ),
            ("The implementation is ready for verification.", [self._call("run_tests")]),
            (
                "Tests have been executed, so I will finish.",
                [self._call("finish", summary="Generated a runnable Space Fractions service, tests, and architecture artifacts.")],
            ),
        ]


def create_provider(name: str, model: str) -> Provider:
    if name == "scripted":
        return ScriptedDemoProvider()
    if name == "openai":
        return OpenAIProvider(model=model)
    raise ValueError(f"Unsupported provider: {name}")
