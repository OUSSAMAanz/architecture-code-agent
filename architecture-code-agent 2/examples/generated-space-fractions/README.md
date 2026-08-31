# Space Fractions

Generated example for the Architecture Code Agent assignment. Space Fractions is
a responsive browser game for sixth-grade learners backed by a small Node.js API.
It keeps game sessions in memory and uses only Node.js built-ins.

## Run

```bash
npm test
npm start
```

Open `http://localhost:3000/` to play the visual game. The interface presents six
fraction challenges, immediate explanations, progress, scoring, and an ending
scene with personalized feedback.

## API

- `GET /health` returns service status.
- `POST /games` starts a game.
- `GET /games/:id` returns the game state.
- `POST /games/:id/answers` submits `{"selectedIndex": 0}` and checks the answer
  on the server.

The included OpenAPI, SQL, Kubernetes, and traceability artifacts preserve the
architecture contracts while the educational runtime stays intentionally small.
