import React from 'react';

/**
 * Per-question result popup shown after submitting an answer.
 *
 * evaluation shape (from FastAPI EvaluationResult, snake_case):
 * { is_correct, correct_answer, correct_answer_index, explanation,
 *   points_awarded, total_score, streak, skill_score }
 *
 * difficultyShift shape (from FastAPI DifficultyShift, snake_case):
 * { previous_difficulty, new_difficulty, changed, direction, reason }
 */
export default function ResultPopup({ evaluation, difficultyShift, onNextQuestion, isCompleted }) {
  if (!evaluation) return null;

  const isCorrect = evaluation.is_correct;
  const indexLetter = ['A', 'B', 'C', 'D'][evaluation.correct_answer_index] ?? '';

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 8, 16, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 200,
      padding: '1.5rem',
      overflowY: 'auto'
    }}>
      <div className="glass-panel fade-in" style={{
        maxWidth: '620px',
        width: '100%',
        padding: '2rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
        border: isCorrect ? '1px solid var(--easy-color)' : '1px solid var(--hard-color)',
        maxHeight: '90vh',
        overflowY: 'auto'
      }}>
        {/* Header: Correct/Incorrect + Points */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{
            fontSize: '1.5rem',
            fontWeight: 800,
            color: isCorrect ? 'var(--easy-color)' : 'var(--hard-color)'
          }}>
            {isCorrect ? '🎉 Correct Answer!' : '✕ Incorrect'}
          </span>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            background: 'rgba(255,255,255,0.08)',
            padding: '0.25rem 0.75rem',
            borderRadius: 'var(--radius-full)'
          }}>
            +{evaluation.points_awarded} pts
          </span>
        </div>

        {/* Always show the correct answer */}
        <div style={{
          padding: '0.85rem 1.15rem',
          borderRadius: 'var(--radius-sm)',
          background: isCorrect ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.08)',
          border: '1px solid var(--easy-color)',
          fontSize: '0.95rem',
          color: 'var(--easy-color)',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.5rem'
        }}>
          <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>✅</span>
          <div>
            <div style={{ marginBottom: '0.2rem', fontWeight: 700, letterSpacing: '0.02em' }}>
              Correct Answer ({indexLetter}):
            </div>
            <span style={{ fontWeight: 400, color: 'var(--text-main)', lineHeight: 1.5 }}>
              {evaluation.correct_answer}
            </span>
          </div>
        </div>

        {/* Difficulty Shift */}
        {difficultyShift?.changed && (
          <div style={{
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-sm)',
            background: difficultyShift.direction === 'UP' ? 'var(--medium-bg)' : 'rgba(255,255,255,0.05)',
            border: '1px solid var(--glass-border-glow)',
            fontSize: '0.9rem',
            fontWeight: 600,
            color: 'var(--accent-cyan)'
          }}>
            ⚡ <strong>Adaptive Adjustment:</strong> {difficultyShift.reason} ({difficultyShift.previous_difficulty} → {difficultyShift.new_difficulty})
          </div>
        )}

        {/* Detailed Explanation Section */}
        <div style={{
          padding: '1.1rem 1.25rem',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '0.6rem',
            fontSize: '0.95rem',
            fontWeight: 700,
            color: 'var(--accent-cyan)',
            letterSpacing: '0.02em'
          }}>
            <span>📖</span> Detailed Explanation
          </div>
          <p style={{
            margin: 0,
            fontSize: '0.92rem',
            lineHeight: '1.7',
            color: 'var(--text-muted)',
            whiteSpace: 'pre-line'
          }}>
            {evaluation.explanation}
          </p>
        </div>

        {/* Score Summary */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '1.5rem',
          padding: '0.5rem 0',
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
          fontWeight: 600
        }}>
          <span>📊 Total: {evaluation.total_score} pts</span>
          {evaluation.streak > 1 && <span>🔥 Streak: {evaluation.streak}</span>}
          <span>🎯 Skill: {Math.round(evaluation.skill_score)}%</span>
        </div>

        <button
          className="submit-btn"
          style={{ width: '100%', marginTop: '0.5rem' }}
          onClick={onNextQuestion}
        >
          {isCompleted ? 'View Final Results 🎉' : 'Next Adaptive Question →'}
        </button>
      </div>
    </div>
  );
}
