import React from 'react';
import DifficultyBadge from './DifficultyBadge';
import OptionButton from './OptionButton';

/**
 * Renders the current question and its answer options.
 *
 * questionData shape (from FastAPI QuestionResponse):
 * { id, question_number, question_type, difficulty, question_text, options[], topic, subtopic, ... }
 *
 * evaluation shape (from FastAPI EvaluationResult, snake_case):
 * { is_correct, correct_answer, correct_answer_index, explanation, points_awarded, total_score, streak, skill_score }
 */
export default function QuestionCard({
  questionData,
  questionNumber,
  totalQuestions,
  selectedIndex,
  onSelectOption,
  isSubmitted,
  evaluation
}) {
  return (
    <div className="glass-panel question-card-panel fade-in">
      <div className="question-header">
        <span className="question-number">Question {questionNumber} of {totalQuestions}</span>
        <DifficultyBadge difficulty={questionData.difficulty} />
      </div>

      {questionData.subtopic && (
        <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', marginBottom: '0.5rem', fontWeight: 600 }}>
          📌 {questionData.subtopic}
        </div>
      )}

      <h2 className="question-text">{questionData.question_text}</h2>

      <div className="options-grid">
        {(questionData.options ?? []).map((opt, idx) => (
          <OptionButton
            key={idx}
            index={idx}
            optionText={opt}
            isSelected={selectedIndex === idx}
            isSubmitted={isSubmitted}
            isCorrect={evaluation?.is_correct}
            isTargetCorrect={isSubmitted && idx === evaluation?.correct_answer_index}
            onClick={onSelectOption}
          />
        ))}
      </div>
    </div>
  );
}
