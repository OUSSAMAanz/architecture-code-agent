'use strict';

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
