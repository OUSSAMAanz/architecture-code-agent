# Space Fractions

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
- `POST /games/:id/answers` submits `{"correct": true|false}`.

The included OpenAPI, SQL, Kubernetes, and traceability artifacts preserve the
architecture contracts while the educational runtime stays intentionally small.
