'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { GameService, QUESTIONS } = require('../src/game-service');

test('starts a game with a visible question and zero score', () => {
  const service = new GameService();
  const game = service.start();
  assert.equal(game.score, 0);
  assert.equal(game.status, 'playing');
  assert.equal(game.totalQuestions, QUESTIONS.length);
  assert.equal(game.currentQuestion.id, QUESTIONS[0].id);
  assert.equal('correctIndex' in game.currentQuestion, false);
});

test('checks answers on the server and advances the question', () => {
  const service = new GameService();
  const game = service.start();
  const updated = service.answer(game.id, QUESTIONS[0].correctIndex);
  assert.equal(updated.feedback.correct, true);
  assert.equal(updated.score, 1);
  assert.equal(updated.answered, 1);
  assert.equal(updated.currentQuestion.id, QUESTIONS[1].id);
});

test('completes a game and returns the final score', () => {
  const service = new GameService();
  const game = service.start();
  let updated;
  for (const question of QUESTIONS) {
    updated = service.answer(game.id, question.correctIndex);
  }
  assert.equal(updated.status, 'completed');
  assert.equal(updated.score, QUESTIONS.length);
  assert.equal(updated.currentQuestion, null);
});

test('returns null for unknown games', () => {
  assert.equal(new GameService().get('missing'), null);
});
