import React, { useState, useEffect } from 'react';
import QuestionCard from '../components/QuestionCard';
import ProgressBar from '../components/ProgressBar';
import LoadingSpinner from '../components/LoadingSpinner';
import ResultPopup from '../components/ResultPopup';
import { submitQuizAnswer } from '../services/api';

/**
 * Quiz page — orchestrates the adaptive quiz flow.
 *
 * sessionData shape (from FastAPI /api/quiz/start):
 * {
 *   success: true,
 *   quiz_id: string,
 *   subject: string,
 *   current_difficulty: string,
 *   question_number: number,
 *   total_questions: number,
 *   skill_score: number,
 *   question: {
 *     id: string,
 *     question_number: number,
 *     question_type: string,
 *     difficulty: string,
 *     question_text: string,
 *     options: string[],
 *     topic: string, subtopic: string, bloom_taxonomy: string,
 *     estimated_difficulty_score: number, confidence_score: number
 *   }
 * }
 */
export default function Quiz({ sessionData, onQuizComplete }) {
  const [currentQuestion, setCurrentQuestion] = useState(sessionData.question);
  const [questionNumber, setQuestionNumber] = useState(sessionData.question_number ?? 1);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [difficultyShift, setDifficultyShift] = useState(null);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [skillScore, setSkillScore] = useState(sessionData.skill_score ?? 50);
  const [nextQuestionData, setNextQuestionData] = useState(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [quizSummary, setQuizSummary] = useState(null);
  const [startTime, setStartTime] = useState(Date.now());

  useEffect(() => {
    setStartTime(Date.now());
  }, [currentQuestion]);

  const handleSelectOption = (idx) => {
    if (!isSubmitted) {
      setSelectedIndex(idx);
    }
  };

  const handleSubmitAnswer = async () => {
    if (selectedIndex === null || isSubmitted || submitting) return;

    setSubmitting(true);
    const responseTimeSeconds = Math.max(1, Math.round((Date.now() - startTime) / 1000));
    const selectedAnswer = currentQuestion.options?.[selectedIndex] ?? '';

    try {
      // POST /api/quiz/answer
      const response = await submitQuizAnswer({
        quizId: sessionData.quiz_id,
        questionId: currentQuestion.id,
        selectedIndex,
        selectedAnswer,
        responseTimeSeconds,
      });

      if (response.success) {
        // evaluation fields: is_correct, correct_answer, correct_answer_index,
        //                    explanation, points_awarded, total_score, streak, skill_score
        setEvaluation(response.evaluation);
        setDifficultyShift(response.difficulty_shift);
        setScore(response.evaluation.total_score);
        setStreak(response.evaluation.streak);
        setSkillScore(response.evaluation.skill_score);
        setIsSubmitted(true);
        setIsCompleted(response.is_completed);

        if (response.is_completed) {
          setQuizSummary(response.summary);
        } else {
          setNextQuestionData(response.next_question);
        }
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleProceedNext = () => {
    if (isCompleted && quizSummary) {
      onQuizComplete(quizSummary);
      return;
    }

    if (nextQuestionData) {
      setCurrentQuestion(nextQuestionData);
      setQuestionNumber(prev => prev + 1);
      setSelectedIndex(null);
      setIsSubmitted(false);
      setEvaluation(null);
      setDifficultyShift(null);
      setNextQuestionData(null);
    }
  };

  if (!currentQuestion) return <LoadingSpinner message="Fetching next adaptive question..." />;

  return (
    <div className="quiz-layout fade-in">
      <ProgressBar current={questionNumber} total={sessionData.total_questions} />

      <div className="glass-panel quiz-meta-bar">
        <div className="quiz-score-tracker">
          <span className="score-badge">Score: {score} pts</span>
          {streak > 1 && <span className="streak-badge">🔥 {streak} Streak!</span>}
          <span className="skill-badge">Skill: {Math.round(skillScore)}%</span>
        </div>
      </div>

      <QuestionCard
        questionData={currentQuestion}
        questionNumber={questionNumber}
        totalQuestions={sessionData.total_questions}
        selectedIndex={selectedIndex}
        onSelectOption={handleSelectOption}
        isSubmitted={isSubmitted}
        evaluation={evaluation}
      />

      <div className="quiz-footer-actions">
        <button
          className="submit-btn"
          disabled={selectedIndex === null || isSubmitted || submitting}
          onClick={handleSubmitAnswer}
        >
          {submitting ? 'Evaluating...' : 'Submit Answer'}
        </button>
      </div>

      {isSubmitted && evaluation && (
        <ResultPopup
          evaluation={evaluation}
          difficultyShift={difficultyShift}
          onNextQuestion={handleProceedNext}
          isCompleted={isCompleted}
        />
      )}
    </div>
  );
}
