'use strict';

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
