import React from 'react';
import DifficultyBadge from '../components/DifficultyBadge';

/**
 * Final results page shown after quiz completion.
 *
 * summary shape (from FastAPI quiz_service.submit_answer when is_completed):
 * { total_score: number, accuracy: number, final_skill_score: number }
 *
 * Note: The backend summary is intentionally lean. For richer history,
 * you can query /api/analytics/overview/{user_id}.
 */
export default function Result({ summary, onRestart }) {
  if (!summary) return null;

  // Support both snake_case (new backend) and any camelCase legacy field names
  const totalScore = summary.total_score ?? summary.totalScore ?? 0;
  const accuracy = summary.accuracy ?? summary.accuracyPercentage ?? 0;
  const skillScore = summary.final_skill_score ?? summary.skillScore ?? null;
  const history = summary.history ?? [];

  const getPerformanceLabel = (acc) => {
    if (acc >= 90) return { label: 'Outstanding! 🌟', color: 'var(--easy-color)' };
    if (acc >= 70) return { label: 'Great Work! 👏', color: 'var(--medium-color)' };
    if (acc >= 50) return { label: 'Good Effort! 💪', color: '#f59e0b' };
    return { label: 'Keep Practicing! 📚', color: 'var(--hard-color)' };
  };

  const perf = getPerformanceLabel(accuracy);

  return (
    <div className="result-container fade-in">
      <div className="glass-panel result-card-main">
        <div className="result-trophy-icon">🏆</div>
        <h1 className="result-title">Quiz Completed!</h1>
        <p style={{ color: perf.color, fontWeight: 700, fontSize: '1.15rem', marginBottom: '0.5rem' }}>
          {perf.label}
        </p>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
          Here is your adaptive quiz performance breakdown
        </p>

        <div className="result-stats-grid">
          <div className="stat-box">
            <span className="stat-value">{totalScore}</span>
            <span className="stat-label">Total Score</span>
          </div>

          <div className="stat-box">
            <span className="stat-value">{Math.round(accuracy)}%</span>
            <span className="stat-label">Accuracy</span>
          </div>

          {skillScore !== null && (
            <div className="stat-box">
              <span className="stat-value">{Math.round(skillScore)}</span>
              <span className="stat-label">Skill Score</span>
            </div>
          )}
        </div>

        <button className="retry-btn" onClick={onRestart}>
          Take Another Adaptive Quiz 🔄
        </button>
      </div>

      {history.length > 0 && (
        <div className="breakdown-section">
          <h3 className="breakdown-title">Detailed Question History</h3>
          {history.map((item, idx) => (
            <div
              key={idx}
              className={`history-item ${item.isCorrect || item.is_correct ? 'correct' : 'incorrect'}`}
            >
              <div className="history-meta">
                <span>Q{item.questionNumber ?? item.question_number ?? idx + 1}</span>
                <DifficultyBadge difficulty={item.difficulty} />
                <span>+{item.pointsAwarded ?? item.points_awarded ?? 0} pts</span>
              </div>
              <p className="history-question">{item.question ?? item.question_text}</p>
              <div className="history-explanation">
                <strong>Explanation:</strong> {item.explanation}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
