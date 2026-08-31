'use strict';

const elements = {
  welcome: document.querySelector('#welcome-screen'),
  game: document.querySelector('#game-screen'),
  result: document.querySelector('#result-screen'),
  start: document.querySelector('#start-button'),
  help: document.querySelector('#help-button'),
  helpPanel: document.querySelector('#help-panel'),
  questionCount: document.querySelector('#question-count'),
  questionId: document.querySelector('#question-id'),
  questionHeading: document.querySelector('#question-heading'),
  expression: document.querySelector('#expression'),
  answers: document.querySelector('#answers'),
  score: document.querySelector('#score-value'),
  scoreTotal: document.querySelector('#score-total'),
  progress: document.querySelector('#progress-bar'),
  streak: document.querySelector('#streak-value'),
  feedback: document.querySelector('#feedback-panel'),
  feedbackTitle: document.querySelector('#feedback-title'),
  feedbackMessage: document.querySelector('#feedback-message'),
  next: document.querySelector('#next-button'),
  resultMessage: document.querySelector('#result-message'),
  resultPercent: document.querySelector('#result-percent'),
  finalScore: document.querySelector('#final-score'),
  finalXp: document.querySelector('#final-xp'),
  finalRank: document.querySelector('#final-rank'),
  replay: document.querySelector('#replay-button'),
  error: document.querySelector('#error-panel'),
  errorMessage: document.querySelector('#error-message'),
  retry: document.querySelector('#retry-button'),
};

const letters = ['A', 'B', 'C', 'D'];
let currentGame = null;
let pendingGame = null;
let streak = 0;

function showScreen(name) {
  elements.welcome.hidden = name !== 'welcome';
  elements.game.hidden = name !== 'game';
  elements.result.hidden = name !== 'result';
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || 'Mission request failed');
  return payload;
}

function showError(message) {
  elements.errorMessage.textContent = message;
  elements.error.hidden = false;
}

function hideError() {
  elements.error.hidden = true;
}

function setBusy(button, busy, label) {
  button.disabled = busy;
  if (label) button.querySelector('span').textContent = label;
}

async function startGame() {
  hideError();
  setBusy(elements.start, true, 'Preparing launch…');
  try {
    currentGame = await request('/games', { method: 'POST', body: '{}' });
    pendingGame = null;
    streak = 0;
    showScreen('game');
    renderQuestion();
  } catch (error) {
    showError(error.message);
  } finally {
    setBusy(elements.start, false, 'Launch mission');
  }
}

function renderQuestion() {
  const question = currentGame.currentQuestion;
  const number = currentGame.answered + 1;
  const progress = (currentGame.answered / currentGame.totalQuestions) * 100;

  elements.questionCount.textContent = `Question ${number} of ${currentGame.totalQuestions}`;
  elements.questionId.textContent = question.id.toUpperCase();
  elements.questionHeading.textContent = question.prompt;
  elements.expression.textContent = question.expression;
  elements.score.textContent = currentGame.score;
  elements.scoreTotal.textContent = currentGame.totalQuestions;
  elements.progress.style.width = `${progress}%`;
  elements.streak.textContent = streak;
  elements.feedback.hidden = true;
  elements.feedback.classList.remove('incorrect');
  elements.answers.replaceChildren();

  question.options.forEach((option, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'answer-button';
    button.dataset.index = String(index);
    button.innerHTML = `<span class="answer-letter">${letters[index]}</span><span class="answer-text"></span>`;
    button.querySelector('.answer-text').textContent = option;
    button.addEventListener('click', () => submitAnswer(index, button));
    elements.answers.append(button);
  });

  elements.questionHeading.focus({ preventScroll: true });
}

async function submitAnswer(selectedIndex, selectedButton) {
  hideError();
  const buttons = [...elements.answers.querySelectorAll('button')];
  buttons.forEach(button => { button.disabled = true; });
  selectedButton.classList.add('selected');

  try {
    pendingGame = await request(`/games/${encodeURIComponent(currentGame.id)}/answers`, {
      method: 'POST',
      body: JSON.stringify({ selectedIndex }),
    });

    const { feedback } = pendingGame;
    streak = feedback.correct ? streak + 1 : 0;
    elements.score.textContent = pendingGame.score;
    elements.streak.textContent = streak;
    elements.progress.style.width = `${(pendingGame.answered / pendingGame.totalQuestions) * 100}%`;
    elements.feedback.classList.toggle('incorrect', !feedback.correct);
    elements.feedbackTitle.textContent = feedback.correct ? 'Correct trajectory!' : 'Course correction needed';
    elements.feedbackMessage.textContent = feedback.correct
      ? feedback.explanation
      : `The correct answer is ${feedback.correctAnswer}. ${feedback.explanation}`;
    elements.next.firstChild.textContent = pendingGame.status === 'completed' ? 'View mission results ' : 'Next challenge ';
    elements.feedback.hidden = false;
    elements.next.focus({ preventScroll: true });
  } catch (error) {
    buttons.forEach(button => { button.disabled = false; });
    selectedButton.classList.remove('selected');
    showError(error.message);
  }
}

function continueMission() {
  if (!pendingGame) return;
  currentGame = pendingGame;
  pendingGame = null;
  if (currentGame.status === 'completed') {
    renderResult();
  } else {
    renderQuestion();
  }
}

function renderResult() {
  const percent = Math.round((currentGame.score / currentGame.totalQuestions) * 100);
  const xp = Math.round(40 + percent * 0.6);
  let message = 'Keep training—the next mission is yours.';
  let rank = 'Orbit apprentice';

  if (percent === 100) {
    message = 'Perfect navigation. Every fraction system is online.';
    rank = 'Star navigator';
  } else if (percent >= 67) {
    message = 'Strong mission. Your fraction skills are ready for deeper space.';
    rank = 'Lunar specialist';
  } else if (percent >= 50) {
    message = 'Mission complete. Review the explanations and launch again.';
    rank = 'Flight cadet';
  }

  elements.resultPercent.textContent = `${percent}%`;
  elements.resultMessage.textContent = message;
  elements.finalScore.textContent = `${currentGame.score} / ${currentGame.totalQuestions}`;
  elements.finalXp.textContent = `${xp} XP`;
  elements.finalRank.textContent = rank;
  showScreen('result');
  elements.replay.focus({ preventScroll: true });
}

elements.start.addEventListener('click', startGame);
elements.replay.addEventListener('click', startGame);
elements.retry.addEventListener('click', startGame);
elements.next.addEventListener('click', continueMission);
elements.help.addEventListener('click', () => {
  const willOpen = elements.helpPanel.hidden;
  elements.helpPanel.hidden = !willOpen;
  elements.help.setAttribute('aria-expanded', String(willOpen));
});
