'use strict';

const { randomUUID } = require('node:crypto');

const QUESTIONS = Object.freeze([
  {
    id: 'orbit-1',
    prompt: 'A satellite completes 1/2 of an orbit, then another 1/4. How much of the orbit is complete?',
    expression: '1/2 + 1/4',
    options: ['1/4', '2/6', '3/4', '1 whole'],
    correctIndex: 2,
    explanation: 'Convert 1/2 to 2/4. Then 2/4 + 1/4 = 3/4.',
  },
  {
    id: 'fuel-2',
    prompt: 'The fuel tank was 7/8 full. The crew used 3/8. What fraction remains?',
    expression: '7/8 − 3/8',
    options: ['3/8', '1/2', '5/8', '4/16'],
    correctIndex: 1,
    explanation: 'The denominators match: 7/8 − 3/8 = 4/8, which simplifies to 1/2.',
  },
  {
    id: 'samples-3',
    prompt: 'Three of every five moon rocks contain crystals. Which fraction is equivalent to 3/5?',
    expression: '3/5 = ?',
    options: ['6/10', '4/10', '9/20', '12/25'],
    correctIndex: 0,
    explanation: 'Multiply the numerator and denominator by 2: 3/5 = 6/10.',
  },
  {
    id: 'crew-4',
    prompt: 'Four astronauts share 3 nutrition bars equally. How much does each astronaut receive?',
    expression: '3 ÷ 4',
    options: ['1/4', '3/4', '4/3', '1 whole'],
    correctIndex: 1,
    explanation: 'Dividing 3 items among 4 people gives each person 3/4 of a bar.',
  },
  {
    id: 'signal-5',
    prompt: 'A signal travels 2/3 of a light-minute, then 1/6 more. What total distance does it travel?',
    expression: '2/3 + 1/6',
    options: ['3/9', '3/6', '5/6', '1 whole'],
    correctIndex: 2,
    explanation: 'Convert 2/3 to 4/6. Then 4/6 + 1/6 = 5/6.',
  },
  {
    id: 'mission-6',
    prompt: 'A mission is 5/6 complete. What fraction is still unfinished?',
    expression: '1 − 5/6',
    options: ['1/6', '1/5', '5/6', '6/5'],
    correctIndex: 0,
    explanation: 'One whole is 6/6. Therefore, 6/6 − 5/6 = 1/6.',
  },
]);

function publicQuestion(question) {
  return {
    id: question.id,
    prompt: question.prompt,
    expression: question.expression,
    options: [...question.options],
  };
}

class GameService {
  constructor() {
    this.games = new Map();
  }

  start() {
    const game = {
      id: randomUUID(),
      score: 0,
      answered: 0,
      questionIndex: 0,
      status: 'playing',
    };
    this.games.set(game.id, game);
    return this._publicGame(game);
  }

  get(id) {
    const game = this.games.get(id);
    return game ? this._publicGame(game) : null;
  }

  answer(id, selectedIndex) {
    const game = this.games.get(id);
    if (!game) return null;

    if (game.status === 'completed') {
      return { ...this._publicGame(game), feedback: null };
    }

    const question = QUESTIONS[game.questionIndex];
    const correct = selectedIndex === question.correctIndex;
    game.answered += 1;
    if (correct) game.score += 1;
    game.questionIndex += 1;
    if (game.questionIndex >= QUESTIONS.length) game.status = 'completed';

    return {
      ...this._publicGame(game),
      feedback: {
        correct,
        correctAnswer: question.options[question.correctIndex],
        explanation: question.explanation,
      },
    };
  }

  _publicGame(game) {
    const question = game.status === 'playing' ? QUESTIONS[game.questionIndex] : null;
    return {
      id: game.id,
      score: game.score,
      answered: game.answered,
      totalQuestions: QUESTIONS.length,
      status: game.status,
      currentQuestion: question ? publicQuestion(question) : null,
    };
  }
}

module.exports = { GameService, QUESTIONS };
