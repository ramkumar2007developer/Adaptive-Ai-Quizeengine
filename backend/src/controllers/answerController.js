import { getSession, saveSession } from './quizController.js';
import { calculateNextDifficulty, calculateScore } from '../services/difficultyService.js';
import { generateQuestion } from '../services/llmService.js';

export const submitAnswer = async (req, res) => {
  try {
    const { sessionId, selectedIndex, timeTakenSeconds = 10, currentQuestionData } = req.body;

    const session = getSession(sessionId);
    if (!session) {
      return res.status(404).json({ success: false, message: 'Quiz session expired or not found' });
    }

    const isCorrect = selectedIndex === currentQuestionData.correctAnswerIndex;
    const pointsAwarded = calculateScore(session.currentDifficulty, timeTakenSeconds, isCorrect);

    session.totalScore += pointsAwarded;
    if (isCorrect) {
      session.streak += 1;
    } else {
      session.streak = 0;
    }

    session.history.push({
      questionNumber: session.currentQuestionIndex,
      difficulty: session.currentDifficulty,
      question: currentQuestionData.question,
      isCorrect,
      selectedIndex,
      correctIndex: currentQuestionData.correctAnswerIndex,
      pointsAwarded,
      explanation: currentQuestionData.explanation
    });

    // Check adaptive difficulty adjustment
    const adaptiveResult = calculateNextDifficulty(session.currentDifficulty, session.history);
    const prevDifficulty = session.currentDifficulty;
    session.currentDifficulty = adaptiveResult.nextDifficulty;

    const TOTAL_QUIZ_QUESTIONS = 10;
    const isCompleted = session.currentQuestionIndex >= TOTAL_QUIZ_QUESTIONS;

    let nextQuestion = null;
    if (!isCompleted) {
      session.currentQuestionIndex += 1;
      nextQuestion = await generateQuestion(session.topic, session.currentDifficulty, session.currentQuestionIndex);
    }

    saveSession(sessionId, session);

    return res.status(200).json({
      success: true,
      evaluation: {
        isCorrect,
        correctAnswerIndex: currentQuestionData.correctAnswerIndex,
        explanation: currentQuestionData.explanation,
        pointsAwarded,
        totalScore: session.totalScore,
        streak: session.streak
      },
      difficultyShift: {
        previousDifficulty: prevDifficulty,
        newDifficulty: session.currentDifficulty,
        changed: adaptiveResult.changed,
        direction: adaptiveResult.direction || 'SAME',
        reason: adaptiveResult.reason
      },
      isCompleted,
      nextQuestion: nextQuestion ? {
        id: nextQuestion.id,
        difficulty: nextQuestion.difficulty,
        question: nextQuestion.question,
        options: nextQuestion.options
      } : null,
      summary: isCompleted ? {
        totalScore: session.totalScore,
        totalQuestions: TOTAL_QUIZ_QUESTIONS,
        correctCount: session.history.filter(h => h.isCorrect).length,
        accuracyPercentage: Math.round((session.history.filter(h => h.isCorrect).length / TOTAL_QUIZ_QUESTIONS) * 100),
        history: session.history
      } : null
    });
  } catch (err) {
    console.error('Error processing answer submission:', err);
    return res.status(500).json({ success: false, message: 'Failed to process answer submission' });
  }
};
