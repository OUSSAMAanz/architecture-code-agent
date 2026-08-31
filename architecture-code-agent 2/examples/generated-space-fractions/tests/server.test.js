'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { createServer } = require('../src/server');

async function withServer(run) {
  const server = createServer();
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const { port } = server.address();
  try {
    await run(`http://127.0.0.1:${port}`);
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
}

test('serves the playable game interface at the root route', async () => {
  await withServer(async baseUrl => {
    const response = await fetch(`${baseUrl}/`);
    const html = await response.text();
    assert.equal(response.status, 200);
    assert.match(response.headers.get('content-type'), /text\/html/);
    assert.match(html, /Launch mission/);
    assert.match(html, /Space Fractions/);
  });
});

test('starts a game and accepts a selected answer through the API', async () => {
  await withServer(async baseUrl => {
    const startResponse = await fetch(`${baseUrl}/games`, { method: 'POST' });
    const game = await startResponse.json();
    assert.equal(startResponse.status, 201);
    assert.equal(game.currentQuestion.options.length, 4);

    const answerResponse = await fetch(`${baseUrl}/games/${game.id}/answers`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ selectedIndex: 2 }),
    });
    const updated = await answerResponse.json();
    assert.equal(answerResponse.status, 200);
    assert.equal(updated.feedback.correct, true);
    assert.equal(updated.answered, 1);
  });
});
