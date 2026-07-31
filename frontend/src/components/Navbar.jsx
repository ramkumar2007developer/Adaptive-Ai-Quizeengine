import React from 'react';

export default function Navbar({ onNavigateHome, activeSessionTopic }) {
  return (
    <header className="navbar">
      <div style={{ cursor: 'pointer' }} onClick={onNavigateHome} className="nav-brand">
        <div className="nav-logo-icon">⚡</div>
        <span>AdaptiveQuiz.AI</span>
      </div>

      {activeSessionTopic && (
        <div style={{
          fontSize: '0.9rem',
          padding: '0.4rem 1rem',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(255,255,255,0.06)',
          border: '1px solid var(--glass-border)',
          color: 'var(--accent-cyan)'
        }}>
          Topic: <strong>{activeSessionTopic}</strong>
        </div>
      )}
    </header>
  );
}
