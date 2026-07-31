import React from 'react';

export default function Home({ onStartClick }) {
  return (
    <div className="home-container fade-in">
      <div className="hero-badge">
        <span>✨ Powered by Next-Gen Adaptive AI</span>
      </div>

      <h1 className="hero-title">
        Master Any Topic with <span>Adaptive Difficulty</span>
      </h1>

      <p className="hero-subtitle">
        An intelligent quiz engine that continuously assesses your performance in real time. Correct answers elevate question difficulty, while wrong answers adjust to build foundational mastery.
      </p>

      <button className="cta-button" onClick={onStartClick}>
        Select Topic & Start Quiz →
      </button>

      <div className="features-grid">
        <div className="glass-panel feature-card">
          <div className="feature-icon">📈</div>
          <h3>Dynamic Engine</h3>
          <p>Real-time algorithm that tracks your response accuracy, speed, and consecutive streaks.</p>
        </div>

        <div className="glass-panel feature-card">
          <div className="feature-icon">🤖</div>
          <h3>AI Prompt Service</h3>
          <p>Generates fresh conceptual, practical, and edge-case questions tailored to your exact level.</p>
        </div>

        <div className="glass-panel feature-card">
          <div className="feature-icon">📊</div>
          <h3>In-Depth Analytics</h3>
          <p>Detailed post-quiz performance reports, score multipliers, and difficulty shift history.</p>
        </div>
      </div>
    </div>
  );
}
