'use strict';

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
