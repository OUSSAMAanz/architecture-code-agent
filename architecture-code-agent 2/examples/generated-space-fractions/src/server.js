'use strict';

const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { GameService } = require('./game-service');

const games = new GameService();
const publicDirectory = path.join(__dirname, '..', 'public');
const staticFiles = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
]);

function securityHeaders(contentType) {
  return {
    'content-type': contentType,
    'content-security-policy': "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'",
    'x-content-type-options': 'nosniff',
    'referrer-policy': 'no-referrer',
  };
}

function sendJson(response, status, body) {
  response.writeHead(status, securityHeaders('application/json; charset=utf-8'));
  response.end(JSON.stringify(body));
}

function createServer() {
  return http.createServer((request, response) => {
    const url = new URL(request.url, 'http://localhost');

    if (request.method === 'GET' && staticFiles.has(url.pathname)) {
      const [filename, contentType] = staticFiles.get(url.pathname);
      try {
        const content = fs.readFileSync(path.join(publicDirectory, filename));
        response.writeHead(200, securityHeaders(contentType));
        response.end(content);
      } catch {
        sendJson(response, 500, { error: 'interface unavailable' });
      }
      return;
    }

    if (request.method === 'GET' && url.pathname === '/health') {
      return sendJson(response, 200, { status: 'ok' });
    }
    if (request.method === 'POST' && url.pathname === '/games') {
      return sendJson(response, 201, games.start());
    }
    const gameMatch = url.pathname.match(/^\/games\/([^/]+)$/);
    if (request.method === 'GET' && gameMatch) {
      const game = games.get(gameMatch[1]);
      return sendJson(response, game ? 200 : 404, game || { error: 'not found' });
    }
    const answerMatch = url.pathname.match(/^\/games\/([^/]+)\/answers$/);
    if (request.method === 'POST' && answerMatch) {
      let raw = '';
      request.on('data', chunk => {
        raw += chunk;
        if (raw.length > 10_000) request.destroy();
      });
      request.on('end', () => {
        try {
          const payload = JSON.parse(raw || '{}');
          if (!Number.isInteger(payload.selectedIndex)) {
            return sendJson(response, 400, { error: 'selectedIndex must be an integer' });
          }
          const game = games.answer(answerMatch[1], payload.selectedIndex);
          sendJson(response, game ? 200 : 404, game || { error: 'not found' });
        } catch {
          sendJson(response, 400, { error: 'invalid JSON' });
        }
      });
      return;
    }
    sendJson(response, 404, { error: 'not found' });
  });
}

if (require.main === module) {
  const port = process.env.PORT || 3000;
  createServer().listen(port, () => {
    console.log(`Space Fractions is ready at http://localhost:${port}`);
  });
}

module.exports = { createServer };
