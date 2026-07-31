/**
 * Adaptive Difficulty Engine
 * Calculates difficulty adjustments based on streak, accuracy, and response time.
 */

const DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard'];

export function calculateNextDifficulty(currentDifficulty, history = []) {
  if (history.length === 0) return { nextDifficulty: currentDifficulty, changed: false, reason: 'Initial question' };

  const recent = history.slice(-2);
  const consecutiveCorrect = recent.length === 2 && recent.every(item => item.isCorrect);
  const consecutiveIncorrect = recent.length === 2 && recent.every(item => !item.isCorrect);

  let nextIndex = DIFFICULTY_LEVELS.indexOf(currentDifficulty);
  if (nextIndex === -1) nextIndex = 0;

  if (consecutiveCorrect && nextIndex < DIFFICULTY_LEVELS.length - 1) {
    nextIndex += 1;
    return {
      nextDifficulty: DIFFICULTY_LEVELS[nextIndex],
      changed: true,
      direction: 'UP',
      reason: 'Great performance! 2 consecutive correct answers level up your question difficulty.'
    };
  }

  if (consecutiveIncorrect && nextIndex > 0) {
    nextIndex -= 1;
    return {
      nextDifficulty: DIFFICULTY_LEVELS[nextIndex],
      changed: true,
      direction: 'DOWN',
      reason: '2 consecutive incorrect answers reduced difficulty to build fundamental understanding.'
    };
  }

  return {
    nextDifficulty: currentDifficulty,
    changed: false,
    reason: 'Maintaining current difficulty baseline.'
  };
}

export function calculateScore(difficulty, timeTakenSeconds, isCorrect) {
  if (!isCorrect) return 0;

  const basePoints = {
    Easy: 10,
    Medium: 20,
    Hard: 30
  }[difficulty] || 10;

  // Speed bonus: max +5 points for answering under 10 seconds
  const speedBonus = timeTakenSeconds && timeTakenSeconds < 10 ? Math.max(1, 10 - timeTakenSeconds) : 0;
  return basePoints + speedBonus;
}
